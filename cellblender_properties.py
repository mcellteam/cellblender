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
from . import cellblender_operators


#Custom Properties

class MCellSurfaceRegionFaceProperty(bpy.types.PropertyGroup):
  index = bpy.props.IntProperty(name="Face Index")


class MCellSurfaceRegionProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Region Name",default="Region",update=cellblender_operators.check_region)
  faces = bpy.props.CollectionProperty(type=MCellSurfaceRegionFaceProperty,name="Surface Region List")
  active_face_index = bpy.props.IntProperty(name="Active Face Index",default=0)


class MCellSurfaceRegionListProperty(bpy.types.PropertyGroup):
  region_list = bpy.props.CollectionProperty(type=MCellSurfaceRegionProperty,name="Surface Region List")
  active_reg_index = bpy.props.IntProperty(name="Active Region Index",default=0)
  status = bpy.props.StringProperty(name="Status")


class MCellMoleculeProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Molecule Name",default="Molecule",update=cellblender_operators.check_molecule)
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


# Generic PropertyGroup to hold float vectors for a ColletionProperty  
class MCellFloatVectorProperty(bpy.types.PropertyGroup):
  vec = bpy.props.FloatVectorProperty(name="Float Vector")


class MCellReactionProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="The Reaction")
  rxn_name = bpy.props.StringProperty(name="Reaction Name")
  reactants = bpy.props.StringProperty(name="Reactants",update=cellblender_operators.check_reaction)
  products = bpy.props.StringProperty(name="Products",update=cellblender_operators.check_reaction)
  type_enum = [
                ('irreversible','->',''),
                ('reversible','<->','')]
  type = bpy.props.EnumProperty(items=type_enum,name="Reaction Type",update=cellblender_operators.check_reaction)
  fwd_rate = bpy.props.FloatProperty(name="Forward Rate",precision=4)
  bkwd_rate = bpy.props.FloatProperty(name="Backward Rate",precision=4)


class MCellMoleculeReleaseProperty(bpy.types.PropertyGroup):
  name = bpy.props.StringProperty(name="Site Name",default="Release_Site",update=cellblender_operators.check_release_site)
  molecule = bpy.props.StringProperty(name="Molecule")
  shape_enum = [
                ('CUBIC','Cubic',''),
                ('SPHERICAL','Spherical',''),
                ('SPHERICAL SHELL','Spherical Shell',''),
  #              ('LIST','List',''),
                ('OBJECT','Object/Region','')]
  shape = bpy.props.EnumProperty(items=shape_enum,name="Release Shape")
  object_name = bpy.props.StringProperty(name="Object/Region")
  location = bpy.props.FloatVectorProperty(name="Location",precision=4)
  diameter = bpy.props.FloatProperty(name="Site Diameter",precision=4)
  probability = bpy.props.FloatProperty(name="Release Probability",precision=4,default=1.0)
  quantity_type_enum = [
                ('NUMBER_TO_RELEASE','Constant Number',''),
                ('GAUSSIAN_RELEASE_NUMBER','Gaussian Number',''),
                ('DENSITY','Concentration/Density','')]
  quantity_type = bpy.props.EnumProperty(items=quantity_type_enum,name="Quantity Type")
  quantity = bpy.props.FloatProperty(name="Quantity to Release",precision=4)
  stddev = bpy.props.FloatProperty(name="Standard Deviation",precision=4)
  pattern = bpy.props.StringProperty(name="Release Pattern")


#Panel Properties:

class MCellProjectPanelProperty(bpy.types.PropertyGroup):
  base_name = bpy.props.StringProperty(name="Project Base Name")
  project_dir = bpy.props.StringProperty(name="Project Directory")
  export_format_enum = [
                         ('mcell_mdl_unified','Single Unified MCell MDL File',''),
                         ('mcell_mdl_modular','Modular MCell MDL Files','')]
  export_format = bpy.props.EnumProperty(items=export_format_enum,name="Export Format",default="mcell_mdl_modular")
#  export_selection_only = bpy.props.BoolProperty(name="Export Selected Objects Only",default=True)


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
  mol_viz_enable = bpy.props.BoolProperty(name="Enable Molecule Vizualization",description="Disable for faster animation preview",default=True,update=cellblender_operators.MolVizUpdate)
  color_list = bpy.props.CollectionProperty(type=MCellFloatVectorProperty,name="Molecule Color List")
  color_index = bpy.props.IntProperty(name="Color Index",default=0)


class MCellInitializationPanelProperty(bpy.types.PropertyGroup):
  iterations = bpy.props.IntProperty(name="Simulation Iterations",default=0)
  time_step = bpy.props.FloatProperty(name="Simulation Time Step",default=1e-6)


class MCellMoleculesPanelProperty(bpy.types.PropertyGroup):
  molecule_list = bpy.props.CollectionProperty(type=MCellMoleculeProperty,name="Molecule List")
  active_mol_index = bpy.props.IntProperty(name="Active Molecule Index",default=0)
  status = bpy.props.StringProperty(name="Status")


class MCellReactionsPanelProperty(bpy.types.PropertyGroup):
  reaction_list = bpy.props.CollectionProperty(type=MCellReactionProperty,name="Reaction List")
  active_rxn_index = bpy.props.IntProperty(name="Active Reaction Index",default=0)
  status = bpy.props.StringProperty(name="Status")


class MCellSurfaceClassesPanelProperty(bpy.types.PropertyGroup):
  include = bpy.props.BoolProperty(name="Include Surface Classes",description="Add INCLUDE_FILE for Surface Classes to main MDL file",default=False)


class MCellModSurfRegionsProperty(bpy.types.PropertyGroup):
  include = bpy.props.BoolProperty(name="Include Modify Surface Regions",description="Add INCLUDE_FILE for Modify Surface Regions to main MDL file",default=False)


class MCellMoleculeReleasePanelProperty(bpy.types.PropertyGroup):
  mol_release_list = bpy.props.CollectionProperty(type=MCellMoleculeReleaseProperty,name="Molecule Release List")
  active_release_index = bpy.props.IntProperty(name="Active Release Index",default=0)
  status = bpy.props.StringProperty(name="Status")


class MCellModelObjectsPanelProperty(bpy.types.PropertyGroup):
  object_list = bpy.props.CollectionProperty(type=MCellStringProperty,name="Object List")
  active_obj_index = bpy.props.IntProperty(name="Active Object Index",default=0)


class MCellVizOutputPanelProperty(bpy.types.PropertyGroup):
  include = bpy.props.BoolProperty(name="Include Viz Output",description="Add INCLUDE_FILE for Viz Output to main MDL file",default=False)


class MCellReactionOutputPanelProperty(bpy.types.PropertyGroup):
  include = bpy.props.BoolProperty(name="Include Reaction Output",description="Add INCLUDE_FILE for Reaction Output to main MDL file",default=False)


class MCellMoleculeGlyphsPanelProperty(bpy.types.PropertyGroup):
  glyph_lib = __file__.replace(__file__.split('/')[len(__file__.split('/'))-1],'')+'glyph_library.blend/Mesh/'
  glyph_enum = [
                    ('Cone','Cone',''),
                    ('Cube','Cube',''),
                    ('Cylinder','Cylinder',''),
                    ('Icosahedron','Icosahedron',''),
                    ('Octahedron','Octahedron',''),
                    ('Receptor','Receptor',''),
                    ('Sphere_1','Sphere_1',''),
                    ('Sphere_2','Sphere_2',''),
                    ('Torus','Torus','')]
  glyph = bpy.props.EnumProperty(items=glyph_enum,name="Molecule Shapes")
  status = bpy.props.StringProperty(name="Status")


class MCellMeshalyzerPanelProperty(bpy.types.PropertyGroup):
  object_name = bpy.props.StringProperty(name="Object Name")
  vertices = bpy.props.IntProperty(name="Vertices",default=0)
  edges = bpy.props.IntProperty(name="Edges",default=0)
  faces = bpy.props.IntProperty(name="Faces",default=0)
  watertight = bpy.props.StringProperty(name="Watertight")
  manifold = bpy.props.StringProperty(name="Manifold")
  normal_status = bpy.props.StringProperty(name="Surface Normals")
  area = bpy.props.FloatProperty(name="Area",default=0)
  volume = bpy.props.FloatProperty(name="Volume",default=0)
  status = bpy.props.StringProperty(name="Status")


class MCellObjectSelectorPanelProperty(bpy.types.PropertyGroup):
  filter = bpy.props.StringProperty(name="Object Name Filter")


# Main MCell (CellBlender) Properties Class:

class MCellPropertyGroup(bpy.types.PropertyGroup):
  project_settings = bpy.props.PointerProperty(type=MCellProjectPanelProperty,name="CellBlender Project Settings")
  mol_viz = bpy.props.PointerProperty(type=MCellMolVizPanelProperty,name="Mol Viz Settings")
  initialization = bpy.props.PointerProperty(type=MCellInitializationPanelProperty,name="Model Initialization")
  molecules = bpy.props.PointerProperty(type=MCellMoleculesPanelProperty,name="Defined Molecules")
  reactions = bpy.props.PointerProperty(type=MCellReactionsPanelProperty,name="Defined Reactions")
  surface_classes = bpy.props.PointerProperty(type=MCellSurfaceClassesPanelProperty,name="Defined Surface Classes")
  mod_surf_regions = bpy.props.PointerProperty(type=MCellModSurfRegionsProperty,name="Modify Surface Regions")
  release_sites = bpy.props.PointerProperty(type=MCellMoleculeReleasePanelProperty,name="Defined Release Sites")
  model_objects = bpy.props.PointerProperty(type=MCellModelObjectsPanelProperty,name="Instantiated Objects")
  viz_output = bpy.props.PointerProperty(type=MCellVizOutputPanelProperty,name="Viz Output")
  rxn_output = bpy.props.PointerProperty(type=MCellReactionOutputPanelProperty,name="Reaction Output")
  meshalyzer = bpy.props.PointerProperty(type=MCellMeshalyzerPanelProperty,name="CellBlender Project Settings")
  object_selector = bpy.props.PointerProperty(type=MCellObjectSelectorPanelProperty,name="CellBlender Project Settings")
  molecule_glyphs = bpy.props.PointerProperty(type=MCellMoleculeGlyphsPanelProperty,name="Molecule Shapes")



# CellBlender Properties Class for Objects:

class MCellObjectPropertyGroup(bpy.types.PropertyGroup):
  regions = bpy.props.PointerProperty(type=MCellSurfaceRegionListProperty,name="Defined Surface Regions")
  status = bpy.props.StringProperty(name="Status")


