import bpy
import mathutils
import os
import glob
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
    row.label(text="Molecule Viz Directory:  "+mc.mol_viz.mol_file_dir)
    row = layout.row()
    row.label(text="Current Molecule File:  "+mc.mol_viz.mol_file_name)
    row = layout.row()
    row.template_list(mc.mol_viz,"mol_file_list",mc.mol_viz,"mol_file_index",rows=2)   
    row = layout.row()
    col = row.column(align=True)
    col.operator("mcell.mol_viz_prev",icon="PLAY_REVERSE",text="")
    col = row.column(align=True)
    col.operator("mcell.mol_viz_set_index",text=str(mc.mol_viz.mol_file_index))
    col = row.column(align=True)
    col.operator("mcell.mol_viz_next",icon="PLAY",text="")
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

class MCellSpeciesProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Molecule Name")
  type_enum = [
                    ('2D','2D','2D'),
                    ('3D','3D','3D')]
  type = bpy.props.EnumProperty(items=type_enum,name="Molecule Type")
  diffusion_constant = bpy.props.FloatProperty(name="Diffusion Constant",precision=4)
  target_only = bpy.props.BoolProperty(name="Target Only")
  custom_time_step = bpy.props.FloatProperty(name="Custom Time Step")
  custom_space_step = bpy.props.FloatProperty(name="Custom Space Step")
  
  
class MCellStringProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Text")
  

class MCellMolVizProperty(bpy.types.PropertyGroup):
  mol_file_dir = bpy.props.StringProperty(name="Molecule File Dir",subtype="NONE")
  mol_file_list = bpy.props.CollectionProperty(type=MCellStringProperty,name="Molecule File Name List")
  mol_file_num = bpy.props.IntProperty(name="Number of Molecule Files",default=0)
  mol_file_name = bpy.props.StringProperty(name="Current Molecule File Name",subtype="NONE")
  mol_file_index = bpy.props.IntProperty(name="Current Molecule File Index",default=0)
  mol_file_start_index = bpy.props.IntProperty(name="Molecule File Start Index",default=0)
  mol_file_stop_index = bpy.props.IntProperty(name="Molecule File Stop Index",default=0)
  mol_file_step_index = bpy.props.IntProperty(name="Molecule File Step Index",default=1)
  mol_viz_list = bpy.props.CollectionProperty(type=MCellStringProperty,name="Molecule Viz Name List")


class MCellPropertyGroup(bpy.types.PropertyGroup):
  mol_viz = bpy.props.PointerProperty(type=MCellMolVizProperty,name="Mol Viz Settings")
  species_list = bpy.props.CollectionProperty(type=MCellSpeciesProperty,name="Molecule List")
  active_mol_index = bpy.props.IntProperty(name="Active Molecule Index",default=0)


class MCELL_OT_molecule_add(bpy.types.Operator):
  bl_idname = "mcell.molecule_add"
  bl_label = "Add Molecule"
  bl_description = "Add a molecule type to an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.species_list.add()
    context.scene.mcell.active_mol_index = len(bpy.context.scene.mcell.species_list)-1
    return {'FINISHED'}
  
 
class MCELL_OT_molecule_remove(bpy.types.Operator):
  bl_idname = "mcell.molecule_remove"
  bl_label = "Remove Molecule"
  bl_description = "Remove a molecule type from an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    context.scene.mcell.species_list.remove(bpy.context.scene.mcell.active_mol_index)
    context.scene.mcell.active_mol_index = bpy.context.scene.mcell.active_mol_index-1
    if (context.scene.mcell.active_mol_index<0):
      context.scene.mcell.active_mol_index = 0
    return {'FINISHED'}


class MCELL_OT_set_mol_viz_dir(bpy.types.Operator):
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
    
    mc = context.scene.mcell
    if (os.path.isdir(self.filepath)):
      mol_file_dir = self.filepath
    else:
      mol_file_dir = os.path.dirname(self.filepath)
    mol_file_list = glob.glob(mol_file_dir + '/*')
    
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
      
    MolVizUpdate(context,0)
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
    mc = context.scene.mcell
    i = mc.mol_viz.mol_file_index
    if (i > mc.mol_viz.mol_file_stop_index):
      i = mc.mol_viz.mol_file_stop_index
    if (i < mc.mol_viz.mol_file_start_index):
      i = mc.mol_viz.mol_file_start_index    
    mc.mol_viz.mol_file_index = i
    MolVizUpdate(context,i)
    return('FINISHED')
  
#  def draw(self,context):
#    layout = self.layout
    
#    mc = context.scene.mcell
#    col = layout.col()
#    col.prop(mc.mol_viz,"mol_file_index",text="")
  

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
    MolVizUpdate(context,i)
    return('FINISHED')


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
    MolVizUpdate(context,i)
    return('FINISHED')


def MolVizUpdate(context,i):

  filename = context.scene.mcell.mol_viz.mol_file_list[i].name
  context.scene.mcell.mol_viz.mol_file_name = filename
  filepath = os.path.join(context.scene.mcell.mol_viz.mol_file_dir,filename) 
  
  global_undo = bpy.context.user_preferences.edit.use_global_undo
  bpy.context.user_preferences.edit.use_global_undo = False   
   
  MolVizDelete(context)
  MolVizFileRead(context,filepath)
  
  bpy.context.user_preferences.edit.use_global_undo = global_undo
  

def MolVizDelete(context):

  mc = context.scene.mcell
  bpy.ops.object.select_all(action='DESELECT')
  for mol_name in mc.mol_viz.mol_viz_list:
    bpy.ops.object.select_name(name=mol_name.name,extend=True)

  bpy.ops.object.delete()
  
  # Reset mol_viz_list to empty
  for i in range(len(mc.mol_viz.mol_viz_list)-1,-1,-1):
    mc.mol_viz.mol_viz_list.remove(i)

    
def MolVizFileRead(context,filepath):
      
  try:
    
    begin = resource.getrusage(resource.RUSAGE_SELF)[0]
    print ('Processing molecules from file:  %s' % (filepath))

    mol_data = [[s.split()[0], [float(x) for x in s.split()[1:]]] for s in open(filepath,'r').read().split('\n') if s != '']
    
    mols_obj = bpy.data.objects.get('molecules')
    if not mols_obj:
      bpy.ops.object.add()
      mols_obj = context.selected_objects[0]
      mols_obj.name = 'molecules'
      
    if len(mol_data) > 0:
      mc = context.scene.mcell
      meshes = bpy.data.meshes
      mats = bpy.data.materials
      objs = bpy.data.objects
      scn = context.scene
      scn_objs = scn.objects
      z_axis = mathutils.Vector((0.0, 0.0, 1.0))
      ident_mat = mathutils.Matrix.Translation(mathutils.Vector((0.0,0.0,0.0)))
      
      mol_dict = {}
      mol_pos = []
      mol_orient = []
    
      for n in range(len(mol_data)):
        mol_name = 'mol_%s' % (mol_data[n][0])
        if not mol_dict.get(mol_name):
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
          mol_shape_mesh_name = '%s_shape' % (mol_name)
          mol_shape_obj_name = mol_shape_mesh_name
        else:
          mol_shape_mesh_name = '%s_shape' % (mol_name)
          mol_shape_obj_name = mol_shape_mesh_name
      
#       Look-up mesh shape template and create if needed
        
        mol_shape_mesh = meshes.get(mol_shape_mesh_name)
        if not mol_shape_mesh:
          bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0, size=0.01)
          mol_shape_obj = context.active_object
          mol_shape_obj.name = mol_shape_obj_name        
          mol_shape_mesh = mol_shape_obj.data
          mol_shape_mesh.name = mol_shape_mesh_name
        else:
          mol_shape_obj = objs.get(mol_shape_obj_name)
          
      
#       Look-up material and create if needed and associate with mesh shape
        mol_mat = mats.get(mol_mat_name)
        if not mol_mat:
          mol_mat = mats.new(mol_mat_name)
          mol_mat.diffuse_color = [1.0, 0.0, 0.0]
        if not mol_shape_mesh.materials.get(mol_mat_name):
          mol_shape_mesh.materials.append(mol_mat)

#       Create mol mesh to hold molecule positions
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
        mol_obj.parent = mols_obj
      
          
    utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
    print ('   Processed %d molecules in %g seconds\n' % (len(mol_data),utime))
        
  except IOError:
    print(('\n***** File not found: %s\n') % (filepath))
  except ValueError:
    print(('\n***** Invalid data in file: %s\n') % (filepath))


def register():
  bpy.utils.register_class(MCellSpeciesProperty)
  bpy.utils.register_class(MCellStringProperty)
  bpy.utils.register_class(MCellMolVizProperty)
  bpy.utils.register_class(MCellPropertyGroup)
  bpy.types.Scene.mcell = bpy.props.PointerProperty(type=MCellPropertyGroup)
#  bpy.types.Scene.mcell.mol_viz = bpy.props.PointerProperty(type=MCellMolVizProperty)
  bpy.utils.register_class(MCELL_OT_set_mol_viz_dir)
  bpy.utils.register_class(MCELL_OT_molecule_add)
  bpy.utils.register_class(MCELL_OT_molecule_remove)
  bpy.utils.register_class(MCELL_OT_mol_viz_set_index)
  bpy.utils.register_class(MCELL_OT_mol_viz_next)
  bpy.utils.register_class(MCELL_OT_mol_viz_prev)
  bpy.utils.register_class(MCELL_PT_viz_results)
  bpy.utils.register_class(MCELL_PT_define_molecules)


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