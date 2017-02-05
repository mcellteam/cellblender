import os
import subprocess
import sys
import json

print ( "Executing Limited C++ Simulation" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "LIM_CPP"
plug_name = "Prototype C++ Simulation"

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
  'C++ Path': {'val': "", 'as':'filename', 'desc':"Optional Path", 'icon':'SCRIPTWIN'},
  'Decay Factor': {'val': 1.0, 'desc':"Decay Rate Multiplier", 'icon':'ARROW_LEFTRIGHT'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Output Detail (0-100)'],
  ['Print Information', 'Reset']
]

def prepare_runs ( data_model ):
  # Return a list of run command dictionaries.
  # Each run command dictionary must contain a "cmd" key and a "wd" key.
  # The cmd key will refer to a command list suitable for popen.
  # The wd key will refer to a working directory string.
  # Each run command dictionary may contain any other keys helpful for post-processing.
  # The run command dictionary list will be passed on to the postprocess_runs function.
  pass

def run_simulation ( data_model, project_dir ):
  print ( "Inside limited_python.run_simulation, project_dir=" + project_dir )

  script_dir_path = os.path.dirname(os.path.realpath(__file__))
  script_file_path = script_dir_path
  final_script_path = os.path.join(script_file_path,"mcell_main")

  if not os.path.exists(final_script_path):
      print ( "\n\nUnable to run, script does not exist: " + final_script_path + "\n\n" )
  else:

      # Create a subprocess for each simulation
      start = 1
      end = 1
      try:
        start = int(data_model['mcell']['simulation_control']['start_seed'])
        end = int(data_model['mcell']['simulation_control']['end_seed'])
      except Exception as e:
        pass

      for sim_seed in range(start,end+1):
          print ("Running with seed " + str(sim_seed) )
          
          file_name = os.path.join(project_dir,"dm.json")

          print ( "Saving CellBlender model to JSON file: " + file_name )
          f = open ( file_name, 'w' )
          f.write ( json.dumps ( {"mcell": data_model} ) )
          f.close()
          print ( "Done saving CellBlender model." )

          command_list = [ final_script_path,
                           "print_detail="+str(parameter_dictionary['Output Detail (0-100)']['val']),
                           "proj_path="+project_dir,
                           "data_model=dm.json" ]

          command_string = "Command:";
          for s in command_list:
            command_string += " " + s
          print ( command_string )

          sp = subprocess.Popen ( command_list, cwd=script_file_path, stdout=None, stderr=None )

def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
