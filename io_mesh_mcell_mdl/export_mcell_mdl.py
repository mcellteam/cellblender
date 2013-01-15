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

    # export model initialization:
    out_file.write('ITERATIONS = %d\n' % (mcell.initialization.iterations))
    out_file.write('TIME_STEP = %g\n\n' % (mcell.initialization.time_step))

    # export molecules:
    if settings.export_format == 'mcell_mdl_modular':
        out_file.write('INCLUDE_FILE = \"%s.molecules.mdl\"\n\n' %
                       (settings.base_name))
        filepath = ('%s/%s.molecules.mdl' %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as mol_file:
            save_molecules(context, mol_file)
    else:
        save_molecules(context, out_file)

    # export surface classes
    have_surf_class = len(mcell.surface_classes.surf_class_list) != 0
    if have_surf_class and settings.export_format == 'mcell_mdl_modular':
        out_file.write('INCLUDE_FILE = \"%s.surface_classes.mdl\"\n\n' %
                       (settings.base_name))
        filepath = ('%s/%s.surface_classes.mdl' %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as mol_file:
            save_surface_classes(context, mol_file)

    # export reactions
    have_reactions = len(context.scene.mcell.reactions.reaction_list) != 0
    if have_reactions and settings.export_format == 'mcell_mdl_modular':
        out_file.write('INCLUDE_FILE = \"%s.reactions.mdl\"\n\n' %
                       (settings.base_name))
        filepath = ('%s/%s.reactions.mdl' %
                   (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as react_file:
            save_reactions(context, react_file)
    else:
        save_reactions(context, out_file)

    # export model geometry:
    if settings.export_format == 'mcell_mdl_modular':
        out_file.write('INCLUDE_FILE = \"%s.geometry.mdl\"\n\n' %
                       (settings.base_name))
        filepath = ('%s/%s.geometry.mdl' %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as geom_file:
            save_geometry(context, geom_file)
    else:
        save_geometry(context, out_file)

    # export modify surface regions
    have_mod_surf_reg = len(mcell.mod_surf_regions.mod_surf_regions_list) != 0
    if have_mod_surf_reg and settings.export_format == 'mcell_mdl_modular':
        out_file.write('INCLUDE_FILE = \"%s.mod_surf_regions.mdl\"\n\n' %
                       (settings.base_name))
        filepath = ('%s/%s.mod_surf_regions.mdl' %
                    (filedir, settings.base_name))
        with open(filepath, "w", encoding="utf8", newline="\n") as mol_file:
            save_mod_surf_regions(context, mol_file)

    # Instantiate Model Geometry and Release sites:
    object_list = mcell.model_objects.object_list
    release_site_list = mcell.release_sites.mol_release_list
    if (len(object_list) > 0) | (len(release_site_list) > 0):
        out_file.write('INSTANTIATE %s OBJECT\n' % (context.scene.name))
        out_file.write('{\n')

        if len(object_list) > 0:
            save_object_list(context, out_file, object_list)

        if len(release_site_list) > 0:
            save_release_site_list(context, out_file, release_site_list,
                                   mcell)

        out_file.write('}\n\n')

    # Include MDL files for viz and reaction output:
    if mcell.viz_output.include:
        out_file.write('INCLUDE_FILE = \"%s.viz_output.mdl\"\n\n' %
                       (settings.base_name))

    if mcell.rxn_output.include:
        out_file.write('INCLUDE_FILE = \"%s.rxn_output.mdl\"\n\n' %
                       (settings.base_name))


def save_object_list(context, out_file, object_list):
    """ Save the list objects to mdl output file """

    for item in object_list:
        out_file.write('  %s OBJECT %s {}\n' % (item.name, item.name))


def save_release_site_list(context, out_file, release_site_list, mcell):
    """ Save the list of release site to mdl output file. """

    for release_site in release_site_list:
        out_file.write('  %s RELEASE_SITE\n' % (release_site.name))
        out_file.write('  {\n')

        # release sites with predefined shapes
        if ((release_site.shape == 'CUBIC') |
                (release_site.shape == 'SPHERICAL') |
                (release_site.shape == 'SPHERICAL_SHELL')):

            out_file.write('   SHAPE = %s\n' % (release_site.shape))
            out_file.write('   LOCATION = [%g, %g, %g]\n' %
                           (release_site.location[0],
                            release_site.location[1],
                           release_site.location[2]))
            out_file.write('   SITE_DIAMETER = %g\n' %
                           (release_site.diameter))

        # user defined shapes
        if (release_site.shape == 'OBJECT'):
            inst_obj_expr = instance_object_expr(context,
                                                 release_site.object_expr)
            out_file.write('   SHAPE = %s\n' % (inst_obj_expr))

        out_file.write('   MOLECULE = %s\n' % (release_site.molecule))

        if release_site.quantity_type == 'NUMBER_TO_RELEASE':
            out_file.write('   NUMBER_TO_RELEASE = %d\n' %
                           (int(release_site.quantity)))

        elif release_site.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
            out_file.write('   GAUSSIAN_RELEASE_NUMBER\n')
            out_file.write('   {\n')
            out_file.write('        MEAN_NUMBER = %g\n' %
                           (release_site.quantity))
            out_file.write('        STANDARD_DEVIATION = %g\n' %
                           (release_site.stddev))
            out_file.write('      }\n')

        elif release_site.quantity_type == 'DENSITY':
            mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
            m = re.match(mol_filter, release_site.molecule)
            mol_name = m.group(1)
            if mcell.molecules.molecule_list[mol_name].type == '2D':
                out_file.write('   DENSITY = %g\n' %
                               (release_item.quantity))
            else:
                out_file.write('   CONCENTRATION = %g\n' %
                               (release_site.quantity))

        out_file.write('   RELEASE_PROBABILITY = %g\n' %
                       (release_site.probability))

        if release_site.pattern:
            out_file.write('   RELEASE_PATTERN = %s\n' %
                           (release_site.pattern))

        out_file.write('  }\n')


def save_molecules(context, out_file):
    """ Saves molecule info to mdl output file. """

    mcell = context.scene.mcell

    # Export Molecules:
    mol_list = mcell.molecules.molecule_list
    if len(mol_list) > 0:
        out_file.write('DEFINE_MOLECULES\n')
        out_file.write('{\n')

        for mol_item in mol_list:
            out_file.write('  %s\n' % (mol_item.name))
            out_file.write('  {\n')

            if mol_item.type == '2D':
                out_file.write('    DIFFUSION_CONSTANT_2D = %g\n' %
                               (mol_item.diffusion_constant))
            else:
                out_file.write('    DIFFUSION_CONSTANT_3D = %g\n' %
                               (mol_item.diffusion_constant))

            if mol_item.custom_time_step > 0:
                out_file.write('    CUSTOM_TIME_STEP = %g\n' %
                               (mol_item.custom_time_step))
            elif mol_item.custom_space_step > 0:
                out_file.write('    CUSTOM_SPACE_STEP = %g\n' %
                               (mol_item.custom_space_step))

            if mol_item.target_only:
                out_file.write('    TARGET_ONLY\n')

            out_file.write('  }\n')
        out_file.write('}\n\n')


def save_surface_classes(context, file):
    """ Saves surface class info to mdl output file. """

    mc = context.scene.mcell
    surf_class_list = mc.surface_classes.surf_class_list
    if len(surf_class_list) > 0:
        file.write('DEFINE_SURFACE_CLASSES\n')
        file.write('{\n')
        for active_surf_class in surf_class_list:
            file.write('  %s\n' % (active_surf_class.name))
            file.write('  {\n')
            for surf_class_props in active_surf_class.surf_class_props_list:
                molecule = surf_class_props.molecule
                orient = surf_class_props.surf_class_orient
                surf_class_type = surf_class_props.surf_class_type
                if surf_class_type == 'CLAMP_CONCENTRATION':
                    clamp_value = surf_class_props.clamp_value
                    file.write('    %s\n' % surf_class_type)
                    file.write('    %s%s = %g\n' % (molecule,
                                                    orient,
                                                    clamp_value))
                else:
                    file.write('    %s = %s%s\n' % (surf_class_type, molecule,
                                                    orient))
            file.write('  }\n')
        file.write('}\n\n')
    return


def save_reactions(context, out_file):
    """ Saves reaction info to mdl output file. """

    mcell = context.scene.mcell

    # Export Reactions:
    rxn_list = mcell.reactions.reaction_list
    if len(rxn_list) > 0:
        out_file.write('DEFINE_REACTIONS\n')
        out_file.write('{\n')

        for rxn_item in rxn_list:
            out_file.write('  %s ' % (rxn_item.name))

            if rxn_item.type == 'irreversible':
                out_file.write('[%g]' % (rxn_item.fwd_rate))
            else:
                out_file.write('[>%g, <%g]' %
                               (rxn_item.fwd_rate, rxn_item.bkwd_rate))

            if rxn_item.rxn_name:
                out_file.write(' : %s\n' % (rxn_item.rxn_name))
            else:
                out_file.write('\n')

        out_file.write('}\n\n')


def save_geometry(context, out_file):
    """ Saves geometry info to mdl output file. """

    mcell = context.scene.mcell

    # Export Model Geometry:
    object_list = mcell.model_objects.object_list
    if len(object_list) > 0:

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

                out_file.write('%s POLYGON_LIST\n' % (data_object.name))
                out_file.write('{\n')

                # write vertex list
                out_file.write('  VERTEX_LIST\n')
                out_file.write('  {\n')
                mesh = data_object.data
                matrix = data_object.matrix_world
                vertices = mesh.vertices
                for v in vertices:
                    t_vec = v.co * matrix
                    out_file.write('    [ %.15g, %.15g, %.15g ]\n' %
                                   (t_vec.x, t_vec.y, t_vec.z))

                # close VERTEX_LIST block
                out_file.write('  }\n')

                # write element connection
                out_file.write('  ELEMENT_CONNECTIONS\n')
                out_file.write('  {\n')

                faces = mesh.polygons
                for f in faces:
                    out_file.write('    [ %d, %d, %d ]\n' %
                                   (f.vertices[0], f.vertices[1],
                                    f.vertices[2]))

                # close ELEMENT_CONNECTIONS block
                out_file.write('  }\n')

                # write regions
                regions = get_regions(data_object)
                if regions:
                    out_file.write('  DEFINE_SURFACE_REGIONS\n')
                    out_file.write('  {\n')

                    region_names = [k for k in regions.keys()]
                    region_names.sort()
                    for region_name in region_names:
                        out_file.write('    %s\n' % (region_name))
                        out_file.write('    {\n')
                        out_file.write('      ELEMENT_LIST = ' +
                                       str(regions[region_name])+'\n')
                        out_file.write('    }\n')

                    out_file.write('  }\n')

                # close SURFACE_REGIONS block
                out_file.write('}\n\n')

                # restore proper object visibility state
                data_object.hide = saved_hide_status


def save_mod_surf_regions(context, file):
    """ Saves modify surface region info to mdl output file. """

    mc = context.scene.mcell
    mod_surf_regions_list = mc.mod_surf_regions.mod_surf_regions_list
    if len(mod_surf_regions_list) > 0:
        file.write('MODIFY_SURFACE_REGIONS\n')
        file.write('{\n')
        for active_mod_surf_regions in mod_surf_regions_list:
            surf_class_name = active_mod_surf_regions.surf_class_name
            file.write('  %s[%s]\n' % (active_mod_surf_regions.object_name,
                                       active_mod_surf_regions.region_name))
            file.write('  {\n    SURFACE_CLASS = %s\n  }\n' %
                       (surf_class_name))
        file.write('}\n\n')
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
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_spec)
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
            elif token_type == 'OP':
                val = " " + val + " "

            instantiated_expression = instantiated_expression + val

        pos = m.end()
        m = get_token(expression, pos)

    if pos != len(expression):
        pass

    return instantiated_expression
