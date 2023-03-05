import math
import time

import pygame

import render

'''
Minimal DOOM WAD renderer

Goals:
-show inner workings of DOOM engine
-without relying on any graphics library
-omit some optimizations for readability (most notably, visplanes)
-less than 1000 lines while following PEP8
-compile with Shedskin to run at 60 FPS

Copyright 2023 Mark Dufour, license unclear.

Based on Java implementation by Leonardo Ono:

https://github.com/leonardo-ono/JavaDoomWADMapRendererTests

Compile with Shedskin for good performance (shedskin -e render && make)!

http://github.com/shedskin/shedskin

'''

WAD = 'DOOM1.WAD'
MAP = 'E1M1'
MUSIC = 'E1M1.FLAC'


def main():
    screen = (render.WIDTH, render.HEIGHT)
    pygame.init()
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    map_ = render.Map(WAD, MAP)
    player = map_.player
    palette = map_.palette
    frame_count = 0

    vx = vy = vz = 0.0
    va = 0.0

    delta = 1 / 60
    angular_accel = 30
    linear_accel = 0.4
    strafe = math.radians(90)

    try:
        pygame.mixer.music.load(MUSIC)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print(f'CANNOT LOAD MUSIC FILE! (f{MUSIC})')

    clock = pygame.time.Clock()

    ingame = True
    while ingame:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            ingame = False

        # angular speed
        if not keys[pygame.K_LCTRL]:
            if keys[pygame.K_RIGHT]:
                va -= angular_accel * delta
            if keys[pygame.K_LEFT]:
                va += angular_accel * delta

            va = min(max(va, -30), 30)

        player.angle += va * delta
        va = va * (1.0 - 8.0 * delta)

        # linear speeds
        def move_player(accel, strafe):
            ax = accel * math.cos(player.angle + strafe)
            ay = accel * math.sin(player.angle + strafe)
            vx2 = vx + ax
            vy2 = vy + ay
            vx2 = min(max(vx2, -4), 4)
            vy2 = min(max(vy2, -4), 4)
            return vx2, vy2

        if keys[pygame.K_LCTRL]:
            if keys[pygame.K_LEFT]:
                vx, vy = move_player(linear_accel, strafe)
            if keys[pygame.K_RIGHT]:
                vx, vy = move_player(linear_accel, -strafe)

        if keys[pygame.K_UP]:
            vx, vy = move_player(linear_accel, 0)

        if keys[pygame.K_DOWN]:
            vx, vy = move_player(-linear_accel, 0)

        # update player
        player.x += vx
        player.y += vy
        vx *= 0.95
        vy *= 0.95
        if player.z < player.floor_h + 48:
            player.z += 0.1 * (player.floor_h + 48 - player.z)
            vz = 0
        else:
            vz -= 0.1
            player.z += max(-5.0, vz)
        player.update()

        # quit?
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                ingame = False

        # render!
        t0 = time.time()

        buf = render.render(map_, frame_count)
        img = pygame.image.frombuffer(buf, (render.WIDTH, render.HEIGHT), 'P')
        img.set_palette(palette)
        surface.blit(img, (0, 0))
        pygame.display.flip()

        clock.tick(60)

        delta = (time.time()-t0)

        if frame_count % 10 == 0:
            print('FPS %.2f' % (1/delta))
        frame_count += 1


if __name__ == '__main__':
    main()
