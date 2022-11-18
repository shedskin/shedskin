# Original author Mariano Lambir. https://github.com/mlambir/Pygame-FPS
# Modified by Ernesto Ferro to work with Shed Skin Python-to-C++ compiler by Mark Dufour
# Shed Skin homepage: http://mark.dufour.googlepages.com

import array
import math

from . import world_draw


class Image(object):
    def __init__(self, data, w, h):
        self.data, self.w, self.h = data, w, h


class WorldManager(object):
    def __init__(self, w, h, worldMap, sprite_positions, x, y, dirx, diry, planex, planey):
        self.w, self.h = w, h
        self.images = {}
        self.camera = Camera(x, y, dirx, diry, planex, planey)
        self.worldMap = worldMap
        self.sprite_positions = sprite_positions
        self.screen = w * h * [0]

    def dump(self):
        return array.array('I', self.screen).tobytes()

    def load_image(self, n, data, w, h):
        self.images[n] = Image(data, w, h)

    def draw(self):
        self.screen[:] = self.images[0].data

        blits = world_draw.draw(
            self.w, self.h,
            self.worldMap,
            self.sprite_positions,
            self.camera.x, self.camera.y,
            self.camera.dirx, self.camera.diry,
            self.camera.planex, self.camera.planey,
            64, 64)

        for blit in blits:
            is_sprite = blit[0]
            image = self.images[blit[1]]
            if blit[3] <= self.h:
                low, high = 0 + blit[5], blit[3] + blit[5]
            else:
                low = 0
                high = self.h
            for y in range(low, high):
                px = image.data[blit[2] + 64 * int(64 * (float(y - blit[5]) / blit[3]))]
                if not is_sprite or px != 0xff000000:
                    self.screen[self.w * y + blit[4]] = px

    def move(self, dir, moveSpeed, rotSpeed):
        wm = self
        if dir == 'Up':
            # move forward if no wall in front of you
            moveX = wm.camera.x + wm.camera.dirx * moveSpeed
            if(self.worldMap[int(moveX)][int(wm.camera.y)] == 0 and self.worldMap[int(moveX + 0.1)][int(wm.camera.y)] == 0):
                wm.camera.x += wm.camera.dirx * moveSpeed
            moveY = wm.camera.y + wm.camera.diry * moveSpeed
            if(self.worldMap[int(wm.camera.x)][int(moveY)] == 0 and self.worldMap[int(wm.camera.x)][int(moveY + 0.1)] == 0):
                wm.camera.y += wm.camera.diry * moveSpeed
        elif dir == 'Down':
            # move backwards if no wall behind you
            if(self.worldMap[int(wm.camera.x - wm.camera.dirx * moveSpeed)][int(wm.camera.y)] == 0):
                wm.camera.x -= wm.camera.dirx * moveSpeed
            if(self.worldMap[int(wm.camera.x)][int(wm.camera.y - wm.camera.diry * moveSpeed)] == 0):
                wm.camera.y -= wm.camera.diry * moveSpeed
        elif dir == 'Right':
            # rotate to the right
            # both camera direction and camera plane must be rotated
            oldDirX = wm.camera.dirx
            wm.camera.dirx = wm.camera.dirx * math.cos(
                - rotSpeed) - wm.camera.diry * math.sin(- rotSpeed)
            wm.camera.diry = oldDirX * math.sin(
                - rotSpeed) + wm.camera.diry * math.cos(- rotSpeed)
            oldPlaneX = wm.camera.planex
            wm.camera.planex = wm.camera.planex * math.cos(
                - rotSpeed) - wm.camera.planey * math.sin(- rotSpeed)
            wm.camera.planey = oldPlaneX * math.sin(
                - rotSpeed) + wm.camera.planey * math.cos(- rotSpeed)
        elif dir == 'Left':
            # rotate to the left
            # both camera direction and camera plane must be rotated
            oldDirX = wm.camera.dirx
            wm.camera.dirx = wm.camera.dirx * math.cos(
                rotSpeed) - wm.camera.diry * math.sin(rotSpeed)
            wm.camera.diry = oldDirX * math.sin(
                rotSpeed) + wm.camera.diry * math.cos(rotSpeed)
            oldPlaneX = wm.camera.planex
            wm.camera.planex = wm.camera.planex * math.cos(
                rotSpeed) - wm.camera.planey * math.sin(rotSpeed)
            wm.camera.planey = oldPlaneX * math.sin(
                rotSpeed) + wm.camera.planey * math.cos(rotSpeed)


class Camera(object):
    def __init__(self, x, y, dirx, diry, planex, planey):
        self.x = float(x)
        self.y = float(y)
        self.dirx = float(dirx)
        self.diry = float(diry)
        self.planex = float(planex)
        self.planey = float(planey)


def main():
    # modeling for shedskin extension module
    wm = WorldManager(1, 1, [[8]], [(1.0,)], 1.1, 2.2, 3.1, 4.2, 5.1, 6.2)
    wm.load_image(0, [1], 1, 1)
    wm.draw()
    wm.dump()
    wm.move('back', 0.0, 0.0)

if __name__ == '__main__':
    main()
