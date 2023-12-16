

xs = range(10)

seq = [(1,2), (3,4)]

cube = [(1,2),(3,4),(5,6)]

def hoei(cube):
    x = None
    for pos in cube:
        x = pos
    return x


def test_for_range():
    result = []
    for i in xs:
        result.append(i)
    assert result == [0,1,2,3,4,5,6,7,8,9]

def test_for_chain():
    assert [x + y for x in range(2) for y in range(3)] == [0, 1, 2, 1, 2, 3]
    assert list(x + y for x in range(3) for y in range(4)) == [0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5] 
    assert [x+y+z  for x in range(2) for y in range(2) for z in range(2)] == [0, 1, 1, 2, 1, 2, 2, 3]

def test_for_tuple():
    result = []
    for i in seq:
        result.append(i)
    assert result == seq

def test_for_fn():
    assert hoei(cube) == (5,6)

def test_for_enumerate():
    result_i = []
    result_o = []
    for i, o in enumerate(cube):
        result_i.append(i)
        result_o.append(o)
    assert result_i == [0,1,2]
    assert result_o == cube

def test_for_break():
    xs = range(10)
    x = 0
    for i in xs:
        if i > 5:
            x = i
            break
    assert x == 6

def test_for_continue():
    xs = []
    for i in range(10):
        if i == 5:
            continue
        xs.append(i)
    assert xs == [0, 1, 2, 3, 4, 6, 7, 8, 9]


def test_for_else():
    xs = []
    for i in range(6):
        xs.append(1)
    else:
        xs.append(2)
    assert xs == [1, 1, 1, 1, 1, 1, 2]



def test_all():
    test_for_range()
    test_for_chain()
    test_for_tuple()
    test_for_fn()
    test_for_enumerate()
    test_for_break()
    test_for_continue()
    test_for_else()

if __name__ == '__main__':
    test_all() 


