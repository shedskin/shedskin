import copy

class Person:
    def __init__(self, name):
        self.name = name


def test_deepcopy_nested():
    a = [1, (2, 3)]
    b = copy.deepcopy(a)
    assert b[1][0] == 2

def test_deepcopy_obj():
    p = Person('loki')
    c = copy.deepcopy(p)
    assert c.name == 'loki'


def test_copy():
    a = 1
    b = copy.copy(a)
    assert b == 1

    x = 'loki'
    y = copy.copy(x)
    assert y == 'loki'

def test_all():
    test_copy()
    # test_deepcopy_nested()
    test_deepcopy_obj()

if __name__ == '__main__':
    test_all()
