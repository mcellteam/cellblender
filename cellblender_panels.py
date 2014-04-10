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


#CellBlendereGUI Panels:
class MCELL_PT_cellblender_preferences(bpy.types.Panel):
    bl_label = "CellBlender - Preferences"
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
            row = layout.row(align=True)
            row.operator("mcell.preferences_reset")
            layout.separator()

            row = layout.row()
            row.operator("mcell.set_mcell_binary",
                         text="Set Path to MCell Binary", icon='FILESEL')
            row = layout.row()
            mcell_binary = mcell.cellblender_preferences.mcell_binary
            if not mcell_binary:
                row.label("MCell Binary not set", icon='UNPINNED')
            elif not mcell.cellblender_preferences.mcell_binary_valid:
                row.label("MCell File/Permissions Error: " +
                    mcell.cellblender_preferences.mcell_binary, icon='ERROR')
            else:
                row.label(
                    text="MCell Binary: "+mcell.cellblender_preferences.mcell_binary,
                    icon='FILE_TICK')

            row = layout.row()
            row.operator("mcell.set_bionetgen_location",
                         text="Set Path to BioNetGen File", icon='FILESEL')
            row = layout.row()
            bionetgen_location = mcell.cellblender_preferences.bionetgen_location
            if not bionetgen_location:
                row.label("BioNetGen location not set", icon='UNPINNED')
            elif not mcell.cellblender_preferences.bionetgen_location_valid:
                row.label("BioNetGen File/Permissions Error: " +
                    mcell.cellblender_preferences.bionetgen_location, icon='ERROR')
            else:
                row.label(
                    text="BioNetGen Location: " + mcell.cellblender_preferences.bionetgen_location,
                    icon='FILE_TICK')

            row = layout.row()
            row.operator("mcell.set_python_binary",
                         text="Set Path to Python Binary", icon='FILESEL')
            row = layout.row()
            python_path = mcell.cellblender_preferences.python_binary
            if not python_path:
                row.label("Python Binary not set", icon='UNPINNED')
            elif not mcell.cellblender_preferences.python_binary_valid:
                row.label("Python File/Permissions Error: " +
                    mcell.cellblender_preferences.python_binary, icon='ERROR')
            else:
                row.label(
                    text="Python Binary: " + mcell.cellblender_preferences.python_binary,
                    icon='FILE_TICK')

            row = layout.row()
            row.prop(mcell.cellblender_preferences, "decouple_export_run")
            row = layout.row()
            row.prop(mcell.cellblender_preferences, "invalid_policy")
            #row = layout.row()
            #row.prop(mcell.cellblender_preferences, "debug_level")


class MCELL_PT_project_settings(bpy.types.Panel):
    bl_label = "CellBlender - Project Settings"
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
            row.label(text="CellBlender ID: "+cellblender.cellblender_info[
                'cellblender_source_sha1'])


            row = layout.row()
            if not bpy.data.filepath:
                row.label(
                    text="No Project Directory: Use File/Save or File/SaveAs",
                    icon='UNPINNED')
            else:
                row.label(
                    text="Project Directory: " + os.path.dirname(bpy.data.filepath),
                    icon='FILE_TICK')

            row = layout.row()
            layout.prop(context.scene, "name", text="Project Base Name")


class MCELL_UL_error_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.label(item.name, icon='ERROR')


class MCELL_UL_run_simulation(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

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


class MCELL_PT_run_simulation(bpy.types.Panel):
    bl_label = "CellBlender - Run Simulation"
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

            #main_mdl = ("%s.main.mdl" %
            #            os.path.join(os.path.dirname(bpy.data.filepath),
            #            mcell.project_settings.base_name))

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")

            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            #mcell.project_settings.base_name = scene_name

            main_mdl = project_files_path()
            main_mdl = os.path.join(main_mdl, scene_name + ".main.mdl")

            row = layout.row()

            # Only allow the simulation to be run if both an MCell binary and a
            # project dir have been selected. There also needs to be a main mdl
            # file present.
            if not mcell.cellblender_preferences.mcell_binary:
                row.label(text="Set an MCell binary in CellBlender - Preferences Panel", icon='ERROR')
            elif not os.path.dirname(bpy.data.filepath):
                row.label(
                    text="Open or save a .blend file to set the project directory",
                    icon='ERROR')
            elif (not os.path.isfile(main_mdl) and
                    mcell.cellblender_preferences.decouple_export_run):
                row.label(text="Export the project", icon='ERROR')
                row = layout.row()
                row.operator(
                    "mcell.export_project",
                    text="Export CellBlender Project", icon='EXPORT')
            else:
                row = layout.row(align=True)
                row.prop(mcell.run_simulation, "start_seed")
                row.prop(mcell.run_simulation, "end_seed")
                row = layout.row()
                row.prop(mcell.run_simulation, "mcell_processes")
                row = layout.row()
                row.prop(mcell.run_simulation, "log_file")
                row = layout.row()
                row.prop(mcell.run_simulation, "error_file")

                if mcell.cellblender_preferences.decouple_export_run:
                    row = layout.row()
                    row.prop(mcell.export_project, "export_format")
                    row = layout.row()
                    row.operator(
                        "mcell.export_project", text="Export CellBlender Project",
                        icon='EXPORT')
                row = layout.row()
                row.prop(mcell.run_simulation, "remove_append", expand=True)
                row = layout.row()
                row.operator("mcell.run_simulation", text="Run Simulation",
                             icon='COLOR_RED')

                if (mcell.run_simulation.processes_list and
                        cellblender.simulation_popen_list):
                    row = layout.row()
                    row.label(text="Sets of MCell Processes:",
                              icon='FORCE_LENNARDJONES')
                    row = layout.row()
                    row.template_list("MCELL_UL_run_simulation", "run_simulation",
                                      mcell.run_simulation, "processes_list",
                                      mcell.run_simulation, "active_process_index",
                                      rows=2)
                    row = layout.row()
                    row.operator("mcell.clear_run_list")
            if mcell.run_simulation.status:
                row = layout.row()
                row.label(text=mcell.run_simulation.status, icon='ERROR')
            
            if mcell.run_simulation.error_list: 
                row = layout.row() 
                row.label(text="Errors:", icon='ERROR')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_error_list", "run_simulation",
                                  mcell.run_simulation, "error_list",
                                  mcell.run_simulation, "active_err_index", rows=2)



class MCELL_PT_viz_results(bpy.types.Panel):
    bl_label = "CellBlender - Visualize Simulation Results"
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
            row.prop(mcell.mol_viz, "manual_select_viz_dir")
            row = layout.row()
            if mcell.mol_viz.manual_select_viz_dir:
                row.operator("mcell.select_viz_data", icon='IMPORT')
            else:
                row.operator("mcell.read_viz_data", icon='IMPORT')
            row = layout.row()
            row.label(text="Molecule Viz Directory: " + mcell.mol_viz.mol_file_dir,
                      icon='FILE_FOLDER')
            row = layout.row()
            if not mcell.mol_viz.manual_select_viz_dir:
                row.template_list("UI_UL_list", "viz_seed", mcell.mol_viz,
                                "mol_viz_seed_list", mcell.mol_viz,
                                "active_mol_viz_seed_index", rows=2)
            row = layout.row()
            row = layout.row()
            row.label(text="Current Molecule File: "+mcell.mol_viz.mol_file_name,
                      icon='FILE')
            row = layout.row()
            row.template_list("UI_UL_list", "viz_results", mcell.mol_viz,
                              "mol_file_list", mcell.mol_viz, "mol_file_index",
                              rows=2)
            row = layout.row()
            layout.prop(mcell.mol_viz, "mol_viz_enable")


class MCELL_UL_model_objects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_model_objects(bpy.types.Panel):
    bl_label = "CellBlender - Model Objects"
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
            row.label(text="Model Objects:", icon='MESH_ICOSPHERE')
            row = layout.row()
            col = row.column()
            col.template_list("MCELL_UL_model_objects", "model_objects",
                              mcell.model_objects, "object_list",
                              mcell.model_objects, "active_obj_index", rows=2)
            col = row.column(align=True)
#           col.active = (len(context.selected_objects) == 1)
            col.operator("mcell.model_objects_add", icon='ZOOMIN', text="")
            col.operator("mcell.model_objects_remove", icon='ZOOMOUT', text="")
#           row = layout.row()
#           sub = row.row(align=True)
#           sub.operator("mcell.model_objects_include", text="Include")
#           sub = row.row(align=True)
#           sub.operator("mcell.model_objects_select", text="Select")
#           sub.operator("mcell.model_objects_deselect", text="Deselect")



class MCELL_PT_object_selector(bpy.types.Panel):
    bl_label = "CellBlender - Object Selector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
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


'''
class MCELL_PT_user_model_parameters(bpy.types.Panel):
    bl_label = "CellBlender - User-Defined Model Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
'''


class MCELL_PT_initialization(bpy.types.Panel):
    bl_label = "CellBlender - Model Initialization"
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
            ps = mcell.parameter_system
            mcell.initialization.iterations.draw(layout,ps)
            mcell.initialization.time_step.draw(layout,ps)

            # Advanced Options
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if mcell.initialization.advanced:
                row.prop(mcell.initialization, "advanced", icon='TRIA_DOWN',
                         text="Advanced Options", emboss=False)

                mcell.initialization.time_step_max.draw(box,ps)
                mcell.initialization.space_step.draw(box,ps)
                mcell.initialization.interaction_radius.draw(box,ps)
                mcell.initialization.radial_directions.draw(box,ps)
                mcell.initialization.radial_subdivisions.draw(box,ps)
                mcell.initialization.vacancy_search_distance.draw(box,ps)
                mcell.initialization.surface_grid_density.draw(box,ps)

                row = box.row()
                row.prop(mcell.initialization, "accurate_3d_reactions")
                row = box.row()
                row.prop(mcell.initialization, "center_molecules_grid")
                row = box.row()
                row.prop(mcell.initialization, "microscopic_reversibility")
            else:
                row.prop(mcell.initialization, "advanced", icon='TRIA_RIGHT',
                         text="Advanced Options", emboss=False)

            # Notifications
            #box = layout.box(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if mcell.initialization.notifications:
                row.prop(mcell.initialization, "notifications", icon='TRIA_DOWN',
                         text="Notifications", emboss=False)
                row = box.row()
                row.prop(mcell.initialization, "all_notifications")
                if mcell.initialization.all_notifications == 'INDIVIDUAL':
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "probability_report")
                    if mcell.initialization.probability_report == 'THRESHOLD':
                        row.prop(
                            mcell.initialization, "probability_report_threshold",
                            slider=True)
                    row = box.row()
                    row.prop(mcell.initialization, "diffusion_constant_report")
                    row = box.row()
                    row.prop(mcell.initialization, "file_output_report")
                    row = box.row()
                    row.prop(mcell.initialization, "final_summary")
                    row = box.row()
                    row.prop(mcell.initialization, "iteration_report")
                    row = box.row()
                    row.prop(mcell.initialization, "partition_location_report")
                    row = box.row()
                    row.prop(mcell.initialization, "varying_probability_report")
                    row = box.row()
                    row.prop(mcell.initialization, "progress_report")
                    row = box.row()
                    row.prop(mcell.initialization, "release_event_report")
                    row = box.row()
                    row.prop(mcell.initialization, "molecule_collision_report")
            else:
                row.prop(mcell.initialization, "notifications", icon='TRIA_RIGHT',
                         text="Notifications", emboss=False)

            # Warnings
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if mcell.initialization.warnings:
                row.prop(mcell.initialization, "warnings", icon='TRIA_DOWN',
                         text="Warnings", emboss=False)
                row = box.row()
                row.prop(mcell.initialization, "all_warnings")
                if mcell.initialization.all_warnings == 'INDIVIDUAL':
                    row = box.row()
                    row.prop(mcell.initialization, "degenerate_polygons")
                    row = box.row()
                    row.prop(mcell.initialization, "missing_surface_orientation")
                    row = box.row()
                    row.prop(mcell.initialization, "negative_diffusion_constant")
                    row = box.row()
                    row.prop(mcell.initialization, "negative_reaction_rate")
                    row = box.row()
                    row.prop(mcell.initialization, "useless_volume_orientation")
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "high_reaction_probability")
                    if mcell.initialization.high_reaction_probability != 'IGNORED':
                        row.prop(mcell.initialization,
                                 "high_probability_threshold", slider=True)
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "lifetime_too_short")
                    if mcell.initialization.lifetime_too_short == 'WARNING':
                        row.prop(mcell.initialization, "lifetime_threshold")
                    row = box.row(align=True)
                    row.prop(mcell.initialization, "missed_reactions")
                    if mcell.initialization.missed_reactions == 'WARNING':
                        row.prop(mcell.initialization, "missed_reaction_threshold")
            else:
                row.prop(mcell.initialization, "warnings", icon='TRIA_RIGHT',
                         text="Warnings", emboss=False)

            if (mcell.initialization.status != ""):
                row = layout.row()
                row.label(text=mcell.initialization.status, icon='ERROR')


class MCELL_PT_partitions(bpy.types.Panel):
    bl_label = "CellBlender - Define and Visualize Partitions"
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
            layout.prop(mcell.partitions, "include")
            if mcell.partitions.include:
                row = layout.row(align=True)
                row.prop(mcell.partitions, "x_start")
                row.prop(mcell.partitions, "x_end")
                row.prop(mcell.partitions, "x_step")

                row = layout.row(align=True)
                row.prop(mcell.partitions, "y_start")
                row.prop(mcell.partitions, "y_end")
                row.prop(mcell.partitions, "y_step")

                row = layout.row(align=True)
                row.prop(mcell.partitions, "z_start")
                row.prop(mcell.partitions, "z_end")
                row.prop(mcell.partitions, "z_step")

                if mcell.model_objects.object_list:
                    layout.operator("mcell.auto_generate_boundaries",
                                    icon='OUTLINER_OB_LATTICE')
                if not "partitions" in bpy.data.objects:
                    layout.operator("mcell.create_partitions_object",
                                    icon='OUTLINER_OB_LATTICE')
                else:
                    layout.operator("mcell.remove_partitions_object",
                                    icon='OUTLINER_OB_LATTICE')

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




class MCELL_UL_check_reaction(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_reactions(bpy.types.Panel):
    bl_label = "CellBlender - Define Reactions"
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
            ps = mcell.parameter_system
            row = layout.row()
            if mcell.molecules.molecule_list:
                row.label(text="Defined Reactions:", icon='FORCE_LENNARDJONES')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_reaction", "define_reactions",
                                  mcell.reactions, "reaction_list",
                                  mcell.reactions, "active_rxn_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.reaction_add", icon='ZOOMIN', text="")
                col.operator("mcell.reaction_remove", icon='ZOOMOUT', text="")
                if len(mcell.reactions.reaction_list) > 0:
                    rxn = mcell.reactions.reaction_list[
                        mcell.reactions.active_rxn_index]
                    layout.prop(rxn, "reactants")
                    layout.prop(rxn, "type")
                    layout.prop(rxn, "products")
                    layout.prop(rxn, "variable_rate_switch")
                    if rxn.variable_rate_switch:
                        layout.operator("mcell.variable_rate_add", icon='FILESEL')
                        # Do we need these messages in addition to the status
                        # message that appears in the list? I'll leave it for now.
                        if not rxn.variable_rate:
                            layout.label("Rate file not set", icon='UNPINNED')
                        elif not rxn.variable_rate_valid:
                            layout.label("File/Permissions Error: " +
                                rxn.variable_rate, icon='ERROR')
                        else:
                            layout.label(
                                text="Rate File: " + rxn.variable_rate,
                                icon='FILE_TICK')
                    else:
                        #rxn.fwd_rate.draw_in_new_row(layout)
                        rxn.fwd_rate.draw(layout,ps)
                        if rxn.type == "reversible":
                            #rxn.bkwd_rate.draw_in_new_row(layout)
                            rxn.bkwd_rate.draw(layout,ps)
                    layout.prop(rxn, "rxn_name")
            else:
                row.label(text="Define at least one molecule", icon='ERROR')


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


class MCELL_PT_define_surface_classes(bpy.types.Panel):
    bl_label = "CellBlender - Define Surface Classes"
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
            surf_class = mcell.surface_classes

            row = layout.row()
            row.label(text="Defined Surface Classes:", icon='FACESEL_HLT')
            row = layout.row()
            col = row.column()
            # The template_list for the surface classes themselves
            col.template_list("MCELL_UL_check_surface_class", "define_surf_class",
                              surf_class, "surf_class_list", surf_class,
                              "active_surf_class_index", rows=2)
            col = row.column(align=True)
            col.operator("mcell.surface_class_add", icon='ZOOMIN', text="")
            col.operator("mcell.surface_class_remove", icon='ZOOMOUT', text="")
            row = layout.row()
            # Show the surface class properties template_list if there is at least
            # a single surface class.
            if surf_class.surf_class_list:
                active_surf_class = surf_class.surf_class_list[
                    surf_class.active_surf_class_index]
                row = layout.row()
                row.prop(active_surf_class, "name")
                row = layout.row()
                row.label(text="%s Properties:" % active_surf_class.name,
                          icon='FACESEL_HLT')
                row = layout.row()
                col = row.column()
                # The template_list for the properties of a surface class.
                # Properties include molecule, orientation, and type of surf class.
                # There can be multiple properties for a single surface class
                col.template_list("MCELL_UL_check_surface_class_props",
                                  "define_surf_class_props", active_surf_class,
                                  "surf_class_props_list", active_surf_class,
                                  "active_surf_class_props_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.surf_class_props_add", icon='ZOOMIN', text="")
                col.operator("mcell.surf_class_props_remove", icon='ZOOMOUT',
                             text="")
                # Show the surface class property fields (molecule, orientation,
                # type) if there is at least a single surface class property.
                if active_surf_class.surf_class_props_list:
                    surf_class_props = active_surf_class.surf_class_props_list[
                        active_surf_class.active_surf_class_props_index]
                    layout.prop_search(surf_class_props, "molecule",
                                       mcell.molecules, "molecule_list",
                                       icon='FORCE_LENNARDJONES')
                    layout.prop(surf_class_props, "surf_class_orient")
                    layout.prop(surf_class_props, "surf_class_type")
                    if (surf_class_props.surf_class_type == 'CLAMP_CONCENTRATION'):
                        layout.prop(surf_class_props, "clamp_value_str")


class MCELL_UL_check_mod_surface_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_mod_surface_regions(bpy.types.Panel):
    bl_label = "CellBlender - Modify Surface Regions"
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

            mod_surf_regions = context.scene.mcell.mod_surf_regions

            row = layout.row()
            if not mcell.surface_classes.surf_class_list:
                row.label(text="Define at least one surface class", icon='ERROR')
            elif not mcell.model_objects.object_list:
                row.label(text="Add a mesh to the Model Objects list",
                          icon='ERROR')
            else:
                row.label(text="Modified Surface Regions:", icon='FACESEL_HLT')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_mod_surface_regions",
                                  "mod_surf_regions", mod_surf_regions,
                                  "mod_surf_regions_list", mod_surf_regions,
                                  "active_mod_surf_regions_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.mod_surf_regions_add", icon='ZOOMIN', text="")
                col.operator("mcell.mod_surf_regions_remove", icon='ZOOMOUT',
                             text="")
                if mod_surf_regions.mod_surf_regions_list:
                    active_mod_surf_regions = \
                        mod_surf_regions.mod_surf_regions_list[
                            mod_surf_regions.active_mod_surf_regions_index]
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "surf_class_name",
                                    mcell.surface_classes, "surf_class_list",
                                    icon='FACESEL_HLT')
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "object_name",
                                    mcell.model_objects, "object_list",
                                    icon='MESH_ICOSPHERE')
                    if active_mod_surf_regions.object_name:
                        try:
                            regions = bpy.data.objects[
                                active_mod_surf_regions.object_name].mcell.regions
                            layout.prop_search(active_mod_surf_regions,
                                               "region_name", regions,
                                               "region_list", icon='FACESEL_HLT')
                        except KeyError:
                            pass


class MCELL_UL_check_release_pattern(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_release_pattern(bpy.types.Panel):
    bl_label = "CellBlender - Release Pattern"
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
          ps = mcell.parameter_system

          row = layout.row()
          row.label(text="Release Patterns:",
                      icon='FORCE_LENNARDJONES')
          row = layout.row()
          col = row.column()
          col.template_list("MCELL_UL_check_release_pattern",
                              "release_pattern", mcell.release_patterns,
                              "release_pattern_list", mcell.release_patterns,
                              "active_release_pattern_index", rows=2)
          col = row.column(align=True)
          col.operator("mcell.release_pattern_add", icon='ZOOMIN', text="")
          col.operator("mcell.release_pattern_remove", icon='ZOOMOUT', text="")
          if mcell.release_patterns.release_pattern_list:
              rel_pattern = mcell.release_patterns.release_pattern_list[
                  mcell.release_patterns.active_release_pattern_index]
              layout.prop(rel_pattern, "name")

              rel_pattern.delay.draw(layout,ps)
              rel_pattern.release_interval.draw(layout,ps)
              rel_pattern.train_duration.draw(layout,ps)
              rel_pattern.train_interval.draw(layout,ps)
              rel_pattern.number_of_trains.draw(layout,ps)
              """
              layout.prop(rel_pattern, "delay_str")
              layout.prop(rel_pattern, "release_interval_str")
              layout.prop(rel_pattern, "train_duration_str")
              layout.prop(rel_pattern, "train_interval_str")
              layout.prop(rel_pattern, "number_of_trains")
              """


class MCELL_UL_check_molecule_release(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_molecule_release(bpy.types.Panel):
    bl_label = "CellBlender - Molecule Release/Placement"
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
            ps = mcell.parameter_system
            row = layout.row()
            if not mcell.molecules.molecule_list:
                row.label(text="Define at least one molecule", icon='ERROR')
            else:
                row.label(text="Release/Placement Sites:",
                          icon='FORCE_LENNARDJONES')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_molecule_release",
                                  "molecule_release", mcell.release_sites,
                                  "mol_release_list", mcell.release_sites,
                                  "active_release_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.release_site_add", icon='ZOOMIN', text="")
                col.operator("mcell.release_site_remove", icon='ZOOMOUT', text="")
                if len(mcell.release_sites.mol_release_list) > 0:
                    rel = mcell.release_sites.mol_release_list[
                        mcell.release_sites.active_release_index]
                    layout.prop(rel, "name")
                    layout.prop_search(rel, "molecule", mcell.molecules,
                                       "molecule_list", text="Molecule",
                                       icon='FORCE_LENNARDJONES')
                    if rel.molecule in mcell.molecules.molecule_list:
                        if mcell.molecules.molecule_list[rel.molecule].type == '2D':
                            layout.prop(rel, "orient")

                    layout.prop(rel, "shape")

                    if ((rel.shape == 'CUBIC') | (rel.shape == 'SPHERICAL') |
                            (rel.shape == 'SPHERICAL_SHELL')):
                        #layout.prop(rel, "location")
                        rel.location_x.draw(layout,ps)
                        rel.location_y.draw(layout,ps)
                        rel.location_z.draw(layout,ps)
                        rel.diameter.draw(layout,ps)

                    if rel.shape == 'OBJECT':
                        layout.prop(rel, "object_expr")

                    rel.probability.draw(layout,ps)
            
                    layout.prop(rel, "quantity_type")
                    rel.quantity.draw(layout,ps)

                    if rel.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
                        rel.stddev.draw(layout,ps)
                 
                     
                    layout.prop_search(rel, "pattern", mcell.release_patterns,
                                       "release_pattern_rxn_name_list",
                                       icon='FORCE_LENNARDJONES')


class MCELL_UL_check_reaction_output_settings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_reaction_output_settings(bpy.types.Panel):
    bl_label = "CellBlender - Reaction Output Settings"
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
            if mcell.molecules.molecule_list:
                row.label(text="Reaction Data Output:", icon='FORCE_LENNARDJONES')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_reaction_output_settings",
                                  "reaction_output", mcell.rxn_output,
                                  "rxn_output_list", mcell.rxn_output,
                                  "active_rxn_output_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.rxn_output_add", icon='ZOOMIN', text="")
                col.operator("mcell.rxn_output_remove", icon='ZOOMOUT', text="")
                # Show molecule, object, and region options only if there is at
                # least one count statement.
                if mcell.rxn_output.rxn_output_list:
                    rxn_output = mcell.rxn_output.rxn_output_list[
                        mcell.rxn_output.active_rxn_output_index]
                    layout.prop(rxn_output, "rxn_or_mol", expand=True)
                    if rxn_output.rxn_or_mol == 'Molecule':
                        layout.prop_search(
                            rxn_output, "molecule_name", mcell.molecules,
                            "molecule_list", icon='FORCE_LENNARDJONES')
                    else:
                        layout.prop_search(
                            rxn_output, "reaction_name", mcell.reactions,
                            "reaction_name_list", icon='FORCE_LENNARDJONES')
                    layout.prop(rxn_output, "count_location", expand=True)
                    # Show the object selector if Object or Region is selected
                    if rxn_output.count_location != "World":
                        layout.prop_search(
                            rxn_output, "object_name", mcell.model_objects,
                            "object_list", icon='MESH_ICOSPHERE')
                        if (rxn_output.object_name and
                                (rxn_output.count_location == "Region")):
                            try:
                                regions = bpy.data.objects[
                                    rxn_output.object_name].mcell.regions
                                layout.prop_search(rxn_output, "region_name",
                                                   regions, "region_list",
                                                   icon='FACESEL_HLT')
                            except KeyError:
                                pass

                    layout.separator()
                    layout.separator()

                    row = layout.row()
                    row.label(text="Plot Reaction Data:",
                              icon='FORCE_LENNARDJONES')

                    row = layout.row()

                    col = row.column()
                    col.prop(mcell.rxn_output, "plot_layout")

                    col = row.column()
                    col.prop(mcell.rxn_output, "combine_seeds")

                    row = layout.row()

                    col = row.column()
                    col.prop(mcell.rxn_output, "plot_legend")

                    col = row.column()
                    col.prop(mcell.rxn_output, "mol_colors")


                    row = layout.row()
                    button_num = 0
                    num_columns = len(cellblender.cellblender_info[
                        'cellblender_plotting_modules'])
                    if num_columns > 3:
                        num_columns = 2
                    for plot_module in cellblender.cellblender_info[
                            'cellblender_plotting_modules']:
                        mod_name = plot_module.get_name()
                        if (button_num % num_columns) == 0:
                            button_num = 0
                            row = layout.row()
                        col = row.column()
                        col.operator("mcell.plot_rxn_output_generic",
                                     text=mod_name).plotter_button_label = mod_name
                        button_num = button_num + 1

                    #layout.separator()
                    #layout.separator()

                    #row = layout.row()
                    #col = row.column()
                    #col.operator("mcell.plot_rxn_output_command",
                    #             text="Execute Custom Plot Command:")
                    #layout.prop(mcell.reactions, "plot_command")

            else:
                row.label(text="Define at least one molecule", icon='ERROR')


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


class MCELL_PT_visualization_output_settings(bpy.types.Panel):
    bl_label = "CellBlender - Visualization Output Settings"
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
            if mcell.molecules.molecule_list:
                row.label(text="Molecules To Visualize:",
                          icon='FORCE_LENNARDJONES')
                row.prop(mcell.viz_output, "export_all")
                layout.template_list("MCELL_UL_visualization_export_list",
                                     "viz_export", mcell.molecules,
                                     "molecule_list", mcell.viz_output,
                                     "active_mol_viz_index", rows=2)
                layout.prop(mcell.viz_output, "all_iterations")
                if mcell.viz_output.all_iterations is False:
                    row = layout.row(align=True)
                    row.prop(mcell.viz_output, "start")
                    row.prop(mcell.viz_output, "end")
                    row.prop(mcell.viz_output, "step")
            else:
                row.label(text="Define at least one molecule", icon='ERROR')


class MCELL_PT_molecule_glyphs(bpy.types.Panel):
    bl_label = "CellBlender - Molecule Shape"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

#    @classmethod
#    def poll(cls, context):

#        return ((len(context.selected_objects) == 1) and
#                (context.selected_objects[0].type == 'MESH'))

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:
            active = False
            if ((len(context.selected_objects) == 1) and
                    (context.selected_objects[0].type == 'MESH')):
                filter = "mol_.*_shape"
                obj = context.selected_objects[0]
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        active = True

            layout.active = active

            row = layout.row()
            layout.prop(mcell.molecule_glyphs, "glyph")

            if (mcell.molecule_glyphs.status != ""):
                row = layout.row()
                row.label(text=mcell.molecule_glyphs.status, icon="ERROR")

            row = layout.row()
            if (len(context.selected_objects) == 0):
                row.label(text="Selected Molecule:  ")
            else:
                row.label(text="Selected Molecule:  %s" % (
                    context.selected_objects[0].name))

            row = layout.row()
            row.operator("mcell.set_molecule_glyph", text="Set Molecule Shape",
                         icon='MESH_ICOSPHERE')

