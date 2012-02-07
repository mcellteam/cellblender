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

# Copyright (C) 2012: Tom Bartol, bartol@salk.edu
# Contributors: Tom Bartol

"""
This script exports MCell MDL files from Blender,
and is a component of CellBlender.
"""

import bpy
import os
import mathutils


#__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

def createRegDict(obj):

  scn = bpy.context.scene
  reg_dict = {}
  obj_regs = obj.mcell.regions.region_list
  for reg in obj_regs:
    reg_dict[reg.name] = obj.data['mcell']['regions'][reg.name].to_list()

#  vgs = obj.vertex_groups
#  if (len(vgs) > 0):
#    mesh = obj.data
#    bpy.ops.object.mode_set(mode='EDIT')
#    bpy.ops.mesh.select_all(action='DESELECT')
#    for vg in vgs:
#      reg_faces = []
#      bpy.ops.object.mode_set(mode='OBJECT')
#      bpy.ops.object.vertex_group_set_active(group=vg.name)
#      bpy.ops.object.mode_set(mode='EDIT')
#      bpy.ops.object.vertex_group_select()
#      bpy.ops.object.mode_set(mode='OBJECT')
#      for f in mesh.faces:
#        if (f.select):
#          reg_faces.append(f.index)  
#      if not reg_dict.get(vg.name):
#        reg_dict[vg.name] = reg_faces
#
#      bpy.ops.object.mode_set(mode='EDIT')
#      bpy.ops.object.vertex_group_deselect()
#
#    bpy.ops.object.mode_set(mode='OBJECT')

  return reg_dict


def save(operator, context, filepath="", use_modifiers=True, use_normals=True, use_uv_coords=True, use_colors=True):

  scn = context.scene
  sobjs = context.selected_objects
#  sobjs = context.scene.objects
#  bpy.ops.object.select_all(action='DESELECT')

  if sobjs:
    file = open(filepath, "w", encoding="utf8", newline="\n")

    for obj in sobjs:
      if obj.type == 'MESH':
        scn.objects.active = obj
#        obj.select = True
        bpy.ops.object.mode_set(mode='OBJECT')
        file.write('%s POLYGON_LIST\n' % (obj.name))
        file.write('{\n')

        file.write('  VERTEX_LIST\n')
        file.write('  {\n')
        mesh = obj.data
        t_mat = obj.matrix_world
        verts = mesh.vertices
        for v in verts:
          t_vec = v.co * t_mat
          file.write('    [ %.15g, %.15g, %.15g ]\n' % (t_vec.x, t_vec.y, t_vec.z))
        file.write('  }\n')

        file.write('  ELEMENT_CONNECTIONS\n')
        file.write('  {\n')
        faces = mesh.faces
        for f in faces:
          file.write('    [ %d, %d, %d ]\n' % (f.vertices[0], f.vertices[1], f.vertices[2]))
        file.write('  }\n')

        reg_dict = createRegDict(obj)
        if reg_dict:
          file.write('  DEFINE_SURFACE_REGIONS\n')
          file.write('  {\n')
          reg_names = [k for k in reg_dict.keys()]
          reg_names.sort()
          for reg in reg_names:
            file.write('    %s\n' % (reg))
            file.write('    {\n')
            file.write('      ELEMENT_LIST = '+str(reg_dict[reg])+'\n' )
            file.write('    }\n')

          file.write('  }\n')

        file.write('}\n')
#        obj.select = False
        

  return {'FINISHED'}
