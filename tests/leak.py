
class Point:
    def __init__(self):
        self.x = 4.4
        self.y = 7

def test_float(x):
    return x

def test_int(x):
    return x

def test_str(s):
    return s

if __name__ == '__main__':
    p = Point()
    test_float(4.4)
    test_int(4)
    test_str('hoi')
