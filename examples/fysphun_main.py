# (c) Alex P-B (chozabu@gmail.com) 
# license: http://creativecommons.org/licenses/by-nc-sa/2.5/

import pygame
import fysphun
print fysphun.__file__

pygame.init()

sh = 768
sw = 1024
fysphun.setup(sw,sh)

screen = pygame.display.set_mode((sw,sh),0,32)
pygame.display.set_caption("FysPhun, check command line for controls!")

points = fysphun.points
links = fysphun.links
wheels = fysphun.wheels

def nearestpoint(x,y):
	mind = 10000000
	retp = None
	for p in points:
		xd = x-p.x
		yd = y-p.y
		td = xd*xd+yd*yd
		if td < mind:
			retp = p
			mind = td
	return retp

mx = 100
my = 100

paused = 0
shiftdown = 0
wheelpower = 0.1
draggingpoint = 0
nearp = points[0]

ingame = 1

while ingame:
        for p in points:
                if not p.locked:
                        p.basicphys()

	for e in pygame.event.get():
		if e.type is pygame.QUIT:
			ingame = 0
                elif e.type is pygame.MOUSEMOTION:
			mx,my = e.pos
                elif e.type is pygame.MOUSEBUTTONDOWN:
			mx,my = e.pos
                        nearp = nearestpoint(mx,my)
                        draggingpoint = 1
                elif e.type is pygame.MOUSEBUTTONUP:
                        draggingpoint = 0

	if draggingpoint:
		nearp.x = mx
                nearp.y = my

        gravmax = 0.0

        #more input!
        for w in wheels:
                w.addpower(wheelpower)
        #Constraints!
        for l in links:
                l.applyme()
        #World constraints!
        for p in points:
                p.basiclimits()
        for p in points:
                if p.locked:
                        p.x = p.ox
                        p.y = p.oy

	#draw
	screen.fill((0,0,0))
	for l in links:
		if l.drawme:pygame.draw.lines(screen, (255,0,0),0, [(int(l.p1.x),int(l.p1.y)),(int(l.p2.x),int(l.p2.y))],1)
	for p in points:
		pygame.draw.circle(screen, (0,255,0), (int(p.x),int(p.y)), int(p.rad))

	pygame.draw.circle(screen, (0,0,255), (int(nearp.x),int(nearp.y)), int(nearp.rad*0.74))

	pygame.display.flip()
	pygame.time.wait(5)
