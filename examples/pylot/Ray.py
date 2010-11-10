import string
from Vector4 import Vector4
from Color import Color

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
    return "[" + string.join([repr(self.origin), repr(self.offset), ], ", ") + "]"
