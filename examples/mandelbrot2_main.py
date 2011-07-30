# interactive mandelbrot program
# copyright Tony Veijalainen, tony.veijalainen@gmail.com

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import os
from PIL import Image, ImageTk

from mandelbrot2 import mandel_file

class MandelbrotTk(tk.Tk):
    def __init__(self, width=640, height=480, image_file='m-1.000000 0.000000i_3.500000_240.bmp'):
        tk.Tk.__init__(self)
        self.canvas = tk.Canvas(width=width, height=height)
        self.geometry("%sx%s+100+100" % (width,height+40))
        self.canvas.pack()
        self.item = None
        self.label = tk.Label(self.canvas, font=('courier', 16, 'bold'), 
            width=10)
        self.label.pack(side=tk.BOTTOM)
        self.cx = None
        self.image_file = image_file
        self.canvas.image = self.load_image()
        self.x, self.y, self.size = None, None, (0,)
        # Linux
        self.bind("<Button-1>", self.zoom_in)
        self.bind("<Button-3>", self.zoom_out)
        # Windows
        self.bind("<MouseWheel>", self.mouse_wheel)
  
        
    def load_image(self):   
        self.canvas.delete('m')
        photo = Image.open(self.image_file)
        im = ImageTk.PhotoImage(photo)
        self.canvas.create_image(0, 0, image=im, anchor='nw', tag='m')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        if self.cx is None:
            # extract parameters from name
            ipos = self.image_file.find('i')
            self.cx, self.cy = map(float, self.image_file[1:ipos].split())
            self.fsize, rest = self.image_file[ipos+2:].split('_', 1)
            self.fsize = float(self.fsize)
            self.max_iterations = int(rest.split('.',1)[0])

        self.max_iterations = min(max(self.max_iterations, 256), 10000)
        self.label['text'] = self.max_iterations
        self.step = self.fsize / max(im.width(), im.height())
        print('cx: %f, cy: %f, fsize: %f, max_iterations: %i, step: %f'  %
              (self.cx, self.cy, self.fsize, self.max_iterations, self.step))
        return im

    def zoom_in(self, event):
        print('ZOOM in')
        xshift, yshift = event.x - self.canvas.image.width() // 2, self.canvas.image.height() // 2 - event.y
        print('Click at %i, %i, xshift %i, yshift %i' % (event.x, event.y, xshift, yshift))

        self.fsize /= 4.0
        self.cx, self.cy = xshift * self.step + self.cx, yshift * self.step + self.cy
        self.image_file = mandel_file(self.cx, self.cy, self.fsize, self.max_iterations)
        self.canvas.image = self.load_image()

    def zoom_out(self, event):
        print('zoom out')
        xshift, yshift = event.x - self.canvas.image.width() // 2, self.canvas.image.height() // 2 - event.y
        print('Click at %i, %i, xshift %i, yshift %i' % (event.x, event.y, xshift, yshift))
        self.fsize *= 4.0
        self.cx, self.cy =  xshift * self.step + self.cx, yshift * self.step + self.cy
        self.image_file = mandel_file(self.cx, self.cy, self.fsize, self.max_iterations)
        self.canvas.image = self.load_image()

    def mouse_wheel(self, event):
        """respond to Linux or Windows wheel event"""
        print('Mousewheel event.num %s, ent.delta %s' % (event.num, event.delta))
        if event.num == 5 or event.delta == -120:
            self.max_iterations -= 120
        if event.num == 4 or event.delta == 120:
            self.max_iterations += 120
        self.label['text'] = self.max_iterations

if __name__ == '__main__':
    if not os.path.isfile('m-1.000000 0.000000i_3.500000_240.bmp'):
        mandel_file(-1.000000, 0.000000, 3.500000, 240)
    mand = MandelbrotTk()
    mand.mainloop()
