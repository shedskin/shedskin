

def test_format():
    assert "%d" % 255 == '255'
    assert "%s" % "255" == '255'
    assert "%x" % 255 == 'ff'
    assert b"%c" % 6 == b'\x06'

    assert "%g" % (-496.0 / 3.0) == '-165.333'
    assert "%g" % (496.0 / 3.0) == '165.333'
    assert "%g" % (-496.0 / -3.0) == '165.333'
    assert "%g" % (496.0 / -3.0) == '-165.333'


def test_all():
    test_format()


if __name__ == "__main__":
    test_all()
