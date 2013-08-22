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

    """ Encapsulate a parameter space with mutable parameter names associated with parameter expressions
        IDs currently run from 1 to n, with negative IDs typically indicating an error and ID 0 unused
    """

    def __init__ ( self ):
        """ Initialize a new ParameterSpace """
        #print ( "ParameterSpace.__init__() called" )
        self.VERSION = self.get_version()
        self.EXPRESSION_KEYWORDS = { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' }
        self.UNDEFINED_NAME = "   (0*1111111111*0)   "
        self.init_param_space()

    def get_version ( self ):
        return ( 1 )  # N O T E: This constant is in the function to keep it from being saved when pickling!!!
    
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
        self.ID_valu_dict = {}  # Maps IDs to their current value as a string
        self.ID_edit_dict = {}  # When not None this contains an expression that needs further editing because it is in error
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
            print ( "  ID->valu = " + str(self.ID_valu_dict) )
            print ( "  ID->text = " + str(self.ID_edit_dict) )
            for i in self.ID_name_dict:
                #print ( "    " + str(self.ID_name_dict[i]) + " = " + str(self.ID_valu_dict[i]) + " = " + self.get_expr(i) + " = " + self.get_expr(i,to_py=True) + " = " + str(self.ID_expr_dict[i]) )

                print ( "    " + str(self.ID_name_dict[i])  )
                print ( "    " + str(self.ID_valu_dict[i]) )
                print ( "    " + self.get_expr(i) )
                print ( "    " + self.get_expr(i,to_py=True) )
                print ( "    " + str(self.ID_expr_dict[i]) )

                #print ( "    " + str(self.ID_name_dict[i]) + " = " + self.get_expr(i) + " = " + self.get_expr(i,to_py=True) + " = " + str(self.ID_expr_dict[i]) )
            self.eval_all(True)


    def print_keywords ( self ):
        for mdl_keyword in self.EXPRESSION_KEYWORDS:
            print ( "  " + mdl_keyword + " = " + self.EXPRESSION_KEYWORDS[mdl_keyword] )


    def define ( self, name, expr ):
        """ Define a parameter ... may be new or may overwrite an existing parameter"""
        """ Return the ID of this parameter whether it's new or not """
        # print "Define: " + str(name) + " = " + str(expr)
        if name == None:
            # Try to choose a name with this mext ID if possible, but search further as needed
            next_unused_number = self.next_id
            while self.get_id( "P%d" % (next_unused_number) ) >= 0:
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
            self.set_expr ( this_id, expr )
            self.next_id += 1
        return this_id


    def get_dependents_list ( self, id ):
        """ Return a list of all parameter ids that reference this parameter id directly """
        dependents = []
        for test_id in self.ID_expr_dict:
            exp_list = self.ID_expr_dict[test_id]
            for token in exp_list:
                if type(token) == int:
                    if token == id:
                        dependents = dependents + [ test_id ]
                        break
        return dependents


    def get_dependents_names ( self, id ):
        """ Return a list of all parameter names that reference this parameter id directly """
        dlist = self.get_dependents_list(id)
        if len(dlist) > 0:
            dlist = [self.get_name(i) for i in dlist]
        return dlist


    def absolute_delete ( self, id ):
        """ Delete a parameter """
        name = self.get_name ( id )
        if name != None:
            self.name_ID_dict.pop(name)
            self.ID_name_dict.pop(id)
            self.ID_expr_dict.pop(id)
            self.ID_valu_dict.pop(id)
            self.ID_edit_dict.pop(id)
            if len(self.name_ID_dict) <= 0:
                # Reset the ID numbers when the list becomes empty
                self.next_id = 1

    def delete ( self, id ):
        """ Delete a parameter only if it has no dependencies """
        dependents = self.get_dependents_list(id)
        if len(dependents) == 0:
          self.absolute_delete ( id )
          return True
        else:
          return False


    def get_id ( self, name ):
        """ Get the ID of a parameter by name """
        if (len(self.name_ID_dict) > 0) and (name in self.name_ID_dict):
            return self.name_ID_dict[name]
        else:
            return -1


    def get_name ( self, id ):
        """ Get the name of the parameter with the specified ID """
        if id in self.ID_name_dict:
            return self.ID_name_dict[id]
        else:
            return None


    def set_name ( self, id, name ):
        """ Change the name of the parameter for the specified ID """
        old_name = self.get_name ( id )
        if old_name != None:
            self.ID_name_dict.update ( { id : name } )
            self.name_ID_dict.update ( { name : self.name_ID_dict.pop(old_name) } )


    def set_expr ( self, id, expr ):
        """ Store original text and parse and store the expression for the specified parameter ID """
        self.ID_edit_dict.update ( { id : expr } )
        parsed_expr = self.parse_param_expr ( expr )
        self.ID_expr_dict.update ( { id : parsed_expr } )
        self.eval_all()
        self.ID_valu_dict.update ( { id : self.get_value(id) } )


    def get_text ( self, id ):
        """ Get the original text expression for the specified parameter ID """
        if id in self.ID_edit_dict:
            return self.ID_edit_dict[id]
        else:
            return ""

    def get_value ( self, id ):
        """ Get the current value for the specified parameter ID """
        if id in self.ID_valu_dict:
            return self.ID_valu_dict[id]
        else:
            return ""

    def get_expr ( self, id, to_py=False, prefix='', suffix='' ):
        """ Construct a string representation of the expression by substituting symbols for IDs """
        exp_list = self.ID_expr_dict[id]
        expr = ""
        for token in exp_list:
            if type(token) == int:
                # This is an integer id, so look up the variable name to concatenate
                if token in self.ID_name_dict:
                    expr = expr + (prefix + self.ID_name_dict[token] + suffix)
                else:
                    expr = expr + self.UNDEFINED_NAME
            else:
                # This is a string so simply concatenate it after translation as needed
                if to_py and (token in self.EXPRESSION_KEYWORDS):
                    expr = expr + self.EXPRESSION_KEYWORDS[token]
                else:
                    expr = expr + token
        return expr

    def get_depend_list ( self, id ):
        """ Construct a list of ids that this id depends upon (or is a function of) """
        exp_list = self.ID_expr_dict[id]
        depends_on = set ( [] )
        for token in exp_list:
            if type(token) == int:
                depends_on.add ( token )
        return [ x for x in depends_on ]


    def get_depend_dict ( self, id ):
        """ Construct a dictionary of ids and names that this id depends upon (or is a function of) """
        exp_list = self.ID_expr_dict[id]
        depends_on = {}
        for token in exp_list:
            if type(token) == int:
                depends_on.update ( {token : self.get_name(token)} )
        return depends_on


    def eval_all ( self, prnt=False, requested_id=-1 ):
        """ Evaluate all parameters in order, printing either a requested ID or all (-1) when prnt is True """
        # from math import *
        from math import sqrt, exp, log, log10, sin, cos, tan, asin, acos, atan, ceil, floor  # abs, max, and min are not from math?
        from random import uniform, gauss

        # The following prefix and suffix are used to ensure that parameter names (like "if" and "def") are not interpreted as python keywords.
        # Note that this works with evaluation, but the parsing itself still fails when certain names (like "if" and "def") are used.
        prefix = ''   # 'cellblender_'
        suffix = ''   # '_cellblender'

        requested_val = 0
        if prnt and (requested_id<0):
            print ( "==============================================================================" )

        for id in self.ID_name_dict:
            py_statement = (prefix + self.get_name(id) + suffix) + " = " + self.get_expr ( id, to_py=True, prefix=prefix, suffix=suffix )
            try:
                exec ( py_statement )
                val = eval ( (prefix + self.get_name(id) + suffix), locals() )
                self.ID_valu_dict.update ( { id : str(val) } )
                if (requested_id == id):
                    requested_val = val
                if prnt:
                    if (requested_id == -1) or (requested_id == id):
                        print ( self.get_name(id) + " = " + str(val) + " = " + self.get_expr ( id, to_py=True ) + " = " + self.get_expr ( id, to_py=False ) + 
                                ", " + self.get_name(id) + " depends on " + str(self.get_depend_list(id)) +   # " = " + str(self.get_depend_dict(id)) +
                                ", " + self.get_name(id) + " is referenced by " + str(self.get_dependents_list(id)) )

            except:
                print ( "==> Evaluation Exception: " + str ( sys.exc_info() ) )
                if prnt:
                    print ( "  Error in statement:   " + self.get_name(id) + " = " + self.get_text(id) )
                    print ( "    ... interpreted as: " + py_statement )

        if prnt and (requested_id<0):
            print ( "==============================================================================" )

        return requested_val



    def rename ( self, old_name, new_name ):
        id = self.get_id ( old_name )
        if id < 0:
            # Old name doesn't exist so it can't be renamed
            return False
        else:
            new_id = self.get_id ( new_name )
            if new_id >= 0:
                # New name already exists so a duplicate name can't be created
                return False
            else:
                # It's ok to rename, so update the two dictionaries that associate names and IDs
                self.ID_name_dict.update ( { id : new_name } )
                self.name_ID_dict.update ( { new_name : self.name_ID_dict.pop(old_name) } )
                return True


    def parse_param_expr ( self, param_expr ):
        """ Converts a string expression into a list expression with variable id's as integers and all others as strings
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

        parameterized_expr = param_expr
        if pt != None:
        
            parameterized_expr = self.recurse_tree_symbols ( pt, [] );
            
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
                print ( "  .par : Delete Parameter par" )
                print ( "  . : Delete All Parameters" )
                print ( "  Control-C : Exit program" )
                print ( "" )
            elif '=' in s:
                # Perform an assignment
                sparts = s.split('=')
                ps.define ( sparts[0].strip(), sparts[1].strip() )
                ps.eval_all(True, ps.get_id(sparts[0].strip()))
            elif s == '\\':
                # Dump all parameters
                ps.dump(True)
            elif s == '!':
                # Dump all parameters as a pickled object
                print ( pickle.dumps(ps) )
            elif s == '.':
                # Delete all parameters
                print ( "Deleting all" )
                ps.delete_all()
            elif (len(s) > 0) and (s[0] == '.'):
                # Delete selected parameter
                name = s[1:].strip()
                print ( "Deleting " + name )
                id = ps.get_id ( name )
                if id < 0:
                    print ( "Unable to delete " + name + " because it is not a valid parameter name" )
                else:
                    ok = ps.delete ( id )
                    if not ok:
                        print ( "Unable to delete " + name + " because it is used by " + str(ps.get_dependents_names(id)) )
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


