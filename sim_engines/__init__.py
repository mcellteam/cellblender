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



######################################################################################
#### This function has been duplicated in cellblender/mdl/run_data_model_mcell.py ####
#### This function was originally in the run_data_model_mcell_3.py file as well.  ####
######################################################################################
def build_sweep_list ( par_dict ):
    """ Count the number of runs that will be swept with this data model. """
    sweep_list = []
    print ( "Building sweep list... " )
    if 'model_parameters' in par_dict:
        for par in par_dict['model_parameters']:
            print ( "Checking par " + str(par) )
            if ('sweep_expression' in par) and ('sweep_enabled' in par):
                if par['sweep_enabled']:
                    sweep_item = {}
                    if 'par_name' in par:
                        sweep_item['par_name'] = par['par_name']
                    else:
                        sweep_item['par_name'] = "Unknown"
                    # Sweep expression example: "0, 2, 9, 10:20, 25:35:5, 50"
                    num_runs_for_this_parameter = 0
                    # Get the sweep expression sublists which are separated by commas
                    sw_items = []
                    if 'sweep_expression' in par:
                        sw_items = [ p.strip() for p in par['sweep_expression'].split(',') ]
                    #print ( "Sweep item list = " + str(sw_items) )
                    # Count the number of runs represented by each sweep item (either:  #  or  #:#  or  #:#:#  )
                    sweep_values = []
                    for sw_item in sw_items:
                        parts = [ p.strip() for p in sw_item.split(':') ]
                        if len(parts) <= 0:
                          # This would be two commas together?
                          pass
                        elif len(parts) == 1:
                          # This is a scalar
                          sweep_values.append ( float(parts[0]) )
                          #print ( "Added " + parts[0] )
                        elif len(parts) >= 2:
                          # This is a range with a start and stop
                          start = float(parts[0])
                          stop = float(parts[1])
                          step = 1
                          if len(parts) > 2:
                            step = float(parts[2])
                          if start > stop:
                            start = float(parts[1])
                            stop = float(parts[0])
                          if step < 0:
                            step = -step
                          if step == 0:
                            # Do something to keep it from an infinite loop
                            step = 1;
                          # Start with a pessimistic guess
                          num = int((stop-start) / step)
                          # Increase until equal or over
                          #print ( "Before increasing, num = " + str(num) )
                          while (start+((num-1)*step)) < (stop+(step/1000)):
                            num += 1
                            #print ( "Increased to num = " + str(num) )
                          # Reduce while actually over
                          while start+((num-1)*step) > (stop+(step/1000)):
                            num += -1
                            #print ( "Decreased to num = " + str(num) )
                          # Finally append the values
                          for n in range(num):
                            sweep_values.append ( start + (n*step) )
                    sweep_item['values'] = sweep_values
                    sweep_list.append ( sweep_item )
    return sweep_list


def count_sweep_runs ( sweep_list ):
    total_sweep_runs = 1
    for sweep_item in sweep_list:
      if 'values' in sweep_item:
        total_sweep_runs *= len(sweep_item['values'])
    return total_sweep_runs

def build_sweep_layout ( sweep_list, start_seed, end_seed ):
    sweep_layout = {}
    sweep_layout['version'] = 2;
    sweep_layout['data_layout'] = []
    sweep_layout['data_layout'].append ( [ '/DIR', [ 'output_data' ] ] )
    for sw_item in sweep_list:
      sweep_layout['data_layout'].append ( [ sw_item['par_name'], sw_item['values'] ] )
    sweep_layout['data_layout'].append ( [ '/FILE_TYPE', [ 'react_data', 'viz_data' ] ] )
    sweep_layout['data_layout'].append ( [ '/SEED', [s for s in range(start_seed,end_seed+1)] ] )
    return sweep_layout


def write_sweep_list_to_layout_file ( sweep_list, start_seed, end_seed, sweep_list_file_name ):
    # Save the sweep list to a file for plotting, visualization, and other processing
    # sweep_list_file_name = os.path.join ( project_dir, "data_layout.json" )
    sweep_list_file = open ( sweep_list_file_name, "w" )
    sweep_list_length = len(sweep_list)
    sweep_list_file.write ( "{\n" )
    sweep_list_file.write ( " \"version\": 2,\n" )
    sweep_list_file.write ( " \"data_layout\": [\n" )
    sweep_list_file.write ( "  [\"/DIR\", [\"output_data\"]],\n" )
    for i in range ( sweep_list_length ):
      sw_item = sweep_list[i]
      sweep_list_file.write ( "  [\"" + sw_item['par_name'] + "\", " + str(sw_item['values']) + "],\n" )
    # Include the file type
    sweep_list_file.write ( "  [\"/FILE_TYPE\", [\"react_data\", \"viz_data\"]],\n" )
    # Include the seeds in the sweep list file for plotting, etc.
    sweep_list_file.write ( "  [\"/SEED\", " + str([s for s in range(start_seed,end_seed+1)]) + "]\n" )
    sweep_list_file.write ( " ]\n" )
    sweep_list_file.write ( "}\n" )
    sweep_list_file.close()


def write_default_data_layout(project_dir, start, end):
    sweep_list_file_name = os.path.join ( project_dir, "data_layout.json" )
    sweep_list_file = open ( sweep_list_file_name, "w" )
    sweep_list_file.write ( "{\n" )
    sweep_list_file.write ( " \"version\": 2,\n" )
    sweep_list_file.write ( " \"data_layout\": [\n" )
    sweep_list_file.write ( "  [\"/DIR\", [\"output_data\"]],\n" )
    sweep_list_file.write ( "  [\"/FILE_TYPE\", [\"react_data\", \"viz_data\"]],\n" )
    sweep_list_file.write ( "  [\"/SEED\", " + str([s for s in range(start,end+1)]) + "]\n" )
    sweep_list_file.write ( " ]\n" )
    sweep_list_file.write ( "}\n" )
    sweep_list_file.close()

def makedirs_exist_ok ( path_to_build, exist_ok=False ):
    # Needed for old python which doesn't have the exist_ok option!!!
    print ( " Make dirs for " + path_to_build )
    parts = path_to_build.split(os.sep)  # Variable "parts" should be a list of subpath sections. The first will be empty ('') if it was absolute.
    full = ""
    if len(parts[0]) == 0:
      # This happens with an absolute PosixPath
      full = os.sep
    else:
      # This may be a Windows drive or the start of a non-absolute path
      if ":" in parts[0]:
        # Assume a Windows drive
        full = parts[0] + os.sep
      else:
        # This is a non-absolute path which will be handled naturally with full=""
        pass
    for p in parts:
      full = os.path.join(full,p)
      if not os.path.exists(full):
        os.makedirs ( full, exist_ok=True )

