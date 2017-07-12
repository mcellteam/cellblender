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
  'Show Normal Output': {'val':True, 'desc':"Show stdout from process"},
  'Show Error Output':  {'val':True, 'desc':"Show stderr from process"},
}

parameter_layout = [
  ['Show Normal Output', 'Show Error Output']
]


def run_commands ( commands ):
    sp_list = []
    window_num = 0
    for cmd in commands:
        command_list = [ cmd['cmd'] ]
        for arg in cmd['args']:
            command_list.append ( arg )
        sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=None, stderr=None ) )
        window_num += 1


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
                    command_list.append ( arg )
            if 'wd' in cmd:
                sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=None, stderr=None ) )
            else:
                sp_list.append ( subprocess.Popen ( command_list, stdout=None, stderr=None ) )
        window_num += 1
    return sp_list

