#!/usr/bin/python

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

import random
import time

import pygame



from tkinter import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk
import pylot
from pylot.Pool import ThreadedQueueProcessor
from pylot.Utils import *
from pylot import SimpleGeometry
print(SimpleGeometry.__file__)

WIDTH = 320
BLOCKS_WIDE = 20
BLOCKS_TALL = 20


class CameraHandler(object):
  def __init__(self, camera):
    self.camera = camera

  def handle(self, job):
    realJob, debugFlag = job
    set_debug(debugFlag)
    return self.camera.runPixelRange(realJob)

QUEUE_CHECK_TIME = 250 # ms
class App(object):
  def __init__(self, root, viewports):
    self.root = root
    self.viewports = viewports
    self.labels = []
    for v in viewports:
      label = Label(root)
      self.labels.append(label)
      label.pack(side=LEFT)
      v.setLabel(label)
      v.setApp(self)
    root.bind("<Destroy>", lambda x : self.shutdown())

  def process(self):
    for v in self.viewports:
      v.process()

  def shutdown(self):
    for v in self.viewports:
      v.shutdown()
    self.viewports = []
    self.root.quit()
    self.root.update()


class Viewport(object):
  def __init__(self, camera):
    self.processor = None
    self.camera = camera
    self.jobs = None
    self.image = None
    self.label = None
    self.app = None
    self.count = 0

  def setLabel(self, label):
    assert not self.label
    self.label = label

  def setApp(self, app):
    assert not self.app
    self.app = app

  def shutdown(self):
    if self.processor:
      self.processor.terminate()
      self.processor = None

  def getBlock(self, i, j, BLOCKS_WIDE, BLOCKS_TALL):
    cols = self.camera.cols
    rows = self.camera.rows
    return ((int(float(cols) / BLOCKS_WIDE * i),
             int(float(cols) / BLOCKS_WIDE * (i + 1))),
            (int(float(rows) / BLOCKS_TALL * j),
             int(float(rows) / BLOCKS_TALL * (j + 1))))

  def initProcessor(self):
    self.processor = ThreadedQueueProcessor(CameraHandler(self.camera), 8,
                                            use_processes=True)
    self.image = Image.new("RGBA", (self.camera.cols, self.camera.rows))
    self.draw = ImageDraw.Draw(self.image)

  def process(self):
    try:
      jobs = []
      if self.jobs:
        jobs = self.jobs
        self.jobs = None
      elif not self.count:
        self.startTime = time.time()
        if not self.processor:
          self.initProcessor()
        else:
          self.draw.rectangle(((0, 0), (self.camera.cols, self.camera.rows)),
                              fill="grey")
        jobs = []
        for i in range(BLOCKS_WIDE):
          for j in range(BLOCKS_TALL):
            jobs.append((self.getBlock(i, j, BLOCKS_WIDE, BLOCKS_TALL), False))
        random.shuffle(jobs)
        self.count = BLOCKS_WIDE * BLOCKS_TALL
      for j in jobs:
        self.processor.put(j)
      if jobs:
        self.app.root.after(QUEUE_CHECK_TIME, self.checkQueue)
    except:
      if self.processor:
        self.processor.terminate()
      raise

  def imageFromBlock(self, r, pixels):
    (x, xMax), (y, yMax) = r
    w = xMax - x
    h = yMax - y
    return Image.frombytes('RGB', (w, h), pixels)

  def refreshImage(self):
    self.imageTk = ImageTk.PhotoImage(self.image)
    self.label.config(image=self.imageTk)

  def checkQueue(self):
    gotData = False
    if self.processor:
      block = self.processor.get(False)
      while block:
        gotData = True
        self.count -= 1
        assert self.count >= 0
        r, pixels = block
        image_temp = self.imageFromBlock(r, pixels)
        (x, _), (y, _) = r
        self.image.paste(image_temp, (x, y))
        block = self.processor.get(False)
      if gotData:
        self.refreshImage()
        if not self.count:
          print("That took %.3f seconds." % (time.time() - self.startTime))
      self.app.root.after(QUEUE_CHECK_TIME, self.checkQueue)


root = Tk()
root.title("Pylot")

geometry = SimpleGeometry.getGeometry(size=WIDTH, which=2)
world = SimpleGeometry.getWorld(geometry)
cameras = [SimpleGeometry.getCamera(world)] #,
viewports = [Viewport(c) for c in cameras]
app = App(root, viewports)

try:
    app.process()
    root.mainloop()
finally:
    app.shutdown()
