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


dm_indent_by = 2
dm_text_depth = 0
def text_data_model ( name, dm, dm_list, comma ):
    """Generate a list of the data model elements with indenting"""
    global dm_text_depth
    indent = dm_indent_by*" "
    dict_type = type({'a':1})
    list_type = type(['a',1])
    if type(dm) == dict_type:  #dm is a dictionary
        num_items = len(dm.keys())
        if num_items == 0:
            dm_list.append ( str(dm_text_depth*indent) + name + "{}" + comma )
        else:
            dm_list.append ( str(dm_text_depth*indent) + name + "{" )
            dm_text_depth += 1
            item_num = 0
            for k,v in sorted(dm.items()):
                if not k.startswith("_"):
                    subcomma = ','
                    if item_num > num_items-2:
                      subcomma = ''
                    text_data_model ( "\'"+k+"\'"+" : ", v, dm_list, subcomma )
                    item_num += 1
            dm_text_depth += -1
            dm_list.append ( str(dm_text_depth*indent) + "}" + comma )
    elif type(dm) == list_type:  #dm is a list
        num_items = len(dm)
        if num_items == 0:
            dm_list.append ( str(dm_text_depth*indent) + name + "[]" + comma )
        else:
            one_liner = True
            if num_items > 4:
                one_liner = False
            for v in dm:
                if type(v) in [dict_type, list_type]:
                  one_liner = False
                  break
            if one_liner:
                dm_list.append ( str(dm_text_depth*indent) + name + str(dm) + comma )
            else:
                dm_list.append ( str(dm_text_depth*indent) + name + "[" )
                dm_text_depth += 1
                i = 0
                for v in dm:
                    k = name + "["+str(i)+"]"
                    subcomma = ','
                    if i > num_items-2:
                      subcomma = ''
                    text_data_model ( "", v, dm_list, subcomma )
                    i += 1
                dm_text_depth += -1
                dm_list.append ( str(dm_text_depth*indent) + "]" + comma )
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')):  #dm is a string
        dm_list.append ( str(dm_text_depth*indent) + name + "\"" + str(dm) + "\"" + comma )
    else:
        dm_list.append ( str(dm_text_depth*indent) + name + str(dm) + comma )
    return dm_list


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
    return True
  return False

# Import math to be available for user scripts
import math

# For debugging
import traceback


def write_export_scripting ( dm, before_after, section, mdl_file ):
    if 'mcell' in dm:
        mcell_dm = dm['mcell']
        if 'scripting' in mcell_dm:
            scripting = mcell_dm['scripting']
            print ( "################### Write Scripting Ouptut " + before_after + " " + section )
            # mdl_file.write("\n\n/* Begin Custom MDL Inserted %s %s */\n" % (before_after, section))
            for script in scripting['scripting_list']:
                if (script['include_where'] == before_after) and (script['include_section'] == section):

                    if script['internal_external'] == 'internal':
                        mdl_file.write ( "\n/*** Beginning of internal script \"%s\" included %s %s ***/\n\n" % (script['internal_file_name'], before_after, section))
                    else:
                        mdl_file.write ( "\n/*** Beginning of external script \"%s\" included %s %s ***/\n\n" % (script['external_file_name'], before_after, section))

                    if script['mdl_python'] == 'mdl':
                        if script['internal_external'] == 'internal':
                            mdl_file.write ( scripting['script_texts'][script['internal_file_name']] )
                        else:
                            print ( "Loading external MDL script: " + script['external_file_name'] )
                            f = None
                            if script['external_file_name'].startswith ( "//" ):
                                # Convert the file name from blend file relative (//) to full path:
                                if has_blender:
                                    f = open ( os.path.join ( os.path.dirname(bpy.data.filepath), script['external_file_name'][2:] ), mode='r' )
                                else:
                                    # Not sure what to do without Blender in this case ... assume it's local for now
                                    f = open ( script['external_file_name'][2:], mode='r' )
                            else:
                                f = open ( script['external_file_name'], mode='r' )
                            script_text = f.read()
                            mdl_file.write ( script_text )

                    if script['mdl_python'] == 'python':
                        if script['internal_external'] == 'internal':
                            data_model = dm
                            mdl_file.write ( "\n  /* Before executing internal Python script \"%s\" %s %s */\n\n" % (script['internal_file_name'], before_after, section))
                            exec ( scripting['script_texts'][script['internal_file_name']], globals(), locals() )
                            mdl_file.write ( "\n  /* After executing internal Python script \"%s\" %s %s */\n\n" % (script['internal_file_name'], before_after, section))
                        else:
                            print ( "Loading external Python script: " + script['external_file_name'] )
                            f = None
                            if script['internal_file_name'].startswith ( "//" ):
                                if has_blender:
                                    # Convert the file name from blend file relative (//) to full path:
                                    f = open ( os.path.join ( os.path.dirname(bpy.data.filepath), script['external_file_name'][2:] ), mode='r' )
                                else:
                                    # Not sure what to do without Blender in this case ... assume it's local for now
                                    f = open ( script['external_file_name'][2:], mode='r' )
                            else:
                                f = open ( script['external_file_name'], mode='r' )
                            script_text = f.read()
                            mdl_file.write ( "\n  /* Before executing external Python script \"%s\" %s %s */\n\n" % (script['external_file_name'], before_after, section))
                            exec ( script_text, globals(), locals() )
                            mdl_file.write ( "\n  /* After executing external Python script \"%s\" %s %s */\n\n" % (script['external_file_name'], before_after, section))

                    if script['internal_external'] == 'internal':
                        mdl_file.write ( "\n/*** End of internal script \"%s\" included %s %s ***/\n\n" % (script['internal_file_name'], before_after, section))
                    else:
                        mdl_file.write ( "\n/*** End of external script \"%s\" included %s %s ***/\n\n" % (script['external_file_name'], before_after, section))
            # mdl_file.write("\n\n/* End Custom MDL Inserted %s %s */\n\n" % (before_after, section))



#####################################################################################################################
############################################  M  D  L  R    Code  ###################################################
#####################################################################################################################

try:

    import subprocess
    import sys
    import shutil
    import cellblender

    project_files_dir = ""
    start_seed = 1
    end_seed = 1


    def postprocess():
      global parameter_dictionary
      print ( "Postprocessing MCellR Reaction Output..." )

      mcellr_react_dir = os.path.join(project_files_dir, "output_data")

      react_dir = os.path.join(mcellr_react_dir, "react_data")

      if os.path.exists(react_dir):
          shutil.rmtree(react_dir,ignore_errors=True)
      if not os.path.exists(react_dir):
          os.makedirs(react_dir)

      for run_seed in range(start_seed, end_seed+1):
        print ( "  Postprocessing for seed " + str(run_seed) )

        seed_dir = "seed_%05d" % run_seed

        react_seed_dir = os.path.join(react_dir, seed_dir)

        if os.path.exists(react_seed_dir):
            shutil.rmtree(react_seed_dir,ignore_errors=True)
        if not os.path.exists(react_seed_dir):
            os.makedirs(react_seed_dir)


        # Read the MCellR data file and split into a list of rows where each row is a list of columns
        mcellr_react_file = open ( os.path.join ( mcellr_react_dir, 'Scene.mdlr_total.xml.gdat' ) )
        all_react_data = mcellr_react_file.read()
        react_data_all = [ [t.strip() for t in s.split(',') if len(t.strip()) > 0] for s in all_react_data.split('\n') if len(s) > 0 ]
        react_data_header = react_data_all[0]
        react_data_rows = react_data_all[1:]

        for col in range(1,len(react_data_header)):
          out_file_name = os.path.join ( react_seed_dir, react_data_header[col] + ".dat" )
          print ( "    Writing data to " + out_file_name )
          f = open(out_file_name,"w")
          for row in react_data_rows:
    #        print ( "  " + row[0] + " " + row[col] )
            f.write ( row[0] + " " + row[col] + '\n' )
          f.close()

      print ( "Done Postprocessing MCellR Reaction Output" )

    def makedirs_exist_ok ( path_to_build, exist_ok=False ):
        # Needed for old python which doesn't have the exist_ok option!!!
        parts = path_to_build.split(os.sep)  # Variable "parts" should be a list of subpath sections. The first will be empty ('') if it was absolute.
        full = ""
        if len(parts[0]) == 0:
          full = os.sep
        for p in parts:
          full = os.path.join(full,p)
          print ( "   " + full )
          if not os.path.exists(full):
            os.makedirs ( full, exist_ok=True )

    def write_geometry_mdlr3 ( geom, f ):
        if 'object_list' in geom:
          glist = geom['object_list']
          if len(glist) > 0:
            for g in glist:
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

    def write_viz_out_mdlr3 ( vizout, mols, f ):

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
          f.write ( "  FILENAME = \"./viz_data/seed_\" & seed & \"/Scene\"\n" )
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

    def write_mdlr ( dm, file_name, scene_name='Scene' ):
        # The file_name parameter will be something like:
        #   <project>_files/mcell/output_data/Scene.main.mdl"
        #   <project>_files/mcell/output_data/Par_x_index_n/Scene.main.mdl
        #   <project>_files/mcell/output_data/Par_x_index_n/Par_y_index_n/Scene.main.mdl
        print ( "write_mdlr called with file_name = \"" + str(file_name) + "\"" )
        output_detail = 20
        data_model = dm['mcell']
        print ( "DM: " + str(data_model.keys()) )
        # This function does essentially what the sim_engines/mcell3r/__init__.py file did
        # This function does not add any of the other functionality of write_mdl which called it
        # This function should eventually be removed if the writing of MDLR can be integrated with write_mdl
        project_dir = os.path.dirname(file_name)
        print ( "project_dir = " + str(project_dir) )

        final_shared_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"extensions")
        cb_path = "" + final_shared_path
        print ( "final_shared_path = " + str(final_shared_path) )

        final_bionetgen_path = os.path.join(final_shared_path,"bng2","BNG2.pl")
        print ( "final_bionetgen_path = " + str(final_bionetgen_path) )

        final_lib_path = os.path.join(final_shared_path,"lib") + os.path.sep
        print ( "final_lib_path = " + str(final_lib_path) )

        final_mcell_path = os.path.join(final_shared_path,"mcell")
        print ( "final_mcell_path = " + str(final_mcell_path) )

        output_data_dir = project_dir
        makedirs_exist_ok ( output_data_dir, exist_ok=True )

        react_data_dir = os.path.join(output_data_dir, "react_data")
        if os.path.exists(react_data_dir):
            shutil.rmtree(react_data_dir,ignore_errors=True)
        if not os.path.exists(react_data_dir):
            os.makedirs(react_data_dir)

        viz_data_dir = os.path.join(output_data_dir, "viz_data")
        if os.path.exists(viz_data_dir):
            shutil.rmtree(viz_data_dir,ignore_errors=True)
        if not os.path.exists(viz_data_dir):
            os.makedirs(viz_data_dir)

        time_step = '1e-6'  # This is needed as a default for plotting

        f = open ( os.path.join(output_data_dir,"Scene.mdlr"), 'w' )

        if 'parameter_system' in data_model:
          # Write the parameter system
          write_parameter_system ( data_model['parameter_system'], f )

        if 'initialization' in data_model:
          # Can't write all initialization MDL because booleans like "TRUE" are referenced but not defined in BNGL
          # write_initialization(data_model['initialization'], f)
          # Write specific parts instead:
          write_dm_str_val ( data_model['initialization'], f, 'iterations',                'ITERATIONS' )
          write_dm_str_val ( data_model['initialization'], f, 'time_step',                 'TIME_STEP' )
          write_dm_str_val ( data_model['initialization'], f, 'vacancy_search_distance',   'VACANCY_SEARCH_DISTANCE', blank_default='10' )

          time_step = data_model['initialization']['time_step']

        f.write ( 'INCLUDE_FILE = "Scene.geometry.mdl"\n' )


        # Note that reflective surface classes may need to be added as defaults for MCell-R to run
        # If so, it might be good to automate this rather than explicitly requiring it in CellBlender's model.

        if 'define_surface_classes' in data_model:
          write_surface_classes(data_model['define_surface_classes'], f)

        if 'modify_surface_regions' in data_model:
          write_modify_surf_regions ( data_model['modify_surface_regions'], f )

        if 'define_molecules' in data_model:
          mols = data_model['define_molecules']
          if 'molecule_list' in mols:
            mlist = mols['molecule_list']
            if len(mlist) > 0:
              f.write ( "#DEFINE_MOLECULES\n" )
              f.write ( "{\n" )
              for m in mlist:
                f.write ( "  %s" % m['mol_name'] )
                if "bngl_component_list" in m:
                  f.write( "(" )
                  num_components = len(m['bngl_component_list'])
                  if num_components > 0:
                    for ci in range(num_components):
                      c = m['bngl_component_list'][ci]
                      f.write( c['cname'] )
                      for state in c['cstates']:
                        f.write ( "~" + state )
                      if ci < num_components-1:
                        f.write ( "," )
                  f.write( ")" )
                f.write ( "\n" )
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

        if 'define_reactions' in data_model:
          reacts = data_model['define_reactions']
          if 'reaction_list' in reacts:
            rlist = reacts['reaction_list']
            if len(rlist) > 0:
              f.write ( "#DEFINE_REACTIONS\n" )
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
                  f.write ( "[%s, %s]" % ( r['fwd_rate'], r['bkwd_rate'] ) )
                if 'rxn_name' in r:
                  if len(r['rxn_name']) > 0:
                    f.write ( " : %s" % (r['rxn_name']) )
                f.write("\n")
              f.write ( "}\n" )
              f.write("\n")

        if ('model_objects' in data_model) or ('release_sites' in data_model):
          geom = None
          rels = None
          if 'model_objects' in data_model:
            geom = data_model['model_objects']
          if 'release_sites' in data_model:
            rels = data_model['release_sites']
          mols = data_model['define_molecules']
          #TODO Note that the use of "Scene" here is a temporary measure!!!!
          f.write ( "#INSTANTIATE Scene OBJECT\n" )
          f.write ( "{\n" )
          if geom != None:
            if 'model_object_list' in geom:
              glist = geom['model_object_list']
              if len(glist) > 0:
                # Sort the objects by parent
                unsorted_objs = [ g for g in glist ]
                sorted_objs = []
                sorted_obj_names = []
                while len(unsorted_objs) > 0:
                  for index in range(len(unsorted_objs)):
                    if output_detail > 10: print ( "  Sorting by parent: checking " + unsorted_objs[index]['name'] + " for parent " + unsorted_objs[index]['parent_object'] )
                    if len(unsorted_objs[index]['parent_object']) == 0:
                      # Move this object to the sorted list because it has no parent
                      sorted_obj_names.append ( unsorted_objs[index]['name'])
                      sorted_objs.append ( unsorted_objs.pop(index) )
                      break
                    elif unsorted_objs[index]['parent_object'] in sorted_obj_names:
                      # Move this object to the sorted list because its parent is already in the list
                      sorted_obj_names.append ( unsorted_objs[index]['name'])
                      sorted_objs.append ( unsorted_objs.pop(index) )
                      break

                for g in sorted_objs:
                  f.write ( "  %s OBJECT %s {\n" % (g['name'], g['name']) )
                  if len(g['parent_object']) > 0:
                    f.write ( "    PARENT = %s\n" % (g['parent_object']) )
                  if len(g['membrane_name']) > 0:
                    # f.write ( "    MEMBRANE = %s\n" % (g['membrane_name']) )
                    f.write ( "    MEMBRANE = %s OBJECT %s[ALL]\n" % (g['membrane_name'], g['name']) )
                  f.write ( "  }\n" )
          if rels != None:
            if 'release_site_list' in rels:
              rlist = rels['release_site_list']
              if len(rlist) > 0:
                for r in rlist:
                  f.write ( "  %s RELEASE_SITE\n" % (r['name']) )
                  f.write ( "  {\n" )

                  # First handle the release shape
                  if ((r['shape'] == 'CUBIC') |
                      (r['shape'] == 'SPHERICAL') |
                      (r['shape'] == 'SPHERICAL_SHELL')):
                    # Output MDL for releasing in a non-object shape pattern
                    f.write("   SHAPE = %s\n" % (r['shape']))
                    f.write("   LOCATION = [%s, %s, %s]\n" % (r['location_x'],r['location_y'],r['location_z']))
                    f.write("   SITE_DIAMETER = %s\n" % (r['site_diameter']))
                  elif r['shape'] == "OBJECT":
                    # Output MDL for releasing in or on and object
                    #TODO Note that the use of "Scene." here for object names is a temporary measure!!!!
                    obj_expr = r['object_expr']
                    obj_expr = '-'.join(["Scene."+t.strip() for t in obj_expr.split('-')])
                    # Can't repeat this because the "Scene's" accumulate
                    #obj_expr = '+'.join(["Scene."+t.strip() for t in obj_expr.split('+')])
                    #obj_expr = '*'.join(["Scene."+t.strip() for t in obj_expr.split('*')])
                    f.write("   SHAPE = %s\n" % (obj_expr))

                  # Next handle the molecule to be released (maybe the Molecule List should have been a dictionary keyed on mol_name?)
                  mlist = mols['molecule_list']
                  mol = None
                  for m in mlist:
                    if m['mol_name'] == r['molecule']:
                      mol = m
                      break
                  f.write("   MOLECULE = %s\n" % (r['molecule']))

                  # Now write out the quantity, probability, and pattern

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
                  f.write("   RELEASE_PROBABILITY = %s\n" % (r['release_probability']))
                  if len(r['pattern']) > 0:
                    f.write("   RELEASE_PATTERN = %s\n" % (r['pattern']))

                  f.write ( "  }\n" )
          f.write ( "}\n" )
          f.write("\n")


        if 'reaction_data_output' in data_model:
          plot_out = data_model['reaction_data_output']
          rxn_step = time_step  # Default if not otherwise specified in the reaction data output block
          if 'rxn_step' in plot_out:
            if len(plot_out['rxn_step']) > 0:
              rxn_step = plot_out['rxn_step']
          if 'reaction_output_list' in plot_out:
            plist = plot_out['reaction_output_list']
            if len(plist) > 0:
              f.write ( "#REACTION_DATA_OUTPUT\n" )
              f.write ( "{\n" )
              f.write ( "  STEP = %s\n" % rxn_step )
              for p in plist:
                if 'rxn_or_mol' in p:
                  if p['rxn_or_mol'] == 'MDLString':
                    # Trouble with first two approaches:
                    # f.write ( "  { %s } => \"./react_data/seed_\" & seed & \"/%s_MDLString.dat\"\n" % (p['mdl_string'], p['mdl_file_prefix']) )
                    # f.write ( "  { %s } => \"./react_data/seed_00001/%s_MDLString.dat\"\n" % (p['mdl_string'], p['mdl_file_prefix']) )
                    f.write ( "  { %s } => \"./react_data/%s_MDLString.dat\"\n" % (p['mdl_string'], p['mdl_file_prefix']) )
              f.write ( "}\n" )
              f.write("\n")

        f.write("\n")
        f.write ( "INCLUDE_FILE = \"Scene.viz_output.mdl\"\n\n" )

        f.close()

        f = open ( os.path.join(output_data_dir,"Scene.geometry.mdl"), 'w' )
        write_geometry_mdlr3 (data_model['geometrical_objects'], f)
        f.close()

        f = open ( os.path.join(output_data_dir,"Scene.viz_output.mdl"), 'w' )
        f.write ( 'sprintf(seed,"%05g",SEED)\n\n' )
        write_viz_out_mdlr3(data_model['viz_output'], data_model['define_molecules'], f)
        f.close()

        fseed = data_model['simulation_control']['start_seed']
        lseed = data_model['simulation_control']['end_seed']

        global start_seed
        global end_seed
        start_seed = int(fseed)
        end_seed = int(lseed)

        # execute mdlr2mdl.py to generate MDL from MDLR
        mdlr_cmd = os.path.join ( cb_path, 'mdlr2mdl.py' )
        mdlr_args = [ cellblender.python_path, mdlr_cmd, '-ni', 'Scene.mdlr', '-o', 'Scene' ]
        wd = output_data_dir
        p = subprocess.Popen(mdlr_args, cwd = wd)

        # For now return no commands at all since the run has already taken place
        command_list = []

        command_dict = { 'cmd': cellblender.python_path,
                         'args': [ os.path.join(cb_path, "mcell3r.py"), '-s', fseed, '-r', 'Scene.mdlr_rules.xml', '-m', 'Scene.main.mdl' ],
                         'wd': output_data_dir
                       }

        command_line_options = ''

        if len(command_line_options) > 0:
          command_dict['args'].append(command_line_options)

        command_list.append ( command_dict )
        if output_detail > 0:
          print ( str(command_dict) )

        # Postprocessing should be done through the command_list, but force it here for now...

        # postprocess()

        return ( command_list )

except:
    # Unable to import Blender classses
    print ( "Unable to import cellblender ... running outside normal environment." )
    pass



def requires_mcellr ( dm ):
    # Determine if this is a BioNetGen model
    bionetgen_mode = False
    if ('mcell' in dm):
      mcell = dm['mcell']
      if 'define_molecules' in mcell:
        mols = mcell['define_molecules']
        if 'molecule_list' in mols:
          mlist = mols['molecule_list']
          if len(mlist) > 0:
            for m in mlist:
              if 'bngl_component_list' in m:
                if len(m['bngl_component_list']) > 0:
                  bionetgen_mode = True
                  break
    return bionetgen_mode


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################


def write_mdl ( dm, file_name, scene_name='Scene' ):
    """ Write a data model to a named file (generally follows "export_mcell_mdl" ordering) """

    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
    print ( "Top of data_model_to_mdl.write_mdl() to " + str(file_name) )
    print ( "Data Model Keys: " + str( [k for k in dm['mcell'].keys()] ) )
    if 'parameter_system' in dm['mcell'].keys():
        pars = dm['mcell']['parameter_system']['model_parameters']
        for p in pars:
            if p['par_name'] == 'n0':
                n0 = p['_extras']['par_value']
            print ( "Parameter " + p['par_name'] + " = " + str(p['par_expression']) )
    export_cellblender_data = not dm['mcell']['scripting']['ignore_cellblender_data']
    if not export_cellblender_data:
      print ( "Exporting only the scripts ... ignoring all other CellBlender data" )
    export_modular = ( dm['mcell']['simulation_control']['export_format'] == 'mcell_mdl_modular' )
    print ( "Export Modular = " + str(export_modular) )
    modular_path = None
    if export_modular:
      # Set the modular path
      modular_path = os.path.dirname(file_name)
    #print ( "Call Stack:" )
    #traceback.print_stack()
    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


    # Determine if this is a BioNetGen model
    bionetgen_mode = requires_mcellr ( dm )

    if bionetgen_mode:
      print ( 100 * "#" )
      print ( "  BioNetGen Mode!!!" )
      write_mdlr ( dm, file_name, scene_name )
      print ( 100 * "#" )
      return

    # Begin actually exporting

    # First check for any dynamic objects in the data model
    num_dynamic = len ( [ True for o in dm['mcell']['model_objects']['model_object_list'] if o['dynamic'] ] )

    f = open ( file_name, 'w' )
    if not export_cellblender_data:
      f.write ( "/* MDL from scripts alone - all CellBlender data ignored!! */" )

    actually_wrote = False
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


      write_export_scripting ( dm, 'before', 'everything', f )

      write_export_scripting ( dm, 'before', 'parameters', f )

      if export_cellblender_data and ('parameter_system' in mcell):
        ps = mcell['parameter_system']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name+'.parameters.mdl'), 'w' )
        actually_wrote = write_parameter_system ( ps, out_file )
        print ( "actually_wrote parameters = " + str(actually_wrote) )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.parameters.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'parameters', f )
      write_export_scripting ( dm, 'before', 'initialization', f )

      if export_cellblender_data and ('initialization' in mcell):
        init = mcell['initialization']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.initialization.mdl'), 'w' )
        actually_wrote = write_initialization ( init, out_file )
        print ( "actually_wrote initialization = " + str(actually_wrote) )
        if 'partitions' in init:
          parts = mcell['initialization']['partitions']
          write_partitions ( parts, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.initialization.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'initialization', f )
      write_export_scripting ( dm, 'before', 'molecules', f )

      if export_cellblender_data and ('define_molecules' in mcell):
        mols = mcell['define_molecules']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.molecules.mdl'), 'w' )
        actually_wrote = write_molecules ( mols, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.molecules.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'molecules', f )
      write_export_scripting ( dm, 'before', 'surface_classes', f )

      if export_cellblender_data and ('define_surface_classes' in mcell):
        sclasses = mcell['define_surface_classes']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.surface_classes.mdl'), 'w' )
        actually_wrote = write_surface_classes ( sclasses, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.surface_classes.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'surface_classes', f )
      write_export_scripting ( dm, 'before', 'reactions', f )

      if export_cellblender_data and ('define_reactions' in mcell):
        reacts = mcell['define_reactions']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.reactions.mdl'), 'w' )
        actually_wrote = write_reactions ( reacts, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.reactions.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'reactions', f )
      write_export_scripting ( dm, 'before', 'geometry', f )

      if export_cellblender_data:
        if num_dynamic == 0:
          # MCell currently requires all objects to be either static or dynamic
          # So only write static objects if there are NO dynamic objects
          if ('model_objects' in mcell) and ('geometrical_objects' in mcell):
            objs = mcell['model_objects']
            geom = mcell['geometrical_objects']
            scripting = None
            if 'scripting' in mcell:
                scripting = mcell['scripting']
            out_file = f
            if not (modular_path is None):
              out_file = open ( os.path.join(modular_path,scene_name + '.geometry.mdl'), 'w' )
            actually_wrote = write_static_geometry ( objs, geom, dm, out_file )
            if not (out_file == f):
              out_file.close()
              if actually_wrote:
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

      write_export_scripting ( dm, 'after', 'geometry', f )
      write_export_scripting ( dm, 'before', 'mod_surf_regions', f )

      if export_cellblender_data and ('modify_surface_regions' in mcell):
        modsurfrs = mcell['modify_surface_regions']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.mod_surf_regions.mdl'), 'w' )
        actually_wrote = write_modify_surf_regions ( modsurfrs, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.mod_surf_regions.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'mod_surf_regions', f )
      write_export_scripting ( dm, 'before', 'release_patterns', f )

      if export_cellblender_data and ('define_release_patterns' in mcell):
        pats = mcell['define_release_patterns']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.release_patterns.mdl'), 'w' )
        actually_wrote = write_release_patterns ( pats, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.release_patterns.mdl"\n\n' )


      write_export_scripting ( dm, 'after', 'release_patterns', f )
      write_export_scripting ( dm, 'before', 'instantiate', f )

      # Figure out what we have to output based on:
      #   Static Geometry
      #   Dynamic Geometry
      #   Release Sites
      has_static_geometry = False
      has_dynamic_geometry = False
      has_release_sites = False
      if export_cellblender_data and ('model_objects' in mcell):
        if 'model_object_list' in mcell['model_objects']:
          if len(mcell['model_objects']['model_object_list']) > 0:
            num_static = len(dm['mcell']['model_objects']['model_object_list']) - num_dynamic
            if num_static > 0:
              has_static_geometry = True
            if num_dynamic > 0:
              has_dynamic_geometry = True

      if export_cellblender_data and ('release_sites' in mcell):
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

        if export_cellblender_data:
          out_file.write ( "INSTANTIATE " + block_name + " OBJECT\n" )
          out_file.write ( "{\n" )
          if has_static_geometry:
            objs = None
            geom = None
            if 'model_objects' in mcell:
              objs = mcell['model_objects']
            if 'geometrical_objects' in mcell:
              geom = mcell['geometrical_objects']
            actually_wrote = write_static_instances ( scene_name, objs, geom, out_file )

        write_export_scripting ( dm, 'before', 'release_sites', f )

        if export_cellblender_data:
          if has_release_sites:
            rels = mcell['release_sites']
            wrote_rels = write_release_sites ( scene_name, rels, mcell['define_molecules'], out_file )
            actually_wrote = actually_wrote or wrote_rels

        write_export_scripting ( dm, 'after', 'release_sites', f )

        if export_cellblender_data:
          out_file.write ( "}\n\n" )

        if export_cellblender_data:
          if not (out_file == f):
            out_file.close()
            if actually_wrote:
              f.write ( 'INCLUDE_FILE = "' + scene_name + '.instantiation.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'instantiate', f )
      write_export_scripting ( dm, 'before', 'seed', f )

      if export_cellblender_data:
        f.write("sprintf(seed,\"%05g\",SEED)\n\n")

      write_export_scripting ( dm, 'after', 'seed', f )
      write_export_scripting ( dm, 'before', 'viz_output', f )

      if export_cellblender_data and ('viz_output' in mcell):
        vizout = mcell['viz_output']
        mols = None
        if ('define_molecules' in mcell):
          mols = mcell['define_molecules']
        out_file = f
        if not (modular_path is None):
          out_file = open ( os.path.join(modular_path,scene_name + '.viz_output.mdl'), 'w' )
        actually_wrote = write_viz_out ( scene_name, vizout, mols, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.viz_output.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'viz_output', f )
      write_export_scripting ( dm, 'before', 'rxn_output', f )

      if export_cellblender_data and ('reaction_data_output' in mcell):
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
        actually_wrote = write_react_out ( scene_name, reactout, mols, time_step, out_file )
        if not (out_file == f):
          out_file.close()
          if actually_wrote:
            f.write ( 'INCLUDE_FILE = "' + scene_name + '.rxn_output.mdl"\n\n' )

      write_export_scripting ( dm, 'after', 'rxn_output', f )

      write_export_scripting ( dm, 'after', 'everything', f )

    f.close()

    # Check for any dynamic objects, and update MDL as needed

    num_dynamic = len ( [ True for o in dm['mcell']['model_objects']['model_object_list'] if o['dynamic'] ] )
    if export_cellblender_data and (num_dynamic > 0):

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
            #     dynamic
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
                    #frame_number             # The name "frame_number" may be expected by the user's script if it can also generate dynamic geometry
                    dynamic = obj['dynamic']  # The script may need to know this to ignore or use the frame number
                    points = []               # The list "points" is expected by the user's script
                    faces = []                # The list "faces" is expected by the user's script
                    regions_dict = {}         # The dict "regions_dict" is expected by the user's script
                    region_props = {}         # The dict "region_props" is expected by the user's script
                    origin = [0,0,0]          # The list "origin" is expected by the user's script

                    # print ( "data_model['mcell'].keys() = " + str(data_model['mcell'].keys()) )

                    if len(obj['script_name']) > 0:
                        # Let the script create the geometry
                        #print ( "   Build object mesh from user script for frame " + str(frame_number) )
                        #script_text = script_dict[obj['script_name']]
                        script_text = mcell['scripting']['script_texts'][obj['script_name']]
                        #print ( 80*"=" )
                        #print ( script_text )
                        #print ( 80*"=" )
                        # exec ( script_dict[obj.script_name], locals() )
                        #print ( "Before script: region_props = " + str(region_props) )
                        data_model = dm        # Use a more "official" name for the data model to be used by dynamic geometry scripts
                        #exec ( script_dict[obj['script_name']], globals(), locals() )
                        #exec ( script_dict[obj['script_name']] )
                        exec ( script_text, globals(), locals() )
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
    wrote_mdl = False
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
          wrote_mdl = True
        f.write ( "\n" );
    return wrote_mdl


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
    return True

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
    return True

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
    return True


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
        return True
    return False


def write_molecules ( mols, f ):
    wrote_mdl = False
    if 'molecule_list' in mols:
      mlist = mols['molecule_list']
      if len(mlist) > 0:
        wrote_mdl = True
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
    return wrote_mdl


def write_surface_classes ( sclasses, f ):
    wrote_mdl = False
    if 'surface_class_list' in sclasses:
      sclist = sclasses['surface_class_list']
      if len(sclist) > 0:
        wrote_mdl = True
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
    return wrote_mdl


def write_reactions ( reacts, f ):
    wrote_mdl = False
    if 'reaction_list' in reacts:
      rlist = reacts['reaction_list']
      if len(rlist) > 0:
        wrote_mdl = True
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
    return wrote_mdl


def write_static_geometry ( objs, geom, dm, f ):
    wrote_mdl = False
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
            wrote_mdl = True
            if obj['object_source'] == 'script':
              # Generate this object's MDL from a script

              # print ( "  Saving static geometry for object " + obj['name'] + " with script \"" + obj['script_name'] + "\"" )

              frame_number = -1         # The name "frame_number" may be expected by the user's script if it can also generate dynamic geometry
              dynamic = obj['dynamic']  # The script may need to know this to ignore or use the frame number
              points = []               # The list "points" is expected by the user's script
              faces = []                # The list "faces" is expected by the user's script
              regions_dict = {}         # The dict "regions_dict" is expected by the user's script
              region_props = {}         # The dict "region_props" is expected by the user's script
              origin = [0,0,0]          # The list "origin" is expected by the user's script

              # print ( "data_model['mcell'].keys() = " + str(data_model['mcell'].keys()) )

              if len(obj['script_name']) > 0:
                  # Let the script create the geometry
                  #print ( "   Build object mesh from user script for frame " + str(frame_number) )
                  #script_text = script_dict[obj['script_name']]
                  script_text = dm['mcell']['scripting']['script_texts'][obj['script_name']]
                  #print ( 80*"=" )
                  #print ( script_text )
                  #print ( 80*"=" )
                  # exec ( script_dict[obj.script_name], locals() )
                  #print ( "Before script: region_props = " + str(region_props) )
                  data_model = dm        # Use a more "official" name for the data model to be used by dynamic geometry scripts
                  #exec ( script_dict[obj['script_name']], globals(), locals() )
                  #exec ( script_dict[obj['script_name']] )
                  exec ( script_text, globals(), locals() )
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

              # Generate this object's MDL from the collected data
              loc_x = 0.0
              loc_y = 0.0
              loc_z = 0.0
              f.write ( "%s POLYGON_LIST\n" % obj['name'] )
              f.write ( "{\n" )
              if len(points) > 0:
                f.write ( "  VERTEX_LIST\n" )
                f.write ( "  {\n" )
                for v in points:
                  f.write ( "    [ %.15g, %.15g, %.15g ]\n" % ( loc_x+v[0], loc_y+v[1], loc_z+v[2] ) )
                f.write ( "  }\n" )
              if len(faces) > 0:
                f.write ( "  ELEMENT_CONNECTIONS\n" )
                f.write ( "  {\n" )
                for c in faces:
                  f.write ( "    [ %d, %d, %d ]\n" % ( c[0], c[1], c[2] ) )
                f.write ( "  }\n" )
              if len(regions_dict) > 0:
                rkeys = sorted ( regions_dict.keys() )
                f.write ( "  DEFINE_SURFACE_REGIONS\n" )
                f.write ( "  {\n" )
                for rk in rkeys:
                  r = regions_dict[rk]
                  f.write ( "    %s\n" % r['name'] )
                  f.write ( "    {\n" )
                  if 'include_elements' in r:
                    int_regs = [ int(r) for r in r['include_elements'] ]
                    f.write ( "      ELEMENT_LIST = " + str(int_regs) + "\n" )
                  f.write ( "    }\n" )
                f.write ( "  }\n" )
              f.write ( "}\n")
              f.write ( "\n" );

            else:

              # Generate this object's MDL from the geometry data
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
    return wrote_mdl


def write_static_instances ( scene_name, objs, geom, f, write_block=False ):
    wrote_mdl = False
    #TODO Note that the use of "Scene" here is a temporary measure!!!!
    if (objs != None) and (geom != None):
      if 'model_object_list' in objs:
        num_static = 0
        for o in objs['model_object_list']:
          if not o['dynamic']:
            num_static += 1
        if num_static > 0:
          wrote_mdl = True
          if write_block:
            f.write ( "INSTANTIATE " + scene_name + " OBJECT\n" )
            f.write ( "{\n" )
          for o in objs['model_object_list']:
            if not o['dynamic']:
              f.write ( "  %s OBJECT %s {}\n" % (o['name'], o['name']) )
          if write_block:
            f.write ( "}\n" )
            f.write("\n")
    return wrote_mdl


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
    wrote_mdl = False
    if instantiate_name != None:
      f.write ( "INSTANTIATE " + instantiate_name + " OBJECT\n" )
      f.write ( "{\n" )
      wrote_mdl = True

    if rels != None:
      if 'release_site_list' in rels:
        rlist = rels['release_site_list']
        if len(rlist) > 0:
          wrote_mdl = True
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
      wrote_mdl = True
      f.write ( "}\n" )
      f.write("\n")
    return wrote_mdl


def write_modify_surf_regions ( modsurfrs, f ):
    wrote_mdl = False
    if 'modify_surface_regions_list' in modsurfrs:
      msrlist = modsurfrs['modify_surface_regions_list']
      if len(msrlist) > 0:
        wrote_mdl = True
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
    return wrote_mdl


def write_release_patterns ( pats, f ):
    wrote_mdl = False
    if 'release_pattern_list' in pats:
      plist = pats['release_pattern_list']
      if len(plist) > 0:
        wrote_mdl = True
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
    return wrote_mdl


def write_viz_out ( scene_name, vizout, mols, f ):

    wrote_mdl = False

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
      wrote_mdl = True
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

    return wrote_mdl


def write_react_out ( scene_name, rout, mols, time_step, f ):

    wrote_mdl = False

    if ("reaction_output_list" in rout) and (len(rout["reaction_output_list"]) > 0):
        context_scene_name = scene_name

        wrote_mdl = True

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
    return wrote_mdl


"""
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
"""





def write_data_model ( dm, file_name ):
  """ Write a data model to a named file """
  if (file_name[-5:].lower() == '.json'):
    # Assume this is a JSON format file
    print ( "Saving a JSON file" )
    f = open ( file_name, 'w' )
    status = f.write ( json.dumps ( dm ) )
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
  if 'children' in parent:
    children = parent['children']
    for k in children.keys():
      child = children[k]
      child_depth = get_max_depth ( child )
      if child_depth > max_child_depth:
        max_child_depth = child_depth
  return ( max_child_depth + 1 )


def check_legal ( parent ):
  # Ensure that parents and children alternate between volume and surface
  if 'children' in parent:
    children = parent['children']
    if 'dim' in parent:
      for child_key in children.keys():
        if parent['dim'] == children[child_key]['dim']:
          print ( "ERROR: Nested Children must alternate dimensions" )
    for child in children:
      check_legal ( child )


def build_topology_from_list ( cdefs, parent ):
  c_by_name = {}
  for c in cdefs:
    print ( "cdef = " + str(c) )
    if len(c) == 3:
      # This is an outer compartment
      print ( "Outer" )
      parent['children'][c[0]] = { 'name':c[0], 'dim':c[1], 'vol':c[2], 'children':{} }
      c_by_name[c[0]] = parent['children'][c[0]]
    elif len(c) == 4:
      # This compartment has a parent ... find it and add it
      print ( "Inside " + str(c[3]) )
      c_by_name[c[3]]['children'][c[0]] = { 'name':c[0], 'dim':c[1], 'vol':c[2], 'children':{} }
      c_by_name[c[0]] = c_by_name[c[3]]['children'][c[0]]
  return parent


def assign_dimensions ( obj, inner_cube_dim, nesting_space ):
  # Figure out the dimensions needed for each object to contain its children
  obj['xdim'] = inner_cube_dim
  obj['ydim'] = inner_cube_dim
  obj['zdim'] = inner_cube_dim
  if 'children' in obj:
    children = obj['children']
    if len(children) > 0:
      for k in children.keys():
        child = children[k]
        assign_dimensions ( child, inner_cube_dim, nesting_space )
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


def assign_coordinates ( obj, x, y, z, nesting_space ):
  # Convert the dimensions to actual coordinates
  obj['x'] = x
  obj['y'] = y
  obj['z'] = z
  if 'children' in obj:
    children = obj['children']
    if len(children) > 0:
      x_offset = nesting_space - ( obj['xdim'] / 2.0 )
      for k in children.keys():
        child = children[k]
        assign_coordinates ( child, x+x_offset+(child['xdim']/2.0), y, z, nesting_space )
        x_offset += child['xdim'] + nesting_space


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


def append_objects ( obj, inner_parent, outer_parent, dm_geom_obj_list, dm_model_obj_list ):
  # Append this object (if 3D) and its 3D children to the data model object list
  print ( "append_objects called with obj = " + str(obj['name']) )
  if 'dim' in obj.keys():
    if obj['dim'] == '3':

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

      dm_geom_obj_list.append ( go )

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

      dm_model_obj_list.append ( mo )

  if 'children' in obj.keys():
    children = obj['children']
    if len(children) > 0:
      for k in children.keys():
        child = children[k]
        append_objects ( child, obj, inner_parent, dm_geom_obj_list, dm_model_obj_list )




example_world = { 'ECF': {
                      'PM1': { 
                          'CP1': {
                              'NM1':{
                                  'Nuc1':{}
                                    },
                              'ERM1':{
                                  'ER1':{}
                                     }
                                 }
                              },
                      'PM2': { 
                          'CP2': {
                              'NM2':{
                                  'Nuc2':{}
                                    },
                              'ERM2':{
                                  'ER2':{}
                                     }
                                 }
                              }
                           }
                  }

example_world = {'ECF': {'PM2': {'CP2': {'ERM2': {'ER2': {}}, 'NM2': {'Nuc2': {}}}}, 'PM1': {'CP1': {'NM1': {'Nuc1': {}}, 'ERM1': {'ER1': {}}}}}}


ex_world = {
  'children': {
    'ECF': {
      'name': 'ECF', 
      'vol': 
      'vol_ECF', 
      'children': {
        'PM1': {
          'name': 'PM1', 
          'vol': 'sa_PM*eff_width', 
          'children': {
            'CP1': {
              'name': 'CP1', 
              'vol': 'vol_CP', 
              'children': {
                'ERM1': {
                  'name': 'ERM1', 
                  'vol': 'sa_ERM*eff_width', 
                  'children': {
                    'ER1': {
                      'name': 'ER1', 
                      'vol': 'vol_ER', 
                      'children': {}, 
                      'dim': '3'
                    }
                  },
                  'dim': '2'
                }, 
                'NM1': {
                  'name': 'NM1', 
                  'vol': 'sa_NM*eff_width', 
                  'children': {
                    'Nuc1': {
                      'name': 'Nuc1', 
                      'vol': 'vol_Nuc', 
                      'children': {}, 
                      'dim': '3'}
                    }, 
                    'dim': '2'
                  }
                }, 
                'dim': '3'
              }
            }, 
            'dim': '2'
          }, 
          'PM2': {
            'name': 'PM2', 
            'vol': 'sa_PM*eff_width', 
            'children': {
              'CP2': {
                'name': 'CP2', 
                'vol': 'vol_CP', 
                'children': {
                  'ERM2': {
                    'name': 'ERM2', 
                    'vol': 'sa_ERM*eff_width', 
                    'children': {
                      'ER2': {
                        'name': 'ER2',
                        'vol': 'vol_ER',
                        'children': {}, 
                        'dim': '3'
                      }
                    }, 
                    'dim': '2'
                  }, 
                  'NM2': {
                    'name': 'NM2', 
                    'vol': 'sa_NM*eff_width', 
                    'children': {
                      'Nuc2': {
                        'name': 'Nuc2', 
                        'vol': 'vol_Nuc', 
                        'children': {}, 
                        'dim': '3'
                      }
                    }, 
                    'dim': '2'
                  }
                }, 
                'dim': '3'
              }
            },
            'dim': '2'
          }
        }, 
        'dim': '3'
      }
    }
  }


if __name__ == "__main__":

    dmf = {}

    default_vol_dc = "8.51e-7"
    default_surf_dc = "1.7e-7"

    if len(sys.argv) > 2:
        print ( "Got parameters: " + sys.argv[1] + " " + sys.argv[2] )
        print ( "Reading BioNetGen File: " + sys.argv[1] )
        
        bngl_model_file = open ( sys.argv[1], 'r' )
        bngl_model_text = bngl_model_file.read()
        
        # First split by lines to remove comments and whitespace on ends
        lines = re.split(r'\n', bngl_model_text)
        i = 0
        for i in range(len(lines)):
          l = lines[i]
          if '#' in l:
            lines[i] = l.split('#')[0].strip()

        # Remove any empty lines
        lines = [ l for l in lines if len(l) > 0 ]

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
        dm = { 'mcell': { 'api_version': 0, 'blender_version': [2,78,0], 'data_model_version': "DM_2017_06_23_1300" } }
        dm['mcell']['cellblender_source_sha1'] = "61cc8da7bfe09b42114982616ce284301adad4cc"
        dm['mcell']['cellblender_version'] = "0.1.54"
        dm['mcell']['model_language'] = "mcell3r"


        # Now start building the data model
        
        special_parameters = { 'ITERATIONS': 1000, 'TIME_STEP': 1e-6, 'VACANCY_SEARCH_DISTANCE': 10 }

        # Add the parameter system

        par_list = []
        for block in blocks:
          if ' '.join(block[0].split()[1:]) == 'parameters':
            # Process parameters
            for line in block[1:-1]:
              # Pull MCellR special items out of the BNGL file (they appear to be coded as regular parameters such as ITERATIONS...)
              name_val = line.split()
              if name_val[0] in special_parameters.keys():
                special_parameters[name_val[0]] = name_val[1]
              else:
                par = {}
                par['par_name'] = name_val[0]
                par['par_expression'] = name_val[1]
                par['par_description'] = ""
                par['par_units'] = ""
                par_list.append ( par )
        dm['mcell']['parameter_system'] = { 'model_parameters': par_list }

        # Add the molecules list

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

              print ( "***** WARNING: Using fixed 3D names of Lig and Syk" )
              if mol['mol_name'] in ['Lig','Syk']:
                mol['mol_type'] = '3D'
              else:
                mol['mol_type'] = '2D'

              mol['custom_space_step'] = ""
              mol['custom_time_step'] = ""
              mol['description'] = ""

              print ( "***** WARNING: Using fixed diffusion constants" )
              if mol['mol_type'] == '3D':
                mol['diffusion_constant'] = "8.51e-7"
              else:
                mol['diffusion_constant'] = "1.7e-7"

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
        dm['mcell']['define_molecules'] = { 'molecule_list': mol_list, 'data_model_version': "DM_2014_10_24_1638" }

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

        for block in blocks:
          if ' '.join(block[0].split()[1:]) == 'compartments':
            # Process compartments

            print ( "***** WARNING: Compartment Volumes are not used" )

            print ( "Here's the block: " + str(block) )

            if False:
                block = """begin compartments
                          ECF   3    vol_ECF

                          PM1   2    sa_PM*eff_width    ECF
                          CP1   3    vol_CP             PM1
                          NM1   2    sa_NM*eff_width    CP1
                          Nuc1  3    vol_Nuc            NM1
                          ERM1  2    sa_ERM*eff_width   CP1
                          ER1   3    vol_ER             ERM1

                          PM2   2    sa_PM*eff_width    ECF
                          CP2   3    vol_CP             PM2
                          NM2   2    sa_NM*eff_width    CP2
                          Nuc2  3    vol_Nuc            NM2
                          ERM2  2    sa_ERM*eff_width   CP2
                          ER2   3    vol_ER             ERM2
                        end compartments""".split('\n')

            cdefs = []
            for line in block[1:-1]:
              parts = [ p for p in line.strip().split() ]
              cdefs.append(parts)

            topology = build_topology_from_list ( cdefs, { 'children':{}, 'name':"World" } )
            check_legal ( topology )
            assign_dimensions ( topology, inner_cube_dim, nesting_space )

            assign_coordinates ( topology, 0, 0, 0, nesting_space )

            append_objects ( topology, None, None, dm['mcell']['geometrical_objects']['object_list'], dm['mcell']['model_objects']['model_object_list'] )

            print ( "Max depth = " + str(get_max_depth(topology)) )

            # Print the compartments:
            print ( "Topology = " + str(topology) )

            dump_data_model ( "Topology", topology )


        # Change the materials to add a new one for each object
        mat_name_number = 1
        for obj in dm['mcell']['geometrical_objects']['object_list']:
          if len(obj['material_names']) > 0:
            if obj['material_names'][0] == 'membrane_mat':
              # Make a new material to replace the defaulted "membrane_mat"
              mat_name = obj['name'] + '_mat_' + str(mat_name_number)
              dm['mcell']['materials']['material_dict'][mat_name] = { 'diffuse_color' : { 'a':0.1, 'r':mat_name_number&1, 'g':mat_name_number&2, 'b':mat_name_number&4 } }
              obj['material_names'][0] = mat_name
              mat_name_number += 1

        # Make a "Modify Surface Regions" "ALL" entry for every object
        dm['mcell']['modify_surface_regions'] = {
          'data_model_version' : "DM_2014_10_24_1638",
          'modify_surface_regions_list' : []
        }

        # Make a "Modify Surface Regions" entry for every named surface in an object
        for obj in dm['mcell']['geometrical_objects']['object_list']:
          msr = {
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'name' : "Surface Class: reflect   Object: " + obj['name'] + "   ALL",
              'object_name' : obj['name'],
              'region_name' : "",
              'region_selection' : "ALL",
              'surf_class_name' : "reflect"
            }
          dm['mcell']['modify_surface_regions']['modify_surface_regions_list'].append ( msr )

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
              dm['mcell']['modify_surface_regions']['modify_surface_regions_list'].append ( msr )


        # Add the seed species as release sites

        dm['mcell']['release_sites'] = { 'data_model_version' : "DM_2014_10_24_1638" }
        rel_list = []
        site_num = 1
        for block in blocks:
          if ' '.join(block[0].split()[1:]) == 'seed species':
            # Process seed species
            for line in block[1:-1]:
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
              # Need to fill in fields for obj_expr since these have not been parsed yet
              if site_num == 1:
                rel_item['object_expr'] = "EC[ALL] - CP[ALL]"
              elif site_num == 2:
                rel_item['object_expr'] = "CP[PM]"
              elif site_num == 3:
                rel_item['object_expr'] = "CP"
              elif site_num == 4:
                rel_item['object_expr'] = "CP[PM]"

              rel_list.append(rel_item)
              site_num += 1

        dm['mcell']['release_sites']['release_site_list'] = rel_list



        # observables
        dm['mcell']['viz_output'] = {
          'all_iterations' : True,
          'data_model_version' : "DM_2014_10_24_1638",
          'end' : "1000",
          'export_all' : True,
          'start' : "0",
          'step' : "5"
        }
        dm['mcell']['reaction_data_output'] = {
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

        # This regular expression seems to find BNGL molecules with parens: \b\w+\([\w,~\!\?\+]+\)+([.]\w+\([\w,~\!\?\+]+\))*
        mol_regx = "\\b\\w+\\([\\w,~\\!\\?\\+]+\\)+([.]\\w+\\([\\w,~\\!\\?\\+]+\\))*"

        # This regular expression seems to find BNGL molecules with or without parens: \b\w+(\([\w,~\!\?\+]+\)+)*([.]\w+\([\w,~\!\?\+]+\))*
        mol_regx = "\\b\\w+(\\([\\w,~\\!\\?\\+]+\\)+)*([.]\\w+\\([\\w,~\\!\\?\\+]+\\))*"

        compiled_mol_regx = re.compile(mol_regx)

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
              if len(things_to_count) == 0:
                # This happens when a non-BNGL molecule is specified that doesn't have "()"
                pass

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
              dm['mcell']['reaction_data_output']['reaction_output_list'].append ( count_item )


        # reaction rules
        dm['mcell']['define_reactions'] = { 'data_model_version' : "DM_2014_10_24_1638" }
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
                # Time for a regular expression ... This could use some expert review!!!
                import re
                last_comma_regexp = "[,][\w\d\+\-\.\s]*$"
                cregx = re.compile ( last_comma_regexp )
                m = cregx.search(parts[1])
                rrate = parts[1][m.start()+1:].strip()
                pre_comma = parts[1][0:m.start()].strip()
                products,frate = [ p.strip() for p in pre_comma.split() ]
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
                products,frate = [ p.strip() for p in parts[1].split() ]
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

        dm['mcell']['define_reactions']['reaction_list'] = react_list


        # reaction rules
        """
        dm['mcell']['define_reactions'] = {
          'data_model_version' : "DM_2014_10_24_1638",
          'reaction_list' : [
            {
              'bkwd_rate' : "km1",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "kp1",
              'name' : "Rec(a) + Lig(l,l) <-> Rec(a!1).Lig(l!1,l)",
              'products' : "Rec(a!1).Lig(l!1,l)",
              'reactants' : "Rec(a) + Lig(l,l)",
              'rxn_name' : "",
              'rxn_type' : "reversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "kmL",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "kpL",
              'name' : "Rec(b~Y) + Lyn(U,SH2) <-> Rec(b~Y!1).Lyn(U!1,SH2)",
              'products' : "Rec(b~Y!1).Lyn(U!1,SH2)",
              'reactants' : "Rec(b~Y) + Lyn(U,SH2)",
              'rxn_name' : "",
              'rxn_type' : "reversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pLb",
              'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)",
              'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)",
              'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pLg",
              'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)",
              'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)",
              'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "kmLs",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "kpLs",
              'name' : "Rec(b~pY) + Lyn(U,SH2) <-> Rec(b~pY!1).Lyn(U,SH2!1)",
              'products' : "Rec(b~pY!1).Lyn(U,SH2!1)",
              'reactants' : "Rec(b~pY) + Lyn(U,SH2)",
              'rxn_name' : "",
              'rxn_type' : "reversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pLbs",
              'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)",
              'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)",
              'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pLgs",
              'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)",
              'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)",
              'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "kmS",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "kpS",
              'name' : "Rec(g~pY) + Syk(tSH2) <-> Rec(g~pY!1).Syk(tSH2!1)",
              'products' : "Rec(g~pY!1).Syk(tSH2!1)",
              'reactants' : "Rec(g~pY) + Syk(tSH2)",
              'rxn_name' : "",
              'rxn_type' : "reversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pLS",
              'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
              'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
              'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pLSs",
              'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
              'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
              'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pSS",
              'name' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
              'products' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
              'reactants' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "pSSs",
              'name' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
              'products' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
              'reactants' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "dm",
              'name' : "Rec(b~pY) -> Rec(b~Y)",
              'products' : "Rec(b~Y)",
              'reactants' : "Rec(b~pY)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "dm",
              'name' : "Rec(g~pY) -> Rec(g~Y)",
              'products' : "Rec(g~Y)",
              'reactants' : "Rec(g~pY)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "dm",
              'name' : "Syk(tSH2! + ,l~pY) -> Syk(tSH2! + ,l~Y)",
              'products' : "Syk(tSH2! + ,l~Y)",
              'reactants' : "Syk(tSH2! + ,l~pY)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "dm",
              'name' : "Syk(tSH2! + ,a~pY) -> Syk(tSH2! + ,a~Y)",
              'products' : "Syk(tSH2! + ,a~Y)",
              'reactants' : "Syk(tSH2! + ,a~pY)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "dc",
              'name' : "Syk(tSH2,l~pY) -> Syk(tSH2,l~Y)",
              'products' : "Syk(tSH2,l~Y)",
              'reactants' : "Syk(tSH2,l~pY)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            },
            {
              'bkwd_rate' : "",
              'data_model_version' : "DM_2018_01_11_1330",
              'description' : "",
              'fwd_rate' : "dc",
              'name' : "Syk(tSH2,a~pY) -> Syk(tSH2,a~Y)",
              'products' : "Syk(tSH2,a~Y)",
              'reactants' : "Syk(tSH2,a~pY)",
              'rxn_name' : "",
              'rxn_type' : "irreversible",
              'variable_rate' : "",
              'variable_rate_switch' : False,
              'variable_rate_text' : "",
              'variable_rate_valid' : False
            }
          ]
        }
        """

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

        # This is the entire data model from the actual fceri version

        dmf['mcell'] = {
          'api_version' : 0,
          'blender_version' : [2, 78, 0],
          'cellblender_source_sha1' : "61cc8da7bfe09b42114982616ce284301adad4cc",
          'cellblender_version' : "0.1.54",
          'data_model_version' : "DM_2017_06_23_1300",
          'define_molecules' : {
            'data_model_version' : "DM_2014_10_24_1638",
            'molecule_list' : [
              {
                'bngl_component_list' : [
                  {
                    'cname' : "l",
                    'cstates' : []
                  },
                  {
                    'cname' : "l",
                    'cstates' : []
                  }
                ],
                'custom_space_step' : "",
                'custom_time_step' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'diffusion_constant' : "8.51e-7",
                'display' : {
                  'color' : [0.07500000298023224, 0.550000011920929, 1.0],
                  'emit' : 0.0,
                  'glyph' : "Tetrahedron",
                  'scale' : 1.0
                },
                'export_viz' : False,
                'maximum_step_length' : "",
                'mol_bngl_label' : "",
                'mol_name' : "Lig",
                'mol_type' : "3D",
                'target_only' : False
              },
              {
                'bngl_component_list' : [
                  {
                    'cname' : "U",
                    'cstates' : []
                  },
                  {
                    'cname' : "SH2",
                    'cstates' : []
                  }
                ],
                'custom_space_step' : "",
                'custom_time_step' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'diffusion_constant' : "1.7e-7",
                'display' : {
                  'color' : [1.0, 1.0, 0.0],
                  'emit' : 1.0,
                  'glyph' : "Sphere_2",
                  'scale' : 2.0
                },
                'export_viz' : False,
                'maximum_step_length' : "",
                'mol_bngl_label' : "",
                'mol_name' : "Lyn",
                'mol_type' : "2D",
                'target_only' : False
              },
              {
                'bngl_component_list' : [
                  {
                    'cname' : "tSH2",
                    'cstates' : []
                  },
                  {
                    'cname' : "l",
                    'cstates' : ['Y', 'pY']
                  },
                  {
                    'cname' : "a",
                    'cstates' : ['Y', 'pY']
                  }
                ],
                'custom_space_step' : "",
                'custom_time_step' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'diffusion_constant' : "8.51e-7",
                'display' : {
                  'color' : [0.008200000040233135, 1.0, 0.0],
                  'emit' : 2.0,
                  'glyph' : "Cube",
                  'scale' : 1.0
                },
                'export_viz' : False,
                'maximum_step_length' : "",
                'mol_bngl_label' : "",
                'mol_name' : "Syk",
                'mol_type' : "3D",
                'target_only' : False
              },
              {
                'bngl_component_list' : [
                  {
                    'cname' : "a",
                    'cstates' : []
                  },
                  {
                    'cname' : "b",
                    'cstates' : ['Y', 'pY']
                  },
                  {
                    'cname' : "g",
                    'cstates' : ['Y', 'pY']
                  }
                ],
                'custom_space_step' : "",
                'custom_time_step' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'diffusion_constant' : "1.7e-7",
                'display' : {
                  'color' : [1.0, 0.27000001072883606, 0.029999999329447746],
                  'emit' : 0.0,
                  'glyph' : "Torus",
                  'scale' : 4.0
                },
                'export_viz' : False,
                'maximum_step_length' : "",
                'mol_bngl_label' : "",
                'mol_name' : "Rec",
                'mol_type' : "2D",
                'target_only' : False
              }
            ]
          },
          'define_reactions' : {
            'data_model_version' : "DM_2014_10_24_1638",
            'reaction_list' : [
              {
                'bkwd_rate' : "km1",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "kp1",
                'name' : "Rec(a) + Lig(l,l) <-> Rec(a!1).Lig(l!1,l)",
                'products' : "Rec(a!1).Lig(l!1,l)",
                'reactants' : "Rec(a) + Lig(l,l)",
                'rxn_name' : "",
                'rxn_type' : "reversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "kmL",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "kpL",
                'name' : "Rec(b~Y) + Lyn(U,SH2) <-> Rec(b~Y!1).Lyn(U!1,SH2)",
                'products' : "Rec(b~Y!1).Lyn(U!1,SH2)",
                'reactants' : "Rec(b~Y) + Lyn(U,SH2)",
                'rxn_name' : "",
                'rxn_type' : "reversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pLb",
                'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)",
                'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~pY)",
                'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,b~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pLg",
                'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)",
                'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY)",
                'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "kmLs",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "kpLs",
                'name' : "Rec(b~pY) + Lyn(U,SH2) <-> Rec(b~pY!1).Lyn(U,SH2!1)",
                'products' : "Rec(b~pY!1).Lyn(U,SH2!1)",
                'reactants' : "Rec(b~pY) + Lyn(U,SH2)",
                'rxn_name' : "",
                'rxn_type' : "reversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pLbs",
                'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)",
                'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~pY)",
                'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,b~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pLgs",
                'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)",
                'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY)",
                'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "kmS",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "kpS",
                'name' : "Rec(g~pY) + Syk(tSH2) <-> Rec(g~pY!1).Syk(tSH2!1)",
                'products' : "Rec(g~pY!1).Syk(tSH2!1)",
                'reactants' : "Rec(g~pY) + Syk(tSH2)",
                'rxn_name' : "",
                'rxn_type' : "reversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pLS",
                'name' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
                'products' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
                'reactants' : "Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b~Y!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pLSs",
                'name' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y) -> Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
                'products' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~pY)",
                'reactants' : "Lig(l!1,l!2).Lyn(U,SH2!3).Rec(a!2,b~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,l~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pSS",
                'name' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
                'products' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
                'reactants' : "Lig(l!1,l!2).Syk(tSH2!3,a~Y).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "pSSs",
                'name' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y) -> Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
                'products' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~pY)",
                'reactants' : "Lig(l!1,l!2).Syk(tSH2!3,a~pY).Rec(a!2,g~pY!3).Rec(a!1,g~pY!4).Syk(tSH2!4,a~Y)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "dm",
                'name' : "Rec(b~pY) -> Rec(b~Y)",
                'products' : "Rec(b~Y)",
                'reactants' : "Rec(b~pY)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "dm",
                'name' : "Rec(g~pY) -> Rec(g~Y)",
                'products' : "Rec(g~Y)",
                'reactants' : "Rec(g~pY)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "dm",
                'name' : "Syk(tSH2! + ,l~pY) -> Syk(tSH2! + ,l~Y)",
                'products' : "Syk(tSH2! + ,l~Y)",
                'reactants' : "Syk(tSH2! + ,l~pY)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "dm",
                'name' : "Syk(tSH2! + ,a~pY) -> Syk(tSH2! + ,a~Y)",
                'products' : "Syk(tSH2! + ,a~Y)",
                'reactants' : "Syk(tSH2! + ,a~pY)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "dc",
                'name' : "Syk(tSH2,l~pY) -> Syk(tSH2,l~Y)",
                'products' : "Syk(tSH2,l~Y)",
                'reactants' : "Syk(tSH2,l~pY)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              },
              {
                'bkwd_rate' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'fwd_rate' : "dc",
                'name' : "Syk(tSH2,a~pY) -> Syk(tSH2,a~Y)",
                'products' : "Syk(tSH2,a~Y)",
                'reactants' : "Syk(tSH2,a~pY)",
                'rxn_name' : "",
                'rxn_type' : "irreversible",
                'variable_rate' : "",
                'variable_rate_switch' : False,
                'variable_rate_text' : "",
                'variable_rate_valid' : False
              }
            ]
          },
          'define_release_patterns' : {
            'data_model_version' : "DM_2014_10_24_1638",
            'release_pattern_list' : []
          },
          'define_surface_classes' : {
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
          },
          'geometrical_objects' : {
            'object_list' : [
              {
                'define_surface_regions' : [
                  {
                    'include_elements' : [1, 7],
                    'name' : "PM"
                  }
                ],
                'element_connections' : [
                  [0, 1, 2],
                  [4, 7, 6],
                  [0, 4, 5],
                  [1, 5, 6],
                  [2, 6, 7],
                  [4, 0, 3],
                  [3, 0, 2],
                  [5, 4, 6],
                  [1, 0, 5],
                  [2, 1, 6],
                  [3, 2, 7],
                  [7, 4, 3]
                ],
                'location' : [0, 0, 0],
                'material_names' : ['CP_mat'],
                'name' : "CP",
                'vertex_list' : [
                  [0.5, 0.5, -0.5],
                  [0.5, -0.5, -0.5],
                  [-0.5, -0.5, -0.5],
                  [-0.5, 0.5, -0.5],
                  [0.5, 0.5, 0.5],
                  [0.5, -0.5, 0.5],
                  [-0.5, -0.5, 0.5],
                  [-0.5, 0.5, 0.5]
                ]
              },
              {
                'define_surface_regions' : [
                  {
                    'include_elements' : [
                      0,
                      1,
                      2,
                      3,
                      4,
                      5,
                      6,
                      7,
                      8,
                      9,
                      10,
                      11
                    ],
                    'name' : "wall"
                  }
                ],
                'element_connections' : [
                  [4, 5, 1],
                  [5, 6, 2],
                  [6, 7, 3],
                  [7, 4, 0],
                  [0, 1, 2],
                  [7, 6, 5],
                  [0, 4, 1],
                  [1, 5, 2],
                  [2, 6, 3],
                  [3, 7, 0],
                  [3, 0, 2],
                  [4, 7, 5]
                ],
                'location' : [0, 0, 0],
                'material_names' : ['EC_mat'],
                'name' : "EC",
                'vertex_list' : [
                  [-2.0, -1.25, -1.0],
                  [-2.0, 1.25, -1.0],
                  [2.0, 1.25, -1.0],
                  [2.0, -1.25, -1.0],
                  [-2.0, -1.25, 1.0],
                  [-2.0, 1.25, 1.0],
                  [2.0, 1.25, 1.0],
                  [2.0, -1.25, 1.0]
                ]
              }
            ]
          },
          'initialization' : {
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
          },
          'materials' : {
            'material_dict' : {
              'CP_mat' : {
                'diffuse_color' : {
                  'a' : 0.3799999952316284,
                  'b' : 0.7300000190734863,
                  'g' : 0.0,
                  'r' : 0.800000011920929
                }
              },
              'EC_mat' : {
                'diffuse_color' : {
                  'a' : 0.10000000149011612,
                  'b' : 0.4300000071525574,
                  'g' : 0.4300000071525574,
                  'r' : 0.4300000071525574
                }
              }
            }
          },
          'model_language' : "mcell3r",
          'model_objects' : {
            'data_model_version' : "DM_2018_01_11_1330",
            'model_object_list' : [
              {
                'description' : "",
                'dynamic' : False,
                'dynamic_display_source' : "script",
                'membrane_name' : "PM",
                'name' : "CP",
                'object_source' : "blender",
                'parent_object' : "EC",
                'script_name' : ""
              },
              {
                'description' : "",
                'dynamic' : False,
                'dynamic_display_source' : "script",
                'membrane_name' : "",
                'name' : "EC",
                'object_source' : "blender",
                'parent_object' : "",
                'script_name' : ""
              }
            ]
          },
          'modify_surface_regions' : {
            'data_model_version' : "DM_2014_10_24_1638",
            'modify_surface_regions_list' : [
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'name' : "Surface Class: reflect   Object: EC   Region: wall",
                'object_name' : "EC",
                'region_name' : "wall",
                'region_selection' : "SEL",
                'surf_class_name' : "reflect"
              },
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'name' : "Surface Class: reflect   Object: EC   ALL",
                'object_name' : "EC",
                'region_name' : "",
                'region_selection' : "ALL",
                'surf_class_name' : "reflect"
              },
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'name' : "Surface Class: reflect   Object: CP   Region: PM",
                'object_name' : "CP",
                'region_name' : "PM",
                'region_selection' : "SEL",
                'surf_class_name' : "reflect"
              },
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'name' : "Surface Class: reflect   Object: CP   ALL",
                'object_name' : "CP",
                'region_name' : "",
                'region_selection' : "ALL",
                'surf_class_name' : "reflect"
              }
            ]
          },
          'mol_viz' : {
            'active_seed_index' : 0,
            'color_index' : 0,
            'color_list' : [
              [0.800000011920929, 0.0, 0.0],
              [0.0, 0.800000011920929, 0.0],
              [0.0, 0.0, 0.800000011920929],
              [0.0, 0.800000011920929, 0.800000011920929],
              [0.800000011920929, 0.0, 0.800000011920929],
              [0.800000011920929, 0.800000011920929, 0.0],
              [1.0, 1.0, 1.0],
              [0.0, 0.0, 0.0]
            ],
            'data_model_version' : "DM_2015_04_13_1700",
            'file_dir' : "",
            'file_index' : 312,
            'file_name' : "Scene.cellbin.0312.dat",
            'file_num' : 1001,
            'file_start_index' : 0,
            'file_step_index' : 1,
            'file_stop_index' : 1000,
            'manual_select_viz_dir' : False,
            'render_and_save' : False,
            'seed_list' : ['seed_00001'],
            'viz_enable' : True,
            'viz_list' : [
              "mol_volume_proxy",
              "mol_surface_proxy",
              "mol_Rec",
              "mol_Lyn",
              "mol_Syk",
              "mol_Lig"
            ]
          },
          'parameter_system' : {
            'model_parameters' : [
              {
                'par_description' : "Avogadro number based on a volume size of 1 cubic um",
                'par_expression' : "6.022e8",
                'par_name' : "Nav",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.01",
                'par_name' : "rxn_layer_t",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Surface area",
                'par_expression' : "0.88/rxn_layer_t",
                'par_name' : "vol_wall",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "39",
                'par_name' : "vol_EC",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Surface area",
                'par_expression' : "0.01/rxn_layer_t",
                'par_name' : "vol_PM",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "1",
                'par_name' : "vol_CP",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Default: 6.0e3",
                'par_expression' : "6.0e3 * Scale_Totals",
                'par_name' : "Lig_tot",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Default: 4.0e2",
                'par_expression' : "4.0e2 * Scale_Totals",
                'par_name' : "Rec_tot",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Default: 2.8e2",
                'par_expression' : "2.8e2 * Scale_Totals",
                'par_name' : "Lyn_tot",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Default: 4e2",
                'par_expression' : "4e2 * Scale_Totals",
                'par_name' : "Syk_tot",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "0.00358 gives at least one each,   0.5 gives 2 of some",
                'par_expression' : "1",
                'par_name' : "Scale_Totals",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.000166057788110262*Nav",
                'par_name' : "kp1",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.00",
                'par_name' : "km1",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "1.66057788110262e-06/rxn_layer_t",
                'par_name' : "kp2",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.00",
                'par_name' : "km2",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.0166057788110262/rxn_layer_t",
                'par_name' : "kpL",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "20",
                'par_name' : "kmL",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.0166057788110262/rxn_layer_t",
                'par_name' : "kpLs",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.12",
                'par_name' : "kmLs",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.0166057788110262*Nav",
                'par_name' : "kpS",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.13",
                'par_name' : "kmS",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "30",
                'par_name' : "pLb",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "100",
                'par_name' : "pLbs",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "1",
                'par_name' : "pLg",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "3",
                'par_name' : "pLgs",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "30",
                'par_name' : "pLS",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "100",
                'par_name' : "pLSs",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "100",
                'par_name' : "pSS",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "200",
                'par_name' : "pSSs",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.1",
                'par_name' : "dm",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "",
                'par_expression' : "0.1",
                'par_name' : "dc",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Temperature, K",
                'par_expression' : "298.15",
                'par_name' : "T",
                'par_units' : "K",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Thickness of 2D compartment, um",
                'par_expression' : "rxn_layer_t",
                'par_name' : "h",
                'par_units' : "um",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Radius of a (spherical) molecule in 3D compartment, um",
                'par_expression' : "0.002564",
                'par_name' : "Rs",
                'par_units' : "um",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Radius of a (cylindrical) molecule in 2D compartment, um",
                'par_expression' : "0.0015",
                'par_name' : "Rc",
                'par_units' : "um",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Euler's constant",
                'par_expression' : "0.5722",
                'par_name' : "gamma",
                'par_units' : "",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Boltzmann constant, cm^2.kg/K.s^2",
                'par_expression' : "1.3806488e-19",
                'par_name' : "KB",
                'par_units' : "cm^2.kg/K.s^2",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Viscosity in compartment wall, kg/um.s",
                'par_expression' : "1e-9",
                'par_name' : "mu_wall",
                'par_units' : "kg/um.s",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Viscosity in compartment EC, kg/um.s",
                'par_expression' : "1e-9",
                'par_name' : "mu_EC",
                'par_units' : "kg/um.s",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Viscosity in compartment PM, kg/um.s",
                'par_expression' : "1e-9",
                'par_name' : "mu_PM",
                'par_units' : "kg/um.s",
                'sweep_enabled' : False,
              },
              {
                'par_description' : "Viscosity in compartment CP, kg/um.s",
                'par_expression' : "1e-9",
                'par_name' : "mu_CP",
                'par_units' : "kg/um.s",
                'sweep_enabled' : False,
              }
            ],
          },
          'reaction_data_output' : {
            'always_generate' : True,
            'combine_seeds' : True,
            'data_model_version' : "DM_2016_03_15_1800",
            'mol_colors' : False,
            'output_buf_size' : "",
            'plot_layout' : " plot ",
            'plot_legend' : "0",
            'reaction_output_list' : [
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "LycFree",
                'mdl_string' : "COUNT[Lyn(U,SH2), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Lyn(U,SH2), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecPbeta",
                'mdl_string' : "COUNT[Rec(b~pY!?), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Rec(b~pY!?), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecMon",
                'mdl_string' : "COUNT[Rec(a!1).Lig(l!1,l), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Rec(a!1).Lig(l!1,l), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecDim",
                'mdl_string' : "COUNT[Rec(a!1).Lig(l!1,l!2).Rec(a!2), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Rec(a!1).Lig(l!1,l!2).Rec(a!2), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecRecLigLyn",
                'mdl_string' : "COUNT[Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b!3).Rec(a!1,b), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Lig(l!1,l!2).Lyn(U!3,SH2).Rec(a!2,b!3).Rec(a!1,b), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecPgamma",
                'mdl_string' : "COUNT[Rec(g~pY),WORLD] + COUNT[Rec(g~pY!+), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Rec(g~pY),WORLD] + COUNT[Rec(g~pY!+), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecSyk",
                'mdl_string' : "COUNT[Rec(g~pY!1).Syk(tSH2!1), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Rec(g~pY!1).Syk(tSH2!1), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "RecSykPS",
                'mdl_string' : "COUNT[Rec(g~pY!1).Syk(tSH2!1,a~pY), WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Rec(g~pY!1).Syk(tSH2!1,a~pY), WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "Lig",
                'mdl_string' : "COUNT[Lig,WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Lig,WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              },
              {
                'count_location' : "World",
                'data_file_name' : "",
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'mdl_file_prefix' : "Lyn",
                'mdl_string' : "COUNT[Lyn,WORLD]",
                'molecule_name' : "",
                'name' : "MDL: COUNT[Lyn,WORLD]",
                'object_name' : "",
                'plotting_enabled' : True,
                'reaction_name' : "",
                'region_name' : "",
                'rxn_or_mol' : "MDLString"
              }
            ],
            'rxn_step' : ""
          },
          'release_sites' : {
            'data_model_version' : "DM_2014_10_24_1638",
            'release_site_list' : [
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'location_x' : "0",
                'location_y' : "0",
                'location_z' : "0",
                'molecule' : "@EC::Lig(l,l)",
                'name' : "ligand_rel",
                'object_expr' : "EC[ALL] - CP[ALL]",
                'orient' : "'",
                'pattern' : "",
                'points_list' : [],
                'quantity' : "Lig_tot",
                'quantity_type' : "NUMBER_TO_RELEASE",
                'release_probability' : "1",
                'shape' : "OBJECT",
                'site_diameter' : "0",
                'stddev' : "0"
              },
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'location_x' : "0",
                'location_y' : "0",
                'location_z' : "0",
                'molecule' : "@PM::Lyn(U,SH2)",
                'name' : "lyn_rel",
                'object_expr' : "CP[PM]",
                'orient' : "'",
                'pattern' : "",
                'points_list' : [],
                'quantity' : "Lyn_tot",
                'quantity_type' : "NUMBER_TO_RELEASE",
                'release_probability' : "1",
                'shape' : "OBJECT",
                'site_diameter' : "0",
                'stddev' : "0"
              },
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'location_x' : "0",
                'location_y' : "0",
                'location_z' : "0",
                'molecule' : "@CP::Syk(tSH2,l~Y,a~Y)",
                'name' : "syk_rel",
                'object_expr' : "CP",
                'orient' : "'",
                'pattern' : "",
                'points_list' : [],
                'quantity' : "Syk_tot",
                'quantity_type' : "NUMBER_TO_RELEASE",
                'release_probability' : "1",
                'shape' : "OBJECT",
                'site_diameter' : "0",
                'stddev' : "0"
              },
              {
                'data_model_version' : "DM_2018_01_11_1330",
                'description' : "",
                'location_x' : "0",
                'location_y' : "0",
                'location_z' : "0",
                'molecule' : "@PM::Rec(a,b~Y,g~Y)",
                'name' : "receptor_rel",
                'object_expr' : "CP[PM]",
                'orient' : "'",
                'pattern' : "",
                'points_list' : [],
                'quantity' : "Rec_tot",
                'quantity_type' : "NUMBER_TO_RELEASE",
                'release_probability' : "1",
                'shape' : "OBJECT",
                'site_diameter' : "0",
                'stddev' : "0"
              }
            ]
          },
          'scripting' : {
            'data_model_version' : "DM_2017_11_30_1830",
            'dm_external_file_name' : "",
            'dm_internal_file_name' : "",
            'force_property_update' : True,
            'ignore_cellblender_data' : False,
            'script_texts' : {},
            'scripting_list' : []
          },
          'simulation_control' : {
            'data_model_version' : "DM_2017_11_22_1617",
            'end_seed' : "1",
            'export_format' : "mcell_mdl_modular",
            'name' : "",
            'processes_list' : [],
            'run_limit' : "-1",
            'sim_engines' : [
              {
                'parameter_dictionary' : {
                  'Error File' : {
                    'as' : "filename",
                    'desc' : "Error File name",
                    'icon' : "EXPORT",
                    'val' : ""
                  },
                  'Log File' : {
                    'as' : "filename",
                    'desc' : "Log File name",
                    'icon' : "EXPORT",
                    'val' : ""
                  },
                  'MCell Path' : {
                    'as' : "filename",
                    'desc' : "MCell Path",
                    'icon' : "SCRIPTWIN",
                    'val' : ""
                  },
                  'Output Detail (0-100)' : {
                    'desc' : "Output Detail",
                    'val' : 20
                  }
                },
                'parameter_layout' : [
                  ['MCell Path'],
                  ['Version', 'Full Version', 'Help', 'Reset'],
                  ['Log File', 'Error File']
                ],
                'plug_active' : True,
                'plug_code' : "MCELL3",
                'plug_name' : "MCell 3 with Dynamic Geometry"
              },
              {
                'parameter_dictionary' : {
                  'Output Detail (0-100)' : {
                    'desc' : "Amount of Information to Print (0-100)",
                    'icon' : "INFO",
                    'val' : 20
                  },
                  'Python Command' : {
                    'as' : "filename",
                    'desc' : "Command to run Python (default is python)",
                    'icon' : "SCRIPTWIN",
                    'val' : ""
                  },
                  'Reaction Factor' : {
                    'desc' : "Decay Rate Multiplier",
                    'icon' : "ARROW_LEFTRIGHT",
                    'val' : 1.0
                  }
                },
                'parameter_layout' : [
                  ['Python Command'],
                  ['Output Detail (0-100)'],
                  ['Reaction Factor'],
                  ['Print Information', 'Reset']
                ],
                'plug_active' : True,
                'plug_code' : "LIM_PYTHON",
                'plug_name' : "Prototype Python Simulation"
              },
              {
                'parameter_dictionary' : {
                  'Error File' : {
                    'as' : "filename",
                    'desc' : "Error File name",
                    'icon' : "EXPORT",
                    'val' : ""
                  },
                  'Log File' : {
                    'as' : "filename",
                    'desc' : "Log File name",
                    'icon' : "EXPORT",
                    'val' : ""
                  },
                  'MCell Path' : {
                    'as' : "filename",
                    'desc' : "MCell Path",
                    'icon' : "SCRIPTWIN",
                    'val' : ""
                  },
                  'Output Detail (0-100)' : {
                    'desc' : "Output Detail",
                    'val' : 20
                  }
                },
                'parameter_layout' : [
                  ['MCell Path'],
                  ['Log File', 'Error File'],
                  ['Version', 'Full Version', 'Help', 'Reset']
                ],
                'plug_active' : True,
                'plug_code' : "MCELL3DM",
                'plug_name' : "MCell 3 via Data Model"
              },
              {
                'parameter_dictionary' : {
                  'BioNetGen Path' : {
                    'as' : "filename",
                    'desc' : "BioNetGen Path",
                    'icon' : "OUTLINER_DATA_MESH",
                    'val' : "bng2/BNG2.pl"
                  },
                  'MCellR Path' : {
                    'as' : "filename",
                    'desc' : "MCellR Path",
                    'icon' : "FORCE_LENNARDJONES",
                    'val' : "mcell"
                  },
                  'MCellRlib Path' : {
                    'as' : "filename",
                    'desc' : "MCellR Library Path",
                    'icon' : "FORCE_LENNARDJONES",
                    'val' : "lib/"
                  },
                  'Output Detail (0-100)' : {
                    'desc' : "Amount of Information to Print (0-100)",
                    'icon' : "INFO",
                    'val' : 20
                  },
                  'Shared Path' : {
                    'as' : "filename",
                    'desc' : "Shared Path",
                    'icon' : "FORCE_LENNARDJONES",
                    'val' : "/netapp/cnl/home/bobkuczewski/proj/Blender/downloads/Blender-2.78c-CellBlender-linux/2.78/scripts/addons/cellblender/extensions"
                  }
                },
                'parameter_layout' : [
                  ['Shared Path'],
                  ['MCellR Path'],
                  ['MCellRlib Path'],
                  ['BioNetGen Path'],
                  ['Output Detail (0-100)'],
                  ['Print Information', 'Postprocess', 'Reset']
                ],
                'plug_active' : True,
                'plug_code' : "MCELLR",
                'plug_name' : "MCell Rules"
              },
              {
                'parameter_dictionary' : {
                  'BioNetGen Path' : {
                    'as' : "filename",
                    'desc' : "BioNetGen Path",
                    'icon' : "OUTLINER_DATA_MESH",
                    'val' : "bionetgen/BNG2.pl"
                  },
                  'NFSIM' : {
                    'desc' : "Simulate using Network-free Simulation Method",
                    'val' : True
                  },
                  'ODE' : {
                    'desc' : "Simulate using Ordinary Differential Equation Solver",
                    'val' : False
                  },
                  'Output Detail (0-100)' : {
                    'desc' : "Amount of Information to Print (0-100)",
                    'icon' : "INFO",
                    'val' : 20
                  },
                  'PLA' : {
                    'desc' : "Simulate using Partitioned tau-Leaping Algorithm",
                    'val' : False
                  },
                  'SSA' : {
                    'desc' : "Simulate using Gillespie Stochastic Simulation Algorithm",
                    'val' : False
                  },
                  'Shared Path' : {
                    'as' : "filename",
                    'desc' : "Shared Path",
                    'icon' : "FORCE_LENNARDJONES",
                    'val' : "/netapp/cnl/home/bobkuczewski/proj/Blender/downloads/Blender-2.78c-CellBlender-linux/2.78/scripts/addons/cellblender/sim_engines/cBNGL"
                  }
                },
                'parameter_layout' : [
                  ['Shared Path'],
                  ['BioNetGen Path'],
                  ['ODE', 'NFSIM', 'SSA', 'PLA'],
                  ['Output Detail (0-100)'],
                  ['Print Information', 'Postprocess', 'Reset']
                ],
                'plug_active' : True,
                'plug_code' : "cBNGL",
                'plug_name' : "cBNGL"
              },
              {
                'parameter_dictionary' : {
                  'Auto Boundaries' : {
                    'desc' : "Compute boundaries from all geometric points",
                    'val' : True
                  },
                  'Command Line' : {
                    'desc' : "Additional Command Line Parameters",
                    'val' : ""
                  },
                  'Graphics' : {
                    'desc' : "Show Smoldyn Graphics",
                    'val' : False
                  },
                  'Output Detail (0-100)' : {
                    'desc' : "Amount of Information to Print (0-100)",
                    'icon' : "INFO",
                    'val' : 20
                  },
                  'Smoldyn Path' : {
                    'as' : "filename",
                    'desc' : "Optional Path",
                    'icon' : "SCRIPTWIN",
                    'val' : "//../../../../../smoldyn/smoldyn-2.51/cmake/smoldyn"
                  },
                  'bounding_cube_size' : {
                    'desc' : "Cube Boundary Size",
                    'val' : 2
                  },
                  'x_bound_max' : {
                    'desc' : "x boundary (maximum)",
                    'val' : 1.0
                  },
                  'x_bound_min' : {
                    'desc' : "x boundary (minimum)",
                    'val' : -1.0
                  },
                  'y_bound_max' : {
                    'desc' : "y boundary (maximum)",
                    'val' : 1.0
                  },
                  'y_bound_min' : {
                    'desc' : "y boundary (minimum)",
                    'val' : -1.0
                  },
                  'z_bound_max' : {
                    'desc' : "z boundary (maximum)",
                    'val' : 1.0
                  },
                  'z_bound_min' : {
                    'desc' : "z boundary (minimum)",
                    'val' : -1.0
                  }
                },
                'parameter_layout' : [
                  ['Smoldyn Path'],
                  ['Auto Boundaries', 'Set Cube Boundaries:', 'bounding_cube_size'],
                  ['x_bound_min', 'y_bound_min', 'z_bound_min'],
                  ['x_bound_max', 'y_bound_max', 'z_bound_max'],
                  ['Graphics', 'Command Line'],
                  ['Output Detail (0-100)'],
                  ['Postprocess', 'Reset']
                ],
                'plug_active' : True,
                'plug_code' : "SMOLDYN248",
                'plug_name' : "Prototype Smoldyn 2.48 Simulation"
              },
              {
                'parameter_dictionary' : {
                  'C++ Path' : {
                    'as' : "filename",
                    'desc' : "Optional Path",
                    'icon' : "SCRIPTWIN",
                    'val' : ""
                  },
                  'Decay Factor' : {
                    'desc' : "Decay Rate Multiplier",
                    'icon' : "ARROW_LEFTRIGHT",
                    'val' : 1.0
                  },
                  'Output Detail (0-100)' : {
                    'desc' : "Amount of Information to Print (0-100)",
                    'icon' : "INFO",
                    'val' : 20
                  }
                },
                'parameter_layout' : [
                  ['Output Detail (0-100)'],
                  ['Print Information', 'Reset']
                ],
                'plug_active' : True,
                'plug_code' : "LIM_CPP",
                'plug_name' : "Prototype C++ Simulation"
              }
            ],
            'start_seed' : "1"
          },
          'viz_output' : {
            'all_iterations' : True,
            'data_model_version' : "DM_2014_10_24_1638",
            'end' : "1000",
            'export_all' : True,
            'start' : "0",
            'step' : "5"
          }
        }


        #write_data_model ( dm, "test.txt" )
        
        # Compare?

        dm_keys = set(dm['mcell'].keys())
        dmf_keys = set(dmf['mcell'].keys())
        intersect_keys = dm_keys.intersection(dmf_keys)
        added = dm_keys - dmf_keys
        missing = dmf_keys - dm_keys
        modified = { o : (dm['mcell'][o], dmf['mcell'][o]) for o in intersect_keys if dm['mcell'][o] != dmf['mcell'][o] }
        same = set ( o for o in intersect_keys if dm['mcell'][o] == dmf['mcell'][o] )
        
        # dm = read_data_model ( sys.argv[1] )
        # dump_data_model ( dm )
        print ( "Writing CellBlender Data Model: " + sys.argv[2] )
        write_data_model ( dm, sys.argv[2] )
        # write_mdl ( dm, sys.argv[2] )
        print ( "Wrote BioNetGen file found in \"" + sys.argv[1] + "\" to CellBlender data model \"" + sys.argv[2] + "\"" )
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

