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
This file contains the classes for CellBlender's Reaction Output.

"""

import glob
import os
import tempfile
import json

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
from . import data_model
from . import parameter_system
from . import cellblender_release
from . import cellblender_utils
from . import cellblender_pbc
from cellblender.cellblender_utils import project_files_path, mcell_files_path, get_python_path



# Reaction Output Operators:


class MCELL_OT_rxn_output_add(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_add"
    bl_label = "Add Reaction Data Output"
    bl_description = "Add new reaction data output to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.add()
        mcell.rxn_output.active_rxn_output_index = len(
            mcell.rxn_output.rxn_output_list)-1
        check_rxn_output(self, context)

        return {'FINISHED'}


class MCELL_OT_rxn_output_remove(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_remove"
    bl_label = "Remove Reaction Data Output"
    bl_description = "Remove selected reaction data output from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.remove(
            mcell.rxn_output.active_rxn_output_index)
        mcell.rxn_output.active_rxn_output_index -= 1
        if (mcell.rxn_output.active_rxn_output_index < 0):
            mcell.rxn_output.active_rxn_output_index = 0

        if mcell.rxn_output.rxn_output_list:
            check_rxn_output(self, context)

        return {'FINISHED'}


class MCELL_OT_rxn_output_disable_all(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_disable_all"
    bl_label = "Disable All Plotting"
    bl_description = "Disable All Items for Plotting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        for rxn_output in mcell.rxn_output.rxn_output_list:
            rxn_output.plotting_enabled = False
        return {'FINISHED'}


class MCELL_OT_rxn_output_enable_all(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_enable_all"
    bl_label = "Enable All Plotting"
    bl_description = "Enable All Items for Plotting"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        for rxn_output in mcell.rxn_output.rxn_output_list:
            rxn_output.plotting_enabled = True
        return {'FINISHED'}


class MCELL_OT_add_all_world(bpy.types.Operator):
    bl_idname = "mcell.rxn_out_all_world"
    bl_label = "Add all in world"
    bl_description = "Add a count statement for each molecule in the world"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mol_list = mcell.molecules.molecule_list
        for mol in mol_list:
            new_rxn_out = mcell.rxn_output.rxn_output_list.add()
            mcell.rxn_output.active_rxn_output_index = len(mcell.rxn_output.rxn_output_list)-1
            new_rxn_out.molecule_name = mol.name
            new_rxn_out.count_location = "World"
            new_rxn_out.rxn_or_mol = "Molecule"
            check_rxn_output(self, context)
        return {'FINISHED'}


# This is just a means to store a temporary file path for the duration of a
# Blender session.
class ReactionDataTmpFile:
    reactdata_tmpfile = None


def create_reactdata_tmpfile(data_path):
    if not ReactionDataTmpFile.reactdata_tmpfile:
        with tempfile.NamedTemporaryFile(
                delete=False, mode='wt', prefix="cellblender") as tmpfile:
            tmpfile.write(data_path)
            ReactionDataTmpFile.reactdata_tmpfile = tmpfile.name
    else:
        with open(ReactionDataTmpFile.reactdata_tmpfile, 'w') as tmpfile:
            tmpfile.write(data_path)

def remove_mdl_string_suffix(path):
    s = '_MDLString'
    path_ext = os.path.splitext(path)
    if path_ext[0].endswith(s): 
        return path_ext[0][:-len(s)] + path_ext[1]
    else:
        return path

class MCELL_OT_plot_rxn_output_with_selected(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_with_selected"
    bl_label = "Plot"
    bl_description = "Plot the reactions using selected plotting package"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        plot_sep = mcell.rxn_output.plot_layout
        plot_legend = mcell.rxn_output.plot_legend
        ###use_sweep = mcell.rxn_output.use_sweep

        combine_seeds = mcell.rxn_output.combine_seeds
        mol_colors = mcell.rxn_output.mol_colors

        # Look up the plotting module by its name
        
        mod_name = None

        for plot_module in cellblender.cellblender_info[
                'cellblender_plotting_modules']:
            mod_name = plot_module.get_name()
            if mod_name == mcell.rxn_output.plotter_to_use:
                break
        if mod_name == None:
            return {'FINISHED'}

        files_path = mcell_files_path()  # This will include the "mcell" on the end

        DATA_LAYOUT_FILE = "data_layout.json"
        KEY_MCELL4_MODE = "mcell4_mode"

        mcell4_mode = False 
        if os.path.exists(DATA_LAYOUT_FILE):
            f = open ( os.path.join(DATA_LAYOUT_FILE), 'r' )
            layout_spec = json.loads ( f.read() )
            f.close()
            mcell4_mode = KEY_MCELL4_MODE in layout_spec and layout_spec[KEY_MCELL4_MODE]

        
        if not mcell4_mode:
            # output obtained by running simulation in cellblender
            # Determine if this data structure is in the newer sweep format or not
            use_sweep = 'output_data' in os.listdir(files_path)
        else:
            # output obtained from mcell4 - expecting current directory to contain 
            # data_layout.json
            files_path = os.getcwd()
            use_sweep = True

        root_path = files_path
        data_paths = []

        if use_sweep:

          # Build the list from the sweep data file

          root_path = files_path
          f = open ( os.path.join(files_path, DATA_LAYOUT_FILE), 'r' )
          layout_spec = json.loads ( f.read() )
          f.close()

          data_layout_version = 0
          if 'version' in layout_spec:
            data_layout_version = layout_spec['version']

          data_layout = layout_spec['data_layout']
          print ( "data_layout = " + str(layout_spec) )
          num_runs = 1

          if data_layout_version == 2:
            for level in data_layout:
              if (level[0] != '/DIR') and (level[0] != '/FILE_TYPE') and (level[0] != '/SEED'):
                # Multiply by the number of sweep points in each level (stored at index 1)
                num_runs *= len(level[1])
                # append a counter to keep track of looping through levels
              level.append ( 0 )
            print ( "num_runs = " + str(num_runs) + ",  data_layout = " + str(layout_spec) )

            # Use the counters to count up the paths from the reversed layout
            data_layout.reverse()
            run_num = 0
            while run_num < num_runs:
              print ( "Preparing run " + str(run_num) )
              counters = ""
              for level in data_layout:
                counters = counters + "  " + level[0] + ":" + str(level[2])
              print ( " Counters = " + counters )
              run_path = ""
              par_path = ""
              for level in data_layout:
                if (level[0] == '/DIR'):
                  run_path = os.path.join ( level[1][0], run_path )
                elif (level[0] ==  '/FILE_TYPE'):
                  run_path = os.path.join ( level[1][0], run_path )
                elif (level[0] ==  '/SEED'):
                  pass
                else:
                  # Build on to the run path (used for getting data)
                  run_path = os.path.join ( level[0] + "_index_" + str(level[2]), run_path )
                  # Build on to the par path (used for displaying label)
                  if len(par_path) > 0:
                    par_path = "," + par_path
                  par_path = level[0] + "=" + str(level[1][level[2]]) + par_path
              run_num += 1

              run_path = run_path.strip ( os.path.sep )
              # Each point in data_paths will contain a run_path and a parameter "path"
              data_paths.append ( [ run_path, par_path ] )
              print ( "Run path = " + run_path )
              print ( "Parameter Point for run is: " + par_path )

              # Increment the counters
              for level in data_layout:
                if (level[0] == '/DIR'):
                  pass
                elif (level[0] ==  '/FILE_TYPE'):
                  pass
                elif (level[0] ==  '/SEED'):
                  pass
                else:
                  level[2] += 1
                  if (level[2] < len(level[1])):
                    # This counter didn't roll over, so there's no need to carry into the next one. Break.
                    break
                  else:
                    # This counter did roll over, so go back to zero and continue to increment the next one
                    level[2] = 0
          else:
            for level in data_layout:
              if (level[0] != 'dir') and (level[0] != 'file_type') and (level[0] != 'SEED'):
                # Multiply by the number of sweep points in each level (stored at index 1)
                num_runs *= len(level[1])
                # append a counter to keep track of looping through levels
              level.append ( 0 )
            print ( "num_runs = " + str(num_runs) + ",  data_layout = " + str(layout_spec) )

            # Use the counters to count up the paths from the reversed layout
            data_layout.reverse()
            run_num = 0
            while run_num < num_runs:
              print ( "Preparing run " + str(run_num) )
              counters = ""
              for level in data_layout:
                counters = counters + "  " + level[0] + ":" + str(level[2])
              print ( " Counters = " + counters )
              run_path = ""
              for level in data_layout:
                if (level[0] == 'dir'):
                  run_path = os.path.join ( level[1][0], run_path )
                elif (level[0] ==  'file_type'):
                  run_path = os.path.join ( level[1][0], run_path )
                elif (level[0] ==  'SEED'):
                  pass
                else:
                  run_path = os.path.join ( level[0] + "_index_" + str(level[2]), run_path )
              run_num += 1

              run_path = run_path.strip ( os.path.sep )
              # Each point in data_paths will contain a run_path and a parameter "path"
              data_paths.append ( [ run_path, run_path ] )
              print ( "Run path = " + run_path )

              # Increment the counters
              for level in data_layout:
                if (level[0] == 'dir'):
                  pass
                elif (level[0] ==  'file_type'):
                  pass
                elif (level[0] ==  'SEED'):
                  pass
                else:
                  level[2] += 1
                  if (level[2] < len(level[1])):
                    # This counter didn't roll over, so there's no need to carry into the next one. Break.
                    break
                  else:
                    # This counter did roll over, so go back to zero and continue to increment the next one
                    level[2] = 0

        else:

          # This is a pre-sweeping directory structure, so build a list containing a single item

          root_path = os.path.join(files_path, "react_data")
          data_paths.append ( [ "", "" ] )

        # Plot the data via this module
        # print("Preparing to call %s" % (mod_name))
        # The mcell_files_path is now where the MDL lives:
        create_reactdata_tmpfile(files_path)

        plot_spec_string = "xlabel=time(s) ylabel=count "
        if plot_legend != 'x':
            plot_spec_string = plot_spec_string + "legend=" + plot_legend

        for data_path in data_paths:

            for rxn_output in mcell.rxn_output.rxn_output_list:
                print("mdl_file_prefix: " + rxn_output.mdl_file_prefix)

                if rxn_output.plotting_enabled:

                    molecule_name = rxn_output.molecule_name
                    object_name = rxn_output.object_name
                    region_name = rxn_output.region_name
                    file_name = None

                    if rxn_output.rxn_or_mol == 'Molecule':
                        if rxn_output.count_location == 'World':
                            file_name = "%s.World.dat" % (molecule_name)
                        elif rxn_output.count_location == 'Object':
                            file_name = "%s.%s.dat" % (molecule_name, object_name)
                        elif rxn_output.count_location == 'Region':
                            file_name = "%s.%s.%s.dat" % (molecule_name,
                                                   object_name, region_name)
                    elif rxn_output.rxn_or_mol == 'Reaction':
                        rxn_name = rxn_output.reaction_name
                        if rxn_output.count_location == 'World':
                            file_name = "%s.World.dat" % (rxn_name)
                        elif rxn_output.count_location == 'Object':
                            file_name = "%s.%s.dat" % (rxn_name, object_name)
                        elif rxn_output.count_location == 'Region':
                            file_name = "%s.%s.%s.dat" % (rxn_name,
                                                   object_name, region_name)

                    elif rxn_output.rxn_or_mol == 'MDLString':
                        if not mcell4_mode:
                            file_name = rxn_output.mdl_file_prefix + "_MDLString.dat"
                        else:
                            # in MCell4, we need to keep the name of the file the user entered
                            file_name = rxn_output.mdl_file_prefix + ".dat"

                    elif rxn_output.rxn_or_mol == 'File':
                        file_name = rxn_output.data_file_name
                        print ( "Preparing to plot a File with file_name = " + file_name )

                    if file_name:
                        first_pass = True

                        if rxn_output.rxn_or_mol == 'File':
                            # Assume that the file path is blend file relative (begins with "//")
                            if file_name.startswith ( "//" ):
                                # Convert the file name from blend file relative to react_data folder relative:
                                candidate_file_list = [ os.path.pardir + os.path.sep + os.path.pardir + os.path.sep + file_name[2:] ]
                            else:
                                # Use the file name as absolute
                                candidate_file_list = [ file_name ]
                        else:
                            # Prepend a search across all seeds for this file
                            file_name = os.path.join("seed_*", file_name)
                            if len(data_path[0]) > 0:
                              base_path = os.path.join(root_path, data_path[0])
                            else:
                              base_path = root_path
                                
                            print ( "glob of " + os.path.join(base_path, file_name) )
                            candidate_file_list = glob.glob(os.path.join(base_path, file_name))
                            print ( "Candidate list = " + str(candidate_file_list) )
                            if not candidate_file_list and '_MDLString' in file_name:
                              # try to search without the _MDLString suffix
                              pattern_wo_mdlstring = os.path.join(base_path, remove_mdl_string_suffix(file_name))
                              print ( " - glob did not find any files, searching for " + pattern_wo_mdlstring)
                              candidate_file_list = glob.glob(pattern_wo_mdlstring)
                              
                            if not candidate_file_list:
                              # try to search with '.' replaced with '_'
                              name_ext = os.path.splitext(file_name)
                              pattern_wo_dots = os.path.join(base_path, name_ext[0].replace('.', '_') + name_ext[1]) 
                              print ( " - glob did not find any files, searching for " + pattern_wo_dots)
                              candidate_file_list = glob.glob(pattern_wo_dots)
                                
                            # Without sorting, the seeds may not be increasing
                            candidate_file_list.sort()
                            #print("Candidate file list for %s:" % (file_name))
                            #print("  ", candidate_file_list)
                            if not mcell4_mode and not mcell.rxn_output.ignore_start_time:
                              # TODO: support this also for mcell4
                              # Use the start_time.txt file to find files modified since MCell was started (minus 10 seconds)
                              start_time = os.stat(os.path.join(project_files_path(), "start_time.txt")).st_mtime - 10
                              # This file is both in the list and newer than the run time for MCell
                              candidate_file_list = [ffn for ffn in candidate_file_list if os.stat(ffn).st_mtime >= start_time]

                        print ( "Candidate list = " + str(candidate_file_list) )

                        for ffn in candidate_file_list:

                            print ( "   Files path      = " + str(files_path) )
                            print ( "    Candidate file = " + str(ffn) )
                            print ( "    Parameter Point = " + str(data_path[1]) )

                            par_string = ""
                            if len(data_path[1]) > 0:
                              par_string = " ppt=" + data_path[1]

                            f = None
                            if rxn_output.rxn_or_mol == 'File':
                              # Use the file name as it is
                              f = ffn
                            else:
                              # Create f as a relative path containing seed/file
                              #split1 = os.path.split(ffn)
                              #split2 = os.path.split(split1[0])
                              #f = os.path.join(split2[1], split1[1])

                              f = ffn[len(root_path)+1:]

                            color_string = ""
                            if rxn_output.rxn_or_mol == 'Molecule' and mol_colors:
                                # Use molecule colors for graphs
                                # Should be standardized!!
                                mol_mat_name = "mol_%s_mat" % (molecule_name)
                                #print ("Molecule Material Name = ", mol_mat_name)
                                #Look up the material
                                mats = bpy.data.materials
                                mol_color = mats.get(mol_mat_name).diffuse_color
                                #print("Molecule color = ", mol_mat.diffuse_color)

                                mol_color_red = int(255 * mol_color[0])
                                mol_color_green = int(255 * mol_color[1])
                                mol_color_blue = int(255 * mol_color[2])
                                color_string = " color=#%2.2x%2.2x%2.2x " % (
                                    mol_color_red, mol_color_green, mol_color_blue)

                            base_name = os.path.basename(f)

                            if combine_seeds:
                                title_string = " title=" + base_name
                            else:
                                title_string = " title=" + f

                            if plot_sep == ' ':
                                # No title when all are on the same plot since only
                                # last will show
                                title_string = ""

                            if combine_seeds:
                                psep = " "
                                if first_pass:
                                    psep = plot_sep
                                    first_pass = False
                                plot_spec_string = (plot_spec_string + psep + color_string + title_string + par_string + " f=" + f)
                            else:
                                plot_spec_string = (plot_spec_string + plot_sep + color_string + title_string + par_string + " f=" + f)

        plot_spec_string += " tf="+ReactionDataTmpFile.reactdata_tmpfile
        print("Plotting from", root_path)
        print("Plotting spec", plot_spec_string)
        python_path = get_python_path(mcell=mcell)
        plot_module.plot(root_path, plot_spec_string, python_path)

        return {'FINISHED'}


# Reaction Output callback functions


def check_rxn_output(self, context):
    """ Format reaction data output. """

    mcell = context.scene.mcell
    rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output = rxn_output_list[
        mcell.rxn_output.active_rxn_output_index]
    mol_list = mcell.molecules.molecule_list
    reaction_list = mcell.reactions.reaction_name_list
    molecule_name = rxn_output.molecule_name
    reaction_name = rxn_output.reaction_name
    obj_list = mcell.model_objects.object_list
    object_name = rxn_output.object_name
    region_name = rxn_output.region_name
    rxn_output_name = ""

    status = ""
    count_name = ""
    if rxn_output.rxn_or_mol == 'Reaction':
        count_name = reaction_name
        name_list = reaction_list
    elif rxn_output.rxn_or_mol == 'Molecule':
        count_name = molecule_name
        name_list = mol_list
    elif rxn_output.rxn_or_mol == 'MDLString':
        count_name = molecule_name
        rxn_output.status = ""
        # Can't do these here because this causes another check_rxn_output call (infinite recursion)
        #rxn_output.name = rxn_output.mdl_string
        #rxn_output.name = "MDL: " + rxn_output.mdl_string
        return
    elif rxn_output.rxn_or_mol == 'File':
        print ( "Checked file name and got " + rxn_output.name )
        rxn_output.status = ""
        # Can't do these here because this causes another check_rxn_output call (infinite recursion)
        #rxn_output.name = rxn_output.mdl_string
        rxn_output_name = "FILE: " + rxn_output.data_file_name
        if rxn_output.name != rxn_output_name:
            rxn_output.name = rxn_output_name
        return
    else:
        pass

    try:
        region_list = bpy.data.objects[object_name].mcell.regions.region_list
    except KeyError:
        # The object name isn't a blender object
        region_list = []


    # Check for illegal names (Starts with a letter. No special characters.)
    count_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    c = re.match(count_filter, count_name)
    if c is None:
        status = "Name error: %s" % (count_name)
    else:
        # Check for undefined molecule or reaction names
        c_name = c.group(1)
        if not c_name in name_list:
            status = "Undefined: %s" % (c_name)

    # Use different formatting depending on where we are counting
    if rxn_output.count_location == 'World':
        rxn_output_name = "Count %s in World" % (count_name)
    elif rxn_output.count_location == 'Object':
        if not object_name in obj_list:
            status = "Undefined object: %s" % object_name
        else:
            rxn_output_name = "Count %s in/on %s" % (
                count_name, object_name)
    elif rxn_output.count_location == 'Region':
        if not region_name in region_list:
            status = "Undefined region: %s" % region_name
        else:
            rxn_output_name = "Count %s in/on %s[%s]" % (
                count_name, object_name, region_name)

    # Only update reaction output if necessary to avoid infinite recursion
    if rxn_output.name != rxn_output_name:
        rxn_output.name = rxn_output_name

    # Check for duplicate reaction data
    rxn_output_keys = rxn_output_list.keys()
    if rxn_output_keys.count(rxn_output.name) > 1 and not status:
        status = "Duplicate reaction output: %s" % (rxn_output.name)

    rxn_output.status = status

    return



def update_name_and_check_rxn_output(self, context):
    # Set the name to show the MDL

    mcell = context.scene.mcell
    rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output = rxn_output_list[mcell.rxn_output.active_rxn_output_index]
    if rxn_output.rxn_or_mol == 'MDLString':
        rxn_output.name = "MDL: " + rxn_output.mdl_string
    elif rxn_output.rxn_or_mol == 'File':
        rxn_output.name = "FILE: " + rxn_output.data_file_name

    # Now perform the normal reaction output check:
    check_rxn_output(self, context)
    return



# Reaction Output Panel Classes


class MCELL_UL_check_reaction_output_settings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.status:
            layout.label(text=item.status, icon='ERROR')
        else:
            col = layout.column()
            if item.plotting_enabled:
                col.label(text=item.name, icon='CHECKMARK')
            else:
                col.label(text=item.name, icon='BLANK1')
            col = layout.column()
            if item.plotting_enabled:
                col.prop(item, "plotting_enabled", text="", icon='HIDE_OFF')
            else:
                col.prop(item, "plotting_enabled", text="", icon='HIDE_ON')



# Reaction Output Property Groups


class MCellReactionOutputProperty(bpy.types.PropertyGroup):
    name: StringProperty(
        name="Reaction Output", update=check_rxn_output)
    description: StringProperty(name="Description", default="")
    molecule_name: StringProperty(
        name="Molecule",
        description="Count the selected molecule.",
        update=check_rxn_output)
    reaction_name: StringProperty(
        name="Reaction",
        description="Count the selected reaction.",
        update=check_rxn_output)
    # allows the user to define a literal mdl string to count using complex expressions. E.g. 2*S1 
    mdl_string: StringProperty(
        name="MDL Definition",
        description="Count using a literal MDL definition.",
        update=update_name_and_check_rxn_output)
    mdl_file_prefix: StringProperty(
        name="MDL File Prefix",
        description="Prefix name for this file." )
    data_file_name: StringProperty ( name = "Data File Name", subtype='FILE_PATH', default="", description="Data File to Plot.", update=check_rxn_output )

    object_name: StringProperty(
        name="Object", update=check_rxn_output)
    region_name: StringProperty(
        name="Region", update=check_rxn_output)
    count_location_enum = [
        ('World', "World", ""),
        ('Object', "Object", ""),
        ('Region', "Region", "")]
    count_location: EnumProperty(
        items=count_location_enum, name="Count Location",
        description="Count all molecules in the selected location.",
        update=check_rxn_output)
    rxn_or_mol_enum = [
        ('Reaction', "Reaction", ""),
        ('Molecule', "Molecule", ""),
        ('MDLString', "MDLString", ""),
        ('File', "File", "")]
    rxn_or_mol: EnumProperty(
        items=rxn_or_mol_enum, name="Count Reaction or Molecule",
        default='Molecule',
        description="Select between counting a reaction or molecule.",
        update=update_name_and_check_rxn_output)

    plotting_enabled: BoolProperty ( default=True, description="Enable this item in plotting output" )

    description_show_help: BoolProperty ( default=False, description="Toggle more information about this parameter" )
    mdl_string_show_help: BoolProperty ( default=False, description="Toggle more information about this item" )
    mdl_file_prefix_show_help: BoolProperty ( default=False, description="Toggle more information about this item" )
    data_file_name_show_help: BoolProperty ( default=False, description="Toggle more information about this item" )

    # plot_command: StringProperty(name="Command")  # , update=check_rxn_output)
    status: StringProperty(name="Status")

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction Output building Data Model" )
        ro_dm = {}
        ro_dm['data_model_version'] = "DM_2018_01_11_1330"
        ro_dm['name'] = self.name
        ro_dm['description'] = self.description
        ro_dm['molecule_name'] = self.molecule_name
        ro_dm['reaction_name'] = self.reaction_name
        ro_dm['mdl_string'] = self.mdl_string
        ro_dm['mdl_file_prefix'] = self.mdl_file_prefix
        ro_dm['data_file_name'] = self.data_file_name
        ro_dm['object_name'] = self.object_name
        ro_dm['region_name'] = self.region_name
        ro_dm['count_location'] = self.count_location
        ro_dm['rxn_or_mol'] = self.rxn_or_mol
        ro_dm['plotting_enabled'] = self.plotting_enabled
        return ro_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionOutputProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['mdl_string'] = ""
            dm['data_model_version'] = "DM_2015_07_24_2311"

        if dm['data_model_version'] == "DM_2015_07_24_2311":
            # Versions prior to this re-used the molecule name to hold the file prefix, so check and copy
            if dm['rxn_or_mol'] == "MDLString":
                dm['mdl_file_prefix'] = dm['molecule_name']
                dm['molecule_name'] = ""
            else:
                dm['mdl_file_prefix'] = ""
            dm['data_model_version'] = "DM_2015_10_07_1500"

        if dm['data_model_version'] == "DM_2015_10_07_1500":
            # Add the plotting_enabled flag with a default of true (since previous versions plotted everything)
            dm['plotting_enabled'] = True
            # Add the data file name with the default of an empty string
            dm['data_file_name'] = ""
            # Update the data model version for this item
            dm['data_model_version'] = "DM_2016_03_15_1800"

        if dm['data_model_version'] == "DM_2016_03_15_1800":
            # Change on January 11th, 2018 to add a description field to reaction output items
            dm['description'] = ""
            dm['data_model_version'] = "DM_2018_01_11_1330"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2018_01_11_1330":
            data_model.flag_incompatible_data_model ( "Upgrade Error: Unable to upgrade MCellReactionOutputProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2018_01_11_1330":
            data_model.handle_incompatible_data_model ( "Build Error: Unable to upgrade MCellReactionOutputProperty data model to current version." )
        self.name = dm["name"]
        self.description = dm["description"]
        self.molecule_name = dm["molecule_name"]
        self.reaction_name = dm["reaction_name"]
        self.mdl_string = dm['mdl_string']
        self.mdl_file_prefix = dm['mdl_file_prefix']
        self.data_file_name = dm['data_file_name']
        self.object_name = dm["object_name"]
        self.region_name = dm["region_name"]
        self.count_location = dm["count_location"]
        self.rxn_or_mol = dm["rxn_or_mol"]
        self.plotting_enabled = dm["plotting_enabled"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Output Properties... no collections to remove." )




import cellblender


def get_plotters_as_items(scene, context):
    prefs = [ "MatPlotLib Plotter", "XmGrace Plotter", "GnuPlot Plotter", "Java Plotter", "Simple Plotter" ]
    found = []
    available = []
    for plot_module in cellblender.cellblender_info['cellblender_plotting_modules']:
        mod_name = plot_module.get_name()
        found.append ( mod_name )
    # Order the items according to hard-coded preferences
    for p in prefs:
        if p in found:
            available.append ( p )
    # Include the unlisted plotters at the end
    for p in found:
        if not (p in available):
            available.append ( p )
    items = []
    for p in available:
        items.append ( (p, p, "") )
    return items


class MCellReactionOutputPropertyGroup(bpy.types.PropertyGroup):

    rxn_step: PointerProperty ( name="Step",
        type=parameter_system.Parameter_Reference )
    output_buf_size: PointerProperty ( name="OutBufSize",
        type=parameter_system.Parameter_Reference )
    active_rxn_output_index: IntProperty(
        name="Active Reaction Output Index", default=0)
    virt_x  : IntProperty(name="X Position", default=0,
        description="The X coordinate of the Virtual Box")
    virt_y  : IntProperty(name="Y Position", default=0,
        description="The Y coordinate of the Virtual Box")
    virt_z  : IntProperty(name="Z Position", default=0,
        description="The Z coordinate of the Virtual Box")
    all_enc : BoolProperty(name="Enable All enclosed", default = False, 
        description = 'Count all molecules or reactions that occur in the area enclosed by region ')
    est_conc: BoolProperty(name="Enable Estimate Concentration", default = False, 
        description = 'Estimate the concentration of the volume molecule at that region, averaged since the beginning of the simulation.')
    trig : BoolProperty(name = "Enable Triggers", default = False, description= "Tags molecules with their locations")
    fr_bk: BoolProperty(name = "Show Hits/Crossings options",default = False)
    hit_back   : BoolProperty(name = "BACK_HITS",default = False)
    hit_front  : BoolProperty(name = "FRONT_HITS",default = False)
    hit_all    : BoolProperty(name = "ALL_HITS",default = False)
    cross_front: BoolProperty(name = "FRONT_CROSSINGS",default = False)
    cross_back : BoolProperty(name = "BACK_CROSSINGS",default = False)
    cross_all  : BoolProperty(name = "ALL_CROSSINGS",default = False)
    rxn_output_list: CollectionProperty(type=MCellReactionOutputProperty, name="Reaction Output List")
    plot_layout_enum = [
        (' page ', "Separate Page for each Plot", ""),
        (' plot ', "One Page, Multiple Plots", ""),
        (' ',      "One Page, One Plot", "")]
    plot_layout: EnumProperty ( 
        items=plot_layout_enum, name="", 
        description="Select the Page and Plot Layout",
        default=' plot ' )
    plot_legend_enum = [
        ('x', "No Legend", ""),
        ('0', "Legend with Automatic Placement", ""),
        ('1', "Legend in Upper Right", ""),
        ('2', "Legend in Upper Left", ""),
        ('3', "Legend in Lower Left", ""),
        ('4', "Legend in Lower Right", ""),
        # ('5', "Legend on Right", ""), # This appears to duplicate option 7
        ('6', "Legend in Center Left", ""),
        ('7', "Legend in Center Right", ""),
        ('8', "Legend in Lower Center", ""),
        ('9', "Legend in Upper Center", ""),
        ('10', "Legend in Center", "")]
    plot_legend: EnumProperty ( 
        items=plot_legend_enum, name="", 
        description="Select the Legend Display and Placement",
        default='0' )
    combine_seeds: BoolProperty(
        name="Combine Seeds",
        description="Combine all seeds onto the same plot.",
        default=True)
    mol_colors: BoolProperty(
        name="Molecule Colors",
        description="Use Molecule Colors for line colors.",
        default=False)
    #use_sweep: BoolProperty(
    #    name="Use Sweep",
    #    description="Plot from the sweep file.",
    #    default=False)
    plotter_to_use: EnumProperty(
        name="", # "Plot with:",
        description="Plotter to use.",
        items=get_plotters_as_items )

    always_generate: BoolProperty(
        name="Always Generate All Plot Data",
        description="Generate All Plot Data Regardless of Current View Setting",
        default=True)


    ignore_start_time: BoolProperty(
        name="Ignore Start Time",
        description="Ignore the start_time.txt file when plotting.",
        default=False)


    def init_properties ( self, parameter_system ):
        self.rxn_step.init_ref (
            parameter_system, user_name="Step", 
            user_expr="", user_units="", user_descr="Step\n"
            "Output reaction data every t seconds.\nUses simulation time step when blank.") 
        self.output_buf_size.init_ref (
            parameter_system, user_name="OutputBufSize", 
            user_expr="", user_units="", user_descr="OutputBufSize\n"
            "Write output to disk after every N lines. Default is N=10000.") 

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction Output Panel building Data Model" )
        ro_dm = {}
        ro_dm['data_model_version'] = "DM_2016_03_15_1800"
        try:
            ro_dm['rxn_step'] = self.rxn_step.get_expr()
            ro_dm['output_buf_size'] = self.output_buf_size.get_expr()
        except:
            print("WARNING: Exception caught while calling get_expr(), the resultign data model might not be correct.")
        ro_dm['plot_layout'] = self.plot_layout
        ro_dm['plot_legend'] = self.plot_legend
        ro_dm['combine_seeds'] = self.combine_seeds
        ro_dm['mol_colors'] = self.mol_colors
        ro_dm['always_generate'] = self.always_generate
        ro_list = []
        for ro in self.rxn_output_list:
            ro_list.append ( ro.build_data_model_from_properties(context) )
        ro_dm['reaction_output_list'] = ro_list
        return ro_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionOutputPropertyGroup Data Model" )
        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['rxn_step'] = ""
            dm['data_model_version'] = "DM_2015_05_15_1214"

        if dm['data_model_version'] == "DM_2015_05_15_1214":
            # Set "always_generate" to true to be consistent with previous behavior which generated all files
            dm['always_generate'] = True
            dm['data_model_version'] = "DM_2016_03_15_1800"

        if dm['data_model_version'] == "DM_2016_03_15_1800":
            dm['output_buf_size'] = ""
            dm['data_model_version'] = "DM_2016_06_30_1600"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2016_06_30_1600":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputPropertyGroup data model to current version." )
            return None

        if "reaction_output_list" in dm:
            for item in dm["reaction_output_list"]:
                if MCellReactionOutputProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2016_06_30_1600":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputPropertyGroup data model to current version." )
        self.init_properties(context.scene.mcell.parameter_system)
        self.plot_layout = dm["plot_layout"]
        self.plot_legend = dm["plot_legend"]
        self.rxn_step.set_expr ( dm["rxn_step"] )
        self.output_buf_size.set_expr ( dm["output_buf_size"] )
        self.combine_seeds = dm["combine_seeds"]
        self.mol_colors = dm["mol_colors"]
        self.always_generate = dm["always_generate"]
        while len(self.rxn_output_list) > 0:
            self.rxn_output_list.remove(0)
        if "reaction_output_list" in dm:
            for r in dm["reaction_output_list"]:
                self.rxn_output_list.add()
                self.active_rxn_output_index = len(self.rxn_output_list)-1
                ro = self.rxn_output_list[self.active_rxn_output_index]
                # ro.init_properties(context.scene.mcell.parameter_system)
                ro.build_properties_from_data_model ( context, r )


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        # Note that the two "Panel Parameters" (rxn_step and output_buf_size) in this group are static and should not be removed.
        #self.rxn_step.clear_ref ( ps )
        #self.output_buf_size.clear_ref ( ps )
        print ( "Removing all Reaction Output Properties..." )
        self.active_rxn_output_index = 0
        for item in self.rxn_output_list:
            item.remove_properties(context)
        self.rxn_output_list.clear()
        print ( "Done removing all Reaction Output Properties." )


    def draw_layout ( self, context, layout ):
        """ Draw the reaction output "panel" within the layout """
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        PBC = mcell.pbc


        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            self.rxn_step.draw(layout,ps)
            row = layout.row()
            self.output_buf_size.draw(layout,ps)
            row = layout.row()

            # Do not need molecules to bring up plotting for pure MDL cases
            if mcell.molecules.molecule_list:
                col = row.column()
                col.template_list("MCELL_UL_check_reaction_output_settings",
                                  "reaction_output", self,
                                  "rxn_output_list", self,
                                  "active_rxn_output_index", rows=2)

                col = row.column(align=False)
                # Use subcolumns to group logically related buttons together
                subcol = col.column(align=True)
                subcol.operator("mcell.rxn_output_add", icon='ADD', text="")
                subcol.operator("mcell.rxn_output_remove", icon='REMOVE', text="")
                subcol = col.column(align=True)
                subcol.operator("mcell.rxn_out_all_world", icon='PLUS', text="")
                subcol = col.column(align=True)
                subcol.operator("mcell.rxn_output_enable_all", icon='HIDE_OFF', text="")
                subcol.operator("mcell.rxn_output_disable_all", icon='HIDE_ON', text="")
                subcol = col.column(align=True)
                if self.always_generate:
                    subcol.prop ( self, "always_generate", icon='EXPORT', text="" )
                else:
                    subcol.prop ( self, "always_generate", icon='BLANK1', text="" )

                # Show molecule, object, and region options only if there is at
                # least one count statement.
                if self.rxn_output_list:
                    rxn_output = self.rxn_output_list [ self.active_rxn_output_index ]
                    layout.prop(rxn_output, "rxn_or_mol", expand=True)
                    if rxn_output.rxn_or_mol == 'Molecule':
                        layout.prop_search(
                            rxn_output, "molecule_name", mcell.molecules,
                            "molecule_list", icon='FORCE_LENNARDJONES')
                    elif rxn_output.rxn_or_mol =='Reaction':
                        layout.prop_search(
                            rxn_output, "reaction_name", mcell.reactions,
                            "reaction_name_list", icon='FORCE_LENNARDJONES')
                    elif rxn_output.rxn_or_mol == 'MDLString':
                        ## layout.prop(rxn_output, "mdl_string")
                        helptext = "MDL String\n" + \
                                   "Specifies the MDL String used to generate output.\n" + \
                                   "Example:\n" + \
                                   "   COUNT[my_mol,Scene.Circle.039,FRONT_CROSSINGS]\n" + \
                                   "See MCell Quick Reference Guide for more details."
                        ps.draw_prop_with_help ( layout, "MDL String", rxn_output, "mdl_string", "mdl_string_show_help", rxn_output.mdl_string_show_help, helptext )

                        ## layout.prop(rxn_output,"mdl_file_prefix")
                        helptext = "MDL File Prefix\n" + \
                                   "Specifies a portion of the file name for this output.\n" + \
                                   "Example:\n" + \
                                   "     circle_039_front_cross\n" + \
                                   "  will generate a file named:\n" + \
                                   "     circle_039_front_cross_MDLString.dat\n" + \
                                   "That file will be located in react_data/seed_xxxxx\n" + \
                                   "All output files must have unique names.\n" + \
                                   "See MCell Quick Reference Guide for more details."
                        ps.draw_prop_with_help ( layout, "MDL File Prefix", rxn_output, "mdl_file_prefix", "mdl_file_prefix_show_help", rxn_output.mdl_file_prefix_show_help, helptext )

                    elif rxn_output.rxn_or_mol =='File':
                        ## layout.prop ( rxn_output, "data_file_name" )
                        helptext = "File:\n" + \
                                   "  Specifies the File to Plot.\n" + \
                                   "  This Plot Specification does not generate any data.\n" + \
                                   "  The file path may be either relative or absolute.\n" + \
                                   "  Blender's convention for relative paths start with \"//\".\n" + \
                                   "  Relative paths are relative to the location of the .blend file."
                        ps.draw_prop_with_help ( layout, "File", rxn_output, "data_file_name", "data_file_name_show_help", rxn_output.data_file_name_show_help, helptext )

                    if (rxn_output.rxn_or_mol == 'Molecule') or (rxn_output.rxn_or_mol == 'Reaction'):
                        layout.prop(rxn_output, "count_location", expand=True)
                        # Show the object selector if Object or Region is selected
                        if rxn_output.count_location != "World":
                            layout.prop_search(
                                rxn_output, "object_name", mcell.model_objects,
                                "object_list", icon='MESH_ICOSPHERE')                        
                            if (rxn_output.object_name and
                                    (rxn_output.count_location == "Region")):

                                try:
                                    regions = bpy.data.objects[
                                        rxn_output.object_name].mcell.regions
                                    layout.prop_search(rxn_output, "region_name",
                                                       regions, "region_list",
                                                       icon='FACESEL')                                      
                                except KeyError:
                                    pass                                           
                            if rxn_output.count_location != "World":
                                
                                if rxn_output.count_location == "Region":

                                    if PBC.peri_trad==True and self.est_conc==False and self.fr_bk==False:  
                                        row = layout.row(align=True)                                                            
                                        row.prop(self, "all_enc")
                                    if self.all_enc==False and self.trig==False and self.fr_bk==False and mcell.molecules.molecule_list[0].type=="3D":
                                        row = layout.row(align=True)
                                        row.prop(self, "est_conc")
                                    if  self.est_conc==False and self.fr_bk==False:
                                        row = layout.row(align=True)
                                        row.prop(self, "trig")
                                    if self.all_enc==False and self.trig==False and self.est_conc==False:
                                        row = layout.row(align=True)
                                        row.prop(self, "fr_bk")
                                        if self.fr_bk == True:
                                            row = layout.row(align=True)
                                            if self.hit_front==False and self.hit_back==False and self.cross_all==False and self.cross_front==False and self.cross_back==False:                                            
                                                row.prop(self, "hit_all")
                                            if self.hit_all==False and self.hit_front==False and self.hit_back==False and self.cross_front==False and self.cross_back==False:
                                                row.prop(self, "cross_all")
                                            row = layout.row(align=True)
                                            if self.hit_all==False and self.hit_back==False and self.cross_all==False and self.cross_front==False and self.cross_back==False:
                                                row.prop(self, "hit_front")
                                            if self.hit_all==False and self.hit_front==False and self.hit_back==False and self.cross_all==False and self.cross_back==False:
                                                row.prop(self, "cross_front")
                                            row = layout.row(align=True)
                                            if self.hit_all==False and self.hit_front==False and self.cross_all==False and self.cross_front==False and self.cross_back==False:
                                                row.prop(self, "hit_back")
                                            if self.hit_all==False and self.hit_front==False and self.hit_back==False and self.cross_all==False and self.cross_front==False:
                                                row.prop(self, "cross_back")
                                        if self.fr_bk==False:
                                            self.hit_all     = False
                                            self.hit_front   = False
                                            self.hit_back    = False
                                            self.cross_all   = False
                                            self.cross_front = False
                                            self.cross_back  = False                                            
                                            
                                if rxn_output.count_location == "Object":

                                    row = layout.row(align=True)
                                    row.prop(self, "trig")                                  
                            #Checking which region they want to count in from the PBC file
                            if rxn_output.count_location != "World":
                                #layout.label(text= "I'm a label",icon='GRID')
                                if PBC.peri_trad == False:
                                    layout.label(text= "Virtual box selection",icon='GRID')
                                    row = layout.row(align=True)
                                    row.prop(self, "virt_x")
                                    row.prop(self, "virt_y")
                                    row.prop(self, "virt_z")
                            #Checking to see if they want to use all_enclosed to count the molecules
                            #if (rxn_output.object_name and (rxn_output.count_location == "Region")): 

                    helptext = "Plot Item Description - \nUser-specified text describing this plot item"
                    ps.draw_prop_with_help ( layout, "Description", rxn_output, "description", "description_show_help", rxn_output.description_show_help, helptext )
            else:

                row.label(text="Define at least one molecule", icon='ERROR')

            layout.separator()
            layout.separator()

            row = layout.row()
            row.label(text="Plot Reaction Data:", icon='FORCE_LENNARDJONES')

            row = layout.row()

            col = row.column()
            col.prop(self, "plot_layout")

            col = row.column()
            col.prop(self, "combine_seeds")

            row = layout.row()

            col = row.column()
            col.prop(self, "plot_legend")

            col = row.column()
            col.prop(self, "mol_colors")

            row = layout.row()
            col = row.column()
            col.prop ( self, "plotter_to_use" )
            col = row.column()
            col.operator("mcell.plot_rxn_output_with_selected")


            row = layout.row()
            col = row.column()
            col.prop ( self, "ignore_start_time" )



    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


classes = ( 
            MCELL_OT_rxn_output_add,
            MCELL_OT_rxn_output_remove,
            MCELL_OT_rxn_output_disable_all,
            MCELL_OT_rxn_output_enable_all,
            MCELL_OT_add_all_world,
            MCELL_OT_plot_rxn_output_with_selected,
            MCELL_UL_check_reaction_output_settings,
            MCellReactionOutputProperty,
            MCellReactionOutputPropertyGroup,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

