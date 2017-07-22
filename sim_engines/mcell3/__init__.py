import os
import subprocess
import time
import sys
import pickle
import shutil

import cellblender
import cellblender_utils
from cellblender.cellblender_utils import mcell_files_path

import cellblender.sim_engines as engine_manager
import cellblender.sim_runners as runner_manager


from . import data_model_to_mdl_3
from . import run_data_model_mcell_3

print ( "Executing MCell Simulation" )


"""
MCell 3.3 (commit: 7030a99  date: Thu, 19 May 2016 11:14:16 -0400)

Usage: mcell [options] mdl_file_name

  options:
     [-help]                  print this help message
     [-version]               print the program version and exit
     [-fullversion]           print the detailed program version report and exit
     [-seed n]                choose random sequence number (default: 1)
     [-iterations n]          override iterations in mdl_file_name
     [-logfile log_file_name] send output log to file (default: stdout)
     [-logfreq n]             output log frequency
     [-errfile err_file_name] send errors log to file (default: stderr)
     [-checkpoint_infile checkpoint_file_name]   read checkpoint file
     [-checkpoint_outfile checkpoint_file_name]  write checkpoint file
     [-quiet]                 suppress all unrequested output except for errors
     [-with_checks ('yes'/'no', default 'yes')]   performs check of the geometry for coincident walls
"""

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "MCELL3"
plug_name = "MCell 3 with Dynamic Geometry"

def print_info():
    global parameter_dictionary
    print ( 30*'==' + " Engine Parameters " + 30*'==' )
    for k in sorted(parameter_dictionary.keys()):
        print ( "" + k + " = " + str(parameter_dictionary[k]) )
    print ( 30*'==' + "===================" + 30*'==' )
    print ( '\n' )

def print_version():
    global parameter_dictionary
    print_info()
    subprocess.Popen ( [parameter_dictionary['MCell Path']['val'], "-version"] )

def print_full_version():
    global parameter_dictionary
    print_info()
    subprocess.Popen ( [parameter_dictionary['MCell Path']['val'], "-fullversion"] )

def print_help():
    global parameter_dictionary
    print_info()
    subprocess.Popen ( [parameter_dictionary['MCell Path']['val'], "-help"] )



def reset():
    global parameter_dictionary
    print ( "Resetting all Engine Parameters" )
    parameter_dictionary['Log File']['val'] = ""
    parameter_dictionary['Error File']['val'] = ""

# Get data from Blender / CellBlender
import bpy
mcell_path = ""
try:
    mcell_path = bpy.context.scene.mcell.cellblender_preferences.mcell_binary
except:
    mcell_path = ""


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
    'MCell Path': {'val': mcell_path, 'as':'filename', 'desc':"MCell Path", 'icon':'SCRIPTWIN'},
    'Log File': {'val':"", 'as':'filename', 'desc':"Log File name", 'icon':'EXPORT'},
    'Error File': {'val':"", 'as':'filename', 'desc':"Error File name", 'icon':'EXPORT'},
    'Version': {'val': print_version, 'desc':"Print Version"},
    'Full Version': {'val': print_full_version, 'desc':"Print Full Version"},
    'Help': {'val': print_help, 'desc':"Print Help"},
    'Reset': {'val': reset, 'desc':"Reset everything"},
    'Output Detail (0-100)': {'val': 20, 'desc':"Output Detail"}  # This is used below but may not be shown as a user option
}

parameter_layout = [
    ['MCell Path'],
    ['Log File', 'Error File' ],
    ['Version', 'Full Version', 'Help', 'Reset']
]


def prepare_runs_no_data_model ( project_dir ):

    print ( "MCell 3 Engine is preparing runs with no data model!!" )

    command_list = []

    context = bpy.context

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
        print ( "MCell 3 Engine is exporting the project" )
        bpy.ops.mcell.export_project()
        print ( "MCell 3 Engine is done exporting the project" )

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

        base_name = mcell.project_settings.base_name

        error_file_option = mcell.run_simulation.error_file
        log_file_option = mcell.run_simulation.log_file
        script_dir_path = os.path.dirname(os.path.realpath(__file__))

        engine_manager.write_default_data_layout(mcell_files, start, end)

        for sim_seed in range(start,end+1):
            new_command = [ mcell_binary, ("-seed %s" % str(sim_seed)), os.path.join(project_dir, ("%s.main.mdl" % base_name)) ]

            cmd_entry = {}
            cmd_entry['cmd'] = mcell_binary
            cmd_entry['wd'] = project_dir
            cmd_entry['args'] = [ "-seed %s" % str(sim_seed),os.path.join(project_dir, ("%s.main.mdl" % base_name)) ]
            cmd_entry['stdout'] = ""
            cmd_entry['stderr'] = ""
            command_list.append ( cmd_entry )

        """
        sp_list = sim_module.run_commands ( commands, cwd=project_dir )

        for sp in sp_list:
            cellblender.simulation_popen_list.append(sp)


        if ((end - start) == 0):
            simulation_process.name = ("PID: %d, Seed: %d" %
                                        (sp_list[0].pid, start))
        else:
            simulation_process.name = ("PID: %d-%d, Seeds: %d-%d" %
                                        (sp_list[0].pid, sp_list[-1].pid, start, end))

        """
    # mcell.run_simulation.status = status

    print ( "MCell 3 Engine is returning a command list." )

    return ( command_list )


def get_progress_message_and_status ( stdout_txt ):
  progress_message = "?"
  task_complete = False
  # MCell 3.3 iteration lines look like this:
  # Iterations: 40 of 100  (50.8182 iter/sec)
  for i in reversed(stdout_txt.split("\n")):
      if i.startswith("Iterations"):
          last_iter = int(i.split()[1])
          total_iter = int(i.split()[3])
          percent = int((last_iter/total_iter)*100)
          if (last_iter == total_iter) and (total_iter != 0):
              task_complete = True
          progress_message = "MCell3 Dynamic Geometry: %d%%" % (percent)
          break
  return ( progress_message, task_complete )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
