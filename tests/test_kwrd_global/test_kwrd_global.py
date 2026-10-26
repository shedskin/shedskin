global y  # module-level 'global' is a no-op

x = 10
y = 1
z = 'a'


class C:
    global y, z
    y += 4
    z = z + 'b'
    w = y * 2

    def m(self):
        return y

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


def test_global_class_body():
    assert C().m() == 5
    assert y == 5
    assert z == 'ab'
    assert C.w == 10


def test_all():
    test_global()
    test_global_class_body()


if __name__ == "__main__":
    test_all()
