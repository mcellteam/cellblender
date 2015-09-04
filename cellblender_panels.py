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

# <pep8 compliant>

"""
This script draws the panels and other UI elements for CellBlender.

"""

# blender imports
import bpy
from bpy.types import Menu


# python imports
import re
import os

# cellblender imports
import cellblender
from cellblender.cellblender_utils import project_files_path


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


class MCELL_MT_presets(Menu):
    bl_label = "CellBlender Presets"
    preset_subdir = "cellblender"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset



class MCELL_PT_project_settings(bpy.types.Panel):
    bl_label = "CellBlender - Project Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw ( self, context ):
        # Call the draw function of the object itself
        context.scene.mcell.project_settings.draw_panel ( context, self )



class MCELL_UL_model_objects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            # Would like to lay out the actual object name so it can be changed right there.
            # But this has many "trickle down" effects so it hasn't been done yet.
            # layout.prop(item, 'name', text="", icon='FILE_TICK')
            # layout.prop(bpy.data.objects[item.name], 'name', text="", icon='FILE_TICK')
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_model_objects(bpy.types.Panel):
    bl_label = "CellBlender - Model Objects"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.model_objects.draw_panel ( context, self )




class MCELL_PT_object_selector(bpy.types.Panel):
    bl_label = "CellBlender - Object Selector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "CellBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:
            layout.prop(mcell.object_selector, "filter", text="Object Filter:")
            row = layout.row(align=True)
            row.operator("mcell.select_filtered", text="Select Filtered")
            row.operator("mcell.deselect_filtered", text="Deselect Filtered")
            row=layout.row(align=True)
            row.operator("mcell.toggle_visibility_filtered",text="Visibility Filtered")
            row.operator("mcell.toggle_renderability_filtered",text="Renderability Filtered")




############### DB: The following two classes are included to create a parameter input panel: only relevant for BNG, SBML or other model import #################

class MCELL_UL_check_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')
	    
  
class MCELL_PT_define_parameters(bpy.types.Panel):
    bl_label = "CellBlender - Imported Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:
            row = layout.row()
            if mcell.parameters.parameter_list:
                row.label(text="Defined Parameters:", icon='FORCE_LENNARDJONES')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_parameter", "define_parameters",
                                  mcell.parameters, "parameter_list",
                                  mcell.parameters, "active_par_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.parameter_add", icon='ZOOMIN', text="")
                col.operator("mcell.parameter_remove", icon='ZOOMOUT', text="")
                if len(mcell.parameters.parameter_list) > 0:
                    par = mcell.parameters.parameter_list[mcell.parameters.active_par_index]
                    layout.prop(par, "name")
                    layout.prop(par, "value")
                    layout.prop(par, "unit")
                    layout.prop(par, "type")
            else:
                row.label(text="No imported/defined parameter found", icon='ERROR')
#########################################################################################################################################


class MCELL_UL_check_mod_surface_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_mod_surface_regions(bpy.types.Panel):
    bl_label = "CellBlender - Assign Surface Classes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.mod_surf_regions.draw_panel ( context, self )


