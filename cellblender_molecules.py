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
import mathutils

# python imports
import re

import cellblender
from . import cellblender_parameters


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
        description="Surface molecules are constrained to surfaces/meshes. "
                    "Volume molecules exist in space.")

    diffusion_constant = PointerProperty(name="Diffusion Constant", type=cellblender_parameters.PanelParameterFloat)

    target_only = BoolProperty(
        name="Target Only",
        description="If selected, molecule will not initiate reactions when "
                    "it runs into other molecules. Can speed up simulations.")

    custom_time_step = PointerProperty(name="Custom Time Step", type=cellblender_parameters.PanelParameterFloat)
    custom_space_step = PointerProperty(name="Custom Space Step", type=cellblender_parameters.PanelParameterFloat)

    export_viz = bpy.props.BoolProperty(
        default=False, description="If selected, the molecule will be "
                                   "included in the visualization data.")
    status = StringProperty(name="Status")


    def set_defaults(self):
        self.name = "Molecule_"+str(self.id)
        self.diffusion_constant.set_label ( "Diffusion Constant" )  # Tried self.diffusion_constant.name but didn't work.
        self.custom_time_step.set_label ( "Custom Time Step" )
        self.custom_space_step.set_label ( "Custom Space Step" )


    # Exporting to an MDL file could be done just like this
    def print_details( self ):
        print ( "Name = " + self.name )

    def draw_props ( self, layout, molecules ):
        layout.prop ( self, "name" )
        layout.prop ( self, "type" )
        # layout.prop ( self, "diffusion_constant")
        self.diffusion_constant.draw_in_new_row(layout)

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
            self.custom_time_step.draw_in_new_row(box)
            self.custom_space_step.draw_in_new_row(box)
            #row = box.row()
            #row.prop(self, "custom_time_step")
            #row = box.row()
            #row.prop(self, "custom_space_step")

    def check_callback(self, context):
        """Allow the parent molecule list (MCellMoleculesListProperty) to do the checking"""
        get_parent(self).check(context)
        return



class MCell_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCell_PT_define_molecules(bpy.types.Panel):
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
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    def set_defaults(self):
        # It's not clear if setting the defaults for the molecule list should
        #    set defaults for each molecule in the list or
        #    delete all the molecules to create an empty list
        # Since it's more interesting to set the molecules back to their defaults ... do that.
        if self.molecule_list:
            for mol in self.molecule_list:
                mol.set_defaults()
    
    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_mol = self.molecule_list.add()
        new_mol.id = self.allocate_available_id()
        new_mol.set_defaults()
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        self.molecule_list.remove ( self.active_mol_index )
        self.active_mol_index -= 1
        if self.active_mol_index < 0:
            self.active_mol_index = 0
        if self.molecule_list:
            self.check(context)

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

    def draw_panel ( self, context, panel ):
        layout = panel.layout
        row = layout.row()
        row.label(text="Defined Molecules:", icon='FORCE_LENNARDJONES')
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
            mol.draw_props ( layout, self )

