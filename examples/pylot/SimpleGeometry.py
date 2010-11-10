from Camera import Camera
from Shape import *
from Vector4 import Vector4, Point, Offset
import Material
import Color
import math
# For Shedskin:
from World import World

COLS = 512
ROWS = 512
EYE = Point(5, 1, 5)
TARGET = Point(0, 0, 0)
UP = Point(0, 2, 0)
DISTANCE = 1
W = 0.3
H = 0.3

EYE2 = Point(0, 2, 0)
UP2 = Point(0, 2, -1)
COLS2 = 256
ROWS2 = 256

# Note: call these AFTER getGeometry as their inputs may change!
def getCamera(world):
  return Camera(world, EYE, TARGET, UP, DISTANCE, W, H, COLS, ROWS)

def getCamera2(world):
  return Camera(world, EYE2, TARGET, UP2, DISTANCE, W, H, COLS2, ROWS2)

useGeometry = 3

def getGeometry():
  global EYE
  global TARGET
  global W
  global H
  global DISTANCE
  global UP
  global COLS
  global ROWS
  if useGeometry == 1:
    TARGET = Point(.125, 0.5, 0)
    W = 0.2
    H = 0.2
    geometry = [
                 Sphere(Point(0, 0, 0), 0.5, name="Red Sphere",
                        material=Material.RED_SPEC),
                 Sphere(Point(0, 0.75, 0), 0.125, name="Blue Sphere",
                        material=Material.BLUE_SPEC),
                 Sphere(Point(0, 0, -1.5), 1.0,
                        material=Material.MIRROR,
                        name="Mirror Sphere"),
                 Sphere(Point(3, 6, 0), 0.125, color="white",
                        material=Material.WHITE_LIGHT),
               ]

  elif useGeometry == 3:
    EYE = Point(0, 0, 2)
    TARGET = Point(0, 0, 0)
    W = 0.75
    H = 0.75
    DISTANCE = 1
    geometry = []
    s0 = SquareAt(Point(0.5, 0, 0),
                  Offset(0, 0, 1),
                  Offset(0, 1, 0),
                  0.5, material=Material.GREEN_FLAT, name="Green Wall")
    s1 = SquareAt(Point(-0.5, 0, 0),
                  Offset(0, 0, -1),
                  Offset(0, 1, 0),
                  0.5, material=Material.RED_FLAT, name="Red Wall")
    s2 = SquareAt(Point(0, 0, -0.5),
                  Offset(1, 0, 0),
                  Offset(0, 1, 0),
                  0.5, material=Material.BLUE_FLAT, name="Blue Wall")
    s3 = SquareAt(Point(0, -0.5, 0),
                  Offset(1, 0, 0),
                  Offset(0, 0, -1),
                  0.5, material=Material.WHITE_FLAT, name="Floor")
    s4 = SquareAt(Point(0, 0.5, 0),
                  Offset(1, 0, 0),
                  Offset(0, 0, 1),
                  0.5, material=Material.WHITE_LIGHT, name="Ceiling")
#    fast_lighting = True
#    if fast_lighting:
#      geometry = [Sphere(Point(0, 0.37, 0), 0.05,
#                  material=Material.BRIGHT_LIGHT, name="Light source 1"),
#                  Sphere(Point(0, -0.37, -0.2), 0.05,
#                  material=Material.BRIGHT_LIGHT, name="Light source 2"),
#                  Sphere(Point(-0.37, 0.15, 0), 0.05,
#                  material=Material.BRIGHT_LIGHT, name="Light source 3"),
#                  Sphere(Point(0.37, 0.37, 0), 0.05,
#                  material=Material.BRIGHT_LIGHT, name="Light source 4"),
#                 ]
#    else:
#      geometry = []
#      for a in [-1, 1]:
#        c = CubeAt(Point(0, a * 0.40, 0), Offset(1, 0, 0), Offset(0, 1, 0),
#                   0.10, material=Material.WHITE_LIGHT)
#        geometry += c
    geometry += [s0, s1, s2, s3, s4]
    geometry += [
#                 Sphere(Point(-0.25, 0.25, -0.1), 0.2,
#                        material=Material.MIRROR,
#                        name="Mirror Sphere"),
#                 Sphere(Point(0.25, 0.0, -0.2), 0.15,
#                        material=Material.RED_MIRROR,
#                        name="Red Mirror Sphere"),
#                 Sphere(Point(0, -0.25, -0.25), 0.15,
#                        material=Material.MIRROR,
#                        name="Back Mirror Sphere"),
#                 Sphere(Point(0.25, 0, 0), 0.2,
#                        name="Purple Sphere", material=Material.PURPLE_SPEC),
                 Sphere(Point(-0.1, -0.1, 0.4), 0.20,
                        material=Material.GLASS,
                        name="Refracting Sphere"),
                ]
    geometry += CubeAt(Point(-0.1, -0.1, 0.4),
                       Offset(1, 0, -1), Offset(0, 1, 0), 0.05,
                       material=Material.DARK_MIRROR,
                       name="Core Cube")
#    geometry += CubeAt(Point(0.3, -0.25, 0), Offset(1, 0, -1), Offset(0, 1, 0),
#                       0.20, material=Material.GLASS, name="Right Cube")
#    geometry += CubeAt(Point(-0.3, -0.2, 0.4), Offset(1, 0, 0),
#                       Offset(0, 1, 0), 0.25, material=Material.GLASS,
#                       name="Left Cube")
  elif useGeometry == 4:
    EYE = Point(0, 0, 2)
    TARGET = Point(0, -0.25, 0)
    factor = 10
    H = 0.375 / 8
    W = H * factor
    COLS = ROWS * factor
    DISTANCE = 1
    s0 = SquareAt(Point(0.5, 0, 0),
                  Offset(0, 0, 1),
                  Offset(0, 1, 0),
                  0.5, material=Material.GREEN_FLAT, name="Green Wall")
    s1 = SquareAt(Point(-0.5, 0, 0),
                  Offset(0, 0, -1),
                  Offset(0, 1, 0),
                  0.5, material=Material.RED_FLAT, name="Red Wall")
    s2 = SquareAt(Point(0, 0, -0.5),
                  Offset(1, 0, 0),
                  Offset(0, 1, 0),
                  0.5, material=Material.BLUE_FLAT, name="Blue Wall")
    s3 = SquareAt(Point(0, -0.5, 0),
                  Offset(1, 0, 0),
                  Offset(0, 0, -1),
                  0.5, material=Material.WHITE_FLAT, name="Floor")
    s4 = SquareAt(Point(0, 0.5, 0),
                  Offset(1, 0, 0),
                  Offset(0, 0, 1),
                  0.5, material=Material.WHITE_FLAT, name="Ceiling")
    geometry = [s0, s1, s2, s3, s4]
#    geometry += [Sphere(Point(0, 0.47, 0), 0.05,
#                        material=Material.WHITE_LIGHT, name="Light source 1"),
#                 Sphere(Point(0, -0.47, 0), 0.05,
#                        material=Material.WHITE_LIGHT, name="Light source 2"),
#                 Sphere(Point(0, 0, 5), 0.05,
#                        material=Material.WHITE_LIGHT, name="Light source 3"),
#                ]
    other_offset = Offset(0.05, 0, 0)
    for t in [t * 10 for t in range(9)]:
#    for t in [t * 10 for t in [3, 4]]:
      x = -0.4 + 0.01 * t
      y = -0.25
      z = 0
      center = Point(x, y, z)
      cube_radius = 0.045 / 2
      right = Offset(0, math.sin(t), -math.cos(t))
      up = Offset(0, math.cos(t), math.sin(t))
      other_center = center + other_offset
      geometry += CubeAt(other_center, right, up, cube_radius,
                         material=Material.BLUE_SPEC,
                         name=("Cube " + repr(t)))
      geometry += CubeAt(center, right, up, cube_radius,
                         material=Material.GLASS, name=("Cube " + repr(t)))
      geometry += [Sphere(center + Offset(0.05, 0.25, -0.25), 0.1,
                         material=Material.BRIGHT_LIGHT)]
#    x = 0
#    y = -0.25
#    z = 0
#    center = Point(x, y, z)
#    cube_radius = 0.045 / 2
#    right = Offset(1, 0, 0)
#    up = Offset(0, 1, 0)
#    geometry += CubeAt(center, right, up, cube_radius,
#                       material=Material.PURPLE_FLAT, name="Cube")
  else:
    geometry = [
                 Sphere(Point(1, 0, 0), 0.5, name="Red Sphere",
                        material=Material.RED_SPEC),
                 Sphere(Point(0, 1, 0), 0.5, name="Blue Sphere",
                        material=Material.BLUE_SPEC),
                 Sphere(Point(0, 0, 1), 0.5,
                        material=Material.MIRROR,
                        name="Mirror Sphere"),
                 Sphere(Point(1, 1, 1), 0.125, name="Light source",
                        material=Material.WHITE_LIGHT),
                 Tri([
                      Point(1, 0, 0),
                      Point(0, 1, 0),
                      Point(0, 0, 1)
                      ])
               ]
  return geometry

def getWorld(geometry):
    return World(geometry)

# XXX
if __name__ == '__main__':
  geometry = getGeometry()
  world = getWorld(geometry)
  camera = getCamera(world)
  camera = getCamera2(world)
  print camera.runPixelRange(((0,5), (0,5)))
