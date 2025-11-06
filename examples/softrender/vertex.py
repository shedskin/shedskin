from vector4 import Vector4

class Vertex:
    def __init__(self, pos, texCoords, normal):
        self.pos = pos
        self.texCoords = texCoords
        self.normal = normal

    def transform(self, transform, normalTransform):
        return Vertex(transform.transform(self.pos), self.texCoords, normalTransform.transform(self.normal).normalized())

    def inside_view_frustum(self):
        return (abs(self.pos.x) <= abs(self.pos.w) and
                abs(self.pos.y) <= abs(self.pos.w) and
                abs(self.pos.z) <= abs(self.pos.w))

    def perspective_divide(self):
        w = self.pos.w
        return Vertex(Vector4(self.pos.x/w, self.pos.y/w, self.pos.z/w, w), self.texCoords, self.normal)

    def triangle_area_times_two(self, b, c):
        x1 = b.pos.x - self.pos.x
        y1 = b.pos.y - self.pos.y

        x2 = c.pos.x - self.pos.x
        y2 = c.pos.y - self.pos.y

        return x1 * y2 - x2 * y1
