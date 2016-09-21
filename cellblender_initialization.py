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
This file contains the classes for CellBlender's Reactions.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Initialization Panel Classes

class MCELL_PT_initialization(bpy.types.Panel):
    bl_label = "CellBlender - Model Initialization"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.initialization.draw_panel ( context, self )



class MCellInitializationPropertyGroup(bpy.types.PropertyGroup):

    def __init__(self):
        print ( "\n\nMCellInitializationPropertyGroup.__init__() called\n\n" )

    iterations = PointerProperty ( name="iterations", type=parameter_system.Parameter_Reference )
    time_step =  PointerProperty ( name="Time Step", type=parameter_system.Parameter_Reference )

    status = StringProperty(name="Status")
    advanced = bpy.props.BoolProperty(default=False)
    warnings = bpy.props.BoolProperty(default=False)
    notifications = bpy.props.BoolProperty(default=False)

    # Advanced/Optional Commands

    time_step_max = PointerProperty ( name="Time Step Max", type=parameter_system.Parameter_Reference )
    space_step = PointerProperty ( name="Space Step", type=parameter_system.Parameter_Reference )
    interaction_radius = PointerProperty ( name="Interaction Radius", type=parameter_system.Parameter_Reference )
    radial_directions = PointerProperty ( name="Radial Directions", type=parameter_system.Parameter_Reference )
    radial_subdivisions = PointerProperty ( name="Radial Subdivisions", type=parameter_system.Parameter_Reference )
    vacancy_search_distance = PointerProperty ( name="Radial Subdivisions", type=parameter_system.Parameter_Reference )
    surface_grid_density = PointerProperty ( name="Surface Grid Density", type=parameter_system.Parameter_Reference )

    def init_properties ( self, parameter_system ):
        helptext = "Number of iterations to run"
        self.iterations.init_ref    ( parameter_system,
                                      user_name="Iterations", 
                                      user_expr="1000",    
                                      user_units="",  
                                      user_descr=helptext,  
                                      user_int=True )

        helptext = "Simulation Time Step\n1e-6 is a common value."
        self.time_step.init_ref     ( parameter_system,
                                      user_name="Time Step",  
                                      user_expr="1e-6", 
                                      user_units="seconds", 
                                      user_descr=helptext )
       
        helptext = "The longest possible time step.\n" + \
                   "MCell3 will move longer than the specified simulation time step\n" + \
                   "if it seems safe. This command makes sure that the longest possible\n" + \
                   "time step is no longer than this value (in seconds), even if MCell3\n" + \
                   "thinks a longer step would be safe. The default is no limit."
        self.time_step_max.init_ref ( parameter_system,
                                      user_name="Maximum Time Step", 
                                      user_expr="", 
                                      user_units="seconds", 
                                      user_descr=helptext )
       
        helptext = "Have molecules take the same mean diffusion distance.\n" + \
                   "Have all diffusing molecules take time steps of different duration,\n" + \
                   "chosen so that the mean diffusion distance is N microns for each\n" + \
                   "molecule. By default, all molecules move the same time step."
        self.space_step.init_ref    ( parameter_system,
                                      user_name="Space Step",    
                                      user_expr="", 
                                      user_units="microns", 
                                      user_descr=helptext )
       
        helptext = "Diffusing Volume Molecules will interact when they get within\n" + \
                   "N microns of each other.\n" + \
                   "The default is:  1 / sqrt(Pi * SurfaceGridDensity)"
        self.interaction_radius.init_ref ( parameter_system,
                                           user_name="Interaction Radius", 
                                           user_expr="", user_units="microns", 
                                           user_descr=helptext )
       
        helptext = "Specifies how many different directions to put in the lookup table." + \
                   "The default is sensible. Don’t use this unless you know what you’re doing." + \
                   "Instead of a number, you can specify FULLY_RANDOM in MDL to generate the" + \
                   "directions directly from double precision numbers (but this is slower)."
        self.radial_directions.init_ref   ( parameter_system,
                                            user_name="Radial Directions",   
                                            user_expr="", user_units="microns", 
                                            user_descr=helptext )
       
        helptext = "Specifies how many distances to put in the diffusion look-up table.\n" + \
                   "The default is sensible. FULLY_RANDOM is not implemented."
        self.radial_subdivisions.init_ref ( parameter_system,
                                            user_name="Radial Subdivisions", 
                                            user_expr="", 
                                            user_descr=helptext )
       
        helptext = "Surface molecule products can be created at r distance.\n" + \
                   "Normally, a reaction will not proceed on a surface unless there\n" + \
                   "is room to place all products on the single grid element where\n" + \
                   "the reaction is initiated. By increasing r from its default value\n" + \
                   "of 0, one can specify how far from the reaction’s location, in microns,\n" + \
                   "the reaction can place its products. To be useful, r must\n" + \
                   "be larger than the longest axis of the grid element on the triangle\n" + \
                   "in question. The reaction will then proceed if there is room to\n" + \
                   "place its products within a radius r, and will place those products\n" + \
                   "as close as possible to the place where the reaction occurs\n" + \
                   "(deterministically, so small- scale directional bias is possible)."
        self.vacancy_search_distance.init_ref ( parameter_system,
                                                user_name="Vacancy Search Distance", 
                                                user_expr="", 
                                                user_units="microns", 
                                                user_descr=helptext )
       
        helptext = "Number of molecules that can be stored per square micron.\n" + \
                   "Tile all surfaces so that they can hold molecules at N different\n" + \
                   "positions per square micron. The default is 10000. For backwards\n" + \
                   "compatibility, EFFECTOR_GRID_DENSITY works also in MCell MDL."
        self.surface_grid_density.init_ref ( parameter_system,
                                             user_name="Surface Grid Density", 
                                             user_expr="10000", 
                                             user_units="count / sq micron", 
                                             user_descr=helptext )

    def remove_properties ( self, context ):
        ps = context.scene.mcell.parameter_system
        # It's not needed to remove these properties because there is only one copy? Mostly yes.

        # It appears that removing some of the "original 16" panel parameters causes a problem.
        # This was fixed by commenting out the removal code. However, that causes some of the
        # other "original 16" to be recreated when reading from a data model (or using the
        # "Clear Project" scripting button). These duplicate parameters appear to not be a
        # problem because the RNA properties only store a reference to the most current one.
        # However, they do leave a trail of ID property "ghosts" which show multiple versions
        # of the same panel parameters.

        # But if they were to be removed, here's what it would look like:
        """
        self.iterations.clear_ref ( ps )
        self.time_step.clear_ref ( ps )
        self.time_step_max.clear_ref ( ps )
        self.space_step.clear_ref ( ps )
        self.interaction_radius.clear_ref ( ps )
        self.radial_directions.clear_ref ( ps )
        self.radial_subdivisions.clear_ref ( ps )
        self.vacancy_search_distance.clear_ref ( ps )
        self.surface_grid_density.clear_ref ( ps )
        """


    def build_data_model_from_properties ( self, context ):
        dm_dict = {}

        dm_dict['data_model_version'] = "DM_2014_10_24_1638"

        dm_dict['iterations'] = self.iterations.get_expr()
        dm_dict['time_step'] = self.time_step.get_expr()
        dm_dict['time_step_max'] = self.time_step_max.get_expr()
        dm_dict['space_step'] = self.space_step.get_expr()
        dm_dict['interaction_radius'] = self.interaction_radius.get_expr()
        dm_dict['radial_directions'] = self.radial_directions.get_expr()
        dm_dict['radial_subdivisions'] = self.radial_subdivisions.get_expr()
        dm_dict['vacancy_search_distance'] = self.vacancy_search_distance.get_expr()
        dm_dict['surface_grid_density'] = self.surface_grid_density.get_expr()
        dm_dict['microscopic_reversibility'] = str(self.microscopic_reversibility)
        dm_dict['accurate_3d_reactions'] = self.accurate_3d_reactions==True
        dm_dict['center_molecules_on_grid'] = self.center_molecules_grid==True

        notify_dict = {}
        notify_dict['all_notifications'] = str(self.all_notifications)
        notify_dict['diffusion_constant_report'] = str(self.diffusion_constant_report)
        notify_dict['file_output_report'] = self.file_output_report==True
        notify_dict['final_summary'] = self.final_summary==True
        notify_dict['iteration_report'] = self.iteration_report==True
        notify_dict['partition_location_report'] = self.partition_location_report==True
        notify_dict['probability_report'] = str(self.probability_report)
        notify_dict['probability_report_threshold'] = "%g" % (self.probability_report_threshold)
        notify_dict['varying_probability_report'] = self.varying_probability_report==True
        notify_dict['progress_report'] = self.progress_report==True
        notify_dict['release_event_report'] = self.release_event_report==True
        notify_dict['molecule_collision_report'] = self.molecule_collision_report==True
        notify_dict['box_triangulation_report'] = False
        dm_dict['notifications'] = notify_dict
        
        warn_dict = {}
        warn_dict['all_warnings'] = str(self.all_warnings)
        warn_dict['degenerate_polygons'] = str(self.degenerate_polygons)
        warn_dict['high_reaction_probability'] = str(self.high_reaction_probability)
        warn_dict['high_probability_threshold'] = "%g" % (self.high_probability_threshold)
        warn_dict['lifetime_too_short'] = str(self.lifetime_too_short)
        warn_dict['lifetime_threshold'] = str(self.lifetime_threshold)
        warn_dict['missed_reactions'] = str(self.missed_reactions)
        warn_dict['missed_reaction_threshold'] = "%g" % (self.missed_reaction_threshold)
        warn_dict['negative_diffusion_constant'] = str(self.negative_diffusion_constant)
        warn_dict['missing_surface_orientation'] = str(self.missing_surface_orientation)
        warn_dict['negative_reaction_rate'] = str(self.negative_reaction_rate)
        warn_dict['useless_volume_orientation'] = str(self.useless_volume_orientation)
        dm_dict['warnings'] = warn_dict

        return dm_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellInitializationPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellInitializationPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm_dict ):

        print ( "Top of MCellInitializationPropertyGroup.build_properties_from_data_model" )

        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellInitializationPropertyGroup data model to current version." )

        #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

        if "iterations" in dm_dict: self.iterations.set_expr ( dm_dict["iterations"] )
        if "time_step" in dm_dict: self.time_step.set_expr ( dm_dict["time_step"] )
        if "time_step_max" in dm_dict: self.time_step_max.set_expr ( dm_dict["time_step_max"] )
        if "space_step" in dm_dict: self.space_step.set_expr ( dm_dict["space_step"] )
        if "interaction_radius" in dm_dict: self.interaction_radius.set_expr ( dm_dict["interaction_radius"] )
        if "radial_directions" in dm_dict: self.radial_directions.set_expr ( dm_dict["radial_directions"] )
        if "radial_subdivisions" in dm_dict: self.radial_subdivisions.set_expr ( dm_dict["radial_subdivisions"] )
        if "vacancy_search_distance" in dm_dict: self.vacancy_search_distance.set_expr ( dm_dict["vacancy_search_distance"] )
        if "surface_grid_density" in dm_dict: self.surface_grid_density.set_expr ( dm_dict["surface_grid_density"] )
        if "microscopic_reversibility" in dm_dict: self.microscopic_reversibility = dm_dict["microscopic_reversibility"]
        if "accurate_3d_reactions" in dm_dict: self.accurate_3d_reactions = dm_dict["accurate_3d_reactions"]
        if "center_molecules_on_grid" in dm_dict: self.center_molecules_grid = dm_dict["center_molecules_on_grid"]

        if "notifications" in dm_dict:
            note_dict = dm_dict['notifications']
            if "all_notifications" in note_dict: self.all_notifications = note_dict['all_notifications']
            if "diffusion_constant_report" in note_dict: self.diffusion_constant_report = note_dict['diffusion_constant_report']
            if "file_output_report" in note_dict: self.file_output_report = note_dict['file_output_report']
            if "final_summary" in note_dict: self.final_summary = note_dict['final_summary']
            if "iteration_report" in note_dict: self.iteration_report = note_dict['iteration_report']
            if "partition_location_report" in note_dict: self.partition_location_report = note_dict['partition_location_report']
            if "probability_report" in note_dict: self.probability_report = note_dict['probability_report']
            if "probability_report_threshold" in note_dict: self.probability_report_threshold = float(note_dict['probability_report_threshold'])
            if "varying_probability_report" in note_dict: self.varying_probability_report = note_dict['varying_probability_report']
            if "progress_report" in note_dict: self.progress_report = note_dict['progress_report']
            if "release_event_report" in note_dict: self.release_event_report = note_dict['release_event_report']
            if "molecule_collision_report" in note_dict: self.molecule_collision_report = note_dict['molecule_collision_report']

        ##notify_dict[box_triangulation_report'] = False

        if "warnings" in dm_dict:
            warn_dict = dm_dict['warnings']
            if "all_warnings" in warn_dict: self.all_warnings = warn_dict['all_warnings']
            if "degenerate_polygons" in warn_dict: self.degenerate_polygons = warn_dict['degenerate_polygons']
            if "high_reaction_probability" in warn_dict: self.high_reaction_probability = warn_dict['high_reaction_probability']
            if "high_probability_threshold" in warn_dict: self.high_probability_threshold = float(warn_dict['high_probability_threshold'])
            if "lifetime_too_short" in warn_dict: self.lifetime_too_short = warn_dict['lifetime_too_short']
            if "lifetime_threshold" in warn_dict: self.lifetime_threshold = float(warn_dict['lifetime_threshold'])
            if "missed_reactions" in warn_dict: self.missed_reactions = warn_dict['missed_reactions']
            if "missed_reaction_threshold" in warn_dict: self.missed_reaction_threshold = float(warn_dict['missed_reaction_threshold'])
            if "negative_diffusion_constant" in warn_dict: self.negative_diffusion_constant = warn_dict['negative_diffusion_constant']
            if "missing_surface_orientation" in warn_dict: self.missing_surface_orientation = warn_dict['missing_surface_orientation']
            if "negative_reaction_rate" in warn_dict: self.negative_reaction_rate = warn_dict['negative_reaction_rate']
            if "useless_volume_orientation" in warn_dict: self.useless_volume_orientation = warn_dict['useless_volume_orientation']

        print ( "Bottom of MCellInitializationPropertyGroup.build_properties_from_data_model" )


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


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


    acc3D_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    center_on_grid_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    micro_rev_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            self.iterations.draw(layout,ps)
            self.time_step.draw(layout,ps)


            # Note that the run_simulation panel is effectively being drawn in the middle of this model_initialization panel!!!
            mcell.run_simulation.draw_layout_queue(context,layout)


            # Advanced Options
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.advanced:
                row.prop(mcell.initialization, "advanced", icon='TRIA_DOWN',
                         text="Advanced Options", emboss=False)

                self.time_step_max.draw(box,ps)
                self.space_step.draw(box,ps)
                self.interaction_radius.draw(box,ps)
                self.radial_directions.draw(box,ps)
                self.radial_subdivisions.draw(box,ps)
                self.vacancy_search_distance.draw(box,ps)
                self.surface_grid_density.draw(box,ps)

                #row = box.row()
                # row.prop(mcell.initialization, "accurate_3d_reactions")
                helptext = "Accurate 3D Reactions\n" + \
                           "Specifies which method to use for computing 3D molecule-molecule\n" + \
                           "interactions. If value is TRUE, then molecules will look\n" + \
                           "through partition boundaries for potential interacting\n" + \
                           "partners – this is slower but more accurate. If boolean is\n" + \
                           "FALSE, then molecule interaction disks will be clipped at partition\n" + \
                           "boundaries and probabilities adjusted to get the correct rate – \n" + \
                           "this is faster but can be less accurate. The default is TRUE."
                ps.draw_prop_with_help ( box, "Accurate 3D Reactions", mcell.initialization, "accurate_3d_reactions", "acc3D_show_help", self.acc3D_show_help, helptext )
                
                #row = box.row()
                #row.prop(mcell.initialization, "center_molecules_grid")
                helptext = "Center Molecules on Grid\n" + \
                           "If boolean is set to TRUE, then all molecules on a surface will be\n" + \
                           "located exactly at the center of their grid element. If FALSE, the\n" + \
                           "molecules will be randomly located when placed, and reactions\n" + \
                           "will take place at the location of the target (or the site of impact\n" + \
                           "in the case of 3D molecule/surface reactions). The default is FALSE."
                ps.draw_prop_with_help ( box, "Center Molecules on Grid", mcell.initialization, "center_molecules_grid", "center_on_grid_show_help", self.center_on_grid_show_help, helptext )

                #row = box.row()
                #row.prop(mcell.initialization, "microscopic_reversibility")
                helptext = "Microscopic Reversibility\n" + \
                           "If value is set to OFF, then binding- unbinding reactions between\n" + \
                           "molecules will be somewhat more efficient but may not be accurate\n" + \
                           "if the probability of binding is high (close to 1).\n" + \
                           "If ON, a more computationally demanding routine will be used to\n" + \
                           "make sure binding- unbinding is more similar in both directions.\n" + \
                           "If value is set to SURFACE_ONLY or VOLUME_ONLY, the more\n" + \
                           "accurate routines will be used only for reactions at surfaces\n" + \
                           "or only for those in the volume. OFF is the default."
                ps.draw_prop_with_help ( box, "Microscopic Reversibility", mcell.initialization, "microscopic_reversibility", "micro_rev_show_help", self.micro_rev_show_help, helptext )

            else:
                row.prop(mcell.initialization, "advanced", icon='TRIA_RIGHT',
                         text="Advanced Options", emboss=False)

            # Notifications
            #box = layout.box(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.notifications:
                row.prop(mcell.initialization, "notifications", icon='TRIA_DOWN',
                         text="Notifications", emboss=False)
                row = box.row()
                row.prop(mcell.initialization, "all_notifications")
                if self.all_notifications == 'INDIVIDUAL':
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "probability_report")
                    if self.probability_report == 'THRESHOLD':
                        row.prop(
                            mcell.initialization, "probability_report_threshold",
                            slider=True)
                    row = box.row()
                    row.prop(mcell.initialization, "diffusion_constant_report")
                    row = box.row()
                    row.prop(mcell.initialization, "file_output_report")
                    row = box.row()
                    row.prop(mcell.initialization, "final_summary")
                    row = box.row()
                    row.prop(mcell.initialization, "iteration_report")
                    row = box.row()
                    row.prop(mcell.initialization, "partition_location_report")
                    row = box.row()
                    row.prop(mcell.initialization, "varying_probability_report")
                    row = box.row()
                    row.prop(mcell.initialization, "progress_report")
                    row = box.row()
                    row.prop(mcell.initialization, "release_event_report")
                    row = box.row()
                    row.prop(mcell.initialization, "molecule_collision_report")
            else:
                row.prop(mcell.initialization, "notifications", icon='TRIA_RIGHT',
                         text="Notifications", emboss=False)

            # Warnings
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.warnings:
                row.prop(mcell.initialization, "warnings", icon='TRIA_DOWN',
                         text="Warnings", emboss=False)
                row = box.row()
                row.prop(mcell.initialization, "all_warnings")
                if self.all_warnings == 'INDIVIDUAL':
                    row = box.row()
                    row.prop(mcell.initialization, "degenerate_polygons")
                    row = box.row()
                    row.prop(mcell.initialization, "missing_surface_orientation")
                    row = box.row()
                    row.prop(mcell.initialization, "negative_diffusion_constant")
                    row = box.row()
                    row.prop(mcell.initialization, "negative_reaction_rate")
                    row = box.row()
                    row.prop(mcell.initialization, "useless_volume_orientation")
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "high_reaction_probability")
                    if self.high_reaction_probability != 'IGNORED':
                        row.prop(mcell.initialization,
                                 "high_probability_threshold", slider=True)
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "lifetime_too_short")
                    if self.lifetime_too_short == 'WARNING':
                        row.prop(mcell.initialization, "lifetime_threshold")
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "missed_reactions")
                    if self.missed_reactions == 'WARNING':
                        row.prop(mcell.initialization, "missed_reaction_threshold")
            else:
                row.prop(mcell.initialization, "warnings", icon='TRIA_RIGHT',
                         text="Warnings", emboss=False)

            if (self.status != ""):
                row = layout.row()
                row.label(text=self.status, icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




