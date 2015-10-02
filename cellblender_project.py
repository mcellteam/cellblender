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

"""
This file contains the classes for CellBlender's Preferences.

"""

import cellblender

# blender imports
import bpy
from bpy.app.handlers import persistent
from bl_operators.presets import AddPresetBase
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, BoolVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re
import os


# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils
from . import cellblender_objects

from cellblender.cellblender_utils import project_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl

# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


class MCELL_PT_project_settings(bpy.types.Panel):
    bl_label = "CellBlender - Project Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw ( self, context ):
        # Call the draw function of the object itself
        context.scene.mcell.project_settings.draw_panel ( context, self )




class MCellProjectPropertyGroup(bpy.types.PropertyGroup):
    base_name = StringProperty(
        name="Project Base Name", default="cellblender_project")

    status = StringProperty(name="Status")

    def draw_layout (self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            split = row.split(0.96)
            col = split.column()
            col.label(text="CellBlender ID: "+cellblender.cellblender_info['cellblender_source_sha1'])
            col = split.column()
            col.prop ( mcell, "refresh_source_id", icon='FILE_REFRESH', text="" )
            if 'cellblender_source_id_from_file' in cellblender.cellblender_info:
                # This means that the source ID didn't match the refreshed version
                # Draw a second line showing the original file ID as an error
                row = layout.row()
                row.label("File ID: " + cellblender.cellblender_info['cellblender_source_id_from_file'], icon='ERROR')

            # if not mcell.versions_match:
            if not cellblender.cellblender_info['versions_match']:
                # Version in Blend file does not match Addon, so give user a button to upgrade if desired
                row = layout.row()
                row.label ( "Blend File version doesn't match CellBlender version", icon='ERROR' )

                row = layout.row()
                row.operator ( "mcell.upgrade", text="Upgrade Blend File to Current Version", icon='RADIO' )
                #row = layout.row()
                #row.operator ( "mcell.delete", text="Delete CellBlender Collection Properties", icon='RADIO' )

                row = layout.row()
                row.label ( "Note: Saving this file will FORCE an upgrade!!!", icon='ERROR' )

            row = layout.row()
            if not bpy.data.filepath:
                row.label(
                    text="No Project Directory: Use File/Save or File/SaveAs",
                    icon='UNPINNED')
            else:
                row.label(
                    text="Project Directory: " + os.path.dirname(bpy.data.filepath),
                    icon='FILE_TICK')

            row = layout.row()
            layout.prop(context.scene, "name", text="Project Base Name")

    def remove_properties ( self, context ):
        print ( "Removing all Preferences Properties... no collections to remove." )

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




class MCellExportProjectPropertyGroup(bpy.types.PropertyGroup):
    export_format_enum = [
        ('mcell_mdl_unified', "Single Unified MCell MDL File", ""),
        ('mcell_mdl_modular', "Modular MCell MDL Files", "")]
    export_format = EnumProperty(items=export_format_enum,
                                 name="Export Format",
                                 default='mcell_mdl_modular')

    def remove_properties ( self, context ):
        print ( "Removing all Export Project Properties... no collections to remove." )




class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self,context):

        mcell = context.scene.mcell
        if mcell.cellblender_preferences.lockout_export:
            # print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            # The "self" here doesn't contain or permit the report function.
            # self.report({'INFO'}, "Exporting is Locked Out")
            return False

        return True

    def execute(self, context):
        print("MCELL_OT_export_project.execute()")

        if context.scene.mcell.cellblender_preferences.lockout_export:
            print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            self.report({'INFO'}, "Exporting is Locked Out")
        else:
            print(" Scene name =", context.scene.name)

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")

            # Change the actual scene name to the legal MCell Name
            context.scene.name = scene_name

            mcell = context.scene.mcell

            # Force the project directory to be where the .blend file lives
            cellblender_objects.model_objects_update(context)

            filepath = project_files_path()
            os.makedirs(filepath, exist_ok=True)

            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            mcell.project_settings.base_name = scene_name

            #filepath = os.path.join(
            #   filepath, mcell.project_settings.base_name + ".main.mdl")
            filepath = os.path.join(filepath, scene_name + ".main.mdl")
    #        bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)
            export_mcell_mdl.save(context, filepath)

            # These two branches of the if statement seem identical ?

            #if mcell.export_project.export_format == 'mcell_mdl_unified':
            #    filepath = os.path.join(os.path.dirname(bpy.data.filepath),
            #                            (mcell.project_settings.base_name +
            #                            ".main.mdl"))
            #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)
            #elif mcell.export_project.export_format == 'mcell_mdl_modular':
            #    filepath = os.path.join(os.path.dirname(bpy.data.filepath),
            #                            (mcell.project_settings.base_name +
            #                            ".main.mdl"))
            #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=filepath)

            self.report({'INFO'}, "Project Exported")

        return {'FINISHED'}



