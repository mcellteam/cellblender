#include <iostream>
#include <string>
#include <vector>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <math.h>

#include "libMCell.h"
// #include "StorageClasses.h"

using namespace std;


int main ( int argc, char *argv[] ) {

  cout << "\n\n" << endl;
  cout << "*********************************************" << endl;
  cout << "*   MCell C++ Test Program using libMCell   *" << endl;
  cout << "*********************************************" << endl;
  cout << "\n" << endl;

  //This is a hard-coded simulation as a simple example of the API

  MCellSimulation *mcell = new MCellSimulation();

  MCellMoleculeSpecies *mol_a = new MCellMoleculeSpecies();
  mol_a->name = "A";
  mol_a->diffusion_constant = 1e-6;
  mcell->add_molecule_species( mol_a );

  MCellMoleculeSpecies *mol_b = new MCellMoleculeSpecies();
  mol_b->name = "B";
  mol_b->diffusion_constant = 2e-5;
  mcell->add_molecule_species( mol_b );

  MCellReleaseSite *rel_a = new MCellReleaseSite();
  rel_a->x = 0.0;
  rel_a->y = 0.0;
  rel_a->z = 0.0;
  rel_a->molecule_species = mol_a;
  rel_a->quantity = 300;
  mcell->add_molecule_release_site ( rel_a );

  MCellReleaseSite *rel_b = new MCellReleaseSite();
  rel_b->x = 0.3;
  rel_b->y = 0.2;
  rel_b->z = 0.1;
  rel_b->molecule_species = mol_b;
  rel_b->quantity = 700;
  mcell->add_molecule_release_site ( rel_b );

  mcell->num_iterations = 200;
  mcell->time_step = 1e-7;

  mcell->run_simulation(".");

  return ( 0 );
}

