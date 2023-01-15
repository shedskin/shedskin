"""
Ported from Sean McCullough's Processing code:
http://www.cricketschirping.com/processing/CirclePacking1/

See also: http://en.wiki.mcneel.com/default.aspx/McNeel/2DCirclePacking
http://www.cricketschirping.com/weblog/?p=1047
See also:
http://www.infovis-wiki.net/index.php/Circle_Packing

Original NodeBox code by Tom De Smedt:
http://nodebox.net/code/index.php/shared_2008-08-07-12-55-33
Later ported to Python + Psyco + Pygame by leonardo maffi, V.1.0, Apr 14 2009
"""

import sys, os, time
from random import randrange

import pygame # if pygame is absent this program may just print coords
from pygame.locals import QUIT, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

import circle

# to center the window in the screen
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 850

# you can reduce the NCIRCLES if you don't have Psyco or you have a slow PC
NCIRCLES = 120

# more iterations = smoother physics but slower animation
ITERATIONS = 80

SCREEN_WIDTH_2 = SCREEN_WIDTH / 2
SCREEN_HEIGHT_2 = SCREEN_HEIGHT / 2

def clamp(col):
    col = int(col)
    if col <= 0:
        return 0
    elif col > 255:
        return 255
    else:
        return col

def setup():
    global circles, surface, drawsurf, dragged, screen

    pygame.init()
    icon = pygame.Surface((1, 1))
    icon.set_alpha(0)
    pygame.display.set_icon(icon)
    screen = (SCREEN_WIDTH, SCREEN_HEIGHT)

    pygame.display.set_caption("Circle packing 2")
    surface = pygame.display.set_mode(screen)

    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    circles = []
    for i in range(NCIRCLES):
        radius = randrange(5, 6 + int(i/1.8))

        r = clamp(radius * 0.02 * 256)
        g = clamp((0.2 + radius * 0.03) * 256)
        b = 0
        a = clamp(0.8 * 256)
        c = circle.Circle(randrange(SCREEN_WIDTH), randrange(SCREEN_HEIGHT), radius, (r, g, b, a))

        circles.append(c)

    dragged = None

def get_input():
    global dragged
    key = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT or key[K_ESCAPE]:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN and dragged is None:
            mousex, mousey = pygame.mouse.get_pos()
            for circle in circles:
                if circle.contains(mousex, mousey):
                    dragged = circle
        elif event.type == MOUSEMOTION and dragged is not None:
            # drag objects with the mouse
            dragged.x, dragged.y = pygame.mouse.get_pos()
        elif event.type == MOUSEBUTTONUP:
            dragged = None

def run():
    global dragged

    iterations = 0
    t0 = time.time()
    while True:
        iterations += 1
        if iterations % 10 == 0:
            print(time.time()-t0)
            t0 = time.time()
        get_input()

        surface.fill((0, 0, 0))
        drawsurf.fill((0, 0, 0))

        for c in circles:
            pygame.draw.circle(drawsurf, pygame.Color(*c.color), (int(c.x), int(c.y)), int(c.radius), 0)

        for i in range(1, ITERATIONS):
            circle.pack(circles, 0.1/i, 2, dragged)

        surface.blit(drawsurf, (0, 0))
        pygame.display.flip()

setup()
circle.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
run()
