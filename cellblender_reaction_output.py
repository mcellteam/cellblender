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
This file contains the classes for CellBlender's Reaction Output.

"""

import glob
import os

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
from . import cellblender_release
from . import cellblender_utils
from cellblender.cellblender_utils import project_files_path


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Reaction Output Operators:


class MCELL_OT_rxn_output_add(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_add"
    bl_label = "Add Reaction Data Output"
    bl_description = "Add new reaction data output to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.add()
        mcell.rxn_output.active_rxn_output_index = len(
            mcell.rxn_output.rxn_output_list)-1
        check_rxn_output(self, context)

        return {'FINISHED'}


class MCELL_OT_rxn_output_remove(bpy.types.Operator):
    bl_idname = "mcell.rxn_output_remove"
    bl_label = "Remove Reaction Data Output"
    bl_description = "Remove selected reaction data output from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.rxn_output.rxn_output_list.remove(
            mcell.rxn_output.active_rxn_output_index)
        mcell.rxn_output.active_rxn_output_index -= 1
        if (mcell.rxn_output.active_rxn_output_index < 0):
            mcell.rxn_output.active_rxn_output_index = 0

        if mcell.rxn_output.rxn_output_list:
            check_rxn_output(self, context)

        return {'FINISHED'}


class MCELL_OT_plot_rxn_output_generic(bpy.types.Operator):
    bl_idname = "mcell.plot_rxn_output_generic"
    bl_label = "Plot Reactions"
    bl_description = "Plot the reactions using specified plotting package"
    bl_options = {'REGISTER', 'UNDO'}

    plotter_button_label = bpy.props.StringProperty()

    def execute(self, context):
        mcell = context.scene.mcell
        plot_sep = mcell.rxn_output.plot_layout
        plot_legend = mcell.rxn_output.plot_legend

        combine_seeds = mcell.rxn_output.combine_seeds
        mol_colors = mcell.rxn_output.mol_colors

        plot_button_label = self.plotter_button_label

        # Look up the plotting module by its name

        for plot_module in cellblender.cellblender_info[
                'cellblender_plotting_modules']:
            mod_name = plot_module.get_name()
            if mod_name == plot_button_label:
                break

        # Plot the data via this module
        # print("Preparing to call %s" % (mod_name))
        # The project_files_path is now where the MDL lives:
        data_path = project_files_path()
        data_path = os.path.join(data_path, "react_data")
        plot_spec_string = "xlabel=time(s) ylabel=count "
        if plot_legend != 'x':
            plot_spec_string = plot_spec_string + "legend=" + plot_legend

        for rxn_output in mcell.rxn_output.rxn_output_list:
            molecule_name = rxn_output.molecule_name
            object_name = rxn_output.object_name
            region_name = rxn_output.region_name
            file_name = None

            if rxn_output.rxn_or_mol == 'Molecule':
                if rxn_output.count_location == 'World':
                    file_name = "%s.World.dat" % (molecule_name)
                elif rxn_output.count_location == 'Object':
                    file_name = "%s.%s.dat" % (molecule_name, object_name)
                elif rxn_output.count_location == 'Region':
                    file_name = "%s.%s.%s.dat" % (molecule_name,
                                           object_name, region_name)
            else:
                rxn_name = rxn_output.reaction_name
                file_name = "%s.World.dat" % (rxn_name)

            if file_name:
                file_name = os.path.join("seed_*", file_name)
                candidate_file_list = glob.glob(
                    os.path.join(data_path, file_name))
                # Without sorting, the seeds may not be increasing
                candidate_file_list.sort()
                #print("Candidate file list for %s:" % (file_name))
                #print("  ", candidate_file_list)
                first_pass = True
                # Use the start_time.txt file to find files modified since
                # MCell was started
                start_time = os.stat(os.path.join(os.path.dirname(
                    bpy.data.filepath), "start_time.txt")).st_mtime
                # This file is both in the list and newer
                # than the run time for MCell
                candidate_file_list = [
                    ffn for ffn in candidate_file_list if os.stat(ffn).st_mtime >= start_time]
                for ffn in candidate_file_list:

                    # Create f as a relative path containing seed/file
                    split1 = os.path.split(ffn)
                    split2 = os.path.split(split1[0])
                    f = os.path.join(split2[1], split1[1])
                    
                    color_string = ""
                    if rxn_output.rxn_or_mol == 'Molecule' and mol_colors:
                        # Use molecule colors for graphs
                        # Should be standardized!!
                        mol_mat_name = "mol_%s_mat" % (molecule_name)
                        #print ("Molecule Material Name = ", mol_mat_name)
                        #Look up the material
                        mats = bpy.data.materials
                        mol_color = mats.get(mol_mat_name).diffuse_color
                        #print("Molecule color = ", mol_mat.diffuse_color)

                        mol_color_red = 255 * mol_color.r
                        mol_color_green = 255 * mol_color.g
                        mol_color_blue = 255 * mol_color.b
                        color_string = " color=#%2.2x%2.2x%2.2x " % (
                            mol_color_red, mol_color_green, mol_color_blue)

                    base_name = os.path.basename(f)

                    if combine_seeds:
                        title_string = " title=" + base_name
                    else:
                        title_string = " title=" + f
                    
                    if plot_sep == ' ':
                        # No title when all are on the same plot since only
                        # last will show
                        title_string = ""

                    if combine_seeds:
                        psep = " "
                        if first_pass:
                            psep = plot_sep
                            first_pass = False
                        plot_spec_string = (
                            plot_spec_string + psep + color_string +
                            title_string + " f=" + f)
                    else:
                        plot_spec_string = (
                            plot_spec_string + plot_sep + color_string +
                            title_string + " f=" + f)

        print("Plotting from", data_path)
        print("Plotting spec", plot_spec_string)
        plot_module.plot(data_path, plot_spec_string)

        return {'FINISHED'}


# Reaction Output callback functions


def check_rxn_output(self, context):
    """ Format reaction data output. """

    mcell = context.scene.mcell
    rxn_output_list = mcell.rxn_output.rxn_output_list
    rxn_output = rxn_output_list[
        mcell.rxn_output.active_rxn_output_index]
    mol_list = mcell.molecules.molecule_list
    reaction_list = mcell.reactions.reaction_name_list
    molecule_name = rxn_output.molecule_name
    reaction_name = rxn_output.reaction_name
    obj_list = mcell.model_objects.object_list
    object_name = rxn_output.object_name
    region_name = rxn_output.region_name
    rxn_output_name = ""

    status = ""
    if rxn_output.rxn_or_mol == 'Reaction':
        count_name = reaction_name
        name_list = reaction_list
    elif rxn_output.rxn_or_mol == 'Molecule':
        count_name = molecule_name
        name_list = mol_list
    else:
        count_name = molecule_name
        rxn_output.status = ""
        #rxn_output.name = rxn_output.mdl_string

        return

    try:
        region_list = bpy.data.objects[object_name].mcell.regions.region_list
    except KeyError:
        # The object name isn't a blender object
        region_list = []


    # Check for illegal names (Starts with a letter. No special characters.)
    count_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    c = re.match(count_filter, count_name)
    if c is None:
        status = "Name error: %s" % (count_name)
    else:
        # Check for undefined molecule or reaction names
        c_name = c.group(1)
        if not c_name in name_list:
            status = "Undefined: %s" % (c_name)

    # Use different formatting depending on where we are counting
    if rxn_output.count_location == 'World':
        rxn_output_name = "Count %s in World" % (count_name)
    elif rxn_output.count_location == 'Object':
        if not object_name in obj_list:
            status = "Undefined object: %s" % object_name
        else:
            rxn_output_name = "Count %s in/on %s" % (
                count_name, object_name)
    elif rxn_output.count_location == 'Region':
        if not region_name in region_list:
            status = "Undefined region: %s" % region_name
        else:
            rxn_output_name = "Count %s in/on %s[%s]" % (
                count_name, object_name, region_name)

    # Only update reaction output if necessary to avoid infinite recursion
    if rxn_output.name != rxn_output_name:
        rxn_output.name = rxn_output_name

    # Check for duplicate reaction data
    rxn_output_keys = rxn_output_list.keys()
    if rxn_output_keys.count(rxn_output.name) > 1 and not status:
        status = "Duplicate reaction output: %s" % (rxn_output.name)

    rxn_output.status = status

    return


# Reaction Output Panel Classes


class MCELL_UL_check_reaction_output_settings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_reaction_output_settings(bpy.types.Panel):
    bl_label = "CellBlender - Reaction Output Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.rxn_output.draw_panel ( context, self )



# Reaction Output Property Groups



class MCellReactionOutputProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Reaction Output", update=check_rxn_output)
    molecule_name = StringProperty(
        name="Molecule",
        description="Count the selected molecule.",
        update=check_rxn_output)
    reaction_name = StringProperty(
        name="Reaction",
        description="Count the selected reaction.",
        update=check_rxn_output)
    # allows the user to define a literal mdl string to count using complex expressions. E.g. 2*S1 
    mdl_string = StringProperty(
        name="MDL Definition",
        description="Count using a literal MDL definition.",
        update=check_rxn_output)
    object_name = StringProperty(
        name="Object", update=check_rxn_output)
    region_name = StringProperty(
        name="Region", update=check_rxn_output)
    count_location_enum = [
        ('World', "World", ""),
        ('Object', "Object", ""),
        ('Region', "Region", "")]
    count_location = bpy.props.EnumProperty(
        items=count_location_enum, name="Count Location",
        description="Count all molecules in the selected location.",
        update=check_rxn_output)
    rxn_or_mol_enum = [
        ('Reaction', "Reaction", ""),
        ('Molecule', "Molecule", ""),
        ('MDLString', "MDLString", "")]
    rxn_or_mol = bpy.props.EnumProperty(
        items=rxn_or_mol_enum, name="Count Reaction or Molecule",
        default='Molecule',
        description="Select between counting a reaction or molecule.",
        update=check_rxn_output)
    # plot_command = StringProperty(name="Command")  # , update=check_rxn_output)
    status = StringProperty(name="Status")

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction Output building Data Model" )
        ro_dm = {}
        ro_dm['data_model_version'] = "DM_2015_07_24_2311"
        ro_dm['name'] = self.name
        ro_dm['molecule_name'] = self.molecule_name
        ro_dm['reaction_name'] = self.reaction_name
        ro_dm['mdl_string'] = self.mdl_string
        ro_dm['object_name'] = self.object_name
        ro_dm['region_name'] = self.region_name
        ro_dm['count_location'] = self.count_location
        ro_dm['rxn_or_mol'] = self.rxn_or_mol
        return ro_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionOutputProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['mdl_string'] = ""
            dm['data_model_version'] = "DM_2015_07_24_2311"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_07_24_2311":
            data_model.flag_incompatible_data_model ( "Upgrade Error: Unable to upgrade MCellReactionOutputProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_07_24_2311":
            data_model.handle_incompatible_data_model ( "Build Error: Unable to upgrade MCellReactionOutputProperty data model to current version." )
        self.name = dm["name"]
        self.molecule_name = dm["molecule_name"]
        self.reaction_name = dm["reaction_name"]
        self.object_name = dm["object_name"]
        self.region_name = dm["region_name"]
        self.count_location = dm["count_location"]
        self.rxn_or_mol = dm["rxn_or_mol"]
        self.mdl_string = dm['mdl_string']

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Output Properties... no collections to remove." )




import cellblender


class MCellReactionOutputPropertyGroup(bpy.types.PropertyGroup):

    rxn_step = PointerProperty ( name="Step",
        type=parameter_system.Parameter_Reference )
    active_rxn_output_index = IntProperty(
        name="Active Reaction Output Index", default=0)
    rxn_output_list = CollectionProperty(
        type=MCellReactionOutputProperty, name="Reaction Output List")
    plot_layout_enum = [
        (' page ', "Separate Page for each Plot", ""),
        (' plot ', "One Page, Multiple Plots", ""),
        (' ',      "One Page, One Plot", "")]
    plot_layout = bpy.props.EnumProperty ( 
        items=plot_layout_enum, name="", 
        description="Select the Page and Plot Layout",
        default=' plot ' )
    plot_legend_enum = [
        ('x', "No Legend", ""),
        ('0', "Legend with Automatic Placement", ""),
        ('1', "Legend in Upper Right", ""),
        ('2', "Legend in Upper Left", ""),
        ('3', "Legend in Lower Left", ""),
        ('4', "Legend in Lower Right", ""),
        # ('5', "Legend on Right", ""), # This appears to duplicate option 7
        ('6', "Legend in Center Left", ""),
        ('7', "Legend in Center Right", ""),
        ('8', "Legend in Lower Center", ""),
        ('9', "Legend in Upper Center", ""),
        ('10', "Legend in Center", "")]
    plot_legend = bpy.props.EnumProperty ( 
        items=plot_legend_enum, name="", 
        description="Select the Legend Display and Placement",
        default='0' )
    combine_seeds = BoolProperty(
        name="Combine Seeds",
        description="Combine all seeds onto the same plot.",
        default=True)
    mol_colors = BoolProperty(
        name="Molecule Colors",
        description="Use Molecule Colors for line colors.",
        default=False)

    def init_properties ( self, parameter_system ):
        self.rxn_step.init_ref (
            parameter_system, "Rxn_Output_Step", user_name="Step", 
            user_expr="", user_units="", user_descr="Step\n"
            "Output reaction data every t seconds.") 

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction Output Panel building Data Model" )
        ro_dm = {}
        ro_dm['data_model_version'] = "DM_2014_10_24_1638"
        ro_dm['rxn_step'] = self.rxn_step.get_expr()
        ro_dm['plot_layout'] = self.plot_layout
        ro_dm['plot_legend'] = self.plot_legend
        ro_dm['combine_seeds'] = self.combine_seeds
        ro_dm['mol_colors'] = self.mol_colors
        ro_list = []
        for ro in self.rxn_output_list:
            ro_list.append ( ro.build_data_model_from_properties(context) )
        ro_dm['reaction_output_list'] = ro_list
        return ro_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionOutputPropertyGroup Data Model" )
        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            dm['rxn_step'] = ""
            dm['data_model_version'] = "DM_2015_05_15_1214"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_05_15_1214":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputPropertyGroup data model to current version." )
            return None

        if "reaction_output_list" in dm:
            for item in dm["reaction_output_list"]:
                if MCellReactionOutputProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_05_15_1214":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionOutputPropertyGroup data model to current version." )
        self.init_properties(context.scene.mcell.parameter_system)
        self.plot_layout = dm["plot_layout"]
        self.plot_legend = dm["plot_legend"]
        self.rxn_step.set_expr ( dm["rxn_step"] )
        self.combine_seeds = dm["combine_seeds"]
        self.mol_colors = dm["mol_colors"]
        while len(self.rxn_output_list) > 0:
            self.rxn_output_list.remove(0)
        if "reaction_output_list" in dm:
            for r in dm["reaction_output_list"]:
                self.rxn_output_list.add()
                self.active_rxn_output_index = len(self.rxn_output_list)-1
                ro = self.rxn_output_list[self.active_rxn_output_index]
                # ro.init_properties(context.scene.mcell.parameter_system)
                ro.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Output Properties..." )
        self.active_rxn_output_index = 0
        for item in self.rxn_output_list:
            item.remove_properties(context)
        self.rxn_output_list.clear()
        print ( "Done removing all Reaction Output Properties." )



    def draw_layout ( self, context, layout ):
        """ Draw the reaction output "panel" within the layout """
        mcell = context.scene.mcell
        ps = mcell.parameter_system

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            self.rxn_step.draw(layout,ps)
            row = layout.row()
            if mcell.molecules.molecule_list:
                col = row.column()
                col.template_list("MCELL_UL_check_reaction_output_settings",
                                  "reaction_output", self,
                                  "rxn_output_list", self,
                                  "active_rxn_output_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.rxn_output_add", icon='ZOOMIN', text="")
                col.operator("mcell.rxn_output_remove", icon='ZOOMOUT', text="")
                # Show molecule, object, and region options only if there is at
                # least one count statement.
                if self.rxn_output_list:
                    rxn_output = self.rxn_output_list[
                        self.active_rxn_output_index]
                    layout.prop(rxn_output, "rxn_or_mol", expand=True)
                    if rxn_output.rxn_or_mol == 'Molecule':
                        layout.prop_search(
                            rxn_output, "molecule_name", mcell.molecules,
                            "molecule_list", icon='FORCE_LENNARDJONES')
                    elif rxn_output.rxn_or_mol =='Reaction':
                        layout.prop_search(
                            rxn_output, "reaction_name", mcell.reactions,
                            "reaction_name_list", icon='FORCE_LENNARDJONES')
                    elif rxn_output.rxn_or_mol == 'MDLString':
                        layout.prop(rxn_output, "mdl_string")
                        layout.prop(rxn_output,"molecule_name")
                        #literal mdl string

                    layout.prop(rxn_output, "count_location", expand=True)
                    # Show the object selector if Object or Region is selected
                    if rxn_output.count_location != "World":
                        layout.prop_search(
                            rxn_output, "object_name", mcell.model_objects,
                            "object_list", icon='MESH_ICOSPHERE')
                        if (rxn_output.object_name and
                                (rxn_output.count_location == "Region")):
                            try:
                                regions = bpy.data.objects[
                                    rxn_output.object_name].mcell.regions
                                layout.prop_search(rxn_output, "region_name",
                                                   regions, "region_list",
                                                   icon='FACESEL_HLT')
                            except KeyError:
                                pass

                    layout.separator()
                    layout.separator()

                    row = layout.row()
                    row.label(text="Plot Reaction Data:",
                              icon='FORCE_LENNARDJONES')

                    row = layout.row()

                    col = row.column()
                    col.prop(self, "plot_layout")

                    col = row.column()
                    col.prop(self, "combine_seeds")

                    row = layout.row()

                    col = row.column()
                    col.prop(self, "plot_legend")

                    col = row.column()
                    col.prop(self, "mol_colors")


                    row = layout.row()
                    button_num = 0
                    num_columns = len(cellblender.cellblender_info[
                        'cellblender_plotting_modules'])
                    if num_columns > 3:
                        num_columns = 2
                    for plot_module in cellblender.cellblender_info[
                            'cellblender_plotting_modules']:
                        mod_name = plot_module.get_name()
                        if (button_num % num_columns) == 0:
                            button_num = 0
                            row = layout.row()
                        col = row.column()
                        col.operator("mcell.plot_rxn_output_generic",
                                     text=mod_name).plotter_button_label = mod_name
                        button_num = button_num + 1

            else:
                row.label(text="Define at least one molecule", icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


