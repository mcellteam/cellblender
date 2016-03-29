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
This file contains the classes defining and handling the CellBlender Data Model.
The CellBlender Data Model is intended to be a fairly stable representation of
a CellBlender project which should be compatible across CellBlender versions.
"""


"""
  CONVERSION NOTES:
    How do our CellBlender reaction fields/controls handle catalytic reactions?
    Would it be better to allow a full reaction expression rather than reactants/products?
    Should we have an option for using full reaction syntax?
    What is the MCellReactionsPanelProperty.reaction_name_list? Is it needed any more?
    
    MCellMoleculeReleaseProperty:
       Do we still need location, or is it handled by location_x,y,z?

    Release Patterns:

      Should "release pattern" be called "release timing" or "release train"?

      Why does MCellReleasePatternPanelProperty contain:
         release_pattern_rxn_name_list?
      JC: There is a "Release Pattern" field in the "Molecule Placement" panel.
      One can assign either a release pattern or a named reaction to it. 
       
"""


# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent

# python imports
import pickle
import pprint
import json
import os

from bpy_extras.io_utils import ExportHelper
import cellblender
# import cellblender/cellblender_id


def code_api_version():
    return 1


def flag_incompatible_data_model ( message ):
    print ( "#########################################################" )
    print ( "#########################################################" )
    print ( "Note: an Incompatible CellBlender Data Model was detected" )
    print ( message )
    print ( "#########################################################" )
    print ( "#########################################################" )

def handle_incompatible_data_model ( message ):
    print ( "###########################################################" )
    print ( "###########################################################" )
    print ( "Quitting Blender due to Incompatible CellBlender Data Model" )
    print ( message )
    print ( "###########################################################" )
    print ( "###########################################################" )
    bpy.ops.wm.quit_blender()


data_model_depth = 0
def dump_data_model ( name, dm ):
    global data_model_depth
    if type(dm) == type({'a':1}):  #dm is a dictionary
        print ( str(data_model_depth*"  ") + name + " {}" )
        data_model_depth += 1
        for k,v in sorted(dm.items()):
            dump_data_model ( k, v )
        data_model_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
        print ( str(data_model_depth*"  ") + name + " []" )
        data_model_depth += 1
        i = 0
        for v in dm:
            k = name + "["+str(i)+"]"
            dump_data_model ( k, v )
            i += 1
        data_model_depth += -1
    # elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
    elif (type(dm) == type('a1')):  #dm is a string
        print ( str(data_model_depth*"  ") + name + " = " + "\"" + str(dm) + "\"" )
    else:
        print ( str(data_model_depth*"  ") + name + " = " + str(dm) )


dm_list_depth = 0
def list_data_model ( name, dm, dm_list ):
    """Generate a list of the data model elements one line per item"""
    global dm_list_depth
    if type(dm) == type({'a':1}):  #dm is a dictionary
        dm_list.append ( str(dm_list_depth*"   ") + name + " {}" )
        dm_list_depth += 1
        for k,v in sorted(dm.items()):
            list_data_model ( k, v, dm_list )
        dm_list_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
        dm_list.append ( str(dm_list_depth*"   ") + name + " []" )
        dm_list_depth += 1
        i = 0
        for v in dm:
            k = name + "["+str(i)+"]"
            list_data_model ( k, v, dm_list )
            i += 1
        dm_list_depth += -1
    # elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
    elif (type(dm) == type('a1')):  #dm is a string
        dm_list.append ( str(dm_list_depth*"   ") + name + " = " + "\"" + str(dm) + "\"" )
    else:
        dm_list.append ( str(dm_list_depth*"   ") + name + " = " + str(dm) )
    return dm_list


dm_indent_by = 2
dm_text_depth = 0
def text_data_model ( name, dm, dm_list, comma ):
    """Generate a list of the data model elements with indenting"""
    global dm_text_depth
    indent = dm_indent_by*" "
    dict_type = type({'a':1})
    list_type = type(['a',1])
    if type(dm) == dict_type:  #dm is a dictionary
        num_items = len(dm.keys())
        if num_items == 0:
            dm_list.append ( str(dm_text_depth*indent) + name + "{}" + comma )
        else:
            dm_list.append ( str(dm_text_depth*indent) + name + "{" )
            dm_text_depth += 1
            item_num = 0
            for k,v in sorted(dm.items()):
                subcomma = ','
                if item_num > num_items-2:
                  subcomma = ''
                text_data_model ( "\'"+k+"\'"+" : ", v, dm_list, subcomma )
                item_num += 1
            dm_text_depth += -1
            dm_list.append ( str(dm_text_depth*indent) + "}" + comma )
    elif type(dm) == list_type:  #dm is a list
        num_items = len(dm)
        if num_items == 0:
            dm_list.append ( str(dm_text_depth*indent) + name + "[]" + comma )
        else:
            one_liner = True
            if num_items > 4:
                one_liner = False
            for v in dm:
                if type(v) in [dict_type, list_type]:
                  one_liner = False
                  break
            if one_liner:
                dm_list.append ( str(dm_text_depth*indent) + name + str(dm) + comma )
            else:
                dm_list.append ( str(dm_text_depth*indent) + name + "[" )
                dm_text_depth += 1
                i = 0
                for v in dm:
                    k = name + "["+str(i)+"]"
                    subcomma = ','
                    if i > num_items-2:
                      subcomma = ''
                    text_data_model ( "", v, dm_list, subcomma )
                    i += 1
                dm_text_depth += -1
                dm_list.append ( str(dm_text_depth*indent) + "]" + comma )
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
        dm_list.append ( str(dm_text_depth*indent) + name + "\"" + str(dm) + "\"" + comma )
    else:
        dm_list.append ( str(dm_text_depth*indent) + name + str(dm) + comma )
    return dm_list


def data_model_as_text ( dm ):
    dm_list = text_data_model ( "", dm, [], "" )
    s = ""
    for l in dm_list:
        s += l + "\n"
    return s


def pickle_data_model ( dm ):
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

def unpickle_data_model ( dmp ):
    return ( pickle.loads ( dmp.encode('latin1') ) )

def json_from_data_model ( dm ):
    return ( json.dumps ( dm ) )

def data_model_from_json ( dmp ):
    return ( json.loads ( dmp ) )


def save_data_model_to_json_file ( mcell_dm, file_name ):
    print ( "Saving CellBlender model to JSON file: " + file_name )
    f = open ( file_name, 'w' )
    f.write ( json_from_data_model ( {"mcell": mcell_dm} ) )
    f.close()


def save_data_model_to_file ( mcell_dm, file_name ):
    print ( "Saving CellBlender model to file: " + file_name )
    dm = { 'mcell': mcell_dm }
    f = open ( file_name, 'w' )
    f.write ( pickle_data_model(dm) )
    f.close()
    print ( "Done saving CellBlender model." )


class MCELL_PT_data_model_browser(bpy.types.Panel):
    bl_label = "CellBlender - Data Model Browser"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "CellBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        row = layout.row()
        row.operator ( "cb.regenerate_data_model" )

        try:
            # Try to import tkinter to see if it is installed in this version of Blender
            import tkinter as tk
            row = layout.row()
            row.operator ( "cb.tk_browse_data_model" )

        except ( ImportError ):
            # Unable to import needed libraries so don't draw
            print ( "Unable to import tkinter for TK Data Model Browser" )
            row = layout.row()
            col = row.column()
            col.operator ( "cb.copy_data_model_to_cbd" )
            col = row.column()
            col.prop ( mcell.scripting, "include_geometry_in_dm" )
            pass

        if 'data_model' in mcell:
            row = layout.row()
            col = row.column()
            if not mcell.scripting.show_dm_flag:
                col.prop ( mcell.scripting, "show_dm_flag", icon='TRIA_RIGHT', text="Copy Data Model", emboss=False)
                col = row.column()
                col.prop ( mcell.scripting, "include_geometry_in_dm" )
                col = row.column()
                col.prop ( mcell.scripting, "include_scripts_in_dm" )
            else:
                col.prop ( mcell.scripting, "show_dm_flag", icon='TRIA_DOWN', text="Copy Data Model", emboss=False)
                col = row.column()
                col.prop ( mcell.scripting, "include_geometry_in_dm" )
                col = row.column()
                col.prop ( mcell.scripting, "include_scripts_in_dm" )
                row = layout.row()
                row.operator ( "cb.copy_data_model_to_cbd", icon='COPYDOWN' )
                row = layout.row()
                row.operator ( "cb.copy_mols_to_cbd", icon='COPYDOWN' )
                row = layout.row()
                row.operator ( "cb.copy_rels_to_cbd", icon='COPYDOWN' )

                """
                # This created the line by line labels - locked up Blender when too many labels were created
                dm = unpickle_data_model ( mcell['data_model'] )
                dm_list = list_data_model ( "Data Model", { "mcell": dm }, [] )
                for line in dm_list:
                    row = layout.row()
                    row.label(text=line)
                """

class CopyDataModelFromProps(bpy.types.Operator):
    '''Copy the data model to the Clipboard'''
    bl_idname = "cb.copy_data_model_to_cbd"
    bl_label = "Copy Entire Data Model"
    bl_description = "Copy the data model to the Clipboard"

    def execute(self, context):
        print ( "Copying CellBlender Data Model:" )
        mcell = context.scene.mcell
        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=mcell.scripting.include_geometry_in_dm, scripts=mcell.scripting.include_scripts_in_dm )
        #s = "dm['mcell'] = " + pprint.pformat ( mcell_dm, indent=4, width=40 ) + "\n"
        s = "dm['mcell'] = " + data_model_as_text ( mcell_dm ) + "\n"
        #s = "dm['mcell'] = " + str(mcell_dm) + "\n"
        bpy.context.window_manager.clipboard = s
        return {'FINISHED'}


class CopyDataModelFromMols(bpy.types.Operator):
    '''Copy the molecules data model to the Clipboard'''
    bl_idname = "cb.copy_mols_to_cbd"
    bl_label = "Copy Molecules Data Model"
    bl_description = "Copy the molecules data model to the Clipboard"

    def execute(self, context):
        mcell = context.scene.mcell
        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=False )
        # s = "dm['mcell']['define_molecules'] = " + pprint.pformat ( mcell_dm['define_molecules'], indent=4, width=40 ) + "\n"
        s = "dm['mcell']['define_molecules'] = " + data_model_as_text ( mcell_dm['define_molecules'] ) + "\n"
        bpy.context.window_manager.clipboard = s
        return {'FINISHED'}


class CopyDataModelFromRels(bpy.types.Operator):
    '''Copy the release site data model to the Clipboard'''
    bl_idname = "cb.copy_rels_to_cbd"
    bl_label = "Copy Release Site Data Model"
    bl_description = "Copy the release site data model to the Clipboard"

    def execute(self, context):
        mcell = context.scene.mcell
        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=False )
        # s = "dm['mcell']['release_sites'] = " + pprint.pformat ( mcell_dm['release_sites'], indent=4, width=40 ) + "\n"
        s = "dm['mcell']['release_sites'] = " + data_model_as_text ( mcell_dm['release_sites'] ) + "\n"
        bpy.context.window_manager.clipboard = s
        
        return {'FINISHED'}



# Set up to run tkinter code in another thread

try:
    import tkinter as tk
    from tkinter import ttk as ttk
    from tkinter import messagebox
    import threading
    import random

    import bpy

    class CellBlenderDataModelBrowser(threading.Thread):

        depth = 0

        copy_with_pretty_print = True

        def build_tree_from_data_model ( self, parent_id, name, dm ):
            self.depth += 1
            draw_as_open = self.depth <= 1
            if type(dm) == type({'a':1}):  # dm is a dictionary
              name_str = name + " {} (" + str(len(dm)) + ")"
              if 'name' in dm:
                if len(dm['name']) > 0:
                  name_str += " = " + dm['name']
              else:
                name_keys = [k for k in dm.keys() if k.endswith('_name')]
                if len(name_keys) == 1:
                  if len(str(dm[name_keys[0]])) > 0:
                    name_str += " = " + str(dm[name_keys[0]])
              new_parent = self.tree.insert(parent_id, 'end', text=name_str, open=draw_as_open, tags='d:'+name)
              for k,v in sorted(dm.items()):
                self.build_tree_from_data_model ( new_parent, k, v )
            elif type(dm) == type(['a',1]):  # dm is a list
              i = 0
              new_parent = self.tree.insert(parent_id, 'end', text=name+" [] ("+str(len(dm))+")", open=draw_as_open, tags='l:'+name)
              for v in dm:
                self.build_tree_from_data_model ( new_parent, str(i), v )
                i += 1
            elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
              new_parent = self.tree.insert(parent_id, 'end', text=name + " = " + "\"" + str(dm) + "\"", open=draw_as_open, tags='s:'+name)
            elif type(dm) == type(True):  # dm is a boolean
              new_parent = self.tree.insert(parent_id, 'end', text=name + " = " + str(dm), open=draw_as_open, tags='b:'+name)
            elif type(dm) == type(1.0):  # dm is a float
              new_parent = self.tree.insert(parent_id, 'end', text=name + " = " + str(dm), open=draw_as_open, tags='f:'+name)
            elif type(dm) == type(1):  # dm is an integer
              new_parent = self.tree.insert(parent_id, 'end', text=name + " = " + str(dm), open=draw_as_open, tags='i:'+name)
            else: # dm is unknown
              new_parent = self.tree.insert(parent_id, 'end', text=name + " = " + str(dm), open=draw_as_open, tags='?:'+name)
            self.depth += -1

        w = 800
        h = 800

        def __init__(self):
            threading.Thread.__init__(self)
            self.start()


        current_data_model = None

        def load_data_model(self):
            if 'mcell' in bpy.context.scene:
                if "data_model" in bpy.context.scene.mcell.keys():
                    dm = pickle.loads ( bpy.context.scene.mcell['data_model'].encode('latin1') )
                    if len(self.tree.get_children()) > 0:
                        self.tree.delete ( self.tree.get_children() )
                    root_id = self.tree.insert ( '', 'end', text='Data_Model', values=[""], open=True, tags='d')
                    self.build_tree_from_data_model ( root_id, "mcell", dm )
                    self.current_data_model = { 'mcell' : dm }


        def set_copy_as_one_line(self):
            self.copy_with_pretty_print = False

        def set_copy_as_pretty_print(self):
            self.copy_with_pretty_print = True


        def random_color_string(self):
            red = hex(int(random.uniform(16,256)))[2:4]
            grn = hex(int(random.uniform(16,256)))[2:4]
            blu = hex(int(random.uniform(16,256)))[2:4]
            return ( "#"+red+grn+blu )

        def random_ends(self):
            x0 = int(self.w*random.random())
            y0 = int(self.h*random.random())
            x1 = int(self.w*random.random())
            y1 = int(self.h*random.random())
            ends = (x0, y0, x1, y1)
            return ends

        def random_line(self):
            print ( "Draw a random line" )
            e = self.random_ends()
            self.c.create_line(e[0],e[1],e[2],e[3],fill=self.random_color_string())

        def random_box(self):
            print ( "Draw a random box" )
            e = self.random_ends()
            self.c.create_rectangle(e[0],e[1],e[2],e[3],fill=self.random_color_string())

        def resize_window(self, event):
            if str(event.widget) == '.':
                self.w = event.width

        def item_select(self, event):
            selected_item = event.widget.item(event.widget.selection()[0])

            # Build an expression to reference this item from inside the data model

            expr = ""
            iid_expr = ""
            selected_iid = event.widget.selection()[0]
            while len(selected_iid) > 0:
                item = self.tree.item(selected_iid)
                type_tag = item['tags'][0]
                parent = self.tree.parent(selected_iid)
                parent_type_tags = self.tree.item(parent)['tags']
                parent_type_tag = ""
                if len(parent_type_tags) > 0:
                    parent_type_tag = parent_type_tags[0][0]
                if ('tags' in item) and (len(item['tags']) > 0):
                    if len(parent) == 0:
                        expr = 'dm' + expr
                    elif parent_type_tag == 'l':
                        expr = '[' + item['text'].split()[0] + ']' + expr
                    else:
                        expr = '[\'' + item['text'].split()[0] + '\']' + expr
                else:
                    expr = " /* " + item['text'] + " /* " + expr
                iid_expr = selected_iid + "/" + iid_expr
                selected_iid = self.tree.parent(selected_iid)

            value = ""
            try:
                dm = self.current_data_model   # Copy to local name "dm" since that's what's used in expr
                value = eval(expr)
                if self.copy_with_pretty_print:
                    value = pprint.pformat ( value, indent=4, width=40 ) + "\n"
            except:
                pass

            self.root.clipboard_clear()
            self.root.clipboard_append ( expr + " = " + str(value) + "\n" )

        def copy_selected(self):
            if len(self.tree.selection()) > 0:
                selected_item = self.tree.item(self.tree.selection()[0])
                self.root.clipboard_clear()
                self.root.clipboard_append(str(selected_item['text']))

        def destroy(self):
            if messagebox.askyesno("Exit", "Do you want to close the Data Model Browser?"):
                # print ( "Destroying Tk" )
                self.root.destroy()

        def debug(self):
            __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

        def run(self):
            self.root = tk.Tk()
            self.root.wm_title("CellBlender Data Model Browser")
            self.root.protocol("WM_DELETE_WINDOW", self.destroy)

            self.top = self.root.winfo_toplevel()
            self.menuBar = tk.Menu(self.top)
            self.top['menu'] = self.menuBar

            self.dmMenu = tk.Menu ( self.menuBar )
            self.dmMenu.add_command ( label='Reload', command = self.load_data_model )
            self.dmMenu.add_command ( label='Copy with Pretty Print', command = self.set_copy_as_pretty_print )
            self.dmMenu.add_command ( label='Copy as One Line', command = self.set_copy_as_one_line )
            self.menuBar.add_cascade(label="Data Model", menu=self.dmMenu)

            self.root.bind_all ( '<Configure>', self.resize_window )

            self.tree = ttk.Treeview(self.root, show='tree', selectmode='browse' )
            self.tree.bind ( '<<TreeviewSelect>>', self.item_select )
            vscroll = ttk.Scrollbar(self.root, orient='vertical', command=self.tree.yview)
            self.tree.configure(yscroll=vscroll.set)

            self.tree.pack(fill=tk.BOTH,expand=1)

            self.load_data_model()

            self.root.mainloop()

except ( ImportError ):
    # Unable to import needed libraries so don't draw
    print ( "Unable to import libraries needed for Data Model Editor ... most likely tkinter" )
    pass



class TkBrowseDataModelFromProps(bpy.types.Operator):
    '''Browse/Copy the data model with a Tk Application (requires tkinter installation)'''
    bl_idname = "cb.tk_browse_data_model"
    bl_label = "Browse Data Model with Tk"
    bl_description = "Browse/Copy the data model with a Tk Application (requires tkinter installation)"

    def execute(self, context):
        print ( "Browsing CellBlender Data Model:" )
        mcell = context.scene.mcell
        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=mcell.scripting.include_geometry_in_dm )
        mcell['data_model'] = pickle_data_model ( mcell_dm )
        app = CellBlenderDataModelBrowser()
        return {'FINISHED'}


class RegenerateDataModelFromProps(bpy.types.Operator):
    '''Regenerate the data model from the properties'''
    bl_idname = "cb.regenerate_data_model"
    bl_label = "Regenerate Data Model"
    bl_description = "Regenerate the data model from the Blender Properties"

    def execute(self, context):
        print ( "Showing CellBlender Data Model:" )
        mcell = context.scene.mcell
        mcell_dm = mcell.build_data_model_from_properties ( context, geometry=mcell.scripting.include_geometry_in_dm )
        mcell['data_model'] = pickle_data_model ( mcell_dm )
        return {'FINISHED'}


class PrintDataModel(bpy.types.Operator):
    '''Print the CellBlender data model to the console'''
    bl_idname = "cb.print_data_model" 
    bl_label = "Print Data Model"
    bl_description = "Print the CellBlender Data Model to the console"

    def execute(self, context):
        print ( "Printing CellBlender Data Model:" )
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context )
        dump_data_model ( "Data Model", {"mcell": mcell_dm} )
        return {'FINISHED'}


class ExportDataModel(bpy.types.Operator, ExportHelper):
    '''Export the CellBlender model as a Python Pickle in a text file'''
    bl_idname = "cb.export_data_model" 
    bl_label = "Export Data Model"
    bl_description = "Export CellBlender Data Model to a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        #print ( "Saving CellBlender model to file: " + self.filepath )
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=False )
        save_data_model_to_file ( mcell_dm, self.filepath )
        """
        dm = { 'mcell': mcell_dm }
        f = open ( self.filepath, 'w' )
        f.write ( pickle_data_model(dm) )
        f.close()
        """
        #print ( "Done saving CellBlender model." )
        return {'FINISHED'}


class ExportDataModelAll(bpy.types.Operator, ExportHelper):
    '''Export the CellBlender model including geometry as a Python Pickle in a text file'''
    bl_idname = "cb.export_data_model_all" 
    bl_label = "Export Data Model with Geometry"
    bl_description = "Export CellBlender Data Model and Geometry to a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        #print ( "Saving CellBlender model and geometry to file: " + self.filepath )
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        save_data_model_to_file ( mcell_dm, self.filepath )
        """
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        dm = { 'mcell': mcell_dm }
        f = open ( self.filepath, 'w' )
        f.write ( pickle_data_model(dm) )
        f.close()
        print ( "Done saving CellBlender model." )
        """
        return {'FINISHED'}


class ExportDataModelAllJSON(bpy.types.Operator, ExportHelper):
    '''Export the CellBlender model including geometry as a JSON text file'''
    bl_idname = "cb.export_data_model_all_json"
    bl_label = "Export Data Model with Geometry JSON"
    bl_description = "Export CellBlender Data Model and Geometry to a JSON text file"

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json",options={'HIDDEN'},)

    def execute(self, context):
        mcell_dm = context.scene.mcell.build_data_model_from_properties ( context, geometry=True )
        save_data_model_to_json_file ( mcell_dm, self.filepath )
        return {'FINISHED'}


class ImportDataModel(bpy.types.Operator, ExportHelper):
    '''Import a CellBlender model from a Python Pickle in a text file'''
    bl_idname = "cb.import_data_model" 
    bl_label = "Import Data Model"
    bl_description = "Import CellBlender Data Model from a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Loading CellBlender model from file: " + self.filepath + " ..." )
        f = open ( self.filepath, 'r' )
        pickle_string = f.read()
        f.close()

        dm = unpickle_data_model ( pickle_string )
        dm['mcell'] = cellblender.cellblender_main.MCellPropertyGroup.upgrade_data_model(dm['mcell'])
        context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'] )

        print ( "Done loading CellBlender model." )
        return {'FINISHED'}


class ImportDataModelAll(bpy.types.Operator, ExportHelper):
    '''Import a CellBlender model from a Python Pickle in a text file'''
    bl_idname = "cb.import_data_model_all" 
    bl_label = "Import Data Model with Geometry"
    bl_description = "Import CellBlender Data Model and Geometry from a Python Pickle in a file"

    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Loading CellBlender model from file: " + self.filepath + " ..." )
        f = open ( self.filepath, 'r' )
        pickle_string = f.read()
        f.close()

        dm = unpickle_data_model ( pickle_string )
        dm['mcell'] = cellblender.cellblender_main.MCellPropertyGroup.upgrade_data_model(dm['mcell'])
        context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'], geometry=True )

        print ( "Done loading CellBlender model." )
        return {'FINISHED'}

class ImportDataModelAllJSON(bpy.types.Operator, ExportHelper):
    '''Import a CellBlender model with geometry from a JSON text file'''
    bl_idname = "cb.import_data_model_all_json"
    bl_label = "Import Data Model with Geometry JSON"
    bl_description = "Import CellBlender Data Model and Geometry from a JSON text file"

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Loading CellBlender model from JSON file: " + self.filepath + " ..." )
        f = open ( self.filepath, 'r' )
        json_string = f.read()
        f.close()

        dm = {}
        dm['mcell'] = data_model_from_json ( json_string ) ['mcell']
        dm['mcell'] = cellblender.cellblender_main.MCellPropertyGroup.upgrade_data_model(dm['mcell'])
        context.scene.mcell.build_properties_from_data_model ( context, dm['mcell'], geometry=True )

        print ( "Done loading CellBlender model." )
        return {'FINISHED'}

def save_mcell_preferences ( mcell ):
    mp = {}
    mp['mcell_binary'] = mcell.cellblender_preferences.mcell_binary
    mp['mcell_binary_valid'] = mcell.cellblender_preferences.mcell_binary_valid
    mp['python_binary'] = mcell.cellblender_preferences.python_binary
    mp['python_binary_valid'] = mcell.cellblender_preferences.python_binary_valid
    mp['bionetgen_location'] = mcell.cellblender_preferences.bionetgen_location
    mp['bionetgen_location_valid'] = mcell.cellblender_preferences.bionetgen_location_valid
    return mp

def restore_mcell_preferences ( mp, mcell ):
    mcell.cellblender_preferences.mcell_binary = mp['mcell_binary']
    mcell.cellblender_preferences.mcell_binary_valid = mp['mcell_binary_valid']
    mcell.cellblender_preferences.python_binary = mp['python_binary']
    mcell.cellblender_preferences.python_binary_valid = mp['python_binary_valid']
    mcell.cellblender_preferences.bionetgen_location = mp['bionetgen_location']
    mcell.cellblender_preferences.bionetgen_location_valid = mp['bionetgen_location_valid']

import traceback

def upgrade_properties_from_data_model ( context ):
    print ( "Upgrading Properties from Data Model" )
    mcell = context.scene.mcell

    if 'data_model' in mcell:

        print ( "Found a data model to upgrade." )
        dm = cellblender.data_model.unpickle_data_model ( mcell['data_model'] )

        # Save any preferences that are stored in properties but not in the Data Model
        mp = save_mcell_preferences ( mcell )

        print ( "Delete MCell RNA properties" )
        del bpy.types.Scene.mcell
        if context.scene.get ( 'mcell' ):
          del context.scene['mcell']

        # Something like the following code would be needed if the
        #  internal data model handled the regions. But at this time
        #  the regions are handled and upgraded separately in:
        #           object_surface_regions.py
        #
        #del bpy.types.Object.mcell
        #for obj in context.scene.objects:
        #  if obj.get ( 'mcell' ):
        #    del obj['mcell']
        #    if obj.type == 'MESH':
        #      m = obj.data
        #      if m.get ( 'mcell' ):
        #        del m['mcell']
        #bpy.types.Object.mcell = bpy.props.PointerProperty(type=cellblender.object_surface_regions.MCellObjectPropertyGroup)

        print ( "Reinstate MCell RNA properties" )

        bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender.cellblender_main.MCellPropertyGroup)

        print ( "Reinstated MCell RNA properties" )

        # Restore the local variable mcell to be consistent with not taking this branch of the if.
        mcell = context.scene.mcell
        
        # Restore the current preferences that had been saved
        restore_mcell_preferences ( mp, mcell )

        # Do the actual updating of properties from data model right here
        dm = cellblender.cellblender_main.MCellPropertyGroup.upgrade_data_model(dm)
        mcell.build_properties_from_data_model ( context, dm )
    else:
        print ( "Warning: This should never happen." )
        traceback.print_stack()
        print ( "No data model to upgrade ... building a data model and then recreating properties." )
        dm = mcell.build_data_model_from_properties ( context )
        dm = cellblender.cellblender_main.MCellPropertyGroup.upgrade_data_model(dm)
        mcell.build_properties_from_data_model ( context, dm )

    # Update the source_id
    mcell['saved_by_source_id'] = cellblender.cellblender_info['cellblender_source_sha1']
    #mcell.versions_match = True
    cellblender.cellblender_info['versions_match'] = True
    print ( "Finished Upgrading Properties from Data Model" )


def upgrade_RC3_properties_from_data_model ( context ):
      print ( "Upgrading Properties from an RC3 File Data Model" )
      mcell = context.scene.mcell

      dm = None
      if 'data_model' in mcell:
          # This must be an RC4 file?
          print ( "Found a data model to upgrade." )
          dm = cellblender.data_model.unpickle_data_model ( mcell['data_model'] )
      else:
          print ( "No data model in RC3 file ... building a data model and then recreating properties." )
          dm = mcell.legacy.build_data_model_from_RC3_ID_properties ( context )

      # Save any preferences that are stored in properties but not in the Data Model
      mp = save_mcell_preferences ( mcell )

      print ( "Delete MCell RNA properties" )
      del bpy.types.Scene.mcell
      if context.scene.get ( 'mcell' ):
        del context.scene['mcell']

      # Something like the following code would be needed if the
      #  internal data model handled the regions. But at this time
      #  the regions are handled and upgraded separately in:
      #           object_surface_regions.py
      #
      #del bpy.types.Object.mcell
      #for obj in context.scene.objects:
      #  if obj.get ( 'mcell' ):
      #    del obj['mcell']
      #    if obj.type == 'MESH':
      #      m = obj.data
      #      if m.get ( 'mcell' ):
      #        del m['mcell']
      #bpy.types.Object.mcell = bpy.props.PointerProperty(type=cellblender.object_surface_regions.MCellObjectPropertyGroup)

      print ( "Reinstate MCell RNA properties" )

      bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender.cellblender_main.MCellPropertyGroup)

      print ( "Reinstated MCell RNA properties" )

      # Restore the local variable mcell
      mcell = context.scene.mcell

      # Restore the current preferences that had been saved
      restore_mcell_preferences ( mp, mcell )

      # Do the actual updating of properties from data model right here
      dm = cellblender.cellblender_main.MCellPropertyGroup.upgrade_data_model(dm)
      mcell.build_properties_from_data_model ( context, dm )

      # Update the source_id
      mcell['saved_by_source_id'] = cellblender.cellblender_info['cellblender_source_sha1']
      #mcell.versions_match = True
      cellblender.cellblender_info['versions_match'] = True
      print ( "Finished Upgrading Properties from RC3 Data Model" )



# Construct the data model property
@persistent
def save_pre(context):
    """Set the "saved_by_source_id" value and store a data model based on the current property settings in this application"""
    # The context appears to always be "None"
    print ( "========================================" )
    source_id = cellblender.cellblender_info['cellblender_source_sha1']
    print ( "save_pre() has been called ... source_id = " + source_id )
    if cellblender.cellblender_info['versions_match']:
        print ( "save_pre() called with versions matching ... save Data Model and Source ID" )
        if not context:
            # The context appears to always be "None", so use bpy.context
            context = bpy.context
        if hasattr ( context.scene, 'mcell' ):
            print ( "Updating source ID of mcell before saving" )
            mcell = context.scene.mcell
            mcell['saved_by_source_id'] = source_id
            dm = mcell.build_data_model_from_properties ( context )
            context.scene.mcell['data_model'] = pickle_data_model(dm)
    else:
        print ( "save_pre() called with versions not matching ... force an upgrade." )
        if not context:
            # The context appears to always be "None", so use bpy.context
            context = bpy.context
        if hasattr ( context.scene, 'mcell' ):
            mcell = context.scene.mcell
            # Only save the data model if mcell has been initialized
            if hasattr ( mcell, 'initialized' ):
                if mcell.initialized:
                    print ( "Upgrading blend file to current version before saving" )
                    mcell = context.scene.mcell
                    if not mcell.get ( 'saved_by_source_id' ):
                        # This .blend file was created with CellBlender RC3 / RC4
                        upgrade_RC3_properties_from_data_model ( context )
                    else:
                        upgrade_properties_from_data_model ( context )
                    mcell['saved_by_source_id'] = source_id
                    dm = mcell.build_data_model_from_properties ( context )
                    context.scene.mcell['data_model'] = pickle_data_model(dm)
    print ( "========================================" )


    """
    print ( "data_model.save_pre called" )

    if not context:
        context = bpy.context

    if 'mcell' in context.scene:
        dm = context.scene.mcell.build_data_model_from_properties ( context )
        context.scene.mcell['data_model'] = pickle_data_model(dm)

    return
    """


# Check for a data model in the properties
@persistent
def load_post(context):
    """Detect whether the loaded .blend file matches the current addon and set a flag to be used by other code"""

    print ( "load post handler: data_model.load_post() called" )

    # SELECT ONE OF THE FOLLOWING THREE:

    # To compute the ID on load, uncomment this choice and comment out the other three
    #cellblender_source_info.identify_source_version(addon_path,verbose=True)

    # To import the ID as python code, uncomment this choice and comment out the other three
    #from . import cellblender_id
    #cellblender.cellblender_info['cellblender_source_sha1'] = cellblender_id.cellblender_id

    # To read the ID from the file as text, uncomment this choice and comment out the other three
    #cs = open ( os.path.join(os.path.dirname(__file__), 'cellblender_id.py') ).read()
    #cellblender.cellblender_info['cellblender_source_sha1'] = cs[1+cs.find("'"):cs.rfind("'")]

    # To read the ID from the file as text via a shared call uncomment this choice and comment out the other three
    cellblender.cellblender_info['cellblender_source_sha1'] = cellblender.cellblender_source_info.identify_source_version_from_file()


    source_id = cellblender.cellblender_info['cellblender_source_sha1']
    print ( "cellblender source id = " + source_id )

    if not context:
        # The context appears to always be "None", so use bpy.context
        context = bpy.context

    api_version_in_blend_file = -1  # TODO May not be used

    #if 'mcell' in context.scene:
    if hasattr ( context.scene, 'mcell' ):
        mcell = context.scene.mcell

        # mcell.versions_match = False
        cellblender.cellblender_info['versions_match'] = False
        if 'saved_by_source_id' in mcell:
            saved_by_id = mcell['saved_by_source_id']
            print ( "load_post() opened a blend file with source_id = " + saved_by_id )
            if source_id == saved_by_id:
                #mcell.versions_match = True
                cellblender.cellblender_info['versions_match'] = True
            else:
                # Don't update the properties here. Just flag to display the "Upgrade" button for user to choose.
                #mcell.versions_match = False
                cellblender.cellblender_info['versions_match'] = False
    #print ( "End of load_post(): mcell.versions_match = " + str(mcell.versions_match) )
    print ( "End of load_post(): cellblender.cellblender_info['versions_match'] = " + str(cellblender.cellblender_info['versions_match']) )
    print ( "========================================" )


    """
    print ( "Delete MCell RNA properties" )
    del bpy.types.Scene.mcell
    if context.scene.get ( 'mcell' ):
      del context.scene['mcell']
    print ( "Reinstate MCell RNA properties" )
    bpy.types.Scene.mcell = bpy.props.PointerProperty(type=cellblender.cellblender_main.MCellPropertyGroup)
    print ( "Reinstated MCell RNA properties" )
    """

    #print ( "Unregister, delete all ID properties, and Reregister" )
    # Unregister, delete all ID properties, and Reregister
    #bpy.utils.unregister_module('cellblender')
    #print ( "Unregistered" )

    #bpy.utils.register_module('cellblender')
    #mcell = context.scene.mcell
    #print ( "Reregistered" )


def menu_func_import(self, context):
    self.layout.operator("cb.import_data_model", text="CellBlender Model (text/pickle)")

def menu_func_export(self, context):
    self.layout.operator("cb.export_data_model", text="CellBlender Model (text/pickle)")

def menu_func_import_all(self, context):
    self.layout.operator("cb.import_data_model_all", text="CellBlender Model and Geometry (text/pickle)")

def menu_func_export_all(self, context):
    self.layout.operator("cb.export_data_model_all", text="CellBlender Model and Geometry (text/pickle)")

def menu_func_import_all_json(self, context):
    self.layout.operator("cb.import_data_model_all_json", text="CellBlender Model and Geometry (JSON)")

def menu_func_export_all_json(self, context):
    self.layout.operator("cb.export_data_model_all_json", text="CellBlender Model and Geometry (JSON)")

def menu_func_print(self, context):
    self.layout.operator("cb.print_data_model", text="Print CellBlender Model (text)")



# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)
    #bpy.types.INFO_MT_file_export.append(menu_func_export_dm)

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_file_import.remove(menu_func_export_dm)


if __name__ == "__main__": 
    register()

