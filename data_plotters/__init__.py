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


def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def print_plotting_options():
    plot_executables = ['python', 'xmgrace', 'java', 'excel']
    plot_modules = ['matplotlib', 'junktestlib', 'matplotlib.pyplot', 'pylab', 'numpy', 'scipy']

    for plot_app in plot_executables:
        path = find_in_path ( plot_app )
        if path != None:
            print ( "  ", plot_app, "is available at", path )
        else:
            print ( "  ", plot_app, "is not found in the current path" )

    for plot_mod in plot_modules:
        try:
            __import__ ( plot_mod )
            print ( "  ", plot_mod, "is importable" )
        except:
            print ( "  ", plot_mod, "is not importable in this configuration" )

    python_command = find_in_path ( "python" )

    for plot_mod in plot_modules:
        import_test_program = 'import %s\nprint("Found=OK")'%(plot_mod)
        #print ( "Test Program:" )
        #print ( import_test_program )
        process = subprocess.Popen([python_command, '-c', import_test_program],
            shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print ( "Back from Popen" )
        process.poll()
        #print ( "Back from poll" )
        output = process.stdout.readline()
        #print ( "Back from readline" )
        #print ( "  output =", output )
        strout = str(output)
        if (strout != None) & (strout.find("Found=OK")>=0):
            print ( "  ", plot_mod, "is available through external python interpreter" )
        else:
            print ( "  ", plot_mod, "is not available through external python interpreter" )

print ( "=== Searching for known plotting plugins ===" )

try:
    # Trap exceptions in case this test code fails for some reason
    print_plotting_options()
except:
    print ( "Exception in print_plotting_options()" )
    pass


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    # register()
    pass
