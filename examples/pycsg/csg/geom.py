import math
import sys
from functools import reduce

# increase the max number of recursive calls
sys.setrecursionlimit(10000) # my default is 1000, increasing too much may cause a seg fault


class Vector(object):
    """
    class Vector

    Represents a 3D vector.

    Example usage:
         Vector(1, 2, 3);
         Vector([1, 2, 3]);
         Vector({ 'x': 1, 'y': 2, 'z': 3 });
    """
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def clone(self):
        """ Clone. """
        return Vector(self.x, self.y, self.z)

    def negated(self):
        """ Negated. """
        return Vector(-self.x, -self.y, -self.z)

#    def __neg__(self):
#        return self.negated()

    def plus(self, a):
        """ Add. """
        return Vector(self.x+a.x, self.y+a.y, self.z+a.z)

#    def __add__(self, a):
#        return self.plus(a)

    def minus(self, a):
        """ Subtract. """
        return Vector(self.x-a.x, self.y-a.y, self.z-a.z)

#    def __sub__(self, a):
#        return self.minus(a)

    def times(self, a):
        """ Multiply. """
        return Vector(self.x*a, self.y*a, self.z*a)

#    def __mul__(self, a):
#        return self.times(a)

    def dividedBy(self, a):
        """ Divide. """
        return Vector(self.x/a, self.y/a, self.z/a)

#    def __truediv__(self, a):
#        return self.dividedBy(float(a))

#    def __div__(self, a):
#        return self.dividedBy(float(a))

    def dot(self, a):
        """ Dot. """
        return self.x*a.x + self.y*a.y + self.z*a.z

    def lerp(self, a, t):
        """ Lerp. Linear interpolation from self to a"""
        return self.plus(a.minus(self).times(t));

    def length(self):
        """ Length. """
        return math.sqrt(self.dot(self))

    def unit(self):
        """ Normalize. """
        return self.dividedBy(self.length())

    def cross(self, a):
        """ Cross. """
        return Vector(
            self.y * a.z - self.z * a.y,
            self.z * a.x - self.x * a.z,
            self.x * a.y - self.y * a.x)

#    def __getitem__(self, key):
#        return (self.x, self.y, self.z)[key]

#    def __setitem__(self, key, value):
#        l = [self.x, self.y, self.z]
#        l[key] = value
#        self.x, self.y, self.z = l

#    def __len__(self):
#        return 3

#    def __iter__(self):
#        return iter((self.x, self.y, self.z))

#    def __repr__(self):
#        return 'Vector(%.2f, %.2f, %0.2f)' % (self.x, self.y, self.z) 


class Vertex(object):
    """ 
    Class Vertex 

    Represents a vertex of a polygon. Use your own vertex class instead of this
    one to provide additional features like texture coordinates and vertex
    colors. Custom vertex classes need to provide a `pos` property and `clone()`,
    `flip()`, and `interpolate()` methods that behave analogous to the ones
    defined by `Vertex`. This class provides `normal` so convenience
    functions like `CSG.sphere()` can return a smooth vertex normal, but `normal`
    is not used anywhere else.
    """
    def __init__(self, pos, normal=None):
        self.pos = pos.clone()
        if normal is None:
            self.normal = Vector(0, 0, 0)
        else:
            self.normal = normal.clone()

    def clone(self):
        return Vertex(self.pos, self.normal)

    def flip(self):
        """
        Invert all orientation-specific data (e.g. vertex normal). Called when the
        orientation of a polygon is flipped.
        """
        self.normal = self.normal.negated()

    def interpolate(self, other, t):
        """
        Create a new vertex between this vertex and `other` by linearly
        interpolating all properties using a parameter of `t`. Subclasses should
        override this to interpolate additional properties.
        """
        return Vertex(self.pos.lerp(other.pos, t), 
                          self.normal.lerp(other.normal, t))

#    def __repr__(self):
#        return repr(self.pos)


class Plane(object):
    """
    class Plane

    Represents a plane in 3D space.
    """

    """
    `Plane.EPSILON` is the tolerance used by `splitPolygon()` to decide if a
    point is on the plane.
    """
    EPSILON = 1.e-5

    COPLANAR = 0 # all the vertices are within EPSILON distance from plane
    FRONT = 1 # all the vertices are in front of the plane
    BACK = 2 # all the vertices are at the back of the plane
    SPANNING = 3 # some vertices are in front, some in the back

    def __init__(self, normal, w):
        self.normal = normal
        # w is the (perpendicular) distance of the plane from (0, 0, 0)
        self.w = w

    def clone(self):
        return Plane(self.normal.clone(), self.w)

    def flip(self):
        self.normal = self.normal.negated()
        self.w = -self.w

#    def __repr__(self):
#        return 'normal: {0} w: {1}'.format(self.normal, self.w)

    def vertexLocation(self, polygon, i):
        t = self.normal.dot(polygon.vertices[i].pos) - self.w

        loc = -1
        if t < -Plane.EPSILON:
            loc = Plane.BACK
        elif t > Plane.EPSILON:
            loc = Plane.FRONT
        else:
            loc = Plane.COPLANAR

        return loc

    def splitPolygon(self, polygon, coplanarFront, coplanarBack, front, back):
        """
        Split `polygon` by this plane if needed, then put the polygon or polygon
        fragments in the appropriate lists. Coplanar polygons go into either
        `coplanarFront` or `coplanarBack` depending on their orientation with
        respect to this plane. Polygons in front or in back of this plane go into
        either `front` or `back`
        """

        # Classify each point as well as the entire polygon into one of the above
        # four classes.
        numVertices = len(polygon.vertices)

        polygonType = 0
        for i in range(numVertices):
            loc = self.vertexLocation(polygon, i)
            polygonType |= loc

        # Put the polygon in the correct list, splitting it when necessary.
        if polygonType == Plane.COPLANAR:
            normalDotPlaneNormal = self.normal.dot(polygon.plane.normal)
            if normalDotPlaneNormal > 0:
                coplanarFront.append(polygon)
            else:
                coplanarBack.append(polygon)
        elif polygonType == Plane.FRONT:
            front.append(polygon)
        elif polygonType == Plane.BACK:
            back.append(polygon)
        elif polygonType == Plane.SPANNING:
            vertexLocs = []
            for i in range(numVertices):
                vertexLocs.append(self.vertexLocation(polygon, i))
            f = []
            b = []
            for i in range(numVertices):
                j = (i+1) % numVertices
                ti = vertexLocs[i]
                tj = vertexLocs[j]
                vi = polygon.vertices[i]
                vj = polygon.vertices[j]
                if ti != Plane.BACK:
                    f.append(vi)
                if ti != Plane.FRONT:
                    if ti != Plane.BACK:
                        b.append(vi.clone())
                    else:
                        b.append(vi)
                if (ti | tj) == Plane.SPANNING:
                    # interpolation weight at the intersection point
                    t = (self.w - self.normal.dot(vi.pos)) / self.normal.dot(vj.pos.minus(vi.pos))
                    # intersection point on the plane
                    v = vi.interpolate(vj, t)
                    f.append(v)
                    b.append(v.clone())
            if len(f) >= 3: 
                front.append(Polygon(f, polygon.shared))
            if len(b) >= 3: 
                back.append(Polygon(b, polygon.shared))

def planeFromPoints(a, b, c):
    n = b.minus(a).cross(c.minus(a)).unit()
    return Plane(n, n.dot(a))

class Polygon(object):
    """
    class Polygon

    Represents a convex polygon. The vertices used to initialize a polygon must
    be coplanar and form a convex loop. They do not have to be `Vertex`
    instances but they must behave similarly (duck typing can be used for
    customization).

    Each convex polygon has a `shared` property, which is shared between all
    polygons that are clones of each other or were split from the same polygon.
    This can be used to define per-polygon properties (such as surface color).
    """
    def __init__(self, vertices, shared=None):
        self.vertices = vertices
        self.shared = shared
        self.plane = planeFromPoints(vertices[0].pos, vertices[1].pos, vertices[2].pos)

    def clone(self):
        vertices = list(map(lambda v: v.clone(), self.vertices))
        return Polygon(vertices, self.shared)

    def flip(self):
        self.vertices.reverse()
        map(lambda v: v.flip(), self.vertices)
        self.plane.flip()

#    def __repr__(self):
#        return reduce(lambda x,y: x+y,
#                      ['Polygon(['] + [repr(v) + ', ' \
#                                       for v in self.vertices] + ['])'], '')

class BSPNode(object):
    """
    class BSPNode

    Holds a node in a BSP tree. A BSP tree is built from a collection of polygons
    by picking a polygon to split along. That polygon (and all other coplanar
    polygons) are added directly to that node and the other polygons are added to
    the front and/or back subtrees. This is not a leafy BSP tree since there is
    no distinction between internal and leaf nodes.
    """
    def __init__(self, polygons=None):
        self.plane = None # Plane instance
        self.front = None # BSPNode
        self.back = None  # BSPNode
        self.polygons = []
        if polygons:
            self.build(polygons)

    def clone(self):
        node = BSPNode()
        if self.plane: 
            node.plane = self.plane.clone()
        if self.front: 
            node.front = self.front.clone()
        if self.back: 
            node.back = self.back.clone()
        node.polygons = list(map(lambda p: p.clone(), self.polygons))
        return node

    def invert(self):
        """ 
        Convert solid space to empty space and empty space to solid space.
        """
        for poly in self.polygons:
            poly.flip()
        self.plane.flip()
        if self.front: 
            self.front.invert()
        if self.back: 
            self.back.invert()
        temp = self.front
        self.front = self.back
        self.back = temp

    def clipPolygons(self, polygons):
        """ 
        Recursively remove all polygons in `polygons` that are inside this BSP
        tree.
        """
        if not self.plane: 
            return polygons[:]

        front = []
        back = []
        for poly in polygons:
            self.plane.splitPolygon(poly, front, back, front, back)

        if self.front: 
            front = self.front.clipPolygons(front)

        if self.back: 
            back = self.back.clipPolygons(back)
            front.extend(back)

        return front

    def clipTo(self, bsp):
        """ 
        Remove all polygons in this BSP tree that are inside the other BSP tree
        `bsp`.
        """
        self.polygons = bsp.clipPolygons(self.polygons)
        if self.front: 
            self.front.clipTo(bsp)
        if self.back: 
            self.back.clipTo(bsp)

    def allPolygons(self):
        """
        Return a list of all polygons in this BSP tree.
        """
        polygons = self.polygons[:]
        if self.front: 
            polygons.extend(self.front.allPolygons())
        if self.back: 
            polygons.extend(self.back.allPolygons())
        return polygons

    def build(self, polygons):
        """
        Build a BSP tree out of `polygons`. When called on an existing tree, the
        new polygons are filtered down to the bottom of the tree and become new
        nodes there. Each set of polygons is partitioned using the first polygon
        (no heuristic is used to pick a good split).
        """
        if len(polygons) == 0:
            return
        if not self.plane: 
            self.plane = polygons[0].plane.clone()
        # add polygon to this node
        self.polygons.append(polygons[0])
        front = []
        back = []
        # split all other polygons using the first polygon's plane
        i = 1
        while i < len(polygons): ## TODO using range trips up type inference
            # coplanar front and back polygons go into self.polygons
            self.plane.splitPolygon(polygons[i], self.polygons, self.polygons,
                                    front, back)
            i += 1
        # recursively build the BSP tree
        if len(front) > 0:
            if not self.front:
                self.front = BSPNode()
            self.front.build(front)
        if len(back) > 0:
            if not self.back:
                self.back = BSPNode()
            self.back.build(back)


if False:
    polygons = [Polygon([Vertex(Vector(1.,2.,3.))])]
    node = BSPNode(polygons)
    node.clipTo(node)
    node.invert()
    node.allPolygons()
    node.clone()
