relative_path_to_mcell = "/../mcell_git/src/linux/mcell"
install_to = "2.74"


# From within Blender: import cellblender.test_suite.test_suite
if __name__ == "__main__":
  # Simple method to "install" a new version with "python test_suite/test_suite.py" assuming "test_suite" directory exists in target location.
  import os
  print ( "MAIN with __file__ = " + __file__ )
  print ( " Installing into Blender " + install_to )
  os.system ( "cp ./" + __file__ + " ~/.config/blender/" + install_to + "/scripts/addons/cellblender/" + __file__ )
  print ( "Copied files" )
  exit(0)


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

import os
import bpy
from bpy.props import *

class CellBlenderTestPropertyGroup(bpy.types.PropertyGroup):
    path_to_mcell = bpy.props.StringProperty(name="PathToMCell", default="")
    path_to_blend = bpy.props.StringProperty(name="PathToBlend", default="")

class CellBlenderTestSuitePanel(bpy.types.Panel):
    bl_label = "CellBlender Test Suite"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    def draw(self, context):
        app = context.scene.cellblender_test_suite
        row = self.layout.row()
        row.prop(app, "path_to_mcell")
        row = self.layout.row()
        row.prop(app, "path_to_blend")

        row = self.layout.row()
        row.operator ( "cellblender_test.new_file" )

        row = self.layout.row()
        row.operator ( "cellblender_test.single_mol" )
        row = self.layout.row()
        row.operator ( "cellblender_test.double_sphere" )
        row = self.layout.row()
        row.operator ( "cellblender_test.reaction" )
        row = self.layout.row()
        row.operator ( "cellblender_test.release_shape" )
        row = self.layout.row()
        row.operator ( "cellblender_test.cube_test" )
        row = self.layout.row()
        row.operator ( "cellblender_test.cube_surf_test" )
        row = self.layout.row()
        row.operator ( "cellblender_test.rel_time_patterns_test" )
        row = self.layout.row()
        row.operator ( "cellblender_test.lotka_volterra_torus_test_diff_lim" )
        row = self.layout.row()
        row.operator ( "cellblender_test.lotka_volterra_torus_test_phys" )



class NewFileOp(bpy.types.Operator):
    bl_idname = "cellblender_test.new_file"
    bl_label = "Reset"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        bpy.ops.wm.read_homefile()
        return { 'FINISHED' }




class CellBlender_Model:

    old_type = None
    context = None
    scn = None
    mcell = None
    
    def __init__(self, cb_context):
        # bpy.ops.wm.read_homefile()
        self.old_type = None
        self.context = cb_context
        self.setup_cb_defaults ( self.context )
        
    def get_scene(self):
        return self.scn
        
    def get_mcell(self):
        return self.mcell


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
            bpy.ops.wm.save_as_mainfile(filepath=app.path_to_blend, check_existing=False)
        else:
            bpy.ops.wm.save_as_mainfile(filepath=os.getcwd() + "/Test.blend", check_existing=False)


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

    def add_cube_to_model ( self, name="Cell", draw_type="WIRE" ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_cube_add()
        self.scn.objects.active.name = name
        bpy.data.objects['Cell'].draw_type = draw_type

        # Add the newly added object to the model objects list

        self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding " + name )


    def add_molecule_species_to_model ( self, name="A", mol_type="3D", diff_const_expr="0.0" ):
        """ Add a molecule species """
        print ( "Adding Molecule Species " + name )
        self.mcell.cellblender_main_panel.molecule_select = True
        bpy.ops.mcell.molecule_add()
        mol_index = self.mcell.molecules.active_mol_index
        self.mcell.molecules.molecule_list[mol_index].name = name
        self.mcell.molecules.molecule_list[mol_index].type = mol_type
        self.mcell.molecules.molecule_list[mol_index].diffusion_constant.set_expr(diff_const_expr)
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


    def add_reaction_to_model ( self, name="", rin="", rtype="irreversible", rout="", fwd_rate="0", bkwd_rate="" ):
        """ Add a reaction """
        print ( "Adding Reaction " + rin + " " + rtype + " " + rout )
        self.mcell.cellblender_main_panel.reaction_select = True
        bpy.ops.mcell.reaction_add()
        rxn_index = self.mcell.reactions.active_rxn_index
        self.mcell.reactions.reaction_list[rxn_index].reactants = rin
        self.mcell.reactions.reaction_list[rxn_index].products = rout
        self.mcell.reactions.reaction_list[rxn_index].type = rtype
        self.mcell.reactions.reaction_list[rxn_index].fwd_rate.set_expr(fwd_rate)
        self.mcell.reactions.reaction_list[rxn_index].bkwd_rate.set_expr(bkwd_rate)
        print ( "Done Adding Reaction " + rin + " " + rtype + " " + rout )
        return self.mcell.reactions.reaction_list[rxn_index]


    def wait ( self, wait_time ):
        import time
        time.sleep ( wait_time )


    def run_model ( self, iterations="100", time_step="1e-6", export_format="mcell_mdl_unified", wait_time=10.0 ):
        """ export_format is one of: mcell_mdl_unified, mcell_mdl_modular """
        print ( "Running Simulation" )
        self.mcell.cellblender_main_panel.init_select = True
        self.mcell.initialization.iterations.set_expr(iterations)
        self.mcell.initialization.time_step.set_expr(time_step)
        self.mcell.export_project.export_format = export_format
        bpy.ops.mcell.run_simulation()
        self.wait ( wait_time )


    def refresh_molecules ( self ):
        """ Refresh the display """
        bpy.ops.cbm.refresh_operator()


    def change_molecule_display ( self, mol, glyph="Cube", scale=1.0, red=-1, green=-1, blue=-1 ):
        print ( "Changing Display for Molecule " + mol.name )
        self.mcell.cellblender_main_panel.molecule_select = True
        self.mcell.molecules.show_display = True
        mol.glyph = glyph
        mol.scale = scale
        if red >= 0: mol.color.r = red
        if green >= 0: mol.color.g = green
        if blue >= 0: mol.color.b = blue

        print ( "Done Changing Display for Molecule a" )


    def scale_view_distance ( self, scale ):
        """ Change the view distance for all 3D_VIEW windows """
        for area in bpy.context.screen.areas:
          if area.spaces[0].type == 'VIEW_3D':
            area.spaces[0].region_3d.view_distance *= scale

        #bpy.ops.view3d.zoom(delta=3)
        #set_view_3d()


    def play_animation ( self ):
        """ Play the animation """
        bpy.ops.screen.animation_play()




######################
#  Individual Tests  #
######################


class SingleMoleculeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.single_mol"
    bl_label = "Single Molecule Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="1" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Torus', scale=4.0, red=1.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.02 )

        cb_model.play_animation()

        return { 'FINISHED' }



class DoubleSphereTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.double_sphere"
    bl_label = "Double Sphere Test"

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

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )

        cb_model.play_animation()

        return { 'FINISHED' }



class ReactionTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.reaction"
    bl_label = "Simple Reaction Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )
        mol_c = cb_model.add_molecule_species_to_model ( name="c", diff_const_expr="1e-5" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="400", d="0.5", y="-0.05" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="400", d="0.5", y="0.05" )

        # Create a single c molecule at the origin so its properties will be changed
        cb_model.add_molecule_release_site_to_model ( mol="c", q_expr="1", d="0", y="0" )

        cb_model.add_reaction_to_model ( rin="a + b", rtype="irreversible", rout="c", fwd_rate="1e8", bkwd_rate="" )

        cb_model.run_model ( iterations='2000', time_step='1e-6', wait_time=5.0 )

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


class ReleaseShapeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.release_shape"
    bl_label = "Release Shape Test"

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
        mol_c = cb_model.add_molecule_species_to_model ( name="c", diff_const_expr=diff_const )
        mol_d = cb_model.add_molecule_species_to_model ( name="d", diff_const_expr=diff_const )

        num_rel = "1000"

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr=num_rel, shape="OBJECT", obj_expr="Cell",  )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr=num_rel, shape="SPHERICAL",       d="1.5", y="1" )
        cb_model.add_molecule_release_site_to_model ( mol="c", q_expr=num_rel, shape="CUBIC",           d="1.5", y="-1" )
        cb_model.add_molecule_release_site_to_model ( mol="d", q_expr=num_rel, shape="SPHERICAL_SHELL", d="1.5", z="1" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

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



class CubeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.cube_test"
    bl_label = "Simple Cube Test"

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

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Cube', scale=4.0, red=1.0, green=0.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



class CubeSurfaceTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.cube_surf_test"
    bl_label = "Cube Surface Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )
        

        print ("Selected Object = " + str(context.object) )
        # bpy.ops.object.mode_set ( mode="EDIT" )

        # Start in Object mode for selecting
        bpy.ops.object.mode_set ( mode="OBJECT" )

        # Face Select Mode:
        msm = context.scene.tool_settings.mesh_select_mode[0:3]
        context.scene.tool_settings.mesh_select_mode = (False, False, True)

        # Deselect everything
        bpy.ops.object.select_all ( action='DESELECT')
        c = bpy.data.objects['Cell']
        c.select = False
        
        # Select just the top faces (normals up)
        mesh = c.data

        bpy.ops.object.mode_set(mode='OBJECT')

        for p in mesh.polygons:
          n = p.normal
          if (n.z > n.x) and (n.z > n.y):
            # This appears to be a triangle in the top face
            print ( "Normal Up = " + str (n) )
            p.select = True
          else:
            print ( "Normal Down = " + str (n) )
            p.select = False

        bpy.ops.object.mode_set(mode='EDIT')
        
        # Add a new region
        
        bpy.ops.mcell.region_add()
        bpy.data.objects['Cell'].mcell.regions.region_list[0].name = 'top'
        
        # Assign the currently selected faces to this region
        bpy.ops.mcell.region_faces_assign()

        # Restore the selection settings
        context.scene.tool_settings.mesh_select_mode = msm
        bpy.ops.object.mode_set(mode='OBJECT')


        mola = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mols = cb_model.add_molecule_species_to_model ( name="s", mol_type="2D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( mol="s", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="1000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="1", shape="SPHERICAL", d="0", z="1.001" )


        cb_model.add_reaction_to_model ( rin="a' + s,", rtype="irreversible", rout="b, + s,", fwd_rate="1e8", bkwd_rate="" )


        cb_model.run_model ( iterations='500', time_step='1e-6', wait_time=5.0 )

        cb_model.refresh_molecules()
        
        scn.frame_current = 450

        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



class ReleaseTimePatternsTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.rel_time_patterns_test"
    bl_label = "Release Time Patterns Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        diff_const = "0"

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr=diff_const )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr=diff_const )


        decay_rate = "8e6"
        cb_model.add_reaction_to_model ( rin="a", rtype="irreversible", rout="NULL", fwd_rate=decay_rate, bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="b", rtype="irreversible", rout="NULL", fwd_rate=decay_rate+"/5", bkwd_rate="" )


        dt = "1e-6"

        bpy.ops.mcell.release_pattern_add()
        mcell.release_patterns.release_pattern_list[0].name = "spike_pattern"
        mcell.release_patterns.release_pattern_list[0].delay.set_expr ( "200 * " + dt )
        mcell.release_patterns.release_pattern_list[0].release_interval.set_expr ( "10 * " + dt )
        mcell.release_patterns.release_pattern_list[0].train_duration.set_expr ( "100 * " + dt )
        mcell.release_patterns.release_pattern_list[0].train_interval.set_expr ( "200 * " + dt )
        mcell.release_patterns.release_pattern_list[0].number_of_trains.set_expr ( "5" )


        num_rel = "10"

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr=num_rel, shape="SPHERICAL", d="0.1", z="0.2", pattern="spike_pattern" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr=num_rel, shape="SPHERICAL", d="0.1", z="0.4", pattern="spike_pattern" )

        #### Add a single a molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="a", name="a_dummy", q_expr="1", shape="SPHERICAL" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", name="b_dummy", q_expr="1", shape="SPHERICAL" )


        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[0].molecule_name = 'a'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[1].molecule_name = 'b'


        cb_model.run_model ( iterations='1500', time_step=dt, wait_time=7.0 )

        cb_model.refresh_molecules()

        mol_scale = 1

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=mol_scale, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=mol_scale, red=0.5, green=0.5, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.05 )

        cb_model.play_animation()

        return { 'FINISHED' }



def LotkaVolterraTorus ( context, prey_birth_rate, predation_rate, pred_death_rate, interaction_radius, time_step, iterations, wait_time ):

    cb_model = CellBlender_Model ( context )

    scn = cb_model.get_scene()
    mcell = cb_model.get_mcell()

    # Create the Torus
    bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=10,major_radius=0.1,minor_radius=0.03)
    scn.objects.active.name = 'arena'

    # Set up the material for the Torus
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

    cb_model.refresh_molecules()

    scn.frame_current = 10

    cb_model.set_view_back()

    mcell.rxn_output.mol_colors = True

    cb_model.change_molecule_display ( prey, glyph='Cube',       scale=0.2, red=0.0, green=1.0, blue=0.0 )
    cb_model.change_molecule_display ( pred, glyph='Octahedron', scale=0.3, red=1.0, green=0.0, blue=0.0 )

    cb_model.scale_view_distance ( 0.015 )

    return cb_model


class LotkaVolterraTorusTestDiffLimOp(bpy.types.Operator):
    bl_idname = "cellblender_test.lotka_volterra_torus_test_diff_lim"
    bl_label = "Lotka Volterra Torus - Diffusion Limited Reaction"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = LotkaVolterraTorus ( context, prey_birth_rate="8.6e6", predation_rate="1e12", pred_death_rate="5e6", interaction_radius="0.003", time_step="1e-8", iterations="1200", wait_time=10.0 )
        cb_model.play_animation()

        return { 'FINISHED' }


class LotkaVolterraTorusTestPhysOp(bpy.types.Operator):
    bl_idname = "cellblender_test.lotka_volterra_torus_test_phys"
    bl_label = "Lotka Volterra Torus - Physiologic Reaction"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = LotkaVolterraTorus ( context, prey_birth_rate="129e3", predation_rate="1e8", pred_death_rate="130e3", interaction_radius=None, time_step="1e-6", iterations="1200", wait_time=50.0 )
        cb_model.play_animation()

        return { 'FINISHED' }





def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.cellblender_test_suite = bpy.props.PointerProperty(type=CellBlenderTestPropertyGroup)

def unregister():
    print ("Unregistering ", __name__)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.cellblender_test_suite

if __name__ == "__main__":
    register()


# test call
#bpy.ops.modtst.dialog_operator('INVOKE_DEFAULT')


