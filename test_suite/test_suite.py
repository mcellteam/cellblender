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
        row.operator ( "cellblender_test.cube_test" )



old_type = None

def set_view_3d():
  global old_type
  area = bpy.context.area
  old_type = area.type
  area.type = 'VIEW_3D'
  
def set_view_back():
  global old_type
  area = bpy.context.area
  area.type = old_type




######################
#  Individual Tests  #
######################


class CubeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.cube_test"
    bl_label = "Simple Cube Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        self.report({'INFO'}, "Running Tests")
        app = context.scene.cellblender_test_suite
        wm = context.window_manager
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join ( app.path_to_blend, "SimpleCube.blend"), check_existing=False)

        print ( "Test Suite's invoke called on " + str(self) )
        print ( "       self is a " + str(type(self)) )

        scn = bpy.data.scenes['Scene']


        print ( "Changing the Area Type to VIEW_3D" )
        set_view_3d()
        print ( "Done Changing the Area Type to VIEW_3D" )


        print ( "Select and Delete All Objects" )
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=True)
        print ( "Done Deleting All Objects" )


        print ( "Disabling CellBlender Application" )
        bpy.ops.wm.addon_disable(module='cellblender')

        print ( "Delete MCell RNA properties if needed" )
        # del bpy.types.Scene.mcell
        if scn.get ( 'mcell' ):
          print ( "Deleting MCell RNA properties" )
          del scn['mcell']




        print ( "Enabling CellBlender Application" )
        bpy.ops.wm.addon_enable(module='cellblender')

        mcell = scn.mcell


        print ( "Initializing CellBlender Application" )
        bpy.ops.mcell.init_cellblender()




        print ( "Setting Preferences" )
        mcell.cellblender_preferences.mcell_binary = app.path_to_mcell
        mcell.cellblender_preferences.mcell_binary_valid = True
        mcell.cellblender_preferences.show_sim_runner_options = True
        mcell.run_simulation.simulation_run_control = 'COMMAND'


        print ( "Snapping Cursor to Center" )
        bpy.ops.view3d.snap_cursor_to_center()
        print ( "Done Snapping Cursor to Center" )

        print ( "Adding Cell" )
        bpy.ops.mesh.primitive_cube_add()
        scn.objects.active.name = 'Cell'
        bpy.data.objects['Cell'].draw_type = 'WIRE'
        print ( "Done Adding Cell" )

        print ( "Adding Cell to Model Objects" )
        mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding Cell to Model Objects" )

        print ( "Adding Molecule a" )
        mcell.cellblender_main_panel.molecule_select = True
        bpy.ops.mcell.molecule_add()
        mcell.molecules.molecule_list[0].name = 'a'
        mcell.molecules.molecule_list[0].diffusion_constant.set_expr('1e-6')
        print ( "Done Adding Molecule a" )

        print ( "Releasing Molecule a" )
        mcell.cellblender_main_panel.placement_select = True
        bpy.ops.mcell.release_site_add()
        mcell.release_sites.mol_release_list[0].name = 'rel_a'
        mcell.release_sites.mol_release_list[0].molecule = 'a'
        mcell.release_sites.mol_release_list[0].shape = 'OBJECT'
        mcell.release_sites.mol_release_list[0].object_expr = 'Cell'
        mcell.release_sites.mol_release_list[0].quantity.set_expr('1000')
        print ( "Done Releasing Molecule a" )

        print ( "Running Simulation" )
        mcell.cellblender_main_panel.init_select = True
        mcell.initialization.iterations.set_expr('200')
        mcell.export_project.export_format = 'mcell_mdl_unified'
        bpy.ops.mcell.run_simulation()

        print ( "Sleep while Simulation Runs ..." )

        import time
        time.sleep ( 4 )

        print ( "Done Running Simulation" )

        bpy.ops.cbm.refresh_operator()

        print ( "Changing Display for Molecule a" )
        mcell.cellblender_main_panel.molecule_select = True
        mcell.molecules.show_display = True
        mcell.molecules.molecule_list[0].glyph = 'Cube'
        mcell.molecules.molecule_list[0].scale = 4.0
        mcell.molecules.molecule_list[0].color.r = 1.0
        mcell.molecules.molecule_list[0].color.g = 0.0
        mcell.molecules.molecule_list[0].color.b = 0.0

        print ( "Done Changing Display for Molecule a" )

        set_view_back()

        for area in bpy.context.screen.areas:
          if area.spaces[0].type == 'VIEW_3D':
            area.spaces[0].region_3d.view_distance *= 0.25

        #set_view_3d()

        #bpy.ops.view3d.zoom(delta=3)

        bpy.ops.screen.animation_play()

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


