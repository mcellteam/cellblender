############################################################################################################
#
#  Example mol-viz program modified from default_mol_viz.py.
#
#  This version doesn't supply random rotations and filters out proxy molecules from the display.
#  Compare to default_mol_viz.py for other subtle differences.
#
############################################################################################################

# Import the required modules.
# These are the same modules imported by cellblender_mol_viz.py.
import bpy
import mathutils
import array
import random

import os
import json

# Initialize some CellBlender references
mcell = bpy.context.scene.mcell
mv = mcell.mol_viz

# Get the current mol_viz file name. This is "normal" file from MCell.
# This is normally passed to "cellblender_mol_viz.mol_viz_file_read".
filepath = mv.frame_file_name

#print ( "\nFilepath = " + filepath )

# Convert the normal file name to the BNGL file name
path_split = filepath.rfind ( os.sep )
path_part = filepath[0:path_split]
file_part = filepath[1+path_split:]
new_file_part = '.bnglviz.'.join(file_part.split(".cellbin."))
new_path = os.sep.join ( [path_part, "viz_bngl", new_file_part] )

#print ( "new_path = " + new_path )

# Open the file and read as a string
mol_file = open ( new_path, 'r' )
json_string = mol_file.read()

# Use the JSON library to load the molecules
mols = json.loads ( json_string )

print ( "\n\nFile contains an array of " + str(len(mols)) + " blocks" )

version = mols[0]
templates = mols[1]
instances = mols[2]
positions = [ i[1] for i in instances ]

templates_bngl = []

for t in templates:
    # print ( "Template = " + str(t) )
    bngl_str = ""
    next_bond_num = 1
    bond_num_dict = {}
    for m in t:
        if m[0] == "m":
            # This "m" is a molecule
            if len(bngl_str) != 0:
                bngl_str += '.'  # Add the "." as needed between molecules
            bngl_str += m[1]  # Add the molecule name
            if True and len(m[3]) > 0: # This molecule has components
                cstr = ''
                for c in m[3]: # Loop through the components
                    # print ( "c = " + str(c) )
                    # print ( "  len t[c][3] = " + str(len(t[c][3])) )
                    if len(t[c][3]) > 1:  # This means it's bound
                        if len(cstr) != 0:
                            cstr += ','
                        cstr += t[c][1]
                        if c in bond_num_dict:
                            # This means the other binding partner has added it
                            cstr += "!" + str(bond_num_dict[c])
                        else:
                            # This means the bond isn't in the dictionary yet so add it
                            bond_num_dict[t[c][3][1]] = next_bond_num
                            cstr += "!" + str(next_bond_num)
                            next_bond_num += 1
                if True and len(cstr) > 0:
                    bngl_str += '('
                    bngl_str += cstr
                    bngl_str += ')'
                
    print ( "BNGL = " + bngl_str )
    templates_bngl.append ( bngl_str )

mols_by_species = []
global s  # For some reason this needs to be global??? or: Unexpected Exception calling mol_viz_update: (<class 'NameError'>, NameError("name 's' is not defined",), <traceback object at 0x7f871798fa08>)
for s in range(len(templates)):
    next_species = [ i[1] for i in instances if i[0] == s ]
    mols_by_species.append ( next_species )

print ( "Version = " + str(version) + 
        ", Num templates = " + str(len(templates))  +
        ", Num instances = " + str(len(instances))  + 
        ", Num species = " + str(len(mols_by_species)) )

for i in range ( len(mols_by_species) ):
    print ( "   Species " + str(i) + " has " + str(len(mols_by_species[i])) + " instances" )


mol_labels_obj = bpy.data.objects.get("molecule_labels")
if not mol_labels_obj:
    bpy.ops.object.add(type='MESH',location=[0, 0, 0])      # Create an "Empty" object in the Blender scene
    ### Note, the following line seems to cause an exception in some contexts: 'Context' object has no attribute 'selected_objects'
    mol_labels_obj = bpy.context.selected_objects[0]  # The newly added object will be selected
    mol_labels_obj.name = "molecule_labels"                 # Name this empty object "molecules" 
    mol_labels_obj.hide_select = True
    mol_labels_obj.hide = True

mol_labels_obj['mol_labels_bngl'] = templates_bngl
mol_labels_obj['mol_labels_index'] = [ i[0] for i in instances ]
mol_labels_obj['mol_labels_x'] = [ i[1][0] for i in instances ]
mol_labels_obj['mol_labels_y'] = [ i[1][1] for i in instances ]
mol_labels_obj['mol_labels_z'] = [ i[1][2] for i in instances ]

'''

#for p in positions:
#    print ( "   " + str(p) )

"""
for p in positions:
    mol_pos.append(p[0])
    mol_pos.append(p[1])
    mol_pos.append(p[2])

mol_orient = [random.uniform(-1.0, 1.0) for i in range(len(mol_pos))]
"""


############## Previous processing ############


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
        # z_axis = mathutils.Vector((0.0, 0.0, 1.0))

        for mol_name in mol_dict.keys():
            ############################
            print ( "mol_name = " + str(mol_name) )
            ############################
            if mol_name in ["mol_volume_proxy", "mol_surface_proxy"]:
                # Use "continue" to not update the proxies
                # User "pass" to update the proxies
                continue

            mol_mat_name = "%s_mat" % (mol_name)
            mol_type = mol_dict[mol_name][0]
            mol_pos = mol_dict[mol_name][1]
            mol_orient = mol_dict[mol_name][2]

            ############################
            #print ( "mol_pos[" + str(len(mol_pos)) + "] = " + str(mol_pos) )
            ############################

            # Randomly orient volume molecules
            if True and (mol_type == 0):
                mol_orient.extend([random.uniform(-1.0, 1.0) for i in range(len(mol_pos))])

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

'''