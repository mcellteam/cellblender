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


// This is a "user-land" iteration callback class
class time_ticker : public MCellTimerEvent {
 public:
  long t = 0;
  // This constructor adds this event's handler to the timer events list
  time_ticker(MCellSimulation *sim) {
    t = 0;
    sim->timer_event_handlers.append ( this );
  }
  // This is the callback that's called whenever the iteration is changed
  void execute() {
    cout << "Time Ticker = " << t << endl;
    t += 1;
  }
};


// This is a "user-land" molecule counting callback class
class mol_counter : public MCellMolCreationEvent {
 public:
  long count = 0;
  string name = "";
  bool named = false;
  // This constructor will count all molecules
  mol_counter(MCellSimulation *sim) {
    time = 0.0;
    count = 0;
    name = "";
    named = false;
    sim->mol_creation_event_handlers.append ( this );
  }
  // This constructor will only count the molecule species specified
  mol_counter(MCellSimulation *sim, MCellMoleculeSpecies *mol) {
    time = 0.0;
    count = 0;
    name = mol->name;
    named = true;
    sim->mol_creation_event_handlers.append ( this );
  }
  // This is the callback function that libMCell calls whenever it creates any molecule
  void execute(MCellMoleculeInstance *mol) {
    // Just print out the counts (they could go to a file or for any other use)
    if ( !named ) {
      count += 1;
      cout << "Unnamed Mol Count = " << count << endl;
    } else if (mol->molecule_species->name == this->name) {
      count += 1;
      cout << "Mol " << this->name << " Count = " << count << endl;
    }
  }
};



int main ( int argc, char *argv[] ) {

  cout << "\n\n" << endl;
  cout << "*********************************************" << endl;
  cout << "*   MCell C++ Test Program using libMCell   *" << endl;
  cout << "*********************************************" << endl;
  cout << "\n" << endl;

  //This is a hard-coded simulation as a simple example of the API

  MCellSimulation *mcell = new MCellSimulation();

  // Create a time ticker
  time_ticker *my_ticker = new time_ticker ( mcell );

  // Create Molecule A Species
  MCellMoleculeSpecies *mol_a = new MCellMoleculeSpecies();
  mol_a->name = "A";
  mol_a->diffusion_constant = 1e-6;
  mcell->add_molecule_species( mol_a );

  // Create Molecule B Species
  MCellMoleculeSpecies *mol_b = new MCellMoleculeSpecies();
  mol_b->name = "B";
  mol_b->diffusion_constant = 2e-5;
  mcell->add_molecule_species( mol_b );

  // Set up an initial release of A molecules
  MCellReleaseSite *rel_a = new MCellReleaseSite();
  rel_a->x = 0.0;
  rel_a->y = 0.0;
  rel_a->z = 0.0;
  rel_a->molecule_species = mol_a;
  rel_a->quantity = 300;
  mcell->add_molecule_release_site ( rel_a );

  // Set up an initial release of B molecules
  MCellReleaseSite *rel_b = new MCellReleaseSite();
  rel_b->x = 0.3;
  rel_b->y = 0.2;
  rel_b->z = 0.1;
  rel_b->molecule_species = mol_b;
  rel_b->quantity = 700;
  mcell->add_molecule_release_site ( rel_b );

  // Add counters to count all, A, and B
  mol_counter *all_counter = new mol_counter ( mcell );
  mol_counter *a_counter = new mol_counter ( mcell, mol_a );
  mol_counter *b_counter = new mol_counter ( mcell, mol_b );

  // Set up the iterations and time step (maybe this should be done earlier?)
  mcell->num_iterations = 200;
  mcell->time_step = 1e-7;

  // Run the simulation in the current "." directory
  mcell->run_simulation(".");

  // Print out the final counts
  cout << endl << endl << "After simulation:" << endl;
  cout << "  Count[ALL] = " << all_counter->count << endl;
  cout << "  Count[A] = "   << a_counter->count << endl;
  cout << "  Count[B] = "   << b_counter->count << endl;


  return ( 0 );
}

