import os
import time
import signal
from subprocess import Popen, PIPE

script_dir_path = os.path.dirname(os.path.realpath(__file__))
script_file_path = os.path.join(script_dir_path, "mcell_pipe_cpp")

print("Starting MCell ...")


if not os.path.exists(script_file_path):

    print ( "\n\nUnable to run " + script_file_path + "\n\n" )

else:

    command_list = [ script_file_path, "proj_path="+script_dir_path, "data_model=dm.json" ]

    command_string = "Command:";
    for s in command_list:
      command_string += " " + s
    print ( command_string )

    sp = Popen ( command_list, cwd=script_dir_path, stdin=PIPE, stdout=PIPE, stderr=None ) #, bufsize=0 )
    
    time.sleep(2)

    last_3 = b"   "
    while (sp.poll() is None) and (len(sp.stdout.peek(1)) > 0):
        b = sp.stdout.read(1)
        last_3 = last_3[1:] + b
        print ( "Read " + str(len(b)) + " bytes: " + str(b) )
        if last_3 == b"...":
            break

    print ( "Done reading!!" )

    time.sleep(3)

    try:
        sp.send_signal ( signal.SIGUSR1 )
        time.sleep(1)
        sp.send_signal ( signal.SIGUSR2 )
        time.sleep(1)
        sp.send_signal ( signal.SIGINT )
    except:
        # Just in case
        print ( "\n\nWarning: Had to kill subprocess" )
        subprocess.Popen.kill ( sp )



