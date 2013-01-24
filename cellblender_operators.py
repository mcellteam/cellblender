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
This script stores the operators for CellBlender. As such, it is responsible
for what the buttons do when pressed (amongst other things).

"""

# blender imports
import bpy
from bpy.app.handlers import persistent
import mathutils

# python imports
import array
import glob
import os
import random
import re


# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


#CellBlender Operators:
class MCELL_OT_region_add(bpy.types.Operator):
    bl_idname = "mcell.region_add"
    bl_label = "Add New Surface Region"
    bl_description = "Add a new surface region to an object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mc_obj = context.object.mcell
        mc_obj.regions.region_list.add()
        mc_obj.regions.active_reg_index = len(mc_obj.regions.region_list)-1
        mc_obj.regions.region_list[
            mc_obj.regions.active_reg_index].name = 'Region'
        return {'FINISHED'}


class MCELL_OT_region_remove(bpy.types.Operator):
    bl_idname = "mcell.region_remove"
    bl_label = "Remove Surface Region"
    bl_description = "Remove selected surface region from object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mc_obj = context.object.mcell
        mc_obj.regions.region_list.remove(mc_obj.regions.active_reg_index)
        mc_obj.regions.active_reg_index -= 1
        if (mc_obj.regions.active_reg_index < 0):
            mc_obj.regions.active_reg_index = 0

        if len(mc_obj.regions.region_list) > 0:
            check_region(self, context)
        else:
            mc_obj.regions.status = ''

        return {'FINISHED'}


def check_region(self, context):
    """Checks for duplicate or illegal region name"""

    mc_obj = context.object.mcell
    reg_list = mc_obj.regions.region_list
    reg = reg_list[mc_obj.regions.active_reg_index]

    status = ''

    # Check for duplicate region name
    reg_keys = reg_list.keys()
    if reg_keys.count(reg.name) > 1:
        status = 'Duplicate region: %s' % (reg.name)

    # Check for illegal names (Starts with a letter. No special characters)
    reg_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(reg_filter, reg.name)
    if m is None:
        status = 'Region name error: %s' % (reg.name)

    mc_obj.regions.status = status

    return


class MCELL_OT_region_faces_assign(bpy.types.Operator):
    bl_idname = "mcell.region_faces_assign"
    bl_label = "Assign Selected Faces To Surface Region"
    bl_description = "Assign selected faces to surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        aobj = context.active_object
        obj_regs = aobj.mcell.regions
        if (aobj.data.total_face_sel > 0):
            if not aobj.data.get('mcell'):
                aobj.data['mcell'] = {}
            if not aobj.data['mcell'].get('regions'):
                aobj.data['mcell']['regions'] = {}
            reg = obj_regs.region_list[obj_regs.active_reg_index]
            if not aobj.data['mcell']['regions'].get(reg.name):
                aobj.data['mcell']['regions'][reg.name] = []
            mesh = aobj.data
            face_set = set([])
            for f in aobj.data['mcell']['regions'][reg.name]:
                face_set.add(f)
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    face_set.add(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            reg_faces = list(face_set)
            reg_faces.sort()
            aobj.data['mcell']['regions'][reg.name] = reg_faces

#        obj_regs = aobj.mcell.regions
#        reg = obj_regs.region_list[obj_regs.active_reg_index]
#        mesh = aobj.data
#        for f in mesh.polygons:
#            if f.select:
#                reg.faces.add()
#                reg.active_face_index = len(reg.faces)-1
#                reg.faces[reg.active_face_index].index = f.index

        return {'FINISHED'}


class MCELL_OT_region_faces_remove(bpy.types.Operator):
    bl_idname = "mcell.region_faces_remove"
    bl_label = "Remove Selected Faces From Surface Region"
    bl_description = "Remove selected faces from surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        aobj = context.active_object
        obj_regs = aobj.mcell.regions
        if (aobj.data.total_face_sel > 0):
            if not aobj.data.get('mcell'):
                aobj.data['mcell'] = {}
            if not aobj.data['mcell'].get('regions'):
                aobj.data['mcell']['regions'] = {}
            reg = obj_regs.region_list[obj_regs.active_reg_index]
            if not aobj.data['mcell']['regions'].get(reg.name):
                aobj.data['mcell']['regions'][reg.name] = []
            mesh = aobj.data
            face_set = set(aobj.data['mcell']['regions'][reg.name].to_list())
            bpy.ops.object.mode_set(mode='OBJECT')
            for f in mesh.polygons:
                if f.select:
                    if f.index in face_set:
                        face_set.remove(f.index)
            bpy.ops.object.mode_set(mode='EDIT')

            reg_faces = list(face_set)
            reg_faces.sort()
            aobj.data['mcell']['regions'][reg.name] = reg_faces

        return {'FINISHED'}


class MCELL_OT_region_faces_select(bpy.types.Operator):
    bl_idname = "mcell.region_faces_select"
    bl_label = "Select Faces of Selected Surface Region"
    bl_description = "Select faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        aobj = context.active_object
        obj_regs = aobj.mcell.regions
        if not aobj.data.get('mcell'):
            aobj.data['mcell'] = {}
        if not aobj.data['mcell'].get('regions'):
            aobj.data['mcell']['regions'] = {}
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        if not aobj.data['mcell']['regions'].get(reg.name):
            aobj.data['mcell']['regions'][reg.name] = []
        mesh = aobj.data
        face_set = set(aobj.data['mcell']['regions'][reg.name].to_list())
        bpy.ops.object.mode_set(mode='OBJECT')
        msm = context.tool_settings.mesh_select_mode[0:]
        context.tool_settings.mesh_select_mode = [False, False, True]
        for f in face_set:
            mesh.polygons[f].select = True
        bpy.ops.object.mode_set(mode='EDIT')

        context.tool_settings.mesh_select_mode = msm
        return {'FINISHED'}


class MCELL_OT_region_faces_deselect(bpy.types.Operator):
    bl_idname = "mcell.region_faces_deselect"
    bl_label = "Deselect Faces of Selected Surface Region"
    bl_description = "Deselect faces of selected surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        aobj = context.active_object
        obj_regs = aobj.mcell.regions
        if not aobj.data.get('mcell'):
            aobj.data['mcell'] = {}
        if not aobj.data['mcell'].get('regions'):
            aobj.data['mcell']['regions'] = {}
        reg = obj_regs.region_list[obj_regs.active_reg_index]
        if not aobj.data['mcell']['regions'].get(reg.name):
            aobj.data['mcell']['regions'][reg.name] = []
        mesh = aobj.data
        face_set = set(aobj.data['mcell']['regions'][reg.name].to_list())
        bpy.ops.object.mode_set(mode='OBJECT')
        msm = context.tool_settings.mesh_select_mode[0:]
        context.tool_settings.mesh_select_mode = [False, False, True]
        for f in face_set:
            mesh.polygons[f].select = False
        bpy.ops.object.mode_set(mode='EDIT')

        context.tool_settings.mesh_select_mode = msm
        return {'FINISHED'}


class MCELL_OT_vertex_groups_to_regions(bpy.types.Operator):
    bl_idname = "mcell.vertex_groups_to_regions"
    bl_label = "Convert Vertex Groups of Selected Objects to Regions"
    bl_description = "Convert Vertex Groups to Regions"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        sobjs = context.selected_objects

        # For each selected object:
        for obj in sobjs:
            print(obj.name)
            scn.objects.active = obj
            obj.select = True
            obj_regs = obj.mcell.regions
            vgs = obj.vertex_groups

            # If there are vertex groups to convert:
            if (len(vgs) > 0):
                mesh = obj.data

                # For each vertex group:
                for vg in vgs:

                    # Deselect the whole mesh:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')

                    # Select the vertex group:
                    print(vg.name)
                    bpy.ops.object.vertex_group_set_active(group=vg.name)
                    bpy.ops.object.vertex_group_select()

                    # If there are selected faces:
                    if (mesh.total_face_sel > 0):
                        print('  vg faces: %d' % (mesh.total_face_sel))

                        # Setup mesh regions IDProp if necessary:
                        if not mesh.get('mcell'):
                            mesh['mcell'] = {}
                        if not mesh['mcell'].get('regions'):
                            mesh['mcell']['regions'] = {}

                        # look for vg.name in region_list and add if not found:
                        # method 1:
                        if (obj_regs.region_list.find(vg.name) == -1):
                            bpy.ops.mcell.region_add()
                            reg = obj_regs.region_list[
                                obj_regs.active_reg_index]
                            reg.name = vg.name
                        reg = obj_regs.region_list[vg.name]

                        # append faces in vertex group to faces in region:
                        # retreive or create region on mesh:
                        if not mesh['mcell']['regions'].get(vg.name):
                            mesh['mcell']['regions'][reg.name] = []
                        face_set = set([])
                        for f in mesh['mcell']['regions'][reg.name]:
                            face_set.add(f)
                        print('  reg faces 0: %d' % (len(face_set)))
                        bpy.ops.object.mode_set(mode='OBJECT')
                        for f in mesh.polygons:
                            if f.select:
                                face_set.add(f.index)
                        bpy.ops.object.mode_set(mode='EDIT')
                        reg_faces = list(face_set)
                        reg_faces.sort()
                        print('  reg faces 1: %d' % (len(reg_faces)))
                        mesh['mcell']['regions'][reg.name] = reg_faces
                        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class MCELL_OT_molecule_add_template(bpy.types.Operator):
    bl_idname = "mcell.molecule_add_template"
    bl_label = "Add Template Molecule"
    bl_description = "Add a new template molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        # This flag makes the template fields visible in cellblender_panels
        mcell.molecules.add_template_molecule = True
        mcell.molecules.status = ''

        return {'FINISHED'}


class MCELL_OT_molecule_cancel(bpy.types.Operator):
    bl_idname = "mcell.molecule_cancel"
    bl_label = "Cancel Template Molecule"
    bl_description = "Cancel molecule update or new template molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell

        reset_template_molecule(self, context)
        # These flags hides the template fields in cellblender_panels
        mcell.molecules.add_template_molecule = False
        mcell.molecules.list_selected = False
        mcell.molecules.status = ''

        return {'FINISHED'}


class MCELL_OT_molecule_add(bpy.types.Operator):
    bl_idname = "mcell.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        template_molecule = mcell.molecules.template_molecule
        molecule_list = mcell.molecules.molecule_list

        check_all_molecule_status(self, context, check_duplicate_molecule_add)

        if not mcell.molecules.status:
            molecule_list.add()
            mcell.molecules.active_mol_index = len(
                mcell.molecules.molecule_list)-1
            active_mol_index = mcell.molecules.active_mol_index
            active_molecule = molecule_list[active_mol_index]
            copy_molecule_properties(self, template_molecule, active_molecule)
            reset_template_molecule(self, context)
            mcell.molecules.status = 'Add successful'
            mcell.molecules.add_template_molecule = False

        return {'FINISHED'}


class MCELL_OT_molecule_update(bpy.types.Operator):
    bl_idname = "mcell.molecule_update"
    bl_label = "Update Molecule"
    bl_description = "Update the molecule properties in an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        template_molecule = mcell.molecules.template_molecule
        molecule_list = mcell.molecules.molecule_list

        check_all_molecule_status(self, context,
                                  check_duplicate_molecule_update)

        if not mcell.molecules.status:
            active_mol_index = mcell.molecules.active_mol_index
            active_molecule = molecule_list[active_mol_index]
            copy_molecule_properties(self, template_molecule, active_molecule)
            reset_template_molecule(self, context)
            mcell.molecules.status = 'Update successful'
            mcell.molecules.list_selected = False

        return {'FINISHED'}


def check_all_molecule_status(self, context, check_duplicate_molecule):
    """ Check for any invalid molecule properties. """

    # This could be more concise if we had the functions return values,
    # but then they can't also be used as callbacks in the future
    mcell = context.scene.mcell
    check_duplicate_molecule(self, context)
    duplicate_molecule_status = mcell.molecules.status
    check_illegal_molecule(self, context)
    illegal_molecule_status = mcell.molecules.status
    update_diffusion_constant(self, context)
    diffusion_constant_status = mcell.molecules.status
    update_custom_time_step(self, context)
    custom_time_step_status = mcell.molecules.status
    update_custom_space_step(self, context)
    custom_space_step_status = mcell.molecules.status

    if duplicate_molecule_status:
        mcell.molecules.status = duplicate_molecule_status
    elif illegal_molecule_status:
        mcell.molecules.status = illegal_molecule_status
    elif diffusion_constant_status:
        mcell.molecules.status = diffusion_constant_status
    elif custom_time_step_status:
        mcell.molecules.status = custom_time_step_status
    elif custom_space_step_status:
        mcell.molecules.status = custom_space_step_status


def copy_molecule_properties(self, molecule_old, molecule_new):
    """ Copy properties from one molecule to another. """

    molecule_new.name = molecule_old.name
    molecule_new.type = molecule_old.type
    molecule_new.diffusion_constant = molecule_old.diffusion_constant
    molecule_new.diffusion_constant_str = \
        molecule_old.diffusion_constant_str
    molecule_new.target_only = molecule_old.target_only
    molecule_new.custom_time_step = molecule_old.custom_time_step
    molecule_new.custom_time_step_str = \
        molecule_old.custom_time_step_str
    molecule_new.custom_space_step = molecule_old.custom_space_step
    molecule_new.custom_space_step_str = \
        molecule_old.custom_space_step_str


def reset_template_molecule(self, context):
    """ Set template molecule member values back to defaults. """

    mcell = context.scene.mcell
    template_molecule = mcell.molecules.template_molecule
    template_molecule.name = ''
    template_molecule.type = '2D'
    template_molecule.diffusion_constant = 0
    template_molecule.diffusion_constant_str = ''
    template_molecule.target_only = False
    template_molecule.custom_time_step = 0
    template_molecule.custom_time_step_str = ''
    template_molecule.custom_space_step = 0
    template_molecule.custom_space_step_str = ''


class MCELL_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "mcell.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mcell = context.scene.mcell
        mcell.molecules.molecule_list.remove(mcell.molecules.active_mol_index)
        mcell.molecules.active_mol_index -= 1
        if (mcell.molecules.active_mol_index < 0):
            mcell.molecules.active_mol_index = 0
        else:
            reset_template_molecule(self, context)
        mcell.molecules.status = 'Remove successful'
        mcell.molecules.list_selected = False

        return {'FINISHED'}


def check_illegal_molecule(self, context):
    """ Checks for illegal molecule name. """

    mcell = context.scene.mcell
    template_molecule = mcell.molecules.template_molecule

    status = ''

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(mol_filter, template_molecule.name)
    if m is None:
        status = 'Molecule name error: %s' % (template_molecule.name)

    mcell.molecules.status = status

    return


def check_duplicate_molecule_add(self, context):
    """ Checks for duplicate molecule name when adding molecule. """

    mcell = context.scene.mcell
    molecule_list = mcell.molecules.molecule_list
    template_molecule = mcell.molecules.template_molecule

    status = ''

    # Check for duplicate molecule name
    molecule_keys = molecule_list.keys()
    if molecule_keys.count(template_molecule.name):
        status = 'Duplicate molecule: %s' % (template_molecule.name)

    mcell.molecules.status = status

    return


def check_duplicate_molecule_update(self, context):
    """ Checks for duplicate molecule name when updating molecule. """

    mcell = context.scene.mcell
    molecule_list = mcell.molecules.molecule_list
    active_molecule_index = mcell.molecules.active_mol_index
    template_molecule = mcell.molecules.template_molecule
    active_molecule = molecule_list[active_molecule_index]

    status = ''

    # Check for duplicate molecule name
    molecule_keys = molecule_list.keys()
    if (molecule_keys.count(template_molecule.name) and
            active_molecule.name != template_molecule.name):
        status = 'Duplicate molecule: %s' % (template_molecule.name)

    mcell.molecules.status = status

    return


class MCELL_OT_reaction_add(bpy.types.Operator):
    bl_idname = "mcell.reaction_add"
    bl_label = "Add Reaction"
    bl_description = "Add a new reaction to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mc = context.scene.mcell
        mc.reactions.reaction_list.add()
        mc.reactions.active_rxn_index = len(mc.reactions.reaction_list)-1
        mc.reactions.reaction_list[
            mc.reactions.active_rxn_index].name = 'Reaction'
        return {'FINISHED'}


class MCELL_OT_reaction_remove(bpy.types.Operator):
    bl_idname = "mcell.reaction_remove"
    bl_label = "Remove Reaction"
    bl_description = "Remove selected reaction from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mc = context.scene.mcell
        mc.reactions.reaction_list.remove(mc.reactions.active_rxn_index)
        mc.reactions.active_rxn_index = mc.reactions.active_rxn_index-1
        if (mc.reactions.active_rxn_index < 0):
            mc.reactions.active_rxn_index = 0

        if len(mc.reactions.reaction_list) > 0:
            check_reaction(self, context)
        else:
            mc.reactions.status = ''

        return {'FINISHED'}


def check_reaction(self, context):
    """Checks for duplicate or illegal reaction name. Cleans up formatting."""

    mc = context.scene.mcell

    #Retrieve reaction
    rxn = mc.reactions.reaction_list[mc.reactions.active_rxn_index]
    for item in rxn.type_enum:
        if rxn.type == item[0]:
            rxtype = item[1]

    status = ''

    # clean up rxn.reactants only if necessary to avoid infinite recursion.
    reactants = rxn.reactants.replace(' ', '')
    reactants = reactants.replace('+', ' + ')
    if reactants != rxn.reactants:
        rxn.reactants = reactants

    # clean up rxn.products only if necessary to avoid infinite recursion.
    products = rxn.products.replace(' ', '')
    products = products.replace('+', ' + ')
    if products != rxn.products:
        rxn.products = products

    #Check for duplicate reaction
    rxn.name = ('%s %s %s') % (rxn.reactants, rxtype, rxn.products)
    rxn_keys = mc.reactions.reaction_list.keys()
    if rxn_keys.count(rxn.name) > 1:
        status = 'Duplicate reaction: %s' % (rxn.name)

    #Check syntax of reactant specification
    mol_list = mc.molecules.molecule_list
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)((',)|(,')|(;)|(,*)|('*))$"
    reactants = rxn.reactants.split(' + ')
    for reactant in reactants:
        m = re.match(mol_filter, reactant)
        if m is None:
            status = 'Reactant error: %s' % (reactant)
            break
        else:
            mol_name = m.group(1)
            if not mol_name in mol_list:
                status = 'Undefine molecule: %s' % (mol_name)

    #Check syntax of product specification
    if rxn.products == 'NULL':
        if rxn.type == 'reversible':
            rxn.type = 'irreversible'
    else:
        products = rxn.products.split(' + ')
        for product in products:
            m = re.match(mol_filter, product)
            if m is None:
                status = 'Product error: %s' % (product)
                break
            else:
                mol_name = m.group(1)
                if not mol_name in mol_list:
                    status = 'Undefine molecule: %s' % (mol_name)

    mc.reactions.status = status
    return


class MCELL_OT_surf_class_props_add(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_add"
    bl_label = "Add Surface Class Properties"
    bl_description = "Add new surface class properties to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[
            surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.add()
        active_surf_class.active_surf_class_props_index = len(
            active_surf_class.surf_class_props_list) - 1
        new_name = 'Surface_Class_Property'
        active_surf_class.surf_class_props_list[
            active_surf_class.active_surf_class_props_index].name = new_name

        return {'FINISHED'}


class MCELL_OT_surf_class_props_remove(bpy.types.Operator):
    bl_idname = "mcell.surf_class_props_remove"
    bl_label = "Remove Surface Class Properties"
    bl_description = "Remove surface class properties from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        active_surf_class = surf_class.surf_class_list[
            surf_class.active_surf_class_index]
        active_surf_class.surf_class_props_list.remove(
            active_surf_class.active_surf_class_props_index)
        active_surf_class.active_surf_class_props_index = len(
            active_surf_class.surf_class_props_list) - 1
        if (active_surf_class.active_surf_class_props_index < 0):
            active_surf_class.active_surf_class_props_index = 0

        if len(active_surf_class.surf_class_props_list) > 0:
            check_surf_class_props(self, context)
        else:
            surf_class.surf_class_props_status = ''

        return {'FINISHED'}


class MCELL_OT_surface_class_add(bpy.types.Operator):
    bl_idname = "mcell.surface_class_add"
    bl_label = "Add Surface Class"
    bl_description = "Add a new surface class to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        surf_class.surf_class_list.add()
        surf_class.active_surf_class_index = len(
            surf_class.surf_class_list) - 1
        surf_class.surf_class_list[
            surf_class.active_surf_class_index].name = 'Surface_Class'

        return {'FINISHED'}


class MCELL_OT_surface_class_remove(bpy.types.Operator):
    bl_idname = "mcell.surface_class_remove"
    bl_label = "Remove Surface Class"
    bl_description = "Remove selected surface class from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        surf_class = context.scene.mcell.surface_classes
        surf_class.surf_class_list.remove(surf_class.active_surf_class_index)
        surf_class.active_surf_class_index -= 1
        if (surf_class.active_surf_class_index < 0):
            surf_class.active_surf_class_index = 0

        if len(surf_class.surf_class_list) > 0:
            check_surface_class(self, context)
        else:
            surf_class.surf_class_status = ''

        return {'FINISHED'}


def check_surface_class(self, context):
    """Checks for duplicate or illegal surface class name"""

    surf_class = context.scene.mcell.surface_classes
    active_surf_class = surf_class.surf_class_list[
        surf_class.active_surf_class_index]

    status = ''

    # Check for duplicate names
    surf_class_keys = surf_class.surf_class_list.keys()
    if surf_class_keys.count(active_surf_class.name) > 1:
        status = 'Duplicate Surface Class: %s' % (active_surf_class.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    surf_class_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(surf_class_filter, active_surf_class.name)
    if m is None:
        status = 'Surface Class name error: %s' % (active_surf_class.name)

    surf_class.surf_class_status = status

    return


def convert_surf_class_str(surf_class_type):
    """Format MDL language (surf class type) for viewing in the UI"""

    if surf_class_type == 'ABSORPTIVE':
        surf_class_type = 'Absorptive'
    elif surf_class_type == 'TRANSPARENT':
        surf_class_type = 'Transparent'
    elif surf_class_type == 'REFLECTIVE':
        surf_class_type = 'Reflective'
    elif surf_class_type == 'CLAMP_CONCENTRATION':
        surf_class_type = 'Clamp Concentration'

    return(surf_class_type)


def convert_orient_str(orient):
    """Format MDL language (orientation) for viewing in the UI"""

    if orient == "'":
        orient = 'Top/Front'
    elif orient == ",":
        orient = 'Bottom/Back'
    elif orient == ";":
        orient = 'Ignore'

    return(orient)


def check_surf_class_props(self, context):
    """Checks for illegal/undefined molecule names in surf class properties"""

    mc = context.scene.mcell
    active_surf_class = mc.surface_classes.surf_class_list[
        mc.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    mol_list = mc.molecules.molecule_list
    molecule = surf_class_props.molecule
    surf_class_type = surf_class_props.surf_class_type
    orient = surf_class_props.surf_class_orient

    surf_class_type = convert_surf_class_str(surf_class_type)
    orient = convert_orient_str(orient)

    if molecule:
        surf_class_props.name = 'Molec.: %s   Orient.: %s   Type: %s' % (
            molecule, orient, surf_class_type)
    else:
        surf_class_props.name = 'Molec.: NA   Orient.: %s   Type: %s' % (
            orient, surf_class_type)

    status = ''

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*)"
    m = re.match(mol_filter, molecule)
    if m is None:
        status = 'Molecule name error: %s' % (molecule)
    else:
        # Check for undefined names
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = 'Undefined molecule: %s' % (mol_name)

    mc.surface_classes.surf_class_props_status = status

    return


class MCELL_OT_mod_surf_regions_add(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_add"
    bl_label = "Add Surface Region Modification"
    bl_description = "Add a surface region modification to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.add()
        mod_surf_regions.active_mod_surf_regions_index = len(
            mod_surf_regions.mod_surf_regions_list) - 1
        new_name = 'Modify_Surface_Region'
        mod_surf_regions.mod_surf_regions_list[
            mod_surf_regions.active_mod_surf_regions_index].name = new_name

        return {'FINISHED'}


class MCELL_OT_mod_surf_regions_remove(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_remove"
    bl_label = "Remove Surface Region Modification"
    bl_description = "Remove selected surface region modification"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.remove(
            mod_surf_regions.active_mod_surf_regions_index)
        mod_surf_regions.active_mod_surf_regions_index -= 1
        if (mod_surf_regions.active_mod_surf_regions_index < 0):
            mod_surf_regions.active_mod_surf_regions_index = 0

        return {'FINISHED'}


def format_mod_surf_regions_entry(surf_class_name, object_name, region_name):
    """Check if the entries in Modify Surface Regions exist and format them"""
    if not surf_class_name:
        surf_class_name = 'NA'
    if not object_name:
        object_name = 'NA'
    if not region_name:
        region_name = 'NA'

    mod_surf_regions_entry = 'Surface Class: %s   Object: %s   Region: %s' % (
        surf_class_name, object_name, region_name)

    return(mod_surf_regions_entry)


def check_assigned_surface_class(self, context):
    """Make sure the surface class name is valid and format the list entry"""

    mc = context.scene.mcell
    surf_class_list = mc.surface_classes.surf_class_list
    mod_surf_regions = mc.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    active_mod_surf_regions.name = format_mod_surf_regions_entry(
        surf_class_name, object_name, region_name)

    status = ''

    #Make sure there is something in the Defined Surface Classes list
    if not surf_class_list:
        status = 'No surface classes defined'
    #Make sure the user entered surf class is in Defined Surface Classes list
    elif not surf_class_name in surf_class_list:
        status = 'Undefined surface class: %s' % surf_class_name

    mod_surf_regions.status = status

    return


def check_assigned_object(self, context):
    """Make sure the object name is valid and format the list entry"""

    mc = context.scene.mcell
    obj_list = mc.model_objects.object_list
    mod_surf_regions = mc.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    active_mod_surf_regions.name = format_mod_surf_regions_entry(
        surf_class_name, object_name, region_name)

    status = ''

    #Make sure there is something in the Model Objects list
    if not obj_list:
        status = 'No objects available'
    #Make sure the user entered object name is in the Model Objects list
    elif not active_mod_surf_regions.object_name in obj_list:
        status = 'Undefined object: %s' % active_mod_surf_regions.object_name

    mod_surf_regions.status = status

    return


def check_modified_region(self, context):
    """Make sure the region name is valid and format the list entry"""

    mc = context.scene.mcell
    mod_surf_regions = mc.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    region_list = bpy.data.objects[
        active_mod_surf_regions.object_name].mcell.regions.region_list
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    active_mod_surf_regions.name = format_mod_surf_regions_entry(
        surf_class_name, object_name, region_name)

    status = ''

    try:
        if not region_list:
            status = 'The selected object has no surface regions'
        elif not region_name in region_list:
            status = 'Undefined region: %s' % region_name
    except KeyError:
        #the object name in mod surf regions isn't a blender object
        pass

    mod_surf_regions.status = status

    return


class MCELL_OT_release_site_add(bpy.types.Operator):
    bl_idname = "mcell.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add a new Molecule Release Site to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mc = context.scene.mcell
        mc.release_sites.mol_release_list.add()
        mc.release_sites.active_release_index = len(
            mc.release_sites.mol_release_list)-1
        mc.release_sites.mol_release_list[
            mc.release_sites.active_release_index].name = 'Release_Site'

        return {'FINISHED'}


class MCELL_OT_release_site_remove(bpy.types.Operator):
    bl_idname = "mcell.release_site_remove"
    bl_label = "Remove Release Site"
    bl_description = "Remove selected Molecule Release Site from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mc = context.scene.mcell
        mc.release_sites.mol_release_list.remove(
            mc.release_sites.active_release_index)
        mc.release_sites.active_release_index -= 1
        if (mc.release_sites.active_release_index < 0):
            mc.release_sites.active_release_index = 0

        if len(mc.release_sites.mol_release_list) > 0:
            check_release_site(self, context)
        else:
            mc.release_sites.status = ''

        return {'FINISHED'}


def check_release_site(self, context):
    """Checks for duplicate or illegal release site name."""

    mc = context.scene.mcell
    rel_list = mc.release_sites.mol_release_list
    rel = rel_list[mc.release_sites.active_release_index]

    status = ''

    # Check for duplicate release site name
    rel_keys = rel_list.keys()
    if rel_keys.count(rel.name) > 1:
        status = 'Duplicate release site: %s' % (rel.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_filter, rel.name)
    if m is None:
        status = 'Release Site name error: %s' % (rel.name)

    mc.release_sites.status = status

    return


def check_release_molecule(self, context):
    """Checks for illegal release site molecule name."""

    mc = context.scene.mcell
    rel_list = mc.release_sites.mol_release_list
    rel = rel_list[mc.release_sites.active_release_index]
    mol = rel.molecule

    mol_list = mc.molecules.molecule_list

    status = ''

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(mol_filter, mol)
    if m is None:
        status = 'Molecule name error: %s' % (mol)
    else:
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = 'Undefined molecule: %s' % (mol_name)

    mc.release_sites.status = status

    return


def check_release_object_expr(self, context):
    """Checks for illegal release object name."""

    scn = context.scene
    mc = context.scene.mcell
    rel_list = mc.release_sites.mol_release_list
    rel = rel_list[mc.release_sites.active_release_index]
    obj_expr = rel.object_expr

    status = ''

    #obj_reg_filter = r"(^([A-Za-z]+[0-9A-Za-z_.]*)$)|((^[A-Za-z]+[0-9A-Za-z_.]*)(\[)([A-Za-z]+[0-9A-Za-z_.]*)(\])$)"

    # Check for illegal names. (Starts with a letter. No special characters.)
    # May be only object name or object name and region (e.g. object[reg].)
    obj_reg_filter = r"(?P<obj_reg>(?P<obj_name>^[A-Za-z]+[0-9A-Za-z_.]*)(\[)(?P<reg_name>[A-Za-z]+[0-9A-Za-z_.]*)(\])$)|(?P<obj_name_only>^([A-Za-z]+[0-9A-Za-z_.]*)$)"

    expr_filter = r"[\+\-\*\(\)]"

    expr_vars = re.sub(expr_filter, ' ', obj_expr).split()

    for var in expr_vars:
        m = re.match(obj_reg_filter, var)
        if m is None:
            status = 'Object name error: %s' % (var)
            break
        else:
            if m.group('obj_reg') is not None:
                obj_name = m.group('obj_name')
                reg_name = m.group('reg_name')
                if not obj_name in scn.objects:
                    status = 'Undefined object: %s' % (obj_name)
                    break
                obj = scn.objects[obj_name]
                if reg_name != "ALL":
                    if not obj.data.get('mcell'):
                        status = 'Undefined region: %s' % (reg_name)
                        break
                    if not obj.data['mcell'].get('regions'):
                        status = 'Undefined region: %s' % (reg_name)
                        break
                    if not obj.data['mcell']['regions'].get(reg_name):
                        status = 'Undefined region: %s' % (reg_name)
                        break
            else:
                obj_name = m.group('obj_name_only')
                if not obj_name in scn.objects:
                    status = 'Undefined object: %s' % (obj_name)
                    break

    mc.release_sites.status = status

    return


class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mc = context.scene.mcell
        if mc.project_settings.export_format == 'mcell_mdl_unified':
#            if not mc.project_settings.export_selection_only:
#                bpy.ops.object.select_by_type(type='MESH')
            filepath = mc.project_settings.project_dir + '/' + \
                mc.project_settings.base_name + '.main.mdl'
            bpy.ops.export_mdl_mesh.mdl('INVOKE_DEFAULT', filepath=filepath)
        elif mc.project_settings.export_format == 'mcell_mdl_modular':
            filepath = mc.project_settings.project_dir + '/' + \
                mc.project_settings.base_name + '.main.mdl'
            bpy.ops.export_mdl_mesh.mdl('INVOKE_DEFAULT', filepath=filepath)

        return {'FINISHED'}


class MCELL_OT_set_project_dir(bpy.types.Operator):
    bl_idname = "mcell.set_project_dir"
    bl_label = "Set Project Directory"
    bl_description = "Set CellBlender Project Directory"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH", default="")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    def __init__(self):
        self.directory = bpy.context.scene.mcell.project_settings.project_dir

    # Note: use classmethod "poll" to determine when
    # runability of operator is valid
    #
    #    @classmethod
    #    def poll(cls, context):
    #        return context.object is not None

    def execute(self, context):

        mc = context.scene.mcell
        if (os.path.isdir(self.filepath)):
            dir = self.filepath
        else:
            dir = os.path.dirname(self.filepath)

        # Reset mol_file_list to empty
        for i in range(mc.mol_viz.mol_file_num-1, -1, -1):
            mc.mol_viz.mol_file_list.remove(i)

        mc.mol_viz.mol_file_name = ''
        mc.project_settings.project_dir = dir
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MCELL_OT_set_mol_viz_dir(bpy.types.Operator):
    bl_idname = "mcell.set_mol_viz_dir"
    bl_label = "Read Molecule Files"
    bl_description = "Read MCell Molecule Files for Visualization"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH", default="")
    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    def __init__(self):
        self.directory = bpy.context.scene.mcell.mol_viz.mol_file_dir

    # Note: use classmethod "poll" to determine when
    # runability of operator is valid
    #
    #    @classmethod
    #    def poll(cls, context):
    #        return context.object is not None

    def execute(self, context):

        mc = context.scene.mcell
        if (os.path.isdir(self.filepath)):
            mol_file_dir = self.filepath
        else:
            mol_file_dir = os.path.dirname(self.filepath)
        mol_file_list = glob.glob(mol_file_dir + '/*')
        mol_file_list.sort()

        # Reset mol_file_list to empty
        for i in range(mc.mol_viz.mol_file_num-1, -1, -1):
            mc.mol_viz.mol_file_list.remove(i)

        mc.mol_viz.mol_file_dir = mol_file_dir
        i = 0
        for mol_file_name in mol_file_list:
            new_item = mc.mol_viz.mol_file_list.add()
            new_item.name = os.path.basename(mol_file_name)
            i += 1

        mc.mol_viz.mol_file_num = len(mc.mol_viz.mol_file_list)
        mc.mol_viz.mol_file_stop_index = mc.mol_viz.mol_file_num-1
        mc.mol_viz.mol_file_index = 0

        mc.mol_viz.color_index = 0
        if len(mc.mol_viz.color_list) == 0:
            for i in range(8):
                mc.mol_viz.color_list.add()
            mc.mol_viz.color_list[0].vec = [0.8, 0.0, 0.0]
            mc.mol_viz.color_list[1].vec = [0.0, 0.8, 0.0]
            mc.mol_viz.color_list[2].vec = [0.0, 0.0, 0.8]
            mc.mol_viz.color_list[3].vec = [0.0, 0.8, 0.8]
            mc.mol_viz.color_list[4].vec = [0.8, 0.0, 0.8]
            mc.mol_viz.color_list[5].vec = [0.8, 0.8, 0.0]
            mc.mol_viz.color_list[6].vec = [1.0, 1.0, 1.0]
            mc.mol_viz.color_list[7].vec = [0.0, 0.0, 0.0]

        MolVizUpdate(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MCELL_OT_mol_viz_set_index(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_set_index"
    bl_label = "Set Molecule File Index"
    bl_description = "Set MCell Molecule File Index for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mc = context.scene.mcell
        if (len(mc.mol_viz.mol_file_list) > 0):
            i = mc.mol_viz.mol_file_index
            if (i > mc.mol_viz.mol_file_stop_index):
                i = mc.mol_viz.mol_file_stop_index
            if (i < mc.mol_viz.mol_file_start_index):
                i = mc.mol_viz.mol_file_start_index
            mc.mol_viz.mol_file_index = i
            MolVizUpdate(self, context)
        return{'FINISHED'}


class MCELL_OT_mol_viz_next(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_next"
    bl_label = "Step to Next Molecule File"
    bl_description = "Step to Next MCell Molecule File for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mc = context.scene.mcell
        i = mc.mol_viz.mol_file_index + mc.mol_viz.mol_file_step_index
        if (i > mc.mol_viz.mol_file_stop_index):
            i = mc.mol_viz.mol_file_stop_index
        mc.mol_viz.mol_file_index = i
        MolVizUpdate(self, context)
        return{'FINISHED'}


class MCELL_OT_mol_viz_prev(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_prev"
    bl_label = "Step to Previous Molecule File"
    bl_description = "Step to Previous MCell Molecule File for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        mc = context.scene.mcell
        i = mc.mol_viz.mol_file_index - mc.mol_viz.mol_file_step_index
        if (i < mc.mol_viz.mol_file_start_index):
            i = mc.mol_viz.mol_file_start_index
        mc.mol_viz.mol_file_index = i
        MolVizUpdate(self, context)
        return{'FINISHED'}


#CellBlender operator helper functions:


@persistent
def frame_change_handler(scn):
    mc = scn.mcell
    curr_frame = mc.mol_viz.mol_file_index
    if (not curr_frame == scn.frame_current):
        mc.mol_viz.mol_file_index = scn.frame_current
        bpy.ops.mcell.mol_viz_set_index()
#        scn.update()
        if mc.mol_viz.render_and_save:
            scn.render.filepath = '//stores_on/frames/frame_%05d.png' % (
                scn.frame_current)
            bpy.ops.render.render(write_still=True)


def render_handler(scn):
    mc = scn.mcell
    curr_frame = mc.mol_viz.mol_file_index
    if (not curr_frame == scn.frame_current):
        mc.mol_viz.mol_file_index = scn.frame_current
        bpy.ops.mcell.mol_viz_set_index()
#    scn.update()


def MolVizUpdate(self, context):
    mc = context.scene.mcell

    filename = mc.mol_viz.mol_file_list[mc.mol_viz.mol_file_index].name
    mc.mol_viz.mol_file_name = filename
    filepath = os.path.join(mc.mol_viz.mol_file_dir, filename)

    global_undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False

    MolVizClear(mc)
    if mc.mol_viz.mol_viz_enable:
        MolVizFileRead(mc, filepath)

    bpy.context.user_preferences.edit.use_global_undo = global_undo
    return


def MolVizClear(mcell_prop):

    mc = mcell_prop
    scn = bpy.context.scene
    scn_objs = scn.objects
    meshes = bpy.data.meshes
    objs = bpy.data.objects
    for mol_item in mc.mol_viz.mol_viz_list:
        mol_name = mol_item.name
#        mol_obj = scn_objs[mol_name]
        mol_obj = scn_objs.get(mol_name)
        if mol_obj:
            hide = mol_obj.hide

            mol_pos_mesh = mol_obj.data
            mol_pos_mesh_name = mol_pos_mesh.name
            mol_shape_obj_name = '%s_shape' % (mol_name)
            mol_shape_obj = objs.get(mol_shape_obj_name)
            if mol_shape_obj:
                mol_shape_obj.parent = None

            scn_objs.unlink(mol_obj)
            objs.remove(mol_obj)
            meshes.remove(mol_pos_mesh)

            mol_pos_mesh = meshes.new(mol_pos_mesh_name)
            mol_obj = objs.new(mol_name, mol_pos_mesh)
            scn_objs.link(mol_obj)

            if mol_shape_obj:
                mol_shape_obj.parent = mol_obj

            mol_obj.dupli_type = 'VERTS'
            mol_obj.use_dupli_vertices_rotation = True
            mols_obj = objs.get('molecules')
            mol_obj.parent = mols_obj

            mol_obj.hide = hide

#    scn.update()

    # Reset mol_viz_list to empty
    for i in range(len(mc.mol_viz.mol_viz_list)-1, -1, -1):
        mc.mol_viz.mol_viz_list.remove(i)


def MolVizFileRead(mcell_prop, filepath):

    mc = mcell_prop
    try:

#        begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#        print ('Processing molecules from file:    %s' % (filepath))

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, 'rb')
        b = array.array('I')
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read Binary format molecule file:
            bin_data = 1
            while True:
                try:
                    ni = array.array('B')
                    ni.fromfile(mol_file, 1)
                    ns = array.array('B')
                    ns.fromfile(mol_file, ni[0])
                    s = ns.tostring().decode()
                    mol_name = 'mol_%s' % (s)
                    mt = array.array('B')
                    mt.fromfile(mol_file, 1)
                    ni = array.array('I')
                    ni.fromfile(mol_file, 1)
                    mol_pos = array.array('f')
                    mol_orient = array.array('f')
                    mol_pos.fromfile(mol_file, ni[0])
#                    tot += ni[0]/3
                    if mt[0] == 1:
                        mol_orient.fromfile(mol_file, ni[0])
                    mol_dict[mol_name] = [mt[0], mol_pos, mol_orient]
                    new_item = mc.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                except:
#                    print('Molecules read: %d' % (int(tot)))
                    mol_file.close()
                    break

        else:
            # Read ASCII format molecule file:
            bin_data = 0
            mol_file.close()
            mol_data = [[s.split()[0], [
                float(x) for x in s.split()[1:]]] for s in open(
                    filepath, 'r').read().split('\n') if s != '']

            for mol in mol_data:
                mol_name = 'mol_%s' % (mol[0])
                if not mol_name in mol_dict:
                    mol_orient = mol[1][3:]
                    mt = 0
                    if ((mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) |
                            (mol_orient[2] != 0.0)):
                        mt = 1
                    mol_dict[mol_name] = [
                        mt, array.array('f'), array.array('f')]
                    new_item = mc.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                mt = mol_dict[mol_name][0]
                mol_dict[mol_name][1].extend(mol[1][:3])
                if mt == 1:
                    mol_dict[mol_name][2].extend(mol[1][3:])

        mols_obj = bpy.data.objects.get('molecules')
        if not mols_obj:
            bpy.ops.object.add()
            mols_obj = bpy.context.selected_objects[0]
            mols_obj.name = 'molecules'

        if len(mol_dict) > 0:
            meshes = bpy.data.meshes
            mats = bpy.data.materials
            objs = bpy.data.objects
            scn = bpy.context.scene
            scn_objs = scn.objects
            z_axis = mathutils.Vector((0.0, 0.0, 1.0))
            ident_mat = mathutils.Matrix.Translation(
                mathutils.Vector((0.0, 0.0, 0.0)))

            for mol_name in mol_dict.keys():
                mol_mat_name = '%s_mat' % (mol_name)
                mol_type = mol_dict[mol_name][0]
                mol_pos = mol_dict[mol_name][1]
                mol_orient = mol_dict[mol_name][2]

                # Randomly orient volume molecules
                if mol_type == 0:
                    mol_orient.extend([random.uniform(
                        -1.0, 1.0) for i in range(len(mol_pos))])

#             Look-up mesh shape template and create if needed
                mol_shape_mesh_name = '%s_shape' % (mol_name)
                mol_shape_obj_name = mol_shape_mesh_name
                mol_shape_mesh = meshes.get(mol_shape_mesh_name)
                if not mol_shape_mesh:
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=0, size=0.005)
                    mol_shape_obj = bpy.context.active_object
                    mol_shape_obj.name = mol_shape_obj_name
                    mol_shape_obj.track_axis = "POS_Z"
                    mol_shape_mesh = mol_shape_obj.data
                    mol_shape_mesh.name = mol_shape_mesh_name
                else:
                    mol_shape_obj = objs.get(mol_shape_obj_name)

#             Look-up material, create if needed.
#             Associate material with mesh shape.
                mol_mat = mats.get(mol_mat_name)
                if not mol_mat:
                    mol_mat = mats.new(mol_mat_name)
                    mol_mat.diffuse_color = mc.mol_viz.color_list[
                        mc.mol_viz.color_index].vec
                    mc.mol_viz.color_index = mc.mol_viz.color_index + 1
                    if mc.mol_viz.color_index > len(mc.mol_viz.color_list)-1:
                        mc.mol_viz.color_index = 0
                if not mol_shape_mesh.materials.get(mol_mat_name):
                    mol_shape_mesh.materials.append(mol_mat)

#             Create a "mesh" to hold instances of molecule positions
                mol_pos_mesh_name = '%s_pos' % (mol_name)
                mol_pos_mesh = meshes.get(mol_pos_mesh_name)
                if not mol_pos_mesh:
                    mol_pos_mesh = meshes.new(mol_pos_mesh_name)

#             Add and place vertices at positions of molecules
                mol_pos_mesh.vertices.add(len(mol_pos)//3)
                mol_pos_mesh.vertices.foreach_set("co", mol_pos)
                mol_pos_mesh.vertices.foreach_set("normal", mol_orient)

#             Create object to contain the mol_pos_mesh data
                mol_obj = objs.get(mol_name)
                if not mol_obj:
                    mol_obj = objs.new(mol_name, mol_pos_mesh)
                    scn_objs.link(mol_obj)
                    mol_shape_obj.parent = mol_obj
                    mol_obj.dupli_type = 'VERTS'
                    mol_obj.use_dupli_vertices_rotation = True
                    mol_obj.parent = mols_obj

#        scn.update()

#        utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
#        print ('     Processed %d molecules in %g seconds\n' % (
#            len(mol_data), utime))

    except IOError:
        print(('\n***** File not found: %s\n') % (filepath))
    except ValueError:
        print(('\n***** Invalid data in file: %s\n') % (filepath))


# Meshalyzer
class MCELL_OT_meshalyzer(bpy.types.Operator):
    bl_idname = "mcell.meshalyzer"
    bl_label = "Analyze Geometric Properties of Mesh"
    bl_description = "Analyze Geometric Properties of Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mc = context.scene.mcell
        objs = context.selected_objects

        mc.meshalyzer.object_name = ''
        mc.meshalyzer.vertices = 0
        mc.meshalyzer.edges = 0
        mc.meshalyzer.faces = 0
        mc.meshalyzer.watertight = ''
        mc.meshalyzer.manifold = ''
        mc.meshalyzer.normal_status = ''
        mc.meshalyzer.area = 0
        mc.meshalyzer.volume = 0

        if (len(objs) != 1):
            mc.meshalyzer.status = 'Please Select One Mesh Object'
            return {'FINISHED'}

        obj = objs[0]

        mc.meshalyzer.object_name = obj.name

        if not (obj.type == 'MESH'):
            mc.meshalyzer.status = 'Selected Object Not a Mesh'
            return {'FINISHED'}

        t_mat = obj.matrix_world
        mesh = obj.data

        mc.meshalyzer.vertices = len(mesh.vertices)
        mc.meshalyzer.edges = len(mesh.edges)
        mc.meshalyzer.faces = len(mesh.polygons)

        area = 0
        for f in mesh.polygons:
            if not (len(f.vertices) == 3):
                mc.meshalyzer.status = '***** Mesh Not Triangulated *****'
                mc.meshalyzer.watertight = 'Mesh Not Triangulated'
                return {'FINISHED'}

            tv0 = mesh.vertices[f.vertices[0]].co * t_mat
            tv1 = mesh.vertices[f.vertices[1]].co * t_mat
            tv2 = mesh.vertices[f.vertices[2]].co * t_mat
            area = area + mathutils.geometry.area_tri(tv0, tv1, tv2)

        mc.meshalyzer.area = area

        (edge_faces, edge_face_count) = make_efdict(mesh)

        is_closed = check_closed(edge_face_count)
        is_manifold = check_manifold(edge_face_count)
        is_orientable = check_orientable(mesh, edge_faces, edge_face_count)

        if is_orientable:
            mc.meshalyzer.normal_status = 'Consistent Normals'
        else:
            mc.meshalyzer.normal_status = 'Inconsistent Normals'

        if is_closed:
            mc.meshalyzer.watertight = 'Watertight Mesh'
        else:
            mc.meshalyzer.watertight = 'Non-watertight Mesh'

        if is_manifold:
            mc.meshalyzer.manifold = 'Manifold Mesh'
        else:
            mc.meshalyzer.manifold = 'Non-manifold Mesh'

        if is_orientable and is_manifold and is_closed:
            volume = mesh_vol(mesh, t_mat)
            mc.meshalyzer.volume = volume
            if volume >= 0:
                mc.meshalyzer.normal_status = 'Outward Facing Normals'
            else:
                mc.meshalyzer.normal_status = 'Inward Facing Normals'

        mc.meshalyzer.status = ''
        return {'FINISHED'}


def mesh_vol(mesh, t_mat):
    """Compute volume of triangulated, orientable, watertight, manifold mesh

    volume > 0 means outward facing normals
    volume < 0 means inward facing normals

    """

    volume = 0.0
    for f in mesh.polygons:
        tv0 = mesh.vertices[f.vertices[0]].co * t_mat
        tv1 = mesh.vertices[f.vertices[1]].co * t_mat
        tv2 = mesh.vertices[f.vertices[2]].co * t_mat
        x0 = tv0.x
        y0 = tv0.y
        z0 = tv0.z
        x1 = tv1.x
        y1 = tv1.y
        z1 = tv1.z
        x2 = tv2.x
        y2 = tv2.y
        z2 = tv2.z
        det = x0*(y1*z2-y2*z1)+x1*(y2*z0-y0*z2)+x2*(y0*z1-y1*z0)
        volume = volume + det

    volume = volume/6.0

    return(volume)


def make_efdict(mesh):

    edge_faces = {}
    edge_face_count = {}
    for f in mesh.polygons:
        for ek in f.edge_keys:
            if ek in edge_faces:
                edge_faces[ek] ^= f.index
                edge_face_count[ek] = edge_face_count[ek] + 1
            else:
                edge_faces[ek] = f.index
                edge_face_count[ek] = 1

    return(edge_faces, edge_face_count)


def check_manifold(edge_face_count):
    """ Make sure the object is manifold """

    for ek in edge_face_count.keys():
        if edge_face_count[ek] != 2:
            return (0)

    return(1)


def check_closed(edge_face_count):
    """ Make sure the object is closed (no leaks). """

    for ek in edge_face_count.keys():
        if not edge_face_count[ek] == 2:
            return (0)

    return(1)


def check_orientable(mesh, edge_faces, edge_face_count):

    ev_order = [[0, 1], [1, 2], [2, 0]]
    edge_checked = {}

    for f in mesh.polygons:
        for i in range(0, len(f.vertices)):
            ek = f.edge_keys[i]
            if not ek in edge_checked:
                edge_checked[ek] = 1
                if edge_face_count[ek] == 2:
                    nfi = f.index ^ edge_faces[ek]
                    nf = mesh.polygons[nfi]
                    for j in range(0, len(nf.vertices)):
                        if ek == nf.edge_keys[j]:
                            if f.vertices[ev_order[i][0]] != nf.vertices[
                                    ev_order[j][1]]:
                                return (0)
                            break

    return (1)


class MCELL_OT_select_filtered(bpy.types.Operator):
    bl_idname = "mcell.select_filtered"
    bl_label = "Select Filtered"
    bl_description = "Select objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mc = scn.mcell
        objs = scn.objects

        filter = mc.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = True

        return {'FINISHED'}


class MCELL_OT_deselect_filtered(bpy.types.Operator):
    bl_idname = "mcell.deselect_filtered"
    bl_label = "Deselect Filtered"
    bl_description = "Deselect objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mc = scn.mcell
        objs = scn.objects

        filter = mc.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = False

        return {'FINISHED'}


class MCELL_OT_model_objects_add(bpy.types.Operator):
    bl_idname = "mcell.model_objects_add"
    bl_label = "Model Objects Include"
    bl_description = "Include selected objects in model object export list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mc = context.scene.mcell
        # From the list of selected objects, only add MESH objects.
        objs = [obj for obj in context.selected_objects if obj.type == 'MESH']

        for obj in objs:
            mc.model_objects.object_list.add()
            mc.model_objects.active_obj_index = len(
                mc.model_objects.object_list)-1
            mc.model_objects.object_list[
                mc.model_objects.active_obj_index].name = obj.name

        return {'FINISHED'}


class MCELL_OT_model_objects_remove(bpy.types.Operator):
    bl_idname = "mcell.model_objects_remove"
    bl_label = "Model Objects Remove"
    bl_description = "Remove current item from model object export list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mc = context.scene.mcell

        mc.model_objects.object_list.remove(mc.model_objects.active_obj_index)
        mc.model_objects.active_obj_index -= 1
        if (mc.model_objects.active_obj_index < 0):
            mc.model_objects.active_obj_index = 0

        return {'FINISHED'}


class MCELL_OT_set_molecule_glyph(bpy.types.Operator):
    bl_idname = "mcell.set_molecule_glyph"
    bl_label = "Set Molecule Glyph"
    bl_description = "Set molecule glyph to desired shape in glyph library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mc = context.scene.mcell
        mc.molecule_glyphs.status = ''
#        new_glyph_name = 'receptor_glyph'
#        mol_shape_name = 'mol_Ca_shape'
        sobjs = context.selected_objects
        if (len(sobjs) != 1):
            mc.molecule_glyphs.status = 'Select One Molecule'
            return {'FINISHED'}
        if (sobjs[0].type != 'MESH'):
            mc.molecule_glyphs.status = 'Selected Object Not a Molecule'
            return {'FINISHED'}

        mol_obj = sobjs[0]
        mol_shape_name = mol_obj.name

        new_glyph_name = mc.molecule_glyphs.glyph

        bpy.ops.wm.link_append(directory=mc.molecule_glyphs.glyph_lib, files=[
            {'name': new_glyph_name}], link=False, autoselect=False)

        mol_mat = mol_obj.material_slots[0].material
        new_mol_mesh = bpy.data.meshes[new_glyph_name]
        mol_obj.data = new_mol_mesh
        bpy.data.meshes.remove(bpy.data.meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        new_mol_mesh.materials.append(mol_mat)

        return {'FINISHED'}


def load_active_molecule(self, context):
    """ Load molecule properties when user clicks in molecule list. """

    mcell = context.scene.mcell
    template_molecule = mcell.molecules.template_molecule
    molecule_list = mcell.molecules.molecule_list
    if molecule_list:
        active_molecule_index = mcell.molecules.active_mol_index
        active_molecule = molecule_list[active_molecule_index]
        # Adding and removing molecules will also trigger this callback.
        # In those two cases, the active name is still blank.
        # The following name check ensures we only pay attention to list clicks
        if active_molecule.name:
            active_mol_index = mcell.molecules.active_mol_index
            active_molecule = molecule_list[active_mol_index]
            copy_molecule_properties(self, active_molecule, template_molecule)
            #template_molecule.name = active_molecule.name
            #template_molecule.type = active_molecule.type
            #template_molecule.diffusion_constant = \
            #    active_molecule.diffusion_constant
            #template_molecule.diffusion_constant_str = \
            #    active_molecule.diffusion_constant_str
            #template_molecule.target_only = active_molecule.target_only
            #template_molecule.custom_time_step = \
            #    active_molecule.custom_time_step
            #template_molecule.custom_time_step_str = \
            #    active_molecule.custom_time_step_str
            #template_molecule.custom_space_step = \
            #    active_molecule.custom_time_step
            #template_molecule.custom_space_step_str = \
            #    active_molecule.custom_time_step_str

            mcell.molecules.list_selected = True
            mcell.molecules.status = ''


def check_val_str(val_str, min_val, max_val):

    status = ''
    val = None

    try:
        val = float(val_str)
        if min_val is not None:
            if val < min_val:
                status = "Invalid value for %s: %s"
        if max_val is not None:
            if val > max_val:
                status = "Invalid value for %s: %s"
    except ValueError:
        status = "Invalid value for %s: %s"

    return (val, status)


def update_clamp_value(self, context):
    """ Store the clamp value as a float if it's legal or generate an error """

    mc = context.scene.mcell
    surf_class = context.scene.mcell.surface_classes
    active_surf_class = mc.surface_classes.surf_class_list[
        mc.surface_classes.active_surf_class_index]
    surf_class_props = active_surf_class.surf_class_props_list[
        active_surf_class.active_surf_class_props_index]
    surf_class_type = surf_class_props.surf_class_type
    orient = surf_class_props.surf_class_orient
    molecule = surf_class_props.molecule
    clamp_value_str = surf_class_props.clamp_value_str

    (clamp_value, status) = check_val_str(clamp_value_str, 0, None)

    if status == '':
        surf_class_props.clamp_value = clamp_value
    else:
        status = status % ('clamp_value', clamp_value_str)
        surf_class_props.clamp_value_str = '%g' % (
            surf_class_props.clamp_value)

    surf_class_type = convert_surf_class_str(surf_class_type)
    orient = convert_orient_str(orient)

    if molecule:
        surf_class_props.name = 'Molec.: %s   Orient.: %s   Type: %s' % (
            molecule, orient, surf_class_type)
    else:
        surf_class_props.name = 'Molec.: NA   Orient.: %s   Type: %s' % (
            orient, surf_class_type)

    surf_class.surf_class_props_status = status

    return


def update_time_step(self, context):
    """ Store the time step as a float if it's legal or generate an error """

    mc = context.scene.mcell
    time_step_str = mc.initialization.time_step_str

    (time_step, status) = check_val_str(time_step_str, 0, None)

    if status == '':
        mc.initialization.time_step = time_step
    else:
        status = status % ('time_step', time_step_str)
        mc.initialization.time_step_str = '%g' % (mc.initialization.time_step)

    mc.initialization.status = status

    return


def update_diffusion_constant(self, context):
    """ Store the diffusion constant as a float if it's legal """

    mc = context.scene.mcell
    template_molecule = mc.molecules.template_molecule
    diffusion_constant_str = template_molecule.diffusion_constant_str

    (diffusion_constant, status) = check_val_str(
        diffusion_constant_str, 0, None)

    if status:
        status = status % ('diffusion_constant', diffusion_constant_str)
    else:
        template_molecule.diffusion_constant = diffusion_constant

    mc.molecules.status = status

    return


def update_custom_time_step(self, context):
    """ Store the custom time step as a float if it's legal """

    mcell = context.scene.mcell
    template_molecule = mcell.molecules.template_molecule
    custom_time_step_str = template_molecule.custom_time_step_str

    if custom_time_step_str:
        (custom_time_step, status) = check_val_str(custom_time_step_str,
                                                   0, None)
        if status:
            status = status % ('custom_time_step', custom_time_step_str)
        else:
            template_molecule.custom_time_step = custom_time_step

        mcell.molecules.status = status

    return


def update_custom_space_step(self, context):
    """ Store the custom space step as a float if it's legal """

    mcell = context.scene.mcell
    template_molecule = mcell.molecules.template_molecule
    custom_space_step_str = template_molecule.custom_space_step_str

    if custom_space_step_str:
        (custom_space_step, status) = check_val_str(custom_space_step_str,
                                                    0, None)
        if status:
            status = status % ('custom_space_step', custom_space_step_str)
        else:
            template_molecule.custom_space_step = custom_space_step

        mcell.molecules.status = status

    return


def update_fwd_rate(self, context):
    """ Store the forward reaction rate as a float if it's legal """

    mc = context.scene.mcell
    rxn = mc.reactions.reaction_list[mc.reactions.active_rxn_index]
    fwd_rate_str = rxn.fwd_rate_str

    (fwd_rate, status) = check_val_str(fwd_rate_str, 0, None)

    if status == '':
        rxn.fwd_rate = fwd_rate
    else:
        status = status % ('fwd_rate', fwd_rate_str)
        rxn.fwd_rate_str = '%g' % (rxn.fwd_rate)

    mc.reactions.status = status

    return


def update_bkwd_rate(self, context):
    """ Store the backward reaction rate as a float if it's legal """

    mc = context.scene.mcell
    rxn = mc.reactions.reaction_list[mc.reactions.active_rxn_index]
    bkwd_rate_str = rxn.bkwd_rate_str

    (bkwd_rate, status) = check_val_str(bkwd_rate_str, 0, None)

    if status == '':
        rxn.bkwd_rate = bkwd_rate
    else:
        status = status % ('bkwd_rate', bkwd_rate_str)
        rxn.bkwd_rate_str = '%g' % (rxn.bkwd_rate)

    mc.reactions.status = status

    return
