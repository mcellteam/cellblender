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
from . import data_model
from . import parameter_system
from . import cellblender_utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)





###############################
#   Begin Data_Browser code   #
###############################


class DataBrowserStringProperty(bpy.types.PropertyGroup):
    v = StringProperty(name="DBString")

class DataBrowserIntProperty(bpy.types.PropertyGroup):
    v = IntProperty(name="DBInt")

class DataBrowserFloatProperty(bpy.types.PropertyGroup):
    v = FloatProperty(name="DBFloat")

class DataBrowserBoolProperty(bpy.types.PropertyGroup):
    v = BoolProperty(name="DBBool")

class leaf_item:
    def __init__ ( value, index ):
        self.value = value
        self.index = index

dm = None
dmi = None

class DataBrowserPropertyGroup(bpy.types.PropertyGroup):
    show_list   = CollectionProperty(type=DataBrowserBoolProperty,   name="Show List")

    string_list = CollectionProperty(type=DataBrowserStringProperty, name="String List")
    int_list    = CollectionProperty(type=DataBrowserIntProperty,    name="Int List")
    float_list  = CollectionProperty(type=DataBrowserFloatProperty,  name="Float List")
    bool_list   = CollectionProperty(type=DataBrowserBoolProperty,   name="Bool List")

    internal_file_name = StringProperty ( name = "Internal Text Name" )


    def draw_layout ( self, context, layout ):
        mcell = context.scene.mcell
        scripting = mcell.scripting

        row = layout.row()
        row.operator ( "cb.regenerate_data_model", icon='FILE_REFRESH' )

        row = layout.row()
        col = row.column()
        col.prop ( scripting, "include_geometry_in_dm" )
        col = row.column()
        col.prop ( scripting, "include_scripts_in_dm" )
        col = row.column()
        col.prop ( scripting, "include_dyn_geom_in_dm" )

        row = layout.row()
        col = row.column()
        col.operator ( "browser.from_dm" )
        col = row.column()
        col.operator ( "browser.clear" )

        if len(self.show_list) > 0:
            row = layout.row()
            col = row.column()
            col.operator ( "browser.open_all" )
            col = row.column()
            col.operator ( "browser.close_all" )

        # row = layout.row()
        # row.prop ( self, "internal_file_name" )
        #col = row.column()
        #col.operator ( "browser.from_file" )
        #col = row.column()
        #col.operator ( "browser.to_file" )

        global dm
        global dmi
        self.draw_recurse ( layout, "Model", dm, dmi )


    def convert_recurse ( self, dm ):
        # Convert any structure into an index structure
        # print ( "  Convert: got a dm of type " + str(type(dm)) )
        dmi = None
        if type(dm) == type({'a':1}):
            # Process a dictionary
            new_val = self.show_list.add()
            new_val.v = False
            dmi = ( {}, len(self.show_list)-1 )
            #for k in sorted(dm.keys()):
            #for k in dm.keys():
            for k in sorted([str(k) for k in dm.keys()]):
                dmi[0][k] = self.convert_recurse ( dm[k] )
        elif type(dm) == type(['a',1]):
            # Process a list
            new_val = self.show_list.add()
            new_val.v = False
            dmi = ( [], len(self.show_list)-1 )
            for v in dm:
                dmi[0].append ( self.convert_recurse ( v ) )
        elif (type(dm) == type('a')) or (type(dm) == type(u'a')):  #dm is a string
            new_val = self.string_list.add()
            new_val.v = dm
            dmi = len(self.string_list) - 1
        elif type(dm) == type(1):  # dm is an integer
            new_val = self.int_list.add()
            new_val.v = dm
            dmi = len(self.int_list) - 1
        elif type(dm) == type(1.0):  # dm is a float
            new_val = self.float_list.add()
            new_val.v = dm
            dmi = len(self.float_list) - 1
        elif type(dm) == type(True):  # dm is a boolean
            new_val = self.bool_list.add()
            new_val.v = dm
            dmi = len(self.bool_list) - 1
        else: # dm is unknown
            dmi = None
        # print ( "convert_recurse returning a dmi of type " + str(type(dmi)) )
        return ( dmi )


    def draw_recurse ( self, layout, name, dm, dmi ):
        # Draw the structure
        if type(dmi) == type ( (0,1) ):
            # A tuple represents either a dictionary ({},show_index) or a list ([],show_index)
            row = layout.row()
            box = row.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if type(dmi[0]) == type({'a':1}):
                # Draw a dictionary
                dname = str(name) + "   {" + str(len(dm)) + "}"
                if 'name' in dm.keys():
                    dname = dname + "   (\"" + str(dm['name']) + "\")"
                else:
                    possible_names = [ n for n in dm.keys() if 'name' in n ]
                    if len(possible_names) > 0:
                        dname = dname + "   (\"" + str(dm[possible_names[0]]) + "\")"
                if self.show_list[dmi[1]].v == False:
                    row.prop ( self.show_list[dmi[1]], "v", text=dname, icon='TRIA_RIGHT', emboss=False )
                else:
                    row.prop ( self.show_list[dmi[1]], "v", text=dname, icon='TRIA_DOWN', emboss=False )
                    #for k in sorted(dm.keys()):
                    #for k in dm.keys():
                    for k in sorted([str(k) for k in dm.keys()]):
                        self.draw_recurse ( box, k, dm[k], dmi[0][k] )
            elif type(dmi[0]) == type(['a',1]):
                # Draw a list
                dname = str(name) + "   [" + str(len(dm)) + "]"
                if self.show_list[dmi[1]].v == False:
                    row.prop ( self.show_list[dmi[1]], "v", text=dname, icon='TRIA_RIGHT', emboss=False )
                else:
                    row.prop ( self.show_list[dmi[1]], "v", text=dname, icon='TRIA_DOWN', emboss=False )
                    for k in range(len(dm)):
                        self.draw_recurse ( box, str(name)+'['+str(k)+']', dm[k], dmi[0][k] )
        elif (type(dm) == type('a')) or (type(dm) == type(u'a')):  #dm is a string
            row = layout.row()
            row.prop ( self.string_list[dmi], "v", text=str(name) )
        elif type(dm) == type(1):  # dm is an integer
            row = layout.row()
            row.prop ( self.int_list[dmi], "v", text=str(name) )
        elif type(dm) == type(1.0):  # dm is a float
            row = layout.row()
            row.prop ( self.float_list[dmi], "v", text=str(name) )
        elif type(dm) == type(True):  # dm is a boolean
            row = layout.row()
            row.prop ( self.bool_list[dmi], "v", text=str(name) )
        else: # dm is unknown
            pass

    def clear_lists ( self ):
        self.show_list.clear()
        self.string_list.clear()
        self.int_list.clear()
        self.float_list.clear()
        self.bool_list.clear()

    def convert_text_to_properties ( self, context, layout ):

        global dm
        global dmi

        if not self.internal_file_name in bpy.data.texts:
            print ( "Error: Specify a script name. Name \"" + self.internal_file_name + "\" is not an internal script name. Try refreshing the scripts list." )
        else:
            script_text = bpy.data.texts[self.internal_file_name].as_string()
            print ( 80*"=" )
            print ( script_text )
            print ( 80*"=" )
            dm = eval ( script_text, locals() )
            print ( str(dm) )

            # Clear out the properties that will be used for display
            self.clear_lists()

            dmi = self.convert_recurse ( dm )

            print ( "dmi = \n" + str(dmi) )


    def convert_dm_to_properties ( self, layout ):

        global dm
        global dmi

        # Clear out the properties that will be used for display
        self.clear_lists()

        dmi = self.convert_recurse ( dm )

        return dmi


class FromDMOperator(bpy.types.Operator):
    bl_idname = "browser.from_dm"
    bl_label = "Build Tree"

    def invoke(self, context, event):
        global dm
        global dmi
        mcell = context.scene.mcell
        scripting = mcell.scripting
        db = scripting.data_browser
        dm = mcell.build_data_model_from_properties ( context, geometry=scripting.include_geometry_in_dm,
                                                               scripts=scripting.include_scripts_in_dm,
                                                               dyn_geo=scripting.include_dyn_geom_in_dm )
        dmi = db.convert_dm_to_properties ( self.layout)
        return{'FINISHED'}


class ClearBrowserOperator(bpy.types.Operator):
    bl_idname = "browser.clear"
    bl_label = "Clear Tree"

    def invoke(self, context, event):
        global dm
        global dmi
        mcell = context.scene.mcell
        scripting = mcell.scripting
        db = scripting.data_browser
        db.clear_lists()
        dm = None
        dmi = None
        return{'FINISHED'}


class BrowserOpenAllOperator(bpy.types.Operator):
    bl_idname = "browser.open_all"
    bl_label = "Open All"

    def invoke(self, context, event):
        mcell = context.scene.mcell
        scripting = mcell.scripting
        db = scripting.data_browser
        for s in db.show_list:
          s.v = True
        return{'FINISHED'}


class BrowserCloseAllOperator(bpy.types.Operator):
    bl_idname = "browser.close_all"
    bl_label = "Close All"

    def invoke(self, context, event):
        mcell = context.scene.mcell
        scripting = mcell.scripting
        db = scripting.data_browser
        for s in db.show_list:
          s.v = False
        return{'FINISHED'}


class FromFileOperator(bpy.types.Operator):
    bl_idname = "browser.from_file"
    bl_label = "From File"

    def invoke(self, context, event):
        db = context.scene.mcell.scripting.data_browser
        db.convert_text_to_properties ( context, self.layout)
        return{'FINISHED'}


class ToFileOperator(bpy.types.Operator):
    bl_idname = "browser.to_file"
    bl_label = "To File"

    def invoke(self, context, event):
        return{'FINISHED'}

"""
class Data_Browser_Panel(bpy.types.Panel):
  bl_label = "Data Browser"
  bl_space_type = "VIEW_3D"
  bl_region_type = "TOOLS"
  bl_category = "Data Browser"
  bl_options = {'DEFAULT_CLOSED'}

  def draw(self, context):
    db = context.scene.data_browser
    db.draw_layout(context, self.layout)
"""

#############################
#   End Data_Browser code   #
#############################



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




class CopyDataModelFromSelectedProps(bpy.types.Operator):
    '''Copy the selected data model section to the Clipboard'''
    bl_idname = "cb.copy_sel_data_model_to_cbd"
    bl_label = "Copy"
    bl_description = "Copy the selected data model section to the Clipboard"

    def execute(self, context):
        print ( "Copying CellBlender Data Model:" )
        mcell = context.scene.mcell
        scripting = mcell.scripting
        section = str(mcell.scripting.dm_section)
        print ( "Copying section " + section )
        full_dm = mcell.build_data_model_from_properties ( context, geometry=scripting.include_geometry_in_dm,
                                                                    scripts=scripting.include_scripts_in_dm,
                                                                    dyn_geo=scripting.include_dyn_geom_in_dm )
        selected_dm = full_dm
        selected_key = "dm['mcell']"
        if section != 'ALL':
            if section in full_dm:
                selected_dm = full_dm[section]
            else:
                selected_dm = ""
            selected_key += '[\'' + section + '\']'
        # Clean up selected_dm as desired
        if 'mol_viz' in selected_dm:
          selected_dm['mol_viz']['file_dir'] = ""
        else:
          if ('file_dir' in selected_dm) and ('viz_list' in selected_dm):
            # This is likely to be a "mol_viz" entry
            selected_dm['file_dir'] = ""

        #s = "dm['mcell'] = " + pprint.pformat ( selected_dm, indent=4, width=40 ) + "\n"
        s = selected_key + " = " + data_model.data_model_as_text ( selected_dm ) + "\n"
        #s = "dm['mcell'] = " + str(selected_dm) + "\n"
        bpy.context.window_manager.clipboard = s
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


# Scripting Property Groups


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

    def init_properties ( self, parameter_system ):
        pass

    def build_data_model_from_properties ( self, context ):
        print ( "Scripting Item building Data Model" )
        dm = {}
        dm['data_model_version'] = "DM_2016_03_15_1900"
        dm['name'] = self.name
        dm['internal_file_name'] = self.internal_file_name
        dm['external_file_name'] = self.external_file_name
        dm['include_where'] = self.include_where
        dm['include_section'] = self.include_section
        dm['internal_external'] = self.internal_external
        dm['mdl_python'] = self.mdl_python
        return dm

    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading CellBlenderScriptingProperty Data Model" )
        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2016_03_15_1900
            dm['data_model_version'] = "DM_2016_03_15_1900"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2016_03_15_1900":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade CellBlenderScriptingProperty data model to current version." )
            return None

        return dm

    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2016_03_15_1900":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade CellBlenderScriptingProperty data model to current version." )
        self.init_properties(context.scene.mcell.parameter_system)

        self.name = dm["name"]
        self.internal_file_name = dm["internal_file_name"]
        self.external_file_name = dm["external_file_name"]
        self.include_where = dm["include_where"]
        self.include_section = dm["include_section"]
        self.internal_external = dm["internal_external"]
        self.mdl_python = dm["mdl_python"]



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
    ignore_cellblender_data = BoolProperty(name="Ignore CellBlender Data", default=False)

    internal_mdl_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="MDL Internal Scripts")
    external_mdl_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="MDL External Scripts")
    internal_python_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="Python Internal Scripts")
    external_python_scripts_list = CollectionProperty(type=CellBlenderScriptProperty, name="Python External Scripts")

    show_simulation_scripting = BoolProperty(name="Export Scripting", default=False)
    show_data_model_scripting = BoolProperty(name="Data Model Scripting", default=False)
    show_data_model_script_make = BoolProperty(name="Make Script", default=False)
    show_data_model_script_run = BoolProperty(name="Run Script", default=False)
    show_data_model_browser = BoolProperty(name="Data Model Browser", default=False)

    dm_internal_file_name = StringProperty ( name = "Internal File Name" )
    dm_external_file_name = StringProperty ( name = "External File Name", subtype='FILE_PATH', default="" )
    force_property_update = BoolProperty(name="Update CellBlender from Data Model", default=True)
    # upgrade_data_model_for_script = BoolProperty(name="Upgrade Script", default=False)

    # The following properties are associated with Data Model Scripting
    include_geometry_in_dm = bpy.props.BoolProperty ( name = "Include Geometry", description = "Include Geometry in the Data Model", default = False )
    include_scripts_in_dm = bpy.props.BoolProperty ( name = "Include Scripts", description = "Include Scripts in the Data Model", default = False )
    include_dyn_geom_in_dm = bpy.props.BoolProperty ( name = "Dynamic Geometry", description = "Include Dynamic Geometry in the Data Model", default = False )

    dm_section_enum = [
        ('ALL',                     "All", ""),
        ('define_molecules',        "Molecules", ""),
        ('define_reactions',        "Reactions",  ""),
        ('define_release_patterns', "Release Time Patterns",  ""),
        ('define_surface_classes',  "Surface Classes",  ""),
        ('geometrical_objects',     "Geometrical Objects",  ""),
        ('initialization',          "Initialization",  ""),
        ('materials',               "Materials",  ""),
        ('model_objects',           "Model Objects",  ""),
        ('modify_surface_regions',  "Surface Regions",  ""),
        ('mol_viz',                 "Molecule Visualization",  ""),
        ('parameter_system',        "Parameters",  ""),
        ('reaction_data_output',    "Plot Data",  ""),
        ('release_sites',           "Release Sites",  ""),
        ('simulation_control',      "Simulation Control",  ""),
        ('viz_output',              "Visualization Data",  "")]
    dm_section = bpy.props.EnumProperty(
        items=dm_section_enum, name="Data Model Section",
        default='define_molecules',
        description="Data Model Section to copy to the Clipboard" )

    dm_internal_external_enum = [
        ('internal', "Internal", ""),
        ("external", "External",  "")]
    dm_internal_external = bpy.props.EnumProperty(
        items=dm_internal_external_enum, name="Internal/External",
        default='internal',
        description="Choose location of file (internal text or external file).",
        update=check_scripting)


    data_browser = PointerProperty(type=DataBrowserPropertyGroup)


    def init_properties ( self, parameter_system ):
        pass

    def build_data_model_from_properties ( self, context, scripts=False ):
        dm = {}
        dm['data_model_version'] = "DM_2017_11_30_1830"
        dm['ignore_cellblender_data'] = self.ignore_cellblender_data
        #dm['show_simulation_scripting'] = self.show_simulation_scripting
        #dm['show_data_model_scripting'] = self.show_data_model_scripting
        dm['dm_internal_file_name'] = self.dm_internal_file_name
        dm['dm_external_file_name'] = self.dm_external_file_name
        dm['force_property_update'] = self.force_property_update
        s_list = []
        for s in self.scripting_list:
            s_list.append ( s.build_data_model_from_properties(context) )
        dm['scripting_list'] = s_list

        # Don't: Store the scripts lists in the data model for now - they are regenerated when rebuilding properties

        # Do: Store all .mdl text files and all .py text files if scripts flag is True (defaults to false)

        texts = {}
        if scripts:
          for txt in bpy.data.texts:
             if (txt.name[-4:] == ".mdl") or (txt.name[-3:] == ".py"):
                texts[txt.name] = txt.as_string()
        dm['script_texts'] = texts

        return dm

    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading CellBlenderScriptingPropertyGroup Data Model" )
        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2016_03_15_1900
            dm['data_model_version'] = "DM_2016_03_15_1900"

        if dm['data_model_version'] == "DM_2016_03_15_1900":
            # Add the ignore_cellblender_data flag as False (the prior behaviour before this change)
            dm['ignore_cellblender_data'] = False
            dm['data_model_version'] = "DM_2017_11_30_1830"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2017_11_30_1830":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade CellBlenderScriptingPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm, scripts=True ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2017_11_30_1830":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade CellBlenderScriptingPropertyGroup data model to current version." )
        self.init_properties(context.scene.mcell.parameter_system)

        self.ignore_cellblender_data = dm['ignore_cellblender_data']
        #self.show_simulation_scripting = dm["show_simulation_scripting"]
        #self.show_data_model_scripting = dm["show_data_model_scripting"]
        self.dm_internal_file_name = dm["dm_internal_file_name"]
        self.dm_external_file_name = dm["dm_external_file_name"]
        self.force_property_update = dm["force_property_update"]

        while len(self.scripting_list) > 0:
            self.scripting_list.remove(0)
        if "scripting_list" in dm:
            for dm_s in dm["scripting_list"]:
                self.scripting_list.add()
                self.active_scripting_index = len(self.scripting_list)-1
                s = self.scripting_list[self.active_scripting_index]
                # s.init_properties(context.scene.mcell.parameter_system)
                s.build_properties_from_data_model ( context, dm_s )

        if scripts:
          print ( "\nReading scripts because \"scripts\" parameter is true\n" )
          if 'script_texts' in dm:
            for key_name in dm['script_texts'].keys():
              print ( "  Script: " + key_name )
              if key_name in bpy.data.texts:
                bpy.data.texts[key_name].clear()
              else:
                bpy.data.texts.new(key_name)
              bpy.data.texts[key_name].write ( dm['script_texts'][key_name] )
        else:
          print ( "\nNot reading scripts because \"scripts\" parameter is false\n" )

        # Update the list of available scripts (for the user interface list)
        update_available_scripts ( self )


    def execute_selected_script ( self, context ):
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        if (self.dm_internal_external == "internal"):
            print ( "Executing internal script" )
            if not self.dm_internal_file_name in bpy.data.texts:
                print ( "Error: Specify a script name. Name \"" + self.dm_internal_file_name + "\" is not an internal script name. Try refreshing the scripts list." )
            elif False:
                # This was the run code before adding cb.get_data_model and cb.replace_data_model to the user's API
                # Wrap the internal data model in a dictionary with an "mcell" key to make it an external data model
                dm = { 'mcell' : mcell_dm }
                #exec ( bpy.data.texts[self.dm_internal_file_name].as_string(), globals(), locals() )
                original_cwd = os.getcwd()
                os.makedirs ( cellblender_utils.project_files_path(), exist_ok=True )
                os.chdir ( cellblender_utils.project_files_path() )
                script_text = bpy.data.texts[self.dm_internal_file_name].as_string()
                print ( 80*"=" )
                print ( script_text )
                print ( 80*"=" )
                exec ( script_text, locals() )
                os.chdir ( original_cwd )
                # Strip off the outer dictionary wrapper because the internal data model does not have the "mcell" key layer
                # dm = dm['mcell']
                # Upgrade the data model if requested.
                # This requires the data model to contain our internal data model versioning keys.
                # An unversioned data model will be upgraded as if it were a pre-1.0 data model when this is set
                # If this is NOT set, then the data model will be assumed to match the current version
                #if (self.upgrade_data_model_for_script):
                if self.force_property_update:
                    dm['mcell'] = context.scene.mcell.upgrade_data_model ( dm['mcell'] )
                    # Regenerate the Blender properties to reflect this data model ... including geometry
                    context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'], geometry=True )
            elif False:
                # This version runs the script from the project directory
                original_cwd = os.getcwd()
                os.makedirs ( cellblender_utils.project_files_path(), exist_ok=True )
                os.chdir ( cellblender_utils.project_files_path() )
                script_text = bpy.data.texts[self.dm_internal_file_name].as_string()
                print ( 80*"=" )
                print ( script_text )
                print ( 80*"=" )
                exec ( script_text, locals() )
                os.chdir ( original_cwd )
            else:
                # This version just runs the script
                script_text = bpy.data.texts[self.dm_internal_file_name].as_string()
                print ( 80*"=" )
                print ( script_text )
                print ( 80*"=" )
                exec ( script_text, locals() )
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
            #col.label ( "Export Scripting" )
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
                    if len(self.scripting_list) > 0:
                        selected_script = self.scripting_list[self.active_scripting_index]
                        selected_script.draw_layout ( context, box )
                row = box.row()
                row.prop ( self, "ignore_cellblender_data" )


            else:
                row.prop(self, "show_simulation_scripting", icon='TRIA_RIGHT', emboss=False)


            parent_box = layout.box()
            row = parent_box.row(align=True)
            row.alignment = 'LEFT'

            if self.show_data_model_scripting:
                row.prop(self, "show_data_model_scripting", icon='TRIA_DOWN', emboss=False)

                box = parent_box.box()
                row = box.row(align=True)
                row.alignment = 'LEFT'

                if self.show_data_model_script_make:
                    row.prop(self, "show_data_model_script_make", icon='TRIA_DOWN', emboss=False)

                    row = box.row()
                    row.operator ( "cb.regenerate_data_model", icon='FILE_REFRESH' )

                    try:
                        # Try to import tkinter to see if it is installed in this version of Blender
                        import tkinter as tk
                        row = box.row()
                        row.operator ( "cb.tk_browse_data_model", icon='ZOOM_ALL' )

                    except ( ImportError ):
                        # Unable to import needed libraries so don't draw
                        print ( "Unable to import tkinter for TK Data Model Browser" )
                        """
                        row = box.row()
                        col = row.column()
                        col.operator ( "cb.copy_data_model_to_cbd" )
                        col = row.column()
                        col.prop ( self, "include_geometry_in_dm" )
                        """
                        pass

                    if 'data_model' in mcell:
                        row = box.row()
                        col = row.column()
                        col.prop ( self, "include_geometry_in_dm" )
                        col = row.column()
                        col.prop ( self, "include_scripts_in_dm" )
                        col = row.column()
                        col.prop ( self, "include_dyn_geom_in_dm" )

                        row = box.row()
                        col = row.column()
                        col.prop ( self, "dm_section", text="" )
                        col = row.column()
                        col.operator ( "cb.copy_sel_data_model_to_cbd", icon='COPYDOWN' )



                        """
                        # This created the line by line labels - locked up Blender when too many labels were created
                        dm = unpickle_data_model ( mcell['data_model'] )
                        dm_list = list_data_model ( "Data Model", { "mcell": dm }, [] )
                        for line in dm_list:
                            row = box.row()
                            row.label(text=line)
                        """


                else:
                    row.prop(self, "show_data_model_script_make", icon='TRIA_RIGHT', emboss=False)


                box = parent_box.box()
                row = box.row(align=True)
                row.alignment = 'LEFT'

                if self.show_data_model_script_run:
                    row.prop(self, "show_data_model_script_run", icon='TRIA_DOWN', emboss=False)

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

                    # This is now part of the code's API
                    #row = box.row()
                    #row.prop ( self, "force_property_update" )

                    row = box.row()
                    col = row.column()
                    col.operator("mcell.scripting_execute", text="Run Script", icon='SCRIPTWIN')
                    # TODO: The following operator is not enabled (probably in the wrong context in the 3D view rather than text editor)
                    #col = row.column()
                    #col.operator("text.run_script", text="Run Script", icon='SCRIPTWIN')
                    col = row.column()
                    col.operator("mcell.delete", text="Clear Project", icon='RADIO')   # or use 'X'

                else:
                    row.prop(self, "show_data_model_script_run", icon='TRIA_RIGHT', emboss=False)

            else:
                row.prop(self, "show_data_model_scripting", icon='TRIA_RIGHT', emboss=False)

            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if self.show_data_model_browser:
                row.prop(self, "show_data_model_browser", icon='TRIA_DOWN', emboss=False)
                self.data_browser.draw_layout ( context, box )
            else:
                row.prop(self, "show_data_model_browser", icon='TRIA_RIGHT', emboss=False)


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
                if script.internal_external == 'internal':
                    mdl_file.write ( "\n/* Begin file %s */\n\n" % (script.internal_file_name))
                else:
                    mdl_file.write ( "\n/* Begin file %s */\n\n" % (script.external_file_name))
                if script.mdl_python == 'mdl':
                    if script.internal_external == 'internal':
                        mdl_file.write ( bpy.data.texts[script.internal_file_name].as_string() )
                    else:
                        print ( "Loading external MDL script: " + script.external_file_name )
                        f = None
                        if script.external_file_name.startswith ( "//" ):
                            # Convert the file name from blend file relative (//) to full path:
                            f = open ( os.path.join ( os.path.dirname(bpy.data.filepath), script.external_file_name[2:] ), mode='r' )
                        else:
                            f = open ( script.external_file_name, mode='r' )
                        script_text = f.read()
                        mdl_file.write ( script_text )
                if script.mdl_python == 'python':
                    if script.internal_external == 'internal':
                        mdl_file.write ( "\n/* Before Executing Python %s */\n\n" % (script.internal_file_name))
                        exec ( bpy.data.texts[script.internal_file_name].as_string(), locals() )
                        mdl_file.write ( "\n/* After Executing Python %s */\n\n" % (script.internal_file_name))
                    else:
                        print ( "Loading external Python script: " + script.external_file_name )
                        f = None
                        if script.external_file_name.startswith ( "//" ):
                            # Convert the file name from blend file relative (//) to full path:
                            f = open ( os.path.join ( os.path.dirname(bpy.data.filepath), script.external_file_name[2:] ), mode='r' )
                        else:
                            f = open ( script.external_file_name, mode='r' )
                        script_text = f.read()
                        mdl_file.write ( "\n/* Before Executing Python %s */\n\n" % (script.external_file_name))
                        exec ( script_text, locals() )
                        mdl_file.write ( "\n/* After Executing Python %s */\n\n" % (script.external_file_name))
                if script.internal_external == 'internal':
                    mdl_file.write ( "\n\n/* End file %s */\n\n" % (script.internal_file_name))
                else:
                    mdl_file.write ( "\n\n/* End file %s */\n\n" % (script.external_file_name))
        # mdl_file.write("\n\n/* End Custom MDL Inserted %s %s */\n\n" % (before_after, section))



