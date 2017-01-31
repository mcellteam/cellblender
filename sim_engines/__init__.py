import os
import subprocess
import sys

# import cellblender

plug_modules = None

def get_plug_modules():

    module_name_list = []
    module_list = []

    parent_path = os.path.dirname(__file__)

    if parent_path == '':
        parent_path = '.'

    inpath = True
    try:
        if sys.path.index(parent_path) < 0:
            inpath = False
    except:
        inpath = False
    if not inpath:
        sys.path.append ( parent_path )


    # print ( "System path = %s" % (sys.path) ) 
    module_name_list = []
    module_list = []

    print ( "Searching for installed plugins in " + parent_path )

    for f in os.listdir(parent_path):
        if (f != "__pycache__"):
            plugin = os.path.join ( parent_path, f )
            if os.path.isdir(plugin):
                if os.path.exists(os.path.join(plugin,"__init__.py")):
                    print ( "Adding %s " % (plugin) )
                    import_name = plugin
                    module_name_list = module_name_list + [f]
                    print ( "Attempting to import %s" % (import_name) )
                    plugin_module = __import__ ( f )
                    # print ( "Checking requirements for %s" % ( plugin_module.get_name() ) )
                    #if plugin_module.requirements_met():
                    # print ( "System requirements met for Plot Module \"%s\"" % ( plugin_module.get_name() ) )
                    module_list = module_list + [ plugin_module ]
                    #else:
                    #    print ( "System requirements NOT met for Plot Module \"%s\"" % ( plugin_module.get_name() ) )
                    # print ( "Imported __init__.py from %s" % (f) )
    return ( module_list )


