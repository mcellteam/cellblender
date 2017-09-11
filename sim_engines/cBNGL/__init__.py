import os
import sys
import shutil

import cellblender
import re


print ( "Executing cBNGL Simulation" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "cBNGL"
plug_name = "cBNGL"

def print_info():
  global parameter_dictionary
  global parameter_layout
  print ( 50*'==' )
  print ( "This is a preliminary cBNGL engine." )
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
bionetgen_path = "bionetgen/BNG2.pl"

project_files_dir = ""
start_seed = 1
end_seed = 1


def postprocess():
  global parameter_dictionary
  print ( "Postprocess called" )

  cbngl_react_dir = os.path.join(project_files_dir, "output_data")

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

    # Read the cBNGL data file and split into a list of rows where each row is a list of columns
    cbngl_react_file = open ( os.path.join ( cbngl_react_dir, 'Scene.gdat' ) )
    all_react_data = cbngl_react_file.read()
    react_data_all = [ [t.strip() for t in s.split() if len(t.strip()) > 0] for s in all_react_data.split('\n') if len(s) > 0 ]
    react_data_header = react_data_all[0]
    react_data_rows = react_data_all[1:]

    for col in range(1,len(react_data_header)):
      out_file_name = os.path.join ( react_seed_dir, react_data_header[col] + ".dat" )
      print ( "Writing data to " + out_file_name )
      f = open(out_file_name,"w")
      for row in react_data_rows:
        print ( "  " + row[0] + " " + row[col-1] )
        f.write ( row[0] + " " + row[col-1] + '\n' )
      f.close()

  print ( "Done postrocessing cBNGL Reaction Output" )


def parse_mdl_count_string(mdl_count_string):

  
  m_list = []
  cpat = re.compile('COUNT\[')
  wpat = re.compile('\s*,\s*WORLD\]')
  mc = cpat.split(mdl_count_string.strip())
  if len(mc) > 0:
    for m in mc:
      m_list.extend(wpat.split(m))

  obs_mol = ''.join(m_list)

  return(obs_mol)


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'Shared Path':    {'val': shared_path,    'as':'filename', 'desc':"Shared Path",         'icon':'FORCE_LENNARDJONES'},
  'BioNetGen Path': {'val': bionetgen_path, 'as':'filename', 'desc':"BioNetGen Path",      'icon':'OUTLINER_DATA_MESH'},
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)",    'icon':'INFO'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Postprocess': {'val': postprocess, 'desc':"Postprocess the data for CellBlender"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Shared Path'],
  ['BioNetGen Path'],
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
        os.makedirs ( full, exist_ok=exist_ok )


def prepare_runs_data_model_full ( data_model, project_dir, data_layout=None ):

  global project_files_dir

  project_files_dir = "" + project_dir

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "Inside prepare_runs in cBNGL Engine, project_dir=" + project_dir )

  if output_detail > 0: print ( "  Note: The current cBNGL engine doesn't support the prepare/run model.\n  It just runs directly." )

  print ( "Running with python " + sys.version )   # This will be Blender's Python which will be 3.5+
  print ( "Project Dir: " + project_dir )          # This will be .../blend_file_name_files/mcell
  print ( "Data Layout: " + str(data_layout) )     # This will typically be None

  output_data_dir = os.path.join ( project_dir, "output_data" )
  makedirs_exist_ok ( output_data_dir, exist_ok=True )


##############################
  bngl_file = os.path.join(output_data_dir, "Scene.bngl")
  f = open ( bngl_file, 'w' )

  f.write("begin model\n")
  f.write("\n")

  # Write the parameter system
  if 'parameter_system' in data_model:
    ps = data_model['parameter_system']
    if 'model_parameters' in ps:

      mplist = ps['model_parameters']

      if ('_extras' in ps) and ('ordered_id_names' in ps['_extras']):
        # Re-order the model parameters list (mplist) for proper dependency order based on ordered_id_names
        unordered_mplist = [ p for p in mplist ]  # Make a copy first since the algorithm removes items from this list!!
        ordered_mplist = []
        # First get all the parameters that match the ids in order (leave remaining in original list)
        ordered_ids = ps['_extras']['ordered_id_names']
        for ordered_id in ordered_ids:
          for p in unordered_mplist:
            if ('_extras' in p) and ('par_id_name' in p['_extras']):
              if p['_extras']['par_id_name'] == ordered_id:
                ordered_mplist.append(p)
                unordered_mplist.remove(p)
                break
        # Finish by adding all remaing items to the new list)
        for p in unordered_mplist:
          ordered_mplist.append(p)
        # Replace the old list by the new sorted list
        mplist = ordered_mplist
      else:
        # This is where the parameters could be placed in dependency order without relying on _extras fields
        # There should be no data models that don't have those fields, so pass for now.
        pass

      if len(mplist) > 0:
        f.write("  begin parameters\n")

        for p in mplist:

          # Write the name = val portion of the definition
          f.write ("    %s %s" % (p['par_name'], p['par_expression']) )

          # Write the optional description and units in a comment (if non empty)
          if (len(p['par_description']) > 0) or (len(p['par_units']) > 0):
            f.write ( "    # %s  %s" % (p['par_description'], p['par_units']) )

          f.write ( "\n" )

        f.write("  end parameters\n")
        f.write ( "\n" );


  if 'define_molecules' in data_model:
    mols = data_model['define_molecules']
    if 'molecule_list' in mols:
      mlist = mols['molecule_list']
      if len(mlist) > 0:
        f.write("  begin molecule types\n")
        for m in mlist:
          f.write ( "    %s(" % m['mol_name'] )
          if "bngl_component_list" in m:
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
        f.write("  end molecule types\n")
        f.write ( "\n" );


  if ('model_objects' in data_model) or ('release_sites' in data_model):
    geom = None
    rels = None
    mols = None
    if 'model_objects' in data_model:
      geom = data_model['model_objects']
    if 'release_sites' in data_model:
      rels = data_model['release_sites']
    if 'define_molecules' in data_model:
      mols = data_model['define_molecules']
    #TODO Note that the use of "Scene" here is a temporary measure!!!!
    if geom != None:
      if 'model_object_list' in geom:
        glist = geom['model_object_list']
        if len(glist) > 0:
          f.write("  begin compartments\n")
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
            g_volume = 1.0
            if len(g['membrane_name']) > 0:
              f.write ( "    %s 2 %.15g" % (g['membrane_name'],g_volume) )
              if len(g['parent_object']) > 0:
                f.write ( " %s" % (g['parent_object']) )
              f.write("\n")
              f.write ( "    %s 3 %.15g" % (g['name'],g_volume) )
              f.write ( " %s\n" % (g['membrane_name']) )
            else:
              f.write ( "    %s 3 %.15g" % (g['name'],g_volume) )
              if len(g['parent_object']) > 0:
                f.write ( " %s" % (g['parent_object']) )
              f.write("\n")
          f.write("  end compartments\n")
          f.write("\n")

    if rels != None:
      if 'release_site_list' in rels:
        rlist = rels['release_site_list']
        mlist = mols['molecule_list']
        if len(rlist) > 0:
          f.write("  begin seed species\n")
          for r in rlist:

            # Handle the molecule to be released (maybe the Molecule List should have been a dictionary keyed on mol_name?)
            mol = None
            for m in mlist:
              if m['mol_name'] == r['molecule']:
                mol = m
                break
            f.write("    %s" % (r['molecule']))

            # Now write out the quantity
            if r['quantity_type'] == 'NUMBER_TO_RELEASE':
              f.write(" %s\n" % (r['quantity']))
            elif r['quantity_type'] == 'GAUSSIAN_RELEASE_NUMBER':
              f.write(" %s\n" % (r['quantity']))
            elif r['quantity_type'] == 'DENSITY':
              f.write(" %s\n" % (r['quantity']))

          f.write("  end seed species\n")
          f.write("\n")

  if 'reaction_data_output' in data_model:
    plot_out = data_model['reaction_data_output']
    if 'reaction_output_list' in plot_out:
      plist = plot_out['reaction_output_list']
      if len(plist) > 0:
        f.write ( "  begin observables\n" )
        for p in plist:
          if 'rxn_or_mol' in p:
            if p['rxn_or_mol'] == 'MDLString':
              obs_mol = parse_mdl_count_string(p['mdl_string'])
              f.write ("    Molecules %s %s\n" % (p['mdl_file_prefix'], obs_mol))
        f.write ( "  end observables\n" )
        f.write("\n")


  if 'define_reactions' in data_model:
    reacts = data_model['define_reactions']
    if 'reaction_list' in reacts:
      rlist = reacts['reaction_list']
      if len(rlist) > 0:
        f.write("  begin reaction rules\n")
        for r in rlist:
          f.write("    ")
          if 'rxn_name' in r:
            if len(r['rxn_name']) > 0:
              f.write("%s: " % (r['rxn_name']))
          rxn = ''.join(r['name'].split())
          f.write("%s" % (rxn))
          if r['rxn_type'] == "irreversible":
            f.write ( "  %s" % ( r['fwd_rate'] ) )
          else:
            f.write ( "  %s, %s" % ( r['fwd_rate'], r['bkwd_rate'] ) )
          f.write("\n")
        f.write("  end reaction rules\n")
        f.write("\n")

  f.write("end model\n")
  f.write("\n")


  f.write("begin actions\n")
  f.write('  generate_network({overwrite=>1})\n')
#  f.write('  writeSBML()\n')
  f.write('  simulate({method=>"ode",t_start=>0,t_end=>30,n_steps=>10000,atol=>1e-8,rtol=>1e-8})\n')
  f.write("end actions\n")


  if 'initialization' in data_model:

    # To be use in actions block:
    time_step = data_model['initialization']['time_step']
    iterations = data_model['initialization']['iterations']


  f.close()
#####################################


  fs = data_model['simulation_control']['start_seed']
  ls = data_model['simulation_control']['end_seed']

  global start_seed
  global end_seed
  start_seed = int(fs)
  end_seed = int(ls)

  engine_path = os.path.dirname(__file__)


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

  # Build command list
  command_list = []

  command_dict = { 'cmd': os.path.join(shared_path,bionetgen_path),
                           'args': [ bngl_file ],
                           'wd': output_data_dir
                         }

  command_line_options = ''

  if len(command_line_options) > 0:
    command_dict['args'].append(command_line_options)

  command_list.append ( command_dict )
  if output_detail > 0:
    print ( str(command_dict) )

  # Postprocessing should be done through the command_list, but force it here for now...

#  postprocess()

  return ( command_list )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass

