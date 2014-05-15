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
This file contains the classes defining and handling the CellBlender data model.

"""

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent

# python imports
import pickle

import cellblender


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def code_api_version():
    return 1


def build_data_model_from_properties ( context ):
    print ( "Constructing a data_model dictionary and storing in an ID property" )


def build_properties_from_data_model ( context ):
    print ( "Overwriting properites based on data in the data model" )


# Construct the data model property
@persistent
def save_pre(context):

    print ( "data_model.save_pre called" )

    if not context:
        context = bpy.context
    
    build_data_model_from_properties ( context )
    
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
    
    if (api_version <= 0) or (api_version != code_api_version()):
    
        build_properties_from_data_model ( context )
        
        context.scene['mcell']['api_version'] = code_api_version()

    return



