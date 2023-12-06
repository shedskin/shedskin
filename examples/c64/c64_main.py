#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

from c64 import c64, screens
print(c64)
from c64.symbols import S_A, S_X, S_Y, S_SP, S_PC
from optparse import OptionParser

def unpack_unsigned(value):
    return value

def to_signed_byte(value):
    return value if value < 0x80 else -(256 - value)

class StatusDialog(Gtk.Dialog):
    def __init__(self, *args, **kwargs):
        Gtk.Dialog.__init__(self, *args, **kwargs)
        self.size_group = Gtk.SizeGroup(Gtk.SIZE_GROUP_HORIZONTAL)
        self.add_button(Gtk.STOCK_CLOSE, Gtk.RESPONSE_CLOSE)
        self.controls = {}
        for ID in [S_A, S_X, S_Y, S_SP, S_PC]:
            self.add_line(ID)

    def add_line(self, ID):
        box = Gtk.HBox()
        label = Gtk.Label(chr(ID))
        self.size_group.add_widget(label)
        control = Gtk.Label()
        box.pack_start(label, False, False, 0)
        box.pack_start(control, True, True, 0)
        self.vbox.pack_start(box, False, False, 0)
        self.controls[ID] = control
        return control

    def set_value(self, ID, value):
        v = unpack_unsigned(value)
        text = "$%04X=%r=%r" % (v, v, to_signed_byte(value) if ID != S_PC else value)
        self.controls[ID].set_text(text)

class Controls(Gtk.VBox):
    def __init__(self, c64):
        Gtk.VBox.__init__(self)
        self.C64 = c64
        self.status_dialog = None
        keyboard_matrix = self.C64.CIA1.get_keyboard_matrix()
        self.hardware_keycodes = {} # keyval_name -> keycode
        self.keycode_names = {}
        self.keymap = Gdk.Keymap.get_default()
        self.screen_count = 0
        alternatives = { # C64_name: GDK_name
            "grave": "numbersign", # German
            "LeftArrow": "Escape",
            "pound": "F9",
            "/": "F8", # actually overwritten below :P
            "=": "F7", # eep.
            ";": "F6", # eep.
        }
        for row in keyboard_matrix:
            for cell in row:
                #print(cell)
                entries = self.keymap.get_entries_for_keyval(Gdk.keyval_from_name(alternatives.get(cell) or cell) or ord(cell))
                if entries is None:
                    entries = self.keymap.get_entries_for_keyval(Gdk.keyval_from_name(alternatives[cell]))
                    #print(cell)
                assert(entries)
                if entries[1]:
                    hardware_keycode = entries[1][0].keycode
                    self.hardware_keycodes[cell] = hardware_keycode
                    self.keycode_names[hardware_keycode] = cell # for the C64, that is.
        self.hardware_keycodes["/"] = 20 # FIXME remove this.
        self.keycode_names[20] = "/" # FIXME remove this.

        status_button = Gtk.Button(label="_Status")
        status_button.connect("clicked", self.show_status)
        pause_button = Gtk.Button(label="_Pause")
        pause_button.connect("clicked", self.pause_CPU)
        read_memory_button = Gtk.Button(label="_Read Memory...")
        read_memory_button.connect("clicked", self.dump_memory)
        toggle_disassembly_button = Gtk.Button(label="_Toggle Disassembly")
        toggle_disassembly_button.connect("clicked", self.toggle_disassembly)
        self.pack_start(status_button, False, False ,0)
        self.pack_start(pause_button, False, False ,0)
        self.pack_start(read_memory_button, False, False ,0)
        self.pack_start(toggle_disassembly_button, False, False ,0)
        self.show_all()

    def show_status(self, *args, **kwargs):
        pass

    def pause_CPU(self, widget, *args, **kwargs):
        pass

    def toggle_disassembly(self, *args, **kwargs):
        pass

    def dump_memory(self, *args, **kwargs):
        pass

    def update_status(self):
        pass

    def handle_key_press(self, keycode):
        n = self.keycode_names.get(keycode)
        if n:
            return self.C64.CIA1.handle_key_press(n)

    def handle_key_release(self, keycode):
        n = self.keycode_names.get(keycode)
        if n:
            return self.C64.CIA1.handle_key_release(n)

# TODO 3 bit row counter.

class EventBox(Gtk.EventBox):
    def __init__(self, controls):
        Gtk.EventBox.__init__(self)
        self.controls = controls
        self.props.can_focus = True
        #self.pressed_keys = set()
        #self.keymap = Gdk.keymap_get_default()
        self.connect("key-press-event", self.handle_key_press)
        self.connect("key-release-event", self.handle_key_release)
        self.connect("button-press-event", self.handle_button_press)
    def handle_button_press(self, widget, event):
        self.grab_focus()
        return False
    def handle_key_press(self, widget, event):
        return self.controls.handle_key_press(event.hardware_keycode)
    def handle_key_release(self, widget, event):
        # hardware_keycode
        return self.controls.handle_key_release(event.hardware_keycode)
        #self.pressed_keys.discard(event.keycode)

class View(object): # graphical part.
    def __init__(self, c64, controls):
        self.C64 = c64
        self.screen = c64.VIC.screen
        native_pixbuf = self.screen.get_rendered_pixbuf()
        if native_pixbuf != 0:
            self.pixbuf = GObject.PyGObjectCPAI().pygobject_new(native_pixbuf)
            self.B_create_flip_pixbuf = False
        else:
            self.pixbuf = None
            self.B_create_flip_pixbuf = True
        #self.pixbuf = Gdk.Pixbuf(Gdk.COLORSPACE_RGB, True, 8, screens.WIDTH, screens.HEIGHT)
        #self.pixbuf.fill(0x000000FF)
        self.window = Gtk.Window()
        self.event_box = EventBox(controls)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.repaint)
        self.drawing_area.set_size_request(screens.WIDTH*2, screens.HEIGHT*2) # FIXME make configurable.
        self.drawing_area.show()
        self.event_box.show()
        box = Gtk.HBox()
        self.event_box.add(self.drawing_area)
        box.pack_start(self.event_box, False, False, 0)
        box.pack_start(controls, False, False, 0)
        box.show()
        self.window.add(box)
        self.window.show_all()

    def repaint(self, drawarea, pCr):
        self.C64.fire_timer()

        s = self.screen.pixbuf_obj.get_rendered_image()
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_data(s, GdkPixbuf.Colorspace.RGB, True, 8, screens.WIDTH, screens.HEIGHT, screens.WIDTH * 4)  # TODO optimize!!
        self.pixbuf = self.pixbuf.scale_simple(2*screens.WIDTH, 2*screens.HEIGHT, GdkPixbuf.InterpType.NEAREST)

        Gdk.cairo_set_source_pixbuf(pCr, self.pixbuf, 5, 5)
        pCr.paint()

        self.drawing_area.queue_draw()

def main():
    parser = OptionParser()
    parser.add_option("-t", "--tape", dest="tape",help="load from T64 tape image", metavar="TAPE")
    parser.add_option("-p", "--prg", dest="prg", help="load from PRG file", metavar="PRG")
    (options, args) = parser.parse_args()
    c_64 = c64.C64()
    if options.tape:
        c_64.set_tape_image_name(options.tape.encode(), b"T64")
        #c_64.set_tape_loader(loaders.t64.Loader.parse(open(options.tape, "rb"), options.tape))
    elif options.prg:
        c_64.set_tape_image_name(options.prg.encode(), b"PRG")
        #c_64.set_tape_loader(loaders.t64.Loader.parse(open(options.prg, "rb"), options.prg))
    for i in range(50000): # boot a little first
        c_64.iterate()
    controls = Controls(c_64)
    assert(isinstance(controls, Gtk.VBox))
    graphics_view = View(c_64, controls)
    controls.graphics_view = graphics_view
    Gtk.main()

if __name__ == '__main__':
    main()
