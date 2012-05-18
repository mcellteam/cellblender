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


bl_info = {
    "name": "CellBlender",
    "author": "Tom Bartol",
    "version": (0,1,'rev_47'),
    "blender": (2, 6, 2),
    "api": 44136,
    "location": "Properties > Scene > CellBlender Panel",
    "description": "CellBlender Modeling System for MCell",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "",
    "category": "Cell Modeling"
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
  import imp
  imp.reload(cellblender_properties)
  imp.reload(cellblender_panels)
  imp.reload(cellblender_operators)
  imp.reload(io_mesh_mcell_mdl)
else:
  from . import cellblender_properties, cellblender_panels, cellblender_operators, io_mesh_mcell_mdl


import bpy


# See notes below


def register():

#  glyph_lib = bpy.utils.script_paths()[0]+'/addons/cellblender/glyph_library.blend/Mesh/'
#  bpy.ops.wm.link_append(directory=glyph_lib,link=False,files=[{'name': new_glyph_name}]) 
 
  bpy.utils.register_class(io_mesh_mcell_mdl.ImportMCellMDL)
  bpy.utils.register_class(io_mesh_mcell_mdl.ExportMCellMDL)
  bpy.types.INFO_MT_file_import.append(io_mesh_mcell_mdl.menu_func_import)
  bpy.types.INFO_MT_file_export.append(io_mesh_mcell_mdl.menu_func_export)

  bpy.utils.register_class(cellblender_properties.MCellMoleculeProperty)
  bpy.utils.register_class(cellblender_properties.MCellReactionProperty)
  bpy.utils.register_class(cellblender_properties.MCellMoleculeReleaseProperty)
  bpy.utils.register_class(cellblender_properties.MCellStringProperty)
  bpy.utils.register_class(cellblender_properties.MCellFloatVectorProperty)
  bpy.utils.register_class(cellblender_properties.MCellProjectPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellMolVizPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellInitializationPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellMoleculesPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellReactionsPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellSurfaceClassesPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellModSurfRegionsProperty)
  bpy.utils.register_class(cellblender_properties.MCellMoleculeReleasePanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellMeshalyzerPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellModelObjectsPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellVizOutputPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellReactionOutputPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellObjectSelectorPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellMoleculeGlyphsPanelProperty)
  bpy.utils.register_class(cellblender_properties.MCellPropertyGroup)

  bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender_properties.MCellPropertyGroup)

  bpy.utils.register_class(cellblender_properties.MCellSurfaceRegionFaceProperty)
  bpy.utils.register_class(cellblender_properties.MCellSurfaceRegionProperty)
  bpy.utils.register_class(cellblender_properties.MCellSurfaceRegionListProperty)
  bpy.utils.register_class(cellblender_properties.MCellObjectPropertyGroup)

  bpy.types.Object.mcell = bpy.props.PointerProperty(type=cellblender_properties.MCellObjectPropertyGroup)

  bpy.utils.register_class(cellblender_operators.MCELL_OT_set_project_dir)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_export_project)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_set_mol_viz_dir)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_region_add)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_region_remove)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_region_faces_assign)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_region_faces_remove)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_region_faces_select)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_region_faces_deselect)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_molecule_add)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_molecule_remove)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_reaction_add)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_reaction_remove)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_release_site_add)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_release_site_remove)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_mol_viz_set_index)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_mol_viz_next)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_mol_viz_prev)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_model_objects_add)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_model_objects_remove)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_vertex_groups_to_regions)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_meshalyzer)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_select_filtered)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_deselect_filtered)
  bpy.utils.register_class(cellblender_operators.MCELL_OT_set_molecule_glyph)

  bpy.utils.register_class(cellblender_panels.MCELL_PT_project_settings)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_model_objects)
#  bpy.utils.register_class(cellblender_panels.MCELL_PT_sim_control)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_viz_results)
#  bpy.utils.register_class(cellblender_panels.MCELL_PT_utilities)
#  bpy.utils.register_class(cellblender_panels.MCELL_PT_user_model_parameters)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_initialization)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_define_molecules)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_define_reactions)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_define_surface_classes)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_molecule_release)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_reaction_output_settings)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_visualization_output_settings)

  bpy.utils.register_class(cellblender_panels.MCELL_PT_define_surface_regions)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_molecule_glyphs)

  bpy.utils.register_class(cellblender_panels.MCELL_PT_meshalyzer)
  bpy.utils.register_class(cellblender_panels.MCELL_PT_object_selector)


def unregister():
#  del bpy.types.Scene.mcell
  pass
      

if len(bpy.app.handlers.frame_change_pre) == 0:
  bpy.app.handlers.frame_change_pre.append(cellblender_operators.frame_change_handler)

if __name__ == '__main__':
  register()
#  bpy.app.handlers.frame_change_pre.append(frame_change_handler)
#  bpy.app.handlers.render_pre.append(render_handler)
#  bpy.app.handlers.render_pre.append(frame_change_handler)

#def register():
#    bpy.utils.register_module(__name__)
#
#    bpy.types.INFO_MT_file_import.append(menu_func_import)
#    bpy.types.INFO_MT_file_export.append(menu_func_export)


#def unregister():
#    bpy.utils.unregister_module(__name__)
#
#    bpy.types.INFO_MT_file_import.remove(menu_func_import)
#    bpy.types.INFO_MT_file_export.remove(menu_func_export)



# Notes:
#   template_list takes a CollectionProperty and active index as input
#     "name" member of each item in the collection is shown in the GUI
#     the item specified by active index is highlighted

#   Turn off global undo for better performance and atomic operation of sequence of operators:
#     bpy.context.user_preferences.edit.use_global_undo = False
#     ...
#     bpy.context.user_preferences.edit.use_global_undo = True
