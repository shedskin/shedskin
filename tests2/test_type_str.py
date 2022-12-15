def heuk(x):
    return


def test_str_concat():
    assert "x" + "x" + "x" == "xxx"

def test_str_methods():
    # missing string methods
    assert "ab\ncd\r\nef\rghi\n".splitlines() == ['ab', 'cd', 'ef', 'ghi']
    assert "ab\ncd\r\nef\rghi\n".splitlines(1) == ['ab\n', 'cd\r\n', 'ef\r', 'ghi\n']
    assert "This Is A Title".istitle()
    assert not "This is not a title".istitle()
    assert "a and b and c".partition("and") == ('a ', 'and', ' b and c')
    assert "a and b and c".rpartition("and") == ('a and b ', 'and', ' c')

    ah = "hatsie flatsie pots"
    assert ah == " ".join(ah.split())
    assert "hoei hoei".split() == ['hoei', 'hoei']
    assert "hoei hoei\\n".split() == ['hoei', 'hoei\\n']
    assert "hoei\\n" != "hoei\n"


def test_str_overload():
    # locally overloading builtin definition
    str = "4"
    t = ("aha", 2)
    str, x = t
    assert not heuk("aha")


if __name__ == '__main__':
    test_str_methods()
    test_str_concat()
    test_str_overload()

