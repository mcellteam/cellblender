import bpy
import os
import sys
import io

import cellblender
from cellblender import cellblender_properties, cellblender_operators, ParameterSpace
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

    """ def execute_dipaks_original (self, context):
        mcell = context.scene.mcell
        par_list = net.par_list
        index = -1
        for key in sorted(par_list.keys()):
            index += 1
            mcell.parameters.parameter_list.add()
            mcell.parameters.active_par_index = index
            parameter = mcell.parameters.parameter_list[
                mcell.parameters.active_par_index]

            parameter.name = par_list[key]['name']
            parameter.value = par_list[key]['value']
            parameter.unit = par_list[key]['unit']
            parameter.type = par_list[key]['type']

        return {'FINISHED'}
    """


    def execute(self, context):
        print ( "Importing Parameters" )
        mcell = context.scene.mcell

        ps = cellblender_operators.check_out_parameter_space ( mcell.general_parameters )
        ##print ( "Before adding new parameters:" )
        ##ps.dump(True)
        
        par_list = net.par_list
        index = -1
        for key in sorted(par_list.keys()):
            print ( "Importing key " + str(key) )
            index += 1

            # Dipak's parameters
            mcell.parameters.parameter_list.add()
            mcell.parameters.active_par_index = index
            parameter = mcell.parameters.parameter_list[mcell.parameters.active_par_index]

            parameter.name = par_list[key]['name']
            parameter.value = par_list[key]['value']
            parameter.unit = par_list[key]['unit']
            parameter.type = par_list[key]['type']


            # General parameters
            mcell.general_parameters.parameter_list.add()
            mcell.general_parameters.active_par_index = len(mcell.general_parameters.parameter_list)-1
            
            parameter = mcell.general_parameters.parameter_list[mcell.general_parameters.active_par_index]

            parameter.name = par_list[key]['name']
            parameter.expr = par_list[key]['value']
            parameter.value = par_list[key]['value']
            parameter.unit = par_list[key]['unit']
            parameter.desc = par_list[key]['type']
            
            new_id = ps.define ( parameter.name, parameter.expr )
            parameter.id = new_id
        
            ps.eval_all(False,-1)  # Try forcing the re-evaluation of all parameters

            parameter.expr = ps.get_expr(new_id)
        
            parameter.value = str ( ps.eval_all(False,new_id) )
            parameter.valid = True


        ##print ( "After adding new parameters:" )
        ##ps.dump(True)

        cellblender_operators.check_in_parameter_space ( mcell.general_parameters, ps )

        return {'FINISHED'}


class BNG_OT_molecule_add(bpy.types.Operator):
    bl_idname = "bng.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add imported molecules from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mol_list = net.mol_list
        index = -1
        for key in sorted(mol_list.keys()):
            index += 1
            mcell.molecules.molecule_list.add()
            mcell.molecules.active_mol_index = index
            molecule = mcell.molecules.molecule_list[
                mcell.molecules.active_mol_index]

            molecule.name = mol_list[key]['name']
            molecule.type = mol_list[key]['type']
            molecule.diffusion_constant_expr = mol_list[key]['dif']

        return {'FINISHED'}
    
class BNG_OT_reaction_add(bpy.types.Operator):
    bl_idname = "bng.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add imported reactions from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        rxn_list = net.rxn_list
        index = -1
        for key in sorted(rxn_list.keys()):
            index += 1
            mcell.reactions.reaction_list.add()
            mcell.reactions.active_rxn_index = index
            reaction = mcell.reactions.reaction_list[
                mcell.reactions.active_rxn_index]
		
            reaction.reactants = rxn_list[key]['reactants']
            reaction.products = rxn_list[key]['products']
            reaction.fwd_rate_expr = rxn_list[key]['fwd_rate']

        return {'FINISHED'}

class BNG_OT_release_site_add(bpy.types.Operator):
    bl_idname = "bng.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add imported release sites from BNG-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        rel_list = net.rel_list
        index = -1
        for key in sorted(rel_list.keys()):
            index += 1
            mcell.release_sites.mol_release_list.add()
            mcell.release_sites.active_release_index = index
            release_site = mcell.release_sites.mol_release_list[
                mcell.release_sites.active_release_index]
            
            release_site.name = rel_list[key]['name']
            release_site.molecule = rel_list[key]['molecule']
            release_site.shape = rel_list[key]['shape']
            release_site.orient = rel_list[key]['orient']
            release_site.object_expr = rel_list[key]['object_expr']
            release_site.quantity_type = rel_list[key]['quantity_type']
            release_site.quantity_expr = rel_list[key]['quantity_expr']
            cellblender_operators.check_release_molecule(self, context)
	    
        return {'FINISHED'}

    
def execute_bionetgen(filepath):
    from os.path import exists
    filebasename = os.path.basename(filepath)
    filedirpath = os.path.dirname(filepath)    # dir of the bngl script file
    
    # Just execute it without the search!!!
    os.system("~/proj/MCell/BioNetGen/BioNetGen-2.2.4-stable/BNG2.pl --outdir ~/.config/blender/2.68/scripts/addons/cellblender/bng ~/proj/MCell/src/cellblender_git/cellblender_trunk/bng/")    # execute BNG    
    
    # This search took over a full minute every time it was run!!!
    """
    check_dir = filedirpath;
    n = 0
    while(n!=20):    # iterative search for BNG exe file (starts from the dir containing the bngl script file)
        bng_dir = check_dir  # current dir (+ any unchecked child dir) to be checked 
        checked = {}    # list of dirs for which search is complete
        i = 0
        for (dirpath, dirname, filename) in os.walk(bng_dir):    # Search over the current and previously unchecked child dirs 
            print ( "n=" + str(n) + "Checking " + str(dirpath) + ", " + str(dirname) + ", " + str(filename) )
            if (i == 0):
                check_dir = os.path.dirname(dirpath)    #  mark the parent dir for next search (after current and child dirs are done) 
                i = 1
            if dirpath in checked:  # escape any child dir if already been checked
                continue
            bngpath = os.path.join(dirpath,"BNG2.pl")    # tentative path for the BNG exe. file 
            if os.path.exists(bngpath):    # if BNG exe.file found, proceed for BNG execution
                print ("\nBioNetGen exe found: " + bngpath)
                destpath = os.path.dirname(__file__)
                exe_bng = "    ".join([bngpath, "--outdir", destpath, filepath])    # create command string for BNG execution
                print("*** Started BioNetGen execution ***")
                print("  Command = " + exe_bng )
                os.system(exe_bng)    # execute BNG
                return{'FINISHED'}
            checked.update({dirpath:True})    # store checked directory in the list
        n +=1  
        if (n==20):    # too many iterations; BNG not found, stop further search
            print ("Error running BioNetGen. BNG2.pl not found....")
    """
    return{'FINISHED'}
   
