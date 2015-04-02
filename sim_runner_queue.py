#!/usr/bin/env python3

import sys
from queue import Queue
from threading import Thread
import subprocess as sp

class SimQueue:
  def __init__(self):
    self.q = Queue(maxsize=0)
    self.workers = []
    self.task_dict = {}
    self.n_threads = 0
    self.python_exec = 'python'
    self.run_wrapper = './run_wrapper.py'
    self.notify = False

  def start(self,n_threads):
    if n_threads > self.n_threads:
      for i in range(n_threads - self.n_threads):
        worker = Thread(target=self.run_q_item)
        worker.daemon = True
        worker.start()
        self.workers.append(worker)
      self.n_threads = n_threads

  def run_q_item(self):
    while True:
      task = self.q.get()
      process = task['process']
      cmd = task['cmd']
      res = process.communicate('{0}'.format(cmd).encode())
      self.task_dict[process.pid]['stdout'] = res[0]
      self.task_dict[process.pid]['stderr'] = res[1]
      if self.notify:
          sys.stdout.write('{0} {1}\n'.format(process.pid, cmd))
          sys.stdout.write(res[0].decode())
          sys.stdout.write(res[1].decode())
      self.q.task_done()

  def add_task(self,cmd,wd):
    process = sp.Popen([self.python_exec, self.run_wrapper, wd], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    pid = process.pid
    self.task_dict[pid] = {}
    self.task_dict[pid]['process'] = process
    self.task_dict[pid]['cmd'] = cmd
    self.task_dict[pid]['stdout'] = b''
    self.task_dict[pid]['stderr'] = b''
    self.q.put(self.task_dict[pid])
    return process

  def clear_task(self,pid):
    if self.task_dict.get(pid):
      self.task_dict.pop(pid)

#  def stop(self):



if (__name__ == '__main__'):
  import multiprocessing
  from argparse import ArgumentParser
  import time

  parser = ArgumentParser()
  parser.add_argument('--cpus', help='number of CPUs to use.  If omitted, use the number of hyperthreads available.')
  ns=parser.parse_args()

  my_q = SimQueue()

  if ns.cpus:
    cpus = int(ns.cpus)
  else:
    cpus = multiprocessing.cpu_count()

  my_q.start(cpus)

  begin = time.time()

  wd = './sim_runner_test_files/mcell'
  my_q.add_task('"mcell3.2.1 -iterations 5000 -seed 1 Scene.main.mdl"',wd)
  my_q.add_task('"mcell3.2.1 -iterations 5000 -seed 2 Scene.main.mdl"',wd)
  my_q.add_task('"mcell3.2.1 -iterations 5000 -seed 3 Scene.main.mdl"',wd)
  my_q.add_task('"mcell3.2.1 -iterations 5000 -seed 4 Scene.main.mdl"',wd)

  time.sleep(5.)

  pids = list(my_q.task_dict.keys())
  pids.sort()
  a_pid = pids[2]
  my_q.task_dict[a_pid]['process'].terminate()

  my_q.q.join()

#  time.sleep(0.5)

  sys.stdout.write(my_q.task_dict[a_pid]['stdout'].decode())
  sys.stdout.write(my_q.task_dict[a_pid]['stderr'].decode())

  sys.stdout.write('\n\nTook {0:0.2f} seconds.\n\n'.format(time.time() - begin))


