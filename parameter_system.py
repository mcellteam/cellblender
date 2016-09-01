"""
This module supports parameters and evaluation of expressions.
"""


"""
### This CellBlender Data Model script can generate parameters for testing

num_pars_to_gen = 20
num_back = 2
make_loop = False

import cellblender as cb

dm = cb.get_data_model()

def make_par_name ( n ):
    name = None
    if n < 26:
        name = chr(ord('a')+n)
    else:
        name = "P_" + str(n)
    if (n % 3) == 0:
        name += 'x'
    if (n % 3) == 1:
        name += 'y'
    return name

pars = []
for n in range(num_pars_to_gen):
    pname = make_par_name ( n )
    par = {}
    par['par_name'] = pname
    par['par_description'] = "Description for " + pname
    par['par_units'] = "u"
    par['par_expression'] = "1"
    for i in range(max(n-num_back,0),n):
        par['par_expression'] += " + "
        par['par_expression'] += make_par_name ( i )
    pars.append ( par )

if make_loop:
    mid = round(num_pars_to_gen / 2)
    print ( " mid = " + str(mid) )
    if (mid-1) >= 0:
        # There are enough parameters to make a loop
        pars[mid-1]['par_expression'] += " + " + pars[mid]['par_name']

dm['mcell']['parameter_system'] = { 'model_parameters':pars }

cb.replace_data_model ( dm )

"""

#Handy debugging line:  __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

import bpy
from bpy.props import *
from math import *
from random import uniform, gauss
import parser
import re
import token
import symbol
import sys
import pickle
import time
import io

import inspect

def dbprint ( s, thresh=1 ):   # Threshold high means no printing, Threshold low (or negative) means lots of printing
    ps = bpy.context.scene.mcell.parameter_system
    if ps.debug_level >= thresh:
        print ( s )



####################### Start of Profiling Code #######################

# From: http://wiki.blender.org/index.php/User:Z0r/PyDevAndProfiling

prof = {}

# Defines a dictionary associating a call name with a list of 3 (now 4) entries:
#  0: Name
#  1: Duration
#  2: Count
#  3: Start Time (for non-decorated version)

class profile:
    ''' Function decorator for code profiling.'''

    def __init__(self,name):
        self.name = name

    def print_call_stack(self):
        frame = inspect.currentframe()
        call_list_frames = inspect.getouterframes(frame)
        filtered_frames = [ {"function":f.function, "line":f.lineno, "file":f.filename} for f in call_list_frames if not ( f.function in ("execute", "print_frame", "profile_fun", "draw", "draw_self", "draw_layout") ) ]
        
        if len(filtered_frames) > 0:
            filtered_frames.reverse()
            s = ""
            last_call = ""
            num_repeat = 0
            sep = " ->  "
            for f in filtered_frames:
                # this_call = str(f["function"]) + '[' + str(f["line"]) + ' in ' + str(f["file"].split('/')[-1].split('.')[0]) + ']'
                this_call = str(f["function"]).strip()
                if this_call == last_call:
                    num_repeat += 1
                else:
                    repeat_str = num_repeat * "*"
                    #if len(repeat_str) > 0:
                    #    repeat_str = " " + repeat_str + " "
                    s += last_call + repeat_str + sep
                    num_repeat = 0
                    last_call = this_call
                # print ( "    Frame: " + str(f.function) + " at " + str(f.lineno) + " in "  + str(f.filename.split('/')[-1].split('.')[0]) )
            if num_repeat > 0:
                s += last_call + (num_repeat * "*") + sep
            s = s[len(sep):-len(sep)]
            if len(s) > 0:
                print ( s )

        del filtered_frames
        del call_list_frames
        del frame

    def __call__(self,fun):
        def profile_fun(*args, **kwargs):
            #self.print_call_stack()               # This will print the call stack as each function is called
            start = time.clock()
            try:
                return fun(*args, **kwargs)
            finally:
                duration = time.clock() - start
                if fun in prof:
                    prof[fun][1] += duration
                    prof[fun][2] += 1
                else:
                    prof[fun] = [self.name, duration, 1, 0]
        return profile_fun

# Builds on the previous profiling code with non-decorated versions (needed by some Blender functions):
#  0: Name
#  1: Duration
#  2: Count
#  3: Start Time (for non-decorated version)

def start_timer(fun):
    start = time.clock()
    if fun in prof:
        prof[fun][2] += 1
        prof[fun][3] = start
    else:
        prof[fun] = [fun, 0, 1, start]

def stop_timer(fun):
    stop = time.clock()
    if fun in prof:
        prof[fun][1] += stop - prof[fun][3]   # Stop - Start
        # prof[fun][2] += 1
    else:
        print ( "Timing Error: stop called without start!!" )
        pass


def print_statistics(app):
    '''Prints profiling results to the console,
       appends to plot files,
       and generates plotting and deleting scripts.'''

    print ( "=== Execution Statistics with " + str(len(app.parameter_system.general_parameter_list)) + " general parameters and " + str(len(app.parameter_system.panel_parameter_list)) + " panel parameters ===" )

    def timekey(stat):
        return stat[1] / float(stat[2])

    stats = sorted(prof.values(), key=timekey, reverse=True)

    print ( '{:<55} {:>7} {:>7} {:>8}'.format('FUNCTION', 'CALLS', 'SUM(ms)', 'AV(ms)'))
    for stat in stats:
        print ( '{:<55} {:>7} {:>7.0f} {:>8.2f}'.format(stat[0],stat[2],stat[1]*1000,(stat[1]/float(stat[2]))*1000))
        f = io.open(stat[0]+"_plot.txt",'a')
        #f.write ( str(len(app.parameter_system.general_parameter_list)) + " " + str((stat[1]/float(stat[2]))*1000) + "\n" )
        f.write ( str(len(app.parameter_system.general_parameter_list)) + " " + str(float(stat[1])*1000) + "\n" )
        f.flush()
        f.close()

    f = io.open("plot_command.bat",'w')
    f.write ( "java -jar data_plotters/java_plot/PlotData.jar" )
    for stat in stats:
        f.write ( " fxy=" + stat[0]+"_plot.txt" )
    f.flush()
    f.close()

    f = io.open("delete_command.bat",'w')
    for stat in stats:
        f.write ( "rm -f " + stat[0]+"_plot.txt\n" )
    f.flush()
    f.close()


class MCELL_OT_print_profiling(bpy.types.Operator):
    bl_idname = "mcell.print_profiling"
    bl_label = "Print Profiling"
    bl_description = ("Print Profiling Information")
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.mcell
        print_statistics(app)
        return {'FINISHED'}

    def invoke(self, context, event):
        app = context.scene.mcell
        print_statistics(app)
        return {'RUNNING_MODAL'}


class MCELL_OT_clear_profiling(bpy.types.Operator):
    bl_idname = "mcell.clear_profiling"
    bl_label = "Clear Profiling"
    bl_description = ("Clear Profiling Information")
    bl_options = {'REGISTER'}

    def execute(self, context):
        prof.clear()
        return {'FINISHED'}

    def invoke(self, context, event):
        prof.clear()
        return {'RUNNING_MODAL'}



####################### End of Profiling Code #######################


#####################################################################
#  Forced update operators (may be commented out when not used)
#####################################################################

#class MCELL_OT_update_general(bpy.types.Operator):
#    bl_idname = "mcell.update_general"
#    bl_label = "Update General Parameters"
#    bl_description = "Update all General Parameters"
#    #bl_options = {'REGISTER', 'UNDO'}
#    bl_options = {'REGISTER' }
#    def execute(self, context):
#        mcell = context.scene.mcell
#        ps = mcell.parameter_system
#        ps.evaluate_all_gp_expressions ( context )
#        return {'FINISHED'}


#class MCELL_OT_update_panel(bpy.types.Operator):
#    bl_idname = "mcell.update_panel"
#    bl_label = "Update Panel Parameters"
#    bl_description = "Update all Panel Parameters"
#    #bl_options = {'REGISTER', 'UNDO'}
#    bl_options = {'REGISTER' }
#    def execute(self, context):
#        mcell = context.scene.mcell
#        ps = mcell.parameter_system
#        dbprint ( "This doesn't do anything at this time" )
#        return {'FINISHED'}



#####################################################################
#  Operators for printing and debugging
#####################################################################

class MCELL_OT_print_gen_parameters(bpy.types.Operator):
    bl_idname = "mcell.print_gen_parameters"
    bl_label = "Print General Parameters"
    bl_description = "Print All General Parameters"
    #bl_options = {'REGISTER', 'UNDO'}
    bl_options = {'REGISTER' }
    
    def print_subdict ( self, pname, item, depth ):
        if len(item.keys()) <= 0:
            print ( "  " + ("  "*depth) + pname + " = {}" )
        else:
            for k in item.keys():
                if str(type(item[k])) == "<class 'IDPropertyGroup'>":
                    self.print_subdict ( pname + "." + str(k), item[k], depth+1 )
                else:
                    print ( "  " + ("  "*depth) + pname + "." + str(k) + " = " + str(item[k]) )


    def print_items (self, d, ps):
        #self.print_subdict ( 'gp_dict', d, 0 )
        fw = ps.max_field_width
        for k in d.keys():
            output = "  " + str(k) + " = "
            item = d[k]

            if 'name' in item:
                output += str(item['name']) + " = "

            if 'elist' in item:
                elist = pickle.loads(item['elist'].encode('latin1'))
                output += str(elist) + " = "

            if str(type(item)) == "<class 'IDPropertyGroup'>":
                # output += str(item.to_dict())
                ditem = item.to_dict()
                output += "{ "
                for dk in ditem.keys():
                    ditem_str = str(ditem[dk])
                    if dk == 'elist':
                        #ditem_str = str(pickle.loads(ditem[dk].encode('latin1')))
                        ditem_str = str(ditem[dk]).replace('\n',' ')
                    if type(ditem[dk]) == type('abc'):
                        ditem_str = "\"" + ditem_str + "\""
                    output += str(dk) + ":" + ps.shorten_string(ditem_str,fw) + "  "  # ", "
                if len(output) > 2:
                    # Strip off the last ", "
                    output = output[0:-2]
                output += " }"
            else:
                output += str(item)
            print ( output )

    def execute(self, context):
        #global global_params
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        # ps.init_parameter_system()

        print ( "=== ID Parameters ===" )

        if 'gp_dict' in ps:
            self.print_items ( ps['gp_dict'], ps )

        print ( "  = Ordered Evaluation List =" )

        if 'gp_ordered_list' in ps:
          ols = ""
          for k in ps['gp_ordered_list']:
            ols += str(k) + " "
          print ( "    " + ols )

        return {'FINISHED'}



class MCELL_OT_print_pan_parameters(bpy.types.Operator):
    bl_idname = "mcell.print_pan_parameters"
    bl_label = "Print Panel Parameters"
    bl_description = "Print All Panel Parameters"
    bl_options = {'REGISTER' }

    def execute(self, context):
        #global global_params
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        fw = ps.max_field_width
        # ps.init_parameter_system()

        print ( "=== RNA Panel Parameters ===" )

        ppl = ps.panel_parameter_list
        for k in ppl.keys():
            pp = ppl[k]
            # pp is an RNA property, so the ID properties (and keys) might not exist yet ... prefer RNA references
            s  = ""
            s += "  " + ps.shorten_string(str(pp.name),fw)
            s += " = " + ps.shorten_string(str(pp['user_name']),fw)
            s += " = \"" + ps.shorten_string(str(pp.expr),fw) + "\""
            elist = pickle.loads(pp.elist.encode('latin1'))
            s += ",  elist : \"" + ps.shorten_string(str(elist),fw) + "\""
            v = "??"
            if 'value' in pp:
                v = str(pp['value'])
            s += "  value : " + v + ""
            for pk in pp.keys():
                if not (pk in ['name', 'user_name', 'expr', 'elist', 'value']):
                    v = ps.shorten_string(str(pp[pk]),fw)
                    if type(pp[pk]) == type('abc'):
                        v = "\"" + v + "\""
                    s += "  " + str(pk) + " : " + v
            s += "  elistp : \"" + ps.shorten_string(str(pp.elist),fw) + "\""
            print ( s.replace('\n',' ') )

        return {'FINISHED'}



class MCELL_OT_add_par_list(bpy.types.Operator):
    bl_idname = "mcell.add_par_list"
    bl_label = "Add List"
    bl_description = "Add a short list of parameters"
    bl_options = {'REGISTER'}

    def make_par_name ( self, n ):
        name = None
        if n < 26:
            name = chr(ord('a')+n)
        else:
            name = "P_" + str(n)
        """
        # These were helpful for testing filtering (by "x" or "y", for example)
        if (n % 3) == 0:
            name += 'x'
        if (n % 3) == 1:
            name += 'y'
        """
        return name

    def execute(self, context):
        num_pars_to_gen = context.scene.mcell.parameter_system.num_pars_to_gen
        num_back = context.scene.mcell.parameter_system.num_pars_back
        make_loop = False

        pars = []
        for n in range(num_pars_to_gen):
            pname = self.make_par_name ( n )
            par = {}
            par['par_name'] = pname
            par['par_description'] = "Description for " + pname
            par['par_units'] = "u"
            par['par_expression'] = "1"
            if n > 0:
                par['par_expression'] = "a"
            for i in range(max(n-num_back,0),n):
                if i % 2:
                    par['par_expression'] += " - "
                else:
                    par['par_expression'] += " + "
                par['par_expression'] += self.make_par_name ( i )
            pars.append ( par )

        if make_loop:
            mid = round(num_pars_to_gen / 2)
            dbprint ( " mid = " + str(mid) )
            if (mid-1) >= 0:
                # There are enough parameters to make a loop
                pars[mid-1]['par_expression'] += " + " + pars[mid]['par_name']

        dbprint ( "Before call to add_general_parameters_from_list" )
        context.scene.mcell.parameter_system.add_general_parameters_from_list ( context, pars )
        dbprint ( "After call to add_general_parameters_from_list" )
        return {'FINISHED'}



#####################################################################
#  Operators for adding and removing parameters
#####################################################################


class MCELL_OT_add_parameter(bpy.types.Operator):
    bl_idname = "mcell.add_parameter"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        context.scene.mcell.parameter_system.add_general_parameter()
        return {'FINISHED'}

class MCELL_OT_remove_parameter(bpy.types.Operator):
    bl_idname = "mcell.remove_parameter"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        status = context.scene.mcell.parameter_system.remove_active_parameter(context)
        if status != "":
            self.report({'ERROR'}, status)
        return {'FINISHED'}

class MCELL_OT_remove_all_pars(bpy.types.Operator):
    bl_idname = "mcell.delete_all_pars"
    bl_label = "Delete All Pars"
    bl_description = "Delete All Parameters (that aren't used)"
    bl_options = {'REGISTER'}
    def execute(self, context):
        status = ""
        ps = context.scene.mcell.parameter_system
        num_deleted = 1
        while ( len(ps.general_parameter_list) > 0 ) and ( num_deleted > 0 ):
            # Delete from end since that's most likely to be the fastest
            num_before = len(ps.general_parameter_list)
            next_to_delete = len(ps.general_parameter_list) - 1
            dbprint ( "Deleting parameters starting with " + str(next_to_delete) )
            while next_to_delete >= 0:
                dbprint ( "  Deleting parameter " + str(next_to_delete) )
                ps.active_par_index = next_to_delete
                ps.remove_active_parameter(context)
                next_to_delete += -1
            num_deleted = num_before - len(ps.general_parameter_list)
        if len(ps.general_parameter_list) > 0:
            self.report({'ERROR'}, "Unable to delete all")
        return {'FINISHED'}




#######################################################################
#  Parameter Drawing Class - Displays each line in the parameter list
#######################################################################


class MCELL_UL_draw_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mcell = context.scene.mcell
        #icon = 'FILE_TICK'
        #layout.label("parameter goes here", icon=icon)
        ps = mcell.parameter_system

        par = ps.general_parameter_list[index]
        par_id = par.par_id
        id_par = ps['gp_dict'][par_id]
        
        disp = id_par['name'] + " = " + id_par['expr']
        if 'value' in id_par:
            disp += " = " + str(id_par['value'])
        else:
            disp += " = ??"
        icon = 'FILE_TICK'
        if 'status' in ps['gp_dict'][par_id]:
            status = ps['gp_dict'][par_id]['status']
            if 'undef' in status:
                icon='ERROR'
            elif 'loop' in status:
                icon='LOOP_BACK'
        layout.label(disp, icon=icon)



"""
#######################################################################
#  Top Level Panel for the Parameter System (not currently used)
#######################################################################

class MCELL_PT_parameter_system(bpy.types.Panel):
    bl_label = "CellBlender - Model Parameters"  # This names the collapse control at the top of the panel
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "ID Parameters"  # This is the tab name on the side

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)

    def draw(self, context):
        mcell = context.scene.mcell
        ps = mcell.parameter_system
        ps.draw_panel ( context, self.layout )
"""



#######################################################################
#  A Panel Parameter Data object exists for each panel parameter
#    They are stored in the panel_parameter_list CollectionProperty
#      within the ParameterSystemPropertyGroup
#######################################################################


### External callback needed to match the "update=" syntax of Blender.
### This just calls the function with the same name from within the class

##@profile('PanelParameterDataCallBack.update_panel_expression')  # profiling callbacks can be problematic
def update_panel_expr ( self, context ):
    self.update_panel_expression ( context )

class PanelParameterData ( bpy.types.PropertyGroup ):
    """ Holds the actual properties needed for a panel parameter """
    # There are only a few properties for items in this class ... most of the rest are in the parameter system itself.
    #self.name is a Blender defined key that should be set to the unique_static_name (new_pid_key) on creation (typically "p#")
    expr = StringProperty(name="Expression", default="0", description="Expression to be evaluated for this parameter", update=update_panel_expr)
    elist = StringProperty(name="elist", default="(lp0\n.", description="Pickled Expression List")  # This ("(lp0\n.") is a pickled empty list: pickle.dumps([],protocol=0).decode('latin1')
    show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    # The following PanelParameterData (PPD) ID properties are added dynamically (for performance reasons):

    #  PPD['user_name']
    #  PPD['user_type']
    #  PPD['user_units']
    #  PPD['user_descr']
    #  PPD['expr']
    #  PPD['value']
    #  PPD['valid']

    @profile('PanelParameterData.update_panel_expression')
    def update_panel_expression (self, context, gl=None):
        mcell = context.scene.mcell
        parameter_system = mcell.parameter_system
        dbprint ( "Update the panel expression for " + self.name + " with keys = " + str(self.keys()) )
        dbprint ( "Updating " + str(parameter_system.panel_parameter_list[self.name]) )

        parameter_system.init_parameter_system()  # Do this in case it isn't already initialized
        
        old_parameterized_expr = pickle.loads(self.elist.encode('latin1'))

        if True or (len(parameter_system['gp_dict']) > 0):
            dbprint ("Parameter string changed to " + self.expr, 10 )
            parameterized_expr = parameter_system.parse_param_expr ( self.expr )
            self.elist = pickle.dumps(parameterized_expr,protocol=0).decode('latin1')

            dbprint ("Parsed expression = " + str(parameterized_expr), 10 )
            if None in parameterized_expr:
                print ( "Error: None in " + str(parameterized_expr) )
                return

            # Check to see if any dependencies have changed

            old_who_i_depend_on = set ( [ 'g'+str(w) for w in old_parameterized_expr if type(w) == type(1) ] )
            new_who_i_depend_on = set ( [ 'g'+str(w) for w in parameterized_expr if type(w) == type(1) ] )
            
            if old_who_i_depend_on != new_who_i_depend_on:
            
                # Update the "what_depends_on_me" fields of the general parameters based on the changes

                dbprint ( "Old: " + str(old_who_i_depend_on) )
                dbprint ( "New: " + str(new_who_i_depend_on) )

                remove_me_from = old_who_i_depend_on - new_who_i_depend_on
                add_me_to = new_who_i_depend_on - old_who_i_depend_on

                if len(remove_me_from) > 0:
                    dbprint ( "Remove " + self.name + " from what_depends_on_me list for: " + str(remove_me_from), 10 )
                if len(add_me_to) > 0:
                    dbprint ( "Add " + self.name + " to what_depends_on_me list for: " + str(add_me_to), 10 )

                for k in remove_me_from:
                    dbprint ( "  Removing ( " + self.name + " ) from " + str(k), 10 )
                    parameter_system['gp_dict'][k]['what_depends_on_me'].pop ( self.name )
                for k in add_me_to:
                    parameter_system['gp_dict'][k]['what_depends_on_me'][self.name] = True

            # Recompute the value

            # Start by creating a dictionary of values from all general parameters if not passed in:
            valid = True
            if gl is None:
                gl = {}
                parameter_system.update_dependency_ordered_name_list() # This call is needed the first time
                valid = parameter_system.build_eval_dict ( gl )

            if not valid:
                print ( "Error: \"" + str(parameterized_expr) + "\" cannot be evaluated (1)" )
                self['valid'] = False
                self['value'] = 0.0
            else:
                py_expr = parameter_system.build_expression ( parameterized_expr, as_python=True )
                if (py_expr != None) and (len(py_expr.strip()) > 0):
                    self['valid'] = True
                    try:
                        self['value'] = float(eval(py_expr,globals(),gl))
                    except:
                        print ( "Error: \"" + str(py_expr) + "\" cannot be evaluated (2)" )
                        print ( "  Globals (gl) = " + str(gl) )
                        self['valid'] = False
                else:
                    # Empty parameters are intended to be interpreted as defaults by the code that uses them
                    # print ( "Error: \"" + str(py_expr) + "\" cannot be evaluated (3)" )
                    self['valid'] = False
                    self['value'] = 0.0
            # It's not clear if this should be integerized here or only on display. Retain full value for now.
            #if ('user_type' in self) and (self['user_type'] == 'i'):
            #    self['value'] = int(self['value'])




#######################################################################
#  A Panel Parameter Reference is just an ID that is stored wherever
#    a panel parameter is defined. That ID is the name index into the
#    the panel_parameter_list CollectionProperty within the top level
#    ParameterSystemPropertyGroup. The panel_parameter_list contains
#    the PanelParameterData items keyed by this ID.
#######################################################################


class Parameter_Reference ( bpy.types.PropertyGroup ):
    """ Simple class to reference a panel parameter - used throughout the application """
    # There is ONLY ONE property in this class ... don't add any more without careful thought
    unique_static_name = StringProperty ( name="unique_name", default="" )


    # __init__ does not appear to be called
    #def __init__ ( self ):
    #    print ( "Parameter_Reference.__init__ called" )


    # __del__ appears to be called all the time ... even when nothing is being added or removed
    #def __del__ ( self ):
    #    print ( "Parameter_Reference.__del__ called" )


    #######################################################################
    #  This is the function that actually creates the data associated with
    #    a panel parameter.
    #  The "type_name" was used in the past, and it is being preserved
    #    temporarily since it's used throughout CellBlender. Removing it
    #    prior to merging with the development branch will only cause
    #    additional headache at this time.
    #  The "user_int" parameter will probably change to "user_type" when we
    #    add string parameters giving: 'f', 'i', 's'.
    #######################################################################

    @profile('Parameter_Reference.init_ref')
    def init_ref ( self, parameter_system, type_name, user_name=None, user_expr="0", user_descr="Panel Parameter", user_units="", user_int=False ):

        parameter_system.init_parameter_system()  # Do this in case it isn't already initialized

        if user_name == None:
            user_name = "none"
        
        t = 'f'
        if user_int:
            t = 'i'

        new_pid = parameter_system.allocate_available_pid()
        new_pid_key = 'p'+str(new_pid)

        # Add special information for panel parameters:

        self.unique_static_name = new_pid_key

        new_rna_par = parameter_system.panel_parameter_list.add()
        new_rna_par.name = new_pid_key
        new_rna_par.expr = user_expr   # This should trigger an evaluation of the expression into an expression list

        new_rna_par['user_name'] = user_name
        new_rna_par['user_type'] = t
        new_rna_par['user_units'] = user_units
        new_rna_par['user_descr'] = user_descr
        #new_rna_par['expr'] = user_expr
        if (len(user_expr.strip()) > 0):
            new_rna_par['value'] = eval(user_expr)
            new_rna_par['valid'] = True
        else:
            new_rna_par['value'] = 0.0
            new_rna_par['valid'] = True
        dbprint ( 'Finished init_ref for ' + str(user_name) + ' = ' + str(new_pid_key) )
        #bpy.ops.mcell.print_gen_parameters()
        #bpy.ops.mcell.print_pan_parameters()
        dbprint ( "==============================================================================================" )



    #######################################################################
    #  This is the function that deletes the data associated with a panel
    #    parameter. This was not needed prior to ID properties because the
    #    RNA properties (supposedly) cleaned up after themselves. This is
    #    not the case with ID parameters, and this data must be removed.
    #  Nothing depends on panel parameters (they are leaves in the tree)
    #    so no dependencies need to be checked.
    #  However, the general parameters DO keep track of which panel
    #    parameters depend on them. This relationship is stored in their
    #    "what_depends_on_me" list. So removing a panel parameter requires
    #    clearing that panel parameter reference from each general parameter
    #    that is used by the panel parameter. This function does that.
    #######################################################################

    def clear_ref ( self, parameter_system ):
        dbprint ( "clear_ref for " + self.unique_static_name )
        ppl = parameter_system.panel_parameter_list
        if 'gp_dict' in parameter_system:
            gpd = parameter_system['gp_dict']
            rna_par = ppl[self.unique_static_name]

            # Start by removing this reference from the what_depends_on_me of any general parameters that it depends on
            if 'elist' in rna_par:
                elist = pickle.loads(rna_par['elist'].encode('latin1'))
                for term in elist:
                    if type(term) == int:
                        # This refers to a general parameter, so remove this panel parameter from its "what_depends_on_me" list
                        gp = gpd['g'+str(term)]
                        if self.unique_static_name in gp['what_depends_on_me']:
                            gp['what_depends_on_me'].pop(self.unique_static_name)

        # Now remove this parameter from the panel parameters list
        i = ppl.find(self.unique_static_name)
        if i >= 0:
            ppl.remove ( i )


    #######################################################################
    #  These are the general access functions used to set and get the
    #    parameter's expression and value. They take an optional plist
    #    argument that should be the panel parameter list. This is done
    #    to keep this function from looking it up when the list is already
    #    available in the calling function.
    #    The available access functions are:
    #      get_param  - Returns a PanelParameterData item for the parameter
    #      set_expr   - Sets the expression for the parameter
    #      get_expr   - Gets the expression for the parameter
    #      get_value  - Returns a numeric value for the parameter 
    #      get_as_string_or_value - Returns a string which might be
    #                               either a string expression or a
    #                               string representation of a number
    #######################################################################

    @profile('Parameter_Reference.get_param')
    def get_param ( self, plist=None ):
        #print ( "get_param called on Parameter_Reference " + str(self.unique_static_name) )

        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list   # <<<< This appears to be empty after rebuilding parameters from a data model
            # print ( "Inside get_param, len(ppl) = " + str(len(plist)) )
        return plist[self.unique_static_name]

    @profile('Parameter_Reference.set_expr')
    def set_expr ( self, expr, plist=None ):
        ##print ( "###############\n  set_expr for " + self.unique_static_name + " Error!!!\n###############\n" )
        rna_par = self.get_param(plist)
        rna_par.expr = expr
        return

    @profile('Parameter_Reference.get_expr')
    def get_expr ( self, plist=None ):
        ##print ( "###############\n  get_expr for " + self.unique_static_name + "\n###############\n" )
        rna_par = self.get_param(plist)
        ##print ( "###############\n    returning " + str(rna_par.expr) + "\n###############\n" )
        return rna_par.expr


    @profile('Parameter_Reference.get_value')
    def get_value ( self, plist=None ):
        #print ( "###############\n  get_value for " + self.unique_static_name + " Error!!!\n###############\n" )
        par = self.get_param()
        #print ( "Par.keys() = " + str(par.keys()) )
        #print ( "Par.items() = " + str(par.items()) )
        user_type = 'f'
        user_value = 0.0
        if 'user_type' in par:
            user_type = par['user_type']
        if 'value' in par:
            #print ( "Par[value] = " + str(par['value']) )
            if True or par['valid']:    # Force this to be valid for now
                if user_type == 'f':
                    user_value = float(par['value'])
                else:
                    user_value = int(par['value'])
            else:
                user_value = None
                user_type = ''
        #print ( "Returning " + str(user_value) )
        return user_value


    @profile('Parameter_Reference.get_as_string_or_value')
    def get_as_string_or_value ( self, plist=None, as_expr=False ):
        '''Return a string represeting the numeric value or a non-blank expression'''
        rna_par = self.get_param(plist)
        if as_expr and (len(rna_par.expr.strip()) > 0):
            return self.get_expr(plist)
        else:
            isint = False
            s = None
            if ('user_type' in rna_par) and (rna_par['user_type'] == 'i'):
                s = "%g" % (int(self.get_value(plist)))
            else:
                s = "%g" % (self.get_value(plist))
            return s


    #######################################################################
    #  This function draws a panel parameter in a panel "layout".
    #    This is the function that shows help, labels, double rows, etc.
    #######################################################################

    @profile('Parameter_Reference.draw')
    def draw ( self, layout, parameter_system, label=None ):

        row = layout.row()
        rna_par = parameter_system.panel_parameter_list[self.unique_static_name]

        val = "??"
        icon = 'ERROR'
        if 'value' in rna_par:
            if not (rna_par['value'] is None):
                if rna_par['user_type'] == 'i':
                    val = str(int(rna_par['value']))
                else:
                    val = str(rna_par['value'])
                icon = 'NONE'
        if 'valid' in rna_par:
            if not rna_par['valid']:
                val = "??"
                icon = 'ERROR'

        if len(rna_par['expr'].strip()) == 0:
            val = ""
            icon = 'NONE'

        if parameter_system.param_display_mode == 'one_line':
            split = row.split(parameter_system.param_label_fraction)
            col = split.column()
            col.label ( text=rna_par['user_name']+" = "+val, icon=icon )
            col = split.column()
            col.prop ( rna_par, "expr", text="", icon=icon )
            col = row.column()
            col.prop ( rna_par, "show_help", icon='INFO', text="" )
        elif parameter_system.param_display_mode == 'two_line':
            row.label ( text=rna_par['user_name']+" = "+val, icon=icon )
            row = layout.row()
            split = row.split(0.03)
            col = split.column()
            col = split.column()
            col.prop ( rna_par, "expr", text="", icon=icon )
            col = row.column()
            col.prop ( rna_par, "show_help", icon='INFO', text="" )

        if rna_par.show_help:
            # Draw the help information in a box inset from the left side
            row = layout.row()
            # Use a split with two columns to indent the box
            split = row.split(0.03)
            col = split.column()
            col = split.column()
            box = col.box()
            desc_list = rna_par['user_descr'].split("\n")
            for desc_line in desc_list:
                box.label (text=desc_line)
            if len(rna_par['user_units']) > 0:
                box.label(text="Units = " + rna_par['user_units'])
            if parameter_system.show_all_details:
                box = box.box()
                row = box.row()
                row.label ( "Paremeter ID: " + self.unique_static_name )
                parameter_system.draw_rna_par_details ( rna_par, box )



#######################################################################
#  External callbacks needed to match the "update=" syntax of Blender.
#  Blender's "update=" parameter cannot accept a class method, so there
#  must be a "global" method for each update. They mostly just call the
#  function with the same name from within the class. There is also a
#  problem with profiling of callbacks, so the profile is disabled.
#######################################################################


##@profile('ParameterSystemCallBack.update_parameter_index')  # profiling callbacks can be problematic
def update_parameter_index ( self, context ):
    self.update_parameter_index ( context, interactive=True )

##@profile('ParameterSystemCallBack.update_parameter_name')  # profiling callbacks can be problematic
def update_parameter_name ( self, context ):
    self.update_parameter_name ( context, interactive=True )
    context.scene.mcell.parameter_system.last_parameter_update_time = str(time.time())

##@profile('ParameterSystemCallBack.update_parameter_elist')  # profiling callbacks can be problematic
def update_parameter_elist ( self, context ):
    self.update_parameter_elist ( context, interactive=True )
    context.scene.mcell.parameter_system.last_parameter_update_time = str(time.time())

##@profile('ParameterSystemCallBack.update_parameter_expression')  # profiling callbacks can be problematic
def update_parameter_expression ( self, context ):
    self.update_parameter_expression ( context, interactive=True )
    context.scene.mcell.parameter_system.last_parameter_update_time = str(time.time())

##@profile('ParameterSystemCallBack.update_parameter_units')  # profiling callbacks can be problematic
def update_parameter_units ( self, context ):
    self.update_parameter_units ( context, interactive=True )

##@profile('ParameterSystemCallBack.update_parameter_desc')  # profiling callbacks can be problematic
def update_parameter_desc ( self, context ):
    self.update_parameter_desc ( context, interactive=True )



#######################################################################
#  The "general_parameter_list" is a Blender CollectionProperty which
#    must take an object type that is a subclass of PropertyGroup (see
#    "bpy.props.CollectionProperty" in documentation). This class is
#    just a PropertyGroup subclass to hold a StringProperty (par_id)
#    so that it can be included in a CollectionProperty.
#  The general_parameter_list is just a collection of par_id values
#    stored in this "ParameterMappingProperty" group.
#######################################################################

class ParameterMappingProperty(bpy.types.PropertyGroup):
    """An instance of this class exists for every general parameter"""
    par_id = StringProperty(default="", description="Unique ID for each parameter used as a key into the Python Dictionary") # name="Par_ID",


#######################################################################
#  The ParameterSystemPropertyGroup is the top-level group containing
#    CellBlender's parameter system. It contains both RNA properties
#    (defined here) and ID properties added as keys to its dictionary.
#    The use of ID properties is intended to improve performance over
#    the earlier versions that used all RNA properties.
#
#  The following ID Properties are added to this class at run time:
#
#    gp_dict - Dictionary containing the actual general parameter data
#    gp_ordered_list - A dependency-ordered list of parameter IDs
#
#  While the drawing functions appear to be drawing data from a selected
#    Blender CollectionProperty, they are actually drawing the same
#    static "active_.." StringProperty items from this class that are
#    being re-populated with data from the ID properties mentioned
#    above (mostly from the gp_dict ID property). This "re-populating"
#    happens whenever the active_par_index is changed via the update
#    callback function associated with the active_par_index. This helps
#    minimize the number of actual RNA properties (which appears to be
#    the primary performance bottleneck). When the selection changes,
#    the "last_selected_id" value is set so that changes to the "active"
#    properties can be stored in the appropriate slot in the ID property
#    dictionary ("gp_dict").
#
#  Note that previous versions of the parameter system defined a
#    separate "Expression_Handler" class which contained the various
#    expression parsing and evaluation functions. This separate class
#    was inherited by the ParameterSystemPropertyGroup using Python's
#    multiple inheritance. While this isolation might have been useful
#    if the "Expression_Handler" class found other uses, it was mostly
#    just confusing and served no real purpose. Those functions have
#    now all been included in the ParameterSystemPropertyGroup itself.
#######################################################################

class ParameterSystemPropertyGroup ( bpy.types.PropertyGroup ):
    """Root of CellBlender's Parameter Handling Capabilities"""
    # ID Property: gp_dict - Indexed by g# key. Holds the data for each parameter (name, expression, elist, units, description, dependencies)
    # ID Property: gp_ordered_list - List of g# keys in dependency order for evaluation.

    general_parameter_list = CollectionProperty(type=ParameterMappingProperty) # , name="Parameters List"
    panel_parameter_list = CollectionProperty(type=PanelParameterData) # , name="Panel Parameters List"
    next_gid = IntProperty(default=0) # name="Counter for Unique General Parameter IDs",
    next_pid = IntProperty(default=0) # name="Counter for Unique Panel Parameter IDs",
    active_par_index = IntProperty(default=0,                                                                 update=update_parameter_index) # name="Active Parameter",
    active_name  = StringProperty(default="Par", description="User name for this parameter (must be unique)", update=update_parameter_name)    # name="Parameter Name",
    active_elist = StringProperty(default="",    description="Pickled Expression list for this parameter",    update=update_parameter_elist)   # name="Expression List",
    active_expr  = StringProperty(default="0",   description="Expression to be evaluated for this parameter", update=update_parameter_expression) # name="Expression",
    active_units = StringProperty(default="",    description="Units for this parameter",                      update=update_parameter_units)  # name="Units",
    active_desc  = StringProperty(default="",    description="Description of this parameter",                 update=update_parameter_desc)   # name="Description",
    last_selected_id = StringProperty(default="")

    show_options_panel = BoolProperty(name="Show Options Panel", default=False)

    debug_level = IntProperty(name="Debug Level", default=0, description="Higher values print more detail")
    
    status = StringProperty ( name="status", default="" )

    show_all_details = BoolProperty(name="Show All Details", default=False)
    max_field_width = IntProperty(name="Max Field Width", default=20)
    num_pars_to_gen = IntProperty(name="Num Pars", default=5)
    num_pars_back = IntProperty(name="Num Back", default=2)

    param_display_mode_enum = [ ('one_line',  "One line per parameter", ""), ('two_line',  "Two lines per parameter", "") ]
    param_display_mode = bpy.props.EnumProperty ( items=param_display_mode_enum, default='one_line', name="Parameter Display Mode", description="Display layout for each parameter" )
    param_display_format = StringProperty ( default='%.6g', description="Formatting string for each parameter" )
    param_label_fraction = FloatProperty(precision=4, min=0.0, max=1.0, default=0.35, description="Width (0 to 1) of parameter's label")

    export_as_expressions = BoolProperty ( default=False, description="Export Parameters as Expressions rather than Numbers" )

    # This would be better as a double, but Blender would store as a float which doesn't have enough precision to resolve time in seconds from the epoch.
    last_parameter_update_time = StringProperty ( default="-1.0", description="Time that the last parameter was updated" )

    show_debugging = BoolProperty ( default=False, description="Show Debugging" )


    @profile('ParameterSystem.build_ordered_data_model_from_properties')
    def build_ordered_data_model_from_properties ( self, context ):
        # Normally, a Property Group would delegate the building of group items to those items.
        # But since the parameter system is so complex, it's all being done at the group level for now.
        dbprint ( "Parameter System building Data Model" )

        par_sys_dm = {}
        gen_par_list = []

        # Save the list in dependency order so they can be exported from the data model to MDL in dependency order
        gp_ordered_list = [ p for p in self['gp_ordered_list'] ]
        dbprint ( "gp_ordered_list = " + str ( gp_ordered_list ) )

        # It is possible that there are parameters NOT in the gp_ordered_list, but in the RNA parameters (those with circular references)
        # So build a list that contains the ordered parameters first, followed by any that were not in the ordered list
        gp_set_from_list = set ( gp_ordered_list )
        gp_set_from_rna = set ( [ self.general_parameter_list[k].par_id for k in self.general_parameter_list.keys() ] )
        remaining_unordered_set = gp_set_from_rna - gp_set_from_list
        dbprint ( str(remaining_unordered_set) + " = " + str(gp_set_from_rna) + " - " + str(gp_set_from_list) )
        for k in remaining_unordered_set:
            gp_ordered_list.append ( k )

        dbprint ( "Ordered GP keys = " + str ( gp_ordered_list ) )

        for pkey in gp_ordered_list:
            par_dict = {}
            par_dict['par_name']        = self['gp_dict'][pkey]['name']
            par_dict['par_expression']  = self['gp_dict'][pkey]['expr']
            par_dict['par_units']       = self['gp_dict'][pkey]['units']
            par_dict['par_description'] = self['gp_dict'][pkey]['desc']

            extras_dict = {}
            extras_dict['par_id_name'] = pkey
            extras_dict['par_value'] = 0.0
            if 'value' in self['gp_dict'][pkey]:
                extras_dict['par_value'] = self['gp_dict'][pkey]['value']
            extras_dict['par_valid'] = True

            par_dict['_extras'] = extras_dict

            dbprint ( "Dm for " + pkey + " = " + str(par_dict) )

            gen_par_list.append ( par_dict )

        par_sys_dm['model_parameters'] = gen_par_list
        return par_sys_dm


    @profile('ParameterSystem.build_data_model_from_properties')
    def build_data_model_from_properties ( self, context ):
        # Normally, a Property Group would delegate the building of group items to those items.
        # But since the parameter system is so complex, it's all being done at the group level for now.
        dbprint ( "Parameter System building Data Model" )

        par_sys_dm = {}
        gen_par_list = []

        gp_list_par_ids = [ self.general_parameter_list[k].par_id for k in self.general_parameter_list.keys() ]

        for pkey in gp_list_par_ids:
            par_dict = {}
            par_dict['par_name']        = self['gp_dict'][pkey]['name']
            par_dict['par_expression']  = self['gp_dict'][pkey]['expr']
            par_dict['par_units']       = self['gp_dict'][pkey]['units']
            par_dict['par_description'] = self['gp_dict'][pkey]['desc']

            extras_dict = {}
            extras_dict['par_id_name'] = pkey
            extras_dict['par_value'] = 0.0
            if 'value' in self['gp_dict'][pkey]:
                extras_dict['par_value'] = self['gp_dict'][pkey]['value']
            extras_dict['par_valid'] = True

            par_dict['_extras'] = extras_dict

            dbprint ( "Dm for " + pkey + " = " + str(par_dict) )

            gen_par_list.append ( par_dict )

        par_sys_dm['model_parameters'] = gen_par_list
        par_sys_dm['_extras'] = { 'ordered_id_names': [ p for p in self['gp_ordered_list'] ] }
        return par_sys_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        dbprint ( "------------------------->>> Upgrading ParameterSystemPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade ParameterSystemPropertyGroup data model to current version." )
            return None

        return dm


    @profile('ParameterSystem.build_properties_from_data_model')
    def build_properties_from_data_model ( self, context, par_sys_dm ):
        # Check that the data model version matches the version for this property group
        if par_sys_dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model to current version." )

        dbprint ( "Parameter System building Properties from Data Model ...", thresh=-1 )

        self.init_parameter_system()  # Do this in case it isn't already initialized

        self.next_gid = 0
        self.active_par_index = 0
        self.active_name = "Par"
        self.active_elist = ""
        self.active_expr = "0"
        self.active_units = ""
        self.active_desc = ""
        self.last_selected_id = ""
        self.general_parameter_list.clear()
        #self.panel_parameter_list.clear()
        self['gp_dict'] = {}
        self['gp_ordered_list'] = []

        if 'model_parameters' in par_sys_dm:
            # Add all of the parameters - some may be invalid if they depend on other parameters that haven't been read yet

            self.add_general_parameters_from_list ( context, par_sys_dm['model_parameters'] )

        dbprint ( "=== After parameter_system.ParameterSystemPropertyGroup.build_properties_from_data_model() ===" )
        #bpy.ops.mcell.print_gen_parameters()
        #bpy.ops.mcell.print_pan_parameters()
        #dbprint ( "==============================================================================================" )


    @profile('ParameterSystem.clear_all_parameters')
    def clear_all_parameters ( self, context ):
        """ Clear all Parameters """
        self.next_gid = 0
        # self.next_pid = 0  # Do not reset the PID because the panel parameters must be deleted by the property group that created them.
        #                    # Note that there are some panel parameters that should never be deleted (iterations, time_step, start_seed ...)
        #                    # There is a problem in resetting a simulation that requires the defaults to be re-established for the "static" panel parameters.
        self.active_par_index = 0
        self.active_name = "Par"
        self.active_elist = ""
        self.active_expr = "0"
        self.active_units = ""
        self.active_desc = ""
        self.last_selected_id = ""
        self.general_parameter_list.clear()
        #self.panel_parameter_list.clear()
        self['gp_dict'] = {}
        self['gp_ordered_list'] = []


    @profile('ParameterSystem.allocate_available_gid')
    def allocate_available_gid(self):
        if len(self.general_parameter_list) <= 0:
            self.next_gid = 0
        self.next_gid += 1
        return ( self.next_gid )

    # TODO: This allocation function does not re-use id numbers
    @profile('ParameterSystem.allocate_available_pid')
    def allocate_available_pid(self):
        self.next_pid += 1
        return ( self.next_pid )


    @profile('ParameterSystem.new_general_parameter')
    def new_general_parameter ( self, new_name=None, new_expr=None, new_units=None, new_desc=None, new_type='f' ):
        """ Add a new parameter to the list of parameters, and return its id name (g# or p#) """
        # Create and return a parameter dictionary entry
        # The new name is the user name ... not the id name

        dbprint ( "Called new_general_parameter ( " + str(new_name) + ", " + str(new_expr) + ", " + str(new_units) + ", " + str(new_desc) + " )" )

        new_par_id_dict = {
            'name': new_name,           # This is the user name
            'value' : 0.0,              # This is the initial value
            ##### Note that the expression is currently ignored!!!!!
            'expr': "0",
            'elist': pickle.dumps(['0'],protocol=0).decode('latin1'),
            'units': new_units,
            'desc': new_desc,
            'user_type' : new_type,
            'who_i_depend_on': {},      # This ID dictionary acts as a set
            'who_depends_on_me': {},    # This ID dictionary acts as a set
            'what_depends_on_me': {},   # This ID dictionary acts as a set
            'status': {}                # This ID dictionary acts as a set
            }
        return ( new_par_id_dict )


    @profile('ParameterSystem.draw_id_par_details')
    def draw_id_par_details ( self, id_par, drawable ):
        box = drawable.box()
        pref_order = ['name', 'expr', 'elist', 'who_i_depend_on', 'who_depends_on_me', 'what_depends_on_me', 'units', 'desc' ]
        pref_found = set()
        # Start by displaying known things in preferred order:
        for k in pref_order:
            if k in id_par:
                pref_found.add ( k )
                if k == 'elist':
                    elist = pickle.loads(id_par['elist'].encode('latin1'))
                    row = box.row()
                    row.label ( "  " + str(k) + " = " + str(elist) )
                    row = box.row()
                    row.label ( "  " + str(k) + " = " + str(id_par[k]) )
                elif k == 'who_i_depend_on':
                    row = box.row()
                    row.label ( "  Who I Depend On = " + str(id_par['who_i_depend_on'].keys()) )
                elif k == 'who_depends_on_me':
                    row = box.row()
                    row.label ( "  Who Depends On Me = " + str(id_par['who_depends_on_me'].keys()) )
                elif k == 'what_depends_on_me':
                    row = box.row()
                    row.label ( "  What Depends On Me = " + str(id_par['what_depends_on_me'].keys()) )
                else:
                    row = box.row()
                    row.label ( "  " + str(k) + " = " + str(id_par[k]) )
        # End by drawing unknown things in no particular order
        for k in id_par.keys():
            if not (k in pref_found):
                row = box.row()
                row.label ( "  " + str(k) + " = " + str(id_par[k]) )

    @profile('ParameterSystem.draw_rna_par_details')
    def draw_rna_par_details ( self, rna_par, drawable ):
        box = drawable.box()
        pref_order = ['name', 'expr', 'elist', 'who_i_depend_on', 'who_depends_on_me', 'what_depends_on_me', 'units', 'desc' ]
        pref_found = set()
        # Start by displaying known things in preferred order:
        for k in pref_order:
            if k in rna_par:
                pref_found.add ( k )
                if k == 'elist':
                    elist = pickle.loads(rna_par['elist'].encode('latin1'))
                    row = box.row()
                    row.label ( "  " + str(k) + " = " + str(elist) )
                    row = box.row()
                    row.label ( "  " + str(k) + " = " + str(rna_par[k]) )
                elif k == 'who_i_depend_on':
                    row = box.row()
                    row.label ( "  Who I Depend On = " + str(rna_par['who_i_depend_on'].keys()) )
                elif k == 'who_depends_on_me':
                    row = box.row()
                    row.label ( "  Who Depends On Me = " + str(rna_par['who_depends_on_me'].keys()) )
                elif k == 'what_depends_on_me':
                    row = box.row()
                    row.label ( "  What Depends On Me = " + str(rna_par['what_depends_on_me'].keys()) )
                else:
                    row = box.row()
                    row.label ( "  " + str(k) + " = " + str(rna_par[k]) )
        # End by drawing unknown things in no particular order
        for k in rna_par.keys():
            if not (k in pref_found):
                row = box.row()
                row.label ( "  " + str(k) + " = " + str(rna_par[k]) )

    @profile('ParameterSystem.init_parameter_system')
    def init_parameter_system( self ):
        if not 'gp_dict' in self:
            self['gp_dict'] = {}
        if not 'gp_ordered_list' in self:
            self['gp_ordered_list'] = []

    @profile('ParameterSystem.init_properties')
    def init_properties ( self ):
        self.init_parameter_system()

    @profile('ParameterSystem.remove_properties')
    def remove_properties ( self, context ):
        dbprint ( "Removing all Parameter System Properties ... (actually doing nothing right now)", thresh=-1 )
        #print ( "Before removing:" )
        #bpy.ops.mcell.print_gen_parameters()
        #bpy.ops.mcell.print_pan_parameters()
        # It's not clear if this should be done or not ... it wasn't done in the old version.
        self.clear_all_parameters ( context )
        #print ( "After removing:" )
        #bpy.ops.mcell.print_gen_parameters()
        #bpy.ops.mcell.print_pan_parameters()


    @profile('ParameterSystem.construct_unique_name')
    def construct_unique_name( self, new_name ):
        """ Construct a name that's not already in the list """
        dbprint ( "construct_unique_name called" )

        if new_name is None:
            new_name = 'Parameter'
        if new_name in self.general_parameter_list:
            # Deal with duplicate names
            base_name = (' ' + new_name).strip()  # This is just a mechanism to ensure a true copy
            next_copy_num = 2
            while base_name + '_' + str(next_copy_num) in self.general_parameter_list:
                next_copy_num += 1
            new_name = base_name + '_' + str(next_copy_num)
        return new_name



    @profile('ParameterSystem.add_general_parameter')
    def add_general_parameter ( self, name=None, expr="0", units="", desc="" ):
        """ Add a new parameter to the list of parameters and set as the active parameter """
        dbprint ( "add_general_parameter called" )

        self.init_parameter_system()  # Do this in case it isn't already initialized

        new_gid = self.allocate_available_gid()
        new_gid_key = 'g'+str(new_gid)
        
        new_name = self.construct_unique_name ( name )

        new_id_par = self.new_general_parameter ( new_name=new_name, new_expr=expr, new_units=units, new_desc=desc )

        dbprint ( "Adding " + str(new_id_par) )
        self['gp_dict'][new_gid_key] = new_id_par

        new_rna_par = self.general_parameter_list.add()
        new_rna_par.par_id = new_gid_key
        new_rna_par.name = new_name

        self.active_par_index = len(self.general_parameter_list)-1
        self.active_name = new_rna_par.name
        self.active_expr = new_id_par['expr']
        self.active_units = new_id_par['units']
        self.active_desc = new_id_par['desc']



    @profile('ParameterSystem.add_general_parameter_and_update')
    def add_general_parameter_and_update ( self, context, name=None, expr="0", units="", desc="" ):
        """ This function is currently only used by the test suite """
        self.add_general_parameter ( name, expr, units, desc )

        self.update_parameter_index ( context )
        self.update_parameter_name ( context )

        self.active_expr = expr

        self.update_parameter_expression ( context )
        self.update_parameter_elist ( context )
        self.update_parameter_units ( context )
        self.update_parameter_desc ( context )

        self.last_parameter_update_time = str(time.time())


    @profile('ParameterSystem.add_general_parameters_from_list')
    def add_general_parameters_from_list ( self, context, par_list ):

        self.init_parameter_system()  # Do this in case it isn't already initialized

        # Start by creating all of the parameters

        dbprint ( "Top of add_general_parameters_from_list" )

        for p in par_list:

            name = p['par_name']
            expr = p['par_expression']
            units = ""
            descr = ""
            if 'par_units' in p: units = p['par_units']
            if 'par_description' in p: descr = p['par_description']

            dbprint ( "Bulk Adding " + name + " = " + expr + " (" + units + ") ... " + descr )
            
            # Check to see if this name already exists in the name-to-id list

            gid = None
            if name is None:
                # Always add with a default name (although this shouldn't happen)
                gid = 'g'+str(self.allocate_available_gid())
                name = 'Parameter_'+str(gid)
            else:
                # Check to see if the name already exists
                if name in self.general_parameter_list:
                    gid = self.general_parameter_list[name].par_id
                else:
                    gid = 'g'+str(self.allocate_available_gid())

            # Create or overwrite this entry

            new_id_par = self.new_general_parameter ( new_name=name, new_expr=expr, new_units=units, new_desc=descr )
            new_id_par['expr'] = expr

            self['gp_dict'][gid] = new_id_par

            rna_par = None
            if name in self.general_parameter_list:
                rna_par = self.general_parameter_list[name]
                rna_par.par_id = gid
            else:
                rna_par = self.general_parameter_list.add()
                rna_par.par_id = gid
                rna_par.name = name

        dbprint ( "Step 2 of add_general_parameters_from_list" )

        # Determine the dependency order of the list
        if len(self['gp_dict']) > 0:
            gp_dict = self['gp_dict']
            for k in gp_dict.keys():
                par = gp_dict[k]

                parameterized_expr = self.parse_param_expr ( par['expr'] )
                dbprint ( "ParExp = " + str(parameterized_expr) )
                par['elist'] = pickle.dumps(parameterized_expr,protocol=0).decode('latin1')

        dbprint ( "Step 3 of add_general_parameters_from_list" )

        for k in self['gp_dict'].keys():
            self.update_expr_list_by_id ( context, k )

        dbprint ( "Step 4 of add_general_parameters_from_list" )

        # This one takes a long time:
        self.update_all_parameters ( context )  # This calls update_dependency_ordered_name_list

        dbprint ( "Step 5 of add_general_parameters_from_list" )

        self.active_par_index = len(self.general_parameter_list)-1

        self.last_parameter_update_time = str(time.time())


    """ This works, but is very slow:
    @profile('ParameterSystem.add_general_parameters_from_list')
    def add_general_parameters_from_list ( self, context, par_list ):

        self.init_parameter_system()  # Do this in case it isn't already initialized

        for p in par_list:

            name = p['par_name']
            expr = p['par_expression']
            units = ""
            descr = ""
            if 'par_units' in p: units = p['par_units']
            if 'par_description' in p: descr = p['par_description']
            self.add_general_parameter_and_update ( context, name=name, expr=expr, units=units, desc=descr )

        self.last_parameter_update_time = str(time.time())
    """



    @profile('ParameterSystem.remove_active_parameter')
    def remove_active_parameter ( self, context ):
        """ Remove the active parameter from the list of parameters if not needed by others """
        status = ""
        if len(self.general_parameter_list) > 0:
            par_map_item = self.general_parameter_list[self.active_par_index]
            pid = par_map_item.par_id
            if pid in self['gp_dict']:
                who_depends_on_me =  [ k for k in self['gp_dict'][pid]['who_depends_on_me']  ]
                what_depends_on_me = [ k for k in self['gp_dict'][pid]['what_depends_on_me'] ]
                #print ( "Who  depends on me: " + str(who_depends_on_me) )
                #print ( "What depends on me: " + str(what_depends_on_me) )

                for wdom in who_depends_on_me:
                    status += " " + self['gp_dict'][wdom]['name']

                for wdom in what_depends_on_me:
                    # The following test checks to see that any dependencies still exist
                    #  before adding the dependency to the error list preventing deletion
                    # However, this still does not work because some items (like Mol Placement)
                    #  don't actively delete their own parameters when they are removed.
                    if wdom in self.panel_parameter_list:
                        status += " " + self.panel_parameter_list[wdom]['user_name']

                status = status.strip()

                if len(status) > 0:
                    # Don't delete
                     status = "Parameter " + self['gp_dict'][pid]['name'] + " is used by: " + status
                else:
                    # OK to delete

                    # Remove this parameter from the who_depends_on_me of every parameter in the who_i_depend_on dictionary

                    wido_list = [ k for k in self['gp_dict'][pid]['who_i_depend_on'] ]
                    for wido in wido_list:
                        self['gp_dict'][wido]['who_depends_on_me'].pop(pid)

                    # Remove this parameter itself

                    self['gp_dict'].pop(par_map_item.par_id)
                    self['gp_ordered_list'] = [ i for i in self['gp_ordered_list'] if i != par_map_item.par_id ]  # This is one way to remove an item in a read only list

                    self.general_parameter_list.remove ( self.active_par_index )
                    self.active_par_index += -1
                    if self.active_par_index < 0:
                        self.active_par_index = 0

        return ( status )


    @profile('ParameterSystem.update_parameter_index')
    def update_parameter_index ( self, context, interactive=False ):
        """ Swap the ID property versions of this parameter into the active RNA properties to be displayed and possibly edited. """
        # The "self" passed in is a ParameterSystemPropertyGroup object.
        dbprint ( "Type of self = " + str ( type(self) ), thresh=50 )

        par_num = self.active_par_index  # self.active_par_index is what gets changed when the user selects an item
        dbprint ( "update_parameter_index callback: par_num = " + str(par_num) )
        if (par_num >= 0) and (len(self.general_parameter_list) > 0):
            par_id = self.general_parameter_list[par_num].par_id
            self.last_selected_id = "" + par_id
            self.active_name  = self['gp_dict'][par_id]['name']
            self.active_elist = str( self['gp_dict'][par_id]['elist'] )
            self.active_expr  = self['gp_dict'][par_id]['expr']
            self.active_units = self['gp_dict'][par_id]['units']
            self.active_desc  = self['gp_dict'][par_id]['desc']
            dbprint ( "Active parameter index changed to " + str(par_num) )


    @profile('ParameterSystem.update_parameter_name')
    def update_parameter_name (self, context, interactive=False):
        if ('gp_dict' in self):   ## and (len(self['gp_dict']) > 0):
            pid = self.last_selected_id
            old_name = "\1\2\3\4\5\6\7" # This should be a string that cannot be legally entered as a parameter name
            try:
                old_name = str(self['gp_dict'][pid]['name'])  # Note that sometimes the old name cannot be found
            except:
                print ( "Unexpected error: Cannot find name for self['gp_dict'][" + str(pid) + "]['name']" )
                # Halt here for interaction
                # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
            new_name = self.active_name
            if new_name != old_name:
                # The name actually changed, so really perform the update

                # First make the name unique in case it's already there
                # TODO: This function is a temporary way to ensure unique names.
                new_name = self.construct_unique_name( new_name )
                dbprint ("Parameter name changed from " + old_name + " to " + new_name )

                if pid in self['gp_dict']:

                    # Update this name
                    dbprint ("Update gp_dict from " + old_name + " to " + new_name )
                    self['gp_dict'][pid]['name'] = new_name
                    dbprint ("Update general_parameter_list from " + old_name + " to " + new_name )
                    if old_name in self.general_parameter_list:
                        self.general_parameter_list[old_name].name = new_name
                    dbprint ("Propagate changes from " + old_name + " to " + new_name )

                    who_depends_on_me =  [ k for k in self['gp_dict'][pid]['who_depends_on_me']  ]
                    what_depends_on_me = [ k for k in self['gp_dict'][pid]['what_depends_on_me'] ]
                    ppl = self.panel_parameter_list
                    
                    dbprint ( "who_depends_on_me = " + str(who_depends_on_me) )
                    dbprint ( "what_depends_on_me = " + str(what_depends_on_me) )

                    # Update all other general parameter expressions that depend on this name
                    for dep_key in who_depends_on_me:
                        dep_par = self['gp_dict'][dep_key]
                        elist = pickle.loads(dep_par['elist'].encode('latin1'))
                        dep_par['expr'] = self.build_expression ( elist )

                    # Update all panel parameter expressions that depend on this name (this also forces a redraw)
                    for dep_key in what_depends_on_me:
                        elist = pickle.loads(ppl[dep_key]['elist'].encode('latin1'))
                        ppl[dep_key]['expr'] = self.build_expression ( elist )


                    # Save the current index so it can be changed to update other parameters
                    saved_index = self.active_par_index

                    # Force a redraw of all general parameters that depend on this one by selecting each one
                    for dep_key in who_depends_on_me:
                        dep_name = self['gp_dict'][dep_key]['name']
                        dbprint ( "  Setting index to: " + dep_name )
                        self.active_par_index = self.general_parameter_list.find(dep_name)

                    """ # This is being done earlier ... delete this if that works.
                    # Force a redraw of all panel parameters that depend on this one
                    dbprint ( "Updating name: " + old_name + " -> " + new_name + ", these depend on me: " + str(what_depends_on_me) )
                    for p in what_depends_on_me:
                        elist = pickle.loads(ppl[p]['elist'].encode('latin1'))
                        ppl[p]['expr'] = self.build_expression ( elist )
                    """

                    # Force a redraw of all general parameters that might depend on this newly changed name (those with a "None" in thier list)
                    #for p in self['gp_dict'].keys():
                    #    elist = pickle.loads(self['gp_dict'][p]['elist'].encode('latin1'))
                    #    if None in elist:
                    #        dep_name = self['gp_dict'][p]['name']
                    #        dbprint ( "  Setting index to: " + dep_name )
                    #        self.active_par_index = self.general_parameter_list.find(dep_name)

                    # Restore the current index
                    self.active_par_index = saved_index
                    # TODO Need to deal with errors in panel parameters

                else:
                    print ( "Unexpected error: pid \"" + str(pid) + "\" not in self['gp_dict']" )

    @profile('ParameterSystem.update_all_parameters')
    def update_all_parameters (self, context, interactive=False):
        if ('gp_dict' in self):   ## and (len(self['gp_dict']) > 0):

            # Now set all status based on the expression lists:
            for par in self['gp_dict'].keys():
                self['gp_dict'][par]['status'] = {} # Intended to be a set(), but sets are not stored as ID properties. So use a dictionary.
                elist = pickle.loads(self['gp_dict'][par]['elist'].encode('latin1'))
                if None in elist:
                    # self['gp_dict'][par]['status'].add ( 'undef' ) # This would be the set operation, but we're using a dictionary
                    self['gp_dict'][par]['status']['undef'] = True   # Use "True" to flag the intention of 'undef' being in the set

            # Next add status based on loops:
            result = self.update_dependency_ordered_name_list()

            if len(result) > 0:
                # There was a loop and result contains the names of unresolvable parameters
                for par in self['gp_dict'].keys():
                    if par in result:
                        # self['gp_dict'][par]['status'].add ( 'loop' ) # This would be the set operation, but we're using a dictionary
                        self['gp_dict'][par]['status']['loop'] = True   # Use "True" to flag the intention of 'loop' being in the set
            else:
                # TODO: Note that this might not be the most efficient thing to do!!!!
                self.evaluate_all_gp_expressions ( context )
                self.evaluate_all_pp_expressions ( context )


    @profile('ParameterSystem.update_parameter_expression')
    def update_parameter_expression (self, context, interactive=False):
        if len(self.active_expr.strip()) <= 0:
            self.active_expr = "0"
            return
        if ('gp_dict' in self):   ## and (len(self['gp_dict']) > 0):
            needs_update = False
            try:
                needs_update = (str(self['gp_dict'][self.last_selected_id]['expr']) != self.active_expr)
            except:
                needs_update = True
            if needs_update:
                # The expression string actually changed, so really perform the update
                # dbprint ("Parameter string changed from " + str(self['gp_dict'][self.last_selected_id]['expr']) + " to " + self.active_expr )
                if self.last_selected_id in self['gp_dict']:
                    self['gp_dict'][self.last_selected_id]['expr'] = self.active_expr
                    self.evaluate_active_expression(context)
                else:
                    print ( "Unexpected error: last_selected_id \"" + str(self.last_selected_id) + "\" not in self['gp_dict']" )

                self.update_all_parameters ( context, interactive )


    @profile('ParameterSystem.update_parameter_elist')
    def update_parameter_elist (self, context, interactive=False):
        if ('gp_dict' in self):   ## and (len(self['gp_dict']) > 0):
            needs_update = False
            try:
                needs_update = (str(self['gp_dict'][self.last_selected_id]['elist']) != self.active_elist)
            except:
                needs_update = True
            if needs_update:
                # The expression list actually changed, so really perform the update
                # dbprint ("Parameter elist changed from " + str(self['gp_dict'][self.last_selected_id]['elist']) + " to " + self.active_elist )
                if self.last_selected_id in self['gp_dict']:
                    # self['gp_dict'][self.last_selected_id]['elist'] = eval(self.active_elist)
                    elist = pickle.loads(self['gp_dict'][self.last_selected_id]['elist'].encode('latin1'))
                    if not None in elist:
                        self.active_expr = str ( self.build_expression ( elist ) )
                        # self.evaluate_active_expression(context)
                else:
                    print ( "Unexpected error: \"" + str(self.last_selected_id) + "\" not in self['gp_dict']" )

    @profile('ParameterSystem.update_parameter_units')
    def update_parameter_units (self, context, interactive=False):
        if ('gp_dict' in self):   ## and (len(self['gp_dict']) > 0):
            needs_update = False
            try:
                needs_update = (str(self['gp_dict'][self.last_selected_id]['units']) != self.active_units)
            except:
                needs_update = True
            if needs_update:
                # The units actually changed, so really perform the update
                # dbprint ("Parameter units changed from " + str(self['gp_dict'][self.last_selected_id]['units']) + " to " + self.active_units )
                if self.last_selected_id in self['gp_dict']:
                    self['gp_dict'][self.last_selected_id]['units'] = self.active_units
                else:
                    print ( "Unexpected error: \"" + str(self.last_selected_id) + "\" not in self['gp_dict']" )

    @profile('ParameterSystem.update_parameter_desc')
    def update_parameter_desc (self, context, interactive=False):
        if ('gp_dict' in self) and (len(self['gp_dict']) > 0):
            needs_update = False
            try:
                needs_update = (str(self['gp_dict'][self.last_selected_id]['desc']) != self.active_desc)
            except:
                needs_update = True
            if needs_update:
                # The description actually changed, so really perform the update
                # dbprint ("Parameter description changed from " + str(self['gp_dict'][self.last_selected_id]['desc']) + " to " + self.active_desc )
                if self.last_selected_id in self['gp_dict']:
                    self['gp_dict'][self.last_selected_id]['desc'] = self.active_desc
                else:
                    print ( "Unexpected error: \"" + str(self.last_selected_id) + "\" not in self['gp_dict']" )



    @profile('ParameterSystem.draw')
    def draw(self, context, layout):
        if len(self.general_parameter_list) > 0:
            layout.prop(self, "active_name", text='Name')
            layout.prop(self, "active_expr", text='Expression')
            # layout.prop(self, "active_elist")
            layout.prop(self, "active_units", text='Units')
            layout.prop(self, "active_desc", text='Description')


    @profile('ParameterSystem.update_expr_list_by_id')
    def update_expr_list_by_id ( self, context, gid ):
        if len(self['gp_dict']) > 0:
            gp_dict = self['gp_dict']
            par = gp_dict[gid]

            #id_par = self['gp_dict'][gid]
            #parameterized_expr = self.parse_param_expr ( id_par['expr'] )
            
            parameterized_expr = self.parse_param_expr ( par['expr'] )
            dbprint ( "ParExp = " + str(parameterized_expr) )
            par['elist'] = pickle.dumps(parameterized_expr,protocol=0).decode('latin1')

            explst = parameterized_expr
            dbprint ( "Top: ExprList = " + str ( explst ) )
            """
            if (type(explst) == type(1)) or (type(explst) == type(1.0)):
                # Force it to be a list for now to suppress errors when constants are entered
                explst = [ str(explst) ]
            if type(explst) != type([]):
                # Force it to be a list for now to suppress errors when constants are entered
                explst = [ explst ]
            """
            dbprint ( "Eval exprlist: " + str(explst) )
            if None in explst:
                dbprint ( "Expression Error: Contains None during update_expr_list_by_id" )
            else:
                expr = ""

                old_who_i_depend_on = set([ w for w in par['who_i_depend_on'] ])
                new_who_i_depend_on = set()

                par['who_i_depend_on'] = {}

                for term in explst:
                    if type(term) == int:
                        # This is a parameter
                        #par['who_i_depend_on'].add ( "g" + str(term) )

                        new_who_i_depend_on.add ( "g" + str(term) )
                        par['who_i_depend_on']["g"+str(term)] = True
                        #self['gp_dict']["g"+str(term)]['who_depends_on_me'][gid] = True
                        
                        gp_dict["g"+str(term)]['who_depends_on_me'][gid] = True
                        expr += " " + gp_dict["g"+str(term)]['name']
                    elif type(term) == type('a'):
                        # This is an operator or constant
                        expr += " " + term
                    else:
                        dbprint ( "Error" )
                    dbprint ( "Expr: " + par['name'] + " = " + expr )

                remove_me_from = old_who_i_depend_on - new_who_i_depend_on
                add_me_to = new_who_i_depend_on - old_who_i_depend_on
                if len(remove_me_from) > 0:
                    dbprint ( "Remove " + par['name'] + " from who_depends_on_me list for: " + str(remove_me_from) )
                if len(add_me_to) > 0:
                    dbprint ( "Add " + par['name'] + " to who_depends_on_me list for: " + str(add_me_to) )
                for k in remove_me_from:
                    dbprint ( "  Removing ( " + str(gid) + " ) from " + str(k) )
                    self['gp_dict'][k]['who_depends_on_me'].pop ( gid )
                for k in add_me_to:
                    self['gp_dict'][k]['who_depends_on_me'][gid] = True

            if self.debug_level >= 0:
                dbprint ( "ExprList = " + str ( explst ) )
                dbprint ( "MDL Expr = " + str ( self.build_expression ( explst ) ) )
                dbprint ( "Py  Expr = " + str ( self.build_expression ( explst, as_python=True ) ) )


    @profile('ParameterSystem.evaluate_active_expression')
    def evaluate_active_expression ( self, context ):
        if len(self['gp_dict']) > 0:
            self.update_expr_list_by_id ( context, self.last_selected_id )


    @profile('ParameterSystem.evaluate_all_gp_expressions')
    def evaluate_all_gp_expressions ( self, context ):
        if ('gp_dict' in self) and (len(self['gp_dict']) > 0):
            gp_dict = self['gp_dict']
            if 'gp_ordered_list' in self:
                dbprint ( "self['gp_ordered_list'] = " + str(self['gp_ordered_list']), thresh=1 )
                gl = {}  # This is the dictionary to contain the globals and locals of the evaluated python expressions
                for par_id in self['gp_ordered_list']:
                    par = gp_dict[par_id]
                    elist = pickle.loads(par['elist'].encode('latin1'))

                    dbprint ( "Eval exprlist: " + str(elist) )
                    if None in elist:
                        dbprint ( "Expression Error: Contains None during evaluate_all_gp_expressions" )
                    else:
                        expr = ""
                        for term in elist:
                            if type(term) == int:
                                # This is a parameter
                                expr += " " + gp_dict["g"+str(term)]['name']
                            elif type(term) == type('a'):
                                # This is an operator or constant
                                expr += " " + term
                            else:
                                dbprint ( "Error" )
                            dbprint ( "Expr: " + par['name'] + " = " + expr )
                        py_expr = self.build_expression ( elist, as_python=True )
                        # Assign the value to the parameter item
                        par['value'] = float(eval(py_expr,globals(),gl))
                        # Make the assignment in the dictionary used as "globals" and "locals" for any parameters that depend on it
                        gl[par['name']] = par['value']


    @profile('ParameterSystem.evaluate_all_pp_expressions')
    def evaluate_all_pp_expressions ( self, context ):
        dbprint ( "Evaluate all pp expressions" )
        ppl = self.panel_parameter_list
        gl = {}
        valid = self.build_eval_dict ( gl )
        for k in ppl.keys():
            # This causes a re-evaluation of all general parameters for each panel parameter which is very inefficient
            # ppl[k].expr = ppl[k].expr
            ppl[k].update_panel_expression(context, gl)


    @profile('ParameterSystem.build_eval_dict')
    def build_eval_dict ( self, gl ):
        """ Build a dictionary of { par_name:par_val } for all valid expressions """
        # Simply omit any names that are not valid. This will trigger an evaluation error later.
        if gl is None:
            gl = {}  # This is the dictionary to contain the globals and locals of the evaluated python expressions

        valid = True
        if True or ('gp_dict' in self): ## and (len(self['gp_dict']) > 0):
            gp_dict = self['gp_dict']
            if True or ('gp_ordered_list' in self):
                dbprint ( "parameter_system['gp_ordered_list'] = " + str(self['gp_ordered_list']), thresh=1 )
                for par_id in self['gp_ordered_list']:
                    par = gp_dict[par_id]
                    elist = pickle.loads(par['elist'].encode('latin1'))

                    dbprint ( "Eval exprlist: " + str(elist) )
                    if None in elist:
                        print ( "Expression Error: Contains None during build_eval_dict" )
                        if 'value' in par:
                            par.pop('value')
                    else:
                        if self.debug_level >= 0:
                            # Build an expression and print as it is built
                            expr = ""
                            for term in elist:
                                if type(term) == int:
                                    # This is a parameter
                                    expr += " " + gp_dict["g"+str(term)]['name']
                                elif type(term) == type('a'):
                                    # This is an operator or constant
                                    expr += " " + term
                                else:
                                    dbprint ( "Unexpected Type Error in " + str(elist) )
                                    if 'value' in par:
                                        par.pop('value')
                                    valid = False
                                dbprint ( "Expr: " + par['name'] + " = " + expr )
                        py_expr = self.build_expression ( elist, as_python=True )
                        if py_expr is None:
                            print ( "Error: " + str(elist) + " cannot be evaluated" )
                            if 'value' in par:
                                par.pop('value')
                            valid = False
                        else:
                            # Assign the value to the parameter item
                            par['value'] = float(eval(py_expr,globals(),gl))
                    if 'value' in par:
                        # Make the assignment in the dictionary used as "globals" and "locals" for any parameters that depend on it
                        gl[par['name']] = par['value']
        return valid



    @profile('ParameterSystem.update_dependency_ordered_name_list')
    def update_dependency_ordered_name_list ( self ):
        """ Update the dependency order list. Return a list or set containing items in a loop. """
        dbprint ( "Updating Dependency Ordered Name List", thresh=5 )
        
        ol = []
        if len(self['gp_dict']) > 0:
            # Assign some convenience variables
            
            gp_dict = self['gp_dict']
            gp_ordered_list = self['gp_ordered_list']
            glkeys = gp_dict.keys()
            # Ensure that the starting ordered name list contains exactly all the names from the dictionary
            items_not_in_global_dict = set(gp_ordered_list) - set(glkeys)
            if len(items_not_in_global_dict) > 0:
                # There are some items in the ordered list that are no longer in the parameter system. Remove them.
                for k in items_not_in_global_dict:
                    #gp_ordered_list.remove(k)
                    gp_ordered_list = [ i for i in gp_ordered_list if i != k ]  # This is one way to remove an item in a read only list

            items_not_in_ordered_list = set(glkeys) - set(self['gp_ordered_list'])
            if len(items_not_in_ordered_list) > 0:
                # There are some items in the global list that are not yet in the ordered list. Add them.
                for k in items_not_in_ordered_list:
                    #gp_ordered_list.append(k)
                    gp_ordered_list = [ i for i in gp_ordered_list ] + [ k ]  # This is one way to add an item to a read only list

            assert len(gp_ordered_list) == len(gp_dict)

            # Continually loop through all parameters until they're either all in order or a loop is detected
            double_check_count = 0
            gl = self['gp_dict']
            gs = gp_ordered_list
            dbprint ( " general parameter ordered list before update (gs) = " + str(gs), thresh=5 )
            while len(gs) > 0:
                defined_set = set(ol)
                dbprint ( "  In while with already defined_set = " + str(defined_set), thresh=5 )
                added = set()
                for n in gs:
                    dbprint ( gl[n]['name'] + " is " + n + ", depends on (" + str(gl[n]['who_i_depend_on'].keys()) + "), and depended on by (" + str(gl[n]['who_depends_on_me'].keys()) + ")", thresh=5 )
                    dbprint ( "   Checking for " + gl[n]['name'] + " in the defined set", thresh=5 )
                    if not (n in defined_set):
                        dbprint ( "     " + gl[n]['name'] + " is not defined yet, check if it can be", thresh=5 )
                        dep_set = set(gl[n]['who_i_depend_on'])
                        if dep_set.issubset(defined_set):
                            dbprint ( "       " + gl[n]['name'] + " is now defined since all its dependencies are defined.", thresh=5 )
                            ol.append ( n );
                            added.add ( n );
                            defined_set.add ( n )
                        else:
                            dbprint ( "     " + gl[n]['name'] + " cannot be defined yet", thresh=5 )
                if len(added) > 0:
                    # Remove all that are in od from gs to speed up subsequent searching
                    for r in added:
                        gs.remove ( r )
                else:
                    # Getting here indicates a loop, but continue anyway to remove those that aren't in the loop for flagging
                    double_check_count += 1
                    if double_check_count > len(gp_dict):
                        dbprint ( "Cannot Order Name List: " + str(gs), thresh=1 )
                        self['gp_ordered_list'] = ol
                        # self['loop_status'] = "Circular Dependency Detected"
                        return (gs)
        dbprint ( "Final dependency ordered name list = " + str(ol), thresh=3 )
        self['gp_ordered_list'] = ol
        # self['loop_status'] = ""
        return ([])

    @profile('ParameterSystem.draw_label_with_help')
    def draw_label_with_help ( self, layout, label, prop_group, show, show_help, help_string ):
        """ This function helps draw non-parameter properties with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=label )
        col = split.column()
        col.label ( text="" )
        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
            row = layout.row()
            # Use a split with two columns to indent the box
            split = row.split(0.03)
            col = split.column()
            col = split.column()
            box = col.box()
            desc_list = help_string.split("\n")
            for desc_line in desc_list:
                box.label (text=desc_line)


    @profile('ParameterSystem.draw_prop_with_help')
    def draw_prop_with_help ( self, layout, prop_label, prop_group, prop, show, show_help, help_string ):
        """ This function helps draw non-parameter properties with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=prop_label )
        col = split.column()
        col.prop ( prop_group, prop, text="" )
        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
            row = layout.row()
            # Use a split with two columns to indent the box
            split = row.split(0.03)
            col = split.column()
            col = split.column()
            box = col.box()
            desc_list = help_string.split("\n")
            for desc_line in desc_list:
                box.label (text=desc_line)


    @profile('ParameterSystem.draw_operator_with_help')
    def draw_operator_with_help ( self, layout, op_label, prop_group, op, show, show_help, help_string ):
        """ This function helps draw operators with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=op_label )
        col = split.column()
        col.operator ( op )
        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
            row = layout.row()
            # Use a split with two columns to indent the box
            split = row.split(0.03)
            col = split.column()
            col = split.column()
            box = col.box()
            desc_list = help_string.split("\n")
            for desc_line in desc_list:
                box.label (text=desc_line)



    @profile('ParameterSystem.draw_prop_search_with_help')
    def draw_prop_search_with_help ( self, layout, prop_label, prop_group, prop, prop_parent, prop_list_name, show, show_help, help_string, icon='FORCE_LENNARDJONES' ):
        """ This function helps draw non-parameter properties with help (info) button functionality """
        row = layout.row()
        split = row.split(self.param_label_fraction)
        col = split.column()
        col.label ( text=prop_label )
        col = split.column()

        col.prop_search( prop_group, prop, prop_parent, prop_list_name, text="", icon=icon)

        col = row.column()
        col.prop ( prop_group, show, icon='INFO', text="" )
        if show_help:
            row = layout.row()
            # Use a split with two columns to indent the box
            split = row.split(0.03)
            col = split.column()
            col = split.column()
            box = col.box()
            desc_list = help_string.split("\n")
            for desc_line in desc_list:
                box.label (text=desc_line)

    def draw_debug_items ( self, context, layout ):
        row = layout.row()
        col = row.column()
        col.operator ( "mcell.add_par_list" )
        col = row.column()
        col.prop ( self, "num_pars_to_gen" )
        col = row.column()
        col.prop ( self, "num_pars_back" )
        col = row.column()
        col.operator ( "mcell.delete_all_pars" )

        row = layout.row()
        col = row.column()
        col.operator ( "mcell.print_gen_parameters" )
        col = row.column()
        col.operator ( "mcell.print_pan_parameters" )
        col = row.column()
        col.prop ( self, "max_field_width" )

        row = layout.row()
        row.operator("mcell.print_profiling", text="Print Profiling")
        row.operator("mcell.clear_profiling", text="Clear Profiling")
        row.prop ( self, "debug_level" )

    @profile('ParameterSystem.draw_layout')
    def draw_layout ( self, context, layout ):

        if context.scene.mcell.cellblender_preferences.debug_level > 0:
            ### This is here for help during debugging when errors might keep the rest of the panel from being drawn
            self.draw_debug_items ( context, layout )

        errors = set()
        if 'gp_dict' in self:
            gpd = self['gp_dict']
            for p in gpd:
                par = gpd[p]
                if ('status' in par) and (len(par['status']) > 0):
                    if 'loop' in par['status']:
                        errors.add ( 'loop' )
                    if 'undef' in par['status']:
                        errors.add ( 'undef' )

        for err in errors:
            if 'loop' in err:
                row = layout.row()
                row.label ( "Parameter Error: Circular References Detected", icon='ERROR' )
            if 'undef' in err:
                row = layout.row()
                row.label ( "Parameter Error: Undefined Values Detected", icon='ERROR' )


        row = layout.row()
        col = row.column()
        col.template_list("MCELL_UL_draw_parameter", "",
                          self, "general_parameter_list",
                          self, "active_par_index", rows=7)
        col = row.column(align=True)
        col.operator("mcell.add_parameter", icon='ZOOMIN', text="")
        col.operator("mcell.remove_parameter", icon='ZOOMOUT', text="")

        col.separator()
        col.operator("mcell.delete_all_pars", icon='X_VEC', text="")


        if len(self.general_parameter_list) > 0:
            par_map_item = self.general_parameter_list[self.active_par_index]
            par_name = par_map_item.name
            par_id = par_map_item.par_id
            layout.prop(self, "active_name", text='Name')
            layout.prop(self, "active_expr", text='Expression')
            layout.prop(self, "active_units", text='Units')
            layout.prop(self, "active_desc", text='Description')

            elist = pickle.loads(self.active_elist.encode('latin1'))
            
            pstatus = set()
            if None in elist:
                # A None indicates a missing parameter and is the highest priority error
                pstatus.add ( 'undef' )
            if 'status' in self['gp_dict'][par_id]:
                pstatus = pstatus.union(self['gp_dict'][par_id]['status'])
            if len(pstatus) > 0:
                # Add label lines for errors:
                if 'undef' in pstatus:
                    undefs = ""
                    # elist = self['gp_dict'][par_id]['elist']
                    for i in range(len(elist)-1):
                        if elist[i] == None:
                            undefs += " " + str(elist[i+1])
                    layout.label ( "  Undefined Value(s) [" + undefs + " ] in Expression:   " + par_name + " = " + str(self['gp_dict'][par_id]['expr']), icon='ERROR' )
                if 'loop' in pstatus:
                    layout.label ( "  Circular Reference:   " + par_name + " = " + str(self['gp_dict'][par_id]['expr']), icon='LOOP_BACK' )
                if not (('undef' in pstatus) or ('loop' in pstatus)):
                    layout.label ( "  Unknown Error:   " + par_name + " = " + str(self['gp_dict'][par_id]['expr']) + " = ?", icon='ERROR' )


            # TODO
            """
            if str(self.param_display_mode) != "none":
                par = self.general_parameter_list[self.active_par_index]

                row = layout.row()
                if par.name_status == "":
                    layout.prop(par, "par_name")
                else:
                    #layout.prop(par, "par_name", icon='ERROR')
                    layout.prop(par, "par_name")
                    row = layout.row()
                    row.label(text=str(par.name_status), icon='ERROR')
                if len(par.pending_expr) > 0:
                    layout.prop(par, "expr")
                    row = layout.row()
                    row.label(text="Undefined Expression: " + str(par.pending_expr), icon='ERROR')
                elif not par.isvalid:
                    layout.prop(par, "expr", icon='ERROR')
                    row = layout.row()
                    row.label(text="Invalid Expression: " + str(par.pending_expr), icon='ERROR')
                elif par.inloop:
                    layout.prop(par, "expr", icon='ERROR')
                    row = layout.row()
                    row.label(text="Circular Reference", icon='ERROR')
                else:
                    layout.prop(par, "expr")
                layout.prop(par, "units")
                layout.prop(par, "descr")
            """


        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not self.show_options_panel:
            row.prop(self, "show_options_panel", text="Parameter Options", icon='TRIA_RIGHT', emboss=False)
        else:
            col = row.column()
            col.alignment = 'LEFT'
            col.prop(self, "show_options_panel", text="Parameter Options", icon='TRIA_DOWN', emboss=False)
            col = row.column()
            col.prop(self, "show_all_details", text="Show Internal Details for All")

            if self.show_all_details:
                row = layout.row()
                col = row.column()
                #detail_box = None
                if len(self.general_parameter_list) > 0:
                    par = self.general_parameter_list[self.active_par_index]
                    par_map_item = self.general_parameter_list[self.active_par_index]
                    par_name = par_map_item.name
                    par_id = par_map_item.par_id

                    box.prop(self, "last_selected_id")
                    box.prop(par_map_item, "par_id")

                    detail_box = box.box()
                    #par.draw_details(detail_box)

                    elist = pickle.loads(self['gp_dict'][par_id]['elist'].encode('latin1'))
                    if None in elist:
                        detail_box.label ( "Parameter \'" + par_name + "\' is {" + par_id + "} = " + str(elist) + " = ?" )
                    else:
                        detail_box.label ( "Parameter \'" + par_name + "\' is {" + par_id + "} = " + str(elist) + " = " + self.build_expression ( elist ) )
                    if 'status' in self['gp_dict'][par_id]:
                        if len(self['gp_dict'][par_id]['status']) > 0:
                            detail_box.label ( "  Status = " + str(self['gp_dict'][par_id]['status']) )
                    detail_box.label ( "Who I Depend On ID = " + str(self['gp_dict'][par_id]['who_i_depend_on'].keys()) )
                    detail_box.label ( "Who Depends On Me ID = " + str(self['gp_dict'][par_id]['who_depends_on_me'].keys()) )
                    detail_box.label ( "What Depends On Me ID = " + str(self['gp_dict'][par_id]['what_depends_on_me'].keys()) )

                    self.draw_id_par_details ( self['gp_dict'][par_id], detail_box )

                    #detail_box.label ( "elist pickle = " + str(self.active_elist) )
                    #detail_box.label ( "elist = " + str(elist) )


                    row = detail_box.row()
                else:
                    detail_box = box.box()
                    detail_box.label(text="No General Parameters Defined")
                    row = detail_box.row()

            row = box.row()
            row.prop(self, "param_display_mode", text="Parameter Display Mode")
            row = box.row()
            row.prop(self, "param_display_format", text="Parameter Display Format")
            row = box.row()
            row.prop(self, "param_label_fraction", text="Parameter Label Fraction")

            row = box.row()
            row.prop(self, "export_as_expressions", text="Export Parameters as Expressions (experimental)")


            if not self.show_debugging:
                row = box.row()
                row.prop(self, "show_debugging", text="Show Debugging", icon='TRIA_RIGHT', emboss=False)
            else:
                row = box.row()
                row.prop(self, "show_debugging", text="Show Debugging", icon='TRIA_DOWN', emboss=False)
                self.draw_debug_items ( context, box )


    @profile('ParameterSystem.draw_panel')
    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


    @profile('ParameterSystem.shorten_string')
    def shorten_string ( self, s, fw ):
        if (fw<=0):
            return s[:]
        else:
            return s[0:fw]


    """
    Expression Handler Code:
      Expressions are encoded into lists containing strings and integers.
      The string items in the lists are verbatim representations of parts
      of the expression that do not represent variable parameters. The
      integer items in the list are the ID numbers of variable parameters
      known as "general parameters" in this code. The value of "None" is
      used to prefix general parameters that are currently undefined
      within the parameter system.

      Example:
        Parameter 'a' has an ID of 1
        Parameter 'b' has an ID of 2
        Parameter 'c' is undefined
        Original Expression:  a + 5 + b + c
        Expression as a List: [1, '+', '5', '+', 2, '+', None, 'c' ]
        Alternate Expression as a List: [1, '+ 5 +', 2, '+', None, 'c' ]
          Note that these ID numbers always reference General Parameters so the IDs
          used in this example (1 and 2) will reference "g1" and "g2" respectively.
          Panel Parameters cannot be referenced in expressions (they have no name).
    """


    @profile('Expression_Handler.UNDEFINED_NAME')
    def UNDEFINED_NAME(self):
        return ( "   (0*1111111*0)   " )   # This is a string that evaluates to zero, but is easy to spot in expressions

    @profile('Expression_Handler.get_expression_keywords')
    def get_expression_keywords(self):
        return ( { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' } )

    @profile('Expression_Handler.get_mdl_keywords')
    def get_mdl_keywords(self):
        # It's not clear how these will be handled, but they've been added here because they will be needed to avoid naming conflicts
        return ( [  "ABS",
                    "ABSORPTIVE",
                    "ACCURATE_3D_REACTIONS",
                    "ACOS",
                    "ALL_DATA",
                    "ALL_CROSSINGS",
                    "ALL_ELEMENTS",
                    "ALL_ENCLOSED",
                    "ALL_HITS",
                    "ALL_ITERATIONS",
                    "ALL_MESHES",
                    "ALL_MOLECULES",
                    "ALL_NOTIFICATIONS",
                    "ALL_TIMES",
                    "ALL_WARNINGS",
                    "ASCII",
                    "ASIN",
                    "ASPECT_RATIO",
                    "ATAN",
                    "BACK",
                    "BACK_CROSSINGS",
                    "BACK_HITS",
                    "BINARY",
                    "BOTTOM",
                    "BOX",
                    "BOX_TRIANGULATION_REPORT",
                    "BRIEF",
                    "CEIL",
                    "CELLBLENDER",
                    "CENTER_MOLECULES_ON_GRID",
                    "CHECKPOINT_INFILE",
                    "CHECKPOINT_OUTFILE",
                    "CHECKPOINT_ITERATIONS",
                    "CHECKPOINT_REALTIME",
                    "CHECKPOINT_REPORT",
                    "CLAMP",
                    "CLAMP_CONC",
                    "CLAMP_CONCENTRATION",
                    "CLOSE_PARTITION_SPACING",
                    "COMPLEX_PLACEMENT_ATTEMPTS",
                    "COMPLEX_PLACEMENT_FAILURE",
                    "COMPLEX_PLACEMENT_FAILURE_THRESHOLD",
                    "COMPLEX_RATE",
                    "CORNERS",
                    "COS",
                    "CONC",
                    "CONCENTRATION",
                    "COUNT",
                    "CUBIC",
                    "CUBIC_RELEASE_SITE",
                    "CUSTOM_SPACE_STEP",
                    "CUSTOM_RK",
                    "CUSTOM_TIME_STEP",
                    "D_3D",
                    "DIFFUSION_CONSTANT",
                    "DIFFUSION_CONSTANT_3D",
                    "D_2D",
                    "DIFFUSION_CONSTANT_2D",
                    "DEFAULT",
                    "DEFINE_COMPLEX_MOLECULE",
                    "DEFINE_MOLECULE",
                    "DEFINE_MOLECULES",
                    "DEFINE_REACTIONS",
                    "DEFINE_RELEASE_PATTERN",
                    "DEFINE_SURFACE_REGIONS",
                    "DEFINE_SURFACE_CLASS",
                    "DEFINE_SURFACE_CLASSES",
                    "DEGENERATE_POLYGONS",
                    "DELAY",
                    "DENSITY",
                    "DIFFUSION_CONSTANT_REPORT",
                    "DX",
                    "DREAMM_V3",
                    "DREAMM_V3_GROUPED",
                    "EFFECTOR_GRID_DENSITY",
                    "SURFACE_GRID_DENSITY",
                    "EFFECTOR_POSITIONS",
                    "EFFECTOR_STATES",
                    "ELEMENT_CONNECTIONS",
                    "ELEMENT_LIST",
                    "ELLIPTIC",
                    "ELLIPTIC_RELEASE_SITE",
                    "ERROR",
                    "ESTIMATE_CONC",
                    "ESTIMATE_CONCENTRATION",
                    "EXCLUDE_ELEMENTS",
                    "EXCLUDE_PATCH",
                    "EXCLUDE_REGION",
                    "EXIT",
                    "EXP",
                    "EXPRESSION",
                    "FALSE",
                    "FILENAME",
                    "FILENAME_PREFIX",
                    "FILE_OUTPUT_REPORT",
                    "FINAL_SUMMARY",
                    "FLOOR",
                    "FRONT",
                    "FRONT_CROSSINGS",
                    "FRONT_HITS",
                    "FULLY_RANDOM",
                    "GAUSSIAN_RELEASE_NUMBER",
                    "GEOMETRY",
                    "HEADER",
                    "HIGH_PROBABILITY_THRESHOLD",
                    "HIGH_REACTION_PROBABILITY",
                    "IGNORE",
                    "IGNORED",
                    "INCLUDE_ELEMENTS",
                    "INCLUDE_FILE",
                    "INCLUDE_PATCH",
                    "INCLUDE_REGION",
                    "INPUT_FILE",
                    "INSTANTIATE",
                    "INTERACTION_RADIUS",
                    "INVALID_OUTPUT_STEP_TIME",
                    "ITERATIONS",
                    "ITERATION_FRAME_DATA",
                    "ITERATION_LIST",
                    "ITERATION_NUMBERS",
                    "ITERATION_REPORT",
                    "LEFT",
                    "LIFETIME_TOO_SHORT",
                    "LIFETIME_THRESHOLD",
                    "LIST",
                    "LOCATION",
                    "LOG10",
                    "LOG",
                    "MAX",
                    "MAXIMUM_STEP_LENGTH",
                    "MEAN_DIAMETER",
                    "MEAN_NUMBER",
                    "MEMORY_PARTITION_X",
                    "MEMORY_PARTITION_Y",
                    "MEMORY_PARTITION_Z",
                    "MEMORY_PARTITION_POOL",
                    "MESHES",
                    "MICROSCOPIC_REVERSIBILITY",
                    "MIN",
                    "MISSED_REACTIONS",
                    "MISSED_REACTION_THRESHOLD",
                    "MISSING_SURFACE_ORIENTATION",
                    "MOD",
                    "MODE",
                    "MODIFY_SURFACE_REGIONS",
                    "MOLECULE_DENSITY",
                    "MOLECULE_NUMBER",
                    "MOLECULE",
                    "LIGAND",
                    "MOLECULES",
                    "MOLECULE_COLLISION_REPORT",
                    "MOLECULE_POSITIONS",
                    "LIGAND_POSITIONS",
                    "MOLECULE_STATES",
                    "LIGAND_STATES",
                    "MOLECULE_FILE_PREFIX",
                    "MOLECULE_PLACEMENT_FAILURE",
                    "NAME_LIST",
                    "NEGATIVE_DIFFUSION_CONSTANT",
                    "NEGATIVE_REACTION_RATE",
                    "NO",
                    "NOEXIT",
                    "NONE",
                    "NOTIFICATIONS",
                    "NULL",
                    "NUMBER_OF_SUBUNITS",
                    "NUMBER_OF_SLOTS",
                    "NUMBER_OF_TRAINS",
                    "NUMBER_TO_RELEASE",
                    "OBJECT",
                    "OBJECT_FILE_PREFIXES",
                    "OFF",
                    "ON",
                    "ORIENTATIONS",
                    "OUTPUT_BUFFER_SIZE",
                    "OVERWRITTEN_OUTPUT_FILE",
                    "PARTITION_LOCATION_REPORT",
                    "PARTITION_X",
                    "PARTITION_Y",
                    "PARTITION_Z",
                    "PI",
                    "POLYGON_LIST",
                    "POSITIONS",
                    "PROBABILITY_REPORT",
                    "PROBABILITY_REPORT_THRESHOLD",
                    "PROGRESS_REPORT",
                    "RADIAL_DIRECTIONS",
                    "RADIAL_SUBDIVISIONS",
                    "RAND_UNIFORM",
                    "RAND_GAUSSIAN",
                    "RATE_RULES",
                    "REACTION_DATA_OUTPUT",
                    "REACTION_OUTPUT_REPORT",
                    "REACTION_GROUP",
                    "RECTANGULAR",
                    "RECTANGULAR_RELEASE_SITE",
                    "REFERENCE_DIFFUSION_CONSTANT",
                    "REFLECTIVE",
                    "REGION_DATA",
                    "RELEASE_EVENT_REPORT",
                    "RELEASE_INTERVAL",
                    "RELEASE_PATTERN",
                    "RELEASE_PROBABILITY",
                    "RELEASE_SITE",
                    "REMOVE_ELEMENTS",
                    "RIGHT",
                    "ROTATE",
                    "ROUND_OFF",
                    "SCALE",
                    "SEED",
                    "SHAPE",
                    "SHOW_EXACT_TIME",
                    "SIN",
                    "SITE_DIAMETER",
                    "SITE_RADIUS",
                    "SPACE_STEP",
                    "SPHERICAL",
                    "SPHERICAL_RELEASE_SITE",
                    "SPHERICAL_SHELL",
                    "SPHERICAL_SHELL_SITE",
                    "SQRT",
                    "STANDARD_DEVIATION",
                    "STATE_VALUES",
                    "STEP",
                    "STRING_TO_NUM",
                    "SUBUNIT",
                    "SLOT",
                    "SUBUNIT_RELATIONSHIPS",
                    "SLOT_RELATIONSHIPS",
                    "SUM",
                    "SURFACE_CLASS",
                    "SURFACE_ONLY",
                    "SURFACE_POSITIONS",
                    "SURFACE_STATES",
                    "TAN",
                    "TARGET_ONLY",
                    "TET_ELEMENT_CONNECTIONS",
                    "THROUGHPUT_REPORT",
                    "TIME_LIST",
                    "TIME_POINTS",
                    "TIME_STEP",
                    "TIME_STEP_MAX",
                    "TO",
                    "TOP",
                    "TRAIN_DURATION",
                    "TRAIN_INTERVAL",
                    "TRANSLATE",
                    "TRANSPARENT",
                    "TRIGGER",
                    "TRUE",
                    "UNLIMITED",
                    "VACANCY_SEARCH_DISTANCE",
                    "VARYING_PROBABILITY_REPORT",
                    "USELESS_VOLUME_ORIENTATION",
                    "VERTEX_LIST",
                    "VIZ_DATA_OUTPUT",
                    "VIZ_MESH_FORMAT",
                    "VIZ_MOLECULE_FORMAT",
                    "VIZ_OUTPUT",
                    "VIZ_OUTPUT_REPORT",
                    "VIZ_VALUE",
                    "VOLUME_DATA_OUTPUT",
                    "VOLUME_OUTPUT_REPORT",
                    "VOLUME_DEPENDENT_RELEASE_NUMBER",
                    "VOLUME_ONLY",
                    "VOXEL_COUNT",
                    "VOXEL_LIST",
                    "VOXEL_SIZE",
                    "WARNING",
                    "WARNINGS",
                    "WORLD",
                    "YES",
                    "printf",
                    "fprintf",
                    "sprintf",
                    "print_time",
                    "fprint_time",
                    "fopen",
                    "fclose" ] )

    @profile('Expression_Handler.build_expression')
    def build_expression ( self, expr_list, as_python=False ):
        """ Converts an MDL expression list into either an MDL expression or Python expression using user names for parameters"""
        # With "as_python=True", this becomes:  build_py_expr_using_names ( self, expr_list ):
        # global global_params
        expr = ""
        if None in expr_list:
            expr = None
        else:
            expression_keywords = None
            if as_python:
                expression_keywords = self.get_expression_keywords()
            for token in expr_list:
                if token is None:
                    return None
                elif type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in self['gp_dict']:
                        expr = expr + self['gp_dict'][token_name]['name']
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        dbprint ( "build_expression did not find " + str(token_name) + " in " + str(self['gp_dict']) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    if as_python and (token in expression_keywords):
                        # This is a string so simply concatenate it after translation as needed
                        expr = expr + expression_keywords[token]
                    else:
                        # This is a string so simply concatenate it without translation
                        expr = expr + token
        return expr

    @profile('Expression_Handler.build_py_expr_using_ids')
    def build_py_expr_using_ids ( self, expr_list ):
        """ Converts an MDL expression list into a python expression using unique names for parameters"""
        # global global_params
        expr = ""
        if None in expr_list:
            expr = None
        else:
            expression_keywords = self.get_expression_keywords()
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in self['gp_dict']:
                        expr = expr + self['gp_dict'][token_name]['name']
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        dbprint ( "build_py_expr_using_ids did not find " + str(token_name) + " in " + str(self['gp_dict']) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it after translation as needed
                    if token in expression_keywords:
                        expr = expr + expression_keywords[token]
                    else:
                        expr = expr + token
        return expr

    @profile('Expression_Handler.parse_param_expr')
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
        # global global_params
        dbprint ( "parse_param_expr called with param_expr = " + str(param_expr) )
        #general_parameter_list = self['gp_dict']
        local_name_ID_dict = self.general_parameter_list
        dbprint ( "Parsing using local_name_ID_dict: " + str(local_name_ID_dict) )

        param_expr = param_expr.strip()
        if len(param_expr) == 0:
            return []
        st = None
        pt = None
        try:
            st = parser.expr(param_expr)
            pt = st.totuple()
        except:
            print ( "==> Parsing Exception: " + str ( sys.exc_info() ) )
        parameterized_expr = None  # param_expr
        if pt != None:
            #start_timer("All_Expression_Handler.recurse_tree_symbols" )
            parameterized_expr = self.recurse_tree_symbols ( local_name_ID_dict, pt, [] )
            #stop_timer("All_Expression_Handler.recurse_tree_symbols" )

            if parameterized_expr != None:

                # Remove trailing empty strings from parse tree - why are they there?
                while len(parameterized_expr) > 0:
                    if parameterized_expr[-1] != '':
                        break
                    parameterized_expr = parameterized_expr[0:-2]
        dbprint ( "Original: " + param_expr )
        dbprint ( "Parsed:   " + str(parameterized_expr) )
        # This is where the preservation of white space might take place
        return parameterized_expr

    @profile('Expression_Handler.count_stub')
    def count_stub ( self ):
        pass

    @profile('Expression_Handler.recurse_tree_symbols')
    def recurse_tree_symbols ( self, local_name_ID_dict, pt, current_expr ):
        """ Recurse through the parse tree looking for "terminal" items which are added to the list """
        dbprint ( "Top of recurse_tree_symbols" )

        # Strip off the outer layers that are not of interest
        while (type(pt) == tuple) and (len(pt) == 2) and (type(pt[1]) == tuple):
            # print ( "  changing " + str(pt) + " to " + str(pt[1]) )
            pt = pt[1]

        # self.count_stub()

        if type(pt) == tuple:
            # This is a tuple, so find out if it's a terminal leaf in the parse tree
            # Note: This code didn't use the token.ISTERMINAL function.
            # It might have been written as:
            #   terminal = False
            #   if len(pt) > 0:
            #     if token.ISTERMINAL(pt[0]):
            #       terminal = True
            # However, that doesn't check that the terminal is a 2-tuple containing a string
            terminal = False
            if len(pt) == 2:
                if type(pt[1]) == str:
                    terminal = True
            if terminal:
                # This is a 2-tuple with a type and value
                if pt[0] == token.NAME:
                    expression_keywords = self.get_expression_keywords()
                    if pt[1] in expression_keywords:
                        # This is a recognized name and not a user-defined symbol, so append the string itself
                        # return current_expr + [ pt[1] ]
                        return current_expr.append ( pt[1] )
                    else:
                        # This must be a user-defined symbol, so check if it's in the dictionary
                        pt1_str = str(pt[1])
                        #if pt[1] in local_name_ID_dict:
                        if pt1_str in local_name_ID_dict:
                            # Append the integer ID to the list after stripping off the leading "g"
                            #dbprint ( "Found a user defined name in the dictionary: " + pt1_str )
                            #dbprint ( "  Maps to: " + str(local_name_ID_dict[pt1_str]['par_id']) )
                            #return current_expr + [ int(local_name_ID_dict[pt1_str]['par_id'][1:]) ]
                            return current_expr.append ( int(local_name_ID_dict[pt1_str]['par_id'][1:]) )
                        else:
                            # Not in the dictionary, so append a None flag followed by the undefined name
                            #dbprint ( "Found a user defined name NOT in the dictionary: " + pt1_str )
                            #return current_expr + [ None, pt[1] ]
                            #return current_expr.append(None).append( pt[1] )
                            current_expr.append(None)
                            current_expr.append( pt[1] )
                            return current_expr
                else:
                    # This is a non-name part of the expression
                    #return current_expr + [ pt[1] ]
                    return current_expr.append ( pt[1] )
            else:
                # Break it down further
                for i in range(len(pt)):
                    next_segment = self.recurse_tree_symbols ( local_name_ID_dict, pt[i], current_expr )
                    if next_segment != None:
                        current_expr = next_segment
                return current_expr
        return None




def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)

def unregister():
    print ("Unregistering ", __name__)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()

