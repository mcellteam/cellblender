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
# blender imports
import bpy
from . import cellblender_operators
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, PointerProperty, StringProperty

print ( "Importing cellblender_parameters inside cellblender_properties.py" )
from . import cellblender_parameters
print ( "Done importing cellblender_parameters inside cellblender_properties.py" )
from . import cellblender_molecules


# python imports
from multiprocessing import cpu_count


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#Custom Properties

class MCellStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")


class MCellFloatVectorProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold float vector for a CollectionProperty """
    vec = bpy.props.FloatVectorProperty(name="Float Vector")


######################## The definitions of MCellParameterProperty and MCellGeneralParameterProperty were here ########################


class MCellReactionProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="The Reaction")
    rxn_name = StringProperty(
        name="Reaction Name",
        description="The name of the reaction. "
                    "Can be used in Reaction Output.",
        update=cellblender_operators.update_reaction_name_list)
    reactants = StringProperty(
        name="Reactants", 
        description="Specify 1-3 reactants separated by a + symbol. "
                    "Optional: end with @ surface class. Ex: a; + b; @ sc;",
        update=cellblender_operators.check_reaction)
    products = StringProperty(
        name="Products",
        description="Specify zero(NULL) or more products separated by a + "
                    "symbol.",
        update=cellblender_operators.check_reaction)
    type_enum = [
        ('irreversible', "->", ""),
        ('reversible', "<->", "")]
    type = EnumProperty(
        items=type_enum, name="Reaction Type",
        description="A unidirectional/irreversible(->) reaction or a "
                    "bidirectional/reversible(<->) reaction.",
        update=cellblender_operators.check_reaction)
    fwd_rate = FloatProperty(name="Forward Rate")
    fwd_rate_str = StringProperty(
        name="Forward Rate",
        default="0",
        description="Forward Rate Units: sec^-1 (unimolecular),"
                    " M^-1*sec^-1 (bimolecular)",
        update=cellblender_operators.update_fwd_rate)
    fwd_rate_expr = StringProperty(    # DB: This property is added so that the rate laws (forward rate constants) take expressions 
        name="Forward Rate",
        default="0",
        description="Forward Rate Units: sec^-1 (unimolecular),"
                    " M^-1*sec^-1 (bimolecular)")
    bkwd_rate = FloatProperty(name="Backward Rate")
    bkwd_rate_str = StringProperty(
        name="Backward Rate",
        description="Backward Rate Units: sec^-1 (unimolecular),"
                    " M^-1*sec^-1 (bimolecular)",
        update=cellblender_operators.update_bkwd_rate)
    status = StringProperty(name="Status")


class MCellMoleculeReleaseProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Site Name", default="Release_Site",
        description="The name of the release site",
        update=cellblender_operators.check_release_site)
    molecule = StringProperty(
        name="Molecule",
        description="The molecule to release",
        update=cellblender_operators.check_release_site)
    shape_enum = [
        ('CUBIC', 'Cubic', ''),
        ('SPHERICAL', 'Spherical', ''),
        ('SPHERICAL SHELL', 'Spherical Shell', ''),
        #('LIST', 'List', ''),
        ('OBJECT', 'Object/Region', '')]
    shape = EnumProperty(
        items=shape_enum, name="Release Shape",
        description="Release in the specified shape. Surface molecules can "
                    "only use Object/Region.",
                    update=cellblender_operators.check_release_site)
    orient_enum = [
        ('\'', "Top Front", ""),
        (',', "Top Back", ""),
        (';', "Mixed", "")]
    orient = bpy.props.EnumProperty(
        items=orient_enum, name="Initial Orientation",
        description="Release surface molecules with the specified initial "
                    "orientation.")
    object_expr = StringProperty(
        name="Object/Region",
        description="Release in/on the specified object/region.",
        update=cellblender_operators.check_release_site)
    location = bpy.props.FloatVectorProperty(
        name="Location", precision=4,
        description="The center of the release site specified by XYZ "
                    "coordinates")
    diameter = FloatProperty(
        name="Site Diameter", precision=4, min=0.0,
        description="Release molecules uniformly within the specified "
                    "diameter.")
    probability = FloatProperty(
        name="Release Probability", precision=4,
        description="Release does not occur every time, "
                    "but rather with specified probability.",
        default=1.0, min=0.0, max=1.0)
    quantity_type_enum = [
        ('NUMBER_TO_RELEASE', "Constant Number", ""),
        ('GAUSSIAN_RELEASE_NUMBER', "Gaussian Number", ""),
        ('DENSITY', "Concentration/Density", "")]
    quantity_type = EnumProperty(items=quantity_type_enum,
                                 name="Quantity Type")
    quantity = FloatProperty(
        name="Quantity to Release", precision=4, min=0.0,
        description="Concentration units: molar. Density units: molecules per "
                    "square micron")
    quantity_expr = StringProperty(name="Quantity to Release",default="0")  ####### DB: added to include expressions for imported quantities ###
    stddev = FloatProperty(name="Standard Deviation", precision=4, min=0.0)
    pattern = StringProperty(
        name="Release Pattern",
        description="Use the named release pattern. "
                    "If blank, release molecules at start of simulation.")
    status = StringProperty(name="Status")


class MCellReleasePatternProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Site Name", default="Release_Site",
        description="The name of the release site",
        update=cellblender_operators.check_release_pattern_name)

    delay = FloatProperty(name="Delay")
    delay_str = StringProperty(
        name="Delay",
        default="0",
        description="The time at which the release pattern will start "
                    "(units: seconds).",
        update=cellblender_operators.update_delay)

    release_interval = FloatProperty(name="Release Interval", default=1e-12)
    release_interval_str = StringProperty(
        name="Release Interval",
        default="1e-12",
        description="During a train, release molecules after every interval "
                    "(units: seconds). Default is once.",
        update=cellblender_operators.update_release_interval)

    train_duration = FloatProperty(name="Train Duration", default=1e-12)
    train_duration_str = StringProperty(
        name="Train Duration",
        default="1e-12",
        description="The duration of the train before turning off "
                    "(units: seconds). Default is to never turn off.",
        update=cellblender_operators.update_train_duration)

    train_interval = FloatProperty(name="Train Interval", default=1e-12)
    train_interval_str = StringProperty(
        name="Train Interval",
        default="1e-12",
        description="A new train happens every interval (units: seconds). "
                    "Default is no new trains.",
        update=cellblender_operators.update_train_interval)

    number_of_trains = IntProperty(
        name="Number of Trains", min=0,
        description="Repeat the release process this number of times. "
                    "Default is one train.")

    status = StringProperty(name="Status")


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
        description="The molecule that is affected by the surface class",
        update=cellblender_operators.check_surf_class_props)
    surf_class_orient_enum = [
        ('\'', "Top/Front", ""),
        (',', "Bottom/Back", ""),
        (';', "Ignore", "")]
    surf_class_orient = EnumProperty(
        items=surf_class_orient_enum, name="Orientation",
        description="Volume molecules affected at front or back of a surface. "
                    "Surface molecules affected by orientation at border.",
        update=cellblender_operators.check_surf_class_props)
    surf_class_type_enum = [
        ('ABSORPTIVE', "Absorptive", ""),
        ('TRANSPARENT', "Transparent", ""),
        ('REFLECTIVE', "Reflective", ""),
        ('CLAMP_CONCENTRATION', "Clamp Concentration", "")]
    surf_class_type = EnumProperty(
        items=surf_class_type_enum, name="Type",
        description="Molecules are destroyed by absorptive surfaces, pass "
                    "through transparent, and \"bounce\" off of reflective.",
        update=cellblender_operators.check_surf_class_props)
    clamp_value = FloatProperty(name="Value", precision=4, min=0.0)
    clamp_value_str = StringProperty(
        name="Value", description="Concentration Units: Molar",
        update=cellblender_operators.update_clamp_value)
    status = StringProperty(name="Status")


class MCellSurfaceClassesProperty(bpy.types.PropertyGroup):
    """ Stores the surface class name and a list of its properties. """

    name = StringProperty(
        name="Surface Class Name", default="Surface_Class",
        description="This name can be selected in Modify Surface Regions.",
        update=cellblender_operators.check_surface_class)
    surf_class_props_list = CollectionProperty(
        type=MCellSurfaceClassPropertiesProperty, name="Surface Classes List")
    active_surf_class_props_index = IntProperty(
        name="Active Surface Class Index", default=0)
    status = StringProperty(name="Status")


class MCellModSurfRegionsProperty(bpy.types.PropertyGroup):
    """ Assign a surface class to a surface region. """

    name = StringProperty(name="Modify Surface Region")
    surf_class_name = StringProperty(
        name="Surface Class Name:",
        description="This surface class will be assigned to the surface "
                    "region listed below.",
        update=cellblender_operators.check_mod_surf_regions)
    object_name = StringProperty(
        name="Object Name:",
        description="A region on this object will have the above surface "
                    "class assigned to it.",
        update=cellblender_operators.check_mod_surf_regions)
    region_name = StringProperty(
        name="Region Name:",
        description="This surface region will have the above surface class "
                    "assigned to it.",
        update=cellblender_operators.check_mod_surf_regions)
    status = StringProperty(name="Status")


#Panel Properties:

class CellBlenderPreferencesPanelProperty(bpy.types.PropertyGroup):
    filter_invalid = BoolProperty(
        name="Filter Invalid Entries", default=True,
        description="If selected, entries with a warning(!) icon will not be "
                    "included in simulation.")
    decouple_export_run = BoolProperty(
        name="Decouple Export and Run", default=False,
        description="Allow the project to be exported without also running"
                    " the simulation.")
    debug_level = IntProperty(
        name="Debug", default=10, min=0, max=100,
        description="Amount of debug information to print: 0 to 100")


class MCellScratchPanelProperty(bpy.types.PropertyGroup):
    show_all_icons = BoolProperty(
        name="Show All Icons",
        description="Show all Blender icons and their names",
        default=False)
    print_all_icons = BoolProperty(
        name="Print All Icon Names",
        description="Print all Blender icon names (helpful for searching)",
        default=False)


class MCellProjectPanelProperty(bpy.types.PropertyGroup):
    base_name = StringProperty(
        name="Project Base Name", default="cellblender_project")
    mcell_binary = StringProperty(name="MCell Binary",
        update=cellblender_operators.check_mcell_binary)
    mcell_binary_valid = BoolProperty(name="MCell Binary Valid",
        default=False)
    python_binary = StringProperty(name="Python Binary",
        update=cellblender_operators.check_python_binary)
    python_binary_valid = BoolProperty(name="Python Binary Valid",
        default=False)
    status = StringProperty(name="Status")


class MCellExportProjectPanelProperty(bpy.types.PropertyGroup):
    export_format_enum = [
        ('mcell_mdl_unified', "Single Unified MCell MDL File", ""),
        ('mcell_mdl_modular', "Modular MCell MDL Files", "")]
    export_format = EnumProperty(items=export_format_enum,
                                 name="Export Format",
                                 default='mcell_mdl_modular')


class MCellRunSimulationProcessesProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Simulation Runner Process")
    #pid = IntProperty(name="PID")


class MCellRunSimulationPanelProperty(bpy.types.PropertyGroup):
    start_seed = IntProperty(
        name="Start Seed", default=1, min=1,
        description="The starting value of the random number generator seed")
    end_seed = IntProperty(
        name="End Seed", default=1, min=1,
        description="The ending value of the random number generator seed")
    mcell_processes = IntProperty(
        name="Number of Processes",
        default=cpu_count(),
        min=1,
        max=cpu_count(),
        description="Number of simultaneous MCell processes")
    log_file_enum = [
        ('none', "Do not Generate", ""),
        ('file', "Send to File", ""),
        ('console', "Send to Console", "")]
    log_file = EnumProperty(
        items=log_file_enum, name="Output Log", default='file',
        description="Where to send MCell log output")
    error_file_enum = [
        ('none', "Do not Generate", ""),
        ('file', "Send to File", ""),
        ('console', "Send to Console", "")]
    error_file = EnumProperty(
        items=error_file_enum, name="Error Log", default='console',
        description="Where to send MCell error output")
    remove_append_enum = [
        ('remove', "Remove Previous Data", ""),
        ('append', "Append to Previous Data", "")]
    remove_append = EnumProperty(
        items=remove_append_enum, name="Previous Simulation Data",
        default='remove',
        description="Remove or append to existing rxn/viz data from previous"
                    " simulations before running new simulations.")
    processes_list = CollectionProperty(
        type=MCellRunSimulationProcessesProperty,
        name="Simulation Runner Processes")
    active_process_index = IntProperty(
        name="Active Simulation Runner Process Index", default=0)
    status = StringProperty(name="Status")


class MCellMolVizPanelProperty(bpy.types.PropertyGroup):
    """ Property group for for molecule visualization.

    This is the "Visualize Simulation Results Panel".

    """

    mol_viz_seed_list = CollectionProperty(
        type=MCellStringProperty, name="Visualization Seed List")
    active_mol_viz_seed_index = IntProperty(
        name="Current Visualization Seed Index", default=0,
        update=cellblender_operators.read_viz_data)
        #update= bpy.ops.mcell.read_viz_data)
    mol_file_dir = StringProperty(
        name="Molecule File Dir", subtype='NONE')
    mol_file_list = CollectionProperty(
        type=MCellStringProperty, name="Molecule File Name List")
    mol_file_num = IntProperty(
        name="Number of Molecule Files", default=0)
    mol_file_name = StringProperty(
        name="Current Molecule File Name", subtype='NONE')
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
        default=True, update=cellblender_operators.mol_viz_update)
    color_list = CollectionProperty(
        type=MCellFloatVectorProperty, name="Molecule Color List")
    color_index = IntProperty(name="Color Index", default=0)
    manual_select_viz_dir = BoolProperty(
        name="Manually Select Viz Directory", default=False,
        description="Toggle the option to manually load viz data.",
        update=cellblender_operators.mol_viz_toggle_manual_select)


class MCellInitializationPanelProperty(bpy.types.PropertyGroup):
    iterations = IntProperty(
        name="Simulation Iterations",
        description="Number of iterations to run",
        default=0, min=0)
    time_step = FloatProperty(name="Time Step", default=1e-6, min=0.0)
    time_step_str = StringProperty(
        name="Time Step", default="1e-6",
        description="Simulation Time Step Units: seconds",
        update=cellblender_operators.update_time_step)
    status = StringProperty(name="Status")
    advanced = bpy.props.BoolProperty(default=False)
    warnings = bpy.props.BoolProperty(default=False)
    notifications = bpy.props.BoolProperty(default=False)

    # Advanced/Optional Commands
    time_step_max = FloatProperty(name="Time Step", min=0.0)
    time_step_max_str = StringProperty(
        name="Maximum Time Step",
        description="The longest possible time step",
        update=cellblender_operators.update_time_step_max)
    space_step = FloatProperty(name="Space Step", min=0.0)
    space_step_str = StringProperty(
        name="Space Step",
        description="Have molecules take the same mean diffusion distance",
        update=cellblender_operators.update_space_step)
    surface_grid_density = IntProperty(
        name="Surface Grid Density", default=10000, min=0,
        description="Number of molecules that can be stored per square micron")
    interaction_radius = FloatProperty(name="Interaction Radius", min=0.0)
    interaction_radius_str = StringProperty(
        name="Interaction Radius",
        description="Molecules will interact when they get within N microns.",
        update=cellblender_operators.update_interaction_radius)
    radial_directions = FloatProperty(name="Radial Directions", min=0.0)
    radial_directions_str = StringProperty(
        name="Radial Directions",
        description="Number of different directions to put in lookup table. "
                    "Leave alone unless you know what you are doing.",
        update=cellblender_operators.update_radial_directions)
    radial_subdivisions = FloatProperty(name="Radial Subdivisions", min=0.0)
    radial_subdivisions_str = StringProperty(
        name="Radial Subdivisions",
        description="Number of distances to put in look-up table. "
                    "Leave alone unless you know what you are doing.",
        update=cellblender_operators.update_radial_subdivisions)
    accurate_3d_reactions = BoolProperty(
        name="Accurate 3D Reaction",
        description="If selected, molecules will look through partitions to "
                    "react.",
        default=True)
    center_molecules_grid = BoolProperty(
        name="Center Molecules on Grid",
        description="If selected, surface molecules will be centered on the "
                    "grid.",
        default=False)
    vacancy_search_distance = FloatProperty(
        name="Vacancy Search Distance", min=0.0)
    vacancy_search_distance_str = StringProperty(
        name="Vacancy Search Distance",
        description="Surface molecule products can be created at N distance.",
        update=cellblender_operators.update_vacancy_search_distance)
    microscopic_reversibility_enum = [
        ('ON', "On", ""),
        ('OFF', "Off", ""),
        ('SURFACE_ONLY', "Surface Only", ""),
        ('VOLUME_ONLY', "Volume Only", "")]
    microscopic_reversibility = EnumProperty(
        items=microscopic_reversibility_enum, name="Microscopic Reversibility",
        description="If false, more efficient but less accurate reactions",
        default='OFF')

    # Notifications
    all_notifications_enum = [
        ('INDIVIDUAL', "Set Individually", ""),
        ('ON', "On", ""),
        ('OFF', "Off", "")]
    all_notifications = EnumProperty(
        items=all_notifications_enum, name="All Notifications",
        description="If on/off, all notifications will be set to on/off "
                    "respectively.",
        default='INDIVIDUAL')
    diffusion_constant_report_enum = [
        ('BRIEF', "Brief", ""),
        ('ON', "On", ""),
        ('OFF', "Off", "")]
    diffusion_constant_report = EnumProperty(
        items=diffusion_constant_report_enum, name="Diffusion Constant Report",
        description="If brief, Mcell will report average diffusion distance "
                    "per step for each molecule.")
    file_output_report = BoolProperty(
        name="File Output Report",
        description="If selected, MCell will report every time that reaction "
                    "data is written.",
        default=False)
    final_summary = BoolProperty(
        name="Final Summary",
        description="If selected, MCell will report about the CPU time used",
        default=True)
    iteration_report = BoolProperty(
        name="Iteration Report",
        description="If selected, MCell will report how many iterations have "
                    "completed based on total.",
        default=True)
    partition_location_report = BoolProperty(
        name="Partition Location Report",
        description="If selected, the partition locations will be printed.",
        default=False)
    probability_report_enum = [
        ('ON', "On", ""),
        ('OFF', "Off", ""),
        ('THRESHOLD', "Threshold", "")]
    probability_report = EnumProperty(
        items=probability_report_enum, name="Probability Report", default='ON',
        description="If on, MCell will report reaction probabilites for each "
                    "reaction.")
    probability_report_threshold = bpy.props.FloatProperty(
        name="Threshold", min=0.0, max=1.0, precision=2)
    varying_probability_report = BoolProperty(
        name="Varying Probability Report",
        description="If selected, MCell will print out the reaction "
                    "probabilites for time-varying reaction.",
        default=True)
    progress_report = BoolProperty(
        name="Progress Report",
        description="If selected, MCell will print out messages indicating "
                    "which part of the simulation is underway.",
        default=True)
    release_event_report = BoolProperty(
        name="Release Event Report",
        description="If selected, MCell will print a message every time "
                    "molecules are released through a release site.",
        default=True)
    molecule_collision_report = BoolProperty(
        name="Molecule Collision Report",
        description="If selected, MCell will print the number of "
                    "bi/trimolecular collisions that occured.",
        default=False)

    # Warnings
    all_warnings_enum = [
        ('INDIVIDUAL', "Set Individually", ""),
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    all_warnings = EnumProperty(
        items=all_warnings_enum, name="All Warnings",
        description="If not \"Set Individually\", all warnings will be set "
                    "the same.",
        default='INDIVIDUAL')
    degenerate_polygons_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    degenerate_polygons = EnumProperty(
        items=degenerate_polygons_enum, name="Degenerate Polygons",
        description="Degenerate polygons have zero area and must be removed.",
        default='WARNING')
    high_reaction_probability_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    high_reaction_probability = EnumProperty(
        items=high_reaction_probability_enum, name="High Reaction Probability",
        description="Generate warnings or errors if probability reaches a "
                    "specified threshold.",
        default='IGNORED')
    high_probability_threshold = bpy.props.FloatProperty(
        name="High Probability Threshold", min=0.0, max=1.0, default=1.0,
        precision=2)
    lifetime_too_short_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", "")]
    lifetime_too_short = EnumProperty(
        items=lifetime_too_short_enum, name="Lifetime Too Short",
        description="Generate warning if molecules have short lifetimes.",
        default='WARNING')
    lifetime_threshold = IntProperty(
        name="Threshold", min=0, default=50)
    missed_reactions_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", "")]
    missed_reactions = EnumProperty(
        items=missed_reactions_enum, name="Missed Reactions",
        description="Generate warning if there are missed reactions.",
        default='WARNING')
    missed_reaction_threshold = bpy.props.FloatProperty(
        name="Threshold", min=0.0, max=1.0, default=0.001,
        precision=4)
    negative_diffusion_constant_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    negative_diffusion_constant = EnumProperty(
        items=negative_diffusion_constant_enum,
        description="Diffusion constants cannot be negative and will be set "
                    "to zero.",
        name="Negative Diffusion Constant", default='WARNING')
    missing_surface_orientation_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    missing_surface_orientation = EnumProperty(
        items=missing_surface_orientation_enum,
        description="Generate errors/warnings if molecules are placed on "
                    "surfaces or reactions occur at surfaces without "
                    "specified orientation.",
        name="Missing Surface Orientation",
        default='ERROR')
    negative_reaction_rate_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    negative_reaction_rate = EnumProperty(
        items=negative_reaction_rate_enum, name="Negative Reaction Rate",
        description="Reaction rates cannot be negative and will be set "
                    "to zero.",
        default='WARNING')
    useless_volume_orientation_enum = [
        ('IGNORED', "Ignored", ""),
        ('WARNING', "Warning", ""),
        ('ERROR', "Error", "")]
    useless_volume_orientation = EnumProperty(
        items=useless_volume_orientation_enum,
        description="Generate errors/warnings if molecules are released in a "
                    "volume or reactions occur in a volume with specified "
                    "orientation.",
        name="Useless Volume Orientation", default='WARNING')


class MCellPartitionsPanelProperty(bpy.types.PropertyGroup):
    include = BoolProperty(
        name="Include Partitions",
        description="Partitions are a way of speeding up a simulation if used "
                    "properly.",
        default=False)
    recursion_flag = BoolProperty(
        name="Recursion Flag",
        description="Flag to prevent infinite recursion",
        default=False)
    x_start = bpy.props.FloatProperty(
        name="X Start", default=-1, precision=3,
        description="The start of the partitions on the x-axis",
        update=cellblender_operators.transform_x_partition_boundary)
    x_end = bpy.props.FloatProperty(
        name="X End", default=1, precision=3,
        description="The end of the partitions on the x-axis",
        update=cellblender_operators.transform_x_partition_boundary)
    x_step = bpy.props.FloatProperty(
        name="X Step", default=0.02, precision=3,
        description="The distance between partitions on the x-axis",
        update=cellblender_operators.check_x_partition_step)
    y_start = bpy.props.FloatProperty(
        name="Y Start", default=-1, precision=3,
        description="The start of the partitions on the y-axis",
        update=cellblender_operators.transform_y_partition_boundary)
    y_end = bpy.props.FloatProperty(
        name="Y End", default=1, precision=3,
        description="The end of the partitions on the y-axis",
        update=cellblender_operators.transform_y_partition_boundary)
    y_step = bpy.props.FloatProperty(
        name="Y Step", default=0.02, precision=3,
        description="The distance between partitions on the y-axis",
        update=cellblender_operators.check_y_partition_step)
    z_start = bpy.props.FloatProperty(
        name="Z Start", default=-1, precision=3,
        description="The start of the partitions on the z-axis",
        update=cellblender_operators.transform_z_partition_boundary)
    z_end = bpy.props.FloatProperty(
        name="Z End", default=1, precision=3,
        description="The end of the partitions on the z-axis",
        update=cellblender_operators.transform_z_partition_boundary)
    z_step = bpy.props.FloatProperty(
        name="Z Step", default=0.02, precision=3,
        description="The distance between partitions on the z-axis",
        update=cellblender_operators.check_z_partition_step)


######################## DB: added for imported parameters from BNG, SBML or other models###############################
class MCellParameterProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Parameter Name", default="Parameter")
    value = StringProperty(name="Parameter Value", default="0")
    unit = StringProperty(name="Parameter Unit", default="",
        description="Forward Rate Units: sec^-1 (unimolecular),"
                    " M^-1*sec^-1 (bimolecular)")
    type = StringProperty(name="Parameter type", default="", description="")		    
    status = StringProperty(name="Status")

class MCellParametersPanelProperty(bpy.types.PropertyGroup):
    parameter_list = CollectionProperty(
        type=MCellParameterProperty, name="Parameter List")
    active_par_index = IntProperty(name="Active Parameter Index", default=0)
    plot_command = StringProperty(name="", default="")
###########################################################################################################################





############### BK: Duplicating some of Dipak's code to experiment with general-purpose (non-imported) parameters #################

"""
# This is now being replaced by code from cellblender_parameters.py
class MCellGeneralParameterProperty(bpy.types.PropertyGroup):
    id = IntProperty(name="ID", default=0, description="Unique ID for each parameter")
    name = StringProperty(name="Name", default="Parameter", description="Unique name for this parameter",
        update=cellblender_operators.update_parameter_name)
    expr = StringProperty(name="Expression", default="0", description="Expression to be evaluated for this parameter",
        update=cellblender_operators.update_parameter_expression)

    pending_expr = StringProperty(name="PendingExpression", default="0", description="Expression as entered with errors pending correction")

    value = StringProperty(name="Value", default="0", description="Current evaluated value for this parameter" )
    valid = BoolProperty(default=False)
    initialized = BoolProperty(default=False)

    unit = StringProperty(name="Units", default="", description="Parameter Unit")
    desc = StringProperty(name="Description", default="", description="Parameter Description")
    
    status = StringProperty(name="Status")


class MCellParametersPropertyGroup(bpy.types.PropertyGroup):
    parameter_list = CollectionProperty(type=MCellGeneralParameterProperty, name="Parameters List")
    active_par_index = IntProperty(name="Active Parameter", default=0)
    param_group_error = StringProperty( default="", description="Error Message for Entire Parameter Group")
    parameter_space_string = StringProperty ( name="ParameterSpace", default="", description="ParameterSpace object pickled as a string" )
"""
###########################################################################################################################


class MCellReactionsPanelProperty(bpy.types.PropertyGroup):
    reaction_list = CollectionProperty(
        type=MCellReactionProperty, name="Reaction List")
    active_rxn_index = IntProperty(name="Active Reaction Index", default=0)
    reaction_name_list = CollectionProperty(
        type=MCellStringProperty, name="Reaction Name List")
    plot_command = StringProperty(name="", default="")


class MCellSurfaceClassesPanelProperty(bpy.types.PropertyGroup):
    surf_class_list = CollectionProperty(
        type=MCellSurfaceClassesProperty, name="Surface Classes List")
    active_surf_class_index = IntProperty(
        name="Active Surface Class Index", default=0)
    #surf_class_props_status = StringProperty(name="Status")


class MCellModSurfRegionsPanelProperty(bpy.types.PropertyGroup):
    mod_surf_regions_list = CollectionProperty(
        type=MCellModSurfRegionsProperty, name="Modify Surface Region List")
    active_mod_surf_regions_index = IntProperty(
        name="Active Modify Surface Region Index", default=0)


class MCellReleasePatternPanelProperty(bpy.types.PropertyGroup):
    release_pattern_list = CollectionProperty(
        type=MCellReleasePatternProperty, name="Release Pattern List")
    active_release_pattern_index = IntProperty(
        name="Active Release Pattern Index", default=0)


class MCellMoleculeReleasePanelProperty(bpy.types.PropertyGroup):
    mol_release_list = CollectionProperty(
        type=MCellMoleculeReleaseProperty, name="Molecule Release List")
    active_release_index = IntProperty(name="Active Release Index", default=0)


class MCellModelObjectsProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Object Name", update=cellblender_operators.check_model_object)
    status = StringProperty(name="Status")


class MCellModelObjectsPanelProperty(bpy.types.PropertyGroup):
    object_list = CollectionProperty(
        type=MCellModelObjectsProperty, name="Object List")
    active_obj_index = IntProperty(name="Active Object Index", default=0)


class MCellVizOutputPanelProperty(bpy.types.PropertyGroup):
    active_mol_viz_index = IntProperty(
        name="Active Molecule Viz Index", default=0)
    all_iterations = bpy.props.BoolProperty(
        name="All Iterations",
        description="Include all iterations for visualization.", default=True)
    start = bpy.props.IntProperty(
        name="Start", description="Starting iteration", default=0, min=0)
    end = bpy.props.IntProperty(
        name="End", description="Ending iteration", default=1, min=1)
    step = bpy.props.IntProperty(
        name="Step", description="Output viz data every n iterations.",
        default=1, min=1)


class MCellReactionOutputProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Reaction Output", update=cellblender_operators.check_rxn_output)
    molecule_name = StringProperty(
        name="Molecule",
        description="Count the selected molecule.",
        update=cellblender_operators.check_rxn_output)
    reaction_name = StringProperty(
        name="Reaction",
        description="Count the selected reaction.",
        update=cellblender_operators.check_rxn_output)
    object_name = StringProperty(
        name="Object", update=cellblender_operators.check_rxn_output)
    region_name = StringProperty(
        name="Region", update=cellblender_operators.check_rxn_output)
    count_location_enum = [
        ('World', "World", ""),
        ('Object', "Object", ""),
        ('Region', "Region", "")]
    count_location = bpy.props.EnumProperty(
        items=count_location_enum, name="Count Location",
        description="Count all molecules in the selected location.",
        update=cellblender_operators.check_rxn_output)
    rxn_or_mol_enum = [
        ('Reaction', "Reaction", ""),
        ('Molecule', "Molecule", "")]
    rxn_or_mol = bpy.props.EnumProperty(
        items=rxn_or_mol_enum, name="Count Reaction or Molecule",
        default='Molecule',
        description="Select between counting a reaction or molecule.",
        update=cellblender_operators.check_rxn_output)
    plot_command = StringProperty(
        name="Command")  # , update=cellblender_operators.check_rxn_output)
    status = StringProperty(name="Status")


import cellblender


class MCellReactionOutputPanelProperty(bpy.types.PropertyGroup):
    active_rxn_output_index = IntProperty(
        name="Active Reaction Output Index", default=0)
    rxn_output_list = CollectionProperty(
        type=MCellReactionOutputProperty, name="Reaction Output List")
    plot_layout_enum = [
        (' page ', "Separate Page for each Plot", ""),
        (' plot ', "One Page, Multiple Plots", ""),
        (' ',      "One Page, One Plot", "")]
    plot_layout = bpy.props.EnumProperty ( items=plot_layout_enum, name="" )
    plot_legend_enum = [
        ('x', "No Legend", ""),
        ('0', "Legend with Automatic Placement", ""),
        ('1', "Legend in Upper Right", ""),
        ('2', "Legend in Upper Left", ""),
        ('3', "Legend in Lower Left", ""),
        ('4', "Legend in Lower Right", ""),
        # ('5', "Legend on Right", ""), This appears to duplicate option 7
        ('6', "Legend in Center Left", ""),
        ('7', "Legend in Center Right", ""),
        ('8', "Legend in Lower Center", ""),
        ('9', "Legend in Upper Center", ""),
        ('10', "Legend in Center", "")]
    plot_legend = bpy.props.EnumProperty ( items=plot_legend_enum, name="", default='0' )
    combine_seeds = BoolProperty(
        name="Combine Seeds",
        description="Combine all seeds onto the same plot.",
        default=True)
    mol_colors = BoolProperty(
        name="Molecule Colors",
        description="Use Molecule Colors for line colors.",
        default=False)


class MCellMoleculeGlyphsPanelProperty(bpy.types.PropertyGroup):
    glyph_lib = __file__.replace(__file__.split('/')[len(
        __file__.split("/"))-1], "")+"glyph_library.blend/Mesh/"
    glyph_enum = [
        ('Cone', "Cone", ""),
        ('Cube', "Cube", ""),
        ('Cylinder', "Cylinder", ""),
        ('Icosahedron', "Icosahedron", ""),
        ('Octahedron', "Octahedron", ""),
        ('Receptor', "Receptor", ""),
        ('Sphere_1', "Sphere_1", ""),
        ('Sphere_2', "Sphere_2", ""),
        ('Torus', "Torus", "")]
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
    sav_ratio = FloatProperty(name="SA/V Ratio", default=0)
    status = StringProperty(name="Status")


class MCellObjectSelectorPanelProperty(bpy.types.PropertyGroup):
    filter = StringProperty(
        name="Object Name Filter",
        description="Enter a regular expression for object names.")


# Main MCell (CellBlender) Properties Class:

class MCellPropertyGroup(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(
        name="Contains CellBlender Parameters", default=True)
    cellblender_version = StringProperty(
        name="CellBlender Version", default="0.1.54")
    cellblender_source_hash = StringProperty(
        name="CellBlender Source Hash", default="unknown")
    cellblender_preferences = PointerProperty(
        type=CellBlenderPreferencesPanelProperty,
        name="CellBlender Preferences")
    project_settings = PointerProperty(
        type=MCellProjectPanelProperty, name="CellBlender Project Settings")
    export_project = PointerProperty(
        type=MCellExportProjectPanelProperty, name="Export Simulation")
    run_simulation = PointerProperty(
        type=MCellRunSimulationPanelProperty, name="Run Simulation")
    mol_viz = PointerProperty(
        type=MCellMolVizPanelProperty, name="Mol Viz Settings")
    initialization = PointerProperty(
        type=MCellInitializationPanelProperty, name="Model Initialization")
    partitions = bpy.props.PointerProperty(
        type=MCellPartitionsPanelProperty, name="Partitions")
############## DB: added for parameter import from BNG, SBML models####
    parameters = PointerProperty(
        type=MCellParametersPanelProperty, name="Defined Parameters")
############## BK: Duplicating some of Dipak's code to experiment with general-purpose (non-imported) parameters ####
    general_parameters = PointerProperty(
        type=cellblender_parameters.MCellParametersPropertyGroup, name="General Parameters")
########################################################################
    molecules = PointerProperty(
        type=cellblender_molecules.MCellMoleculesListProperty, name="Defined Molecules")
    reactions = PointerProperty(
        type=MCellReactionsPanelProperty, name="Defined Reactions")
    surface_classes = PointerProperty(
        type=MCellSurfaceClassesPanelProperty, name="Defined Surface Classes")
    mod_surf_regions = PointerProperty(
        type=MCellModSurfRegionsPanelProperty, name="Modify Surface Regions")
    release_patterns = PointerProperty(
        type=MCellReleasePatternPanelProperty, name="Defined Release Patterns")
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
    scratch_settings = PointerProperty(
        type=MCellScratchPanelProperty, name="CellBlender Scratch Settings")

