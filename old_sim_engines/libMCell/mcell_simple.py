# file: mcell_main.py

import sys

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


mcell = MCellSimulation()

mol_a = MCellMoleculeSpecies()
mol_a.name = "A"
mol_a.diffusion_constant = 1e-7
mcell.add_molecule_species ( mol_a )

mol_b = MCellMoleculeSpecies()
mol_b.name = "B"
mol_b.diffusion_constant = 2e-7
mcell.add_molecule_species ( mol_b )

rel_a = MCellReleaseSite()
rel_a.x = 0.0
rel_a.y = 0.0
rel_a.z = 0.0
rel_a.molecule_species = mol_a
rel_a.quantity = 3
mcell.add_molecule_release_site ( rel_a )

rel_b = MCellReleaseSite()
rel_b.x = 0.3
rel_b.y = 0.2
rel_b.z = 0.1
rel_b.molecule_species = mol_b
rel_b.quantity = 7
mcell.add_molecule_release_site ( rel_b )

mcell.num_iterations = 200
mcell.time_step = 1e-7

mcell.run_simulation(proj_path)


print "Done."
