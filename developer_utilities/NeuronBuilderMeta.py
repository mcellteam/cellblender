import math
import mathutils
import time

import bpy
from bpy.props import *
import bmesh

bl_info = {
	"name": "Neuron Builder Meta",
	"author": "Bob Kuczewski",
	"version": (1,0,0),
	"blender": (2,6,6),
	"location": "View 3D > Edit Mode > Tool Shelf",
	"description": "Generate a Neuron Mesh",
	"warning" : "",
	"wiki_url" : "http://salk.edu",
	"tracker_url" : "",
	"category": "Add Mesh",
}

class MakeNeuronMeta_Panel(bpy.types.Panel):
  bl_label = "BuildNeuronMeta"
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "scene"
  bl_options = {'DEFAULT_CLOSED'}

  def draw(self, context):
    mnm = context.scene.make_neuron_meta
    mnm.draw ( self.layout )

class MakeNeuronStick_Operator ( bpy.types.Operator ):
  bl_idname = "mnm.make_line_mesh"
  bl_label = "Make Line Mesh from File"
  bl_options = {"REGISTER", "UNDO"}
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "objectmode"

  def execute ( self, context ):
    print ( "Execute" )
    mnm = context.scene.make_neuron_meta
    mnm.build_neuron_stick_from_file ( context )
    return {"FINISHED"}

  def invoke ( self, context, event ):
    print ( "Invoke" )
    mnm = context.scene.make_neuron_meta
    mnm.build_neuron_stick_from_file ( context )
    return {"FINISHED"}

class SaveNeuronStick_Operator ( bpy.types.Operator ):
  bl_idname = "mnm.save_as_update"
  bl_label = "Save Line Mesh Update File"
  bl_options = {"REGISTER", "UNDO"}
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "objectmode"
  
  def save ( self, context ):
    mnm = context.scene.make_neuron_meta
    file_lines = mnm.get_swc_from_mesh_stick ( context )
    if file_lines == None:
      print ( "Unable to save file" )
    else:
      f = open ( mnm.neuron_file_name + ".out.swc", 'w' )
      for l in file_lines:
        f.write ( l + "\n" )
      f.close()

  def execute ( self, context ):
    print ( "Execute" )
    self.save ( context )
    return {"FINISHED"}

  def invoke ( self, context, event ):
    print ( "Invoke" )
    self.save ( context )
    return {"FINISHED"}

class MakeNeuronMeta_Operator ( bpy.types.Operator ):
  bl_idname = "mnm.make_neuron_from_file"
  bl_label = "Make Surface Mesh from File"
  bl_options = {"REGISTER", "UNDO"}
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "objectmode"

  def execute ( self, context ):
    print ( "Execute" )
    mnm = context.scene.make_neuron_meta
    segments = mnm.read_segments_from_file()
    mnm.build_neuron_meta_from_segments ( context, segments )
    return {"FINISHED"}

  def invoke ( self, context, event ):
    print ( "Invoke" )
    mnm = context.scene.make_neuron_meta
    segments = mnm.read_segments_from_file()
    mnm.build_neuron_meta_from_segments ( context, segments )
    return {"FINISHED"}

class MakeNeuronMeta_Operator ( bpy.types.Operator ):
  bl_idname = "mnm.make_neuron_from_data"
  bl_label = "Make Surface Mesh from Data"
  bl_options = {"REGISTER", "UNDO"}
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "objectmode"

  def execute ( self, context ):
    print ( "Execute" )
    mnm = context.scene.make_neuron_meta
    segments = mnm.read_segments_from_object(context)
    mnm.build_neuron_meta_from_segments ( context, segments )
    return {"FINISHED"}

  def invoke ( self, context, event ):
    print ( "Invoke" )
    mnm = context.scene.make_neuron_meta
    segments = mnm.read_segments_from_object(context)
    mnm.build_neuron_meta_from_segments ( context, segments )
    return {"FINISHED"}

class MakeNeuronMetaAnalyze_Operator ( bpy.types.Operator ):
  bl_idname = "mnm.analyze_file"
  bl_label = "Analyze File"
  bl_options = {"REGISTER", "UNDO"}
  bl_space_type = "PROPERTIES"
  bl_region_type = "WINDOW"
  bl_context = "objectmode"

  def execute ( self, context ):
    print ( "Execute" )
    mnm = context.scene.make_neuron_meta
    mnm.read_segments_from_file()
    return {"FINISHED"}

  def invoke ( self, context, event ):
    print ( "Invoke" )
    mnm = context.scene.make_neuron_meta
    mnm.read_segments_from_file()
    return {"FINISHED"}


def file_name_change ( self, context ):
  mnm = context.scene.make_neuron_meta
  mnm.file_name_change()
  

class MakeNeuronMetaPropGroup(bpy.types.PropertyGroup):
  # frames_dir = StringProperty(name="frames_dir", default="")
  neuron_file_name = StringProperty ( subtype='FILE_PATH', default="", update=file_name_change)
  neuron_file_data = StringProperty ( default="" )

  convert_to_mesh = BoolProperty ( name="Convert to Mesh", default=False )
  show_analysis = BoolProperty ( default=False )
  show_stick    = BoolProperty ( default=False )
  show_create   = BoolProperty ( default=False )
  file_analyzed = BoolProperty ( default=False )
  num_lines_in_file = IntProperty ( default=-1 )
  num_segments_in_file = IntProperty ( default=-1 )
  num_nodes_in_file = IntProperty ( default=-1 )
  largest_radius_in_file = FloatProperty ( default=-1 )
  smallest_radius_in_file = FloatProperty ( default=-1 )
  min_x = FloatProperty ( default=-1 )
  max_x = FloatProperty ( default=-1 )
  min_y = FloatProperty ( default=-1 )
  max_y = FloatProperty ( default=-1 )
  min_z = FloatProperty ( default=-1 )
  max_z = FloatProperty ( default=-1 )
  
  scale_file_data = FloatProperty ( default=1.0 )
  mesh_resolution = FloatProperty ( default=0.1 )
  min_forced_radius = FloatProperty ( default=0.0 )
  num_segs_limit = IntProperty ( default=0 )


  def draw ( self, layout ):

    box = layout.box()
    row = box.row(align=True)
    row.alignment = 'LEFT'

    if not self.show_analysis:
      row.prop(self, "show_analysis", icon='TRIA_RIGHT', text="Original File", emboss=False)
    else:
      row.prop(self, "show_analysis", icon='TRIA_DOWN', text="Original File", emboss=False)

      #row = box.row()
      #row.label ( "Neuron File:" )

      row = box.row()
      row.prop ( self, "neuron_file_name", text="" )

      row = box.row()
      row.operator ( "mnm.analyze_file" )

      if self.file_analyzed:
        row = box.row()
        box = row.box()
        row = box.row()
        row.label ( "File contains " + str(self.num_lines_in_file) + " lines." )
        row = box.row()
        row.label ( "File contains " + str(self.num_segments_in_file) + " segments." )
        row = box.row()
        row.label ( "File contains " + str(self.num_nodes_in_file) + " nodes." )
        row = box.row()
        row.label ( "Largest radius is %g" % self.largest_radius_in_file )
        row = box.row()
        row.label ( "Smallest radius is %g" % self.smallest_radius_in_file )
        row = box.row()
        row.label ( "X range: %g to %g" % (self.min_x, self.max_x) )
        row = box.row()
        row.label ( "Y range: %g to %g" % (self.min_y, self.max_y) )
        row = box.row()
        row.label ( "Z range: %g to %g" % (self.min_z, self.max_z) )

    box = layout.box()
    row = box.row(align=True)
    row.alignment = 'LEFT'

    if not self.show_stick:
      row.prop(self, "show_stick", icon='TRIA_RIGHT', text="Line Mesh", emboss=False)
    else:
      row.prop(self, "show_stick", icon='TRIA_DOWN', text="Line Mesh", emboss=False)

      row = box.row()
      row.operator ( "mnm.make_line_mesh" )
      row.operator ( "mnm.save_as_update" )


    box = layout.box()
    row = box.row(align=True)
    row.alignment = 'LEFT'

    if not self.show_create:
      row.prop(self, "show_create", icon='TRIA_RIGHT', text="Surface Mesh", emboss=False)
    else:
      row.prop(self, "show_create", icon='TRIA_DOWN', text="Surface Mesh", emboss=False)

      row = box.row()
      row.prop ( self, "scale_file_data", text="Scale File Factor" )
      row = box.row()
      row.prop ( self, "mesh_resolution", text="Resolution of the Final Mesh" )
      row = box.row()
      row.prop ( self, "min_forced_radius", text="Minimum Forced Radius" )
      row = box.row()
      row.prop ( self, "num_segs_limit", text="Limit Number of Segments" )
      #row = box.row()
      #row.prop ( self, "convert_to_mesh", text="Convert Meta to Mesh" )
      row = box.row()
      row.operator ( "mnm.make_neuron_from_file" )
      row.operator ( "mnm.make_neuron_from_data" )


  def file_name_change ( self ):
    self.read_segments_from_file()
    # self.file_analyzed = True


  def read_segments_from_object ( self, context ):
    # Read in the data
    segments = []
    
    print ( "Reading from active object" )

    if context.scene.objects.active == None:
      print ( "Select a mesh object to make active" )
    elif context.scene.objects.active.type != 'MESH':
      print ( "Active object is not a mesh" )
    else:
      obj = context.scene.objects.active
      mesh = obj.data
      verts = mesh.vertices
      print ( "Mesh has " + str(len(verts)) + " verts" )

      index_number_layer = mesh.vertex_layers_float['index_number']
      parent_index_layer = mesh.vertex_layers_float['parent_index']
      segment_type_layer = mesh.vertex_layers_float['segment_type']
      #packed_layer = mesh.vertex_layers_int['packed_data']
      radius_layer = mesh.vertex_layers_float['radius']

      self.num_nodes_in_object = 0
      num_total_segments = 0

      # Start by putting all points into a dictionary keyed by their label n

      point_dict = {}
      i = 0
      for v in verts:
        # Fields: n T x y z R P

        n = int(index_number_layer.data[i].value)
        # n = (packed_layer.data[i].value >> 17) & 0x03fff
        T = int(segment_type_layer.data[i].value)
        # T = packed_layer.data[i].value & 0x07
        x = v.co.x
        y = v.co.y
        z = v.co.z
        R = radius_layer.data[i].value
        P = int(parent_index_layer.data[i].value)
        # P = (packed_layer.data[i].value >> 3) & 0x03fff

        # For some reason, many of these fields need to be swapped!!

        #fields = [ str(int(P)), str(int(T)), str(x), str(y), str(z), str(int(n)), str(R) ]
        fields  = [ str(int(n)), str(int(T)), str(x), str(y), str(z), str(R), str(int(P)) ]

        print ( "  Fields from " + obj.name + " = " + str(fields) )
        point_dict[fields[0]] = fields
        i += 1

      sorted_int_keys = sorted ( [ int(k) for k in point_dict.keys() ] )
      point_keys = ( [ str(k) for k in sorted_int_keys ] )
      self.num_lines_in_file = len(point_keys)
      self.num_nodes_in_file = len(point_keys)

      # Next create the list of segments - one for each child that has a parent
      for k in point_keys:
        child_fields = point_dict[k]
        print ( "  Sorted Fields from " + obj.name + " = " + str(child_fields) )
        if child_fields[6] in point_keys:
          # This point has a parent, so make a segment from parent to child
          parent_fields = point_dict[child_fields[6]]
          px = float(parent_fields[2])
          py = float(parent_fields[3])
          pz = float(parent_fields[4])
          pr = float(parent_fields[5])
          cx = float(child_fields[2])
          cy = float(child_fields[3])
          cz = float(child_fields[4])
          cr = float(child_fields[5])
          segments = segments + [ [ [px, py, pz, pr], [cx, cy, cz, cr] ] ]
          num_total_segments += 1

      if self.num_segs_limit > 0:
        # Limit the number of segments
        segments = segments[0:self.num_segs_limit]
        num_total_segments = len(segments)

      self.num_segments_in_file = num_total_segments

      self.perform_analysis ( segments )

    return segments



  def read_segments_from_file ( self ):
    # Read in the data
    segments = []
    
    print ( "Reading from file " + self.neuron_file_name )

    self.num_nodes_in_file = 0
    num_total_segments = 0

    if (self.neuron_file_name[-4:] == ".nbf"):

      # Read Node Branch Format
      # Node Branch Format has explicit connections, but they're not needed with metaballs
      segment = []
      f = open ( self.neuron_file_name, 'r' )
      lines = f.readlines();
      self.num_lines_in_file = len(lines)
      for l in lines:
        l = l.strip()
        print ( "Line: " + l )
        if len(l) > 0:
          if l[0:6] == "Branch":
            print ( "Branch" )
            if len(segment) > 0:
              segments = segments + [ segment ]
              segment = []
              num_total_segments += 1
          if l[0:4] == "Node":
            print ( "Node" )
            values = l.split()[1:]
            segment = segment + [ values ]
            self.num_nodes_in_file += 1
      if len(segment) > 0:
        segments = segments + [ segment ]
        segment = []
        num_total_segments += 1

    elif (self.neuron_file_name[-4:] == ".swc") or (self.neuron_file_name[-8:] == ".swc.txt"):

      # Read SWC Format
      # SWC format has explicit connections, but they're not needed with metaballs
      """
      The format of an SWC file is fairly simple. It is a text file consisting of 
      a header with various fields beginning with a # character, 
      and a series of three dimensional points containing 
      an index, radius, type, and connectivity information. 
      The lines in the text file representing points have the following layout.

            n T x y z R P

            n is an integer label that identifies the current point and 
                increments by one from one line to the next.

            T is an integer representing the type of neuronal segment, 
                such as soma, axon, apical dendrite, etc. The standard 
                accepted integer values are given below.

                0 = undefined
                1 = soma
                2 = axon
                3 = dendrite
                4 = apical dendrite
                5 = fork point
                6 = end point
                7 = custom

            x, y, z gives the cartesian coordinates of each node.

            R is the radius at that node.
            P indicates the parent (the integer label) of the current 
                point or -1 to indicate an origin (soma).
      """
      # Note that the SWC format could define cyclic references,
      #   However, since we just need to generate segments, this is not a problem.
      #   This is done by making each segment only one line (from parent to child)
      
      # Start by reading all the points into a dictionary keyed by their label n

      f = open ( self.neuron_file_name, 'r' )
      lines = f.readlines();
      point_dict = {}
      for l in lines:
        l = l.strip()
        print ( "Line: " + l )
        if len(l) > 0:
          if l[0] != "#":
            fields = l.split()
            point_dict[fields[0]] = fields
      point_keys = sorted ( [ k for k in point_dict.keys() ] )
      self.num_lines_in_file = len(point_keys)
      self.num_nodes_in_file = len(point_keys)

      # Next create the list of segments - one for each child that has a parent
      for k in point_keys:
        child_fields = point_dict[k]
        if child_fields[6] in point_keys:
          # This point has a parent, so make a segment from parent to child
          parent_fields = point_dict[child_fields[6]]
          px = float(parent_fields[2])
          py = float(parent_fields[3])
          pz = float(parent_fields[4])
          pr = float(parent_fields[5])
          cx = float(child_fields[2])
          cy = float(child_fields[3])
          cz = float(child_fields[4])
          cr = float(child_fields[5])
          segments = segments + [ [ [px, py, pz, pr], [cx, cy, cz, cr] ] ]
          num_total_segments += 1

    else:

      # Read the legacy format found from early work with Neuron

      f = open ( self.neuron_file_name, 'r' )
      lines = f.readlines();
      self.num_lines_in_file = len(lines)
      num_entries_to_read = 0
      segment = []
      for l in lines:
        print ( "Line: " + l.strip() )
        if len(l.strip()) > 0:
          # This is a real line
          if num_entries_to_read == 0:
            # Look for a line containing a 1 and the number of fields
            fields = l.strip().split()
            if len(fields) != 2:
              print ( "Error: expected 2 values" )
            else:
              if int(fields[0]) != 1:
                print ( "Unexpected first value for line" + l )
              num_entries_to_read = int(fields[1])
              print ( "Read " + str(num_entries_to_read) )
              if len(segment) > 0:
                segments = segments + [ segment ]
                segment = []
                num_total_segments += 1
          else:
            # This is another entry in the current segment
            values = l.strip().split()
            segment = segment + [ values ]
            num_entries_to_read += -1
            self.num_nodes_in_file += 1
      if len(segment) > 0:
        # Be sure to save the last segment
        segments = segments + [ segment ]
        num_total_segments += 1

    if self.num_segs_limit > 0:
      # Limit the number of segments
      segments = segments[0:self.num_segs_limit]
      num_total_segments = len(segments)

    self.num_segments_in_file = num_total_segments

    self.perform_analysis ( segments )

    return segments



  def perform_analysis ( self, segments ):

    # Dump to compare:
    #print ( "========== DUMP OF SEGMENTS ==========" )
    #for seg in segments:
    #  print ( "Segment:" )
    #  for node in seg:
    #    print ( "  Node: " + str(node) )
    #print ( "======================================" )

    # Find the smallest radius

    seg_num = 1
    obj_name = None
    first_pass = True
    self.largest_radius_in_file = -1
    self.smallest_radius_in_file = -1
    self.min_x = self.max_x = self.min_y = self.max_y = self.min_z = self.max_z = -1
    for seg in segments:
      print ( "=== Finding bounds and smallest radius for segment " + str(seg_num) + " ===" )
      seg_num += 1
      lc = None
      cap1 = True
      for c in seg:
        x = float(c[0])
        y = float(c[1])
        z = float(c[2])
        r = float(c[3])
        if first_pass or (r > self.largest_radius_in_file):
          self.largest_radius_in_file = r
        if first_pass or (r < self.smallest_radius_in_file):
          self.smallest_radius_in_file = r
        if first_pass or (x < self.min_x):
          self.min_x = x
        if first_pass or (x > self.max_x):
          self.max_x = x
        if first_pass or (y < self.min_y):
          self.min_y = y
        if first_pass or (y > self.max_y):
          self.max_y = y
        if first_pass or (z < self.min_z):
          self.min_z = z
        if first_pass or (z > self.max_z):
          self.max_z = z
        first_pass = False

    print ( "X range: %g to %g" % (self.min_x, self.max_x) )
    print ( "Y range: %g to %g" % (self.min_y, self.max_y) )
    print ( "Z range: %g to %g" % (self.min_z, self.max_z) )
    print ( "Largest radius = " + str(self.largest_radius_in_file) )
    print ( "Smallest radius = " + str(self.smallest_radius_in_file) )

    self.file_analyzed = True




  def get_swc_from_mesh_stick ( self, context ):
    # Convert the current stick mesh into an swc format file
    if context.scene.objects.active == None:
      return None

    lines = []
    lines.append ( "# n T x y z R P" )

    mesh = context.scene.objects.active.data
    verts = mesh.vertices
    
    p = 0
    for edge in mesh.edges:
      v1i = edge.vertices[0]
      v2i = edge.vertices[1]
      if p == 0:
        # This is the first segment, so output the first point with -1 as parent
        lines.append ( str(p) + " 0 " + str(verts[v1i].co.x) + " " + str(verts[v1i].co.y) + " " + str(verts[v1i].co.z) + " 0.1 -1" )
        p += 1
      # THIS LINE OF CODE APPEARS TO PRODUCE THE WRONG PARENT AT THE END OF THE OUTPUT LINE:
      lines.append ( str(p) + " 0 " + str(verts[v2i].co.x) + " " + str(verts[v2i].co.y) + " " + str(verts[v2i].co.z) + " 0.1 " + str(p) )
      p += 1
    
    print ( "Output file:" )
    for l in lines:
      print ( l )
    
    return ( lines )


  def build_neuron_stick_from_file ( self, context ):
    # Read once with standard code to update the display
    segments = self.read_segments_from_file()

    if (self.neuron_file_name[-4:] == ".swc") or (self.neuron_file_name[-8:] == ".swc.txt"):
      # Read again to get all the data needed for a stick figure
      
      # Start by reading all the points into a dictionary keyed by their label n

      f = open ( self.neuron_file_name, 'r' )
      file_lines = f.readlines();
      point_dict = {}
      point_keys = []
      point_num = 0
      for l in file_lines:
        l = l.strip()
        print ( "Line: " + l )
        if len(l) > 0:
          if l[0] != "#":
            fields = l.split() + [ str(point_num) ]
            point_dict[fields[0]] = fields
            point_keys.append ( fields[0] )
            point_num += 1
      self.num_lines_in_file = len(point_keys)
      self.num_nodes_in_file = len(point_keys)

      # Build the Blender mesh starting with the vertices

      print ( "Making the verts:" )

      verts = []
      for k in point_keys:
        p = point_dict[k]
        print ( str(p) )
        px = float(p[2])
        py = float(p[3])
        pz = float(p[4])
        pr = float(p[5])
        verts.append ( [ px, py, pz ] )

      print ( "Making the lines:" )

      lines = []
      for k in point_keys:
        p = point_dict[k]
        print ( str(p) )
        ppkey = p[6]
        if int(ppkey) >= 0:
          # This point has a parent, so make a line segment
          pp = point_dict[ppkey]
          lines.append ( [ int(pp[7]), int(p[7]) ] )

      print ( "Making the mesh:" )

      new_mesh = bpy.data.meshes.new ( "my_mesh" )
      new_mesh.from_pydata ( verts, lines, [] )
      new_mesh.update()
      new_obj = bpy.data.objects.new ( "my_obj", new_mesh )
      context.scene.objects.link ( new_obj )


      print ( "Adding the metadata to each vertex:" )

      #  n T x y z R P

      mesh = new_obj.data
      index_number_layer = mesh.vertex_layers_float.new(name="index_number")
      parent_index_layer = mesh.vertex_layers_float.new(name="parent_index")
      segment_type_layer = mesh.vertex_layers_float.new(name="segment_type")
      # packed_layer = mesh.vertex_layers_int.new(name="packed_data")
      radius_layer       = mesh.vertex_layers_float.new(name="radius")

      vert_index = 0
      for k in point_keys:
        p = point_dict[k]
        print ( "Adding metadata from " + str(p) )
        index_number_layer.data[vert_index].value = int(p[0])
        parent_index_layer.data[vert_index].value = int(p[6])
        segment_type_layer.data[vert_index].value = int(p[1])
        #binary_value = (int(p[0]) << 17) | (int(p[6]) << 3) | (int(p[1]))
        #packed_layer.data[vert_index].value = binary_value
        radius_layer.data[vert_index].value = float(p[5])
        vert_index += 1

      #bpy.ops.object.mode_set()

  
  def build_neuron_meta_from_segments ( self, context, segments ):

    # segments = self.read_segments_from_file()

    # Create the object to hold the metaballs

    scene = bpy.context.scene
    mball = bpy.data.metaballs.new('neuron')
    obj = bpy.data.objects.new('Neuron',mball)
    scene.objects.link(obj)
    mball.resolution = self.mesh_resolution
    mball.render_resolution = self.mesh_resolution

    # Generate the metashape segments from the branch segments

    seg_num = 1
    obj_name = None
    for seg in segments:
      print ( "=== Building Branch " + str(seg_num) + " ===" )
      seg_num += 1
      lc = None
      for c in seg:
        if (lc != None):  # and (seg_num < 20):

          print ( "Building segment with radius of " + str(lc[3]) + " and " + str(c[3]) )

          x1 = float(lc[0]) * self.scale_file_data
          y1 = float(lc[1]) * self.scale_file_data
          z1 = float(lc[2]) * self.scale_file_data
          r1 = float(lc[3]) * self.scale_file_data
          x2 = float(c[0]) * self.scale_file_data
          y2 = float(c[1]) * self.scale_file_data
          z2 = float(c[2]) * self.scale_file_data
          r2 = float(c[3]) * self.scale_file_data

          # Make the segment from a series of meta balls

          segment_vector = mathutils.Vector ( ( (x2-x1), (y2-y1), (z2-z1) ) )
          segment_length = segment_vector.length

          # Be sure that the radiuses are non-zero
          if segment_length < 0:
            segment_length = 0.01
          if r1 < segment_length / 1000:
            r1 = segment_length / 1000
          if r2 < segment_length / 1000:
            r2 = segment_length / 1000

          if r1 < self.min_forced_radius:
            r1 = self.min_forced_radius
          if r2 < self.min_forced_radius:
            r2 = self.min_forced_radius

          dr = r2 - r1
          dx = x2 - x1
          dy = y2 - y1
          dz = z2 - z1

          r = r1
          x = x1
          y = y1
          z = z1

          length_so_far = 0
          while length_so_far < segment_length:
            # Make a sphere at this point
            ele = mball.elements.new()
            ele.radius = r
            ele.co = (x, y, z)
            
            # Move x, y, z, and r to the next point
            length_so_far += r/2
            r = r1 + (length_so_far * dr / segment_length)
            x = x1 + (length_so_far * dx / segment_length)
            y = y1 + (length_so_far * dy / segment_length)
            z = z1 + (length_so_far * dz / segment_length)

          # Make the last one just to be sure

          #ele = mball.elements.new()
          #ele.radius = r2
          #ele.co = (x2, y2, z2)

          # obj_name = self.add_segment ( obj_name, p1=mathutils.Vector((x1,y1,z1)), p2=mathutils.Vector((x2,y2,z2)), r1=r1, r2=r2, faces=10, cap1=cap1, cap2=True )
        lc = c

    if self.convert_to_mesh:
      bpy.ops.object.convert()

    obj.select = True


def add_to_menu ( self, context ):
  self.layout.operator ( "mesh.make_meta_neuron", icon = "PLUGIN" )


def register():
  print ( "NeuronMetaBuilder.py: register() called ... note that there is a bl_rna is in bpy.context" )
  bpy.utils.register_module(__name__)
  bpy.types.Scene.make_neuron_meta = bpy.props.PointerProperty(type=MakeNeuronMetaPropGroup)
  #bpy.utils.register_class ( MakeNeuronMeta )
  #bpy.types.INFO_MT_mesh_add.append(add_to_menu)


def unregister():
  print ( "NeuronBuilder.py: unregister() called ... note that there is a bl_rna is in bpy.context" )
  bpy.utils.unregister_module(__name__)
  #bpy.utils.unregister_class ( MakeNeuronMeta )
  #bpy.types.INFO_MT_mesh_add.remove(add_to_menu)


if __name__ == "__main__":
  print ("Registering")
  register()

