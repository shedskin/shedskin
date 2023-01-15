from random import random
from math import sqrt
import sys

# path tracer, (c) jonas wagner (http://29a.ch/)
# http://29a.ch/2010/5/17/path-tracing-a-cornell-box-in-javascript
# converted to Python by <anonymous>

ITERATIONS = 10  # should be much higher for good quality


class V3(object):
    def __init__(self, x_, y_, z_):
        self.x = x_
        self.y = y_
        self.z = z_

    def add(self, v):
        return V3(self.x + v.x, self.y + v.y, self.z + v.z)

    def iadd(self, v):
        self.x += v.x
        self.y += v.y
        self.z += v.z

    def sub(self, v):
        return V3(self.x - v.x, self.y - v.y, self.z - v.z)

    def subdot(self, v, u):
        return (self.x - v.x) * u.x + (self.y - v.y) * u.y + (self.z - v.z) * u.z

    def subdot2(self, v):
        return (self.x - v.x) ** 2 + (self.y - v.y) ** 2 + (self.z - v.z) ** 2

    def mul(self, v):
        return V3(self.x * v.x, self.y * v.y, self.z * v.z)

    def div(self, v):
        return V3(self.x / v.x, self.y / v.y, self.z / v.z)

    def muls(self, s):
        return V3(self.x * s, self.y * s, self.z * s)

    def divs(self, s):
        return self.muls(1.0 / s)

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def normalize(self):
        return self.divs(sqrt(self.dot(self)))


def getRandomNormalInHemisphere(v):
    """
    This is my crude way of generating random normals in a hemisphere.
    In the first step I generate random vectors with components
    from -1 to 1. As this introduces a bias I discard all the points
    outside of the unit sphere. Now I've got a random normal vector.
    The last step is to mirror the poif it is in the wrong hemisphere.
    """
    while True:
        v2 = V3(random() * 2.0 - 1.0, random() * 2.0 - 1.0, random() * 2.0 - 1.0)
        v2_dot = v2.dot(v2)
        if v2_dot <= 1.0:
            break

    # should only require about 1.9 iterations of average
    # v2 = v2.normalize()
    v2 = v2.divs(sqrt(v2_dot))

    # if the pois in the wrong hemisphere, mirror it
    if v2.dot(v) < 0.0:
        return v2.muls(-1)
    return v2


class Ray(object):
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction


class Camera(object):
    """
    The camera is defined by an eyepo(origin) and three corners
    of the view plane (it's a rect in my case...)
    """

    def __init__(self, origin, topleft, topright, bottomleft):
        self.origin = origin
        self.topleft = topleft
        self.topright = topleft
        self.bottomleft = bottomleft

        self.xd = topright.sub(topleft)
        self.yd = bottomleft.sub(topleft)

    def getRay(self, x, y):
        # poon screen plane
        p = self.topleft.add(self.xd.muls(x)).add(self.yd.muls(y))
        return Ray(self.origin, p.sub(self.origin).normalize())


class Sphere(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.radius2 = radius * radius

    # returns distance when ray intersects with sphere surface
    def intersect(self, ray):
        b = ray.origin.subdot(self.center, ray.direction)
        c = ray.origin.subdot2(self.center) - self.radius2
        d = b * b - c
        return (-b - sqrt(d)) if d > 0 else -1.0

    def getNormal(self, point):
        return point.sub(self.center).normalize()


class Material(object):
    def __init__(self, color, emission=None):
        self.color = color
        self.emission = V3(0.0, 0.0, 0.0) if emission is None else emission

    def bounce(self, ray, normal):
        return getRandomNormalInHemisphere(normal)


class Chrome(Material):
    def __init__(self, color):
        super(Chrome, self).__init__(color)

    def bounce(self, ray, normal):
        theta1 = abs(ray.direction.dot(normal))
        return ray.direction.add(normal.muls(theta1 * 2.0))


class Glass(Material):
    def __init__(self, color, ior, reflection):
        super(Glass, self).__init__(color)
        self.ior = ior
        self.reflection = reflection

    def bounce(self, ray, normal):
        theta1 = abs(ray.direction.dot(normal))
        if theta1 >= 0.0:
            internalIndex = self.ior
            externalIndex = 1.0
        else:
            internalIndex = 1.0
            externalIndex = self.ior
        eta = externalIndex / internalIndex
        theta2 = sqrt(1.0 - (eta * eta) * (1.0 - (theta1 * theta1)))
        rs = (externalIndex * theta1 - internalIndex * theta2) / (
            externalIndex * theta1 + internalIndex * theta2
        )
        rp = (internalIndex * theta1 - externalIndex * theta2) / (
            internalIndex * theta1 + externalIndex * theta2
        )
        reflectance = rs * rs + rp * rp
        # reflection
        if random() < reflectance + self.reflection:
            return ray.direction.add(normal.muls(theta1 * 2.0))
        # refraction
        return (
            ray.direction.add(normal.muls(theta1)).muls(eta).add(normal.muls(-theta2))
        )


class Body(object):
    def __init__(self, shape, material):
        self.shape = shape
        self.material = material


class Output(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Scene(object):
    def __init__(self, output, camera, objects):
        self.output = output
        self.camera = camera
        self.objects = objects


class Renderer(object):
    def __init__(self, scene):
        self.scene = scene
        self.buffer = [
            V3(0.0, 0.0, 0.0) for i in range(scene.output.width * scene.output.height)
        ]

    def clearBuffer(self):
        for i in range(len(self.buffer)):
            self.buffer[i].x = 0.0
            self.buffer[i].y = 0.0
            self.buffer[i].z = 0.0

    def iterate(self):
        scene = self.scene
        w = scene.output.width
        h = scene.output.height
        i = 0
        # randomly jitter pixels so there is no aliasing
        y = random() / h
        ystep = 1.0 / h
        while y < 0.99999:
            x = random() / w
            xstep = 1.0 / w
            while x < 0.99999:
                ray = scene.camera.getRay(x, y)
                color = self.trace(ray, 0)
                self.buffer[i].iadd(color)
                i += 1
                x += xstep
            y += ystep

    def trace(self, ray, n):
        mint = float("inf")

        # trace no more than 5 bounces
        if n > 4:
            return V3(0.0, 0.0, 0.0)

        hit = None

        for i in range(len(self.scene.objects)):
            o = self.scene.objects[i]
            t = o.shape.intersect(ray)
            if t > 0 and t <= mint:
                mint = t
                hit = o

        if hit is None:
            return V3(0.0, 0.0, 0.0)

        point = ray.origin.add(ray.direction.muls(mint))
        normal = hit.shape.getNormal(point)
        direction = hit.material.bounce(ray, normal)
        # if the ray is refractedmove the intersection poa bit in
        if direction.dot(ray.direction) > 0.0:
            point = ray.origin.add(ray.direction.muls(mint * 1.0000001))
            # otherwise move it out to prevent problems with floating point
            # accuracy
        else:
            point = ray.origin.add(ray.direction.muls(mint * 0.9999999))
        newray = Ray(point, direction)
        return (
            self.trace(newray, n + 1).mul(hit.material.color).add(hit.material.emission)
        )

    @staticmethod
    def cmap(x):
        return 0 if x < 0.0 else (255 if x > 1.0 else int(x * 255))

    # / Write image to PPM file
    def saveFrame(self, filename, nframe):
        fout = open(filename, "w")
        fout.write(
            "P3\n%d %d\n%d\n" % (self.scene.output.width, self.scene.output.height, 255)
        )
        for p in self.buffer:
            fout.write(
                "%d %d %d\n"
                % (
                    Renderer.cmap(p.x / nframe),
                    Renderer.cmap(p.y / nframe),
                    Renderer.cmap(p.z / nframe),
                )
            )
        fout.close()


def main():
    width = 320
    height = 240

    scene = Scene(
        Output(width, height),
        Camera(
            V3(0.0, -0.5, 0.0),
            V3(-1.3, 1.0, 1.0),
            V3(1.3, 1.0, 1.0),
            V3(-1.3, 1.0, -1.0),
        ),
        [
            # glowing sphere
            # Body(Sphere(V3(0.0, 3.0, 0.0), 0.5), Material(V3(0.9, 0.9, 0.9), V3(1.5, 1.5, 1.5))),
            # glass sphere
            Body(Sphere(V3(1.0, 2.0, 0.0), 0.5), Glass(V3(1.00, 1.00, 1.00), 1.5, 0.1)),
            # chrome sphere
            Body(Sphere(V3(-1.1, 2.8, 0.0), 0.5), Chrome(V3(0.8, 0.8, 0.8))),
            # floor
            Body(Sphere(V3(0.0, 3.5, -10e6), 10e6 - 0.5), Material(V3(0.9, 0.9, 0.9))),
            # back
            Body(Sphere(V3(0.0, 10e6, 0.0), 10e6 - 4.5), Material(V3(0.9, 0.9, 0.9))),
            # left
            Body(Sphere(V3(-10e6, 3.5, 0.0), 10e6 - 1.9), Material(V3(0.9, 0.5, 0.5))),
            # right
            Body(Sphere(V3(10e6, 3.5, 0.0), 10e6 - 1.9), Material(V3(0.5, 0.5, 0.9))),
            # top light, the emmision should be close to that of warm sunlight (~5400k)
            Body(
                Sphere(V3(0.0, 0.0, 10e6), 10e6 - 2.5),
                Material(V3(0.0, 0.0, 0.0), V3(1.6, 1.47, 1.29)),
            ),
            # front
            Body(Sphere(V3(0.0, -10e6, 0.0), 10e6 - 2.5), Material(V3(0.9, 0.9, 0.9))),
        ],
    )

    renderer = Renderer(scene)

    nframe = 0
    for count in range(ITERATIONS):
        renderer.iterate()
        sys.stdout.write("*")
        sys.stdout.flush()
        nframe += 1

    renderer.saveFrame("pt.ppm", nframe)


main()
