import math

from matrix4 import Matrix4
from vector4 import Vector4

class Quaternion:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    @staticmethod
    def from_axis_angle(axis, angle):
        sin_half_angle = math.sin(angle / 2)
        cos_half_angle = math.cos(angle / 2)
        return Quaternion(axis.x * sin_half_angle, axis.y * sin_half_angle, axis.z * sin_half_angle, cos_half_angle)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)

    def normalized(self):
        length = self.length()
        return Quaternion(self.x / length, self.y / length, self.z / length, self.w / length)

    def conjugate(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def mul(self, r):
        assert isinstance(r, Quaternion)
        return Quaternion(
            self.x * r.w + self.w * r.x + self.y * r.z - self.z * r.y,
            self.y * r.w + self.w * r.y + self.z * r.x - self.x * r.z,
            self.z * r.w + self.w * r.z + self.x * r.y - self.y * r.x,
            self.w * r.w - self.x * r.x - self.y * r.y - self.z * r.z,
        )

    def to_rotation_matrix(self):
        return Matrix4().init_rotation(
            Vector4(2.0 * (self.x * self.z - self.w * self.y), 2.0 * (self.y * self.z + self.w * self.x), 1.0 - 2.0 * (self.x * self.x + self.y * self.y)),
            Vector4(2.0 * (self.x * self.y + self.w * self.z), 1.0 - 2.0 * (self.x * self.x + self.z * self.z), 2.0 * (self.y * self.z - self.w * self.x)),
            Vector4(1.0 - 2.0 * (self.y * self.y + self.z * self.z), 2.0 * (self.x * self.y - self.w * self.z), 2.0 * (self.x * self.z + self.w * self.y)),
        )
