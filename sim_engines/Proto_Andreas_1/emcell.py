from minimcell import *

class Electric_species(Species):
    def __init__(self, diffusion_constant, name, electric_field, z):
        self.z = z
        self.electric_field = electric_field
        Species.__init__(self, diffusion_constant, name)

    def move_molecule(self, molecule):
        # super(Electric_species, self).move_molecule(molecule)
        molecule.y += self.D*self.mcellsim.dt*self.z*self.electric_field.Ey

class Electric_field:
    def __init__(self, Ex, Ey, Ez):
        self.Ex = Ex
        self.Ey = Ey
        self.Ez = Ez

if __name__=='__main__':
    electric_field = Electric_field(1, 1, 1)
    mcellsim = MCellSim()

    spec = Species(0.1, 'Ca')
    spec.add_species_to_mcellsim(mcellsim)
    spec.add_molecules(0, 0, 0, 2)

    spec2 = Electric_species(0.2, 'Fast', electric_field, 1)
    spec2.add_species_to_mcellsim(mcellsim)
    spec2.add_molecules(0, 0, 0, 3)

    mcellsim.print_all_positions()
    mcellsim.perform_time_step()
    mcellsim.print_all_positions()
