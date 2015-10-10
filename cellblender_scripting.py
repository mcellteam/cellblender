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
This file contains the classes for CellBlender's Scripting.

"""

import glob
import os

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils
from cellblender.cellblender_utils import project_files_path


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Scripting Operators:

def update_available_scripts ( scripting ):
    #mdl_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="MDL Scripts")
    #python_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="Python Scripts")
    
    # Delete current scripts list
    while scripting.internal_mdl_scripts_list:
      scripting.internal_mdl_scripts_list.remove(0)
    while scripting.internal_python_scripts_list:
      scripting.internal_python_scripts_list.remove(0)

    # Find the current internal scripts
    for txt in bpy.data.texts:
       # print ( "\n" + txt.name + "\n" + txt.as_string() + "\n" )
       if txt.name[-4:] == ".mdl":
          scripting.internal_mdl_scripts_list.add()
          index = len(scripting.internal_mdl_scripts_list)-1
          scripting.internal_mdl_scripts_list[index].name = txt.name
       if txt.name[-3:] == ".py":
          scripting.internal_python_scripts_list.add()
          index = len(scripting.internal_python_scripts_list)-1
          scripting.internal_python_scripts_list[index].name = txt.name


class MCELL_OT_scripting_add(bpy.types.Operator):
    bl_idname = "mcell.scripting_add"
    bl_label = "Add Script"
    bl_description = "Add a new script to the model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scripting = context.scene.mcell.scripting
        scripting.scripting_list.add()
        scripting.active_scripting_index = len(scripting.scripting_list)-1
        check_scripting(self, context)
        update_available_scripts ( scripting )
        return {'FINISHED'}


class MCELL_OT_scripting_remove(bpy.types.Operator):
    bl_idname = "mcell.scripting_remove"
    bl_label = "Remove Script"
    bl_description = "Remove selected script from the model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scripting = context.scene.mcell.scripting
        scripting.scripting_list.remove(scripting.active_scripting_index)
        scripting.active_scripting_index -= 1
        if (scripting.active_scripting_index < 0):
            scripting.active_scripting_index = 0
        if scripting.scripting_list:
            check_scripting(self, context)
        update_available_scripts ( scripting )
        return {'FINISHED'}


class MCELL_OT_scripting_refresh(bpy.types.Operator):
    bl_idname = "mcell.scripting_refresh"
    bl_label = "Refresh Files"
    bl_description = "Refresh the list of available script files"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scripting = context.scene.mcell.scripting
        check_scripting(self, context)
        update_available_scripts ( scripting )
        return {'FINISHED'}




# Scripting callback functions


def check_scripting(self, context):
    mcell = context.scene.mcell
    scripting_list = mcell.scripting.scripting_list
    scripting = scripting_list[mcell.scripting.active_scripting_index]
    return



# Scripting Panel Classes


class MCELL_UL_scripting_item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        desc = item.get_description()
        if item.include_where == "Don't Include":
            layout.label ( icon='ERROR', text=desc )
        else:
            layout.label ( icon='FILE_TICK', text=desc )


class MCELL_PT_scripting_settings(bpy.types.Panel):
    bl_label = "CellBlender - Scripting Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.scripting.draw_panel ( context, self )


# Scripting Property Groups


class CellBlenderScriptingProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Scripting", update=check_scripting)
    status = StringProperty(name="Status")
    
    internal_file_name = StringProperty ( name = "Internal File Name" )
    external_file_name = StringProperty ( name = "External File Name", subtype='FILE_PATH', default="" )

    include_where_enum = [
        ('Include Before', "Include Before", ""),
        ('Include After',  "Include After",  ""),
        ("Don't Include",  "Don't Include",  "")]
    include_where = bpy.props.EnumProperty(
        items=include_where_enum, name="Include Where",
        default='Include Before',
        description="Choose relative location to include this script.",
        update=check_scripting)

    include_section_enum = [
        ('Parameters',      "Parameters", ""),
        ('Initialization',  "Initialization",  ""),
        ("Molecules",       "Molecules",  ""),
        ("Reactions",       "Reactions",  ""),
        ("Geometry",        "Geometry",  ""),
        ("Output",          "Output",  "")]
    include_section = bpy.props.EnumProperty(
        items=include_section_enum, name="Include Section",
        default='Initialization',
        description="Choose MDL section to include this script.",
        update=check_scripting)

    internal_external_enum = [
        ('Internal', "Internal", ""),
        ("External", "External",  "")]
    internal_external = bpy.props.EnumProperty(
        items=internal_external_enum, name="Internal/External",
        default='Internal',
        description="Choose location of file (internal text or external file).",
        update=check_scripting)

    mdl_python_enum = [
        ('MDL',    "MDL", ""),
        ("Python", "Python",  "")]
    mdl_python = bpy.props.EnumProperty(
        items=mdl_python_enum, name="MDL/Python",
        default='MDL',
        description="Choose type of scripting (MDL or Python).",
        update=check_scripting)

    def get_description ( self ):
        desc = ""

        if self.include_where == "Don't Include":
            desc = "Don't include "
            if self.internal_external == "Internal":
                desc += "internal \"" + self.internal_file_name + "\" "
            if self.internal_external == "External":
                desc += "external \"" + self.external_file_name + "\" "
        else:
            int_ext = ""
            fname = ""
            if self.internal_external == "Internal":
                int_ext = "internal "
                fname = "\"" + self.internal_file_name + "\" "
            if self.internal_external == "External":
                int_ext = "external "
                fname = "\"" + self.external_file_name + "\" "

            where = ""
            if self.include_where == "Include Before":
                where = "before "
            if self.include_where == "Include After":
                where = "after "

            mdl_py = self.mdl_python + " "

            desc = "Include " + int_ext + mdl_py + fname + where + self.include_section

        return ( desc )
        

    def draw_layout ( self, context, layout ):
        mcell = context.scene.mcell
        ps = mcell.parameter_system

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            row.prop(self, "internal_external", expand=True)
            row.prop(self, "mdl_python", expand=True)
            
            row = layout.row()

            if (self.internal_external == "Internal"):

                if (self.mdl_python == "MDL"):
                    row.prop_search ( self, "internal_file_name",
                                      context.scene.mcell.scripting, "internal_mdl_scripts_list",
                                      text="File:", icon='TEXT' )
                    row.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")
                    """
                    layout.label ( "Internal MDL Scripts:" )
                    for txt in context.scene.mcell.scripting.internal_mdl_scripts_list:
                        box = layout.box()
                        box.label ( bpy.data.texts[txt.name].name )
                        box.label ( bpy.data.texts[txt.name].as_string() )
                    """

                if (self.mdl_python == "Python"):
                    row.prop_search ( self, "internal_file_name",
                                      context.scene.mcell.scripting, "internal_python_scripts_list",
                                      text="File:", icon='TEXT' )
                    row.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")
                    """
                    layout.label ( "Internal Python Scripts:" )
                    for txt in context.scene.mcell.scripting.internal_python_scripts_list:
                        box = layout.box()
                        box.label ( bpy.data.texts[txt.name].name )
                        box.label ( bpy.data.texts[txt.name].as_string() )
                    """

            if (self.internal_external == "External"):

                row.prop ( self, "external_file_name" )
                row.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")

            row = layout.row()
            row.prop(self, "include_where", text="", expand=False)
            row.prop(self, "include_section", text="", expand=False)

class CellBlenderScriptProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Script")


class CellBlenderScriptingPropertyGroup(bpy.types.PropertyGroup):

    active_scripting_index = IntProperty(name="Active Scripting Index", default=0)
    scripting_list = CollectionProperty(type=CellBlenderScriptingProperty, name="Scripting List")
    internal_mdl_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="MDL Internal Scripts")
    external_mdl_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="MDL External Scripts")
    internal_python_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="Python Internal Scripts")
    external_python_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="Python External Scripts")

    def draw_layout ( self, context, layout ):
        """ Draw the scripting "panel" within the layout """
        mcell = context.scene.mcell
        ps = mcell.parameter_system

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            col = row.column()
            col.template_list("MCELL_UL_scripting_item", "scripting",
                              self, "scripting_list",
                              self, "active_scripting_index", rows=2)
            col = row.column(align=True)
            col.operator("mcell.scripting_add", icon='ZOOMIN', text="")
            # col.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")
            col.operator("mcell.scripting_remove", icon='ZOOMOUT', text="")
            
            if self.scripting_list:
                selected_script = self.scripting_list[self.active_scripting_index]
                selected_script.draw_layout ( context, layout )

            #layout.label ( "Texts:" )
            #for txt in bpy.data.texts:
            #  box = layout.box()
            #  box.label ( txt.name )
            #  box.label ( txt.as_string() )

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


    def write_scripting_output ( self, before_after, section, context, out_file, filedir ):
        print ( "################### Write Scripting Ouptut " + before_after + " " + section )
        out_file.write("\n/* Begin Custom MDL Inserted %s %s */\n" % (before_after, section))
        out_file.write("/* End Custom MDL Inserted %s %s */\n\n" % (before_after, section))
        pass
