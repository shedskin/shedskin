#!/usr/bin/env python2
# Original author Mariano Lambir. https://github.com/mlambir/Pygame-FPS
# Modified by Ernesto Ferro and Mark Dufour to work with Shed Skin Python-to-C++ compiler by Mark Dufour
# Shed Skin homepage: http://mark.dufour.googlepages.com


import pygtk
pygtk.require("2.0")
import gtk
import gobject
import sys
import time

from Gh0stenstein import world_manager

WIDTH, HEIGHT = 1024, 768

worldMap = [
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 4, 4, 6, 4, 4, 6, 4, 6, 4, 4, 4, 6, 4],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    [8, 0, 3, 3, 0, 0, 0, 0, 0, 8, 8, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [8, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [8, 0, 3, 3, 0, 0, 0, 0, 0, 8, 8, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 4, 0, 0, 0, 0, 0, 6, 6, 6, 0, 6, 4, 6],
    [8, 8, 8, 8, 0, 8, 8, 8, 8, 8, 8, 4, 4, 4, 4, 4, 4, 6, 0, 0, 0, 0, 0, 6],
    [7, 7, 7, 7, 0, 7, 7, 7, 7, 0, 8, 0, 8, 0, 8, 0, 8, 4, 0, 4, 0, 6, 0, 6],
    [7, 7, 0, 0, 0, 0, 0, 0, 7, 8, 0, 8, 0, 8, 0, 8, 8, 6, 0, 0, 0, 0, 0, 6],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 6, 0, 0, 0, 0, 0, 4],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 6, 0, 6, 0, 6, 0, 6],
    [7, 7, 0, 0, 0, 0, 0, 0, 7, 8, 0, 8, 0, 8, 0, 8, 8, 6, 4, 6, 0, 6, 6, 6],
    [7, 7, 7, 7, 0, 7, 7, 7, 7, 8, 8, 4, 0, 6, 8, 4, 8, 3, 3, 3, 0, 3, 3, 3],
    [2, 2, 2, 2, 0, 2, 2, 2, 2, 4, 6, 4, 0, 0, 6, 0, 6, 3, 0, 0, 0, 0, 0, 3],
    [2, 2, 0, 0, 0, 0, 0, 2, 2, 4, 0, 0, 0, 0, 0, 0, 4, 3, 0, 0, 0, 0, 0, 3],
    [2, 0, 0, 0, 0, 0, 0, 0, 2, 4, 0, 0, 0, 0, 0, 0, 4, 3, 0, 0, 0, 0, 0, 3],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4, 4, 4, 6, 0, 6, 3, 3, 0, 0, 0, 3, 3],
    [2, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1, 2, 2, 2, 6, 6, 0, 0, 5, 0, 5, 0, 5],
    [2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 5, 0, 5, 0, 0, 0, 5, 5],
    [2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 5, 0, 5, 0, 5, 0, 5, 0, 5],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
    [2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 5, 0, 5, 0, 5, 0, 5, 0, 5],
    [2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0, 5, 0, 5, 0, 0, 0, 5, 5],
    [2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 5, 5, 5, 5, 5, 5, 5, 5, 5]
]

sprite_positions = [
    (20.5, 11.5, 11),  # green light in front of playerstart
    # green lights in every room
    (18.5, 4.5, 11),
    (10.0, 4.5, 11),
    (10.0, 12.5, 11),
    (3.5, 6.5, 11),
    (3.5, 20.5, 11),
    (3.5, 14.5, 11),
    (14.5, 20.5, 11),

    # row of pillars in front of wall: fisheye test
    (18.5, 10.5, 10),
    (18.5, 11.5, 10),
    (18.5, 12.5, 10),

    # some barrels around the map
    (21.5, 1.5, 9),
    (15.5, 1.5, 9),
    (16.0, 1.8, 9),
    (16.2, 1.2, 9),
    (3.5,  2.5, 9),
    (9.5, 15.5, 9),
    (10.0, 15.1, 9),
    (10.5, 15.8, 9),
]


class EventBox(gtk.EventBox):
    def __init__(self, view):
        gtk.EventBox.__init__(self)
        self.view = view
        self.props.can_focus = True
        self.pressed = {}
        self.connect("key-press-event", self.handle_key_press)
        self.connect("key-release-event", self.handle_key_release)

    def handle_key_press(self, widget, event):
        keyval = gtk.gdk.keyval_name(event.keyval)
        if keyval == 'q':
            sys.exit()
        self.pressed[keyval] = True

    def handle_key_release(self, widget, event):
        self.pressed[gtk.gdk.keyval_name(event.keyval)] = False


class View(object):
    def __init__(self):
        self.wm = world_manager.WorldManager(WIDTH, HEIGHT, worldMap, sprite_positions, 22, 11.5, -1, 0, 0, .66)
        self.frame_time = 0.0

        load_image(self.wm, 0, 'Gh0stenstein/pics/background.png', WIDTH, HEIGHT)

        load_image(self.wm, 1, 'Gh0stenstein/pics/walls/eagle.png', 64, 64)
        load_image(self.wm, 2, 'Gh0stenstein/pics/walls/redbrick.png', 64, 64)
        load_image(self.wm, 3, 'Gh0stenstein/pics/walls/purplestone.png', 64, 64)
        load_image(self.wm, 4, 'Gh0stenstein/pics/walls/greystone.png', 64, 64)
        load_image(self.wm, 5, 'Gh0stenstein/pics/walls/bluestone.png', 64, 64)
        load_image(self.wm, 6, 'Gh0stenstein/pics/walls/mossy.png', 64, 64)
        load_image(self.wm, 7, 'Gh0stenstein/pics/walls/wood.png', 64, 64)
        load_image(self.wm, 8, 'Gh0stenstein/pics/walls/colorstone.png', 64, 64)

        load_image(self.wm, 9, 'Gh0stenstein/pics/items/GoldBar.png', 64, 64)
        load_image(self.wm, 10, 'Gh0stenstein/pics/items/PlantInPot.png', 64, 64)
        load_image(self.wm, 11, 'Gh0stenstein/pics/items/BlueOverheadLight.png', 64, 64)

        self.window = gtk.Window()
        self.event_box = EventBox(self)
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.connect("realize", self.allocate_GC)
        self.drawing_area.connect("expose-event", self.repaint_X)
        self.drawing_area.set_size_request(WIDTH, HEIGHT)
        self.drawing_area.show()
        self.event_box.show()
        gobject.timeout_add(16, self.repaint_T)
        box = gtk.HBox()
        self.event_box.add(self.drawing_area)
        box.pack_start(self.event_box, False, False)
        box.show()
        self.window.add(box)
        self.window.show_all()
        self.times = 0
        self.t0 = 0

    def allocate_GC(self, widget, *args, **kwargs):
        self.GC = widget.window.new_gc()

    def repaint_X(self, widget, event):
        self.repaint()

    def repaint_T(self):
        self.repaint()
        return(True)

    def repaint(self):
        for key, val in self.event_box.pressed.items():
            if val:
                move_speed = self.frame_time * 6.0  # the constant value is in squares / second
                rot_speed = self.frame_time * 2.0
                self.wm.move(key, move_speed, rot_speed)
        t0 = time.time()
        self.wm.draw()
        s = self.wm.dump()
        self.pixbuf = gtk.gdk.pixbuf_new_from_data(s, gtk.gdk.COLORSPACE_RGB, True, 8, WIDTH, HEIGHT, WIDTH * 4)  # TODO optimize!!
        widget = self.drawing_area
        if widget.window:  # window already realized
            widget.window.draw_pixbuf(self.GC, self.pixbuf, 0, 0, 0, 0, WIDTH, HEIGHT, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        self.frame_time = time.time() - t0
        self.times += 1
        if self.times == 10:
            print 'FPS: %.2f' % (1 / ((time.time() - self.t0) / 10))
            self.times = 0
            self.t0 = time.time()


def load_image(wm, pos, filename, w, h):
    pb = gtk.gdk.pixbuf_new_from_file(filename)
    pb = pb.scale_simple(w, h, gtk.gdk.INTERP_NEAREST)
    pixels = pb.get_pixels_array().tolist()
    data = [0 for i in range(w * h)]
    for x in range(w):
        for y in range(h):
            data[w * y + x] = pixels[y][x]
    wm.load_image(pos, data, w, h)


def main():
    View()
    gtk.main()


if __name__ == '__main__':
    main()
