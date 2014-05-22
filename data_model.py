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

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent

# python imports
import pickle

from bpy_extras.io_utils import ExportHelper
import cellblender


def code_api_version():
    return 1


data_model_depth = 0
def dump_data_model ( dm ):
    global data_model_depth
    data_model_depth += 1
    if type(dm) == type({'a':1}): # dm is a dictionary
        for k,v in dm.items():
            print ( str(data_model_depth*"  ") + "Key = " + str(k) )
            dump_data_model ( v )
    elif type(dm) == type(['a',1]): # dm is a list
        i = 0
        for v in dm:
            print ( str(data_model_depth*"  ") + "Entry["+str(i)+"]" )
            dump_data_model ( v )
            i += 1
    elif type(dm) == type("a1"): # dm is a string
        print ( str(data_model_depth*"  ") + "\"" + str(dm) + "\"" )
    else: # dm is anything else
        print ( str(data_model_depth*"  ") + str(dm) )
    data_model_depth += -1


def pickle_data_model ( dm ):
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

def unpickle_data_model ( dmp ):
    return ( pickle.loads ( dmp.encode('latin1') ) )



class ExportDataModel(bpy.types.Operator, ExportHelper):
    '''Export the CellBlender model as a Python Pickle in a text file'''
    bl_idname = "cb.export_data_model" 
    bl_label = "Export Data Model"
    bl_description = "Export CellBlender Data Model to a Python Pickle in a file"
 
    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Saving CellBlender model to file: " + self.filepath )
        dm = context.scene.mcell.build_data_model_from_properties ( context )
        f = open ( self.filepath, 'w' )
        f.write ( pickle_data_model(dm) )
        f.close()
        print ( "Done saving CellBlender model." )
        return {'FINISHED'}


class ImportDataModel(bpy.types.Operator, ExportHelper):
    '''Import a CellBlender model from a Python Pickle in a text file'''
    bl_idname = "cb.import_data_model" 
    bl_label = "Import Data Model"
    bl_description = "Import CellBlender Data Model from a Python Pickle in a file"
 
    filename_ext = ".txt"
    filter_glob = StringProperty(default="*.txt",options={'HIDDEN'},)

    def execute(self, context):
        print ( "Loading CellBlender model from file: " + self.filepath )
        f = open ( self.filepath, 'r' )
        pickle_string = f.read()
        f.close()

        dm = unpickle_data_model ( pickle_string )
        dump_data_model ( dm )
        context.scene.mcell.build_properties_from_data_model ( context, dm )

        print ( "Done loading CellBlender model." )
        return {'FINISHED'}



# Construct the data model property
@persistent
def save_pre(context):

    print ( "data_model.save_pre called" )

    if not context:
        context = bpy.context
    
    if 'mcell' in context.scene:
        dm = context.scene.mcell.build_data_model_from_properties ( context )
        print ( "=================== Begin Data Model ===================" )
        print ( str(dm) )
        print ( "================== Decoded Data Model ==================" )
        dump_data_model ( dm )
        print ( "=================== End Data Model ===================" )
        #self['data_model'] = dm
        context.scene.mcell['data_model'] = pickle_data_model(dm)
    
    return


# Check for a data model in the properties
@persistent
def load_post(context):

    print ( "data_model.load_post called" )

    if not context:
        context = bpy.context

    api_version = -1
    if 'mcell' in context.scene:
        mcell = context.scene['mcell']
        if 'api_version' in mcell:
            api_version = mcell['api_version']

        print ( "Code API = " + str(code_api_version()) + ", File API = " + str(api_version) )
        
        if (api_version <= 0):
            # There is no data model so build it from the properties

            dm = context.scene.mcell.build_data_model_from_properties ( context )
            print ( "=================== Begin Data Model ===================" )
            print ( str(dm) )
            print ( "================== Decoded Data Model ==================" )
            dump_data_model ( dm )
            print ( "=================== End Data Model ===================" )
            #context.scene.mcell['data_model'] = dm
            context.scene.mcell['data_model'] = pickle_data_model(dm)
        
        elif (api_version != code_api_version()):
            # There is a data model in the file so convert it to match current properties

            dm = unpickle_data_model ( context.scene.mcell['data_model'] )
        
            context.scene.mcell.build_properties_from_data_model ( context, dm )
            
            context.scene['mcell']['api_version'] = code_api_version()
    else:
        print ( "context.scene does not have an 'mcell' key ... no data model to import" )

    return


def menu_func_import(self, context):
    print ( "=== Called menu_func_import ===" )
    self.layout.operator("cb.import_data_model", text="Import CellBlender Model (pickle.txt)")

def menu_func_export(self, context):
    print ( "=== Called menu_func_export ===" )
    self.layout.operator("cb.export_data_model", text="Export CellBlender Model (pickle.txt)")


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)
    #print ( "=== Appending menu_func_export ===" )
    #bpy.types.INFO_MT_file_export.append(menu_func_export_dm)

def unregister():
    bpy.utils.unregister_module(__name__)
    #bpy.types.INFO_MT_file_import.remove(menu_func_export_dm)


if __name__ == "__main__": 
    register()

