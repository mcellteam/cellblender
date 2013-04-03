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
    "version": (0, 1, 56),
    "blender": (2, 66, 1),
    "api": 55057,
    "location": "Properties > Scene > CellBlender Panel",
    "description": "CellBlender Modeling System for MCell",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "http://code.google.com/p/cellblender/issues/list",
    "category": "Cell Modeling",
    "supported_version_list": [(2, 64, 0), (2, 65, 0), (2, 66, 1)],
    "cellblender_source_list": [
        "__init__.py", 
        "cellblender_properties.py", 
        "cellblender_panels.py", 
        "cellblender_operators.py", 
        "io_mesh_mcell_mdl/__init__.py", 
        "io_mesh_mcell_mdl/export_mcell_mdl.py", 
        "io_mesh_mcell_mdl/import_mcell_mdl.py", 
        "io_mesh_mcell_mdl/mdlmesh_parser.py" ],
    "cellblender_source_sha1": "x"
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
    if (bpy.app.version not in bl_info['supported_version_list']):
        print("Warning, current Blender version", bpy.app.version,
              " is not in supported list:", bl_info['supported_version_list'])

    cbsl = bl_info["cellblender_source_list"]
    hashobject = hashlib.sha1()
    for i in range(len(cbsl)):
        source_file_name = bpy.utils.script_paths()[0] + os.sep + "addons" + os.sep + "cellblender" + os.sep + cbsl[i]
        print ( "Including SHA1 of ", source_file_name )
    	hashobject.update ( open(source_file_name,'r').read().encode("utf-8") )
    	print ( "  gives ... ", hashobject.hexdigest() )
    
    bl_info['cellblender_source_sha1'] = hashobject.hexdigest()
    print ( "CellBlender Source Sha1 = ", bl_info['cellblender_source_sha1'] )
    #bpy.data.scenes[0].mcell.cellblender_source_hash = bl_info['cellblender_source_sha1']


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
    register()
