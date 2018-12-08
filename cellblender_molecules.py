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

# These 3 imports are for the text overlays
import blf
from mathutils import Matrix, Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

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
from . import cellblender_preferences

from . import cellblender_glyphs

class MCELL_MolLabelProps(bpy.types.PropertyGroup):
    enabled = bpy.props.BoolProperty(default=False)

    loc_x = bpy.props.IntProperty(name='LocX', default=0)
    loc_y = bpy.props.IntProperty(name='LocY', default=0)

    show_mol_labels = bpy.props.BoolProperty(name="", default=True)

print ( "Mols imported for Tom commented with " + __name__ )
# We use per module class registration/unregistration
"""
def register():
    print ( "cellblender_molecules.py.register() called" )
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.display_mol_labels = bpy.props.PointerProperty(type=MCELL_MolLabelProps)


def unregister():
    bpy.utils.unregister_module(__name__)
    MCELL_OT_mol_show_text.handle_remove(bpy.context)
    del bpy.types.WindowManager.display_mol_labels
"""

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


class MCELL_OT_mol_comp_add(bpy.types.Operator):
    bl_idname = "mcell.mol_comp_add"
    bl_label = "Add Component"
    bl_description = "Add a new component to molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.add_component(context)
        self.report({'INFO'}, "Added Component")
        return {'FINISHED'}

class MCELL_OT_mol_comp_remove(bpy.types.Operator):
    bl_idname = "mcell.mol_comp_remove"
    bl_label = "Remove Component"
    bl_description = "Remove selected component from molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.molecules.remove_active_component(context)
        self.report({'INFO'}, "Deleted Component")
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


class MCELL_OT_mol_comp_stick(bpy.types.Operator):
    bl_idname = "mcell.mol_comp_stick"
    bl_label = "Show Stick Molecule"
    bl_description = "Show a Stick Molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        meshes = bpy.data.meshes
        mats = bpy.data.materials
        objs = bpy.data.objects
        scn = bpy.context.scene
        scn_objs = scn.objects

        stick_name = "mol_comp_stick_mesh"
        shape_name = stick_name + "_shape"

        mols = context.scene.mcell.molecules
        this_mol = mols.molecule_list[mols.active_mol_index]
        num_comps = len(this_mol.component_list)
        comp_dist = this_mol.component_distance

        # Delete the old object and mesh
        if shape_name in objs:
            scn_objs.unlink ( objs[shape_name] )
            objs.remove ( objs[shape_name] )
        if shape_name in meshes:
            meshes.remove ( meshes[shape_name] )

        shape_vertices = []
        shape_lines = []
        shape_faces = []

        # Start with the origin molecule (for radial lines)
        shape_vertices.append ( mathutils.Vector((0.0, 0.0, 0.0)) )


        for index in range(num_comps):

          loc = [0.0, 0.0, 0.0]
          print ( "Mol geometry = " + this_mol.geom_type )

          if this_mol.geom_type == '2DAuto':
            loc = get_2D_auto_point ( num_comps, comp_dist, index )

          elif this_mol.geom_type == '3DAuto':
            loc = get_3D_auto_point ( num_comps, comp_dist, index )

          elif this_mol.geom_type in ['XYZ','XYZRef','XYZA','XYZVA']:
            loc[0] = this_mol.component_list[index].loc_x.get_value();
            loc[1] = this_mol.component_list[index].loc_y.get_value();
            loc[2] = this_mol.component_list[index].loc_z.get_value();

          x = loc[0]
          y = loc[1]
          z = loc[2]
          shape_vertices.append ( mathutils.Vector((x, y, z)) )
          shape_lines.append ( [0,index+1] )
          print ( "  making a stick for " + str(x) + ", " + str(y) + ", " + str(z) )

        # Create and build the new mesh
        stick_shape_mesh = bpy.data.meshes.new ( shape_name )
        stick_shape_mesh.from_pydata ( shape_vertices, shape_lines, shape_faces )
        stick_shape_mesh.update()

        # Create the new shape object from the mesh
        stick_shape_obj = bpy.data.objects.new ( shape_name, stick_shape_mesh )

        # Be sure the new shape is at the origin
        stick_shape_obj.location.x = 0
        stick_shape_obj.location.y = 0
        stick_shape_obj.location.z = 0

        # Allow the shape to be selected so it can be manipulated like any other object.
        stick_shape_obj.hide_select = False

        # Add the shape to the scene
        scn.objects.link ( stick_shape_obj )

        # Select to highlight it
        scn.objects[shape_name].select = True

        self.report({'INFO'}, "Built a Stick Molecule")
        return {'FINISHED'}


class MCELL_OT_mol_comp_nostick(bpy.types.Operator):
    bl_idname = "mcell.mol_comp_nostick"
    bl_label = "Remove Stick Molecule"
    bl_description = "Remove the Stick Molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        meshes = bpy.data.meshes
        mats = bpy.data.materials
        objs = bpy.data.objects
        scn = bpy.context.scene
        scn_objs = scn.objects

        stick_name = "mol_comp_stick_mesh"
        shape_name = stick_name + "_shape"

        # Delete the old object and mesh
        if shape_name in objs:
            scn_objs.unlink ( objs[shape_name] )
            objs.remove ( objs[shape_name] )
        if shape_name in meshes:
            meshes.remove ( meshes[shape_name] )

        self.report({'INFO'}, "Deleted Stick Molecule")
        return {'FINISHED'}


class MCELL_OT_mol_auto_key(bpy.types.Operator):
    bl_idname = "mcell.mol_auto_key"
    bl_label = "Auto Key"
    bl_description = "Automatically Key the Components"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Auto keyed")
        print ( "Auto keying components to first key" )
        mols = context.scene.mcell.molecules
        this_mol = mols.molecule_list[mols.active_mol_index]
        cl = this_mol.component_list
        # Create a list of ONLY the actual keys
        key_only_list = [ i for i in range(len(cl)) if cl[i].is_key == True ]
        if len(key_only_list) > 0:
          comp_only_list = [ i for i in range(len(cl)) if cl[i].is_key == False ]
          for i in comp_only_list:
            if cl[i].rot_index < 0:
              cl[i].rot_index = key_only_list[0]
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
    # print ( "name_change_callback called with self = " + str(self) )
    # print ( "  old = " + self.old_name + " => new = " + self.name )
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
    # print ( "Shape change callback for molecule " + self.name )
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
                obj = bpy.data.objects[shape_name]
                cellblender_utils.preserve_selection_use_operator(
                        bpy.ops.object.shade_flat, obj)
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
                obj = bpy.data.objects[shape_name]
                cellblender_utils.preserve_selection_use_operator(
                        bpy.ops.object.shade_smooth, obj)
        return {'FINISHED'}


def draw_text(context, vector, text):
    if context == None:
      print ( "draw_text: context is None" )
      return
    if vector == None:
      print ( "draw_text: vector is None" )
      return
    if text == None:
      print ( "draw_text: text is None" )
      return

    if context.region == None:
      print ( "draw_text: context.region is None" )
      return
    if context.space_data == None:
      print ( "draw_text: context.space_data is None" )
      return
    if context.space_data.region_3d == None:
      print ( "draw_text: context.space_data.region_3d is None" )
      return
    loc_x, loc_y = location_3d_to_region_2d (
        context.region,
        context.space_data.region_3d,
        vector)

    blf.position(0, loc_x, loc_y, 0)
    blf.draw(0, text)


def draw_labels_callback(self, context):
    disp_mol_labels = context.window_manager.display_mol_labels
    if disp_mol_labels.show_mol_labels:
      if context.window_manager.display_mol_labels.enabled:
        if 'molecule_labels' in context.scene.objects:
          # Add labels from the molecule_labels data
          ml_obj = context.scene.objects['molecule_labels']
          for i in range(len(ml_obj['mol_labels_index'])):
            t = ml_obj['mol_labels_index'][i]
            x = ml_obj['mol_labels_x'][i]
            y = ml_obj['mol_labels_y'][i]
            z = ml_obj['mol_labels_z'][i]
            draw_text ( context, [x,y,z], ml_obj['mol_labels_bngl'][t] )

        else:
          # Add labels to each molecule by molecule name
          for obj in context.scene.objects:
            if obj.name.startswith ( 'mol_' ):
              if not obj.name.endswith ( '_shape' ):
                mode = obj.mode
                texts = []
                mo = obj
                if type(mo.data) == bpy.types.Mesh:
                  texts.append ( (obj.name[4:],[]) )
                  verts = mo.data.vertices
                  for v in verts:
                    draw_text ( context, v.co, obj.name[4:] )


class MCELL_OT_mol_show_text(bpy.types.Operator):
    """Display mol labels"""
    bl_idname = "mcell.mol_show_text"
    bl_label = "Show Text"
    bl_description = "Display a text representation of the molecule (name or BNGL string)"
    bl_options = {'REGISTER'}

    """
    def execute(self, context):
        mols = context.scene.mcell.molecules
        if len(mols.molecule_list) > 0:
            mol = mols.molecule_list[mols.active_mol_index]
            if mol:
                shape_name = 'mol_' + mol.name + '_shape'
                obj = bpy.data.objects[shape_name]
                pass
        return {'FINISHED'}
    """

    _handle = None

    def modal(self, context, event):
        context.area.tag_redraw()
        if not context.window_manager.display_mol_labels.enabled:
            # MCELL_OT_mol_show_text.handle_remove(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    @staticmethod
    def handle_add(self, context):
        MCELL_OT_mol_show_text._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_labels_callback,
            (self, context),
            'WINDOW', 'POST_PIXEL')

    @staticmethod
    def handle_remove(context):
        _handle = MCELL_OT_mol_show_text._handle
        if _handle != None:
            bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        MCELL_OT_mol_show_text._handle = None

    def cancel(self, context):
        if context.window_manager.display_mol_labels.enabled:
            MCELL_OT_mol_show_text.handle_remove(context)
            context.window_manager.display_mol_labels.enabled = False
        return {'CANCELLED'}

    def invoke(self, context, event):
        if context.window_manager.display_mol_labels.enabled == False:
            context.window_manager.display_mol_labels.enabled = True
            context.window_manager.modal_handler_add(self)
            MCELL_OT_mol_show_text.handle_add(self, context)

            return {'RUNNING_MODAL'}
        else:
            context.window_manager.display_mol_labels.enabled = False
            MCELL_OT_mol_show_text.handle_remove(context)

            return {'CANCELLED'}

        return {'CANCELLED'}




import os

def remove_mol_data_by_name ( mol_name, context ):

    # print ( "Call to: \"remove_mol_data_by_name\" to remove " + mol_name )

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




class MCellMolComponentProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    component_name = StringProperty(default="", description="Component name")
    states_string = StringProperty(default="", description="States String")
    is_key = BoolProperty(default=False, description="Indicates that this is a Rotation Key and not a true component")
    loc_x = PointerProperty ( name="loc_x",  type=parameter_system.Parameter_Reference )
    loc_y = PointerProperty ( name="loc_y",  type=parameter_system.Parameter_Reference )
    loc_z = PointerProperty ( name="loc_z",  type=parameter_system.Parameter_Reference )
    rot_x = PointerProperty ( name="rot_x",  type=parameter_system.Parameter_Reference )
    rot_y = PointerProperty ( name="rot_y",  type=parameter_system.Parameter_Reference )
    rot_z = PointerProperty ( name="rot_z",  type=parameter_system.Parameter_Reference )
    rot_ang = PointerProperty ( name="rot_ang",  type=parameter_system.Parameter_Reference )
    rot_index = IntProperty ( name="AngleRef", default = 0, description="Index of Component/Key to use as Angle Reference (-1 defines a key)" )

    def init_properties ( self, parameter_system ):

        self.loc_x.init_ref   ( parameter_system, user_name="Component location x",   user_expr="0", user_units="microns", user_descr="loc_x" )
        self.loc_y.init_ref   ( parameter_system, user_name="Component location y",   user_expr="0", user_units="microns", user_descr="loc_y" )
        self.loc_z.init_ref   ( parameter_system, user_name="Component location z",   user_expr="0", user_units="microns", user_descr="loc_z" )

        self.rot_x.init_ref   ( parameter_system, user_name="Component rotation axis x",   user_expr="0", user_units="none", user_descr="rot_x" )
        self.rot_y.init_ref   ( parameter_system, user_name="Component rotation axis y",   user_expr="0", user_units="none", user_descr="rot_y" )
        self.rot_z.init_ref   ( parameter_system, user_name="Component rotation axis z",   user_expr="0", user_units="none", user_descr="rot_z" )

        self.rot_ang.init_ref   ( parameter_system, user_name="Component rotation angle",   user_expr="0", user_units="degrees", user_descr="rot_ang" )

    def remove_properties ( self, context ):
        print ( "Removing all Component Properties ..." )
        ps = context.scene.mcell.parameter_system
        self.loc_x.clear_ref ( ps )
        self.loc_y.clear_ref ( ps )
        self.loc_z.clear_ref ( ps )
        self.rot_x.clear_ref ( ps )
        self.rot_y.clear_ref ( ps )
        self.rot_z.clear_ref ( ps )
        self.rot_ang.clear_ref ( ps )
        print ( "Done removing all Component Properties." )


class MCell_OT_molecule_recalc_comps(bpy.types.Operator):
    bl_idname = "mcell.molecule_recalc_comps"
    bl_label = "Recalculate"
    bl_description = "Recalculate Component Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.mcell.molecules
        print ( "Recalculating Component Geometry" )
        for m in ms.molecule_list:
          if (m.geom_type == '2DAuto') or (m.geom_type == '3DAuto'):
            print ( "Updating molecule " + str(m) )
            num_comps = len(m.component_list)
            comp_dist = m.component_distance
            index = 0
            for comp in m.component_list:
              loc = []
              if m.geom_type == '2DAuto':
                loc = get_2D_auto_point ( num_comps, comp_dist, index )
              if m.geom_type == '3DAuto':
                loc = get_3D_auto_point ( num_comps, comp_dist, index )
              print ( "Move Mol Component \"" + comp.component_name + "\" to:" + str(loc) )
              comp.loc_x.set_expr ( str(loc[0]) )
              comp.loc_y.set_expr ( str(loc[1]) )
              comp.loc_z.set_expr ( str(loc[2]) )
              index += 1
        return {'FINISHED'}


class MCell_OT_molecule_2D_Circ(bpy.types.Operator):
    bl_idname = "mcell.dist_two_d_circle"
    bl_label = "Recalculate 2D"
    bl_description = "Recalculate 2D Component Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Arrange the components evenly spaced on a sphere

        print ( "Recalculating Molecule Component Geometry in 3D" )
        ps = context.scene.mcell.parameter_system
        mols = context.scene.mcell.molecules
        this_mol = mols.molecule_list[mols.active_mol_index]

        # Create a list of ONLY the actual components
        comp_only_list = [ c for c in this_mol.component_list if c.is_key == False ]
        num_comps = len(comp_only_list)
        comp_dist = this_mol.component_distance
        index = 0
        for comp in comp_only_list:
          loc = get_2D_auto_point ( num_comps, comp_dist, index )
          comp.loc_x.set_expr ( str(loc[0]) )
          comp.loc_y.set_expr ( str(loc[1]) )
          comp.loc_z.set_expr ( str(loc[2]) )
          index += 1
        return {'FINISHED'}


class MCell_OT_molecule_3D_Sp(bpy.types.Operator):
    bl_idname = "mcell.dist_three_d_sphere"
    bl_label = "Recalculate 3D"
    bl_description = "Recalculate 3D Component Geometry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Arrange the components evenly spaced on a sphere

        print ( "Recalculating Molecule Component Geometry in 3D" )
        ps = context.scene.mcell.parameter_system
        mols = context.scene.mcell.molecules
        this_mol = mols.molecule_list[mols.active_mol_index]

        # Create a list of ONLY the actual components
        comp_only_list = [ c for c in this_mol.component_list if c.is_key == False ]
        num_comps = len(comp_only_list)
        comp_dist = this_mol.component_distance
        index = 0
        for comp in comp_only_list:
          loc = get_3D_auto_point ( num_comps, comp_dist, index )
          comp.loc_x.set_expr ( str(loc[0]) )
          comp.loc_y.set_expr ( str(loc[1]) )
          comp.loc_z.set_expr ( str(loc[2]) )
          index += 1
        return {'FINISHED'}



### Using a mode change callback is one way to swap in the fields (currently disabled)
def mol_geom_type_changed_callback ( self, context ):
    print ( "Geometry Type has been changed!!" )
    print ( "self = " + str(self) )

    # ps = context.scene.mcell.parameter_system

    if self.geom_type == '2DAuto':

        # Arrange the components evenly spaced on a circle in the x-y plane
        this_mol = self
        num_comps = len(this_mol.component_list)
        comp_dist = this_mol.component_distance
        index = 0
        for comp in this_mol.component_list:
          loc = get_2D_auto_point ( num_comps, comp_dist, index )
          print ( "Move 2D Mol Component \"" + comp.component_name + "\" to:" + str(loc) )
          # These created an error: AttributeError: bpy_struct: attribute "loc_x" from "MCellMolComponentProperty" is read-only
          #comp.loc_x = loc[0]
          #comp.loc_y = loc[1]
          #comp.loc_z = loc[2]
          index += 1

    elif self.geom_type == '3DAuto':

        # Arrange the components evenly spaced on a sphere
        this_mol = self
        num_comps = len(this_mol.component_list)
        comp_dist = this_mol.component_distance
        for index in range(num_comps):
          loc = get_3D_auto_point ( num_comps, comp_dist, index )
          # print ( "Move 3D Mol Component \"" + comp.component_name + "\" to:" + str(loc) )

    # item.loc_x = x



class MCellMoleculeProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    name = StringProperty(
        name="Molecule Name", default="Molecule",
        description="The molecule species name",
        update=name_change_callback)
    old_name = StringProperty(name="Old Mol Name", default="Molecule")
    description = StringProperty(name="Description", default="")

    component_list = CollectionProperty(type=MCellMolComponentProperty, name="Component List")
    active_component_index = IntProperty(name="Active Component Index", default=0)

    geom_type_enum = [
        ('None',   "Coincident", ""),
        ('XYZRef', "XYZ,RotRef", ""),
        ('XYZVA',  "XYZ,RotAxis", ""),      # label was: "XYZ,V,A Specified"
        ('2DAuto', "---------------", ""),  # label was: "2D Auto"
        ('3DAuto', "---------------", ""),  # label was: "3D Auto"
        ('XYZ',    "---------------", ""),  # label was: "XYZ"
        ('XYZA',   "---------------", "")   # label was: "XYZ,A Specified"
        ]
    geom_type = EnumProperty(
        items=geom_type_enum, name="Geometry",
        default='None',
        description="Layout method for Complex Molecules." )
        #,
        #update=mol_geom_type_changed_callback)

    component_distance = FloatProperty ( name="R", min=0.0, default=0.01, description="Distance of Components from Molecule" )

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

    custom_time_step =    PointerProperty ( name="Molecule Custom Time Step",  type=parameter_system.Parameter_Reference )
    custom_space_step =   PointerProperty ( name="Molecule Custom Space Step", type=parameter_system.Parameter_Reference )
    maximum_step_length = PointerProperty ( name="Maximum Step Length",        type=parameter_system.Parameter_Reference )

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
    description_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    bngl_label_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    target_only_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )


    def init_properties ( self, parameter_system ):
        self.name = "Molecule_"+str(self.id)
        self.old_name = self.name

        helptext = "Molecule Diffusion Constant - \n" + \
                   "This molecule diffuses in space with 3D diffusion constant for volume molecules.\n" + \
                   "This molecule diffuses on a surface with 2D diffusion constant for surface molecules.\n" + \
                   "The Diffusion Constant can be zero, in which case the molecule doesn’t move."
        self.diffusion_constant.init_ref   ( parameter_system, user_name="Diffusion Constant",   user_expr="0", user_units="cm^2/sec", user_descr=helptext )

        helptext = "Molecule Custom Time Step - \n" + \
                   "This molecule should take timesteps of this length (in seconds).\n" + \
                   "Use either this or CUSTOM_SPACE_STEP, not both."
        self.custom_time_step.init_ref     ( parameter_system, user_name="Custom Time Step",     user_expr="",  user_units="seconds",  user_descr=helptext )

        helptext = "Molecule Custom Space Step - \n" + \
                   "This molecule should take steps of this average length (in microns).\n" + \
                   "If you use this directive, do not set CUSTOM_TIME_STEP.\n" + \
                   "Providing a CUSTOM_SPACE_STEP for a molecule overrides a potentially\n" + \
                   "present global SPACE_STEP for this particular molecule."
        self.custom_space_step.init_ref    ( parameter_system, user_name="Custom Space Step",    user_expr="",  user_units="microns",  user_descr=helptext )

        helptext = "Maximum Step Length - \n" + \
                   "This molecule should never step farther than length L (in microns) during a\n" + \
                   "single timestep. This can be used to speed up simulations by enforcing a certain\n" + \
                   "maximum step length for molecules such as molecular motors on a surface\n" + \
                   "without having to reduce the global timestep unnecessarily. Please use this\n" + \
                   "keyword with care since it may give rise to a non-equilibrium distribution of\n" + \
                   "the given molecule and also cause deviations from mass action kinetics."
        self.maximum_step_length.init_ref  ( parameter_system, user_name="Maximum Step Length",  user_expr="",  user_units="microns",  user_descr=helptext )

        self.create_mol_data() #(context)


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Properties ..." )
        ps = context.scene.mcell.parameter_system
        self.diffusion_constant.clear_ref ( ps )
        self.custom_time_step.clear_ref ( ps )
        self.custom_space_step.clear_ref ( ps )
        self.maximum_step_length.clear_ref ( ps )
        self.remove_mol_data ( context )
        self.component_list.clear()
        self.active_component_index = 0
        print ( "Done removing all Molecule Properties." )


    def initialize ( self, context ):
        # This assumes that the ID has already been assigned!!!
        self.name = "Molecule_"+str(self.id)
        self.old_name = self.name
        self.glyph = self.glyph_enum[random.randint(0,len(self.glyph_enum)-1)][0]
        self.create_mol_data() # (context)


    def create_mol_data ( self ):

        # print ( "Creating mol data for " + self.name )

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
            # print ( "next_color = " + str(mol_list.next_color) )
            new_color = [ 1.0*c for c in def_colors[mol_list.next_color] ]
            # print ( "new_color = " + str(new_color) )
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

        # print ( "Done creating mol data for " + self.name )



    def remove_mol_data ( self, context ):
        remove_mol_data_by_name ( self.name, context )


    def add_component_vals ( self, context, name, states="", is_key = False, loc_x = "0", loc_y="0", loc_z="0", rot_x="0", rot_y="0", rot_z="0", rot_ang="0", rot_index=-1 ):
        new_comp = self.component_list.add()
        new_comp.init_properties(context.scene.mcell.parameter_system)
        new_comp.component_name = name
        new_comp.states_string = states
        new_comp.is_key = is_key;
        new_comp.loc_x.set_expr ( loc_x )
        new_comp.loc_y.set_expr ( loc_y )
        new_comp.loc_z.set_expr ( loc_z )
        new_comp.rot_x.set_expr ( rot_x )
        new_comp.rot_y.set_expr ( rot_y )
        new_comp.rot_z.set_expr ( rot_z )
        new_comp.rot_ang.set_expr ( rot_ang )
        new_comp.rot_index = rot_index
        self.active_component_index = len(self.component_list)-1


    def remove_active_component ( self, context ):
        if len(self.component_list) > 0:
            self.component_list[self.active_component_index].remove_properties(context)
            self.component_list.remove ( self.active_component_index )
            self.active_component_index -= 1
            if self.active_component_index < 0:
                self.active_component_index = 0


    def build_data_model_from_properties ( self ):
        m = self
        m_dict = {}
        m_dict['data_model_version'] = "DM_2018_10_16_1632"
        m_dict['mol_name'] = m.name
        m_dict['description'] = m.description
        m_dict['spatial_structure'] = m.geom_type
        comp_list = []
        for comp in self.component_list:
          comp_list.append ( { 'cname':comp.component_name,
                               'cstates':comp.states_string.replace(',',' ').split(),
                               'is_key':comp.is_key,
                               'loc_x':comp.loc_x.get_expr(),
                               'loc_y':comp.loc_y.get_expr(),
                               'loc_z':comp.loc_z.get_expr(),
                               'rot_x':comp.rot_x.get_expr(),
                               'rot_y':comp.rot_y.get_expr(),
                               'rot_z':comp.rot_z.get_expr(),
                               'rot_ang':comp.rot_ang.get_expr(),
                               'rot_index':comp.rot_index } )
        m_dict['bngl_component_list'] = comp_list
        m_dict['mol_bngl_label'] = m.bnglLabel
        m_dict['mol_type'] = str(m.type)
        m_dict['diffusion_constant'] = m.diffusion_constant.get_expr()
        m_dict['target_only'] = m.target_only
        m_dict['custom_time_step'] = m.custom_time_step.get_expr()
        m_dict['custom_space_step'] = m.custom_space_step.get_expr()
        m_dict['maximum_step_length'] = m.maximum_step_length.get_expr()
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

        if dm['data_model_version'] == "DM_2016_01_13_1930":
            # Change on June 9th, 2017: the maximum_step_length and bngl_component_list was added
            dm['maximum_step_length'] = ""
            dm['bngl_component_list'] = []
            dm['data_model_version'] = "DM_2017_06_19_1960"

        if dm['data_model_version'] == "DM_2017_06_19_1960":
            # Change on January 11th, 2018 to add a description field to molecules
            dm['description'] = ""
            dm['data_model_version'] = "DM_2018_01_11_1330"

        if dm['data_model_version'] == "DM_2018_01_11_1330":
            # Change on July 3rd, 2018 to add component locations
            if 'bngl_component_list' in dm:
                for comp in dm['bngl_component_list']:
                    comp['x'] = '0'
                    comp['y'] = '0'
                    comp['z'] = '0'
                    comp['a'] = '0'
            dm['data_model_version'] = "DM_2018_07_03_1955"
        if dm['data_model_version'] == "DM_2018_07_03_1955":
            # Change on July 5th, 2018 to use "ang" instead of "a" as the angle key in the data model
            if 'bngl_component_list' in dm:
                for comp in dm['bngl_component_list']:
                    if 'a' in comp:
                      comp['ang'] = comp.pop('a')
            dm['data_model_version'] = "DM_2018_07_05_1450"
        if dm['data_model_version'] == "DM_2018_07_05_1450":
            # Change on August 21st, 2018 to add "loc_ x,y,z" for location keys and to use "rot_  x,y,z,ang" instead of "x,y,z,ang" as the rotation axis and angle keys in the data model
            if 'bngl_component_list' in dm:
                for comp in dm['bngl_component_list']:
                    comp['loc_x'] = '0'
                    comp['loc_y'] = '0'
                    comp['loc_z'] = '0'
                    if 'x' in comp:
                      comp['rot_x'] = comp.pop('x')
                    if 'y' in comp:
                      comp['rot_y'] = comp.pop('y')
                    if 'z' in comp:
                      comp['rot_z'] = comp.pop('z')
                    if 'ang' in comp:
                      comp['rot_ang'] = comp.pop('ang')
            dm['data_model_version'] = "DM_2018_08_21_1200"
        if dm['data_model_version'] == "DM_2018_08_21_1200":
            # Change on September 24th, 2018 to add the spatial_structure type indicator
            # Use a default of "None" for older models that had no spatial structure
            dm['spatial_structure'] = "None"
            dm['data_model_version'] = "DM_2018_09_24_1620"
        if dm['data_model_version'] == "DM_2018_09_24_1620":
            # Change on October 15th, 2018 to add the rotation angle reference index
            # Add the new rot_index field as an integer (it doesn't need to be a parameterized string for now)
            if 'bngl_component_list' in dm:
                for comp in dm['bngl_component_list']:
                    comp['rot_index'] = 0
            dm['data_model_version'] = "DM_2018_10_15_2242"
        if dm['data_model_version'] == "DM_2018_10_15_2242":
            # Change on October 16th, 2018 to add an is_key flag (reflects older "comp_not_key" variable used in some code)
            # Older code did not have rotation keys, so set them to False when upgrading
            if 'bngl_component_list' in dm:
                for comp in dm['bngl_component_list']:
                    comp['is_key'] = False
            dm['data_model_version'] = "DM_2018_10_16_1632"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2018_10_16_1632":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model " + str(dm['data_model_version']) + " to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm_dict ):
        # Check that the data model version matches the version for this property group
        if dm_dict['data_model_version'] != "DM_2018_10_16_1632":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model " + str(dm['data_model_version']) + " to current version." )
        # Now convert the updated Data Model into CellBlender Properties
        self.name = dm_dict["mol_name"]
        self.description = dm_dict["description"]
        if "bngl_component_list" in dm_dict:
            for comp in dm_dict["bngl_component_list"]:
                self.add_component_vals ( context, comp['cname'], " ".join(comp['cstates']), comp['is_key'], comp['loc_x'], comp['loc_y'], comp['loc_z'], comp['rot_x'], comp['rot_y'], comp['rot_z'], comp['rot_ang'], comp['rot_index'] )
        if "mol_bngl_label" in dm_dict: self.bnglLabel = dm_dict['mol_bngl_label']
        if "spatial_structure" in dm_dict: self.geom_type = dm_dict["spatial_structure"]
        if "mol_type" in dm_dict: self.type = dm_dict["mol_type"]
        if "diffusion_constant" in dm_dict: self.diffusion_constant.set_expr ( dm_dict["diffusion_constant"] )
        if "target_only" in dm_dict: self.target_only = dm_dict["target_only"]
        if "custom_time_step" in dm_dict: self.custom_time_step.set_expr ( dm_dict["custom_time_step"] )
        if "custom_space_step" in dm_dict: self.custom_space_step.set_expr ( dm_dict["custom_space_step"] )
        if "maximum_step_length" in dm_dict: self.maximum_step_length.set_expr ( dm_dict["maximum_step_length"] )
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

        helptext = "Molecule Name - \nThis is the name used in Reactions and Display"
        parameter_system.draw_prop_with_help ( layout, "Name", self, "name", "name_show_help", self.name_show_help, helptext )

        helptext = "Molecule Description - \nUser-specified text describing this molecule"
        parameter_system.draw_prop_with_help ( layout, "Description", self, "description", "description_show_help", self.description_show_help, helptext )

        helptext = "Molecule Type - Either Volume or Surface\n" + \
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


        if bpy.context.scene.mcell.cellblender_preferences.bionetgen_mode:

            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'LEFT'

            comp_label = "BNGL: " + self.name
            if len(self.component_list) > 0:
              comp_list = []
              for comp in self.component_list:
                cname = comp.component_name
                # state_list = comp.states_string.replace(',',' ').split() # Allows commas as separators
                state_list = comp.states_string.split()
                if len(state_list) > 0:
                  cname += "~"+"~".join(state_list)
                comp_list.append(cname)
              comp_label += " ( " + ", ".join(comp_list) + " )"

            if not molecules.show_components:
                row.prop(molecules, "show_components", icon='TRIA_RIGHT', text=comp_label, emboss=False)
                """
                col = row.column()
                col.prop(molecules, "show_components", icon='TRIA_RIGHT', text=comp_label, emboss=False)
                col = row.column()
                col.prop(self, "geom_type" );
                if (self.geom_type=="2DAuto") or (self.geom_type=="3DAuto"):
                  col = row.column()
                  col.prop(self, "component_distance")
                  col = row.column()
                  col.operator("mcell.molecule_recalc_comps", icon='FILE_REFRESH', text="")
                """
            else:
                #row.prop(molecules, "show_components", icon='TRIA_DOWN',  text=comp_label, emboss=False)
                col = row.column()
                col.prop(molecules, "show_components", icon='TRIA_DOWN',  text=comp_label, emboss=False)
                col = row.column()
                col.prop(self, "geom_type" )
                col = row.column() # Provide some space?
                col.label ( " " )
                col = row.column()
                col.prop(self, "component_distance")
                col = row.column()
                col.operator ( "mcell.dist_two_d_circle", icon='FILE_REFRESH', text='2D' )
                col = row.column()
                col.operator ( "mcell.dist_three_d_sphere", icon='FILE_REFRESH', text='3D' )
                if (self.geom_type=="2DAuto") or (self.geom_type=="3DAuto"):
                  col = row.column()
                  col.operator("mcell.molecule_recalc_comps", icon='FILE_REFRESH', text="")

                if self.geom_type == 'XYZRef':
                  row = box.row()
                  col = row.column()
                  col.label ( "Index" )
                  col = row.column()
                  col.label ( "Name" )
                  col = row.column()
                  col.label ( "States" )
                  col = row.column()
                  col.label ( "Loc: x" )
                  col = row.column()
                  col.label ( "Loc: y" )
                  col = row.column()
                  col.label ( "Loc: z" )
                  col = row.column()
                  col.label ( "Rot Ref" )

                if self.geom_type == 'XYZVA':
                  row = box.row()
                  col = row.column()
                  col.label ( "Name" )
                  col = row.column()
                  col.label ( "States" )
                  col = row.column()
                  col.label ( "Loc: x" )
                  col = row.column()
                  col.label ( "Loc: y" )
                  col = row.column()
                  col.label ( "Loc: z" )
                  col = row.column()
                  col.label ( "Rot: x" )
                  col = row.column()
                  col.label ( "Rot: y" )
                  col = row.column()
                  col.label ( "Rot: z" )
                  col = row.column()
                  col.label ( "Angle" )

                row = box.row()
                col = row.column()
                col.template_list("MCell_UL_check_component", "define_molecules",
                                  self, "component_list",
                                  self, "active_component_index",
                                  rows=4)
                col = row.column(align=False)
                # Use subcolumns to group logically related buttons together
                subcol = col.column(align=True)
                subcol.operator("mcell.mol_comp_add", icon='ZOOMIN', text="")
                subcol.operator("mcell.mol_comp_remove", icon='ZOOMOUT', text="")
                subcol = col.column(align=True)
                subcol.operator("mcell.mol_comp_stick", icon='RESTRICT_VIEW_OFF', text="")
                subcol.operator("mcell.mol_comp_nostick", icon='RESTRICT_VIEW_ON', text="")
                if self.geom_type == 'XYZRef':
                  # Only draw the mol_auto_key when appropriate
                  subcol = col.column(align=True)
                  subcol.operator("mcell.mol_auto_key", icon='KEY_HLT', text="")  # or KEY_DEHLT

                if self.component_list:
                    comp = self.component_list[self.active_component_index]


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
                col = row.column()
                col.operator ('mcell.mol_show_text')

                # Allow the user to set what layer(s) the molecule appears on
                mol = molecules.molecule_list[molecules.active_mol_index]
                mol_obj_name = "mol_" + mol.name
                mol_shape_name = mol_obj_name + "_shape"
                mol_obj = bpy.context.scene.objects.get(mol_obj_name)
                mol_shape_obj = bpy.context.scene.objects.get(mol_shape_name)
                row = box.row(align=True)
                row.prop(mol_obj, "layers")
                mol_shape_obj.layers = mol_obj.layers

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


        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'
        if not molecules.show_molmaker:
            row.prop(molecules, "show_molmaker", icon='TRIA_RIGHT',
                     text="Molecule Structure Tool", emboss=False)
        else:
            row.prop(molecules, "show_molmaker", icon='TRIA_DOWN',
                     text="Molecule Structure Tool", emboss=False)
            molmaker = bpy.context.scene.mcell.molmaker
            molmaker.draw_layout ( bpy.context, box )

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
                "when applied t molecule at high concentrations that reacts with\n" +
                "a molecule at low concentrations (it is more efficient for the\n" +
                "low-concentration molecule to trigger the reactions). This directive\n" +
                "does not affect unimolecular reactions." )
            self.custom_time_step.draw(box,parameter_system)
            self.custom_space_step.draw(box,parameter_system)
            self.maximum_step_length.draw(box,parameter_system)

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
            """
            # Example of using split to subdivide into: [0.2][     0.6     ][0.2]

            split = layout.split(percentage=0.2)
            col1 = split.column()
            remainder = split.column()
            split = remainder.split(percentage=0.6666)
            col2 = split.column()
            col3 = split.column()

            col1.label ( "11111111111111111" )
            col2.label ( "22222222222222222" )
            col3.label ( "33333333333333333" )
            """

            mcell = context.scene.mcell
            ms = mcell.molecules
            show_name = "mol_" + item.name
            show_shape_name = show_name + "_shape"
            mat_name = show_name + "_mat"
            objs = context.scene.objects

            col = layout.column()
            col.label(item.name, icon='FILE_TICK')

            sv_bngcolor_split = layout.split(percentage=0.05)
            col = sv_bngcolor_split.column()
            if item.type == '2D':
                col.label ( "", icon='TEXTURE' )  #  'OUTLINER_OB_SURFACE' 'SNAP_FACE'
            else:
                col.label ( "", icon='PHYSICS' )  #  'VIEW3D' 'OBJECT_DATA'  'SNAP_VOLUME'

            col = sv_bngcolor_split.column()
            bng_color_split = col.split(percentage=0.82)   # Amount of space for BGNL, the rest is color
            col = bng_color_split.column()
            if len(item.bnglLabel) > 0:
                col.label (item.bnglLabel)
            else:
                col.label (" ")

            col = bng_color_split.column()
            if mat_name in bpy.data.materials:
                col.prop ( bpy.data.materials[mat_name], "diffuse_color", text="" )
            else:
                col.label (" ")


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




def get_2D_auto_point ( num_components, component_radius, component_index ):
  x = 0
  y = 0
  z = 0
  angle = 2 * math.pi * component_index / num_components;
  x = component_radius * math.cos(angle)
  y = component_radius * math.sin(angle)
  if abs(x) < 1e-10:
    x = 0
  if abs(y) < 1e-10:
    y = 0
  return [x, y, z]


def get_distributed_sphere_points ( num_points ):
  points = None
  if num_points == 0:     # Define the single point along the x axis
    points = [ ]
  elif num_points == 1:     # Define the single point along the x axis
    points = [ [ 1, 0, 0 ] ]
  elif num_points == 2:   # Define the two points along the x axis
    points = [ [ 1, 0, 0 ], [ -1, 0, 0 ] ]
  elif num_points == 3:   # Define an equilateral triangle in the x-y plane with one point on x axis
    sr3o2 = math.sqrt(3.0) / 2.0
    points = [ [ 1, 0, 0 ], [ -0.5, sr3o2, 0 ], [ -0.5, -sr3o2, 0 ] ]
  elif num_points == 4:   # Define the points on a tetrahedron
    oosr2 = 1.0 / math.sqrt(2.0)
    points = [ [ 1, 0, -oosr2 ], [ -1, 0, -oosr2 ], [ 0, 1, oosr2 ], [ 0, -1, oosr2 ] ]
  elif num_points == 5:   # The "best" answer isn't clear, so place one on each pole and 3 around the "equator"
    sr3o2 = math.sqrt(3.0) / 2.0
    points = [ [ 0, 0, 1 ], [ 1, 0, 0 ], [ -0.5, sr3o2, 0 ], [ -0.5, -sr3o2, 0 ], [ 0, 0, -1 ] ]
  elif num_points == 6:   # Define 2 points on each axis (x, y, z)
    points = [
      [ 1, 0, 0 ],
      [-1, 0, 0 ],
      [ 0, 1, 0 ],
      [ 0,-1, 0 ],
      [ 0, 0, 1 ],
      [ 0, 0,-1 ] ]
  elif num_points == 8:   # Define 8 points at the corners of a cube
    d = 1.0 / math.sqrt(3)
    points = [
      [  d,  d,  d ],
      [  d,  d, -d ],
      [  d, -d,  d ],
      [  d, -d, -d ],
      [ -d,  d,  d ],
      [ -d,  d, -d ],
      [ -d, -d,  d ],
      [ -d, -d, -d ] ]
  else:   # Use the Fibonacci Sphere Algorithm ("Golden Spiral") for any undefined number of points
    points = [ [0,0,0] for i in range(num_points) ]
    rnd = 1
    offset = 2.0 / num_points
    increment = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(num_points):
      y = ((i * offset) -1) + (offset / 2)
      r = math.sqrt ( 1 - math.pow(y,2) )
      phi = ( (i+rnd) % num_points ) * increment

      x = math.cos(phi) * r
      z = math.sin(phi) * r
      points[i][0] = x
      points[i][1] = y
      points[i][2] = z
  return ( points )


def get_3D_auto_point ( num_components, component_radius, component_index ):

  x = 0
  y = 0
  z = 0

  points = get_distributed_sphere_points ( num_components )
  p = points[component_index]

  return ( [ v*component_radius for v in p ] )



class MCell_UL_check_component(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # print ("Draw with " + str(data) + " " + str(item) + " " + str(active_data) + " " + str(active_propname) + " " + str(index) )
        # print ("  Type = " + data.geom_type )

        col = layout.column()
        if data.geom_type == 'XYZRef':
          #col.label(text=str(index) + ': Component / States:', icon='NONE')
          label = str(index) + ": (Component)"
          if item.is_key:
            label = str(index) + ": (Rotation Key)"
          col.prop (item, 'is_key', text=label, icon='NONE')
        elif data.geom_type != 'XYZVA':
          col.label(text='Component / States:', icon='NONE')

        col = layout.column()
        col.prop(item, "component_name", text='', icon='NONE')

        col = layout.column()
        if (data.geom_type == 'XYZRef') and item.is_key:
          col.label(text=' ', icon='NONE')
        else:
          col.prop(item, "states_string", text='', icon='NONE')

        if data.geom_type == '2DAuto':

            # Arrange the components evenly spaced on a circle in the x-y plane
            ps = context.scene.mcell.parameter_system
            mols = context.scene.mcell.molecules
            this_mol = mols.molecule_list[mols.active_mol_index]
            num_comps = len(this_mol.component_list)
            comp_dist = this_mol.component_distance

            loc = get_2D_auto_point ( num_comps, comp_dist, index )

            x = loc[0]
            y = loc[1]
            z = loc[2]

            col = layout.column()
            col.label ( "x="+format(x,'.6g') )
            col = layout.column()
            col.label ( "y="+format(y,'.6g') )

        elif data.geom_type == '3DAuto':

            # Arrange the components evenly spaced on a sphere

            ps = context.scene.mcell.parameter_system
            mols = context.scene.mcell.molecules
            this_mol = mols.molecule_list[mols.active_mol_index]

            # Create a list of ONLY the actual components
            comp_only_list = [ c for c in this_mol.component_list if c.is_key == False ]
            # Get the index of the original item in the new comp_only_list
            x = 0
            y = 0
            z = 0
            if this_mol.component_list[index] in comp_only_list:
              comp_only_index = comp_only_list.index(this_mol.component_list[index])

              num_comps = len(comp_only_list)
              comp_dist = this_mol.component_distance

              loc = get_3D_auto_point ( num_comps, comp_dist, comp_only_index )

              x = loc[0]
              y = loc[1]
              z = loc[2]

            # Show the point
            col = layout.column()
            col.label ( "x="+format(x,'.6g') )
            col = layout.column()
            col.label ( "y="+format(y,'.6g') )
            col = layout.column()
            col.label ( "z="+format(z,'.6g') )

        elif data.geom_type == 'XYZ':

            # Arrange the components at the coordinates x, y, z

            ps = context.scene.mcell.parameter_system

            col = layout.column()
            col.label(text='loc [x,y,z]', icon='NONE')

            col = layout.column()
            item.loc_x.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_y.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_z.draw_prop_only ( col, ps )

        elif data.geom_type == 'XYZRef':

            # Arrange the components at the coordinates x, y, z with reference point (using rot_x, rot_y, rot_z)

            ps = context.scene.mcell.parameter_system

            #col = layout.column()
            #col.label(text='loc [x,y,z]', icon='NONE')

            col = layout.column()
            item.loc_x.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_y.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_z.draw_prop_only ( col, ps )

            col = layout.column()
            if item.is_key:
              col.label(text=' ', icon='NONE')
            else:
              col.prop ( item, "rot_index", text="Ref:", icon='NONE' )

        elif data.geom_type == 'XYZA':

            # Arrange the components at the coordinates x, y, z with binding angle

            ps = context.scene.mcell.parameter_system

            col = layout.column()
            col.label(text='x,y,z,ang', icon='NONE')

            col = layout.column()
            item.loc_x.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_y.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_z.draw_prop_only ( col, ps )

            col = layout.column()
            item.rot_ang.draw_prop_only ( col, ps )

        elif data.geom_type == 'XYZVA':

            # Arrange the components at the coordinates x, y, z with binding angle about a vector

            ps = context.scene.mcell.parameter_system

            #col = layout.column()
            #col.label(text='loc [x,y,z]', icon='NONE')

            col = layout.column()
            item.loc_x.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_y.draw_prop_only ( col, ps )
            col = layout.column()
            item.loc_z.draw_prop_only ( col, ps )

            #col = layout.column()
            #col.label(text='rot [x,y,z,ang]', icon='NONE')

            col = layout.column()
            item.rot_x.draw_prop_only ( col, ps )
            col = layout.column()
            item.rot_y.draw_prop_only ( col, ps )
            col = layout.column()
            item.rot_z.draw_prop_only ( col, ps )
            col = layout.column()
            item.rot_ang.draw_prop_only ( col, ps )


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
    last_id = IntProperty(name="Counter for Unique Molecule IDs", default=0)  # Start ID's at 0 (will be incremented to 1)
    show_molmaker = bpy.props.BoolProperty(default=False)
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_components = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_preview = bpy.props.BoolProperty(default=False, name="Material Preview")
    show_extra_columns = bpy.props.BoolProperty(default=False, description="Show additional visibility control columns")
    dup_check = bpy.props.BoolProperty(default=False)

    next_color = IntProperty (default=0)  # Keeps track of the next molecule color to use


    def default_name ( self, item_id ):
        return "Molecule_"+str(item_id)


    def allocate_available_id ( self ):
        """ Return a unique molecule ID for a new molecule """
        if len(self.molecule_list) <= 0:
            # Reset the ID to 0 (will become 1) when there are no more molecules
            self.last_id = 0
        self.last_id += 1
        all_names = [ item.name for item in self.molecule_list ]
        while self.default_name(self.last_id) in all_names:
            self.last_id += 1
        return ( self.last_id )



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
        self.last_id = 0
        print ( "Done removing all Molecule List Properties." )
        
    
    def add_molecule ( self, context ):
        mcell = context.scene.mcell
        """ Add a new molecule to the list of molecules and set as the active molecule """
        if mcell.mol_viz.molecule_read_in == False:
            new_mol = self.molecule_list.add()
            new_mol.id = self.allocate_available_id()
            new_mol.init_properties(context.scene.mcell.parameter_system)
              # new_mol.initialize(context)
            self.active_mol_index = len(self.molecule_list)-1
        elif mcell.mol_viz.molecule_read_in == True:
            mcell.mol_viz.molecule_read_in = False
            for x in range(len(bpy.data.objects['molecules'].children)): 
                # new_mol.initialize(context)                
                for i in range(len(self.molecule_list)):
                        if self.molecule_list[i].name == bpy.data.objects['molecules'].children[x].name[4:]:
                            self.dup_check = True                                                         
                if self.dup_check == False:
                    new_mol = self.molecule_list.add()       
                    new_mol.init_properties(context.scene.mcell.parameter_system)
                    new_mol.remove_mol_data(context.scene.mcell)
                    self.active_mol_index = len(self.molecule_list)-1
                    self.molecule_list[self.active_mol_index].name = bpy.data.objects['molecules'].children[x].name[4:]
                elif self.dup_check == True:
                    self.dup_check = False
      

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
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
                self.last_id = 0
            if self.molecule_list:
                self.check(context)



    def add_component ( self, context ):
        """ Add a new component to the active molecule """
        if len(self.molecule_list) > 0:
            mol = self.molecule_list[self.active_mol_index]
            if mol:
                mol.add_component_vals ( context, "C" + str(self.allocate_available_id()) )

    def remove_active_component ( self, context ):
        """ Remove the active component from the active molecule """
        if len(self.molecule_list) > 0:
            mol = self.molecule_list[self.active_mol_index]
            if mol:
              mol.remove_active_component ( context )


    def build_data_model_from_properties ( self, context ):
        print ( "Molecule List building Data Model" )
        mol_dm = {}
        mol_dm['data_model_version'] = "DM_2014_10_24_1638"
        mol_list = []
        for m in self.molecule_list:
            mol_list.append ( m.build_data_model_from_properties() )
        mol_dm['molecule_list'] = mol_list

        molmaker = bpy.context.scene.mcell.molmaker
        mol_dm['molmaker'] = molmaker.build_data_model_from_properties()

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

        if "molmaker" in dm:
          molmaker = bpy.context.scene.mcell.molmaker
          molmaker.upgrade_data_model ( dm['molmaker'] )

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # print ( "Call to: \"MCellMoleculesListProperty.build_properties_from_data_model\" with %d molecules" % len(self.molecule_list) )
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
                # print ( "New length of molecule_list = " + str(len(bpy.data.objects['molecules'].children)) )

        # Add molecules from the data model
        if "molecule_list" in dm:
            for m in dm["molecule_list"]:
                self.add_molecule(context)
                self.molecule_list[self.active_mol_index].build_properties_from_data_model(context,m)

        if "molmaker" in dm:
          molmaker = bpy.context.scene.mcell.molmaker
          molmaker.build_properties_from_data_model ( context, dm['molmaker'] )


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


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

#
#if __name__ == "__main__":
#    register()

