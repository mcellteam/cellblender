# file: mcell_main.py

import sys
import os
import pickle
import math
import random
import array
import shutil
from libMCell import *

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

##### Use the Data Model to initialize a libMCell model

mcell_sim = MCellSimulation()

mcell_sim.num_iterations = eval(dm['mcell']['initialization']['iterations'])
mcell_sim.time_step = eval(dm['mcell']['initialization']['time_step'])

mol_defs = dm['mcell']['define_molecules']['molecule_list']
mols = {}

for m in mol_defs:
  print ( "Molecule " + m['mol_name'] + " is a " + m['mol_type'] + " molecule diffusing with " + str(m['diffusion_constant']) )
  mol = MCellMoleculeSpecies()
  mol.name = m['mol_name']
  mol.diffusion_constant = m['diffusion_constant']
  mcell_sim.add_molecule_species(mol)
  mols[mol.name] = mol

rel_defs = dm['mcell']['release_sites']['release_site_list']
rels = {}

for r in rel_defs:
  print ( "Release " + str(r['quantity']) + " of " + r['molecule'] + " at (" + str(r['location_x']) + "," + str(r['location_y']) + "," + str(r['location_z']) + ")"  )
  rel = MCellReleaseSite
  rel.x = eval(r['location_x'])
  rel.y = eval(r['location_y'])
  rel.z = eval(r['location_z'])
  rel.quantity = eval(r['quantity'])
  rel.molecule_species = mols[r['molecule']]

mcell_sim.run_simulation(proj_path)

print ( "\nPython simulation using libMCell is complete.\n" )

