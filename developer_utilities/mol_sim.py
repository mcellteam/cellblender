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




"""
class MATERIAL_PT_mol_preview(MolMaterialButtonsPanel, Panel):
    bl_label = "Mol Preview"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        engine = context.scene.render.engine
        return check_material(mat) and (mat.type in {'SURFACE', 'WIRE'}) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        self.layout.template_preview(context.material)
        mat = active_node_mat(context.material)
        row = self.layout.row()
        col = row.column()
        col.prop(mat, "diffuse_color", text="")
        col = row.column()
        col.prop(mat, "emit", text="Mol Emit")
"""


class MolMATERIAL_PT_preview(MolMaterialButtonsPanel, Panel):
    bl_label = "Molecule Material Preview"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}

    """
    @classmethod
    def poll(cls, context):
        mat = context.material
        engine = context.scene.render.engine
        return check_material(mat) and (mat.type in {'SURFACE', 'WIRE'}) and (engine in cls.COMPAT_ENGINES)
    """

    @classmethod
    def poll(cls, context):
        ok = len(bpy.data.materials) and (context.scene.render.engine in cls.COMPAT_ENGINES)
        if not ok:
          print ( "MolMATERIAL_PT_preview poll returning " + str(ok) )
        return ok


    def draw(self, context):
        print ( "Inside MolMATERIAL_PT_preview draw method " + str(context) )
        #self.layout.template_preview(context.material)
        if 'molecule_simulation' in context.scene.keys():
          print ( "Context OK, showing materials" )
          app = context.scene.molecule_simulation
          m = app.molecule_list[app.active_mol_index]
          mat_name = m.name + "_mat"
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
          print ( "Context NOT OK, not showing materials" )














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
    print ( "name_change_callback called with self = " + str(self) )
    #self.name_change_callback(context)
    #self.check_callback(context)
    return


def display_callback(self, context):
    #self.display_callback(context)
    return

def shape_change_callback(self, context):
    print ( "Shape change callback for molecule " + self.name )
    #plf = MolCluster ( self.num, self.dist, self.center_x, self.center_y, self.center_z, context.scene.frame_current )
    #update_obj_from_plf ( context.scene, "molecules", self.name, plf, glyph=self.glyph, force=True )
    return

import os


class MoleculeProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Molecule Name", default="Molecule",description="The molecule species name",update=name_change_callback)
    old_name = StringProperty(name="Old Mol Name", default="Molecule")

    shape_name = StringProperty(name="ShapeName", default="")
    material_name = StringProperty(name="MatName", default="")

    mol_id = IntProperty(name="Molecule ID", default=0)


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
        ('A', "A", ""),
        ('B', "B", ""),
        ('C', "C", ""),
        ('Cube', "Cube", ""),
        ('Pyramid', "Pyramid", ""),
        ('Tetrahedron', "Tetrahedron", "")]
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
        self.dist = random.uniform(0.1,0.5)
        self.center_x = random.uniform(-2.0,2.0)
        self.center_y = random.uniform(-2.0,2.0)
        self.center_z = random.uniform(-2.0,2.0)
        self.glyph = self.glyph_enum[random.randint(0,len(self.glyph_enum)-1)][0]
        self.create_mol_data(context)


    def create_mol_data ( self, context ):

        meshes = bpy.data.meshes
        mats = bpy.data.materials
        objs = bpy.data.objects
        scn = bpy.context.scene
        scn_objs = scn.objects

        shape_name = self.name + "_shape"
        material_name = self.name + "_mat"

        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])
            mols_obj = bpy.context.selected_objects[0]
            mols_obj.name = "molecules"

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

        # Look-up material, create if needed.
        # Associate material with mesh shape.
        # Bob: Maybe we need to associate it with the OBJECT with: shape_object.material_slots[0].link = 'OBJECT'
        mol_mat = mats.get(material_name)
        if not mol_mat:
            mol_mat = mats.new(material_name)
            # Need to pick a color here
        if not mol_shape_mesh.materials.get(material_name):
            mol_shape_mesh.materials.append(mol_mat)

        # Create a "mesh" to hold instances of molecule positions
        mol_pos_mesh_name = "%s_pos" % (self.name)
        mol_pos_mesh = meshes.get(mol_pos_mesh_name)
        if not mol_pos_mesh:
            mol_pos_mesh = meshes.new(mol_pos_mesh_name)

        # Create object to contain the mol_pos_mesh data
        mol_obj = objs.get(self.name)
        if not mol_obj:
            mol_obj = objs.new(self.name, mol_pos_mesh)
            scn_objs.link(mol_obj)
            mol_shape_obj.parent = mol_obj
            mol_obj.dupli_type = 'VERTS'
            mol_obj.use_dupli_vertices_rotation = True
            mol_obj.parent = mols_obj


    def remove_mol_data ( self, context ):

        meshes = bpy.data.meshes
        mats = bpy.data.materials
        objs = bpy.data.objects
        scn = bpy.context.scene
        scn_objs = scn.objects

        mol_obj_name        = self.name
        mol_shape_obj_name  = self.name + "_shape"
        mol_shape_mesh_name = self.name + "_shape"
        mol_pos_mesh_name   = self.name + "_pos"
        mol_material_name   = self.name + "_mat"

        mols_obj = objs.get("molecules")

        mol_obj = objs.get(mol_obj_name)
        mol_shape_obj = objs.get(mol_shape_obj_name)
        mol_shape_mesh = meshes.get(mol_shape_mesh_name)
        mol_pos_mesh = meshes.get(mol_pos_mesh_name)
        mol_material = mats.get(mol_material_name)
        
        scn_objs.unlink ( mol_obj )
        scn_objs.unlink ( mol_shape_obj )

        if mol_obj.users <= 0:
            objs.remove ( mol_obj )
            meshes.remove ( mol_pos_mesh )

        if mol_shape_obj.users <= 0:
            objs.remove ( mol_shape_obj )
            meshes.remove ( mol_shape_mesh )
        
        if mol_material.users <= 0:
            mats.remove ( mol_material )
        


    def draw_layout ( self, context, layout, mol_list ):
        """ Draw the molecule "panel" within the layout """
        row = layout.row()
        row.prop(self, "name")
        row = layout.row()
        row.prop(self, "diffusion_constant")
        """
        box = layout.box()
        
        row = layout.row()
        row.prop(self, "glyph", text="Shape")
        if self.name+"_mat" in bpy.data.materials:
            row = layout.row()
            row.prop ( bpy.data.materials[self.name+"_mat"], "diffuse_color", text="Color" )

        box = layout.box()
        
        row = layout.row()
        row.prop(self, "num")
        row.prop(self, "dist")
        row = layout.row()
        row.prop(self, "center_x")
        row.prop(self, "center_y")
        row.prop(self, "center_z")
        """


    def old_draw_display_layout ( self, context, layout, mol_list ):
        """ Draw the molecule display "panel" within the layout """
        row = layout.row()
        row.prop(self, "glyph", text="Shape")
        if self.name+"_mat" in bpy.data.materials:
            row = layout.row()
            row.prop ( bpy.data.materials[self.name+"_mat"], "diffuse_color", text="Color" )
            row = layout.row()
            col = row.column()
            col.label ( "Brightness" )
            col = row.column()
            col.prop ( bpy.data.materials[self.name+"_mat"], "emit", text="Emit" )


    def draw_display_layout ( self, context, layout, mol_list ):
        """ Draw the molecule display "panel" within the layout """
        mat_name = self.name+"_mat"
        if mat_name in bpy.data.materials:
            if len(bpy.data.materials) and (context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}):
              if 'molecule_simulation' in context.scene.keys():
                #print ( "Context OK, showing materials" )
                app = context.scene.molecule_simulation
                m = app.molecule_list[app.active_mol_index]
                mat_name = m.name + "_mat"
                #print ( "" + mat_name + " in bpy.data.materials = " + str(mat_name in bpy.data.materials) )
                if mat_name in bpy.data.materials:
                  layout.template_preview(bpy.data.materials[mat_name])
              else:
                print ( "molecule_simulation not found, not showing color preview" )
                pass
            row = layout.row()
            row.prop ( bpy.data.materials[mat_name], "diffuse_color", text="Color" )
            row = layout.row()
            col = row.column()
            col.label ( "Brightness" )
            col = row.column()
            col.prop ( bpy.data.materials[mat_name], "emit", text="Emit" )
        else:
            print ( "Material " + mat_name + " not found, not showing materials" )
        row = layout.row()
        row.prop(self, "glyph", text="Shape")


    def draw(self, context):
        print ( "Inside MolMATERIAL_PT_preview draw method " + str(context) )
        if len(bpy.data.materials) and (context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}):
          #self.layout.template_preview(context.material)
          if 'molecule_simulation' in context.scene.keys():
            print ( "Context OK, showing materials" )
            app = context.scene.molecule_simulation
            m = app.molecule_list[app.active_mol_index]
            mat_name = m.name + "_mat"
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






        

    def draw_release_layout ( self, context, layout, mol_list ):
        """ Draw the molecule release "panel" within the layout """
        row = layout.row()
        row.prop(self, "method")
        row.prop(self, "num")
        row.prop(self, "dist")
        row = layout.row()
        row.prop(self, "center_x")
        row.prop(self, "center_y")
        row.prop(self, "center_z")


    def update_simulation ( self, scene ):
        plf = MolCluster ( self.num, self.dist, self.center_x, self.center_y, self.center_z, scene.frame_current, method=self.method )
        update_obj_from_plf ( scene, "molecules", self.name, plf, glyph=self.glyph )


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
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')




class MoleculeSimPropertyGroup(bpy.types.PropertyGroup):
    run_mcell = bpy.props.BoolProperty(name="Run MCell", default=True)

    molecule_list = CollectionProperty(type=MoleculeProperty, name="Molecule List")
    active_mol_index = IntProperty(name="Active Molecule Index", default=0)
    next_id = IntProperty(name="Counter for Unique Molecule IDs", default=1)  # Start ID's at 1 to confirm initialization
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!
    show_advanced = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!


    show_molecules = bpy.props.BoolProperty(default=True, name="Define Molecules")
    show_display = bpy.props.BoolProperty(default=False, name="Molecule Display Options")
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
            mol.update_simulation ( scene )



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
            row = layout.row()
            row.label ( "Renaming Molecules Doesn't Work YET!!!", icon='ERROR' )
            ################################



            row = layout.row()
            col = row.column()
            col.template_list("MolSim_UL_check_molecule", "define_molecules",
                              self, "molecule_list",
                              self, "active_mol_index",
                              rows=2)
            col = row.column(align=True)
            col.operator("molecule_simulation.molecule_add", icon='ZOOMIN', text="")
            col.operator("molecule_simulation.molecule_remove", icon='ZOOMOUT', text="")
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

  # An object that can hold points and faces

  points = []
  faces = []
  
  def __init__ ( self ):
    self.points = []
    self.faces = []


class Letter_A (plf_object):

  def __init__  ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):
    size_scale = 5
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
    size_scale = 5
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
    size_scale = 5
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

    self.points = [];
    self.faces = [];

    self.points = self.points + [ point (  size_x,  size_y, -size_z ) ]
    self.points = self.points + [ point (     0.0, -size_y, -size_z ) ]
    self.points = self.points + [ point ( -size_x,  size_y, -size_z ) ]
    self.points = self.points + [ point (     0.0,     0.0,  size_z ) ]

    face_list = [ [ 0, 1, 2 ], [ 0, 3, 1 ], [ 1, 3, 2 ], [ 2, 3, 0 ] ]

    for f in face_list:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class Pyramid (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a pyramid of the requested size

    self.points = [];
    self.faces = [];

    self.points = self.points + [ point (  size_x,  size_y, -size_z ) ]
    self.points = self.points + [ point (  size_x, -size_y, -size_z ) ]
    self.points = self.points + [ point ( -size_x, -size_y, -size_z ) ]
    self.points = self.points + [ point ( -size_x,  size_y, -size_z ) ]
    self.points = self.points + [ point (     0.0,     0.0,  size_z ) ]

    face_list = [ [ 1, 2, 3 ], [ 0, 1, 3 ], [ 0, 4, 1 ],
                  [ 1, 4, 2 ], [ 2, 4, 3 ], [ 3, 4, 0 ] ]

    for f in face_list:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


class BasicBox (plf_object):

  def __init__ ( self, size_x=1.0, size_y=1.0, size_z=1.0 ):

    # Create a box of the requested size

    self.points = [];
    self.faces = [];

    self.points = self.points + [ point (  size_x,  size_y, -size_z ) ]
    self.points = self.points + [ point (  size_x, -size_y, -size_z ) ]
    self.points = self.points + [ point ( -size_x, -size_y, -size_z ) ]
    self.points = self.points + [ point ( -size_x,  size_y, -size_z ) ]
    self.points = self.points + [ point (  size_x,  size_y,  size_z ) ]
    self.points = self.points + [ point (  size_x, -size_y,  size_z ) ]
    self.points = self.points + [ point ( -size_x, -size_y,  size_z ) ]
    self.points = self.points + [ point ( -size_x,  size_y,  size_z ) ]

    face_list = [ [ 1, 2, 3 ], [ 7, 6, 5 ], [ 4, 5, 1 ], [ 5, 6, 2 ],
                  [ 2, 6, 7 ], [ 0, 3, 7 ], [ 0, 1, 3 ], [ 4, 7, 5 ],
                  [ 0, 4, 1 ], [ 1, 5, 2 ], [ 3, 2, 7 ], [ 4, 0, 7 ] ]

    for f in face_list:
      self.faces.append ( face ( f[0], f[1], f[2] ) )


def create_squashed_z_box ( scene, min_len=0.25, max_len=3.5, period_frames=100, frame_num=None ):

    cur_frame = frame_num
    if cur_frame == None:
      cur_frame = scene.frame_current

    size_x = min_len + ( (max_len-min_len) * ( (1 - math.cos ( 2 * math.pi * cur_frame / period_frames )) / 2 ) )
    size_y = min_len + ( (max_len-min_len) * ( (1 - math.cos ( 2 * math.pi * cur_frame / period_frames )) / 2 ) )
    size_z = min_len + ( (max_len-min_len) * ( (1 - math.sin ( 2 * math.pi * cur_frame / period_frames )) / 2 ) )

    return BasicBox ( size_x, size_y, size_z )

"""

add Torus
rename Torus to 'mol_b_shape'

mbso = bpy.data.objects['mol_b_shape']
mb = bpy.data.objects['mol_b']
mb.dupli_type = 'VERTS'
mbso.parent = mb

"""


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

        


"""
Generating Letters:

text = "Hello"
bpy.ops.object.text_add(location=(0,0,0),rotation=(0,0,0))
text_object = bpy.context.object
text_object.name = text + "_name"
text_data = text_object.data
text_data.name = text + "_data"

text_object_data.body = text
text_object_data.size = 2
text_object_data.extrude = 0.2

bpy.ops.object.convert(target=  'MESH')
bpy.ops.shade_flat()





bpy.ops.view3d.snap_cursor_to_center()
bpy.ops.object.text_add(view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
bpy.ops.object.editmode_toggle()
bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')
bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')
bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')
bpy.ops.font.delete(type='PREVIOUS_OR_SELECTION')
bpy.ops.font.text_insert(text="A")
bpy.ops.object.editmode_toggle()
bpy.ops.object.convert(target='MESH')
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='TOGGLE')
bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.108318), "constraint_axis":(False, False, True), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
bpy.ops.object.editmode_toggle()




bpy.ops.view3d.snap_cursor_to_center()
bpy.ops.object.text_add()
ob=bpy.context.object
ob.data.body = "A"
bpy.ops.object.convert(target='MESH')
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 0.1), "constraint_axis":(False, False, True), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
bpy.ops.object.editmode_toggle()
bpy.ops.transform.resize(value=(0.1, 0.1, 0.1), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
bpy.ops.object.select_all(action='DESELECT')
"""


def generate_letter_object ( letter ):
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

    """
    bpy.ops.mesh.extrude_region_move (
         MESH_OT_extrude_region={"mirror":False},
         TRANSFORM_OT_translate={ "value":(0, 0, 0.1), 
                                  "constraint_axis":(False, False, True), 
                                  "constraint_orientation":'GLOBAL', 
                                  "mirror":False, 
                                  "proportional":'DISABLED', 
                                  "proportional_edit_falloff":'SMOOTH', 
                                  "proportional_size":1, 
                                  "snap":False, 
                                  "snap_target":'CLOSEST', 
                                  "snap_point":(0, 0, 0), 
                                  "snap_align":False, 
                                  "snap_normal":(0, 0, 0), 
                                  "gpencil_strokes":False, 
                                  "texture_space":False, 
                                  "remove_on_cancel":False, 
                                  "release_confirm":False } )
    """

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
    if obj_name in scene.objects:
        obj = scene.objects[obj_name]
        old_mesh = obj.data
        obj.data = new_mesh
        bpy.data.meshes.remove ( old_mesh )
    else:
        print ( "Creating a new object" )
        obj = bpy.data.objects.new ( obj_name, new_mesh )
        scene.objects.link ( obj )
        if parent_name:
            if parent_name in bpy.data.objects:
                obj.parent = bpy.data.objects[parent_name]

    if "old_"+mesh_name in bpy.data.meshes:
        bpy.data.meshes.remove ( bpy.data.meshes["old_"+mesh_name] )

    if len(face_list) <= 0:
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


