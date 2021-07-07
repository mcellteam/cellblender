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
This file contains the classes for CellBlender's Partitioning System.
"""

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

#Property class for the PBC
class MCellPBCPropertyGroup(bpy.types.PropertyGroup):
    #Include PBC boolean
    include: BoolProperty(name="Include PBC", default=False ,
    	description="Enable to define a domain having Periodic Boundaries")
    #Periodic Traditional variable
    peri_trad: BoolProperty(name="Periodic Traditional", default=True)
    #Periodic X variable
    peri_x: BoolProperty(name="Periodic X", default=True)
    #Periodic Y variable
    peri_y: BoolProperty(name="Periodic Y", default=True)
    #Periodic Z variable
    peri_z: BoolProperty(name="Periodic Z", default=True)
    #Start variable for the X coordinate
    x_start: FloatProperty(name="X Start", default=0, precision=3,
        description="The start of the Periodic boundary on the x-axis")
    #Start variable for the Y coordinate
    y_start: FloatProperty(name="Y Start", default=0, precision=3,
        description="The start of the Periodic boundary on the y-axis")
    #Start variable for the Z coordinate
    z_start: FloatProperty(name="Z Start", default=0, precision=3,
        description="The start of the Periodic boundary on the z-axis")
    #End variable for the X coordinate
    x_end: FloatProperty(name="X End", default=0, precision=3,
        description="The end of the Periodic boundary on the x-axis")
    #End variable for the Y coordinate
    y_end: FloatProperty(name="Y End", default=0, precision=3,
        description="The end of the Periodic boundary on the y-axis")
    #End variable for the Z coordinate
    z_end: FloatProperty(name="Z End", default=0, precision=3,
        description="The end of the Periodic boundary on the z-axis")
    #Function to draw the panel
    def draw_layout(self, context, layout):
        mcell4_mode = context.scene.mcell.cellblender_preferences.mcell4_mode
        if mcell4_mode:
            layout.label(text="Periodic Boundary Conditions are not supported in MCell4.")
        else:
            #Making the include option
            layout.prop(self, "include")
        
        #If the include checkbox is checked
        if self.include and not mcell4_mode:
            #The start coordinates
            row = layout.row(align=True)
            row.prop(self, "x_start")
            row.prop(self, "y_start")
            row.prop(self, "z_start")
            #The end coordinates
            row = layout.row(align=True)
            row.prop(self, "x_end")
            row.prop(self, "y_end")
            row.prop(self, "z_end")
            #Boolean variables
            row = layout.row(align=True)
            layout.label(text="Defaulted to True, uncheck the boxes to set them to false.")

            row = layout.row(align=True)
            #Periodic Traditional variable
            row.prop(self, "peri_trad")
            #Periodic X variable
            row.prop(self, "peri_x")

            row = layout.row(align=True)
            #Periodic Y variable
            row.prop(self, "peri_y")
            #Periodic Z variable
            row.prop(self, "peri_z")

    def build_data_model_from_properties ( self, context ):
        print ( "Periodic Boundary Conditions building Data Model" )
        dm_dict = {}
        dm_dict['data_model_version'] = "DM_2020_02_21_1900"
        dm_dict['include'] = self.include==True
        dm_dict['periodic_traditional'] = self.peri_trad==True
        dm_dict['peri_x'] = self.peri_x==True
        dm_dict['peri_y'] = self.peri_y==True
        dm_dict['peri_z'] = self.peri_z==True
        dm_dict['x_start'] = "%g" % (self.x_start)
        dm_dict['x_end'] =   "%g" % (self.x_end)
        dm_dict['y_start'] = "%g" % (self.y_start)
        dm_dict['y_end'] =   "%g" % (self.y_end)
        dm_dict['z_start'] = "%g" % (self.z_start)
        dm_dict['z_end'] =   "%g" % (self.z_end)
        return dm_dict

    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellPBCPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['data_model_version'] = "DM_2020_02_21_1900"

        if dm['data_model_version'] != "DM_2020_02_21_1900":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellPBCPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2020_02_21_1900":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellPBCPropertyGroup data model to current version." )

        self.include = dm['include']
        self.peri_trad = dm['periodic_traditional']
        self.peri_x  = dm['peri_x']
        self.peri_y  = dm['peri_y']
        self.peri_z  = dm['peri_z']
        self.x_start = float(dm['x_start'])
        self.x_end   = float(dm['x_end'])
        self.y_start = float(dm['y_start'])
        self.y_end   = float(dm['y_end'])
        self.z_start = float(dm['z_start'])
        self.z_end   = float(dm['z_end'])


    #Function that contains the previous function
    def draw_panel ( self, context, panel ):
            # Create a layout from the panel and draw into it
            layout = panel.layout
            self.draw_layout ( context, layout )


classes = ( 
            MCellPBCPropertyGroup,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)


