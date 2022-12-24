
def propagate(la):
    return la, la

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

# def inner(x): # not yet supported
#     def _f(y):
#         return y+x
#     return _f

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

def best_move(board):
    max_move = (1, 2)
    max_mobility = 1
    return max_move, max_mobility

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

## does not work!
# 
# def test_return_float_param():
#     assert aap(1.0) == 1.0

# def test_return_str_param():
#     assert aap("hh") == "hh"

def test_return_str():
    assert bwa() == 'hoi'

def test_return_float():
    assert hap(1.0) == 1.0

def test_return_tuple_of_lists():
    assert propagate([1]) == ([1],[1])
    assert propagate([2]) == ([2],[2])

def test_return_tuple():
    board = 1
    move, mob = best_move(board)
    assert move == (1,2)
    assert mob == 1

def row_perm_rec(numbers):
    return numbers[0]

def test_return_indexed_value():
    puzzlerows = [[8]]
    assert row_perm_rec(puzzlerows[0]) == 8


def test_all():
    test_basic()
    test_nested()
    test_local()
    test_return_int()
    test_return_int_param()
    # test_return_float_param()
    # test_return_str_param()
    test_return_str()
    test_return_float()
    test_return_tuple()
    test_return_tuple_of_lists()
    test_return_indexed_value()
    # test_inner()

if __name__ == '__main__':
    test_all() 



