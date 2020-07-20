#############################################################################################
#
# Terminal input: blender -P ~/.../cellblender/developer_utilities/mol_viz_scripts/dat_to_blender.py -- ~/.../viz_data/seed_00001 <-- where the .dat or .ascii files are located.
# 
# This file reads binary data files that are generated by MCell and updates their display in blender. 
# Color and object geomerty are not handled here (because this data is not given in the seed_00001 files).
#
#############################################################################################

import json
import bpy
import os
import re
import sys

#FIXME: need to find cellblender plugin directory, maybe pass as argument
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CELLBLENDER_DIR = os.path.join(THIS_DIR, '..', '..')
if not os.path.exists(CELLBLENDER_DIR):
    print("Directory where the cellblender plugin should reside was not found: " + CELLBLENDER_DIR)
    sys.exit(1)
sys.path.insert(1, CELLBLENDER_DIR)
import cellblender_mol_viz as cb_mv
import data_model

# TODO: better argument checkinbg 
INPUT_DIRECTORY = sys.argv[4]
   
# reports error when the cellblender frame goes past the mcell data provided
def out_of_bounds(n):
    print('ERROR: frame number '+ str(n) + ' is out of bounds. This frame was not simulated in MCell.')
    

def mol_viz_update_from_file(mcell, filename):
    """ Clear the old viz data. Draw the new viz data. """

    mcell.mol_viz.mol_file_name = filename
    filepath = os.path.join(mcell.mol_viz.mol_file_dir, filename)

    # Save current global_undo setting. Turn undo off to save memory
    global_undo = bpy.context.user_preferences.edit.use_global_undo
    bpy.context.user_preferences.edit.use_global_undo = False

    cb_mv.mol_viz_clear(mcell)
    cb_mv.mol_viz_file_read(mcell, filepath)

    # Reset undo back to its original state
    bpy.context.user_preferences.edit.use_global_undo = global_undo    


def update_frame_data(scene):
    # this is our iteration
    current_iteration = bpy.context.scene.frame_current - 1
   
    best_datamodel_iteration = -1
    best_datamodel_file = ''
    best_mol_pos_file = ''
    
    filepath = os.scandir(INPUT_DIRECTORY)
    for file in filepath:
        # --- geometry ---
        if re.match(r'(.*\.datamodel\.[0-9]+\.json)'.format(), str(file)):
            name = str(file.path)
            file_iteration = int(name.split('.')[-2])
            
            # find the highest value that is still lower or equal than current_iteration
            if file_iteration <= current_iteration and file_iteration > best_datamodel_iteration:
                best_datamodel_iteration = file_iteration
                best_datamodel_file = file.path
        
        # --- molecule positions --- 
        if not best_mol_pos_file and re.match(r'(.*\.0*{}\.dat)'.format(current_iteration), str(file)):
            best_mol_pos_file = file.path


    # geometry does not have to be present
    if best_datamodel_file:
        print("** Matching datamodel file " + best_datamodel_file)
        #load_datamodel(best_datamodel_file)
        data_model.import_datamodel_all_json(best_datamodel_file, bpy.context)
        pass
    
    # molecule positions must be found        
    if best_mol_pos_file:
        # file.path gets the entire folder path as well as the file name as a string.
        mol_viz_update_from_file(bpy.context.scene.mcell, best_mol_pos_file)
    else:
        # print out of bounds error
        out_of_bounds(current_iteration)
    

def load_first_frame_and_set_nr_of_frames():
    
    # get nr of frames
    max_frame_nr = -1
    filepath = os.scandir(INPUT_DIRECTORY)
    for file in filepath:
        # --- geometry ---
        if re.match(r'(.*\.[0-9]+\.dat)', str(file)):
            name = str(file.path)
            file_iteration = int(name.split('.')[-2])
            
            # find the highest value 
            if file_iteration >= max_frame_nr:
                max_frame_nr = file_iteration
            
                
    bpy.context.scene.frame_end = max_frame_nr + 1 # frames are counted from 1, iterations from 0
    update_frame_data(bpy.context.scene)
    

print("*** Loading visualization data from directory " + INPUT_DIRECTORY)
if not os.path.exists(INPUT_DIRECTORY):
    print("Error: directory " + INPUT_DIRECTORY + " does not exist, terminating.")
    sys.exit(1)

# remove all default objects from blender startup
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# set number of frames and load first file
load_first_frame_and_set_nr_of_frames()

# register a handler for events when frame changes
# update the visual output by sending the .dat files created by mcell into cellblender for each frame
bpy.app.handlers.frame_change_pre.append(update_frame_data)