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

import cellblender
import bpy, bmesh
import os
import mathutils
from bpy.props import BoolProperty
from cellblender import examples

# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def clear_texts():
    for text in bpy.data.texts:
        bpy.data.texts.remove(text, do_unlink=True )


def zoom_view(delta):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.zoom(delta=delta, mx=delta, my=delta)


def view_all():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_all(override)


def view_selected():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_selected(override)


def get_3d_view_spaces():
    spaces_3d = []
    for area in bpy.context.screen.areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                spaces_3d = spaces_3d + [space]
                # area.spaces.active.show_manipulator = False
    return spaces_3d



def scale_view_distance ( scale ):
    """ Change the view distance for all 3D_VIEW windows """
    spaces = get_3d_view_spaces()
    for space in spaces:
        space.region_3d.view_distance *= scale
    #bpy.ops.view3d.zoom(delta=3)
    #set_view_3d()


def set_axis_angle ( axis, angle ):
    """ Change the view axis and angle for all 3D_VIEW windows """
    spaces = get_3d_view_spaces()
    for space in spaces:
        space.region_3d.view_rotation.axis = mathutils.Vector(axis)
        space.region_3d.view_rotation.angle = angle
    #set_view_3d()


def hide_manipulator ( hide=True ):
    # C.screen.areas[4].spaces[0].show_manipulator = False
    spaces = get_3d_view_spaces()
    for space in spaces:
        space.show_manipulator = not hide


def switch_to_perspective():
    """ Change to perspective for all 3D_VIEW windows """
    spaces = get_3d_view_spaces()
    for space in spaces:
        space.region_3d.view_perspective = 'PERSP'

def switch_to_orthographic():
    """ Change to orthographic for all 3D_VIEW windows """
    spaces = get_3d_view_spaces()
    for space in spaces:
        space.region_3d.view_perspective = 'ORTHO'



class MCELL_OT_load_lotka_volterra_rxn_limited(bpy.types.Operator):
    bl_idname = "mcell.load_lotka_volterra_rxn_limited"
    bl_label = "Lotka-Volterra: Reaction-Limited"
    bl_description = "Loads the Reaction-Limited Lotka-Volterra model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lv.lv_rxn_lim_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        bpy.ops.view3d.viewnumpad(type='TOP')
        hide_manipulator ( hide=True )
        return {'FINISHED'}


class MCELL_OT_load_lotka_volterra_diff_limited(bpy.types.Operator):
    bl_idname = "mcell.load_lotka_volterra_diff_limited"
    bl_label = "Lotka-Volterra: Diffusion-Limited"
    bl_description = "Loads the Diffusion-Limited Lotka-Volterra model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lv.lv_diff_lim_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        bpy.ops.view3d.viewnumpad(type='TOP')
        hide_manipulator ( hide=True )
        return {'FINISHED'}


class MCELL_OT_load_fceri_mcell3r(bpy.types.Operator):
    bl_idname = "mcell.load_fceri_mcell3r"
    bl_label = "FCERI MCell Rules"
    bl_description = "Loads a model of FCERI utilizing MCell Rules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.fceri_mcell3r.fceri_mcell3r_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_lr_cbngl_mcell3r(bpy.types.Operator):
    bl_idname = "mcell.load_lr_cbngl_mcell3r"
    bl_label = "LR CBNGL MCell Rules"
    bl_description = "Loads an LR CBNGL model utilizing MCell Rules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lr_cbngl_mcell3r.lr_cbngl_mcell3r_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=False)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_tlbr_mcell3r(bpy.types.Operator):
    bl_idname = "mcell.load_tlbr_mcell3r"
    bl_label = "TLBR MCell Rules"
    bl_description = "Loads a TLBR model utilizing MCell Rules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.tlbr_mcell3r.tlbr_mcell3r_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=False)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_schain_mcell3r(bpy.types.Operator):
    bl_idname = "mcell.load_schain_mcell3r"
    bl_label = "Simple Chain MCell Rules [MCell3]"
    bl_description = "Loads a simple chain model utilizing MCell Rules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.simple_chain_mcell3r.simple_chain_mcell3r_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        bpy.ops.view3d.viewnumpad(type='TOP')
        hide_manipulator ( hide=True )
        return {'FINISHED'}


class MCELL_OT_load_scoil_mcell3r(bpy.types.Operator):
    bl_idname = "mcell.load_scoil_mcell3r"
    bl_label = "Simple Coil MCell Rules [MCell3]"
    bl_description = "Loads a simple coil model utilizing MCell Rules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.simple_coil_mcell3r.simple_coil_mcell3r_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        bpy.ops.view3d.viewnumpad(type='TOP')
        hide_manipulator ( hide=True )
        return {'FINISHED'}


class MCELL_OT_load_organelle(bpy.types.Operator):
    bl_idname = "mcell.load_organelle"
    bl_label = "Organelle Model"
    bl_description = "Loads the Organelle model using MCell"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.organelle.organelle_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_ficks_1D(bpy.types.Operator):
    bl_idname = "mcell.load_ficks_1d"
    bl_label = "Fick's Law 1D"
    bl_description = "Loads a model illustrating Fick's Laws"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.ficks_laws.ficks_law_1D_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_ficks_3D(bpy.types.Operator):
    bl_idname = "mcell.load_ficks_3d"
    bl_label = "Fick's Law 3D"
    bl_description = "Loads a model illustrating Fick's Laws"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.ficks_laws.ficks_law_3D_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_mind_mine(bpy.types.Operator):
    bl_idname = "mcell.load_mind_mine"
    bl_label = "MinD / MinE System"
    bl_description = "Loads a sample MinD/MinE System"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.mind_mine_system.mind_mine_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_rat_nmj(bpy.types.Operator):
    bl_idname = "mcell.load_rat_nmj"
    bl_label = "Rat NMJ"
    bl_description = "Loads a model of the rat NMJ"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.rat_nmj.rat_nmj_dm

        clear_texts()

        param_mdl_name = 'customization.py'
        customization_py = bpy.data.texts.new(param_mdl_name)
        customization_py.write(dm['mcell']['scripting']['script_texts'][param_mdl_name])

        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_pbc(bpy.types.Operator):
    bl_idname = "mcell.load_pbc"
    bl_label = "Periodic Boundary Conditions [MCell3]"
    bl_description = "Loads a model illustrating periodic boundary conditions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.pbc.pbc_dm

        clear_texts()

        mdl_name = 'pbc.mdl'
        pbc_txt = bpy.data.texts.new(mdl_name)
        pbc_txt.write(dm['mcell']['scripting']['script_texts'][mdl_name])

        cellblender.replace_data_model(dm, geometry=True)
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.scene.objects.active.scale = (0.5, 0.1, 0.1)
        bpy.context.object.draw_type = 'WIRE'
        view_all()
        
        # this is set when data model is imported but not for examples
        cellblender_preferences = context.scene.mcell.cellblender_preferences        
        cellblender_preferences.mcell4_mode = False
        cellblender_preferences.bionetgen_mode = False

        return {'FINISHED'}



class MCELL_OT_load_direct_transport(bpy.types.Operator):
    bl_idname = "mcell.load_dir_transp"
    bl_label = "Direct Transport"
    bl_description = "Simple Direct Transport from inside of Cube to outside of Cube"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.direct_transport.direct_transport_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_delayed_transport(bpy.types.Operator):
    bl_idname = "mcell.load_del_transp"
    bl_label = "Delayed Transport"
    bl_description = "Simple Delayed Transport from inside of Cube to outside of Cube"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.delayed_transport.delayed_transport_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_direct_transport_bngl(bpy.types.Operator):
    bl_idname = "mcell.load_dir_tr_bngl"
    bl_label = "Direct Transport with Compartments"
    bl_description = "Simple Direct Transport from inside of Cube to outside of Cube that uses BNGL compartments"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.direct_transport_BNGL.direct_transport_bngl_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}



class MCELL_OT_load_lipid_raft(bpy.types.Operator):
    bl_idname = "mcell.load_lipid_raft"
    bl_label = "Lipid Raft"
    bl_description = "Loads a lipid raft model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lipid_raft.lipid_raft_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}



class MCELL_OT_load_variable_rate_constant(bpy.types.Operator):
    bl_idname = "mcell.load_variable_rate_constant"
    bl_label = "Variable Rate Constant"
    bl_description = "Loads a model with a variable rate constant"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.variable_rate_constant.variable_rate_constant_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}



class MCELL_OT_load_shape_key_dyn_geo(bpy.types.Operator):
    bl_idname = "mcell.load_skey_dyn_geo"
    bl_label = "Dynamic Geometry (Shape Keys) [MCell3]"
    bl_description = "Loads a model with shape key dynamic geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Start by loading the data model and placing into CellBlender properties
        dm = {}
        dm['mcell'] = examples.shape_key_dyn_geo.shape_key_dyn_geo_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=False)

        # Select the Cube object (created by the data model)
        obj = bpy.data.objects['Cube']
        obj.select = True
        context.scene.objects.active = obj

        # Remove all previous shape keys (otherwise this can't be run twice!!)

        # Suggestion from cmomoney:
        # https://blenderartists.org/forum/showthread.php?243733-Shape-Key-Removal&p=3177866&viewfull=1#post3177866

        #if obj.data.shape_keys:
        # This is never executed because obj.data.shape_keys is None
        # The problem isn't how to delete from the object, but how to delete from bpy.data.shape_keys
        #  for k in obj.data.shape_keys.key_blocks:
        #    obj.shape_key_remove(k)


        # https://blender.stackexchange.com/questions/27193/how-do-i-delete-one-single-shape-key
        # Shape keys can be added and deleted through the Properties editor (the on the right ) under the Data tab in Shape keys.
        # Note that you have to be in Object Mode for this to work... otherwise the minus sign will be greyed out!

        # https://blenderartists.org/forum/showthread.php?283867-Delete-All-Shape-Keys
        # Try this in the python console:
        # [bpy.ops.object.shape_key_remove() for x in range(50)]
        # It's a hack, but it should work!

        # https://blenderartists.org/forum/showthread.php?233730-delete-shape-key-by-name-via-python
        #  delete shape key by name via python

        #    Q. how to delete shapekey by name from python...
        #    foreach_get_howto.jpgforeach_get_howto.jpg

        #    i can get shapekey names via
        #    #### iterate over existing shapekeys
        #    obj = bpy.context.object
        #    sk = obj.data.shape_keys
        #    skNamesArr = sk.key_blocks
        #    for each in skNamesArr:
        #    print each
        #    ##########################

        #    #### adding shape keys
        #    obj.shape_key_add("nameStr")
        #    ##########################

        #    #### removing by name seems hard...
        #    bpy.ops.object.shape_key_remove() # this will remove selected shape key.
        #    # how to give it parameter/ datapath from above lines(where i m iterating over sk)
        #    or how to select a shapekey from list by name, ??

        #    another question(thanks in advance for taking time n helping me out)

        #    Q. how to use function "foreach_get" or "foreach_set" in most of blender returned data objects.?? 

        #you could wrap it like this:

        #Code:

        #import bpy
        #def deleteShapekeyByName(oObject, sShapekeyName):
        #
        #    # setting the active shapekey
        #    iIndex = oObject.data.shape_keys.key_blocks.keys().index(sShapekeyName)
        #    oObject.active_shape_key_index = iIndex
        #
        #    # delete it
        #    bpy.ops.object.shape_key_remove()
        #
        #oActiveObject = bpy.context.active_object
        #deleteShapekeyByName(oActiveObject, "MyShapeKey")

        try:
          # This currently fails with:
          #  RuntimeError: Operator bpy.ops.object.shape_key_remove.poll() failed, context is incorrect
          # Keep it here until we figure out how to make it work!!
          bpy.ops.object.shape_key_remove(all=True)
        except:
          pass


        # Add two shape keys
        bpy.ops.object.shape_key_add(from_mix=False)  # Adds "Basis" Shape Key
        bpy.ops.object.shape_key_add(from_mix=False)  # Adds "Key 1" Shape Key

        # Temp fix - this works,
        #   but additional shape keys are added to:
        #       bpy.data.shape_keys.keys
        #   every time the example is loaded.
        # key_to_modify = bpy.data.shape_keys['Key']
        key_to_modify = bpy.data.shape_keys[-1]
        print ( "Current bpy.data.shape_keys.keys() = " + str(bpy.data.shape_keys.keys()) )

        # Enter Edit Mode and deselect all
        bpy.ops.object.mode_set ( mode="EDIT" )
        bpy.ops.mesh.select_all(action='DESELECT')

        # Move the top 4 points when on "Key 1" (the default key after the previous adds)
        obj = context.object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.verts.ensure_lookup_table()
        verts = bm.verts
        for v in verts:
          if v.co[2] > 0:
            # This is a positive (top) vertex so stretch it
            v.co[0] = v.co[0] * 0.25
            v.co[1] = v.co[1] * 0.25
            v.co[2] = 3.0
        bmesh.update_edit_mesh(mesh)

        # Return to Object Mode
        bpy.ops.object.mode_set ( mode="OBJECT" )

        # Default frame_start is 1, set to 0 to match shape key assignments
        context.scene.frame_start = 0

        # Assign the shape keys to complete one cycle every 100 frames
        context.scene.frame_current = 0
        key_to_modify.key_blocks["Key 1"].value = 0.0
        mesh.shape_keys.key_blocks['Key 1'].keyframe_insert(data_path='value')

        context.scene.frame_current = 100
        key_to_modify.key_blocks["Key 1"].value = 1.0
        mesh.shape_keys.key_blocks['Key 1'].keyframe_insert(data_path='value')

        context.scene.frame_current = 200
        key_to_modify.key_blocks["Key 1"].value = 0.0
        mesh.shape_keys.key_blocks['Key 1'].keyframe_insert(data_path='value')

        # Set the frame to 50 (large cube) so the view all operator will fit at max size
        context.scene.frame_current = 100

        # Switch area type to set the F-Curve modifier to "CYCLES"
        area = bpy.context.area
        old_type = area.type
        area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.fmodifier_add(type='CYCLES')
        area.type = old_type

        # Set the view to show the selected object
        context.scene.update()
        view_all()
        # Return the current frame to 0 (small cube) after viewing large cube
        context.scene.frame_current = 0

        # this is set when data model is imported but not for examples
        cellblender_preferences = context.scene.mcell.cellblender_preferences        
        cellblender_preferences.mcell4_mode = False
        cellblender_preferences.bionetgen_mode = False

        return {'FINISHED'}


class MCELL_OT_load_scripted_dyn_geo(bpy.types.Operator):
    bl_idname = "mcell.load_scripted_dyn_geo"
    bl_label = "Dynamic Geometry (Scripted) [MCell3]"
    bl_description = "Loads a model with scripted dynamic geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.scripted_dyn_geo.scripted_dyn_geo_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)

        # Default frame_start is 1, set to 0 to match model
        context.scene.frame_start = 0
        context.scene.update()

        # Set the frame to 50 (large cube) so the view all operator will fit at max size (not really needed for scripting)
        context.scene.frame_current = 50

        # Set the view to show the selected object
        context.scene.update()

        # Add a cube tepmorarily to use for centering the view
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.scene.objects.active.location.z = 3

        view_all()
        # This zooming seems to have no effect
        # zoom_view(-500)

        # Remove the temporary cube that was used for centering the view
        bpy.ops.object.delete(use_global=False)

        # Re-select the original cube
        bpy.data.objects['Cube'].select = True                       # This selects it (enables manipulator on the object)
        context.scene.objects.active = bpy.data.objects['Cube']      # This makes it active for material display etc

        # Return the current frame to 0 (small cube) after viewing large cube (not really needed for scripting)
        context.scene.frame_current = 0

        # this is set when data model is imported but not for examples
        cellblender_preferences = context.scene.mcell.cellblender_preferences        
        cellblender_preferences.mcell4_mode = False
        cellblender_preferences.bionetgen_mode = False

        return {'FINISHED'}


class MCELL_OT_load_dyn_geo_cc(bpy.types.Operator):
    bl_idname = "mcell.load_dyn_geo_cc"
    bl_label = "Dynamic Geometry (Scripted with concentration clamp) [MCell3]"
    bl_description = "Loads a scripted dynamic geometry model with concentration clamp"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.dyn_geo_conc_clamp.dyn_geo_cc_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)

        # Default frame_start is 1, set to 0 to match model
        context.scene.frame_start = 0
        context.scene.update()

        # Set the frame to 50 (large cube) so the view all operator will fit at max size (not really needed for scripting)
        context.scene.frame_current = 50

        # Set the view to show the selected object
        context.scene.update()

        # Add a cube tepmorarily to use for centering the view
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.scene.objects.active.location.z = 3

        view_all()
        # This zooming seems to have no effect
        # zoom_view(-500)

        # Remove the temporary cube that was used for centering the view
        bpy.ops.object.delete(use_global=False)

        # Re-select the original cube
        bpy.data.objects['Cube'].select = True                       # This selects it (enables manipulator on the object)
        context.scene.objects.active = bpy.data.objects['Cube']      # This makes it active for material display etc

        # Return the current frame to 0 (small cube) after viewing large cube (not really needed for scripting)
        context.scene.frame_current = 0

        # this is set when data model is imported but not for examples
        cellblender_preferences = context.scene.mcell.cellblender_preferences        
        cellblender_preferences.mcell4_mode = False
        cellblender_preferences.bionetgen_mode = False

        return {'FINISHED'}


class MCELL_OT_load_dynamic_geometry(bpy.types.Operator):
    bl_idname = "mcell.load_dynamic_geometry"
    bl_label = "Dynamic Geometry (Blend file) [MCell3]"
    bl_description = "Loads a model using dynamic geometries"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.dynamic_geometry.dynamic_geometry_dm
        cellblender.replace_data_model(dm, geometry=True, scripts=True)

        # load object with shape keys from blend file
        blendfile = os.path.join(os.path.dirname(__file__), "./examples/dynamic_geometry.blend")
        section   = "/Object/"
        obj    = "Cube"
        filepath  = blendfile + section + obj
        directory = blendfile + section
        filename  = obj
        bpy.ops.wm.append(
            filepath=filepath, 
            filename=filename,
            directory=directory)

        # set it to be dynamic and make transparent
        bpy.context.scene.mcell.model_objects.object_list[0].dynamic = True
        bpy.data.objects["Cube"].show_transparent = True
        bpy.data.materials["Cube_mat"].use_transparency = True
        bpy.data.materials["Cube_mat"].alpha = 0.2
        view_all()
        
        # this is set when data model is imported but not for examples
        cellblender_preferences = context.scene.mcell.cellblender_preferences        
        cellblender_preferences.mcell4_mode = False
        cellblender_preferences.bionetgen_mode = False

        return {'FINISHED'}


class MCELL_PT_examples(bpy.types.Panel):
    bl_label = "CellBlender - Examples"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.cellblender_examples.draw_panel ( context, self )



class CellBlenderExamplesPropertyGroup(bpy.types.PropertyGroup):

    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            row = layout.row()
            row.operator("mcell.load_organelle")
            row = layout.row()
            row.operator("mcell.load_ficks_1d")
            row = layout.row()
            row.operator("mcell.load_ficks_3d")
            row = layout.row()
            row.operator("mcell.load_rat_nmj")
            row = layout.row()
            row.operator("mcell.load_lipid_raft")
            row = layout.row()
            row.operator("mcell.load_variable_rate_constant")
            row = layout.row()
            row.operator("mcell.load_lotka_volterra_rxn_limited")
            row = layout.row()
            row.operator("mcell.load_lotka_volterra_diff_limited")
            row = layout.row()
            row.operator("mcell.load_dir_transp")
            row = layout.row()
            row.operator("mcell.load_del_transp")
            row = layout.row()
            row.operator("mcell.load_dir_tr_bngl")
            row = layout.row()
            row.operator("mcell.load_fceri_mcell3r")
            row = layout.row()
            row.operator("mcell.load_lr_cbngl_mcell3r")
            row = layout.row()
            row.operator("mcell.load_tlbr_mcell3r")
            row = layout.row()
            row.operator("mcell.load_mind_mine")
            row = layout.row()
            row.operator("mcell.load_pbc")
            row = layout.row()
            row.operator("mcell.load_dynamic_geometry")
            row = layout.row()
            row.operator("mcell.load_skey_dyn_geo")
            row = layout.row()
            row.operator("mcell.load_scripted_dyn_geo")
            row = layout.row()
            row.operator("mcell.load_dyn_geo_cc")
            row = layout.row()
            row.operator("mcell.load_schain_mcell3r")
            row = layout.row()
            row.operator("mcell.load_scoil_mcell3r")

