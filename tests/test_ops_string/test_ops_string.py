def test_classic1():
    assert "%d" % 255 == '255'
    assert "%s" % "255" == '255'
    assert "%x" % 255 == 'ff'
    assert b"%c" % 6 == b'\x06'
    assert "%.2f" % 4.1 == '4.10'
    assert "%d %x %d" % (10, 11, 12) == '10 b 12'
    assert "%d %s" % (1, "een") == '1 een'
    assert '%s' % b'bert' == "b'bert'"


def test_classic2():
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


def test_classic3():
    v = "1 %(aap)s, 1 %(aap)s, %% 2 %(bert)s.."
    d = {"aap": "aapje", "bert": "bertjes"}
    assert (v % d) == '1 aapje, 1 aapje, % 2 bertjes..'

    w = "1 %(aap)s, %% 1 %(aap)d, 2 %(bert)c.."
    f = {"aap": 70, "bert": 71}
    assert (w % f) == '1 70, % 1 70, 2 G..'

    t = (70, 70, 70)
    assert ("1 %s %% %d %c.." % t) == '1 70 % 70 F..'

    t2 = ("x", 71)
    assert (" %%%c, en %%%c.. huhu" % t2) == ' %x, en %G.. huhu'

    t3 = (70, 71, 72, 73, 74)
    assert ("%c %d %x %s %r" % t3) == 'F 71 48 73 74'

    assert ("%(aap)s %(bert)s %% %(bert)c" % {"aap": "hallo", "bert": "H"}) == 'hallo H % H'


def test_str_precision():
    assert ('%.8s' % 'abracadabra') == 'abracada'
    assert ('%.8r' % 'abracadabra') == "'abracad"
    assert ('%.8s' % b'abracadabra') == "b'abraca"
    assert ('%.8r' % b'abracadabra') == "b'abraca"


def test_unterminated_mapping_key():
    # "%(name" with no closing ')' used to scan past the end of the
    # format string looking for ')', reading arbitrary memory instead
    # of raising. CPython raises ValueError here.
    d = {"aap": "aapje"}
    try:
        "%(aap" % d
        assert False, 'expected ValueError'
    except ValueError:
        pass

    try:
        "hello %(aap" % d
        assert False, 'expected ValueError'
    except ValueError:
        pass

    # sanity: well-formed mapping keys still work fine
    assert ("%(aap)s" % d) == 'aapje'


def test_none_argument():
    # None used to be emitted as a bare NULL into the variadic formatting
    # helper, where it was deduced as an integer type with no __str/repr
    # overload rather than as a pointer, and the generated c++ did not compile
    assert "%s" % None == 'None'
    assert "%r" % None == 'None'
    assert "[%s] [%s]" % (None, 3) == '[None] [3]'
    assert "%s %s" % (None, None) == 'None None'

    x = None
    assert "%s" % x == 'None'


def test_width_and_justify():
    assert "[%-5d]" % 42 == '[42   ]'
    assert "[%5d]" % 42 == '[   42]'
    assert "[%-05d]" % 42 == '[42   ]'
    assert "[%05d]" % -42 == '[-0042]'
    assert "[%-06d]" % -42 == '[-42   ]'
    assert "[%-5s]" % "ab" == '[ab   ]'
    assert "[%5s]" % "ab" == '[   ab]'
    assert "[%-10.2s]" % "hello" == '[he        ]'
    assert "[%-5x]" % 255 == '[ff   ]'
    assert "[%05x]" % 255 == '[000ff]'
    assert "[%-5o]" % 8 == '[10   ]'
    assert "[%-10.2f]" % 3.14159 == '[3.14      ]'
    assert "[%10.2f]" % 3.14159 == '[      3.14]'
    assert "[%06.2f]" % -3.14159 == '[-03.14]'
    assert "[%+06.2f]" % 3.14159 == '[+03.14]'
    assert "[%8.3d]" % 5 == '[     005]'
    assert "[%-8.3d]" % 5 == '[005     ]'
    assert "[%08.3d]" % 5 == '[00000005]'


def test_float_conversions():
    # %g used to be formatted as %f with precision-1, so it had no
    # significant-digit semantics, never switched to exponent form and kept
    # its trailing zeroes
    assert ("%g" % 0.5) == '0.5'
    assert ("%g" % 100.0) == '100'
    assert ("%g" % 1234.5678) == '1234.57'
    assert ("%g" % 0.000123456) == '0.000123456'
    assert ("%g" % 1e-5) == '1e-05'
    assert ("%g" % 1e20) == '1e+20'
    assert ("%.1g" % 123456789.0) == '1e+08'
    assert ("%.2g" % 123456789.0) == '1.2e+08'
    assert ("%.3g" % 3.14159265358979) == '3.14'
    assert ("%.12g" % 0.450632335008) == '0.450632335008'
    assert ("%.0g" % 123.0) == '1e+02'  # a precision of 0 means 1

    # %e ignored its precision entirely, always formatting as %.6e
    assert ("%e" % 1234.5678) == '1.234568e+03'
    assert ("%.0e" % 1234.5678) == '1e+03'
    assert ("%.3e" % 3.14159265358979) == '3.142e+00'
    assert ("%.10e" % 0.5) == '5.0000000000e-01'

    # the uppercase conversions were not recognized at all, and silently
    # formatted as the empty string
    assert ("%E" % 1234.5678) == '1.234568E+03'
    assert ("%F" % 1234.5678) == '1234.567800'
    assert ("%G" % 1234.5678) == '1234.57'
    assert ("%.2E" % 0.000123456) == '1.23E-04'
    assert ("%.3G" % 1e20) == '1E+20'

    # %f keeps working as before
    assert ("%f" % 1234.5678) == '1234.567800'
    assert ("%.0f" % 2.5) == '2'
    assert ("%.3f" % 3.14159265358979) == '3.142'

    # negative zero was not detected as negative, so it lost its sign to the
    # digits and confused the sign/padding logic
    assert ("%g" % -0.0) == '-0'
    assert ("%f" % -0.0) == '-0.000000'
    assert ("%+g" % -0.0) == '-0'
    assert ("%012.3g" % -0.0) == '-00000000000'


def test_sign_padding():
    # space padding used to be inserted between the sign and the digits,
    # giving '[-   42]' instead of '[   -42]'
    assert ("[%6d]" % -42) == '[   -42]'
    assert ("[%6x]" % -255) == '[   -ff]'
    assert ("[%6o]" % -8) == '[   -10]'
    assert ("[%8.2f]" % -3.14159) == '[   -3.14]'
    assert ("[%12.3g]" % -2.5) == '[        -2.5]'
    assert ("[%14.3e]" % -1234.5678) == '[    -1.235e+03]'
    assert ("[%6d]" % 42) == '[    42]'

    # zero fill still pads between the sign and the digits
    assert ("[%06d]" % -42) == '[-00042]'
    assert ("[%012.3g]" % -2.5) == '[-000000002.5]'
    assert ("[%014.3e]" % -1234.5678) == '[-00001.235e+03]'

    # and '-' still left-justifies with spaces after the digits
    assert ("[%-6d]" % -42) == '[-42   ]'
    assert ("[%-12.3g]" % -2.5) == '[-2.5        ]'


def test_all():
    test_classic1()
    test_classic2()
    test_classic3()
    test_str_precision()
    test_unterminated_mapping_key()
    test_none_argument()
    test_width_and_justify()
    test_float_conversions()
    test_sign_padding()


if __name__ == "__main__":
    test_all()
