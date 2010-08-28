from Vector4 import Vector4

class Matrix4(object):

  def __init__(self, rows):
    assert isinstance(rows[0], Vector4)
    self.rows = [
      rows[0],
      rows[1],
      rows[2],
      rows[3]]

def hoppa(v):
    return v

if __name__ == '__main__':
  row = Vector4(1, 2, 3, 1)
  hoppa(row)
  m = Matrix4([row, row, row, row])
  print m
