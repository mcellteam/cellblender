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

### NOTE: Portions of this were intentionally written to be more "C-like" than "Pythonic"

# This code is based on text representation that looks like this:

"""
  [0] = A (m) at (0,0,0) with peers [1, 2, 3, 4, 5, 6, 7]
  [1] = a (c) at (0.009999999776482582,0.0,0.0) with peers [0] <7,0.0>
  [2] = a (c) at (-0.009999999776482582,0.0,0.0) with peers [0] <7,0.0>
  [3] = a (c) at (0.0,0.009999999776482582,0.0) with peers [0] <7,0.0>
  [4] = a (c) at (0.0,-0.009999999776482582,0.0) with peers [0] <7,0.0>
  [5] = a (c) at (0.0,0.0,0.009999999776482582) with peers [0] <7,0.0>
  [6] = a (c) at (0.0,0.0,-0.009999999776482582) with peers [0, 9] <7,0.0>
  [7] = a (k) at (0.0,0.0,0.03) with peers [0]
  [8] = A (m) at (-6.12323385887182e-19,0.0,-0.019999999552965164) with peers [9, 10, 11, 12, 13, 14, 15]
  [9] = a (c) at (0.0,0.0,-0.009999999776482582) with peers [8, 6] <15,0.0>
  [10] = a (c) at (-1.224646771774364e-18,0.0,-0.029999999329447746) with peers [8] <15,0.0>
  [11] = a (c) at (0.009999999776482582,6.123233858871821e-19,-0.019999999552965164) with peers [8] <15,0.0>
  [12] = a (c) at (-0.009999999776482582,-6.123233858871821e-19,-0.019999999552965164) with peers [8] <15,0.0>
  [13] = a (c) at (-1.224646771774364e-18,0.009999999776482582,-0.019999999552965164) with peers [8] <15,0.0>
  [14] = a (c) at (9.62964972193618e-35,-0.009999999776482582,-0.019999999552965164) with peers [8, 17] <15,0.0>
  [15] = a (k) at (-2.4492935846082116e-18,0.03,-0.019999999552965164) with peers [8]
  [16] = A (m) at (-6.123233858871819e-19,-0.019999999552965164,-0.019999999552965164) with peers [17, 18, 19, 20, 21, 22, 23]
  [17] = a (c) at (9.62964972193618e-35,-0.009999999776482582,-0.019999999552965164) with peers [16, 14] <23,0.0>
  [18] = a (c) at (-1.224646771774364e-18,-0.029999999329447746,-0.019999999552965164) with peers [16] <23,0.0>
  [19] = a (c) at (-1.224646771774364e-18,-0.019999999552965164,-0.029999999329447746) with peers [16] <23,0.0>
  [20] = a (c) at (1.925929944387236e-34,-0.019999999552965164,-0.009999999776482582) with peers [16] <23,0.0>
  [21] = a (c) at (-0.009999999776482582,-0.019999999552965164,-0.019999999552965164) with peers [16] <23,0.0>
  [22] = a (c) at (0.009999999776482582,-0.019999999552965164,-0.019999999552965164) with peers [16] <23,0.0>
  [23] = a (k) at (-0.03,-0.01999999955296516,-0.01999999955296516) with peers [16]
"""

# This example text was printed by CellBlender's MolMaker code.
# The format shown here can be used as an "interchange" format.

# This example shows a complex of 3 "A" molecules (each denoted with an "(m)").
# Each "A" molecule has 6 "normal" components and one "key" component (all named "a").
# Normal components are denoted with a "(c)" and key components are denoted with a "(k)".
# All final coordinate positions are relative to the molecule located at the origin (0,0,0).
# All molecules, components, and keys are related through their "peer" lists.
# All entries in any "peer" list refer to the item's index in the table (such as "[3]").
# Each molecule lists all of its components (both "normal" and "key") in its list of peers.
# All of a molecule's peers will be rotated and translated along with the molecule itself.
# Each non-molecule ("component" or "key") has a list of either 1 or 2 peers.
# The first peer of each non-molecule is an index to that item's molecule.
# The second peer of each non-molecule (if it exists) references a binding partner.
# The binding between molecules is done by co-locating the binding components.
# Any two bound molecules and their respective binding components are collinear.
# The angle brackets "<...>" define rotation angles about the collinear binding axis.
# A rotation angle is specified as "reference,angle" pair: <reference,angle>
# The "reference" in a rotation angle specification is an index into that molecule's table.
# A rotation "reference" may refer to either a component (c) or a key (k) in that molecule.
# Rotation Alignment Planes are defined by the ordered triplet: (molecule, component, reference).
# Rotation Alignment Planes must be defined (molecule, component, reference must not be collinear).
# Rotational Alignment between two molecules specifies an angle between their Alignment Planes.
# The binding angle between bound Alignment Planes is the sum of the two angles in each component.
# The rotation angle is interpreted as counter-clockwise viewed from its associated molecule.
# When both rotation angles are 0, the normals to the Rotation Alignment Planes are opposites.


import bpy
from bpy.props import StringProperty
from bpy.props import BoolProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import EnumProperty
from bpy.props import FloatVectorProperty
from bpy.props import IntVectorProperty
from bpy.props import CollectionProperty
from bpy.props import PointerProperty

from bpy.app.handlers import persistent

import math
import mathutils



bl_info = {
	"name": "Molecule Maker",
	"author": "Bob Kuczewski",
	"version": (1,1,0),
	"blender": (2,5,7),
	"location": "View 3D > Edit Mode > Tool Shelf",
	"description": "Generate a Molecule",
	"warning" : "",
	"wiki_url" : "http://mcell.org",
	"tracker_url" : "",
	"category": "Add Mesh",
}


def checked_print ( s ):
  context = bpy.context
  mcell = context.scene.mcell
  molmaker = mcell.molmaker
  if molmaker.print_debug:
    print ( s )



def update_available_scripts ( molmaker ):
  # Delete current scripts list
  while molmaker.molecule_texts_list:
    molmaker.molecule_texts_list.remove(0)
  # Find the current internal scripts and add them to the list
  for txt in bpy.data.texts:
     checked_print ( "\n" + txt.name + "\n" + txt.as_string() + "\n" )
     if True or (txt.name[-3:] == ".py"):
        molmaker.molecule_texts_list.add()
        index = len(molmaker.molecule_texts_list)-1
        molmaker.molecule_texts_list[index].name = txt.name

  while molmaker.comp_loc_texts_list:
    molmaker.comp_loc_texts_list.remove(0)
  # Find the current internal scripts and add them to the list
  for txt in bpy.data.texts:
     checked_print ( "\n" + txt.name + "\n" + txt.as_string() + "\n" )
     if True or (txt.name[-3:] == ".py"):
        molmaker.comp_loc_texts_list.add()
        index = len(molmaker.comp_loc_texts_list)-1
        molmaker.comp_loc_texts_list[index].name = txt.name

class MolMaker_OT_update_files(bpy.types.Operator):
  bl_idname = "mol.update_files"
  bl_label = "Refresh Files"
  bl_description = "Refresh the list of available script files"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    molmaker = context.scene.mcell.molmaker
    update_available_scripts ( molmaker )
    return {'FINISHED'}


# This one is called by Build 2D and Build 3D
def read_molcomp_data_from_text ( fdata ):
  ldata = [ l.strip() for l in fdata.split('\n') if len(l.strip()) > 0 ]
  ldata = [ l for l in ldata if not l.startswith('#') ]

  molcomp_list = []
  for l in ldata:
    mc = { # 'line':l,
      'ftype':'c',
      'has_coords':False,
      'is_final':False,
      'coords':[0,0,0],
      'name':"",
      'graph_string':"",
      'peer_list':[],
      'key_list':[],
      'angle': 0,
    }
    mc['name'] = l.split("=")[1].split('(')[0].strip()
    mc['ftype'] = l.split('(')[1][0]   # Pull out the type (m or c or k)
    mc['coords'] = eval ( '[' + l.split('(')[2].split(')')[0] + ']' )

    peer_part = l.split('with peers')[1].strip()
    if '[' in peer_part:
      peers = peer_part.split('[')[1].split(']')[0].split(',')
      peers = [ p for p in peers if len(p) > 0 ]  # Remove any empty peers
      for p in peers:
        mc['peer_list'].append ( int(p) )

    if '<' in peer_part:
      keys = peer_part.split('<')[1].split('>')[0].split(',')
      if mc['ftype'] == 'm':
        # Molecules have a plain list of keys to be transformed along with the molecule
        keys = [ k for k in keys if len(k) > 0 ]  # Remove any empty keys
        for k in keys:
          mc['key_list'].append ( int(k) )
      elif mc['ftype'] == 'c':
        # Components have a key and an optional angle referenced to that key
        if len(keys) == 1:
          mc['key_list'].append ( int(keys[0]) )
          mc['angle'] = 0.0
        elif len(keys) == 2:
          mc['key_list'].append ( int(keys[0]) )
          mc['angle'] = ( float(keys[1]) )
        else:
          print ( "Expected <KeyIndex [, Angle]> for " + mc['name'] + ", but got " + peer_part.split('<')[1] )

    molcomp_list.append ( mc )

  return molcomp_list


'''
MolDef Text File Format:
# Type M C      x     y      z                 rfx rfy rfz  Unused
XYZRef T t    0.01  0.00 -0.007071067811865476  0   0   0   0
XYZRef T t   -0.01  0.00 -0.007071067811865476  0   0   0   0
XYZRef T t    0.00  0.01  0.007071067811865476  0   0   0   0
XYZRef T t    0.00 -0.01  0.007071067811865476  0   0   0   0

XYZRef B t    0.01  0.00 -0.007071067811865476  0   0   0   0
XYZRef B t   -0.01  0.00 -0.007071067811865476  0   0   0   0
XYZRef B t    0.00  0.01  0.007071067811865476  0   0   0   0
XYZRef B t    0.00 -0.01  0.007071067811865476  0   0   0   0

XYZRef C c    0.00  0.01  -0.002                0   0   0   0
XYZRef C c    0.00 -0.01   0.002                0   0   0   0
'''

def update_molcomp_list_from_defs ( context, molcomp_list, moldef_text, build_as_3D ):

  mcell = context.scene.mcell
  mcell_mols = mcell.molecules.molecule_list
  molmaker = mcell.molmaker

  if moldef_text == None:
    # Try reading from a file
    if molmaker.comp_loc_text_name in bpy.data.texts:
      # There is a component location definition text
      checked_print ( "Read component definition text named " + molmaker.comp_loc_text_name )
      # Read the component definitions
      moldef_text = bpy.data.texts[molmaker.comp_loc_text_name].as_string()

  if moldef_text != None:
    # There is a component location definition text

    # Set the has_coords flag to false on each component of each molecule
    for mc in molcomp_list:
      if mc['ftype'] == 'm':
        mc['coords'] = [0,0,0]
        mc['has_coords'] = False
      else:
        mc['has_coords'] = False

    # Read the component definitions
    ldata = moldef_text
    comploc_lines = [ l.strip() for l in ldata.split('\n') if len(l.strip()) > 0 ]
    comploc_lines = [ l for l in comploc_lines if not l.startswith('#') ]

    mol_comp_loc_dict = {}
    for cll in comploc_lines:
      cl_parts = [ p.strip() for p in cll.split() if len(p.strip()) > 0 ]
      cl_type      = cl_parts[0]
      cl_mol_name  = cl_parts[1]
      cl_comp_name = cl_parts[2]
      cl_x         = float(cl_parts[3])
      cl_y         = float(cl_parts[4])
      cl_z         = float(cl_parts[5])
      cl_refx      = float(cl_parts[6])
      cl_refy      = float(cl_parts[7])
      cl_refz      = float(cl_parts[8])
      if not build_as_3D:
        checked_print ( "Setting z to zero for " + cl_mol_name + "." + cl_comp_name )
        cl_z       = 0.0
        cl_refz    = 0.0

      if not (cl_mol_name in mol_comp_loc_dict):
        # Make a list for this mol name
        mol_comp_loc_dict[cl_mol_name] = []
      # Append the current component definition to the list for this molecule
      mol_comp_loc_dict[cl_mol_name].append ( { 'cname':cl_comp_name, 'coords':[cl_x, cl_y, cl_z], 'ref':[cl_refx, cl_refy, cl_refz], 'assigned':False } )

    # Assign the component locations by molecule
    for mc in molcomp_list:
      # Only assign to components connected to molecules
      if (mc['ftype']=='m') and (len(mc['peer_list']) > 0):
        # Clear out the usage for this molecule in the component location table
        for c in mol_comp_loc_dict[mc['name']]:
          checked_print ( " Clearing assigned for " + c['cname'] + " with coords: " + str(c['coords']) )
          c['assigned'] = False
        # Sweep through all the components for this molecule
        checked_print ( " Assigning coordinates to components in mol " + mc['name'] )
        for pi in mc['peer_list']:
          # Only assign to components that don't have coords
          checked_print ( "   Checking peer " + str(pi) )
          if not molcomp_list[pi]['has_coords']:
            # Sweep through the component name list looking for an unassigned match
            for c in mol_comp_loc_dict[mc['name']]:
              if not c['assigned']:
                if c['cname'] == molcomp_list[pi]['name']:
                  molcomp_list[pi]['coords'] = [ cc for cc in c['coords'] ]
                  checked_print ( "          Assigning coordinates: " + str(molcomp_list[pi]['coords']) )
                  molcomp_list[pi]['has_coords'] = True
                  c['assigned'] = True
                  break


# This is called directly by the "build as is" operator.
# The SphereCyl format is simpler and intended for rendering.
# The SphereCyl format only contains Spheres ("SphereList") and Cylinders ("CylList").
def read_molcomp_data_SphereCyl ( fdata ):
  ldata = [ l.strip() for l in fdata.split('\n') if len(l.strip()) > 0 ]
  ldata = [ l for l in ldata if not l.startswith('#') ]
  SphereCyl_data = { 'Version':1.1, 'SphereList':[], 'CylList':[], 'FaceList':[] }
  this_index = 0
  for l in ldata:
    checked_print ( "Line: " + l )
    m = { 'name':'', 'loc':[0,0,0], 'r':1, 'c':'MolMaker_mol', 'ftype':'' }
    m['name'] = l.split("=")[1].split('(')[0].strip()
    m['ftype'] = l.split('(')[1][0]   # Pull out the type (m or c or k)
    if m['ftype'] == 'm':
      m['r'] = 0.005
      peer_part = l.split('with peers')[1].strip()
      if '[' in peer_part:
        peers = peer_part.split('[')[1].split(']')[0].split(',')
        peers = [ p for p in peers if len(p) > 0 ]  # Remove any empty peers
        for p in peers:
          SphereCyl_data['CylList'].append ( [this_index, int(p), 0.001] )  # Add the connecting bond cylinder
          checked_print ( "  Bond: " + str(this_index) + " " + p.strip() )
    elif m['ftype'] == 'c':
      m['r'] = 0.0025
      m['c'] = 'MolMaker_comp'
    elif m['ftype'] == 'k':
      m['r'] = 0.0015
      m['c'] = 'MolMaker_key'
    m['loc'] = eval ( '[' + l.split('(')[2].split(')')[0] + ']' )
    SphereCyl_data['SphereList'].append ( m )
    this_index += 1
  return SphereCyl_data


# This converts MolComp format to SphereCyl format for simple 3D rendering.
def MolComp_to_SphereCyl ( molcomp_list, build_as_3D ):
  SphereCyl_data = { 'Version':1.1, 'SphereList':[], 'CylList':[], 'FaceList':[] }
  this_index = 0
  for mc in molcomp_list:
    m = { 'name':mc['name'], 'loc':mc['coords'], 'r':1, 'c':'MolMaker_mol', 'ftype':mc['ftype'] }
    if mc['ftype'] == 'm':
      m['r'] = 0.005
      if len(mc['peer_list']) > 0:
        peers = mc['peer_list']
        for p in peers:
          if molcomp_list[int(p)]['ftype'] != 'k':
            SphereCyl_data['CylList'].append ( [this_index, int(p), 0.001] )  # Add the connecting bond cylinder
          if build_as_3D and len(molcomp_list[int(p)]['key_list']) > 0:
            # This component has a key
            k = molcomp_list[int(p)]['key_list'][0]
            SphereCyl_data['FaceList'].append ( [ mc['coords'], molcomp_list[p]['coords'], molcomp_list[k]['coords'] ] ) # , [0.01,0.01,0.0 1] ] )
    elif mc['ftype'] == 'c':
      m['r'] = 0.0025
      m['c'] = 'MolMaker_comp'
    elif mc['ftype'] == 'k':
      m['r'] = 0.0015
      m['c'] = 'MolMaker_key'
    SphereCyl_data['SphereList'].append ( m )
    this_index += 1
  return SphereCyl_data



def dump_molcomp_list ( molcomp_list ):
  i = 0
  for mc in molcomp_list:
    mc_str = "[" + str(i) + "] = " + mc['name'] + " (" + mc['ftype'] + ") at (" + str(mc['coords'][0]) + "," + str(mc['coords'][1]) + "," + str(mc['coords'][2]) + ") with peers " + str(mc['peer_list'])
    if len(mc['key_list']) > 0:
      mc_str += " <" + str(mc['key_list'][0]) + "," + str(mc['angle']) + ">"
    checked_print ( mc_str )
    i += 1


class MolMaker_OT_build_as_is(bpy.types.Operator):
  bl_idname = "mol.build_as_is"
  bl_label = "Build As Is"
  bl_description = "Build a molecule from the coordinates in the file"
  bl_options = {'REGISTER', 'UNDO'}


  def execute(self, context):
    checked_print ( "Build Molecule from values in file" )
    molmaker = context.scene.mcell.molmaker
    fdata = bpy.data.texts[molmaker.molecule_text_name].as_string()
    checked_print ( "Read:\n" + fdata )
    mol_data = read_molcomp_data_SphereCyl ( fdata )

    new_blender_mol_from_SphereCyl_data ( context, mol_data, show_key_planes=molmaker.show_key_planes )

    return {'FINISHED'}


def get_distributed_sphere_points ( num_points ):
  points = None
  if num_points == 0:     # Define the single point along the x axis
    points = [ ]
  elif num_points == 1:     # Define the single point along the x axis
    points = [ [ 1, 0, 0 ] ]
  elif num_points == 2:   # Define the two points along the x axis
    points = [ [ 1, 0, 0 ], [ -1, 0, 0 ] ]
  elif num_points == 3:   # Define an equilateral triangle in the x-y plane with one point on x axis
    sr3o2 = math.sqrt(3.0) / 2.0
    points = [ [ 1, 0, 0 ], [ -0.5, sr3o2, 0 ], [ -0.5, -sr3o2, 0 ] ]
  elif num_points == 4:   # Define the points on a tetrahedron
    oosr2 = 1.0 / math.sqrt(2.0)
    points = [ [ 1, 0, -oosr2 ], [ -1, 0, -oosr2 ], [ 0, 1, oosr2 ], [ 0, -1, oosr2 ] ]
  elif num_points == 5:   # The "best" answer isn't clear, so place one on each pole and 3 around the "equator"
    sr3o2 = math.sqrt(3.0) / 2.0
    points = [ [ 0, 0, 1 ], [ 1, 0, 0 ], [ -0.5, sr3o2, 0 ], [ -0.5, -sr3o2, 0 ], [ 0, 0, -1 ] ]
  elif num_points == 6:   # Define 2 points on each axis (x, y, z)
    points = [
      [ 1, 0, 0 ],
      [-1, 0, 0 ],
      [ 0, 1, 0 ],
      [ 0,-1, 0 ],
      [ 0, 0, 1 ],
      [ 0, 0,-1 ] ]
  elif num_points == 8:   # Define 8 points at the corners of a cube
    d = 1.0 / math.sqrt(3)
    points = [
      [  d,  d,  d ],
      [  d,  d, -d ],
      [  d, -d,  d ],
      [  d, -d, -d ],
      [ -d,  d,  d ],
      [ -d,  d, -d ],
      [ -d, -d,  d ],
      [ -d, -d, -d ] ]
  else:   # Use the Fibonacci Sphere Algorithm ("Golden Spiral") for any undefined number of points
    points = [ [0,0,0] for i in range(num_points) ]
    rnd = 1
    offset = 2.0 / num_points
    increment = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(num_points):
      y = ((i * offset) -1) + (offset / 2)
      r = math.sqrt ( 1 - math.pow(y,2) )
      phi = ( (i+rnd) % num_points ) * increment

      x = math.cos(phi) * r
      z = math.sin(phi) * r
      points[i][0] = x
      points[i][1] = y
      points[i][2] = z
  return ( points )


def set_component_positions_3D ( mc ):
  scale = 0.02;
  for mi in range(len(mc)):
    if mc[mi]['ftype'] == 'm':
      #### fprintf ( stdout, "Setting component positions for %s\n", mc[mi].name );
      mc[mi]['coords'] = [0,0,0]
      # Because the molecule's peer list includes keys, they must be removed by creating a separate list of components only
      component_index_list = [ ci for ci in range(len(mc[mi]['peer_list'])) if mc[mc[mi]['peer_list'][ci]]['ftype'] == 'c' ]
      num_points = len(component_index_list)
      points = get_distributed_sphere_points ( num_points )
      for ci in component_index_list:
        mc[mc[mi]['peer_list'][ci]]['coords'][0] = scale * points[ci][0];
        mc[mc[mi]['peer_list'][ci]]['coords'][1] = scale * points[ci][1];
        mc[mc[mi]['peer_list'][ci]]['coords'][2] = scale * points[ci][2];
        #### fprintf ( stdout, "  Component %s is at (%g,%g)\n", mc[mc[mi].peers[ci]].name, mc[mc[mi].peers[ci]].x, mc[mc[mi].peers[ci]].y );
    elif mc[mi]['ftype'] == 'k':
      # Set the rotation keys straight up in Z?
      #mc[mi]['coords'][0] = 0
      #mc[mi]['coords'][1] = 0
      #mc[mi]['coords'][2] = 1 * scale
      # Actually, do nothing while testing
      pass


def set_component_positions_2D ( mc ):
  scale = 0.02;
  for mi in range(len(mc)):
    if mc[mi]['ftype'] == 'm':
      #### fprintf ( stdout, "Setting component positions for %s\n", mc[mi].name );
      mc[mi]['coords'] = [0,0,0]
      # Because the molecule's peer list includes keys, they must be removed by creating a separate list of components only
      component_index_list = [ ci for ci in range(len(mc[mi]['peer_list'])) if mc[mc[mi]['peer_list'][ci]]['ftype'] == 'c' ]
      for ci in component_index_list:
        angle = 2 * math.pi * ci / len(component_index_list)
        mc[mc[mi]['peer_list'][ci]]['coords'][0] = scale * math.cos(angle)
        mc[mc[mi]['peer_list'][ci]]['coords'][1] = scale * math.sin(angle)
        mc[mc[mi]['peer_list'][ci]]['coords'][2] = 0
        #### fprintf ( stdout, "  Component %s is at (%g,%g)\n", mc[mc[mi].peers[ci]].name, mc[mc[mi].peers[ci]].x, mc[mc[mi].peers[ci]].y );
    elif mc[mi]['ftype'] == 'k':
      # For 2D, the rotation keys should be straight up in Z
      mc[mi]['coords'][0] = 0
      mc[mi]['coords'][1] = 0
      mc[mi]['coords'][2] = 1 * scale



def bind_molecules_at_components ( mc, fixed_comp_index, var_comp_index, build_as_3D, include_rotation=True ):
  # Bind these two molecules by aligning their axes and shifting to align their components
  # num_parts = len(mc)

  checked_print ( "  Binding " + str(mc[fixed_comp_index]['name']) + " to " + str(mc[var_comp_index]['name']) );
  ##### dump_molcomp_array(mc,num_parts);

  fixed_mol_index = mc[fixed_comp_index]['peer_list'][0]
  var_mol_index = mc[var_comp_index]['peer_list'][0]

  fixed_vec = []
  var_vec = []

  fixed_vec.append   ( mc[fixed_comp_index]['coords'][0] - mc[fixed_mol_index]['coords'][0] )
  fixed_vec.append   ( mc[fixed_comp_index]['coords'][1] - mc[fixed_mol_index]['coords'][1] )
  var_vec.append     ( mc[  var_comp_index]['coords'][0] - mc[  var_mol_index]['coords'][0] )
  var_vec.append     ( mc[  var_comp_index]['coords'][1] - mc[  var_mol_index]['coords'][1] )
  if build_as_3D:
    fixed_vec.append ( mc[fixed_comp_index]['coords'][2] - mc[fixed_mol_index]['coords'][2] )
    var_vec.append   ( mc[  var_comp_index]['coords'][2] - mc[  var_mol_index]['coords'][2] )

  fixed_mag = None
  var_mag   = None

  if build_as_3D:
    fixed_mag = math.sqrt ( (fixed_vec[0]*fixed_vec[0]) + (fixed_vec[1]*fixed_vec[1]) + (fixed_vec[2]*fixed_vec[2]) )
    var_mag   = math.sqrt ( (  var_vec[0]*  var_vec[0]) + (  var_vec[1]*  var_vec[1]) + (  var_vec[2]*  var_vec[2]) )
  else:
    fixed_mag = math.sqrt ( (fixed_vec[0]*fixed_vec[0]) + (fixed_vec[1]*fixed_vec[1]) )
    var_mag   = math.sqrt ( (  var_vec[0]*  var_vec[0]) + (  var_vec[1]*  var_vec[1]) )

  dot_prod = None
  if build_as_3D:
    dot_prod = (fixed_vec[0] * var_vec[0]) + (fixed_vec[1] * var_vec[1]) + (fixed_vec[2] * var_vec[2])
  else:
    dot_prod = (fixed_vec[0] * var_vec[0]) + (fixed_vec[1] * var_vec[1])


  # In general, the magnitudes should be checked for 0.
  # However, in this case, they were generated as non-zero.
  norm_dot_prod = dot_prod / ( fixed_mag * var_mag )

  # Ensure that the dot product is a legal argument for the "acos" function:
  if norm_dot_prod >  1:
    print ( "Numerical Warning: normalized dot product " + str( ) + " was greater than 1" )
    norm_dot_prod =  1
  if norm_dot_prod < -1:
    print ( "Numerical Warning: normalized dot product " + str(norm_dot_prod) + " was less than 11" )
    norm_dot_prod = -1

  ##### fprintf ( stdout, "norm_dot_prod = %g\n", norm_dot_prod );
  angle = math.acos ( norm_dot_prod )
  ##### fprintf ( stdout, "Angle (from acos) = %g\n", angle );

  if not build_as_3D:
    # Try using a 2D "cross product" to fix the direction issue
    ##### fprintf ( stdout, "2D Cross of (%g,%g) X (%g,%g) = %g\n", fixed_vec[0], fixed_vec[1], var_vec[0], var_vec[1], (fixed_vec[0] * var_vec[1]) - (fixed_vec[1] * var_vec[0]) );
    if ( (fixed_vec[0] * var_vec[1]) - (fixed_vec[1] * var_vec[0]) ) > 0:
      angle = -angle
  else:
    # This seems to be required to get everything right:
    angle = -angle

  # Reverse the direction since we want the components attached to each other
  angle = math.pi + angle;

  # Bound the angle between -PI and PI
  while angle > math.pi:
    angle = angle - (2 * math.pi)
  while angle <= -math.pi:
    angle = angle + (2 * math.pi)

  #angle = -angle;

  ##### fprintf ( stdout, "Final corrected angle = %g\n", angle );

  ##### fprintf ( stdout, "Binding between f(%s: %g,%g) and v(%s: %g,%g) is at angle %g deg\n", mc[fixed_comp_index].name, fixed_vec[0], fixed_vec[1], mc[var_comp_index].name, var_vec[0], var_vec[1], 180*angle/math.pi );

  # Rotate all of the components of the var_mol_index by the angle
  ca = math.cos(angle)
  sa = math.sin(angle)

  if build_as_3D:
    cross_prod = [ (fixed_vec[1] * var_vec[2]) - (fixed_vec[2] * var_vec[1]),
                   (fixed_vec[2] * var_vec[0]) - (fixed_vec[0] * var_vec[2]),
                   (fixed_vec[0] * var_vec[1]) - (fixed_vec[1] * var_vec[0]) ]
    norm_cross_prod = [ cp / ( fixed_mag * var_mag ) for cp in cross_prod ]

    xpx = norm_cross_prod[0]
    xpy = norm_cross_prod[1]
    xpz = norm_cross_prod[2]

    axis_length = math.sqrt( (xpx*xpx) + (xpy*xpy) + (xpz*xpz) )

    R = None

    if axis_length < 1e-30:
        # Can't compute a meaningful unit vector to use for rotation matrix or quaternion
        if norm_dot_prod < 0:
          R = [ [ 1, 0, 0 ],
                [ 0, 1, 0 ],
                [ 0, 0, 1 ] ]
        else:
          R = [ [ -1,  0,  0 ],
                [  0, -1,  0 ],
                [  0,  0, -1 ] ]

    else:

        ux = xpx / axis_length
        uy = xpy / axis_length
        uz = xpz / axis_length

        if True:  # Build the rotation matrix directly

          # Build a 3D rotation matrix
          omca = 1 - ca

          R = [ [ca + (ux*ux*omca), (ux*uy*omca) - (uz*sa), (ux*uz*omca) + (uy*sa)],
                [(uy*ux*omca) + (uz*sa), ca + (uy*uy*omca), (uy*uz*omca) - (ux*sa)],
                [(uz*ux*omca) - (uy*sa), (uz*uy*omca) + (ux*sa), ca + (uz*uz*omca)] ]

        else:  # Build the rotation matrix from a quaternion

          s2 = math.sin(angle/2)
          c2 = math.cos(angle/2)

          q  = [ c2,  s2*ux,  s2*uy,  s2*uz ]
          # qconj = [ c2, -s2*ux, -s2*uy, -s2*uz ]

          # Create convenience variables for components and squares

          qr = q[0]
          qi = q[1]
          qj = q[2]
          qk = q[3]

          qi2 = qi * qi
          qj2 = qj * qj
          qk2 = qk * qk

          # Create the rotation matrix itself from the quaternion

          R = [ [     1-(2*(qj2+qk2)), 2*((qi*qj)-(qk*qr)), 2*((qi*qk)+(qj*qr)) ],
                [ 2*((qi*qj)+(qk*qr)),     1-(2*(qi2+qk2)), 2*((qj*qk)-(qi*qr)) ],
                [ 2*((qi*qk)-(qj*qr)), 2*((qj*qk)+(qi*qr)),     1-(2*(qi2+qj2)) ] ]

    ##### fprintf ( stdout, "Rotating component positions for %s by %g\n", mc[var_mol_index].name, 180*angle/math.pi );
    # for (int ci=0; ci<mc[var_mol_index].num_peers; ci++) {
    for ci in range ( len(mc[var_mol_index]['peer_list']) ):
      ##### fprintf ( stdout, "  Component %s before is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
      x = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0]
      y = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1]
      z = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][2]
      mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0] = (R[0][0]*x) + (R[0][1]*y) + (R[0][2]*z)
      mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1] = (R[1][0]*x) + (R[1][1]*y) + (R[1][2]*z)
      mc[mc[var_mol_index]['peer_list'][ci]]['coords'][2] = (R[2][0]*x) + (R[2][1]*y) + (R[2][2]*z)
      ##### fprintf ( stdout, "  Component %s after  is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
    for ci in range ( len(mc[var_mol_index]['key_list']) ):
      ##### fprintf ( stdout, "  Component %s before is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
      x = mc[mc[var_mol_index]['key_list'][ci]]['coords'][0]
      y = mc[mc[var_mol_index]['key_list'][ci]]['coords'][1]
      z = mc[mc[var_mol_index]['key_list'][ci]]['coords'][2]
      mc[mc[var_mol_index]['key_list'][ci]]['coords'][0] = (R[0][0]*x) + (R[0][1]*y) + (R[0][2]*z)
      mc[mc[var_mol_index]['key_list'][ci]]['coords'][1] = (R[1][0]*x) + (R[1][1]*y) + (R[1][2]*z)
      mc[mc[var_mol_index]['key_list'][ci]]['coords'][2] = (R[2][0]*x) + (R[2][1]*y) + (R[2][2]*z)
      ##### fprintf ( stdout, "  Component %s after  is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
  else:

    R = [ [ca, -sa],
          [sa,  ca] ]

    ##### fprintf ( stdout, "Rotating component positions for %s by %g\n", mc[var_mol_index].name, 180*angle/math.pi );
    # for (int ci=0; ci<mc[var_mol_index].num_peers; ci++) {
    for ci in range ( len(mc[var_mol_index]['peer_list']) ):
      ##### fprintf ( stdout, "  Component %s before is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
      x = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0];
      y = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1];
      mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0] = (R[0][0]*x) + (R[0][1]*y)
      mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1] = (R[1][0]*x) + (R[1][1]*y)
      ##### fprintf ( stdout, "  Component %s after  is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
    for ci in range ( len(mc[var_mol_index]['key_list']) ):
      ##### fprintf ( stdout, "  Component %s before is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
      x = mc[mc[var_mol_index]['key_list'][ci]]['coords'][0];
      y = mc[mc[var_mol_index]['key_list'][ci]]['coords'][1];
      mc[mc[var_mol_index]['key_list'][ci]]['coords'][0] = (R[0][0]*x) + (R[0][1]*y)
      mc[mc[var_mol_index]['key_list'][ci]]['coords'][1] = (R[1][0]*x) + (R[1][1]*y)
      ##### fprintf ( stdout, "  Component %s after  is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );


  # Now the molecules are aligned as they should be except for rotation along their bonding axis

  if build_as_3D and include_rotation:

    # dump_molcomp_list ( mc )

    # Rotate the variable molecule along its bonding axis to align based on the rotation key angle

    checked_print ( "Final Rotation:" )
    checked_print ( "  Fixed mol " + str(fixed_mol_index) + " binding to Var mol " + str(var_mol_index) )
    checked_print ( "  Fixed component " + str(fixed_comp_index) + " binding to Var component " + str(var_comp_index) )

    fixed_key_index = int(mc[fixed_comp_index]['key_list'][0])
    var_key_index = int(mc[var_comp_index]['key_list'][0])

    checked_print ( "  Fixed component key: " + str(fixed_key_index) + ", Var component key: " + str(var_key_index) )

    fixed_req_bond_angle = mc[fixed_comp_index]['angle']
    var_req_bond_angle = mc[var_comp_index]['angle']

    checked_print ( "  Fixed angle = " + str(fixed_req_bond_angle) + ", Var angle = " + str(var_req_bond_angle) )

    # fixed_vcomp will be the vector from the fixed molecule to the fixed component
    fixed_vcomp = []
    for i in range(3):
      fixed_vcomp.append ( mc[fixed_comp_index]['coords'][i] - mc[fixed_mol_index]['coords'][i] )

    # var_vcomp will be the vector from the var molecule to the var component
    var_vcomp = []
    for i in range(3):
      var_vcomp.append ( mc[var_comp_index]['coords'][i] - mc[var_mol_index]['coords'][i] )

    # fixed_vkey will be the vector from the fixed molecule to the fixed key
    fixed_vkey = []
    for i in range(3):
      fixed_vkey.append ( mc[fixed_key_index]['coords'][i] - mc[fixed_mol_index]['coords'][i] )

    # var_vkey will be the vector from the var molecule to the var key
    var_vkey = []
    for i in range(3):
      var_vkey.append ( mc[var_key_index]['coords'][i] - mc[var_mol_index]['coords'][i] )

    checked_print ( "  Fixed vcomp = " + str(fixed_vcomp) )
    checked_print ( "  Var   vcomp = " + str(var_vcomp) )
    checked_print ( "  Fixed vkey  = " + str(fixed_vkey) )
    checked_print ( "  Var vkey    = " + str(var_vkey) )

    # Use the cross product to get the normal to the fixed molecule-component-key plane
    fixed_normal = [ (fixed_vcomp[1] * fixed_vkey[2]) - (fixed_vcomp[2] * fixed_vkey[1]),
                     (fixed_vcomp[2] * fixed_vkey[0]) - (fixed_vcomp[0] * fixed_vkey[2]),
                     (fixed_vcomp[0] * fixed_vkey[1]) - (fixed_vcomp[1] * fixed_vkey[0]) ]

    # Use the cross product to get the normal to the variable molecule-component-key plane
    var_normal = [ (var_vcomp[1] * var_vkey[2]) - (var_vcomp[2] * var_vkey[1]),
                   (var_vcomp[2] * var_vkey[0]) - (var_vcomp[0] * var_vkey[2]),
                   (var_vcomp[0] * var_vkey[1]) - (var_vcomp[1] * var_vkey[0]) ]

    # Get the magnitudes of the two vectors for normalization
    fixed_norm_mag = math.sqrt ( (fixed_normal[0]*fixed_normal[0]) + (fixed_normal[1]*fixed_normal[1]) + (fixed_normal[2]*fixed_normal[2]) )
    var_norm_mag   = math.sqrt ( (  var_normal[0]*  var_normal[0]) + (  var_normal[1]*  var_normal[1]) + (  var_normal[2]*  var_normal[2]) )


    # Calculate unit vectors
    fixed_unit = [ cp / fixed_norm_mag for cp in fixed_normal ]
    var_unit   = [ cp / var_norm_mag   for cp in var_normal   ]

    checked_print ( "  Fixed unit = " + str(fixed_unit) )
    checked_print ( "  Var unit = " + str(var_unit) )

    norm_dot_prod = (fixed_unit[0] * var_unit[0]) + (fixed_unit[1] * var_unit[1]) + (fixed_unit[2] * var_unit[2])

    # Ensure that the dot product is a legal argument for the "acos" function:
    if norm_dot_prod >  1:
      print ( "Numerical Warning: normalized dot product " + str(norm_dot_prod) + " was greater than 1" )
      norm_dot_prod =  1
    if norm_dot_prod < -1:
      print ( "Numerical Warning: normalized dot product " + str(norm_dot_prod) + " was less than -1" )
      norm_dot_prod = -1

    checked_print ( "  Normalized Dot Product between fixed and var is " + str(norm_dot_prod) )

    # Compute the amount of rotation to bring the planes into alignment offset by the requested bond angles
    cur_key_plane_angle = math.acos ( norm_dot_prod )

    checked_print ( "Current key plane angle = " + str(180*cur_key_plane_angle/math.pi) )

    cross_prod = [ (fixed_unit[1] * var_unit[2]) - (fixed_unit[2] * var_unit[1]),
                   (fixed_unit[2] * var_unit[0]) - (fixed_unit[0] * var_unit[2]),
                   (fixed_unit[0] * var_unit[1]) - (fixed_unit[1] * var_unit[0]) ]

    dot_cross_rot = (cross_prod[0] * var_vcomp[0]) + (cross_prod[1] * var_vcomp[1]) + (cross_prod[2] * var_vcomp[2])
    if dot_cross_rot > 0:
      cur_key_plane_angle = (2*math.pi) - cur_key_plane_angle

    checked_print ( "Current key plane angle = " + str(180*cur_key_plane_angle/math.pi) + ",  dot_cross_rot = " + str(dot_cross_rot) )


    composite_rot_angle = math.pi + (var_req_bond_angle+fixed_req_bond_angle) + cur_key_plane_angle # The "math.pi" adds 180 degrees to make the components "line up"

    checked_print ( "  Fixed angle                is = " + str(180 * fixed_req_bond_angle / math.pi) + " degrees" )
    checked_print ( "  Var angle                  is = " + str(180 * var_req_bond_angle / math.pi) + " degrees" )
    checked_print ( "  Current angle between keys is = " + str(180 * cur_key_plane_angle / math.pi) + " degrees" )
    checked_print ( "  Composite rotation angle   is = " + str(180 * composite_rot_angle / math.pi) + " degrees" )

    # Build a 3D rotation matrix along the axis of the molecule to the component
    var_vcomp_mag = math.sqrt ( (var_vcomp[0]*var_vcomp[0]) + (var_vcomp[1]*var_vcomp[1]) + (var_vcomp[2]*var_vcomp[2]) )

    var_rot_unit = [ v / var_vcomp_mag for v in var_vcomp ]
    ux = var_rot_unit[0]
    uy = var_rot_unit[1]
    uz = var_rot_unit[2]

    R = None

    if True:  # Build the rotation matrix directly

      cca = math.cos(composite_rot_angle)
      sca = math.sin(composite_rot_angle)
      omcca = 1 - cca

      R = [ [cca + (ux*ux*omcca), (ux*uy*omcca) - (uz*sca), (ux*uz*omcca) + (uy*sca)],
            [(uy*ux*omcca) + (uz*sca), cca + (uy*uy*omcca), (uy*uz*omcca) - (ux*sca)],
            [(uz*ux*omcca) - (uy*sca), (uz*uy*omcca) + (ux*sca), cca + (uz*uz*omcca)] ]

    else:  # Build the rotation matrix from a quaternion

      s2 = math.sin(composite_rot_angle/2)
      c2 = math.cos(composite_rot_angle/2)

      q  = [ c2,  s2*ux,  s2*uy,  s2*uz ]
      # qconj = [ c2, -s2*ux, -s2*uy, -s2*uz ]

      # Create convenience variables for components and squares

      qr = q[0]
      qi = q[1]
      qj = q[2]
      qk = q[3]

      qi2 = qi * qi
      qj2 = qj * qj
      qk2 = qk * qk

      # Create the rotation matrix itself from the quaternion

      R = [ [     1-(2*(qj2+qk2)), 2*((qi*qj)-(qk*qr)), 2*((qi*qk)+(qj*qr)) ],
            [ 2*((qi*qj)+(qk*qr)),     1-(2*(qi2+qk2)), 2*((qj*qk)-(qi*qr)) ],
            [ 2*((qi*qk)-(qj*qr)), 2*((qj*qk)+(qi*qr)),     1-(2*(qi2+qj2)) ] ]

    mm = bpy.context.scene.mcell.molmaker
    if (not mm.skip_rotation) or (fixed_comp_index != mm.skip_fixed_comp_index) or (var_comp_index != mm.skip_var_comp_index):

        # Apply the rotation matrix after subtracting the molecule center location from all components and keys
        for ci in range ( len(mc[var_mol_index]['peer_list']) ):
          ##### fprintf ( stdout, "  Component %s before is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
          x = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0] - mc[var_mol_index]['coords'][0]
          y = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1] - mc[var_mol_index]['coords'][1]
          z = mc[mc[var_mol_index]['peer_list'][ci]]['coords'][2] - mc[var_mol_index]['coords'][2]
          mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0] = (R[0][0]*x) + (R[0][1]*y) + (R[0][2]*z) + mc[var_mol_index]['coords'][0]
          mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1] = (R[1][0]*x) + (R[1][1]*y) + (R[1][2]*z) + mc[var_mol_index]['coords'][1]
          mc[mc[var_mol_index]['peer_list'][ci]]['coords'][2] = (R[2][0]*x) + (R[2][1]*y) + (R[2][2]*z) + mc[var_mol_index]['coords'][2]
          ##### fprintf ( stdout, "  Component %s after  is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
        for ci in range ( len(mc[var_mol_index]['key_list']) ):
          ##### fprintf ( stdout, "  Component %s before is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );
          x = mc[mc[var_mol_index]['key_list'][ci]]['coords'][0] - mc[var_mol_index]['coords'][0]
          y = mc[mc[var_mol_index]['key_list'][ci]]['coords'][1] - mc[var_mol_index]['coords'][1]
          z = mc[mc[var_mol_index]['key_list'][ci]]['coords'][2] - mc[var_mol_index]['coords'][2]
          mc[mc[var_mol_index]['key_list'][ci]]['coords'][0] = (R[0][0]*x) + (R[0][1]*y) + (R[0][2]*z) + mc[var_mol_index]['coords'][0]
          mc[mc[var_mol_index]['key_list'][ci]]['coords'][1] = (R[1][0]*x) + (R[1][1]*y) + (R[1][2]*z) + mc[var_mol_index]['coords'][1]
          mc[mc[var_mol_index]['key_list'][ci]]['coords'][2] = (R[2][0]*x) + (R[2][1]*y) + (R[2][2]*z) + mc[var_mol_index]['coords'][2]
          ##### fprintf ( stdout, "  Component %s after  is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]]['coords'][0], mc[mc[var_mol_index].peers[ci]]['coords'][1] );


  ##### dump_molcomp_array(mc,num_parts);

  # Shift the var molecule location and the locations of all of its components by the difference of the binding components

  dx = mc[fixed_comp_index]['coords'][0] - mc[var_comp_index]['coords'][0]
  dy = mc[fixed_comp_index]['coords'][1] - mc[var_comp_index]['coords'][1]
  dz = 0
  if build_as_3D:
    dz = mc[fixed_comp_index]['coords'][2] - mc[var_comp_index]['coords'][2]

  ##### fprintf ( stdout, "Shifting molecule and component positions for %s\n", mc[var_mol_index].name );
  mc[var_mol_index]['coords'][0] += dx
  mc[var_mol_index]['coords'][1] += dy
  mc[var_mol_index]['coords'][2] += dz
  #for (int ci=0; ci<mc[var_mol_index].num_peers; ci++) {
  for ci in range ( len(mc[var_mol_index]['peer_list']) ):
    mc[mc[var_mol_index]['peer_list'][ci]]['coords'][0] += dx
    mc[mc[var_mol_index]['peer_list'][ci]]['coords'][1] += dy
    mc[mc[var_mol_index]['peer_list'][ci]]['coords'][2] += dz
    ##### fprintf ( stdout, "  Component %s is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]].x, mc[mc[var_mol_index].peers[ci]]['coords'][1] );
  for ci in range ( len(mc[var_mol_index]['key_list']) ):
    mc[mc[var_mol_index]['key_list'][ci]]['coords'][0] += dx
    mc[mc[var_mol_index]['key_list'][ci]]['coords'][1] += dy
    mc[mc[var_mol_index]['key_list'][ci]]['coords'][2] += dz
    ##### fprintf ( stdout, "  Component %s is at (%g,%g)\n", mc[mc[var_mol_index].peers[ci]].name, mc[mc[var_mol_index].peers[ci]].x, mc[mc[var_mol_index].peers[ci]]['coords'][1] );

  ##### dump_molcomp_array(mc,num_parts);


  ##### fprintf ( stdout, "########## Done Binding %s to %s\n", mc[fixed_comp_index].name, mc[var_comp_index].name );



def bind_all_molecules ( molcomp_array, build_as_3D, include_rotation=True ):

  context = bpy.context
  mcell = context.scene.mcell
  molmaker = mcell.molmaker

  old_debug = molmaker.print_debug
  ## molmaker.print_debug = True
  checked_print ( "======================================================================================" )
  checked_print ( "===================================== bind_all_molecules =============================" )
  checked_print ( "======================================================================================" )
  dump_molcomp_list ( molcomp_array )
  checked_print ( "======================================================================================" )
  molmaker.print_debug = old_debug



  # Compute positions for all molecules/components in a molcomp_array
  num_parts = len(molcomp_array)

  mi=0;
  pi=0;

  # Set all molecules and components to not final
  for mi in range(num_parts):
    molcomp_array[mi]['is_final'] = False

  # Find first molecule
  found_mol = False
  for mi in range(num_parts):
    if molcomp_array[mi]['ftype'] == 'm':
      found_mol = True
      break;

  if found_mol:
    # Set this first molecule and all of its components to final
    molcomp_array[mi]['is_final'] = True
    num_peers = len(molcomp_array[mi]['peer_list'])
    for ci in range(num_peers):
      molcomp_array[molcomp_array[mi]['peer_list'][ci]]['is_final'] = True
    done = False
    while not done:
      # Look for a bond between a non-final and a final component
      done = True
      for mi in range(num_parts):
        if molcomp_array[mi]['ftype'] == 'c':
          # Only search components for bonds
          if len(molcomp_array[mi]['peer_list']) > 1:
            # This component has bonds, so search them
            for ci in range(1,len(molcomp_array[mi]['peer_list'])):  # for (int ci=1; ci<molcomp_array[mi].num_peers; ci++) {
              pi = molcomp_array[mi]['peer_list'][ci]  # Peer index
              if molcomp_array[mi]['is_final'] != molcomp_array[pi]['is_final']:
                done = False
                # One of these is final and the other is not so join them and make them all final
                fci=0  # Fixed Component Index
                vci=0  # Variable Component Index
                vmi=0  # Variable Molecule Index
                # Figure out which is fixed and which is not
                if molcomp_array[mi]['is_final']:
                  fci = mi;
                  vci = pi;
                else:
                  fci = pi;
                  vci = mi;

                # Set the variable molecule index for the bond based on the component
                vmi = molcomp_array[vci]['peer_list'][0]

                # Perform the bond (changes the locations)

                bind_molecules_at_components ( molcomp_array, fci, vci, build_as_3D, include_rotation )

                # The bonding process will have specified the placement of the variable molecule
                # Set the variable molecule and all of its components to final
                molcomp_array[vmi]['is_final'] = True
                #for (int vmici=0; vmici<molcomp_array[vmi].num_peers; vmici++) {
                for vmici in range(len(molcomp_array[vmi]['peer_list'])):
                  molcomp_array[molcomp_array[vmi]['peer_list'][vmici]]['is_final'] = True

                old_debug = molmaker.print_debug
                ## molmaker.print_debug = True
                checked_print ( "======================================================================================" )
                dump_molcomp_list ( molcomp_array )
                checked_print ( "======================================================================================" )
                molmaker.print_debug = old_debug


def build_all_mols ( context, molcomp_list, build_as_3D=True, include_rotation=True ):

  if build_as_3D:
    checked_print ( "\n\nBuilding as 3D" )
  else:
    checked_print ( "\n\nBuilding as 2D" )

  molmaker = context.scene.mcell.molmaker

  bind_all_molecules ( molcomp_list, build_as_3D, include_rotation=molmaker.include_rotation )

  if molmaker.average_coincident:
    i = 0
    for mc in molcomp_list:
      # Only average components connected to molecules
      if (mc['ftype']=='c') and (len(mc['peer_list']) > 1):
        j = mc['peer_list'][1]
        print ( "Average components " + str(i) + " and " + str(j) )
        print ( " Component: " + str([ n for n in mc.keys()]) )
        print ( "  Peer List: " + str(mc['peer_list']) + ", Coords: " + str(mc['coords']) )
        x = (molcomp_list[i]['coords'][0] + molcomp_list[j]['coords'][0]) / 2
        y = (molcomp_list[i]['coords'][1] + molcomp_list[j]['coords'][1]) / 2
        z = (molcomp_list[i]['coords'][2] + molcomp_list[j]['coords'][2]) / 2
        molcomp_list[i]['coords'][0] = x
        molcomp_list[j]['coords'][0] = x
        molcomp_list[i]['coords'][1] = y
        molcomp_list[j]['coords'][1] = y
        molcomp_list[i]['coords'][2] = z
        molcomp_list[j]['coords'][2] = z

      i += 1

  checked_print ( "======================================================================================" )
  dump_molcomp_list ( molcomp_list )
  checked_print ( "======================================================================================" )

  new_blender_mol_from_SphereCyl_data ( context, MolComp_to_SphereCyl ( molcomp_list, build_as_3D ), show_key_planes=molmaker.show_key_planes )



class MolMaker_OT_build_2D(bpy.types.Operator):
  bl_idname = "mol.rebuild_two_d"
  bl_label = "Build 2D"
  bl_description = "Build a molecule based on 2D assumption"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    checked_print ( "Build Molecule 2D" )
    molmaker = context.scene.mcell.molmaker
    moldef_text = None
    if molmaker.comp_loc_text_name in bpy.data.texts:
      moldef_text = bpy.data.texts[molmaker.comp_loc_text_name].as_string()
    fdata = bpy.data.texts[molmaker.molecule_text_name].as_string()

    molcomp_list = read_molcomp_data_from_text ( fdata )
    update_molcomp_list_from_defs ( context, molcomp_list, moldef_text, build_as_3D=False )

    set_component_positions_2D ( molcomp_list )
    build_all_mols ( context, molcomp_list, build_as_3D=False, include_rotation=molmaker.include_rotation )
    return {'FINISHED'}



class MolMaker_OT_build_3D(bpy.types.Operator):
  bl_idname = "mol.rebuild_three_d"
  bl_label = "Build 3D"
  bl_description = "Build a molecule based on 3D Definitions"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    checked_print ( "Build Molecule calculating new values from CellBlender" )
    molmaker = context.scene.mcell.molmaker
    moldef_text = None
    if molmaker.comp_loc_text_name in bpy.data.texts:
      moldef_text = bpy.data.texts[molmaker.comp_loc_text_name].as_string()
    fdata = bpy.data.texts[molmaker.molecule_text_name].as_string()

    molcomp_list = read_molcomp_data_from_text ( fdata )
    update_molcomp_list_from_defs ( context, molcomp_list, moldef_text, build_as_3D=True )

    set_component_positions_3D ( molcomp_list )
    build_all_mols ( context, molcomp_list, build_as_3D=True, include_rotation=molmaker.include_rotation )
    return {'FINISHED'}



class MolMaker_OT_to_nauty(bpy.types.Operator):
  bl_idname = "mol.to_nauty"
  bl_label = "To NAUTY"
  bl_description = "Build a NAUTY string from a BNGL string"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    print ( "Build a NAUTY string from a BNGL string" )
    molmaker = context.scene.mcell.molmaker
    return {'FINISHED'}


class MolMaker_OT_to_bngl(bpy.types.Operator):
  bl_idname = "mol.to_bngl"
  bl_label = "To BNGL"
  bl_description = "Build a BNGL string from a NAUTY string"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    print ( "Build a BNGL string from a NAUTY string" )
    molmaker = context.scene.mcell.molmaker
    ns = molmaker.nauty_string
    print ( "Original NAUTY string: " + ns )

    # Start by making a list of dictionaries to work with
    molcomp_list = [ {'s':mc.strip(),'t':mc.strip()[0]} for mc in ns.split(',') if len(mc) > 0 ]


    # Extract the names
    for item in molcomp_list:
        name = item['s'].split(':')[1]
        if '~' in name:
            name = name[0:name.find('~')]
        if '@' in name:
            name = name[0:name.find('@')]
        if '!' in name:
            name = name[0:name.find('!')]
        item['name'] = name


    # Extract the peers
    for item in molcomp_list:
        peers = []
        s = '' + item['s']
        while '!' in s:
            s = s[1+s.find('!'):]
            n = ''
            i = 0
            while (i<len(s)) and (s[i] in '0123456789'):
                n = n + s[i]
                i = i + 1
            peers.append ( int(n) )
        item['peers'] = peers


    # Extract the states
    for item in molcomp_list:
        states = []
        s = '' + item['s']
        if '~' in s:
            # print ( "~~~~~~~~" )
            ss = s[s.find('~'):s.find('!')]
            while '~' in ss:
                # print ( "ss = " + ss )  # Should always lead with a ~
                ss = ss[1+ss.find('~'):] # Should not lead with a ~
                # print ( "  ss = " + ss )
                state = ''
                if '~' in ss:
                    state = ss[0:ss.find('~')]
                    ss = ss[ss.find('~'):]
                else:
                    state = ss
                    ss = ''
                if state != 'NO_STATE':
                    states.append ( state )
        item['states'] = states


    #Extract the compartments (objects)
    for item in molcomp_list:
        s = '' + item['s']
        if '@' in s:
            # print ( "@@@@@@@@" )
            ss = s[s.find('@'):]
            # print ( "ss = " + ss )
            if '!' in ss:
                ss = ss[0:ss.find('!')]
            # print ( "  " + ss )
            item['obj'] = ss
        else:
            item['obj'] = ""


    #Assign the bond numbers
    nbn = 1
    for item in molcomp_list:
        if item['t'] == 'c':
            if len(item['peers']) == 2:
                if not ('bnum' in item):
                    item['bnum'] = nbn
                    molcomp_list[item['peers'][1]]['bnum'] = nbn
                    nbn = nbn + 1


    #Finally build the BNGL string
    bngl = ""
    for item in molcomp_list:
        if item['t'] == 'm':
            if len(bngl) > 0:
                bngl += '.'
            bngl += item['name']
            if len(item['peers']) > 0:
                bngl += "("
                for p in range(len(item['peers'])):
                    peer_num = item['peers'][p]
                    peer = molcomp_list[peer_num]
                    if p > 0:
                        bngl += ','
                    bngl += peer['name']
                    if len(peer['states']) > 0:
                        for s in peer['states']:
                            bngl += "~" + s
                    if 'bnum' in peer:
                        bngl += "!" + str(peer['bnum'])
                bngl += ")"


    # Print the molcomp_list
    print ( "" )
    print ( "Full Molecule/Component (MolComp) List:" )
    for li in molcomp_list:
        print ( "  " + str(li) )

    # Print the final BNGL string
    print ( "" )
    print ( "Final BNGL:" )
    print ( "  " + bngl )
    print ( "" )

    molmaker.bngl_string = bngl

    return {'FINISHED'}





def check_bond_index ( self, context ):
  mcell = context.scene.mcell
  molmaker = mcell.molmaker
  this_mc_index = 0
  for mc in molmaker.molcomp_items:
    if mc.bond_index < 0:
      mc.alert_string = ""
    else:
      # Check that the link is reciprocated
      if molmaker.molcomp_items[mc.bond_index].bond_index != this_mc_index:
        mc.alert_string = "Unmatched bond"
      else:
        if mc.alert_string == "Unmatched bond":
          mc.alert_string = ""
    this_mc_index += 1


def redraw_mol ( self, context ):
  mcell = context.scene.mcell
  molmaker = mcell.molmaker
  if molmaker.dynamic_rotation:
    checked_print ( "Redrawing the molecule with:" )
    checked_print ( "  self = " + str(self) )
    checked_print ( "  context = " + str(context) )
    if 'Mol Object' in context.scene.objects:
      # The following may not have deleted everything since there was progressive slowing:

      #obj = context.scene.objects['Mol Object']
      #context.scene.objects.unlink ( obj )
      #bpy.data.objects.remove ( obj )

      # Try this:
      bpy.ops.object.select_all ( action = 'DESELECT' )
      obj = context.scene.objects['Mol Object']
      obj.select = True
      bpy.ops.object.delete()

      # Still shows progressive slowing ... maybe add a purge to clear datablocks
      # save and re-open the file to clean up the data blocks
      #bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
      #bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
    build_complex_from_cellblender ( context )


class MolMakerFileNameProperty(bpy.types.PropertyGroup):
  name = StringProperty(name="Script")

class MolMakerMolCompProperty(bpy.types.PropertyGroup):
  name = StringProperty(name="Script")
  field_type = StringProperty() # Either m, c, or k (for molecule, component, or key)
  has_coords = BoolProperty()
  is_final = BoolProperty()
  coords = FloatVectorProperty ( size=3 )
  graph_string = StringProperty(default="")
  peer_list = StringProperty(default="") # Comma-separated list of indexes
  key_list = StringProperty(default="")  # Comma-separated list of indexes
  angle = FloatProperty(name="Bond Angle", step=0.5, precision=3, update=redraw_mol)
  bond_index = IntProperty(name="Bond Index", default=-1, update=check_bond_index)
  key_index = IntProperty(default=-1)
  alert_string = StringProperty(default="")


class MolMaker_OT_refresh_mol_def(bpy.types.Operator):
  bl_idname = "mol.refresh_mol_def"
  bl_label = "Layout Parts"
  bl_description = "Layout Components for this Complex"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    mcell = context.scene.mcell
    molmaker = mcell.molmaker
    parts = molmaker.molecule_definition.split(".")
    checked_print ( "Update the molecule/component list with " + str(parts) )
    while len(molmaker.molcomp_items) > 0:
      molmaker.molcomp_items.remove ( 0 )
    cur_mol_index = 0
    for p in parts:
      new_mol = molmaker.molcomp_items.add()
      new_mol.name = p
      new_mol.field_type = "m"
      new_mol.alert_string = ""
      new_mol.peer_list = ""
      if p in mcell.molecules.molecule_list:
        m = mcell.molecules.molecule_list[p]
        cur_comp_index = cur_mol_index + 1
        for cindex in range(len(m.component_list)):
          new_comp = molmaker.molcomp_items.add()
          new_comp.name = m.component_list[cindex].component_name
          if m.component_list[cindex].is_key:
            new_comp.field_type = "k"
          else:
            new_comp.field_type = "c"
          # Link the component to the molecule
          new_comp.peer_list = str(cur_mol_index)
          if len(new_mol.peer_list) > 0:
            new_mol.peer_list = new_mol.peer_list + ','
          # Link the molecule to the component
          new_mol.peer_list = new_mol.peer_list + str(cur_comp_index)
          cur_comp_index += 1
        cur_mol_index = cur_comp_index
      else:
        new_mol.alert_string = "Undefined Molecule Name: " + p
        cur_mol_index += 1


    return {'FINISHED'}



class MolMaker_OT_chain_mols(bpy.types.Operator):
  bl_idname = "mol.chain_mol_defs"
  bl_label = "Chain Molecules"
  bl_description = "Connect Molecules to form a Chain"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    mcell = context.scene.mcell
    molmaker = mcell.molmaker
    molcomp_items = molmaker.molcomp_items
    for mol_index in range(len(molcomp_items)):
      mol = molcomp_items[mol_index]
      if mol.field_type == 'm':
        # Found a molecule, so connect the previous and next components if possible
        if (mol_index > 0) and (mol_index < (len(molcomp_items)-1)):
          # This molecule is at least between two non-molecules
          # This is where the code should search both up and down for actual components (not keys)
          # However, for now, we'll assume that there are no keys and make the bond
          prev_comp_index = mol_index-1
          while (prev_comp_index > 0) and (molcomp_items[prev_comp_index].field_type != 'c'):
            prev_comp_index += -1
          if (prev_comp_index >= 0) and (molcomp_items[prev_comp_index].field_type == 'c'):
            next_comp_index = mol_index+1
            while (next_comp_index < len(molcomp_items)) and (molcomp_items[next_comp_index].field_type != 'c'):
              next_comp_index += 1
            if (next_comp_index < len(molcomp_items)) and (molcomp_items[next_comp_index].field_type == 'c'):
              molcomp_items[prev_comp_index].bond_index = next_comp_index
              molcomp_items[next_comp_index].bond_index = prev_comp_index
    return {'FINISHED'}



def build_complex_from_cellblender ( context ):

  checked_print ( "Build Molecule calculating new values from CellBlender" )

  # Note that this assumes that the Molecules come first followed by components
  mcell = context.scene.mcell
  mcell_mols = mcell.molecules.molecule_list
  molmaker = mcell.molmaker

  mols_used = {}
  molcomp_list = []

  cur_mol_index = -1 # The Molecules must come before the components for this to work!!

  # Build the molcomp list (without coordinates) from Blender's Molecule Structure Property List

  for i in range(len(molmaker.molcomp_items)):
    checked_print ( "Current Index = " + str(i) )

    # Build the basic molcomp entry

    m = molmaker.molcomp_items[i]
    mc = {
      'name': m.name,
      'ftype':m.field_type,
      'has_coords':m.has_coords,
      'is_final':m.is_final,
      'coords':[c for c in m.coords],
      'graph_string':m.graph_string,
      'peer_list':[int(s.strip()) for s in m.peer_list.split(',') if len(s.strip()) > 0],
      'key_list':[int(s.strip()) for s in m.key_list.split(',') if len(s.strip()) > 0],
      'bond_index': m.bond_index,
      'angle': m.angle,
    }

    if m.field_type == 'm':
      # Store this molecule name in the dictionary
      cur_mol_index = i
      mols_used[m.name] = True

    if m.bond_index >= 0:
      # This is a real bond (CellBlender uses -1 for unbonded components)
      mc['peer_list'].append ( m.bond_index )

    # Build the Angle References for any components

    if m.field_type == 'c':
      cur_comp_index = (i - cur_mol_index) - 1
      comp = mcell_mols[molmaker.molcomp_items[cur_mol_index].name].component_list[cur_comp_index]
      rot_index = comp.rot_index
      if rot_index < 0:
        print ( "Warning: This bond uses a component that has no reference!!" )
      abs_rot_index = rot_index + cur_mol_index + 1
      if rot_index >= 0:
        mc['key_list'] = [ abs_rot_index ]
        mc['angle'] = m.angle

    molcomp_list.append ( mc )

  # Update the molcomp list with actual coordinates from each molecule

  # Start by building a molecule dictionary where each molecule has a list of components and their assignment status

  mol_comp_loc_dict = {}
  for mol_name in mols_used.keys():
    mol_comp_loc_dict[mol_name] = []  # This will be a list of dictionaries for each component
    cb_mol = mcell.molecules.molecule_list[mol_name]
    for cb_comp in cb_mol.component_list:
      mol_comp_loc_dict[mol_name].append ( { 'cname':cb_comp.component_name, 'coords':[cb_comp.loc_x.get_value(),cb_comp.loc_y.get_value(),cb_comp.loc_z.get_value()], 'assigned':False } )

  # Assign the component locations by molecule with matching component names
  # Keep track of which ones have already been assigned

  for mc in molcomp_list:
    # Only assign to components connected to molecules
    if (mc['ftype']=='m') and (len(mc['peer_list']) > 0):
      # Clear out the usage for this molecule in the component location table
      for c in mol_comp_loc_dict[mc['name']]:
        checked_print ( " Clearing assigned for " + c['cname'] + " with coords: " + str(c['coords']) )
        c['assigned'] = False
      # Sweep through all the components for this molecule
      checked_print ( " Assigning coordinates to components in mol " + mc['name'] )
      for peer_index in mc['peer_list']:
        # Only assign to components that don't have coords
        checked_print ( "   Checking peer " + str(peer_index) )
        if not molcomp_list[peer_index]['has_coords']:
          # Sweep through the component name list looking for an unassigned match
          for c in mol_comp_loc_dict[mc['name']]:
            if not c['assigned']:
              if c['cname'] == molcomp_list[peer_index]['name']:
                molcomp_list[peer_index]['coords'] = [ cc for cc in c['coords'] ]
                checked_print ( "          Assigning coordinates: " + str(molcomp_list[peer_index]['coords']) )
                molcomp_list[peer_index]['has_coords'] = True
                c['assigned'] = True
                break

  # Finally build the molecules from the molcomp_list

  build_all_mols ( context, molcomp_list, build_as_3D=True, include_rotation=molmaker.include_rotation )

  checked_print ( 'Built Blender model\n' )



class MolMaker_OT_build_struct(bpy.types.Operator):
  bl_idname = "mol.rebuild_with_cb"
  bl_label = "Build Structure from CellBlender"
  bl_description = "Build a molecule based on CellBlender Definitions"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    build_complex_from_cellblender ( context )
    return {'FINISHED'}

class MolMaker_OT_purge_by_reopen(bpy.types.Operator):
  bl_idname = "mol.purge_by_reopen"
  bl_label = "Purge by Re-Open"
  bl_description = "Purge datablocks by reopening"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    # save and re-open the file to clean up the data blocks
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)
    return {'FINISHED'}



class MCellMolMakerPropertyGroup(bpy.types.PropertyGroup):
  molecule_texts_list = CollectionProperty(type=MolMakerFileNameProperty, name="Molecule Texts List")
  molecule_text_name = StringProperty ( name = "Text name containing this molecule description (molcomp)" )
  comp_loc_texts_list = CollectionProperty(type=MolMakerFileNameProperty, name="Component Location Texts List")
  comp_loc_text_name = StringProperty ( name = "Text name containing optional component locations (rather than from CellBlender)" )

  molcomp_items = CollectionProperty(type=MolMakerMolCompProperty, name="MolCompList")

  molecule_definition = StringProperty ( name = "MolDef", description="Molecule Definition (such as: A.B.B.C)" )

  make_materials = BoolProperty ( default=True )
  cellblender_colors = BoolProperty ( default=True )
  show_key_planes = BoolProperty ( default=True )
  average_coincident = BoolProperty ( default=False )
  include_rotation = BoolProperty ( default=True )
  dynamic_rotation = BoolProperty ( default=False )
  print_debug = BoolProperty ( default=False )

  show_text_interface = BoolProperty ( default=False )
  show_string_interface = BoolProperty ( default=True )


  skip_rotation = BoolProperty ( default=False )
  skip_fixed_comp_index = IntProperty ( default=-1 )
  skip_var_comp_index = IntProperty ( default=-1 )

  # c:a~NO_STATE!3,c:b~NO_STATE!3,c:c~NO_STATE!3,m:A@CP!0!1!2
  # c:a~NO_STATE!7,c:a~NO_STATE!6!5,c:b~NO_STATE!7,c:b~NO_STATE!6,c:c~NO_STATE!6,c:c~NO_STATE!7!1,m:A@CP!1!3!4,m:A@CP!0!2!5,
  # c:a~NO_STATE!7,c:a~NO_STATE!6!5,c:b~NO_STATE!7,c:b~NO_STATE!6,c:c~NO_STATE!6,c:c~NO_STATE!7!1,m:A@CP!1!3!4,m:A@CP!0!2!5, c:a~NO_STATE!7,c:a~NO_STATE!6!5,c:b~NO_STATE!7,c:b~NO_STATE!6,c:c~NO_STATE!6,c:c~NO_STATE!7!1,m:A@CP!1!3!4,m:A@CP!0!2!5,
  nauty_string = StringProperty ( name = "NAUTY", default="c:a~x!19,c:a~st~y!16!11,c:a~NO_STATE!15!12,c:a~NO_STATE!17!13,c:a~NO_STATE!18!14,c:b~www!16,c:b~NO_STATE!15,c:b~NO_STATE!17,c:b~NO_STATE!18,c:b~NO_STATE!19,c:c~NO_STATE!16,c:c~NO_STATE!15!1,c:c~NO_STATE!17!2,c:c~NO_STATE!18!3,c:c~yyy!19!4,m:A@CP!2!6!11,m:A@CP!1!5!10,m:A@CP!3!7!12,m:A@CP!4!8!13,m:A@CP!0!9!14,",
                                  description="NAUTY String as defined by MCellR" )
  bngl_string  = StringProperty ( name = "BNGL", description="BNGL String as defined by BioNetGen" )

  def build_data_model_from_properties ( self ):
    mm_dict = {}
    mm_dict['data_model_version'] = "DM_2018_10_31_1510"
    mm_dict['molecule_definition'] = self.molecule_definition
    mm_dict['molecule_text_name'] = self.molecule_text_name
    mm_dict['comp_loc_text_name'] = self.comp_loc_text_name
    mm_dict['make_materials'] = self.make_materials
    mm_dict['cellblender_colors'] = self.cellblender_colors
    mm_dict['show_key_planes'] = self.show_key_planes
    mm_dict['average_coincident'] = self.average_coincident
    mm_dict['include_rotation'] = self.include_rotation
    mm_dict['dynamic_rotation'] = self.dynamic_rotation
    mm_dict['print_debug'] = self.print_debug
    mm_dict['show_text_interface'] = self.show_text_interface

    mm_dict['skip_rotation'] = self.skip_rotation
    mm_dict['skip_fixed_comp_index'] = self.skip_fixed_comp_index
    mm_dict['skip_var_comp_index'] = self.skip_var_comp_index


    mm_dict['molcomp_list'] = []
    for i in range(len(self.molcomp_items)):
      m = self.molcomp_items[i]
      item = {}
      item['name'] = m.name
      item['field_type'] = m.field_type
      item['has_coords'] = m.has_coords
      item['is_final'] = m.is_final
      item['coords'] = [ c for c in m.coords ]
      item['graph_string'] = m.graph_string
      item['peer_list'] = m.peer_list
      item['key_list'] = m.key_list
      item['angle'] = m.angle
      item['bond_index'] = m.bond_index
      item['key_index'] = m.key_index
      item['alert_string'] = m.alert_string
      mm_dict['molcomp_list'].append ( item )
    return mm_dict

  @staticmethod
  def upgrade_data_model ( dm ):
    # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
    print ( "------------------------->>> Upgrading MCellMolMakerProperty Data Model" )
    if not ('data_model_version' in dm):
        # Make changes to move from unversioned to DM_2014_10_24_1638
        dm['data_model_version'] = "DM_2018_10_26_1310"

    # Check that the upgraded data model version matches the version for this property group
    if dm['data_model_version'] == "DM_2018_10_26_1310":
        # Add the average_coincident flag
        dm['average_coincident'] = False
        dm['data_model_version'] = "DM_2018_10_31_1510"
        return None
    if dm['data_model_version'] != "DM_2018_10_31_1510":
        data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMolMakerPropertyGroup data model " + str(dm['data_model_version']) + " to current version." )
        return None

    return dm

  def build_properties_from_data_model ( self, context, dm_dict ):
    # Check that the data model version matches the version for this property group
    if dm_dict['data_model_version'] != "DM_2018_10_31_1510":
        data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMolMakerPropertyGroup data model " + str(dm['data_model_version']) + " to current version." )
    # Now convert the updated Data Model into CellBlender Properties
    self.molecule_definition = dm_dict['molecule_definition']
    self.molecule_text_name = dm_dict['molecule_text_name']
    self.comp_loc_text_name = dm_dict['comp_loc_text_name']
    self.make_materials = dm_dict['make_materials']
    self.cellblender_colors = dm_dict['cellblender_colors']
    self.average_coincident = dm_dict['average_coincident']
    self.include_rotation = dm_dict['include_rotation']
    self.dynamic_rotation = dm_dict['dynamic_rotation']
    self.print_debug = dm_dict['print_debug']
    self.show_text_interface = dm_dict['show_text_interface']

    if 'skip_rotation' in dm_dict: self.skip_rotation = dm_dict['skip_rotation']
    if 'skip_fixed_comp_index' in dm_dict: self.skip_fixed_comp_index = dm_dict['skip_fixed_comp_index']
    if 'skip_var_comp_index' in dm_dict: self.skip_var_comp_index = dm_dict['skip_var_comp_index']


    # Remove all the old items
    while len(self.molcomp_items) > 0:
      self.molcomp_items.remove ( 0 )

    # Add all the new items
    for item in dm_dict['molcomp_list']:
      new_mol = self.molcomp_items.add()
      new_mol.name = item['name']
      new_mol.field_type = item['field_type']
      new_mol.has_coords = item['has_coords']
      new_mol.is_final = item['is_final']
      new_mol.coords = [ c for c in item['coords'] ]
      new_mol.graph_string = item['graph_string']
      new_mol.peer_list = item['peer_list']
      new_mol.key_list = item['key_list']
      new_mol.angle = item['angle']
      new_mol.bond_index = item['bond_index']
      new_mol.key_index = item['key_index']
      new_mol.alert_string = item['alert_string']


  def draw_layout ( self, context, layout ):

    mcell = context.scene.mcell
    molmaker = mcell.molmaker

    row = layout.row()
    #row.prop_search( self, "molecule_definition", mcell.molecules, "molecule_list", icon='FORCE_LENNARDJONES')
    row.prop ( self, "molecule_definition", icon='FORCE_LENNARDJONES')
    row.operator("mol.refresh_mol_def", icon='NLA_PUSHDOWN', text="")
    row.operator("mol.chain_mol_defs", icon='CONSTRAINT', text="")

    for i in range(len(molmaker.molcomp_items)):
      m = molmaker.molcomp_items[i]
      row = layout.row()
      if m.field_type == "m":
        col = row.column()
        col.label ( str(i) + " Molecule " + m.name )
        col = row.column()
      elif m.field_type == "c":
        col = row.column()
        label_string = "   Component:  " + m.name
        if m.bond_index >= 0:
          label_string += "  (bonded)"
        col.label ( str(i) + label_string )
        col = row.column()
        if len(m.alert_string) > 0:
          col.alert = True
        col.prop ( m, 'bond_index' )
        col = row.column()
        if m.bond_index >= 0:
          col.prop ( m, 'angle' )
        else:
          col.label ( " " )
      elif m.field_type == "k":
        col = row.column()
        col.label ( str(i) + "     Key " + m.name )
        col = row.column()
        col = row.column()

    row = layout.row()
    col = row.column()
    col.prop ( self, 'make_materials', text="Make Materials" )
    col = row.column()
    col.prop ( self, 'cellblender_colors', text="CellBlender Colors" )
    col = row.column()
    col.prop ( self, 'show_key_planes', text="Show Key Planes" )
    col = row.column()
    col.prop ( self, 'average_coincident', text="Average Coincident" )
    row = layout.row()
    col = row.column()
    col.prop ( self, 'include_rotation', text="Axial Rotation" )
    col = row.column()
    col.prop ( self, 'dynamic_rotation', text="Dynamic Rotation" )
    col = row.column()
    col.prop ( self, 'print_debug', text="Text Output" )

    row = layout.row()
    col = row.column()
    col.prop ( self, 'skip_rotation', text="Skip Rotation" )
    if self.skip_rotation:
      col = row.column()
      col.prop ( self, 'skip_fixed_comp_index', text="Fixed Comp #" )
      col = row.column()
      col.prop ( self, 'skip_var_comp_index', text="Var Comp #" )

    row = layout.row()
    col = row.column()
    col.operator ( "mol.purge_by_reopen" )
    col = row.column()
    col.operator ( "mol.rebuild_with_cb" )

    row = layout.row(align=True)
    row.alignment = 'LEFT'
    if not self.show_text_interface:
      row.prop(self, "show_text_interface", icon='TRIA_RIGHT', text="Show Text Interface", emboss=False)
    else:
      row.prop(self, "show_text_interface", icon='TRIA_DOWN',  text="Show Text Interface", emboss=False)
      row = layout.row()
      row.prop_search ( self, "molecule_text_name",
                        self, "molecule_texts_list",
                        text="Molecule Definition Text:", icon='TEXT' )
      row.operator("mol.update_files", icon='FILE_REFRESH', text="")

      row = layout.row()
      row.prop_search ( self, "comp_loc_text_name",
                        self, "comp_loc_texts_list",
                        text="Component Location Text (opt):", icon='TEXT' )
      row.operator("mol.update_files", icon='FILE_REFRESH', text="")


      row = layout.row()
      row.operator ( "mol.build_as_is" )
      if 'mcell' in context.scene:
        # CellBlender is installed, so allow these options which use CellBlender molecule definitions
        row = layout.row()
        row.operator ( "mol.rebuild_two_d" )
        row = layout.row()
        row.operator ( "mol.rebuild_three_d" )

      row = layout.row()
      if not self.show_string_interface:
        row.prop(self, "show_string_interface", icon='TRIA_RIGHT', text="Show String Interface", emboss=False)
      else:
        row.prop(self, "show_string_interface", icon='TRIA_DOWN',  text="Show String Interface", emboss=False)
        row = layout.row()
        row.prop(self, "nauty_string")
        row = layout.row()
        col = row.column()
        col.operator("mol.to_bngl", icon='TRIA_DOWN', text="NAUTY -> BNGL")
        #col = row.column()
        #col.operator("mol.to_nauty", icon='TRIA_UP', text="BNGL -> NAUTY")
        row = layout.row()
        row.prop(self, "bngl_string")





  def draw_panel ( self, context, panel ):
    """ Create a layout from the panel and draw into it """
    layout = panel.layout
    self.draw_layout ( context, layout )


def add_cylinder_from_lpts ( p1, p2, radius=0.1, faces=8, caps=False ):

  #Calculate a few parameters for the wire (center, vector from center, and length):
  wire_center = mathutils.Vector ( ( (p1[0]+p2[0])/2,(p1[1]+p2[1])/2,(p1[2]+p2[2])/2 ) )
  wire_vector = mathutils.Vector ( ( (p2[0]-p1[0]),  (p2[1]-p1[1]),  (p2[2]-p1[2])   ) )
  wire_length = wire_vector.length

  # Assume that Blender will create the cylinder vertically, so find the rotation angle from vertical
  vertical_vector = mathutils.Vector ( (0, 0, 1) )
  rot_diff = vertical_vector.rotation_difference(wire_vector).to_euler()

  # Create the actual cylinder to represent the wire
  bpy.ops.mesh.primitive_cylinder_add(vertices=faces,radius=radius,depth=wire_length,location=wire_center,rotation=rot_diff)

  # Create the optional end caps - This seems to break up the object without: join_to_working_object(context,mol_obj)
  if caps:
    bpy.ops.mesh.primitive_uv_sphere_add(size=radius,location=p1)
    bpy.ops.mesh.primitive_uv_sphere_add(size=radius,location=p2)


def join_to_working_object ( context, working_obj ):
  context.scene.objects.active = working_obj
  working_obj.select = True
  bpy.ops.object.join()


def new_blender_mol_from_SphereCyl_data ( context, mol_data, show_key_planes=False ):

  # print ( "Mol data = " + str(mol_data) )
  mcell = context.scene.mcell
  mcell_mols = mcell.molecules.molecule_list
  molmaker = mcell.molmaker
  mats = bpy.data.materials

  if molmaker.make_materials:
    mol_mat = mats.get ( "MolMaker_mol" )
    if not mol_mat:
      # It didn't exist, so make it
      mol_mat = mats.new ( "MolMaker_mol" )
      color = mol_mat.diffuse_color
      color[0] = 1
      color[1] = 0.03
      color[2] = 0.03
    mol_mat = mats.get ( "MolMaker_comp" )
    if not mol_mat:
      # It didn't exist, so make it
      mol_mat = mats.new ( "MolMaker_comp" )
      color = mol_mat.diffuse_color
      color[0] = 0.3
      color[1] = 0.3
      color[2] = 0.6
    mol_mat = mats.get ( "MolMaker_bond" )
    if not mol_mat:
      # It didn't exist, so make it
      mol_mat = mats.new ( "MolMaker_bond" )
      color = mol_mat.diffuse_color
      color[0] = 0.1
      color[1] = 0.1
      color[2] = 0.1
      mol_mat.specular_intensity = 0
    mol_mat = mats.get ( "MolMaker_key" )
    if not mol_mat:
      # It didn't exist, so make it
      mol_mat = mats.new ( "MolMaker_key" )
      color = mol_mat.diffuse_color
      color[0] = 0
      color[1] = 0.25
      color[2] = 0.25
      mol_mat.specular_intensity = 0
    mol_mat = mats.get ( "MolMaker_key_plane" )
    if not mol_mat:
      # It didn't exist, so make it
      mol_mat = mats.new ( "MolMaker_key_plane" )
      color = mol_mat.diffuse_color
      color[0] = 0.5
      color[1] = 0.0
      color[2] = 0.0
      mol_mat.specular_intensity = 0
      mol_mat.use_transparency = True
      mol_mat.alpha = 0.2

  # Make an empty mesh
  mol_mesh = bpy.data.meshes.new ( "Mol Mesh" )

  # NOTE: The mesh doesn't need any verts or faces to be used as the join target for other parts.

  mol_mesh.from_pydata ( [], [], [] )
  mol_mesh.update()

  mol_obj = bpy.data.objects.new("Mol Object", mol_mesh)

  # Put the mesh into the scene and make active
  context.scene.objects.link(mol_obj)
  bpy.ops.object.select_all ( action = "DESELECT" )
  mol_obj.select = True
  context.scene.objects.active = mol_obj

  sphere_list = mol_data['SphereList']
  cylinder_list = mol_data['CylList']
  face_list = mol_data['FaceList']

  # Add the molecules (spheres)
  for mol in sphere_list:
    if show_key_planes or (mol['ftype'] != 'k'):
      p = mol['loc']
      # bpy.ops.mesh.primitive_uv_sphere_add(size=mol['r'],location=p)
      bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, size=mol['r'],location=p)
      color_set = False
      if molmaker.cellblender_colors:
        # Try to find a molecule color material matching this molecule
        mname = "mol_" + mol['name'] + "_mat"
        if mname in mats:
          context.active_object.data.materials.append ( mats.get(mname) )
          color_set = True
      if (not color_set) and ('c' in mol):
        if mol['c'] in mats:
          context.active_object.data.materials.append ( mats.get(mol['c']) )
      join_to_working_object ( context, mol_obj )

  # Add the bonds (cylinders)
  for i in range(len(cylinder_list)):
    cyl = cylinder_list[i]
    sph0 = sphere_list[cyl[0]]
    sph1 = sphere_list[cyl[1]]
    p0 = sph0['loc']
    p1 = sph1['loc']
    add_cylinder_from_lpts ( p0, p1, radius=cyl[2], faces=16, caps=False )
    context.active_object.data.materials.append ( mats.get("MolMaker_bond") )
    join_to_working_object ( context, mol_obj )

  # Add the keys (as faces)
  if show_key_planes:
    for i in range(len(face_list)):
      # checked_print ( "Adding a face" )
      vlist = face_list[i]

      Vertices = []
      Faces = [[]]
      i = 0
      for vertex in vlist:
        # checked_print ( "  Adding vertex at " + str(vertex) )
        Vertices.append ( mathutils.Vector((vertex[0],vertex[1],vertex[2])) )
        Faces[0].append ( i )
        i += 1

      NewMesh = bpy.data.meshes.new("KeyMesh")
      NewMesh.from_pydata ( Vertices, [], Faces )
      NewMesh.update()
      NewMesh.materials.append ( mats.get("MolMaker_key_plane") )
      NewObj = bpy.data.objects.new("KeyObj", NewMesh)
      NewObj.show_transparent = True
      context.scene.objects.link ( NewObj)
      context.scene.objects.active = NewObj
      for o in context.scene.objects:
        o.select = False
      context.scene.objects.active = NewObj
      NewObj.select = True
      join_to_working_object ( context, mol_obj )
      mol_obj.show_transparent = True



# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)



"""
def register():
  print ("Registering ", __name__)
  bpy.utils.register_module(__name__)
  bpy.types.Scene.molmaker = bpy.props.PointerProperty(type=MCellMolMakerPropertyGroup)
#end register

def unregister():
  print ("Unregistering ", __name__)
  del bpy.types.Scene.molmaker
  bpy.utils.unregister_module(__name__)
#end unregister
"""

