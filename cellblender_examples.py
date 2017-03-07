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
import bpy
import os
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


def view_all():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    bpy.ops.view3d.view_all(override)


class MCELL_OT_load_lotka_volterra_rxn_limited(bpy.types.Operator):
    bl_idname = "mcell.load_lotka_volterra_rxn_limited"
    bl_label = "Reaction-Limited"
    bl_description = "Loads the Reaction-Limited Lotka-Volterra model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lv.lv_rxn_lim_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_lotka_volterra_diff_limited(bpy.types.Operator):
    bl_idname = "mcell.load_lotka_volterra_diff_limited"
    bl_label = "Diffusion-Limited"
    bl_description = "Loads the Diffusion-Limited Lotka-Volterra model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lv.lv_diff_lim_dm
        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_ficks_law(bpy.types.Operator):
    bl_idname = "mcell.load_ficks_laws"
    bl_label = "Fick's Laws"
    bl_description = "Loads a model illustrating Fick's Laws"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.ficks_laws.ficks_laws_dm
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

        param_mdl_name = 'rat_nmj.parameters.mdl'
        parameters_txt = bpy.data.texts.new(param_mdl_name)
        parameters_txt.write(dm['mcell']['scripting']['script_texts'][param_mdl_name])

        release_mdl_name = 'rat_nmj.release_sites.mdl'
        release_sites_txt = bpy.data.texts.new(release_mdl_name)
        release_sites_txt.write(dm['mcell']['scripting']['script_texts'][release_mdl_name])

        cellblender.replace_data_model(dm, geometry=True)
        view_all()
        return {'FINISHED'}


class MCELL_OT_load_pbc(bpy.types.Operator):
    bl_idname = "mcell.load_pbc"
    bl_label = "Periodic Boundary Conditions"
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


class MCELL_OT_load_dynamic_geometry(bpy.types.Operator):
    bl_idname = "mcell.load_dynamic_geometry"
    bl_label = "Dynamic Geometry"
    bl_description = "Loads a model using dynamic geometries"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.dynamic_geometry.dynamic_geometry_dm
        cellblender.replace_data_model(dm, geometry=True)

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
            row = layout.row(align=True)
            row.label(text="Lotka-Volterra:")
            row.operator("mcell.load_lotka_volterra_rxn_limited")
            row.operator("mcell.load_lotka_volterra_diff_limited")
            row = layout.row()
            row.operator("mcell.load_ficks_laws")
            row = layout.row()
            row.operator("mcell.load_rat_nmj")
            row = layout.row()
            row.operator("mcell.load_pbc")
            row = layout.row()
            row.operator("mcell.load_lipid_raft")
            row = layout.row()
            row.operator("mcell.load_variable_rate_constant")
            row = layout.row()
            row.operator("mcell.load_dynamic_geometry")
