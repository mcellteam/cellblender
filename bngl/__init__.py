import bpy
import os
from . import sbml_operators
from . import sbml_properties

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.path import basename

class ImportSBMLData(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_sbml.model_data"  
    bl_label = "Import SBML Data"

    filename_ext = ".txt"

    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    def execute(self, context):
        read_sbml_data(context, self.filepath)
        return {'FINISHED'}
	

def read_sbml_data(context, filepath):
    print("importing sbml data...")
    f = open(filepath, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    from . import model
    print(data)
    return {'FINISHED'}
    
class ImportBNGData(bpy.types.Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_bng.model_data"  
    bl_label = "Import BNG Data"

    filename_ext = ".bngl"

    filter_glob = StringProperty(
            default="*.bngl",
            options={'HIDDEN'},
            )

    def execute(self, context):
        from os import pathsep
        import sys
        from os.path import exists, join
	
        filepath = self.filepath         # Path for the bngl file
        check_dir = os.path.dirname(filepath)   # Path for directory containing the bngl file
        j = 0
        while(j < 5):   # Search for the directory containing BNG2.pl (in the reverse direction, starting from the directory containing the bngl file)
            bng_dir = check_dir      
            print(bng_dir)
            bngpath = bng_dir + "/BNG2.pl"
            print(bngpath)

            checked = {}    # Stores the list of directories already searched
            i = 0
       
            for (dirpath, dirname, filename) in os.walk(bng_dir):
                if (i==0):
                    check_dir = os.path.dirname(dirpath)        #  Parent directory is stored for the next search step once the for loop is done 
                    i = 1

                if dirpath in checked:
                    continue
            
                if os.path.exists(bngpath):
                    print (bngpath)
                    i = 2
                    break
	    
                checked.update({dirpath:True})
                print (checked[dirpath])
		
            if (i==2):
                break       
            j += 1

        os.system("ls")
        read_bng_data(context, self.filepath)
        return {'FINISHED'}
	

def read_bng_data(context, filepath):
    print("importing bng data...")
    f = open(filepath, 'r', encoding='utf-8')
    data = f.read()
    f.close()
    from . import model
    print(data)
    return {'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportSBMLData.bl_idname, text="SBML Model (.sbml)")
    self.layout.operator(ImportBNGData.bl_idname, text="BNG Model (.bngl)")
    
def register():
    bpy.utils.register_class(ImportSBMLData)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportSBMLData)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

register()

