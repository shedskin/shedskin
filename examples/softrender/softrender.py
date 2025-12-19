import math


def saturate(val):
    return max(0.0, min(val, 1.0))


class Bitmap:
    def __init__(self, width, height, components=None):
        self.width, self.height = width, height
        self.components = components or bytearray(width * height * 4)
        self.reset = bytearray(width * height * 4)

    def clear(self):
        self.components[:] = self.reset


class Vector4:
    def __init__(self, x, y, z, w=1.0):
        self.x, self.y, self.z, self.w = x, y, z, w

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

    def normalized(self):
        return self.mul(1 / self.length())

    def mul(self, r):
        return Vector4(self.x * r, self.y * r, self.z * r, self.w * r)

    def sub(self, r):
        return Vector4(self.x - r.x, self.y - r.y, self.z - r.z, self.w - r.w)

    def add(self, r):
        return Vector4(self.x + r.x, self.y + r.y, self.z + r.z, self.w + r.w)

    def dot(self, r):
        return self.x * r.x + self.y * r.y + self.z * r.z + self.w * r.w

    def cross(self, r):
        return Vector4(self.y * r.z - self.z * r.y, self.z * r.x - self.x * r.z, self.x * r.y - self.y * r.x, 0)

    def lerp(self, dest, lerpFactor):
        return dest.sub(self).mul(lerpFactor).add(self)


class Matrix4:
    def __init__(self):
        self.m = [[0.0 for i in range(4)] for j in range(4)]

    def init_scale(self, x, y, z):
        m = self.m
        m[0][0] = x; m[0][1] = 0; m[0][2] = 0; m[0][3] = 0
        m[1][0] = 0; m[1][1] = y; m[1][2] = 0; m[1][3] = 0
        m[2][0] = 0; m[2][1] = 0; m[2][2] = z; m[2][3] = 0
        m[3][0] = 0; m[3][1] = 0; m[3][2] = 0; m[3][3] = 1
        return self

    def init_translation(self, x, y, z):
        m = self.m
        m[0][0] = 1; m[0][1] = 0; m[0][2] = 0; m[0][3] = x
        m[1][0] = 0; m[1][1] = 1; m[1][2] = 0; m[1][3] = y
        m[2][0] = 0; m[2][1] = 0; m[2][2] = 1; m[2][3] = z
        m[3][0] = 0; m[3][1] = 0; m[3][2] = 0; m[3][3] = 1
        return self

    def init_rotation(self, f, u, r):
        m = self.m
        m[0][0] = r.x; m[0][1] = r.y; m[0][2] = r.z; m[0][3] = 0
        m[1][0] = u.x; m[1][1] = u.y; m[1][2] = u.z; m[1][3] = 0
        m[2][0] = f.x; m[2][1] = f.y; m[2][2] = f.z; m[2][3] = 0
        m[3][0] = 0;   m[3][1] = 0;   m[3][2] = 0;   m[3][3] = 1
        return self

    def init_screenspace_transform(self, halfWidth, halfHeight):
        m = self.m
        m[0][0] = halfWidth; m[0][1] = 0;           m[0][2] = 0; m[0][3] = halfWidth - 0.5
        m[1][0] = 0;         m[1][1] = -halfHeight; m[1][2] = 0; m[1][3] = halfHeight - 0.5
        m[2][0] = 0;         m[2][1] = 0;           m[2][2] = 1; m[2][3] = 0
        m[3][0] = 0;         m[3][1] = 0;           m[3][2] = 0; m[3][3] = 1
        return self

    def init_perspective(self, fov, aspectRatio, zNear, zFar):
        tanHalfFOV = math.tan(fov / 2)
        zRange = zNear - zFar
        m = self.m
        m[0][0] = 1.0 / (tanHalfFOV * aspectRatio); m[0][1] = 0;                m[0][2] = 0;                     m[0][3] = 0
        m[1][0] = 0;                                m[1][1] = 1.0 / tanHalfFOV; m[1][2] = 0;                     m[1][3] = 0
        m[2][0] = 0;                                m[2][1] = 0;                m[2][2] = (-zNear -zFar)/zRange; m[2][3] = 2 * zFar * zNear / zRange
        m[3][0] = 0;                                m[3][1] = 0;                m[3][2] = 1;                     m[3][3] = 0
        return self

    def transform(self, r):
        m = self.m
        return Vector4(m[0][0] * r.x + m[0][1] * r.y + m[0][2] * r.z + m[0][3] * r.w,
                       m[1][0] * r.x + m[1][1] * r.y + m[1][2] * r.z + m[1][3] * r.w,
                       m[2][0] * r.x + m[2][1] * r.y + m[2][2] * r.z + m[2][3] * r.w,
                       m[3][0] * r.x + m[3][1] * r.y + m[3][2] * r.z + m[3][3] * r.w)

    def mul(self, other):
        m = self.m
        r = other.m
        res = Matrix4()
        for i in range(4):
            for j in range(4):
                res.m[i][j] = m[i][0] * r[0][j] + m[i][1] * r[1][j] + m[i][2] * r[2][j] + m[i][3] * r[3][j]
        return res


class Quaternion:
    def __init__(self, x, y, z, w):
        self.x, self.y, self.z, self.w = x, y, z, w

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

    def normalized(self):
        length = self.length()
        return Quaternion(self.x / length, self.y / length, self.z / length, self.w / length)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def mul(self, r):
        return Quaternion(
            self.x * r.w + self.w * r.x + self.y * r.z - self.z * r.y,
            self.y * r.w + self.w * r.y + self.z * r.x - self.x * r.z,
            self.z * r.w + self.w * r.z + self.x * r.y - self.y * r.x,
            self.w * r.w - self.x * r.x - self.y * r.y - self.z * r.z)

    def to_rotation_matrix(self):
        return Matrix4().init_rotation(
            Vector4(2.0 * (self.x * self.z - self.w * self.y), 2.0 * (self.y * self.z + self.w * self.x), 1.0 - 2.0 * (self.x * self.x + self.y * self.y)),
            Vector4(2.0 * (self.x * self.y + self.w * self.z), 1.0 - 2.0 * (self.x * self.x + self.z * self.z), 2.0 * (self.y * self.z - self.w * self.x)),
            Vector4(1.0 - 2.0 * (self.y * self.y + self.z * self.z), 2.0 * (self.x * self.y - self.w * self.z), 2.0 * (self.x * self.z + self.w * self.y)),
        )


# TODO static_method not exported in extmod
def quaternion_from_axis_angle(axis, angle):
    sin_half_angle = math.sin(angle / 2)
    cos_half_angle = math.cos(angle / 2)
    return Quaternion(axis.x * sin_half_angle, axis.y * sin_half_angle, axis.z * sin_half_angle, cos_half_angle)


class Vertex:
    def __init__(self, pos, texCoords, normal):
        self.pos = pos
        self.texCoords = texCoords
        self.normal = normal

    def transform(self, transform, normalTransform=None):
        if normalTransform:
            normal = normalTransform.transform(self.normal).normalized()
        else:
            normal = self.normal
        return Vertex(transform.transform(self.pos), self.texCoords, normal)

    def inside_view_frustum(self):
        return (abs(self.pos.x) <= abs(self.pos.w) and
                abs(self.pos.y) <= abs(self.pos.w) and
                abs(self.pos.z) <= abs(self.pos.w))

    def perspective_divide(self):
        w = self.pos.w
        return Vertex(Vector4(self.pos.x/w, self.pos.y/w, self.pos.z/w, w), self.texCoords, self.normal)

    def triangle_area_times_two(self, b, c):
        return ((b.pos.x - self.pos.x) * (c.pos.y - self.pos.y)) - ((c.pos.x - self.pos.x) * (b.pos.y - self.pos.y))

    def get(self, index):
        if index == 0:
            return self.pos.x
        elif index == 1:
            return self.pos.y
        elif index == 2:
            return self.pos.z
        elif index == 3:
            return self.pos.w
        raise IndexError

    def lerp(self, other, lerpAmt):
        return Vertex(self.pos.lerp(other.pos, lerpAmt),
                      self.texCoords.lerp(other.texCoords, lerpAmt),
                      self.normal.lerp(other.normal, lerpAmt))


class Transform:
    def __init__(self, pos=None, rot=None, scale=None):
        self.pos = pos or Vector4(0.0, 0.0, 0.0, 0.0)
        self.rot = rot or Quaternion(0.0, 0.0, 0.0, 1.0)
        self.scale = scale or Vector4(1.0, 1.0, 1.0, 1.0)

    def rotate(self, rotation):
        return Transform(self.pos, rotation.mul(self.rot).normalized(), self.scale)

    def get_transformation(self):
        translationMatrix = Matrix4().init_translation(self.pos.x , self.pos.y, self.pos.z)
        rotationMatrix = self.rot.to_rotation_matrix()
        scaleMatrix = Matrix4().init_scale(self.scale.x, self.scale.y, self.scale.z)

        return translationMatrix.mul(rotationMatrix.mul(scaleMatrix))


class Camera:
    def __init__(self, projection):
        self.projection = projection
        self.transform = Transform()

    def get_view_projection(self):
        camera_rotation = self.transform.rot.conjugate().to_rotation_matrix()
        camera_pos = self.transform.pos.mul(-1)
        camera_translation = Matrix4().init_translation(camera_pos.x, camera_pos.y, camera_pos.z)

        return self.projection.mul(camera_rotation.mul(camera_translation))


class Mesh:
    def __init__(self, filename, scale=1):
        self.vertices = []
        self.faces = []

        vertices = []
        texcoords = []
        normals = []

        for line in open(filename):
            if line.startswith('v '):
                x, y, z = map(float, line[2:].split())
                vertices.append((x / scale, y / scale, z / scale))

            elif line.startswith('vt '):
                tu, tv = map(float, line[2:].split())
                texcoords.append((tu, 1.0 - tv))

            elif line.startswith('vn '):
                x, y, z = map(float, line[2:].split())
                normals.append((x, y, z))

        index = {}  # create unique vertices for vertex-texcoords-normal combinations
        for line in open(filename):
            if line.startswith('f '):
                idcs = []
                for token in line[2:].split():
                    v, t, n = map(int, token.split('/'))
                    if not normals:
                        n = 0
                    idx = index.get((v, t, n), -1)
                    if idx == -1:
                        x, y, z = vertices[v-1]
                        tu, tv = texcoords[t-1]
                        a = b = c = 0
                        if normals and n-1 < len(normals):
                            a, b, c = normals[n-1]
                        vertex = Vertex(Vector4(x, y, z, 1), Vector4(tu, tv, 0, 0), Vector4(a, b, c, 0))
                        index[v, t, n] = idx = len(self.vertices)
                        self.vertices.append(vertex)
                    idcs.append(idx)

                for i in range(len(idcs)-2):
                    self.faces.extend([idcs[0], idcs[i+1], idcs[i+2]])

        if not normals:  # calculate vertex normals if not specified
            pos_normal = {}

            for i in range(0, len(self.faces), 3):
                i0, i1, i2 = self.faces[i:i+3]

                v1 = self.vertices[i1].pos.sub(self.vertices[i0].pos)
                v2 = self.vertices[i2].pos.sub(self.vertices[i0].pos)
                normal = v1.cross(v2).normalized()

                for j in (i0, i1, i2):
                    vtx = self.vertices[j]
                    key = (vtx.pos.x, vtx.pos.y, vtx.pos.z)
                    if key in pos_normal:
                        havenormal = pos_normal[key]
                    else:
                        havenormal = Vector4(0, 0, 0, 0)
                    pos_normal[key] = havenormal.add(normal)

            for vtx in self.vertices:
                vtx.normal = pos_normal[vtx.pos.x, vtx.pos.y, vtx.pos.z].normalized()

    def draw(self, context, view_projection, transform, texture, lightDir):
        mvp = view_projection.mul(transform)

        for i in range(0, len(self.faces), 3):
            context.draw_triangle(
                self.vertices[self.faces[i  ]].transform(mvp, transform),
                self.vertices[self.faces[i+1]].transform(mvp, transform),
                self.vertices[self.faces[i+2]].transform(mvp, transform),
                texture,
                lightDir
            )


class Gradients:
    def __init__(self, minYVert, midYVert, maxYVert, lightDir):
        self.depth = [minYVert.pos.z, midYVert.pos.z, maxYVert.pos.z]

        self.oneOverZ = [
            1.0 / minYVert.pos.w,
            1.0 / midYVert.pos.w,
            1.0 / maxYVert.pos.w
        ]

        self.lightAmt = [
            saturate(minYVert.normal.dot(lightDir)) * 0.5 + 0.5,
            saturate(midYVert.normal.dot(lightDir)) * 0.5 + 0.5,
            saturate(maxYVert.normal.dot(lightDir)) * 0.5 + 0.5,
        ]

        self.texCoordX = [
            minYVert.texCoords.x * self.oneOverZ[0],
            midYVert.texCoords.x * self.oneOverZ[1],
            maxYVert.texCoords.x * self.oneOverZ[2],
        ]

        self.texCoordY = [
            minYVert.texCoords.y * self.oneOverZ[0],
            midYVert.texCoords.y * self.oneOverZ[1],
            maxYVert.texCoords.y * self.oneOverZ[2],
        ]

        oneOverdX = (1.0 /
            (((midYVert.pos.x - maxYVert.pos.x) * (minYVert.pos.y - maxYVert.pos.y)) -
            ((minYVert.pos.x - maxYVert.pos.x) * (midYVert.pos.y - maxYVert.pos.y))))

        oneOverdY = -oneOverdX

        self.texCoordXXStep = self.CalcXStep(self.texCoordX, minYVert, midYVert, maxYVert, oneOverdX)
        self.texCoordXYStep = self.CalcYStep(self.texCoordX, minYVert, midYVert, maxYVert, oneOverdY)
        self.texCoordYXStep = self.CalcXStep(self.texCoordY, minYVert, midYVert, maxYVert, oneOverdX)
        self.texCoordYYStep = self.CalcYStep(self.texCoordY, minYVert, midYVert, maxYVert, oneOverdY)
        self.oneOverZXStep  = self.CalcXStep(self.oneOverZ,  minYVert, midYVert, maxYVert, oneOverdX)
        self.oneOverZYStep  = self.CalcYStep(self.oneOverZ,  minYVert, midYVert, maxYVert, oneOverdY)
        self.depthXStep     = self.CalcXStep(self.depth,     minYVert, midYVert, maxYVert, oneOverdX)
        self.depthYStep     = self.CalcYStep(self.depth,     minYVert, midYVert, maxYVert, oneOverdY)
        self.lightAmtXStep  = self.CalcXStep(self.lightAmt,  minYVert, midYVert, maxYVert, oneOverdX)
        self.lightAmtYStep  = self.CalcYStep(self.lightAmt,  minYVert, midYVert, maxYVert, oneOverdY)

    def CalcXStep(self, values, minYVert, midYVert, maxYVert, oneOverdX):
        return (((values[1] - values[2]) *
                (minYVert.pos.y - maxYVert.pos.y)) -
                ((values[0] - values[2]) *
                (midYVert.pos.y - maxYVert.pos.y))) * oneOverdX

    def CalcYStep(self, values, minYVert, midYVert, maxYVert, oneOverdY):
        return ((((values[1] - values[2]) *
                (minYVert.pos.x - maxYVert.pos.x)) -
                ((values[0] - values[2]) *
                (midYVert.pos.x - maxYVert.pos.x)))) * oneOverdY


class Edge:
    def __init__(self, gradients, minYVert, maxYVert, minYVertIndex):
        self.yStart = math.ceil(minYVert.pos.y)
        self.yEnd = math.ceil(maxYVert.pos.y)

        yDist = maxYVert.pos.y - minYVert.pos.y
        xDist = maxYVert.pos.x - minYVert.pos.x
        if yDist == 0:
            self.xStep = 0
        else:
            self.xStep = xDist / yDist

        yPrestep = self.yStart - minYVert.pos.y

        self.x = minYVert.pos.x + yPrestep * self.xStep
        xPrestep = self.x - minYVert.pos.x

        self.texCoordX = (gradients.texCoordX[minYVertIndex] +
                          gradients.texCoordXXStep * xPrestep +
                          gradients.texCoordXYStep * yPrestep)
        self.texCoordXStep = gradients.texCoordXYStep + gradients.texCoordXXStep * self.xStep

        self.texCoordY = (gradients.texCoordY[minYVertIndex] +
                          gradients.texCoordYXStep * xPrestep +
                          gradients.texCoordYYStep * yPrestep)
        self.texCoordYStep = gradients.texCoordYYStep + gradients.texCoordYXStep * self.xStep

        self.oneOverZ = (gradients.oneOverZ[minYVertIndex] +
                         gradients.oneOverZXStep * xPrestep +
                         gradients.oneOverZYStep * yPrestep)
        self.oneOverZStep = gradients.oneOverZYStep + gradients.oneOverZXStep * self.xStep

        self.depth = (gradients.depth[minYVertIndex] +
                      gradients.depthXStep * xPrestep +
                      gradients.depthYStep * yPrestep)
        self.depthStep = gradients.depthYStep + gradients.depthXStep * self.xStep

        self.lightAmt = (gradients.lightAmt[minYVertIndex] +
                         gradients.lightAmtXStep * xPrestep +
                         gradients.lightAmtYStep * yPrestep)
        self.lightAmtStep = gradients.lightAmtYStep + gradients.lightAmtXStep * self.xStep

    def step(self):
        self.x += self.xStep
        self.texCoordX += self.texCoordXStep
        self.texCoordY += self.texCoordYStep
        self.oneOverZ += self.oneOverZStep
        self.depth += self.depthStep
        self.lightAmt += self.lightAmtStep


class RenderContext:
    def __init__(self, width, height):
        self.bitmap = Bitmap(width, height)
        self.width, self.height = width, height
        self.zbuffer = [0.0] * width * height
        self.zbuffer_reset = [float('inf')] * width * height

        self.screenSpaceTransform = Matrix4().init_screenspace_transform(self.width/2, self.height/2)

    def clear(self):
        self.bitmap.clear()

    def clear_zbuffer(self):
        self.zbuffer[:] = self.zbuffer_reset

    def draw_triangle(self, v1, v2, v3, texture, lightDir):
        if v1.inside_view_frustum() and v2.inside_view_frustum() and v3.inside_view_frustum():
            self.fill_triangle(v1, v2, v3, texture, lightDir)
        else:
            vertices = [v1, v2, v3]
            auxillaryList = []
            if (self.ClipPolygonAxis(vertices, auxillaryList, 0) and
                self.ClipPolygonAxis(vertices, auxillaryList, 1) and
                self.ClipPolygonAxis(vertices, auxillaryList, 2)):
                initialVertex = vertices[0]
                for i in range(1, len(vertices)-1):
                    self.fill_triangle(initialVertex, vertices[i], vertices[i+1], texture, lightDir)

    def ClipPolygonAxis(self, vertices, auxillaryList, componentIndex):
        self.ClipPolygonComponent(vertices, componentIndex, 1.0, auxillaryList)
        vertices[:] = [] #.clear()  # TODO clear unsupported
        if not auxillaryList:
            return False
        self.ClipPolygonComponent(auxillaryList, componentIndex, -1.0, vertices)
        auxillaryList[:] = [] #.clear()  # TODO
        return bool(vertices)

    def ClipPolygonComponent(self, vertices, componentIndex, componentFactor, result):
        previousVertex = vertices[len(vertices) - 1]
        previousComponent = previousVertex.get(componentIndex) * componentFactor
        previousInside = previousComponent <= previousVertex.pos.w

        for currentVertex in vertices:
            currentComponent = currentVertex.get(componentIndex) * componentFactor
            currentInside = currentComponent <= currentVertex.pos.w

            if currentInside ^ previousInside:
                lerpAmt = ((previousVertex.pos.w - previousComponent) /
                           ((previousVertex.pos.w - previousComponent) -
                           (currentVertex.pos.w - currentComponent)))
                result.append(previousVertex.lerp(currentVertex, lerpAmt))

            if currentInside:
                result.append(currentVertex)

            previousVertex = currentVertex
            previousComponent = currentComponent
            previousInside = currentInside

    def fill_triangle(self, v1, v2, v3, texture, lightDir):
        minYVert = v1.transform(self.screenSpaceTransform).perspective_divide()
        midYVert = v2.transform(self.screenSpaceTransform).perspective_divide()
        maxYVert = v3.transform(self.screenSpaceTransform).perspective_divide()

        if minYVert.triangle_area_times_two(maxYVert, midYVert) < 0:
            if maxYVert.pos.y < midYVert.pos.y:
                maxYVert, midYVert = midYVert, maxYVert
            if midYVert.pos.y < minYVert.pos.y:
                midYVert, minYVert = minYVert, midYVert
            if maxYVert.pos.y < midYVert.pos.y:
                maxYVert, midYVert = midYVert, maxYVert

            self.scan_triangle(
                minYVert, midYVert, maxYVert,
                minYVert.triangle_area_times_two(maxYVert, midYVert) >= 0,
                texture,
                lightDir,
            )

    def scan_triangle(self, minYVert, midYVert, maxYVert, handedness, texture, lightDir):
        gradients = Gradients(minYVert, midYVert, maxYVert, lightDir)

        topToBottom    = Edge(gradients, minYVert, maxYVert, 0)
        topToMiddle    = Edge(gradients, minYVert, midYVert, 0)
        middleToBottom = Edge(gradients, midYVert, maxYVert, 1)

        self.scan_edges(gradients, topToBottom, topToMiddle, handedness, texture)
        self.scan_edges(gradients, topToBottom, middleToBottom, handedness, texture)

    def scan_edges(self, gradients, a, b, handedness, texture):
        left, right = a, b
        if handedness:
            left, right = right, left

        for j in range(b.yStart, b.yEnd):
            self.draw_scanline(gradients, left, right, j, texture)
            left.step()
            right.step()

    def draw_scanline(self, gradients, left, right, j, texture):
        xMin = math.ceil(left.x)
        xMax = math.ceil(right.x)

        xPrestep = xMin - left.x

        texCoordXXStep = gradients.texCoordXXStep
        texCoordYXStep = gradients.texCoordYXStep
        oneOverZXStep = gradients.oneOverZXStep
        depthXStep = gradients.depthXStep
        lightAmtXStep = gradients.lightAmtXStep

        texCoordX = left.texCoordX + texCoordXXStep * xPrestep
        texCoordY = left.texCoordY + texCoordYXStep * xPrestep
        oneOverZ = left.oneOverZ + oneOverZXStep * xPrestep
        depth = left.depth + depthXStep * xPrestep
        lightAmt = left.lightAmt + lightAmtXStep * xPrestep

        for i in range(xMin, xMax):
            index = i + j * self.width

            if depth < self.zbuffer[index]:
                self.zbuffer[index] = depth
                z = 1.0 / oneOverZ

                srcX = srcY = 0
                if texture:
                    srcX = int(texCoordX * z * (texture.width - 1) + 0.5)
                    srcY = int(texCoordY * z * (texture.width - 1) + 0.5)

                self.copy_pixel(i, j, srcX, srcY, texture, lightAmt)

            oneOverZ += oneOverZXStep
            texCoordX += texCoordXXStep
            texCoordY += texCoordYXStep
            depth += depthXStep
            lightAmt += lightAmtXStep


    def copy_pixel(self, destX, destY, srcX, srcY, src, lightAmt):
        destIndex = (destX + destY * self.width) * 4
        components = self.bitmap.components

        if src is not None:
            srcIndex = (srcX + srcY * src.width) * 4
            components[destIndex    ] = int(src.components[srcIndex    ] * lightAmt)
            components[destIndex + 1] = int(src.components[srcIndex + 1] * lightAmt)
            components[destIndex + 2] = int(src.components[srcIndex + 2] * lightAmt)
            components[destIndex + 3] = int(src.components[srcIndex + 3] * lightAmt)
        else:
            components[destIndex    ] = int(lightAmt * 255)
            components[destIndex + 1] = int(lightAmt * 255)
            components[destIndex + 2] = int(lightAmt * 255)
            components[destIndex + 3] = int(lightAmt * 255)


if __name__ == '__main__':
    mesh = Mesh("buddha2.obj")
    texture = Bitmap(1, 1, b'')
    v = Vector4(0.0, 0.0, 0.0)
    transform = Transform(v).rotate(quaternion_from_axis_angle(v, 80.0))
    target = RenderContext(0, 0)
    target.clear()
    target.clear_zbuffer()
    camera = Camera(Matrix4().init_perspective(1.0, 1.0, 0.1, 1000.0))
    mesh.draw(target, camera.get_view_projection(), transform.get_transformation(), texture, v)
