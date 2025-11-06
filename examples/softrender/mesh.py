from vector4 import Vector4
from vertex import Vertex

class Mesh:
    def __init__(self, filename, scale=1):
        self.vertices = []
        self.faces = []

        vertices = []
        texcoords = []
        normals = []

        for line in open(filename):
            if line.startswith('v '):
                x, y, z = map(float, line[2:].split())
                vertices.append((x / scale, y / scale, z / scale))

            elif line.startswith('vt '):
                tu, tv = map(float, line[2:].split())
                texcoords.append((tu, 1.0 - tv))

            elif line.startswith('vn '):
                x, y, z = map(float, line[2:].split())
                normals.append((x, y, z))

        index = {} # create unique vertices for vertex-texcoords-normal combinations

        for line in open(filename):
            if line.startswith('f '):
                idcs = []
                for token in line[2:].split():
                    v, t, n = map(int, token.split('/'))  # TODO n is ignored!
                    if not normals:
                        n = 0
                    idx = index.get((v, t, n), -1)
                    if idx == -1:
                        x, y, z = vertices[v-1]
                        tu, tv = texcoords[t-1]  # TODO handle missing t like n
                        if normals and n-1 < len(normals):
                            a, b, c = normals[n-1]
                        else:
                            a, b, c = 0, 0, 0
                        vertex = Vertex(Vector4(x, y, z, 1), Vector4(tu, tv, 0, 0), Vector4(a, b, c, 0))
                        index[v, t, n] = idx = len(self.vertices)
                        self.vertices.append(vertex)
                    idcs.append(idx)

                for i in range(len(idcs)-2):  # TODO inline in above
                    self.faces.extend([idcs[0], idcs[i+1], idcs[i+2]])

        if not normals:
            pos_normal = {}

            for i in range(0, len(self.faces), 3):
                i0 = self.faces[i]
                i1 = self.faces[i+1]
                i2 = self.faces[i+2]

                v1 = self.vertices[i1].pos.sub(self.vertices[i0].pos)
                v2 = self.vertices[i2].pos.sub(self.vertices[i0].pos)

                normal = v1.cross(v2).normalized()

                for j in (i0, i1, i2):
                    vtx = self.vertices[j]
                    key = (vtx.pos.x, vtx.pos.y, vtx.pos.z)
                    if key in pos_normal:
                        havenormal = pos_normal[key]
                    else:
                        havenormal = Vector4(0, 0, 0, 0)
                    pos_normal[key] = havenormal.add(normal)

            for vtx in self.vertices:
                vtx.normal = pos_normal[vtx.pos.x, vtx.pos.y, vtx.pos.z].normalized()

    def draw(self, context, view_projection, transform, texture, lightDir):
        mvp = view_projection.mul(transform)

        for i in range(0, len(self.faces), 3):
            context.draw_triangle(
                self.vertices[self.faces[i  ]].transform(mvp, transform),
                self.vertices[self.faces[i+1]].transform(mvp, transform),
                self.vertices[self.faces[i+2]].transform(mvp, transform),
                texture,
                lightDir
            )
