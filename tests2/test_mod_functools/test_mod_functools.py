from functools import reduce

def test_reduce():
    assert reduce(lambda a, b: a + b, [3, 5, 7]) == 15

def test_all():
    test_reduce()

if __name__ == '__main__':
    test_all() 

