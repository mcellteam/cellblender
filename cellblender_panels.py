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


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#CellBlendereGUI Panels:
class MCELL_PT_project_settings(bpy.types.Panel):
    bl_label = "CellBlender Project Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.operator("mcell.select_mcell_binary",
                     text="Set Path to MCell Binary", icon='FILESEL')
        row = layout.row()
        row.label(
            text="MCell Binary: "+mcell.project_settings.mcell_binary)
        row = layout.row()
        row.operator("mcell.set_project_dir",
                     text="Set CellBlender Project Directory", icon='FILESEL')
        row = layout.row()
        row.label(
            text="Project Directory: "+mcell.project_settings.project_dir)
        row = layout.row()
        layout.prop(mcell.project_settings, "base_name")
        layout.separator()
        row = layout.row()


class MCELL_PT_export_project(bpy.types.Panel):
    bl_label = "Export Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.prop(mcell.export_project, "export_format")
        row = layout.row()
        row.operator("mcell.export_project", text="Export CellBlender Project",
                     icon='FILESEL')


class MCELL_PT_run_simulatin(bpy.types.Panel):
    bl_label = "Run Simulation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell
        main_mdl = ("%s.main.mdl" %
                    os.path.join(mcell.project_settings.project_dir,
                    mcell.project_settings.base_name))

        row = layout.row()

        # Only allow the simulation to be run if both an MCell binary and a
        # project dir have been selected. There also needs to be a main mdl
        # file present.
        if not mcell.project_settings.mcell_binary:
            row.label(text="Set an MCell binary", icon='ERROR')
        elif not mcell.project_settings.project_dir:
            row.label(text="Set a project directory", icon='ERROR')
        elif not os.path.isfile(main_mdl):
            row.label(text="Export the project", icon='ERROR')
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
            row = layout.row()
            row.operator("mcell.run_simulation", text="Run Simulation",
                         icon='COLOR_RED')


class MCELL_PT_model_objects(bpy.types.Panel):
    bl_label = "Model Objects"
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
        col.template_list("UI_UL_list", "model_objects", mcell.model_objects,
                          "object_list", mcell.model_objects,
                          "active_obj_index", rows=2)
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
class MCELL_PT_sim_control(bpy.types.Panel):
    bl_label = "Simulation Control"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
'''


class MCELL_PT_viz_results(bpy.types.Panel):
    bl_label = "Visualize Simulation Results"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        mcell = context.scene.mcell

        row = layout.row()
        row.operator("mcell.set_mol_viz_dir",
                     text="Set Molecule Viz Directory", icon="FILESEL")
        row = layout.row()
        row.label(text="Molecule Viz Directory: "+mcell.mol_viz.mol_file_dir)
        row = layout.row()
        row.label(text="Current Molecule File: "+mcell.mol_viz.mol_file_name)
        row = layout.row()
        row.template_list("UI_UL_list", "viz_results", mcell.mol_viz,
                          "mol_file_list", mcell.mol_viz, "mol_file_index",
                          rows=2)
        row = layout.row()
        layout.prop(mcell.mol_viz, "mol_viz_enable")
#        row = layout.row()
#        layout.prop(mcell.mol_viz, "render_and_save")

#        col = row.column(align=True)
#        col.operator("mcell.mol_viz_prev", icon="PLAY_REVERSE", text="")
#        col = row.column(align=True)
#        col.operator("mcell.mol_viz_set_index",
#                     text=str(mcell.mol_viz.mol_file_index))
#        col = row.column(align=True)
#        col.operator("mcell.mol_viz_next", icon="PLAY", text="")


'''
class MCELL_PT_utilities(bpy.types.Panel):
    bl_label = "Utilities"
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
    bl_label = "Object Selector"
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
    bl_label = "Mesh Analysis"
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
        row.label(text="Mesh Topology:")
        row = layout.row()
        row.label(text="      %s" % (mcell.meshalyzer.watertight))
        row = layout.row()
        row.label(text="      %s" % (mcell.meshalyzer.manifold))
        row = layout.row()
        row.label(text="      %s" % (mcell.meshalyzer.normal_status))


'''
class MCELL_PT_user_model_parameters(bpy.types.Panel):
    bl_label = "User-Defined Model Parameters"
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
    bl_label = "Model Initialization"
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
    bl_label = "Define and Visualize Partitions"
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


class MCELL_PT_define_molecules(bpy.types.Panel):
    bl_label = "Define Molecules"
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
        col.template_list("UI_UL_list", "define_molecules", mcell.molecules,
                          "molecule_list", mcell.molecules, "active_mol_index",
                          rows=2)
        col = row.column(align=True)
        col.operator("mcell.molecule_add", icon='ZOOMIN', text="")
        col.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
        if mcell.molecules.molecule_list:
            mol = mcell.molecules.molecule_list[
                mcell.molecules.active_mol_index]
            if mcell.molecules.status != "":
                row = layout.row()
                row.label(text=mcell.molecules.status, icon='ERROR')
            layout.prop(mol, "name")
            layout.prop(mol, "type")
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


class MCELL_PT_define_reactions(bpy.types.Panel):
    bl_label = "Define Reactions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.label(text="Defined Reactions:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "define_reactions", mcell.reactions,
                          "reaction_list", mcell.reactions, "active_rxn_index",
                          rows=2)
        col = row.column(align=True)
        col.operator("mcell.reaction_add", icon='ZOOMIN', text="")
        col.operator("mcell.reaction_remove", icon='ZOOMOUT', text="")
        if len(mcell.reactions.reaction_list) > 0:
            rxn = mcell.reactions.reaction_list[
                mcell.reactions.active_rxn_index]
            layout.prop(rxn, "reactants")
            layout.prop(rxn, "type")
            layout.prop(rxn, "products")
            layout.prop(rxn, "fwd_rate_str")
            if rxn.type == "reversible":
                layout.prop(rxn, "bkwd_rate_str")
            layout.prop(rxn, "rxn_name")

        if mcell.reactions.status != "":
            row = layout.row()
            row.label(text=mcell.reactions.status, icon='ERROR')


class MCELL_PT_define_surface_classes(bpy.types.Panel):
    bl_label = "Define Surface Classes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        surf_class = context.scene.mcell.surface_classes
        row = layout.row()
        row.label(text="Defined Surface Classes:", icon='FACESEL_HLT')
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "define_surf_class", surf_class,
                          "surf_class_list", surf_class,
                          "active_surf_class_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.surface_class_add", icon='ZOOMIN', text="")
        col.operator("mcell.surface_class_remove", icon='ZOOMOUT', text="")
        if len(surf_class.surf_class_list) > 0:
            active_surf_class = surf_class.surf_class_list[
                surf_class.active_surf_class_index]
            if surf_class.surf_class_status != "":
                row = layout.row()
                row.label(text=surf_class.surf_class_status, icon='ERROR')
            row = layout.row()
            row.prop(active_surf_class, "name")


class MCELL_PT_define_surface_class_properties(bpy.types.Panel):
    bl_label = "Define Surface Class Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell
        surf_class = mcell.surface_classes

        row = layout.row()
        if len(surf_class.surf_class_list) > 0:
            active_surf_class = surf_class.surf_class_list[
                surf_class.active_surf_class_index]
            row = layout.row()
            row.label(text="%s Properties:" % active_surf_class.name,
                      icon='FACESEL_HLT')
            row = layout.row()
            col = row.column()
            col.template_list("UI_UL_list", "define_surf_class_props",
                              active_surf_class, "surf_class_props_list",
                              active_surf_class,
                              "active_surf_class_props_index", rows=2)
            col = row.column(align=True)
            col.operator("mcell.surf_class_props_add", icon='ZOOMIN', text="")
            col.operator("mcell.surf_class_props_remove", icon='ZOOMOUT',
                         text="")
            if len(active_surf_class.surf_class_props_list) > 0:
                surf_class_props = active_surf_class.surf_class_props_list[
                    active_surf_class.active_surf_class_props_index]
                if surf_class.surf_class_props_status != "":
                    row = layout.row()
                    row.label(text=surf_class.surf_class_props_status,
                              icon='ERROR')
                layout.prop_search(surf_class_props, "molecule",
                                   mcell.molecules, "molecule_list",
                                   icon='FORCE_LENNARDJONES')
                layout.prop(surf_class_props, "surf_class_orient")
                layout.prop(surf_class_props, "surf_class_type")
                if (surf_class_props.surf_class_type == 'CLAMP_CONCENTRATION'):
                    layout.prop(surf_class_props, "clamp_value_str")
        else:
            row.label(text="Add a surface class")


class MCELL_PT_mod_surface_regions(bpy.types.Panel):
    bl_label = "Modify Surface Regions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        row = layout.row()
        row.label(text="Modified Surface Regions:", icon='FACESEL_HLT')
        row = layout.row()
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "mod_surf_regions", mod_surf_regions,
                          "mod_surf_regions_list", mod_surf_regions,
                          "active_mod_surf_regions_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.mod_surf_regions_add", icon='ZOOMIN', text="")
        col.operator("mcell.mod_surf_regions_remove", icon='ZOOMOUT', text="")
        if mod_surf_regions.status != "":
            row = layout.row()
            row.label(text=mod_surf_regions.status, icon='ERROR')
        if len(mod_surf_regions.mod_surf_regions_list) > 0:
            active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
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
                    layout.prop_search(active_mod_surf_regions, "region_name",
                                       regions, "region_list",
                                       icon='FACESEL_HLT')
                except KeyError:
                    pass


class MCELL_PT_molecule_release(bpy.types.Panel):
    bl_label = "Molecule Release/Placement"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.label(text="Release/Placement Sites:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "molecule_release",
                          mcell.release_sites, "mol_release_list",
                          mcell.release_sites, "active_release_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.release_site_add", icon='ZOOMIN', text="")
        col.operator("mcell.release_site_remove", icon='ZOOMOUT', text="")
        if len(mcell.release_sites.mol_release_list) > 0:
            rel = mcell.release_sites.mol_release_list[
                mcell.release_sites.active_release_index]
            if mcell.release_sites.status != "":
                row = layout.row()
                row.label(text=mcell.release_sites.status, icon='ERROR')
            layout.prop(rel, "name")
            layout.prop_search(rel, "molecule", mcell.molecules,
                               "molecule_list", text="Molecule:",
                               icon='FORCE_LENNARDJONES')
            if rel.molecule in mcell.molecules.molecule_list:
                if mcell.molecules.molecule_list[rel.molecule].type == '2D':
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
            layout.prop(rel, "quantity")
            if rel.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
                layout.prop(rel, "stddev")

            layout.prop(rel, "pattern")


class MCELL_PT_reaction_output_settings(bpy.types.Panel):
    bl_label = "Reaction Output Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.label(text="Reaction Data Output:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "reaction_output", mcell.rxn_output,
                          "rxn_output_list", mcell.rxn_output,
                          "active_rxn_output_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.rxn_output_add", icon='ZOOMIN', text="")
        col.operator("mcell.rxn_output_remove", icon='ZOOMOUT', text="")
        # Show molecule, object, and region options only if there is at least
        # one count statement.
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
                        layout.prop_search(rxn_output, "region_name", regions,
                                           "region_list", icon='FACESEL_HLT')
                    except KeyError:
                        pass
        if (mcell.rxn_output.status != ""):
            row = layout.row()
            row.label(text=mcell.rxn_output.status, icon='ERROR')


class MCELL_UL_visualization_export_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        layout.label(item.name)
        layout.prop(item, "export_viz", text="Export")


class MCELL_PT_visualization_output_settings(bpy.types.Panel):
    bl_label = "Visualization Output Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mcell = context.scene.mcell

        row = layout.row()
        row.label(text="Molecules To Visualize:",
                  icon='FORCE_LENNARDJONES')
        row.operator("mcell.toggle_viz_molecules", text="Toggle All")
        layout.template_list("MCELL_UL_visualization_export_list",
                             "viz_export", mcell.molecules, "molecule_list",
                             mcell.viz_output, "active_mol_viz_index", rows=2)
        layout.prop(mcell.viz_output, "all_iterations")
        if mcell.viz_output.all_iterations is False:
            row = layout.row(align=True)
            row.prop(mcell.viz_output, "start")
            row.prop(mcell.viz_output, "end")
            row.prop(mcell.viz_output, "step")


class MCELL_PT_define_surface_regions(bpy.types.Panel):
    bl_label = "Define Surface Regions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj_regs = context.object.mcell.regions
        active_obj = context.active_object

        row = layout.row()
        row.label(text="Defined Regions:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "define_surf_regions", obj_regs,
                          "region_list", obj_regs, "active_reg_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.region_add", icon='ZOOMIN', text="")
        col.operator("mcell.region_remove", icon='ZOOMOUT', text="")
        row = layout.row()
        if (obj_regs.status != ""):
            row = layout.row()
            row.label(text=obj_regs.status, icon='ERROR')
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
    bl_label = "Molecule Shape"
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
