# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Kevin Carson
# modified by Tupteq
# modified by Fredrik Johansson
# modified by Tupteq (again)

import sys
from math import sqrt, pi

solar_mass = 4 * pi * pi

def advance(bodies, dt, nbodies):
    for i in xrange(nbodies):
        b = bodies[i]
        b_mass = b.mass
        b_x = b.x
        b_y = b.y
        b_z = b.z

        for j in xrange(i + 1, nbodies):
            b2 = bodies[j]

            dx = b_x - b2.x
            dy = b_y - b2.y
            dz = b_z - b2.z

            distance = sqrt(dx*dx + dy*dy + dz*dz)
            aux = dt / (distance*distance*distance)
            b_mass_x_mag = b_mass * aux
            b2_mass_x_mag = b2.mass * aux

            b.vx -= dx * b2_mass_x_mag
            b.vy -= dy * b2_mass_x_mag
            b.vz -= dz * b2_mass_x_mag
            b2.vx += dx * b_mass_x_mag
            b2.vy += dy * b_mass_x_mag
            b2.vz += dz * b_mass_x_mag

    for i in xrange(nbodies):
        b = bodies[i]
        b.x += dt * b.vx
        b.y += dt * b.vy
        b.z += dt * b.vz


def energy(bodies, nbodies):
    e = 0.0
    for i in xrange(nbodies):
        b = bodies[i]
        e += 0.5 * b.mass * (b.vx*b.vx + b.vy*b.vy + b.vz*b.vz)

        for j in xrange(i + 1, nbodies):
            b2 = bodies[j]

            dx = b.x - b2.x
            dy = b.y - b2.y
            dz = b.z - b2.z
            distance = sqrt(dx*dx + dy*dy + dz*dz)

            e -= (b.mass * b2.mass) / distance
    return e


def offset_momentum(bodies, sun):
    px = py = pz = 0.0

    for b in bodies:
        px += b.vx * b.mass
        py += b.vy * b.mass
        pz += b.vz * b.mass

    sun.vx = - px / solar_mass
    sun.vy = - py / solar_mass
    sun.vz = - pz / solar_mass


class Body:
    pass

def main():
    days_per_year = 365.24

    sun = Body()
    sun.x = sun.y = sun.z = sun.vx = sun.vy = sun.vz = 0.0
    sun.mass = solar_mass

    jupiter = Body()
    jupiter.x = 4.84143144246472090e+00
    jupiter.y = -1.16032004402742839e+00
    jupiter.z = -1.03622044471123109e-01
    jupiter.vx = 1.66007664274403694e-03 * days_per_year
    jupiter.vy = 7.69901118419740425e-03 * days_per_year
    jupiter.vz = -6.90460016972063023e-05 * days_per_year
    jupiter.mass = 9.54791938424326609e-04 * solar_mass

    saturn = Body()
    saturn.x = 8.34336671824457987e+00
    saturn.y = 4.12479856412430479e+00
    saturn.z = -4.03523417114321381e-01
    saturn.vx = -2.76742510726862411e-03 * days_per_year
    saturn.vy = 4.99852801234917238e-03 * days_per_year
    saturn.vz = 2.30417297573763929e-05 * days_per_year
    saturn.mass = 2.85885980666130812e-04 * solar_mass

    uranus = Body()
    uranus.x = 1.28943695621391310e+01
    uranus.y = -1.51111514016986312e+01
    uranus.z = -2.23307578892655734e-01
    uranus.vx = 2.96460137564761618e-03 * days_per_year
    uranus.vy = 2.37847173959480950e-03 * days_per_year
    uranus.vz = -2.96589568540237556e-05 * days_per_year
    uranus.mass = 4.36624404335156298e-05 * solar_mass

    neptune = Body()
    neptune.x = 1.53796971148509165e+01
    neptune.y = -2.59193146099879641e+01
    neptune.z = 1.79258772950371181e-01
    neptune.vx = 2.68067772490389322e-03 * days_per_year
    neptune.vy = 1.62824170038242295e-03 * days_per_year
    neptune.vz = -9.51592254519715870e-05 * days_per_year
    neptune.mass = 5.15138902046611451e-05 * solar_mass

    n = int(sys.argv[1])
    bodies = [sun, jupiter, saturn, uranus, neptune]
    nbodies = len(bodies)
    offset_momentum(bodies, sun)
    print round(energy(bodies, nbodies), 9)

    for i in xrange(n):
        advance(bodies, 0.01, nbodies)
    print round(energy(bodies, nbodies), 9)

main()
