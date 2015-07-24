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

This program queries git to generate a list of dictionaries of:

  GIT_ID - The GIT commit hash
  CB_ID  - The CellBlender ID
  Date   - The date of the commit

This is handy for generating code that can match a CellBlender ID
with a Git commit when GIT may not be available.

If git is available, the GIT commit can be found with:

  git log -S'461aacb3b54c3ded80c45140dddabd9e28f88f98' -- cellblender_id.py

Note that the CellBlender ID is only correct if "make" was run prior to committing.
If make was not run between commits, then the same CBID may appear in multiple commits.

"""


import os
import subprocess

def find_in_path(program_name):
  for path in os.environ.get('PATH','').split(os.pathsep):
    full_name = os.path.join(path,program_name)
    if os.path.exists(full_name) and not os.path.isdir(full_name):
      return full_name
  return None

def run_command ( cmd ):
  result_lines = []
  pid = subprocess.Popen ( cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE )
  while True:
    line = (pid.stdout.readline()).strip()
    if len(line) > 0:
      result_lines.append ( line )
    else:
      break
  return result_lines
  

git_cmd = find_in_path("git")
# print ( "Found git at " + git_cmd )

# Start by getting all the commits of cellblender_id.py in the GIT repository

cmd = git_cmd + " log --date-order --pretty=format:%H__%ci -- cellblender_id.py"
git_id_date_strings = run_command ( cmd )

# Create a git_info list containing the GIT ID as the first entry
git_info = []
for s in git_id_date_strings:
  id_date = s.split('__')
  git_info.append ( id_date )
  
# Use "git show commit:cellblender_id.py" to get the CellBlenderID for that commit

for git_entry in git_info:

  # print ( " GIT ID = " + git_entry[0] + ", committed on " + git_entry[1] )
  cmd = git_cmd + ' show ' + git_entry[0] + ':cellblender_id.py'
  cb_ids = run_command ( cmd )
  for cb_id in cb_ids:
    if 'cellblender_id' in cb_id:
      parts = cb_id.strip().split("'")
      # print ( "parts = " + str(parts) )
      if len(parts) > 1:
        git_entry.append ( parts[1] )


print ( "git_cb_db = [" )
for git_entry in git_info:
  print ( " {" )
  if len(git_entry) > 0:
    print ( "   'GIT_ID': '" + git_entry[0] + "'," )
  if len(git_entry) > 2:
    print ( "   'CB_ID': '" + git_entry[2] + "'," )
  if len(git_entry) > 1:
    print ( "   'Date': '" + git_entry[1] + "'" )
  print ( " }," )
print ( "]" )


