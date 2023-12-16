#!/usr/bin/python

# Copyright 2010 Eric Uhrhane.
#
# This file is part of Pylot.
#
# Pylot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pylot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.import math

import random
import time

import pygame

import pylot
from pylot.Pool import ThreadedQueueProcessor
#from pylot.Utils import *
from pylot import SimpleGeometry
print(SimpleGeometry.__file__)

WIDTH = 640
BLOCKS_WIDE = 40
BLOCKS_TALL = 40


class CameraHandler(object):
  def __init__(self, camera):
    self.camera = camera

  def handle(self, job):
    realJob, debugFlag = job
    return self.camera.runPixelRange(realJob)


def getBlock(i, j, BLOCKS_WIDE, BLOCKS_TALL):
    cols = WIDTH
    rows = WIDTH
    return ((int(float(cols) / BLOCKS_WIDE * i),
             int(float(cols) / BLOCKS_WIDE * (i + 1))),
            (int(float(rows) / BLOCKS_TALL * j),
             int(float(rows) / BLOCKS_TALL * (j + 1))))


def imageFromBlock(r, pixels):
    (x, xMax), (y, yMax) = r
    w = xMax - x
    h = yMax - y
    return Image.frombytes('RGB', (w, h), pixels)


def main():
    screen = (WIDTH, WIDTH)
    pygame.init()
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    geometry = SimpleGeometry.getGeometry(size=WIDTH, which=2)
    world = SimpleGeometry.getWorld(geometry)
    camera = SimpleGeometry.getCamera(world)

    processor = ThreadedQueueProcessor(CameraHandler(camera), 8, use_processes=True)

    jobs = []
    for i in range(BLOCKS_WIDE):
        for j in range(BLOCKS_TALL):
            jobs.append((getBlock(i, j, BLOCKS_WIDE, BLOCKS_TALL), False))
    random.shuffle(jobs)

    startTime = time.time()

    for j in jobs:
        processor.put(j)

    count = BLOCKS_WIDE * BLOCKS_TALL

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

        gotData = False
        block = processor.get(False)
        while block:
            gotData = True
            count -= 1
            r, pixels = block
            (x, _), (y, _) = r

            img = pygame.image.frombuffer(pixels, (WIDTH // BLOCKS_WIDE, WIDTH // BLOCKS_TALL), 'RGB')
            surface.blit(img, (x, y))
            pygame.display.flip()

            if count == 0:
                print("That took %.3f seconds." % (time.time() - startTime))
                break

            block = processor.get(False)

        clock.tick(60)

    processor.terminate()


if __name__ == '__main__':
    main()
