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
This file contains the classes for CellBlender's Reactions.

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
from . import cellblender_utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Reaction Operators:

class MCELL_OT_reaction_add(bpy.types.Operator):
    bl_idname = "mcell.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add a new reaction to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.reactions.reaction_list.add()
        mcell.reactions.active_rxn_index = len(mcell.reactions.reaction_list)-1
        rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
        rxn.init_properties(mcell.parameter_system)
        check_reaction(self, context)
        return {'FINISHED'}


class MCELL_OT_reaction_remove(bpy.types.Operator):
    bl_idname = "mcell.reaction_remove"
    bl_label = "Remove Reaction"
    bl_description = "Remove selected reaction from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.reactions.reaction_list.remove(mcell.reactions.active_rxn_index)
        mcell.reactions.active_rxn_index = mcell.reactions.active_rxn_index-1
        if (mcell.reactions.active_rxn_index < 0):
            mcell.reactions.active_rxn_index = 0

        if mcell.reactions.reaction_list:
            check_reaction(self, context)
        else:
            cellblender_release.update_release_pattern_rxn_name_list()

        return {'FINISHED'}


class MCELL_OT_add_variable_rate_constant(bpy.types.Operator):
    """ Create variable rate constant text object from a file.

    Create a text object from an existing text file that represents the
    variable rate constant. This ensures that the variable rate constant is
    actually stored in the blend. Although, ultimately, this text object will
    be exported as another text file in the project directory when the MDLs are
    exported so it can be used by MCell.
    """

    bl_idname = "mcell.variable_rate_add"
    bl_label = "Add Variable Rate Constant"
    bl_description = "Add a variable rate constant to a reaction."
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        mcell = context.scene.mcell
        rxn = mcell.reactions.reaction_list[
            mcell.reactions.active_rxn_index]

        rxn.load_variable_rate_file ( context, self.filepath )

        return {'FINISHED'}


    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Reaction callback functions


def check_reaction(self, context):
    """Checks for duplicate or illegal reaction. Cleans up formatting."""

    mcell = context.scene.mcell

    #Retrieve reaction
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    for item in rxn.type_enum:
        if rxn.type == item[0]:
            rxtype = item[1]

    status = ""

    # Clean up rxn.reactants only if necessary to avoid infinite recursion.
    reactants = rxn.reactants.replace(" ", "")
    reactants = reactants.replace("+", " + ")
    reactants = reactants.replace("@", " @ ")
    if reactants != rxn.reactants:
        rxn.reactants = reactants

    # Clean up rxn.products only if necessary to avoid infinite recursion.
    products = rxn.products.replace(" ", "")
    products = products.replace("+", " + ")
    if products != rxn.products:
        rxn.products = products

    # Check for duplicate reaction
    rxn.name = ("%s %s %s") % (rxn.reactants, rxtype, rxn.products)
    rxn_keys = mcell.reactions.reaction_list.keys()
    if rxn_keys.count(rxn.name) > 1:
        status = "Duplicate reaction: %s" % (rxn.name)

    # Does the reaction need reaction directionality (i.e. there is at least
    # one surface molecule or a surface class)
    need_rxn_direction = False
    # Are there ever any reactants, products, or surface classes that don't
    # specify reaction directionality?
    ever_no_direction = False
    # Conversely, are there ever any reactants/products/SCs which do?
    ever_direction = False

    # Check syntax of reactant specification
    mol_list = mcell.molecules.molecule_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mol_surf_class_filter = \
        r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
    # Check the syntax of the surface class if one exists
    if rxn.reactants.count(" @ ") == 1:
        need_rxn_direction = True
        reactants_no_surf_class, surf_class = rxn.reactants.split(" @ ")
        match = re.match(mol_surf_class_filter, surf_class)
        if match is None:
            status = "Illegal surface class name: %s" % (surf_class)
        else:
            surf_class_name = match.group(1)
            surf_class_direction = match.group(2)
            if not surf_class_name in surf_class_list:
                status = "Undefined surface class: %s" % (surf_class_name)
            if not surf_class_direction:
                status = ("No directionality specified for surface class: "
                          "%s" % (surf_class_name))
    else:
        reactants_no_surf_class = rxn.reactants
        surf_class = None

    reactants = reactants_no_surf_class.split(" + ")
    for reactant in reactants:
        match = re.match(mol_surf_class_filter, reactant)
        if match is None:
            status = "Illegal reactant name: %s" % (reactant)
            break
        else:
            mol_name = match.group(1)
            mol_direction = match.group(2)
            if not mol_name in mol_list:
                status = "Undefined molecule: %s" % (mol_name)
            else:
                if mol_list[mol_name].type == '2D':
                    need_rxn_direction = True
                if not mol_direction:
                    ever_no_direction = True
                else:
                    ever_direction = True

    # Check syntax of product specification
    if rxn.products == "NULL":
        if rxn.type == 'reversible':
            rxn.type = 'irreversible'
    else:
        products = rxn.products.split(" + ")
        for product in products:
            match = re.match(mol_surf_class_filter, product)
            if match is None:
                status = "Illegal product name: %s" % (product)
                break
            else:
                mol_name = match.group(1)
                mol_direction = match.group(2)
                if not mol_name in mol_list:
                    status = "Undefined molecule: %s" % (mol_name)
                else:
                    if mol_list[mol_name].type == '2D':
                        need_rxn_direction = True
                    if not mol_direction:
                        ever_no_direction = True
                    else:
                        ever_direction = True

    # Is directionality required (i.e. any surface molecules or surface class)?
    # If so, is it missing anywhere in the rxn?
    if need_rxn_direction and ever_no_direction:
        status = "Reaction directionality required (e.g. semicolon after name)"
    # Is reaction directionality specified despite there only being vol. mols?
    if not surf_class and not need_rxn_direction and ever_direction:
        status = "Unneeded reaction directionality"

    # Check for a variable rate constant
    if rxn.variable_rate_switch:
        # Make sure that the file has not been deleted
        if rxn.variable_rate not in bpy.data.texts:
            rxn.variable_rate_valid = False

        # Check if file doesn't exist, isn't UTF8, is a directory, etc
        if not rxn.variable_rate_valid:
            status = ("Variable rate constant is not valid: "
                      "%s" % rxn.variable_rate)
        # Variable rate constants only support irreversible reactions
        elif rxn.variable_rate_valid and rxn.type == 'reversible':
            rxn.type = 'irreversible'

    rxn_name_status = check_reaction_name()
    if rxn_name_status:
        status = rxn_name_status

    rxn.status = status
    cellblender_release.update_release_pattern_rxn_name_list()


def check_reaction_name():
    """ Make sure the reaction name is legal.

    Also make sure that it is available for counting and as a release pattern.

    """

    mcell = bpy.context.scene.mcell
    rxn = mcell.reactions.reaction_list[mcell.reactions.active_rxn_index]
    rxn_name = rxn.rxn_name
    status = ""

    # Check for illegal names
    # (Starts with a letter. No special characters. Can be blank.)
    reaction_name_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)|(^$)"
    m = re.match(reaction_name_filter, rxn_name)
    if m is None:
        status = "Reaction name error: %s" % (rxn_name)

    return status



# Reactions Panel Classes

class MCELL_UL_check_reaction(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_reactions(bpy.types.Panel):
    bl_label = "CellBlender - Define Reactions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.reactions.draw_panel ( context, self )




# Reaction Property Groups

class MCellReactionProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="The Reaction")
    rxn_name = StringProperty(
        name="Reaction Name",
        description="The name of the reaction. "
                    "Can be used in Reaction Output.",
        update=check_reaction)
    reactants = StringProperty(
        name="Reactants", 
        description="Specify 1-3 reactants separated by a + symbol. "
                    "Optional: end with @ surface class. Ex: a; + b; @ sc;",
        update=check_reaction)
    products = StringProperty(
        name="Products",
        description="Specify zero(NULL) or more products separated by a + "
                    "symbol.",
        update=check_reaction)
    type_enum = [
        ('irreversible', "->", ""),
        ('reversible', "<->", "")]
    type = EnumProperty(
        items=type_enum, name="Reaction Type",
        description="A unidirectional/irreversible(->) reaction or a "
                    "bidirectional/reversible(<->) reaction.",
        update=check_reaction)
    variable_rate_switch = BoolProperty(
        name="Enable Variable Rate Constant",
        description="If set, use a variable rate constant defined by a two "
                    "column file (col1=time, col2=rate).",
        default=False, update=check_reaction)
    variable_rate = StringProperty(
        name="Variable Rate", subtype='FILE_PATH', default="")
    variable_rate_valid = BoolProperty(name="Variable Rate Valid",
        default=False, update=check_reaction)


    fwd_rate = PointerProperty ( name="Forward Rate", type=parameter_system.Parameter_Reference )
    bkwd_rate = PointerProperty ( name="Backward Rate", type=parameter_system.Parameter_Reference )


    reactants_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    rxn_type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    products_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    variable_rate_switch_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    rxn_name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def init_properties ( self, parameter_system ):
        self.name = "The_Reaction"
        self.rxn_name = ""
        self.reactants = ""
        self.products = ""
        self.type = 'irreversible'
        self.variable_rate_switch = False
        self.variable_rate = ""
        self.variable_rate_valid = False
        
        helptext = "Forward Rate\n" + \
                   "The units for the reaction rate for uni- and bimolecular reactions is:\n" + \
                   "  [1/s] for unimolecular reactions,\n" + \
                   "  [1/(M * s)] for bimolecular reactions between either\n" + \
                   "      two volume molecules or a volume molecule and a surface molecule,\n" + \
                   "  [um^2 / (N * s)] for bimolecular reactions between two surface molecules."
        self.fwd_rate.init_ref   ( parameter_system, "FW_Rate_Type", user_name="Forward Rate",  user_expr="0", user_units="", user_descr=helptext )
       
        helptext = "Backward Rate\n" + \
                  "The units for the reaction rate for uni- and bimolecular reactions is:\n" + \
                  "  [1/s] for unimolecular reactions,\n" + \
                  "  [1/(M * s)] for bimolecular reactions between either\n" + \
                  "      two volume molecules or a volume molecule and a surface molecule,\n" + \
                  "  [um^2 / (N * s)] for bimolecular reactions between two surface molecules."
        self.bkwd_rate.init_ref  ( parameter_system, "BW_Rate_Type", user_name="Backward Rate", user_expr="",  user_units="s", user_descr=helptext )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Properties... no collections to remove." )

    status = StringProperty(name="Status")


    def build_data_model_from_properties ( self, context ):
        r = self
        r_dict = {}
        r_dict['data_model_version'] = "DM_2014_10_24_1638"
        r_dict['name'] = r.name
        r_dict['rxn_name'] = r.rxn_name
        r_dict['reactants'] = r.reactants
        r_dict['products'] = r.products
        r_dict['rxn_type'] = r.type
        r_dict['variable_rate_switch'] = r.variable_rate_switch
        r_dict['variable_rate'] = r.variable_rate
        r_dict['variable_rate_valid'] = r.variable_rate_valid
        r_dict['fwd_rate'] = r.fwd_rate.get_expr()
        r_dict['bkwd_rate'] = r.bkwd_rate.get_expr()
        variable_rate_text = ""
        if r.type == 'irreversible':
            # Check if a variable rate constant file is specified
            if r.variable_rate_switch and r.variable_rate_valid:
                variable_rate_text = bpy.data.texts[r.variable_rate].as_string()
        r_dict['variable_rate_text'] = variable_rate_text
        return r_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm_dict ):
        # Check that the data model version matches the version for this property group
        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionProperty data model to current version." )
        self.name = dm_dict["name"]
        self.rxn_name = dm_dict["rxn_name"]
        self.reactants = dm_dict["reactants"]
        self.products = dm_dict["products"]
        self.type = dm_dict["rxn_type"]
        self.variable_rate_switch = dm_dict["variable_rate_switch"]
        self.variable_rate = dm_dict["variable_rate"]
        self.variable_rate_valid = dm_dict["variable_rate_valid"]
        self.fwd_rate.set_expr ( dm_dict["fwd_rate"] )
        self.bkwd_rate.set_expr ( dm_dict["bkwd_rate"] )
        # TODO: The following logic doesn't seem right ... we might want to check it!!
        if self.type == 'irreversible':
            # Check if a variable rate constant file is specified
            if self.variable_rate_switch and self.variable_rate_valid:
                variable_rate_text = bpy.data.texts[self.variable_rate].as_string()
                self.store_variable_rate_text ( context, self.variable_rate, dm_dict["variable_rate_text"] )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def store_variable_rate_text ( self, context, text_name, rate_string ):
        """ Create variable rate constant text object from text string.

        Create a text object from an existing text string that represents the
        variable rate constant. This ensures that the variable rate constant is
        actually stored in the blend. Although, ultimately, this text object will
        be exported as another text file in the project directory when the MDLs are
        exported so it can be used by MCell."""
        print ( "store_variable_rate_text ( " + text_name + ", " + rate_string + " )" )
        texts = bpy.data.texts
        # Overwrite existing text objects.
        # XXX: Add warning.
        if text_name in texts:
            texts.remove(texts[text_name])
            print ( "Found " + text_name + ", and removed from texts" )

        # Create the text object from the text string
        try:
            text_object = texts.new(text_name)
            # Should add in some simple error checking
            text_object.write(rate_string)
            self.variable_rate_valid = True
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            self.variable_rate_valid = False
        

    def load_variable_rate_file ( self, context, filepath ):
        # Create the text object from the text file
        self.variable_rate = os.path.basename(filepath)
        try:
            with open(filepath, "r") as rate_file:
                rate_string = rate_file.read()
                self.store_variable_rate_text ( context, self.variable_rate, rate_string )
        except (UnicodeDecodeError, IsADirectoryError, FileNotFoundError):
            self.variable_rate_valid = False


    def write_to_mdl_file ( self, context, out_file, filedir ):
        out_file.write("  %s " % (self.name))

        ps = context.scene.mcell.parameter_system

        if self.type == 'irreversible':
            # Use a variable rate constant file if specified
            if self.variable_rate_switch and self.variable_rate_valid:
                variable_rate_name = self.variable_rate
                out_file.write('["%s"]' % (variable_rate_name))
                variable_rate_text = bpy.data.texts[variable_rate_name]
                variable_out_filename = os.path.join(
                    filedir, variable_rate_name)
                with open(variable_out_filename, "w", encoding="utf8",
                          newline="\n") as variable_out_file:
                    variable_out_file.write(variable_rate_text.as_string())
            # Use a single-value rate constant
            else:
                out_file.write("[%s]" % (self.fwd_rate.get_as_string_or_value(
                               ps.panel_parameter_list,ps.export_as_expressions)))    
        else:
            out_file.write(
                "[>%s, <%s]" % (self.fwd_rate.get_as_string_or_value(
                ps.panel_parameter_list, ps.export_as_expressions),
                self.bkwd_rate.get_as_string_or_value(ps.panel_parameter_list,
                ps.export_as_expressions)))

        if self.rxn_name:
            out_file.write(" : %s\n" % (self.rxn_name))
        else:
            out_file.write("\n")


#Custom Properties

class RxnStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell String Property with name \"" + self.name + "\" ... no collections to remove." )
        pass




class MCellReactionsListProperty(bpy.types.PropertyGroup):
    reaction_list = CollectionProperty(
        type=MCellReactionProperty, name="Reaction List")
    active_rxn_index = IntProperty(name="Active Reaction Index", default=0)
    reaction_name_list = CollectionProperty(
        type=RxnStringProperty, name="Reaction Name List")
    # plot_command = StringProperty(name="", default="")      # TODO: This may not be needed ... check on it

    def build_data_model_from_properties ( self, context ):
        print ( "Reaction List building Data Model" )
        react_dm = {}
        react_dm['data_model_version'] = "DM_2014_10_24_1638"
        react_list = []
        for r in self.reaction_list:
            react_list.append ( r.build_data_model_from_properties(context) )
        react_dm['reaction_list'] = react_list
        return react_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReactionsListProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReactionsListProperty data model to current version." )
            return None

        if "reaction_list" in dm:
            for item in dm["reaction_list"]:
                if MCellReactionProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReactionsListProperty data model to current version." )
        while len(self.reaction_list) > 0:
            self.reaction_list.remove(0)
        if "reaction_list" in dm:
            for r in dm["reaction_list"]:
                self.reaction_list.add()
                self.active_rxn_index = len(self.reaction_list)-1
                rxn = self.reaction_list[self.active_rxn_index]
                rxn.init_properties(context.scene.mcell.parameter_system)
                rxn.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    def remove_properties ( self, context ):
        print ( "Removing all Reaction Properties..." )
        for item in self.reaction_list:
            item.remove_properties(context)
        self.reaction_list.clear()
        for item in self.reaction_name_list:
            item.remove_properties(context)
        self.reaction_name_list.clear()
        self.active_rxn_index = 0
        print ( "Done removing all Reaction Properties." )


    def draw_layout(self, context, layout):
        # layout = self.layout
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            row = layout.row()
            if mcell.molecules.molecule_list:
                col = row.column()
                col.template_list("MCELL_UL_check_reaction", "define_reactions",
                                  self, "reaction_list",
                                  self, "active_rxn_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.reaction_add", icon='ZOOMIN', text="")
                col.operator("mcell.reaction_remove", icon='ZOOMOUT', text="")
                if len(self.reaction_list) > 0:
                    rxn = self.reaction_list[
                        self.active_rxn_index]

                    helptext = "Reactants\nThe reactants may contain one, two, or three molecule names\n" + \
                               "separated with the plus ('+') sign. Molecules in the reactants\n" + \
                               "list may also contain orientation marks (' or , or ;) as needed."
                    ps.draw_prop_with_help ( layout, "Reactants:", rxn, "reactants", "reactants_show_help", rxn.reactants_show_help, helptext )

                    helptext = "Reaction Type\n  ->   Unidirectional/Irreversible Reaction\n" + \
                               "  <->  Bidirectional/Reversible Reaction"
                    ps.draw_prop_with_help ( layout, "Reaction Type:", rxn, "type", "rxn_type_show_help", rxn.rxn_type_show_help, helptext )

                    helptext = "Products\nThe products list may contain an arbitrary number of\n" + \
                               "molecule names separated with the plus ('+') sign.\n" + \
                               "Molecules may also use NULL to specify no products.\n" + \
                               "Molecules in the products list may also contain orientation\n" + \
                               "marks  (' or , or ;) as needed."
                    ps.draw_prop_with_help ( layout, "Products:", rxn, "products", "products_show_help", rxn.products_show_help, helptext )

                    helptext = "Variable Rate Flag\n" + \
                               "When enabled, the reaction rate is given as a function of time\n" + \
                               "in the form of a 2 column table contained in a text file.\n" + \
                               "The first column in the file specifies the time (in seconds),\n" + \
                               "and the second column contains the rate at that time.\n" + \
                               " \n" + \
                               "When enabled, the normal rate constants will be replaced with\n" + \
                               "a file selection control that will allow you to navigate to the\n" + \
                               "file containing the two columns."
                    ps.draw_prop_with_help ( layout, "Enable Variable Rate", rxn, "variable_rate_switch", "variable_rate_switch_show_help", rxn.variable_rate_switch_show_help, helptext )

                    if rxn.variable_rate_switch:
                        layout.operator("mcell.variable_rate_add", icon='FILESEL')
                        # Do we need these messages in addition to the status
                        # message that appears in the list? I'll leave it for now.
                        if not rxn.variable_rate:
                            layout.label("Rate file not set", icon='UNPINNED')
                        elif not rxn.variable_rate_valid:
                            layout.label("File/Permissions Error: " +
                                rxn.variable_rate, icon='ERROR')
                        else:
                            layout.label(
                                text="Rate File: " + rxn.variable_rate,
                                icon='FILE_TICK')
                    else:
                        #rxn.fwd_rate.draw_in_new_row(layout)
                        rxn.fwd_rate.draw(layout,ps)
                        if rxn.type == "reversible":
                            #rxn.bkwd_rate.draw_in_new_row(layout)
                            rxn.bkwd_rate.draw(layout,ps)

                    helptext = "Reaction Name\nReactions may be named to be referred to by\n" + \
                               "count statements or reaction driven molecule release / placement."
                    ps.draw_prop_with_help ( layout, "Reaction Name:", rxn, "rxn_name", "rxn_name_show_help", rxn.rxn_name_show_help, helptext )

                    reactants = rxn.reactants.split(" + ")
                    products = rxn.products.split(" + ")
                    mol_list = mcell.molecules.molecule_list
                    bnglreactant = []
                    bnglproduct = []
                    for reactant in reactants:
                        reactantStr = reactant
                        if len(reactantStr) > 0:
                            while reactantStr[-1] in ["'", ",", ";"]:
                                reactantStr = reactantStr[:-1]
                        if reactantStr in mol_list:
                            tmpStr = mol_list[reactantStr].bnglLabel if mol_list[reactantStr].bnglLabel != '' else mol_list[reactantStr].name
                            bnglreactant.append(tmpStr)
                    for product in products:
                        productStr = product
                        if len(productStr) > 0:
                            while productStr[-1] in ["'", ",", ";"]:
                                productStr = productStr[:-1]

                        if productStr in mol_list:
                            tmpStr = mol_list[productStr].bnglLabel if mol_list[productStr].bnglLabel != '' else mol_list[productStr].name
                            bnglproduct.append(tmpStr)

                    reactant_string = ' + '.join(bnglreactant) + ' -> '
                    product_string = ' + '.join(bnglproduct)

                    if len(product_string) > 0:
                        row = layout.row()
                        row2 = layout.row()

                        row.label(text="BNGL reaction: {0}".format(reactant_string), icon='BLANK1')
                        row2.label(text="{0}".format(product_string), icon='BLANK1')

            else:
                row.label(text="Define at least one molecule", icon='ERROR')

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

