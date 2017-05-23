import sys
import os
import pickle
import math
import random
import array
import shutil

##### Start by reading the command line parameters which includes the data model file name

proj_path = ""
data_model_file_name = ""
data_model_full_path = ""
run_seed = 1
decay_rate_factor = 1.0
output_detail = 0
for arg in sys.argv:
  if output_detail > 10: print ( "   " + str(arg) )
  if arg[0:10] == "proj_path=":
    proj_path = arg[10:]
  elif arg[0:11] == "data_model=":
    data_model_file_name = arg[11:]
  elif arg[0:5] == "seed=":
    run_seed = int(arg[5:])
  elif arg[0:13] == "decay_factor=":
    decay_rate_factor = float(arg[13:])
  elif arg[0:14] == "output_detail=":
    output_detail = int(arg[14:])
  else:
    if output_detail > 0: print ( "Unknown argument = " + str(arg) )
if output_detail > 10: print ( "\n\n" )

if output_detail > 0: print ( "**********************************************" )
if output_detail > 0: print ( "*  Limited Pure Python Prototype Simulation  *" )
if output_detail > 0: print ( "*        Updated: February 5th, 2017         *" )
if output_detail > 0: print ( "**********************************************" )

if output_detail > 10: print ( "Arguments: " + str(sys.argv) )

random.seed ( run_seed )
seed_dir = "seed_%05d" % run_seed

if len(data_model_file_name) > 0:
  data_model_full_path = os.path.join ( proj_path, data_model_file_name )

print ( "Project path = \"%s\", data_model_file_name = \"%s\"" % (proj_path, data_model_full_path) )

##### Read in the data model itself

dm = None
if len(data_model_full_path) > 0:
  if output_detail > 0: print ( "Loading data model from file: " + data_model_full_path + " ..." )
  f = open ( data_model_full_path, 'r' )
  pickle_string = f.read()
  f.close()
  dm = pickle.loads ( pickle_string.encode('latin1') )

if output_detail > 0: print ( "Done loading CellBlender model." )

if dm is None:
  print ( "ERROR: Unable to use data model" )
  sys.exit(1)

#print ( str(dm) )

##### Clear out the old data

# Note that there have been some errors calling rmtree, which are currently being ignored:
#  OSError: [Errno 16] Device or resource busy: '.nfs0000000000a48d3e00005e12'
#  OSError: [Errno 39] Directory not empty: 'seed_00001'

react_dir = os.path.join(proj_path, "output_data", "react_data")
if not os.path.exists(react_dir):
    os.makedirs(react_dir)

viz_dir = os.path.join(proj_path, "output_data", "viz_data")
if not os.path.exists(viz_dir):
    os.makedirs(viz_dir)

viz_seed_dir = os.path.join(viz_dir, seed_dir)
if not os.path.exists(viz_seed_dir):
    os.makedirs(viz_seed_dir)

react_seed_dir = os.path.join(react_dir, seed_dir)
if not os.path.exists(react_seed_dir):
    os.makedirs(react_seed_dir)

##### Use the Data Model to generate output files

## Start by building a parameter value dictionary

par_val_dict = {}
for p in dm['mcell']['parameter_system']['model_parameters']:
  par_val_dict[p['par_name']] = p['_extras']['par_value']

if output_detail > 0:
  print ( "Parameter Dictionary: " + str(par_val_dict) )
  for k in par_val_dict.keys():
    print ( "   " + str(k) + ": " + str(par_val_dict[k]) )

def convert_to_value ( expression ):
  global par_val_dict
  return eval(expression,globals(),par_val_dict)

iterations = int(convert_to_value(dm['mcell']['initialization']['iterations']))
time_step = convert_to_value(dm['mcell']['initialization']['time_step'])
mols = dm['mcell']['define_molecules']['molecule_list']
rels = dm['mcell']['release_sites']['release_site_list']

rxns = []
if 'define_reactions' in dm['mcell']:
  if 'reaction_list' in dm['mcell']['define_reactions']:
    if len(dm['mcell']['define_reactions']['reaction_list']) > 0:
      rxns = dm['mcell']['define_reactions']['reaction_list']

for m in mols:
  if output_detail > 0: print ( "Molecule " + m['mol_name'] + " is a " + m['mol_type'] + " molecule diffusing with " + str(m['diffusion_constant']) )

for r in rels:
  if output_detail > 0: print ( "Release " + str(r['quantity']) + " of " + r['molecule'] + " at (" + str(r['location_x']) + "," + str(r['location_y']) + "," + str(r['location_z']) + ")"  )

for r in rxns:
  arrow = '->'
  bkwd = ''
  if len(r['bkwd_rate']) > 0:
    arrow = '<->'
    bkwd = ", " + str(r['bkwd_rate'])
  if output_detail > 0: print ( "Reaction: " + r['reactants'] + " " + arrow + " " + r['products'] + "  [" + str(r['fwd_rate']) + bkwd + "]"  )

# Create instances for each molecule that is released (note that release patterns are not handled)

for m in mols:
  m['instances'] = []

for r in rels:
  rel_x = convert_to_value(r['location_x'])
  rel_y = convert_to_value(r['location_y'])
  rel_z = convert_to_value(r['location_z'])
  q = int(convert_to_value(r['quantity']))
  for m in mols:
    if m['mol_name'] == r['molecule']:
      for i in range(q):
        x = rel_x  # +random.gauss(0.0,0.1)
        y = rel_y  # +random.gauss(0.0,0.1)
        z = rel_z  # +random.gauss(0.0,0.1)
        m['instances'].append ( [x,y,z] )

# Figure out the number of digits needed for file names

ndigits = 1 + math.log(iterations+1,10)
file_name_template = "Scene.cellbin.%%0%dd.dat" % ndigits

# Create the count files for each molecule species (doesn't currently use the count specifications)

count_files = {}

for m in mols:
  react_file_name = "%s/%s/%s.World.dat" % ( react_dir, seed_dir, m['mol_name'] )
  count_files[m['mol_name']] = open(react_file_name,"w")


# Begin the simulation

print_every = math.pow(10,math.floor(math.log10((iterations/10))));
if print_every < 1: print_every = 1;
for i in range(iterations+1):
  # Write the viz data (every iteration for now)
  viz_file_name = file_name_template % i
  viz_file_name = os.path.join(viz_seed_dir,viz_file_name)
  if (i % print_every) == 0:
    if output_detail > 0: print ( "File = " + viz_file_name )
  f = open(viz_file_name,"wb")
  int_array = array.array("I")   # Marker indicating a binary file
  int_array.fromlist([1])
  int_array.tofile(f)
  for m in mols:
    name = m['mol_name']
    f.write(bytearray([len(name)]))       # Number of bytes in the name
    for ni in range(len(name)):
      f.write(bytearray([ord(name[ni])]))  # Each byte of the name
    f.write(bytearray([0]))                # Molecule Type, 1=Surface, 0=Volume?

    # Write out the total number of values for this molecule species
    int_array = array.array("I")
    int_array.fromlist([3*len(m['instances'])])
    int_array.tofile(f)
    
    dc = convert_to_value(m['diffusion_constant'])
    ds = math.sqrt(4.0 * 1.0e8 * dc * time_step)
    for mi in m['instances']:
      x = mi[0]
      y = mi[1]
      z = mi[2]
      mol_pos = array.array("f")
      mol_pos.fromlist ( [ x, y, z ] )
      mol_pos.tofile(f)
      mi[0] += random.gauss(0.0,ds) * 0.70710678118654752440
      mi[1] += random.gauss(0.0,ds) * 0.70710678118654752440
      mi[2] += random.gauss(0.0,ds) * 0.70710678118654752440
  f.close()
  # Write the count data (every iteration for now)
  for m in mols:
    name = m['mol_name']
    count = len(m['instances'])
    count_files[name].write ( "%.15g" % (i*time_step) + " " + str(count) + "\n" )

  # Perform approximate decay reactions for now  (TODO: Make this realistic)
  for m in mols:
    if len(m['instances']) > 0:
      # There are some molecules left to react
      for r in rxns:
        if r['reactants'] == m['mol_name']:
          # The reaction applies to this molecule
          rate = convert_to_value(r['fwd_rate'])
          fraction_to_remove = decay_rate_factor * rate * time_step
          amount_to_remove = fraction_to_remove * len(m['instances'])
          num_to_remove = int(amount_to_remove)
          if random.random() < (amount_to_remove - num_to_remove):
            num_to_remove += 1
          if output_detail > 50: print ( "React " + m['mol_name'] + " with rate = " + str(rate) + ", remove " + str(num_to_remove) + " (should be about " + str(100*fraction_to_remove) + "%)" )
          for i in range(num_to_remove):
            if len(m['instances']) > 0:
              m['instances'].pop()


for fname in count_files.keys():
  count_files[fname].close()

if output_detail > 0: print ( "Done simulation.\n" );

