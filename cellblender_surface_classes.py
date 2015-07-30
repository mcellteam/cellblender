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
from . import cellblender_operators
from . import cellblender_release
from . import utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Reaction Operators:


# Reaction callback functions



# Surface Classes Property Groups



class MCellSurfaceClassPropertiesProperty(bpy.types.PropertyGroup):

    """ This is where properties for a given surface class are stored.

    All of the properties here ultimately get converted into something like the
    following: ABSORPTIVE = Molecule' or REFLECTIVE = Molecule;
    Each instance is only one set of properties for a surface class that may
    have many sets of properties.

    """

    name = StringProperty(name="Molecule", default="Molecule")
    molecule = StringProperty(
        name="Molecule Name",
        description="The molecule that is affected by the surface class",
        update=cellblender_operators.check_surf_class_props)
    surf_class_orient_enum = [
        ('\'', "Top/Front", ""),
        (',', "Bottom/Back", ""),
        (';', "Ignore", "")]
    surf_class_orient = EnumProperty(
        items=surf_class_orient_enum, name="Orientation",
        description="Volume molecules affected at front or back of a surface. "
                    "Surface molecules affected by orientation at border.",
        update=cellblender_operators.check_surf_class_props)
    surf_class_type_enum = [
        ('ABSORPTIVE', "Absorptive", ""),
        ('TRANSPARENT', "Transparent", ""),
        ('REFLECTIVE', "Reflective", ""),
        ('CLAMP_CONCENTRATION', "Clamp Concentration", "")]
    surf_class_type = EnumProperty(
        items=surf_class_type_enum, name="Type",
        description="Molecules are destroyed by absorptive surfaces, pass "
                    "through transparent, and \"bounce\" off of reflective.",
        update=cellblender_operators.check_surf_class_props)
    clamp_value = FloatProperty(name="Value", precision=4, min=0.0)
    clamp_value_str = StringProperty(
        name="Value", description="Concentration Units: Molar",
        update=cellblender_operators.update_clamp_value)
    status = StringProperty(name="Status")

    def build_data_model_from_properties ( self, context ):
        sc = self
        sc_dict = {}
        sc_dict['data_model_version'] = "DM_2014_10_24_1638"
        sc_dict['name'] = sc.name
        sc_dict['molecule'] = sc.molecule
        sc_dict['surf_class_orient'] = str(sc.surf_class_orient)
        sc_dict['surf_class_type'] = str(sc.surf_class_type)
        sc_dict['clamp_value'] = str(sc.clamp_value_str)
        return sc_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellSurfaceClassPropertiesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassPropertiesProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellSurfaceClassPropertiesProperty data model to current version." )

        self.name = dm["name"]
        self.molecule = dm["molecule"]
        self.surf_class_orient = dm["surf_class_orient"]
        self.surf_class_type = dm["surf_class_type"]
        self.clamp_value_str = dm["clamp_value"]
        self.clamp_value = float(self.clamp_value_str)

    def init_properties ( self, parameter_system ):
        self.name = "Molecule"
        self.molecule = ""
        self.surf_class_orient = '\''
        self.surf_class_type = 'REFLECTIVE'
        self.clamp_value_str = "0.0"
        self.clamp_value = float(self.clamp_value_str)

    def remove_properties ( self, context ):
        print ( "Removing all Surface Class Properties... no collections to remove." )


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )




class MCellSurfaceClassesProperty(bpy.types.PropertyGroup):
    """ Stores the surface class name and a list of its properties. """

    name = StringProperty(
        name="Surface Class Name", default="Surface_Class",
        description="This name can be selected in Assign Surface Classes.",
        update=cellblender_operators.check_surface_class)
    surf_class_props_list = CollectionProperty(
        type=MCellSurfaceClassPropertiesProperty, name="Surface Classes List")
    active_surf_class_props_index = IntProperty(
        name="Active Surface Class Index", default=0)
    status = StringProperty(name="Status")

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
                # scp.init_properties(context.scene.mcell.parameter_system)
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
                # sc.init_properties(context.scene.mcell.parameter_system)
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
                row.label(text="%s Properties:" % active_surf_class.name,
                          icon='FACESEL_HLT')
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
                    layout.prop_search(surf_class_props, "molecule",
                                       mcell.molecules, "molecule_list",
                                       icon='FORCE_LENNARDJONES')
                    layout.prop(surf_class_props, "surf_class_orient")
                    layout.prop(surf_class_props, "surf_class_type")
                    if (surf_class_props.surf_class_type == 'CLAMP_CONCENTRATION'):
                        layout.prop(surf_class_props, "clamp_value_str")


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




#Custom Properties


