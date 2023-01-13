#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/


from random import choice
from .spatialindex import SpatialIndex
from .triangle import Triangle
from .vector3f import Vector3f_str, ZERO, ONE, MAX

import re
SEARCH = re.compile('(\(.+\))\s*(\(.+\))')

MAX_TRIANGLES = 0x100000

class Scene(object):

    def __init__(self, in_stream, eye_position):
        for line in in_stream:
            if not line.isspace():
                s, g = SEARCH.search(line).groups()
                self.sky_emission = Vector3f_str(s).clamped(ZERO, MAX)
                self.ground_reflection = Vector3f_str(g).clamped(ZERO, ONE)
                self.triangles = []
                try:
                    for i in range(MAX_TRIANGLES):
                        self.triangles.append(Triangle(in_stream))
                except StopIteration:
                    pass
                self.emitters = [triangle for triangle in self.triangles if not triangle.emitivity.is_zero() and triangle.area > 0.0]
                self.index = SpatialIndex(eye_position, None, self.triangles)

                break

    def get_intersection(self, ray_origin, ray_direction, last_hit):
        return self.index.get_intersection(ray_origin, ray_direction, last_hit)

    def get_emitter(self):
        emitter = None if len(self.emitters) == 0 else choice(self.emitters)
        return (emitter.get_sample_point() if emitter else ZERO), emitter

    def emitters_count(self):
        return len(self.emitters)

    def get_default_emission(self, back_direction):
        return self.sky_emission if back_direction.y < 0.0 else self.sky_emission.mul(self.ground_reflection)
