import os
import subprocess
import time
import sys
import pickle
import shutil

import cellblender
from cellblender import cellblender_utils

import cellblender.cellblender_simulation as cellblender_sim

from cellblender.cellblender_utils import mcell_files_path


from bpy.props import CollectionProperty, StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

import cellblender.sim_engines as engine_manager

from . import export_project_mcell_3


print ( "Executing MCell Simulation" )

# Name of this engine and to display in the list of choices
# Both should be unique within a CellBlender installation
plug_code = "MCELL3"
plug_name = "MCell 3 with Dynamic Geometry"

def print_info():
    global parameter_dictionary
    print ( 30*'==' + " Engine Parameters " + 30*'==' )
    for k in sorted(parameter_dictionary.keys()):
        print ( "" + k + " = " + str(parameter_dictionary[k]) )
    print ( 30*'==' + "===================" + 30*'==' )
    print ( '\n' )

def print_version():
    global parameter_dictionary
    print_info()
    subprocess.Popen ( [parameter_dictionary['MCell Path']['val'], "-version"] )

def print_full_version():
    global parameter_dictionary
    print_info()
    subprocess.Popen ( [parameter_dictionary['MCell Path']['val'], "-fullversion"] )

def print_help():
    global parameter_dictionary
    print_info()
    subprocess.Popen ( [parameter_dictionary['MCell Path']['val'], "-help"] )



def reset():
    global parameter_dictionary
    print ( "Resetting all Engine Parameters" )
    parameter_dictionary['Log File']['val'] = ""
    parameter_dictionary['Error File']['val'] = ""


# Get data from Blender / CellBlender
import bpy
mcell_path = ""
try:
    mcell_path = bpy.context.scene.mcell.cellblender_preferences.mcell_binary
except:
    mcell_path = ""


# List of parameters as dictionaries - each with keys for 'name', 'desc', 'def', and optional 'as':
parameter_dictionary = {
    'MCell Path': {'val': mcell_path, 'as':'filename', 'desc':"MCell Path", 'icon':'SCRIPTWIN'},
    'Log File': {'val':"", 'as':'filename', 'desc':"Log File name", 'icon':'EXPORT'},
    'Error File': {'val':"", 'as':'filename', 'desc':"Error File name", 'icon':'EXPORT'},
    'Version': {'val': print_version, 'desc':"Print Version"},
    'Full Version': {'val': print_full_version, 'desc':"Print Full Version"},
    'Help': {'val': print_help, 'desc':"Print Help"},
    'Reset': {'val': reset, 'desc':"Reset everything"},
    'Output Detail (0-100)': {'val': 20, 'desc':"Output Detail"}  # This is used below but may not be shown as a user option
}

parameter_layout = [
    ['MCell Path'],
    ['Version', 'Full Version', 'Help', 'Reset'],
    ['Log File', 'Error File' ]
]


def blend_to_path ( path ):
  if path.startswith ('//'):
    # This is a special Blender-relative path like this: //../../../dir/mcell
    blend_file_path = os.path.dirname(bpy.data.filepath)
    path = os.path.abspath ( os.path.join ( blend_file_path, path[2:] ) )
    return path
  else:
    # This isn't a special Blender-relative path:
    return path



def draw_layout ( self, context, layout ):
    mcell = context.scene.mcell
    run_sim = mcell.run_simulation
    ps = mcell.parameter_system

    row = layout.row()
    run_sim.start_seed.draw(layout,ps)
    run_sim.end_seed.draw(layout,ps)
    run_sim.run_limit.draw(layout,ps)

    row = layout.row()
    row.prop(run_sim, "mcell_processes")
    #row = layout.row()
    #row.prop(run_sim, "log_file")
    #row = layout.row()
    #row.prop(run_sim, "error_file")
    row = layout.row()
    row.prop(mcell.export_project, "export_format")


    row = layout.row()
    row.prop(run_sim, "remove_append", expand=True)

    if cellblender_sim.global_scripting_enabled_once:
        helptext = "Allow Running of Python Code in Scripting Panel - \n" + \
                   " \n" + \
                   "The Scripting Interface can run Python code contained\n" + \
                   "in text files (text blocks) within Blender.\n" + \
                   "\n" + \
                   "Running scripts from unknown sources is a security risk.\n" + \
                   "Only enable this option if you are confident that all of\n" + \
                   "the scripts contained in this .blend file are safe to run."
        ps.draw_prop_with_help ( layout, "Enable Python Scripting", run_sim,
                   "enable_python_scripting", "python_scripting_show_help",
                   run_sim.python_scripting_show_help, helptext )
    else:
        helptext = "Initialize Python Code Scripting for this Session\n" + \
                   "This must be done each time CellBlender is restarted."
        ps.draw_operator_with_help ( layout, "Enable Python Scripting", run_sim,
                   "mcell.initialize_scripting", "python_initialize_show_help",
                   run_sim.python_initialize_show_help, helptext )

    row = layout.row()
    col = row.column()
    col.prop(mcell.cellblender_preferences, "decouple_export_run")




def prepare_runs_no_data_model ( project_dir ):

    print ( "MCell 3 Engine is preparing runs from Blender properties without a data model." )

    command_list = []

    context = bpy.context

    mcell = context.scene.mcell
    mcell.run_simulation.last_simulation_run_time = str(time.time())

    binary_path = mcell.cellblender_preferences.mcell_binary
    binary_path = blend_to_path ( parameter_dictionary['MCell Path']['val'] )  # Over-ride the preferences with the value in the engine itself.

    mcell.cellblender_preferences.mcell_binary_valid = cellblender_utils.is_executable ( binary_path )

    start = int(mcell.run_simulation.start_seed.get_value())
    end = int(mcell.run_simulation.end_seed.get_value())
    mcell_processes_str = str(mcell.run_simulation.mcell_processes)
    mcell_binary = mcell.cellblender_preferences.mcell_binary
    # Force the project directory to be where the .blend file lives
    mcell_files = mcell_files_path()
    project_dir = os.path.join( mcell_files, "output_data" )
    status = ""

    if not mcell.cellblender_preferences.decouple_export_run:
        print ( "MCell 3 Engine is exporting the project" )
        export_project_mcell_3.export_project ( context )
        # bpy.ops.mcell.export_project()
        print ( "MCell 3 Engine is done exporting the project" )

    if (mcell.run_simulation.error_list and
            mcell.cellblender_preferences.invalid_policy == 'dont_run'):
        pass
    else:
        react_dir = os.path.join(project_dir, "react_data")
        if (os.path.exists(react_dir) and
                mcell.run_simulation.remove_append == 'remove'):
            shutil.rmtree(react_dir)
        if not os.path.exists(react_dir):
            os.makedirs(react_dir)

        viz_dir = os.path.join(project_dir, "viz_data")
        if (os.path.exists(viz_dir) and
                mcell.run_simulation.remove_append == 'remove'):
            shutil.rmtree(viz_dir)
        if not os.path.exists(viz_dir):
            os.makedirs(viz_dir)

        base_name = mcell.project_settings.base_name

        error_file_option = mcell.run_simulation.error_file
        log_file_option = mcell.run_simulation.log_file
        script_dir_path = os.path.dirname(os.path.realpath(__file__))

        engine_manager.write_default_data_layout(mcell_files, start, end)

        for sim_seed in range(start,end+1):
            new_command = [ mcell_binary, "-seed",  str(sim_seed), os.path.join(project_dir, "%s.main.mdl" % base_name) ]

            cmd_entry = {}
            cmd_entry['cmd'] = mcell_binary
            cmd_entry['wd'] = project_dir
            cmd_entry['args'] = [ "-seed", str(sim_seed), os.path.join(project_dir, "%s.main.mdl" % base_name) ]
            cmd_entry['stdout'] = ""
            cmd_entry['stderr'] = ""
            command_list.append ( cmd_entry )

    # mcell.run_simulation.status = status

    print ( "MCell 3 Engine is returning a command list." )

    return ( command_list )


def get_progress_message_and_status ( stdout_txt ):
  progress_message = "?"
  task_complete = False
  # MCell 3.3 iteration lines look like this:
  # Iterations: 40 of 100  (50.8182 iter/sec)
  for i in reversed(stdout_txt.split("\n")):
      if i.startswith("Iterations"):
          last_iter = int(i.split()[1])
          total_iter = int(i.split()[3])
          percent = int((last_iter/total_iter)*100)
          if (last_iter == total_iter) and (total_iter != 0):
              task_complete = True
          progress_message = "MCell3 Dynamic Geometry: %d%%" % (percent)
          break
  return ( progress_message, task_complete )


#def postprocess_runs ( data_model, command_strings ):
#  # Move and/or transform data to match expected CellBlender file structure as required
#  pass



class ImportMCellMDL(bpy.types.Operator, ImportHelper):
    '''Load an MCell MDL geometry file with regions'''
    bl_idname = "import_mdl_mesh.mdl"
    bl_label = "Import MCell MDL"
    bl_options = {'UNDO'}

    files = CollectionProperty(name="File Path",
                          description="File path used for importing "
                                      "the MCell MDL file",
                          type=bpy.types.OperatorFileListElement)

    directory = StringProperty()

    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    add_to_model_objects = BoolProperty(
        name="Add to Model Objects",
        description="Automatically add all meshes to the Model Objects list",
        default=True,)

    def execute(self, context):
        paths = [os.path.join(self.directory, name.name) for name in self.files]
        if not paths:
            paths.append(self.filepath)

        # Attempt to use fast swig importer (assuming make was successful)
        try:
            from . import import_mcell_mdl
            from . import mdlmesh_parser

            for path in paths:
                import_mcell_mdl.load(
                    self, context, path, self.add_to_model_objects)

        # Fall back on slow pure python parser (pyparsing)
        except ImportError:
            from . import import_mcell_mdl_pyparsing

            for path in paths:
                import_mcell_mdl_pyparsing.load(
                    self, context, path, self.add_to_model_objects)


        return {'FINISHED'}


class ExportMCellMDL(bpy.types.Operator, ExportHelper):
    '''Export selected mesh objects as MCell MDL geometry with regions'''
    bl_idname = "export_mdl_mesh.mdl"
    bl_label = "Export MCell MDL"

    print ( ":::::::::io_mesh_mcell_mdl/__init__.py/ExportMCellMDL initialization" )

    filename_ext = ".mdl"
    filter_glob = StringProperty(default="*.mdl", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        #print ( "io_mesh_mcell_mdl/__init__.py/ExportMCellMDL.poll()" )
        return len([obj for obj in context.selected_objects if obj.type == 'MESH']) != 0

    def execute(self, context):
        #print ( "io_mesh_mcell_mdl/__init__.py/ExportMCellMDL.execute()" )
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)
        from . import export_mcell_mdl
        object_list = [obj for obj in context.selected_objects if obj.type == 'MESH']
        with open(filepath, "w", encoding="utf8", newline="\n") as out_file:
            export_mcell_mdl.save_geometry(context, out_file, object_list)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportMCellMDL.bl_idname, text="MCell MDL Geometry (.mdl)")


def menu_func_export(self, context):
    self.layout.operator(ExportMCellMDL.bl_idname, text="MCell MDL Geometry (.mdl)")



def register_blender_classes():
    print ( "Registering MCell 3 Engine classes" )
    bpy.utils.register_class(ImportMCellMDL)
    bpy.utils.register_class(ExportMCellMDL)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    print ( "Done Registering" )

def unregister_this_class(this_class):
    try:
      bpy.utils.unregister_class(this_class)
    except Exception as ex:
      pass

def unregister_blender_classes():
    print ( "UnRegistering MCell 3 Engine classes" )
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    unregister_this_class (ExportMCellMDL)
    unregister_this_class (ImportMCellMDL)
    print ( "Done Unregistering" )


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    pass
