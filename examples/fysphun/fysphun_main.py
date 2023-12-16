# (c) Alex P-B (chozabu@gmail.com)
# license: http://creativecommons.org/licenses/by-nc-sa/2.5/

import pygame
import fysphun

print(fysphun.__file__)

WIDTH, HEIGHT = 1024, 768


def main():
    def nearestpoint(x, y):
        mind = 10000000
        retp = None
        for p in points:
            xd = x - p.x
            yd = y - p.y
            td = xd * xd + yd * yd
            if td < mind:
                retp = p
                mind = td
        return retp

    pygame.init()
    screen = (WIDTH, HEIGHT)
    surface = pygame.display.set_mode(screen)
    pygame.display.set_caption("drag points!")

    fysphun.setup(WIDTH, HEIGHT)

    points = fysphun.points
    links = fysphun.links
    wheels = fysphun.wheels

    mx = 100
    my = 100

    paused = 0
    shiftdown = 0
    wheelpower = 0.1
    draggingpoint = False
    nearp = points[0]

    clock = pygame.time.Clock()

    ingame = True
    while ingame:
        for p in points:
            if not p.locked:
                p.basicphys()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                ingame = False
            elif e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                nearp = nearestpoint(mx, my)
                draggingpoint = True
            elif e.type == pygame.MOUSEBUTTONUP:
                draggingpoint = False

        if draggingpoint:
            nearp.x = mx
            nearp.y = my

            gravmax = 0.0

        # more input!
        for w in wheels:
            w.addpower(wheelpower)

        # Constraints!
        for l in links:
            l.applyme()

        # World constraints!
        for p in points:
            p.basiclimits()
        for p in points:
            if p.locked:
                p.x = p.ox
                p.y = p.oy

        # draw
        surface.fill((0, 0, 0))
        for l in links:
            if l.drawme:
                pygame.draw.lines(
                    surface,
                    (255, 0, 0),
                    0,
                    [(int(l.p1.x), int(l.p1.y)), (int(l.p2.x), int(l.p2.y))],
                    1,
                )
        for p in points:
            pygame.draw.circle(surface, (0, 255, 0), (int(p.x), int(p.y)), int(p.rad))

        pygame.draw.circle(
            surface, (0, 0, 255), (int(nearp.x), int(nearp.y)), int(nearp.rad * 0.74)
        )

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
