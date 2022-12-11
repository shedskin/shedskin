
def gettuple():
    return (5,6)


def test_tuple():
    a = gettuple()
    assert [(1,2),(3,4), a, gettuple()] == [(1,2), (3,4), (5,6), (5,6)]



if __name__ == '__main__':
    test_tuple()