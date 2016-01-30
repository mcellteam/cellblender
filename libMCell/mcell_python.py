import sys
import os
import pickle
import random
import array
import shutil
import libMCell

##### Start by reading the command line parameters which includes the data model file name

print ( "\n\nmcell_python.py is running with %d arguments\n" % len(sys.argv) )
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

print ( str(dm) )

##### These are some test calls to the currently incomplete libMCell

#print ( "My variable = %f" % libMCell.My_variable )  # This doesn't work yet
print ( "5 factorial = %d" % libMCell.fact(5) )
print ( "25 mod 7 = %d" % libMCell.my_mod(25,7) )
print ( "sin(1.234) = %g" % libMCell.my_sin(1.234) )
print ( "Time = %s" % libMCell.get_time() )

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
mols = dm['mcell']['define_molecules']['molecule_list']
rels = dm['mcell']['release_sites']['release_site_list']

for m in mols:
  print ( "Molecule " + m['mol_name'] + " is a " + m['mol_type'] + " molecule diffusing with " + str(m['diffusion_constant']) )

for r in rels:
  print ( "Release " + str(r['quantity']) + " of " + r['molecule'] + " at (" + str(r['location_x']) + "," + str(r['location_y']) + "," + str(r['location_z']) + ")"  )

for i in range(iterations+1):
  viz_file_name = "Scene.cellbin.%02d.dat" % i
  viz_file_name = os.path.join(viz_seed_dir,viz_file_name)
  print ( "File = " + viz_file_name )
  f = open(viz_file_name,"wb")
  #f.write(bytearray([1,0,0,0]))           # Marker indicating a binary file
  int_array = array.array("I")
  int_array.fromlist([1])
  int_array.tofile(f)
  for m in mols:
    name = m['mol_name']
    f.write(bytearray([len(name)]))       # Number of bytes in the name
    for i in range(len(name)):
      f.write(bytearray([ord(name[i])]))  # Each byte of the name
    f.write(bytearray([0]))               # Molecule Type, 1=Surface, 0=Volume?
    for r in rels:
      if r['molecule'] == name:
        rel_x = eval(r['location_x'])
        rel_y = eval(r['location_y'])
        rel_z = eval(r['location_z'])
        q = eval(r['quantity'])
        #f.write(bytearray([0,0,0,0]))         # Number of instances of this molecule in this frame
        int_array = array.array("I")
        int_array.fromlist([3*q])
        int_array.tofile(f)
        for i in range(q):
          mol_pos = array.array("f")
          mol_pos.fromlist ( [ rel_x+random.gauss(0.0,0.1), rel_y+random.gauss(0.0,0.1), rel_z+random.gauss(0.0,0.1) ] )
          mol_pos.tofile(f)

  f.close()


for i in range(iterations):
  print ( "x = " + str(random.gauss(0.0,1.0)) )

