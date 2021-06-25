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
    FloatProperty, FloatVectorProperty, IntProperty, \
    IntVectorProperty, PointerProperty, StringProperty, BoolVectorProperty

from bpy.app.handlers import persistent

import cellblender

from . import cellblender_examples
from . import cellblender_preferences
from . import cellblender_project
from . import cellblender_initialization
from . import cellblender_objects
from . import cellblender_molecules
from . import cellblender_molmaker
from . import cellblender_reactions
from . import cellblender_release
from . import cellblender_surface_classes
from . import cellblender_surface_regions
from . import cellblender_partitions
from . import cellblender_pbc
from . import cellblender_simulation
from . import cellblender_mol_viz
from . import cellblender_reaction_output
from . import cellblender_meshalyzer
from . import cellblender_scripting
from . import parameter_system
from . import data_model

from . import cellblender_legacy

# python imports
import os



# Two callbacks that had been in the cellblender operators file:

from . import cellblender_utils
#from cellblender.cellblender_utils import mcell_files_path
from cellblender.cellblender_utils import mcell_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl

@persistent
def mcell_valid_update(context):
    """ Check whether the mcell executable in the .blend file is valid """
    print ( "load post handler: cellblender_main.mcell_valid_update() called" )
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    binary_path = mcell.cellblender_preferences.mcell_binary
    mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )
    # print ( "mcell_binary_valid = ", mcell.cellblender_preferences.mcell_binary_valid )


@persistent
def init_properties(context):
    """ Initialize MCell properties if not already initialized """
    print ( "load post handler: cellblender_main.init_properties() called" )
    if not context:
        context = bpy.context
    mcell = context.scene.mcell
    if not mcell.initialized:
        mcell.init_properties(context)
        mcell.initialized = True




#Custom Properties

'''
# Uneeded?
class MCellStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name: StringProperty(name="Text")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell String Property with name \"" + self.name + "\" ... no collections to remove." )
        pass


class MCellFloatVectorProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold float vector for a CollectionProperty """
    vec: FloatVectorProperty(name="Float Vector")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell Float Vector Property... no collections to remove. Is there anything special do to for Vectors?" )
        pass
'''



# from . import parameter_system


import mathutils


####
##
##  REFACTORING NOTE: Almost all of the following code is at the "application" level and will probably stay in cellblender_main.
##
####



import cellblender



class MCellObjectSelectorPropertyGroup(bpy.types.PropertyGroup):
    filter: StringProperty(
        name="Object Name Filter",
        description="Enter a regular expression for object names.")

    def remove_properties ( self, context ):
        print ( "Removing all Object Selector Properties... no collections to remove." )




class PP_OT_init_mcell(bpy.types.Operator):
    bl_idname = "mcell.init_cellblender"
    bl_label = "Init CellBlender"
    bl_description = "Initialize CellBlender"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print ( "Initializing CellBlender" )
        mcell = context.scene.mcell
        mcell.init_properties(context)
        mcell.rxn_output.init_properties(mcell.parameter_system)
        print ( "CellBlender has been initialized" )
        return {'FINISHED'}




# My panel class (which happens to augment 'Scene' properties)
class MCELL_PT_main_panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_CellBlender"
    bl_label = "  CellBlender"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CellBlender"

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)


    def draw_header(self, context):
        # LOOK HERE!! This is where the icon is actually included in the panel layout!
        # The icon() method takes the image data-block in and returns an integer that
        # gets passed to the 'icon_value' argument of your label/prop constructor or
        # within a UIList subclass
        img = bpy.data.images.get('cellblender_icon')
        #could load multiple images and animate the icon too.
        #icons = [img for img in bpy.data.images if hasattr(img, "icon")]
        if img is not None:
            icon = self.layout.icon(img)
            self.layout.label(text="", icon_value=icon)

    def draw(self, context):
        context.scene.mcell.cellblender_main_panel.draw_self(context,self.layout)



# load_pre callback
@persistent
def report_load_pre(dummy):
    # Note that load_pre may not be called when the startup file is loaded for earlier versions of Blender (somewhere before 2.73)
    print ( "===================================================================================" )
    print ( "================================= Load Pre called =================================" )
    print ( "===================================================================================" )


# Load scene callback
@persistent
def scene_loaded(dummy):
    # Disable Scripting when the scene is loaded
    bpy.context.scene.mcell.run_simulation.enable_python_scripting = False

    # Icon
    #print("ADDON_ICON")
    icon_files = { 'cellblender_icon': 'cellblender_icon.png', 'mol_u': 'mol_unsel.png', 'mol_s': 'mol_sel.png', 'reaction_u': 'reactions_unsel.png', 'reaction_s': 'reactions_sel.png' }
    for icon_name in icon_files:
        fname = icon_files[icon_name]
        dirname = os.path.dirname(__file__)
        dirname = os.path.join(dirname,'icons')
        icon = bpy.data.images.get(icon_name)
        if icon is None:
            img = bpy.data.images.load(os.path.join(dirname, fname))
            img.name = icon_name
#            img.use_alpha = True
            img.user_clear() # Won't get saved into .blend files
        # remove scene_update handler
        elif "icon" not in icon.keys():
            icon["icon"] = True
            for f in bpy.app.handlers.depsgraph_update_pre:
                if f.__name__ == "scene_loaded":
                    print("Removing scene_loaded handler now that icons are loaded")
                    bpy.app.handlers.depsgraph_update_pre.remove(f)



class MCELL_OT_upgrade(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.upgrade"
    bl_label = "Upgrade Blend File"
    bl_description = "Upgrade the data from a previous version of CellBlender"
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Upgrade Operator called" )
        objstat = cellblender_objects.get_object_status(context)
        data_model.upgrade_properties_from_data_model ( context )
        bpy.ops.cbm.refresh_operator()
        cellblender_objects.restore_object_status(context, objstat)
        return {'FINISHED'}


class MCELL_OT_export_dm(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.export_data_model"
    bl_label = "Export Data Model to DM.txt"
    bl_description = "Export Data Model from ID Properties to a file."
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Export Data Model Operator called" )
        mcell = context.scene.mcell
        if 'data_model' in mcell.keys():
            # There is a data model present
            dm = data_model.unpickle_data_model(mcell['data_model'])
            # Build a full data model to get the geometry
            full_dm = mcell.build_data_model_from_properties ( context, geometry=True )
            # Add the geometry data to the original data model before exporting
            if 'geometrical_objects' in full_dm:
              dm['geometrical_objects'] = full_dm['geometrical_objects']
            if 'materials' in full_dm:
              dm['materials'] = full_dm['materials']
            data_model.save_data_model_to_file ( dm, "DM.txt" )
        return {'FINISHED'}


class MCELL_OT_export_dm_json(bpy.types.Operator):
    """This is the Upgrade operator called when the user presses the "Upgrade" button"""
    bl_idname = "mcell.export_data_model_json"
    bl_label = "Export Data Model to DM.json"
    bl_description = "Export Data Model from ID Properties to a JSON file."
    bl_options = {'REGISTER'}

    def execute(self, context):

        print ( "Export Data Model JSON Operator called" )
        mcell = context.scene.mcell
        if 'data_model' in mcell.keys():
            # There is a data model present
            dm = data_model.unpickle_data_model(mcell['data_model'])
            # Build a full data model to get the geometry
            full_dm = mcell.build_data_model_from_properties ( context, geometry=True )
            # Add the geometry data to the original data model before exporting
            if 'geometrical_objects' in full_dm:
              dm['geometrical_objects'] = full_dm['geometrical_objects']
            if 'materials' in full_dm:
              dm['materials'] = full_dm['materials']
            data_model.save_data_model_to_json_file ( dm, "DM.json" )
        return {'FINISHED'}


class MCELL_OT_delete(bpy.types.Operator):
    """This is the Delete operator called when the user presses the "Delete Properties" button"""
    bl_idname = "mcell.delete"
    bl_label = "Delete CellBlender Collection Properties"
    bl_description = "Delete CellBlender Collection Properties"
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Deleting CellBlender Collection Properties" )
        mcell = context.scene.mcell
        mcell.remove_properties(context)
        print ( "Finished Deleting CellBlender Collection Properties" )
        return {'FINISHED'}



class CBM_OT_refresh_operator(bpy.types.Operator):
    bl_idname = "cbm.refresh_operator"
    bl_label = "Refresh"
    bl_description = ("Refresh Molecules from Simulation")
    bl_options = {'REGISTER'}

    def execute(self, context):
        print ( "Refreshing/Reloading the Parameters, Molecules, and Geometry ..." )

        mcell = context.scene.mcell
        if cellblender.current_data_model == None:
            # Build the entire data model
            cellblender.current_data_model = { 'mcell': mcell.build_data_model_from_properties ( context ) }
        else:
            # Only refresh the parameters
            cellblender.current_data_model['mcell']['parameter_system'] = mcell.parameter_system.build_data_model_from_properties(context)

        bpy.ops.mcell.update_data_layout()
        mcell.model_objects.update_scene ( context.scene, force=True )
        bpy.ops.mcell.read_viz_data()
        return {'FINISHED'}



def select_callback ( self, context ):
    self.select_callback(context)


class CellBlenderMainPanelPropertyGroup(bpy.types.PropertyGroup):

    examples_select: BoolProperty ( name="example_sel", description="Examples", default=False, subtype='NONE', update=select_callback)
    preferences_select: BoolProperty ( name="pref_sel", description="Settings & Preferences", default=False, subtype='NONE', update=select_callback)
    #settings_select: BoolProperty ( name="set_sel", description="Project Settings", default=False, subtype='NONE', update=select_callback)
    scripting_select: BoolProperty ( name="set_mdl", description="Scripting", default=False, subtype='NONE', update=select_callback)
    parameters_select: BoolProperty ( name="par_sel", description="Model Parameters", default=False, subtype='NONE', update=select_callback)
    reaction_select: BoolProperty ( name="react_sel", description="Reactions", default=False, subtype='NONE', update=select_callback)
    molecule_select: BoolProperty ( name="mol_sel", description="Molecules", default=False, subtype='NONE', update=select_callback)
    placement_select: BoolProperty ( name="place_sel", description="Molecule Placement", default=False, subtype='NONE', update=select_callback)
    objects_select: BoolProperty ( name="obj_sel", description="Model Objects", default=False, subtype='NONE', update=select_callback)
    surf_classes_select: BoolProperty ( name="surfc_sel", description="Surface Classes", default=False, subtype='NONE', update=select_callback)
    surf_regions_select: BoolProperty ( name="surfr_sel", description="Assign Surface Classes", default=False, subtype='NONE', update=select_callback)
    rel_patterns_select: BoolProperty ( name="relpat_sel", description="Release Patterns", default=False, subtype='NONE', update=select_callback)
    partitions_select: BoolProperty ( name="part_sel", description="Partitions", default=False, subtype='NONE', update=select_callback)
    pbc_select: BoolProperty ( name="pbc_sel", description="Periodic Boundary Conditions", default=False, subtype='NONE', update=select_callback)
    init_select: BoolProperty ( name="init_sel", description="Run Simulation", default=False, subtype='NONE', update=select_callback)
    # run_select: BoolProperty ( name="run_sel", description="Old Run Simulation", default=False, subtype='NONE', update=select_callback)
    graph_select: BoolProperty ( name="graph_sel", description="Plot Output Settings", default=False, subtype='NONE', update=select_callback)
    mol_viz_select: BoolProperty ( name="mviz_sel", description="Visual Output Settings", default=False, subtype='NONE', update=select_callback)
    viz_select: BoolProperty ( name="viz_sel", description="Visual Output Settings", default=False, subtype='NONE', update=select_callback)
    reload_viz: BoolProperty ( name="reload", description="Reload Simulation Data", default=False, subtype='NONE', update=select_callback)

    select_multiple: BoolProperty ( name="multiple", description="Show Multiple Panels", default=False, subtype='NONE', update=select_callback)

    last_state: BoolVectorProperty ( size=22 ) # Keeps track of previous button state to detect transitions

    dummy_bool: BoolProperty( name="DummyBool", default=True )
    dummy_string: StringProperty( name="DummyString", default=" " )
    dummy_float: FloatProperty ( name="DummyFloat", default=12.34 )

    def remove_properties ( self, context ):
        print ( "Removing all CellBlender Main Panel Properties... no collections to remove." )


    def select_callback ( self, context ):
        """
        Desired Logic:
          pin_state 0->1 with no others selected:
            Show All
          pin_state 0->1 with just 1 selected:
            No Change (continue showing the currently selected, and allow more)
          pin_state 0->1 with more than 1 selected ... should NOT happen because only one panel should show when pin_state is 0
            Illegal state
          pin_state 1->0 :
            Hide all panels ... always

        """
        prop_keys = [ 'examples_select', 'preferences_select', 'scripting_select', 'parameters_select', 'reaction_select', 'molecule_select', 'placement_select', 'objects_select', 'surf_classes_select', 'surf_regions_select', 'rel_patterns_select', 'partitions_select', 'pbc_select', 'init_select', 'graph_select', 'viz_select', 'select_multiple' ]

        pin_state = False

        """
        try:
            pin_state = (self['select_multiple'] != 0)
        except:
            pass
        old_pin_state = (self.last_state[prop_keys.index('select_multiple')] != 0)
        """

        if self.get('select_multiple'):
            pin_state = (self['select_multiple'] != 0)
        old_pin_state = (self.last_state[prop_keys.index('select_multiple')] != 0)

        # print ( "Select Called without try/except with pin state:" + str(pin_state) + ", and old pin state = " + str(old_pin_state) )

        if (old_pin_state and (not pin_state)):
            # Pin has been removed, so hide all panels ... always
            # print ("Hiding all")
            for k in prop_keys:
                self.last_state[prop_keys.index(k)] = False
                self[k] = 0
                """
                try:
                    self.last_state[prop_keys.index(k)] = False
                    self[k] = 0
                except:
                    pass
                """
            self.last_state[prop_keys.index('select_multiple')] = False

        elif ((not old_pin_state) and pin_state):
            # Pin has been pushed
            # Find out how many panels are currently shown
            num_panels_shown = 0
            for k in prop_keys:
                if k != 'select_multiple':
                    if self.get(k):
                        if self[k] != 0:
                            num_panels_shown += 1
                    """
                    try:
                        if self[k] != 0:
                            num_panels_shown += 1
                    except:
                        pass
                    """
            # Check for case where no panels are showing
            if num_panels_shown == 0:
                # print ("Showing all")
                # Show all panels
                for k in prop_keys:
                    if self.get(k):
                        self[k] = 1
                        self.last_state[prop_keys.index(k)] = False
                    """
                    try:
                        self[k] = 1
                        self.last_state[prop_keys.index(k)] = False
                    except:
                        pass
                    """

            self.last_state[prop_keys.index('select_multiple')] = True

        else:
            # Pin state has not changed, so assume some other button has been toggled

            # Go through and find which one has changed to positive, setting all others to 0 if not pin_state
            for k in prop_keys:
                if self.get(k):
                    # print ( "Key " + k + " is " + str(self[k]) + ", Last state = " + str(self.last_state[index]) )
                    if (self[k] != 0) and (self.last_state[prop_keys.index(k)] == False):
                        self.last_state[prop_keys.index(k)] = True
                    else:
                        if not pin_state:
                            self.last_state[prop_keys.index(k)] = False
                            self[k] = 0
                """
                try:
                    if (self[k] != 0) and (self.last_state[prop_keys.index(k)] == False):
                        self.last_state[prop_keys.index(k)] = True
                    else:
                        if not pin_state:
                            self.last_state[prop_keys.index(k)] = False
                            self[k] = 0
                except:
                    pass
                """


    def draw_self (self, context, layout):


        mcell = context.scene.mcell

        if not mcell.get ( 'saved_by_source_id' ):
            # This .blend file has no CellBlender data at all or was created with CellBlender RC3 / RC4
            if not mcell.initialized:  # if not mcell['initialized']:
                # This .blend file has no CellBlender data (never saved with CellBlender enabled)
                mcell.draw_uninitialized ( layout )
            else:
                # This is a CellBlender RC3 or RC4 file so draw the RC3/4 upgrade button
                row = layout.row()
                row.label ( text="Blend File version (RC3/4) doesn't match CellBlender version", icon='ERROR' )
                row = layout.row()
                row.operator ( "mcell.upgraderc3", text="Upgrade RC3/4 Blend File to Current Version", icon='GHOST_ENABLED' )
        else:
            CB_ID = mcell['saved_by_source_id']
            source_id = cellblender.cellblender_info['cellblender_source_sha1']
            if CB_ID != source_id:
                # This is a CellBlender file >= 1.0, so draw the normal upgrade button
                row = layout.row()
                row.label ( text="Blend File version doesn't match CellBlender version", icon='ERROR' )
                row = layout.row()
                row.operator ( "mcell.upgrade", text="Upgrade Blend File to Current Version", icon='GHOST_ENABLED' )
                if 'data_model' in mcell.keys():
                    # There is a data model present, so show the option to save it directly
                    row = layout.row()
                    row.operator ( "mcell.export_data_model", text="Export Data Model to DM.txt", icon='EXPORT' )
                    row = layout.row()
                    row.operator ( "mcell.export_data_model_json", text="Export Data Model to DM.json", icon='EXPORT' )

            else:
                # The versions matched, so draw the normal panels

                ################################################################################
                #
                #  Button Panel Notes:
                #
                #    The menu buttons can be shown in either short format or long format.
                #    Short format shows all the buttons in a row similar to the header in
                #    Blender's native "Properties" panel. This was the original design.
                #    Long format was added to show text (at the expense of screen space).
                #    The Preferences panel has a check box for "Show Long Menu Buttons"
                #    that has been defaulted to "True" for quite some time. The short form
                #    is still handy when showing multiple panels or with smaller screens
                #    or both.
                #
                #    The original short format also had the ability to show or hide each
                #    button via a series of check boxes in the "Show Extra Options" section
                #    of the Preferences panel. These were enabled with the "show_button_num"
                #    boolean array in the "cellblender_preferences" property group. To keep
                #    it simple, they were just numbered with "0" being the push pin and the
                #    refresh button. All others started from index "1" and counted upward.
                #    The size of this boolean array needs to match (or be larger than) the
                #    number of buttons being shown or hidden. This show/hide functionality
                #    was not implemented for the long format buttons when they were added.
                #
                #    It's not clear whether the show/hide functionality remains useful. It
                #    could be used for experimental or special panels that the normal user
                #    shouldn't see. It could also be useful in teaching environments to limit
                #    the number of things that can go wrong. At this time, those questionable
                #    uses would not justify adding the feature. Conversely, it's not clear at
                #    this time that removal is justified either. But since the feature exists,
                #    it should work correctly which means ensuring that the number of buttons
                #    is less than the size of the "show_button_num" array.
                #
                #    Note that there was a bit of a logic error in allowing the "Settings"
                #    button to be hidden. If that button were hidden, then it wouldn't be
                #    possible to get to the Settings panel to show it again (although it
                #    could be shown again via command line operations). This might be a
                #    "feature" to lock away certain buttons, but it's more likely to cause
                #    problems than be useful. For that reason, it is always drawn for now.
                #
                ################################################################################

                if not mcell.cellblender_preferences.use_long_menus:

                    # Draw all the selection buttons in a single row (Short format)

                    real_row = layout.row()
                    split = real_row.split(factor=0.9)
                    col = split.column()

                    #row = layout.row(align=True)
                    row = col.row(align=True)

                    ############################################################################################################################
                    #                                                                                                                          #
                    #   !! N O T E !! - The size of "show_button_num" BoolVectorProperty in cellblender_preferences.py MUST be large enough!!  #
                    #                                                                                                                          #
                    ############################################################################################################################


                    if mcell.cellblender_preferences.show_button_num[1]: row.prop ( self, "examples_select", icon='MOD_BUILD', text="" )
                    if mcell.cellblender_preferences.show_button_num[2]: row.prop ( self, "pbc_select", icon='GRID', text="" )

                    if True or mcell.cellblender_preferences.show_button_num[3]: row.prop ( self, "preferences_select", icon='PREFERENCES', text="" )
                    if mcell.cellblender_preferences.show_button_num[4]: row.prop ( self, "scripting_select", icon='SCRIPT', text="" )

                    if mcell.cellblender_preferences.show_button_num[5]: row.prop ( self, "parameters_select", icon='SEQ_SEQUENCER', text="" )
                    if mcell.cellblender_preferences.show_button_num[6]: row.prop ( self, "objects_select", icon='MESH_ICOSPHERE', text="" )  # Or 'MESH_CUBE'

                    if mcell.cellblender_preferences.use_stock_icons:
                        # Use "stock" icons for molecules and reactions
                        if mcell.cellblender_preferences.show_button_num[7]: row.prop ( self, "molecule_select", icon='FORCE_LENNARDJONES', text="" )
                        if mcell.cellblender_preferences.show_button_num[8]: row.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="" )
                    else:
                        # Use custom icons for molecules and reactions
                        if mcell.cellblender_preferences.show_button_num[7]:
                            if self.molecule_select:
                                molecule_img_sel = bpy.data.images.get('mol_s')
                                mol_s = layout.icon(molecule_img_sel)
                                row.prop ( self, "molecule_select", icon_value=mol_s, text="" )
                            else:
                                molecule_img_unsel = bpy.data.images.get('mol_u')
                                mol_u = layout.icon(molecule_img_unsel)
                                row.prop ( self, "molecule_select", icon_value=mol_u, text="" )

                        if mcell.cellblender_preferences.show_button_num[8]:
                            if self.reaction_select:
                                react_img_sel = bpy.data.images.get('reaction_s')
                                reaction_s = layout.icon(react_img_sel)
                                row.prop ( self, "reaction_select", icon_value=reaction_s, text="" )
                            else:
                                react_img_unsel = bpy.data.images.get('reaction_u')
                                reaction_u = layout.icon(react_img_unsel)
                                row.prop ( self, "reaction_select", icon_value=reaction_u, text="" )

                    if mcell.cellblender_preferences.show_button_num[9]: row.prop ( self, "placement_select", icon='GROUP_VERTEX', text="" )
                    if mcell.cellblender_preferences.show_button_num[10]: row.prop ( self, "rel_patterns_select", icon='TIME', text="" )
                    if mcell.cellblender_preferences.show_button_num[11]: row.prop ( self, "surf_classes_select", icon='LIGHTPROBE_CUBE_MAP', text="" )
                    if mcell.cellblender_preferences.show_button_num[12]: row.prop ( self, "surf_regions_select", icon='UV_DATA', text="" )
                    if mcell.cellblender_preferences.show_button_num[13]: row.prop ( self, "partitions_select", icon='GRID', text="" )
                    if mcell.cellblender_preferences.show_button_num[14]: row.prop ( self, "graph_select", icon='GRAPH', text="" )
                    if mcell.cellblender_preferences.show_button_num[15]: row.prop ( self, "viz_select", icon='SEQUENCE', text="" )
                    if mcell.cellblender_preferences.show_button_num[16]: row.prop ( self, "init_select", icon='COLOR_RED', text="" )


                    col = split.column()
                    row = col.row()

                    if self.select_multiple:
                        if mcell.cellblender_preferences.show_button_num[0]: row.prop ( self, "select_multiple", icon='PINNED', text="" )
                    else:
                        if mcell.cellblender_preferences.show_button_num[0]: row.prop ( self, "select_multiple", icon='UNPINNED', text="" )

                    # Use an operator rather than a property to make it an action button
                    # row.prop ( self, "reload_viz", icon='FILE_REFRESH' )
                    if mcell.cellblender_preferences.show_button_num[0]: row.operator ( "cbm.refresh_operator", icon='FILE_REFRESH', text="")

                else:

                    # Draw all the selection buttons with labels in 2 columns (Long format):

                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "examples_select", icon='MOD_BUILD', text="Examples" )
                    bcol = brow.column()
                    bcol.prop ( self, "pbc_select", icon='GRID', text="Periodic Boundary Conditions" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "preferences_select", icon='PREFERENCES', text="Settings & Preferences" )
                    bcol = brow.column()
                    bcol.prop ( self, "scripting_select", icon='SCRIPT', text="Scripting" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "parameters_select", icon='SEQ_SEQUENCER', text="Parameters" )
                    bcol = brow.column()
                    bcol.prop ( self, "objects_select", icon='MESH_ICOSPHERE', text="Model Objects" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    if mcell.cellblender_preferences.use_stock_icons:
                        # Use "stock" icons to check on drawing speed problem
                        bcol.prop ( self, "molecule_select", icon='FORCE_LENNARDJONES', text="Molecules" )
                    else:
                        # Use custom icons for some buttons
                        if self.molecule_select:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='FORCE_LENNARDJONES', text="Molecules" )
                            else:
                                molecule_img_sel = bpy.data.images.get('mol_s')
                                mol_s = layout.icon(molecule_img_sel)
                                bcol.prop ( self, "molecule_select", icon_value=mol_s, text="Molecules" )
                        else:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='FORCE_LENNARDJONES', text="Molecules" )
                            else:
                                molecule_img_unsel = bpy.data.images.get('mol_u')
                                mol_u = layout.icon(molecule_img_unsel)
                                bcol.prop ( self, "molecule_select", icon_value=mol_u, text="Molecules" )

                    bcol = brow.column()
                    if mcell.cellblender_preferences.use_stock_icons:
                        bcol.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="Reactions" )
                    else:
                        if self.reaction_select:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="Reactions" )
                            else:
                                react_img_sel = bpy.data.images.get('reaction_s')
                                reaction_s = layout.icon(react_img_sel)
                                bcol.prop ( self, "reaction_select", icon_value=reaction_s, text="Reactions" )
                        else:
                            if mcell.cellblender_preferences.use_stock_icons:
                                # Use "stock" icons to check on drawing speed problem
                                bcol.prop ( self, "reaction_select", icon='ARROW_LEFTRIGHT', text="Reactions" )
                            else:
                                react_img_unsel = bpy.data.images.get('reaction_u')
                                reaction_u = layout.icon(react_img_unsel)
                                bcol.prop ( self, "reaction_select", icon_value=reaction_u, text="Reactions" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "placement_select", icon='GROUP_VERTEX', text=" Molecule Placement" )
                    bcol = brow.column()
                    bcol.prop ( self, "rel_patterns_select", icon='TIME', text="Release Patterns" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "surf_classes_select", icon='LIGHTPROBE_CUBEMAP', text="Surface Classes" )
                    bcol = brow.column()
                    bcol.prop ( self, "surf_regions_select", icon='UV_DATA', text="Assign Surface Classes" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "partitions_select", icon='GRID', text="Partitions" )
                    bcol = brow.column()
                    bcol.prop ( self, "graph_select", icon='GRAPH', text="Plot Output Settings" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    bcol.prop ( self, "viz_select", icon='SEQUENCE', text="Visualization Settings" )
                    bcol = brow.column()
                    bcol.prop ( self, "init_select", icon='ARMATURE_DATA', text="Run Simulation" )


                    brow = layout.row()  ##############################################################

                    bcol = brow.column()
                    if self.select_multiple:
                        bcol.prop ( self, "select_multiple", icon='PINNED', text="Multiple Panels" )
                    else:
                        bcol.prop ( self, "select_multiple", icon='UNPINNED', text="Multiple Panels" )
                    bcol = brow.column()
                    bcol.operator ( "cbm.refresh_operator",icon='FILE_REFRESH', text="Reload Visualization Data")



                # Check for modifications to the model since the last run

                if eval(mcell.parameter_system.last_parameter_update_time) > eval(mcell.run_simulation.last_simulation_run_time):
                    row = layout.row()
                    row.label ( text="Warning: Possible model change since last run", icon="INFO" )  # Information might be better than "ERROR" since this is not really an error


                # Draw each panel only if it is selected

                if self.preferences_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Project Settings", icon='SETTINGS' )
                    context.scene.mcell.project_settings.draw_layout ( context, layout )

                    layout.box() # Use as a separator
                    layout.label ( text="Preferences", icon='PREFERENCES' )
                    context.scene.mcell.cellblender_preferences.draw_layout ( context, layout )

                if self.scripting_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Scripting", icon='SCRIPT' )
                    context.scene.mcell.scripting.draw_layout ( context, layout )

                if self.parameters_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Model Parameters", icon='SEQ_SEQUENCER' )
                    context.scene.mcell.parameter_system.draw_layout ( context, layout )

                if self.molecule_select:
                    layout.box() # Use as a separator
                    layout.label(text="Defined Molecules", icon='FORCE_LENNARDJONES')
                    context.scene.mcell.molecules.draw_layout ( context, layout )

                if self.reaction_select:
                    layout.box() # Use as a separator
                    if mcell.cellblender_preferences.use_stock_icons:
                        # Use "stock" icons to check on drawing speed problem
                        layout.label ( text="Defined Reactions", icon='ARROW_LEFTRIGHT' )
                    else:
                        react_img_sel = bpy.data.images.get('reaction_s')
                        reaction_s = layout.icon(react_img_sel)
                        layout.label ( text="Defined Reactions", icon_value=reaction_s )
                    context.scene.mcell.reactions.draw_layout ( context, layout )

                if self.placement_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Molecule Release/Placement", icon='GROUP_VERTEX' )
                    context.scene.mcell.release_sites.draw_layout ( context, layout )

                if self.rel_patterns_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Release Patterns", icon='TIME' )
                    context.scene.mcell.release_patterns.draw_layout ( context, layout )

                if self.objects_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Model Objects", icon='MESH_ICOSPHERE' )  # Or 'MESH_CUBE'
                    context.scene.mcell.model_objects.draw_layout ( context, layout )
                    # layout.box() # Use as a separator
                    if context.object != None:
                        context.object.mcell.regions.draw_layout(context, layout)

                if self.surf_classes_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Defined Surface Classes", icon='LIGHTPROBE_CUBEMAP' )
                    context.scene.mcell.surface_classes.draw_layout ( context, layout )

                if self.surf_regions_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Assigned Surface Classes", icon='UV_DATA' )
                    context.scene.mcell.mod_surf_regions.draw_layout ( context, layout )

                if self.partitions_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Partitions", icon='GRID' )
                    context.scene.mcell.partitions.draw_layout ( context, layout )

                if self.pbc_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Periodic Boundary Conditions", icon='GRID' )
                    context.scene.mcell.pbc.draw_layout ( context, layout )

                if self.graph_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Reaction Data Output", icon='GRAPH' )
                    context.scene.mcell.rxn_output.draw_layout ( context, layout )

                if self.viz_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Visualization", icon='SEQUENCE' )
                    context.scene.mcell.viz_output.draw_layout ( context, layout )
                    layout.box() # Use as a separator
                    context.scene.mcell.mol_viz.draw_layout ( context, layout )

                if self.init_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Run Simulation", icon='ARMATURE_DATA' )
                    context.scene.mcell.initialization.draw_layout ( context, layout )

                if self.examples_select:
                    layout.box() # Use as a separator
                    layout.label ( text="Examples", icon='MOD_BUILD' )
                    context.scene.mcell.cellblender_examples.draw_layout ( context, layout )

        # print ( "Bottom of CellBlenderMainPanelPropertyGroup.draw_self" )


import pickle

# Main MCell (CellBlender) Properties Class:
def refresh_source_id_callback ( self, context ):
    # This is a boolean which defaults to false. So clicking it should change it to true which triggers this callback:
    if self.refresh_source_id:
        print ("Updating ID")
        if not ('cellblender_source_id_from_file' in cellblender.cellblender_info):
            # Save the version that was read from the file
            cellblender.cellblender_info.update ( { "cellblender_source_id_from_file": cellblender.cellblender_info['cellblender_source_sha1'] } )
        # Compute the new version
        cellblender.cellblender_source_info.identify_source_version(os.path.dirname(__file__),verbose=True)
        # Check to see if they match
        if cellblender.cellblender_info['cellblender_source_sha1'] == cellblender.cellblender_info['cellblender_source_id_from_file']:
            # They still match, so remove the "from file" version from the info to let the panel know that there's no longer a mismatch:
            cellblender.cellblender_info.pop('cellblender_source_id_from_file')
        # Setting this to false will redraw the panel
        self.refresh_source_id = False



class MCellPropertyGroup(bpy.types.PropertyGroup):
    initialized: BoolProperty(name="Initialized", default=False)
    # versions_match: BoolProperty ( default=True )

    cellblender_version: StringProperty(name="CellBlender Version", default="0")
    cellblender_addon_id: StringProperty(name="CellBlender Addon ID", default="0")
    cellblender_data_model_version: StringProperty(name="CellBlender Data Model Version", default="0")
    refresh_source_id: BoolProperty ( default=False, description="Recompute the Source ID from actual files", update=refresh_source_id_callback )
    #cellblender_source_hash: StringProperty(
    #    name="CellBlender Source Hash", default="unknown")

    # This provides a means to convert Python double values to Blender's FloatProperty precision
    blender_float_prop: FloatProperty()
    def blender_float ( self, python_float ):
        self.blender_float_prop = python_float
        return ( self.blender_float_prop )


    cellblender_main_panel: PointerProperty ( type=CellBlenderMainPanelPropertyGroup, name="CellBlender Main Panel" )


    cellblender_examples: PointerProperty ( type=cellblender_examples.CellBlenderExamplesPropertyGroup, name="CellBlender Examples" )
    cellblender_preferences: PointerProperty ( type=cellblender_preferences.CellBlenderPreferencesPropertyGroup, name="CellBlender Preferences" )
    scripting: PointerProperty ( type=cellblender_scripting.CellBlenderScriptingPropertyGroup, name="CellBlender Scripting" )
    project_settings: PointerProperty ( type=cellblender_project.MCellProjectPropertyGroup, name="CellBlender Project Settings" )
    export_project: PointerProperty ( type=cellblender_project.MCellExportProjectPropertyGroup, name="Export Simulation" )
    run_simulation: PointerProperty ( type=cellblender_simulation.MCellRunSimulationPropertyGroup, name="Run Simulation" )
    sim_engines: PointerProperty ( type=cellblender_simulation.Pluggable, name="Simulation Engines" )
    sim_runners: PointerProperty ( type=cellblender_simulation.Pluggable, name="Simulation Runners" )
    mol_viz: PointerProperty ( type=cellblender_mol_viz.MCellMolVizPropertyGroup, name="Mol Viz Settings" )
    initialization: PointerProperty ( type=cellblender_initialization.MCellInitializationPropertyGroup, name="Model Initialization" )
    partitions: PointerProperty ( type=cellblender_partitions.MCellPartitionsPropertyGroup, name="Partitions" )
    pbc: PointerProperty ( type=cellblender_pbc.MCellPBCPropertyGroup, name="Periodic Boundary Conditions" )
    ############# DB: added for parameter import from BNG, SBML models####
    #parameters: PointerProperty ( type=MCellParametersPropertyGroup, name="Defined Parameters" )
    parameter_system: PointerProperty ( type=parameter_system.ParameterSystemPropertyGroup, name="Parameter System" )
    molecules: PointerProperty ( type=cellblender_molecules.MCellMoleculesListProperty, name="Defined Molecules" )
    molmaker: PointerProperty ( type=cellblender_molmaker.MCellMolMakerPropertyGroup, name="Molecule Maker" )
    reactions: PointerProperty ( type=cellblender_reactions.MCellReactionsListProperty, name="Defined Reactions" )
    surface_classes: PointerProperty ( type=cellblender_surface_classes.MCellSurfaceClassesPropertyGroup, name="Defined Surface Classes" )
    mod_surf_regions: PointerProperty ( type=cellblender_surface_regions.MCellModSurfRegionsPropertyGroup, name="Assign Surface Classes" )
    release_patterns: PointerProperty ( type=cellblender_release.MCellReleasePatternPropertyGroup, name="Defined Release Patterns" )
    release_sites: PointerProperty (  type=cellblender_release.MCellMoleculeReleasePropertyGroup, name="Defined Release Sites" )
    model_objects: PointerProperty (  type=cellblender_objects.MCellModelObjectsPropertyGroup, name="Instantiated Objects" )
    viz_output: PointerProperty ( type=cellblender_mol_viz.MCellVizOutputPropertyGroup, name="Viz Output" )
    rxn_output: PointerProperty ( type=cellblender_reaction_output.MCellReactionOutputPropertyGroup, name="Reaction Output" )
    meshalyzer: PointerProperty ( type=cellblender_meshalyzer.MCellMeshalyzerPropertyGroup, name="CellBlender Meshalyzer" )
    object_selector: PointerProperty ( type=MCellObjectSelectorPropertyGroup, name="CellBlender Project Settings" )
    #molecule_glyphs: PointerProperty ( type=cellblender_molecules.MCellMoleculeGlyphsPropertyGroup, name="Molecule Shapes" )

    legacy: PointerProperty ( type=cellblender_legacy.MCellLegacyGroup, name="Lecacy Support" )

    #scratch_settings: PointerProperty ( type=MCellScratchPropertyGroup, name="CellBlender Scratch Settings" )

    def init_properties ( self, context=None ):
        print ("MCellPropertyGroup.init_properties called")
        self.cellblender_version = "0.1.54"
        self.cellblender_addon_id = "0"
        self.cellblender_data_model_version = "0"
        self.parameter_system.init_properties()
        self.initialization.init_properties ( self.parameter_system )
        self.run_simulation.init_properties ( self.parameter_system )
        self.molecules.init_properties ( self.parameter_system )
        self.viz_output.init_properties ( self.parameter_system )
        self.sim_engines.name = "sim_engines"
        self.sim_runners.name = "sim_runners"
        #if context != None:
        #    # Force an update of the pluggable items.
        #    print ("MCellPropertyGroup.init_properties is updating engines and runners")
        #    self.sim_engines.plugs_changed_callback ( context )
        #    self.sim_runners.plugs_changed_callback ( context )
        # Don't forget to update the "saved_by_source_id" to match the current version of the addon
        self['saved_by_source_id'] = cellblender.cellblender_info['cellblender_source_sha1']
        self.initialized = True


    def remove_properties ( self, context ):
        print ( "Removing all MCell Properties..." )
        #self.molecule_glyphs.remove_properties(context)
        self.object_selector.remove_properties(context)
        self.meshalyzer.remove_properties(context)
        self.rxn_output.remove_properties(context)
        self.viz_output.remove_properties(context)
        self.model_objects.remove_properties(context)
        self.release_sites.remove_properties(context)
        self.release_patterns.remove_properties(context)
        self.mod_surf_regions.remove_properties(context)
        self.surface_classes.remove_properties(context)
        self.reactions.remove_properties(context)
        self.molecules.remove_properties(context)
        self.partitions.remove_properties(context)
        self.initialization.remove_properties(context)
        self.mol_viz.remove_properties(context)
        self.run_simulation.remove_properties(context)
        self.export_project.remove_properties(context)
        self.project_settings.remove_properties(context)
        self.cellblender_preferences.remove_properties(context)
        self.cellblender_main_panel.remove_properties(context)
        self.parameter_system.remove_properties(context)
        print ( "Done removing all MCell Properties." )



    def build_data_model_from_properties ( self, context, geometry=False, scripts=False, dyn_geo=False ):
        print ( "build_data_model_from_properties: Constructing a data_model dictionary from current properties" )
        print ( "   geometry=" + str(geometry) + ", scripts=" + str(scripts) + ", dyn_geo=" + str(dyn_geo) )
        dm = {}
        dm['data_model_version'] = "DM_2017_06_23_1300"
        if self.cellblender_preferences.mcell4_mode:
          dm['model_language'] = 'mcell4'
        elif self.cellblender_preferences.bionetgen_mode:
          dm['model_language'] = 'mcell3r'
        else:
          dm['model_language'] = 'mcell3'
        dm['blender_version'] = [v for v in bpy.app.version]
        dm['cellblender_version'] = self.cellblender_version
        #dm['cellblender_source_hash'] = self.cellblender_source_hash
        dm['cellblender_source_sha1'] = cellblender.cellblender_info["cellblender_source_sha1"]
        if 'api_version' in self:
            dm['api_version'] = self['api_version']
        else:
            dm['api_version'] = 0
        dm['parameter_system'] = self.parameter_system.build_data_model_from_properties(context)
        dm['initialization'] = self.initialization.build_data_model_from_properties(context)
        dm['initialization']['partitions'] = self.partitions.build_data_model_from_properties(context)
        dm['define_molecules'] = self.molecules.build_data_model_from_properties(context)
        dm['define_reactions'] = self.reactions.build_data_model_from_properties(context)
        dm['release_sites'] = self.release_sites.build_data_model_from_properties(context)
        dm['define_release_patterns'] = self.release_patterns.build_data_model_from_properties(context)
        dm['define_surface_classes'] = self.surface_classes.build_data_model_from_properties(context)
        dm['modify_surface_regions'] = self.mod_surf_regions.build_data_model_from_properties(context)
        dm['periodic_boundary_conditions'] = self.pbc.build_data_model_from_properties(context)
        dm['model_objects'] = self.model_objects.build_data_model_from_properties(context)
        dm['viz_output'] = self.viz_output.build_data_model_from_properties(context)
        dm['simulation_control'] = self.run_simulation.build_data_model_from_properties(context)
        dm['mol_viz'] = self.mol_viz.build_data_model_from_properties(context)
        dm['reaction_data_output'] = self.rxn_output.build_data_model_from_properties(context)
        dm['scripting'] = self.scripting.build_data_model_from_properties(context,scripts)
        if geometry:
            print ( "Adding Geometry to Data Model" )
            dm['geometrical_objects'] = self.model_objects.build_data_model_geometry_from_mesh(context,dyn_geo=dyn_geo)
            dm['materials'] = self.model_objects.build_data_model_materials_from_materials(context)
        return dm



    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellPropertyGroup Data Model" )
        # cellblender.data_model.dump_data_model ( "Dump of dm passed to MCellPropertyGroup.upgrade_data_model", dm )

        # Set the model_language field which should be "mcell4" for any upgraded models
        dm['model_language'] = 'mcell4'

        # Perform any upgrades to this top level data model
        if 'data_model_version' not in dm:
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['data_model_version'] = "DM_2017_06_23_1300"

        if dm['data_model_version'] != "DM_2017_06_23_1300":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellPropertyGroup data model to current version." )
            return None

        # Perform any upgrades to all components within this top level data model

        group_name = "parameter_system"
        if group_name in dm:
            dm[group_name] = parameter_system.ParameterSystemPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "initialization"
        if group_name in dm:
            dm[group_name] = cellblender_initialization.MCellInitializationPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

            subgroup_name = "partitions"
            if subgroup_name in dm[group_name]:
                dm[group_name][subgroup_name] = cellblender_partitions.MCellPartitionsPropertyGroup.upgrade_data_model ( dm[group_name][subgroup_name] )
                if dm[group_name][subgroup_name] == None:
                    return None

        group_name = "define_molecules"
        if group_name in dm:
            dm[group_name] = cellblender_molecules.MCellMoleculesListProperty.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "define_reactions"
        if group_name in dm:
            dm[group_name] = cellblender_reactions.MCellReactionsListProperty.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "release_sites"
        if group_name in dm:
            dm[group_name] = cellblender_release.MCellMoleculeReleasePropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "define_release_patterns"
        if group_name in dm:
            dm[group_name] = cellblender_release.MCellReleasePatternPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "define_surface_classes"
        if group_name in dm:
            dm[group_name] = cellblender_surface_classes.MCellSurfaceClassesPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "modify_surface_regions"
        if group_name in dm:
            dm[group_name] = cellblender_surface_regions.MCellModSurfRegionsPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "periodic_boundary_conditions"
        if group_name in dm:
            dm[group_name] = cellblender_pbc.MCellPBCPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "model_objects"
        if group_name in dm:
            dm[group_name] = cellblender_objects.MCellModelObjectsPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "viz_output"
        if group_name in dm:
            dm[group_name] = cellblender_mol_viz.MCellVizOutputPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "simulation_control"
        if group_name in dm:
            dm[group_name] = cellblender_simulation.MCellRunSimulationPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "mol_viz"
        if group_name in dm:
            dm[group_name] = cellblender_mol_viz.MCellMolVizPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "reaction_data_output"
        if group_name in dm:
            dm[group_name] = cellblender_reaction_output.MCellReactionOutputPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        group_name = "scripting"
        if group_name in dm:
            dm[group_name] = cellblender_scripting.CellBlenderScriptingPropertyGroup.upgrade_data_model ( dm[group_name] )
            if dm[group_name] == None:
                return None

        return dm



    def build_properties_from_data_model ( self, context, dm, geometry=False, scripts=False ):
        print ( "build_properties_from_data_model: Data Model Keys = " + str(dm.keys()) )

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2017_06_23_1300":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellPropertyGroup data model to current version." )

        # Remove the existing MCell Property Tree
        self.remove_properties(context)

        # Now convert the updated Data Model into CellBlender Properties
        print ( "Overwriting properites based on data in the data model dictionary" )

        # Start by calling "init_properties" which creates a full new CellBlender property tree
        self.init_properties( context )

        # Set the bionetgen_mode based on model_language
        if 'model_language' in dm:
            if dm['model_language'] == 'mcell4':
                self.cellblender_preferences.mcell4_mode = True
                self.cellblender_preferences.bionetgen_mode = True
            else:
                self.cellblender_preferences.mcell4_mode = False
                if dm['model_language'] == 'mcell3r':
                    self.cellblender_preferences.bionetgen_mode = True
                else:
                    self.cellblender_preferences.bionetgen_mode = False
        else:
            # default
            self.cellblender_preferences.mcell4_mode = True
            self.cellblender_preferences.bionetgen_mode = True
            

        # Then add each section

        if "parameter_system" in dm:
            print ( "Overwriting the parameter_system properties" )
            self.parameter_system.build_properties_from_data_model ( context, dm["parameter_system"] )


        ### __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

        #return ##############  See what we have at this point...



        # Move below model objects?
        #if "modify_surface_regions" in dm:
        #    print ( "Overwriting the modify_surface_regions properties" )
        #    self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
        if geometry:
            print ( "Deleting all mesh objects" )
            self.model_objects.delete_all_mesh_objects(context)
            if "materials" in dm:
                print ( "Overwriting the materials properties" )
                print ( "Building Materials from Data Model Materials" )
                self.model_objects.build_materials_from_data_model_materials ( context, dm['materials'] )
            if "geometrical_objects" in dm:
                print ( "Overwriting the geometrical_objects properties" )
                print ( "Building Mesh Geometry from Data Model Geometry" )
                self.model_objects.build_mesh_from_data_model_geometry ( context, dm["geometrical_objects"] )
            print ( "Not fully implemented yet!!!!" )

        if "scripting" in dm:
            print ( "Overwriting the scripting properties" )
            self.scripting.build_properties_from_data_model ( context, dm["scripting"], scripts )

        if "initialization" in dm:
            print ( "Overwriting the initialization properties" )
            self.initialization.build_properties_from_data_model ( context, dm["initialization"] )
            if "partitions" in dm["initialization"]:
                print ( "Overwriting the partitions properties" )
                self.partitions.build_properties_from_data_model ( context, dm["initialization"]["partitions"] )
        if "define_molecules" in dm:
            print ( "Overwriting the define_molecules properties" )
            self.molecules.build_properties_from_data_model ( context, dm["define_molecules"] )
        if "release_sites" in dm:
            print ( "Overwriting the release_sites properties" )
            self.release_sites.build_properties_from_data_model ( context, dm["release_sites"] )
        if "define_release_patterns" in dm:
            print ( "Overwriting the define_release_patterns properties" )
            self.release_patterns.build_properties_from_data_model ( context, dm["define_release_patterns"] )
        if "define_surface_classes" in dm:
            print ( "Overwriting the define_surface_classes properties" )
            self.surface_classes.build_properties_from_data_model ( context, dm["define_surface_classes"] )
        if "define_reactions" in dm:
            print ( "Overwriting the define_reactions properties" )
            self.reactions.build_properties_from_data_model ( context, dm["define_reactions"] )

        # Building geometry was here ... moved above to keep it from deleting molecule objects and meshes
        if "model_objects" in dm:
            print ( "Overwriting the model_objects properties" )
            self.model_objects.build_properties_from_data_model ( context, dm["model_objects"] )
        if "modify_surface_regions" in dm:
            print ( "Overwriting the modify_surface_regions properties" )
            self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
        if "periodic_boundary_conditions" in dm:
            print ( "Overwriting the periodic_boundary_conditions properties" )
            self.pbc.build_properties_from_data_model ( context, dm["periodic_boundary_conditions"] )
        if "viz_output" in dm:
            print ( "Overwriting the viz_output properties" )
            self.viz_output.build_properties_from_data_model ( context, dm["viz_output"] )
        if "mol_viz" in dm:
            print ( "Overwriting the mol_viz properties" )
            self.mol_viz.build_properties_from_data_model ( context, dm["mol_viz"] )

        # This had been commented out because it's not clear how it should work yet...
        if "simulation_control" in dm:
            print ( "Overwriting the simulation_control properties" )
            self.run_simulation.build_properties_from_data_model ( context, dm["simulation_control"] )

        if "reaction_data_output" in dm:
            print ( "Overwriting the reaction_data_output properties" )
            self.rxn_output.build_properties_from_data_model ( context, dm["reaction_data_output"] )

        # Now call the various "check" routines to clean up any unresolved references
        print ( "Checking the initialization and partitions properties" )
        self.initialization.check_properties_after_building ( context )
        self.partitions.check_properties_after_building ( context )
        print ( "Checking the define_molecules properties" )
        self.molecules.check_properties_after_building ( context )
        print ( "Checking the define_reactions properties" )
        self.reactions.check_properties_after_building ( context )
        print ( "Checking the release_sites properties" )
        self.release_sites.check_properties_after_building ( context )
        print ( "Checking the define_release_patterns properties" )
        self.release_patterns.check_properties_after_building ( context )
        print ( "Checking the define_surface_classes properties" )
        self.surface_classes.check_properties_after_building ( context )
        print ( "Checking the modify_surface_regions properties" )
        self.mod_surf_regions.check_properties_after_building ( context )
        print ( "Checking all mesh objects" )
        self.model_objects.check_properties_after_building ( context )
        print ( "Checking the viz_output properties" )
        self.viz_output.check_properties_after_building ( context )
        print ( "Checking the mol_viz properties" )
        self.mol_viz.check_properties_after_building ( context )
        print ( "Checking the reaction_data_output properties" )
        self.rxn_output.check_properties_after_building ( context )
        print ( "Checking/Updating the model_objects properties" )
        cellblender_objects.model_objects_update(context)

        print ( "Done building properties from the data model." )



    def draw_uninitialized ( self, layout ):
        row = layout.row()
        row.operator("mcell.init_cellblender", text="Initialize CellBlender")




    def print_id_property_tree ( self, obj, name, depth ):
        """ Recursive routine that prints an ID Property Tree """
        depth = depth + 1
        indent = "".join([ '  ' for x in range(depth) ])
        print ( indent + "Depth="+str(depth) )
        print ( indent + "print_ID_property_tree() called with \"" + name + "\" of type " + str(type(obj)) )
        if "'IDPropertyGroup'" in str(type(obj)):
            print ( indent + "This is an ID property group: " + name )
            for k in obj.keys():
                self.print_id_property_tree ( obj[k], k, depth )
        elif "'list'" in str(type(obj)):
            print ( indent + "This is a list: " + name )
            i = 0
            for k in obj:
                self.print_id_property_tree ( k, name + '['+str(i)+']', depth )
                i += 1
        else:
            print ( indent + "This is NOT an ID property group: " + name + " = " + str(obj) )

        depth = depth - 1
        return

classes = (
            MCellObjectSelectorPropertyGroup,
            PP_OT_init_mcell,
            MCELL_PT_main_panel,
            MCELL_OT_upgrade,
            MCELL_OT_export_dm,
            MCELL_OT_export_dm_json,
            MCELL_OT_delete,
            CBM_OT_refresh_operator,
            CellBlenderMainPanelPropertyGroup,
            MCellPropertyGroup,
           )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)


# we use per module class registration/unregistration
#def register():
#    bpy.utils.register_module(__name__)
#
#def unregister():
#    bpy.utils.unregister_module(__name__)

