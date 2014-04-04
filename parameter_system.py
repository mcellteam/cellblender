#"""
#This program explores property initialization for property groups

#Flow:

#create_n_items calls:
#  app.parameter_system.new_parameter

#  app.parameter_system.new_parameter calls:
#    par_name_already_in_use()

#      par_name_already_in_use returns:
#        par_name in self['gname_to_id_dict']

#    allocate_available_pid()
#        allocate_available_pid checks lengths of lists

#    pan/gen_parameter_list.add()
#    
#    new_par.init_par_properties()
#      init_par_properties only sets properties
#    
#    update_name_ID_dictionary()
#"""

#bl_info = {
#  "version": "0.1",
#  "name": "Optimal Property Referencing",
#  'author': 'BlenderHawk',
#  "location": "Properties > Scene",
#  "category": "Cell Modeling"
#  }


# To support reload properly, try to access a package var, 
# if it's there, reload everything
#if "bpy" in locals():
#  import imp
#  print("Reloaded Parameters")
#else:
#  print("Imported Parameters")


import bpy
from bpy.props import *

from math import *
from random import uniform, gauss
import parser
import re
import token
import symbol
import sys
# Debugging:
from pdb import set_trace

import cellblender


# For timing code:
import time
import io

######################## Start of Profiling Code #######################

## From: http://wiki.blender.org/index.php/User:Z0r/PyDevAndProfiling

#prof = {}

#class profile:
#    ''' Function decorator for code profiling.'''
#    
#    def __init__(self,name):
#        self.name = name
#    
#    def __call__(self,fun):
#        def profile_fun(*args, **kwargs):
#            start = time.clock()
#            try:
#                return fun(*args, **kwargs)
#            finally:
#                duration = time.clock() - start
#                if not fun in prof:
#                    prof[fun] = [self.name, duration, 1]
#                else:
#                    prof[fun][1] += duration
#                    prof[fun][2] += 1
#        return profile_fun


#def print_statistics(app):
#    '''Prints profiling results to the console. Run from a Python controller.'''
#    
#    print ( "=== Execution Statistics with " + str(len(app.parameter_system.general_parameter_list)) + " general parameters and " + str(len(app.parameter_system.panel_parameter_list)) + " panel parameters ===" )

#    def timekey(stat):
#        return stat[1] / float(stat[2])

#    stats = sorted(prof.values(), key=timekey, reverse=True)

#    print ( '{:<55} {:>7} {:>7} {:>8}'.format('FUNCTION', 'CALLS', 'SUM(ms)', 'AV(ms)'))
#    for stat in stats:
#        print ( '{:<55} {:>7} {:>7.0f} {:>8.2f}'.format(stat[0],stat[2],stat[1]*1000,(stat[1]/float(stat[2]))*1000))
#        f = io.open(stat[0]+"_plot.txt",'a')
#        #f.write ( str(len(app.parameter_system.general_parameter_list)) + " " + str((stat[1]/float(stat[2]))*1000) + "\n" )
#        f.write ( str(len(app.parameter_system.general_parameter_list)) + " " + str(float(stat[1])*1000) + "\n" )
#        f.flush()
#        f.close()

#    f = io.open("plot_command.bat",'w')
#    f.write ( "java -jar ~/proj/java/Graphing/PlotData/Plot.jar" )
#    for stat in stats:
#        f.write ( " fxy=" + stat[0]+"_plot.txt" )
#    f.flush()
#    f.close()

#    f = io.open("delete_command.bat",'w')
#    for stat in stats:
#        f.write ( "rm -f " + stat[0]+"_plot.txt\n" )
#    f.flush()
#    f.close()


#class APP_OT_print_profiling(bpy.types.Operator):
#    bl_idname = "app.print_profiling"
#    bl_label = "Print Profiling"
#    bl_description = ("Print Profiling Information")
#    bl_options = {'REGISTER'}

#    def execute(self, context):
#        app = context.scene.app
#        print_statistics(app)
#        return {'FINISHED'}

#    def invoke(self, context, event):
#        app = context.scene.app
#        print_statistics(app)
#        return {'RUNNING_MODAL'}


#class APP_OT_clear_profiling(bpy.types.Operator):
#    bl_idname = "app.clear_profiling"
#    bl_label = "Clear Profiling"
#    bl_description = ("Clear Profiling Information")
#    bl_options = {'REGISTER'}

#    def execute(self, context):
#        prof.clear()
#        return {'FINISHED'}

#    def invoke(self, context, event):
#        prof.clear()
#        return {'RUNNING_MODAL'}

######################## End of Profiling Code #######################

######################## Start of Testing Code #######################


#@profile('create_n_items')
#def create_n_items ( app, context ):
#    if str(app.testing_param_generation_mode) == "separate":
#        print ( "Creating " + str(app.testing_num_items_to_add) + " separate independent parameters" )
#        for i in range(app.testing_num_items_to_add):
#            new_name = "P"+str(app.testing_next_param_num)
#            new_expr = str(app.testing_next_param_num)
#            p = app.parameter_system.new_parameter(new_name=new_name, new_expr=new_expr)
#            #p.old_par_name = p.par_name
#            app.testing_next_param_num += 1

#    elif str(app.testing_param_generation_mode) == "linear":
#        print ( "Creating " + str(app.testing_num_items_to_add) + " parameters that depend sequentially on one another" )
#        for i in range(app.testing_num_items_to_add):
#            new_name = "P"+str(app.testing_next_param_num)
#            new_expr = str(app.testing_next_param_num)

#            depends_on = "g"+str(app.testing_next_param_num-1)
#            if depends_on in app.parameter_system.general_parameter_list:
#                prev_name = app.parameter_system.general_parameter_list[depends_on].par_name
#                new_expr = new_expr + " + " + prev_name

#            # print ( "New expression = " + new_expr )
#            p = app.parameter_system.new_parameter(new_name=new_name, new_expr=new_expr)
#            #p.old_par_name = p.par_name
#            app.testing_next_param_num += 1

#    elif str(app.testing_param_generation_mode) == "firstn":

#        # First ensure that there are enough "first" parameters to draw from
#        while len(app.parameter_system.general_parameter_list) < app.testing_num_inputs_per_param:
#            new_name = "P"+str(app.testing_next_param_num)
#            new_expr = str(app.testing_next_param_num)
#            p = app.parameter_system.new_parameter(new_name=new_name, new_expr=new_expr)
#            #p.old_par_name = p.par_name
#            app.testing_next_param_num += 1

#        if app.testing_random_connection_mode:
#            print ( "Creating " + str(app.testing_num_items_to_add) + " parameters that depend randomly on " + str(app.testing_num_inputs_per_param) + " parameters." )
#        else:
#            print ( "Creating " + str(app.testing_num_items_to_add) + " parameters that depend on first " + str(app.testing_num_inputs_per_param) + " parameters." )
#            for i in range(app.testing_num_items_to_add):

#                new_name = "P"+str(app.testing_next_param_num)
#                new_expr = str(app.testing_next_param_num)
#                for i in range(app.testing_num_inputs_per_param):
#                    depends_on = "g"+str(i+1)
#                    prev_name = app.parameter_system.general_parameter_list[depends_on].par_name
#                    new_expr = new_expr + " + " + prev_name
#                p = app.parameter_system.new_parameter(new_name=new_name, new_expr=new_expr)
#                #p.old_par_name = p.par_name
#                app.testing_next_param_num += 1
#    
#    elif str(app.testing_param_generation_mode) == "molecules":
#        print ( "Creating " + str(app.testing_num_items_to_add) + " molecule(s) ..." )
#        for i in range(app.testing_num_items_to_add):
#            m = app.molecules.add_molecule(context, app.parameter_system)
#            m.name = "M"+str(app.testing_next_mol_num)
#            app.testing_next_mol_num += 1
#        print ( "Done creating molecules." )
#    
#    print ( "Done creating parameters." )


#class APP_OT_add_parameters(bpy.types.Operator):
#    bl_idname = "app.add_parameters"
#    bl_label = "Add Parameters"
#    bl_description = ("Add a number of parameters")
#    bl_options = {'REGISTER'}

#    def execute(self, context):
#        print ( "\n" )
#        app = context.scene.app
#        app.parameter_system.suspend_evaluation = True
#        create_n_items ( app, context )
#        app.parameter_system.suspend_evaluation = False
#        print ( "Done adding ... try auto update..." )
#        #if app.parameter_system.auto_update:
#        #    app.parameter_system.update_all_parameters()
#        print ( "Done adding and updating!!!!" )
#        return {'FINISHED'}
#        # testing_next_mol_num = IntProperty(name="Next Molecule Number", default=1)

#    def invoke(self, context, event):
#        self.execute(context)
#        return {'RUNNING_MODAL'}
#        
#        
#        

#class APP_PT_parameter_control(bpy.types.Panel):
#    bl_label = "Parameter Testing: Parameter Controls"
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "scene"
#    bl_options = {'DEFAULT_CLOSED'}

#    def draw(self, context):

#        mcell = context.scene.mcell
#        app = context.scene.app
#        if not app.initialized:
#            app.draw_uninitialized ( self.layout )
#        else:
#            layout = self.layout
#            row = layout.row()
#            col = row.column()
#            col.operator("app.update_all_parameters", text="Update All Parameters")
#            col = row.column()
#            col.operator("app.print_all_parameters", text="Print All Parameters")
#            col = row.column()
#            col.operator("app.print_parameter_system", text="Print General Parameters")
#            col = row.column()
#            col.operator("app.print_panel_parameters", text="Print Panel Parameters")
#            col = row.column()
#            col.operator("app.print_name_id_map", text="Print Name/ID Map")

#            row = layout.row()
#            col = row.column()
#            col.prop(mcell.parameter_system, "auto_update")
#            col = row.column()
#            col.prop(app, "silent_mode")

#            row = layout.row()
#            col = row.column()
#            col.prop(app, "testing_param_generation_mode", text="")
#            col = row.column()
#            col.prop(app, "testing_num_items_to_add")
#            col = row.column()
#            col.operator("app.add_parameters", text="Add Specified Items")
#            
#            if str(app.testing_param_generation_mode) == "separate":
#                pass

#            elif str(app.testing_param_generation_mode) == "linear":
#                pass

#            elif str(app.testing_param_generation_mode) == "firstn":
#                row = layout.row()
#                col = row.column()
#                col.prop(app, "testing_random_connection_mode")
#                col = row.column()
#                col.prop(app, "testing_num_inputs_per_param")

#            row = layout.row()
#            col = row.column()
#            col.operator("app.print_profiling", text="Print Profiling")
#            col = row.column()
#            col.operator("app.clear_profiling", text="Clear Profiling")

#            row = layout.row()
#            if not app.show_all_icons:
#                row.prop(app, "show_all_icons", text="Show All Icons", icon='TRIA_RIGHT')
#            else:
#                row.prop(app, "show_all_icons", text="Hide All Icons", icon='TRIA_DOWN')
#                icon_list = ['NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'GO_LEFT', 'PLUG', 'UI', 'NODE', 'NODE_SEL', 'FULLSCREEN', 'SPLITSCREEN', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ZOOMIN', 'ZOOMOUT', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'LINK_AREA', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'DOTSUP', 'DOTSDOWN', 'LINK', 'INLINK', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'LINKED', 'UNLINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'RENDER_REGION', 'BORDER_RECT', 'BORDER_LASSO', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'BLANK1', 'LAMP', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'EDIT', 'GAME', 'RADIO', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TEXTURE_SHADED', 'VIEW3D', 'IPO', 'OOPS', 'BUTS', 'FILESEL', 'IMAGE_COL', 'INFO', 'SEQUENCE', 'TEXT', 'IMASEL', 'SOUND', 'ACTION', 'NLA', 'SCRIPTWIN', 'TIME', 'NODETREE', 'LOGIC', 'CONSOLE', 'PREFERENCES', 'CLIP', 'ASSET_MANAGER', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'FACESEL_HLT', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'LIGHTPAINT', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LAMP_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'POSE_DATA', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'CAMERA_STEREO', 'PACKAGE', 'UGLYPACKAGE', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'SETTINGS', 'RENDER_ANIMATION', 'RENDER_STILL', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'LINE_DATA', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'RNA', 'RNA_ADD', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LAMP', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'OUTLINER_OB_SPEAKER', 'RESTRICT_VIEW_OFF', 'RESTRICT_VIEW_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_RENDER_ON', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LAMP', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_SPEAKER', 'OUTLINER_DATA_POSE', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'LAMP_POINT', 'LAMP_SUN', 'LAMP_SPOT', 'LAMP_HEMI', 'LAMP_AREA', 'META_EMPTY', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'COLOR_RED', 'COLOR_GREEN', 'COLOR_BLUE', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'FORCE_SMOKEFLOW', 'MODIFIER', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'CONSTRAINT_DATA', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_SMOKE', 'MOD_SOLIDIFY', 'MOD_SCREW', 'MOD_VERTEX_WEIGHT', 'MOD_DYNAMICPAINT', 'MOD_REMESH', 'MOD_OCEAN', 'MOD_WARP', 'MOD_SKIN', 'MOD_TRIANGULATE', 'MOD_WIREFRAME', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_AUDIO', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'SPACE2', 'SPACE3', 'KEYINGSET', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'VISIBLE_IPO_OFF', 'VISIBLE_IPO_ON', 'DRIVER', 'SOLO_OFF', 'SOLO_ON', 'FRAME_PREV', 'FRAME_NEXT', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'ROTATE', 'CURSOR', 'ROTATECOLLECTION', 'ROTATECENTER', 'ROTACTIVE', 'ALIGN', 'SMOOTHCURVE', 'SPHERECURVE', 'ROOTCURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'SCULPT_DYNTOPO', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'MAN_TRANS', 'MAN_ROT', 'MAN_SCALE', 'MANIPUL', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_INCREMENT', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'PASTEDOWN', 'COPYDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'SNAP_SURFACE', 'AUTOMERGE_ON', 'AUTOMERGE_OFF', 'RETOPO', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'BBOX', 'WIRE', 'SOLID', 'SMOOTH', 'POTATO', 'ORTHO', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'NDOF_DOM', 'NDOF_TURN', 'NDOF_FLY', 'NDOF_TRANS', 'LAYER_USED', 'LAYER_ACTIVE', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'LONGDISPLAY', 'SHORTDISPLAY', 'GHOST', 'IMGDISPLAY', 'SAVE_AS', 'SAVE_COPY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'OPEN_RECENT', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'FILE_TEXT', 'RECOVER_AUTO', 'SAVE_PREFS', 'LINK_BLEND', 'APPEND_BLEND', 'IMPORT', 'EXPORT', 'EXTERNAL_DATA', 'LOAD_FACTORY', 'LOOP_BACK', 'LOOP_FORWARDS', 'BACK', 'FORWARD', 'FILE_BACKUP', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'IMAGEFILE', 'BRUSH_ADD', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLAY_STRIPS', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_DARKEN', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_LIGHTEN', 'BRUSH_MASK', 'BRUSH_MIX', 'BRUSH_MULTIPLY', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_SUBTRACT', 'BRUSH_TEXDRAW', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'BRUSH_VERTEXDRAW', 'MATCAP_01', 'MATCAP_02', 'MATCAP_03', 'MATCAP_04', 'MATCAP_05', 'MATCAP_06', 'MATCAP_07', 'MATCAP_08', 'MATCAP_09', 'MATCAP_10', 'MATCAP_11', 'MATCAP_12', 'MATCAP_13', 'MATCAP_14', 'MATCAP_15', 'MATCAP_16', 'MATCAP_17', 'MATCAP_18', 'MATCAP_19', 'MATCAP_20', 'MATCAP_21', 'MATCAP_22', 'MATCAP_23', 'MATCAP_24', 'VIEW3D_VEC', 'EDIT_VEC', 'EDITMODE_VEC_DEHLT', 'EDITMODE_VEC_HLT', 'DISCLOSURE_TRI_RIGHT_VEC', 'DISCLOSURE_TRI_DOWN_VEC', 'MOVE_UP_VEC', 'MOVE_DOWN_VEC', 'X_VEC', 'SMALL_TRI_RIGHT_VEC']
#                for i in icon_list:
#                    row = layout.row()
#                    row.label(text=i, icon=i)



######################## End of Testing Code #######################




##### vvvvvvvvv   General Parameter Code   vvvvvvvvv

# For some reason, these two parent finding routines take far too much time and should not be used:
#
#@profile('get_path_to_parent')
#def get_path_to_parent(self_object):
#    " Return the Blender class path to the parent object with regard to the Blender Property Tree System "
#    path_to_self = "bpy.context.scene." + self_object.path_from_id()
#    path_to_parent = path_to_self[0:path_to_self.rfind(".")]
#    return path_to_parent
#
#@profile('get_parent')
#def get_parent(self_object):
#    " Return the parent Blender object with regard to the Blender Property Tree System "
#    path_to_parent = get_path_to_parent(self_object)
#    parent = eval(path_to_parent)
#    return parent



#@profile('spaced_strings_from_list')
def spaced_strings_from_list ( list_of_strings ):
    space = " "
    return space.join(list_of_strings)


class MCELL_UL_draw_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mcell = context.scene.mcell
        parsys = mcell.parameter_system
        par = parsys.general_parameter_list[index]
        # disp = par.par_name + " = " + str(par.expr) + " = " + str(par.value)

        disp = par.par_name + " = " + str(par.expr) + " = " + parsys.param_display_format%par.value
                    
        if par.isvalid:
            icon = 'FILE_TICK'
        else:
            icon = 'ERROR'
            # disp = disp + "  <= " + item.status
            
        layout.label(disp, icon=icon)


class MCELL_PT_parameter_system(bpy.types.Panel):
    bl_label = "CellBlender - General Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):

        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:
            ps = mcell.parameter_system
            layout = self.layout
            row = layout.row()
            if ps.param_error_list == "":
                row.label(text="Defined Parameters:", icon='FORCE_LENNARDJONES')
            else:
                row.label(text="Error with: " + ps.translated_param_name_list(ps.param_error_list), icon='ERROR')

            row = layout.row()

            col = row.column()
            col.template_list("MCELL_UL_draw_parameter", "parameter_system",
                              ps, "general_parameter_list",
                              ps, "active_par_index", rows=5)

            col = row.column(align=True)

            subcol = col.column(align=True)
            subcol.operator("mcell.add_parameter", icon='ZOOMIN', text="")
            subcol.operator("mcell.remove_parameter", icon='ZOOMOUT', text="")

            # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

            if len(ps.general_parameter_list) > 0:

                if str(ps.param_display_mode) != "none":
                    par = ps.general_parameter_list[ps.active_par_index]

                    row = layout.row()
                    layout.prop(par, "par_name")
                    if len(par.pending_expr) > 0:
                        layout.prop(par, "expr")
                        row = layout.row()
                        row.label(text="Undefined Expression: " + str(par.pending_expr), icon='ERROR')
                    elif not par.isvalid:
                        layout.prop(par, "expr", icon='ERROR')
                        row = layout.row()
                        row.label(text="Invalid Expression: " + str(par.pending_expr), icon='ERROR')
                    else:
                        layout.prop(par, "expr")
                    layout.prop(par, "units")
                    layout.prop(par, "descr")


            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            #row = layout.row()
            if not ps.show_panel:
                row.prop(ps, "show_panel", text="Show Parameter Options", icon='TRIA_RIGHT', emboss=False)
            else:
                col = row.column()
                col.alignment = 'LEFT'
                col.prop(ps, "show_panel", text="Hide Parameter Options", icon='TRIA_DOWN', emboss=False)
                col = row.column()
                col.prop(ps, "show_all_details", text="Show Internal Details for All")

                if ps.show_all_details:
                    detail_box = box.box()
                    if len(ps.general_parameter_list) > 0:
                        par = ps.general_parameter_list[ps.active_par_index]
                        par.draw_details(detail_box)
                    else:
                        detail_box.label(text="No General Parameters Defined")
                    if len(ps.param_error_list) > 0:
                    
                        # Note that this is the kind of logic that should be used to check
                        #    for undefined names matching newly created names:
                        
                        error_names_box = box.box()
                        param_error_names = ps.param_error_list.split()
                        for name in param_error_names:
                            error_names_box.label(text="Parameter Error for: " + name, icon='ERROR')

                row = box.row()
                row.prop(ps, "param_display_mode", text="Parameter Display Mode")
                row = box.row()
                row.prop(ps, "param_display_format", text="Parameter Display Format")
                row = box.row()
                row.prop(ps, "param_label_fraction", text="Parameter Label Fraction")




class MCELL_OT_add_parameter(bpy.types.Operator):
    bl_idname = "mcell.add_parameter"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.parameter_system.add_parameter(context)
        return {'FINISHED'}

class MCELL_OT_remove_parameter(bpy.types.Operator):
    bl_idname = "mcell.remove_parameter"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        status = context.scene.mcell.parameter_system.remove_active_parameter(context)
        if status != "":
            # One of: 'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY'
            self.report({'ERROR'}, status)
        return {'FINISHED'}


#class PP_OT_update_all_parameters(bpy.types.Operator):
#    bl_idname = "app.update_all_parameters"
#    bl_label = "Update All Parameters"
#    bl_description = "Updates all parameters"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.mcell.parameter_system.update_all_parameters()
#        return {'FINISHED'}

#class PP_OT_print_all_parameters(bpy.types.Operator):
#    bl_idname = "app.print_all_parameters"
#    bl_label = "Print All Parameters"
#    bl_description = "Prints all parameters"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.mcell.parameter_system.print_general_parameter_list()
#        context.scene.mcell.parameter_system.print_panel_parameter_list()
#        return {'FINISHED'}

#class PP_OT_print_parameter_system(bpy.types.Operator):
#    bl_idname = "app.print_parameter_system"
#    bl_label = "Print General Parameters"
#    bl_description = "Prints general parameters"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.mcell.parameter_system.print_general_parameter_list()
#        return {'FINISHED'}

#class PP_OT_print_panel_parameters(bpy.types.Operator):
#    bl_idname = "app.print_panel_parameters"
#    bl_label = "Print Panel Parameters"
#    bl_description = "Prints panel parameters"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.mcell.parameter_system.print_panel_parameter_list()
#        return {'FINISHED'}

#class PP_OT_print_name_id_map(bpy.types.Operator):
#    bl_idname = "app.print_name_id_map"
#    bl_label = "Print Name to ID Map"
#    bl_description = "Prints Name to ID Map"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.mcell.parameter_system.print_name_id_map()
#        return {'FINISHED'}


# __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})


class Parameter_Reference ( bpy.types.PropertyGroup ):
    """ Simple class to reference a panel parameter - used throughout the application """
    unique_static_name = StringProperty ( name="unique_name", default="" )

    #@profile('set_unique_static_name')
    def set_unique_static_name ( self, new_name ):
        self.unique_static_name = new_name
    
    #@profile('init_ref')
    def init_ref ( self, parameter_system, type_name, user_name=None, user_expr="0", user_descr="Panel Parameter", user_units="", user_int=False ):

        #new_name = "p" + str(parameter_system.allocate_available_pid())
        #self.set_unique_static_name ( new_name )

        if user_name == None:
            user_name = "none"

        new_par = parameter_system.new_parameter ( new_name=user_name, pp=True, new_expr=user_expr )
        new_par.descr = user_descr
        new_par.units = user_units
        new_par.isint = user_int
        #new_par.panel_path = self.path_from_id()  # This appears to take a very long time???
    
        self.set_unique_static_name ( new_par.name )
        

    #@profile('del_ref')
    def del_ref ( self, parameter_system ):
        parameter_system.del_panel_parameter ( self.unique_static_name )


    #@profile('get_param')
    def get_param ( self, plist ):
        return plist[self.unique_static_name]

    #@profile('get_expr')
    def get_expr ( self, plist ):
        return self.get_param(plist).expr

    #@profile('set_expr')
    def set_expr ( self, expr, plist ):
        p = self.get_param(plist)
        p.expr = expr

    #@profile('get_value')
    def get_value ( self, plist=None ):
        if plist == None:
            # No list specified, so get it from the top (it would be better to NOT have to do this!!!)
            mcell = bpy.context.scene.mcell
            plist = mcell.parameter_system.panel_parameter_list
        p = self.get_param(plist)
        if p.isint:
            return int(p.get_numeric_value())
        else:
            return p.get_numeric_value()

    #@profile('get_label')
    def get_label ( self, plist ):
        return self.get_param(plist).par_name

    #@profile('draw_stub')
    def draw_stub ( self ):
        pass

    ##@profile('draw')
    def draw ( self, layout, parameter_system ):
        #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

        self.draw_stub()

        plist = parameter_system.panel_parameter_list
        # print ( "plist = " + str(plist) )
        try:
            p = self.get_param(plist)
            # print ( "p = " + str(p) )
            if parameter_system.param_display_mode == 'two_line':
                # Create a box to put everything inside
                # Cheat by using the same name (layout) so subsequent code doesn't change
                layout = layout.box()
            row = layout.row()
            if p.isvalid:
                value = 0
                disp_val = " "
                if p.expr.strip() != "":
                    value = p.get_numeric_value()
                    disp_val = parameter_system.param_display_format%value
                if parameter_system.param_display_mode == 'one_line':
                    split = row.split(parameter_system.param_label_fraction)
                    col = split.column()
                    col.label ( text=p.par_name+" = "+disp_val )
                    
                    col = split.column()
                    col.prop ( p, "expr", text="" )
                    col = row.column()
                    col.prop ( p, "show_help", icon='QUESTION', text="" )
                elif parameter_system.param_display_mode == 'two_line':
                    row.label ( icon='NONE', text=p.par_name+" = "+disp_val )  # was icon='FORWARD'
                    row = layout.row()

                    split = row.split(0.03)
                    col = split.column()
                    col = split.column()

                    # col = row.column()
                    col.prop ( p, "expr", text="" )
                    col = row.column()
                    col.prop ( p, "show_help", icon='QUESTION', text="" )
            else:
                #row.prop (p, "expr", text=p.par_name+" = ?", icon='ERROR')
                #row = layout.row()
                #row.label (icon='ERROR', text="Invalid Expression: " + str(p.pending_expr) )

                value = 0
                if parameter_system.param_display_mode == 'one_line':
                    split = row.split(parameter_system.param_label_fraction)
                    col = split.column()
                    col.label ( text=p.par_name+" = ?", icon='ERROR' )

                    col = split.column()
                    col.prop ( p, "expr", text="", icon='ERROR' )
                    col = row.column()
                    col.prop ( p, "show_help", icon='QUESTION', text="" )
                elif parameter_system.param_display_mode == 'two_line':
                    row.label ( icon='ERROR', text=p.par_name+" = ?" )
                    row = layout.row()

                    split = row.split(0.03)
                    col = split.column()
                    col = split.column()

                    # col = row.column()
                    col.prop ( p, "expr", text="", icon='ERROR' )
                    col = row.column()
                    col.prop ( p, "show_help", icon='QUESTION', text="" )
                
                
            if p.show_help:
                # Draw the help information in a box inset from the left side
                row = layout.row()
                split = row.split(0.03)
                col = split.column()
                col = split.column()
                box = col.box()
                desc_list = p.descr.split("\n")
                for desc_line in desc_list:
                    box.label (text=desc_line)
                if len(p.units) > 0:
                    box.label(text="Units = " + p.units)
                if parameter_system.show_all_details:
                    box = box.box()
                    p.draw_details(box)

        except Exception as ex:
            # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
            print ( "Parameter not found (or other error) for: \"" + self.unique_static_name + "\" (" + str(self) + "), exception = " + str(ex) )
            pass


class Expression_Handler:

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
        Note that these ID numbers always reference General Parameters so the IDs
          used in this example (1 and 2) will reference "g1" and "g2" respectively.
          Panel Parameters cannot be referenced in expressions (they have no name).
    """
    
    #@profile('get_term_sep')
    def get_term_sep (self):
        return ( "~" )    # This is the string used to separate terms in an expression. It should be illegal in whatever syntax is being parsed.

    #@profile('UNDEFINED_NAME')
    def UNDEFINED_NAME(self):
        return ( "   (0*1111111*0)   " )   # This is a string that evaluates to zero, but is easy to spot in expressions
    
    #@profile('get_expression_keywords')
    def get_expression_keywords(self):
        return ( { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' } )

    #@profile('encode_expr_list_to_str')
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
                    print ( "Unexepected type while encoding list: " + str(expr_list) )

        if len(expr_str) >= len(term_sep):
            # Remove the first term_sep string (easier here than checking above)
            expr_str = expr_str[len(term_sep):]
        return expr_str


    #@profile('decode_str_to_expr_list')
    def decode_str_to_expr_list ( self, expr_str ):
        """ Recovers an expression list from a string that has been stored as a Blender StringProperty """
        expr_list = []
        terms = expr_str.split(self.get_term_sep())
        for e in terms:
            if len(e) > 0:
                if e[0] == '#':
                    if (len(e) > 1) and (e[1] == '?'):
                        expr_list = expr_list + [None] + [e[2:]]
                    else:
                        expr_list = expr_list + [int(e[1:])]
                else:
                    expr_list = expr_list + [e]
        return expr_list


    #@profile('build_mdl_expr')
    def build_mdl_expr ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into an MDL expression using user names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + gen_param_list[token_name].par_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_mdl_expr did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it without translation
                    expr = expr + token
        return expr

    #@profile('build_py_expr_using_names')
    def build_py_expr_using_names ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into a python expression using user names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            expression_keywords = self.get_expression_keywords()
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + gen_param_list[token_name].par_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_py_expr_using_names did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it after translation as needed
                    if token in expression_keywords:
                        expr = expr + expression_keywords[token]
                    else:
                        expr = expr + token
        return expr

    #@profile('build_py_expr_using_ids')
    def build_py_expr_using_ids ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into a python expression using unique names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            expression_keywords = self.get_expression_keywords()
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + token_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_py_expr_using_ids did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it after translation as needed
                    if token in expression_keywords:
                        expr = expr + expression_keywords[token]
                    else:
                        expr = expr + token
        return expr


    #@profile('parse_param_expr')
    def parse_param_expr ( self, param_expr, parameter_system ):
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
        general_parameter_list = parameter_system.general_parameter_list

        lcl_name_ID_dict = parameter_system['gname_to_id_dict']

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
        
            parameterized_expr = self.recurse_tree_symbols ( lcl_name_ID_dict, pt, [] )
            
            if parameterized_expr != None:
            
                # Remove trailing empty strings from parse tree - why are they there?
                while len(parameterized_expr) > 0:
                    if parameterized_expr[-1] != '':
                        break
                    parameterized_expr = parameterized_expr[0:-2]

        return parameterized_expr


    # #@profile('recurse_tree_symbols')
    def recurse_tree_symbols ( self, local_name_ID_dict, pt, current_expr ):
        """ Recurse through the parse tree looking for "terminal" items which are added to the list """

        if type(pt) == tuple:
            # This is a tuple, so find out if it's a terminal leaf in the parse tree

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
                        return current_expr + [ pt[1] ]
                    else:
                        # This must be a user-defined symbol, so check if it's in the dictionary
                        pt1_str = str(pt[1])
                        #if pt[1] in local_name_ID_dict:
                        if pt1_str in local_name_ID_dict:
                            # Append the integer ID to the list after stripping off the leading "g"
                            return current_expr + [ int(local_name_ID_dict[pt1_str][1:]) ]
                        else:
                            # Not in the dictionary, so append a None flag followed by the undefined name
                            return current_expr + [ None, pt[1] ]
                else:
                    # This is a non-name part of the expression
                    return current_expr + [ pt[1] ]
            else:
                # Break it down further
                for i in range(len(pt)):
                    next_segment = self.recurse_tree_symbols ( local_name_ID_dict, pt[i], current_expr )
                    if next_segment != None:
                        current_expr = next_segment
                return current_expr
        return None


    #@profile('evaluate_parsed_expr_py')
    def evaluate_parsed_expr_py ( self, param_sys ):
        self.updating = True        # Set flag to check for self-references
        param_sys.recursion_depth += 1

        #print ( "Inside evaluate_parsed_expr_py with depth = " + str(param_sys.recursion_depth) )

        self.isvalid = False        # Mark as invalid and return None on any failure

        general_parameter_list = param_sys.general_parameter_list
        who_I_depend_on_list = self.who_I_depend_on.split()
        for I_depend_on in who_I_depend_on_list:
            if not general_parameter_list[I_depend_on].isvalid:
                print ( "Cannot evaluate " + self.name + " because " + general_parameter_list[I_depend_on].name + " is not valid." )
                self.isvalid = False
                self.pending_expr = self.expr
                param_sys.register_validity ( self.name, False )
                # Might want to propagate invalidity here as well ???
                param_sys.recursion_depth += -1
                self.updating = False
                print ( "Return from evaluate_parsed_expr_py with depth = " + str(param_sys.recursion_depth) )
                return None
            exec ( general_parameter_list[I_depend_on].name + " = " + str(general_parameter_list[I_depend_on].value) )
        #print ( "About to exec (" + self.name + " = " + self.parsed_expr_py + ")" )
        exec ( self.name + " = " + self.parsed_expr_py )
        self.isvalid = True
        self.pending_expr = ""
        param_sys.register_validity ( self.name, True )
        return ( eval ( self.name, locals() ) )


# Callbacks for Property updates appear to require global (non-member) functions
# This is circumvented by simply calling the associated member function passed as self

##@profile('update_parameter_name')
def update_parameter_name ( self, context ):
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.par_name_changed ( context )

##@profile('update_parameter_expression')
def update_parameter_expression ( self, context ):
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.expression_changed ( context )

##@profile('update_parameter_parsed_expression')
def update_parameter_parsed_expression ( self, context ):
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.parsed_expression_changed ( context )

##@profile('update_parameter_value')
def update_parameter_value ( self, context ):
    """ The "self" passed in is a Parameter_Data object. """
    if not self.disable_parse:
        self.value_changed ( context )

##@profile('dummy_update')
def dummy_update ( self, context ):
    """ The "self" passed in is a Parameter_Data object. """
    pass


class Parameter_Data ( bpy.types.PropertyGroup, Expression_Handler ):
    """ Parameter - Contains the actual data for a parameter """
    name = StringProperty  ( name="ID Name", default="" )      # Unique Static Identifier used as the key to find this item in the collection
    expr = StringProperty  ( name="Expression", default="0", description="Expression to be evaluated for this parameter", update=update_parameter_expression )
    pending_expr = StringProperty ( default="" )     # Pending expression
    parsed_expr = StringProperty ( name="Parsed", default="", update=update_parameter_parsed_expression )
    parsed_expr_py = StringProperty ( name="Parsed_Python", default="" )
    value = FloatProperty ( name="Value", default=0.0, description="Current evaluated value for this parameter", update=update_parameter_value )
    isvalid = BoolProperty ( default=True )   # Boolean flag to signify that the value and float_value are accurate

    who_I_depend_on = StringProperty ( name="who_I_depend_on", default="" )
    who_depends_on_me = StringProperty ( name="who_depends_on_me", default="" )

    par_name = StringProperty ( name="Name", default="Unnamed", description="Name of this Parameter", update=update_parameter_name )  # User's name for this parameter - can be changed by the user
    old_par_name = StringProperty ( name="Name", default="", description="Old name of this Parameter" )  # Will generally be the same as the current name except during a name change
    units = StringProperty ( name="Units", default="none", description="Units for this Parameter" )
    descr = StringProperty ( name="Description", default="", description="Description of this Parameter" )

    show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    panel_path = StringProperty ( name="Panel Path", default="" )
    ispanel = BoolProperty ( default=False )  # Boolean flag to signify panel parameter
    isint = BoolProperty ( default=False )    # Boolean flag to signify an integer parameter
    initialized = BoolProperty(default=False) # Set to true by "init_par_properties"

    updating = BoolProperty(default=False)    # Set to true when changing a value to suppress infinite recursion
    disable_parse = BoolProperty ( default=True )   # Boolean flag to signify that this parameter should not be parsed at this time, start with True for speed!!
    
    
    #@profile('__init__')
    def __init__ ( self ):
        print ( "The Parameter_Data.__init__ function has been called." )

    #@profile('Parameter_Data.init_par_properties')
    def init_par_properties ( self ):
        #print ( "Setting Defaults for a Parameter" )

        # TODO - C H E C K   F O R   D U P L I C A T E    N A M E S  !!!!!!!!

        # self.name = "?"  Don't change the unique name (self.name), since it should be set at creation
        # self.expr = "0"
        self.pending_expr = ""
        # self.parsed_expr = ""
        self.parsed_expr_py = ""
        # self.value = 0.0
        self.isvalid = True

        self.who_I_depend_on = ""
        self.who_depends_on_me = ""

        # self.par_name = "Parameter_" + self.name[1:]
        self.old_par_name = self.par_name
        self.units = ""
        self.descr = self.par_name + " Description"
        self.show_help = False
        self.panel_path = ""
        self.ispanel = False
        self.isint = False
        self.initialized = True

        self.updating = False
        self.disable_parse = False

    ##@profile('draw_details')
    def draw_details ( self, layout ):
        p = self
        layout.label("Internal Information:")
        layout.label(" Parameter Name = " + p.par_name)
        layout.label(" Parameter ID Name = " + p.name)
        layout.label(" Parameter Expression = " + p.expr)
        layout.label(" Parameter Pending Expression = " + p.pending_expr)
        layout.label(" Parameter Parsed Expression = " + p.parsed_expr)
        layout.label(" Parameter Parsed Python Expression = " + p.parsed_expr_py)
        layout.label(" Numeric Value = " + str(p.value))
        layout.label(" Is Valid Flag = " + str(p.isvalid))
        layout.label(" Who I Depend On = " + p.who_I_depend_on)
        layout.label(" Who Depends on Me = " + p.who_depends_on_me)
        layout.label(" Old Parameter Name = " + p.old_par_name)
        layout.label(" Panel Path = " + p.panel_path)
        layout.label(" Is Panel = " + str(p.ispanel))
        layout.label(" Is Integer = " + str(p.isint))
        layout.label(" Initialized = " + str(p.initialized))


    ##@profile('draw')
    def draw ( self, layout ):
        # This is generally not called, so show a banner if it is
        print ( "####################################################" )
        print ( "####################################################" )
        print ( "####################################################" )
        print ( "####################################################" )
        print ( "#######  ParameterData.draw was Called  ############" )
        print ( "####################################################" )
        print ( "####################################################" )
        print ( "####################################################" )
        print ( "####################################################" )


    #@profile('print_parameter')
    def print_parameter ( self ):
        print ( "  Printing  Parameter:" )
        print ( "    Internal key name: " + self.name )
        print ( "    User Name: " + self.par_name )
        print ( "    Expression: " + self.expr )
        print ( "    Parsed Expr: " + self.parsed_expr )
        print ( "    Python Expr: " + self.parsed_expr_py )
        print ( "    Description: " + self.descr )
        print ( "    Is Panel: " + str(self.ispanel) )
        print ( "    Is Integer: " + str(self.isint) )
        print ( "    Is Initialized: " + str(self.initialized) )
        print ( "    Is Valid: " + str(self.isvalid) )
        print ( "    I depend on: " + str(self.who_I_depend_on) )
        print ( "    Who depends on me: " + str(self.who_depends_on_me) )
        print ( "    Value: " + str(self.value) )
        if len(self.panel_path) > 0:
            print ( "    Panel Path: " + self.panel_path )


    #@profile('get_numeric_value')
    def get_numeric_value ( self ):
        return self.value


    #@profile('update_parsed_and_dependencies')
    def update_parsed_and_dependencies ( self, parameter_system ):
        general_parameter_list = parameter_system.general_parameter_list 
        old_who_I_depend_on_set = set(self.who_I_depend_on.split())
        
        expr_list = self.parse_param_expr ( self.expr, parameter_system )
        
        print ( "Expression List for " + str(self.expr) + " = " + str(expr_list) )

        if expr_list is None:
            self.parsed_expr = ""
            self.parsed_expr_py = ""
            self.who_I_depend_on = ""
            self.isvalid = False
            self.pending_expr = self.expr
            parameter_system.register_validity ( self.name, False )

        elif None in expr_list:
            self.isvalid = False
            self.pending_expr = self.expr
            parameter_system.register_validity ( self.name, False )
        else:
            self.parsed_expr = self.encode_expr_list_to_str ( expr_list )
            self.parsed_expr_py = self.build_py_expr_using_ids ( expr_list, general_parameter_list )
            who_I_depend_on_list = [ "g"+str(x) for x in expr_list if type(x) == int ]
            who_I_depend_on_list = [ p for p in set(who_I_depend_on_list) ]
            who_I_depend_on_str = spaced_strings_from_list ( who_I_depend_on_list )
            self.who_I_depend_on = who_I_depend_on_str
            
            new_who_I_depend_on_set = set(self.who_I_depend_on.split())
            remove_me_from_set = old_who_I_depend_on_set.difference(new_who_I_depend_on_set)
            add_me_to_set = new_who_I_depend_on_set.difference(old_who_I_depend_on_set)
            for remove_me_from in remove_me_from_set:
                p = general_parameter_list[remove_me_from]
                if self.name in p.who_depends_on_me:
                    # p.who_depends_on_me = spaced_strings_from_list ( [x for x in set(p.who_depends_on_me.split()).remove(self.name)] )
                    pset = set(p.who_depends_on_me.split())
                    pset.discard(self.name)
                    p.who_depends_on_me = spaced_strings_from_list ( [x for x in pset] )

            for add_me_to in add_me_to_set:
                p = general_parameter_list[add_me_to]
                if not self.name in p.who_depends_on_me:
                    p.who_depends_on_me = (p.who_depends_on_me + " " + self.name).strip()

            self.pending_expr = ""
            parameter_system.register_validity ( self.name, True )

    #@profile('par_name_changed')
    def par_name_changed ( self, context ):
        # print ( "Updating a Property_Reference.Parameter_Data name with who_depends_on_me = " + self.who_depends_on_me )
        """
        This parameter's user name string has been changed.

        Update the entire parameter system based on a parameter's name being changed.
        This function is called with a "self" which is a GeneralParameterProperty
        whenever the name is changed (either programatically or via the GUI).
        This function needs to force the redraw of all parameters that depend
        on this one so their expressions show the new name as needed.

        The "self" passed in is a GeneralParameterProperty object.
        """

        if self.old_par_name == self.par_name:
            # Nothing to do ...
            return
        
        mcell = context.scene.mcell
        params = mcell.parameter_system
        general_param_list = params.general_parameter_list
        panel_param_list = params.panel_parameter_list

        #if params.suspend_evaluation:
        #    return


        # TODO - C H E C K   F O R   I L L E G A L    N A M E S  !!!!!!!!

        #print ( "Attempting name change from " + self.old_par_name + " to " + self.par_name )

        if self.name[0] == "g":
            # This is a general parameter which must maintain unique names
            if params.par_name_already_in_use ( self.par_name ):
                # Don't allow the change, so change it back!!!
                print ( "Cannot change name from " + self.old_par_name + " to " + self.par_name + " because " + self.par_name + " is already in use." )
                self.par_name = self.old_par_name
                return

            #print ( "Name change from " + self.old_par_name + " to " + self.par_name )
            params.update_name_ID_dictionary(self)

        self.old_par_name = self.par_name

        # Update any expressions that use this parameter (to change this name in their expressions)

        who_depends_on_me_list = self.who_depends_on_me.split()
        for pname in who_depends_on_me_list:
            p = None
            if pname[0] == "g":
                p = general_param_list[pname]
            else:
                p = panel_param_list[pname]
            p.regenerate_expr_from_parsed_expr ( general_param_list )

        # Check the parameters with errors in case this name change fixes any of them

        if len(params.param_error_list) > 0:
            # There are parameters with errors that this name change might fix
            param_error_names = params.param_error_list.split()
            for pname in param_error_names:
                # pname will be the name of a parameter that contains an error - possibly an invalid name!
                if pname != self.name:   # Some small attempt to avoid recursion?
                    p = None
                    if pname[0] == "g":
                        p = general_param_list[pname]
                    else:
                        p = panel_param_list[pname]
                    # "Touch" the parameter's expression to cause it to be re-evaluated
                    p.expr = p.expr


    #@profile('expression_changed')
    def expression_changed ( self, context ):
        """
        This parameter's expression string has been changed.

        Update the entire parameter system based on a parameter's expression being changed.
        This function is called with a "self" which is a Property_Reference.Parameter_Data
        whenever the string expression is changed (either programatically or via the GUI).
        This function needs to update the parsed expression of this parameter based on the
        expression having changed.

        The "self" passed in is a Property_Reference.Parameter_Data object.
        """

        #print ( "Expression Changed for " + str(self.name) )

        mcell = context.scene.mcell
        params = mcell.parameter_system
        gen_param_list = params.general_parameter_list
        
        #if params.suspend_evaluation:
        #    return

        expr_list = self.parse_param_expr ( self.expr, params )
        #print ( "New expr_list = " + str(expr_list) )
        if expr_list is None:
            print ( "ERROR ... expr_list = None!!!" )
            self.parsed_expr = ""
            self.parsed_expr_py = ""
            self.isvalid = False
            self.pending_expr = self.expr
            params.register_validity ( self.name, False )
        else:
            if None in expr_list:
                self.isvalid = False
                self.pending_expr = self.expr
                params.register_validity ( self.name, False )
            else:
                self.isvalid = True
                self.pending_expr = ""
                if (self.expr.strip() == "") and (self.parsed_expr != ""):
                    # When an expression is empty, it's value should be zero
                    self.parsed_expr = ""
                params.register_validity ( self.name, True )
            parsed_expr = self.encode_expr_list_to_str ( expr_list )
            if self.parsed_expr != parsed_expr:
                # Force an update by changing the property
                #print ( "Old expression of \"" + str(self.parsed_expr) + "\" != \"" + str(parsed_expr) + "\" making assignment..." )
                self.parsed_expr = parsed_expr



    #@profile('parsed_expression_changed')
    def parsed_expression_changed ( self, context ):
        """ 
        This parameter's parsed expression string has been changed.

        Update the parameter system based on a parameter's parsed expression being changed.
        This function is called with a "self" which is a Property_Reference.Parameter_Data
        whenever the parsed expression is changed (either programatically or via the GUI).
        This function needs to evaluate the new parsed expression to produce an updated
        value for this expression.

        The "self" passed in is a Property_Reference.Parameter_Data object.
        """

        mcell = context.scene.mcell
        params = mcell.parameter_system
        gen_param_list = params.general_parameter_list
        
        #if params.suspend_evaluation:
        #    return

        #print ( "Parsed Expression Changed for " + str(self.name) + " = " + str(self.parsed_expr) )

        if self.parsed_expr == "":
            self.parsed_expr_py = ""
            self.who_I_depend_on = ""
            if self.value != 0:
                self.value = 0
        else:
            # self.update_parsed_and_dependencies(params)

            old_who_I_depend_on_set = set(self.who_I_depend_on.split())
            
            expr_list = self.decode_str_to_expr_list (self.parsed_expr )
            
            #print ( "Expression List for " + str(self.expr) + " = " + str(expr_list) )

            if expr_list is None:
                self.parsed_expr = ""
                self.parsed_expr_py = ""
                self.who_I_depend_on = ""
                self.isvalid = False
                self.pending_expr = self.expr
            elif None in expr_list:
                self.parsed_expr_py = ""
                self.who_I_depend_on = ""
                self.isvalid = False
                self.pending_expr = self.expr
            else:
                self.parsed_expr_py = self.build_py_expr_using_ids ( expr_list, gen_param_list )
                who_I_depend_on_list = [ "g"+str(x) for x in expr_list if type(x) == int ]
                who_I_depend_on_list = [ p for p in set(who_I_depend_on_list) ]
                who_I_depend_on_str = spaced_strings_from_list ( who_I_depend_on_list )
                self.who_I_depend_on = who_I_depend_on_str
                self.isvalid = True
                self.pending_expr = ""
            
            if self.isvalid:
                new_who_I_depend_on_set = set(self.who_I_depend_on.split())
                remove_me_from_set = old_who_I_depend_on_set.difference(new_who_I_depend_on_set)
                add_me_to_set = new_who_I_depend_on_set.difference(old_who_I_depend_on_set)
                for remove_me_from in remove_me_from_set:
                    p = gen_param_list[remove_me_from]
                    if self.name in p.who_depends_on_me:
                        # p.who_depends_on_me = spaced_strings_from_list ( [x for x in set(p.who_depends_on_me.split()).remove(self.name)] )
                        pset = set(p.who_depends_on_me.split())
                        pset.discard(self.name)
                        p.who_depends_on_me = spaced_strings_from_list ( [x for x in pset] )

                for add_me_to in add_me_to_set:
                    p = gen_param_list[add_me_to]
                    if not self.name in p.who_depends_on_me:
                        p.who_depends_on_me = (p.who_depends_on_me + " " + self.name).strip()

                count_down = 3
                done = False
                #print ( "Enter Evaluation loop:" )
                params.recursion_depth = 0
                while not done:
                    try:
                        params.recursion_depth = 0
                        value = self.evaluate_parsed_expr_py(params)
                        if value != None:
                            if self.value != value:
                                # Force an update by changing this parameters value
                                self.value = value
                            self.isvalid = True
                            self.pending_expr = ""
                        else:
                            self.isvalid = False
                            self.pending_expr = self.expr
                        done = True
                    except Exception as e:
                        print ( ">>>>>>>>>>>>>>>>\n\nGot an exception while evaluating ... try again\n\n>>>>>>>>>>>>>>>>" )
                        print ( "   Exception was " + str(e) )
                        count_down += -1
                        if count_down > 0:
                            done = False
                        else:
                            self.isvalid = False
                            self.pending_expr = self.expr
                            done = True
                #print ( "Exit Evaluation loop." )
                params.recursion_depth = 0


    #@profile('value_changed')
    def value_changed ( self, context ):
        """ 
        Update the entire parameter system based on a parameter's value being changed.
        This function is called with a "self" which is a Property_Reference.Parameter_Data
        whenever the value is changed (typically via an expression evaluation).
        This function needs to force the redraw of all values that depend on this one.

        The "self" passed in is a Property_Reference.Parameter_Data object.
        """

        mcell = context.scene.mcell
        params = mcell.parameter_system
        gen_param_list = params.general_parameter_list
        
        #if params.suspend_evaluation:
        #    return

        #print ( "Value changed for " + str(self.name) )
        
        # Force a redraw of the expression itself
        self.expr = self.expr

        # Propagate forward ...
        who_depends_on_me_list = []
        if (self.who_depends_on_me != None) and (self.who_depends_on_me != "") and (self.who_depends_on_me != "None"):
            who_depends_on_me_list = self.who_depends_on_me.split()
        for pname in who_depends_on_me_list:
            p = None
            if pname[0] == "g":
                p = gen_param_list[pname]
            else:
                p = params.panel_parameter_list[pname]
            if p != None:
                if p.updating:
                    # May or may not be an error? print ( "Warning: Circular reference detected when updating " + self.name + "(" + self.par_name + ")")
                    pass
                p.parsed_expr = p.parsed_expr




    #@profile('regenerate_expr_from_parsed_expr')
    def regenerate_expr_from_parsed_expr ( self, general_parameter_list ):
        expr_list = self.decode_str_to_expr_list ( self.parsed_expr )
        regen_expr = self.build_mdl_expr ( expr_list, general_parameter_list )
        if regen_expr != None:
            if self.expr != regen_expr:
                self.expr = regen_expr


    #@profile('build_mdl_expr')
    def build_mdl_expr ( self, expr_list, gen_param_list ):
        """ Converts an MDL expression list into an MDL expression using user names for parameters"""
        expr = ""
        if None in expr_list:
            expr = None
        else:
            for token in expr_list:
                if type(token) == int:
                    # This is an integer parameter ID, so look up the variable name to concatenate
                    token_name = "g" + str(token)
                    if token_name in gen_param_list:
                        expr = expr + gen_param_list[token_name].par_name
                    else:
                        # In previous versions, this case might have defined a new parameter here.
                        # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                        #threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                        print ( "build_mdl_expr did not find " + str(token_name) + " in " + str(gen_param_list) + ", adding an undefined name flag to " + expr )
                        expr = expr + self.UNDEFINED_NAME()
                else:
                    # This is a string so simply concatenate it without translation
                    expr = expr + token
        return expr


class ParameterSystemPropertyGroup ( bpy.types.PropertyGroup ):
    """ Master list of all existing Parameters throughout the application """
    general_parameter_list = CollectionProperty ( type=Parameter_Data, name="GP List" )
    panel_parameter_list = CollectionProperty ( type=Parameter_Data, name="PP List" )
    
    # This might be needed to keep a mapping from user names to id names for parsing speed
    #general_name_to_id_list = CollectionProperty ( type=Name_ID_Data, name="Name ID" )
    
    active_par_index = IntProperty(name="Active Parameter", default=0)
    next_gid = IntProperty(name="Counter for Unique General Parameter IDs", default=1)  # Start ID's at 1 to confirm initialization
    next_pid = IntProperty(name="Counter for Unique Panel Parameter IDs", default=1)  # Start ID's at 1 to confirm initialization
    
    recursion_depth = IntProperty(default=0)  # Counts recursion depth

    param_display_mode_enum = [ ('one_line',  "One line per parameter", ""), ('two_line',  "Two lines per parameter", "") ]
    param_display_mode = bpy.props.EnumProperty ( items=param_display_mode_enum, default='one_line', name="Parameter Display Mode", description="Display layout for each parameter" )
    param_display_format = StringProperty ( default='%.6g', description="Formatting string for each parameter" )
    param_label_fraction = FloatProperty(precision=4, min=0.0, max=1.0, default=0.35, description="Width (0 to 1) of parameter's label")
    
    
    show_panel = BoolProperty(name="Show Panel", default=False)
    show_all_details = BoolProperty(name="Show All Details", default=False)
    print_panel = BoolProperty(name="Print Panel", default=True)
    param_error_list = StringProperty(name="Parameter Error List", default="")
    currently_updating = BoolProperty(name="Currently Updating", default=False)
    suspend_evaluation = BoolProperty(name="Suspend Evaluation", default=False)
    auto_update = BoolProperty ( name="Auto Update", default=True )

    #@profile('ParameterSystemPropertyGroup.init_properties')
    def init_properties ( self ):
        # print ( "Inside init_properties for ParameterSystemPropertyGroup" )
        if not ('gname_to_id_dict' in self):
            self['gname_to_id_dict'] = {}

    #@profile('allocate_available_gid')
    def allocate_available_gid ( self ):
        """ Return a unique parameter ID for a new parameter """
        if (len(self.general_parameter_list) <= 0) and (len(self.panel_parameter_list) <= 0):
            # Reset the ID to 1 when there are no more parameters
            self.next_gid = 1
        self.next_gid += 1
        return ( self.next_gid - 1 )


    #@profile('allocate_available_pid')
    def allocate_available_pid ( self ):
        """ Return a unique parameter ID for a new parameter """
        if (len(self.general_parameter_list) <= 0) and (len(self.panel_parameter_list) <= 0):
            # Reset the ID to 1 when there are no more parameters
            self.next_pid = 1
        self.next_pid += 1
        return ( self.next_pid - 1 )


    #@profile('get_parameter')
    def get_parameter ( self, unique_name, pp=False ):
        if pp:
            # Look for this name in the list of panel parameter references
            if unique_name in self.panel_parameter_list:
                return self.panel_parameter_list[unique_name]
            else:
                return None
        else:
            # Look for this name in the list of general parameter references
            if unique_name in self.general_parameter_list:
                return self.general_parameter_list[unique_name]
            else:
                return None


    #@profile('add_general_parameter_with_values')
    def add_general_parameter_with_values ( self, name, expression, units, description ):
        """ Add a new parameter to the list of parameters """
        p = self.new_parameter ( new_name=name, pp=False, new_expr=expression, new_units=units, new_desc=description )
        return p


    #@profile('new_parameter')
    def new_parameter ( self, new_name=None, pp=False, new_expr=None, new_units=None, new_desc=None ):
        """ Add a new parameter to the list of parameters """
        #print ( "new_parameter called with a requested name of " + str(new_name) )

        if new_name != None:
            #print ( "new_parameter called with a requested name of " + new_name )
            if (not pp) and self.par_name_already_in_use(new_name):
                #print ( "new_parameter called with a requested name that already exists." )
                # Cannot use this name because it's already used by a general parameter
                # Could optionally return with an error,
                #   but for now, just set to None to pick an automated name
                new_name = None

        #print ( "Creating the new Parameter" )
        
        par_num = -1
        par_name = "undefinded"
        par_user_name = "undefined"
        if pp:
            # Set up a panel parameter
            par_num = self.allocate_available_pid()
            par_name = "p" + str(par_num)
            par_user_name = "PP" + str(par_num)
        else:
            # Set up a general parameter
            par_num = self.allocate_available_gid()
            par_name = "g" + str(par_num)
            par_user_name = "P" + str(par_num)

        if not (new_name is None):
            par_user_name = new_name

        if pp:
            # Create the parameter in the panel parameter list
            new_par = self.panel_parameter_list.add()
        else:
            # Create the parameter in the general parameter list
            new_par = self.general_parameter_list.add()

        new_par.disable_parse = True

        new_par.name = par_name
        new_par.par_name = par_user_name

        new_par.init_par_properties()

        if not (new_expr is None):
            new_par.expr = new_expr

        if not pp:
            self.update_name_ID_dictionary(new_par)

        new_par.disable_parse = False

        return new_par


    #@profile('del_panel_parameter')
    def del_panel_parameter ( self, unique_name ):

        if unique_name[0] == 'p':
            p = self.panel_parameter_list[unique_name]

            # The parameters that I depend on have references to me that must be removed
            remove_me_from_set = set(p.who_I_depend_on.split())
            for remove_me_from in remove_me_from_set:
                rp = self.general_parameter_list[remove_me_from]
                if self.name in rp.who_depends_on_me:
                    rpset = set(rp.who_depends_on_me.split())
                    rpset.discard(p.name)
                    rp.who_depends_on_me = spaced_strings_from_list ( [x for x in rpset] )

            # Delete the parameter from the panel parameter list
            self.panel_parameter_list.remove(self.panel_parameter_list.find(unique_name))
        else:
            print ( "Warning: del_panel_parameter called on a non-panel parameter: " + unique_name )
            print ( "  Parameter " + unique_name + " was not deleted!!" )
            ## Delete the parameter from the general parameter list
            #self.general_parameter_list.remove(self.general_parameter_list.find(unique_name))
            ## Also delete it from the name to ID mapping (check first to avoid exception)
            #if unique_name in self['gname_to_id_dict'].keys():
            #    self['gname_to_id_dict'].pop(unique_name)


    #@profile('add_parameter')
    def add_parameter ( self, context ):
        """ Add a new parameter to the list of general parameters and set as the active parameter """
        #print ( "Adding a parameter to the Parameter List" )
        p = self.new_parameter()
        self.active_par_index = len(self.general_parameter_list)-1
        return p

    #@profile('remove_active_parameter')
    def remove_active_parameter ( self, context ):
        """ Remove the active parameter from the list of parameters if not needed by others """
        status = ""
        if len(self.general_parameter_list) > 0:
            p = self.general_parameter_list[self.active_par_index]
            if p != None:
                ok_to_delete = True
                if p.who_depends_on_me != None:
                    who_depends_on_me = p.who_depends_on_me.strip()
                    if len(who_depends_on_me) > 0:
                        ok_to_delete = False
                        status = "Parameter " + p.par_name + " is used by: " + self.translated_param_name_list(who_depends_on_me)
                if ok_to_delete:
                    # The parameters that I depend on have references to me that must be removed
                    remove_me_from_set = set(p.who_I_depend_on.split())
                    for remove_me_from in remove_me_from_set:
                        rp = self.general_parameter_list[remove_me_from]
                        if self.name in rp.who_depends_on_me:
                            rpset = set(rp.who_depends_on_me.split())
                            rpset.discard(p.name)
                            rp.who_depends_on_me = spaced_strings_from_list ( [x for x in rpset] )

                    # Remove this name from the gname to id dictionary
                    print ( "Testing if " + p.par_name + " is in " + str(self['gname_to_id_dict'].keys()) )
                    if p.par_name in self['gname_to_id_dict'].keys():
                        self['gname_to_id_dict'].pop(p.par_name)
                    
                    # Remove this parameter from the general parameter list and move the pointer
                    self.general_parameter_list.remove ( self.active_par_index )
                    self.active_par_index -= 1
                    if self.active_par_index < 0:
                        self.active_par_index = 0

        return ( status )

    #@profile('register_validity')
    def register_validity ( self, name, valid ):
        """ Register the global validity or invalidity of a parameter """
        if valid:
            # Check to see if it's in the list and remove it
            if name in self.param_error_list:
                param_error_names = self.param_error_list.split()    # Convert to a list
                while name in param_error_names:                 # Remove all references
                    param_error_names.remove(name)
                self.param_error_list = spaced_strings_from_list(param_error_names)  # Rebuild the string
        else:
            # Check to see if it's in the list and add it
            if not (name in self.param_error_list):
                self.param_error_list = self.param_error_list + " " + name

    #@profile('translated_param_name_list')
    def translated_param_name_list ( self, param_name_string ):
        param_list = param_name_string.split()
        name_list = ""
        for name in param_list:
            if len(name_list) > 0:
                name_list = name_list + " "
            if name[0] == 'g':
                name_list = name_list + self.general_parameter_list[name].par_name
            else:
                name_list = name_list + self.panel_parameter_list[name].par_name
        return name_list

    ##@profile('draw')
    def draw ( self, layout ):
        pass

    #@profile('print_general_parameter_list')
    def print_general_parameter_list ( self ):
        print ( "General Parameters:" )
        for p in self.general_parameter_list:
            p.print_parameter()

    #@profile('print_panel_parameter_list')
    def print_panel_parameter_list ( self ):
        print ( "Panel Parameters:" )
        for p in self.panel_parameter_list:
            p.print_parameter()

    #@profile('print_name_id_map')
    def print_name_id_map ( self ):
        #print ( "Name to ID Map:" )
        #for p in self.general_name_to_id_list:
        #    p.print_parameter()
        gname_dict = self['gname_to_id_dict']
        print ( "Name to ID Map:" )
        for k,v in gname_dict.items():
            print ( "  gname: " + str(k) + " = " + str(v) )


    #@profile('par_name_already_in_use')
    def par_name_already_in_use ( self, par_name ):
        #return par_name in self.general_name_to_id_list
        return par_name in self['gname_to_id_dict']


    #@profile('update_name_ID_dictionary')
    def update_name_ID_dictionary ( self, param ):
        # print ( "Update the general parameters name to ID dictionary with \"" + str(param.par_name) + "\" -> \"" + str(param.name) + "\"" )

        # Would like to do something like this:
        #   self.general_name_to_id_list.update ( { param.par_name : param.name } )
        # But Blender collections don't implement the "update" function

        # print ( "Updating gname_to_id_dict inside update_name_ID_dictionary" )
        gname_dict = self['gname_to_id_dict']

        if (len(param.old_par_name) > 0) and (param.old_par_name != param.par_name):
            # This is a name change, so remove the old name first
            while param.old_par_name in gname_dict:
                gname_dict.pop(param.old_par_name)

        # Perform the update
        gname_dict.update ( { param.par_name : param.name } )

        # Remove all entries that match the new name (if any)
        #while param.par_name in gname_dict:
        #    gname_dict.pop(param.par_name)

        # Add the new entry
        #gname_dict[param.par_name] = param.name


        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})



#################################################################################################################
##########################    Application's "User" Code Starts Here   ###########################################
#################################################################################################################


###
### Top Level Initialization Code:
###

#class PP_OT_init_app(bpy.types.Operator):
#    bl_idname = "app.init_app"
#    bl_label = "Init App"
#    bl_description = "Initialize Application"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        print ( "Initialize Application" )
#        # context.scene.mcell.init_properties()
#        context.scene.app.init_properties()
#        return {'FINISHED'}



###
### Model Initialization Code:
###


#class AppInitializationGroup(bpy.types.PropertyGroup):
#    
#    initialized = BoolProperty ( name="initialized", default = False )
#    
#    iterations = PointerProperty ( name="iterations", type=Parameter_Reference )
#    time_step = PointerProperty ( name="time_step", type=Parameter_Reference )


#    #@profile('__init__')
#    def __init__ ( self ):
#        print ( "AppInitializationGroup.__init__ was called!!" )
#        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
#        # print ( "type(iterations) = " + str(type(iterations)) )
#    
#    #@profile('AppInitializationGroup.init_properties')
#    def init_properties ( self, parameter_system ):
#        # print ( "Inside init_properties for AppInitializationGroup" )
#        self.iterations.init_ref(parameter_system, "Iteration_Type", user_name="Iterations", user_expr="1", user_units="", user_descr="Iterations to run", user_int=True)
#        self.time_step.init_ref(parameter_system, "TimeStep_Type", user_name="Time Step", user_expr="1e-6", user_units="sec", user_descr="Time step for each iteration")
#        self.initialized = True

#    #@profile('register')
#    def register():
#        # print ( "AppInitializationGroup.register was called!!" )
#        # print ( "type(iterations) = " + str(type(iterations)) )
#        pass
#    
#    ##@profile('draw')
#    def draw(self, layout, parameter_system):
#        # print ( "In AppInitializationGroup.draw" )
#        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
#        self.iterations.draw(layout,parameter_system)
#        self.time_step.draw(layout,parameter_system)
#            
#    

#class APP_PT_Initialization(bpy.types.Panel):
#    bl_label = "Parameter Testing: App Initialization"
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "scene"
#    bl_options = {'DEFAULT_CLOSED'}

#    ##@profile('draw')
#    def draw(self, context):
#        app = context.scene.app
#        mcell = context.scene.mcell
#        if not app.initialized:
#            app.draw_uninitialized ( self.layout )
#        else:
#            # print ( "Inside APP_PT_Initialization.draw, app.initialization is of type " + str(type(app.initialization)) )
#            app.initialization.draw ( self.layout, mcell.parameter_system )



###
### Molecule Definition Code:
###


#class APP_OT_molecule_add(bpy.types.Operator):
#    bl_idname = "app.molecule_add"
#    bl_label = "Add Molecule"
#    bl_description = "Add a new molecule type to an MCell model"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.app.molecules.add_molecule(context, context.scene.mcell.parameter_system)
#        return {'FINISHED'}

#class APP_OT_molecule_remove(bpy.types.Operator):
#    bl_idname = "app.molecule_remove"
#    bl_label = "Remove Molecule"
#    bl_description = "Remove selected molecule type from an MCell model"
#    bl_options = {'REGISTER', 'UNDO'}

#    def execute(self, context):
#        context.scene.app.molecules.remove_active_molecule(context, context.scene.mcell.parameter_system)
#        # One of: 'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY'
#        self.report({'INFO'}, "Deleted Molecule")
#        return {'FINISHED'}


## Callbacks for all Property updates appear to require global (non-member) functions.
## This is circumvented by simply calling the associated member function passed as self:

#def check_callback(self, context):
#    self.check_callback(context)
#    return

#class AppMoleculeProperty(bpy.types.PropertyGroup):
#    """ Example class for handling the molecules panel parameters """
#    id = IntProperty(name="ID", default=-1)
#    name = StringProperty ( name="Molecule Name", default="Molecule", description="The molecule species name", update=check_callback )

#    diffusion_constant = PointerProperty(name="Diffusion Constant", type=Parameter_Reference)
#    diameter = PointerProperty(name="Diameter", type=Parameter_Reference)
#    mol_wt = PointerProperty(name="Molecular Weight", type=Parameter_Reference)
#    status = StringProperty(name="Status")

#    #@profile('AppMoleculeProperty.init_properties')
#    def init_properties ( self, parameter_system ):
#        #print ( "Inside init_properties for AppMoleculeProperty" )
#        self.name = "Molecule_"+str(self.id)
#        self.diffusion_constant.init_ref(parameter_system, "CellBlender_DiffConst_Type", user_name="Diff Const", user_expr="0.001*"+str(self.id), user_units="m/s", user_descr="Diffusion Constant for this Molecule")
#        self.diameter.init_ref(parameter_system, "CellBlender_Diameter_Type", user_name="Diameter", user_expr="0.002*"+str(self.id), user_units="m", user_descr="Diameter for this Molecule")
#        self.mol_wt.init_ref(parameter_system, "CellBlender_MolWt_Type", user_name="Mol Wt", user_expr="0.003*"+str(self.id), user_units="g", user_descr="Molecular Weight for this Molecule")

#    #@profile('remove_properties')
#    def remove_properties ( self, parameter_system ):
#        #print ( "Inside remove_properties for AppMoleculeProperty" )
#        self.diffusion_constant.del_ref(parameter_system)
#        self.diameter.del_ref(parameter_system)
#        self.mol_wt.del_ref(parameter_system)

#    #@profile('print_details')
#    def print_details( self, thresh, prefix=""):
#        print ( "Name = " + self.name )
#        print ( "  " + self.diffusion_constant.get_label() + " = " + self.diffusion_constant.get_text() )
#        print ( "  " + self.diameter.get_label() + " = " + self.diameter.get_text() )
#        print ( "  " + self.mol_wt.get_label() + " = " + self.mol_wt.get_text() )

#    ##@profile('draw')
#    def draw ( self, layout, parameter_system ):
#        if parameter_system.param_display_mode == 'one_line':
#            layout.prop ( self, "name" )
#        else:
#            row = layout.row()
#            row.label ( "Molecule Name" )
#            row = layout.row()
#            row.prop ( self, "name", text="" )
#        self.diffusion_constant.draw(layout, parameter_system)
#        self.diameter.draw(layout, parameter_system)
#        self.mol_wt.draw(layout, parameter_system)
#            
#    #@profile('check_callback')
#    def check_callback(self, context):
#        """Allow the parent molecule list (AppMoleculesListProperty) to do the checking"""
#        # get_parent(self).check(context)  # get_parent takes too long ... hard code the molecule list parent
#        context.scene.app.molecules.check(context, self)
#        return


#class APP_UL_check_molecule(bpy.types.UIList):
#    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#        # print ( "APP_UL_check_molecule called" )
#        if item.status:
#            layout.label(item.status, icon='ERROR')
#        else:
#            layout.label(item.name, icon='FILE_TICK')


#class APP_PT_define_molecules(bpy.types.Panel):
#    bl_label = "Parameter Testing: Define Molecules"
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "scene"
#    bl_options = {'DEFAULT_CLOSED'}

#    ##@profile('draw')
#    def draw ( self, context ):
#        # Call the draw function for the instance being drawn in this panel
#        mcell = context.scene.mcell
#        app = context.scene.app
#        if not app.initialized:
#            app.draw_uninitialized ( self.layout )
#        else:
#            # print ( "Inside APP_PT_Initialization.draw, app.initialization is of type " + str(type(app.initialization)) )
#            app.molecules.draw ( self.layout, mcell.parameter_system )


#class AppMoleculesListProperty(bpy.types.PropertyGroup):
#    molecule_list = CollectionProperty(type=AppMoleculeProperty, name="Molecule List")
#    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
#    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
#    show_advanced = bpy.props.BoolProperty(default=True)  # If Properties are not shown, they may not exist!!!

#    #@profile('AppMoleculesListProperty.init_properties')
#    def init_properties ( self, parameter_system ):
#        # It's not clear if setting the defaults for the molecule list should
#        #    set defaults for each molecule in the list or
#        #    delete all the molecules to create an empty list
#        # Since it's more interesting to set the molecules back to their defaults ... do that.
#        if self.molecule_list:
#            for mol in self.molecule_list:
#                mol.init_properties(parameter_system)

#    #@profile('add_molecule')
#    def add_molecule ( self, context, parameter_system ):
#        """ Add a new molecule to the list of molecules and set as the active molecule """
#        new_mol = self.molecule_list.add()
#        new_mol.id = self.allocate_available_id()
#        new_mol.init_properties ( parameter_system )
#        self.active_mol_index = len(self.molecule_list)-1
#        return new_mol

#    #@profile('remove_active_molecule')
#    def remove_active_molecule ( self, context, parameter_system ):
#        """ Remove the active molecule from the list of molecules """

#        mol = self.molecule_list[self.active_mol_index]
#        mol.remove_properties(parameter_system)
#        
#        self.molecule_list.remove ( self.active_mol_index )
#        self.active_mol_index -= 1
#        if self.active_mol_index < 0:
#            self.active_mol_index = 0
#        if self.molecule_list:
#            #print ( "Inside remove_active_molecule with self of type " + str(type(self)) )
#            #print ( "  remove_active_molecule calling self.check(context)" )
#            self.check(context,mol)

#    #@profile('AppMoleculesListProperty.check')
#    def check ( self, context, mol ):
#        """Checks for duplicate or illegal molecule name"""
#        # Note: Some of the list-oriented functionality is appropriate here (since this
#        #        is a list), but some of the molecule-specific checks (like name legality)
#        #        could be handled by the the molecules themselves. They're left here for now.
#        #print ( "Top of local check with self of type " + str(type(self)) )
#        #print ( "  and parent of type " + str(type(get_parent(self))) )

#        #mol = self.molecule_list[self.active_mol_index]

#        status = ""

#        # Check for duplicate molecule name
#        mol_keys = self.molecule_list.keys()
#        if mol_keys.count(mol.name) > 1:
#            status = "Duplicate molecule: %s" % (mol.name)

#        # Check for illegal names (Starts with a letter. No special characters.)
#        mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
#        m = re.match(mol_filter, mol.name)
#        if m is None:
#            status = "Molecule name error: %s" % (mol.name)

#        mol.status = status

#        # print ( "Bottom of local check with self of type " + str(type(self)) )
#        return


#    #@profile('allocate_available_id')
#    def allocate_available_id ( self ):
#        """ Return a unique molecule ID for a new molecule """
#        if len(self.molecule_list) <= 0:
#            # Reset the ID to 1 when there are no more molecules
#            self.next_id = 1
#        self.next_id += 1
#        return ( self.next_id - 1 )

#    ##@profile('draw')
#    def draw ( self, layout, parameter_system ):
#        row = layout.row()
#        row.label(text="Defined Molecules:", icon='FORCE_LENNARDJONES')
#        row = layout.row()
#        col = row.column()
#        col.template_list("APP_UL_check_molecule", "define_molecules",
#                          self, "molecule_list",
#                          self, "active_mol_index",
#                          rows=2)
#        col = row.column(align=True)
#        col.operator("app.molecule_add", icon='ZOOMIN', text="")
#        col.operator("app.molecule_remove", icon='ZOOMOUT', text="")
#        if self.molecule_list:
#            mol = self.molecule_list[self.active_mol_index]
#            mol.draw ( layout, parameter_system )




#####
##### Overall Application Code:
#####


#class AppPropertyGroup(bpy.types.PropertyGroup):
#    """ Properties for this particular application """

#    # parameter_system = PointerProperty(type=ParameterSystemPropertyGroup, name="Parameter System")

#    initialization = PointerProperty(type=AppInitializationGroup, name="Initialization")
#    molecules = PointerProperty(type=AppMoleculesListProperty, name="Defined Molecules")

#    initialized = BoolProperty ( name="initialized", default=False )

#    silent_mode = BoolProperty ( name="Silent", default=True )
#    
#    show_all_icons = BoolProperty ( name="Icons", default=False )

#    testing_param_generation_enum = [
#        ('separate', "Independent Parameters", ""),
#        ('linear',   "Each depends on the previous", ""),
#        ('firstn',  "All depend on first N", ""),
#        ('molecules',  "Molecules", "") ]
#    testing_param_generation_mode = bpy.props.EnumProperty ( items=testing_param_generation_enum, default='firstn', name="Parameter Generation Mode" )


#    testing_random_connection_mode = BoolProperty ( name="Random", default=False )
#    testing_num_inputs_per_param = IntProperty(name="Inputs / Param", default=3)
#    testing_num_items_to_add = IntProperty(name="Items to Add", default=2000)
#    testing_next_param_num = IntProperty(name="Next Parameter Number", default=1)
#    testing_next_mol_num = IntProperty(name="Next Molecule Number", default=1)

#    #@profile('AppPropertyGroup.init_properties')
#    def init_properties ( self ):
#        mcell = bpy.context.scene.mcell
#        print ( "Inside init_properties for AppPropertyGroup" )
#        mcell.parameter_system.init_properties()
#        self.initialization.init_properties ( mcell.parameter_system )
#        self.molecules.init_properties ( mcell.parameter_system )
#        self.initialized = True

#    ##@profile('draw_uninitialized')
#    def draw_uninitialized ( self, layout ):
#        row = layout.row()
#        row.operator("app.init_app", text="Initialize Testing App")
#    
#    #@profile('__init__')
#    def __init__ ( self ):
#        print ( "AppPropertyGroup.__init__ called." )


def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    #bpy.types.Scene.app = bpy.props.PointerProperty(type=AppPropertyGroup)

def unregister():
    print ("Unregistering ", __name__)
    #del bpy.types.Scene.app
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()

