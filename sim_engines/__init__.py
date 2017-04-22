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

# import cellblender

plug_modules = None  # This is currently set by "cellblender_simulation.load_plug_modules"

def get_modules():

    module_name_list = []
    module_list = []

    parent_path = os.path.dirname(__file__)

    if parent_path == '':
        parent_path = '.'

    inpath = True
    try:
        if sys.path.index(parent_path) < 0:
            inpath = False
    except:
        inpath = False
    if not inpath:
        sys.path.append ( parent_path )


    # print ( "System path = %s" % (sys.path) ) 
    module_name_list = []
    module_list = []

    print ( "Searching for installed plugins in " + parent_path )

    for f in os.listdir(parent_path):
        if (f != "__pycache__"):
            plugin = os.path.join ( parent_path, f )
            if os.path.isdir(plugin):
                if os.path.exists(os.path.join(plugin,"__init__.py")):
                    print ( "Adding %s " % (plugin) )
                    import_name = plugin
                    module_name_list = module_name_list + [f]
                    print ( "Attempting to import %s" % (import_name) )
                    plugin_module = __import__ ( f )
                    # plugin_module = import f
                    # print ( "Checking requirements for %s" % ( plugin_module.get_name() ) )
                    #if plugin_module.requirements_met():
                    # print ( "System requirements met for Plot Module \"%s\"" % ( plugin_module.get_name() ) )
                    module_list = module_list + [ plugin_module ]
                    #else:
                    #    print ( "System requirements NOT met for Plot Module \"%s\"" % ( plugin_module.get_name() ) )
                    # print ( "Imported __init__.py from %s" % (f) )
    return ( module_list )


