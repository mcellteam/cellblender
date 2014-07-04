import sys
import os
import hashlib

cellblender_info = {
    "supported_version_list": [(2, 66, 1), (2, 67, 0), (2, 68, 0), (2, 69, 0), (2, 70, 0)],

    "cellblender_source_list": [
        "__init__.py",
        "data_model.py",
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
        "io_mesh_mcell_mdl/mdlmesh_parser.py",
        "mdl/__init__.py",
        "bng/__init__.py",
        "bng/sbml2blender.py",
        "bng/sbml2json.py",
        "bng/external_operators.py",
        "bng/sbml_operators.py",
        "bng/sbml_properties.py",
        "bng/bng_operators.py",
        "bng/treelib3/__init__.py",
        "bng/treelib3/node.py",
        "bng/treelib3/tree.py",
        "bng/libsbml3/__init__.py",
        ],

    "cellblender_source_sha1": "",
    "cellblender_addon_path": "",
    "cellblender_plotting_modules": []
}


def identify_source_version(addon_path,verbose=False):
    """ Compute the SHA1 of all source files in cellblender_info["cellblender_source_list"]"""
    cbsl = cellblender_info["cellblender_source_list"]
    hashobject = hashlib.sha1()
    for source_file_basename in cbsl:
        source_file_name = os.path.join(addon_path, source_file_basename)
        if os.path.isfile(source_file_name):
            hashobject.update(open(source_file_name, 'rb').read())  # .encode("utf-8"))
            #if verbose:
            #    print("  Cumulative SHA1 = " + str(hashobject.hexdigest()) + " after adding " + source_file_name )
        else:
            # This is mainly needed in case the make file wasn't run. 
            # (i.e. missing mdlmesh_parser.py)
            #print('  File "%s" does not exist' % source_file_name)
            pass

    cellblender_info['cellblender_source_sha1'] = hashobject.hexdigest()


def print_source_list (addon_path,verbose=False):
    """ Compute the SHA1 of all source files in cellblender_info["cellblender_source_list"]"""
    cbsl = cellblender_info["cellblender_source_list"]
    for source_file in cbsl:
        if os.path.isfile(source_file):
            print( "cellblender" + os.sep + source_file )


if __name__ == '__main__':

    """Run this file from the command line to update the cellblender_id.py file """

    id_file_name = "cellblender_id.py"
    #print("CellBlender is running as __main__ ... will generate " + id_file_name )
    identify_source_version(os.path.dirname(__file__),verbose=True)
    cb_id_statement = "cellblender_id = '" + cellblender_info['cellblender_source_sha1'] + "'\n"
    sha_file = os.path.join(os.path.dirname(__file__), id_file_name)
    open(sha_file, 'w').write(cb_id_statement)
    #print ( cb_id_statement )
    print_source_list(os.path.dirname(__file__))
    import sys
    sys.exit(0)
