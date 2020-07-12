############################################################################################################
#
#  Example mol-viz program taken directly from CellBlender's internal code:
#
#      cellblender_mol_viz.py
#
#  This program duplicates the functionality of CellBlender's internal visualization code.
#  This program can be used as a starting point for developing custom molecule displays.
#
#  A handy debugging feature is the ability to drop into a debug console using this code:
#
#      if mcell.cellblender_preferences.debug_level > 100:
#        __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
#
#  This program can also be used to test the performance of loading and compiling the JSON code.
#
#  A quick way to get started is to simply insert a print statement at the top of this code.
#  Then use CellBlender's "Custom Visualization" option specifying this file.
#  When it runs, it should print whatever you've specified.
#
############################################################################################################

# Import the required modules.
# These are the same modules imported by cellblender_mol_viz.py.
import bpy
import mathutils
import array
import random

# Initialize some CellBlender references (not in the original mol_viz.py)
mcell = bpy.context.scene.mcell
mv = mcell.mol_viz

# Get the current mol_viz file name. This is "normal" file from MCell.
# This is normally passed to "cellblender_mol_viz.mol_viz_file_read".
filepath = mv.frame_file_name

# The code below is directly from cellblender_mol_viz.py at line 843:

dup_check = False
try:

    # Quick check for Binary or ASCII format of molecule file:
    mol_file = open(filepath, "rb")
    b = array.array("I")
    b.fromfile(mol_file, 1)

    mol_dict = {}

    if b[0] == 1:
        # Read MCell/CellBlender Binary Format molecule file, version 1:
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
                mol_file.close()
                break

            except:
                print( "Unexpected Exception: " + str(sys.exc_info()) )
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

        for mol_name in mol_dict.keys():
            mol_mat_name = "%s_mat" % (mol_name)
            mol_type = mol_dict[mol_name][0]
            mol_pos = mol_dict[mol_name][1]
            mol_orient = mol_dict[mol_name][2]

            # Randomly orient volume molecules
            if mol_type == 0:
                mol_orient.extend([random.uniform(
                    -1.0, 1.0) for i in range(len(mol_pos))])

            # Look up the glyph, color, size, and other attributes from the molecules list
            # If the molecule found in the viz file doesn't exist in the molecules list, create it as the interface for changing color, etc.
            mname = mol_name[4:]   # Trim off the "mol_" portion to use as an index into the molecules list
            mol = None
            if (len(mname) > 0) and (mname in mcell.molecules.molecule_list):
                mol = mcell.molecules.molecule_list[mname]

            # Look-up mesh shape (glyph) template and create if needed
            # This may end up calling a member function of the molecule class to create a new default molecule (including glyph)
            mol_shape_mesh_name = "%s_shape" % (mol_name)
            mol_shape_obj_name = mol_shape_mesh_name
            mol_shape_mesh = meshes.get(mol_shape_mesh_name)  # This will return None if not found by that name
            if not mol_shape_mesh:
                # Make the glyph right here
                bpy.ops.mesh.primitive_ico_sphere_add(
                    subdivisions=0, size=0.005, location=[0, 0, 0])
                mol_shape_obj = bpy.context.active_object
                mol_shape_obj.name = mol_shape_obj_name
                mol_shape_obj.track_axis = "POS_Z"
                mol_shape_obj.hide_select = True
                mol_shape_mesh = mol_shape_obj.data
                mol_shape_mesh.name = mol_shape_mesh_name
            else:
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

