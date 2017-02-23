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


def reset():
    print ( "Resetting" )

def info():
    print ( "Print Command Line Information" )

parameter_dictionary = {
  'Command Line Path': {'val': "", 'as':'filename', 'desc':"Optional Path", 'icon':'SCRIPTWIN'},
  'Print Command Line Info': {'val': info, 'desc':"Print information"},
  'Reset': {'val': reset, 'desc':"Reset everything"}
}

parameter_layout = [
  ['Command Line Path'],
  ['Print Command Line Info', 'Reset']
]


def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def run_commands ( commands ):
    sp_list = []
    window_num = 0
    for cmd in commands:
        command_list = [ cmd['cmd'] ]
        for arg in cmd['args']:
            command_list.append ( arg )
        sp_list.append ( subprocess.Popen ( command_list, cwd=cmd['wd'], stdout=None, stderr=None ) )
        window_num += 1
    return sp_list


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
