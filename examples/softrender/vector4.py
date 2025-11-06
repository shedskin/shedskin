import math

class Vector4:
    def __init__(self, x, y, z, w=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

    def normalized(self):
        length = self.length()
        return Vector4(self.x / length, self.y / length, self.z / length, self.w / length)

    def mul(self, r):  # TODO scalar/instance mul convention?
        assert isinstance(r, float) or isinstance(r, int)
        return Vector4(self.x * r, self.y * r, self.z * r, self.w * r)

    def sub(self, r):
        return Vector4(self.x - r.x, self.y - r.y, self.z - r.z, self.w - r.w)

    def add(self, r):
        return Vector4(self.x + r.x, self.y + r.y, self.z + r.z, self.w + r.w)

    def dot(self, r):
        return self.x * r.x + self.y * r.y + self.z * r.z + self.w * r.w

    def cross(self, r):
        return Vector4(
            self.y * r.z - self.z * r.y,
            self.z * r.x - self.x * r.z,
            self.x * r.y - self.y * r.x,
            0,
        )

    def lerp(self, dest, lerpFactor):
        return dest.sub(self).mul(lerpFactor).add(self)

    def __str__(self):
        return f'Vector4({self.x}, {self.y}, {self.z}, {self.w})'
