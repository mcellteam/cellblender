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

# Each Simulation Engine provides:
#
#   optional engine_user_parameters - dictionary to be displayed as parameters
#   optional draw_blender_panel - optional function to draw a Blender panel

import os
import subprocess
import sys

# Name of this engine to display in the list of choices
engine_name = "MCell"

# List of parameters dictionaries - each with keys for 'name', 'desc', 'def':
engine_user_parameters = [
  { 'name':"Log File Name", 'desc':"File name for logging (blank for no logging)", 'def':"" },
  { 'name':"Log Frequency", 'desc':"How often to log (default is 100)", 'def':100 },
  { 'name':"With Checks", 'desc':"Perform a geometry check for coincident walls", 'def':["yes", "no"] },
  { 'name':"Quiet", 'desc':"Suppress all unrequested output except for errors", 'def':False }
]


def prepare_runs ( data_model ) {
  # Return a list of run command strings
}


def postprocess_runs ( data_model, command_strings ) {
  # Move and/or transform data to match expected CellBlender file structure
}


def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
