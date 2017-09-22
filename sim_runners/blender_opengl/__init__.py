# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
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

import os
import subprocess
import sys

import bpy
import bgl
import blf


plug_code = "BLEND_OGL"
plug_name = "Blender OpenGL"


handler_list = []

def draw_callback_px(context):
    global stroke_list
    global x
    global y
    global zoom

    bgl.glPushAttrib(bgl.GL_ENABLE_BIT)

    font_id = 0  # XXX, need to find out how best to get this.

    # draw some text
    blf.position(font_id, 15, 30, 0)
    blf.size(font_id, 20, 72)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.5)
    text = "Blender OpenGL Runner"
    blf.draw(font_id, text)

    # 100% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)

    bgl.glPopAttrib()

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def get_3d_areas():
  areas = []
  if len(bpy.data.window_managers) > 0:
    if len(bpy.data.window_managers[0].windows) > 0:
      if len(bpy.data.window_managers[0].windows[0].screen.areas) > 0:
        if len(handler_list) <= 0:
          for area in bpy.data.window_managers[0].windows[0].screen.areas:
            print ( "Found an area of type " + str(area.type) )
            if area.type == 'VIEW_3D':
              areas.append ( area )
  return ( areas )

def enable():
  global parameter_dictionary
  global handler_list
  # self.report({'WARNING'}, "View3D not found, cannot run operator")
  areas = get_3d_areas()
  for area in areas:
    # context.area = area
    temp_context = bpy.context.copy()
    temp_context['area'] = area
    args = (temp_context,)
    handler_list.append ( bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL') )
    bpy.context.area.tag_redraw()
  print ( "Enable completed" )

def disable():
  global parameter_dictionary
  global handler_list
  while len(handler_list) > 0:
    print ( "Removing draw_handler " + str(handler_list[-1]) )
    bpy.types.SpaceView3D.draw_handler_remove(handler_list[-1], 'WINDOW')
    handler_list.pop()
  bpy.context.area.tag_redraw()
  print ( "Disable completed" )



parameter_dictionary = {
  'Enable': {'val': enable, 'desc':"Enable the display overlay"},
  'Disable': {'val': disable, 'desc':"Disable the display overlay"},
  'Print Commands': {'val':False, 'desc':"Print the commands to be executed"},
}

parameter_layout = [
  ['Enable', 'Disable'],
  ['Print Commands']
]

def run_commands ( commands ):

    if parameter_dictionary['Print Commands']['val']:
        print ( "Commands for " + plug_name + " runner:" )
        for cmd in commands:
            print ( "  " + str(cmd) )

    sp_list = []
    for cmd in commands:
        command_list = []
        if type(cmd) == type('str'):
            # This command is a string, so just append it
            command_list.append ( cmd )
            sp_list.append ( subprocess.Popen ( command_list, stdout=None, stderr=None ) )
        elif type(cmd) == type({'a':1}):
            # This command is a dictionary, so use its keys:
            command_list.append ( cmd['cmd'] )  # The dictionary must contain a 'cmd' key
            if 'args' in cmd:
                for arg in cmd['args']:
                    # For some reason, the ' ' in the args may be creating a problem for "-seed 1"
                    # This isn't a problem in the Java or OpenGL runners, but it is here.
                    # So ... check for spaces and split into additional arguments
                    if ' ' in arg:
                      for s in arg.split(' '):
                        command_list.append ( s )
                    else:
                      command_list.append ( arg )
            if parameter_dictionary['Print Commands']['val']:
                print ( "Popen with: " + str(command_list) )
            if 'wd' in cmd:
                sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=None, stderr=None ) )
            else:
                sp_list.append ( subprocess.Popen ( command_list, stdout=None, stderr=None ) )

    return sp_list

def draw_layout ( self, context, layout ):
    #mcell = context.scene.mcell
    row = layout.row()
    row.label ( "draw_layout" )
    #row.operator("ql.clear_run_list")
    #row = layout.row()
    #row.operator("ql.kill_simulation")
    #row.operator("ql.kill_all_simulations")

