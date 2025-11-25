'''
3D Software Renderer

Converted to Python from:

https://github.com/BennyQBD/3DSoftwareRenderer/blob/master/LICENSE.txt

https://www.youtube.com/watch?v=Y_vvC2G7vRo&list=PLEETnX-uPtBUbVOok816vTl1K9vV1GgH5

Copyright (c) 2014, Benny Bobaganoosh

Copyright (c) 2025, Mark Dufour

Implements the following in < 500 LOC:

- reading of .obj files
- rendering polygons
- perspective-correct texture mapping
- z-buffering
- back-face and frustum culling
- clipping
- gouraud shading

Becomes ~13 times faster after compilation with Shedskin.

'''

import math
import time

from PIL import Image
import pygame

from render import *

WIDTH, HEIGHT = 800, 600


def load_texture(filename):
    image = Image.open(filename)
    return Bitmap(image.width, image.height, image.convert('RGBX').tobytes())


def main():
    screen = (WIDTH, HEIGHT)
    pygame.init()

    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()

    clock = pygame.time.Clock()
    frame_count = 0

    mesh = Mesh("buddha2.obj", scale=200)
    texture = load_texture("buddha2.jpg")
    transform = Transform(Vector4(0.0, 0.3, 3.0))
    transform = transform.rotate(quaternion_from_axis_angle(Vector4(1, 0, 0), 80))
    lightDir = Vector4(0, 0, -1)

#    mesh = Mesh("monkey0.obj")
#    texture = None
#    transform = Transform(Vector4(0.0, 0, 3.0))
#    lightDir = Vector4(0, -1, 0)

#    mesh = Mesh("smoothMonkey1.obj")
#    texture = load_texture("bricks2.jpg")
#    transform = Transform(Vector4(0.0, 0, 3.0))
#    lightDir = Vector4(1, 0, 0)

    camera = Camera(Matrix4().init_perspective(math.radians(70.0), WIDTH/HEIGHT, 0.1, 1000.0))

    target = RenderContext(WIDTH, HEIGHT)

    while True:
        t0 = time.time()

        target.clear()
        target.clear_zbuffer()
        mesh.draw(target, camera.get_view_projection(), transform.get_transformation(), texture, lightDir)

        img = pygame.image.frombuffer(target.bitmap.components, screen, 'RGBX')
        surface.blit(img, (0, 0))
        pygame.display.flip()

        clock.tick(60)

        delta = (time.time()-t0)

        transform = transform.rotate(quaternion_from_axis_angle(Vector4(0, 1, 0), delta/2))

        if frame_count % 10 == 0:
            print('FPS %.2f' % (1/delta))
        frame_count += 1

if __name__ == '__main__':
    main()
