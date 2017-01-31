#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
// This was an attempt to correct the exp10 warning that didn't work: #define _GNU_SOURCE
#include <math.h>

#include "JSON.h"

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
  
  printf ( "Done loading CellBlender model.\n" );

  file_text[file_length] = '\0'; // Be sure to null terminate!!
  
  // ##### Parse the data model text into convenient structures

  printf ( "Parsing the JSON data model ...\n" );

  data_model_element *dm; // Data Model Tree
  dm = parse_json_text ( file_text );

  printf ( "Done parsing the JSON data model ...\n" );

  if (dump_data_model != 0) {
    dump_json_element_tree ( dm, 80, 0 ); printf ( "\n\n" );
  }
  
  // ##### Clear out the old data

  printf ( "Creating directories ...\n" );

  char *react_dir = join_path ( proj_path, '/', "react_data" );
  mkdir ( react_dir, 0777 );

  char *viz_dir = join_path ( proj_path, '/', "viz_data" );
  mkdir ( viz_dir, 0777 );

  char *viz_seed_dir = join_path ( viz_dir, '/', "seed_00001" );
  mkdir ( viz_seed_dir, 0777 );


  printf ( "Generating Data ...\n" );

  // ##### Use the Data Model to generate output files
  
  // data_model_element *mcell = json_get_element_with_key ( dm, "mcell" );
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
  

  // Create structures to hold the molecules and fill them

  typedef struct mol_species_struct {
    char *name;
    char *type;
    char type_code;
    double diffusion_const;
    void *instance_list;
    int num_instances;
    struct mol_species_struct *next;
  } mol_species;

  mol_species *mol_species_list = NULL;

  int mol_num = 0;
  data_model_element *this_mol;
  while ((this_mol=json_get_element_by_index(mols,mol_num)) != NULL) {
    mol_species *new_mol = (mol_species *) malloc ( sizeof(mol_species) );
    new_mol->next = mol_species_list;
    new_mol->instance_list = NULL;
    new_mol->num_instances = 0;
    new_mol->name = json_get_string_value ( json_get_element_with_key ( this_mol, "mol_name" ) );
    new_mol->type = json_get_string_value ( json_get_element_with_key ( this_mol, "mol_type" ) );
    if (new_mol->type[0] == '3') {
      new_mol->type_code = 0;
    } else {
      new_mol->type_code = 1;
    }
    new_mol->diffusion_const = json_get_float_value ( json_get_element_with_key ( this_mol, "diffusion_constant" ) );
    mol_species_list = new_mol;
    printf ( "Molecule:\n" );
    printf ( "  name = %s\n", new_mol->name );
    printf ( "  type = %s\n", new_mol->type );
    printf ( "  dc = %g\n", new_mol->diffusion_const );
    mol_num++;
  }
  int total_mols = mol_num;
  printf ( "Total molecules = %d\n", total_mols );

  // Create structures to hold the release sites and fill them

  typedef struct rel_site_struct {
    mol_species *molecule_species;
    double loc_x;
    double loc_y;
    double loc_z;
    double quantity;
    struct rel_site_struct *next;
  } rel_site;

  rel_site *rel_site_list = NULL;

  int rel_num = 0;
  data_model_element *this_rel;
  while ((this_rel=json_get_element_by_index(rels,rel_num)) != NULL) {
    rel_site *new_rel = (rel_site *) malloc ( sizeof(rel_site) );
    new_rel->next = rel_site_list;
    char *mname = json_get_string_value ( json_get_element_with_key ( this_rel, "molecule" ) );
    mol_species *ms = mol_species_list;
    while ( (ms != NULL) && (strcmp(mname,ms->name)!=0) ) {
      ms = ms->next;
    }
    new_rel->molecule_species = ms;
    new_rel->loc_x = json_get_float_value ( json_get_element_with_key ( this_rel, "location_x" ) );
    new_rel->loc_y = json_get_float_value ( json_get_element_with_key ( this_rel, "location_y" ) );
    new_rel->loc_z = json_get_float_value ( json_get_element_with_key ( this_rel, "location_z" ) );
    new_rel->quantity = json_get_float_value ( json_get_element_with_key ( this_rel, "quantity" ) );
    rel_site_list = new_rel;
    printf ( "Release Site:\n" );
    printf ( "  molecule_name = %s\n", new_rel->molecule_species->name );
    printf ( "  at x = %g\n", new_rel->loc_x );
    printf ( "  at y = %g\n", new_rel->loc_y );
    printf ( "  at z = %g\n", new_rel->loc_z );
    printf ( "  quantity = %g\n", new_rel->quantity );
    rel_num++;
  }
  int total_rels = rel_num;
  printf ( "Total release sites = %d\n", total_rels );

  // # Create structures and instances for each molecule that is released (note that release patterns are not handled)

  typedef struct mol_instance_struct {
    mol_species *molecule_species;
    double x;
    double y;
    double z;
    struct mol_instance_struct *next;
  } mol_instance;
  
  mol_instance *mol_instances_list = NULL;
  
  rel_site *this_site = rel_site_list;
  while (this_site != NULL) {
    int i;
    for (i=0; i<this_site->quantity; i++) {
      mol_instance *new_mol_instance = (mol_instance *) malloc ( sizeof(mol_instance) );
      new_mol_instance->next = this_site->molecule_species->instance_list;
      this_site->molecule_species->instance_list = new_mol_instance;
      this_site->molecule_species->num_instances += 1;
      new_mol_instance->molecule_species = this_site->molecule_species;
      new_mol_instance->x = this_site->loc_x;
      new_mol_instance->y = this_site->loc_y;
      new_mol_instance->z = this_site->loc_z;
    }
    this_site = this_site->next;
  }
  
  // # Figure out the number of digits needed for file names and allocate strings as file name templates

  int ndigits = 1 + log10(iterations+1);
  printf ( "File names will require %d digits\n", ndigits );
  char *template_template = "seed_00001/Scene.cellbin.%%0%dd.dat";
  char *file_template = (char *) malloc ( strlen(template_template) + (ndigits*sizeof(char)) + 10 );
  sprintf ( file_template, template_template, ndigits );
  printf ( "File Template = %s\n", file_template );
  char *template =  (char *) malloc ( ( strlen(viz_dir) + 1 + strlen(file_template) + ndigits + 10 ) *sizeof(char));
  sprintf ( template, "%s/%s", viz_dir, file_template );
  printf ( "Full Template = %s\n", template );

  char *sim_step_mol_name = (char *) malloc ( strlen(template) + 10 );

  // Run the actual simulation
  printf ( "Begin simulation.\n" );

  int iteration;
  int print_every = (int)(exp10(floor(log10((iterations/10)))));
  if (print_every < 1) print_every = 1;
  for (iteration=0; iteration<=iterations; iteration++) {
    sprintf ( sim_step_mol_name, template, iteration );
    if ((iteration%print_every) == 0) {
      printf ( "Creating mol viz file: \"%s\"\n", sim_step_mol_name );
    }
    FILE *f = fopen ( sim_step_mol_name, "w" );
    // Write the binary marker for this file
    int binary_marker = 1;
    fwrite ( &binary_marker, sizeof(int), 1, f );
    
    // Write out the molecules from each species
    mol_species *this_species = mol_species_list;
    while (this_species != NULL) {
      unsigned char name_len = 0x0ff & strlen(this_species->name);
      fwrite ( &name_len, sizeof(unsigned char), 1, f );
      fwrite ( this_species->name, sizeof(unsigned char), strlen(this_species->name), f );
      unsigned char type_code = 0x0ff & (int)(this_species->type_code);
      fwrite ( &type_code, sizeof(unsigned char), 1, f );
      int total_values = 3 * this_species->num_instances;
      fwrite ( &total_values, sizeof(int), 1, f );
      
      /*
      printf ( "length of name = %d\n", (int)name_len );
      printf ( "molecule name  = %s\n", this_species->name );
      printf ( "mol type = %s\n", this_species->type );
      printf ( "type code = %d\n", (int)(this_species->type_code) );
      printf ( "num mols = %d\n", this_species->num_instances );
      printf ( "num values = %d\n", 3*this_species->num_instances );
      */

      mol_instance *this_mol_instance = this_species->instance_list;
      float float_val;
      double dc = this_species->diffusion_const;
      double ds = 6000 * sqrt( 6 * dc * time_step );    /// N O T E:  This is a guess!!!!  (TODO: Make this realistic)

      while (this_mol_instance != NULL) {
        float_val = this_mol_instance->x;
        fwrite ( &float_val, sizeof(float), 1, f );
        float_val = this_mol_instance->y;
        fwrite ( &float_val, sizeof(float), 1, f );
        float_val = this_mol_instance->z;
        fwrite ( &float_val, sizeof(float), 1, f );
        // NOTE: The following equations are just guesses to approximate the look of MCell for now (TODO: Make this realistic)
        this_mol_instance->x += 2.0 * ds * (((drand48()+drand48()+drand48())-1.5));
        this_mol_instance->y += 2.0 * ds * (((drand48()+drand48()+drand48())-1.5));
        this_mol_instance->z += 2.0 * ds * (((drand48()+drand48()+drand48())-1.5));
        this_mol_instance = this_mol_instance->next;
      }
      
      // printf ( "Move to next_species\n" );
      this_species = this_species->next;
    }
    
    fclose(f);
  }

  printf ( "Done simulation.\n" );
  
  //free_json_tree ( dm );
  //free ( file_text );
  
  printf ( "Still need to free lots of stuff!!\n\n" );

  return ( 0 );
}
