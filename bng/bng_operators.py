import bpy
import os
import sys
import io

import cellblender
from cellblender import cellblender_properties, cellblender_operators
from . import net

# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)

class BNG_OT_parameter_add(bpy.types.Operator):
    bl_idname = "bng.parameter_add"
    bl_label = "Add Parameter"
    bl_description = "Add imported parameters to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        par_list = net.par_list
        index = -1
        count = 0
        for key in sorted(par_list.keys()):
            index += 1
            #mcell.parameters.parameter_list.add()
            #mcell.parameters.active_par_index = index
            #parameter = mcell.parameters.parameter_list[
            #    mcell.parameters.active_par_index]

            par_name = par_list[key]['name']
            par_value = par_list[key]['value']
            par_unit = par_list[key]['unit']
            par_type = par_list[key]['type']
            #print ( "Adding parameter \"" + str(par_name) + "\"  =  \"" + str(par_value) + "\"  (" + str(par_unit) + ")" )
            mcell.parameter_system.add_general_parameter_with_values ( par_name, par_value, par_unit, par_type )
            count += 1
        print ( "Added " + str(count) + " parameters" )
        return {'FINISHED'}


class BNG_OT_molecule_add(bpy.types.Operator):
    bl_idname = "bng.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add imported molecules from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        mol_list = net.mol_list
        index = -1
        count = 0
        for key in sorted(mol_list.keys()):
            index += 1
            mcell.molecules.molecule_list.add()
            mcell.molecules.active_mol_index = index
            molecule = mcell.molecules.molecule_list[
                mcell.molecules.active_mol_index]
            #molecule.set_defaults()
            molecule.init_properties(ps)

            molecule.name = mol_list[key]['name']
            molecule.type = mol_list[key]['type']
            #molecule.diffusion_constant.expression = mol_list[key]['dif']
            #molecule.diffusion_constant.param_data.label = "Diffusion Constant"
            molecule.diffusion_constant.set_expr ( mol_list[key]['dif'], ps.panel_parameter_list )
            #print ( "Adding molecule " + str(molecule.name) )
            count += 1
        print ( "Added " + str(count) + " molecules" )
        return {'FINISHED'}


class BNG_OT_reaction_add(bpy.types.Operator):
    bl_idname = "bng.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add imported reactions from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        rxn_list = net.rxn_list
        index = -1
        count = 0
        for key in sorted(rxn_list.keys()):
            index += 1
            mcell.reactions.reaction_list.add()
            mcell.reactions.active_rxn_index = index
            reaction = mcell.reactions.reaction_list[
                mcell.reactions.active_rxn_index]
            #reaction.set_defaults()
            reaction.init_properties(ps)
            		
            reaction.reactants = rxn_list[key]['reactants']
            reaction.products = rxn_list[key]['products']
            #reaction.fwd_rate.expression = rxn_list[key]['fwd_rate']
            #reaction.fwd_rate.param_data.label = "Forward Rate"
            reaction.fwd_rate.set_expr ( rxn_list[key]['fwd_rate'], ps.panel_parameter_list )
            #print ( "Adding reaction  " + str(reaction.reactants) + "  ->  " + str(reaction.products) )
            count += 1
        print ( "Added " + str(count) + " reactions" )
        return {'FINISHED'}


class BNG_OT_release_site_add(bpy.types.Operator):
    bl_idname = "bng.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add imported release sites from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        rel_list = net.rel_list
        index = -1
        count = 0
        for key in sorted(rel_list.keys()):
            index += 1
            mcell.release_sites.mol_release_list.add()
            mcell.release_sites.active_release_index = index
            release_site = mcell.release_sites.mol_release_list[
                mcell.release_sites.active_release_index]
            #release_site.set_defaults()
            release_site.init_properties(ps)
            
            release_site.name = rel_list[key]['name']
            release_site.molecule = rel_list[key]['molecule']
            release_site.shape = rel_list[key]['shape']
            release_site.orient = rel_list[key]['orient']
            release_site.object_expr = rel_list[key]['object_expr']     # This may not be the best name to use for Release Shape
            release_site.quantity_type = rel_list[key]['quantity_type']

            #release_site.quantity.expression = rel_list[key]['quantity_expr']
            release_site.quantity.set_expr ( rel_list[key]['quantity_expr'], ps.panel_parameter_list )

            #cellblender_operators.check_release_molecule(context)
            #print ( "Adding release site " + str(release_site.name) )
            count += 1
        print ( "Added " + str(count) + " release sites" )
        return {'FINISHED'}


def execute_bionetgen(filepath,context):
    mcell = context.scene.mcell
    if mcell.cellblender_preferences.bionetgen_location_valid:
      bngpath = mcell.cellblender_preferences.bionetgen_location
      print ("\nBioNetGen exe found: " + bngpath)
      destpath = os.path.dirname(__file__)
      exe_bng = "  ".join([bngpath, "--outdir", destpath, filepath])    # create command string for BNG execution
      print("*** Starting BioNetGen execution ***")
      print("    Command: " + exe_bng )
      os.system(exe_bng)    # execute BNG
    
    else:
      # Perform the search as done before
      from os.path import exists
      filebasename = os.path.basename(filepath)
      filedirpath = os.path.dirname(filepath)    # dir of the bngl script file
      check_dir = filedirpath;
      n = 0
      while(n!=20):    # iterative search for BNG exe file (starts from the dir containing the bngl script file)
          bng_dir = check_dir  # current dir (+ any unchecked child dir) to be checked 
          checked = {}    # list of dirs for which search is complete
          i = 0
          for (dirpath, dirname, filename) in os.walk(bng_dir):    # Search over the current and previously unchecked child dirs 
              if (i == 0):
                  check_dir = os.path.dirname(dirpath)    #  mark the parent dir for next search (after current and child dirs are done) 
                  i = 1
              if dirpath in checked:  # escape any child dir if already been checked
                  continue
              bngpath = os.path.join(dirpath,"BNG2.pl")    # tentative path for the BNG exe. file
              print ( "Searching for " + bngpath )
              if os.path.exists(bngpath):    # if BNG exe.file found, proceed for BNG execution
                  print ("\nBioNetGen exe found: " + bngpath)
                  destpath = os.path.dirname(__file__)
                  exe_bng = "    ".join([bngpath, "--outdir", destpath, filepath])    # create command string for BNG execution
                  print("*** Started BioNetGen execution ***")
                  os.system(exe_bng)    # execute BNG
                  return{'FINISHED'}
              checked.update({dirpath:True})    # store checked directory in the list
          n +=1  
          if (n==20):    # too many iterations; BNG not found, stop further search
              print ("Error running BioNetGen. BNG2.pl not found....")
    return{'FINISHED'}

