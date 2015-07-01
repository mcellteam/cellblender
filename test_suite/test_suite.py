# From within Blender: import cellblender.test_suite.test_suite
if __name__ == "__main__":
  # Simple method to "install" a new version with "python test_suite/test_suite.py" assuming "test_suite" directory exists in target location.
  import os
  print ( "MAIN with __file__ = " + __file__ )
  install_to = "2.74"
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
    path_to_mcell = bpy.props.StringProperty(name="PathToMCell", default="/home/bobkuczewski/proj/MCell/mcell_git/src/linux/mcell")
    path_to_blend = bpy.props.StringProperty(name="PathToBlend", default="/home/bobkuczewski/proj/MCell/tutorials/intro/2015_06_26")

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
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join ( app.path_to_blend, "SimpleCube.blend"), check_existing=False)

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

    def get_path_to_mcell(self):
        app = bpy.context.scene.cellblender_test_suite
        return app.path_to_mcell
        
    def setup_mcell(self, scn):
        mcell = scn.mcell

        print ( "Initializing CellBlender Application" )
        bpy.ops.mcell.init_cellblender()

        print ( "Setting Preferences" )
        mcell.cellblender_preferences.mcell_binary = self.get_path_to_mcell()
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


    def add_molecule_release_site_to_model ( self, name=None, mol="a", shape="SPHERICAL", obj_expr="", orient="'", q_expr="100", q_type='NUMBER_TO_RELEASE', d="0", x="0", y="0", z="0" ):
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
        cb_model.add_molecule_release_site_to_model ( mol="b", shape="OBJECT", obj_expr="Cell", q_expr="1" )

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


