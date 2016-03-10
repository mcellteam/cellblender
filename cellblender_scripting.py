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


class MCELL_OT_scripting_execute(bpy.types.Operator):
    bl_idname = "mcell.scripting_execute"
    bl_label = "Execute Script on Current Data Model"
    bl_description = "Execute the selected script to REPLACE the current data model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scripting = context.scene.mcell.scripting
        print ( "Executing Script" )
        scripting.execute_selected_script(context)
        return {'FINISHED'}


# Scripting callback functions


def check_scripting(self, context):
    mcell = context.scene.mcell
    scripting_list = mcell.scripting.scripting_list
    if len(scripting_list) > 0:
        scripting = scripting_list[mcell.scripting.active_scripting_index]
    return



# Scripting Panel Classes


class MCELL_UL_scripting_item(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        desc = item.get_description()
        if item.include_where == "dont_include":
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

################### Write Scripting Ouptut before everything
################### Write Scripting Ouptut before parameters
################### Write Scripting Ouptut after parameters
################### Write Scripting Ouptut before initialization
################### Write Scripting Ouptut after initialization
################### Write Scripting Ouptut before partitions
################### Write Scripting Ouptut after partitions
################### Write Scripting Ouptut before molecules
################### Write Scripting Ouptut after molecules
################### Write Scripting Ouptut before surface_classes
################### Write Scripting Ouptut after surface_classes
################### Write Scripting Ouptut before reactions
################### Write Scripting Ouptut after reactions
################### Write Scripting Ouptut before geometry
################### Write Scripting Ouptut after geometry
################### Write Scripting Ouptut before mod_surf_regions
################### Write Scripting Ouptut after mod_surf_regions
################### Write Scripting Ouptut before release_patterns
################### Write Scripting Ouptut after release_patterns
################### Write Scripting Ouptut before instantiate
################### Write Scripting Ouptut after instantiate
################### Write Scripting Ouptut before seed
################### Write Scripting Ouptut after seed
################### Write Scripting Ouptut before viz_output
################### Write Scripting Ouptut after viz_output
################### Write Scripting Ouptut before rxn_output
################### Write Scripting Ouptut after rxn_output
################### Write Scripting Ouptut after everything


class CellBlenderScriptingProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Scripting", update=check_scripting)
    status = StringProperty(name="Status")
    
    internal_file_name = StringProperty ( name = "Internal File Name" )
    external_file_name = StringProperty ( name = "External File Name", subtype='FILE_PATH', default="" )

    include_where_enum = [
        ('before', "Include Before", ""),
        ('after',  "Include After",  ""),
        ("dont_include",  "Don't Include",  "")]
    include_where = bpy.props.EnumProperty(
        items=include_where_enum, name="Include Where",
        default='before',
        description="Choose relative location to include this script.",
        update=check_scripting)

    include_section_enum = [
        ('everything',       "Everything", ""),
        ('parameters',       "Parameters", ""),
        ('initialization',   "Initialization",  ""),
        ('partitions',       "Partitions",  ""),
        ("molecules",        "Molecules",  ""),
        ("surface_classes",  "Surface Classes",  ""),
        ("reactions",        "Reactions",  ""),
        ("geometry",         "Geometry",  ""),
        ("mod_surf_regions", "Modify Surface Regions",  ""),
        ("release_patterns", "Release Patterns",  ""),
        ("instantiate",      "Instantiate Objects",  ""),
        ("release_sites",    "Release Sites",  ""),
        ("seed",             "Seed",  ""),
        ("viz_output",       "Visualization Output",  ""),
        ("rxn_output",       "Reaction Output",  "")]
    include_section = bpy.props.EnumProperty(
        items=include_section_enum, name="Include Section",
        default='initialization',
        description="Choose MDL section to include this script.",
        update=check_scripting)

    internal_external_enum = [
        ('internal', "Internal", ""),
        ("external", "External",  "")]
    internal_external = bpy.props.EnumProperty(
        items=internal_external_enum, name="Internal/External",
        default='internal',
        description="Choose location of file (internal text or external file).",
        update=check_scripting)

    mdl_python_enum = [
        ('mdl',    "MDL", ""),
        ("python", "Python",  "")]
    mdl_python = bpy.props.EnumProperty(
        items=mdl_python_enum, name="MDL/Python",
        default='mdl',
        description="Choose type of scripting (MDL or Python).",
        update=check_scripting)

    def get_description ( self ):
        desc = ""

        if self.include_where == "dont_include":
            desc = "Don't include "
            if self.internal_external == "internal":
                desc += "internal \"" + self.internal_file_name + "\" "
            if self.internal_external == "external":
                desc += "external \"" + self.external_file_name + "\" "
        else:
            int_ext = ""
            fname = ""
            if self.internal_external == "internal":
                int_ext = "internal "
                fname = "\"" + self.internal_file_name + "\" "
            if self.internal_external == "external":
                int_ext = "external "
                fname = "\"" + self.external_file_name + "\" "

            where = ""
            if self.include_where == "before":
                where = "before "
            if self.include_where == "after":
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

            if (self.internal_external == "internal"):

                if (self.mdl_python == "mdl"):
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

                if (self.mdl_python == "python"):
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

            if (self.internal_external == "external"):

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

    show_simulation_scripting = BoolProperty(name="Simulation Scripting", default=False)
    show_data_model_scripting = BoolProperty(name="Data Model Scripting", default=False)

    dm_internal_file_name = StringProperty ( name = "Internal File Name" )
    dm_external_file_name = StringProperty ( name = "External File Name", subtype='FILE_PATH', default="" )
    # upgrade_data_model_for_script = BoolProperty(name="Upgrade Script", default=False)


    dm_internal_external_enum = [
        ('internal', "Internal", ""),
        ("external", "External",  "")]
    dm_internal_external = bpy.props.EnumProperty(
        items=dm_internal_external_enum, name="Internal/External",
        default='internal',
        description="Choose location of file (internal text or external file).",
        update=check_scripting)

    def execute_selected_script ( self, context ):
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        if (self.dm_internal_external == "internal"):
            print ( "Executing internal script" )
            # Wrap the internal data model in a dictionary with an "mcell" key to make it an external data model
            dm = { 'mcell' : mcell_dm }
            exec ( bpy.data.texts[self.dm_internal_file_name].as_string(), globals(), locals() )
            # Strip off the outer dictionary wrapper because the internal data model does not have the "mcell" key layer
            # dm = dm['mcell']
            # Upgrade the data model if requested.
            # This requires the data model to contain our internal data model versioning keys.
            # An unversioned data model will be upgraded as if it were a pre-1.0 data model when this is set
            # If this is NOT set, then the data model will be assumed to match the current version
            #if (self.upgrade_data_model_for_script):
            dm['mcell'] = context.scene.mcell.upgrade_data_model ( dm['mcell'] )
            # Regenerate the Blender properties to reflect this data model ... including geometry
            context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'], geometry=True )
        else:
            print ( "Executing external script ... not implemented yet!!" )

    def draw_layout ( self, context, layout ):
        """ Draw the scripting "panel" within the layout """
        mcell = context.scene.mcell
        ps = mcell.parameter_system

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'

            #row = layout.row()

            #col = row.column()
            #col.label ( "Simulation Scripting" )
            #col.prop ( self, "show_simulation_scripting" )

            if self.show_simulation_scripting:
                row.prop(self, "show_simulation_scripting", icon='TRIA_DOWN', emboss=False)

                row = box.row()
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
                    selected_script.draw_layout ( context, box )

            else:
                row.prop(self, "show_simulation_scripting", icon='TRIA_RIGHT', emboss=False)


            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'

            if self.show_data_model_scripting:
                row.prop(self, "show_data_model_scripting", icon='TRIA_DOWN', emboss=False)

                row = box.row()
                row.prop ( self, "dm_internal_external", text="" )
                row = box.row()

                if (self.dm_internal_external == "internal"):

                    row.prop_search ( self, "dm_internal_file_name",
                                      context.scene.mcell.scripting, "internal_python_scripts_list",
                                      text="File:", icon='TEXT' )
                    row.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")

                if (self.dm_internal_external == "external"):

                    row.prop ( self, "dm_external_file_name" )
                    row.operator("mcell.scripting_refresh", icon='FILE_REFRESH', text="")

                row = box.row()
                row.operator("mcell.scripting_execute", icon='COLOR_RED')

            else:
                row.prop(self, "show_data_model_scripting", icon='TRIA_RIGHT', emboss=False)



    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

    def needs_a_data_model ( self ):
        return True

    def write_scripting_output ( self, before_after, section, context, mdl_file, filedir, data_model ):
        print ( "################### Write Scripting Ouptut " + before_after + " " + section )
        # mdl_file.write("\n\n/* Begin Custom MDL Inserted %s %s */\n" % (before_after, section))
        for script in self.scripting_list:
            if (script.include_where == before_after) and (script.include_section == section):
                mdl_file.write ( "\n/* Begin file %s */\n\n" % (script.internal_file_name))
                if script.mdl_python == 'mdl':
                    mdl_file.write ( bpy.data.texts[script.internal_file_name].as_string() )
                if script.mdl_python == 'python':
                    mdl_file.write ( "\n/* Before Executing Python %s */\n\n" % (script.internal_file_name))
                    #exec ( bpy.data.texts[script.internal_file_name].as_string(), globals(), locals() )
                    exec ( bpy.data.texts[script.internal_file_name].as_string(), locals() )
                    mdl_file.write ( "\n/* After Executing Python %s */\n\n" % (script.internal_file_name))
                mdl_file.write ( "\n\n/* End file %s */\n\n" % (script.internal_file_name))
        # mdl_file.write("\n\n/* End Custom MDL Inserted %s %s */\n\n" % (before_after, section))



