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
This file contains the classes for CellBlender's Molecules.

Molecules (or more properly "Molecule Species") contain two types of data:

  MCell data - Name, diffusion constant, 2D/3D, etc.
  Blender data - Name, glyph, size, color, position mesh

Note that some items (the name, for example) is considered as both
MCell data and Blender data.

Molecules (or parts of molecules) can be created from:

  User interface (clicking buttons, and setting values)
  Data Model (loading from a .blend file or an external data model file)
  CellBlender API (currently the test suite, but possibly more general)
  Reading a Visualization file without any molecules defined (CellBlender 0)

One of the key goals of the molecules module is to provide the proper
class structures and methods to support those different creation modes.

In general, creating the MCell data for a molecule (in CellBlender) will
also immediately create the Blender data (glyph, empty position mesh,...).
This allows the "Blender data" (glyph, size, color, mesh) to be created,
seen, and modified without running any simulations. Similarly, reading
Visualization data should probably create molecules as needed.

This leads to a "create as needed" mechanism for both MCell data and
Blender data. The "as needed" part will be based on the molecule name
as the "key". If that "key" exists in any context, then that data will
be used or updated. If that "key" does not exist in any context, then
new data will be created for that key.
"""

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty
from bpy.app.handlers import persistent
import math
import mathutils

# python imports
import re
import os
import random

import cellblender
from . import data_model
# from . import cellblender_parameters
from . import parameter_system
from . import cellblender_mol_viz
from . import cellblender_utils

from . import cellblender_glyphs


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def set_molecule_glyph ( context, glyph_name ):

    mcell = context.scene.mcell
    meshes = bpy.data.meshes
    mcell.molecule_glyphs.status = ""
    select_objs = context.selected_objects
    if (len(select_objs) != 1):
        mcell.molecule_glyphs.status = "Select One Molecule"
        return
    if (select_objs[0].type != 'MESH'):
        mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
        return

    mol_obj = select_objs[0]
    mol_shape_name = mol_obj.name

    # There may be objects in the scene with the same name as the glyphs in
    # the glyph library, so we need to deal with this possibility
    new_glyph_name = glyph_name
    if glyph_name in meshes:
        # pattern: glyph name, period, numbers. (example match: "Cube.001")
        pattern = re.compile(r'%s(\.\d+)' % glyph_name)
        competing_names = [m.name for m in meshes if pattern.match(m.name)]
        # example: given this: ["Cube.001", "Cube.3"], make this: [1, 3]
        trailing_nums = [int(n.split('.')[1]) for n in competing_names]
        # remove dups & sort... better way than list->set->list?
        trailing_nums = list(set(trailing_nums))
        trailing_nums.sort()
        i = 0
        gap = False
        for i in range(0, len(trailing_nums)):
            if trailing_nums[i] != i+1:
                gap = True
                break
        if not gap and trailing_nums:
            i+=1
        new_glyph_name = "%s.%03d" % (glyph_name, i + 1)

    if (bpy.app.version[0] > 2) or ( (bpy.app.version[0]==2) and (bpy.app.version[1] > 71) ):
      bpy.ops.wm.link(
          directory=mcell.molecule_glyphs.glyph_lib,
          files=[{"name": glyph_name}], link=False, autoselect=False)
    else:
      bpy.ops.wm.link_append(
          directory=mcell.molecule_glyphs.glyph_lib,
          files=[{"name": glyph_name}], link=False, autoselect=False)

    mol_mat = mol_obj.material_slots[0].material
    new_mol_mesh = meshes[new_glyph_name]
    mol_obj.data = new_mol_mesh
    mol_obj.hide_select = True
    meshes.remove(meshes[mol_shape_name])

    new_mol_mesh.name = mol_shape_name
    new_mol_mesh.materials.append(mol_mat)

"""
class MCellMoleculeGlyphsPropertyGroup(bpy.types.PropertyGroup):
    glyph_lib = os.path.join(
        os.path.dirname(__file__), "glyph_library.blend/Mesh/")
    glyph_enum = [
        ('Cone', "Cone", ""),
        ('Cube', "Cube", ""),
        ('Cylinder', "Cylinder", ""),
        ('Icosahedron', "Icosahedron", ""),
        ('Octahedron', "Octahedron", ""),
        ('Receptor', "Receptor", ""),
        ('Sphere_1', "Sphere_1", ""),
        ('Sphere_2', "Sphere_2", ""),
        ('Torus', "Torus", "")]
    glyph = EnumProperty(items=glyph_enum, name="Molecule Shapes")
    show_glyph = BoolProperty(name="Show Glyphs",description="Show Glyphs ... can cause slowness!!",default=True)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Molecule Glyph Properties... no collections to remove." )
"""




# Molecule Operators:

class MCELL_OT_molecule_add(bpy.types.Operator):
    bl_idname = "mcell.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule type to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.add_molecule(context)
        return {'FINISHED'}

class MCELL_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "mcell.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.remove_active_molecule(context)
        self.report({'INFO'}, "Deleted Molecule")
        return {'FINISHED'}


class MCELL_OT_set_molecule_glyph(bpy.types.Operator):
    bl_idname = "mcell.set_molecule_glyph"
    bl_label = "Set Molecule Glyph"
    bl_description = "Set molecule glyph to desired shape in glyph library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        mcell.molecule_glyphs.status = ""
        select_objs = context.selected_objects
        if (len(select_objs) != 1):
            mcell.molecule_glyphs.status = "Select One Molecule"
            return {'FINISHED'}
        if (select_objs[0].type != 'MESH'):
            mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
            return {'FINISHED'}

        glyph_name = mcell.molecule_glyphs.glyph

        set_molecule_glyph ( context, glyph_name )

        return {'FINISHED'}



# Callbacks for all Property updates appear to require global (non-member) functions.
# This is circumvented by simply calling the associated member function passed as self:
""" Old Callbacks called corresponding from class ... new version should do this as well """
def check_callback(self, context):
    self.check_callback(context)
    return


def display_callback(self, context):
    self.display_callback(context)
    return



def name_change_callback(self, context):
    print ( "name_change_callback called with self = " + str(self) )
    print ( "  old = " + self.old_name + " => new = " + self.name )
    old_mol_name = "mol_" + self.old_name
    new_mol_name = "mol_" + self.name

    if old_mol_name + '_mat' in bpy.data.materials:
        bpy.data.materials[old_mol_name + '_mat'].name = new_mol_name + '_mat'
    if old_mol_name + '_shape' in bpy.data.meshes:
        bpy.data.meshes[old_mol_name + '_shape'].name = new_mol_name + '_shape'
    if old_mol_name + '_shape' in bpy.data.objects:
        bpy.data.objects[old_mol_name + '_shape'].name = new_mol_name + '_shape'
    if old_mol_name + '_pos' in bpy.data.meshes:
        bpy.data.meshes[old_mol_name + '_pos'].name = new_mol_name + '_pos'
    if old_mol_name in bpy.data.objects:
        bpy.data.objects[old_mol_name].name = new_mol_name

    self.old_name = self.name

    #self.check_callback(context)
    return


def glyph_visibility_callback(self, context):
    # print ( "Glyph vis change callback for molecule " + self.name )
    ms = context.scene.mcell
    show_name = "mol_" + self.name
    show_shape_name = show_name + "_shape"
    objs = context.scene.objects
    objs[show_name].hide = not self.glyph_visibility
    objs[show_shape_name].hide = not self.glyph_visibility
    return

def glyph_show_only_callback(self, context):
    # print ( "Glyph show only callback for molecule " + self.name )
    # Note the check before set to keep from infinite recursion in properties!!
    if self.glyph_show_only != False:
        self.glyph_show_only = False
    ms = context.scene.mcell.molecules
    ml = ms.molecule_list
    show_only_name = "mol_" + self.name
    show_only_shape_name = show_only_name + "_shape"
    show_only_items = [show_only_name, show_only_shape_name]
    # print ( "Only showing " + str(show_only_items) )
    
    # Note the check before set to keep from infinite recursion in properties!!
    for o in context.scene.objects:
        if o.name.startswith("mol_"):
            if o.name in show_only_items:
                if o.hide != False:
                    o.hide = False
            else:
                if o.hide != True:
                    o.hide = True
    for o in ml:
        if o.name == self.name:
            if o.glyph_visibility != True:
                o.glyph_visibility = True
        else:
            if o.glyph_visibility != False:
                o.glyph_visibility = False
    if self.name in ms.molecule_list:
        # Select this item in the list as well
        ms.active_mol_index = ms.molecule_list.find ( self.name )
    return

def shape_change_callback(self, context):
    print ( "Shape change callback for molecule " + self.name )
    self.create_mol_data () # ( context )
    return

class MCELL_OT_mol_shade_flat(bpy.types.Operator):
    bl_idname = "mcell.mol_shade_flat"
    bl_label = "Shade Flat"
    bl_description = "Apply flat shading to this molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mols = context.scene.mcell.molecules
        if len(mols.molecule_list) > 0:
            mol = mols.molecule_list[mols.active_mol_index]
            if mol:
                shape_name = 'mol_' + mol.name + '_shape'
                cur_sel = bpy.data.objects[shape_name].select
                bpy.data.objects[shape_name].select = True
                bpy.ops.object.shade_flat()
                bpy.data.objects[shape_name].select = cur_sel
        return {'FINISHED'}

class MCELL_OT_mol_shade_smooth(bpy.types.Operator):
    bl_idname = "mcell.mol_shade_smooth"
    bl_label = "Shade Smooth"
    bl_description = "Apply smooth shading to this molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mols = context.scene.mcell.molecules
        if len(mols.molecule_list) > 0:
            mol = mols.molecule_list[mols.active_mol_index]
            if mol:
                shape_name = 'mol_' + mol.name + '_shape'
                cur_sel = bpy.data.objects[shape_name].select
                bpy.data.objects[shape_name].select = True
                bpy.ops.object.shade_smooth()
                bpy.data.objects[shape_name].select = cur_sel
        return {'FINISHED'}


import os

def remove_mol_data_by_name ( mol_name, context ):

    print ( "Call to: \"remove_mol_data_by_name\" to remove " + mol_name )

    meshes = bpy.data.meshes
    mats = bpy.data.materials
    objs = bpy.data.objects
    scn = bpy.context.scene
    scn_objs = scn.objects

    mol_obj_name        = "mol_" + mol_name
    mol_shape_obj_name  = mol_obj_name + "_shape"
    mol_shape_mesh_name = mol_obj_name + "_shape"
    mol_pos_mesh_name   = mol_obj_name + "_pos"
    mol_material_name   = mol_obj_name + "_mat"

    mols_obj = objs.get("molecules")

    mol_obj = objs.get(mol_obj_name)
    mol_shape_obj = objs.get(mol_shape_obj_name)
    mol_shape_mesh = meshes.get(mol_shape_mesh_name)
    mol_pos_mesh = meshes.get(mol_pos_mesh_name)
    mol_material = mats.get(mol_material_name)

    if mol_obj:
        scn_objs.unlink ( mol_obj )

    if mol_shape_obj:
        scn_objs.unlink ( mol_shape_obj )

    if mol_obj:
        if mol_obj.users <= 0:
            try: objs.remove ( mol_obj )
            except: pass
            try: meshes.remove ( mol_pos_mesh )
            except: pass

    if mol_shape_obj:
        if mol_shape_obj.users <= 0:
            try: objs.remove ( mol_shape_obj )
            except: pass
            try: meshes.remove ( mol_shape_mesh )
            except: pass

    if mol_material:
        if mol_material.users <= 0:
            try: mats.remove ( mol_material )
            except: pass


class MCellMoleculeProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    name = StringProperty(
        name="Molecule Name", default="Molecule",
        description="The molecule species name",
        update=name_change_callback)
    old_name = StringProperty(name="Old Mol Name", default="Molecule")

    shape_name = StringProperty(name="ShapeName", default="")
    material_name = StringProperty(name="MatName", default="")

    glyph_visibility = BoolProperty ( default=True, description='Show this molecule glyph', update=glyph_visibility_callback )
    glyph_show_only = BoolProperty ( default=False, description='Show only this molecule glyph', update=glyph_show_only_callback )

    id = IntProperty(name="Molecule ID", default=0)
    type_enum = [
        ('2D', "Surface Molecule", ""),
        ('3D', "Volume Molecule", "")]
    type = EnumProperty(
        items=type_enum, name="Molecule Type",
        default='3D',
        description="Surface molecules are constrained to surfaces/meshes. "    
                    "Volume molecules exist in space.")
    diffusion_constant = PointerProperty ( name="Molecule Diffusion Constant", type=parameter_system.Parameter_Reference )
    lr_bar_trigger = BoolProperty("lr_bar_trigger", default=False)
    bnglLabel = StringProperty(
        name="BNGL Label", default="",
        description="The molecule BNGL label",
        update=check_callback)
    target_only = BoolProperty(
        name="Target Only",
        description="If selected, molecule will not initiate reactions when "
                    "it runs into other molecules. Can speed up simulations.")

    custom_time_step =   PointerProperty ( name="Molecule Custom Time Step",   type=parameter_system.Parameter_Reference )
    custom_space_step =  PointerProperty ( name="Molecule Custom Space Step",  type=parameter_system.Parameter_Reference )
    # TODO: Add after data model release:  maximum_step_length =  PointerProperty ( name="Maximum Step Length",  type=parameter_system.Parameter_Reference )

    usecolor = BoolProperty ( name="Use this Color", default=True, description='Use Molecule Color instead of Material Color', update=display_callback )
    color = FloatVectorProperty ( name="", min=0.0, max=1.0, default=(0.5,0.5,0.5), subtype='COLOR', description='Molecule Color', update=display_callback )
    alpha = FloatProperty ( name="Alpha", min=0.0, max=1.0, default=1.0, description="Alpha (inverse of transparency)", update=display_callback )
    emit = FloatProperty ( name="Emit", min=0.0, default=1.0, description="Emits Light (brightness)", update=display_callback )
    scale = FloatProperty ( name="Scale", min=0.0001, default=1.0, description="Relative size (scale) for this molecule", update=shape_change_callback )
    previous_scale = FloatProperty ( name="Previous_Scale", min=0.0, default=1.0, description="Previous Scale" )
    #cumulative_scale = FloatProperty ( name="Cumulative_Scale", min=0.0, default=1.0, description="Cumulative Scale" )

    glyph_lib = os.path.join(os.path.dirname(__file__), "glyph_library.blend", "Mesh", "")
    glyph_enum = [
        ('Sphere_1', "Sphere_1", ""),
        ('Cone', "Cone", ""),
        ('Cube', "Cube", ""),
        ('Cylinder', "Cylinder", ""),
        ('Icosahedron', "Icosahedron", ""),
        ('Octahedron', "Octahedron", ""),
        ('Receptor', "Receptor", ""),
        ('Sphere_2', "Sphere_2", ""),
        ('Torus', "Torus", ""),
        ('Tetrahedron', "Tetrahedron", ""),
        ('Pyramid', "Pyramid", ""),
        ('Letter', "Letter", "")]
    glyph = EnumProperty ( items=glyph_enum, name="Molecule Shape", update=shape_change_callback )

    letter_enum = [
        ('A', "A", ""),
        ('B', "B", ""),
        ('C', "C", ""),
        ('D', "D", ""),
        ('E', "E", ""),
        ('F', "F", ""),
        ('G', "G", ""),
        ('H', "H", ""),
        ('I', "I", ""),
        ('J', "J", ""),
        ('K', "K", ""),
        ('L', "L", ""),
        ('M', "M", ""),
        ('N', "N", ""),
        ('O', "O", ""),
        ('P', "P", ""),
        ('Q', "Q", ""),
        ('R', "R", ""),
        ('S', "S", ""),
        ('T', "T", ""),
        ('U', "U", ""),
        ('V', "V", ""),
        ('W', "W", ""),
        ('X', "X", ""),
        ('Y', "Y", ""),
        ('Z', "Z", "")]
    letter = EnumProperty ( items=letter_enum, name="Molecule Letter", update=shape_change_callback )

    export_viz = bpy.props.BoolProperty(
        default=False, description="If selected, the molecule will be "
                                   "included in the visualization data.")
    status = StringProperty(name="Status")


    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    bngl_label_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    target_only_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )


    def init_properties ( self, parameter_system ):
        self.name = "Molecule_"+str(self.id)
        self.old_name = self.name

        helptext = "Molecule Diffusion Constant\n" + \
                   "This molecule diffuses in space with 3D diffusion constant for volume molecules.\n" + \
                   "This molecule diffuses on a surface with 2D diffusion constant for surface molecules.\n" + \
                   "The Diffusion Constant can be zero, in which case the molecule doesn’t move."
        self.diffusion_constant.init_ref   ( parameter_system, "Mol_Diff_Const_Type", user_name="Diffusion Constant",   user_expr="0", user_units="cm^2/sec", user_descr=helptext )

        helptext = "Molecule Custom Time Step\n" + \
                   "This molecule should take timesteps of this length (in seconds).\n" + \
                   "Use either this or CUSTOM_SPACE_STEP, not both."
        self.custom_time_step.init_ref     ( parameter_system, "Mol_Time_Step_Type",  user_name="Custom Time Step",     user_expr="",  user_units="seconds",  user_descr=helptext )

        helptext = "Molecule Custom Space Step\n" + \
                   "This molecule should take steps of this average length (in microns).\n" + \
                   "If you use this directive, do not set CUSTOM_TIME_STEP.\n" + \
                   "Providing a CUSTOM_SPACE_STEP for a molecule overrides a potentially\n" + \
                   "present global SPACE_STEP for this particular molecule."
        self.custom_space_step.init_ref    ( parameter_system, "Mol_Space_Step_Type", user_name="Custom Space Step",    user_expr="",  user_units="microns",  user_descr=helptext )
        self.create_mol_data() #(context)
        # TODO: Add after data model release:  self.maximum_step_length.init_ref  ( parameter_system, "Max_Step_Len_Type",   user_name="Maximum Step Length",  user_expr="",  user_units="microns",  user_descr="Molecule should never step farther than this length during a single timestep. Use with caution (see documentation)." )


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Properties ... not implemented yet!" )
        ps = context.scene.mcell.parameter_system
        self.diffusion_constant.clear_ref ( ps )
        self.custom_time_step.clear_ref ( ps )
        self.custom_space_step.clear_ref ( ps )
        self.remove_mol_data ( context )


    def initialize ( self, context ):
        # This assumes that the ID has already been assigned!!!
        self.name = "Molecule_"+str(self.id)
        self.old_name = self.name
        self.glyph = self.glyph_enum[random.randint(0,len(self.glyph_enum)-1)][0]
        self.create_mol_data() # (context)


    def create_mol_data ( self ):

        print ( "Creating mol data for " + self.name )

        meshes = bpy.data.meshes
        mats = bpy.data.materials
        objs = bpy.data.objects
        scn = bpy.context.scene
        scn_objs = scn.objects

        mol_name = "mol_" + self.name
        mol_pos_mesh_name = mol_name + "_pos"
        shape_name = mol_name + "_shape"
        material_name = mol_name + "_mat"


        # First be sure that the parent "empty" for holding molecules is available (create as needed)
        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])
            mols_obj = bpy.context.selected_objects[0]
            mols_obj.name = "molecules"
            mols_obj.location.x = 0
            mols_obj.location.y = 0
            mols_obj.location.z = 0
            mols_obj.lock_location[0] = True
            mols_obj.lock_location[1] = True
            mols_obj.lock_location[2] = True
            mols_obj.lock_rotation[0] = True
            mols_obj.lock_rotation[1] = True
            mols_obj.lock_rotation[2] = True
            mols_obj.lock_scale[0] = True
            mols_obj.lock_scale[1] = True
            mols_obj.lock_scale[2] = True
            mols_obj.select = False
            mols_obj.hide_select = True
            mols_obj.hide = True

        # Build the new shape vertices and faces
        # print ( "Creating a new glyph for " + self.name )

        size = 1.0 * self.scale
        glyph_name = self.glyph
        if glyph_name == "Letter":
            glyph_name = "Letter_" + self.letter
        shape_plf = cellblender_glyphs.get_named_shape ( glyph_name, size_x=size, size_y=size, size_z=size )

        shape_vertices = []
        for point in shape_plf.points:
            shape_vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
        shape_faces = []
        for face_element in shape_plf.faces:
            shape_faces.append ( face_element.verts )


        # Delete the old object and mesh
        if shape_name in objs:
            scn_objs.unlink ( objs[shape_name] )
            objs.remove ( objs[shape_name] )
        if shape_name in meshes:
            meshes.remove ( meshes[shape_name] )

        # Create and build the new mesh
        mol_shape_mesh = bpy.data.meshes.new ( shape_name )
        mol_shape_mesh.from_pydata ( shape_vertices, [], shape_faces )
        mol_shape_mesh.update()

        # Create the new shape object from the mesh
        mol_shape_obj = bpy.data.objects.new ( shape_name, mol_shape_mesh )
        # Be sure the new shape is at the origin, and lock it there.
        mol_shape_obj.location.x = 0
        mol_shape_obj.location.y = 0
        mol_shape_obj.location.z = 0
        mol_shape_obj.lock_location[0] = True
        mol_shape_obj.lock_location[1] = True
        mol_shape_obj.lock_location[2] = True
        mol_shape_obj.track_axis = "POS_Z"
        # Allow the shape to be selected so it can have its size changed like any other object.
        mol_shape_obj.hide_select = False

        # Add the shape to the scene as a glyph for the object
        scn.objects.link ( mol_shape_obj )

        # Look-up material, create if needed.
        # Associate material with mesh shape.
        # Bob: Maybe we need to associate it with the OBJECT with: shape_object.material_slots[0].link = 'OBJECT'
        mol_mat = mats.get(material_name)
        if not mol_mat:
            mol_list = bpy.context.scene.mcell.molecules

            def_colors = [ (1,0,0), (0,1,0), (0,0,1), (0,1,1), (1,0,1), (1,1,0), (1,1,1), (0,0,0) ]
            print ( "next_color = " + str(mol_list.next_color) )
            new_color = [ 1.0*c for c in def_colors[mol_list.next_color] ]
            print ( "new_color = " + str(new_color) )
            mol_list.next_color += 1
            if mol_list.next_color >= len(def_colors):
               mol_list.next_color = 0
            mol_mat = mats.new(material_name)
            # Need to pick a color here ?
            color = mol_mat.diffuse_color
            color[0] = new_color[0]
            color[1] = new_color[1]
            color[2] = new_color[2]
        if not mol_shape_mesh.materials.get(material_name):
            mol_shape_mesh.materials.append(mol_mat)

        # Create a "mesh" to hold instances of molecule positions
        mol_pos_mesh = meshes.get(mol_pos_mesh_name)
        if not mol_pos_mesh:
            mol_pos_mesh = meshes.new(mol_pos_mesh_name)

        # Create object to contain the mol_pos_mesh data
        mol_obj = objs.get(mol_name)
        if not mol_obj:
            mol_obj = objs.new(mol_name, mol_pos_mesh)
            scn_objs.link(mol_obj)
            mol_shape_obj.parent = mol_obj
            mol_obj.dupli_type = 'VERTS'
            mol_obj.use_dupli_vertices_rotation = True
            mol_obj.parent = mols_obj

        # Be sure the new object is at the origin, and lock it there.
        mol_obj.location.x = 0
        mol_obj.location.y = 0
        mol_obj.location.z = 0
        mol_obj.lock_location[0] = True
        mol_obj.lock_location[1] = True
        mol_obj.lock_location[2] = True
        # Also lock the rotation and scaling for the molecule positions.
        mol_obj.lock_rotation[0] = True
        mol_obj.lock_rotation[1] = True
        mol_obj.lock_rotation[2] = True
        mol_obj.lock_scale[0] = True
        mol_obj.lock_scale[1] = True
        mol_obj.lock_scale[2] = True

        # Allow the molecule locations to be selected ... this may either help or become annoying.
        mol_obj.hide_select = False

        # Add the shape to the scene as a glyph for the object
        mol_obj.dupli_type = 'VERTS'
        mol_shape_obj.parent = mol_obj

        print ( "Done creating mol data for " + self.name )



    def remove_mol_data ( self, context ):
        remove_mol_data_by_name ( self.name, context )


    def build_data_model_from_properties ( self ):
        m = self

        m_dict = {}
        m_dict['data_model_version'] = "DM_2016_01_13_1930"
        m_dict['mol_name'] = m.name
        m_dict['mol_bngl_label'] = m.bnglLabel
        m_dict['mol_type'] = str(m.type)
        m_dict['diffusion_constant'] = m.diffusion_constant.get_expr()
        m_dict['target_only'] = m.target_only
        m_dict['custom_time_step'] = m.custom_time_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        # TODO: Add after data model release:   m_dict['maximum_step_length'] = m.maximum_step_length.get_expr()
        m_dict['maximum_step_length'] = ""  # TODO: Remove this line after data model release
        m_dict['export_viz'] = m.export_viz
        disp_dict = {}
        disp_dict['glyph'] = str(m.glyph)
        if m.glyph == 'Letter':
            disp_dict['letter'] = str(m.letter)
        mat_name = "mol_" + self.name+"_mat"
        if mat_name in bpy.data.materials:
            color = bpy.data.materials[mat_name].diffuse_color
            disp_dict['color'] = [ color[0], color[1], color[2] ]
            disp_dict['emit'] = bpy.data.materials[mat_name].emit
            disp_dict['scale'] = self.scale
        m_dict['display'] = disp_dict
        return m_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculeProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            # Change on June 2nd, 2015: the mol_bngl_label field was added, but data model update wasn't done until July 24th, 2015
            dm['mol_bngl_label'] = ""
            dm['data_model_version'] = "DM_2015_07_24_1330"

        if dm['data_model_version'] == "DM_2015_07_24_1330":
            # Change in mid January, 2016: Add display information previously stored only in the object's materials
            disp_dict = {}
            # We may not know the glyph used for a molecule because it's set with an operator that builds the mesh.
            # The old "glyph" variable may be defaulted to "Cone" regardless of how it was displayed in that file.
            # We could examine the mesh to figure out what it is, but for now just go with volume / surface defaults.
            # Volume molecules will be Icosahedrons and Surface molecules will be Cones.
            disp_dict['glyph'] = "Icosahedron"
            if 'mol_type' in dm:
                if dm['mol_type'] == '2D':
                    disp_dict['glyph'] = "Cone"
            disp_dict['letter'] = "A"
            # Set various defaults to be used if no corresponding material or object is found
            disp_dict['color'] = [ 0.8, 0.8, 0.8 ]
            disp_dict['emit'] = 0.0
            disp_dict['scale'] = 1.0
            # Look for a material that may exist before the upgrade to replace the defaults
            mat_name = "mol_" + dm['mol_name'] + "_mat"
            if mat_name in bpy.data.materials:
                color = bpy.data.materials[mat_name].diffuse_color
                disp_dict['color'] = [ color[0], color[1], color[2] ]
                disp_dict['emit'] = bpy.data.materials[mat_name].emit
            # Look for an object that may exist before the upgrade to replace the defaults
            shape_name = "mol_" + dm['mol_name'] + "_shape"
            if shape_name in bpy.data.objects:
                scale = bpy.data.objects[shape_name].scale
                disp_dict['scale'] = ( scale[0] + scale[1] + scale[2] ) / 3.0
            dm['display'] = disp_dict
            dm['data_model_version'] = "DM_2016_01_13_1930"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2016_01_13_1930":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model " + str(dm['data_model_version']) + " to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm_dict ):
        # Check that the data model version matches the version for this property group
        if dm_dict['data_model_version'] != "DM_2016_01_13_1930":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model " + str(dm['data_model_version']) + " to current version." )
        # Now convert the updated Data Model into CellBlender Properties
        self.name = dm_dict["mol_name"]
        if "mol_bngl_label" in dm_dict: self.bnglLabel = dm_dict['mol_bngl_label']
        if "mol_type" in dm_dict: self.type = dm_dict["mol_type"]
        if "diffusion_constant" in dm_dict: self.diffusion_constant.set_expr ( dm_dict["diffusion_constant"] )
        if "target_only" in dm_dict: self.target_only = dm_dict["target_only"]
        if "custom_time_step" in dm_dict: self.custom_time_step.set_expr ( dm_dict["custom_time_step"] )
        if "custom_space_step" in dm_dict: self.custom_space_step.set_expr ( dm_dict["custom_space_step"] )
        # TODO: Add after data model release:   self.maximum_step_length.set_expr ( dm_dict["maximum_step_length"] )
        if "export_viz" in dm_dict: self.export_viz = dm_dict["export_viz"]

        if "display" in dm_dict:
            disp_dict = dm_dict['display']
            if "glyph" in disp_dict: self.glyph = disp_dict["glyph"]
            if "letter" in disp_dict: self.letter = disp_dict["letter"]
            if "scale"  in disp_dict: self.scale = disp_dict["scale"]

        self.create_mol_data()

        if "display" in dm_dict:
            disp_dict = dm_dict['display']
            if "color" in disp_dict:
                dm_color = disp_dict['color']
                mat_name = "mol_" + self.name+"_mat"
                if mat_name in bpy.data.materials:
                    color = bpy.data.materials[mat_name].diffuse_color
                    color[0] = dm_color[0]
                    color[1] = dm_color[1]
                    color[2] = dm_color[2]
            if "emit" in disp_dict:
                mat_name = "mol_" + self.name+"_mat"
                bpy.data.materials[mat_name].emit = disp_dict['emit']


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    # Exporting to an MDL file could be done just like this
    def print_details( self ):
        print ( "Name = " + self.name )

    def draw_props ( self, layout, molecules, parameter_system ):

        helptext = "Molecule Name\nThis is the name used in Reactions and Display"
        parameter_system.draw_prop_with_help ( layout, "Name", self, "name", "name_show_help", self.name_show_help, helptext )

        helptext = "This is a BNGL label that is used to identify a given species \n \
                    as a complex molecule."
        parameter_system.draw_prop_with_help ( layout, "BNGL Label", self, "bnglLabel", "bngl_label_show_help", self.bngl_label_show_help, helptext )

        helptext = "Molecule Type: Either Volume or Surface\n" + \
                   "Volume molecules are placed in and diffuse in 3D spaces." + \
                   "Surface molecules are placed on and diffuse on 2D surfaces."
        parameter_system.draw_prop_with_help ( layout, "Molecule Type", self, "type", "type_show_help", self.type_show_help, helptext )

        self.diffusion_constant.draw(layout,parameter_system)
        #self.lr_bar_trigger = False
        
        lr_bar_display = 0
        if len(self.custom_space_step.get_expr().strip()) > 0:
            # Set lr_bar_display directly
            lr_bar_display = self.custom_space_step.get_value()
        else:
            # Calculate lr_bar_display from diffusion constant and time step
            dc = 1e8 * self.diffusion_constant.get_value() # convert from cm2/s to um2/s 
            ts = bpy.context.scene.mcell.initialization.time_step.get_value()
            if len(self.custom_time_step.get_expr().strip()) > 0:
                ts = self.custom_time_step.get_value()
            lr_bar_display = 2 * math.sqrt ( 4 * dc * ts / math.pi )

        row = layout.row()
        row.label(text="lr_bar:  %.4g  microns"%(lr_bar_display), icon='BLANK1')  # BLANK1 RIGHTARROW_THIN SMALL_TRI_RIGHT_VEC DISCLOSURE_TRI_RIGHT_VEC DRIVER DOT FORWARD LINKED
        #layout.prop ( self, "lr_bar_trigger", icon='NONE', text="lr_bar: " + str(lr_bar_display) )

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_display:
            row.prop(molecules, "show_display", icon='TRIA_RIGHT', text="Display Options", emboss=False)
        else:
            row.prop(molecules, "show_display", icon='TRIA_DOWN',  text="Display Options", emboss=False)

            row = box.row()
            row.prop(self, "glyph", text="Shape")

            if self.glyph == "Letter":
                row = box.row()
                row.prop(self, "letter", text="Letter")

            mat_name = "mol_" + self.name+"_mat"
            if mat_name in bpy.data.materials:
                row = box.row()
                row.prop ( bpy.data.materials[mat_name], "diffuse_color", text="Color" )
                row = box.row()
                col = row.column()
                col.label ( "Brightness" )
                col = row.column()
                col.prop ( bpy.data.materials[mat_name], "emit", text="Emit" )
                row = box.row()
                col = row.column()
                col.label ( "Scale" )
                col = row.column()
                col.prop ( self, "scale", text="Factor" )
                row = box.row()
                col = row.column()
                col.operator ('mcell.mol_shade_smooth')
                col = row.column()
                col.operator ('mcell.mol_shade_flat')
                if len(bpy.data.materials) and (bpy.context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}):
                  if 'mcell' in bpy.context.scene.keys():
                    #print ( "Context OK, showing materials" )
                    mcell = bpy.context.scene.mcell
                    m = molecules.molecule_list[molecules.active_mol_index]
                    mat_name = "mol_" + m.name + "_mat"
                    #print ( "" + mat_name + " in bpy.data.materials = " + str(mat_name in bpy.data.materials) )
                    if mat_name in bpy.data.materials:
                      row = box.row()
                      row.alignment = 'LEFT'
                      if molecules.show_preview:
                        row.prop(molecules, "show_preview", icon='TRIA_DOWN', emboss=False, text="Material Preview (resize to refresh)")
                        box.template_preview(bpy.data.materials[mat_name])
                      else:
                        row.prop(molecules, "show_preview", icon='TRIA_RIGHT', emboss=False)
                  else:
                    print ( "mcell not found, not showing color preview" )
                    pass
            else:
                print ( "Material " + mat_name + " not found, not showing materials" )

            """
            row = box.row()
            row.label ( "Molecule Display Settings" )
            row = box.row()
            col = row.column()
            col.prop ( self, "glyph" )
            col = row.column()
            col.prop ( self, "scale" )
            row = box.row()
            col = row.column()
            mol_mat_name = 'mol_' + self.name + '_mat'
            if False and mol_mat_name in bpy.data.materials.keys():
                # This would control the actual Blender material property directly
                col.prop ( bpy.data.materials[mol_mat_name], "diffuse_color" )
                col = row.column()
                col.prop ( bpy.data.materials[mol_mat_name], "emit" )
            else:
                # This controls the molecule property which changes the Blender property via callback
                # But changing the color via the Materials interface doesn't change these values
                col.prop ( self, "color" )
                col = row.column()
                col.prop ( self, "emit" )
            #col = row.column()
            #col.prop ( self, "usecolor" )
            """

        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_advanced:
            row.prop(molecules, "show_advanced", icon='TRIA_RIGHT',
                     text="Advanced Options", emboss=False)
        else:
            row.prop(molecules, "show_advanced", icon='TRIA_DOWN',
                     text="Advanced Options", emboss=False)
            # row = box.row()
            # row.prop(self, "target_only")
            parameter_system.draw_prop_with_help ( box, "Target Only", self, "target_only", "target_only_show_help", self.target_only_show_help, 
                "Target Only - This molecule will not initiate reactions when\n" +
                "it runs into other molecules. This setting can speed up simulations\n" +
                "when applied to a molecule at high concentrations that reacts with\n" +
                "a molecule at low concentrations (it is more efficient for the\n" +
                "low-concentration molecule to trigger the reactions). This directive\n" +
                "does not affect unimolecular reactions." )
            self.custom_time_step.draw(box,parameter_system)
            self.custom_space_step.draw(box,parameter_system)


    def check_callback(self, context):
        """Allow the parent molecule list (MCellMoleculesListProperty) to do the checking"""
        cellblender_utils.get_parent(self).check(context)
        return


    def display_callback(self, context):
        """One of the display items has changed for this molecule"""
        print ( "Display for molecule \"" + self.name + "\" changed to: " + str(self.glyph) + ", color=" + str(self.color) + ", emit=" + str(self.emit) + ", scale=" + str(self.scale) )
        mol_name = 'mol_' + self.name
        mol_shape_name = mol_name + '_shape'
        if mol_shape_name in bpy.data.objects:
            if self.scale != self.previous_scale:
                # Scale by the ratio of current scale to previous scale
                bpy.data.objects[mol_shape_name].scale *= (self.scale / self.previous_scale)
                self.previous_scale = self.scale
                
            

        mol_mat_name = 'mol_' + self.name + '_mat'
        if mol_mat_name in bpy.data.materials.keys():
            if bpy.data.materials[mol_mat_name].diffuse_color != self.color:
                bpy.data.materials[mol_mat_name].diffuse_color = self.color
            if bpy.data.materials[mol_mat_name].emit != self.emit:
                bpy.data.materials[mol_mat_name].emit = self.emit


        # Refresh the scene
        self.set_mol_glyph ( context )
        cellblender_mol_viz.mol_viz_update(self,context)  # It's not clear why mol_viz_update needs a self. It's not in a class, and doesn't use the "self".
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return



    def set_mol_glyph (self, context):
        # Use exact code from MCELL_OT_set_molecule_glyph(bpy.types.Operator).execute
        # Except added a test to see if the molecule exists first!!
        
        mol_name = 'mol_' + self.name
        if mol_name in bpy.data.objects:

            # First set up the selected and active molecules

            mol_obj = bpy.data.objects['mol_' + self.name]     # Is this used before being resest below?
            mol_shape_name = 'mol_' + self.name + '_shape'

            bpy.ops.object.select_all(action='DESELECT')
            context.scene.objects[mol_shape_name].hide_select = False
            context.scene.objects[mol_shape_name].select = True
            context.scene.objects.active = bpy.data.objects[mol_shape_name]


            # Exact code starts here (allow it to duplicate some previous code for now):

            set_molecule_glyph ( context, self.glyph )

        return



    def testing_set_mol_glyph (self, context):

        ###########################################
        ###########################################
        # return
        ###########################################
        ###########################################
        
        mcell = context.scene.mcell
        meshes = bpy.data.meshes
        mcell.molecule_glyphs.status = ""
        #select_objs = context.selected_objects
        #if len(select_objs) == -123:
        #    if (len(select_objs) != 1):
        #        mcell.molecule_glyphs.status = "Select One Molecule"
        #        return {'FINISHED'}
        #    if (select_objs[0].type != 'MESH'):
        #        mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
        #        return {'FINISHED'}

        #mol_obj = select_objs[0]
        #mol_shape_name = mol_obj.name

        # Try to deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        mol_obj = bpy.data.objects['mol_' + self.name]
        mol_shape_name = 'mol_' + self.name + '_shape'
        print ( "Try to select " + mol_shape_name + " from bpy.data.objects["+self.name+"]" )
        context.scene.objects.active = bpy.data.objects[mol_shape_name]

        glyph_name = str(self.glyph)

        # There may be objects in the scene with the same name as the glyphs in
        # the glyph library, so we need to deal with this possibility
        new_glyph_name = glyph_name
        if glyph_name in meshes:
            # pattern: glyph name, period, numbers. (example match: "Cube.001")
            pattern = re.compile(r'%s(\.\d+)' % glyph_name)
            competing_names = [m.name for m in meshes if pattern.match(m.name)]
            # example: given this: ["Cube.001", "Cube.3"], make this: [1, 3]
            trailing_nums = [int(n.split('.')[1]) for n in competing_names]
            # remove dups & sort... better way than list->set->list?
            trailing_nums = list(set(trailing_nums))
            trailing_nums.sort()
            i = 0
            gap = False
            for i in range(0, len(trailing_nums)):
                if trailing_nums[i] != i+1:
                    gap = True
                    break
            if not gap and trailing_nums:
                i+=1
            new_glyph_name = "%s.%03d" % (glyph_name, i + 1)

        print ( "New Glyph Name = " + new_glyph_name )

        if (bpy.app.version[0] > 2) or ( (bpy.app.version[0]==2) and (bpy.app.version[1] > 71) ):
          bpy.ops.wm.link(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)
        else:
          bpy.ops.wm.link_append(
              directory=mcell.molecule_glyphs.glyph_lib,
              files=[{"name": glyph_name}], link=False, autoselect=False)

        mol_mat = None
        if len(mol_obj.material_slots) > 0:
          mol_mat = mol_obj.material_slots[0].material

        new_mol_mesh = meshes[new_glyph_name]
        mol_obj.data = new_mol_mesh
        ### causes a problem?  meshes.remove(meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        if mol_mat != None:
            new_mol_mesh.materials.append(mol_mat)
        print ( "Done setting molecule glyph" )






#class MCell_UL_check_molecule(bpy.types.UIList):
#    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
#        if item.status:
#            layout.label(item.status, icon='ERROR')
#        else:
#            layout.label(item.name, icon='FILE_TICK')


class MCell_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # print ("Draw with " + str(data) + " " + str(item) + " " + str(active_data) + " " + str(active_propname) + " " + str(index) )
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            col = layout.column()
            col.label(item.name, icon='FILE_TICK')

            ms = context.scene.mcell.molecules
            show_name = "mol_" + item.name
            show_shape_name = show_name + "_shape"
            objs = context.scene.objects
            #col = layout.column()
            #col.operator("mcell.molecule_show_only", icon='VIEWZOOM', text="")
            col = layout.column()
            col.prop(item, "glyph_show_only", text="", icon='VIEWZOOM')
            col = layout.column()
            if item.glyph_visibility:
                col.prop(item, "glyph_visibility", text="", icon='RESTRICT_VIEW_OFF')
            else:
                col.prop(item, "glyph_visibility", text="", icon='RESTRICT_VIEW_ON')
            #col = layout.column()
            #col.prop(objs[show_name], "hide", text="", icon='RESTRICT_VIEW_OFF')
            if ms.show_extra_columns:
                col = layout.column()
                if objs[show_name].hide:
                    # NOTE: For some reason, when Blender displays a boolean, it will use an offset of 1 for true.
                    #       So since GROUP_BONE is the icon BEFORE GROUP_VERTEX, picking it when true shows GROUP_VERTEX.
                    col.prop(objs[show_name], "hide", text="", icon='GROUP_BONE')
                else:
                    col.prop(objs[show_name], "hide", text="", icon='GROUP_VERTEX')
                col = layout.column()
                if objs[show_shape_name].hide:
                    # NOTE: For some reason, when Blender displays a boolean, it will use an offset of 1 for true.
                    #       So since GROUP_BONE is the icon BEFORE GROUP_VERTEX, picking it when true shows GROUP_VERTEX.
                    col.prop(objs[show_shape_name], "hide", text="", icon='FORCE_CHARGE')
                else:
                    col.prop(objs[show_shape_name], "hide", text="", icon='FORCE_LENNARDJONES')


class MCell_OT_molecule_show_all(bpy.types.Operator):
    bl_idname = "mcell.molecule_show_all"
    bl_label = "Show All"
    bl_description = "Show all of the molecules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.mcell.molecules
        print ( "Showing All" )
        for o in ms.molecule_list:
            if not o.glyph_visibility:
                o.glyph_visibility = True
            if o.glyph_show_only:
                o.glyph_show_only = False
        for o in context.scene.objects:
            if o.name.startswith("mol_"):
                o.hide = False
        return {'FINISHED'}


class MCell_OT_molecule_hide_all(bpy.types.Operator):
    bl_idname = "mcell.molecule_hide_all"
    bl_label = "Hide All"
    bl_description = "Hide all of the molecules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.mcell.molecules
        print ( "Hiding All" )
        for o in ms.molecule_list:
            if o.glyph_visibility:
                o.glyph_visibility = False
            if o.glyph_show_only:
                o.glyph_show_only = False
        for o in context.scene.objects:
            if o.name.startswith("mol_"):
                o.hide = True
        return {'FINISHED'}




class MCELL_PT_define_molecules(bpy.types.Panel):
    bl_label = "CellBlender - Define Molecules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw ( self, context ):
        # Call the draw function for the instance being drawn in this panel
        context.scene.mcell.molecules.draw_panel ( context, self )


class MCellMoleculesListProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    molecule_list = CollectionProperty(type=MCellMoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_preview = bpy.props.BoolProperty(default=False, name="Material Preview")
    show_extra_columns = bpy.props.BoolProperty(default=False, description="Show additional visibility control columns")

    next_color = IntProperty (default=0)  # Keeps track of the next molecule color to use


    def init_properties ( self, parameter_system ):
        if self.molecule_list:
            for mol in self.molecule_list:
                mol.init_properties(parameter_system)

    def remove_properties ( self, context ):
        print ( "Removing all %d Molecule List Properties..." % len(self.molecule_list) )
        for item in self.molecule_list:
            item.remove_properties(context)
        self.molecule_list.clear()
        self.active_mol_index = 0
        self.next_id = 1
        print ( "Done removing all Molecule List Properties." )
        
    
    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_mol = self.molecule_list.add()
        new_mol.id = self.allocate_available_id()
        new_mol.init_properties(context.scene.mcell.parameter_system)
        # new_mol.initialize(context)
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        print ( "Call to: \"remove_active_molecule\"" )
        if len(self.molecule_list) > 0:
            mol = self.molecule_list[self.active_mol_index]
            if mol:
                mol.remove_mol_data(context)
                mol.remove_properties(context)
            self.molecule_list.remove ( self.active_mol_index )
            self.active_mol_index -= 1
            if self.active_mol_index < 0:
                self.active_mol_index = 0
            if len(self.molecule_list) <= 0:
                self.next_id = 1
            if self.molecule_list:
                self.check(context)

    def build_data_model_from_properties ( self, context ):
        print ( "Molecule List building Data Model" )
        mol_dm = {}
        mol_dm['data_model_version'] = "DM_2014_10_24_1638"
        mol_list = []
        for m in self.molecule_list:
            mol_list.append ( m.build_data_model_from_properties() )
        mol_dm['molecule_list'] = mol_list
        return mol_dm

    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculesListProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculesListProperty data model to current version." )
            return None

        if "molecule_list" in dm:
            for item in dm["molecule_list"]:
                if MCellMoleculeProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):
        print ( "Call to: \"MCellMoleculesListProperty.build_properties_from_data_model\" with %d molecules" % len(self.molecule_list) )
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculesListProperty data model to current version." )

        # Now convert the Data Model into CellBlender Properties

        # Start by removing all molecules from the list
        while len(self.molecule_list) > 0:
            self.remove_active_molecule ( context )

        # For some reason, the length of the molecule list is sometimes 0 which may leave molecule objects ... delete them all
        if 'molecules' in bpy.data.objects:
            while len(bpy.data.objects['molecules'].children) > 0:
                mol_name = bpy.data.objects['molecules'].children[0].name
                remove_mol_data_by_name ( mol_name[4:], context )
                print ( "New length of molecule_list = " + str(len(bpy.data.objects['molecules'].children)) )



        # Add molecules from the data model
        if "molecule_list" in dm:
            for m in dm["molecule_list"]:
                self.add_molecule(context)
                self.molecule_list[self.active_mol_index].build_properties_from_data_model(context,m)

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def check ( self, context ):
        """Checks for duplicate or illegal molecule name"""
        # Note: Some of the list-oriented functionality is appropriate here (since this
        #        is a list), but some of the molecule-specific checks (like name legality)
        #        could be handled by the the molecules themselves. They're left here for now.

        mol = self.molecule_list[self.active_mol_index]

        status = ""

        # Check for duplicate molecule name
        mol_keys = self.molecule_list.keys()
        if mol_keys.count(mol.name) > 1:
            status = "Duplicate molecule: %s" % (mol.name)

        # Check for illegal names (Starts with a letter. No special characters.)
        mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
        m = re.match(mol_filter, mol.name)
        if m is None:
            status = "Molecule name error: %s" % (mol.name)

        mol.status = status

        return


    def allocate_available_id ( self ):
        """ Return a unique molecule ID for a new molecule """
        if len(self.molecule_list) <= 0:
            # Reset the ID to 1 when there are no more molecules
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def draw_layout ( self, context, layout ):
        """ Draw the molecule "panel" within the layout """
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            row = layout.row()
            col = row.column()
            col.template_list("MCell_UL_check_molecule", "define_molecules",
                              self, "molecule_list",
                              self, "active_mol_index",
                              rows=4)
            col = row.column(align=False)
            # Use subcolumns to group logically related buttons together
            subcol = col.column(align=True)
            subcol.operator("mcell.molecule_add", icon='ZOOMIN', text="")
            subcol.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
            subcol = col.column(align=True)
            subcol.operator("mcell.molecule_show_all", icon='RESTRICT_VIEW_OFF', text="")
            subcol.operator("mcell.molecule_hide_all", icon='RESTRICT_VIEW_ON', text="")
            subcol = col.column(align=True)
            subcol.prop (self, "show_extra_columns", icon='SCRIPTWIN', text="")

            if self.molecule_list:
                mol = self.molecule_list[self.active_mol_index]
                #mol.draw_layout ( context, layout, self )
                mol.draw_props ( layout, self, mcell.parameter_system )


            """ Old Code
            row = layout.row()
            col = row.column()
            col.template_list("MCell_UL_check_molecule", "define_molecules",
                              self, "molecule_list",
                              self, "active_mol_index",
                              rows=2)
            col = row.column(align=True)
            col.operator("mcell.molecule_add", icon='ZOOMIN', text="")
            col.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
            if self.molecule_list:
                mol = self.molecule_list[self.active_mol_index]
                # The self is needed to pass the "advanced" flag to the molecule
                mol.draw_props ( layout, self, mcell.parameter_system )
            """


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

