import bpy
import mathutils
import os
import resource
import re
from math import *


class MCELL_PT_viz_results(bpy.types.Panel):
  bl_label = "Visualize Simulation Results"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"

  def draw(self, context):
    layout = self.layout

    mc = context.scene.mcell 

    row=layout.row()
    row.operator("mcell.set_mol_viz_dir",text="Set Molecule Viz Directory",icon="FILESEL")
#    layout.prop(mc,"mol_file_path",text="Molecule Viz Directory")
    row = layout.row()
    row.label(text="Molecule Viz Directory:  "+mc.mol_file_dir)
    row = layout.row()
    row.label(text="Current Molecule File:  "+mc.mol_file_name)
#    col = row.column()
#    col.label(text="Molecule File Path:  "+mc.mol_file_path)
#    col = row.column(align=True)
#    col.operator("mcell.molecule_file_read",text="",icon="FILESEL")
#    layout.prop(mcell.molecule_file_read,"filepath",text="Molecule File Path")
      
#  def MolFileRead(self, context)
  

class MCELL_PT_define_molecules(bpy.types.Panel):
  bl_label = "Define Molecules"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"

  def draw(self, context):
    layout = self.layout

    mc = context.scene.mcell 

    row = layout.row()
    row.label(text="Defined Molecule Types:", icon='FORCE_LENNARDJONES')
    row = layout.row()
    col = row.column()
    col.template_list(mc,"species_list",mc,"active_mol_index",rows=2)
    col = row.column(align=True)
    col.operator("mcell.molecule_add",icon='ZOOMIN',text="")
    col.operator("mcell.molecule_remove",icon='ZOOMOUT',text="")
    if len(mc.species_list)>0:
      mol = mc.species_list[mc.active_mol_index]
      layout.prop(mol,"name")
      layout.prop(mol,"type")
      layout.prop(mol,"diffusion_constant")
      layout.prop(mol,"target_only")
      layout.prop(mol,"custom_time_step")
      layout.prop(mol,"custom_space_step")


# See notes below for errors in documentation

class MCellSpeciesProperty(bpy.types.IDPropertyGroup):
  name = bpy.props.StringProperty(name="Molecule Name")
  type_enum = [
                    ('2D','2D','2D'),
                    ('3D','3D','3D')]
  type = bpy.props.EnumProperty(items=type_enum,name="Molecule Type")
  diffusion_constant = bpy.props.FloatProperty(name="Diffusion Constant",precision=4)
  target_only = bpy.props.BoolProperty(name="Target Only")
  custom_time_step = bpy.props.FloatProperty(name="Custom Time Step")
  custom_space_step = bpy.props.FloatProperty(name="Custom Space Step")

  
class MCellPropertyGroup(bpy.types.IDPropertyGroup):
  mol_file_path = bpy.props.StringProperty(name="Molecule File Path",subtype="NONE")
  mol_file_dir = bpy.props.StringProperty(name="Molecule File Dir",subtype="NONE")
  mol_file_name = bpy.props.StringProperty(name="Molecule File Name",subtype="NONE")
  species_list = bpy.props.CollectionProperty(type=MCellSpeciesProperty,name="Molecule List")
  active_mol_index = bpy.props.IntProperty(name="Active Molecule Index",default=0)


class MCellMoleculeAdd(bpy.types.Operator):
  bl_idname = "mcell.molecule_add"
  bl_label = "Add Molecule"
  bl_description = "Add a molecule type to an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.species_list.add()
    context.scene.mcell.active_mol_index = len(bpy.context.scene.mcell.species_list)-1
    return {'FINISHED'}
  
 
class MCellMoleculeRemove(bpy.types.Operator):
  bl_idname = "mcell.molecule_remove"
  bl_label = "Remove Molecule"
  bl_description = "Remove a molecule type from an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    bpy.context.scene.mcell.species_list.remove(bpy.context.scene.mcell.active_mol_index)
    bpy.context.scene.mcell.active_mol_index = bpy.context.scene.mcell.active_mol_index-1
    if (bpy.context.scene.mcell.active_mol_index<0):
      bpy.context.scene.mcell.active_mol_index = 0
    return {'FINISHED'}


class MCellSetMolVizDir(bpy.types.Operator):
  bl_idname = "mcell.set_mol_viz_dir"
  bl_label = "Read Molecule File"
  bl_description = "Read an MCell Molecule File for Visualization"
  bl_options = {'REGISTER'}

  filepath = bpy.props.StringProperty(subtype="FILE_PATH")

# Note: use classmethod "poll" to determine when runability of operator is valid
#  @classmethod
#  def poll(cls, context):
#    return context.object is not None

  def execute(self, context):
#    self.filepath = bpy.path.relpath(self.filepath)
    context.scene.mcell.mol_file_path = self.filepath
    context.scene.mcell.mol_file_dir = bpy.path.relpath(os.path.split(self.filepath)[0])
    context.scene.mcell.mol_file_name = os.path.split(self.filepath)[-1]
    bpy.context.user_preferences.edit.use_global_undo = False
#    MolVizUnlink(context)
    MolVizFileRead(context,self.filepath)
    bpy.context.user_preferences.edit.use_global_undo = True
    return {'FINISHED'}

  def invoke(self, context, event):
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}


def MolVizUnlink(context):

  mol_re = re.compile('mol_.*')
  scn_objs = context.scene.objects
  for obj in scn_objs:
    if obj.type == 'MESH':
      if mol_re.match(obj.name) != None:
        scn_objs.unlink(obj)
  

def MolVizFileRead(context,filepath):
      
  try:
    
    begin = resource.getrusage(resource.RUSAGE_SELF)[0]
    print ('Processing molecules from file:  %s' % (filepath))

    mol_data = [[s.split()[0], [float(x) for x in s.split()[1:]]] for s in open(filepath,'r').read().split('\n') if s != '']
  
    if len(mol_data) > 0:
      meshes = bpy.data.meshes
      mats = bpy.data.materials
      objs = bpy.data.objects
      scn = context.scene
      scn_objs = scn.objects
      z_axis = mathutils.Vector((0.0, 0.0, 1.0))
      ident_mat = mathutils.Matrix.Translation(mathutils.Vector((0.0,0.0,0.0)))
      mol_dict = {}
    
      for n in range(len(mol_data)):
        mol_name = 'mol_%s' % (mol_data[n][0])
        mol_pos = mol_data[n][1][0:3]
        mol_orient= mol_data[n][1][3:]
        
        pobj_name = '%s[%05d]' % (mol_name,0)
        mol_mat_name='%s_mat'%(mol_name)
      
#         name mesh shape template according to molecule type (2D or 3D)
#            Can now use shape from molecule properties if it exists
        if (mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) | (mol_orient[2] != 0.0):
          mol_mesh_name = '%s_shape' % (mol_name)
          mol_obj_name = mol_mesh_name
        else:
          mol_mesh_name = '%s_shape' % (mol_name)
          mol_obj_name = mol_mesh_name
      
#        Look-up mesh shape template and create if needed
        
        mol_mesh = meshes.get(mol_mesh_name)
        if not mol_mesh:
          bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0, size=0.01)
          mol_obj = context.active_object
          mol_obj.name = mol_obj_name
          mol_mesh = mol_obj.data
          mol_mesh.name = mol_mesh_name
        

#        Look-up material and create if needed and associate with mesh shape
        mol_mat = mats.get(mol_mat_name)
        if not mol_mat:
          mol_mat = mats.new(mol_mat_name)
          mol_mat.diffuse_color = [1.0, 0.0, 0.0]
          if not mol_mesh.materials.get(mol_mat_name):
            mol_mesh.materials.append(mol_mat)
            
# Create new mol_dict entry and zero counter for mol_name if necessary
        try:
          mol_n = mol_dict[mol_name]
        except KeyError:
          mol_dict[mol_name] = 0
          mol_n = 0
          obj_name_pattern = '%s[*' % (mol_name)
          bpy.ops.object.select_pattern(pattern=obj_name_pattern,extend=False)
          if context.selected_objects:
            bpy.ops.object.parent_clear()

        obj_name = '%s[%05d]' % (mol_name,mol_n)
          
        obj = objs.get(obj_name)
        if not obj:
          obj = objs.new(obj_name,mol_mesh)

#        pobj = objs[pobj_name]
#        if not obj == pobj:             
#          obj.parent = pobj
        
        if not scn_objs.get(obj_name):
          scn_objs.link(obj)
                           
        mol_dict[mol_name]=mol_n+1
        
        if (mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) | (mol_orient[2] != 0.0):
          obj_axis = mathutils.Vector(mol_orient)
          rot_angle = obj_axis.angle(z_axis)
          rot_axis = z_axis.cross(obj_axis).normalize()
          rot_mat = mathutils.Matrix.Rotation(rot_angle,4,rot_axis)
        else:
          rot_mat = ident_mat

        trans_vec = mathutils.Vector(mol_pos)
        trans_mat = mathutils.Matrix.Translation(trans_vec)
        obj_mat = rot_mat*trans_mat
        obj.matrix_world = obj_mat
    
    for key in mol_dict.keys():
      pobj_name = '%s[%05d]' % (key,0)
      obj_name_pattern = '%s[*' % (key)
      bpy.ops.object.select_name(name=pobj_name)
      bpy.ops.object.select_pattern(pattern=obj_name_pattern)
      bpy.ops.object.parent_set()
      bpy.ops.object.select_all(action='DESELECT')
          
    utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
    print ('   Processed %d molecules in %g seconds\n' % (len(mol_data),utime))
        
  except IOError:
    print(('\n***** File not found: %s\n') % (filepath))
  except ValueError:
    print(('\n***** Invalid data in file: %s\n') % (filepath))
        

def register():
  bpy.types.Scene.mcell = bpy.props.PointerProperty(type=MCellPropertyGroup)


def unregister():
#  del bpy.types.Scene.mcell
  pass
  
      
if __name__ == '__main__':
  register()


# Notes:
#   template_list takes a CollectionProperty and active index as input
#     "name" member of each item in the collection is shown in the GUI
#     the item specified by active index is highlighted

#   Turn off global undo for better performance and atomic operation of sequence of operators:
#     bpy.context.user_preferences.edit.use_global_undo = False
#     ...
#     bpy.context.user_preferences.edit.use_global_undo = True

# Errors in documentation:
#   ProperyGroup is really IDProptertyGroup
#   bpy.utils.register_class(myclass) does not exist.  Apparently classes automatically register