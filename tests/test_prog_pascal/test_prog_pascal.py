
def pascal(n):
    """pascal(n): print n first lines of Pascal's
    triangle (shortest version)."""
    r = [[1]]
    for i in range(1, n):
        r += [[1] + [sum(r[-1][j:j+2]) for j in range(i)]]
    return r

# print(pascal(9))

def test_pascal():
    assert pascal(9) == [
        [1],
        [1, 1],
        [1, 2, 1],
        [1, 3, 3, 1],
        [1, 4, 6, 4, 1],
        [1, 5, 10, 10, 5, 1],
        [1, 6, 15, 20, 15, 6, 1],
        [1, 7, 21, 35, 35, 21, 7, 1],
        [1, 8, 28, 56, 70, 56, 28, 8, 1],
    ]


def test_all():
    test_pascal()
    

if __name__ == '__main__':
    test_all() 