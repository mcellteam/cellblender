import os
import subprocess
import sys
import pickle
import shutil

import cellblender
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
plug_name = "MCell 3"

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


def prepare_runs_data_model_full ( data_model, project_dir, data_layout=None ):

  """ Arguments to:  run_mcell_sweep ( sys_argv, data_model=None )
    arg_parser = argparse.ArgumentParser(description='Run MCell with appropriate arguments')
    arg_parser.add_argument ( '-dm', '--data_model_file_name',     type=str, default='',        help='the file name of the data model to run' )
    arg_parser.add_argument ( '-pd', '--proj_dir',        type=str, default='',        help='the directory where the program will run' )
    arg_parser.add_argument ( '-b',  '--binary',          type=str, default='mcell',   help='full path of binary file to run' )
    arg_parser.add_argument ( '-fs', '--first_seed',      type=int, default=1,         help='the first seed in a series of seeds to run' )
    arg_parser.add_argument ( '-ls', '--last_seed',       type=int, default=1,         help='the last seed in a series of seeds to run' )
    arg_parser.add_argument ( '-lf', '--log_file_opt',    type=str, default='console', help='the log file option for mcell' )
    arg_parser.add_argument ( '-ef', '--error_file_opt',  type=str, default='console', help='the error file option for mcell' )
    arg_parser.add_argument ( '-np', '--num_processors',  type=int, default=8,         help='the number of processors' )
    arg_parser.add_argument ( '-rl', '--run_limit',       type=int, default=-1,        help='limit the total number of runs' )
    arg_parser.add_argument ( '-rt', '--runner_type',     type=str, default='mpp',     help='run mechanism: mpp or sge (mpp=MultiProcessingPool, sge=SunGridEngine)' )
    arg_parser.add_argument ( '-nl', '--node_list',       type=str, default='',        help='list of comma-separated nodes to run on with SGE' )
    arg_parser.add_argument ( '-mm', '--min_memory',      type=int, default=0,         help='minimum memory in Gigabytes' )
    arg_parser.add_argument ( '-em', '--email_addr',      type=str, default='',        help='email address for notifications of job results' )
    arg_parser.add_argument ( '-gh', '--grid_host',       type=str, default='',        help='grid engine host name' )
  """

  #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

  fs = data_model['simulation_control']['start_seed']
  ls = data_model['simulation_control']['end_seed']

  run_cmd_list = run_data_model_mcell_3.run_mcell_sweep(['-rt','extern','-pd',project_dir,'-b',parameter_dictionary['MCell Path']['val'],'-fs',fs,'-ls',ls],data_model={'mcell':data_model})

  print ( "Run Cmds prepared by the mcell3 engine:" )
  print ( "  = " + str(run_cmd_list) )
  if len(run_cmd_list) > 0:
    for run_cmd in run_cmd_list:
      print ( "  " + str(run_cmd) )

  print ( "Currently running from the engine ..." )

  run_data_model_mcell_3.run_mcell_sweep(['-pd',project_dir,'-b',parameter_dictionary['MCell Path']['val'],'-fs',fs,'-ls',ls],data_model={'mcell':data_model})



  # Return a list of run command dictionaries.
  # Each run command dictionary must contain a "cmd" key, an "args" key, and a "wd" key.
  # The cmd key will refer to a command string suitable for popen.
  # The args key will refer to an argument list suitable for popen.
  # The wd key will refer to a working directory string.
  # Each run command dictionary may contain any other keys helpful for post-processing.
  # The run command dictionary list will be passed on to the postprocess_runs function.

  # The data_layout should be a dictionary something like this:

  #  {
  #   "version": 2,
  #   "data_layout": [
  #    ["/DIR", ["output_data"]],
  #    ["dc_a", [1e-06, 1e-05]],
  #    ["nrel", [100.0, 200.0, 300.0]],
  #    ["/FILE_TYPE", ["react_data", "viz_data"]],
  #    ["/SEED", [100, 101]]
  #   ]
  #  }

  # That dictionary describes the directory structure that CellBlender expects to find on the disk

  command_list = []

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "Inside MCell3 Engine, project_dir=" + project_dir )

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
          progress_message = "MCell3: %d%%" % (percent)
          break
  return ( progress_message, task_complete )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
