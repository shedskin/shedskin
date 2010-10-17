#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import pygtk
pygtk.require("2.0")
import gtk
import gobject

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

class GTextView:
    def __init__(self, VIC, controls):
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

class TextView(object):
    def __init__(self, VIC, controls):
        self.gt = GTextView(VIC, controls)

        self.VIC = VIC
        self.first_column = 0
        self.first_row = 0
        self.last_column = 0
        self.last_row = 0
        self.character_bitmaps_offset = 0 # FIXME correct that.
        self.video_offset = 0 # FIXME correct that.
        self.mode = "normal-text"
        self._border_color = 0 # FIXME default?
        self.old_VIC_bank = None
        self.background_color_0 = 0 # FIXME default?
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
        self.viewport_column = 0 # FIXME
        self.viewport_row = 0  # FIXME
        self.VIC_bank = -1 # FIXME
        self.characters = [] # code -> pixbuf.
        self.width = 40
        self.height = 25

    def allocate_pixmap(self, *args, **kwargs):
        self.pixmap = gtk.gdk.Pixmap(self.window.window, WIDTH, HEIGHT) #.connect("realize", self.use_pixmap)
        self.gt.colors = [self.pixmap.get_colormap().alloc_color(color) for color in self.gt.colors]

    def load_pixbuf(self, bits):
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, 8, 8)
        pixbuf.fill(0)
        # FIXME
        return pixbuf

    def get_pixmap_mask(self, char_data_1, B_invert):
            data = []
            for row in char_data_1:
                for column in range(8):
                    if ((row & (1 << (7 - column))) != 0) ^ B_invert:
                        data.append(0x0)
                        data.append(0x0)
                        data.append(0x0)
                        data.append(0xFF)
                    else:
                        data.append(0xFF)
                        data.append(0xFF)
                        data.append(0xFF)
                        data.append(0x00)

            data = b"".join(map(chr, data))
            pixbuf = gtk.gdk.pixbuf_new_from_data(data, gtk.gdk.COLORSPACE_RGB, True, 8, 8, 8, 8*4)
            pixmap_part, mask_part = pixbuf.render_pixmap_and_mask()
            return mask_part

    #def use_pixmap(self, window):
    #   self.pixmap = window

    def unprepare(self):
        self.old_VIC_bank = -1
        print("unprepare...")

    def prepare_characters(self):
        print("preparing...")
        self.characters = []
        self.inverse_characters = []
        character_bitmaps_offset = self.character_bitmaps_offset
        #VIC_bank_offset = self.VIC_bank * 4096
        #print("OFFS", character_bitmaps_offset)
        character_data = self.VIC.load_chunk(character_bitmaps_offset, 8 * 256)
        #print("L", len(character_data))
        for i in range(0, len(character_data), 8):
            char_data_1 = character_data[i : i + 8]
            self.characters.append(self.get_pixmap_mask(char_data_1, False))
            self.inverse_characters.append(self.get_pixmap_mask(char_data_1, True))
        self.characters = self.characters + self.inverse_characters

    def repaint_pixmap(self):
        window = self.pixmap
        GC = window.new_gc()
        #print("=========== REPAINT ========")
        #print(dir(self))
        size = window.get_size()
        color = self.gt.colors[self.border_color]
        #color = gtk.gdk.Color(red = 123.039015) # * 65535.0 / 255.0, green = 72.130708003 * 65535.0 / 255.0, blue = 144.4171376 * 65535.0 / 255.0)
        #print color.red, color.green, color.blue, self.border_color, "XX"
        GC.set_foreground(self.gt.colors[self.border_color])
        GC.set_fill(gtk.gdk.SOLID)
        #GC.set_background(self.colors[self.border_color])
        window.draw_rectangle(GC, True, 0, 0, size[0], size[1]) # TODO only draw border around it.
        GC.set_foreground(self.gt.colors[self.background_color_0])
        window.draw_rectangle(GC, True, self.first_column, self.first_row, self.last_column - self.first_column + 1, self.last_row - self.first_row + 1)

        # FIXME support other modes.
        if self.old_VIC_bank != self.VIC_bank:
            self.old_VIC_bank = self.VIC_bank
            self.prepare_characters()

        VIC = self.VIC
        offset = self.video_offset
        VX = self.first_column - self.viewport_column
        VY = self.first_row - self.viewport_row
        for row in range(24): # FIXME 25
            for column in range(40): # FIXME configurable
                code_color = VIC.VIC_read_memory(offset, 1)
                code = code_color & 255
                color = code_color >> 8
                pixmap = self.characters[code] if code < 128 else self.inverse_characters[code] # TODO inverse.
                if (color if code < 128 else self.background_color_0) >= len(self.gt.colors):
                    print("WHOOPS, code", code, "color", color)
                GC.set_foreground(self.gt.colors[color if code < 128 else self.background_color_0]) # FIXME
                GC.set_clip_mask(pixmap)
                GC.set_clip_origin(VX + column * 8, VY + row * 8)
                window.draw_rectangle(GC, True, VX + column * 8, VY + row * 8, 8, 8)
                #window.draw_pixbuf(GC, pixbuf, 0, 0, VX + column * 8, VY + row * 8)
                offset += 1

    def repaint(self):
        widget = self.drawing_area
        if self.pixmap is None:
            print("WHOOPS")
            return
        self.repaint_pixmap()
        GC = widget.window.new_gc()
        widget.window.draw_drawable(GC, self.pixmap, 0, 0, 0, 0, -1, -1)
        pass # TODO

    def repaint_X(self, widget, event):
        self.repaint()

    def repaint_T(self):
        #print("TIMER")
        self.repaint()
        #print("END")
        return True

    def set_border_color(self, value):
        self._border_color = value
        # TODO update pixbuf etc.

    border_color = property(lambda self: self._border_color, set_border_color)
