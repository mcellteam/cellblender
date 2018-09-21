import os
import subprocess
import sys
import pickle
import shutil

print ( "Executing Proto_Andreas_1" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "PROTO_ANDREAS_1"
plug_name = "Prototype Andreas 1"

def print_info():
  global parameter_dictionary
  print ( "Print from Proto_Andreas_1" )
  print ( 50*'==' )
  for k in sorted(parameter_dictionary.keys()):
    print ( "" + k + " = " + str(parameter_dictionary[k]) )
  print ( 50*'==' )

def reset():
  global parameter_dictionary
  print ( "Reset was called" )
  parameter_dictionary['Output Detail (0-100)']['val'] = 20
  parameter_dictionary['Python Command']['val'] = ""
  parameter_dictionary['Reaction Factor']['val'] = 1.0


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'Electric Species': {'val': "", 'desc':"Names of Electric Field Species (comma separated)"},
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)", 'icon':'INFO'},
  'Python Command': {'val': "", 'as':'filename', 'desc':"Command to run Python (default is python)", 'icon':'SCRIPTWIN'},
  'Reaction Factor': {'val': 1.0, 'desc':"Decay Rate Multiplier", 'icon':'ARROW_LEFTRIGHT'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}


parameter_layout = [
  ['Electric Species'],
  ['Python Command'],
  ['Output Detail (0-100)'],
  ['Reaction Factor'],
  ['Print Information', 'Reset']
]

def prepare_runs_data_model_full ( data_model, project_dir, data_layout=None ):
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

  if output_detail > 0:    print ( "Inside limited_python.prepare_runs, project_dir=" + project_dir )
  if output_detail >= 10:  print ( "  Data Layout = " + str(data_layout) )
  if output_detail >= 50:  print ( "    Data Model = " + str(data_model) )

  electric_species = parameter_dictionary['Electric Species']['val']
  print ( "Electric Species = \"" + electric_species + "\"" )

  python_cmd = parameter_dictionary['Python Command']['val']

  if len(python_cmd) == 0:
      python_cmd = 'python'

  script_file_path = os.path.dirname(os.path.realpath(__file__))
  final_script_path = os.path.join(script_file_path,"minimcell.py")
  final_script_path = os.path.join(script_file_path,"emcell.py")
  final_script_path = os.path.join(script_file_path,"run_sim.py")

  if not os.path.exists(final_script_path):
      print ( "\n\nUnable to prepare runs, script does not exist: " + final_script_path + "\n\n" )
  else:

      # Create a command to use for each simulation and add it to the command_list

      # Get the start and end seeds from the data model (default to 1)
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
          if output_detail > 10: print ("Running with seed " + str(sim_seed) )

          file_name = os.path.join(project_dir,"dm.txt")

          if output_detail > 20: print ( "Saving CellBlender model to file: " + file_name )
          f = open ( file_name, 'w' )
          f.write ( pickle.dumps({'mcell':data_model},protocol=0).decode('latin1') )
          f.close()
          if output_detail > 10: print ( "Done saving CellBlender model." )

          command_dict = { 'cmd': python_cmd,
                           'args': [ final_script_path,
                               "output_detail="+str(parameter_dictionary['Output Detail (0-100)']['val']),
                               "proj_path="+project_dir,
                               "seed="+str(sim_seed),
                               "decay_factor="+str(parameter_dictionary['Reaction Factor']['val']),
                               "data_model=dm.txt" ],
                           'wd': project_dir
                         }
          if len(electric_species) > 0:
            command_dict['args'].append ( "electric_species="+electric_species )

          command_list.append ( command_dict )
          if output_detail > 70: print ( str(command_dict) )

  return ( command_list )


def get_progress_message_and_status ( stdout_txt ):
  progress_message = "?"
  task_complete = False
  # MCell Pure Prototype iteration lines look like this:
  # Iteration 10 of 1000
  for i in reversed(stdout_txt.split("\n")):
      if i.startswith("Iteration "):
          last_iter = int(i.split()[1])
          total_iter = int(i.split()[3])
          percent = int((last_iter/total_iter)*100)
          if (last_iter == total_iter) and (total_iter != 0):
              task_complete = True
          progress_message = "PySim: %d%%" % (percent)
          break
  return ( progress_message, task_complete )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
