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
This file contains the classes for CellBlender's Surface Regions.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

# blender imports
import bpy
from bpy.app.handlers import persistent
from bl_operators.presets import AddPresetBase
import mathutils

# python imports
import array
import glob
import os
import random
import re
import subprocess
import time
import shutil
import datetime

import sys, traceback


#from bpy.app.handlers import persistent
#import math
#import mathutils


# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_preferences
from . import cellblender_release
from . import cellblender_objects
from . import cellblender_utils

import cellblender.data_model as data_model
# import cellblender_source_info
from . import cellblender_utils
#from cellblender.cellblender_utils import mcell_files_path
from cellblender.cellblender_utils import mcell_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl



# Surface Regions callback functions


def check_mod_surf_regions(self, context):
    """Make sure the surface class name is valid and format the list entry"""
    # print ( "  Checking the mod_surf_region for " + str(self) )

    mcell = context.scene.mcell
    obj_list = mcell.model_objects.object_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = self
    surf_class_name = active_mod_surf_regions.surf_class_name
    if surf_class_name == "NONE":
        # this is an initial molecule release surface class and it has no name
        return    
    
    object_name = active_mod_surf_regions.object_name
    region_selection = active_mod_surf_regions.region_selection

    region_name = active_mod_surf_regions.region_name

    region_list = []

    # At some point during the building of properties the object name is "" which causes problems. So skip it for now.
    if len(object_name) > 0:
        try:
            region_list = bpy.data.objects[object_name].mcell.regions.region_list
        except KeyError as kerr:
            # The object name in mod_surf_regions isn't a blender object - print a stack trace ...
            print ( "Error: The object name (\"" + object_name + "\") isn't a blender object ... at this time?" )
            fail_error = sys.exc_info()
            print ( "    Error Type: " + str(fail_error[0]) )
            print ( "    Error Value: " + str(fail_error[1]) )
            tb = fail_error[2]
            # tb.print_stack()
            print ( "=== Traceback Start ===" )
            traceback.print_tb(tb)
            traceback.print_stack()
            print ( "=== Traceback End ===" )
            pass


    # Format the entry as it will appear in the Modify Surface Regions
    if region_selection == 'ALL':
        active_mod_surf_regions.name = ("Surface Class: %s   Object: %s   ALL" % (
                                            surf_class_name, object_name))
    else:
        active_mod_surf_regions.name = ("Surface Class: %s   Object: %s   "
                                        "Region: %s" % (
                                            surf_class_name, object_name,
                                            region_name))

    status = ""

    # Make sure the user entered surf class is in Defined Surface Classes list
    if not surf_class_name in surf_class_list:
        status = "Undefined surface class: %s" % surf_class_name
    # Make sure the user entered object name is in the Model Objects list
    elif not active_mod_surf_regions.object_name in obj_list:
        status = "Undefined object: %s" % active_mod_surf_regions.object_name
    # Make sure the user entered object name is in the object's
    # Surface Region list
    elif (not region_name in region_list) and (region_selection != 'ALL'):
        status = "Undefined region: %s" % region_name

    active_mod_surf_regions.status = status

    return


def check_active_mod_surf_regions(self, context):
    """This calls check_mod_surf_regions on the active mod_surf_regions"""

    mcell = context.scene.mcell
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    # This is a round-about way to call "check_mod_surf_regions" above
    # Maybe these functions belong in the MCellModSurfRegionsProperty class
    # Leave them here for now to not disturb too much code at once

    active_mod_surf_regions.check_properties_after_building(context)
    return



# Surface Regions Operators:


class MCELL_OT_mod_surf_regions_add(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_add"
    bl_label = "Assign Surface Class"
    bl_description = "Assign a surface class to a surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.add()
        mod_surf_regions.active_mod_surf_regions_index = len(
            mod_surf_regions.mod_surf_regions_list) - 1
        check_active_mod_surf_regions(self, context)

        return {'FINISHED'}


class MCELL_OT_mod_surf_regions_remove(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_remove"
    bl_label = "Remove Surface Class Assignment"
    bl_description = "Remove a surface class assignment from a surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.remove(
            mod_surf_regions.active_mod_surf_regions_index)
        mod_surf_regions.active_mod_surf_regions_index -= 1
        if (mod_surf_regions.active_mod_surf_regions_index < 0):
            mod_surf_regions.active_mod_surf_regions_index = 0

        return {'FINISHED'}


# Surface Regions Panels:


class MCELL_PT_object_selector(bpy.types.Panel):
    bl_label = "CellBlender - Object Selector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CellBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:
            layout.prop(mcell.object_selector, "filter", text="Object Filter:")
            row = layout.row(align=True)
            row.operator("mcell.select_filtered", text="Select Filtered")
            row.operator("mcell.deselect_filtered", text="Deselect Filtered")
            row=layout.row(align=True)
            row.operator("mcell.toggle_visibility_filtered",text="Visibility Filtered")
            row.operator("mcell.toggle_renderability_filtered",text="Renderability Filtered")




class MCELL_UL_check_mod_surface_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(text=item.status, icon='ERROR')
        else:
            layout.label(text=item.name, icon='CHECKMARK')



# Surface Regions Property Groups


class MCellModSurfRegionsProperty(bpy.types.PropertyGroup):
    """ Assign a surface class to a surface region. """

    name: StringProperty(name="Assign Surface Class")
    description: StringProperty(name="Description", default="")
    surf_class_name: StringProperty(
        name="Surface Class Name",
        description="This surface class will be assigned to the surface "
                    "region listed below.",
        update=check_active_mod_surf_regions)
    object_name: StringProperty(
        name="Object Name",
        description="A region on this object will have the above surface "
                    "class assigned to it.",
        update=check_active_mod_surf_regions)
    region_selection_enum = [
        ('ALL', "All Surfaces", ""),
        ('SEL', "Specified Region", "")]
    region_selection: EnumProperty(
        items=region_selection_enum, name="Region Selection",
        default='ALL',
        description="Choose between ALL Surfaces or Specified Regions. ")
    region_name: StringProperty(
        name="Region Name",
        description="This surface region will have the above surface class "
                    "assigned to it.",
        update=check_active_mod_surf_regions)
    status: StringProperty(name="Status")

    description_show_help: BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def remove_properties ( self, context ):
        print ( "Removing all Surface Regions Properties... no collections to remove." )


    def build_data_model_from_properties ( self, context ):
        print ( "Surface Region building Data Model" )
        sr_dm = {}
        sr_dm['data_model_version'] = "DM_2018_01_11_1330"
        sr_dm['name'] = self.name
        sr_dm['description'] = self.description
        sr_dm['surf_class_name'] = self.surf_class_name
        sr_dm['object_name'] = self.object_name
        sr_dm['region_selection'] = self.region_selection
        sr_dm['region_name'] = self.region_name
        return sr_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModSurfRegionsProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            # Make changes to move from DM_2014_10_24_1638 to DM_2015_09_25_1216
            # Added an "all_faces" flag to specify the "ALL" option (default to false)
            dm['all_faces'] = False
            dm['data_model_version'] = "DM_2015_09_25_1216"

        if dm['data_model_version'] == "DM_2015_09_25_1216":
            # Make changes to move from DM_2015_09_25_1216 to DM_2015_11_06_1732
            # Changed representation from "Boolean all_faces" to "Enum region_selection"
            if dm['all_faces']:
                dm['region_selection'] = 'ALL'
            else:
                dm['region_selection'] = 'SEL'
            dm.pop('all_faces')
            dm['data_model_version'] = "DM_2015_11_06_1732"

        if dm['data_model_version'] == "DM_2015_11_06_1732":
            # Change on January 11th, 2018 to add a description field to modified surface regions
            dm['description'] = ""
            dm['data_model_version'] = "DM_2018_01_11_1330"

        if dm['data_model_version'] == "DM_2020_07_12_1600":
            print("WARNING: Initial region molecules are not supported by cellblender yet, they are ignored.")
            dm['description'] = "Initial region molecules are not supported by cellblender yet, they were ignored."
            dm['data_model_version'] = "DM_2018_01_11_1330"
            
        if dm['data_model_version'] != "DM_2018_01_11_1330":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsProperty data_model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2018_01_11_1330":
            data_model.handle_incompatible_data_model ( "Error: MCellModSurfRegionsProperty data model is not current." )

        self.name = dm["name"]
        self.description = dm["description"]
        if "surf_class_name" in dm:
            self.surf_class_name = dm["surf_class_name"]
            self.object_name = dm["object_name"]
            self.region_selection = dm['region_selection']
            self.region_name = dm["region_name"]
        else:
            self.surf_class_name = "NONE"

    def check_properties_after_building ( self, context ):
        # print ( "Implementing check_properties_after_building for " + str(self) )
        # print ( "Calling check_mod_surf_regions on object named: " + self.object_name )
        check_mod_surf_regions(self, context)


class MCellModSurfRegionsPropertyGroup(bpy.types.PropertyGroup):
    mod_surf_regions_list: CollectionProperty( type=MCellModSurfRegionsProperty, name="Assign Surface Class List")
    active_mod_surf_regions_index: IntProperty(
        name="Active Assign Surface Class Index", default=0)

    def build_data_model_from_properties ( self, context ):
        print ( "Assign Surface Class List building Data Model" )
        sr_dm = {}
        sr_dm['data_model_version'] = "DM_2014_10_24_1638"
        sr_list = []
        for sr in self.mod_surf_regions_list:
            sr_list.append ( sr.build_data_model_from_properties(context) )
        sr_dm['modify_surface_regions_list'] = sr_list
        return sr_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModSurfRegionsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsPropertyGroup data model to current version." )
            return None

        if "modify_surface_regions_list" in dm:
            for item in dm["modify_surface_regions_list"]:
                if MCellModSurfRegionsProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: MCellModSurfRegionsPropertyGroup data model is not current." )

        while len(self.mod_surf_regions_list) > 0:
            self.mod_surf_regions_list.remove(0)
        if "modify_surface_regions_list" in dm:
            for s in dm["modify_surface_regions_list"]:
                self.mod_surf_regions_list.add()
                self.active_mod_surf_regions_index = len(self.mod_surf_regions_list)-1
                sr = self.mod_surf_regions_list[self.active_mod_surf_regions_index]
                # sr.init_properties(context.scene.mcell.parameter_system)
                sr.build_properties_from_data_model ( context, s )


    def check_properties_after_building ( self, context ):
        print ( "Implementing check_properties_after_building for " + str(self) )
        for sr in self.mod_surf_regions_list:
            sr.check_properties_after_building(context)

    def remove_properties ( self, context ):
        print ( "Removing all Surface Regions Properties ..." )
        for item in self.mod_surf_regions_list:
            item.remove_properties(context)
        self.mod_surf_regions_list.clear()
        self.active_mod_surf_regions_index = 0
        print ( "Done removing all Surface Regions Properties." )


    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            # mod_surf_regions = context.scene.mcell.mod_surf_regions

            row = layout.row()
            if not mcell.surface_classes.surf_class_list:
                row.label(text="Define at least one surface class", icon='ERROR')
            elif not mcell.model_objects.object_list:
                row.label(text="Add a mesh to the Model Objects list",
                          icon='ERROR')
            else:
                col = row.column()
                col.template_list("MCELL_UL_check_mod_surface_regions",
                                  "mod_surf_regions", self,
                                  "mod_surf_regions_list", self,
                                  "active_mod_surf_regions_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.mod_surf_regions_add", icon='ADD', text="")
                col.operator("mcell.mod_surf_regions_remove", icon='REMOVE',
                             text="")
                if self.mod_surf_regions_list:
                    active_mod_surf_regions =  self.mod_surf_regions_list[self.active_mod_surf_regions_index]

                    # Note that these panels don't have help on each item. To remain consistent with other items, don't add help for "description".
                    # helptext = "Modify Surface Region Description - \nUser-specified text describing this modified surface region"
                    # mcell.parameter_system.draw_prop_with_help ( layout, "Description", active_mod_surf_regions, "description", "description_show_help", active_mod_surf_regions.description_show_help, helptext )
                    # Remove these two lines if drawing with help:
                    row = layout.row()
                    row.prop ( active_mod_surf_regions, "description" )

                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "surf_class_name",
                                    mcell.surface_classes, "surf_class_list",
                                    icon='LIGHTPROBE_CUBEMAP')
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "object_name",
                                    mcell.model_objects, "object_list",
                                    icon='MESH_ICOSPHERE')
                    if active_mod_surf_regions.object_name:
                        try:
                            regions = bpy.data.objects[
                                active_mod_surf_regions.object_name].mcell.regions
                            layout.prop ( active_mod_surf_regions, "region_selection" )

                            if active_mod_surf_regions.region_selection == 'SEL':
                                layout.prop_search(active_mod_surf_regions,
                                                   "region_name", regions,
                                                   "region_list", icon='UV_DATA')
                        except KeyError:
                            pass


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



classes = ( 
            MCELL_OT_mod_surf_regions_add,
            MCELL_OT_mod_surf_regions_remove,
            MCELL_PT_object_selector,
            MCELL_UL_check_mod_surface_regions,
            MCellModSurfRegionsProperty,
            MCellModSurfRegionsPropertyGroup,
          )
 
def register():
    for cls in classes:
      bpy.utils.register_class(cls)
 
def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

