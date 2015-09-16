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
This script stores the operators for CellBlender. As such, it is responsible
for what the buttons do when pressed (amongst other things).

"""

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



import cellblender
from . import data_model
from . import cellblender_preferences
from . import cellblender_release
from . import cellblender_objects
# import cellblender.data_model
# import cellblender_source_info
from . import cellblender_utils
#from cellblender.cellblender_utils import project_files_path
from cellblender.cellblender_utils import project_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl


# from . import ParameterSpace


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#CellBlender Operators:

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


def check_mod_surf_regions(self, context):
    """Make sure the surface class name is valid and format the list entry"""
    print ( "  Checking the mod_surf_region for " + str(self) )

    mcell = context.scene.mcell
    obj_list = mcell.model_objects.object_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = self
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
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
    elif not region_name in region_list:
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

    ######  commented out temporarily (causes names to not be built):
    active_mod_surf_regions.check_properties_after_building(context)
    # The previous line appears to cause the following problem:
    """
        Done removing all MCell Properties.
        Overwriting properites based on data in the data model dictionary
        Overwriting the parameter_system properties
        Parameter System building Properties from Data Model ...
        Overwriting the initialization properties
        Overwriting the define_molecules properties
        Overwriting the define_reactions properties
        Overwriting the release_sites properties
        Overwriting the define_release_patterns properties
        Overwriting the define_surface_classes properties
        Overwriting the modify_surface_regions properties
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: top")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: top")>
        Error: The object name ("") isn't a blender object
            Error Type: <class 'KeyError'>
            Error Value: 'bpy_prop_collection[key]: key "" not found'
        === Traceback Start ===
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 842, in check_mod_surf_regions
            region_list = bpy.data.objects[active_mod_surf_regions.object_name].mcell.regions.region_list
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 78, in execute
            data_model.upgrade_properties_from_data_model ( context )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/data_model.py", line 298, in upgrade_properties_from_data_model
            mcell.build_properties_from_data_model ( context, dm )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 4986, in build_properties_from_data_model
            self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 2755, in build_properties_from_data_model
            sr.build_properties_from_data_model ( context, s )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 774, in build_properties_from_data_model
            self.surf_class_name = dm["surf_class_name"]
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 892, in check_active_mod_surf_regions
            active_mod_surf_regions.check_properties_after_building(context)
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 780, in check_properties_after_building
            cellblender_operators.check_mod_surf_regions(self, context)
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 853, in check_mod_surf_regions
            traceback.print_stack()
        === Traceback End ===
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object:    Region: ")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object:    Region: ")>
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: ")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: ")>
        Overwriting the model_objects properties
        Data model contains Cube
        Overwriting the viz_output properties
        Overwriting the mol_viz properties
    """
    return


