# interactive mandelbrot program
# copyright Tony Veijalainen, tony.veijalainen@gmail.com

from __future__ import print_function
import sys
import time

class kohn_bmp:
    '''py_kohn_bmp - Copyright 2007 by Michael Kohn
       http://www.mikekohn.net/
       mike@mikekohn.net'''

    def __init__(self, filename, width, height, depth):
        self.width = width
        self.height = height
        self.depth = depth
        self.xpos = 0

        self.width_bytes = width * depth
        if (self.width_bytes % 4) != 0:
            self.width_bytes = self.width_bytes + (4 - (self.width_bytes % 4))

        self.out=open(filename,"wb")
        self.out.write("BM")                    # magic number
        
        self.write_int(self.width_bytes * height + 54 + (1024 if depth==1 else 0))

        self.write_word(0)
        self.write_word(0)
        self.write_int(54 + (1024 if depth==1 else 0))
        self.write_int(40)                               # header_size
        self.write_int(width)                        # width
        self.write_int(height)                       # height
        self.write_word(1)                               # planes
        self.write_word(depth * 8)                   # bits per pixel
        self.write_int(0)                                # compression
        self.write_int(self.width_bytes * height * depth) # image_size
        self.write_int(0)                                # biXPelsperMetre
        self.write_int(0)                                # biYPelsperMetre

        if depth == 1:
            self.write_int(256)                          # colors used
            self.write_int(256)                          # colors important
            self.out.write(''.join(chr(c) * 3 + chr(0) for c in range(256)))
        else:
            self.write_int(0)                            # colors used - 0 since 24 bit
            self.write_int(0)                            # colors important - 0 since 24 bit

    def write_int(self, n):
        self.out.write('%c%c%c%c' % ((n&255),(n>>8)&255,(n>>16)&255,(n>>24)&255))

    def write_word(self, n):
        self.out.write('%c%c' % ((n&255),(n>>8)&255))

    def write_pixel_bw(self, y):
        self.out.write(chr(y))
        self.xpos = self.xpos + 1
        if self.xpos == self.width:
            while self.xpos < self.width_bytes:
                self.out.write(chr(0))
                self.xpos = self.xpos + 1
            self.xpos = 0

    def write_pixel(self, red, green, blue):
        self.out.write(chr((blue&255)))
        self.out.write(chr((green&255)))
        self.out.write(chr((red&255)))
        self.xpos = self.xpos+1
        if self.xpos == self.width:
            self.xpos = self.xpos * 3
            while self.xpos < self.width_bytes:
                self.out.write(chr(0))
                self.xpos = self.xpos + 1
            self.xpos = 0

    def close(self):
        self.out.close()

def mandel(real, imag, max_iterations=20):
    '''determines if a point is in the Mandelbrot set based on deciding if,
       after a maximum allowed number of iterations, the absolute value of
       the resulting number is greater or equal to 2.'''
    z_real, z_imag = 0.0, 0.0
    for i in range(0, max_iterations):
        z_real, z_imag = ( z_real*z_real - z_imag*z_imag + real,
                           2*z_real*z_imag + imag )
        if (z_real*z_real + z_imag*z_imag) >= 4:
            return i % max_iterations
    return -1

res = 0
res = mandel(1.0, 1.0, 128)
colors = [[0, 100, 100], [127, 0, 0], [127, 127, 0], [0, 127, 0], [0, 255, 0],
           [0, 255, 0], [0, 255, 127], [0, 127, 127], [255, 0, 0],
           [0, 127, 255], [0, 0, 255], [127, 0, 255],
           [127, 0, 255], [255, 0, 255], [255, 0, 127],
           [127, 127, 0], [0, 0, 0]]

# Changing the values below will change the resulting image
def mandel_file(cx=-0.7, cy=0.0, size=3.2, max_iterations=512, width = 640, height = 480):
    t0 = time.clock()
    try:
        increment = min(size / width, size / height)
        proportion = 1.0 * width / height
        start_real, start_imag = cx - increment * width/2, cy - increment * height/2

        mandel_pos = "%f %fi_%f_%i" % (cx, cy, size, max_iterations)
        fname = "m%s.bmp" % mandel_pos
        my_bmp = kohn_bmp(fname, width, height, 3)

        current_y = start_imag
        for y in range(height):
            if not y % 10:
                sys.stdout.write('\rrow %i / %i'  % (y + 1, height))
            sys.stdout.flush()
            current_x = start_real

            for x in range(width):
                c = mandel(current_x, current_y, max_iterations)
                c %= len(colors) 
                current_x += increment
                my_bmp.write_pixel(colors[c][0], colors[c][1], colors[c][2])
            current_y += increment

        print("\r%.3f s             " % (time.clock() - t0))
        my_bmp.close()
        return fname
    except IOError as e:
         print(e,'x %i, y %i, current_x %f, colors %s' %(x, y, current_x, colors))
        

if __name__ == '__main__':
    mandel_file(max_iterations=256)
