
class Point:   
    def __init__(self, x , y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return '<Point(%s, %s)>' % (self.x, self.y)
    
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)
    
    def __mul__(self, other):
        x = self.x * other.x
        y = self.y * other.y
        return Point(x, y)
    
    def __truediv__(self, other):
        x = self.x / other.x
        y = self.y / other.y
        return Point(x, y)
    
    def __floordiv__(self, other):
        x = self.x // other.x
        y = self.y // other.y
        return Point(x, y)
    
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __imul__(self, other):
        self.x *= other.x
        self.y *= other.y
        return self
    
    def __itruediv__(self, other):
        self.x /= other.x
        self.y /= other.y
        return self


def test_point():
    p1 = Point(5, 5)
    p2 = Point(10, 10)

    assert str(p1) == '<Point(5, 5)>'

    p3 = p1 + p2
    assert p3.x == 15 and p3.y == 15

    p4 = p3 * p2
    assert p4.x == 150 and p4.y == 150

    p5 = p4 - p2
    assert p5.x == 140 and p5.y == 140

    p6 = p5 // p2 # floor division
    assert p6.x == 14 and p6.y == 14

    # p7 = p5 / p2 # true division
    # assert int(p7.x) == 14 and int(p7.y) == 14


def test_all():
    test_point()

if __name__ == '__main__':
    test_all() 
