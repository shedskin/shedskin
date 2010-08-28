class Vector4(object):

  def __init__(self, x, y, z, w):
    self.x = float(x)
    self.y = float(y)
    self.z = float(z)
    self.w = float(w)

if __name__ == '__main__':
  a = Vector4(1, 2, 3, 1)
  print a
