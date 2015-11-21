import os
import subprocess
import atexit
import signal

def get_name():
	return ("Browser Plotter")

def requirements_met():
	return True

def plot(data_path, plot_spec, python_cmd):
	program_path = os.path.dirname(__file__)

	if python_cmd is None:
		print("Unable to plot: python not found in path")
	else:
		plot_cmd = []
		plot_cmd.append(python_cmd)
		plot_cmd.append(os.path.join(program_path, "server.py"))	

		print(data_path)
		plot_cmd.append(data_path)
		for spec in plot_spec.split():
			plot_cmd.append(spec)

		print ("Plotting with: \"" + ' '.join(plot_cmd) + "\"")
		server_proc = subprocess.Popen(plot_cmd, cwd = program_path)
		atexit.register(shut_down, server_proc)

def shut_down(proc):
	proc.kill()
