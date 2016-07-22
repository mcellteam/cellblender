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
This file contains the classes for CellBlender's Reactions.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_release
from . import cellblender_utils
from . import data_model


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)



# Surface Classes callback functions


def convert_orient_str(orient):
    """Format MDL language (orientation) for viewing in the UI"""

    if orient == "'":
        orient = "Top/Front"
    elif orient == ",":
        orient = "Bottom/Back"
    elif orient == ";":
        orient = "Ignore"

    return(orient)


def convert_surf_class_str(surf_class_type):
    """Format MDL language (surf class type) for viewing in the UI"""

    if surf_class_type == "ABSORPTIVE":
        surf_class_type = "Absorptive"
    elif surf_class_type == "TRANSPARENT":
        surf_class_type = "Transparent"
    elif surf_class_type == "REFLECTIVE":
        surf_class_type = "Reflective"
    elif surf_class_type == "CLAMP_CONCENTRATION":
        surf_class_type = "Clamp Concentration"

    return(surf_class_type)



def check_surf_class_props(self, context):
    """Checks for illegal/undefined molecule names in surf class properties"""

    mcell = context.scene.mcell
    active_surf_class = mcell.surface_classes.surf_class_list[
        mcell.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    mol_list = mcell.molecules.molecule_list
    affected_mols = surf_class_props.affected_mols
    molecule = surf_class_props.molecule
    surf_class_type = surf_class_props.surf_class_type
    orient = surf_class_props.surf_class_orient

    surf_class_type = convert_surf_class_str(surf_class_type)
    orient = convert_orient_str(orient)

    if affected_mols == 'SINGLE':
        surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (molecule, orient, surf_class_type)
    else:
        surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (affected_mols, orient, surf_class_type)

    status = ""

    if affected_mols == 'SINGLE':
        # Check for illegal names (Starts with a letter. No special characters.)
        mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
        m = re.match(mol_filter, molecule)

        if m is None:
            status = "SC: Molecule name error: %s" % (molecule)
        else:
            # Check for undefined names
            mol_name = m.group(1)
            if not mol_name in mol_list:
                status = "Undefined molecule: %s" % (mol_name)

    surf_class_props.status = status

    return


def check_surface_class(self, context):
    """Checks for duplicate or illegal surface class name"""

    surf_class = context.scene.mcell.surface_classes
    active_surf_class = surf_class.surf_class_list[
        surf_class.active_surf_class_index]

    status = ""

    # Check for duplicate names
    surf_class_keys = surf_class.surf_class_list.keys()
    if surf_class_keys.count(active_surf_class.name) > 1:
        status = "Duplicate Surface Class: %s" % (active_surf_class.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    surf_class_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(surf_class_filter, active_surf_class.name)
    if m is None:
        status = "Surface Class name error: %s" % (active_surf_class.name)

    active_surf_class.status = status

    return

"""
def update_clamp_value(self, context):
    # Store the clamp value as a float if it's legal or generate an error

    mcell = context.scene.mcell
    surf_class = context.scene.mcell.surface_classes
    active_surf_class = mcell.surface_classes.surf_class_list[
        mcell.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    #surf_class_type = surf_class_props.surf_class_type
    #orient = surf_class_props.surf_class_orient
    #molecule = surf_class_props.molecule
    clamp_value_str = surf_class_props.clamp_value_str

    (clamp_value, status) = cellblender_utils.check_val_str(clamp_value_str, 0, None)

    if status == "":
        surf_class_props.clamp_value = clamp_value
    else:
        #status = status % ("clamp_value", clamp_value_str)
        surf_class_props.clamp_value_str = "%g" % (
            surf_class_props.clamp_value)

    #surf_class_type = convert_surf_class_str(surf_class_type)
    #orient = convert_orient_str(orient)

    #if molecule:
    #    surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (
    #        molecule, orient, surf_class_type)
    #else:
    #    surf_class_props.name = "Molec.: NA   Orient.: %s   Type: %s" % (
    #        orient, surf_class_type)

    #surf_class.surf_class_props_status = status

    return
"""

# Surface Classes Operators:


class MCELL_OT_surf_class_props_add(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_add"
    bl_label = "Add Surface Class Properties"
    bl_description = "Add new surface class properties to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.add()
        active_surf_class.active_surf_class_props_index = len(active_surf_class.surf_class_props_list) - 1
        active_surf_class.surf_class_props_list[active_surf_class.active_surf_class_props_index].init_properties(context.scene.mcell.parameter_system)
        check_surf_class_props(self, context)

        return {'FINISHED'}


class MCELL_OT_surf_class_props_remove(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_remove"
    bl_label = "Remove Surface Class Properties"
    bl_description = "Remove surface class properties from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.mcell.parameter_system
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[surf_class.active_surf_class_index]
        active_surf_class_prop = active_surf_class.surf_class_props_list[active_surf_class.active_surf_class_props_index]
        active_surf_class_prop.remove_properties(context)

        active_surf_class.surf_class_props_list.remove(active_surf_class.active_surf_class_props_index)
        active_surf_class.active_surf_class_props_index = len(active_surf_class.surf_class_props_list) - 1
        if (active_surf_class.active_surf_class_props_index < 0):
            active_surf_class.active_surf_class_props_index = 0

        return {'FINISHED'}


class MCELL_OT_surface_class_add(bpy.types.Operator):
    bl_idname = "mcell.surface_class_add"
    bl_label = "Add Surface Class"
    bl_description = "Add a new surface class to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        surf_class.surf_class_list.add()
        surf_class.active_surf_class_index = len(surf_class.surf_class_list) - 1
        surf_class.surf_class_list[surf_class.active_surf_class_index].init_properties(context.scene.mcell.parameter_system)
        surf_class.surf_class_list[surf_class.active_surf_class_index].name = "Surface_Class"

        return {'FINISHED'}


class MCELL_OT_surface_class_remove(bpy.types.Operator):
    bl_idname = "mcell.surface_class_remove"
    bl_label = "Remove Surface Class"
    bl_description = "Remove selected surface class from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        surf_class.surf_class_list.remove(surf_class.active_surf_class_index)
        surf_class.active_surf_class_index -= 1
        if (surf_class.active_surf_class_index < 0):
            surf_class.active_surf_class_index = 0

        if surf_class.surf_class_list:
            check_surface_class(self, context)
        else:
            surf_class.surf_class_status = ""

        return {'FINISHED'}


# Surface Classes Panels:


class MCELL_UL_check_surface_class(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_surface_class_props(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_surface_classes(bpy.types.Panel):
    bl_label = "CellBlender - Define Surface Classes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.surface_classes.draw_panel ( context, self )


# Surface Classes Property Groups



class MCellSurfaceClassPropertiesProperty(bpy.types.PropertyGroup):

    """ This is where properties for a given surface class are stored.

    All of the properties here ultimately get converted into something like the
    following: ABSORPTIVE = Molecule' or REFLECTIVE = Molecule;
    Each instance is only one set of properties for a surface class that may
    have many sets of properties.

    """

    affected_mols_enum = [
        ( 'ALL_MOLECULES', "All Molecules", "" ),
        ( 'ALL_VOLUME_MOLECULES', "All Volume Molecules", "" ),
        ( 'ALL_SURFACE_MOLECULES', "All Surface Molecules", "" ),
        ( 'SINGLE', "Single Molecule", "" ) ]
    affected_mols = EnumProperty (
        items = affected_mols_enum, name="Molecules", default='ALL_MOLECULES',
        description="Molecules (or groups of molecules) affected by this surface class.",
        update=check_surf_class_props )

    name = StringProperty(name="Molecule", default="Molecule")
    molecule = StringProperty(
        name="Molecule Name",
        description="The molecule that is affected by the surface class",
        update=check_surf_class_props)
    surf_class_orient_enum = [
        ('\'', "Top/Front", ""),
        (',', "Bottom/Back", ""),
        (';', "Ignore", "")]
    surf_class_orient = EnumProperty(
        items=surf_class_orient_enum, name="Orientation", default=";",
        description="Volume molecules affected at front or back of a surface. "
                    "Surface molecules affected by orientation at border.",
        update=check_surf_class_props)
    surf_class_type_enum = [
        ('ABSORPTIVE', "Absorptive", ""),
        ('TRANSPARENT', "Transparent", ""),
        ('REFLECTIVE', "Reflective", ""),
        ('CLAMP_CONCENTRATION', "Clamp Concentration", "")]
    surf_class_type = EnumProperty(
        items=surf_class_type_enum, name="Type", default="TRANSPARENT",
        description="Molecules are destroyed by absorptive surfaces, pass "
                    "through transparent, and \"bounce\" off of reflective.",
        update=check_surf_class_props)

    clamp_value = PointerProperty ( name="Value", type=parameter_system.Parameter_Reference )

    status = StringProperty(name="Status")

    def build_data_model_from_properties ( self, context ):
        sc = self
        sc_dict = {}
        sc_dict['data_model_version'] = "DM_2015_11_08_1756"
        sc_dict['name'] = sc.name
        sc_dict['affected_mols'] = sc.affected_mols
        sc_dict['molecule'] = sc.molecule
        sc_dict['surf_class_orient'] = str(sc.surf_class_orient)
        sc_dict['surf_class_type'] = str(sc.surf_class_type)
        sc_dict['clamp_value'] = sc.clamp_value.get_expr()
        return sc_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassPropertiesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            # Need to convert the clamp value from a plain string to a string expression
            # It turns out that the old clamp_value was already stored as a string so it should be compatible
            # Just update the data model version
            dm['data_model_version'] = "DM_2015_09_25_1653"

        if dm['data_model_version'] == "DM_2015_09_25_1653":
            # Previous versions could only represent SINGLE molecules, so make it explicit when upgrading
            dm['affected_mols'] = "SINGLE"
            dm['data_model_version'] = "DM_2015_11_08_1756"

        if dm['data_model_version'] != "DM_2015_11_08_1756":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassPropertiesProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the current version for this property group
        if dm['data_model_version'] != "DM_2015_11_08_1756":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassPropertiesProperty data model to current version." )
        # Now convert the updated Data Model into CellBlender Properties
        self.name = dm["name"]
        self.affected_mols = dm['affected_mols']
        self.molecule = dm["molecule"]
        self.surf_class_orient = dm["surf_class_orient"]
        self.surf_class_type = dm["surf_class_type"]
        self.clamp_value.set_expr ( dm["clamp_value"] )

    def init_properties ( self, parameter_system ):
        self.name = "Molecule"
        self.affected_mols = 'ALL_MOLECULES'
        self.molecule = ""
        self.surf_class_orient = ';'
        self.surf_class_type = 'TRANSPARENT'
        helptext = "Clamp the Concentration of this molecule to this value on this surface."
        self.clamp_value.init_ref ( parameter_system, "Surf_Class_Val_Type", user_name="Value", user_expr="0", user_units="Concentration Units: Molar", user_descr=helptext )

    def remove_properties ( self, context ):
        print ( "Removing all Surface Class Properties... no collections to remove." )
        ps = context.scene.mcell.parameter_system
        self.clamp_value.clear_ref ( ps )


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )




class MCellSurfaceClassesProperty(bpy.types.PropertyGroup):
    """ Stores the surface class name and a list of its properties. """

    name = StringProperty(
        name="Surface Class Name", default="Surface_Class",
        description="This name can be selected in Assign Surface Classes.",
        update=check_surface_class)
    surf_class_props_list = CollectionProperty(
        type=MCellSurfaceClassPropertiesProperty, name="Surface Classes List")
    active_surf_class_props_index = IntProperty(
        name="Active Surface Class Index", default=0)
    status = StringProperty(name="Status")

    def init_properties ( self, parameter_system ):
        if self.surf_class_props_list:
            for sc in self.surf_class_props_list:
                sc.init_properties(parameter_system)


    def remove_properties ( self, context ):
        print ( "Removing all Surface Class Properties..." )
        for item in self.surf_class_props_list:
            item.remove_properties(context)
        self.surf_class_props_list.clear()
        self.active_surf_class_props_index = 0
        print ( "Done removing all Surface Class Properties." )

    def build_data_model_from_properties ( self, context ):
        print ( "Surface Classes building Data Model" )
        sc_dm = {}
        sc_dm['data_model_version'] = "DM_2014_10_24_1638"
        sc_dm['name'] = self.name
        sc_list = []
        for sc in self.surf_class_props_list:
            sc_list.append ( sc.build_data_model_from_properties(context) )
        sc_dm['surface_class_prop_list'] = sc_list
        return sc_dm



    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesProperty data model to current version." )
            return None

        if "surface_class_prop_list" in dm:
            for item in dm["surface_class_prop_list"]:
                if MCellSurfaceClassPropertiesProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesProperty data model to current version." )

        self.name = dm["name"]
        while len(self.surf_class_props_list) > 0:
            self.surf_class_props_list.remove(0)
        if "surface_class_prop_list" in dm:
            for sc in dm["surface_class_prop_list"]:
                self.surf_class_props_list.add()
                self.active_surf_class_props_index = len(self.surf_class_props_list)-1
                scp = self.surf_class_props_list[self.active_surf_class_props_index]
                scp.init_properties(context.scene.mcell.parameter_system)
                scp.build_properties_from_data_model ( context, sc )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )
        




class MCellSurfaceClassesPropertyGroup(bpy.types.PropertyGroup):
    surf_class_list = CollectionProperty(
        type=MCellSurfaceClassesProperty, name="Surface Classes List")
    active_surf_class_index = IntProperty(
        name="Active Surface Class Index", default=0)
    #surf_class_props_status = StringProperty(name="Status")

    # surf_class_help_title = StringProperty(name="SCT", default="Help on Surface Classes", description="Toggle Showing of Help for Surface Classes." )
    surf_class_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def build_data_model_from_properties ( self, context ):
        print ( "Surface Classes Panel building Data Model" )
        sc_dm = {}
        sc_dm['data_model_version'] = "DM_2014_10_24_1638"
        sc_list = []
        for sc in self.surf_class_list:
            sc_list.append ( sc.build_data_model_from_properties(context) )
        sc_dm['surface_class_list'] = sc_list
        return sc_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassesPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesPropertyGroup data model to current version." )
            return None

        if "surface_class_list" in dm:
            for item in dm["surface_class_list"]:
                if MCellSurfaceClassesProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassesPropertyGroup data model to current version." )

        while len(self.surf_class_list) > 0:
            self.surf_class_list.remove(0)
        if "surface_class_list" in dm:
            for s in dm["surface_class_list"]:
                self.surf_class_list.add()
                self.active_surf_class_index = len(self.surf_class_list)-1
                sc = self.surf_class_list[self.active_surf_class_index]
                sc.init_properties(context.scene.mcell.parameter_system)
                sc.build_properties_from_data_model ( context, s )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Surface Classes Properties..." )
        for item in self.surf_class_list:
            item.remove_properties(context)
        self.surf_class_list.clear()
        self.active_surf_class_index = 0
        print ( "Done removing all Surface Classes Properties." )



    def draw_layout(self, context, layout):
        # layout = self.layout
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            # surf_class = mcell.surface_classes
            ps = mcell.parameter_system

            helptext = "Surface Classes\n" + \
                       " \n" + \
                       "MCell3 allows the user to specify properties of the surfaces\n" + \
                       "of objects. For example, one may wish to specify that a surface\n" + \
                       "does not block the diffusion of molecules. Each type of surface\n" + \
                       "is defined by name, and each surface name must be unique in the\n" + \
                       "simulation and should not match any molecule names.\n" + \
                       " \n" + \
                       "Each Surface Class can associate a number of properties with different molecules:\n" + \
                       " \n" + \
                       "     -  REFLECTIVE = name\n" + \
                       "           If name refers to a volume molecule it is reflected by any surface with\n" + \
                       "           this surface class. This is the default behavior for volume molecules.\n" + \
                       "           If name refers to a surface molecule it is reflected by the border of the\n" + \
                       "           surface with this surface class. Tick marks on the name allow selective\n" + \
                       "           reflection of volume molecules from only the front or back of a surface\n" + \
                       "           or selective reflection of surface molecules with only a certain orientation\n" + \
                       "           from the surface’s border. Using the keyword ALL_MOLECULES\n" + \
                       "           for name has the effect that all volume molecules are reflected by surfaces\n" + \
                       "           with this surface class and all surface molecules are reflected by\n" + \
                       "           the border of the surfaces with this surface class. Using the keyword\n" + \
                       "           ALL_VOLUME_MOLECULES for the name has the effect that all volume\n" + \
                       "           molecules are reflected by surfaces with this surface class. Using\n" + \
                       "           the keyword ALL_SURFACE_MOLECULES has the effect that all\n" + \
                       "           surface molecules are reflected by the border of the surface with this\n" + \
                       "           surface class\n" + \
                       " \n" + \
                       "     -  TRANSPARENT = name\n" + \
                       "           If name refers to a volume molecule it passes through all surfaces with\n" + \
                       "           this surface class. If name refers to a surface molecule it passes through\n" + \
                       "           the border of the surface with this surface class. This is the default\n" + \
                       "           behavior for surface molecules. Tick marks onname allow the creation\n" + \
                       "           of one-way transparent surfaces for volume molecules or oneway\n" + \
                       "           transparent surface borders for surface molecules. To make a\n" + \
                       "           surface with this surface class transparent to all volume molecules,\n" + \
                       "           use ALL_VOLUME_MOLECULES for name. To make a border of the\n" + \
                       "           surface with this surface class transparent to all surface molecules,\n" + \
                       "           use ALL_SURFACE_MOLECULES for name. Using the keyword\n" + \
                       "           ALL_MOLECULES for name has the effect that surfaces with this surface\n" + \
                       "           class are transparent to all volume molecules and borders of the\n" + \
                       "           surfaces with this surface class are transparent to all surface molecules.\n" + \
                       " \n" + \
                       "     -  ABSORPTIVE = name\n" + \
                       "           If name refers to a volume molecule it is destroyed if it touches surfaces\n" + \
                       "           with this surface class. If name refers to a surface molecule it\n" + \
                       "           is destroyed if it touches the border of the surface with this surface\n" + \
                       "           class. Tick marks on name allow destruction from only one side of\n" + \
                       "           the surface for volume molecules or selective destruction for surface\n" + \
                       "           molecules on the surfaces’s border based on their orientation. To make\n" + \
                       "           a surface with this surface class absorptive to all volume molecules,\n" + \
                       "           ALL_VOLUME_MOLECULES can be used for name. To make a border\n" + \
                       "           of the surface with this surface class absorptive to all surface molecules,\n" + \
                       "           ALL_SURFACE_MOLECULES can be used for name. Using the keyword\n" + \
                       "           ALL_MOLECULES has the effect that surfaces with this surface\n" + \
                       "           class are absorptive for all volume molecules and borders of the surfaces\n" + \
                       "           with this surface class are absorptive for all surface molecules.\n" + \
                       " \n" + \
                       "     -  CLAMP_CONCENTRATION = name = value\n" + \
                       "           The molecule called name is destroyed if it touches the surface (as if it\n" + \
                       "           had passed through), and new molecules are created at the surface, as\n" + \
                       "           if molecules had passed through from the other side at a concentration\n" + \
                       "           value (units = M). Orientation marks may be used; in this case, the other\n" + \
                       "           side of the surface is reflective. Note that this command is only used to\n" + \
                       "           set the effective concentration of a volume molecule at a surface; it is not\n" + \
                       "           valid to specify a surface molecule. This command can be abbreviated\n" + \
                       "           as CLAMP_CONC."
            ps.draw_label_with_help ( layout, "Surface Class Help", self, "surf_class_show_help", self.surf_class_show_help, helptext )


            row = layout.row()
            col = row.column()
            # The template_list for the surface classes themselves
            col.template_list("MCELL_UL_check_surface_class", "define_surf_class",
                              self, "surf_class_list", self,
                              "active_surf_class_index", rows=2)
            col = row.column(align=True)
            col.operator("mcell.surface_class_add", icon='ZOOMIN', text="")
            col.operator("mcell.surface_class_remove", icon='ZOOMOUT', text="")
            row = layout.row()

            # Show the surface class properties template_list if there is at least
            # a single surface class.

            if self.surf_class_list:
                active_surf_class = self.surf_class_list[
                    self.active_surf_class_index]
                row = layout.row()

                row.prop(active_surf_class, "name")
                row = layout.row()
                row.label(text="%s Properties:" % active_surf_class.name, icon='FACESEL_HLT')
                row = layout.row()
                col = row.column()
                # The template_list for the properties of a surface class.
                # Properties include molecule, orientation, and type of surf class.
                # There can be multiple properties for a single surface class
                col.template_list("MCELL_UL_check_surface_class_props",
                                  "define_surf_class_props", active_surf_class,
                                  "surf_class_props_list", active_surf_class,
                                  "active_surf_class_props_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.surf_class_props_add", icon='ZOOMIN', text="")
                col.operator("mcell.surf_class_props_remove", icon='ZOOMOUT',
                             text="")
                # Show the surface class property fields (molecule, orientation,
                # type) if there is at least a single surface class property.
                if active_surf_class.surf_class_props_list:
                    surf_class_props = active_surf_class.surf_class_props_list[
                        active_surf_class.active_surf_class_props_index]
                    layout.prop(surf_class_props, "affected_mols")
                    if surf_class_props.affected_mols == 'SINGLE':
                        layout.prop_search(surf_class_props, "molecule",
                                           mcell.molecules, "molecule_list",
                                           icon='FORCE_LENNARDJONES')
                    layout.prop(surf_class_props, "surf_class_orient")
                    layout.prop(surf_class_props, "surf_class_type")
                    if (surf_class_props.surf_class_type == 'CLAMP_CONCENTRATION'):
                        surf_class_props.clamp_value.draw(layout,ps)


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




#Custom Properties


