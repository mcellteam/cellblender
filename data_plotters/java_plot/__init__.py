import os
import subprocess

def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None



def get_name():
    return ( "Java Plotter" )


def requirements_met():
    print ( "Checking requirements for java plot" )
    path = find_in_path ( "java" )
    if path == None:
        print ( "Required program \"java\" was not found" )
        return False
    else:
        jarfile = "PlotData.jar"
        print ("Checking for existence of ", jarfile )
        plot_path = os.path.dirname(__file__)
        print ("plot_path = ", plot_path )
        if plot_path == '':
            pass
        else:
            jarfile = os.path.join(plot_path, jarfile)
        print ("Checking for existence of ", jarfile )
        if os.path.exists ( jarfile ):
            return True
        else:
            print ( "PlotData.jar was not found" )
            return False


def plot ( data_path, plot_spec ):
    program_path = os.path.dirname(__file__)
    print ( "Java Plotter called with %s, %s" % (data_path, plot_spec) )
    print ( "Plotter-specific files are located here: %s" % ( program_path ) )
    
    # The java program only understands fxy=filename parameters so translate:
    
    java_plot_spec = ""
    for generic_param in plot_spec.split():
        if generic_param[0:2] == "f=":
            java_plot_spec = java_plot_spec + " fxy=" + generic_param[2:]
    
    plot_cmd = find_in_path("java")
    plot_cmd = plot_cmd + ' -jar ' + os.path.join ( program_path, 'PlotData.jar' ) + " "
    plot_cmd = plot_cmd + java_plot_spec
    pid = subprocess.Popen ( plot_cmd.split(), cwd=data_path )
