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
# Contributors: Tom Bartol


"""
This script exports MCell MDL files from Blender, and is a component
of CellBlender.

"""

# python imports
import os
import re

# blender imports
import bpy


def get_regions(obj):
    """ return a dictionary with region names """

    reg_dict = {}
    obj_regs = obj.mcell.regions.region_list
    for reg in obj_regs:
        reg_dict[reg.name] = obj.data['mcell']['regions'][reg.name].to_list()

    return reg_dict


def save(operator, context, filepath=""):
    """ Top level function for saving the current MCell model
        as MDL.

    """

    with open(filepath, "w", encoding="utf8", newline="\n") as out_file:
        filedir = os.path.dirname(filepath)
        save_wrapper(context, out_file, filedir)

    return {'FINISHED'}


def save_wrapper(context, out_file, filedir):
    """ This function saves the current model to MDL.

    It provides a wrapper assembling the final mdl piece by piece.

    """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    export_project = mcell.export_project
    project_settings = mcell.project_settings

    # Export model initialization:
    out_file.write("ITERATIONS = %d\n" % (mcell.initialization.iterations))
    out_file.write("TIME_STEP = %g\n\n" % (mcell.initialization.time_step))

    # Export optional initialization commands:
    if export_project.export_format == 'mcell_mdl_modular':
        out_file.write("INCLUDE_FILE = \"%s.initialization.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.initialization.mdl" %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as init_file:
            save_initialization_commands(context, init_file)
    else:
        save_initialization_commands(context, out_file)

    # Export partitions:
    if mcell.partitions.include:
        out_file.write("PARTITION_X = [[%g TO %g STEP %g]]\n" % (
            mcell.partitions.x_start, mcell.partitions.x_end,
            mcell.partitions.x_step))
        out_file.write("PARTITION_Y = [[%g TO %g STEP %g]]\n" % (
            mcell.partitions.y_start, mcell.partitions.y_end,
            mcell.partitions.y_step))
        out_file.write("PARTITION_Z = [[%g TO %g STEP %g]]\n\n" % (
            mcell.partitions.z_start, mcell.partitions.z_end,
            mcell.partitions.z_step))

    # Export molecules:
    if export_project.export_format == 'mcell_mdl_modular':
        out_file.write("INCLUDE_FILE = \"%s.molecules.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.molecules.mdl" %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as mol_file:
            save_molecules(context, mol_file)
    else:
        save_molecules(context, out_file)

    # Export surface classes:
    unfiltered_surf_class_list = mcell.surface_classes.surf_class_list
    surf_class_list = [
        sc for sc in unfiltered_surf_class_list if not sc.status]
    have_surf_class = len(surf_class_list) != 0
    if have_surf_class and export_project.export_format == 'mcell_mdl_modular':
        out_file.write("INCLUDE_FILE = \"%s.surface_classes.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.surface_classes.mdl" %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as sc_file:
            save_surface_classes(context, sc_file, surf_class_list)
    else:
        save_surface_classes(context, out_file, surf_class_list)

    # Export reactions:
    unfiltered_rxn_list = mcell.reactions.reaction_list
    rxn_list = [rxn for rxn in unfiltered_rxn_list if not rxn.status]
    have_reactions = len(rxn_list) != 0
    if have_reactions and export_project.export_format == 'mcell_mdl_modular':
        out_file.write("INCLUDE_FILE = \"%s.reactions.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.reactions.mdl" %
                   (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as react_file:
            save_reactions(context, react_file, rxn_list)
    else:
        save_reactions(context, out_file, rxn_list)

    # Export model geometry:
    have_geometry = len(context.scene.mcell.model_objects.object_list) != 0
    if have_geometry and export_project.export_format == 'mcell_mdl_modular':
        out_file.write("INCLUDE_FILE = \"%s.geometry.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.geometry.mdl" %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as geom_file:
            save_geometry(context, geom_file)
    else:
        save_geometry(context, out_file)

    # Export modify surface regions:
    unfiltered_mod_surf_regions_list = \
        mcell.mod_surf_regions.mod_surf_regions_list
    mod_surf_regions_list = [
        msr for msr in unfiltered_mod_surf_regions_list if not msr.status]
    have_mod_surf_regions = len(mod_surf_regions_list) != 0
    if (have_mod_surf_regions and
            export_project.export_format == 'mcell_mdl_modular'):
        out_file.write("INCLUDE_FILE = \"%s.mod_surf_regions.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.mod_surf_regions.mdl" %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as mod_sr_file:
            save_mod_surf_regions(context, mod_sr_file)
    else:
        save_mod_surf_regions(context, out_file)

    # Instantiate Model Geometry and Release sites:
    object_list = mcell.model_objects.object_list
    unfiltered_release_site_list = mcell.release_sites.mol_release_list
    release_site_list = [
        rel for rel in unfiltered_release_site_list if not rel.status]
    if object_list or release_site_list:
        out_file.write("INSTANTIATE %s OBJECT\n" % (context.scene.name))
        out_file.write("{\n")

        if object_list:
            save_object_list(context, out_file, object_list)

        if release_site_list:
            save_release_site_list(context, out_file, release_site_list,
                                   mcell)

        out_file.write("}\n\n")

    out_file.write("sprintf(seed,\"%04g\",SEED)\n\n")

    # Include MDL files for viz and reaction output:
    molecule_list = mcell.molecules.molecule_list
    molecule_viz_list = [
        molecule.name for molecule in molecule_list if molecule.export_viz]
    if (molecule_viz_list and
            export_project.export_format == 'mcell_mdl_modular'):
        out_file.write("INCLUDE_FILE = \"%s.viz_output.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.viz_output.mdl" % (filedir, settings.base_name))
        with open(
                filepath, "w", encoding="utf8", newline="\n") as mod_viz_file:
            save_viz_output_mdl(context, mod_viz_file)
    else:
        save_viz_output_mdl(context, out_file)

    if (mcell.rxn_output.rxn_output_list and
            export_project.export_format == 'mcell_mdl_modular'):
        out_file.write("INCLUDE_FILE = \"%s.rxn_output.mdl\"\n\n" %
                       (settings.base_name))
        filepath = ("%s/%s.rxn_output.mdl" % (filedir, settings.base_name))
        with open(
                filepath, "w", encoding="utf8", newline="\n") as mod_rxn_file:
            save_rxn_output_mdl(context, mod_rxn_file)
    else:
        save_rxn_output_mdl(context, out_file)


def save_initialization_commands(context, out_file):
    """ Save the advanced/optional initialization commands.

        This also includes notifications and warnings.

    """

    init = context.scene.mcell.initialization
    # Maximum Time Step
    if init.time_step_max_str:
        out_file.write("TIME_STEP_MAX = %g\n" % (init.time_step_max))
    # Space Step
    if init.space_step_str:
        out_file.write("SPACE_STEP = %g\n" % (init.space_step))
    # Interaction Radius
    if init.interaction_radius_str:
        out_file.write("INTERACTION_RADIUS = %g\n" % (init.interaction_radius))
    # Radial Directions
    if init.radial_directions_str:
        out_file.write("RADIAL_DIRECTIONS = %d\n" % (init.radial_directions))
    # Radial Subdivisions
    if init.radial_subdivisions_str:
        out_file.write(
            "RADIAL_SUBDIVISIONS = %d\n" % (init.radial_subdivisions))
    # Vacancy Search Distance
    if init.vacancy_search_distance_str:
        out_file.write(
            "VACANCY_SEARCH_DISTANCE = %g\n" % (init.vacancy_search_distance))
    # Surface Grid Density
    out_file.write("SURFACE_GRID_DENSITY = %g\n" % (init.surface_grid_density))
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
            out_file.write("   PROBABILITY_REPORT_THRESHOLD = %g\n" % (
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
    if init.all_notifications == 'INDIVIDUAL':

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
            out_file.write("   MISSED_REACTION_THRESHOLD = %g\n"
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

    for release_site in release_site_list:
        out_file.write("  %s RELEASE_SITE\n" % (release_site.name))
        out_file.write("  {\n")

        # release sites with predefined shapes
        if ((release_site.shape == 'CUBIC') |
                (release_site.shape == 'SPHERICAL') |
                (release_site.shape == 'SPHERICAL_SHELL')):

            out_file.write("   SHAPE = %s\n" % (release_site.shape))
            out_file.write("   LOCATION = [%g, %g, %g]\n" %
                           (release_site.location[0],
                            release_site.location[1],
                           release_site.location[2]))
            out_file.write("   SITE_DIAMETER = %g\n" %
                           (release_site.diameter))

        # user defined shapes
        if (release_site.shape == 'OBJECT'):
            inst_obj_expr = instance_object_expr(context,
                                                 release_site.object_expr)
            out_file.write("   SHAPE = %s\n" % (inst_obj_expr))

        if release_site.molecule in mol_list:
            if mol_list[release_site.molecule].type == '2D':
                out_file.write("   MOLECULE = %s%s\n" % (release_site.molecule,
                                                         release_site.orient))
            else:
                out_file.write("   MOLECULE = %s\n" % (release_site.molecule))

        if release_site.quantity_type == 'NUMBER_TO_RELEASE':
            out_file.write("   NUMBER_TO_RELEASE = %d\n" %
                           (int(release_site.quantity)))

        elif release_site.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
            out_file.write("   GAUSSIAN_RELEASE_NUMBER\n")
            out_file.write("   {\n")
            out_file.write("        MEAN_NUMBER = %g\n" %
                           (release_site.quantity))
            out_file.write("        STANDARD_DEVIATION = %g\n" %
                           (release_site.stddev))
            out_file.write("      }\n")

        elif release_site.quantity_type == 'DENSITY':
            if release_site.molecule in mol_list:
                if mol_list[release_site.molecule].type == '2D':
                    out_file.write("   DENSITY = %g\n" %
                                   (release_site.quantity))
                else:
                    out_file.write("   CONCENTRATION = %g\n" %
                                   (release_site.quantity))

        out_file.write("   RELEASE_PROBABILITY = %g\n" %
                       (release_site.probability))

        if release_site.pattern:
            out_file.write("   RELEASE_PATTERN = %s\n" %
                           (release_site.pattern))

        out_file.write('  }\n')


def save_molecules(context, out_file):
    """ Saves molecule info to mdl output file. """

    mcell = context.scene.mcell

    # Export Molecules:
    unfiltered_mol_list = mcell.molecules.molecule_list
    mol_list = [mol for mol in unfiltered_mol_list if not mol.status]
    if mol_list:
        out_file.write("DEFINE_MOLECULES\n")
        out_file.write("{\n")

        for mol_item in mol_list:
            out_file.write("  %s\n" % (mol_item.name))
            out_file.write("  {\n")

            if mol_item.type == '2D':
                out_file.write("    DIFFUSION_CONSTANT_2D = %g\n" %
                               (mol_item.diffusion_constant))
            else:
                out_file.write("    DIFFUSION_CONSTANT_3D = %g\n" %
                               (mol_item.diffusion_constant))

            if mol_item.custom_time_step > 0:
                out_file.write("    CUSTOM_TIME_STEP = %g\n" %
                               (mol_item.custom_time_step))
            elif mol_item.custom_space_step > 0:
                out_file.write("    CUSTOM_SPACE_STEP = %g\n" %
                               (mol_item.custom_space_step))

            if mol_item.target_only:
                out_file.write("    TARGET_ONLY\n")

            out_file.write("  }\n")
        out_file.write("}\n\n")


def save_surface_classes(context, out_file, surf_class_list):
    """ Saves surface class info to mdl output file. """

    if surf_class_list:
        out_file.write("DEFINE_SURFACE_CLASSES\n")
        out_file.write("{\n")
        for active_surf_class in surf_class_list:
            out_file.write("  %s\n" % (active_surf_class.name))
            out_file.write("  {\n")
            unfiltered_surf_class_props_list = \
                active_surf_class.surf_class_props_list
            surf_class_props_list = [
                scp for scp in unfiltered_surf_class_props_list if not
                scp.status]
            for surf_class_props in surf_class_props_list:
                molecule = surf_class_props.molecule
                orient = surf_class_props.surf_class_orient
                surf_class_type = surf_class_props.surf_class_type
                if surf_class_type == 'CLAMP_CONCENTRATION':
                    clamp_value = surf_class_props.clamp_value
                    out_file.write("    %s\n" % surf_class_type)
                    out_file.write("    %s%s = %g\n" % (molecule,
                                                        orient,
                                                        clamp_value))
                else:
                    out_file.write("    %s = %s%s\n" % (surf_class_type,
                                                        molecule, orient))
            out_file.write("  }\n")
        out_file.write("}\n\n")
    return


def save_reactions(context, out_file, rxn_list):
    """ Saves reaction info to mdl output file. """

    if rxn_list:
        out_file.write("DEFINE_REACTIONS\n")
        out_file.write("{\n")

        for rxn_item in rxn_list:
            out_file.write("  %s " % (rxn_item.name))

            if rxn_item.type == 'irreversible':
                out_file.write("[%g]" % (rxn_item.fwd_rate))
            else:
                out_file.write("[>%g, <%g]" %
                               (rxn_item.fwd_rate, rxn_item.bkwd_rate))

            if rxn_item.rxn_name:
                out_file.write(" : %s\n" % (rxn_item.rxn_name))
            else:
                out_file.write("\n")

        out_file.write("}\n\n")


def save_geometry(context, out_file):
    """ Saves geometry info to mdl output file. """

    mcell = context.scene.mcell

    # Export Model Geometry:
    object_list = mcell.model_objects.object_list
    if object_list:

        for object_item in object_list:

            data_object = bpy.data.objects[object_item.name]

            if data_object.type == 'MESH':

                # NOTE (Markus): I assume this is what is happening
                # here. We need to unhide objects (if hidden) during
                # writing and then restore the state in the end.
                saved_hide_status = data_object.hide
                data_object.hide = False

                context.scene.objects.active = data_object
                bpy.ops.object.mode_set(mode='OBJECT')

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
                regions = get_regions(data_object)
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

                    out_file.write("  }\n")

                # close SURFACE_REGIONS block
                out_file.write("}\n\n")

                # restore proper object visibility state
                data_object.hide = saved_hide_status


def save_viz_output_mdl(context, out_file):
    """ Saves a visualization output MDL file """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    start = mcell.viz_output.start
    end = mcell.viz_output.end
    step = mcell.viz_output.step
    all_iterations = mcell.viz_output.all_iterations

    unfiltered_mol_list = mcell.molecules.molecule_list
    molecule_viz_list = [
        mol.name for mol in unfiltered_mol_list if mol.export_viz and
        not mol.status]

    if molecule_viz_list:
        out_file.write("VIZ_OUTPUT\n{\n")
        out_file.write("  MODE = CELLBLENDER\n")
        out_file.write("  FILENAME = \"./viz_data/%s\"\n" % settings.base_name)
        out_file.write("  MOLECULES\n")
        out_file.write("  {\n")
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

    return


def save_rxn_output_mdl(context, out_file):
    """ Saves a reaction output MDL file """

    mcell = context.scene.mcell
    settings = mcell.project_settings
    unfiltered_rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output_list = [
        rxn for rxn in unfiltered_rxn_output_list if not rxn.status]

    if rxn_output_list:
        out_file.write("REACTION_DATA_OUTPUT\n{\n")
        rxn_step = mcell.initialization.time_step
        out_file.write("  STEP=%g\n" % rxn_step)

        for rxn_output in rxn_output_list:
            molecule_name = rxn_output.molecule_name
            object_name = rxn_output.object_name
            region_name = rxn_output.region_name
            if rxn_output.count_location == 'World':
                out_file.write("  {COUNT[%s,WORLD]}=> \"./react_data/%s."
                               "World.\" & seed & \".dat\"\n" %
                               (molecule_name, molecule_name,))
            elif rxn_output.count_location == 'Object':
                out_file.write("  {COUNT[%s,%s.%s]}=> \"./react_data/%s."
                               "%s.\" & seed & \".dat\"\n" %
                               (molecule_name, context.scene.name, object_name,
                                molecule_name, object_name))
            elif rxn_output.count_location == 'Region':
                out_file.write("  {COUNT[%s,%s.%s[%s]]}=> \"./react_data/%s."
                               "%s.%s.\" & seed & \".dat\"\n" %
                               (molecule_name, context.scene.name, object_name,
                                region_name, molecule_name, object_name,
                                region_name))

        out_file.write("}\n\n")

    return


def save_mod_surf_regions(context, out_file):
    """ Saves modify surface region info to mdl output file. """

    mcell = context.scene.mcell
    unfiltered_mod_surf_regions_list = \
        mcell.mod_surf_regions.mod_surf_regions_list
    mod_surf_regions_list = [
        msr for msr in unfiltered_mod_surf_regions_list if not msr.status]
    if mod_surf_regions_list:
        out_file.write("MODIFY_SURFACE_REGIONS\n")
        out_file.write("{\n")
        for active_mod_surf_regions in mod_surf_regions_list:
            surf_class_name = active_mod_surf_regions.surf_class_name
            out_file.write("  %s[%s]\n" %
                           (active_mod_surf_regions.object_name,
                            active_mod_surf_regions.region_name))
            out_file.write("  {\n    SURFACE_CLASS = %s\n  }\n" %
                           (surf_class_name))
        out_file.write("}\n\n")

    return


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
