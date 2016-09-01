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
#include "StorageClasses.h"

extern "C" {
#include "JSON.h"
}

using namespace std;

typedef json_element data_model_element;

char *join_path ( char *p1, char sep, char *p2 ) {
  char *joined_path;
  if ((p1 == NULL) && (p2 == NULL) ) {
    joined_path = NULL;
  } else if ((p2 == NULL) || (strlen(p2) == 0) ) {
    joined_path = (char *) malloc ( strlen(p1) + 1 );
    strcpy ( joined_path, p1 );
  } else if ((p1 == NULL) || (strlen(p1) == 0) ) {
    joined_path = (char *) malloc ( strlen(p2) + 1 );
    strcpy ( joined_path, p2 );
  } else {
    joined_path = (char *) malloc ( strlen(p1) + 1 + strlen(p2) + 1 );
    strcpy ( joined_path, p1 );
    joined_path[strlen(p1)] = '/';
    strcpy ( &joined_path[strlen(p1)+1], p2 );
  }
  return ( joined_path );
}


int main ( int argc, char *argv[] ) {

  cout << "\n\n" << endl;
  cout << "******************************************" << endl;
  cout << "*   MCell C++ Prototype using libMCell   *" << endl;
  cout << "*      Updated: August 31st, 2016        *" << endl;
  cout << "******************************************" << endl;
  cout << "\n" << endl;

  // Define data items to come from the command line arguments

  char *proj_path = NULL;
  char *data_model_file_name = NULL;
  char *data_model_full_path = "dm.json";
  
  int dump_data_model = 0;

  // Process the command line arguments

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


  // Read the data model text from the input file

  data_model_full_path = join_path ( proj_path, '/', data_model_file_name );

  printf ( "Project path = \"%s\", data_model_file_name = \"%s\"\n", proj_path, data_model_full_path );

  char *file_name = data_model_full_path;
  FILE *f = fopen ( file_name, "r" );

  printf ( "Loading data model from file: %s ...\n", file_name );

  long file_length;
  fseek (f, 0L, SEEK_END);
  file_length = ftell(f);

  char *file_text = (char *) malloc ( file_length + 2 );

  fseek (f, 0L, SEEK_SET);
  fread ( file_text, 1, file_length, f );

  fclose(f);
  
  printf ( "Done loading CellBlender model.\n" );

  file_text[file_length] = '\0'; // Be sure to null terminate!!


  // Parse the data model text into convenient structures

  printf ( "Parsing the JSON data model ...\n" );

  data_model_element *dm; // Data Model Tree
  dm = parse_json_text ( file_text );

  printf ( "Done parsing the JSON data model ...\n" );

  if (dump_data_model != 0) {
    dump_json_element_tree ( dm, 80, 0 ); printf ( "\n\n" );
  }


  // Extract various dictionaries and fields from the data model needed to run a minimal simulation:

  data_model_element *top_array = json_get_element_by_index ( dm, 0 );
  data_model_element *mcell = json_get_element_with_key ( top_array, "mcell" );

  // Blender version = ['mcell']['blender_version']
  data_model_element *blender_ver = json_get_element_with_key ( mcell, "blender_version" );
  data_model_element *vn = json_get_element_by_index ( blender_ver, 0 );
  printf ( "Blender API version = %ld", json_get_int_value ( vn ) );
  vn = json_get_element_by_index ( blender_ver, 1 );
  printf ( ".%ld", json_get_int_value ( vn ) );
  vn = json_get_element_by_index ( blender_ver, 2 );
  printf ( ".%ld\n", json_get_int_value ( vn ) );
  
  // API version = ['mcell']['api_version']
  data_model_element *api_ver = json_get_element_with_key ( mcell, "api_version" );

  printf ( "CellBlender API version = %d\n", json_get_int_value ( api_ver ) );

  // iterations = ['mcell']['initialization']['iterations']
  data_model_element *dm_init = json_get_element_with_key ( mcell, "initialization" );

  int iterations = json_get_int_value ( json_get_element_with_key ( dm_init, "iterations" ) );
  //mcell_set_iterations ( iterations );

  double time_step = json_get_float_value ( json_get_element_with_key ( dm_init, "time_step" ) );
  //mcell_set_time_step ( time_step );

  
  data_model_element *dm_define_molecules = json_get_element_with_key ( mcell, "define_molecules" );
  data_model_element *mols = json_get_element_with_key ( dm_define_molecules, "molecule_list" );
  
  data_model_element *dm_release_sites = json_get_element_with_key ( mcell, "release_sites" );
  data_model_element *rels = json_get_element_with_key ( dm_release_sites, "release_site_list" );
  

  // Finally build the actual simulation from the data extracted from the data model

  MCellSimulation *mcell_sim = new MCellSimulation();


  // Define the molecules for this simulation

  int mol_num = 0;
  data_model_element *this_mol;
  MCellMoleculeSpecies *mol;
  while ((this_mol=json_get_element_by_index(mols,mol_num)) != NULL) {
    mol = new MCellMoleculeSpecies();
    mol->name = json_get_string_value ( json_get_element_with_key ( this_mol, "mol_name" ) );
    mol->diffusion_constant = json_get_float_value ( json_get_element_with_key ( this_mol, "diffusion_constant" ) );
    // This allows the molecule to be referenced by name when needed:
    mcell_sim->molecule_species[mol->name.c_str()] = mol;
    mol_num++;
  }
  int total_mols = mol_num;
  printf ( "Total molecules = %d\n", total_mols );


  // Define the release sites for this simulation

  int rel_num = 0;
  data_model_element *this_rel;
  MCellReleaseSite *rel;
  while ((this_rel=json_get_element_by_index(rels,rel_num)) != NULL) {
    char *mname = json_get_string_value ( json_get_element_with_key ( this_rel, "molecule" ) );
    rel = new MCellReleaseSite();
    rel->x = json_get_float_value ( json_get_element_with_key ( this_rel, "location_x" ) );
    rel->y = json_get_float_value ( json_get_element_with_key ( this_rel, "location_y" ) );
    rel->z = json_get_float_value ( json_get_element_with_key ( this_rel, "location_z" ) );
    rel->quantity = json_get_float_value ( json_get_element_with_key ( this_rel, "quantity" ) );
    rel->molecule_species = mcell_sim->molecule_species[mname];
    mcell_sim->molecule_release_sites.append ( rel );
    rel_num++;
  }
  int total_rels = rel_num;
  printf ( "Total release sites = %d\n", total_rels );


  // Set final parameters needed to run simulation and Run it

  mcell_sim->num_iterations = iterations;
  mcell_sim->time_step = time_step;

  mcell_sim->run_simulation(proj_path);

  printf ( "\nMay need to free some things ...\n\n" );

  return ( 0 );
}

