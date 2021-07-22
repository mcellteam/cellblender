import bpy
import os
import platform
from . import sbml2blender
from cellblender.cellblender_utils import get_python_path


filePath = ''


def execute_sbml2mcell(filepath, context):
    import subprocess
    import shutil
    mcell = context.scene.mcell
    python_path = get_python_path(mcell=mcell)
    destpath = os.path.dirname(__file__)
    subprocess.call([python_path, destpath + '{0}sbml2json.py'.format(
        os.sep), '-i', filepath])
    # execute_externally(filepath,context)
    #TODO: If isTransformed is false a window should be shown that the model
    # failed to load
    return{'FINISHED'}


def execute_sbml2blender(filepath, context, addObjects=True):
    mcell = context.scene.mcell
    sbml2blender.sbml2blender(filepath, addObjects)
