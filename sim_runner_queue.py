import os
from queue import Queue
from threading import Thread
import subprocess as sp
import multiprocessing
from argparse import ArgumentParser
import time


def q_start(cpus):
  q = Queue(maxsize=0)
  start_thread_workers(cpus,q,notify)
  return q

def q_stop(q):
  

def run_q_item(q,notify):
  while True:
    process, cmd_str = q.get()
    process.communicate('{0}'.format(cmd_str).encode())
    if notify:
        print(process.pid, cmd_str)
    q.task_done()


def start_thread_workers(n_threads,q,notify):
  for i in range(n_threads):
    worker = Thread(target=run_q_item, args=(q,notify,))
    worker.setDaemon(True)
    worker.start()


def q_add_cmd(q,qlist,cmd,wd):
  task = (sp.Popen(['./run_mcell_job.py',wd], stdin=sp.PIPE), cmd)
  qlist.append(task)
  q.put(task)


if (__name__ == '__main__'):

  parser = ArgumentParser()
  parser.add_argument('--cpus', help='number of CPUs to use.  If omitted, use the number of hyperthreads available.')
  ns=parser.parse_args()

  notify = True

  q = Queue(maxsize=0)

  if ns.cpus:
    cpus = int(ns.cpus)
  else:
    cpus = multiprocessing.cpu_count()


  start_thread_workers(cpus,q,notify)


  cmds = []
  cmds.append('mcell3.2.1 -iterations 40000 -seed 1 Scene.main.mdl')
  cmds.append('mcell3.2.1 -iterations 40000 -seed 2 Scene.main.mdl')
  cmds.append('mcell3.2.1 -iterations 40000 -seed 3 Scene.main.mdl')
  cmds.append('mcell3.2.1 -iterations 40000 -seed 4 Scene.main.mdl')
  wd = './sim_runner_test_files/mcell'

  qlist = [(sp.Popen(['./run_mcell_job.py',wd], stdin=sp.PIPE), cmd) for cmd in cmds ]

  begin = time.time()

  [q.put(item) for item in qlist]

  time.sleep(10.)
  qlist[2][0].terminate()
  q.join()

  print('Took {0:0.2f} seconds.'.format(time.time() - begin))


