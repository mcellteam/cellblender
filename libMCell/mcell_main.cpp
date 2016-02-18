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

using namespace std;

int main ( int argc, char *argv[] ) {

  char *proj_path = NULL;
  char *data_model_file_name = NULL;
  char *data_model_full_path = "dm.json";
  
  int dump_data_model = 0;

  for (int i=1; i<argc; i++) {
    printf ( "   Arg: %s\n", argv[i] );
    if (strncmp("proj_path=",argv[i],10) == 0) {
      proj_path = &argv[i][10];
    }
    if (strncmp("data_model=",argv[i],11) == 0) {
      data_model_file_name = &argv[i][11];
    }
    if (strcmp("dump",argv[i]) == 0) {
      dump_data_model = 1;
    }
  }
  printf ( "\n" );

  MCellSimulation *mcell = new MCellSimulation();
  
  MCellMoleculeSpecies *mol_a = new MCellMoleculeSpecies();
  //mol_a->name = "A";
  mol_a->set_name("A");
  mol_a->diffusion_constant = 1e-7;
  mcell->molecule_species.push_back ( mol_a );

  MCellMoleculeSpecies *mol_b = new MCellMoleculeSpecies();
  //mol_b->name = "B";
  mol_b->set_name("B");
  mol_b->diffusion_constant = 2e-7;
  mcell->molecule_species.push_back ( mol_b );

  MCellReleaseSite *rel_a = new MCellReleaseSite();
  rel_a->x = 0.0;
  rel_a->y = 0.0;
  rel_a->z = 0.0;
  rel_a->molecule_species = mol_a;
  rel_a->quantity = 3;
  mcell->molecule_release_sites.push_back ( rel_a );

  MCellReleaseSite *rel_b = new MCellReleaseSite();
  rel_b->x = 0.3;
  rel_b->y = 0.2;
  rel_b->z = 0.1;
  rel_b->molecule_species = mol_b;
  rel_b->quantity = 7;
  mcell->molecule_release_sites.push_back ( rel_b );

  mcell->num_iterations = 200;
  mcell->time_step = 1e-7;

  mcell->run_simulation(proj_path);

  printf ( "\nMay need to free some things ...\n\n" );

  return ( 0 );
}

