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
This stand-alone Python program reads from a CellBlender Data Model
and attempts to generate corresponding MCell MDL.

Note that it is acceptable to assume that this code is getting the
most current data model since CellBlender can upgrade any previous
data model and provide the most current to this function.

"""


import pickle
import sys
import json
import os
import re

#### Helper Functions ####

def pickle_data_model ( dm ):
    """ Return a pickle string containing a data model """
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

def unpickle_data_model ( dmp ):
    """ Return a data model from a pickle string """
    return ( pickle.loads ( dmp.encode('latin1') ) )

def read_data_model ( file_name ):
    """ Return a data model read from a named file """
    # Start by determining if this is a JSON file or not
    is_json = False
    f = open ( file_name, 'r' )
    header = "xxxxx"
    try:
      header = f.read(20)
    except  UnicodeDecodeError:
      pass # The header value shouldn't contain "'mcell:'" in this case anyway
    if '"mcell":' in header:
      is_json = True
    elif "'mcell':" in header:
      is_json = True
    f.close()
    # Open as appropriate
    if is_json:
        # Open as a JSON format file
        print ( "Opening a JSON file: " + file_name )
        f = open ( file_name, 'r' )
        print ( "Reading a JSON file" )
        json_model = f.read()
        print ( "Loading a JSON file" )
        data_model = json.loads ( json_model )
        print ( "Done loading a JSON file" )
    else:
        # Open as a pickled format file
        print ( "Opening a Pickle file: " + file_name )
        f = open ( file_name, 'r' )
        pickled_model = f.read()
        data_model = unpickle_data_model ( pickled_model )
    print ( "Returning a data model" )
    return data_model

dump_depth = 0;
def dump_data_model ( name, dm ):
    if type(dm) == type({'a':1}):  #dm is a dictionary
        print ( str(dump_depth*"  ") + name + " {}" )
        dump_depth += 1
        for k,v in sorted(dm.items()):
            dump_data_model ( k, v )
        dump_depth += -1
    elif type(dm) == type(['a',1]):  #dm is a list
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


def as_float_str ( dm, dm_name, mdl_name, blank_default="" ):
    if dm_name in dm:
      val = str(dm[dm_name])
      if mdl_name in ['MISSED_REACTION_THRESHOLD', 'PARTITION_VAL']:
        # Force to be a float value to match values exported from Blender float properties
        import array
        val = array.array('f',[float(dm[dm_name])])
        val = "%.15g" % val[0]
      elif len(val) > 0:
        if type(dm[dm_name]) == type(True):
          val = val.upper()
        elif type(dm[dm_name]) == type(1.234):
          val = "%.15g" % dm[dm_name]
      elif len(blank_default) > 0:
        val = str(blank_default)
      return val
    else:
      return None


def write_dm_str_val_good ( dm, f, dm_name, mdl_name, blank_default="", indent="" ):
    # This writes out values with their full double precision
    if dm_name in dm:
      val = str(dm[dm_name])
      if len(val) > 0:
        if type(dm[dm_name]) == type(True):
          val = val.upper()
        elif type(dm[dm_name]) == type(1.234):
          val = "%.15g" % dm[dm_name]
        f.write ( indent + mdl_name + " = " + val + "\n" )
      elif len(blank_default) > 0:
        f.write ( indent + mdl_name + " = " + str(blank_default) + "\n" )


def write_dm_str_val ( dm, f, dm_name, mdl_name, blank_default="", indent="" ):
    print ( "  Par " + str(dm_name) + " is MDL: " + str(mdl_name) )
    # This writes out values with forced single precision
    if dm_name in dm:
      val = str(dm[dm_name])
      print ( "      " + str(dm_name) + " = \"" + str(val) + "\"" )
      if mdl_name in ['MISSED_REACTION_THRESHOLD']:
        # Force to be a float value to match values exported from Blender float properties
        import array
        val = array.array('f',[float(dm[dm_name])])
        val = "%.15g" % val[0]
        f.write ( indent + mdl_name + " = " + val + "\n" )
        print ( "      MDL: " + mdl_name + " = " + val )
      elif len(val) > 0:
        if type(dm[dm_name]) == type(True):
          val = val.upper()
        elif type(dm[dm_name]) == type(1.234):
          val = "%.15g" % dm[dm_name]
        f.write ( indent + mdl_name + " = " + val + "\n" )
        print ( "      MDL: " + mdl_name + " = " + val )
      elif len(blank_default) > 0:
        f.write ( indent + mdl_name + " = " + str(blank_default) + "\n" )
        print ( "      MDL: " + mdl_name + " = " + str(blank_default) )
      else:
        print ( "      MDL: not written" )

def write_dm_str_val_junk ( dm, f, dm_name, mdl_name, blank_default="", indent="" ):
    if mdl_name == 'TIME_STEP':
      __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    if mdl_name == 'MISSED_REACTION_THRESHOLD':
      __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
    if dm_name in dm:
      val = str(dm[dm_name])
      if len(val) > 0:
        if type(dm[dm_name]) == type(True):
          val = val.upper()
        elif type(dm[dm_name]) == type(1):
          val = str(dm[dm_name])
        elif type(dm[dm_name]) == type(1.234):
          # Force to be a float value to match values exported from Blender float properties
          import array
          val = array.array('f',[float(dm[dm_name])])
          val = "%.15g" % val[0]
        elif type(dm[dm_name]) == type("1.234"):
          # This may be a float hiding in a string
          import re
          float_regexp = re.compile(r"^[-+]?(?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)(?:[eE][-+]?[0-9]+\b)?$")
          match = re.match(float_regexp,dm[dm_name])
          if match != None:
            import array
            val = array.array('f',[float(match.string)])
            val = "%.15g" % val[0]
          else:
            val = str(dm[dm_name])
        f.write ( indent + mdl_name + " = " + val + "\n" )
      elif len(blank_default) > 0:
        f.write ( indent + mdl_name + " = " + str(blank_default) + "\n" )

def write_dm_on_off ( dm, f, dm_name, mdl_name, blank_default="", indent="" ):
    if dm_name in dm:
      val = dm[dm_name]
      if type(val) == type(True):
        if val:
          val = "ON"
        else:
          val = "OFF"
        f.write ( indent + mdl_name + " = " + val + "\n" )
      else:
        f.write ( indent + mdl_name + " = " + val + "\n" )


#### Start of MDL Code ####

"""
List of CellBlender files containing Data Model code:
  ( found with: grep build_data_model_from_properties *.py )

    File                               Classes Exported to Data Model
    ----                               ------------------------------
    cellblender_initialization.py      MCellInitializationPropertyGroup
    cellblender_legacy.py              None (only comments found)
    cellblender_main.py                MCellPropertyGroup
    cellblender_molecules.py           MCellMoleculeProperty MCellMoleculesListProperty
    cellblender_mol_viz.py             MCellMolVizPropertyGroup MCellVizOutputPropertyGroup
    cellblender_objects.py             MCellModelObjectsProperty  MCellModelObjectsPropertyGroup
    cellblender_partitions.py          MCellPartitionsPropertyGroup
    cellblender_reaction_output.py     MCellReactionOutputProperty MCellReactionOutputPropertyGroup
    cellblender_reactions.py           MCellReactionProperty MCellReactionsListProperty
    cellblender_release.py             MCellMoleculeReleaseProperty MCellMoleculeReleasePropertyGroup MCellReleasePatternProperty MCellReleasePatternPropertyGroup
    cellblender_simulation.py          MCellRunSimulationProcessesProperty MCellRunSimulationPropertyGroup
    cellblender_surface_classes.py     MCellSurfaceClassPropertiesProperty MCellSurfaceClassesProperty MCellSurfaceClassesPropertyGroup
    cellblender_surface_regions.py     MCellModSurfRegionsProperty MCellModSurfRegionsPropertyGroup
    data_model.py                      None (only calls to other methods)
    parameter_system.py                Parameter_Data ParameterSystemPropertyGroup
"""


# These were added to support dynamic geometry export from Blender
# These should not be needed for non-Blender export.
has_blender = False
try:
  import bpy
  has_blender = True
except:
  pass


def write_obj_as_mdl ( scene_name, obj_name, points, faces, regions_dict, region_props, origin=None, file_name=None, partitions=False, instantiate=False ):
  # print ( "data_model_to_mdl.write_obj_as_mdl()" )
  # print ( "     region_props = " + str(region_props) )
  if file_name != None:
    out_file = open ( file_name, "w" )
    if partitions:
        out_file.write ( "PARTITION_X = [[-2.0 TO 2.0 STEP 0.5]]\n" )
        out_file.write ( "PARTITION_Y = [[-2.0 TO 2.0 STEP 0.5]]\n" )
        out_file.write ( "PARTITION_Z = [[-2.0 TO 2.0 STEP 0.5]]\n" )
        out_file.write ( "\n" )
    out_file.write ( "%s POLYGON_LIST\n" % (obj_name) )
    out_file.write ( "{\n" )
    out_file.write ( "  VERTEX_LIST\n" )
    out_file.write ( "  {\n" )
    for p in points:
        out_file.write ( "    [ " + str(p[0]) + ", " + str(p[1]) + ", " + str(p[2]) + " ]\n" );
    out_file.write ( "  }\n" )
    out_file.write ( "  ELEMENT_CONNECTIONS\n" )
    out_file.write ( "  {\n" )
    for f in faces:
        s = "    [ " + str(f[0]) + ", " + str(f[1]) + ", " + str(f[2]) + " ]\n"
        out_file.write ( s );
    out_file.write ( "  }\n" )

    if len(regions_dict) > 0:
        # Begin DEFINE_SURFACE_REGIONS block
        # See definitions on pages 17 (Region Command), 18 (Regional Surface Command), and 21 (MODIFY_SURFACE_REGIONS)
        # Define the faces that make up a region named 'top':
        #   regions_dict = { 'top': [1, 7] }
        # Define the surface classes applied to region 'top':
        #   region_props = { 'top': ['trans_a','absorb_bcd'] }

        out_file.write("  DEFINE_SURFACE_REGIONS\n")
        out_file.write("  {\n")

        region_names = [k for k in regions_dict.keys()]
        region_names.sort()
        for region_name in region_names:
            out_file.write("    %s\n" % (region_name))
            out_file.write("    {\n")
            out_file.write("      ELEMENT_LIST = " + str(regions_dict[region_name])+'\n')
            if region_name in region_props:
                props = region_props[region_name]
                for prop in props:
                    out_file.write("      SURFACE_CLASS = " + str(prop)+'\n')
            out_file.write("    }\n")

        # close DEFINE_SURFACE_REGIONS block
        out_file.write("  }\n")


    if origin != None:
        out_file.write ( "  TRANSLATE = [ %.15g, %.15g, %.15g ]\n" % (origin[0], origin[1], origin[2] ) )
    out_file.write ( "}\n" )
    if instantiate:
        out_file.write ( "\n" )
        out_file.write ( "INSTANTIATE " + scene_name + " OBJECT {\n" )
        out_file.write ( "  %s OBJECT %s {}\n" % (obj_name, obj_name) )
        out_file.write ( "}\n" )
    out_file.close()

# Import math to be available for user scripts
import math

# For debugging
import traceback

def write_mdl ( dm, file_name, scene_name='Scene' ):
    """ Write a data model to a named file (generally follows "export_mcell_mdl" ordering) """

    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
    print ( "Top of data_model_to_mdl.write_mdl() to " + str(file_name) )
    print ( "Data Model Keys: " + str( [k for k in dm['mcell'].keys()] ) )
    export_modular = ( dm['mcell']['simulation_control']['export_format'] == 'mcell_mdl_modular' )
    print ( "Export Modular = " + str(export_modular) )
    modular_path = None
    if export_modular:
      # Set the modular path
      modular_path = os.path.dirname(file_name)
    #print ( "Call Stack:" )
    #traceback.print_stack()
    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )

    # First check for any dynamic objects in the data model
    num_dynamic = len ( [ True for o in dm['mcell']['model_objects']['model_object_list'] if o['dynamic'] ] )

    f = open ( file_name, 'w' )
    # f.write ( "/* MDL Generated from Data Model */\n" )
    if ('mcell' in dm):
      mcell = dm['mcell']

      if 'model_objects' in mcell:
        # For some reason, the model object list appears to be sorted in the IO Mesh exporter
        # Sort them here to get the same result
        if True:
          mlist = mcell['model_objects']['model_object_list']
          obj_names = sorted ( [ o['name'] for o in mlist ] )
          sorted_mlist = []
          for n in obj_names:
            mo = [ o for o in mlist if o['name'] == n ][0]
            sorted_mlist.append ( mo )
          mcell['model_objects']['model_object_list'] = sorted_mlist

      if 'parameter_system' in mcell:
        ps = mcell['parameter_system']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name+'.parameters.mdl'), 'w' )
        write_parameter_system ( ps, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.parameters.mdl"\n\n' )

      if 'initialization' in mcell:
        init = mcell['initialization']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.initialization.mdl'), 'w' )
        write_initialization ( init, out_file )
        if 'partitions' in init:
          parts = mcell['initialization']['partitions']
          write_partitions ( parts, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.initialization.mdl"\n\n' )

      if 'define_molecules' in mcell:
        mols = mcell['define_molecules']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.molecules.mdl'), 'w' )
        write_molecules ( mols, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.molecules.mdl"\n\n' )

      if 'define_surface_classes' in mcell:
        sclasses = mcell['define_surface_classes']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.surface_classes.mdl'), 'w' )
        write_surface_classes ( sclasses, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.surface_classes.mdl"\n\n' )

      if 'define_reactions' in mcell:
        reacts = mcell['define_reactions']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.reactions.mdl'), 'w' )
        write_reactions ( reacts, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.reactions.mdl"\n\n' )

      if num_dynamic == 0:
        # MCell currently requires all objects to be either static or dynamic
        # So only write static objects if there are NO dynamic objects
        if ('model_objects' in mcell) and ('geometrical_objects' in mcell):
          objs = mcell['model_objects']
          geom = mcell['geometrical_objects']
          out_file = f
          if not (modular_path is None):
            out_file = open ( os.path.join(modular_path,scene_name + '.geometry.mdl'), 'w' )
          write_static_geometry ( objs, geom, out_file )
          if not (out_file == f):
            out_file.close()
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.geometry.mdl"\n\n' )
      else:
        # The geometry will be written to other files, just specify the list file name
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.geometry.mdl'), 'w' )
        out_file.write ( "DYNAMIC_GEOMETRY = \"dyn_geom_list.txt\"\n\n" )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.geometry.mdl"\n\n' )

      if 'modify_surface_regions' in mcell:
        modsurfrs = mcell['modify_surface_regions']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.mod_surf_regions.mdl'), 'w' )
        write_modify_surf_regions ( modsurfrs, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.mod_surf_regions.mdl"\n\n' )

      if 'define_release_patterns' in mcell:
        pats = mcell['define_release_patterns']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.release_patterns.mdl'), 'w' )
        write_release_patterns ( pats, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.release_patterns.mdl"\n\n' )



      # Figure out what we have to output based on:
      #   Static Geometry
      #   Dynamic Geometry
      #   Release Sites
      has_static_geometry = False
      has_dynamic_geometry = False
      has_release_sites = False
      if 'model_objects' in mcell:
        if 'model_object_list' in mcell['model_objects']:
          if len(mcell['model_objects']['model_object_list']) > 0:
            num_static = len(dm['mcell']['model_objects']['model_object_list']) - num_dynamic
            if num_static > 0:
              has_static_geometry = True
            if num_dynamic > 0:
              has_dynamic_geometry = True

      if 'release_sites' in mcell:
        rels = mcell['release_sites']
        if 'release_site_list' in rels:
          rlist = rels['release_site_list']
          if len(rlist) > 0:
            has_release_sites = True

      if has_dynamic_geometry:
        # Force static geometry off since both can't be defined in current MCell
        has_static_geometry = False

      # Actually write the MDL:
      out_file = f
      if not (modular_path is None):
        out_file = open ( os.path.join(modular_path,scene_name + '.instantiation.mdl'), 'w' )

      if has_static_geometry or has_release_sites:
        # Put both together into the same INSTANTIATE block
        block_name = scene_name
        if has_dynamic_geometry:
          # The dynamic geometry uses the name "Scene" so choose something else here
          block_name = "Releases"

        out_file.write ( "INSTANTIATE " + block_name + " OBJECT\n" )
        out_file.write ( "{\n" )
        if has_static_geometry:
          objs = None
          geom = None
          if 'model_objects' in mcell:
            objs = mcell['model_objects']
          if 'geometrical_objects' in mcell:
            geom = mcell['geometrical_objects']
          write_static_instances ( scene_name, objs, geom, out_file )

        if has_release_sites:
          rels = mcell['release_sites']
          write_release_sites ( scene_name, rels, mcell['define_molecules'], out_file )

        out_file.write ( "}\n\n" )

        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.instantiation.mdl"\n\n' )


      f.write("sprintf(seed,\"%05g\",SEED)\n\n")



      if 'viz_output' in mcell:
        vizout = mcell['viz_output']
        mols = None
        if ('define_molecules' in mcell):
          mols = mcell['define_molecules']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.viz_output.mdl'), 'w' )
        write_viz_out ( scene_name, vizout, mols, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.viz_output.mdl"\n\n' )

      if 'reaction_data_output' in mcell:
        reactout = mcell['reaction_data_output']
        mols = None
        if ('define_molecules' in mcell):
          mols = mcell['define_molecules']
        time_step = ""
        if 'initialization' in mcell:
          init = mcell['initialization']
          if "time_step" in init:
            time_step = init['time_step']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.rxn_output.mdl'), 'w' )
        write_react_out ( scene_name, reactout, mols, time_step, out_file )
        if not (out_file == f):
          out_file.close()
          f.write ( 'INCLUDE_FILE = "' + scene_name + '.rxn_output.mdl"\n\n' )

    f.close()

    # Check for any dynamic objects, and update MDL as needed

    num_dynamic = len ( [ True for o in dm['mcell']['model_objects']['model_object_list'] if o['dynamic'] ] )
    if num_dynamic > 0:
    
      # This code must add the following to each directory where MDL is written:
      #   dyn_geom_list.txt
      #   dynamic_geometry directory containing <object_name>_frame_#.mdl files
      # This code must also update the existing MDL files
      # For a non-swept project, this should look like:
      #   blend_files/
      #   blend_files/mcell
      #              /mcell/output_data
      #              /mcell/output_data
      #              /mcell/output_data/.../
      #                    /output_data/.../react_data/...
      #                    /output_data/.../viz_data/...
      #                    /output_data/.../Scene.main.mdl       // MDL file (along with others)
      #                    /output_data/.../dyn_geom_list.txt    // List of frame files relative to output_data
      #                    /output_data/.../dynamic_geometry     // Location of actual frame files
      #                                /.../dynamic_geometry/Obj_frame_0.mdl
      #                                /.../dynamic_geometry/Obj_frame_1.mdl
      #                                   :
      #                                /.../dynamic_geometry/Obj_frame_n.mdl
      #
      # For swept projects, there will be additional directories (...) appended directly after "output_data".


      filepath = os.path.dirname(file_name)

      context = None
      if has_blender:
          context = bpy.context

      print ( "Exporting dynamic objects from data_model_to_mdl.write_mdl() to " + str(filepath) )
      print ( "  file_name = " + str(file_name) )

      # scene_name = "Scene"
      fc = None
      if has_blender:
          # Over-ride the default or passed scene_name when in Blender
          # Filter or replace problem characters (like space, ...)
          scene_name = context.scene.name.replace(" ", "_")

          # Save the current frame to restore later
          fc = context.scene.frame_current

      # Generate the dynamic geometry

      geom_list_name = 'dyn_geom_list.txt'
      geom_list_file = open(os.path.join(filepath,geom_list_name), "w", encoding="utf8", newline="\n")
      path_to_dg_files = os.path.join ( filepath, "dynamic_geometry" )
      if not os.path.exists(path_to_dg_files):
          os.makedirs(path_to_dg_files)

      iterations = None
      time_step = None
      if has_blender:
          iterations = context.scene.mcell.initialization.iterations.get_value()
          time_step = context.scene.mcell.initialization.time_step.get_value()
      else:
          # Note that these conversions might not work if these are expressions.
          # In that case, parameter evaluation will have to be done to get a value.
          # For now, assume that they're plain numeric values.
          iterations = int(dm['mcell']['initialization']['iterations'])
          time_step  = float(dm['mcell']['initialization']['time_step'])

      print ( "iterations = " + str(iterations) + ", time_step = " + str(time_step) )

      # Build the script list first as a dictionary by object names so they aren't read at every iteration
      # It might also be efficient if these could be precompiled at this time (rather than in the loop).
      script_dict = {}
      print ( "\n\nBuilding Script List:" )
      if ('mcell' in dm) and ('scripting' in dm['mcell']) and ('script_texts' in dm['mcell']['scripting']):
          mcell = dm['mcell']
          scr_txts = mcell['scripting']['script_texts']
          # print ( "Script text names: " + str(scr_txts.keys()) )

          if ('model_objects' in mcell) and ('model_object_list' in mcell['model_objects']):
              mo_list = mcell['model_objects']['model_object_list']
              for obj in mo_list:
                  if obj['dynamic']:
                      if len(obj['script_name']) > 0:
                          script_name = obj['script_name']
                          script_text = scr_txts[script_name]
                          compiled_text = compile ( script_text, '<string>', 'exec' )
                          script_dict[script_name] = compiled_text

      # Save state of mol_viz_enable and disable mol viz during frame change for dynamic geometry
      mol_viz_state = None
      if has_blender:
          mol_viz_state = context.scene.mcell.mol_viz.mol_viz_enable
          context.scene.mcell.mol_viz.mol_viz_enable = False

      print ( "\n\nStepping through Frames:" )
      for frame_number in range(iterations+1):
          ####################################################################
          #
          #  This section essentially defines the interface to the user's
          #  dynamic geometry code. Right now it's being done through 7 global
          #  variables which will be in the user's environment when they run:
          #
          #     frame_number
          #     time_step
          #     points[]
          #     faces[]
          #     regions_dict[]
          #     region_props[]
          #     origin[]
          #
          #  The user code gets the frame number as input and fills in both the
          #  points and faces arrays (lists). The format is fairly standard with
          #  each point being a list of 3 double values [x, y, z], and with each
          #  face being a list of 3 point indexes defining a triangle with outward
          #  facing normals using the right hand rule. The index values are the
          #  integer offsets into the points array starting with index 0.
          #  This is a very primitive interface, and it may be subject to change.
          #
          ####################################################################
          if (frame_number % 100) == 0:
              print ( "  Writing frame " + str(frame_number) )


          if has_blender:
              # Set the frame number for Blender
              context.scene.frame_set(frame_number)

          # Write out the individual MDL files for each dynamic object at this frame
          if ('mcell' in dm) and ('model_objects' in mcell) and ('model_object_list' in mcell['model_objects']):
            for obj in dm['mcell']['model_objects']['model_object_list']:
              # MCell currently requires all objects to be either static or dynamic
              # So if we're here, that means ALL objects should be written as dynamic
              if   True   or obj['dynamic']:
                  # print ( "  Frame " + str(frame_number) + ", Saving dynamic geometry for object " + obj['name'] + " with script \"" + obj['script_name'] + "\"" )
                  points = []            # The list "points" is expected by the user's script
                  faces = []             # The list "faces" is expected by the user's script
                  regions_dict = {}      # The dict "regions_dict" is expected by the user's script
                  region_props = {}      # The dict "region_props" is expected by the user's script
                  origin = [0,0,0]       # The list "origin" is expected by the user's script

                  if len(obj['script_name']) > 0:
                      # Let the script create the geometry
                      #print ( "   Build object mesh from user script for frame " + str(frame_number) )
                      #script_text = script_dict[obj.script_name]
                      #print ( 80*"=" )
                      #print ( script_text )
                      #print ( 80*"=" )
                      # exec ( script_dict[obj.script_name], locals() )
                      #print ( "Before script: region_props = " + str(region_props) )
                      exec ( script_dict[obj['script_name']] )
                      #print ( "After  script: region_props = " + str(region_props) )
                  elif has_blender:
                      # Get the geometry from the object (presumably animated by Blender)

                      #print ( "   Build object mesh from Blender object for frame " + str(frame_number) )
                      import mathutils

                      geom_obj = context.scene.objects[obj['name']]
                      mesh = geom_obj.to_mesh(context.scene, True, 'PREVIEW', calc_tessface=False)
                      mesh.transform(mathutils.Matrix() * geom_obj.matrix_world)
                      points = [v.co for v in mesh.vertices]
                      faces = [f.vertices for f in mesh.polygons]
                      regions_dict = geom_obj.mcell.get_regions_dictionary(geom_obj)
                      del mesh
                  else:
                      # Get the geometry from the data model (either from the frame list or from static geometry)
                      #print ( "   Build object mesh without Blender for frame " + str(frame_number) )
                      if ('mcell' in dm) and ('geometrical_objects' in dm['mcell']) and ('object_list' in dm['mcell']['geometrical_objects']):
                          mcell = dm['mcell']
                          for o in mcell['geometrical_objects']['object_list']:
                              if o['name'] == obj['name']:
                                  #print ( "    Found object " )
                                  if ('frame_list' in o) and (len(o['frame_list']) > 0):
                                      # This object has non-empty frame list data to use
                                      #print ( "      Object " + str(o['name']) + ": frame_list length = " + str(len(o['frame_list'])) )
                                      frame = None
                                      if frame_number >= len(o['frame_list']):
                                          # Hold the last frame forever
                                          frame = o['frame_list'][-1]
                                      else:
                                          # Get the frame for this iteration
                                          frame = o['frame_list'][frame_number]
                                      points = frame['vertex_list']
                                      faces = frame['element_connections']
                                      origin = frame['location']
                                  else:
                                      # Use the object's original static geometry from the data model
                                      #print ( "      Object " + str(o['name']) + " has no frame_list" )
                                      points = o['vertex_list']
                                      faces = o['element_connections']
                                      origin = o['location']
                                  #print ( "    Found object " + str(o['name']) + " with zmax of " + str(max([v[2] for v in o['vertex_list']])) )
                                  if 'define_surface_regions' in o:
                                      # This object has surface regions
                                      regions_dict = {}
                                      for reg in o['define_surface_regions']:
                                          regions_dict[reg['name']] = reg['include_elements']

                  f_name = "%s_frame_%d.mdl"%(obj['name'],frame_number)
                  full_file_name = os.path.join(path_to_dg_files,f_name)
                  write_obj_as_mdl ( scene_name, obj['name'], points, faces, regions_dict, region_props, origin=origin, file_name=full_file_name, partitions=False, instantiate=False )
                  #geom_list_file.write('%.9g %s\n' % (frame_number*time_step, os.path.join(".","dynamic_geometry",f_name)))

          # Write out the "master" MDL file for this frame

          frame_file_name = os.path.join(".","dynamic_geometry","frame_%d.mdl"%(frame_number))
          full_frame_file_name = os.path.join(path_to_dg_files,"frame_%d.mdl"%(frame_number))
          frame_file = open(full_frame_file_name, "w", encoding="utf8", newline="\n")

          # Write the INCLUDE statements
          if ('mcell' in dm) and ('model_objects' in mcell) and ('model_object_list' in mcell['model_objects']):
            for obj in dm['mcell']['model_objects']['model_object_list']:
              if   True   or obj['dynamic']:
                  f_name = "%s_frame_%d.mdl"%(obj['name'],frame_number)
                  frame_file.write ( "INCLUDE_FILE = \"%s\"\n" % (f_name) )

          # Write the INSTANTIATE statement for this frame
          frame_file.write ( "INSTANTIATE " + scene_name + " OBJECT {  /* write_mdl for each frame */\n" )

          if ('mcell' in dm) and ('model_objects' in mcell) and ('model_object_list' in mcell['model_objects']):
            for obj in dm['mcell']['model_objects']['model_object_list']:
              if   True   or obj['dynamic']:
                  frame_file.write ( "  %s OBJECT %s {}\n" % (obj['name'], obj['name']) )

          frame_file.write ( "}\n" )
          frame_file.close()

          geom_list_file.write('%.9g %s\n' % (frame_number*time_step, frame_file_name))

      geom_list_file.close()

      if has_blender:
          # Restore setting for mol viz
          context.scene.mcell.mol_viz.mol_viz_enable = mol_viz_state

          # Restore the current frame
          context.scene.frame_set(fc)





def write_parameter_system ( ps, f ):
    if 'model_parameters' in ps:

      mplist = ps['model_parameters']

      if ('_extras' in ps) and ('ordered_id_names' in ps['_extras']):
        # Re-order the model parameters list (mplist) for proper dependency order based on ordered_id_names
        unordered_mplist = [ p for p in mplist ]  # Make a copy first since the algorithm removes items from this list!!
        ordered_mplist = []
        # First get all the parameters that match the ids in order (leave remaining in original list)
        ordered_ids = ps['_extras']['ordered_id_names']
        for ordered_id in ordered_ids:
          for p in unordered_mplist:
            if ('_extras' in p) and ('par_id_name' in p['_extras']):
              if p['_extras']['par_id_name'] == ordered_id:
                ordered_mplist.append(p)
                unordered_mplist.remove(p)
                break
        # Finish by adding all remaing items to the new list
        for p in unordered_mplist:
          ordered_mplist.append(p)
        # Replace the old list by the new sorted list
        mplist = ordered_mplist
      else:
        # This is where the parameters could be placed in dependency order without relying on _extras fields
        # There should be no data models that don't have those fields, so pass for now.
        # If this should happen, MCell should either handle the dependencies or flag any forward references.
        pass

      if len(mplist) > 0:
        f.write ( "/* DEFINE PARAMETERS */\n" );

        for p in mplist:
          print ( "   Parameter " + str(p['par_name']) + " = " + "%.15g"%(p['_extras']['par_value']) )

          # Write the name = val portion of the definition ("True" to export expressions, "False" to export values)
          if True:
            f.write ( p['par_name'] + " = " + p['par_expression'] )
          else:
            f.write ( p['par_name'] + " = " + "%.15g"%(p['extras']['par_value']) )

          # Write the optional description and units in a comment (if non empty)
          if (len(p['par_description']) > 0) or (len(p['par_units']) > 0):
            f.write ( "    /* " )
            if len(p['par_description']) > 0:
              f.write ( p['par_description'] + " " )
            if len(p['par_units']) > 0:
              f.write ( "   units=" + p['par_units'] )
            f.write ( " */\n" )
          else:
            f.write ( "\n" )
            
        f.write ( "\n" );


def write_initialization ( init, f ):
    # f.write ( "\n/* This should break the checksums for testing */\n" )

    write_dm_str_val ( init, f, 'iterations',                'ITERATIONS' )
    write_dm_str_val ( init, f, 'time_step',                 'TIME_STEP' )
    write_dm_str_val ( init, f, 'vacancy_search_distance',   'VACANCY_SEARCH_DISTANCE', blank_default='10' )
    f.write ( "\n" )
    write_dm_str_val ( init, f, 'time_step_max',             'TIME_STEP_MAX' )
    write_dm_str_val ( init, f, 'space_step',                'SPACE_STEP' )
    write_dm_str_val ( init, f, 'interaction_radius',        'INTERACTION_RADIUS' )
    write_dm_str_val ( init, f, 'radial_directions',         'RADIAL_DIRECTIONS' )
    write_dm_str_val ( init, f, 'radial_subdivisions',       'RADIAL_SUBDIVISIONS' )
    write_dm_str_val ( init, f, 'surface_grid_density',      'SURFACE_GRID_DENSITY' )
    write_dm_str_val ( init, f, 'accurate_3d_reactions',     'ACCURATE_3D_REACTIONS' )
    write_dm_str_val ( init, f, 'center_molecules_on_grid',  'CENTER_MOLECULES_ON_GRID' )
    write_dm_str_val ( init, f, 'microscopic_reversibility', 'MICROSCOPIC_REVERSIBILITY' )


    if 'notifications' in init:
      f.write ( "\n" )
      f.write ( "NOTIFICATIONS\n{\n" )
      notifications = init['notifications']
      write_notifications ( notifications, f )
      f.write ( "}\n" )

    if 'warnings' in init:
      f.write ( "\n" )
      f.write ( "WARNINGS\n{\n" )
      warnings = init['warnings']
      write_warnings ( warnings, f )
      f.write ( "}\n" )

    f.write ( "\n" );


def write_notifications ( notifications, f ):
    individual = True
    if 'all_notifications' in notifications:
      if notifications['all_notifications'] == 'INDIVIDUAL':
        individual = True
      else:
        individual = False
        write_dm_str_val ( notifications, f, 'all_notifications', 'ALL_NOTIFICATIONS', indent="   " )

    if individual:
      if 'probability_report' in notifications:
        if notifications['probability_report'] == 'THRESHOLD':
          write_dm_str_val ( notifications, f, 'probability_report_threshold', 'PROBABILITY_REPORT_THRESHOLD', indent="   " )
        else:
          write_dm_str_val ( notifications, f, 'probability_report',        'PROBABILITY_REPORT', indent="   " )
      write_dm_str_val ( notifications, f, 'diffusion_constant_report', 'DIFFUSION_CONSTANT_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'file_output_report', 'FILE_OUTPUT_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'final_summary', 'FINAL_SUMMARY', indent="   " )
      write_dm_on_off  ( notifications, f, 'iteration_report', 'ITERATION_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'partition_location_report', 'PARTITION_LOCATION_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'varying_probability_report', 'VARYING_PROBABILITY_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'progress_report', 'PROGRESS_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'release_event_report', 'RELEASE_EVENT_REPORT', indent="   " )
      write_dm_on_off  ( notifications, f, 'molecule_collision_report', 'MOLECULE_COLLISION_REPORT', indent="   " )


def write_warnings ( warnings, f ):
    individual = True
    if 'all_warnings' in warnings:
      if warnings['all_warnings'] == 'INDIVIDUAL':
        individual = True
      else:
        individual = False
        write_dm_str_val ( warnings, f, 'all_warnings', 'ALL_WARNINGS', indent="   " )

    if individual:
      write_dm_str_val ( warnings, f, 'large_molecular_displacement', 'LARGE_MOLECULAR_DISPLACEMENT', indent="   " )
      write_dm_str_val ( warnings, f, 'degenerate_polygons', 'DEGENERATE_POLYGONS', indent="   " )
      write_dm_str_val ( warnings, f, 'negative_diffusion_constant', 'NEGATIVE_DIFFUSION_CONSTANT', indent="   " )
      write_dm_str_val ( warnings, f, 'missing_surface_orientation', 'MISSING_SURFACE_ORIENTATION', indent="   " )
      write_dm_str_val ( warnings, f, 'negative_reaction_rate', 'NEGATIVE_REACTION_RATE', indent="   " )
      write_dm_str_val ( warnings, f, 'useless_volume_orientation', 'USELESS_VOLUME_ORIENTATION', indent="   " )
      write_dm_str_val ( warnings, f, 'high_reaction_probability', 'HIGH_REACTION_PROBABILITY', indent="   " )

      write_dm_str_val ( warnings, f, 'lifetime_too_short', 'LIFETIME_TOO_SHORT', indent="   " )
      if 'lifetime_too_short' in warnings:
        if warnings['lifetime_too_short'] == 'WARNING':
          write_dm_str_val ( warnings, f, 'lifetime_threshold', 'LIFETIME_THRESHOLD', indent="   " )

      write_dm_str_val ( warnings, f, 'missed_reactions', 'MISSED_REACTIONS', indent="   " )
      if 'missed_reactions' in warnings:
        if warnings['missed_reactions'] == 'WARNING':
          write_dm_str_val ( warnings, f, 'missed_reaction_threshold', 'MISSED_REACTION_THRESHOLD', indent="   " )


def write_partitions ( parts, f ):
    if 'include' in parts:
      if parts['include']:
        # Note that partition values are floats in CellBlender, but exported as strings for future compatibility with expressions
        #f.write ( "PARTITION_X = [[%s TO %s STEP %s]]\n" % ( parts['x_start'], parts['x_end'], parts['x_step'] ) )
        #f.write ( "PARTITION_Y = [[%s TO %s STEP %s]]\n" % ( parts['y_start'], parts['y_end'], parts['y_step'] ) )
        #f.write ( "PARTITION_Z = [[%s TO %s STEP %s]]\n" % ( parts['z_start'], parts['z_end'], parts['z_step'] ) )

        # Use forced floats
        f.write ( "PARTITION_X = [[%s TO %s STEP %s]]\n" % ( as_float_str(parts,'x_start','PARTITION_VAL'), as_float_str(parts,'x_end','PARTITION_VAL'), as_float_str(parts,'x_step','PARTITION_VAL') ) )
        f.write ( "PARTITION_Y = [[%s TO %s STEP %s]]\n" % ( as_float_str(parts,'y_start','PARTITION_VAL'), as_float_str(parts,'y_end','PARTITION_VAL'), as_float_str(parts,'y_step','PARTITION_VAL') ) )
        f.write ( "PARTITION_Z = [[%s TO %s STEP %s]]\n" % ( as_float_str(parts,'z_start','PARTITION_VAL'), as_float_str(parts,'z_end','PARTITION_VAL'), as_float_str(parts,'z_step','PARTITION_VAL') ) )
        f.write ( "\n" )




def write_molecules ( mols, f ):
    if 'molecule_list' in mols:
      mlist = mols['molecule_list']
      if len(mlist) > 0:
        f.write ( "DEFINE_MOLECULES\n" )
        f.write ( "{\n" )
        for m in mlist:
          f.write ( "  %s\n" % m['mol_name'] )
          f.write ( "  {\n" )
          if m['mol_type'] == '2D':
            f.write ( "    DIFFUSION_CONSTANT_2D = %s\n" % m['diffusion_constant'] )
          else:
            f.write ( "    DIFFUSION_CONSTANT_3D = %s\n" % m['diffusion_constant'] )
          if 'custom_time_step' in m:
            if len(m['custom_time_step']) > 0:
              f.write ( "    CUSTOM_TIME_STEP = %s\n" % m['custom_time_step'] )
          if 'custom_space_step' in m:
            if len(m['custom_space_step']) > 0:
              f.write ( "    CUSTOM_SPACE_STEP = %s\n" % m['custom_space_step'] )
          if 'target_only' in m:
            if m['target_only']:
              f.write("    TARGET_ONLY\n")
          f.write("  }\n")
        f.write ( "}\n" )
      f.write ( "\n" );


def write_surface_classes ( sclasses, f ):
    if 'surface_class_list' in sclasses:
      sclist = sclasses['surface_class_list']
      if len(sclist) > 0:
        f.write ( "DEFINE_SURFACE_CLASSES\n" )
        f.write ( "{\n" )
        for sc in sclist:
          f.write ( "  %s\n" % (sc['name']) )
          f.write ( "  {\n" )
          if 'surface_class_prop_list' in sc:
            for scp in sc['surface_class_prop_list']:
              mol = scp['molecule']
              if scp['affected_mols'] != 'SINGLE':
                  mol = scp['affected_mols']
              if scp['surf_class_type'] == 'CLAMP_CONCENTRATION':
                  clamp_value = scp['clamp_value']
                  f.write("    %s" % scp['surf_class_type'])
                  f.write(" %s%s = %s\n" % (mol,scp['surf_class_orient'],scp['clamp_value']))
              else:
                  f.write("    %s = %s%s\n" % (scp['surf_class_type'],mol,scp['surf_class_orient']))
          f.write ( "  }\n" )
        f.write ( "}\n" )
        f.write("\n")


def write_reactions ( reacts, f ):
    if 'reaction_list' in reacts:
      rlist = reacts['reaction_list']
      if len(rlist) > 0:
        f.write ( "DEFINE_REACTIONS\n" )
        f.write ( "{\n" )
        for r in rlist:
          f.write("  %s " % (r['name']))
          if r['rxn_type'] == "irreversible":
            if r['variable_rate_switch'] and r['variable_rate_valid']:
              variable_rate_name = r['variable_rate']
              f.write('["%s"]' % (variable_rate_name))
              ## Create the actual variable rate file and write to it
              vrf = open(variable_rate_name, "w")
              vrf.write ( r['variable_rate_text'] )
              #with open(variable_rate_name, "w", encoding="utf8",
              #          newline="\n") as variable_out_file:
              #    variable_out_file.write(r['variable_rate_text'])
            else:
              f.write ( "[%s]" % ( r['fwd_rate'] ) )
          else:
            f.write ( "[>%s, <%s]" % ( r['fwd_rate'], r['bkwd_rate'] ) )
          if 'rxn_name' in r:
            if len(r['rxn_name']) > 0:
              f.write ( " : %s" % (r['rxn_name']) )
          f.write("\n")
        f.write ( "}\n" )
        f.write("\n")


def write_static_geometry ( objs, geom, f ):
    if 'object_list' in geom:
      glist = geom['object_list']
      if len(glist) > 0:
        olist = objs['model_object_list']
        print ( "objs: " + str( [ o['name'] for o in olist ] ) )
        print ( "geos: " + str( [ o['name'] for o in glist ] ) )

        # For some reason, these appear to be sorted in the IO Mesh exporter
        # Sort them here to get the same result
        gnames = sorted ( [ o['name'] for o in olist ] )
        sorted_glist = []
        for gn in gnames:
          go = [ o for o in glist if o['name'] == gn ][0]
          sorted_glist.append ( go )
        glist = sorted_glist
        print ( "geos: " + str( [ o['name'] for o in glist ] ) )

        for g in glist:
          obj = [ o for o in objs['model_object_list'] if o['name'] == g['name'] ][0]
          # MCell currently requires all objects to be either static or dynamic
          # Since this is "write_static_geometry", then assume all objects are
          #   to be written as static regardless of their obj['dynamic'] flag
          if False and obj['dynamic']:
            # Don't write dynamic objects here
            # This branch is here for future writing of only static objects
            pass
          else:
            # Write static objects here
            loc_x = 0.0
            loc_y = 0.0
            loc_z = 0.0
            if 'location' in g:
              loc_x = g['location'][0]
              loc_y = g['location'][1]
              loc_z = g['location'][2]
            f.write ( "%s POLYGON_LIST\n" % g['name'] )
            f.write ( "{\n" )
            if 'vertex_list' in g:
              f.write ( "  VERTEX_LIST\n" )
              f.write ( "  {\n" )
              for v in g['vertex_list']:
                f.write ( "    [ %.15g, %.15g, %.15g ]\n" % ( loc_x+v[0], loc_y+v[1], loc_z+v[2] ) )
              f.write ( "  }\n" )
            if 'element_connections' in g:
              f.write ( "  ELEMENT_CONNECTIONS\n" )
              f.write ( "  {\n" )
              for c in g['element_connections']:
                f.write ( "    [ %d, %d, %d ]\n" % ( c[0], c[1], c[2] ) )
              f.write ( "  }\n" )
            if 'define_surface_regions' in g:
              f.write ( "  DEFINE_SURFACE_REGIONS\n" )
              f.write ( "  {\n" )
              for r in g['define_surface_regions']:
                f.write ( "    %s\n" % r['name'] )
                f.write ( "    {\n" )
                if 'include_elements' in r:
                  int_regs = [ int(r) for r in r['include_elements'] ]
                  f.write ( "      ELEMENT_LIST = " + str(int_regs) + "\n" )
                f.write ( "    }\n" )
              f.write ( "  }\n" )
            f.write ( "}\n")
            f.write ( "\n" );


def write_static_instances ( scene_name, objs, geom, f, write_block=False ):
    #TODO Note that the use of "Scene" here is a temporary measure!!!!
    if (objs != None) and (geom != None):
      if 'model_object_list' in objs:
        num_static = 0
        for o in objs['model_object_list']:
          if not o['dynamic']:
            num_static += 1
        if num_static > 0:
          if write_block:
            f.write ( "INSTANTIATE " + scene_name + " OBJECT\n" )
            f.write ( "{\n" )
          for o in objs['model_object_list']:
            if not o['dynamic']:
              f.write ( "  %s OBJECT %s {}\n" % (o['name'], o['name']) )
          if write_block:
            f.write ( "}\n" )
            f.write("\n")


def instance_object_expr(scene_name, expression):
    """ Converts an object expression into an instantiated MDL object

    This function was copied from:
       io_mesh_mcell_mdl/export_mcell_mdl.py
    It was modified to take a "scene_name" rather than a context.

    This function converts an object specification coming from
    the GUI into a fully qualified (instantiated) MDL expression.
    E.g., if the instantiated object is named *Scene*

      - an object *Cube* will be converted to *Scene.Cube* and
      - an expression *Cube + Sphere* will be converted to
        "Scene.Cube + Scene.Sphere"

    NOTE (Markus): I am not sure if this function isn't a bit
    too complex for the task (i.e. regular expressions and all)
    but perhaps it's fine. Time will tell.
    """

    token_spec = [
        ("ID", r"[A-Za-z]+[0-9A-Za-z_.]*(\[[A-Za-z]+[0-9A-Za-z_.]*\])?"),
                              # Identifiers
        ("PAR", r"[\(\)]"),   # Parentheses
        ("OP", r"[\+\*\-]"),  # Boolean operators
        ("SKIP", r"[ \t]"),   # Skip over spaces and tabs
    ]
    token_regex = "|".join("(?P<%s>%s)" % pair for pair in token_spec)
    get_token = re.compile(token_regex).match

    instantiated_expression = ""
    pos = 0
    line_start = 0
    m = get_token(expression)
    while m:
        token_type = m.lastgroup
        if token_type != "SKIP":
            val = m.group(token_type)

            if token_type == "ID":
                val = scene_name + "." + val
            elif token_type == "OP":
                val = " " + val + " "

            instantiated_expression = instantiated_expression + val

        pos = m.end()
        m = get_token(expression, pos)

    if pos != len(expression):
        pass

    return instantiated_expression


def write_release_sites ( scene_name, rels, mols, f, instantiate_name=None ):
    #TODO Note that the use of "Scene" here is a temporary measure!!!!
    if instantiate_name != None:
      f.write ( "INSTANTIATE " + instantiate_name + " OBJECT\n" )
      f.write ( "{\n" )

    if rels != None:
      if 'release_site_list' in rels:
        rlist = rels['release_site_list']
        if len(rlist) > 0:
          for r in rlist:
            f.write ( "  %s RELEASE_SITE\n" % (r['name']) )
            f.write ( "  {\n" )
            list_type = False

            # First get the molecule to be released (maybe the Molecule List should have been a dictionary keyed on mol_name?)
            mlist = mols['molecule_list']
            mol = None
            for m in mlist:
              if m['mol_name'] == r['molecule']:
                mol = m
                break

            # Next, handle the release shape
            if ((r['shape'] == 'CUBIC') |
                (r['shape'] == 'SPHERICAL') |
                (r['shape'] == 'SPHERICAL_SHELL')):
              # Output MDL for releasing in a non-object shape pattern
              f.write("   SHAPE = %s\n" % (r['shape']))
              f.write("   LOCATION = [%s, %s, %s]\n" % (r['location_x'],r['location_y'],r['location_z']))
              f.write("   SITE_DIAMETER = %s\n" % (r['site_diameter']))
            elif r['shape'] == "OBJECT":
              # Output MDL for releasing in or on and object
              #TODO Note that the use of "Scene" here for object names is a temporary measure!!!!
              f.write ( "   SHAPE = %s\n" % ( instance_object_expr(scene_name, r['object_expr']) ) )
            elif r['shape'] == "LIST":
              # Output MDL for releasing a list of molecules
              # Note that the CellBlender List interface (and data model) only allows one molecule type for each list
              # MDL, however, allows each point to have a different molecule type
              list_type = True
              mol_expr = r['molecule']
              if mol:
                if mol['mol_type'] == '2D':
                  mol_expr = "%s%s" % (r['molecule'],r['orient'])
                else:
                  mol_expr = "%s" % (r['molecule'])
              f.write ( "   SHAPE = LIST\n" )
              f.write ( "   SITE_DIAMETER = %s\n" % (r['site_diameter']))
              f.write ( "   MOLECULE_POSITIONS\n" )
              f.write ( "   {\n" )
              if 'points_list' in r:
                for p in r['points_list']:
                  f.write ( "     %s [%.15g, %.15g, %.15g]\n" % (mol_expr, p[0], p[1], p[2]) )
              f.write ( "   }\n" )

            if (not list_type) and mol:

              # Write out the molecule expression

              if mol['mol_type'] == '2D':
                f.write("   MOLECULE = %s%s\n" % (r['molecule'],r['orient']))
              else:
                f.write("   MOLECULE = %s\n" % (r['molecule']))

              # Now write out the quantity and probability (when not a list)

              if r['quantity_type'] == 'NUMBER_TO_RELEASE':
                f.write("   NUMBER_TO_RELEASE = %s\n" % (r['quantity']))
              elif r['quantity_type'] == 'GAUSSIAN_RELEASE_NUMBER':
                f.write("   GAUSSIAN_RELEASE_NUMBER\n")
                f.write("   {\n")
                f.write("        MEAN_NUMBER = %s\n" % (r['quantity']))
                f.write("        STANDARD_DEVIATION = %s\n" % (r['stddev']))
                f.write("      }\n")
              elif r['quantity_type'] == 'DENSITY':
                if mol:
                  if mol['mol_type'] == '2D':
                    f.write("   DENSITY = %s\n" % (r['quantity']))
                  else:
                    f.write("   CONCENTRATION = %s\n" % (r['quantity']))

            # Write the release probability for all cases (including lists)

            f.write("   RELEASE_PROBABILITY = %s\n" % (r['release_probability']))
            if len(r['pattern']) > 0:
              f.write("   RELEASE_PATTERN = %s\n" % (r['pattern']))

            f.write ( "  }\n" )

    if instantiate_name != None:
      f.write ( "}\n" )
      f.write("\n")


def write_modify_surf_regions ( modsurfrs, f ):
    if 'modify_surface_regions_list' in modsurfrs:
      msrlist = modsurfrs['modify_surface_regions_list']
      if len(msrlist) > 0:
        f.write ( "MODIFY_SURFACE_REGIONS\n" )
        f.write ( "{\n" )
        for msr in msrlist:
          surf = "ALL"
          if len(msr['region_name']) > 0:
            surf = msr['region_name']
          f.write ( "  %s[%s]\n" % (msr['object_name'],surf) )
          f.write ( "  {\n" )
          f.write ( "    SURFACE_CLASS = %s\n" % (msr['surf_class_name']) )
          f.write ( "  }\n" )
        f.write ( "}\n" )
        f.write("\n")


def write_release_patterns ( pats, f ):
    if 'release_pattern_list' in pats:
      plist = pats['release_pattern_list']
      if len(plist) > 0:
        for p in plist:
          f.write ( "DEFINE_RELEASE_PATTERN %s\n" % (p['name']) )
          f.write ( "{\n" )
          if ('delay' in p) and (len(p['delay']) > 0): f.write ( "  DELAY = %s\n" % (p['delay']) )
          if ('release_interval' in p) and (len(p['release_interval']) > 0): f.write ( "  RELEASE_INTERVAL = %s\n" % (p['release_interval']) )
          if ('train_duration' in p) and (len(p['train_duration']) > 0): f.write ( "  TRAIN_DURATION = %s\n" % (p['train_duration']) )
          if ('train_interval' in p) and (len(p['train_interval']) > 0): f.write ( "  TRAIN_INTERVAL = %s\n" % (p['train_interval']) )
          if ('number_of_trains' in p) and (len(p['number_of_trains']) > 0): f.write ( "  NUMBER_OF_TRAINS = %s\n" % (p['number_of_trains']) )
          f.write ( "}\n" )
          f.write("\n")


def write_viz_out ( scene_name, vizout, mols, f ):

    mol_list_string = ""

    if vizout['export_all']:
      # Don't check the molecules just output all of them
      mol_list_string = "ALL_MOLECULES"
    elif (mols != None):
      # There might be some (or all) molecules with viz output enabled ... need to check
      if 'molecule_list' in mols:
        mlist = mols['molecule_list']
        if len(mlist) > 0:
          for m in mlist:
            if 'export_viz' in m:
              if m['export_viz']:
                mol_list_string += " " + m['mol_name']
      mol_list_string = mol_list_string.strip()

    # Write a visualization block only if needed
    if len(mol_list_string) > 0:
      f.write ( "VIZ_OUTPUT\n" )
      f.write ( "{\n" )
      f.write ( "  MODE = CELLBLENDER\n" )
      #TODO Note that the use of "Scene" here for file output is a temporary measure!!!!
      f.write ( "  FILENAME = \"./viz_data/seed_\" & seed & \"/" + scene_name + "\"\n" )
      f.write ( "  MOLECULES\n" )
      f.write ( "  {\n" )
      f.write ( "    NAME_LIST {%s}\n" % (mol_list_string) )
      if vizout['all_iterations']:
        f.write ( "    ITERATION_NUMBERS {ALL_DATA @ ALL_ITERATIONS}\n" )
      else:
        f.write ( "    ITERATION_NUMBERS {ALL_DATA @ [[%s TO %s STEP %s]]}\n" % (vizout['start'], vizout['end'], vizout['step']) )
      f.write ( "  }\n" )
      f.write ( "}\n" )
      f.write ( "\n" );


def write_react_out ( scene_name, rout, mols, time_step, f ):

    if ("reaction_output_list" in rout) and (len(rout["reaction_output_list"]) > 0):
        context_scene_name = scene_name

        f.write("REACTION_DATA_OUTPUT\n{\n")

        if "output_buf_size" in rout:
          if len(rout["output_buf_size"].strip()) > 0:
            f.write("  OUTPUT_BUFFER_SIZE=%s\n" % (rout['output_buf_size']))

        if "rxn_step" in rout:
          if len(rout["rxn_step"]) > 0:
            f.write("  STEP=%s\n" % (rout['rxn_step']))
          else:
            f.write("  STEP=%s\n" % time_step)
        else:
          f.write("  STEP=%s\n" % time_step)

        always_generate = False
        if "always_generate" in rout:
          always_generate = rout["always_generate"]
        if "reaction_output_list" in rout:
          count_name = ""
          for rxn_output in rout["reaction_output_list"]:
            plotting_enabled = True
            if "plotting_enabled" in rxn_output:
              plotting_enabled = rxn_output["plotting_enabled"]
            if always_generate or plotting_enabled:
              if "rxn_or_mol" in rxn_output:
                rxn_or_mol = rxn_output["rxn_or_mol"]
                if rxn_or_mol == 'Reaction':
                    count_name = rxn_output["reaction_name"]
                elif rxn_or_mol == 'Molecule':
                    count_name = rxn_output["molecule_name"]
                elif rxn_or_mol == 'MDLString':
                    outputStr = rxn_output["mdl_string"]
                    output_file = rxn_output["mdl_file_prefix"]
                    if outputStr not in ['', None]:
                        outputStr = '  {%s} =>  "./react_data/seed_" & seed & \"/%s_MDLString.dat\"\n' % (outputStr, output_file)
                        f.write(outputStr)
                    else:
                        print('Found invalid reaction output {0}'.format(rxn_output["name"]))
                    continue  ####   <=====-----  C O N T I N U E     H E R E  !!!!!
                elif rxn_or_mol == 'File':
                    # No MDL is generated for plot items that are plain files
                    continue  ####   <=====-----  C O N T I N U E     H E R E  !!!!!

                object_name = rxn_output["object_name"]
                region_name = rxn_output["region_name"]
                if rxn_output["count_location"] == 'World':
                    f.write(
                        "  {COUNT[%s,WORLD]}=> \"./react_data/seed_\" & seed & "
                        "\"/%s.World.dat\"\n" % (count_name, count_name,))
                elif rxn_output["count_location"] == 'Object':
                    f.write(
                        "  {COUNT[%s,%s.%s]}=> \"./react_data/seed_\" & seed & "
                        "\"/%s.%s.dat\"\n" % (count_name, context_scene_name,
                                              object_name, count_name, object_name))
                elif rxn_output["count_location"] == 'Region':
                    f.write(
                        "  {COUNT[%s,%s.%s[%s]]}=> \"./react_data/seed_\" & seed & "
                        "\"/%s.%s.%s.dat\"\n" % (count_name, context_scene_name,
                        object_name, region_name, count_name, object_name, region_name))


        f.write ( "}\n" )
        f.write ( "\n" );


##### NOTE that this function shadows the earlier version ... which is best??
data_model_depth = 0
def dump_data_model ( dm ):
    global data_model_depth
    data_model_depth += 1
    if type(dm) == type({'a':1}): # dm is a dictionary
        for k,v in sorted(dm.items()):
            print ( str(data_model_depth*"  ") + "Key = " + str(k) )
            dump_data_model ( v )
    elif type(dm) == type(['a',1]): # dm is a list
        i = 0
        for v in dm:
            print ( str(data_model_depth*"  ") + "Entry["+str(i)+"]" )
            dump_data_model ( v )
            i += 1
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')): # dm is a string
        print ( str(data_model_depth*"  ") + "\"" + str(dm) + "\"" )
    else: # dm is anything else
        print ( str(data_model_depth*"  ") + str(dm) )
    data_model_depth += -1



if __name__ == "__main__":

    if len(sys.argv) > 2:
        print ( "Got parameters: " + sys.argv[1] + " " + sys.argv[2] )
        print ( "Reading Data Model: " + sys.argv[1] )
        dm = read_data_model ( sys.argv[1] )
        # dump_data_model ( dm )
        print ( "Writing MDL: " + sys.argv[2] )
        write_mdl ( dm, sys.argv[2] )
        print ( "Wrote Data Model found in \"" + sys.argv[1] + "\" to MDL file \"" + sys.argv[2] + "\"" )
        # Drop into an interactive python session
        #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

    else:
        # Print the help information
        print ( "\nhelp():" )
        print ( "\n=======================================" )
        print ( "Requires 2 parameters:" )
        print ( "   data_model_file_name - A Data Model (pickled format)" )
        print ( "   mdl_base_name - The base name to use for the project" )
        # print ( "Use Control-D to exit the interactive mode" )
        print ( "=======================================\n" )

