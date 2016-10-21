import bpy
import os
import platform
from . import sbml2blender
from cellblender.cellblender_utils import get_python_path

# We use per module class registration/unregistration

filePath = ''


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def execute_sbml2mcell(filepath, context):
    import subprocess
    import shutil
    mcell = context.scene.mcell
    python_path = get_python_path(mcell=mcell)
    destpath = os.path.dirname(__file__)
    # We still have to use the pyinstaller version for windows, since 
    # the Miniconda version isn't working.
    if platform.system() == "Windows":
        subprocess.call([os.path.join(destpath, 'bin', 'sbml2json.exe'),
                        '-i', filepath])
    else:
        subprocess.call([python_path, destpath + '{0}sbml2json.py'.format(
            os.sep), '-i', filepath])
    # execute_externally(filepath,context)
    #TODO: If isTransformed is false a window should be shown that the model
    # failed to load
    return{'FINISHED'}


def execute_sbml2blender(filepath, context, addObjects=True):
    mcell = context.scene.mcell
    sbml2blender.sbml2blender(filepath, addObjects)
