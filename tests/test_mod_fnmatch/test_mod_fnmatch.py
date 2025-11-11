import os
import os.path
import fnmatch

fs = ['a.txt', 'b.txt', 'c.txt', 'd.mod']


def test_fnmatch():
    assert fnmatch.fnmatch("run.py", "run.[py]y")

    assert sorted([f for f in fs if fnmatch.fnmatch(f, '*.txt')]) == ['a.txt', 'b.txt', 'c.txt']
    assert sorted([f for f in fs if fnmatch.fnmatch(f, '*.mod')]) == ['d.mod']


def test_fnmatchcase():
    assert fnmatch.fnmatchcase("run.py", "run.[py]y")
    assert not fnmatch.fnmatchcase("RUN.py", "run.[py]y")


def test_filter():
    fnmatch.filter(fs, '*.txt') == ['a.txt', 'b.txt', 'c.txt']


def test_filterfalse():
    fnmatch.filterfalse(fs, '*.txt') == ['d.mod']


def test_translate():
    fnmatch.translate("run.[py]y")  # TODO difference in output?


def test_all():
    test_fnmatch()
    test_fnmatchcase()
    test_filter()
    test_filterfalse()
    test_translate()


if __name__ == "__main__":
    test_all()



