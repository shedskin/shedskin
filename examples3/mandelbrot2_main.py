# interactive mandelbrot program
# copyright Tony Veijalainen, tony.veijalainen@gmail.com

try:
    import tkinter as tk
except ImportError:
    import tkinter as tk

import os
from PIL import Image, ImageTk

from mandelbrot2 import mandel_file

main_file = 'm-1 0i_3.5_240.bmp'
class MandelbrotTk(tk.Tk):
    def __init__(self, width=640, height=480, image_file=main_file):
        tk.Tk.__init__(self)
        self.canvas = tk.Canvas(width=width, height=height)
        self.geometry("%sx%s+100+100" % (width,height+40))
        self.canvas.pack()
        self.item = None
        
        self.label = tk.Label(self.canvas, font=('courier', 10))
        self.parameters_from_fn(image_file)
        if not os.path.isfile(image_file):
            self.image_file = mandel_file(self.cx, self.cy, self.fsize, self.max_iterations)
            print(('Mainfile %s generated' % self.image_file))
        else:
            self.image_file = image_file           
        self.label.pack(side=tk.BOTTOM)

        self.canvas.image = self.load_image()
        self.x, self.y, self.size = None, None, (0,)
        self.bind("<Button-2>", self.recalculate)
        # Linux
        self.bind("<Button-1>", self.zoom_in)
        self.bind("<Button-3>", self.zoom_out)
        # Windows
        self.bind("<MouseWheel>", self.mouse_wheel)

    def recalculate(self, event):
        print('recalculating')
        self.image_file = mandel_file(self.cx, self.cy, self.fsize, self.max_iterations)
        self.canvas.image = self.load_image()
        self.update_label()
        
    def parameters_from_fn(self, fn):
        # extract parameters from name
        ipos = fn.find('i')
        self.cx, self.cy = list(map(float, fn[1:ipos].split()))
        self.fsize, rest = fn[ipos+2:].split('_', 1)
        self.fsize = float(self.fsize)
        self.max_iterations = int(rest.split('.',1)[0])
        self.update_label()

    def load_image(self):   
        self.canvas.delete('m')
        photo = Image.open(self.image_file)
        im = ImageTk.PhotoImage(photo)
        self.canvas.create_image(0, 0, image=im, anchor='nw', tag='m')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.max_iterations = min(max(self.max_iterations, 256), 10000)
        self.update_label()
        self.step = self.fsize / max(im.width(), im.height())
        return im

    def update_label(self):
        self.label['text'] = ('cx: %g, cy: %g, fsize: %g, max_iterations: %i'  %
              (self.cx, self.cy, self.fsize, self.max_iterations))
        
    def zoom_in(self, event):
        print('ZOOM in')
        xshift, yshift = event.x - self.canvas.image.width() // 2, self.canvas.image.height() // 2 - event.y
        self.fsize /= 4.0
        self.cx, self.cy = xshift * self.step + self.cx, yshift * self.step + self.cy
        self.image_file = mandel_file(self.cx, self.cy, self.fsize, self.max_iterations)
        self.canvas.image = self.load_image()

    def zoom_out(self, event):
        print('zoom out')
        xshift, yshift = event.x - self.canvas.image.width() // 2, self.canvas.image.height() // 2 - event.y
        self.fsize *= 4.0
        self.cx, self.cy =  xshift * self.step + self.cx, yshift * self.step + self.cy
        self.image_file = mandel_file(self.cx, self.cy, self.fsize, self.max_iterations)
        self.canvas.image = self.load_image()

    def mouse_wheel(self, event):
        """respond to Linux or Windows wheel event"""
        if event.num == 5 or event.delta == -120:
            self.max_iterations -= 120
        if event.num == 4 or event.delta == 120:
            self.max_iterations += 120
        self.update_label()

if __name__ == '__main__':
    mand = MandelbrotTk()
    mand.mainloop()
