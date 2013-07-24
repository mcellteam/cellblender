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


# python imports
import re
import os

# cellblender imports
import cellblender


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


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

        row = layout.row()
        row.prop(mcell.cellblender_preferences, "decouple_export_run")
        row = layout.row()
        row.prop(mcell.cellblender_preferences, "filter_invalid")
        layout.separator()
        row = layout.row()
        row.operator("wm.save_homefile", text="Save Startup File",
                     icon='SAVE_PREFS')


class MCELL_PT_project_settings(bpy.types.Panel):
    bl_label = "CellBlender - Project Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.label(text="CellBlender ID: "+cellblender.cellblender_info[
            'cellblender_source_sha1'])

        row = layout.row()
        row.operator("mcell.set_mcell_binary",
                     text="Set Path to MCell Binary", icon='FILESEL')
        row = layout.row()
        mcell_binary = mcell.project_settings.mcell_binary
        if not mcell_binary:
            # Using pin icon to be consistent with project directory, but maybe
            # we should use error icon to be consistent with other sections.
            row.label("MCell Binary not set", icon='UNPINNED')
        elif not mcell.project_settings.mcell_binary_valid:
            row.label("MCell File/Permissions Error: " +
                mcell.project_settings.mcell_binary, icon='ERROR')
        else:
            row.label(
                text="MCell Binary: "+mcell.project_settings.mcell_binary,
                icon='FILE_TICK')
        #row.operator("mcell.set_project_dir",
        #             text="Set CellBlender Project Directory", icon='FILESEL')
        #row = layout.row()
        # mcell.project_settings.project_dir = os.path.dirname(
        #     bpy.data.filepath)
        # row.label(text="Project Directory: " +
        #           mcell.project_settings.project_dir)

        row = layout.row()
        if not bpy.data.filepath:
            row.label(
                text="No Project Directory: Use File/Save or File/SaveAs",
                icon='UNPINNED')
        else:
            row.label(
                text="Project Directory: "+os.path.dirname(bpy.data.filepath),
                icon='FILE_TICK')

        row = layout.row()
        layout.prop(context.scene, "name", text="Project Base Name")


#class MCELL_PT_scratch(bpy.types.Panel):
#    bl_label = "CellBlender - Scratch Panel (testing)"
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "scene"
#    bl_options = {'DEFAULT_CLOSED'}
#
#    def draw(self, context):
#        layout = self.layout
#        mcell = context.scene.mcell
#
#        row = layout.row()
#        col = row.column(align=True)
#        col.prop(mcell.scratch_settings, "show_all_icons")
#        col = row.column(align=True)
#        col.prop(mcell.scratch_settings, "print_all_icons")
#
#        if mcell.scratch_settings.show_all_icons:
#            all_icons = bpy.types.UILayout.bl_rna.functions[
#                'prop'].parameters['icon'].enum_items.keys()
#            layout.separator()
#            row = layout.row()
#            for icon in all_icons:
#                row = layout.row()
#                row.label(icon=icon, text=icon)
#
#        if mcell.scratch_settings.print_all_icons:
#            all_icons = bpy.types.UILayout.bl_rna.functions[
#                'prop'].parameters['icon'].enum_items.keys()
#            print("Icon list has ", len(all_icons), "icons")
#            print("Icon names:")
#            print(all_icons)
#            # mcell.scratch_settings.print_all_icons = False
#            # AttributeError: Writing to ID classes in this context is not
#            # allowed: Scene, Scene datablock, error setting
#            # MCellScratchPanelProperty.print_all_icons

#class MCELL_PT_export_project(bpy.types.Panel):
#    bl_label = "CellBlender - Export Project"
#    bl_space_type = "PROPERTIES"
#    bl_region_type = "WINDOW"
#    bl_context = "scene"
#    bl_options = {'DEFAULT_CLOSED'}
#
#    def draw(self, context):
#        layout = self.layout
#        mcell = context.scene.mcell
#
#        row = layout.row()
#        if not bpy.data.filepath:
#            row.label(text="Save the blend file", icon='ERROR')
#        else:
#            row.prop(mcell.export_project, "export_format")
#            row = layout.row()
#            row.operator("mcell.export_project",
#                         text="Export CellBlender Project", icon='EXPORT')

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


def project_files_path():
    ''' Consolidate the creation of the path to the project files'''
    # DUPLICATED FUNCTION ... This is the same function as in
    # cellblender_operators.py
    # print ( "DUPLICATED FUNCTION ... PLEASE FIX" )
    filepath = os.path.dirname(bpy.data.filepath)
    filepath, dot, blend = bpy.data.filepath.rpartition(os.path.extsep)
    filepath = filepath + "_files"
    filepath = os.path.join(filepath, "mcell")
    return filepath


class MCELL_PT_run_simulation(bpy.types.Panel):
    bl_label = "CellBlender - Run Simulation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell
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
        if not mcell.project_settings.mcell_binary:
            row.label(text="Set an MCell binary", icon='ERROR')
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


class MCELL_PT_viz_results(bpy.types.Panel):
    bl_label = "CellBlender - Visualize Simulation Results"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        mcell = context.scene.mcell

        row = layout.row()
        #row = layout.row()
        #row.operator("mcell.set_mol_viz_dir",
        #             text="Set Molecule Viz Directory", icon="FILESEL")
        row.operator(
            "mcell.read_viz_data", text="Read Viz Data",
            icon='IMPORT')
        row = layout.row()
        row.label(text="Molecule Viz Directory: "+mcell.mol_viz.mol_file_dir,
                  icon='FILE_FOLDER')
        row = layout.row()
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

        row = layout.row()
        row.label(text="Model Objects:", icon='MESH_ICOSPHERE')
        row = layout.row()
        col = row.column()
        col.template_list("MCELL_UL_model_objects", "model_objects",
                          mcell.model_objects, "object_list",
                          mcell.model_objects, "active_obj_index", rows=2)
        col = row.column(align=True)
#        col.active = (len(context.selected_objects) == 1)
        col.operator("mcell.model_objects_add", icon='ZOOMIN', text="")
        col.operator("mcell.model_objects_remove", icon='ZOOMOUT', text="")
#        row = layout.row()
#        sub = row.row(align=True)
#        sub.operator("mcell.model_objects_include", text="Include")
#        sub = row.row(align=True)
#        sub.operator("mcell.model_objects_select", text="Select")
#        sub.operator("mcell.model_objects_deselect", text="Deselect")

'''
class MCELL_PT_utilities(bpy.types.Panel):
    bl_label = "CellBlender - Utilities"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
#        row.operator("mcell.vertex_groups_to_regions",
#                     text="Convert Vertex Group to Region")
'''


class MCELL_PT_object_selector(bpy.types.Panel):
    bl_label = "CellBlender - Object Selector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        layout.prop(mcell.object_selector, "filter", text="Object Filter:")
        row = layout.row(align=True)
        row.operator("mcell.select_filtered", text="Select Filtered")
        row.operator("mcell.deselect_filtered", text="Deselect Filtered")


class MCELL_PT_meshalyzer(bpy.types.Panel):
    bl_label = "CellBlender - Mesh Analysis"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        row = layout.row()
        row.operator("mcell.meshalyzer", text="Analyze Mesh",
                     icon='MESH_ICOSPHERE')

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
        row.label(text="Volume: %.5g" % (mcell.meshalyzer.volume))
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

        layout.prop(mcell.initialization, "iterations")
        layout.prop(mcell.initialization, "time_step_str")

        # Advanced Options
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if mcell.initialization.advanced:
            row.prop(mcell.initialization, "advanced", icon='TRIA_DOWN',
                     text="Advanced Options", emboss=False)
            row = box.row()
            row.prop(mcell.initialization, "time_step_max_str")
            row = box.row()
            row.prop(mcell.initialization, "space_step_str")
            row = box.row()
            row.prop(mcell.initialization, "interaction_radius_str")
            row = box.row()
            row.prop(mcell.initialization, "radial_directions_str")
            row = box.row()
            row.prop(mcell.initialization, "radial_subdivisions_str")
            row = box.row()
            row.prop(mcell.initialization, "vacancy_search_distance_str")
            row = box.row()
            row.prop(mcell.initialization, "surface_grid_density")
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

############### DB: The following to classes are included to create a parameter input panel: only relevant for BNG, SBML or other model import #################

class MCELL_UL_check_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                 active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')
	    
  
class MCELL_PT_define_parameters(bpy.types.Panel):
    bl_label = "CellBlender - Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

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
                par = mcell.parameters.parameter_list[
                    mcell.parameters.active_par_index]
                layout.prop(par, "name")
                layout.prop(par, "value")
                layout.prop(par, "unit")
                layout.prop(par, "type")
        else:
            row.label(text="No imported/defined parameter found", icon='ERROR')
#########################################################################################################################################

class MCELL_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_molecules(bpy.types.Panel):
    bl_label = "CellBlender - Define Molecules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout

        mcell = context.scene.mcell

        row = layout.row()
        row.label(text="Defined Molecules:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list("MCELL_UL_check_molecule", "define_molecules",
                          mcell.molecules, "molecule_list", mcell.molecules,
                          "active_mol_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.molecule_add", icon='ZOOMIN', text="")
        col.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
        if mcell.molecules.molecule_list:
            mol = mcell.molecules.molecule_list[
                mcell.molecules.active_mol_index]
            layout.prop(mol, "name")
            layout.prop(mol, "type")
            if (mol.diffusion_constant_expr != "0"): #DB: This is added for diffusion constant to take expression; not sure if it has other implications 
                layout.prop(mol, "diffusion_constant_expr")
            else:
                layout.prop(mol, "diffusion_constant_str")

            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if not mcell.molecules.advanced:
                row.prop(mcell.molecules, "advanced", icon='TRIA_RIGHT',
                         text="Advanced Options", emboss=False)
            else:
                row.prop(mcell.molecules, "advanced", icon='TRIA_DOWN',
                         text="Advanced Options", emboss=False)
                row = box.row()
                row.prop(mol, "target_only")
                row = box.row()
                row.prop(mol, "custom_time_step_str")
                row = box.row()
                row.prop(mol, "custom_space_step_str")


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
                if (rxn.fwd_rate_expr != "0"):
                    layout.prop(rxn, "fwd_rate_expr")
                else:
                    layout.prop(rxn, "fwd_rate_str")
                if rxn.type == "reversible":
                    layout.prop(rxn, "bkwd_rate_str")
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

        row = layout.row()
        if mcell.molecules.molecule_list:
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
                                   "molecule_list", text="Molecule:",
                                   icon='FORCE_LENNARDJONES')
                if rel.molecule in mcell.molecules.molecule_list:
                    if mcell.molecules.molecule_list[
                            rel.molecule].type == '2D':
                        layout.prop(rel, "orient")
                layout.prop(rel, "shape")
                if ((rel.shape == 'CUBIC') | (rel.shape == 'SPHERICAL') |
                        (rel.shape == 'SPHERICAL SHELL')):
                    layout.prop(rel, "location")
                    layout.prop(rel, "diameter")
                if rel.shape == 'OBJECT':
                    layout.prop(rel, "object_expr")

                layout.prop(rel, "probability")
                layout.prop(rel, "quantity_type")
                if rel.quantity_expr != "0":
                   layout.prop(rel, "quantity_expr")
                else:
                   layout.prop(rel, "quantity")
                if rel.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
                    layout.prop(rel, "stddev")

                layout.prop(rel, "pattern")
        else:
            row.label(text="Define at least one molecule", icon='ERROR')


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
                layout.prop_search(
                    rxn_output, "molecule_name", mcell.molecules,
                    "molecule_list", icon='FORCE_LENNARDJONES')
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

        row = layout.row()
        if mcell.molecules.molecule_list:
            row.label(text="Molecules To Visualize:",
                      icon='FORCE_LENNARDJONES')
            row.operator("mcell.toggle_viz_molecules", text="Toggle All")
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


class MCELL_UL_check_region(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_define_surface_regions(bpy.types.Panel):
    bl_label = "CellBlender - Define Surface Regions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj_regs = context.object.mcell.regions
        active_obj = context.active_object

        if active_obj.type == 'MESH':
            row = layout.row()
            row.label(text="Defined Regions:", icon='FORCE_LENNARDJONES')
            row = layout.row()
            col = row.column()
            col.template_list("MCELL_UL_check_region", "define_surf_regions",
                              obj_regs, "region_list", obj_regs,
                              "active_reg_index", rows=2)
            col = row.column(align=True)
            col.operator("mcell.region_add", icon='ZOOMIN', text="")
            col.operator("mcell.region_remove", icon='ZOOMOUT', text="")
            row = layout.row()
            if len(obj_regs.region_list) > 0:
                reg = obj_regs.region_list[obj_regs.active_reg_index]
                layout.prop(reg, "name")
            if active_obj.mode == 'EDIT':
                row = layout.row()
                sub = row.row(align=True)
                sub.operator("mcell.region_faces_assign", text="Assign")
                sub.operator("mcell.region_faces_remove", text="Remove")
                sub = row.row(align=True)
                sub.operator("mcell.region_faces_select", text="Select")
                sub.operator("mcell.region_faces_deselect", text="Deselect")


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

