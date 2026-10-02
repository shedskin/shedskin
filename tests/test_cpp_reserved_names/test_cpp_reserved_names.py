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


def double(v):
    return v * 2


def union(v):
    return v + 1


def apply(f, x):
    return f(x)


def test_nullptr_as_identifier():
    assert use_nullptr(5) == 6


def test_decltype_and_thread_local_as_identifiers():
    assert use_decltype() == 10


def test_other_reserved_identifiers():
    assert use_more_reserved() == 36


def test_reserved_function_names_as_values():
    f = double
    assert f(21) == 42
    assert apply(double, 4) == 8
    assert apply(union, 4) == 5


def test_all():
    test_nullptr_as_identifier()
    test_decltype_and_thread_local_as_identifiers()
    test_other_reserved_identifiers()
    test_reserved_function_names_as_values()


if __name__ == '__main__':
    test_all()
