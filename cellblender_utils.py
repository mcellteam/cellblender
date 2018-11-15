import os
import bpy
import shutil
import sys
import subprocess


def get_tool_shelf():
    tool_shelf = None
    area = bpy.context.area

    for region in area.regions:
        if region.type == 'TOOLS':
            tool_shelf = region
    return tool_shelf


def wrap_long_text(width, text):

    lines = []
    arr = text.split()
    lengthSum = 0
    strSum = ""

    for var in arr:
        lengthSum+=len(var) + 1
        if lengthSum <= width:
            strSum += " " + var
        else:
            lines.append(strSum)
            lengthSum = 0
            strSum = var
    # lines.append(" " + arr[len(arr) - 1])
    lines.append(strSum)

    return lines


def timeline_view_all ( context ):
    if bpy.context.screen != None:
        for area in bpy.context.screen.areas:
            if area != None:
                if area.type == 'TIMELINE':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            ctx = bpy.context.copy()
                            ctx['area'] = area
                            ctx['region'] = region
                            bpy.ops.time.view_all(ctx)
                            break  # It's not clear if this should break or continue ... breaking for now


def project_files_path():
    ''' Consolidate the creation of the path to the project files'''

    filepath = os.path.dirname(bpy.data.filepath)
    filepath, dot, blend = bpy.data.filepath.rpartition(os.path.extsep)
    filepath = filepath + "_files"
    return filepath


def mcell_files_path():
    ''' Consolidate the creation of the path to the mcell files'''

    filepath = project_files_path()
    filepath = os.path.join(filepath, "mcell")
    return filepath



def preserve_selection_use_operator(operator, new_obj):
    """ Preserve current object selection state and use operator.

    It is not uncommon for Blender operators to make use of the current
    selection. This means you first have to save the current selection state,
    deselect everything, select the object you actually want to do the
    operation on, execute the operator, deselect that object, and finally
    reselect the original selection state. This sounds silly but can be quite
    useful. """

    object_list = bpy.context.scene.objects
    selected_objs = [obj for obj in object_list if obj.select]
    # Deselect everything currently selected, so the operator doesn't act on it
    for obj in selected_objs:
        obj.select = False
    # Select the object we actually want the operator to act on, use it, and
    # deselect.
    new_obj.select = True
    operator()
    new_obj.select = False
    # It's annoying if operators change things they shouldn't, so let's restore
    # the originally select objects.
    for obj in selected_objs:
        obj.select = True


def check_val_str(val_str, min_val, max_val):
    """ Convert val_str to float if possible. Otherwise, generate error. """

    status = ""
    val = None

    try:
        val = float(val_str)
        if min_val is not None:
            if val < min_val:
                status = "Invalid value for %s: %s"
        if max_val is not None:
            if val > max_val:
                status = "Invalid value for %s: %s"
    except ValueError:
        status = "Invalid value for %s: %s"

    return (val, status)


def try_to_import(python_path, required_modules):
    if (required_modules == None):
        return True

    import_test = ''
    for module in required_modules:
        import_test += ('import %s' + os.linesep) % (module)
    
    cmd = [python_path, '-c', import_test] 
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
    process.wait()
    if (process.poll()):
        return False
    else:
        return True


def get_python_path(required_modules=None, mcell=None):
    python_path = None
    # Try user assigned python path first. This won't work if we don't have
    # bpy.context.scene.mcell
    if (mcell and mcell.cellblender_preferences.python_binary_valid and
            try_to_import(mcell.cellblender_preferences.python_binary, required_modules)):
        python_path = mcell.cellblender_preferences.python_binary
        print("Using user specified Python: " + python_path)
    # Try to use the built-in version. This will require the bundled miniconda
    # version for the matplotlib plotters.
    elif (try_to_import(bpy.app.binary_path_python, required_modules)):
        python_path = bpy.app.binary_path_python
        print("Using Blender's Python: " + python_path)
    # Try python in the user's PATH. This will probably fail on Windows.
    elif (try_to_import(shutil.which("python", mode=os.X_OK), required_modules)):
        python_path = shutil.which("python", mode=os.X_OK)
        print("Using shutil.which Python: " + python_path)
    return python_path


def get_mcell_path ( mcell ):
    # If MCell path was set by user, use that one. Otherwise, try to use
    # bundled version (i.e. <cellblender_path>/bin/mcell). As a last resort,
    # try finding MCell in user's path, which will likely fail on Windows.
    mcell_path = None
    if sys.platform == "win32":
        mcell_binary = "mcell.exe"
    else:
        mcell_binary = "mcell"
    bundled_path = os.path.join(os.path.dirname(__file__), "extensions", "mcell", mcell_binary)
    if mcell.cellblender_preferences.mcell_binary_valid:
        mcell_path = mcell.cellblender_preferences.mcell_binary
    elif is_executable(bundled_path):
        mcell_path = bundled_path
    else:
        mcell_path = shutil.which("mcell", mode=os.X_OK)
    return mcell_path


def is_executable(binary_path):
    """Checks for nonexistant or non-executable binary file"""
    is_exec = False
    try:
        st = os.stat(binary_path)
        if os.path.isfile(binary_path):
            if os.access(binary_path, os.X_OK):
                is_exec = True
    except Exception as err:
        is_exec = False
    return is_exec


def get_path_to_parent(self_object):
    # Return the Blender class path to the parent object with regard to the Blender Property Tree System
    path_to_self = "bpy.context.scene." + self_object.path_from_id()
    path_to_parent = path_to_self[0:path_to_self.rfind(".")]
    return path_to_parent

def get_parent(self_object):
    # Return the parent Blender object with regard to the Blender Property Tree System
    path_to_parent = get_path_to_parent(self_object)
    parent = eval(path_to_parent)
    return parent

