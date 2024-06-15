import math
import operator
from csg.geom import *
from functools import reduce

class CSG(object):
    """
    Constructive Solid Geometry (CSG) is a modeling technique that uses Boolean
    operations like union and intersection to combine 3D solids. This library
    implements CSG operations on meshes elegantly and concisely using BSP trees,
    and is meant to serve as an easily understandable implementation of the
    algorithm. All edge cases involving overlapping coplanar polygons in both
    solids are correctly handled.
    
    Example usage::
    
        from csg.core import CSG
        
        cube = CSG.cube();
        sphere = CSG.sphere({'radius': 1.3});
        polygons = cube.subtract(sphere).toPolygons();
    
    ## Implementation Details
    
    All CSG operations are implemented in terms of two functions, `clipTo()` and
    `invert()`, which remove parts of a BSP tree inside another BSP tree and swap
    solid and empty space, respectively. To find the union of `a` and `b`, we
    want to remove everything in `a` inside `b` and everything in `b` inside `a`,
    then combine polygons from `a` and `b` into one solid::
    
        a.clipTo(b);
        b.clipTo(a);
        a.build(b.allPolygons());
    
    The only tricky part is handling overlapping coplanar polygons in both trees.
    The code above keeps both copies, but we need to keep them in one tree and
    remove them in the other tree. To remove them from `b` we can clip the
    inverse of `b` against `a`. The code for union now looks like this::
    
        a.clipTo(b);
        b.clipTo(a);
        b.invert();
        b.clipTo(a);
        b.invert();
        a.build(b.allPolygons());
    
    Subtraction and intersection naturally follow from set operations. If
    union is `A | B`, subtraction is `A - B = ~(~A | B)` and intersection is
    `A & B = ~(~A | ~B)` where `~` is the complement operator.
    
    ## License
    
    Copyright (c) 2011 Evan Wallace (http://madebyevan.com/), under the MIT license.
    
    Python port Copyright (c) 2012 Tim Knip (http://www.floorplanner.com), under the MIT license.
    Additions by Alex Pletzer (Pennsylvania State University)
    """
    def __init__(self):
        self.polygons = []
    
    @classmethod
    def fromPolygons(cls, polygons):
        csg = CSG()
        csg.polygons = polygons
        return csg
    
    def clone(self):
        csg = CSG()
        csg.polygons = list(map(lambda p: p.clone(), self.polygons))
        return csg
        
    def toPolygons(self):
        return self.polygons

    def refine(self):
        """
        Return a refined CSG. To each polygon, a middle point is added to each edge and to the center 
        of the polygon
        """
        newCSG = CSG()
        for poly in self.polygons:

            verts = poly.vertices
            numVerts = len(verts)

            if numVerts == 0:
                continue

            midPos = reduce(operator.add, [v.pos for v in verts]) / float(numVerts)
            midNormal = None
            if verts[0].normal is not None:
                midNormal = poly.plane.normal
            midVert = Vertex(midPos, midNormal)

            newVerts = verts + \
                       [verts[i].interpolate(verts[(i + 1)%numVerts], 0.5) for i in range(numVerts)] + \
                       [midVert]

            i = 0
            vs = [newVerts[i], newVerts[i+numVerts], newVerts[2*numVerts], newVerts[2*numVerts-1]]
            newPoly = Polygon(vs, poly.shared)
            newPoly.shared = poly.shared
            newPoly.plane = poly.plane
            newCSG.polygons.append(newPoly)

            for i in range(1, numVerts):
                vs = [newVerts[i], newVerts[numVerts+i], newVerts[2*numVerts], newVerts[numVerts+i-1]]
                newPoly = Polygon(vs, poly.shared)
                newCSG.polygons.append(newPoly)
                
        return newCSG

    def translate(self, disp):
        """
        Translate Geometry.
           disp: displacement (array of floats)
        """
        d = Vector(disp[0], disp[1], disp[2])
        for poly in self.polygons:
            for v in poly.vertices:
                v.pos = v.pos.plus(d)
                # no change to the normals

    def rotate(self, axis, angleDeg):
        """
        Rotate geometry.
           axis: axis of rotation (array of floats)
           angleDeg: rotation angle in degrees
        """
        ax = Vector(axis[0], axis[1], axis[2]).unit()
        cosAngle = math.cos(math.pi * angleDeg / 180.)
        sinAngle = math.sin(math.pi * angleDeg / 180.)

        def newVector(v):
            vA = v.dot(ax)
            vPerp = v.minus(ax.times(vA))
            vPerpLen = vPerp.length()
            if vPerpLen == 0:
                # vector is parallel to axis, no need to rotate
                return v
            u1 = vPerp.unit()
            u2 = u1.cross(ax)
            vCosA = vPerpLen*cosAngle
            vSinA = vPerpLen*sinAngle
            return ax.times(vA).plus(u1.times(vCosA).plus(u2.times(vSinA)))

        for poly in self.polygons:
            for vert in poly.vertices:
                vert.pos = newVector(vert.pos)
                normal = vert.normal
                if normal.length() > 0:
                    vert.normal = newVector(vert.normal)
    
    def toVerticesAndPolygons(self):
        """
        Return list of vertices, polygons (cells), and the total
        number of vertex indices in the polygon connectivity list
        (count).
        """
        offset = 1.234567890
        verts = []
        polys = []
        vertexIndexMap = {}
        count = 0
        for poly in self.polygons:
            verts = poly.vertices
            cell = []
            for v in poly.vertices:
                p = v.pos
                # use string key to remove degeneracy associated
                # very close points. The format %.10e ensures that
                # points differing in the 11 digits and higher are 
                # treated as the same. For instance 1.2e-10 and 
                # 1.3e-10 are essentially the same.
                vKey = '%.10e,%.10e,%.10e' % (p.x + offset,
                                              p.y + offset,
                                              p.z + offset)
                if not vKey in vertexIndexMap:
                    vertexIndexMap[vKey] = len(vertexIndexMap)
                index = vertexIndexMap[vKey]
                cell.append(index)
                count += 1
            polys.append(cell)
        # sort by index
        sortedVertexIndex = sorted(vertexIndexMap.items(),
                                   key=operator.itemgetter(1))
        verts = []
        for v, i in sortedVertexIndex:
            p = []
            for c in v.split(','):
                p.append(float(c) - offset)
            verts.append(tuple(p))
        return verts, polys, count

    def saveVTK(self, filename):
        """
        Save polygons in VTK file.
        """
        with open(filename, 'w') as f:
            f.write('# vtk DataFile Version 3.0\n')
            f.write('pycsg output\n')
            f.write('ASCII\n')
            f.write('DATASET POLYDATA\n')
        
            verts, cells, count = self.toVerticesAndPolygons()

            f.write('POINTS {0} float\n'.format(len(verts)))
            for v in verts:
                f.write('{0} {1} {2}\n'.format(v[0], v[1], v[2]))
            numCells = len(cells)
            f.write('POLYGONS {0} {1}\n'.format(numCells, count + numCells))
            for cell in cells:
                f.write('{0} '.format(len(cell)))
                for index in cell:
                    f.write('{0} '.format(index))
                f.write('\n')

    def union(self, csg):
        """
        Return a new CSG solid representing space in either this solid or in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.union(B)
        
            +-------+            +-------+
            |       |            |       |
            |   A   |            |       |
            |    +--+----+   =   |       +----+
            +----+--+    |       +----+       |
                 |   B   |            |       |
                 |       |            |       |
                 +-------+            +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.clipTo(b)
        b.clipTo(a)
        b.invert()
        b.clipTo(a)
        b.invert()
        a.build(b.allPolygons());
        return CSG.fromPolygons(a.allPolygons())

    def __add__(self, csg):
        return self.union(csg)
        
    def subtract(self, csg):
        """
        Return a new CSG solid representing space in this solid but not in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.subtract(B)
        
            +-------+            +-------+
            |       |            |       |
            |   A   |            |       |
            |    +--+----+   =   |    +--+
            +----+--+    |       +----+
                 |   B   |
                 |       |
                 +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.invert()
        a.clipTo(b)
        b.clipTo(a)
        b.invert()
        b.clipTo(a)
        b.invert()
        a.build(b.allPolygons())
        a.invert()
        return CSG.fromPolygons(a.allPolygons())

    def __sub__(self, csg):
        return self.subtract(csg)
        
    def intersect(self, csg):
        """
        Return a new CSG solid representing space both this solid and in the
        solid `csg`. Neither this solid nor the solid `csg` are modified.::
        
            A.intersect(B)
        
            +-------+
            |       |
            |   A   |
            |    +--+----+   =   +--+
            +----+--+    |       +--+
                 |   B   |
                 |       |
                 +-------+
        """
        a = BSPNode(self.clone().polygons)
        b = BSPNode(csg.clone().polygons)
        a.invert()
        b.clipTo(a)
        b.invert()
        a.clipTo(b)
        b.clipTo(a)
        a.build(b.allPolygons())
        a.invert()
        return CSG.fromPolygons(a.allPolygons())

    def __mul__(self, csg):
        return self.intersect(csg)
        
    def inverse(self):
        """
        Return a new CSG solid with solid and empty space switched. This solid is
        not modified.
        """
        csg = self.clone()
        map(lambda p: p.flip(), csg.polygons)
        return csg

    @classmethod
    def cube(cls, center=[0,0,0], radius=[1,1,1]):
        """
        Construct an axis-aligned solid cuboid. Optional parameters are `center` and
        `radius`, which default to `[0, 0, 0]` and `[1, 1, 1]`. The radius can be
        specified using a single number or a list of three numbers, one for each axis.
        
        Example code::
        
            cube = CSG.cube(
              center=[0, 0, 0],
              radius=1
            )
        """
        c = Vector(0, 0, 0)
        r = [1, 1, 1]
        if isinstance(center, list): c = Vector(center[0], center[1], center[2])
        if isinstance(radius, list): r = radius
        else: r = [radius, radius, radius]

        polygons = list(map(
            lambda v: Polygon( 
                list(map(lambda i: 
                    Vertex(
                        Vector(
                            c.x + r[0] * (2 * bool(i & 1) - 1),
                            c.y + r[1] * (2 * bool(i & 2) - 1),
                            c.z + r[2] * (2 * bool(i & 4) - 1)
                        ), 
                        None
                    ), v[0]))),
                    [
                        [[0, 4, 6, 2], [-1, 0, 0]],
                        [[1, 3, 7, 5], [+1, 0, 0]],
                        [[0, 1, 5, 4], [0, -1, 0]],
                        [[2, 6, 7, 3], [0, +1, 0]],
                        [[0, 2, 3, 1], [0, 0, -1]],
                        [[4, 5, 7, 6], [0, 0, +1]]
                    ]))
        return CSG.fromPolygons(polygons)
        
    @classmethod
    def sphere(cls, **kwargs):
        """ Returns a sphere.
            
            Kwargs:
                center (list): Center of sphere, default [0, 0, 0].
                
                radius (float): Radius of sphere, default 1.0.
                
                slices (int): Number of slices, default 16.
                
                stacks (int): Number of stacks, default 8.
        """
        center = kwargs.get('center', [0.0, 0.0, 0.0])
        if isinstance(center, float):
            center = [center, center, center]
        c = Vector(center[0], center[1], center[2])
        r = kwargs.get('radius', 1.0)
        if isinstance(r, list) and len(r) > 2:
            r = r[0]
        slices = kwargs.get('slices', 16)
        stacks = kwargs.get('stacks', 8)
        polygons = []
        def appendVertex(vertices, theta, phi):
            d = Vector(
                math.cos(theta) * math.sin(phi),
                math.cos(phi),
                math.sin(theta) * math.sin(phi))
            vertices.append(Vertex(c.plus(d.times(r)), d))
            
        dTheta = math.pi * 2.0 / float(slices)
        dPhi = math.pi / float(stacks)

        j0 = 0
        j1 = j0 + 1
        for i0 in range(0, slices):
            i1 = i0 + 1
            #  +--+
            #  | /
            #  |/
            #  +
            vertices = []
            appendVertex(vertices, i0 * dTheta, j0 * dPhi)
            appendVertex(vertices, i1 * dTheta, j1 * dPhi)
            appendVertex(vertices, i0 * dTheta, j1 * dPhi)
            polygons.append(Polygon(vertices))

        j0 = stacks - 1
        j1 = j0 + 1
        for i0 in range(0, slices):
            i1 = i0 + 1
            #  +
            #  |\
            #  | \
            #  +--+
            vertices = []
            appendVertex(vertices, i0 * dTheta, j0 * dPhi)
            appendVertex(vertices, i1 * dTheta, j0 * dPhi)
            appendVertex(vertices, i0 * dTheta, j1 * dPhi)
            polygons.append(Polygon(vertices))
            
        for j0 in range(1, stacks - 1):
            j1 = j0 + 0.5
            j2 = j0 + 1
            for i0 in range(0, slices):
                i1 = i0 + 0.5
                i2 = i0 + 1
                #  +---+
                #  |\ /|
                #  | x |
                #  |/ \|
                #  +---+
                verticesN = []
                appendVertex(verticesN, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesN, i2 * dTheta, j2 * dPhi)
                appendVertex(verticesN, i0 * dTheta, j2 * dPhi)
                polygons.append(Polygon(verticesN))
                verticesS = []
                appendVertex(verticesS, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesS, i0 * dTheta, j0 * dPhi)
                appendVertex(verticesS, i2 * dTheta, j0 * dPhi)
                polygons.append(Polygon(verticesS))
                verticesW = []
                appendVertex(verticesW, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesW, i0 * dTheta, j2 * dPhi)
                appendVertex(verticesW, i0 * dTheta, j0 * dPhi)
                polygons.append(Polygon(verticesW))
                verticesE = []
                appendVertex(verticesE, i1 * dTheta, j1 * dPhi)
                appendVertex(verticesE, i2 * dTheta, j0 * dPhi)
                appendVertex(verticesE, i2 * dTheta, j2 * dPhi)
                polygons.append(Polygon(verticesE))
                
        return CSG.fromPolygons(polygons)
    
    @classmethod
    def cylinder(cls, **kwargs):
        """ Returns a cylinder.
            
            Kwargs:
                start (list): Start of cylinder, default [0, -1, 0].
                
                end (list): End of cylinder, default [0, 1, 0].
                
                radius (float): Radius of cylinder, default 1.0.
                
                slices (int): Number of slices, default 16.
        """
        s = kwargs.get('start', Vector(0.0, -1.0, 0.0))
        e = kwargs.get('end', Vector(0.0, 1.0, 0.0))
        if isinstance(s, list):
            s = Vector(*s)
        if isinstance(e, list):
            e = Vector(*e)
        r = kwargs.get('radius', 1.0)
        slices = kwargs.get('slices', 16)
        ray = e.minus(s)

        axisZ = ray.unit()
        isY = (math.fabs(axisZ.y) > 0.5)
        axisX = Vector(float(isY), float(not isY), 0).cross(axisZ).unit()
        axisY = axisX.cross(axisZ).unit()
        start = Vertex(s, axisZ.negated())
        end = Vertex(e, axisZ.unit())
        polygons = []
        
        def point(stack, angle, normalBlend):
            out = axisX.times(math.cos(angle)).plus(
                axisY.times(math.sin(angle)))
            pos = s.plus(ray.times(stack)).plus(out.times(r))
            normal = out.times(1.0 - math.fabs(normalBlend)).plus(
                axisZ.times(normalBlend))
            return Vertex(pos, normal)
            
        dt = math.pi * 2.0 / float(slices)
        for i in range(0, slices):
            t0 = i * dt
            i1 = (i + 1) % slices
            t1 = i1 * dt
            polygons.append(Polygon([start.clone(), 
                                     point(0., t0, -1.), 
                                     point(0., t1, -1.)]))
            polygons.append(Polygon([point(0., t1, 0.), 
                                     point(0., t0, 0.),
                                     point(1., t0, 0.), 
                                     point(1., t1, 0.)]))
            polygons.append(Polygon([end.clone(), 
                                     point(1., t1, 1.), 
                                     point(1., t0, 1.)]))
        
        return CSG.fromPolygons(polygons)

    @classmethod
    def cone(cls, **kwargs):
        """ Returns a cone.
            
            Kwargs:
                start (list): Start of cone, default [0, -1, 0].
                
                end (list): End of cone, default [0, 1, 0].
                
                radius (float): Maximum radius of cone at start, default 1.0.
                
                slices (int): Number of slices, default 16.
        """
        s = kwargs.get('start', Vector(0.0, -1.0, 0.0))
        e = kwargs.get('end', Vector(0.0, 1.0, 0.0))
        if isinstance(s, list):
            s = Vector(*s)
        if isinstance(e, list):
            e = Vector(*e)
        r = kwargs.get('radius', 1.0)
        slices = kwargs.get('slices', 16)
        ray = e.minus(s)
        
        axisZ = ray.unit()
        isY = (math.fabs(axisZ.y) > 0.5)
        axisX = Vector(float(isY), float(not isY), 0).cross(axisZ).unit()
        axisY = axisX.cross(axisZ).unit()
        startNormal = axisZ.negated()
        start = Vertex(s, startNormal)
        polygons = []
        
        taperAngle = math.atan2(r, ray.length())
        sinTaperAngle = math.sin(taperAngle)
        cosTaperAngle = math.cos(taperAngle)
        def point(angle):
            # radial direction pointing out
            out = axisX.times(math.cos(angle)).plus(
                axisY.times(math.sin(angle)))
            pos = s.plus(out.times(r))
            # normal taking into account the tapering of the cone
            normal = out.times(cosTaperAngle).plus(axisZ.times(sinTaperAngle))
            return pos, normal

        dt = math.pi * 2.0 / float(slices)
        for i in range(0, slices):
            t0 = i * dt
            i1 = (i + 1) % slices
            t1 = i1 * dt
            # coordinates and associated normal pointing outwards of the cone's
            # side
            p0, n0 = point(t0)
            p1, n1 = point(t1)
            # average normal for the tip
            nAvg = n0.plus(n1).times(0.5)
            # polygon on the low side (disk sector)
            polyStart = Polygon([start.clone(), 
                                 Vertex(p0, startNormal), 
                                 Vertex(p1, startNormal)])
            polygons.append(polyStart)
            # polygon extending from the low side to the tip
            polySide = Polygon([Vertex(p0, n0), Vertex(e, nAvg), Vertex(p1, n1)])
            polygons.append(polySide)

        return CSG.fromPolygons(polygons)
