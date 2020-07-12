import os
import subprocess

from cellblender.cellblender_utils import get_python_path

def get_name():
    return("Simple Plotter")


def requirements_met():
    ok = True
    required_modules = ['matplotlib', 'matplotlib.pyplot', 'pylab', 'numpy']
    python_command = get_python_path(required_modules=required_modules)
    if python_command is None:
        print("  Python is needed for \"%s\"" % (get_name()))
        ok = False
    return ok


def plot(data_path, plot_spec, python_path=None):
    # The bundled version of python now has maplotlib, so we can use it here.
    program_path = os.path.dirname(__file__)
    print("Simple Plotter called with %s, %s" % (data_path, plot_spec))
    print("Plotter-specific files are located here: %s" %(program_path))

    # mpl_simple.py expects plain file names so translate:

    python_cmd = python_path
    plot_cmd = []
    plot_cmd.append(python_cmd)

    if plot_cmd is None:
        print("Unable to plot: python not found in path")
    else:
        plot_cmd.append(os.path.join(program_path, "mpl_simple.py"))

        generic_params = plot_spec.split()

        legend = False
        for generic_param in generic_params:
            if "legend" in generic_param:
                legend = True

        if legend:
          plot_cmd.append ( "-legend" )
        else:
          plot_cmd.append ( "-no-legend" )

        for generic_param in generic_params:
            if generic_param[0:2] == "f=":
                plot_cmd.append(generic_param[2:])
            elif generic_param[0:4] == "ppt=":
                plot_cmd.append("-n=" + generic_param[4:])

        print ( "Plotting from: " + data_path )
        print ( "Plot Command:  " + " ".join(plot_cmd) )
        pid = subprocess.Popen(plot_cmd, cwd=data_path)
