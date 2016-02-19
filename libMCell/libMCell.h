/* File : libMCell.h */

#include <iostream>
#include <string>
#include <vector>

using namespace std;

class MCellMoleculeInstance; // Forward declaration needed

class MCellMoleculeSpecies {
 private:
  static int next_species_id;
 public:
  string name;
  int species_id;
  string type;
  char type_code;
  double diffusion_constant;

  //vector<MCellMoleculeInstance *> instance_list;
  MCellMoleculeInstance *instance_list;
  int num_instances;

  MCellMoleculeSpecies() {
    species_id = next_species_id++;
    cout << "Constructed a new molecule species " << species_id << endl;
    name = "";
    type = 'v';
    type_code = '\0';
    diffusion_constant = 0.0;
    instance_list = NULL;
    num_instances = 0;
  }

  void set_name ( char *name ) {
    this->name = string(name);
  }

};

class MCellMoleculeInstance {
 public:
  MCellMoleculeSpecies *molecule_species;
  double x, y, z;
  MCellMoleculeInstance *next;
};

class MCellReleaseSite {
 public:
  MCellMoleculeSpecies *molecule_species;
  int mol_id;
  double x, y, z;
  double quantity;
  MCellReleaseSite *next;
  MCellReleaseSite() {
    molecule_species = NULL;
    mol_id = 0;
    x = y = z = quantity = 0;
    next = NULL;
  }

};


class MCellSimulation {
 private:
  char *join_path ( char *p1, char sep, char *p2 );
 public:
  static int num_simulations;

  int num_iterations;
  double time_step;

  vector<MCellMoleculeSpecies *> molecule_species;
  vector<MCellReleaseSite *> molecule_release_sites;

  MCellSimulation() {
    num_simulations++;
    num_iterations = 0;
    time_step = 0.0;
  }
  virtual ~MCellSimulation() {
    num_simulations--;
  }

  void dump() {
    cout << endl << "<> <> <> MCell Data <> <> <>" << endl;
    MCellMoleculeSpecies *this_species = NULL;
    for (int sp_num=0; sp_num<this->molecule_species.size(); sp_num++) {
      this_species = this->molecule_species[sp_num];
      cout << "Simulation contains molecule with species = " << this_species->species_id << endl;
    }
    cout << endl;
    MCellReleaseSite *this_site = NULL;
    for (int sp_num=0; sp_num<this->molecule_release_sites.size(); sp_num++) {
      this_site = this->molecule_release_sites[sp_num];
      if (this_site->mol_id > 0) {
        cout << "Simulation contains release site releasing species = " << this_site->mol_id << endl;
      } else {
        cout << "Simulation contains release site releasing species = " << this_site->molecule_species->name << endl;
      }
    }
    cout << endl;
  }

  void add_molecule_species ( MCellMoleculeSpecies *species );
  void add_molecule_release_site ( MCellReleaseSite *site );
  // MCellMoleculeSpecies *get_molecule_species_by_name ( char *species_name );
  MCellMoleculeSpecies *get_molecule_species_by_id ( int species_id );

  void run_simulation ( char *proj_path );
};

  
