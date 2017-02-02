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

plug_code = "OPENGL"
plug_name = "OpenGL Control"

runner_user_parameters = [
  { 'name':"Start Seed", 'desc':"First seed number for simulations that use seeds", 'def':1 },
  { 'name':"End Seed", 'desc':"Last seed number for simulations that use seeds", 'def':1 },
]

def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def run_commands ( commands, cwd="" ):
    sp_list = []
    window_num = 0
    for cmd in commands:
        command_list = [ os.path.join(os.path.dirname(os.path.realpath(__file__)),"SimControl") ]
        command_list.append ( "x=%d" % ((50*(1+window_num))%500) ),
        command_list.append ( "y=%d" % ((40*(1+window_num))%400) ),
        command_list.append ( ":" ),
        for subcmd in cmd:
            command_list.append ( subcmd )
        sp_list.append ( subprocess.Popen ( command_list, cwd=cwd, stdout=None, stderr=None ) )
        window_num += 1
    return sp_list


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
