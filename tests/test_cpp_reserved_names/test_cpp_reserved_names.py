"""Regression test: Python identifiers that are C++ keywords/reserved words.

shedskin renames identifiers that collide with entries in
resources/illegal/illegal.txt (see cpp.py / typestr.py), so any name in
that file should be usable as a Python variable/parameter/function name
without producing invalid C++.

This covers reserved words that were previously missing from illegal.txt
and caused a C++ compile failure (variable named the same as a C++
keyword, e.g. `nullptr`, `decltype`, `thread_local`, ...).
"""


def use_nullptr(nullptr):
    nullptr += 1
    return nullptr


def use_decltype():
    decltype = 7
    thread_local = 3
    return decltype + thread_local


def use_more_reserved():
    concept = 1
    requires = 2
    noexcept = 3
    static_assert = 4
    bitand = 5
    bitor = 6
    xor = 7
    compl = 8
    return concept + requires + noexcept + static_assert + bitand + bitor + xor + compl


def use_windows_macros():
    # lowercase macros from the Windows SDK headers (e.g. rpcndr.h has
    # '#define small char'), which broke the MSVC build
    small = 1
    hyper = 2
    near = 3
    far = 4
    pascal = 5
    cdecl = 6
    interface = 7
    return small + hyper + near + far + pascal + cdecl + interface


def double(v):
    return v * 2


def union(v):
    return v + 1


def apply(f, x):
    return f(x)


# classes whose names are renamed (1029-A1): class variables, __name__
# and static methods are accessed via the renamed C++ class
class template:
    n = 3

    def __init__(self):
        self.x = 1

    @staticmethod
    def s():
        return 7


class new:
    k = 'k'


class B0:  # termios constant
    pass


def test_nullptr_as_identifier():
    assert use_nullptr(5) == 6


def test_decltype_and_thread_local_as_identifiers():
    assert use_decltype() == 10


def test_other_reserved_identifiers():
    assert use_more_reserved() == 36


def test_windows_macros_as_identifiers():
    assert use_windows_macros() == 28


def test_reserved_function_names_as_values():
    f = double
    assert f(21) == 42
    assert apply(double, 4) == 8
    assert apply(union, 4) == 5


def test_reserved_class_names():
    assert template().x == 1
    assert template.n == 3
    assert template.s() == 7
    template.n = 4
    assert template.n == 4
    assert template.__name__ == 'template'
    assert new.k == 'k'
    assert new.__name__ == 'new'
    assert B0.__name__ == 'B0'
    assert B0().__class__.__name__ == 'B0'


def test_all():
    test_nullptr_as_identifier()
    test_decltype_and_thread_local_as_identifiers()
    test_other_reserved_identifiers()
    test_windows_macros_as_identifiers()
    test_reserved_function_names_as_values()
    test_reserved_class_names()


if __name__ == '__main__':
    test_all()
