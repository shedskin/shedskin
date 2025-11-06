import math

from bitmap import Bitmap
from edge import Edge
from gradients import Gradients
from matrix4 import Matrix4


class RenderContext(Bitmap):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zbuffer = [0.0] * width * height
        self.components = [0] * width * height * 4

    def clear(self, val):
#        print('CLEAR!!', val)
        for i in range(self.width * self.height * 4):
            self.components[i] = val

    def clear_zbuffer(self):
        inf = float('inf')
        for i in range(self.width * self.height):
            self.zbuffer[i] = inf

    def draw_triangle(self, v1, v2, v3, texture, lightDir):
        print('DRAW TRIANGLE')

        if v1.inside_view_frustum() and v2.inside_view_frustum() and v3.inside_view_frustum():
            self.fill_triangle(v1, v2, v3, texture, lightDir);
        else:
            print('NEEDS CLIPPING!')
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
        vertices.clear()
        if not auxillaryList:
            return False
        self.ClipPolygonComponent(auxillaryList, componentIndex, -1.0, vertices)
        auxillaryList.clear()
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
        print('FILL TRIANGLE')

#        print('WH', self.width, self.height)
        screenSpaceTransform = Matrix4().init_screenspace_transform(self.width/2, self.height/2)

#        print('SST')
#        screenSpaceTransform.print()

        identity = Matrix4().init_identity();

        minYVert = v1.transform(screenSpaceTransform, identity).perspective_divide()
        midYVert = v2.transform(screenSpaceTransform, identity).perspective_divide()
        maxYVert = v3.transform(screenSpaceTransform, identity).perspective_divide()

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
        else:
            print('INVIS')

    def scan_triangle(self, minYVert, midYVert, maxYVert, handedness, texture, lightDir):
        print('scan triangle')
        print('minyvert', minYVert.pos.x, minYVert.pos.y, minYVert.pos.z)
        print('midyvert', midYVert.pos.x, midYVert.pos.y, midYVert.pos.z)
        print('maxyvert', maxYVert.pos.x, maxYVert.pos.y, maxYVert.pos.z)
        print('handedness', handedness)

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

        for j in range(b.yStart, b.yEnd):  # TODO b? simplify?
            self.draw_scanline(gradients, left, right, j, texture)
            left.step()
            right.step()

    def draw_scanline(self, gradients, left, right, j, texture):
        xMin = math.ceil(left.x);
        xMax = math.ceil(right.x);

        print('scanline', j, xMin, xMax)

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

#        print('texX', texCoordX, texCoordXXStep)
#        print('texY', texCoordY, texCoordYXStep)

#        print('oneOverZ', oneOverZ, oneOverZXStep)
#        print('depth', depth, depthXStep)
        print('lightAmt', lightAmt, lightAmtXStep)

        for i in range(xMin, xMax):
            index = i + j * self.width

            if depth < self.zbuffer[index]:
                self.zbuffer[index] = depth
                z = 1.0/oneOverZ

                if texture:
                    srcX = int(texCoordX * z * (texture.width - 1) + 0.5)
                    srcY = int(texCoordY * z * (texture.width - 1) + 0.5)
                else:
                    srcX = None
                    srcY = None

#                print('src', srcX, srcY)

                self.copy_pixel(i, j, srcX, srcY, texture, lightAmt)

            oneOverZ += oneOverZXStep
            texCoordX += texCoordXXStep
            texCoordY += texCoordYXStep
            depth += depthXStep
            lightAmt += lightAmtXStep
