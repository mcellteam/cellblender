#!/usr/bin/env python3

import sys
import signal
import subprocess as sp


def run_cmd(cmd,cmd_wd='.'):

     print('run_cmd starting...')
     try:
       proc = sp.Popen(cmd.split(), cwd=cmd_wd, stdout=sp.PIPE, stderr=sp.PIPE)

       def sig_handler(signum, frame):
         print('Sending signal: {0} to PID: {1}'.format(signum,proc.pid))
         proc.send_signal(signum)

       signal.signal(signal.SIGTERM, sig_handler)

       r = proc.communicate()
       print('run_cmd finished.')
     except Exception as e:
        r = 'run_cmd error: %s  cmd: %s' % (str(e), cmd)

     return r


if __name__ == '__main__':

  cmd_wd = sys.argv[1]
  cmd_str = input()

  print ('cmd_str: ', cmd_str, '  cmd_wd: ', cmd_wd)
  res = run_cmd(cmd_str,cmd_wd)

