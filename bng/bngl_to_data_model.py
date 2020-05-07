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

"""
This stand-alone Python program reads from a BNGL file
and attempts to generate a corresponding CellBlender Data Model.

"""


import pickle
import sys
import json
import os
import re
import math

#### DataModel class ####
class DataModel:
    def __init__(self):
        # Define special parameters that appear to be MCell Specific
        self.special_parameters = { 'MCELL_ITERATIONS': 1000, 'MCELL_TIME_STEP': 1e-6, 'MCELL_VACANCY_SEARCH_DISTANCE': 10 }
        # populate defaults 
        dm = { 'mcell': { 'api_version': 0, 'blender_version': [2,78,0], 'data_model_version': "DM_2017_06_23_1300" } }
        dm['mcell']['cellblender_source_sha1'] = "61cc8da7bfe09b42114982616ce284301adad4cc"
        dm['mcell']['cellblender_version'] = "0.1.54"
        dm['mcell']['model_language'] = "mcell3r"
        # Force a reflective surface class
        dm['mcell']['define_surface_classes'] = {
          'data_model_version' : "DM_2014_10_24_1638",
          'surface_class_list' : [
            {
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'name' : "reflect",
              'surface_class_prop_list' : [
                {
                  'affected_mols' : "ALL_MOLECULES",
                  'clamp_value' : "0",
                  'data_model_version' : "DM_2015_11_08_1756",
                  'molecule' : "",
                  'name' : "Molec.: ALL_MOLECULES   Orient.: Ignore   Type: Reflective",
                  'surf_class_orient' : ";",
                  'surf_class_type' : "REFLECTIVE"
                }
              ]
            }
          ]
        }
        # Add a default object material (may be augmented later)
        dm['mcell']['materials'] = {
          'material_dict' : {
            'membrane_mat' : {
              'diffuse_color' : {
                'a' : 0.1,
                'b' : 0.43,
                'g' : 0.43,
                'r' : 0.43
              }
            }
          }
        }
        dm['mcell']['geometrical_objects'] = {
          'object_list' : []
        }
        dm['mcell']['model_objects'] = {
          'data_model_version' : "DM_2018_01_11_1330",
          'model_object_list' : []
        }
        # initialization
        dm['mcell']['initialization'] = {
          'accurate_3d_reactions' : True,
          'center_molecules_on_grid' : False,
          'data_model_version' : "DM_2017_11_18_0130",
          'export_all_ascii' : False,
          'interaction_radius' : "",
          'iterations' : "1000",
          'microscopic_reversibility' : "OFF",
          'notifications' : {
            'all_notifications' : "INDIVIDUAL",
            'box_triangulation_report' : False,
            'diffusion_constant_report' : "BRIEF",
            'file_output_report' : False,
            'final_summary' : True,
            'iteration_report' : True,
            'molecule_collision_report' : False,
            'partition_location_report' : False,
            'probability_report' : "ON",
            'probability_report_threshold' : "0",
            'progress_report' : True,
            'release_event_report' : True,
            'varying_probability_report' : True
          },
          'partitions' : {
            'data_model_version' : "DM_2016_04_15_1600",
            'include' : False,
            'recursion_flag' : False,
            'x_end' : "1",
            'x_start' : "-1",
            'x_step' : "0.02",
            'y_end' : "1",
            'y_start' : "-1",
            'y_step' : "0.02",
            'z_end' : "1",
            'z_start' : "-1",
            'z_step' : "0.02"
          },
          'radial_directions' : "",
          'radial_subdivisions' : "",
          'space_step' : "",
          'surface_grid_density' : "10000",
          'time_step' : "1e-6",
          'time_step_max' : "",
          'vacancy_search_distance' : "",
          'warnings' : {
            'all_warnings' : "INDIVIDUAL",
            'degenerate_polygons' : "WARNING",
            'high_probability_threshold' : "1",
            'high_reaction_probability' : "IGNORED",
            'large_molecular_displacement' : "WARNING",
            'lifetime_threshold' : "50",
            'lifetime_too_short' : "WARNING",
            'missed_reaction_threshold' : "0.001",
            'missed_reactions' : "WARNING",
            'missing_surface_orientation' : "ERROR",
            'negative_diffusion_constant' : "WARNING",
            'negative_reaction_rate' : "WARNING",
            'useless_volume_orientation' : "WARNING"
          }
        }
        self.dm = dm

    def handle_special_params(self):
        for sp, spv in self.special_parameters.items():
            if sp == "MCELL_ITERATIONS":
                self.dm['mcell']['initialization']['iterations'] = spv
            elif sp == "MCELL_TIME_STEP":
                self.dm['mcell']['initialization']['time_step'] = spv
            elif sp == "MCELL_VACANCY_SEARCH_DISTANCE":
                self.dm['mcell']['initialization']['vacancy_search_distance'] = spv
            elif "MCELL_REDEFINE_" in sp:
                # this is a MCELL_REDEFINE 
                param_name = sp.replace("MCELL_REDEFINE_","")
                ps = self.dm['mcell']['parameter_system']['model_parameters']
                # this _only_ changes the parameter
                # if it exists in the set of parameters
                # we already have
                for pdict in ps:
                    if pdict['par_name'] == param_name:
                        pdict['par_expression'] = spv
                        print("redefined parameter: {} to {}".format(param_name, spv))
            else:
                print("Not handled special parameter")
                print(sp, spv)

    def add_parameters(self, par_list):
        self.dm['mcell']['parameter_system'] = { 'model_parameters': par_list }

    def add_materials(self):
        # Change the materials to add a new one for each object
        mat_name_number = 1
        for obj in self.dm['mcell']['geometrical_objects']['object_list']:
          if len(obj['material_names']) > 0:
            if obj['material_names'][0] == 'membrane_mat':
              # Make a new material to replace the defaulted "membrane_mat"
              mat_name = obj['name'] + '_mat_' + str(mat_name_number)
              self.dm['mcell']['materials']['material_dict'][mat_name] = { 'diffuse_color' : { 'a':0.1, 'r':mat_name_number&1, 'g':mat_name_number&2, 'b':mat_name_number&4 } }
              obj['material_names'][0] = mat_name
              mat_name_number += 1

    def mod_surface_regions(self):
        # Make a "Modify Surface Regions" "ALL" entry for every object
        self.dm['mcell']['modify_surface_regions'] = {
          'data_model_version' : "DM_2014_10_24_1638",
          'modify_surface_regions_list' : []
        }

        # Make a "Modify Surface Regions" entry for every named surface in an object
        for obj in self.dm['mcell']['geometrical_objects']['object_list']:
          msr = {
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'name' : "Surface Class: reflect   Object: " + obj['name'] + "   ALL",
              'object_name' : obj['name'],
              'region_name' : "",
              'region_selection' : "ALL",
              'surf_class_name' : "reflect"
            }
          self.dm['mcell']['modify_surface_regions']['modify_surface_regions_list'].append ( msr )

          if 'define_surface_regions' in obj:
            for surf in obj['define_surface_regions']:
              msr = {
                  'data_model_version' : "DM_2018_01_11_1330",
                  'description' : "",
                  'name' : "Surface Class: reflect   Object: " + obj['name'] + "   Region: " + surf['name'],
                  'object_name' : obj['name'],
                  'region_name' : surf['name'],
                  'region_selection' : "SEL",
                  'surf_class_name' : "reflect"
                }
              self.dm['mcell']['modify_surface_regions']['modify_surface_regions_list'].append ( msr )

    def add_release_sites(self, rel_list):
        self.dm['mcell']['release_sites'] = { 'data_model_version' : "DM_2014_10_24_1638" }
        self.dm['mcell']['release_sites']['release_site_list'] = rel_list

    def add_molecules(self, mol_list):
        self.dm['mcell']['define_molecules'] = { 'molecule_list': mol_list, 'data_model_version': "DM_2014_10_24_1638" }

    def init_observables(self):
        # observables
        self.dm['mcell']['viz_output'] = {
          'all_iterations' : True,
          'data_model_version' : "DM_2014_10_24_1638",
          'end' : "1000",
          'export_all' : True,
          'start' : "0",
          'step' : "5"
        }
        self.dm['mcell']['reaction_data_output'] = {
          'always_generate' : True,
          'combine_seeds' : True,
          'data_model_version' : "DM_2016_03_15_1800",
          'mol_colors' : False,
          'output_buf_size' : "",
          'plot_layout' : " plot ",
          'plot_legend' : "0",
          'rxn_step' : "",
          'reaction_output_list' : []
        }

    def add_observable(self, item):
        self.dm['mcell']['reaction_data_output']['reaction_output_list'].append(item)
    
    def add_rules(self, react_list):
        self.dm['mcell']['define_reactions'] = { 'data_model_version' : "DM_2014_10_24_1638" }
        self.dm['mcell']['define_reactions']['reaction_list'] = react_list

    def append_to_geom_obj_list(self, item):
        self.dm['mcell']['geometrical_objects']['object_list'].append(item)
    def append_to_model_obj_list(self, item):
        self.dm['mcell']['model_objects']['model_object_list'].append(item)

    def append_objects(self, obj, inner_parent, outer_parent):
      # Append this object (if 3D) and its 3D children to the data model object list
      print ( "append_objects called with obj = " + str(obj['name']) )
      if 'dim' in obj.keys():
        if int(obj['dim']) == 3:
          xr = obj['xdim'] / 2.0
          yr = obj['ydim'] / 2.0
          zr = obj['zdim'] / 2.0
          points,faces = create_rectangle (-xr, xr, -yr, yr, -zr, zr )
    
          inner_parent_name = ""
          if inner_parent != None:
            if 'dim' in inner_parent.keys():
              inner_parent_name = inner_parent['name']
    
          go = {
              'name' : obj['name'],
              'location' : [obj['x'], obj['y'], obj['z']],
              'material_names' : ['membrane_mat'],
              'vertex_list' : points,
              'element_connections' : faces }
    
          if len(inner_parent_name) > 0:
            go['define_surface_regions'] = [ { 'include_elements' : [ i for i in range(len(faces)) ], 'name' : inner_parent_name } ]
          else:
            go['define_surface_regions'] = [ { 'include_elements' : [ i for i in range(len(faces)) ], 'name' : obj['name']+'_outer_wall' } ]
    
          self.append_to_geom_obj_list(go)
    
          mo = {
              'name' : obj['name'],
              'parent_object' : "",
              'membrane_name' : inner_parent_name,
              'description' : "",
              'object_source' : "blender",
              'dynamic' : False,
              'dynamic_display_source' : "script",
              'script_name' : "" }
    
          if outer_parent != None:
            if 'dim' in outer_parent.keys():
              mo['parent_object'] = outer_parent['name']
    
          self.append_to_model_obj_list(mo)
    
      if '~children' in obj.keys():
        children = obj['~children']
        if len(children) > 0:
          for k in children.keys():
            child = children[k]
            self.append_objects(child, obj, inner_parent)

#### Helper Functions ####
dump_depth = 0;
def dump_data_model ( name, dm ):
    global dump_depth
    dict_type = type({'a':1})
    list_type = type(['a',1])
    if type(dm) == type({'a':1}):  #dm is a dictionary
        print ( str(dump_depth*"  ") + name + " {}" )
        dump_depth += 1
        for k,v in sorted(dm.items()):
            dump_data_model ( k, v )
        dump_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
        num_items = len(dm)
        one_liner = True
        if num_items > 4:
            one_liner = False
        for v in dm:
            if type(v) in [dict_type, list_type]:
              one_liner = False
              break
        if one_liner:
            print ( str(dump_depth*"  ") + name + " [] = " + str(dm) )
        else:
            print ( str(dump_depth*"  ") + name + " []" )
            dump_depth += 1
            i = 0
            for v in dm:
                k = name + "["+str(i)+"]"
                dump_data_model ( k, v )
                i += 1
            dump_depth += -1
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
        print ( str(dump_depth*"  ") + name + " = " + "\"" + str(dm) + "\"" )
    else:
        print ( str(dump_depth*"  ") + name + " = " + str(dm) )


def write_data_model ( dm, file_name ):
  """ Write a data model to a named file """
  if (file_name[-5:].lower() == '.json'):
    # Assume this is a JSON format file
    print ( "Saving a JSON file" )
    f = open ( file_name, 'w' )
    jde = json.JSONEncoder ( indent=2, separators=(",",": "), sort_keys=True )
    json_string = jde.encode ( dm )
    status = f.write ( json_string )
    f.write ( "\n" )
    # status = f.write ( json.dumps ( dm ) )
  else:
    # Assume this is a pickled format file
    print ( "Saving to a Pickle file" )
    f = open ( file_name, 'w' )
    status = f.write ( pickle.dumps(dm,protocol=0).decode('latin1') )
    f.close()
  return status

def get_max_depth ( parent ):
  # Count the depth of the tree
  max_child_depth = 0
  if '~children' in parent:
    children = parent['~children']
    for k in children.keys():
      child = children[k]
      child_depth = get_max_depth ( child )
      if child_depth > max_child_depth:
        max_child_depth = child_depth
  return ( max_child_depth + 1 )


def check_legal ( parent ):
  # Ensure that parents and children alternate between volume and surface
  if '~children' in parent:
    children = parent['~children']
    if 'dim' in parent:
      for child_key in children.keys():
        if parent['dim'] == children[child_key]['dim']:
          print ( "ERROR: Nested Children must alternate dimensions" )
    for child in children:
      check_legal ( child )


def find_object_by_name ( parent, name ):
  # Ensure that parents and children alternate between volume and surface
  if 'name' in parent:
    if parent['name'] == name:
      return parent
  if '~children' in parent:
    children = parent['~children']
    for child_key in children.keys():
      found_object = find_object_by_name ( children[child_key], name )
      if found_object != None:
        return found_object
  return None


def update_compartment_defs ( parent, compartment_type_dict ):
  if ('dim' in parent) and ('name' in parent):
    compartment_type_dict[parent['name']] = parent['dim']
  if '~children' in parent:
    children = parent['~children']
    for child_key in children.keys():
      update_compartment_defs ( children[child_key], compartment_type_dict )


def contains_siblings ( parent ):
  # Detect whether there are any sibling relationships in the tree
  if '~children' in parent:
    children = parent['~children']
    if len(children) > 1:
      return True
    else:
      for child_key in children.keys():
        if contains_siblings ( children[child_key] ):
          return True
  else:
    return False

def get_child_names ( parent ):
  child_names = []
  if '~children' in parent:
    child_names = [ k for k in parent['~children'].keys() ]
  return child_names

def get_grandchild_names ( parent ):
  grandchild_names = []
  if '~children' in parent:
    child_names = [ k for k in parent['~children'].keys() ]
    for child_name in child_names:
      child = parent['~children'][child_name]
      if '~children' in child:
        for k in child['~children'].keys():
          grandchild_names.append ( k )
  return grandchild_names

def build_topology_from_list ( cdefs, parent ):
  c_by_name = {}
  for c in cdefs:
    print ( "cdef = " + str(c) )
    if len(c) == 3:
      # This is an outer compartment
      print ( "Outer" )
      parent['~children'][c[0]] = { 'name':c[0], 'dim':c[1], 'vol':c[2], '~children':{} }
      c_by_name[c[0]] = parent['~children'][c[0]]
    elif len(c) == 4:
      # This compartment has a parent ... find it and add it
      print ( "Inside " + str(c[3]) )
      c_by_name[c[3]]['~children'][c[0]] = { 'name':c[0], 'dim':c[1], 'vol':c[2], '~children':{} }
      c_by_name[c[0]] = c_by_name[c[3]]['~children'][c[0]]
  return parent

def assign_nested_dimensions ( obj ):
  # Figure out the dimensions needed for each compartment to have the proper volume
  child_volume = 0
  print ( "Assigning dimensions for object: " + str(obj['name']) )
  if '~children' in obj:
    children = obj['~children']
    if len(children) > 0:
      for k in children.keys():
        child = children[k]
        assign_nested_dimensions ( child )
        if 'vol' in child.keys():
          child_volume += float(child['vol'])
  if 'vol' in obj.keys():
    print ( "Using volume of \"" + str(obj['vol']) + "\"" )
    # Compute the dimensions that will provide the compartment volume and the child volume
    cube_len = math.pow ( float(obj['vol'])+child_volume, 1/3 )
    obj['xdim'] = cube_len
    obj['ydim'] = cube_len
    obj['zdim'] = cube_len
  else:
    print ( "Object has no volume" )
    # It's not clear whether these even need to be added in this case or should it be cube root of child volume?
    # This should only happen for the outer "World" object which is just a logical container for actual inner objects.
    obj['xdim'] = 0
    obj['ydim'] = 0
    obj['zdim'] = 0

def assign_linear_dimensions ( obj, inner_cube_dim, nesting_space ):
  # Figure out the dimensions needed for each object to contain its children
  print ( "Assigning dimensions for object: " + str(obj['name']) )
  if 'vol' in obj.keys():
    print ( "***** WARNING: Ignoring volume of \"" + str(obj['vol']) + "\"" )
  obj['xdim'] = inner_cube_dim
  obj['ydim'] = inner_cube_dim
  obj['zdim'] = inner_cube_dim
  if '~children' in obj:
    children = obj['~children']
    if len(children) > 0:
      for k in children.keys():
        child = children[k]
        assign_linear_dimensions ( child, inner_cube_dim, nesting_space )
      obj['xdim'] = nesting_space
      for k in children.keys():
        child = children[k]
        obj['xdim'] += child['xdim'] + nesting_space
      max_y_dim = 0
      max_z_dim = 0
      for k in children.keys():
        child = children[k]
        max_y_dim = max ( max_y_dim, child['ydim'] )
        max_z_dim = max ( max_z_dim, child['zdim'] )
      obj['ydim'] = max_y_dim + (2*nesting_space)
      obj['zdim'] = max_z_dim + (2*nesting_space)

def assign_linear_coordinates ( obj, x, y, z, nesting_space ):
  # Convert the dimensions to actual coordinates distributed along the x axis
  obj['x'] = x
  obj['y'] = y
  obj['z'] = z
  if '~children' in obj:
    children = obj['~children']
    if len(children) > 0:
      x_offset = nesting_space - ( obj['xdim'] / 2.0 )
      for k in children.keys():
        child = children[k]
        assign_linear_coordinates ( child, x+x_offset+(child['xdim']/2.0), y, z, nesting_space )
        x_offset += child['xdim'] + nesting_space

def assign_nested_coordinates ( obj, x, y, z ):
  # Convert the dimensions to actual coordinates centered at the origin
  obj['x'] = x
  obj['y'] = y
  obj['z'] = z
  if '~children' in obj:
    children = obj['~children']
    if len(children) > 0:
      for k in children.keys():
        child = children[k]
        assign_nested_coordinates ( child, x, y, z )


def create_rectangle ( xmin, xmax, ymin, ymax, zmin, zmax ):
    points = [
        [ xmin, ymin, zmin ],
        [ xmin, ymin, zmax ],
        [ xmin, ymax, zmin ],
        [ xmin, ymax, zmax ],
        [ xmax, ymin, zmin ],
        [ xmax, ymin, zmax ],
        [ xmax, ymax, zmin ],
        [ xmax, ymax, zmax ]
      ]
    faces = [
        [ 3, 0, 1 ],
        [ 7, 2, 3 ],
        [ 5, 6, 7 ],
        [ 1, 4, 5 ],
        [ 2, 4, 0 ],
        [ 7, 1, 5 ],
        [ 3, 2, 0 ],
        [ 7, 6, 2 ],
        [ 5, 4, 6 ],
        [ 1, 0, 4 ],
        [ 2, 6, 4 ],
        [ 7, 3, 1 ]
      ]
    return [ points, faces ]


def read_data_model_from_bngl_text ( bngl_model_text ):
  print("\n\n\nReading BNGL Model\n\n\n")

  # First split by lines to remove comments and whitespace on ends
  # lines = re.split(r'\n', bngl_model_text)
  lines = r'\n'.join(re.split(r'\r', bngl_model_text))
  lines = r' '.join(re.split(r'\t', lines))
  lines = re.split('\n', lines)
  i = 0
  for i in range(len(lines)):
    lines[i] = lines[i].strip()
    l = lines[i]
    if '#' in l:
      lines[i] = l.split('#')[0].strip()

  # Remove any empty lines
  lines = [ l.strip() for l in lines if len(l.strip()) > 0 ]

  # Remove any lines after the "end model" tokens.
  # This might be done more efficiently below, but it might be more clear here
  model_lines = []
  past_end = False
  for l in lines:
    if not past_end:
      model_lines.append ( l )
      tokens = [ t for t in l.split() if len(t) > 0 ]
      if len(tokens) > 1:
        if (tokens[0] == 'end') and (tokens[1] == 'model'):
          past_end = True
  lines = model_lines

  # Separate into blocks assuming begin/end pairs with outer b/e model
  blocks = []
  current_block = []
  for l in lines:
    tokens = [ t for t in l.split() if len(t) > 0 ]
    if (tokens[0] == 'begin') and (tokens[1] == 'model'):
      pass
    elif (tokens[0] == 'end') and (tokens[1] == 'model'):
      pass
    elif (tokens[0] == 'begin'):
      if len(current_block) > 0:
        blocks.append ( current_block )
        current_block = []
      current_block.append ( l )
    elif (tokens[0] == 'end'):
      current_block.append ( l )
    else:
      current_block.append( l )
  if len(current_block) > 0:
    blocks.append ( current_block )

  # Verify that each block has a begin and end that matches
  for block in blocks:
    line_parts = block[0].split()
    if (len(line_parts) < 2) or (line_parts[0] != 'begin'):
      print ( "Error: every block should start with \"begin\", and include a block type." )
      exit(1)
    line_parts = block[-1].split()
    if (len(line_parts) < 2) or (line_parts[0] != 'end'):
      print ( "Error: every block should end with \"end\", and include a block type." )
      exit(1)
    if ' '.join(block[0].split()[1:]) != ' '.join(block[-1].split()[1:]):
      print ( "Error: begin and end must match" )
      exit(1)

  # Now start building the data model
  dm = DataModel()

  # Add the parameter system and build a parameter/value dictionary for future use
  # This assumes that parameters are defined before being used
  par_expr_dict = {}
  par_val_dict = {}

  par_list = []
  for block in blocks:
    if ' '.join(block[0].split()[1:]) == 'parameters':
      # Process parameters
      for line in block[1:-1]:
        # Pull MCellR special items out of the BNGL file (they will appear as regular parameters such as MCELL_ITERATIONS...)
        print("++++++" + line)
        name_val = line.split()
        if name_val[0] in dm.special_parameters.keys():
          if len(name_val) == 3:
            dm.special_parameters[name_val[0]] = name_val[2]
          else:
            dm.special_parameters[name_val[0]] = name_val[1]
        else:
          # Note that taking this section out of the "else" would also include the special parameters in par_val_dict
          # It's not clear whether that is what should be done.
          par = {}
          par['par_name'] = name_val[0]
          if len(name_val) == 3:
            par['par_expression'] = ' '.join ( name_val[2:] )
          else:
            par['par_expression'] = ' '.join ( name_val[1:] )
          par['par_description'] = ""
          par['par_units'] = ""
          par_list.append ( par )
          # Store an evaluated copy of this parameter in the parameter/value dictionary
          # This assumes that parameters are defined before being used
          par_expr_dict[par['par_name']] = par['par_expression']
          par_val_dict[par['par_name']] = eval(par['par_expression'],globals(),par_val_dict)

  dm.add_parameters(par_list)

  for k in sorted(par_val_dict.keys()):
    print ( "  " + str(k) + " = " + str(par_expr_dict[k]) + " = " + str(par_val_dict[k]) )

  # Add the compartments
  # Format:   Name Dimension Volume [outside compartment]
  # Compartment Topology Rules
  #  (generally analogous to SBML compartment topology)
  #    The outside of a surface must be volume (or undefined).
  #    The outside of a volume must be a surface (or undefined).
  #    A compartment may only have one outside.
  #    A volume may be outside of multiple surfaces.
  #    A surface may be outside of only one volume.
  #  The outside compartment must be defined before it is referenced

  nesting_space = 0.05 # Note that this should be half of desired because of the intervening 2D surfaces
  inner_cube_dim = 0.5

  compartment_type_dict = {} # This will be a dictionary of name:type for each compartment
  molecule_type_dict = {}    # This will be a dictionary of name:[types] for each molecule
  topology = None            # This will be a recursive tree dictionary of nested objects

  for block in blocks:
    if ' '.join(block[0].split()[1:]) == 'compartments':
      # Process compartments

      cdefs = []
      for line in block[1:-1]:
        parts = [ p for p in line.strip().split() ]
        # Evaluate the volume expression string (3rd value, parts[2]) to a float
        parts[2] = eval(parts[2],globals(),par_val_dict)
        cdefs.append(parts)

      topology = build_topology_from_list ( cdefs, { '~children':{}, 'name':"World" } )
      check_legal ( topology )
      update_compartment_defs ( topology, compartment_type_dict )
      if contains_siblings(topology):
        print ( "Topology contains siblings" )
        print ( "***** WARNING: Compartment Volumes are not used with siblings" )
        assign_linear_dimensions ( topology, inner_cube_dim, nesting_space )
        assign_linear_coordinates ( topology, 0, 0, 0, nesting_space )
      else:
        print ( "Topology does not contain siblings. Create nested volumes." )
        assign_nested_dimensions ( topology )
        assign_nested_coordinates ( topology, 0, 0, 0 )


      dm.append_objects ( topology, None, None )  

      print ( "Max depth = " + str(get_max_depth(topology)) )

      # Print the compartments:
      print ( "Topology = " + str(topology) )

      dump_data_model ( "Topology", topology )


  for k in compartment_type_dict.keys():
    print ( "  Compartment " + str(k) + " is type " + str(compartment_type_dict[k]) )

  dm.add_materials()
  dm.mod_surface_regions()

  # Add the seed species as release sites
  rel_list = []
  site_num = 1
  for block in blocks:
    if ' '.join(block[0].split()[1:]) == 'seed species':
      # Process seed species
      for line in block[1:-1]:
        print ( "Release line: " + line )
        mol_expr, mol_quant = line.strip().split()
        rel_item = {
          'data_model_version' : "DM_2018_01_11_1330",
          'description' : "",
          'location_x' : "0",
          'location_y' : "0",
          'location_z' : "0",
          'molecule' : mol_expr,
          'name' : "Rel_Site_" + str(site_num),
          'object_expr' : "",
          'orient' : "'",
          'pattern' : "",
          'points_list' : [],
          'quantity' : mol_quant,
          'quantity_type' : "NUMBER_TO_RELEASE",
          'release_probability' : "1",
          'shape' : "OBJECT",
          'site_diameter' : "0",
          'stddev' : "0"
        }

        # Release based on compartment names and parent/child relationships in the object topology

        if '@' in mol_expr:
          # This release site is in a compartment
          compartment_name = None
          mol_name = None
          if ":" in mol_expr:
            # This is the old format using a colon
            compartment_name = mol_expr[mol_expr.find('@')+1:mol_expr.find(':')].strip()
            mol_name = mol_expr[mol_expr.find(':')+1:]
            mol_name = mol_name[0:mol_name.find('(')].strip()
            # some notations will use double :: for compartments
            mol_name = mol_name.replace(":","")
          else:
            compartment_name = mol_expr[mol_expr.find('@')+1:].split()[0].strip()
            if '(' in mol_expr:
              mol_name = mol_expr.split('(')[0].strip()
            else:
              mol_name = mol_expr.split('@')[0].strip()
          if not (mol_name in molecule_type_dict):
            molecule_type_dict[mol_name] = []
          # Note that a molecule may be of multiple types if used in different contexts!!
          # This might be better implemented as a set, but using a dictionary for now
          molecule_type_dict[mol_name].append ( compartment_type_dict[compartment_name] )

          compartment = find_object_by_name ( topology, compartment_name )
          compartment_expression = ""
          if compartment['dim'] == '3':
            # The compartment of interest is a volume
            # The volume's children will be surfaces
            # The volume's grandchildren will be volumes (which is what MCell expects)
            # Each of these grandchildren will need to be subtracted from the volume
            compartment_expression = compartment['name'] + "[ALL]"
            grandchild_names = get_grandchild_names ( compartment )
            print ( "  " + str(compartment['name']) + " is " + str(compartment['dim']) + "D" )
            print ( "    GrandChildren: " + str(grandchild_names) )
            for cn in grandchild_names:
              compartment_expression += " - " + cn + "[ALL]"
          elif compartment['dim'] == '2':
            # The OUTER compartment of interest is a surface.
            # In CBNGL, the enclosed volume is the INNER object.
            # In MCell, the surface is referenced as a part of the volume object: vol[surf]
            # In mixed MCell/CBNGL syntax, this becomes INNER[OUTER]
            child_names = get_child_names ( compartment )
            print ( "  " + str(compartment['name']) + " is " + str(compartment['dim']) + "D" )
            print ( "    Children: " + str(child_names) )
            if len(child_names) > 1:
              print ( "***** WARNING: Surface should not contain more than one volume!!" )
            compartment_expression = child_names[0] + "[" + compartment['name'] + "]"
          print ( "  " + "Releasing " + rel_item['molecule'] + " in " + compartment_expression )
          print ( "  " )
          rel_item['object_expr'] = compartment_expression

        rel_list.append(rel_item)
        site_num += 1

  for rel_item in rel_list:
    print ( "  Release " + str(rel_item['molecule']) + " at " + str(rel_item['object_expr']) )

  dm.add_release_sites(rel_list)

  for k in molecule_type_dict.keys():
    print ( "  Molecule " + str(k) + " is of types: " + str(molecule_type_dict[k]) )


  # Add the molecules list here since the vol/surf type is deduced from compatments and seed species (above)

  default_vol_dc = "1e-6"
  default_surf_dc = "1e-8"

  if 'MCELL_DEFAULT_DIFFUSION_CONSTANT_3D' in dm.special_parameters:
    default_vol_dc = dm.special_parameters.pop('MCELL_DEFAULT_DIFFUSION_CONSTANT_3D')
  if 'MCELL_DEFAULT_DIFFUSION_CONSTANT_2D' in dm.special_parameters:
    default_surf_dc = dm.special_parameters.pop('MCELL_DEFAULT_DIFFUSION_CONSTANT_2D')

  mol_list = []
  color_index = 1
  vol_glyphs = ['Icosahedron', 'Sphere_1', 'Sphere_2', 'Octahedron', 'Cube']
  surf_glyphs = ['Torus', 'Cone', 'Receptor', 'Cylinder', 'Pyramid', 'Tetrahedron']
  vol_glyph_index = 0
  surf_glyph_index = 0
  for block in blocks:
    if ' '.join(block[0].split()[1:]) == 'molecule types':
      # Process molecules
      for line in block[1:-1]:
        mol = {}
        mol['data_model_version'] = "DM_2018_01_11_1330"
        mol['mol_name'] = line.split('(')[0].strip()

        mol['mol_type'] = '3D'
        if mol['mol_name'] in molecule_type_dict.keys():
          print ( "Assigning molecule {} based on type of : ".format(mol['mol_name']) + str(molecule_type_dict[mol['mol_name']]) )
          # Use the first item in the list for now. Eventually may need to create two mols (for vol & surf)
          if int(molecule_type_dict[mol['mol_name']][0]) == 2:
            mol['mol_type'] = '2D'
        else:
          print ( "***** WARNING: Molecule type not known for \"" + mol['mol_name'] + "\", using 3D" )

        mol['custom_space_step'] = ""
        mol['custom_time_step'] = ""
        mol['description'] = ""

        if mol['mol_type'] == '3D':
          mol['diffusion_constant'] = default_vol_dc
          key = 'MCELL_DIFFUSION_CONSTANT_3D_' + mol['mol_name']
          if key in dm.special_parameters:
            mol['diffusion_constant'] = dm.special_parameters.pop(key)
        else:
          mol['diffusion_constant'] = default_surf_dc
          key = 'MCELL_DIFFUSION_CONSTANT_2D_' + mol['mol_name']
          if key in dm.special_parameters:
            mol['diffusion_constant'] = dm.special_parameters.pop(key)

        mol['export_viz'] = False
        mol['maximum_step_length'] = ""
        mol['mol_bngl_label'] = ""
        mol['target_only'] = False

        mol['display'] = { 'color': [color_index&1, color_index&2, color_index&4], 'emit': 0.0, 'glyph': "Cube", 'scale': 1.0 }
        color_index += 1
        if mol['mol_type'] == '2D':
          mol['display']['glyph'] = surf_glyphs[surf_glyph_index%len(surf_glyphs)]
          surf_glyph_index += 1
        else:
          mol['display']['glyph'] = vol_glyphs[vol_glyph_index%len(vol_glyphs)]
          vol_glyph_index += 1

        mol['bngl_component_list'] = []
        if "(" in line:
          mol_comps = line.split('(')[1].split(')')[0].split(',')
          for c in mol_comps:
            comp = {}
            cparts = c.split('~')
            comp['cname'] = cparts[0]
            comp['cstates'] = []
            if len(cparts) > 1:
              comp['cstates'] = cparts[1:]
            mol['bngl_component_list'].append ( comp )
        mol_list.append ( mol )

  dm.add_molecules(mol_list)

  # This regular expression seems to find BNGL molecules with parens: \b\w+\([\w,~\!\?\+]+\)+([.]\w+\([\w,~\!\?\+]+\))*
  mol_regx = "\\b\\w+\\([\\w,~\\!\\?\\+]+\\)+([.]\\w+\\([\\w,~\\!\\?\\+]+\\))*"

  # This regular expression seems to find BNGL molecules with or without parens: \b\w+(\([\w,~\!\?\+]+\)+)*([.]\w+\([\w,~\!\?\+]+\))*
  mol_regx = "\\b\\w+(\\([\\w,~\\!\\?\\+]+\\)+)*([.]\\w+\\([\\w,~\\!\\?\\+]+\\))*"

  compiled_mol_regx = re.compile(mol_regx)

  dm.init_observables()
  # Fill in the reaction output list
  for block in blocks:
    if ' '.join(block[0].split()[1:]) == 'observables':
      # Process observables
      for line in block[1:-1]:

        print ( "Observables Line: " + line )

        split_line = line.strip().split()
        keyword = split_line[0]
        if keyword != "Molecules":
          print ( "Warning: Conversion only supports Molecule observables" )
        label = split_line[1]

        mols_part = ' '.join(split_line[2:])
        print ( "  Mols part: " + mols_part )

        start = 0
        end = 0
        match = compiled_mol_regx.search(mols_part,start)
        things_to_count = []
        while match:
          start = match.start()
          end = match.end()
          print ( "  Found: \"" + mols_part[start:end] + "\"" )
          things_to_count.append ( mols_part[start:end] )
          start = end
          match = compiled_mol_regx.search(mols_part,start)

        count_parts = [ "COUNT[" + thing + ",WORLD]" for thing in things_to_count ]
        count_expr = ' + '.join(count_parts)

        mdl_prefix = label
        if label.endswith ( '_MDLString' ):
          mdl_prefix = label[0:len(label)-len('_MDLString')]
        count_item = {
            'count_location' : "World",
            'data_file_name' : "",
            'data_model_version' : "DM_2018_01_11_1330",
            'description' : "",
            'mdl_file_prefix' : mdl_prefix,
            'mdl_string' : count_expr,
            'molecule_name' : "",
            'name' : "MDL: " + count_expr,
            'object_name' : "",
            'plotting_enabled' : True,
            'reaction_name' : "",
            'region_name' : "",
            'rxn_or_mol' : "MDLString"
          }
        dm.add_observable(count_item)

  # reaction rules

  # These regular expressions seem to find rates at the end of a line
  last_rate_regx = "[\\w\\.+-]+$"
  last_2_rates_regx = "([\w\.+-]+){1}\s*,\s*([\w\.+-]+){1}$"

  compiled_last_rate_regx = re.compile(last_rate_regx)
  compiled_last_2_rates_regx = re.compile(last_2_rates_regx)

  react_list = []
  for block in blocks:
    if ' '.join(block[0].split()[1:]) == 'reaction rules':
      # Process reaction rules
      for line in block[1:-1]:
        rxn = {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "",
                'name' : "",
                'products' : "",
                'reactants' : "",
                'rxn_name' : "",
                'rxn_type' : "",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              }
        if '<->' in line:
          # Process as a reversible reaction
          parts = [ s.strip() for s in line.strip().split('<->') ]
          reactants = parts[0]

          match = compiled_last_2_rates_regx.search(parts[1],0)
          start = match.start()
          end = match.end()
          products = parts[1][0:start]
          rates = parts[1][start:end]
          frate,rrate = [ r.strip() for r in rates.split(',') ]

          rxn['reactants'] = reactants
          rxn['products'] = products
          rxn['fwd_rate'] = frate
          rxn['bkwd_rate'] = rrate
          rxn['rxn_type'] = "reversible"
          rxn['name'] = reactants + " <-> " + products
        elif '->' in line:
          # Process as an irreversible reaction
          parts = [ s.strip() for s in line.strip().split('->') ]
          reactants = parts[0]

          match = compiled_last_rate_regx.search(parts[1],0)
          start = match.start()
          end = match.end()
          products = parts[1][0:start]
          frate = parts[1][start:end].strip()

          rxn['reactants'] = reactants
          rxn['products'] = products
          rxn['fwd_rate'] = frate
          rxn['bkwd_rate'] = ""
          rxn['rxn_type'] = "irreversible"
          rxn['name'] = reactants + " -> " + products
        else:
          # Error?
          print ( "Reaction definition \"" + line + "\" does not specify '->' or '<->'" )

        react_list.append ( rxn )

  dm.add_rules(react_list)
  dm.handle_special_params()
  return dm.dm


def read_data_model_from_bngsim( model ):
  # Now start building the data model
  dm = DataModel()

  # Add the parameter system and build a parameter/value dictionary for future use
  # This assumes that parameters are defined before being used

  par_expr_dict = {}
  par_val_dict = {}

  par_list = []
  for param in model.parameters: 
    if "MCELL_" in param:
      if param in model.parameters.expressions:
        dm.special_parameters[param] = model.parameters.expressions[param]
      else:
        dm.special_parameters[param] = str(model.parameters[param])
    par = {}
    par['par_name'] = param
    if param in model.parameters.expressions:
      par['par_expression'] = model.parameters.expressions[param]
    else:
      par['par_expression'] = str(model.parameters[param])
    par['par_description'] = ""
    par['par_units'] = ""
    par_list.append (par)
    par_val_dict[param] = model.parameters[param]

  dm.add_parameters(par_list)

  for k in sorted(par_val_dict.keys()):
    print ( "  " + str(k) + " = " + str(par_val_dict[k]) )

  # Add the compartments
  # Format:   Name Dimension Volume [outside compartment]
  # Compartment Topology Rules
  #  (generally analogous to SBML compartment topology)
  #    The outside of a surface must be volume (or undefined).
  #    The outside of a volume must be a surface (or undefined).
  #    A compartment may only have one outside.
  #    A volume may be outside of multiple surfaces.
  #    A surface may be outside of only one volume.
  #  The outside compartment must be defined before it is referenced

  nesting_space = 0.05 # Note that this should be half of desired because of the intervening 2D surfaces
  inner_cube_dim = 0.5

  compartment_type_dict = {} # This will be a dictionary of name:type for each compartment
  molecule_type_dict = {}    # This will be a dictionary of name:[types] for each molecule
  topology = None            # This will be a recursive tree dictionary of nested objects

  cdefs = []
  for compartment in model.compartments:
    dim = model.compartments[compartment][0]
    vol = model.compartments[compartment][1]
    parent = model.compartments[compartment][2]
    if parent is None:
        cdefs.append( [compartment, dim, vol] )
    else:
        cdefs.append( [compartment, dim, vol, parent] )
  # FIXME: If this topology is out of order, next command fails
  print(cdefs)
  topology = build_topology_from_list ( cdefs, { '~children':{}, 'name':"World" } )
  check_legal ( topology )
  update_compartment_defs ( topology, compartment_type_dict )
  if contains_siblings(topology):
    print ( "Topology contains siblings" )
    print ( "***** WARNING: Compartment Volumes are not used with siblings" )
    assign_linear_dimensions ( topology, inner_cube_dim, nesting_space )
    assign_linear_coordinates ( topology, 0, 0, 0, nesting_space )
  else:
    print ( "Topology does not contain siblings. Create nested volumes." )
    assign_nested_dimensions ( topology )
    assign_nested_coordinates ( topology, 0, 0, 0 )

    dm.append_objects (topology, None, None)

    print ( "Max depth = " + str(get_max_depth(topology)) )

    # Print the compartments:
    print ( "Topology = " + str(topology) )

    dump_data_model ( "Topology", topology )


  for k in compartment_type_dict.keys():
    print ( "  Compartment " + str(k) + " is type " + str(compartment_type_dict[k]) )


  # adjusting materials 
  dm.add_materials()
  dm.mod_surface_regions()

  # Add the seed species as release sites
  site_num = 1
  rel_list = []
 
  for species in model.species:
    mol_patt, mol_quant = species, model.species[species]
    mol_expr = mol_patt.string
    rel_item = {
      'data_model_version' : "DM_2018_01_11_1330",
      'description' : "",
      'location_x' : "0",
      'location_y' : "0",
      'location_z' : "0",
      'molecule' : mol_expr,
      'name' : "Rel_Site_" + str(site_num),
      'object_expr' : "",
      'orient' : "'",
      'pattern' : "",
      'points_list' : [],
      'quantity' : str(mol_quant),
      'quantity_type' : "NUMBER_TO_RELEASE",
      'release_probability' : "1",
      'shape' : "OBJECT",
      'site_diameter' : "0",
      'stddev' : "0"
    }

    # Release based on compartment names and parent/child relationships in the object topology

    # replacing parsing with info from molecule pattern
    mol_dict = mol_patt.molecules[0]
    if 'compartment' in mol_dict:
      mol_name = mol_dict['name']
      compartment_name = mol_dict['compartment']
      if not (mol_name in molecule_type_dict):
        molecule_type_dict[mol_name] = []
      # Note that a molecule may be of multiple types if used in different contexts!!
      # This might be better implemented as a set, but using a dictionary for now
      molecule_type_dict[mol_name].append ( compartment_type_dict[compartment_name] )

      compartment = find_object_by_name ( topology, compartment_name )
      compartment_expression = ""
      if compartment['dim'] == str(3):
        # The compartment of interest is a volume
        # The volume's children will be surfaces
        # The volume's grandchildren will be volumes (which is what MCell expects)
        # Each of these grandchildren will need to be subtracted from the volume
        compartment_expression = compartment['name'] + "[ALL]"
        grandchild_names = get_grandchild_names ( compartment )
        print ( "  " + str(compartment['name']) + " is " + str(compartment['dim']) + "D" )
        print ( "    GrandChildren: " + str(grandchild_names) )
        for cn in grandchild_names:
          compartment_expression += " - " + cn + "[ALL]"
      elif compartment['dim'] == str(2):
        # The OUTER compartment of interest is a surface.
        # In CBNGL, the enclosed volume is the INNER object.
        # In MCell, the surface is referenced as a part of the volume object: vol[surf]
        # In mixed MCell/CBNGL syntax, this becomes INNER[OUTER]
        child_names = get_child_names ( compartment )
        print ( "  " + str(compartment['name']) + " is " + str(compartment['dim']) + "D" )
        print ( "    Children: " + str(child_names) )
        if len(child_names) > 1:
          print ( "***** WARNING: Surface should not contain more than one volume!!" )
        compartment_expression = child_names[0] + "[" + compartment['name'] + "]"
      print ( "  " + "Releasing " + rel_item['molecule'] + " in " + compartment_expression )
      print ( "  " )
      rel_item['object_expr'] = compartment_expression

    rel_list.append(rel_item)
    site_num += 1

  for rel_item in rel_list:
    print ( "  Release " + str(rel_item['molecule']) + " at " + str(rel_item['object_expr']) )

  dm.add_release_sites(rel_list)

  for k in molecule_type_dict.keys():
    print ( "  Molecule " + str(k) + " is of types: " + str(molecule_type_dict[k]) )


  # Add the molecules list here since the vol/surf type is deduced from compatments and seed species (above)

  default_vol_dc = "1e-6"
  default_surf_dc = "1e-8"

  if 'MCELL_DEFAULT_DIFFUSION_CONSTANT_3D' in dm.special_parameters:
    default_vol_dc = dm.special_parameters.pop('MCELL_DEFAULT_DIFFUSION_CONSTANT_3D')
  if 'MCELL_DEFAULT_DIFFUSION_CONSTANT_2D' in dm.special_parameters:
    default_surf_dc = dm.special_parameters.pop('MCELL_DEFAULT_DIFFUSION_CONSTANT_2D')

  mol_list = []
  color_index = 1
  vol_glyphs = ['Icosahedron', 'Sphere_1', 'Sphere_2', 'Octahedron', 'Cube']
  surf_glyphs = ['Torus', 'Cone', 'Receptor', 'Cylinder', 'Pyramid', 'Tetrahedron']
  vol_glyph_index = 0
  surf_glyph_index = 0

  for mtype in model.moltypes:
    mol = {}
    mol['data_model_version'] = "DM_2018_01_11_1330"
    mol['mol_name'] = mtype.molecules[0]['name']
    mol['mol_type'] = '3D'
    if mol['mol_name'] in molecule_type_dict.keys():
      print ( "Assigning molecule {} based on type of : ".format(mol['mol_name']) + str(molecule_type_dict[mol['mol_name']]) )
      # Use the first item in the list for now. Eventually may need to create two mols (for vol & surf)
      if int(molecule_type_dict[mol['mol_name']][0]) == 2:
        mol['mol_type'] = '2D'
    else:
      print ( "***** WARNING: Molecule type not known for \"" + mol['mol_name'] + "\", using 3D" )

    mol['custom_space_step'] = ""
    mol['custom_time_step'] = ""
    mol['description'] = ""

    if mol['mol_type'] == '3D':
      mol['diffusion_constant'] = default_vol_dc
      key = 'MCELL_DIFFUSION_CONSTANT_3D_' + mol['mol_name']
      if key in dm.special_parameters:
        mol['diffusion_constant'] = dm.special_parameters.pop(key)
    else:
      mol['diffusion_constant'] = default_surf_dc
      key = 'MCELL_DIFFUSION_CONSTANT_2D_' + mol['mol_name']
      if key in dm.special_parameters:
        mol['diffusion_constant'] = dm.special_parameters.pop(key)

    mol['export_viz'] = False
    mol['maximum_step_length'] = ""
    mol['mol_bngl_label'] = ""
    mol['target_only'] = False

    mol['display'] = { 'color': [color_index&1, color_index&2, color_index&4], 'emit': 0.0, 'glyph': "Cube", 'scale': 1.0 }
    color_index += 1
    if mol['mol_type'] == '2D':
      mol['display']['glyph'] = surf_glyphs[surf_glyph_index%len(surf_glyphs)]
      surf_glyph_index += 1
    else:
      mol['display']['glyph'] = vol_glyphs[vol_glyph_index%len(vol_glyphs)]
      vol_glyph_index += 1

    mol['bngl_component_list'] = []
    if len(mtype.molecules[0]['components']) > 0:
      for c in mtype.molecules[0]['components']:
        comp = {}
        comp['cname'] = c['name']
        comp['cstates'] = []
        if 'states' in c:
          comp['cstates'] = c['states']
        mol['bngl_component_list'].append ( comp )
    mol_list.append ( mol )

  dm.add_molecules(mol_list)

  dm.init_observables()

  # Fill in the reaction output list
  for obs in model.observables:
    # obs is the name of the observable
    # model.observables is tuple (type, expression)
    keyword = model.observables[obs][0]
    if keyword != "Molecules":
      print ( "Warning: Conversion only supports Molecule observables" )
    label = obs

    mols_part = model.observables[obs][1].string
    print ( "  Mols part: " + mols_part )

    things_to_count = []
    # can read the molecules directly from the 
    # parsed xml here
    for molec in model.observables[obs][1].molecule_list:
      print("  Found: \"" + molec + "\"")
      things_to_count.append ( molec )

    count_parts = [ "COUNT[" + thing + ",WORLD]" for thing in things_to_count ]
    count_expr = ' + '.join(count_parts)

    mdl_prefix = label
    if label.endswith ( '_MDLString' ):
      mdl_prefix = label[0:len(label)-len('_MDLString')]
    count_item = {
        'count_location' : "World",
        'data_file_name' : "",
        'data_model_version' : "DM_2018_01_11_1330",
        'description' : "",
        'mdl_file_prefix' : mdl_prefix,
        'mdl_string' : count_expr,
        'molecule_name' : "",
        'name' : "MDL: " + count_expr,
        'object_name' : "",
        'plotting_enabled' : True,
        'reaction_name' : "",
        'region_name' : "",
        'rxn_or_mol' : "MDLString"
      }
    dm.add_observable(count_item)

  # reaction rules
  react_list = []
  for rule in model.rules:
    rxn = {
            'bkwd_rate' : "",
            'data_model_version' : "DM_2018_01_11_1330",
            'description' : "",
            'fwd_rate' : "",
            'name' : "",
            'products' : "",
            'reactants' : "",
            'rxn_name' : "",
            'rxn_type' : "",
            'variable_rate' : "",
            'variable_rate_switch' : False,
            'variable_rate_text' : "",
            'variable_rate_valid' : False
          }
    if model.rules[rule].bidirectional:
      # Process as a reversible reaction
      reactants = model.rules[rule].lhs
      products = model.rules[rule].rhs
      frate = model.rules[rule].rate_law[0]
      rrate = model.rules[rule].rate_law[1]

      rxn['reactants'] = reactants
      rxn['products'] = products
      rxn['fwd_rate'] = frate
      rxn['bkwd_rate'] = rrate
      rxn['rxn_type'] = "reversible"
      rxn['name'] = reactants + " <-> " + products
    else:
      # Process as an irreversible reaction
      reactants = model.rules[rule].lhs
      products = model.rules[rule].rhs
      frate = model.rules[rule].rate_law[0]

      rxn['reactants'] = reactants
      rxn['products'] = products
      rxn['fwd_rate'] = frate
      rxn['bkwd_rate'] = ""
      rxn['rxn_type'] = "irreversible"
      rxn['name'] = reactants + " -> " + products
    react_list.append ( rxn )
 
  dm.add_rules(react_list)
  dm.handle_special_params()
  return dm.dm

def read_data_model_from_bngl_file ( bngl_file_name ):
  try: 
    path = os.path.dirname(__file__)
    path = [:-1]
    bngpath = path + ("extensions", "mcell", "bng2")
    path = os.path.join(*bngpath)
    os.environ["BNGPATH"] = path
    import BNGSim
    model = BNGSim.BNGModel(bngl_file_name)
    return read_data_model_from_bngsim( model )
  # we might have to catch more than the import error here
  # e.g. if BNGSim fails to find BNG2.pl 
  except ImportError:
    print("XML parsing via BNGSim failed, using fallback parser")
    bngl_model_file = open ( bngl_file_name, 'r' )
    bngl_model_text = bngl_model_file.read()
    return read_data_model_from_bngl_text ( bngl_model_text )

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print ( "Got parameters: " + sys.argv[1] + " " + sys.argv[2] )
        print ( "Reading BioNetGen File: " + sys.argv[1] )
        dm = read_data_model_from_bngl_file ( sys.argv[1] )

        print ( "Writing CellBlender Data Model: " + sys.argv[2] )
        write_data_model ( dm, sys.argv[2] )

        print ( "Wrote BioNetGen file found in \"" + sys.argv[1] + "\" to CellBlender data model \"" + sys.argv[2] + "\"" )
        # Drop into an interactive python session
        #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    elif len(sys.argv) > 1:
        bngl =  """
                begin model
                begin parameters
                  diff_const_multiplier = 1e-10
                  MCELL_REDEFINE_diff_const_multiplier = 1
                  km2  0.00
                  pLbs  100
                  km1  0.00
                  mu_wall  1e-9    # Viscosity in compartment wall, kg/um.s    units=kg/um.s
                  pLS  30
                  KB  1.3806488e-19    # Boltzmann constant, cm^2.kg/K.s^2    units=cm^2.kg/K.s^2
                  mu_PM  1e-9    # Viscosity in compartment PM, kg/um.s    units=kg/um.s
                  Nav  6.022e8    # Avogadro number based on a volume size of 1 cubic um
                  kmS  0.13
                  kpS  0.0166057788110262*Nav
                  vol_CP  1
                  pLgs  3
                  pSSs  200
                  pSS  100
                  dc  0.1
                  dm  0.1
                  Rc  0.0015    # Radius of a (cylindrical) molecule in 2D compartment, um    units=um
                  gamma  0.5722    # Euler's constant
                  mu_CP  1e-9    # Viscosity in compartment CP, kg/um.s    units=kg/um.s
                  pLSs  100
                  kmLs  0.12
                  vol_EC  39
                  T  298.15    # Temperature, K    units=K
                  Rs  0.002564    # Radius of a (spherical) molecule in 3D compartment, um    units=um
                  mu_EC  1e-9    # Viscosity in compartment EC, kg/um.s    units=kg/um.s
                  rxn_layer_t  0.01
                  vol_wall  0.88/rxn_layer_t    # Surface area
                  pLg  1
                  kmL  20
                  pLb  30
                  Scale_Totals  1    # 0.00358 gives at least one each,   0.5 gives 2 of some
                  kp1  0.000166057788110262*Nav
                  Lig_tot  6.0e3 * Scale_Totals    # Default: 6.0e3
                  kpL  0.0166057788110262/rxn_layer_t
                  kp2  1.66057788110262e-06/rxn_layer_t
                  Syk_tot  4e2 * Scale_Totals    # Default: 4e2
                  Rec_tot  4.0e2 * Scale_Totals    # Default: 4.0e2
                  Lyn_tot  2.8e2 * Scale_Totals    # Default: 2.8e2
                  kpLs  0.0166057788110262/rxn_layer_t
                  vol_PM  0.01/rxn_layer_t    # Surface area
                  h  rxn_layer_t    # Thickness of 2D compartment, um    units=um
                  MCELL_ITERATIONS  1000
                  MCELL_TIME_STEP 1e-6
                  MCELL_VACANCY_SEARCH_DISTANCE  10
                  MCELL_DEFAULT_DIFFUSION_CONSTANT_2D  1.7e-7 * diff_const_multiplier
                  MCELL_DEFAULT_DIFFUSION_CONSTANT_3D  8.51e-7 * diff_const_multiplier
                  MCELL_DIFFUSION_CONSTANT_2D_Lyn  1.7e-7 * diff_const_multiplier
                  MCELL_DIFFUSION_CONSTANT_2D_Rec  1.7e-7 * diff_const_multiplier
                  MCELL_DIFFUSION_CONSTANT_3D_Lig  8.51e-7 * diff_const_multiplier
                  MCELL_DIFFUSION_CONSTANT_3D_Syk  8.51e-7 * diff_const_multiplier
                end parameters
                begin molecule types
                  Lig(l,l)
                  Lyn(SH2,U)
                  Syk(a~Y~pY,l~Y~pY,tSH2)
                  Rec(a,b~Y~pY,g~Y~pY)
                end molecule types
                begin compartments
                  EC 3 vol_EC
                  PM 2 vol_PM EC
                  CP 3 vol_CP PM
                end compartments
                begin seed species
                   @EC::Lig(l,l)  Lig_tot
                   @PM::Lyn(SH2,U)  Lyn_tot
                   @CP::Syk(a~Y,l~Y,tSH2)  Syk_tot
                   @PM::Rec(a,b~Y,g~Y)  Rec_tot
                end seed species
                begin observables
                  Molecules LycFree_MDLString Lyn(SH2,U)                                              # Should be: "COUNT[Lyn(U,SH2), WORLD]"
                  Molecules RecPbeta_MDLString Rec(b~pY!?)                                            # Should be: "COUNT[Rec(b~pY!?), WORLD]"
                  Molecules RecMon_MDLString Lig(l!1,l).Rec(a!1)                                      # Should be: "COUNT[Rec(a!1).Lig(l!1,l), WORLD]"
                  Molecules RecDim_MDLString Lig(l!1,l!2).Rec(a!1).Rec(a!2)                           # Should be: "COUNT[Rec(a!1).Lig(l!1,l!2).Rec(a!2), WORLD]"
                  Molecules RecRecLigLyn_MDLString Rec(a!1,b).Lig(l!1,l!2).Rec(a!2,b!3).Lyn(SH2,U!3)  # Should be: "COUNT[Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b!3).Rec(a!1,b), WORLD]"
                  Molecules RecPgamma_MDLString Rec(g~pY), Rec(g~pY!+)                                # Should be: "COUNT[Rec(g~pY),WORLD] + COUNT[Rec(g~pY!+), WORLD]"
                  Molecules RecSyk_MDLString Syk(tSH2!1).Rec(g~pY!1)                                  # Should be: "COUNT[Rec(g~pY!1).Syk(tSH2!1), WORLD]"
                  Molecules RecSykPS_MDLString Syk(a~pY,tSH2!1).Rec(g~pY!1)                           # Should be: "COUNT[Rec(g~pY!1).Syk(tSH2!1,a~pY), WORLD]"
                  Molecules Lig_MDLString Lig                                                         # Should be: "COUNT[Lig,WORLD]"
                  Molecules Lyn_MDLString Lyn                                                         # Should be: "COUNT[Lyn,WORLD]"
                end observables
                begin reaction rules
                  Rec(a) + Lig(l,l) <-> Lig(l!1,l).Rec(a!1) kp1,km1
                  Rec(b~Y) + Lyn(SH2,U) <-> Lyn(SH2,U!1).Rec(b~Y!1) kpL,kmL
                  Rec(a!1,b~Y).Lig(l!1,l!2).Rec(a!2,b~Y!3).Lyn(SH2,U!3) -> Rec(a!1,b~pY).Lig(l!1,l!2).Rec(a!2,b~Y!3).Lyn(SH2,U!3) pLb
                  Rec(a!1,g~Y).Lig(l!1,l!2).Rec(a!2,b~Y!3).Lyn(SH2,U!3) -> Rec(a!1,g~pY).Lig(l!1,l!2).Rec(a!2,b~Y!3).Lyn(SH2,U!3) pLg
                  Rec(b~pY) + Lyn(SH2,U) <-> Lyn(SH2!1,U).Rec(b~pY!1) kpLs,kmLs
                  Rec(a!1,b~Y).Lig(l!1,l!2).Rec(a!2,b~pY!3).Lyn(SH2!3,U) -> Rec(a!1,b~pY).Lig(l!1,l!2).Rec(a!2,b~pY!3).Lyn(SH2!3,U) pLbs
                  Rec(a!1,g~Y).Lig(l!1,l!2).Rec(a!2,b~pY!3).Lyn(SH2!3,U) -> Rec(a!1,g~pY).Lig(l!1,l!2).Rec(a!2,b~pY!3).Lyn(SH2!3,U) pLgs
                  Rec(g~pY) + Syk(tSH2) <-> Syk(tSH2!1).Rec(g~pY!1) kpS,kmS
                  Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,b~Y!3).Lyn(SH2,U!3).Syk(l~Y,tSH2!4) -> Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,b~Y!3).Lyn(SH2,U!3).Syk(l~pY,tSH2!4) pLS
                  Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,b~pY!3).Lyn(SH2!3,U).Syk(l~Y,tSH2!4) -> Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,b~pY!3).Lyn(SH2!3,U).Syk(l~pY,tSH2!4) pLSs
                  Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,g~pY!3).Syk(a~Y,tSH2!3).Syk(a~Y,tSH2!4) -> Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,g~pY!3).Syk(a~Y,tSH2!3).Syk(a~pY,tSH2!4) pSS
                  Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,g~pY!3).Syk(a~pY,tSH2!3).Syk(a~Y,tSH2!4) -> Rec(a!1,g~pY!4).Lig(l!1,l!2).Rec(a!2,g~pY!3).Syk(a~pY,tSH2!3).Syk(a~pY,tSH2!4) pSSs
                  Rec(b~pY) -> Rec(b~Y) dm
                  Rec(g~pY) -> Rec(g~Y) dm
                  Syk(l~pY,tSH2!+) -> Syk(l~Y,tSH2!+) dm
                  Syk(a~pY,tSH2!+) -> Syk(a~Y,tSH2!+) dm
                  Syk(l~pY,tSH2) -> Syk(l~Y,tSH2) dc
                  Syk(a~pY,tSH2) -> Syk(a~Y,tSH2) dc
                end reaction rules
                end model
                """
          
        dm = read_data_model_from_bngl_text ( bngl )

        print ( "Writing Test CellBlender Data Model to " + sys.argv[1] )
        write_data_model ( dm, sys.argv[1] )
        print ( "Wrote internal BioNetGen file to CellBlender data model \"" + sys.argv[1] + "\"" )
        # Drop into an interactive python session
        #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

    else:
        # Print the help information
        print ( "\nhelp():" )
        print ( "\n=======================================" )
        print ( "Requires 2 parameters:" )
        print ( "   bngl_file_name - A BioNetGen Language file name for input" )
        print ( "   data_model_file_name - A Data Model file name for output" )
        # print ( "Use Control-D to exit the interactive mode" )
        print ( "=======================================\n" )
