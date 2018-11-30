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
This file contains the classes for CellBlender's Molecule Visualization.

"""

import cellblender

# blender imports
import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
#import mathutils

# python imports
import mathutils
import array
import glob
import os
import random
import re
import json

# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_release
from . import cellblender_utils

from cellblender.cellblender_utils import timeline_view_all
from cellblender.cellblender_utils import mcell_files_path


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


# Mol Viz Operators:


global_mol_file_list = []


def create_color_list():
    """ Create a list of colors to be assigned to the glyphs. """ 

    mcell = bpy.context.scene.mcell
    mcell.mol_viz.color_index = 0
    if not mcell.mol_viz.color_list:
        for i in range(8):
            mcell.mol_viz.color_list.add()
        mcell.mol_viz.color_list[0].vec = [0.8, 0.0, 0.0]
        mcell.mol_viz.color_list[1].vec = [0.0, 0.8, 0.0]
        mcell.mol_viz.color_list[2].vec = [0.0, 0.0, 0.8]
        mcell.mol_viz.color_list[3].vec = [0.0, 0.8, 0.8]
        mcell.mol_viz.color_list[4].vec = [0.8, 0.0, 0.8]
        mcell.mol_viz.color_list[5].vec = [0.8, 0.8, 0.0]
        mcell.mol_viz.color_list[6].vec = [1.0, 1.0, 1.0]
        mcell.mol_viz.color_list[7].vec = [0.0, 0.0, 0.0]


# Matrix Form:  Assemble obj2 onto obj1 at location of obj1
def assemble_mat(obj1, obj2):

  # get tform matrices of obj1 and obj2
  m1 = obj1.matrix_world.copy()
  m2 = obj2.matrix_world.copy()

  # compute inverse of tform matrix of obj2
  m2i = m2.inverted_safe()

  # create rotation and translation tform matrix for binding site of assembly
  r = mathutils.Matrix.Rotation(pi/8,4,'Y')
  t = mathutils.Matrix.Translation((0,-2, 0))
  bsm = r*t

  # create complete composite tform matrix for assembly
  assem = m2i*m1*bsm

  # Apply the assembly tform matrix to obj2
  obj2.matrix_world = obj2.matrix_world*assem
  
  


@persistent
def read_viz_data_load_post(context):
    print ( "load post handler: cellblender_mol_viz.read_viz_data_load_post() called" )
    bpy.ops.mcell.read_viz_data()


@persistent
def viz_data_save_post(context):
    # context appears to be None
    print ( "save post handler: cellblender_mol_viz.viz_data_save_post() called" )
    if 'global_mol_file_list' in dir(cellblender.cellblender_mol_viz):
        if len(cellblender.cellblender_mol_viz.global_mol_file_list) > 0:
            # There is a non-empty file list, so check if this file path matches the current viz directory
            print ( "New file name = " + str(bpy.data.filepath) )
            mv = bpy.context.scene.mcell.mol_viz
            if not mv.manual_select_viz_dir:
                print ( "Viz not manually selected" )
                bfn = os.path.abspath(str(bpy.data.filepath))
                mfd = os.path.abspath(str(mv.mol_file_dir))

                print ( "Blend:  " + bfn )
                print ( "Viz:    " + mfd )

                if not mfd.startswith(os.path.splitext(bfn)[0] + "_files" + os.sep + "mcell" + os.sep ):
                    print ( "Paths don't match, so clear mol-viz information" )
                    # This is being saved as a different file than was used to generate the visualization data
                    cellblender.cellblender_mol_viz.global_mol_file_list = []
                    mv.mol_file_dir = ''
                    #  __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})


# Operators can't be callbacks, so we need this function for now.  This is
# temporary until we make importing viz data automatic.
def read_viz_data_callback(self, context):
    # print ( "read_viz_data_callback" )
    bpy.ops.mcell.read_viz_data()


class MCELL_OT_update_data_layout(bpy.types.Operator):
    bl_idname = "mcell.update_data_layout"
    bl_label = "Update Layout Data"
    bl_description = "Update the Data Layout based on most recent run of this project."
    bl_options = {'REGISTER'}

    def execute(self, context):
        # print ( "MCELL_OT_update_data_layout operator" )
        mcell = context.scene.mcell
        mcell.mol_viz.update_data_layout(context)
        return {'FINISHED'}


class MCELL_OT_read_viz_data(bpy.types.Operator):
    bl_idname = "mcell.read_viz_data"
    bl_label = "Read Viz Data"
    bl_description = "Load the molecule visualization data into Blender"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global global_mol_file_list

        # Called when the molecule files are actually to be read (when the
        # "Read Molecule Files" button is pushed or a seed value is selected
        # from the list)

        mcell = context.scene.mcell
        mol_viz = mcell.mol_viz
        choices_list = mol_viz.choices_list

        mol_file_dir = ''

        if mol_viz.manual_select_viz_dir:

          #  mol_file_dir comes from directory already chosen manually
          mol_file_dir = mol_viz.mol_file_dir
          print("manual mol_file_dir: %s" % (mol_file_dir))


        else:

          #  mol_file_dir comes from directory associated with saved .blend file
          mol_viz_top_level_dir = None
          files_path = mcell_files_path()  # This will be the full path from "/"

          # Check to see if the data is in an output_data directory or not

          if os.path.exists(files_path) and 'output_data' in os.listdir(files_path):
            # New "output_data" layout
            # Read the viz data from the first data path in the potential sweep
            f = open ( os.path.join(files_path,"data_layout.json"), 'r' )
            layout_spec = json.loads ( f.read() )
            f.close()
            data_layout = layout_spec['data_layout']
            sub_path = ""
            for level in data_layout:
              if level[0] == '/DIR':
                # This is typically the top level directory
                sub_path = os.path.join ( sub_path, level[1][0] )
              elif level[0] == '/FILE_TYPE':
                # This is typically either "viz_data" or "react_data" ... force "viz_data
                sub_path = os.path.join ( sub_path, 'viz_data', '' )
              elif (level[0] ==  '/SEED'):
                # Seed selection is handled in another part of the application so pass
                pass
              else:
                # This is a parameter sweep subdirectory, use the parameter name and currently selected index
                selected_index = 0
                try:
                  selected_index = choices_list[level[0]]['enum_choice']
                except:
                  pass
                sub_path = os.path.join ( sub_path, level[0] + ("_index_%d" % selected_index) )
            mol_viz_top_level_dir = os.path.join(files_path, sub_path)

          else:
            # Old "non-output_data" layout
            # Force the top level mol_viz directory to be where the .blend file
            # lives plus "viz_data". The seed directories will live underneath it.
            mol_viz_top_level_dir = os.path.join(files_path, "viz_data", "")

          mol_viz_top_level_dir = os.path.relpath(mol_viz_top_level_dir)

          mol_viz_seed_list = glob.glob(os.path.join(mol_viz_top_level_dir, "*"))
          mol_viz_seed_list.sort()

          # Clear the list of seeds (e.g. seed_00001, seed_00002, etc) and the
          # list of files (e.g. my_project.cellbin.0001.dat,
          # my_project.cellbin.0002.dat)
          mol_viz.mol_viz_seed_list.clear()


          # Add all the seed directories to the mol_viz_seed_list collection
          # (seed_00001, seed_00002, etc)
          for mol_viz_seed in mol_viz_seed_list:
              new_item = mol_viz.mol_viz_seed_list.add()
              new_item.name = os.path.basename(mol_viz_seed)

          if mol_viz.mol_viz_seed_list:
              # If you previously had some viz data loaded, but reran the
              # simulation with less seeds, you can receive an index error.
              try:
                  active_mol_viz_seed = mol_viz.mol_viz_seed_list[
                      mol_viz.active_mol_viz_seed_index]
              except IndexError:
                  mol_viz.active_mol_viz_seed_index = 0
                  active_mol_viz_seed = mol_viz.mol_viz_seed_list[0]
              mol_file_dir = os.path.join(mol_viz_top_level_dir, active_mol_viz_seed.name)
              mol_file_dir = os.path.relpath(mol_file_dir)

              mol_viz.mol_file_dir = mol_file_dir

#        mol_viz.mol_file_list.clear()

        global_mol_file_list = []
        mol_file_list = []

        if mol_file_dir != '':
          mol_file_list = [ f for f in glob.glob(os.path.join(mol_file_dir, "*")) if not f.endswith(os.sep + "viz_bngl") ]
          print ( "Read found " + str(len(mol_file_list)) + " files" )
          print ( "Last file is " + mol_file_list[len(mol_file_list)-1] )
          mol_file_list.sort()

        if mol_file_list:
          # Add all the viz_data files to global_mol_file_list (e.g.
          # my_project.cellbin.0001.dat, my_project.cellbin.0001.dat, etc)
          for mol_file_name in mol_file_list:
#              new_item = mol_viz.mol_file_list.add()
#              new_item.name = os.path.basename(mol_file_name)
              global_mol_file_list.append(os.path.basename(mol_file_name))

          # If you previously had some viz data loaded, but reran the
          # simulation with less iterations, you can receive an index error.
          try:
#              mol_file = mol_viz.mol_file_list[
#                  mol_viz.mol_file_index]
              mol_file = global_mol_file_list[
                  mol_viz.mol_file_index]
          except IndexError:
              mol_viz.mol_file_index = 0

          create_color_list()
          set_viz_boundaries(context)

          # Set the mol_file_index to match the cursor as closely as possible
          cursor_index = context.scene.frame_current
          if len(mol_file_list) > cursor_index:
            mol_viz.mol_file_index = cursor_index
          elif len(mol_file_list) >= 1:
            mol_viz.mol_file_index = len(mol_file_list) - 1
          else:
            mol_viz.mol_file_index = 0

          try:
              mol_viz_clear(mcell, force_clear=True)
              mol_viz_update(self, context)
          except:
              print( "Unexpected Exception calling mol_viz_update: " + str(sys.exc_info()) )

        return {'FINISHED'}



# Mol Viz callback functions




def set_viz_boundaries( context ):
        global global_mol_file_list

        mcell = context.scene.mcell

#        mcell.mol_viz.mol_file_num = len(mcell.mol_viz.mol_file_list)
        mcell.mol_viz.mol_file_num = len(global_mol_file_list)
        mcell.mol_viz.mol_file_stop_index = mcell.mol_viz.mol_file_num - 1

        #print("Setting frame_start to 0")
        #print("Setting frame_end to ", len(mcell.mol_viz.mol_file_list)-1)
        bpy.context.scene.frame_start = 0
#        bpy.context.scene.frame_end = len(mcell.mol_viz.mol_file_list)-1
        bpy.context.scene.frame_end = len(global_mol_file_list)-1

        timeline_view_all ( context )
        """
        if bpy.context.screen != None:
            for area in bpy.context.screen.areas:
                if area != None:
                    if area.type == 'TIMELINE':
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                ctx = bpy.context.copy()
                                ctx['area'] = area
                                ctx['region'] = region
                                bpy.ops.time.view_all(ctx)
                                break  # It's not clear if this should break or continue ... breaking for now
        """


class MCELL_OT_select_viz_data(bpy.types.Operator):
    bl_idname = "mcell.select_viz_data"
    bl_label = "Read Viz Data"
    bl_description = "Read MCell Molecule Files for Visualization"
    bl_options = {'REGISTER'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
    directory = bpy.props.StringProperty(subtype='DIR_PATH')

    def __init__(self):
        self.directory = bpy.context.scene.mcell.mol_viz.mol_file_dir

    def execute(self, context):
        global global_mol_file_list

        mcell = context.scene.mcell
        
        if (os.path.isdir(self.filepath)):
            mol_file_dir = self.filepath
        else:
            # Strip the file name off of the file path.
            mol_file_dir = os.path.dirname(self.filepath)

        mcell.mol_viz.mol_file_dir = mol_file_dir

        mol_file_list = [ f for f in glob.glob(os.path.join(mol_file_dir, "*")) if not f.endswith(os.sep + "viz_bngl") ]
        print ( "Select found " + str(len(mol_file_list)) + " files" )
        mol_file_list.sort()

        # Reset mol_file_list and mol_viz_seed_list to empty
#        mcell.mol_viz.mol_file_list.clear()
        global_mol_file_list = []

        for mol_file_name in mol_file_list:
#            new_item = mcell.mol_viz.mol_file_list.add()
#            new_item.name = os.path.basename(mol_file_name)
            global_mol_file_list.append(os.path.basename(mol_file_name))

        create_color_list()
        set_viz_boundaries(context)
        mcell.mol_viz.mol_file_index = 0

        mol_viz_update(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        # Called when the file selection panel is requested
        # (when the "Set Molecule Viz Directory" button is pushed)
        print("MCELL_OT_select_viz_data.invoke() called")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class MCELL_OT_mol_viz_set_index(bpy.types.Operator):
    bl_idname = "mcell.mol_viz_set_index"
    bl_label = "Set Molecule File Index"
    bl_description = "Set MCell Molecule File Index for Visualization"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global global_mol_file_list

        mcell = context.scene.mcell
#        if mcell.mol_viz.mol_file_list:
        if global_mol_file_list:
            i = mcell.mol_viz.mol_file_index
            if (i > mcell.mol_viz.mol_file_stop_index):
                i = mcell.mol_viz.mol_file_stop_index
            if (i < mcell.mol_viz.mol_file_start_index):
                i = mcell.mol_viz.mol_file_start_index
            mcell.mol_viz.mol_file_index = i
            # print ( "Set index calling update" )
            mol_viz_update(self, context)
        return{'FINISHED'}



#CellBlender operator helper functions:


@persistent
def frame_change_handler(scn):
    """ Update the viz data every time a frame is changed. """

    mcell = scn.mcell
    curr_frame = mcell.mol_viz.mol_file_index
    if (not curr_frame == scn.frame_current):
        mcell.mol_viz.mol_file_index = scn.frame_current
        bpy.ops.mcell.mol_viz_set_index()
        # Is the following code necessary?
        #if mcell.mol_viz.render_and_save:
        #    scn.render.filepath = "//stores_on/frames/frame_%05d.png" % (
        #        scn.frame_current)
        #    bpy.ops.render.render(write_still=True)


def mol_viz_toggle_manual_select(self, context):
    """ Toggle the option to manually load viz data. """
    global global_mol_file_list

    mcell = context.scene.mcell

    mcell.mol_viz.mol_file_dir = ""
    mcell.mol_viz.mol_file_name = ""
#    mcell.mol_viz.mol_file_list.clear()
    global_mol_file_list = []
    mcell.mol_viz.mol_viz_seed_list.clear()

    if not mcell.mol_viz.manual_select_viz_dir:
        bpy.ops.mcell.read_viz_data()

    mol_viz_clear(mcell)


def get_mol_file_dir():
    """ Get the viz dir """

    mcell = bpy.context.scene.mcell

    # If you previously had some viz data loaded, but reran the
    # simulation with less seeds, you can receive an index error.
    try:
        active_mol_viz_seed = mcell.mol_viz.mol_viz_seed_list[
            mcell.mol_viz.active_mol_viz_seed_index]
    except IndexError:
        mcell.mol_viz.active_mol_viz_seed_index = 0
        active_mol_viz_seed = mcell.mol_viz.mol_viz_seed_list[0]
    filepath = os.path.join(
        mcell_files_path(), "viz_data/%s" % active_mol_viz_seed.name)
    filepath = os.path.relpath(filepath)

    return filepath


def mol_viz_update(self, context):
    """ Clear the old viz data. Draw the new viz data. """
    global global_mol_file_list

    mcell = context.scene.mcell

#    if len(mcell.mol_viz.mol_file_list) > 0:
    if len(global_mol_file_list) > 0:
#        filename = mcell.mol_viz.mol_file_list[mcell.mol_viz.mol_file_index].name
        filename = global_mol_file_list[mcell.mol_viz.mol_file_index]
        mcell.mol_viz.mol_file_name = filename
        filepath = os.path.join(mcell.mol_viz.mol_file_dir, filename)

        # Save current global_undo setting. Turn undo off to save memory
        global_undo = bpy.context.user_preferences.edit.use_global_undo
        bpy.context.user_preferences.edit.use_global_undo = False

        mol_viz_clear(mcell)
        if mcell.mol_viz.mol_viz_enable:
            mol_viz_file_read(mcell, filepath)

        # Reset undo back to its original state
        bpy.context.user_preferences.edit.use_global_undo = global_undo
    return


def mol_viz_clear(mcell_prop, force_clear=False):
    """ Clear the viz data from the previous frame. """

    mcell = mcell_prop
    scn = bpy.context.scene
    scn_objs = scn.objects
    meshes = bpy.data.meshes
    objs = bpy.data.objects

    if force_clear:
      mol_viz_list = [obj for obj in scn_objs if (obj.name[:4] == 'mol_') and (obj.name[-6:] != '_shape')]
    else:
      mol_viz_list = mcell.mol_viz.mol_viz_list

    for mol_item in mol_viz_list:
        mol_name = mol_item.name
        mol_obj = scn_objs.get(mol_name)
        if mol_obj:
            hide = mol_obj.hide

            mol_pos_mesh = mol_obj.data
            mol_pos_mesh_name = mol_pos_mesh.name
            mol_shape_obj_name = "%s_shape" % (mol_name)
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
            mols_obj = objs.get("molecules")
            mol_obj.parent = mols_obj

            mol_obj.hide = hide

    # Reset mol_viz_list to empty
    for i in range(len(mcell.mol_viz.mol_viz_list)-1, -1, -1):
        mcell.mol_viz.mol_viz_list.remove(i)





def old_mol_viz_file_read(mcell_prop, filepath):
    """ Draw the viz data for the current frame. """
    mcell = mcell_prop
    try:

#        begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#        print ("Processing molecules from file:    %s" % (filepath))

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, "rb")
        b = array.array("I")
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read Binary format molecule file:
            bin_data = 1
            while True:
                try:
                    # Variable names are a little hard to follow
                    # Here's what I assume they mean:
                    # ni = Initially, array of molecule name length.
                    # Later, array of number of molecule positions in xyz
                    # (essentially, the number of molecules multiplied by 3).
                    # ns = Array of ascii character codes for molecule name.
                    # s = String of molecule name.
                    # mt = Surface molecule flag.
                    ni = array.array("B")
                    ni.fromfile(mol_file, 1)
                    ns = array.array("B")
                    ns.fromfile(mol_file, ni[0])
                    s = ns.tostring().decode()
                    mol_name = "mol_%s" % (s)
                    mt = array.array("B")
                    mt.fromfile(mol_file, 1)
                    ni = array.array("I")
                    ni.fromfile(mol_file, 1)
                    mol_pos = array.array("f")
                    mol_orient = array.array("f")
                    mol_pos.fromfile(mol_file, ni[0])
#                    tot += ni[0]/3
                    if mt[0] == 1:
                        mol_orient.fromfile(mol_file, ni[0])
                    mol_dict[mol_name] = [mt[0], mol_pos, mol_orient]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                except:
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

        else:
            # Read ASCII format molecule file:
            bin_data = 0
            mol_file.close()
            # Create a list of molecule names, positions, and orientations
            # Each entry in the list is ordered like this (afaik):
            # [molec_name, [x_pos, y_pos, z_pos, x_orient, y_orient, z_orient]]
            # Orientations are zero in the case of volume molecules.
            mol_data = [[s.split()[0], [
                float(x) for x in s.split()[2:]]] for s in open(
                    filepath, "r").read().split("\n") if s != ""]

            for mol in mol_data:
                mol_name = "mol_%s" % (mol[0])
                if not mol_name in mol_dict:
                    mol_orient = mol[1][3:]
                    mt = 0
                    # Check to see if it's a surface molecule
                    if ((mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) |
                            (mol_orient[2] != 0.0)):
                        mt = 1
                    mol_dict[mol_name] = [
                        mt, array.array("f"), array.array("f")]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                mt = mol_dict[mol_name][0]
                mol_dict[mol_name][1].extend(mol[1][:3])
                if mt == 1:
                    mol_dict[mol_name][2].extend(mol[1][3:])

        # Get the parent object to all the molecule positions if it exists.
        # Otherwise, create it.
        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])
            mols_obj = bpy.context.selected_objects[0]
            mols_obj.name = "molecules"

        #mol_viz_list

        if mol_dict:
            meshes = bpy.data.meshes
            mats = bpy.data.materials
            objs = bpy.data.objects
            scn = bpy.context.scene
            scn_objs = scn.objects
            z_axis = mathutils.Vector((0.0, 0.0, 1.0))
            #ident_mat = mathutils.Matrix.Translation(
            #    mathutils.Vector((0.0, 0.0, 0.0)))

            for mol_name in mol_dict.keys():
                mol_mat_name = "%s_mat" % (mol_name)
                mol_type = mol_dict[mol_name][0]
                mol_pos = mol_dict[mol_name][1]
                mol_orient = mol_dict[mol_name][2]

                # Randomly orient volume molecules
                if mol_type == 0:
                    mol_orient.extend([random.uniform(
                        -1.0, 1.0) for i in range(len(mol_pos))])

                # Look-up mesh shape (glyph) template and create if needed
                mol_shape_mesh_name = "%s_shape" % (mol_name)
                mol_shape_obj_name = mol_shape_mesh_name
                mol_shape_mesh = meshes.get(mol_shape_mesh_name)
                if not mol_shape_mesh:
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=0, size=0.005, location=[0, 0, 0])
                    mol_shape_obj = bpy.context.active_object
                    mol_shape_obj.name = mol_shape_obj_name
                    mol_shape_obj.track_axis = "POS_Z"
                    mol_shape_mesh = mol_shape_obj.data
                    mol_shape_mesh.name = mol_shape_mesh_name
                else:
                    mol_shape_obj = objs.get(mol_shape_obj_name)

                # Look-up material, create if needed.
                # Associate material with mesh shape.
                mol_mat = mats.get(mol_mat_name)
                if not mol_mat:
                    mol_mat = mats.new(mol_mat_name)
                    mol_mat.diffuse_color = mcell.mol_viz.color_list[
                        mcell.mol_viz.color_index].vec
                    mcell.mol_viz.color_index = mcell.mol_viz.color_index + 1
                    if (mcell.mol_viz.color_index >
                            len(mcell.mol_viz.color_list)-1):
                        mcell.mol_viz.color_index = 0
                if not mol_shape_mesh.materials.get(mol_mat_name):
                    mol_shape_mesh.materials.append(mol_mat)

                # Create a "mesh" to hold instances of molecule positions
                mol_pos_mesh_name = "%s_pos" % (mol_name)
                mol_pos_mesh = meshes.get(mol_pos_mesh_name)
                if not mol_pos_mesh:
                    mol_pos_mesh = meshes.new(mol_pos_mesh_name)

                # Add and place vertices at positions of molecules
                mol_pos_mesh.vertices.add(len(mol_pos)//3)
                mol_pos_mesh.vertices.foreach_set("co", mol_pos)
                mol_pos_mesh.vertices.foreach_set("normal", mol_orient)

                # Create object to contain the mol_pos_mesh data
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
#        print ("     Processed %d molecules in %g seconds\n" % (
#            len(mol_data), utime))

    except IOError:
        print(("\n***** File not found: %s\n") % (filepath))

    except ValueError:
        print(("\n***** Invalid data in file: %s\n") % (filepath))




import sys, traceback


def mol_viz_file_dump(filepath):
    """ Read and Dump a molecule viz file. """
    tot = 0
    try:

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, "rb")
        b = array.array("I")
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read MCell/CellBlender Binary Format molecule file, version 1:
            print ("Reading binary file " + filepath )
            while True:
                try:
                    # ni = Initially, byte array of molecule name length.
                    # Later, array of number of molecule positions in xyz
                    # (essentially, the number of molecules multiplied by 3).
                    # ns = Array of ascii character codes for molecule name.
                    # s = String of molecule name.
                    # mt = Surface molecule flag.
                    ni = array.array("B")          # Create a binary byte ("B") array
                    ni.fromfile(mol_file, 1)       # Read one byte which is the number of characters in the molecule name
                    ns = array.array("B")          # Create another byte array to hold the molecule name
                    ns.fromfile(mol_file, ni[0])   # Read ni bytes from the file
                    s = ns.tostring().decode()     # Decode bytes as ASCII into a string (s)
                    mol_name = "mol_%s" % (s)      # Construct name of blender molecule viz object
                    mt = array.array("B")          # Create a byte array for the molecule type
                    mt.fromfile(mol_file, 1)       # Read one byte for the molecule type
                    ni = array.array("I")          # Re-use ni as an integer array to hold the number of molecules of this name in this frame
                    ni.fromfile(mol_file, 1)       # Read the 4 byte integer value which is 3 times the number of molecules
                    mol_pos = array.array("f")     # Create a floating point array to hold the positions
                    mol_orient = array.array("f")  # Create a floating point array to hold the orientations
                    mol_pos.fromfile(mol_file, ni[0])  # Read the positions which should be 3 floats per molecule
                    mol_type_name = "Volume"
                    tot += ni[0]/3
                    if mt[0] == 1:                                        # If mt==1, it's a surface molecule
                        mol_orient.fromfile(mol_file, ni[0])              # Read the surface molecule orientations
                        mol_type_name = "Surface"
                    print ( mol_type_name + " Molecule " + s + " contains " + str(tot) + " instances" )

                except EOFError:
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

                except:
                    print( "Unexpected Exception: " + str(sys.exc_info()) )
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break
        else:
            print ( "Dump doesn't read text files." )
    except IOError:
        print(("\n***** IOError: File: %s\n") % (filepath))

    except ValueError:
        print(("\n***** ValueError: Invalid data in file: %s\n") % (filepath))

    except RuntimeError as rte:
        print(("\n***** RuntimeError reading file: %s\n") % (filepath))
        print("      str(error): \n" + str(rte) + "\n")
        fail_error = sys.exc_info()
        print ( "    Error Type: " + str(fail_error[0]) )
        print ( "    Error Value: " + str(fail_error[1]) )
        tb = fail_error[2]
        # tb.print_stack()
        print ( "=== Traceback Start ===" )
        traceback.print_tb(tb)
        print ( "=== Traceback End ===" )

    except Exception as uex:
        # Catch any exception
        print ( "\n***** Unexpected exception:" + str(uex) + "\n" )
        raise



def mol_viz_file_read(mcell_prop, filepath):
    """ Read and Draw the molecule viz data for the current frame. """

    mcell = mcell_prop  # Why is this here?

    if mcell.mol_viz.use_custom_mol_code and ("custom_mol_viz.py" in bpy.data.texts):
      # print ( "Using Custom Mol Code from \"custom_mol_viz.py\"" )
      # Store the filepath for this frame in a place where it can be found
      mcell.mol_viz.frame_file_name = filepath
      
      #source_code = bpy.data.texts["custom_mol_viz.py"].as_string()
      
      # Convert the text to code (this might be done earlier when the file is selected)
      code = compile ( bpy.data.texts["custom_mol_viz.py"].as_string(), "<string>", 'exec' )
      
      # Execute the code
      exec ( code )

      return

    dup_check = False
    try:

#        begin = resource.getrusage(resource.RUSAGE_SELF)[0]
#        print ("Processing molecules from file:    %s" % (filepath))

        # Quick check for Binary or ASCII format of molecule file:
        mol_file = open(filepath, "rb")
        b = array.array("I")
        b.fromfile(mol_file, 1)

        mol_dict = {}

        if b[0] == 1:
            # Read MCell/CellBlender Binary Format molecule file, version 1:
            # print ("Reading binary file " + filepath )
            bin_data = 1
            while True:
                try:
                    # ni = Initially, byte array of molecule name length.
                    # Later, array of number of molecule positions in xyz
                    # (essentially, the number of molecules multiplied by 3).
                    # ns = Array of ascii character codes for molecule name.
                    # s = String of molecule name.
                    # mt = Surface molecule flag.
                    ni = array.array("B")          # Create a binary byte ("B") array
                    ni.fromfile(mol_file, 1)       # Read one byte which is the number of characters in the molecule name
                    ns = array.array("B")          # Create another byte array to hold the molecule name
                    ns.fromfile(mol_file, ni[0])   # Read ni bytes from the file
                    s = ns.tostring().decode()     # Decode bytes as ASCII into a string (s)
                    mol_name = "mol_%s" % (s)      # Construct name of blender molecule viz object
                    mt = array.array("B")          # Create a byte array for the molecule type
                    mt.fromfile(mol_file, 1)       # Read one byte for the molecule type
                    ni = array.array("I")          # Re-use ni as an integer array to hold the number of molecules of this name in this frame
                    ni.fromfile(mol_file, 1)       # Read the 4 byte integer value which is 3 times the number of molecules
                    mol_pos = array.array("f")     # Create a floating point array to hold the positions
                    mol_orient = array.array("f")  # Create a floating point array to hold the orientations
                    mol_pos.fromfile(mol_file, ni[0])  # Read the positions which should be 3 floats per molecule
#                    tot += ni[0]/3  
                    if mt[0] == 1:                                        # If mt==1, it's a surface molecule
                        mol_orient.fromfile(mol_file, ni[0])              # Read the surface molecule orientations
                    mol_dict[mol_name] = [mt[0], mol_pos, mol_orient]     # Create a dictionary entry for this molecule containing a list of relevant data                    
                    if len(mcell.mol_viz.mol_viz_list) > 0:
                      for i in range(len(mcell.mol_viz.mol_viz_list)):
                        if mcell.mol_viz.mol_viz_list[i].name[4:] == mol_name:
                          dup_check = True      
                    if dup_check == False:
                      new_item = mcell.mol_viz.mol_viz_list.add()           # Create a new collection item to hold the name for this molecule
                      new_item.name = mol_name                              # Assign the name to the new item                              

                except EOFError:
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

                except:
                    print( "Unexpected Exception: " + str(sys.exc_info()) )
#                    print("Molecules read: %d" % (int(tot)))
                    mol_file.close()
                    break

        else:
            # Read ASCII format molecule file:
            # print ("Reading ASCII file " + filepath )
            bin_data = 0
            mol_file.close()
            # Create a list of molecule names, positions, and orientations
            # Each entry in the list is ordered like this (afaik):
            # [molec_name, [x_pos, y_pos, z_pos, x_orient, y_orient, z_orient]]
            # Orientations are zero in the case of volume molecules.
            mol_data = [[s.split()[0], [
                float(x) for x in s.split()[2:]]] for s in open(
                    filepath, "r").read().split("\n") if s != ""]

            for mol in mol_data:
                mol_name = "mol_%s" % (mol[0])
                if not mol_name in mol_dict:
                    mol_orient = mol[1][3:]
                    mt = 0
                    # Check to see if it's a surface molecule
                    if ((mol_orient[0] != 0.0) | (mol_orient[1] != 0.0) |
                            (mol_orient[2] != 0.0)):
                        mt = 1
                    mol_dict[mol_name] = [
                        mt, array.array("f"), array.array("f")]
                    new_item = mcell.mol_viz.mol_viz_list.add()
                    new_item.name = mol_name
                mt = mol_dict[mol_name][0]
                mol_dict[mol_name][1].extend(mol[1][:3])
                if mt == 1:
                    mol_dict[mol_name][2].extend(mol[1][3:])

        # Get the parent object to all the molecule positions if it exists.
        # Otherwise, create it.
        mols_obj = bpy.data.objects.get("molecules")
        if not mols_obj:
            bpy.ops.object.add(location=[0, 0, 0])      # Create an "Empty" object in the Blender scene
            ### Note, the following line seems to cause an exception in some contexts: 'Context' object has no attribute 'selected_objects'
            mols_obj = bpy.context.selected_objects[0]  # The newly added object will be selected
            mols_obj.name = "molecules"                 # Name this empty object "molecules" 
            mols_obj.hide_select = True
            mols_obj.hide = True

        if mol_dict:
            meshes = bpy.data.meshes
            mats = bpy.data.materials
            objs = bpy.data.objects
            scn = bpy.context.scene
            scn_objs = scn.objects
            z_axis = mathutils.Vector((0.0, 0.0, 1.0))
            #ident_mat = mathutils.Matrix.Translation(
            #    mathutils.Vector((0.0, 0.0, 0.0)))

            for mol_name in mol_dict.keys():
                mol_mat_name = "%s_mat" % (mol_name)
                mol_type = mol_dict[mol_name][0]
                mol_pos = mol_dict[mol_name][1]
                mol_orient = mol_dict[mol_name][2]

                # print ( "in mol_viz_file_read with mol_name = " + mol_name + ", mol_mat_name = " + mol_mat_name + ", file = " + filepath[filepath.rfind(os.sep)+1:] )

                # Randomly orient volume molecules
                if mol_type == 0:
                    mol_orient.extend([random.uniform(
                        -1.0, 1.0) for i in range(len(mol_pos))])

                # Look up the glyph, color, size, and other attributes from the molecules list
                
                #### If the molecule found in the viz file doesn't exist in the molecules list, create it as the interface for changing color, etc.

                mname = mol_name[4:]   # Trim off the "mol_" portion to use as an index into the molecules list
                mol = None
                if (len(mname) > 0) and (mname in mcell.molecules.molecule_list):
                    mol = mcell.molecules.molecule_list[mname]
                    # The color below doesn't seem to be used ... the color comes from a material
                    # print ( "Mol " + mname + " has color " + str(mol.color) )

                # Look-up mesh shape (glyph) template and create if needed
                
                # This may end up calling a member function of the molecule class to create a new default molecule (including glyph)
                if mol != None:
                    # print ( "Molecule  glyph: " + str (mol.glyph) )
                    pass
                mol_shape_mesh_name = "%s_shape" % (mol_name)
                mol_shape_obj_name = mol_shape_mesh_name
                mol_shape_mesh = meshes.get(mol_shape_mesh_name)  # This will return None if not found by that name
                # print ( "Getting or Making the glyph for " + mol_shape_obj_name )
                if not mol_shape_mesh:
                    # Make the glyph right here
                    # print ( "Making a " + str(mol.glyph) + " molecule glyph" )
                    bpy.ops.mesh.primitive_ico_sphere_add(
                        subdivisions=0, size=0.005, location=[0, 0, 0])
                    mol_shape_obj = bpy.context.active_object
                    mol_shape_obj.name = mol_shape_obj_name
                    mol_shape_obj.track_axis = "POS_Z"
                    mol_shape_obj.hide_select = True
                    mol_shape_mesh = mol_shape_obj.data
                    mol_shape_mesh.name = mol_shape_mesh_name
                else:
                    # print ( "Using a " + str(mol.glyph) + " molecule glyph" )
                    mol_shape_obj = objs.get(mol_shape_obj_name)

                # Save the current layer(s) that the molecule positions are on.
                # We'll apply this to the new position and glyph objects later.
                mol_layers = None
                if not (mol_shape_obj is None):
                    mol_layers = mol_shape_obj.layers[:]

                # Look-up material, create if needed.
                # Associate material with mesh shape.
                mol_mat = mats.get(mol_mat_name)
                if not mol_mat:
                    mol_mat = mats.new(mol_mat_name)
                    mol_mat.diffuse_color = mcell.mol_viz.color_list[
                        mcell.mol_viz.color_index].vec
                    mcell.mol_viz.color_index = mcell.mol_viz.color_index + 1
                    if (mcell.mol_viz.color_index >
                            len(mcell.mol_viz.color_list)-1):
                        mcell.mol_viz.color_index = 0
                if not mol_shape_mesh.materials.get(mol_mat_name):
                    mol_shape_mesh.materials.append(mol_mat)

                #if (mol != None):
                #    # and (mol.usecolor):
                #    # Over-ride the default colors
                #    mol_mat.diffuse_color = mol.color
                #    mol_mat.emit = mol.emit

                # Look-up mesh to hold instances of molecule positions, create if needed
                mol_pos_mesh_name = "%s_pos" % (mol_name)
                mol_pos_mesh = meshes.get(mol_pos_mesh_name)
                if not mol_pos_mesh:
                    mol_pos_mesh = meshes.new(mol_pos_mesh_name)

                # Add and set values of vertices at positions of molecules
                # This uses vertices.add(), but where are the old vertices removed?
                mol_pos_mesh.vertices.add(len(mol_pos)//3)
                mol_pos_mesh.vertices.foreach_set("co", mol_pos)
                mol_pos_mesh.vertices.foreach_set("normal", mol_orient)

                if mcell.cellblender_preferences.debug_level > 100:

                  __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

                # Save the molecule's visibility state, so it can be restored later
                mol_obj = objs.get(mol_name)
                if mol_obj:
                    hide = mol_obj.hide
                    scn_objs.unlink(mol_obj)
                    objs.remove(mol_obj)
                else:
                    hide = False

                # Create object to contain the mol_pos_mesh data
                mol_obj = objs.new(mol_name, mol_pos_mesh)
                scn_objs.link(mol_obj)
                mol_shape_obj.parent = mol_obj
                mol_obj.dupli_type = 'VERTS'
                mol_obj.use_dupli_vertices_rotation = True
                mol_obj.parent = mols_obj
                mol_obj.hide_select = True
                if (not (mol_obj is None)) and (not (mol_shape_obj is None)):
                    mol_obj.layers = mol_layers[:]
                    mol_shape_obj.layers = mol_layers[:]
            
                # Restore the visibility state
                mol_obj.hide = hide

                if mol_obj:
                    if (mol_name == "mol_volume_proxy") or (mol_name == "mol_surface_proxy"):
                        if mcell.cellblender_preferences.bionetgen_mode and not mcell.cellblender_preferences.show_mcellr_proxies:
                            mol_obj.hide = True
                        else:
                            mol_obj.hide = False


#        utime = resource.getrusage(resource.RUSAGE_SELF)[0]-begin
#        print ("     Processed %d molecules in %g seconds\n" % (
#            len(mol_data), utime))

    except IOError:
        print(("\n***** IOError: File: %s\n") % (filepath))

    except ValueError:
        print(("\n***** ValueError: Invalid data in file: %s\n") % (filepath))

    except RuntimeError as rte:
        print(("\n***** RuntimeError reading file: %s\n") % (filepath))
        print("      str(error): \n" + str(rte) + "\n")
        fail_error = sys.exc_info()
        print ( "    Error Type: " + str(fail_error[0]) )
        print ( "    Error Value: " + str(fail_error[1]) )
        tb = fail_error[2]
        # tb.print_stack()
        print ( "=== Traceback Start ===" )
        traceback.print_tb(tb)
        print ( "=== Traceback End ===" )

    except Exception as uex:
        # Catch any exception
        print ( "\n***** Unexpected exception:" + str(uex) + "\n" )
        raise





# Mol Viz Panel Classes



class MCELL_PT_viz_results(bpy.types.Panel):
    bl_label = "CellBlender - Visualize Simulation Results"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.mol_viz.draw_panel ( context, self )



class MCELL_UL_visualization_export_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')

        # Don't bother showing individual export option if the user has already
        # asked to export everything
        if not context.scene.mcell.viz_output.export_all:
            layout.prop(item, "export_viz", text="Export")


class MCELL_PT_visualization_output_settings(bpy.types.Panel):
    bl_label = "CellBlender - Visualization Output Settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.viz_output.draw_panel ( context, self )




# Mol Viz Property Groups


class MolVizStringProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold string for a CollectionProperty """
    name = StringProperty(name="Text")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell String Property with name \"" + self.name + "\" ... no collections to remove." )
        pass


class MCellFloatVectorProperty(bpy.types.PropertyGroup):
    """ Generic PropertyGroup to hold float vector for a CollectionProperty """
    vec = bpy.props.FloatVectorProperty(name="Float Vector")
    def remove_properties ( self, context ):
        #print ( "Removing an MCell Float Vector Property... no collections to remove. Is there anything special do to for Vectors?" )
        pass


def generate_choices_callback(self, context):

    mcell = context.scene.mcell
    data_layout = mcell.mol_viz['data_layout']

    #print ( "generate_choices_callback called with a self of " + str(self) )
    #print ( "generate_choices_callback called with a self.name of " + str(self.name) )
    #print ( "generate_choices_callback called with a dyn_data_layout of " + str(data_layout) )

    items = []

    for item in data_layout:
        if self.name == item[0]:
            opt_num = 0
            for option in item[1]:
                # print ( "appending " + str(option) + " as " + str(opt_num) )
                items.append ( (str(opt_num), str(option), "") )
                opt_num += 1
    return items


def select_test_case_callback(self, context):
    # Build the path starting from output_data
    mcell = context.scene.mcell
    mol_viz = mcell.mol_viz
    data_layout = mcell.mol_viz['data_layout']
    bpy.ops.mcell.update_data_layout()
    mcell.model_objects.update_scene(context.scene, force=True)
    bpy.ops.mcell.read_viz_data()

class DynamicChoicePropGroup(bpy.types.PropertyGroup):
    enum_choice = EnumProperty( name="Parameter Value", description="Dynamic List of Choices.", items=generate_choices_callback, update=select_test_case_callback )


class MCellMolVizPropertyGroup(bpy.types.PropertyGroup):
    """ Property group for for molecule visualization.

      This was the "Visualize Simulation Results Panel".

    """

    mol_viz_seed_list = CollectionProperty(
        type=MolVizStringProperty, name="Visualization Seed List")
    active_mol_viz_seed_index = IntProperty(
        name="Current Visualization Seed Index", default=0,
        update=read_viz_data_callback)
    mol_file_dir = StringProperty(
        name="Molecule File Dir", subtype='NONE')
    mol_file_list = CollectionProperty(
        type=MolVizStringProperty, name="Molecule File Name List")
    mol_file_num = IntProperty(
        name="Number of Molecule Files", default=0)
    mol_file_name = StringProperty(
        name="Current Molecule File Name", subtype='NONE')
    mol_file_index = IntProperty(name="Current Molecule File Index", default=0)
    mol_file_start_index = IntProperty(
        name="Molecule File Start Index", default=0)
    mol_file_stop_index = IntProperty(
        name="Molecule File Stop Index", default=0)
    mol_file_step_index = IntProperty(
        name="Molecule File Step Index", default=1)
    mol_viz_list = CollectionProperty(
        type=MolVizStringProperty, name="Molecule Viz Name List")
    render_and_save = BoolProperty(name="Render & Save Images")
    mol_viz_enable = BoolProperty(
        name="Enable Molecule Vizualization",
        description="Disable for faster animation preview",
        default=True, update=mol_viz_update)
    ascii_enable = BoolProperty(name="Change Viz Data to Ascii",default= False)
    molecule_read_in = BoolProperty(name = "Define molecules from Viz Data.",default= False)
    color_list = CollectionProperty(
        type=MCellFloatVectorProperty, name="Molecule Color List")
    color_index = IntProperty(name="Color Index", default=0)
    manual_select_viz_dir = BoolProperty(
        name="Manually Select Viz Directory", default=False,
        description="Toggle the option to manually load viz data.",
        update=mol_viz_toggle_manual_select)

    use_custom_mol_code = BoolProperty(
        name="Use custom_mol_viz.py", default=False,
        description="Use a custom program to read and display molecules.") # May want to use an update to compile

    frame_file_name = StringProperty(description="Place to store the file name")

    #mol_viz_sweep_list = CollectionProperty(type=DynamicChoicePropGroup, name="Choice Dimensions")
    choices_list = CollectionProperty(type=DynamicChoicePropGroup, name="Choice Dimensions")


    def build_data_model_from_properties ( self, context ):
        print ( "Building Mol Viz data model from properties" )
        mv_dm = {}
        mv_dm['data_model_version'] = "DM_2015_04_13_1700"

        mv_seed_list = []
        for s in self.mol_viz_seed_list:
            mv_seed_list.append ( str(s.name) )
        mv_dm['seed_list'] = mv_seed_list

        mv_dm['active_seed_index'] = self.active_mol_viz_seed_index

        # Don't save the actual mol_file_dir, but save the path relative to this blend file.
        # mv_dm['file_dir'] = self.mol_file_dir

        real_mol_file_dir = os.path.realpath(self.mol_file_dir)
        real_blend_file_dir = os.path.split(os.path.realpath(bpy.data.filepath))[0]
        mv_dm['file_dir'] = os.path.relpath(real_mol_file_dir,real_blend_file_dir)

        # mv_file_list = []
        # for s in self.mol_file_list:
        #     mv_file_list.append ( str(s.name) )
        # mv_dm['file_list'] = mv_file_list

        mv_dm['file_num'] = self.mol_file_num
        mv_dm['file_name'] = self.mol_file_name
        mv_dm['file_index'] = self.mol_file_index
        mv_dm['file_start_index'] = self.mol_file_start_index
        mv_dm['file_stop_index'] = self.mol_file_stop_index
        mv_dm['file_step_index'] = self.mol_file_step_index

        mv_viz_list = []
        for s in self.mol_viz_list:
            mv_viz_list.append ( str(s.name) )
        mv_dm['viz_list'] = mv_viz_list

        mv_dm['render_and_save'] = self.render_and_save
        mv_dm['viz_enable'] = self.mol_viz_enable

        mv_color_list = []
        for c in self.color_list:
            mv_color = []
            for i in c.vec:
                mv_color.append ( i )
            # Only store if it's not already stored
            if not mv_color in mv_color_list:
                mv_color_list.append ( mv_color )
        mv_dm['color_list'] = mv_color_list

        mv_dm['color_index'] = self.color_index
        mv_dm['manual_select_viz_dir'] = self.manual_select_viz_dir

        return mv_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellMolVizPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2015_04_13_1700
            dm['data_model_version'] = "DM_2015_04_13_1700"

        if dm['data_model_version'] == "DM_2015_04_13_1700":
            # Change on June 22nd, 2015: The molecule file list will no longer be stored in the data model
            if 'file_list' in dm:
                dm.pop ( 'file_list' )
            dm['data_model_version'] = "DM_2015_06_22_1430"

        if dm['data_model_version'] != "DM_2015_06_22_1430":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellMolVizPropertyGroup data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2015_06_22_1430":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellMolVizPropertyGroup data model to current version." )

        # Remove the old properties (includes emptying collections)
        self.remove_properties ( context )

        # Build the new properties
        
        for s in dm["seed_list"]:
            new_item = self.mol_viz_seed_list.add()
            new_item.name = s
            
        self.active_mol_viz_seed_index = dm['active_seed_index']

        # Don't restore the actual mol_file_dir, but append the blend file path to the relative file_dir.
        # self.mol_file_dir = dm['file_dir']

        real_blend_file_dir = os.path.split(os.path.realpath(bpy.data.filepath))[0]
        self.mol_file_dir = os.path.join(real_blend_file_dir,dm['file_dir'])

        #for s in dm["file_list"]:
        #    new_item = self.mol_file_list.add()
        #    new_item.name = s

        self.mol_file_num = dm['file_num']
        self.mol_file_name = dm['file_name']
        self.mol_file_index = dm['file_index']
        self.mol_file_start_index = dm['file_start_index']
        self.mol_file_stop_index = dm['file_stop_index']
        self.mol_file_step_index = dm['file_step_index']

        for s in dm["viz_list"]:
            new_item = self.mol_viz_list.add()
            new_item.name = s
            
        self.render_and_save = dm['render_and_save']
        self.mol_viz_enable = dm['viz_enable']


        # Remove duplicates from color list before building colors
        new_color_list = []
        for c in dm["color_list"]:
            if not c in new_color_list:
                new_color_list.append ( c )
        dm['color_list'] = new_color_list

        # Add to the color_list collection
        for c in dm["color_list"]:
            new_item = self.color_list.add()
            new_item.vec = c
            
        if 'color_index' in dm:
            self.color_index = dm['color_index']
        else:
            self.color_index = 0

        self.manual_select_viz_dir = dm['manual_select_viz_dir']


    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Molecule Visualization Properties..." )

        """
        while len(self.mol_viz_seed_list) > 0:
            self.mol_viz_seed_list.remove(0)

        while len(self.mol_file_list) > 0:
            self.mol_file_list.remove(0)

        while len(self.mol_viz_list) > 0:
            self.mol_viz_list.remove(0)

        while len(self.color_list) > 0:
            # It's not clear if anything needs to be done to remove individual color components first
            self.color_list.remove(0)
        """

        for item in self.mol_viz_seed_list:
            item.remove_properties(context)
        self.mol_viz_seed_list.clear()
        self.active_mol_viz_seed_index = 0
        for item in self.mol_file_list:
            item.remove_properties(context)
        self.mol_file_list.clear()
        self.mol_file_index = 0
        self.mol_file_start_index = 0
        self.mol_file_stop_index = 0
        self.mol_file_step_index = 1
        for item in self.mol_viz_list:
            item.remove_properties(context)
        self.mol_viz_list.clear()
        for item in self.color_list:
            item.remove_properties(context)
        self.color_list.clear()
        self.color_index = 0
        print ( "Done removing all Molecule Visualization Properties." )


    def update_data_layout(self, context):
        """
        The data layout describes the folder structure containing mcell's output.
        For consistency, it is currently a Python structure directly reflecting
        the JSON structure stored in that file. Some of those fields may not be
        needed for all types of processing, and substructures could be passed.
        But that might result in confusion, so the whole structure is used for now.

        self.choices_list is the Blender structure holding the list of subdirectories
        described by the data layout. It is currently a list of enum fields where the
        choices in the enum are the possible sub-subdirectories at each level. This
        function updates those choices based on the data in "data_layout.json". It is
        relatively easy to simply read that file and recreate the self.choices_list
        each time a refresh is requested. However, this has the unfortunate effect
        of not preserving the previously chosen settings. This code attempts to
        preserve the settings when the structure hasn't changed.
        """

        mcell = context.scene.mcell

        files_path = mcell_files_path()  # This will include the "mcell" on the end

        if os.path.exists(files_path):

          # Determine if this data structure is in the newer sweep format or not
          use_sweep = 'output_data' in os.listdir(files_path)

          data_paths = []

          if use_sweep:

            # Check if the current structure reflects the recent run

            f = open ( os.path.join(files_path,"data_layout.json"), 'r' )
            layout_spec = json.loads ( f.read() )
            f.close()
            data_layout = layout_spec['data_layout']

            self['data_layout'] = data_layout

            # Build an expected choice list that won't contain '/DIR', '/FILE_TYPE', '/SEED'
            expected_choice_list = []
            for i in range(len(data_layout)):
                name = str(data_layout[i][0])
                if not (name in ['/DIR', '/FILE_TYPE', '/SEED']):
                    # This is a directory name so add it to the expected list
                    expected_choice_list.append ( name )

            # Compare the expected list with the current Blender choice list
            needs_refresh = False
            if len(self.choices_list) != len(expected_choice_list):
                # print ( "List Lengths don't match" )
                needs_refresh = True
            else:
                for i in range(len(self.choices_list)):
                    if self.choices_list[i]['name'] != expected_choice_list[i]:
                        needs_refresh = True
                        break

            if needs_refresh:
                # Remove all items from Blender's RNA self.choices_list
                while len(self.choices_list) > 0:
                    self.choices_list.remove ( 0 )
                # Add the items in the current data layout
                for i in range(len(data_layout)):
                    if not (data_layout[i][0] in ['/DIR', '/FILE_TYPE', '/SEED']):
                        self.choices_list.add()
                        choice = self.choices_list[len(self.choices_list)-1]
                        choice['name'] = data_layout[i][0]
                        choice['values'] = data_layout[i][1]

    def draw_layout(self, context, layout):
        mcell = context.scene.mcell
        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            row.prop(mcell.mol_viz, "manual_select_viz_dir")
            row = layout.row()
            row.prop(self,"ascii_enable")
            row = layout.row()

            if self.manual_select_viz_dir == True:
              if len(mcell.mol_viz.mol_viz_list) > 0:
                row.prop(self,"molecule_read_in", icon = 'IMPORT')                

            row = layout.row()
            row.prop(self,"use_custom_mol_code")

            row = layout.row()
            if self.manual_select_viz_dir:
                row.operator("mcell.select_viz_data", icon='IMPORT')
            else:
                row.operator("mcell.read_viz_data", icon='IMPORT')
            row = layout.row()
            row.label(text="Molecule Viz Directory: " + self.mol_file_dir,
                      icon='FILE_FOLDER')
            row = layout.row()
            if not self.manual_select_viz_dir:
                row.template_list("UI_UL_list", "viz_seed", mcell.mol_viz,
                                "mol_viz_seed_list", mcell.mol_viz,
                                "active_mol_viz_seed_index", rows=2)
            row = layout.row()

            row = layout.row()
            row.label(text="Current Molecule File: "+self.mol_file_name,
                      icon='FILE')
# Disabled to explore UI slowdown behavior of Plot Panel and run options subpanel when mol_file_list is large
#            row = layout.row()
#            row.template_list("UI_UL_list", "viz_results", mcell.mol_viz,
#                              "mol_file_list", mcell.mol_viz, "mol_file_index",
#                              rows=2)
            row = layout.row()
            layout.prop(mcell.mol_viz, "mol_viz_enable")


            layout.box()
            for i in range(len(self.choices_list)):
                choice = self.choices_list[i]
                row = layout.row()
                row.prop ( self.choices_list[i], "enum_choice", text=choice['name'] )



    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )



class MCellVizOutputPropertyGroup(bpy.types.PropertyGroup):
    active_mol_viz_index = IntProperty(
        name="Active Molecule Viz Index", default=0)
    all_iterations = bpy.props.BoolProperty(
        name="All Iterations",
        description="Include all iterations for visualization.", default=True)
    start = PointerProperty ( name="Start", type=parameter_system.Parameter_Reference )
    end = PointerProperty ( name="End", type=parameter_system.Parameter_Reference )
    step = PointerProperty ( name="Step", type=parameter_system.Parameter_Reference )
    export_all = BoolProperty(
        name="Export All",
        description="Visualize all molecules",
        default=True)

    def init_properties ( self, parameter_system ):
        helptext = "Starting iteration"
        self.start.init_ref  ( parameter_system, user_name="Start", user_expr="0", user_units="", user_descr=helptext, user_int=True )
        helptext = "Ending iteration"
        self.end.init_ref    ( parameter_system, user_name="End",   user_expr="1", user_units="", user_descr=helptext, user_int=True )
        helptext = "Output viz every n iterations"
        self.step.init_ref   ( parameter_system, user_name="Step",  user_expr="1", user_units="", user_descr=helptext, user_int=True )


    def build_data_model_from_properties ( self, context ):
        print ( "Viz Output building Data Model" )
        vo_dm = {}
        vo_dm['data_model_version'] = "DM_2014_10_24_1638"
        vo_dm['all_iterations'] = self.all_iterations
        vo_dm['start'] = self.start.get_expr()
        vo_dm['end']   = self.end.get_expr()
        vo_dm['step']  = self.step.get_expr()
        vo_dm['export_all'] = self.export_all
        return vo_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellVizOutputPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        # Check that the upgraded data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellVizOutputPropertyGroup data model to current version." )
            return None

        return dm



    def build_properties_from_data_model ( self, context, dm ):
        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellVizOutputPropertyGroup data model to current version." )
        
        self.all_iterations = dm["all_iterations"]
        if "start" in dm: self.start.set_expr ( dm["start"] )
        if "end"   in dm: self.end.set_expr   ( dm["end"] )
        if "step"  in dm: self.step.set_expr  ( dm["step"] )
        self.export_all = dm["export_all"]

    def check_properties_after_building ( self, context ):
        print ( "check_properties_after_building not implemented for " + str(self) )


    def remove_properties ( self, context ):
        print ( "Removing all Visualization Output Properties... no collections to remove." )
        # Note that the three "Panel Parameters" (start, end, and step) in this group are all static and should not be removed.
        #self.start.clear_ref ( ps )
        #self.end.clear_ref ( ps )
        #self.step.clear_ref ( ps )


    def draw_layout ( self, context, layout ):
        """ Draw the reaction output "panel" within the layout """
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:
            ps = mcell.parameter_system
            row = layout.row()
            if mcell.molecules.molecule_list:
                row.label(text="Molecules To Visualize:",
                          icon='FORCE_LENNARDJONES')
                row.prop(self, "export_all")
                layout.template_list("MCELL_UL_visualization_export_list",
                                     "viz_export", mcell.molecules,
                                     "molecule_list", self,
                                     "active_mol_viz_index", rows=2)
                layout.prop(self, "all_iterations")
                if self.all_iterations is False:
                    row = layout.row(align=True)
                    self.start.draw(layout,ps)
                    self.end.draw(layout,ps)
                    self.step.draw(layout,ps)

            else:
                row.label(text="Define at least one molecule", icon='ERROR')


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )


