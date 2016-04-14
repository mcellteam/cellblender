bl_info = {
  "version": "0.1",
  "name": "Box Test",
  'author': 'Bob',
  "location": "Properties > Scene",
  "category": "Cell Modeling"
  }


"""
Dynamic Geometry Demo:

  Start Blender with Factory Settings (may need to save startup and restart)
  Delete everything from the Scene (a,a,x,Delete)
  Enable CellBlender and Box Test Addons
  Open CellBlender tab, Initialize CellBlender, Expand the panel

  Open the "Growing Box" Tab (beside CellBlender)
  Disable "Freeze Geometry" (defaulted to frozen to minimize interference)
  Check the "Use CellBlender Data" box to get iterations from CellBlender
  Drag the time line to watch the geometry change
  Zoom in on object and right click to select it (outlined in orange)
  When selected, set the Maximum Draw Type to "Bounds" (easier to see molecules)
  You can change Geometry Settings here, but leave as is the first time
  Save the .blend file somewhere to start a new project (File / SaveAs)

  Begin building your CellBlender project with the Model Objects Panel
  With the box selected, click the "+" button to add it to the model objects
  Add volume and surface molecules to the model and release them in and on the box
    Add molecules "v" (Volume 1e-5) and "s" (Surface 1e-4)
    Release 1000 of each on Object/Region "box"

  Open the Preferences panel and "Set Path to MCell Binary" to dynamic geometry mcell

  Open the "Run" panel and expand the Output/Control Options subpanel
  Check the "Decouple Export and Run" button so you can export and run separately
  Set the time on the timeline to zero (0) so your geometry.mdl file will start there
  Click the Export CellBlender Project button to export all of your static MDL

  Open the Growing Box tab again
  Click on Generate Dynamic Geometry MDL and wait for the button to return
    Note that this may take some time while it's generating the MDL for 1000 frames
  When the button returns, Click on the "Show MDL Geometry" button
  Drag the cursor in the timeline to see the Dynamic MDL changing (this is reading MDL)
  Click the "Update MDL Files" button to insert Dynamic Geometry commands in the static MDL

  Return to the CellBlender tab and the Run Simulation panel
  Click the "Run" button and wait while MCell runs the simulation for 1000 steps

  When done, click the "Reload Visualization Data" button
  Then drag the cursor through the time line and watch the dynamic geometry simulation
  Try changing the molecule size, shape, and color in the Molecule Display Options panel

  The procedure for changing the MCell simulation (not geometry) is:

     Change the model (molecules, reactions, plots, etc)
     Set the time to zero to export the original geometry file
     "Export CellBlender Project" in the CellBlender Run Simulation Panel
     "Update MDL Files" in the Growing Box tab
     Run the  simulation and reload the visualization data

  The procedure for changing the geometry is very similar:

     Change values in the Growing Box panel and check with timeline
     Set the time to zero to export the original geometry file
     "Export CellBlender Project" in the CellBlender Run Simulation Panel
     "Update MDL Files" in the Growing Box tab
     Run the  simulation and reload the visualization data

"""


import sys
import os
import os.path
import hashlib
import bpy
import math
import mathutils
from bpy.props import *



import cellblender.cellblender_utils

def copy_cellblender_data(self, context):
    # Copy the values from CellBlender
    self.path_to_mdl = cellblender.cellblender_utils.mcell_files_path()
    self.time_step = context.scene.mcell.initialization.time_step.get_value()
    self.num_frames = context.scene.mcell.initialization.iterations.get_value()
    return

def use_cellblender_data_callback(self, context):
    print ( "Use CBD = " + str(self.use_cellblender_data) )
    if self.use_cellblender_data:
        # Save the User's settings
        self.user_path_to_mdl = self.path_to_mdl
        self.user_time_step = self.time_step
        self.user_num_frames = self.num_frames
        # Copy the values from CellBlender
        copy_cellblender_data ( self, context )
        context.scene.frame_end = self.num_frames
        # Call the view_all operator in the timeline window (not easy!!!)
        cellblender.cellblender_utils.timeline_view_all ( context )

    else:
        # Copy the values from the saved settings
        self.path_to_mdl = self.user_path_to_mdl
        self.time_step = self.user_time_step
        self.num_frames = self.user_num_frames
    return



def display_callback(self, context):
    self.display_callback(context)
    return

def show_calc_callback(self, context):
    if self.show_MDL_geometry == self.show_calc_geometry:
        self.show_MDL_geometry = not self.show_calc_geometry
        self.display_callback(context)
    return

def show_mdl_callback(self, context):
    if self.show_MDL_geometry == self.show_calc_geometry:
        self.show_calc_geometry = not self.show_MDL_geometry
        self.display_callback(context)
    return


class BoxMakerPropertyGroup(bpy.types.PropertyGroup):

    # Properties for the Box
    
    min_length = bpy.props.FloatProperty(name="Min Length", min=0.0, default=1.0, update=display_callback)
    max_length = bpy.props.FloatProperty(name="Max Length", min=0.0, default=2.0, update=display_callback)
    num_frames = bpy.props.IntProperty(name="Num Frames", min=2, default=1000, update=display_callback)
    period_frames = bpy.props.FloatProperty(name="Period Frames", min=1, default=100, update=display_callback)
    wire = bpy.props.BoolProperty(name="Wire", default=False, update=display_callback)
    disabled = bpy.props.BoolProperty(name="Freeze Geometry", default=True, update=display_callback)
    time_step = bpy.props.FloatProperty(name="Time Step", default=0.000005)
    all_frames = bpy.props.BoolProperty(name="All Frames", default=True)

    cell_name = bpy.props.StringProperty(name="CellName", default="box")

    use_cellblender_data = bpy.props.BoolProperty(name="Use CellBlender Data", default=False,  update=use_cellblender_data_callback)
    user_path_to_mdl = bpy.props.StringProperty(name="User_UseCBD", default="")
    user_time_step = bpy.props.FloatProperty(name="User_TS", default=-1.0)
    user_num_frames = bpy.props.IntProperty(name="User_NF", default=-1)

    path_to_mdl = bpy.props.StringProperty(name="", default="")

    show_calc_geometry = bpy.props.BoolProperty(name="Show Calculated Geometry", default=True,  update=show_calc_callback)
    show_MDL_geometry  = bpy.props.BoolProperty(name="Show MDL Geometry",        default=False, update=show_mdl_callback)


    def get_path_to_mdl ( self, context ):
        return self.path_to_mdl

    def display_callback(self, context):
        # Refresh the scene
        self.update_scene (context.scene)
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return

    def update_scene ( self, scene ):
        if not self.disabled:
            app = scene.box_maker

            box_plf = None
            if self.show_calc_geometry:
                box_plf = self.create_box ( scene )
            else:
                box_plf = self.read_plf_from_mdl ( scene )

            vertex_list = box_plf.points
            face_list = box_plf.faces

            vertices = []
            for point in vertex_list:
                vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
            faces = []
            for face_element in face_list:
                faces.append ( face_element.verts )

            new_mesh = bpy.data.meshes.new ( self.cell_name + "_mesh" )
            new_mesh.from_pydata ( vertices, [], faces )
            new_mesh.update()
            
            box_object = None
            if self.cell_name in scene.objects:
                box_object = scene.objects[self.cell_name]
                old_mesh = box_object.data
                box_object.data = new_mesh
                bpy.data.meshes.remove ( old_mesh )
            else:
                box_object = bpy.data.objects.new ( self.cell_name, new_mesh )
                scene.objects.link ( box_object )



    def read_plf_from_mdl ( self, scene, frame_num=None ):
        cur_frame = frame_num
        if cur_frame == None:
          cur_frame = scene.frame_current

        app = scene.box_maker

        fname = "frame_%d.mdl"%cur_frame
        full_fname = None

        if False and (cur_frame == 0):
            # This geometry file is saved as a normal geometry MDL file and not included in the dynamic geometry file list
            full_fname = os.path.join(app.path_to_mdl,"Scene.geometry.mdl")
        else:
            # This geometry file is saved as a dynamic geometry MDL file and is included in the dynamic geometry file list
            path_to_dg_files = os.path.join ( app.path_to_mdl, "dynamic_geometry" )
            full_fname = os.path.join(path_to_dg_files,fname)

        plf_from_mdl = plf_object()
        plf_from_mdl.read_from_regularized_mdl (file_name = full_fname )

        return plf_from_mdl



    def create_box ( self, scene, frame_num=None ):

        cur_frame = frame_num
        if cur_frame == None:
          cur_frame = scene.frame_current

        app = scene.box_maker

        size_x = app.min_length + ( (app.max_length-app.min_length) * ( (1 - math.cos ( 2 * math.pi * cur_frame / app.period_frames )) / 2 ) )
        size_y = app.min_length + ( (app.max_length-app.min_length) * ( (1 - math.cos ( 2 * math.pi * cur_frame / app.period_frames )) / 2 ) )
        size_z = app.min_length + ( (app.max_length-app.min_length) * ( (1 - math.sin ( 2 * math.pi * cur_frame / app.period_frames )) / 2 ) )
        
        return BasicBox ( size_x, size_y, size_z )




class BoxMakerPanel(bpy.types.Panel):
    bl_label = "Growing Box"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Growing Box"
    def draw(self, context):
        app = context.scene.box_maker

        box = self.layout.box()
        row = box.row()
        row.label ( "Geometry Settings" )
        row = box.row()
        row.prop ( app, "min_length" )
        row.prop ( app, "max_length" )

        row = box.row()
        row.prop ( app, "num_frames" )
        row.prop ( app, "period_frames" )
        row = box.row()
        row.prop ( app, "disabled" )
        if context.object != None:
            row = box.row()
            row.prop ( context.object, "draw_type" )

        row = self.layout.row()
        row.prop ( app, "show_calc_geometry" )
        row.prop ( app, "show_MDL_geometry" )

        box = self.layout.box()
        row = box.row()
        row.prop ( app, "use_cellblender_data" )
        row = box.row()
        if app.use_cellblender_data:
            row.label ( "MDL Interface set by CellBlender" )
        else:
            row.label ( "MDL Interface" )
            row = box.row()
            row.operator ( "box_maker.set_blend_path" )
            row = box.row()
            row.prop ( app, "path_to_mdl" )
            row = box.row()
            row.prop ( app, "time_step" )
            row.prop ( app, "all_frames" )
        row = box.row()
        row.operator ( "box_maker.gen_mdl_geom" )
        row.operator ( "box_maker.update_mdl_files" )


def update_mdl_files(app):
    # Update the main MDL file Scene.main.mdl to insert the DYNAMIC_GEOMETRY directive
    try:

        full_fname = os.path.join(app.path_to_mdl,"Scene.main.mdl")
        print ( "Updating Main MDL file: " + full_fname )
        mdl_file = open ( full_fname )
        mdl_lines = mdl_file.readlines()
        mdl_file.close()

        # Remove any old dynamic geometry lines
        new_lines = []
        for line in mdl_lines:
            if line.strip()[0:16] != "DYNAMIC_GEOMETRY":
                new_lines.append(line)
        lines = new_lines

        # Remove the Scene.geometry.mdl file line
        new_lines = []
        for line in lines:
            if not "\"Scene.geometry.mdl\"" in line:
                new_lines.append(line)
        lines = new_lines

        # Change the "INSTANTIATE Scene OBJECT" line  to  "INSTANTIATE Releases OBJECT"
        new_lines = []
        for line in lines:
            if "INSTANTIATE Scene OBJECT" in line:
                new_lines.append("INSTANTIATE Releases OBJECT\n")
            else:
                new_lines.append(line)
        lines = new_lines

        # Remove the "  box OBJECT box {}" line:
        new_lines = []
        for line in lines:
            if not "box OBJECT box {}" in line:
                new_lines.append(line)
        lines = new_lines

        # Rewrite the MDL with the changes
        mdl_file = open ( full_fname, "w" )
        line_num = 0
        for line in lines:
            line_num += 1
            mdl_file.write ( line )
            if line_num == 3:
                # Insert the dynamic geometry line
                mdl_file.write ( "DYNAMIC_GEOMETRY = \"box_dyn_geom_list.txt\"\n" )
        mdl_file.close()

        full_fname = os.path.join(app.path_to_mdl,"Scene.initialization.mdl")
        print ( "Updating Initialization MDL file: " + full_fname )
        mdl_file = open ( full_fname )
        mdl_lines = mdl_file.readlines()
        mdl_file.close()

        # Remove any old LARGE_MOLECULAR_DISPLACEMENT lines
        new_lines = []
        for line in mdl_lines:
            if line.strip()[0:28] != "LARGE_MOLECULAR_DISPLACEMENT":
                new_lines.append(line)
        lines = new_lines

        # Find the WARNINGS section
        warning_line = -10
        line_num = 0
        for line in lines:
            line_num += 1
            if line.strip() == "WARNINGS":
                warning_line = line_num

        mdl_file = open ( full_fname, "w" )
        line_num = 0
        for line in lines:
            line_num += 1
            mdl_file.write ( line )
            if line_num == warning_line + 1:
                # Insert the dynamic geometry line
                mdl_file.write ( "   LARGE_MOLECULAR_DISPLACEMENT = IGNORED\n" )
        mdl_file.close()
    except Exception as e:
        print ( "Warning: unable to update the existing Scene.main.mdl file, try running the model to generate it first." )
        print ( "   Exception = " + str(e) )
    except:
        print ( "Warning: unable to update the existing Scene.main.mdl file, try running the model to generate it first." )
    return { 'FINISHED' }


class Generate_MDL_Geometry(bpy.types.Operator):
    bl_idname = "box_maker.gen_mdl_geom"
    bl_label = "Generate Dynamic Geometry MDL"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        print ( "Generating Dynamic MDL" )

        app = context.scene.box_maker

        if app.use_cellblender_data:
            # Force an update of the CellBlender values in case they've changed
            copy_cellblender_data(app,context)
        
        start = 1
        end = app.num_frames
        
        print ( "Saving frames from " + str(start) + " to " + str(end) )
        # Make the directory in case CellBlender hasn't been run to make it already
        os.makedirs(app.path_to_mdl,exist_ok=True)
        geom_list_file = open(os.path.join(app.path_to_mdl,'box_dyn_geom_list.txt'), "w", encoding="utf8", newline="\n")
        path_to_dg_files = os.path.join ( app.path_to_mdl, "dynamic_geometry" )
        if not os.path.exists(path_to_dg_files):
            os.makedirs(path_to_dg_files)        
        step = 0
        for f in range(1 + 1+end-start):
            box_plf = context.scene.box_maker.create_box ( context.scene, frame_num=f )
            fname = "frame_%d.mdl"%f
            if False and (f == 0):
                # This geometry file is saved as a normal geometry MDL file and not included in the dynamic geometry file list
                full_fname = os.path.join(app.path_to_mdl,"Scene.geometry.mdl")
                print ( "Saving file " + full_fname )
                box_plf.write_as_mdl ( file_name=full_fname, partitions=False, instantiate=False )
            else:
                # This geometry file is saved as a dynamic geometry MDL file and is included in the dynamic geometry file list
                full_fname = os.path.join(path_to_dg_files,fname)
                print ( "Saving file " + full_fname )
                box_plf.write_as_mdl ( file_name=full_fname, partitions=True, instantiate=True )
                geom_list_file.write('%.9g %s\n' % (step*context.scene.box_maker.time_step, os.path.join(".","dynamic_geometry",fname)))
            step += 1
        geom_list_file.close()
        update_mdl_files(app)
        return { 'FINISHED' }


class Update_MDL_Files(bpy.types.Operator):
    bl_idname = "box_maker.update_mdl_files"
    bl_label = "Update MDL Files"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        app = context.scene.box_maker
        update_mdl_files(app)
        return { 'FINISHED' }


class SetBlendPath(bpy.types.Operator):
    bl_idname = "box_maker.set_blend_path"
    bl_label = "Set Path to MDL Files"
    bl_description = ("Set Path to the Blend File created for each test.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.box_maker

        filepath = os.path.dirname(bpy.data.filepath)
        filepath, dot, blend = bpy.data.filepath.rpartition(os.path.extsep)
        filepath = filepath + "_files"
        app.path_to_mdl = os.path.join(filepath, "mcell")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class App_Model:

    context = None
    scn = None
    path_to_blend = None
    
    def __init__(self, cb_context):
        self.context = cb_context
        self.setup_cb_defaults ( self.context )
        
    def get_scene(self):
        return bpy.data.scenes['Scene']

    def delete_all_objects(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=True)

    def setup_cb_defaults ( self, context ):
        scn = self.get_scene()
        return bpy.data.scenes['Scene']




######################
#   Model  Support   #
######################

import math
import random

class point:
  x=0;
  y=0;
  z=0;

  def __init__ ( self, x, y, z ):
    self.x = x;
    self.y = y;
    self.z = z;
  
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

  # An object that can hold points, lines, and faces (only points and faces are currently implemented)

  points = []
  faces = []
  
  def __init__ ( self ):
    self.points = []
    self.faces = []
  
  def add_point ( self, p ):
    self.points.append ( p );

  def add_face ( self, f ):
    self.faces.append ( f );



  def write_as_mdl ( self, file_name=None, partitions=False, instantiate=False ):
    if file_name != None:
      out_file = open ( file_name, "w" )
      if partitions:
          out_file.write ( "PARTITION_X = [[-2.0 TO 2.0 STEP 0.5]]\n" )
          out_file.write ( "PARTITION_Y = [[-2.0 TO 2.0 STEP 0.5]]\n" )
          out_file.write ( "PARTITION_Z = [[-2.0 TO 2.0 STEP 0.5]]\n" )
          out_file.write ( "\n" )
      out_file.write ( "box POLYGON_LIST\n" )
      out_file.write ( "{\n" )
      out_file.write ( "  VERTEX_LIST\n" )
      out_file.write ( "  {\n" )
      for p in self.points:
          out_file.write ( "    [ " + str(p.x) + ", " + str(p.y) + ", " + str(p.z) + " ]\n" );
      out_file.write ( "  }\n" )
      out_file.write ( "  ELEMENT_CONNECTIONS\n" )
      out_file.write ( "  {\n" )
      for f in self.faces:
          s = "    [ " + str(f.verts[0]) + ", " + str(f.verts[1]) + ", " + str(f.verts[2]) + " ]\n"
          out_file.write ( s );
      out_file.write ( "  }\n" )
      out_file.write ( "}\n" )
      if instantiate:
          out_file.write ( "\n" )
          out_file.write ( "INSTANTIATE Scene OBJECT {\n" )
          out_file.write ( "  box OBJECT box {}\n" )
          out_file.write ( "}\n" )
      out_file.close()


  def read_from_regularized_mdl ( self, file_name=None, partitions=False, instantiate=False ):

    # This function makes some assumptions about the format of the geometry in an MDL file

    self.points = []
    self.faces = []

    if file_name == None:
      # Generate an easy tetrahedron for testing
      self.add_point ( point(0,0,0) )
      self.add_point ( point(0,0,1) )
      self.add_point ( point(0,1,0) )
      self.add_point ( point(1,0,0) )
      self.add_face ( face ( 0, 1, 2 ) )
      self.add_face ( face ( 0, 1, 3 ) )
      self.add_face ( face ( 0, 2, 3 ) )
      self.add_face ( face ( 1, 2, 3 ) )

    if file_name != None:
      try:
        f = open ( file_name, 'r' )
        lines = f.readlines();

        mode = ""

        for line in lines:
          l = line.strip()

          if l == "VERTEX_LIST":
            mode = 'v'
          elif l == "ELEMENT_CONNECTIONS":
            mode = 'f'
          elif l == "}":
            mode = ""

          if (len(l)>1):
            if (l[0] == '[') and (l[-1] == ']'):
              # This is list
              v = l[1:-1].replace(',',' ').split()

              if mode == 'v':
                # This is a vertex
                self.add_point ( point ( float(v[0]), float(v[1]), float(v[2]) ) )
              elif mode == 'f':
                # This is a face
                self.add_face ( face ( int(v[0]), int(v[1]), int(v[2]) ) )
        f.close()
      except FileNotFoundError as ioe:
          # User has probably dragged off the time line, just ignore it
          pass
      except Exception as e:
          print ( "Exception reading MDL: " + str(e) )
      except:
          print ( "Unknown Exception" )


  def merge ( self, obj_to_add ):
    # Loop through all faces of the new object to be merged
    for oa_face in obj_to_add.faces:
      # Find point indexes that match in the target object or add them
      new_verts = [ -1, -1, -1 ];
      for new_vert_index in range(3):
        # Loop through all existing points in the target object looking for a match
        looking_for = None
        looking_for = obj_to_add.points[oa_face.verts[new_vert_index]]
        found = -1
        for p in self.points:
          if (p.x == looking_for.x) and (p.y == looking_for.y) and (p.z == looking_for.z):
            found = self.points.index(p)
            break
        if found >= 0:
          new_verts[new_vert_index] = found
        if (new_verts[new_vert_index] < 0):
          # The point was not found in the target object, so add it
          new_p = point ( looking_for.x, looking_for.y, looking_for.z );
          self.points.append ( new_p );
          new_verts[new_vert_index] = self.points.index(new_p);

      new_f = face(new_verts[0], new_verts[1], new_verts[2]);
      self.faces.append ( new_f );



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
      new_face = plf_object();  
      new_face.add_point ( self.points[f[0]] );
      new_face.add_point ( self.points[f[1]] );
      new_face.add_point ( self.points[f[2]] );
      new_face.add_face ( face (0, 1, 2) );
      self.merge ( new_face );



from bpy.app.handlers import persistent

def add_handler ( handler_list, handler_function ):
    """ Only add a handler if it's not already in the list """
    if not (handler_function in handler_list):
        handler_list.append ( handler_function )


def remove_handler ( handler_list, handler_function ):
    """ Only remove a handler if it's in the list """
    if handler_function in handler_list:
        handler_list.remove ( handler_function )


@persistent
def box_frame_change_handler(scene):
  scene.box_maker.update_scene(scene)


def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.box_maker = bpy.props.PointerProperty(type=BoxMakerPropertyGroup)
    add_handler ( bpy.app.handlers.frame_change_pre, box_frame_change_handler )


def unregister():
    print ("Unregistering ", __name__)
    remove_handler ( bpy.app.handlers.frame_change_pre, box_frame_change_handler )
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.box_maker

if __name__ == "__main__":
    register()

