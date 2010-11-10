import string
import copy
from Vector4 import Vector4, Point

class Matrix4(object):

  def __init__(self, rows):
    self.rows = [
      copy.copy(rows[0]),
      copy.copy(rows[1]),
      copy.copy(rows[2]),
      copy.copy(rows[3])]

  def toList(self):
    return [
      self.rows[0],
      self.rows[1],
      self.rows[2],
      self.rows[3]]

  def mulByMatrix(self, other):
#{
    assert type(other) == Matrix4
#}
    cols = other.cols()
    return Matrix4(
        [Vector4(
           self.rows[i].dot(cols[0]),
           self.rows[i].dot(cols[1]),
           self.rows[i].dot(cols[2]),
           self.rows[i].dot(cols[3])
          ) for i in range(4)])

  def mulByVector(self, vector):
#{
    assert type(vector) == Vector4
#}
    return Vector4(self.rows[0].dot(vector),
                   self.rows[1].dot(vector),
                   self.rows[2].dot(vector),
                   self.rows[3].dot(vector))

  # Somewhat expensive; used during mul for now.
  def cols(self):
    c = [
      Vector4(self.rows[0].x, self.rows[1].x, self.rows[2].x, self.rows[3].x),
      Vector4(self.rows[0].y, self.rows[1].y, self.rows[2].y, self.rows[3].y),
      Vector4(self.rows[0].z, self.rows[1].z, self.rows[2].z, self.rows[3].z),
      Vector4(self.rows[0].w, self.rows[1].w, self.rows[2].w, self.rows[3].w)]
    return c

  def __repr__(self):
    return "[" + string.join([str(i) for i in self.toList()], ",\n") + "]"
