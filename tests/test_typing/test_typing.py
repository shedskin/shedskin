
def greeting(name: str) -> str:
    return 'Hello ' + name


def test_assign():
    a: str = 'hoera'
    assert a == 'hoera'

def test_func():
    assert greeting('world') == 'Hello world'

def test_all():
    test_assign()
    test_func()


if __name__ == "__main__":
    test_all()
