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
    header = f.read(20)
    if '"mcell":' in header:
      is_json = True
    elif "'mcell':" in header:
      is_json = True
    f.close()
    # Open as appropriate
    if is_json:
        # Open as a JSON format file
        print ( "Opening a JSON file" )
        f = open ( file_name, 'r' )
        print ( "Reading a JSON file" )
        json_model = f.read()
        print ( "Loading a JSON file" )
        data_model = json.loads ( json_model )
        print ( "Done loading a JSON file" )
    else:
        # Open as a pickled format file
        print ( "Opening a Pickle file" )
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


def write_dm_str_val ( dm, f, dm_name, mdl_name, blank_default="", indent="" ):
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

def write_mdl ( dm, file_name ):
    """ Write a data model to a named file (generally follows "export_mcell_mdl" ordering) """
    f = open ( file_name, 'w' )
    # f.write ( "/* MDL Generated from Data Model */\n" )
    if ('mcell' in dm):
      mcell = dm['mcell']
      if 'parameter_system' in mcell:
        ps = mcell['parameter_system']
        write_parameter_system ( ps, f )
      if 'initialization' in mcell:
        init = mcell['initialization']
        write_initialization ( init, f )
        if 'partitions' in init:
          parts = mcell['initialization']['partitions']
          write_partitions ( parts, f )
      if 'define_molecules' in mcell:
        mols = mcell['define_molecules']
        write_molecules ( mols, f )
      if 'define_surface_classes' in mcell:
        sclasses = mcell['define_surface_classes']
        write_surface_classes ( sclasses, f )
      if 'define_reactions' in mcell:
        reacts = mcell['define_reactions']
        write_reactions ( reacts, f )
      if 'geometrical_objects' in mcell:
        geom = mcell['geometrical_objects']
        write_geometry ( geom, f )
      if 'modify_surface_regions' in mcell:
        modsurfrs = mcell['modify_surface_regions']
        write_modify_surf_regions ( modsurfrs, f )
      if 'define_release_patterns' in mcell:
        pats = mcell['define_release_patterns']
        write_release_patterns ( pats, f )
      if ('geometrical_objects' in mcell) or ('release_sites' in mcell):
        geom = None
        rels = None
        if 'geometrical_objects' in mcell:
          geom = mcell['geometrical_objects']
        if 'release_sites' in mcell:
          rels = mcell['release_sites']
        write_instances ( geom, rels, mcell['define_molecules'], f )

      f.write("sprintf(seed,\"%05g\",SEED)\n\n")

      if 'viz_output' in mcell:
        vizout = mcell['viz_output']
        mols = None
        if ('define_molecules' in mcell):
          mols = mcell['define_molecules']
        write_viz_out ( vizout, mols, f )

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
        write_react_out ( reactout, mols, time_step, f )

    f.close()


def write_parameter_system ( ps, f ):
    if 'model_parameters' in ps:
      mplist = ps['model_parameters']
      if len(mplist) > 0:
        f.write ( "/* DEFINE PARAMETERS */\n" );

        for p in mplist:

          # Write the name = val portion of the definition
          if True:
            f.write ( p['par_name'] + " = " +              p['par_expression'] )
          else:
            f.write ( p['par_name'] + " = " + "%.15g"%(p['extras']['par_value']) )

          # Write the optional description and units in a comment (if non empty)
          if (len(p['par_description']) > 0) or (len(p['par_units']) > 0):
            f.write ( "    /* " + p['par_description'] + " " + p['par_units'] + " */\n" )
          else:
            f.write ( "\n" )
            
        f.write ( "\n" );


def write_initialization ( init, f ):
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
        f.write ( "PARTITION_X = [[%s TO %s STEP %s]]\n" % ( parts['x_start'], parts['x_end'], parts['x_step'] ) )
        f.write ( "PARTITION_Y = [[%s TO %s STEP %s]]\n" % ( parts['y_start'], parts['y_end'], parts['y_step'] ) )
        f.write ( "PARTITION_Z = [[%s TO %s STEP %s]]\n" % ( parts['z_start'], parts['z_end'], parts['z_step'] ) )
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


def write_geometry ( geom, f ):
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


def write_instances ( geom, rels, mols, f ):
    #TODO Note that the use of "Scene" here is a temporary measure!!!!
    f.write ( "INSTANTIATE Scene OBJECT\n" )
    f.write ( "{\n" )
    if geom != None:
      if 'object_list' in geom:
        glist = geom['object_list']
        if len(glist) > 0:
          for g in glist:
            f.write ( "  %s OBJECT %s {}\n" % (g['name'], g['name']) )
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
              f.write("   SHAPE = Scene.%s\n" % (r['object_expr']))

            # Next handle the molecule to be released (maybe the Molecule List should have been a dictionary keyed on mol_name?)
            mlist = mols['molecule_list']
            mol = None
            for m in mlist:
              if m['mol_name'] == r['molecule']:
                mol = m
                break

            if mol:
              if mol['mol_type'] == '2D':
                f.write("   MOLECULE = %s%s\n" % (r['molecule'],r['orient']))
              else:
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


def write_viz_out ( vizout, mols, f ):

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


def write_react_out ( rout, mols, time_step, f ):

    if ("reaction_output_list" in rout) and (len(rout["reaction_output_list"]) > 0):
        context_scene_name = "Scene"

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

