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
This file contains the classes for CellBlender's Partitioning System.

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
from . import cellblender_utils
from . import data_model



class MCELL_OT_create_partitions_object(bpy.types.Operator):
    bl_idname = "mcell.create_partitions_object"
    bl_label = "Show Partition Boundaries"
    bl_description = "Create a representation of the partition boundaries"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene_objs = scene.objects
        objs = bpy.data.objects
        meshes = bpy.data.meshes
        if not "partitions" in objs:
            # Save object selections and mode
            object_list = bpy.context.scene.collection.children[0].objects
            selected_objs = [obj for obj in object_list if obj.select_get()]
            for obj in selected_objs:
                obj.select_set(False)
            active_object = bpy.context.active_object
            active_object_mode = active_object.mode
            bpy.ops.object.mode_set(mode='OBJECT')
            # Add a box that represents the partitions' boundaries
            bpy.ops.mesh.primitive_cube_add()
            partition_object = bpy.context.active_object
            # Restore selections and mode
            context.view_layer.objects.active = active_object
            for obj in selected_objs:
                obj.select_set(True)
            bpy.ops.object.mode_set(mode=active_object_mode)
            partition_object.select_set(False)
            # Prevent user from manipulating the box, because I don't yet have
            # a good way of updating the partitions when the box object is
            # moved/scaled in the 3D view window
            partition_object.hide_select = True
            # Set draw_type to wireframe so the user can see what's inside
            partition_object.display_type = 'WIRE'
            partition_object.name = "partitions"
            partition_mesh = partition_object.data
            partition_mesh.name = "partitions"
            
            if context.scene.mcell.cellblender_preferences.mcell4_mode:
                transform_all_axes_partition_boundary(self, context)
            else:
                transform_x_partition_boundary(self, context)
                transform_y_partition_boundary(self, context)
                transform_z_partition_boundary(self, context)

        return {'FINISHED'}


class MCELL_OT_remove_partitions_object(bpy.types.Operator):
    bl_idname = "mcell.remove_partitions_object"
    bl_label = "Hide Partition Boundaries"
    bl_description = "Remove a representation of the partition boundaries"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene_objects = context.scene.collection.children[0].objects
        objects = bpy.data.objects
        meshes = bpy.data.meshes
        if "partitions" in scene_objects:
            partition_object = scene_objects["partitions"]
            partition_mesh = partition_object.data
            scene_objects.unlink(partition_object)
            objects.remove(partition_object)
            meshes.remove(partition_mesh)

        return {'FINISHED'}


class MCELL_OT_auto_generate_boundaries(bpy.types.Operator):
    bl_idname = "mcell.auto_generate_boundaries"
    bl_label = "Automatically Generate Boundaries"
    bl_description = ("Automatically generate partition boundaries based off "
                      "of Model Objects list")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell4_mode = mcell.cellblender_preferences.mcell4_mode
        partitions = mcell.partitions
        object_list = mcell.model_objects.object_list
        first_time = True
        for obj in object_list:
            try:
                obj = bpy.data.objects[obj.name]
                obj_matrix = obj.matrix_world
                vertices = obj.data.vertices
                for vert in vertices:
                    # Transform local coordinates to global coordinates
                    (x, y, z) = obj_matrix @ vert.co
                    if first_time:
                        x_min = x_max = x
                        y_min = y_max = y
                        z_min = z_max = z
                        first_time = False
                    else:
                        # Check for x max and min
                        if x > x_max:
                            x_max = x
                        elif x < x_min:
                            x_min = x
                        # Check for y max and min
                        if y > y_max:
                            y_max = y
                        elif y < y_min:
                            y_min = y
                        # Check for z max and min
                        if z > z_max:
                            z_max = z
                        elif z < z_min:
                            z_min = z
                    
            # In case object was deleted, but still in model objects list
            except KeyError:
                pass

        # If we don't iterate through object_list, then we don't have values
        # for x_min, x_max, etc, therefore we need to skip over setting bounds
        if not first_time:
                                        
            if mcell4_mode:
                partitions.start = min(x_min, y_min, z_min)
                partitions.end = max(x_max, y_max, z_max)
            else:
                partitions.x_start = x_min
                partitions.x_end = x_max
                partitions.y_start = y_min
                partitions.y_end = y_max
                partitions.z_start = z_min
                partitions.z_end = z_max

        return {'FINISHED'}



def transform_x_partition_boundary(self, context):
    """ Transform the partition object along the x-axis. """

    partitions = context.scene.mcell.partitions
    x_start = partitions.x_start
    x_end = partitions.x_end
    x_step = partitions.x_step
    partitions.x_step = check_partition_step(
        self, context, x_start, x_end, x_step)
    transform_partition_boundary(self, context, x_start, x_end, 0)


def transform_y_partition_boundary(self, context):
    """ Transform the partition object along the y-axis. """

    partitions = context.scene.mcell.partitions
    y_start = partitions.y_start
    y_end = partitions.y_end
    y_step = partitions.y_step
    partitions.y_step = check_partition_step(
        self, context, y_start, y_end, y_step)
    transform_partition_boundary(self, context, y_start, y_end, 1)


def transform_z_partition_boundary(self, context):
    """ Transform the partition object along the z-axis. """

    partitions = context.scene.mcell.partitions
    z_start = partitions.z_start
    z_end = partitions.z_end
    z_step = partitions.z_step
    partitions.z_step = check_partition_step(
        self, context, z_start, z_end, z_step)
    transform_partition_boundary(self, context, z_start, z_end, 2)


def transform_all_axes_partition_boundary(self, context):
    """ Transform the partition object along all axes """
    partitions = context.scene.mcell.partitions
    start = partitions.start
    end = partitions.end
    step = partitions.step
    partitions.step = check_partition_step(
        self, context, start, end, step)
    transform_partition_boundary(self, context, start, end, -1)


def transform_partition_boundary(self, context, start, end, xyz_index):
    """ Transform the partition object along the provided axis.

    Change the scaling and location of the cube that represents partition
    boundaries. Also, make sure the step lengths are valid.
    
    xyz_index -1 is used for MCell4
    """

    difference = end-start
    # Scale works this way, because default Cube is 2x2x2
    half_difference = scale = difference/2
    # The object center of the partition boundaries (i.e. the box)
    location = start + half_difference
    # Move the partition boundary object if it exists
    if "partitions" in bpy.data.objects:
        partition_object = bpy.data.objects["partitions"]
        if xyz_index == -1:
            for i in range(3):
                partition_object.location[i] = location
                partition_object.scale[i] = scale
        else:
            partition_object.location[xyz_index] = location
            partition_object.scale[xyz_index] = scale
            


def check_x_partition_step(self, context):
    """ Make sure the partition's step along the x-axis is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        x_start = partitions.x_start
        x_end = partitions.x_end
        x_step = partitions.x_step
        partitions.x_step = check_partition_step(
            self, context, x_start, x_end, x_step)
        partitions.recursion_flag = False


def check_y_partition_step(self, context):
    """ Make sure the partition's step along the y-axis is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        y_start = partitions.y_start
        y_end = partitions.y_end
        y_step = partitions.y_step
        partitions.y_step = check_partition_step(
            self, context, y_start, y_end, y_step)
        partitions.recursion_flag = False


def check_z_partition_step(self, context):
    """ Make sure the partition's step along the z-axis is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        z_start = partitions.z_start
        z_end = partitions.z_end
        z_step = partitions.z_step
        partitions.z_step = check_partition_step(
            self, context, z_start, z_end, z_step)
        partitions.recursion_flag = False


def check_all_axes_partition_step(self, context):
    """ Make sure the partition's step is valid. """

    partitions = context.scene.mcell.partitions
    if not partitions.recursion_flag:
        partitions.recursion_flag = True
        start = partitions.start
        end = partitions.end
        step = partitions.step
        partitions.z_step = check_partition_step(
            self, context, start, end, step)
        partitions.recursion_flag = False
        
        
def check_partition_step(self, context, start, end, step):
    """ Make sure the partition's step along the provided axis is valid. """

    difference = end-start
    # Scale works this way, because default Cube is 2x2x2
    half_difference = scale = difference/2
    # The object center of the partition boundaries (i.e. the box)
    location = start + half_difference
    # Ensure step length isn't larger than partition range
    if abs(step) > abs(difference):
        step = difference
    # Make sure partition range and step length are compatible
    # Good:
    # "PARTITION_X = [[-1.0 TO 1.0 STEP 0.2]]" or
    # "PARTITION_X = [[1.0 TO -1.0 STEP -0.2]]"
    # Bad:
    # "PARTITION_X = [[-1.0 TO 1.0 STEP -0.2]]" or
    # "PARTITION_X = [[1.0 TO -1.0 STEP 0.2]]"
    # x_scale < 0 means that x_start > x_end (e.g "1.0 TO -1.0")
    if ((scale < 0 and step > 0) or (scale > 0 and step < 0)):
        step *= -1
    return step




class MCellPartitionsPropertyGroup(bpy.types.PropertyGroup):
    include: BoolProperty(
        name="Include Partitions",
        description="Partitions are a way of speeding up a simulation if used "
                    "properly.",
        default=False)
    recursion_flag: BoolProperty(
        name="Recursion Flag",
        description="Flag to prevent infinite recursion",
        default=False)
    x_start: FloatProperty(
        name="X Start", default=-1, precision=3,
        description="The start of the partitions on the x-axis",
        update=transform_x_partition_boundary)
    x_end: FloatProperty(
        name="X End", default=1, precision=3,
        description="The end of the partitions on the x-axis",
        update=transform_x_partition_boundary)
    x_step: FloatProperty(
        name="X Step", default=0.05, precision=3,
        description="The distance between partitions on the x-axis",
        update=check_x_partition_step)
    y_start: FloatProperty(
        name="Y Start", default=-1, precision=3,
        description="The start of the partitions on the y-axis",
        update=transform_y_partition_boundary)
    y_end: FloatProperty(
        name="Y End", default=1, precision=3,
        description="The end of the partitions on the y-axis",
        update=transform_y_partition_boundary)
    y_step: FloatProperty(
        name="Y Step", default=0.05, precision=3,
        description="The distance between partitions on the y-axis",
        update=check_y_partition_step)
    z_start: FloatProperty(
        name="Z Start", default=-1, precision=3,
        description="The start of the partitions on the z-axis",
        update=transform_z_partition_boundary)
    z_end: FloatProperty(
        name="Z End", default=1, precision=3,
        description="The end of the partitions on the z-axis",
        update=transform_z_partition_boundary)
    z_step: FloatProperty(
        name="Z Step", default=0.05, precision=3,
        description="The distance between partitions on the z-axis",
        update=check_z_partition_step)
    
    # mcell4
    start: FloatProperty(
        name="Start", default=-10, precision=3,
        description="The x,y,z coordinates of the lowest left bottom point",
        update=transform_all_axes_partition_boundary)

    end: FloatProperty(
        name="End", default=10, precision=3,
        description="The x,y,z coordinates of the upper right top point",
        update=transform_all_axes_partition_boundary)

    step: FloatProperty(
        name="Step", default=0.1, precision=3,
        description="The distance between subpartitions",
        update=check_all_axes_partition_step)


    def build_data_model_from_properties ( self, context ):
        print ( "Partitions building Data Model" )
        
        mcell = context.scene.mcell
        mcell4_mode = mcell.cellblender_preferences.mcell4_mode
        
        dm_dict = {}
        dm_dict['data_model_version'] = "DM_2016_04_15_1600"
        
        if mcell4_mode:
            dm_dict['include'] = True
            dm_dict['recursion_flag'] = False # in case some tools require it in the data model
            dm_dict['x_start'] = "%g" % (self.start)
            dm_dict['x_end'] =   "%g" % (self.end)
            dm_dict['x_step'] =  "%g" % (self.step)
            dm_dict['y_start'] = "%g" % (self.start)
            dm_dict['y_end'] =   "%g" % (self.end)
            dm_dict['y_step'] =  "%g" % (self.step)
            dm_dict['z_start'] = "%g" % (self.start)
            dm_dict['z_end'] =   "%g" % (self.end)
            dm_dict['z_step'] =  "%g" % (self.step)
        else:
            dm_dict['include'] = self.include==True
            dm_dict['recursion_flag'] = self.recursion_flag==True
            dm_dict['x_start'] = "%g" % (self.x_start)
            dm_dict['x_end'] =   "%g" % (self.x_end)
            dm_dict['x_step'] =  "%g" % (self.x_step)
            dm_dict['y_start'] = "%g" % (self.y_start)
            dm_dict['y_end'] =   "%g" % (self.y_end)
            dm_dict['y_step'] =  "%g" % (self.y_step)
            dm_dict['z_start'] = "%g" % (self.z_start)
            dm_dict['z_end'] =   "%g" % (self.z_end)
            dm_dict['z_step'] =  "%g" % (self.z_step)
        return dm_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellPartitionsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            # There was a bug in earlier exports of the data model which saved self.z_start to dm['x_start']
            # Similarly, self.z_start was loaded from dm['x_start'] when the model was read back into properties
            # Here's the error code (fixed in this version):
            #  build_data_model_from_properties:
            #    dm_dict['x_start'] = str(self.z_start)
            #  build_properties_from_data_model:
            #    self.z_start = float(dm["x_start"])
            # So those data models did not have a 'z_start' key in their partition dictionary at all.
            # The originally intended 'x_start' in those data models had likely been over-written by 'z_start'
            # To upgrade this, add a 'z_start' key with the value of 'x_start' (which was the previous z_start)
            dm['z_start'] = dm['x_start']
            # Update the data model version to mark that this patch has been applied
            dm['data_model_version'] = "DM_2015_10_20_1446"

        if dm['data_model_version'] == "DM_2015_10_20_1446":
            # Earlier versions were exporting the partitions but not importing them at all
            # This version doesn't really change the data model but just marks the change
            dm['data_model_version'] = "DM_2016_04_15_1600"

        if dm['data_model_version'] != "DM_2016_04_15_1600":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellPartitionsPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        mcell = context.scene.mcell
        mcell4_mode = mcell.cellblender_preferences.mcell4_mode
        
        if dm['data_model_version'] != "DM_2016_04_15_1600":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellPartitionsPropertyGroup data model to current version." )

        if mcell4_mode:
            self.include = True
            self.recursion_flag = False
            self.start = min(float(dm["x_start"]), float(dm["y_start"]), float(dm["z_start"]))
            self.end = max(float(dm["x_end"]), float(dm["y_end"]), float(dm["z_end"]))
            self.step = min(float(dm["x_step"]), float(dm["y_step"]), float(dm["z_step"]))
        else:
            self.include = dm["include"]
            # not sure why this is read from data model, this is an internal state
            self.recursion_flag = dm["recursion_flag"] 
            self.x_start = float(dm["x_start"])
            self.x_end = float(dm["x_end"])
            self.x_step = float(dm["x_step"])
            self.y_start = float(dm["y_start"])
            self.y_end = float(dm["y_end"])
            self.y_step = float(dm["y_step"])
            self.z_start = float(dm["z_start"])
            self.z_end = float(dm["z_end"])
            self.z_step = float(dm["z_step"])


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Partition Properties... no collections to remove." )

    def draw_layout(self, context, layout):
        mcell = context.scene.mcell
        mcell4_mode = mcell.cellblender_preferences.mcell4_mode

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            if mcell4_mode:
                row = layout.row(align=True)
                row.prop(self, "start")
                row.prop(self, "end")
                row.prop(self, "step")
            else:
                layout.prop(self, "include")
                if self.include:
                    row = layout.row(align=True)
                    row.prop(self, "x_start")
                    row.prop(self, "x_end")
                    row.prop(self, "x_step")
    
                    row = layout.row(align=True)
                    row.prop(self, "y_start")
                    row.prop(self, "y_end")
                    row.prop(self, "y_step")
    
                    row = layout.row(align=True)
                    row.prop(self, "z_start")
                    row.prop(self, "z_end")
                    row.prop(self, "z_step")
    
            if mcell.model_objects.object_list:
                layout.operator("mcell.auto_generate_boundaries",
                                icon='OUTLINER_OB_LATTICE')
            if not "partitions" in bpy.data.objects:
                layout.operator("mcell.create_partitions_object",
                                icon='OUTLINER_OB_LATTICE')
            else:
                layout.operator("mcell.remove_partitions_object",
                                icon='OUTLINER_OB_LATTICE')

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



classes = ( 
            MCELL_OT_create_partitions_object,
            MCELL_OT_remove_partitions_object,
            MCELL_OT_auto_generate_boundaries,
            MCellPartitionsPropertyGroup,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

