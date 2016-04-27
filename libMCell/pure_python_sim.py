import sys
import os
import pickle
import math
import random
import array
import shutil

##### Start by reading the command line parameters which includes the data model file name

print ( "\n\nMCell Python Prototype using libMCell %d arguments:\n" % len(sys.argv) )
proj_path = ""
data_model_file_name = ""
data_model_full_path = ""
for arg in sys.argv:
  print ( "   " + str(arg) )
  if arg[0:10] == "proj_path=":
    proj_path = arg[10:]
  if arg[0:11] == "data_model=":
    data_model_file_name = arg[11:]
print ( "\n\n" )

if len(data_model_file_name) > 0:
  data_model_full_path = os.path.join ( proj_path, data_model_file_name )

print ( "Project path = \"%s\", data_model_file_name = \"%s\"" % (proj_path, data_model_full_path) )

##### Read in the data model itself

dm = None
if len(data_model_full_path) > 0:
  print ( "Loading data model from file: " + data_model_full_path + " ..." )
  f = open ( data_model_full_path, 'r' )
  pickle_string = f.read()
  f.close()
  dm = pickle.loads ( pickle_string.encode('latin1') )

print ( "Done loading CellBlender model." )

if dm is None:
  print ( "ERROR: Unable to use data model" )
  sys.exit(1)

#print ( str(dm) )

##### Clear out the old data

react_dir = os.path.join(proj_path, "react_data")

if os.path.exists(react_dir):
    shutil.rmtree(react_dir)
if not os.path.exists(react_dir):
    os.makedirs(react_dir)

viz_dir = os.path.join(proj_path, "viz_data")

if os.path.exists(viz_dir):
    shutil.rmtree(viz_dir)
if not os.path.exists(viz_dir):
    os.makedirs(viz_dir)

viz_seed_dir = os.path.join(viz_dir, "seed_00001")

if os.path.exists(viz_seed_dir):
    shutil.rmtree(viz_seed_dir)
if not os.path.exists(viz_seed_dir):
    os.makedirs(viz_seed_dir)

##### Use the Data Model to generate output files

iterations = eval(dm['mcell']['initialization']['iterations'])
time_step = eval(dm['mcell']['initialization']['time_step'])
mols = dm['mcell']['define_molecules']['molecule_list']
rels = dm['mcell']['release_sites']['release_site_list']

for m in mols:
  print ( "Molecule " + m['mol_name'] + " is a " + m['mol_type'] + " molecule diffusing with " + str(m['diffusion_constant']) )

for r in rels:
  print ( "Release " + str(r['quantity']) + " of " + r['molecule'] + " at (" + str(r['location_x']) + "," + str(r['location_y']) + "," + str(r['location_z']) + ")"  )

# Create instances for each molecule that is released (note that release patterns are not handled)

for m in mols:
  m['instances'] = []

for r in rels:
  rel_x = eval(r['location_x'])
  rel_y = eval(r['location_y'])
  rel_z = eval(r['location_z'])
  q = eval(r['quantity'])
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

# Begin the simulation

print_every = math.pow(10,math.floor(math.log10((iterations/10))));
if print_every < 1: print_every = 1;
for i in range(iterations+1):
  viz_file_name = file_name_template % i
  viz_file_name = os.path.join(viz_seed_dir,viz_file_name)
  if (i % print_every) == 0:
    print ( "File = " + viz_file_name )
  f = open(viz_file_name,"wb")
  int_array = array.array("I")   # Marker indicating a binary file
  int_array.fromlist([1])
  int_array.tofile(f)
  for m in mols:
    name = m['mol_name']
    f.write(bytearray([len(name)]))       # Number of bytes in the name
    for i in range(len(name)):
      f.write(bytearray([ord(name[i])]))  # Each byte of the name
    f.write(bytearray([0]))               # Molecule Type, 1=Surface, 0=Volume?

    # Write out the total number of values for this molecule species
    int_array = array.array("I")
    int_array.fromlist([3*len(m['instances'])])
    int_array.tofile(f)
    
    dc = eval(m['diffusion_constant'])
    ds = 6000 * math.sqrt( 6 * dc * time_step )    # N O T E:  This is a guess!!!!  (TODO: Make this realistic)

    for i in m['instances']:
      x = i[0]
      y = i[1]
      z = i[2]
      mol_pos = array.array("f")
      mol_pos.fromlist ( [ x, y, z ] )
      mol_pos.tofile(f)
      i[0] += random.gauss(0.0,ds)
      i[1] += random.gauss(0.0,ds)
      i[2] += random.gauss(0.0,ds)
  f.close()

print ( "Done simulation.\n" );

