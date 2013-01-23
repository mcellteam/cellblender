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
        mc = context.scene.mcell

        row = layout.row()
        row.operator("mcell.set_project_dir",
                     text="Set CellBlender Project Directory", icon="FILESEL")
        row = layout.row()
        row.label(text="Project Directory: "+mc.project_settings.project_dir)
        row = layout.row()
        layout.prop(mc.project_settings, "base_name")
        layout.separator()
        row = layout.row()
        row.label(text="Export Project: "+mc.project_settings.base_name)
        row = layout.row()
        layout.prop(mc.project_settings, "export_format")
        row = layout.row()
        row.operator("mcell.export_project", text="Export CellBlender Project",
                     icon="FILESEL")


class MCELL_PT_model_objects(bpy.types.Panel):
    bl_label = "Model Objects"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        mc = context.scene.mcell

        row = layout.row()
        row.label(text="Model Objects:", icon='MESH_ICOSPHERE')
        row = layout.row()
        col = row.column()
        col.template_list(mc.model_objects, "object_list", mc.model_objects,
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
        mc = context.scene.mcell

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

        mc = context.scene.mcell

        row = layout.row()
        row.operator("mcell.set_mol_viz_dir",
                     text="Set Molecule Viz Directory", icon="FILESEL")
        row = layout.row()
        row.label(text="Molecule Viz Directory: "+mc.mol_viz.mol_file_dir)
        row = layout.row()
        row.label(text="Current Molecule File: "+mc.mol_viz.mol_file_name)
        row = layout.row()
        row.template_list(mc.mol_viz, "mol_file_list", mc.mol_viz,
                          "mol_file_index", rows=2)
        row = layout.row()
        layout.prop(mc.mol_viz, "mol_viz_enable")
#        row = layout.row()
#        layout.prop(mc.mol_viz, "render_and_save")

#        col = row.column(align=True)
#        col.operator("mcell.mol_viz_prev", icon="PLAY_REVERSE", text="")
#        col = row.column(align=True)
#        col.operator("mcell.mol_viz_set_index",
#                     text=str(mc.mol_viz.mol_file_index))
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
        mc = context.scene.mcell

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
        mc = context.scene.mcell

        layout.prop(mc.object_selector, "filter", text="Object Filter:")
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
        mc = context.scene.mcell

        row = layout.row()
        row.operator("mcell.meshalyzer", text="Analyze Mesh",
                     icon="MESH_ICOSPHERE")

        if (mc.meshalyzer.status != ''):
            row = layout.row()
            row.label(text=mc.meshalyzer.status, icon="ERROR")
        row = layout.row()
        row.label(text="Object Name: %s" % (mc.meshalyzer.object_name))
        row = layout.row()
        row.label(text="Vertices: %d" % (mc.meshalyzer.vertices))
        row = layout.row()
        row.label(text="Edges: %d" % (mc.meshalyzer.edges))
        row = layout.row()
        row.label(text="Faces: %d" % (mc.meshalyzer.faces))
        row = layout.row()
        row.label(text="Surface Area: %.5g" % (mc.meshalyzer.area))
        row = layout.row()
        row.label(text="Volume: %.5g" % (mc.meshalyzer.volume))

        row = layout.row()
        row.label(text="Mesh Topology:")
        row = layout.row()
        row.label(text="      %s" % (mc.meshalyzer.watertight))
        row = layout.row()
        row.label(text="      %s" % (mc.meshalyzer.manifold))
        row = layout.row()
        row.label(text="      %s" % (mc.meshalyzer.normal_status))


'''
class MCELL_PT_user_model_parameters(bpy.types.Panel):
    bl_label = "User-Defined Model Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mc = context.scene.mcell

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
        mc = context.scene.mcell

        layout.prop(mc.initialization, "iterations")
        layout.prop(mc.initialization, "time_step_str")
        if (mc.initialization.status != ''):
            row = layout.row()
            row.label(text=mc.initialization.status, icon="ERROR")


class MCELL_PT_define_molecules(bpy.types.Panel):
    bl_label = "Define Molecules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        mc = context.scene.mcell

        row = layout.row()
        row.label(text="New Molecule:", icon='FORCE_LENNARDJONES')
        mol = mc.molecules.template_molecule
        if mc.molecules.status.endswith('successful'):
            row = layout.row()
            row.label(text=mc.molecules.status, icon='FILE_TICK')
        elif mc.molecules.status:
            row = layout.row()
            row.label(text=mc.molecules.status, icon='ERROR')
        layout.prop(mol, "name")
        layout.prop(mol, "type")
        layout.prop(mol, "diffusion_constant_str")
        if mc.molecules.hide:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.prop(mc.molecules, "hide", icon='TRIA_RIGHT',
                     text='Advanced Options', emboss=False)
        else:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.prop(mc.molecules, "hide", icon='TRIA_DOWN',
                     text='Advanced Options', emboss=False)
            layout.prop(mol, "target_only")
            layout.prop(mol, "custom_time_step_str")
            layout.prop(mol, "custom_space_step_str")
        row = layout.row()
        row = layout.row(align=True)
        row.operator("mcell.molecule_add", text="Add to List")
        row.operator("mcell.molecule_update", text="Update List")
        layout.separator()
        row = layout.row()
        row.label(text="Defined Molecules:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        row.template_list(mc.molecules, "molecule_list", mc.molecules,
                          "active_mol_index", rows=2)
        row = layout.row(align=True)
        row.operator("mcell.molecule_remove", text="Remove from List")


class MCELL_PT_define_reactions(bpy.types.Panel):
    bl_label = "Define Reactions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mc = context.scene.mcell

        row = layout.row()
        row.label(text="Defined Reactions:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list(mc.reactions, "reaction_list", mc.reactions,
                          "active_rxn_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.reaction_add", icon='ZOOMIN', text="")
        col.operator("mcell.reaction_remove", icon='ZOOMOUT', text="")
        if len(mc.reactions.reaction_list) > 0:
            rxn = mc.reactions.reaction_list[mc.reactions.active_rxn_index]
            layout.prop(rxn, "reactants")
            layout.prop(rxn, "type")
            layout.prop(rxn, "products")
            layout.prop(rxn, "fwd_rate_str")
            if rxn.type == "reversible":
                layout.prop(rxn, "bkwd_rate_str")
            layout.prop(rxn, "rxn_name")

        if mc.reactions.status != '':
            row = layout.row()
            row.label(text=mc.reactions.status, icon="ERROR")


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
        col.template_list(surf_class, "surf_class_list", surf_class,
                          "active_surf_class_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.surface_class_add", icon='ZOOMIN', text="")
        col.operator("mcell.surface_class_remove", icon='ZOOMOUT', text="")
        if len(surf_class.surf_class_list) > 0:
            active_surf_class = surf_class.surf_class_list[
                surf_class.active_surf_class_index]
            if surf_class.surf_class_status != '':
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
        mc = context.scene.mcell
        surf_class = mc.surface_classes

        row = layout.row()
        if len(surf_class.surf_class_list) > 0:
            active_surf_class = surf_class.surf_class_list[
                surf_class.active_surf_class_index]
            row = layout.row()
            row.label(text="%s Properties:" % active_surf_class.name,
                      icon='FACESEL_HLT')
            row = layout.row()
            col = row.column()
            col.template_list(active_surf_class, "surf_class_props_list",
                              active_surf_class,
                              "active_surf_class_props_index",
                              rows=2)
            col = row.column(align=True)
            col.operator("mcell.surf_class_props_add", icon='ZOOMIN', text="")
            col.operator("mcell.surf_class_props_remove", icon='ZOOMOUT',
                         text="")
            if len(active_surf_class.surf_class_props_list) > 0:
                surf_class_props = active_surf_class.surf_class_props_list[
                    active_surf_class.active_surf_class_props_index]
                if surf_class.surf_class_props_status != '':
                    row = layout.row()
                    row.label(text=surf_class.surf_class_props_status,
                              icon='ERROR')
                layout.prop_search(surf_class_props, 'molecule', mc.molecules,
                                   "molecule_list")
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
        mc = context.scene.mcell
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        row = layout.row()
        row.label(text="Modified Surface Regions:", icon='FACESEL_HLT')
        row = layout.row()
        row = layout.row()
        col = row.column()
        col.template_list(mod_surf_regions, "mod_surf_regions_list",
                          mod_surf_regions, "active_mod_surf_regions_index",
                          rows=2)
        col = row.column(align=True)
        col.operator("mcell.mod_surf_regions_add", icon='ZOOMIN', text="")
        col.operator("mcell.mod_surf_regions_remove", icon='ZOOMOUT', text="")
        if mod_surf_regions.status != '':
            row = layout.row()
            row.label(text=mod_surf_regions.status, icon='ERROR')
        if len(mod_surf_regions.mod_surf_regions_list) > 0:
            active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
                mod_surf_regions.active_mod_surf_regions_index]
            row = layout.row()
            row.prop_search(active_mod_surf_regions, "surf_class_name",
                            mc.surface_classes, "surf_class_list")
            row = layout.row()
            row.prop_search(active_mod_surf_regions, "object_name",
                            mc.model_objects, "object_list")
            if active_mod_surf_regions.object_name:
                try:
                    regions = bpy.data.objects[
                        active_mod_surf_regions.object_name].mcell.regions
                    layout.prop_search(active_mod_surf_regions, "region_name",
                                       regions, "region_list")
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
        mc = context.scene.mcell

        row = layout.row()
        row.label(text="Release/Placement Sites:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list(mc.release_sites, "mol_release_list",
                          mc.release_sites, "active_release_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.release_site_add", icon='ZOOMIN', text="")
        col.operator("mcell.release_site_remove", icon='ZOOMOUT', text="")
        if len(mc.release_sites.mol_release_list) > 0:
            rel = mc.release_sites.mol_release_list[
                mc.release_sites.active_release_index]
            if mc.release_sites.status != '':
                row = layout.row()
                row.label(text=mc.release_sites.status, icon='ERROR')
            layout.prop(rel, "name")
            layout.prop_search(rel, 'molecule', mc.molecules, "molecule_list",
                               text='Molecule:')
            if rel.molecule in mc.molecules.molecule_list:
                if mc.molecules.molecule_list[rel.molecule].type == '2D':
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
        mc = context.scene.mcell

        layout.prop(mc.rxn_output, "include")


class MCELL_PT_visualization_output_settings(bpy.types.Panel):
    bl_label = "Visualization Output Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        mc = context.scene.mcell

        layout.prop(mc.viz_output, "include")


class MCELL_PT_define_surface_regions(bpy.types.Panel):
    bl_label = "Define Surface Regions"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        obj_regs = context.object.mcell.regions
        aobj = context.active_object

        row = layout.row()
        row.label(text="Defined Regions:", icon='FORCE_LENNARDJONES')
        row = layout.row()
        col = row.column()
        col.template_list(obj_regs, "region_list", obj_regs,
                          "active_reg_index", rows=2)
        col = row.column(align=True)
        col.operator("mcell.region_add", icon='ZOOMIN', text="")
        col.operator("mcell.region_remove", icon='ZOOMOUT', text="")
        row = layout.row()
        if (obj_regs.status != ''):
            row = layout.row()
            row.label(text=obj_regs.status, icon="ERROR")
        if len(obj_regs.region_list) > 0:
            reg = obj_regs.region_list[obj_regs.active_reg_index]
            layout.prop(reg, "name")
        if aobj.mode == 'EDIT':
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
        mc = context.scene.mcell

        active = False
        if ((len(context.selected_objects) == 1) and
                (context.selected_objects[0].type == 'MESH')):
            filter = 'mol_.*_shape'
            obj = context.selected_objects[0]
            m = re.match(filter, obj.name)
            if m is not None:
                if m.end() == len(obj.name):
                    active = True

        layout.active = active

        row = layout.row()
        layout.prop(mc.molecule_glyphs, "glyph")

        if (mc.molecule_glyphs.status != ''):
            row = layout.row()
            row.label(text=mc.molecule_glyphs.status, icon="ERROR")

        row = layout.row()
        if (len(context.selected_objects) == 0):
            row.label(text="Selected Molecule:  ")
        else:
            row.label(text="Selected Molecule:  %s" % (
                context.selected_objects[0].name))

        row = layout.row()
        row.operator("mcell.set_molecule_glyph", text="Set Molecule Shape",
                     icon="MESH_ICOSPHERE")
