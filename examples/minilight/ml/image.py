#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/


from math import log10
from .vector3f import Vector3f, Vector3f_seq

PPM_ID = b'P6'
MINILIGHT_URI = b'http://www.hxa7241.org/minilight/'
DISPLAY_LUMINANCE_MAX = 200.0
RGB_LUMINANCE = Vector3f(0.2126, 0.7152, 0.0722)
GAMMA_ENCODE = 0.45


class Image(object):

    def __init__(self, in_stream):
        for line in in_stream:
            if not line.isspace():
                self.width, self.height = self.dim(line.split()[0]), self.dim(line.split()[1])
                self.pixels = [0.0] * self.width * self.height * 3
                break

    def dim(self, dimension):
        return min(max(1, int(dimension)), 10000)

    def add_to_pixel(self, x, y, radiance):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            index = (x + ((self.height - 1 - y) * self.width)) * 3
            self.pixels[index] += radiance.x
            self.pixels[index+1] += radiance.y
            self.pixels[index+2] += radiance.z

    def get_formatted(self, out, iteration):
        divider = 1.0 / ((iteration if iteration > 0 else 0) + 1) ## truediv
        tonemap_scaling = self.calculate_tone_mapping(self.pixels, divider)
        header = b'%s\n# %s\n\n%u %u\n255\n' % (PPM_ID, MINILIGHT_URI, self.width, self.height)
        out.write(header)
        for channel in self.pixels:
            mapped = channel * divider * tonemap_scaling
            gammaed = (mapped if mapped > 0.0 else 0.0) ** GAMMA_ENCODE
            output = b'%c' % min(int((gammaed * 255.0) + 0.5), 255)
            out.write(output)

    def calculate_tone_mapping(self, pixels, divider):
        sum_of_logs = 0.0
        for i in range(len(pixels) // 3): ## intdiv
            y = Vector3f_seq(pixels[i * 3: i * 3 + 3]).dot(RGB_LUMINANCE) * divider
            sum_of_logs += log10(y if y > 1e-4 else 1e-4)
        assert(isinstance(sum_of_logs, float))
        log_mean_luminance = 10.0 ** (sum_of_logs / (len(pixels) // 3)) ## intdiv
        a = 1.219 + (DISPLAY_LUMINANCE_MAX * 0.25) ** 0.4
        b = 1.219 + log_mean_luminance ** 0.4
        return ((a / b) ** 2.5) / DISPLAY_LUMINANCE_MAX ## truediv
