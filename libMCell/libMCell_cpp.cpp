#include <iostream>
#include <string>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <math.h>

extern "C" {
#include "JSON.h"
// #include "libMCell.h"
}

#include "libMCell_cpp.h"

using namespace std;

/*
void Shape::setPosition(int nx, int ny) {
  x = nx;
  y = ny;
}

void Shape::move(int dx, int dy) {
  x += dx;
  y += dy;
}

double Rectangle::area(void) {
  return width*height;
}

double Rectangle::perimeter(void) {
  return 2*width+2*height;
}

double Circle::area(void) {
  return M_PI*radius*radius;
}

double Circle::perimeter(void) {
  return 2*M_PI*radius;
}

void foo(int x) {
  printf("Called foo(int) : %d\n", x);
}

void foo(double x) {
  printf("Called foo(double) : %f\n", x);
}

void foo(char *s) {
  printf("Called foo(char *) : %s\n", s);
}

namespace Spam {
  void PointDebug(Point *p) {
    printf("Spam::Point(%d,%d)\n", p->x, p->y);
  }
};

void CoordDebug(Coord<int> *c) {
  printf("Coord<int>(%d,%d)\n",c->x, c->y);
}

void CoordDebug(Coord<double> *c) {
  printf("Coord<int>(%f,%f)\n",c->x, c->y);
}
*/

/*
int mcell_iterations = 0;
int mcell_set_iterations(int iters) {
  printf ( "  * ** *** libMCell.mcell_set_mcell_iterations called with %d\n", iters );
  mcell_iterations = iters;
  return ( mcell_iterations );
}

double mcell_time_step = 0;
double mcell_set_time_step(double dt) {
  printf ( "  * ** *** libMCell.mcell_set_mcell_time_step called with %g\n", dt );
  mcell_time_step = dt;
  return ( mcell_time_step );
}
*/

char *Simulation::join_path ( char *p1, char sep, char *p2 ) {
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


int Simulation::run ( char *proj_path, data_model_element *dm ) {

  // ##### Clear out the old data

  printf ( "Creating directories ...\n" );

  char *react_dir = join_path ( proj_path, '/', "react_data" );
  mkdir ( react_dir, 0777 );

  char *viz_dir = join_path ( proj_path, '/', "viz_data" );
  mkdir ( viz_dir, 0777 );

  char *viz_seed_dir = join_path ( viz_dir, '/', "seed_00001" );
  mkdir ( viz_seed_dir, 0777 );

  printf ( "Generating C++ Data ...\n" );

  // ##### Use the Data Model to build a simulation and generate output files

  // Simulation *sim = new Simulation;

  // data_model_element *mcell = json_get_element_with_key ( dm, "mcell" );
  data_model_element *top_array = json_get_element_by_index ( dm, 0 );
  data_model_element *mcell = json_get_element_with_key ( top_array, "mcell" );

  // Blender version = ['mcell']['blender_version']
  data_model_element *blender_ver = json_get_element_with_key ( mcell, "blender_version" );
  data_model_element *vn = json_get_element_by_index ( blender_ver, 0 );
  printf ( "Blender API version = %d", json_get_int_value ( vn ) );
  vn = json_get_element_by_index ( blender_ver, 1 );
  printf ( ".%d", json_get_int_value ( vn ) );
  vn = json_get_element_by_index ( blender_ver, 2 );
  printf ( ".%d\n", json_get_int_value ( vn ) );

  // API version = ['mcell']['api_version']
  data_model_element *api_ver = json_get_element_with_key ( mcell, "api_version" );

  printf ( "CellBlender API version = %d\n", json_get_int_value ( api_ver ) );

  // iterations = ['mcell']['initialization']['iterations']
  data_model_element *dm_init = json_get_element_with_key ( mcell, "initialization" );

  int iterations = json_get_int_value ( json_get_element_with_key ( dm_init, "iterations" ) );
  // mcell_set_iterations ( iterations );

  double time_step = json_get_float_value ( json_get_element_with_key ( dm_init, "time_step" ) );
  // mcell_set_time_step ( time_step );


  data_model_element *dm_define_molecules = json_get_element_with_key ( mcell, "define_molecules" );
  data_model_element *mols = json_get_element_with_key ( dm_define_molecules, "molecule_list" );

  data_model_element *dm_release_sites = json_get_element_with_key ( mcell, "release_sites" );
  data_model_element *rels = json_get_element_with_key ( dm_release_sites, "release_site_list" );


  // Create structures to hold the molecules and fill them

  /* sim-> */ mol_species_list = NULL;

  int mol_num = 0;
  data_model_element *this_mol;
  while ((this_mol=json_get_element_by_index(mols,mol_num)) != NULL) {
    MolSpecies *new_mol = new MolSpecies;
    new_mol->next = /* sim-> */ mol_species_list;
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
    /* sim-> */ mol_species_list = new_mol;
    printf ( "Molecule:\n" );
    printf ( "  name = %s\n", new_mol->name );
    printf ( "  type = %s\n", new_mol->type );
    printf ( "  dc = %g\n", new_mol->diffusion_const );
    mol_num++;
  }
  int total_mols = mol_num;
  printf ( "Total molecules = %d\n", total_mols );

  // Create structures to hold the release sites and fill them

  /* sim-> */ rel_site_list = NULL;

  int rel_num = 0;
  data_model_element *this_rel;
  while ((this_rel=json_get_element_by_index(rels,rel_num)) != NULL) {
    ReleaseSite *new_rel = new ReleaseSite;
    new_rel->next = /* sim-> */ rel_site_list;
    char *mname = json_get_string_value ( json_get_element_with_key ( this_rel, "molecule" ) );
    MolSpecies *ms = /* sim-> */ mol_species_list;
    while ( (ms != NULL) && (strcmp(mname,ms->name)!=0) ) {
      ms = ms->next;
    }
    new_rel->molecule_species = ms;
    new_rel->loc_x = json_get_float_value ( json_get_element_with_key ( this_rel, "location_x" ) );
    new_rel->loc_y = json_get_float_value ( json_get_element_with_key ( this_rel, "location_y" ) );
    new_rel->loc_z = json_get_float_value ( json_get_element_with_key ( this_rel, "location_z" ) );
    new_rel->quantity = json_get_float_value ( json_get_element_with_key ( this_rel, "quantity" ) );
    /* sim-> */ rel_site_list = new_rel;
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

  ReleaseSite *this_site = /* sim-> */ rel_site_list;
  while (this_site != NULL) {
    int i;
    for (i=0; i<this_site->quantity; i++) {
      MolInstance *new_mol_instance = new MolInstance;
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
  char *mol_file_template =  (char *) malloc ( ( strlen(viz_dir) + 1 + strlen(file_template) + ndigits + 10 ) *sizeof(char));
  sprintf ( mol_file_template, "%s/%s", viz_dir, file_template );
  printf ( "Full Template = %s\n", mol_file_template );

  char *sim_step_mol_name = (char *) malloc ( strlen(mol_file_template) + 10 );

  // Run the actual simulation
  printf ( "Begin simulation.\n" );

  int iteration;
  int print_every = exp10(floor(log10((iterations/10))));
  if (print_every < 1) print_every = 1;
  for (iteration=0; iteration<=iterations; iteration++) {
    sprintf ( sim_step_mol_name, mol_file_template, iteration );
    if ((iteration%print_every) == 0) {
      printf ( "Creating mol viz file: \"%s\"\n", sim_step_mol_name );
    }
    FILE *f = fopen ( sim_step_mol_name, "w" );
    // Write the binary marker for this file
    int binary_marker = 1;
    fwrite ( &binary_marker, sizeof(int), 1, f );

    // Write out the molecules from each species
    MolSpecies *this_species = /* sim-> */ mol_species_list;
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

      MolInstance *this_mol_instance = this_species->instance_list;
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

  printf ( "Done C++ simulation.\n" );

  return ( 0 );
}
