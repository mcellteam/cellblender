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
import datetime
import multiprocessing

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
        mcell_obj.regions.region_list[
            mcell_obj.regions.active_reg_index].name = "Region"
        return {'FINISHED'}


class MCELL_OT_region_remove(bpy.types.Operator):
    bl_idname = "mcell.region_remove"
    bl_label = "Remove Surface Region"
    bl_description = "Remove selected surface region from object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell_obj = context.object.mcell
        mcell_obj.regions.region_list.remove(
            mcell_obj.regions.active_reg_index)
        mcell_obj.regions.active_reg_index -= 1
        if (mcell_obj.regions.active_reg_index < 0):
            mcell_obj.regions.active_reg_index = 0

        if mcell_obj.regions.region_list:
            check_region(self, context)
        else:
            mcell_obj.regions.status = ""

        return {'FINISHED'}


def check_region(self, context):
    """Checks for duplicate or illegal region name"""

    mcell_obj = context.object.mcell
    reg_list = mcell_obj.regions.region_list
    reg = reg_list[mcell_obj.regions.active_reg_index]

    status = ""

    # Check for duplicate region name
    reg_keys = reg_list.keys()
    if reg_keys.count(reg.name) > 1:
        status = "Duplicate region: %s" % (reg.name)

    # Check for illegal names (Starts with a letter. No special characters)
    reg_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(reg_filter, reg.name)
    if m is None:
        status = "Region name error: %s" % (reg.name)

    mcell_obj.regions.status = status

    return


class MCELL_OT_region_faces_assign(bpy.types.Operator):
    bl_idname = "mcell.region_faces_assign"
    bl_label = "Assign Selected Faces To Surface Region"
    bl_description = "Assign selected faces to surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        if (active_obj.data.total_face_sel > 0):
            if not active_obj.data.get("mcell"):
                active_obj.data["mcell"] = {}
            if not active_obj.data["mcell"].get("regions"):
                active_obj.data["mcell"]["regions"] = {}
            reg = obj_regs.region_list[obj_regs.active_reg_index]
            if not active_obj.data["mcell"]["regions"].get(reg.name):
                active_obj.data["mcell"]["regions"][reg.name] = []
            mesh = active_obj.data
            face_set = set([])
            for f in active_obj.data["mcell"]["regions"][reg.name]:
                face_set.add(f)
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    face_set.add(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            reg_faces = list(face_set)
            reg_faces.sort()
            active_obj.data["mcell"]["regions"][reg.name] = reg_faces

#        obj_regs = active_obj.mcell.regions
#        reg = obj_regs.region_list[obj_regs.active_reg_index]
#        mesh = active_obj.data
#        for f in mesh.polygons:
#            if f.select:
#                reg.faces.add()
#                reg.active_face_index = len(reg.faces)-1
#                reg.faces[reg.active_face_index].index = f.index

        return {'FINISHED'}


class MCELL_OT_region_faces_remove(bpy.types.Operator):
    bl_idname = "mcell.region_faces_remove"
    bl_label = "Remove Selected Faces From Surface Region"
    bl_description = "Remove selected faces from surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        if (active_obj.data.total_face_sel > 0):
            if not active_obj.data.get("mcell"):
                active_obj.data["mcell"] = {}
            if not active_obj.data["mcell"].get("regions"):
                active_obj.data["mcell"]["regions"] = {}
            reg = obj_regs.region_list[obj_regs.active_reg_index]
            if not active_obj.data["mcell"]["regions"].get(reg.name):
                active_obj.data["mcell"]["regions"][reg.name] = []
            mesh = active_obj.data
            face_set = set(
                active_obj.data["mcell"]["regions"][reg.name].to_list())
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    if f.index in face_set:
                        face_set.remove(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            reg_faces = list(face_set)
            reg_faces.sort()
            active_obj.data["mcell"]["regions"][reg.name] = reg_faces

        return {'FINISHED'}


class MCELL_OT_region_faces_select(bpy.types.Operator):
    bl_idname = "mcell.region_faces_select"
    bl_label = "Select Faces of Selected Surface Region"
    bl_description = "Select faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        obj_regs = active_obj.mcell.regions
        if not active_obj.data.get("mcell"):
            active_obj.data["mcell"] = {}
        if not active_obj.data["mcell"].get("regions"):
            active_obj.data["mcell"]["regions"] = {}
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        if not active_obj.data["mcell"]["regions"].get(reg.name):
            active_obj.data["mcell"]["regions"][reg.name] = []
        mesh = active_obj.data
        face_set = set(active_obj.data["mcell"]["regions"][reg.name].to_list())
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
        if not active_obj.data.get("mcell"):
            active_obj.data["mcell"] = {}
        if not active_obj.data["mcell"].get("regions"):
            active_obj.data["mcell"]["regions"] = {}
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        if not active_obj.data["mcell"]["regions"].get(reg.name):
            active_obj.data["mcell"]["regions"][reg.name] = []
        mesh = active_obj.data
        face_set = set(active_obj.data["mcell"]["regions"][reg.name].to_list())
        bpy.ops.object.mode_set(mode='OBJECT')
        msm = context.tool_settings.mesh_select_mode[0:]
        context.tool_settings.mesh_select_mode = [False, False, True]
        for f in face_set:
            mesh.polygons[f].select = False
        bpy.ops.object.mode_set(mode='EDIT')

        context.tool_settings.mesh_select_mode = msm
        return {'FINISHED'}


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
    bl_description = "Automatically generate partition boundaries"
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
        else:
            mcell.molecules.status = ""

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

    mcell.molecules.status = status

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
        mcell.reactions.reaction_list[
            mcell.reactions.active_rxn_index].name = "Reaction"
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
        else:
            mcell.reactions.status = ""

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
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
    reactants = rxn.reactants.split(" + ")
    for reactant in reactants:
        m = re.match(mol_filter, reactant)
        if m is None:
            status = "Reactant error: %s" % (reactant)
            break
        else:
            mol_name = m.group(1)
            if not mol_name in mol_list:
                status = "Undefine molecule: %s" % (mol_name)

    #Check syntax of product specification
    if rxn.products == "NULL":
        if rxn.type == 'reversible':
            rxn.type = 'irreversible'
    else:
        products = rxn.products.split(" + ")
        for product in products:
            m = re.match(mol_filter, product)
            if m is None:
                status = "Product error: %s" % (product)
                break
            else:
                mol_name = m.group(1)
                if not mol_name in mol_list:
                    status = "Undefine molecule: %s" % (mol_name)

    mcell.reactions.status = status
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
        new_name = "Surface_Class_Property"
        active_surf_class.surf_class_props_list[
            active_surf_class.active_surf_class_props_index].name = new_name

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

        if active_surf_class.surf_class_props_list:
            check_surf_class_props(self, context)
        else:
            surf_class.surf_class_props_status = ""

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

    surf_class.surf_class_status = status

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

    if molecule:
        surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (
            molecule, orient, surf_class_type)
    else:
        surf_class_props.name = "Molec.: NA   Orient.: %s   Type: %s" % (
            orient, surf_class_type)

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

    mcell.surface_classes.surf_class_props_status = status

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
        new_name = "Modify_Surface_Region"
        mod_surf_regions.mod_surf_regions_list[
            mod_surf_regions.active_mod_surf_regions_index].name = new_name

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


def format_mod_surf_regions_entry(surf_class_name, object_name, region_name):
    """Check if the entries in Modify Surface Regions exist and format them"""
    if not surf_class_name:
        surf_class_name = "NA"
    if not object_name:
        object_name = "NA"
    if not region_name:
        region_name = "NA"

    mod_surf_regions_entry = "Surface Class: %s   Object: %s   Region: %s" % (
        surf_class_name, object_name, region_name)

    return(mod_surf_regions_entry)


def check_assigned_surface_class(self, context):
    """Make sure the surface class name is valid and format the list entry"""

    mcell = context.scene.mcell
    surf_class_list = mcell.surface_classes.surf_class_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    active_mod_surf_regions.name = format_mod_surf_regions_entry(
        surf_class_name, object_name, region_name)

    status = ""

    #Make sure there is something in the Defined Surface Classes list
    if not surf_class_list:
        status = "No surface classes defined"
    #Make sure the user entered surf class is in Defined Surface Classes list
    elif not surf_class_name in surf_class_list:
        status = "Undefined surface class: %s" % surf_class_name

    mod_surf_regions.status = status

    return


def check_assigned_object(self, context):
    """Make sure the object name is valid and format the list entry"""

    mcell = context.scene.mcell
    obj_list = mcell.model_objects.object_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    active_mod_surf_regions.name = format_mod_surf_regions_entry(
        surf_class_name, object_name, region_name)

    status = ""

    #Make sure there is something in the Model Objects list
    if not obj_list:
        status = "No objects available"
    #Make sure the user entered object name is in the Model Objects list
    elif not active_mod_surf_regions.object_name in obj_list:
        status = "Undefined object: %s" % active_mod_surf_regions.object_name

    mod_surf_regions.status = status

    return


def check_modified_region(self, context):
    """Make sure the region name is valid and format the list entry"""

    mcell = context.scene.mcell
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    region_list = bpy.data.objects[
        active_mod_surf_regions.object_name].mcell.regions.region_list
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    active_mod_surf_regions.name = format_mod_surf_regions_entry(
        surf_class_name, object_name, region_name)

    status = ""

    try:
        if not region_list:
            status = "The selected object has no surface regions"
        elif not region_name in region_list:
            status = "Undefined region: %s" % region_name
    except KeyError:
        #the object name in mod surf regions isn't a blender object
        pass

    mod_surf_regions.status = status

    return


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
        else:
            mcell.release_sites.status = ""

        return {'FINISHED'}


def check_release_site(self, context):
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

    mcell.release_sites.status = status

    return


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

    mcell.release_sites.status = status

    return


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
                    if not obj.data.get("mcell"):
                        status = "Undefined region: %s" % (reg_name)
                        break
                    if not obj.data["mcell"].get("regions"):
                        status = "Undefined region: %s" % (reg_name)
                        break
                    if not obj.data["mcell"]["regions"].get(reg_name):
                        status = "Undefined region: %s" % (reg_name)
                        break
            else:
                obj_name = m.group("obj_name_only")
                if not obj_name in scn.objects:
                    status = "Undefined object: %s" % (obj_name)
                    break

    mcell.release_sites.status = status

    return


class MCELL_OT_set_mcell_binary(bpy.types.Operator):
    bl_idname = "mcell.set_mcell_binary"
    bl_label = "Set MCell Binary"
    bl_description = "Set MCell Binary"
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


def run_sim(seed):
    """ Run the MCell simulations. """

    mcell = bpy.context.scene.mcell
    mcell_binary = mcell.project_settings.mcell_binary
    project_dir = mcell.project_settings.project_dir
    base_name = mcell.project_settings.base_name
    mdl_filepath = '%s%s.main.mdl' % (project_dir, base_name)
    # Log filename will be log.year-month-day_hour:minute_seed.txt
    # (e.g. log.2013-03-12_11:45_1.txt)
    time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
    log_filepath = "%s%s" % (project_dir, "log.%s_%d.txt" % (time_now, seed))
    error_filepath = "%s%s" % (
        project_dir, "error.%s_%d.txt" % (time_now, seed))

    if mcell.run_simulation.error_file == 'none':
        error_file = subprocess.DEVNULL
    elif mcell.run_simulation.error_file == 'console':
        error_file = None

    if mcell.run_simulation.log_file == 'none':
        log_file = subprocess.DEVNULL
    elif mcell.run_simulation.log_file == 'console':
        log_file = None

    # Both output and error log file
    print ( "Running", mcell_binary, "with", mdl_filepath )
    subprocess_cwd = os.path.dirname(mdl_filepath)
    print ( "  Should run from cwd =", subprocess_cwd )
    if (mcell.run_simulation.log_file == 'file' and
            mcell.run_simulation.error_file == 'file'):
        with open(log_filepath, "w") as log_file, open(
                error_filepath, "w") as error_file:
            subprocess.call(
                [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
                cwd=subprocess_cwd,
                stdout=log_file, stderr=error_file)
    # Only output log file
    elif mcell.run_simulation.log_file == 'file':
        with open(log_filepath, "w") as log_file:
            subprocess.call(
                [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
                cwd=subprocess_cwd,
                stdout=log_file, stderr=error_file)
    # Only error log file
    elif mcell.run_simulation.error_file == 'file':
        with open(error_filepath, "w") as error_file:
            subprocess.call(
                [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
                cwd=subprocess_cwd,
                stdout=log_file, stderr=error_file)
    # Neither error nor output log
    else:
        subprocess.call(
            [mcell_binary, '-seed', '%d' % seed, mdl_filepath],
            cwd=subprocess_cwd,
            stdout=log_file, stderr=error_file)


class MCELL_OT_run_simulation(bpy.types.Operator):
    bl_idname = "mcell.run_simulation"
    bl_label = "Run MCell Simulation"
    bl_description = "Run MCell Simulation"
    bl_options = {'REGISTER'}

    def execute(self, context):
        self.report({'INFO'}, "Simulation Running")
        mcell = context.scene.mcell
        start = mcell.run_simulation.start_seed
        end = mcell.run_simulation.end_seed + 1
        mcell_processes = mcell.run_simulation.mcell_processes

        # Create a pool of mcell processes.
        # NOTE: There could very well be something wrong or inneficient about
        # this implementation, and it should be reviewed.
        pool = multiprocessing.Pool(processes=mcell_processes)
        pool.map_async(run_sim, range(start, end))

        return {'FINISHED'}


class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell

        model_objects_update(context)
        if mcell.export_project.export_format == 'mcell_mdl_unified':
            filepath = mcell.project_settings.project_dir + "/" + \
                mcell.project_settings.base_name + ".main.mdl"
            bpy.ops.export_mdl_mesh.mdl('INVOKE_DEFAULT', filepath=filepath)
        elif mcell.export_project.export_format == 'mcell_mdl_modular':
            filepath = mcell.project_settings.project_dir + "/" + \
                mcell.project_settings.base_name + ".main.mdl"
            bpy.ops.export_mdl_mesh.mdl('INVOKE_DEFAULT', filepath=filepath)

        return {'FINISHED'}


class MCELL_OT_set_project_dir(bpy.types.Operator):
    bl_idname = "mcell.set_project_dir"
    bl_label = "Set Project Directory"
    bl_description = "Set CellBlender Project Directory"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def __init__(self):
        self.directory = bpy.context.scene.mcell.project_settings.project_dir

    # Note: use classmethod "poll" to determine when
    # runability of operator is valid
    #
    #    @classmethod
    #    def poll(cls, context):
    #        return context.object is not None

    def execute(self, context):

        mcell = context.scene.mcell
        if (os.path.isdir(self.filepath)):
            dir = self.filepath
        else:
            dir = os.path.dirname(self.filepath)

        # Reset mol_file_list to empty
        for i in range(mcell.mol_viz.mol_file_num-1, -1, -1):
            mcell.mol_viz.mol_file_list.remove(i)

        mcell.mol_viz.mol_file_name = ""
        mcell.project_settings.project_dir = dir
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MCELL_OT_set_mol_viz_dir(bpy.types.Operator):
    bl_idname = "mcell.set_mol_viz_dir"
    bl_label = "Read Molecule Files"
    bl_description = "Read MCell Molecule Files for Visualization"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def __init__(self):
        self.directory = bpy.context.scene.mcell.mol_viz.mol_file_dir

    # Note: use classmethod "poll" to determine when
    # runability of operator is valid
    #
    #    @classmethod
    #    def poll(cls, context):
    #        return context.object is not None

    def execute(self, context):

        mcell = context.scene.mcell
        if (os.path.isdir(self.filepath)):
            mol_file_dir = self.filepath
        else:
            mol_file_dir = os.path.dirname(self.filepath)
        mol_file_list = glob.glob(mol_file_dir + "/*")
        mol_file_list.sort()

        # Reset mol_file_list to empty
        for i in range(mcell.mol_viz.mol_file_num-1, -1, -1):
            mcell.mol_viz.mol_file_list.remove(i)

        mcell.mol_viz.mol_file_dir = mol_file_dir
        i = 0
        for mol_file_name in mol_file_list:
            new_item = mcell.mol_viz.mol_file_list.add()
            new_item.name = os.path.basename(mol_file_name)
            i += 1

        mcell.mol_viz.mol_file_num = len(mcell.mol_viz.mol_file_list)
        mcell.mol_viz.mol_file_stop_index = mcell.mol_viz.mol_file_num-1
        mcell.mol_viz.mol_file_index = 0

        mcell.mol_viz.color_index = 0
        if len(mcell.mol_viz.color_list) == 0:
            # Create a list of colors to be assigned to the glyphs
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

        print("Setting frame_end to ", len(mcell.mol_viz.mol_file_list))
        context.scene.frame_end = len(mcell.mol_viz.mol_file_list)
        mol_viz_update(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def plot_rxns ( plot_command ):
    """ Plot a file """
    mcell = bpy.context.scene.mcell
    project_dir = mcell.project_settings.project_dir
    base_name = mcell.project_settings.base_name
    print ( "Plotting ", base_name, " with ", plot_command, " at ", project_dir )
    # subprocess.call ( plot_command.split(), cwd=os.path.join(project_dir,"react_data") )
    pid = subprocess.Popen ( plot_command.split(), cwd=os.path.join(project_dir,"react_data") )


class MCELL_OT_plot_rxn_output(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using specified plotting package"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        print ( "Plotting with cmd=", mcell.reactions.plot_command )
        plot_rxns ( mcell.reactions.plot_command )
        return {'FINISHED'}




class MCELL_OT_plot_rxn_output_mpl(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_mpl"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using MatPlotLib"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        plot_sep = mcell.rxn_output.plot_layout

        program_path = find_in_path("python")
        if program_path == None:
            print ( "Unable to plot: python not found in path" )
        else:
            mcell = context.scene.mcell
            print ( "CellBlender path = ", cellblender.cellblender_info['cellblender_addon_path'] )
            plot_cmd = cellblender.cellblender_info['cellblender_addon_path']
            plot_cmd = os.path.join(plot_cmd, 'data_plotters')
            plot_cmd = os.path.join(plot_cmd, 'mpl_plot')
            plot_cmd = os.path.join(plot_cmd, 'mpl_plot.py')
            plot_cmd = program_path + ' ' + plot_cmd
            
            project_dir = mcell.project_settings.project_dir
            defaults_name = os.path.join(project_dir,"react_data")
            defaults_name = os.path.join(defaults_name,"mpl_defaults.py")
            print ( "Checking for defaults file at: " + defaults_name )
            if os.path.exists(defaults_name):
              plot_cmd = plot_cmd + " defs=" + defaults_name

            settings = mcell.project_settings
            if mcell.rxn_output.rxn_output_list:
                for rxn_output in mcell.rxn_output.rxn_output_list:
                    molecule_name = rxn_output.molecule_name
                    object_name = rxn_output.object_name
                    region_name = rxn_output.region_name
                    if rxn_output.count_location == 'World':
                        fn = "%s.World.0001.dat" % (molecule_name)
                        plot_cmd = plot_cmd + plot_sep + " title=" + fn + " f=" + fn
                    elif rxn_output.count_location == 'Object':
                        fn = "%s.%s.0001.dat" % (molecule_name, object_name)
                        plot_cmd = plot_cmd + plot_sep + " title=" + fn + " f=" + fn
                    elif rxn_output.count_location == 'Region':
                        fn = "%s.%s.%s.0001.dat" % (molecule_name, object_name, region_name)
                        plot_cmd = plot_cmd + plot_sep + " title=" + fn + " f=" + fn

            print ( "plot_cmd = ", plot_cmd )
            plot_rxns ( plot_cmd )
        return {'FINISHED'}




class MCELL_OT_plot_rxn_output_simple(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_simple"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using a simple Python script"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        program_path = find_in_path("python")
        if program_path == None:
            print ( "Unable to plot: python not found in path" )
        else:
            mcell = context.scene.mcell
            print ( "CellBlender path = ", cellblender.cellblender_info['cellblender_addon_path'] )
            plot_cmd = cellblender.cellblender_info['cellblender_addon_path']
            plot_cmd = os.path.join(plot_cmd, 'data_plotters')
            plot_cmd = os.path.join(plot_cmd, 'mpl_simple')
            plot_cmd = os.path.join(plot_cmd, 'mpl_simple.py')
            plot_cmd = program_path + ' ' + plot_cmd

            settings = mcell.project_settings
            if mcell.rxn_output.rxn_output_list:
                for rxn_output in mcell.rxn_output.rxn_output_list:
                    molecule_name = rxn_output.molecule_name
                    object_name = rxn_output.object_name
                    region_name = rxn_output.region_name
                    if rxn_output.count_location == 'World':
                        plot_cmd = plot_cmd + " " + "%s.World.0001.dat" % (molecule_name)
                    elif rxn_output.count_location == 'Object':
                        plot_cmd = plot_cmd + " " + "%s.%s.0001.dat" % (molecule_name, object_name)
                    elif rxn_output.count_location == 'Region':
                        plot_cmd = plot_cmd + " " + "%s.%s.%s.0001.dat" % (molecule_name, object_name, region_name)

            print ( "plot_cmd = ", plot_cmd )
            plot_rxns ( plot_cmd )
        return {'FINISHED'}


class MCELL_OT_plot_rxn_output_xmgrace(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_xmgrace"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using xmgrace"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        program_path = find_in_path("xmgrace")
        if program_path == None:
            print ( "Unable to plot: xmgrace not found in path" )
        else:
            mcell = context.scene.mcell
            plot_cmd = program_path

            settings = mcell.project_settings
            if mcell.rxn_output.rxn_output_list:
                for rxn_output in mcell.rxn_output.rxn_output_list:
                    molecule_name = rxn_output.molecule_name
                    object_name = rxn_output.object_name
                    region_name = rxn_output.region_name
                    if rxn_output.count_location == 'World':
                        plot_cmd = plot_cmd + " %s.World.0001.dat" % (molecule_name)
                    elif rxn_output.count_location == 'Object':
                        plot_cmd = plot_cmd + " %s.%s.0001.dat" % (molecule_name, object_name)
                    elif rxn_output.count_location == 'Region':
                        plot_cmd = plot_cmd + " %s.%s.%s.0001.dat" % (molecule_name, object_name, region_name)

            print ( "plot_cmd = ", plot_cmd )
            plot_rxns ( plot_cmd )
        return {'FINISHED'}


class MCELL_OT_plot_rxn_output_java(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_java"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using a simple Java program"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        program_path = find_in_path("java")
        if program_path == None:
            print ( "Unable to plot: java not found in path" )
        else:
            mcell = context.scene.mcell
            print ( "CellBlender path = ", cellblender.cellblender_info['cellblender_addon_path'] )
            plot_cmd = cellblender.cellblender_info['cellblender_addon_path']
            plot_cmd = os.path.join(plot_cmd, 'data_plotters')
            plot_cmd = os.path.join(plot_cmd, 'java_plot')
            plot_cmd = os.path.join(plot_cmd, 'PlotData.jar')
            plot_cmd = program_path + ' -jar ' + plot_cmd

            settings = mcell.project_settings
            if mcell.rxn_output.rxn_output_list:
                for rxn_output in mcell.rxn_output.rxn_output_list:
                    molecule_name = rxn_output.molecule_name
                    object_name = rxn_output.object_name
                    region_name = rxn_output.region_name
                    if rxn_output.count_location == 'World':
                        plot_cmd = plot_cmd + " fxy=" + "%s.World.0001.dat" % (molecule_name)
                    elif rxn_output.count_location == 'Object':
                        plot_cmd = plot_cmd + " fxy=" + "%s.%s.0001.dat" % (molecule_name, object_name)
                    elif rxn_output.count_location == 'Region':
                        plot_cmd = plot_cmd + " fxy=" + "%s.%s.%s.0001.dat" % (molecule_name, object_name, region_name)

            print ( "plot_cmd = ", plot_cmd )
            plot_rxns ( plot_cmd )
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
        if (len(mcell.mol_viz.mol_file_list) > 0):
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


def mol_viz_update(self, context):
    """ Clear the old viz data. Draw the new viz data. """

    mcell = context.scene.mcell

    filename = mcell.mol_viz.mol_file_list[mcell.mol_viz.mol_file_index].name
    mcell.mol_viz.mol_file_name = filename
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

        if is_orientable and is_manifold and is_closed:
            volume = mesh_vol(mesh, t_mat)
            mcell.meshalyzer.volume = volume
            if volume >= 0:
                mcell.meshalyzer.normal_status = "Outward Facing Normals"
            else:
                mcell.meshalyzer.normal_status = "Inward Facing Normals"

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

    model_obj_names = [obj.name for obj in sobjs if obj.mcell.include == True]

    # Note: This bit only needed to convert
    #       old model object list (pre 0.1 rev_55) to new style.
    #       Old style did not have obj.mcell.include Boolean Property.
    if ((len(model_obj_names) == 0) & (len(mobjs.object_list) > 0)):
        for i in range(len(mobjs.object_list)-1):
            obj = sobjs.get(mobjs.object_list[i].name)
            if obj:
              obj.mcell.include = True
        model_obj_names = [
            obj.name for obj in sobjs if obj.mcell.include == True]

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

        mobjs.active_obj_index = active_index

    return


class MCELL_OT_model_objects_add(bpy.types.Operator):
    bl_idname = "mcell.model_objects_add"
    bl_label = "Model Objects Include"
    bl_description = "Include selected objects in model object export list"
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
    bl_description = "Remove current item from model object export list"
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
    l_description = "Remove selected reaction data output from an MCell model"
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
        else:
            mcell.rxn_output.status = ""

        return {'FINISHED'}


def check_rxn_output(self, context):
    """ Format reaction data output. """

    mcell = context.scene.mcell
    rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output = rxn_output_list[
        mcell.rxn_output.active_rxn_output_index]
    molecule_name = rxn_output.molecule_name
    object_name = rxn_output.object_name
    region_name = rxn_output.region_name

    if not molecule_name:
        molecule_name = "N/A"
    if not object_name:
        object_name = "N/A"
    if not region_name:
        region_name = "N/A"

    # Use different formatting depending on where we are counting
    if rxn_output.count_location == 'World':
        rxn_output_name = "Count %s in World" % (molecule_name)
    elif rxn_output.count_location == 'Object':
        rxn_output_name = "Count %s in/on %s" % (
            molecule_name, object_name)
    elif rxn_output.count_location == 'Region':
        rxn_output_name = "Count %s in/on %s[%s]" % (
            molecule_name, object_name, region_name)

    # Only update reaction output if necessary to avoid infinite recursion
    if rxn_output.name != rxn_output_name:
        rxn_output.name = rxn_output_name

    status = ""

    # Check for duplicate reaction data
    rxn_output_keys = rxn_output_list.keys()
    if rxn_output_keys.count(rxn_output.name) > 1:
        status = "Duplicate reaction output: %s" % (rxn_output.name)

    mcell.rxn_output.status = status

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


def update_clamp_value(self, context):
    """ Store the clamp value as a float if it's legal or generate an error """

    mcell = context.scene.mcell
    surf_class = context.scene.mcell.surface_classes
    active_surf_class = mcell.surface_classes.surf_class_list[
        mcell.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    surf_class_type = surf_class_props.surf_class_type
    orient = surf_class_props.surf_class_orient
    molecule = surf_class_props.molecule
    clamp_value_str = surf_class_props.clamp_value_str

    (clamp_value, status) = check_val_str(clamp_value_str, 0, None)

    if status == "":
        surf_class_props.clamp_value = clamp_value
    else:
        status = status % ("clamp_value", clamp_value_str)
        surf_class_props.clamp_value_str = "%g" % (
            surf_class_props.clamp_value)

    surf_class_type = convert_surf_class_str(surf_class_type)
    orient = convert_orient_str(orient)

    if molecule:
        surf_class_props.name = "Molec.: %s   Orient.: %s   Type: %s" % (
            molecule, orient, surf_class_type)
    else:
        surf_class_props.name = "Molec.: NA   Orient.: %s   Type: %s" % (
            orient, surf_class_type)

    surf_class.surf_class_props_status = status

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
    """ Store the space step as a float if it's legal or create an error """

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
    """ Store the space step as a float if it's legal or create an error """

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
    """ Store the space step as a float if it's legal or create an error """

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
    """ Store the space step as a float if it's legal or create an error """

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
        status = status % ("diffusion_constant", diffusion_constant_str)
        mol.diffusion_constant_str = "%g" % (mol.diffusion_constant)

    mcell.molecules.status = status

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
        status = status % ("custom_time_step", custom_time_step_str)
        mol.custom_time_step_str = "%g" % (mol.custom_time_step)

    mcell.molecules.status = status

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
        status = status % ("custom_space_step", custom_space_step_str)
        mol.custom_space_step_str = "%g" % (mol.custom_space_step)

    mcell.molecules.status = status

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
        status = status % ("fwd_rate", fwd_rate_str)
        rxn.fwd_rate_str = "%g" % (rxn.fwd_rate)

    mcell.reactions.status = status

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
        status = status % ("bkwd_rate", bkwd_rate_str)
        rxn.bkwd_rate_str = "%g" % (rxn.bkwd_rate)

    mcell.reactions.status = status

    return
