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

import cellblender


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#CellBlender Operators:


class MCELL_OT_region_add(bpy.types.Operator):
    bl_idname = "mcell.region_add"
    bl_label = "Add New Surface Region"
    bl_description = "Add a new surface region to an object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell_obj = context.object.mcell
        mcell_obj.regions.region_list.add()
        mcell_obj.regions.active_reg_index = len(
            mcell_obj.regions.region_list)-1
        id = mcell_obj.regions.id_counter
        mcell_obj.regions.id_counter += 1
        mcell_obj.regions.region_list[
            mcell_obj.regions.active_reg_index].id = id
        mcell_obj.regions.region_list[
            mcell_obj.regions.active_reg_index].name = "Region_%d" % (id)

        return {'FINISHED'}


class MCELL_OT_region_remove(bpy.types.Operator):
    bl_idname = "mcell.region_remove"
    bl_label = "Remove Surface Region"
    bl_description = "Remove selected surface region from object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        obj_regs = context.object.mcell.regions

        # Clear existing faces from this region id
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        id = str(reg.id)
        mesh = obj.data
        for seg_id in mesh["mcell"]["regions"][id].keys():
            mesh["mcell"]["regions"][id][seg_id] = []
        mesh["mcell"]["regions"][id].clear()
        mesh["mcell"]["regions"].pop(id)

        # Now remove the region from the object
        obj_regs.region_list.remove(obj_regs.active_reg_index)
        obj_regs.active_reg_index -= 1
        if (obj_regs.active_reg_index < 0):
            obj_regs.active_reg_index = 0

        return {'FINISHED'}


def inplace_quicksort(v, beg, end):  # collection array, int, int
    """
      Sorts a collection array, v, in place.
        Sorts according values in v[i].name
    """

    if ((end - beg) > 0):  # only perform quicksort if we are dealing with > 1 values
        pivot = v[beg].name  # we set the first item as our initial pivot
        i, j = beg, end

        while (j > i):
            while ((v[i].name <= pivot) and (j > i)):
                i += 1
            while ((v[j].name > pivot) and (j >= i)):
                j -= 1
            if (j > i):
                v.move(i, j)
                v.move(j-1, i)

        if (not beg == j):
            v.move(beg, j)
            v.move(j-1, beg)
        inplace_quicksort(v, beg, j-1)
        inplace_quicksort(v, j+1, end)
    return


def check_region_name(obj):
    """Checks for duplicate or illegal region name"""

    mcell_obj = obj.mcell
    reg_list = mcell_obj.regions.region_list
    act_reg = reg_list[mcell_obj.regions.active_reg_index]
    act_reg_name = act_reg.name

    status = ""

    # Check for duplicate region name
    reg_keys = reg_list.keys()
    if reg_keys.count(act_reg_name) > 1:
        status = "Duplicate region: %s" % (act_reg_name)

    # Check for illegal names (Starts with a letter. No special characters)
    reg_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(reg_filter, act_reg_name)
    if m is None:
        status = "Region name error: %s" % (act_reg_name)

    act_reg.status = status

    return


def sort_region_list(obj):
    """Sorts region list"""

    mcell_obj = obj.mcell
    reg_list = mcell_obj.regions.region_list
    act_reg = reg_list[mcell_obj.regions.active_reg_index]
    act_reg_name = act_reg.name

    # Sort the region list
    inplace_quicksort(reg_list, 0, len(reg_list)-1)

    act_i = reg_list.find(act_reg_name)
    mcell_obj.regions.active_reg_index = act_i

    return


def region_update(self, context):
    """Performs checks and sorts region list after update of region names"""

    obj = context.object
    mcell_obj = obj.mcell
    reg_list = mcell_obj.regions.region_list

    if reg_list:
        check_region_name(obj)
        sort_region_list(obj)

    return


def rl_encode(l):
    """Run-length encode an array of face indices"""

    runlen = 0
    runstart = 0
    rle = []
    i = 0

    while (i < len(l)):
      if (runlen == 0):
        rle.append(l[i])
        runstart = l[i]
        runlen = 1
        i+=1
      elif (l[i] == (runstart+runlen)):
        if (i < (len(l)-1)):
          runlen += 1
        else:
          if (runlen == 1):
            rle.append(runstart+1)
          else:
            rle.append(-runlen)
        i+=1
      elif (runlen == 1):
        runlen = 0
      elif (runlen == 2):
        rle.append(runstart+1)
        runlen = 0
      else:
        rle.append(-(runlen-1))
        runlen = 0

    return(rle)


def rl_decode(l):
    """Decode a run-length encoded array of face indices"""

    runlen = 0
    runstart = 0
    rld = []
    i = 0

    while (i < len(l)):
      if (runlen == 0):
        rld.append(l[i])
        runstart = l[i]
        runlen = 1
        i+=1
      elif (l[i] > 0):
        runlen = 0
      else:
        for j in range(1,-l[i]+1):
          rld.append(runstart+j)
        runlen = 0
        i+=1

    return(rld)


def get_region_faces(mesh,id):
    """Given a mesh and a region id, return the set of region face indices"""

    if not mesh.get("mcell"):
        mesh["mcell"] = {}
    if not mesh["mcell"].get("regions"):
        mesh["mcell"]["regions"] = {}
    if not mesh["mcell"]["regions"].get(id):
        mesh["mcell"]["regions"][id] = {}
    face_rle = []
    for seg_id in mesh["mcell"]["regions"][id].keys():
      face_rle.extend(mesh["mcell"]["regions"][id][seg_id].to_list())
    if (len(face_rle) > 0): 
        face_set = set(rl_decode(face_rle))
    else:
        face_set = set([])

    return(face_set)


def set_region_faces(mesh,id,face_set):
    """Set the faces of a given region id on a mesh, given a set of faces """

    face_list = list(face_set)
    face_list.sort()
    face_rle = rl_encode(face_list)

    # Clear existing faces from this region id
    mesh["mcell"]["regions"][id].clear()

    # segment face_rle into pieces <= max_len (i.e. <= 32767)
    #   and assign these segments to the region id
    max_len = 32767
    seg_rle = face_rle
    len_rle = len(seg_rle)
    seg_idx = 0
    while len_rle > 0:
      if len_rle <= 32767:
        mesh["mcell"]["regions"][id][str(seg_idx)] = seg_rle
        len_rle = 0
      else:
        mesh["mcell"]["regions"][id][str(seg_idx)] = seg_rle[0:max_len]
        tmp_rle = seg_rle[max_len:]
        seg_rle = tmp_rle
        len_rle = len(seg_rle)
      seg_idx += 1


class MCELL_OT_region_faces_assign(bpy.types.Operator):
    bl_idname = "mcell.region_faces_assign"
    bl_label = "Assign Selected Faces To Surface Region"
    bl_description = "Assign selected faces to surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        id = str(reg.id)
        mesh = active_obj.data
        if (mesh.total_face_sel > 0):
            face_set = get_region_faces(mesh,id) 
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    face_set.add(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            set_region_faces(mesh,id,face_set) 

        return {'FINISHED'}


class MCELL_OT_region_faces_remove(bpy.types.Operator):
    bl_idname = "mcell.region_faces_remove"
    bl_label = "Remove Selected Faces From Surface Region"
    bl_description = "Remove selected faces from surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        id = str(reg.id)
        mesh = active_obj.data
        if (mesh.total_face_sel > 0):
            face_set = get_region_faces(mesh,id) 
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    if f.index in face_set:
                        face_set.remove(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            set_region_faces(mesh,id,face_set) 

        return {'FINISHED'}


class MCELL_OT_region_faces_select(bpy.types.Operator):
    bl_idname = "mcell.region_faces_select"
    bl_label = "Select Faces of Selected Surface Region"
    bl_description = "Select faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        id = str(reg.id)
        mesh = active_obj.data
        face_set = get_region_faces(mesh,id) 
        bpy.ops.object.mode_set(mode='OBJECT')
        msm = context.tool_settings.mesh_select_mode[0:]
        context.tool_settings.mesh_select_mode = [False, False, True]
        for f in face_set:
            mesh.polygons[f].select = True
        bpy.ops.object.mode_set(mode='EDIT')

        context.tool_settings.mesh_select_mode = msm
        return {'FINISHED'}


class MCELL_OT_region_faces_deselect(bpy.types.Operator):
    bl_idname = "mcell.region_faces_deselect"
    bl_label = "Deselect Faces of Selected Surface Region"
    bl_description = "Deselect faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        id = str(reg.id)
        mesh = active_obj.data
        face_set = get_region_faces(mesh,id) 
        bpy.ops.object.mode_set(mode='OBJECT')
        msm = context.tool_settings.mesh_select_mode[0:]
        context.tool_settings.mesh_select_mode = [False, False, True]
        for f in face_set:
            mesh.polygons[f].select = False
        bpy.ops.object.mode_set(mode='EDIT')

        context.tool_settings.mesh_select_mode = msm
        return {'FINISHED'}


# Update format of object regions
# This is required to update regions from pre v1.0 format to new v1.0 format
# Note: This function is registered as a load_post handler
@persistent
def object_regions_format_update(context):

    scn = bpy.context.scene
    mcell = scn.mcell
    objs = scn.objects
    for obj in objs:
        if obj.type == 'MESH':
            obj_regs = obj.mcell.regions
            regs = obj_regs.region_list 
            mesh = obj.data
            if len(regs) > 0:
                # We have object regions so check for pre v1.0 region format
                # We'll do that by checking the region name on the mesh.
                # If even one mesh region is old then they're all old
                sort_region_list(obj)
                # Check that the mesh has regions
                if mesh.get("mcell"):
                    if mesh["mcell"].get("regions"):
                        mregs =  mesh["mcell"]["regions"]
                        if len(mregs.keys()) > 0:
                            # if reg_name is alpha followed by alphanumeric
                            #   then we've got an old format region
                            reg_name = mregs.keys()[0]
                            reg_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
                            m = re.match(reg_filter, reg_name)
                            if m is not None:
                                # We have old region format
                                # Make copies of old regions
                                mreg_tmp = {}
                                obj_regs.id_counter = 0
                                for reg in regs:
                                    reg.id = obj_regs.id_counter
                                    obj_regs.id_counter += 1
                                    mreg_tmp[reg.name] = set(
                                        mregs[reg.name].to_list())
                                # Clear old regions from mesh
                                for key in mregs.keys():
                                    mregs[key] = []
                                mregs.clear()
                                # Convert old regions to new format
                                for reg in regs:
                                    id = str(reg.id)
                                    mregs[id] = {}
                                    set_region_faces(
                                        mesh,id,mreg_tmp[reg.name])
                else:
                    # The mesh did not have regions so the object regions are
                    # empty. If id_counter is 0 then we have old object regions
                    if obj_regs.id_counter == 0:
                        for reg in regs:
                            # Update the object region id's
                            reg.id = obj_regs.id_counter
                            obj_regs.id_counter += 1
            else:
                # There are no object regions but there might be mesh cruft
                # Remove any region cruft we find attached to mesh["mcell"]
                if mesh.get("mcell"):
                    if mesh["mcell"].get("regions"):
                        mregs =  mesh["mcell"]["regions"]
                        for key in mregs.keys():
                            mregs[key] = []
                        mregs.clear()
                        mesh["mcell"].pop("regions")


# Legacy code from when we used to store regions as vertex groups
#   Useful to run from Blender's python console on some older models
#   We'll eliminate this when our face regions have query features akin
#   to those available with vertex groups.
class MCELL_OT_vertex_groups_to_regions(bpy.types.Operator):
    bl_idname = "mcell.vertex_groups_to_regions"
    bl_label = "Convert Vertex Groups of Selected Objects to Regions"
    bl_description = "Convert Vertex Groups to Regions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        select_objs = context.selected_objects

        # For each selected object:
        for obj in select_objs:
            print(obj.name)
            scn.objects.active = obj
            obj.select = True
            obj_regs = obj.mcell.regions
            vert_groups = obj.vertex_groups

            # If there are vertex groups to convert:
            if vert_groups:
                mesh = obj.data

                # For each vertex group:
                for vg in vert_groups:

                    # Deselect the whole mesh:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')

                    # Select the vertex group:
                    print(vg.name)
                    bpy.ops.object.vertex_group_set_active(group=vg.name)
                    bpy.ops.object.vertex_group_select()

                    # If there are selected faces:
                    if (mesh.total_face_sel > 0):
                        print("  vg faces: %d" % (mesh.total_face_sel))

                        # Setup mesh regions IDProp if necessary:
                        if not mesh.get("mcell"):
                            mesh["mcell"] = {}
                        if not mesh["mcell"].get("regions"):
                            mesh["mcell"]["regions"] = {}

                        # look for vg.name in region_list and add if not found:
                        # method 1:
                        if (obj_regs.region_list.find(vg.name) == -1):
                            bpy.ops.mcell.region_add()
                            reg = obj_regs.region_list[
                                obj_regs.active_reg_index]
                            reg.name = vg.name
                        reg = obj_regs.region_list[vg.name]

                        # append faces in vertex group to faces in region:
                        # retreive or create region on mesh:
                        if not mesh["mcell"]["regions"].get(vg.name):
                            mesh["mcell"]["regions"][reg.name] = []
                        face_set = set([])
                        for f in mesh["mcell"]["regions"][reg.name]:
                            face_set.add(f)
                        print("  reg faces 0: %d" % (len(face_set)))
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for f in mesh.polygons:
                            if f.select:
                                face_set.add(f.index)
                        bpy.ops.object.mode_set(mode='EDIT')
                        reg_faces = list(face_set)
                        reg_faces.sort()
                        print("  reg faces 1: %d" % (len(reg_faces)))
                        mesh["mcell"]["regions"][reg.name] = reg_faces
                        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


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
            old_active_object = bpy.context.active_object
            # Add a box that represents the partitions' boundaries
            bpy.ops.mesh.primitive_cube_add()
            partition_object = bpy.context.active_object
            # Prevent user from manipulating the box, because I don't yet have
            # a good way of updating the partitions when the box object is
            # moved/scaled in the 3D view window
            scene.objects.active = old_active_object
            partition_object.select = False
            partition_object.hide_select = True
            # Set draw_type to wireframe so the user can see what's inside
            partition_object.draw_type = 'WIRE'
            partition_object.name = "partitions"
            partition_mesh = partition_object.data
            partition_mesh.name = "partitions"
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
        scene_objects = scene.objects
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
                    (x, y, z) = obj_matrix * vert.co
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


def transform_partition_boundary(self, context, start, end, xyz_index):
    """ Transform the partition object along the provided axis.

    Change the scaling and location of the cube that represents partition
    boundaries. Also, make sure the step lengths are valid.

    """

    difference = end-start
    # Scale works this way, because default Cube is 2x2x2
    half_difference = scale = difference/2
    # The object center of the partition boundaries (i.e. the box)
    location = start + half_difference
    # Move the partition boundary object if it exists
    if "partitions" in bpy.data.objects:
        partition_object = bpy.data.objects["partitions"]
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

############### BK: Duplicating some of Dipak's code to experiment with general-purpose (non-imported) parameters #################
class MCELL_OT_add_parameter(bpy.types.Operator):
    bl_idname = "mcell.add_parameter"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.general_parameters.parameter_list.add()
        mcell.general_parameters.active_par_index = len(mcell.general_parameters.parameter_list)-1
        mcell.general_parameters.parameter_list[mcell.general_parameters.active_par_index].name = "Parameter Name"
        return {'FINISHED'}

class MCELL_OT_remove_parameter(bpy.types.Operator):
    bl_idname = "mcell.remove_parameter"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.general_parameters.parameter_list.remove(mcell.general_parameters.active_par_index)
        mcell.general_parameters.active_par_index = mcell.general_parameters.active_par_index-1
        if (mcell.general_parameters.active_par_index < 0):
            mcell.general_parameters.active_par_index = 0

        return {'FINISHED'}


# These functions belong in the MCellGeneralParameterProperty class (in cellblender_properties.py) ... but they didn't work there!!

"""
#### Making a dictionary ####
data = {}
# OR #
data = dict()

#### Initially adding values ####
data = {'a':1,'b':2,'c':3}
# OR #
data = dict(a=1, b=2, c=3)

#### Inserting/Updating value ####
data['a']=1  # updates if 'a' exists, else adds 'a'
# OR #
data.update({'a':1})
# OR #
data.update(dict(a=1))

#### Merging 2 dictionaries ####
data.update(data2)  # Where data2 is also a dict.
"""


"""
Experimenting in the Blender Console
>>> C.scene.mcell['general_parameters']["parameter_list"][0].
                                                             clear(
                                                             get(
                                                             items(
                                                             iteritems(
                                                             keys(
                                                             name
                                                             pop(
                                                             to_dict(
                                                             update(
                                                             values(
>>> C.scene.mcell['general_parameters']["parameter_list"][0].items()
[('name', 'A'), ('value', '1'), ('unit', 'counts'), ('type', ''), ('desc', 'Parameter A in counts'), ('expr', '1')]

>>> C.scene.mcell['general_parameters']["parameter_list"][0]['name']
'A'

>>> C.scene.mcell['general_parameters']["parameter_list"][1]['name']
'B'

>>> for p in C.scene.mcell['general_parameters']["parameter_list"]:
...   print p['name']
  File "<blender_console>", line 2
    print p['name']
          ^
SyntaxError: invalid syntax

>>> for p in C.scene.mcell['general_parameters']["parameter_list"]:
...   p['name']
... 
'A'
'B'
'C'
'D'

>>> 
"""


def check_parameter_dict ( mcell ):
    if len ( mcell.general_parameters.parameter_dict ) == 0:
        print ( "\nBuildiing the dictionary!!\n" )
        mcell.general_parameters.parameter_dict = {}
        print ("After assignment ", mcell.general_parameters.parameter_dict )
        d = mcell.general_parameters.parameter_dict
        # Search through the existing Blender Properties (if any) to initialize
        plist = mcell.general_parameters.parameter_list
        for p in plist:
            d.update ( { p['name']: p['expr'] } )
        print ( d )
            



def change_parameter_name ( self, context ):
    print ( "\nChanging Parameter Name\n" )
    mcell = context.scene.mcell
    check_parameter_dict(mcell)
    print ( "\nmcell OK\n" )

def parse_parameter_expression ( self, context ):
    print ( "\nParsing Parameter Expression\n" )
    parameter = self
    mcell = context.scene.mcell
    check_parameter_dict(mcell)
    param_dict = mcell.general_parameters.parameter_dict
    
    print ( "Parms: ", param_dict )

    print ( "expr: ", parameter.expr )




# Tom's Parameter Parsing / Evaluation Code

def toms_check_param_name(param_name,param_dict):
    # Check for duplicate param name
    if param_name in param_dict.keys():
        print("name already in dict: %s" %(param_name))
        return 0

    # Check for illegal names (Starts with a letter. No special characters.)
    name_filter = r'^[A-Za-z]+[0-9A-Za-z_.]*$'
    m = re.match(name_filter, param_name)
    if m is None:
        print("name not ok: %s %d" %(param_name,len(param_name)))
        return 0

    print("name ok: %s" %(param_name))
    return 1


def toms_check_param_expr(param_expr,param_dict):

    # remove white space
    pe = re.sub(r'[ \t]','',param_expr)

    # Now make sure we have a parsable python expression
    try:
        st = parser.expr(pe)
    except:
        print("syntax error in expression: %s" %(param_expr))
        return None

    func_list = ['SQRT(','EXP(','LOG(','LOG10(','SIN(','COS(','TAN(','ASIN(','ACOS(','ATAN(','ABS(','CEIL(','FLOOR(','MAX(','MIN(','RAND_UNIFORM(','RAND_GAUSSIAN(']
    const_list = ['PI','SEED']

    # Extract vars, numeric constants, and functions from expression
    pe_nop = re.sub(r'[+\-*/^)]',' ',pe)
    pe_nofunc = re.sub(r'[A-Z]+[A-Z0-9_]*\(',' ',pe_nop)
    pe_var = re.findall(r'[A-Za-z]+[A-Za-z0-9_]*',pe_nofunc)
    pe_numconst = re.sub(r'[A-Za-z]+[A-Za-z0-9_]*',' ',pe_nofunc).split()
    pe_func = re.findall(r'[A-Z]+[A-Z0-9_]*\(',pe_nop)

    # Check function calls
    for f in pe_func:
        if f not in func_list:
            print("func %s invalid in expression: %s" %(f,param_expr))
            return None

    # Check vars
    param_dep = []
    for v in pe_var:
        if v not in param_dict:
            if v not in const_list:
                print("var %s undefined in expression: %s" %(v,param_expr))
                return None
        else:
            if v not in param_dep:
                param_dep.append(v)

    return param_dep


def toms_eval_param(param_expr,param_dict):
    # remove white space
    pe = re.sub(r'[ \t]','',param_expr)

    # Convert expression from MDL syntax to equivalent python syntax
    # Substitute "^" with "**"
    pe_py = re.sub(r'[\^]','**',pe)
    # Substitute MDL funcs with python funcs
    func_dict = {'SQRT\(': 'sqrt(', 'EXP\(': 'exp(', 'LOG\(': 'log(', 'LOG10\(': 'log10(', 'SIN\(': 'sin(', 'COS\(': 'cos(', 'TAN\(': 'tan(', 'ASIN\(': 'asin(', 'ACOS\(':'acos(', 'ATAN\(': 'atan(', 'ABS\(': 'abs(', 'CEIL\(': 'ceil(', 'FLOOR\(': 'floor(', 'MAX\(': 'max(', 'MIN\(': 'min(', 'RAND_UNIFORM\(': 'uniform(', 'RAND_GAUSSIAN\(': 'gauss('}

    const_dict = {'PI':pi,'SEED':1}

    for mdl_func in func_dict.keys():
        pe_py = re.sub(mdl_func,func_dict[mdl_func],pe_py)

    # Extract vars, numeric constants, and functions from expression
    pe_nop = re.sub(r'[+\-*/^)]',' ',pe_py)
    pe_nofunc = re.sub(r'[a-z]+[0-9]*\(',' ',pe_nop)
    pe_var = re.findall(r'[A-Za-z]+[A-Za-z0-9_]*',pe_nofunc)
    pe_numconst = re.sub(r'[A-Za-z]+[A-Za-z0-9_]*',' ',pe_nofunc).split()
    pe_func = re.findall(r'[a-z]+[0-9]*\(',pe_nop)

    for v in pe_var:
        if v in const_dict:
            v_stmt = ('%s = %g') % (v,const_dict[v])
        else:
            v_stmt = ('%s = %g') % (v,param_dict[v][1])
        exec(v_stmt)

    val = eval(pe_py,locals())

    return val


def toms_add_param(param_stmt,param_dict):
    param_clean = param_stmt.replace(' ','')
    param_split = param_stmt.split('=')
    if(len(param_split)==2):
        param_name = param_split[0].strip()
        param_expr = param_split[1].strip()
    else:
        return 0

    if not toms_check_param_name(param_name,param_dict):
        return 0

    param_dep = toms_check_param_expr(param_expr,param_dict)
    if (param_dep == None):
        return 0

    param_val = toms_eval_param(param_expr,param_dict)
      
    param_dict[param_name] = [param_expr,param_val,param_dep]

    return 1

def sort_params(param_dict):
    return 1


"""
# Testing code

my_param_dict = {}

toms_add_param("a = 1.0",my_param_dict)
toms_add_param("b = 2.0",my_param_dict)
toms_add_param("c = 3.0",my_param_dict)
toms_add_param("d12_5ft = 4.0",my_param_dict)
toms_add_param("mu = 10.0",my_param_dict)
toms_add_param("sigma = 2.0",my_param_dict)

toms_add_param("p = SQRT(EXP(b + c/2.718)) + LOG10(a*d12_5ft \t+ 123.5 + 34^(a+b)) + RAND_GAUSSIAN(mu,sigma)",my_param_dict)

toms_add_param("pi_e = PI*EXP(p)",my_param_dict)

sort_params(my_param_dict)

print(my_param_dict)
"""


	
#########################################################################################################################################

class MCELL_OT_molecule_add(bpy.types.Operator):
    bl_idname = "mcell.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule type to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.molecules.molecule_list.add()
        mcell.molecules.active_mol_index = len(mcell.molecules.molecule_list)-1
        mcell.molecules.molecule_list[
            mcell.molecules.active_mol_index].name = "Molecule"
        return {'FINISHED'}
    
 
class MCELL_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "mcell.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.molecules.molecule_list.remove(mcell.molecules.active_mol_index)
        mcell.molecules.active_mol_index = mcell.molecules.active_mol_index-1
        if (mcell.molecules.active_mol_index < 0):
            mcell.molecules.active_mol_index = 0

        if mcell.molecules.molecule_list:
            check_molecule(self, context)

        return {'FINISHED'}


def check_molecule(self, context):
    """Checks for duplicate or illegal molecule name"""

    mcell = context.scene.mcell
    mol_list = mcell.molecules.molecule_list
    mol = mol_list[mcell.molecules.active_mol_index]

    status = ""

    # Check for duplicate molecule name
    mol_keys = mol_list.keys()
    if mol_keys.count(mol.name) > 1:
        status = "Duplicate molecule: %s" % (mol.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(mol_filter, mol.name)
    if m is None:
        status = "Molecule name error: %s" % (mol.name)

    mol.status = status

    return


class MCELL_OT_reaction_add(bpy.types.Operator):
    bl_idname = "mcell.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add a new reaction to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.reactions.reaction_list.add()
        mcell.reactions.active_rxn_index = len(mcell.reactions.reaction_list)-1
        check_reaction(self, context)
        return {'FINISHED'}


class MCELL_OT_reaction_remove(bpy.types.Operator):
    bl_idname = "mcell.reaction_remove"
    bl_label = "Remove Reaction"
    bl_description = "Remove selected reaction from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.reactions.reaction_list.remove(mcell.reactions.active_rxn_index)
        mcell.reactions.active_rxn_index = mcell.reactions.active_rxn_index-1
        if (mcell.reactions.active_rxn_index < 0):
            mcell.reactions.active_rxn_index = 0

        if mcell.reactions.reaction_list:
            check_reaction(self, context)

        return {'FINISHED'}


def check_reaction(self, context):
    """Checks for duplicate or illegal reaction name. Cleans up formatting."""

    mcell = context.scene.mcell

    #Retrieve reaction
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    for item in rxn.type_enum:
        if rxn.type == item[0]:
            rxtype = item[1]

    status = ""

    # clean up rxn.reactants only if necessary to avoid infinite recursion.
    reactants = rxn.reactants.replace(" ", "")
    reactants = reactants.replace("+", " + ")
    reactants = reactants.replace("@", " @ ")
    if reactants != rxn.reactants:
        rxn.reactants = reactants

    # clean up rxn.products only if necessary to avoid infinite recursion.
    products = rxn.products.replace(" ", "")
    products = products.replace("+", " + ")
    if products != rxn.products:
        rxn.products = products

    #Check for duplicate reaction
    rxn.name = ("%s %s %s") % (rxn.reactants, rxtype, rxn.products)
    rxn_keys = mcell.reactions.reaction_list.keys()
    if rxn_keys.count(rxn.name) > 1:
        status = "Duplicate reaction: %s" % (rxn.name)

    #Check syntax of reactant specification
    mol_list = mcell.molecules.molecule_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mol_surf_class_filter = \
        r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
    # Check the syntax of the surface class if one exists
    if rxn.reactants.count(" @ ") == 1:
        reactants_no_surf_class, surf_class = rxn.reactants.split(" @ ")
        m = re.match(mol_surf_class_filter, surf_class)
        if m is None:
            status = "Surface class error: %s" % (surf_class)
        else:
            surf_class_name = m.group(1)
            if not surf_class_name in surf_class_list:
                status = "Undefined surface class: %s" % (surf_class_name)
    else:
        reactants_no_surf_class = rxn.reactants
    reactants = reactants_no_surf_class.split(" + ")
    for reactant in reactants:
        m = re.match(mol_surf_class_filter, reactant)
        if m is None:
            status = "Reactant error: %s" % (reactant)
            break
        else:
            mol_name = m.group(1)
            if not mol_name in mol_list:
                status = "Undefined molecule: %s" % (mol_name)

    #Check syntax of product specification
    if rxn.products == "NULL":
        if rxn.type == 'reversible':
            rxn.type = 'irreversible'
    else:
        products = rxn.products.split(" + ")
        for product in products:
            m = re.match(mol_surf_class_filter, product)
            if m is None:
                status = "Product error: %s" % (product)
                break
            else:
                mol_name = m.group(1)
                if not mol_name in mol_list:
                    status = "Undefined molecule: %s" % (mol_name)

    rxn.status = status
    return


class MCELL_OT_surf_class_props_add(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_add"
    bl_label = "Add Surface Class Properties"
    bl_description = "Add new surface class properties to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[
            surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.add()
        active_surf_class.active_surf_class_props_index = len(
            active_surf_class.surf_class_props_list) - 1
        check_surf_class_props(self, context)

        return {'FINISHED'}


class MCELL_OT_surf_class_props_remove(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_remove"
    bl_label = "Remove Surface Class Properties"
    bl_description = "Remove surface class properties from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[
            surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.remove(
            active_surf_class.active_surf_class_props_index)
        active_surf_class.active_surf_class_props_index = len(
            active_surf_class.surf_class_props_list) - 1
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
        surf_class.active_surf_class_index = len(
            surf_class.surf_class_list) - 1
        surf_class.surf_class_list[
            surf_class.active_surf_class_index].name = "Surface_Class"

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


def convert_orient_str(orient):
    """Format MDL language (orientation) for viewing in the UI"""

    if orient == "'":
        orient = "Top/Front"
    elif orient == ",":
        orient = "Bottom/Back"
    elif orient == ";":
        orient = "Ignore"

    return(orient)


def check_surf_class_props(self, context):
    """Checks for illegal/undefined molecule names in surf class properties"""

    mcell = context.scene.mcell
    active_surf_class = mcell.surface_classes.surf_class_list[
        mcell.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    mol_list = mcell.molecules.molecule_list
    molecule = surf_class_props.molecule
    surf_class_type = surf_class_props.surf_class_type
    orient = surf_class_props.surf_class_orient

    surf_class_type = convert_surf_class_str(surf_class_type)
    orient = convert_orient_str(orient)

    surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (
        molecule, orient, surf_class_type)

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    m = re.match(mol_filter, molecule)
    if m is None:
        status = "Molecule name error: %s" % (molecule)
    else:
        # Check for undefined names
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = "Undefined molecule: %s" % (mol_name)

    surf_class_props.status = status

    return


class MCELL_OT_mod_surf_regions_add(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_add"
    bl_label = "Add Surface Region Modification"
    bl_description = "Add a surface region modification to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.add()
        mod_surf_regions.active_mod_surf_regions_index = len(
            mod_surf_regions.mod_surf_regions_list) - 1
        check_mod_surf_regions(self, context)

        return {'FINISHED'}


class MCELL_OT_mod_surf_regions_remove(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_remove"
    bl_label = "Remove Surface Region Modification"
    bl_description = "Remove selected surface region modification"
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

    mcell = context.scene.mcell
    obj_list = mcell.model_objects.object_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    try:
        region_list = bpy.data.objects[
            active_mod_surf_regions.object_name].mcell.regions.region_list
    except KeyError:
        # The object name in mod_surf_regions isn't a blender object
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


class MCELL_OT_release_pattern_add(bpy.types.Operator):
    bl_idname = "mcell.release_pattern_add"
    bl_label = "Add Release Pattern"
    bl_description = "Add a new Release Pattern to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_patterns.release_pattern_list.add()
        mcell.release_patterns.active_release_pattern_index = len(
            mcell.release_patterns.release_pattern_list)-1
        mcell.release_patterns.release_pattern_list[
            mcell.release_patterns.active_release_pattern_index].name = "Release_Pattern"
        check_release_pattern_name(self, context)

        return {'FINISHED'}


class MCELL_OT_release_pattern_remove(bpy.types.Operator):
    bl_idname = "mcell.release_pattern_remove"
    bl_label = "Remove Release Pattern"
    bl_description = "Remove selected Release Pattern from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_patterns.release_pattern_list.remove(
            mcell.release_patterns.active_release_pattern_index)
        mcell.release_patterns.active_release_pattern_index -= 1
        if (mcell.release_patterns.active_release_pattern_index < 0):
            mcell.release_patterns.active_release_pattern_index = 0

        if mcell.release_patterns.release_pattern_list:
            check_release_pattern_name(self, context)

        return {'FINISHED'}


def check_release_pattern_name(self, context):
    """Checks for duplicate or illegal release pattern name."""

    mcell = context.scene.mcell
    rel_pattern_list = mcell.release_patterns.release_pattern_list
    rel_pattern = rel_pattern_list[
        mcell.release_patterns.active_release_pattern_index]

    status = ""

    # Check for duplicate release pattern name
    rel_pattern_keys = rel_pattern_list.keys()
    if rel_pattern_keys.count(rel_pattern.name) > 1:
        status = "Duplicate release pattern: %s" % (rel_pattern.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_pattern_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_pattern_filter, rel_pattern.name)
    if m is None:
        status = "Release Pattern name error: %s" % (rel_pattern.name)

    rel_pattern.status = status


class MCELL_OT_release_site_add(bpy.types.Operator):
    bl_idname = "mcell.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add a new Molecule Release Site to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_sites.mol_release_list.add()
        mcell.release_sites.active_release_index = len(
            mcell.release_sites.mol_release_list)-1
        mcell.release_sites.mol_release_list[
            mcell.release_sites.active_release_index].name = "Release_Site"
        check_release_molecule(self, context)

        return {'FINISHED'}


class MCELL_OT_release_site_remove(bpy.types.Operator):
    bl_idname = "mcell.release_site_remove"
    bl_label = "Remove Release Site"
    bl_description = "Remove selected Molecule Release Site from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.release_sites.mol_release_list.remove(
            mcell.release_sites.active_release_index)
        mcell.release_sites.active_release_index -= 1
        if (mcell.release_sites.active_release_index < 0):
            mcell.release_sites.active_release_index = 0

        if mcell.release_sites.mol_release_list:
            check_release_site(self, context)

        return {'FINISHED'}


def check_release_site(self, context):

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]

    name_status = check_release_site_name(self, context)
    molecule_status = check_release_molecule(self, context)
    object_status = check_release_object_expr(self, context)

    if name_status:
        rel.status = name_status
    elif molecule_status:
        rel.status = molecule_status
    elif object_status and rel.shape == 'OBJECT':
        rel.status = object_status
    else:
        rel.status = ""

    return


def check_release_site_name(self, context):
    """Checks for duplicate or illegal release site name."""

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]

    status = ""

    # Check for duplicate release site name
    rel_keys = rel_list.keys()
    if rel_keys.count(rel.name) > 1:
        status = "Duplicate release site: %s" % (rel.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_filter, rel.name)
    if m is None:
        status = "Release Site name error: %s" % (rel.name)

    return status


def check_release_molecule(self, context):
    """Checks for illegal release site molecule name."""

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    mol = rel.molecule

    mol_list = mcell.molecules.molecule_list

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(mol_filter, mol)
    if m is None:
        status = "Molecule name error: %s" % (mol)
    else:
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = "Undefined molecule: %s" % (mol_name)
        # Only change if necessary to avoid infinite recursion
        elif (mol_list[mol_name].type == '2D') and (not rel.shape == 'OBJECT'):
            rel.shape = 'OBJECT'

    return status


def check_release_object_expr(self, context):
    """Checks for illegal release object name."""

    scn = context.scene
    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    obj_expr = rel.object_expr

    status = ""

    # Check for illegal names. (Starts with a letter. No special characters.)
    # May be only object name or object name and region (e.g. object[reg].)
    obj_reg_filter = (r"(?P<obj_reg>(?P<obj_name>^[A-Za-z]+[0-9A-Za-z_.]*)(\[)"
                      "(?P<reg_name>[A-Za-z]+[0-9A-Za-z_.]*)(\])$)|"
                      "(?P<obj_name_only>^([A-Za-z]+[0-9A-Za-z_.]*)$)")

    expr_filter = r"[\+\-\*\(\)]"

    expr_vars = re.sub(expr_filter, " ", obj_expr).split()

    if not obj_expr:
        status = "Object name error"

    for var in expr_vars:
        m = re.match(obj_reg_filter, var)
        if m is None:
            status = "Object name error: %s" % (var)
            break
        else:
            if m.group("obj_reg") is not None:
                obj_name = m.group("obj_name")
                reg_name = m.group("reg_name")
                if not obj_name in scn.objects:
                    status = "Undefined object: %s" % (obj_name)
                    break
                obj = scn.objects[obj_name]
                if reg_name != "ALL":
                    if (not obj.mcell.regions.region_list or 
                            reg_name not in obj.mcell.regions.region_list):
                        status = "Undefined region: %s" % (reg_name)
                        break
            else:
                obj_name = m.group("obj_name_only")
                if not obj_name in scn.objects:
                    status = "Undefined object: %s" % (obj_name)
                    break

    return status


def is_executable ( binary_path ):
    """Checks for nonexistant or non-executable mcell binary file"""
    is_exec = False
    try:
        st = os.stat ( binary_path )
        if os.path.isfile( binary_path ):
            if os.access( binary_path, os.X_OK ):
                is_exec = True
    except Exception as err:
        is_exec = False
    return is_exec
    

def check_mcell_binary(self, context):
    """Callback to check for mcell executable"""
    mcell = context.scene.mcell
    binary_path = mcell.project_settings.mcell_binary
    mcell.project_settings.mcell_binary_valid = is_executable ( binary_path )
    return None



class MCELL_OT_set_mcell_binary(bpy.types.Operator):
    bl_idname = "mcell.set_mcell_binary"
    bl_label = "Set MCell Binary"
    bl_description = ("Set MCell Binary. If needed, download at "
                      "mcell.org/download.html")
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def __init__(self):
        self.filepath = bpy.context.scene.mcell.project_settings.mcell_binary

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.project_settings.mcell_binary = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MCELL_OT_run_simulation(bpy.types.Operator):
    bl_idname = "mcell.run_simulation"
    bl_label = "Run MCell Simulation"
    bl_description = "Run MCell Simulation"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell

        binary_path = mcell.project_settings.mcell_binary
        mcell.project_settings.mcell_binary_valid = is_executable ( binary_path )

        start = mcell.run_simulation.start_seed
        end = mcell.run_simulation.end_seed
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.project_settings.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = project_files_path()
        status = ""
        python_path = shutil.which("python")

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            react_dir = os.path.join(project_dir, "react_data")
            if (os.path.exists(react_dir) and
                    mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(react_dir)
            if not os.path.exists(react_dir):
                os.makedirs(react_dir)

            viz_dir = os.path.join(project_dir, "viz_data")
            if (os.path.exists(viz_dir) and
                    mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)

            base_name = mcell.project_settings.base_name

            error_file_option = mcell.run_simulation.error_file
            log_file_option = mcell.run_simulation.log_file
            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(
                script_dir_path, "run_simulations.py")

            processes_list = mcell.run_simulation.processes_list
            processes_list.add()
            mcell.run_simulation.active_process_index = len(
                mcell.run_simulation.processes_list) - 1
            simulation_process = processes_list[
                mcell.run_simulation.active_process_index]

            print("Starting MCell ... create start_time.txt file:")
            with open(os.path.join(os.path.dirname(bpy.data.filepath),
                      "start_time.txt"), "w") as start_time_file:
                start_time_file.write(
                    "Started MCell at: " + (str(time.ctime())) + "\n")

            # We have to create a new subprocess that in turn creates a
            # multiprocessing pool, instead of directly creating it here,
            # because the multiprocessing package requires that the __main__
            # module be importable by the children.
            sp = subprocess.Popen([
                python_path, script_file_path, mcell_binary, str(start),
                str(end + 1), project_dir, base_name, error_file_option,
                log_file_option, mcell_processes_str], stdout=None,
                stderr=None)
            self.report({'INFO'}, "Simulation Running")

            # This is a hackish workaround since we can't return arbitrary
            # objects from operators or store arbitrary objects in collection
            # properties, and we need to keep track of the progress of the
            # subprocess objects in cellblender_panels.
            cellblender.simulation_popen_list.append(sp)

            if ((end - start) == 0):
                simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                           "Seed: %d" % (sp.pid, base_name,
                                                         start))
            else:
                simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                           "Seeds: %d-%d" % (sp.pid, base_name,
                                                             start, end))
        else:
            status = "Python not found."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_clear_run_list(bpy.types.Operator):
    bl_idname = "mcell.clear_run_list"
    bl_label = "Clear Completed MCell Runs"
    bl_description = ("Clear the list of completed and failed MCell runs. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        # The collection property of subprocesses
        processes_list = mcell.run_simulation.processes_list
        # A list holding actual subprocess objects
        simulation_popen_list = cellblender.simulation_popen_list
        sim_list_length = len(simulation_popen_list)
        idx = 0
        ctr = 0

        while ctr < sim_list_length:
            ctr += 1
            sp = simulation_popen_list[idx]
            # Simulation set is still running. Leave it in the collection
            # property and list of subprocess objects.
            if sp.poll() is None:
                idx += 1
            # Simulation set has failed or finished. Remove it from
            # collection property and the list of subprocess objects.
            else:
                processes_list.remove(idx)
                simulation_popen_list.pop(idx)
                mcell.run_simulation.active_process_index -= 1
                if (mcell.run_simulation.active_process_index < 0):
                    mcell.run_simulation.active_process_index = 0

        return {'FINISHED'}


@persistent
def clear_run_list(context):
    """ Clear processes_list when loading a blend.

    Data in simulation_popen_list can not be saved with the blend, so we need
    to clear the processes_list upon reload so the two aren't out of sync.

    """

    if not context:
        context = bpy.context

    processes_list = context.scene.mcell.run_simulation.processes_list

    if not cellblender.simulation_popen_list:
        processes_list.clear()



@persistent
def mcell_valid_update(context):
    """ Check whether the mcell executable in the .blend file is valid """
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    binary_path = mcell.project_settings.mcell_binary
    mcell.project_settings.mcell_binary_valid = is_executable ( binary_path )
    # print ( "mcell_binary_valid = ", mcell.project_settings.mcell_binary_valid )


def project_files_path():
    ''' Consolidate the creation of the path to the project files'''
    # DUPLICATED FUNCTION ... This is the same function as in cellblender_panesl.py
    # print ( "DUPLICATED FUNCTION ... PLEASE FIX" )
    filepath = os.path.dirname(bpy.data.filepath)
    filepath, dot, blend = bpy.data.filepath.rpartition(os.path.extsep)
    filepath = filepath + "_files"
    filepath = os.path.join(filepath, "mcell")
    return filepath

def create_color_list():
    """ Create a list of colors to be assigned to the glyphs. """ 

    mcell = bpy.context.scene.mcell
    mcell.mol_viz.color_index = 0
    if not mcell.mol_viz.color_list:
        for i in range(8):
            mcell.mol_viz.color_list.add()
        mcell.mol_viz.color_list[0].vec = [0.8, 0.0, 0.0]
        mcell.mol_viz.color_list[1].vec = [0.0, 0.8, 0.0]
        mcell.mol_viz.color_list[2].vec = [0.0, 0.0, 0.8]
        mcell.mol_viz.color_list[3].vec = [0.0, 0.8, 0.8]
        mcell.mol_viz.color_list[4].vec = [0.8, 0.0, 0.8]
        mcell.mol_viz.color_list[5].vec = [0.8, 0.8, 0.0]
        mcell.mol_viz.color_list[6].vec = [1.0, 1.0, 1.0]
        mcell.mol_viz.color_list[7].vec = [0.0, 0.0, 0.0]

# Operators can't be callbacks, so we need this function for now.  This is
# temporary until we make importing viz data automatic.
def read_viz_data(self, context):
    bpy.ops.mcell.read_viz_data()


class MCELL_OT_read_viz_data(bpy.types.Operator):
    bl_idname = "mcell.read_viz_data"
    bl_label = "Read Viz Data"
    bl_description = "Load the molecule visualization data into Blender"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Called when the molecule files are actually to be read (when the
        # "Read Molecule Files" button is pushed or a seed value is selected
        # from the list)
        print("MCELL_OT_read_viz_data.execute() called")
        # self.report({'INFO'}, "Reading Visualization Data")

        mcell = context.scene.mcell

        # Force the top level mol_viz directory to be where the .blend file
        # lives plus "viz_data". The seed directories will live underneath it.
        mol_viz_top_level_dir = os.path.join(project_files_path(), "viz_data/")
        mol_viz_seed_list = glob.glob(os.path.join(mol_viz_top_level_dir, "*"))
        mol_viz_seed_list.sort()

        # Clear the list of seeds (e.g. seed_00001, seed_00002, etc) and the
        # list of files (e.g. my_project.cellbin.0001.dat,
        # my_project.cellbin.0002.dat)
        mcell.mol_viz.mol_viz_seed_list.clear()
        mcell.mol_viz.mol_file_list.clear()

        # Add all the seed directories to the mol_viz_seed_list collection
        # (seed_00001, seed_00002, etc)
        for mol_viz_seed in mol_viz_seed_list:
            new_item = mcell.mol_viz.mol_viz_seed_list.add()
            new_item.name = os.path.basename(mol_viz_seed)

        if mcell.mol_viz.mol_viz_seed_list:
            mol_file_dir = get_mol_file_dir()
            mcell.mol_viz.mol_file_dir = mol_file_dir

            mol_file_list = glob.glob(os.path.join(mol_file_dir, "*"))
            mol_file_list.sort()

            # Add all the viz_data files to mol_file_list collection (e.g.
            # my_project.cellbin.0001.dat, my_project.cellbin.0001.dat, etc)
            for mol_file_name in mol_file_list:
                new_item = mcell.mol_viz.mol_file_list.add()
                new_item.name = os.path.basename(mol_file_name)

            # If you previously had some viz data loaded, but reran the
            # simulation with less iterations, you can receive an index error.
            try:
                mol_file = mcell.mol_viz.mol_file_list[
                    mcell.mol_viz.mol_file_index]
            except IndexError:
                mcell.mol_viz.mol_file_index = 0

            create_color_list()
            set_viz_boundaries()

            mol_viz_update(self, context)
        return {'FINISHED'}


class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print("MCELL_OT_export_project.execute()")
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
        bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)

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

def set_viz_boundaries():
        mcell = bpy.context.scene.mcell

        mcell.mol_viz.mol_file_num = len(mcell.mol_viz.mol_file_list)
        mcell.mol_viz.mol_file_stop_index = mcell.mol_viz.mol_file_num - 1

        print("Setting frame_start to 0")
        print("Setting frame_end to ", len(mcell.mol_viz.mol_file_list)-1)
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = len(mcell.mol_viz.mol_file_list)-1


class MCELL_OT_select_viz_data(bpy.types.Operator):
    bl_idname = "mcell.select_viz_data"
    bl_label = "Read Viz Data"
    bl_description = "Read MCell Molecule Files for Visualization"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def __init__(self):
        self.directory = bpy.context.scene.mcell.mol_viz.mol_file_dir

    def execute(self, context):

        mcell = context.scene.mcell
        
        if (os.path.isdir(self.filepath)):
            mol_file_dir = self.filepath
        else:
            # Strip the file name off of the file path.
            mol_file_dir = os.path.dirname(self.filepath)
        mol_file_list = glob.glob(os.path.join(mol_file_dir, "*"))
        mol_file_list.sort()

        # Reset mol_file_list and mol_viz_seed_list to empty
        mcell.mol_viz.mol_file_list.clear()

        mcell.mol_viz.mol_file_dir = mol_file_dir
        for mol_file_name in mol_file_list:
            new_item = mcell.mol_viz.mol_file_list.add()
            new_item.name = os.path.basename(mol_file_name)

        create_color_list()
        set_viz_boundaries()
        mcell.mol_viz.mol_file_index = 0

        mol_viz_update(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        # Called when the file selection panel is requested
        # (when the "Set Molecule Viz Directory" button is pushed)
        print("MCELL_OT_select_viz_data.invoke() called")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def plot_rxns(plot_command):
    """ Plot a file """
    mcell = bpy.context.scene.mcell
    # Force the project directory to be where the .blend file lives
    project_dir = os.path.dirname(bpy.data.filepath)
    base_name = mcell.project_settings.base_name
    print("Plotting ", base_name, " with ", plot_command, " at ", project_dir)
    pid = subprocess.Popen(
        plot_command.split(), cwd=os.path.join(project_dir, "react_data"))


class MCELL_OT_plot_rxn_output_command(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_command"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using command line"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        print("Plotting with cmd=", mcell.reactions.plot_command)
        plot_rxns(mcell.reactions.plot_command)
        return {'FINISHED'}


class MCELL_OT_plot_rxn_output_generic(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_generic"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using specified plotting package"
    bl_options = {'REGISTER', 'UNDO'}

    plotter_button_label = bpy.props.StringProperty()

    def execute(self, context):
        mcell = context.scene.mcell
        plot_sep = mcell.rxn_output.plot_layout
        plot_legend = mcell.rxn_output.plot_legend

        combine_seeds = mcell.rxn_output.combine_seeds
        mol_colors = mcell.rxn_output.mol_colors

        plot_button_label = self.plotter_button_label

        # Look up the plotting module by its name

        for plot_module in cellblender.cellblender_info[
                'cellblender_plotting_modules']:
            mod_name = plot_module.get_name()
            if mod_name == plot_button_label:
                # Plot the data via this module
                # print("Preparing to call %s" % (mod_name))
                # The project_files_path is now where the MDL lives:
                data_path = project_files_path()
                data_path = os.path.join(data_path, "react_data")
                plot_spec_string = "xlabel=time(s) ylabel=count "
                if plot_legend != 'x':
                    plot_spec_string = plot_spec_string + "legend=" + plot_legend

                settings = mcell.project_settings

                # New plotting approach uses list and modification dates
                if mcell.rxn_output.rxn_output_list:
                    # Use the start_time.txt file to find files modified since
                    # MCell was started
                    start_time = os.stat(os.path.join(os.path.dirname(
                        bpy.data.filepath), "start_time.txt")).st_mtime
                    # print("Modification Time of start_time.txt is",
                    #       start_time)
                    for rxn_output in mcell.rxn_output.rxn_output_list:
                        molecule_name = rxn_output.molecule_name
                        object_name = rxn_output.object_name
                        region_name = rxn_output.region_name
                        fn = None
                        if rxn_output.count_location == 'World':
                            # fn = "%s.World.*.dat" % (molecule_name)
                            fn = "%s.World.dat" % (molecule_name)
                        elif rxn_output.count_location == 'Object':
                            # fn = "%s.%s.*.dat" % (molecule_name, object_name)
                            fn = "%s.%s.dat" % (molecule_name, object_name)
                        elif rxn_output.count_location == 'Region':
                            #fn = "%s.%s.%s.*.dat" % (molecule_name,
                            #                         object_name, region_name)
                            fn = "%s.%s.%s.dat" % (molecule_name,
                                                   object_name, region_name)
                        if fn is not None:
                            fn = os.path.join ( "seed_*", fn )
                            candidate_file_list = glob.glob(
                                os.path.join(data_path, fn))
                            # Without sorting, the seeds may not be increasing
                            candidate_file_list.sort()
                            #print("Candidate file list for %s:" % (fn))
                            #print("  ", candidate_file_list)
                            first_pass = True
                            for ffn in candidate_file_list:
                                if os.stat(ffn).st_mtime > start_time:
                                    # This file is both in the list and newer
                                    # than the run time for MCell

                                    # Create f as a relative path containing seed/file
                                    split1 = os.path.split(ffn)
                                    split2 = os.path.split(split1[0])
                                    f = os.path.join ( split2[1], split1[1] )
                                    
                                    color_string = ""
                                    if mol_colors:
                                        # Use molecule colors for graphs
                                        mol_mat_name = "mol_%s_mat" % (molecule_name)  # Should be standardized!!
                                        #print ( "Molecule Material Name = ", mol_mat_name )
                                        #Look up the material
                                        mats = bpy.data.materials
                                        mol_color = mats.get(mol_mat_name).diffuse_color
                                        #print ( "Molecule color = ", mol_mat.diffuse_color )

                                        mol_color_red = 255 * mol_color.r
                                        mol_color_green = 255 * mol_color.g
                                        mol_color_blue = 255 * mol_color.b
                                        color_string = " color=#%2.2x%2.2x%2.2x " % (mol_color_red, mol_color_green, mol_color_blue)

                                    base_name = os.path.basename(f)

                                    if combine_seeds:
                                        title_string = " title=" + base_name
                                    else:
                                        title_string = " title=" + f
                                    
                                    if plot_sep == ' ':
                                        # No title when all are on the same plot since only last will show
                                        title_string = ""

                                    if combine_seeds:
                                        psep = " "
                                        if first_pass:
                                            psep = plot_sep
                                            first_pass = False
                                        plot_spec_string = (
                                            plot_spec_string + psep + color_string +
                                            title_string + " f=" + f)
                                    else:
                                        plot_spec_string = (
                                            plot_spec_string + plot_sep + color_string +
                                            title_string + " f=" + f)

                print("Plotting from", data_path)
                print("Plotting spec", plot_spec_string)
                plot_module.plot(data_path, plot_spec_string)

        return {'FINISHED'}


class MCELL_OT_toggle_viz_molecules(bpy.types.Operator):
    bl_idname = "mcell.toggle_viz_molecules"
    bl_label = "Toggle Molecules"
    bl_description = "Toggle all molecules for export in visualization output"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        molecule_list = mcell.molecules.molecule_list

        # If the viz export option for the entire molecule list is already set
        # to true, then set them all to false
        if all([molecule.export_viz for molecule in molecule_list]):
            for molecule in molecule_list:
                molecule.export_viz = False
        else:
            for molecule in molecule_list:
                molecule.export_viz = True

        return {'FINISHED'}


class MCELL_OT_mol_viz_set_index(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_set_index"
    bl_label = "Set Molecule File Index"
    bl_description = "Set MCell Molecule File Index for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        if mcell.mol_viz.mol_file_list:
            i = mcell.mol_viz.mol_file_index
            if (i > mcell.mol_viz.mol_file_stop_index):
                i = mcell.mol_viz.mol_file_stop_index
            if (i < mcell.mol_viz.mol_file_start_index):
                i = mcell.mol_viz.mol_file_start_index
            mcell.mol_viz.mol_file_index = i
            mol_viz_update(self, context)
        return{'FINISHED'}


# These next two classes don't seem to be used anywhere. Unnecessary?
# Commented out for now.

"""
class MCELL_OT_mol_viz_next(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_next"
    bl_label = "Step to Next Molecule File"
    bl_description = "Step to Next MCell Molecule File for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        i = mcell.mol_viz.mol_file_index + mcell.mol_viz.mol_file_step_index
        if (i > mcell.mol_viz.mol_file_stop_index):
            i = mcell.mol_viz.mol_file_stop_index
        mcell.mol_viz.mol_file_index = i
        mol_viz_update(self, context)
        return{'FINISHED'}


class MCELL_OT_mol_viz_prev(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_prev"
    bl_label = "Step to Previous Molecule File"
    bl_description = "Step to Previous MCell Molecule File for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        i = mcell.mol_viz.mol_file_index - mcell.mol_viz.mol_file_step_index
        if (i < mcell.mol_viz.mol_file_start_index):
            i = mcell.mol_viz.mol_file_start_index
        mcell.mol_viz.mol_file_index = i
        mol_viz_update(self, context)
        return{'FINISHED'}
"""

#CellBlender operator helper functions:


@persistent
def frame_change_handler(scn):
    """ Update the viz data every time a frame is changed. """

    mcell = scn.mcell
    curr_frame = mcell.mol_viz.mol_file_index
    if (not curr_frame == scn.frame_current):
        mcell.mol_viz.mol_file_index = scn.frame_current
        bpy.ops.mcell.mol_viz_set_index()
        #scn.update()
        # Is the following code necessary?
        if mcell.mol_viz.render_and_save:
            scn.render.filepath = "//stores_on/frames/frame_%05d.png" % (
                scn.frame_current)
            bpy.ops.render.render(write_still=True)


#def render_handler(scn):
#    mcell = scn.mcell
#    curr_frame = mcell.mol_viz.mol_file_index
#    if (not curr_frame == scn.frame_current):
#        mcell.mol_viz.mol_file_index = scn.frame_current
#        bpy.ops.mcell.mol_viz_set_index()
#    scn.update()


def mol_viz_toggle_manual_select(self, context):
    """ Toggle the option to manually load viz data. """

    mcell = context.scene.mcell

    mcell.mol_viz.mol_file_dir = ""
    mcell.mol_viz.mol_file_name = ""
    mcell.mol_viz.mol_file_list.clear()
    mcell.mol_viz.mol_viz_seed_list.clear()

    if not mcell.mol_viz.manual_select_viz_dir:
        bpy.ops.mcell.read_viz_data()

    mol_viz_clear(mcell)


def get_mol_file_dir():
    """ Get the viz dir """

    mcell = bpy.context.scene.mcell

    # If you previously had some viz data loaded, but reran the
    # simulation with less seeds, you can receive an index error.
    try:
        active_mol_viz_seed = mcell.mol_viz.mol_viz_seed_list[
            mcell.mol_viz.active_mol_viz_seed_index]
    except IndexError:
        mcell.mol_viz.active_mol_viz_seed_index = 0
        active_mol_viz_seed = mcell.mol_viz.mol_viz_seed_list[0]
    filepath = os.path.join(
        project_files_path(), "viz_data/%s" % active_mol_viz_seed.name)

    return filepath


def mol_viz_update(self, context):
    """ Clear the old viz data. Draw the new viz data. """

    mcell = context.scene.mcell

    filename = mcell.mol_viz.mol_file_list[mcell.mol_viz.mol_file_index].name
    mcell.mol_viz.mol_file_name = filename
    # filepath is relative to blend file location under default scenarios (i.e.
    # when we can expect to find the standard CellBlender directory layout).
    if not mcell.mol_viz.manual_select_viz_dir:
        filepath = os.path.join(get_mol_file_dir(), filename)
    # filepath is absolute in case of manually selecting viz data, since it may
    # have nothing to do with the particular blend file in question.
    else:
        filepath = os.path.join(mcell.mol_viz.mol_file_dir, filename)

    # Save current global_undo setting. Turn undo off to save memory
    global_undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False

    mol_viz_clear(mcell)
    if mcell.mol_viz.mol_viz_enable:
        mol_viz_file_read(mcell, filepath)

    # Reset undo back to its original state
    bpy.context.user_preferences.edit.use_global_undo = global_undo
    return


def mol_viz_clear(mcell_prop):
    """ Clear the viz data from the previous frame. """

    mcell = mcell_prop
    scn = bpy.context.scene
    scn_objs = scn.objects
    meshes = bpy.data.meshes
    objs = bpy.data.objects
    for mol_item in mcell.mol_viz.mol_viz_list:
        mol_name = mol_item.name
#        mol_obj = scn_objs[mol_name]
        mol_obj = scn_objs.get(mol_name)
        if mol_obj:
            hide = mol_obj.hide

            mol_pos_mesh = mol_obj.data
            mol_pos_mesh_name = mol_pos_mesh.name
            mol_shape_obj_name = "%s_shape" % (mol_name)
            mol_shape_obj = objs.get(mol_shape_obj_name)
            if mol_shape_obj:
                mol_shape_obj.parent = None

            scn_objs.unlink(mol_obj)
            objs.remove(mol_obj)
            meshes.remove(mol_pos_mesh)

            mol_pos_mesh = meshes.new(mol_pos_mesh_name)
            mol_obj = objs.new(mol_name, mol_pos_mesh)
            scn_objs.link(mol_obj)

            if mol_shape_obj:
                mol_shape_obj.parent = mol_obj

            mol_obj.dupli_type = 'VERTS'
            mol_obj.use_dupli_vertices_rotation = True
            mols_obj = objs.get("molecules")
            mol_obj.parent = mols_obj

            mol_obj.hide = hide

#    scn.update()

    # Reset mol_viz_list to empty
    for i in range(len(mcell.mol_viz.mol_viz_list)-1, -1, -1):
        mcell.mol_viz.mol_viz_list.remove(i)


def mol_viz_file_read(mcell_prop, filepath):
    """ Draw the viz data for the current frame. """

    mcell = mcell_prop
    try:

#        begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#        print ("Processing molecules from file:    %s" % (filepath))

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, "rb")
        b = array.array("I")
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read Binary format molecule file:
            bin_data = 1
            while True:
                try:
                    # Variable names are a little hard to follow
                    # Here's what I assume they mean:
                    # ni = Initially, array of molecule name length.
                    # Later, array of number of molecule positions in xyz
                    # (essentially, the number of molecules multiplied by 3).
                    # ns = Array of ascii character codes for molecule name.
                    # s = String of molecule name.
                    # mt = Surface molecule flag.
                    ni = array.array("B")
                    ni.fromfile(mol_file, 1)
                    ns = array.array("B")
                    ns.fromfile(mol_file, ni[0])
                    s = ns.tostring().decode()
                    mol_name = "mol_%s" % (s)
                    mt = array.array("B")
                    mt.fromfile(mol_file, 1)
                    ni = array.array("I")
                    ni.fromfile(mol_file, 1)
                    mol_pos = array.array("f")
                    mol_orient = array.array("f")
                    mol_pos.fromfile(mol_file, ni[0])
#                    tot += ni[0]/3
                    if mt[0] == 1:
                        mol_orient.fromfile(mol_file, ni[0])
                    mol_dict[mol_name] = [mt[0], mol_pos, mol_orient]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                except:
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

        else:
            # Read ASCII format molecule file:
            bin_data = 0
            mol_file.close()
            # Create a list of molecule names, positions, and orientations
            # Each entry in the list is ordered like this (afaik):
            # [molec_name, [x_pos, y_pos, z_pos, x_orient, y_orient, z_orient]]
            # Orientations are zero in the case of volume molecules.
            mol_data = [[s.split()[0], [
                float(x) for x in s.split()[1:]]] for s in open(
                    filepath, "r").read().split("\n") if s != ""]

            for mol in mol_data:
                mol_name = "mol_%s" % (mol[0])
                if not mol_name in mol_dict:
                    mol_orient = mol[1][3:]
                    mt = 0
                    # Check to see if it's a surface molecule
                    if ((mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) |
                            (mol_orient[2] != 0.0)):
                        mt = 1
                    mol_dict[mol_name] = [
                        mt, array.array("f"), array.array("f")]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                mt = mol_dict[mol_name][0]
                mol_dict[mol_name][1].extend(mol[1][:3])
                if mt == 1:
                    mol_dict[mol_name][2].extend(mol[1][3:])

        # Get the parent object to all the molecule positions if it exists.
        # Otherwise, create it.
        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])
            mols_obj = bpy.context.selected_objects[0]
            mols_obj.name = "molecules"

        if mol_dict:
            meshes = bpy.data.meshes
            mats = bpy.data.materials
            objs = bpy.data.objects
            scn = bpy.context.scene
            scn_objs = scn.objects
            z_axis = mathutils.Vector((0.0, 0.0, 1.0))
            #ident_mat = mathutils.Matrix.Translation(
            #    mathutils.Vector((0.0, 0.0, 0.0)))

            for mol_name in mol_dict.keys():
                mol_mat_name = "%s_mat" % (mol_name)
                mol_type = mol_dict[mol_name][0]
                mol_pos = mol_dict[mol_name][1]
                mol_orient = mol_dict[mol_name][2]

                # Randomly orient volume molecules
                if mol_type == 0:
                    mol_orient.extend([random.uniform(
                        -1.0, 1.0) for i in range(len(mol_pos))])

                # Look-up mesh shape (glyph) template and create if needed
                mol_shape_mesh_name = "%s_shape" % (mol_name)
                mol_shape_obj_name = mol_shape_mesh_name
                mol_shape_mesh = meshes.get(mol_shape_mesh_name)
                if not mol_shape_mesh:
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=0, size=0.005, location=[0, 0, 0])
                    mol_shape_obj = bpy.context.active_object
                    mol_shape_obj.name = mol_shape_obj_name
                    mol_shape_obj.track_axis = "POS_Z"
                    mol_shape_mesh = mol_shape_obj.data
                    mol_shape_mesh.name = mol_shape_mesh_name
                else:
                    mol_shape_obj = objs.get(mol_shape_obj_name)

                # Look-up material, create if needed.
                # Associate material with mesh shape.
                mol_mat = mats.get(mol_mat_name)
                if not mol_mat:
                    mol_mat = mats.new(mol_mat_name)
                    mol_mat.diffuse_color = mcell.mol_viz.color_list[
                        mcell.mol_viz.color_index].vec
                    mcell.mol_viz.color_index = mcell.mol_viz.color_index + 1
                    if (mcell.mol_viz.color_index >
                            len(mcell.mol_viz.color_list)-1):
                        mcell.mol_viz.color_index = 0
                if not mol_shape_mesh.materials.get(mol_mat_name):
                    mol_shape_mesh.materials.append(mol_mat)

                # Create a "mesh" to hold instances of molecule positions
                mol_pos_mesh_name = "%s_pos" % (mol_name)
                mol_pos_mesh = meshes.get(mol_pos_mesh_name)
                if not mol_pos_mesh:
                    mol_pos_mesh = meshes.new(mol_pos_mesh_name)

                # Add and place vertices at positions of molecules
                mol_pos_mesh.vertices.add(len(mol_pos)//3)
                mol_pos_mesh.vertices.foreach_set("co", mol_pos)
                mol_pos_mesh.vertices.foreach_set("normal", mol_orient)

                # Create object to contain the mol_pos_mesh data
                mol_obj = objs.get(mol_name)
                if not mol_obj:
                    mol_obj = objs.new(mol_name, mol_pos_mesh)
                    scn_objs.link(mol_obj)
                    mol_shape_obj.parent = mol_obj
                    mol_obj.dupli_type = 'VERTS'
                    mol_obj.use_dupli_vertices_rotation = True
                    mol_obj.parent = mols_obj

#        scn.update()

#        utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
#        print ("     Processed %d molecules in %g seconds\n" % (
#            len(mol_data), utime))

    except IOError:
        print(("\n***** File not found: %s\n") % (filepath))

    except ValueError:
        print(("\n***** Invalid data in file: %s\n") % (filepath))


# Meshalyzer
class MCELL_OT_meshalyzer(bpy.types.Operator):
    bl_idname = "mcell.meshalyzer"
    bl_label = "Analyze Geometric Properties of Mesh"
    bl_description = "Analyze Geometric Properties of Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        objs = context.selected_objects

        mcell.meshalyzer.object_name = ""
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.watertight = ""
        mcell.meshalyzer.manifold = ""
        mcell.meshalyzer.normal_status = ""
        mcell.meshalyzer.area = 0
        mcell.meshalyzer.volume = 0
        mcell.meshalyzer.sav_ratio = 0

        if (len(objs) != 1):
            mcell.meshalyzer.status = "Please Select One Mesh Object"
            return {'FINISHED'}

        obj = objs[0]

        mcell.meshalyzer.object_name = obj.name

        if not (obj.type == 'MESH'):
            mcell.meshalyzer.status = "Selected Object Not a Mesh"
            return {'FINISHED'}

        t_mat = obj.matrix_world
        mesh = obj.data

        mcell.meshalyzer.vertices = len(mesh.vertices)
        mcell.meshalyzer.edges = len(mesh.edges)
        mcell.meshalyzer.faces = len(mesh.polygons)

        area = 0
        for f in mesh.polygons:
            if not (len(f.vertices) == 3):
                mcell.meshalyzer.status = "***** Mesh Not Triangulated *****"
                mcell.meshalyzer.watertight = "Mesh Not Triangulated"
                return {'FINISHED'}

            tv0 = mesh.vertices[f.vertices[0]].co * t_mat
            tv1 = mesh.vertices[f.vertices[1]].co * t_mat
            tv2 = mesh.vertices[f.vertices[2]].co * t_mat
            area = area + mathutils.geometry.area_tri(tv0, tv1, tv2)

        mcell.meshalyzer.area = area

        (edge_faces, edge_face_count) = make_efdict(mesh)

        is_closed = check_closed(edge_face_count)
        is_manifold = check_manifold(edge_face_count)
        is_orientable = check_orientable(mesh, edge_faces, edge_face_count)

        if is_orientable:
            mcell.meshalyzer.normal_status = "Consistent Normals"
        else:
            mcell.meshalyzer.normal_status = "Inconsistent Normals"

        if is_closed:
            mcell.meshalyzer.watertight = "Watertight Mesh"
        else:
            mcell.meshalyzer.watertight = "Non-watertight Mesh"

        if is_manifold:
            mcell.meshalyzer.manifold = "Manifold Mesh"
        else:
            mcell.meshalyzer.manifold = "Non-manifold Mesh"

        volume = 0
        if is_orientable and is_manifold and is_closed:
            volume = mesh_vol(mesh, t_mat)
            if volume >= 0:
                mcell.meshalyzer.normal_status = "Outward Facing Normals"
            else:
                mcell.meshalyzer.normal_status = "Inward Facing Normals"

        mcell.meshalyzer.volume = volume
        if (not volume == 0.0):
            mcell.meshalyzer.sav_ratio = area/volume

        mcell.meshalyzer.status = ""
        return {'FINISHED'}


def mesh_vol(mesh, t_mat):
    """Compute volume of triangulated, orientable, watertight, manifold mesh

    volume > 0 means outward facing normals
    volume < 0 means inward facing normals

    """

    volume = 0.0
    for f in mesh.polygons:
        tv0 = mesh.vertices[f.vertices[0]].co * t_mat
        tv1 = mesh.vertices[f.vertices[1]].co * t_mat
        tv2 = mesh.vertices[f.vertices[2]].co * t_mat
        x0 = tv0.x
        y0 = tv0.y
        z0 = tv0.z
        x1 = tv1.x
        y1 = tv1.y
        z1 = tv1.z
        x2 = tv2.x
        y2 = tv2.y
        z2 = tv2.z
        det = x0*(y1*z2-y2*z1)+x1*(y2*z0-y0*z2)+x2*(y0*z1-y1*z0)
        volume = volume + det

    volume = volume/6.0

    return(volume)


def make_efdict(mesh):

    edge_faces = {}
    edge_face_count = {}
    for f in mesh.polygons:
        for ek in f.edge_keys:
            if ek in edge_faces:
                edge_faces[ek] ^= f.index
                edge_face_count[ek] = edge_face_count[ek] + 1
            else:
                edge_faces[ek] = f.index
                edge_face_count[ek] = 1

    return(edge_faces, edge_face_count)


def check_manifold(edge_face_count):
    """ Make sure the object is manifold """

    for ek in edge_face_count.keys():
        if edge_face_count[ek] != 2:
            return (0)

    return(1)


def check_closed(edge_face_count):
    """ Make sure the object is closed (no leaks). """

    for ek in edge_face_count.keys():
        if not edge_face_count[ek] == 2:
            return (0)

    return(1)


def check_orientable(mesh, edge_faces, edge_face_count):

    ev_order = [[0, 1], [1, 2], [2, 0]]
    edge_checked = {}

    for f in mesh.polygons:
        for i in range(0, len(f.vertices)):
            ek = f.edge_keys[i]
            if not ek in edge_checked:
                edge_checked[ek] = 1
                if edge_face_count[ek] == 2:
                    nfi = f.index ^ edge_faces[ek]
                    nf = mesh.polygons[nfi]
                    for j in range(0, len(nf.vertices)):
                        if ek == nf.edge_keys[j]:
                            if f.vertices[ev_order[i][0]] != nf.vertices[
                                    ev_order[j][1]]:
                                return (0)
                            break

    return (1)


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


# Rebuild Model Objects List from Scratch
#   This is required to catch changes in names of objects.
#   Note: This function is registered as a load_post and save_pre handler
@persistent
def model_objects_update(context):
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

        return {'FINISHED'}


def check_model_object(self, context):
    """Checks for illegal object name"""

    mcell = context.scene.mcell
    model_object_list = mcell.model_objects.object_list
    model_object = model_object_list[mcell.model_objects.active_obj_index]

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
        mcell.molecule_glyphs.status = ""
        #new_glyph_name = "receptor_glyph"
        #mol_shape_name = "mol_Ca_shape"
        select_objs = context.selected_objects
        if (len(select_objs) != 1):
            mcell.molecule_glyphs.status = "Select One Molecule"
            return {'FINISHED'}
        if (select_objs[0].type != 'MESH'):
            mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
            return {'FINISHED'}

        mol_obj = select_objs[0]
        mol_shape_name = mol_obj.name

        new_glyph_name = mcell.molecule_glyphs.glyph

        bpy.ops.wm.link_append(
            directory=mcell.molecule_glyphs.glyph_lib,
            files=[{"name": new_glyph_name}], link=False, autoselect=False)

        mol_mat = mol_obj.material_slots[0].material
        new_mol_mesh = bpy.data.meshes[new_glyph_name]
        mol_obj.data = new_mol_mesh
        bpy.data.meshes.remove(bpy.data.meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        new_mol_mesh.materials.append(mol_mat)

        return {'FINISHED'}


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


def update_reaction_name_list(self, context):
    """ Format reaction data output. """

    mcell = bpy.context.scene.mcell
    mcell.reactions.reaction_name_list.clear()
    rxns = mcell.reactions.reaction_list
    # If a reaction has a reaction name, save it in reaction_name_list for
    # counting in the reaction output.
    if rxns:
        for rxn in rxns:
            if rxn.rxn_name:
                new_item = mcell.reactions.reaction_name_list.add()
                new_item.name = rxn.rxn_name


def check_rxn_output(self, context):
    """ Format reaction data output. """

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

    try:
        region_list = bpy.data.objects[object_name].mcell.regions.region_list
    except KeyError:
        # The object name isn't a blender object
        region_list = []

    status = ""

    if rxn_output.rxn_or_mol == 'Reaction':
        count_name = reaction_name
        name_list = reaction_list
    else:
        count_name = molecule_name
        name_list = mol_list

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


def check_val_str(val_str, min_val, max_val):
    """ Convert val_str to float if possible. Otherwise, generate error. """

    status = ""
    val = None

    try:
        val = float(val_str)
        if min_val is not None:
            if val < min_val:
                status = "Invalid value for %s: %s"
        if max_val is not None:
            if val > max_val:
                status = "Invalid value for %s: %s"
    except ValueError:
        status = "Invalid value for %s: %s"

    return (val, status)


def update_delay(self, context):
    """ Store the release pattern delay as a float if it's legal """

    mcell = context.scene.mcell
    release_pattern = mcell.release_patterns.release_pattern_list[
        mcell.release_patterns.active_release_pattern_index]
    delay_str = release_pattern.delay_str

    (delay, status) = check_val_str(delay_str, 0, None)

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

    (release_interval, status) = check_val_str(
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

    (train_duration, status) = check_val_str(train_duration_str, 1e-12, None)

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

    (train_interval, status) = check_val_str(train_interval_str, 1e-12, None)

    if status == "":
        release_pattern.train_interval = train_interval
    else:
        release_pattern.train_interval_str = "%g" % (
            release_pattern.train_interval)


def update_clamp_value(self, context):
    """ Store the clamp value as a float if it's legal or generate an error """

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

    (clamp_value, status) = check_val_str(clamp_value_str, 0, None)

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


def update_time_step(self, context):
    """ Store the time step as a float if it's legal or generate an error """

    mcell = context.scene.mcell
    time_step_str = mcell.initialization.time_step_str

    (time_step, status) = check_val_str(time_step_str, 0, None)

    if status == "":
        mcell.initialization.time_step = time_step
    else:
        status = status % ("time_step", time_step_str)
        mcell.initialization.time_step_str = "%g" % (
            mcell.initialization.time_step)

    mcell.initialization.status = status

    return


def update_time_step_max(self, context):
    """ Store the max time step as a float if it's legal or create an error """

    mcell = context.scene.mcell
    time_step_max_str = mcell.initialization.time_step_max_str

    if time_step_max_str:
        (time_step_max, status) = check_val_str(time_step_max_str, 0, None)

        if not status:
            mcell.initialization.time_step_max = time_step_max
        else:
            status = status % ("time_step_max", time_step_max_str)
            mcell.initialization.time_step_max_str = ""

        mcell.initialization.status = status


def update_space_step(self, context):
    """ Store the space step as a float if it's legal or create an error """

    mcell = context.scene.mcell
    space_step_str = mcell.initialization.space_step_str

    if space_step_str:
        (space_step, status) = check_val_str(space_step_str, 0, None)

        if not status:
            mcell.initialization.space_step = space_step
        else:
            status = status % ("space_step", space_step_str)
            mcell.initialization.space_step_str = ""

        mcell.initialization.status = status


def update_interaction_radius(self, context):
    """ Store interaction radius as a float if legal or create an error """

    mcell = context.scene.mcell
    interaction_radius_str = mcell.initialization.interaction_radius_str

    if interaction_radius_str:
        (interaction_radius, status) = check_val_str(
            interaction_radius_str, 0, None)

        if not status:
            mcell.initialization.interaction_radius = interaction_radius
        else:
            status = status % ("interaction_radius", interaction_radius_str)
            mcell.initialization.interaction_radius_str = ""

        mcell.initialization.status = status


def update_radial_directions(self, context):
    """ Store radial directions as a float if it's legal or create an error """

    mcell = context.scene.mcell
    radial_directions_str = mcell.initialization.radial_directions_str

    if radial_directions_str:
        (radial_directions, status) = check_val_str(
            radial_directions_str, 0, None)

        if status == "":
            mcell.initialization.radial_directions = radial_directions
        else:
            status = status % ("radial_directions", radial_directions_str)
            mcell.initialization.radial_directions_str = ""

        mcell.initialization.status = status


def update_radial_subdivisions(self, context):
    """ Store radial subdivisions as a float if legal or create an error """

    mcell = context.scene.mcell
    radial_subdivisions_str = mcell.initialization.radial_subdivisions_str

    if radial_subdivisions_str:
        (radial_subdivisions, status) = check_val_str(
            radial_subdivisions_str, 0, None)

        if status == "":
            mcell.initialization.radial_subdivisions = radial_subdivisions
        else:
            status = status % ("radial_subdivisions", radial_subdivisions_str)
            mcell.initialization.radial_subdivisions_str = ""

        mcell.initialization.status = status


def update_vacancy_search_distance(self, context):
    """ Store vacancy search distance as float if legal or create an error """

    mcell = context.scene.mcell
    vacancy_search_distance_str = \
        mcell.initialization.vacancy_search_distance_str

    if vacancy_search_distance_str:
        (vacancy_search_distance, status) = check_val_str(
            vacancy_search_distance_str, 0, None)

        if not status:
            mcell.initialization.vacancy_search_distance = \
                vacancy_search_distance
        else:
            status = status % (
                "vacancy_search_distance", vacancy_search_distance_str)
            mcell.initialization.vacancy_search_distance_str = ""

        mcell.initialization.status = status


def update_diffusion_constant(self, context):
    """ Store the diffusion constant as a float if it's legal """

    mcell = context.scene.mcell
    mol = mcell.molecules.molecule_list[mcell.molecules.active_mol_index]
   
    diffusion_constant_str = mol.diffusion_constant_str

    (diffusion_constant, status) = check_val_str(
        diffusion_constant_str, 0, None)
     
    if status == "":
        mol.diffusion_constant = diffusion_constant
    else:
        #status = status % ("diffusion_constant", diffusion_constant_str)
        mol.diffusion_constant_str = "%g" % (mol.diffusion_constant)

    #mcell.molecules.status = status

    return


def update_custom_time_step(self, context):
    """ Store the custom time step as a float if it's legal """

    mcell = context.scene.mcell
    mol = mcell.molecules.molecule_list[mcell.molecules.active_mol_index]
    custom_time_step_str = mol.custom_time_step_str

    (custom_time_step, status) = check_val_str(custom_time_step_str, 0, None)

    if status == "":
        mol.custom_time_step = custom_time_step
    else:
        #status = status % ("custom_time_step", custom_time_step_str)
        mol.custom_time_step_str = "%g" % (mol.custom_time_step)

    #mcell.molecules.status = status

    return


def update_custom_space_step(self, context):
    """ Store the custom space step as a float if it's legal """

    mcell = context.scene.mcell
    mol = mcell.molecules.molecule_list[mcell.molecules.active_mol_index]
    custom_space_step_str = mol.custom_space_step_str

    (custom_space_step, status) = check_val_str(custom_space_step_str, 0, None)

    if status == "":
        mol.custom_space_step = custom_space_step
    else:
        #status = status % ("custom_space_step", custom_space_step_str)
        mol.custom_space_step_str = "%g" % (mol.custom_space_step)

    #mcell.molecules.status = status

    return


def update_fwd_rate(self, context):
    """ Store the forward reaction rate as a float if it's legal """

    mcell = context.scene.mcell
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    fwd_rate_str = rxn.fwd_rate_str

    (fwd_rate, status) = check_val_str(fwd_rate_str, 0, None)

    if status == "":
        rxn.fwd_rate = fwd_rate
    else:
        #status = status % ("fwd_rate", fwd_rate_str)
        rxn.fwd_rate_str = "%g" % (rxn.fwd_rate)

    #mcell.reactions.status = status

    return


def update_bkwd_rate(self, context):
    """ Store the backward reaction rate as a float if it's legal """

    mcell = context.scene.mcell
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    bkwd_rate_str = rxn.bkwd_rate_str

    (bkwd_rate, status) = check_val_str(bkwd_rate_str, 0, None)

    if status == "":
        rxn.bkwd_rate = bkwd_rate
    else:
        #status = status % ("bkwd_rate", bkwd_rate_str)
        rxn.bkwd_rate_str = "%g" % (rxn.bkwd_rate)

    #mcell.reactions.status = status

    return
