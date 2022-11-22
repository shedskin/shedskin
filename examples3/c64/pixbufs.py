#!/usr/bin/env python
# I, Danny Milosavljevic, hereby place this file into the public domain.

import array

WIDTH = 366 # 320
HEIGHT = 300 # 240

class Pixbuf(object):
    def __init__(self):
        self.native_pixbuf = 0
        self.data = WIDTH * HEIGHT * [0]
    def merge(self, index, scanline):
        """ index is the pixel index, not just the row index """
        offset = index
        for i in range(WIDTH):
            self.data[offset + i] = scanline[i]
    def get_rendered_image(self):
        #data = [(2**32+item) if item < 0 else item for item in self.data] if palette contains full alpha.
        #data = [item for item in self.data]
        return array.array('I', self.data).tostring()

if __name__ == "__main__":
    p = Pixbuf()
    p.merge(0, 366 * [0])
    p.get_rendered_image()
