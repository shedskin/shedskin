

def test_sum():
    xs = range(10)
    ys = range(10, 20)
    assert sum(x+y for x,y in zip(xs,ys)) == 190

def test_list():
    assert list(i for i in range(2)) == [0,1]

def test_all():
    test_sum()
    test_list()


if __name__ == "__main__":
    test_all()
