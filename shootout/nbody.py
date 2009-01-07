# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Kevin Carson
# modified by Tupteq
# modified by Fredrik Johansson
# modified by Tupteq (again)

import sys

pi = 3.14159265358979323
solar_mass = 4 * pi * pi
days_per_year = 365.24


def advance(bodies, dt, n):
    # Create all possible pairs first
    #pairs = [(b, b2) for i, b in enumerate(bodies) for b2 in bodies[i+1:]] XXX doesnt compile
    pairs = []
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            pairs.append((bodies[i], bodies[j]))

    for i in xrange(n):
        for b, b2 in pairs:
            dx = b[0] - b2[0]
            dy = b[1] - b2[1]
            dz = b[2] - b2[2]

            mag = dt * (dx*dx + dy*dy + dz*dz)**-1.5
            b_mm = b[6] * mag
            b2_mm = b2[6] * mag

            b[3] -= dx * b2_mm
            b[4] -= dy * b2_mm
            b[5] -= dz * b2_mm
            b2[3] += dx * b_mm
            b2[4] += dy * b_mm
            b2[5] += dz * b_mm

        for b in bodies:
            b[0] += dt * b[3]
            b[1] += dt * b[4]
            b[2] += dt * b[5]

def energy(bodies):
    e = 0.0
    bodies2 = bodies[1:]
    for b in bodies:
        e += 0.5 * b[6] * (b[3]*b[3] + b[4]*b[4] + b[5]*b[5])
        for b2 in bodies2:
            dx = b[0] - b2[0]
            dy = b[1] - b2[1]
            dz = b[2] - b2[2]
            distance = (dx*dx + dy*dy + dz*dz)**0.5
            e -= (b[6] * b2[6]) / distance
        del bodies2[:1]

    return e

def offset_momentum(bodies):
    global sun
    px = py = pz = 0.0

    for b in bodies:
        px -= b[3] * b[6]
        py -= b[4] * b[6]
        pz -= b[5] * b[6]

    sun[3] = px / solar_mass
    sun[4] = py / solar_mass
    sun[5] = pz / solar_mass

sun = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, solar_mass]

jupiter = [
    4.84143144246472090e+00,
    -1.16032004402742839e+00,
    -1.03622044471123109e-01,
    1.66007664274403694e-03 * days_per_year,
    7.69901118419740425e-03 * days_per_year,
    -6.90460016972063023e-05 * days_per_year,
    9.54791938424326609e-04 * solar_mass]

saturn = [
    8.34336671824457987e+00,
    4.12479856412430479e+00,
    -4.03523417114321381e-01,
    -2.76742510726862411e-03 * days_per_year,
    4.99852801234917238e-03 * days_per_year,
    2.30417297573763929e-05 * days_per_year,
    2.85885980666130812e-04 * solar_mass]

uranus = [
    1.28943695621391310e+01,
    -1.51111514016986312e+01,
    -2.23307578892655734e-01,
    2.96460137564761618e-03 * days_per_year,
    2.37847173959480950e-03 * days_per_year,
    -2.96589568540237556e-05 * days_per_year,
    4.36624404335156298e-05 * solar_mass]

neptune = [
    1.53796971148509165e+01,
    -2.59193146099879641e+01,
    1.79258772950371181e-01,
    2.68067772490389322e-03 * days_per_year,
    1.62824170038242295e-03 * days_per_year,
    -9.51592254519715870e-05 * days_per_year,
    5.15138902046611451e-05 * solar_mass]


def main():
    n = int(sys.argv[1])
    bodies = [sun, jupiter, saturn, uranus, neptune]
    offset_momentum(bodies)
    print "%.9f" % energy(bodies)
    advance(bodies, 0.01, n)
    print "%.9f" % energy(bodies)


main()

