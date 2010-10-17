#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import pygtk
pygtk.require("2.0")
import gtk
import gobject
from c64 import C64
import timer

# TODO 3 bit row counter.

WIDTH = 366
HEIGHT = 300

class EventBox(gtk.EventBox):
    def __init__(self, controls):
        gtk.EventBox.__init__(self)
#       self.controls = controls
        self.props.can_focus = True
        #self.pressed_keys = set()
        self.connect("key-press-event", self.handle_key_press)
        self.connect("key-release-event", self.handle_key_release)

    def handle_key_press(self, widget, event):
                pass
#       return self.controls.handle_key_press(event.keyval)

    def handle_key_release(self, widget, event):
        # hardware_keycode
                pass
        #return self.controls.handle_key_release(event.keyval)
        #self.pressed_keys.discard(event.keycode)

class GTextView(timer.Timer):
    def __init__(self, controls):
        self.colors = [
            gtk.gdk.Color(red = 0, green = 0, blue = 0),
            gtk.gdk.Color(red = 65535, green = 65535, blue = 65535),
            gtk.gdk.Color(red = 115.505637 / 255, green = 66.5865 / 255, blue = 53.281385 / 255),
            gtk.gdk.Color(red = 123.556863 / 255, green = 172.47599981 / 255, blue = 185.7811146 / 255.0),
            gtk.gdk.Color(red = 123.039015 / 255.0, green = 72.130708003 / 255.0, blue = 144.4171376 / 255.0),
            gtk.gdk.Color(red = 100.085985 / 255, green = 150.9942919966 / 255, blue = 78.70786237 / 255),
            gtk.gdk.Color(red = 63.75 / 255, green = 50.282779 / 255, blue = 132.75250 / 255),
            gtk.gdk.Color(red = 191.25 / 255, green = 204.717220846 / 255, blue = 122.24749723 / 255),
            gtk.gdk.Color(red = 123.039015226 / 255, green = 91.17623437 / 255, blue = 46.832862373 / 255),
            gtk.gdk.Color(red = 78.586358 / 255, green = 68.63075 / 255, blue = 0.0),
            gtk.gdk.Color(red = 163.318137 / 255, green = 114.399 / 255, blue = 101.0938853987 / 255),
            gtk.gdk.Color(red = 79.6875 / 255, green = 79.6875 / 255, blue = 79.6875 / 255),
            gtk.gdk.Color(red = 119.53125 / 255, green = 119.53125 / 255, blue = 119.53125 / 255),
            gtk.gdk.Color(red = 163.83598477 / 255, green = 214.74429 / 255, blue = 142.45786 / 255),
            gtk.gdk.Color(red = 119.53125 / 255, green = 106.064029 / 255, blue = 188.53375 / 255),
            gtk.gdk.Color(red = 159.375 / 255, green = 159.375 / 255, blue = 159.375 / 255),
        ]
        self.pixmap = None
        self.window = gtk.Window()
        self.event_box = EventBox(controls)
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.connect("expose-event", self.repaint_X)
        self.window.connect("realize", self.allocate_pixmap)
        self.drawing_area.set_size_request(WIDTH, HEIGHT) # FIXME make configurable.
        self.drawing_area.show()
        self.event_box.show()
        gobject.timeout_add(440, self.repaint_T)
        box = gtk.HBox()
        self.event_box.add(self.drawing_area)
        box.pack_start(self.event_box, False, False)
#       box.pack_start(controls, False, False)
        box.show()
        self.window.add(box)
        self.window.show()
        self.count = 0

    def repaint_X(self, widget, event):
        return self.repaint()

    def repaint_T(self):
        return self.repaint()

    def allocate_pixmap(self, *args, **kwargs):
        self.pixmap = gtk.gdk.Pixmap(self.window.window, WIDTH, HEIGHT) #.connect("realize", self.use_pixmap)
        self.colors = [self.pixmap.get_colormap().alloc_color(color) for color in self.colors]

    def repaint(self):
        widget = self.drawing_area
        if self.pixmap is None:
            print("WHOOPS")
            return
        self.repaint_pixmap()
        GC = widget.window.new_gc()
        widget.window.draw_drawable(GC, self.pixmap, 0, 0, 0, 0, -1, -1)

    def repaint_pixmap(self):
        window = self.pixmap
        GC = window.new_gc()
        #print("=========== REPAINT ========")
        #print(dir(self))
        size = window.get_size()
        color = self.colors[self.tv.border_color]
        #color = gtk.gdk.Color(red = 123.039015) # * 65535.0 / 255.0, green = 72.130708003 * 65535.0 / 255.0, blue = 144.4171376 * 65535.0 / 255.0)
        #print color.red, color.green, color.blue, self.border_color, "XX"
        GC.set_foreground(self.colors[self.tv.border_color])
        GC.set_fill(gtk.gdk.SOLID)
        #GC.set_background(self.colors[self.border_color])
        window.draw_rectangle(GC, True, 0, 0, size[0], size[1]) # TODO only draw border around it.
        GC.set_foreground(self.colors[self.tv.background_color_0])
        window.draw_rectangle(GC, True, self.tv.first_column, self.tv.first_row, self.tv.last_column - self.tv.first_column + 1, self.tv.last_row - self.tv.first_row + 1)

        # FIXME support other modes.
        if self.tv.old_VIC_bank != self.tv.VIC_bank:
            self.tv.old_VIC_bank = self.tv.VIC_bank
            self.tv.prepare_characters()

        VIC = self.tv.VIC
        offset = self.tv.video_offset
        VX = self.tv.first_column - self.tv.viewport_column
        VY = self.tv.first_row - self.tv.viewport_row
        for row in range(24): # FIXME 25
            for column in range(40): # FIXME configurable
                code_color = VIC.VIC_read_memory(offset, 1)
                code = code_color & 255
                color = code_color >> 8
                pixmap = self.tv.characters[code] if code < 128 else self.tv.inverse_characters[code] # TODO inverse.
                if (color if code < 128 else self.tv.background_color_0) >= len(self.colors):
                    print("WHOOPS, code", code, "color", color)
                GC.set_foreground(self.colors[color if code < 128 else self.tv.background_color_0]) # FIXME
                GC.set_clip_mask(pixmap)
                GC.set_clip_origin(VX + column * 8, VY + row * 8)
                window.draw_rectangle(GC, True, VX + column * 8, VY + row * 8, 8, 8)
                #window.draw_pixbuf(GC, pixbuf, 0, 0, VX + column * 8, VY + row * 8)
                offset += 1

    def fire_timer(self):
        self.c64.fire()
        self.count += 1
        if self.count % 1000 == 0:
            print 'REPAINT', self.count
            self.c64.VIC.repaint()
            self.repaint()
        return True

if __name__ == '__main__':
    gt = GTextView({})
    c64 = C64(gt)
    gt.c64 = c64
    c64.CPU_clock = timer.timeout_add(2, gt)
    for i in range(800000):
        c64.iterate()
    gt.count = 800000
    gtk.main()
