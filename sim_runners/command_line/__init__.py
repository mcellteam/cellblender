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

plug_code = "CMDLINE"
plug_name = "Command Line"


parameter_dictionary = {
  'Print Commands': {'val':False, 'desc':"Print the commands to be executed"},
}

def run_commands ( commands ):

    if parameter_dictionary['Print Commands']['val']:
        print ( "Commands for " + plug_name + " runner:" )
        for cmd in commands:
            print ( "  " + str(cmd) )

    sp_list = []
    for cmd in commands:
        if parameter_dictionary['Print Commands']['val']:
            print ( "cmd = \"" + str(cmd) + "\"" )
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
                    if False and (' ' in arg):
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

