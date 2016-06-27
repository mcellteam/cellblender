import os
import subprocess
import shutil

from cellblender.cellblender_utils import get_python_path

def get_name():
    return("MatPlotLib Plotter")


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
    # print("MPL Plotter called with %s, %s" % (data_path, plot_spec))
    # print("Plotter-specific files are located here: %s" %(program_path))

    # mpl_plot.py accepts all generic parameters, so no translation is needed

    python_cmd = python_path

    if python_cmd is None:
        print("Unable to plot: python not found in path")
    else:
        plot_cmd = []
        plot_cmd.append(python_cmd)
        plot_cmd.append(os.path.join(program_path, "mpl_plot.py"))

        defaults_name = os.path.join(data_path, "mpl_defaults.py")
        print("Checking for defaults file at: " + defaults_name)
        if os.path.exists(defaults_name):
            plot_cmd.append("defs=" + defaults_name)
        else:
            defaults_name = os.path.join(program_path, "mpl_defaults.py")
            print("Checking for defaults file at: " + defaults_name)
            if os.path.exists(defaults_name):
                plot_cmd.append("defs=" + defaults_name)

        for generic_param in plot_spec.split():
            plot_cmd.append(generic_param)

        print ( "Plotting from: " + data_path )
        print ( "Plotting with: \"" + ' '.join(plot_cmd) + "\"" )
        pid = subprocess.Popen(plot_cmd, cwd=data_path)
