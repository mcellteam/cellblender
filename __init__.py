# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import os

bl_info = {
    "name": "CellBlender",
    "author": "Tom Bartol, Jacob Czech, Markus Dittrich, Bob Kuczewski",
    "version": (0, 1, 57),
    "blender": (2, 66, 1),
    "api": 55057,
    "location": "Properties > Scene > CellBlender Panel",
    "description": "CellBlender Modeling System for MCell",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "http://code.google.com/p/cellblender/issues/list",
    "category": "Cell Modeling"
}

cellblender_info = {
    "supported_version_list": [(2, 64, 0), (2, 65, 0), (2, 66, 1)],
    "cellblender_source_list": [
        "__init__.py",
        "cellblender_properties.py",
        "cellblender_panels.py",
        "cellblender_operators.py",
        "io_mesh_mcell_mdl/__init__.py",
        "io_mesh_mcell_mdl/export_mcell_mdl.py",
        "io_mesh_mcell_mdl/import_mcell_mdl.py",
        "io_mesh_mcell_mdl/mdlmesh_parser.py"],
    "cellblender_source_sha1": "",
    "cellblender_addon_path": ""
}



# To support reload properly, try to access a package var.
# If it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(cellblender_properties)
    imp.reload(cellblender_panels)
    imp.reload(cellblender_operators)
    imp.reload(io_mesh_mcell_mdl)
else:
    from . import cellblender_properties, cellblender_panels, \
        cellblender_operators, io_mesh_mcell_mdl


import bpy
import hashlib


# Compute, print, and save the SHA1 of all source files in
# cellblender_info["cellblender_source_list"]

def identify_source_version(addon_path):
    cbsl = cellblender_info["cellblender_source_list"]
    hashobject = hashlib.sha1()
    for source_file_basename in cbsl:
        source_file_name = os.path.join(addon_path, source_file_basename)
        hashobject.update(open(source_file_name, 'r').read().encode("utf-8"))
        print("  Cumulative SHA1: ", hashobject.hexdigest(), "=",
              source_file_name)

    cellblender_info['cellblender_source_sha1'] = hashobject.hexdigest()
    print("CellBlender Source ID (SHA1) = ", cellblender_info['cellblender_source_sha1'])
    sha_file = os.path.join(addon_path, "cellblender_source_sha1.txt")
    open(sha_file, 'w').write(hashobject.hexdigest())


import subprocess

def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def print_plotting_options():
    plot_executables = ['python', 'xmgrace', 'java', 'excel']
    plot_modules = ['matplotlib', 'junktestlib', 'matplotlib.pyplot', 'pylab', 'numpy', 'scipy']

    for plot_app in plot_executables:
        path = find_in_path ( plot_app )
        if path != None:
            print ( "  ", plot_app, "is available at", path )
        else:
            print ( "  ", plot_app, "is not found in the current path" )

    for plot_mod in plot_modules:
        try:
            __import__ ( plot_mod )
            print ( "  ", plot_mod, "is importable" )
        except:
            print ( "  ", plot_mod, "is not importable in this configuration" )

    python_command = find_in_path ( "python" )

    for plot_mod in plot_modules:
        import_test_program = 'import %s\nprint("Found=OK")'%(plot_mod)
        #print ( "Test Program:" )
        #print ( import_test_program )
        process = subprocess.Popen([python_command, '-c', import_test_program], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print ( "Back from Popen" )
        process.poll()
        #print ( "Back from poll" )
        output = process.stdout.readline()
        #print ( "Back from readline" )
        #print ( "  output =", output )
        strout = str(output)
        if (strout != None) & (strout.find("Found=OK")>=0):
            print ( "  ", plot_mod, "is available through external python interpreter" )
        else:
            print ( "  ", plot_mod, "is not available through external python interpreter" )

try:
    import cellblender.data_plotters
except ImportError:
    print("data_plotters was not found")

# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(io_mesh_mcell_mdl.menu_func_import)
    bpy.types.INFO_MT_file_export.append(io_mesh_mcell_mdl.menu_func_export)
    bpy.types.Scene.mcell = bpy.props.PointerProperty(
        type=cellblender_properties.MCellPropertyGroup)
    bpy.types.Object.mcell = bpy.props.PointerProperty(
        type=cellblender_properties.MCellObjectPropertyGroup)
    print("CellBlender registered")
    if (bpy.app.version not in cellblender_info['supported_version_list']):
        print("Warning, current Blender version", bpy.app.version,
              " is not in supported list:", cellblender_info['supported_version_list'])

    print ( "CellBlender Addon found: ", __file__ )
    cellblender_info["cellblender_addon_path"] = os.path.dirname(__file__)
    print ( "CellBlender Addon Path is ", cellblender_info["cellblender_addon_path"] )
    addon_path = os.path.dirname(__file__)
    identify_source_version ( addon_path )
    print ( "CellBlender is searching for known plotting plugins" )
    try:
        # Trap exceptions in case this test code fails for some reason
        print_plotting_options()
    except:
        print ( "Exception in print_plotting_options()" )
        pass


def unregister():
    bpy.utils.unregister_module(__name__)
    print("CellBlender unregistered")


if len(bpy.app.handlers.frame_change_pre) == 0:
    bpy.app.handlers.frame_change_pre.append(
        cellblender_operators.frame_change_handler)

if len(bpy.app.handlers.load_post) == 0:
    bpy.app.handlers.load_post.append(
        cellblender_operators.model_objects_update)

if len(bpy.app.handlers.save_pre) == 0:
    bpy.app.handlers.save_pre.append(
        cellblender_operators.model_objects_update)

# for testing
if __name__ == '__main__':
    #identify_source_version ( "" )
    register()
