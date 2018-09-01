import numpy as np

class MCellSim(object):
    def __init__(self, seed=42, time=0, dt=0.1):
        self.seed = seed
        self.time = time
        self.species_list = []
        self.dt = dt

    def add_species(self, species):
        self.species_list.append(species)

    def perform_time_step(self):
        for species in self.species_list:
            species.perform_time_step()
        self.time += self.dt

    def run_simulation(self, t_stop):
        while self.time < t_stop:
            self.perform_time_step()

    def print_all_positions(self):
        for species in self.species_list:
            for molecule in species.molecule_list:
                print "Position = (", molecule.x, molecule.y, molecule.z, ")"

class Species(object):
    def __init__(self, diffusion_constant, name):
        self.D = diffusion_constant
        self.name = name
        self.molecule_list = []

    def add_species_to_mcellsim(self, mcellsim):
        mcellsim.add_species(self)
        self.mcellsim = mcellsim

    def add_molecules(self, x, y, z, N):
        for i in range(N):
            self.molecule_list.append(Molecule(self, x, y, z))

    def move_molecule(self, molecule):
        molecule.x += self.D*self.mcellsim.dt

    def perform_time_step(self):
        for molecule in self.molecule_list:
            self.move_molecule(molecule)

class Molecule(object):
    def __init__(self, species, x, y, z):
        self.species = species
        self.x = x
        self.y = y
        self.z = z


if __name__=='__main__':
    mcellsim = MCellSim()

    spec = Species(0.1, 'Ca')
    spec.add_species_to_mcellsim(mcellsim)
    spec.add_molecules(0, 0, 0, 2)

    spec2 = Species(0.2, 'Fast')
    spec2.add_species_to_mcellsim(mcellsim)
    spec2.add_molecules(0, 0, 0, 3)

    mcellsim.print_all_positions()
    mcellsim.perform_time_step()
    mcellsim.print_all_positions()

