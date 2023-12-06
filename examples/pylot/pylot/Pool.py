# Copyright 2010 Eric Uhrhane.
#
# This file is part of Pylot.
#
# Pylot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pylot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.import math

from queue import Empty
from threading import Thread
import queue
import multiprocessing


class Quit(object):
  pass

class ThreadedQueueProcessor(object):
  def __init__(self, handler, count=1, use_processes=False):
    self.tasks = []
    self.taskKillers = []
    if use_processes:
      queueClass = multiprocessing.Queue
    else:
      queueClass = queue.Queue
    self.inputQ = queueClass()
    self.outputQ = queueClass()
    for i in range(count):
      quitQ = queueClass()
      self.taskKillers.append(quitQ)
      if use_processes:
        t = multiprocessing.Process(target=ProcessFunc,
                                    args=(self.inputQ, self.outputQ, quitQ,
                                          handler))
      else:
        t = QueueTask(self.inputQ, self.outputQ, quitQ, handler)
      print("Created task %d" % i)
      self.tasks.append(t)
      t.start()

  def clear(self):
    input = []
    while not self.inputQ.empty():
      try:
        item = self.inputQ.get_nowait()
        input.append(item)
      except Empty:
        pass
    return input

  def terminate(self):
    # This kills any task that's just finished processing a job, before it
    # checks for a new one.
    for q in self.taskKillers:
      q.put(True)
    # This kills tasks blocked on an otherwise-empty task queue.
    for i in range(len(self.tasks)):
      self.inputQ.put(Quit())
    i = 0
    for t in self.tasks:
      t.join()
      i = i + 1
      print("%d task%s joined." % (i, "s" if i > 1 else ""))

  def put(self, job):
    self.inputQ.put(job)

  def get(self, *args):
    try:
      job = self.outputQ.get(*args)
    except Empty:
      job = None
    return job

# This is the main function of a task when using multiprocessing.
def ProcessFunc(inputQ, outputQ, quitQ, handler):
  while True:
    try:
      try:
        quitQ.get(False)
        return
      except Empty:
        job = inputQ.get()
        if type(job) == Quit:
          return
    except KeyboardInterrupt:
      return
    temp = handler.handle(job)
#    print "Before" # FIXME: These two print statements make the queue behave.
    outputQ.put(temp)
#    print "After"  # FIXME: Without them, it gets backed up for some reason.

# This is the thread class for when running in threaded [single-process] mode.
class QueueTask(Thread):
  def __init__(self, inputQ, outputQ, quitQ, handler):
    Thread.__init__(self)
    self.inputQ = inputQ
    self.outputQ = outputQ
    self.quitQ = quitQ
    self.handler = handler

  def run(self):
    while True:
      try:
        self.quitQ.get(False)
        return
      except Empty:
        pass
      job = self.inputQ.get()
      if type(job) == Quit:
        return
      self.outputQ.put(self.handler.handle(job))
