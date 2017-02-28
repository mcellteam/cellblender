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


class MCELL_OT_load_lotka_volterra(bpy.types.Operator):
    bl_idname = "mcell.load_lotka_volterra"
    bl_label = "Load Lotka-Volterra Model"
    bl_description = "Loads a Lotka-Volterra model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.lv.lv_dm
        cellblender.replace_data_model(dm, geometry=True)
        return {'FINISHED'}


class MCELL_OT_load_ficks_law(bpy.types.Operator):
    bl_idname = "mcell.load_ficks_laws"
    bl_label = "Load Fick's Laws Model"
    bl_description = "Loads a model illustrating Fick's Laws"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.ficks_laws.ficks_laws_dm
        cellblender.replace_data_model(dm, geometry=True)
        return {'FINISHED'}


class MCELL_OT_load_rat_nmj(bpy.types.Operator):
    bl_idname = "mcell.load_rat_nmj"
    bl_label = "Load Rat NMJ Model"
    bl_description = "Loads a model of the rat NMJ"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        dm = {}
        dm['mcell'] = examples.rat_nmj.rat_nmj_dm

        from pprint import pprint
        pprint(dm['mcell']['scripting']['script_texts']['rat_nmj.parameters.mdl'])
        parameters_txt = bpy.data.texts.new("rat_nmj.parameters.mdl")
        parameters_txt.write(dm['mcell']['scripting']['script_texts']['rat_nmj.parameters.mdl'])

        release_sites_txt = bpy.data.texts.new("rat_nmj.release_sites.mdl")
        release_sites_txt.write(dm['mcell']['scripting']['script_texts']['rat_nmj.release_sites.mdl'])

        cellblender.replace_data_model(dm, geometry=True)
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
            row.operator("mcell.load_lotka_volterra")
            row.operator("mcell.load_ficks_laws")
            row.operator("mcell.load_rat_nmj")
