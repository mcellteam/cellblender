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

"""
This script contains the custom properties used in CellBlender.

"""


import bpy
from . import cellblender_operators
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, IntProperty, PointerProperty, StringProperty


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#Custom Properties
class MCellSurfaceRegionFaceProperty(bpy.types.PropertyGroup):
    index = IntProperty(name="Face Index")


class MCellSurfaceRegionProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Region Name", default="Region",
        update=cellblender_operators.check_region)
    faces = CollectionProperty(
        type=MCellSurfaceRegionFaceProperty, name="Surface Region List")
    active_face_index = IntProperty(name="Active Face Index", default=0)


class MCellSurfaceRegionListProperty(bpy.types.PropertyGroup):
    region_list = CollectionProperty(
        type=MCellSurfaceRegionProperty, name="Surface Region List")
    active_reg_index = IntProperty(name="Active Region Index", default=0)
    status = StringProperty(name="Status")


class MCellMoleculeProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Molecule Name", default="Molecule",
        update=cellblender_operators.check_molecule)
    type_enum = [
        ('2D', 'Surface Molecule', ''),
        ('3D', 'Volume Molecule', '')]
    type = EnumProperty(items=type_enum, name="Molecule Type")
    diffusion_constant = FloatProperty(name="Diffusion Constant")
    diffusion_constant_str = StringProperty(
        name="Diffusion Constant",
        description="Diffusion Constant Units: cm^2/sec",
        update=cellblender_operators.update_diffusion_constant)
    target_only = BoolProperty(name="Target Only")
    custom_time_step = FloatProperty(name="Custom Time Step")
    custom_time_step_str = StringProperty(
        name="Custom Time Step",
        description="Custom Time Step Units: seconds",
        update=cellblender_operators.update_custom_time_step)
    custom_space_step = FloatProperty(name="Custom Space Step")
    custom_space_step_str = StringProperty(
        name="Custom Space Step",
        description="Custom Space Step Units: microns",
        update=cellblender_operators.update_custom_space_step)


class MCellStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")


class MCellFloatVectorProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold float vector for a CollectionProperty """
    vec = bpy.props.FloatVectorProperty(name="Float Vector")


class MCellReactionProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="The Reaction")
    rxn_name = StringProperty(name="Reaction Name")
    reactants = StringProperty(
        name="Reactants", update=cellblender_operators.check_reaction)
    products = StringProperty(
        name="Products", update=cellblender_operators.check_reaction)
    type_enum = [
        ('irreversible', '->', ''),
        ('reversible', '<->', '')]
    type = EnumProperty(
        items=type_enum, name="Reaction Type",
        update=cellblender_operators.check_reaction)
    fwd_rate = FloatProperty(name="Forward Rate")
    fwd_rate_str = StringProperty(
        name="Forward Rate",
        description="Forward Rate Units: sec^-1 (unimolecular), M^-1*sec^-1 (bimolecular)",
        update=cellblender_operators.update_fwd_rate)
    bkwd_rate = FloatProperty(name="Backward Rate")
    bkwd_rate_str = StringProperty(
        name="Backward Rate",
        description="Backward Rate Units: sec^-1 (unimolecular), M^-1*sec^-1 (bimolecular)",
        update=cellblender_operators.update_bkwd_rate)


class MCellMoleculeReleaseProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Site Name", default="Release_Site",
        update=cellblender_operators.check_release_site)
    molecule = StringProperty(
        name="Molecule", update=cellblender_operators.check_release_molecule)
    shape_enum = [
        ('CUBIC', 'Cubic', ''),
        ('SPHERICAL', 'Spherical', ''),
        ('SPHERICAL SHELL', 'Spherical Shell', ''),
        #('LIST', 'List', ''),
        ('OBJECT', 'Object/Region', '')]
    shape = EnumProperty(items=shape_enum, name="Release Shape")
    object_expr = StringProperty(
        name="Object/Region",
        update=cellblender_operators.check_release_object_expr)
    location = bpy.props.FloatVectorProperty(name="Location", precision=4)
    diameter = FloatProperty(name="Site Diameter", precision=4, min=0.0)
    probability = FloatProperty(name="Release Probability", precision=4,
                                default=1.0, min=0.0, max=1.0)
    quantity_type_enum = [
        ('NUMBER_TO_RELEASE', 'Constant Number', ''),
        ('GAUSSIAN_RELEASE_NUMBER', 'Gaussian Number', ''),
        ('DENSITY', 'Concentration/Density', '')]
    quantity_type = EnumProperty(items=quantity_type_enum,
                                 name="Quantity Type")
    quantity = FloatProperty(name="Quantity to Release", precision=4, min=0.0)
    stddev = FloatProperty(name="Standard Deviation", precision=4, min=0.0)
    pattern = StringProperty(name="Release Pattern")


class MCellSurfaceClassPropertiesProperty(bpy.types.PropertyGroup):

    """ This is where properties for a given surface class are stored.

    All of the properties here ultimately get converted into something like the
    following: ABSORPTIVE = Molecule' or REFLECTIVE = Molecule;
    Each instance is only one set of properties for a surface class that may
    have many sets of properties.

    """

    name = StringProperty(name="Molecule", default="Molecule")
    molecule = StringProperty(
        name="Molecule Name:",
        update=cellblender_operators.check_surf_class_props)
    surf_class_orient_enum = [
        ("'", 'Top/Front', ''),
        (",", 'Bottom/Back', ''),
        (";", 'Ignore', '')]
    surf_class_orient = EnumProperty(
        items=surf_class_orient_enum, name="Orientation",
        update=cellblender_operators.check_surf_class_props)
    surf_class_type_enum = [
        ('ABSORPTIVE', 'Absorptive', ''),
        ('TRANSPARENT', 'Transparent', ''),
        ('REFLECTIVE', 'Reflective', ''),
        ('CLAMP_CONCENTRATION', 'Clamp Concentration', '')]
    surf_class_type = EnumProperty(
        items=surf_class_type_enum, name="Type",
        update=cellblender_operators.check_surf_class_props)
    clamp_value = FloatProperty(name="Value", precision=4, min=0.0)
    clamp_value_str = StringProperty(
        name="Value", description="Concentration Units: Molar",
        update=cellblender_operators.update_clamp_value)


class MCellSurfaceClassesProperty(bpy.types.PropertyGroup):
    """ Stores the surface class name and a list of its properties. """

    name = StringProperty(
        name="Surface Class Name", default="Surface_Class",
        update=cellblender_operators.check_surface_class)
    surf_class_props_list = CollectionProperty(
        type=MCellSurfaceClassPropertiesProperty, name="Surface Classes List")
    active_surf_class_props_index = IntProperty(
        name="Active Surface Class Index", default=0)


class MCellModSurfRegionsProperty(bpy.types.PropertyGroup):
    """ Assign a surface class to a surface region. """

    name = StringProperty(name="Surface Class Name", default="Surface_Class")
    surf_class_name = StringProperty(
        name="Surface Class Name:",
        update=cellblender_operators.check_assigned_surface_class)
    object_name = StringProperty(
        name="Object Name:",
        update=cellblender_operators.check_assigned_object)
    region_name = StringProperty(
        name="Region Name:",
        update=cellblender_operators.check_modified_region)


#Panel Properties:

class MCellProjectPanelProperty(bpy.types.PropertyGroup):
    base_name = StringProperty(name="Project Base Name")
    project_dir = StringProperty(name="Project Directory")
    export_format_enum = [
        ('mcell_mdl_unified', 'Single Unified MCell MDL File', ''),
        ('mcell_mdl_modular', 'Modular MCell MDL Files', '')]
    export_format = EnumProperty(items=export_format_enum,
                                 name="Export Format",
                                 default="mcell_mdl_modular")
#    export_selection_only = BoolProperty(name="Export Selected Objects Only",
#                                         default=True)


class MCellMolVizPanelProperty(bpy.types.PropertyGroup):
    """ Property group for for molecule visualization.

    This is the "Visualize Simulation Results Panel".

    """

    mol_file_dir = StringProperty(
        name="Molecule File Dir", subtype="NONE")
    mol_file_list = CollectionProperty(
        type=MCellStringProperty, name="Molecule File Name List")
    mol_file_num = IntProperty(
        name="Number of Molecule Files", default=0)
    mol_file_name = StringProperty(
        name="Current Molecule File Name", subtype="NONE")
    mol_file_index = IntProperty(name="Current Molecule File Index", default=0)
    mol_file_start_index = IntProperty(
        name="Molecule File Start Index", default=0)
    mol_file_stop_index = IntProperty(
        name="Molecule File Stop Index", default=0)
    mol_file_step_index = IntProperty(
        name="Molecule File Step Index", default=1)
    mol_viz_list = CollectionProperty(
        type=MCellStringProperty, name="Molecule Viz Name List")
    render_and_save = BoolProperty(name="Render & Save Images")
    mol_viz_enable = BoolProperty(
        name="Enable Molecule Vizualization",
        description="Disable for faster animation preview",
        default=True, update=cellblender_operators.MolVizUpdate)
    color_list = CollectionProperty(
        type=MCellFloatVectorProperty, name="Molecule Color List")
    color_index = IntProperty(name="Color Index", default=0)


class MCellInitializationPanelProperty(bpy.types.PropertyGroup):
    iterations = IntProperty(
        name="Simulation Iterations",
        description="Number of Iterations to Run",
        default=0, min=0)
    time_step = FloatProperty(name="Time Step", default=1e-6, min=0.0)
    time_step_str = StringProperty(
        name="Time Step", default="1e-6",
        description="Simulation Time Step Units: seconds",
        update=cellblender_operators.update_time_step)
    status = StringProperty(name="Status")


class MCellMoleculesPanelProperty(bpy.types.PropertyGroup):
    molecule_list = CollectionProperty(
        type=MCellMoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    status = StringProperty(name="Status")


class MCellReactionsPanelProperty(bpy.types.PropertyGroup):
    reaction_list = CollectionProperty(
        type=MCellReactionProperty, name="Reaction List")
    active_rxn_index = IntProperty(name="Active Reaction Index", default=0)
    status = StringProperty(name="Status")


class MCellSurfaceClassesPanelProperty(bpy.types.PropertyGroup):
    surf_class_list = CollectionProperty(
        type=MCellSurfaceClassesProperty, name="Surface Classes List")
    active_surf_class_index = IntProperty(
        name="Active Surface Class Index", default=0)
    surf_class_status = StringProperty(name="Status")
    surf_class_props_status = StringProperty(name="Status")


class MCellModSurfRegionsPanelProperty(bpy.types.PropertyGroup):
    mod_surf_regions_list = CollectionProperty(
        type=MCellModSurfRegionsProperty, name="Modify Surface Region List")
    active_mod_surf_regions_index = IntProperty(
        name="Active Modify Surface Region Index", default=0)
    status = StringProperty(name="Status")


class MCellMoleculeReleasePanelProperty(bpy.types.PropertyGroup):
    mol_release_list = CollectionProperty(
        type=MCellMoleculeReleaseProperty, name="Molecule Release List")
    active_release_index = IntProperty(name="Active Release Index", default=0)
    status = StringProperty(name="Status")


class MCellModelObjectsPanelProperty(bpy.types.PropertyGroup):
    object_list = CollectionProperty(
        type=MCellStringProperty, name="Object List")
    active_obj_index = IntProperty(name="Active Object Index", default=0)


class MCellVizOutputPanelProperty(bpy.types.PropertyGroup):
    include = BoolProperty(
        name="Include Viz Output",
        description="Add INCLUDE_FILE for Viz Output to main MDL file",
        default=False)


class MCellReactionOutputPanelProperty(bpy.types.PropertyGroup):
    include = BoolProperty(
        name="Include Reaction Output",
        description="Add INCLUDE_FILE for Reaction Output to main MDL file",
        default=False)


class MCellMoleculeGlyphsPanelProperty(bpy.types.PropertyGroup):
    glyph_lib = __file__.replace(__file__.split('/')[len(__file__.split('/'))-1], '')+'glyph_library.blend/Mesh/'
    glyph_enum = [
        ('Cone', 'Cone', ''),
        ('Cube', 'Cube', ''),
        ('Cylinder', 'Cylinder', ''),
        ('Icosahedron', 'Icosahedron', ''),
        ('Octahedron', 'Octahedron', ''),
        ('Receptor', 'Receptor', ''),
        ('Sphere_1', 'Sphere_1', ''),
        ('Sphere_2', 'Sphere_2', ''),
        ('Torus', 'Torus', '')]
    glyph = EnumProperty(items=glyph_enum, name="Molecule Shapes")
    status = StringProperty(name="Status")


class MCellMeshalyzerPanelProperty(bpy.types.PropertyGroup):
    object_name = StringProperty(name="Object Name")
    vertices = IntProperty(name="Vertices", default=0)
    edges = IntProperty(name="Edges", default=0)
    faces = IntProperty(name="Faces", default=0)
    watertight = StringProperty(name="Watertight")
    manifold = StringProperty(name="Manifold")
    normal_status = StringProperty(name="Surface Normals")
    area = FloatProperty(name="Area", default=0)
    volume = FloatProperty(name="Volume", default=0)
    status = StringProperty(name="Status")


class MCellObjectSelectorPanelProperty(bpy.types.PropertyGroup):
    filter = StringProperty(name="Object Name Filter")


# Main MCell (CellBlender) Properties Class:

class MCellPropertyGroup(bpy.types.PropertyGroup):
    project_settings = PointerProperty(
        type=MCellProjectPanelProperty, name="CellBlender Project Settings")
    mol_viz = PointerProperty(
        type=MCellMolVizPanelProperty, name="Mol Viz Settings")
    initialization = PointerProperty(
        type=MCellInitializationPanelProperty, name="Model Initialization")
    molecules = PointerProperty(
        type=MCellMoleculesPanelProperty, name="Defined Molecules")
    reactions = PointerProperty(
        type=MCellReactionsPanelProperty, name="Defined Reactions")
    surface_classes = PointerProperty(
        type=MCellSurfaceClassesPanelProperty, name="Defined Surface Classes")
    mod_surf_regions = PointerProperty(
        type=MCellModSurfRegionsPanelProperty, name="Modify Surface Regions")
    release_sites = PointerProperty(
        type=MCellMoleculeReleasePanelProperty, name="Defined Release Sites")
    model_objects = PointerProperty(
        type=MCellModelObjectsPanelProperty, name="Instantiated Objects")
    viz_output = PointerProperty(
        type=MCellVizOutputPanelProperty, name="Viz Output")
    rxn_output = PointerProperty(
        type=MCellReactionOutputPanelProperty, name="Reaction Output")
    meshalyzer = PointerProperty(
        type=MCellMeshalyzerPanelProperty, name="CellBlender Project Settings")
    object_selector = PointerProperty(
        type=MCellObjectSelectorPanelProperty,
        name="CellBlender Project Settings")
    molecule_glyphs = PointerProperty(
        type=MCellMoleculeGlyphsPanelProperty, name="Molecule Shapes")


# CellBlender Properties Class for Objects:

class MCellObjectPropertyGroup(bpy.types.PropertyGroup):
    regions = PointerProperty(
        type=MCellSurfaceRegionListProperty, name="Defined Surface Regions")
    status = StringProperty(name="Status")
