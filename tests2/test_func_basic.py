
def ident(x):
    return x

def boing(c, d):
    return ident(c)

def bla():
    return 8

def bwa():
    d = 'hoi'
    return d

def aap(y):
    return y

def hap(y):
    return y

class xevious:
    def solvalou(self, x):
        return x

def pacman(a):
    return 1

def qbert():
    c = 1
    a = 1
    pacman(a)
    b = 1
    a = c
    d = 1
    e = 1
    x = xevious()
    x.y = d
    x.z = 'hoi'
    x.solvalou(e)

    return b

def test_basic():
    assert boing(1, 1.0) == 1

def test_nested():
    a = 1
    h = boing(boing(a, 1.0), boing(3.0, a))
    assert h == 1

def test_local():
    assert qbert() == 1

def test_return_int():
    assert bla() == 8

def test_return_int_param():
    assert aap(100) == 100

def test_return_str():
    assert bwa() == 'hoi'

def test_return_float():
    assert hap(1.0) == 1.0





if __name__ == '__main__':
    test_basic()
    test_nested()
    test_local()
    test_return_int()
    test_return_int_param()
    test_return_str()
    test_return_float()


