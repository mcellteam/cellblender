# file: mcell_main.py

import sys
import os
import pickle

from libMCell import *


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

##### Copy values from the data model into a new MCellSimulation

mcell = MCellSimulation()

mcell.num_iterations = eval(dm['mcell']['initialization']['iterations']);
mcell.time_step = eval(dm['mcell']['initialization']['time_step']);

mols = dm['mcell']['define_molecules']['molecule_list']
rels = dm['mcell']['release_sites']['release_site_list']

mol_dict = {}

for m in mols:
  mol = MCellMoleculeSpecies();
  mol_dict.update ( { m['mol_name'] : mol.species_id } )
  #m['sim_species_id'] = mol.species_id
  #mol.set_name ( str(m['mol_name']) )
  mol.diffusion_constant = eval(m['diffusion_constant'])
  mcell.add_molecule_species ( mol );

mcell.dump()

print ( mol_dict )

for r in rels:
  rel = MCellReleaseSite();
  rel.x = eval(r['location_x']);
  rel.y = eval(r['location_y']);
  rel.z = eval(r['location_z']);
  mol_id_to_release = mol_dict[r['molecule']]
  print ( "Releasing " + r['molecule'] + " with index " + str(mol_id_to_release) )
  #rel.molecule_species = mcell.get_molecule_species_by_name(r['molecule']);
  rel.mol_id = mol_id_to_release
  rel.molecule_species = mcell.get_molecule_species_by_id(mol_id_to_release);
  rel.quantity = eval(r['quantity'])
  mcell.add_molecule_release_site ( rel );

##### Run the simulation

mcell.run_simulation(proj_path);


print "Done."
