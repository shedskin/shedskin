#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import pygtk
pygtk.require("2.0")
import gtk
import gobject
import sys
import time
from c64 import c64, screens
from c64.symbols import S_A, S_X, S_Y, S_SP, S_PC
from optparse import OptionParser

def unpack_unsigned(value):
    return value

def to_signed_byte(value):
    return value if value < 0x80 else -(256 - value)

class StatusDialog(gtk.Dialog):
    def __init__(self, *args, **kwargs):
        gtk.Dialog.__init__(self, *args, **kwargs)
        self.size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        self.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.controls = {}
        for ID in [S_A, S_X, S_Y, S_SP, S_PC]:
            self.add_line(ID)

    def add_line(self, ID):
        box = gtk.HBox()
        label = gtk.Label(chr(ID))
        self.size_group.add_widget(label)
        control = gtk.Label()
        box.pack_start(label, False, False)
        box.pack_start(control, True, True)
        self.vbox.pack_start(box, False, False)
        self.controls[ID] = control
        return control

    def set_value(self, ID, value):
        v = unpack_unsigned(value)
        text = "$%04X=%r=%r" % (v, v, to_signed_byte(value) if ID != S_PC else value)
        self.controls[ID].set_text(text)

class Controls(gtk.VBox):
    def __init__(self, c64):
        gtk.VBox.__init__(self)
        self.C64 = c64
        self.status_dialog = None
        keyboard_matrix = self.C64.CIA1.get_keyboard_matrix()
        self.hardware_keycodes = {} # keyval_name -> keycode
        self.keycode_names = {}
        self.keymap = gtk.gdk.keymap_get_default()
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
                entries = self.keymap.get_entries_for_keyval(gtk.gdk.keyval_from_name(alternatives.get(cell) or cell) or ord(cell))
                if entries is None:
                    entries = self.keymap.get_entries_for_keyval(gtk.gdk.keyval_from_name(alternatives[cell]))
                    #print(cell)
                assert(entries)
                hardware_keycode = entries[0][0]
                self.hardware_keycodes[cell] = hardware_keycode
                self.keycode_names[hardware_keycode] = cell # for the C64, that is.
        self.hardware_keycodes["/"] = 20 # FIXME remove this.
        self.keycode_names[20] = "/" # FIXME remove this.
                
        status_button = gtk.Button("_Status")
        status_button.connect("clicked", self.show_status)
        pause_button = gtk.Button("_Pause")
        pause_button.connect("clicked", self.pause_CPU)
        read_memory_button = gtk.Button("_Read Memory...")
        read_memory_button.connect("clicked", self.dump_memory)
        toggle_disassembly_button = gtk.Button("_Toggle Disassembly")
        toggle_disassembly_button.connect("clicked", self.toggle_disassembly)
        self.pack_start(status_button, False)
        self.pack_start(pause_button, False)
        self.pack_start(read_memory_button, False)
        self.pack_start(toggle_disassembly_button, False)
        self.show_all()
    def set_timer(self):
        self.timer = gobject.timeout_add(16, self.fire_timer)
        #self.timer = gobject.timeout_add(90, self.fire_timer)
    def unset_timer(self):
        gobject.source_remove(self.timer)
        self.timer = 0
    def is_timer_running(self):
        return(self.timer != 0)
    def fire_timer(self):
        # FIXME self.C64.CIA1.pressed_keys = self.graphics_view.event_box.pressed_keys
        t0 = time.time()
        self.C64.fire_timer()
        #self.graphics_view.repaint()
        self.screen_count += 1
        if self.screen_count % 10 == 0:
            print 'drawing speed: %.2f fps' % (1 / (time.time()-t0))
        return True

    def show_status(self, *args, **kwargs):
        toplevel_widget = self.get_toplevel()
        if self.status_dialog is None:
            self.status_dialog = StatusDialog(parent = toplevel_widget)
            def unset_status_dialog(*args, **kwargs):
                self.status_dialog = None
            self.status_dialog.set_transient_for(toplevel_widget)
            self.status_dialog.connect("delete-event", unset_status_dialog)
            self.status_dialog.show_all()
            gobject.timeout_add(50, self.update_status) # FIXME don't do that too often.

        self.update_status()

    def pause_CPU(self, widget, *args, **kwargs):
        # FIXME abstract that properly.
        C64 = self.C64
        if self.is_timer_running():
            self.unset_timer()
            widget.set_label("_Continue")
        else:
            self.set_timer()
            widget.set_label("_Pause")

    def toggle_disassembly(self, *args, **kwargs):
        self.C64.CPU.B_disasm = not self.C64.CPU.B_disasm
        
    def dump_memory(self, *args, **kwargs):
        MMU = self.C64.CPU.MMU
        address = 0xF3 # 300
        sys.stdout.write("(%04X) " % address)
        for i in range(16):
            v = MMU.read_memory(address + i, 1)
            sys.stdout.write("%02X " % v)
        sys.stdout.write("\n")

    def update_status(self):
        if self.status_dialog is None:
            return False
        C64 = self.C64
        for register in [S_A, S_X, S_Y, S_SP, S_PC]:
            self.status_dialog.set_value(register, C64.CPU.read_register(register))
        return True

    def handle_key_press(self, keycode):
        n = self.keycode_names.get(keycode)
        if n:
            return self.C64.CIA1.handle_key_press(n)

    def handle_key_release(self, keycode):
        n = self.keycode_names.get(keycode)
        if n:
            return self.C64.CIA1.handle_key_release(n)

# TODO 3 bit row counter.

class EventBox(gtk.EventBox):
    def __init__(self, controls):
        gtk.EventBox.__init__(self)
        self.controls = controls
        self.props.can_focus = True
        #self.pressed_keys = set()
        #self.keymap = gtk.gdk.keymap_get_default()
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
        self.screen = c64.VIC.screen
        native_pixbuf = self.screen.get_rendered_pixbuf()
        if native_pixbuf != 0:
            self.pixbuf = gobjectc.PyGObjectCPAI().pygobject_new(native_pixbuf)
            self.B_create_flip_pixbuf = False
        else:
            self.pixbuf = None
            self.B_create_flip_pixbuf = True
        #self.pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, screens.WIDTH, screens.HEIGHT)
        #self.pixbuf.fill(0x000000FF)
        self.window = gtk.Window()
        self.event_box = EventBox(controls)
        self.drawing_area = gtk.DrawingArea()
        self.drawing_area.connect("realize", self.allocate_GC)
        self.drawing_area.connect("expose-event", self.repaint_X)
        self.drawing_area.set_size_request(screens.WIDTH*2, screens.HEIGHT*2) # FIXME make configurable.
        self.drawing_area.show()
        self.event_box.show()
        gobject.timeout_add(16, self.repaint_T)
        box = gtk.HBox()
        self.event_box.add(self.drawing_area)
        box.pack_start(self.event_box, False, False)
        box.pack_start(controls, False, False)
        box.show()
        self.window.add(box)
        self.window.show_all()
    def allocate_GC(self, widget, *args, **kwargs):
        self.GC = widget.window.new_gc()
    def repaint_X(self, widget, event):
        self.repaint()
    def repaint_T(self):
        self.repaint()
        return(True)
    def repaint(self):
        if self.B_create_flip_pixbuf:
            s = self.screen.pixbuf_obj.get_rendered_image()
            assert(len(s) == 439200)
            self.pixbuf = gtk.gdk.pixbuf_new_from_data(s, gtk.gdk.COLORSPACE_RGB, True, 8, screens.WIDTH, screens.HEIGHT, screens.WIDTH * 4) # TODO optimize!!
        widget = self.drawing_area
        self.pixbuf = self.pixbuf.scale_simple(screens.WIDTH*2, screens.HEIGHT*2, gtk.gdk.INTERP_NEAREST)
        if widget.window: # window already realized
            #print("YEP", data)
            widget.window.draw_pixbuf(self.GC, self.pixbuf, 0, 0, 0, 0, screens.WIDTH*2, screens.HEIGHT*2, gtk.gdk.RGB_DITHER_NONE, 0, 0)
            #drawable(self.pixmap_GC, self.pixmap, 0, 0, 0, 0, -1, -1)

def main():
    parser = OptionParser()
    parser.add_option("-t", "--tape", dest="tape",help="load from T64 tape image", metavar="TAPE")
    parser.add_option("-p", "--prg", dest="prg", help="load from PRG file", metavar="PRG")
    (options, args) = parser.parse_args()
    c_64 = c64.C64()
    if options.tape:
        c_64.set_tape_image_name(options.tape, "T64")
        #c_64.set_tape_loader(loaders.t64.Loader.parse(open(options.tape, "rb"), options.tape))
    elif options.prg:
        c_64.set_tape_image_name(options.prg, "PRG")
        #c_64.set_tape_loader(loaders.t64.Loader.parse(open(options.prg, "rb"), options.prg))
    for i in range(50000): # boot a little first
        c_64.iterate()
    controls = Controls(c_64)
    assert(isinstance(controls, gtk.VBox))
    graphics_view = View(c_64, controls)
    controls.graphics_view = graphics_view
    controls.set_timer()
    gtk.main()

if __name__ == '__main__':
    main()
