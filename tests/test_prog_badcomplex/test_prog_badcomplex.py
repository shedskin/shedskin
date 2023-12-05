import re

def parsevalue(s):
    if not s:
        return 0 + 0j
    mult = 1 + 0j
    if s[-1] == "j":
        s = s[:-1]
        mult = 0 + 1j
    if s in ["+", "-"]:
        s += "1"
    return float(s) * mult


def str_to_complex(s):
    pat = r"(?P<%s>[+-]?([\d\.]+e[+-]?\d+|[\d\.]*)j?)"
    imag = re.compile(pat % "one" + pat % "two" + "?$")
    m = imag.match(s.strip())
    if m:
        return parsevalue(m.group("one")) + parsevalue(m.group("two"))
    else:
        raise ValueError("complex() arg is a malformed string")

def bad_complex(s):
    try:
        complex(s)
        return False
    except ValueError:
        # print(repr(s) + ": " + str(e))
        return True


def test_program():
    assert str_to_complex(" 2.4+0j") == complex(2.4, 0)
    assert str_to_complex("2.4") == complex(2.4, 0)
    assert str_to_complex(" .4j") == complex(0, 0.4)
    assert str_to_complex("1-j") == complex(1, -1)
    assert str_to_complex("-10-j") == complex(-10, -1)
    assert str_to_complex("+10.1+2.4j") == complex(10.1, 2.4)
    assert str_to_complex("+j") == complex(0, 1)
    assert str_to_complex("2e02") == complex(200,0)
    assert str_to_complex("2e-02-2e+01j") == complex(0.02, -20)
    assert str_to_complex("-1.3e-3.1j") == complex(-0.0013, 0.1)
    assert not bad_complex("2+2j")
    assert not bad_complex("+10.1+2.4j")
    assert bad_complex("")
    assert bad_complex("i")
    assert bad_complex("0j0")
    assert bad_complex("j+1")
    assert bad_complex("1+jj")
    assert bad_complex("3+123")


def test_all():
    test_program()
    

if __name__ == '__main__':
    test_all() 
