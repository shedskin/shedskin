# Original author Mariano Lambir. https://github.com/mlambir/Pygame-FPS
# Modified by Ernesto Ferro to work with Shed Skin Python-to-C++ compiler by Mark Dufour
# Shed Skin homepage: http://mark.dufour.googlepages.com

import math


sort_camera_x = 0.0
sort_camera_y = 0.0


# function to sort sprites
def sprite_key(s1):
    s1Dist = (s1[0] - sort_camera_x) ** 2 + (s1[1] - sort_camera_y) ** 2
    return s1Dist


def draw(w, h,
         worldMap,
         sprite_positions,
         camera_x, camera_y,
         camera_dirx, camera_diry,
         camera_planex, camera_planey,
         texWidth, texHeight):
    zBuffer = []
    blits = []

    for x in range(w):
        # calculate ray position and direction
        cameraX = float(2 * x / float(w) - 1)  # x-coordinate in camera space
        rayPosX = camera_x
        rayPosY = camera_y
        rayDirX = camera_dirx + camera_planex * cameraX
        rayDirY = camera_diry + camera_planey * cameraX
        # which box of the map we're in
        mapX = int(rayPosX)
        mapY = int(rayPosY)

        # length of ray from current position to next x or y-side
        sideDistX = 0.
        sideDistY = 0.

        # length of ray from one x or y-side to next x or y-side
        deltaDistX = math.sqrt(1 + (rayDirY * rayDirY) / (rayDirX * rayDirX))
        if rayDirY == 0:
            rayDirY = 0.00001
        deltaDistY = math.sqrt(1 + (
            rayDirX * rayDirX) / (rayDirY * rayDirY))
        perpWallDist = 0.

        # what direction to step in x or y-direction (either +1 or -1)
        stepX = 0
        stepY = 0

        hit = 0  # was there a wall hit?
        side = 0  # was a NS or a EW wall hit?

        # calculate step and initial sideDist
        if rayDirX < 0:
            stepX = - 1
            sideDistX = (rayPosX - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - rayPosX) * deltaDistX

        if rayDirY < 0:
            stepY = - 1
            sideDistY = (rayPosY - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY

        # perform DDA
        while hit == 0:
            # jump to next map square, OR in x - direction, OR in y -
            # direction
            if sideDistX < sideDistY:

                sideDistX += deltaDistX
                mapX += stepX
                side = 0
            else:
                sideDistY += deltaDistY
                mapY += stepY
                side = 1

            # Check if ray has hit a wall
            if (worldMap[mapX][mapY] > 0):
                hit = 1
        # Calculate distance projected on camera direction (oblique
        # distance will give fisheye effect !)
        if (side == 0):
            perpWallDist = (abs((mapX - rayPosX + (1 - stepX) // 2) / rayDirX))
        else:
            perpWallDist = (abs((mapY - rayPosY + (1 - stepY) // 2) / rayDirY))

        # Calculate height of line to draw on surface
        if perpWallDist == 0:
            perpWallDist = 0.000001
        lineHeight = abs(int(h / perpWallDist))

        # calculate lowest and highest pixel to fill in current stripe
        drawStart = -lineHeight // 2 + h // 2

        # texturing calculations
        texNum = worldMap[mapX][mapY]  # - 1
        # 1 subtracted from it so that texture 0 can be used!

        # calculate value of wallX
        wallX = 0  # where exactly the wall was hit
        if (side == 1):
            wallX = rayPosX + ((mapY - rayPosY + (
                1 - stepY) // 2) / rayDirY) * rayDirX
        else:
            wallX = rayPosY + ((mapX - rayPosX + (
                1 - stepX) // 2) / rayDirX) * rayDirY
        wallX -= math.floor((wallX))

        # x coordinate on the texture
        texX = int(wallX * float(texWidth))
        if(side == 0 and rayDirX > 0):
            texX = texWidth - texX - 1
        if(side == 1 and rayDirY < 0):
            texX = texWidth - texX - 1

#        if(side == 1):
#            texNum += 8
        if lineHeight > 10000:
            lineHeight = 10000
            drawStart = -10000 // 2 + h // 2
        blits.append((0, texNum, texX, lineHeight, x, drawStart))
        zBuffer.append(perpWallDist)

    # draw sprites
    global sort_camera_x
    global sort_camera_y
    sort_camera_x = camera_x
    sort_camera_y = camera_y
    sprite_positions.sort(key=sprite_key)
    for sprite in sprite_positions:
        # translate sprite position to relative to camera
        spriteX = sprite[0] - camera_x
        spriteY = sprite[1] - camera_y

        invDet = 1.0 / (camera_planex * camera_diry - camera_dirx *
                        camera_planey)  # required for correct matrix multiplication

        transformX = invDet * (
            camera_diry * spriteX - camera_dirx * spriteY)
        transformY = invDet * (-camera_planey * spriteX + camera_planex *
                               spriteY)  # this is actually the depth inside the surface, that what Z is in 3D

        spritesurfaceX = int((w // 2) * (1 + transformX / transformY))

        # calculate height of the sprite on surface
        spriteHeight = abs(int(h / (
            transformY)))  # using "transformY" instead of the real distance prevents fisheye
        # calculate lowest and highest pixel to fill in current stripe
        drawStartY = -spriteHeight // 2 + h // 2

        # calculate width of the sprite
        spriteWidth = abs(int(h / (transformY)))
        drawStartX = -spriteWidth // 2 + spritesurfaceX
        drawEndX = spriteWidth // 2 + spritesurfaceX

        if spriteHeight < 1000:
            for stripe in range(drawStartX, drawEndX):
                texX = int(256 * (stripe - (
                    -spriteWidth // 2 + spritesurfaceX)) * texWidth // spriteWidth) // 256
                # the conditions in the if are:
                # 1) it's in front of camera plane so you don't see things behind you
                # 2) it's on the surface (left)
                # 3) it's on the surface (right)
                # 4) ZBuffer, with perpendicular distance
                if(transformY > 0 and stripe > 0 and stripe < w and transformY < zBuffer[stripe]):
                    blits.append((1, int(sprite[2]), texX, spriteHeight, stripe, drawStartY))
    return blits

if __name__ == '__main__':
    w, h = 640, 480
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
    sprite_positions = [(1.0, 2.0, 3), (1.0, 2.0, 3)]
    camera_x, camera_y = 1.1, 2.2
    camera_dirx, camera_diry = 3.1, 4.2
    camera_planex, camera_planey = 5.1, 6.2
    texWidth, texHeight = 64, 64

    print(draw(
        w, h,
        worldMap,
        sprite_positions,
        camera_x, camera_y,
        camera_dirx, camera_diry,
        camera_planex, camera_planey,
        texWidth, texHeight))
