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
This file contains the classes for CellBlender's Meshalyzer.

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
import mathutils

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_release
from . import cellblender_utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Meshalyzer Operators:


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
        mcell.meshalyzer.genus_string = ""
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
        
        mcell.meshalyzer.genus = 1 - ( (mcell.meshalyzer.vertices + mcell.meshalyzer.faces - mcell.meshalyzer.edges) / 2 )
        mcell.meshalyzer.genus_string = "      Genus = %d" % (mcell.meshalyzer.genus)

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


class MCELL_OT_gen_meshalyzer_report(bpy.types.Operator):
    bl_idname = "mcell.gen_meshalyzer_report"
    bl_label = "Analyze Geometric Properties of Multiple Meshes"
    bl_description = "Generate Analysis Report of Geometric Properties of Multiple Meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):

        mcell = context.scene.mcell
        objs = context.selected_objects

        mcell.meshalyzer.object_name = ''
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.watertight = ''
        mcell.meshalyzer.manifold = ''
        mcell.meshalyzer.normal_status = ''
        mcell.meshalyzer.area = 0
        mcell.meshalyzer.volume = 0
        mcell.meshalyzer.sav_ratio = 0

        if (len(objs) == 0):
            mcell.meshalyzer.status = 'Please Select One or More Mesh Objects'
            return {'FINISHED'}

        bpy.ops.text.new()
        report = bpy.data.texts['Text']
        report.name = 'mesh_analysis.txt'
        report.write("# Object  Surface Area  Volume\n")

        for obj in objs:

            mcell.meshalyzer.object_name = obj.name

            if not (obj.type == 'MESH'):
                mcell.meshalyzer.status = 'Selected Object Not a Mesh'
                return {'FINISHED'}

            t_mat = obj.matrix_world
            mesh=obj.data

            mcell.meshalyzer.vertices = len(mesh.vertices)
            mcell.meshalyzer.edges = len(mesh.edges)
            mcell.meshalyzer.faces = len(mesh.polygons)

            area = 0
            for f in mesh.polygons:
                if not (len(f.vertices) == 3):
                    mcell.meshalyzer.status = '***** Mesh Not Triangulated *****'
                    mcell.meshalyzer.watertight = 'Mesh Not Triangulated'
                    return {'FINISHED'}

                tv0 = mesh.vertices[f.vertices[0]].co * t_mat
                tv1 = mesh.vertices[f.vertices[1]].co * t_mat
                tv2 = mesh.vertices[f.vertices[2]].co * t_mat
                area = area + mathutils.geometry.area_tri(tv0,tv1,tv2)

            mcell.meshalyzer.area = area

            (edge_faces, edge_face_count) = make_efdict(mesh)

            is_closed = check_closed(edge_face_count)
            is_manifold = check_manifold(edge_face_count)
            is_orientable = check_orientable(mesh,edge_faces,edge_face_count)

            if is_orientable:
                mcell.meshalyzer.normal_status = 'Consistent Normals'
            else:
                mcell.meshalyzer.normal_status = 'Inconsistent Normals'

            if is_closed:
                mcell.meshalyzer.watertight = 'Watertight Mesh'
            else:
                mcell.meshalyzer.watertight = 'Non-watertight Mesh'

            if is_manifold:
                mcell.meshalyzer.manifold = 'Manifold Mesh'
            else:
                mcell.meshalyzer.manifold = 'Non-manifold Mesh'

            volume = 0
            if is_orientable and is_manifold and is_closed:
                volume = mesh_vol(mesh,t_mat)
                if volume >= 0:
                    mcell.meshalyzer.normal_status = 'Outward Facing Normals'
                else:
                    mcell.meshalyzer.normal_status = 'Inward Facing Normals'

            mcell.meshalyzer.volume = volume
            if (not volume == 0.0):
                mcell.meshalyzer.sav_ratio = area/volume

            report.write("%s %.9g %.9g\n" % (obj.name, mcell.meshalyzer.area, mcell.meshalyzer.volume))

        mcell.meshalyzer.status = ''
        return {'FINISHED'}


# Meshalyzer support functions


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


# Meshalyzer Panel Classes

class MCELL_PT_meshalyzer(bpy.types.Panel):
    bl_label = "CellBlender - Mesh Analysis"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "CellBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:

            row = layout.row()
            row.operator("mcell.meshalyzer", text="Analyze Mesh",
                icon='MESH_ICOSPHERE')
            row = layout.row()
            row.operator("mcell.gen_meshalyzer_report",
                text="Generate Analysis Report",icon="MESH_ICOSPHERE")

            if (mcell.meshalyzer.status != ""):
                row = layout.row()
                row.label(text=mcell.meshalyzer.status, icon='ERROR')
            row = layout.row()
            row.label(text="Object Name: %s" % (mcell.meshalyzer.object_name))
            row = layout.row()
            row.label(text="Vertices: %d" % (mcell.meshalyzer.vertices))
            row = layout.row()
            row.label(text="Edges: %d" % (mcell.meshalyzer.edges))
            row = layout.row()
            row.label(text="Faces: %d" % (mcell.meshalyzer.faces))
            row = layout.row()
            row.label(text="Surface Area: %.5g" % (mcell.meshalyzer.area))
            row = layout.row()
            if (mcell.meshalyzer.watertight == 'Watertight Mesh'):
              row.label(text="Volume: %.5g" % (mcell.meshalyzer.volume))
            else:
              row.label(text="Volume: approx: %.5g" % (mcell.meshalyzer.volume))
            row = layout.row()
            row.label(text="SA/V Ratio: %.5g" % (mcell.meshalyzer.sav_ratio))

            row = layout.row()
            row.label(text="Mesh Topology:")
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.watertight))
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.manifold))
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.normal_status))
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.genus_string))



# Meshalyzer Property Groups

class MCellMeshalyzerPropertyGroup(bpy.types.PropertyGroup):
    object_name = StringProperty(name="Object Name")
    vertices = IntProperty(name="Vertices", default=0)
    edges = IntProperty(name="Edges", default=0)
    faces = IntProperty(name="Faces", default=0)
    watertight = StringProperty(name="Watertight")
    manifold = StringProperty(name="Manifold")
    normal_status = StringProperty(name="Surface Normals")
    genus = IntProperty(name="Genus", default=0)
    genus_string = StringProperty(name="", default="")
    area = FloatProperty(name="Area", default=0)
    volume = FloatProperty(name="Volume", default=0)
    sav_ratio = FloatProperty(name="SA/V Ratio", default=0)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Meshalyzer Properties... no collections to remove." )

