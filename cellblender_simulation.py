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
import bgl
import blf
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

from bpy.app.handlers import persistent


# python imports
import array
import glob
import os
import sys
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

from cellblender.mdl import data_model_to_mdl
#from cellblender.mdl import run_data_model_mcell

from cellblender.cellblender_utils import project_files_path, mcell_files_path

from multiprocessing import cpu_count

import cellblender.sim_engines as engine_manager
import cellblender.sim_runners as runner_manager
import cellblender.mcell4 as mcell4

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


############## Overlay Support (some from sim_runners/queue_local/__init__.py) ##################

handler_list = []           # Holds returns from bpy.types.SpaceView3D.draw_handler_add() for removal
screen_display_lines = {}   # Dictionary of lines keyed by integer Process ID (PID)
scroll_offset = 0           # Current Scroll offset
scroll_page_size = 10       # Lines per scroll
clear_flag = False          # Drawing when this is set will clear the background
showing_text = False        # Flag to indicate whether text is currently being shown


def draw_callback_px(context):
    # print ( "draw callback -=-=-=-=" + (50 * "-=" ) + "-" )

    # Note that the "context" passed in here is a regular dictionary and not the Blender context
    global screen_display_lines
    global scroll_offset
    global clear_flag
    local_display_lines = {}

    task_dict = cellblender.simulation_queue.task_dict

    pid = None
    if 'mcell' in bpy.context.scene:
      mcell = bpy.context.scene.mcell
      if 'run_simulation' in mcell:
        rs = mcell.run_simulation
        if len(rs.processes_list) > 0:
          pid_str = rs.processes_list[rs.active_process_index].name
          pid = pid_str.split(',')[0].split()[1]

    if pid != None:
        ipid = int(pid)
        # print ( " ))))))))))) " + str(task_dict[ipid]['output'][-1]) )
        local_display_lines[ipid] = [ l.strip() for l in task_dict[ipid]['output'] ]
        local_display_lines[ipid].reverse()
        screen_display_lines[str(pid)] = local_display_lines[ipid]
        # screen_display_lines[str(pid)].reverse() # Reverse since they'll be drawn from the bottom up

    bgl.glPushAttrib(bgl.GL_ENABLE_BIT)

    if clear_flag:
      bgl.glClearColor ( 0.0, 0.0, 0.0, 1.0 )
      bgl.glClear ( bgl.GL_COLOR_BUFFER_BIT )

    font_id = 0  # XXX, need to find out how best to get this.

    y_pos = 15 * (scroll_offset + 1)
    if pid and (pid in screen_display_lines):
      for l in screen_display_lines[pid]:
          blf.position(font_id, 15, y_pos, 0)
          y_pos += 15
          blf.size(font_id, 14, 72) # fontid, size, DPI
          bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
          blf.draw(font_id, l)
    else:
      keys = screen_display_lines.keys()
      for k in keys:
          for l in screen_display_lines[k]:
              blf.position(font_id, 15, y_pos, 0)
              y_pos += 15
              blf.size(font_id, 14, 72) # fontid, size, DPI
              bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
              blf.draw(font_id, l)

    # 100% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)

    bgl.glPopAttrib()

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def get_3d_areas():
  global handler_list
  areas = []
  if len(bpy.data.window_managers) > 0:
    if len(bpy.data.window_managers[0].windows) > 0:
      if len(bpy.data.window_managers[0].windows[0].screen.areas) > 0:
        if len(handler_list) <= 0:
          for area in bpy.data.window_managers[0].windows[0].screen.areas:
            # print ( "Found an area of type " + str(area.type) )
            if area.type == 'VIEW_3D':
              areas.append ( area )
  return ( areas )


def enable_text_overlay():
  global handler_list
  global showing_text
  areas = get_3d_areas()
  for area in areas:
    temp_context = bpy.context.copy()
    temp_context['area'] = area
    args = (temp_context,)
    handler_list.append ( bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL') )
  bpy.context.area.tag_redraw()
  showing_text = True
  print ( "Enable completed" )

def disable_text_overlay():
  global handler_list
  global showing_text
  while len(handler_list) > 0:
    print ( "Removing draw_handler " + str(handler_list[-1]) )
    bpy.types.SpaceView3D.draw_handler_remove(handler_list[-1], 'WINDOW')
    handler_list.pop()
  bpy.context.area.tag_redraw()
  showing_text = False
  print ( "Disable completed" )


def page_up():
  global scroll_offset
  global scroll_page_size
  if scroll_page_size == 0:
    # This provides a way to get back to 0 without searching
    scroll_offset = 0
  else:
    scroll_offset += -scroll_page_size
  # Force a redraw of the OpenGL code
  bpy.context.area.tag_redraw()

def page_dn():
  global scroll_offset
  global scroll_page_size
  if scroll_page_size == 0:
    # This provides a way to get back to 0 without searching
    scroll_offset = 0
  else:
    scroll_offset += scroll_page_size
  # Force a redraw of the OpenGL code
  bpy.context.area.tag_redraw()



class MCELL_OT_show_text_overlay (bpy.types.Operator):
    bl_idname = "mcell.show_text_overlay"
    bl_label = "Show Text"
    bl_description = ("Show the Text Overlay.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        #print ( "Show text" )
        enable_text_overlay()
        return {'FINISHED'}

class MCELL_OT_hide_text_overlay (bpy.types.Operator):
    bl_idname = "mcell.hide_text_overlay"
    bl_label = "Hide Text"
    bl_description = ("Hide the Text Overlay.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        #print ( "Hide text" )
        disable_text_overlay()
        return {'FINISHED'}


class MCELL_OT_page_overlay_up (bpy.types.Operator):
    bl_idname = "mcell.page_overlay_up"
    bl_label = "View Up"
    bl_description = ("Page the Text Overlay Up.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        #print ( "Show text" )
        page_up()
        return {'FINISHED'}

class MCELL_OT_page_overlay_dn (bpy.types.Operator):
    bl_idname = "mcell.page_overlay_dn"
    bl_label = "View Dn"
    bl_description = ("Page the Text Overlay Down.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        #print ( "Hide text" )
        page_dn()
        return {'FINISHED'}

class MCELL_OT_page_overlay_hm (bpy.types.Operator):
    bl_idname = "mcell.page_overlay_hm"
    bl_label = "Home"
    bl_description = ("Page the Text Overlay to Home.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        global scroll_offset
        scroll_offset = 0
        # Force a redraw of the OpenGL code
        bpy.context.area.tag_redraw()
        return {'FINISHED'}


######################################################################





def run_generic_runner (context, sim_module):

    mcell = context.scene.mcell
    mcell.run_simulation.last_simulation_run_time = str(time.time())

    binary_path = mcell.cellblender_preferences.mcell_binary
    mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )
    if not mcell.cellblender_preferences.mcell_binary_valid:
        print ( "cellblender_simulation.run_generic_runner: invalid binary: " + str(binary_path) )

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
            os.makedirs(react_dir, exist_ok=True)

        viz_dir = os.path.join(project_dir, "viz_data")
        if (os.path.exists(viz_dir) and
                mcell.run_simulation.remove_append == 'remove'):
            shutil.rmtree(viz_dir)
        if not os.path.exists(viz_dir):
            os.makedirs(viz_dir, exist_ok=True)

        runner_input = "dm.txt"
        if "runner_input" in dir(sim_module):
          runner_input = sim_module.runner_input

        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True, scripts=True )
        if runner_input.endswith("json"):
          data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,runner_input) )
        else:
          print("SAVING to " + os.path.join(project_dir,runner_input))
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

        print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
        engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
        with open(os.path.join(project_files_path(),"start_time.txt"), "w") as start_time_file:
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


class MCELL_OT_dm_export_mdl(bpy.types.Operator):
    bl_idname = "mcell.dm_export_mdl"
    bl_label = "Export CellBlender Project"
    bl_description = ("Export CellBlender Project (via data model)")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self,context):

        mcell = context.scene.mcell
        if mcell.cellblender_preferences.lockout_export and mcell.cellblender_preferences.decouple_export_run:
            # print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            # The "self" here doesn't contain or permit the report function.
            # self.report({'INFO'}, "Exporting is Locked Out")
            return False
        else:
            # Note: We could copy more complex logic from mcell.run_simulation's poll method.
            return True
        return True

    def execute(self, context):
        print ( "Export via data model" )
        mcell = context.scene.mcell
        run_sim = mcell.run_simulation
        run_sim.export_requested = True
        run_sim.run_requested = False

        if str(run_sim.simulation_run_control) == 'SWEEP_QUEUE':
            bpy.ops.mcell.run_simulation_sweep_queue()
        #elif str(run_sim.simulation_run_control) == 'SWEEP_SGE':
        #    bpy.ops.mcell.run_simulation_sweep_sge()
        else:
            print ( "Run option \"" + str(run_sim.simulation_run_control) + "\" cannot be exported without being run in this version of CellBlender." )
            print ( "  Disable the \"Decouple Export and Run\" option to use this runner." )

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

        if mcell.cellblender_preferences.decouple_export_run:
            run_sim.export_requested = False
        else:
            run_sim.export_requested = True
        run_sim.run_requested = True

        if mcell.cellblender_preferences.lockout_export and (not mcell.cellblender_preferences.decouple_export_run):
            # Exporting is locked out and this operator is in "Export and Run Mode"
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
            if str(mcell.run_simulation.simulation_run_control) == 'SWEEP_QUEUE':
                bpy.ops.mcell.run_simulation_sweep_queue()
            elif str(mcell.run_simulation.simulation_run_control) == 'QUEUE':
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
                print ( "Unexpected case (" + str(mcell.run_simulation.simulation_run_control) + ") in MCELL_OT_run_simulation" )
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
                    os.makedirs(sweep_dir, exist_ok=True)

                mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True, scripts=True )
                data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,"data_model.json") )

                # base_name = mcell.project_settings.base_name
                base_name = context.scene.name.replace(" ", "_")

                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))

                # The following Python program will create the "data_layout.json" file describing the directory structure
                script_file_path = os.path.join(script_dir_path, os.path.join("mdl", "run_data_model_mcell.py") )

                processes_list = run_sim.processes_list
                processes_list.add()
                run_sim.active_process_index = len(run_sim.processes_list) - 1
                simulation_process = processes_list[run_sim.active_process_index]

                print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
                engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
                with open(os.path.join(project_files_path(),"start_time.txt"), "w") as start_time_file:
                    start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

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
            if mcell.run_simulation.print_timer_ticks:
                print ( "modal -=-=-=-=" + (50 * "-=" ) + "-" )
            processes_list = mcell.run_simulation.processes_list
            for simulation_process in processes_list:
                #if not mcell.run_simulation.save_text_logs:
                #    return {'CANCELLED'}
                pid = get_pid(simulation_process)
                seed = int(simulation_process.name.split(',')[1].split(':')[1])
                q_item = cellblender.simulation_queue.task_dict[pid] # q_item is a dictionary with stdout,stderr,status,args,cmd,process,bl_text
                percent = None
                if 'output' in q_item:
                    output_lines = q_item['output']
                    n = len(output_lines)
                    last_iter = total_iter = 0
                    for i in reversed(range(n)):
                        l = output_lines[i]
                        if l.startswith("Iterations"):
                            last_iter = int(l.split()[1])
                            total_iter = int(l.split()[3])
                            percent = (last_iter/total_iter)*100
                            break
                    if ((last_iter == total_iter) and (total_iter != 0)) or (q_item['status'] in ['died','mcell_error']):
                        task_ctr += 1

                if percent is None:
                    simulation_process.name = "PID: %d, Seed: %d" % (pid, seed)
                else:
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
        print ( "Inside MCELL_OT_percentage_done_timer.execute with context = " + str(context) )
        print ( "Inside MCELL_OT_percentage_done_timer.execute with mcell = " + str(context.scene.mcell) )
        run_sim = context.scene.mcell.run_simulation
        delay = run_sim.text_update_timer_delay   # this is how often we should update this in seconds
        print ( "Setting timer to delay of " + str(delay) )
        wm = context.window_manager
        self._timer = wm.event_timer_add(delay, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class MCELL_OT_run_simulation_sweep_queue(bpy.types.Operator):
    bl_idname = "mcell.run_simulation_sweep_queue"
    bl_label = "Run MCell Simulation Using Sweep Queue"
    bl_description = "Run MCell Simulation Using Sweep Queue"
    bl_options = {'REGISTER'}


    def execute(self, context):
        print ( "+++++++++++++ Begin: mcell.run_simulation_sweep_queue +++++++++++++" )

        mcell = context.scene.mcell
        run_sim = mcell.run_simulation
        
        mcell4_mode = mcell.cellblender_preferences.mcell4_mode
        if mcell.cellblender_preferences.mcell4_mode:
            print ( "- Using mcell4 mode" )

        run_sim.last_simulation_run_time = str(time.time())

        start_seed = int(run_sim.start_seed.get_value())
        end_seed = int(run_sim.end_seed.get_value())
        mcell_processes = run_sim.mcell_processes
        mcell_processes_str = str(run_sim.mcell_processes)
        mcell_binary = cellblender_utils.get_mcell_path(mcell)
        ext_path = os.path.dirname(os.path.realpath(mcell_binary))

        # Set environment variable for the shared library path
        my_env = os.environ.copy()
        if (sys.platform == 'darwin'):
          if my_env.get('DYLD_LIBRARY_PATH'):
            my_env['DYLD_LIBRARY_PATH']=os.path.join(ext_path,'lib') + os.pathsep + my_env['DYLD_LIBRARY_PATH']
          else:
            my_env['DYLD_LIBRARY_PATH']=os.path.join(ext_path,'lib')
        else:
          if my_env.get('LD_LIBRARY_PATH'):
            my_env['LD_LIBRARY_PATH']=os.path.join(ext_path,'lib') + os.pathsep + my_env['LD_LIBRARY_PATH']
          else:
            my_env['LD_LIBRARY_PATH']=os.path.join(ext_path,'lib')

        # Force the project directory to be where the .blend file lives
        project_dir = mcell_files_path()
        status = ""

        python_path = cellblender.cellblender_utils.get_python_path(mcell=mcell)

        if python_path:
            #if not mcell.cellblender_preferences.decouple_export_run:
            #    bpy.ops.mcell.export_project()

            # The separation between exporting and running is complicated when sweeping
            # because the same steps may need to be carried out twice. The sweep needs
            # to be traversed when exporting, and it needs to be traversed again to generate
            # the run commands. Otherwise it needs to be saved between exporting and running.
            #
            # For now, this is handled with these two flags:
            #    export_requested = BoolProperty(name="Export Requested", default=True)
            #    run_requested = BoolProperty(name="Run Requested", default=True)
            # This allows the same code to do what's appropriate for the current requests.

            if (run_sim.error_list and mcell.cellblender_preferences.invalid_policy == 'dont_run'):
                pass
            else:
                react_dir = os.path.join(project_dir, "output_data", "react_data")
                viz_dir = os.path.join(project_dir, "output_data", "viz_data")

                if run_sim.export_requested and (run_sim.remove_append == 'remove'):
                    # Remove the entire output directory
                    out_dir = os.path.join(project_dir, "output_data")
                    if os.path.exists(out_dir):
                        shutil.rmtree(out_dir)

                if run_sim.export_requested and not os.path.exists(react_dir):
                    os.makedirs(react_dir, exist_ok=True)

                if run_sim.export_requested and not os.path.exists(viz_dir):
                    os.makedirs(viz_dir, exist_ok=True)


                # This assumes "mcell.export_project" operator had been run:   base_name = mcell.project_settings.base_name
                # Do this here since "mcell.export_project" is not being used with this code.
                base_name = scene_name = context.scene.name.replace(" ", "_")

                if run_sim.export_requested:
                    # The export checking logic is broken for sweep runs that don't have a main MDL file at the top.
                    # Rather than muck with that right now, just create a dummy file to signal that it's been exported.
                    ##################################################################
                    main_mdl = mcell_files_path()
                    main_mdl = os.path.join(main_mdl, "output_data")
                    main_mdl = os.path.join(main_mdl, base_name + ".main.mdl")
                    main_mdl_file = open(main_mdl, "w", encoding="utf8", newline="\n")
                    main_mdl_file.write ( "/* This file is written to signal to CellBlender that the project has been exported. */" )
                    main_mdl_file.close()
                    ##################################################################


                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                cellblender.simulation_queue.python_exec = python_path
                cellblender.simulation_queue.start(mcell_processes)
                cellblender.simulation_queue.notify = True

                if run_sim.enable_run_once_script:
                    # Execute a run once during export data model script before getting the data model
                    script_name = None

                    if run_sim.internal_external == "internal":
                        script_name = run_sim.dm_run_once_internal_fn

                        print ( "Executing internal script" )
                        if not script_name in bpy.data.texts:
                            print ( "Error: Script \"" + script_name + "\" is not an internal script name. Try refreshing the scripts list." )
                        else:
                            # This version just runs the script
                            script_text = bpy.data.texts[script_name].as_string()
                            print ( 80*"=" )
                            print ( script_text )
                            print ( 80*"=" )
                            exec ( script_text, locals() )

                    elif run_sim.internal_external == "external":
                        script_name = run_sim.dm_run_once_external_fn
                        print ( "Executing external script \"" + str(script_name) + "\" ... not implemented yet!!" )

                dm = None
                if run_sim.export_requested:
                    # When exporting, the geometry data will be needed to write the MDL
                    dm = mcell.build_data_model_from_properties ( context, geometry=True, scripts=True )
                else:
                    # When just running, the geometry data isn't needed so build a data model without it
                    dm = mcell.build_data_model_from_properties ( context, geometry=False, scripts=False )

                sweep_list = engine_manager.build_sweep_list( dm['parameter_system'] )
                print ( "Sweep list = " + str(sweep_list) )
                # Add a "current_index" of 0 to support the sweeping
                for sw_item in sweep_list:
                  sw_item['current_index'] = 0
                  print ( "  Sweep list item = " + str(sw_item) )

                if run_sim.export_requested:
                    # The following line will create the "data_layout.json" file describing the directory structure
                    engine_manager.write_sweep_list_to_layout_file ( sweep_list, start_seed, end_seed, os.path.join ( project_dir, "data_layout.json" ) )

                # Count the number of sweep runs
                num_sweep_runs = engine_manager.count_sweep_runs ( sweep_list )
                num_requested_runs = num_sweep_runs * (1 + end_seed - start_seed)
                print ( "Number of non-seed sweep runs = " + str(num_sweep_runs) )
                print ( "Total runs (sweep and seed) is " + str(num_requested_runs) )


                # Build a list of "run commands" (one for each run) to be put in the queue
                # Note that the format of these came from the original "run_simulations.py" program and may not be what we want in the long run
                run_cmd_list = []
                # Build a sweep list with an "output_data" prefix directory
                for run in range (num_sweep_runs):
                    sweep_path = "output_data"
                    for sw_item in sweep_list:
                        sweep_path += os.sep + sw_item['par_name'] + "_index_" + str(sw_item['current_index'])
                    print ( "Sweep path = " + sweep_path )
                    # Set the data model parameters to the current parameter settings
                    for par in dm['parameter_system']['model_parameters']:
                        if ('par_name' in par):
                            for sweep_item in sweep_list:
                                if par['par_name'] == sweep_item['par_name']:
                                    par['par_expression'] = str(sweep_item['values'][sweep_item['current_index']])
                    # Sweep through the seeds for this set of parameters creating a run specification for each seed
                    for seed in range(start_seed,end_seed+1):
                        # Create the directories and write the MDL
                        sweep_item_path = os.path.join(project_dir,sweep_path)
                        if run_sim.export_requested:
                            engine_manager.makedirs_exist_ok ( sweep_item_path, exist_ok=True )
                            engine_manager.makedirs_exist_ok ( os.path.join(sweep_item_path,'react_data'), exist_ok=True )
                            engine_manager.makedirs_exist_ok ( os.path.join(sweep_item_path,'viz_data'), exist_ok=True )
                            
                            if mcell4_mode:
                                dm_file = str(os.path.join(sweep_item_path, '%s.data_model.json' % (base_name)))
                                print ( "Writing data model to " + dm_file )
                                data_model.save_data_model_to_json_file(dm, dm_file)
                                print ( "Converting data model to MCell4 Python code" )
                                error_msg = mcell4.convert_data_model_to_python(mcell_binary, dm_file, sweep_item_path, base_name)
                                if error_msg:
                                    status = 'Conversion of data model into MCell4 Python code failed. ' + error_msg 
                                    self.report({'ERROR'}, status)
                                    return {'FINISHED'} # what should be returned when error was encountered?
                            else:
                                print ( "Writing data model as MDL at " + str(os.path.join(sweep_item_path, '%s.main.mdl' % (base_name) )) )
                                cellblender.current_data_model = {'mcell':dm} # this creates two mcell levels: mcell: { mcell: {
                                data_model_to_mdl.write_mdl ( cellblender.current_data_model, os.path.join(sweep_item_path, '%s.main.mdl' % (base_name) ), scene_name=context.scene.name )
                            
                        run_cmd_list.append ( [mcell_binary, sweep_item_path, base_name, error_file_option, log_file_option, seed] )
                    # Increment the current_index counters from rightmost side (deepest directory)
                    i = len(sweep_list) - 1
                    while i >= 0:
                        sweep_list[i]['current_index'] += 1
                        if sweep_list[i]['current_index'] >= len(sweep_list[i]['values']):
                          sweep_list[i]['current_index'] = 0
                        else:
                          break
                        i += -1


                # Print the run commands as a record of what's being done
                print ( "Run Cmds for Sweep Queue (0:mcell, 1:wd, 2:base_name, 3:error, 4:log, 5:seed):" )
                for run_cmd in run_cmd_list:
                    print ( "  " + str(run_cmd) )

                bionetgen_mode = data_model_to_mdl.requires_mcellr ( {'mcell':dm} )

                if run_sim.run_requested:
                    processes_list = run_sim.processes_list
                    #for seed in range(start_seed,end_seed + 1):
                    for run_cmd in run_cmd_list:
                      processes_list.add()
                      run_sim.active_process_index = len(run_sim.processes_list) - 1
                      simulation_process = processes_list[run_sim.active_process_index]

                      print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
                      engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
                      with open(os.path.join(project_files_path(),"start_time.txt"), "w") as start_time_file:
                          start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

                      # Log filename will be log.year-month-day_hour:minute_seed.txt
                      # (e.g. log.2013-03-12_11:45_1.txt)
                      time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

                      if error_file_option == 'file':
                          error_filename = "error.%s_%d.txt" % (time_now, seed)  # Note: this is insufficiently unique for sweeps
                      elif error_file_option == 'none':
                          error_file = subprocess.DEVNULL
                      elif error_file_option == 'console':
                          error_file = None

                      if log_file_option == 'file':
                          log_filename = "log.%s_%d.txt" % (time_now, seed)  # Note: this is insufficiently unique for sweeps
                      elif log_file_option == 'none':
                          log_file = subprocess.DEVNULL
                      elif log_file_option == 'console':
                          log_file = None

                      if not mcell4_mode and bionetgen_mode:
                          # execute mdlr2mdl.py to generate MDL from MDLR

                          mdlr_cmd = os.path.join ( ext_path, 'mdlr2mdl.py' )
                          mdlr_args = [ cellblender.python_path, mdlr_cmd, '-ni', 'Scene.mdlr', '-o', 'Scene' ]
                          wd = run_cmd[1]
                          print ( "\n\nConverting MDLR to MDL by running " + str(mdlr_args) + " from " + str(wd) )
                          #p = subprocess.Popen(mdlr_args, cwd = wd)
                          # The previous seemed to fail. Try this:
                          print ( "\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" )
                          with subprocess.Popen(mdlr_args, env=my_env, cwd=wd, stdout=subprocess.PIPE) as pre_proc:
                              pre_proc.wait()
                              print ( "\n\nProcess Finished from Operator with:\n" + str(pre_proc.stdout.read().decode('utf-8')) + "\n\n" )
                          print ( "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n" )
                          print ( "Done " + str(mdlr_args) + " from " + str(wd) )

                          mcellr_args = None
                          if True:
                            # TODO This is sending as a list (the new way)
                            mcellr_args = [ os.path.join(ext_path, "mcell3r.py"), '-s', str(run_cmd[5]), '-r', 'Scene.mdlr_rules.xml', '-m', 'Scene.main.mdl' ]
                            if len(mcell.initialization.command_options) > 0:
                              mcellr_args.append ( mcell.initialization.command_options.split() ) # Split by spaces
                          else:
                            # TODO This is sending as a string (the old way)
                            # Passing mcellr_args as a list seemed to cause problems ... try as a string instead ...
                            # mcellr_args = [ os.path.join(ext_path, "mcell3r.py"), '-s', str(run_cmd[5]), '-r', 'Scene.mdlr_rules.xml', '-m', 'Scene.main.mdl' ]
                            mcellr_args = os.path.join(ext_path, "mcell3r.py") + ' -s ' + str(run_cmd[5]) + ' -r ' + 'Scene.mdlr_rules.xml' + ' -m ' + 'Scene.main.mdl'
                            if len(mcell.initialization.command_options) > 0:
                              mcellr_args = mcellr_args + " " + mcell.initialization.command_options

                          make_texts = run_sim.save_text_logs
                          print ( 100 * "@" )
                          print ( "Add Task:" + cellblender.python_path + " args:" + str(mcellr_args) + " wd:" + str(run_cmd[1]) + " txt:" + str(make_texts) )
                          proc = cellblender.simulation_queue.add_task([cellblender.python_path], mcellr_args, run_cmd[1], make_texts, env=my_env)
                          print ( 100 * "@" )
                      elif not mcell4_mode:

                          mdl_filename = '%s.main.mdl' % (run_cmd[2])
                          mcell_args = '-seed %d %s' % (run_cmd[5], mdl_filename)
                          if len(mcell.initialization.command_options) > 0:
                            mcell_args = mcell_args + " " + mcell.initialization.command_options
                          make_texts = run_sim.save_text_logs
                          print ( 100 * "@" )
                          print ( "Add Task:" + run_cmd[0] + " args:" + str(mcell_args) + " wd:" + str(run_cmd[1]) + " txt:" + str(make_texts) )
                          proc = cellblender.simulation_queue.add_task(run_cmd[0], mcell_args, run_cmd[1], make_texts, env=my_env)
                          print ( 100 * "@" )
                      else:
                          # mcell4
                          # (0:mcell, 1:wd, 2:base_name, 3:error, 4:log, 5:seed)
                          py_filename = '%s_model.py' % (run_cmd[2])
                          mcell_args = '%s -seed %d' % (py_filename, run_cmd[5])
                          make_texts = run_sim.save_text_logs
                          my_env['MCELL_DIR'] = os.path.dirname(mcell_binary)
                          proc = cellblender.simulation_queue.add_task(python_path, mcell_args, run_cmd[1], make_texts, env=my_env)

                      self.report({'INFO'}, "Simulation Running")

                      if not simulation_process.name:
                          simulation_process.name = ("PID: %d, Seed: %d" % (proc.pid, run_cmd[5]))
                    bpy.ops.mcell.percentage_done_timer()


        else:
            status = "Python not found. Set it in Project Settings."

        run_sim.status = status

        print ( "+++++++++++++ Exit: mcell.run_simulation_sweep_queue +++++++++++++" )

        return {'FINISHED'}





class MCELL_OT_run_simulation_control_sweep_sge (bpy.types.Operator):
    bl_idname = "mcell.run_simulation_sweep_sge"
    bl_label = "Run MCell Simulation Using Sweep SGE"
    bl_description = "Run MCell Simulation Sweep SGE"
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
                    os.makedirs(sweep_dir, exist_ok=True)

                mcell_dm = mcell.build_data_model_from_properties ( context, geometry=True, scripts=True, dyn_geo=True )
                data_model.save_data_model_to_json_file ( mcell_dm, os.path.join(project_dir,"data_model.json") )

                base_name = mcell.project_settings.base_name


                if run_sim.export_requested:
                    # The export checking logic is broken for sweep runs that don't have a main MDL file at the top.
                    # Rather than muck with that right now, just create a dummy file to signal that it's been exported.
                    ##################################################################
                    main_mdl = mcell_files_path()
                    main_mdl = os.path.join(main_mdl, "output_data")
                    main_mdl = os.path.join(main_mdl, base_name + ".main.mdl")
                    main_mdl_file = open(main_mdl, "w", encoding="utf8", newline="\n")
                    main_mdl_file.write ( "/* This file is written to signal to CellBlender that the project has been exported. */" )
                    main_mdl_file.close()
                    ##################################################################


                error_file_option = run_sim.error_file
                log_file_option = run_sim.log_file
                script_dir_path = os.path.dirname(os.path.realpath(__file__))

                # The following Python program will create the "data_layout.json" file describing the directory structure
                script_file_path = os.path.join(script_dir_path, os.path.join("mdl", "run_data_model_mcell.py") )

                processes_list = run_sim.processes_list
                processes_list.add()
                run_sim.active_process_index = len(run_sim.processes_list) - 1
                simulation_process = processes_list[run_sim.active_process_index]

                print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
                engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
                with open(os.path.join(project_files_path(),"start_time.txt"), "w") as start_time_file:
                    start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

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



                sweep_list = engine_manager.build_sweep_list( mcell_dm['parameter_system'] )
                print ( "Sweep list = " + str(sweep_list) )
                # Count the number of sweep runs
                num_sweep_runs = engine_manager.count_sweep_runs ( sweep_list )
                num_requested_runs = num_sweep_runs * (1 + end - start)

                if num_requested_runs <= 1:
                    simulation_process.name = ("PID: %d, Seed: %d" % (sp.pid, start))
                else:
                    simulation_process.name = ("PID: %d, %d Runs with Seeds: %d-%d" % (sp.pid, num_requested_runs, start, end))
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
        if not mcell.cellblender_preferences.mcell_binary_valid:
            print ( "cellblender_simulation.MCELL_OT_run_simulation_control_normal: invalid binary: " + str(binary_path) )

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
                    os.makedirs(react_dir, exist_ok=True)

                viz_dir = os.path.join(project_dir, "output_data", "viz_data")
                if (os.path.exists(viz_dir) and
                        run_sim.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir, exist_ok=True)

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

                print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
                engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
                with open(os.path.join(project_files_path(), "start_time.txt"), "w") as start_time_file:
                    start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

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
        ext_path = os.path.dirname(os.path.realpath(mcell_binary))

        # Set environment variable for the shared library path
        my_env = os.environ.copy()
        if (sys.platform == 'darwin'):
          if my_env.get('DYLD_LIBRARY_PATH'):
            my_env['DYLD_LIBRARY_PATH']=os.path.join(ext_path,'lib') + os.pathsep + my_env['DYLD_LIBRARY_PATH']
          else:
            my_env['DYLD_LIBRARY_PATH']=os.path.join(ext_path,'lib')
        else:
          if my_env.get('LD_LIBRARY_PATH'):
            my_env['LD_LIBRARY_PATH']=os.path.join(ext_path,'lib') + os.pathsep + my_env['LD_LIBRARY_PATH']
          else:
            my_env['LD_LIBRARY_PATH']=os.path.join(ext_path,'lib')


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
                    os.makedirs(react_dir, exist_ok=True)

                viz_dir = os.path.join(project_dir, "output_data", "viz_data")
                if (os.path.exists(viz_dir) and
                        run_sim.remove_append == 'remove'):
                    shutil.rmtree(viz_dir)
                if not os.path.exists(viz_dir):
                    os.makedirs(viz_dir, exist_ok=True)

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

                  print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
                  engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
                  with open(os.path.join(project_files_path(), "start_time.txt"), "w") as start_time_file:
                      start_time_file.write("Started simulation at: " + (str(time.ctime())) + "\n")

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
                  proc = cellblender.simulation_queue.add_task(mcell_binary, mcell_args, os.path.join(project_dir, "output_data"), make_texts, env=my_env)

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
        if active_index < len(processes_list):
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
        if active_index < len(processes_list):
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

    @classmethod
    def poll(self,context):
        task_dict = cellblender.simulation_queue.task_dict
        for pid in task_dict.keys():
            q_item = task_dict[pid]
            if (q_item['status'] == 'running') or (q_item['status'] == 'queued'):
                return True

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
            status = "Error: function \"prepare_runs...\" not found in selected engine"

        if len(status) == 0:
            print ( "Update start time" )

            print("Starting MCell ... create " + project_files_path() + "/start_time.txt file:")
            engine_manager.makedirs_exist_ok ( project_files_path(), exist_ok=True )
            with open(os.path.join(project_files_path(), "start_time.txt"), "w") as start_time_file:
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
                os.makedirs(react_dir, exist_ok=True)

            print ( "Remove old viz data and make new directories" )
            viz_dir = os.path.join(project_dir, "output_data", "viz_data")
            if os.path.exists(viz_dir) and (mcell.run_simulation.remove_append == 'remove'):
                shutil.rmtree(viz_dir)
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir, exist_ok=True)

            # The following line will create the "data_layout.json" file describing the directory structure
            # It would probably be better for the actual engine to do this, but put it here for now...
            print ( "Write the default data layout" )
            engine_manager.write_default_data_layout(project_dir, start, end)

            script_dir_path = os.path.dirname(os.path.realpath(__file__))
            script_file_path = os.path.join(script_dir_path, "sim_engines")

            if "run_engine" in dir(active_runner_module):
                print ( "Selected Runner supports running the engine directly ... so pass the engine." )
                dm = mcell.build_data_model_from_properties ( context, geometry=True, scripts=True )
                active_runner_module.run_engine ( active_engine_module, dm, project_dir )

            else:
                command_list = None
                dm = None
                print ( "Calling prepare_runs... in active_engine_module" )
                if 'prepare_runs_no_data_model' in dir(active_engine_module):
                    command_list = active_engine_module.prepare_runs_no_data_model ( project_dir )
                elif 'prepare_runs_data_model_no_geom' in dir(active_engine_module):
                    dm = mcell.build_data_model_from_properties ( context, geometry=False, scripts=True )
                    command_list = active_engine_module.prepare_runs_data_model_no_geom ( dm, project_dir )
                elif 'prepare_runs_data_model_full' in dir(active_engine_module):
                    dm = mcell.build_data_model_from_properties ( context, geometry=True, scripts=True )
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


# The status can be one of: 'queued', 'running', 'completed', 'mcell_error', 'died'

class MCELL_OT_clear_run_list(bpy.types.Operator):
    bl_idname = "mcell.clear_run_list"
    bl_label = "Clear Completed MCell Runs"
    bl_description = ("Clear the list of completed and failed MCell runs. "
                      "Does not remove rxn/viz data.")
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self,context):
        task_dict = cellblender.simulation_queue.task_dict
        for pid in task_dict.keys():
            q_item = task_dict[pid]
            if (q_item['status'] == 'completed') or (q_item['status'] == 'died') or (q_item['status'] == 'mcell_error'):
                return True

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

    @classmethod
    def poll(self,context):
        task_dict = cellblender.simulation_queue.task_dict
        for pid in task_dict.keys():
            q_item = task_dict[pid]
            if (q_item['status'] == 'completed') or (q_item['status'] == 'died') or (q_item['status'] == 'mcell_error'):
                return True

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
    # These sometimes create a Blender context exception.
    # The try/catch just ensures that both have a chance.
    try:
      bpy.ops.mcell.clear_run_list()
    except:
      print ( "Warning from sim_runner_changed_callback: unable to clear run list" )
      pass
    try:
      bpy.ops.mcell.clear_simulation_queue()
    except:
      print ( "Warning from sim_runner_changed_callback: unable to clear simulation queue" )
      pass


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



class MCellRunSimulationPropertyGroup(bpy.types.PropertyGroup):
    enable_python_scripting = BoolProperty ( name='Enable Python Scripting', default=False )  # Intentionally not in the data model
    sge_host_name = StringProperty ( default="", description="Name of Grid Engine Scheduler" )
    sge_email_addr = StringProperty ( default="", description="Email address for notifications" )
    computer_list = CollectionProperty(type=MCellComputerProperty, name="Computer List")
    required_memory_gig = FloatProperty(default=2.0, description="Minimum memory per job - used for selecting hosts")
    required_free_slots = IntProperty(default=1, description="Minimum free slots for selecting hosts")
    active_comp_index = IntProperty(name="Active Computer Index", default=0)

    show_run_once_options = BoolProperty ( name='Run Once Options', default=False )
    enable_run_once_script = BoolProperty ( name='Enable Run Once Script', default=False )

    internal_external_enum = [
        ('internal', "Internal", ""),
        ("external", "External",  "")]
    internal_external = bpy.props.EnumProperty(
        items=internal_external_enum, name="Internal/External",
        default='internal',
        description="Choose location of file (internal text or external file).")


    dm_run_once_internal_fn = StringProperty ( name = "Internal File Name" )
    dm_run_once_external_fn = StringProperty ( name = "External File Name", subtype='FILE_PATH', default="" )

    export_requested = BoolProperty(name="Export Requested", default=True)
    run_requested = BoolProperty(name="Run Requested", default=True)

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

    save_text_logs = BoolProperty ( name='Save Text Logs', default=False, description="Create a text log for each run" )

    # This would be better as a double, but Blender would store as a float which doesn't have enough precision to resolve time in seconds from the epoch.
    last_simulation_run_time = StringProperty ( default="-1.0", description="Time that the simulation was last run" )

    text_update_timer_delay = FloatProperty ( name='Text Update Interval (s)', default=0.5, description="Text update timer delay" )
    print_timer_ticks = BoolProperty ( name='Print Timer Ticks', default=False, description="Print a message for each timer tick" )

    simulation_engine_and_run_enum = [
         ('SWEEP_QUEUE', "MCell Local", ""),
         ('SWEEP_SGE', "MCell SGE", ""),
         ('QUEUE', "MCell via Queue Runner", ""),       # This should be commented out once the SWEEP_QUEUE is working with Dynamic Geometry
         #('COMMAND', "MCell via Command Line", ""),
         #('SWEEP', "MCell via Sweep Runner", ""),
         ('DYNAMIC', "Engine/Runner (Experimental)", "") ]

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
        dm['data_model_version'] = "DM_2017_11_22_1617"
        dm['name'] = self.name
        dm['start_seed'] = self.start_seed.get_expr()
        dm['end_seed'] = self.end_seed.get_expr()
        dm['run_limit'] = self.run_limit.get_expr()
        dm['export_format'] = context.scene.mcell.export_project.export_format
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

        if dm['data_model_version'] == "DM_2017_08_10_1657":
            # Add the export format. This hadn't been part of the data model, but is needed for export.
            # The default actually depends on the engine, but had traditionally defaulted to modular:
            dm['export_format'] = 'mcell_mdl_modular'
            dm['data_model_version'] = "DM_2017_11_22_1617"

        if dm['data_model_version'] != "DM_2017_11_22_1617":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )
            return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2017_11_22_1617":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellRunSimulationPropertyGroup data model to current version." )

        self.enable_python_scripting = False  # Explicitly disable this when building from a data model
        if 'name' in dm:
            self.name = dm["name"]
        print ( "Setting start and end seeds to " + dm['start_seed'] + " and " + dm['end_seed'] )
        print ( "Setting the run limit to " + dm['run_limit'] )
        self.start_seed.set_expr ( dm["start_seed"] )
        self.end_seed.set_expr ( dm["end_seed"] )
        self.run_limit.set_expr ( dm["run_limit"] )
        context.scene.mcell.export_project.export_format = dm['export_format']
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

    def draw_layout_run_once_dm_script ( self, context, layout ):

        scripting = context.scene.mcell.scripting
        #check_scripting(self, context)
        #update_available_scripts ( scripting )

        box = layout.box()
        row = box.row()
        row.alignment = 'LEFT'
        if self.show_run_once_options:
            col = row.column()
            col.prop(self, "show_run_once_options", icon='TRIA_DOWN', text="", emboss=False)
        else:
            col = row.column()
            col.prop(self, "show_run_once_options", icon='TRIA_RIGHT', text="", emboss=False)

        col = row.column()
        col.prop ( self, "enable_run_once_script", text="" )
        col = row.row()

        if (self.internal_external == "internal"):

            col.prop_search ( self, "dm_run_once_internal_fn",
                              context.scene.mcell.scripting, "internal_python_scripts_list",
                              text="Upon Export", icon='TEXT' )

            col.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")

        if (self.internal_external == "external"):

            col.prop (        self, "dm_run_once_external_fn",
                              text="Upon Export" )
            col.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")

        if self.show_run_once_options:
          row = box.row()
          row.prop ( self, "internal_external", text="" )

        # row.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")
        pass

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

            self.draw_layout_run_once_dm_script ( context, layout )

            row = layout.row()

            # Only allow the simulation to be run if both an MCell binary and a
            # project dir have been selected. There also needs to be a main mdl
            # file present.
            if (not cellblender_utils.get_mcell_path(mcell)) and mcell.cellblender_preferences.require_mcell:
                # The "require_mcell" preference is defaulted to true which will require a valid mcell path
                row.label(text="Set an MCell binary in CellBlender - Preferences Panel", icon='ERROR')
            elif not os.path.dirname(bpy.data.filepath):
                row.label(text="Open or save a .blend file to set the project directory", icon='ERROR')
            elif (not os.path.isfile(main_mdl) and mcell.cellblender_preferences.decouple_export_run):
                row.label(text="Export the project or uncheck \"Decouple Export and Run\" below.", icon='ERROR')
                row = layout.row()
                if self.simulation_run_control in [ "QUEUE" ]:
                    # Use the old Export operator
                    row.operator("mcell.export_project", text="Export CellBlender Project", icon='EXPORT')
                else:
                    # Use the new Export operator
                    row.operator("mcell.dm_export_mdl", text="Export CellBlender Project", icon='EXPORT')
                # Give the user a chance to turn this off!!!
                #   The check for "not os.path.isfile(main_mdl)" will fail when exporting a swept model.
                #   It will fail because there is no "main_mdl" file ... there are lots of them.
                #   We should probably not be hiding an entire panel just because there's no main MDL file.
                #   This switch is a quick (but not very graceful) way out of this problem.
                row = layout.row()
                row.prop(mcell.cellblender_preferences, "decouple_export_run")
            else:

                row = layout.row(align=True)
                if mcell.cellblender_preferences.decouple_export_run:
                    if mcell.cellblender_preferences.lockout_export:
                        # The lockout indicates that the MDL should not be over-written (likely hand edited)
                        # The poll function should be returning False to "gray out" this option
                        if self.simulation_run_control in [ "QUEUE" ]:
                            # Use the old Export operator
                            row.operator("mcell.export_project", text="Export CellBlender Project", icon='CANCEL')
                        else:
                            # Use the new Export operator
                            row.operator("mcell.dm_export_mdl", text="Export CellBlender Project", icon='CANCEL')
                    else:
                        # Show the export as enabled
                        # The poll function should be returning true to show this option as available
                        if self.simulation_run_control in [ "QUEUE" ]:
                            # Use the old Export operator
                            row.operator("mcell.export_project", text="Export CellBlender Project", icon='EXPORT')
                        else:
                            # Use the new Export operator
                            row.operator( "mcell.dm_export_mdl", text="Export CellBlender Project", icon='EXPORT')
                    # Show the run operator as available (always available when exporting is locked out)
                    row.operator("mcell.run_simulation", text="Run", icon='COLOR_RED')
                else:
                    if mcell.cellblender_preferences.lockout_export:
                        # The lockout indicates that the MDL should not be over-written (likely hand edited)
                        # The poll function should be returning False to "gray out" this combined export/run option
                        row.operator("mcell.run_simulation", text="Export & Run", icon='CANCEL')
                    else:
                        # Show the export as enabled
                        # The poll function should be returning true to show this export/run option as available
                        row.operator("mcell.run_simulation", text="Export & Run", icon='COLOR_RED')

                # This is just for testing and verification that the flags are being set properly ... TODO: delete eventually.
                #if not ( self.simulation_run_control in [ "QUEUE" ] ):
                #    row = layout.row(align=True)
                #    col = row.column()
                #    col.prop ( self, "export_requested" )
                #    col = row.column()
                #    col.prop ( self, "run_requested" )

                display_queue_panel = False

                if self.simulation_run_control in [ "QUEUE", "SWEEP_QUEUE" ]:
                    display_queue_panel = True
                elif self.simulation_run_control == 'DYNAMIC':
                    global active_engine_module
                    global active_runner_module
                    if active_engine_module == None:
                        pass
                    elif active_runner_module == None:
                        pass
                    elif 'get_pid' in dir(active_runner_module):
                        display_queue_panel = True

                if display_queue_panel:
                    # print ( "Drawing the Queue Panel" )

                    if True or (self.processes_list and cellblender.simulation_queue.task_dict):
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

                    row = layout.row()
                    col = row.column()
                    global showing_text
                    if not showing_text:
                      col.operator("mcell.show_text_overlay", icon='RESTRICT_VIEW_OFF')
                    else:
                      col.operator("mcell.hide_text_overlay", icon='RESTRICT_VIEW_ON')
                    col = row.column()
                    col.operator("mcell.page_overlay_hm", icon='SOLO_OFF')
                    col = row.column()
                    col.operator("mcell.page_overlay_up", icon='TRIA_UP')
                    col = row.column()
                    col.operator("mcell.page_overlay_dn", icon='TRIA_DOWN')


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

