#/usr/bin/env python

# placed in the public domain by John Eriksson, http://arainyday.se

import pygame
from pygame.locals import *

from time import time

import os
os.system('cp astar.py astar_orig.py')
import astar_orig as AStar
import astar as AStar_ss
print('using', AStar_ss.__file__)

class AStarExample:
    #           -1        1           2            3            4        Start    Finish    Find path    Shed Skin     Reset
    colors = [(0,0,0),(0,255,0),(0,255-20,0),(0,255-40,0),(0,255-60,0),(0,0,255),(255,0,0),(100,150,100),(120,0,120),(150,100,100)]

    pathlines = []

    def initMap(self,w,h):
        self.mapdata = []
        self.mapw = w
        self.maph = h
        self.startpoint = [1,1]
        self.endpoint = [w-2,h-2]

        size = w*h
        for i in range(size):
            self.mapdata.append(1)

        self.mapdata[(self.startpoint[1]*w)+self.startpoint[0]] = 5
        self.mapdata[(self.endpoint[1]*w)+self.endpoint[0]] = 6

        self.maprect = Rect(0,0,w*16,h*16)

    def drawMap(self):
        x = 0
        y = 0
        rect = [0,0,16,16]
        for p in self.mapdata:
            if p == -1:
                p = 0
            rect[0] = x*16
            rect[1] = y*16
            self.screen.fill(self.colors[p],rect)
            x+=1
            if x>=self.mapw:
                x=0
                y+=1

    def updateMap(self,x,y,v):
        mi = (y*self.mapw)+x
        if v == 5: # startpoint
            if self.mapdata[mi] != 5 and self.mapdata[mi] != 6:
                self.mapdata[(self.startpoint[1]*self.mapw)+self.startpoint[0]] = 1
                self.screen.fill(self.colors[1],(self.startpoint[0]*16,self.startpoint[1]*16,16,16))
                self.startpoint = [x,y]
                self.mapdata[mi] = 5
                self.screen.fill(self.colors[5],(x*16,y*16,16,16))
        elif v == 6: # endpoint
            if self.mapdata[mi] != 5 and self.mapdata[mi] != 6:
                self.mapdata[(self.endpoint[1]*self.mapw)+self.endpoint[0]] = 1
                self.screen.fill(self.colors[1],(self.endpoint[0]*16,self.endpoint[1]*16,16,16))
                self.endpoint = [x,y]
                self.mapdata[mi] = 6
                self.screen.fill(self.colors[6],(x*16,y*16,16,16))
        else:
            if self.mapdata[mi] != 5 and self.mapdata[mi] != 6:
                if v == 0:
                    self.mapdata[mi] = -1
                else:
                    self.mapdata[mi] = v

                self.screen.fill(self.colors[v],(x*16,y*16,16,16))

    def drawMenu(self):

        text = ["Blocking (-1)", "Walkable (1)", "Walkable (2)", "Walkable (3)", "Walkable (4)", "Start point", "End point", "Find path", "Shed Skin", "Reset"]

        fnt = pygame.font.Font(pygame.font.get_default_font(),11)

        self.menurect = Rect(550,5,85,32*len(self.colors))

        rect = Rect(550,5,85,32)

        i = 0
        for c in self.colors:
            self.screen.fill(c,rect)
            ts=fnt.render(text[i], 1, (255,255,255))
            trect = ts.get_rect()
            trect.center = rect.center
            self.screen.blit(ts,trect.topleft)
            rect.y+=32
            i+=1

    def findPath(self):
        astar = AStar.AStar(AStar.SQ_MapHandler(self.mapdata,self.mapw,self.maph))
        start = AStar.SQ_Location(self.startpoint[0],self.startpoint[1])
        end = AStar.SQ_Location(self.endpoint[0],self.endpoint[1])

        s = time()
        for x in range(10): # XXX to better compare times
            p = astar.findPath(start,end)
        e = time()

        if not p:
            print("No path found!")
        else:
            print("Found path (10 times) in %d moves and %f seconds." % (len(p.nodes),(e-s)))
            self.pathlines = []
            self.pathlines.append((start.x*16+8,start.y*16+8))
            for n in p.nodes:
                self.pathlines.append((n.location.x*16+8,n.location.y*16+8))
            self.pathlines.append((end.x*16+8,end.y*16+8))

    def findPath_ss(self):
        astar = AStar_ss.AStar(AStar_ss.SQ_MapHandler(self.mapdata,self.mapw,self.maph))
        start = AStar_ss.SQ_Location(self.startpoint[0],self.startpoint[1])
        end = AStar_ss.SQ_Location(self.endpoint[0],self.endpoint[1])

        s = time()
        for x in range(10): # XXX to better compare times
            p = astar.findPath(start,end)
        e = time()

        if not p:
            print("No path found!")
        else:
            print("Found path (10 times) in %d moves and %f seconds." % (len(p.nodes),(e-s)))
            self.pathlines = []
            self.pathlines.append((start.x*16+8,start.y*16+8))
            for n in p.nodes:
                self.pathlines.append((n.location.x*16+8,n.location.y*16+8))
            self.pathlines.append((end.x*16+8,end.y*16+8))

    def mainLoop(self):

        pygame.init()    

        self.screen = pygame.display.set_mode((640, 480),HWSURFACE)
        pygame.display.set_caption('AStarExample')

        self.screen.fill((150,150,150))

        self.initMap(34,30)
        self.drawMap()
        self.editmode = 0

        self.drawMenu()

        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return

                elif event.type == MOUSEBUTTONDOWN:
                    if len(self.pathlines):
                        self.pathlines=[]
                        self.drawMap()
                    mx = event.pos[0]
                    my = event.pos[1]
                    if self.maprect.collidepoint(mx,my):
                        self.updateMap(mx//16,my//16,self.editmode)
                    elif self.menurect.collidepoint(mx,my):
                        my-=self.menurect.y
                        em = my//32
                        if em == 7: #trace
                            self.findPath()
                            if len(self.pathlines):
                                pygame.draw.lines(self.screen, (255,255,255,255), 0, self.pathlines)
                        elif em == 8: #trace
                            self.findPath_ss()
                            if len(self.pathlines):
                                pygame.draw.lines(self.screen, (255,255,255,255), 0, self.pathlines)
                        elif em == 9: #reset
                            self.initMap(34,30)
                            self.drawMap()
                        else:
                            self.editmode = em

                elif event.type == MOUSEMOTION and event.buttons[0]:
                    mx = event.pos[0]
                    my = event.pos[1]
                    if self.maprect.collidepoint(mx,my):
                        if len(self.pathlines):
                            self.pathlines=[]
                            self.drawMap()
                        self.updateMap(mx//16,my//16,self.editmode)

            pygame.display.flip()

def main():
    g = AStarExample()
    g.mainLoop()

#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
