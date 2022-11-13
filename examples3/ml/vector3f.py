#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/


from math import sqrt

def Vector3f_str(s):
    split = s.lstrip(' (').rstrip(') ').split()
    return Vector3f(float(split[0]), float(split[1]), float(split[2]))

def Vector3f_seq(seq):
    return Vector3f(seq[0], seq[1], seq[2])

def Vector3f_scalar(s):
    return Vector3f(s, s, s)

class Vector3f(object):

    def __init__(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)

    def as_list(self):
        return [self.x, self.y, self.z]

    def copy(self):
        return Vector3f(self.x, self.y, self.z)

    def __getitem__(self, key):
        if key == 2:
            return self.z
        elif key == 1:
            return self.y
        else:
            return self.x

    def __neg__(self):
        return Vector3f(-self.x, -self.y, -self.z)

    def __add__(self, other):
        return Vector3f(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3f(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vector3f(self.x * other, self.y * other, self.z * other)

    def mul(self, other):
        return Vector3f(self.x * other.x, self.y * other.y, self.z * other.z)

    def is_zero(self):
        return self.x == 0.0 and self.y == 0.0 and self.z == 0.0

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def unitize(self):
        length = sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        one_over_length = 1.0 / length if length != 0.0 else 0.0
        return Vector3f(self.x * one_over_length, self.y * one_over_length, self.z * one_over_length)

    def cross(self, other):
        return Vector3f((self.y * other.z) - (self.z * other.y),
                        (self.z * other.x) - (self.x * other.z),
                        (self.x * other.y) - (self.y * other.x))

    def clamped(self, lo, hi):
        return Vector3f(min(max(self.x, lo.x), hi.x),
                        min(max(self.y, lo.y), hi.y),
                        min(max(self.z, lo.z), hi.z))

ZERO = Vector3f_scalar(0.0)
ONE = Vector3f_scalar(1.0)
MAX = Vector3f_scalar(1.797e308)
##ALMOST_ONE?
