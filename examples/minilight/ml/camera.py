#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/


from math import pi, tan
from random import random
from .raytracer import RayTracer
from .vector3f import Vector3f, Vector3f_str

import re
SEARCH = re.compile('(\(.+\))\s*(\(.+\))\s*(\S+)')

class Camera(object):

    def __init__(self, in_stream):
        for line in in_stream:
            if not line.isspace():
                p, d, a = SEARCH.search(line).groups()
                self.view_position = Vector3f_str(p)
                self.view_direction = Vector3f_str(d).unitize()
                if self.view_direction.is_zero():
                    self.view_direction = Vector3f(0.0, 0.0, 1.0)
                self.view_angle = min(max(10.0, float(a)), 160.0) * (pi / 180.0) ## truediv
                self.right = Vector3f(0.0, 1.0, 0.0).cross(self.view_direction).unitize()
                if self.right.is_zero():
                    self.up = Vector3f(0.0, 0.0, 1.0 if self.view_direction.y else -1.0)
                    self.right = self.up.cross(self.view_direction).unitize()
                else:
                    self.up = self.view_direction.cross(self.right).unitize()
                break

    def get_frame(self, scene, image):
        raytracer = RayTracer(scene)
        aspect = float(image.height) / float(image.width) ## truediv
        for y in range(image.height):
            for x in range(image.width):
                x_coefficient = ((x + random()) * 2.0 / image.width) - 1.0  ## truediv
                y_coefficient = ((y + random()) * 2.0 / image.height) - 1.0 ## truediv
                offset = self.right * x_coefficient + self.up * (y_coefficient * aspect)
                sample_direction = (self.view_direction + (offset * tan(self.view_angle * 0.5))).unitize()
                radiance = raytracer.get_radiance(self.view_position, sample_direction)
                image.add_to_pixel(x, y, radiance)

