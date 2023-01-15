'''
ambient occlusion renderer
http://lucille.atso-net.jp/aobench/

Original version of AO bench was written by Syoyo Fujita. The original code(Proce55ing version) is licensed under BSD3 license. You can freely modify, port and distribute AO bench
'''

from math import sqrt, sin, cos, fabs
import random
from array import array

random.seed(1)

WIDTH = 128
HEIGHT = WIDTH
NSUBSAMPLES = 2
NAO_SAMPLES = 8

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Isect:
    def __init__(self):
        self.p = Vector(0.0, 0.0, 0.0)
        self.n = Vector(0.0, 0.0, 0.0)

    def reset(self):
        self.t = 1.0e+17
        self.hit = 0
        self.p.x = self.p.y = self.p.z = 0.0
        self.n.x = self.n.y = self.n.z = 0.0

class Sphere:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

class Plane:
    def __init__(self, p, n):
        self.p = p
        self.n = n

class Ray:
    def __init__(self):
        self.org = Vector(0.0, 0.0, 0.0)
        self.dir = Vector(0.0, 0.0, 0.0)

    def reset(self, p, x, y, z):
        self.org.x, self.org.y, self.org.z = p.x, p.y, p.z
        self.dir.x, self.dir.y, self.dir.z = x, y, z

def vdot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def vcross(c, v0, v1):
    c.x = v0.y * v1.z - v0.z *v1.y
    c.y = v0.z * v1.x - v0.x *v1.z
    c.z = v0.x * v1.y - v0.y *v1.x

def vnormalize(c):
    length = sqrt(vdot(c, c))

    if fabs(length) > 1.0e-17:
        c.x /= length
        c.y /= length
        c.z /= length

def ray_sphere_intersect(isect, ray, sphere):
    rsx = ray.org.x - sphere.center.x
    rsy = ray.org.y - sphere.center.y
    rsz = ray.org.z - sphere.center.z

    B = rsx * ray.dir.x + rsy * ray.dir.y + rsz * ray.dir.z
    C = rsx * rsx + rsy * rsy + rsz * rsz - sphere.radius * sphere.radius
    D = B * B - C

    if D > 0.0:
        t = -B - sqrt(D)
        if t > 0.0:
            if t < isect.t:
                isect.t = t
                isect.hit = 1

                isect.p.x = ray.org.x + ray.dir.x * t
                isect.p.y = ray.org.y + ray.dir.y * t
                isect.p.z = ray.org.z + ray.dir.z * t

                isect.n.x = isect.p.x - sphere.center.x
                isect.n.y = isect.p.y - sphere.center.y
                isect.n.z = isect.p.z - sphere.center.z

                vnormalize(isect.n)

def ray_plane_intersect(isect, ray, plane):
    d = -vdot(plane.p, plane.n)
    v = vdot(ray.dir, plane.n)

    if abs(v) < 1.0e-17:
        return

    t = -(vdot(ray.org, plane.n) + d) / v

    if t > 0.0:
        if t < isect.t:
            isect.t = t
            isect.hit = 1

            isect.p.x = ray.org.x + ray.dir.x * t
            isect.p.y = ray.org.y + ray.dir.y * t
            isect.p.z = ray.org.z + ray.dir.z * t

            isect.n.x = plane.n.x
            isect.n.y = plane.n.y
            isect.n.z = plane.n.z

def ortho_basis(basis, n):
    basis[2] = n
    basis[1].x = basis[1].y = basis[1].z = 0.0

    if n.x < 0.6 and n.x > -0.6:
        basis[1].x = 1.0
    elif n.y < 0.6 and n.y > -0.6:
        basis[1].y = 1.0
    elif n.z < 0.6 and n.z > -0.6:
        basis[1].z = 1.0
    else:
        basis[1].x = 1.0

    vcross(basis[0], basis[1], basis[2])
    vnormalize(basis[0])

    vcross(basis[1], basis[2], basis[0])
    vnormalize(basis[1])

def ambient_occlusion(col, isect):
    global random_idx
    ntheta = NAO_SAMPLES
    nphi = NAO_SAMPLES
    eps = 0.0001

    p = Vector(isect.p.x + eps * isect.n.x,
               isect.p.y + eps * isect.n.y,
               isect.p.z + eps * isect.n.z)

    basis = [Vector(0.0, 0.0, 0.0) for x in range(3)]
    ortho_basis(basis, isect.n)

    occlusion = 0.0
    b0, b1, b2 = basis[0], basis[1], basis[2]
    isect = Isect()
    ray = Ray()

    for j in range(ntheta):
        for i in range(nphi):
            theta = sqrt(random.random())
            phi = 2.0 * 3.14159265358979323846 * random.random()

            x = cos(phi) * theta
            y = sin(phi) * theta
            z = sqrt(1.0 - theta * theta)

            rx = x * b0.x + y * b1.x + z * b2.x
            ry = x * b0.y + y * b1.y + z * b2.y
            rz = x * b0.z + y * b1.z + z * b2.z
            ray.reset(p, rx, ry, rz)

            isect.reset()

            ray_sphere_intersect(isect, ray, sphere1)
            ray_sphere_intersect(isect, ray, sphere2)
            ray_sphere_intersect(isect, ray, sphere3)
            ray_plane_intersect(isect, ray, plane)

            if isect.hit:
                occlusion += 1.0

    occlusion = (ntheta * nphi - occlusion) / float(ntheta * nphi)
    col.x = col.y = col.z = occlusion

def clamp(f):
    i = int(f * 255.5)
    if i < 0:
        i = 0
    if i > 255:
        i = 255
    return i


def render(w, h, nsubsamples):
    img = [0] * (WIDTH * HEIGHT * 3)

    nsubs = float(nsubsamples)
    nsubs_nsubs = nsubs * nsubs

    v0 = Vector(0.0, 0.0, 0.0)
    col = Vector(0.0, 0.0, 0.0)
    isect = Isect()
    ray = Ray()

    for y in range(h):
        for x in range(w):
            fr = 0.0
            fg = 0.0
            fb = 0.0
            for v in range(nsubsamples):
                for u in range(nsubsamples):
                    px = (x + (u / float(nsubsamples)) - (w/2.0)) / (w/2.0)
                    py = -(y + (v / float(nsubsamples)) - (h/2.0)) / (h/2.0)
                    ray.reset(v0, px, py, -1.0)
                    vnormalize(ray.dir)

                    isect.reset()

                    ray_sphere_intersect(isect, ray, sphere1)
                    ray_sphere_intersect(isect, ray, sphere2)
                    ray_sphere_intersect(isect, ray, sphere3)
                    ray_plane_intersect(isect, ray, plane)

                    if isect.hit:
                        ambient_occlusion(col, isect)
                        fr += col.x
                        fg += col.y
                        fb += col.z

            img[3 * (y * w + x) + 0] = clamp(fr / nsubs_nsubs)
            img[3 * (y * w + x) + 1] = clamp(fg / nsubs_nsubs)
            img[3 * (y * w + x) + 2] = clamp(fb / nsubs_nsubs)

    return img


def init_scene():
    global sphere1, sphere2, sphere3, plane
    sphere1 = Sphere(Vector(-2.0, 0.0, -3.5), 0.5)
    sphere2 = Sphere(Vector(-0.5, 0.0, -3.0), 0.5)
    sphere3 = Sphere(Vector(1.0, 0.0, -2.2), 0.5)
    plane = Plane(Vector(0.0, -0.5, 0.0), Vector(0.0, 1.0, 0.0))

def save_ppm(img, w, h, fname):
    fout = open(fname, "wb")
    fout.write(b'P6\n')
    fout.write(b"%i %i\n" % (w, h))
    fout.write(b"255\n")
    array("B", img).tofile(fout)
    fout.close()

if __name__ == '__main__':
    init_scene()
    img = render(WIDTH, HEIGHT, NSUBSAMPLES)
    save_ppm(img, WIDTH, HEIGHT, "mao.ppm")
