import os
import subprocess
import sys
import pickle
import shutil

print ( "Executing Limited Python Simulation" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "LIM_PYTHON"
plug_name = "Prototype Python Simulation"

def print_info():
  global parameter_dictionary
  print ( 50*'==' )
  for k in sorted(parameter_dictionary.keys()):
    print ( "" + k + " = " + str(parameter_dictionary[k]) )
  print ( 50*'==' )

def reset():
  global parameter_dictionary
  print ( "Reset was called" )
  parameter_dictionary['Output Detail (0-100)']['val'] = 20


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)", 'icon':'INFO'},
  'Python Path': {'val': "", 'as':'filename', 'desc':"Optional Path", 'icon':'SCRIPTWIN'},
  'Reaction Factor': {'val': 1.0, 'desc':"Decay Rate Multiplier", 'icon':'ARROW_LEFTRIGHT'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Output Detail (0-100)'],
  ['Reaction Factor'],
  ['Print Information', 'Reset']
]


def prepare_runs ( data_model, project_dir, data_layout=None ):
  # Return a list of run command dictionaries.
  # Each run command dictionary must contain a "cmd" key, an "args" key, and a "wd" key.
  # The cmd key will refer to a command string suitable for popen.
  # The args key will refer to an argument list suitable for popen.
  # The wd key will refer to a working directory string.
  # Each run command dictionary may contain any other keys helpful for post-processing.
  # The run command dictionary list will be passed on to the postprocess_runs function.

  # The data_layout should be a dictionary something like this:

  #  {
  #   "version": 1,
  #   "data_layout": [
  #    ["/", ["output_data"]],
  #    ["dc_a", [1e-06, 1e-05]],
  #    ["nrel", [100.0, 200.0, 300.0]],
  #    ["/", ["react_data", "viz_data"]],
  #    ["SEED", [100, 101]]
  #   ]
  #  }

  # That dictionary describes the directory structure that CellBlender expects to find on the disk

  command_list = []

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "Inside limited_python.prepare_runs, project_dir=" + project_dir )

  script_file_path = os.path.dirname(os.path.realpath(__file__))
  final_script_path = os.path.join(script_file_path,"limited_python_sim.py")

  if not os.path.exists(final_script_path):
      print ( "\n\nUnable to prepare runs, script does not exist: " + final_script_path + "\n\n" )
  else:

      # Create a subprocess for each simulation
      start = 1
      end = 1
      try:
        start = int(data_model['simulation_control']['start_seed'])
        end = int(data_model['simulation_control']['end_seed'])
      except Exception as e:
        print ( "Unable to find the start and/or end seeds in the data model" )
        pass

      # Make all of the directories first to avoid race condition errors in the file system
      for sim_seed in range(start,end+1):

        seed_dir = "seed_%05d" % sim_seed

        react_dir = os.path.join(project_dir, "output_data", "react_data")

        if os.path.exists(react_dir):
            shutil.rmtree(react_dir,ignore_errors=True)
        if not os.path.exists(react_dir):
            os.makedirs(react_dir)

        viz_dir = os.path.join(project_dir, "output_data", "viz_data")

        if os.path.exists(viz_dir):
            shutil.rmtree(viz_dir,ignore_errors=True)
        if not os.path.exists(viz_dir):
            os.makedirs(viz_dir)

        viz_seed_dir = os.path.join(viz_dir, seed_dir)

        if os.path.exists(viz_seed_dir):
            shutil.rmtree(viz_seed_dir,ignore_errors=True)
        if not os.path.exists(viz_seed_dir):
            os.makedirs(viz_seed_dir)

        react_seed_dir = os.path.join(react_dir, seed_dir)
        if os.path.exists(react_seed_dir):
            shutil.rmtree(react_seed_dir,ignore_errors=True)
        if not os.path.exists(react_seed_dir):
            os.makedirs(react_seed_dir)

      # Build the list of commands to be run along with any data files needed
      for sim_seed in range(start,end+1):
          if output_detail > 0: print ("Running with seed " + str(sim_seed) )

          file_name = os.path.join(project_dir,"dm.txt")

          if output_detail > 0: print ( "Saving CellBlender model to file: " + file_name )
          f = open ( file_name, 'w' )
          ##dm = { 'mcell': mcell_dm }
          f.write ( pickle.dumps({'mcell':data_model},protocol=0).decode('latin1') )
          f.close()
          if output_detail > 0: print ( "Done saving CellBlender model." )

          command_dict = { 'cmd': 'python3',
                           'args': [ final_script_path,
                               "output_detail="+str(parameter_dictionary['Output Detail (0-100)']['val']),
                               "proj_path="+project_dir,
                               "seed="+str(sim_seed),
                               "decay_factor="+str(parameter_dictionary['Reaction Factor']['val']),
                               "data_model=dm.txt" ],
                           'wd': project_dir
                         }

          command_list.append ( command_dict )
          if output_detail > 0: print ( str(command_dict) )

  return ( command_list )


def run_simulations ( command_list ):

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "Inside limited_python.run_simulations." )
  if output_detail > 10:
      for cmd in command_list:
          print ( "cmd = " + str(cmd) )

  for cmd in command_list:
      if output_detail > 0: print ( "" )

      cmd_list = [ cmd['cmd'] ]
      for arg in cmd['args']:
        cmd_list.append ( arg )

      sp = subprocess.Popen ( cmd_list, cwd=cmd['wd'], stdout=None, stderr=None )

def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
