bl_info = {
  "version": "0.1",
  "name": "Capsule Test",
  'author': 'Bob',
  "location": "Properties > Scene",
  "category": "Cell Modeling"
  }


"""
Dynamic Geometry Demo:

  Start Blender with Factory Settings (may need to save startup and restart)
  Delete everything from the Scene (a,a,x,Delete)
  Enable CellBlender and Capsule Test Addons
  Open CellBlender tab, Initialize CellBlender, Expand the panel

  Open the "Growing Capsule" Tab (beside CellBlender)
  Disable "Freeze Geometry" (defaulted to frozen to minimize interference)
  Check the "Use CellBlender Data" box to get iterations from CellBlender
  Drag the time line to watch the geometry change
  Zoom in on object and right click to select it (outlined in orange)
  When selected, set the Maximum Draw Type to "Wire" (easier to see molecules)
  You can change Geometry Settings here, but leave as is the first time
  Save the .blend file somewhere to start a new project (File / SaveAs)

  Begin building your CellBlender project with the Model Objects Panel
  With the capsule selected, click the "+" button to add it to the model objects
  Add volume and surface molecules to the model and release them in and on the capsule
    Add molecules "v" (Volume 1e-5) and "s" (Surface 1e-4)
    Release 1000 of each on Object/Region "capsule"

  Open the Preferences panel and "Set Path to MCell Binary" to dynamic geometry mcell

  Open the "Run" panel and expand the Output/Control Options subpanel
  Check the "Decouple Export and Run" button so you can export and run separately
  Set the time on the timeline to zero (0) so your geometry.mdl file will start there
  Click the Export CellBlender Project button to export all of your static MDL

  Open the Growing Capsule tab again
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
     "Update MDL Files" in the Growing Capsule tab
     Run the  simulation and reload the visualization data

  The procedure for changing the geometry is very similar:

     Change values in the Growing Capsule panel and check with timeline
     Set the time to zero to export the original geometry file
     "Export CellBlender Project" in the CellBlender Run Simulation Panel
     "Update MDL Files" in the Growing Capsule tab
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
    self.path_to_mdl = cellblender.cellblender_utils.project_files_path()
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
    #self.show_calc_geometry = not self.show_calc_geometry
    if self.show_MDL_geometry == self.show_calc_geometry:
        self.show_MDL_geometry = not self.show_calc_geometry
        self.display_callback(context)
    return

def show_mdl_callback(self, context):
    if self.show_MDL_geometry == self.show_calc_geometry:
        self.show_calc_geometry = not self.show_MDL_geometry
        self.display_callback(context)
    return


class CapsuleMakerPropertyGroup(bpy.types.PropertyGroup):

    # Properties for the Capsule
    
    ns  = bpy.props.IntProperty(name="Radial Segments", min=3, default=7, update=display_callback)              # Number of sections around the circumference of the cylinder
    ncf = bpy.props.IntProperty(name="Num Cap Facets", min=1, default=3, update=display_callback)               # Number of cap facets from side to tip
    ilength = bpy.props.FloatProperty(name="Initial Length", min=0.0, default=2.0, update=display_callback)     # Initial length of entire object from tip to tip
    flength = bpy.props.FloatProperty(name="Final Length", min=0.0, default=7.0, update=display_callback)       # Final length of entire object from tip to tip
    mnclength = bpy.props.FloatProperty(name="Min Cell Length", min=0.0, default=2.0, update=display_callback)  # Minimum length of a single cell
    mxclength = bpy.props.FloatProperty(name="Max Cell Length", min=0.0, default=3.2, update=display_callback)  # Maximum length of a single cell
    glength = bpy.props.FloatProperty(name="Gap Length", min=0.0, default=0.05, update=display_callback)        # Distance between cells
    radius = bpy.props.FloatProperty(name="Radius", min=0.0, default=0.5, update=display_callback)              # Radius of cylinder
    num_frames = bpy.props.IntProperty(name="Num Frames", min=2, default=1000, update=display_callback)          # Frames from start to finish
    pinch = bpy.props.BoolProperty(name="Pinch when Dividing", default=True, update=display_callback)
    wire = bpy.props.BoolProperty(name="Wire", default=False, update=display_callback)
    disabled = bpy.props.BoolProperty(name="Freeze Geometry", default=True, update=display_callback)
    time_step = bpy.props.FloatProperty(name="Time Step", default=0.000005)
    all_frames = bpy.props.BoolProperty(name="All Frames", default=True)

    cell_name = bpy.props.StringProperty(name="CellName", default="capsule")

    use_cellblender_data = bpy.props.BoolProperty(name="Use CellBlender Data", default=False,  update=use_cellblender_data_callback)
    user_path_to_mdl = bpy.props.StringProperty(name="User_UseCBD", default="")
    user_time_step = bpy.props.FloatProperty(name="User_TS", default=-1.0)
    user_num_frames = bpy.props.IntProperty(name="User_NF", default=-1)

    path_to_mdl = bpy.props.StringProperty(name="", default="")

    show_calc_geometry = bpy.props.BoolProperty(name="Show Calculated Geometry", default=True,  update=show_calc_callback)
    show_MDL_geometry  = bpy.props.BoolProperty(name="Show MDL Geometry",        default=False, update=show_mdl_callback)


    test_status = bpy.props.StringProperty(name="TestStatus", default="?")

    def get_path_to_mdl ( self, context ):
        return self.path_to_mdl

    def display_callback(self, context):
        # Refresh the scene
        # print ( "Display Callback called" )
        self.update_scene (context.scene)
        context.scene.update()  # It's also not clear if this is needed ... but it doesn't seem to hurt!!
        return

    def update_scene ( self, scene ):
        if not self.disabled:
            # print ( "Updating with " + str(self.show_calc_geometry) + " " + str(self.show_MDL_geometry) )
            # print ( "Updating Scene at " + str(scene.frame_current) )
            app = scene.capsule_maker

            """
            # Delete all mesh objects
            bpy.ops.object.select_all(action='DESELECT')
            for scene_object in scene.objects:
              if scene_object.type == 'MESH':
                # print ( "Deleting mesh object: " + scene_object.name )
                scene_object.hide = False
                scene_object.select = True
                bpy.ops.object.delete()
            """

            capsule_chain_plf = None
            if self.show_calc_geometry:
                capsule_chain_plf = self.create_capsule_chain ( scene )
            else:
                capsule_chain_plf = self.read_plf_from_mdl ( scene )

            vertex_list = capsule_chain_plf.points
            face_list = capsule_chain_plf.faces

            # print ( "===> Creating an object from " + str(len(vertex_list)) + " vertices and " + str(len(face_list)) + " faces." )
            vertices = []
            for point in vertex_list:
                vertices.append ( mathutils.Vector((point.x,point.y,point.z)) )
            faces = []
            for face_element in face_list:
                faces.append ( face_element.verts )

            new_mesh = bpy.data.meshes.new ( self.cell_name + "_mesh" )
            new_mesh.from_pydata ( vertices, [], faces )
            new_mesh.update()
            
            capsule_object = None
            if self.cell_name in scene.objects:
                # print ( "Object exists, so just update the mesh" )
                capsule_object = scene.objects[self.cell_name]
                old_mesh = capsule_object.data
                capsule_object.data = new_mesh
                bpy.data.meshes.remove ( old_mesh )
            else:
                # print ( "Object doesn't exist, so create a new one" )
                capsule_object = bpy.data.objects.new ( self.cell_name, new_mesh )
                scene.objects.link ( capsule_object )

            #bpy.ops.object.select_all ( action = "DESELECT" )
            #capsule_object.select = True
            #scene.objects.active = capsule_object

            """
            draw_type = None
            if app.wire:
                draw_type = "WIRE" #  one of: WIRE, TEXTURED, SOLID, BOUNDS

            if draw_type != None:
                bpy.data.objects[self.cell_name].draw_type = draw_type
            """

            #bpy.ops.object.mode_set ( mode="OBJECT" )
            # print ( "Done Adding " + self.cell_name )



    def read_plf_from_mdl ( self, scene, frame_num=None ):

        # print ( "Redraw Frame " + str(frame_num) + ", Save as " + str(save_as) )

        cur_frame = frame_num
        if cur_frame == None:
          cur_frame = scene.frame_current

        # print ( "Redraw Frame " + str(cur_frame) )

        app = scene.capsule_maker

        fname = "frame_%d.mdl"%cur_frame
        full_fname = None
        if cur_frame == 0:
            # This geometry file is saved as a normal geometry MDL file and not included in the dynamic geometry file list
            full_fname = os.path.join(app.path_to_mdl,"Scene.geometry.mdl")
        else:
            # This geometry file is saved as a dynamic geometry MDL file and is included in the dynamic geometry file list
            path_to_dg_files = os.path.join ( app.path_to_mdl, "dynamic_geometry" )
            full_fname = os.path.join(path_to_dg_files,fname)

        # print ( "Read from " + str(full_fname) )
        plf_from_mdl = plf_object()
        plf_from_mdl.read_from_regularized_mdl (file_name = full_fname )

        return plf_from_mdl



    def create_capsule_chain ( self, scene, frame_num=None ):

        # print ( "Redraw Frame " + str(frame_num) + ", Save as " + str(save_as) )

        cur_frame = frame_num
        if cur_frame == None:
          cur_frame = scene.frame_current

        # print ( "Redraw Frame " + str(cur_frame) )

        app = scene.capsule_maker

        # Create a dividing capsule
        
        ns = app.ns               # Number of sections around the circumference of the cylinder
        ncf = app.ncf             # Number of cap facets from side to tip
        mnclength = app.mnclength # Minimum Length of each cell from tip to tip
        mxclength = app.mxclength # Maximum Length of each cell from tip to tip
        glength = app.glength     # Length of the gap between each cell
        radius = app.radius       # Radius of cylinder
        pinch = app.pinch         # Pinch if true
        wire = app.wire           # Force Wire Drawing

        total_length = app.ilength + ( cur_frame * (app.flength-app.ilength) / app.num_frames ) # Length of entire object from tip to tip
        
        capsule_chain_plf = self.make_capsule_chain_mesh ( total_length, mxclength, radius, ns, ncf, glength, pinch )
        
        return capsule_chain_plf



    def make_capsule_chain_mesh ( self, total_length, max_cell_length, radius, num_radial_sections, num_cap_facets, gap_dist, pinch ):

        # print ( "Make Capsule Chain of length " + str(total_length) )

        # Create the radial profile of the "chain" of capsule cells

        # As a cell approaches its maximum length, it will start to split by constricting in the middle
        # At the point of it's maximum length, it will have constricted to zero radius in the middle
        # The constriction area ranges from 0 to the cell radius
        # If cell is less than max_cell_length - radius, then there is no constriction zone
        # When the cell is between (max_cell_length - radius) and (max_cell_length) there will be a constriction
        #
        
        # Start with the total length based on the current time frame:
        
        # Compute the number of cells
        
        norm_length = total_length / (max_cell_length + gap_dist)
        num_cells = int ( math.pow ( 2, int ( math.log2 ( 2 * norm_length ) ) ) )
        if num_cells < 1: num_cells = 1
        seglength = total_length/num_cells
        cell_length = seglength - (gap_dist)
        
        capsule_z_profile = []
        
        hg = gap_dist / 2.0
        z = -total_length / 2.0
        # z = z + hg
        capsule_z_profile = capsule_z_profile + [ (z, 0.0) ]
        for cnum in range(num_cells):

          # Create the bottom cap

          for fn in range(num_cap_facets):
            angle = fn * (math.pi/2) / num_cap_facets
            capsule_z_profile = capsule_z_profile + [ ( z+hg+(radius*((1-math.cos(angle)))), radius*math.sin(angle) ) ]
          
          capsule_z_profile = capsule_z_profile + [ ( z+hg+radius, radius ) ]

          # Create the cylinder for the main body
          
          cylinder_length = cell_length - (2 * radius)
          nominal_length = math.pi * radius / (2 * num_cap_facets)
          num_segments = round ( (cylinder_length + (nominal_length/2)) / nominal_length )
          
          # Force an even number of segments so there's a pinch center
          if (num_segments % 2) > 0:
            num_segments += 1

          bot_z = z + hg + radius
          for cyl_seg_num in range(num_segments-1):
            pinch_factor = 1.0
            if pinch and (cell_length > (max_cell_length - (2*radius))):
              # Need to start pinching the center
              pinch_dist = ( cell_length - (max_cell_length - (2*radius)) ) / 2
              if pinch_dist > 0:
                dist_from_center = ((cyl_seg_num+1) * cylinder_length / num_segments) - (cylinder_length/2)
                if abs(dist_from_center) < pinch_dist:
                  norm_dist = abs(dist_from_center) / radius
                  pinch_factor = math.sin ( math.acos((pinch_dist/radius)-norm_dist) )
            
            capsule_z_profile = capsule_z_profile + [ ( bot_z + (cylinder_length*(cyl_seg_num+1)/num_segments), radius * pinch_factor ) ]


          # Create the top cap

          capsule_z_profile = capsule_z_profile + [ ( z+seglength-(radius+hg), radius ) ]

          for fn in range(num_cap_facets):
            angle = ((num_cap_facets-1)-fn) * (math.pi/2) / num_cap_facets
            capsule_z_profile = capsule_z_profile + [ ( z+seglength+(radius*((0+math.cos(angle))))-(radius+hg), radius*math.sin(angle) ) ]

          z += seglength

        capsule_z_profile = capsule_z_profile + [ (z, 0.0) ]
        
        shaped_cyl = ShapedCylinder ( num_radial_sections, capsule_z_profile )

        return shaped_cyl


class CapsuleMakerPanel(bpy.types.Panel):
    bl_label = "Growing Capsule"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Growing Capsule"
    #bl_space_type = "PROPERTIES"
    #bl_region_type = "WINDOW"
    #bl_context = "scene"
    def draw(self, context):
        app = context.scene.capsule_maker

        box = self.layout.box()
        row = box.row()
        row.label ( "Geometry Settings" )
        row = box.row()
        row.prop ( app, "num_frames" )
        row.prop ( app, "ilength" )
        row.prop ( app, "flength" )
        row = box.row()
        # row.prop ( app, "mnclength" )
        row.prop ( app, "mxclength" )
        row.prop ( app, "glength" )
        row = box.row()
        row.prop ( app, "ns" )
        row.prop ( app, "ncf" )
        row.prop ( app, "radius" )
        row = box.row()
        row.prop ( app, "pinch" )
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
            row.operator ( "capsule_maker.set_blend_path" )
            row = box.row()
            row.prop ( app, "path_to_mdl" )
            row = box.row()
            row.prop ( app, "time_step" )
            row.prop ( app, "all_frames" )
        row = box.row()
        row.operator ( "capsule_maker.gen_mdl_geom" )
        row.operator ( "capsule_maker.update_mdl_files" )

        #row = self.layout.row()
        #row.operator ( "capsule_maker.save_home_file" )
        #row.operator ( "capsule_maker.load_home_file" )


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

        mdl_file = open ( full_fname, "w" )
        line_num = 0
        for line in lines:
            line_num += 1
            mdl_file.write ( line )
            if line_num == 3:
                # Insert the dynamic geometry line
                mdl_file.write ( "DYNAMIC_GEOMETRY = \"capsule_dyn_geom_list.txt\"\n" )
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
    bl_idname = "capsule_maker.gen_mdl_geom"
    bl_label = "Generate Dynamic Geometry MDL"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        print ( "Generating Dynamic MDL" )

        app = context.scene.capsule_maker

        if app.use_cellblender_data:
            # Force an update of the CellBlender values in case they've changed
            copy_cellblender_data(app,context)
        
        # This section gets the number of frames from the time line:
        #if context.scene.capsule_maker.all_frames:
        #    start = context.scene.frame_start
        #    end = context.scene.frame_end
        #else:
        #    start = context.scene.frame_current
        #    end = context.scene.frame_current

        # This section gets the number of frames from the setting:
        start = 1
        end = app.num_frames
        
        print ( "Saving frames from " + str(start) + " to " + str(end) )
        # Make the directory in case CellBlender hasn't been run to make it already
        os.makedirs(app.path_to_mdl,exist_ok=True)
        geom_list_file = open(os.path.join(app.path_to_mdl,'capsule_dyn_geom_list.txt'), "w", encoding="utf8", newline="\n")
        path_to_dg_files = os.path.join ( app.path_to_mdl, "dynamic_geometry" )
        if not os.path.exists(path_to_dg_files):
            os.makedirs(path_to_dg_files)        
        step = 0
        for f in range(1 + 1+end-start):
            capsule_chain_plf = context.scene.capsule_maker.create_capsule_chain ( context.scene, frame_num=f )
            fname = "frame_%d.mdl"%f
            if f == 0:
                # This geometry file is saved as a normal geometry MDL file and not included in the dynamic geometry file list
                full_fname = os.path.join(app.path_to_mdl,"Scene.geometry.mdl")
                print ( "Saving file " + full_fname )
                capsule_chain_plf.write_as_mdl ( file_name=full_fname, partitions=False, instantiate=False )
            else:
                # This geometry file is saved as a dynamic geometry MDL file and is included in the dynamic geometry file list
                full_fname = os.path.join(path_to_dg_files,fname)
                print ( "Saving file " + full_fname )
                capsule_chain_plf.write_as_mdl ( file_name=full_fname, partitions=True, instantiate=True )
                geom_list_file.write('%.9g %s\n' % (step*context.scene.capsule_maker.time_step, os.path.join(".","dynamic_geometry",fname)))
            step += 1
        geom_list_file.close()
        update_mdl_files(app)
        """
        # Update the main MDL file Scene.main.mdl to insert the DYNAMIC_GEOMETRY directive
        try:
            full_fname = os.path.join(app.path_to_mdl,"Scene.main.mdl")
            mdl_file = open ( full_fname )
            mdl_lines = mdl_file.readlines()
            mdl_file.close()
            mdl_file = open ( full_fname, "w" )
            line_num = 0
            for line in mdl_lines:
                line_num += 1
                mdl_file.write ( line )
                if line_num == 3:
                    # Insert the dynamic geometry line
                    mdl_file.write ( "\nDYNAMIC_GEOMETRY = \"capsule_dyn_geom_list.txt\"\n" )
            mdl_file.close()
        except:
            print ( "Warning: unable to update the existing Scene.main.mdl file, try running the model to generate it first." )
        """
        return { 'FINISHED' }


class Update_MDL_Files(bpy.types.Operator):
    bl_idname = "capsule_maker.update_mdl_files"
    bl_label = "Update MDL Files"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        app = context.scene.capsule_maker
        update_mdl_files(app)
        return { 'FINISHED' }


class LoadHomeOp(bpy.types.Operator):
    bl_idname = "capsule_maker.load_home_file"
    bl_label = "Load Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        context.scene.capsule_maker.test_status == "?"
        context.scene.capsule_maker.groups_real = False
        bpy.ops.wm.read_homefile()
        return { 'FINISHED' }


class SaveHomeOp(bpy.types.Operator):
    bl_idname = "capsule_maker.save_home_file"
    bl_label = "Save Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        context.scene.capsule_maker.test_status == "?"
        bpy.ops.wm.save_homefile()
        return { 'FINISHED' }


class SetBlendPath(bpy.types.Operator):
    bl_idname = "capsule_maker.set_blend_path"
    bl_label = "Set Path to MDL Files"
    bl_description = ("Set Path to the Blend File created for each test.")
    bl_options = {'REGISTER'}

    def execute(self, context):
        app = context.scene.capsule_maker

        filepath = os.path.dirname(bpy.data.filepath)
        filepath, dot, blend = bpy.data.filepath.rpartition(os.path.extsep)
        filepath = filepath + "_files"
        app.path_to_mdl = os.path.join(filepath, "mcell")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class App_Model:

    old_type = None
    context = None
    scn = None
    path_to_blend = None
    
    def __init__(self, cb_context):
        # bpy.ops.wm.read_homefile()
        self.old_type = None
        self.context = cb_context
        self.setup_cb_defaults ( self.context )
        self.context.scene.capsule_maker.test_status == "?"
        
    def get_scene(self):
        return self.scn

    def get_3d_view_spaces(self):
        spaces_3d = []
        for area in self.context.screen.areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    spaces_3d = spaces_3d + [space]
                    # area.spaces.active.show_manipulator = False
        return spaces_3d


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

    def save_blend_file( self, context ):
        app = context.scene.capsule_maker
        wm = context.window_manager

        if len(app.path_to_blend) > 0:
            self.path_to_blend = app.path_to_blend
        else:
            self.path_to_blend = os.getcwd() + "/Test.blend"

        bpy.ops.wm.save_as_mainfile(filepath=self.path_to_blend, check_existing=False)


    def get_scene(self):
        return bpy.data.scenes['Scene']

    def delete_all_objects(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=True)


    def setup_cb_defaults ( self, context ):

        #self.save_blend_file( context )
        scn = self.get_scene()
        # self.set_view_3d()
        self.delete_all_objects()

        #print ( "Snapping Cursor to Center" )
        #bpy.ops.view3d.snap_cursor_to_center()
        #print ( "Done Snapping Cursor to Center" )
        
        self.scn = scn


    def create_object_from_mesh ( self, name="ObjectFromMesh", draw_type=None, x=0, y=0, z=0, vertex_list=None, face_list=None ):

        # print ( "===> Creating an object from " + str(len(vertex_list)) + " vertices and " + str(len(face_list)) + " faces." )
        vertices = []
        for point in vertex_list:
            vertices.append ( mathutils.Vector((point.x+x,point.y+y,point.z+z)) )
        faces = []
        for face_element in face_list:
            faces.append ( face_element.verts )

        new_mesh = bpy.data.meshes.new ( name + "_mesh" )
        new_mesh.from_pydata ( vertices, [], faces )
        new_mesh.update()
        new_obj = bpy.data.objects.new ( name, new_mesh )

        self.scn.objects.link ( new_obj )
        bpy.ops.object.select_all ( action = "DESELECT" )
        new_obj.select = True
        self.scn.objects.active = new_obj

        if draw_type != None:
            bpy.data.objects[name].draw_type = draw_type

        bpy.ops.object.mode_set ( mode="OBJECT" )
        # print ( "Done Adding " + name )


    def add_cube_to_model ( self, name="PLF", draw_type=None, x=0, y=0, z=0, size=1 ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_cube_add ( location=(x,y,z), radius=size)
        self.scn.objects.active.name = name
        if draw_type != None:
            bpy.data.objects[name].draw_type = draw_type

        print ( "Done Adding " + name )


    def add_icosphere_to_model ( self, name="PLF", draw_type=None, x=0, y=0, z=0, size=1, subdiv=2 ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_ico_sphere_add ( subdivisions=subdiv, size=size, location=(x, y, z) )
        self.scn.objects.active.name = name
        if draw_type != None:
            bpy.data.objects[name].draw_type = draw_type

        print ( "Done Adding " + name )


    def add_capsule_to_model ( self, name="PLF", draw_type=None, x=0, y=0, z=0, sigma=0, subdiv=2, radius=1, cyl_len=2, subdivide_sides=True ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        capsule = Capsule(subdiv,radius,cyl_len,subdivide_sides)
        capsule.dither_points ( sigma, sigma, sigma )
        #print ( "Writing capsule.plf" )
        #capsule.dump_as_plf ( "capsule.plf" )
        self.create_object_from_mesh ( name=name, draw_type=draw_type, x=x, y=y, z=z, vertex_list=capsule.points, face_list=capsule.faces )


    def add_plf_object_to_model ( self, plf_object, name="PLF", draw_type=None, x=0, y=0, z=0 ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        self.create_object_from_mesh ( name=name, draw_type=draw_type, x=x, y=y, z=z, vertex_list=plf_object.points, face_list=plf_object.faces )


    def add_label_to_model ( self, name="Label", text="Text", x=0, y=0, z=0, size=1, rx=0, ry=0, rz=0 ):
        print ( "Adding " + text )

        bpy.ops.object.text_add ( location=(x,y,z), rotation=(rx,ry,rz), radius=size )
        tobj = bpy.context.active_object
        tobj.data.body = text

        print ( "Done Adding " + text )


    def wait ( self, wait_time ):
        if self.all_processes_finished():
            print ( "============== ALL DONE ==============" )
        else:
            print ( "============== WAITING ==============" )
        import time
        time.sleep ( wait_time )


    def scale_view_distance ( self, scale ):
        """ Change the view distance for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_distance *= scale
        #bpy.ops.view3d.zoom(delta=3)
        #set_view_3d()

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
        app = bpy.context.scene.capsule_maker
        bpy.ops.screen.animation_play()



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
  
  def equals ( self, p ):
    if ( (self.x == p.x) and (self.y == p.y) and (self.z == p.z) ):
      return ( True );
    else:
      return ( False );

  def equals ( self, p ):
    return (self == p )

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


class line:
  p1 = point(0,0,0);
  p2 = point(0,0,0);

  def __init__ ( self, p1, p2 ):
    self.p1 = p1;
    self.p2 = p2;
  
  def toString( self ):
    return ( "["+str(p1.x)+","+str(p1.y)+","+str(p1.z)+"]-["+str(p2.x)+","+str(p2.y)+","+str(p2.z)+"]" );


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

  def offset_points ( self, dx, dy, dz ):
    for p in self.points:
      p.x += dx;
      p.y += dy;
      p.z += dz;

  def scale_points ( self, sx, sy, sz ):
    for p in self.points:
      p.x *= sx;
      p.y *= sy;
      p.z *= sz;

  def dither_points ( self, sigma_x, sigma_y, sigma_z ):
    g = random.gauss
    for p in self.points:
      p.x += g(0,sigma_x);
      p.y += g(0,sigma_y);
      p.z += g(0,sigma_z);

  def sqr ( self, v ):
    return ( v * v );

  def dump_as_plf ( self, file_name=None ):
    if file_name != None:
      out_file = open ( file_name, "w" )

    for p in self.points:
      if file_name == None:
        print ( "P " + str(p.x) + " " + str(p.y) + " " + str(p.z) );
      else:
        out_file.write ( "P " + str(p.x) + " " + str(p.y) + " " + str(p.z) + "\n" );

    for f in self.faces:
      for edge in range(3):
        p1i = f.verts[edge];
        p2i = f.verts[(edge+1)%3];
        if file_name == None:
          print  ( "L " + str(p1i) + " " + str(p2i) );
        else:
          out_file.write  ( "L " + str(p1i) + " " + str(p2i) + "\n" );

    for f in self.faces:
      s = "F"
      for vert in f.verts:
        s += " " + str(vert)
      if file_name == None:
        print ( s )
      else:
        out_file.write ( s + "\n" )

    if file_name != None:
      out_file.close()


  def write_as_mdl ( self, file_name=None, partitions=False, instantiate=False ):
    if file_name != None:
      out_file = open ( file_name, "w" )
      if partitions:
          out_file.write ( "PARTITION_X = [[-0.5 TO 0.5 STEP 0.1]]\n" )
          out_file.write ( "PARTITION_Y = [[-0.5 TO 0.5 STEP 0.1]]\n" )
          out_file.write ( "PARTITION_Z = [[-5.0 TO 5.0 STEP 0.1]]\n" )
          out_file.write ( "\n" )
      out_file.write ( "capsule POLYGON_LIST\n" )
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
      """
      out_file.write ( "  DEFINE_SURFACE_REGIONS\n" )
      out_file.write ( "  {\n" )
      out_file.write ( "    membrane\n" )
      out_file.write ( "    {\n" )
      out_file.write ( "      ELEMENT_LIST = " + str ( [i for i in range(len(self.faces))] ) + "\n" )
      out_file.write ( "    }\n" )
      out_file.write ( "  }\n" )
      """
      out_file.write ( "}\n" )
      if instantiate:
          out_file.write ( "\n" )
          out_file.write ( "INSTANTIATE Scene OBJECT {\n" )
          out_file.write ( "  capsule OBJECT capsule {}\n" )
          out_file.write ( "}\n" )
      out_file.close()


  def read_from_regularized_mdl ( self, file_name=None, partitions=False, instantiate=False ):

    # This function makes some assumptions about the format of the geometry in an MDL file

    #old_points = [ p for p in self.points ]
    #old_faces = [ f for f in self.faces ]

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
      # print ( "Reading MDL from file " + file_name )
      try:
        f = open ( file_name, 'r' )
        lines = f.readlines();

        mode = ""

        for line in lines:
          l = line.strip()
          # print ( " Line: " + l )

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
          #self.points = old_points
          #self.faces = old_faces
          pass
      except Exception as e:
          print ( "Exception reading MDL: " + str(e) )
      except:
          print ( "Unknown Exception" )


  def get_average_edge_length ( self ):
    len_sum = 0;
    num_summed = 0;
    for f in self.faces:
      for edge in range(3):
        p1i = f.verts[edge];
        p2i = f.verts[(edge+1)%3];
        p1 = self.points[p1i];
        p2 = self.points[p2i];
        len_sum += math.sqrt ( self.sqr(p1.x-p2.x) + self.sqr(p1.y-p2.y) + self.sqr(p1.z-p2.z) );
        num_summed += 1;
    # Handle the case where there are faces
    if num_summed == 0: num_summed = 1
    return ( len_sum / num_summed );


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
          #print ( "  I have: [" + str(p.x) + ","  + str(p.y) + ","  + str(p.z) + "]" )
          if (p.x == looking_for.x) and (p.y == looking_for.y) and (p.z == looking_for.z):
            found = self.points.index(p)
            break
        if found >= 0:
          #print ( "Found a point" )
          new_verts[new_vert_index] = found
        #else:
        #  print ( "Didn't find a point" )
        if (new_verts[new_vert_index] < 0):
          # The point was not found in the target object, so add it
          new_p = point ( looking_for.x, looking_for.y, looking_for.z );
          self.points.append ( new_p );
          new_verts[new_vert_index] = self.points.index(new_p);

        #for p in self.points:
        #  print ( "  I now have: [" + str(p.x) + ","  + str(p.y) + ","  + str(p.z) + "]" )

      new_f = face(new_verts[0], new_verts[1], new_verts[2]);
      self.faces.append ( new_f );

  def remove_point_by_index ( self, index ):
    # Start by removing all faces using this index
    n = len(self.faces)-1
    face_index = n;
    while face_index >= 0:
      f = self.faces[face_index]
      remove = False
      for point_index in range(3):
        if (f.verts[point_index] == index):
          remove = True;
          break;
      if (remove):
        self.faces.pop( face_index );
      face_index += -1

    # Renumber all point indices greater than the index to be removed
    for f in self.faces:
      for point_index in range(3):
        if (f.verts[point_index] > index):
          f.verts[point_index] += -1;

    # Now remove the point itself
    self.points.pop ( index );


  def remove_all_with_z_gt ( self, z ):
    self.remove_all_with_z ( z, True );

  def remove_all_with_z_lt ( self, z ):
    self.remove_all_with_z ( z, False );

  def remove_all_with_z ( self, z, gt ):
    n = len(self.points)-1;
    point_index = n
    while point_index >= 0:
      p = self.points[point_index];
      remove = False;
      if (gt):
        if (p.z > z):
          remove = True;
      else:
        if (p.z < z):
          remove = True;
      if (remove):
        self.remove_point_by_index ( point_index ); # This removes faces as well
      point_index += -1

  def get_all_with_z_at ( self, z, tolerance ):
    result_list = []
    for point_index in range(len(self.points)):
      p = self.points[point_index];
      if ( (p.z >= z-tolerance) and (p.z <= z+tolerance) ):
        result_list.append ( point_index );
    result = None
    if len(result_list) > 0:
      result = []
      for i in range(len(result_list)):
        result.append ( result_list[i] );
    return ( result );



class IcoSphere ( plf_object ):

  # Subclass of plf_object that builds an icosphere with recursion

  def add_normalized_vertex ( self, p ):
    # Normalize the point
    # Add to the list of points if it's not already in the list
    # Return an index to the new or existing point in the list

    l = math.sqrt ( (p.x * p.x) + (p.y * p.y) + (p.z * p.z) );
    pnorm = point ( p.x/l, p.y/l, p.z/l );

    # Check if it's already there
    index = -1;
    for pt in self.points:
      if (pt.x == pnorm.x) and (pt.y == pnorm.y) and (pt.z == pnorm.z):
        index = self.points.index(pt)
        break;

    if (index < 0):
      self.points.append ( pnorm );
      index = self.points.index ( pnorm );
      #print ( "Added vertex at " + str(index) );
    #else:
    #  print ( "Found vertex at " + str(index) );
    return (index);


  def __init__ ( self, recursion_level ):

    self.points = [];

    t = (1.0 + math.sqrt(5.0)) / 2.0;  # Approx 1.618033988749895
    
    # Create 12 verticies from the 3 perpendicular planes whose corners define an icosahedron

    self.add_normalized_vertex ( point (-1,  t,  0) );
    self.add_normalized_vertex ( point ( 1,  t,  0) );
    self.add_normalized_vertex ( point (-1, -t,  0) );
    self.add_normalized_vertex ( point ( 1, -t,  0) );

    self.add_normalized_vertex ( point ( 0, -1,  t) );
    self.add_normalized_vertex ( point ( 0,  1,  t) );
    self.add_normalized_vertex ( point ( 0, -1, -t) );
    self.add_normalized_vertex ( point ( 0,  1, -t) );

    self.add_normalized_vertex ( point ( t,  0, -1) );
    self.add_normalized_vertex ( point ( t,  0,  1) );
    self.add_normalized_vertex ( point (-t,  0, -1) );
    self.add_normalized_vertex ( point (-t,  0,  1) );
    
    
    # Rotate all points such that the resulting icosphere will be separable at the equator
    
    if (True):
      # A PI/6 rotation about z (transform x and y) gives an approximate equator in x-y plane
      angle = (math.pi / 2) - math.atan(1/t);
      print ( "Rotating with angle = " + str(180 * angle / math.pi) );
      for p in self.points:
        newx = (math.cos(angle) * p.x) - (math.sin(angle) * p.z);
        newz = (math.sin(angle) * p.x) + (math.cos(angle) * p.z);
        p.x = newx;
        p.z = newz;

    # Build the original 20 faces for the Icosphere

    self.faces = []

    # Add 5 faces around point 0 (top)
    self.faces.append ( face (  0, 11,  5 ) );    
    self.faces.append ( face (  0,  5,  1 ) );    
    self.faces.append ( face (  0,  1,  7 ) );    
    self.faces.append ( face (  0,  7, 10 ) );    
    self.faces.append ( face (  0, 10, 11 ) );    

    # Add 5 faces adjacent faces
    self.faces.append ( face (  1,  5,  9 ) );    
    self.faces.append ( face (  5, 11,  4 ) );    
    self.faces.append ( face ( 11, 10,  2 ) );    
    self.faces.append ( face ( 10,  7,  6 ) );    
    self.faces.append ( face (  7,  1,  8 ) );    

    # Add 5 faces around point 3 (bottom)
    self.faces.append ( face (  3,  9,  4 ) );    
    self.faces.append ( face (  3,  4,  2 ) );    
    self.faces.append ( face (  3,  2,  6 ) );    
    self.faces.append ( face (  3,  6,  8 ) );    
    self.faces.append ( face (  3,  8,  9 ) );    

    # Add 5 faces adjacent faces
    self.faces.append ( face (  4,  9,  5 ) );    
    self.faces.append ( face (  2,  4, 11 ) );    
    self.faces.append ( face (  6,  2, 10 ) );    
    self.faces.append ( face (  8,  6,  7 ) );    
    self.faces.append ( face (  9,  8,  1 ) );
    

    # Subdivide the faces as requested by the recursion_level argument
    old_points = None;
    old_faces = None;
    
    for rlevel in range(recursion_level):
      # System.out.println ( "\nRecursion Level = " + rlevel );
      # Save the old points and faces and build a new set for this recursion level
      old_points = self.points;
      old_faces = self.faces;
      self.points = []
      self.faces = []
      for f in old_faces:
        # Split this face into 4 more faces
        midpoint = point(0,0,0)
        potential_new_points = []
        for i in range(6):
          potential_new_points.append ( point(0,0,0) )
        for side in range(3):
          p1 = old_points[f.verts[side]];
          p2 = old_points[f.verts[(side+1)%3]];
          midpoint = point ( ((p1.x+p2.x)/2), ((p1.y+p2.y)/2), ((p1.z+p2.z)/2) );
          potential_new_points[2*side] = p1;
          potential_new_points[(2*side)+1] = midpoint;
        # Add the 4 new faces
        # Start with the verticies ... add them all since add_normalized_vertex() will remove duplicates
        vertex_indicies = []
        for i in range(6):
          vertex_indicies.append ( 0 )
        for i in range(6):
          vertex_indicies[i] = self.add_normalized_vertex ( potential_new_points[i] );
        # Now add the 4 new faces
        self.faces.append ( face ( vertex_indicies[0], vertex_indicies[1], vertex_indicies[5] ) );
        self.faces.append ( face ( vertex_indicies[1], vertex_indicies[2], vertex_indicies[3] ) );
        self.faces.append ( face ( vertex_indicies[3], vertex_indicies[4], vertex_indicies[5] ) );
        self.faces.append ( face ( vertex_indicies[1], vertex_indicies[3], vertex_indicies[5] ) );



class Capsule (plf_object):


  def sort_ring_indicies ( self, ring ):
    for i in range(len(ring)):
      for j in range(i+1,len(ring)):
        pi = self.points[ring[i]];
        pj = self.points[ring[j]];
        itheta = math.atan2(pi.x, pi.y);
        jtheta = math.atan2(pj.x, pj.y);
        if (jtheta < itheta):
          temp = ring[i];
          ring[i] = ring[j];
          ring[j] = temp;


  def __init__ ( self, recursion_level, radius, height, subdivide_sides=True ):

    self.points = [];
    self.faces = []

    h = height/2; # h is the height of each half
    tol = 0.0001;

    # Make half of an icosphere for the bottom (start with the whole icosphere and remove the top half)
    ico = IcoSphere ( recursion_level );
    ico.remove_all_with_z_gt ( tol );
    ico.scale_points ( radius, radius, radius )
    ico.offset_points ( 0, 0, -h );
    self.merge ( ico );

    # Make half of an icosphere for the top (start with the whole icosphere and remove the bottom half)
    ico = IcoSphere ( recursion_level );
    ico.remove_all_with_z_lt ( -tol );
    ico.scale_points ( radius, radius, radius )
    ico.offset_points ( 0, 0, h );
    self.merge ( ico );
    
    # Get the bottom and top rings to make the side faces
    bot_ring = self.get_all_with_z_at(-h, tol);
    top_ring = self.get_all_with_z_at(h, tol);

    # Make the sides
    if ((bot_ring==None) or (top_ring==None)):
      print ( "Error: one of the rings is null" );
    elif (len(bot_ring) != len(top_ring)):
      print ( "Error: rings are not the same length" );
    elif (h <= 0):
      print ( "Note: no height to make the cylinder" );
    else:
      self.sort_ring_indicies ( bot_ring );
      self.sort_ring_indicies ( top_ring );
      
      if not subdivide_sides:

        # Create a single face with only two triangles for each face of the cylinder

        n = len(bot_ring)

        # Loop around the circumference of the cylinder
        for i in range(n):

          # Get the corner points of the entire face from top to bottom
          cb1 = self.points[bot_ring[i]];
          ct1 = self.points[top_ring[i]];
          cb2 = self.points[bot_ring[(i+1)%n]];
          ct2 = self.points[top_ring[(i+1)%n]];

          # Make two triangular faces for this full-length rectangle

          new_face = plf_object();
          new_face.add_point ( cb1 );
          new_face.add_point ( ct1 );
          new_face.add_point ( cb2 );
          new_face.add_face ( face (0, 1, 2) );
          self.merge ( new_face );

          new_face = plf_object();
          new_face.add_point ( ct1 );
          new_face.add_point ( ct2 );
          new_face.add_point ( cb2 );
          new_face.add_face ( face (0, 1, 2) );
          self.merge ( new_face );

      else:

        # Segment the cylinder along its length to create roughly square (but triangulated) segments

        avg_len = self.get_average_edge_length();
        num_segs = int(math.floor(((2*h)+(avg_len/2)) / avg_len));
        if (num_segs <= 0):
          num_segs = 1;
        
        # Loop through each ring segment from bottom to top
        for seg_num in range(num_segs):

          n = len(bot_ring)

          # Loop around the circumference of the cylinder
          for i in range(n):

            # Get the corner points of the entire face from top to bottom
            cb1 = self.points[bot_ring[i]];
            ct1 = self.points[top_ring[i]];
            cb2 = self.points[bot_ring[(i+1)%n]];
            ct2 = self.points[top_ring[(i+1)%n]];
            
            # print ( "Corners: " + str(cb1.x) + "," + str(ct1.x) + "," + str(cb2.x) + "," + str(ct2.x) )

            # Start out assuming they fill to all 4 corners
            pb1 = point (cb1.x, cb1.y, cb1.z);
            pt1 = point (ct1.x, ct1.y, ct1.z);
            pb2 = point (cb2.x, cb2.y, cb2.z);
            pt2 = point (ct2.x, ct2.y, ct2.z);

            if (seg_num > 0):
              # Need to interpolate the bottom because it's no longer the bottom ring
              pb1.x = cb1.x + ((ct1.x-cb1.x)*(seg_num * 1.0 / num_segs));
              pb1.y = cb1.y + ((ct1.y-cb1.y)*(seg_num * 1.0 / num_segs));
              pb1.z = cb1.z + ((ct1.z-cb1.z)*(seg_num * 1.0 / num_segs));

              pb2.x = cb2.x + ((ct2.x-cb2.x)*(seg_num * 1.0 / num_segs));
              pb2.y = cb2.y + ((ct2.y-cb2.y)*(seg_num * 1.0 / num_segs));
              pb2.z = cb2.z + ((ct2.z-cb2.z)*(seg_num * 1.0 / num_segs));

            if (seg_num < (num_segs-1)):
              # Need to interpolate the top because it's not the top ring
              pt1.x = cb1.x + ((ct1.x-cb1.x)*((seg_num+1) * 1.0 / num_segs));
              pt1.y = cb1.y + ((ct1.y-cb1.y)*((seg_num+1) * 1.0 / num_segs));
              pt1.z = cb1.z + ((ct1.z-cb1.z)*((seg_num+1) * 1.0 / num_segs));

              pt2.x = cb2.x + ((ct2.x-cb2.x)*((seg_num+1) * 1.0 / num_segs));
              pt2.y = cb2.y + ((ct2.y-cb2.y)*((seg_num+1) * 1.0 / num_segs));
              pt2.z = cb2.z + ((ct2.z-cb2.z)*((seg_num+1) * 1.0 / num_segs));

            # Make the two triangular faces for this rectangle

            new_face = plf_object();
            new_face.add_point ( pb1 );
            new_face.add_point ( pt1 );
            new_face.add_point ( pb2 );
            new_face.add_face ( face (0, 1, 2) );
            self.merge ( new_face );

            new_face = plf_object();
            new_face.add_point ( pt1 );
            new_face.add_point ( pt2 );
            new_face.add_point ( pb2 );
            new_face.add_face ( face (0, 1, 2) );
            self.merge ( new_face );




class ShapedCylinder (plf_object):

  def sort_ring_indicies ( self, ring ):
    for i in range(len(ring)):
      for j in range(i+1,len(ring)):
        pi = self.points[ring[i]];
        pj = self.points[ring[j]];
        itheta = math.atan2(pi.x, pi.y);
        jtheta = math.atan2(pj.x, pj.y);
        if (jtheta < itheta):
          temp = ring[i];
          ring[i] = ring[j];
          ring[j] = temp;


  def __init__ ( self, num_sectors, z_profile ):
    """ z_profile is a sorted list of tuples where each tuple is (z,r), and the list is sorted with increasing z """

    self.points = [];
    self.faces = [];
    
    # Make the sides

    if ( len(z_profile) < 2 ):

      print ( "Error: z-profile must contain at least 2 entries (bottom and top)" );

    else:

      # Build the cylinder from bottom to top creating faces along the way

      # Loop through each ring segment from bottom to top (start with lowest ring as "upper")
      lower_z = -1
      lower_r = -1
      lower_ring = []
      upper_ring = []

      for seg_num in range(len(z_profile)):

        # Prepare to build a new upper ring
        upper_z = z_profile[seg_num][0]
        upper_r = z_profile[seg_num][1]

        # Loop around the circumference of the cylinder building a new upper ring
        if upper_r > 0:
          for i in range(num_sectors):
            theta = i * 2 * math.pi / num_sectors
            new_point = point ( upper_r*math.cos(theta), upper_r*math.sin(theta), upper_z )
            self.points = self.points + [ new_point ]
            upper_ring = upper_ring + [ new_point ]
        elif upper_r == 0:
          new_point = point ( 0.0, 0.0, upper_z )
          self.points = self.points + [ new_point ]
          for i in range(num_sectors):
            upper_ring = upper_ring + [ new_point ]

        if (seg_num > 0) and (len(upper_ring) > 0) and (len(lower_ring) > 0):
        
          # Both the upper and lower rings exist and are valid, so build the faces

          for i in range(num_sectors):

            # Make the faces for this rectangle / triangle

            pb1 = lower_ring[i];
            pt1 = upper_ring[i];
            pb2 = lower_ring[(i+1)%num_sectors];
            pt2 = upper_ring[(i+1)%num_sectors];

            if (lower_r >= 0) and (upper_r > 0):

              # We have either a triangle or a rectangle. Make this face.

              new_face = plf_object();  
              new_face.add_point ( pt1 );
              new_face.add_point ( pt2 );
              new_face.add_point ( pb2 );
              new_face.add_face ( face (0, 2, 1) );
              self.merge ( new_face );

            if (upper_r >= 0) and (lower_r > 0):

              # We have either a triangle or a rectangle. Make this face.

              new_face = plf_object();
              new_face.add_point ( pb1 );
              new_face.add_point ( pt1 );
              new_face.add_point ( pb2 );
              new_face.add_face ( face (0, 2, 1) );
              self.merge ( new_face );
              
        # Move the upper ring down to the lower ring
        lower_z = upper_z
        lower_r = upper_r
        lower_ring = upper_ring
        upper_ring = []



from bpy.app.handlers import persistent

def add_handler ( handler_list, handler_function ):
    """ Only add a handler if it's not already in the list """
    if not (handler_function in handler_list):
        handler_list.append ( handler_function )
        
        #cellblender_added_handlers


def remove_handler ( handler_list, handler_function ):
    """ Only remove a handler if it's in the list """
    if handler_function in handler_list:
        handler_list.remove ( handler_function )


# Load scene callback
#@persistent
#def scene_loaded(dummy):
#    #bpy.context.scene.capsule_maker.make_real()
#    pass

@persistent
def capsule_frame_change_handler(scene):
  # print ( "Frame changed" )
  scene.capsule_maker.update_scene(scene)


def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.capsule_maker = bpy.props.PointerProperty(type=CapsuleMakerPropertyGroup)
    add_handler ( bpy.app.handlers.frame_change_pre, capsule_frame_change_handler )
    #add_handler ( bpy.app.handlers.scene_update_pre, scene_loaded )


def unregister():
    print ("Unregistering ", __name__)
    remove_handler ( bpy.app.handlers.frame_change_pre, capsule_frame_change_handler )
    #remove_handler ( bpy.app.handlers.scene_update_pre, scene_loaded )
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.capsule_maker

if __name__ == "__main__":
    register()

# test call
#bpy.ops.modtst.dialog_operator('INVOKE_DEFAULT')


