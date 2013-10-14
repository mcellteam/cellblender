import bpy
import os
import sys
import io
import json

import cellblender
from cellblender import cellblender_properties, cellblender_operators
#from . import sbml2json
#from . import sbml2json
# We use per module class registration/unregistration

filePath = ''

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)

class SBML_OT_parameter_add(bpy.types.Operator):
    
    bl_idname = "sbml.parameter_add"
    bl_label = "Add Parameter"
    bl_description = "Add imported parameters to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        filePointer= open(filePath + '.json','r')
        jfile = json.load(filePointer)        
        par_list = jfile['par_list']
        index = -1
        for key in par_list:
            index += 1
            mcell.parameters.parameter_list.add()
            mcell.parameters.active_par_index = index
            parameter = mcell.parameters.parameter_list[
                mcell.parameters.active_par_index]

            parameter.name = str(key['name'])
            parameter.value = str(key['value'])
            parameter.unit = str(key['unit'])
            parameter.type = str(key['type'])
 
        return {'FINISHED'}


class SBML_OT_molecule_add(bpy.types.Operator):
    bl_idname = "sbml.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add imported molecules from SBML-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        filePointer= open(filePath + '.json','r')
        jfile = json.load(filePointer)        
        mol_list = jfile['mol_list']
        index = -1
        for key in mol_list:
            index += 1
            mcell.molecules.molecule_list.add()
            mcell.molecules.active_mol_index = index
            molecule = mcell.molecules.molecule_list[
                mcell.molecules.active_mol_index]

            molecule.name = str(key['name'])
            molecule.type = str(key['type'])
            molecule.diffusion_constant_expr = str(key['dif'])

        return {'FINISHED'}
    
class SBML_OT_reaction_add(bpy.types.Operator):
    bl_idname = "sbml.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add imported reactions from SBML-generated network"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        filePointer= open(filePath + '.json','r')
        jfile = json.load(filePointer)        
        rxn_list = jfile['rxn_list']        
        index = -1
        for key in rxn_list:
            index += 1
            mcell.reactions.reaction_list.add()
            mcell.reactions.active_rxn_index = index
            reaction = mcell.reactions.reaction_list[
                mcell.reactions.active_rxn_index]
		
            reaction.reactants = str(key['reactants'])
            reaction.products = str(key['products'])
            reaction.fwd_rate_expr = str(key['fwd_rate'])

        return {'FINISHED'}

class SBML_OT_release_site_add(bpy.types.Operator):
    bl_idname = "sbml.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add imported release sites from SBML-generated networxn_listrk"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        filePointer= open(filePath + '.json','r')
        jfile = json.load(filePointer)        
        rel_list = jfile['rel_list']     
        index = -1
        for key in rel_list:
            index += 1
            mcell.release_sites.mol_release_list.add()
            mcell.release_sites.active_release_index = index
            release_site = mcell.release_sites.mol_release_list[
                mcell.release_sites.active_release_index]
            
            release_site.name = str(key['name'])
            release_site.molecule = str(key['molecule'])
            release_site.shape = str(key['shape'])
            release_site.orient = str(key['orient'])
            release_site.object_expr = str(key['object_expr'])
            release_site.quantity_type = str(key['quantity_type'])
            release_site.quantity_expr = str(key['quantity_expr'])
            cellblender_operators.check_release_molecule(self, context)
	    
        return {'FINISHED'}

    
def execute_bionetgen(filepath,context):
    mcell = context.scene.mcell
    exe_sbml = "python {2} -i {0} -o {1}".format(filepath,filepath +'.json',mcell.project_settings.sbml2mcell)
    os.system(exe_sbml)    #
    #sbml2json.sbml2json(filepath)
    return{'FINISHED'}
   
