from vector4 import Vector4

def saturate(val):
    return max(0.0, min(val, 1.0))


class Gradients:
    def __init__(self, minYVert, midYVert, maxYVert, lightDir):
#        print('gradients')

        self.oneOverZ = [
            1.0 / minYVert.pos.w,
            1.0 / midYVert.pos.w,
            1.0 / maxYVert.pos.w,
        ]

#        print('oneoverZ', self.oneOverZ[0])

        self.depth = [
            minYVert.pos.z,
            midYVert.pos.z,
            maxYVert.pos.z,
        ]

        print('wattt', minYVert.normal)
        print('wattt', midYVert.normal)
        print('wattt', maxYVert.normal)

        self.lightAmt = [
            saturate(minYVert.normal.dot(lightDir)) * 0.9 + 0.5,
            saturate(midYVert.normal.dot(lightDir)) * 0.9 + 0.5,
            saturate(maxYVert.normal.dot(lightDir)) * 0.9 + 0.5,
        ]
        print('lightamt at vcts', self.lightAmt)

#        print('vtx texcoordx', minYVert.texCoords.x)

        self.texCoordX = [
            minYVert.texCoords.x * self.oneOverZ[0],
            midYVert.texCoords.x * self.oneOverZ[1],
            maxYVert.texCoords.x * self.oneOverZ[2],
        ]
#        print('texCoordX', self.texCoordX[0])

#        print('minyvert texcoords', minYVert.texCoords.x, minYVert.texCoords.y)

        self.texCoordY = [
            minYVert.texCoords.y * self.oneOverZ[0],
            midYVert.texCoords.y * self.oneOverZ[1],
            maxYVert.texCoords.y * self.oneOverZ[2],
        ]

#        print('texCoordY', self.texCoordY[0])

        oneOverdX = (1.0 /
            (((midYVert.pos.x - maxYVert.pos.x) *
            (minYVert.pos.y - maxYVert.pos.y)) -
            ((minYVert.pos.x - maxYVert.pos.x) *
            (midYVert.pos.y - maxYVert.pos.y))))

        oneOverdY = -oneOverdX

        self.texCoordXXStep = self.CalcXStep(self.texCoordX, minYVert, midYVert, maxYVert, oneOverdX);

#        print('texCoordXXStep', self.texCoordXXStep)

        self.texCoordXYStep = self.CalcYStep(self.texCoordX, minYVert, midYVert, maxYVert, oneOverdY);
        self.texCoordYXStep = self.CalcXStep(self.texCoordY, minYVert, midYVert, maxYVert, oneOverdX);

#        print('texCoordYXStep', self.texCoordYXStep)

        self.texCoordYYStep = self.CalcYStep(self.texCoordY, minYVert, midYVert, maxYVert, oneOverdY);
        self.oneOverZXStep  = self.CalcXStep(self.oneOverZ,  minYVert, midYVert, maxYVert, oneOverdX);
        self.oneOverZYStep  = self.CalcYStep(self.oneOverZ,  minYVert, midYVert, maxYVert, oneOverdY);
        self.depthXStep     = self.CalcXStep(self.depth,     minYVert, midYVert, maxYVert, oneOverdX);
        self.depthYStep     = self.CalcYStep(self.depth,     minYVert, midYVert, maxYVert, oneOverdY);
        self.lightAmtXStep  = self.CalcXStep(self.lightAmt,  minYVert, midYVert, maxYVert, oneOverdX);
        self.lightAmtYStep  = self.CalcYStep(self.lightAmt,  minYVert, midYVert, maxYVert, oneOverdY);

        print('lightamt steps', self.lightAmtXStep, self.lightAmtYStep)

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
