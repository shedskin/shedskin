

def reduce(func, seq, initial=0):
    res = func(initial, seq[0])
    for i in range(len(seq)-1):
        res = func(res, seq[i+1])
    return res


def test_reduce():
    add = lambda x,y: x+y
    assert reduce(add, [1,2,3]) == 6
    assert reduce(add, [1,2,3], 5) == 11


def test_all():
    test_reduce()

if __name__ == '__main__':
    test_all() 
