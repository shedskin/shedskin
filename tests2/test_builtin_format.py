

def test_format1():
    assert "%d" % 255 == '255'
    assert "%s" % "255" == '255'
    assert "%x" % 255 == 'ff'
    assert b"%c" % 6 == b'\x06'

    assert "%g" % (-496.0 / 3.0) == '-165.333'
    assert "%g" % (496.0 / 3.0) == '165.333'
    assert "%g" % (-496.0 / -3.0) == '165.333'
    assert "%g" % (496.0 / -3.0) == '-165.333'

    assert "%.2f" % 4.1 == '4.10'
    assert "%d %x %d" % (10, 11, 12) == '10 b 12'
    assert "%d %s" % (1, "een") == '1 een'


def test_format2():
    assert "%04x" % 0xFEDA == 'feda'
    assert "%d %s %.2f" % (1, "een", 8.1) == '1 een 8.10'
    assert "%x %d %x" % (10, 11, 12) == 'a 11 c'
    assert "%s %04x" % ("twee", 2) == 'twee 0002'
    assert "%02x" % 0x1234 == '1234'

    assert "%o" % 10 == '12'
    assert "%.4s %.4r\n" % ("abcdefg", "\0hoplakee") == "abcd '\\x0\n"

    assert "?%% %c?" % 70 == '?% F?'
    assert "?%c?%%" % 0 == '?\x00?%'
    assert "!%s!" % [1, 2, 3] == '![1, 2, 3]!'
    assert "%.2f %d %.2f %d" % (4, 4.4, 5.5, 5) == '4.00 4 5.50 5'
    assert "%s." % 1 == '1.'
    assert "%s." % (1,) == '1.'
    assert "aha %s %r" % (18, 19) == 'aha 18 19'
    assert "%i%%-%i%%" % (1, 2) == '1%-2%'
    assert "%i%%-%s%%" % (12, "21") == '12%-21%'


def test_all():
    test_format1()
    test_format2()


if __name__ == "__main__":
    test_all()
