#!/usr/bin/env python3

from sim_runner_queue import OutputQueue
import sys
import signal
import subprocess as sp


def parse_quoted_args ( s ):
    # Turn a string of quoted arguments into a list of arguments
    # This code handles escaped quotes (\") and escaped backslashes (\\)
    args = []
    next = ""
    inquote = False
    escaped = False
    i = 0
    while i < len(s):
        if s[i] == '"':
            if escaped:
                next += '"'
                escaped = False
            else:
                if inquote:
                    args.append ( next )
                    next = ""
                inquote = not inquote
        elif s[i] == '\\':
            if escaped:
                next += '\\'
                escaped = False
            else:
                escaped = True
        else:
            if inquote:
                next += s[i]
        i += 1
    if len(next) > 0:
        args.append ( next )
    return args



if __name__ == '__main__':

  wd = sys.argv[1]
  if sys.version_info.major == 3:
    cmd = input()
    args = input()
  else:
    cmd = raw_input()
    args = raw_input()

  sys.stdout.write('\n\nMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM\n')
  sys.stdout.write('Running run_wrapper.py with \n  cmd: {0}   \n  args: {1}   \n  wd: {2}\n'.format(cmd, args, wd))

  cmd_list = []
  if (cmd.strip()[0] == '"') and (cmd.strip()[-1] == '"'):
    sys.stdout.write("\nUsing quoted command syntax\n")
    # Using quoted command syntax, so remove quotes before adding
    cmd_list = parse_quoted_args(cmd.strip())
  else:
    sys.stdout.write("\nUsing string command syntax\n")
    # Just add the string as before
    cmd_list.append(cmd)

  if (args.strip()[0] == '"') and (args.strip()[-1] == '"'):
    sys.stdout.write("\nUsing quoted arg syntax\n")
    # Using quoted arguments syntax (space separated list of strings), so remove quotes before adding
    cmd_list.append ( cmd.strip()[1:-1] )
  else:
    sys.stdout.write("\nUsing string arg syntax\n")
    # Just add the strings split by spaces as before
    cmd_list.extend(args.split())

  sys.stdout.write ( "\nFinal cmd_list: " + str(cmd_list) )

  sys.stdout.write('\nMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM\n\n\n')

  proc = sp.Popen(cmd_list, cwd=wd, bufsize=1, shell=False, close_fds=False, stdout=sp.PIPE, stderr=sp.PIPE)

  def sig_handler(signum, frame):
    sys.stdout.write('\nSending signal: {0} to child PID: {1}\n'.format(signum, proc.pid))
    sys.stdout.flush()
    proc.send_signal(signum)
    sys.stdout.write('\nTerminated run_wrapper.py\n')
    sys.stdout.flush()
    exit(15)

  signal.signal(signal.SIGTERM, sig_handler)

  output_q = OutputQueue() 
  rc, res = output_q.run_proc(proc,passthrough=True)

  exit(abs(rc))

