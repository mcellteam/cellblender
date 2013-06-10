import bpy
import os
import sys

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

    
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
        filepath = self.filepath         # bngl file path
        read_bng_data(context, self.filepath)
        execute_bionetgen(filepath)        
        try:
            from . import net
        except ImportError as e:
            print (sys.stderr,e) 
	    
        return {'FINISHED'}
	

def execute_bionetgen(filepath):
    from os.path import exists
    filebasename = os.path.basename(filepath)
    filedirpath = os.path.dirname(filepath)    # directory containing the bngl script 
    check_dir = filedirpath;
    n = 0
    while(n!=20):    # iterative search for BNG execution directory (in the reverse direction, starting from the directory containing the bngl script)
        bng_dir = check_dir  # current directory (and its child directories) to be checked 
        checked = {}    # list to store directories for which search is complete
        i = 0
        for (dirpath, dirname, filename) in os.walk(bng_dir):    # iterate over the current directory and previously unchecked child directories 
            if (i == 0):
                check_dir = os.path.dirname(dirpath)    #  mark the parent directory for next search step (after current directory and its child directories are done) 
                i = 1
            if dirpath in checked:  # escape the (child) directory checked in the previous step
                continue
            bngpath = os.path.join(dirpath,"BNG2.pl")    # BNG executable file name
            if os.path.exists(bngpath):    # if BNG executable file is identified, proceed for BNG execution 
                exe_bng = bngpath + "    " + filepath    # create command string for BNG execution
                os.system(exe_bng)    # execute BNG
                srcname = os.path.join(os.getcwd(),(filebasename + ".py"))   # created python file containing the reaction network informaion 
                dstname = os.path.join(os.path.dirname(__file__), "net.py")
                os.system("mv" + " " + srcname + " " + dstname)
                return{'FINISHED'}
            checked.update({dirpath:True})    # store checked directory in the list
        n +=1  
        if (n==20):    # too many iteration for search. stop now
            print ("Error running BioNetGen. BNG2.pl not found....")
    return{'FINISHED'}

def menu_func_import(self, context):
    self.layout.operator(ImportBNGData.bl_idname, text="BNG Model (.bngl)")
    
def register():
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    
class ErrBNG(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self): 
        return ("search resulted no BNG executable")
	
register()

