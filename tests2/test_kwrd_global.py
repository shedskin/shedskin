x = 10

def get_global_x():
    # global x
    return x


def set_global_x():
    global x
    x = 4


def test_global():
    set_global_x()
    x = get_global_x()
    assert x == 4


def test_all():
    test_global()


if __name__ == "__main__":
    test_all()
