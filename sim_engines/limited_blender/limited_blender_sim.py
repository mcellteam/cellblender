import sys
import os
import pickle
import math
import random
import array
import shutil

import bpy
import mathutils as mu


def print_and_flush ( some_string ):
  # sys.stdout.write ( some_string + "\n" )
  print ( some_string )
  sys.stdout.flush()


def run_jobs ( jobs_list ):
    example_running_in_blender()
    for job in jobs_list:
      print ( "Job: " + str(job) )
      for k in job.keys():
        print ( "  Key = " + str(k) )
      run_job ( {'mcell':job['data_model']}, job['proj_path'], job['seed'], job['decay_factor'], job['output_detail'] )
    pass


def example_running_in_blender():
    print ( "Hello" )

    import mathutils as mu

    # bpy.ops.view3d.snap_cursor_to_center()

    c = bpy.context

    o = c.active_object

    if not (o is None):
        
        print ( "Active object is " + o.name )
        if o.type == 'MESH':
            print ( "Active object is a mesh" )
            
            mol_pos = mu.Vector ( (0,0,0) )

            m = o.data

            verts = m.vertices
            faces = m.polygons

            for v in verts:
                print ( "  Vert: " + str(v.co) )

            for f in faces:
                print ( "  Face: " + str([ v for v in f.vertices]) )
                if len(f.vertices) != 3:
                    print ( "Ignoring face with " + str(len(f.vertices)) + " faces." )

            import mathutils as mu
            g = mu.geometry

            p1 = mu.Vector((0,0,1))
            p2 = mu.Vector((0,1,0))
            p3 = mu.Vector((1,0,0))
            ray = mu.Vector((1,1,1))
            orig = mu.Vector((0,0,0))
            hit = g.intersect_ray_tri ( p1, p2, p3, ray, orig, True )
            print ( str(hit) )

            import random

            areas = c.screen.areas
            areas_3d = [ areas[i] for i in range(len(areas)) if areas[i].type == 'VIEW_3D' ]

            for i in range(1000):
                ss = 0.1
                # Note that this isn't uniformly distributed in all directions!!!
                mol_delta = mu.Vector ( (random.uniform(-ss,ss), random.uniform(-ss,ss), random.uniform(-ss,ss)) )
                #mol_delta = mu.Vector ( (ss, ss, ss) )
                shortest_hit = None
                for f in faces:
                    fv = f.vertices
                    hit = g.intersect_ray_tri ( verts[fv[0]].co, verts[fv[1]].co, verts[fv[2]].co, mol_delta, mol_pos, True )
                    if not (hit is None):
                        # The molecule collided with the object, check to see if this is the closest hit
                        if (shortest_hit is None) or ( (mol_pos-hit).length < (mol_pos-shortest_hit).length ):
                            shortest_hit = hit
                print ( "Shortest hit = " + str(shortest_hit) )
                if (shortest_hit is None) or ((shortest_hit-mol_pos).length > mol_delta.length):
                    # No collision with the sides, just move the molecule
                    mol_pos = mol_pos + mol_delta
                else:
                    # There was a collision, so mark it but don't move the molecule
                    for area in areas_3d:
                        for space in area.spaces:
                            if 'cursor_location' in dir(space):
                                #print ( "Moving Cursor to " + str(hit_list) )
                                # space['cursor_location'] = hit_list
                                space.cursor_location = tuple ( [ h for h in shortest_hit ] )
                                bpy.ops.mesh.primitive_ico_sphere_add()
                                c.active_object.scale = mu.Vector((0.01,0.01,0.01))
                                space.cursor_location = ( 0, 0, 0 )


par_val_dict = {}
def convert_to_value ( expression ):
  global par_val_dict
  return eval(expression,globals(),par_val_dict)


def run_job ( data_model, proj_path, run_seed, decay_rate_factor, output_detail ):

    ##### Start by reading the command line parameters which includes the data model file name

    """
    for arg in sys.argv:
      if output_detail > 10: print_and_flush ( "   " + str(arg) )
      if arg[0:10] == "proj_path=":
        proj_path = arg[10:]
      elif arg[0:5] == "seed=":
        run_seed = int(arg[5:])
      elif arg[0:13] == "decay_factor=":
        decay_rate_factor = float(arg[13:])
      elif arg[0:14] == "output_detail=":
        output_detail = int(arg[14:])
      else:
        if output_detail > 0: print_and_flush ( "Unknown argument = " + str(arg) )
    """


    if output_detail > 10: print_and_flush ( "\n\n" )

    if output_detail > 0:
      print_and_flush ( "**********************************************" )
      print_and_flush ( "*  Limited Pure Python Prototype Simulation  *" )
      print_and_flush ( "*          Updated: July 19th, 2017          *" )
      print_and_flush ( "**********************************************" )
      print_and_flush ( "" )
      print_and_flush ( "Running with Python:" )
      print_and_flush ( sys.version )
      print_and_flush ( "" )

    if output_detail > 10: print_and_flush ( "Arguments: " + str(sys.argv) )

    random.seed ( run_seed )
    seed_dir = "seed_%05d" % run_seed


    dm = data_model

    if dm is None:
      print_and_flush ( "ERROR: Unable to use data model" )
      sys.exit(1)

    #print_and_flush ( str(dm) )

    ##### Clear out the old data

    # Note that there have been some errors calling rmtree, which are currently being ignored:
    #  OSError: [Errno 16] Device or resource busy: '.nfs0000000000a48d3e00005e12'
    #  OSError: [Errno 39] Directory not empty: 'seed_00001'

    react_dir = os.path.join(proj_path, "output_data", "react_data")
    if not os.path.exists(react_dir):
        os.makedirs(react_dir)

    viz_dir = os.path.join(proj_path, "output_data", "viz_data")
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)

    viz_seed_dir = os.path.join(viz_dir, seed_dir)
    if not os.path.exists(viz_seed_dir):
        os.makedirs(viz_seed_dir)

    react_seed_dir = os.path.join(react_dir, seed_dir)
    if not os.path.exists(react_seed_dir):
        os.makedirs(react_seed_dir)

    ##### Use the Data Model to generate output files

    ## Start by building a parameter value dictionary

    global par_val_dict
    par_val_dict = {}
    for p in dm['mcell']['parameter_system']['model_parameters']:
      par_val_dict[p['par_name']] = p['_extras']['par_value']

    if output_detail > 0:
      print_and_flush ( "Parameter Dictionary: " + str(par_val_dict) )
      for k in par_val_dict.keys():
        print_and_flush ( "   " + str(k) + ": " + str(par_val_dict[k]) )

    iterations = int(convert_to_value(dm['mcell']['initialization']['iterations']))
    time_step = convert_to_value(dm['mcell']['initialization']['time_step'])
    mols = dm['mcell']['define_molecules']['molecule_list']
    rels = dm['mcell']['release_sites']['release_site_list']

    rxns = []
    if 'define_reactions' in dm['mcell']:
      if 'reaction_list' in dm['mcell']['define_reactions']:
        if len(dm['mcell']['define_reactions']['reaction_list']) > 0:
          rxns = dm['mcell']['define_reactions']['reaction_list']

    for m in mols:
      if output_detail > 0: print_and_flush ( "Molecule " + m['mol_name'] + " is a " + m['mol_type'] + " molecule diffusing with " + str(m['diffusion_constant']) )

    for r in rels:
      if output_detail > 0: print_and_flush ( "Release " + str(r['quantity']) + " of " + r['molecule'] + " at (" + str(r['location_x']) + "," + str(r['location_y']) + "," + str(r['location_z']) + ")"  )

    for r in rxns:
      arrow = '->'
      bkwd = ''
      if len(r['bkwd_rate']) > 0:
        arrow = '<->'
        bkwd = ", " + str(r['bkwd_rate'])
      if output_detail > 0: print_and_flush ( "Reaction: " + r['reactants'] + " " + arrow + " " + r['products'] + "  [" + str(r['fwd_rate']) + bkwd + "]"  )

    # Create instances for each molecule that is released (note that release patterns are not handled)

    for m in mols:
      m['instances'] = []

    for r in rels:
      rel_x = convert_to_value(r['location_x'])
      rel_y = convert_to_value(r['location_y'])
      rel_z = convert_to_value(r['location_z'])
      q = int(convert_to_value(r['quantity']))
      for m in mols:
        if m['mol_name'] == r['molecule']:
          for i in range(q):
            x = rel_x  # +random.gauss(0.0,0.1)
            y = rel_y  # +random.gauss(0.0,0.1)
            z = rel_z  # +random.gauss(0.0,0.1)
            m['instances'].append ( [x,y,z] )

    # Figure out the number of digits needed for file names

    ndigits = 1 + math.log(iterations+1,10)
    file_name_template = "Scene.cellbin.%%0%dd.dat" % ndigits

    # Create the count files for each molecule species (doesn't currently use the count specifications)

    count_files = {}

    for m in mols:
      react_file_name = "%s/%s/%s.World.dat" % ( react_dir, seed_dir, m['mol_name'] )
      count_files[m['mol_name']] = open(react_file_name,"w")


    # Begin the simulation

    print_every = math.pow(10,math.floor(math.log10((iterations/10))));
    if print_every < 1: print_every = 1;
    for i in range(iterations+1):
      # Write the viz data (every iteration for now)
      viz_file_name = file_name_template % i
      viz_file_name = os.path.join(viz_seed_dir,viz_file_name)
      if (i % print_every) == 0:
        #if output_detail > 0: print_and_flush ( "File = " + viz_file_name )
        if output_detail > 0: print_and_flush ( "Iteration %d of %d" % (i, iterations) )
      f = open(viz_file_name,"wb")
      int_array = array.array("I")   # Marker indicating a binary file
      int_array.fromlist([1])
      int_array.tofile(f)
      for m in mols:
        name = m['mol_name']
        f.write(bytearray([len(name)]))       # Number of bytes in the name
        for ni in range(len(name)):
          f.write(bytearray([ord(name[ni])]))  # Each byte of the name
        f.write(bytearray([0]))                # Molecule Type, 1=Surface, 0=Volume?

        # Write out the total number of values for this molecule species
        int_array = array.array("I")
        int_array.fromlist([3*len(m['instances'])])
        int_array.tofile(f)
        
        dc = convert_to_value(m['diffusion_constant'])
        ds = math.sqrt(4.0 * 1.0e8 * dc * time_step)
        for mi in m['instances']:
          x = mi[0]
          y = mi[1]
          z = mi[2]
          mol_pos = array.array("f")
          mol_pos.fromlist ( [ x, y, z ] )
          mol_pos.tofile(f)
          mi[0] += random.gauss(0.0,ds) * 0.70710678118654752440
          mi[1] += random.gauss(0.0,ds) * 0.70710678118654752440
          mi[2] += random.gauss(0.0,ds) * 0.70710678118654752440
      f.close()
      # Write the count data (every iteration for now)
      for m in mols:
        name = m['mol_name']
        count = len(m['instances'])
        count_files[name].write ( "%.15g" % (i*time_step) + " " + str(count) + "\n" )

      # Perform approximate decay reactions for now  (TODO: Make this realistic)
      for m in mols:
        if len(m['instances']) > 0:
          # There are some molecules left to react
          for r in rxns:
            if r['reactants'] == m['mol_name']:
              # The reaction applies to this molecule
              rate = convert_to_value(r['fwd_rate'])
              fraction_to_remove = decay_rate_factor * rate * time_step
              amount_to_remove = fraction_to_remove * len(m['instances'])
              num_to_remove = int(amount_to_remove)
              if random.random() < (amount_to_remove - num_to_remove):
                num_to_remove += 1
              if output_detail > 50: print_and_flush ( "React " + m['mol_name'] + " with rate = " + str(rate) + ", remove " + str(num_to_remove) + " (should be about " + str(100*fraction_to_remove) + "%)" )
              for i in range(num_to_remove):
                if len(m['instances']) > 0:
                  m['instances'].pop()


    for fname in count_files.keys():
      count_files[fname].close()

    if output_detail > 0: print_and_flush ( "Done simulation.\n" );

