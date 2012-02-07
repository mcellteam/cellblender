# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
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

import bpy
import re
from . import mdlmesh_parser


def read(filepath):

  root_mdlobj = mdlmesh_parser.mdl_parser(filename)

  in_editmode = Blender.Window.EditMode()
  if in_editmode: Blender.Window.EditMode(0)

  scn = Blender.Scene.GetCurrent()
  default_mat = Blender.Material.New('default_material')
  default_mat.setRGBCol([0.7, 0.7, 0.7])
  region_mat = Blender.Material.New('region_material')
  region_mat.setRGBCol([0.8, 0.0, 0.0])

  mdlobj = root_mdlobj
  while not mdlobj == None:
    if mdlobj.object_type == 0:
      # META_OBJ
      p_mdlobj = mdlobj
      mdlobj = mdlobj.first_child
    else:
      # POLY_OBJ
      mesh = Blender.Mesh.New()
      mesh.verts.extend(mdlobj.vertices)
      mesh.faces.extend(mdlobj.faces)

      objname = mdlobj.name

      mesh.name = objname
      obj = scn.objects.new(mesh, objname)

      mesh.materials = [default_mat,region_mat]
      for f in mesh.faces:
        f.mat = 0
      for rkey, reg in mdlobj.regions.iteritems():
        mesh.addVertGroup(reg.name)
        vertlist=[]
        for f in reg.faces:          mesh.faces[f].mat = 1
          for v in mesh.faces[f].verts:
            vertlist.append(v.index)
        mesh.assignVertsToGroup(reg.name,vertlist,1.0,Blender.Mesh.AssignModes.A
DD)

      mesh.calcNormals()

      mdlobj = mdlobj.next
      if mdlobj == None:
        mdlobj = p_mdlobj.next


def load_mcell_mdl(filepath):
    import time
    from io_utils import load_image, unpack_list, unpack_face_list

    t = time.time()
    obj_spec, obj = read(filepath)
    if obj is None:
        print('Invalid file')
        return

    uvindices = colindices = None
    # noindices = None # Ignore normals

    for el in obj_spec.specs:
        if el.name == b'vertex':
            vindices = vindices_x, vindices_y, vindices_z = (el.index(b'x'), el.index(b'y'), el.index(b'z'))
            # noindices = (el.index('nx'), el.index('ny'), el.index('nz'))
            # if -1 in noindices: noindices = None
            uvindices = (el.index(b's'), el.index(b't'))
            if -1 in uvindices:
                uvindices = None
            colindices = (el.index(b'red'), el.index(b'green'), el.index(b'blue'))
            if -1 in colindices:
                colindices = None
        elif el.name == b'face':
            findex = el.index(b'vertex_indices')

    mesh_faces = []
    mesh_uvs = []
    mesh_colors = []

    def add_face(vertices, indices, uvindices, colindices):
        mesh_faces.append(indices)
        if uvindices:
            mesh_uvs.append([(vertices[index][uvindices[0]], 1.0 - vertices[index][uvindices[1]]) for index in indices])
        if colindices:
            mesh_colors.append([(vertices[index][colindices[0]] / 255.0, vertices[index][colindices[1]] / 255.0, vertices[index][colindices[2]] / 255.0) for index in indices])

    if uvindices or colindices:
        # If we have Cols or UVs then we need to check the face order.
        add_face_simple = add_face

        # EVIL EEKADOODLE - face order annoyance.
        def add_face(vertices, indices, uvindices, colindices):
            if len(indices) == 4:
                if indices[2] == 0 or indices[3] == 0:
                    indices = indices[2], indices[3], indices[0], indices[1]
            elif len(indices) == 3:
                if indices[2] == 0:
                    indices = indices[1], indices[2], indices[0]

            add_face_simple(vertices, indices, uvindices, colindices)

    verts = obj[b'vertex']

    if b'face' in obj:
        for f in obj[b'face']:
            ind = f[findex]
            len_ind = len(ind)
            if len_ind <= 4:
                add_face(verts, ind, uvindices, colindices)
            else:
                # Fan fill the face
                for j in range(len_ind - 2):
                    add_face(verts, (ind[0], ind[j + 1], ind[j + 2]), uvindices, colindices)

    ply_name = bpy.path.display_name_from_filepath(filepath)

    mesh = bpy.data.meshes.new(name=ply_name)

    mesh.vertices.add(len(obj[b'vertex']))

    mesh.vertices.foreach_set("co", [a for v in obj[b'vertex'] for a in (v[vindices_x], v[vindices_y], v[vindices_z])])

    if mesh_faces:
        mesh.faces.add(len(mesh_faces))
        mesh.faces.foreach_set("vertices_raw", unpack_face_list(mesh_faces))

        if uvindices or colindices:
            if uvindices:
                uvlay = mesh.uv_textures.new()
            if colindices:
                vcol_lay = mesh.vertex_colors.new()

            if uvindices:
                for i, f in enumerate(uvlay.data):
                    ply_uv = mesh_uvs[i]
                    for j, uv in enumerate(f.uv):
                        uv[0], uv[1] = ply_uv[j]

            if colindices:
                for i, f in enumerate(vcol_lay.data):
                    # XXX, colors dont come in right, needs further investigation.
                    ply_col = mesh_colors[i]
                    if len(ply_col) == 4:
                        f_col = f.color1, f.color2, f.color3, f.color4
                    else:
                        f_col = f.color1, f.color2, f.color3

                    for j, col in enumerate(f_col):
                        col.r, col.g, col.b = ply_col[j]

    mesh.validate()
    mesh.update()

    scn = bpy.context.scene
    #scn.objects.selected = [] # XXX25

    obj = bpy.data.objects.new(ply_name, mesh)
    scn.objects.link(obj)
    scn.objects.active = obj
    obj.select = True

    print('\nSuccessfully imported %r in %.3f sec' % (filepath, time.time() - t))


def load(operator, context, filepath=""):
    load_mcell_mdl(filepath)
    return {'FINISHED'}
