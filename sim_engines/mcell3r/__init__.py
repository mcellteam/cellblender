import os
import subprocess
import sys
import pickle
import shutil

import cellblender
from . import data_model_to_mdl_3r
from . import run_data_model_mcell_3r

print ( "Executing MCellR Simulation" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "MCELLR"
plug_name = "MCell Rules"

def print_info():
  global parameter_dictionary
  global parameter_layout
  print ( 50*'==' )
  print ( "This is a preliminary MCell-R engine." )
  print ( 50*'==' )
  for row in parameter_layout:
    for k in row:
      print ( "" + k + " = " + str(parameter_dictionary[k]) )
  print ( 50*'==' )

def reset():
  global parameter_dictionary
  print ( "Reset was called" )
  parameter_dictionary['Output Detail (0-100)']['val'] = 20

# Get data from Blender / CellBlender
import bpy
mcell_path = ""
bionetgen_path = ""
nfsim_path = ""
try:
  mcell_path = bpy.context.scene.mcell.cellblender_preferences.mcell_binary
except:
  mcell_path = ""


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'MCellR Path':    {'val': mcell_path,     'as':'filename', 'desc':"MCellR Path",    'icon':'FORCE_LENNARDJONES'},
  'BioNetGen Path': {'val': bionetgen_path, 'as':'filename', 'desc':"BioNetGen Path", 'icon':'OUTLINER_DATA_MESH'},
  'NFSim Path':     {'val': nfsim_path,     'as':'filename', 'desc':"NFSim Path",     'icon':'DRIVER'},
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)", 'icon':'INFO'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['MCellR Path'],
  ['BioNetGen Path'],
  ['NFSim Path'],
  ['Output Detail (0-100)'],
  ['Print Information', 'Reset']
]


def prepare_runs ( data_model, project_dir, data_layout=None ):

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "The current MCell-R engine doesn't really support the prepare/run model.\nIt just runs directly." )

  #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

  fs = data_model['simulation_control']['start_seed']
  ls = data_model['simulation_control']['end_seed']

  run_data_model_mcell_3r.run_mcell_sweep(['-pd',project_dir,'-b',parameter_dictionary['MCellR Path']['val'],'-fs',fs,'-ls',ls],data_model={'mcell':data_model})



  # This should return a list of run command dictionaries.
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

  # That last dictionary describes the directory structure that CellBlender expects to find on the disk

  # For now return no commands at all since the run has already taken place
  command_list = []

  if output_detail > 0: print ( "Inside MCellR Engine, project_dir=" + project_dir )

  return ( command_list )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
