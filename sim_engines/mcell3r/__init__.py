import os
import subprocess
import sys
import pickle
import shutil

import cellblender
from . import data_model_to_mdl_3r
from . import run_data_model_mcell_3r

# from . import mdlr2mdl

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

# Force some defaults which would otherwise be empty (""):
shared_path = os.path.dirname(__file__)
mcell_path = "mcell/build/mcell"
mcell_lib_path = "mcell/lib/"
bionetgen_path = "bionetgen/bng2/BNG2.pl"
nfsim_path = ""


project_files_dir = ""
start_seed = 1
end_seed = 1

#try:
#  mcell_path = bpy.context.scene.mcell.cellblender_preferences.mcell_binary
#except:
#  mcell_path = ""


def postprocess():
  global parameter_dictionary
  print ( "Postprocess called" )

  mcellr_react_dir = os.path.join(project_files_dir, "output_data")

  react_dir = os.path.join(project_files_dir, "output_data", "react_data")

  if os.path.exists(react_dir):
      shutil.rmtree(react_dir,ignore_errors=True)
  if not os.path.exists(react_dir):
      os.makedirs(react_dir)

  react_dir = os.path.join(project_files_dir, "output_data", "react_data")

  if os.path.exists(react_dir):
      shutil.rmtree(react_dir,ignore_errors=True)
  if not os.path.exists(react_dir):
      os.makedirs(react_dir)


  for run_seed in range(start_seed, end_seed+1):
    print ( "  Postprocessing for seed " + str(run_seed) )

    seed_dir = "seed_%05d" % run_seed

    react_seed_dir = os.path.join(react_dir, seed_dir)

    if os.path.exists(react_seed_dir):
        shutil.rmtree(react_seed_dir,ignore_errors=True)
    if not os.path.exists(react_seed_dir):
        os.makedirs(react_seed_dir)


    # Read the MCellR data file and split into a list of rows where each row is a list of columns
    mcellr_react_file = open ( os.path.join ( mcellr_react_dir, 'Scene.mdlr_total.xml.gdat' ) )
    all_react_data = mcellr_react_file.read()
    react_data_all = [ [t.strip() for t in s.split(',') if len(t.strip()) > 0] for s in all_react_data.split('\n') if len(s) > 0 ]
    react_data_header = react_data_all[0]
    react_data_rows = react_data_all[1:]

    for col in range(1,len(react_data_header)):
      out_file_name = os.path.join ( react_seed_dir, react_data_header[col] + ".dat" )
      print ( "Writing data to " + out_file_name )
      f = open(out_file_name,"w")
      for row in react_data_rows:
        print ( "  " + row[0] + " " + row[col] )
        f.write ( row[0] + " " + row[col] + '\n' )
      f.close()

    #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})


  print ( "Done postrocessing MCellR Reaction Output" )


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'Shared Path':    {'val': shared_path,    'as':'filename', 'desc':"Shared Path",         'icon':'FORCE_LENNARDJONES'},
  'MCellR Path':    {'val': mcell_path,     'as':'filename', 'desc':"MCellR Path",         'icon':'FORCE_LENNARDJONES'},
  'MCellRlib Path': {'val': mcell_lib_path, 'as':'filename', 'desc':"MCellR Library Path", 'icon':'FORCE_LENNARDJONES'},
  'BioNetGen Path': {'val': bionetgen_path, 'as':'filename', 'desc':"BioNetGen Path",      'icon':'OUTLINER_DATA_MESH'},
  #'NFSim Path':     {'val': nfsim_path,     'as':'filename', 'desc':"NFSim Path",          'icon':'DRIVER'},
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)",    'icon':'INFO'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Postprocess': {'val': postprocess, 'desc':"Postprocess the data for CellBlender"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Shared Path'],
  ['MCellR Path'],
  ['MCellRlib Path'],
  ['BioNetGen Path'],
  #['NFSim Path'],
  ['Output Detail (0-100)'],
  ['Print Information', 'Postprocess', 'Reset']
]


def makedirs_exist_ok ( path_to_build, exist_ok=False ):
    # Needed for old python which doesn't have the exist_ok option!!!
    print ( " Make dirs for " + path_to_build )
    parts = path_to_build.split(os.sep)  # Variable "parts" should be a list of subpath sections. The first will be empty ('') if it was absolute.
    # print ( "  Parts = " + str(parts) )
    full = ""
    if len(parts[0]) == 0:
      full = os.sep
    for p in parts:
      full = os.path.join(full,p)
      # print ( "   " + full )
      if not os.path.exists(full):
        os.makedirs ( full, exist_ok=True )

def prepare_runs ( data_model, project_dir, data_layout=None ):

  global project_files_dir

  project_files_dir = "" + project_dir

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "Inside prepare_runs in MCellR Engine, project_dir=" + project_dir )

  if output_detail > 0: print ( "  Note: The current MCell-R engine doesn't support the prepare/run model.\n  It just runs directly." )

  print ( "Running with python " + sys.version )   # This will be Blender's Python which will be 3.5+
  print ( "Project Dir: " + project_dir )          # This will be .../blend_file_name_files/mcell
  print ( "Data Layout: " + str(data_layout) )     # This will typically be None

  output_data_dir = os.path.join ( project_dir, "output_data" )
  makedirs_exist_ok ( output_data_dir, exist_ok=True )

  time_step = '1e-6'  # This is needed as a default for plotting

  f = open ( os.path.join(output_data_dir,"Scene.mdlr"), 'w' )
  if 'initialization' in data_model:
    # Can't write all initialization MDL because booleans like "TRUE" are referenced but not defined in BNGL
    # data_model_to_mdl_3r.write_initialization(data_model['initialization'], f)
    # Write specific parts instead:
    data_model_to_mdl_3r.write_dm_str_val ( data_model['initialization'], f, 'iterations',                'ITERATIONS' )
    data_model_to_mdl_3r.write_dm_str_val ( data_model['initialization'], f, 'time_step',                 'TIME_STEP' )
    data_model_to_mdl_3r.write_dm_str_val ( data_model['initialization'], f, 'vacancy_search_distance',   'VACANCY_SEARCH_DISTANCE', blank_default='10' )

    time_step = data_model['initialization']['time_step']

  f.write ( 'INCLUDE_FILE = "Scene.geometry.mdl"\n' )

  if 'parameter_system' in data_model:
    # Write the parameter system
    data_model_to_mdl_3r.write_parameter_system ( data_model['parameter_system'], f )

  # Note that reflective surface classes may be needed by MCell-R
  # If so, it might be good to automate this rather than explicitly requiring it in CellBlender's model.

  if 'define_surface_classes' in data_model:
    data_model_to_mdl_3r.write_surface_classes(data_model['define_surface_classes'], f)

  if 'modify_surface_regions' in data_model:
    data_model_to_mdl_3r.write_modify_surf_regions ( data_model['modify_surface_regions'], f )

  if 'define_molecules' in data_model:
    mols = data_model['define_molecules']
    if 'molecule_list' in mols:
      mlist = mols['molecule_list']
      if len(mlist) > 0:
        f.write ( "#DEFINE_MOLECULES\n" )
        f.write ( "{\n" )
        for m in mlist:
          f.write ( "  %s" % m['mol_name'] )
          if "bngl_component_list" in m:
            f.write( "(" )
            num_components = len(m['bngl_component_list'])
            if num_components > 0:
              for ci in range(num_components):
                c = m['bngl_component_list'][ci]
                f.write( c['cname'] )
                for state in c['cstates']:
                  f.write ( "~" + state )
                if ci < num_components-1:
                  f.write ( "," )
            f.write( ")" )
          f.write ( "\n" )
          f.write ( "  {\n" )
          if m['mol_type'] == '2D':
            f.write ( "    DIFFUSION_CONSTANT_2D = %s\n" % m['diffusion_constant'] )
          else:
            f.write ( "    DIFFUSION_CONSTANT_3D = %s\n" % m['diffusion_constant'] )
          if 'custom_time_step' in m:
            if len(m['custom_time_step']) > 0:
              f.write ( "    CUSTOM_TIME_STEP = %s\n" % m['custom_time_step'] )
          if 'custom_space_step' in m:
            if len(m['custom_space_step']) > 0:
              f.write ( "    CUSTOM_SPACE_STEP = %s\n" % m['custom_space_step'] )
          if 'target_only' in m:
            if m['target_only']:
              f.write("    TARGET_ONLY\n")
          f.write("  }\n")
        f.write ( "}\n" )
      f.write ( "\n" );

  if 'define_reactions' in data_model:
    reacts = data_model['define_reactions']
    if 'reaction_list' in reacts:
      rlist = reacts['reaction_list']
      if len(rlist) > 0:
        f.write ( "#DEFINE_REACTIONS\n" )
        f.write ( "{\n" )
        for r in rlist:
          f.write("  %s " % (r['name']))
          if r['rxn_type'] == "irreversible":
            if r['variable_rate_switch'] and r['variable_rate_valid']:
              variable_rate_name = r['variable_rate']
              f.write('["%s"]' % (variable_rate_name))
              ## Create the actual variable rate file and write to it
              vrf = open(variable_rate_name, "w")
              vrf.write ( r['variable_rate_text'] )
              #with open(variable_rate_name, "w", encoding="utf8",
              #          newline="\n") as variable_out_file:
              #    variable_out_file.write(r['variable_rate_text'])
            else:
              f.write ( "[%s]" % ( r['fwd_rate'] ) )
          else:
            f.write ( "[%s, %s]" % ( r['fwd_rate'], r['bkwd_rate'] ) )
          if 'rxn_name' in r:
            if len(r['rxn_name']) > 0:
              f.write ( " : %s" % (r['rxn_name']) )
          f.write("\n")
        f.write ( "}\n" )
        f.write("\n")

  if ('model_objects' in data_model) or ('release_sites' in data_model):
    geom = None
    rels = None
    if 'model_objects' in data_model:
      geom = data_model['model_objects']
    if 'release_sites' in data_model:
      rels = data_model['release_sites']
    mols = data_model['define_molecules']
    #TODO Note that the use of "Scene" here is a temporary measure!!!!
    f.write ( "#INSTANTIATE Scene OBJECT\n" )
    f.write ( "{\n" )
    if geom != None:
      if 'model_object_list' in geom:
        glist = geom['model_object_list']
        if len(glist) > 0:
          # Sort the objects by parent
          unsorted_objs = [ g for g in glist ]
          sorted_objs = []
          sorted_obj_names = []
          while len(unsorted_objs) > 0:
            for index in range(len(unsorted_objs)):
              print ( "  Sorting by parent: checking " + unsorted_objs[index]['name'] + " for parent " + unsorted_objs[index]['parent_object'] )
              if len(unsorted_objs[index]['parent_object']) == 0:
                # Move this object to the sorted list because it has no parent
                sorted_obj_names.append ( unsorted_objs[index]['name'])
                sorted_objs.append ( unsorted_objs.pop(index) )
                break
              elif unsorted_objs[index]['parent_object'] in sorted_obj_names:
                # Move this object to the sorted list because its parent is already in the list
                sorted_obj_names.append ( unsorted_objs[index]['name'])
                sorted_objs.append ( unsorted_objs.pop(index) )
                break

          for g in sorted_objs:
            f.write ( "  %s OBJECT %s {\n" % (g['name'], g['name']) )
            if len(g['parent_object']) > 0:
              f.write ( "    PARENT = %s\n" % (g['parent_object']) )
            if len(g['membrane_name']) > 0:
              # f.write ( "    MEMBRANE = %s\n" % (g['membrane_name']) )
              f.write ( "    MEMBRANE = %s OBJECT %s[ALL]\n" % (g['membrane_name'], g['name']) )
            f.write ( "  }\n" )
    if rels != None:
      if 'release_site_list' in rels:
        rlist = rels['release_site_list']
        if len(rlist) > 0:
          for r in rlist:
            f.write ( "  %s RELEASE_SITE\n" % (r['name']) )
            f.write ( "  {\n" )

            # First handle the release shape
            if ((r['shape'] == 'CUBIC') |
                (r['shape'] == 'SPHERICAL') |
                (r['shape'] == 'SPHERICAL_SHELL')):
              # Output MDL for releasing in a non-object shape pattern
              f.write("   SHAPE = %s\n" % (r['shape']))
              f.write("   LOCATION = [%s, %s, %s]\n" % (r['location_x'],r['location_y'],r['location_z']))
              f.write("   SITE_DIAMETER = %s\n" % (r['site_diameter']))
            elif r['shape'] == "OBJECT":
              # Output MDL for releasing in or on and object
              #TODO Note that the use of "Scene." here for object names is a temporary measure!!!!
              obj_expr = r['object_expr']
              obj_expr = '-'.join(["Scene."+t.strip() for t in obj_expr.split('-')])
              # Can't repeat this because the "Scene's" accumulate
              #obj_expr = '+'.join(["Scene."+t.strip() for t in obj_expr.split('+')])
              #obj_expr = '*'.join(["Scene."+t.strip() for t in obj_expr.split('*')])
              f.write("   SHAPE = %s\n" % (obj_expr))

            # Next handle the molecule to be released (maybe the Molecule List should have been a dictionary keyed on mol_name?)
            mlist = mols['molecule_list']
            mol = None
            for m in mlist:
              if m['mol_name'] == r['molecule']:
                mol = m
                break
            f.write("   MOLECULE = %s\n" % (r['molecule']))

            # Now write out the quantity, probability, and pattern

            if r['quantity_type'] == 'NUMBER_TO_RELEASE':
              f.write("   NUMBER_TO_RELEASE = %s\n" % (r['quantity']))
            elif r['quantity_type'] == 'GAUSSIAN_RELEASE_NUMBER':
              f.write("   GAUSSIAN_RELEASE_NUMBER\n")
              f.write("   {\n")
              f.write("        MEAN_NUMBER = %s\n" % (r['quantity']))
              f.write("        STANDARD_DEVIATION = %s\n" % (r['stddev']))
              f.write("      }\n")
            elif r['quantity_type'] == 'DENSITY':
              if mol:
                if mol['mol_type'] == '2D':
                  f.write("   DENSITY = %s\n" % (r['quantity']))
                else:
                  f.write("   CONCENTRATION = %s\n" % (r['quantity']))
            f.write("   RELEASE_PROBABILITY = %s\n" % (r['release_probability']))
            if len(r['pattern']) > 0:
              f.write("   RELEASE_PATTERN = %s\n" % (r['pattern']))

            f.write ( "  }\n" )
    f.write ( "}\n" )
    f.write("\n")


  if 'reaction_data_output' in data_model:
    plot_out = data_model['reaction_data_output']
    rxn_step = time_step  # Default if not otherwise specified in the reaction data output block
    if 'rxn_step' in plot_out:
      if len(plot_out['rxn_step']) > 0:
        rxn_step = plot_out['rxn_step']
    if 'reaction_output_list' in plot_out:
      plist = plot_out['reaction_output_list']
      if len(plist) > 0:
        f.write ( "#REACTION_DATA_OUTPUT\n" )
        f.write ( "{\n" )
        f.write ( "  STEP = %s\n" % rxn_step )
        for p in plist:
          if 'rxn_or_mol' in p:
            if p['rxn_or_mol'] == 'MDLString':
              # Trouble with first two approaches:
              # f.write ( "  { %s } => \"./react_data/seed_\" & seed & \"/%s_MDLString.dat\"\n" % (p['mdl_string'], p['mdl_file_prefix']) )
              # f.write ( "  { %s } => \"./react_data/seed_00001/%s_MDLString.dat\"\n" % (p['mdl_string'], p['mdl_file_prefix']) )
              f.write ( "  { %s } => \"./react_data/%s_MDLString.dat\"\n" % (p['mdl_string'], p['mdl_file_prefix']) )
        f.write ( "}\n" )
        f.write("\n")

  f.write("\n")
  f.write ( "INCLUDE_FILE = \"Scene.viz_output.mdl\"\n\n" )

  f.close()

  f = open ( os.path.join(output_data_dir,"Scene.geometry.mdl"), 'w' )
  data_model_to_mdl_3r.write_geometry(data_model['geometrical_objects'], f)
  f.close()

  f = open ( os.path.join(output_data_dir,"Scene.viz_output.mdl"), 'w' )
  f.write ( 'sprintf(seed,"%05g",SEED)\n\n' )
  data_model_to_mdl_3r.write_viz_out(data_model['viz_output'], data_model['define_molecules'], f)
  f.close()

  f = open ( os.path.join(output_data_dir,"mcellr.yaml"), 'w' )
  f.write ( "bionetgen: '" + os.path.join(parameter_dictionary['Shared Path']['val'],parameter_dictionary['BioNetGen Path']['val']) + "'\n" )
  f.write ( "libpath: '" + os.path.join(parameter_dictionary['Shared Path']['val'],parameter_dictionary['MCellRlib Path']['val']) + "'\n" )
  f.write ( "mcell: '" + os.path.join(parameter_dictionary['Shared Path']['val'],parameter_dictionary['MCellR Path']['val']) + "'\n" )
  f.close()

  # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

  fs = data_model['simulation_control']['start_seed']
  ls = data_model['simulation_control']['end_seed']

  global start_seed
  global end_seed
  start_seed = int(fs)
  end_seed = int(ls)

  engine_path = os.path.dirname(__file__)

  # python mdlr2mdl.py -ni ./fceri_files/fceri.mdlr -o ./fceri_files/fceri.mdl
  subprocess.call ( [ cellblender.python_path, os.path.join(engine_path, "mdlr2mdl.py"), "-ni", "Scene.mdlr", "-o", "Scene.mdl" ], cwd=output_data_dir )

  # run_data_model_mcell_3r.run_mcell_sweep(['-pd',project_dir,'-b',parameter_dictionary['MCellR Path']['val'],'-fs',fs,'-ls',ls],data_model={'mcell':data_model})



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


  # Postprocessing should be done through the command_list, but force it here for now...

  postprocess()

  return ( command_list )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass

