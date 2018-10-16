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

# This code is based model text that looks like this:

"""
  [0] = l (c) at  (0.0950524, -0.0258901, 0) with peers [59,32]
  [1] = l (c) at  (0.0950524, -0.0430901, 0) with peers [58,31]
  [2] = l (c) at  (0.085, -0.0086, 0) with peers [59,30]
  [3] = l (c) at  (0.085, -0.0603803, 0) with peers [58,33]
  [4] = l (c) at  (0.05, 0, 0) with peers [60,34]
  [5] = l (c) at  (0.03, 0, 0) with peers [60,38]
  [6] = l (c) at  (0.05, -0.0689803, 0) with peers [61,35]
  [7] = l (c) at  (-0.005, 0.0086, 0) with peers [62,39]
  [8] = l (c) at  (0.03, -0.0689803, 0) with peers [61,37]
  [9] = l (c) at  (-0.0150524, 0.0258901, 0) with peers [62,36]
  [10] = l (c) at  (-0.0299999, 0.0343998, 0) with peers [64,41]
  [11] = l (c) at  (-0.00521005, 0.0605613, 0) with peers [63,40]
  [12] = l (c) at  (0.0151305, -0.0776254, 0) with peers [65,42]
  [13] = l (c) at  (-0.005, -0.0086, 0) with peers [66,43]
  [14] = l (c) at  (-0.049999, 0.0342181, 0) with peers [64,45]
  [15] = l (c) at  (0.00468486, 0.077942, 0) with peers [63,44]
  [16] = l (c) at  (0.00523557, -0.0950061, 0) with peers [65,46]
  [17] = l (c) at  (-0.0150524, -0.0258901, 0) with peers [66,47]
  [18] = r (c) at  (0.085, 0.0086, 0) with peers [51]
  [19] = r (c) at  (0.130052, -0.0344901, 0) with peers [50]
  [20] = r (c) at  (0.085, -0.0775803, 0) with peers [52]
  [21] = r (c) at  (0.00497352, -0.0430451, 0) with peers [53]
  [22] = r (c) at  (0.0396053, 0.0868597, 0) with peers [55]
  [23] = r (c) at  (0.00452859, 0.0951413, 0) with peers [55]
  [24] = r (c) at  (-0.0850757, 0.0424997, 0) with peers [54]
  [25] = r (c) at  (-0.0849195, 0.0253004, 0) with peers [54]
  [26] = r (c) at  (0.0153925, -0.129586, 0) with peers [56]
  [27] = r (c) at  (-0.00963395, -0.103651, 0) with peers [56]
  [28] = r (c) at  (-0.0500524, -0.0344901, 0) with peers [57]
  [29] = r (c) at  (-0.0150524, -0.0430901, 0) with peers [57]
  [30] = r (c) at  (0.085, -0.0086, 0) with peers [51,2]
  [31] = r (c) at  (0.0950524, -0.0430901, 0) with peers [50,1]
  [32] = r (c) at  (0.0950524, -0.0258901, 0) with peers [50,0]
  [33] = r (c) at  (0.085, -0.0603803, 0) with peers [52,3]
  [34] = r (c) at  (0.05, 0, 0) with peers [51,4]
  [35] = r (c) at  (0.05, -0.0689803, 0) with peers [52,6]
  [36] = r (c) at  (-0.0150524, 0.0258901, 0) with peers [49,9]
  [37] = r (c) at  (0.03, -0.0689803, 0) with peers [53,8]
  [38] = r (c) at  (0.03, 0, 0) with peers [48,5]
  [39] = r (c) at  (-0.005, 0.0086, 0) with peers [48,7]
  [40] = r (c) at  (-0.00521005, 0.0605613, 0) with peers [49,11]
  [41] = r (c) at  (-0.0299999, 0.0343998, 0) with peers [49,10]
  [42] = r (c) at  (0.0151305, -0.0776254, 0) with peers [53,12]
  [43] = r (c) at  (-0.005, -0.0086, 0) with peers [48,13]
  [44] = r (c) at  (0.00468486, 0.077942, 0) with peers [55,15]
  [45] = r (c) at  (-0.049999, 0.0342181, 0) with peers [54,14]
  [46] = r (c) at  (0.00523557, -0.0950061, 0) with peers [56,16]
  [47] = r (c) at  (-0.0150524, -0.0258901, 0) with peers [57,17]
  [48] = L (m) at  (0, 0, 0) with peers [38,39,43]
  [49] = L (m) at  (-0.0200524, 0.0344901, 0) with peers [40,41,36]
  [50] = L (m) at  (0.100052, -0.0344901, 0) with peers [19,32,31]
  [51] = L (m) at  (0.08, -3.67394e-18, 0) with peers [34,30,18]
  [52] = L (m) at  (0.08, -0.0689803, 0) with peers [35,20,33]
  [53] = L (m) at  (0.0200521, -0.0689803, 0) with peers [21,42,37]
  [54] = L (m) at  (-0.0799978, 0.0339455, 0) with peers [45,24,25]
  [55] = L (m) at  (0.00960652, 0.0865871, 0) with peers [22,23,44]
  [56] = L (m) at  (0.00031391, -0.103651, 0) with peers [26,46,27]
  [57] = L (m) at  (-0.0200524, -0.0344901, 0) with peers [28,29,47]
  [58] = R (m) at  (0.0900262, -0.0517352, 0) with peers [1,3]
  [59] = R (m) at  (0.0900262, -0.0172451, 0) with peers [0,2]
  [60] = R (m) at  (0.04, 0, 0) with peers [4,5]
  [61] = R (m) at  (0.04, -0.0689803, 0) with peers [8,6]
  [62] = R (m) at  (-0.0100262, 0.0172451, 0) with peers [7,9]
  [63] = R (m) at  (-0.000262595, 0.0692517, 0) with peers [11,15]
  [64] = R (m) at  (-0.0399994, 0.0343089, 0) with peers [14,10]
  [65] = R (m) at  (0.010183, -0.0863157, 0) with peers [12,16]
  [66] = R (m) at  (-0.0100262, -0.0172451, 0) with peers [17,13]
"""

# Note that this was extended as follows to support a bond angle:

#   The type can now be "m" or "c" or "k". The "k" indicates a rotation key.
#   An optional field was added after the components with <#> to reference the rotation key index.
#   A rotation key index can reference any other entry in the table (m, c, or k).
#   The triad of the molecule, component, and key fields must define a unique plane.


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

def update_available_scripts ( molmaker ):
  # Delete current scripts list
  while molmaker.molecule_texts_list:
    molmaker.molecule_texts_list.remove(0)
  # Find the current internal scripts and add them to the list
  for txt in bpy.data.texts:
     print ( "\n" + txt.name + "\n" + txt.as_string() + "\n" )
     if True or (txt.name[-3:] == ".py"):
        molmaker.molecule_texts_list.add()
        index = len(molmaker.molecule_texts_list)-1
        molmaker.molecule_texts_list[index].name = txt.name

  while molmaker.comp_loc_texts_list:
    molmaker.comp_loc_texts_list.remove(0)
  # Find the current internal scripts and add them to the list
  for txt in bpy.data.texts:
     print ( "\n" + txt.name + "\n" + txt.as_string() + "\n" )
     if True or (txt.name[-3:] == ".py"):
        molmaker.comp_loc_texts_list.add()
        index = len(molmaker.comp_loc_texts_list)-1
        molmaker.comp_loc_texts_list[index].name = txt.name

class MolMaker_OT_scripting_refresh(bpy.types.Operator):
  bl_idname = "mol.scripting_refresh"
  bl_label = "Refresh Files"
  bl_description = "Refresh the list of available script files"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    molmaker = context.scene.mcell.molmaker
    update_available_scripts ( molmaker )
    return {'FINISHED'}


# This one is called by Build 2D and Build 3D
def read_molcomp_data_MolComp ( fdata ):
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


# This is called directly by the "build as is" operator.
# The SphereCyl format is simpler and intended for rendering.
# The SphereCyl format only contains Spheres ("SphereList") and Cylinders ("CylList").
def read_molcomp_data_SphereCyl ( fdata ):
  ldata = [ l.strip() for l in fdata.split('\n') if len(l.strip()) > 0 ]
  ldata = [ l for l in ldata if not l.startswith('#') ]
  SphereCyl_data = { 'Version':1.1, 'SphereList':[], 'CylList':[], 'FaceList':[] }
  this_index = 0
  for l in ldata:
    print ( "Line: " + l )
    m = { 'name':'', 'loc':[0,0,0], 'r':1 }
    m['name'] = l.split("=")[1].split('(')[0].strip()
    m['ftype'] = l.split('(')[1][0]   # Pull out the type (m or c or k)
    if m['ftype'] == 'm':
      m['r'] = 0.005
      peer_part = l.split('with peers')[1].strip()
      if '[' in peer_part:
        peers = peer_part.split('[')[1].split(']')[0].split(',')
        peers = [ p for p in peers if len(p) > 0 ]  # Remove any empty peers
        for p in peers:
          SphereCyl_data['CylList'].append ( [this_index, int(p), 0.001] )
          print ( "  Bond: " + str(this_index) + " " + p.strip() )
    elif m['ftype'] == 'c':
      m['r'] = 0.0025
    elif m['ftype'] == 'k':
      m['r'] = 0.001
    m['loc'] = eval ( '[' + l.split('(')[2].split(')')[0] + ']' )
    SphereCyl_data['SphereList'].append ( m )
    this_index += 1
  return SphereCyl_data


# This converts MolComp format to SphereCyl format for simple 3D rendering.
def MolComp_to_SphereCyl ( molcomp_list, build_as_3D ):
  SphereCyl_data = { 'Version':1.1, 'SphereList':[], 'CylList':[], 'FaceList':[] }
  this_index = 0
  for mc in molcomp_list:
    m = { 'name':'', 'loc':mc['coords'], 'r':1 }
    if mc['ftype'] == 'm':
      m['r'] = 0.005
      if len(mc['peer_list']) > 0:
        peers = mc['peer_list']
        for p in peers:
          SphereCyl_data['CylList'].append ( [this_index, int(p), 0.001] )  # Add the connecting bond cylinder
          if build_as_3D and len(molcomp_list[int(p)]['key_list']) > 0:
            # This component has a key
            k = molcomp_list[int(p)]['key_list'][0]
            SphereCyl_data['FaceList'].append ( [ mc['coords'], molcomp_list[p]['coords'], molcomp_list[k]['coords'] ] ) # , [0.01,0.01,0.0 1] ] )
    elif mc['ftype'] == 'c':
      m['r'] = 0.0025
    elif mc['ftype'] == 'k':
      m['r'] = 0.001
    SphereCyl_data['SphereList'].append ( m )
    this_index += 1
  return SphereCyl_data



def dump_molcomp_list ( molcomp_list ):
  i = 0
  for mc in molcomp_list:
    print ( "[" + str(i) + "] = " + mc['name'] + " (" + mc['ftype'] + ") at (" + str(mc['coords'][0]) + "," + str(mc['coords'][1]) + "," + str(mc['coords'][2]) + ") with peers " + str(mc['peer_list']) + " with keys " + str(mc['key_list']) + " and angle " + str(mc['angle']) )
    i += 1


class MolMaker_OT_build_as_is(bpy.types.Operator):
  bl_idname = "mol.build_as_is"
  bl_label = "Build As Is"
  bl_description = "Build a molecule from the coordinates in the file"
  bl_options = {'REGISTER', 'UNDO'}


  def execute(self, context):
    print ( "Build Molecule from values in file" )
    molmaker = context.scene.mcell.molmaker
    fdata = bpy.data.texts[molmaker.molecule_text_name].as_string()
    print ( "Read:\n" + fdata )
    mol_data = read_molcomp_data_SphereCyl ( fdata )

    new_blender_mol_from_SphereCyl_data ( context, mol_data )

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
      num_points = len(mc[mi]['peer_list'])
      points = get_distributed_sphere_points ( num_points )
      for ci in range(num_points):
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
      for ci in range(len(mc[mi]['peer_list'])):
        angle = 2 * math.pi * ci / len(mc[mi]['peer_list'])
        mc[mc[mi]['peer_list'][ci]]['coords'][0] = scale * math.cos(angle)
        mc[mc[mi]['peer_list'][ci]]['coords'][1] = scale * math.sin(angle)
        mc[mc[mi]['peer_list'][ci]]['coords'][2] = 0
        #### fprintf ( stdout, "  Component %s is at (%g,%g)\n", mc[mc[mi].peers[ci]].name, mc[mc[mi].peers[ci]].x, mc[mc[mi].peers[ci]].y );
    elif mc[mi]['ftype'] == 'k':
      # For 2D, the rotation keys should be straight up in Z
      mc[mi]['coords'][0] = 0
      mc[mi]['coords'][1] = 0
      mc[mi]['coords'][2] = 1 * scale



def bind_molecules_at_components ( mc, fixed_comp_index, var_comp_index, build_as_3D ):
  # Bind these two molecules by aligning their axes and shifting to align their components
  # num_parts = len(mc)

  print ( "  Binding " + str(mc[fixed_comp_index]['name']) + " to " + str(mc[var_comp_index]['name']) );
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
    norm_dot_prod =  1
  if norm_dot_prod < -1:
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

  # Normalize between -PI and PI
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

    # Build a 3D rotation matrix
    ux = norm_cross_prod[0]
    uy = norm_cross_prod[1]
    uz = norm_cross_prod[2]
    omca = 1 - ca

    R = [ [ca + (ux*ux*omca), (ux*uy*omca) - (uz*sa), (ux*uz*omca) + (uy*sa)],
          [(uy*ux*omca) + (uz*sa), ca + (uy*uy*omca), (uy*uz*omca) - (ux*sa)],
          [(uz*ux*omca) - (uy*sa), (uz*uy*omca) + (ux*sa), ca + (uz*uz*omca)] ]

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


  # Now the molecules are aligned as they would be except for rotation along their bonding axis

  if build_as_3D:
    # dump_molcomp_list ( mc )

    # Rotate the variable molecule along its bonding axis to align based on the rotation key angle
    print ( "Final Rotation:" )
    print ( "  Fixed mol " + str(fixed_mol_index) + " binding to Var mol " + str(var_mol_index) )
    print ( "  Fixed component " + str(fixed_comp_index) + " binding to Var component " + str(var_comp_index) )
    fixed_key_index = int(mc[fixed_comp_index]['key_list'][0])
    var_key_index = int(mc[var_comp_index]['key_list'][0])
    print ( "  Fixed component key: " + str(fixed_key_index) + ", Var component key: " + str(var_key_index) )
    fixed_angle = mc[fixed_comp_index]['angle']
    var_angle = mc[var_comp_index]['angle']
    print ( "  Fixed angle = " + str(fixed_angle) + ", Var angle = " + str(var_angle) )

    vec1 = []
    vec2 = []

    vec1.append ( mc[fixed_comp_index]['coords'][0] - mc[fixed_mol_index]['coords'][0] )
    vec1.append ( mc[fixed_comp_index]['coords'][1] - mc[fixed_mol_index]['coords'][1] )
    vec1.append ( mc[fixed_comp_index]['coords'][2] - mc[fixed_mol_index]['coords'][2] )

    vec2.append ( mc[fixed_key_index]['coords'][0] - mc[fixed_mol_index]['coords'][0] )
    vec2.append ( mc[fixed_key_index]['coords'][1] - mc[fixed_mol_index]['coords'][1] )
    vec2.append ( mc[fixed_key_index]['coords'][2] - mc[fixed_mol_index]['coords'][2] )

    fixed_normal = [ (vec1[1] * vec2[2]) - (vec1[2] * vec2[1]),
                     (vec1[2] * vec2[0]) - (vec1[0] * vec2[2]),
                     (vec1[0] * vec2[1]) - (vec1[1] * vec2[0]) ]

    v1_mag = math.sqrt ( (vec1[0]*vec1[0]) + (vec1[1]*vec1[1]) + (vec1[2]*vec1[2]) )
    v2_mag = math.sqrt ( (vec2[0]*vec2[0]) + (vec2[1]*vec2[1]) + (vec2[2]*vec2[2]) )

    fixed_normal = [ cp / ( v1_mag * v2_mag ) for cp in fixed_normal ]

    print ( "  Fixed normal = " + str(fixed_normal) )

    vec1 = []
    vec2 = []

    vec1.append ( mc[var_comp_index]['coords'][0] - mc[var_mol_index]['coords'][0] )
    vec1.append ( mc[var_comp_index]['coords'][1] - mc[var_mol_index]['coords'][1] )
    vec1.append ( mc[var_comp_index]['coords'][2] - mc[var_mol_index]['coords'][2] )

    vec2.append ( mc[var_key_index]['coords'][0] - mc[var_mol_index]['coords'][0] )
    vec2.append ( mc[var_key_index]['coords'][1] - mc[var_mol_index]['coords'][1] )
    vec2.append ( mc[var_key_index]['coords'][2] - mc[var_mol_index]['coords'][2] )

    var_normal = [ (vec1[1] * vec2[2]) - (vec1[2] * vec2[1]),
                   (vec1[2] * vec2[0]) - (vec1[0] * vec2[2]),
                   (vec1[0] * vec2[1]) - (vec1[1] * vec2[0]) ]

    v1_mag = math.sqrt ( (vec1[0]*vec1[0]) + (vec1[1]*vec1[1]) + (vec1[2]*vec1[2]) )
    v2_mag = math.sqrt ( (vec2[0]*vec2[0]) + (vec2[1]*vec2[1]) + (vec2[2]*vec2[2]) )

    var_normal = [ cp / ( v1_mag * v2_mag ) for cp in var_normal ]

    print ( "  Var normal = " + str(var_normal) )


    norm_dot_prod = (fixed_normal[0] * var_normal[0]) + (fixed_normal[1] * var_normal[1]) + (fixed_normal[2] * var_normal[2])

    # Ensure that the dot product is a legal argument for the "acos" function:
    if norm_dot_prod >  1:
      norm_dot_prod =  1
    if norm_dot_prod < -1:
      norm_dot_prod = -1

    cur_rot_angle = math.acos ( norm_dot_prod )

    composite_rot_angle = (var_angle-fixed_angle) - cur_rot_angle

    # Build a 3D rotation matrix
    var_rot_unit = [ v / v1_mag for v in vec1 ]
    ux = var_rot_unit[0]
    uy = var_rot_unit[1]
    uz = var_rot_unit[2]
    ca = math.cos(composite_rot_angle)
    sa = math.sin(composite_rot_angle)
    omca = 1 - ca

    R = [ [ca + (ux*ux*omca), (ux*uy*omca) - (uz*sa), (ux*uz*omca) + (uy*sa)],
          [(uy*ux*omca) + (uz*sa), ca + (uy*uy*omca), (uy*uz*omca) - (ux*sa)],
          [(uz*ux*omca) - (uy*sa), (uz*uy*omca) + (ux*sa), ca + (uz*uz*omca)] ]

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



def bind_all_molecules ( molcomp_array, build_as_3D ):
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

                bind_molecules_at_components ( molcomp_array, fci, vci, build_as_3D )

                # The bonding process will have specified the placement of the variable molecule
                # Set the variable molecule and all of its components to final
                molcomp_array[vmi]['is_final'] = True
                #for (int vmici=0; vmici<molcomp_array[vmi].num_peers; vmici++) {
                for vmici in range(len(molcomp_array[vmi]['peer_list'])):
                  molcomp_array[molcomp_array[vmi]['peer_list'][vmici]]['is_final'] = True



def build_all_mols ( context, build_as_3D ):

  if build_as_3D:
    print ( "\n\nBuilding as 3D" )
  else:
    print ( "\n\nBuilding as 2D" )

  molmaker = context.scene.mcell.molmaker
  fdata = bpy.data.texts[molmaker.molecule_text_name].as_string()

  molcomp_list = read_molcomp_data_MolComp ( fdata )

  # Use the default cases to start
  if build_as_3D:
    set_component_positions_3D ( molcomp_list )
  else:
    set_component_positions_2D ( molcomp_list )

  if molmaker.comp_loc_text_name in bpy.data.texts:
    # There is a component location definition text
    print ( "Read component definition text named " + molmaker.comp_loc_text_name )

    # Set the has_coords flag to false on each component of each molecule
    for mc in molcomp_list:
      if mc['ftype'] == 'm':
        mc['coords'] = [0,0,0]
        mc['has_coords'] = False
      else:
        mc['has_coords'] = False

    # Read the component definitions
    ldata = bpy.data.texts[molmaker.comp_loc_text_name].as_string()
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
        print ( "Setting z to zero for " + cl_mol_name + "." + cl_comp_name )
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
          print ( " Clearing assigned for " + c['cname'] + " with coords: " + str(c['coords']) )
          c['assigned'] = False
        # Sweep through all the components for this molecule
        print ( " Assigning coordinates to components in mol " + mc['name'] )
        for pi in mc['peer_list']:
          # Only assign to components that don't have coords
          print ( "   Checking peer " + str(pi) )
          if not molcomp_list[pi]['has_coords']:
            # Sweep through the component name list looking for an unassigned match
            for c in mol_comp_loc_dict[mc['name']]:
              if not c['assigned']:
                if c['cname'] == molcomp_list[pi]['name']:
                  molcomp_list[pi]['coords'] = [ cc for cc in c['coords'] ]
                  print ( "          Assigning coordinates: " + str(molcomp_list[pi]['coords']) )
                  molcomp_list[pi]['has_coords'] = True
                  c['assigned'] = True
                  break

  bind_all_molecules ( molcomp_list, build_as_3D )

  print ( "======================================================================================" )
  dump_molcomp_list ( molcomp_list )
  print ( "======================================================================================" )

  new_blender_mol_from_SphereCyl_data ( context, MolComp_to_SphereCyl ( molcomp_list, build_as_3D ) )



class MolMaker_OT_build_2D(bpy.types.Operator):
  bl_idname = "mol.rebuild_two_d"
  bl_label = "Build 2D"
  bl_description = "Build a molecule based on 2D assumption"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    print ( "Build Molecule 2D" )
    build_all_mols ( context, build_as_3D=False )
    return {'FINISHED'}



class MolMaker_OT_build_3D(bpy.types.Operator):
  bl_idname = "mol.rebuild_three_d"
  bl_label = "Build 3D"
  bl_description = "Build a molecule based on CellBlender Definitions"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self, context):
    print ( "Build Molecule calculating new values from CellBlender" )
    build_all_mols ( context, build_as_3D=True )
    return {'FINISHED'}



class MolMakerFileNameProperty(bpy.types.PropertyGroup):
  name = StringProperty(name="Script")


class MCellMolMakerPropertyGroup(bpy.types.PropertyGroup):
  molecule_texts_list = CollectionProperty(type=MolMakerFileNameProperty, name="Molecule Texts List")
  molecule_text_name = StringProperty ( name = "Text name containing this molecule description (molcomp)" )
  comp_loc_texts_list = CollectionProperty(type=MolMakerFileNameProperty, name="Component Location Texts List")
  comp_loc_text_name = StringProperty ( name = "Text name containing optional component locations (rather than from CellBlender)" )


  def draw_layout ( self, context, layout ):
    row = layout.row()
    row.prop_search ( self, "molecule_text_name",
                      self, "molecule_texts_list",
                      text="Molecule Definition Text:", icon='TEXT' )
    row.operator("mol.scripting_refresh", icon='FILE_REFRESH', text="")

    row = layout.row()
    row.prop_search ( self, "comp_loc_text_name",
                      self, "comp_loc_texts_list",
                      text="Component Location Text (opt):", icon='TEXT' )
    row.operator("mol.scripting_refresh", icon='FILE_REFRESH', text="")


    row = layout.row()
    row.operator ( "mol.build_as_is" )
    if 'mcell' in context.scene:
      # CellBlender is installed, so allow this option
      row = layout.row()
      row.operator ( "mol.rebuild_two_d" )
      row = layout.row()
      row.operator ( "mol.rebuild_three_d" )


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


def new_blender_mol_from_SphereCyl_data ( context, mol_data ):

  # print ( "Mol data = " + str(mol_data) )

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
    p = mol['loc']
    # bpy.ops.mesh.primitive_uv_sphere_add(size=mol['r'],location=p)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, size=mol['r'],location=p)
    join_to_working_object ( context, mol_obj )

  # Add the bonds (cylinders)
  for i in range(len(cylinder_list)):
    cyl = cylinder_list[i]
    sph0 = sphere_list[cyl[0]]
    sph1 = sphere_list[cyl[1]]
    p0 = sph0['loc']
    p1 = sph1['loc']
    add_cylinder_from_lpts ( p0, p1, radius=cyl[2], faces=16, caps=False )
    join_to_working_object ( context, mol_obj )

  # Add the keys (as faces)
  for i in range(len(face_list)):
    print ( "Adding a face" )
    vlist = face_list[i]

    Vertices = []
    Faces = [[]]
    i = 0
    for vertex in vlist:
      print ( "  Adding vertex at " + str(vertex) )
      Vertices.append ( mathutils.Vector((vertex[0],vertex[1],vertex[2])) )
      Faces[0].append ( i )
      i += 1

    NewMesh = bpy.data.meshes.new("KeyMesh")
    NewMesh.from_pydata ( Vertices, [], Faces )
    NewMesh.update()
    NewObj = bpy.data.objects.new("KeyObj", NewMesh)
    context.scene.objects.link ( NewObj)
    # This fails for some reason:   join_to_working_object ( context, mol_obj )





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

