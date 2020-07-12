import os
import subprocess

def find_in_path(program_name="java"):
    if os.name == "nt":
        program_name = "java.exe"
    for path in os.environ.get('PATH','').split(os.pathsep):
        print ( "Searching " + path + " for " + program_name )
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def subdivide ( l, sep ):
  ''' Splits a list into sublists by dividing at (and removing) instances of sep '''
  nl = []
  c = []
  for s in l:
    if s==sep:
      if len(c) > 0:
        nl = nl + [c]
        c = []
    else:
      c = c + [s]
  if len(c) > 0:
    nl = nl + [c]
  return nl



def get_name():
    return ( "Java Plotter" )


def requirements_met():
    # print ( "Checking requirements for java plot" )
    path = find_in_path()
    if path == None:
        print ( "Required program \"java\" was not found" )
        return False
    else:
        jarfile = "PlotData.jar"
        plot_path = os.path.dirname(__file__)
        # print ("plot_path = ", plot_path )
        if plot_path == '':
            pass
        else:
            jarfile = os.path.join(plot_path, jarfile)
        # print ("Checking for existence of ", jarfile )
        if os.path.exists ( jarfile ):
            return True
        else:
            print ( "Required file: PlotData.jar was not found" )
            return False


def plot ( data_path, plot_spec, python_path=None ):
    print ( "Java plot called with \"" + data_path + "\", and \"" + plot_spec + "\"" );
    program_path = os.path.dirname(__file__)
    # print ( "Java Plotter called with %s, %s" % (data_path, plot_spec) )
    # print ( "Plotter-specific files are located here: %s" % ( program_path ) )
    
    # Subdivide the plot spec by "page"
    
    plot_spec = subdivide ( plot_spec.split(), "page" )
    color_spec = ""
    
    any_found = False

    for page in plot_spec:

        # The java program only understands color=#rrggbb and fxy=filename parameters so find "f=":

        found = False
        for generic_param in page:
            if generic_param[0:2] == "f=":
                found = True
                any_found = True
                break

        # Go through the entire plot command (whether found or not) to set other settings

        java_plot_spec = ""
        for generic_param in page:
            if generic_param[0:2] == "f=":
                java_plot_spec = java_plot_spec + " fxy=" + generic_param[2:]
            elif generic_param[0:4] == "ppt=":
                java_plot_spec = java_plot_spec + " name=" + generic_param[4:]
            elif generic_param[0:7] == "color=#":
                java_plot_spec = java_plot_spec + " color=" + generic_param[7:]

        if found:
            popen_list = []
            popen_list.append ( find_in_path() )
            popen_list.append ( "-jar" )
            popen_list.append ( os.path.join ( program_path, "PlotData.jar" ) )
            popen_list.append ( 'path=' + data_path )
            for ps in java_plot_spec.split():
              popen_list.append ( ps )
            print ( "Calling popen with " + str(popen_list) )
            pid = subprocess.Popen ( popen_list, cwd=data_path )

    if not any_found:

        # Bring up an empty plotting window (useful for pure MDL runs)

        popen_list = []
        popen_list.append ( find_in_path() )
        popen_list.append ( "-jar" )
        popen_list.append ( os.path.join ( program_path, "PlotData.jar" ) )
        popen_list.append ( 'path=' + data_path )
        for ps in java_plot_spec.split():
          popen_list.append ( ps )
        print ( "Calling popen with " + str(popen_list) )
        pid = subprocess.Popen ( popen_list, cwd=data_path )

