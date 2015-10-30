import os
import subprocess


def find_in_path(program_name):
    for path in os.environ.get('PATH', '').split(os.pathsep):
        full_name = os.path.join(path, program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def get_name():
    return("GnuPlot Plotter")


def requirements_met():
    path = find_in_path("gnuplot")
    if path is None:
        print("Required program \"gnuplot\" was not found")
        return False
    else:
        return True


def plot(data_path, plot_spec):
    program_path = os.path.dirname(__file__)

    plot_cmd = find_in_path("gnuplot")
    
    # Get the file names from the generic command (f=seed_00001/file1.dat f=seed_00001/file2.dat)
    
    file_list = []

    for plot_param in plot_spec.split():
      if plot_param[0:2] == "f=":
        file_list.append ( plot_param[2:] )

    # Create a subprocess running gnuplot

    p = subprocess.Popen ( [plot_cmd, "-persist"], cwd=data_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

    for f in file_list:
      cmd = "plot \"" + f + "\" with lines\n"
      print ( "Sending " + cmd )
      p.stdin.write ( cmd.encode() )
    p.stdin.flush()


    #for plot_param in plot_spec.split():
    #    if plot_param[0:2] == "f=":
    #        plot_cmd = plot_cmd + " " + plot_param[2:]

    # pid = subprocess.Popen(plot_cmd.split(), cwd=data_path)
