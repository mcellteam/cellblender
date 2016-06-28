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
This file contains the classes for CellBlender's Model Objects.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_release
from . import cellblender_utils


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Model Object Operators:

class MCELL_OT_snap_cursor_to_center(bpy.types.Operator):
    bl_idname = "mcell.snap_cursor_to_center"
    bl_label = "Snap Cursor to Center"
    bl_description = ("Snap the 3D Cursor to the Center")

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
        return{'FINISHED'}


class MCELL_OT_create_object(bpy.types.Operator):
    bl_idname = "mcell.model_objects_create"
    bl_label = "Model Objects Create"
    bl_description = ("Add a new primitive object")

    def get_object_options(self, context):
        return [ ("bpy.ops.mesh.primitive_cube_add()","Cube","0"),
                 ("bpy.ops.mesh.primitive_ico_sphere_add()","IcoSphere","0"),
                 ("bpy.ops.mesh.primitive_cylinder_add()","Cylinder","0"),
                 ("bpy.ops.mesh.primitive_cone_add()","Cone","0"),
                 ("bpy.ops.mesh.primitive_torus_add()","Torus","0") ]

    option_item = bpy.props.EnumProperty(items = get_object_options, name = "NewObjectOptions", description = "New Object Options List")

    def execute(self, context):
        #print ( "Executing with self.get_object_options = " + str(self.get_object_options(context)) )
        #print ( "Executing with self.option_list = " + str(self.option_item) )
        eval ( str(self.option_item) )
        return{'FINISHED'}


class MCELL_OT_model_obj_add_mat(bpy.types.Operator):
    bl_idname = "mcell.model_obj_add_mat"
    bl_label = "Create Material"
    bl_description = ("Create a new material for selected object")

    def execute(self, context):
        model_objects = context.scene.mcell.model_objects
        obj_name = str(model_objects.object_list[model_objects.active_obj_index].name)
        for obj in context.selected_objects:
            obj.select = False
        obj = bpy.data.objects[obj_name]
        obj.select = True
        context.scene.objects.active = obj
        mat_name = obj_name + "_mat"
        if bpy.data.materials.get(mat_name) is not None:
            mat = bpy.data.materials[mat_name]
        else:
            mat = bpy.data.materials.new(name=mat_name)
        if len(obj.data.materials):
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        return{'FINISHED'}


class MCELL_OT_model_objects_add(bpy.types.Operator):
    bl_idname = "mcell.model_objects_add"
    bl_label = "Model Objects Include"
    bl_description = ("Include objects selected in 3D View Window in Model Objects export list")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        # From the list of selected objects, only add MESH objects.
        objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objs:
            # context.active_object = obj # Can't do this because active_object is read only
            context.scene.objects.active = obj

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY',
                                               ngon_method='BEAUTY')
            bpy.ops.object.mode_set(mode='OBJECT')
            obj.draw_type = 'SOLID'
            obj.show_all_edges = True
            obj.mcell.include = True

        if len(objs) > 0:
            # Rebuild the list of objects
            model_objects_update(context)
            # Select the last selected object
            obj_to_select_in_list = objs[-1]  # The last selected object
            if obj_to_select_in_list.name in mcell.model_objects.object_list:
                mcell.model_objects.active_obj_index = mcell.model_objects.object_list.find(obj_to_select_in_list.name)

#        for obj in objs:
#            # Prevent duplicate entries
#            if not obj.name in mcell.model_objects.object_list:
#                mcell.model_objects.object_list.add()
#                mcell.model_objects.active_obj_index = len(
#                    mcell.model_objects.object_list)-1
#                mcell.model_objects.object_list[
#                    mcell.model_objects.active_obj_index].name = obj.name


        return {'FINISHED'}


class MCELL_OT_model_objects_remove(bpy.types.Operator):
    bl_idname = "mcell.model_objects_remove"
    bl_label = "Model Objects Remove"
    bl_description = "Remove selected item from Model Objects export list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        mobjs = mcell.model_objects
        sobjs = context.scene.objects

        if (len(mobjs.object_list) > 0):
            obj = sobjs.get(mobjs.object_list[mobjs.active_obj_index].name)
            if obj:
                obj.mcell.include = False

                mobjs.object_list.remove(mobjs.active_obj_index)
                mobjs.active_obj_index -= 1
                if (mobjs.active_obj_index < 0):
                    mobjs.active_obj_index = 0
        
        model_objects_update(context)

        return {'FINISHED'}


class MCELL_OT_model_objects_remove_sel(bpy.types.Operator):
    bl_idname = "mcell.model_objects_remove_sel"
    bl_label = "Model Objects Remove Selected"
    bl_description = ("Remove objects selected in 3D View Window from Model Objects export list")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        mcell = context.scene.mcell
        mobjs = mcell.model_objects
        sobjs = context.scene.objects

        # From the list of selected objects, only remove MESH objects.
        objs = [obj for obj in context.selected_objects if obj.type == 'MESH']
        for obj in objs:
            obj.mcell.include = False

        model_objects_update(context)

        return {'FINISHED'}




class MCELL_OT_select_filtered(bpy.types.Operator):
    bl_idname = "mcell.select_filtered"
    bl_label = "Select Filtered"
    bl_description = "Select objects matching the filter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scn = context.scene
        mcell = scn.mcell
        objs = scn.objects

        filter = mcell.object_selector.filter

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
        mcell = scn.mcell
        objs = scn.objects

        filter = mcell.object_selector.filter

        for obj in objs:
            if obj.type == 'MESH':
                m = re.match(filter, obj.name)
                if m is not None:
                    if m.end() == len(obj.name):
                        obj.select = False

        return {'FINISHED'}


class MCELL_OT_toggle_visibility_filtered(bpy.types.Operator):
  bl_idname = "mcell.toggle_visibility_filtered"
  bl_label = "Visibility Filtered"
  bl_description = "Toggle visibility of objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mcell = scn.mcell
    objs = scn.objects

    filter = mcell.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.hide = not obj.hide

    return {'FINISHED'}


class MCELL_OT_toggle_renderability_filtered(bpy.types.Operator):
  bl_idname = "mcell.toggle_renderability_filtered"
  bl_label = "Renderability Filtered"
  bl_description = "Toggle renderability of objects matching the filter"
  bl_options = {'REGISTER', 'UNDO'}

  def execute(self,context):

    scn = context.scene
    mcell = scn.mcell
    objs = scn.objects

    filter = mcell.object_selector.filter

    for obj in objs:
      if obj.type == 'MESH':
        m = re.match(filter,obj.name)
        if m != None:
          if m.end() == len(obj.name):
            obj.hide_render= not obj.hide_render

    return {'FINISHED'}




class MCell_OT_object_show_all(bpy.types.Operator):
    bl_idname = "mcell.object_show_all"
    bl_label = "Show All"
    bl_description = "Show all of the model objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in context.scene.objects:
            if 'mcell' in o:
                if o.mcell.include:
                    # This is a model object, so show it
                    o.hide = False
        return {'FINISHED'}

class MCell_OT_object_hide_all(bpy.types.Operator):
    bl_idname = "mcell.object_hide_all"
    bl_label = "Hide All"
    bl_description = "Hide all of the model objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for o in context.scene.objects:
            if 'mcell' in o:
                if o.mcell.include:
                    # This is a model object, so hide it
                    o.hide = True
        return {'FINISHED'}



# Model Objects callback functions


# Rebuild Model Objects List from Scratch
#   This is required to catch changes in names of objects.
#   Note: This function is also registered as a load_post and save_pre handler
@persistent
def model_objects_update(context):
    # print ( "model_objects_update() called" )
    if not context:
        context = bpy.context

    mcell = context.scene.mcell
    mobjs = mcell.model_objects
    sobjs = context.scene.objects

    model_obj_names = [obj.name for obj in sobjs if obj.mcell.include]

    # Note: This bit only needed to convert
    #       old model object list (pre 0.1 rev_55) to new style.
    #       Old style did not have obj.mcell.include Boolean Property.
    if ((len(model_obj_names) == 0) & (len(mobjs.object_list) > 0)):
        for i in range(len(mobjs.object_list)-1):
            obj = sobjs.get(mobjs.object_list[i].name)
            if obj:
                obj.mcell.include = True
        model_obj_names = [
            obj.name for obj in sobjs if obj.mcell.include]

    # Update the model object list from objects marked obj.mcell.include = True
    if (len(model_obj_names) > 0):
        model_obj_names.sort()

        for i in range(len(mobjs.object_list)-1, -1, -1):
            mobjs.object_list.remove(i)

        active_index = mobjs.active_obj_index
        for obj_name in model_obj_names:
            mobjs.object_list.add()
            mobjs.active_obj_index = len(mobjs.object_list)-1
            mobjs.object_list[mobjs.active_obj_index].name = obj_name
            scene_object = sobjs[obj_name]
            # Set an error status if object is not triangulated
            for face in scene_object.data.polygons:
                if not (len(face.vertices) == 3):
                    status = "Object is not triangulated: %s" % (obj_name)
                    mobjs.object_list[mobjs.active_obj_index].status = status
                    break

        if len(mobjs.object_list) <= 0:
            mobjs.active_obj_index = 0
        else:
            if active_index < len(mobjs.object_list):
                mobjs.active_obj_index = active_index
            else:
                mobjs.active_obj_index = len(mobjs.object_list) - 1

        # We check release sites are valid here in case a user adds an object
        # referenced in a release site after adding the release site itself.
        # (e.g. Add Cube shaped release site. Then add Cube.)
        release_list = mcell.release_sites.mol_release_list
        save_release_idx = mcell.release_sites.active_release_index
        # check_release_site_wrapped acts on the active release site, so we
        # need to increment it and then check
        for rel_idx, _ in enumerate(release_list):
            mcell.release_sites.active_release_index = rel_idx
            cellblender_release.check_release_site_wrapped(context)
        # Restore the active index
        mcell.release_sites.active_release_index = save_release_idx

    return


def check_model_object(self, context):
    """Checks for illegal object name"""

    mcell = context.scene.mcell
    model_object_list = mcell.model_objects.object_list
    model_object = model_object_list[mcell.model_objects.active_obj_index]

    # print ("Checking name " + model_object.name )

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    model_object_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(model_object_filter, model_object.name)
    if m is None:
        status = "Object name error: %s" % (model_object.name)

    model_object.status = status

    return




# Model Objects Panel Classes

class MCELL_UL_model_objects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        #print ( "item = " + str(item) )
        #print ( "data = " + str(data) )
        #print ( "active_data = " + str(active_data) )
        #print ( "active_propname = " + str(active_propname) )
        #print ( "index = " + str(index) )
        #print ( "active = " + str(active_data[active_propname]) )
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            # Would like to lay out the actual object name so it can be changed right there.
            # But this has many "trickle down" effects so it hasn't been done yet.
            # layout.prop(item, 'name', text="", icon='FILE_TICK')
            # layout.prop(bpy.data.objects[item.name], 'name', text="", icon='FILE_TICK')
            model_obj = context.scene.objects[item.name]
            col = layout.column()
            col.label(item.name, icon='FILE_TICK')

            has_material = True
            if len(model_obj.material_slots) <= 0:
              has_material = False
            else:
              if model_obj.material_slots[0].material == None:
                has_material = False

            split = layout.split(percentage=0.8)  # This is used to make the color patch smaller
            col1 = split.column()
            col = split.column()
            if not has_material:
              if active_data[active_propname] == index:
                  # Only draw the add material in this slot when this object is selected
                  col.operator("mcell.model_obj_add_mat", text=" ", icon='COLOR')  # 'MATERIAL'
              else:
                  # If this slot is not selected, just draw a label
                  col.label(text=" ", icon='COLOR')  # 'MATERIAL'
            else:
              mat = model_obj.material_slots[0].material
              col.prop ( mat, "diffuse_color", text="" )

            col = layout.column()
            col.prop(item, 'object_show_only', text="", icon='VIEWZOOM')

            col = layout.column()
            col.prop(model_obj, 'hide', text="")


class MCELL_PT_model_objects(bpy.types.Panel):
    bl_label = "CellBlender - Model Objects"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.model_objects.draw_panel ( context, self )



# Model Objects Property Groups

def object_show_only_callback(self, context):
    mcell = context.scene.mcell

    #print ( "Object show only callback for object " + self.name )
    # Note the check before set to keep from infinite recursion in properties!!
    if self.object_show_only != False:
        self.object_show_only = False

    for o in context.scene.objects:
        if 'mcell' in o:
            if o.mcell.include:
                # This is a model object, so check the name
                if o.name == self.name:
                    # Unhide, Select, and Make Active
                    o.hide = False
                    o.select = True
                    context.scene.objects.active = o
                else:
                    # Unhide and DeSelect
                    o.hide = True
                    o.select = False

    if self.name in mcell.model_objects.object_list:
        # Select this item in the list as well
        mcell.model_objects.active_obj_index = mcell.model_objects.object_list.find ( self.name )
    return


class MCellModelObjectsProperty(bpy.types.PropertyGroup):
    name = StringProperty(name="Object Name", update=check_model_object)
    object_show_only = BoolProperty ( default=False, description='Show only this object', update=object_show_only_callback )
    status = StringProperty(name="Status")
    """
    def build_data_model_from_properties ( self, context ):
        print ( "Model Object building Data Model" )
        mo_dm = {}
        mo_dm['data_model_version'] = "DM_2014_10_24_1638"
        mo_dm['name'] = self.name
        return mo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModelObjectsProperty Data Model" )
        print ( "-------------->>>>>>>>>>>>>>>>>>>>> NOT IMPLEMENTED YET!!!" )
        return dm



    def build_properties_from_data_model ( self, context, dm ):

        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModelObjectsProperty data model to current version." )

        print ( "Assigning Model Object " + dm['name'] )
        self.name = dm["name"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )

    """

    def remove_properties ( self, context ):
        print ( "Removing all Model Objects Properties... no collections to remove." )


def active_obj_index_changed ( self, context ):
    """ The "self" passed in is a MCellModelObjectsPropertyGroup object. """
    #print ( "Type of self = " + str ( type(self) ) )

    if len(self.object_list) > 0:
        model_object = self.object_list[self.active_obj_index]
        for o in context.scene.objects:
            if o.name == model_object.name:
                # Unhide, Select, and Make Active
                o.hide = False
                o.select = True
                context.scene.objects.active = o
            else:
                # DeSelect
                o.select = False



import mathutils

class MCellModelObjectsPropertyGroup(bpy.types.PropertyGroup):
    object_list = CollectionProperty(
        type=MCellModelObjectsProperty, name="Object List")
    active_obj_index = IntProperty(name="Active Object Index", default=0, update=active_obj_index_changed)
    show_display = bpy.props.BoolProperty(default=False)  # If Some Properties are not shown, they may not exist!!!

    def remove_properties ( self, context ):
        print ( "Removing all Model Object List Properties..." )
        for item in self.object_list:
            item.remove_properties(context)
        self.object_list.clear()
        self.active_obj_index = 0
        print ( "Done removing all Model Object List Properties." )


    def draw_layout ( self, context, layout ):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            #col = row.column()
            row.operator("mcell.snap_cursor_to_center", icon="CURSOR", text="Center Cursor")
            #col = row.column()
            #row.label(text="    Add:")
            #col = row.column()
            row.operator("mesh.primitive_cube_add", text="", icon='MESH_CUBE')
            #col = row.column()
            row.operator("mesh.primitive_ico_sphere_add", text="", icon='MESH_ICOSPHERE')
            #col = row.column()
            row.operator("mesh.primitive_cylinder_add", text="", icon='MESH_CYLINDER')
            #col = row.column()
            row.operator("mesh.primitive_cone_add", text="", icon='MESH_CONE')
            #col = row.column()
            row.operator("mesh.primitive_torus_add", text="", icon='MESH_TORUS')
            #col = row.column()
            row.operator("mesh.primitive_plane_add", text="", icon='MESH_PLANE')
            #col = row.column()
            #col.operator_menu_enum("mcell.model_objects_create", 'option_item', text="Create Object")

            row = layout.row()
            if context.active_object is None:
                row.label ( "No active object" )
            else:
                row.prop (context.active_object, "name", text="Active Object")

            row = layout.row()
            col = row.column()
            col.template_list("MCELL_UL_model_objects", "model_objects",
                              self, "object_list",
                              self, "active_obj_index", rows=4)
            """
            col = row.column(align=True)
#           col.active = (len(context.selected_objects) == 1)
            col.operator("mcell.model_objects_add", icon='ZOOMIN', text="")
            col.operator("mcell.model_objects_remove", icon='ZOOMOUT', text="")

            col.operator("mcell.model_objects_remove_sel", icon='X', text="")

            subcol = col.column(align=True)
            subcol.operator("mcell.object_show_all", icon='RESTRICT_VIEW_OFF', text="")
            subcol.operator("mcell.object_hide_all", icon='RESTRICT_VIEW_ON', text="")
            """

            col = row.column(align=False)
            # Use subcolumns to group logically related buttons together
            subcol = col.column(align=True)
            subcol.operator("mcell.model_objects_add", icon='ZOOMIN', text="")
            subcol.operator("mcell.model_objects_remove", icon='ZOOMOUT', text="")
            subcol.operator("mcell.model_objects_remove_sel", icon='X', text="")
            subcol = col.column(align=True)
            subcol.operator("mcell.object_show_all", icon='RESTRICT_VIEW_OFF', text="")
            subcol.operator("mcell.object_hide_all", icon='RESTRICT_VIEW_ON', text="")



            if len(self.object_list) > 0:
                obj_name = str(self.object_list[self.active_obj_index].name)
                # layout.label(text="") # Use as a separator
                # layout.box() # Use as a separator
                # layout.label(text="") # Use as a separator
                box = layout.box()
                row = box.row()
                if not self.show_display:
                    row.prop(self, "show_display", icon='TRIA_RIGHT',
                             text=obj_name+" Display Options", emboss=False)
                else:
                    row.prop(self, "show_display", icon='TRIA_DOWN',
                             text=obj_name+" Display Options", emboss=False)

                    #row = box.row()
                    #row.prop ( self.object_list[self.active_obj_index], "name", text="Current Name" )

                    row = box.row()
                    col = row.column()
                    col.prop ( context.scene.objects[obj_name], "draw_type", text="" )
                    col = row.column()
                    col.prop ( context.scene.objects[obj_name], "show_wire", text="Show Wire" )
                    col = row.column()
                    col.prop ( context.scene.objects[obj_name], "show_x_ray", text="Show X-Ray" )
                    col = row.column()
                    col.prop ( context.scene.objects[obj_name], "show_name", text="Show Name" )
                    
                    has_material = True
                    if len(context.scene.objects[obj_name].material_slots) <= 0:
                      has_material = False
                    else:
                      if context.scene.objects[obj_name].material_slots[0].material == None:
                        has_material = False
                    if not has_material:
                      row = box.row()
                      row.operator("mcell.model_obj_add_mat", text="Add a Material")
                    else:
                      mat = context.scene.objects[obj_name].material_slots[0].material
                      row = box.row()
                      col = row.column()
                      col.prop ( mat, "diffuse_color", text="" )
                      col = row.column()
                      col.prop ( mat, "emit", text="Emit" )
                      row = box.row()
                      col = row.column()
                      col.prop ( context.scene.objects[obj_name], "show_transparent", text="Object Transparent" )
                      col = row.column()
                      col.prop ( mat, "use_transparency", text="Material Transparent" )
                      if context.scene.objects[obj_name].show_transparent and mat.use_transparency:
                        row = box.row()
                        row.prop ( mat, "alpha", text="Alpha" )

#           row = layout.row()
#           sub = row.row(align=True)
#           sub.operator("mcell.model_objects_include", text="Include")
#           sub = row.row(align=True)
#           sub.operator("mcell.model_objects_select", text="Select")
#           sub.operator("mcell.model_objects_deselect", text="Deselect")

            """
            row = layout.row()
            row.label(text="Object Color:", icon='COLOR')
            
            active = None
            for o in self.object_list.keys():
                # print ( "Object: " + o )
                row = layout.row()
                if bpy.context.scene.objects[o] == bpy.context.scene.objects.active:
                    active = bpy.context.scene.objects[o]
                    row.label(text=o, icon='TRIA_RIGHT')
                else:
                    row.label(text=o, icon='DOT')

            if active == None:
                row = layout.row()
                row.label(text="No CellBlender object is active", icon='DOT')
            else:
                row = layout.row()
                row.label ( icon='DOT', text="  Object " + active.name + " is active and has " +
                    str(len(active.material_slots)) + " material slots" )
            """


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


    def build_data_model_from_properties ( self, context ):
    
        print ( "Model Objects List building Data Model" )
        mo_dm = {}
        mo_dm['data_model_version'] = "DM_2014_10_24_1638"
        mo_list = []
        for scene_object in context.scene.objects:
            if scene_object.type == 'MESH':
                if scene_object.mcell.include:
                    print ( "MCell object: " + scene_object.name )
                    mo_list.append ( { "name": scene_object.name } )
        mo_dm['model_object_list'] = mo_list
        return mo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModelObjectsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModelObjectsPropertyGroup data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):
        # Note that model object list is represented in two places:
        #   context.scene.mcell.model_objects.object_list[] - stores the name
        #   context.scene.objects[].mcell.include - boolean is true for model objects
        # This code updates both locations based on the data model

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModelObjectsPropertyGroup data model to current version." )
        
        # Remove all model objects in the list
        while len(self.object_list) > 0:
            self.object_list.remove(0)
            
        # Create a list of model object names from the Data Model
        mo_list = []
        if "model_object_list" in dm:
          for m in dm["model_object_list"]:
              print ( "Data model contains " + m["name"] )
              self.object_list.add()
              self.active_obj_index = len(self.object_list)-1
              mo = self.object_list[self.active_obj_index]
              #mo.init_properties(context.scene.mcell.parameter_system)
              #mo.build_properties_from_data_model ( context, m )
              mo.name = m['name']
              mo_list.append ( m["name"] )

        # Use the list of Data Model names to set flags of all objects
        for k,o in context.scene.objects.items():
            if k in mo_list:
                o.mcell.include = True
            else:
                o.mcell.include = False

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )



    def build_data_model_materials_from_materials ( self, context ):
        print ( "Model Objects List building Materials for Data Model" )
        mat_dm = {}
        mat_dict = {}

        # First build the list of materials from all objects
        for data_object in context.scene.objects:
            if data_object.type == 'MESH':
                if data_object.mcell.include:
                    print ( "Saving Materials for: " + data_object.name )
                    for mat_slot in data_object.material_slots:
                        if not mat_slot.name in mat_dict:
                            # This is a new material, so add it
                            mat = bpy.data.materials[mat_slot.name]
                            print ( "  Adding " + mat_slot.name )
                            mat_obj = {}
                            mat_obj['diffuse_color'] = {
                                'r': mat.diffuse_color.r,
                                'g': mat.diffuse_color.g,
                                'b': mat.diffuse_color.b,
                                'a': mat.alpha }
                            # Need to set:
                            #  mat.use_transparency
                            #  obj.show_transparent
                            mat_dict[mat_slot.name] = mat_obj;
        mat_dm['material_dict'] = mat_dict
        return mat_dm


    def build_materials_from_data_model_materials ( self, context, dm ):

        # Delete any materials with conflicting names and then rebuild all

        # Start by creating a list of named materials in the data model
        mat_names = dm['material_dict'].keys()
        print ( "Material names = " + str(mat_names) )
        
        # Delete all materials with identical names
        for mat_name in mat_names:
            if mat_name in bpy.data.materials:
                bpy.data.materials.remove ( bpy.data.materials[mat_name] )
        
        # Now add all the new materials
        
        for mat_name in mat_names:
            new_mat = bpy.data.materials.new(mat_name)
            c = dm['material_dict'][mat_name]['diffuse_color']
            new_mat.diffuse_color = ( c['r'], c['g'], c['b'] )
            new_mat.alpha = c['a']
            if new_mat.alpha < 1.0:
                new_mat.use_transparency = True


    def build_data_model_geometry_from_mesh ( self, context ):
        print ( "Model Objects List building Geometry for Data Model" )
        g_dm = {}
        g_list = []

        for data_object in context.scene.objects:
            if data_object.type == 'MESH':
                if data_object.mcell.include:
                    print ( "MCell object: " + data_object.name )

                    g_obj = {}
                    
                    saved_hide_status = data_object.hide
                    data_object.hide = False

                    context.scene.objects.active = data_object
                    bpy.ops.object.mode_set(mode='OBJECT')

                    g_obj['name'] = data_object.name
                    
                    loc_x = data_object.location.x
                    loc_y = data_object.location.y
                    loc_z = data_object.location.z

                    g_obj['location'] = [loc_x, loc_y, loc_z]
                    
                    if len(data_object.data.materials) > 0:
                        g_obj['material_names'] = []
                        for mat in data_object.data.materials:
                            g_obj['material_names'].append ( mat.name )
                            # g_obj['material_name'] = data_object.data.materials[0].name
                    
                    v_list = []
                    mesh = data_object.data
                    matrix = data_object.matrix_world
                    vertices = mesh.vertices
                    for v in vertices:
                        t_vec = matrix * v.co
                        v_list.append ( [t_vec.x-loc_x, t_vec.y-loc_y, t_vec.z-loc_z] )
                    g_obj['vertex_list'] = v_list

                    f_list = []
                    faces = mesh.polygons
                    for f in faces:
                        f_list.append ( [f.vertices[0], f.vertices[1], f.vertices[2]] )
                    g_obj['element_connections'] = f_list
                    
                    if len(data_object.data.materials) > 1:
                        # This object has multiple materials, so store the material index for each face
                        mi_list = []
                        for f in faces:
                            mi_list.append ( f.material_index )
                        g_obj['element_material_indices'] = mi_list

                    regions = data_object.mcell.get_regions_dictionary(data_object)
                    if regions:
                        r_list = []

                        region_names = [k for k in regions.keys()]
                        region_names.sort()
                        for region_name in region_names:
                            rgn = {}
                            rgn['name'] = region_name
                            rgn['include_elements'] = regions[region_name]
                            r_list.append ( rgn )
                        g_obj['define_surface_regions'] = r_list

                    # restore proper object visibility state
                    data_object.hide = saved_hide_status

                    g_list.append ( g_obj )

        g_dm['object_list'] = g_list
        return g_dm


    def delete_all_mesh_objects ( self, context ):
        print ( "Inside \"delete_all_mesh_objects\"" )
        # TODO This function is VERY slow for large numbers of objects
        # TODO There should be a faster way since Blender can do this quicly
        bpy.ops.object.select_all(action='DESELECT')
        for scene_object in context.scene.objects:
            if scene_object.type == 'MESH':
                # print ( "Deleting Mesh object: " + scene_object.name )
                scene_object.hide = False
                scene_object.select = True
                bpy.ops.object.delete()
                # TODO Need to delete the mesh for this object as well!!!


    def build_mesh_from_data_model_geometry ( self, context, dm ):
            
        # Delete any objects with conflicting names and then rebuild all

        print ( "Model Objects List building Mesh Objects from Data Model Geometry" )
        
        # Start by creating a list of named objects in the data model
        model_names = [ o['name'] for o in dm['object_list'] ]
        # print ( "Model names = " + str(model_names) )

        print ( "  Delete objects with matching names" )

        # Delete all objects with identical names to model objects in the data model
        bpy.ops.object.select_all(action='DESELECT')
        for scene_object in context.scene.objects:
            if scene_object.type == 'MESH':
                print ( "Mesh object: " + scene_object.name )
                if scene_object.name in model_names:
                    print ( "  will be recreated from the data model ... deleting." )
                    # TODO preserve hidden/shown status
                    scene_object.hide = False
                    scene_object.select = True
                    bpy.ops.object.delete()
                    # TODO Need to delete the mesh for this object as well!!!

        print ( "  Done deleting objects" )
        print ( "  Create new objects" )

        most_recent_object = None
        # Now create all the object meshes from the data model
        for model_object in dm['object_list']:

            # print ( "    Create object " + model_object['name'] )

            vertices = []
            for vertex in model_object['vertex_list']:
                vertices.append ( mathutils.Vector((vertex[0],vertex[1],vertex[2])) )
            faces = []
            for face_element in model_object['element_connections']:
                faces.append ( face_element )
            new_mesh = bpy.data.meshes.new ( model_object['name'] )
            new_mesh.from_pydata ( vertices, [], faces )
            new_mesh.update()
            new_obj = bpy.data.objects.new ( model_object['name'], new_mesh )
            if 'location' in model_object:
                new_obj.location = mathutils.Vector((model_object['location'][0],model_object['location'][1],model_object['location'][2]))

            #print ( "    Add materials to " + model_object['name'] )

            # Add the materials to the object
            if 'material_names' in model_object:
                print ( "Object " + model_object['name'] + " has material names" )
                for mat_name in model_object['material_names']:
                    new_obj.data.materials.append ( bpy.data.materials[mat_name] )
                    if bpy.data.materials[mat_name].alpha < 1:
                        new_obj.show_transparent = True
                if 'element_material_indices' in model_object:
                    print ( "Object " + model_object['name'] + " has material indices" )
                    faces = new_obj.data.polygons
                    dm_count = len(model_object['element_material_indices'])
                    index = 0
                    for f in faces:
                        f.material_index = model_object['element_material_indices'][index % dm_count]
                        index += 1

            #print ( "    Add " + model_object['name'] + " to scene.objects" )

            context.scene.objects.link ( new_obj )
            # The following code slowed the creation process to a crawl!!!
            #bpy.ops.object.select_all ( action = "DESELECT" )
            #new_obj.select = True
            #context.scene.objects.active = new_obj
            most_recent_object = new_obj

            #print ( "    Add surface regions for " + model_object['name'] )

            # Add the surface regions to new_obj.mcell
            
            if model_object.get('define_surface_regions'):
                for rgn in model_object['define_surface_regions']:
                    print ( "  Building region[" + rgn['name'] + "]" )

                    bpy.ops.object.select_all ( action = "DESELECT" )
                    new_obj.select = True
                    context.scene.objects.active = new_obj

                    new_obj.mcell.regions.add_region_by_name ( context, rgn['name'] )
                    reg = new_obj.mcell.regions.region_list[rgn['name']]
                    reg.set_region_faces ( new_mesh, set(rgn['include_elements']) )

                print ( "  Done building all regions" )

        if most_recent_object != None:

            bpy.ops.object.select_all ( action = "DESELECT" )
            most_recent_object.select = True
            context.scene.objects.active = most_recent_object

        print ( "  Done creating new objects" )


