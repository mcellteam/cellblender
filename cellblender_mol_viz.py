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

# <pep8 compliant>

"""
This file contains the classes for CellBlender's Molecule Visualization.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_operators
from . import cellblender_release
from . import utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Mol Viz Operators:


# Mol Viz callback functions


# Mol Viz Panel Classes


# Mol Viz Property Groups


class MCellFloatVectorProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold float vector for a CollectionProperty """
    vec = bpy.props.FloatVectorProperty(name="Float Vector")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell Float Vector Property... no collections to remove. Is there anything special do to for Vectors?" )
        pass


class MCellVizOutputPropertyGroup(bpy.types.PropertyGroup):
    active_mol_viz_index = IntProperty(
        name="Active Molecule Viz Index", default=0)
    all_iterations = bpy.props.BoolProperty(
        name="All Iterations",
        description="Include all iterations for visualization.", default=True)
    start = bpy.props.IntProperty(
        name="Start", description="Starting iteration", default=0, min=0)
    end = bpy.props.IntProperty(
        name="End", description="Ending iteration", default=1, min=1)
    step = bpy.props.IntProperty(
        name="Step", description="Output viz data every n iterations.",
        default=1, min=1)
    export_all = BoolProperty(
        name="Export All",
        description="Visualize all molecules",
        default=True)

    def build_data_model_from_properties ( self, context ):
        print ( "Viz Output building Data Model" )
        vo_dm = {}
        vo_dm['data_model_version'] = "DM_2014_10_24_1638"
        vo_dm['all_iterations'] = self.all_iterations
        vo_dm['start'] = str(self.start)
        vo_dm['end'] = str(self.end)
        vo_dm['step'] = str(self.step)
        vo_dm['export_all'] = self.export_all
        return vo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellVizOutputPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellVizOutputPropertyGroup data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellVizOutputPropertyGroup data model to current version." )
        
        self.all_iterations = dm["all_iterations"]
        self.start = int(dm["start"])
        self.end = int(dm["end"])
        self.step = int(dm["step"])
        self.export_all = dm["export_all"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Visualization Output Properties... no collections to remove." )


    def draw_layout ( self, context, layout ):
        """ Draw the reaction output "panel" within the layout """
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            if mcell.molecules.molecule_list:
                row.label(text="Molecules To Visualize:",
                          icon='FORCE_LENNARDJONES')
                row.prop(self, "export_all")
                layout.template_list("MCELL_UL_visualization_export_list",
                                     "viz_export", mcell.molecules,
                                     "molecule_list", self,
                                     "active_mol_viz_index", rows=2)
                layout.prop(self, "all_iterations")
                if self.all_iterations is False:
                    row = layout.row(align=True)
                    row.prop(self, "start")
                    row.prop(self, "end")
                    row.prop(self, "step")
            else:
                row.label(text="Define at least one molecule", icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




class MCellMolVizPropertyGroup(bpy.types.PropertyGroup):
    """ Property group for for molecule visualization.

      This is the "Visualize Simulation Results Panel".

    """

    mol_viz_seed_list = CollectionProperty(
        type=StringProperty, name="Visualization Seed List")
    active_mol_viz_seed_index = IntProperty(
        name="Current Visualization Seed Index", default=0,
        update=cellblender_operators.read_viz_data_callback)
        #update= bpy.ops.mcell.read_viz_data)
    mol_file_dir = StringProperty(
        name="Molecule File Dir", subtype='NONE')
    mol_file_list = CollectionProperty(
        type=StringProperty, name="Molecule File Name List")
    mol_file_num = IntProperty(
        name="Number of Molecule Files", default=0)
    mol_file_name = StringProperty(
        name="Current Molecule File Name", subtype='NONE')
    mol_file_index = IntProperty(name="Current Molecule File Index", default=0)
    mol_file_start_index = IntProperty(
        name="Molecule File Start Index", default=0)
    mol_file_stop_index = IntProperty(
        name="Molecule File Stop Index", default=0)
    mol_file_step_index = IntProperty(
        name="Molecule File Step Index", default=1)
    mol_viz_list = CollectionProperty(
        type=StringProperty, name="Molecule Viz Name List")
    render_and_save = BoolProperty(name="Render & Save Images")
    mol_viz_enable = BoolProperty(
        name="Enable Molecule Vizualization",
        description="Disable for faster animation preview",
        default=True, update=cellblender_operators.mol_viz_update)
    color_list = CollectionProperty(
        type=MCellFloatVectorProperty, name="Molecule Color List")
    color_index = IntProperty(name="Color Index", default=0)
    manual_select_viz_dir = BoolProperty(
        name="Manually Select Viz Directory", default=False,
        description="Toggle the option to manually load viz data.",
        update=cellblender_operators.mol_viz_toggle_manual_select)


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

        # mv_file_list = []
        # for s in self.mol_file_list:
        #     mv_file_list.append ( str(s.name) )
        # mv_dm['file_list'] = mv_file_list

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


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMolVizPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_13_1700
            dm['data_model_version'] = "DM_2015_04_13_1700"

        if dm['data_model_version'] == "DM_2015_04_13_1700":
            # Change on June 22nd, 2015: The molecule file list will no longer be stored in the data model
            if 'file_list' in dm:
                dm.pop ( 'file_list' )
            dm['data_model_version'] = "DM_2015_06_22_1430"

        if dm['data_model_version'] != "DM_2015_06_22_1430":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMolVizPropertyGroup data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_06_22_1430":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMolVizPropertyGroup data model to current version." )

        # Remove the old properties (includes emptying collections)
        self.remove_properties ( context )

        # Build the new properties
        
        for s in dm["seed_list"]:
            new_item = self.mol_viz_seed_list.add()
            new_item.name = s
            
        self.active_mol_viz_seed_index = dm['active_seed_index']

        self.mol_file_dir = dm['file_dir']

        #for s in dm["file_list"]:
        #    new_item = self.mol_file_list.add()
        #    new_item.name = s

        self.mol_file_num = dm['file_num']
        self.mol_file_name = dm['file_name']
        self.mol_file_index = dm['file_index']
        self.mol_file_start_index = dm['file_start_index']
        self.mol_file_stop_index = dm['file_stop_index']
        self.mol_file_step_index = dm['file_step_index']
            
        for s in dm["viz_list"]:
            new_item = self.mol_viz_list.add()
            new_item.name = s
            
        self.render_and_save = dm['render_and_save']
        self.mol_viz_enable = dm['viz_enable']

        for c in dm["color_list"]:
            new_item = self.color_list.add()
            new_item.vec = c
            
        if 'color_index' in dm:
            self.color_index = dm['color_index']
        else:
            self.color_index = 0

        self.manual_select_viz_dir = dm['manual_select_viz_dir']


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Visualization Properties..." )

        """
        while len(self.mol_viz_seed_list) > 0:
            self.mol_viz_seed_list.remove(0)

        while len(self.mol_file_list) > 0:
            self.mol_file_list.remove(0)

        while len(self.mol_viz_list) > 0:
            self.mol_viz_list.remove(0)

        while len(self.color_list) > 0:
            # It's not clear if anything needs to be done to remove individual color components first
            self.color_list.remove(0)
        """

        for item in self.mol_viz_seed_list:
            item.remove_properties(context)
        self.mol_viz_seed_list.clear()
        self.active_mol_viz_seed_index = 0
        for item in self.mol_file_list:
            item.remove_properties(context)
        self.mol_file_list.clear()
        self.mol_file_index = 0
        self.mol_file_start_index = 0
        self.mol_file_stop_index = 0
        self.mol_file_step_index = 1
        for item in self.mol_viz_list:
            item.remove_properties(context)
        self.mol_viz_list.clear()
        for item in self.color_list:
            item.remove_properties(context)
        self.color_list.clear()
        self.color_index = 0
        print ( "Done removing all Molecule Visualization Properties." )





    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            row.prop(mcell.mol_viz, "manual_select_viz_dir")
            row = layout.row()
            if self.manual_select_viz_dir:
                row.operator("mcell.select_viz_data", icon='IMPORT')
            else:
                row.operator("mcell.read_viz_data", icon='IMPORT')
            row = layout.row()
            row.label(text="Molecule Viz Directory: " + self.mol_file_dir,
                      icon='FILE_FOLDER')
            row = layout.row()
            if not self.manual_select_viz_dir:
                row.template_list("UI_UL_list", "viz_seed", mcell.mol_viz,
                                "mol_viz_seed_list", mcell.mol_viz,
                                "active_mol_viz_seed_index", rows=2)
            row = layout.row()

            row = layout.row()
            row.label(text="Current Molecule File: "+self.mol_file_name,
                      icon='FILE')
# Disabled to explore UI slowdown behavior of Plot Panel and run options subpanel when mol_file_list is large
#            row = layout.row()
#            row.template_list("UI_UL_list", "viz_results", mcell.mol_viz,
#                              "mol_file_list", mcell.mol_viz, "mol_file_index",
#                              rows=2)
            row = layout.row()
            layout.prop(mcell.mol_viz, "mol_viz_enable")


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



