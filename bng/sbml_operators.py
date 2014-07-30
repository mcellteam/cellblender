import bpy
import os
import json

from . import sbml2blender
from . import sbml2json

import cellblender
from cellblender import cellblender_operators
import logging

logging.basicConfig(filename='cellblender2.log',level=logging.DEBUG,format='%(asctime)s - %(levelname)s:%(message)s')
    
#from . import sbml2json
#from . import sbml2json
# We use per module class registration/unregistration

filePath = ''

def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)




def execute_sbml2mcell(filepath,context):
    mcell = context.scene.mcell
    isTransformed = sbml2json.transform(filePath)
    if not isTransformed:
        print('Bundled libsbml does not support your platform. Using local python and libsbml installations')
        execute_externally(filepath,context)
    #TODO: If isTransformed is false a window should be shown that the model failed to load
    return{'FINISHED'}

def execute_externally(filepath,context):
    import subprocess
    import shutil
    mcell = context.scene.mcell
    if mcell.cellblender_preferences.python_binary_valid:
        python_path = mcell.cellblender_preferences.python_binary
    else:
        python_path = shutil.which("python", mode=os.X_OK)
    destpath = os.path.dirname(__file__)
    logging.info('Execution {0} with arguments {1},{2}'.format(python_path,destpath+ '{0}sbml2json.py'.format(os.sep),filepath))
    subprocess.call([python_path,destpath + '{0}sbml2json.py'.format(os.sep),'-i',filepath])
   
def execute_sbml2blender(filepath,context,addObjects=True):
    mcell = context.scene.mcell
    sbml2blender.sbml2blender(filepath,addObjects)

