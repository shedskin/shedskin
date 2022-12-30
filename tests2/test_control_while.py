

def test_while_build_list():
    n = 8
    count = 0

    f = 1
    s = 1
    nums = []
    while n > 0:
        count += 1
        nums.append((count, f))
        temp = f
        f = s
        s = temp + s
        n -= 1
    assert nums == [(1, 1), (2, 1), (3, 2), (4, 3), (5, 5), (6, 8), (7, 13), (8, 21)]


def test_while_break():
    val = 0
    i = 0
    while True:
        i += 1
        if i == 10:
            val = i
            break
    assert val == 10

def test_while_continue():
    xs = []
    i = 0
    while i < 10:
        i += 1
        if i == 5:
            continue
        xs.append(i)
    assert xs == [1, 2, 3, 4, 6, 7, 8, 9, 10]

def test_while_else():
    i = 0
    xs = []
    while i < 6:
        i += 1
        xs.append(1)
    else:
        xs.append(2)


def test_all():
    test_while_build_list()
    test_while_break()
    test_while_continue()
    test_while_else()


if __name__ == '__main__':
    test_all() 
