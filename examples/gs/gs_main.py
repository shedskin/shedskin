#!/usr/bin/env python2
# Original author Mariano Lambir. https://github.com/mlambir/Pygame-FPS
# Modified by Ernesto Ferro and Mark Dufour to work with Shed Skin Python-to-C++ compiler by Mark Dufour
# Shed Skin homepage: http://mark.dufour.googlepages.com

import array
import sys
import time

import pygame

from Gh0stenstein import world_manager
print(world_manager)

WIDTH, HEIGHT = 800, 600

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


def load_image(wm, pos, filename, w, h):
    surf = pygame.image.load(filename)
    surf = pygame.transform.scale(surf, (w, h))

    img = pygame.image.tostring(surf, 'RGBA')

    arr = array.array('I')
    arr.frombytes(img)
    wm.load_image(pos, arr.tolist(), w, h)


def main():
    screen = (WIDTH, HEIGHT)
    pygame.init()
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    wm = world_manager.WorldManager(WIDTH, HEIGHT, worldMap, sprite_positions, 22, 11.5, -1, 0, 0, .66)

    load_image(wm, 0, 'Gh0stenstein/pics/background.png', WIDTH, HEIGHT)
    load_image(wm, 1, 'Gh0stenstein/pics/walls/eagle.png', 64, 64)
    load_image(wm, 2, 'Gh0stenstein/pics/walls/redbrick.png', 64, 64)
    load_image(wm, 3, 'Gh0stenstein/pics/walls/purplestone.png', 64, 64)
    load_image(wm, 4, 'Gh0stenstein/pics/walls/greystone.png', 64, 64)
    load_image(wm, 5, 'Gh0stenstein/pics/walls/bluestone.png', 64, 64)
    load_image(wm, 6, 'Gh0stenstein/pics/walls/mossy.png', 64, 64)
    load_image(wm, 7, 'Gh0stenstein/pics/walls/wood.png', 64, 64)
    load_image(wm, 8, 'Gh0stenstein/pics/walls/colorstone.png', 64, 64)
    load_image(wm, 9, 'Gh0stenstein/pics/items/GoldBar.png', 64, 64)
    load_image(wm, 10, 'Gh0stenstein/pics/items/PlantInPot.png', 64, 64)
    load_image(wm, 11, 'Gh0stenstein/pics/items/BlueOverheadLight.png', 64, 64)

    clock = pygame.time.Clock()
    frame_count = 0
    delta = 0

    ingame = True
    while ingame:
        # handle keys
        keys = pygame.key.get_pressed()

        move_speed = 0.06  # the constant value is in squares / second
        rot_speed = 0.02

        if keys[pygame.K_LEFT]:
            wm.move('Left', move_speed, rot_speed)
        elif keys[pygame.K_RIGHT]:
            wm.move('Right', move_speed, rot_speed)
        elif keys[pygame.K_UP]:
            wm.move('Up', move_speed, rot_speed)
        elif keys[pygame.K_DOWN]:
            wm.move('Down', move_speed, rot_speed)

        if keys[pygame.K_q]:
            ingame = False
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                ingame = False

        # render!
        t0 = time.time()

        wm.draw()

        img = pygame.image.frombuffer(wm.dump(), (WIDTH, HEIGHT), 'RGBX')
        surface.blit(img, (0, 0))
        pygame.display.flip()

        clock.tick(60)

        delta = (time.time()-t0)

        if frame_count % 10 == 0:
            print('FPS %.2f' % (1/delta))
        frame_count += 1


if __name__ == '__main__':
    main()
