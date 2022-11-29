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

from .Ray import Ray
from .Shape import Shape, HitResult
from .Utils import Roughly


class World(object):
  def __init__(self, shapes):
#{
    assert type(shapes) == list
    for shape in shapes:
      assert isinstance(shape, Shape)
#}
    self.shapes = shapes

  def __repr__(self):
    return repr(self.shapes)

  def intersect(self, ray, ignore=None, inside=None, insideMaterial=None):
#{
    assert isinstance(ray, Ray)
#}
    assert Roughly(ray.offset.length(), 1)
    result = HitResult()

    for shape in self.shapes:
      if shape is not ignore:
        insideThisShape = shape is inside
        bidirectional = (inside is None) and (insideMaterial is shape.material)
        hit = shape.hitTest(ray,
                            bidirectional=bidirectional,
                            best=result,
                            inside=insideThisShape)
    return result

  def lightSources(self):
    return [s for s in self.shapes if s.material.isLightSource()]
