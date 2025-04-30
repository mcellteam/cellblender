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


# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

# python imports
import re
import mathutils

from itertools import combinations
from time import perf_counter
import numpy as np
from numpy.typing import NDArray
from scipy.sparse.csgraph import connected_components, yen
from scipy.sparse import coo_array, csc_array, sparray
from statistics import median
import bmesh

# CellBlender imports
from . import parameter_system
from . import cellblender_release
from . import cellblender_utils


# Meshalyzer Operators:

# recursively flatten a list nested to any depth
# after completion of all recursion, returns a single flat list
def flatten(arr):
  if not arr:
    return arr
  if isinstance(arr[0], list):
    return flatten(arr[0]) + flatten(arr[1:])
  return arr[:1] + flatten(arr[1:])


class MCELL_OT_meshalyzer(bpy.types.Operator):
    bl_idname = "mcell.meshalyzer"
    bl_label = "Analyze Geometric Properties of Mesh"
    bl_description = "Analyze Geometric Properties of Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def count_components(self,context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = bpy.context.active_object
        mesh = obj.data

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Count total vertices and number of vertices contiguous with vertex 0
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh.vertices[0].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_linked()
        n_v_tot = len(mesh.vertices)
        n_v_sel = mesh.total_vert_sel
        bpy.ops.object.mode_set(mode='OBJECT')

        # Loop over disjoint components
        n_components = 1
        while (n_v_sel < n_v_tot):
            n_components += 1
            # make list of selected indices
            vl1 = [v.index for v in mesh.vertices if v.select == True]
            # make list of indices of remaining component(s)
            vl2 = [v.index for v in mesh.vertices if v.select == False]
            # Grow selection with vertices contiguous with first vertex of remainder
            mesh.vertices[vl2[0]].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_linked()

            # Count number of vertices now selected and loop again if necessary
            n_v_sel = mesh.total_vert_sel
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        return n_components


    def count_boundaries(self, context):
        obj = bpy.context.active_object
        mesh = obj.data

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False,
                                         use_boundary=True, use_multi_face=False,
                                         use_non_contiguous=False, use_verts=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        edges = [ tuple(e.vertices) for e in mesh.edges ]
        boundary_edge_indices = [ e.index for e in mesh.edges if e.select ]
        if not boundary_edge_indices:
            return 0, 0  # No boundary edges found

        n_boundary_edges = len(boundary_edge_indices)
        boundary_cycles = BoundaryCycles(edges, boundary_edge_indices)
        boundary_cycles.compute_boundary_cycles()

        n_cycles = len(boundary_cycles.boundary_cycles)  # Count the number of boundary cycles
        # Return the number of boundary cycles  
        return n_boundary_edges, n_cycles


    def execute(self, context):

        mcell = bpy.context.scene.mcell
        objs = bpy.context.selected_objects

        mcell.meshalyzer.object_name = ""
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.orphan_vertices = 0
        mcell.meshalyzer.orphan_edges = 0
        mcell.meshalyzer.dangling_edges = 0
        mcell.meshalyzer.pure = True
        mcell.meshalyzer.non_orientable = False
        mcell.meshalyzer.nonmanifold_vertices = 0
        mcell.meshalyzer.nonmanifold_edges = 0
        mcell.meshalyzer.boundary_edges = 0
        mcell.meshalyzer.boundary_cycles = 0
        mcell.meshalyzer.genus = 0
        mcell.meshalyzer.manifold = ""
        mcell.meshalyzer.disjoint_components = 1
        mcell.meshalyzer.subcomponents = 1
        mcell.meshalyzer.watertight_components = 0
        mcell.meshalyzer.normal_status = ""
        mcell.meshalyzer.area = 0
        mcell.meshalyzer.volume = 0
        mcell.meshalyzer.sav_invalid = False
        mcell.meshalyzer.sav_ratio = 0
        mcell.meshalyzer.status = ""

        if (len(objs) != 1):
            mcell.meshalyzer.status = "Please Select One Mesh Object"
            return {'FINISHED'}

        obj = objs[0]

        if (obj.type != 'MESH'):
            mcell.meshalyzer.status = "Please Select One Mesh Object"
            return {'FINISHED'}

        mesh = obj.data
       
        tmp = [None] * 3 * len(mesh.polygons) 
        try:
          mesh.polygons.foreach_get('vertices', tmp)
        except:
            mcell.meshalyzer.status = "***** Mesh Not Triangulated *****"
            return {'FINISHED'}


        checked_orientable = False
        while not mcell.meshalyzer.non_orientable:
          if bpy.context.mode != 'OBJECT':
              bpy.ops.object.mode_set(mode='OBJECT')
              bpy.ops.object.mode_set(mode='EDIT')
          ma = MeshAnalyzer(obj.data)
          mcell.meshalyzer.object_name = obj.name
          mcell.meshalyzer.vertices = ma.number_vertices
          mcell.meshalyzer.edges = ma.number_edges
          mcell.meshalyzer.faces = ma.number_simplices

          ma._orphan_vertices()
          ma._dangling_orphan_edges()
          mcell.meshalyzer.orphan_vertices = len(ma.orphan_vertices)
          mcell.meshalyzer.orphan_edges = len(ma.orphan_edges)
          mcell.meshalyzer.dangling_edges = len(ma.dangling_edges)
        
          if ma.orphan_vertices or ma.orphan_edges or ma.dangling_edges:
            mcell.meshalyzer.status = "***** Mesh Not Pure: Repair Required *****"
            mcell.meshalyzer.pure = False
            return {'FINISHED'}

          ma._disjoint_components()
          mcell.meshalyzer.disjoint_components = ma.number_disjoint_components
          ma._subcomponents()
          mcell.meshalyzer.subcomponents = sum(ma.number_subcomponents)

          ma._consistent_normals()
          mcell.meshalyzer.consistent_normals = all(flatten(ma.consistent_normals))

          if mcell.meshalyzer.consistent_normals:
            mcell.meshalyzer.normal_status = "Consistent Normals -> Orientable"
            if checked_orientable:
              mcell.meshalyzer.normal_status = "Consistent Normals, Recalculated -> Orientable"
            break
          else:
            if not checked_orientable:
              # Recalculate Normals Here:
              bpy.ops.object.mode_set(mode='EDIT')
              bpy.ops.mesh.select_mode(type='VERT')
              bpy.ops.mesh.reveal()
              bpy.ops.mesh.select_mode(type='FACE')
              bpy.ops.mesh.select_all(action='SELECT')
              bpy.ops.mesh.normals_make_consistent(inside=False)
              bpy.ops.mesh.select_all(action='DESELECT')
              bpy.ops.object.mode_set(mode='OBJECT')

              checked_orientable = True
            else:
              mcell.meshalyzer.non_orientable = True
              mcell.meshalyzer.normal_status = "Inconsistent Normals, Recalculated -> Non-Orientable"


        ma._nonmanifold_edges()
        mcell.meshalyzer.nonmanifold_edges = len(flatten(ma.nonmanifold_edges))

        ma._nonmanifold_vertices_volume()
        ma._boundary_edges()
        ma._boundary_cycles()
        nmv = set(flatten(ma.nonmanifold_vertices_volume) + flatten(ma.nonmanifold_vertices_surface))
        mcell.meshalyzer.nonmanifold_vertices = len(nmv)
        mcell.meshalyzer.boundary_edges = len(flatten(ma.boundary_edges))
        mcell.meshalyzer.boundary_cycles = sum(flatten(ma.number_boundary_cycles))
        ma._euler_characteristic()
        ma._genus()
        mcell.meshalyzer.genus = sum(flatten(ma.genus))

        ma._area()
        mcell.meshalyzer.area = sum(flatten(ma.area))
        ma._volume()
        fvol = flatten(ma.volume)
        mcell.meshalyzer.volume = sum([v for v in fvol if v is not None])
        mcell.meshalyzer.watertight_components = len(fvol) - fvol.count(None)
        sav = [v for v in flatten(ma.area_to_volume) if v is not None]
        if sav:
          mcell.meshalyzer.sav_ratio = median(sav)
        else:
          mcell.meshalyzer.sav_invalid = True




        return {'FINISHED'}


    def execute_orig(self, context):

        mcell = bpy.context.scene.mcell
        objs = bpy.context.selected_objects

        mcell.meshalyzer.object_name = ""
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.orphan_vertices = 0
        mcell.meshalyzer.nonmanifold_vertices = 0
        mcell.meshalyzer.nonmanifold_edges = 0
        mcell.meshalyzer.orphan_edges = 0
        mcell.meshalyzer.boundary_edges = 0
        mcell.meshalyzer.components = 0
        mcell.meshalyzer.genus = 0
        mcell.meshalyzer.manifold = ""
        mcell.meshalyzer.watertight = ""
        mcell.meshalyzer.boundaries = 0
        mcell.meshalyzer.normal_status = ""
        mcell.meshalyzer.components = 0
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
        
        
        mcell.meshalyzer.components = self.count_components(context)
        # mcell.meshalyzer.genus = int(mcell.meshalyzer.components - ( (mcell.meshalyzer.vertices - mcell.meshalyzer.edges + mcell.meshalyzer.faces)) / 2 )
        # mcell.meshalyzer.boundaries = 2 - 2*mcell.meshalyzer.genus - (mcell.meshalyzer.vertices - mcell.meshalyzer.edges + mcell.meshalyzer.faces)

        area = 0
        for f in mesh.polygons:
            if not (len(f.vertices) == 3):
                mcell.meshalyzer.status = "***** Mesh Not Triangulated *****"
                mcell.meshalyzer.watertight = "Mesh Not Triangulated"
                return {'FINISHED'}

            tv0 = mesh.vertices[f.vertices[0]].co @ t_mat
            tv1 = mesh.vertices[f.vertices[1]].co @ t_mat
            tv2 = mesh.vertices[f.vertices[2]].co @ t_mat
            area = area + mathutils.geometry.area_tri(tv0, tv1, tv2)

        mcell.meshalyzer.area = area

        (edge_faces, edge_face_count) = make_efdict(mesh)

        mcell.meshalyzer.orphan_vertices = count_orphan_vertices(edge_face_count)
        mcell.meshalyzer.nonmanifold_vertices = count_nonmanifold_vertices(edge_face_count)
        mcell.meshalyzer.nonmanifold_edges = count_nonmanifold_edges(edge_face_count)
        mcell.meshalyzer.orphan_edges = mcell.meshalyzer.edges - len(edge_face_count)
        mcell.meshalyzer.boundary_edges, mcell.meshalyzer.boundaries = self.count_boundaries(context)
        X = (mcell.meshalyzer.vertices - mcell.meshalyzer.edges + mcell.meshalyzer.faces)
        mcell.meshalyzer.genus = int((2*mcell.meshalyzer.components - mcell.meshalyzer.boundaries - X)/2)
  

        is_closed = check_closed(edge_face_count)
        is_manifold = check_manifold(edge_face_count) and (mcell.meshalyzer.orphan_vertices == 0) and (mcell.meshalyzer.nonmanifold_vertices == 0) and (mcell.meshalyzer.orphan_edges == 0)
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
        if is_orientable and is_closed:
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

        mcell = bpy.context.scene.mcell
        objs = bpy.context.selected_objects

        mcell.meshalyzer.object_name = ''
        mcell.meshalyzer.vertices = 0
        mcell.meshalyzer.edges = 0
        mcell.meshalyzer.faces = 0
        mcell.meshalyzer.orphan_vertices = 0
        mcell.meshalyzer.nonmanifold_vertices = 0
        mcell.meshalyzer.nonmanifold_edges = 0
        mcell.meshalyzer.orphan_edges = 0
        mcell.meshalyzer.boundary_edges = 0
        mcell.meshalyzer.components = 0
        mcell.meshalyzer.genus = 0
        mcell.meshalyzer.manifold = ''
        mcell.meshalyzer.watertight = ''
        mcell.meshalyzer.boundaries = 0
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

                tv0 = mesh.vertices[f.vertices[0]].co @ t_mat
                tv1 = mesh.vertices[f.vertices[1]].co @ t_mat
                tv2 = mesh.vertices[f.vertices[2]].co @ t_mat
                area = area + mathutils.geometry.area_tri(tv0,tv1,tv2)

            mcell.meshalyzer.area = area

            (edge_faces, edge_face_count) = make_efdict(mesh)

            mcell.meshalyzer.orphan_vertices = count_orphan_vertices(edge_face_count)
            mcell.meshalyzer.nonmanifold_vertices = count_nonmanifold_vertices(edge_face_count)
            mcell.meshalyzer.orphan_edges = mcell.meshalyzer.edges - len(edge_face_count)
            mcell.meshalyzer.boundary_edges = count_boundary_edges(edge_face_count)
            is_closed = check_closed(edge_face_count)
            is_manifold = check_manifold(edge_face_count) and (mcell.meshalyzer.orphan_vertices == 0) and (mcell.meshalyzer.nonmanifold_vertices == 0) and (mcell.meshalyzer.orphan_edges == 0)
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


# Meshalyzer support classes and functions

Matrix_NExNV = NDArray[np.int64]
Matrix_NVxNV = NDArray[np.int64]
Matrix_NxM = NDArray[np.int64]
SMatrix_NExNV = sparray  # dtype: np.int64
SMatrix_NSxNE = sparray  # dtype: np.int64

class BoundaryCycles:

    '''
    Class to compute boundary cycles of a surface mesh, even if some of those cycles meet at a single vertex,
    which makes the surface non-manifold. Cycles are not traversed with respect to a specific orientation.
    '''

    def __init__(self, edges: list[tuple[int, int]],
                 boundary_edge_indices: list[int]) -> None:

        self.edges = edges
        self.boundary_edge_indices = boundary_edge_indices
        self.boundary_edges = np.array(self.edges)[self.boundary_edge_indices]
        self.number_of_boundary_edges = self.boundary_edges.shape[0]
        self.boundary_vertices = np.unique(self.boundary_edges)
        self.number_of_boundary_vertices = self.boundary_vertices.shape[0]

        # instance variables to be computed
        self._boundary_vertex_degree: NDArray[np.int64] | None = None
        self._boundary_edges: list[tuple[int, int]] | None = None
        self._incidence_edge_vertex: Matrix_NExNV | None = None
        self._adjacency_vertex: Matrix_NVxNV | None = None
        self.vertices_singular: list[int] | None = None
        self.boundary_cycles_non_touching: list[tuple[int, int]] | None = None
        self.boundary_cycles_touching: list[tuple[int, int]] | None = None
        self.boundary_cycles: list[list[int]] | None = None

        self.compute_boundary_cycles()


    def incidence_edge_vertex(self) -> None:

        self._incidence_edge_vertex = np.zeros((self.number_of_boundary_edges,
                                                self.number_of_boundary_vertices),
                                               dtype=np.int64)
        for i, (j, k) in enumerate(self._boundary_edges):
            self._incidence_edge_vertex[i, j] = 1
            self._incidence_edge_vertex[i, k] = 1


    def adjacency_vertex(self) -> None:

        self._adjacency_vertex = (self._incidence_edge_vertex.T
                                  @ self._incidence_edge_vertex
                                  - np.diag(self._boundary_vertex_degree))


    def vertex_degree(self, vertex: int) -> int:
        # vertex: internal vertex index

        return np.count_nonzero(self._incidence_edge_vertex[:, vertex])


    def vertex_edges(self, vertex: int) -> list[int]:
        # edges emanating from vertex
        # vertex: internal vertex index

        return np.nonzero(self._incidence_edge_vertex[:, vertex])[0].tolist()


    def vertex_next(self, edge: int, vertex: int) -> int:
        # next vertex on the edge for a given vertex on that edge
        # edge: internal edge index
        # vertex: internal vertex index

        return np.setdiff1d(self._boundary_edges[edge], vertex).item()


    def edge_next(self, edge: int, vertex: int) -> int:
        # edges emanating from the vertex on the edge except itself
        # edge: internal edge index
        # vertex: internal vertex index

        edges = np.nonzero(self._incidence_edge_vertex[:, vertex])[0]
        return np.setdiff1d(edges, edge).item()


    def path(self, predecessors: NDArray[np.int64]) -> list[tuple[int, int]]:

        current = np.where(predecessors != -9999)[0]
        previous = predecessors[current]

        return [tuple(sorted((pre.item(), cur.item())))
                for pre, cur in zip(previous, current)]


    def order_singular_vertices(self, booleans: NDArray[np.bool_]) -> list[int]:

        tmp_0 = np.where(booleans)[0]
        tmp_1 = np.argsort(self._boundary_vertex_degree[booleans])
        tmp = tmp_0[tmp_1][::-1]

        return tmp.tolist()


    def compute_non_touching_boundary_cycles(self, vertices: list[int]) -> list[int]:

        cycle = []
        for vertex in vertices:
            cycle.extend(self.vertex_edges(vertex))
        cycle = list(set(cycle))

        return cycle


    def compute_touching_boundary_cycles(self, vertices: list[int]) -> list[list[int]]:

        vertex_singular = vertices[:]
        visited_edges = []
        cycles = []

        while vertex_singular:
            pivot_vertex = vertex_singular.pop()
            current_vertex = pivot_vertex
            edges = self.vertex_edges(current_vertex)

            while edges:
                current_vertex = pivot_vertex
                current_edge = edges.pop()
                if current_edge in visited_edges:
                    continue

                _visited_edges = [current_edge]
                previous_vertex = current_vertex
                current_vertex = self.vertex_next(current_edge, previous_vertex)

                while current_vertex not in vertices:
                    current_edge = self.edge_next(current_edge, current_vertex)
                    _visited_edges.append(current_edge)
                    previous_vertex = current_vertex
                    current_vertex = self.vertex_next(current_edge, previous_vertex)

                if current_vertex == pivot_vertex:
                    cycle = _visited_edges
                else:
                    _, predecessors = yen(self._adjacency_vertex,
                                          pivot_vertex, current_vertex, 2,
                                          directed=False,
                                          return_predecessors=True)
                    _cycle = self.path(predecessors[0]) + self.path(predecessors[1])
                    cycle = [self._boundary_edges.index(edge) for edge in _cycle]

                visited_edges.extend(cycle)
                cycles.append(cycle)

        return cycles


    def compute_boundary_cycles(self) -> None:

        boundary_vertex_dict = {v: i for i, v in enumerate(self.boundary_vertices)}

        self._boundary_edges = [(boundary_vertex_dict[i], boundary_vertex_dict[j])
                                for i, j in self.boundary_edges]

        self.incidence_edge_vertex()

        self._boundary_vertex_degree = np.apply_along_axis(np.count_nonzero,
                                                           axis=0,
                                                           arr=self._incidence_edge_vertex)

        self.adjacency_vertex()

        _, labels = connected_components(self._adjacency_vertex, directed=False)

        labels_singular = np.unique(labels[self._boundary_vertex_degree > 2])
        labels_non_singular = np.setdiff1d(np.unique(labels), labels_singular)

        vertices_non_singular = [np.where(labels == i)[0] for i in labels_non_singular]
        boundary_cycles_non_touching = [self.compute_non_touching_boundary_cycles(vertex)
                                        for vertex in vertices_non_singular]
        self.boundary_cycles_non_touching = [[self.boundary_edge_indices[idx] for idx in cycle]
                                             for cycle in boundary_cycles_non_touching]

        vertices_singular_boolean = [np.logical_and(labels == label,
                                                    self._boundary_vertex_degree > 2)
                                     for label in labels_singular]
        vertices_singular_ordered = [self.order_singular_vertices(booleans)
                                     for booleans in vertices_singular_boolean]
        self.vertices_singular = [self.boundary_vertices[vertex].item()
                                  for vertices in vertices_singular_ordered
                                  for vertex in vertices]
        boundary_cycles_touching = []
        for vertices in vertices_singular_ordered:
            boundary_cycles_touching.extend(self.compute_touching_boundary_cycles(vertices))
        self.boundary_cycles_touching = [[self.boundary_edge_indices[idx] for idx in cycle]
                                         for cycle in boundary_cycles_touching]

        self.boundary_cycles = (self.boundary_cycles_non_touching
                                + self.boundary_cycles_touching)


class MeshAnalyzer:
    '''
    Class to analyze meshes in Blender.
    '''

    def __init__(self, mesh: bpy.types.Mesh) -> None:
        self.mesh = mesh
        self.number_simplices: int = len(mesh.polygons)
        self.number_vertices: int = len(mesh.vertices)
        self.number_edges: int = len(mesh.edges)

        # instance variables to be computed
        self.simplex_indices: list[int] | None = None
        self.edge_indices: list[int] | None = None
        self.edge_vertices: tuple[list[int]] | None = None
        self.incidence_edge_vertex: SMatrix_NExNV | None = None
        self.incidence_simplex_edge: SMatrix_NSxNE | None = None
        self.orphan_vertices: list[int] | None = None
        self.dangling_edges: list[int] | None = None
        self.orphan_edges: list[int] | None = None
        self.number_disjoint_components: int | None = None
        self.disjoint_components: list[NDArray[np.bool_]] | None = None
        self.simplex_index_disjoint_components: list[NDArray[np.int64]] | None = None
        self.incidence_simplex_edge_disjoint_components: list[SMatrix_NSxNE] | None = None
        self.nonanifold_edges: list[list[int]] | None = None
        self.number_subcomponents: list[int] | None = None
        self.subcomponents: list[list[NDArray[np.bool_]]] | None = None
        self.nonmanifold_vertices_volume: list[list[int]] | None = None
        self.consistent_normals: list[list[bool] | bool] | None = None
        self.boundary_edges: list[list[list[int]] | int] | None = None
        self.boundary_cycle_instances: list[list[BoundaryCycles] | None] | None = None
        self.boundary_cycles: list[list[list[list[int] | int]]] | None = None
        self.number_boundary_cycles: list[list[int]] | None = None
        self.nonmanifold_vertices_surface: list[list[list[int]]] | None = None
        self.euler_characteristic: list[list[int]] | None = None
        self.genus: list[list[int] | int] | None = None
        self.area: list[list[float]] | None = None
        self.volume: list[list[float | None]] | None = None
        self.area_to_volume: list[list[float | None] | None] | None = None

        self._incidence_edge_vertex()
        self._incidence_simplex_edge()


    def _incidence_edge_vertex(self) -> None:
        '''
        Computes the incidence matrix of edges and vertices.
        The incidence matrix is a sparse matrix that represents the oriented
        incidence relation between edges and vertices. The incidence matrix is
        defined as follows:

        incidence_edge_vertex[i, j] = 1 if edge i leaves vertex j,
                                     -1 if edge i enters vertex j,
                                      0 otherwise.
        '''

        t = perf_counter()

        self.edge_indices = [None] * self.number_edges
        self.mesh.edges.foreach_get('index', self.edge_indices)

        # The vertex indices normally follow ascending order for each edge.
        # However, some of them may happen to be reordered reverse if the mesh
        # is manipulated, e.g. (17, 4) instead of (4, 17). This is possibly a bug
        # in Blender. This does not happen if you get edge keys from polygons.
        # Therefore, we fix it as follows:

        self.edge_vertices = [None] * 2 * self.number_edges
        self.mesh.edges.foreach_get('vertices', self.edge_vertices)

        v0, v1 = np.array(self.edge_vertices[::2]), np.array(self.edge_vertices[1::2])
        b = v0 < v1
        self.edge_vertices = (np.where(b, v0, v1).tolist(), np.where(b, v1, v0).tolist())


        self.incidence_edge_vertex = coo_array(([-1] * self.number_edges + [1] * self.number_edges,
                                                (self.edge_indices * 2,
                                                 self.edge_vertices[0] + self.edge_vertices[1])),
                                               shape=(self.number_edges, self.number_vertices),
                                               dtype=np.int64)
        self.incidence_edge_vertex = self.incidence_edge_vertex.tocsc()

        #print(f'\n iev: {perf_counter() - t:.3f} s')


    def _incidence_simplex_edge(self) -> None:
        '''
        Computes the incidence matrix of simplices and edges.
        The incidence matrix is a sparse matrix that represents the oriented
        incidence relation between simplices and edges. The incidence matrix
        is defined as follows:

        incidence_simplex_edge[i, j] = 1 if simplex i traverses edge j in the same direction,
                                      -1 if simplex i traverses edge j in the opposite direction,
                                       0 otherwise.
        '''

        t = perf_counter()

        edg_dic = dict(zip(zip(self.edge_vertices[0], self.edge_vertices[1]), self.edge_indices))

        self.ver_idx = [None] * 3 * self.number_simplices
        self.mesh.polygons.foreach_get('vertices', self.ver_idx)

        self.simplex_indices = [None] * self.number_simplices
        self.mesh.polygons.foreach_get('index', self.simplex_indices)

        edg_tra = lambda i, j: ((edg_dic[self.ver_idx[i], self.ver_idx[j]], 1)
                                if self.ver_idx[i] < self.ver_idx[j]
                                else (edg_dic[self.ver_idx[j], self.ver_idx[i]], -1))

        self.incidence_simplex_edge = []
        for i in range(self.number_simplices):
            i0, i1, i2 = i * 3, i * 3 + 1, i * 3 + 2
            self.incidence_simplex_edge.append((*edg_tra(i0, i1),
                                                *edg_tra(i1, i2),
                                                *edg_tra(i2, i0)))
        self.incidence_simplex_edge = list(zip(*self.incidence_simplex_edge))

        self.incidence_simplex_edge = coo_array((self.incidence_simplex_edge[1]
                                                 + self.incidence_simplex_edge[3]
                                                 + self.incidence_simplex_edge[5],
                                                 (self.simplex_indices * 3,
                                                  self.incidence_simplex_edge[0]
                                                  + self.incidence_simplex_edge[2]
                                                  + self.incidence_simplex_edge[4])),
                                                shape=(self.number_simplices, self.number_edges),
                                                dtype=np.int64)
        self.incidence_simplex_edge = self.incidence_simplex_edge.tocsc()

        #print(f'\n ise: {perf_counter() - t:.3f} s')


    def _orphan_vertices(self) -> None:
        '''
        Computes a list of orphan vertices.
        Orphan vertices are those that are not connected to any other vertices.
        '''

        t = perf_counter()

        self.orphan_vertices =  np.where(self.incidence_edge_vertex.count_nonzero(0) == 0)[0].tolist()

        #print(f'\n ov: {perf_counter() - t:.3f} s')


    def _dangling_orphan_edges(self) -> None:
        '''
        Computes a list of dangling and orphan edges.
        Dangling edges are those that are not shared by any faces.
        Oprhan edges are those that are not connected to any other edges.
        '''

        t = perf_counter()

        self.dangling_edges = []
        self.orphan_edges = []
        no_sim_edg = np.where(self.incidence_simplex_edge.count_nonzero(0) == 0)[0]

        for edge in no_sim_edg:
            i, j = self.incidence_edge_vertex.tocsr()[edge].nonzero()[0]
            tmp = (self.incidence_edge_vertex[:, i].count_nonzero() == 1
                   and self.incidence_edge_vertex[:, j].count_nonzero() == 1)
            if not tmp:
                self.dangling_edges.append(edge.item())
            else:
                self.orphan_edges.append(edge.item())

        #print(f'\n doe: {perf_counter() - t:.3f} s')


    def _disjoint_components(self) -> None:
        '''
        Computes disjoint components in the mesh as well as related quantities.
        Each component is represented by a boolean array.

        '''

        t = perf_counter()

        eet = self.incidence_edge_vertex @ self.incidence_edge_vertex.T
        self.number_disjoint_components, labels = connected_components(eet, directed=False)
        if self.number_disjoint_components == 1:
            self.disjoint_components = []
            self.simplex_index_disjoint_components = []
            self.incidence_simplex_edge_disjoint_components = []
        else:
            # 0.3759135000873357 sec for astrocyte
            self.disjoint_components = [labels == i for i in range(self.number_disjoint_components)]

            inc_sim_edg = [self.incidence_simplex_edge[:, self.disjoint_components[i]].copy()
                           for i in range(self.number_disjoint_components)]
            self.simplex_index_disjoint_components = [np.unique(inc_sim_edg[i].nonzero()[0])
                                                      for i in range(self.number_disjoint_components)]
            self.incidence_simplex_edge_disjoint_components = [inc_sim_edg[i].tocsr()[self.simplex_index_disjoint_components[i]].tocsc()
                                                               for i in range(self.number_disjoint_components)]
            # 0.38218312500976026 sec for astrocyte
#            self.disjoint_components = []
#            self.simplex_index_disjoint_components = []
#            self.incidence_simplex_edge_disjoint_components = []
#            for i in range(self.number_disjoint_components):
#                self.disjoint_components.append(labels == i)
#                inc_sim_edg = self.incidence_simplex_edge[:, self.disjoint_components[-1]].copy()
#                self.simplex_index_disjoint_components.append(np.unique(inc_sim_edg.nonzero()[0]))
#                self.incidence_simplex_edge_disjoint_components.append(inc_sim_edg.tocsr()[self.simplex_index_disjoint_components[-1]].tocsc())

        #print(f'\n dc: {perf_counter() - t:.3f}')


    def _nonmanifold_edges(self) -> None:
        '''
        Computes a list of nonmanifold edge indices of (the disjoint components) of a mesh.
        Nonmanifold edges are those that are shared by more than two faces.
        The edge indices are in the global mesh index space.
        '''

        t = perf_counter()

        if self.number_disjoint_components == 1:
            self.nonmanifold_edges = [np.where(self.incidence_simplex_edge.count_nonzero(0) > 2)[0].tolist()]

        else:
            self.nonmanifold_edges = [np.where(self.disjoint_components[i])[0][self.incidence_simplex_edge_disjoint_components[i].count_nonzero(0) > 2].tolist()
                                      for i in range(self.number_disjoint_components)]

        #print(f'\n ne: {perf_counter() - t:.3f} s')


    def _subcomponents(self) -> None:
        '''
        Computes the connected (possibly nonmanifold) subcomponents of
        (the disjoint components of) a mesh connected by nonmanifold edges or vertices.

        Each component may have boundary cycles and some of them may meet at a
        single vertex. This makes it a singular vertex such that the neighborhood
        thereof cannot be mapped into a single open half disk. In such a case,
        this component is assumed to be able to be resolved into a manifold mesh
        by fattening the singular vertex out through adding new simplices and a local
        retriangulation so that the number of boundary cycles is preserved.
        In this way, it can be shown that the intrepretation of the Euler characteristic
        in terms of genus and boundary cycles still applies.

        Being a nonmanifold due to having a single vertex at which two more meshes meet
        is automatically taken care of by the adjacency matrix built upon a simplex-edge
        incidence matrix.

        However, the case where two or more meshes coincide on a single edge needs to be taken
        care of explicitly. This is done by setting the corresponding entries in the
        incidence matrix to zero.
        '''

        t = perf_counter()

        self.number_subcomponents = []
        self.subcomponents = []

        for i in range(self.number_disjoint_components):
            if self.number_disjoint_components != 1:
                inc_sim_edg = self.incidence_simplex_edge_disjoint_components[i]
            else:
                inc_sim_edg = self.incidence_simplex_edge

            nonmanifold_edges = inc_sim_edg.count_nonzero(0) > 2
            if nonmanifold_edges.any():
                inc_sim_edg = inc_sim_edg.tolil(copy=True)
                inc_sim_edg[:, nonmanifold_edges] = 0

            sst = inc_sim_edg @ inc_sim_edg.T

            n_subcomponents, labels = connected_components(sst, directed=False)
            self.number_subcomponents.append(n_subcomponents)
            if n_subcomponents == 1:
                self.subcomponents.append([])
            else:
                subcomponents = [labels == i for i in range(n_subcomponents)]
                self.subcomponents.append(subcomponents)

        #print(f'\n sc: {perf_counter() - t:.3f} s')


    def _nonmanifold_vertices_volume(self) -> None:
        '''
        Computes a list of nonmanifold vertices that are share by two or more
        subcomponents. Nonmanifold vertices are those that are shared by more
        than one neighborhood (open half/full disk). The computed list does not
        include the vertices at which two or more boundary cycles meet, which
        are computed by BoundaryCycle class.
        '''

        t = perf_counter()

        self.nonmanifold_vertices_volume = []
        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                self.nonmanifold_vertices_volume.append([])
            else:
                if self.number_disjoint_components != 1:
                    simplex_index = self.simplex_index_disjoint_components[i]
                else:
                    simplex_index = np.array(self.simplex_indices)
                simplex_components = [simplex_index[subcomponent]
                                      for subcomponent in self.subcomponents[i]]
                component_vertices = [set(v for _idx in idx for v in self.mesh.polygons[_idx].vertices)
                                      for idx in simplex_components]

                nonmanifold_vertices = set()
                for j, k in combinations(range(len(component_vertices)), 2):
                    nonmanifold_vertices.update(component_vertices[j].intersection(component_vertices[k]))

                nonmanifold_edges = self.nonmanifold_edges[i]
                if nonmanifold_edges:
                    nonmanifold_edge_vertices = [self.mesh.edges[edge].vertices[:]
                                                 for edge in nonmanifold_edges]
                    nonmanifold_edge_vertices_set = set(v for edge in nonmanifold_edge_vertices
                                                        for v in edge)

                    for i, j in nonmanifold_edge_vertices:
                        for vertices in component_vertices:
                            bi, bj = (i in vertices), (j in vertices)
                            if bi ^ bj:
                                if bi:
                                    nonmanifold_edge_vertices_set.difference_update({i})
                                else:
                                    nonmanifold_edge_vertices_set.difference_update({j})

                    nonmanifold_vertices.difference_update(nonmanifold_edge_vertices_set)

                self.nonmanifold_vertices_volume.append(list(nonmanifold_vertices))

        #print(f'\n nv: {perf_counter() - t:.3f} s')


    def _consistent_normals(self) -> None:
        '''
        Computes True if (the disjoint components or the subcomponents or the
        subcomponents of the disjoint components of) a mesh have consistent
        normals, False otherwise. A consistent normal orientation is one that has
        a consistent orientation for all faces.
        '''

        t = perf_counter()

        self.consistent_normals = []

        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                if self.number_disjoint_components != 1:
                    boolean = self.incidence_simplex_edge_disjoint_components[i].count_nonzero(0) != 1
                    self.consistent_normals.append(np.all(self.incidence_simplex_edge_disjoint_components[i][:, boolean].sum(0) == 0).item())
                else:
                    boolean = self.incidence_simplex_edge.count_nonzero(0) != 1
                    self.consistent_normals.append(np.all(self.incidence_simplex_edge[:, boolean].sum(0) == 0).item())
            else:
                subcomponents = self.subcomponents[i]
                n = self.number_subcomponents[i]
                if self.number_disjoint_components != 1:
                    inc_sim_edg = self.incidence_simplex_edge_disjoint_components[i]
                else:
                    inc_sim_edg = self.incidence_simplex_edge
                consistent_normals = [np.all(inc_sim_edg[:, inc_sim_edg.count_nonzero(0) != 1].tocsr()[subcomponents[j]].sum(0) == 0).item()
                                      for j in range(n)]
                self.consistent_normals.append(consistent_normals)

        #print(f'\n cn: {perf_counter() - t:.3f} s')


    def _boundary_edges(self) -> None:
        '''
        Computes the boundary edges of (the disjoint components or the subcomponents
        or th subcomponents of the disjoint components of) a mesh.
        '''

        t = perf_counter()

        self.boundary_edges = []

        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                if self.number_disjoint_components != 1:
                    boolean = self.incidence_simplex_edge_disjoint_components[i].count_nonzero(0) == 1
                    boundary_edges = np.where(self.disjoint_components[i])[0][boolean].tolist()
                    self.boundary_edges.append(boundary_edges)
                else:
                    self.boundary_edges.append(np.where(self.incidence_simplex_edge.count_nonzero(0) == 1)[0].tolist())
            else:
                subcomponents = self.subcomponents[i]
                n = self.number_subcomponents[i]
                if self.number_disjoint_components != 1:
                    inc_sim_edg = self.incidence_simplex_edge_disjoint_components[i]
                    boundary_edges = [np.where(self.disjoint_components[i])[0][inc_sim_edg.tocsr()[subcomponents[j]].count_nonzero(0) == 1].tolist()
                                      for j in range(n)]
                else:
                    inc_sim_edg = self.incidence_simplex_edge
                    boundary_edges = [np.where(inc_sim_edg.tocsr()[subcomponents[j]].count_nonzero(0) == 1)[0].tolist()
                                      for j in range(n)]
                self.boundary_edges.append(boundary_edges)

        #print(f'\n be: {perf_counter() - t:.3f} s')


    def _boundary_cycles(self) -> None:
        '''
        Computes the boundary cycles of (the disjoint components or the subcomponents
        or th subcomponents of the disjoint components of) a mesh.
        '''

        t = perf_counter()

        self.boundary_cycle_instances = []
        self.boundary_cycles = []
        self.number_boundary_cycles = []
        self.nonmanifold_vertices_surface = []

        edg_ver = list(zip(self.edge_vertices[0], self.edge_vertices[1]))

        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                if self.boundary_edges[i]:
                    self.boundary_cycle_instances.append(BoundaryCycles(edg_ver, self.boundary_edges[i]))
                    self.boundary_cycles.append(self.boundary_cycle_instances[-1].boundary_cycles)
                    self.number_boundary_cycles.append(len(self.boundary_cycles[-1]))
                    self.nonmanifold_vertices_surface.append(self.boundary_cycle_instances[-1].vertices_singular)
                else:
                    self.boundary_cycle_instances.append(None)
                    self.boundary_cycles.append([])
                    self.number_boundary_cycles.append(0)
                    self.nonmanifold_vertices_surface.append([])
            else:
                n = self.number_subcomponents[i]
                self.boundary_cycle_instances.append([BoundaryCycles(edg_ver, self.boundary_edges[i][j])
                                                      if self.boundary_edges[i][j] else None
                                                      for j in range(n)])
                self.boundary_cycles.append([bci.boundary_cycles
                                             if bci is not None else []
                                             for bci in self.boundary_cycle_instances[i]])
                self.number_boundary_cycles.append([len(bc) for bc in self.boundary_cycles[i]])
                self.nonmanifold_vertices_surface.append([bci.vertices_singular
                                                          if bci is not None else []
                                                          for bci in self.boundary_cycle_instances[i]])

#                bou_cyc_ins, bou_cyc, num_bou_cyc, non_ver_sur = [], [], [], []
#                for j in range(n):
#                    bou_cyc_ins.append(BoundaryCycles(edg_ver, self.boundary_edges[i][j]) if self.boundary_edges[i][j] else None)
#                    bou_cyc.append(bou_cyc_ins[-1].boundary_cycles if bou_cyc_ins[-1] is not None else [])
#                    num_bou_cyc.append(len(bou_cyc[-1]))
#                    non_ver_sur.append(bou_cyc_ins[-1].vertices_singular if bou_cyc_ins[-1] is not None else [])
#                self.boundary_cycle_instances.append(bou_cyc_ins)
#                self.boundary_cycles.append(bou_cyc)
#                self.number_boundary_cycles.append(num_bou_cyc)
#                self.nonmanifold_vertices_surface.append(non_ver_sur)

        #print(f'\n bc: {perf_counter() - t:.3f} s')


    def _euler_characteristic(self) -> None:
        '''
        Computes the Euler characteristic of (the disjoint components or the subcomponents
        or the subcomponents of the disjoint components of) a mesh.
        '''

        t = perf_counter()

        self.euler_characteristic = []
        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                if self.number_disjoint_components != 1:
                    E = np.where(self.disjoint_components[i])[0].size
                    V = np.unique(self.incidence_edge_vertex.tocsr()[self.disjoint_components[i]].nonzero()[1]).size
                    F = self.simplex_index_disjoint_components[i].size
                    self.euler_characteristic.append(V - E + F)
                else:
                    self.euler_characteristic.append(self.number_vertices - self.number_edges + self.number_simplices)
            else:
                subcomponents = self.subcomponents[i]
                n = self.number_subcomponents[i]
                V, E, F = [], [], []
                if self.number_disjoint_components != 1:
                    for j in range(n):
                        _F = self.incidence_simplex_edge_disjoint_components[i].tocsr()[subcomponents[j]]
                        F.append(_F.shape[0])
                        _E = np.unique(_F.nonzero()[1])
                        E.append(_E.size)
                        V.append(np.unique(self.incidence_edge_vertex.tocsr()[np.where(self.disjoint_components[i])[0][_E]].nonzero()[1]).size)
                else:
                    for j in range(n):
                        F.append(np.where(subcomponents[j])[0].size)
                        _E = np.unique(self.incidence_simplex_edge.tocsr()[subcomponents[j]].nonzero()[1])
                        E.append(_E.size)
                        V.append(np.unique(self.incidence_edge_vertex.tocsr()[_E].nonzero()[1]).size)
                self.euler_characteristic.append([_V - _E + _F for _V, _E, _F in zip(V, E, F)])

        #print(f'\n ec: {perf_counter() - t:.3f} s')


    def _gen(self, eul_cha: int, num_bou: int, orientable: bool = True) -> float:
        '''
        Returns the genus for a given Euler characteristic and the number of
        boundary cycles of an (non-)orientable surface mesh.
        '''

        if orientable:
            g = 1 - (eul_cha + num_bou) / 2
            if (g % 1.0) == 0.0:
                return int(g)
            else:
                raise ValueError('genus should be integer!')
        else:
            return 2 - (eul_cha + num_bou)


    def _genus(self) -> None:

        '''
        Computes the genus of (the disjoint components or the subcomponents
        or the subcomponents of the disjoint components of) a mesh.
        '''

        t = perf_counter()

        self.genus = []

        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                self.genus.append(self._gen(self.euler_characteristic[i],
                                            self.number_boundary_cycles[i],
                                            orientable=self.consistent_normals[i]))
            else:
                self.genus.append([self._gen(self.euler_characteristic[i][j],
                                             self.number_boundary_cycles[i][j],
                                             orientable=self.consistent_normals[i][j])
                                   for j in range(self.number_subcomponents[i])])

        #print(f'\n g: {perf_counter() - t:.3f} s')


    def _area(self) -> None:
        '''
        Computes the area of (the disjoint componens or the subcomponents
        or the subcomponents of the disjoint components of) a mesh.
        '''

        t = perf_counter()

        area = [0.0] * self.number_simplices
        self.mesh.polygons.foreach_get('area', area)
        area = np.array(area)

        self.area = []

        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                if self.number_disjoint_components != 1:
                    self.area.append(area[self.simplex_index_disjoint_components[i]].sum().item())
                else:
                    self.area.append(area.sum().item())
            else:
                subcomponents = self.subcomponents[i]
                n = self.number_subcomponents[i]
                if self.number_disjoint_components != 1:
                    self.area.append([area[self.simplex_index_disjoint_components[i][subcomponents[j]]].sum().item()
                                      for j in range(n)])
                else:
                    self.area.append([area[np.where(subcomponents[j])[0]].sum().item()
                                      for j in range(n)])

        #print(f'\n a: {perf_counter() - t:.3f} s')


    def _vol(self, sim_ver: Matrix_NxM) -> float:
        '''
        Returns the signed volume of the tets constructed by the vertices
        (v0, v1, v2) of the simplices of a mesh, given by sim_ver, with respect
        to the origin.
        '''

        lam = lambda args: np.linalg.det((self.mesh.vertices[args[0]].co,
                                          self.mesh.vertices[args[1]].co,
                                          self.mesh.vertices[args[2]].co))

        return 1 / 6 * np.apply_along_axis(lam, 1, sim_ver).sum().item()


    def _volume(self) -> None:
        '''
        Returns the volume of (the disjoint components or the subcomponents
        or the subcomponents of the disjoint components of) a mesh.
        '''

        t = perf_counter()

        ver = np.array(self.ver_idx).reshape(-1, 3)

        self.volume = []
        self.area_to_volume = []

        for i in range(self.number_disjoint_components):
            if self.number_subcomponents[i] == 1:
                if not self.boundary_edges[i]:
                    if self.number_disjoint_components != 1:
                        self.volume.append(self._vol(ver[self.simplex_index_disjoint_components[i]]))
                    else:
                        self.volume.append(self._vol(ver))
                    self.area_to_volume.append(self.area[i] / self.volume[i])
                else:
                    self.volume.append(None)
                    self.area_to_volume.append(None)
            else:
                subcomponents = self.subcomponents[i]
                n = self.number_subcomponents[i]
                if self.number_disjoint_components != 1:
                    self.volume.append([self._vol(ver[self.simplex_index_disjoint_components[i][subcomponents[j]]])
                                        if not self.boundary_edges[i][j] else None
                                        for j in range(n)])
                else:
                    self.volume.append([self._vol(ver[np.where(subcomponents[j])[0]])
                                        if not self.boundary_edges[i][j] else None
                                        for j in range(n)])
                self.area_to_volume.append([self.area[i][j] / self.volume[i][j]
                                            if self.volume[i][j] is not None else None
                                            for j in range(n)])

        #print(f'\n v: {perf_counter() - t:.3f} s')


def select_vertices(object: bpy.types.Object, vertices: list[int]) -> None:

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh = object.data
    bpy.context.view_layer.objects.active = object

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')

    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()

    for vertex in vertices:
        bm.verts[vertex].select = True


def select_edges(object: bpy.types.Object, edges: list[int]) -> None:

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh = object.data
    bpy.context.view_layer.objects.active = object

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='EDGE')

    bm = bmesh.from_edit_mesh(mesh)
    bm.edges.ensure_lookup_table()

    for edge in edges:
        bm.edges[edge].select = True


def select_faces(object: bpy.types.Object, faces: list[int]) -> None:

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh = object.data
    bpy.context.view_layer.objects.active = object

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')

    bm = bmesh.from_edit_mesh(mesh)
    bm.faces.ensure_lookup_table()

    for face in faces:
        bm.faces[face].select = True


def mesh_vol(mesh, t_mat):
    """Compute volume of triangulated, orientable, watertight, manifold mesh

    volume > 0 means outward facing normals
    volume < 0 means inward facing normals

    """

    volume = 0.0
    for f in mesh.polygons:
        tv0 = mesh.vertices[f.vertices[0]].co @ t_mat
        tv1 = mesh.vertices[f.vertices[1]].co @ t_mat
        tv2 = mesh.vertices[f.vertices[2]].co @ t_mat
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

    return volume


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
    """ Make sure the object is manifold -> edge_face_count always <= 2 """

    for ek in edge_face_count.keys():
        if edge_face_count[ek] > 2:
            return 0

    return 1


def count_nonmanifold_edges(edge_face_count):
    """ count number of edges with edge_face_count > 2 """
   
    n_nonmanifold_edges = len([ ek for ek in edge_face_count.keys() if edge_face_count[ek] > 2 ])

    return n_nonmanifold_edges



def check_closed(edge_face_count):
    """ Make sure the object is closed (no leaks) -> edge_face_count always == 2 """

    for ek in edge_face_count.keys():
        if not edge_face_count[ek] == 2:
            return 0

    return 1 


def count_orphan_vertices(edge_face_count):
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.active_object
    mesh = obj.data

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode='OBJECT')
    for e in mesh.edges:
        e.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    count = len([ v for v in mesh.vertices if v.select ])
    return count


def count_nonmanifold_vertices(edge_face_count):
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = bpy.context.active_object
    mesh = obj.data

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=True)

    bpy.ops.object.mode_set(mode='OBJECT')
    count = len([ v for v in mesh.vertices if v.select ])
    return count


# As written this code only checks for consistent normals.
#   It does not check whether the mesh is truly orientable.
#   To do that we would need to recalculate normals and check again.
#   We could add a button in the UI to recalculate and recheck for consistent
#   normals to determine true orientability.  If the normals are consistent
#   then we know it is orientable.  If orientable we calculate the genus 
#   using genus formula 1. In the case of non-orientable we calculate the genus
#   using genus formula 2.
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
                                return  0 
                            break

    return 1


# Meshalyzer Panel Classes

class MCELL_PT_meshalyzer(bpy.types.Panel):
    bl_label = "CellBlender - Mesh Analysis"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CellBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene
        mcell = bpy.context.scene.mcell

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
            row.label(text="Orphan Vertices: %d" % (mcell.meshalyzer.orphan_vertices))
            row = layout.row()
            row.label(text="Dangling Edges: %d" % (mcell.meshalyzer.dangling_edges))
            row = layout.row()
            row.label(text="Orphan Edges: %d" % (mcell.meshalyzer.orphan_edges))
            if mcell.meshalyzer.pure:
              row = layout.row()
              row.label(text="%s" % (mcell.meshalyzer.normal_status))
              row = layout.row()
              row.label(text="Disjoint Components = %d" % (mcell.meshalyzer.disjoint_components))
              row = layout.row()
              row.label(text="Subcomponents = %d" % (mcell.meshalyzer.subcomponents))
              row = layout.row()
              row.label(text="Watertight Components = %d" % (mcell.meshalyzer.watertight_components))
              row = layout.row()
              row.label(text="Non-manifold Edges: %d" % (mcell.meshalyzer.nonmanifold_edges))
              row = layout.row()
              row.label(text="Non-manifold Vertices: %d" % (mcell.meshalyzer.nonmanifold_vertices))
              row = layout.row()
              row.label(text="Boundary Edges: %d" % (mcell.meshalyzer.boundary_edges))
              row = layout.row()
              row.label(text="Boundary Cycles = %d" % (mcell.meshalyzer.boundary_cycles))
              row = layout.row()
              row.label(text="Genus = %d" % (mcell.meshalyzer.genus))
              row = layout.row()
              row.label(text="Surface Area: %.5g" % (mcell.meshalyzer.area))
              row = layout.row()
              row.label(text="Signed Volume: %.5g" % (mcell.meshalyzer.volume))
              row = layout.row()
              if not mcell.meshalyzer.sav_invalid:
                row.label(text="Median Signed SA/V Ratio: %.5g" % (mcell.meshalyzer.sav_ratio))
              else:
                row.label(text="Median Signed SA/V Ratio: N/A")



# Meshalyzer Property Groups

class MCellMeshalyzerPropertyGroup(bpy.types.PropertyGroup):
    object_name: StringProperty(name="Object Name")
    vertices: IntProperty(name="Vertices", default=0)
    edges: IntProperty(name="Edges", default=0)
    faces: IntProperty(name="Faces", default=0)
    orphan_vertices: IntProperty(name="Orphan Vertices", default=0)
    dangling_edges: IntProperty(name="Dangling Edges", default=0)
    orphan_edges: IntProperty(name="Orphan Edges", default=0)
    pure: BoolProperty(name="Pure Geometry", default=True)
    nonmanifold_vertices: IntProperty(name="Non-manifold Vertices", default=0)
    nonmanifold_edges: IntProperty(name="Non-manifold Edges", default=0)
    boundary_edges: IntProperty(name="Boundary Edges", default=0)
    boundary_cycles: IntProperty(name="Boundary Cycles", default=0)
    manifold: StringProperty(name="Manifold Mesh")
    watertight_components: IntProperty(name="Watertight Components", default=0)
    non_orientable: BoolProperty(name="Orientable", default=False)
    consistent_normals: BoolProperty(name="Consistent Normals", default=False)
    normal_status: StringProperty(name="Surface Normals")
    disjoint_components: IntProperty(name="Disjoint Components", default=1)
    subcomponents: IntProperty(name="Subcomponents", default=1)
    genus: IntProperty(name="Genus", default=0)
    area: FloatProperty(name="Area", default=0)
    volume: FloatProperty(name="Volume", default=0)
    sav_invalid: BoolProperty(name="SA/V Invalid", default=False)
    sav_ratio: FloatProperty(name="SA/V Ratio", default=0)
    status: StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Meshalyzer Properties... no collections to remove." )


classes = ( 
            MCELL_OT_meshalyzer,
            MCELL_OT_gen_meshalyzer_report,
            MCELL_PT_meshalyzer,
            MCellMeshalyzerPropertyGroup,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

