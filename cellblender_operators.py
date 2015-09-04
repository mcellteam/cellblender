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

import cellblender
from . import data_model
from . import cellblender_preferences
from . import cellblender_release
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


class MCELL_OT_upgrade(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.upgrade"
    bl_label = "Upgrade Blend File"
    bl_description = "Upgrade the data from a previous version of CellBlender"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Upgrade Operator called" )
        data_model.upgrade_properties_from_data_model ( context )
        return {'FINISHED'}


class MCELL_OT_upgradeRC3(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.upgraderc3"
    bl_label = "Upgrade RC3/4 Blend File"
    bl_description = "Upgrade the data from an RC3/4 version of CellBlender"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Upgrade RC3 Operator called" )
        data_model.upgrade_RC3_properties_from_data_model ( context )
        return {'FINISHED'}



class MCELL_OT_delete(bpy.types.Operator):
    """This is the Delete operator called when the user presses the "Delete Properties" button"""
    bl_idname = "mcell.delete"
    bl_label = "Delete CellBlender Collection Properties"
    bl_description = "Delete CellBlender Collection Properties"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Deleting CellBlender Collection Properties" )
        mcell = context.scene.mcell
        mcell.remove_properties(context)
        print ( "Finished Deleting CellBlender Collection Properties" )
        return {'FINISHED'}



############### DB: The following two classes are included to create a parameter input panel: only relevant for BNG, SBML or other model import #################
class MCELL_OT_parameter_add(bpy.types.Operator):
    bl_idname = "mcell.parameter_add"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.parameters.parameter_list.add()
        mcell.parameters.active_par_index = len(mcell.parameters.parameter_list)-1
        mcell.parameters.parameter_list[
            mcell.parameters.active_par_index].name = "Parameter"
        return {'FINISHED'}
	
class MCELL_OT_parameter_remove(bpy.types.Operator):
    bl_idname = "mcell.parameter_remove"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.parameters.parameter_list.remove(mcell.parameters.active_par_index)
        mcell.parameters.active_par_index = mcell.parameters.active_par_index-1
        if (mcell.parameters.active_par_index < 0):
            mcell.parameters.active_par_index = 0

        return {'FINISHED'}	
	
#########################################################################################################################################


class MCELL_OT_add_variable_rate_constant(bpy.types.Operator):
    """ Create variable rate constant text object from a file.

    Create a text object from an existing text file that represents the
    variable rate constant. This ensures that the variable rate constant is
    actually stored in the blend. Although, ultimately, this text object will
    be exported as another text file in the project directory when the MDLs are
    exported so it can be used by MCell.
    """

    bl_idname = "mcell.variable_rate_add"
    bl_label = "Add Variable Rate Constant"
    bl_description = "Add a variable rate constant to a reaction."
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        mcell = context.scene.mcell
        rxn = mcell.reactions.reaction_list[
            mcell.reactions.active_rxn_index]
        
        rxn.load_variable_rate_file ( context, self.filepath )
        
        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


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



@persistent
def mcell_valid_update(context):
    """ Check whether the mcell executable in the .blend file is valid """
    print ( "load post handler: cellblender_operators.mcell_valid_update() called" )
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    binary_path = mcell.cellblender_preferences.mcell_binary
    mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )
    # print ( "mcell_binary_valid = ", mcell.cellblender_preferences.mcell_binary_valid )


@persistent
def init_properties(context):
    """ Initialize MCell properties if not already initialized """
    print ( "load post handler: cellblender_operators.init_properties() called" )
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    if not mcell.initialized:
        mcell.init_properties()
        mcell.initialized = True



class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("MCELL_OT_export_project.execute()")

        if context.scene.mcell.cellblender_preferences.lockout_export:
            print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            self.report({'INFO'}, "Exporting is Locked Out")
        else:
            print(" Scene name =", context.scene.name)

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")

            # Change the actual scene name to the legal MCell Name
            context.scene.name = scene_name

            mcell = context.scene.mcell

            # Force the project directory to be where the .blend file lives
            model_objects_update(context)

            filepath = project_files_path()
            os.makedirs(filepath, exist_ok=True)

            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            mcell.project_settings.base_name = scene_name

            #filepath = os.path.join(
            #   filepath, mcell.project_settings.base_name + ".main.mdl")
            filepath = os.path.join(filepath, scene_name + ".main.mdl")
    #        bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)
            export_mcell_mdl.save(context, filepath)

            # These two branches of the if statement seem identical ?

            #if mcell.export_project.export_format == 'mcell_mdl_unified':
            #    filepath = os.path.join(os.path.dirname(bpy.data.filepath),
            #                            (mcell.project_settings.base_name +
            #                            ".main.mdl"))
            #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)
            #elif mcell.export_project.export_format == 'mcell_mdl_modular':
            #    filepath = os.path.join(os.path.dirname(bpy.data.filepath),
            #                            (mcell.project_settings.base_name +
            #                            ".main.mdl"))
            #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)

            self.report({'INFO'}, "Project Exported")

        return {'FINISHED'}



import sys, traceback



class MCELL_OT_select_filtered(bpy.types.Operator):
    bl_idname = "mcell.select_filtered"
    bl_label = "Select Filtered"
    bl_description = "Select objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mcell = scn.mcell
        objs = scn.objects

        filter = mcell.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = True

        return {'FINISHED'}


class MCELL_OT_deselect_filtered(bpy.types.Operator):
    bl_idname = "mcell.deselect_filtered"
    bl_label = "Deselect Filtered"
    bl_description = "Deselect objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mcell = scn.mcell
        objs = scn.objects

        filter = mcell.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = False

        return {'FINISHED'}


class MCELL_OT_toggle_visibility_filtered(bpy.types.Operator):
  bl_idname = "mcell.toggle_visibility_filtered"
  bl_label = "Visibility Filtered"
  bl_description = "Toggle visibility of objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mcell = scn.mcell
    objs = scn.objects

    filter = mcell.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.hide = not obj.hide

    return {'FINISHED'}


class MCELL_OT_toggle_renderability_filtered(bpy.types.Operator):
  bl_idname = "mcell.toggle_renderability_filtered"
  bl_label = "Renderability Filtered"
  bl_description = "Toggle renderability of objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mcell = scn.mcell
    objs = scn.objects

    filter = mcell.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.hide_render= not obj.hide_render

    return {'FINISHED'}


# Rebuild Model Objects List from Scratch
#   This is required to catch changes in names of objects.
#   Note: This function is also registered as a load_post and save_pre handler
@persistent
def model_objects_update(context):
    # print ( "cellblender_operators.model_objects_update() called" )
    if not context:
        context = bpy.context

    mcell = context.scene.mcell
    mobjs = mcell.model_objects
    sobjs = context.scene.objects

    model_obj_names = [obj.name for obj in sobjs if obj.mcell.include]

    # Note: This bit only needed to convert
    #       old model object list (pre 0.1 rev_55) to new style.
    #       Old style did not have obj.mcell.include Boolean Property.
    if ((len(model_obj_names) == 0) & (len(mobjs.object_list) > 0)):
        for i in range(len(mobjs.object_list)-1):
            obj = sobjs.get(mobjs.object_list[i].name)
            if obj:
                obj.mcell.include = True
        model_obj_names = [
            obj.name for obj in sobjs if obj.mcell.include]

    # Update the model object list from objects marked obj.mcell.include = True
    if (len(model_obj_names) > 0):
        model_obj_names.sort()

        for i in range(len(mobjs.object_list)-1, -1, -1):
            mobjs.object_list.remove(i)

        active_index = mobjs.active_obj_index
        for obj_name in model_obj_names:
            mobjs.object_list.add()
            mobjs.active_obj_index = len(mobjs.object_list)-1
            mobjs.object_list[mobjs.active_obj_index].name = obj_name
            scene_object = sobjs[obj_name]
            # Set an error status if object is not triangulated
            for face in scene_object.data.polygons:
                if not (len(face.vertices) == 3):
                    status = "Object is not triangulated: %s" % (obj_name)
                    mobjs.object_list[mobjs.active_obj_index].status = status
                    break

        mobjs.active_obj_index = active_index

        # We check release sites are valid here in case a user adds an object
        # referenced in a release site after adding the release site itself.
        # (e.g. Add Cube shaped release site. Then add Cube.)
        release_list = mcell.release_sites.mol_release_list
        save_release_idx = mcell.release_sites.active_release_index
        # check_release_site_wrapped acts on the active release site, so we
        # need to increment it and then check
        for rel_idx, _ in enumerate(release_list):
            mcell.release_sites.active_release_index = rel_idx
            cellblender_release.check_release_site_wrapped(context)
        # Restore the active index
        mcell.release_sites.active_release_index = save_release_idx

    return


class MCELL_OT_model_objects_add(bpy.types.Operator):
    bl_idname = "mcell.model_objects_add"
    bl_label = "Model Objects Include"
    bl_description = ("Include objects selected in 3D View Window in Model "
                      "Objects export list")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        # From the list of selected objects, only add MESH objects.
        objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objs:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY',
                                               ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')
            obj.mcell.include = True

        model_objects_update(context)

#        for obj in objs:
#            # Prevent duplicate entries
#            if not obj.name in mcell.model_objects.object_list:
#                mcell.model_objects.object_list.add()
#                mcell.model_objects.active_obj_index = len(
#                    mcell.model_objects.object_list)-1
#                mcell.model_objects.object_list[
#                    mcell.model_objects.active_obj_index].name = obj.name


        return {'FINISHED'}


class MCELL_OT_model_objects_remove(bpy.types.Operator):
    bl_idname = "mcell.model_objects_remove"
    bl_label = "Model Objects Remove"
    bl_description = "Remove selected item from Model Objects export list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        mobjs = mcell.model_objects
        sobjs = context.scene.objects

        if (len(mobjs.object_list) > 0):
            obj = sobjs.get(mobjs.object_list[mobjs.active_obj_index].name)
            if obj:
                obj.mcell.include = False

                mobjs.object_list.remove(mobjs.active_obj_index)
                mobjs.active_obj_index -= 1
                if (mobjs.active_obj_index < 0):
                    mobjs.active_obj_index = 0
        
        model_objects_update(context)

        return {'FINISHED'}


def check_model_object(self, context):
    """Checks for illegal object name"""

    mcell = context.scene.mcell
    model_object_list = mcell.model_objects.object_list
    model_object = model_object_list[mcell.model_objects.active_obj_index]

    # print ("Checking name " + model_object.name )

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    model_object_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(model_object_filter, model_object.name)
    if m is None:
        status = "Object name error: %s" % (model_object.name)

    model_object.status = status

    return


class MCELL_OT_set_molecule_glyph(bpy.types.Operator):
    bl_idname = "mcell.set_molecule_glyph"
    bl_label = "Set Molecule Glyph"
    bl_description = "Set molecule glyph to desired shape in glyph library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        meshes = bpy.data.meshes
        mcell.molecule_glyphs.status = ""
        select_objs = context.selected_objects
        if (len(select_objs) != 1):
            mcell.molecule_glyphs.status = "Select One Molecule"
            return {'FINISHED'}
        if (select_objs[0].type != 'MESH'):
            mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
            return {'FINISHED'}

        mol_obj = select_objs[0]
        mol_shape_name = mol_obj.name

        glyph_name = mcell.molecule_glyphs.glyph

        # There may be objects in the scene with the same name as the glyphs in
        # the glyph library, so we need to deal with this possibility
        new_glyph_name = glyph_name
        if glyph_name in meshes:
            # pattern: glyph name, period, numbers. (example match: "Cube.001")
            pattern = re.compile(r'%s(\.\d+)' % glyph_name)
            competing_names = [m.name for m in meshes if pattern.match(m.name)]
            # example: given this: ["Cube.001", "Cube.3"], make this: [1, 3]
            trailing_nums = [int(n.split('.')[1]) for n in competing_names]
            # remove dups & sort... better way than list->set->list?
            trailing_nums = list(set(trailing_nums))
            trailing_nums.sort()
            i = 0
            gap = False
            for i in range(0, len(trailing_nums)):
                if trailing_nums[i] != i+1:
                    gap = True
                    break
            if not gap and trailing_nums:
                i+=1
            new_glyph_name = "%s.%03d" % (glyph_name, i + 1)

        if (bpy.app.version[0] > 2) or ( (bpy.app.version[0]==2) and (bpy.app.version[1] > 71) ):
          bpy.ops.wm.link(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)
        else:
          bpy.ops.wm.link_append(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)

        mol_mat = mol_obj.material_slots[0].material
        new_mol_mesh = meshes[new_glyph_name]
        mol_obj.data = new_mol_mesh
        meshes.remove(meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        new_mol_mesh.materials.append(mol_mat)

        return {'FINISHED'}

"""

class MCELL_OT_rxn_output_add(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_add"
    bl_label = "Add Reaction Data Output"
    bl_description = "Add new reaction data output to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.add()
        mcell.rxn_output.active_rxn_output_index = len(
            mcell.rxn_output.rxn_output_list)-1
        check_rxn_output(self, context)

        return {'FINISHED'}


class MCELL_OT_rxn_output_remove(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_remove"
    bl_label = "Remove Reaction Data Output"
    bl_description = "Remove selected reaction data output from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.remove(
            mcell.rxn_output.active_rxn_output_index)
        mcell.rxn_output.active_rxn_output_index -= 1
        if (mcell.rxn_output.active_rxn_output_index < 0):
            mcell.rxn_output.active_rxn_output_index = 0

        if mcell.rxn_output.rxn_output_list:
            check_rxn_output(self, context)

        return {'FINISHED'}

def check_rxn_output(self, context):
    # Format reaction data output. 

    mcell = context.scene.mcell
    rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output = rxn_output_list[
        mcell.rxn_output.active_rxn_output_index]
    mol_list = mcell.molecules.molecule_list
    reaction_list = mcell.reactions.reaction_name_list
    molecule_name = rxn_output.molecule_name
    reaction_name = rxn_output.reaction_name
    obj_list = mcell.model_objects.object_list
    object_name = rxn_output.object_name
    region_name = rxn_output.region_name
    rxn_output_name = ""

    status = ""
    if rxn_output.rxn_or_mol == 'Reaction':
        count_name = reaction_name
        name_list = reaction_list
    elif rxn_output.rxn_or_mol == 'Molecule':
        count_name = molecule_name
        name_list = mol_list
    else:
        count_name = molecule_name
        rxn_output.status = ""
        #rxn_output.name = rxn_output.mdl_string

        return

    try:
        region_list = bpy.data.objects[object_name].mcell.regions.region_list
    except KeyError:
        # The object name isn't a blender object
        region_list = []


    # Check for illegal names (Starts with a letter. No special characters.)
    count_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    c = re.match(count_filter, count_name)
    if c is None:
        status = "Name error: %s" % (count_name)
    else:
        # Check for undefined molecule or reaction names
        c_name = c.group(1)
        if not c_name in name_list:
            status = "Undefined: %s" % (c_name)

    # Use different formatting depending on where we are counting
    if rxn_output.count_location == 'World':
        rxn_output_name = "Count %s in World" % (count_name)
    elif rxn_output.count_location == 'Object':
        if not object_name in obj_list:
            status = "Undefined object: %s" % object_name
        else:
            rxn_output_name = "Count %s in/on %s" % (
                count_name, object_name)
    elif rxn_output.count_location == 'Region':
        if not region_name in region_list:
            status = "Undefined region: %s" % region_name
        else:
            rxn_output_name = "Count %s in/on %s[%s]" % (
                count_name, object_name, region_name)

    # Only update reaction output if necessary to avoid infinite recursion
    if rxn_output.name != rxn_output_name:
        rxn_output.name = rxn_output_name

    # Check for duplicate reaction data
    rxn_output_keys = rxn_output_list.keys()
    if rxn_output_keys.count(rxn_output.name) > 1 and not status:
        status = "Duplicate reaction output: %s" % (rxn_output.name)

    rxn_output.status = status

    return
"""

def update_delay(self, context):
    """ Store the release pattern delay as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    delay_str = release_pattern.delay_str

    (delay, status) = cellblender_utils.check_val_str(delay_str, 0, None)

    if status == "":
        release_pattern.delay = delay
    else:
        release_pattern.delay_str = "%g" % (release_pattern.delay)


def update_release_interval(self, context):
    """ Store the release interval as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    release_interval_str = release_pattern.release_interval_str

    (release_interval, status) = cellblender_utils.check_val_str(
        release_interval_str, 1e-12, None)

    if status == "":
        release_pattern.release_interval = release_interval
    else:
        release_pattern.release_interval_str = "%g" % (
            release_pattern.release_interval)


def update_train_duration(self, context):
    """ Store the train duration as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    train_duration_str = release_pattern.train_duration_str

    (train_duration, status) = cellblender_utils.check_val_str(train_duration_str, 1e-12, None)

    if status == "":
        release_pattern.train_duration = train_duration
    else:
        release_pattern.train_duration_str = "%g" % (
            release_pattern.train_duration)


def update_train_interval(self, context):
    """ Store the train interval as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    train_interval_str = release_pattern.train_interval_str

    (train_interval, status) = cellblender_utils.check_val_str(train_interval_str, 1e-12, None)

    if status == "":
        release_pattern.train_interval = train_interval
    else:
        release_pattern.train_interval_str = "%g" % (
            release_pattern.train_interval)


