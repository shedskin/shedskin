#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import pygame

from c64 import c64, screens
print(c64)
from c64.symbols import S_A, S_X, S_Y, S_SP, S_PC
from optparse import OptionParser


'''
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

    def handle_key_press(self, keycode):
        n = self.keycode_names.get(keycode)
        if n:
            return self.C64.CIA1.handle_key_press(n)

    def handle_key_release(self, keycode):
        n = self.keycode_names.get(keycode)
        if n:
            return self.C64.CIA1.handle_key_release(n)

        self.screen = c64.VIC.screen
        native_pixbuf = self.screen.get_rendered_pixbuf()
        if native_pixbuf != 0:
            self.pixbuf = GObject.PyGObjectCPAI().pygobject_new(native_pixbuf)
            self.B_create_flip_pixbuf = False
        else:
            self.pixbuf = None
            self.B_create_flip_pixbuf = True

    def repaint(self, drawarea, pCr):
        self.C64.fire_timer()

        s = self.screen.pixbuf_obj.get_rendered_image()
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_data(s, GdkPixbuf.Colorspace.RGB, True, 8, screens.WIDTH, screens.HEIGHT, screens.WIDTH * 4)  # TODO optimize!!
        self.pixbuf = self.pixbuf.scale_simple(2*screens.WIDTH, 2*screens.HEIGHT, GdkPixbuf.InterpType.NEAREST)

        Gdk.cairo_set_source_pixbuf(pCr, self.pixbuf, 5, 5)
        pCr.paint()

        self.drawing_area.queue_draw()
'''

def main():
    parser = OptionParser()
    parser.add_option("-t", "--tape", dest="tape",help="load from T64 tape image", metavar="TAPE")
    parser.add_option("-p", "--prg", dest="prg", help="load from PRG file", metavar="PRG")
    (options, args) = parser.parse_args()

    c_64 = c64.C64()
    c64_screen = c_64.VIC.screen

    if options.tape:
        c_64.set_tape_image_name(options.tape.encode(), b"T64")
    elif options.prg:
        c_64.set_tape_image_name(options.prg.encode(), b"PRG")

    for i in range(50000): # boot a little first
        c_64.iterate()

    screen = (screens.WIDTH, screens.HEIGHT)
    pygame.init()
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))


    clock = pygame.time.Clock()

    ingame = True
    while ingame:
        c_64.fire_timer()
        s = c64_screen.pixbuf_obj.get_rendered_image()
        img = pygame.image.frombuffer(s, screen, 'RGBX')

        surface.blit(img, (0, 0))
        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    main()
