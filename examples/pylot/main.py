#!/usr/bin/python

#TODO:
#   Softer lighting, by supersampling light sources
#   Texture/bump/normal mapping.  Mipmaps for the textures, at least.
#   Hierarchies with transforms--probably should wait until we see what a real
#     file format looks like.
#   Bounding boxes for hierarchies and complex shapes

from Tkinter import *
import Image
import ImageTk
import ImageDraw
import random
import struct
import time
import SimpleGeometry
print 'using', SimpleGeometry.__file__
from Pool import ThreadedQueueProcessor

class CameraHandler(object):
  def __init__(self, camera):
#    assert type(camera) == Camera
    self.camera = camera
    
  def handle(self, job):
    realJob, debugFlag = job
#    set_debug(debugFlag)
    return self.camera.runPixelRange(realJob)

class App(object):
  def __init__(self, root, viewports):
    self.root = root
    self.viewports = viewports
    self.topButtonFrame = Frame(root)
    self.topButtonFrame.pack(side=TOP)
    self.botButtonFrame = Frame(root)
    self.botButtonFrame.pack(side=BOTTOM)
    self.button = Button(self.topButtonFrame, text="Quit",
                         command=self.shutdown)
    self.button.pack(side=LEFT)

    self.button = Button(self.topButtonFrame, text="Save", command=self.save)
    self.button.pack(side=LEFT)

    self.button = Button(self.botButtonFrame, text="Process",
                         command=self.process)
    self.button.pack(side=LEFT)

    self.button = Button(self.botButtonFrame, text="Stop", command=self.stop)
    self.button.pack(side=LEFT)
    self.labels = []
    for v in viewports:
      label = Label(root)
      self.labels.append(label)
      label.pack(side=LEFT)
      def clickHandler(v):
        return lambda event: v.handleClick(event)
      label.bind("<Button-1>", clickHandler(v))
      v.setLabel(label)
      v.setApp(self)
    root.bind("<Destroy>", lambda x : self.shutdown())

  def process(self):
    for v in self.viewports:
      v.process()

  def processSingleThreaded(self):
    for v in self.viewports:
      v.processSingleThreaded()

  def stop(self):
    for v in self.viewports:
      v.stop()

  def shutdown(self):
    if self.viewports:
      for v in self.viewports:
        v.shutdown()
      self.viewports = None
      self.root.quit()
      self.root.update()

  def save(self):
    for i in range(len(self.viewports)):
      self.viewports[i].save("test%d.png" % i)

  def drawDebugRays(self, debug_rays):
    for v in self.viewports:
      v.drawDebugRays(debug_rays)

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

  def debugPixel(self, x, y):
    if not self.processor:
      self.initProcessor()
    print "Processing pixel: ", x, ", ", y
    d = get_debug()
#    set_debug(True)
    block = self.camera.runPixelRange( ((x, x+1), (y, y+1)) )
    for (i, j), c in block:
      self.draw.point((i, j), c)
    self.refreshImage()
    print "Calling get_debug_rays"
    debug_rays = get_debug_rays();
    self.app.drawDebugRays(debug_rays)
    print "Calling clear_debug_rays"
#    set_debug(False)
    clear_debug_rays()

  def handleClick(self, event):
    if self.count and not self.jobs:
      self.stop()
    self.debugPixel(event.x, event.y)

  def getBlock(self, i, j, BLOCKS_WIDE, BLOCKS_TALL):
    cols = self.camera.cols
    rows = self.camera.rows
    return ((int(float(cols) / BLOCKS_WIDE * i),
             int(float(cols) / BLOCKS_WIDE * (i + 1))),
            (int(float(rows) / BLOCKS_TALL * j),
             int(float(rows) / BLOCKS_TALL * (j + 1))))

  def initProcessor(self):
    self.processor = ThreadedQueueProcessor(CameraHandler(self.camera), 9,
                                            use_processes=True)
    self.memo = []
    self.starttime = time.time()
    self.done = 0

  def process(self):
    self.start_time = time.time()
    try:
      jobs = []
      if self.jobs:
        jobs = self.jobs
        self.jobs = None
      elif not self.count:
        if not self.processor:
          self.initProcessor()
        BLOCKS_WIDE = 10
        BLOCKS_TALL = 10
        jobs = []
        for i in range(BLOCKS_WIDE):
          for j in range(BLOCKS_TALL):
            jobs.append((self.getBlock(i, j, BLOCKS_WIDE, BLOCKS_TALL), False))
        random.shuffle(jobs)
        self.count = BLOCKS_WIDE * BLOCKS_TALL
      for j in jobs:
        self.processor.put(j)
      if jobs:
        self.app.root.after(250, self.checkQueue)
    except:
      if self.processor:
        self.processor.terminate()
      raise

  def processSingleThreaded(self):
    self.image = Image.new("RGBA", (self.camera.cols, self.camera.rows))
    self.draw = ImageDraw.Draw(self.image)
    self.draw.rectangle(((0, 0), (self.camera.cols, self.camera.rows)),
                        fill="grey")
    pixels = self.camera.runImage()
    for (i, j), c in pixels:
      self.draw.point((i, j), c)
    self.refreshImage()

  def stop(self):
    if not self.jobs:
      self.jobs = self.processor.clear()

  def refreshImage(self):
    self.imageTk = ImageTk.PhotoImage(self.image)
    self.label.config(image=self.imageTk)

  def checkQueue(self):
    if self.processor:
        block = self.processor.get(False)
        while block:
          ((startCol, endCol), (startRow, endRow)), colors = block
          w,h = (endCol-startCol), (endRow-startRow)
          ork = [struct.pack('BBB', int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)) for c in colors]
          image1 = Image.fromstring('RGB', (w, h), ''.join(ork))
          tkpi = ImageTk.PhotoImage(image1)
          self.memo.append(tkpi)
          label_image = Label(self.app.root, image=tkpi)
          label_image.place(x=startCol, y=startRow+50,width=w, height=h)
          self.done += 1
          if self.done == 100:
              print 'time: %.2f' % (time.time()-self.start_time)
          block = self.processor.get(False)
        self.app.root.after(250, self.checkQueue)

  def drawDebugRays(self, debug_rays):
    for ray, color in debug_rays:
      origin = self.camera.mapPointToScreen(ray.origin)
      if not origin:
        print ("Whoa!  Could not map origin!")
        continue
      offset = self.camera.mapPointToScreen(ray.origin + ray.offset)
      if not offset:
        print ("Whoa!  Got a bad offset!")
        continue
      self.draw.line([origin, offset], color)
    self.refreshImage()

  def drawShapeCenters(self, color):
    if not self.image:
      self.image = Image.new("RGBA", (self.camera.cols, self.camera.rows))
      self.draw = ImageDraw.Draw(self.image)
      self.draw.rectangle(((0, 0), (self.camera.cols, self.camera.rows)),
                          fill="black")
    for shape in world.shapes:
      pixel = self.camera.mapPointToScreen(shape.getLocation())
      if pixel:
        self.draw.point(pixel, color)
    self.refreshImage()

  def save(self, name):
    self.image.save(name)

root = Tk()
root.title("Pylot")

geometry = SimpleGeometry.getGeometry()
world = SimpleGeometry.getWorld(geometry)
cameras = [SimpleGeometry.getCamera(world), SimpleGeometry.getCamera2(world)]
#cameras = [getCamera(world)]
viewports = [Viewport(c) for c in cameras[:1]]
app = App(root, viewports)

single_threaded = False
if single_threaded:
  app.processSingleThreaded()
else:
#  app.viewports[0].debugPixel(93, 155)
  app.process()

try:
  root.mainloop()
except KeyboardInterrupt:
  app.shutdown()
