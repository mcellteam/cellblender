import bpy
from . import bng_operators
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

class ImportBioNetGenData(bpy.types.Operator, ImportHelper):
    bl_idname = "bng.import_data"  
    bl_label = "Import BNG"
    bl_description = "Import BioNetGen-generated reaction network information"
 
    filename_ext = ".bngl"

    filter_glob = StringProperty(
            default="*.bngl",
            options={'HIDDEN'},
            )
    def execute(self, context):
        bngfilepath = self.filepath         # bngl file path
        print ( "Calling bng_operators.execute_bionetgen("+bngfilepath+")" )
        bng_operators.execute_bionetgen(bngfilepath)
        print ( "Back from bng_operators.execute_bionetgen("+bngfilepath+")" )
        import imp
        imp.reload(net)                     # This loads (and runs?) net.py which defines par_list and other lists
        bpy.ops.bng.parameter_add()         # This processes all entries in the par_list parameter list
        bpy.ops.bng.molecule_add()
        bpy.ops.bng.reaction_add()
        bpy.ops.bng.release_site_add()
        
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator("bng.import_data", text="BNG Model (.bngl)")
    
def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__": 
    register()

