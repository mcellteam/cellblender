import os
import subprocess

def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None



def get_name():
    return ( "XmGrace Plotter" )


def requirements_met():
    print ( "Checking requirements for xmgrace" )
    path = find_in_path ( "xmgrace" )
    if path == None:
        print ( "Required program \"xmgrace\" was not found" )
        return False
    else:
        return True


def plot ( data_path, plot_spec ):
    program_path = os.path.dirname(__file__)
    print ( "XmGrace Plotter called with %s, %s" % (data_path, plot_spec) )
    print ( "Plotter-specific files are located here: %s" % ( program_path ) )
    
    # XmGrace expects plain file names so translate:
    
    plot_cmd = find_in_path ( "xmgrace" )
    
    for generic_param in plot_spec.split():
        if generic_param[0:2] == "f=":
            plot_cmd = plot_cmd + " " + generic_param[2:]
    
    pid = subprocess.Popen ( plot_cmd.split(), cwd=data_path )
