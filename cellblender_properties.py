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


#Custom Properties

class MCellSurfaceRegionFaceProperty(bpy.types.PropertyGroup):
  index = bpy.props.IntProperty(name="Face Index")


class MCellSurfaceRegionProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Region Name")
  faces = bpy.props.CollectionProperty(type=MCellSurfaceRegionFaceProperty,name="Surface Region List")
  active_face_index = bpy.props.IntProperty(name="Active Face Index",default=0)


class MCellSurfaceRegionListProperty(bpy.types.PropertyGroup):
  region_list = bpy.props.CollectionProperty(type=MCellSurfaceRegionProperty,name="Surface Region List")
  active_reg_index = bpy.props.IntProperty(name="Active Region Index",default=0)


class MCellSpeciesProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Molecule Name")
  type_enum = [
                    ('2D','Surface Molecule',''),
                    ('3D','Volume Molecule','')]
  type = bpy.props.EnumProperty(items=type_enum,name="Molecule Type")
  diffusion_constant = bpy.props.FloatProperty(name="Diffusion Constant",precision=4)
  target_only = bpy.props.BoolProperty(name="Target Only")
  custom_time_step = bpy.props.FloatProperty(name="Custom Time Step")
  custom_space_step = bpy.props.FloatProperty(name="Custom Space Step")
  

# Generic PropertyGroup to hold strings for a ColletionProperty  
class MCellStringProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Text")


class MCellReactionProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="The Reaction")
  rxn_name = bpy.props.StringProperty(name="Reaction Name")
  reactants = bpy.props.StringProperty(name="Reactants")
  products = bpy.props.StringProperty(name="Products")
  type_enum = [
                ('irreversible','->',''),
                ('reversible','<->','')]
  type = bpy.props.EnumProperty(items=type_enum,name="Reaction Type")
  fwd_rate = bpy.props.FloatProperty(name="Forward Rate",precision=4)
  bkwd_rate = bpy.props.FloatProperty(name="Backward Rate",precision=4)


#Panel Properties:

class MCellProjectPanelProperty(bpy.types.PropertyGroup):
  base_name = bpy.props.StringProperty(name="Project Base Name")
  project_dir = bpy.props.StringProperty(name="Project Directory")
  export_format_enum = [
                         ('mcell_mdl','MCell MDL Format','')]
  export_format = bpy.props.EnumProperty(items=export_format_enum,name="Export Format",default="mcell_mdl")
  export_selection_only = bpy.props.BoolProperty(name="Export Selected Objects Only",default=True)


# Property group for for molecule visualization (Visualize Simulation Results Panel)
class MCellMolVizPanelProperty(bpy.types.PropertyGroup):
  mol_file_dir = bpy.props.StringProperty(name="Molecule File Dir",subtype="NONE")
  mol_file_list = bpy.props.CollectionProperty(type=MCellStringProperty,name="Molecule File Name List")
  mol_file_num = bpy.props.IntProperty(name="Number of Molecule Files",default=0)
  mol_file_name = bpy.props.StringProperty(name="Current Molecule File Name",subtype="NONE")
  mol_file_index = bpy.props.IntProperty(name="Current Molecule File Index",default=0)
  mol_file_start_index = bpy.props.IntProperty(name="Molecule File Start Index",default=0)
  mol_file_stop_index = bpy.props.IntProperty(name="Molecule File Stop Index",default=0)
  mol_file_step_index = bpy.props.IntProperty(name="Molecule File Step Index",default=1)
  mol_viz_list = bpy.props.CollectionProperty(type=MCellStringProperty,name="Molecule Viz Name List")
  render_and_save = bpy.props.BoolProperty(name="Render & Save Images")


class MCellReactionsPanelProperty(bpy.types.PropertyGroup):
  reaction_list = bpy.props.CollectionProperty(type=MCellReactionProperty,name="Reaction List")
  active_rxn_index = bpy.props.IntProperty(name="Active Reaction Index",default=0)


class MCellModelObjectsPanelProperty(bpy.types.PropertyGroup):
  object_list = bpy.props.CollectionProperty(type=MCellStringProperty,name="Object List")
  active_obj_index = bpy.props.IntProperty(name="Active Object Index",default=0)


class MCellMeshalyzerPanelProperty(bpy.types.PropertyGroup):
  status = bpy.props.StringProperty(name="Status")
  object_name = bpy.props.StringProperty(name="Object Name")
  vertices = bpy.props.IntProperty(name="Vertices",default=0)
  edges = bpy.props.IntProperty(name="Edges",default=0)
  faces = bpy.props.IntProperty(name="Faces",default=0)
  watertight = bpy.props.StringProperty(name="Watertight")
  manifold = bpy.props.StringProperty(name="Manifold")
  normal_status = bpy.props.StringProperty(name="Surface Normals")
  area = bpy.props.FloatProperty(name="Area",default=0)
  volume = bpy.props.FloatProperty(name="Volume",default=0)


class MCellObjectSelectorPanelProperty(bpy.types.PropertyGroup):
  filter = bpy.props.StringProperty(name="Object Name Filter")


# Main MCell (CellBlender) Properties Class:

class MCellPropertyGroup(bpy.types.PropertyGroup):
  # Note: should add one pointer property slot per GUI panel (like mol_viz).  Right now species list
  #   and active_mol_index are exposed here but should be grouped in a PropertyGroup.
  project_settings = bpy.props.PointerProperty(type=MCellProjectPanelProperty,name="CellBlender Project Settings")
  meshalyzer = bpy.props.PointerProperty(type=MCellMeshalyzerPanelProperty,name="CellBlender Project Settings")
  object_selector = bpy.props.PointerProperty(type=MCellObjectSelectorPanelProperty,name="CellBlender Project Settings")
  mol_viz = bpy.props.PointerProperty(type=MCellMolVizPanelProperty,name="Mol Viz Settings")
  species_list = bpy.props.CollectionProperty(type=MCellSpeciesProperty,name="Molecule List")
  active_mol_index = bpy.props.IntProperty(name="Active Molecule Index",default=0)
  reactions = bpy.props.PointerProperty(type=MCellReactionsPanelProperty,name="Defined Reactions")
  model_objects = bpy.props.PointerProperty(type=MCellModelObjectsPanelProperty,name="Defined Reactions")



# CellBlender Properties Class for Objects:

class MCellObjectPropertyGroup(bpy.types.PropertyGroup):
  regions = bpy.props.PointerProperty(type=MCellSurfaceRegionListProperty,name="Defined Surface Regions")


