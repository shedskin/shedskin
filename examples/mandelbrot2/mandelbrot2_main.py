# interactive mandelbrot program
# copyright Tony Veijalainen, tony.veijalainen@gmail.com

import os

import mandelbrot2
print(mandelbrot2)
from mandelbrot2 import mandel_file

import pygame

WIDTH, HEIGHT = 1024, 768


def main():
    screen = (WIDTH, HEIGHT)
    pygame.init()
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    # get params from file name
    fn = 'm-1 0i_3.5_240.bmp'
    ipos = fn.find('i')
    cx, cy = list(map(float, fn[1:ipos].split()))
    fsize, rest = fn[ipos+2:].split('_', 1)
    fsize = float(fsize)
    max_iterations = int(rest.split('.',1)[0])
    step = fsize / max(WIDTH, HEIGHT)

    def render(bmp):
        img = pygame.image.load(bmp)
        surface.blit(img, (0, 0))
        pygame.display.flip()

    # render initial image
    render(mandel_file(cx, cy, fsize, max_iterations, WIDTH, HEIGHT))

    clock = pygame.time.Clock()

    ingame = True
    while ingame:
        # quit?
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            ingame = False

        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                ingame = False

            # check mouse
            elif event.type == pygame.MOUSEBUTTONDOWN:
                xshift, yshift = event.pos[0] - WIDTH // 2, HEIGHT // 2 - event.pos[1]
                cx, cy = xshift * step + cx, yshift * step + cy

                # zoom in/out?
                if event.button == 1:
                    print('zoom in')
                    fsize /= 2.0

                elif event.button == 3:
                    print('zoom out')
                    fsize *= 2.0

                step = fsize / max(WIDTH, HEIGHT)

                # render updated image
                render(mandel_file(cx, cy, fsize, max_iterations, WIDTH, HEIGHT))

        clock.tick(60)

if __name__ == '__main__':
    main()
