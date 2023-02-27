import math
from struct import unpack_from
import random

WIDTH = 800
HEIGHT = 600

WIDTH_2 = WIDTH//2
HEIGHT_2 = HEIGHT//2
HEIGHT_INV = 1.0 / WIDTH

TAN_45_DEG = math.tan(math.radians(45))

FLOOR_Y_INV = [1.0 / (y - HEIGHT_2) if y > HEIGHT_2 else 0.0
               for y in range(HEIGHT)]

CEIL_Y_INV = [1.0 / (HEIGHT_2 - y) if y < HEIGHT_2 else 0.0
              for y in range(HEIGHT)]

OSCILLATION = [int(13 + 13 * math.sin(2 * math.pi * (i / 255)))
               for i in range(256)]


class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Sidedef:
    def __init__(self, offset_x, offset_y, upper_texture, lower_texture,
                 middle_texture, sector):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.upper_texture = upper_texture
        self.lower_texture = lower_texture
        self.middle_texture = middle_texture
        self.sector = sector
        self.skyhack = False


class Linedef:
    def __init__(self, vertex_start, vertex_end, special_type, sidedef_front,
                 sidedef_back):
        self.vertex_start = vertex_start
        self.vertex_end = vertex_end
        self.special_type = special_type
        self.sidedef_front = sidedef_front
        self.sidedef_back = sidedef_back


class Sector:
    def __init__(self, floor_h, ceil_h, floor_texture, ceil_texture,
                 light_level, special_type, floor_flat, ceil_flat, ceil_pic):
        self.floor_h = floor_h
        self.ceil_h = ceil_h
        self.floor_texture = floor_texture
        self.ceil_texture = ceil_texture
        self.light_level = light_level
        self.special_type = special_type
        self.floor_flat = floor_flat
        self.ceil_flat = ceil_flat
        self.ceil_pic = ceil_pic

        self.random = [random.random() < 0.5 for i in range(256)]


class SubSector:
    def __init__(self, segs):
        self.segs = segs


class Seg:
    def __init__(self, vertex_start, vertex_end, angle, linedef,
                 sidedef_front, sidedef_back, is_portal, offset,
                 sector_front, sector_back):
        self.vertex_start = vertex_start
        self.vertex_end = vertex_end
        self.angle = angle
        self.linedef = linedef
        self.sidedef_front = sidedef_front
        self.sidedef_back = sidedef_back
        self.is_portal = is_portal
        self.offset = offset
        self.sector_front = sector_front
        self.sector_back = sector_back

        self.length = math.hypot(vertex_end.x - vertex_start.x,
                                 vertex_end.y - vertex_start.y)


class Flat:
    def __init__(self, data):
        self.data = [[[d[64*y+x] for y in range(64)]
                     for x in range(64)] for d in data]

    def get_data(self, frame_count):
        return self.data[(frame_count >> 4) % len(self.data)]


class BSPNode:
    def __init__(self, partition_x, partition_y, change_partition_x,
                 change_partition_y, rchild_id, lchild_id):
        self.partition_x = partition_x
        self.partition_y = partition_y
        self.change_partition_x = change_partition_x
        self.change_partition_y = change_partition_y
        self.rchild_id = rchild_id
        self.lchild_id = lchild_id

    def visit(self,  map_, subsectors=None):
        if subsectors is None:
            subsectors = []
        player = map_.player
        px = player.x - self.partition_x
        py = player.y - self.partition_y

        closest_id, farthest_id = self.lchild_id, self.rchild_id
        if py * self.change_partition_x <= px * self.change_partition_y:
            closest_id, farthest_id = farthest_id, closest_id

        for child_id in (closest_id, farthest_id):
            if child_id < 0:
                subsectors.append(map_.subsectors[child_id & 0x7fff])
            else:
                map_.bspnodes[child_id].visit(map_, subsectors)
        return subsectors


class Thing:
    def __init__(self, x, y, angle, type_):
        self.x = float(x)
        self.y = float(y)
        self.angle = math.radians(90)
        self.type_ = type_


class Player:
    def __init__(self, thing):
        self.x = thing.x
        self.y = thing.y
        self.z = 0.0
        self.angle = thing.angle
        self.floor_h = 48.0
        self.direction = Vec2(math.cos(self.angle), math.sin(self.angle))

    def update(self):
        self.direction = Vec2(math.cos(self.angle), math.sin(self.angle))


class Texture:
    def __init__(self, name, data, width, height):
        self.name = name
        self.data = data
        self.width = width
        self.height = height


class Picture:
    def __init__(self, data):
        width, height, offset_x, offset_y = unpack_from('<HHhh', data, 0)
        self.width, self.height = width, height
        self.data = [[0 for k in range(height)] for j in range(width)]

        for j in range(width):
            col_offset, = unpack_from('<H', data, 8+4*j)
            y_offset, = unpack_from('<B', data, col_offset)
            length, _ = unpack_from('<BB', data, col_offset+1)
            for y in range(length):
                self.data[j][y+y_offset] = data[col_offset+3+y]


class Colormap:
    def __init__(self, data):
        self.data = []
        for i in range(256):
            self.data.append(data[i])


class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def dot(self, v):
        return self.x * v.x + self.y * v.y


class Map:
    def __init__(self, filepath, map_):
        self.extract_entries(filepath, map_)

        self.extract_palette()
        self.extract_colormaps()
        self.extract_patches()
        self.extract_textures()
        self.extract_vertices()
        self.extract_sectors()
        self.extract_sidedefs()
        self.extract_linedefs()
        self.extract_segs()
        self.extract_subsectors()
        self.extract_bspnodes()
        self.extract_things()

        self.player = Player(self.things[0])

    def extract_entries(self, filepath, mapname):
        data = open(filepath, 'rb').read()
        nentries, dir_offset = unpack_from('<II', data, 4)

        self.entry_data = {}
        inmap = False
        bmapname = bytes([ord(c) for c in mapname])  # TODO encoding='acscii'?

        # filter entries that apply to map
        for i in range(nentries):
            offset, length, name = unpack_from('<II8s', data, dir_offset+i*16)
            name = name.rstrip(b'\0')

            if name == bmapname:
                inmap = True
            elif ((inmap or name in (b'PLAYPAL', b'COLORMAP')) and
                    name not in self.entry_data):
                self.entry_data[name.upper()] = data[offset: offset+length]

    def extract_vertices(self):
        self.vertices = []
        data = self.entry_data[b'VERTEXES']
        for j in range(len(data)//4):
            x, y = unpack_from('<hh', data, j*4)
            self.vertices.append(Vertex(x, y))

    def extract_linedefs(self):
        self.linedefs = []
        data = self.entry_data[b'LINEDEFS']
        for j in range(len(data)//14):
            (vertex_start, vertex_end, _, special_type, _, sidedef_front,
                sidedef_back) = unpack_from('<HHHHHHH', data, j*14)
            vertex_a = self.vertices[vertex_start]
            vertex_b = self.vertices[vertex_end]
            sidedef_a = self.sidedefs[sidedef_front]
            if sidedef_back != 0xffff:
                sidedef_b = self.sidedefs[sidedef_back]
            else:
                sidedef_b = None
            linedef = Linedef(vertex_a, vertex_b, special_type,
                              sidedef_a, sidedef_b)
            self.linedefs.append(linedef)

        # sky hack
        for linedef in self.linedefs:
            if (linedef.sidedef_front is not None and
                    linedef.sidedef_front.sector.ceil_pic is not None and
                    linedef.sidedef_back is not None and
                    linedef.sidedef_back.sector.ceil_pic is not None):
                linedef.sidedef_front.skyhack = True

    def extract_sidedefs(self):
        self.sidedefs = []
        data = self.entry_data[b'SIDEDEFS']
        for j in range(len(data)//30):
            (offset_x, offset_y, upper_texture_name, lower_texture_name,
                middle_texture_name, sector_nr) = \
                    unpack_from('<HH8s8s8sH', data, j*30)

            upper_texture = self.textures.get(upper_texture_name.rstrip(b'\0'))
            lower_texture = self.textures.get(lower_texture_name.rstrip(b'\0'))
            middle_texture = \
                self.textures.get(middle_texture_name.rstrip(b'\0'))
            sector = self.sectors[sector_nr]
            sidedef = Sidedef(offset_x, offset_y, upper_texture, lower_texture,
                              middle_texture, sector)
            self.sidedefs.append(sidedef)

    def extract_sectors(self):
        self.sectors = []
        data = self.entry_data[b'SECTORS']
        for j in range(len(data)//26):
            (floor_h, ceil_h, floor_texture, ceil_texture, light_level,
                special_type, _) = \
                    unpack_from('<hh8s8sHhh', data, j*26)
            light_level &= 0xff
            floor_texture = floor_texture.rstrip(b'\0')
            if floor_texture.startswith(b'NUKAGE'):
                names = [b'NUKAGE1', b'NUKAGE2', b'NUKAGE3']
                floor_flat = Flat([self.entry_data[name] for name in names])
            else:
                floor_flat = Flat([self.entry_data[floor_texture]])
            ceil_texture = ceil_texture.rstrip(b'\0')
            ceil_flat = Flat([self.entry_data[ceil_texture]])
            ceil_pic = None
            if b'F_SKY' in ceil_texture:
                pic_data = self.entry_data[ceil_texture.replace(b'F_', b'')]
                ceil_pic = Picture(pic_data)
            sector = Sector(floor_h, ceil_h, floor_texture, ceil_texture,
                            light_level, special_type, floor_flat, ceil_flat,
                            ceil_pic)
            self.sectors.append(sector)

    def extract_patches(self):
        self.patches = []
        data = self.entry_data[b'PNAMES']
        n_pnames, = unpack_from('<i', data, 0)
        for j in range(n_pnames):
            patch_name = data[4+j*8:4+(j+1)*8].rstrip(b'\0').upper()
            try:
                patch = Picture(self.entry_data[patch_name])
            except KeyError:
                patch = None
            self.patches.append(patch)

    def extract_textures(self):
        self.textures = {}
        data = self.entry_data[b'TEXTURE1']
        n_textures, = unpack_from('<i', data, 0)
        for j in range(n_textures):
            offset, = unpack_from('<i', data, 4+j*4)
            (name, _, width, height, _, n_patches) = \
                unpack_from('<8sIHHIH', data, offset)
            name = name.rstrip(b'\0')
            patch = [[0 for k in range(height)] for j in range(width)]
            for k in range(n_patches):
                offset_x, offset_y, patch_index, _, _ = \
                    unpack_from('<hhhhh', data, offset+22+k*10)
                pic = self.patches[patch_index]
                for m in range(pic.width):
                    for n in range(pic.height):
                        x = m+offset_x
                        y = n+offset_y
                        if 0 <= x < width and 0 <= y < height:
                            patch[x][y] = pic.data[m][n]
            self.textures[name] = Texture(name, patch, width, height)

    def extract_palette(self):
        self.palette = []
        data = self.entry_data[b'PLAYPAL']
        for j in range(256):
            r, g, b = unpack_from('<BBB', data, 3*j)
            self.palette.append((r, g, b))

    def extract_colormaps(self):
        self.colormaps = []
        data = self.entry_data[b'COLORMAP']
        for j in range(34):
            self.colormaps.append(Colormap(data[256*j:256*(j+1)]))

    def extract_segs(self):
        self.segs = []
        data = self.entry_data[b'SEGS']
        for j in range(len(data)//12):
            vertex_start, vertex_end, angle, linedef_nr, direction, offset = \
                unpack_from('<HHhHHh', data, j*12)
            vertex_a = self.vertices[vertex_start]
            vertex_b = self.vertices[vertex_end]
            linedef = self.linedefs[linedef_nr]
            sidedef_back = None
            is_portal = False
            if direction == 0:
                sidedef_front = linedef.sidedef_front
                if linedef.sidedef_back is not None:
                    sidedef_back = linedef.sidedef_back
                    is_portal = True
            else:
                sidedef_front = linedef.sidedef_back
                if linedef.sidedef_front is not None:
                    sidedef_back = linedef.sidedef_front
                    is_portal = True
            sector_front = sidedef_front.sector
            if sidedef_back is not None:
                sector_back = sidedef_back.sector
            else:
                sector_back = None
            self.segs.append(Seg(vertex_a, vertex_b, angle, linedef,
                                 sidedef_front, sidedef_back, is_portal,
                                 offset, sector_front, sector_back))

    def extract_subsectors(self):
        self.subsectors = []
        data = self.entry_data[b'SSECTORS']
        for j in range(len(data)//4):
            seg_count, first_seg = unpack_from('<HH', data, j*4)
            segs = self.segs[first_seg:first_seg+seg_count]
            self.subsectors.append(SubSector(segs))

    def extract_bspnodes(self):
        self.bspnodes = []
        data = self.entry_data[b'NODES']
        for j in range(len(data)//28):
            (partition_x, partition_y, change_partition_x, change_partition_y,
             _, _, _,  _, _, _, _, _, rchild_id, lchild_id) = \
                unpack_from('<hhhhhhhhhhhhhh', data, j*28)
            bspnode = BSPNode(partition_x, partition_y, change_partition_x,
                              change_partition_y, rchild_id, lchild_id)
            self.bspnodes.append(bspnode)

    def extract_things(self):
        self.things = []
        data = self.entry_data[b'THINGS']
        for j in range(len(data)//10):
            x, y, angle, type_, _ = unpack_from('<hhhhh', data, j*10)
            self.things.append(Thing(x, y, angle, type_))


class ClipBufferNode:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.occluded = False
        self.left = None
        self.right = None
        self.partitioned = False

    def checkSpan(self, start, end, result, add):
        # span completely occluded by node
        if self.occluded and start >= self.start and end <= self.end:
            return

        # no overlap, so node does not apply to span
        if start > self.end or end < self.start:
            return

        # reduce span to overlap with node
        if start <= self.start:
            start = self.start

        if end >= self.end:
            end = self.end

        if add:
            # unpartitioned, unoccluded node covered fully by span
            if (not self.occluded and not self.partitioned and
                    start <= self.start and end >= self.end):
                result.append(start)
                result.append(end)
                self.occluded = True
                return

            # partition if needed
            if not self.partitioned:
                if start == self.start:
                    self.partitionPoint = end
                else:
                    self.partitionPoint = start - 1

                self.left = ClipBufferNode(self.start, self.partitionPoint)
                self.right = ClipBufferNode(self.partitionPoint + 1, self.end)
                self.partitioned = True

        else:
            if not self.partitioned:
                result.append(start)
                result.append(end)
                return

        # recurse into left and right
        if start <= self.partitionPoint and end <= self.partitionPoint:
            self.left.checkSpan(start, end, result, add)

        elif start <= self.partitionPoint and end > self.partitionPoint:
            self.left.checkSpan(start, self.partitionPoint, result, add)
            self.right.checkSpan(self.partitionPoint + 1, end, result, add)

        elif start > self.partitionPoint and end > self.partitionPoint:
            self.right.checkSpan(start, end, result, add)

        # left and right occluded, so node fully occluded
        if add and self.left.occluded and self.right.occluded:
            self.occluded = True


def get_special_light(sector, frame_count):
    special_type = sector.special_type

    if special_type in (1, 17):
        if sector.random[(frame_count & 0xff0) >> 4]:
            return 10
    elif special_type in (2, 12):
        if (frame_count % 120) < 60:
            return 10
    elif special_type in (3, 13):
        if (frame_count % 240) < 120:
            return 10
    elif special_type == 8:
        return OSCILLATION[frame_count & 0xff]

    return 0


def get_wall_colormap(colormaps, currentZ, seg, frame_count):
    sector = seg.sector_front

    colorMapIndex = int((currentZ - 5) * 0.05)
    colorMapIndex = min(colorMapIndex, 32 - (sector.light_level >> 3))

    colorMapIndex += ((((seg.angle + 8192) & 0x7fff) - 16384) & 0x7fff) // 3200
    colorMapIndex += get_special_light(sector, frame_count)

    colorMapIndex = max(min(colorMapIndex, 31), 0)
    return colormaps[colorMapIndex]


def get_flat_colormap(colormaps, currentZ, seg, frame_count):
    sector = seg.sector_front

    colorMapIndex = int((currentZ - 5) * 0.05)
    colorMapIndex = min(colorMapIndex, 32 - (sector.light_level >> 3))

    colorMapIndex += get_special_light(sector, frame_count)

    colorMapIndex = max(min(colorMapIndex, 31), 0)
    return colormaps[colorMapIndex]


def draw_wall_col(drawsurf, x, middleMinY, middleMaxY, wallTexture,
                  currentTextureX, currentZ, middleTextureY,
                  middleTextureYStep, colormap):
    width = wallTexture.width
    height = wallTexture.height
    wallTextureData = wallTexture.data

    tx = int(currentTextureX * currentZ) % width
    for y in range(middleMinY, middleMaxY):
        ty = int(middleTextureY) % height
        drawsurf[y*WIDTH+x] = colormap.data[wallTextureData[tx][ty]]
        middleTextureY += middleTextureYStep


def draw_flat_col(drawsurf, x, ceilMin, ceilMax, seg, player, flatTexture,
                  flat_h, INV, sign, colormaps, frame_count):
    for y in range(ceilMin, ceilMax):
        z = sign * WIDTH_2 * (-flat_h + player.z) * INV[y]

        colormap = get_flat_colormap(colormaps, z, seg, frame_count)

        playerDir = player.direction
        px = playerDir.x * z + player.x
        py = playerDir.y * z + player.y

        lateralLength = TAN_45_DEG * z

        leftX = -playerDir.y * lateralLength + px
        leftY = playerDir.x * lateralLength + py
        rightX = playerDir.y * lateralLength + px
        rightY = -playerDir.x * lateralLength + py

        dx = (rightX - leftX) * HEIGHT_INV
        dy = (rightY - leftY) * HEIGHT_INV

        tx = int(leftX + dx * x) & 0x3f
        ty = int(leftY + dy * x) & 0x3f

        drawsurf[y*WIDTH+x] = colormap.data[flatTexture[tx][ty]]


def draw_sky_col(drawsurf, x, upperMinY, upperMaxY, seg, player):
    ceil_pic = seg.sector_front.ceil_pic
    ceilingTextureWidth = ceil_pic.width
    ceilingTextureHeight = ceil_pic.height
    ceilTextureData = ceil_pic.data

    normPlayerAngle = player.angle % (2 * math.pi)
    if normPlayerAngle < 0:
        normPlayerAngle += 2 * math.pi

    textureOffsetX = ceilingTextureWidth * (normPlayerAngle / (math.pi * 0.5))
    dx = ceilingTextureWidth / WIDTH
    dy = ceilingTextureHeight / (WIDTH//2)

    for y in range(upperMinY, upperMaxY):
        tx = int(dx * x - textureOffsetX) % ceilingTextureWidth
        ty = int(y * dy) % ceilingTextureHeight
        drawsurf[y*WIDTH+x] = ceilTextureData[tx][ty]


def draw_seg(seg, map_, drawsurf, scrXA, scrXB, cbuffer, za, zb, textureX0,
             textureX1, frontSidedef, lowerOcclusion, upperOcclusion,
             frame_count):
    # get non-occluded clips from cbuffer
    cbufferResult = []
    cbuffer.checkSpan(scrXA, scrXB, cbufferResult, not seg.is_portal)

    # no visible clips
    if not cbufferResult:
        return

    player = map_.player
    colormaps = map_.colormaps
    sector_front = seg.sector_front
    sector_back = seg.sector_back

    # front side
    frontCeil = sector_front.ceil_h - player.z
    frontFloor = sector_front.floor_h - player.z
    scrYAFrontCeil = WIDTH_2 * (frontCeil / -za) + HEIGHT_2
    scrYAFrontFloor = WIDTH_2 * (frontFloor / -za) + HEIGHT_2
    scrYBFrontCeil = WIDTH_2 * (frontCeil / -zb) + HEIGHT_2
    scrYBFrontFloor = WIDTH_2 * (frontFloor / -zb) + HEIGHT_2

    # back side
    if seg.is_portal:
        backCeil = sector_back.ceil_h - player.z
        backFloor = sector_back.floor_h - player.z
        scrYABackCeil = WIDTH_2 * (backCeil / -za) + HEIGHT_2
        scrYABackFloor = WIDTH_2 * (backFloor / -za) + HEIGHT_2
        scrYBBackCeil = WIDTH_2 * (backCeil / -zb) + HEIGHT_2
        scrYBBackFloor = WIDTH_2 * (backFloor / -zb) + HEIGHT_2
        hasLowerWall = backFloor > frontFloor
        hasUpperWall = backCeil < frontCeil
    else:
        backCeil = 0
        backFloor = 0
        scrYABackCeil = 0
        scrYABackFloor = 0
        scrYBBackCeil = 0
        scrYBBackFloor = 0
        hasLowerWall = False
        hasUpperWall = False

    # calculate steps
    dxInv = 1.0 / (scrXB - scrXA)
    zInvStep = (1 / zb - 1 / za) * dxInv
    textureXStep = (textureX1 / zb - textureX0 / za) * dxInv
    middleCeilStep = (scrYBFrontCeil - scrYAFrontCeil) * dxInv
    middlefloorStep = (scrYBFrontFloor - scrYAFrontFloor) * dxInv
    lowerCeilStep = (scrYBBackFloor - scrYABackFloor) * dxInv
    lowerfloorStep = (scrYBFrontFloor - scrYAFrontFloor) * dxInv
    upperCeilStep = (scrYBFrontCeil - scrYAFrontCeil) * dxInv
    upperFloorStep = (scrYBBackCeil - scrYABackCeil) * dxInv

    # loop over non-occluded seg clips
    for clip in range(0, len(cbufferResult), 2):
        clipLeft = cbufferResult[clip]
        clipRight = cbufferResult[clip+1]

        currentMiddleCeil = scrYAFrontCeil
        currentMiddleFloor = scrYAFrontFloor

        currentLowerCeil = scrYABackFloor
        currentLowerFloor = scrYAFrontFloor
        currentUpperCeil = scrYAFrontCeil
        currentUpperFloor = scrYABackCeil

        currentZInv = 1 / za
        currentTextureX = textureX0 / za
        scrLeft = scrXA
        scrRight = scrXB

        # narrow to clip
        if scrLeft < clipLeft:
            dif = clipLeft - scrXA
            currentTextureX += dif * textureXStep
            currentZInv += dif * zInvStep
            currentMiddleCeil += dif * middleCeilStep
            currentMiddleFloor += dif * middlefloorStep

            if hasLowerWall:
                currentLowerCeil += dif * lowerCeilStep
                currentLowerFloor += dif * lowerfloorStep

            if hasUpperWall:
                currentUpperCeil += dif * upperCeilStep
                currentUpperFloor += dif * upperFloorStep

            scrLeft = clipLeft

        if scrRight > clipRight:
            scrRight = clipRight

        # draw clip column-wise
        for x in range(scrLeft, scrRight+1):
            currentZ = 1.0 / currentZInv
            colormap = get_wall_colormap(colormaps, currentZ, seg, frame_count)

            middleMaxY = int(currentMiddleFloor)
            middleMinY = int(currentMiddleCeil)
            middleDy = middleMaxY - middleMinY

            if middleDy == 0:  # on collision with wall
                middleTextureYStep = 0
            else:
                middleTextureYStep = (frontCeil - frontFloor) / middleDy
            middleTextureY = frontSidedef.offset_y

            if middleMinY < lowerOcclusion[x]:
                dif = lowerOcclusion[x] - middleMinY
                middleTextureY = \
                    dif * middleTextureYStep + frontSidedef.offset_y
                middleMinY = lowerOcclusion[x]

            middleMaxY = min(middleMaxY, upperOcclusion[x])

            # middle wall
            middle_texture = frontSidedef.middle_texture
            if not seg.is_portal and middle_texture is not None:
                draw_wall_col(drawsurf, x, middleMinY, middleMaxY,
                              middle_texture, currentTextureX, currentZ,
                              middleTextureY, middleTextureYStep, colormap)

            # floor
            ceilMin = int(max(lowerOcclusion[x], middleMaxY))
            if ceilMin < upperOcclusion[x]:
                floor_flat = sector_front.floor_flat.get_data(frame_count)
                draw_flat_col(drawsurf, x, ceilMin, upperOcclusion[x], seg,
                              player, floor_flat, sector_front.floor_h,
                              FLOOR_Y_INV, 1, colormaps, frame_count)
                upperOcclusion[x] = ceilMin

            # lower wall
            if hasLowerWall:
                lowerMaxY = int(currentLowerFloor)
                lowerMinY = int(currentLowerCeil)

                lowerDy = lowerMaxY - lowerMinY
                lowerTextureYStep = (backFloor - frontFloor) / lowerDy
                lowerTextureY = frontSidedef.offset_y

                if lowerMinY < lowerOcclusion[x]:
                    dif = lowerOcclusion[x] - lowerMinY
                    lowerTextureY = \
                        dif * lowerTextureYStep + frontSidedef.offset_y
                    lowerMinY = lowerOcclusion[x]

                lowerMaxY = min(lowerMaxY, upperOcclusion[x])

                lower_texture = frontSidedef.lower_texture
                if lower_texture is not None:
                    draw_wall_col(drawsurf, x, lowerMinY, lowerMaxY,
                                  lower_texture, currentTextureX, currentZ,
                                  lowerTextureY, lowerTextureYStep, colormap)

                if lowerMinY < upperOcclusion[x]:
                    upperOcclusion[x] = lowerMinY

                currentLowerCeil += lowerCeilStep
                currentLowerFloor += lowerfloorStep

            # ceil
            ceilMax = int(min(upperOcclusion[x], middleMinY))
            if ceilMax > lowerOcclusion[x]:
                # sky
                if sector_front.ceil_pic is not None:
                    draw_sky_col(drawsurf, x, lowerOcclusion[x], ceilMax, seg,
                                 player)
                # ceil
                else:
                    ceil_flat = sector_front.ceil_flat.get_data(frame_count)
                    draw_flat_col(drawsurf, x, lowerOcclusion[x], ceilMax, seg,
                                  player, ceil_flat, sector_front.ceil_h,
                                  CEIL_Y_INV, -1, colormaps, frame_count)

                lowerOcclusion[x] = middleMinY

            # upper wall
            if hasUpperWall:
                upperMaxY = int(currentUpperFloor)
                upperMinY = int(currentUpperCeil)

                upperDy = upperMaxY - upperMinY
                upperTextureYStep = (frontCeil - backCeil) / upperDy
                upperTextureY = frontSidedef.offset_y

                if upperMinY < lowerOcclusion[x]:
                    dif = lowerOcclusion[x] - upperMinY
                    upperTextureY = \
                        dif * upperTextureYStep + frontSidedef.offset_y
                    upperMinY = lowerOcclusion[x]

                upperMaxY = min(upperMaxY, upperOcclusion[x])
                upper_texture = frontSidedef.upper_texture

                # sky
                if frontSidedef.skyhack or upper_texture is None:
                    if sector_front.ceil_pic is not None:
                        draw_sky_col(drawsurf, x, upperMinY, upperMaxY, seg,
                                     player)
                # wall
                else:
                    draw_wall_col(drawsurf, x, upperMinY, upperMaxY,
                                  upper_texture, currentTextureX, currentZ,
                                  upperTextureY, upperTextureYStep, colormap)

                if upperMaxY > lowerOcclusion[x]:
                    lowerOcclusion[x] = upperMaxY

                currentUpperCeil += upperCeilStep
                currentUpperFloor += upperFloorStep

            currentMiddleCeil += middleCeilStep
            currentMiddleFloor += middlefloorStep
            currentZInv += zInvStep
            currentTextureX += textureXStep


def render(map_, frame_count):
    drawsurf = bytearray(WIDTH * HEIGHT)

    lowerOcclusion = WIDTH * [0]
    upperOcclusion = WIDTH * [HEIGHT]

    cbuffer = ClipBufferNode(0, WIDTH-1)

    subsectors = map_.bspnodes[-1].visit(map_)

    player = map_.player
    player.floor_h = subsectors[0].segs[0].sector_front.floor_h

    for subsector in subsectors:
        if cbuffer.occluded:
            break

        for seg in subsector.segs:
            if cbuffer.occluded:
                break

            # backface/frustrum culling
            pa = seg.vertex_start
            pb = seg.vertex_end
            v0 = Vec2(pa.x - player.x, pa.y - player.y)
            v1 = Vec2(pb.x - player.x, pb.y - player.y)
            v2 = Vec2(player.direction.x, player.direction.y)
            za = v2.dot(v0)
            zb = v2.dot(v1)
            v3 = Vec2(-v2.y, v2.x)
            xa = v3.dot(v0)
            xb = v3.dot(v1)

            if not (za <= 0.1 and zb <= 0.1):
                frontSidedef = seg.sidedef_front
                textureX0 = seg.offset + frontSidedef.offset_x
                textureX1 = seg.offset + seg.length + frontSidedef.offset_x

                if za <= 0.1:
                    p = (zb - 0.1) / (zb - za)
                    xa = xb + p * (xa - xb)
                    textureX0 = textureX1 + p * (textureX0 - textureX1)
                    za = 0.1

                elif zb <= 0.1:
                    p = (za - 0.1) / (za - zb)
                    xb = xa + p * (xb - xa)
                    textureX1 = textureX0 + p * (textureX1 - textureX0)
                    zb = 0.1

                scrXA = int(WIDTH_2 * xa / -za) + WIDTH_2
                scrXB = int(WIDTH_2 * xb / -zb) + WIDTH_2

                if scrXA < scrXB:
                    draw_seg(seg, map_, drawsurf, scrXA, scrXB, cbuffer, za,
                             zb, textureX0, textureX1, frontSidedef,
                             lowerOcclusion, upperOcclusion, frame_count)

    return drawsurf


if __name__ == '__main__':
    map_ = Map('DOOM1.WAD', 'E1M1')
    map_.player.update()
    render(map_, 0)
