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
                u, v = map(float, line[2:].split())
                texcoords.append((u, 1.0 - v))

            elif line.startswith('vn '):
                x, y, z = map(float, line[2:].split())
                normals.append((x, y, z))

        index = {} # create unique vertices for vertex-texcoords-normal combinations

        for line in open(filename):
            if line.startswith('f '):
                print('gogo', line[2:].split())
                idcs = []
                for token in line[2:].split():
                    v, t, n = map(int, token.split('/'))  # TODO n is ignored!
                    if not normals:
                        n = 0
                    print('VTN', v, t, n)
                    idx = index.get((v, t, n))
                    if idx is None:
                        x, y, z = vertices[v-1]
                        u, v = texcoords[t-1]  # TODO handle missing t like n
                        if normals and n-1 < len(normals):
                            a, b, c = normals[n-1]
                        else:
                            a, b, c = 0, 0, 0
                        print('VTX NORMAL', a, b, c)
                        vertex = Vertex(Vector4(x, y, z, 1), Vector4(u, v, 0, 0), Vector4(a, b, c, 0))
                        index[v, t, n] = idx = len(self.vertices)
                        self.vertices.append(vertex)
                    else:
                        print('ALREADY')
                    idcs.append(idx)

                print('idcs', idcs)
                for i in range(len(idcs)-2):  # TODO inline in above
                    print('fa', [idcs[0], idcs[i+1], idcs[i+2]])
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
                print('NORMAL', normal)

                for j in (i0, i1, i2):
                    v = self.vertices[j]
                    key = (v.pos.x, v.pos.y, v.pos.z)
                    if key in pos_normal:
                        havenormal = pos_normal[key]
                    else:
                        havenormal = Vector4(0, 0, 0, 0)
                    pos_normal[key] = havenormal.add(normal)

#                print('INITNORMAL', self.vertices[i0].normal)
#                print('INITNORMAL', self.vertices[i1].normal)
#                print('INITNORMAL', self.vertices[i2].normal)
#
#                self.vertices[i0].normal = self.vertices[i0].normal.add(normal)
#                self.vertices[i1].normal = self.vertices[i1].normal.add(normal)
#                self.vertices[i2].normal = self.vertices[i2].normal.add(normal)
#
#                print('INITNORMALB', self.vertices[i0].normal)
#                print('INITNORMALB', self.vertices[i1].normal)
#                print('INITNORMALB', self.vertices[i2].normal)

            for v in self.vertices:
                v.normal = pos_normal[v.pos.x, v.pos.y, v.pos.z].normalized()
                print('NN', v.pos.x, v.pos.y, v.pos.z, v.normal)

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
