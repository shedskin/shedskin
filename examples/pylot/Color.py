import math

class Color(object):
  def __init__(self, r, g, b):
#{
    assert type(r) == float or type(r) == int
    assert type(g) == float or type(g) == int
    assert type(b) == float or type(b) == int
#}
    self.r, self.g, self.b = float(r), float(g), float(b)

  def toList(self):
    return [self.r, self.g, self.b]

  def __add__(self, other):
    assert isinstance(other, Color)
    return Color(self.r + other.r,
                 self.g + other.g,
                 self.b + other.b)

  def __mul__(self, other):
    assert isinstance(other, Color)
    return Color(self.r * other.r,
                 self.g * other.g,
                 self.b * other.b)

  def scale(self, val):
#{
      assert type(val) == float or type(val) == int
#}
      return Color(self.r * val,
                   self.g * val,
                   self.b * val)

  def clip(self):
    if self.r < 0.0:
      self.r = 0.0
    if self.r > 1.0:
      self.r = 1.0
    if self.g < 0.0:
      self.g = 0.0
    if self.g > 1.0:
      self.g = 1.0
    if self.b < 0.0:
      self.b = 0.0
    if self.b > 1.0:
      self.b = 1.0
    return self

  def __repr__(self):
    return "#%02X%02X%02X" % tuple([int(c * 255) for c in self.toList()])

  def toImageColor(self):
    return repr(Color(math.sqrt(self.r), math.sqrt(self.g), math.sqrt(self.b)).clip())
#    return repr(Color(self.r, self.g, self.b).scale(10).clip())

def fromList(l):
  assert len(l) == 3
  return Color(l[0], l[1], l[2])

BLACK = Color(0, 0, 0)
RED = Color(1, 0.2, 0.2)
GREEN = Color(0.2, 1, 0.2)
BLUE = Color(0.2, 0.2, 1)
PURPLE = Color(0.9, 0.2, 0.9)
WHITE = Color(1, 1, 1)
OFF_WHITE = Color(0.85, 0.85, 0.85)
NEARLY_WHITE = Color(0.95, 0.95, 0.95)
PALE_BLUE = Color(0.80, 0.80, 0.90)
GRAY = GREY = Color(0.5, 0.5, 0.5)
