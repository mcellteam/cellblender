#!/usr/bin/env python
from math import *
from random import uniform, gauss
import parser
import re
import token
import symbol
import sys

print ( "ParameterSpace.py being processed ..." )

class ParameterSpace:

    """ Encapsulate a parameter space with mutable parameter names associated with parameter expressions:

        IDs currently run from 1 to n, with negative IDs typically indicating an error. ID 0 is unused.
        The expression for each parameter is always valid (default is "0"). It cannot contain any negative ids.
        When an invalid expression is defined, the original expression remains in effect, and the invalid
          expression is stored and displayed along with the original (current) expression.
        It is not allowable to delete a parameter which is used in other parameter expressions.
        
    """

    def __init__ ( self ):
        """ Initialize a new ParameterSpace """
        #print ( "ParameterSpace.__init__() called" )
        self.VERSION = self.get_version()
        self.EXPRESSION_KEYWORDS = { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' }
        self.UNDEFINED_NAME = "   (0*1111111111*0)   "
        self.init_param_space()

    def get_version ( self ):
        return ( 0.001 )  # N O T E: This constant is in the function to keep it from being saved when pickling!!!
    
    def version_match ( self ):
        if self.VERSION == self.get_version():
            return True
        else:
            return False

    def init_param_space ( self ):
        #print ( "Init_param_space called" )
        self.name_ID_dict = {}  # Maps string names to integer IDs
        self.ID_name_dict = {}  # Maps IDs to string names
        self.ID_expr_dict = {}  # Maps IDs to expression list containing either string literals or integer IDs
        self.ID_value_dict = {}  # Maps IDs to their current value as a string
        self.ID_error_dict = {}  # When not None this contains an expression that needs further editing because it is in error
        self.ID_valid_dict = {}  # Boolean value for each parameter indicating that it's value is valid with respect to all other parameters
        self.next_id = 1

    def delete_all ( self ):
        """ Delete all parameters """
        self.init_param_space()


    def num_parameters ( self ):
        return ( len(self.ID_name_dict) )

    def get_next_id ( self ):
        return self.next_id


    def dump ( self, prnt=False ):
        # For right now, this function defaults to silence (an easy way to turn it on and off globally)
        if prnt:
            print ( " Parameter space:" )
            print ( "  next_id = " + str(self.next_id) )
            print ( "  name->ID = " + str(self.name_ID_dict) )
            print ( "  ID->name = " + str(self.ID_name_dict) )
            print ( "  ID->expr = " + str(self.ID_expr_dict) )
            print ( "  ID->valu = " + str(self.ID_value_dict) )
            print ( "  ID->erro = " + str(self.ID_error_dict) )
            print ( "  ID->vali = " + str(self.ID_valid_dict) )
            for i in self.ID_name_dict:
                #print ( "    " + str(self.ID_name_dict[i]) + " = " + str(self.ID_value_dict[i]) + " = " + self.get_expr(i) + " = " + self.get_expr(i,to_py=True) + " = " + str(self.ID_expr_dict[i]) )

                print ( "    " + str(i) + ": " + str(self.ID_name_dict[i])  )
                print ( "    " + str(i) + ": " + str(self.ID_value_dict[i]) )
                print ( "    " + str(i) + ": " + self.get_expr(i) )
                print ( "    " + str(i) + ": " + self.get_expr(i,to_py=True) )
                print ( "    " + str(i) + ": " + str(self.ID_expr_dict[i]) )
                print ( "    " + str(i) + ": " + str(self.ID_error_dict[i]) )
                print ( "    " + str(i) + ": " + str(self.ID_valid_dict[i]) )

                #print ( "    " + str(self.ID_name_dict[i]) + " = " + self.get_expr(i) + " = " + self.get_expr(i,to_py=True) + " = " + str(self.ID_expr_dict[i]) )
            self.eval_all(True)


    def print_keywords ( self ):
        for mdl_keyword in self.EXPRESSION_KEYWORDS:
            print ( "  " + mdl_keyword + " = " + self.EXPRESSION_KEYWORDS[mdl_keyword] )


    """
    The following functions (define, set_expr, and get_expr) provide the core functionality
      for setting and getting expressions.
    """

    def define ( self, name, expr ):
        """ Define a parameter ... may be new or may overwrite an existing parameter"""
        """ Return the ID of this parameter whether it's new or not """
        # print "Define: " + str(name) + " = " + str(expr)
        if name == None:
            # Try to choose a name with this next ID if possible, but search further as needed
            next_unused_number = self.next_id
            while self.get_id( "P%d" % (next_unused_number) ) != None:
                next_unused_number += 1
            name = "P%d" % (next_unused_number)
            
        this_id = -1
        if name in self.name_ID_dict:
            # This parameter already exists, so just update its expression
            # print ( "Parameter " + name + " already exists, so just update the expression" )
            this_id = self.get_id(name)
            self.set_expr ( this_id, expr )
        else:
            # This is a new name, so make a new entry
            # print ( "Parameter " + name + " is new, so make new name/ID entries as well as update the expression" )
            this_id = self.next_id
            self.name_ID_dict.update ( { name : this_id } )
            self.ID_name_dict.update ( { this_id : name } )
            # Always set the default ("original") value to 0
            self.ID_expr_dict.update ( { this_id : "0" } )
            # Now try to set the expression
            # Note that set_expr will validate the expression before replacing the current one.
            #  If the new expression is not valid, it will not replace the current expression and
            #  instead, it will update the error expression.
            self.set_expr ( this_id, expr )
            self.next_id += 1
        return this_id


    def set_expr ( self, parid, expr ):
        """ Store original text and parse and store the expression for the specified parameter ID """
        # self.ID_error_dict.update ( { parid : expr } )  # This may be redundant, but is here for clarity
        parsed_expr = self.parse_param_expr ( expr )


        # Try parsing a second time to catch forward references?
        parsed_expr = self.parse_param_expr ( expr )

        if (parsed_expr == None) or (-1 in parsed_expr):
            # There was an error in the string expression, so save the error version and don't change anything else
            self.ID_error_dict.update ( { parid : expr } )
        else:
            # The expression parsed fine, so set error version to None, update the expression, and evaluate it's value
            self.ID_error_dict.update ( { parid : None } )
            self.ID_expr_dict.update ( { parid : parsed_expr } )
            self.ID_valid_dict.update ( { parid : False } )
            self.eval_all()
            self.ID_value_dict.update ( { parid : self.get_value(parid) } )


    def get_expr ( self, parid, to_py=False, prefix='', suffix='' ):
        """ Construct a string representation of the expression by substituting symbols for IDs """
        exp_list = self.ID_expr_dict[parid]
        expr = ""
        for token in exp_list:
            if type(token) == int:
                # This is an integer parid, so look up the variable name to concatenate
                if token in self.ID_name_dict:
                    expr = expr + (prefix + self.ID_name_dict[token] + suffix)
                else:
                    # In previous versions, this case might have defined a new parameter here.
                    # # Assume that this use is defining a new parameter with a value of 0
                    # if self.define ( token, "0" ) > 0:
                    #     # The name was successfully defined as a new parameter
                    #     expr = expr + (prefix + self.ID_name_dict[token] + suffix)
                    # In this version, it should never happen, but appends an undefined name in case it does
                    expr = expr + self.UNDEFINED_NAME
            else:
                # This is a string so simply concatenate it after translation as needed
                if to_py and (token in self.EXPRESSION_KEYWORDS):
                    expr = expr + self.EXPRESSION_KEYWORDS[token]
                else:
                    expr = expr + token
        return expr



    """
    These functions (get_dependents_list and get_dependents_names) find parameters
    that reference the requested ID.
    """

    def get_dependents_list ( self, parid ):
        """ Return a list of all parameter ids that reference this parameter id directly """
        dependents = []
        for test_id in self.ID_expr_dict:
            exp_list = self.ID_expr_dict[test_id]
            for token in exp_list:
                if type(token) == int:
                    if token == parid:
                        dependents = dependents + [ test_id ]
                        break
        return dependents


    def get_dependents_names ( self, parid ):
        """ Return a list of all parameter names that reference this parameter id directly """
        dlist = self.get_dependents_list(parid)
        if len(dlist) > 0:
            dlist = [self.get_name(i) for i in dlist]
        return dlist



    """
    These functions (get_depend_list and get_depend_dict) find parameters that
    are referenced by the requested id.
    """

    def get_depend_list ( self, parid ):
        """ Construct a list of ids that this id depends upon (or is a function of) """
        exp_list = self.ID_expr_dict[parid]
        depends_on = set ( [] )
        for token in exp_list:
            if type(token) == int:
                depends_on.add ( token )
        return [ x for x in depends_on ]


    def get_depend_dict ( self, parid ):
        """ Construct a dictionary of ids and names that this id depends upon (or is a function of) """
        exp_list = self.ID_expr_dict[parid]
        depends_on = {}
        for token in exp_list:
            if type(token) == int:
                depends_on.update ( {token : self.get_name(token)} )
        return depends_on



    """
    These functions delete parameters.
    """    

    def absolute_delete ( self, parid ):
        """ Delete a parameter """
        name = self.get_name ( parid )
        if name != None:
            self.name_ID_dict.pop(name)
            self.ID_name_dict.pop(parid)
            self.ID_expr_dict.pop(parid)
            self.ID_value_dict.pop(parid)
            self.ID_error_dict.pop(parid)
            self.ID_valid_dict.pop(parid)
            if len(self.name_ID_dict) <= 0:
                # Reset the ID numbers when the list becomes empty
                self.next_id = 1

    def delete ( self, parid ):
        """ Delete a parameter only if it has no dependencies """
        dependents = self.get_dependents_list(parid)
        if len(dependents) == 0:
          self.absolute_delete ( parid )
          return True
        else:
          return False


    """
    These are general purpose "get" and "set" functions that don't do
       much processing.
    """

    def get_id ( self, name ):
        """ Get the ID of a parameter by name """
        if (len(self.name_ID_dict) > 0) and (name in self.name_ID_dict):
            return self.name_ID_dict[name]
        else:
            return None

    def get_name ( self, parid ):
        """ Get the name of the parameter with the specified ID """
        if parid in self.ID_name_dict:
            return self.ID_name_dict[parid]
        else:
            return None

    def get_error ( self, parid ):
        """ Get the text expression that is currently in error for the specified parameter ID """
        if parid in self.ID_error_dict:
            return self.ID_error_dict[parid]
        else:
            return None

    def get_value ( self, parid ):
        """ Get the current value for the specified parameter ID """
        if parid in self.ID_value_dict:
            return self.ID_value_dict[parid]
        else:
            return None

    def set_name ( self, parid, name ):
        """ Change the name of the parameter for the specified ID returning a boolean success value"""
        old_name = self.get_name ( parid )
        if old_name != None:
            self.ID_name_dict.update ( { parid : name } )
            self.name_ID_dict.update ( { name : self.name_ID_dict.pop(old_name) } )
            return True
        return False


    def rename ( self, old_name, new_name ):
        """ Rename a parameter returning a boolean success value """
        parid = self.get_id ( old_name )
        if parid < 0:
            # Old name doesn't exist so it can't be renamed
            return False
        else:
            new_id = self.get_id ( new_name )
            if new_id != None:
                # New name already exists so a duplicate name can't be created
                return False
            else:
                # It's ok to rename, so update the two dictionaries that associate names and IDs
                self.ID_name_dict.update ( { parid : new_name } )
                self.name_ID_dict.update ( { new_name : self.name_ID_dict.pop(old_name) } )
                return True



    """
    These are the parsing and evaluation functions.
    These functions currently rely on the python parsing and evaluation capabilities.
    """


    def eval_all_ordered ( self, prnt=False, requested_id=None ):
        """ Evaluate all parameters in order, printing either a requested ID or all (-1) when prnt is True """

        # requested_val = self.eval_all_depend ( prnt=prnt, requested_id=requested_id )


        # from math import *
        from math import sqrt, exp, log, log10, sin, cos, tan, asin, acos, atan, ceil, floor  # abs, max, and min are not from math?
        from random import uniform, gauss

        # The following prefix and suffix are used to ensure that parameter names (like "if" and "def") are not interpreted as python keywords.
        # Note that this works with evaluation, but the parsing itself still fails when certain names (like "if" and "def") are used.
        prefix = ''   # 'cellblender_'
        suffix = ''   # '_cellblender'

        requested_val = 0
        if requested_id == None:
            requested_id = -1   # This eliminated the need to check the type for NoneType all the time!!
        
        # local_variables = locals()

        # Loop through as many times as IDs to ensure catching all non-circular dependencies (forward references):

        for pass_num in self.ID_name_dict:
            # print ( "Looping ... " + str(pass_num) )

            something_changed = False

            if prnt and (requested_id<0):
                print ( "==============================================================================" )

            for parid in self.ID_name_dict:
                #print ( "get_name(): " + str(self.get_name(parid)) )
                #print ( "prefix: " + prefix )
                #print ( "suffix: " + suffix )
                #print ( "parid = " + str(parid) )
                py_statement = (prefix + self.get_name(parid) + suffix) + " = " + self.get_expr ( parid, to_py=True, prefix=prefix, suffix=suffix )
                try:
                    #print ( "Before executing \"" + py_statement + "\":" + str(locals()) )
                    exec ( py_statement )
                    val = eval ( (prefix + self.get_name(parid) + suffix), locals() )
                    #print ( "After executing \"" + py_statement + "\":" + str(locals()) )
                    
                    # Check for changes ...
                    if parid in self.ID_value_dict:
                        # The parameter is already there, so check if it's different
                        if str(val) != self.ID_value_dict[parid]:
                            something_changed = True
                    else:
                        # If it wasn't there, then this is a change!!
                        something_changed = True

                    self.ID_value_dict.update ( { parid : str(val) } )
                    if (requested_id == parid):
                        requested_val = val
                    if prnt:
                        if (requested_id == -1) or (requested_id == parid):
                            error_string = ""
                            if self.get_error(parid) != None:
                                error_string = ", *** Error Pending: " + self.get_error(parid)
                            print ( str(parid) + ": " + self.get_name(parid) + " = " + str(val) + " = " + self.get_expr ( parid, to_py=True ) + " = " + self.get_expr ( parid, to_py=False ) + 
                                    ", " + self.get_name(parid) + " depends on " + str(self.get_depend_list(parid)) +   # " = " + str(self.get_depend_dict(parid)) +
                                    ", " + self.get_name(parid) + " is referenced by " + str(self.get_dependents_list(parid)) + error_string )

                except:
                    print ( "==> Evaluation Exception: " + str ( sys.exc_info() ) )
                    if prnt:
                        print ( "  Error in statement:   " + self.get_name(parid) + " = " + self.get_error(parid) )
                        print ( "    ... interpreted as: " + py_statement )

            if prnt and (requested_id<0):
                print ( "==============================================================================" )

            if something_changed == False:
                break
        return requested_val



    def eval_one ( self, dep_locals, parid, prnt=False ):
        # from math import *
        from math import sqrt, exp, log, log10, sin, cos, tan, asin, acos, atan, ceil, floor  # abs, max, and min are not from math?
        from random import uniform, gauss

        something_changed = False
        prefix = ''   # 'cellblender_'
        suffix = ''   # '_cellblender'
        py_statement = ""
        try:
            py_statement = str(prefix + str(self.get_name(parid)) + suffix) + " = " + str(self.get_expr ( parid, to_py=True, prefix=prefix, suffix=suffix ))
            #print ( "Before executing \"" + py_statement + "\":" + str(locals()) )
            exec ( py_statement )
            val = eval ( (prefix + self.get_name(parid) + suffix), dep_locals )
            #print ( "After executing \"" + py_statement + "\":" + str(locals()) )
            
            # Check for changes ...
            if parid in self.ID_value_dict:
                # The parameter is already there, so check if it's different
                if str(val) != self.ID_value_dict[parid]:
                    something_changed = True
            else:
                # If it wasn't there, then this is a change!!
                something_changed = True

            self.ID_value_dict.update ( { parid : str(val) } )
            if (requested_id == parid):
                requested_val = val
            if prnt:
                if (requested_id == -1) or (requested_id == parid):
                    error_string = ""
                    if self.get_error(parid) != None:
                        error_string = ", *** Error Pending: " + self.get_error(parid)
                    print ( str(parid) + ": " + self.get_name(parid) + " = " + str(val) + " = " + self.get_expr ( parid, to_py=True ) + " = " + self.get_expr ( parid, to_py=False ) + 
                            ", " + self.get_name(parid) + " depends on " + str(self.get_depend_list(parid)) +   # " = " + str(self.get_depend_dict(parid)) +
                            ", " + self.get_name(parid) + " is referenced by " + str(self.get_dependents_list(parid)) + error_string )

        except:
            print ( "==> Evaluation Exception: " + str ( sys.exc_info() ) )
            if prnt:
                print ( "  Error in statement:   " + self.get_name(parid) + " = " + self.get_error(parid) )
                print ( "    ... interpreted as: " + py_statement )


    

    def eval_all ( self, prnt=False, requested_id=None ):
        """ Evaluate all parameters based on dependencies. """
        # from math import *
        from math import sqrt, exp, log, log10, sin, cos, tan, asin, acos, atan, ceil, floor  # abs, max, and min are not from math?
        from random import uniform, gauss
        
        # Start by marking all parameters as invalid

        for parid in self.ID_name_dict:
            self.ID_valid_dict[parid] = False
        
        # Loop through all parameters over and over evaluating those parameters with valid dependencies
        
        #if prnt:
        #    print ( "================= Begin eval_all_depend =============================================================" )

        num_passes = 0
        all_valid = False

        while (num_passes <= len(self.ID_name_dict)) and (all_valid == False):

            num_passes = num_passes + 1
            # print ( "Pass = " + str(num_passes) )

            # Visit each parameter and try to update it as needed
            for parid in self.ID_name_dict:
                # Check to see if this parameter can be updated based on its dependencies all being valid
                dep_list = self.get_depend_list ( parid )
                dep_satisfied = True
                for dep_id in dep_list:
                    if not self.ID_valid_dict[dep_id]:
                        dep_satisfied = False
                        break
                if dep_satisfied:
                    # It's OK to evaluate this parameter
                    
                    # It would be nice if this were a function call, but couldn't get it to work

                    something_changed = False
                    py_statement = ""
                    try:
                        py_statement = str(str(self.get_name(parid))) + " = " + str(self.get_expr ( parid, to_py=True ))
                        # print ( "Before executing " + py_statement )
                        exec ( py_statement )
                        val = eval ( self.get_name(parid), locals() )
                        # print ( "After executing " + py_statement )
                        
                        # Check for changes ...
                        if parid in self.ID_value_dict:
                            # The parameter is already there, so check if it's different
                            if str(val) != self.ID_value_dict[parid]:
                                something_changed = True
                        else:
                            # If it wasn't there, then this is a change!!
                            something_changed = True

                        self.ID_value_dict.update ( { parid : str(val) } )
                        if (requested_id == parid):
                            requested_val = val
                        if prnt:
                            #print ( "requested_id = " + str(requested_id) )
                            if (requested_id == None) or (requested_id == -1) or (requested_id == parid):
                                error_string = ""
                                if self.get_error(parid) != None:
                                    error_string = ", *** Error Pending: " + self.get_error(parid)
                                print ( str(parid) + ": " + self.get_name(parid) + " = " + str(val) + " = " + self.get_expr ( parid, to_py=True ) + " = " + self.get_expr ( parid, to_py=False ) + 
                                        ", " + self.get_name(parid) + " depends on " + str(self.get_depend_list(parid)) +   # " = " + str(self.get_depend_dict(parid)) +
                                        ", " + self.get_name(parid) + " is referenced by " + str(self.get_dependents_list(parid)) + error_string )

                    except:
                        print ( "==> Evaluation Exception: " + str ( sys.exc_info() ) )
                        if prnt:
                            print ( "  Error in statement:   " + self.get_name(parid) + " = " + self.get_error(parid) )
                            print ( "    ... interpreted as: " + py_statement )

                    self.ID_valid_dict[parid] = True

            # Check to see if they're all valid yet
            all_valid = True
            for parid in self.ID_name_dict:
                if not self.ID_valid_dict[parid]:
                    all_valid = False
                    break

        # End While

        # Check to see if they all got updated or not
        all_valid = True
        for parid in self.ID_name_dict:
            if not self.ID_valid_dict[parid]:
                all_valid = False
                break
        
        if not all_valid:
            print ( "!!!!!!!!! WARNING: CIRCULAR REFERENCE !!!!!!!!!!!!" )

        #if prnt:
        #    print ( "================= End eval_all_depend =============================================================" )



    def parse_param_expr ( self, param_expr ):
        """ Converts a string expression into a list expression with variable parid's as integers and all others as strings
            Returns either a list (if successful or None if there is an error
            Example:
              Expression: "A * (B + C)" becomes something like: [ 3, "*", "(", 22, "+", 5, ")", "" ]
                 where 3, 22, and 5 are the ID numbers for parameters A, B, and C respectively
              Note that the parsing may produce empty strings in the list which should not cause any problem.
        """
        param_expr = param_expr.strip()
        st = None
        pt = None
        try:
            st = parser.expr(param_expr)
            pt = st.totuple()
        except:
            print ( "==> Parsing Exception: " + str ( sys.exc_info() ) )

        parameterized_expr = None  # param_expr
        if pt != None:
        
            parameterized_expr = self.recurse_tree_symbols ( pt, [] )
            
            if parameterized_expr != None:
            
                # Remove trailing empty strings from parse tree - why are they there?
                while len(parameterized_expr) > 0:
                    if parameterized_expr[-1] != '':
                        break
                    parameterized_expr = parameterized_expr[0:-2]

        return parameterized_expr


    def recurse_tree_symbols ( self, pt, current_expr ):
        """ Recurse through the parse tree looking for "terminal" items which are added to the list """

        if type(pt) == tuple:
            # This is a tuple, so find out if it's a terminal leaf in the parse tree

            #print ( "recurse_tree_symbols with a tuple (", current_expr, ")" )
            #print ( "  pt = ", str(pt) )

            terminal = False
            if len(pt) == 2:
                if type(pt[1]) == str:
                    terminal = True

            if terminal:
                # This is a 2-tuple with a type and value
                if pt[0] == token.NAME:
                    if pt[1] in self.EXPRESSION_KEYWORDS:
                        # This is a recognized name and not a user-defined symbol
                        return current_expr + [ pt[1] ]
                    else:
                        # This must be a user-defined symbol
                        par_id = -1
                        if pt[1] in self.name_ID_dict:
                            par_id = self.name_ID_dict[pt[1]]
                        return current_expr + [ par_id ]
                else:
                    # This is a non-name part of the expression
                    return current_expr + [ pt[1] ]
            else:
                # Break it down further
                for i in range(len(pt)):
                    next_segment = self.recurse_tree_symbols ( pt[i], current_expr )
                    if next_segment != None:
                        current_expr = next_segment
                return current_expr
        return None
    

###############   T E S T    C O D E   ##################

if __name__ == "__main__":

    import traceback
    import sys
    import pickle

    ps = ParameterSpace()

    s = "?" # Initialize with the command for help
    while True:
        try:
            s = s.strip()
            if s == '?':
                print ( "" )
                print ( " Expression Keywords: MDL = Python" )
                ps.print_keywords()
                print ( "" )
                print ( " Commands:" )
                print ( "  ? : Print help" )
                print ( "  \ : Dump All Parameters" )
                print ( "  ! : Dump Parameters object as a pickled string" )
                print ( "  param = expression : Assign expression to parameter" )
                print ( "  param : Evaluate param" )
                print ( "  old @ new : Rename parameter old to new" )
                print ( "  # n: Generate n parameters where each is the sum of the preceding 3" )
                print ( "  .par : Delete Parameter par" )
                print ( "  . : Delete All Parameters" )
                print ( "  Control-C : Exit program" )
                print ( "" )
            elif '=' in s:
                # Perform an assignment
                sparts = s.split('=')
                lhs = sparts[0].strip()
                rhs = sparts[1].strip()
                if len(lhs) == 0:
                    lhs = None
                parid = ps.define ( lhs, rhs )
                ps.eval_all(True, parid)
                    
            elif s == '\\':
                # Dump all parameters
                ps.dump(True)
            elif s == '!':
                # Dump all parameters as a pickled object
                s = pickle.dumps(ps,protocol=0)
                print ( "Length = " + str(len(s)) + ", String = ", s )
            elif s == '.':
                # Delete all parameters
                print ( "Deleting all" )
                ps.delete_all()
            elif (len(s) > 0) and (s[0] == '#'):
                # Delete selected parameter
                count = int(s[1:].strip())
                print ( "Generating " + str(count) + " parameters" )
                for i in range(count):
                    name = ("p%s" % i)
                    if i == 0:
                        expr = "1"
                    else:
                        expr = ""
                        n = min(i,3)  # Constant value limits the number of parameters in each expression
                        for j in range(n):
                            if j > 0:
                                expr = expr + "+"
                            expr = expr + ("p%s" % (j+i-n))
                    ps.define ( name, expr )
                ps.eval_all(True)
            elif (len(s) > 0) and (s[0] == '.'):
                # Delete selected parameter
                name = s[1:].strip()
                print ( "Deleting " + name )
                parid = ps.get_id ( name )
                if parid < 0:
                    print ( "Unable to delete " + name + " because it is not a valid parameter name" )
                else:
                    ok = ps.delete ( parid )
                    if not ok:
                        print ( "Unable to delete " + name + " because it is used by " + str(ps.get_dependents_names(parid)) )
            elif (len(s) > 0) and ("@" in s):
                # Rename old to new
                old,new = s.split("@")
                old = old.strip()
                new = new.strip()
                print ( "Renaming " + old + " to " + new )
                ok = ps.rename ( old, new )
                if not ok:
                    print ( "Unable to rename " + old + " to because it is not a valid parameter name" )
            elif s != '':
                # Assume s is a parameter name to print
                req_id = ps.get_id ( s )
                ps.eval_all(True, req_id)
            else:
                # Print all parameters
                ps.eval_all(True)
        except KeyboardInterrupt:
            print ( "Exiting" )
            sys.exit(0)
        except:
            print ( "Error: " + str(sys.exc_info()) )
            print ( traceback.format_exc() )
        # The following is a work around for Python 3 which no longer has raw_input!!!!
        try:
            # In pre-python 3, raw_input is defined
            input = raw_input
        except NameError:
            # In python 3, raw_input is NOT defined, but now has an "input" function to use instead
            pass
        s = input ( "Enter a parameter statement > " )


