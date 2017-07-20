# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
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

# Copyright (C) 2012: Tom Bartol, bartol@salk.edu
# Contributors: Tom Bartol, Bob Kuczewski


"""
This script exports MCell MDL files from Blender and is a component of
CellBlender.

"""

# python imports
import os
import re
import shutil

# blender imports
import bpy

# from cellblender import cellblender_operators  # Shouldn't need this anymore!!

from cellblender import object_surface_regions
from cellblender.cellblender_utils import mcell_files_path


def save(context, filepath=""):
    """ Top level function for saving the current MCell model
        as MDL.

    """
    print("export_mcell_mdl.py/save(context,filepath=\"" + filepath + "\")")
    with open(filepath, "w", encoding="utf8", newline="\n") as out_file:
        filedir = os.path.dirname(filepath)
        save_wrapper(context, out_file, filedir)


def dontrun_filter_ignore(unfiltered_item_list):
    """ Apply selected filter/ignore policy.
    
    This function helps reduce boilerplate code.
    """
    
    mcell = bpy.context.scene.mcell

    item_list = []
    error_list = []

    if unfiltered_item_list:
        # Only export and run if everything is valid
        if mcell.cellblender_preferences.invalid_policy == 'dont_run':
            # Populate the list of errors to be shown in the Run Sim panel
            error_list = [entry for entry in unfiltered_item_list if entry.status]
            for error in error_list:
                mcell.run_simulation.error_list.add()
                mcell.run_simulation.error_list[
                    mcell.run_simulation.active_err_index].name = error.status
                mcell.run_simulation.active_err_index += 1
            #item_list = unfiltered_item_list
            item_list = [entry for entry in unfiltered_item_list if not entry.status]
        # Filter out invalid/illegal entries.
        elif mcell.cellblender_preferences.invalid_policy == 'filter':
            item_list = [entry for entry in unfiltered_item_list if not entry.status]
        # The user thinks they know better than CellBlender. Let them try to
        # export and run.
        elif mcell.cellblender_preferences.invalid_policy == 'ignore':
            item_list = unfiltered_item_list

    return item_list, error_list


def save_modular_or_allinone(filedir, main_mdl_file, mdl_filename,
                             save_function, args):
    """ Save output (either in main mdl or included mdl).

    This function helps reduce boilerplate code.

    args should contain everything the function will need except for the actual
    file to be written to, which will be inserted in this function.
    """

    mcell = bpy.context.scene.mcell
    settings = mcell.project_settings

    # Save modular (e.g. Scene.molecules.mdl, Scene.reactions.mdl)
    if mcell.export_project.export_format == 'mcell_mdl_modular':
        print ( "Saving as modular MDL files" )
        main_mdl_file.write("INCLUDE_FILE = \"%s.%s.mdl\"\n\n" %
                       (settings.base_name, mdl_filename))
        filepath = ("%s/%s.%s.mdl" %
                    (filedir, settings.base_name, mdl_filename))
        with open(filepath, "w", encoding="utf8", newline="\n") as mdl_file:
            # Maybe find a cleaner way to handle args list. Looks kind of ugly.
            args.insert(1, mdl_file)
            save_function(*args)
    # Or save everything in main mdl (e.g. Scene.main.mdl)
    else:
        print ( "Saving as one unified MDL file" )
        args.insert(1, main_mdl_file)
        save_function(*args)


def save_general(mdl_filename, save_function, save_state, unfiltered_item_list):
    """ Set the filter/ignore policy and write to mdl.
   
    This function helps reduce boilerplate code.
    """

    context = bpy.context    
    filedir = save_state['filedir']
    main_mdl_file = save_state['main_mdl_file']

    item_list, error_list = dontrun_filter_ignore(unfiltered_item_list)
    if item_list and not error_list:
        args = [context, item_list]

        # Add additional parameters here. Only save_reactions for now.
        if save_function.__name__ == 'save_reactions':
            args.append(filedir)

        save_modular_or_allinone(filedir, main_mdl_file, mdl_filename,
                                 save_function, args)

    return item_list


def save_partitions(context, out_file):
    """Export partitions"""

    mcell = context.scene.mcell

    if mcell.partitions.include:
        out_file.write("PARTITION_X = [[%.15g TO %.15g STEP %.15g]]\n" % (
            mcell.partitions.x_start, mcell.partitions.x_end,
            mcell.partitions.x_step))
        out_file.write("PARTITION_Y = [[%.15g TO %.15g STEP %.15g]]\n" % (
            mcell.partitions.y_start, mcell.partitions.y_end,
            mcell.partitions.y_step))
        out_file.write("PARTITION_Z = [[%.15g TO %.15g STEP %.15g]]\n\n" % (
            mcell.partitions.z_start, mcell.partitions.z_end,
            mcell.partitions.z_step))


def save_pbc(context, out_file):
    #Export the periodic boundary conditions

    mcell = context.scene.mcell
    ptrad = format(mcell.pbc.peri_trad)
    px = format(mcell.pbc.peri_x)
    py = format(mcell.pbc.peri_y)
    pz = format(mcell.pbc.peri_z)

    if mcell.pbc.include:
        out_file.write("PERIODIC_BOX\n")
        out_file.write("{\n")
        out_file.write("CORNERS = [%g,%g,%g]\n,[%g,%g,%g]\n" % (mcell.pbc.x_start,mcell.pbc.y_start,mcell.pbc.z_start,mcell.pbc.x_end,mcell.pbc.y_end,mcell.pbc.z_end))
        out_file.write("PERIODIC_TRADITIONAL = " + ptrad.upper() + "\n")
        out_file.write("PERIODIC_X = " + px.upper() + "\n")
        out_file.write("PERIODIC_Y = " + py.upper() + "\n")
        out_file.write("PERIODIC_Z = " + pz.upper() + "\n")
        out_file.write("}\n\n")


def save_wrapper(context, out_file, filedir):
    """ This function saves the current model to MDL.

    It provides a wrapper assembling the final mdl piece by piece.

    """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    export_project = mcell.export_project
    project_settings = mcell.project_settings
    ps = mcell.parameter_system
    error_list = mcell.run_simulation.error_list
    error_list.clear()
    mcell.run_simulation.active_err_index = 0
    invalid_policy = mcell.cellblender_preferences.invalid_policy
    save_state = {'main_mdl_file': out_file, 'filedir': filedir}


    scripting = mcell.scripting

    dm = None

    if scripting.needs_a_data_model():
      # Only build a data model if running Python code?
      dm = { 'mcell': mcell.build_data_model_from_properties ( context ) }


    scripting.write_scripting_output ( 'before', 'everything', context, out_file, filedir, dm )
    
    scripting.write_scripting_output ( 'before', 'parameters', context, out_file, filedir, dm )

    # Export parameters: 
    if ps and ps.general_parameter_list:
        args = [ps]
        save_modular_or_allinone(
            filedir, out_file, 'parameters', save_general_parameters, args)

    scripting.write_scripting_output ( 'after', 'parameters', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'initialization', context, out_file, filedir, dm )

    # Export model initialization:
    out_file.write("ITERATIONS = %s\n" % (mcell.initialization.iterations.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    
    out_file.write("TIME_STEP = %s\n" % (mcell.initialization.time_step.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

    if mcell.initialization.vacancy_search_distance.get_expr(ps.panel_parameter_list) != '':
        out_file.write("VACANCY_SEARCH_DISTANCE = %s\n" % (mcell.initialization.vacancy_search_distance.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    else:
        out_file.write("VACANCY_SEARCH_DISTANCE = 10\n\n") # DB: added to avoid error (I think it should have a default value to avoid error in most of the reaction networks)

    # Export optional initialization commands:
    args = [context]

    save_modular_or_allinone(filedir, out_file, 'initialization', save_initialization_commands, args)
    
    scripting.write_scripting_output ( 'after', 'initialization', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'partitions', context, out_file, filedir, dm )

    save_partitions(context, out_file)

    scripting.write_scripting_output ( 'after', 'partitions', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'pbc', context, out_file, filedir, dm )

    save_pbc(context, out_file)

    scripting.write_scripting_output ( 'after', 'pbc', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'molecules', context, out_file, filedir, dm )

    # Export molecules:
    unfiltered_mol_list = mcell.molecules.molecule_list
    save_general('molecules', save_molecules, save_state, unfiltered_mol_list)

    scripting.write_scripting_output ( 'after', 'molecules', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'surface_classes', context, out_file, filedir, dm )

    # Export surface classes:
    unfiltered_surf_class_list = mcell.surface_classes.surf_class_list
    surf_class_list = save_general(
        'surface_classes', save_surface_classes, save_state,
        unfiltered_surf_class_list)

    scripting.write_scripting_output ( 'after', 'surface_classes', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'reactions', context, out_file, filedir, dm )

    # Export reactions:
    unfiltered_rxn_list = mcell.reactions.reaction_list
    save_general('reactions', save_reactions, save_state, unfiltered_rxn_list)

    scripting.write_scripting_output ( 'after', 'reactions', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'geometry', context, out_file, filedir, dm )

    # Export model geometry:
    unfiltered_object_list = context.scene.mcell.model_objects.object_list
    object_list = save_general(
        'geometry', save_geometry, save_state, unfiltered_object_list)

    scripting.write_scripting_output ( 'after', 'geometry', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'mod_surf_regions', context, out_file, filedir, dm )

    # Export modify surface regions:
    if surf_class_list:
        unfiltered_msr_list = mcell.mod_surf_regions.mod_surf_regions_list
        save_general('mod_surf_regions', save_mod_surf_regions, save_state,
                     unfiltered_msr_list)

    scripting.write_scripting_output ( 'after', 'mod_surf_regions', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'release_patterns', context, out_file, filedir, dm )

    # Export release patterns:
    unfiltered_rel_pattern_list = mcell.release_patterns.release_pattern_list
    save_general('release_patterns', save_rel_patterns, save_state,
                 unfiltered_rel_pattern_list)

    scripting.write_scripting_output ( 'after', 'release_patterns', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'instantiate', context, out_file, filedir, dm )

    # Instantiate Model Geometry and Release sites:
    unfiltered_release_site_list = mcell.release_sites.mol_release_list
    release_site_list, _ = dontrun_filter_ignore(unfiltered_release_site_list)

    if object_list or release_site_list:
        out_file.write("INSTANTIATE %s OBJECT\n" % (context.scene.name))
        out_file.write("{\n")

        if object_list:
            save_object_list(context, out_file, object_list)

        scripting.write_scripting_output ( 'before', 'release_sites', context, out_file, filedir, dm )

        if release_site_list:
            save_release_site_list(context, out_file, release_site_list, mcell)

        scripting.write_scripting_output ( 'after', 'release_sites', context, out_file, filedir, dm )

        out_file.write("}\n\n")

    scripting.write_scripting_output ( 'after', 'instantiate', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'seed', context, out_file, filedir, dm )

    out_file.write("sprintf(seed,\"%05g\",SEED)\n\n")

    scripting.write_scripting_output ( 'after', 'seed', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'viz_output', context, out_file, filedir, dm )

    # Export viz output:

    unfiltered_mol_list = mcell.molecules.molecule_list
    unfiltered_mol_viz_list = [
        mol for mol in unfiltered_mol_list if mol.export_viz]
    molecule_viz_list, _ = dontrun_filter_ignore(unfiltered_mol_viz_list)
    molecule_viz_str_list = [mol.name for mol in molecule_viz_list]

    export_all = mcell.viz_output.export_all
    export_all_ascii = mcell.initialization.export_all_ascii
    if export_all or molecule_viz_list or export_all_ascii:
        args = [context, molecule_viz_str_list, export_all, export_all_ascii]
        save_modular_or_allinone(
            filedir, out_file, 'viz_output', save_viz_output_mdl, args)

    scripting.write_scripting_output ( 'after', 'viz_output', context, out_file, filedir, dm )
    scripting.write_scripting_output ( 'before', 'rxn_output', context, out_file, filedir, dm )

    # Export reaction output:
    settings = mcell.project_settings
    unfiltered_rxn_output_list = mcell.rxn_output.rxn_output_list

    save_general('rxn_output', save_rxn_output_mdl, save_state, unfiltered_rxn_output_list)

    scripting.write_scripting_output ( 'after', 'rxn_output', context, out_file, filedir, dm )

    scripting.write_scripting_output ( 'after', 'everything', context, out_file, filedir, dm )
                 
    """
    #deprecated
    #JJT:temporary solution for complex output expressions
    complex_rxn_output_list = mcell.rxn_output.complex_rxn_output_list
    if len(complex_rxn_output_list) > 0:
        save_modular_or_allinone(filedir, out_file, 'rxn_output',
                                 save_rxn_output_temp_mdl,[context, complex_rxn_output_list])
    """

    if error_list and invalid_policy == 'dont_run':
        # If anything is invalid, delete all the MDLs.
        project_dir = mcell_files_path()
        try:
            shutil.rmtree(project_dir)
        except:
            pass

    #if mcell.cellblender_preferences.filter_invalid:
    #    rxn_output_list = [
    #        rxn for rxn in unfiltered_rxn_output_list if not rxn.status]
    #else:
    #    rxn_output_list = unfiltered_rxn_output_list

    #if (rxn_output_list and export_project.export_format == 'mcell_mdl_modular'):
    #    out_file.write("INCLUDE_FILE = \"%s.rxn_output.mdl\"\n\n" %
    #                   (settings.base_name))
    #    filepath = ("%s/%s.rxn_output.mdl" % (filedir, settings.base_name))
    #    with open(
    #            filepath, "w", encoding="utf8", newline="\n") as mod_rxn_file:
    #        save_rxn_output_mdl(context, mod_rxn_file, rxn_output_list)
    #else:
    #    save_rxn_output_mdl(context, out_file, rxn_output_list)


def save_initialization_commands(context, out_file):
    """ Save the advanced/optional initialization commands.

        This also includes notifications and warnings.

    """

    mcell = context.scene.mcell
    init = mcell.initialization
    ps = mcell.parameter_system
    # Maximum Time Step
    if init.time_step_max.get_expr(ps.panel_parameter_list) != '':
        out_file.write("TIME_STEP_MAX = %s\n" % (init.time_step_max.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Space Step
    if init.space_step.get_expr(ps.panel_parameter_list) != '':
        out_file.write("SPACE_STEP = %s\n" % (init.space_step.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Interaction Radius
    if init.interaction_radius.get_expr(ps.panel_parameter_list) != '':
        out_file.write("INTERACTION_RADIUS = %s\n" % (init.interaction_radius.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Radial Directions
    if init.radial_directions.get_expr(ps.panel_parameter_list) != '':
        out_file.write("RADIAL_DIRECTIONS = %s\n" % (init.radial_directions.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Radial Subdivisions
    if init.radial_subdivisions.get_expr(ps.panel_parameter_list) != '':
        out_file.write("RADIAL_SUBDIVISIONS = %s\n" % (init.radial_subdivisions.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Vacancy Search Distance
    if init.vacancy_search_distance.get_expr(ps.panel_parameter_list) != '':
        out_file.write("VACANCY_SEARCH_DISTANCE = %s\n" % (init.vacancy_search_distance.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Surface Grid Density
    out_file.write("SURFACE_GRID_DENSITY = %s\n" % (init.surface_grid_density.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
    # Accurate 3D Reactions
    if init.accurate_3d_reactions:
        out_file.write("ACCURATE_3D_REACTIONS = TRUE\n")
    else:
        out_file.write("ACCURATE_3D_REACTIONS = FALSE\n")
    # Center Molecules on Grid
    if init.center_molecules_grid:
        out_file.write("CENTER_MOLECULES_ON_GRID = TRUE\n")
    else:
        out_file.write("CENTER_MOLECULES_ON_GRID = FALSE\n")
    # Microscopic Reversibility
    out_file.write("MICROSCOPIC_REVERSIBILITY = %s\n\n" %
                   (init.microscopic_reversibility))

    # Notifications
    out_file.write("NOTIFICATIONS\n{\n")
    if init.all_notifications == 'INDIVIDUAL':

        # Probability Report
        if init.probability_report == 'THRESHOLD':
            out_file.write("   PROBABILITY_REPORT_THRESHOLD = %.15g\n" % (
                init.probability_report_threshold))
        else:
            out_file.write("   PROBABILITY_REPORT = %s\n" % (
                init.probability_report))
        # Diffusion Constant Report
        out_file.write("   DIFFUSION_CONSTANT_REPORT = %s\n" % (
            init.diffusion_constant_report))
        # File Output Report
        if init.file_output_report:
            out_file.write("   FILE_OUTPUT_REPORT = ON\n")
        else:
            out_file.write("   FILE_OUTPUT_REPORT = OFF\n")
        # Final Summary
        if init.final_summary:
            out_file.write("   FINAL_SUMMARY = ON\n")
        else:
            out_file.write("   FINAL_SUMMARY = OFF\n")
        # Iteration Report
        if init.iteration_report:
            out_file.write("   ITERATION_REPORT = ON\n")
        else:
            out_file.write("   ITERATION_REPORT = OFF\n")
        # Partition Location Report
        if init.partition_location_report:
            out_file.write("   PARTITION_LOCATION_REPORT = ON\n")
        else:
            out_file.write("   PARTITION_LOCATION_REPORT = OFF\n")
        # Varying Probability Report
        if init.varying_probability_report:
            out_file.write("   VARYING_PROBABILITY_REPORT = ON\n")
        else:
            out_file.write("   VARYING_PROBABILITY_REPORT = OFF\n")
        # Progress Report
        if init.progress_report:
            out_file.write("   PROGRESS_REPORT = ON\n")
        else:
            out_file.write("   PROGRESS_REPORT = OFF\n")
        # Release Event Report
        if init.release_event_report:
            out_file.write("   RELEASE_EVENT_REPORT = ON\n")
        else:
            out_file.write("   RELEASE_EVENT_REPORT = OFF\n")
        # Release Event Report
        if init.molecule_collision_report:
            out_file.write("   MOLECULE_COLLISION_REPORT = ON\n")
        else:
            out_file.write("   MOLECULE_COLLISION_REPORT = OFF\n")

    else:
        out_file.write(
            "   ALL_NOTIFICATIONS = %s\n" % (init.all_notifications))
    out_file.write('}\n\n')

    # Warnings
    out_file.write("WARNINGS\n{\n")
    if init.all_warnings == 'INDIVIDUAL':

        # Degenerate Polygons
        out_file.write(
            "   DEGENERATE_POLYGONS = %s\n" % init.degenerate_polygons)
        # Negative Diffusion Constant
        out_file.write("   NEGATIVE_DIFFUSION_CONSTANT = %s\n"
                       % init.negative_diffusion_constant)
        # Missing Surface Orientation
        out_file.write("   MISSING_SURFACE_ORIENTATION = %s\n"
                       % init.missing_surface_orientation)
        # Negative Reaction Rate
        out_file.write("   NEGATIVE_REACTION_RATE = %s\n"
                       % init.negative_reaction_rate)
        # Useless Volume Orientation
        out_file.write("   USELESS_VOLUME_ORIENTATION = %s\n"
                       % init.useless_volume_orientation)
        # High Reaction Probability
        out_file.write("   HIGH_REACTION_PROBABILITY = %s\n"
                       % init.high_reaction_probability)
        # Lifetime Too Short
        out_file.write("   LIFETIME_TOO_SHORT = %s\n"
                       % init.lifetime_too_short)
        if init.lifetime_too_short == 'WARNING':
            out_file.write("   LIFETIME_THRESHOLD = %s\n"
                           % init.lifetime_threshold)
        # Missed Reactions
        out_file.write("   MISSED_REACTIONS = %s\n" % init.missed_reactions)
        if init.missed_reactions == 'WARNING':
            out_file.write("   MISSED_REACTION_THRESHOLD = %.15g\n"
                           % init.missed_reaction_threshold)
    else:
        out_file.write(
            "   ALL_WARNINGS = %s\n" % (init.all_warnings))
    out_file.write('}\n\n')


def save_object_list(context, out_file, object_list):
    """ Save the list objects to mdl output file """

    for item in object_list:
        out_file.write("  %s OBJECT %s {}\n" % (item.name, item.name))


def save_release_site_list(context, out_file, release_site_list, mcell):
    """ Save the list of release site to mdl output file. """

    mol_list = mcell.molecules.molecule_list
    ps = mcell.parameter_system

    for release_site in release_site_list:
        out_file.write("  %s RELEASE_SITE\n" % (release_site.name))
        out_file.write("  {\n")


        print ( "release_site.shape = " + release_site.shape )
        
        # Always need the molecule, so do it first
        mol_spec = None
        if release_site.molecule in mol_list:
            if mol_list[release_site.molecule].type == '2D':
                mol_spec = "%s%s" % (release_site.molecule, release_site.orient)
            else:
                mol_spec = "%s" % (release_site.molecule)


        # release sites with predefined shapes or list shapes
        if ((release_site.shape == 'LIST') |
            (release_site.shape == 'CUBIC') |
            (release_site.shape == 'SPHERICAL') |
            (release_site.shape == 'SPHERICAL_SHELL')):

            out_file.write("   SHAPE = %s\n" % (release_site.shape))
            if release_site.shape != 'LIST':
                out_file.write("   LOCATION = [%s, %s, %s]\n" %
                               (release_site.location_x.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions),
                                release_site.location_y.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions),
                                release_site.location_z.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
            out_file.write("   SITE_DIAMETER = %s\n" %
                           (release_site.diameter.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        # user defined shapes
        if (release_site.shape == 'OBJECT'):
            inst_obj_expr = instance_object_expr(context, release_site.object_expr)
            out_file.write("   SHAPE = %s\n" % (inst_obj_expr))

        if (release_site.shape == 'LIST'):
            out_file.write("   MOLECULE_POSITIONS\n")
            out_file.write("   {\n")
            for p in release_site.points_list:
                out_file.write("     %s [%.15g, %.15g, %.15g]\n" % ( mol_spec, p.x, p.y, p.z ) )
            out_file.write("   }\n")
        else:
            out_file.write("   MOLECULE = %s\n" % (mol_spec))

            if release_site.quantity_type == 'NUMBER_TO_RELEASE':
                out_file.write("   NUMBER_TO_RELEASE = %s\n" %
                           (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

            elif release_site.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
                out_file.write("   GAUSSIAN_RELEASE_NUMBER\n")
                out_file.write("   {\n")
                out_file.write("        MEAN_NUMBER = %s\n" %
                               (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
                out_file.write("        STANDARD_DEVIATION = %s\n" %
                               (release_site.stddev.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
                out_file.write("   }\n")

            elif release_site.quantity_type == 'DENSITY':
                if release_site.molecule in mol_list:
                    if mol_list[release_site.molecule].type == '2D':
                        out_file.write("   DENSITY = %s\n" %
                                   (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))
                    else:
                        out_file.write("   CONCENTRATION = %s\n" %
                                   (release_site.quantity.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        out_file.write("   RELEASE_PROBABILITY = %s\n" %
                       (release_site.probability.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)))

        if release_site.pattern:
            out_file.write("   RELEASE_PATTERN = %s\n" %
                           (release_site.pattern))

        out_file.write('  }\n')


def write_parameter_as_mdl_old ( p, out_file, as_expr ):
    """ Writes a single parameter as MDL as either a value or an expression """

    # Export Parameter:
    if as_expr:
        # Note that some expressions are allowed to be blank which indicates use of the default VALUE
        if len(p.expr.strip()) <= 0:
            # The expression is blank, so use the value which should be the default
            out_file.write("%s = %.15g" % (p.par_name, p.value))
        else:
            # The expression is not blank, so use it
            out_file.write("%s = %s" % (p.par_name, p.expr))
    else:
        # Output the value rather than the expression
        out_file.write("%s = %.15g" % (p.par_name, p.value))

    if ((p.descr != "") | (p.units != "")):
        out_file.write("    /* ")

        if p.descr != "":
            out_file.write("%s " % (p.descr))

        if p.units != "":
            out_file.write("   units=%s" % (p.units))

        out_file.write(" */")
    out_file.write("\n")



"""

# This is the proper release version of this function
def write_parameter_as_mdl ( par_name, p, out_file, as_expr ):
    # Writes a single parameter as MDL as either a value or an expression

    # Export Parameter:
    if as_expr:
        # Note that some expressions are allowed to be blank which indicates use of the default VALUE
        if len(p['expr'].strip()) <= 0:
            # The expression is blank, so use the value which should be the default
            out_file.write("%s = %.15g" % (par_name, p['value']))
        else:
            # The expression is not blank, so use it
            out_file.write("%s = %s" % (par_name, p['expr']))
    else:
        # Output the value rather than the expression
        out_file.write("%s = %.15g" % (par_name, p['value']))

    if ((p['desc'] != "") | (p['units'] != "")):
        out_file.write("    /* ")

        if p['desc'] != "":
            out_file.write("%s " % (p['desc']))

        if p['units'] != "":
            out_file.write("   units=%s" % (p['units']))

        out_file.write(" */")
    out_file.write("\n")


"""

# This temporary version uses a flag to force output with Blender's precision
def write_parameter_as_mdl ( par_name, p, out_file, as_expr ):
    # Writes a single parameter as MDL as either a value or an expression
    force_blender_precision = False

    # Export Parameter:
    if as_expr:
        # Note that some expressions are allowed to be blank which indicates use of the default VALUE
        if len(p['expr'].strip()) <= 0:
            # The expression is blank, so use the value which should be the default
            if force_blender_precision:
                mcell = bpy.context.scene.mcell
                out_file.write("%s = %.15g" % (par_name, mcell.blender_float(p['value'])))
            else:
                out_file.write("%s = %.15g" % (par_name, p['value']))
        else:
            # The expression is not blank, so use it
            out_file.write("%s = %s" % (par_name, p['expr']))
    else:
        # Output the value rather than the expression
        if force_blender_precision:
            mcell = bpy.context.scene.mcell
            out_file.write("%s = %.15g" % (par_name, mcell.blender_float(p['value'])))
        else:
            out_file.write("%s = %.15g" % (par_name, p['value']))

    if ((p['desc'] != "") | (p['units'] != "")):
        out_file.write("    /* ")

        if p['desc'] != "":
            out_file.write("%s " % (p['desc']))

        if p['units'] != "":
            out_file.write("   units=%s" % (p['units']))

        out_file.write(" */")
    out_file.write("\n")



def save_general_parameters(ps, out_file):
    """ Saves parameter info to mdl output file. """

    # Export Parameters:
    if ps and ps.general_parameter_list:
                
        if not ps.export_as_expressions:

            # Output as values ... order doesn't matter
            out_file.write("/* DEFINE PARAMETERS */\n")
            for p in ps.general_parameter_list:
                #print ( "Writing id = " + str(p.par_id) )
                write_parameter_as_mdl ( p.name, ps['gp_dict'][p.par_id], out_file, ps.export_as_expressions )
            out_file.write("\n")

        else:

            #ordered_names = ps.build_dependency_ordered_name_list()
            ordered_names = None
            if 'gp_ordered_list' in ps:
                ordered_names = ps['gp_ordered_list']
            #print ( "Ordered names = " + str(ordered_names) )
            out_file.write("/* DEFINE PARAMETERS */\n")
            if ordered_names == None:
                #print ( "Warning: Unable to export as expressions." )
                # Output as values ... order doesn't matter
                for p in ps.general_parameter_list:
                    #print ( "Writing id = " + str(p.par_id) )
                    write_parameter_as_mdl ( p.name, ps['gp_dict'][p.par_id], out_file, False )
            else:
                # Output as expressions where order matters
                for pn in ordered_names:
                    p = ps['gp_dict'][pn]
                    #print ( "Writing id = " + str(pn) )
                    write_parameter_as_mdl ( p['name'], ps['gp_dict'][pn], out_file, ps.export_as_expressions )
            out_file.write("\n")


def save_molecules(context, out_file, mol_list):
    """ Saves molecule info to mdl output file. """

    # Export Molecules:
    out_file.write("DEFINE_MOLECULES\n")
    out_file.write("{\n")

    ps = context.scene.mcell.parameter_system

    for mol_item in mol_list:
        out_file.write("  %s\n" % (mol_item.name))
        out_file.write("  {\n")

        if mol_item.type == '2D':
            out_file.write("    DIFFUSION_CONSTANT_2D = %s\n" %
                           (mol_item.diffusion_constant.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))
        else:
            out_file.write("    DIFFUSION_CONSTANT_3D = %s\n" %
                           (mol_item.diffusion_constant.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))

        if mol_item.custom_time_step.get_value(ps.panel_parameter_list) > 0:
            out_file.write("    CUSTOM_TIME_STEP = %s\n" %
                           (mol_item.custom_time_step.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))
        elif mol_item.custom_space_step.get_value(ps.panel_parameter_list) > 0:
            out_file.write("    CUSTOM_SPACE_STEP = %s\n" %
                           (mol_item.custom_space_step.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))

        if mol_item.target_only:
            out_file.write("    TARGET_ONLY\n")

        if mol_item.maximum_step_length.get_expr(ps.panel_parameter_list) != '':
            out_file.write("    MAXIMUM_STEP_LENGTH = %s\n" %
                           (mol_item.maximum_step_length.get_as_string_or_value(
                            ps.panel_parameter_list, ps.export_as_expressions)))

        out_file.write("  }\n")
    out_file.write("}\n\n")


def save_surface_classes(context, out_file, surf_class_list):
    """ Saves surface class info to mdl output file. """

    mcell = context.scene.mcell

    ps = mcell.parameter_system

    out_file.write("DEFINE_SURFACE_CLASSES\n")
    out_file.write("{\n")
    for active_surf_class in surf_class_list:
        out_file.write("  %s\n" % (active_surf_class.name))
        out_file.write("  {\n")
        unfiltered_surf_class_props_list = \
            active_surf_class.surf_class_props_list
        surf_class_props_list, _ = dontrun_filter_ignore(
            unfiltered_surf_class_props_list)
        for surf_class_props in surf_class_props_list:
            molecule = surf_class_props.molecule
            affected_mols = surf_class_props.affected_mols
            if affected_mols != 'SINGLE':
                molecule = affected_mols
            orient = surf_class_props.surf_class_orient
            surf_class_type = surf_class_props.surf_class_type
            if surf_class_type == 'CLAMP_CONCENTRATION':
                clamp_value = surf_class_props.clamp_value.get_as_string_or_value(
                              ps.panel_parameter_list, ps.export_as_expressions)
                out_file.write("    %s" % surf_class_type)
                out_file.write(   " %s%s = %s\n" % (molecule,
                                                    orient,
                                                    clamp_value))
            else:
                out_file.write("    %s = %s%s\n" % (surf_class_type,
                                                    molecule, orient))
        out_file.write("  }\n")
    out_file.write("}\n\n")


def save_rel_patterns(context, out_file, release_pattern_list):
    """ Saves release pattern info to mdl output file. """

    mcell = context.scene.mcell

    ps = mcell.parameter_system
    for active_release_pattern in release_pattern_list:
        out_file.write("DEFINE_RELEASE_PATTERN %s\n" %
                       (active_release_pattern.name))
        out_file.write("{\n")

        out_file.write(
            "  DELAY = %s\n" % active_release_pattern.delay.get_as_string_or_value(
            ps.panel_parameter_list, ps.export_as_expressions))

        if active_release_pattern.release_interval.get_expr(ps.panel_parameter_list) != '':
            out_file.write(
                "  RELEASE_INTERVAL = %s\n" %
                active_release_pattern.release_interval.get_as_string_or_value(
                ps.panel_parameter_list,ps.export_as_expressions))

        if active_release_pattern.train_duration.get_expr(ps.panel_parameter_list) != '':
            out_file.write(
                "  TRAIN_DURATION = %s\n" %
                active_release_pattern.train_duration.get_as_string_or_value(
                ps.panel_parameter_list,ps.export_as_expressions))

        if active_release_pattern.train_interval.get_expr(ps.panel_parameter_list) != '':
            out_file.write(
                "  TRAIN_INTERVAL = %s\n" %
                active_release_pattern.train_interval.get_as_string_or_value(
                ps.panel_parameter_list,ps.export_as_expressions))

        out_file.write(
            "  NUMBER_OF_TRAINS = %s\n" %
            active_release_pattern.number_of_trains.get_as_string_or_value(
            ps.panel_parameter_list,ps.export_as_expressions))

        out_file.write("}\n\n")


def save_reactions(context, out_file, rxn_list, filedir):
    """ Saves reaction info to mdl output file. """

    out_file.write("DEFINE_REACTIONS\n")
    out_file.write("{\n")

    # ps = context.scene.mcell.parameter_system

    for rxn_item in rxn_list:
        rxn_item.write_to_mdl_file ( context, out_file, filedir )
        
    out_file.write("}\n\n")


def save_geometry(context, out_file, object_list):
    """ Saves geometry info to mdl output file. """

    # Export Model Geometry:
    for object_item in object_list:

        data_object = context.scene.objects[object_item.name]

        if data_object.type == 'MESH':

            # NOTE (Markus): I assume this is what is happening
            # here. We need to unhide objects (if hidden) during
            # writing and then restore the state in the end.
            saved_hide_status = data_object.hide
            data_object.hide = False

            context.scene.objects.active = data_object
            bpy.ops.object.mode_set(mode='OBJECT')

            # Begin POLYGON_LIST block
            out_file.write("%s POLYGON_LIST\n" % (data_object.name))
            out_file.write("{\n")

            # write vertex list
            out_file.write("  VERTEX_LIST\n")
            out_file.write("  {\n")
            mesh = data_object.data
            matrix = data_object.matrix_world
            vertices = mesh.vertices
            for v in vertices:
                t_vec = matrix * v.co
                out_file.write("    [ %.15g, %.15g, %.15g ]\n" %
                               (t_vec.x, t_vec.y, t_vec.z))

            # close VERTEX_LIST block
            out_file.write("  }\n")

            # write element connection
            out_file.write("  ELEMENT_CONNECTIONS\n")
            out_file.write("  {\n")

            faces = mesh.polygons
            for f in faces:
                out_file.write("    [ %d, %d, %d ]\n" %
                               (f.vertices[0], f.vertices[1],
                                f.vertices[2]))

            # close ELEMENT_CONNECTIONS block
            out_file.write("  }\n")

            # write regions
            # regions = get_regions(data_object)
            regions = data_object.mcell.get_regions_dictionary(data_object)
            if regions:
                out_file.write("  DEFINE_SURFACE_REGIONS\n")
                out_file.write("  {\n")

                region_names = [k for k in regions.keys()]
                region_names.sort()
                for region_name in region_names:
                    out_file.write("    %s\n" % (region_name))
                    out_file.write("    {\n")
                    out_file.write("      ELEMENT_LIST = " +
                                   str(regions[region_name])+'\n')
                    out_file.write("    }\n")

                # close SURFACE_REGIONS block
                out_file.write("  }\n")

            # close POLYGON_LIST block
            out_file.write("}\n\n")

            # restore proper object visibility state
            data_object.hide = saved_hide_status


def save_viz_output_mdl(context, out_file, molecule_viz_list, export_all, export_all_ascii):
    """ Saves visualizaton output info to mdl output file. """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    ps = mcell.parameter_system
    start = mcell.viz_output.start.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)
    end   = mcell.viz_output.end.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)
    step  = mcell.viz_output.step.get_as_string_or_value(ps.panel_parameter_list,ps.export_as_expressions)
    all_iterations = mcell.viz_output.all_iterations

    if molecule_viz_list or export_all:
        out_file.write("VIZ_OUTPUT\n{\n")
        out_file.write("  MODE = CELLBLENDER\n")
        out_file.write("  FILENAME = \"./viz_data/seed_\" & seed & \"/%s\"\n" % settings.base_name)
        out_file.write("  MOLECULES\n")
        out_file.write("  {\n")
        if export_all:
            out_file.write("    NAME_LIST {ALL_MOLECULES}\n")
        else:
            out_file.write("    NAME_LIST {%s}\n" % " ".join(molecule_viz_list))
        if all_iterations:
            out_file.write(
                "    ITERATION_NUMBERS {ALL_DATA @ ALL_ITERATIONS}\n")
        else:
            out_file.write(
                "    ITERATION_NUMBERS {ALL_DATA @ [[%s TO %s STEP %s]]}\n" %
                (start, end, step))
        out_file.write("  }\n")
        out_file.write("}\n\n")

    # New viz block if we also output ascii
    if export_all_ascii:
        out_file.write("VIZ_OUTPUT\n{\n")
        out_file.write("  MODE = ASCII\n")
        out_file.write("  FILENAME = \"./viz_data_ascii/seed_\" & seed & \"/%s\"\n" % settings.base_name)
        out_file.write("  MOLECULES\n")
        out_file.write("  {\n")
        out_file.write("    NAME_LIST {ALL_MOLECULES}\n")
        if all_iterations:
            out_file.write(
                "    ITERATION_NUMBERS {ALL_DATA @ ALL_ITERATIONS}\n")
        else:
            out_file.write(
                "    ITERATION_NUMBERS {ALL_DATA @ [[%s TO %s STEP %s]]}\n" %
                (start, end, step))
        out_file.write("  }\n")
        out_file.write("}\n\n")

def save_rxn_output_mdl(context, out_file, rxn_output_list):
    """ Saves reaction output info to mdl output file. """

    mcell = context.scene.mcell
    ps = mcell.parameter_system

    out_file.write("REACTION_DATA_OUTPUT\n{\n")

    output_buf_size = mcell.rxn_output.output_buf_size.get_expr(ps.panel_parameter_list)
    if len(output_buf_size.strip()) > 0:
        # When not blank, convert it as a normal panel parameter
        output_buf_size = mcell.rxn_output.output_buf_size.get_as_string_or_value(
            ps.panel_parameter_list, ps.export_as_expressions)
        out_file.write("  OUTPUT_BUFFER_SIZE=%s\n" % output_buf_size)

    rxn_step = mcell.rxn_output.rxn_step.get_expr(ps.panel_parameter_list)
    if len(rxn_step.strip()) == 0:
        # When blank, use the system time step set in initialization
        rxn_step = mcell.initialization.time_step.get_as_string_or_value(
            ps.panel_parameter_list, ps.export_as_expressions)
    else:
        # When not blank, convert it as a normal panel parameter
        rxn_step = mcell.rxn_output.rxn_step.get_as_string_or_value(
            ps.panel_parameter_list, ps.export_as_expressions)
    out_file.write("  STEP=%s\n" % rxn_step)

    always_generate = mcell.rxn_output.always_generate
    for rxn_output in rxn_output_list:
        if always_generate or rxn_output.plotting_enabled:
            if rxn_output.rxn_or_mol == 'Reaction':
                count_name = rxn_output.reaction_name
            elif rxn_output.rxn_or_mol == 'Molecule':
                count_name = rxn_output.molecule_name
            elif rxn_output.rxn_or_mol == 'MDLString':
                outputStr = rxn_output.mdl_string
                output_file = rxn_output.mdl_file_prefix
                if outputStr not in ['', None]:
                    outputStr = '  {%s} =>  "./react_data/seed_" & seed & \"/%s_MDLString.dat\"\n' % (outputStr, output_file)
                    out_file.write(outputStr)
                else:
                    print('Found invalid reaction output {0}'.format(rxn_output.name))
                continue  ####   <=====-----  C O N T I N U E     H E R E  !!!!!
            elif rxn_output.rxn_or_mol == 'File':
                # No MDL is generated for plot items that are plain files
                continue  ####   <=====-----  C O N T I N U E     H E R E  !!!!!

            object_name = rxn_output.object_name
            region_name = rxn_output.region_name
            if rxn_output.count_location == 'World':
                out_file.write(
                    "  {COUNT[%s,WORLD]}=> \"./react_data/seed_\" & seed & "
                    "\"/%s.World.dat\"\n" % (count_name, count_name,))
            elif rxn_output.count_location == 'Object' and mcell.pbc.peri_trad == True:
                out_file.write(
                    "  {COUNT[%s,%s.%s]}=> \"./react_data/seed_\" & seed & "
                    "\"/%s.%s.dat\"\n" % (count_name, context.scene.name,object_name, count_name, object_name))
            elif rxn_output.count_location == 'Region' and mcell.pbc.peri_trad == True:
                out_file.write(
                    "  {COUNT[%s,%s.%s[%s]]}=> \"./react_data/seed_\" & seed & "
                    "\"/%s.%s.%s.dat\"\n" % (count_name, context.scene.name,object_name, region_name, count_name, object_name, region_name))
                
            elif rxn_output.count_location == 'Region' and mcell.pbc.peri_trad == False:
                    out_file.write("  {COUNT["+count_name+","+context.scene.name+"."+object_name+"["+region_name+"]"+",[%.15g,%.15g,%.15g]]" %(mcell.rxn_output.virt_x,mcell.rxn_output.virt_y,mcell.rxn_output.virt_z)
                     + "}=> \"./react_data/seed_\" & seed &  \"/%s.%s.%s.dat\"\n" %(count_name,object_name,region_name))
                    #(count_name, context.scene.name,object_name, count_name, object_name))
            elif rxn_output.count_location == 'Object' and mcell.pbc.peri_trad == False:
                    out_file.write("  {COUNT["+count_name+ ","+ context.scene.name+ "." + object_name + ",[%.15g,%.15g,%.15g]]" %(mcell.rxn_output.virt_x,mcell.rxn_output.virt_y,mcell.rxn_output.virt_z)
                     + "}=> \"./react_data/seed_\" & seed &  \"/%s.%s.%s_%s_%s.dat\"\n" %(count_name, object_name,mcell.rxn_output.virt_x,mcell.rxn_output.virt_y,mcell.rxn_output.virt_z))
                
    out_file.write("}\n\n")

""" 
#deprecated
def save_rxn_output_temp_mdl(context, out_file, rxn_output_list):
    #JJT:temporary code that outsputs imported rxn output expressions
    #remove when we figure out how to add this directly to the interface
    
    mcell = context.scene.mcell
    ps = mcell.parameter_system

    out_file.write("REACTION_DATA_OUTPUT\n{\n")
    rxn_step = mcell.rxn_output.rxn_step.get_as_string_or_value(
        ps.panel_parameter_list, ps.export_as_expressions)
    out_file.write("  STEP=%s\n" % rxn_step)

    
    for rxn_output in rxn_output_list:
        outputStr = rxn_output.molecule_name
        if outputStr not in ['',None]:
            outputStr = '{%s} =>  "./react_data/seed_" & seed & \"/%s.World.dat\"\n' % (outputStr,rxn_output.name)
            out_file.write(outputStr)
        else:
            print('Found invalid reaction output {0}'.format(outputStr))
    out_file.write("}\n\n")
"""

def save_mod_surf_regions(context, out_file, mod_surf_regions_list):
    """ Saves modify surface region info to mdl output file. """

    out_file.write("MODIFY_SURFACE_REGIONS\n")
    out_file.write("{\n")
    for active_mod_surf_regions in mod_surf_regions_list:
        surf_class_name = active_mod_surf_regions.surf_class_name
        object_name = active_mod_surf_regions.object_name
        region_name = active_mod_surf_regions.region_name
        if active_mod_surf_regions.region_selection == 'ALL':
            region_name = "ALL"
        out_file.write("  %s[%s]\n" % (object_name, region_name))
        out_file.write("  {\n    SURFACE_CLASS = %s\n  }\n" %
                       (surf_class_name))
    out_file.write("}\n\n")


def instance_object_expr(context, expression):
    """ Converts an object expression into an instantiated MDL object

    This function converts an object specification coming from
    the GUI into a fully qualified (instantiated) MDL expression.
    E.g., if the instantiated object is named *Scene*

      - an object *Cube* will be converted to *Scene.Cube* and
      - an expression *Cube + Sphere* will be converted to
        "Scene.Cube + Scene.Sphere"

    NOTE (Markus): I am not sure if this function isn't a bit
    too complex for the task (i.e. regular expressions and all)
    but perhaps it's fine. Time will tell.

    """

    token_spec = [
        ("ID", r"[A-Za-z]+[0-9A-Za-z_.]*(\[[A-Za-z]+[0-9A-Za-z_.]*\])?"),
                              # Identifiers
        ("PAR", r"[\(\)]"),   # Parentheses
        ("OP", r"[\+\*\-]"),  # Boolean operators
        ("SKIP", r"[ \t]"),   # Skip over spaces and tabs
    ]
    token_regex = "|".join("(?P<%s>%s)" % pair for pair in token_spec)
    get_token = re.compile(token_regex).match

    instantiated_expression = ""
    pos = 0
    line_start = 0
    m = get_token(expression)
    while m:
        token_type = m.lastgroup
        if token_type != "SKIP":
            val = m.group(token_type)

            if token_type == "ID":
                val = context.scene.name + "." + val
            elif token_type == "OP":
                val = " " + val + " "

            instantiated_expression = instantiated_expression + val

        pos = m.end()
        m = get_token(expression, pos)

    if pos != len(expression):
        pass

    return instantiated_expression
