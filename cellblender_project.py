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
This file contains the classes for CellBlender's Preferences.

"""

import cellblender

# blender imports
import bpy
from bpy.app.handlers import persistent
from bl_operators.presets import AddPresetBase
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, BoolVectorProperty, PointerProperty, StringProperty

#from bpy.app.handlers import persistent
#import math
import mathutils

# python imports
import re
import os
import math


# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_utils
from . import cellblender_objects

from cellblender.cellblender_utils import mcell_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl



class MCellProjectPropertyGroup(bpy.types.PropertyGroup):
    base_name: StringProperty(
        name="Project Base Name", default="cellblender_project")

    status: StringProperty(name="Status")

    def draw_layout (self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            row = layout.row()
            split = row.split(factor=0.96)
            col = split.column()
            col.label(text="CellBlender ID: "+cellblender.cellblender_info['cellblender_source_sha1'])
            col = split.column()
            col.prop ( mcell, "refresh_source_id", icon='FILE_REFRESH', text="" )
            if 'cellblender_source_id_from_file' in cellblender.cellblender_info:
                # This means that the source ID didn't match the refreshed version
                # Draw a second line showing the original file ID as an error
                row = layout.row()
                row.label(text="File ID: " + cellblender.cellblender_info['cellblender_source_id_from_file'], icon='ERROR')

            # if not mcell.versions_match:
            if not cellblender.cellblender_info['versions_match']:
                # Version in Blend file does not match Addon, so give user a button to upgrade if desired
                row = layout.row()
                row.label ( text="Blend File version doesn't match CellBlender version", icon='ERROR' )

                row = layout.row()
                row.operator ( "mcell.upgrade", text="Upgrade Blend File to Current Version", icon='GHOST_ENABLED' )
                #row = layout.row()
                #row.operator ( "mcell.delete", text="Delete CellBlender Collection Properties", icon='GHOST_ENABLED' )

                row = layout.row()
                row.label ( text="Note: Saving this file will FORCE an upgrade!!!", icon='ERROR' )

            row = layout.row()
            if not bpy.data.filepath:
                row.label(
                    text="No Project Directory: Use File/Save or File/SaveAs",
                    icon='UNPINNED')
            else:
                row.label(
                    text="Project Directory: " + os.path.dirname(bpy.data.filepath),
                    icon='CHECKMARK')

            row = layout.row()
            layout.prop(context.scene, "name", text="Project Base Name")

    def remove_properties ( self, context ):
        print ( "Removing all Preferences Properties... no collections to remove." )

    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




class MCellExportProjectPropertyGroup(bpy.types.PropertyGroup):
    export_format_enum = [
        ('mcell_mdl_unified', "Single Unified MCell MDL File", ""),
        ('mcell_mdl_modular', "Modular MCell MDL Files", "")]
    export_format: EnumProperty(items=export_format_enum,
                                 name="Export Format",
                                 default='mcell_mdl_modular')

    def remove_properties ( self, context ):
        print ( "Removing all Export Project Properties... no collections to remove." )


class MCELL_OT_export_project(bpy.types.Operator):
    bl_idname = "mcell.export_project"
    bl_label = "Export CellBlender Project"
    bl_description = "Export CellBlender Project"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self,context):

        mcell = context.scene.mcell
        if mcell.cellblender_preferences.lockout_export:
            # print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            # The "self" here doesn't contain or permit the report function.
            # self.report({'INFO'}, "Exporting is Locked Out")
            return False

        return True


    def write_obj_as_mdl ( self, obj_name, points, faces, regions_dict, region_props, origin=None, file_name=None, partitions=False, instantiate=False ):
      print ( "MCELL_OT_export_project.write_obj_as_mdl()" )
      if file_name != None:
        out_file = open ( file_name, "w" )
        if partitions:
            out_file.write ( "PARTITION_X = [[-2.0 TO 2.0 STEP 0.5]]\n" )
            out_file.write ( "PARTITION_Y = [[-2.0 TO 2.0 STEP 0.5]]\n" )
            out_file.write ( "PARTITION_Z = [[-2.0 TO 2.0 STEP 0.5]]\n" )
            out_file.write ( "\n" )
        out_file.write ( "%s POLYGON_LIST\n" % (obj_name) )
        out_file.write ( "{\n" )
        out_file.write ( "  VERTEX_LIST\n" )
        out_file.write ( "  {\n" )
        for p in points:
            out_file.write ( "    [ " + str(p[0]) + ", " + str(p[1]) + ", " + str(p[2]) + " ]\n" );
        out_file.write ( "  }\n" )
        out_file.write ( "  ELEMENT_CONNECTIONS\n" )
        out_file.write ( "  {\n" )
        for f in faces:
            s = "    [ " + str(f[0]) + ", " + str(f[1]) + ", " + str(f[2]) + " ]\n"
            out_file.write ( s );
        out_file.write ( "  }\n" )

        if regions_dict:
            # Begin SURFACE_REGIONS block
            out_file.write("  DEFINE_SURFACE_REGIONS\n")
            out_file.write("  {\n")

            region_names = [k for k in regions_dict.keys()]
            region_names.sort()
            for region_name in region_names:
                out_file.write("    %s\n" % (region_name))
                out_file.write("    {\n")
                out_file.write("      ELEMENT_LIST = " +
                               str(regions_dict[region_name])+'\n')
                out_file.write("    }\n")

            # close SURFACE_REGIONS block
            out_file.write("  }\n")


        if origin != None:
            out_file.write ( "  TRANSLATE = [ %.15g, %.15g, %.15g ]\n" % (origin[0], origin[1], origin[2] ) )
        out_file.write ( "}\n" )
        if instantiate:
            out_file.write ( "\n" )
            out_file.write ( "INSTANTIATE Scene OBJECT {\n" )
            out_file.write ( "  %s OBJECT %s {}\n" % (obj_name, obj_name) )
            out_file.write ( "}\n" )
        out_file.close()


    def execute(self, context):
        print("Start of MCELL_OT_export_project.execute()")

        if context.scene.mcell.cellblender_preferences.lockout_export:
            print ( "Exporting is currently locked out. See the Preferences/ExtraOptions panel." )
            self.report({'INFO'}, "Exporting is Locked Out")
        else:
            print(" Scene name =", context.scene.name)

            # Filter or replace problem characters (like space, ...)
            scene_name = context.scene.name.replace(" ", "_")

            # Change the actual scene name to the legal MCell Name
            context.scene.name = scene_name

            mcell = context.scene.mcell

            # Force the project directory to be where the .blend file lives
            cellblender_objects.model_objects_update(context)

            filepath = os.path.join ( mcell_files_path(), "output_data" )
            os.makedirs(filepath, exist_ok=True)

            # Set this for now to have it hopefully propagate until base_name can
            # be removed
            mcell.project_settings.base_name = scene_name

            #mainmdl = os.path.join(
            #   filepath, mcell.project_settings.base_name + ".main.mdl")
            mainmdl = os.path.join(filepath, scene_name + ".main.mdl")
            #   bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=mainmdl)
            export_mcell_mdl.save(context, mainmdl)

            # These two branches of the if statement seem identical ?

            #if mcell.export_project.export_format == 'mcell_mdl_unified':
            #    mainmdl = os.path.join(os.path.dirname(bpy.data.filepath),
            #                            (mcell.project_settings.base_name +
            #                            ".main.mdl"))
            #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=mainmdl)
            #elif mcell.export_project.export_format == 'mcell_mdl_modular':
            #    mainmdl = os.path.join(os.path.dirname(bpy.data.filepath),
            #                            (mcell.project_settings.base_name +
            #                            ".main.mdl"))
            #    bpy.ops.export_mdl_mesh.mdl('EXEC_DEFAULT', filepath=mainmdl)


            ###################################
            ### Begin Dynamic Geometry Export
            ###################################

            print ( "Checking for dynamic objects" )

            dynamic = len([ True for o in mcell.model_objects.object_list if o.dynamic ]) > 0

            if dynamic:

                print ( "Exporting dynamic objects from MCELL_OT_export_project.execute()" )

                # Save the current frame to restore later
                fc = context.scene.frame_current

                # Generate the dynamic geometry

                geom_list_name = 'dyn_geom_list.txt'
                geom_list_file = open(os.path.join(filepath,geom_list_name), "w", encoding="utf8", newline="\n")
                path_to_dg_files = os.path.join ( filepath, "dynamic_geometry" )
                if not os.path.exists(path_to_dg_files):
                    os.makedirs(path_to_dg_files)


                iterations = context.scene.mcell.initialization.iterations.get_value()
                time_step = context.scene.mcell.initialization.time_step.get_value()
                print ( "iterations = " + str(iterations) + ", time_step = " + str(time_step) )

                # Build the script list first as a dictionary by object names so they aren't read at every iteration
                # It might also be efficient if these could be precompiled at this time (rather than in the loop).
                script_dict = {}
                for obj in context.scene.mcell.model_objects.object_list:
                    if obj.dynamic:
                        if len(obj.script_name) > 0:
                            # script_text = bpy.data.texts[obj.script_name].as_string()
                            compiled_text = compile ( bpy.data.texts[obj.script_name].as_string(), '<string>', 'exec' )
                            script_dict[obj.script_name] = compiled_text

                # Save state of mol_viz_enable and disable mol viz during frame change for dynamic geometry
                mol_viz_state = context.scene.mcell.mol_viz.mol_viz_enable
                context.scene.mcell.mol_viz.mol_viz_enable = False

                for frame_number in range(iterations+1):
                    ####################################################################
                    #
                    #  This section essentially defines the interface to the user's
                    #  dynamic geometry code. Right now it's being done through 7 global
                    #  variables which will be in the user's environment when they run:
                    #
                    #     frame_number
                    #     time_step
                    #     points[]
                    #     faces[]
                    #     regions_dict[]
                    #     region_props[]
                    #     origin[]
                    #
                    #  The user code gets the frame number as input and fills in both the
                    #  points and faces arrays (lists). The format is fairly standard with
                    #  each point being a list of 3 double values [x, y, z], and with each
                    #  face being a list of 3 point indexes defining a triangle with outward
                    #  facing normals using the right hand rule. The index values are the
                    #  integer offsets into the points array starting with index 0.
                    #  This is a very primitive interface, and it may be subject to change.
                    #
                    ####################################################################


                    # Set the frame number for Blender
                    context.scene.frame_set(frame_number)

                    # Write out the individual MDL files for each dynamic object at this frame
                    for obj in context.scene.mcell.model_objects.object_list:
                        if obj.dynamic:
                            # print ( "  Iteration " + str(frame_number) + ", Saving geometry for object " + obj.name + " using script \"" + obj.script_name + "\"" )
                            points = []
                            faces = []
                            regions_dict = None
                            region_props = None
                            origin = [0,0,0]
                            if len(obj.script_name) > 0:
                                # Let the script create the geometry
                                print ( "Build object mesh from user script for frame " + str(frame_number) )
                                #script_text = script_dict[obj.script_name]
                                #print ( 80*"=" )
                                #print ( script_text )
                                #print ( 80*"=" )
                                # exec ( script_dict[obj.script_name], locals() )
                                exec ( script_dict[obj.script_name] )
                            else:
                                # Get the geometry from the object (presumably animated by Blender)

                                print ( " cellblender_project.py: Build MDL mesh from Blender object for frame " + str(frame_number) )

                                geom_obj = context.scene.collection.children[0].objects[obj.name]
                                mesh = geom_obj.to_mesh(preserve_all_data_layers=True, depsgraph=context.evaluated_depsgraph_get())
                                mesh.transform(mathutils.Matrix() @ geom_obj.matrix_world)
                                points = [v.co for v in mesh.vertices]
                                faces = [f.vertices for f in mesh.polygons]
                                regions_dict = geom_obj.mcell.get_regions_dictionary(geom_obj)
                                del mesh

                            file_name = "%s_frame_%d.mdl"%(obj.name,frame_number)
                            full_file_name = os.path.join(path_to_dg_files,file_name)
                            self.write_obj_as_mdl ( obj.name, points, faces, regions_dict, region_props, origin=origin, file_name=full_file_name, partitions=False, instantiate=False )
                            #geom_list_file.write('%.9g %s\n' % (frame_number*time_step, os.path.join(".","dynamic_geometry",file_name)))

                    # Write out the "master" MDL file for this frame

                    frame_file_name = os.path.join(".","dynamic_geometry","frame_%d.mdl"%(frame_number))
                    full_frame_file_name = os.path.join(path_to_dg_files,"frame_%d.mdl"%(frame_number))
                    frame_file = open(full_frame_file_name, "w", encoding="utf8", newline="\n")

                    # Write the INCLUDE statements
                    for obj in context.scene.mcell.model_objects.object_list:
                        if obj.dynamic:
                            file_name = "%s_frame_%d.mdl"%(obj.name,frame_number)
                            frame_file.write ( "INCLUDE_FILE = \"%s\"\n" % (file_name) )

                    # Write the INSTANTIATE statement
                    frame_file.write ( "INSTANTIATE Scene OBJECT {\n" )
                    for obj in context.scene.mcell.model_objects.object_list:
                        if obj.dynamic:
                            frame_file.write ( "  %s OBJECT %s {}\n" % (obj.name, obj.name) )
                    frame_file.write ( "}\n" )
                    frame_file.close()

                    geom_list_file.write('%.9g %s\n' % (frame_number*time_step, frame_file_name))

                geom_list_file.close()

                # Restore setting for mol viz
                context.scene.mcell.mol_viz.mol_viz_enable = mol_viz_state

                # Restore the current frame
                context.scene.frame_set(fc)

                # Update the main MDL file Scene.main.mdl to insert the DYNAMIC_GEOMETRY directive
                try:

                    full_fname = mainmdl
                    print ( "Updating Main MDL file: " + full_fname + " for dynamic geometry" )
                    
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

                    # Remove the "  obj OBJECT obj {}" lines:
                    for obj in context.scene.mcell.model_objects.object_list:
                        new_lines = []
                        for line in lines:
                            if not "%s OBJECT %s {}" % (obj.name, obj.name) in line:
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
                            mdl_file.write ( "DYNAMIC_GEOMETRY = \"%s\"\n" % (geom_list_name) )
                    mdl_file.close()

                    full_fname = os.path.join(filepath, scene_name + ".initialization.mdl")
                    #print ( "Updating Initialization MDL file: " + full_fname )
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

            #################################
            ### End Dynamic Geometry Export
            #################################

            self.report({'INFO'}, "Project Exported")

        print("End of MCELL_OT_export_project.execute()")

        return {'FINISHED'}


classes = (
            MCELL_OT_export_project,
            MCellProjectPropertyGroup,
            MCellExportProjectPropertyGroup,
          )

def register():
    for cls in classes:
      bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
      bpy.utils.unregister_class(cls)

