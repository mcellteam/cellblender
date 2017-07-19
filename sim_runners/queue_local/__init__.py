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

import os
import subprocess
import sys

import cellblender

import cellblender.sim_engines as engine_manager
import cellblender.sim_runners as runner_manager


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
import cellblender.parameter_system as parameter_system
import cellblender.cellblender_utils as cellblender_utils
import cellblender.cellblender_simulation as cellblender_simulation
import cellblender.data_model as data_model

#from cellblender.mdl import data_model_to_mdl
#from cellblender.mdl import run_data_model_mcell

from cellblender.cellblender_utils import mcell_files_path

from multiprocessing import cpu_count




plug_code = "QUEUE_LOCAL"
plug_name = "Local Queue"

def remove_task_texts():
    print ( "Remove task texts" )
    bpy.ops.mcell.remove_text_logs()


parameter_dictionary = {
  'Save Text Logs': {'val':True, 'desc':"Create a text log for each run"},
  'Remove Task Output Texts':  {'val':remove_task_texts, 'desc':'Remove all text files of name "task_*_output"'}
}

parameter_layout = [
  ['Save Text Logs', 'Remove Task Output Texts'],
]

def draw_layout ( self, context, layout ):
    mcell = context.scene.mcell
    #row = layout.row()
    #row.label ( text="This label was drawn by the Dynamic Queue Runner!!", icon='FORCE_LENNARDJONES' )
    #row = layout.row()
    #row.operator("ql.clear_run_list")




def get_pid(item):
    # print ( "queue_local.get_pid called with item.name = " + str(item.name) )
    l = item.name.split(',')[0].split(':')
    rtn_val = 0
    if len(l) > 1:
      rtn_val = int(l[1])
    return rtn_val



def run_commands ( commands ):
    print ( "run_commands" )
    for cmd in commands:
      print ( "  CMD: " + str(cmd['cmd']) + " " + str(cmd['args']) )
      """
      CMD: {
        'args': ['print_detail=20',
                 'proj_path=/.../intro/2017/2017_07/2017_07_11/queue_runner_tests_files/mcell',
                 'seed=1',
                 'data_model=dm.json'],
        'cmd': '/.../blender/2.78/scripts/addons/cellblender/sim_engines/limited_cpp/mcell_main',
        'wd':  '/.../intro/2017/2017_07/2017_07_11/queue_runner_tests_files/mcell',
        'stdout': '',
        'stderr': ''
      }
      """

    context = bpy.context
    mcell = context.scene.mcell

    # Set the Blender property from the local for now using the older code
    # Eventually, the parameter_dictionary version should be used directly by the runner
    mcell.run_simulation.save_text_logs = parameter_dictionary['Save Text Logs']['val']


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
            # engine_manager.write_default_data_layout(project_dir, start_seed, end_seed)

            processes_list = mcell.run_simulation.processes_list

            run_index = 0
            # for seed in range(start_seed,end_seed + 1):
            for cmd in commands:
              processes_list.add()

              mcell.run_simulation.active_process_index = len(mcell.run_simulation.processes_list) - 1
              simulation_process = processes_list[mcell.run_simulation.active_process_index]

              print("Starting MCell for cmd %s ... create start_time.txt file:" % str(cmd))
              with open(os.path.join(os.path.dirname(bpy.data.filepath), "start_time.txt"), "w") as start_time_file:
                  start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

              # Log filename will be log.year-month-day_hour:minute_run_index.txt
              # (e.g. log.2013-03-12_11:45_1.txt)
              time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

              if error_file_option == 'file':
                  error_filename = "error.%s_%d.txt" % (time_now, run_index)
              elif error_file_option == 'none':
                  error_file = subprocess.DEVNULL
              elif error_file_option == 'console':
                  error_file = None

              if log_file_option == 'file':
                  log_filename = "log.%s_%d.txt" % (time_now, run_index)
              elif log_file_option == 'none':
                  log_file = subprocess.DEVNULL
              elif log_file_option == 'console':
                  log_file = None

              #mdl_filename = '%s.main.mdl' % (base_name)
              #mcell_args = '-seed %d %s' % (seed, mdl_filename)
              make_texts = mcell.run_simulation.save_text_logs

              if type(cmd) == type('str'):
                  proc = cellblender.simulation_queue.add_task(cmd, "", os.path.join(project_dir, "output_data"), make_texts)
              elif type(cmd) == type({'a':1}):
                  proc = cellblender.simulation_queue.add_task(cmd['cmd'], ' '.join(cmd['args']), cmd['wd'], make_texts)
              # Save the module in the engine_module_dict by PID
              cellblender_simulation.engine_module_dict[proc.pid] = cellblender_simulation.active_engine_module

              # self.report({'INFO'}, "Simulation Running")

              if not simulation_process.name:
                  simulation_process.name = ("PID: %d, Index: %d" % (proc.pid, run_index))
              bpy.ops.mcell.percentage_done_timer()

    else:
        status = "Python not found. Set it in Project Settings."

    mcell.run_simulation.status = status

    # return {'FINISHED'}



class MCELL_QL_percentage_done_timer(bpy.types.Operator):
    """Update the MCell job list periodically to show percentage done"""
    bl_idname = "mcell.percentage_done_timer"
    bl_label = "Modal Timer Operator"
    bl_options = {'REGISTER'}

    _timer = None

    def modal(self, context, event):
        #print ( "modal called inside dynamic queue runner" )
        if event.type == 'TIMER':
            task_len = len(cellblender.simulation_queue.task_dict)
            task_ctr = 0
            mcell = context.scene.mcell
            processes_list = mcell.run_simulation.processes_list
            for simulation_process in processes_list:
                if not mcell.run_simulation.save_text_logs:
                    return {'CANCELLED'}
                pid = get_pid(simulation_process)
                q_item = cellblender.simulation_queue.task_dict[pid]
                progress_message = None
                task_complete = False
                if pid in cellblender_simulation.engine_module_dict:
                    em = cellblender_simulation.engine_module_dict[pid]
                    # print ( "Engine Module for " + str(pid) + " is : " + em.plug_name )
                    # print ( "   Engine Module Contains : " + str(dir(em)) )
                    if 'get_progress_message_and_status' in dir(em):
                        # Engine supports progress, so pass current stdout to the progress/status function and show as progress
                        if q_item['bl_text'] is None:
                            # This sometimes happens at the start of a run
                            progress_message = em.plug_name
                        else:
                            stdout_txt = q_item['bl_text'].as_string()
                            (progress_message, task_complete) = em.get_progress_message_and_status ( stdout_txt )
                    else:
                        # Engine doesn't support progress, so just show its own name as progress
                        progress_message = em.plug_name

                if progress_message == None:
                    progress_message = ""

                simulation_process.name = "PID: %d" % (pid)
                if progress_message != None:
                    if len(progress_message) > 0:
                        simulation_process.name = simulation_process.name + ", " + progress_message

                if task_complete:
                    task_ctr += 1

            # just a silly way of forcing a screen update. ¯\_(ツ)_/¯
            color = context.user_preferences.themes[0].view_3d.space.gradients.high_gradient
            color.h += 0.01
            color.h -= 0.01
            # if every job is done, quit updating the screen
            if task_len == task_ctr:
                self.cancel(context)
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        #print ( "execute called inside dynamic queue runner" )
        wm = context.window_manager
        # this is how often we should update this in seconds
        secs = 0.5
        self._timer = wm.event_timer_add(secs, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        #print ( "cancel called inside dynamic queue runner" )
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class MCELL_QL_kill_simulation(bpy.types.Operator):
    bl_idname = "mcell.kill_simulation"
    bl_label = "Kill Selected Simulation"
    bl_description = ("Kill/Cancel Selected Running/Queued MCell Simulation. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}


    @classmethod
    def poll(self,context):
        #print ( "kill_simulation.poll called inside dynamic queue runner" )
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
        #print ( "kill_simulation.execute called inside dynamic queue runner" )

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


class MCELL_QL_kill_all_simulations(bpy.types.Operator):
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

class MCELL_QL_clear_run_list(bpy.types.Operator):
    bl_idname = "ql.clear_run_list"
    bl_label = "Clear Completed Runs"
    bl_description = ("Clear the list of completed and failed runs. "
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

def register_blender_classes():
    print ( "Registering Queue_Local classes" )
    bpy.utils.register_class(MCELL_QL_percentage_done_timer)
    #bpy.utils.register_class(MCELL_QL_run_simulation_control_queue)
    bpy.utils.register_class(MCELL_QL_kill_simulation)
    bpy.utils.register_class(MCELL_QL_kill_all_simulations)
    bpy.utils.register_class(MCELL_QL_clear_run_list)
    print ( "Done Registering" )

def unregister_this_class(this_class):
    try:
      bpy.utils.unregister_class(this_class)
    except Exception as ex:
      pass

def unregister_blender_classes():
    print ( "UnRegistering Queue_Local classes" )
    unregister_this_class (MCELL_QL_clear_run_list)
    unregister_this_class (MCELL_QL_kill_all_simulations)
    unregister_this_class (MCELL_QL_kill_simulation)
    #unregister_this_class (MCELL_QL_run_simulation_control_queue)
    unregister_this_class (MCELL_QL_percentage_done_timer)
    print ( "Done Unregistering" )

