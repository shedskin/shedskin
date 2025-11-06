import math

class Edge:
    def __init__(self, gradients, minYVert, maxYVert, minYVertIndex):
        self.yStart = math.ceil(minYVert.pos.y)
        self.yEnd = math.ceil(maxYVert.pos.y)

        yDist = maxYVert.pos.y - minYVert.pos.y
        xDist = maxYVert.pos.x - minYVert.pos.x
        if yDist == 0:  # TODO in java div-0 creates inf.. nicer solution?
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
        self.x += self.xStep;
        self.texCoordX += self.texCoordXStep
        self.texCoordY += self.texCoordYStep
        self.oneOverZ += self.oneOverZStep
        self.depth += self.depthStep
        self.lightAmt += self.lightAmtStep
