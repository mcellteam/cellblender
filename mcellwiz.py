import bpy


class OBJECT_PT_VIZ_RESULTS(bpy.types.Panel):
  bl_label = "Visualize Simulation Results"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"

  def draw(self, context):
    layout = self.layout

    mc = context.scene.mcell 

    layout.prop(mc,"mol_file_path",text="Molecule File Path")
 

class OBJECT_PT_DEFINE_MOLECULES(bpy.types.Panel):
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
    mol = mc.species_list[mc.active_mol_index]
    if mol:
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
  mol_file_path = bpy.props.StringProperty(name="Molecule File Path",subtype="FILE_PATH")
  species_list = bpy.props.CollectionProperty(type=MCellSpeciesProperty,name="Molecule List")
  active_mol_index = bpy.props.IntProperty(name="Active Molecule Index",default=0)


class MCellMoleculeAdd(bpy.types.Operator):
  bl_idname = "mcell.molecule_add"
  bl_label = "Add Molecule"
  bl_description = "Add a molecule type to an MCell model"
  bl_options = {'REGISTER', 'UNDO'}
  
  def execute(self,context):
    bpy.context.scene.mcell.species_list.add()
    bpy.context.scene.mcell.active_mol_index = len(bpy.context.scene.mcell.species_list)-1
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