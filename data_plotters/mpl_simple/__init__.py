import os
import subprocess
import sys


def find_in_path(program_name):
    for path in os.environ.get('PATH', '').split(os.pathsep):
        full_name = os.path.join(path, program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def get_name():
    return("Simple Plotter")


def requirements_met():
    ok = True
    required_modules = ['matplotlib', 'matplotlib.pyplot', 'pylab', 'numpy',
                        'scipy']
    python_command = find_in_path("python")
    if python_command is None:
        print("  Python is needed for \"%s\"" % (get_name()))
        ok = False
    else:
        for plot_mod in required_modules:
            import_test_program = 'import %s\nprint("Found=OK")' % (plot_mod)
            process = subprocess.Popen(
                [python_command, '-c', import_test_program],
                shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            process.poll()
            output = process.stdout.readline()
            strout = str(output)
            if (strout is not None) & (strout.find("Found=OK") >= 0):
                # print("  ", plot_mod,
                #       "is available through external python interpreter")
                pass
            else:
                print("  ", plot_mod,
                      "is not available through external python interpreter")
                ok = False
    return ok


def plot(data_path, plot_spec):
    program_path = os.path.dirname(__file__)
    # print("Simple Plotter called with %s, %s" % (data_path, plot_spec))
    # print("Plotter-specific files are located here: %s" %(program_path))

    # mpl_simple.py expects plain file names so translate:

    plot_cmd = find_in_path("python")

    if plot_cmd is None:
        print("Unable to plot: python not found in path")
    else:
        plot_cmd = plot_cmd + " " + os.path.join(program_path, "mpl_simple.py")
        for generic_param in plot_spec.split():
            if generic_param[0:2] == "f=":
                plot_cmd = plot_cmd + " " + generic_param[2:]
        pid = subprocess.Popen(plot_cmd.split(), cwd=data_path)
