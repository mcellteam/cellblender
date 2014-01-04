"""
This program demonstrates a parameter space based on Blender's native properties.
Much of the code was borrowed from the previous ParameterSpace.py program.
"""

# Check Version numbers with: bzr log --line --forward

#----------------------------------------------------------
# File Property_Params.py
#----------------------------------------------------------
#

# Addon info

bl_info = {
  "version": "0.50",
  "name": "Property Parameters",
  'author': 'Bob Kuczewski',
  "location": "Properties > Scene",
  "category": "Blender Experiments"
  }

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
  import imp
  print("Reloaded Parameters")
else:
  print("Imported Parameters")


import bpy
from bpy.props import *

from math import *
from random import uniform, gauss
import parser
import re
import token
import symbol
import sys


def threshold_print ( thresh, s ):
    # Items will print if the user selected level is greater than the level in the print statement (thresh)
    #  User setting = 100 -> print everything
    #  User setting =   0 -> print nothing
    if thresh < bpy.context.scene.app.debug_level:
        print ( s )

def print_info_about_self ( self, thresh, context ):
    threshold_print ( thresh, "Info:" )
    threshold_print ( thresh, "  Self: " + str(self) )
    threshold_print ( thresh, "    Self contains " + str(dir(self)) )
    threshold_print ( thresh, "__qualname__ = " + str(self.__qualname__) )
    threshold_print ( thresh, "name = \"" + str(self.name) + "\"" )
    threshold_print ( thresh, "rna_type = \"" + str(self.rna_type) + "\"" )


def get_path_to_parent(self_object):
    """ Return the Blender class path to the parent object with regard to the Blender Property Tree System """
    path_to_self = "bpy.context.scene." + self_object.path_from_id()
    path_to_parent = path_to_self[0:path_to_self.rfind(".")]
    return path_to_parent

def get_parent(self_object):
    """ Return the parent Blender object with regard to the Blender Property Tree System """
    path_to_parent = get_path_to_parent(self_object)
    parent = eval(path_to_parent)
    return parent



##### vvvvvvvvv   General Parameter Code   vvvvvvvvv

class APP_OT_add_parameter(bpy.types.Operator):
    bl_idname = "app.add_parameter"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.app.general_parameters.add_parameter(context)
        return {'FINISHED'}
        

class APP_OT_remove_parameter(bpy.types.Operator):
    bl_idname = "app.remove_parameter"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        status = context.scene.app.general_parameters.remove_active_parameter(context)
        if status != "":
            # One of: 'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY'
            self.report({'ERROR'}, status)
        return {'FINISHED'}


class APP_UL_draw_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        app = context.scene.app
        par = app.general_parameters.parameter_list[index]
        disp = par.name + " = " + par.expr
        # Try to force None to be 0 ... doesn't seem to work!!
        if par.value == None:
            par.value = "0"
        disp = disp + " = " + par.value
        if par.unit != "":
            disp = disp + " (" + par.unit + ")"
        icon = 'FILE_TICK'
        if not par.valid:
            icon = 'ERROR'
        if item.status:
            icon = 'ERROR'
            disp = disp + "  <= " + item.status
        layout.label(disp, icon=icon)

  
class APP_PT_general_parameters(bpy.types.Panel):
    bl_label = "General Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        threshold_print (99, "Panel Draw with context.scene.app = " + str(context.scene.app) + " of type " + str(type(context.scene.app)) )
        app = context.scene.app

        layout = self.layout
        row = layout.row()
        if app.general_parameters.param_group_error == "":
            row.label(text="Defined Parameters:", icon='FORCE_LENNARDJONES')
        else:
            row.label(text=app.general_parameters.param_group_error, icon='ERROR')

        row = layout.row()
        col = row.column()
        col.template_list("APP_UL_draw_parameter", "general_parameters",
                          app.general_parameters, "parameter_list",
                          app.general_parameters, "active_par_index", rows=5)
        col = row.column(align=True)
        col.operator("app.add_parameter", icon='ZOOMIN', text="")
        col.operator("app.remove_parameter", icon='ZOOMOUT', text="")
        if len(app.general_parameters.parameter_list) > 0:
            par = app.general_parameters.parameter_list[app.general_parameters.active_par_index]
            layout.prop(par, "name")
            if len(par.pending_expr) > 0:
                layout.prop(par, "expr")
                row = layout.row()
                row.label(text="Undefined Expression: " + str(par.pending_expr), icon='ERROR')
            else:
                layout.prop(par, "expr")
            layout.prop(par, "unit")
            layout.prop(par, "desc")


# Callbacks for Property updates appear to require global (non-member) functions
# This is circumvented by simply calling the associated member function passed as self

def update_parameter_name ( self, context ):
    """ The "self" passed in is a GeneralParameterProperty object. """
    self.update_name ( context )

def update_parameter_expression ( self, context ):
    """ The "self" passed in is a GeneralParameterProperty object. """
    self.update_expression ( context )


# These are the properties that make up the general parameter classes

class GeneralParameterProperty(bpy.types.PropertyGroup):

    """An instance of this class exists for every general parameter"""

    id = IntProperty(name="ID", default=0, description="Unique ID for each parameter")
    name = StringProperty(name="Name", default="Parameter", description="Unique name for this parameter", update=update_parameter_name)
    expr = StringProperty(name="Expression", default="0", description="Expression to be evaluated for this parameter", update=update_parameter_expression)
    value = StringProperty(name="Value", default="0", description="Current evaluated value for this parameter" )

    last_name = StringProperty(name="Last Name", default="", description="Last value of name (used for comparison to detect changes)")
    last_expr = StringProperty(name="Last Expression", default="", description="Last value of expr (used for comparison to detect changes)")
    last_value = StringProperty(name="Last Value", default="", description="Last value of value (used for comparison to detect changes)")

    id_expr_str = StringProperty(name="EncodedExpressionString", default="", description="Parsed and Encoded Expression list stored as a string")
    
    pending_expr = StringProperty(name="PendingExpression", default="", description="Expression as entered with errors pending correction")

    valid = BoolProperty(default=False) # Transient value used when evaluating all parameters to flag which have been updated

    initialized = BoolProperty(default=False) # Set to true by "set_defaults"

    unit = StringProperty(name="Units", default="", description="Parameter Unit")
    desc = StringProperty(name="Description", default="", description="Parameter Description")

    status = StringProperty(name="Status", default="")  # Normal="", Otherwise contains any error messages
    
    def set_defaults ( self ):
        self.name = "Parameter_" + str(self.id)
        self.expr = "0"
        self.value = "0"
        
        self.last_name = self.name
        self.last_expr = self.expr
        self.last_value = self.value

        self.valid = True
        self.status = ""
        self.initialized = True

    def print_parameter(self, thresh, prefix=""):
        threshold_print ( thresh, prefix + self.name + " (#" + str(self.id) + ") = " + self.expr + " = " + self.id_expr_str + " = " + str(self.value) )

    def print_details(self, thresh, prefix=""):
        threshold_print ( thresh, prefix + "ID = " + str(self.id) )
        threshold_print ( thresh, prefix + "  Name  = " + self.name + ", previously " + self.last_name )
        threshold_print ( thresh, prefix + "  Expr  = " + self.expr + ", previously " + self.last_expr )
        threshold_print ( thresh, prefix + "  IDExp = " + self.id_expr_str )
        threshold_print ( thresh, prefix + "  _expr = " + self.pending_expr )
        threshold_print ( thresh, prefix + "  Value = " + str(self.value) )
        threshold_print ( thresh, prefix + "  Valid = " + str(self.valid) )
        threshold_print ( thresh, prefix + "  Init  = " + str(self.initialized) )
        threshold_print ( thresh, prefix + "  Stat  = " + str(self.status) )

    def update_name ( self, context ):
        """
        Update the entire parameter system based on a parameter's name being changed.
        This function is called with a "self" which is a GeneralParameterProperty
        whenever the name is changed (either programatically or via the GUI).
        This function needs to force the redraw of all parameters that depend
        on this one so their expressions show the new name as needed.

        The "self" passed in is a GeneralParameterProperty object.
        """
        threshold_print ( 30, "==================================================================" )
        threshold_print ( 30, "Updating name for parameter " + self.name )
        if (self.name == self.last_name):
            threshold_print ( 30, "Names are identical, no change made" )
        else:
            threshold_print ( 30, "Names are different, ask parent to change name checking for duplicates" )
            gen_params = get_parent ( self )
            gen_params.name_update_in_progress = True
            
            gen_params.name_change(self)
            
            # Is this needed for a name change?
            gen_params.eval_all_any_order()

            # Update all the panel parameters based on all the general parameters
            plist = get_numeric_parameter_list ( None, [], debug=False )
            for p in plist:
                # Fix any potential broken references
                fixed_expression = gen_params.fix_broken_references ( p.param_data.ID_expression )
                if fixed_expression != p.param_data.ID_expression:
                    # Re-evaluate the fixed expression
                    threshold_print ( 30, "Fixing reference from " + str(p.param_data.ID_expression) + " to " + fixed_expression )
                    p.param_data.ID_expression = fixed_expression

                    value = gen_params.eval_panel_param_ID_expr ( p.param_data.ID_expression )
                    if value == None:
                        threshold_print ( 5, "Invalid expression detected in update_name!!!" )
                        p.param_data.status = "Invalid Expression"
                    else:
                        if p.param_data.value != value:
                            p.param_data.value = value
                        p.param_data.status = ""
                    
                    p.param_data.expression = gen_params.translate_panel_param_ID_expr ( p.param_data.ID_expression )
                # Translate the expression to reflect the new name
                threshold_print ( 30, "Translating " + str(p.param_data.ID_expression) + " during update_name" )
                expr = gen_params.translate_panel_param_ID_expr ( p.param_data.ID_expression )
                if p.param_data.expression != expr:
                    p.param_data.expression = expr
            gen_params.name_update_in_progress = False

        threshold_print ( 30, "Done updating name for parameter " + self.name )
        threshold_print ( 30, "==================================================================" )
        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

    def update_expression ( self, context ):
        """ 
        Update the entire parameter system based on a parameter's expression being changed.
        This function is called with a "self" which is a GeneralParameterProperty
        whenever the string expression is changed (either programatically or via the GUI).
        This function needs to force the redraw of all parameters that depend on this
        one so their values are updated as needed.

        The "self" passed in is a GeneralParameterProperty object.
        """
        threshold_print ( 30, "==================================================================" )
        threshold_print ( 30, "Inside update_expression with self = " + str(self) )

        gen_params = get_parent ( self )

        if gen_params.name_update_in_progress:
            threshold_print ( 30, "update_expression not executed because name update is in progress" )
            return

        status = gen_params.expression_change(self)
        if len(status) > 0:
            print ( "Should report this error: " + status )
            # Can't report without being an "operator" and this is through a callback
            #self.report({'ERROR'}, status)
            pass

        # Is this needed?   gen_params.eval_all_any_order()

        threshold_print ( 30, "Inside update_expression, calling print_all_general_parameters()" )
        gen_params.print_all_general_parameters(30)

        plist = get_numeric_parameter_list ( None, [], debug=False )

        for p in plist:
            # Create a string encoded version of the expression (like "#1~+~3~*~(~#2~+~7.0~)")
            id_expr = gen_params.parse_panel_param_expr ( p.param_data.expression )
            threshold_print ( 30, "Inside update_expression, id_expr = " + str(id_expr) )
            if p.param_data.ID_expression != id_expr:
                p.param_data.ID_expression = id_expr
                threshold_print ( 30, "Changing self.ID_expression to " + str(p.param_data.ID_expression) )
            expr = gen_params.translate_panel_param_ID_expr ( p.param_data.ID_expression )
            if p.param_data.expression != expr:
                p.param_data.expression = expr
            value = gen_params.eval_panel_param_ID_expr ( p.param_data.ID_expression )
            if p.param_data.value != value:
                p.param_data.value = value
        threshold_print ( 30, "Done updating expression for parameter " + self.name )
        threshold_print ( 30, "==================================================================" )
        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})


class ParametersPropertyGroup(bpy.types.PropertyGroup):
    """This is the class that encapsulates a group (or list) of general purpose parameters"""
    parameter_list = CollectionProperty(type=GeneralParameterProperty, name="Parameters List")
    active_par_index = IntProperty(name="Active Parameter", default=0)
    param_group_error = StringProperty( default="", description="Error Message for Entire Parameter Group")
    next_id = IntProperty(name="Counter for Unique Parameter IDs", default=1)  # Start ID's at 1 to confirm initialization
    name_update_in_progress = BoolProperty(default=False)  # Used to disable expression evaluation when names are being changed
    # parameter_space_string = StringProperty ( name="ParameterSpace", default="", description="ParameterSpace object pickled as a string" )
    
    """
      String encoding of expression lists:
      
      Rules:
        The tilde character (~) separates all terms
        Any term that does not start with # is a string literal
        Any term that starts with #? is an undefined parameter name
        Any term that starts with # followed by an integer is a parameter ID

      Example:
        Parameter 'a' has an ID of 1
        Parameter 'b' has an ID of 2
        Parameter 'c' is undefined
        Original Expression:  a + 5 + b + c
          Expression as a List: [1, '+', '5', '+', 2, '+', None, 'c' ]
          Expression as string:  #1~+~5~+~#2~+~#?c
    """
    
    def get_term_sep (self):
        return ( "~" )    # This is the string used to separate terms in an expression. It should be illegal in whatever syntax is being parsed.

    def UNDEFINED_NAME(self):
        return ( "   (0*1111111*0)   " )   # This is a string that evaluates to zero, but is easy to spot in expressions
    
    def get_expression_keywords(self):
        return ( { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' } )

    def encode_expr_list_to_str ( self, expr_list ):
        """ Turns an expression list into a string that can be stored as a Blender StringProperty """
        term_sep = self.get_term_sep()
        expr_str = ""
        next_is_undefined = False
        for e in expr_list:
            if next_is_undefined:
                expr_str += term_sep + '#?' + e
                next_is_undefined = False
            else:
                if type(e) == type(None):
                    next_is_undefined = True
                elif type(e) == int:
                    expr_str += term_sep + "#" + str(e)
                elif type(e) == type("a"):
                    expr_str += term_sep + e
                else:
                    threshold_print ( 0, "Unexepected type while encoding list: " + str(expr_list) )

        if len(expr_str) >= len(term_sep):
            # Remove the first term_sep string (easier here than checking above)
            expr_str = expr_str[len(term_sep):]
        return expr_str


    def decode_str_to_expr_list ( self, expr_str ):
        """ Recovers an expression list from a string that has been stored as a Blender StringProperty """
        expr_list = []
        terms = expr_str.split(self.get_term_sep())
        threshold_print ( 90, "   ...breaking into terms: " + str(terms) )
        for e in terms:
            threshold_print ( 90, "  ...checking term: " + str(e) )
            if len(e) > 0:
                threshold_print ( 90, "  ...storing term: " + str(e) )
                if e[0] == '#':
                    if (len(e) > 1) and (e[1] == '?'):
                        expr_list = expr_list + [None] + [e[2:]]
                    else:
                        expr_list = expr_list + [int(e[1:])]
                else:
                    expr_list = expr_list + [e]
        return expr_list


    def print_all_general_parameters ( self, thresh, prefix="" ):
        """ Prints all general parameters based on comparison to a user-adjustable threshold """
        threshold_print ( thresh, prefix + "There are " + str(len(self.parameter_list)) + " general parameters defined" )
        threshold_print ( thresh, prefix + "  [ name (#id) = expr = idexpr = value ]" )
        for p in self.parameter_list:
            p.print_parameter( thresh, prefix=prefix+"    " )


    def fix_broken_references ( self, id_expr_str ):
        """ Attempts to fix any broken references in this expression by searching for names """
        if "#?" in id_expr_str:
            # This indicates that there is at least one broken reference in the string, so convert to a list and fix
            expr_list = self.decode_str_to_expr_list ( id_expr_str )
            fixed_list = []
            last_none = False
            for term in expr_list:
                if last_none:
                    # The previous term was none, so try to evaluate this term as a name
                    found = False
                    for q in self.parameter_list:
                        if term.strip() == q.name.strip():
                            # Add the id to the list as an integer index
                            fixed_list.append ( int(q.id) )
                            found = True
                            break
                    if not found:
                        # The name wasn't found, so keep it as an undefined name
                        fixed_list.append ( None )
                        fixed_list.append ( term )
                    last_none = False
                elif term == None:
                    # Flag the next term as a name to try to evaluate
                    last_none = True
                else:
                    # Just add this term to the list
                    fixed_list.append ( term )
            return ( self.encode_expr_list_to_str(fixed_list) )
        else:
            return ( id_expr_str )

    def fix_all_broken_references ( self ):
        """ Attempts to fix all broken references """
        for p in self.parameter_list:
            p.id_expr_str = self.fix_broken_references ( p.id_expr_str )


    def build_name_ID_dict ( self ):
        """ Builds a dictionary mapping parameter names to their IDs """
        name_ID_dict = {}
        for p in self.parameter_list:
            name_ID_dict.update ( { p.name : p.id } )
        return name_ID_dict

    def build_ID_name_dict ( self ):
        """ Builds a dictionary mapping parameter IDs to their names """
        ID_name_dict = {}
        for p in self.parameter_list:
            ID_name_dict.update ( { p.id : p.name } )
        return ID_name_dict

    def build_ID_value_dict ( self ):
        """ Builds a dictionary mapping parameter IDs to their values """
        ID_value_dict = {}
        for p in self.parameter_list:
            ID_value_dict.update ( { p.id : p.value } )
        return ID_value_dict

    def load_ID_value_dict ( self, ID_value_dict, ID_valid_dict ):
        """ Uses a Python dictionary to update values into the parameter properties """
        for p in self.parameter_list:
            if p.id in ID_value_dict:
                p.value = ID_value_dict[p.id]
            if p.id in ID_valid_dict:
                if ID_valid_dict[p.id]:
                    p.status = ""
                else:
                    p.status = "Evaluation Error"

    def build_ID_valid_dict ( self, is_valid ):
        """ Builds a dictionary mapping each parameter ID to the is_valid value """
        ID_valid_dict = {}
        for p in self.parameter_list:
            ID_valid_dict.update ( { p.id : is_valid } )
        return ID_valid_dict

    def build_depend_list_dict ( self ):
        """ Builds a dictionary containing ID:[dependency_list] pairs for all parameters """
        dep_list_dict = {}
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            dep_list_p = []
            for e in expr_list:
                if (type(e) == int) or (e == None):
                    dep_list_p = dep_list_p + [e]
            dep_list_dict.update ( { p.id : dep_list_p } )
        return dep_list_dict

    def used_by_other_general_parameters ( self, id ):
        """ Return a boolean reflecting whether any general parameters use this parameter id (True) or not (False) """
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            if id in expr_list:
                return True
        return False

    def used_by_these_general_parameters ( self, id ):
        """ Return a string of names of any general parameters that use this parameter id """
        name_list = ""
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            if id in expr_list:
                if len(name_list) > 0:
                    name_list = name_list + ","
                name_list = name_list + p.name
        return name_list

    def used_by_panel_parameters ( self, id ):
        """ Return a boolean reflecting whether any panel parameters use this parameter id (True) or not (False) """
        plist = get_numeric_parameter_list ( None, [] )
        for p in plist:
            expr_list = self.decode_str_to_expr_list ( p.get_ID_expression() )
            if id in expr_list:
                return True
        return False

    def used_by_these_panel_parameters ( self, id ):
        """ Return a string of names of any panel parameters that use this parameter id """
        name_list = ""
        plist = get_numeric_parameter_list ( None, [] )
        plist_names = str(plist)[1:-1].split(",")
        for i in range(len(plist)):
            p = plist[i]
            expr_list = self.decode_str_to_expr_list ( p.get_ID_expression() )
            if id in expr_list:
                if len(name_list) > 0:
                    name_list = name_list + ","
                name_list = name_list + plist_names[i].split(".")[-1]
        return name_list

    def used_by_any_other_parameters ( self, id ):
        return self.used_by_other_general_parameters(id) | self.used_by_panel_parameters(id)

    def used_by_these_other_parameters ( self, id ):
        gpu = self.used_by_these_general_parameters(id)
        ppu = self.used_by_these_panel_parameters(id)
        apu = ""
        if (len(gpu) > 0) and (len(ppu) > 0):
            apu = gpu + "," + ppu
        else:
            apu = gpu + ppu
        return apu


    def build_ID_pyexpr_dict ( self, ID_name_dict ):
        """ Construct a dictionary containing python executable string representations of the expressions by substituting symbols for IDs """
        threshold_print ( 90, "Inside build_ID_pyexpr_dict ... " )
        expression_keywords = self.get_expression_keywords()
        ID_pyexpr_dict = {}
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            expr = ""
            if None in expr_list:
                expr = None
            else:
                for token in expr_list:
                    if type(token) == int:
                        # This is an integer parameter ID, so look up the variable name to concatenate
                        if token in ID_name_dict:
                            expr = expr + ID_name_dict[token]
                        else:
                            # In previous versions, this case might have defined a new parameter here.
                            # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                            #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                            threshold_print ( 1, "build_ID_pyexpr_dict did not find " + str(token) + " in " + str(ID_name_dict) + ", adding an undefined name flag to " + expr )
                            expr = expr + self.UNDEFINED_NAME()
                    else:
                        # This is a string so simply concatenate it after translation as needed
                        if token in expression_keywords:
                            expr = expr + expression_keywords[token]
                        else:
                            expr = expr + token
            ID_pyexpr_dict.update ( { p.id : expr } )
        return ID_pyexpr_dict


    def build_expr_str ( self, encoded_ID_expr, ID_name_dict ):
        """ Translate an encoded ID expression string into a human-readable expression string with respect to current parameters """
        threshold_print ( 30, "Inside build_expr_str ... translating " + str(encoded_ID_expr) )
        threshold_print ( 30, "  using dictionary: " + str(ID_name_dict) )
        new_expr = ""
        expr_list = self.decode_str_to_expr_list ( encoded_ID_expr )
        next_is_undefined = False
        for token in expr_list:
            if token == None:
                next_is_undefined = True
            elif type(token) == int:
                # This is an integer parameter ID, so look up the variable name to concatenate
                if token in ID_name_dict:
                    new_expr = new_expr + ID_name_dict[token]
                else:
                    # In previous versions, this case might have defined a new parameter here.
                    # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                    threshold_print ( 1, "build_expr_str did not find " + str(token) + " in " + str(ID_name_dict) + ", adding an undefined name flag to " + new_expr )
                    new_expr = new_expr + self.UNDEFINED_NAME()
            else:
                # This is a string so simply concatenate it
                if next_is_undefined:
                    new_expr = new_expr + token
                    next_is_undefined = False
                else:
                    new_expr = new_expr + token

        threshold_print ( 30, "Returning from build_exp_str with     " + str(new_expr) )
        return new_expr


    def name_change ( self, param ):
        """ Change the name of a parameter and reflect the change in all expressions. This does not change any values. """
        threshold_print ( 30, "ParametersPropertyGroup.name_change() called by parameter " + param.name + ":" )
        param.print_details ( 30, prefix="  " )
        threshold_print ( 30, "  All other parameters:" )
        for p in self.parameter_list:
            p.print_details( 30, prefix="    " )
        # Assume name is OK, then test for various illegal conditions
        name_ok = True
        # Check to see if the new name is legal
        if not param.name.isidentifier():
            name_ok = False
        # Check to see if the new name already exists
        for p in self.parameter_list:
            p.print_details( 40, prefix="  " )
            if param.name == p.name:
                if param != p:
                    name_ok = False
                    threshold_print ( 20, " Name conflict between " + param.name + " and " + p.name )
                    break
        if not name_ok:
            threshold_print ( 0, "Error: Name is not legal or duplicates another name, reverting to previous" )
            param.name = param.last_name
        else:
            param.last_name = param.name
            # Update all parameter expressions to reflect the new name
            ID_name_dict = self.build_ID_name_dict()
            for p in self.parameter_list:
                threshold_print ( 30, "Inside name_change, building a new expression from " + p.id_expr_str + " and the current ID_name_dict" )
                new_expr = self.build_expr_str ( p.id_expr_str, ID_name_dict )
                # To prevent infinite recursion, only update the expression if it differs from the current one
                if p.expr != new_expr:
                    # The expression differs, so change it. NOTE: This triggers an update of the parameter!!
                    p.expr = new_expr
        # Re-evaluate all the parameters to force them to redraw their expressions
        self.eval_all_any_order()
        # Note that updating of the panel parameters is done after calling this function


    def expression_change ( self, param ):
        """ Change the expression of a parameter and reflect the change in all expressions. This can change values. """
        threshold_print ( 60, "ParametersPropertyGroup.expression_change() called by parameter " + param.name + ":" )
        status = ""
        expr_list = self.parse_param_expr ( param.expr )
        if None in expr_list:
            param.status = "Undefined variables in " + str(param.expr)
            threshold_print ( 1, "Undefined variables in expression: " + param.expr )
        else:
            param.status = ""
        # Store the ID expression string back in the parameter
        param.id_expr_str = self.encode_expr_list_to_str ( expr_list )
        new_expr = self.translate_panel_param_ID_expr ( param.id_expr_str )
        if param.expr != new_expr:
            param.expr = new_expr
        threshold_print ( 60, "After update: expr = " + param.expr + ", id_expr = " + param.id_expr_str )
        # Re-evaluate all the parameters
        self.eval_all_any_order()
        return status


    def parse_panel_param_expr ( self, panel_param_expr ):
        """ Convert a string expression into an encoded ID expression string with respect to current parameters """
        return self.encode_expr_list_to_str ( self.parse_param_expr(panel_param_expr) )

    def translate_panel_param_ID_expr ( self, panel_param_ID_expr ):
        """ Translate a panel parameter's encoded ID expression into a string for display """
        threshold_print ( 30, "Inside translate_panel_param_ID_expr: Translating expression " + str(panel_param_ID_expr ) )
        return self.build_expr_str ( panel_param_ID_expr, self.build_ID_name_dict() )

    def eval_panel_param_ID_expr ( self, panel_param_ID_expr ):
        """ Evaluate a panel parameter's ID expression (like "#1~+~3~*~(~#2~+~7.0~)") into a numeric value or None if invalid """
        threshold_print ( 30, "Evaluating ID expression " + str(panel_param_ID_expr) )
        expr_list = self.decode_str_to_expr_list(panel_param_ID_expr)
        threshold_print ( 30, "  Expression: " + str(panel_param_ID_expr) + " evaluates to list: " + str(expr_list) )
        (value,valid) = (None,False)
        if not (None in expr_list):
            (value,valid) = self.eval_all_any_order ( expression = self.translate_panel_param_ID_expr ( panel_param_ID_expr ) )
        return value

    def eval_all_any_order ( self, prnt=False, requested_id=None, expression=None ):
        """ Evaluate all parameters based on dependencies without assuming any order of definition """

        # from math import *
        from math import sqrt, exp, log, log10, sin, cos, tan, asin, acos, atan, ceil, floor  # abs, max, and min are not from math?
        from random import uniform, gauss

        # Start by trying to fix any broken references

        self.fix_all_broken_references()
        
        # Build the working dictionaries needed for evaluation (built from Blender's Properties)

        ID_name_dict = self.build_ID_name_dict()
        ID_value_dict = self.build_ID_value_dict()
        ID_valid_dict = self.build_ID_valid_dict(False)
        dep_list_dict = self.build_depend_list_dict()
        ID_py_expr_dict = self.build_ID_pyexpr_dict ( ID_name_dict )

        requested_val = 0
        valid = True

        # Loop through all parameters over and over evaluating those parameters with valid dependencies
        
        num_passes = 0

        while (num_passes <= len(ID_name_dict)) and (False in ID_valid_dict.values()):

            num_passes = num_passes + 1

            # Visit each parameter
            for parid in ID_name_dict:

                # Only need to update parameters with invalid values
                if not ID_valid_dict[parid]:

                    # Check to see if this parameter can be updated based on ALL of its dependencies being valid
                    dep_list = dep_list_dict[parid]   # May contain "None" values which indicate unresolved references
                    
                    dep_satisfied = True
                    if None in dep_list:
                        # This parameter cannot be evalated regardless of any other dependencies being satisfied
                        dep_satisfied = False
                    else:
                        # Check to see if everything this parameter depends on is valid
                        dep_satisfied = True
                        for dep_id in dep_list:
                            if not ID_valid_dict[dep_id]:
                                dep_satisfied = False
                                break

                    if dep_satisfied:
                        # It's OK to evaluate this parameter
                        
                        something_changed = False
                        py_statement = ""
                        try:
                            if (len(str(ID_name_dict[parid]).strip()) <= 0) or (len(str(ID_py_expr_dict[parid]).strip()) <= 0):
                                val = 0
                                threshold_print ( 20, "Empty name or expression: \"" + str(ID_name_dict[parid]) + " = " + str(ID_py_expr_dict[parid]) + "\"" )
                            else:
                                #py_statement = str(str(self.get_name(parid))) + " = " + str(self.get_expr ( parid, to_py=True ))
                                py_statement = str(ID_name_dict[parid]) + " = " + str(ID_py_expr_dict[parid])
                                threshold_print ( 90, "About to exec: " + py_statement )
                                exec ( py_statement )
                                val = eval ( ID_name_dict[parid], locals() )
                            
                            # Check for changes ...
                            if parid in ID_value_dict:
                                # The parameter is already there, so check if it's different
                                if str(val) != ID_value_dict[parid]:
                                    something_changed = True
                            else:
                                # If it wasn't there, then this is a change!!
                                something_changed = True

                            ID_value_dict.update ( { parid : str(val) } )
                            if (requested_id == parid):
                                requested_val = val
                        except:
                            valid = False
                            threshold_print ( 0, "==> Evaluation Exception for " + py_statement + ": " + str ( sys.exc_info() ) )
                            if prnt:
                                threshold_print ( 0, "  Error in statement:   " + self.get_name(parid) + " = " + self.get_error(parid) )
                                threshold_print ( 0, "    ... interpreted as: " + py_statement )

                        ID_valid_dict[parid] = True

                    # End If
                # End If
            # End For
        # End While

        if expression != None:
            # Evaluate the requested expression in the context of the variables that have already been evaluated:
            try:
                requested_val = 0
                if len(expression.strip()) > 0:
                    val = eval ( expression, locals() )
                    requested_val = val
            except:
                valid = False
                threshold_print ( 0, "==> Evaluation Exception for requested expression " + expression + ": " + str ( sys.exc_info() ) )
                if prnt:
                    threshold_print ( 0, "  Error in requested statement:   " + expression )

        # Load the updated values back into the Properties
        self.load_ID_value_dict ( ID_value_dict, ID_valid_dict )

        return ( requested_val, valid )


    def add_parameter ( self, context ):
        """ Add a new parameter to the list of parameters and set as the active parameter """
        new_par = self.parameter_list.add()
        new_par.id = self.allocate_available_id()
        new_par.set_defaults()
        self.active_par_index = len(self.parameter_list)-1

    def remove_active_parameter ( self, context ):
        """ Remove the active parameter from the list of parameters if not needed by others """
        status = ""
        if len(self.parameter_list) > 0:
            if self.used_by_any_other_parameters(self.parameter_list[self.active_par_index].id):
                status = "Parameter is needed by: " + self.used_by_these_other_parameters(self.parameter_list[self.active_par_index].id)
            else:
                self.parameter_list.remove ( self.active_par_index )
                self.active_par_index -= 1
                if self.active_par_index < 0:
                    self.active_par_index = 0
        return ( status )

    def allocate_available_id ( self ):
        """ Return a unique parameter ID for a new parameter """
        if len(self.parameter_list) <= 0:
            # Reset the ID to 1 when there are no more parameters
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def parse_param_expr ( self, param_expr ):
        """ Converts a string expression into a list expression with:
                 variable id's as integers,
                 None preceding undefined names
                 all others as strings
            Returns either a list (if successful) or None if there is an error

            Examples:

              Expression: "A * (B + C)" becomes something like: [ 3, "*", "(", 22, "+", 5, ")", "" ]
                 where 3, 22, and 5 are the ID numbers for parameters A, B, and C respectively

              Expression: "A * (B + C)" when B is undefined becomes: [ 3, "*", "(", None, "B", "+", 5, ")", "" ]

              Note that the parsing may produce empty strings in the list which should not cause any problem.
        """
        
        name_ID_dict = self.build_name_ID_dict()

        param_expr = param_expr.strip()

        if len(param_expr) == 0:
            return []

        st = None
        pt = None
        try:
            st = parser.expr(param_expr)
            pt = st.totuple()
        except:
            threshold_print ( 0, "==> Parsing Exception: " + str ( sys.exc_info() ) )

        parameterized_expr = None  # param_expr
        if pt != None:
        
            parameterized_expr = self.recurse_tree_symbols ( name_ID_dict, pt, [] )
            
            if parameterized_expr != None:
            
                # Remove trailing empty strings from parse tree - why are they there?
                while len(parameterized_expr) > 0:
                    if parameterized_expr[-1] != '':
                        break
                    parameterized_expr = parameterized_expr[0:-2]

        return parameterized_expr


    def recurse_tree_symbols ( self, name_ID_dict, pt, current_expr ):
        """ Recurse through the parse tree looking for "terminal" items which are added to the list """

        expression_keywords = self.get_expression_keywords()

        if type(pt) == tuple:
            # This is a tuple, so find out if it's a terminal leaf in the parse tree

            threshold_print ( 95, "recurse_tree_symbols with a tuple (" + str(current_expr) + ")" )
            threshold_print ( 95, "  pt = " + str(pt) )

            terminal = False
            if len(pt) == 2:
                if type(pt[1]) == str:
                    terminal = True

            if terminal:
                # This is a 2-tuple with a type and value
                if pt[0] == token.NAME:
                    if pt[1] in expression_keywords:
                        # This is a recognized name and not a user-defined symbol, so append the string itself
                        return current_expr + [ pt[1] ]
                    else:
                        # This must be a user-defined symbol, so check it it's in the dictionary
                        if pt[1] in name_ID_dict:
                            # Append the integer ID to the list
                            return current_expr + [ name_ID_dict[pt[1]] ]
                        else:
                            # Not in the dictionary, so append a None flag followed by the undefined name
                            return current_expr + [ None, pt[1] ]
                else:
                    # This is a non-name part of the expression
                    return current_expr + [ pt[1] ]
            else:
                # Break it down further
                for i in range(len(pt)):
                    next_segment = self.recurse_tree_symbols ( name_ID_dict, pt[i], current_expr )
                    if next_segment != None:
                        current_expr = next_segment
                return current_expr
        return None

##### ^^^^^^^^^   General Parameter Code   ^^^^^^^^^



##### vvvvvvvvv   Panel Parameter Code   vvvvvvvvv

# These are the classes that make up panel parameters

def update_PanelParameter ( self, context ):
    """
    This is the callback function for all panel parameters.
    This function should do all of the generic parsing and
    updating and then call a specific user update callback
    function to do any special processing with the result.
    """

    threshold_print ( 30, "update_PanelParameter called" )
    threshold_print ( 30, "  self.expression = " + str(self.expression) )
    threshold_print ( 30, "  self.value = " + str(self.value) )
    
    app = context.scene.app
    gen_params = app.general_parameters
    
    # Always test values first before setting to avoid infinite recursion since setting triggers re-evaluation
    
    # Create a string encoded version of the expression (like "#1~+~3~*~(~#2~+~7.0~)")
    id_expr = gen_params.parse_panel_param_expr ( self.expression )
    threshold_print ( 30, "update_PanelParameter with id_expr = " + str(id_expr) )
    if self.ID_expression != id_expr:
        self.ID_expression = id_expr
        threshold_print ( 30, "changing self.ID_expression to " + str(self.ID_expression) )
    expr = gen_params.translate_panel_param_ID_expr ( self.ID_expression )
    if self.expression != expr:
        self.expression = expr
    value = gen_params.eval_panel_param_ID_expr ( self.ID_expression )
    if value == None:
        threshold_print ( 5, "Invalid expression detected in update_PanelParameter!!!" )
        self.status = "Invalid Expression: " + expr
    else:
        if self.value != value:
            self.value = value
        self.status = ""

    #try:
    #    self.value = float(self.expression)
    #except:
    #    self.value = 0.0

    threshold_print ( 30, " After Automatic Update:" )
    threshold_print ( 30, "  self.expression = " + str(self.expression) )
    threshold_print ( 30, "  self.value = " + str(self.value) )

    get_parent(self).update()

    threshold_print ( 30, " After User Update:" )
    threshold_print ( 30, "  self.expression = " + str(self.expression) )
    threshold_print ( 30, "  self.value = " + str(self.value) )



class PanelParameterData(bpy.types.PropertyGroup):
    # This class contains data that might have been better stored in the PanelParameter class,
    #  but for some reason, it was not able to be accessed there by subclasses.

    status = StringProperty(name="status", default="")

    expression = StringProperty(name="expression", default="0", update=update_PanelParameter)
    ID_expression = StringProperty(name="ID_expression", default="0")
    value = FloatProperty(name="value", default=0)
    label = StringProperty(name="label", default="Parameter")

    min_set = bpy.props.BoolProperty(name="min_set", default=False)
    max_set = bpy.props.BoolProperty(name="max_set", default=False)
    min_value = FloatProperty(name="min_value", default=0)
    max_value = FloatProperty(name="max_value", default=1)

    """
    def ok(self):
        return ( "" )
    def uninitialized(self):
        return ( "Uninitialized" )
    def undefined_parameter(self):
        return ( "Undefined Parameter" )
    def illegal_expression(self):
        return ( "Illegal Expression" )
    """
    


class PanelParameter(bpy.types.PropertyGroup):
    # For some reason, subclassing this class inherits functions, but not Properties. Is this a Blender/Python inconsistency?
    # Otherwise, the "param_data" would be here rather than in the subclasses.  : (

    def get_status(self):
        return str(self.param_data.status)
    def append_status(self, stat_string):
        self.param_data.status = self.param_data.status + "   " + stat_string
    def set_status_ok(self):
        self.param_data.status = ""
    def is_status_ok(self):
        return len(self.param_data.status) == 0

    def set_label(self, label):
        self.param_data.label = label
    def get_label(self):
        return str(self.param_data.label)

    def set_expression(self, expr):
        self.param_data.expression = expr
        return True
    def get_expression(self):
        return str(self.param_data.expression)

    def get_ID_expression(self):
        return str(self.param_data.ID_expression)

    def get_value(self):
        return float(self.param_data.value)

    def get_text(self):
        """ Default string expression for parameters ... overload for different functionality """
        return (  self.get_expression() + " = " + str(self.get_value()) )

    def set_fields(self, label=None, expr=None, min_val=None, max_val=None):
        if label != None:
            self.set_label(label)
        if expr != None:
            self.set_expression(expr)
        if min_val != None:
            self.param_data.min_value = min_val
            self.param_data.min_set = True
        if max_val != None:
            self.param_data.max_value = max_val
            self.param_data.max_set = True
        return True

    def update(self):
        threshold_print ( 90, "   Default PanelParameter.update() function ... overload for functionality" )
        plist = get_numeric_parameter_list ( None, [] )
        threshold_print ( 95, "     List of all panel parameters:" )
        for pp in plist:
            threshold_print ( 95, pp )
        plist_names = str(plist)[1:-1].split(",")
        for pp in plist_names:
            threshold_print ( 95, "       " + pp.strip() )
        for i in range(len(plist)):
            threshold_print ( 95, "      " + plist_names[i].strip() + " = " + str(plist[i].get_value()) )

    def draw_in_new_row(self, layout):
        """ Default drawing for parameters ... overload for different functionality """
        row = layout.row()
        value = self.get_value()
        row.prop ( self.param_data, "expression", text=self.param_data.label+" = "+str(value) )
        if not self.is_status_ok():
            row = layout.row()
            row.label(icon='ERROR', text=self.param_data.status)
        else:
            if self.param_data.min_set:
                if value < self.param_data.min_value:
                    row = layout.row()
                    row.label(icon='ERROR', text="Warning: Value of " + str(value) + " for " + self.get_label() + " is less than minimum of "+str(self.param_data.min_value))
            if self.param_data.max_set:
                if value > self.param_data.max_value:
                    row = layout.row()
                    row.label(icon='ERROR', text="Warning: Value of " + str(value) + " for " + self.get_label() + " is greater than maximum of "+str(self.param_data.max_value))



class PanelParameterFloat(PanelParameter):
    """ Simple (but useful) subclass of PanelParameter """
    param_data = PointerProperty(type=PanelParameterData)

class PanelParameterInt(PanelParameter):
    """ Simple (but useful) subclass of PanelParameter """
    param_data = PointerProperty(type=PanelParameterData)
    # Over-ride the "get_value" function to return an integer
    def get_value(self):
        return int(self.param_data.value)


def get_numeric_parameter_list ( objpath, plist, debug=False ):
    """ Recursive routine that builds a list of numeric (PanelParameterInt and PanelParameterFloat) parameters """
    threshold_print ( 95, "get_numeric_parameter_list() called with objpath = " + str(objpath) )
    if (objpath == None):
        # Start with default path
        objpath = "bpy.context.scene.app"
    obj = eval(objpath)
    threshold_print ( 95, "Path = " + str(objpath) + ", obj = " + str(obj) )
    threshold_print ( 98, "  plist = " + str(plist) )
    # Note, even though PanelParameterFloat and PanelParameterInt are subclasses of PanelParameter, they're not found that way!!
    if isinstance(obj,(bpy.types.PanelParameterInt,bpy.types.PanelParameterFloat)):
        # This is what we're looking for so add it to the list
        plist.append ( obj )
        threshold_print ( 98, "   plist.append gives " + str(plist) )
    elif isinstance(obj,bpy.types.PanelParameter):
        # This might be some other (non-numeric) type of PanelParameter ... ignore it
        pass
    elif isinstance(obj,bpy.types.PropertyGroup):
        # This is a property group, so walk through all of its properties using keys
        # for objkey in obj.keys():
        for objkey in obj.bl_rna.properties.keys():    # This is somewhat ugly, but works best!!
            try:
                pstr = objpath+"."+str(objkey)
                plist = get_numeric_parameter_list(pstr, plist, debug)
            except:
                # This can happen with properties in the .blend file that are no longer in the code or have been renamed!!!
                threshold_print ( 0, "  ===> Exception:" )
                threshold_print ( 0, "    ===> Exception type = " + sys.exc_type )
                threshold_print ( 0, "    ===> Exception value = " + sys.exc_value )
                threshold_print ( 0, "    ===> Exception traceback = " + sys.exc_traceback )
                threshold_print ( 0, "    ===> Exception in recursive call to get_numeric_parameter_list ( " + pstr + " )" )
                # threshold_print ( 0, "    ===> Exception in get_numeric_parameter_list isinstance branch with " + objpath + "." + str(objkey) )
    elif type(obj).__name__ == 'bpy_prop_collection_idprop':
        # This is a collection, so step through its elements as if it's an array using keys
        for objkey in obj.keys():
            try:
                plist = get_numeric_parameter_list(objpath+"['"+str(objkey)+"']", plist, debug)
            except:
                threshold_print ( 0, " ===> Exception in get_numeric_parameter_list idprop branch with " + objpath + "['" + str(objkey) + "']" )
    else:
        # This could be anything else ... like <'int'> or <'str'>
        pass
    return plist


def print_numeric_parameter_list ( thresh, prefix="" ):
    """ Obtains a list of all numeric panel parameters and prints them to the console """
    plist = get_numeric_parameter_list ( None, [] )
    # Remove the leading and trailing brackets and split by commas
    plist_names = str(plist)[1:-1].split(",")
    threshold_print ( thresh, prefix + "There are " + str(len(plist)) + " panel parameters defined" )
    for i in range(len(plist)):
        threshold_print ( thresh, prefix + "  " +  plist_names[i].strip() + " = " + str(plist[i].get_expression()) + " = " + str(plist[i].get_ID_expression()) + " = " + str(plist[i].get_value()) )

### Some generic example classes ... WARNING: The examples in this section contain ideas that have not been fully tested

class PARAM_debug_class(PanelParameter):
    """ Example of subclassing PanelParameter and overloading its methods """
    param_data = PointerProperty(type=PanelParameterData)
    def update( self ):
        threshold_print ( 20, "   User's update called with " + " self.param_data.expression = " + str(self.param_data.expression) + ", self.param_data.value = " + str(self.param_data.value) )
        threshold_print ( 20, "     dir(self) = " + str(dir(self)) )
        threshold_print ( 20, "     Starting python interactive console ... control-D to continue running..." )
        # This drops into a python interpreter on the console ( don't start Blender with an & !! )
        __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})


class ExampleOverloadedPanelParameter(PanelParameter):
    """ Example of subclassing PanelParameter and overloading its methods """
    param_data = PointerProperty(type=PanelParameterData)
    def get_text(self):
        return (  str(self.param_data.expression) + "=" + str(self.param_data.value) )
    def update( self ):
        parent = get_parent ( self )
        threshold_print ( 50, "Parent = " + str(parent) )

class Iterations_class(PanelParameter):
    """ Example class for handling the iterations panel parameter """
    param_data = PointerProperty(type=PanelParameterData)
    def get_text(self):
        return ( "n=" + str(self.param_data.value) )
    def update( self ):
        parent = get_parent ( self )


##### ^^^^^^^^^   Panel Parameter Code   ^^^^^^^^^



#################################################################################################################
##########################    Application's "User" Code Starts Here   ###########################################
#################################################################################################################


### Model Initialization Code:


class APP_PT_Initialization(bpy.types.Panel):
    bl_label = "Initialization"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        # "self" is an APP_PT_Initialization object not an AppInitializationProperties object
        # Call the draw_panel function for the instance being drawn in this panel
        context.scene.app.initialization.draw_panel ( context, panel=self )


class AppInitializationProperties(bpy.types.PropertyGroup):
    """ Example of top level application parameters """
    iterations = PointerProperty(name="Iterations", type=PanelParameterInt)
    time_step = PointerProperty(name="Time Step", type=PanelParameterFloat)
    show_advanced = bpy.props.BoolProperty(default=False)
    time_step_max = PointerProperty(name="Time Step Max", type=PanelParameterFloat)
    space_step = PointerProperty(name="Space Step", type=PanelParameterFloat)
    
    def set_defaults(self):
        # Set defaults for all Properties or they may not exist for printing or exporting!!
        self.iterations.set_fields ( label="Iterations", expr="1000", min_val=0, max_val=None )
        self.time_step.set_fields ( label="Time Step", expr="0.001", min_val=0, max_val=None )
        self.show_advanced = False
        self.time_step_max.set_fields ( label="Time Step Max", expr="0.01", min_val=0, max_val=None )
        self.space_step.set_fields ( label="Space Step", expr="0.1", min_val=0, max_val=None )

    # Exporting to an MDL file could be done just like this or via a non-member function that knows the details of this class
    def print_details( self, thresh, prefix=""):
        threshold_print ( thresh, prefix + "Running for "      + self.iterations.get_text()    + " iterations" )
        threshold_print ( thresh, prefix + "Time Step = "      + self.time_step.get_text()     + " seconds" )
        threshold_print ( thresh, prefix + "Time Step Max = "  + self.time_step_max.get_text() + " seconds" )
        threshold_print ( thresh, prefix + "Space Step Max = " + self.space_step.get_text()    + " meters" )

    def draw_panel ( self, context, panel ):
        app = context.scene.app
        layout = panel.layout

        layout.row().prop ( app, "debug_level", text="Debug Level" )
        self.iterations.draw_in_new_row(layout)
        self.time_step.draw_in_new_row(layout)
        
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if self.show_advanced:
            row.prop ( self, "show_advanced", icon='TRIA_DOWN', text="Advanced Options", emboss=False )
            self.time_step_max.draw_in_new_row(box)
            self.space_step.draw_in_new_row(box)
        else:
            row.prop(self, "show_advanced", icon='TRIA_RIGHT', text="Advanced Options", emboss=False)
        
        row = layout.row()
        row.operator("app.run_simulation", text="Export (print) the Current Model", icon='COLOR_RED')
        row.operator("app.reset_everything", text="Reset all to defaults", icon='ERROR')



### Molecule Definition Code:


class APP_OT_molecule_add(bpy.types.Operator):
    bl_idname = "app.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule type to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.app.molecules.add_molecule(context)
        return {'FINISHED'}

class APP_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "app.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.app.molecules.remove_active_molecule(context)
        # One of: 'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY'
        self.report({'INFO'}, "Deleted Molecule")
        return {'FINISHED'}


# Callbacks for all Property updates appear to require global (non-member) functions.
# This is circumvented by simply calling the associated member function passed as self:

def check_callback(self, context):
    self.check_callback(context)
    return

class AppMoleculeProperty(bpy.types.PropertyGroup):
    """ Example class for handling the molecules panel parameters """
    id = IntProperty(name="ID", default=-1)
    name = StringProperty ( name="Molecule Name", default="Molecule", description="The molecule species name", update=check_callback )
    diffusion_constant = PointerProperty(name="Diffusion Constant", type=PanelParameterFloat)
    diameter = PointerProperty(name="Diameter", type=PanelParameterFloat)
    mol_wt = PointerProperty(name="Molecular Weight", type=PanelParameterInt)
    status = StringProperty(name="Status")

    def set_defaults(self):
        self.name = "Molecule_"+str(self.id)
        self.diffusion_constant.set_fields ( label="Diff Const", expr="0.001", min_val=0, max_val=None )        
        self.diameter.set_fields ( label="Diameter", expr="0.002", min_val=0, max_val=None )
        self.mol_wt.set_fields ( label="Mol Wt", expr="5", min_val=0, max_val=None )

    # Exporting to an MDL file could be done just like this or via a non-member function that knows the details of this class
    def print_details( self, thresh, prefix=""):
        threshold_print ( thresh, prefix + "Name = " + self.name )
        threshold_print ( thresh, prefix + "  " + self.diffusion_constant.get_label() + " = " + self.diffusion_constant.get_text() )
        threshold_print ( thresh, prefix + "  " + self.diameter.get_label() + " = " + self.diameter.get_text() )
        threshold_print ( thresh, prefix + "  " + self.mol_wt.get_label() + " = " + self.mol_wt.get_text() )

    def draw_props ( self, layout ):
        layout.prop ( self, "name" )
        self.diffusion_constant.draw_in_new_row(layout)
        self.diameter.draw_in_new_row(layout)
        self.mol_wt.draw_in_new_row(layout)

    def check_callback(self, context):
        """Allow the parent molecule list (AppMoleculesListProperty) to do the checking"""
        get_parent(self).check(context)
        return


class APP_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        threshold_print ( 90, "APP_UL_check_molecule called" )
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class APP_PT_define_molecules(bpy.types.Panel):
    bl_label = "Define Molecules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw ( self, context ):
        # Call the draw function for the instance being drawn in this panel
        context.scene.app.molecules.draw_panel ( context, self )


class AppMoleculesListProperty(bpy.types.PropertyGroup):
    molecule_list = CollectionProperty(type=AppMoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_advanced = bpy.props.BoolProperty(default=True)  # If Properties are not shown, they may not exist!!!

    def set_defaults(self):
        # It's not clear if setting the defaults for the molecule list should
        #    set defaults for each molecule in the list or
        #    delete all the molecules to create an empty list
        # Since it's more interesting to set the molecules back to their defaults ... do that.
        if self.molecule_list:
            for mol in self.molecule_list:
                mol.set_defaults()
    
    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_mol = self.molecule_list.add()
        new_mol.id = self.allocate_available_id()
        new_mol.set_defaults()
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        self.molecule_list.remove ( self.active_mol_index )
        self.active_mol_index -= 1
        if self.active_mol_index < 0:
            self.active_mol_index = 0
        if self.molecule_list:
            threshold_print ( 90, "Inside remove_active_molecule with self of type " + str(type(self)) )
            threshold_print ( 90, "  remove_active_molecule calling self.check_molecule(context)" )
            self.check(context)

    def check ( self, context ):
        """Checks for duplicate or illegal molecule name"""
        # Note: Some of the list-oriented functionality is appropriate here (since this
        #        is a list), but some of the molecule-specific checks (like name legality)
        #        could be handled by the the molecules themselves. They're left here for now.
        threshold_print ( 90, "Top of local check with self of type " + str(type(self)) )
        threshold_print ( 90, "  and parent of type " + str(type(get_parent(self))) )

        mol = self.molecule_list[self.active_mol_index]

        status = ""

        # Check for duplicate molecule name
        mol_keys = self.molecule_list.keys()
        if mol_keys.count(mol.name) > 1:
            status = "Duplicate molecule: %s" % (mol.name)

        # Check for illegal names (Starts with a letter. No special characters.)
        mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
        m = re.match(mol_filter, mol.name)
        if m is None:
            status = "Molecule name error: %s" % (mol.name)

        mol.status = status

        threshold_print ( 90, "Bottom of local check with self of type " + str(type(self)) )
        return


    def allocate_available_id ( self ):
        """ Return a unique molecule ID for a new molecule """
        if len(self.molecule_list) <= 0:
            # Reset the ID to 1 when there are no more molecules
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )

    def draw_panel ( self, context, panel ):
        layout = panel.layout
        row = layout.row()
        row.label(text="Defined Molecules:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list("APP_UL_check_molecule", "define_molecules",
                          self, "molecule_list",
                          self, "active_mol_index",
                          rows=2)
        col = row.column(align=True)
        col.operator("app.molecule_add", icon='ZOOMIN', text="")
        col.operator("app.molecule_remove", icon='ZOOMOUT', text="")
        if self.molecule_list:
            mol = self.molecule_list[self.active_mol_index]
            mol.draw_props ( layout )



### An operator for running the simulation (essentially exporting state to MDL or other format)

class PARAMS_OT_run_simulation(bpy.types.Operator):
    bl_idname = "app.run_simulation"
    bl_label = "Run Simulation"
    bl_description = "Run Simulation"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Pretend to run a simulation by printing all of the parameters that would be used
        app = context.scene.app
        app.print_self()
        return {'FINISHED'}



### An operator for resetting everything

class PARAMS_OT_reset_everything(bpy.types.Operator):
    bl_idname = "app.reset_everything"
    bl_label = "Reset Everything"
    bl_description = "Reset Everything - Set everything to defaults"
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.app
        app.set_defaults(context)
        return {'FINISHED'}


# Main Parameters Properties Class:

class AppPropertyGroup(bpy.types.PropertyGroup):
    """This is the top level property group that contains user code and a ParametersPropertyGroup"""

    initialized = BoolProperty(default=False)
    
    parameter_version = StringProperty(name="Parameters Version", default="0.1")
    debug_level = IntProperty(name="Debug", default=10, min=0, max=100, description="Amount of debug information to print")

    general_parameters = PointerProperty(type=ParametersPropertyGroup, name="General Parameters")

    initialization = PointerProperty(type=AppInitializationProperties, name="Model Initialization")
    molecules = PointerProperty(type=AppMoleculesListProperty, name="Defined Molecules")
    
    def set_defaults ( self, context ):
        self.debug_level = 31 # Normally 10
        self.initialization.set_defaults()
        self.molecules.set_defaults()

    def print_self(self):

        # import pdb; pdb.Pdb(completekey='tab').set_trace()
        

        threshold_print ( 5, "==================== Simulation Parameters ==========================" )

        threshold_print ( 5, "----- All General Parameters -----" )
        self.general_parameters.print_all_general_parameters ( 5, prefix="  " )

        threshold_print ( 5, "----- All Panel Parameters -----" )
        print_numeric_parameter_list ( 5, prefix = "  ")

        threshold_print ( 5, "----- Formatted Panel Parameters -----" )

        mols = self.molecules.molecule_list
        threshold_print ( 5, "  Model contains " + str(len(mols)) + " molecules" )
        for mol in mols:
            mol.print_details ( 5, prefix = "    " )
        self.initialization.print_details ( 5, prefix = "  " )




from bpy.app.handlers import persistent

@persistent
def auto_initialize(context):
    """ Check whether the application data has been initialized """
    print ( "auto_initialize() has been called" )
    if not context:
        context = bpy.context
    if "app" in dir(context.scene):
        app = context.scene.app
        if not app.initialized:
            # Initialize the application defaults
            app.set_defaults(context)
            app.initialized = True



#############################################################################################################


#
#    Registration
#

def register():
  print ("Registering ", __name__)
  bpy.utils.register_module(__name__)
  bpy.types.Scene.app = bpy.props.PointerProperty(type=AppPropertyGroup)
  # Try calling the set defaults function?
  # This doesn't seem to work ... it might need to be added to a hook prior to loading a .blend file
  # bpy.context.scene.app.set_defaults ( bpy.context )

def unregister():
  print ("Unregistering ", __name__)
  del bpy.types.Scene.app
  bpy.utils.unregister_module(__name__)


# Establish handlers
if len(bpy.app.handlers.load_post) == 0:
    bpy.app.handlers.load_post.append ( auto_initialize )

if __name__ == "__main__":
  register()

