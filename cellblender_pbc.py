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
    include = BoolProperty(name="Include PBC", default=False ,
    	description="PBC is used to define an area that you wish to use" "properly.")
    #Periodic Traditional variable
    peri_trad = BoolProperty(name="Periodic Traditional", default=True)
    #Periodic X variable
    peri_x = BoolProperty(name="Periodic X", default=True)
    #Periodic Y variable
    peri_y = BoolProperty(name="Periodic Y", default=True)
    #Periodic Z variable
    peri_z = BoolProperty(name="Periodic Z", default=True)
    #Start variable for the X coordinate
    x_start = bpy.props.FloatProperty(name="X Start", default=0, precision=3,
        description="The start of the Periodic boundary on the x-axis")
    #Start variable for the Y coordinate
    y_start = bpy.props.FloatProperty(name="Y Start", default=0, precision=3,
        description="The start of the Periodic boundary on the y-axis")
    #Start variable for the Z coordinate
    z_start = bpy.props.FloatProperty(name="Z Start", default=0, precision=3,
        description="The start of the Periodic boundary on the z-axis")
    #End variable for the X coordinate
    x_end = bpy.props.FloatProperty(name="X End", default=0, precision=3,
        description="The end of the Periodic boundary on the x-axis")
    #End variable for the Y coordinate
    y_end = bpy.props.FloatProperty(name="Y End", default=0, precision=3,
        description="The end of the Periodic boundary on the y-axis")
    #End variable for the Z coordinate
    z_end = bpy.props.FloatProperty(name="Z End", default=0, precision=3,
        description="The end of the Periodic boundary on the z-axis")
    #Function to draw the panel
    def draw_layout(self, context, layout):
           #mcell = context.scene.mcell
           #if not mcell.initialized:
           #mcell.draw_uninitialized ( layout )
           # else:
                #Making the include option
                layout.prop(self, "include")
                #If the include checkbox is checked
                if self.include:
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
                    layout.label("Defaulted to True, uncheck the boxes to set them to false.")
                    
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

    #Function that contains the previous function
    def draw_panel ( self, context, panel ):
            # Create a layout from the panel and draw into it 
            layout = panel.layout
            self.draw_layout ( context, layout )

"""
Make the button
Have the button be able to be selected
Have an enabled or not checkbox
Have an input for the starting X,Y,Z
Have an input for the ending X,Y,Z
Have a checkbox for Periodic Traditional
Have a checkbox for Periodic-X
Have a checkbox for Periodic-Y
Have a checkbox for Periodic-Z
create a script from input and export it

VVVV
PERIODIC_BOX
{
  CORNERS = [x_start, y_start, z_start],[x_end, y_end, z_end]
  PERIODIC_TRADITIONAL = peri_trad--defaulted to True
  PERIODIC_X = peri_x--defaulted to True
  PERIODIC_Y = peri_y--defaulted to True
  PERIODIC_Z = peri_z--defaulted to True
}
^^^^^^
"""

"""
clicks the button
brings up below checkbox, must draw the checkbox, 
"""
"""
scripting

button that turns the input into a python script called pbc.mdl
enable python script through black magic then add it the enabled list 

"""