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

import cellblender
# from . import cellblender_parameters
from . import parameter_system
from . import cellblender_mol_viz
from . import cellblender_utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Generic Geometry Helper Classes

class CellBlender_point:
  x=0
  y=0
  z=0

  def __init__ ( self, x, y, z ):
    self.x = x
    self.y = y
    self.z = z

  def toList ( self ):
    return ( [ self.x, self.y, self.z ] )

  def toString ( self ):
    return ( "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")" )


class CellBlender_face:
  verts = []

  def __init__ ( self, v1, v2, v3 ):
    self.verts = []
    self.verts.append ( v1 )
    self.verts.append ( v2 )
    self.verts.append ( v3 )

  def toString( self ):
    return ( "[" + str(verts[0]) + "," + str(verts[1]) + "," + str(verts[2]) + "]" )


class CellBlender_mesh:

  # An object that can hold points and faces

  points = []
  faces = []

  def __init__ ( self ):
    self.points = []
    self.faces = []


  def update_glyph_mesh ( scene, parent_name, obj_name, glyph="", force=False ):
    # Adapted from "update_obj_from_plf" in mol_sim.py

    # Updates or Creates a Blender object with an associated mesh from this object's points and faces

    vertices = []
    for point in self.points:
        vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
    faces = []
    for face_element in self.faces:
        faces.append ( face_element.verts )

    mesh_name = obj_name + "_mesh"
    if mesh_name in bpy.data.meshes:
        bpy.data.meshes[mesh_name].name = "old_" + mesh_name

    # Create and build the new mesh
    new_mesh = bpy.data.meshes.new ( mesh_name )
    new_mesh.from_pydata ( vertices, [], faces )
    new_mesh.update()

    # Assign the new mesh to the object (deleting any old mesh if the object already exists)
    obj = None
    old_mesh = None
    if obj_name in scene.objects:
        obj = scene.objects[obj_name]
        old_mesh = obj.data
        obj.data = new_mesh
        if old_mesh.users <= 0:
            bpy.data.meshes.remove ( old_mesh )
    else:
        print ( "Creating a new glyph object" )
        obj = bpy.data.objects.new ( obj_name, new_mesh )
        scene.objects.link ( obj )
        # Assign the parent if requested in the call with a non-none parent_name
        if parent_name:
            if parent_name in bpy.data.objects:
                obj.parent = bpy.data.objects[parent_name]

    if "old_"+mesh_name in bpy.data.meshes:
        if bpy.data.meshes["old_"+mesh_name].users <= 0:
            bpy.data.meshes.remove ( bpy.data.meshes["old_"+mesh_name] )

    # Could return the object here if needed



class CellBlender_Cube (CellBlender_mesh):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a box of the requested size

    self.points = []
    self.faces = []

    self.points = self.points + [ CellBlender_point (  size_x,  size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point (  size_x, -size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point ( -size_x, -size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point ( -size_x,  size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point (  size_x,  size_y,  size_z ) ]
    self.points = self.points + [ CellBlender_point (  size_x, -size_y,  size_z ) ]
    self.points = self.points + [ CellBlender_point ( -size_x, -size_y,  size_z ) ]
    self.points = self.points + [ CellBlender_point ( -size_x,  size_y,  size_z ) ]

    face_list = [ [ 1, 2, 3 ], [ 7, 6, 5 ], [ 4, 5, 1 ], [ 5, 6, 2 ],
                  [ 2, 6, 7 ], [ 0, 3, 7 ], [ 0, 1, 3 ], [ 4, 7, 5 ],
                  [ 0, 4, 1 ], [ 1, 5, 2 ], [ 3, 2, 7 ], [ 4, 0, 7 ] ]

    for f in face_list:
      self.faces.append ( CellBlender_face ( f[0], f[1], f[2] ) )


class CellBlender_Pyramid (CellBlender_mesh):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a pyramid of the requested size

    self.points = []
    self.faces = []

    self.points = self.points + [ CellBlender_point (  size_x,  size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point (  size_x, -size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point ( -size_x, -size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point ( -size_x,  size_y, -size_z ) ]
    self.points = self.points + [ CellBlender_point (     0.0,     0.0,  size_z ) ]

    face_list = [ [ 1, 2, 3 ], [ 0, 1, 3 ], [ 0, 4, 1 ],
                  [ 1, 4, 2 ], [ 2, 4, 3 ], [ 3, 4, 0 ] ]

    for f in face_list:
      self.faces.append ( CellBlender_face ( f[0], f[1], f[2] ) )



class CellBlender_IcoSphere (CellBlender_mesh):

  # Subclass of CellBlender_mesh that builds an icosphere with recursion

  def add_normalized_vertex ( self, p ):
    # Normalize the point
    # Add to the list of points if it's not already in the list
    # Return an index to the new or existing point in the list

    l = math.sqrt ( (p.x * p.x) + (p.y * p.y) + (p.z * p.z) )
    pnorm = CellBlender_point ( p.x/l, p.y/l, p.z/l )

    # Check if it's already there
    index = -1
    for pt in self.points:
      if (pt.x == pnorm.x) and (pt.y == pnorm.y) and (pt.z == pnorm.z):
        index = self.points.index(pt)
        break

    if (index < 0):
      self.points.append ( pnorm )
      index = self.points.index ( pnorm )
      #print ( "Added vertex at " + str(index) )
    #else:
    #  print ( "Found vertex at " + str(index) )
    return (index)


  def __init__ ( self, recursion_level=0, size_x=1.0, size_y=1.0, size_z=1.0 ):

    self.points = []

    t = (1.0 + math.sqrt(5.0)) / 2.0  # Approx 1.618033988749895

    # Create 12 verticies from the 3 perpendicular planes whose corners define an icosahedron

    self.add_normalized_vertex ( CellBlender_point (-1,  t,  0) )
    self.add_normalized_vertex ( CellBlender_point ( 1,  t,  0) )
    self.add_normalized_vertex ( CellBlender_point (-1, -t,  0) )
    self.add_normalized_vertex ( CellBlender_point ( 1, -t,  0) )

    self.add_normalized_vertex ( CellBlender_point ( 0, -1,  t) )
    self.add_normalized_vertex ( CellBlender_point ( 0,  1,  t) )
    self.add_normalized_vertex ( CellBlender_point ( 0, -1, -t) )
    self.add_normalized_vertex ( CellBlender_point ( 0,  1, -t) )

    self.add_normalized_vertex ( CellBlender_point ( t,  0, -1) )
    self.add_normalized_vertex ( CellBlender_point ( t,  0,  1) )
    self.add_normalized_vertex ( CellBlender_point (-t,  0, -1) )
    self.add_normalized_vertex ( CellBlender_point (-t,  0,  1) )


    # Rotate all points such that the resulting icosphere will be separable at the equator

    if (True):
      # A PI/6 rotation about z (transform x and y) gives an approximate equator in x-y plane
      angle = (math.pi / 2) - math.atan(1/t)
      # print ( "Rotating with angle = " + str(180 * angle / math.pi) )
      for p in self.points:
        newx = (math.cos(angle) * p.x) - (math.sin(angle) * p.z)
        newz = (math.sin(angle) * p.x) + (math.cos(angle) * p.z)
        p.x = newx
        p.z = newz

    # Build the original 20 faces for the Icosphere

    self.faces = []

    # Add 5 faces around point 0 (top)
    self.faces.append ( CellBlender_face (  0, 11,  5 ) )
    self.faces.append ( CellBlender_face (  0,  5,  1 ) )
    self.faces.append ( CellBlender_face (  0,  1,  7 ) )
    self.faces.append ( CellBlender_face (  0,  7, 10 ) )
    self.faces.append ( CellBlender_face (  0, 10, 11 ) )

    # Add 5 faces adjacent faces
    self.faces.append ( CellBlender_face (  1,  5,  9 ) )
    self.faces.append ( CellBlender_face (  5, 11,  4 ) )
    self.faces.append ( CellBlender_face ( 11, 10,  2 ) )
    self.faces.append ( CellBlender_face ( 10,  7,  6 ) )
    self.faces.append ( CellBlender_face (  7,  1,  8 ) )

    # Add 5 faces around point 3 (bottom)
    self.faces.append ( CellBlender_face (  3,  9,  4 ) )
    self.faces.append ( CellBlender_face (  3,  4,  2 ) )
    self.faces.append ( CellBlender_face (  3,  2,  6 ) )
    self.faces.append ( CellBlender_face (  3,  6,  8 ) )
    self.faces.append ( CellBlender_face (  3,  8,  9 ) )

    # Add 5 faces adjacent faces
    self.faces.append ( CellBlender_face (  4,  9,  5 ) )
    self.faces.append ( CellBlender_face (  2,  4, 11 ) )
    self.faces.append ( CellBlender_face (  6,  2, 10 ) )
    self.faces.append ( CellBlender_face (  8,  6,  7 ) )
    self.faces.append ( CellBlender_face (  9,  8,  1 ) )

    # Subdivide the faces as requested by the recursion_level argument
    old_points = None
    old_faces = None

    for rlevel in range(recursion_level):
      # System.out.println ( "\nRecursion Level = " + rlevel )
      # Save the old points and faces and build a new set for this recursion level
      old_points = self.points
      old_faces = self.faces
      self.points = []
      self.faces = []
      for f in old_faces:
        # Split this face into 4 more faces
        midpoint = CellBlender_point(0,0,0)
        potential_new_points = []
        for i in range(6):
          potential_new_points.append ( CellBlender_point(0,0,0) )
        for side in range(3):
          p1 = old_points[f.verts[side]]
          p2 = old_points[f.verts[(side+1)%3]]
          midpoint = CellBlender_point ( ((p1.x+p2.x)/2), ((p1.y+p2.y)/2), ((p1.z+p2.z)/2) )
          potential_new_points[2*side] = p1
          potential_new_points[(2*side)+1] = midpoint
        # Add the 4 new faces
        # Start with the verticies ... add them all since add_normalized_vertex() will remove duplicates
        vertex_indicies = []
        for i in range(6):
          vertex_indicies.append ( 0 )
        for i in range(6):
          vertex_indicies[i] = self.add_normalized_vertex ( potential_new_points[i] )
        # Now add the 4 new faces
        self.faces.append ( CellBlender_face ( vertex_indicies[0], vertex_indicies[1], vertex_indicies[5] ) )
        self.faces.append ( CellBlender_face ( vertex_indicies[1], vertex_indicies[2], vertex_indicies[3] ) )
        self.faces.append ( CellBlender_face ( vertex_indicies[3], vertex_indicies[4], vertex_indicies[5] ) )
        self.faces.append ( CellBlender_face ( vertex_indicies[1], vertex_indicies[3], vertex_indicies[5] ) )

    for pt in self.points:
      pt.x *= size_x
      pt.y *= size_y
      pt.z *= size_z





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
        meshes = bpy.data.meshes
        mcell.molecule_glyphs.status = ""
        select_objs = context.selected_objects
        if (len(select_objs) != 1):
            mcell.molecule_glyphs.status = "Select One Molecule"
            return {'FINISHED'}
        if (select_objs[0].type != 'MESH'):
            mcell.molecule_glyphs.status = "Selected Object Not a Molecule"
            return {'FINISHED'}

        mol_obj = select_objs[0]
        mol_shape_name = mol_obj.name

        glyph_name = mcell.molecule_glyphs.glyph

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
        meshes.remove(meshes[mol_shape_name])

        new_mol_mesh.name = mol_shape_name
        new_mol_mesh.materials.append(mol_mat)

        return {'FINISHED'}



# Callbacks for all Property updates appear to require global (non-member) functions.
# This is circumvented by simply calling the associated member function passed as self:

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

    self.check_callback(context)
    return

def check_callback(self, context):
    self.check_callback(context)
    return


def display_callback(self, context):
    self.display_callback(context)
    return

def change_glyph_callback(self, context):
    self.change_glyph_callback(context)
    return

def mol_scale_callback(self, context):
    self.mol_scale_callback(context)
    return


import os

class MCellMoleculeProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    # name = StringProperty(name="Molecule Name", default="Molecule",description="The molecule species name",update=check_callback)
    name = StringProperty(name="Molecule Name", default="Molecule", description="The molecule species name", update=name_change_callback)
    old_name = StringProperty(name="Old Mol Name", default="Molecule")


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
    scale = FloatProperty ( name="Scale", min=0.0001, default=1.0, description="Relative size (scale) for this molecule", update=mol_scale_callback )
    previous_scale = FloatProperty ( name="Previous_Scale", min=0.0, default=1.0, description="Previous Scale" )
    #cumulative_scale = FloatProperty ( name="Cumulative_Scale", min=0.0, default=1.0, description="Cumulative Scale" )

    glyph_lib = os.path.join(os.path.dirname(__file__), "glyph_library.blend", "Mesh", "")
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
    glyph = EnumProperty ( items=glyph_enum, name="", update=display_callback )

    internal_glyph_enum = [
        ('cellblender.cellblender_molecules.CellBlender_Pyramid()', "Pyramid", ""),
        ('cellblender.cellblender_molecules.CellBlender_IcoSphere ( recursion_level = 3 )', "Icosahedron", ""),
        ('Sphere_1', "Sphere_1", ""),
        ('Sphere_2', "Sphere_2", "")]
    internal_glyph = EnumProperty ( items=internal_glyph_enum, name="", update=change_glyph_callback )


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
        # TODO: Add after data model release:  self.maximum_step_length.init_ref  ( parameter_system, "Max_Step_Len_Type",   user_name="Maximum Step Length",  user_expr="",  user_units="microns",  user_descr="Molecule should never step farther than this length during a single timestep. Use with caution (see documentation)." )

    def remove_properties ( self, context ):
        print ( "Removing all Molecule Properties ... not implemented yet!" )


    def build_data_model_from_properties ( self ):
        m = self

        m_dict = {}
        m_dict['data_model_version'] = "DM_2015_07_24_1330"
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

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_07_24_1330":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm_dict ):
        # Check that the data model version matches the version for this property group
        if dm_dict['data_model_version'] != "DM_2015_07_24_1330":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeProperty data model to current version." )
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

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )




    def initialize_mol_data ( self, context ):
        # This assumes that the ID has already been assigned!!!
        self.name = "Molecule_"+str(self.id)
        self.old_name = self.name
        self.create_mol_data(context)


    def create_mol_data ( self, context ):

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
            mols_obj.hide = True

        # Build the new shape vertices and faces
        size = 0.1 / 20.0  # This number was chosen to be consistent with molecules already created by CellBlender
        print ( "Creating a new glyph for " + self.name )
        shape_mesh_data = None
        if   "Cube" == self.glyph:
            shape_mesh_data = CellBlender_Cube  ( size, size, size )
        elif "Pyramid" == self.glyph:
            shape_mesh_data = CellBlender_Pyramid  ( size, size, size )
        elif "Icosahedron" == self.glyph:
            shape_mesh_data = CellBlender_IcoSphere  ( 0, size, size, size )
        elif "Sphere_1" == self.glyph:
            shape_mesh_data = CellBlender_IcoSphere  ( 1, size, size, size )
        elif "Sphere_2" == self.glyph:
            shape_mesh_data = CellBlender_IcoSphere  ( 2, size, size, size )
        else:
            #shape_mesh_data = CellBlender_Cube ( size, size, size )
            shape_mesh_data = CellBlender_IcoSphere  ( 1, size, size, size )
        shape_vertices = []
        for point in shape_mesh_data.points:
            shape_vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
        shape_faces = []
        for face_element in shape_mesh_data.faces:
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

        # Add the shape to the scene as a glyph for the object
        scn.objects.link ( mol_shape_obj )

        # Look-up material, create if needed.
        # Associate material with mesh shape.
        # Bob: Maybe we need to associate it with the OBJECT with: shape_object.material_slots[0].link = 'OBJECT'
        mol_mat = mats.get(material_name)
        if not mol_mat:
            mol_mat = mats.new(material_name)
            # Need to pick a color here ?
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

        # Add the shape to the scene as a glyph for the object
        mol_obj.dupli_type = 'VERTS'
        mol_shape_obj.parent = mol_obj

        # Could return the object here if needed


    def remove_mol_data ( self, context ):

        meshes = bpy.data.meshes
        mats = bpy.data.materials
        objs = bpy.data.objects
        scn = bpy.context.scene
        scn_objs = scn.objects

        mol_obj_name        = "mol_" + self.name
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

        if mol_obj.users <= 0:
            objs.remove ( mol_obj )
            meshes.remove ( mol_pos_mesh )

        if mol_shape_obj.users <= 0:
            objs.remove ( mol_shape_obj )
            meshes.remove ( mol_shape_mesh )

        if mol_material.users <= 0:
            mats.remove ( mol_material )


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
            row.prop(molecules, "show_display", icon='TRIA_RIGHT',
                     text="Display Options", emboss=False)
        else:
            row.prop(molecules, "show_display", icon='TRIA_DOWN', text="Display Options", emboss=False)
            row = box.row()
            row.label ( "Molecule Display Settings" )
            row = box.row()
            col = row.column()
            col.prop ( self, "glyph" )
            col = row.column()
            col.prop ( self, "internal_glyph" )
            col = row.column()
            col.prop ( self, "scale" )
            row = box.row()
            col = row.column()
            mol_mat_name = 'mol_' + self.name + '_mat'
            if mol_mat_name in bpy.data.materials:
                # This would control the actual Blender material property directly
                col.prop ( bpy.data.materials[mol_mat_name], "diffuse_color", text="" )
                col = row.column()
                col.prop ( bpy.data.materials[mol_mat_name], "emit" )
            #else:
            #    # This controls the molecule property which changes the Blender property via callback
            #    # But changing the color via the Materials interface doesn't change these values
            #    col.prop ( self, "color" )
            #    col = row.column()
            #    col.prop ( self, "emit" )
            #col = row.column()
            #col.prop ( self, "usecolor" )
        
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


    def mol_scale_callback(self, context):
        """Scale has changed for this molecule"""
        print ( "Scale for molecule \"" + self.name + "\" changed to: " + str(self.scale) )
        mol_name = 'mol_' + self.name
        mol_shape_name = mol_name + '_shape'
        if mol_shape_name in bpy.data.objects:
            # Scale by the ratio of current scale to previous scale
            # bpy.data.objects[mol_shape_name].scale *= (self.scale / self.previous_scale)
            bpy.data.objects[mol_shape_name].scale = mathutils.Vector ( ( self.scale, self.scale, self.scale ) )
            self.previous_scale = self.scale

        # May not need to do the following any more:

        #mol_mat_name = 'mol_' + self.name + '_mat'
        #if mol_mat_name in bpy.data.materials.keys():
        #    if bpy.data.materials[mol_mat_name].diffuse_color != self.color:
        #        bpy.data.materials[mol_mat_name].diffuse_color = self.color
        #    if bpy.data.materials[mol_mat_name].emit != self.emit:
        #        bpy.data.materials[mol_mat_name].emit = self.emit


        # Refresh the scene
        # TODO The following may be needed, but were temporarily commented out:
        #self.set_mol_glyph ( context )
        #cellblender_mol_viz.mol_viz_update(self,context)  # It's not clear why mol_viz_update needs a self. It's not in a class.
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return


    def change_glyph_callback(self, context):
        """Glyph has changed for this molecule"""
        print ( "Internal Glyph for molecule \"" + self.name + "\" changed to: " + str(self.internal_glyph) )
        mol_name = 'mol_' + self.name
        mol_shape_name = mol_name + '_shape'
        #if mol_shape_name in bpy.data.objects:
        #    if self.scale != self.previous_scale:
        #        # Scale by the ratio of current scale to previous scale
        #        # bpy.data.objects[mol_shape_name].scale *= (self.scale / self.previous_scale)
        #        bpy.data.objects[mol_shape_name].scale = mathutils.Vector ( ( self.scale, self.scale, self.scale ) )
        #        self.previous_scale = self.scale

        # May not need to do the following any more:

        #mol_mat_name = 'mol_' + self.name + '_mat'
        #if mol_mat_name in bpy.data.materials.keys():
        #    if bpy.data.materials[mol_mat_name].diffuse_color != self.color:
        #        bpy.data.materials[mol_mat_name].diffuse_color = self.color
        #    if bpy.data.materials[mol_mat_name].emit != self.emit:
        #        bpy.data.materials[mol_mat_name].emit = self.emit


        # Refresh the scene
        # TODO The following may be needed, but were temporarily commented out:
        #self.set_mol_glyph ( context )
        #cellblender_mol_viz.mol_viz_update(self,context)  # It's not clear why mol_viz_update needs a self. It's not in a class.
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return


    def display_callback(self, context):
        """One of the display items has changed for this molecule"""
        print ( "Display for molecule \"" + self.name + "\" changed to: " + str(self.glyph) + ", color=" + str(self.color) + ", emit=" + str(self.emit) + ", scale=" + str(self.scale) )
        mol_name = 'mol_' + self.name
        mol_shape_name = mol_name + '_shape'
        #if mol_shape_name in bpy.data.objects:
        #    if self.scale != self.previous_scale:
        #        # Scale by the ratio of current scale to previous scale
        #        # bpy.data.objects[mol_shape_name].scale *= (self.scale / self.previous_scale)
        #        bpy.data.objects[mol_shape_name].scale = mathutils.Vector ( ( self.scale, self.scale, self.scale ) )
        #        self.previous_scale = self.scale

        # May not need to do the following any more:

        #mol_mat_name = 'mol_' + self.name + '_mat'
        #if mol_mat_name in bpy.data.materials.keys():
        #    if bpy.data.materials[mol_mat_name].diffuse_color != self.color:
        #        bpy.data.materials[mol_mat_name].diffuse_color = self.color
        #    if bpy.data.materials[mol_mat_name].emit != self.emit:
        #        bpy.data.materials[mol_mat_name].emit = self.emit


        # Refresh the scene
        # TODO The following may be needed, but were temporarily commented out:
        #self.set_mol_glyph ( context )
        #cellblender_mol_viz.mol_viz_update(self,context)  # It's not clear why mol_viz_update needs a self. It's not in a class.
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

            # glyph_name = mcell.molecule_glyphs.glyph
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






class MCell_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
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

    def draw ( self, context ):
        # Call the draw function for the instance being drawn in this panel
        context.scene.mcell.molecules.draw_panel ( context, self )


class MCellMoleculesListProperty(bpy.types.PropertyGroup):
    contains_cellblender_parameters = BoolProperty(name="Contains CellBlender Parameters", default=True)
    molecule_list = CollectionProperty(type=MCellMoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    def init_properties ( self, parameter_system ):
        if self.molecule_list:
            for mol in self.molecule_list:
                mol.init_properties(parameter_system)

    def remove_properties ( self, context ):
        print ( "Removing all Molecule List Properties..." )
        for item in self.molecule_list:
            item.remove_properties(context)
        self.molecule_list.clear()
        self.active_mol_index = 0
        self.next_id = 1
        print ( "Done removing all Molecule List Properties." )
        
    
    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_id = self.allocate_available_id()  # Do this before adding so it can be reset when empty
        new_mol = self.molecule_list.add()
        new_mol.id = new_id
        new_mol.init_properties(context.scene.mcell.parameter_system)
        new_mol.initialize_mol_data(context)
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        self.molecule_list[self.active_mol_index].remove_mol_data ( context )
        self.molecule_list.remove ( self.active_mol_index )
        self.active_mol_index -= 1
        if self.active_mol_index < 0:
            self.active_mol_index = 0
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
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculesListProperty data model to current version." )

        # Now convert the Data Model into CellBlender Properties

        # Start by removing all molecules from the list
        while len(self.molecule_list) > 0:
            self.remove_active_molecule ( context )

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
        #if len(self.molecule_list) <= 0:
        #    # Reset the ID to 1 when there are no more molecules
        #    self.next_id = 1
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
                              rows=2)
            col = row.column(align=True)
            col.operator("mcell.molecule_add", icon='ZOOMIN', text="")
            col.operator("mcell.molecule_remove", icon='ZOOMOUT', text="")
            if self.molecule_list:
                mol = self.molecule_list[self.active_mol_index]
                # The self is needed to pass the "advanced" flag to the molecule
                mol.draw_props ( layout, self, mcell.parameter_system )


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

