import subprocess
import sys
import os
import pickle
import math
import random
import array
import shutil

print ( "Executing Smoldyn Simulation" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "SMOLDYN248"
plug_name = "Prototype Smoldyn 2.48 Simulation"

smoldyn_files_dir = ""
project_files_dir = ""

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


def postprocess():
  global parameter_dictionary
  global smoldyn_files_dir
  global project_files_dir
  print ( "Postprocess was called with Smoldyn files at " + str(smoldyn_files_dir) )
  print ( "Postprocess was called for CellBlender files " + str(project_files_dir) )
  f1 = open ( os.path.join ( smoldyn_files_dir, 'run1', 'viz_data.txt' ) )
  f2 = open ( os.path.join ( smoldyn_files_dir, 'run1', 'viz_data2.txt' ) )
  f1d = f1.read()
  f2d = f2.read()
  f1s = [ l for l in f1d.split('\n') if len(l) > 0 ]
  f2s = [ l for l in f2d.split('\n') if len(l) > 0 ]

  # Convert each string to a list that includes the molecule name at the end
  n = min(len(f1s),len(f2s))
  full_list = []
  for i in range(n):
    l = f2s[i].strip().split()
    l.append ( f1s[i][0:f1s[i].index('(')] )
    full_list.append ( l )

  first_iteration = int(full_list[0][0])
  last_iteration = int(full_list[-1][0])
  iter_list = sorted(set([ int(l[0]) for l in full_list]))

  frame_dict = {}
  for k in iter_list:
    frame_dict[k] = {}

  for l in full_list:
    i = int(l[0])
    mol = l[-1]
    if not mol in frame_dict[i]:
      frame_dict[i][mol] = []
    frame_dict[i][mol].append ( [ l[3], l[4], l[5] ] )

  # The frame_dict is now organized to use for writing molecule files

  ndigits = 1 + math.log(last_iteration+1,10)
  file_name_template = "Scene.cellbin.%%0%dd.dat" % ndigits


  react_dir = os.path.join(project_files_dir, "output_data", "react_data")

  if os.path.exists(react_dir):
      shutil.rmtree(react_dir,ignore_errors=True)
  if not os.path.exists(react_dir):
      os.makedirs(react_dir)

  viz_dir = os.path.join(project_files_dir, "output_data", "viz_data")

  if os.path.exists(viz_dir):
      shutil.rmtree(viz_dir,ignore_errors=True)
  if not os.path.exists(viz_dir):
      os.makedirs(viz_dir)

  run_seed = 1
  seed_dir = "seed_%05d" % run_seed

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


  for i in iter_list:
    frame = frame_dict[i]

    # Write the viz data (every iteration for now)
    viz_file_name = file_name_template % i
    viz_file_name = os.path.join(viz_seed_dir,viz_file_name)
    #if (i % print_every) == 0:
    #  if output_detail > 0: print ( "File = " + viz_file_name )
    f = open(viz_file_name,"wb")
    int_array = array.array("I")   # Marker indicating a binary file
    int_array.fromlist([1])
    int_array.tofile(f)
    for mol_name in frame.keys():
      f.write(bytearray([len(mol_name)]))        # Number of bytes in the name
      for ni in range(len(mol_name)):
        f.write(bytearray([ord(mol_name[ni])]))  # Each byte of the name
      f.write(bytearray([0]))                    # Molecule Type, 1=Surface, 0=Volume?

      # Write out the total number of values for this molecule species
      int_array = array.array("I")
      #int_array.fromlist([3*len(m['instances'])])
      int_array.fromlist([3*len(frame[mol_name])])
      int_array.tofile(f)
      
      for mi in frame[mol_name]:
        x = float(mi[0])
        y = float(mi[1])
        z = float(mi[2])
        mol_pos = array.array("f")
        mol_pos.fromlist ( [ x, y, z ] )
        mol_pos.tofile(f)
    f.close()

  #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})



# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'Smoldyn Path': {'val': "/home/bobkuczewski/proj/MCell/smoldyn/smoldyn-2.48/cmake/smoldyn", 'as':'filename', 'desc':"Optional Path", 'icon':'SCRIPTWIN'},
  'Command Line': {'val': "", 'desc':"Additional Command Line Parameters"},
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)", 'icon':'INFO'},
  'Postprocess': {'val': postprocess, 'desc':"Postprocess the data for CellBlender"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Smoldyn Path'],
  ['Command Line'],
  ['Output Detail (0-100)'],
  ['Postprocess', 'Reset']
]

def prepare_runs ( data_model=None, data_layout=None ):
  # Return a list of run command dictionaries.
  # Each run command dictionary must contain a "cmd" key and a "wd" key.
  # The cmd key will refer to a command list suitable for popen.
  # The wd key will refer to a working directory string.
  # Each run command dictionary may contain any other keys helpful for post-processing.
  # The run command dictionary list will be passed on to the postprocess_runs function.

  # The data_layout should be a dictionary something like this:

  #  {
  #   "version": 0,
  #   "data_layout": [
  #    ["dir", ["output_data"]],
  #    ["dc_a", [1e-06, 1e-05]],
  #    ["nrel", [100.0, 200.0, 300.0]],
  #    ["file_type", ["react_data", "viz_data"]],
  #    ["SEED", [100, 101]]
  #   ]
  #  }

  # That dictionary describes the directory structure that CellBlender expects to find on the disk

  pass

def run_simulation ( data_model, project_dir ):
  global smoldyn_files_dir
  global project_files_dir
  
  project_files_dir = "" + project_dir

  dm_mol_list = data_model['define_molecules']['molecule_list']
  for m in dm_mol_list:
    print ( "Mol: " + str(m) )

  dm_rel_list = data_model['release_sites']['release_site_list']
  for r in dm_rel_list:
    print ( "Rel: " + str(r) )

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  command_line_options = parameter_dictionary['Command Line']['val']

  if output_detail > 0: print ( "Inside smoldyn248 run_simulation, project_dir=" + project_dir )
  smoldyn_files_dir = os.path.join ( os.path.dirname(project_dir), "smoldyn" )
  if output_detail > 0: print ( "Inside smoldyn248 run_simulation, smoldyn_files_dir=" + smoldyn_files_dir )

  script_dir_path = os.path.dirname(os.path.realpath(__file__))

  if not os.path.exists(str(parameter_dictionary['Smoldyn Path']['val'])):
      print ( "\n\nUnable to run, file does not exist: " + str(parameter_dictionary['Smoldyn Path']['val']) + "\n\n" )
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

      for sim_seed in range(start,end+1):
          if output_detail > 0: print ("Running with seed " + str(sim_seed) )
          
          run_path = os.path.join(smoldyn_files_dir,"run"+str(sim_seed))

          if os.path.exists(run_path):
              shutil.rmtree(run_path,ignore_errors=True)
          if not os.path.exists(run_path):
              os.makedirs(run_path)

          run_file = os.path.join(run_path,"commands.txt")

          if output_detail > 0: print ( "Saving model to Smoldyn file: " + run_file )

          f = open ( run_file, 'w' )
          f.write ( "# Simple bouncing molecules in a 3-D system\n" )
          f.write ( "graphics opengl\n" )
          f.write ( "dim 3\n" )
          f.write ( "boundaries x -2 2 r\n" )
          f.write ( "boundaries y -2 2 r\n" )
          f.write ( "boundaries z -2 2 r\n" )

          f.write ( "species" )
          for m in dm_mol_list:
            f.write ( " " + str(m['mol_name']) )
          f.write ("\n" )

          for m in dm_mol_list:
            f.write ( "difc " + str(m['mol_name']) + " 2\n" )

          for m in dm_mol_list:
            color = m['display']['color']
            f.write ( "color " + str(m['mol_name']) + " " + str(color[0]) + " " + str(color[1]) + " " + str(color[2]) + "\n" )

          f.write ( "time_start 0\n" )
          f.write ( "time_stop 10\n" )
          f.write ( "time_step 0.01\n" )

          for r in dm_rel_list:
            f.write ( "mol " + r['quantity'] + " " + str(r['molecule']) + " " + r['location_x'] + " " + r['location_y'] + " " + r['location_z'] + "\n" )

          f.write ( "output_files viz_data.txt viz_data2.txt\n" )
          f.write ( "output_precision 6\n" )

          f.write ( "cmd E listmols  viz_data.txt\n" )
          f.write ( "cmd E listmols2 viz_data2.txt\n" )

          f.write ( "end_file\n" )
          f.close()

          if output_detail > 0: print ( "Done saving Smoldyn file." )

          command_list = [ str(parameter_dictionary['Smoldyn Path']['val']), run_file ]
          if len(command_line_options) > 0:
            command_list.append(command_line_options)

          command_string = "Command:";
          for s in command_list:
            command_string += " " + s
          if output_detail > 0: print ( "Running with script_dir_path: " + str(script_dir_path) )
          if output_detail > 0: print ( "Running with project_dir: " + str(project_dir) )
          if output_detail > 0: print ( command_string )

          sp = subprocess.Popen ( command_list, cwd=run_path, stdout=None, stderr=None )
          
          print ( "Done running ... copying data from Smoldyn format to CellBlender format" )

def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
