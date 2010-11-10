from Ray import Ray
from Shape import *
# Annoying: I need these just for shedskin
import Color
from Vector4 import Vector4, Point, Offset
from Utils import Roughly

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
    result = None
#{
    assert isinstance(ray, Ray)
#}
    assert Roughly(ray.offset.length(), 1)
    result = None
    for shape in self.shapes:
      if shape <> ignore:
        insideThisShape = shape == inside
        bidirectional = not inside and (insideMaterial == shape.material)
        hit = shape.hitTest(ray,
                            bidirectional=bidirectional,
                            best=result,
                            inside=insideThisShape)
        if hit:
          result = hit
    return result

  def lightSources(self):
    return [s for s in self.shapes if s.material.isLightSource()]
