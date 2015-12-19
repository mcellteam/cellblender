bl_info = {
  "version": "0.1",
  "name": "Molecule Simulator",
  'author': 'Bob',
  "location": "View3D -> ToolShelf -> MolSim",
  "category": "Cell Modeling"
  }


##################
#  Support Code  #
##################

import sys
import os
import os.path
import hashlib
import bpy
import math
import random
import mathutils
from bpy.props import *


from bpy.app.handlers import persistent




################################################################
#########  Start of Code from test_material_props.py  ##########
################################################################



import bpy
from bpy.types import Menu, Panel, UIList
from rna_prop_ui import PropertyPanel
from bpy.app.translations import pgettext_iface as iface_


def active_node_mat(mat):
    # TODO, 2.4x has a pipeline section, for 2.5 we need to communicate
    # which settings from node-materials are used
    if mat is not None:
        mat_node = mat.active_node_material
        if mat_node:
            return mat_node
        else:
            return mat

    return None


def check_material(mat):
    if mat is not None:
        if mat.use_nodes:
            if mat.active_node_material is not None:
                return True
            return False
        return True
    return False


def simple_material(mat):
    if (mat is not None) and (not mat.use_nodes):
        return True
    return False


class MATERIAL_MT_mol_sss_presets(Menu):
    bl_label = "SSS Presets"
    preset_subdir = "sss"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class MATERIAL_MT_mol_specials(Menu):
    bl_label = "MolMaterial Specials"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.material_slot_copy", icon='COPY_ID')
        layout.operator("material.copy", icon='COPYDOWN')
        layout.operator("material.paste", icon='PASTEDOWN')


class MATERIAL_UL_mol_matslots(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # assert(isinstance(item, bpy.types.MaterialSlot)
        # ob = data
        slot = item
        ma = slot.material
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", icon_value=icon)
            if ma and not context.scene.render.use_shading_nodes:
                manode = ma.active_node_material
                if manode:
                    layout.label(text=iface_("Node %s") % manode.name, translate=False, icon_value=layout.icon(manode))
                elif ma.use_nodes:
                    layout.label(text="Node <none>")
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class MolMaterialButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here
    """
    @classmethod
    def poll(cls, context):
        return context.material and (context.scene.render.engine in cls.COMPAT_ENGINES)
    """

    @classmethod
    def poll(cls, context):
        print ( "Inside MolMatButton_poll " + str(context.material) )
        return context.material and (context.scene.render.engine in cls.COMPAT_ENGINES)





##############################################################
#########  End of Code from test_material_props.py  ##########
##############################################################



active_frame_change_handler = None


def value_changed (self, context):
    app = context.scene.molecule_simulation


def check_callback(self, context):
    print ( "check_callback called with self = " + str(self) )
    #self.check_callback(context)
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


def display_callback(self, context):
    #self.display_callback(context)
    return

def glyph_visibility_callback(self, context):
    # print ( "Glyph vis change callback for molecule " + self.name )
    ms = context.scene.molecule_simulation
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
    ms = context.scene.molecule_simulation
    ml = ms.molecule_list
    show_only_name = "mol_" + self.name
    show_only_shape_name = show_only_name + "_shape"
    show_only_items = [show_only_name, show_only_shape_name]
    # print ( "Only showing " + str(show_only_items) )
    
    # Note the check before set to keep from infinite recursion in properties!!
    for o in context.scene.objects:
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
    self.create_mol_data ( context )
    return

import os


class MoleculeProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Molecule Name", default="Molecule",description="The molecule species name",update=name_change_callback)
    old_name = StringProperty(name="Old Mol Name", default="Molecule")

    shape_name = StringProperty(name="ShapeName", default="")
    material_name = StringProperty(name="MatName", default="")

    mol_id = IntProperty(name="Molecule ID", default=0)
    
    glyph_visibility = BoolProperty ( default=True, description='Show this molecule glyph', update=glyph_visibility_callback )
    glyph_show_only = BoolProperty ( default=False, description='Show only this molecule glyph', update=glyph_show_only_callback )


    diffusion_constant = FloatProperty ( name="Molecule Diffusion Constant" )

    usecolor = BoolProperty ( name="Use this Color", default=True, description='Use Molecule Color instead of Material Color', update=display_callback )
    color = FloatVectorProperty ( name="", min=0.0, max=1.0, default=(0.5,0.5,0.5), subtype='COLOR', description='Molecule Color', update=display_callback )
    alpha = FloatProperty ( name="Alpha", min=0.0, max=1.0, default=1.0, description="Alpha (inverse of transparency)", update=display_callback )
    emit = FloatProperty ( name="Emit", min=0.0, default=1.0, description="Emits Light (brightness)", update=display_callback )
    scale = FloatProperty ( name="Scale", min=0.0001, default=1.0, description="Relative size (scale) for this molecule", update=display_callback )
    previous_scale = FloatProperty ( name="Previous_Scale", min=0.0, default=1.0, description="Previous Scale" )
    #cumulative_scale = FloatProperty ( name="Cumulative_Scale", min=0.0, default=1.0, description="Cumulative Scale" )

    method_enum = [
        ('slow', "slow", ""),
        ('med', "med", ""),
        ('fast', "fast", "")]
    method = EnumProperty ( items=method_enum, name="", update=value_changed )
    num      = bpy.props.IntProperty   ( name="num",  default=100,              description="Number of A Molecules",     update=value_changed )
    dist     = bpy.props.FloatProperty ( name="dist", default=0.2, precision=3, description="Distribution",              update=value_changed )
    center_x = bpy.props.FloatProperty ( name="x",    default=-1,  precision=3, description="Location along the x-axis", update=value_changed )
    center_y = bpy.props.FloatProperty ( name="y",    default=-1,  precision=3, description="Location along the y-axis", update=value_changed )
    center_z = bpy.props.FloatProperty ( name="z",    default=-1,  precision=3, description="Location along the z-axis", update=value_changed )

    glyph_lib = os.path.join(os.path.dirname(__file__), "glyph_library.blend", "Mesh", "")
    glyph_enum = [
        ('Cone', "Cone", ""),
        ('Cube', "Cube", ""),
        ('Cylinder', "Cylinder", ""),
        ('Icosahedron', "Icosahedron", ""),
        ('Octahedron', "Octahedron", ""),
        ('Receptor', "Receptor", ""),
        ('Sphere1', "Sphere1", ""),
        ('Sphere2', "Sphere2", ""),
        ('Torus', "Torus", ""),
        ('Tetrahedron', "Tetrahedron", ""),
        ('Pyramid', "Pyramid", ""),
        ('A', "A", ""),
        ('B', "B", ""),
        ('C', "C", "")]
    glyph = EnumProperty ( items=glyph_enum, name="", update=shape_change_callback )


    export_viz = bpy.props.BoolProperty(
        default=False, description="If selected, the molecule will be "
                                   "included in the visualization data.")
    status = StringProperty(name="Status")


    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    bngl_label_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    target_only_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def initialize ( self, context ):
        # This assumes that the ID has already been assigned!!!
        self.name = "Molecule_"+str(self.mol_id)
        self.old_name = self.name

        self.method = self.method_enum[0][0]
        self.num = 0 ### random.randint(10,50)
        self.dist = random.uniform(0.01,0.05)
        loc_range = 0.1
        self.center_x = random.uniform(-loc_range,loc_range)
        self.center_y = random.uniform(-loc_range,loc_range)
        self.center_z = random.uniform(-loc_range,loc_range)
        self.glyph = self.glyph_enum[random.randint(0,len(self.glyph_enum)-1)][0]
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

        # Build the new shape vertices and faces
        size = 0.1
        print ( "Creating a new glyph for " + self.name )

        shape_plf = get_named_shape ( self.glyph, size_x=size, size_y=size, size_z=size )

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

        # Add the shape to the scene as a glyph for the object
        scn.objects.link ( mol_shape_obj )

        """
                    mol_shape_obj.data.materials.clear()  # New
                    mol_shape_obj.data.materials.append ( bpy.data.materials[obj_name + "_mat"] ) # New

                    # This didn't work very well

                    #if not (shape_name in scene.objects):
                    #    shape = bpy.data.objects.new ( shape_name, mol_shape_mesh )
                    ## Create a material specifically for this object
                    #if obj_name+"_mat" in bpy.data.materials:
                    #    shape.data.materials.clear()  # New
                    #    shape.data.materials.append ( bpy.data.materials[obj_name + "_mat"] ) # New
                    ## Remove current children from the target object (otherwise glyphs will be merged ... useful in the future)
                    #while len(obj.children) > 0:
                    #    obj.children[0].parent = None


                    # Add the shape to the scene as a glyph for the object
                    scene.objects.link ( shape )
                    obj.dupli_type = 'VERTS'
                    shape.parent = obj
                    
                    if old_shape_name in bpy.data.meshes:
                        if bpy.data.meshes[old_shape_name].users <= 0:
                            bpy.data.meshes.remove ( bpy.data.meshes[old_shape_name] )



        mol_shape_mesh = meshes.get(shape_name)
        if not mol_shape_mesh:
            # bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=0, size=0.005, location=[0, 0, 0])
            bpy.ops.mesh.primitive_cube_add(radius=0.1, location=[0, 0, 0])
            mol_shape_obj = bpy.context.active_object
            mol_shape_obj.name = shape_name
            mol_shape_obj.track_axis = "POS_Z"
            mol_shape_mesh = mol_shape_obj.data
            mol_shape_mesh.name = shape_name
        else:
            mol_shape_obj = objs.get(shape_name)
        """

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



        """

        # These are points only, so create a shape glyph as needed to show the points
        shape_name = obj_name + "_shape"
        #if force or not (shape_name in scene.objects):
        if not (shape_name in scene.objects):
            old_shape_name = "old_" + shape_name
            size = 0.1
            print ( "Creating a new glyph for " + obj_name )
            shape_plf = None
            if "Cube" == glyph:
                shape_plf = BasicBox  ( size, size, size )
            elif "Pyramid" == glyph:
                shape_plf = Pyramid  ( size, size, size )
            elif "Tetrahedron" == glyph:
                shape_plf = Tetrahedron  ( size, size, size )
            elif "A" in glyph:
                shape_plf = Letter_A  ( size, size, size )
            elif "B" in glyph:
                shape_plf = Letter_B  ( size, size, size )
            elif "C" in glyph:
                shape_plf = Letter_C  ( size, size, size )
            else:
                shape_plf = BasicBox ( size, size, size )
            shape_vertices = []
            for point in shape_plf.points:
                shape_vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
            shape_faces = []
            for face_element in shape_plf.faces:
                shape_faces.append ( face_element.verts )


            # Rename the old mesh shape if it exists
            if shape_name in bpy.data.meshes:
                bpy.data.meshes[shape_name].name = old_shape_name
            # Create and build the new mesh
            new_mesh = bpy.data.meshes.new ( shape_name )
            new_mesh.from_pydata ( shape_vertices, [], shape_faces )
            new_mesh.update()

            shape = bpy.data.objects.new ( shape_name, new_mesh )
            shape.data.materials.clear()  # New
            shape.data.materials.append ( bpy.data.materials[obj_name + "_mat"] ) # New

            # This didn't work very well

            #if not (shape_name in scene.objects):
            #    shape = bpy.data.objects.new ( shape_name, new_mesh )
            ## Create a material specifically for this object
            #if obj_name+"_mat" in bpy.data.materials:
            #    shape.data.materials.clear()  # New
            #    shape.data.materials.append ( bpy.data.materials[obj_name + "_mat"] ) # New
            ## Remove current children from the target object (otherwise glyphs will be merged ... useful in the future)
            #while len(obj.children) > 0:
            #    obj.children[0].parent = None


            # Add the shape to the scene as a glyph for the object
            scene.objects.link ( shape )
            obj.dupli_type = 'VERTS'
            shape.parent = obj
            
            if old_shape_name in bpy.data.meshes:
                if bpy.data.meshes[old_shape_name].users <= 0:
                    bpy.data.meshes.remove ( bpy.data.meshes[old_shape_name] )

        # Could return the object here if needed

        """


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
        

    def draw_layout ( self, context, layout, mol_list_group ):
        """ Draw the molecule "panel" within the layout """
        row = layout.row()
        row.prop(self, "name")
        row = layout.row()
        row.prop(self, "diffusion_constant")


    def draw_display_layout ( self, context, layout, mol_list_group ):
        """ Draw the molecule display "panel" within the layout """
        row = layout.row()
        row.prop(self, "glyph", text="Shape")
        mat_name = "mol_" + self.name+"_mat"
        if mat_name in bpy.data.materials:
            row = layout.row()
            row.prop ( bpy.data.materials[mat_name], "diffuse_color", text="Color" )
            row = layout.row()
            col = row.column()
            col.label ( "Brightness" )
            col = row.column()
            col.prop ( bpy.data.materials[mat_name], "emit", text="Emit" )
            if len(bpy.data.materials) and (context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}):
              if 'molecule_simulation' in context.scene.keys():
                #print ( "Context OK, showing materials" )
                app = context.scene.molecule_simulation
                m = app.molecule_list[app.active_mol_index]
                mat_name = "mol_" + m.name + "_mat"
                #print ( "" + mat_name + " in bpy.data.materials = " + str(mat_name in bpy.data.materials) )
                if mat_name in bpy.data.materials:
                  row = layout.row()
                  row.alignment = 'LEFT'
                  if mol_list_group.show_preview:
                    row.prop(mol_list_group, "show_preview", icon='TRIA_DOWN', emboss=False, text="Material Preview (resize to refresh)")
                    layout.template_preview(bpy.data.materials[mat_name])
                  else:
                    row.prop(mol_list_group, "show_preview", icon='TRIA_RIGHT', emboss=False)
              else:
                print ( "molecule_simulation not found, not showing color preview" )
                pass
        else:
            print ( "Material " + mat_name + " not found, not showing materials" )
        """
        row = layout.row()
        row.operator("molecule_simulation.molecule_show_only", icon='RESTRICT_VIEW_OFF', text="Show Only "+self.name)
        row.operator("molecule_simulation.molecule_hide", icon='RESTRICT_VIEW_OFF', text="Hide "+self.name)
        row = layout.row()
        row.operator("molecule_simulation.molecule_show_all", icon='RESTRICT_VIEW_OFF')
        row.operator("molecule_simulation.molecule_show", icon='RESTRICT_VIEW_OFF', text="Show "+self.name)
        """




    def draw(self, context):
        print ( "Inside MolMATERIAL_PT_preview draw method " + str(context) )
        if len(bpy.data.materials) and (context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}):
          #self.layout.template_preview(context.material)
          if 'molecule_simulation' in context.scene.keys():
            print ( "Context OK, showing materials" )
            app = context.scene.molecule_simulation
            m = app.molecule_list[app.active_mol_index]
            mat_name = "mol_" + m.name + "_mat"
            print ( "" + mat_name + " in bpy.data.materials = " + str(mat_name in bpy.data.materials) )
            if mat_name in bpy.data.materials:
              self.layout.template_preview(bpy.data.materials[mat_name])
              #mat = active_node_mat(context.material)
              mat = active_node_mat(bpy.data.materials[mat_name])
              row = self.layout.row()
              col = row.column()
              col.prop(mat, "diffuse_color", text="")
              col = row.column()
              col.prop(mat, "emit", text="Mol Emit")
          else:
            print ( "molecule_simulation not found, not showing materials" )
        else:
          print ( "Context NOT OK, not showing materials" )



    def draw_release_layout ( self, context, layout, mol_list_group ):
        """ Draw the molecule release "panel" within the layout """
        row = layout.row()
        row.prop(self, "method")
        row.prop(self, "num")
        row.prop(self, "dist")
        row = layout.row()
        row.prop(self, "center_x")
        row.prop(self, "center_y")
        row.prop(self, "center_z")


    def update_molecule_positions ( self, scene ):
        plf = MolCluster ( self.num, self.dist, self.center_x, self.center_y, self.center_z, scene.frame_current, method=self.method )
        update_obj_from_plf ( scene, "molecules", "mol_" + self.name, plf, glyph=self.glyph )


# Molecule Operators:

class APP_OT_molecule_add(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_add"
    bl_label = "Add Molecule"
    bl_description = "Add a new molecule type to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.molecule_simulation.add_molecule(context)
        return {'FINISHED'}

class APP_OT_molecule_remove(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_remove"
    bl_label = "Remove Molecule"
    bl_description = "Remove selected molecule type from an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.molecule_simulation.remove_active_molecule(context)
        self.report({'INFO'}, "Deleted Molecule")
        return {'FINISHED'}

class MolSim_UL_check_molecule(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # print ("Draw with " + str(data) + " " + str(item) + " " + str(active_data) + " " + str(active_propname) + " " + str(index) )
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            col = layout.column()
            col.label(item.name, icon='FILE_TICK')

            ms = context.scene.molecule_simulation
            show_name = "mol_" + item.name
            show_shape_name = show_name + "_shape"
            objs = context.scene.objects
            #col = layout.column()
            #col.operator("molecule_simulation.molecule_show_only", icon='VIEWZOOM', text="")
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


"""
These functions are now implemented in the molecule list

class APP_OT_molecule_show(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_show"
    bl_label = "Show"
    bl_description = "Show the current molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.molecule_simulation
        show_name = "mol_" + ms.molecule_list[ms.active_mol_index].name
        show_shape_name = show_name + "_shape"
        show_items = [show_name, show_shape_name]
        print ( "Showing " + str(show_items) )
        for o in context.scene.objects:
            if o.name in show_items:
                o.hide = False
        return {'FINISHED'}

class APP_OT_molecule_hide(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_hide"
    bl_label = "Hide"
    bl_description = "Hide the current molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.molecule_simulation
        hide_name = "mol_" + ms.molecule_list[ms.active_mol_index].name
        hide_shape_name = hide_name + "_shape"
        hide_items = [hide_name, hide_shape_name]
        print ( "Hiding " + str(hide_items) )
        for o in context.scene.objects:
            if o.name in hide_items:
                o.hide = True
        return {'FINISHED'}

class APP_OT_molecule_show_only(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_show_only"
    bl_label = "Show Only"
    bl_description = "Only show the current molecule"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.molecule_simulation
        show_only_name = "mol_" + ms.molecule_list[ms.active_mol_index].name
        show_only_shape_name = show_only_name + "_shape"
        show_only_items = [show_only_name, show_only_shape_name]
        print ( "Only showing " + str(show_only_items) )
        for o in context.scene.objects:
            if o.name in show_only_items:
                o.hide = False
            else:
                o.hide = True
        return {'FINISHED'}
"""

class APP_OT_molecule_show_all(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_show_all"
    bl_label = "Show All"
    bl_description = "Show all of the molecules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.molecule_simulation
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


class APP_OT_molecule_hide_all(bpy.types.Operator):
    bl_idname = "molecule_simulation.molecule_hide_all"
    bl_label = "Hide All"
    bl_description = "Hide all of the molecules"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ms = context.scene.molecule_simulation
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




class MoleculeSimPropertyGroup(bpy.types.PropertyGroup):
    run_mcell = bpy.props.BoolProperty(name="Run MCell", default=True)

    molecule_list = CollectionProperty(type=MoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    show_extra_columns = bpy.props.BoolProperty(default=True, description="Show additional visibility control columns")
    show_molecules = bpy.props.BoolProperty(default=True, name="Define Molecules")
    show_display = bpy.props.BoolProperty(default=False, name="Molecule Display Options")
    show_preview = bpy.props.BoolProperty(default=False, name="Material Preview")
    show_release = bpy.props.BoolProperty(default=False, name="Define a Release Site")
    show_run = bpy.props.BoolProperty(default=True, name="Run Simulation")



    def allocate_available_id ( self ):
        """ Return a unique molecule ID for a new molecule """
        if len(self.molecule_list) <= 0:
            # Reset the ID to 1 when there are no more molecules
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def add_molecule ( self, context ):
        """ Add a new molecule to the list of molecules and set as the active molecule """
        new_mol = self.molecule_list.add()
        new_mol.mol_id = self.allocate_available_id()
        new_mol.initialize(context)
        self.active_mol_index = len(self.molecule_list)-1

    def remove_active_molecule ( self, context ):
        """ Remove the active molecule from the list of molecules """
        if len(self.molecule_list) > 0:
            mol = self.molecule_list[self.active_mol_index]
            if mol:
                mol.remove_mol_data(context)
            self.molecule_list.remove ( self.active_mol_index )
            self.active_mol_index -= 1
            if self.active_mol_index < 0:
                self.active_mol_index = 0
            if len(self.molecule_list) <= 0:
                self.next_id = 1

    def update_simulation ( self, scene ):
        for mol in self.molecule_list:
            # print ("Updating molecule " + mol.name)
            mol.update_molecule_positions ( scene )



    def draw_layout ( self, context, layout ):
        """ Draw the molecule "panel" within the layout """

        row = layout.row()
        row.operator ( "molecule_sim.load_home_file", icon='IMPORT' )
        row.operator ( "molecule_sim.save_home_file", icon='EXPORT' )

        box = layout.box() ### Used only as a separator

        row = layout.row()
        row.alignment = 'LEFT'
        if self.show_molecules:
            row.prop(self, "show_molecules", icon='TRIA_DOWN', emboss=False)



            ################################
            #row = layout.row()
            #row.label ( "Renaming Molecules Doesn't Work YET!!!", icon='ERROR' )
            ################################



            row = layout.row()
            col = row.column()
            col.template_list("MolSim_UL_check_molecule", "define_molecules",
                              self, "molecule_list",
                              self, "active_mol_index",
                              rows=2)
            col = row.column(align=False)
            # Use subcolumns to group logically related buttons together
            subcol = col.column(align=True)
            subcol.operator("molecule_simulation.molecule_add", icon='ZOOMIN', text="")
            subcol.operator("molecule_simulation.molecule_remove", icon='ZOOMOUT', text="")
            subcol = col.column(align=True)
            subcol.operator("molecule_simulation.molecule_show_all", icon='RESTRICT_VIEW_OFF', text="")
            subcol.operator("molecule_simulation.molecule_hide_all", icon='RESTRICT_VIEW_ON', text="")
            subcol = col.column(align=True)
            subcol.prop (self, "show_extra_columns", text="")

            if self.molecule_list:
                mol = self.molecule_list[self.active_mol_index]
                mol.draw_layout ( context, layout, self )
        else:
            row.prop(self, "show_molecules", icon='TRIA_RIGHT', emboss=False)


        if self.molecule_list:
            if len(self.molecule_list) > 0:
                box = layout.box() ### Used only as a separator

                row = layout.row()
                row.alignment = 'LEFT'
                if self.show_display:
                    row.prop(self, "show_display", icon='TRIA_DOWN', emboss=False)
                    row = layout.row()
                    if self.molecule_list:
                        mol = self.molecule_list[self.active_mol_index]
                        mol.draw_display_layout ( context, layout, self )
                else:
                    row.prop(self, "show_display", icon='TRIA_RIGHT', emboss=False)

                box = layout.box() ### Used only as a separator

                row = layout.row()
                row.alignment = 'LEFT'
                if self.show_release:
                    row.prop(self, "show_release", icon='TRIA_DOWN', emboss=False)
                    row = layout.row()
                    if self.molecule_list:
                        mol = self.molecule_list[self.active_mol_index]
                        mol.draw_release_layout ( context, layout, self )
                else:
                    row.prop(self, "show_release", icon='TRIA_RIGHT', emboss=False)

        box = layout.box() ### Used only as a separator

        row = layout.row()
        row.alignment = 'LEFT'
        if self.show_run:
            row.prop(self, "show_run", icon='TRIA_DOWN', emboss=False)
            row = layout.row()
            row.operator("mol_sim.run", icon='COLOR_RED')
            row.operator("mol_sim.activate", icon='FILE_REFRESH')
            row.operator("mol_sim.deactivate", icon='X')
        else:
            row.prop(self, "show_run", icon='TRIA_RIGHT', emboss=False)



class MoleculeSimToolPanel(bpy.types.Panel):
    bl_label = "Molecule Simulation"

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MolSim"
    # bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)

    def draw(self, context):
        row = self.layout.row()
        row.label ( "Tool Shelf Version", icon='COLOR_GREEN' )

        box = self.layout.box() ### Used only as a separator

        app = context.scene.molecule_simulation
        app.draw_layout ( context, self.layout )



class MoleculeSimScenePanel(bpy.types.Panel):
    bl_label = "Molecule Simulation Scene"

    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)

    def draw(self, context):

        row = self.layout.row()
        row.label ( "Scene Panel Version", icon='COLOR_BLUE' )

        box = self.layout.box() ### Used only as a separator

        app = context.scene.molecule_simulation
        app.draw_layout ( context, self.layout )




class LoadHomeOp(bpy.types.Operator):
    bl_idname = "molecule_sim.load_home_file"
    bl_label = "Load Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        bpy.ops.wm.read_homefile()
        return { 'FINISHED' }

class SaveHomeOp(bpy.types.Operator):
    bl_idname = "molecule_sim.save_home_file"
    bl_label = "Save Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        bpy.ops.wm.save_homefile()
        return { 'FINISHED' }



class Molecule_Model:

    old_type = None
    context = None
    scn = None
    mcell = None
    path_to_blend = None
    
    def __init__(self, cb_context):
        # bpy.ops.wm.read_homefile()
        self.old_type = None
        self.context = cb_context
        self.setup_cb_defaults ( self.context )
        
    def get_scene(self):
        return self.scn
        
    def get_mcell(self):
        return self.mcell


    def set_view_3d(self):
        area = bpy.context.area
        if area == None:
            self.old_type = 'VIEW_3D'
        else:
            self.old_type = area.type
        area.type = 'VIEW_3D'
      
    def set_view_back(self):
        area = bpy.context.area
        area.type = self.old_type


    def get_scene(self):
        return bpy.data.scenes['Scene']

    def delete_all_objects(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=True)


    def setup_cb_defaults ( self, context ):

        scn = self.get_scene()
        self.set_view_3d()
        self.delete_all_objects()
        mcell = None

        bpy.ops.view3d.snap_cursor_to_center()
        
        self.scn = scn
        self.mcell = mcell

    def set_draw_type_for_object ( self, name="", draw_type="WIRE" ):
        if name in bpy.data.objects:
            bpy.data.objects[name].draw_type = draw_type


    def add_active_object_to_model ( self, name="Cell", draw_type="WIRE" ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.data.objects[name].draw_type = draw_type
        bpy.data.objects[name].select = True

        # Make the object active and add it to the model objects list

        self.scn.objects.active = bpy.data.objects[name]

        #self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding " + name )



    def add_label_to_model ( self, name="Label", text="Text", x=0, y=0, z=0, size=1, rx=0, ry=0, rz=0 ):
        print ( "Adding " + text )

        bpy.ops.object.text_add ( location=(x,y,z), rotation=(rx,ry,rz), radius=size )
        tobj = bpy.context.active_object
        tobj.data.body = text

        print ( "Done Adding " + text )



    def refresh_molecules ( self ):
        """ Refresh the display """
        app = bpy.context.scene.molecule_simulation
        if app.run_mcell:
            bpy.ops.cbm.refresh_operator()


    def change_molecule_display ( self, mol, glyph="Cube", scale=1.0, red=-1, green=-1, blue=-1 ):
        app = bpy.context.scene.molecule_simulation
        if app.run_mcell:
            #if mol.name == "Molecule":
            #    print ("Name isn't correct")
            #    return
            print ( "Changing Display for Molecule \"" + mol.name + "\" to R="+str(red)+",G="+str(green)+",B="+str(blue) )
            #self.mcell.cellblender_main_panel.molecule_select = True
            #self.mcell.molecules.show_display = True
            mol.glyph = glyph
            mol.scale = scale
            if red >= 0: mol.color.r = red
            if green >= 0: mol.color.g = green
            if blue >= 0: mol.color.b = blue

            print ( "Done Changing Display for Molecule \"" + mol.name + "\"" )

    def get_3d_view_spaces(self):
        spaces_3d = []
        for area in self.context.screen.areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    spaces_3d = spaces_3d + [space]
                    # area.spaces.active.show_manipulator = False
        return spaces_3d



    def scale_view_distance ( self, scale ):
        """ Change the view distance for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_distance *= scale
        #bpy.ops.view3d.zoom(delta=3)
        #set_view_3d()


    def set_axis_angle ( self, axis, angle ):
        """ Change the view axis and angle for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_rotation.axis = mathutils.Vector(axis)
            space.region_3d.view_rotation.angle = angle
        #set_view_3d()


    def hide_manipulator ( self, hide=True ):
        # C.screen.areas[4].spaces[0].show_manipulator = False
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.show_manipulator = not hide


    def switch_to_perspective ( self ):
        """ Change to perspective for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_perspective = 'PERSP'

    def switch_to_orthographic ( self ):
        """ Change to orthographic for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_perspective = 'ORTHO'

    def play_animation ( self ):
        """ Play the animation """
        app = bpy.context.scene.molecule_simulation
        if app.run_mcell:
            bpy.ops.screen.animation_play()


#### Start of Molecule Shape Code #### 

class point:
  x=0;
  y=0;
  z=0;

  def __init__ ( self, x, y, z ):
    self.x = x;
    self.y = y;
    self.z = z;

  def toList ( self ):
    return ( [ self.x, self.y, self.z ] );

  def toString ( self ):
    return ( "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")" );


class face:
  verts = [];
  
  def __init__ ( self, v1, v2, v3 ):
    self.verts = [];
    self.verts.append ( v1 );
    self.verts.append ( v2 );
    self.verts.append ( v3 );
  
  def toString( self ):
    return ( "[" + str(verts[0]) + "," + str(verts[1]) + "," + str(verts[2]) + "]" );


class plf_object:

  # An object that can hold points and faces (the "L" in PLF stood for Lines which are not needed here)

  points = []
  faces = []
  
  def __init__ ( self ):
    self.points = []
    self.faces = []


class CellBlender_Octahedron (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0.005,0.005,0],[0.005,-0.005,0],[-0.005,-0.005,0],[-0.005,0.005,0],[0,0,0.005],[0,0,-0.005] ]

    fcs = [
      [0,4,1],[0,1,5],[0,3,4],[2,4,3],[1,4,2],[1,2,5],[2,3,5],[0,5,3] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Cube (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0.005,0.005,-0.005],[0.005,-0.005,-0.005],[-0.005,-0.005,-0.005],[-0.005,0.005,-0.005],[0.005,0.005,0.005],
      [0.005,-0.005,0.005],[-0.005,-0.005,0.005],[-0.005,0.005,0.005] ]

    fcs = [
      [1,2,3],[7,6,5],[4,5,1],[5,6,2],[2,6,7],[0,3,7],[0,1,3],[4,7,5],[0,4,1],[1,5,2],[3,2,7], [4,0,7] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Icosahedron (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0,0,-0.005],[0.003618,-0.002629,-0.002236],[-0.001382,-0.004253,-0.002236],[-0.004472,0,-0.002236],[-0.001382,0.004253,-0.002236],
      [0.003618,0.002629,-0.002236],[0.001382,-0.004253,0.002236],[-0.003618,-0.002629,0.002236],[-0.003618,0.002629,0.002236],
      [0.001382,0.004253,0.002236],[0.004472,0,0.002236],[0,0,0.005] ]

    fcs = [
      [2,0,1],[1,0,5],[3,0,2],[4,0,3],[5,0,4],[1,5,10],[2,1,6],[3,2,7],[4,3,8],[5,4,9],[6,1,10],
      [7,2,6],[8,3,7],[9,4,8],[10,5,9],[6,10,11],[7,6,11],[8,7,11],[9,8,11],[10,9,11] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Cone (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0,0.005,-0.005],[0.001913,0.004619,-0.005],[0.003536,0.003536,-0.005],[0.004619,0.001913,-0.005],[0.005,-2.186e-10,-0.005],
      [0.004619,-0.001913,-0.005],[0.003536,-0.003536,-0.005],[0.001913,-0.004619,-0.005],[7.55e-10,-0.005,-0.005],
      [-0.001913,-0.004619,-0.005],[-0.003536,-0.003536,-0.005],[-0.004619,-0.001913,-0.005],[-0.005,5.962e-11,-0.005],
      [-0.004619,0.001913,-0.005],[-0.003536,0.003536,-0.005],[-0.001913,0.004619,-0.005],[0,0,0.005],[0,0,-0.005] ]

    fcs = [
      [1,0,16],[16,2,1],[16,3,2],[16,4,3],[16,5,4],[16,6,5],[16,7,6],[16,8,7],[16,9,8],[16,10,9],[16,11,10],
      [16,12,11],[16,13,12],[16,14,13],[16,15,14],[16,0,15],[17,0,1],[17,1,2],[17,2,3],[17,3,4],[17,4,5],[17,5,6],
      [17,6,7],[17,7,8],[17,8,9],[17,9,10],[17,10,11],[17,11,12],[17,12,13],[17,13,14],[17,14,15],[15,0,17] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Cylinder (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0,0.005,-0.005],[0.001913,0.004619,-0.005],[0.003536,0.003536,-0.005],[0.004619,0.001913,-0.005],[0.005,-2.186e-10,-0.005],
      [0.004619,-0.001913,-0.005],[0.003536,-0.003536,-0.005],[0.001913,-0.004619,-0.005],[7.55e-10,-0.005,-0.005],
      [-0.001913,-0.004619,-0.005],[-0.003536,-0.003536,-0.005],[-0.004619,-0.001913,-0.005],[-0.005,5.962e-11,-0.005],
      [-0.004619,0.001913,-0.005],[-0.003536,0.003536,-0.005],[-0.001913,0.004619,-0.005],[3.258e-09,0.005,0.005],
      [0.001913,0.004619,0.005],[0.003536,0.003536,0.005],[0.004619,0.001913,0.005],[0.005,-6.457e-09,0.005],
      [0.004619,-0.001913,0.005],[0.003536,-0.003536,0.005],[0.001913,-0.004619,0.005],[-9.656e-09,-0.005,0.005],
      [-0.001913,-0.004619,0.005],[-0.003536,-0.003536,0.005],[-0.004619,-0.001913,0.005],[-0.005,1.285e-08,0.005],
      [-0.004619,0.001913,0.005],[-0.003536,0.003536,0.005],[-0.001913,0.004619,0.005],[0,0,-0.005],[0,0,0.005] ]

    fcs = [
      [32,0,1],[33,17,16],[32,1,2],[33,18,17],[32,2,3],[33,19,18],[32,3,4],[33,20,19],[32,4,5],[33,21,20],[32,5,6],
      [33,22,21],[32,6,7],[33,23,22],[32,7,8],[33,24,23],[32,8,9],[33,25,24],[32,9,10],[33,26,25],[32,10,11],
      [33,27,26],[32,11,12],[33,28,27],[32,12,13],[33,29,28],[32,13,14],[33,30,29],[32,14,15],[33,31,30],[15,0,32],
      [33,16,31],[16,17,1],[17,18,2],[18,19,3],[19,20,4],[20,21,5],[21,22,6],[22,23,7],[23,24,8],[24,25,9],
      [25,26,10],[26,27,11],[27,28,12],[28,29,13],[29,30,14],[30,31,15],[0,15,31],[0,16,1],[1,17,2],[2,18,3],
      [3,19,4],[4,20,5],[5,21,6],[6,22,7],[7,23,8],[8,24,9],[9,25,10],[10,26,11],[11,27,12],[12,28,13],[13,29,14],
      [14,30,15],[16,0,31] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Torus (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0.005,0,0],[0.004905,0,0.0004784],[0.004634,0,0.0008839],[0.004228,0,0.001155],[0.00375,0,0.00125],[0.003272,0,0.001155],
      [0.002866,0,0.0008839],[0.002595,0,0.0004784],[0.0025,0,1.531e-19],[0.002595,0,-0.0004784],[0.002866,0,-0.0008839],
      [0.003272,0,-0.001155],[0.00375,0,-0.00125],[0.004228,0,-0.001155],[0.004634,0,-0.0008839],[0.004905,0,-0.0004784],
      [0.004619,0.001913,0],[0.004531,0.001877,0.0004784],[0.004281,0.001773,0.0008839],[0.003906,0.001618,0.001155],
      [0.003465,0.001435,0.00125],[0.003023,0.001252,0.001155],[0.002648,0.001097,0.0008839],[0.002398,0.0009931,0.0004784],
      [0.00231,0.0009567,1.531e-19],[0.002398,0.0009931,-0.0004784],[0.002648,0.001097,-0.0008839],[0.003023,0.001252,-0.001155],
      [0.003465,0.001435,-0.00125],[0.003906,0.001618,-0.001155],[0.004281,0.001773,-0.0008839],[0.004531,0.001877,-0.0004784],
      [0.003536,0.003536,0],[0.003468,0.003468,0.0004784],[0.003277,0.003277,0.0008839],[0.00299,0.00299,0.001155],
      [0.002652,0.002652,0.00125],[0.002313,0.002313,0.001155],[0.002027,0.002027,0.0008839],[0.001835,0.001835,0.0004784],
      [0.001768,0.001768,1.531e-19],[0.001835,0.001835,-0.0004784],[0.002027,0.002027,-0.0008839],[0.002313,0.002313,-0.001155],
      [0.002652,0.002652,-0.00125],[0.00299,0.00299,-0.001155],[0.003277,0.003277,-0.0008839],[0.003468,0.003468,-0.0004784],
      [0.001913,0.004619,0],[0.001877,0.004531,0.0004784],[0.001773,0.004281,0.0008839],[0.001618,0.003906,0.001155],
      [0.001435,0.003465,0.00125],[0.001252,0.003023,0.001155],[0.001097,0.002648,0.0008839],[0.0009931,0.002398,0.0004784],
      [0.0009567,0.00231,1.531e-19],[0.0009931,0.002398,-0.0004784],[0.001097,0.002648,-0.0008839],[0.001252,0.003023,-0.001155],
      [0.001435,0.003465,-0.00125],[0.001618,0.003906,-0.001155],[0.001773,0.004281,-0.0008839],[0.001877,0.004531,-0.0004784],
      [4.47e-10,0.005,0],[4.47e-10,0.004905,0.0004784],[4.47e-10,0.004634,0.0008839],[2.98e-10,0.004228,0.001155],
      [4.47e-10,0.00375,0.00125],[1.49e-10,0.003272,0.001155],[2.98e-10,0.002866,0.0008839],[1.49e-10,0.002595,0.0004784],
      [2.235e-10,0.0025,1.531e-19],[1.49e-10,0.002595,-0.0004784],[2.98e-10,0.002866,-0.0008839],[1.49e-10,0.003272,-0.001155],
      [4.47e-10,0.00375,-0.00125],[2.98e-10,0.004228,-0.001155],[4.47e-10,0.004634,-0.0008839],[4.47e-10,0.004905,-0.0004784],
      [-0.001913,0.004619,0],[-0.001877,0.004531,0.0004784],[-0.001773,0.004281,0.0008839],[-0.001618,0.003906,0.001155],
      [-0.001435,0.003465,0.00125],[-0.001252,0.003023,0.001155],[-0.001097,0.002648,0.0008839],[-0.0009931,0.002398,0.0004784],
      [-0.0009567,0.00231,1.531e-19],[-0.0009931,0.002398,-0.0004784],[-0.001097,0.002648,-0.0008839],[-0.001252,0.003023,-0.001155],
      [-0.001435,0.003465,-0.00125],[-0.001618,0.003906,-0.001155],[-0.001773,0.004281,-0.0008839],[-0.001877,0.004531,-0.0004784],
      [-0.003536,0.003536,0],[-0.003468,0.003468,0.0004784],[-0.003277,0.003277,0.0008839],[-0.00299,0.00299,0.001155],
      [-0.002652,0.002652,0.00125],[-0.002313,0.002313,0.001155],[-0.002027,0.002027,0.0008839],[-0.001835,0.001835,0.0004784],
      [-0.001768,0.001768,1.531e-19],[-0.001835,0.001835,-0.0004784],[-0.002027,0.002027,-0.0008839],[-0.002313,0.002313,-0.001155],
      [-0.002652,0.002652,-0.00125],[-0.00299,0.00299,-0.001155],[-0.003277,0.003277,-0.0008839],[-0.003468,0.003468,-0.0004784],
      [-0.004619,0.001913,0],[-0.004531,0.001877,0.0004784],[-0.004281,0.001773,0.0008839],[-0.003906,0.001618,0.001155],
      [-0.003465,0.001435,0.00125],[-0.003023,0.001252,0.001155],[-0.002648,0.001097,0.0008839],[-0.002398,0.0009931,0.0004784],
      [-0.00231,0.0009567,1.531e-19],[-0.002398,0.0009931,-0.0004784],[-0.002648,0.001097,-0.0008839],[-0.003023,0.001252,-0.001155],
      [-0.003465,0.001435,-0.00125],[-0.003906,0.001618,-0.001155],[-0.004281,0.001773,-0.0008839],[-0.004531,0.001877,-0.0004784],
      [-0.005,4.371e-10,0],[-0.004905,4.288e-10,0.0004784],[-0.004634,4.051e-10,0.0008839],[-0.004228,3.697e-10,0.001155],
      [-0.00375,3.278e-10,0.00125],[-0.003272,2.86e-10,0.001155],[-0.002866,2.506e-10,0.0008839],[-0.002595,2.269e-10,0.0004784],
      [-0.0025,2.186e-10,1.531e-19],[-0.002595,2.269e-10,-0.0004784],[-0.002866,2.506e-10,-0.0008839],[-0.003272,2.86e-10,-0.001155],
      [-0.00375,3.278e-10,-0.00125],[-0.004228,3.697e-10,-0.001155],[-0.004634,4.051e-10,-0.0008839],[-0.004905,4.288e-10,-0.0004784],
      [-0.004619,-0.001913,0],[-0.004531,-0.001877,0.0004784],[-0.004281,-0.001773,0.0008839],[-0.003906,-0.001618,0.001155],
      [-0.003465,-0.001435,0.00125],[-0.003023,-0.001252,0.001155],[-0.002648,-0.001097,0.0008839],[-0.002398,-0.0009931,0.0004784],
      [-0.00231,-0.0009567,1.531e-19],[-0.002398,-0.0009931,-0.0004784],[-0.002648,-0.001097,-0.0008839],[-0.003023,-0.001252,-0.001155],
      [-0.003465,-0.001435,-0.00125],[-0.003906,-0.001618,-0.001155],[-0.004281,-0.001773,-0.0008839],[-0.004531,-0.001877,-0.0004784],
      [-0.003536,-0.003536,0],[-0.003468,-0.003468,0.0004784],[-0.003277,-0.003277,0.0008839],[-0.00299,-0.00299,0.001155],
      [-0.002652,-0.002652,0.00125],[-0.002313,-0.002313,0.001155],[-0.002027,-0.002027,0.0008839],[-0.001835,-0.001835,0.0004784],
      [-0.001768,-0.001768,1.531e-19],[-0.001835,-0.001835,-0.0004784],[-0.002027,-0.002027,-0.0008839],[-0.002313,-0.002313,-0.001155],
      [-0.002652,-0.002652,-0.00125],[-0.00299,-0.00299,-0.001155],[-0.003277,-0.003277,-0.0008839],[-0.003468,-0.003468,-0.0004784],
      [-0.001913,-0.004619,0],[-0.001877,-0.004531,0.0004784],[-0.001773,-0.004281,0.0008839],[-0.001618,-0.003906,0.001155],
      [-0.001435,-0.003465,0.00125],[-0.001252,-0.003023,0.001155],[-0.001097,-0.002648,0.0008839],[-0.0009931,-0.002398,0.0004784],
      [-0.0009567,-0.00231,1.531e-19],[-0.0009931,-0.002398,-0.0004784],[-0.001097,-0.002648,-0.0008839],[-0.001252,-0.003023,-0.001155],
      [-0.001435,-0.003465,-0.00125],[-0.001618,-0.003906,-0.001155],[-0.001773,-0.004281,-0.0008839],[-0.001877,-0.004531,-0.0004784],
      [4.47e-10,-0.005,0],[4.47e-10,-0.004905,0.0004784],[4.47e-10,-0.004634,0.0008839],[2.98e-10,-0.004228,0.001155],
      [4.47e-10,-0.00375,0.00125],[1.49e-10,-0.003272,0.001155],[2.98e-10,-0.002866,0.0008839],[1.49e-10,-0.002595,0.0004784],
      [2.235e-10,-0.0025,1.531e-19],[1.49e-10,-0.002595,-0.0004784],[2.98e-10,-0.002866,-0.0008839],[1.49e-10,-0.003272,-0.001155],
      [4.47e-10,-0.00375,-0.00125],[2.98e-10,-0.004228,-0.001155],[4.47e-10,-0.004634,-0.0008839],[4.47e-10,-0.004905,-0.0004784],
      [0.001913,-0.004619,0],[0.001877,-0.004531,0.0004784],[0.001773,-0.004281,0.0008839],[0.001618,-0.003906,0.001155],
      [0.001435,-0.003465,0.00125],[0.001252,-0.003023,0.001155],[0.001097,-0.002648,0.0008839],[0.0009931,-0.002398,0.0004784],
      [0.0009567,-0.00231,1.531e-19],[0.0009931,-0.002398,-0.0004784],[0.001097,-0.002648,-0.0008839],[0.001252,-0.003023,-0.001155],
      [0.001435,-0.003465,-0.00125],[0.001618,-0.003906,-0.001155],[0.001773,-0.004281,-0.0008839],[0.001877,-0.004531,-0.0004784],
      [0.003536,-0.003536,0],[0.003468,-0.003468,0.0004784],[0.003277,-0.003277,0.0008839],[0.00299,-0.00299,0.001155],
      [0.002652,-0.002652,0.00125],[0.002313,-0.002313,0.001155],[0.002027,-0.002027,0.0008839],[0.001835,-0.001835,0.0004784],
      [0.001768,-0.001768,1.531e-19],[0.001835,-0.001835,-0.0004784],[0.002027,-0.002027,-0.0008839],[0.002313,-0.002313,-0.001155],
      [0.002652,-0.002652,-0.00125],[0.00299,-0.00299,-0.001155],[0.003277,-0.003277,-0.0008839],[0.003468,-0.003468,-0.0004784],
      [0.004619,-0.001913,0],[0.004531,-0.001877,0.0004784],[0.004281,-0.001773,0.0008839],[0.003906,-0.001618,0.001155],
      [0.003465,-0.001435,0.00125],[0.003023,-0.001252,0.001155],[0.002648,-0.001097,0.0008839],[0.002398,-0.0009931,0.0004784],
      [0.00231,-0.0009567,1.531e-19],[0.002398,-0.0009931,-0.0004784],[0.002648,-0.001097,-0.0008839],[0.003023,-0.001252,-0.001155],
      [0.003465,-0.001435,-0.00125],[0.003906,-0.001618,-0.001155],[0.004281,-0.001773,-0.0008839],[0.004531,-0.001877,-0.0004784] ]

    fcs = [
      [0,16,17],[17,18,2],[18,19,3],[3,19,20],[4,20,21],[21,22,6],[22,23,7],[23,24,8],[24,25,9],[25,26,10],
      [26,27,11],[27,28,12],[28,29,13],[29,30,14],[14,30,31],[15,31,16],[32,33,17],[33,34,18],[34,35,19],[35,36,20],
      [36,37,21],[37,38,22],[22,38,39],[39,40,24],[24,40,41],[25,41,42],[26,42,43],[27,43,44],[44,45,29],[29,45,46],
      [30,46,47],[31,47,32],[48,49,33],[33,49,50],[50,51,35],[35,51,52],[52,53,37],[53,54,38],[38,54,55],[55,56,40],
      [56,57,41],[57,58,42],[58,59,43],[59,60,44],[44,60,61],[61,62,46],[62,63,47],[47,63,48],[64,65,49],[49,65,66],
      [50,66,67],[67,68,52],[68,69,53],[69,70,54],[54,70,71],[71,72,56],[72,73,57],[73,74,58],[74,75,59],[59,75,76],
      [76,77,61],[77,78,62],[78,79,63],[63,79,64],[80,81,65],[81,82,66],[82,83,67],[83,84,68],[84,85,69],[85,86,70],
      [86,87,71],[71,87,88],[88,89,73],[89,90,74],[74,90,91],[75,91,92],[92,93,77],[93,94,78],[78,94,95],[95,80,64],
      [80,96,97],[97,98,82],[98,99,83],[99,100,84],[100,101,85],[101,102,86],[102,103,87],[103,104,88],[88,104,105],
      [105,106,90],[90,106,107],[91,107,108],[108,109,93],[93,109,110],[110,111,95],[95,111,96],[112,113,97],
      [113,114,98],[114,115,99],[115,116,100],[116,117,101],[117,118,102],[118,119,103],[103,119,120],[120,121,105],
      [105,121,122],[122,123,107],[107,123,124],[124,125,109],[125,126,110],[126,127,111],[111,127,112],[128,129,113],
      [113,129,130],[114,130,131],[131,132,116],[132,133,117],[133,134,118],[118,134,135],[135,136,120],[120,136,137],
      [137,138,122],[138,139,123],[139,140,124],[140,141,125],[141,142,126],[142,143,127],[127,143,128],[128,144,145],
      [145,146,130],[146,147,131],[147,148,132],[148,149,133],[149,150,134],[150,151,135],[135,151,152],[152,153,137],
      [137,153,154],[154,155,139],[155,156,140],[156,157,141],[141,157,158],[158,159,143],[143,159,144],[144,160,161],
      [161,162,146],[146,162,163],[147,163,164],[148,164,165],[165,166,150],[166,167,151],[167,168,152],[152,168,169],
      [169,170,154],[154,170,171],[171,172,156],[172,173,157],[157,173,174],[158,174,175],[175,160,144],[176,177,161],
      [177,178,162],[162,178,179],[179,180,164],[164,180,181],[181,182,166],[166,182,183],[167,183,184],[184,185,169],
      [185,186,170],[186,187,171],[187,188,172],[188,189,173],[189,190,174],[174,190,191],[191,176,160],[192,193,177],
      [177,193,194],[194,195,179],[179,195,196],[180,196,197],[197,198,182],[182,198,199],[199,200,184],[200,201,185],
      [201,202,186],[186,202,203],[203,204,188],[204,205,189],[205,206,190],[206,207,191],[191,207,192],[192,208,209],
      [209,210,194],[210,211,195],[211,212,196],[196,212,213],[213,214,198],[214,215,199],[215,216,200],[216,217,201],
      [217,218,202],[202,218,219],[219,220,204],[220,221,205],[205,221,222],[206,222,223],[223,208,192],[224,225,209],
      [209,225,226],[226,227,211],[211,227,228],[228,229,213],[229,230,214],[214,230,231],[215,231,232],[232,233,217],
      [233,234,218],[218,234,235],[235,236,220],[236,237,221],[237,238,222],[238,239,223],[223,239,224],[240,241,225],
      [225,241,242],[226,242,243],[243,244,228],[244,245,229],[245,246,230],[246,247,231],[231,247,248],[248,249,233],
      [249,250,234],[250,251,235],[251,252,236],[236,252,253],[253,254,238],[254,255,239],[239,255,240],[0,1,241],
      [1,2,242],[2,3,243],[243,3,4],[4,5,245],[5,6,246],[6,7,247],[247,7,8],[8,9,249],[9,10,250],[250,10,11],
      [11,12,252],[12,13,253],[13,14,254],[14,15,255],[240,255,15],[1,0,17],[1,17,2],[2,18,3],[4,3,20],[5,4,21],
      [5,21,6],[6,22,7],[7,23,8],[8,24,9],[9,25,10],[10,26,11],[11,27,12],[12,28,13],[13,29,14],[15,14,31],
      [0,15,16],[16,32,17],[17,33,18],[18,34,19],[19,35,20],[20,36,21],[21,37,22],[23,22,39],[23,39,24],[25,24,41],
      [26,25,42],[27,26,43],[28,27,44],[28,44,29],[30,29,46],[31,30,47],[16,31,32],[32,48,33],[34,33,50],[34,50,35],
      [36,35,52],[36,52,37],[37,53,38],[39,38,55],[39,55,40],[40,56,41],[41,57,42],[42,58,43],[43,59,44],[45,44,61],
      [45,61,46],[46,62,47],[32,47,48],[48,64,49],[50,49,66],[51,50,67],[51,67,52],[52,68,53],[53,69,54],[55,54,71],
      [55,71,56],[56,72,57],[57,73,58],[58,74,59],[60,59,76],[60,76,61],[61,77,62],[62,78,63],[48,63,64],[64,80,65],
      [65,81,66],[66,82,67],[67,83,68],[68,84,69],[69,85,70],[70,86,71],[72,71,88],[72,88,73],[73,89,74],[75,74,91],
      [76,75,92],[76,92,77],[77,93,78],[79,78,95],[79,95,64],[81,80,97],[81,97,82],[82,98,83],[83,99,84],[84,100,85],
      [85,101,86],[86,102,87],[87,103,88],[89,88,105],[89,105,90],[91,90,107],[92,91,108],[92,108,93],[94,93,110],
      [94,110,95],[80,95,96],[96,112,97],[97,113,98],[98,114,99],[99,115,100],[100,116,101],[101,117,102],[102,118,103],
      [104,103,120],[104,120,105],[106,105,122],[106,122,107],[108,107,124],[108,124,109],[109,125,110],[110,126,111],
      [96,111,112],[112,128,113],[114,113,130],[115,114,131],[115,131,116],[116,132,117],[117,133,118],[119,118,135],
      [119,135,120],[121,120,137],[121,137,122],[122,138,123],[123,139,124],[124,140,125],[125,141,126],[126,142,127],
      [112,127,128],[129,128,145],[129,145,130],[130,146,131],[131,147,132],[132,148,133],[133,149,134],[134,150,135],
      [136,135,152],[136,152,137],[138,137,154],[138,154,139],[139,155,140],[140,156,141],[142,141,158],[142,158,143],
      [128,143,144],[145,144,161],[145,161,146],[147,146,163],[148,147,164],[149,148,165],[149,165,150],[150,166,151],
      [151,167,152],[153,152,169],[153,169,154],[155,154,171],[155,171,156],[156,172,157],[158,157,174],[159,158,175],
      [159,175,144],[160,176,161],[161,177,162],[163,162,179],[163,179,164],[165,164,181],[165,181,166],[167,166,183],
      [168,167,184],[168,184,169],[169,185,170],[170,186,171],[171,187,172],[172,188,173],[173,189,174],[175,174,191],
      [175,191,160],[176,192,177],[178,177,194],[178,194,179],[180,179,196],[181,180,197],[181,197,182],[183,182,199],
      [183,199,184],[184,200,185],[185,201,186],[187,186,203],[187,203,188],[188,204,189],[189,205,190],[190,206,191],
      [176,191,192],[193,192,209],[193,209,194],[194,210,195],[195,211,196],[197,196,213],[197,213,198],[198,214,199],
      [199,215,200],[200,216,201],[201,217,202],[203,202,219],[203,219,204],[204,220,205],[206,205,222],[207,206,223],
      [207,223,192],[208,224,209],[210,209,226],[210,226,211],[212,211,228],[212,228,213],[213,229,214],[215,214,231],
      [216,215,232],[216,232,217],[217,233,218],[219,218,235],[219,235,220],[220,236,221],[221,237,222],[222,238,223],
      [208,223,224],[224,240,225],[226,225,242],[227,226,243],[227,243,228],[228,244,229],[229,245,230],[230,246,231],
      [232,231,248],[232,248,233],[233,249,234],[234,250,235],[235,251,236],[237,236,253],[237,253,238],[238,254,239],
      [224,239,240],[240,0,241],[241,1,242],[242,2,243],[244,243,4],[244,4,245],[245,5,246],[246,6,247],[248,247,8],
      [248,8,249],[249,9,250],[251,250,11],[251,11,252],[252,12,253],[253,13,254],[254,14,255],[0,240,15] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Sphere1 (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0,0,-0.005],[0.003618,-0.002629,-0.002236],[-0.001382,-0.004253,-0.002236],[-0.004472,0,-0.002236],[-0.001382,0.004253,-0.002236],
      [0.003618,0.002629,-0.002236],[0.001382,-0.004253,0.002236],[-0.003618,-0.002629,0.002236],[-0.003618,0.002629,0.002236],
      [0.001382,0.004253,0.002236],[0.004472,0,0.002236],[0,0,0.005],[-0.0008123,-0.0025,-0.004253],[0.002127,-0.001545,-0.004253],
      [0.001314,-0.004045,-0.002629],[0.002127,0.001545,-0.004253],[0.004253,0,-0.002629],[-0.002629,0,-0.004253],
      [-0.003441,-0.0025,-0.002629],[-0.0008123,0.0025,-0.004253],[-0.003441,0.0025,-0.002629],[0.001314,0.004045,-0.002629],
      [0.004755,0.001545,0],[0.004755,-0.001545,0],[0.002939,-0.004045,0],[0,-0.005,0],[-0.002939,-0.004045,0],
      [-0.004755,-0.001545,0],[-0.004755,0.001545,0],[-0.002939,0.004045,0],[0,0.005,0],[0.002939,0.004045,0],
      [0.003441,-0.0025,0.002629],[-0.001314,-0.004045,0.002629],[-0.004253,0,0.002629],[-0.001314,0.004045,0.002629],
      [0.003441,0.0025,0.002629],[0.002629,0,0.004253],[0.0008123,-0.0025,0.004253],[-0.002127,-0.001545,0.004253],
      [-0.002127,0.001545,0.004253],[0.0008123,0.0025,0.004253] ]

    fcs = [
      [14,2,12],[12,13,14],[1,14,13],[12,0,13],[16,1,13],[13,15,16],[5,16,15],[13,0,15],[18,3,17],[17,12,18],
      [2,18,12],[17,0,12],[20,4,19],[19,17,20],[3,20,17],[19,0,17],[21,5,15],[15,19,21],[4,21,19],[15,0,19],
      [23,1,16],[16,22,23],[10,23,22],[22,16,5],[25,2,14],[14,24,25],[6,25,24],[24,14,1],[27,3,18],[18,26,27],
      [7,27,26],[26,18,2],[29,4,20],[20,28,29],[8,29,28],[28,20,3],[31,5,21],[21,30,31],[9,31,30],[30,21,4],
      [32,6,24],[24,23,32],[10,32,23],[23,24,1],[33,7,26],[26,25,33],[6,33,25],[25,26,2],[34,8,28],[28,27,34],
      [7,34,27],[27,28,3],[35,9,30],[30,29,35],[8,35,29],[29,30,4],[36,10,22],[22,31,36],[9,36,31],[31,22,5],
      [38,6,32],[32,37,38],[11,38,37],[37,32,10],[39,7,33],[33,38,39],[11,39,38],[38,33,6],[40,8,34],[34,39,40],
      [11,40,39],[39,34,7],[41,9,35],[35,40,41],[11,41,40],[40,35,8],[37,10,36],[36,41,37],[11,37,41],[41,36,9] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Sphere2 (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [0,0,-0.005],[0.003618,-0.002629,-0.002236],[-0.001382,-0.004253,-0.002236],[-0.004472,0,-0.002236],[-0.001382,0.004253,-0.002236],
      [0.003618,0.002629,-0.002236],[0.001382,-0.004253,0.002236],[-0.003618,-0.002629,0.002236],[-0.003618,0.002629,0.002236],
      [0.001382,0.004253,0.002236],[0.004472,0,0.002236],[0,0,0.005],[-0.0008123,-0.0025,-0.004253],[0.002127,-0.001545,-0.004253],
      [0.001314,-0.004045,-0.002629],[0.002127,0.001545,-0.004253],[0.004253,0,-0.002629],[-0.002629,0,-0.004253],
      [-0.003441,-0.0025,-0.002629],[-0.0008123,0.0025,-0.004253],[-0.003441,0.0025,-0.002629],[0.001314,0.004045,-0.002629],
      [0.004755,0.001545,0],[0.004755,-0.001545,0],[0.002939,-0.004045,0],[0,-0.005,0],[-0.002939,-0.004045,0],
      [-0.004755,-0.001545,0],[-0.004755,0.001545,0],[-0.002939,0.004045,0],[0,0.005,0],[0.002939,0.004045,0],
      [0.003441,-0.0025,0.002629],[-0.001314,-0.004045,0.002629],[-0.004253,0,0.002629],[-0.001314,0.004045,0.002629],
      [0.003441,0.0025,0.002629],[0.002629,0,0.004253],[0.0008123,-0.0025,0.004253],[-0.002127,-0.001545,0.004253],
      [-0.002127,0.001545,0.004253],[0.0008123,0.0025,0.004253],[-0.001141,-0.00351,-0.003373],[-0.0004222,-0.001299,-0.00481],
      [0.002986,-0.002169,-0.003373],[0.001105,-0.0008031,-0.00481],[-3.513e-05,-0.004313,-0.002529],[0.002564,-0.003469,-0.002529],
      [0.002986,0.002169,-0.003373],[0.001105,0.0008031,-0.00481],[0.004091,-0.001366,-0.002529],[0.004091,0.001366,-0.002529],
      [-0.003691,0,-0.003373],[-0.001366,0,-0.00481],[-0.002507,-0.00351,-0.002529],[-0.004113,-0.001299,-0.002529],
      [-0.001141,0.00351,-0.003373],[-0.0004222,0.001299,-0.00481],[-0.002507,0.00351,-0.002529],[-0.004113,0.001299,-0.002529],
      [-3.513e-05,0.004313,-0.002529],[0.002564,0.003469,-0.002529],[0.004352,0.002169,-0.001162],[0.004796,0.0008031,0.001162],
      [0.004352,-0.002169,-0.001162],[0.004796,-0.0008031,0.001162],[0.003408,-0.003469,-0.001162],[0.002246,-0.004313,0.001162],
      [-0.0007183,-0.00481,-0.001162],[0.0007183,-0.00481,0.001162],[-0.002246,-0.004313,-0.001162],[-0.003408,-0.003469,0.001162],
      [-0.004352,-0.002169,0.001162],[-0.004796,-0.0008031,-0.001162],[-0.004352,0.002169,0.001162],[-0.004796,0.0008031,-0.001162],
      [-0.002246,0.004313,-0.001162],[-0.003408,0.003469,0.001162],[0.0007183,0.00481,0.001162],[-0.0007183,0.00481,-0.001162],
      [0.002246,0.004313,0.001162],[0.003408,0.003469,-0.001162],[0.002507,-0.00351,0.002529],[0.004113,-0.001299,0.002529],
      [-0.002564,-0.003469,0.002529],[3.513e-05,-0.004313,0.002529],[-0.004091,-0.001366,0.002529],[-0.004091,0.001366,0.002529],
      [3.513e-05,0.004313,0.002529],[-0.002564,0.003469,0.002529],[0.002507,0.00351,0.002529],[0.004113,0.001299,0.002529],
      [0.001366,0,0.00481],[0.003691,0,0.003373],[0.001141,-0.00351,0.003373],[0.0004222,-0.001299,0.00481],
      [-0.002986,-0.002169,0.003373],[-0.001105,-0.0008031,0.00481],[-0.002986,0.002169,0.003373],[-0.001105,0.0008031,0.00481],
      [0.001141,0.00351,0.003373],[0.0004222,0.001299,0.00481],[0.000264,-0.003441,-0.003618],[0.000691,-0.002127,-0.004472],
      [0.001809,-0.002939,-0.003618],[0.003354,-0.0008123,-0.003618],[0.002236,0,-0.004472],[0.003354,0.0008123,-0.003618],
      [-0.003191,-0.001314,-0.003618],[-0.001809,-0.001314,-0.004472],[-0.002236,-0.002629,-0.003618],[-0.002236,0.002629,-0.003618],
      [-0.001809,0.001314,-0.004472],[-0.003191,0.001314,-0.003618],[0.001809,0.002939,-0.003618],[0.000691,0.002127,-0.004472],
      [0.000264,0.003441,-0.003618],[0.004736,-0.0008123,-0.001382],[0.004736,0.0008123,-0.001382],[0.005,0,0],
      [0.000691,-0.004755,-0.001382],[0.002236,-0.004253,-0.001382],[0.001545,-0.004755,0],[-0.004309,-0.002127,-0.001382],
      [-0.003354,-0.003441,-0.001382],[-0.004045,-0.002939,0],[-0.003354,0.003441,-0.001382],[-0.004309,0.002127,-0.001382],
      [-0.004045,0.002939,0],[0.002236,0.004253,-0.001382],[0.000691,0.004755,-0.001382],[0.001545,0.004755,0],
      [0.003354,-0.003441,0.001382],[0.004045,-0.002939,0],[0.004309,-0.002127,0.001382],[-0.002236,-0.004253,0.001382],
      [-0.001545,-0.004755,0],[-0.000691,-0.004755,0.001382],[-0.004736,0.0008123,0.001382],[-0.005,0,0],[-0.004736,-0.0008123,0.001382],
      [-0.000691,0.004755,0.001382],[-0.001545,0.004755,0],[-0.002236,0.004253,0.001382],[0.004309,0.002127,0.001382],
      [0.004045,0.002939,0],[0.003354,0.003441,0.001382],[0.002236,-0.002629,0.003618],[0.003191,-0.001314,0.003618],
      [0.001809,-0.001314,0.004472],[-0.001809,-0.002939,0.003618],[-0.000264,-0.003441,0.003618],[-0.000691,-0.002127,0.004472],
      [-0.003354,0.0008123,0.003618],[-0.003354,-0.0008123,0.003618],[-0.002236,0,0.004472],[-0.000264,0.003441,0.003618],
      [-0.001809,0.002939,0.003618],[-0.000691,0.002127,0.004472],[0.003191,0.001314,0.003618],[0.002236,0.002629,0.003618],
      [0.001809,0.001314,0.004472] ]

    fcs = [
      [102,14,46],[46,42,102],[12,102,42],[42,46,2],[102,12,103],[103,104,102],[14,102,104],[104,103,13],[44,1,47],
      [47,104,44],[13,44,104],[104,47,14],[45,13,103],[103,43,45],[0,45,43],[43,103,12],[105,16,50],[50,44,105],
      [13,105,44],[44,50,1],[105,13,106],[106,107,105],[16,105,107],[107,106,15],[48,5,51],[51,107,48],[15,48,107],
      [107,51,16],[49,15,106],[106,45,49],[0,49,45],[45,106,13],[108,18,55],[55,52,108],[17,108,52],[52,55,3],
      [108,17,109],[109,110,108],[18,108,110],[110,109,12],[42,2,54],[54,110,42],[12,42,110],[110,54,18],[43,12,109],
      [109,53,43],[0,43,53],[53,109,17],[111,20,58],[58,56,111],[19,111,56],[56,58,4],[111,19,112],[112,113,111],
      [20,111,113],[113,112,17],[52,3,59],[59,113,52],[17,52,113],[113,59,20],[53,17,112],[112,57,53],[0,53,57],
      [57,112,19],[114,21,61],[61,48,114],[15,114,48],[48,61,5],[114,15,115],[115,116,114],[21,114,116],[116,115,19],
      [56,4,60],[60,116,56],[19,56,116],[116,60,21],[57,19,115],[115,49,57],[0,57,49],[49,115,15],[117,23,64],
      [64,50,117],[16,117,50],[50,64,1],[117,16,118],[118,119,117],[23,117,119],[119,118,22],[63,10,65],[65,119,63],
      [22,63,119],[119,65,23],[62,22,118],[118,51,62],[5,62,51],[51,118,16],[120,25,68],[68,46,120],[14,120,46],
      [46,68,2],[120,14,121],[121,122,120],[25,120,122],[122,121,24],[67,6,69],[69,122,67],[24,67,122],[122,69,25],
      [66,24,121],[121,47,66],[1,66,47],[47,121,14],[123,27,73],[73,55,123],[18,123,55],[55,73,3],[123,18,124],
      [124,125,123],[27,123,125],[125,124,26],[71,7,72],[72,125,71],[26,71,125],[125,72,27],[70,26,124],[124,54,70],
      [2,70,54],[54,124,18],[126,29,76],[76,58,126],[20,126,58],[58,76,4],[126,20,127],[127,128,126],[29,126,128],
      [128,127,28],[74,8,77],[77,128,74],[28,74,128],[128,77,29],[75,28,127],[127,59,75],[3,75,59],[59,127,20],
      [129,31,81],[81,61,129],[21,129,61],[61,81,5],[129,21,130],[130,131,129],[31,129,131],[131,130,30],[78,9,80],
      [80,131,78],[30,78,131],[131,80,31],[79,30,130],[130,60,79],[4,79,60],[60,130,21],[132,32,82],[82,67,132],
      [24,132,67],[67,82,6],[132,24,133],[133,134,132],[32,132,134],[134,133,23],[65,10,83],[83,134,65],[23,65,134],
      [134,83,32],[64,23,133],[133,66,64],[1,64,66],[66,133,24],[135,33,84],[84,71,135],[26,135,71],[71,84,7],
      [135,26,136],[136,137,135],[33,135,137],[137,136,25],[69,6,85],[85,137,69],[25,69,137],[137,85,33],[68,25,136],
      [136,70,68],[2,68,70],[70,136,26],[138,34,87],[87,74,138],[28,138,74],[74,87,8],[138,28,139],[139,140,138],
      [34,138,140],[140,139,27],[72,7,86],[86,140,72],[27,72,140],[140,86,34],[73,27,139],[139,75,73],[3,73,75],
      [75,139,28],[141,35,88],[88,78,141],[30,141,78],[78,88,9],[141,30,142],[142,143,141],[35,141,143],[143,142,29],
      [77,8,89],[89,143,77],[29,77,143],[143,89,35],[76,29,142],[142,79,76],[4,76,79],[79,142,30],[144,36,91],
      [91,63,144],[22,144,63],[63,91,10],[144,22,145],[145,146,144],[36,144,146],[146,145,31],[80,9,90],[90,146,80],
      [31,80,146],[146,90,36],[81,31,145],[145,62,81],[5,81,62],[62,145,22],[147,38,94],[94,82,147],[32,147,82],
      [82,94,6],[147,32,148],[148,149,147],[38,147,149],[149,148,37],[92,11,95],[95,149,92],[37,92,149],[149,95,38],
      [93,37,148],[148,83,93],[10,93,83],[83,148,32],[150,39,96],[96,84,150],[33,150,84],[84,96,7],[150,33,151],
      [151,152,150],[39,150,152],[152,151,38],[95,11,97],[97,152,95],[38,95,152],[152,97,39],[94,38,151],[151,85,94],
      [6,94,85],[85,151,33],[153,40,98],[98,87,153],[34,153,87],[87,98,8],[153,34,154],[154,155,153],[40,153,155],
      [155,154,39],[97,11,99],[99,155,97],[39,97,155],[155,99,40],[96,39,154],[154,86,96],[7,96,86],[86,154,34],
      [156,41,100],[100,88,156],[35,156,88],[88,100,9],[156,35,157],[157,158,156],[41,156,158],[158,157,40],
      [99,11,101],[101,158,99],[40,99,158],[158,101,41],[98,40,157],[157,89,98],[8,98,89],[89,157,35],[159,37,93],
      [93,91,159],[36,159,91],[91,93,10],[159,36,160],[160,161,159],[37,159,161],[161,160,41],[101,11,92],[92,161,101],
      [41,101,161],[161,92,37],[100,41,160],[160,90,100],[9,100,90],[90,160,36] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class CellBlender_Receptor (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create an object of the requested size
    size_scale = 10

    self.points = [];
    self.faces = [];

    pts = [
      [-1.112e-09,0.004956,0.001781],[-1.097e-09,0.005,0.002473],[-1.113e-09,0.005,0.003012],[-1.074e-09,0.004996,0.00341],
      [-1.055e-09,0.004962,0.003742],[-1.099e-09,0.004854,0.004061],[0.004755,0.001545,0.003012],[0.003794,0.001233,-0.005168],
      [0.003914,0.001272,-0.005065],[0.003673,0.001194,-0.005233],[0.004003,0.001301,-0.004882],[0.004,0.0013,-0.004477],
      [0.003829,0.001244,-0.003764],[0.003536,0.001149,-0.002894],[0.003387,0.001101,-0.001916],[0.003591,0.001167,-0.0009425],
      [0.004011,0.001303,1.023e-05],[0.004451,0.001446,0.000946],[0.004714,0.001531,0.001781],[0.004755,0.001545,0.002473],
      [0.004751,0.001544,0.00341],[0.004719,0.001533,0.003742],[0.004617,0.0015,0.004061],[0.004407,0.001432,0.004363],
      [0.00413,0.001342,0.004584],[0.003888,0.001263,0.004691],[0.003707,0.001205,0.004725],[0.003566,0.001159,0.004729],
      [0.003425,0.001113,0.004725],[0.003245,0.001055,0.004691],[0.003002,0.0009759,0.004584],[0.002725,0.0008859,0.004363],
      [0.002516,0.0008178,0.004061],[0.002413,0.0007846,0.003742],[0.002381,0.0007742,0.00341],[0.002377,0.0007729,0.003012],
      [0.002377,0.0007729,0.002473],[0.002377,0.0007729,0.001781],[0.002351,0.0007643,0.000946],[0.002182,0.0007094,1.023e-05],
      [0.00199,0.0006471,-0.0009479],[0.001926,0.0006265,-0.001952],[0.002096,0.0006817,-0.002979],[0.002453,0.0007975,-0.003869],
      [0.002815,0.000915,-0.004438],[0.003073,0.0009989,-0.004872],[0.00324,0.001053,-0.005094],[0.003356,0.001091,-0.005186],
      [0.003458,0.001124,-0.005237],[0.003561,0.001157,-0.005256],[0.002853,-0.003927,0.004061],[0.002916,-0.004014,0.003742],
      [0.002936,-0.004042,0.00341],[0.002939,-0.004045,0.002473],[0.002913,-0.00401,0.001781],[0.002751,-0.003786,0.000946],
      [0.002939,-0.004045,0.003012],[0.002345,-0.003228,-0.005168],[0.002419,-0.00333,-0.005065],[0.002474,-0.003405,-0.004882],
      [0.002472,-0.003403,-0.004477],[0.002367,-0.003257,-0.003764],[0.002185,-0.003008,-0.002894],[0.002094,-0.002881,-0.001916],
      [0.00222,-0.003055,-0.0009425],[0.002479,-0.003412,1.023e-05],[0.002724,-0.003749,0.004363],[0.002553,-0.003513,0.004584],
      [0.002403,-0.003307,0.004691],[0.002291,-0.003154,0.004725],[0.002204,-0.003034,0.004729],[0.002117,-0.002914,0.004725],
      [0.002006,-0.002761,0.004691],[0.001856,-0.002554,0.004584],[0.001685,-0.002319,0.004363],[0.001555,-0.00214,0.004061],
      [0.001492,-0.002053,0.003742],[0.001472,-0.002026,0.00341],[0.001469,-0.002023,0.003012],[0.001469,-0.002023,0.002473],
      [0.001469,-0.002023,0.001781],[0.001453,-0.002,0.000946],[0.001349,-0.001856,1.023e-05],[0.00123,-0.001693,-0.0009479],
      [0.001191,-0.001639,-0.001952],[0.001296,-0.001784,-0.002979],[0.001516,-0.002087,-0.003869],[0.00174,-0.002395,-0.004438],
      [0.0019,-0.002615,-0.004872],[0.002003,-0.002757,-0.005094],[0.002074,-0.002855,-0.005186],[0.002137,-0.002942,-0.005237],
      [0.002201,-0.00303,-0.005256],[0.00227,-0.003125,-0.005233],[-0.002939,-0.004045,0.003012],[-0.002939,-0.004045,0.002473],
      [-0.002937,-0.004042,0.00341],[-0.003561,0.001157,-0.005256],[-0.003458,0.001123,-0.005237],[-0.003356,0.00109,-0.005186],
      [-0.00324,0.001053,-0.005094],[-0.003074,0.0009984,-0.004872],[-0.002815,0.0009143,-0.004438],[-0.002453,0.0007967,-0.003869],
      [-0.002097,0.0006808,-0.002979],[-0.001927,0.0006255,-0.001952],[-0.00199,0.0006461,-0.0009479],[-0.002182,0.0007085,1.023e-05],
      [-0.002351,0.0007634,0.000946],[-0.002377,0.000772,0.001781],[-0.002377,0.000772,0.002473],[-0.002377,0.000772,0.003012],
      [-0.002381,0.0007733,0.00341],[-0.002414,0.0007838,0.003742],[-0.002516,0.000817,0.004061],[-0.002726,0.0008852,0.004363],
      [-0.003003,0.0009753,0.004584],[-0.003245,0.001054,0.004691],[-0.003425,0.001113,0.004725],[-0.003566,0.001159,0.004729],
      [-0.003708,0.001204,0.004725],[-0.003888,0.001263,0.004691],[-0.00413,0.001342,0.004584],[-0.004011,0.001303,1.023e-05],
      [-0.003591,0.001167,-0.0009425],[-0.003387,0.0011,-0.001916],[-0.003536,0.001149,-0.002894],[-0.003829,0.001244,-0.003764],
      [-0.004,0.0013,-0.004477],[-0.004003,0.001301,-0.004882],[-0.003673,0.001193,-0.005233],[-0.003914,0.001272,-0.005065],
      [-0.003794,0.001233,-0.005168],[-0.00227,-0.003125,-0.005233],[-0.002201,-0.00303,-0.005256],[-0.002137,-0.002942,-0.005237],
      [-0.002074,-0.002855,-0.005186],[-0.002003,-0.002757,-0.005094],[-0.0019,-0.002615,-0.004872],[-0.00174,-0.002395,-0.004438],
      [-0.001516,-0.002087,-0.003869],[-0.001296,-0.001784,-0.002979],[-0.001191,-0.001639,-0.001952],[-0.00123,-0.001693,-0.0009479],
      [-0.001349,-0.001856,1.023e-05],[-0.001453,-0.002,0.000946],[-0.001469,-0.002023,0.001781],[-0.001469,-0.002023,0.002473],
      [-0.001469,-0.002023,0.003012],[-0.001472,-0.002026,0.00341],[-0.001492,-0.002053,0.003742],[-0.001555,-0.00214,0.004061],
      [-0.001685,-0.002319,0.004363],[-0.001856,-0.002554,0.004584],[-0.002006,-0.002761,0.004691],[-0.002117,-0.002914,0.004725],
      [-0.002204,-0.003034,0.004729],[-0.002291,-0.003154,0.004725],[-0.002403,-0.003307,0.004691],[-0.002553,-0.003513,0.004584],
      [-0.002724,-0.003749,0.004363],[-0.002853,-0.003927,0.004061],[-0.002917,-0.004014,0.003742],[-0.002913,-0.00401,0.001781],
      [-0.002751,-0.003786,0.000946],[-0.002479,-0.003412,1.023e-05],[-0.00222,-0.003055,-0.0009425],[-0.002094,-0.002881,-0.001916],
      [-0.002185,-0.003008,-0.002894],[-0.002367,-0.003257,-0.003764],[-0.002472,-0.003403,-0.004477],[-0.002474,-0.003405,-0.004882],
      [-0.002419,-0.00333,-0.005065],[-0.002345,-0.003228,-0.005168],[-0.004451,0.001446,0.000946],[-0.004714,0.001532,0.001781],
      [-0.004755,0.001545,0.002473],[-0.004755,0.001545,0.003012],[-0.004751,0.001544,0.00341],[-0.004719,0.001533,0.003742],
      [-0.004617,0.0015,0.004061],[-0.004407,0.001432,0.004363],[-1.314e-07,0.00399,-0.005168],[-1.041e-07,0.004116,-0.005065],
      [-1.586e-07,0.003862,-0.005233],[-8.427e-08,0.004209,-0.004882],[-8.523e-08,0.004206,-0.004477],[-1.232e-07,0.004026,-0.003764],
      [-1.892e-07,0.003718,-0.002894],[-2.225e-07,0.003561,-0.001916],[-1.764e-07,0.003776,-0.0009425],[-8.248e-08,0.004217,1.023e-05],
      [1.684e-08,0.00468,0.000946],[7.6e-09,0.004634,0.004363],[-5.528e-08,0.004343,0.004584],[-1.106e-07,0.004088,0.004691],
      [-1.513e-07,0.003898,0.004725],[-1.829e-07,0.00375,0.004729],[-2.145e-07,0.003601,0.004725],[-2.545e-07,0.003412,0.004691],
      [-3.088e-07,0.003157,0.004584],[-3.719e-07,0.002866,0.004363],[-4.195e-07,0.002645,0.004061],[-4.426e-07,0.002538,0.003742],
      [-4.498e-07,0.002504,0.00341],[-4.507e-07,0.0025,0.003012],[-4.507e-07,0.0025,0.002473],[-4.508e-07,0.0025,0.001781],
      [-4.566e-07,0.002472,0.000946],[-4.945e-07,0.002294,1.023e-05],[-5.379e-07,0.002092,-0.0009479],[-5.521e-07,0.002026,-0.001952],
      [-5.142e-07,0.002205,-0.002979],[-4.335e-07,0.002579,-0.003869],[-3.512e-07,0.00296,-0.004438],[-2.932e-07,0.003232,-0.004872],
      [-2.55e-07,0.003407,-0.005094],[-2.299e-07,0.003529,-0.005186],[-2.073e-07,0.003636,-0.005237],[-1.84e-07,0.003745,-0.005256] ]

    fcs = [
      [19,2,6],[1,2,19],[20,6,2],[20,2,3],[52,6,20],[52,56,6],[19,6,53],[53,6,56],[95,56,94],[53,56,95],[96,94,56],
      [96,56,52],[178,94,96],[178,177,94],[95,94,176],[176,94,177],[1,177,2],[176,177,1],[3,2,177],[3,177,178],
      [97,130,219],[219,130,184],[98,97,218],[218,97,219],[99,98,217],[217,98,218],[100,99,216],[216,99,217],
      [101,100,215],[215,100,216],[102,101,214],[214,101,215],[103,102,213],[213,102,214],[104,103,212],[212,103,213],
      [105,104,211],[211,104,212],[106,211,210],[106,105,211],[107,210,209],[107,106,210],[108,209,208],[108,107,209],
      [109,208,207],[109,108,208],[110,207,206],[110,109,207],[111,206,205],[111,110,206],[112,205,204],[112,111,205],
      [113,204,203],[113,112,204],[114,203,202],[114,113,203],[115,202,201],[115,114,202],[116,201,200],[116,115,201],
      [117,200,199],[117,116,200],[118,199,198],[118,117,199],[119,198,197],[119,118,198],[120,197,196],[120,119,197],
      [121,196,195],[121,120,196],[122,195,194],[122,121,195],[181,194,193],[181,122,194],[180,193,5],[180,181,193],
      [179,5,4],[179,180,5],[178,4,3],[178,179,4],[175,1,0],[175,176,1],[174,175,192],[192,175,0],[123,174,191],
      [191,174,192],[124,123,190],[190,123,191],[125,124,189],[189,124,190],[126,189,188],[126,125,189],[127,188,187],
      [127,126,188],[128,187,186],[128,127,187],[129,186,185],[129,128,186],[131,129,183],[183,129,185],[132,182,184],
      [132,184,130],[132,131,182],[182,131,183],[173,172,132],[132,172,131],[173,132,130],[173,130,133],[172,171,131],
      [131,171,129],[171,128,129],[171,170,128],[170,127,128],[170,169,127],[169,126,127],[169,168,126],[168,125,126],
      [168,167,125],[167,166,125],[125,166,124],[166,165,124],[124,165,123],[165,164,123],[123,164,174],[164,163,174],
      [174,163,175],[163,95,175],[175,95,176],[96,179,178],[96,162,179],[162,180,179],[162,161,180],[161,181,180],
      [161,160,181],[160,122,181],[160,159,122],[159,121,122],[159,158,121],[158,120,121],[158,157,120],[157,119,120],
      [157,156,119],[156,118,119],[156,155,118],[155,117,118],[155,154,117],[154,116,117],[154,153,116],[153,115,116],
      [153,152,115],[152,114,115],[152,151,114],[151,113,114],[151,150,113],[150,112,113],[150,149,112],[149,111,112],
      [149,148,111],[148,110,111],[148,147,110],[147,109,110],[147,146,109],[146,108,109],[146,145,108],[145,107,108],
      [145,144,107],[144,106,107],[144,143,106],[143,105,106],[143,142,105],[142,141,105],[105,141,104],[141,140,104],
      [104,140,103],[140,139,103],[103,139,102],[139,138,102],[102,138,101],[138,137,101],[101,137,100],[137,136,100],
      [100,136,99],[136,135,99],[99,135,98],[135,134,98],[98,134,97],[134,133,97],[97,133,130],[92,133,134],
      [92,93,133],[91,92,135],[135,92,134],[90,135,136],[90,91,135],[89,136,137],[89,90,136],[88,137,138],[88,89,137],
      [87,138,139],[87,88,138],[86,139,140],[86,87,139],[85,140,141],[85,86,140],[84,141,142],[84,85,141],[83,142,143],
      [83,84,142],[82,143,144],[82,83,143],[81,144,145],[81,82,144],[80,145,146],[80,81,145],[79,146,147],[79,80,146],
      [78,147,148],[78,79,147],[77,148,149],[77,78,148],[76,149,150],[76,77,149],[75,150,151],[75,76,150],[74,151,152],
      [74,75,151],[73,152,153],[73,74,152],[72,153,154],[72,73,153],[71,154,155],[71,72,154],[70,155,156],[70,71,155],
      [69,156,157],[69,70,156],[68,157,158],[68,69,157],[67,158,159],[67,68,158],[66,67,160],[160,67,159],[50,160,161],
      [50,66,160],[51,161,162],[51,50,161],[52,162,96],[52,51,162],[54,53,163],[163,53,95],[55,54,164],[164,54,163],
      [65,55,165],[165,55,164],[64,165,166],[64,65,165],[63,166,167],[63,64,166],[62,167,168],[62,63,167],[61,168,169],
      [61,62,168],[60,169,170],[60,61,169],[59,170,171],[59,60,170],[58,171,172],[58,59,171],[57,173,133],[57,133,93],
      [57,58,173],[173,58,172],[7,8,57],[57,8,58],[7,57,93],[7,93,9],[8,10,58],[58,10,59],[10,60,59],[10,11,60],
      [11,61,60],[11,12,61],[12,62,61],[12,13,62],[13,63,62],[13,14,63],[14,15,63],[63,15,64],[15,16,64],[64,16,65],
      [16,17,65],[65,17,55],[17,18,55],[55,18,54],[18,19,54],[54,19,53],[20,51,52],[20,21,51],[21,50,51],[21,22,50],
      [22,66,50],[22,23,66],[23,67,66],[23,24,67],[24,68,67],[24,25,68],[25,69,68],[25,26,69],[26,70,69],[26,27,70],
      [27,71,70],[27,28,71],[28,72,71],[28,29,72],[29,73,72],[29,30,73],[30,74,73],[30,31,74],[31,75,74],[31,32,75],
      [32,76,75],[32,33,76],[33,77,76],[33,34,77],[34,78,77],[34,35,78],[35,79,78],[35,36,79],[36,80,79],[36,37,80],
      [37,81,80],[37,38,81],[38,82,81],[38,39,82],[39,83,82],[39,40,83],[40,84,83],[40,41,84],[41,42,84],[84,42,85],
      [42,43,85],[85,43,86],[43,44,86],[86,44,87],[44,45,87],[87,45,88],[45,46,88],[88,46,89],[46,47,89],[89,47,90],
      [47,48,90],[90,48,91],[48,49,91],[91,49,92],[49,9,92],[92,9,93],[219,184,49],[49,184,9],[218,219,48],
      [48,219,49],[217,218,47],[47,218,48],[216,217,46],[46,217,47],[215,216,45],[45,216,46],[214,215,44],[44,215,45],
      [213,214,43],[43,214,44],[212,213,42],[42,213,43],[211,212,41],[41,212,42],[210,41,40],[210,211,41],[209,40,39],
      [209,210,40],[208,39,38],[208,209,39],[207,38,37],[207,208,38],[206,37,36],[206,207,37],[205,36,35],[205,206,36],
      [204,35,34],[204,205,35],[203,34,33],[203,204,34],[202,33,32],[202,203,33],[201,32,31],[201,202,32],[200,31,30],
      [200,201,31],[199,30,29],[199,200,30],[198,29,28],[198,199,29],[197,28,27],[197,198,28],[196,27,26],[196,197,27],
      [195,26,25],[195,196,26],[194,25,24],[194,195,25],[193,24,23],[193,194,24],[5,23,22],[5,193,23],[4,22,21],
      [4,5,22],[3,21,20],[3,4,21],[0,1,18],[18,1,19],[17,192,0],[18,17,0],[191,192,16],[16,192,17],[190,191,15],
      [15,191,16],[189,190,14],[14,190,15],[188,14,13],[188,189,14],[187,13,12],[187,188,13],[186,12,11],[186,187,12],
      [185,11,10],[185,186,11],[183,185,8],[8,185,10],[182,7,9],[182,9,184],[182,183,7],[7,183,8] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class Letter_A (plf_object):

  def __init__  ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):
    size_scale = 0.15
    pts = [
      [0.03136,0.4235,-0.075],[-0.03764,0.4235,-0.075],[-0.3306,-0.2625,-0.075],[-0.2306,-0.2625,-0.075],[-0.1446,-0.06155,-0.075],
      [0.1454,-0.06155,-0.075],[0.2364,-0.2625,-0.075],[0.3364,-0.2625,-0.075],[-0.004636,0.2735,-0.075],[0.1054,0.02645,-0.075],
      [-0.1066,0.02645,-0.075],[0.03136,0.4235,0.075],[-0.03764,0.4235,0.075],[-0.3306,-0.2625,0.075],[-0.2306,-0.2625,0.075],
      [-0.1446,-0.06155,0.075],[0.1454,-0.06155,0.075],[0.2364,-0.2625,0.075],[0.3364,-0.2625,0.075],[-0.004636,0.2735,0.075],
      [0.1054,0.02645,0.075],[-0.1066,0.02645,0.075] ]

    fcs = [
      [2,1,0],[2,0,8],[8,0,7],[2,8,10],[9,8,7],[2,10,4],[4,10,9],[4,9,5],[5,9,7],[2,4,3],[6,5,7],[13,11,12],
      [13,19,11],[19,18,11],[13,21,19],[20,18,19],[13,15,21],[15,20,21],[15,16,20],[16,18,20],[13,14,15],
      [17,18,16],[10,21,20],[2,13,12],[1,12,11],[8,19,21],[5,16,15],[6,17,16],[9,20,19],[7,18,17],[3,14,13],
      [4,15,14],[0,11,18],[9,10,20],[1,2,12],[0,1,11],[10,8,21],[4,5,15],[5,6,16],[8,9,19],[6,7,17],[2,3,13],
      [3,4,14],[7,0,18] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*p[2] ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class Letter_B (plf_object):

  def __init__  ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):
    size_scale = 0.15
    pts = [
      [-0.2006,-0.3332,0],[0.03337,-0.3332,0],[0.0739,-0.3312,0],[0.1101,-0.3255,0],[0.1421,-0.3166,0],[0.17,-0.3047,0],
      [0.1941,-0.2903,0],[0.2145,-0.2737,0],[0.2313,-0.2554,0],[0.2447,-0.2357,0],[0.2549,-0.2151,0],[0.2619,-0.1938,0],
      [0.266,-0.1724,0],[0.2674,-0.1512,0],[0.2661,-0.1287,0],[0.2623,-0.1074,0],[0.2561,-0.08724,0],[0.2475,-0.06838,0],
      [0.2367,-0.05087,0],[0.2236,-0.03481,0],[0.2084,-0.02028,0],[0.1912,-0.007338,0],[0.172,0.003919,0],[0.1509,0.01342,0],
      [0.128,0.02107,0],[0.1034,0.02681,0],[0.1034,0.02881,0],[0.1203,0.03642,0],[0.1357,0.04476,0],[0.1496,0.05387,0],
      [0.1619,0.06377,0],[0.1727,0.07449,0],[0.182,0.08606,0],[0.1898,0.0985,0],[0.1962,0.1118,0],[0.2011,0.1261,0],
      [0.2046,0.1414,0],[0.2067,0.1576,0],[0.2074,0.1748,0],[0.206,0.1963,0],[0.202,0.2176,0],[0.1952,0.2383,0],
      [0.1856,0.2581,0],[0.173,0.2768,0],[0.1575,0.2941,0],[0.1389,0.3095,0],[0.1172,0.3228,0],[0.0922,0.3337,0],
      [0.06397,0.3419,0],[0.03239,0.347,0],[-0.002625,0.3488,0],[-0.2006,0.3488,0],[-0.1026,0.2608,0],[-0.01263,0.2608,0],
      [0.008622,0.2599,0],[0.02744,0.2573,0],[0.04394,0.2531,0],[0.05823,0.2475,0],[0.07042,0.2406,0],[0.08062,0.2324,0],
      [0.08896,0.2232,0],[0.09552,0.2131,0],[0.1004,0.2022,0],[0.1038,0.1906,0],[0.1058,0.1784,0],[0.1064,0.1658,0],
      [0.1054,0.1483,0],[0.1024,0.1324,0],[0.09752,0.118,0],[0.0906,0.1051,0],[0.08168,0.09376,0],[0.07075,0.08394,0],
      [0.0578,0.07563,0],[0.04282,0.06885,0],[0.0258,0.06358,0],[0.006722,0.05981,0],[-0.01442,0.05756,0],[-0.03763,0.05681,0],
      [-0.1026,0.05681,0],[-0.1026,-0.03119,0],[0.01537,-0.03119,0],[0.03998,-0.03209,0],[0.06232,-0.03474,0],
      [0.08242,-0.03903,0],[0.1003,-0.04489,0],[0.116,-0.05223,0],[0.1295,-0.06094,0],[0.1409,-0.07095,0],[0.1501,-0.08215,0],
      [0.1573,-0.09447,0],[0.1623,-0.1078,0],[0.1654,-0.1221,0],[0.1664,-0.1372,0],[0.1657,-0.15,0],[0.1635,-0.1629,0],
      [0.1597,-0.1756,0],[0.1541,-0.1879,0],[0.1464,-0.1995,0],[0.1365,-0.2103,0],[0.1242,-0.2201,0],[0.1093,-0.2285,0],
      [0.0917,-0.2355,0],[0.07112,-0.2407,0],[0.04741,-0.244,0],[0.02037,-0.2452,0],[-0.1026,-0.2452,0],[-0.2006,-0.3332,0.15],
      [0.03337,-0.3332,0.15],[0.0739,-0.3312,0.15],[0.1101,-0.3255,0.15],[0.1421,-0.3166,0.15],[0.17,-0.3047,0.15],
      [0.1941,-0.2903,0.15],[0.2145,-0.2737,0.15],[0.2313,-0.2554,0.15],[0.2447,-0.2357,0.15],[0.2549,-0.2151,0.15],
      [0.2619,-0.1938,0.15],[0.266,-0.1724,0.15],[0.2674,-0.1512,0.15],[0.2661,-0.1287,0.15],[0.2623,-0.1074,0.15],
      [0.2561,-0.08724,0.15],[0.2475,-0.06838,0.15],[0.2367,-0.05087,0.15],[0.2236,-0.03481,0.15],[0.2084,-0.02028,0.15],
      [0.1912,-0.007338,0.15],[0.172,0.003919,0.15],[0.1509,0.01342,0.15],[0.128,0.02107,0.15],[0.1034,0.02681,0.15],
      [0.1034,0.02881,0.15],[0.1203,0.03642,0.15],[0.1357,0.04476,0.15],[0.1496,0.05387,0.15],[0.1619,0.06377,0.15],
      [0.1727,0.07449,0.15],[0.182,0.08606,0.15],[0.1898,0.0985,0.15],[0.1962,0.1118,0.15],[0.2011,0.1261,0.15],
      [0.2046,0.1414,0.15],[0.2067,0.1576,0.15],[0.2074,0.1748,0.15],[0.206,0.1963,0.15],[0.202,0.2176,0.15],
      [0.1952,0.2383,0.15],[0.1856,0.2581,0.15],[0.173,0.2768,0.15],[0.1575,0.2941,0.15],[0.1389,0.3095,0.15],
      [0.1172,0.3228,0.15],[0.0922,0.3337,0.15],[0.06397,0.3419,0.15],[0.03239,0.347,0.15],[-0.002625,0.3488,0.15],
      [-0.2006,0.3488,0.15],[-0.1026,0.2608,0.15],[-0.01263,0.2608,0.15],[0.008622,0.2599,0.15],[0.02744,0.2573,0.15],
      [0.04394,0.2531,0.15],[0.05823,0.2475,0.15],[0.07042,0.2406,0.15],[0.08062,0.2324,0.15],[0.08896,0.2232,0.15],
      [0.09552,0.2131,0.15],[0.1004,0.2022,0.15],[0.1038,0.1906,0.15],[0.1058,0.1784,0.15],[0.1064,0.1658,0.15],
      [0.1054,0.1483,0.15],[0.1024,0.1324,0.15],[0.09752,0.118,0.15],[0.0906,0.1051,0.15],[0.08168,0.09376,0.15],
      [0.07075,0.08394,0.15],[0.0578,0.07563,0.15],[0.04282,0.06885,0.15],[0.0258,0.06358,0.15],[0.006722,0.05981,0.15],
      [-0.01442,0.05756,0.15],[-0.03763,0.05681,0.15],[-0.1026,0.05681,0.15],[-0.1026,-0.03119,0.15],[0.01537,-0.03119,0.15],
      [0.03998,-0.03209,0.15],[0.06232,-0.03474,0.15],[0.08242,-0.03903,0.15],[0.1003,-0.04489,0.15],[0.116,-0.05223,0.15],
      [0.1295,-0.06094,0.15],[0.1409,-0.07095,0.15],[0.1501,-0.08215,0.15],[0.1573,-0.09447,0.15],[0.1623,-0.1078,0.15],
      [0.1654,-0.1221,0.15],[0.1664,-0.1372,0.15],[0.1657,-0.15,0.15],[0.1635,-0.1629,0.15],[0.1597,-0.1756,0.15],
      [0.1541,-0.1879,0.15],[0.1464,-0.1995,0.15],[0.1365,-0.2103,0.15],[0.1242,-0.2201,0.15],[0.1093,-0.2285,0.15],
      [0.0917,-0.2355,0.15],[0.07112,-0.2407,0.15],[0.04741,-0.244,0.15],[0.02037,-0.2452,0.15],[-0.1026,-0.2452,0.15] ]

    fcs = [
      [0,51,52],[52,51,50],[52,50,49],[52,49,48],[52,48,47],[52,47,46],[52,46,45],[52,45,44],[52,44,43],[52,43,53],
      [53,43,42],[0,52,78],[54,53,42],[55,54,42],[55,42,41],[56,55,41],[57,56,41],[58,57,41],[59,58,41],[59,41,40],
      [60,59,40],[61,60,40],[61,40,39],[62,61,39],[63,62,39],[63,39,38],[64,63,38],[65,64,38],[65,38,37],[66,65,37],
      [66,37,36],[67,66,36],[67,36,35],[68,67,35],[68,35,34],[69,68,34],[69,34,33],[70,69,33],[70,33,32],[71,70,32],
      [71,32,31],[72,71,31],[73,72,31],[73,31,30],[74,73,30],[74,30,29],[75,74,29],[76,75,29],[77,76,29],[0,78,79],
      [79,78,77],[79,77,29],[79,29,28],[79,28,27],[79,27,26],[79,26,25],[79,25,24],[79,24,23],[79,23,22],[79,22,21],
      [79,21,20],[79,20,80],[80,20,19],[0,79,105],[81,80,19],[82,81,19],[83,82,19],[83,19,18],[84,83,18],[85,84,18],
      [85,18,17],[86,85,17],[87,86,17],[87,17,16],[88,87,16],[89,88,16],[89,16,15],[90,89,15],[90,15,14],[91,90,14],
      [92,91,14],[92,14,13],[93,92,13],[94,93,13],[94,13,12],[95,94,12],[95,12,11],[96,95,11],[97,96,11],[97,11,10],
      [98,97,10],[99,98,10],[99,10,9],[100,99,9],[101,100,9],[102,101,9],[102,9,8],[103,102,8],[104,103,8],
      [0,105,104],[0,104,8],[0,8,7],[0,7,6],[0,6,5],[0,5,4],[0,4,3],[0,3,2],[0,2,1],[106,158,157],[158,156,157],
      [158,155,156],[158,154,155],[158,153,154],[158,152,153],[158,151,152],[158,150,151],[158,149,150],[158,159,149],
      [159,148,149],[106,184,158],[160,148,159],[161,148,160],[161,147,148],[162,147,161],[163,147,162],[164,147,163],
      [165,147,164],[165,146,147],[166,146,165],[167,146,166],[167,145,146],[168,145,167],[169,145,168],[169,144,145],
      [170,144,169],[171,144,170],[171,143,144],[172,143,171],[172,142,143],[173,142,172],[173,141,142],[174,141,173],
      [174,140,141],[175,140,174],[175,139,140],[176,139,175],[176,138,139],[177,138,176],[177,137,138],[178,137,177],
      [179,137,178],[179,136,137],[180,136,179],[180,135,136],[181,135,180],[182,135,181],[183,135,182],[106,185,184],
      [185,183,184],[185,135,183],[185,134,135],[185,133,134],[185,132,133],[185,131,132],[185,130,131],[185,129,130],
      [185,128,129],[185,127,128],[185,126,127],[185,186,126],[186,125,126],[106,211,185],[187,125,186],[188,125,187],
      [189,125,188],[189,124,125],[190,124,189],[191,124,190],[191,123,124],[192,123,191],[193,123,192],[193,122,123],
      [194,122,193],[195,122,194],[195,121,122],[196,121,195],[196,120,121],[197,120,196],[198,120,197],[198,119,120],
      [199,119,198],[200,119,199],[200,118,119],[201,118,200],[201,117,118],[202,117,201],[203,117,202],[203,116,117],
      [204,116,203],[205,116,204],[205,115,116],[206,115,205],[207,115,206],[208,115,207],[208,114,115],[209,114,208],
      [210,114,209],[106,210,211],[106,114,210],[106,113,114],[106,112,113],[106,111,112],[106,110,111],[106,109,110],
      [106,108,109],[106,107,108],[35,141,140],[95,201,200],[36,142,141],[20,126,125],[7,113,112],[92,198,197],
      [54,160,159],[66,172,171],[33,139,138],[90,196,195],[104,210,209],[4,110,109],[105,211,210],[89,195,194],
      [53,159,158],[18,124,123],[75,181,180],[28,134,133],[3,109,108],[93,199,198],[1,107,106],[17,123,122],
      [103,209,208],[27,133,132],[2,108,107],[72,178,177],[56,162,161],[55,161,160],[42,148,147],[25,131,130],
      [102,208,207],[76,182,181],[26,132,131],[49,155,154],[78,184,183],[32,138,137],[51,157,156],[87,193,192],
      [101,207,206],[73,179,178],[50,156,155],[79,185,211],[100,206,205],[46,152,151],[30,136,135],[29,135,134],
      [44,150,149],[77,183,182],[86,192,191],[12,118,117],[74,180,179],[60,166,165],[43,149,148],[83,189,188],
      [68,174,173],[70,176,175],[84,190,189],[57,163,162],[59,165,164],[41,147,146],[31,137,136],[38,144,143],
      [0,106,157],[52,158,184],[45,151,150],[85,191,190],[69,175,174],[58,164,163],[61,167,166],[10,116,115],
      [9,115,114],[11,117,116],[99,205,204],[97,203,202],[98,204,203],[71,177,176],[91,197,196],[48,154,153],
      [62,168,167],[64,170,169],[96,202,201],[13,119,118],[47,153,152],[16,122,121],[14,120,119],[80,186,185],
      [67,173,172],[37,143,142],[63,169,168],[23,129,128],[22,128,127],[81,187,186],[15,121,120],[40,146,145],
      [82,188,187],[39,145,144],[34,140,139],[21,127,126],[24,130,129],[19,125,124],[6,112,111],[65,171,170],
      [8,114,113],[5,111,110],[88,194,193],[94,200,199],[34,35,140],[94,95,200],[35,36,141],[19,20,125],[6,7,112],
      [91,92,197],[53,54,159],[65,66,171],[32,33,138],[89,90,195],[103,104,209],[3,4,109],[104,105,210],[88,89,194],
      [52,53,158],[17,18,123],[74,75,180],[27,28,133],[2,3,108],[92,93,198],[0,1,106],[16,17,122],[102,103,208],
      [26,27,132],[1,2,107],[71,72,177],[55,56,161],[54,55,160],[41,42,147],[24,25,130],[101,102,207],[75,76,181],
      [25,26,131],[48,49,154],[77,78,183],[31,32,137],[50,51,156],[86,87,192],[100,101,206],[72,73,178],[49,50,155],
      [105,79,211],[99,100,205],[45,46,151],[29,30,135],[28,29,134],[43,44,149],[76,77,182],[85,86,191],[11,12,117],
      [73,74,179],[59,60,165],[42,43,148],[82,83,188],[67,68,173],[69,70,175],[83,84,189],[56,57,162],[58,59,164],
      [40,41,146],[30,31,136],[37,38,143],[51,0,157],[78,52,184],[44,45,150],[84,85,190],[68,69,174],[57,58,163],
      [60,61,166],[9,10,115],[8,9,114],[10,11,116],[98,99,204],[96,97,202],[97,98,203],[70,71,176],[90,91,196],
      [47,48,153],[61,62,167],[63,64,169],[95,96,201],[12,13,118],[46,47,152],[15,16,121],[13,14,119],[79,80,185],
      [66,67,172],[36,37,142],[62,63,168],[22,23,128],[21,22,127],[80,81,186],[14,15,120],[39,40,145],[81,82,187],
      [38,39,144],[33,34,139],[20,21,126],[23,24,129],[18,19,124],[5,6,111],[64,65,170],[7,8,113],[4,5,110],
      [87,88,193],[93,94,199] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*(p[2]-0.075) ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class Letter_C (plf_object):

  def __init__  ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):
    size_scale = 0.15
    pts = [
      [0.2744,0.2927,0],[0.2516,0.302,0],[0.2297,0.3104,0],[0.2085,0.3179,0],[0.188,0.3246,0],[0.1681,0.3304,0],
      [0.1488,0.3353,0],[0.13,0.3395,0],[0.1116,0.3429,0],[0.09346,0.3454,0],[0.07563,0.3473,0],[0.05798,0.3484,0],
      [0.04045,0.3487,0],[-0.0125,0.3456,0],[-0.0626,0.3365,0],[-0.1095,0.3217,0],[-0.153,0.3016,0],[-0.1925,0.2765,0],
      [-0.2279,0.2467,0],[-0.2588,0.2126,0],[-0.2848,0.1745,0],[-0.3056,0.1327,0],[-0.3209,0.0876,0],[-0.3303,0.03949,0],
      [-0.3336,-0.01129,0],[-0.3312,-0.04802,0],[-0.3241,-0.08613,0],[-0.3121,-0.1247,0],[-0.295,-0.163,0],
      [-0.2729,-0.2,0],[-0.2456,-0.2349,0],[-0.2129,-0.2668,0],[-0.1747,-0.2949,0],[-0.1311,-0.3183,0],[-0.0817,-0.336,0],
      [-0.02657,-0.3473,0],[0.03445,-0.3513,0],[0.0605,-0.3508,0],[0.08524,-0.3493,0],[0.1088,-0.3468,0],[0.1311,-0.3435,0],
      [0.1525,-0.3394,0],[0.1729,-0.3344,0],[0.1925,-0.3287,0],[0.2114,-0.3224,0],[0.2296,-0.3154,0],[0.2473,-0.3079,0],
      [0.2646,-0.2998,0],[0.2814,-0.2913,0],[0.2814,-0.1843,0],[0.2621,-0.1963,0],[0.2424,-0.2074,0],[0.2226,-0.2174,0],
      [0.2026,-0.2265,0],[0.1826,-0.2345,0],[0.1624,-0.2415,0],[0.1423,-0.2475,0],[0.1223,-0.2524,0],[0.1023,-0.2563,0],
      [0.08246,-0.2591,0],[0.06283,-0.2607,0],[0.04345,-0.2613,0],[0.003564,-0.2591,0],[-0.03394,-0.2527,0],
      [-0.06887,-0.2423,0],[-0.101,-0.2281,0],[-0.1301,-0.2104,0],[-0.1561,-0.1892,0],[-0.1786,-0.1648,0],[-0.1974,-0.1374,0],
      [-0.2125,-0.1073,0],[-0.2235,-0.0746,0],[-0.2303,-0.03953,0],[-0.2326,-0.002292,0],[-0.2302,0.03435,0],
      [-0.2232,0.06912,0],[-0.212,0.1018,0],[-0.1967,0.132,0],[-0.1776,0.1597,0],[-0.1551,0.1845,0],[-0.1292,0.2061,0],
      [-0.1004,0.2244,0],[-0.06887,0.239,0],[-0.03487,0.2498,0],[0.001324,0.2564,0],[0.03945,0.2587,0],[0.05906,0.2582,0],
      [0.07845,0.2569,0],[0.09768,0.2545,0],[0.1168,0.2512,0],[0.1359,0.2469,0],[0.1551,0.2416,0],[0.1743,0.2353,0],
      [0.1937,0.2279,0],[0.2134,0.2195,0],[0.2334,0.21,0],[0.2537,0.1994,0],[0.2744,0.1877,0],[0.2744,0.2927,0.15],
      [0.2516,0.302,0.15],[0.2297,0.3104,0.15],[0.2085,0.3179,0.15],[0.188,0.3246,0.15],[0.1681,0.3304,0.15],
      [0.1488,0.3353,0.15],[0.13,0.3395,0.15],[0.1116,0.3429,0.15],[0.09346,0.3454,0.15],[0.07563,0.3473,0.15],
      [0.05798,0.3484,0.15],[0.04045,0.3487,0.15],[-0.0125,0.3456,0.15],[-0.0626,0.3365,0.15],[-0.1095,0.3217,0.15],
      [-0.153,0.3016,0.15],[-0.1925,0.2765,0.15],[-0.2279,0.2467,0.15],[-0.2588,0.2126,0.15],[-0.2848,0.1745,0.15],
      [-0.3056,0.1327,0.15],[-0.3209,0.0876,0.15],[-0.3303,0.03949,0.15],[-0.3336,-0.01129,0.15],[-0.3312,-0.04802,0.15],
      [-0.3241,-0.08613,0.15],[-0.3121,-0.1247,0.15],[-0.295,-0.163,0.15],[-0.2729,-0.2,0.15],[-0.2456,-0.2349,0.15],
      [-0.2129,-0.2668,0.15],[-0.1747,-0.2949,0.15],[-0.1311,-0.3183,0.15],[-0.0817,-0.336,0.15],[-0.02657,-0.3473,0.15],
      [0.03445,-0.3513,0.15],[0.0605,-0.3508,0.15],[0.08524,-0.3493,0.15],[0.1088,-0.3468,0.15],[0.1311,-0.3435,0.15],
      [0.1525,-0.3394,0.15],[0.1729,-0.3344,0.15],[0.1925,-0.3287,0.15],[0.2114,-0.3224,0.15],[0.2296,-0.3154,0.15],
      [0.2473,-0.3079,0.15],[0.2646,-0.2998,0.15],[0.2814,-0.2913,0.15],[0.2814,-0.1843,0.15],[0.2621,-0.1963,0.15],
      [0.2424,-0.2074,0.15],[0.2226,-0.2174,0.15],[0.2026,-0.2265,0.15],[0.1826,-0.2345,0.15],[0.1624,-0.2415,0.15],
      [0.1423,-0.2475,0.15],[0.1223,-0.2524,0.15],[0.1023,-0.2563,0.15],[0.08246,-0.2591,0.15],[0.06283,-0.2607,0.15],
      [0.04345,-0.2613,0.15],[0.003564,-0.2591,0.15],[-0.03394,-0.2527,0.15],[-0.06887,-0.2423,0.15],[-0.101,-0.2281,0.15],
      [-0.1301,-0.2104,0.15],[-0.1561,-0.1892,0.15],[-0.1786,-0.1648,0.15],[-0.1974,-0.1374,0.15],[-0.2125,-0.1073,0.15],
      [-0.2235,-0.0746,0.15],[-0.2303,-0.03953,0.15],[-0.2326,-0.002292,0.15],[-0.2302,0.03435,0.15],[-0.2232,0.06912,0.15],
      [-0.212,0.1018,0.15],[-0.1967,0.132,0.15],[-0.1776,0.1597,0.15],[-0.1551,0.1845,0.15],[-0.1292,0.2061,0.15],
      [-0.1004,0.2244,0.15],[-0.06887,0.239,0.15],[-0.03487,0.2498,0.15],[0.001324,0.2564,0.15],[0.03945,0.2587,0.15],
      [0.05906,0.2582,0.15],[0.07845,0.2569,0.15],[0.09768,0.2545,0.15],[0.1168,0.2512,0.15],[0.1359,0.2469,0.15],
      [0.1551,0.2416,0.15],[0.1743,0.2353,0.15],[0.1937,0.2279,0.15],[0.2134,0.2195,0.15],[0.2334,0.21,0.15],
      [0.2537,0.1994,0.15],[0.2744,0.1877,0.15] ]

    fcs = [
      [13,12,11],[13,11,10],[13,10,9],[14,13,9],[14,9,8],[14,8,7],[14,7,6],[15,14,6],[15,6,5],[15,5,4],[15,4,3],
      [16,15,3],[16,3,2],[16,2,1],[16,1,0],[17,16,0],[17,0,87],[87,0,88],[88,0,89],[89,0,90],[90,0,91],[91,0,92],
      [92,0,93],[93,0,94],[94,0,95],[95,0,96],[96,0,97],[18,17,85],[85,17,86],[86,17,87],[18,85,84],[18,84,83],
      [18,83,82],[19,18,82],[19,82,81],[19,81,80],[20,19,80],[20,80,79],[20,79,78],[21,20,78],[21,78,77],[22,21,77],
      [22,77,76],[22,76,75],[23,22,75],[23,75,74],[24,23,74],[24,74,73],[24,73,72],[25,24,72],[25,72,71],[26,25,71],
      [26,71,70],[27,26,70],[27,70,69],[28,27,69],[28,69,68],[29,28,68],[29,68,67],[50,49,48],[29,67,66],[51,50,48],
      [30,29,66],[52,51,48],[30,66,65],[53,52,48],[54,53,48],[30,65,64],[55,54,48],[31,30,64],[56,55,48],[31,64,63],
      [57,56,48],[58,57,48],[31,63,62],[59,58,48],[60,59,48],[31,62,61],[61,60,48],[31,61,48],[32,31,48],[32,48,47],
      [33,32,47],[33,47,46],[33,46,45],[33,45,44],[34,33,44],[34,44,43],[34,43,42],[34,42,41],[35,34,41],[35,41,40],
      [35,40,39],[35,39,38],[36,35,38],[36,38,37],[111,109,110],[111,108,109],[111,107,108],[112,107,111],[112,106,107],
      [112,105,106],[112,104,105],[113,104,112],[113,103,104],[113,102,103],[113,101,102],[114,101,113],[114,100,101],
      [114,99,100],[114,98,99],[115,98,114],[115,185,98],[185,186,98],[186,187,98],[187,188,98],[188,189,98],
      [189,190,98],[190,191,98],[191,192,98],[192,193,98],[193,194,98],[194,195,98],[116,183,115],[183,184,115],
      [184,185,115],[116,182,183],[116,181,182],[116,180,181],[117,180,116],[117,179,180],[117,178,179],[118,178,117],
      [118,177,178],[118,176,177],[119,176,118],[119,175,176],[120,175,119],[120,174,175],[120,173,174],[121,173,120],
      [121,172,173],[122,172,121],[122,171,172],[122,170,171],[123,170,122],[123,169,170],[124,169,123],[124,168,169],
      [125,168,124],[125,167,168],[126,167,125],[126,166,167],[127,166,126],[127,165,166],[148,146,147],[127,164,165],
      [149,146,148],[128,164,127],[150,146,149],[128,163,164],[151,146,150],[152,146,151],[128,162,163],[153,146,152],
      [129,162,128],[154,146,153],[129,161,162],[155,146,154],[156,146,155],[129,160,161],[157,146,156],[158,146,157],
      [129,159,160],[159,146,158],[129,146,159],[130,146,129],[130,145,146],[131,145,130],[131,144,145],[131,143,144],
      [131,142,143],[132,142,131],[132,141,142],[132,140,141],[132,139,140],[133,139,132],[133,138,139],[133,137,138],
      [133,136,137],[134,136,133],[134,135,136],[81,179,178],[34,132,131],[26,124,123],[25,123,122],[48,146,145],
      [47,145,144],[88,186,185],[13,111,110],[28,126,125],[63,161,160],[51,149,148],[83,181,180],[12,110,109],
      [67,165,164],[27,125,124],[70,168,167],[4,102,101],[72,170,169],[59,157,156],[56,154,153],[5,103,102],
      [53,151,150],[3,101,100],[42,140,139],[79,177,176],[16,114,113],[96,194,193],[61,159,158],[87,185,184],
      [8,106,105],[52,150,149],[40,138,137],[93,191,190],[15,113,112],[6,104,103],[14,112,111],[69,167,166],
      [35,133,132],[66,164,163],[37,135,134],[33,131,130],[32,130,129],[20,118,117],[30,128,127],[60,158,157],
      [68,166,165],[89,187,186],[0,98,195],[74,172,171],[29,127,126],[1,99,98],[10,108,107],[90,188,187],[7,105,104],
      [50,148,147],[80,178,177],[62,160,159],[57,155,154],[43,141,140],[38,136,135],[94,192,191],[24,122,121],
      [2,100,99],[65,163,162],[11,109,108],[21,119,118],[36,134,133],[55,153,152],[45,143,142],[19,117,116],
      [39,137,136],[31,129,128],[75,173,172],[86,184,183],[82,180,179],[84,182,181],[85,183,182],[77,175,174],
      [91,189,188],[49,147,146],[17,115,114],[41,139,138],[73,171,170],[64,162,161],[97,195,194],[18,116,115],
      [78,176,175],[92,190,189],[95,193,192],[9,107,106],[58,156,155],[44,142,141],[76,174,173],[54,152,151],
      [22,120,119],[71,169,168],[46,144,143],[23,121,120],[80,81,178],[33,34,131],[25,26,123],[24,25,122],[47,48,145],
      [46,47,144],[87,88,185],[12,13,110],[27,28,125],[62,63,160],[50,51,148],[82,83,180],[11,12,109],[66,67,164],
      [26,27,124],[69,70,167],[3,4,101],[71,72,169],[58,59,156],[55,56,153],[4,5,102],[52,53,150],[2,3,100],
      [41,42,139],[78,79,176],[15,16,113],[95,96,193],[60,61,158],[86,87,184],[7,8,105],[51,52,149],[39,40,137],
      [92,93,190],[14,15,112],[5,6,103],[13,14,111],[68,69,166],[34,35,132],[65,66,163],[36,37,134],[32,33,130],
      [31,32,129],[19,20,117],[29,30,127],[59,60,157],[67,68,165],[88,89,186],[97,0,195],[73,74,171],[28,29,126],
      [0,1,98],[9,10,107],[89,90,187],[6,7,104],[49,50,147],[79,80,177],[61,62,159],[56,57,154],[42,43,140],
      [37,38,135],[93,94,191],[23,24,121],[1,2,99],[64,65,162],[10,11,108],[20,21,118],[35,36,133],[54,55,152],
      [44,45,142],[18,19,116],[38,39,136],[30,31,128],[74,75,172],[85,86,183],[81,82,179],[83,84,181],[84,85,182],
      [76,77,174],[90,91,188],[48,49,146],[16,17,114],[40,41,138],[72,73,170],[63,64,161],[96,97,194],[17,18,115],
      [77,78,175],[91,92,189],[94,95,192],[8,9,106],[57,58,155],[43,44,141],[75,76,173],[53,54,151],[21,22,119],
      [70,71,168],[45,46,143],[22,23,120] ]

    self.points = [];
    self.faces = [];
    for p in pts:
      self.points.append ( point ( size_scale*size_x*p[0], size_scale*size_y*p[1], size_scale*size_z*(p[2]-0.075) ) )
    for f in fcs:
      self.faces.append ( face ( f[0], f[1], f[2] ) )



class Tetrahedron (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a tetrahedron of the requested size

    size_scale = 0.05 * 1.5

    self.points = [];
    self.faces = [];

    z = 1 / math.sqrt(2)

    self.points = self.points + [ point (  -1*size_x*size_scale,  0, -z*size_z*size_scale ) ]
    self.points = self.points + [ point (   1*size_x*size_scale,  0, -z*size_z*size_scale ) ]
    self.points = self.points + [ point (  0, -1*size_y*size_scale,   z*size_z*size_scale ) ]
    self.points = self.points + [ point (  0,  1*size_y*size_scale,   z*size_z*size_scale ) ]

    face_list = [ [ 0, 1, 2 ], [ 0, 2, 3 ], [ 0, 3, 1 ], [ 1, 3, 2 ] ]

    for f in face_list:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class Pyramid (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a pyramid of the requested size

    size_scale = 0.05

    self.points = [];
    self.faces = [];

    self.points = self.points + [ point (  size_x*size_scale,  size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point (  size_x*size_scale, -size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point ( -size_x*size_scale, -size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point ( -size_x*size_scale,  size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point (     0.0*size_scale,     0.0*size_scale,  size_z*size_scale ) ]

    face_list = [ [ 1, 2, 3 ], [ 0, 1, 3 ], [ 0, 4, 1 ],
                  [ 1, 4, 2 ], [ 2, 4, 3 ], [ 3, 4, 0 ] ]

    for f in face_list:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class BasicBox (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a box of the requested size

    size_scale = 0.05

    self.points = [];
    self.faces = [];

    self.points = self.points + [ point (  size_x*size_scale,  size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point (  size_x*size_scale, -size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point ( -size_x*size_scale, -size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point ( -size_x*size_scale,  size_y*size_scale, -size_z*size_scale ) ]
    self.points = self.points + [ point (  size_x*size_scale,  size_y*size_scale,  size_z*size_scale ) ]
    self.points = self.points + [ point (  size_x*size_scale, -size_y*size_scale,  size_z*size_scale ) ]
    self.points = self.points + [ point ( -size_x*size_scale, -size_y*size_scale,  size_z*size_scale ) ]
    self.points = self.points + [ point ( -size_x*size_scale,  size_y*size_scale,  size_z*size_scale ) ]

    face_list = [ [ 1, 2, 3 ], [ 7, 6, 5 ], [ 4, 5, 1 ], [ 5, 6, 2 ],
                  [ 2, 6, 7 ], [ 0, 3, 7 ], [ 0, 1, 3 ], [ 4, 7, 5 ],
                  [ 0, 4, 1 ], [ 1, 5, 2 ], [ 3, 2, 7 ], [ 4, 0, 7 ] ]

    for f in face_list:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


def get_named_shape ( glyph_name, size_x=1.0, size_y=1.0, size_z=1.0 ):

    shape_plf = None
    if   "Octahedron" == glyph_name:
        shape_plf = CellBlender_Octahedron  ( size_x, size_y, size_z )
    elif "Cube" == glyph_name:
        shape_plf = CellBlender_Cube ( size_x, size_y, size_z )
    elif "Icosahedron" == glyph_name:
        shape_plf = CellBlender_Icosahedron ( size_x, size_y, size_z )
    elif "Cone" == glyph_name:
        shape_plf = CellBlender_Cone ( size_x, size_y, size_z )
    elif "Cylinder" == glyph_name:
        shape_plf = CellBlender_Cylinder ( size_x, size_y, size_z )
    elif "Torus" == glyph_name:
        shape_plf = CellBlender_Torus ( size_x, size_y, size_z )
    elif "Sphere1" == glyph_name:
        shape_plf = CellBlender_Sphere1 ( size_x, size_y, size_z )
    elif "Sphere2" == glyph_name:
        shape_plf = CellBlender_Sphere2 ( size_x, size_y, size_z )
    elif "Receptor" == glyph_name:
        shape_plf = CellBlender_Receptor ( size_x, size_y, size_z )
    elif "Cube" == glyph_name:
        shape_plf = BasicBox ( size_x, size_y, size_z )
    elif "Pyramid" == glyph_name:
        shape_plf = Pyramid ( size_x, size_y, size_z )
    elif "Tetrahedron" == glyph_name:
        shape_plf = Tetrahedron ( size_x, size_y, size_z )
    elif "A" in glyph_name:
        shape_plf = Letter_A ( size_x, size_y, size_z )
    elif "B" in glyph_name:
        shape_plf = Letter_B ( size_x, size_y, size_z )
    elif "C" in glyph_name:
        shape_plf = Letter_C ( size_x, size_y, size_z )
    else:
        shape_plf = BasicBox ( size_x, size_y, size_z )

    return shape_plf


#### End of Molecule Shape Code #### 



def create_squashed_z_box ( scene, min_len=0.25, max_len=3.5, period_frames=100, frame_num=None ):

    cur_frame = frame_num
    if cur_frame == None:
      cur_frame = scene.frame_current

    size_x = min_len + ( (max_len-min_len) * ( (1 - math.cos ( 2 * math.pi * cur_frame / period_frames )) / 2 ) )
    size_y = min_len + ( (max_len-min_len) * ( (1 - math.cos ( 2 * math.pi * cur_frame / period_frames )) / 2 ) )
    size_z = min_len + ( (max_len-min_len) * ( (1 - math.sin ( 2 * math.pi * cur_frame / period_frames )) / 2 ) )

    return BasicBox ( size_x, size_y, size_z )



fixed_points = []
fixed_index = 0


class MolCluster (plf_object):

  def __init__ ( self, num, dist, center_x, center_y, center_z, seed, method='slow' ):

    # Create a distribution as requested
    
    global fixed_points
    global fixed_index

    if len(fixed_points) <= 0:
        print ( "Generating normal distribution" )
        random.seed ( seed )
        for i in range(100000):
            fixed_points.append ( point ( random.normalvariate(center_x,dist), random.normalvariate(center_y,dist), random.normalvariate(center_z,dist) ) )

    self.points = [];
    self.faces = [];
    
    if method == 'slow':    # Use random number generator (slowest)
        for i in range(num):
            self.points.append ( point ( random.normalvariate(center_x,dist), random.normalvariate(center_y,dist), random.normalvariate(center_z,dist) ) )
    elif method == 'med':  # Use precalculated random points (faster, but repeats points)
        fixed_index = random.randint ( 0, len(fixed_points)-4 )
        for i in range(num):
            if fixed_index >= len(fixed_points):
                fixed_index = random.randint ( 0, len(fixed_points)-1 )
            self.points.append ( fixed_points[fixed_index] )
            fixed_index += 1
    elif method == 'fast':     # Use a single fixed value (fastest, all points are the same!!)
        single_point = point ( center_x, center_y, center_z )
        for i in range(num):
            self.points.append ( single_point )



def generate_letter_object ( letter ):
    # Note that this doesn't work properly. Earlier versions of this code had additional experiments in doing this.
    print ( "Creating the letter " + letter )
    bpy.ops.view3d.snap_cursor_to_center()
    bpy.ops.object.text_add()
    ob=bpy.context.object
    ob.data.body = letter
    bpy.ops.object.convert(target='MESH')
    bpy.context.scene.objects.active.name = letter
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')

    #bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.1), "constraint_axis":(False, False, True), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})


    #   bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.1), "constraint_axis":(False, False, True), "constraint_orientation":'NORMAL', "mirror":False })

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.editmode_toggle()

    #bpy.ops.transform.resize(value=(0.1, 0.1, 0.1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
    bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
    bpy.ops.object.select_all(action='DESELECT')

    print ( "Done creating the letter " + letter )



def update_obj_from_plf ( scene, parent_name, obj_name, plf, glyph="", force=False ):

    vertex_list = plf.points
    face_list = plf.faces

    vertices = []
    for point in vertex_list:
        vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
    faces = []
    for face_element in face_list:
        faces.append ( face_element.verts )

    # Define the mesh name and prefix the current mesh name with "old_" so creating the new mesh doesn't cause a name collision
    if len(face_list) > 0:
        mesh_name = obj_name + "_mesh"
    else:
        mesh_name = obj_name + "_pos"
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
        print ( "Creating a new object" )
        obj = bpy.data.objects.new ( obj_name, new_mesh )
        scene.objects.link ( obj )
        # Assign the parent if requested in the call with a non-none parent_name
        if parent_name:
            if parent_name in bpy.data.objects:
                obj.parent = bpy.data.objects[parent_name]

    if "old_"+mesh_name in bpy.data.meshes:
        if bpy.data.meshes["old_"+mesh_name].users <= 0:
            bpy.data.meshes.remove ( bpy.data.meshes["old_"+mesh_name] )

    if len(face_list) <= 0:
        # These are points only, so create a shape glyph as needed to show the points
        shape_name = obj_name + "_shape"
        #if force or not (shape_name in scene.objects):
        if not (shape_name in scene.objects):
            old_shape_name = "old_" + shape_name
            size = 0.1
            print ( "Creating a new glyph for " + obj_name )

            shape_plf = get_named_shape ( glyph, size_x=size, size_y=size, size_z=size )

            shape_vertices = []
            for point in shape_plf.points:
                shape_vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
            shape_faces = []
            for face_element in shape_plf.faces:
                shape_faces.append ( face_element.verts )
            # Rename the old mesh shape if it exists
            if shape_name in bpy.data.meshes:
                bpy.data.meshes[shape_name].name = old_shape_name
            # Create and build the new mesh
            new_mesh = bpy.data.meshes.new ( shape_name )
            new_mesh.from_pydata ( shape_vertices, [], shape_faces )
            new_mesh.update()

            shape = bpy.data.objects.new ( shape_name, new_mesh )
            shape.data.materials.clear()  # New
            shape.data.materials.append ( bpy.data.materials[obj_name + "_mat"] ) # New

            # This didn't work very well

            #if not (shape_name in scene.objects):
            #    shape = bpy.data.objects.new ( shape_name, new_mesh )
            ## Create a material specifically for this object
            #if obj_name+"_mat" in bpy.data.materials:
            #    shape.data.materials.clear()  # New
            #    shape.data.materials.append ( bpy.data.materials[obj_name + "_mat"] ) # New
            ## Remove current children from the target object (otherwise glyphs will be merged ... useful in the future)
            #while len(obj.children) > 0:
            #    obj.children[0].parent = None


            # Add the shape to the scene as a glyph for the object
            scene.objects.link ( shape )
            obj.dupli_type = 'VERTS'
            shape.parent = obj
            
            if old_shape_name in bpy.data.meshes:
                if bpy.data.meshes[old_shape_name].users <= 0:
                    bpy.data.meshes.remove ( bpy.data.meshes[old_shape_name] )

    # Could return the object here if needed



@persistent
def mol_sim_frame_change_handler(scene):

    app = scene.molecule_simulation

    plf = create_squashed_z_box ( scene, min_len=0.25, max_len=3.5, period_frames=125, frame_num=scene.frame_current )
    update_obj_from_plf ( scene, None, "dynamic_box", plf )
    
    app.update_simulation(scene)




def add_new_empty_object ( child_name, parent_name=None ):
    obj = bpy.data.objects.get(child_name)
    if not obj:
        bpy.ops.object.add(location=[0, 0, 0])      # Create an "Empty" object in the Blender scene
        ### Note, the following line seems to cause an exception in some contexts: 'Context' object has no attribute 'selected_objects'
        obj = bpy.context.selected_objects[0]  # The newly added object will be selected
        obj.name = child_name                 # Name this empty object "molecules" 
        obj.hide_select = True
        obj.hide = True
    if parent_name:
        obj.parent = bpy.data.objects[parent_name]
    return obj
    
    
def Build_Molecule_Model ( context, mol_types="vs", size=[1.0,1.0,1.0], dc_2D="1e-4", dc_3D="1e-5", time_step=1e-6, iterations=300, min_len=0.25, max_len=3.5, period_frames=100, mdl_hash="", seed=1 ):

    mol_model = Molecule_Model ( context )

    # add_new_empty_object ( "MoleculeSimulation" )
    # add_new_empty_object ( "model_objects", "MoleculeSimulation" )
    # add_new_empty_object ( "molecules", "MoleculeSimulation" )
    add_new_empty_object ( "molecules", None )

    # Run the frame change handler one time to create the box object
    mol_sim_frame_change_handler(context.scene)

    # bpy.data.objects['dynamic_box'].parent = bpy.data.objects['model_objects']
    bpy.data.objects['dynamic_box'].draw_type = "BOUNDS"

    """
    if "v" in mol_types: molv = mol_model.add_molecule_species_to_model ( name="v", mol_type="3D", diff_const_expr=dc_3D )
    if "s" in mol_types: mols = mol_model.add_molecule_species_to_model ( name="s", mol_type="2D", diff_const_expr=dc_2D )

    if "v" in mol_types: mol_model.add_molecule_release_site_to_model ( mol="v", shape="OBJECT", obj_expr="dynamic_box", q_expr="1000" )
    if "s" in mol_types: mol_model.add_molecule_release_site_to_model ( mol="s", shape="OBJECT", obj_expr="dynamic_box", q_expr="1000" )


    mol_model.refresh_molecules()

    if "v" in mol_types: mol_model.change_molecule_display ( molv, glyph='Cube', scale=3.0, red=1.0, green=1.0, blue=1.0 )
    if "s" in mol_types: mol_model.change_molecule_display ( mols, glyph='Cone', scale=5.0, red=0.0, green=1.0, blue=0.1 )

    """
    mol_model.set_view_back()

    return mol_model



class MoleculeSimRunOperator(bpy.types.Operator):
    bl_idname = "mol_sim.run"
    bl_label = "Run Simulation"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        global active_frame_change_handler
        active_frame_change_handler = mol_sim_frame_change_handler

        mol_model = Build_Molecule_Model ( context, time_step=1e-6, iterations=100, period_frames=50, min_len=0.25, max_len=3.5, mdl_hash="", seed=1 )

        mol_model.hide_manipulator ( hide=True )
        mol_model.play_animation()

        return { 'FINISHED' }


class MoleculeSimActivateOperator(bpy.types.Operator):
    bl_idname = "mol_sim.activate"
    bl_label = "Activate"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        global active_frame_change_handler
        active_frame_change_handler = mol_sim_frame_change_handler
        return { 'FINISHED' }


class MoleculeSimDeactivateOperator(bpy.types.Operator):
    bl_idname = "mol_sim.deactivate"
    bl_label = "Deactivate"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        global active_frame_change_handler
        active_frame_change_handler = None
        return { 'FINISHED' }



def add_handler ( handler_list, handler_function ):
    """ Only add a handler if it's not already in the list """
    if not (handler_function in handler_list):
        handler_list.append ( handler_function )


def remove_handler ( handler_list, handler_function ):
    """ Only remove a handler if it's in the list """
    if handler_function in handler_list:
        handler_list.remove ( handler_function )


# Load scene callback
@persistent
def scene_loaded(dummy):
    pass

# Frame change callback
@persistent
def test_suite_frame_change_handler(scene):
  global active_frame_change_handler
  if active_frame_change_handler != None:
      active_frame_change_handler ( scene )


def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.molecule_simulation = bpy.props.PointerProperty(type=MoleculeSimPropertyGroup)
    # Add the scene update pre handler
    add_handler ( bpy.app.handlers.scene_update_pre, scene_loaded )
    add_handler ( bpy.app.handlers.frame_change_pre, test_suite_frame_change_handler )


def unregister():
    print ("Unregistering ", __name__)
    remove_handler ( bpy.app.handlers.frame_change_pre, test_suite_frame_change_handler )
    remove_handler ( bpy.app.handlers.scene_update_pre, scene_loaded )
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.molecule_simulation

if __name__ == "__main__":
    register()


# test call
#bpy.ops.modtst.dialog_operator('INVOKE_DEFAULT')


