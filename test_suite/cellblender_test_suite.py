relative_path_to_mcell = "mcell"
#relative_path_to_mcell = "/../mcell_git/src/linux/mcell"

"""
# This section of code was used (from the command line) to copy this addon to the Blender addons area. Now the makefile performs that task.
install_to = "2.75"


# From within Blender: import cellblender.test_suite.cellblender_test_suite
if __name__ == "__main__":
  # Simple method to "install" a new version with "python test_suite/cellblender_test_suite.py" assuming "test_suite" directory exists in target location.
  import os
  print ( "MAIN with __file__ = " + __file__ )
  print ( " Installing into Blender " + install_to )
  os.system ( "cp ./" + __file__ + " ~/.config/blender/" + install_to + "/scripts/addons/" + __file__ )
  print ( "Copied files" )
  exit(0)
"""


bl_info = {
  "version": "0.1",
  "name": "CellBlender Test Suite",
  'author': 'Bob',
  "location": "Properties > Scene",
  "category": "Cell Modeling"
  }


##################
#  Support Code  #
##################

import sys
import os
import os.path
import hashlib
import bpy
import math
import mathutils
from bpy.props import *

test_groups = []
max_test_groups = 30   # Needed to define a BoolVectorProperty to show and hide each group (32 is max!?!?!)
next_test_group_num = 0    # The index number of the next group to be added


def register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num ):
    found = -1
    for gnum in range(len(test_groups)):
        g = test_groups[gnum]
        if g["group_name"] == group_name:
            found = gnum

    if found < 0:
        test_groups.append ( { "group_index":next_test_group_num, "group_name":group_name, "group_tests":[] } )
        found = len(test_groups) - 1
        next_test_group_num += 1
        if next_test_group_num >= max_test_groups:
            print ( "================================================================================================" )
            print ( "Too many test groups defined. Increase the number of 'show_group_#' entries and max_test_groups." )
            print ( "================================================================================================" )
            bpy.ops.wm.quit_blender()

    test_groups[found]["group_tests"].append ( { "test_name":test_name, "operator_name":operator_name } )
    
    return next_test_group_num
    


class CellBlenderTestPropertyGroup(bpy.types.PropertyGroup):

    # Properties needed by the testing application itself

    show_setup = bpy.props.BoolProperty(name="ShowSetUp", default=True)
    path_to_mcell = bpy.props.StringProperty(name="Path to MCell", default="")
    path_to_blend = bpy.props.StringProperty(name="Path to Blend", default="")
    run_mcell = bpy.props.BoolProperty(name="Run MCell", default=False)
    test_status = bpy.props.StringProperty(name="TestStatus", default="?")
    
    # Properties needed for the dynamically created test case groups

    show_group = BoolVectorProperty ( size=max_test_groups ) # Used for showing and hiding each panel - can only hold 32 elements!!!!!

    groups_real = bpy.props.BoolProperty(default=False)
    # Start with all defaulted to "True" so they can be changed to "False" making them real ID properties!!!
    show_group_0 = bpy.props.BoolProperty(default=True)
    show_group_1 = bpy.props.BoolProperty(default=True)
    show_group_2 = bpy.props.BoolProperty(default=True)
    show_group_3 = bpy.props.BoolProperty(default=True)
    show_group_4 = bpy.props.BoolProperty(default=True)
    show_group_5 = bpy.props.BoolProperty(default=True)
    show_group_6 = bpy.props.BoolProperty(default=True)
    show_group_7 = bpy.props.BoolProperty(default=True)
    show_group_8 = bpy.props.BoolProperty(default=True)
    show_group_9 = bpy.props.BoolProperty(default=True)
    show_group_10 = bpy.props.BoolProperty(default=True)
    show_group_11 = bpy.props.BoolProperty(default=True)
    show_group_12 = bpy.props.BoolProperty(default=True)
    show_group_13 = bpy.props.BoolProperty(default=True)
    show_group_14 = bpy.props.BoolProperty(default=True)
    show_group_15 = bpy.props.BoolProperty(default=True)
    show_group_16 = bpy.props.BoolProperty(default=True)
    show_group_17 = bpy.props.BoolProperty(default=True)
    show_group_18 = bpy.props.BoolProperty(default=True)
    show_group_19 = bpy.props.BoolProperty(default=True)
    show_group_20 = bpy.props.BoolProperty(default=True)
    show_group_21 = bpy.props.BoolProperty(default=True)
    show_group_22 = bpy.props.BoolProperty(default=True)
    show_group_23 = bpy.props.BoolProperty(default=True)
    show_group_24 = bpy.props.BoolProperty(default=True)
    show_group_25 = bpy.props.BoolProperty(default=True)
    show_group_26 = bpy.props.BoolProperty(default=True)
    show_group_27 = bpy.props.BoolProperty(default=True)
    show_group_28 = bpy.props.BoolProperty(default=True)
    show_group_29 = bpy.props.BoolProperty(default=True)
    show_group_30 = bpy.props.BoolProperty(default=True)

    def make_real ( self ):
      if not self.groups_real:
        self.show_group_0 = False
        self.show_group_1 = False
        self.show_group_2 = False
        self.show_group_3 = False
        self.show_group_4 = False
        self.show_group_5 = False
        self.show_group_6 = False
        self.show_group_7 = False
        self.show_group_8 = False
        self.show_group_9 = False
        self.show_group_10 = False
        self.show_group_11 = False
        self.show_group_12 = False
        self.show_group_13 = False
        self.show_group_14 = False
        self.show_group_15 = False
        self.show_group_16 = False
        self.show_group_17 = False
        self.show_group_18 = False
        self.show_group_19 = False
        self.show_group_20 = False
        self.show_group_21 = False
        self.show_group_22 = False
        self.show_group_23 = False
        self.show_group_24 = False
        self.show_group_25 = False
        self.show_group_26 = False
        self.show_group_27 = False
        self.show_group_28 = False
        self.show_group_29 = False
        self.show_group_30 = False
        self.groups_real = True


class CellBlenderTestSuitePanel(bpy.types.Panel):
    bl_label = "CellBlender Test Suite"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    def draw(self, context):
        app = context.scene.cellblender_test_suite

        box = self.layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not app.show_setup:
            row.prop(app, "show_setup", icon='TRIA_RIGHT', text="Setup Panel", emboss=False)
        else:
            row.prop(app, "show_setup", icon='TRIA_DOWN', text="Setup Panel", emboss=False)

            row = box.row()
            row.operator("cellblender_test.set_mcell_path", text="Set Path to MCell Binary", icon='FILESEL')
            row = box.row()
            row.prop ( app, "path_to_mcell" )

            # Problems getting this to work ... use current directory for now
            #row = box.row()
            #row.operator("cellblender_test.set_blend_path", text="Set Path to Blend files", icon='FILESEL')
            #row = box.row()
            #row.prop ( app, "path_to_blend" )


        row = self.layout.row()
        row.operator ( "cellblender_test.load_home_file" )
        row.operator ( "cellblender_test.save_home_file" )

        row = self.layout.row()
        if app.test_status == "?":
          row.label( icon='QUESTION',  text="?" )
        elif app.test_status == "P":
          row.label( icon='FILE_TICK', text="Pass" )
        elif app.test_status == "F":
          row.label( icon='ERROR',     text="Fail" )
        row.prop(app, "run_mcell")

        for group_num in range(next_test_group_num):
            # print ( "Drawing Group " + str(group_num) )
            group = test_groups[group_num]

            box = self.layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'

            gi = group['group_index']

            # print ( "Group Index = " + str(gi) + ", app[gi] = " + str(app["show_group_"+str(gi)]) )
            
            if not app["show_group_"+str(gi)]:
                row.prop(app, "show_group_"+str(gi), icon='TRIA_RIGHT', text=group['group_name'], emboss=False)
            else:
                row.prop(app, "show_group_"+str(gi), icon='TRIA_DOWN', text=group['group_name'], emboss=False)
                test_list = group['group_tests']
                for test in test_list:
                    row = box.row()
                    row.operator(test['operator_name'], text=test['test_name'])


class LoadHomeOp(bpy.types.Operator):
    bl_idname = "cellblender_test.load_home_file"
    bl_label = "Load Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        context.scene.cellblender_test_suite.test_status == "?"
        context.scene.cellblender_test_suite.groups_real = False
        bpy.ops.wm.read_homefile()
        return { 'FINISHED' }


class SaveHomeOp(bpy.types.Operator):
    bl_idname = "cellblender_test.save_home_file"
    bl_label = "Save Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        context.scene.cellblender_test_suite.test_status == "?"
        bpy.ops.wm.save_homefile()
        return { 'FINISHED' }


class SetMCellBinary(bpy.types.Operator):
    bl_idname = "cellblender_test.set_mcell_path"
    bl_label = "Set MCell Binary"
    bl_description = ("Set MCell Binary. If needed, download at mcell.org/download.html")
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        app = context.scene.cellblender_test_suite
        app.path_to_mcell = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SetBlendPath(bpy.types.Operator):
    bl_idname = "cellblender_test.set_blend_path"
    bl_label = "Set Path to Blend File"
    bl_description = ("Set Path to the Blend File created for each test.")
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")

    def execute(self, context):
        app = context.scene.cellblender_test_suite
        app.path_to_blend = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class CellBlender_Model:

    old_type = None
    context = None
    scn = None
    mcell = None
    path_to_blend = None
    
    def __init__(self, cb_context):
        # bpy.ops.wm.read_homefile()
        self.old_type = None
        self.context = cb_context
        self.setup_cb_defaults ( self.context )
        self.context.scene.cellblender_test_suite.test_status == "?"
        
    def get_scene(self):
        return self.scn
        
    def get_mcell(self):
        return self.mcell


    """
    def get_3d_view_areas(self):
        areas_3d = []
        for area in self.context.screen.areas:
            if area.type == 'VIEW_3D':
                areas_3d = areas_3d + [area]
                # area.spaces.active.show_manipulator = False
        return areas_3d
    """

    def get_3d_view_spaces(self):
        spaces_3d = []
        for area in self.context.screen.areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    spaces_3d = spaces_3d + [space]
                    # area.spaces.active.show_manipulator = False
        return spaces_3d


    def set_view_3d(self):
        area = bpy.context.area
        if area == None:
            self.old_type = 'VIEW_3D'
        else:
            self.old_type = area.type
        area.type = 'VIEW_3D'
      
    def set_view_back(self):
        area = bpy.context.area
        area.type = self.old_type

    def save_blend_file( self, context ):
        app = context.scene.cellblender_test_suite
        wm = context.window_manager

        if len(app.path_to_blend) > 0:
            self.path_to_blend = app.path_to_blend
        else:
            self.path_to_blend = os.getcwd() + "/Test.blend"

        bpy.ops.wm.save_as_mainfile(filepath=self.path_to_blend, check_existing=False)


    def get_scene(self):
        return bpy.data.scenes['Scene']

    def delete_all_objects(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=True)

    def reload_cellblender(self, scn):
        print ( "Disabling CellBlender Application" )
        bpy.ops.wm.addon_disable(module='cellblender')

        print ( "Delete MCell RNA properties if needed" )
        # del bpy.types.Scene.mcell
        if scn.get ( 'mcell' ):
            print ( "Deleting MCell RNA properties" )
            del scn['mcell']

        print ( "Enabling CellBlender Application" )
        bpy.ops.wm.addon_enable(module='cellblender')


    def setup_mcell(self, scn):
        mcell = scn.mcell
        app = bpy.context.scene.cellblender_test_suite

        print ( "Initializing CellBlender Application" )
        bpy.ops.mcell.init_cellblender()

        print ( "Setting Preferences" )
        if len(app.path_to_mcell) > 0:
            mcell.cellblender_preferences.mcell_binary = app.path_to_mcell
        else:
            mcell.cellblender_preferences.mcell_binary = os.getcwd() + relative_path_to_mcell

        mcell.cellblender_preferences.mcell_binary_valid = True
        mcell.cellblender_preferences.show_sim_runner_options = True
        #mcell.run_simulation.simulation_run_control = 'QUEUE'
        mcell.run_simulation.simulation_run_control = 'COMMAND'
        
        return mcell

    def setup_cb_defaults ( self, context ):

        self.save_blend_file( context )
        scn = self.get_scene()
        self.set_view_3d()
        self.delete_all_objects()
        self.reload_cellblender(scn)
        mcell = self.setup_mcell(scn)

        print ( "Snapping Cursor to Center" )
        bpy.ops.view3d.snap_cursor_to_center()
        print ( "Done Snapping Cursor to Center" )
        
        self.scn = scn
        self.mcell = mcell

    def create_object_from_mesh ( self, name="ObjectFromMesh", draw_type="WIRE", x=0, y=0, z=0, vertex_list=None, face_list=None ):

        print ( "===> Creating an object from " + str(len(vertex_list)) + " vertices and " + str(len(face_list)) + " faces." )
        vertices = []
        for point in vertex_list:
            vertices.append ( mathutils.Vector((point.x+x,point.y+y,point.z+z)) )
        faces = []
        for face_element in face_list:
            faces.append ( face_element.verts )

        new_mesh = bpy.data.meshes.new ( name + "_mesh" )
        new_mesh.from_pydata ( vertices, [], faces )
        new_mesh.update()
        new_obj = bpy.data.objects.new ( name, new_mesh )

        self.scn.objects.link ( new_obj )
        bpy.ops.object.select_all ( action = "DESELECT" )
        new_obj.select = True
        self.scn.objects.active = new_obj

        # Add the newly added object to the model objects list

        self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        bpy.data.objects[name].draw_type = draw_type
        bpy.ops.object.mode_set ( mode="OBJECT" )
        print ( "Done Adding " + name )


    def add_cube_to_model ( self, name="Cell", draw_type="WIRE", x=0, y=0, z=0, size=1 ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_cube_add ( location=(x,y,z), radius=size)
        self.scn.objects.active.name = name
        bpy.data.objects[name].draw_type = draw_type

        # Add the newly added object to the model objects list

        self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding " + name )


    def add_icosphere_to_model ( self, name="Cell", draw_type="WIRE", x=0, y=0, z=0, size=1, subdiv=2 ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_ico_sphere_add ( subdivisions=subdiv, size=size, location=(x, y, z) )
        self.scn.objects.active.name = name
        bpy.data.objects[name].draw_type = draw_type

        # Add the newly added object to the model objects list

        self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding " + name )


    def add_capsule_to_model ( self, name="Cell", draw_type="WIRE", x=0, y=0, z=0, sigma=0, subdiv=2, radius=1, cyl_len=2, subdivide_sides=True ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """

        capsule = Capsule(subdiv,radius,cyl_len,subdivide_sides)
        
        capsule.dither_points ( sigma, sigma, sigma )

        #print ( "Writing capsule.plf" )
        #capsule.dump_as_plf ( "capsule.plf" )

        self.create_object_from_mesh ( name=name, draw_type=draw_type, x=x, y=y, z=z, vertex_list=capsule.points, face_list=capsule.faces )


    def add_shaped_cylinder_to_model ( self, name="Cell", draw_type="WIRE", x=0, y=0, z=0, sigma=0, numsect=10, z_profile=[ (-2,0.5), (-1.8,0.1), (0,0.1), (0.2,0.5), (2,0.8) ] ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """

        capsule = ShapedCylinder ( numsect, z_profile )
        
        capsule.dither_points ( sigma, sigma, sigma )

        self.create_object_from_mesh ( name=name, draw_type=draw_type, x=x, y=y, z=z, vertex_list=capsule.points, face_list=capsule.faces )



    def add_label_to_model ( self, name="Label", text="Text", x=0, y=0, z=0, size=1, rx=0, ry=0, rz=0 ):
        print ( "Adding " + text )

        bpy.ops.object.text_add ( location=(x,y,z), rotation=(rx,ry,rz), radius=size )
        tobj = bpy.context.active_object
        tobj.data.body = text

        print ( "Done Adding " + text )




    def add_parameter_to_model ( self, name="a", expr="0.0", units="", desc="" ):
        """ Add a parameter to the model """
        print ( "Adding Parameter " + name + " = " + expr )
        ps = self.mcell.parameter_system
        ps.new_parameter ( name, pp=False, new_expr=expr, new_units=units, new_desc=desc )
        print ( "Done Adding Parameter " + name )
        return ps.general_parameter_list[ps.active_par_index]




    def add_molecule_species_to_model ( self, name="A", mol_type="3D", diff_const_expr="0.0", custom_time_step="" ):
        """ Add a molecule species """
        print ( "Adding Molecule Species " + name )
        self.mcell.cellblender_main_panel.molecule_select = True
        bpy.ops.mcell.molecule_add()
        mol_index = self.mcell.molecules.active_mol_index
        self.mcell.molecules.molecule_list[mol_index].name = name
        self.mcell.molecules.molecule_list[mol_index].type = mol_type
        self.mcell.molecules.molecule_list[mol_index].diffusion_constant.set_expr(diff_const_expr)
        self.mcell.molecules.molecule_list[mol_index].custom_time_step.set_expr(custom_time_step)
        print ( "Done Adding Molecule " + name )
        return self.mcell.molecules.molecule_list[mol_index]


    def add_molecule_release_site_to_model ( self, name=None, mol="a", shape="SPHERICAL", obj_expr="", orient="'", q_expr="100", q_type='NUMBER_TO_RELEASE', d="0", x="0", y="0", z="0", pattern=None ):
        """ Add a molecule release site """
        """ shape is one of: 'CUBIC', 'SPHERICAL', 'SPHERICAL_SHELL', 'OBJECT' """
        """ q_type is one of: 'NUMBER_TO_RELEASE', 'GAUSSIAN_RELEASE_NUMBER', 'DENSITY' """
        if name == None:
            name = "rel_" + mol

        print ( "Releasing Molecules at " + name )
        self.mcell.cellblender_main_panel.placement_select = True
        bpy.ops.mcell.release_site_add()
        rel_index = self.mcell.release_sites.active_release_index
        self.mcell.release_sites.mol_release_list[rel_index].name = name
        self.mcell.release_sites.mol_release_list[rel_index].molecule = mol
        self.mcell.release_sites.mol_release_list[rel_index].shape = shape
        self.mcell.release_sites.mol_release_list[rel_index].object_expr = obj_expr
        self.mcell.release_sites.mol_release_list[rel_index].orient = orient
        self.mcell.release_sites.mol_release_list[rel_index].quantity_type = q_type
        self.mcell.release_sites.mol_release_list[rel_index].quantity.set_expr(q_expr)
        self.mcell.release_sites.mol_release_list[rel_index].diameter.set_expr(d)
        self.mcell.release_sites.mol_release_list[rel_index].location_x.set_expr(x)
        self.mcell.release_sites.mol_release_list[rel_index].location_y.set_expr(y)
        self.mcell.release_sites.mol_release_list[rel_index].location_z.set_expr(z)
        if pattern != None:
            self.mcell.release_sites.mol_release_list[rel_index].pattern = pattern
        print ( "Done Releasing Molecule " + name )
        return self.mcell.release_sites.mol_release_list[rel_index]



    def add_release_pattern_to_model ( self, name="time_pattern", delay="0", release_interval="", train_duration="", train_interval="", num_trains="1" ):
        """ Add a release time pattern """
        print ( "Adding a Release Time Pattern " + name + " " + delay + " " + release_interval )
        bpy.ops.mcell.release_pattern_add()
        pat_index = self.mcell.release_patterns.active_release_pattern_index
        self.mcell.release_patterns.release_pattern_list[pat_index].name = name
        self.mcell.release_patterns.release_pattern_list[pat_index].delay.set_expr ( delay )
        self.mcell.release_patterns.release_pattern_list[pat_index].release_interval.set_expr ( release_interval )
        self.mcell.release_patterns.release_pattern_list[pat_index].train_duration.set_expr ( train_duration )
        self.mcell.release_patterns.release_pattern_list[pat_index].train_interval.set_expr ( train_interval )
        self.mcell.release_patterns.release_pattern_list[pat_index].number_of_trains.set_expr ( num_trains )
        print ( "Done Adding Release Time Pattern " + name + " " + delay + " " + release_interval )
        return self.mcell.release_patterns.release_pattern_list[pat_index]



    def add_reaction_to_model ( self, name="", rin="", rtype="irreversible", rout="", fwd_rate="0", bkwd_rate="" ):
        """ Add a reaction """
        print ( "Adding Reaction " + rin + " " + rtype + " " + rout )
        self.mcell.cellblender_main_panel.reaction_select = True
        bpy.ops.mcell.reaction_add()
        rxn_index = self.mcell.reactions.active_rxn_index
        self.mcell.reactions.reaction_list[rxn_index].rxn_name = name
        self.mcell.reactions.reaction_list[rxn_index].reactants = rin
        self.mcell.reactions.reaction_list[rxn_index].products = rout
        self.mcell.reactions.reaction_list[rxn_index].type = rtype
        self.mcell.reactions.reaction_list[rxn_index].fwd_rate.set_expr(fwd_rate)
        self.mcell.reactions.reaction_list[rxn_index].bkwd_rate.set_expr(bkwd_rate)
        print ( "Done Adding Reaction " + rin + " " + rtype + " " + rout )
        return self.mcell.reactions.reaction_list[rxn_index]


    def add_count_output_to_model ( self, name=None, mol_name=None, rxn_name=None, object_name=None, region_name=None, count_location="World" ):
        """ Add a reaction output """
        # count_location may be "World", "Object", or "Region"

        self.mcell.cellblender_main_panel.graph_select = True
        bpy.ops.mcell.rxn_output_add()
        rxn_index = self.mcell.rxn_output.active_rxn_output_index
        rxn = self.mcell.rxn_output.rxn_output_list[rxn_index]

        if (mol_name != None) and (rxn_name == None):
            # This is a Molecule Count Output Definition
            print ( "Adding Count Output for Molecule " + mol_name )
            rxn.rxn_or_mol = "Molecule"
        elif (mol_name == None) and (rxn_name != None):
            # This is a Reaction Count Output Definition
            print ( "Adding Count Output for Reaction " + rxn_name )
            rxn.rxn_or_mol = "Reaction"
        else:
            print ( "Warning: Count output should be either Molecule or Reaction ... returning None." )
            return None


        if name == None:
            rxn.name = ""
        else:
            rxn.name = name

        if mol_name == None:
            rxn.molecule_name = ""
        else:
            rxn.molecule_name = mol_name

        if rxn_name == None:
            rxn.reaction_name = ""
        else:
            rxn.reaction_name = rxn_name

        if object_name == None:
            rxn.object_name = ""
        else:
            rxn.object_name = object_name

        if region_name == None:
            rxn.region_name = ""
        else:
            rxn.region_name = region_name

        rxn.count_location = count_location
        print ( "Done Adding Output Count for Molecule/Reaction" )
        return self.mcell.rxn_output.rxn_output_list[rxn_index]


        """
        All names that aren't listed are defaulted to "".
        All count_locations that don't appear are "World" (same as 0).
        count_location enum meaning
          World = 0
          Object = 1
          Region = 2
        rxn_or_mol enum meaning
          Reaction = 0
          Molecule = 1
          
        
        >>> rxo = C.scene.mcell.rxn_output
        >>> rxl = rxo.rxn_output_list
        >>> ### The following output only shows values that differ from defaults (typical Blender behavior)
        >>> for rxi in rxl:
        ...     print (str(rxi.name))
        ...     for item in rxi.items():
        ...         print ( "  " + str(item) )
        ... 
        Count a in World
          ('name', 'Count a in World')
          ('status', '')
          ('molecule_name', 'a')
          ('reaction_name', '')
          ('object_name', '')
          ('region_name', '')
          ('count_location', 0)
          ('rxn_or_mol', 1)
        Count b in World
          ('name', 'Count b in World')
          ('status', '')
          ('molecule_name', 'b')
          ('reaction_name', '')
          ('object_name', '')
          ('region_name', '')
          ('count_location', 0)
          ('rxn_or_mol', 1)
        Count c in World
          ('name', 'Count c in World')
          ('status', '')
          ('molecule_name', 'c')
          ('reaction_name', '')
          ('object_name', '')
          ('region_name', '')
          ('count_location', 0)
          ('rxn_or_mol', 1)
        Count d in World
          ('name', 'Count d in World')
          ('status', '')
          ('molecule_name', 'd')
          ('reaction_name', '')
          ('object_name', '')
          ('region_name', '')
          ('count_location', 0)
          ('rxn_or_mol', 1)
        Count ab_c in World
          ('name', 'Count ab_c in World')
          ('status', '')
          ('rxn_or_mol', 0)
          ('reaction_name', 'ab_c')
        Count at1_at1 in World
          ('name', 'Count at1_at1 in World')
          ('status', '')
          ('rxn_or_mol', 0)
          ('reaction_name', 'at1_at1')
        Count ct1_ct1 in World
          ('name', 'Count ct1_ct1 in World')
          ('status', '')
          ('rxn_or_mol', 0)
          ('reaction_name', 'ct1_ct1')
        Count t1 in/on Organelle_1[top]
          ('name', 'Count t1 in/on Organelle_1[top]')
          ('status', '')
          ('rxn_or_mol', 1)
          ('reaction_name', 'ct2_dt2')
          ('molecule_name', 't1')
          ('count_location', 2)
          ('object_name', 'Organelle_1')
          ('region_name', 'top')
        Count c in/on Organelle_2
          ('name', 'Count c in/on Organelle_2')
          ('status', '')
          ('molecule_name', 'c')
          ('count_location', 1)
          ('object_name', 'Organelle_2')

        >>> 
        """


        """
        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[0].molecule_name = 't'
        mcell.rxn_output.rxn_output_list[0].count_location = 'Object'
        mcell.rxn_output.rxn_output_list[0].object_name = 'ti'
        """


    def set_partitions ( self, include_partitions=True, auto=False, show=False, xs=None, xe=None, xd=None, ys=None, ye=None, yd=None, zs=None, ze=None, zd=None ):

        self.mcell.partitions.include = include_partitions

        if auto:
            bpy.ops.mcell.auto_generate_boundaries()

        if show:
            bpy.ops.mcell.create_partitions_object()
        else:
            bpy.ops.mcell.remove_partitions_object()
        
        if xs != None: self.mcell.partitions.x_start = xs
        if xe != None: self.mcell.partitions.x_end   = xe
        if xd != None: self.mcell.partitions.x_step  = xd
        
        if ys != None: self.mcell.partitions.y_start = ys
        if ye != None: self.mcell.partitions.y_end   = ye
        if yd != None: self.mcell.partitions.y_step  = yd
        
        if zs != None: self.mcell.partitions.z_start = zs
        if ze != None: self.mcell.partitions.z_end   = ze
        if zd != None: self.mcell.partitions.z_step  = zd


    def set_visualization ( self, enable_visualization=True, export_all=True, all_iterations=True, start=0, end=1, step=1 ):
        """ Setting visualization parameters """
        print ( "Setting visualization parameters" )
        self.mcell.cellblender_main_panel.mol_viz_select = True
        self.mcell.mol_viz.mol_viz_enable = enable_visualization
        self.mcell.viz_output.export_all = export_all
        self.mcell.viz_output.all_iterations = all_iterations
        self.mcell.viz_output.start = start
        self.mcell.viz_output.end = end
        self.mcell.viz_output.step = step
        print ( "Done setting visualization parameters" )
        return self.mcell.viz_output


    def add_surface_class_to_model ( self, surf_class_name ):
        """ Add a surface class """
        print ( "Adding Surface class  " + surf_class_name )
        self.mcell.cellblender_main_panel.surf_classes_select = True
        bpy.ops.mcell.surface_class_add()
        surf_index = self.mcell.surface_classes.active_surf_class_index
        self.mcell.surface_classes.surf_class_list[surf_index].name = surf_class_name
        print ( "Done Adding Surface Class " + surf_class_name )
        return self.mcell.surface_classes.surf_class_list[surf_index]


    def add_property_to_surface_class ( self, mol_name, sc_orient=";", sc_type="REFLECTIVE", sc_clamp_val_str='' ):
        """ Add a property to a surface class """
        print ( "Adding Surface class property " + sc_orient + " " + sc_type + " " + sc_clamp_val_str )
        self.mcell.cellblender_main_panel.surf_classes_select = True
        bpy.ops.mcell.surf_class_props_add()
        surf_index = self.mcell.surface_classes.active_surf_class_index
        prop_index = self.mcell.surface_classes.surf_class_list[surf_index].active_surf_class_props_index
        self.mcell.surface_classes.surf_class_list[surf_index].surf_class_props_list[prop_index].molecule = mol_name
        self.mcell.surface_classes.surf_class_list[surf_index].surf_class_props_list[prop_index].surf_class_orient = sc_orient
        self.mcell.surface_classes.surf_class_list[surf_index].surf_class_props_list[prop_index].surf_class_type = sc_type
        self.mcell.surface_classes.surf_class_list[surf_index].surf_class_props_list[prop_index].clamp_value_str = sc_clamp_val_str
        print ( "Done Adding Surface Class Property " + sc_orient + " " + sc_type + " " + sc_clamp_val_str )
        return self.mcell.surface_classes.surf_class_list[surf_index].surf_class_props_list[prop_index]


    def assign_surface_class_to_region ( self, surf_class_name, obj_name, reg_name="" ):
        """ Assigning a surface class to a Region """
        print ( "Assigning a surface class to Region " + surf_class_name )
        self.mcell.cellblender_main_panel.surf_regions_select = True
        bpy.ops.mcell.mod_surf_regions_add()
        surf_index = self.mcell.mod_surf_regions.active_mod_surf_regions_index
        self.mcell.mod_surf_regions.mod_surf_regions_list[surf_index].surf_class_name = surf_class_name
        self.mcell.mod_surf_regions.mod_surf_regions_list[surf_index].object_name = obj_name
        self.mcell.mod_surf_regions.mod_surf_regions_list[surf_index].region_name = reg_name
        print ( "Done Adding Surface Class to Region " + surf_class_name )
        return self.mcell.mod_surf_regions.mod_surf_regions_list[surf_index]


    def add_surface_region_to_model_by_normal ( self, obj_name, surf_name, nx=0, ny=0, nz=0, min_dot_prod=0.5 ):

        print ("Selected Object = " + str(self.context.object) )
        # bpy.ops.object.mode_set ( mode="EDIT" )

        # Start in Object mode for selecting
        bpy.ops.object.mode_set ( mode="OBJECT" )

        # Face Select Mode:
        msm = self.context.scene.tool_settings.mesh_select_mode[0:3]
        self.context.scene.tool_settings.mesh_select_mode = (False, False, True)

        # Deselect everything
        bpy.ops.object.select_all ( action='DESELECT')
        c = bpy.data.objects[obj_name]
        c.select = False

        # Select just the top faces (normals up)
        mesh = c.data

        bpy.ops.object.mode_set(mode='OBJECT')
        
        for p in mesh.polygons:
          if (nx == 0) and (ny == 0) and (nz == 0):
            # No normal means add all surfaces
            p.select = True
          else:
            n = p.normal
            dp = (n.x * nx) + (n.y * ny) + (n.z * nz)
            if dp > min_dot_prod:
              # This appears to be a triangle in the top face
              #print ( "Normal " + str (n) + " matches with " + str(dp) )
              p.select = True
            else:
              #print ( "Normal " + str (n) + " differs with " + str(dp) )
              p.select = False

        bpy.ops.object.mode_set(mode='EDIT')

        # Add a new region

        bpy.ops.mcell.region_add()
        bpy.data.objects[obj_name].mcell.regions.region_list[0].name = surf_name

        # Assign the currently selected faces to this region
        bpy.ops.mcell.region_faces_assign()

        # Restore the selection settings
        self.context.scene.tool_settings.mesh_select_mode = msm
        bpy.ops.object.mode_set(mode='OBJECT')


    def add_surface_region_to_model_all_faces ( self, obj_name, surf_name ):
        self.add_surface_region_to_model_by_normal ( obj_name, surf_name )


    def all_processes_finished ( self ):
        print ( "Checking if all processes are done..." )
        plist = self.mcell.run_simulation.processes_list
        all_done = False
        if len(plist) <= 0:
            all_done = True
        else:
            all_done = True
            for p in plist:
                # Convert the process list string into a process id
                pid_str = p.name.split(':')[1].split(',')[0].strip()
                print ( "Checking if Process " + pid_str + " is done." )
                if os.path.exists ( "/proc/" + pid_str ):
                    all_done = False
        return all_done


    def wait ( self, wait_time ):
        if self.all_processes_finished():
            print ( "============== ALL DONE ==============" )
        else:
            print ( "============== WAITING ==============" )
        import time
        time.sleep ( wait_time )


    def run_model ( self, iterations="100", time_step="1e-6", export_format="mcell_mdl_unified", wait_time=10.0 ):
        """ export_format is one of: mcell_mdl_unified, mcell_mdl_modular """
        print ( "Running Simulation" )
        self.mcell.cellblender_main_panel.init_select = True
        self.mcell.initialization.iterations.set_expr(iterations)
        self.mcell.initialization.time_step.set_expr(time_step)
        self.mcell.export_project.export_format = export_format

        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            bpy.ops.mcell.run_simulation()
            for i in range(10):
                self.wait ( wait_time / 10.0 )
                print ( "Test Suite is Waiting for MCell to complete ..." )
            print ( "Test Suite is done waiting!!" )
        else:
            bpy.ops.mcell.export_project()


    def refresh_molecules ( self ):
        """ Refresh the display """
        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            bpy.ops.cbm.refresh_operator()


    def change_molecule_display ( self, mol, glyph="Cube", scale=1.0, red=-1, green=-1, blue=-1 ):
        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            #if mol.name == "Molecule":
            #    print ("Name isn't correct")
            #    return
            print ( "Changing Display for Molecule \"" + mol.name + "\" to R="+str(red)+",G="+str(green)+",B="+str(blue) )
            self.mcell.cellblender_main_panel.molecule_select = True
            self.mcell.molecules.show_display = True
            mol.glyph = glyph
            mol.scale = scale
            if red >= 0: mol.color.r = red
            if green >= 0: mol.color.g = green
            if blue >= 0: mol.color.b = blue

            print ( "Done Changing Display for Molecule \"" + mol.name + "\"" )


    def compare_mdl_with_sha1 ( self, good_hash="", test_name=None ):
        """ Compute the sha1 for file_name and compare with sha1 """
        app = bpy.context.scene.cellblender_test_suite
        
        file_name = self.path_to_blend[:self.path_to_blend.rfind('.')] + "_files/mcell/Scene.main.mdl"

        if test_name == None:
            test_name = "Test"

        hashobject = hashlib.sha1()
        if os.path.isfile(file_name):
            hashobject.update(open(file_name, 'rb').read())  # .encode("utf-8"))
            file_hash = str(hashobject.hexdigest())
            print("  SHA1 = " + file_hash + " for \n     " + file_name )

            if len(good_hash) <= 0:

                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%% " + test_name + "   W A R N I N G :  No Hash value provided. Hash from '" + file_name + "' is " + file_hash )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                app.test_status = "F"

            else:

                if file_hash == good_hash:
                    print ( "\n##############################################################################################################" )
                    print ( "##############################################################################################################" )
                    print ( "## " + test_name )
                    print ( "##    O K :  Test Expected " + good_hash + " - confirmed." )
                    print ( "##############################################################################################################" )
                    print ( "##############################################################################################################\n" )
                    app.test_status = "P"

                else:
                    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                    print ( "%% " + test_name + "   E R R O R :  Test Expected " + good_hash + ", but got " + file_hash )
                    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                    print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                    app.test_status = "F"
                    bpy.ops.wm.quit_blender() 

        else:

            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "%% " + test_name + "   E R R O R :  File '%s' does not exist" % file_name )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            app.test_status = "F"
            bpy.ops.wm.quit_blender()


    def scale_view_distance ( self, scale ):
        """ Change the view distance for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_distance *= scale
        #bpy.ops.view3d.zoom(delta=3)
        #set_view_3d()

    def switch_to_perspective ( self ):
        """ Change to perspective for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_perspective = 'PERSP'

    def switch_to_orthographic ( self ):
        """ Change to orthographic for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_perspective = 'ORTHO'

    def play_animation ( self ):
        """ Play the animation """
        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            bpy.ops.screen.animation_play()



######################
#   Model  Support   #
######################

import math
import random

class point:
  x=0;
  y=0;
  z=0;

  def __init__ ( self, x, y, z ):
    self.x = x;
    self.y = y;
    self.z = z;
  
  def equals ( self, p ):
    if ( (self.x == p.x) and (self.y == p.y) and (self.z == p.z) ):
      return ( True );
    else:
      return ( False );

  def equals ( self, p ):
    return (self == p )

  def toString ( self ):
    return ( "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")" );


class face:
  verts = [];
  
  def __init__ ( self, v1, v2, v3 ):
    self.verts = [];
    self.verts.append ( v1 );
    self.verts.append ( v2 );
    self.verts.append ( v3 );
  
  def toString( self ):
    return ( "[" + str(verts[0]) + "," + str(verts[1]) + "," + str(verts[2]) + "]" );


class line:
  p1 = point(0,0,0);
  p2 = point(0,0,0);

  def __init__ ( self, p1, p2 ):
    self.p1 = p1;
    self.p2 = p2;
  
  def toString( self ):
    return ( "["+str(p1.x)+","+str(p1.y)+","+str(p1.z)+"]-["+str(p2.x)+","+str(p2.y)+","+str(p2.z)+"]" );


class plf_object:

  # An object that can hold points, lines, and faces (only points and faces are currently implemented)

  points = []
  faces = []
  
  def __init__ ( self ):
    self.points = []
    self.faces = []
  
  def add_point ( self, p ):
    self.points.append ( p );

  def add_face ( self, f ):
    self.faces.append ( f );

  def offset_points ( self, dx, dy, dz ):
    for p in self.points:
      p.x += dx;
      p.y += dy;
      p.z += dz;

  def scale_points ( self, sx, sy, sz ):
    for p in self.points:
      p.x *= sx;
      p.y *= sy;
      p.z *= sz;

  def dither_points ( self, sigma_x, sigma_y, sigma_z ):
    g = random.gauss
    for p in self.points:
      p.x += g(0,sigma_x);
      p.y += g(0,sigma_y);
      p.z += g(0,sigma_z);

  def sqr ( self, v ):
    return ( v * v );

  def dump_as_plf ( self, file_name=None ):
    if file_name != None:
      out_file = open ( file_name, "w" )

    for p in self.points:
      if file_name == None:
        print ( "P " + str(p.x) + " " + str(p.y) + " " + str(p.z) );
      else:
        out_file.write ( "P " + str(p.x) + " " + str(p.y) + " " + str(p.z) + "\n" );

    for f in self.faces:
      for edge in range(3):
        p1i = f.verts[edge];
        p2i = f.verts[(edge+1)%3];
        if file_name == None:
          print  ( "L " + str(p1i) + " " + str(p2i) );
        else:
          out_file.write  ( "L " + str(p1i) + " " + str(p2i) + "\n" );

    for f in self.faces:
      s = "F"
      for edge in f.verts:
        s += " " + str(edge)
      if file_name == None:
        print ( s )
      else:
        out_file.write ( s + "\n" )

    if file_name != None:
      out_file.close()


  def get_average_edge_length ( self ):
    len_sum = 0;
    num_summed = 0;
    for f in self.faces:
      for edge in range(3):
        p1i = f.verts[edge];
        p2i = f.verts[(edge+1)%3];
        p1 = self.points[p1i];
        p2 = self.points[p2i];
        len_sum += math.sqrt ( self.sqr(p1.x-p2.x) + self.sqr(p1.y-p2.y) + self.sqr(p1.z-p2.z) );
        num_summed += 1;
    # Handle the case where there are faces
    if num_summed == 0: num_summed = 1
    return ( len_sum / num_summed );


  def merge ( self, obj_to_add ):
    # Loop through all faces of the new object to be merged
    for oa_face in obj_to_add.faces:
      # Find point indexes that match in the target object or add them
      new_verts = [ -1, -1, -1 ];
      for new_vert_index in range(3):
        # Loop through all existing points in the target object looking for a match
        looking_for = None
        looking_for = obj_to_add.points[oa_face.verts[new_vert_index]]
        found = -1
        for p in self.points:
          #print ( "  I have: [" + str(p.x) + ","  + str(p.y) + ","  + str(p.z) + "]" )
          if (p.x == looking_for.x) and (p.y == looking_for.y) and (p.z == looking_for.z):
            found = self.points.index(p)
            break
        if found >= 0:
          #print ( "Found a point" )
          new_verts[new_vert_index] = found
        #else:
        #  print ( "Didn't find a point" )
        if (new_verts[new_vert_index] < 0):
          # The point was not found in the target object, so add it
          new_p = point ( looking_for.x, looking_for.y, looking_for.z );
          self.points.append ( new_p );
          new_verts[new_vert_index] = self.points.index(new_p);

        #for p in self.points:
        #  print ( "  I now have: [" + str(p.x) + ","  + str(p.y) + ","  + str(p.z) + "]" )

      new_f = face(new_verts[0], new_verts[1], new_verts[2]);
      self.faces.append ( new_f );

  def remove_point_by_index ( self, index ):
    # Start by removing all faces using this index
    n = len(self.faces)-1
    face_index = n;
    while face_index >= 0:
      f = self.faces[face_index]
      remove = False
      for point_index in range(3):
        if (f.verts[point_index] == index):
          remove = True;
          break;
      if (remove):
        self.faces.pop( face_index );
      face_index += -1

    # Renumber all point indices greater than the index to be removed
    for f in self.faces:
      for point_index in range(3):
        if (f.verts[point_index] > index):
          f.verts[point_index] += -1;

    # Now remove the point itself
    self.points.pop ( index );


  def remove_all_with_z_gt ( self, z ):
    self.remove_all_with_z ( z, True );

  def remove_all_with_z_lt ( self, z ):
    self.remove_all_with_z ( z, False );

  def remove_all_with_z ( self, z, gt ):
    n = len(self.points)-1;
    point_index = n
    while point_index >= 0:
      p = self.points[point_index];
      remove = False;
      if (gt):
        if (p.z > z):
          remove = True;
      else:
        if (p.z < z):
          remove = True;
      if (remove):
        self.remove_point_by_index ( point_index ); # This removes faces as well
      point_index += -1

  def get_all_with_z_at ( self, z, tolerance ):
    result_list = []
    for point_index in range(len(self.points)):
      p = self.points[point_index];
      if ( (p.z >= z-tolerance) and (p.z <= z+tolerance) ):
        result_list.append ( point_index );
    result = None
    if len(result_list) > 0:
      result = []
      for i in range(len(result_list)):
        result.append ( result_list[i] );
    return ( result );



class IcoSphere ( plf_object ):

  # Subclass of plf_object that builds an icosphere with recursion

  def add_normalized_vertex ( self, p ):
    # Normalize the point
    # Add to the list of points if it's not already in the list
    # Return an index to the new or existing point in the list

    l = math.sqrt ( (p.x * p.x) + (p.y * p.y) + (p.z * p.z) );
    pnorm = point ( p.x/l, p.y/l, p.z/l );

    # Check if it's already there
    index = -1;
    for pt in self.points:
      if (pt.x == pnorm.x) and (pt.y == pnorm.y) and (pt.z == pnorm.z):
        index = self.points.index(pt)
        break;

    if (index < 0):
      self.points.append ( pnorm );
      index = self.points.index ( pnorm );
      #print ( "Added vertex at " + str(index) );
    #else:
    #  print ( "Found vertex at " + str(index) );
    return (index);


  def __init__ ( self, recursion_level ):

    self.points = [];

    t = (1.0 + math.sqrt(5.0)) / 2.0;  # Approx 1.618033988749895
    
    # Create 12 verticies from the 3 perpendicular planes whose corners define an icosahedron

    self.add_normalized_vertex ( point (-1,  t,  0) );
    self.add_normalized_vertex ( point ( 1,  t,  0) );
    self.add_normalized_vertex ( point (-1, -t,  0) );
    self.add_normalized_vertex ( point ( 1, -t,  0) );

    self.add_normalized_vertex ( point ( 0, -1,  t) );
    self.add_normalized_vertex ( point ( 0,  1,  t) );
    self.add_normalized_vertex ( point ( 0, -1, -t) );
    self.add_normalized_vertex ( point ( 0,  1, -t) );

    self.add_normalized_vertex ( point ( t,  0, -1) );
    self.add_normalized_vertex ( point ( t,  0,  1) );
    self.add_normalized_vertex ( point (-t,  0, -1) );
    self.add_normalized_vertex ( point (-t,  0,  1) );
    
    
    # Rotate all points such that the resulting icosphere will be separable at the equator
    
    if (True):
      # A PI/6 rotation about z (transform x and y) gives an approximate equator in x-y plane
      angle = (math.pi / 2) - math.atan(1/t);
      print ( "Rotating with angle = " + str(180 * angle / math.pi) );
      for p in self.points:
        newx = (math.cos(angle) * p.x) - (math.sin(angle) * p.z);
        newz = (math.sin(angle) * p.x) + (math.cos(angle) * p.z);
        p.x = newx;
        p.z = newz;

    # Build the original 20 faces for the Icosphere

    self.faces = []

    # Add 5 faces around point 0 (top)
    self.faces.append ( face (  0, 11,  5 ) );    
    self.faces.append ( face (  0,  5,  1 ) );    
    self.faces.append ( face (  0,  1,  7 ) );    
    self.faces.append ( face (  0,  7, 10 ) );    
    self.faces.append ( face (  0, 10, 11 ) );    

    # Add 5 faces adjacent faces
    self.faces.append ( face (  1,  5,  9 ) );    
    self.faces.append ( face (  5, 11,  4 ) );    
    self.faces.append ( face ( 11, 10,  2 ) );    
    self.faces.append ( face ( 10,  7,  6 ) );    
    self.faces.append ( face (  7,  1,  8 ) );    

    # Add 5 faces around point 3 (bottom)
    self.faces.append ( face (  3,  9,  4 ) );    
    self.faces.append ( face (  3,  4,  2 ) );    
    self.faces.append ( face (  3,  2,  6 ) );    
    self.faces.append ( face (  3,  6,  8 ) );    
    self.faces.append ( face (  3,  8,  9 ) );    

    # Add 5 faces adjacent faces
    self.faces.append ( face (  4,  9,  5 ) );    
    self.faces.append ( face (  2,  4, 11 ) );    
    self.faces.append ( face (  6,  2, 10 ) );    
    self.faces.append ( face (  8,  6,  7 ) );    
    self.faces.append ( face (  9,  8,  1 ) );
    

    # Subdivide the faces as requested by the recursion_level argument
    old_points = None;
    old_faces = None;
    
    for rlevel in range(recursion_level):
      # System.out.println ( "\nRecursion Level = " + rlevel );
      # Save the old points and faces and build a new set for this recursion level
      old_points = self.points;
      old_faces = self.faces;
      self.points = []
      self.faces = []
      for f in old_faces:
        # Split this face into 4 more faces
        midpoint = point(0,0,0)
        potential_new_points = []
        for i in range(6):
          potential_new_points.append ( point(0,0,0) )
        for side in range(3):
          p1 = old_points[f.verts[side]];
          p2 = old_points[f.verts[(side+1)%3]];
          midpoint = point ( ((p1.x+p2.x)/2), ((p1.y+p2.y)/2), ((p1.z+p2.z)/2) );
          potential_new_points[2*side] = p1;
          potential_new_points[(2*side)+1] = midpoint;
        # Add the 4 new faces
        # Start with the verticies ... add them all since add_normalized_vertex() will remove duplicates
        vertex_indicies = []
        for i in range(6):
          vertex_indicies.append ( 0 )
        for i in range(6):
          vertex_indicies[i] = self.add_normalized_vertex ( potential_new_points[i] );
        # Now add the 4 new faces
        self.faces.append ( face ( vertex_indicies[0], vertex_indicies[1], vertex_indicies[5] ) );
        self.faces.append ( face ( vertex_indicies[1], vertex_indicies[2], vertex_indicies[3] ) );
        self.faces.append ( face ( vertex_indicies[3], vertex_indicies[4], vertex_indicies[5] ) );
        self.faces.append ( face ( vertex_indicies[1], vertex_indicies[3], vertex_indicies[5] ) );



class Capsule (plf_object):


  def sort_ring_indicies ( self, ring ):
    for i in range(len(ring)):
      for j in range(i+1,len(ring)):
        pi = self.points[ring[i]];
        pj = self.points[ring[j]];
        itheta = math.atan2(pi.x, pi.y);
        jtheta = math.atan2(pj.x, pj.y);
        if (jtheta < itheta):
          temp = ring[i];
          ring[i] = ring[j];
          ring[j] = temp;


  def __init__ ( self, recursion_level, radius, height, subdivide_sides=True ):

    self.points = [];
    self.faces = []

    h = height/2; # h is the height of each half
    tol = 0.0001;

    # Make half of an icosphere for the bottom (start with the whole icosphere and remove the top half)
    ico = IcoSphere ( recursion_level );
    ico.remove_all_with_z_gt ( tol );
    ico.scale_points ( radius, radius, radius )
    ico.offset_points ( 0, 0, -h );
    self.merge ( ico );

    # Make half of an icosphere for the top (start with the whole icosphere and remove the bottom half)
    ico = IcoSphere ( recursion_level );
    ico.remove_all_with_z_lt ( -tol );
    ico.scale_points ( radius, radius, radius )
    ico.offset_points ( 0, 0, h );
    self.merge ( ico );
    
    # Get the bottom and top rings to make the side faces
    bot_ring = self.get_all_with_z_at(-h, tol);
    top_ring = self.get_all_with_z_at(h, tol);

    # Make the sides
    if ((bot_ring==None) or (top_ring==None)):
      print ( "Error: one of the rings is null" );
    elif (len(bot_ring) != len(top_ring)):
      print ( "Error: rings are not the same length" );
    elif (h <= 0):
      print ( "Note: no height to make the cylinder" );
    else:
      self.sort_ring_indicies ( bot_ring );
      self.sort_ring_indicies ( top_ring );
      
      if not subdivide_sides:

        # Create a single face with only two triangles for each face of the cylinder

        n = len(bot_ring)

        # Loop around the circumference of the cylinder
        for i in range(n):

          # Get the corner points of the entire face from top to bottom
          cb1 = self.points[bot_ring[i]];
          ct1 = self.points[top_ring[i]];
          cb2 = self.points[bot_ring[(i+1)%n]];
          ct2 = self.points[top_ring[(i+1)%n]];

          # Make two triangular faces for this full-length rectangle

          new_face = plf_object();
          new_face.add_point ( cb1 );
          new_face.add_point ( ct1 );
          new_face.add_point ( cb2 );
          new_face.add_face ( face (0, 1, 2) );
          self.merge ( new_face );

          new_face = plf_object();
          new_face.add_point ( ct1 );
          new_face.add_point ( ct2 );
          new_face.add_point ( cb2 );
          new_face.add_face ( face (0, 1, 2) );
          self.merge ( new_face );

      else:

        # Segment the cylinder along its length to create roughly square (but triangulated) segments

        avg_len = self.get_average_edge_length();
        num_segs = int(math.floor(((2*h)+(avg_len/2)) / avg_len));
        if (num_segs <= 0):
          num_segs = 1;
        
        # Loop through each ring segment from bottom to top
        for seg_num in range(num_segs):

          n = len(bot_ring)

          # Loop around the circumference of the cylinder
          for i in range(n):

            # Get the corner points of the entire face from top to bottom
            cb1 = self.points[bot_ring[i]];
            ct1 = self.points[top_ring[i]];
            cb2 = self.points[bot_ring[(i+1)%n]];
            ct2 = self.points[top_ring[(i+1)%n]];
            
            # print ( "Corners: " + str(cb1.x) + "," + str(ct1.x) + "," + str(cb2.x) + "," + str(ct2.x) )

            # Start out assuming they fill to all 4 corners
            pb1 = point (cb1.x, cb1.y, cb1.z);
            pt1 = point (ct1.x, ct1.y, ct1.z);
            pb2 = point (cb2.x, cb2.y, cb2.z);
            pt2 = point (ct2.x, ct2.y, ct2.z);

            if (seg_num > 0):
              # Need to interpolate the bottom because it's no longer the bottom ring
              pb1.x = cb1.x + ((ct1.x-cb1.x)*(seg_num * 1.0 / num_segs));
              pb1.y = cb1.y + ((ct1.y-cb1.y)*(seg_num * 1.0 / num_segs));
              pb1.z = cb1.z + ((ct1.z-cb1.z)*(seg_num * 1.0 / num_segs));

              pb2.x = cb2.x + ((ct2.x-cb2.x)*(seg_num * 1.0 / num_segs));
              pb2.y = cb2.y + ((ct2.y-cb2.y)*(seg_num * 1.0 / num_segs));
              pb2.z = cb2.z + ((ct2.z-cb2.z)*(seg_num * 1.0 / num_segs));

            if (seg_num < (num_segs-1)):
              # Need to interpolate the top because it's not the top ring
              pt1.x = cb1.x + ((ct1.x-cb1.x)*((seg_num+1) * 1.0 / num_segs));
              pt1.y = cb1.y + ((ct1.y-cb1.y)*((seg_num+1) * 1.0 / num_segs));
              pt1.z = cb1.z + ((ct1.z-cb1.z)*((seg_num+1) * 1.0 / num_segs));

              pt2.x = cb2.x + ((ct2.x-cb2.x)*((seg_num+1) * 1.0 / num_segs));
              pt2.y = cb2.y + ((ct2.y-cb2.y)*((seg_num+1) * 1.0 / num_segs));
              pt2.z = cb2.z + ((ct2.z-cb2.z)*((seg_num+1) * 1.0 / num_segs));

            # Make the two triangular faces for this rectangle

            new_face = plf_object();
            new_face.add_point ( pb1 );
            new_face.add_point ( pt1 );
            new_face.add_point ( pb2 );
            new_face.add_face ( face (0, 1, 2) );
            self.merge ( new_face );

            new_face = plf_object();
            new_face.add_point ( pt1 );
            new_face.add_point ( pt2 );
            new_face.add_point ( pb2 );
            new_face.add_face ( face (0, 1, 2) );
            self.merge ( new_face );




class ShapedCylinder (plf_object):

  def sort_ring_indicies ( self, ring ):
    for i in range(len(ring)):
      for j in range(i+1,len(ring)):
        pi = self.points[ring[i]];
        pj = self.points[ring[j]];
        itheta = math.atan2(pi.x, pi.y);
        jtheta = math.atan2(pj.x, pj.y);
        if (jtheta < itheta):
          temp = ring[i];
          ring[i] = ring[j];
          ring[j] = temp;


  def __init__ ( self, num_sectors, z_profile ):
    """ z_profile is a sorted list of tuples where each tuple is (z,r), and the list is sorted with increasing z """

    self.points = [];
    self.faces = [];
    
    # Make the sides

    if ( len(z_profile) < 2 ):

      print ( "Error: z-profile must contain at least 2 entries (bottom and top)" );

    else:

      # Build the cylinder from bottom to top creating faces along the way

      # Loop through each ring segment from bottom to top (start with lowest ring as "upper")
      lower_z = -1
      lower_r = -1
      lower_ring = []
      upper_ring = []

      for seg_num in range(len(z_profile)):

        # Prepare to build a new upper ring
        upper_z = z_profile[seg_num][0]
        upper_r = z_profile[seg_num][1]

        # Loop around the circumference of the cylinder building a new upper ring
        if upper_r > 0:
          for i in range(num_sectors):
            theta = i * 2 * math.pi / num_sectors
            new_point = point ( upper_r*math.cos(theta), upper_r*math.sin(theta), upper_z )
            self.points = self.points + [ new_point ]
            upper_ring = upper_ring + [ new_point ]
        elif upper_r == 0:
          new_point = point ( 0.0, 0.0, upper_z )
          self.points = self.points + [ new_point ]
          for i in range(num_sectors):
            upper_ring = upper_ring + [ new_point ]


        if seg_num > 0:
        
          # Both the upper and lower rings exist and are valid, so build the faces

          for i in range(num_sectors):

            # Make the faces for this rectangle / triangle

            pb1 = lower_ring[i];
            pt1 = upper_ring[i];
            pb2 = lower_ring[(i+1)%num_sectors];
            pt2 = upper_ring[(i+1)%num_sectors];

            if (lower_r >= 0) and (upper_r > 0):

              # We have either a triangle or a rectangle. Make this face.

              new_face = plf_object();
              new_face.add_point ( pt1 );
              new_face.add_point ( pt2 );
              new_face.add_point ( pb2 );
              new_face.add_face ( face (0, 2, 1) );
              self.merge ( new_face );

            if (upper_r >= 0) and (lower_r > 0):

              # We have either a triangle or a rectangle. Make this face.

              new_face = plf_object();
              new_face.add_point ( pb1 );
              new_face.add_point ( pt1 );
              new_face.add_point ( pb2 );
              new_face.add_face ( face (0, 2, 1) );
              self.merge ( new_face );
              
        # Move the upper ring down to the lower ring
        lower_z = upper_z
        lower_r = upper_r
        lower_ring = upper_ring
        upper_ring = []



######################
#  Individual Tests  #
######################


###########################################################################################################
##   This is an example model used for all the SimRunner tests.

def SimRunnerExample ( context, method="COMMAND", test_name=None ):

    cb_model = CellBlender_Model ( context )

    scn = cb_model.get_scene()
    mcell = cb_model.get_mcell()
    mcell.run_simulation.simulation_run_control = method

    mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

    cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="200" )

    cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

    cb_model.compare_mdl_with_sha1 ( "a3409b4891f9d5a9be8010afb3923f0a14d5ec4a", test_name=test_name )

    cb_model.refresh_molecules()

    cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )

    cb_model.set_view_back()

    cb_model.scale_view_distance ( 0.1 )

    cb_model.play_animation()



###########################################################################################################
group_name = "Sim Runner Tests"
test_name = "Simulation Runner Command Test"
operator_name = "cellblender_test.sim_runner_command"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SimRunnerCommandTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="COMMAND", test_name="Simulation Runner Command Test" )
        return { 'FINISHED' }



###########################################################################################################
group_name = "Sim Runner Tests"
test_name = "Simulation Runner Queue Test"
operator_name = "cellblender_test.sim_runner_queue"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SimRunnerQueueTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="QUEUE", test_name="Simulation Runner Queue Test" )
        return { 'FINISHED' }



###########################################################################################################
group_name = "Sim Runner Tests"
test_name = "Simulation Runner Java Test"
operator_name = "cellblender_test.sim_runner_java"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SimRunnerJavaTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="JAVA", test_name="Simulation Runner Java Test" )
        return { 'FINISHED' }



###########################################################################################################
group_name = "Sim Runner Tests"
test_name = "Simulation Runner Open GL Test"
operator_name = "cellblender_test.sim_runner_opengl"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SimRunnerOpenGLTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="OPENGL", test_name="Simulation Runner Open GL Test" )
        return { 'FINISHED' }



###########################################################################################################
group_name = "Non-Geometry Tests"
test_name = "Single Molecule Test"
operator_name = "cellblender_test.single_mol"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SingleMoleculeTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="1" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=2.0 )
        
        cb_model.compare_mdl_with_sha1 ( "19fd01beddf82da6026810b52d6955638674f556", test_name="Single Molecule Test" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Torus', scale=4.0, red=1.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.02 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Non-Geometry Tests"
test_name = "Double Sphere Test"
operator_name = "cellblender_test.double_sphere"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class DoubleSphereTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="400", d="0.5", y="-0.25" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="400", d="0.5", y="0.25" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=2.0 )

        cb_model.compare_mdl_with_sha1 ( "4410b18c1530f79c07cc2aebec52a7eabc4aded4", test_name="Double Sphere Test" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Non-Geometry Tests"
test_name = "Volume Diffusion Constant Test"
operator_name = "cellblender_test.vol_diffusion_const"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class VolDiffusionConstTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-7" )
        mol_c = cb_model.add_molecule_species_to_model ( name="c", diff_const_expr="1e-8" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="100", d="0.01", y="-0.25" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="100", d="0.01", y= "0.0" )
        cb_model.add_molecule_release_site_to_model ( mol="c", q_expr="100", d="0.01", y= "0.25" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=3.0 )

        cb_model.compare_mdl_with_sha1 ( "59b7e9f0f672791101d6a0061af362688e8caa42", test_name="Volume Diffusion Constant Test" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_c, glyph='Cube', scale=2.0, red=0.1, green=0.1, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )
        cb_model.switch_to_orthographic()

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Non-Geometry Tests"
test_name = "Simple Reaction Test"
operator_name = "cellblender_test.reaction"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class ReactionTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )
        mol_c = cb_model.add_molecule_species_to_model ( name="bg", diff_const_expr="1e-5" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="400", d="0.5", y="-0.05" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="400", d="0.5", y="0.05" )

        # Create a single c molecule at the origin so its properties will be changed
        cb_model.add_molecule_release_site_to_model ( mol="bg", q_expr="1", d="0", y="0" )

        cb_model.add_reaction_to_model ( rin="a + b", rtype="irreversible", rout="bg", fwd_rate="1e8", bkwd_rate="" )

        cb_model.run_model ( iterations='2000', time_step='1e-6', wait_time=20.0 )

        cb_model.compare_mdl_with_sha1 ( "e302a61ecda563a02e8d65ef17c648ff088745d2", test_name="Simple Reaction Test" )

        cb_model.refresh_molecules()

        # Try to advance frame so molecules exist before changing them
        # scn.frame_current = 1999

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_c, glyph='Torus', scale=10.0, red=1.0, green=1.0, blue=0.5 )

        #cb_model.refresh_molecules()

        # Set time back to 0
        #scn.frame_current = 0

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Non-Geometry Tests"
test_name = "Release Shape Test"
operator_name = "cellblender_test.release_shape"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class ReleaseShapeTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )

        diff_const = "1e-6"

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr=diff_const )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr=diff_const )
        mol_c = cb_model.add_molecule_species_to_model ( name="bg", diff_const_expr=diff_const )
        mol_d = cb_model.add_molecule_species_to_model ( name="d", diff_const_expr=diff_const )

        num_rel = "1000"

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr=num_rel, shape="OBJECT", obj_expr="Cell",  )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr=num_rel, shape="SPHERICAL",       d="1.5", y="1" )
        cb_model.add_molecule_release_site_to_model ( mol="bg", q_expr=num_rel, shape="CUBIC",           d="1.5", y="-1" )
        cb_model.add_molecule_release_site_to_model ( mol="d", q_expr=num_rel, shape="SPHERICAL_SHELL", d="1.5", z="1" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=5.0 )

        cb_model.compare_mdl_with_sha1 ( "c622d3e5c9eaf20911b95ae006eb197401d0e982", test_name="Release Shape Test" )

        cb_model.refresh_molecules()

        mol_scale = 2.5

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=mol_scale, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=mol_scale, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_c, glyph='Cube', scale=mol_scale, red=0.0, green=0.0, blue=1.0 )
        cb_model.change_molecule_display ( mol_d, glyph='Cube', scale=mol_scale, red=1.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Non-Geometry Tests"
test_name = "Parameter System Test"
operator_name = "cellblender_test.par_system"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class ParSystemTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_parameter_to_model ( name="A", expr="1.23", units="A units", desc="" )
        cb_model.add_parameter_to_model ( name="B", expr="A * 2", units="B units", desc="" )
        cb_model.add_parameter_to_model ( name="C", expr="A * B", units="", desc="A * B" )
        cb_model.add_parameter_to_model ( name="dc", expr="1e-8", units="", desc="Diffusion Constant" )

        mol = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="dc" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="C" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=4.0 )

        cb_model.compare_mdl_with_sha1 ( "f7a25eacc4b0ecfa6619c9428ddd761920aab7dd", test_name="Parameter System Test" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Torus', scale=4.0, red=1.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.04 )

        cb_model.play_animation()

        return { 'FINISHED' }





###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Simple Cube Test"
operator_name = "cellblender_test.cube_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class CubeTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )

        mol = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=2.0 )

        cb_model.compare_mdl_with_sha1 ( "c32241a2f97ace100f1af7a711a6a970c6b9a135", test_name="Simple Cube Test" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Cube', scale=4.0, red=1.0, green=0.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }


###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Cube Surface Test"
operator_name = "cellblender_test.cube_surf_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class CubeSurfaceTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "top", 0, 0, 1, 0.8 )

        mola = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mols = cb_model.add_molecule_species_to_model ( name="s", mol_type="2D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( mol="s", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="1000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="1", shape="SPHERICAL", d="0", z="1.001" )


        cb_model.add_reaction_to_model ( rin="a' + s,", rtype="irreversible", rout="b, + s,", fwd_rate="1e8", bkwd_rate="" )


        cb_model.run_model ( iterations='500', time_step='1e-6', wait_time=6.0 )

        cb_model.compare_mdl_with_sha1 ( "32312790f206beaa798ce0a7218f1f712840b0d5", test_name="Cube Surface Test" )

        cb_model.refresh_molecules()
        
        scn.frame_current = 1

        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Sphere Surface Test"
operator_name = "cellblender_test.sphere_surf_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SphereSurfaceTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_icosphere_to_model ( name="Cell", draw_type="WIRE" )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "top", 0, 0, 1, 0.8 )

        mola = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mols = cb_model.add_molecule_species_to_model ( name="s", mol_type="2D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( mol="s", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="1000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="1", shape="SPHERICAL", d="0", z="1.001" )


        cb_model.add_reaction_to_model ( rin="a' + s,", rtype="irreversible", rout="b, + s,", fwd_rate="1e8", bkwd_rate="" )


        cb_model.run_model ( iterations='500', time_step='1e-6', wait_time=7.0 )

        cb_model.compare_mdl_with_sha1 ( "90ef79fc7405aff0bbf9a6f6864f11b148c622a4", test_name="Sphere Surface Test" )

        cb_model.refresh_molecules()
        
        scn.frame_current = 1

        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }




###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Overlapping Surface Test"
operator_name = "cellblender_test.overlapping_surf_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class OverlappingSurfaceTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_icosphere_to_model ( name="Cell", draw_type="WIRE", subdiv=4 )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "top", 0, 0, 1, 0.0 )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "y",   0, 1, 0, 0.0 )

        mola  = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-5" )
        mols1 = cb_model.add_molecule_species_to_model ( name="s1", mol_type="2D", diff_const_expr="0" )
        mols2 = cb_model.add_molecule_species_to_model ( name="s2", mol_type="2D", diff_const_expr="0" )
        molb1 = cb_model.add_molecule_species_to_model ( name="b1", diff_const_expr="1e-7" )
        molb2 = cb_model.add_molecule_species_to_model ( name="b2", diff_const_expr="1e-7" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="2000" )
        cb_model.add_molecule_release_site_to_model ( mol="s1", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="2000" )
        cb_model.add_molecule_release_site_to_model ( mol="s2", shape="OBJECT", obj_expr="Cell[y]", orient="'", q_expr="2000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b1", q_expr="1", shape="SPHERICAL", d="0", z="0" )
        cb_model.add_molecule_release_site_to_model ( mol="b2", q_expr="1", shape="SPHERICAL", d="0", z="0" )


        cb_model.add_reaction_to_model ( rin="a' + s1,", rtype="irreversible", rout="a' + b1, + s1,", fwd_rate="1e10", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="a' + s2,", rtype="irreversible", rout="a' + b2, + s2,", fwd_rate="1e10", bkwd_rate="" )


        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=5.0 )

        cb_model.compare_mdl_with_sha1 ( "3f0d87d4f5e1ab1ecedde6c0d48fa3d2dc89ab93", test_name="Overlapping Surface Test" )

        cb_model.refresh_molecules()

        scn.frame_current = 1

        """
        cb_model.change_molecule_display ( mola, glyph='Cube',  scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols1, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mols2, glyph='Cone', scale=3.0, red=1.0, green=0.0, blue=1.0 )
        cb_model.change_molecule_display ( molb1, glyph='Cube', scale=4.0, red=1.0, green=1.0, blue=1.0 )
        """

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Surface Classes Test"
operator_name = "cellblender_test.surface_classes_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SurfaceClassesTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.switch_to_orthographic()

        cb_model.add_cube_to_model ( name="ti", draw_type="WIRE", x=0, y=0, z=0, size=0.5 )
        cb_model.add_surface_region_to_model_all_faces ( "ti", "t_reg" )
        cb_model.add_cube_to_model ( name="to", draw_type="WIRE", x=0, y=0, z=0, size=1.0 )

        cb_model.add_cube_to_model ( name="ri", draw_type="WIRE", x=0, y=-3, z=0, size=0.5 )
        cb_model.add_surface_region_to_model_all_faces ( "ri", "r_reg" )
        cb_model.add_cube_to_model ( name="ro", draw_type="WIRE", x=0, y=-3, z=0, size=1.0 )

        cb_model.add_cube_to_model ( name="ai", draw_type="WIRE", x=0, y=3, z=0, size=0.5 )
        cb_model.add_surface_region_to_model_all_faces ( "ai", "a_reg" )
        cb_model.add_cube_to_model ( name="ao", draw_type="WIRE", x=0, y=3, z=0, size=1.0 )

        cb_model.add_cube_to_model ( name="ci", draw_type="WIRE", x=0, y=0, z=3, size=0.5 )
        cb_model.add_surface_region_to_model_all_faces ( "ci", "c_reg" )
        cb_model.add_cube_to_model ( name="co", draw_type="WIRE", x=0, y=0, z=3, size=1.0 )

        cb_model.add_label_to_model ( name="t", text="Trans",   x=0, y=-1.13, z=-2,  size=1, rx=math.pi/2, ry=0, rz=math.pi/2 )
        cb_model.add_label_to_model ( name="c", text="Clamp",   x=0, y=-1.26, z=4.4, size=1, rx=math.pi/2, ry=0, rz=math.pi/2 )
        cb_model.add_label_to_model ( name="r", text="Reflect", x=0, y=-4.38, z=-2,  size=1, rx=math.pi/2, ry=0, rz=math.pi/2 )
        cb_model.add_label_to_model ( name="a", text="Absorb",  x=0, y=1.82,  z=-2,  size=1, rx=math.pi/2, ry=0, rz=math.pi/2 )

        mola = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        molt = cb_model.add_molecule_species_to_model ( name="t", diff_const_expr="1e-6" )
        molr = cb_model.add_molecule_species_to_model ( name="r", diff_const_expr="1e-6" )
        molc = cb_model.add_molecule_species_to_model ( name="c", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="ai", q_expr="100" )
        cb_model.add_molecule_release_site_to_model ( mol="t", shape="OBJECT", obj_expr="ti", q_expr="100" )
        cb_model.add_molecule_release_site_to_model ( mol="r", shape="OBJECT", obj_expr="ri", q_expr="100" )
        cb_model.add_molecule_release_site_to_model ( mol="c", shape="OBJECT", obj_expr="ci", q_expr="100" )

        cb_model.add_surface_class_to_model ( "trans_to_t" )
        cb_model.add_property_to_surface_class ( "t", sc_orient=";", sc_type="TRANSPARENT" )

        cb_model.add_surface_class_to_model ( "reflect_to_r" )
        cb_model.add_property_to_surface_class ( "r", sc_orient=";", sc_type="REFLECTIVE" )

        cb_model.add_surface_class_to_model ( "absorb_to_a" )
        cb_model.add_property_to_surface_class ( "a", sc_orient=";", sc_type="ABSORPTIVE" )

        cb_model.add_surface_class_to_model ( "clamp_to_c" )
        cb_model.add_property_to_surface_class ( "c", sc_orient=";", sc_type="CLAMP_CONCENTRATION",  sc_clamp_val_str="1.5e-7" )


        cb_model.assign_surface_class_to_region ( "trans_to_t", "ti", "t_reg" )
        cb_model.assign_surface_class_to_region ( "reflect_to_r", "ri", "r_reg" )
        cb_model.assign_surface_class_to_region ( "absorb_to_a", "ai", "a_reg" )
        cb_model.assign_surface_class_to_region ( "clamp_to_c", "ci", "c_reg" )


        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[0].molecule_name = 't'
        mcell.rxn_output.rxn_output_list[0].count_location = 'Object'
        mcell.rxn_output.rxn_output_list[0].object_name = 'ti'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[1].molecule_name = 'r'
        mcell.rxn_output.rxn_output_list[1].count_location = 'Object'
        mcell.rxn_output.rxn_output_list[1].object_name = 'ri'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[2].molecule_name = 'a'
        mcell.rxn_output.rxn_output_list[2].count_location = 'Object'
        mcell.rxn_output.rxn_output_list[2].object_name = 'ai'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[3].molecule_name = 'c'
        mcell.rxn_output.rxn_output_list[3].count_location = 'Object'
        mcell.rxn_output.rxn_output_list[3].object_name = 'ci'

        mcell.rxn_output.plot_layout = ' '
        mcell.rxn_output.mol_colors = True


        cb_model.run_model ( iterations='5000', time_step='1e-6', wait_time=40.0 )

        cb_model.compare_mdl_with_sha1 ( "b781cd49d7b9499b87570a4ca920134b701657c5", test_name="Surface Classes Test" )

        cb_model.refresh_molecules()

        scn.frame_current = 1

        cb_model.change_molecule_display ( mola, glyph='Cube', scale=5.0, red=0.0, green=0.7, blue=1.0 )
        cb_model.change_molecule_display ( molt, glyph='Cube', scale=5.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molr, glyph='Cube', scale=5.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( molc, glyph='Cube', scale=5.0, red=1.0, green=1.0, blue=0.5 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.5 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Capsule in Capsule Test"
operator_name = "cellblender_test.capsule_tests"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class CapsuleTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        # Create the capsule object, and define the surface as a membrane

        cb_model.add_capsule_to_model ( name="shell",   draw_type="WIRE", x=0, y=0, z=0, sigma=0, subdiv=2, radius=0.501, cyl_len=4.002, subdivide_sides=False )
        cb_model.add_capsule_to_model ( name="capsule", draw_type="WIRE", x=0, y=0, z=0, sigma=0, subdiv=2, radius=0.500, cyl_len=4,     subdivide_sides=False )
        cb_model.add_surface_region_to_model_by_normal ( "capsule", "top", nx=0, ny=0, nz=1, min_dot_prod=0.5 )
        cb_model.add_surface_region_to_model_by_normal ( "capsule", "bot", nx=0, ny=0, nz=-1, min_dot_prod=0.5 )


        mola  = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        molpa = cb_model.add_molecule_species_to_model ( name="pa", mol_type="2D", diff_const_expr="0" )
        molb  = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-5" )
        molpb = cb_model.add_molecule_species_to_model ( name="pb", mol_type="2D", diff_const_expr="0" )
        molc  = cb_model.add_molecule_species_to_model ( name="c", diff_const_expr="1e-7" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="capsule", q_expr="2000" )
        cb_model.add_molecule_release_site_to_model ( mol="pa", shape="OBJECT", obj_expr="capsule[top]", orient="'", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( mol="pb", shape="OBJECT", obj_expr="capsule[bot]", orient="'", q_expr="1000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="1", shape="SPHERICAL", d="0", z="0.000" )
        cb_model.add_molecule_release_site_to_model ( mol="c", q_expr="1", shape="SPHERICAL", d="0", z="0.000" )


        cb_model.add_reaction_to_model ( rin="a' + pa,", rtype="irreversible", rout="b, + pa,", fwd_rate="1e9", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="b, + pb,", rtype="irreversible", rout="c' + pb,", fwd_rate="1e9", bkwd_rate="" )

        cb_model.add_count_output_to_model ( mol_name="a" )
        cb_model.add_count_output_to_model ( mol_name="b" )
        cb_model.add_count_output_to_model ( mol_name="c", object_name="capsule", count_location="Object" )

        cb_model.set_visualization ( enable_visualization=True, export_all=True, all_iterations=False, start=0, end=100000, step=2 )

        mcell.rxn_output.plot_layout = ' '
        mcell.rxn_output.mol_colors = True

        mcell.partitions.include = True
        bpy.ops.mcell.auto_generate_boundaries()

        cb_model.run_model ( iterations='10000', time_step='1e-6', wait_time=50.0 )

        cb_model.compare_mdl_with_sha1 ( "3aaca27e86f45a29de7c121bef1a08029ef8ca37", test_name="Capsule in Capsule Test" )

        cb_model.refresh_molecules()
        
        scn.frame_current = 1

        cb_model.refresh_molecules()
        
        """
        This seems to crash Blender, so leave molecules with default settings for now

        cb_model.change_molecule_display ( mola,  glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( molpa, glyph='Cone', scale=2.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molb,  glyph='Cube', scale=3.0, red=1.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molpb, glyph='Cone', scale=2.0, red=0.0, green=1.0, blue=1.0 )
        cb_model.change_molecule_display ( molc,  glyph='Cube', scale=4.0, red=1.0, green=1.0, blue=1.0 )
        """

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }




###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Goblet Test"
operator_name = "cellblender_test.goblet_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class GobletTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        # Create the capsule object, and define the surface as a membrane
        
        # Create a goblet
        thk = 0.02
        goblet = [ (-2,0.8), (-1.8,0.1), (0,0.1), (0.2,0.5), (2,0.8),
                   (2,0.8-thk), (0.2,0.5-thk), (0,0.1-thk), (-1.8,0.1-thk), (-2,0.8-thk), (-2,0.8) ]

        cb_model.add_shaped_cylinder_to_model ( name="goblet", draw_type="WIRE", x=0, y=0, z=0, sigma=0, numsect=10, z_profile=goblet )

        mola  = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="goblet", q_expr="1000" )

        cb_model.set_visualization ( enable_visualization=True, export_all=True, all_iterations=False, start=0, end=100000, step=1 )

        cb_model.run_model ( iterations='1000', time_step='1e-6', wait_time=10.0 )

        cb_model.compare_mdl_with_sha1 ( "", test_name="Goblet Test" )

        cb_model.refresh_molecules()
        
        scn.frame_current = 1

        cb_model.refresh_molecules()

        cb_model.set_view_back()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Simple Geometry Tests"
test_name = "Dividing ecoli Test"
operator_name = "cellblender_test.ecoli_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class EcoliTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        # Create the capsule object, and define the surface as a membrane
        
        # Create a dividing ecoli
        ecoli = [ (-2,0), (-1.5,0.5), (-1,0.5), (-0.5,0.5), (0,0.5), (0.5,0.5), (1,0.5), (1.5,0.5), (2,0)]

        cb_model.add_shaped_cylinder_to_model ( name="capsule", draw_type="WIRE", x=0, y=0, z=0, sigma=0, numsect=10, z_profile=ecoli )

        cb_model.set_view_back()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Counting Tests"
test_name = "Simple Molecule Count Test"
operator_name = "cellblender_test.simple_molecule_count_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class SimpleMoleculeCountTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
    
        print ( str(test_groups) )

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="500", d="0.5" )
        cb_model.add_reaction_to_model ( name="Decay", rin="a",  rtype="irreversible", rout="NULL", fwd_rate="1e5", bkwd_rate="" )

        cb_model.add_count_output_to_model ( mol_name="a", rxn_name=None, object_name=None, region_name=None, count_location="World" )
        cb_model.add_count_output_to_model ( mol_name=None, rxn_name="Decay", object_name=None, region_name=None, count_location="World" )


        cb_model.run_model ( iterations='100', time_step='1e-6', wait_time=3.0 )

        cb_model.compare_mdl_with_sha1 ( "d24da83d3b07bb1f3be2e571fa29f99c054d6478", test_name="Simple Molecule Count Test" )

        cb_model.refresh_molecules()
        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.set_view_back()
        cb_model.scale_view_distance ( 0.1 )

        cb_model.play_animation()

        return { 'FINISHED' }




###########################################################################################################
group_name = "Counting Tests"
test_name = "Release Time Patterns Test"
operator_name = "cellblender_test.rel_time_patterns_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class ReleaseTimePatternsTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        diff_const = "0"

        mol_a =  cb_model.add_molecule_species_to_model ( name="a",  diff_const_expr=diff_const )
        mol_b =  cb_model.add_molecule_species_to_model ( name="b",  diff_const_expr=diff_const )
        mol_bg = cb_model.add_molecule_species_to_model ( name="bg", diff_const_expr="0" )


        decay_rate = "8e6"
        cb_model.add_reaction_to_model ( rin="a",  rtype="irreversible", rout="NULL", fwd_rate=decay_rate, bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="b",  rtype="irreversible", rout="NULL", fwd_rate=decay_rate+"/5", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="bg", rtype="irreversible", rout="NULL", fwd_rate=decay_rate+"/500", bkwd_rate="" )


        dt = "1e-6"
        cb_model.add_release_pattern_to_model ( name="spike_pattern", delay="300 * " + dt, release_interval="10 * " + dt, train_duration="100 * " + dt, train_interval="200 * " + dt, num_trains="5" )
        cb_model.add_release_pattern_to_model ( name="background", delay="0", release_interval="100 * " + dt, train_duration="1e20", train_interval="2e20", num_trains="1" )


        num_rel = "10"

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr=num_rel, shape="SPHERICAL", d="0.1", z="0.2", pattern="spike_pattern" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr=num_rel, shape="SPHERICAL", d="0.1", z="0.4", pattern="spike_pattern" )
        cb_model.add_molecule_release_site_to_model ( mol="bg", q_expr="1",    shape="SPHERICAL", d="1.0", z="0.0", pattern="background" )

        #### Add a single a molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="a",  name="a_dummy",  q_expr="1", shape="SPHERICAL" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b",  name="b_dummy",  q_expr="1", shape="SPHERICAL" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="bg", name="bg_dummy", q_expr="1", shape="SPHERICAL" )


        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[0].molecule_name = 'a'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[1].molecule_name = 'b'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[2].molecule_name = 'bg'


        cb_model.run_model ( iterations='1500', time_step=dt, wait_time=10.0 )

        cb_model.compare_mdl_with_sha1 ( "ec68e0720b43755c4f193d65ebaaa55eb2c2cfae", test_name="Release Time Patterns Test" )

        cb_model.refresh_molecules()

        mol_scale = 1.0

        cb_model.change_molecule_display ( mol_a,  glyph='Cube',  scale=mol_scale, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b,  glyph='Cube',  scale=mol_scale, red=0.5, green=0.5, blue=1.0 )
        cb_model.change_molecule_display ( mol_bg, glyph='Torus', scale=mol_scale, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.05 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
##   Main Function supporting Lotka Volterra models

def LotkaVolterraTorus ( context, prey_birth_rate, predation_rate, pred_death_rate, interaction_radius, time_step, iterations, mdl_hash, test_name, wait_time ):

    cb_model = CellBlender_Model ( context )

    scn = cb_model.get_scene()
    mcell = cb_model.get_mcell()

    # Create the Torus
    bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=10,major_radius=0.1,minor_radius=0.03)
    scn.objects.active.name = 'arena'

    # Set up the material for the Torus
    if len(bpy.data.materials) <= 0:
        new_mat = bpy.data.materials.new("cell")
    bpy.data.materials[0].name = 'cell'
    bpy.data.materials['cell'].use_transparency = True
    bpy.data.materials['cell'].alpha = 0.3

    # Assign the material to the Torus
    bpy.ops.object.material_slot_add()
    scn.objects['arena'].material_slots[0].material = bpy.data.materials['cell']
    scn.objects['arena'].show_transparent = True

    # Add the new Torus to the model objects list
    mcell.cellblender_main_panel.objects_select = True
    bpy.ops.mcell.model_objects_add()

    # Add the molecules
    prey = cb_model.add_molecule_species_to_model ( name="prey", diff_const_expr="6e-6" )
    pred = cb_model.add_molecule_species_to_model ( name="predator", diff_const_expr="6e-6" )

    cb_model.add_molecule_release_site_to_model ( name="prey_rel", mol="prey", shape="OBJECT", obj_expr="arena", q_expr="1000" )
    cb_model.add_molecule_release_site_to_model ( name="pred_rel", mol="predator", shape="OBJECT", obj_expr="arena", q_expr="1000" )

    cb_model.add_reaction_to_model ( rin="prey", rtype="irreversible", rout="prey + prey", fwd_rate=prey_birth_rate, bkwd_rate="" )
    cb_model.add_reaction_to_model ( rin="prey + predator", rtype="irreversible", rout="predator + predator", fwd_rate=predation_rate, bkwd_rate="" )
    cb_model.add_reaction_to_model ( rin="predator", rtype="irreversible", rout="NULL", fwd_rate=pred_death_rate, bkwd_rate="" )

    bpy.ops.mcell.rxn_output_add()
    mcell.rxn_output.rxn_output_list[0].molecule_name = 'prey'

    bpy.ops.mcell.rxn_output_add()
    mcell.rxn_output.rxn_output_list[1].molecule_name = 'predator'

    mcell.rxn_output.plot_layout = ' '

    mcell.partitions.include = True
    bpy.ops.mcell.auto_generate_boundaries()

    if interaction_radius == None:
        mcell.initialization.interaction_radius.set_expr ( "" )
    else:
        mcell.initialization.interaction_radius.set_expr ( interaction_radius )

    # mcell.run_simulation.simulation_run_control = 'JAVA'
    cb_model.run_model ( iterations=iterations, time_step=time_step, wait_time=wait_time )

    cb_model.compare_mdl_with_sha1 ( mdl_hash, test_name=test_name )

    cb_model.refresh_molecules()

    scn.frame_current = 10

    cb_model.set_view_back()

    mcell.rxn_output.mol_colors = True

    cb_model.change_molecule_display ( prey, glyph='Cube',       scale=0.2, red=0.0, green=1.0, blue=0.0 )
    cb_model.change_molecule_display ( pred, glyph='Octahedron', scale=0.3, red=1.0, green=0.0, blue=0.0 )

    cb_model.scale_view_distance ( 0.015 )

    return cb_model



###########################################################################################################
group_name = "Complete Model Tests"
test_name = "Lotka Volterra Torus - Diffusion Limited Reaction"
operator_name = "cellblender_test.lotka_volterra_torus_test_diff_lim"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class LotkaVolterraTorusTestDiffLimOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = LotkaVolterraTorus ( context, prey_birth_rate="8.6e6", predation_rate="1e12", pred_death_rate="5e6", interaction_radius="0.003", time_step="1e-8", iterations="1200", mdl_hash="be2169e601b5148c9d2da24143aae99367bf7f39", test_name="Lotka Volterra Torus - Diffusion Limited Reaction", wait_time=15.0 )
        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Complete Model Tests"
test_name = "Lotka Volterra Torus - Physiologic Reaction"
operator_name = "cellblender_test.lotka_volterra_torus_test_phys"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class LotkaVolterraTorusTestPhysOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = LotkaVolterraTorus ( context, prey_birth_rate="129e3", predation_rate="1e8", pred_death_rate="130e3", interaction_radius=None, time_step="1e-6", iterations="1200", mdl_hash="bd1033a5ec4f6c51c017da4640d5bce7df5cdbd8", test_name="Lotka Volterra Torus - Physiologic Reaction", wait_time=60.0 )
        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################
group_name = "Complete Model Tests"
test_name = "Organelle Test"
operator_name = "cellblender_test.organelle_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class OrganelleTestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()


        # Set some shared parameters
        subdiv = 3


        # Create Organelle 1

        # Create the object and add it to the CellBlender model
        cb_model.add_icosphere_to_model ( name="Organelle_1", draw_type="WIRE", size=0.3, y=-0.25, subdiv=subdiv+1 )
        cb_model.add_surface_region_to_model_by_normal ( "Organelle_1", "top", 0, 1, 0, 0.92 )


        # Create Organelle 2

        # Create the object and add it to the CellBlender model
        cb_model.add_icosphere_to_model ( name="Organelle_2", draw_type="WIRE", size=0.2, y=0.31, subdiv=subdiv+1 )
        cb_model.add_surface_region_to_model_by_normal ( "Organelle_2", "top", 0, -1, 0, 0.8 )


        # Create Cell itself

        cb_model.add_icosphere_to_model ( name="Cell", draw_type="WIRE", size=0.625, subdiv=subdiv )


        # Define the molecule species

        mola = cb_model.add_molecule_species_to_model ( name="a", mol_type="3D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", mol_type="3D", diff_const_expr="1e-6" )
        molc = cb_model.add_molecule_species_to_model ( name="c", mol_type="3D", diff_const_expr="1e-6" )
        mold = cb_model.add_molecule_species_to_model ( name="d", mol_type="3D", diff_const_expr="1e-6" )

        molt1 = cb_model.add_molecule_species_to_model ( name="t1", mol_type="2D", diff_const_expr="1e-6" )
        molt2 = cb_model.add_molecule_species_to_model ( name="t2", mol_type="2D", diff_const_expr="0" )



        cb_model.add_molecule_release_site_to_model ( name="rel_a",  mol="a",  shape="OBJECT", obj_expr="Cell[ALL] - (Organelle_1[ALL] + Organelle_2[ALL])", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( name="rel_b",  mol="b",  shape="OBJECT", obj_expr="Organelle_1[ALL]", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( name="rel_t1", mol="t1", shape="OBJECT", obj_expr="Organelle_1[top]", orient="'", q_expr="700" )
        cb_model.add_molecule_release_site_to_model ( name="rel_t2", mol="t2", shape="OBJECT", obj_expr="Organelle_2[top]", orient="'", q_expr="700" )
        # Add a single c and d molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="c", shape="OBJECT", obj_expr="Organelle_2", q_expr="1" )
        cb_model.add_molecule_release_site_to_model ( mol="d", shape="OBJECT", obj_expr="Organelle_2", q_expr="1" )


        cb_model.add_reaction_to_model ( rin="a + b",    rtype="irreversible", rout="c",        fwd_rate="1e9", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="a' + t1'", rtype="irreversible", rout="a, + t1'", fwd_rate="3e8", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="c' + t2'", rtype="irreversible", rout="d, + t2'", fwd_rate="3e9", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="c, + t1'", rtype="irreversible", rout="c' + t1'", fwd_rate="3e8", bkwd_rate="" )

        cb_model.add_count_output_to_model ( mol_name="a" )
        cb_model.add_count_output_to_model ( mol_name="b" )
        cb_model.add_count_output_to_model ( mol_name="c" )
        cb_model.add_count_output_to_model ( mol_name="d" )

        #cb_model.add_count_output_to_model ( mol_name="t1" )
        #cb_model.add_count_output_to_model ( mol_name="t2" )

        mcell.rxn_output.plot_layout = ' '
        mcell.rxn_output.mol_colors = True


        mcell.partitions.include = True
        bpy.ops.mcell.auto_generate_boundaries()


        cb_model.run_model ( iterations='1000', time_step='1e-6', wait_time=25.0 )

        cb_model.compare_mdl_with_sha1 ( "ecd81fc1c5b65777866da16f286b4eb70e362620", test_name="Organelle Test" )

        cb_model.refresh_molecules()

        scn.frame_current = 2

        # For some reason, changing some of these molecule display settings crashes Blender (tested for both 2.74 and 2.75)
        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        #cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )
        #cb_model.change_molecule_display ( molc, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        #cb_model.change_molecule_display ( molt1, glyph='Cone', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( molt2, glyph='Cone', scale=1.5, red=0.7, green=0.7, blue=0.0 )


        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.07 )

        cb_model.play_animation()

        return { 'FINISHED' }



###########################################################################################################

# Capsule is 1 BU in diameter (0.5 in radius) and has a total height of 4 (-2 to +2)
group_name = "Complete Model Tests"
test_name = "E. coli MinD/MinE System"
operator_name = "cellblender_test.mind_mine_test"
next_test_group_num = register_test ( test_groups, group_name, test_name, operator_name, next_test_group_num )

class MinDMinETestOp(bpy.types.Operator):
    bl_idname = operator_name
    bl_label = test_name

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()


        # Define the parameters to be used later

        cb_model.add_parameter_to_model ( name="k1", expr="1", units="s-1", desc="k1" )
        cb_model.add_parameter_to_model ( name="k2", expr="3.8e3", units="M-1s-1", desc="k2" )
        cb_model.add_parameter_to_model ( name="k3", expr="9e5", units="M-1s-1", desc="k3" )
        cb_model.add_parameter_to_model ( name="k4", expr="5.6e7", units="M-1s-1", desc="k4" )
        cb_model.add_parameter_to_model ( name="k5", expr="0.7", units="s-1", desc="k5" )
        cb_model.add_parameter_to_model ( name="dte", expr="2e-6", units="", desc="dte" )
        cb_model.add_parameter_to_model ( name="dt", expr="100*dte", units="", desc="dt" )


        # Create the capsule object, and define the surface as a membrane

        cb_model.add_capsule_to_model ( name="ecoli", draw_type="WIRE", x=0, y=0, z=0, sigma=0, subdiv=2, radius=0.5, cyl_len=3 )
        cb_model.add_surface_region_to_model_all_faces ( "ecoli", "membrane" )


        # Create a surface class and assign it to the membrane

        cb_model.add_surface_class_to_model ( "surf" )
        cb_model.assign_surface_class_to_region ( "surf", "ecoli", "membrane" )


        # Define the molecule species

        mind_adp = cb_model.add_molecule_species_to_model ( name="mind_adp", mol_type="3D", diff_const_expr="2.5e-8" )
        mind_atp = cb_model.add_molecule_species_to_model ( name="mind_atp", mol_type="3D", diff_const_expr="2.5e-8" )
        mine     = cb_model.add_molecule_species_to_model ( name="mine",     mol_type="3D", diff_const_expr="2.5e-8", custom_time_step="dte" )
        mind_m   = cb_model.add_molecule_species_to_model ( name="mind_m",   mol_type="2D", diff_const_expr="0" )
        minde_m  = cb_model.add_molecule_species_to_model ( name="minde_m",  mol_type="2D", diff_const_expr="0" )


        # Define the release sites

        cb_model.add_molecule_release_site_to_model ( name="mind_rel",  mol="mind_adp",  shape="OBJECT", obj_expr="ecoli", q_expr="4320" )
        cb_model.add_molecule_release_site_to_model ( name="mine_rel",  mol="mine",      shape="OBJECT", obj_expr="ecoli", q_expr="1080" )


        # Define the reactions

        cb_model.add_reaction_to_model ( rin="mind_adp",             rtype="irreversible", rout="mind_atp",           fwd_rate="k1", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="mind_atp, @ surf'",    rtype="irreversible", rout="mind_m,",            fwd_rate="k2", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="mind_atp, + mind_m,",  rtype="irreversible", rout="mind_m, + mind_m,",  fwd_rate="k3", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="mind_atp, + minde_m,", rtype="irreversible", rout="mind_m, + minde_m,", fwd_rate="k3", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="mine, + mind_m,",      rtype="irreversible", rout="minde_m,",           fwd_rate="k4", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="minde_m,",             rtype="irreversible", rout="mind_adp, + mine,",  fwd_rate="k5", bkwd_rate="" )

        # Specify the output

        cb_model.add_count_output_to_model ( mol_name="mind_adp" )
        cb_model.add_count_output_to_model ( mol_name="mind_atp" )
        cb_model.add_count_output_to_model ( mol_name="mind_m" )
        cb_model.add_count_output_to_model ( mol_name="minde_m" )
        cb_model.add_count_output_to_model ( mol_name="mine" )

        # Set a few special parameters
        mcell.initialization.time_step_max.set_expr('100*dt')
        mcell.initialization.interaction_radius.set_expr('1e-5')
        mcell.initialization.vacancy_search_distance.set_expr('0.08')
        mcell.initialization.surface_grid_density.set_expr('4000')
        mcell.initialization.surface_grid_density.set_expr('4000')
        mcell.initialization.accurate_3d_reactions = False

        # Setup the partitions

        cb_model.set_partitions ( xs=-0.5, xe=0.5, xd=0.02, ys=-0.5, ye=0.5, yd=0.02, zs=-2.0, ze=2.0, zd=0.2 )

        # Setup the visualization

        cb_model.set_visualization ( enable_visualization=True, export_all=True, all_iterations=False, start=0, end=6000000, step=1000 )

        cb_model.run_model ( iterations='0.5 * 200/dt', time_step='dt', wait_time=5.0 )  # Can use to generate MDL, but SHA1 won't be right: export_format="mcell_mdl_modular", 

        cb_model.compare_mdl_with_sha1 ( "cd346130b01966382fd2b6829235e25f13f3dddb", test_name="E. coli MinD/MinE System" )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        return { 'FINISHED' }



#############################################################
################## End of Individual Tests ##################
#############################################################



from bpy.app.handlers import persistent

def add_handler ( handler_list, handler_function ):
    """ Only add a handler if it's not already in the list """
    if not (handler_function in handler_list):
        handler_list.append ( handler_function )
        
        #cellblender_added_handlers


def remove_handler ( handler_list, handler_function ):
    """ Only remove a handler if it's in the list """
    if handler_function in handler_list:
        handler_list.remove ( handler_function )


# Load scene callback
@persistent
def scene_loaded(dummy):
    bpy.context.scene.cellblender_test_suite.make_real()


def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.cellblender_test_suite = bpy.props.PointerProperty(type=CellBlenderTestPropertyGroup)
    # Add the scene update pre handler
    add_handler ( bpy.app.handlers.scene_update_pre, scene_loaded )


def unregister():
    print ("Unregistering ", __name__)
    remove_handler ( bpy.app.handlers.scene_update_pre, scene_loaded )
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.cellblender_test_suite

if __name__ == "__main__":
    register()


# test call
#bpy.ops.modtst.dialog_operator('INVOKE_DEFAULT')


