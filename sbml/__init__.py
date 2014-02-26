import bpy
from . import sbml2blender
from . import sbml_operators
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

class ImportBioNetGenData(bpy.types.Operator, ImportHelper):
    bl_idname = "sbml.import_data"  
    bl_label = "Import SBML"
    bl_description = "Import SBML-generated reaction network information"
 
    filename_ext = ".xml"

    filter_glob = StringProperty(
            default="*.xml",
            options={'HIDDEN'},
            )
    def execute(self, context):
        sbmlfilepath = self.filepath
        sbml_operators.filePath = sbmlfilepath
         # sbml file path
        sbml_operators.execute_sbml2blender(sbmlfilepath,context)
        sbml_operators.execute_sbml2mcell(sbmlfilepath,context)
        
        #import imp
        #imp.reload(net)
        bpy.ops.sbml.parameter_add()
        bpy.ops.sbml.molecule_add()
        bpy.ops.sbml.reaction_add()
        bpy.ops.sbml.release_site_add()
        
        return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator("sbml.import_data", text="SBML Model (.xml)")
    
def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    #bpy.types.Object.sbml = bpy.props.PointerProperty(
     #   type=sbml_properties.SBMLPropertyGroup)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__": 
    register()

