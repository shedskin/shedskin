# Copyright 2010 Eric Uhrhane.
#
# This file is part of Pylot.
#
# Pylot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pylot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.import math

import copy
import math

from .Ray import Ray
from .Utils import *
from .Vector4 import Vector4, Mean, Point
from . import Material

SHAPE_NAME_COUNTER = 0

class HitResult(object):
  def __init__(self):
      self.hit = False

  def update(self, shape, distance, inverted):
      self.hit = True
      self.shape = shape
      self.distance = distance
      self.inverted = inverted

  def __lt__(self, other):
      return self.distance < other.distance

  def __eq__(self, other):
      return self.distance == other.distance

  def __repr__(self):
    return "[HitResult: " + repr(self.distance) + ":" + repr(self.shape) + \
        " inverted: " + repr(self.inverted) + "]"

HIT = HitResult()

class Shape(object):
  def __init__(self, material=None, name=None):
    self.material = material
    if not self.material:
      self.material = Material.GREY_FLAT
    self.name = name
    if not self.name:
      global SHAPE_NAME_COUNTER
      self.name = "Shape %d" % SHAPE_NAME_COUNTER
      SHAPE_NAME_COUNTER += 1

  # If bidirectional is set, check for hits with normals inverted as well as
  # non-inverted.
  # If inside is set, only check for hits from the inside.
  def hitTest(self, ray, bidirectional=False, inside=False, best=None):
    assert not inside or not bidirectional
    assert False # Must override.

  # Used to do shadow ray calculations; later we should be able to return a list
  # of locations for soft shadows.
  def getLocation(self):
    assert False # Must override.
    return Vector4(0, 0, 0, 1)

  # Used to do lighting calculations.
  def getNormal(self, location):
    assert False # Must override.
    return Vector4(0, 0, 0, 0)

  # Used to scale lighting intensity as seen at a given point.  For example,
  # spherical lights die off as r^2, and triangular lights are dimmer if their
  # normal doesn't point at you.  This should return a float between 0 and 1.
  def getIntensity(self, location):
    assert False # Must override
    return 0.0

  def __repr__(self):
    return "[Shape: " + self.name + ", " + repr(self.material) + "]"

class Sphere(Shape):
  def __init__(self, center, radius, material=None, name=None):
    if not name:
      global SHAPE_NAME_COUNTER
      name = "Sphere %d" % SHAPE_NAME_COUNTER
      SHAPE_NAME_COUNTER += 1
    super(Sphere,self).__init__(
        name=name, material=material)
#{
    assert type(center) == Vector4
#}
    assert center.w == 1
    self.center = center
    self.radius = radius
    self.r_2 = radius * radius

  def __repr__(self):
    return "[" + self.name + ": " + repr(self.center) + ", " + \
        repr(self.radius) + "]"

  def hitTest(self, ray, bidirectional=False, inside=False, best=None):
#{
    assert isinstance(ray, Ray)
#}
    assert not inside or not bidirectional
    assert Roughly(ray.offset.length(), 1.0)
    # Here deal with originToSphereDistance_2 and insideMaterial.
    B = ray.origin.subdot(self.center, ray.offset)
    C = ray.origin.sublen(self.center) - self.radius * self.radius
    D = B * B - C
    if (D >= 0):
      sqrtD = math.sqrt(D)
      inverted = False
      if inside or bidirectional:
        # We're coming in through the surface of the sphere, so we only want
        # the far intersection.
        distance = -B + sqrtD
        inverted = True
      else:
        distance = -B - sqrtD
      if 0 <= distance and (not best.hit or distance < best.distance):
          best.update(self, distance, inverted)

  def getLocation(self):
    return self.center

  def getNormal(self, location):
    return (location - self.center).normalize()

  def getIntensity(self, point):
    dist_2 = point.sublen(self.center)
    if dist_2 < self.r_2:
      return 1
    else:
      return self.r_2 / dist_2

class Polygon(Shape):
  def __init__(self, points, material=None, name=None):
    if not name:
      global SHAPE_NAME_COUNTER
      name = "Polygon %d" % SHAPE_NAME_COUNTER
      SHAPE_NAME_COUNTER += 1
    super(Polygon,self).__init__(
        name=name, material=material)
#{
    assert type(points) == list
#}
    count = len(points)
    assert count >= 3
    for index in range(len(points)):
#{
      assert type(points[index]) == Vector4
#}
      assert Roughly(points[index].w, 1)
      assert NonZero(
          (points[(index + 2) % count] - points[index]).cross(
           points[(index + 1) % count] - points[index]).length())

    self.points = copy.copy(points)
    edge01 = points[1] - points[0]
    edge02 = points[2] - points[0]
    self.normal = (edge01).cross(edge02).normalize()
    self.center = Mean(points)
    self.r_2 = max([p.sublen(self.center) for p in points])

  def __repr__(self):
    return "[" + self.name + ": " + repr(self.points) + "; center: " + \
        repr(self.center) + "; normal: " + repr(self.normal) + "]"

  def hitTest(self, ray, bidirectional=False, inside=False, best=None):
#{
    assert isinstance(ray, Ray)
#}
    assert not inside or not bidirectional
    assert Roughly(ray.offset.length(), 1.0)
    if inside: # Only spheres can be hit from the inside.
      return
    hit = rayHitsPlane(self.normal, self.center, ray, bidirectional)
    if hit.hit:
      if 0 <= hit.distance and (not best.hit or hit.distance < best.distance):
         location = ray.origin + ray.offset.scale(hit.distance)
         if self.pointInPolygon(location, hit.inverted):
             best.update(self, hit.distance, hit.inverted)

  def getLocation(self):
    return self.center

  def getNormal(self, location):
    return self.normal

  def getIntensity(self, point):
    intensity = 0.0
    for index in range(len(self.points) - 2):
      intensity += solidAngle(point,
                              [self.points[0]] + self.points[index+1:index+3])
    return intensity

# Assumes the point's in our plane.
  def pointInPolygon(self, point, invertTest):
    if point.sublen(self.center) > self.r_2:
      return False # Outside bounding circle.

    factor = 1.0
    if invertTest:
      factor = -1.0

    count = len(self.points)
    legs = [p - point for p in self.points]
    # Use cross products as a type of winding number indicator.  This works
    # only for convex polygons, and is almost certainly not the fastest way to
    # do this, but it sure is simple.
    for l in range(count):
      if legs[l].cross(legs[(l + 1) % count]).dot(self.normal) * factor < 0.0:
        return False
    return True

def Tri(points, material=None, name=None):
  assert len(points) == 3
  if not name:
    global SHAPE_NAME_COUNTER
    name = "Tri %d" % SHAPE_NAME_COUNTER
    SHAPE_NAME_COUNTER += 1
  return Polygon(points, material=material, name=name)

def Quad(points, material=None, name=None):
  assert len(points) == 4
  if not name:
    global SHAPE_NAME_COUNTER
    name = "Quad %d" % SHAPE_NAME_COUNTER
    SHAPE_NAME_COUNTER += 1
  return Polygon(points, material=material, name=name)

def ParallelogramAt(center, right, up, half_width, half_height, material=None,
                    name=None):
  right = right.normalize()
  up = up.normalize()
  right = right.scale(half_width)
  up = up.scale(half_height)
  p0 = center - right - up
  p1 = center + right - up
  p2 = center + right + up
  p3 = center - right + up
  q = Quad([
            Point(p0.x, p0.y, p0.z),
            Point(p1.x, p1.y, p1.z),
            Point(p2.x, p2.y, p2.z),
            Point(p3.x, p3.y, p3.z),
           ], material=material, name=name)
  return q
  
def SquareAt(center, right, up, radius, material=None, name=None):
  right = right.normalize()
  up = up.normalize()
  normal = right.cross(up).normalize()
  up = normal.cross(right)
  return ParallelogramAt(center, right, up, radius, radius,
                     material=material, name=name)

def ParallelepipedAt(center, right, up, deep, half_width, half_height,
                     half_depth, material=None, name=None):
  right = right.normalize()
  up = up.normalize()
  deep = deep.normalize()
  right = right.scale(half_width)
  left = -right
  up = up.scale(half_height)
  down = -up
  deep = deep.scale(half_depth)
  shallow = -deep
  if name:
    names = \
        [name + ":" + s for s in
            ["back", "front", "right", "left", "top", "bottom"]]
  else:
    names = [None for i in range(6)]
  return [
    # back
    ParallelogramAt(center + deep, left, up, half_width, half_height, material,
                    names[0]),
    # front
    ParallelogramAt(center + shallow, right, up, half_width, half_height,
                    material, names[1]),
    # right
    ParallelogramAt(center + right, deep, up, half_depth, half_height, material,
                    names[2]),
    # left
    ParallelogramAt(center + left, shallow, up, half_depth, half_height,
                    material, names[3]),
    # top
    ParallelogramAt(center + up, left, shallow, half_width, half_depth,
                    material, names[4]),
    # bottom
    ParallelogramAt(center + down, right, shallow, half_width, half_depth,
                    material, names[5])
  ]

def CubeAt(center, right, up, radius, material=None, name=None):
  right = right.normalize()
  up = up.normalize()
  deep = -right.cross(up).normalize()
  up = -deep.cross(right)
  return ParallelepipedAt(center, right, up, deep, radius, radius, radius,
                          material, name)

# Returns (distance, hitLocation) or None
def rayHitsPlane(normal, point, ray, bidirectional=False):
#{
  assert isinstance(ray, Ray)
#}
  assert Roughly(ray.offset.length(), 1.0)
  inverted = False
  dot = normal.dot(ray.offset)
  HIT.hit = False
  if -0.000001 < dot < 0.000001:
    return HIT
  if bidirectional and dot > 0.0:
    normal = -normal
    dot = -dot
    inverted = True
  if (dot < 0.0): # Else it's parallel or facing away.
    # Vector from ray origin to center of polygon [a random point on the
    # plane].
    # Offset to nearest point on the plane from ray origin.
    distanceToPlane = -point.subdot(ray.origin, normal)
    if distanceToPlane > 0.0: # Else it's behind ray.
      progressTowardPlane = -dot
      distance = distanceToPlane / progressTowardPlane
      HIT.hit = True
      HIT.distance = distance
      HIT.inverted = inverted
  return HIT

# Algorithm taken from the equations at
# http://en.wikipedia.org/wiki/Solid_angle#Tetrahedron
def solidAngle(origin, points):
  a = points[0] - origin
  b = points[1] - origin
  c = points[2] - origin
  a_len = a.length()
  b_len = b.length()
  c_len = c.length()
  determinant = math.fabs(a.dot(b.cross(c)))
  bottom = a_len * b_len * c_len + a.dot(b) * c_len + \
                                   a.dot(c) * b_len + \
                                   b.dot(c) * a_len
  half_omega = math.atan2(determinant, bottom)
  if half_omega < 0:
    half_omega += math.pi
  return half_omega * 2
