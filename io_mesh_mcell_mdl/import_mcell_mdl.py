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
from . import mdlmesh_parser


def load_mcell_mdl(filepath):

  print("Calling mdlmesh_parser.mdl_parser(\'%s\')..." % (filepath))
  root_mdlobj = mdlmesh_parser.mdl_parser(filepath)
  print("Done calling mdlmesh_parser.mdl_parser(\'%s\')" % (filepath))

  scn = bpy.context.scene
  mcell = scn.mcell
  meshes = bpy.data.meshes
  mats = bpy.data.materials
  objs = bpy.data.objects
  scn_objs = scn.objects
  
  obj_mat = mats.get('obj_mat')
  if not obj_mat:
    obj_mat = mats.new('obj_mat')
    obj_mat.diffuse_color = [0.7, 0.7, 0.7]

  reg_mat = mats.get('reg_mat')
  if not reg_mat:
    reg_mat = mats.new('reg_mat')
    reg_mat.diffuse_color = [0.8, 0.0, 0.0]

  mdlobj = root_mdlobj
  while not mdlobj == None:
    if mdlobj.object_type == 0:
      # META_OBJ
      p_mdlobj = mdlobj
      mdlobj = mdlobj.first_child
    else:
      # POLY_OBJ
      objname = mdlobj.name
      print(objname,len(mdlobj.vertices),len(mdlobj.faces))
      mesh = meshes.get(objname)
      if not mesh:
        mesh = meshes.new(objname)
        mesh.from_pydata(mdlobj.vertices,[],mdlobj.faces)

      if not mesh.materials.get('obj_mat'):
        mesh.materials.append(obj_mat)

      if not mesh.materials.get('reg_mat'):
        mesh.materials.append(reg_mat)

      obj = objs.get(objname)
      if not obj:
        obj = objs.new(objname, mesh)
        scn_objs.link(obj)

#      mesh.polygons.foreach_set("material_index",mesh.materials.find('obj_mat'))

      mesh.validate(verbose=True)
      mesh.update()
      scn.objects.active = obj
      obj.select = True

      mdlobj = mdlobj.next
      if mdlobj == None:
        mdlobj = p_mdlobj.next



def load(operator, context, filepath=""):
    load_mcell_mdl(filepath)
    return {'FINISHED'}

