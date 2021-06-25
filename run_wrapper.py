#!/usr/bin/env python3

import os
from sim_runner_queue import OutputQueue
import sys
import signal
import subprocess as sp


if not sys.warnoptions:
  import warnings
  warnings.simplefilter("ignore")


def is_windows ():

    if os.name.startswith('posix'):
      return False
    if os.name.startswith('nt'):
      return True

    if sys.platform.startswith('win'):
      return True
    if sys.platform.startswith('cygwin'):
      return True
    if sys.platform.startswith('linux'):
      return False
    if sys.platform.startswith('darwin'):
      return False
    if sys.platform.startswith('freebsd'):
      return False
    if sys.platform.startswith('sunos'):
      return False


def parse_quoted_args_posix ( s ):
    # Turn a string of quoted arguments into a list of arguments
    # This code handles escaped quotes (\") and escaped backslashes (\\)
    print ( "parse_quoted_args_posix got " + s )
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


def parse_quoted_args_windows ( s ):
	# Turn a string of quoted arguments into a list of arguments
	print ( "parse_quoted_args_windows got " + s )
	args = []
	next = ""
	inquote = False
	escaped = False
	i = 0
	while i < len(s):
		if s[i] == '"':
			if inquote:
				args.append ( next )
				next = ""
			inquote = not inquote
		else:
			if inquote:
				next += s[i]
		i += 1
	if len(next) > 0:
		args.append ( next )
	print ( "parse_quoted_args_windows returning " + str(args) )
	return args

def convert_for_windows ( cmds ):
	wcmds = []
	for cmd in cmds:
		if cmd.upper().startswith ( "C:" ):
			wcmds.append ( "c:\\" + cmd[2:] )
		else:
			wcmds.append ( cmd )
	return ( wcmds )



if __name__ == '__main__':

  if is_windows():

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
        sys.stdout.write("\nUsing quoted command syntax with cmd:\n " + cmd )
        # Using quoted command syntax, so remove quotes before adding
        cmd_list.extend ( parse_quoted_args_windows(cmd.strip()) )
      else:
        sys.stdout.write("\nUsing string command syntax\n")
        # Just add the string as before
        cmd_list.append(cmd)

      if (args.strip()[0] == '"') and (args.strip()[-1] == '"'):
        sys.stdout.write("\nUsing quoted arg syntax\n")
        cmd_list.extend ( parse_quoted_args_windows ( args.strip() ) )
        # Using quoted arguments syntax (space separated list of strings), so remove quotes before adding
        # cmd_list.append ( cmd.strip()[1:-1] )
      else:
        sys.stdout.write("\nUsing string arg syntax\n")
        # Just add the strings split by spaces as before
        cmd_list.extend(args.split())

      sys.stdout.write ( "\nNormal cmd_list: " + str(cmd_list) )
      cmd_list = convert_for_windows ( cmd_list )
      sys.stdout.write ( "\nWindows cmd_list: " + str(cmd_list) )

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

  else:

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
        sys.stdout.write("\nUsing quoted command syntax with cmd:\n " + cmd )
        # Using quoted command syntax, so remove quotes before adding
        cmd_list.extend ( parse_quoted_args_posix(cmd.strip()) )
      else:
        sys.stdout.write("\nUsing string command syntax\n")
        # Just add the string as before
        cmd_list.append(cmd)

      if (args.strip()[0] == '"') and (args.strip()[-1] == '"'):
        sys.stdout.write("\nUsing quoted arg syntax\n")
        cmd_list.extend ( parse_quoted_args_posix(args.strip()) )
        # Using quoted arguments syntax (space separated list of strings), so remove quotes before adding
        # cmd_list.append ( cmd.strip()[1:-1] )
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




'''
WINDOWS VERSION (copy and pasted from VM)

#!/usr/bin/env python3

from sim_runner_queue import OutputQueue
import sys
import signal
import subprocess as sp


def linux_parse_quoted_args ( s ):
    # Turn a string of quoted arguments into a list of arguments
    # This code handles escaped quotes (\") and escaped backslashes (\\)
    print ( "parse_quoted_args got " + s )
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
    print ( "parse_quoted_args returning " + str(args) )
    return args

def parse_quoted_args_windows ( s ):
	# Turn a string of quoted arguments into a list of arguments
	# This code handles escaped quotes (\") and escaped backslashes (\\)
	print ( "parse_quoted_args_windows got " + s )
	args = []
	next = ""
	inquote = False
	escaped = False
	i = 0
	while i < len(s):
		if s[i] == '"':
			if inquote:
				args.append ( next )
				next = ""
			inquote = not inquote
		else:
			if inquote:
				next += s[i]
		i += 1
	if len(next) > 0:
		args.append ( next )
	print ( "parse_quoted_args_windows returning " + str(args) )
	return args

def convert_for_windows ( cmds ):
	wcmds = []
	for cmd in cmds:
		if cmd.upper().startswith ( "C:" ):
			wcmds.append ( "c:\\" + cmd[2:] )
		else:
			wcmds.append ( cmd )
	return ( wcmds )

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
    sys.stdout.write("\nUsing quoted command syntax with cmd:\n " + cmd )
    # Using quoted command syntax, so remove quotes before adding
    cmd_list.extend ( parse_quoted_args_windows(cmd.strip()) )
  else:
    sys.stdout.write("\nUsing string command syntax\n")
    # Just add the string as before
    cmd_list.append(cmd)

  if (args.strip()[0] == '"') and (args.strip()[-1] == '"'):
    sys.stdout.write("\nUsing quoted arg syntax\n")
    cmd_list.extend ( parse_quoted_args_windows ( args.strip() ) )
    # Using quoted arguments syntax (space separated list of strings), so remove quotes before adding
    # cmd_list.append ( cmd.strip()[1:-1] )
  else:
    sys.stdout.write("\nUsing string arg syntax\n")
    # Just add the strings split by spaces as before
    cmd_list.extend(args.split())

  sys.stdout.write ( "\nNormal cmd_list: " + str(cmd_list) )
  cmd_list = convert_for_windows ( cmd_list )
  sys.stdout.write ( "\nWindows cmd_list: " + str(cmd_list) )

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

'''

