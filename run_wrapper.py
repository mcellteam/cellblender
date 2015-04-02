#!/usr/bin/env python3

import sys
import signal
import subprocess as sp


if __name__ == '__main__':

  wd = sys.argv[1]
  cmd = input()

  r = (b'', b'')
  try:
    proc = sp.Popen(cmd.split(), cwd=wd, stdout=sp.PIPE, stderr=sp.PIPE)

    def sig_term_handler(signum, frame):
      sys.stderr.write('Sending termination signal to child PID: {0}\n'.format(proc.pid))
      proc.send_signal(signum)

    signal.signal(signal.SIGTERM, sig_term_handler)

    r = proc.communicate()
  except Exception as e:
    err_str = '\nrun_cmd error: {0}  cmd: {1}\n'.format(str(e), cmd)
    r = (r[0], (r[1].decode() + err_str).encode())

  sys.stdout.write(r[0].decode())
  sys.stderr.write(r[1].decode())
  exit(abs(proc.returncode))

