import bpy
from . import bng_operators
from . import sbml_operators
from . import external_operators
from . import bngl_to_data_model
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty,BoolProperty
#import logging
import os

def findCellBlenderDirectory():
    for directory in os.path.sys.path:
        cellblenderDir = [x for x in os.listdir(directory) if 'cellblender' in x]
        if len(cellblenderDir) > 0:
            return directory + '{0}cellblender{0}'.format(os.sep)
   
    
class ImportBioNetGenData(bpy.types.Operator, ImportHelper):
    bl_idname = "bng.import_data"  
    bl_label = "Import External Model"
    bl_description = "Import BioNetGen or SBML encoded reaction network information"
 
    filename_ext = ".bngl,*.xml"

    filter_glob = StringProperty(
            default="*.bngl;*.xml",
            options={'HIDDEN'}
            )
            
    add_to_model_objects = BoolProperty(
	        name="Add to Model Objects",
	        description="Automatically add all meshes to the Model Objects list",
	        default=True,)


    def execute(self, context):
        if hasattr(external_operators.accessFile,"info"):
            del external_operators.accessFile.info
            
        if('.bngl') in self.filepath:
            bngfilepath = self.filepath         # bngl file path
            external_operators.filePath=findCellBlenderDirectory()+'bng{0}'.format(os.sep) + self.filepath.split(os.sep)[-1]
            print ( "Calling bng_operators.execute_bionetgen("+bngfilepath+")" )
            bng_operators.execute_bionetgen(self.filepath,context)
            print ( "Back from bng_operators.execute_bionetgen("+bngfilepath+")" )

        elif('.xml') in self.filepath:
            sbmlfilepath = self.filepath
            external_operators.filePath = sbmlfilepath
            # sbml file path
            #try:
            sbml_operators.execute_sbml2blender(sbmlfilepath,context,self.add_to_model_objects)
            #except:
             #   print('There is no spatial information')
            sbml_operators.execute_sbml2mcell(sbmlfilepath,context)
            print('Proceeding to import SBML file')
 
        
        print ( "Loading parameters from external model..." )
        bpy.ops.external.parameter_add()         # This processes all entries in the par_list parameter list
        print ( "Loading molecules from external model..." )
        bpy.ops.external.molecule_add()
        print ( "Loading reactions from external model..." )
        bpy.ops.external.reaction_add()
        print ( "Loading release sites from external model..." )
        bpy.ops.external.release_site_add()
        print ( "Done Loading external model" )
        if ('.xml') in self.filepath:
            #TODO:this is sbml only until we add this information on the bng side
            print("Loading reaction output ...")
            bpy.ops.external.reaction_output_add()

        return {'FINISHED'}

class ImportCBNGL(bpy.types.Operator, ImportHelper):
    bl_idname = "cbngl.import_data"
    bl_label = "Import CBNGL Model"
    bl_description = "Import CBNGL model replacing the current model"

    filename_ext = ".bngl"

    filter_glob = StringProperty ( default="*.bngl", options={'HIDDEN'} )

    add_to_model_objects = BoolProperty(
	        name="Add to Model Objects",
	        description="Automatically add all meshes to the Model Objects list",
	        default=True,)

    def execute(self, context):
        bngfilepath = self.filepath         # bngl file path
        print ( "Loading CBNGL model from \"" + str(bngfilepath) )
        mcell_dm = bngl_to_data_model.read_data_model_from_bngl_file ( bngfilepath )
        mcell_dm = context.scene.mcell.upgrade_data_model ( mcell_dm['mcell'] )
        context.scene.mcell.build_properties_from_data_model ( context, mcell_dm, geometry=True, scripts=True )
        return {'FINISHED'}

def menu_func_bng_import(self, context):
    self.layout.operator("bng.import_data", text="BioNetGen/SBML Model (.bngl,.xml)")

def menu_func_cbng_import(self, context):
    self.layout.operator("cbngl.import_data", text="Compartmental BioNetGen Model (.bngl)")

def register():
    bpy.types.INFO_MT_file_import.append(menu_func_bng_import)
    bpy.types.INFO_MT_file_import.append(menu_func_cbng_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_cbng_import)
    bpy.types.INFO_MT_file_import.remove(menu_func_bng_import)

if __name__ == "__main__": 
    register()

