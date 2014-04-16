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

import os

bl_info = {
    "name": "CellBlender",
    "author": "Tom Bartol, Jacob Czech, Markus Dittrich, Bob Kuczewski",
    "version": (1, 0, 0),
    "blender": (2, 66, 1),
    "api": 55057,
    "location": "Properties > Scene > CellBlender Panel",
    "description": "CellBlender Modeling System for MCell",
    "warning": "",
    "wiki_url": "http://www.mcell.org",
    "tracker_url": "http://code.google.com/p/cellblender/issues/list",
    "category": "Cell Modeling"
}

cellblender_info = {
    "supported_version_list": [(2, 66, 1), (2, 67, 0), (2, 68, 0), (2, 69, 0), (2, 70, 0)],
    "cellblender_source_list": [
        "__init__.py",
        "parameter_system.py",
        "cellblender_properties.py",
        "cellblender_panels.py",
        "cellblender_operators.py",
        "cellblender_molecules.py",
        "object_surface_regions.py",
        "run_simulations.py",
        "io_mesh_mcell_mdl/__init__.py",
        "io_mesh_mcell_mdl/export_mcell_mdl.py",
        "io_mesh_mcell_mdl/import_mcell_mdl.py",
        "io_mesh_mcell_mdl/import_mcell_mdl_pyparsing.py",
        "io_mesh_mcell_mdl/import_shared.py",
        "io_mesh_mcell_mdl/pyparsing.py",
        "io_mesh_mcell_mdl/mdlmesh_parser.py"],

    "cellblender_source_sha1": "",
    "cellblender_addon_path": "",
    "cellblender_plotting_modules": []
}

simulation_popen_list = []


import hashlib


# Compute, print, and save the SHA1 of all source files in
# cellblender_info["cellblender_source_list"]

def identify_source_version(addon_path):
    cbsl = cellblender_info["cellblender_source_list"]
    hashobject = hashlib.sha1()
    for source_file_basename in cbsl:
        source_file_name = os.path.join(addon_path, source_file_basename)
        if os.path.isfile(source_file_name):
            hashobject.update(open(source_file_name, 'r').read().encode("utf-8"))
            print("  Cumulative SHA1: ", hashobject.hexdigest(), "=",
                  source_file_name)
        else:
            # This is mainly needed in case the make file wasn't run. 
            # (i.e. missing mdlmesh_parser.py)
            print('  File "%s" does not exist' % source_file_name)

    cellblender_info['cellblender_source_sha1'] = hashobject.hexdigest()
    print("CellBlender Source ID = %s" % (cellblender_info[
        'cellblender_source_sha1']))
    sha_file = os.path.join(addon_path, "cellblender_source_sha1.txt")
    open(sha_file, 'w').write(hashobject.hexdigest())


if __name__ == '__main__':
    print("CellBlender is running as __main__")
    identify_source_version("")
    # This might be a good place to exit since this version seems to
    #  crash later if run from the comand line.
    # This is NOT being done in this release in case there was some
    #  other reason to continue, but future releases might uncomment:
    #import sys
    #sys.exit(0)


# To support reload properly, try to access a package var.
# If it's there, reload everything
if "bpy" in locals():
    print("Reloading CellBlender")
    import imp
    imp.reload(cellblender_properties)
    imp.reload(cellblender_panels)
    imp.reload(cellblender_operators)
    #imp.reload(cellblender_parameters)
    imp.reload(parameter_system)
    imp.reload(cellblender_molecules)
    imp.reload(object_surface_regions)
    imp.reload(io_mesh_mcell_mdl)
    imp.reload(mdl)         # BK: Added for MDL
    imp.reload(bng)         # DB: Adde for BNG
    #    imp.reload(sbml)        #JJT: Added for SBML

    # Use "try" for optional modules
    try:
        imp.reload(data_plotters)
    except:
        print("cellblender.data_plotters was not reloaded")
else:
    print("Importing CellBlender")
    """from . import \
        cellblender_properties, \
        cellblender_panels, \
        cellblender_operators, \
        #cellblender_parameters, \
        parameter_system, \
        cellblender_molecules, \
        object_surface_regions, \
        io_mesh_mcell_mdl, \
	      mdl, \ #BK: Added for MDL
        bng, \  # DB: Added for BNG
	      sbml #JJT:SBML"""


    from . import cellblender_properties
    from . import cellblender_panels
    from . import cellblender_operators
    #from . import cellblender_parameters
    from . import parameter_system
    from . import cellblender_molecules
    from . import object_surface_regions
    from . import io_mesh_mcell_mdl
    from . import mdl  # BK: Added for MDL
    from . import bng  # DB: Added for BNG
    #    from . import sbml #JJT: Added for SBML

    # Use "try" for optional modules
    try:
        from . import data_plotters
    except:
        print("cellblender.data_plotters was not imported")


import bpy
import sys


# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)

    # BK: Added for newer parameters ....
    #print ( "Registering parameter_system" )
    #bpy.utils.register_module(parameter_system)


    # Unregister and re-register panels to display them in order
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_cellblender_preferences)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_project_settings)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_run_simulation)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_viz_results)
    #bpy.utils.unregister_class(cellblender_parameters.MCELL_PT_general_parameters)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_model_objects)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_partitions)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_initialization)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_parameters)

    bpy.utils.unregister_class(parameter_system.MCELL_PT_parameter_system)

    bpy.utils.unregister_class(cellblender_molecules.MCELL_PT_define_molecules)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_reactions)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_define_surface_classes)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_mod_surface_regions)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_release_pattern)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_molecule_release)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_reaction_output_settings)
    bpy.utils.unregister_class(cellblender_panels.MCELL_PT_visualization_output_settings)

    bpy.utils.register_class(cellblender_panels.MCELL_PT_cellblender_preferences)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_project_settings)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_run_simulation)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_viz_results)

    #bpy.utils.register_class(cellblender_parameters.MCELL_PT_general_parameters)

    bpy.utils.register_class(parameter_system.MCELL_PT_parameter_system)

    bpy.utils.register_class(cellblender_panels.MCELL_PT_model_objects)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_partitions)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_initialization)
    bpy.utils.register_class(cellblender_molecules.MCELL_PT_define_molecules)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_define_reactions)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_define_surface_classes)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_mod_surface_regions)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_release_pattern)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_molecule_release)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_reaction_output_settings)
    bpy.utils.register_class(cellblender_panels.MCELL_PT_visualization_output_settings)

    bpy.types.INFO_MT_file_import.append(io_mesh_mcell_mdl.menu_func_import)
    bpy.types.INFO_MT_file_export.append(io_mesh_mcell_mdl.menu_func_export)


    # BK: Added for MDL import
    bpy.types.INFO_MT_file_import.append(mdl.menu_func_import)

    # DB: Added for BioNetGen import
    bpy.types.INFO_MT_file_import.append(bng.menu_func_import)

    #JJT: And SBML import
    #bpy.types.INFO_MT_file_import.append(sbml.menu_func_import)

    bpy.types.Scene.mcell = bpy.props.PointerProperty(
        type=cellblender_properties.MCellPropertyGroup)
    bpy.types.Object.mcell = bpy.props.PointerProperty(
        type=object_surface_regions.MCellObjectPropertyGroup)


    print("CellBlender registered")
    if (bpy.app.version not in cellblender_info['supported_version_list']):
        print("Warning, current Blender version", bpy.app.version,
              " is not in supported list:",
              cellblender_info['supported_version_list'])

    print("CellBlender Addon found: ", __file__)
    cellblender_info["cellblender_addon_path"] = os.path.dirname(__file__)
    print("CellBlender Addon Path is ",
          cellblender_info["cellblender_addon_path"])
    addon_path = os.path.dirname(__file__)
    identify_source_version(addon_path)

    # Use "try" for optional modules
    try:
        # print ( "Reloading data_plottters" )
        cellblender_info['cellblender_plotting_modules'] = []
        plotters_list = data_plotters.find_plotting_options()
        # data_plotters.print_plotting_options()
        print("Begin installing the plotters")
        for plotter in plotters_list:
            #This assignment could be done all at once since plotters_list is
            # already a list.
            cellblender_info['cellblender_plotting_modules'] = \
                cellblender_info['cellblender_plotting_modules'] + [plotter]
            print("  System meets requirements for %s" % (plotter.get_name()))
    except:
        print("Error installing some plotting packages" + sys.exc_value)
    
    # Can't do this here: bpy.context.scene.mcell.set_defaults()


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.app.handlers.frame_change_pre.remove(
        cellblender_operators.frame_change_handler)
    bpy.app.handlers.load_post.remove(
        cellblender_operators.clear_run_list)
    bpy.app.handlers.load_post.remove(
        cellblender_operators.model_objects_update)
    bpy.app.handlers.load_post.remove(
        object_surface_regions.object_regions_format_update)
    bpy.app.handlers.load_post.remove(
        cellblender_operators.mcell_valid_update)
    bpy.app.handlers.load_post.remove(
        cellblender_operators.load_preferences)
    bpy.app.handlers.save_pre.remove(
        cellblender_operators.model_objects_update)

    print("CellBlender unregistered")


if len(bpy.app.handlers.frame_change_pre) == 0:
    bpy.app.handlers.frame_change_pre.append(
        cellblender_operators.frame_change_handler)

if len(bpy.app.handlers.load_post) == 0:
    bpy.app.handlers.load_post.append(
        cellblender_operators.clear_run_list)
    bpy.app.handlers.load_post.append(
        cellblender_operators.model_objects_update)
    bpy.app.handlers.load_post.append(
        object_surface_regions.object_regions_format_update)
    bpy.app.handlers.load_post.append(
        cellblender_operators.mcell_valid_update)
    #bpy.app.handlers.load_post.append(
    #    cellblender_operators.set_defaults)
    bpy.app.handlers.load_post.append(
        cellblender_operators.init_properties)
    bpy.app.handlers.load_post.append(
        cellblender_operators.load_preferences)

if len(bpy.app.handlers.save_pre) == 0:
    bpy.app.handlers.save_pre.append(
        cellblender_operators.model_objects_update)

# for testing
if __name__ == '__main__':
    register()
