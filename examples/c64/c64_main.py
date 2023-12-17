#!/usr/bin/env python2
# I, Danny Milosavljevic, hereby place this file into the public domain.

import pygame

from c64 import c64, screens
print(c64)
from c64.symbols import S_A, S_X, S_Y, S_SP, S_PC
from optparse import OptionParser

SCALE = 2

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

    WIDTH = screens.WIDTH*SCALE
    HEIGHT = screens.HEIGHT*SCALE

    pygame.init()
    screen = (WIDTH, HEIGHT)
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    clock = pygame.time.Clock()

    n = 0
    ingame = True
    while ingame:
        c_64.fire_timer()
        s = c64_screen.pixbuf_obj.get_rendered_image()
        img = pygame.image.frombuffer(s, (screens.WIDTH, screens.HEIGHT), 'RGBX')
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                name = pygame.key.name(event.key).title()
                c_64.CIA1.handle_key_press(name)

            elif event.type == pygame.KEYUP:
                name = pygame.key.name(event.key).title()
                c_64.CIA1.handle_key_release(name)

            elif event.type == pygame.QUIT:
                ingame = False

        surface.blit(img, (0, 0))
        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    main()
