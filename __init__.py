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


bl_info = {
    "name": "CellBlender",
    "author": "Tom Bartol, Jacob Czech, Markus Dittrich",
    "version": (0, 1, 54),
    "blender": (2, 6, 5),
    "api": 53177,
    "location": "Properties > Scene > CellBlender Panel",
    "description": "CellBlender Modeling System for MCell",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "http://code.google.com/p/cellblender/issues/list",
    "category": "Cell Modeling"
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


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(io_mesh_mcell_mdl.menu_func_import)
    bpy.types.INFO_MT_file_export.append(io_mesh_mcell_mdl.menu_func_export)
    bpy.types.Scene.mcell = bpy.props.PointerProperty(
        type=cellblender_properties.MCellPropertyGroup)
    bpy.types.Object.mcell = bpy.props.PointerProperty(
        type=cellblender_properties.MCellObjectPropertyGroup)


def unregister():
    bpy.utils.unregister_module(__name__)


if len(bpy.app.handlers.frame_change_pre) == 0:
    bpy.app.handlers.frame_change_pre.append(
        cellblender_operators.frame_change_handler)


# for testing
if __name__ == '__main__':
    register()
