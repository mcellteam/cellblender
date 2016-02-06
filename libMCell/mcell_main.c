#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "JSON.h"

#include "libMCell.h"

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

  // ##### Start by reading the command line parameters which includes the data model file name

  printf ( "\n\nMCell C prototype using libMCell with %d arguments:\n\n", argc-1 );

  char *proj_path = NULL;
  char *data_model_file_name = NULL;
  char *data_model_full_path = "dm.json";
  
  int dump_data_model = 0;

  { // Keep Loop Var Local
    int i;
    for (i=1; i<argc; i++) {
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
  }  
  printf ( "\n" );
  
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
  
  printf ( "Done loading CellBlender model." );

  file_text[file_length] = '\0'; // Be sure to null terminate!!
  
  // ##### Parse the data model text into convenient structures

  data_model_element *dm; // Data Model Tree
  dm = parse_json_text ( file_text );

  if (dump_data_model != 0) {
    dump_json_tree ( dm, 80, 0 ); printf ( "\n\n" );
  }
  
  // ##### Clear out the old data

  char *react_dir = join_path ( proj_path, '/', "react_data" );
  mkdir ( react_dir, 0777 );

  char *viz_dir = join_path ( proj_path, '/', "viz_data" );
  mkdir ( viz_dir, 0777 );

  char *viz_seed_dir = join_path ( viz_dir, '/', "seed_00001" );
  mkdir ( viz_seed_dir, 0777 );


  // ##### Use the Data Model to generate output files
  
  data_model_element *mcell = json_get_element_with_key ( dm, "mcell" );

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

  data_model_element *dm_iters = json_get_element_with_key ( dm_init, "iterations" );
  int iterations = json_get_int_value ( dm_iters );
  mcell_set_iterations ( iterations );

  data_model_element *dm_time_step = json_get_element_with_key ( dm_init, "time_step" );
  double time_step = json_get_float_value ( dm_time_step );
  mcell_set_time_step ( time_step );
  
  data_model_element *dm_define_molecules = json_get_element_with_key ( mcell, "define_molecules" );
  data_model_element *mols = json_get_element_with_key ( dm_define_molecules, "molecule_list" );
  
  data_model_element *dm_release_sites = json_get_element_with_key ( mcell, "release_sites" );
  data_model_element *rels = json_get_element_with_key ( dm_release_sites, "release_site_list" );
  
  int mol_num = 0;
  data_model_element *this_mol;
  while ((this_mol=json_get_element_by_index(mols,mol_num)) != NULL) {
    printf ( "Molecule:\n" );
    printf ( "  name = %s\n", json_get_string_value ( json_get_element_with_key ( this_mol, "mol_name" ) ) );
    printf ( "  type = %s\n", json_get_string_value ( json_get_element_with_key ( this_mol, "mol_type" ) ) );
    printf ( "  dc = %s\n", json_get_string_value ( json_get_element_with_key ( this_mol, "diffusion_constant" ) ) );
    mol_num++;
  }
  
  int rel_num = 0;
  data_model_element *this_rel;
  while ((this_rel=json_get_element_by_index(rels,rel_num)) != NULL) {
    printf ( "Release Site:\n" );
    printf ( "  quantity = %s\n", json_get_string_value ( json_get_element_with_key ( this_rel, "quantity" ) ) );
    printf ( "  molecule = %s\n", json_get_string_value ( json_get_element_with_key ( this_rel, "molecule" ) ) );
    printf ( "  at x = %s\n", json_get_string_value ( json_get_element_with_key ( this_rel, "location_x" ) ) );
    printf ( "  at y = %s\n", json_get_string_value ( json_get_element_with_key ( this_rel, "location_y" ) ) );
    printf ( "  at z = %s\n", json_get_string_value ( json_get_element_with_key ( this_rel, "location_z" ) ) );
    rel_num++;
  }
  
  
  //data_model_element *reaction_data_output = json_get_element_with_key ( mcell, "reaction_data_output" );
  //data_model_element *plot_layout = json_get_element_with_key ( reaction_data_output, "plot_layout" );

  // printf ( "Plot Layout = \"%s\"\n", json_get_string_value ( plot_layout ) );

  free_json_tree ( dm );
  free ( file_text );

  return ( 0 );
}
