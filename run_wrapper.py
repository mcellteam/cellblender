#!/usr/bin/env python3

from sim_runner_queue import OutputQueue
import sys
import signal
import subprocess as sp
import time


if __name__ == '__main__':

  wd = sys.argv[1]
  if sys.version_info.major == 3:
    cmd = input()
  else:
    cmd = raw_input()

#  sys.stdout.write('Starting cmd: {0}   with wd: {1}\n'.format(cmd, wd))

  term = False
  proc = sp.Popen(cmd.split(), cwd=wd, bufsize=1, shell=False, stdout=sp.PIPE, stderr=sp.PIPE)

  def sig_handler(signum, frame):
    sys.stdout.write('Sending signal: {0} to PID: {1}\n'.format(signum, proc.pid))
    sys.stdout.flush()
    term = True
    proc.send_signal(signum)

  signal.signal(signal.SIGTERM, sig_handler)

  output_q = OutputQueue() 
  rc, res = output_q.run_proc(proc,passthrough=True)
  if term:
    rc = 15

  exit(abs(rc))

