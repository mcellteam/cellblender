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

  f = open ( os.path.join(output_data_dir,"Scene.mdlr"), 'w' )
  if 'initialization' in data_model:
    # Can't write all initialization MDL because booleans like "TRUE" are referenced but not defined in BNGL
    # data_model_to_mdl_3r.write_initialization(data_model['initialization'], f)
    # Write specific parts instead:
    data_model_to_mdl_3r.write_dm_str_val ( data_model['initialization'], f, 'iterations',                'ITERATIONS' )
    data_model_to_mdl_3r.write_dm_str_val ( data_model['initialization'], f, 'time_step',                 'TIME_STEP' )
    data_model_to_mdl_3r.write_dm_str_val ( data_model['initialization'], f, 'vacancy_search_distance',   'VACANCY_SEARCH_DISTANCE', blank_default='10' )

  f.write ( 'INCLUDE_FILE = "Scene.geometry.mdl"\n' )

  if 'parameter_system' in data_model:
    # Write the parameter system
    data_model_to_mdl_3r.write_parameter_system ( data_model['parameter_system'], f )

  # Note that reflective surface classes may be needed by MCell-R
  # If so, it might be good to automate this rather than explicitly requiring it in CellBlender's model.

  if 'define_surface_classes' in data_model:
    data_model_to_mdl_3r.write_surface_classes(data_model['define_surface_classes'], f)

  if 'modify_surface_regions' in data_model:
    data_model_to_mdl_3r.write_modify_surf_regions ( data_model['modify_surface_regions'], f )

  if 'define_molecules' in data_model:
    mols = data_model['define_molecules']
    if 'molecule_list' in mols:
      mlist = mols['molecule_list']
      if len(mlist) > 0:
        f.write ( "#DEFINE_MOLECULES\n" )
        f.write ( "{\n" )
        for m in mlist:
          f.write ( "  %s" % m['mol_name'] )
          if "bngl_component_list" in m:
            f.write( "(" )
            num_components = len(m['bngl_component_list'])
            if num_components > 0:
              for ci in range(num_components):
                c = m['bngl_component_list'][ci]
                f.write( c['cname'] )
                for state in c['cstates']:
                  f.write ( "~" + state )
                if ci < num_components-1:
                  f.write ( "," )
            f.write( ")" )
          f.write ( "\n" )
          f.write ( "  {\n" )
          if m['mol_type'] == '2D':
            f.write ( "    DIFFUSION_CONSTANT_2D = %s\n" % m['diffusion_constant'] )
          else:
            f.write ( "    DIFFUSION_CONSTANT_3D = %s\n" % m['diffusion_constant'] )
          if 'custom_time_step' in m:
            if len(m['custom_time_step']) > 0:
              f.write ( "    CUSTOM_TIME_STEP = %s\n" % m['custom_time_step'] )
          if 'custom_space_step' in m:
            if len(m['custom_space_step']) > 0:
              f.write ( "    CUSTOM_SPACE_STEP = %s\n" % m['custom_space_step'] )
          if 'target_only' in m:
            if m['target_only']:
              f.write("    TARGET_ONLY\n")
          f.write("  }\n")
        f.write ( "}\n" )
      f.write ( "\n" );



  # Write the rest of the stuff
  f.write ( fceri_mdlr )
  f.close()

  f = open ( os.path.join(output_data_dir,"Scene.geometry.mdl"), 'w' )
  data_model_to_mdl_3r.write_geometry(data_model['geometrical_objects'], f)
  f.close()

  f = open ( os.path.join(output_data_dir,"Scene.viz_output.mdl"), 'w' )
  f.write ( 'sprintf(seed,"%05g",SEED)\n\n' )
  data_model_to_mdl_3r.write_viz_out(data_model['viz_output'], data_model['define_molecules'], f)
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


fceri_mdlr = """



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
