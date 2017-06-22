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
This file contains the classes for CellBlender's Molecule Release/Placement.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import re

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils
from . import cellblender_preferences

import cellblender.data_model as data_model


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)



########################################################
#
#   Release Site Code
#
########################################################


class MCELL_OT_release_site_add(bpy.types.Operator):
    bl_idname = "mcell.release_site_add"
    bl_label = "Add Release Site"
    bl_description = "Add a new Molecule Release Site to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.release_sites.add_release_site ( context )
        return {'FINISHED'}


class MCELL_OT_release_site_remove(bpy.types.Operator):
    bl_idname = "mcell.release_site_remove"
    bl_label = "Remove Release Site"
    bl_description = "Remove selected Molecule Release Site from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.release_sites.remove_active_rel_site(context)
        self.report({'INFO'}, "Deleted Release Site")
        return {'FINISHED'}



def check_release_site(self, context):
    """ Thin wrapper for check_release_site. """
    check_release_site_wrapped(context)


def check_release_site_wrapped(context):
    """ Make sure that the release site is valid. """

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    rel.status = ""

    if mcell.cellblender_preferences.bionetgen_mode:
        # Perform BioNetGen Checking
        pass

    else:
        # Perform MCell Checking

        name_status = check_release_site_name(context)
        molecule_status = ""

        if mcell.cellblender_preferences.bionetgen_mode:
            # Perform BioNetGen Molecule Checking
            pass
        else:
            # Perform MCell Molecule Checking
            molecule_status = check_release_molecule(context)

        object_status = check_release_object_expr(context)

        if name_status:
            rel.status = name_status
        elif molecule_status:
            rel.status = molecule_status
        elif object_status and rel.shape == 'OBJECT':
            rel.status = object_status
        else:
            rel.status = ""

    return


def check_release_site_name(context):
    """Checks for duplicate or illegal release site name."""

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]

    status = ""

    # Check for duplicate release site name
    rel_keys = rel_list.keys()
    if rel_keys.count(rel.name) > 1:
        status = "Duplicate release site: %s" % (rel.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_filter, rel.name)
    if m is None:
        status = "Release Site name error: %s" % (rel.name)

    return status


def check_release_molecule(context):
    """Checks for illegal release site molecule name."""

    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    mol = rel.molecule

    mol_list = mcell.molecules.molecule_list

    status = ""

    # Check for illegal names (Starts with a letter. No special characters.)
    mol_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(mol_filter, mol)
    if m is None:
        status = "Molecule name error: %s" % (mol)
    else:
        mol_name = m.group(1)
        if not mol_name in mol_list:
            status = "Undefined molecule: %s" % (mol_name)
        # Only change if necessary to avoid infinite recursion
        elif (mol_list[mol_name].type == '2D') and (not rel.shape in ('OBJECT', 'LIST') ):
            rel.shape = 'OBJECT'

    return status


def check_release_object_expr(context):
    """Checks for illegal release object name."""

    scn = context.scene
    mcell = context.scene.mcell
    rel_list = mcell.release_sites.mol_release_list
    rel = rel_list[mcell.release_sites.active_release_index]
    obj_list = mcell.model_objects.object_list
    obj_expr = rel.object_expr

    status = ""

    # Check for illegal names. (Starts with a letter. No special characters.)
    # May be only object name or object name and region (e.g. object[reg].)
    obj_reg_filter = (r"(?P<obj_reg>(?P<obj_name>^[A-Za-z]+[0-9A-Za-z_.]*)(\[)"
                      "(?P<reg_name>[A-Za-z]+[0-9A-Za-z_.]*)(\])$)|"
                      "(?P<obj_name_only>^([A-Za-z]+[0-9A-Za-z_.]*)$)")

    expr_filter = r"[\+\-\*\(\)]"

    expr_vars = re.sub(expr_filter, " ", obj_expr).split()
    
    #print ( "Checking Release Objects: " + str(expr_vars) + " in " + str([k for k in obj_list]) )

    if not obj_expr:
        status = "Object name error"

    for var in expr_vars:
        #print ( "Checking " + str(var) )
        m = re.match(obj_reg_filter, var)
        if m is None:
            #print ( "Match returned None" )
            status = "Object name error: %s" % (var)
            #print ( status )
            break
        else:
            #print ( "Match returned " + str(m) )
            if m.group("obj_reg") is not None:
                obj_name = m.group("obj_name")
                reg_name = m.group("reg_name")
                if not obj_name in obj_list or obj_list[obj_name].status:
                    status = "Undefined/illegal object: %s" % (obj_name)
                    #print ( status )
                    break
                obj = scn.objects[obj_name]
                if reg_name != "ALL":
                    if (not obj.mcell.regions.region_list or 
                            reg_name not in obj.mcell.regions.region_list):
                        status = "Undefined region: %s" % (reg_name)
                        #print ( status )
                        break
            else:
                obj_name = m.group("obj_name_only")
                if not obj_name in obj_list or obj_list[obj_name].status:
                    status = "Undefined/illegal object: %s" % (obj_name)
                    #print ( status )
                    break

    return status




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
        context.scene.mcell.release_sites.draw_panel ( context, self )



class MCellPointItemPropertyGroup(bpy.types.PropertyGroup):
    x = FloatProperty ( name="X", default=0.0, precision=7 )
    y = FloatProperty ( name="Y", default=0.0, precision=7 )
    z = FloatProperty ( name="Z", default=0.0, precision=7 )

    def build_data_model_from_properties ( self, context ):
        return [ self.x, self.y, self.z ]


class MCell_Point_List_OT_point_add(bpy.types.Operator):
    bl_idname = "mcellptlist.point_add"
    bl_label = "Add Point"
    bl_description = "Add a new point to the list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rs = context.scene.mcell.release_sites
        rs.mol_release_list[rs.active_release_index].add_point(context)
        return {'FINISHED'}


class MCell_Point_List_OT_point_add_cursor(bpy.types.Operator):
    bl_idname = "mcellptlist.point_add_cursor"
    bl_label = "Add Point at Cursor"
    bl_description = "Add a new point to the list at location of 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor = context.scene.cursor_location
        rs = context.scene.mcell.release_sites
        rs.mol_release_list[rs.active_release_index].add_point(context,x=cursor.x,y=cursor.y,z=cursor.z)
        return {'FINISHED'}


class MCell_Point_List_OT_point_add_obj_sel(bpy.types.Operator):
    bl_idname = "mcellptlist.point_add_obj_sel"
    bl_label = "Add Selected Points from Object"
    bl_description = "Add all selected points from all selected objects (Object Mode Only)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cursor = context.scene.cursor_location
        rs = context.scene.mcell.release_sites
        pl = rs.mol_release_list[rs.active_release_index]

        for data_object in context.scene.objects:
            if data_object.type == 'MESH':
                if data_object.select:
                    print ( " Selected object: " + data_object.name )

                    saved_hide_status = data_object.hide
                    data_object.hide = False

                    context.scene.objects.active = data_object
                    bpy.ops.object.mode_set(mode='OBJECT')

                    loc_x = data_object.location.x
                    loc_y = data_object.location.y
                    loc_z = data_object.location.z

                    mesh = data_object.data
                    matrix = data_object.matrix_world
                    vertices = mesh.vertices
                    for v in vertices:
                        if v.select:
                            t_vec = matrix * v.co
                            #pl.add_point(context, x=t_vec.x+loc_x, y=t_vec.y+loc_y, z=t_vec.z+loc_z )
                            pl.add_point(context, x=t_vec.x, y=t_vec.y, z=t_vec.z )

                    data_object.hide = saved_hide_status

        return {'FINISHED'}



class MCell_Point_List_OT_point_remove(bpy.types.Operator):
    bl_idname = "mcellptlist.point_remove"
    bl_label = "Remove point"
    bl_description = "Remove selected point from the list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rs = context.scene.mcell.release_sites
        rs.mol_release_list[rs.active_release_index].remove_active_point(context)
        return {'FINISHED'}

class MCell_Point_List_OT_point_remove_all(bpy.types.Operator):
    bl_idname = "mcellptlist.point_remove_all"
    bl_label = "Remove All"
    bl_description = "Remove all points from the list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rs = context.scene.mcell.release_sites
        rs.mol_release_list[rs.active_release_index].remove_all_points(context)
        return {'FINISHED'}


class MCell_PointList_UL(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row()
        col = row.column()
        col.label ( "Point:" )
        col = row.column()
        col.prop ( item, 'x' )
        col = row.column()
        col.prop ( item, 'y' )
        col = row.column()
        col.prop ( item, 'z' )




class MCellMoleculeReleaseProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Site Name", default="Release_Site",
        description="The name of the release site",
        update=check_release_site)
    molecule = StringProperty(
        name="Molecule",
        description="The molecule to release",
        update=check_release_site)
    shape_enum = [
        ('CUBIC', 'Cubic', ''),
        ('SPHERICAL', 'Spherical', ''),
        ('SPHERICAL_SHELL', 'Spherical Shell', ''),
        ('LIST', 'List', ''),
        ('OBJECT', 'Object/Region', '')]
    shape = EnumProperty(
        items=shape_enum, name="Release Shape",
        description="Release in the specified shape. Surface molecules can only use Object/Region.",
        update=check_release_site)
    orient_enum = [
        ('\'', "Top Front", ""),
        (',', "Top Back", ""),
        (';', "Mixed", "")]
    orient = bpy.props.EnumProperty(
        items=orient_enum, name="Initial Orientation",
        description="Release surface molecules with the specified initial "
                    "orientation.")
    object_expr = StringProperty(
        name="Object/Region",
        description="Release in/on the specified object/region.",
        update=check_release_site)
        
    location_x = PointerProperty ( name="Relese Loc X", type=parameter_system.Parameter_Reference )
    location_y = PointerProperty ( name="Relese Loc Y", type=parameter_system.Parameter_Reference )
    location_z = PointerProperty ( name="Relese Loc Z", type=parameter_system.Parameter_Reference )
    
    points_list = CollectionProperty ( type=MCellPointItemPropertyGroup )
    active_point_index = IntProperty(name="Active Point Index", default=0)

    diameter = PointerProperty ( name="Site Diameter", type=parameter_system.Parameter_Reference )
    probability = PointerProperty ( name="Release Probability", type=parameter_system.Parameter_Reference )

    quantity_type_enum = [
        ('NUMBER_TO_RELEASE', "Constant Number", ""),
        ('GAUSSIAN_RELEASE_NUMBER', "Gaussian Number", ""),
        ('DENSITY', "Concentration/Density", "")]
    quantity_type = EnumProperty(items=quantity_type_enum,
                                 name="Quantity Type")

    quantity = PointerProperty ( name="Quantity to Release", type=parameter_system.Parameter_Reference )
    stddev = PointerProperty ( name="Standard Deviation", type=parameter_system.Parameter_Reference )

    pattern = StringProperty(
        name="Release Pattern",
        description="Use the named release pattern. "
                    "If blank, release molecules at start of simulation.")
    status = StringProperty(name="Status")

    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    shape_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    object_expr_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    orient_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    quantity_type_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    mol_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )
    rel_pattern_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )


    def add_point ( self, context, x=0, y=0, z=0 ):
        """ Add a new point to the list of points and set as the active point """
        new_pt = self.points_list.add()
        new_pt.x = x
        new_pt.y = y
        new_pt.z = z
        self.active_point_index = len(self.points_list)-1

    def remove_active_point ( self, context ):
        """ Remove the active point from the list of points """
        self.points_list.remove ( self.active_point_index )
        self.active_point_index -= 1
        if self.active_point_index < 0:
            self.active_point_index = 0

    def remove_all_points ( self, context ):
        """ Remove all points from the list of points """
        while len(self.points_list) > 0:
            self.points_list.remove ( 0 )
        self.active_point_index = 0


    def init_properties ( self, parameter_system ):
        # self.name = "Release_Site_"+str(mcell.release_sites.allocate_available_id())
        self.molecule = ""
        self.shape = 'SPHERICAL'
        self.orient = '\''
        self.object_expr = ""
       
        self.location_x.init_ref  ( parameter_system,  user_name="Release Location X",  user_expr="0", user_units="", user_descr="The center of the release site's X coordinate.\nOnly used for geometrical shapes." )
        self.location_y.init_ref  ( parameter_system,  user_name="Release Location Y",  user_expr="0", user_units="", user_descr="The center of the release site's Y coordinate\nOnly used for geometrical shapes." )
        self.location_z.init_ref  ( parameter_system,  user_name="Release Location Z",  user_expr="0", user_units="", user_descr="The center of the release site's Z coordinate\nOnly used for geometrical shapes." )
        self.diameter.init_ref    ( parameter_system,  user_name="Site Diameter",       user_expr="0", user_units="", user_descr="Release molecules uniformly within a diameter d.\nNot used for releases on regions." )
        self.probability.init_ref ( parameter_system,  user_name="Release Probability", user_expr="1", user_units="", user_descr="This release does not have to occur every time, but rather with probability p.\nEither the whole release occurs or none of it does;\nthe probability does not apply molecule-by-molecule.\np must be in the interval [0;1]." )

        helptext = "Quantity of Molecules to release at this site." + \
                "\n" + \
                "When Quantity Type is Constant Number:\n" + \
                "  Release n molecules. For releases on regions, n can be negative, and\n" + \
                "  the release will then remove molecules of that type from the region. To\n" + \
                "  remove all molecules of a type, just make n large and negative. It is\n" + \
                "  unwise to both add and remove molecules on the same timestep—the\n" + \
                "  order of addition and removal is not defined in that case. This directive\n" + \
                "  is not used for the LIST shape, as every molecule is specified.\n" + \
                "  Concentration units: molar. Density units: molecules per square micron\n" + \
                "\n" + \
                "When Quantity Type is Gaussian Number:\n" + \
                "  Defines the mean of the Quantity of molecules to be released.\n" + \
                "\n" + \
                "When Quantity Type is Concentration / Density:\n" + \
                "  Release molecules at concentration c molar for volumes and d\n" + \
                "  molecules per square micron for surfaces. Neither can be used\n" + \
                "  for the LIST shape; DENSITY is only valid for regions."
        self.quantity.init_ref    ( parameter_system,  user_name="Quantity to Release", user_expr="",  user_units="", user_descr=helptext )

        helptext = "Standard Deviation of number to release\nwhen Quantity Type is Gaussian Number"
        self.stddev.init_ref      ( parameter_system, user_name="Standard Deviation",  user_expr="0", user_units="", user_descr=helptext )

    def remove_properties ( self, context ):
        print ( "Removing all Molecule Release Site Properties... " )
        ps = context.scene.mcell.parameter_system
        self.remove_all_points ( context )
        self.location_x.clear_ref ( ps )
        self.location_y.clear_ref ( ps )
        self.location_z.clear_ref ( ps )
        self.diameter.clear_ref ( ps )
        self.probability.clear_ref ( ps )
        self.quantity.clear_ref ( ps )
        self.stddev.clear_ref ( ps )

    def build_data_model_from_properties ( self, context ):
        r = self
        r_dict = {}
        r_dict['data_model_version'] = "DM_2015_11_11_1717"
        r_dict['name'] = r.name
        r_dict['molecule'] = r.molecule
        r_dict['shape'] = r.shape
        r_dict['orient'] = r.orient
        r_dict['object_expr'] = r.object_expr
        r_dict['location_x'] = r.location_x.get_expr()
        r_dict['location_y'] = r.location_y.get_expr()
        r_dict['location_z'] = r.location_z.get_expr()
        r_dict['site_diameter'] = r.diameter.get_expr()
        r_dict['release_probability'] = r.probability.get_expr()
        r_dict['quantity_type'] = str(r.quantity_type)
        r_dict['quantity'] = r.quantity.get_expr()
        r_dict['stddev'] = r.stddev.get_expr()
        r_dict['pattern'] = str(r.pattern)
        points_list = []
        for p in r.points_list:
            points_list.append ( p.build_data_model_from_properties(context) )
        r_dict['points_list'] = points_list
        return r_dict



    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculeReleaseProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] == "DM_2014_10_24_1638":
            # Make changes to move from DM_2014_10_24_1638 to DM_2015_11_11_1717
            # Added a "points_list" list of points
            dm['points_list'] = []
            dm['data_model_version'] = "DM_2015_11_11_1717"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_11_11_1717":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleaseProperty data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm_dict ):

        if dm_dict['data_model_version'] != "DM_2015_11_11_1717":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleaseProperty data model to current version." )

        self.name = dm_dict["name"]
        self.molecule = dm_dict["molecule"]
        if "shape" in dm_dict: self.shape = dm_dict["shape"]
        if "orient" in dm_dict: self.orient = dm_dict["orient"]
        if "object_expr" in dm_dict: self.object_expr = dm_dict["object_expr"]
        if "location_x" in dm_dict: self.location_x.set_expr ( dm_dict["location_x"] )
        if "location_y" in dm_dict: self.location_y.set_expr ( dm_dict["location_y"] )
        if "location_z" in dm_dict: self.location_z.set_expr ( dm_dict["location_z"] )
        if "site_diameter" in dm_dict: self.diameter.set_expr ( dm_dict["site_diameter"] )
        if "release_probability" in dm_dict: self.probability.set_expr ( dm_dict["release_probability"] )
        if "quantity_type" in dm_dict: self.quantity_type = dm_dict["quantity_type"]
        if "quantity" in dm_dict: self.quantity.set_expr ( dm_dict["quantity"] )
        if "stddev" in dm_dict: self.stddev.set_expr ( dm_dict["stddev"] )
        if "pattern" in dm_dict: self.pattern = dm_dict["pattern"]
        if "points_list" in dm_dict:
            for p in dm_dict['points_list']:
                self.add_point ( context, p[0], p[1], p[2] )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )



class MCellMoleculeReleasePropertyGroup(bpy.types.PropertyGroup):
    mol_release_list = CollectionProperty(
        type=MCellMoleculeReleaseProperty, name="Molecule Release List")
    active_release_index = IntProperty(name="Active Release Index", default=0)
    next_id = IntProperty(name="Counter for Unique Release Site IDs", default=1)  # Start ID's at 1 to confirm initialization


    def allocate_available_id ( self ):
        """ Return a unique release ID for a new release site """
        if len(self.mol_release_list) <= 0:
            # Reset the ID to 1 when there are no more sites
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def add_release_site ( self, context ):
        mcell = context.scene.mcell
        rel_id = self.allocate_available_id()  # Get the ID before allocating to allow it to reset
        self.mol_release_list.add()
        self.active_release_index = len(self.mol_release_list)-1
        self.mol_release_list[self.active_release_index].name = "Release_Site_"+str(rel_id)

        relsite = self.mol_release_list[self.active_release_index]

        relsite.init_properties(mcell.parameter_system)

        if mcell.cellblender_preferences.bionetgen_mode:
            # Perform BioNetGen Checking
            pass
        else:
            # Perform MCell Checking
            check_release_molecule(context)


    def remove_active_rel_site ( self, context ):
        """ Remove the active release site from the list of release sites """
        print ( "Call to: \"remove_active_rel_site\"" )
        if len(self.mol_release_list) > 0:
            rel = self.mol_release_list[self.active_release_index]
            if rel:
                rel.remove_properties(context)
            self.mol_release_list.remove ( self.active_release_index )
            self.active_release_index -= 1
            if self.active_release_index < 0:
                self.active_release_index = 0
            if len(self.mol_release_list) <= 0:
                self.next_id = 1
            if mcell.cellblender_preferences.bionetgen_mode:
                # Perform BioNetGen Checking
                pass
            else:
                # Perform MCell Checking
                if self.mol_release_list:
                    check_release_site(self, context)


    def build_data_model_from_properties ( self, context ):
        print ( "Release Site List building Data Model" )
        rel_site_dm = {}
        rel_site_dm['data_model_version'] = "DM_2014_10_24_1638"
        rel_site_list = []
        for r in self.mol_release_list:
            rel_site_list.append ( r.build_data_model_from_properties(context) )
        rel_site_dm['release_site_list'] = rel_site_list
        return rel_site_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMoleculeReleasePropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleasePropertyGroup data model to current version." )
            return None

        if "release_site_list" in dm:
            for item in dm["release_site_list"]:
                if MCellMoleculeReleaseProperty.upgrade_data_model ( item ) == None:
                    return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Upgrade the data model as needed
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMoleculeReleasePropertyGroup data model to current version." )

        while len(self.mol_release_list) > 0:
            self.mol_release_list.remove(0)
        if "release_site_list" in dm:
            for r in dm["release_site_list"]:
                self.mol_release_list.add()
                self.active_release_index = len(self.mol_release_list)-1
                rs = self.mol_release_list[self.active_release_index]
                rs.init_properties(context.scene.mcell.parameter_system)
                rs.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Release Properties..." )
        for item in self.mol_release_list:
            item.remove_properties(context)
        self.mol_release_list.clear()
        self.active_release_index = 0
        print ( "Done removing all Molecule Release Properties." )



    def draw_layout ( self, context, layout ):
        """ Draw the release "panel" within the layout """
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            row = layout.row()
            if not mcell.molecules.molecule_list:
                row.label(text="Define at least one molecule", icon='ERROR')
            else:
                row.label(text="Release/Placement Sites:",
                          icon='FORCE_LENNARDJONES')
                row = layout.row()
                col = row.column()
                col.template_list("MCELL_UL_check_molecule_release",
                                  "molecule_release", self,
                                  "mol_release_list", self,
                                  "active_release_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.release_site_add", icon='ZOOMIN', text="")
                col.operator("mcell.release_site_remove", icon='ZOOMOUT', text="")

                if len(self.mol_release_list) > 0:
                    rel = self.mol_release_list[self.active_release_index]

                    helptext = "This field specifies the name for this release site\n" + \
                               " \n" + \
                               "A Release Site specifies:\n" + \
                               "     -  A molecule species to be released\n" + \
                               "     -  The location/orientation of the release\n" + \
                               "     -  The probability of the release\n" + \
                               "     -  The quantity to be released\n" + \
                               "     -  The timing of the release\n" + \
                               " \n" + \
                               "Location/Orientation of Release:\n" + \
                               "    Location is controlled by the Release Shape field.\n" + \
                               "    When the shape is a geometric shape, the location is explicit.\n" + \
                               "    When the shape is an Object or Region, the location is implicit.\n" + \
                               "    Initial Orientation is available for Surface Molecules only.\n" + \
                               " \n" + \
                               "Probability of Release:\n" + \
                               "    Probability controls the likelihood that the release will actually happen.\n" + \
                               " \n" + \
                               "Quantity to Release:\n" + \
                               "    The quantity to be released can be:\n" + \
                               "     -  A constant number to be released\n" + \
                               "     -  A random number chosen from a Gaussian distribution\n" + \
                               "     -  A concentration / density\n" + \
                               " \n" + \
                               "Timing of Release:\n" + \
                               "    The timing of releases is controlled by the Release Pattern.\n" + \
                               "    The release pattern field allows selection of:\n" + \
                               "           -  Explicitly defined timing patterns (Release Patterns Panel)\n" + \
                               "           -  Named reactions (Reactions Panel)"
                    ps.draw_prop_with_help ( layout, "Site Name:", rel, "name", "name_show_help", rel.name_show_help, helptext )
                    #layout.prop(rel, "name")

                    helptext = "Molecule to Release\n" + \
                               "Selects the molecule to be released at this site."
                    if mcell.cellblender_preferences.bionetgen_mode:
                        ps.draw_prop_with_help ( layout, "Molecule:", rel, "molecule", "mol_show_help", rel.mol_show_help, helptext )
                    else:
                        ps.draw_prop_search_with_help ( layout, "Molecule:", rel, "molecule", mcell.molecules, "molecule_list", "mol_show_help", rel.mol_show_help, helptext )
                        #layout.prop_search ( rel, "molecule", mcell.molecules, "molecule_list", text="Molecule", icon='FORCE_LENNARDJONES')

                    if rel.molecule in mcell.molecules.molecule_list:
                        label = mcell.molecules.molecule_list[rel.molecule].bnglLabel
                        row = layout.row(align=True)
                        row.label(text="BNGL label: {0}".format(label), icon='BLANK1')

                        if mcell.molecules.molecule_list[rel.molecule].type == '2D':
                            #layout.prop(rel, "orient")
                            ps.draw_prop_with_help ( layout, "Initial Orientation:", rel, "orient", "orient_show_help", rel.orient_show_help,
                                "Initial Orientation\n" + \
                                "Determines how surface molecules are orginally placed in the surface:\n" + \
                                "  Top Front\n" + \
                                "  Top Back\n" + \
                                "  Mixed\n" )

                    helptext = "Release Site Shape\n" + \
                               "Defines the shape of the release site. A shape may be:\n" + \
                               "  A list of locations.\n" + \
                               "  A geometric cubic region.\n" + \
                               "  A geometric spherical region.\n" + \
                               "  A geometric spherical shell region.\n" + \
                               "  A CellBlender/MCell Object or Region\n" + \
                               " \n" + \
                               "When the release site shape is \"List\", CellBlender provides\n" + \
                               "a mechanism to add points to the list.\n" + \
                               " \n" + \
                               "When the release site shape is one of the predefined geometric\n" + \
                               "shapes, CellBlender will provide fields for its location and size.\n" + \
                               " \n" + \
                               "When the release site shape is \"Object/Region\", CellBlender will expect\n" + \
                               "an MCell specification for one of the Objects or Regions defined in\n" + \
                               "your current model (via the \"Model Objects\" panel). For example, if\n" + \
                               "you have an object named \"Cube\", you would enter that name in the\n" + \
                               "Object/Region field. If you've defined a surface region named \"top\"\n" + \
                               "on your Cube, then you would specify that surface as \"Cube[top]\"."


                    ps.draw_prop_with_help ( layout, "Release Shape:", rel, "shape", "shape_show_help", rel.shape_show_help, helptext )

                    if ((rel.shape == 'CUBIC') | (rel.shape == 'SPHERICAL') |
                            (rel.shape == 'SPHERICAL_SHELL')):
                        #layout.prop(rel, "location")
                        rel.location_x.draw(layout,ps)
                        rel.location_y.draw(layout,ps)
                        rel.location_z.draw(layout,ps)
                        rel.diameter.draw(layout,ps)


                    if (rel.shape == 'LIST'):
                        row = layout.row()
                        col = row.column()

                        col.template_list("MCell_PointList_UL", "", rel, "points_list", rel, "active_point_index", rows=5, maxrows=20)

                        col = row.column(align=True)
                        col.operator("mcellptlist.point_add", icon='ZOOMIN', text="")
                        col.operator("mcellptlist.point_remove", icon='ZOOMOUT', text="")
                        col.separator()
                        col.operator("mcellptlist.point_add_cursor", icon='CURSOR', text="")
                        col.operator("mcellptlist.point_add_obj_sel", icon='EDITMODE_HLT', text="")

                        col.separator()
                        col.operator("mcellptlist.point_remove_all", icon='X_VEC', text="")


                    if (rel.shape == 'LIST'):
                        rel.diameter.draw(layout,ps,label="Search Distance")

                    if rel.shape == 'OBJECT':
                        helptext = "Release Site Object/Region\n" + \
                                   "This field requires an MCell-compatible object expression or region\n" + \
                                   "expression for one of the objects or regions defined in your current\n" + \
                                   "CellBlender model (via the \"Model Objects\" panel). For example, if\n" + \
                                   "you have an object named \"Cube\", you would enter that name in the\n" + \
                                   "Object/Region field. If you've defined a surface region named \"top\"\n" + \
                                   "on your Cube, then you would specify that surface as \"Cube[top]\"."
                        ps.draw_prop_with_help ( layout, "Object/Region:", rel, "object_expr", "object_expr_show_help", rel.object_expr_show_help, helptext )

                    rel.probability.draw(layout,ps)
            
                    if (rel.shape != 'LIST'):

                        helptext = "Quantity Type\n" + \
                                   "Defines the meaning of the Quantity:\n" + \
                                   "  Constant Number\n" + \
                                   "  Gaussian Number\n" + \
                                   "  Concentration / Density\n" + \
                                   " \n" + \
                                   "The value of this field determines the interpretation of the\n" + \
                                   "Quantity to Release field below."
                        ps.draw_prop_with_help ( layout, "Quantity Type:", rel, "quantity_type", "quantity_type_show_help", rel.quantity_type_show_help, helptext )

                        rel.quantity.draw(layout,ps)

                        if rel.quantity_type == 'GAUSSIAN_RELEASE_NUMBER':
                            rel.stddev.draw(layout,ps)

                    # We use release_pattern_rxn_name_list instead of
                    # release_pattern_list here, because we want to be able to
                    # assign either reaction names or release patterns to this
                    # field. This parallels exactly how it works in MCell.
                    #
                    #layout.prop_search(rel, "pattern", mcell.release_patterns,  # mcell.release_patterns is of type MCellReleasePatternPropertyGroup
                    #                   "release_pattern_rxn_name_list",  
                    #                   icon='FORCE_LENNARDJONES')

                    helptext = "Release Pattern\n" + \
                               "Selects a release pattern to follow or a named reaction to trigger releases.\n" + \
                               " \n" + \
                               "The Release Pattern generally controls the timing of release events.\n" + \
                               "This is either done with explicit timing parameters defined in the\n" + \
                               "Release Patterns panel or implicit timing by specifying reactions that\n" + \
                               "trigger releases. When reactions are used, the release generally happens\n" + \
                               "at a location relative to the reaction itself."
                    #layout.prop_search ( rel, "molecule", mcell.molecules, "molecule_list", text="Molecule", icon='FORCE_LENNARDJONES')
                    ps.draw_prop_search_with_help ( layout, "Release Pattern:", rel, "pattern", mcell.release_patterns, "release_pattern_rxn_name_list", "rel_pattern_show_help", rel.rel_pattern_show_help, helptext, 'TIME' )




    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



########################################################
#
#   Release Pattern Code
#
########################################################

class MCELL_OT_release_pattern_add(bpy.types.Operator):
    bl_idname = "mcell.release_pattern_add"
    bl_label = "Add Release Pattern"
    bl_description = "Add a new Release Pattern to an MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.release_patterns.add_release_pattern ( context )
        return {'FINISHED'}


class MCELL_OT_release_pattern_remove(bpy.types.Operator):
    bl_idname = "mcell.release_pattern_remove"
    bl_label = "Remove Release Pattern"
    bl_description = "Remove selected Release Pattern from MCell model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.release_patterns.remove_active_rel_pattern ( context )
        self.report({'INFO'}, "Deleted Release Pattern")
        return {'FINISHED'}




def update_release_pattern_rxn_name_list():
    """ Update lists needed to count rxns and use rel patterns. """

    mcell = bpy.context.scene.mcell
    mcell.reactions.reaction_name_list.clear()
    mcell.release_patterns.release_pattern_rxn_name_list.clear()
    rxns = mcell.reactions.reaction_list
    rel_patterns_rxns = mcell.release_patterns.release_pattern_rxn_name_list
    # If a reaction has a reaction name, save it in reaction_name_list for
    # counting in "Reaction Output Settings." Also, save reaction names in
    # release_pattern_rxn_name_list for use as a release pattern, which is
    # assigned in "Molecule Release/Placement"
    for rxn in rxns:
        if rxn.rxn_name and not rxn.status:
            new_rxn_item = mcell.reactions.reaction_name_list.add()
            new_rxn_item.name = rxn.rxn_name
            new_rel_pattern_item = rel_patterns_rxns.add()
            new_rel_pattern_item.name = rxn.rxn_name

    rel_patterns = mcell.release_patterns.release_pattern_list
    for rp in rel_patterns:
        if not rp.status:
            new_rel_pattern_item = rel_patterns_rxns.add()
            new_rel_pattern_item.name = rp.name



def check_release_pattern_name(self, context):
    """Checks for duplicate or illegal release pattern name."""

    mcell = context.scene.mcell
    rel_pattern_list = mcell.release_patterns.release_pattern_list
    rel_pattern = rel_pattern_list[
        mcell.release_patterns.active_release_pattern_index]

    status = ""

    # Check for duplicate release pattern name
    rel_pattern_keys = rel_pattern_list.keys()
    if rel_pattern_keys.count(rel_pattern.name) > 1:
        status = "Duplicate release pattern: %s" % (rel_pattern.name)

    # Check for illegal names (Starts with a letter. No special characters.)
    rel_pattern_filter = r"(^[A-Za-z]+[0-9A-Za-z_.]*$)"
    m = re.match(rel_pattern_filter, rel_pattern.name)
    if m is None:
        status = "Release Pattern name error: %s" % (rel_pattern.name)

    rel_pattern.status = status
    update_release_pattern_rxn_name_list()



class MCELL_UL_check_release_pattern(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_release_pattern(bpy.types.Panel):
    bl_label = "CellBlender - Release Pattern"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.release_patterns.draw_panel ( context, self )





class MCellReleasePatternProperty(bpy.types.PropertyGroup):
    name = StringProperty(
        name="Pattern Name", default="Release_Pattern",
        description="The name of the release site",
        update=check_release_pattern_name)

    delay            = PointerProperty ( name="Release Pattern Delay", type=parameter_system.Parameter_Reference )
    release_interval = PointerProperty ( name="Relese Interval",       type=parameter_system.Parameter_Reference )
    train_duration   = PointerProperty ( name="Train Duration",        type=parameter_system.Parameter_Reference )
    train_interval   = PointerProperty ( name="Train Interval",        type=parameter_system.Parameter_Reference )
    number_of_trains = PointerProperty ( name="Number of Trains",      type=parameter_system.Parameter_Reference )

    status = StringProperty(name="Status")

    name_show_help = BoolProperty ( default=False, description="Toggle more information about this parameter" )

    def init_properties ( self, parameter_system ):
        self.name = "Release_Pattern"
        helptext = ""
        self.delay.init_ref            ( parameter_system,  user_name="Release Pattern Delay", user_expr="0",     user_units="s", user_descr="The time at which the release pattern will start.\nDefault is at time zero." )
        self.release_interval.init_ref ( parameter_system,  user_name="Relese Interval",       user_expr="",      user_units="s", user_descr="During a train of releases, release molecules after every t seconds.\nDefault is release only once (t is infinite)." )
        self.train_duration.init_ref   ( parameter_system,  user_name="Train Duration",        user_expr="",      user_units="s", user_descr="The duration of the train before turning off.\nDefault is to never turn off." )
        self.train_interval.init_ref   ( parameter_system,  user_name="Train Interval",        user_expr="",      user_units="s", user_descr="A new train happens every interval.\nDefault is no new trains.\nThe train interval must not be shorter than the train duration." )
        self.number_of_trains.init_ref ( parameter_system,  user_name="Number of Trains",      user_expr="1",     user_units="",  user_descr="Repeat the release process for this number of trains of releases.\nDefault is one train.", user_int=True )

    def remove_properties ( self, context ):
        print ( "Removing all Release Pattern Properties... no collections to remove." )
        ps = context.scene.mcell.parameter_system
        self.delay.clear_ref ( ps )
        self.release_interval.clear_ref ( ps )
        self.train_duration.clear_ref ( ps )
        self.train_interval.clear_ref ( ps )
        self.number_of_trains.clear_ref ( ps )


    def build_data_model_from_properties ( self, context ):
        r = self
        r_dict = {}
        r_dict['data_model_version'] = "DM_2014_10_24_1638"
        r_dict['name'] = r.name
        r_dict['delay'] = r.delay.get_expr()
        r_dict['release_interval'] = r.release_interval.get_expr()
        r_dict['train_duration'] = r.train_duration.get_expr()
        r_dict['train_interval'] = r.train_interval.get_expr()
        r_dict['number_of_trains'] = r.number_of_trains.get_expr()
        return r_dict


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReleasePatternProperty Data Model" )

        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternProperty data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm_dict ):

        if dm_dict['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternProperty data model to current version." )

        self.name = dm_dict["name"]
        self.delay.set_expr ( dm_dict["delay"] )
        self.release_interval.set_expr ( dm_dict["release_interval"] )
        self.train_duration.set_expr ( dm_dict["train_duration"] )
        self.train_interval.set_expr ( dm_dict["train_interval"] )
        self.number_of_trains.set_expr ( dm_dict["number_of_trains"] )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )



#Custom Properties

class RelStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell String Property with name \"" + self.name + "\" ... no collections to remove." )
        pass



class MCellReleasePatternPropertyGroup(bpy.types.PropertyGroup):
    release_pattern_list = CollectionProperty ( type=MCellReleasePatternProperty, name="Release Pattern List" )
    # Contains release patterns AND reaction names. Used in "Release Placement"
    release_pattern_rxn_name_list = CollectionProperty ( type=RelStringProperty, name="Release Pattern and Reaction Name List")
    active_release_pattern_index = IntProperty ( name="Active Release Pattern Index", default=0 )
    next_id = IntProperty(name="Counter for Unique Release Pattern IDs", default=1)  # Start ID's at 1 to confirm initialization


    def allocate_available_id ( self ):
        """ Return a unique release ID for a new release pattern """
        if len(self.release_pattern_list) <= 0:
            # Reset the ID to 1 when there are no more sites
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    def add_release_pattern ( self, context ):
        mcell = context.scene.mcell
        pat_id = self.allocate_available_id()  # Get the ID before allocating to allow it to reset
        self.release_pattern_list.add()
        self.active_release_pattern_index = len(self.release_pattern_list)-1
        rel_pattern = self.release_pattern_list[self.active_release_pattern_index]
        rel_pattern.init_properties(mcell.parameter_system)
        rel_pattern.name = "Release_Pattern_"+str(pat_id)
        check_release_pattern_name(self, context)


    def remove_active_rel_pattern ( self, context ):
        """ Remove the active release pattern from the list of release pattern """
        print ( "Call to: \"remove_active_rel_pattern\"" )
        if len(self.release_pattern_list) > 0:
            pat = self.release_pattern_list[self.active_release_pattern_index]
            if pat:
                pat.remove_properties(context)
            self.release_pattern_list.remove(self.active_release_pattern_index)
            self.active_release_pattern_index -= 1
            if (self.active_release_pattern_index < 0):
                self.active_release_pattern_index = 0
            if len(self.release_pattern_list) <= 0:
                self.next_id = 1
            if self.release_pattern_list:
                check_release_pattern_name(self, context)
            else:
                update_release_pattern_rxn_name_list()



    def build_data_model_from_properties ( self, context ):
        print ( "Release Pattern List building Data Model" )
        rel_pat_dm = {}
        rel_pat_dm['data_model_version'] = "DM_2014_10_24_1638"
        rel_pat_list = []
        for r in self.release_pattern_list:
            rel_pat_list.append ( r.build_data_model_from_properties(context) )
        rel_pat_dm['release_pattern_list'] = rel_pat_list
        return rel_pat_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellReleasePatternPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternPropertyGroup data model to current version." )
            return None

        group_name = "release_pattern_list"
        if group_name in dm:
            l = dm[group_name]
            for ri in range(len(l)):
                l[ri] = MCellReleasePatternProperty.upgrade_data_model ( l[ri] )
                if l[ri] == None:
                  return None
        return dm


    def build_properties_from_data_model ( self, context, dm ):

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellReleasePatternPropertyGroup data model to current version." )

        while len(self.release_pattern_list) > 0:
            self.release_pattern_list.remove(0)
        if "release_pattern_list" in dm:
            for r in dm["release_pattern_list"]:
                self.release_pattern_list.add()
                self.active_release_pattern_index = len(self.release_pattern_list)-1
                rp = self.release_pattern_list[self.active_release_pattern_index]
                rp.init_properties(context.scene.mcell.parameter_system)
                rp.build_properties_from_data_model ( context, r )

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Release Pattern Properties..." )
        for item in self.release_pattern_list:
            item.remove_properties(context)
        self.release_pattern_list.clear()
        for item in self.release_pattern_rxn_name_list:
            item.remove_properties(context)
        self.release_pattern_rxn_name_list.clear()
        self.active_release_pattern_index = 0
        print ( "Done removing all Release Pattern Properties." )


    def draw_layout ( self, context, layout ):
        """ Draw the release "panel" within the layout """
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
          ps = mcell.parameter_system

          row = layout.row()
          col = row.column()
          col.template_list("MCELL_UL_check_release_pattern",
                              "release_pattern", mcell.release_patterns,
                              "release_pattern_list", mcell.release_patterns,
                              "active_release_pattern_index", rows=2)
          col = row.column(align=True)
          col.operator("mcell.release_pattern_add", icon='ZOOMIN', text="")
          col.operator("mcell.release_pattern_remove", icon='ZOOMOUT', text="")
          if mcell.release_patterns.release_pattern_list:
              rel_pattern = mcell.release_patterns.release_pattern_list[
                  mcell.release_patterns.active_release_pattern_index]


              helptext = "This field specifies the name for this release pattern\n" + \
                         " \n" + \
                         "A Release Pattern is a timing pattern (not a spatial pattern).\n" + \
                         " \n" + \
                         "A Release Pattern is generated from these parameters:\n" + \
                         "     -  Release Pattern Delay\n" + \
                         "     -  Release Interval\n" + \
                         "     -  Train Duration\n" + \
                         "     -  Train Interval\n" + \
                         "     -  Number of Trains"
              ps.draw_prop_with_help ( layout, "Pattern Name:", rel_pattern, "name", "name_show_help", rel_pattern.name_show_help, helptext )
              #layout.prop(rel_pattern, "name")


              rel_pattern.delay.draw(layout,ps)
              rel_pattern.release_interval.draw(layout,ps)
              rel_pattern.train_duration.draw(layout,ps)
              rel_pattern.train_interval.draw(layout,ps)
              rel_pattern.number_of_trains.draw(layout,ps)


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )

