from PIL import Image

class Bitmap:
    def __init__(self, filename):
        image = Image.open(filename)
        self.width = image.width
        self.height = image.height
        self.components = image.convert('RGBA').tobytes()

    def copy_pixel(self, destX, destY, srcX, srcY, src, lightAmt):
        destIndex = (destX + destY * self.width) * 4

        if lightAmt > 1:  # TODO check java
            lightAmt = 1.0
        elif lightAmt < 0:
            lightAmt = 0

        if src is not None:
            srcIndex = (srcX + srcY * src.width) * 4

            self.components[destIndex    ] = int(src.components[srcIndex    ] * lightAmt)
            self.components[destIndex + 1] = int(src.components[srcIndex + 1] * lightAmt)
            self.components[destIndex + 2] = int(src.components[srcIndex + 2] * lightAmt)
            self.components[destIndex + 3] = int(src.components[srcIndex + 3] * lightAmt)
        else:
            self.components[destIndex    ] = int(lightAmt * 255)
            self.components[destIndex + 1] = int(lightAmt * 255)
            self.components[destIndex + 2] = int(lightAmt * 255)
            self.components[destIndex + 3] = int(lightAmt * 255)
