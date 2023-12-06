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

from .Vector4 import Vector4

class Ray(object):
  def __init__(self, origin, offset):
#{
    assert type(origin) == Vector4
    assert type(offset) == Vector4
#}
    assert origin.w == 1
    assert offset.w == 0
    self.origin = origin
    self.offset = offset

  def __repr__(self):
    return "[" + ', '.join([repr(self.origin), repr(self.offset)]) + "]"
