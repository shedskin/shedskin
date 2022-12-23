

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


def test_all():
    test_while_build_list()


if __name__ == '__main__':
    test_all() 
