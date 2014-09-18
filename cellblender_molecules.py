# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

"""
This file contains the classes for CellBlender's Molecules.

"""

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent
import math
import mathutils

# python imports
import re

import cellblender
# from . import cellblender_parameters
from . import parameter_system
from . import cellblender_operators


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Generic helper functions that should go somewhere else!!!

def get_path_to_parent(self_object):
    """ Return the Blender class path to the parent object with regard to the Blender Property Tree System """
    path_to_self = "bpy.context.scene." + self_object.path_from_id()
    path_to_parent = path_to_self[0:path_to_self.rfind(".")]
    return path_to_parent

def get_parent(self_object):
    """ Return the parent Blender object with regard to the Blender Property Tree System """
    path_to_parent = get_path_to_parent(self_object)
    parent = eval(path_to_parent)
    return parent



# Molecule Operators:

class MCELL_OT_molecule_add(bpy.types.Operator):
    bl_idname = "mcell.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule type to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.add_molecule(context)
        return {'FINISHED'}

class MCELL_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "mcell.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.remove_active_molecule(context)
        self.report({'INFO'}, "Deleted Molecule")
        return {'FINISHED'}




# Callbacks for all Property updates appear to require global (non-member) functions.
# This is circumvented by simply calling the associated member function passed as self:

def check_callback(self, context):
    self.check_callback(context)
    return


def display_callback(self, context):
    self.display_callback(context)
    return


class MCellMoleculeProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    name = StringProperty(
        name="Molecule Name", default="Molecule",
        description="The molecule species name",
        update=check_callback)
    id = IntProperty(name="Molecule ID", default=0)
    type_enum = [
        ('2D', "Surface Molecule", ""),
        ('3D', "Volume Molecule", "")]
    type = EnumProperty(
        items=type_enum, name="Molecule Type",
        default='3D',
        description="Surface molecules are constrained to surfaces/meshes. "
                    "Volume molecules exist in space.")
    diffusion_constant = PointerProperty ( name="Molecule Diffusion Constant", type=parameter_system.Parameter_Reference )
    lr_bar_trigger = BoolProperty("lr_bar_trigger", default=False)
    target_only = BoolProperty(
        name="Target Only",
        description="If selected, molecule will not initiate reactions when "
                    "it runs into other molecules. Can speed up simulations.")

    custom_time_step =   PointerProperty ( name="Molecule Custom Time Step",   type=parameter_system.Parameter_Reference )
    custom_space_step =  PointerProperty ( name="Molecule Custom Space Step",  type=parameter_system.Parameter_Reference )
    # TODO: Add after data model release:  maximum_step_length =  PointerProperty ( name="Maximum Step Length",  type=parameter_system.Parameter_Reference )

    color = FloatVectorProperty ( name="", min=0.0, max=1.0, default=(0.5,0.5,0.5), subtype='COLOR', description='Molecule Color', update=display_callback )
    usecolor = BoolProperty ( name="Use this Color", default=True, description='Use Molecule Color instead of Material Color', update=display_callback )
    alpha = FloatProperty ( name="Alpha", min=0.0, max=1.0, default=1.0, description="Alpha (inverse of transparency)", update=display_callback )
    scale = FloatProperty ( name="Scale", min=0.0, default=1.0, description="Relative size (scale) for this molecule", update=display_callback )
    glyph_enum = [
        ('Cone', "Cone", ""),
        ('Cube', "Cube", ""),
        ('Cylinder', "Cylinder", ""),
        ('Icosahedron', "Icosahedron", ""),
        ('Octahedron', "Octahedron", ""),
        ('Receptor', "Receptor", ""),
        ('Sphere_1', "Sphere_1", ""),
        ('Sphere_2', "Sphere_2", ""),
        ('Torus', "Torus", "")]
    glyph = EnumProperty ( items=glyph_enum, name="", update=display_callback )


    export_viz = bpy.props.BoolProperty(
        default=False, description="If selected, the molecule will be "
                                   "included in the visualization data.")
    status = StringProperty(name="Status")

    def init_properties ( self, parameter_system ):
        self.name = "Molecule_"+str(self.id)

        self.diffusion_constant.init_ref   ( parameter_system, "Mol_Diff_Const_Type", user_name="Diffusion Constant",   user_expr="0", user_units="cm^2/sec", user_descr="Molecule Diffusion Constant" )
        self.custom_time_step.init_ref     ( parameter_system, "Mol_Time_Step_Type",  user_name="Custom Time Step",     user_expr="",  user_units="seconds",  user_descr="Molecule Custom Time Step" )
        self.custom_space_step.init_ref    ( parameter_system, "Mol_Space_Step_Type", user_name="Custom Space Step",    user_expr="",  user_units="microns",  user_descr="Molecule Custom Space Step" )
        # TODO: Add after data model release:  self.maximum_step_length.init_ref  ( parameter_system, "Max_Step_Len_Type",   user_name="Maximum Step Length",  user_expr="",  user_units="microns",  user_descr="Molecule should never step farther than this length during a single timestep. Use with caution (see documentation)." )


    def build_data_model_from_properties ( self ):
        m = self

        m_dict = {}
        m_dict['mol_name'] = m.name
        m_dict['mol_type'] = str(m.type)
        m_dict['diffusion_constant'] = m.diffusion_constant.get_expr()
        m_dict['target_only'] = m.target_only
        m_dict['custom_time_step'] = m.custom_time_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        # TODO: Add after data model release:   m_dict['maximum_step_length'] = m.maximum_step_length.get_expr()
        m_dict['maximum_step_length'] = ""  # TODO: Remove this line after data model release
        m_dict['export_viz'] = m.export_viz

        return m_dict

    def build_properties_from_data_model ( self, context, dm_dict ):
        self.name = dm_dict["mol_name"]
        self.type = dm_dict["mol_type"]
        self.diffusion_constant.set_expr ( dm_dict["diffusion_constant"] )
        self.target_only = dm_dict["target_only"]
        self.custom_time_step.set_expr ( dm_dict["custom_time_step"] )
        self.custom_space_step.set_expr ( dm_dict["custom_space_step"] )
        # TODO: Add after data model release:   self.maximum_step_length.set_expr ( dm_dict["maximum_step_length"] )
        self.export_viz = dm_dict["export_viz"]


    # Exporting to an MDL file could be done just like this
    def print_details( self ):
        print ( "Name = " + self.name )

    def draw_props ( self, layout, molecules, parameter_system ):
        layout.prop ( self, "name" )
        layout.prop ( self, "type" )
        self.diffusion_constant.draw(layout,parameter_system)
        #self.lr_bar_trigger = False
        
        lr_bar_display = 0
        if len(self.custom_space_step.get_expr().strip()) > 0:
            # Set lr_bar_display directly
            lr_bar_display = self.custom_space_step.get_value()
        else:
            # Calculate lr_bar_display from diffusion constant and time step
            dc = self.diffusion_constant.get_value()
            ts = bpy.context.scene.mcell.initialization.time_step.get_value()
            if len(self.custom_time_step.get_expr().strip()) > 0:
                ts = self.custom_time_step.get_value()
            lr_bar_display = 2 * math.sqrt ( 4 * dc * ts / math.pi )

        row = layout.row()
        row.label(text="lr_bar: %g"%(lr_bar_display), icon='BLANK1')  # BLANK1 RIGHTARROW_THIN SMALL_TRI_RIGHT_VEC DISCLOSURE_TRI_RIGHT_VEC DRIVER DOT FORWARD LINKED
        #layout.prop ( self, "lr_bar_trigger", icon='NONE', text="lr_bar: " + str(lr_bar_display) )

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_display:
            row.prop(molecules, "show_display", icon='TRIA_RIGHT',
                     text="Display Options", emboss=False)
        else:
            row.prop(molecules, "show_display", icon='TRIA_DOWN',
                     text="Display Options", emboss=False)
            row = box.row()
            row.label ( "These don't all work yet. Use other panels as needed.", icon='ERROR' )
            row = box.row()
            col = row.column()
            col.prop ( self, "glyph" )
            col = row.column()
            col.prop ( self, "scale" )
            row = box.row()
            col = row.column()
            col.prop ( self, "color" )
            col = row.column()
            col.prop ( self, "usecolor" )
        
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_advanced:
            row.prop(molecules, "show_advanced", icon='TRIA_RIGHT',
                     text="Advanced Options", emboss=False)
        else:
            row.prop(molecules, "show_advanced", icon='TRIA_DOWN',
                     text="Advanced Options", emboss=False)
            row = box.row()
            row.prop(self, "target_only")
            self.custom_time_step.draw(box,parameter_system)
            self.custom_space_step.draw(box,parameter_system)


    def check_callback(self, context):
        """Allow the parent molecule list (MCellMoleculesListProperty) to do the checking"""
        get_parent(self).check(context)
        return


    def display_callback(self, context):
        """One of the display items has changed for this molecule"""
        # print ( "Display for molecule \"" + self.name + "\" changed to: " + str(self.glyph) + ", " + str(self.color) + ", " + str(self.alpha) + ", " + str(self.scale) )
        # Refresh the scene
        cellblender_operators.mol_viz_update(self,context)  # It's not clear why mol_viz_update needs a self. It's not in a class.
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return



class MCell_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_molecules(bpy.types.Panel):
    bl_label = "CellBlender - Define Molecules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw ( self, context ):
        # Call the draw function for the instance being drawn in this panel
        context.scene.mcell.molecules.draw_panel ( context, self )


class MCellMoleculesListProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    molecule_list = CollectionProperty(type=MCellMoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    def init_properties ( self, parameter_system ):
        if self.molecule_list:
            for mol in self.molecule_list:
                mol.init_properties(parameter_system)
    
    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_mol = self.molecule_list.add()
        new_mol.id = self.allocate_available_id()
        new_mol.init_properties(context.scene.mcell.parameter_system)
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        self.molecule_list.remove ( self.active_mol_index )
        self.active_mol_index -= 1
        if self.active_mol_index < 0:
            self.active_mol_index = 0
        if self.molecule_list:
            self.check(context)

    def build_data_model_from_properties ( self, context ):
        print ( "Molecule List building Data Model" )
        mol_dm = {}
        mol_list = []
        for m in self.molecule_list:
            mol_list.append ( m.build_data_model_from_properties() )
        mol_dm['molecule_list'] = mol_list
        return mol_dm

    def build_properties_from_data_model ( self, context, dm ):
        while len(self.molecule_list) > 0:
            self.remove_active_molecule ( context )
        
        for m in dm["molecule_list"]:
            self.add_molecule(context)
            self.molecule_list[self.active_mol_index].build_properties_from_data_model(context,m)



    def check ( self, context ):
        """Checks for duplicate or illegal molecule name"""
        # Note: Some of the list-oriented functionality is appropriate here (since this
        #        is a list), but some of the molecule-specific checks (like name legality)
        #        could be handled by the the molecules themselves. They're left here for now.

        mol = self.molecule_list[self.active_mol_index]

        status = ""

        # Check for duplicate molecule name
        mol_keys = self.molecule_list.keys()
        if mol_keys.count(mol.name) > 1:
            status = "Duplicate molecule: %s" % (mol.name)

        # Check for illegal names (Starts with a letter. No special characters.)
        mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
        m = re.match(mol_filter, mol.name)
        if m is None:
            status = "Molecule name error: %s" % (mol.name)

        mol.status = status

        return


    def allocate_available_id ( self ):
        """ Return a unique molecule ID for a new molecule """
        if len(self.molecule_list) <= 0:
            # Reset the ID to 1 when there are no more molecules
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def draw_layout ( self, context, layout ):
        """ Draw the molecule "panel" within the layout """
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            col = row.column()
            col.template_list("MCell_UL_check_molecule", "define_molecules",
                              self, "molecule_list",
                              self, "active_mol_index",
                              rows=2)
            col = row.column(align=True)
            col.operator("mcell.molecule_add", icon='ZOOMIN', text="")
            col.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
            if self.molecule_list:
                mol = self.molecule_list[self.active_mol_index]
                # The self is needed to pass the "advanced" flag to the molecule
                mol.draw_props ( layout, self, mcell.parameter_system )


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

