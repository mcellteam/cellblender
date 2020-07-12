import os
import subprocess
import math


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


def plot(data_path, plot_spec, python_path=None):
    program_path = os.path.dirname(__file__)

    plot_cmd = find_in_path("gnuplot")
    
    # Get the file names from the generic command (f=seed_00001/file1.dat f=seed_00001/file2.dat)
    
    file_list = []
    legend = " notitle"

    for plot_param in plot_spec.split():
      if plot_param[0:2] == "f=":
        file_list.append ( plot_param[2:] )
      elif plot_param[0:6] == "legend":
        legend = ""

    num_plots = len(file_list)

    print("This figure has " + str(num_plots) + " plots")

    num_rows = 1
    num_cols = math.trunc(math.ceil(math.sqrt(num_plots)))
    if num_cols <= 0:
      num_cols = 1
    num_rows = math.trunc(math.ceil(num_plots*1.0/num_cols))
    if num_rows <= 0:
      num_rows = 1

    print("This figure will be " + str(num_rows) + "x" + str(num_cols))


    # Create a subprocess running gnuplot

    p = subprocess.Popen ( [plot_cmd, "-persist"], cwd=data_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

    # Send the basic setup commands 
    # NOTE that different terminals migh be used: "wxt", "x11", "tkcanvas", etc. (try "gnuplot" followed by "set term" for others)
    p.stdin.write ( "set terminal x11 size 1200,900\n".encode() )

    p.stdin.write ( "set multiplot\n".encode() )

    plot_w = 1.0 / num_cols
    plot_h = 1.0 / num_rows

    cmd = "set size " + str(plot_w) + "," + str(plot_h) + "\n"
    # print ( "Sending " + cmd )
    p.stdin.write ( cmd.encode() )

    row = 0
    col = 0
    for f in file_list:
      cmd = "set origin " + str(col*plot_w) + "," + str(1.0-((row+1)*plot_h)) + "\n"
      # print ( "Sending " + cmd )
      p.stdin.write ( cmd.encode() )

      cmd = "plot \"" + f + "\" with lines" + legend + "\n"

      # print ( "Sending " + cmd )
      p.stdin.write ( cmd.encode() )
      
      col += 1
      if col >= num_cols:
        col = 0
        row += 1

    p.stdin.write ( "unset multiplot\n".encode() )

    p.stdin.flush()

