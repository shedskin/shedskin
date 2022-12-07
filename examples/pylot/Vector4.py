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

import math

from .Utils import Roughly
#{
import pdb
#}

class Vector4(object):

  def __init__(self, x, y, z, w):
    self.x = float(x)
    self.y = float(y)
    self.z = float(z)
    self.w = float(w)

  def __neg__(self):
    return Vector4(-self.x, -self.y, -self.z, -self.w)

  def __add__(self, other):
    assert self.w + other.w <= 1
    return Vector4(self.x + other.x,
                   self.y + other.y,
                   self.z + other.z,
                   self.w + other.w)

  def __sub__(self, other):
    assert bool(self.w) or not other.w # Can't subtract point from offset
    return Vector4(self.x - other.x,
                   self.y - other.y,
                   self.z - other.z,
                   self.w - other.w)

  def toList(self):
    return [self.x, self.y, self.z, self.w]

  def __repr__(self):
    return "(" + ", ".join([str(i) for i in self.toList()]) + ")"

# Consider __eq__

  def dot(self, other):
#{
    assert type(other) == Vector4
#}
    assert Roughly(self.w, 0.0)
    assert Roughly(other.w, 0.0)
    return self.x * other.x + self.y * other.y + \
           self.z * other.z + self.w * other.w

  def subdot(self, other1, other2):
    return (self.x - other1.x) * other2.x + \
           (self.y - other1.y) * other2.y + \
           (self.z - other1.z) * other2.z + \
           (self.w - other1.w) * other2.w

  def sublen(self, other):
      x = self.x - other.x
      y = self.y - other.y
      z = self.z - other.z
      w = self.w - other.w
      return x*x + y*y + z*z + w*w

  # Note: this defines a right-handed coordinate system, as x.cross(y) == z.
  def cross(self, other):
#{
    assert type(other) == Vector4
#}
    assert not self.w and not other.w
    return Vector4(self.y * other.z - self.z * other.y,
                  -self.x * other.z + self.z * other.x,
                  -self.y * other.x + self.x * other.y,
                  0)

  def componentProduct(self, other):
    return Vector4(self.x * other.x,
                   self.y * other.y,
                   self.z * other.z,
                   self.w * other.w)

  def length(self):
    return math.sqrt(self.length_2())

  def length_2(self):
    return self.dot(self)

  def scale(self, factor):
    return Vector4(self.x * factor, self.y * factor, self.z * factor, self.w)

  def normalize(self):
    assert self.length() > 0
    return self.scale(1 / self.length())
    
  def reflect(self, normal):
    coefAlongNormal = -self.dot(normal)
    extensionAlongNormal = normal.scale(coefAlongNormal)
    return extensionAlongNormal.scale(2) + self

  def refract(self, normal, firstIndex, secondIndex):
    assert firstIndex
    assert secondIndex
    assert Roughly(self.length(), 1)
    assert Roughly(normal.length(), 1)
    coefAlongNormal = self.dot(normal)
    inside = coefAlongNormal > 0
    # opposite^2 + adjacent^2 = hypotenuse^2
    # Here hypotenuse is the input unit vector, so its length is 1.
    opposite = math.sqrt(1 - coefAlongNormal * coefAlongNormal)
    # Likewise sin_t0 = opposite / hypotenuse == opposite.
    sin_first = opposite
    sin_second = sin_first * firstIndex / secondIndex
    if sin_second > 1:
#{
      pdb.set_trace()
#}
      return None # Total reflection
    perp = self.cross(normal)
    if Roughly(0, perp.length_2()):
      # We're aimed pretty much straight on; we don't bend as we go through.
      return self
    perp = perp.normalize()
    along_surface = -perp.cross(normal)
    along_coord = along_surface.scale(sin_second)
    normal_offset = math.sqrt(1 - sin_second * sin_second)
    if not inside: # Going against the surface normal.
      normal_offset = -normal_offset
    normal_coord = normal.scale(normal_offset)
    result = along_coord + normal_coord
    return result

def Point(x, y, z):
  return Vector4(x, y, z, 1)

def Offset(x, y, z):
  return Vector4(x, y, z, 0)

def Zero():
  return Point(0, 0, 0)

def Mean(vectors):
#{
  assert type(vectors) == list
#}
  x, y, z, w = 0, 0, 0, 0
  for v in vectors:
#{
    assert type(v) == Vector4
#}
    x += v.x
    y += v.y
    z += v.z
    w += v.w
  count = float(len(vectors))
  result = Vector4(x / count, y / count, z / count, w / count)
  assert Roughly(result.w, 0) or Roughly(result.w, 1)
  return result

# sin_Ti/sin_Tt = n2 / n1

# Ti = Theta of Incident light [vs. normal] in degrees
def fresnel_reflectance_at_angle(Ti, n1, n2):
  cos_Ti = math.cos(Ti)
  sin_Ti = math.sin(Ti)
  sin_Tt = sin_Ti / n2 * n1
  cos_Tt = 1 - math.sqrt(sin_Tt * sin_Tt)
  return fresnel_reflectance(cos_Ti, cos_Tt, n1, n2)
  
# Ti = Theta of Incident light [vs. normal]
# Tt = Theta of Transmitted light [vs. -normal]
def fresnel_reflectance(cos_Ti, cos_Tt, n1, n2):
  Rs = math.pow((n1 * cos_Ti - n2 * cos_Tt) / (n1 * cos_Ti + n2 * cos_Tt), 2)
  Rp = math.pow((n1 * cos_Tt - n2 * cos_Ti) / (n1 * cos_Tt + n2 * cos_Ti), 2)
  R = (Rs + Rp) / 2
  if R > 1:
    return 1.0
  return R
