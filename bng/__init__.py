import bpy
from . import bng_operators
from . import sbml_operators
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty,BoolProperty

class ImportBioNetGenData(bpy.types.Operator, ImportHelper):
    bl_idname = "bng.import_data"  
    bl_label = "Import External Model"
    bl_description = "Import BioNetGen or SBML encoded reaction network information"
 
    filename_ext = ".bngl,*.xml"

    filter_glob = StringProperty(
            default="*.bngl;*.xml",
            options={'HIDDEN'},
            )
            
    add_to_model_objects = BoolProperty(
	        name="Add to Model Objects",
	        description="Automatically add all meshes to the Model Objects list",
	        default=True,)

    def execute_bngl(self,context):
        bngfilepath = self.filepath         # bngl file path
        print ( "Calling bng_operators.execute_bionetgen("+bngfilepath+")" )
        bng_operators.execute_bionetgen(bngfilepath,context)
        print ( "Back from bng_operators.execute_bionetgen("+bngfilepath+")" )
        import imp
        imp.reload(net)                     # This loads (and runs?) net.py which defines par_list and other lists
        print ( "Loading parameters from BNGL model..." )
        bpy.ops.bng.parameter_add()         # This processes all entries in the par_list parameter list
        print ( "Loading molecules from BNGL model..." )
        bpy.ops.bng.molecule_add()
        print ( "Loading reactions from BNGL model..." )
        bpy.ops.bng.reaction_add()
        print ( "Loading release sites from BNGL model..." )
        bpy.ops.bng.release_site_add()
        print ( "Done Loading BNGL model" )
        return {'FINISHED'}
	
    def execute_xml(self,context):
        sbmlfilepath = self.filepath
        sbml_operators.filePath = sbmlfilepath
        # sbml file path
        try:
            sbml_operators.execute_sbml2blender(sbmlfilepath,context,self.add_to_model_objects)
        except:
            print('There is no spatial information')
        sbml_operators.execute_sbml2mcell(sbmlfilepath,context)
        
        #import imp
        #imp.reload(net)
        print ( "Loading parameters from SBML model..." )
        bpy.ops.sbml.parameter_add()
        print ( "Loading molecules from SBML model..." )
        bpy.ops.sbml.molecule_add()
        print ( "Loading reactions from SBML model..." )
        bpy.ops.sbml.reaction_add()
        print ("Loading reaction output information from SBML model...")
        bpy.ops.sbml.reaction_output_add()

        print ( "Done Loading SBML model" )
        bpy.ops.sbml.release_site_add()
        
        return {'FINISHED'}

    def execute(self, context):
        if('.bngl') in self.filepath:
            return self.execute_bngl(context)
        elif('.xml') in self.filepath:
            return self.execute_xml(context)

def menu_func_import(self, context):
    self.layout.operator("bng.import_data", text="Import External Model (bngl,sbml)")
    
def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__": 
    register()

