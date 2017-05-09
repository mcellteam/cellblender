/* File : libMCell.cpp */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <math.h>

#include <iostream>
#include <string>
#include <vector>

#include "StorageClasses.h"
#include "libMCell.h"

#include "rng.h"

using namespace std;

int MCellSimulation::num_simulations = 0;

char *MCellSimulation::join_path ( char *p1, char sep, char *p2 ) {
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

void MCellSimulation::set_seed ( unsigned int seed ) {
  this->seed = seed;
}

void MCellSimulation::add_molecule_species ( MCellMoleculeSpecies *species ) {
  molecule_species[species->name.c_str()] = species;
}

void MCellSimulation::add_decay_reaction ( MCellMoleculeSpecies *reactant, double rate ) {
  MCellReaction *rxn = new MCellReaction();
  rxn->reactants.append ( reactant );
  rxn->rate = rate;
  reactions.append ( rxn );
}

void MCellSimulation::add_molecule_release_site ( MCellReleaseSite *site ) {
  molecule_release_sites.append ( site );
}

MCellMoleculeSpecies *MCellSimulation::get_molecule_species_by_name ( char *mol_name ) {
  MCellMoleculeSpecies *found = NULL;
  found = this->molecule_species[mol_name];
  return ( found );
}

/*
void MCellSimulation::pick_displacement( MCellMoleculeInstance *mol, double scale, struct rng_state *rng ) {
  mol->x = scale * rng_gauss(rng) * .70710678118654752440;
  mol->y = scale * rng_gauss(rng) * .70710678118654752440;
  mol->z = scale * rng_gauss(rng) * .70710678118654752440;
}
*/

void MCellSimulation::stuff_seed ( char *path, unsigned int seed ) {
  // Temporary just to get seeds working
  printf ( "Original path: \"%s\"\n", path );
  char temp_buf[100];
  sprintf ( temp_buf, "%d", seed );
  printf ( "Seed to stuff: \"%s\"\n", temp_buf );
  char *seed_string = strstr ( path, "seed_" );
  if (seed_string != NULL) {
    printf ( "Found seed: \"%s\"\n", seed_string );
    int l = strlen(temp_buf);
    int insert_at;
    for (int i=0; i<l; i++) {
      insert_at = strlen("seed_00001") - (i+1);
      printf ( "  Insert \"%c\" from index %d at index %d\n", temp_buf[l-(i+1)], l-(i+1), insert_at );
      seed_string[insert_at] = temp_buf[l-(i+1)];
    }
  }
  printf ( "Updated path: \"%s\"\n", path );
}

void MCellSimulation::run_simulation ( char *proj_path ) {
  int iteration;

  if (this->print_detail >= 10) printf ( "Project path = \"%s\"\n", proj_path );
  if (this->print_detail >= 15) printf ( "Seed = %d\n", this->seed );

  // ##### Clear out the old data

  if (this->print_detail >= 20) printf ( "Creating directories ...\n" );

  char *output_dir = join_path ( proj_path, '/', "output_data" );
  mkdir ( output_dir, 0755 );

  char *react_dir = join_path ( output_dir, '/', "react_data" );
  mkdir ( react_dir, 0755 );

  char *react_seed_dir = join_path ( react_dir, '/', "seed_00001" );
  this->stuff_seed ( react_seed_dir, this->seed );
  mkdir ( react_seed_dir, 0755 );

  char *viz_dir = join_path ( output_dir, '/', "viz_data" );
  mkdir ( viz_dir, 0755 );

  char *viz_seed_dir = join_path ( viz_dir, '/', "seed_00001" );
  this->stuff_seed ( viz_seed_dir, this->seed );
  mkdir ( viz_seed_dir, 0755 );


  if (this->print_detail >= 20) printf ( "Generating Data ...\n" );


  // # Create structures and instances for each molecule that is released (note that release patterns are not handled)

  MCellReleaseSite *this_site;

  for (int rs_num=0; rs_num<this->molecule_release_sites.get_num_items(); rs_num++) {
    if (this->print_detail >= 40) cout << "Release Site " << rs_num << endl;
    this_site = this->molecule_release_sites[rs_num];
    if (this->print_detail >= 40) cout << "  Releasing " << this_site->quantity << " molecules of type " << this_site->molecule_species->name << endl;
    for (int i=0; i<this_site->quantity; i++) {
      if (this->print_detail >= 80) cout << "  Releasing a molecule of type " << this_site->molecule_species->name << endl;
      MCellMoleculeInstance *new_mol_instance = new MCellMoleculeInstance();
      new_mol_instance->next = this_site->molecule_species->instance_list;
      this_site->molecule_species->instance_list = new_mol_instance;
      this_site->molecule_species->num_instances += 1;
      new_mol_instance->molecule_species = this_site->molecule_species;
      new_mol_instance->x = this_site->x;
      new_mol_instance->y = this_site->y;
      new_mol_instance->z = this_site->z;
      for (int i=0; i<this->mol_creation_event_handlers.get_num_items(); i++) {
        this->mol_creation_event_handlers[i]->execute(new_mol_instance);
      }
    }
  }

  // # Figure out the number of digits needed for file names

  int ndigits = 1 + log10(num_iterations+1);
  if (this->print_detail >= 30) printf ( "File names will require %d digits\n", ndigits );

  // Produce file name templates for viz output files

  char *template_template = "seed_00001/Scene.cellbin.%%0%dd.dat";
  char *file_template = (char *) malloc ( strlen(template_template) + (ndigits*sizeof(char)) + 10 );
  sprintf ( file_template, template_template, ndigits );
  this->stuff_seed ( file_template, this->seed );
  if (this->print_detail >= 30) printf ( "File Template = %s\n", file_template );

  char *f_template =  (char *) malloc ( ( strlen(viz_dir) + 1 + strlen(file_template) + ndigits + 10 ) *sizeof(char));
  sprintf ( f_template, "%s/%s", viz_dir, file_template );
  if (this->print_detail >= 30) printf ( "Full Template = %s\n", f_template );

  char *sim_step_mol_name = (char *) malloc ( strlen(f_template) + 10 );

  // Create the count files for each molecule species (doesn't currently use the count specifications)

  FILE **count_files;
  count_files = (FILE **) malloc ( this->molecule_species.get_num_items() * sizeof(FILE *) );

  MCellMoleculeSpecies *this_species;
  if (this->print_detail >= 20) cout << "Set up count files for " << this->molecule_species.get_num_items() << " species." << endl;
  for (int sp_num=0; sp_num<this->molecule_species.get_num_items(); sp_num++) {
    char *react_file_name;
    this_species = this->molecule_species[this->molecule_species.get_key(sp_num)];
    react_file_name = (char *) malloc ( strlen(react_dir) + 1 + strlen ( "/seed_00001/" ) + strlen ( this_species->name.c_str() ) + strlen ( ".World.dat" ) + 10 );
    this->stuff_seed ( react_file_name, this->seed );
    sprintf ( react_file_name, "%s/seed_00001/%s.World.dat", react_dir, this_species->name.c_str() );
    this->stuff_seed ( react_file_name, this->seed );
    if (this->print_detail >= 40) cout << "Setting up count file for species " << this_species->name << " at " << react_file_name << endl;
    count_files[sp_num] = fopen ( react_file_name, "w" );
  }

  // Run the actual simulation

  if (this->print_detail >= 20) cout << "Begin libMCell simulation with seed " << this->seed << endl << endl;

  MCellRandomNumber_mrng *mcell_random = new MCellRandomNumber_mrng((uint32_t)(this->seed));

  // Note that the seed value wasn't contributing to the rng_gauss() result as detected by following debug statement:
  // if (this->print_detail >= 20) cout << "  First random number would be " << mcell_random->rng_gauss() << endl << endl;

  int print_every = pow(10, floor(log10((num_iterations/10))));
  if (print_every < 1) print_every = 1;
  for (iteration=0; iteration<=num_iterations; iteration++) {

    if ( (iteration % print_every) == 0 ) {
      if (this->print_detail >= 20) cout << "Iteration " << iteration << ", t=" << (time_step*iteration) << "   (from libMCell's run_simulation)" << endl;
    }

    for (int i=0; i<this->timer_event_handlers.get_num_items(); i++) {
      this->timer_event_handlers[i]->execute();
    }

    // Count the molecules

    if (this->print_detail >= 40) cout << "Count molecules for " << this->molecule_species.get_num_items() << " species." << endl;
    for (int sp_num=0; sp_num<this->molecule_species.get_num_items(); sp_num++) {
      this_species = this->molecule_species[this->molecule_species.get_key(sp_num)];
      MCellMoleculeInstance *this_mol_instance = this_species->instance_list;
      long count = 0;
      while (this_mol_instance != NULL) {
        count++;
        this_mol_instance = this_mol_instance->next;
      }
      fprintf ( count_files[sp_num], "%g %ld\n", iteration*time_step, count );
    }

    // Create the viz output file for this iteration

    sprintf ( sim_step_mol_name, f_template, iteration );
    if ((iteration%print_every) == 0) {
      if (this->print_detail >= 50) printf ( "Creating mol viz file: \"%s\"\n", sim_step_mol_name );
    }
    FILE *f = fopen ( sim_step_mol_name, "w" );
    // Write the binary marker for this file
    int binary_marker = 1;
    fwrite ( &binary_marker, sizeof(int), 1, f );

    // Move all molecules and produce viz output

    MCellMoleculeSpecies *this_species;
    if (this->print_detail >= 40) cout << "Iterate over " << this->molecule_species.get_num_items() << " species." << endl;
    for (int sp_num=0; sp_num<this->molecule_species.get_num_items(); sp_num++) {
      this_species = this->molecule_species[this->molecule_species.get_key(sp_num)];
      if (this->print_detail >= 80) cout << "Simulating for species " << this_species->name << endl;

      // Output the header of the mol viz file

      unsigned char name_len = 0x0ff & this_species->name.length();
      fwrite ( &name_len, sizeof(unsigned char), 1, f );
      fwrite ( this_species->name.c_str(), sizeof(unsigned char), this_species->name.length(), f );
      unsigned char type_code = 0x0ff & (int)(this_species->type_code);
      fwrite ( &type_code, sizeof(unsigned char), 1, f );
      int total_values = 3 * this_species->num_instances;
      fwrite ( &total_values, sizeof(int), 1, f );

      MCellMoleculeInstance *this_mol_instance = this_species->instance_list;
      float float_val;
      double dc = this_species->diffusion_constant;

      // From one branch of mcell_species.c ...  Determine the actual space step and time step
      double ds = sqrt(16.0 * 1.0e8 * dc * time_step);

      while (this_mol_instance != NULL) {
        float_val = this_mol_instance->x;
        fwrite ( &float_val, sizeof(float), 1, f );
        float_val = this_mol_instance->y;
        fwrite ( &float_val, sizeof(float), 1, f );
        float_val = this_mol_instance->z;
        fwrite ( &float_val, sizeof(float), 1, f );
        // NOTE: The following equations are from pick_displacement in diffuse.c
        this_mol_instance->x += ds * mcell_random->rng_gauss() * 0.70710678118654752440;
        this_mol_instance->y += ds * mcell_random->rng_gauss() * 0.70710678118654752440;
        this_mol_instance->z += ds * mcell_random->rng_gauss() * 0.70710678118654752440;
        this_mol_instance = this_mol_instance->next;
      }

    }

    fclose(f);

    if (has_reactions) {
      // Perform approximate decay reactions for now  (TODO: Make this realistic)
      MCellReaction *this_rxn;
      for (int sp_num=0; sp_num<this->molecule_species.get_num_items(); sp_num++) {
        this_species = this->molecule_species[this->molecule_species.get_key(sp_num)];
        if (this_species->instance_list != NULL) {
          for (int rx_num=0; rx_num<this->reactions.get_num_items(); rx_num++) {
            this_rxn = this->reactions[rx_num];
            if (this_rxn->reactants[0] == this_species) {
              // This reaction applies to this molecule
              double fraction_to_remove = this_rxn->rate * time_step;
              double amount_to_remove = fraction_to_remove * this_species->num_instances;
              int num_to_remove = (int)amount_to_remove;
              if ( (mcell_random->generate() % 1000)/1000.0 < (amount_to_remove - num_to_remove) ) {
                num_to_remove += 1;
              }
              MCellMoleculeInstance *first;
              for (int i=0; i<num_to_remove; i++) {
                first = this_species->instance_list;
                if (first != NULL) {
                  this_species->instance_list = this_species->instance_list->next;
                  this_species->num_instances += -1;
                  delete ( first );
                }
              }
            }
          }
        }
      }
    }

  }

  // Close the count files for each molecule species

  for (int sp_num=0; sp_num<this->molecule_species.get_num_items(); sp_num++) {
    fclose ( count_files[sp_num] );
  }


}

void MCellSimulation::dump_state ( void ) {
  cout << "Dumping state of simulation" << endl;

  MCellMoleculeSpecies *this_species;
  MCellReaction *this_rxn;
  MCellReleaseSite *this_site;

  cout << "  Seed = " << this->seed << endl;

  cout << "  Molecules:" << endl;
  for (int sp_num=0; sp_num<this->molecule_species.get_num_items(); sp_num++) {
    this_species = this->molecule_species[this->molecule_species.get_key(sp_num)];
    cout << "    Molecule \"" << this_species->name << "\" is type " << this_species->type << " with dc = " << this_species->diffusion_constant << endl;
  }

  cout << "  Reactions:" << endl;
  for (int rx_num=0; rx_num<this->reactions.get_num_items(); rx_num++) {
    this_rxn = this->reactions[rx_num];
    cout << "    Reaction: ";
    for (int m_num=0; m_num<this_rxn->reactants.get_num_items(); m_num++) {
      cout << this_rxn->reactants[m_num]->name << " ";
    }
    cout << "  ->  ";
    for (int m_num=0; m_num<this_rxn->products.get_num_items(); m_num++) {
      cout << this_rxn->products[m_num]->name << " ";
    }
    cout << "  with rate " << this_rxn->rate << endl;
  }

  cout << "  Release Sites:" << endl;
  for (int rs_num=0; rs_num<this->molecule_release_sites.get_num_items(); rs_num++) {
    this_site = this->molecule_release_sites[rs_num];
    cout << "    Release " << this_site->quantity << " molecules of type \"" << this_site->molecule_species->name << "\"" << endl;
  }

}
