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


# CellBlender GUI Panels:

class MCELL_PT_project_settings(bpy.types.Panel):
  bl_label = "CellBlender Project Settings"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()
    row.operator("mcell.set_project_dir",text="Set CellBlender Project Directory",icon="FILESEL")
    row = layout.row()
    row.label(text="Project Directory: "+mc.project_settings.project_dir)
    row = layout.row()
    layout.prop(mc.project_settings,"base_name")
    layout.separator()
    row = layout.row()
    row.label(text="Export Project")
    row = layout.row()
    layout.prop(mc.project_settings,"export_format")
    row = layout.row()
    layout.prop(mc.project_settings,"export_selection_only")
    row = layout.row()
    row.operator("mcell.export_project",text="Export CellBlender Project",icon="FILESEL")



class MCELL_PT_sim_control(bpy.types.Panel):
  bl_label = "Simulation Control"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_viz_results(bpy.types.Panel):
  bl_label = "Visualize Simulation Results"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    
    mc = context.scene.mcell
    
    row=layout.row()
    row.operator("mcell.set_mol_viz_dir",text="Set Molecule Viz Directory",icon="FILESEL")
    row = layout.row()
    row.label(text="Molecule Viz Directory: "+mc.mol_viz.mol_file_dir)
    row = layout.row()
    row.label(text="Current Molecule File: "+mc.mol_viz.mol_file_name)
    row = layout.row()
    row.template_list(mc.mol_viz,"mol_file_list",mc.mol_viz,"mol_file_index",rows=2)
    row = layout.row()
    layout.prop(mc.mol_viz,"render_and_save")

#    col = row.column(align=True)
#    col.operator("mcell.mol_viz_prev",icon="PLAY_REVERSE",text="")
#    col = row.column(align=True)
#    col.operator("mcell.mol_viz_set_index",text=str(mc.mol_viz.mol_file_index))
#    col = row.column(align=True)
#    col.operator("mcell.mol_viz_next",icon="PLAY",text="")



class MCELL_PT_utilities(bpy.types.Panel):
  bl_label = "Utilities"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}

  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()
#    row.operator("mcell.vertex_groups_to_regions",text="Convert Vertex Group to Region")



class MCELL_PT_object_selector(bpy.types.Panel):
  bl_label = "Object Selector"
  bl_space_type = "VIEW_3D"
  bl_region_type = "TOOLS"
  bl_options = {'DEFAULT_CLOSED'}

  def draw(self, context):
    layout = self.layout
    scn = context.scene
    mc = context.scene.mcell
    

    layout.prop(mc.object_selector,"filter",text="Object Filter:")
    row=layout.row(align=True)
    row.operator("mcell.select_filtered",text="Select Filtered")
    row.operator("mcell.deselect_filtered",text="Deselect Filtered")



class MCELL_PT_meshalyzer(bpy.types.Panel):
  bl_label = "Mesh Analysis"
  bl_space_type = "VIEW_3D"
  bl_region_type = "TOOLS"
  bl_options = {'DEFAULT_CLOSED'}

  def draw(self, context):
    layout = self.layout
    scn = context.scene
    mc = context.scene.mcell
    
    row = layout.row()
    row.operator("mcell.meshalyzer",text="Analyze Mesh",icon="MESH_ICOSPHERE")

    if (mc.meshalyzer.status != ''):
      row = layout.row()
      row.label(text="%s" % (mc.meshalyzer.status))
    row = layout.row()
    row.label(text="Object Name: %s" % (mc.meshalyzer.object_name))
    row = layout.row()
    row.label(text="Vertices: %d" % (mc.meshalyzer.vertices))
    row = layout.row()
    row.label(text="Edges: %d" % (mc.meshalyzer.edges))
    row = layout.row()
    row.label(text="Faces: %d" % (mc.meshalyzer.faces))
    row = layout.row()
    row.label(text="Surface Area: %.5g" % (mc.meshalyzer.area))
    row = layout.row()
    row.label(text="Volume: %.5g" % (mc.meshalyzer.volume))

    row = layout.row()
    row.label(text="Mesh Topology:")
    row = layout.row()
    row.label(text="      %s" % (mc.meshalyzer.watertight))
    row = layout.row()
    row.label(text="      %s" % (mc.meshalyzer.manifold))
    row = layout.row()
    row.label(text="      %s" % (mc.meshalyzer.normal_status))



class MCELL_PT_user_model_parameters(bpy.types.Panel):
  bl_label = "User-Defined Model Parameters"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_initialization(bpy.types.Panel):
  bl_label = "MCell Model Initialization"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_define_molecules(bpy.types.Panel):
  bl_label = "Define Molecules"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    
    mc = context.scene.mcell
    
    row = layout.row()
    row.label(text="Defined Molecules:", icon='FORCE_LENNARDJONES')
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



class MCELL_PT_define_reactions(bpy.types.Panel):
  bl_label = "Define Reactions"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row = layout.row()
    row.label(text="Defined Reactions:", icon='FORCE_LENNARDJONES')
    row = layout.row()
    col = row.column()
    col.template_list(mc.reactions,"reaction_list",mc.reactions,"active_rxn_index",rows=2)
    col = row.column(align=True)
    col.operator("mcell.reaction_add",icon='ZOOMIN',text="")
    col.operator("mcell.reaction_remove",icon='ZOOMOUT',text="")
    if len(mc.reactions.reaction_list)>0:
      rxn = mc.reactions.reaction_list[mc.reactions.active_rxn_index]
      layout.prop(rxn,"reactants")
      layout.prop(rxn,"type")
      layout.prop(rxn,"products")
      layout.prop(rxn,"fwd_rate")
      if rxn.type == "reversible":
        layout.prop(rxn,"bkwd_rate")
      layout.prop(rxn,"rxn_name")



class MCELL_PT_define_surface_classes(bpy.types.Panel):
  bl_label = "Define Surface Classes"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_molecule_placement(bpy.types.Panel):
  bl_label = "Molecule Placement"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_reaction_output_settings(bpy.types.Panel):
  bl_label = "Reaction Output Settings"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_visualization_output_settings(bpy.types.Panel):
  bl_label = "Visualization Output Settings"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    mc = context.scene.mcell
    
    row=layout.row()



class MCELL_PT_model_objects(bpy.types.Panel):
  bl_label = "Model Objects"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    
    mc = context.scene.mcell
    
    row = layout.row()
    row.label(text="Model Objects:", icon='MESH_ICOSPHERE')
    row = layout.row()
    col = row.column()
    col.template_list(mc.model_objects,"object_list",mc.model_objects,"active_obj_index",rows=2)
    col = row.column(align=True)
    col.operator("mcell.model_objects_remove",icon='ZOOMOUT',text="")
    row = layout.row()
    sub = row.row(align=True)
    sub.operator("mcell.model_objects_include",text="Include")
#    sub = row.row(align=True)
#    sub.operator("mcell.model_objects_select",text="Select")
#    sub.operator("mcell.model_objects_deselect",text="Deselect")



class MCELL_PT_define_surface_regions(bpy.types.Panel):
  bl_label = "Define Surface Regions"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "object"
  bl_options = {'DEFAULT_CLOSED'}
  
  def draw(self, context):
    layout = self.layout
    
    obj_regs = context.object.mcell.regions
    aobj = context.active_object
    
    row = layout.row()
    row.label(text="Defined Regions:", icon='FORCE_LENNARDJONES')
    row = layout.row()
    col = row.column()
    col.template_list(obj_regs,"region_list",obj_regs,"active_reg_index",rows=2)
    col = row.column(align=True)
    col.operator("mcell.region_add",icon='ZOOMIN',text="")
    col.operator("mcell.region_remove",icon='ZOOMOUT',text="")
    row = layout.row()
    if len(obj_regs.region_list)>0:
      reg = obj_regs.region_list[obj_regs.active_reg_index]
      layout.prop(reg,"name")
    if aobj.mode == 'EDIT':
      row = layout.row()
      sub = row.row(align=True)
      sub.operator("mcell.region_faces_assign",text="assign")
      sub.operator("mcell.region_faces_remove",text="remove")
      sub = row.row(align=True)
      sub.operator("mcell.region_faces_select",text="select")
      sub.operator("mcell.region_faces_deselect",text="deselect")



class MCELL_PT_molecule_glyphs(bpy.types.Panel):
  bl_label = "Molecule Shape"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "material"
  bl_options = {'DEFAULT_CLOSED'}

  def draw(self, context):
    layout = self.layout
    scn = context.scene
    mc = context.scene.mcell


    row = layout.row()
    layout.prop(mc.molecule_glyphs,"glyph")

    if (mc.molecule_glyphs.status != ''):
      row = layout.row()
      row.label(text="%s" % (mc.molecule_glyphs.status))

    row = layout.row()
    row.operator("mcell.set_molecule_glyph",text="Set Molecule Shape",icon="MESH_ICOSPHERE")

