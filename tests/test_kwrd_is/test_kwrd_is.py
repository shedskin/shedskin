class Foo:
    pass

def test_is():
    obj = Foo()
    assert obj is obj
    assert obj is not None

    obj = None
    assert obj is None
    assert obj == None
    assert not obj

    bla = "hoei"
    assert bla == "hoei"
    assert bla is "hoei"
    assert bla != "meuk"
    assert bla is not "meuk"

def test_all():
    test_is()

if __name__ == '__main__':
    test_all() 

