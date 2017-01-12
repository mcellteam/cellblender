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
This file contains the classes for CellBlender's Simulations.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

from bpy.app.handlers import persistent


# python imports
import array
import glob
import os
import random
import re
import subprocess
import time
import shutil
import datetime


# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils
from . import data_model

from cellblender.cellblender_utils import mcell_files_path

from multiprocessing import cpu_count


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Simulation Operators:

def run_generic_runner (context, sim_module):

    mcell = context.scene.mcell
    mcell.run_simulation.last_simulation_run_time = str(time.time())

    binary_path = mcell.cellblender_preferences.mcell_binary
    mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

    start = int(mcell.run_simulation.start_seed.get_value())
    end = int(mcell.run_simulation.end_seed.get_value())
    mcell_processes_str = str(mcell.run_simulation.mcell_processes)
    mcell_binary = mcell.cellblender_preferences.mcell_binary
    # Force the project directory to be where the .blend file lives
    mcell_files = mcell_files_path()
    project_dir = os.path.join( mcell_files, "output_data" )
    status = ""

    if not mcell.cellblender_preferences.decouple_export_run:
        bpy.ops.mcell.export_project()

    if (mcell.run_simulation.error_list and
            mcell.cellblender_preferences.invalid_policy == 'dont_run'):
        pass
    else:
        react_dir = os.path.join(project_dir, "react_data")
        if (os.path.exists(react_dir) and
                mcell.run_simulation.remove_append == 'remove'):
            shutil.rmtree(react_dir)
        if not os.path.exists(react_dir):
            os.makedirs(react_dir)

        viz_dir = os.path.join(project_dir, "viz_data")
        if (os.path.exists(viz_dir) and
                mcell.run_simulation.remove_append == 'remove'):
            shutil.rmtree(viz_dir)
        if not os.path.exists(viz_dir):
            os.makedirs(viz_dir)

        runner_input = "dm.txt"
        if "runner_input" in dir(sim_module):
          runner_input = sim_module.runner_input

        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True )
        if runner_input.endswith("json"):
          data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,runner_input) )
        else:
          data_model.save_data_model_to_file ( mcell_dm, os.path.join(project_dir,runner_input) )

        base_name = mcell.project_settings.base_name

        error_file_option = mcell.run_simulation.error_file
        log_file_option = mcell.run_simulation.log_file
        script_dir_path = os.path.dirname(os.path.realpath(__file__))
        write_default_data_layout(mcell_files, start, end)


        processes_list = mcell.run_simulation.processes_list
        processes_list.add()
        mcell.run_simulation.active_process_index = len(mcell.run_simulation.processes_list) - 1
        simulation_process = processes_list[mcell.run_simulation.active_process_index]

        print("Starting MCell ... create start_time.txt file:")
        with open(os.path.join(os.path.dirname(bpy.data.filepath),"start_time.txt"), "w") as start_time_file:
            start_time_file.write("Started MCell at: " + (str(time.ctime())) + "\n")

        commands = []
        for sim_seed in range(start,end+1):
            new_command = [
                mcell_binary,
                ("-seed %s" % str(sim_seed)),
                os.path.join(project_dir, ("%s.main.mdl" % base_name))
              ]
            commands.append ( new_command )

        sp_list = sim_module.run_commands ( commands, cwd=project_dir )

        for sp in sp_list:
            cellblender.simulation_popen_list.append(sp)


        if ((end - start) == 0):
            simulation_process.name = ("PID: %d, MDL: %s.main.mdl, Seed: %d" %
                                        (sp_list[0].pid, base_name, start))
        else:
            simulation_process.name = ("PID: %d-%d, MDL: %s.main.mdl, Seeds: %d-%d" %
                                        (sp_list[0].pid, sp_list[-1].pid, base_name, start, end))

    mcell.run_simulation.status = status

    return {'FINISHED'}



class MCELL_OT_run_simulation(bpy.types.Operator):
    bl_idname = "mcell.run_simulation"
    bl_label = "Run MCell Simulation"
    bl_description = "Run MCell Simulation"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self,context):

        mcell = context.scene.mcell
        if mcell.cellblender_preferences.lockout_export and (not mcell.cellblender_preferences.decouple_export_run):
            # print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            # The "self" here doesn't contain or permit the report function.
            # self.report({'INFO'}, "Exporting is Locked Out")
            return False

        elif str(mcell.run_simulation.simulation_run_control) == 'QUEUE':
            processes_list = mcell.run_simulation.processes_list
            for pl_item in processes_list:
                pid = int(pl_item.name.split(',')[0].split(':')[1])
                q_item = cellblender.simulation_queue.task_dict[pid]
                if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                    return False
        return True


    def execute(self, context):
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        run_sim = mcell.run_simulation
        run_sim.last_simulation_run_time = str(time.time())

        # Calculate the number of runs and check against the limit
        start_seed = int(run_sim.start_seed.get_value())
        end_seed = int(run_sim.end_seed.get_value())
        run_limit = int(run_sim.run_limit.get_value())

        total_sweep_runs = ps.count_sweep_runs()
        print ( "Requested sweep runs = " + str(total_sweep_runs) )

        num_runs_requested = (1 + end_seed - start_seed) * total_sweep_runs
        print ( "Requested runs (including seeds) = " + str(num_runs_requested) )

        if mcell.cellblender_preferences.lockout_export and (not mcell.cellblender_preferences.decouple_export_run):
            print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            self.report({'INFO'}, "Exporting is Locked Out")
        elif (run_limit >=0) and (num_runs_requested > run_limit):
            print ( "Run limit exceeded. Reduce number of runs or increase limit." )
            self.report({'INFO'}, "Request for %d runs exceeds limit of %d" % (num_runs_requested, run_limit) )
        else:
            ### Note: This section of code was taken from the export for cases where a
            ###   newly opened .blend file is being run without being exported.
            ###   In that case, the project name was still defaulted to "cellblender_project".

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")
            # Change the actual scene name to the legal MCell Name
            context.scene.name = scene_name
            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            mcell.project_settings.base_name = scene_name

            print ( "Need to run " + str(mcell.run_simulation.simulation_run_control) )
            if str(mcell.run_simulation.simulation_run_control) == 'QUEUE':
                bpy.ops.mcell.run_simulation_control_queue()
            elif str(mcell.run_simulation.simulation_run_control) == 'COMMAND':
                bpy.ops.mcell.run_simulation_normal()
            elif str(run_sim.simulation_run_control) == 'SWEEP':
                bpy.ops.mcell.run_simulation_sweep()
            elif str(run_sim.simulation_run_control) == 'libMCell':
                bpy.ops.mcell.run_simulation_libmcell()
            elif str(run_sim.simulation_run_control) == 'libMCellpy':
                bpy.ops.mcell.run_simulation_libmcellpy()
            elif str(run_sim.simulation_run_control) == 'PurePython':
                bpy.ops.mcell.run_simulation_pure_python()
            else:
                # Look for it in the dynamic modules
                load_engine_modules()   # Note that this might already have been done ... except by the test suite!!
                load_runner_modules()   # Note that this might already have been done ... except by the test suite!!
                for m in cellblender.cellblender_info['cellblender_runner_modules']:
                    if str(mcell.run_simulation.simulation_run_control) == m.runner_code:
                        # Run with this module
                        print ( "Running a generic runner: " + str(mcell.run_simulation.simulation_run_control) )
                        run_generic_runner ( context, m )
                        break

        return {'FINISHED'}


def write_default_data_layout(project_dir, start, end):
    sweep_list_file_name = os.path.join ( project_dir, "data_layout.json" )
    sweep_list_file = open ( sweep_list_file_name, "w" )
    sweep_list_file.write ( "{\n" )
    sweep_list_file.write ( " \"version\": 0,\n" )
    sweep_list_file.write ( " \"data_layout\": [\n" )
    sweep_list_file.write ( "  [\"dir\", [\"output_data\"]],\n" )
    sweep_list_file.write ( "  [\"file_type\", [\"react_data\", \"viz_data\"]],\n" )
    sweep_list_file.write ( "  [\"SEED\", " + str([s for s in range(start,end+1)]) + "]\n" )
    sweep_list_file.write ( " ]\n" )
    sweep_list_file.write ( "}\n" )
    sweep_list_file.close()


class MCELL_OT_run_simulation_control_sweep (bpy.types.Operator):
    bl_idname = "mcell.run_simulation_sweep"
    bl_label = "Run MCell Simulation Command"
    bl_description = "Run MCell Simulation Command Line"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print("Executing Sweep Runner")

        mcell = context.scene.mcell
        mcell.run_simulation.last_simulation_run_time = str(time.time())

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

        start = int(mcell.run_simulation.start_seed.get_value())
        end = int(mcell.run_simulation.end_seed.get_value())
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (mcell.run_simulation.error_list and mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                sweep_dir = os.path.join(project_dir, "output_data")
                if (os.path.exists(sweep_dir) and mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(sweep_dir)
                if not os.path.exists(sweep_dir):
                    os.makedirs(sweep_dir)

                mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True )
                data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,"data_model.json") )

                base_name = mcell.project_settings.base_name

                error_file_option = mcell.run_simulation.error_file
                log_file_option = mcell.run_simulation.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))

                # The following Python program will create the "data_layout.json" file describing the directory structure
                script_file_path = os.path.join(script_dir_path, os.path.join("mdl", "run_data_model_mcell.py") )

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(
                    mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[
                    mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started MCell at: " + (str(time.ctime())) + "\n")

                # We have to create a new subprocess that in turn creates a
                # multiprocessing pool, instead of directly creating it here,
                # because the multiprocessing package requires that the __main__
                # module be importable by the children.
                print ( "Running subprocess with:" +
                        "\n  python_path = " + str(python_path) +
                        "\n  script_file_path = " + str(script_file_path) +
                        "\n  mcell_binary = " + str(mcell_binary) +
                        "\n  start = " + str(start) +
                        "\n  end = " + str(end) +
                        "\n  project_dir = " + str(project_dir) +
                        "\n  base_name = " + str(base_name) +
                        "\n  error_file_option = " + str(error_file_option) +
                        "\n  log_file_option = " + str(log_file_option) +
                        "\n  mcell_processes_str = " + str(mcell_processes_str) +
                        "\n" )
                sp = subprocess.Popen([
                    python_path,
                    script_file_path,
                    os.path.join(project_dir,"data_model.json"),
                    "-b", mcell_binary,
                    "-fs", str(start), "-ls", str(end),
                    "-pd", project_dir,
                    "-ef", error_file_option,
                    "-lf", log_file_option,
                    "-np", mcell_processes_str],
                    stdout=None,
                    stderr=None)
                self.report({'INFO'}, "Simulation Running")

                # This is a hackish workaround since we can't return arbitrary
                # objects from operators or store arbitrary objects in collection
                # properties, and we need to keep track of the progress of the
                # subprocess objects for the panels.
                cellblender.simulation_popen_list.append(sp)

                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_run_simulation_control_normal(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_normal"
    bl_label = "Run MCell Simulation Command"
    bl_description = "Run MCell Simulation Command Line"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        mcell.run_simulation.last_simulation_run_time = str(time.time())

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

        start = int(mcell.run_simulation.start_seed.get_value())
        end = int(mcell.run_simulation.end_seed.get_value())
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (mcell.run_simulation.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "output_data", "react_data")
                if (os.path.exists(react_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "output_data", "viz_data")
                if (os.path.exists(viz_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = mcell.run_simulation.error_file
                log_file_option = mcell.run_simulation.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))
                script_file_path = os.path.join(
                    script_dir_path, "run_simulations.py")

                # The following line will create the "data_layout.json" file describing the directory structure
                write_default_data_layout(project_dir, start, end)

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(
                    mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[
                    mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started MCell at: " + (str(time.ctime())) + "\n")

                # We have to create a new subprocess that in turn creates a
                # multiprocessing pool, instead of directly creating it here,
                # because the multiprocessing package requires that the __main__
                # module be importable by the children.
                sp = subprocess.Popen([
                    python_path, script_file_path, mcell_binary, str(start),
                    str(end + 1), os.path.join(project_dir,"output_data"), base_name, error_file_option,
                    log_file_option, mcell_processes_str], stdout=None,
                    stderr=None)
                self.report({'INFO'}, "Simulation Running")

                # This is a hackish workaround since we can't return arbitrary
                # objects from operators or store arbitrary objects in collection
                # properties, and we need to keep track of the progress of the
                # subprocess objects for the panels.
                cellblender.simulation_popen_list.append(sp)

                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_run_simulation_control_queue(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_control_queue"
    bl_label = "Run MCell Simulation Using Command Queue"
    bl_description = "Run MCell Simulation Using Command Queue"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        mcell.run_simulation.last_simulation_run_time = str(time.time())

        mcell_binary = cellblender_utils.get_mcell_path(mcell)

        start_seed = int(mcell.run_simulation.start_seed.get_value())
        end_seed = int(mcell.run_simulation.end_seed.get_value())
        mcell_processes = mcell.run_simulation.mcell_processes
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (mcell.run_simulation.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "output_data", "react_data")
                if (os.path.exists(react_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "output_data", "viz_data")
                if (os.path.exists(viz_dir) and
                        mcell.run_simulation.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = mcell.run_simulation.error_file
                log_file_option = mcell.run_simulation.log_file
                cellblender.simulation_queue.python_exec = python_path
                cellblender.simulation_queue.start(mcell_processes)
                cellblender.simulation_queue.notify = True

                # The following line will create the "data_layout.json" file describing the directory structure
                write_default_data_layout(project_dir, start_seed, end_seed)

                processes_list = mcell.run_simulation.processes_list
                for seed in range(start_seed,end_seed + 1):
                  processes_list.add()
                  mcell.run_simulation.active_process_index = len(
                      mcell.run_simulation.processes_list) - 1
                  simulation_process = processes_list[
                      mcell.run_simulation.active_process_index]

                  print("Starting MCell ... create start_time.txt file:")
                  with open(os.path.join(os.path.dirname(bpy.data.filepath),
                            "start_time.txt"), "w") as start_time_file:
                      start_time_file.write(
                          "Started MCell at: " + (str(time.ctime())) + "\n")

                  # Log filename will be log.year-month-day_hour:minute_seed.txt
                  # (e.g. log.2013-03-12_11:45_1.txt)
                  time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

                  if error_file_option == 'file':
                      error_filename = "error.%s_%d.txt" % (time_now, seed)
                  elif error_file_option == 'none':
                      error_file = subprocess.DEVNULL
                  elif error_file_option == 'console':
                      error_file = None

                  if log_file_option == 'file':
                      log_filename = "log.%s_%d.txt" % (time_now, seed)
                  elif log_file_option == 'none':
                      log_file = subprocess.DEVNULL
                  elif log_file_option == 'console':
                      log_file = None

                  mdl_filename = '%s.main.mdl' % (base_name)
                  mcell_args = '-seed %d %s' % (seed, mdl_filename)
                  make_texts = mcell.run_simulation.save_text_logs
                  proc = cellblender.simulation_queue.add_task(mcell_binary, mcell_args, os.path.join(project_dir, "output_data"), make_texts)

                  self.report({'INFO'}, "Simulation Running")

                  simulation_process.name = ("PID: %d, MDL: %s, " "Seed: %d" % (proc.pid, mdl_filename, seed))

        else:
            status = "Python not found. Set it in Project Settings."

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_kill_simulation(bpy.types.Operator):
    bl_idname = "mcell.kill_simulation"
    bl_label = "Kill Selected Simulation"
    bl_description = ("Kill/Cancel Selected Running/Queued MCell Simulation. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}


    @classmethod
    def poll(self,context):
        mcell = context.scene.mcell
        processes_list = mcell.run_simulation.processes_list
        active_index = mcell.run_simulation.active_process_index
        ap = processes_list[active_index]
        pid = int(ap.name.split(',')[0].split(':')[1])
        q_item = cellblender.simulation_queue.task_dict.get(pid)
        if q_item:
            if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                return True

    def execute(self, context):

        mcell = context.scene.mcell

        processes_list = mcell.run_simulation.processes_list
        active_index = mcell.run_simulation.active_process_index
        ap = processes_list[active_index]
        pid = int(ap.name.split(',')[0].split(':')[1])
        q_item = cellblender.simulation_queue.task_dict.get(pid)
        if q_item:
            if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                # Simulation is running or waiting in queue, so let's kill it
                cellblender.simulation_queue.kill_task(pid)

        return {'FINISHED'}


class MCELL_OT_kill_all_simulations(bpy.types.Operator):
    bl_idname = "mcell.kill_all_simulations"
    bl_label = "Kill All Simulations"
    bl_description = ("Kill/Cancel All Running/Queued MCell Simulations. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        processes_list = mcell.run_simulation.processes_list

        for p_item in processes_list:
            pid = int(p_item.name.split(',')[0].split(':')[1])
            q_item = cellblender.simulation_queue.task_dict.get(pid)
            if q_item:
                if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                    # Simulation is running or waiting in queue, so let's kill it
                    cellblender.simulation_queue.kill_task(pid)

        return {'FINISHED'}




class MCELL_OT_run_simulation_libmcell(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_libmcell"
    bl_label = "Run MCell Simulation Control libmcell"
    bl_description = "Run MCell Simulation Control libmcell"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        mcell.run_simulation.last_simulation_run_time = str(time.time())

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

        start = int(mcell.run_simulation.start_seed.get_value())
        end = int(mcell.run_simulation.end_seed.get_value())
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        if not mcell.cellblender_preferences.decouple_export_run:
            bpy.ops.mcell.export_project()

        if (mcell.run_simulation.error_list and
                mcell.cellblender_preferences.invalid_policy == 'dont_run'):
            pass
        else:
            react_dir = os.path.join(project_dir, "output_data", "react_data")
            if os.path.exists(react_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(react_dir)
            if not os.path.exists(react_dir):
                os.makedirs(react_dir)

            viz_dir = os.path.join(project_dir, "output_data", "viz_data")
            if os.path.exists(viz_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)

            base_name = mcell.project_settings.base_name

            error_file_option = mcell.run_simulation.error_file
            log_file_option = mcell.run_simulation.log_file
            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(script_dir_path, "engine_runner_combos")
            final_script_path = os.path.join(script_file_path,"mcell_main")

            # The following line will create the "data_layout.json" file describing the directory structure
            write_default_data_layout(project_dir, start, end)

            if not os.path.exists(final_script_path):
                print ( "\n\nUnable to run, script does not exist: " + final_script_path + "\n\n" )
            else:

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath), "start_time.txt"), "w") as start_time_file:
                    start_time_file.write("Started MCell at: " + (str(time.ctime())) + "\n")

                # Create a subprocess for each simulation

                window_num = 0

                for sim_seed in range(start,end+1):
                    print ("Running with seed " + str(sim_seed) )

                    command_list = [ final_script_path, "proj_path="+project_dir, "data_model=dm.json", "seed=%ld"%sim_seed ]

                    dm = mcell.build_data_model_from_properties ( context, geometry=True )

                    print ( "Data Model = " + str(dm) )

                    data_model.save_data_model_to_json_file ( dm, os.path.join(project_dir,"dm.json") )

                    command_string = "Command:";
                    for s in command_list:
                      command_string += " " + s
                    print ( command_string )

                    sp = subprocess.Popen ( command_list, cwd=script_file_path, stdout=None, stderr=None )

                    self.report({'INFO'}, "Simulation Running")

                    # This is a hackish workaround since we can't return arbitrary
                    # objects from operators or store arbitrary objects in collection
                    # properties, and we need to keep track of the progress of the
                    # subprocess objects for the panels.
                    cellblender.simulation_popen_list.append(sp)
                    window_num += 1


                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))

        mcell.run_simulation.status = status

        return {'FINISHED'}



class MCELL_OT_run_simulation_libmcellpy(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_libmcellpy"
    bl_label = "Run MCell Simulation Control libmcell Python"
    bl_description = "Run MCell Simulation Control libmcell Python"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        mcell.run_simulation.last_simulation_run_time = str(time.time())

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

        start = int(mcell.run_simulation.start_seed.get_value())
        end = int(mcell.run_simulation.end_seed.get_value())
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        if not mcell.cellblender_preferences.decouple_export_run:
            bpy.ops.mcell.export_project()

        if (mcell.run_simulation.error_list and
                mcell.cellblender_preferences.invalid_policy == 'dont_run'):
            pass
        else:
            react_dir = os.path.join(project_dir, "output_data", "react_data")
            if os.path.exists(react_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(react_dir)
            if not os.path.exists(react_dir):
                os.makedirs(react_dir)

            viz_dir = os.path.join(project_dir, "output_data", "viz_data")
            if os.path.exists(viz_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)

            base_name = mcell.project_settings.base_name

            error_file_option = mcell.run_simulation.error_file
            log_file_option = mcell.run_simulation.log_file
            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(script_dir_path, "engine_runner_combos")
            final_script_path = os.path.join(script_file_path,"mcell_main.py")

            # The following line will create the "data_layout.json" file describing the directory structure
            write_default_data_layout(project_dir, start, end)

            if not os.path.exists(final_script_path):
                print ( "\n\nUnable to run, script does not exist: " + final_script_path + "\n\n" )
            else:

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath), "start_time.txt"), "w") as start_time_file:
                    start_time_file.write("Started MCell at: " + (str(time.ctime())) + "\n")

                # Create a subprocess for each simulation

                window_num = 0

                for sim_seed in range(start,end+1):
                    print ("Running with seed " + str(sim_seed) )

                    command_list = [ 'python', final_script_path, "proj_path="+project_dir, "data_model=dm.txt" ]

                    dm = mcell.build_data_model_from_properties ( context, geometry=True )

                    print ( "Data Model = " + str(dm) )

                    data_model.save_data_model_to_file ( dm, os.path.join(project_dir,"dm.txt") )

                    command_string = "Command:";
                    for s in command_list:
                      command_string += " " + s
                    print ( command_string )

                    sp = subprocess.Popen ( command_list, cwd=script_file_path, stdout=None, stderr=None )

                    self.report({'INFO'}, "Simulation Running")

                    # This is a hackish workaround since we can't return arbitrary
                    # objects from operators or store arbitrary objects in collection
                    # properties, and we need to keep track of the progress of the
                    # subprocess objects for the panels.
                    cellblender.simulation_popen_list.append(sp)
                    window_num += 1


                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_run_simulation_pure_python(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_pure_python"
    bl_label = "Run MCell Simulation Control libmcell Pure Python"
    bl_description = "Run MCell Simulation Control libmcell Pure Python"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        mcell.run_simulation.last_simulation_run_time = str(time.time())

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

        start = int(mcell.run_simulation.start_seed.get_value())
        end = int(mcell.run_simulation.end_seed.get_value())
        mcell_processes_str = str(mcell.run_simulation.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        if not mcell.cellblender_preferences.decouple_export_run:
            bpy.ops.mcell.export_project()

        if (mcell.run_simulation.error_list and
                mcell.cellblender_preferences.invalid_policy == 'dont_run'):
            pass
        else:
            react_dir = os.path.join(project_dir, "output_data", "react_data")
            if os.path.exists(react_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(react_dir)
            if not os.path.exists(react_dir):
                os.makedirs(react_dir)

            viz_dir = os.path.join(project_dir, "output_data", "viz_data")
            if os.path.exists(viz_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)

            base_name = mcell.project_settings.base_name

            error_file_option = mcell.run_simulation.error_file
            log_file_option = mcell.run_simulation.log_file
            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(script_dir_path, "engine_runner_combos")
            final_script_path = os.path.join(script_file_path,"pure_python_sim.py")

            # The following line will create the "data_layout.json" file describing the directory structure
            write_default_data_layout(project_dir, start, end)

            if not os.path.exists(final_script_path):
                print ( "\n\nUnable to run, script does not exist: " + final_script_path + "\n\n" )
            else:

                processes_list = mcell.run_simulation.processes_list
                processes_list.add()
                mcell.run_simulation.active_process_index = len(mcell.run_simulation.processes_list) - 1
                simulation_process = processes_list[mcell.run_simulation.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath), "start_time.txt"), "w") as start_time_file:
                    start_time_file.write("Started MCell at: " + (str(time.ctime())) + "\n")

                # Create a subprocess for each simulation

                window_num = 0

                for sim_seed in range(start,end+1):
                    print ("Running with seed " + str(sim_seed) )

                    command_list = [ 'python3', final_script_path, "proj_path="+project_dir, "data_model=dm.txt" ]

                    dm = mcell.build_data_model_from_properties ( context, geometry=True )

                    print ( "Data Model = " + str(dm) )

                    data_model.save_data_model_to_file ( dm, os.path.join(project_dir,"dm.txt") )

                    command_string = "Command:";
                    for s in command_list:
                      command_string += " " + s
                    print ( command_string )

                    sp = subprocess.Popen ( command_list, cwd=script_file_path, stdout=None, stderr=None )

                    self.report({'INFO'}, "Simulation Running")

                    # This is a hackish workaround since we can't return arbitrary
                    # objects from operators or store arbitrary objects in collection
                    # properties, and we need to keep track of the progress of the
                    # subprocess objects for the panels.
                    cellblender.simulation_popen_list.append(sp)
                    window_num += 1


                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seed: %d" % (sp.pid, base_name,
                                                             start))
                else:
                    simulation_process.name = ("PID: %d, MDL: %s.main.mdl, "
                                               "Seeds: %d-%d" % (sp.pid, base_name,
                                                                 start, end))

        mcell.run_simulation.status = status

        return {'FINISHED'}


class MCELL_OT_remove_text_logs(bpy.types.Operator):
    bl_idname = "mcell.remove_text_logs"
    bl_label = "Remove Task Output Texts"
    bl_description = ("Remove all text files of name \"task_*_output\".")
    bl_options = {'REGISTER'}

    def execute(self, context):
        for k in bpy.data.texts.keys():
            if (k[0:5] == "task_") and (k[-7:] == "_output"):
                print ( "Removing text: " + str(k) )
                bpy.data.texts.remove ( bpy.data.texts[k] )
        return {'FINISHED'}


class MCELL_OT_clear_run_list(bpy.types.Operator):
    bl_idname = "mcell.clear_run_list"
    bl_label = "Clear Completed MCell Runs"
    bl_description = ("Clear the list of completed and failed MCell runs. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        # The collection property of subprocesses
        processes_list = mcell.run_simulation.processes_list
        # A list holding actual subprocess objects
        simulation_popen_list = cellblender.simulation_popen_list
        sim_list_length = len(simulation_popen_list)
        idx = 0
        ctr = 0

        while ctr < sim_list_length:
            ctr += 1
            sp = simulation_popen_list[idx]
            # Simulation set is still running. Leave it in the collection
            # property and list of subprocess objects.
            if sp.poll() is None:
                idx += 1
            # Simulation set has failed or finished. Remove it from
            # collection property and the list of subprocess objects.
            else:
                processes_list.remove(idx)
                simulation_popen_list.pop(idx)
                mcell.run_simulation.active_process_index -= 1
                if (mcell.run_simulation.active_process_index < 0):
                    mcell.run_simulation.active_process_index = 0

        return {'FINISHED'}


class MCELL_OT_clear_simulation_queue(bpy.types.Operator):
    bl_idname = "mcell.clear_simulation_queue"
    bl_label = "Clear Completed MCell Runs"
    bl_description = ("Clear the list of completed and failed MCell runs. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        # The collection property of subprocesses
        processes_list = mcell.run_simulation.processes_list
        # Class holding actual subprocess objects
        simulation_queue = cellblender.simulation_queue
        proc_list_length = len(processes_list)
        idx = 0
        ctr = 0

        while ctr < proc_list_length:
            ctr += 1
            pid = int(processes_list[idx].name.split(',')[0].split(':')[1])
            q_item = simulation_queue.task_dict.get(pid)
            if q_item:
                proc = q_item['process']
                if (q_item['status'] == 'queued') or (q_item['status'] == 'running'):
                    # Simulation is still running. Leave it in the collection
                    # property and simulation queue
                    idx += 1
                    pass
                else:
                    # Simulation has failed or finished. Remove it from
                    # collection property and the simulation queue
                    simulation_queue.clear_task(pid)
                    processes_list.remove(idx)
                    if idx <= mcell.run_simulation.active_process_index:
                        mcell.run_simulation.active_process_index -= 1
                        if (mcell.run_simulation.active_process_index < 0):
                            mcell.run_simulation.active_process_index = 0
            else:
                # Process is missing from simulation queue
                # so remove it from collection property
                processes_list.remove(idx)
                if idx <= mcell.run_simulation.active_process_index:
                    mcell.run_simulation.active_process_index -= 1
                    if (mcell.run_simulation.active_process_index < 0):
                        mcell.run_simulation.active_process_index = 0

        return {'FINISHED'}


global_scripting_enabled_once = False

class MCELL_OT_initialize_scripting (bpy.types.Operator):
    bl_idname = "mcell.initialize_scripting"
    bl_label = "Initialize Scripting"
    bl_description = ("Must be done every time CellBLender is restarted.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        global global_scripting_enabled_once
        global_scripting_enabled_once = True
        return {'FINISHED'}



# Simulation callback functions


@persistent
def disable_python(context):
    """ Disable running of Python Scripts whenever a new .blend file is loaded """

    print ( "load post handler: cellblender_simulation.disable_python() called" )

    #if not context:
    #    context = bpy.context
    #
    # context.scene.mcell.run_simulation.enable_python_scripting = False

    # Be sure to disable it in all other scenes as well

    # Use ID properties first
    for scn in bpy.data.scenes:
      print ( "Attempting to disable ID scripting for Scene " + str(scn) )
      if 'mcell' in scn:
        if 'run_simulation' in scn['mcell']:
          if 'enable_python_scripting' in scn['mcell']['run_simulation']:
            scn['mcell']['run_simulation']['enable_python_scripting'] = 0

    # Use RNA properties second
    for scn in bpy.data.scenes:
      print ( "Attempting to disable RNA scripting for Scene " + str(scn) )
      if 'mcell' in scn:
        if 'run_simulation' in scn.mcell:
          if 'enable_python_scripting' in scn.mcell.run_simulation:
            scn.mcell.run_simulation.enable_python_scripting = False



@persistent
def clear_run_list(context):
    """ Clear processes_list when loading a blend.

    Data in simulation_popen_list can not be saved with the blend, so we need
    to clear the processes_list upon reload so the two aren't out of sync.

    """
    print ( "load post handler: cellblender_simulation.clear_run_list() called" )

    if not context:
        context = bpy.context

    processes_list = context.scene.mcell.run_simulation.processes_list

    if not cellblender.simulation_popen_list:
        processes_list.clear()

    if not cellblender.simulation_queue:
        processes_list.clear()


def sim_engine_changed_callback ( self, context ):
    """ The run lists are somewhat incompatible between sim runners, so just clear them when switching. """
    # print ( "Sim Runner has been changed!!" )
    # mcell = context.scene.mcell
    bpy.ops.mcell.clear_run_list()
    bpy.ops.mcell.clear_simulation_queue()


def sim_runner_changed_callback ( self, context ):
    """ The run lists are somewhat incompatible between sim runners, so just clear them when switching. """
    # print ( "Sim Runner has been changed!!" )
    # mcell = context.scene.mcell
    bpy.ops.mcell.clear_run_list()
    bpy.ops.mcell.clear_simulation_queue()


def check_start_seed(self, context):
    """ Ensure start seed is always lte to end seed. """

    run_sim = context.scene.mcell.run_simulation

    start_seed = int(run_sim.start_seed.get_value())
    end_seed = int(run_sim.end_seed.get_value())

    if start_seed > end_seed:
        run_sim.start_seed.expr = str(end_seed)

def check_end_seed(self, context):
    """ Ensure end seed is always gte to start seed. """
    
    run_sim = context.scene.mcell.run_simulation
    start_seed = int(run_sim.start_seed.get_value())
    end_seed = int(run_sim.end_seed.get_value())

    if end_seed < start_seed:
        run_sim.end_seed.expr = str(start_seed)




# Simulation Panel Classes


class MCELL_UL_error_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.label(item.name, icon='ERROR')

class MCELL_UL_run_simulation(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if len(cellblender.simulation_popen_list) > index:
            sp = cellblender.simulation_popen_list[index]
            # Simulations are still running
            if sp.poll() is None:
                layout.label(item.name, icon='POSE_DATA')
            # Simulations have failed or were killed
            elif sp.returncode != 0:
                layout.label(item.name, icon='ERROR')
            # Simulations have finished
            else:
                layout.label(item.name, icon='FILE_TICK')
        else:
            # Indexing error may be caused by stale data in the simulation_popen_list?? Maybe??
            layout.label(item.name, icon='ERROR')


class MCELL_PT_run_simulation(bpy.types.Panel):
    bl_label = "CellBlender - Run Simulation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.run_simulation.draw_panel ( context, self )


class MCELL_UL_run_simulation_queue(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if len(cellblender.simulation_queue.task_dict) > index:
            pid = int(item.name.split(',')[0].split(':')[1])
            q_item = cellblender.simulation_queue.task_dict[pid]
            proc = q_item['process']
            if q_item['status'] == 'queued':
                # Simulation is queued, waiting to run
                layout.label(item.name, icon='TIME')
            elif q_item['status'] == 'running':
                # Simulation is still running
                layout.label(item.name, icon='POSE_DATA')
            elif q_item['status'] == 'mcell_error':
                # Simulation failed due to error detected by MCell
                layout.label(item.name, icon='ERROR')
            elif q_item['status'] == 'died':
                # Simulation was killed or failed due to some other error
                layout.label(item.name, icon='CANCEL')
            else:
                # Simulation has finished normally
                layout.label(item.name, icon='FILE_TICK')
        else:
            # Indexing error may be caused by stale data in the simulation_popen_list?? Maybe??
            layout.label(item.name, icon='ERROR')


class MCELL_PT_run_simulation_queue(bpy.types.Panel):
    bl_label = "CellBlender - Run Simulation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.run_simulation.draw_panel ( context, self )


# Simulation Property Groups

class MCellRunSimulationProcessesProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Simulation Runner Process")
    #pid = IntProperty(name="PID")

    def remove_properties ( self, context ):
        print ( "Removing all Run Simulation Process Properties for " + self.name + "... no collections to remove." )

    def build_data_model_from_properties ( self, context ):
        print ( "MCellRunSimulationProcesses building Data Model" )
        dm = {}
        dm['data_model_version'] = "DM_2015_04_23_1753"
        dm['name'] = self.name
        return dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellRunSimulationProcessesProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_23_1753
            dm['data_model_version'] = "DM_2015_04_23_1753"

        if dm['data_model_version'] != "DM_2015_04_23_1753":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationProcessesProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_04_23_1753":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationProcessesProperty data model to current version." )
        self.name = dm["name"]


class MCellSimStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell String Property with name \"" + self.name + "\" ... no collections to remove." )
        pass

import os
import cellblender.sim_engines
import cellblender.sim_runners

def load_engine_modules():
    if not ('cellblender_engine_modules' in cellblender.cellblender_info):
      print ( "\n\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%\n\nload_engine_modules reloading list\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n\n" )
      cellblender.cellblender_info['cellblender_engine_modules'] = cellblender.sim_engines.get_sim_engine_modules()

def get_engines_as_items(scene, context):
    load_engine_modules()
    # Start with static modules
    engines_list = [("NONE", "Choose Engine", "")]
    # Add the dynamic modules
    for m in cellblender.cellblender_info['cellblender_engine_modules']:
      engines_list.append ( (m.engine_code, m.engine_name + " (dyn)", "") )
    return engines_list


def load_runner_modules():
    if not ('cellblender_runner_modules' in cellblender.cellblender_info):
      print ( "\n\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%\n\nload_runner_modules reloading list\n\n%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n\n" )
      cellblender.cellblender_info['cellblender_runner_modules'] = cellblender.sim_runners.get_sim_runner_modules()

def get_runners_as_items(scene, context):
    load_runner_modules()
    # Start with static modules
    runners_list = [("NONE", "Choose Runner", "")]
    # Add the dynamic modules
    for m in cellblender.cellblender_info['cellblender_runner_modules']:
      runners_list.append ( (m.runner_code, m.runner_name + " (dyn)", "") )
    return runners_list


class MCellRunSimulationPropertyGroup(bpy.types.PropertyGroup):
    enable_python_scripting = BoolProperty ( name='Enable Python Scripting', default=False )  # Intentionally not in the data model

    start_seed = PointerProperty ( name="Start Seed", type=parameter_system.Parameter_Reference )
    end_seed   = PointerProperty ( name="End Seed", type=parameter_system.Parameter_Reference )
    run_limit  = PointerProperty ( name="Run Limit", type=parameter_system.Parameter_Reference )
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
        items=log_file_enum, name="Output Log", default='console',
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
    error_list = CollectionProperty(
        type=MCellSimStringProperty,
        name="Error List")
    active_err_index = IntProperty(
        name="Active Error Index", default=0)

    show_output_options = BoolProperty ( name='Output Options', default=False )
    show_engine_runner_options = BoolProperty ( name='Engine/Runners (experimental)', default=False )
    show_engine_runner_help = BoolProperty ( default=False )
    python_scripting_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    python_initialize_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    save_text_logs = BoolProperty ( name='Save Text Logs', default=False, description="Create a text log for each run" )

    # This would be better as a double, but Blender would store as a float which doesn't have enough precision to resolve time in seconds from the epoch.
    last_simulation_run_time = StringProperty ( default="-1.0", description="Time that the simulation was last run" )

    simulation_engine_control = EnumProperty(
        items=get_engines_as_items, name="",
        description="Simulators for running a simulation",
        # default='QUEUE', # Cannot set a default when "items" is a function
        update=sim_runner_changed_callback)

    simulation_runners = EnumProperty(
        items=get_runners_as_items, name="",
        description="Control mechanisms for running the selected simulation engine",
        # default='QUEUE', # Cannot set a default when "items" is a function
        update=sim_runner_changed_callback)


    simulation_engine_and_run_enum = [
         ('QUEUE', "MCell via Queue Runner", ""),
         ('COMMAND', "MCell via Command Line", ""),
         ('JAVA', "MCell via Java Runner", ""),
         ('OPENGL', "MCell via OpenGL Runner", ""),
         ('SWEEP', "MCell via Sweep Runner", ""),
         ('libMCell', "Prototype Lib MCell via C++", ""),
         ('libMCellpy', "Prototype Lib MCell via Python", ""),
         ('PurePython', "Prototype Pure Python", ""),
         ('NONE', "None", "")]

    simulation_run_control = EnumProperty(
        items=simulation_engine_and_run_enum, name="",
        description="Mechanism for running and controlling a specific simulation",
        # default='QUEUE', # Cannot set a default when "items" is a function
        update=sim_runner_changed_callback)


    def init_properties ( self, parameter_system ):
        helptext = "Start Seed\n" + \
                   "The first seed used in running a series of simulations.\n" + \
                   "The number of simulations depends on the start and end seeds."
        self.start_seed.init_ref   ( parameter_system, user_name="Start Seed",   user_expr="1", user_units="", user_descr=helptext )

        helptext = "End Seed\n" + \
                   "The last seed used in running a series of simulations.\n" + \
                   "The number of simulations depends on the start and end seeds."
        self.end_seed.init_ref   ( parameter_system, user_name="End Seed",   user_expr="1", user_units="", user_descr=helptext )

        helptext = "Run Limit\n" + \
                   "Maximum number of simulation runs that can be submitted.\n" + \
                   "This setting provides a safeguard against running more runs than expected.\n" + \
                   "A value of -1 implies no limit.\n" + \
                   "The default for upgraded files is -1 since they had no limit."
        self.run_limit.init_ref   ( parameter_system, user_name="Run Limit",   user_expr="12", user_units="", user_descr=helptext, user_int=True )



    def remove_properties ( self, context ):
        print ( "Removing all Run Simulation Properties..." )
        # Note that the three "Panel Parameters" (start_seed, end_seed, and run_limit) in this group are all static and should not be removed.
        #self.start_seed.clear_ref ( ps )
        #self.end_seed.clear_ref ( ps )
        #self.run_limit.clear_ref ( ps )

        for item in self.processes_list:
            item.remove_properties(context)
        self.processes_list.clear()
        self.active_process_index = 0

        for item in self.error_list:
            item.remove_properties(context)

        self.error_list.clear()
        self.active_err_index = 0
        print ( "Done removing all Run Simulation Properties." )


    def build_data_model_from_properties ( self, context ):
        print ( "MCellRunSimulationPropertyGroup building Data Model" )
        dm = {}
        dm['data_model_version'] = "DM_2016_10_27_1642"
        dm['name'] = self.name
        dm['start_seed'] = self.start_seed.get_expr()
        dm['end_seed'] = self.end_seed.get_expr()
        dm['run_limit'] = self.run_limit.get_expr()
        p_list = []
        for p in self.processes_list:
            p_list.append ( p.build_data_model_from_properties(context) )
        dm['processes_list'] = p_list
        return dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellRunSimulationPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_23_1753
            dm['data_model_version'] = "DM_2015_04_23_1753"

        if dm['data_model_version'] == "DM_2015_04_23_1753":
            # Add the start_seed and end_seed to the data model with default values
            dm['start_seed'] = "1"
            dm['end_seed'] = "1"
            dm['data_model_version'] = "DM_2016_04_15_1430"

        if dm['data_model_version'] == "DM_2016_04_15_1430":
            # Add the run_limit to the data model with an unlimited value (-1)
            dm['run_limit'] = "-1"
            dm['data_model_version'] = "DM_2016_10_27_1642"

        if dm['data_model_version'] != "DM_2016_10_27_1642":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )
            return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2016_10_27_1642":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )

        self.enable_python_scripting = False  # Explicitly disable this when building from a data model
        if 'name' in dm:
            self.name = dm["name"]
        print ( "Setting start and end seeds to " + dm['start_seed'] + " and " + dm['end_seed'] )
        print ( "Setting the run limit to " + dm['run_limit'] )
        self.start_seed.set_expr ( dm["start_seed"] )
        self.end_seed.set_expr ( dm["end_seed"] )
        self.run_limit.set_expr ( dm["run_limit"] )
        self.processes_list.clear()

        # The processes_list should not be restored from the data model
        #if 'processes_list' in dm:
        #    for p in dm['processes_list']:
        #        self.processes_list.add()
        #        self.active_process_index = len(self.processes_list) - 1
        #        self.processes_list[self.active_process_index].build_properties_from_data_model(context, p)



    def draw_layout_queue(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")

            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            #mcell.project_settings.base_name = scene_name

            main_mdl = mcell_files_path()
            main_mdl = os.path.join(main_mdl, "output_data")
            main_mdl = os.path.join(main_mdl, scene_name + ".main.mdl")

            global global_scripting_enabled_once

            if global_scripting_enabled_once:

                helptext = "Allow Running of Python Code in Scripting Panel\n" + \
                           " \n" + \
                           "The Scripting Interface can run Python code contained\n" + \
                           "in text files (text blocks) within Blender.\n" + \
                           "\n" + \
                           "Running scripts from unknown sources is a security risk.\n" + \
                           "Only enable this option if you are confident that all of\n" + \
                           "the scripts contained in this .blend file are safe to run."
                ps.draw_prop_with_help ( layout, "Enable Python Scripting", self,
                           "enable_python_scripting", "python_scripting_show_help",
                           self.python_scripting_show_help, helptext )

            #else:

            #    row = layout.row()
            #    col = row.column()
            #    col.label ( "Enable Scripting" )
            #    col = row.column()
            #    col.operator ( "mcell.initialize_scripting" )


            row = layout.row()

            # Only allow the simulation to be run if both an MCell binary and a
            # project dir have been selected. There also needs to be a main mdl
            # file present.
            if not cellblender_utils.get_mcell_path(mcell):
                # Note that we should be able to export without requiring an MCell Binary,
                #  but this code is a little messy as it is ... so this requirement remains.
                row.label(text="Set an MCell binary in CellBlender - Preferences Panel", icon='ERROR')
            elif not os.path.dirname(bpy.data.filepath):
                row.label(
                    text="Open or save a .blend file to set the project directory", icon='ERROR')
            elif (not os.path.isfile(main_mdl) and
                    mcell.cellblender_preferences.decouple_export_run):
                row.label(text="Export the project", icon='ERROR')
                row = layout.row()
                row.operator("mcell.export_project",
                    text="Export CellBlender Project", icon='EXPORT')
            else:

                row = layout.row(align=True)
                if mcell.cellblender_preferences.decouple_export_run:
                    if mcell.cellblender_preferences.lockout_export:
                        row.operator( "mcell.export_project", 
                            text="Export CellBlender Project", icon='CANCEL')
                    else:
                        row.operator( "mcell.export_project",
                            text="Export CellBlender Project", icon='EXPORT')
                    row.operator("mcell.run_simulation", text="Run", icon='COLOR_RED')
                else:
                    if mcell.cellblender_preferences.lockout_export:
                        row.operator("mcell.run_simulation", text="Export & Run", icon='CANCEL')
                    else:
                        row.operator("mcell.run_simulation", text="Export & Run", icon='COLOR_RED')

                
                if self.simulation_run_control != "QUEUE":
                    if self.processes_list and (len(self.processes_list) > 0):
                        row = layout.row()
                        row.template_list("MCELL_UL_run_simulation", "run_simulation",
                                          self, "processes_list",
                                          self, "active_process_index",
                                          rows=2)
                        row = layout.row()
                        row.operator("mcell.clear_run_list")

                else:

                    if (self.processes_list and
                            cellblender.simulation_queue.task_dict):
                        row = layout.row()
                        row.label(text="MCell Processes:",
                                  icon='FORCE_LENNARDJONES')
                        row = layout.row()
                        row.template_list("MCELL_UL_run_simulation_queue", "run_simulation_queue",
                                          self, "processes_list",
                                          self, "active_process_index",
                                          rows=2)


                        # Check to see if there are any errors for the selected item and display if non-empty
                        processes_list = mcell.run_simulation.processes_list
                        proc_list_length = len(processes_list)
                        if proc_list_length > 0:
                            active_process_index = mcell.run_simulation.active_process_index
                            simulation_queue = cellblender.simulation_queue
                            pid = int(processes_list[active_process_index].name.split(',')[0].split(':')[1])
                            q_item = cellblender.simulation_queue.task_dict[pid]

                            if q_item['stderr'] != b'':
                                serr = str(q_item['stderr'])
                                if len(serr) > 0:
                                    row = layout.row()
                                    row.label ( "Error from task " + str(pid), icon="ERROR" )
                                    serr_list = serr.split('\n')
                                    for l in serr_list:
                                        row = layout.row()
                                        row.label ( "  " + l, icon="BLANK1" )

                            sout = str(q_item['stdout'])
                            if False and (len(sout) > 0):
                                row = layout.row()
                                row.label ( "Out: " + sout )


                        row = layout.row()
                        row.operator("mcell.clear_simulation_queue")
                        row = layout.row()
                        row.operator("mcell.kill_simulation")
                        row.operator("mcell.kill_all_simulations")


                box = layout.box()

                if self.show_output_options:
                    row = box.row(align=True)
                    row.alignment = 'LEFT'
                    row.prop(self, "show_output_options", icon='TRIA_DOWN',
                             text="Output / Control Options", emboss=False)

                    self.start_seed.draw(box,ps)
                    self.end_seed.draw(box,ps)
                    self.run_limit.draw(box,ps)

                    row = box.row()
                    row.prop(self, "mcell_processes")
                    #row = box.row()
                    #row.prop(self, "log_file")
                    #row = box.row()
                    #row.prop(self, "error_file")
                    row = box.row()
                    row.prop(mcell.export_project, "export_format")


                    row = box.row()
                    row.prop(self, "remove_append", expand=True)


                    #row = box.row()
                    #col = row.column()
                    #col.label ( "Enable Scripting" )
                    #col = row.column()
                    #col.operator ( "mcell.initialize_scripting", icon="COLOR_RED" )

                    helptext = "Initialize Python Code Scripting for this Session\n" + \
                               "This must be done each time CellBlender is restarted."
                    ps.draw_operator_with_help ( box, "Enable Python Scripting", self,
                               "mcell.initialize_scripting", "python_initialize_show_help",
                               self.python_initialize_show_help, helptext )



                    row = box.row()
                    col = row.column()
                    col.prop(mcell.cellblender_preferences, "decouple_export_run")

                    # Generally hide the selector for simulation_run_control options
                    #  Queue control is the default
                    #  Queue control is currently the only option which properly disables the
                    #  run_simulation operator while simulations are currenlty running or queued
                    # Only show this option it when specifically requested
                    #if mcell.cellblender_preferences.show_sim_runner_options:
                    col = row.column()
                    col.prop(self, "simulation_run_control")
                    
                    # This will eventually show the panel for the selected runner

                    if self.simulation_run_control == "QUEUE":
                        row = box.row()
                        row.prop ( self, "save_text_logs" )
                        row.operator("mcell.remove_text_logs")


                else:
                    row = box.row(align=True)
                    row.alignment = 'LEFT'
                    row.prop(self, "show_output_options", icon='TRIA_RIGHT',
                             text="Output / Control Options", emboss=False)


                box = layout.box()

                if self.show_engine_runner_options:
                    row = box.row(align=True)
                    row.alignment = 'LEFT'
                    col = row.column()
                    col.alignment = 'LEFT'
                    col.prop(self, "show_engine_runner_options", icon='TRIA_DOWN',
                             text="Engine / Runner Options (experimental)", emboss=False)
                    col = row.column()
                    col.alignment = 'RIGHT'
                    col.prop ( self, "show_engine_runner_help", icon='INFO', text="" )
                    if self.show_engine_runner_help:
                        row = box.row()
                        row.label ( ">>> Select different simulation engines and run mechanisms <<<" )
                        row = box.row()
                        row.label ( "This experimental panel will eventually permit the independent selection of" )
                        row = box.row()
                        row.label ( "simulation engines and run mechanisms. This will become increasingly important" )
                        row = box.row()
                        row.label ( "as CellBlender supports custom instances of libMCell and distributed computing." )
                        row = box.row()
                        row.label ( "To enable the selections in this panel, choose \"None\" in the normal run control." )
                        row = box.row()


                    row = box.row()
                    row.label ( "Simulate with:" )
                    row.prop(self, "simulation_engine_control")

                    row = box.row()
                    row.label ( "Run with:" )
                    row.prop(self, "simulation_runners")

                else:
                    row = box.row(align=True)
                    row.alignment = 'LEFT'
                    row.prop(self, "show_engine_runner_options", icon='TRIA_RIGHT',
                             text="Engine / Runner Options (experimental)", emboss=False)


                
            if self.status:
                row = layout.row()
                row.label(text=self.status, icon='ERROR')
            
            if self.error_list: 
                row = layout.row() 
                row.label(text="Errors:", icon='ERROR')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_error_list", "run_simulation_queue",
                                  self, "error_list",
                                  self, "active_err_index", rows=2)


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout_queue ( context, layout )



