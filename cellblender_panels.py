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
import time

# cellblender imports
import cellblender
from cellblender.utils import project_files_path


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


class MCELL_UL_error_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.label(item.name, icon='ERROR')


class MCELL_UL_run_simulation(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if len(cellblender.simulation_popen_list) > index:
            sp = cellblender.simulation_popen_list[index]
            # Simulations are still running
            if sp.poll() is None:
                layout.label(item.name, icon='POSE_DATA')
            # Simulations have failed or were killed
            elif sp.returncode != 0:
                layout.label(item.name, icon='ERROR')
            # Simulations have finished
            else:
                layout.label(item.name, icon='FILE_TICK')
        else:
            # Indexing error may be caused by stale data in the simulation_popen_list?? Maybe??
            layout.label(item.name, icon='ERROR')


class MCELL_UL_run_simulation_queue(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if len(cellblender.simulation_queue.task_dict) > index:
            pid = int(item.name.split(',')[0].split(':')[1])
            q_item = cellblender.simulation_queue.task_dict[pid]
            proc = q_item['process']
            if q_item['status'] == 'queued':
                # Simulation is queued, waiting to run
                layout.label(item.name, icon='TIME')
            elif q_item['status'] == 'running':
                # Simulation is still running
                layout.label(item.name, icon='POSE_DATA')
            elif q_item['status'] == 'mcell_error':
                # Simulation failed due to error detected by MCell
                layout.label(item.name, icon='ERROR')
            elif q_item['status'] == 'died':
                # Simulation was killed or failed due to some other error
                layout.label(item.name, icon='CANCEL')
            else:
                # Simulation has finished normally
                layout.label(item.name, icon='FILE_TICK')
        else:
            # Indexing error may be caused by stale data in the simulation_popen_list?? Maybe??
            layout.label(item.name, icon='ERROR')


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


class MCELL_PT_meshalyzer(bpy.types.Panel):
    bl_label = "CellBlender - Mesh Analysis"
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

            row = layout.row()
            row.operator("mcell.meshalyzer", text="Analyze Mesh",
                icon='MESH_ICOSPHERE')
            row = layout.row()
            row.operator("mcell.gen_meshalyzer_report",
                text="Generate Analysis Report",icon="MESH_ICOSPHERE")

            if (mcell.meshalyzer.status != ""):
                row = layout.row()
                row.label(text=mcell.meshalyzer.status, icon='ERROR')
            row = layout.row()
            row.label(text="Object Name: %s" % (mcell.meshalyzer.object_name))
            row = layout.row()
            row.label(text="Vertices: %d" % (mcell.meshalyzer.vertices))
            row = layout.row()
            row.label(text="Edges: %d" % (mcell.meshalyzer.edges))
            row = layout.row()
            row.label(text="Faces: %d" % (mcell.meshalyzer.faces))
            row = layout.row()
            row.label(text="Surface Area: %.5g" % (mcell.meshalyzer.area))
            row = layout.row()
            if (mcell.meshalyzer.watertight == 'Watertight Mesh'):
              row.label(text="Volume: %.5g" % (mcell.meshalyzer.volume))
            else:
              row.label(text="Volume: approx: %.5g" % (mcell.meshalyzer.volume))
            row = layout.row()
            row.label(text="SA/V Ratio: %.5g" % (mcell.meshalyzer.sav_ratio))

            row = layout.row()
            row.label(text="Mesh Topology:")
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.watertight))
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.manifold))
            row = layout.row()
            row.label(text="      %s" % (mcell.meshalyzer.normal_status))


############### DB: The following two classes are included to create a parameter input panel: only relevant for BNG, SBML or other model import #################

class MCELL_UL_check_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')
	    
  
class MCELL_UL_check_reaction(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_surface_class(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_surface_class_props(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_mod_surface_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_release_pattern(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_molecule_release(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_check_reaction_output_settings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_UL_visualization_export_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')

        # Don't bother showing individual export option if the user has already
        # asked to export everything
        if not context.scene.mcell.viz_output.export_all:
            layout.prop(item, "export_viz", text="Export")
