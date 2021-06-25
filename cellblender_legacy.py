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


# ############
#
#  Property Groups
#   CellBlender consists primarily of Property Groups which are the
#   classes which are templates for objects.
#
#   Each Property Group must implement the following functions:
#
#     init_properties - Deletes old and Creates a new object including children
#     build_data_model_from_properties - Builds a Data Model Dictionary from the existing properties
#     @staticmethod upgrade_data_model - Produces a current data model from an older version
#     build_properties_from_data_model - Calls init_properties and builds properties from a data model
#     check_properties_after_building - Used to resolve dependencies
#     
#
# ############


# <pep8 compliant>


"""
This script contains the custom properties used in CellBlender.
"""
# blender imports
import bpy

from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
    FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty, PointerProperty, StringProperty, BoolVectorProperty

from bpy.app.handlers import persistent

import cellblender


from . import cellblender_preferences
from . import cellblender_project
from . import cellblender_initialization
from . import cellblender_objects
from . import cellblender_molecules
from . import cellblender_reactions
from . import cellblender_release
from . import cellblender_surface_classes
from . import cellblender_partitions
from . import cellblender_simulation
from . import cellblender_mol_viz
from . import cellblender_reaction_output
from . import cellblender_meshalyzer
from . import parameter_system
from . import data_model



# python imports
import os


class MCELL_OT_upgradeRC3(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.upgraderc3"
    bl_label = "Upgrade RC3/4 Blend File"
    bl_description = "Upgrade the data from an RC3/4 version of CellBlender"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Upgrade RC3 Operator called" )
        data_model.upgrade_RC3_properties_from_data_model ( context )
        return {'FINISHED'}




class MCellLegacyGroup(bpy.types.PropertyGroup):

    #########       ########       ########
    ##      ##     ##      ##     ##      ##
    ##      ##     ##                     ##
    ##      ##     ##                     ##
    #########      ##                 ####
    ##     ##      ##                     ##
    ##      ##     ##                     ##
    ##      ##     ##      ##     ##      ##
    ##      ##      ########       ########


    #################### Special RC3 Code Below ####################

    def RC3_add_from_ID_panel_parameter ( self, dm_dict, dm_name, prop_dict, prop_name, panel_param_list ):
        dm_dict[dm_name] = [ x for x in panel_param_list if x['name'] == prop_dict[prop_name]['unique_static_name'] ] [0] ['expr']

    def RC3_add_from_ID_string ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = prop_dict[prop_name]
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_float ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = prop_dict[prop_name]
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_int ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = prop_dict[prop_name]
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_floatstr ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = str(prop_dict[prop_name])
        else:
          dm_dict[dm_name] = str(default_value)

    def RC3_add_from_ID_boolean ( self, dm_dict, dm_name, prop_dict, prop_name, default_value ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = ( prop_dict[prop_name] != 0 )
        else:
          dm_dict[dm_name] = default_value

    def RC3_add_from_ID_enum ( self, dm_dict, dm_name, prop_dict, prop_name, default_value, enum_list ):
        if prop_dict.get(prop_name):
          dm_dict[dm_name] = enum_list[int(prop_dict[prop_name])]
        else:
          dm_dict[dm_name] = default_value

    def build_data_model_from_RC3_ID_properties ( self, context, geometry=False ):
        # Build an unversioned data model from RC3 ID properties to match the pre-versioned data models that can be upgraded to versioned data models

        print ( "build_data_model_from_RC3_ID_properties: Constructing a data_model dictionary from RC3 ID properties" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!! THIS MAY NOT WORK YET !!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )
        print ( "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" )

        dm = None

        # Remove the RNA properties overlaying the ID Property 'mcell'
        del bpy.types.Scene.mcell
        
        mcell = context.scene.get('mcell')
        if mcell != None:

          # There's an mcell in the scene
          dm = {}
          

          # Build the parameter system first
          par_sys = mcell.get('parameter_system')
          if par_sys != None:
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There's a parameter system" )
            # There's a parameter system
            dm['parameter_system'] = {}
            dm_ps = dm['parameter_system']
            gpl = par_sys.get('general_parameter_list')
            if gpl != None:
              dm_ps['model_parameters'] = []
              dm_mp = dm_ps['model_parameters']
              if len(gpl) > 0:
                for gp in gpl:
                  print ( "Par name = " + str(gp['par_name']) )
                  dm_p = {}
                  dm_p['par_name'] = str(gp['par_name'])
                  dm_p['par_expression'] = str(gp['expr'])
                  dm_p['par_description'] = str(gp['descr'])
                  dm_p['par_units'] = str(gp['units'])
                  extras = {}
                  extras['par_id_name'] = str(gp['name'])
                  extras['par_valid'] = gp['isvalid'] != 0
                  extras['par_value'] = gp['value']
                  dm_p['extras'] = extras
                  dm_mp.append ( dm_p )

            print ( "Done parameter system" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )

          ppl = par_sys.get('panel_parameter_list')
          

          # Build the rest of the data model

          # Initialization

          init = mcell.get('initialization')
          if init != None:
            # dm['initialization'] = mcell.initialization.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is initialization" )

            # There is initialization
            dm['initialization'] = {}
            dm_init = dm['initialization']

            self.RC3_add_from_ID_panel_parameter ( dm_init, 'iterations',              init, 'iterations', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'time_step',               init, 'time_step',  ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'time_step_max',           init, 'time_step_max', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'space_step',              init, 'space_step', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'interaction_radius',      init, 'interaction_radius', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'radial_directions',       init, 'radial_directions', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'radial_subdivisions',     init, 'radial_subdivisions', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'vacancy_search_distance', init, 'vacancy_search_distance', ppl )
            self.RC3_add_from_ID_panel_parameter ( dm_init, 'surface_grid_density',    init, 'surface_grid_density', ppl )

            self.RC3_add_from_ID_boolean ( dm_init, 'accurate_3d_reactions',     init, 'accurate_3d_reactions', True )
            self.RC3_add_from_ID_boolean ( dm_init, 'center_molecules_on_grid',  init, 'center_molecules_grid', False )


            if init.get('microscopic_reversibility'):
              dm_init['microscopic_reversibility'] = init['microscopic_reversibility']
            else:
              dm_init['microscopic_reversibility'] = 'OFF'

            # Notifications

            dm_init['notifications'] = {}
            dm_note = dm_init['notifications']
            if init.get('all_notifications'):
              dm_note['all_notifications'] = init['all_notifications']
            else:
              dm_note['all_notifications'] = 'INDIVIDUAL'

            if init.get('diffusion_constant_report'):
              dm_note['diffusion_constant_report'] = init['diffusion_constant_report']
            else:
              dm_note['diffusion_constant_report'] = 'BRIEF'

            if init.get('file_output_report'):
              dm_note['file_output_report'] = init['file_output_report'] != 0
            else:
              dm_note['file_output_report'] = False

            if init.get('final_summary'):
              dm_note['final_summary'] = init['final_summary'] != 0
            else:
              dm_note['final_summary'] = True

            if init.get('iteration_report'):
              dm_note['iteration_report'] = init['iteration_report'] != 0
            else:
              dm_note['iteration_report'] = True

            if init.get('partition_location_report'):
              dm_note['partition_location_report'] = init['partition_location_report'] != 0
            else:
              dm_note['partition_location_report'] = False

            if init.get('probability_report'):
              dm_note['probability_report'] = init['probability_report']
            else:
              dm_note['probability_report'] = 'ON'

            if init.get('probability_report_threshold'):
              dm_note['probability_report_threshold'] = init['probability_report_threshold']
            else:
              dm_note['probability_report_threshold'] = 0.0


            if init.get('varying_probability_report'):
              dm_note['varying_probability_report'] = init['varying_probability_report'] != 0
            else:
              dm_note['varying_probability_report'] = True

            if init.get('progress_report'):
              dm_note['progress_report'] = init['progress_report'] != 0
            else:
              dm_note['progress_report'] = True

            if init.get('release_event_report'):
              dm_note['release_event_report'] = init['release_event_report'] != 0
            else:
              dm_note['release_event_report'] = True

            if init.get('molecule_collision_report'):
              dm_note['molecule_collision_report'] = init['molecule_collision_report'] != 0
            else:
              dm_note['molecule_collision_report'] = False


            # Warnings

            dm_init['warnings'] = {}
            dm_warn = dm_init['warnings']

            if init.get('all_warnings'):
              dm_warn['all_warnings'] = init['all_warnings']
            else:
              dm_warn['all_warnings'] = 'INDIVIDUAL'

            if init.get('degenerate_polygons'):
              dm_warn['degenerate_polygons'] = init['degenerate_polygons']
            else:
              dm_warn['degenerate_polygons'] = 'WARNING'

            if init.get('high_reaction_probability'):
              dm_warn['high_reaction_probability'] = init['high_reaction_probability']
            else:
              dm_warn['high_reaction_probability'] = 'IGNORED'

            if init.get('high_probability_threshold'):
              dm_warn['high_probability_threshold'] = init['high_probability_threshold']
            else:
              dm_warn['high_probability_threshold'] = 1.0

            if init.get('lifetime_too_short'):
              dm_warn['lifetime_too_short'] = init['lifetime_too_short']
            else:
              dm_warn['lifetime_too_short'] = 'WARNING'

            if init.get('lifetime_threshold'):
              dm_warn['lifetime_threshold'] = init['lifetime_threshold']
            else:
              dm_warn['lifetime_threshold'] = 50

            if init.get('missed_reactions'):
              dm_warn['missed_reactions'] = init['missed_reactions']
            else:
              dm_warn['missed_reactions'] = 'WARNING'

            if init.get('missed_reaction_threshold'):
              dm_warn['missed_reaction_threshold'] = init['missed_reaction_threshold']
            else:
              dm_warn['missed_reaction_threshold'] = 0.001

            if init.get('negative_diffusion_constant'):
              dm_warn['negative_diffusion_constant'] = init['negative_diffusion_constant']
            else:
              dm_warn['negative_diffusion_constant'] = 'WARNING'

            if init.get('missing_surface_orientation'):
              dm_warn['missing_surface_orientation'] = init['missing_surface_orientation']
            else:
              dm_warn['missing_surface_orientation'] = 'ERROR'

            if init.get('negative_reaction_rate'):
              dm_warn['negative_reaction_rate'] = init['negative_reaction_rate']
            else:
              dm_warn['negative_reaction_rate'] = 'WARNING'

            if init.get('useless_volume_orientation'):
              dm_warn['useless_volume_orientation'] = init['useless_volume_orientation']
            else:
              dm_warn['useless_volume_orientation'] = 'WARNING'

            print ( "Done initialization" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )

          # Partitions

          parts = mcell.get('partitions')
          if parts != None:

            # dm['initialization']['partitions'] = mcell.partitions.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are partitions" )
            # There are partitions
            
            # Ensure that there is an initialization section in the data model that's being built
            dm_init = dm.get('initialization')
            if dm_init == None:
              dm['initialization'] = {}
              dm_init = dm['initialization']
            
            dm['initialization']['partitions'] = {}
            dm_parts = dm['initialization']['partitions']

            if parts.get('include'):
              dm_parts['include'] = ( parts['include'] != 0 )
            else:
              dm_parts['include'] = False

            if parts.get('recursion_flag'):
              dm_parts['recursion_flag'] = ( parts['recursion_flag'] != 0 )
            else:
              dm_parts['recursion_flag'] = False

            if parts.get('x_start'):
              dm_parts['x_start'] = parts['x_start']
            else:
              dm_parts['x_start'] = -1

            if parts.get('x_end'):
              dm_parts['x_end'] = parts['x_end']
            else:
              dm_parts['x_end'] = 1

            if parts.get('x_step'):
              dm_parts['x_step'] = parts['x_step']
            else:
              dm_parts['x_step'] = 0.02

            if parts.get('y_start'):
              dm_parts['y_start'] = parts['y_start']
            else:
              dm_parts['y_start'] = -1

            if parts.get('y_end'):
              dm_parts['y_end'] = parts['y_end']
            else:
              dm_parts['y_end'] = 1

            if parts.get('y_step'):
              dm_parts['y_step'] = parts['y_step']
            else:
              dm_parts['y_step'] = 0.02

            if parts.get('z_start'):
              dm_parts['z_start'] = parts['z_start']
            else:
              dm_parts['z_start'] = -1

            if parts.get('z_end'):
              dm_parts['z_end'] = parts['z_end']
            else:
              dm_parts['z_end'] = 1

            if parts.get('z_step'):
              dm_parts['z_step'] = parts['z_step']
            else:
              dm_parts['z_step'] = 0.02

            print ( "Done partitions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Model Objects

          modobjs = mcell.get('model_objects')
          if modobjs != None:
            # dm['model_objects'] = mcell.model_objects.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are model objects" )
            # There are model objects
            dm['model_objects'] = {}
            dm_mo = dm['model_objects']
            mol = modobjs.get('object_list')
            if mol != None:
              print ( "There is a model_object_list" )
              dm_mo['model_object_list'] = []
              dm_ol = dm_mo['model_object_list']
              if len(mol) > 0:
                for o in mol:
                  print ( "Model Object name = " + str(o['name']) )
                  
                  dm_o = {}
                  
                  self.RC3_add_from_ID_string ( dm_o, 'name', o, 'name', "Object" )

                  dm_ol.append ( dm_o )

            print ( "Done model objects" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Molecules

          mols = mcell.get('molecules')
          if mols != None:
            # dm['define_molecules'] = mcell.molecules.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are molecules" )
            # There are molecules
            dm['define_molecules'] = {}
            dm_mols = dm['define_molecules']
            ml = mols.get('molecule_list')
            if ml != None:
              dm_mols['molecule_list'] = []
              dm_ml = dm_mols['molecule_list']
              if len(ml) > 0:
                for m in ml:
                  print ( "Mol name = " + str(m['name']) )

                  dm_m = {}

                  self.RC3_add_from_ID_string          ( dm_m, 'mol_name',           m, 'name',               "Molecule" )
                  self.RC3_add_from_ID_enum            ( dm_m, 'mol_type',           m, 'type',               "2D",      ["2D", "3D"] )
                  self.RC3_add_from_ID_boolean         ( dm_m, 'target_only',        m, 'target_only',        False )
                  self.RC3_add_from_ID_boolean         ( dm_m, 'export_viz',         m, 'export_viz',         False )
                  self.RC3_add_from_ID_panel_parameter ( dm_m, 'diffusion_constant', m, 'diffusion_constant', ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_m, 'custom_space_step',  m, 'custom_space_step',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_m, 'custom_time_step',   m, 'custom_time_step',   ppl )
                  dm_m['maximum_step_length'] = ""

                  dm_ml.append ( dm_m )

            print ( "Done molecules" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Reactions

          reacts = mcell.get('reactions')
          if reacts != None:
            # dm['define_reactions'] = mcell.reactions.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are reactions" )
            # There are reactions
            dm['define_reactions'] = {}
            dm_reacts = dm['define_reactions']
            rl = reacts.get('reaction_list')
            if rl != None:
              dm_reacts['reaction_list'] = []
              dm_rl = dm_reacts['reaction_list']
              if len(rl) > 0:
                for r in rl:
                  print ( "React name = " + str(r['name']) )
                  
                  dm_r = {}
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'name',      r, 'name',      "The Reaction" )
                  self.RC3_add_from_ID_string  ( dm_r, 'rxn_name',  r, 'rxn_name',  "" )
                  self.RC3_add_from_ID_string  ( dm_r, 'reactants', r, 'reactants', "" )
                  self.RC3_add_from_ID_string  ( dm_r, 'products',  r, 'products',  "" )

                  self.RC3_add_from_ID_enum    ( dm_r, 'rxn_type',  r, 'type', "irreversible", ["irreversible", "reversible"] )

                  self.RC3_add_from_ID_boolean ( dm_r, 'variable_rate_switch', r, 'variable_rate_switch', False )
                  self.RC3_add_from_ID_string  ( dm_r, 'variable_rate',        r, 'variable_rate',        "" )
                  self.RC3_add_from_ID_boolean ( dm_r, 'variable_rate_valid',  r, 'variable_rate_valid',  False )

                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'fwd_rate',  r, 'fwd_rate',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'bkwd_rate', r, 'bkwd_rate', ppl )

                  dm_rl.append ( dm_r )

            print ( "Done reactions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Release Sites

          rels = mcell.get('release_sites')
          if rels != None:
            # dm['release_sites'] = mcell.release_sites.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are release sites" )
            # There are release sites
            dm['release_sites'] = {}
            dm_rel = dm['release_sites']
            rsl = rels.get('mol_release_list')
            if rsl != None:
              print ( "There is a mol_release_list" )
              dm_rel['release_site_list'] = []
              dm_rs = dm_rel['release_site_list']
              if len(rsl) > 0:
                for r in rsl:
                  print ( "Release Site name = " + str(r['name']) )
                  
                  dm_r = {}
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'name',     r, 'name',     "Release_Site" )
                  self.RC3_add_from_ID_string  ( dm_r, 'molecule', r, 'molecule', "" )
                  self.RC3_add_from_ID_enum    ( dm_r, 'shape',    r, 'shape',    "CUBIC", ["CUBIC", "SPHERICAL", "SPHERICAL_SHELL", "OBJECT"] )
                  self.RC3_add_from_ID_enum    ( dm_r, 'orient',   r, 'orient',   "\'",    ["\'", ",", ";"] )
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'object_expr', r, 'object_expr', "" )
                  
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'location_x',  r, 'location_x',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'location_y',  r, 'location_y',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'location_z',  r, 'location_z',  ppl )

                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'site_diameter',        r, 'diameter',     ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'release_probability',  r, 'probability',  ppl )

                  self.RC3_add_from_ID_enum    ( dm_r, 'quantity_type', r, 'quantity_type', "NUMBER_TO_RELEASE", ["NUMBER_TO_RELEASE", "GAUSSIAN_RELEASE_NUMBER", "DENSITY"] )

                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'quantity', r, 'quantity',  ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'stddev',   r, 'stddev',  ppl )

                  self.RC3_add_from_ID_string  ( dm_r, 'pattern', r, 'pattern', "" )

                  dm_rs.append ( dm_r )

            print ( "Done release sites" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Release Patterns

          relps = mcell.get('release_patterns')
          if relps != None:
            # dm['define_release_patterns'] = mcell.release_patterns.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are release patterns" )
            # There are release patterns
            dm['define_release_patterns'] = {}
            dm_relps = dm['define_release_patterns']
            rpl = relps.get('release_pattern_list')
            if rpl != None:
              print ( "There is a release_pattern_list" )
              dm_relps['release_pattern_list'] = []
              dm_rpl = dm_relps['release_pattern_list']
              if len(rpl) > 0:
                for r in rpl:
                  print ( "Release Pattern name = " + str(r['name']) )
                  
                  dm_r = {}
                  
                  self.RC3_add_from_ID_string  ( dm_r, 'name',     r, 'name',     "Release_Pattern" )
                  
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'delay',            r, 'delay',            ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'release_interval', r, 'release_interval', ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'train_duration',   r, 'train_duration',   ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'train_interval',   r, 'train_interval',   ppl )
                  self.RC3_add_from_ID_panel_parameter ( dm_r, 'number_of_trains', r, 'number_of_trains', ppl )

                  dm_rpl.append ( dm_r )

            print ( "Done release patterns" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Surface Class Definitions

          surfcs = mcell.get('surface_classes')
          if surfcs != None:
            # dm['define_surface_classes'] = mcell.surface_classes.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are surface class definitions" )
            # There are surface classes
            print ( "surfcs.keys() = " + str(surfcs.keys()) )
            dm['define_surface_classes'] = {}
            dm_surfcs = dm['define_surface_classes']
            scl = surfcs.get('surf_class_list')
            if scl != None:
              print ( "There is a surf_class_list" )
              dm_surfcs['surface_class_list'] = []
              dm_scl = dm_surfcs['surface_class_list']
              print ( "The surf_class_list has " + str(len(scl)) + " surface classes" )
              if len(scl) > 0:
                for sc in scl:
                  print ( "  Surface Class Name = " + str(sc['name']) )
                  dm_sc = {}
                  if 'name' in sc:
                    dm_sc['name'] = sc['name']
                  dm_sc['surface_class_prop_list'] = []
                  dm_scpl = dm_sc['surface_class_prop_list']
                  if 'surf_class_props_list' in sc:
                    scpl = sc.get('surf_class_props_list')
                    for scp in scpl:
                      print ( "    Surface Class Property Name = " + str(scp['name']) )
                      dm_scp = {}
                      self.RC3_add_from_ID_string   ( dm_scp, 'name',     scp, 'name',     "Surf_Class_Property" )
                      self.RC3_add_from_ID_string   ( dm_scp, 'molecule', scp, 'molecule', "" )
                      
                      self.RC3_add_from_ID_enum     ( dm_scp, 'surf_class_orient', scp, 'surf_class_orient', "\'", ['\'', ',', ';'] )
                      self.RC3_add_from_ID_enum     ( dm_scp, 'surf_class_type',   scp, 'surf_class_type',   "ABSORPTIVE", ['ABSORPTIVE', 'TRANSPARENT', 'REFLECTIVE', 'CLAMP_CONCENTRATION'] )
                      
                      self.RC3_add_from_ID_floatstr ( dm_scp, 'clamp_value',       scp, 'clamp_value', "" )
                      
                      dm_scpl.append ( dm_scp )

                  dm_scl.append ( dm_sc )

            print ( "Done surface class definitions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Surface Region Definitions

          modsrs = mcell.get('mod_surf_regions')
          if modsrs != None:
            # dm['modify_surface_regions'] = mcell.mod_surf_regions.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There are surface regions" )
            # There are surface regions
            print ( "modsrs.keys() = " + str(modsrs.keys()) )
            dm['modify_surface_regions'] = {}
            dm_modsrs = dm['modify_surface_regions']
            msrl = modsrs.get('mod_surf_regions_list')
            if msrl != None:
              print ( "There is a mod_surf_regions_list" )
              dm_modsrs['modify_surface_regions_list'] = []
              dm_msrl = dm_modsrs['modify_surface_regions_list']
              if len(msrl) > 0:
                print ( "The mod_surf_regions_list has " + str(len(msrl)) + " regions" )
                for msr in msrl:
                  print ( " Modify Region Name = " + str(msr['name']) )
                  print ( "   Surf Class Name = " + str(msr['surf_class_name']) )
                  print ( "   Object Name = " + str(msr['object_name']) )
                  print ( "   Region Name = " + str(msr['region_name']) )
                  
                  dm_msr = {}

                  self.RC3_add_from_ID_string ( dm_msr, 'name',     msr, 'name',     "" )
                  self.RC3_add_from_ID_string ( dm_msr, 'surf_class_name', msr, 'surf_class_name', "" )
                  self.RC3_add_from_ID_string ( dm_msr, 'object_name', msr, 'object_name', "" )
                  self.RC3_add_from_ID_string ( dm_msr, 'region_name', msr, 'region_name', "" )

                  dm_msrl.append ( dm_msr )

            print ( "Done surface regions" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Visualization Output

          vizout = mcell.get('viz_output')
          if vizout != None:
            # dm['viz_output'] = mcell.viz_output.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is viz output" )
            # There is viz output
            dm['viz_output'] = {}
            dm_viz = dm['viz_output']
            self.RC3_add_from_ID_boolean ( dm_viz, 'all_iterations', vizout, 'all_iterations', True )
            self.RC3_add_from_ID_int     ( dm_viz, 'start',          vizout, 'start',          0 )
            self.RC3_add_from_ID_int     ( dm_viz, 'end',            vizout, 'end',            1 )
            self.RC3_add_from_ID_int     ( dm_viz, 'step',           vizout, 'step',           1 )
            self.RC3_add_from_ID_boolean ( dm_viz, 'export_all',     vizout, 'export_all',     False )
            print ( "Done viz output" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Reaction Output

          rxnout = mcell.get('rxn_output')
          if rxnout != None:
            # dm['reaction_data_output'] = mcell.rxn_output.build_data_model_from_properties(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is reaction output" )
            # There is reaction output
            dm['reaction_data_output'] = {}
            dm_rxnout = dm['reaction_data_output']

            self.RC3_add_from_ID_boolean ( dm_rxnout, 'combine_seeds', rxnout, 'combine_seeds', True )
            self.RC3_add_from_ID_boolean ( dm_rxnout, 'mol_colors',    rxnout, 'mol_colors',    False )
            self.RC3_add_from_ID_enum    ( dm_rxnout, 'plot_layout',   rxnout, 'plot_layout',   " plot ", [' page ', ' plot ', ' '] )
            self.RC3_add_from_ID_enum    ( dm_rxnout, 'plot_legend',   rxnout, 'plot_legend',   "0", ['x', '0', '1', '2', '3', '4', '6', '7', '8', '9', '10'] )


            print ( "rxnout.keys() = " + str(rxnout.keys()) )
            rxnl = rxnout.get('rxn_output_list')
            if rxnl != None:
              print ( "There is a rxn_output_list" )
              dm_rxnout['reaction_output_list'] = []
              dm_rxnl = dm_rxnout['reaction_output_list']
              if len(rxnl) > 0:
                print ( "The reaction_output_list has " + str(len(rxnl)) + " entries" )
                for rxn in rxnl:
                  dm_rxn = {}

                  self.RC3_add_from_ID_string ( dm_rxn, 'name',            rxn, 'name',            "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'molecule_name',   rxn, 'molecule_name',   "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'reaction_name',   rxn, 'reaction_name',   "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'object_name',     rxn, 'object_name',     "" )
                  self.RC3_add_from_ID_string ( dm_rxn, 'region_name',     rxn, 'region_name',     "" )
                  self.RC3_add_from_ID_enum   ( dm_rxn, 'count_location',  rxn, 'count_location',  "World",    ['World', 'Object', 'Region'] )
                  self.RC3_add_from_ID_enum   ( dm_rxn, 'rxn_or_mol',      rxn, 'rxn_or_mol',      "Molecule", ['Reaction', 'Molecule', 'MDLString'] )

                  dm_rxnl.append ( dm_rxn )

            print ( "Done reaction output" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )


          # Viz Data


            """ Use this as a template for mol_viz data

            def build_data_model_from_properties ( self, context ):
                print ( "Building Mol Viz data model from properties" )
                mv_dm = {}
                mv_dm['data_model_version'] = "DM_2015_04_13_1700"

                mv_seed_list = []
                for s in self.mol_viz_seed_list:
                    mv_seed_list.append ( str(s.name) )
                mv_dm['seed_list'] = mv_seed_list

                mv_dm['active_seed_index'] = self.active_mol_viz_seed_index
                mv_dm['file_dir'] = self.mol_file_dir

                mv_file_list = []
                for s in self.mol_file_list:
                    mv_file_list.append ( str(s.name) )
                mv_dm['file_list'] = mv_file_list

                mv_dm['file_num'] = self.mol_file_num
                mv_dm['file_name'] = self.mol_file_name
                mv_dm['file_index'] = self.mol_file_index
                mv_dm['file_start_index'] = self.mol_file_start_index
                mv_dm['file_stop_index'] = self.mol_file_stop_index
                mv_dm['file_step_index'] = self.mol_file_step_index

                mv_viz_list = []
                for s in self.mol_viz_list:
                    mv_viz_list.append ( str(s.name) )
                mv_dm['viz_list'] = mv_viz_list

                mv_dm['render_and_save'] = self.render_and_save
                mv_dm['viz_enable'] = self.mol_viz_enable

                mv_color_list = []
                for c in self.color_list:
                    mv_color = []
                    for i in c.vec:
                        mv_color.append ( i )
                    mv_color_list.append ( mv_color )
                mv_dm['color_list'] = mv_color_list

                mv_dm['color_index'] = self.color_index
                mv_dm['manual_select_viz_dir'] = self.manual_select_viz_dir

                return mv_dm
            """





          """
          geom = mcell.get('geometrical_objects')
          if geom != None:
            # dm['geometrical_objects'] = self.model_objects.build_data_model_geometry_from_mesh(context)
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "There is viz output" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            # There is viz output
          if geometry:
            print ( "Adding Geometry to Data Model" )
            
            dm['materials'] = self.model_objects.build_data_model_materials_from_materials(context)
          """

        # We don't need the geometry in the data model for an RC3 upgrade since the geometry is already in the .blend file.

        #print ( "Adding Geometry to Data Model" )
        #dm['geometrical_objects'] = mcell.model_objects.build_data_model_geometry_from_mesh(context)
        #dm['materials'] = mcell.model_objects.build_data_model_materials_from_materials(context)
        ## cellblender.data_model.save_data_model_to_file ( dm, "Upgraded_Data_Model.txt" )
        #print ( "Removing Geometry from Data Model" )
        #dm.pop('geometrical_objects')
        #dm.pop('materials')

        #self.print_id_property_tree ( context.scene['mcell'], 'mcell', 0 )

        # Restore the RNA properties overlaying the ID Property 'mcell'
        bpy.types.Scene.mcell: PointerProperty(type=cellblender.cellblender_main.MCellPropertyGroup)

        return dm


classes = ( 
            MCELL_OT_upgradeRC3,
            MCellLegacyGroup,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

