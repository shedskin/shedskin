import math

from vector4 import Vector4


class Matrix4:
    def __init__(self):
        self.m = [[0.0 for i in range(4)] for j in range(4)]

    def init_scale(self, x, y, z):
        m = self.m
        m[0][0] = x; m[0][1] = 0; m[0][2] = 0; m[0][3] = 0
        m[1][0] = 0; m[1][1] = y; m[1][2] = 0; m[1][3] = 0
        m[2][0] = 0; m[2][1] = 0; m[2][2] = z; m[2][3] = 0
        m[3][0] = 0; m[3][1] = 0; m[3][2] = 0; m[3][3] = 1
        return self

    def init_identity(self):
        m = self.m
        m[0][0] = 1; m[0][1] = 0; m[0][2] = 0; m[0][3] = 0
        m[1][0] = 0; m[1][1] = 1; m[1][2] = 0; m[1][3] = 0
        m[2][0] = 0; m[2][1] = 0; m[2][2] = 1; m[2][3] = 0
        m[3][0] = 0; m[3][1] = 0; m[3][2] = 0; m[3][3] = 1
        return self

    def init_translation(self, x, y, z):
        m = self.m
        m[0][0] = 1; m[0][1] = 0; m[0][2] = 0; m[0][3] = x
        m[1][0] = 0; m[1][1] = 1; m[1][2] = 0; m[1][3] = y
        m[2][0] = 0; m[2][1] = 0; m[2][2] = 1; m[2][3] = z
        m[3][0] = 0; m[3][1] = 0; m[3][2] = 0; m[3][3] = 1
        return self

    def init_rotation(self, f, u, r):
        m = self.m
        m[0][0] = r.x; m[0][1] = r.y; m[0][2] = r.z; m[0][3] = 0
        m[1][0] = u.x; m[1][1] = u.y; m[1][2] = u.z; m[1][3] = 0
        m[2][0] = f.x; m[2][1] = f.y; m[2][2] = f.z; m[2][3] = 0
        m[3][0] = 0;   m[3][1] = 0;   m[3][2] = 0;   m[3][3] = 1
        return self

    def init_screenspace_transform(self, halfWidth, halfHeight):
        m = self.m
        m[0][0] = halfWidth; m[0][1] = 0;           m[0][2] = 0; m[0][3] = halfWidth - 0.5
        m[1][0] = 0;         m[1][1] = -halfHeight; m[1][2] = 0; m[1][3] = halfHeight - 0.5
        m[2][0] = 0;         m[2][1] = 0;           m[2][2] = 1; m[2][3] = 0
        m[3][0] = 0;         m[3][1] = 0;           m[3][2] = 0; m[3][3] = 1
        return self

    def init_perspective(self, fov, aspectRatio, zNear, zFar):
        tanHalfFOV = math.tan(fov / 2)
        zRange = zNear - zFar
        m = self.m
        m[0][0] = 1.0 / (tanHalfFOV * aspectRatio); m[0][1] = 0;                m[0][2] = 0;                     m[0][3] = 0
        m[1][0] = 0;                                m[1][1] = 1.0 / tanHalfFOV; m[1][2] = 0;                     m[1][3] = 0
        m[2][0] = 0;                                m[2][1] = 0;                m[2][2] = (-zNear -zFar)/zRange; m[2][3] = 2 * zFar * zNear / zRange
        m[3][0] = 0;                                m[3][1] = 0;                m[3][2] = 1;                     m[3][3] = 0
        return self

    def transform(self, r):
        m = self.m
        return Vector4(m[0][0] * r.x + m[0][1] * r.y + m[0][2] * r.z + m[0][3] * r.w,
                       m[1][0] * r.x + m[1][1] * r.y + m[1][2] * r.z + m[1][3] * r.w,
                       m[2][0] * r.x + m[2][1] * r.y + m[2][2] * r.z + m[2][3] * r.w,
                       m[3][0] * r.x + m[3][1] * r.y + m[3][2] * r.z + m[3][3] * r.w)

    def mul(self, other):
        m = self.m
        r = other.m
        res = Matrix4()
        for i in range(4):
            for j in range(4):
                res.m[i][j] = m[i][0] * r[0][j] + m[i][1] * r[1][j] + m[i][2] * r[2][j] + m[i][3] * r[3][j]
        return res

    def print(self):
        for i in range(4):
            for j in range(4):
                print(self.m[i][j], ',', end='')
            print()
