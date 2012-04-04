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


import bpy
from bpy.app.handlers import persistent
import mathutils
import glob
import os
import random
import re
import resource



#CellBlender Operators:

class MCELL_OT_region_add(bpy.types.Operator):
  bl_idname = "mcell.region_add"
  bl_label = "Add New Surface Region"
  bl_description = "Add a new surface region to an object"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.object.mcell.regions.region_list.add()
    context.object.mcell.regions.active_reg_index = len(bpy.context.object.mcell.regions.region_list)-1
    return {'FINISHED'}
 


class MCELL_OT_region_remove(bpy.types.Operator):
  bl_idname = "mcell.region_remove"
  bl_label = "Remove Surface Region"
  bl_description = "Remove selected surface region from object"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.object.mcell.regions.region_list.remove(bpy.context.object.mcell.regions.active_reg_index)
    context.object.mcell.regions.active_reg_index = bpy.context.object.mcell.regions.active_reg_index-1
    if (context.object.mcell.regions.active_reg_index<0):
      context.object.mcell.regions.active_reg_index = 0
    return {'FINISHED'}



class MCELL_OT_region_faces_assign(bpy.types.Operator):
  bl_idname = "mcell.region_faces_assign"
  bl_label = "Assign Selected Faces To Surface Region"
  bl_description = "Assign selected faces to surface region"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    aobj = context.active_object
    obj_regs = aobj.mcell.regions
    if (aobj.data.total_face_sel > 0):
      if not aobj.data.get('mcell'):
        aobj.data['mcell'] = {}
      if not aobj.data['mcell'].get('regions'):
        aobj.data['mcell']['regions'] = {}
      reg = obj_regs.region_list[obj_regs.active_reg_index]
      if not aobj.data['mcell']['regions'].get(reg.name):
        aobj.data['mcell']['regions'][reg.name] = []
      mesh = aobj.data
      face_set = set([])
      for f in aobj.data['mcell']['regions'][reg.name]:
        face_set.add(f)
      bpy.ops.object.mode_set(mode='OBJECT')
      for f in mesh.faces:
        if f.select:
          face_set.add(f.index)
      bpy.ops.object.mode_set(mode='EDIT')

      reg_faces = list(face_set)
      reg_faces.sort()
      aobj.data['mcell']['regions'][reg.name] = reg_faces
          
#    obj_regs = aobj.mcell.regions
#    reg = obj_regs.region_list[obj_regs.active_reg_index]
#    mesh = aobj.data
#    for f in mesh.faces:
#      if f.select:
#        reg.faces.add()
#        reg.active_face_index = len(reg.faces)-1
#        reg.faces[reg.active_face_index].index = f.index
        
    return {'FINISHED'}
 


class MCELL_OT_region_faces_remove(bpy.types.Operator):
  bl_idname = "mcell.region_faces_remove"
  bl_label = "Remove Selected Faces From Surface Region"
  bl_description = "Remove selected faces from surface region"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    aobj = context.active_object
    obj_regs = aobj.mcell.regions
    if (aobj.data.total_face_sel > 0):
      if not aobj.data.get('mcell'):
        aobj.data['mcell'] = {}
      if not aobj.data['mcell'].get('regions'):
        aobj.data['mcell']['regions'] = {}
      reg = obj_regs.region_list[obj_regs.active_reg_index]
      if not aobj.data['mcell']['regions'].get(reg.name):
        aobj.data['mcell']['regions'][reg.name] = []
      mesh = aobj.data
      face_set = set(aobj.data['mcell']['regions'][reg.name].to_list())
      bpy.ops.object.mode_set(mode='OBJECT')
      for f in mesh.faces:
        if f.select:
          if f.index in face_set:
            face_set.remove(f.index)
      bpy.ops.object.mode_set(mode='EDIT')

      reg_faces = list(face_set)
      reg_faces.sort()
      aobj.data['mcell']['regions'][reg.name] = reg_faces

    return {'FINISHED'}
 


class MCELL_OT_region_faces_select(bpy.types.Operator):
  bl_idname = "mcell.region_faces_select"
  bl_label = "Select Faces of Selected Surface Region"
  bl_description = "Select faces of selected surface region"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    aobj = context.active_object
    obj_regs = aobj.mcell.regions
    if not aobj.data.get('mcell'):
      aobj.data['mcell'] = {}
    if not aobj.data['mcell'].get('regions'):
      aobj.data['mcell']['regions'] = {}
    reg = obj_regs.region_list[obj_regs.active_reg_index]
    if not aobj.data['mcell']['regions'].get(reg.name):
      aobj.data['mcell']['regions'][reg.name] = []
    mesh = aobj.data
    face_set = set(aobj.data['mcell']['regions'][reg.name].to_list())
    bpy.ops.object.mode_set(mode='OBJECT')
    msm = context.tool_settings.mesh_select_mode[0:]
    context.tool_settings.mesh_select_mode=[False,False,True]
    for f in face_set:
      mesh.faces[f].select = True
    bpy.ops.object.mode_set(mode='EDIT')

    context.tool_settings.mesh_select_mode=msm
    return {'FINISHED'}
 


class MCELL_OT_region_faces_deselect(bpy.types.Operator):
  bl_idname = "mcell.region_faces_deselect"
  bl_label = "Deselect Faces of Selected Surface Region"
  bl_description = "Deselect faces of selected surface region"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    aobj = context.active_object
    obj_regs = aobj.mcell.regions
    if not aobj.data.get('mcell'):
      aobj.data['mcell'] = {}
    if not aobj.data['mcell'].get('regions'):
      aobj.data['mcell']['regions'] = {}
    reg = obj_regs.region_list[obj_regs.active_reg_index]
    if not aobj.data['mcell']['regions'].get(reg.name):
      aobj.data['mcell']['regions'][reg.name] = []
    mesh = aobj.data
    face_set = set(aobj.data['mcell']['regions'][reg.name].to_list())
    bpy.ops.object.mode_set(mode='OBJECT')
    msm = context.tool_settings.mesh_select_mode[0:]
    context.tool_settings.mesh_select_mode=[False,False,True]
    for f in face_set:
      mesh.faces[f].select = False
    bpy.ops.object.mode_set(mode='EDIT')

    context.tool_settings.mesh_select_mode=msm
    return {'FINISHED'}
 


class MCELL_OT_vertex_groups_to_regions(bpy.types.Operator):
  bl_idname = "mcell.vertex_groups_to_regions"
  bl_label = "Convert Vertex Groups of Selected Objects to Regions"
  bl_description = "Convert Vertex Groups to Regions"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    scn = context.scene
    sobjs = context.selected_objects

    # For each selected object:
    for obj in sobjs:
      print(obj.name)
      scn.objects.active = obj
      obj.select = True
      obj_regs = obj.mcell.regions
      vgs = obj.vertex_groups

      # If there are vertex groups to convert:
      if (len(vgs) > 0):
        mesh = obj.data

        # For each vertex group:
        for vg in vgs:

          # Deselect the whole mesh:
          bpy.ops.object.mode_set(mode='EDIT')
          bpy.ops.mesh.select_all(action='DESELECT')

          # Select the vertex group:
          print(vg.name)
          bpy.ops.object.vertex_group_set_active(group=vg.name)
          bpy.ops.object.vertex_group_select()

          # If there are selected faces:
          if (mesh.total_face_sel > 0):
            print('  vg faces: %d'%(mesh.total_face_sel))

            # Setup mesh regions IDProp if necessary:
            if not mesh.get('mcell'):
              mesh['mcell'] = {}
            if not mesh['mcell'].get('regions'):
              mesh['mcell']['regions'] = {}

            # look for vg.name in region_list and add if not found:
            # method 1:
            if (obj_regs.region_list.find(vg.name) == -1):
              bpy.ops.mcell.region_add()
              reg = obj_regs.region_list[obj_regs.active_reg_index]
              reg.name = vg.name
            reg = obj_regs.region_list[vg.name]

            # append faces in vertex group to faces in region:
            # retreive or create region on mesh:
            if not mesh['mcell']['regions'].get(vg.name):
              mesh['mcell']['regions'][reg.name] = []
            face_set = set([])
            for f in mesh['mcell']['regions'][reg.name]:
              face_set.add(f)
            print('  reg faces 0: %d'%(len(face_set)))
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.faces:
              if f.select:
                face_set.add(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            reg_faces = list(face_set)
            reg_faces.sort()
            print('  reg faces 1: %d'%(len(reg_faces)))
            mesh['mcell']['regions'][reg.name] = reg_faces
        
    return {'FINISHED'}



class MCELL_OT_molecule_add(bpy.types.Operator):
  bl_idname = "mcell.molecule_add"
  bl_label = "Add Molecule"
  bl_description = "Add a new molecule type to an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.species_list.add()
    context.scene.mcell.active_mol_index = len(bpy.context.scene.mcell.species_list)-1
    return {'FINISHED'}
 


class MCELL_OT_molecule_remove(bpy.types.Operator):
  bl_idname = "mcell.molecule_remove"
  bl_label = "Remove Molecule"
  bl_description = "Remove selected molecule type from an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.species_list.remove(bpy.context.scene.mcell.active_mol_index)
    context.scene.mcell.active_mol_index = bpy.context.scene.mcell.active_mol_index-1
    if (context.scene.mcell.active_mol_index<0):
      context.scene.mcell.active_mol_index = 0
    return {'FINISHED'}



class MCELL_OT_reaction_add(bpy.types.Operator):
  bl_idname = "mcell.reaction_add"
  bl_label = "Add Reaction"
  bl_description = "Add a new reaction to an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.reactions.reaction_list.add()
    context.scene.mcell.reactions.active_rxn_index = len(bpy.context.scene.mcell.reactions.reaction_list)-1
    return {'FINISHED'}
 


class MCELL_OT_reaction_remove(bpy.types.Operator):
  bl_idname = "mcell.reaction_remove"
  bl_label = "Remove Reaction"
  bl_description = "Remove selected reaction from an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.reactions.reaction_list.remove(bpy.context.scene.mcell.reactions.active_rxn_index)
    context.scene.mcell.reactions.active_rxn_index = bpy.context.scene.mcell.reactions.active_rxn_index-1
    if (context.scene.mcell.reactions.active_rxn_index<0):
      context.scene.mcell.reactions.active_rxn_index = 0
    return {'FINISHED'}



class MCELL_OT_export_project(bpy.types.Operator):
  bl_idname = "mcell.export_project"
  bl_label = "Export CellBlender Project"
  bl_description = "Export CellBlender Project"
  bl_options = {'REGISTER'}
  
  def execute(self,context):
    mc = context.scene.mcell
    if mc.project_settings.export_format == 'mcell_mdl':
      if not mc.project_settings.export_selection_only:
        bpy.ops.object.select_by_type(type='MESH')
      filepath = mc.project_settings.project_dir+'/'+mc.project_settings.base_name+'.geometry.mdl'
      bpy.ops.export_mdl_mesh.mdl('INVOKE_DEFAULT',filepath=filepath)

    return {'FINISHED'}



class MCELL_OT_set_project_dir(bpy.types.Operator):
  bl_idname = "mcell.set_project_dir"
  bl_label = "Set Project Directory"
  bl_description = "Set CellBlender Project Directory"
  bl_options = {'REGISTER','UNDO'}

  filepath = bpy.props.StringProperty(subtype="FILE_PATH",default="")
  directory = bpy.props.StringProperty(subtype="DIR_PATH")

  def __init__(self):
    self.directory = bpy.context.scene.mcell.project_settings.project_dir
  
  # Note: use classmethod "poll" to determine when runability of operator is valid
  #  @classmethod
  #  def poll(cls, context):
  #    return context.object is not None
  
  def execute(self, context):
    
    mc = context.scene.mcell
    if (os.path.isdir(self.filepath)):
      dir = self.filepath
    else:
      dir = os.path.dirname(self.filepath)
    
    # Reset mol_file_list to empty
    for i in range(mc.mol_viz.mol_file_num-1,-1,-1):
      mc.mol_viz.mol_file_list.remove(i)
    
    mc.mol_viz.mol_file_name = ''
    mc.project_settings.project_dir=dir
    return {'FINISHED'}
  
  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}



class MCELL_OT_set_mol_viz_dir(bpy.types.Operator):
  bl_idname = "mcell.set_mol_viz_dir"
  bl_label = "Read Molecule Files"
  bl_description = "Read MCell Molecule Files for Visualization"
  bl_options = {'REGISTER'}

  filepath = bpy.props.StringProperty(subtype="FILE_PATH",default="")
  directory = bpy.props.StringProperty(subtype="DIR_PATH")

  def __init__(self):
    self.directory = bpy.context.scene.mcell.mol_viz.mol_file_dir
  
  # Note: use classmethod "poll" to determine when runability of operator is valid
  #  @classmethod
  #  def poll(cls, context):
  #    return context.object is not None
  
  def execute(self, context):
    
    mc = context.scene.mcell
    if (os.path.isdir(self.filepath)):
      mol_file_dir = self.filepath
    else:
      mol_file_dir = os.path.dirname(self.filepath)
    mol_file_list = glob.glob(mol_file_dir + '/*')
    mol_file_list.sort()
    
    # Reset mol_file_list to empty
    for i in range(mc.mol_viz.mol_file_num-1,-1,-1):
      mc.mol_viz.mol_file_list.remove(i)
    
    mc.mol_viz.mol_file_dir=mol_file_dir
    i = 0
    for mol_file_name in mol_file_list:
      new_item = mc.mol_viz.mol_file_list.add()
      new_item.name = os.path.basename(mol_file_name)
      i+=1
    
    mc.mol_viz.mol_file_num = len(mc.mol_viz.mol_file_list)
    mc.mol_viz.mol_file_stop_index = mc.mol_viz.mol_file_num-1
    mc.mol_viz.mol_file_index = 0
    
    MolVizUpdate(mc,0)
    return {'FINISHED'}
  
  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}



class MCELL_OT_mol_viz_set_index(bpy.types.Operator):
  bl_idname = "mcell.mol_viz_set_index"
  bl_label = "Set Molecule File Index"
  bl_description = "Set MCell Molecule File Index for Visualization"
  bl_options = {'REGISTER'}
  
  def execute(self,context):
    mc = bpy.data.scenes[0].mcell
    i = mc.mol_viz.mol_file_index
    if (i > mc.mol_viz.mol_file_stop_index):
      i = mc.mol_viz.mol_file_stop_index
    if (i < mc.mol_viz.mol_file_start_index):
      i = mc.mol_viz.mol_file_start_index
    mc.mol_viz.mol_file_index = i
    MolVizUpdate(mc,i)
    return{'FINISHED'}



class MCELL_OT_mol_viz_next(bpy.types.Operator):
  bl_idname = "mcell.mol_viz_next"
  bl_label = "Step to Next Molecule File"
  bl_description = "Step to Next MCell Molecule File for Visualization"
  bl_options = {'REGISTER'}
  
  def execute(self,context):
    mc = context.scene.mcell
    i = mc.mol_viz.mol_file_index + mc.mol_viz.mol_file_step_index
    if (i > mc.mol_viz.mol_file_stop_index):
      i = mc.mol_viz.mol_file_stop_index
    mc.mol_viz.mol_file_index = i
    MolVizUpdate(mc,i)
    return{'FINISHED'}



class MCELL_OT_mol_viz_prev(bpy.types.Operator):
  bl_idname = "mcell.mol_viz_prev"
  bl_label = "Step to Previous Molecule File"
  bl_description = "Step to Previous MCell Molecule File for Visualization"
  bl_options = {'REGISTER'}
  
  def execute(self,context):
    mc = context.scene.mcell
    i = mc.mol_viz.mol_file_index - mc.mol_viz.mol_file_step_index
    if (i < mc.mol_viz.mol_file_start_index):
      i = mc.mol_viz.mol_file_start_index
    mc.mol_viz.mol_file_index = i
    MolVizUpdate(mc,i)
    return{'FINISHED'}



#CellBlender operator helper functions:


@persistent
def frame_change_handler(scn):
  mc = bpy.data.scenes[0].mcell
  curr_frame = mc.mol_viz.mol_file_index
  if (not curr_frame == scn.frame_current):
    mc.mol_viz.mol_file_index = scn.frame_current
    bpy.ops.mcell.mol_viz_set_index(None)
    scn.update()
    if mc.mol_viz.render_and_save:
      scn.render.filepath = '//stores_on/frames/frame_%05d.png' % (scn.frame_current)
      bpy.ops.render.render(write_still=True)



def render_handler(scn):
  mc = scn.mcell
  curr_frame = mc.mol_viz.mol_file_index
  if (not curr_frame == scn.frame_current):
    mc.mol_viz.mol_file_index = scn.frame_current
    bpy.ops.mcell.mol_viz_set_index(None)
  scn.update()



def MolVizUpdate(mcell_prop,i):
  mc = mcell_prop
  filename = mc.mol_viz.mol_file_list[i].name
  mc.mol_viz.mol_file_name = filename
  filepath = os.path.join(mc.mol_viz.mol_file_dir,filename)
  
  global_undo = bpy.context.user_preferences.edit.use_global_undo
  bpy.context.user_preferences.edit.use_global_undo = False
  
  MolVizUnlink(mc)
  MolVizFileRead(mc,filepath)
  
  bpy.context.user_preferences.edit.use_global_undo = global_undo



def MolVizDelete(mcell_prop):
  
  mc = mcell_prop
  bpy.ops.object.select_all(action='DESELECT')
  for mol_name in mc.mol_viz.mol_viz_list:
    bpy.ops.object.select_name(name=mol_name.name,extend=True)
  
  bpy.ops.object.delete('EXEC_DEFAULT')
  
  # Reset mol_viz_list to empty
  for i in range(len(mc.mol_viz.mol_viz_list)-1,-1,-1):
    mc.mol_viz.mol_viz_list.remove(i)



def MolVizUnlink(mcell_prop):
  
  mc = mcell_prop
  scn = bpy.data.scenes[0]
  scn_objs = scn.objects
  meshes = bpy.data.meshes
  objs = bpy.data.objects
  for mol_item in mc.mol_viz.mol_viz_list:
    mol_name = mol_item.name
    mol_obj = scn_objs[mol_name]
    scn_objs['%s_shape' % (mol_name)].parent = None
    mol_pos_mesh = mol_obj.data
    scn_objs.unlink(mol_obj)
    objs.remove(mol_obj)
  
  scn.update()
  # Reset mol_viz_list to empty
  for i in range(len(mc.mol_viz.mol_viz_list)-1,-1,-1):
    mc.mol_viz.mol_viz_list.remove(i)

    

def MolVizFileRead(mcell_prop,filepath):
  
  try:
    
#    begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#    print ('Processing molecules from file:  %s' % (filepath))

    mol_data = [[s.split()[0], [float(x) for x in s.split()[1:]]] for s in open(filepath,'r').read().split('\n') if s != '']
    
    mols_obj = bpy.data.objects.get('molecules')
    if not mols_obj:
      bpy.ops.object.add()
      mols_obj = bpy.context.selected_objects[0]
      mols_obj.name = 'molecules'
    
    if len(mol_data) > 0:
      meshes = bpy.data.meshes
      mats = bpy.data.materials
      objs = bpy.data.objects
      scn = bpy.data.scenes[0]
      scn_objs = scn.objects
      mc = mcell_prop
      z_axis = mathutils.Vector((0.0, 0.0, 1.0))
      ident_mat = mathutils.Matrix.Translation(mathutils.Vector((0.0,0.0,0.0)))
      
      mol_dict = {}
      mol_pos = []
      mol_orient = []
      
      for n in range(len(mol_data)):
        mol_name = 'mol_%s' % (mol_data[n][0])
        if not mol_name in mol_dict:
          mol_dict[mol_name] = [[],[]]
          new_item = mc.mol_viz.mol_viz_list.add()
          new_item.name = mol_name
        mol_dict[mol_name][0].extend(mol_data[n][1][0:3])
        mol_dict[mol_name][1].extend(mol_data[n][1][3:])
      
      for mol_name in mol_dict.keys():
        mol_mat_name='%s_mat'%(mol_name)
        mol_pos = mol_dict[mol_name][0]
        mol_orient = mol_dict[mol_name][1]

#       Name mesh shape template according to molecule type (2D or 3D)
#         TODO: we can now use shape from molecule properties if it exists
        if (mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) | (mol_orient[2] != 0.0):
          is_vmol = False
          mol_shape_mesh_name = '%s_shape' % (mol_name)
          mol_shape_obj_name = mol_shape_mesh_name
        else:
          is_vmol = True
          mol_shape_mesh_name = '%s_shape' % (mol_name)
          mol_shape_obj_name = mol_shape_mesh_name
          for n in range(len(mol_orient)):
            mol_orient[n] = random.uniform(-1.0,1.0)

#       Look-up mesh shape template and create if needed
        mol_shape_mesh = meshes.get(mol_shape_mesh_name)
        if not mol_shape_mesh:
          bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0, size=0.01)
          mol_shape_obj = bpy.context.active_object
          mol_shape_obj.name = mol_shape_obj_name
          mol_shape_obj.track_axis = "POS_Z" 
          mol_shape_mesh = mol_shape_obj.data
          mol_shape_mesh.name = mol_shape_mesh_name
        else:
          mol_shape_obj = objs.get(mol_shape_obj_name)
      

#       Look-up material and create if needed. Associate material with mesh shape
        mol_mat = mats.get(mol_mat_name)
        if not mol_mat:
          mol_mat = mats.new(mol_mat_name)
          mol_mat.diffuse_color = [1.0, 0.0, 0.0]
        if not mol_shape_mesh.materials.get(mol_mat_name):
          mol_shape_mesh.materials.append(mol_mat)

#       Create a "mesh" to hold instances of molecule positions 
        mol_pos_mesh_name = '%s_pos' % (mol_name)
        mol_pos_mesh = meshes.get(mol_pos_mesh_name)
        if mol_pos_mesh:
          meshes.remove(mol_pos_mesh)
        
        mol_pos_mesh = meshes.new(mol_pos_mesh_name)
        mol_pos_mesh.vertices.add(len(mol_pos)//3)
        mol_pos_mesh.vertices.foreach_set("co",mol_pos)
        mol_pos_mesh.vertices.foreach_set("normal",mol_orient)
        
        mol_obj = objs.get(mol_name)
        if not mol_obj:
          mol_obj = objs.new(mol_name,mol_pos_mesh)
        if not scn_objs.get(mol_name):
          scn_objs.link(mol_obj)
        
        mol_shape_obj.parent = mol_obj
        mol_obj.dupli_type = 'VERTS'
        mol_obj.use_dupli_vertices_rotation=True
        mol_obj.parent = mols_obj
          
    scn.update()

#    utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
#    print ('   Processed %d molecules in %g seconds\n' % (len(mol_data),utime))

  except IOError:
    print(('\n***** File not found: %s\n') % (filepath))
  except ValueError:
    print(('\n***** Invalid data in file: %s\n') % (filepath))



# Meshalyzer
class MCELL_OT_meshalyzer(bpy.types.Operator):
  bl_idname = "mcell.meshalyzer"
  bl_label = "Analyze Geometric Properties of Mesh"
  bl_description = "Analyze Geometric Properties of Mesh"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mc = scn.mcell
    objs = context.selected_objects

    mc.meshalyzer.object_name = ''
    mc.meshalyzer.vertices = 0
    mc.meshalyzer.edges = 0
    mc.meshalyzer.faces = 0
    mc.meshalyzer.watertight = ''
    mc.meshalyzer.manifold = ''
    mc.meshalyzer.normal_status = ''
    mc.meshalyzer.area = 0
    mc.meshalyzer.volume = 0

    if (len(objs) != 1):
      mc.meshalyzer.status = 'Please Select One Mesh Object'
      return {'FINISHED'}

    obj = objs[0]

    mc.meshalyzer.object_name = obj.name

    if not (obj.type == 'MESH'):
      mc.meshalyzer.status = 'Selected Object Not a Mesh'
      return {'FINISHED'}

    t_mat = obj.matrix_world
    mesh=obj.data

    mc.meshalyzer.vertices = len(mesh.vertices)
    mc.meshalyzer.edges = len(mesh.edges)
    mc.meshalyzer.faces = len(mesh.faces)

    area = 0
    for f in mesh.faces:
      if not (len(f.vertices) == 3):
        mc.meshalyzer.status = 'Mesh Not Triangulated'
        return {'FINISHED'}

      tv0 = mesh.vertices[f.vertices[0]].co * t_mat
      tv1 = mesh.vertices[f.vertices[1]].co * t_mat
      tv2 = mesh.vertices[f.vertices[2]].co * t_mat
      area = area + mathutils.geometry.area_tri(tv0,tv1,tv2)

    mc.meshalyzer.area = area

    (edge_faces, edge_face_count) = make_efdict(mesh)

    is_closed = check_closed(edge_face_count)
    is_manifold = check_manifold(edge_face_count)
    is_orientable = check_orientable(mesh,edge_faces,edge_face_count)

    if is_orientable:
      mc.meshalyzer.normal_status = 'Consistent Normals'
    else:
      mc.meshalyzer.normal_status = 'Inconsistent Normals'

    if is_closed:
      mc.meshalyzer.watertight = 'Watertight Mesh'
    else:
      mc.meshalyzer.watertight = 'Non-watertight Mesh'

    if is_manifold:
      mc.meshalyzer.manifold = 'Manifold Mesh'
    else:
      mc.meshalyzer.manifold = 'Non-manifold Mesh'
  
    if is_orientable and is_manifold and is_closed:
      volume = mesh_vol(mesh,t_mat)
      mc.meshalyzer.volume = volume
      if volume >= 0:
        mc.meshalyzer.normal_status = 'Outward Facing Normals'
      else:
        mc.meshalyzer.normal_status = 'Inward Facing Normals'

    mc.meshalyzer.status = ''
    return {'FINISHED'}


#Compute volume of triangulated, orientable, watertight, manifold mesh
#  volume > 0 means outward facing normals
#  volume < 0 means inward facing normals
def mesh_vol(mesh,t_mat):

  volume = 0.0
  for f in mesh.faces:
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
    det=x0*(y1*z2-y2*z1)+x1*(y2*z0-y0*z2)+x2*(y0*z1-y1*z0)
    volume = volume + det

  volume = volume/6.0

  return(volume)



def make_efdict(mesh):

  edge_faces = {}
  edge_face_count = {}
  for f in mesh.faces:
    for ek in f.edge_keys:
      if ek in edge_faces:
        edge_faces[ek] ^= f.index
        edge_face_count[ek] = edge_face_count[ek] + 1
      else:
        edge_faces[ek] = f.index
        edge_face_count[ek] = 1

  return(edge_faces, edge_face_count)



def check_manifold(edge_face_count):

  for ek in edge_face_count.keys():
    if edge_face_count[ek] != 2:
      return (0)

  return(1)



def check_closed(edge_face_count):

  for ek in edge_face_count.keys():
    if not edge_face_count[ek] == 2:
      return (0)

  return(1)



def check_orientable(mesh,edge_faces,edge_face_count):

  ev_order = [[0,1],[1,2],[2,0]]
  edge_checked = {}

  for f in mesh.faces:
    for i in range(0,len(f.vertices)):
      ek = f.edge_keys[i]
      if not ek in edge_checked:
        edge_checked[ek] = 1
        if edge_face_count[ek] == 2:
          nfi = f.index^edge_faces[ek]
          nf = mesh.faces[nfi]
          for j in range(0,len(nf.vertices)):
            if ek == nf.edge_keys[j]:
              if f.vertices[ev_order[i][0]] != nf.vertices[ev_order[j][1]]:
                return (0)
              break

  return (1)



class MCELL_OT_select_filtered(bpy.types.Operator):
  bl_idname = "mcell.select_filtered"
  bl_label = "Select Filtered"
  bl_description = "Select objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mc = scn.mcell
    objs = scn.objects

    filter = mc.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.select = True

    return {'FINISHED'}



class MCELL_OT_deselect_filtered(bpy.types.Operator):
  bl_idname = "mcell.deselect_filtered"
  bl_label = "Deselect Filtered"
  bl_description = "Deselect objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mc = scn.mcell
    objs = scn.objects

    filter = mc.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.select = False

    return {'FINISHED'}



