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

    # XmGrace expects plain file names so translate:

    plot_cmd = find_in_path("gnuplot")
    
    # plot_cmd += " -persist -e \"plot sin(x) with lines\""

    p = subprocess.Popen ( [plot_cmd], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    si = p.stdin
    so = p.stdout
    se = p.stderr
    
    si.write ( b"plot cos(2*x)\n" )
    si.flush()


    #for plot_param in plot_spec.split():
    #    if plot_param[0:2] == "f=":
    #        plot_cmd = plot_cmd + " " + plot_param[2:]

    # pid = subprocess.Popen(plot_cmd.split(), cwd=data_path)
