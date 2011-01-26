
class Point:
    def __init__(self):
        self.x = 4.4
        self.y = 7
        self.s = 'wah'
        self.n = None

points = [Point() for x in range(10)]

def test_float(x):
    return x

def test_int(x):
    return x

def test_str(s):
    return s

def test_none(n):
    return n

def test_list(l):
    return l

def test_list2(l):
    return l

def test_list_nested(l):
    return l

def test_dict(d):
    return d

def test_set(d):
    return d

def test_tuple(d):
    return d

def test_tuple2(d):
    return d

if __name__ == '__main__':
    p = Point()
    test_float(4.4)
    test_int(4)
    test_str('hoi')
    test_none(None)
    test_list([1,2])
    test_list2([1.0,2.0])
    test_list_nested([[1,2]])
    test_dict({'hoi': 8.8})
    test_set(set([1,2,3]))
    test_tuple((1,2,3))
    test_tuple2(('hoi', 8.9))
