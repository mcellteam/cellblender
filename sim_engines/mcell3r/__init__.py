import os
import subprocess
import sys
import pickle
import shutil

import cellblender
from . import data_model_to_mdl_3r
from . import run_data_model_mcell_3r

# from . import mdlr2mdl

print ( "Executing MCellR Simulation" )

# Name of this engine to display in the list of choices (Both should be unique within a CellBlender installation)
plug_code = "MCELLR"
plug_name = "MCell Rules"

def print_info():
  global parameter_dictionary
  global parameter_layout
  print ( 50*'==' )
  print ( "This is a preliminary MCell-R engine." )
  print ( 50*'==' )
  for row in parameter_layout:
    for k in row:
      print ( "" + k + " = " + str(parameter_dictionary[k]) )
  print ( 50*'==' )

def reset():
  global parameter_dictionary
  print ( "Reset was called" )
  parameter_dictionary['Output Detail (0-100)']['val'] = 20

# Get data from Blender / CellBlender
import bpy

# Force some defaults which would otherwise be empty (""):
shared_path = ""
mcell_path = "mcell/build/mcell"
mcell_lib_path = "mcell/lib/"
bionetgen_path = "bionetgen/bng2/BNG2.pl"
nfsim_path = ""

#try:
#  mcell_path = bpy.context.scene.mcell.cellblender_preferences.mcell_binary
#except:
#  mcell_path = ""


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
  'Shared Path':    {'val': shared_path,    'as':'filename', 'desc':"Shared Path",         'icon':'FORCE_LENNARDJONES'},
  'MCellR Path':    {'val': mcell_path,     'as':'filename', 'desc':"MCellR Path",         'icon':'FORCE_LENNARDJONES'},
  'MCellRlib Path': {'val': mcell_lib_path, 'as':'filename', 'desc':"MCellR Library Path", 'icon':'FORCE_LENNARDJONES'},
  'BioNetGen Path': {'val': bionetgen_path, 'as':'filename', 'desc':"BioNetGen Path",      'icon':'OUTLINER_DATA_MESH'},
  #'NFSim Path':     {'val': nfsim_path,     'as':'filename', 'desc':"NFSim Path",          'icon':'DRIVER'},
  'Output Detail (0-100)': {'val': 20, 'desc':"Amount of Information to Print (0-100)",    'icon':'INFO'},
  'Print Information': {'val': print_info, 'desc':"Print information about Limited Python Simulation"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Shared Path'],
  ['MCellR Path'],
  ['MCellRlib Path'],
  ['BioNetGen Path'],
  #['NFSim Path'],
  ['Output Detail (0-100)'],
  ['Print Information', 'Reset']
]


def makedirs_exist_ok ( path_to_build, exist_ok=False ):
    # Needed for old python which doesn't have the exist_ok option!!!
    print ( " Make dirs for " + path_to_build )
    parts = path_to_build.split(os.sep)  # Variable "parts" should be a list of subpath sections. The first will be empty ('') if it was absolute.
    # print ( "  Parts = " + str(parts) )
    full = ""
    if len(parts[0]) == 0:
      full = os.sep
    for p in parts:
      full = os.path.join(full,p)
      # print ( "   " + full )
      if not os.path.exists(full):
        os.makedirs ( full, exist_ok=True )

def prepare_runs ( data_model, project_dir, data_layout=None ):

  output_detail = parameter_dictionary['Output Detail (0-100)']['val']

  if output_detail > 0: print ( "The current MCell-R engine doesn't really support the prepare/run model.\nIt just runs directly." )

  if output_detail > 0: print ( "Converting the data model to an MDLR file (faking it for now with fceri_mdlr)." )

  print ( "Running with python " + sys.version )   # This will be Blender's Python which will be 3.5+
  print ( "Project Dir: " + project_dir )          # This will be .../blend_file_name_files/mcell
  print ( "Data Layout: " + str(data_layout) )     # This will typically be None

  output_data_dir = os.path.join ( project_dir, "output_data" )
  makedirs_exist_ok ( output_data_dir, exist_ok=True )


  global fceri_mdlr
  global fceri_geometry
  global fceri_viz_out

  f = open ( os.path.join(output_data_dir,"Scene.mdlr"), 'w' )
  f.write ( fceri_mdlr )
  f.close()

  f = open ( os.path.join(output_data_dir,"Scene.geometry.mdl"), 'w' )
  data_model_to_mdl_3r.write_geometry(data_model['geometrical_objects'], f)
  f.close()

  f = open ( os.path.join(output_data_dir,"Scene.viz_output.mdl"), 'w' )
  f.write ( fceri_viz_out )
  f.close()

  f = open ( os.path.join(output_data_dir,"mcellr.yaml"), 'w' )
  f.write ( "bionetgen: '" + os.path.join(parameter_dictionary['Shared Path']['val'],parameter_dictionary['BioNetGen Path']['val']) + "'\n" )
  f.write ( "libpath: '" + os.path.join(parameter_dictionary['Shared Path']['val'],parameter_dictionary['MCellRlib Path']['val']) + "'\n" )
  f.write ( "mcell: '" + os.path.join(parameter_dictionary['Shared Path']['val'],parameter_dictionary['MCellR Path']['val']) + "'\n" )
  f.close()

  # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

  fs = data_model['simulation_control']['start_seed']
  ls = data_model['simulation_control']['end_seed']

  engine_path = os.path.dirname(__file__)

  # python mdlr2mdl.py -ni ./fceri_files/fceri.mdlr -o ./fceri_files/fceri.mdl
  subprocess.call ( [ "python", os.path.join(engine_path, "mdlr2mdl.py"), "-ni", "Scene.mdlr", "-o", "Scene.mdl" ], cwd=output_data_dir )

  # run_data_model_mcell_3r.run_mcell_sweep(['-pd',project_dir,'-b',parameter_dictionary['MCellR Path']['val'],'-fs',fs,'-ls',ls],data_model={'mcell':data_model})



  # This should return a list of run command dictionaries.
  # Each run command dictionary must contain a "cmd" key, an "args" key, and a "wd" key.
  # The cmd key will refer to a command string suitable for popen.
  # The args key will refer to an argument list suitable for popen.
  # The wd key will refer to a working directory string.
  # Each run command dictionary may contain any other keys helpful for post-processing.
  # The run command dictionary list will be passed on to the postprocess_runs function.

  # The data_layout should be a dictionary something like this:

  #  {
  #   "version": 2,
  #   "data_layout": [
  #    ["/DIR", ["output_data"]],
  #    ["dc_a", [1e-06, 1e-05]],
  #    ["nrel", [100.0, 200.0, 300.0]],
  #    ["/FILE_TYPE", ["react_data", "viz_data"]],
  #    ["/SEED", [100, 101]]
  #   ]
  #  }

  # That last dictionary describes the directory structure that CellBlender expects to find on the disk

  # For now return no commands at all since the run has already taken place
  command_list = []

  if output_detail > 0: print ( "Inside MCellR Engine, project_dir=" + project_dir )

  return ( command_list )


def postprocess_runs ( data_model, command_strings ):
  # Move and/or transform data to match expected CellBlender file structure as required
  pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass


### The following strings are short cuts (should come from data model)

fceri_viz_out = """VIZ_OUTPUT
{
  MODE = CELLBLENDER
  FILENAME = "./viz_data/seed_00001/Scene"
  MOLECULES
  {
    NAME_LIST {ALL_MOLECULES}
    ITERATION_NUMBERS {ALL_DATA @ ALL_ITERATIONS}
  }
}
"""


fceri_mdlr = """ITERATIONS = 50
TIME_STEP = 5e-06
VACANCY_SEARCH_DISTANCE = 100

INCLUDE_FILE = "Scene.geometry.mdl"

MODIFY_SURFACE_REGIONS
{
   EC[wall] {
      SURFACE_CLASS = reflect
   }
   EC[ALL] {
      SURFACE_CLASS = reflect
   }
   CP[PM] {
      SURFACE_CLASS = reflect
   }
   CP[ALL] {
      SURFACE_CLASS = reflect
   }
}

DEFINE_SURFACE_CLASSES
{
   reflect {
   REFLECTIVE = ALL_MOLECULES
   }
   reflecto {
   REFLECTIVE = ALL_MOLECULES
   }
   reflectop {
   REFLECTIVE = ALL_MOLECULES
   }
}

/* Model Parameters */
   Nav = 6.022e8               /* Avogadro number based on a volume size of 1 cubic um */
   rxn_layer_t = 0.01
   vol_wall = 0.88/rxn_layer_t  /*Surface area*/
   vol_EC = 39
   vol_PM = 0.01/rxn_layer_t  /*Surface area*/
   vol_CP = 1

/* Original Values
   Lig_tot = 6.0e3
   Rec_tot = 4.0e2
   Lyn_tot = 2.8e2
   Syk_tot = 4e2
*/

/* Testing Values */
   Lig_tot = 6.0e2
   Rec_tot = 4.0e1
   Lyn_tot = 2.8e1
   Syk_tot = 4e1

   kp1 = 0.000166057788110262*Nav
   km1 = 0.00
   kp2 = 1.66057788110262e-06/rxn_layer_t
   km2 = 0.00
   kpL = 0.0166057788110262/rxn_layer_t
   kmL = 20
   kpLs = 0.0166057788110262/rxn_layer_t
   kmLs = 0.12
   kpS = 0.0166057788110262*Nav
   kmS = 0.13
   pLb = 30
   pLbs = 100
   pLg = 1
   pLgs = 3
   pLS = 30
   pLSs = 100
   pSS = 100
   pSSs = 200
   dm = 0.1
   dc = 0.1

/* Diffusion bloc */
   T = 298.15      /* Temperature, K */
   h = rxn_layer_t      /* Thickness of 2D compartment, um */
   Rs = 0.002564      /* Radius of a (spherical) molecule in 3D compartment, um */
   Rc = 0.0015      /* Radius of a (cylindrical) molecule in 2D compartment, um */
   gamma = 0.5722      /* Euler's constant */
   KB = 1.3806488e-19     /* Boltzmann constant, cm^2.kg/K.s^2 */
   mu_wall = 1e-9      /* Viscosity in compartment wall, kg/um.s */
   mu_EC = 1e-9      /* Viscosity in compartment EC, kg/um.s */
   mu_PM = 1e-9      /* Viscosity in compartment PM, kg/um.s */
   mu_CP = 1e-9      /* Viscosity in compartment CP, kg/um.s */



#DEFINE_MOLECULES
{
  Lig(l,l)
  {
      DIFFUSION_CONSTANT_3D = 8.51e-7
  }
  Lyn(U,SH2)
  {
      DIFFUSION_CONSTANT_2D =  1.7e-7
  }
  Syk(tSH2,l~Y~pY,a~Y~pY)
  {
      DIFFUSION_CONSTANT_3D = 8.51e-7
  }
  Rec(a,b~Y~pY,g~Y~pY)
  {
      DIFFUSION_CONSTANT_2D =  1.7e-7
  }
}



#DEFINE_REACTIONS
{
    /* Ligand-receptor binding      */
     Rec(a) + Lig(l,l) <-> Rec(a!1).Lig(l!1,l)  [kp1, km1]

    /* Receptor-aggregation*/
     Rec(a) + Lig(l,l!+) <-> Rec(a!2).Lig(l!2,l!+)  [kp2, km2]

    /* Constitutive Lyn-receptor binding  */
     Rec(b~Y) + Lyn(U,SH2) <-> Rec(b~Y!1).Lyn(U!1,SH2)  [kpL, kmL]

    /* Transphosphorylation of beta by constitutive Lyn  */
     Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)  [pLb]

    /* Transphosphorylation of gamma by constitutive Lyn  */
     Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)  [pLg]

    /* Lyn-receptor binding through SH2 domain  */
     Rec(b~pY) + Lyn(U,SH2) <-> Rec(b~pY!1).Lyn(U,SH2!1)  [kpLs, kmLs]

    /* Transphosphorylation of beta by SH2-bound Lyn  */
     Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)  [pLbs]

    /* Transphosphorylation of gamma by SH2-bound Lyn  */
     Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)  [pLgs]

    /* Syk-receptor binding through tSH2 domain  */
     Rec(g~pY) + Syk(tSH2) <-> Rec(g~pY!1).Syk(tSH2!1)  [kpS, kmS]

    /* Transphosphorylation of Syk by constitutive Lyn  */
     Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)  [pLS]

    /* Transphosphorylation of Syk by SH2-bound Lyn  */
     Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)  [pLSs]

    /* Transphosphorylation of Syk by Syk not phosphorylated on aloop  */
     Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)  [pSS]

    /* Transphosphorylation of Syk by Syk phosphorylated on aloop  */
     Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)  [pSSs]

    /* Dephosphorylation of Rec beta  */
     Rec(b~pY) -> Rec(b~Y)  [dm]

    /* Dephosphorylation of Rec gamma  */
     Rec(g~pY) -> Rec(g~Y)  [dm]

    /* Dephosphorylation of Syk at membrane  */
     Syk(tSH2!+,l~pY) -> Syk(tSH2!+,l~Y)  [dm]
     Syk(tSH2!+,a~pY) -> Syk(tSH2!+,a~Y)  [dm]

    /* Dephosphorylation of Syk in cytosol  */
     Syk(tSH2,l~pY) -> Syk(tSH2,l~Y)  [dc]
     Syk(tSH2,a~pY) -> Syk(tSH2,a~Y)  [dc]
}


#INSTANTIATE Scene OBJECT
{
  EC OBJECT EC {}
  CP OBJECT CP {
    PARENT = EC
    MEMBRANE = PM OBJECT CP[ALL]
  }

   ligand_rel RELEASE_SITE
   {
    SHAPE = Scene.EC[ALL] - Scene.CP[ALL]
    MOLECULE = @EC::Lig(l,l)
    NUMBER_TO_RELEASE = Lig_tot
    RELEASE_PROBABILITY = 1
   }
   lyn_rel RELEASE_SITE
   {
    SHAPE = Scene.CP[PM]
    MOLECULE = @PM::Lyn(U,SH2)
    NUMBER_TO_RELEASE = Lyn_tot
    RELEASE_PROBABILITY = 1
   }
   syk_rel RELEASE_SITE
   {
    SHAPE = Scene.CP
    MOLECULE = @CP::Syk(tSH2,l~Y,a~Y)
    NUMBER_TO_RELEASE = Syk_tot
    RELEASE_PROBABILITY = 1
   }
   receptor_rel RELEASE_SITE
   {
    SHAPE = Scene.CP[PM]
    MOLECULE = @PM::Rec(a,b~Y,g~Y)
    NUMBER_TO_RELEASE = Rec_tot
    RELEASE_PROBABILITY = 1
   }

}

/* Observables bloc */
#REACTION_DATA_OUTPUT
{
   STEP = 1e-6

    /*LynFree*/
    {COUNT[Lyn(U,SH2), WORLD] } => "./react_data/LycFree.dat"

    //{COUNT[Rec.Rec, WORLD] } => "./react_data/RecDim.dat"
    //COUNT[Lyn(U!1).Rec(b~Y!1,a), WORLD]} => "./react_data/LynRec.dat"
    //COUNT[Lyn(U!1).Rec(b~Y!1,a!2).Lig(l!2), WORLD]} => "./react_data/LynRecLig.dat"

    {COUNT[Rec(b~pY!?), WORLD] } => "./react_data/RecPbeta.dat"
    {COUNT[Rec(a!1).Lig(l!1,l), WORLD]} => "./react_data/RecMon.dat"
    {COUNT[Rec(a!1).Lig(l!1,l!2).Rec(a!2), WORLD]} => "./react_data/RecDim.dat"
    {COUNT[Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b!3).Rec(a!1,b), WORLD]} => "./react_data/RecRecLigLyn.dat"

    {COUNT[Rec(g~pY),WORLD] + COUNT[Rec(g~pY!+), WORLD] } => "./react_data/RecPgamma.dat"
    {COUNT[Rec(g~pY!1).Syk(tSH2!1), WORLD] } => "./react_data/RecSyk.dat"
    {COUNT[Rec(g~pY!1).Syk(tSH2!1,a~pY), WORLD] } => "./react_data/RecSykPS.dat"

    //{COUNT[Syk, WORLD] } => "./react_data/SykTest.dat"
    //{COUNT[Lyn, WORLD] } => "./react_data/LynTest.dat"
    //{COUNT[Rec, WORLD] } => "./react_data/RecTest.dat"

}


INCLUDE_FILE = "Scene.viz_output.mdl"

"""
