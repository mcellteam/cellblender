import os
import sys
import time
import signal
from subprocess import Popen, PIPE
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for data in iter(lambda: out.read(1), b''):
        queue.put(data)
    out.close()



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

    # Run the MCell subprocess

    sp = Popen ( command_list, cwd=script_dir_path, stdin=PIPE, stdout=PIPE, stderr=None, bufsize=0, close_fds=ON_POSIX)
    q = Queue()
    t = Thread(target=enqueue_output, args=(sp.stdout, q))
    t.daemon = False  # thread dies with the program
    t.start()
    
    time.sleep(2)

    t0 = time.time()

    outline = ""

    while sp.poll() is None:
        # read data without blocking
        try:
            data = q.get_nowait() # or q.get(timeout=.1)
        except Empty:
            pass
            # print('No data this time')
        else: # got data
            # ... do something with data
            s = data.decode()
            while '\n' in s:
                i = s.find('\n')
                outline += s[:i]
                print ( outline )
                outline = ""
                s = s[i+1:]
            outline += s
        if (time.time() - t0) > 3:
            try:
                time.sleep(1)
                sp.send_signal ( signal.SIGUSR1 )
                time.sleep(1)
                sp.send_signal ( signal.SIGUSR2 )
                time.sleep(1)
                sp.send_signal ( signal.SIGINT )
            except:
                # Just in case
                print ( "\n\nWarning: Had to kill the subprocess directly. it may not have completed properly." )
                subprocess.Popen.kill ( sp )
    if len(outline) > 0:
        print ( outline )


