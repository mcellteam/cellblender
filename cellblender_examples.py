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

# blender imports
import bpy
from bpy.props import BoolProperty
from cellblender import examples

# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


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

        parameters_txt = bpy.data.texts.new("rat_nmj.parameters.mdl")
        parameters_txt.write(dm['mcell']['scripting']['script_texts']['rat_nmj.parameters.mdl'])

        release_sites_txt = bpy.data.texts.new("rat_nmj.release_sites.mdl")
        release_sites_txt.write(dm['mcell']['scripting']['script_texts']['rat_nmj.release_sites.mdl'])

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

        pbc_txt = bpy.data.texts.new("pbc.mdl")
        pbc_txt.write(dm['mcell']['scripting']['script_texts']['pbc.mdl'])

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
