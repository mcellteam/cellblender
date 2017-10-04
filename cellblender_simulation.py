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
import math


# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils
from . import data_model

#from cellblender.mdl import data_model_to_mdl
#from cellblender.mdl import run_data_model_mcell

from cellblender.cellblender_utils import mcell_files_path

from multiprocessing import cpu_count

import cellblender.sim_engines as engine_manager
import cellblender.sim_runners as runner_manager


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def get_pid(item):
    return int(item.name.split(',')[0].split(':')[1])

    # Provide a less error-prone version for testing
    #l = item.name.split(',')[0].split(':')
    #rtn_val = 0
    #if len(l) > 1:
    #  rtn_val = int(l[1])
    #return rtn_val



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
        engine_manager.write_default_data_layout(mcell_files, start, end)


        processes_list = mcell.run_simulation.processes_list
        processes_list.add()
        mcell.run_simulation.active_process_index = len(mcell.run_simulation.processes_list) - 1
        simulation_process = processes_list[mcell.run_simulation.active_process_index]

        print("Starting MCell ... create start_time.txt file:")
        with open(os.path.join(os.path.dirname(bpy.data.filepath),"start_time.txt"), "w") as start_time_file:
            start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

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
            simulation_process.name = ("PID: %d, Seed: %d" %
                                        (sp_list[0].pid, start))
        else:
            simulation_process.name = ("PID: %d-%d, Seeds: %d-%d" %
                                        (sp_list[0].pid, sp_list[-1].pid, start, end))

    mcell.run_simulation.status = status

    return {'FINISHED'}


# Simulation Operators:

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
                pid = get_pid(pl_item)
                q_item = cellblender.simulation_queue.task_dict[pid]
                if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                    return False

        elif str(mcell.run_simulation.simulation_run_control) == 'DYNAMIC':
            global active_engine_module
            global active_runner_module
            # Force an update of the pluggable items as needed (typically after starting Blender).
            if active_engine_module == None:
                mcell.sim_engines.plugs_changed_callback ( context )
            if active_runner_module == None:
                mcell.sim_runners.plugs_changed_callback ( context )

            if active_engine_module == None:
                # print ( "Cannot run without selecting a simulation engine" )
                status = "Error: No simulation engine selected"
            elif active_runner_module == None:
                # print ( "Cannot run without selecting a simulation runner" )
                status = "Error: No simulation runner selected"
            elif 'get_pid' in dir(active_runner_module):
                processes_list = mcell.run_simulation.processes_list
                for pl_item in processes_list:
                    pid = get_pid(pl_item)
                    if pid in cellblender.simulation_queue.task_dict:
                        q_item = cellblender.simulation_queue.task_dict[pid]
                        if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                            return False
        return True


    def execute(self, context):
        print ( "Call to \"execute\" for MCELL_OT_run_simulation operator" )
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
            elif str(run_sim.simulation_run_control) == 'SWEEP_SGE':
                bpy.ops.mcell.run_simulation_sweep_sge()
            elif str(run_sim.simulation_run_control) == 'DYNAMIC':
                bpy.ops.mcell.run_simulation_dynamic()
            else:
                print ( "Unexpected case in MCELL_OT_run_simulation" )
                pass

        return {'FINISHED'}



class MCELL_OT_run_simulation_control_sweep (bpy.types.Operator):
    bl_idname = "mcell.run_simulation_sweep"
    bl_label = "Run MCell Simulation Command"
    bl_description = "Run MCell Simulation Command Line"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print("Executing Sweep Runner")

        mcell = context.scene.mcell
        run_sim = mcell.run_simulation

        run_sim.last_simulation_run_time = str(time.time())

        start = int(run_sim.start_seed.get_value())
        end = int(run_sim.end_seed.get_value())
        mcell_processes_str = str(run_sim.mcell_processes)
        mcell_binary = cellblender_utils.get_mcell_path(mcell)
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (run_sim.error_list and mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                sweep_dir = os.path.join(project_dir, "output_data")
                if (os.path.exists(sweep_dir) and run_sim.remove_append == 'remove'):
                    shutil.rmtree(sweep_dir)
                if not os.path.exists(sweep_dir):
                    os.makedirs(sweep_dir)

                mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True )
                data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,"data_model.json") )

                base_name = mcell.project_settings.base_name

                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))

                # The following Python program will create the "data_layout.json" file describing the directory structure
                script_file_path = os.path.join(script_dir_path, os.path.join("mdl", "run_data_model_mcell.py") )

                processes_list = run_sim.processes_list
                processes_list.add()
                run_sim.active_process_index = len(
                    run_sim.processes_list) - 1
                simulation_process = processes_list[
                    run_sim.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started simulation at: " + (str(time.ctime())) + "\n")

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
                    simulation_process.name = ("PID: %d, Seed: %d" % (sp.pid, start))
                else:
                    simulation_process.name = ("PID: %d, Seeds: %d-%d" % (sp.pid, start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        run_sim.status = status

        return {'FINISHED'}



class MCELL_OT_run_simulation_control_sweep_sge (bpy.types.Operator):
    bl_idname = "mcell.run_simulation_sweep_sge"
    bl_label = "Run MCell Simulation Command"
    bl_description = "Run MCell Simulation Command Line"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print("Executing Grid Engine Sweep Runner")

        mcell = context.scene.mcell
        run_sim = mcell.run_simulation

        run_sim.last_simulation_run_time = str(time.time())

        start = int(run_sim.start_seed.get_value())
        end = int(run_sim.end_seed.get_value())
        mcell_processes_str = str(run_sim.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)
        
        computer_names_to_run = []
        computer_list = run_sim.computer_list
        for computer in computer_list:
            if computer.selected:
                computer_names_to_run.append ( computer.comp_name.split()[0] )
        computer_names_string = ""
        if len(computer_names_to_run) > 0:
          computer_names_string = computer_names_to_run[0]
          for n in computer_names_to_run[1:]:
            computer_names_string += ','+n

        print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
        print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
        print ( "Running on computers: " + str(computer_names_string) )
        print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
        print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (run_sim.error_list and mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                sweep_dir = os.path.join(project_dir, "output_data")
                if (os.path.exists(sweep_dir) and run_sim.remove_append == 'remove'):
                    shutil.rmtree(sweep_dir)
                if not os.path.exists(sweep_dir):
                    os.makedirs(sweep_dir)

                mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True )
                data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,"data_model.json") )

                base_name = mcell.project_settings.base_name

                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))

                # The following Python program will create the "data_layout.json" file describing the directory structure
                script_file_path = os.path.join(script_dir_path, os.path.join("mdl", "run_data_model_mcell.py") )

                processes_list = run_sim.processes_list
                processes_list.add()
                run_sim.active_process_index = len(
                    run_sim.processes_list) - 1
                simulation_process = processes_list[
                    run_sim.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started simulation at: " + (str(time.ctime())) + "\n")


                # We have to create a new subprocess that assigns jobs to nodes in the SGE
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
                cmd_list = [
                    python_path,
                    script_file_path,
                    os.path.join(project_dir,"data_model.json"),
                    "-b", mcell_binary,
                    "-fs", str(start), "-ls", str(end),
                    "-pd", project_dir,
                    "-ef", error_file_option,
                    "-lf", log_file_option,
                    "-np", mcell_processes_str,
                    "-rt", "sge",
                    "-gh", run_sim.sge_host_name,
                    "-mm", str(int(run_sim.required_memory_gig)) ]

                if run_sim.manual_sge_host:
                    cmd_list.append("-nl")
                    cmd_list.append(computer_names_string)

                if len(run_sim.sge_email_addr) > 0:
                    cmd_list.append ("-em")
                    cmd_list.append (run_sim.sge_email_addr)

                sp = subprocess.Popen(cmd_list, stdout=None, stderr=None)
                self.report({'INFO'}, "Simulation Running")

                # This is a hackish workaround since we can't return arbitrary
                # objects from operators or store arbitrary objects in collection
                # properties, and we need to keep track of the progress of the
                # subprocess objects for the panels.
                cellblender.simulation_popen_list.append(sp)

                if ((end - start) == 0):
                    simulation_process.name = ("PID: %d, Seed: %d" % (sp.pid, start))
                else:
                    simulation_process.name = ("PID: %d, Seeds: %d-%d" % (sp.pid, start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        run_sim.status = status

        return {'FINISHED'}



class MCELL_OT_run_simulation_control_normal(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_normal"
    bl_label = "Run MCell Simulation Command"
    bl_description = "Run MCell Simulation Command Line"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        run_sim = mcell.run_simulation

        run_sim.last_simulation_run_time = str(time.time())

        binary_path = mcell.cellblender_preferences.mcell_binary
        mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

        start = int(run_sim.start_seed.get_value())
        end = int(run_sim.end_seed.get_value())
        mcell_processes_str = str(run_sim.mcell_processes)
        mcell_binary = mcell.cellblender_preferences.mcell_binary
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (run_sim.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "output_data", "react_data")
                if (os.path.exists(react_dir) and
                        run_sim.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "output_data", "viz_data")
                if (os.path.exists(viz_dir) and
                        run_sim.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))
                script_file_path = os.path.join(
                    script_dir_path, "run_simulations.py")

                # The following line will create the "data_layout.json" file describing the directory structure
                engine_manager.write_default_data_layout(project_dir, start, end)

                processes_list = run_sim.processes_list
                processes_list.add()
                run_sim.active_process_index = len(
                    run_sim.processes_list) - 1
                simulation_process = processes_list[
                    run_sim.active_process_index]

                print("Starting MCell ... create start_time.txt file:")
                with open(os.path.join(os.path.dirname(bpy.data.filepath),
                          "start_time.txt"), "w") as start_time_file:
                    start_time_file.write(
                        "Started simulation at: " + (str(time.ctime())) + "\n")

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
                    simulation_process.name = ("PID: %d, Seed: %d" % (sp.pid, start))
                else:
                    simulation_process.name = ("PID: %d, Seeds: %d-%d" % (sp.pid, start, end))
        else:
            status = "Python not found. Set it in Project Settings."

        run_sim.status = status

        return {'FINISHED'}


class MCELL_OT_percentage_done_timer(bpy.types.Operator):
    """Update the MCell job list periodically to show percentage done"""
    bl_idname = "mcell.percentage_done_timer"
    bl_label = "Modal Timer Operator"
    bl_options = {'REGISTER'}

    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            task_len = len(cellblender.simulation_queue.task_dict)
            task_ctr = 0
            mcell = context.scene.mcell
            processes_list = mcell.run_simulation.processes_list
            for simulation_process in processes_list:
                if not mcell.run_simulation.save_text_logs:
                    return {'CANCELLED'}
                pid = get_pid(simulation_process)
                seed = int(simulation_process.name.split(',')[1].split(':')[1])
                q_item = cellblender.simulation_queue.task_dict[pid]
                stdout_txt = q_item['bl_text'].as_string()
                percent = 0 
                last_iter = total_iter = 0
                for i in reversed(stdout_txt.split("\n")):
                    if i.startswith("Iterations"):
                        last_iter = int(i.split()[1])
                        total_iter = int(i.split()[3])
                        percent = (last_iter/total_iter)*100
                        break
                if (last_iter == total_iter) and (total_iter != 0):
                    task_ctr += 1
                simulation_process.name = "PID: %d, Seed: %d, %d%%" % (pid, seed, percent)

            # just a silly way of forcing a screen update. ¯\_(ツ)_/¯
            color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
            color.h += 0.01
            color.h -= 0.01
            # if every MCell job is done, quit updating the screen
            if task_len == task_ctr:
                self.cancel(context)
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        # this is how often we should update this in seconds
        secs = 0.5
        self._timer = wm.event_timer_add(secs, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class MCELL_OT_run_simulation_control_queue(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_control_queue"
    bl_label = "Run MCell Simulation Using Command Queue"
    bl_description = "Run MCell Simulation Using Command Queue"
    bl_options = {'REGISTER'}

    def execute(self, context):

        mcell = context.scene.mcell
        run_sim = mcell.run_simulation

        run_sim.last_simulation_run_time = str(time.time())

        mcell_binary = cellblender_utils.get_mcell_path(mcell)

        start_seed = int(run_sim.start_seed.get_value())
        end_seed = int(run_sim.end_seed.get_value())
        mcell_processes = run_sim.mcell_processes
        mcell_processes_str = str(run_sim.mcell_processes)
        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            if not mcell.cellblender_preferences.decouple_export_run:
                bpy.ops.mcell.export_project()

            if (run_sim.error_list and
                    mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "output_data", "react_data")
                if (os.path.exists(react_dir) and
                        run_sim.remove_append == 'remove'):
                    shutil.rmtree(react_dir)
                if not os.path.exists(react_dir):
                    os.makedirs(react_dir)

                viz_dir = os.path.join(project_dir, "output_data", "viz_data")
                if (os.path.exists(viz_dir) and
                        run_sim.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir)

                base_name = mcell.project_settings.base_name

                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                cellblender.simulation_queue.python_exec = python_path
                cellblender.simulation_queue.start(mcell_processes)
                cellblender.simulation_queue.notify = True

                # The following line will create the "data_layout.json" file describing the directory structure
                engine_manager.write_default_data_layout(project_dir, start_seed, end_seed)

                processes_list = run_sim.processes_list
                for seed in range(start_seed,end_seed + 1):
                  processes_list.add()
                  run_sim.active_process_index = len(
                      run_sim.processes_list) - 1
                  simulation_process = processes_list[
                      run_sim.active_process_index]

                  print("Starting MCell ... create start_time.txt file:")
                  with open(os.path.join(os.path.dirname(bpy.data.filepath),
                            "start_time.txt"), "w") as start_time_file:
                      start_time_file.write(
                          "Started simulation at: " + (str(time.ctime())) + "\n")

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
                  make_texts = run_sim.save_text_logs
                  proc = cellblender.simulation_queue.add_task(mcell_binary, mcell_args, os.path.join(project_dir, "output_data"), make_texts)

                  self.report({'INFO'}, "Simulation Running")

                  if not simulation_process.name:
                      simulation_process.name = ("PID: %d, Seed: %d" % (proc.pid, seed))
                  bpy.ops.mcell.percentage_done_timer()

        else:
            status = "Python not found. Set it in Project Settings."

        run_sim.status = status

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
        pid = get_pid(ap)
        # pid = int(ap.name.split(',')[0].split(':')[1])
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
            pid = get_pid(p_item)
            q_item = cellblender.simulation_queue.task_dict.get(pid)
            if q_item:
                if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                    # Simulation is running or waiting in queue, so let's kill it
                    cellblender.simulation_queue.kill_task(pid)

        return {'FINISHED'}








class MCELL_OT_run_simulation_dynamic(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_dynamic"
    bl_label = "Run Simulation via Dynamic Engine/Runner"
    bl_description = "Run Simulation via Dynamic Engine/Runner"
    bl_options = {'REGISTER'}


    def execute(self, context):

        print ( "Top of execute" )

        global active_engine_module
        global active_runner_module

        mcell = context.scene.mcell

        status = ""

        print ( "Update Pluggables" )

        # Force an update of the pluggable items as needed (typically after starting Blender).
        if active_engine_module == None:
            mcell.sim_engines.plugs_changed_callback ( context )
        if active_runner_module == None:
            mcell.sim_runners.plugs_changed_callback ( context )


        print ( "Check for engine/runner capabilities" )

        if active_engine_module == None:
            # print ( "Cannot run without selecting a simulation engine" )
            status = "Error: No simulation engine selected"
        elif active_runner_module == None:
            # print ( "Cannot run without selecting a simulation runner" )
            status = "Error: No simulation runner selected"

        elif not ( ( 'prepare_runs_no_data_model' in dir(active_engine_module) )
                or ( 'prepare_runs_data_model_no_geom' in dir(active_engine_module) )
                or ( 'prepare_runs_data_model_full' in dir(active_engine_module) ) ):
            print ( "Selected engine module does not contain a \"prepare_runs...\" function" )
            # status = "Error: function \"prepare_runs...\" not found in selected engine"

        if len(status) == 0:
            print ( "Update start time" )

            with open(os.path.join(os.path.dirname(bpy.data.filepath), "start_time.txt"), "w") as start_time_file:
                start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

            mcell.run_simulation.last_simulation_run_time = str(time.time())

            start = int(mcell.run_simulation.start_seed.get_value())
            end = int(mcell.run_simulation.end_seed.get_value())

            project_dir = mcell_files_path()

            print ( "Remove old reaction data and make new directories" )
            react_dir = os.path.join(project_dir, "output_data", "react_data")
            if os.path.exists(react_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(react_dir)
            if not os.path.exists(react_dir):
                os.makedirs(react_dir)

            print ( "Remove old viz data and make new directories" )
            viz_dir = os.path.join(project_dir, "output_data", "viz_data")
            if os.path.exists(viz_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)

            # The following line will create the "data_layout.json" file describing the directory structure
            # It would probably be better for the actual engine to do this, but put it here for now...
            print ( "Write the default data layout" )
            engine_manager.write_default_data_layout(project_dir, start, end)

            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(script_dir_path, "sim_engines")

            if ('engine' in dir(active_engine_module)) and ('runner' in dir(active_runner_module)):
                # This is the new engine/runner object case
                print ( "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" )
                print ( "OO  Object-Oriented Engine/Runner combination found  OO" )
                print ( "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" )

                engine_object = active_engine_module.engine(active_engine_module)
                runner_object = active_runner_module.runner(active_runner_module, engine_object)
                status = "Engine and Runner have been constructed"

                # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

                command_list = None
                dm = None
                print ( "Calling prepare_runs... in engine class" )
                if 'prepare_runs_no_data_model' in dir(engine_object):
                    command_list = engine_object.prepare_runs_no_data_model ( project_dir )
                elif 'prepare_runs_data_model_no_geom' in dir(engine_object):
                    dm = mcell.build_data_model_from_properties ( context, geometry=False )
                    command_list = engine_object.prepare_runs_data_model_no_geom ( dm, project_dir )
                elif 'prepare_runs_data_model_full' in dir(engine_object):
                    dm = mcell.build_data_model_from_properties ( context, geometry=True )
                    command_list = engine_object.prepare_runs_data_model_full ( dm, project_dir )
                
                if "run_commands" in dir(runner_object):
                    runner_object.run_commands ( command_list )
                elif "run_simulations" in dir(engine_object):
                    print ( "Calling run_simulations in engine_object" )
                    engine_object.run_simulations ( command_list )
                elif "run_simulation" in dir(engine_object):
                    print ( "Calling run_simulation in engine object" )
                    engine_object.run_simulation ( dm, project_dir )

                global global_task_dict
                global global_task_id

                global_task_dict[global_task_id] = runner_object

                new_job = mcell.sim_runners.job_index_list.add()
                new_job.job_index = global_task_id
                mcell.sim_runners.active_job_index = len(mcell.sim_runners.job_index_list) - 1

                global_task_id += 1

            elif "run_engine" in dir(active_runner_module):
                print ( "Selected Runner supports running the engine directly ... so pass the engine." )
                dm = mcell.build_data_model_from_properties ( context, geometry=True )
                active_runner_module.run_engine ( active_engine_module, dm, project_dir )

            else:
                print ( "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" )
                print ( "XX  Object-Oriented Engine/Runner combination NOT found  XX" )
                print ( "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" )

                command_list = None
                dm = None
                print ( "Calling prepare_runs... in active_engine_module" )
                if 'prepare_runs_no_data_model' in dir(active_engine_module):
                    command_list = active_engine_module.prepare_runs_no_data_model ( project_dir )
                elif 'prepare_runs_data_model_no_geom' in dir(active_engine_module):
                    dm = mcell.build_data_model_from_properties ( context, geometry=False )
                    command_list = active_engine_module.prepare_runs_data_model_no_geom ( dm, project_dir )
                elif 'prepare_runs_data_model_full' in dir(active_engine_module):
                    dm = mcell.build_data_model_from_properties ( context, geometry=True )
                    command_list = active_engine_module.prepare_runs_data_model_full ( dm, project_dir )
                
                if "run_commands" in dir(active_runner_module):
                    active_runner_module.run_commands ( command_list )

                elif "run_simulations" in dir(active_engine_module):
                    print ( "Calling run_simulations in active_engine_module" )
                    active_engine_module.run_simulations ( command_list )

                elif "run_simulation" in dir(active_engine_module):
                    print ( "Calling run_simulation in active_engine_module" )
                    active_engine_module.run_simulation ( dm, project_dir )

        mcell.run_simulation.status = status

        return {'FINISHED'}



class sge_interface:

    def read_a_line ( self, process_output, wait_count, sleep_time ):
        count = 0
        while (len(process_output.peek()) > 0) and (count < wait_count):
            # Keep checking for a full line
            if b'\n' in process_output.peek():
                line = str(process_output.readline())
                if line != None:
                    return line
            else:
                # Not a full line yet, so kill some time
                time.sleep ( sleep_time )
            count = count + 1
        # Try to read the line anyway ... this seems to be needed in some cases
        line = str(process_output.readline())
        if line != None:
            return line
        return None


    def wait_for_anything (self, pipe_in, sleep_time, max_count):
        count = 0
        while len(pipe_in.peek()) == 0:
            # Wait for something
            time.sleep ( sleep_time )
            count = count + 1
            if count > max_count:
                # That's enough waiting
                break

    def wait_for_line_start (self, pipe_in, line_start, max_wait_count, line_wait_count, line_sleep_time):
        num_wait = 0
        while True:
            line = self.read_a_line ( pipe_in, 100, 0.001 )
            num_wait += 1
            if num_wait > 1000:
                break
            if line == None:
                break
            if line.startswith("b'----------"):
                break

    def kill_all_users_jobs (self, host_name, user_name):
        num_wait = 0

        args = ['ssh', host_name, 'qdel', '-u', user_name]

        p = subprocess.Popen ( args, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        pi = p.stdin
        po = p.stdout
        pe = p.stderr

        # Read lines until done

        num_wait = 0
        while True:
            line = self.read_a_line ( po, 100, 0.001 )
            if line == None:
                break
            elif len(line.strip()) == 0:
                break
            elif str(line) == "b''":
                break
            else:
                num_wait = 0
                print ( line )
            num_wait += 1
            if num_wait > 1000:
                print ( "Submit Host " + run_sim.sge_host_name + " seems unresponsive. List may not be complete." )
                break
        p.kill()


    def get_hosts_information (self, host_name):
        # Build generic Python structures to use for filling Blender properties later
        name_list = []
        comp_dict = {}


        # First pass - Use qhost to build the basic structure (additional passes will add to it)
        args = ['ssh', host_name, 'qhost']

        p = subprocess.Popen ( args, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        pi = p.stdin
        po = p.stdout
        pe = p.stderr

        # Start by waiting for any kind of response

        self.wait_for_anything (po, 0.01, 100)

        # Read lines until the header line has been found

        self.wait_for_line_start (po, "b'----------", 1000, 100, 0.001)

        # Read lines until done

        num_wait = 0
        while True:
            line = self.read_a_line ( po, 100, 0.001 )
            if line == None:
                break
            elif len(line.strip()) == 0:
                break
            elif str(line) == "b''":
                break
            else:
                num_wait = 0
                print ( " Pass 1 SGE: " + str(line) )
                try:
                    comp = {}
                    fields = line[2:len(line)-3].split()
                    comp['comp_props'] = ','.join(fields[1:])
                    comp['name']  = fields[0].strip()
                    comp['mem']   = fields[4].strip()
                    comp['cores_in_use'] = 0
                    comp['cores_total'] = 0
                    name_list.append ( comp['name'] )
                    comp_dict[comp['name']] = comp
                except Exception as err:
                    # This line didn't contain proper fields, so don't add it to the list
                    print ( "This line didn't contain proper fields, so don't add it to the list" + line )
                    pass
            num_wait += 1
            if num_wait > 1000:
                print ( "Submit Host " + run_sim.sge_host_name + " seems unresponsive. List may not be complete." )
                break
        p.kill()


        # Second pass - Use qhost -q to add the number of cores in use and available
        args = ['ssh', host_name, 'qhost', '-q']

        p = subprocess.Popen ( args, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

        pi = p.stdin
        po = p.stdout
        pe = p.stderr

        # Start by waiting for any kind of response

        self.wait_for_anything (po, 0.01, 100)

        # Read lines until the header line has been found

        self.wait_for_line_start (po, "b'----------", 1000, 100, 0.001)

        # Read lines until done

        num_wait = 0
        most_recent_host = "";
        while True:
            line = self.read_a_line ( po, 100, 0.001 )
            if line == None:
                most_recent_host = "";
                break
            elif len(line.strip()) == 0:
                most_recent_host = "";
                break
            elif str(line) == "b''":
                most_recent_host = "";
                break
            else:
                num_wait = 0
                print ( " Pass 2 SGE: " + str(line) )
                try:
                    fields = line[2:len(line)-3].split()
                    if fields[0].strip() in comp_dict:
                        # The returned name matches a known host, so store the name in preparation for a subsequent line
                        most_recent_host = fields[0].strip()
                    else:
                        if len(most_recent_host) > 0:
                            # The previous line should have been a valid host, and this line should contain: queue BIPC cores_in_use/cores_available
                            if fields[1].strip() == "BIPC":
                                core_info = [ int(f.strip()) for f in fields[2].strip().split('/') ]
                                comp = comp_dict[most_recent_host]
                                comp['cores_in_use'] = core_info[0]
                                comp['cores_total'] = core_info[1]
                                print ( "Cores for " + most_recent_host + " " + core_info[0] + "/" + core_info[1] )
                except Exception as err:
                    most_recent_host = "";
                    # This line didn't contain proper fields, so don't add it to the list
                    print ( "This line didn't contain proper fields, so don't add it to the list" + line )
                    pass
            num_wait += 1
            if num_wait > 1000:
                print ( "Submit Host " + run_sim.sge_host_name + " seems unresponsive. List may not be complete." )
                break
        p.kill()
        return ( name_list, comp_dict )



class MCELL_OT_refresh_sge_list(bpy.types.Operator):
    bl_idname = "mcell.refresh_sge_list"
    bl_label = "Refresh the Execution Host list"
    bl_description = ("Refresh the list of execution hosts in the Sun Grid Engine list.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Refreshing the SGE execution host list" )
        run_sim = context.scene.mcell.run_simulation
        if len(run_sim.sge_host_name) <= 0:
            print ( "Error: SGE Submit Host name is empty" )
        else:
            run_sim.computer_list.clear()
            run_sim.active_comp_index = 0

            # Get the host information as a name list and a dictionary of capabilities for each computer

            sge = sge_interface()
            ( name_list, comp_dict ) = sge.get_hosts_information ( run_sim.sge_host_name )

            # Build the Blender properties from the list

            for name in name_list:
                if comp_dict[name]['mem'] != '-':   # Filter out the "global" node which has "-" for all fields
                    print ( "Adding to computer_list: " + name )
                    run_sim.computer_list.add()
                    run_sim.active_comp_index = len(run_sim.computer_list) - 1
                    new_comp = run_sim.computer_list[run_sim.active_comp_index]
                    new_comp.comp_name = comp_dict[name]['name']
                    new_comp.comp_props = comp_dict[name]['comp_props']
                    new_comp.cores_in_use = comp_dict[name]['cores_in_use']
                    new_comp.cores_total = comp_dict[name]['cores_total']
                    try:
                        # Parse the memory specification (#M,#G,#T)
                        new_comp.comp_mem = float(comp_dict[name]['mem'][:-1])
                        if comp_dict[name]['mem'][-1] == 'G':
                            # No change ... report everything in G for CellBlender interface
                            pass
                        elif comp_dict[name]['mem'][-1] == 'M':
                            new_comp.comp_mem *= 1.0/1024
                        elif comp_dict[name]['mem'][-1] == 'T':
                            new_comp.comp_mem *= 1024
                        elif comp_dict[name]['mem'][-1] == 'P':
                            new_comp.comp_mem *= 1024 * 1024
                        elif comp_dict[name]['mem'][-1] == 'E':
                            new_comp.comp_mem *= 1024 * 1024 * 1024
                        elif comp_dict[name]['mem'][-1] == 'K':
                            new_comp.comp_mem *= 1.0/(1024 * 1024)
                        else:
                            print ( "Unidentified memory units used in: \"" + comp_dict[name]['mem'] + "\"" )
                            new_comp.comp_mem = 0
                    except Exception as err:
                        print ( "Exception translating memory specification: \"" +  comp_dict[name]['mem'] + "\", exception = " + str(err) )
                        pass

            run_sim.active_comp_index = 0

        return {'FINISHED'}


class MCELL_OT_select_all_computers(bpy.types.Operator):
    bl_idname = "mcell.select_all_computers"
    bl_label = "Select All"
    bl_description = ("Select all computers.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        run_sim = context.scene.mcell.run_simulation
        computer_list = run_sim.computer_list
        for computer in computer_list:
            computer.selected = True
        return {'FINISHED'}

class MCELL_OT_deselect_all_computers(bpy.types.Operator):
    bl_idname = "mcell.deselect_all_computers"
    bl_label = "Select None"
    bl_description = ("Select no computers.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        run_sim = context.scene.mcell.run_simulation
        computer_list = run_sim.computer_list
        for computer in computer_list:
            computer.selected = False
        return {'FINISHED'}


class MCELL_OT_kill_all_users_jobs(bpy.types.Operator):
    bl_idname = "mcell.kill_all_users_jobs"
    bl_label = "Terminate All"
    bl_description = ("Kill all jobs run by the current user name.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        run_sim = context.scene.mcell.run_simulation
        sge = sge_interface()
        sge.kill_all_users_jobs ( run_sim.sge_host_name, os.getlogin() );
        return {'FINISHED'}


class MCELL_OT_select_with_required(bpy.types.Operator):
    bl_idname = "mcell.select_with_required"
    bl_label = "Select"
    bl_description = ("Select computers meeting requirements.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Selecting" )
        run_sim = context.scene.mcell.run_simulation
        computer_list = run_sim.computer_list
        for computer in computer_list:
            #print ( "Computer " + str(computer.comp_name.split()[0]) + " selection = " + str(computer.selected) )
            #print ( "Is \"" + str(computer.comp_mem) + "\" > " + str(run_sim.required_memory_gig) + " ?" )
            if (computer.comp_mem >= run_sim.required_memory_gig) and ((computer.cores_total - computer.cores_in_use) >= run_sim.required_free_slots):
                print ( "  Selected to run on " + str(computer.comp_name) )
                computer.selected = True
            else:
                computer.selected = False
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
                bpy.data.texts.remove ( bpy.data.texts[k], do_unlink=True )
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
            pid = get_pid(processes_list[idx])
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
            pid = get_pid(item)
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


class MCellComputerProperty(bpy.types.PropertyGroup):
    comp_name = StringProperty ( default="", description="Computer name" )
    comp_mem = FloatProperty ( default=0, description="Total Memory" )
    cores_in_use = IntProperty ( default=0, description="Cores in use" )
    cores_total = IntProperty ( default=0, description="Cores total" )
    comp_props = StringProperty ( default="", description="Computer properties" )
    selected = BoolProperty ( default=False, description="Select for running" )

class MCell_UL_computer_item ( bpy.types.UIList ):
    def draw_item (self, context, layout, data, item, icon, active_data, active_propname, index):
      col = layout.column()
      col.label ( item.comp_name + "  " + str(int(item.comp_mem)) + "G " + str(item.cores_in_use) + "/" + str(item.cores_total) )
      col = layout.column()
      if item.selected:
          col.prop ( item, "selected", text="", icon="POSE_DATA" )
      else:
          col.prop ( item, "selected", text="" )


global_task_dict = {}
global_task_id = 1


class DYNAMIC_UL_runner(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # data is a Pluggable
        # item is a JobIndexProperty
        # active_data is a Pluggable
        # active_propname is the string key ("active_job_index")
        # index is an integer index into the selected item in the list
        global global_task_dict
        global global_task_id
        s = "Job Index: " + str(item.job_index)
        if item.job_index in global_task_dict:
            job = global_task_dict[item.job_index]
            # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
            if 'get_status_string' in dir(job):
                s = s + " " + job.get_status_string()
            else:
                s = s + " No get_status_string function found"
        layout.label(s, icon='FILE_TICK')
        # def get_status_string ( self ):


class MCellRunSimulationPropertyGroup(bpy.types.PropertyGroup):
    enable_python_scripting = BoolProperty ( name='Enable Python Scripting', default=False )  # Intentionally not in the data model
    sge_host_name = StringProperty ( default="", description="Name of Grid Engine Scheduler" )
    sge_email_addr = StringProperty ( default="", description="Email address for notifications" )
    computer_list = CollectionProperty(type=MCellComputerProperty, name="Computer List")
    required_memory_gig = FloatProperty(default=2.0, description="Minimum memory per job - used for selecting hosts")
    required_free_slots = IntProperty(default=1, description="Minimum free slots for selecting hosts")
    active_comp_index = IntProperty(name="Active Computer Index", default=0)

    start_seed = PointerProperty ( name="Start Seed", type=parameter_system.Parameter_Reference )
    end_seed   = PointerProperty ( name="End Seed", type=parameter_system.Parameter_Reference )
    run_limit  = PointerProperty ( name="Run Limit", type=parameter_system.Parameter_Reference )
    mcell_processes = IntProperty(
        name="Number of Processes",
        default=cpu_count(),
        min=1,
        max=cpu_count(),
        description="Number of simultaneous simulation processes")
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

    save_text_logs = BoolProperty ( name='Save Text Logs', default=True, description="Create a text log for each run" )

    # This would be better as a double, but Blender would store as a float which doesn't have enough precision to resolve time in seconds from the epoch.
    last_simulation_run_time = StringProperty ( default="-1.0", description="Time that the simulation was last run" )

    simulation_engine_and_run_enum = [
         ('QUEUE', "MCell via Queue Runner", ""),
         ('COMMAND', "MCell via Command Line", ""),
         ('SWEEP', "MCell via Sweep Runner", ""),
         ('SWEEP_SGE', "MCell via Sweep Runner and SGE", ""),
         ('DYNAMIC', "Engine/Runner", "") ]

    simulation_run_control = EnumProperty(
        items=simulation_engine_and_run_enum, name="",
        description="Mechanism for running and controlling a specific simulation",
        # default='QUEUE', # Cannot set a default when "items" is a function
        update=sim_runner_changed_callback)

    show_sge_control_panel = BoolProperty ( name="Host Selection Details", default=False, description="Show or hide the Grid Engine host selection controls" )
    manual_sge_host = BoolProperty ( name="Select execution hosts manually", default=False, description="Select execution hosts from a capabilities list" )

    def init_properties ( self, parameter_system ):
        helptext = "The first seed used in running a series of simulations.\n" \
                   "The number of simulations depends on the start and end seeds."
        self.start_seed.init_ref   ( parameter_system, user_name="Start Seed",   user_expr="1", user_units="", user_descr=helptext )

        helptext = "The last seed used in running a series of simulations.\n" \
                   "The number of simulations depends on the start and end seeds."
        self.end_seed.init_ref   ( parameter_system, user_name="End Seed",   user_expr="1", user_units="", user_descr=helptext )

        helptext = "Maximum number of simulation runs that can be submitted.\n" \
                   "This setting provides a safeguard against running more runs than expected.\n" \
                   "A value of -1 implies no limit.  The default for upgraded files is -1 since they\n" \
                   "had no limit."
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
        dm['data_model_version'] = "DM_2017_08_10_1657"
        dm['name'] = self.name
        dm['start_seed'] = self.start_seed.get_expr()
        dm['end_seed'] = self.end_seed.get_expr()
        dm['run_limit'] = self.run_limit.get_expr()
        p_list = []
        for p in self.processes_list:
            p_list.append ( p.build_data_model_from_properties(context) )
        dm['processes_list'] = p_list

        print ( "Save Engines and Runners in Data Model" )

        sim_engine_list = []
        if engine_manager.plug_modules != None:
            print ( "Engine Plugs to save" )
            for plug in engine_manager.plug_modules:
                print ( "Saving Engine Plug " + str(plug.plug_code) )
                plug_dm = {}
                plug_dm['plug_code'] = plug.plug_code
                plug_dm['plug_name'] = plug.plug_name

                plug_dm['plug_active'] = True
                if "plug_active" in dir(plug):
                    plug_dm['plug_active'] = plug.plug_active

                plug_dm['parameter_dictionary'] = {}
                if "parameter_dictionary" in dir(plug):
                    plug_par_dict = plug.parameter_dictionary
                    # Copy only non-functions
                    for k in plug_par_dict.keys():
                        copy_par = True
                        if 'val' in plug_par_dict[k].keys():
                            if type(plug_par_dict[k]['val']) == type(plugs_changed_callback):
                                copy_par = False
                        if copy_par:
                            plug_dm['parameter_dictionary'][k] = plug_par_dict[k]

                plug_dm['parameter_layout'] = []
                if "parameter_layout" in dir(plug):
                    plug_dm['parameter_layout'] = plug.parameter_layout

                sim_engine_list.append ( plug_dm )

        dm['sim_engines'] = sim_engine_list

        if runner_manager.plug_modules != None:
            print ( "Runner Plugs to save" )
            #runner_manager.plug_modules = runner_manager.get_modules()

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

        if dm['data_model_version'] == "DM_2016_10_27_1642":
            # Add Engines and Runners lists if they don't exist
            if not 'sim_engines' in dm.keys():
                dm['sim_engines'] = []
            if not 'sim_runners' in dm.keys():
                dm['sim_runners'] = []
            dm['data_model_version'] = "DM_2017_08_10_1657"

        if dm['data_model_version'] != "DM_2017_08_10_1657":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )
            return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2017_08_10_1657":
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


        # Force a reading of currently installed modules as needed

        if engine_manager.plug_modules == None:
            engine_manager.plug_modules = engine_manager.get_modules()
        if runner_manager.plug_modules == None:
            runner_manager.plug_modules = runner_manager.get_modules()

        # Only restore the engines and runners that are currently installed

        if engine_manager.plug_modules != None:
            print ( "Restoring Engine Plugs" )
            for plug in engine_manager.plug_modules:
                print ( "Looking for saved data for plug " + str(plug.plug_code) )
                for plug_dm in dm['sim_engines']:
                    if plug_dm['plug_code'] == plug.plug_code:
                        print ( "Found data for Engine Plug " + str(plug.plug_code) )

                        plug.plug_active = True
                        if "plug_active" in plug_dm:
                            plug.plug_active = plug_dm['plug_active']

                        if "parameter_dictionary" in plug_dm:
                            # Copy all entries except those that are functions.
                            # Note that it might be good to do this recursively,
                            #   but all functions are currently at the top level.
                            pars_dict = plug_dm['parameter_dictionary']
                            for k in pars_dict.keys():
                                par = pars_dict[k]
                                copy_par = True
                                if 'val' in par.keys():
                                    if type(par['val']) == type(plugs_changed_callback):
                                        copy_par = False
                                if copy_par:
                                    plug.parameter_dictionary[k] = pars_dict[k]

                        if "parameter_layout" in plug_dm:
                            plug.parameter_layout = plug_dm['parameter_layout']

        if runner_manager.plug_modules != None:
            print ( "Runner Plugs to save" )
            #runner_manager.plug_modules = runner_manager.get_modules()



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

            # This is now handled in the Engine panel
            #
            #global global_scripting_enabled_once
            #
            #if global_scripting_enabled_once:
            #
            #    helptext = "Allow Running of Python Code in Scripting Panel\n" + \
            #               " \n" + \
            #               "The Scripting Interface can run Python code contained\n" + \
            #               "in text files (text blocks) within Blender.\n" + \
            #               "\n" + \
            #               "Running scripts from unknown sources is a security risk.\n" + \
            #               "Only enable this option if you are confident that all of\n" + \
            #               "the scripts contained in this .blend file are safe to run."
            #    ps.draw_prop_with_help ( layout, "Enable Python Scripting", self,
            #               "enable_python_scripting", "python_scripting_show_help",
            #               self.python_scripting_show_help, helptext )

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
            elif (not os.path.isfile(main_mdl) and mcell.cellblender_preferences.decouple_export_run):
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

                display_queue_panel = False

                global active_engine_module
                global active_runner_module
                if self.simulation_run_control == "QUEUE":
                    display_queue_panel = True
                elif self.simulation_run_control == 'DYNAMIC':
                    if active_engine_module == None:
                        pass
                    elif active_runner_module == None:
                        pass
                    elif 'get_pid' in dir(active_runner_module):
                        display_queue_panel = True

                if display_queue_panel:
                    # print ( "Drawing the Queue Panel" )

                    if (self.processes_list and cellblender.simulation_queue.task_dict):
                        row = layout.row()
                        row.label(text="Simulation Processes:", icon='FORCE_LENNARDJONES')
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
                            pid = get_pid(processes_list[active_process_index])
                            q_item = cellblender.simulation_queue.task_dict[pid]

                            if q_item['stderr'] != b'':
                                serr = str(q_item['stderr'])
                                if len(serr) > 0:
                                    row = layout.row()
                                    row.label ( "Error from task " + str(pid), icon="ERROR" )

                                    tool_shelf = cellblender_utils.get_tool_shelf()
                                    lines = cellblender_utils.wrap_long_text(math.ceil(tool_shelf.width / 9), serr)

                                    for var in lines:
                                      row = layout.row(align = True)
                                      row.alignment = 'EXPAND'
                                      row.label(var)

                            sout = str(q_item['stdout'])
                            if False and (len(sout) > 0):
                                row = layout.row()
                                row.label ( "Out: " + sout )


                        row = layout.row()
                        row.operator("mcell.clear_simulation_queue")
                        row = layout.row()
                        row.operator("mcell.kill_simulation")
                        row.operator("mcell.kill_all_simulations")

                else:

                    if self.processes_list and (len(self.processes_list) > 0):
                        row = layout.row()
                        row.template_list("MCELL_UL_run_simulation", "run_simulation",
                                          self, "processes_list",
                                          self, "active_process_index",
                                          rows=2)
                        row = layout.row()
                        row.operator("mcell.clear_run_list")


                if self.simulation_run_control == 'DYNAMIC':
                    row = layout.row()
                    if ('engine' in dir(active_engine_module)) and ('runner' in dir(active_runner_module)):

                        row.label ( "============ Dynamic job list ============" )
                        row = layout.row()
                        col = row.column()
                        col.template_list("DYNAMIC_UL_runner", "runner",
                                          mcell.sim_runners, "job_index_list",
                                          mcell.sim_runners, "active_job_index",
                                          rows=4)
                        col = row.column(align=False)
                        subcol = col.column(align=True)
                        #subcol.operator("pluggable.clear_this_job", icon='ZOOMOUT', text="")
                        #subcol.operator("pluggable.clear_all_jobs", icon='X_VEC', text="")
                        subcol.label(icon='ZOOMOUT', text="")
                        subcol.label(icon='X_VEC', text="")


                        row = layout.row()
                        row.label ( "============ Dynamic job list ============" )

                    mcell.sim_engines.draw_panel ( context, layout )
                    mcell.sim_runners.draw_panel ( context, layout )


                box = layout.box()

                if self.show_output_options:
                    row = box.row()
                    row.alignment = 'LEFT'
                    col = row.column()
                    col.prop(self, "show_output_options", icon='TRIA_DOWN',
                             text="Output / Control Options", emboss=False)
                    col = row.column()
                    col.prop ( self, "simulation_run_control" )


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
                    # Comment out with this selector moved to the top:
                    #col = row.column()
                    #col.prop(self, "simulation_run_control")
                    
                    # This will eventually show the panel for the selected runner

                    if display_queue_panel:
                        row = box.row()
                        row.prop ( self, "save_text_logs" )
                        row.operator("mcell.remove_text_logs")

                    if self.simulation_run_control == "SWEEP_SGE":
                        row = box.row()
                        subbox = row.box()
                        row = subbox.row()
                        col = row.column()
                        col.prop ( self, "sge_host_name", text="Submit Host" )
                        col = row.column()
                        col.prop ( self, "sge_email_addr", text="Email" )

                        row = subbox.row()
                        row.alignment = 'LEFT'
                        if not self.show_sge_control_panel:
                            col = row.column()
                            col.alignment = 'LEFT'
                            col.prop ( self, "show_sge_control_panel", icon='TRIA_RIGHT', emboss=False )
                            col = row.column()
                            col.prop ( self, "manual_sge_host" )

                        else:
                            col = row.column()
                            col.alignment = 'LEFT'
                            col.prop ( self, "show_sge_control_panel", icon='TRIA_DOWN', emboss=False )
                            col = row.column()
                            col.prop ( self, "manual_sge_host" )

                            if not self.manual_sge_host:
                                row = subbox.row()
                                col = row.column()
                                col.prop ( self, "required_memory_gig", text="Memory(G)" )
                                col = row.column()
                                col.operator ( "mcell.kill_all_users_jobs" )
                            else:
                                row = subbox.row()
                                col = row.column()
                                col.operator( "mcell.refresh_sge_list", icon='FILE_REFRESH' )
                                row = subbox.row()
                                row.template_list("MCell_UL_computer_item", "computer_item",
                                                  self, "computer_list", self, "active_comp_index", rows=4 )
                                row = subbox.row()
                                col = row.column()
                                col.prop ( self, "required_memory_gig", text="Memory(G)" )
                                col = row.column()
                                col.prop ( self, "required_free_slots", text="Free Slots" )
                                col = row.column()
                                col.operator( "mcell.select_with_required" )

                                row = subbox.row()
                                col = row.column()
                                col.operator ( "mcell.select_all_computers" )
                                col = row.column()
                                col.operator ( "mcell.deselect_all_computers" )
                                col = row.column()
                                col.operator ( "mcell.kill_all_users_jobs" )
                else:
                    row = box.row()
                    row.alignment = 'LEFT'
                    col = row.column()
                    col.prop(self, "show_output_options", icon='TRIA_RIGHT',
                             text="Output / Control Options", emboss=False)
                    col = row.column()
                    col.prop ( self, "simulation_run_control" )
                
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



###########################################################################
###########################################################################
###########################################################################
######                                                               ######
######    Code taken directly from the Pluggable __init__.py file    ######
######                                                               ######
###########################################################################
###########################################################################
###########################################################################


#import os
#import cellblender.sim_engines as engine_manager
#import cellblender.sim_runners as runner_manager

# module_type_dict = { "sim_engines": engine_manager, "sim_runners": runner_manager }

active_engine_module = None
active_runner_module = None

# This dictionary maps process ids (pids) into the active_engine_module used to start that process.
# This dictionary can be used to call functions from the module based on the PID.
engine_module_dict = {}


def load_plug_modules(context):
    # print ( "Call to load_plug_modules" )
    if engine_manager.plug_modules == None:
        engine_manager.plug_modules = engine_manager.get_modules()
    if runner_manager.plug_modules == None:
        runner_manager.plug_modules = runner_manager.get_modules()

def get_engines_as_items(scene, context):
    load_plug_modules(context)
    # Start with any static modules that should always be in the list
    plugs_list = [("NONE", "Choose Engine", "")]
    # Add the dynamic modules
    for plug in engine_manager.plug_modules:
        plug_active = True
        if "plug_active" in dir(plug):
            plug_active = plug.plug_active
        if plug_active:
            plugs_list.append ( (plug.plug_code, plug.plug_name, "") )
    return plugs_list

def get_runners_as_items(scene, context):
    load_plug_modules(context)
    # Start with any static modules that should always be in the list
    plugs_list = [("NONE", "Choose Runner", "")]
    # Add the dynamic modules
    for plug in runner_manager.plug_modules:
        plug_active = True
        if "plug_active" in dir(plug):
            plug_active = plug.plug_active
        if plug_active:
            plugs_list.append ( (plug.plug_code, plug.plug_name, "") )
    return plugs_list



class PLUGGABLE_OT_Reload(bpy.types.Operator):
  bl_idname = "pluggable.reload"
  bl_label = "Reload"

  def execute(self, context):
    print ( "pluggable.reload.execute()" )
    engine_manager.plug_modules = None
    runner_manager.plug_modules = None
    context.scene.mcell.sim_engines.plugs_changed_callback ( context )
    context.scene.mcell.sim_runners.plugs_changed_callback ( context )
    return{'FINISHED'}


class PLUGGABLE_OT_Print(bpy.types.Operator):
  bl_idname = "pluggable.print"
  bl_label = "Print"

  def execute(self, context):
    print ( "pluggable.print.execute()" )
    """
    global active_plug_module
    ###???### pluggable = context.scene.Pluggable
    if active_plug_module == None:
      print ( "No active plug in module" )
    else:
      # Add items to the lists
      if 'print_parameters' in dir(active_plug_module):
        print ( "Calling print in active_plug_module" )
        active_plug_module.print_parameters()
      else:
        print ( "This module does not support printing" )
    """
    return{'FINISHED'}

class PLUGGABLE_OT_Run(bpy.types.Operator):
  bl_idname = "pluggable.run"
  bl_label = "Run"

  def execute(self, context):
    print ( "pluggable.run.execute()" )
    return{'FINISHED'}


class PLUGGABLE_OT_Interact(bpy.types.Operator):
  bl_idname = "pluggable.interact"
  bl_label = "Interact"

  def execute(self, context):
    print ( "pluggable.interact.execute()" )
    __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    return{'FINISHED'}



class PLUGGABLE_OT_User(bpy.types.Operator):
  bl_idname = "pluggable.user_function"
  bl_label = "User"
  user_function_name = StringProperty ( default="", description="Name of function to call for this button" )

  def execute(self, context):
    global active_engine_module
    global active_runner_module
    # print ( "pluggable.user_function.execute() will run function " + str(self.user_function_name) )
    if '\t' in self.user_function_name:
      modname,plugname = self.user_function_name.split('\t')
      pluggable = None
      if modname == 'engines':
        if active_engine_module == None:
          print ( "No active engine in module" )
        else:
          if 'parameter_dictionary' in dir(active_engine_module):
            #print ( "Calling " + str(plugname) )
            active_engine_module.parameter_dictionary[str(plugname)]['val']()
            # Call plugs_changed_callback to force a reloading of properties from the parameter_dictionary
            context.scene.mcell.sim_engines.plugs_changed_callback ( context )
          else:
            print ( "This module does not support a function named " + str(self.user_function_name) )
      if modname == 'runners':
        if active_runner_module == None:
          print ( "No active runner in module" )
        else:
          if 'parameter_dictionary' in dir(active_runner_module):
            #print ( "Calling " + str(plugname) )
            active_runner_module.parameter_dictionary[str(plugname)]['val']()
            # Call plugs_changed_callback to force a reloading of properties from the parameter_dictionary
            context.scene.mcell.sim_runners.plugs_changed_callback ( context )
          else:
            print ( "This module does not support a function named " + str(self.plugname) )
    else:
      print ( "This module does not support a function named " + str(self.user_function_name) )
    return{'FINISHED'}



def plug_int_set_callback ( self, value ):
    self.plug_int_set_callback ( value )
def plug_int_get_callback ( self ):
    return self.plug_int_get_callback()
def plug_int_update_callback ( self, context ):
    self.plug_int_update_callback(context)


def plug_float_set_callback ( self, value ):
    self.plug_float_set_callback ( value )
def plug_float_get_callback ( self ):
    return self.plug_float_get_callback()
def plug_float_update_callback ( self, context ):
    self.plug_float_update_callback(context)


def plug_bool_set_callback ( self, value ):
    self.plug_bool_set_callback ( value )
def plug_bool_get_callback ( self ):
    return self.plug_bool_get_callback()
def plug_bool_update_callback ( self, context ):
    self.plug_bool_update_callback(context)


def plug_string_set_callback ( self, value ):
    self.plug_string_set_callback ( value )
def plug_string_get_callback ( self ):
    return self.plug_string_get_callback()
def plug_string_update_callback ( self, context ):
    self.plug_string_update_callback(context)


def plug_filename_set_callback ( self, value ):
    self.plug_filename_set_callback ( value )
def plug_filename_get_callback ( self ):
    return self.plug_filename_get_callback()
def plug_filename_update_callback ( self, context ):
    self.plug_filename_update_callback(context)



class PluggableValue(bpy.types.PropertyGroup):
    set_name = StringProperty ( default="", description="Name of the set type (such as engine or runner)" )
    key_name = StringProperty ( default="x", description="Key name into the parameters dictionary" )
    val_type = StringProperty ( default="x" )
    icon_code = StringProperty ( default="NONE" )

    func_val = StringProperty ( default="x", description="A function value" )
    func_val_shadow = StringProperty ( default="x" )

    int_val = IntProperty ( default=-1, description="An integer value", set=plug_int_set_callback, get=plug_int_get_callback, update=plug_int_update_callback )
    int_val_shadow = IntProperty ( default=-1 )

    float_val = FloatProperty ( default=-1.0, description="A float value", set=plug_float_set_callback, get=plug_float_get_callback, update=plug_float_update_callback )
    float_val_shadow = FloatProperty ( default=-1.0 )

    bool_val = BoolProperty ( default=True, description="A boolean value", set=plug_bool_set_callback, get=plug_bool_get_callback, update=plug_bool_update_callback )
    bool_val_shadow = BoolProperty ( default=True )

    string_val = StringProperty ( default="x", description="A string value", set=plug_string_set_callback, get=plug_string_get_callback, update=plug_string_update_callback )
    string_val_shadow = StringProperty ( default="x" )

    filename_val = StringProperty ( subtype='FILE_PATH', default="x", description="A file name string value", set=plug_filename_set_callback, get=plug_filename_get_callback, update=plug_filename_update_callback )
    filename_val_shadow = StringProperty ( subtype='FILE_PATH', default="x" )



    def get_active_module ( self ):
      global active_engine_module
      global active_runner_module
      active_module = None
      if self.set_name == 'engine':
        active_module = active_engine_module
      if self.set_name == 'runner':
        active_module = active_runner_module
      return active_module




    def plug_int_set_callback ( self, value ):
        self.int_val_shadow = value
    def plug_int_get_callback ( self ):
        return self.int_val_shadow
    def plug_int_update_callback ( self, context ):
        #print ( "PluggableValue.plug_int_update_callback called with key_name = " + str(self.key_name) )
        if len(self.key_name) > 0:
          active_module = self.get_active_module()
          if active_module != None:
            # Add items to the lists
            if 'parameter_dictionary' in dir(active_module):
              #print ( "Updating parameter_dictionary with " + str(self.key_name) + " = " + str(self.int_val_shadow) )
              active_module.parameter_dictionary[self.key_name]['val'] = self.int_val_shadow


    def plug_float_set_callback ( self, value ):
        self.float_val_shadow = value
    def plug_float_get_callback ( self ):
        return self.float_val_shadow
    def plug_float_update_callback ( self, context ):
        #print ( "PluggableValue.plug_float_update_callback called with key_name = " + str(self.key_name) )
        if len(self.key_name) > 0:
          active_module = self.get_active_module()
          if active_module != None:
            # Add items to the lists
            if 'parameter_dictionary' in dir(active_module):
              #print ( "Updating parameter_dictionary with " + str(self.key_name) + " = " + str(self.float_val_shadow) )
              active_module.parameter_dictionary[self.key_name]['val'] = self.float_val_shadow


    def plug_bool_set_callback ( self, value ):
        self.bool_val_shadow = value
    def plug_bool_get_callback ( self ):
        return self.bool_val_shadow
    def plug_bool_update_callback ( self, context ):
        #print ( "PluggableValue.plug_bool_update_callback called with key_name = " + str(self.key_name) )
        if len(self.key_name) > 0:
          active_module = self.get_active_module()
          if active_module != None:
            # Add items to the lists
            if 'parameter_dictionary' in dir(active_module):
              #print ( "Updating parameter_dictionary with " + str(self.key_name) + " = " + str(self.bool_val_shadow) )
              active_module.parameter_dictionary[self.key_name]['val'] = self.bool_val_shadow


    def plug_string_set_callback ( self, value ):
        self.string_val_shadow = value
    def plug_string_get_callback ( self ):
        return self.string_val_shadow
    def plug_string_update_callback ( self, context ):
        #print ( "PluggableValue.plug_string_update_callback called with key_name = " + str(self.key_name) )
        if len(self.key_name) > 0:
          active_module = self.get_active_module()
          if active_module != None:
            # Add items to the lists
            if 'parameter_dictionary' in dir(active_module):
              #print ( "Updating parameter_dictionary with " + str(self.key_name) + " = " + str(self.string_val_shadow) )
              active_module.parameter_dictionary[self.key_name]['val'] = self.string_val_shadow


    def plug_filename_set_callback ( self, value ):
        self.filename_val_shadow = value
    def plug_filename_get_callback ( self ):
        return self.filename_val_shadow
    def plug_filename_update_callback ( self, context ):
        #print ( "PluggableValue.plug_filename_update_callback called with key_name = " + str(self.key_name) )
        if len(self.key_name) > 0:
          active_module = self.get_active_module()
          if active_module != None:
            # Add items to the lists
            if 'parameter_dictionary' in dir(active_module):
              #print ( "Updating parameter_dictionary with " + str(self.key_name) + " = " + str(self.filename_val_shadow) )
              active_module.parameter_dictionary[self.key_name]['val'] = self.filename_val_shadow




def plugs_changed_callback ( self, context ):
    self.plugs_changed_callback(context)

class JobIndexProperty(bpy.types.PropertyGroup):
    # This class provides an integer index into the pure python job list
    job_index = IntProperty ( default=-1, description="Job Index" )

class Pluggable(bpy.types.PropertyGroup):
    file_name = StringProperty ( subtype='FILE_PATH', default="")
    engines_enum = EnumProperty ( items=get_engines_as_items, name="", description="Engines", update=plugs_changed_callback )
    runners_enum = EnumProperty ( items=get_runners_as_items, name="", description="Runners", update=plugs_changed_callback )
    engines_show = BoolProperty ( default=False, description="Show Engine Options" )
    runners_show = BoolProperty ( default=False, description="Show Runner Options" )

    # This property holds the list of values for the currently selected plug.
    # The list is emptied and loaded whenever the chosen plug changes
    plug_val_list = CollectionProperty(type=PluggableValue, name="String List")
    active_plug_val_index = IntProperty(name="Active String Index", default=0)

    job_index_list = CollectionProperty(type=JobIndexProperty, name="Job Index List")
    active_job_index = IntProperty(name="Active Job Index", default=0)

    debug_mode = BoolProperty ( default=False, description="Debugging" )


    def plugs_changed_callback ( self, context ):
        global active_engine_module
        global active_runner_module

        # print ( "plugs_changed_callback called" )

        selected_module_code = None
        active_sub_module = None
        set_name = None
        if self == context.scene.mcell.sim_engines:
          # print ( "Engines have changed!!" )
          if active_engine_module != None:
              if 'unregister_blender_classes' in dir(active_engine_module):
                  active_engine_module.unregister_blender_classes()
          set_name = "engine"
          selected_module_code = self.engines_enum
          for plug_module in engine_manager.plug_modules:
              if plug_module.plug_code == selected_module_code:
                  active_sub_module = plug_module
                  active_engine_module = plug_module
                  if active_engine_module != None:
                      if 'register_blender_classes' in dir(active_engine_module):
                          active_engine_module.register_blender_classes()
                  break
        if self == context.scene.mcell.sim_runners:
          # print ( "Runners have changed!!" )
          if active_runner_module != None:
              if 'unregister_blender_classes' in dir(active_runner_module):
                  active_runner_module.unregister_blender_classes()
          set_name = "runner"
          selected_module_code = self.runners_enum
          for plug_module in runner_manager.plug_modules:
              if plug_module.plug_code == selected_module_code:
                  active_sub_module = plug_module
                  active_runner_module = plug_module
                  if active_runner_module != None:
                      if 'register_blender_classes' in dir(active_runner_module):
                          active_runner_module.register_blender_classes()
                  break


        # Clear the lists
        try:
          self.plug_val_list.clear()
          self.active_plug_val_index = -1
          if active_sub_module != None:
            # Add items to the lists
            if 'parameter_dictionary' in dir(active_sub_module):
              # print ( "Ready to go with " + str(active_sub_module.parameter_dictionary.keys()) )
              for k in sorted(active_sub_module.parameter_dictionary.keys()):
                self.plug_val_list.add()
                self.active_plug_val_index = len(self.plug_val_list) - 1
                new_plug_val = self.plug_val_list[self.active_plug_val_index]
                # Change all values to force the ID properties to be instantiated
                new_plug_val.set_name = set_name
                new_plug_val.key_name = ""
                new_plug_val.val_type = ""
                new_plug_val.icon_code = "NONE"
                new_plug_val.int_val = 0
                new_plug_val.float_val = 0.0
                new_plug_val.bool_val = False
                new_plug_val.string_val = ""
                new_plug_val.filename_val = ""

                # Save the index of the PluggableValue property in the dictionary for this parameter
                active_sub_module.parameter_dictionary[k]['_i'] = int(self.active_plug_val_index)
                # Save the key and other values in this property
                new_plug_val.key_name = k
                if 'icon' in active_sub_module.parameter_dictionary[k]:
                  new_plug_val.icon_code = active_sub_module.parameter_dictionary[k]['icon']
                val = active_sub_module.parameter_dictionary[k]['val']
                if type(val) == type(plugs_changed_callback):  # type() needs to return a function
                  # print ( "Got a function callback in 'val'" )
                  # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
                  new_plug_val.val_type = 'F'
                  new_plug_val.func_val = str(val)
                elif type(val) == type(1):     # type() needs to return an integer
                  new_plug_val.val_type = 'i'
                  new_plug_val.int_val = val
                elif type(val) == type(1.2):   # type() needs to return a float
                  new_plug_val.val_type = 'f'
                  new_plug_val.float_val = val
                elif type(val) == type(True):  # type() needs to return a boolean
                  new_plug_val.val_type = 'b'
                  new_plug_val.bool_val = val
                elif type(val) == type("ab"):  # type() needs to return a string
                  subtype = 's'
                  if 'as' in active_sub_module.parameter_dictionary[k].keys():
                    if active_sub_module.parameter_dictionary[k]['as'] == 'filename':
                      subtype = 'fn'
                  if subtype == 's':
                    new_plug_val.val_type = 's'
                    new_plug_val.string_val = val
                  else:
                    new_plug_val.val_type = 'fn'
                    new_plug_val.filename_val = val
                else:
                  # Force everything else to be a string for now (add new types as needed)
                  # print ( "Forcing type " + str(type(val)) + " to be a string" )
                  new_plug_val.val_type = 's'
                  new_plug_val.string_val = str(val)
        except:
          # This except hides these kinds of errors which should be caught first:
          """
          AttributeError: Writing to ID classes in this context is not allowed: Scene, Scene datablock, error setting Pluggable.<UNKNOWN>
          """
          pass



    def draw_panel ( self, context, panel ):
        active_module = None
        this_module_name = ""
        global active_engine_module
        global active_runner_module
        engine_runner_label = ""
        engine_runner_key_name = ""
        engine_runner_options_showing = False
        if self == context.scene.mcell.sim_engines:
          #print ( "Drawing Engines" )
          active_module = active_engine_module
          this_module_name = "engines\t"
          engine_runner_label = "Simulate using:"
          engine_runner_key_name = "engines_show"
          engine_runner_options_showing = self.engines_show
        if self == context.scene.mcell.sim_runners:
          #print ( "Drawing Runners" )
          active_module = active_runner_module
          this_module_name = "runners\t"
          engine_runner_label = "Run using:"
          engine_runner_key_name = "runners_show"
          engine_runner_options_showing = self.runners_show
        if self.debug_mode:
          __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

        layout = panel
        #row = layout.row()
        #row.label ( "-=- Dynamic -=-" )

        box = layout.box()
        layout = box

        #### Below here: layout is in the box

        row = layout.row()

        col = row.column()
        col.alignment = 'LEFT'
        if engine_runner_options_showing:
          col.prop ( self, engine_runner_key_name, text=engine_runner_label, icon='TRIA_DOWN', emboss=False )
        else:
          col.prop ( self, engine_runner_key_name, text=engine_runner_label, icon='TRIA_RIGHT', emboss=False )

        col = row.column()
        something_selected = False
        if self == context.scene.mcell.sim_engines:
          col.prop ( self, 'engines_enum' )
          if self.engines_enum != 'NONE':
            something_selected = True
        if self == context.scene.mcell.sim_runners:
          col.prop ( self, 'runners_enum' )
          if self.runners_enum != 'NONE':
            something_selected = True
        #col = row.column()
        #col.operator ( 'pluggable.reload', icon='FILE_REFRESH' )


        if (active_module == None) or (something_selected == False):
            row = layout.row()
            row.label ( "No module selected" )
        elif engine_runner_options_showing:
            if ('parameter_dictionary' in dir(active_module)) and ('parameter_layout' in dir(active_module)):

                # Assign the indexes (needs to be done because the indexes are not stored as Blender Properties
                # There might be a better way to do this.
                idx = 0
                for k in sorted(active_module.parameter_dictionary.keys()):
                  active_module.parameter_dictionary[k]['_i'] = idx
                  idx += 1

                # Draw the panel according to the layout
                for r in active_module.parameter_layout:
                    row = layout.row()
                    for k in r:
                        col = row.column()
                        if k in active_module.parameter_dictionary:
                            p = active_module.parameter_dictionary[k]
                            if p and '_i' in p:
                                s = self.plug_val_list[p['_i']]
                                if s.val_type == 'F':
                                    col.operator ( 'pluggable.user_function', text=s.key_name, icon=s.icon_code ).user_function_name = this_module_name + s.key_name
                                elif s.val_type == 'i':
                                    col.prop ( s, "int_val", text=s.key_name, icon=s.icon_code )
                                elif s.val_type == 'f':
                                    col.prop ( s, "float_val", text=s.key_name, icon=s.icon_code )
                                elif s.val_type == 'b':
                                    col.prop ( s, "bool_val", text=s.key_name, icon=s.icon_code )
                                elif s.val_type == 's':
                                    col.prop ( s, "string_val", text=s.key_name, icon=s.icon_code )
                                elif s.val_type == 'fn':
                                    col.prop ( s, "filename_val", text=s.key_name, icon=s.icon_code )
            else:
                # Draw the panel in alphabetical order
                for s in self.plug_val_list:
                    row = layout.row()
                    if s.val_type == 'F':
                        row.operator ( 'pluggable.user_function', text=s.key_name, icon=s.icon_code ).user_function_name = this_module_name + s.key_name
                    elif s.val_type == 'i':
                        row.prop ( s, "int_val", text=s.key_name, icon=s.icon_code )
                    elif s.val_type == 'f':
                        row.prop ( s, "float_val", text=s.key_name, icon=s.icon_code )
                    elif s.val_type == 'b':
                        row.prop ( s, "bool_val", text=s.key_name, icon=s.icon_code )
                    elif s.val_type == 's':
                        row.prop ( s, "string_val", text=s.key_name, icon=s.icon_code )
                    elif s.val_type == 'fn':
                        col.prop ( s, "filename_val", text=s.key_name, icon=s.icon_code )
                  
            if 'draw_layout' in dir(active_module):
              # Call the custom (typically raw Blender) drawing function for this layout:
              active_module.draw_layout ( None, context, layout )


        #### Above here: layout is in the box

        layout = panel

