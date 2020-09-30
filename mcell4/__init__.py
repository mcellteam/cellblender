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

"""
This file contains functions for MCell4 simulation.

"""
import os
import subprocess

# returns empty string of conversion passed, error message if conversion failed
def convert_data_model_to_python(mcell_binary, dm_file, sweep_item_path, base_name):
    
    mcell_dir = os.path.dirname(mcell_binary)
    exe_ext = os.path.splitext(mcell_binary)[1] 
    converter = os.path.join(mcell_dir, 'utils', 'data_model_to_pymcell', 'data_model_to_pymcell' + exe_ext) 
    
    res = subprocess.run(
        [converter, dm_file, '-o', base_name], 
        cwd=sweep_item_path,
        stderr=subprocess.PIPE
    )
    
    if res.returncode != 0:
        return res.stderr.decode('ascii')
    else:
        return '' 
    
    