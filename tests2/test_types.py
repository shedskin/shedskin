

def test_equality():
    assert int(1) == int(1)
    assert int(1.0) == int(1.0)
    assert float(1) == float(1)
    assert float(1.0) == float(1.0)

def test_edge_case1():
    nrofvars = [1][0]
    assert list(range(nrofvars+1)) == [0,1]

def test_all():
    test_equality()
    test_edge_case1()


if __name__ == "__main__":
    test_all()
