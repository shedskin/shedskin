# Textual Voronoi code modified from: <abhishek@ocf.berkeley.edu>
# http://www.ocf.berkeley.edu/~Eabhishek/

import random  # for generateRandomPoints

random.seed(42)
from math import sqrt


def generateRandomPoints(npoints=6):
    """Generate a few random points v1...vn"""
    # print(npoints, "points x,y:")
    points = []
    for i in range(npoints):
        xrand, yrand = random.random(), random.random()
        #        print('%.2f' % xrand, '%.2f' % yrand)
        for xoff in range(-1, 2):
            for yoff in range(-1, 2):
                points.append((xrand + xoff, yrand + yoff))
    return points


def closest(x, y, points):
    """Function to find the closest of the vi."""
    best, good = 99.0 * 99.0, 99.0 * 99.0
    for px, py in points:
        dist = (x - px) * (x - px) + (y - py) * (y - py)
        if dist < best:
            best, good = dist, best
        elif dist < good:
            good = dist
    return sqrt(best) / sqrt(good)


def generateScreen(points, rows=40, cols=80):
    yfact = 1.0 / cols
    xfact = 1.0 / rows
    screen = []
    chars = " -.,+*$&#~~"
    for i in range(rows):
        x = i * xfact
        line = [chars[int(10 * closest(x, j * yfact, points))] for j in range(cols)]
        screen.extend(line)
        screen.append("\n")
    return "".join(screen)

def test_voronoi():
    points = generateRandomPoints(10)
    # print()
    screen = generateScreen(points, 40, 80)
    assert len(screen) == 3240

def test_all():
    test_voronoi()

if __name__ == '__main__':
    test_all()


