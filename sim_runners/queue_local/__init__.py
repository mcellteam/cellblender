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

import cellblender.sim_engines as sim_engines



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
import cellblender.parameter_system as parameter_system
import cellblender.cellblender_utils as cellblender_utils
import cellblender.data_model as data_model

#from cellblender.mdl import data_model_to_mdl
#from cellblender.mdl import run_data_model_mcell

from cellblender.cellblender_utils import mcell_files_path

from multiprocessing import cpu_count

import cellblender.sim_engines as engine_manager
import cellblender.sim_runners as runner_manager



plug_code = "QUEUE_LOCAL"
plug_name = "Local Queue"

def register():
  global parameter_dictionary
  print ( "Register was called with dictionary = " + str(parameter_dictionary) )
  register_blender_classes()

def unregister():
  global parameter_dictionary
  print ( "UnRegister was called with dictionary = " + str(parameter_dictionary) )
  unregister_blender_classes()

parameter_dictionary = {
  'Show Normal Output': {'val':True, 'desc':"Show stdout from process"},
  'Show Error Output':  {'val':True, 'desc':"Show stderr from process"},
  'Register': {'val': register, 'desc':"Register Blender Classes"},
  'UnRegister': {'val': unregister, 'desc':"UnRegister Blender Classes"}
}

parameter_layout = [
  ['Show Normal Output', 'Show Error Output'],
  ['Register', 'UnRegister']
]


def run_commands ( commands ):
    sp_list = []
    window_num = 0
    for cmd in commands:
        command_list = [ cmd['cmd'] ]
        for arg in cmd['args']:
            command_list.append ( arg )
        sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=None, stderr=None ) )
        window_num += 1
    return sp_list

def draw_layout ( self, context, layout ):
    mcell = context.scene.mcell
    row = layout.row()
    row.label ( text="This label was drawn by the Dynamic Queue Runner!!", icon='FORCE_LENNARDJONES' )




def get_pid(item):
    return int(item.name.split(',')[0].split(':')[1])



class MCELL_OT_percentage_done_timer(bpy.types.Operator):
    """Update the MCell job list periodically to show percentage done"""
    bl_idname = "mcell.percentage_done_timer"
    bl_label = "Modal Timer Operator"
    bl_options = {'REGISTER'}

    _timer = None

    def modal(self, context, event):
        print ( "modal called inside dynamic queue runner" )
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
        print ( "execute called inside dynamic queue runner" )
        wm = context.window_manager
        # this is how often we should update this in seconds
        secs = 0.5
        self._timer = wm.event_timer_add(secs, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        print ( "cancel called inside dynamic queue runner" )
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class MCELL_OT_run_simulation_control_queue(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_control_queue"
    bl_label = "Run MCell Simulation Using Command Queue"
    bl_description = "Run MCell Simulation Using Command Queue"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "run_simulation.execute called inside dynamic queue runner" )

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
                engine_manager.write_default_data_layout(project_dir, start_seed, end_seed)

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
                  make_texts = mcell.run_simulation.save_text_logs
                  proc = cellblender.simulation_queue.add_task(mcell_binary, mcell_args, os.path.join(project_dir, "output_data"), make_texts)

                  self.report({'INFO'}, "Simulation Running")

                  if not simulation_process.name:
                      simulation_process.name = ("PID: %d, Seed: %d" % (proc.pid, seed))
                  bpy.ops.mcell.percentage_done_timer()

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
        print ( "kill_simulation.kill_simulation called inside dynamic queue runner" )
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
        print ( "kill_simulation.execute called inside dynamic queue runner" )

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


def register_blender_classes():
    print ( "Registering" )
    bpy.utils.register_class(MCELL_OT_percentage_done_timer)
    bpy.utils.register_class(MCELL_OT_run_simulation_control_queue)
    bpy.utils.register_class(MCELL_OT_kill_simulation)
    bpy.utils.register_class(MCELL_OT_kill_all_simulations)
    print ( "Done" )

def unregister_blender_classes():
    print ( "UnRegistering" )
    bpy.utils.unregister_class(MCELL_OT_kill_all_simulations)
    bpy.utils.unregister_class(MCELL_OT_kill_simulation)
    bpy.utils.unregister_class(MCELL_OT_run_simulation_control_queue)
    bpy.utils.unregister_class(MCELL_OT_percentage_done_timer)
    print ( "Done" )

