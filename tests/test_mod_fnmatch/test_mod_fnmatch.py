import fnmatch

fs = ['a.txt', 'b.txt', 'c.txt', 'd.mod']


def test_fnmatch():
    assert fnmatch.fnmatch("run.py", "run.[py]y")

    assert sorted([f for f in fs if fnmatch.fnmatch(f, '*.txt')]) == ['a.txt', 'b.txt', 'c.txt']
    assert sorted([f for f in fs if fnmatch.fnmatch(f, '*.mod')]) == ['d.mod']


def test_fnmatchcase():
    assert fnmatch.fnmatchcase("run.py", "run.[py]y")
    assert not fnmatch.fnmatchcase("RUN.py", "run.[py]y")


def test_fnmatch_newline():
    # a bare trailing $ (instead of a strict end-of-string anchor) would
    # wrongly let a trailing newline sneak through a match
    assert not fnmatch.fnmatch("foo.txt\n", "foo.txt")
    assert not fnmatch.fnmatchcase("foo.txt\n", "foo.txt")
    # '?' and '*' should match a literal newline character, same as real
    # fnmatch (this requires DOTALL semantics in the translated regex)
    assert fnmatch.fnmatch("fo\no", "fo?o")
    assert fnmatch.fnmatch("fo\no", "fo*o")


def test_fnmatch_bad_range():
    # a lexicographically out-of-order range inside a character class
    # (e.g. "[a-!]", since ord('!') < ord('a')) is invalid as a regex
    # range. Real Python's fnmatch neutralizes this into a pattern that
    # simply never matches; it must not raise, crash, or otherwise take
    # down the whole program just because a caller passed a funny-looking
    # glob pattern.
    assert not fnmatch.fnmatch("x", "[a-!]")
    assert not fnmatch.fnmatchcase("x", "[a-!]")
    assert not fnmatch.fnmatch("x", "[[-*]")
    # negated out-of-order range: matches anything
    assert fnmatch.fnmatch("x", "[!a-!]")
    assert fnmatch.fnmatch("!", "[!a-!]")
    # a valid, ordinary range should still work as before
    assert fnmatch.fnmatch("b", "[a-c]")
    assert not fnmatch.fnmatch("d", "[a-c]")


def test_fnmatch_posix_bracket():
    # a '[' inside a character class is just a literal in shell patterns
    # (and in Python's re), but PCRE2 treats "[:", "[." and "[=" inside a
    # class as POSIX bracket syntax ([:alpha:], [.a.], [=a=]).
    assert fnmatch.fnmatchcase("x", "[x[:alpha:]")
    assert fnmatch.fnmatchcase(":", "[x[:alpha:]")
    assert fnmatch.fnmatchcase("x", "[x[.a.]")
    assert fnmatch.fnmatchcase("x", "[x[=a=]")
    assert fnmatch.fnmatchcase("x", "[a-z[:b:]")
    assert fnmatch.fnmatchcase("[", "[x[:alpha:]")
    assert not fnmatch.fnmatchcase("b", "[x[:alpha:]")
    # silent wrong match: class must end at the first ']'
    assert not fnmatch.fnmatchcase("5", "[a[:digit:]x[y]")
    assert fnmatch.fnmatchcase("axy", "[a[:digit:]x[y]")
    assert fnmatch.fnmatchcase(":xy", "[a[:digit:]x[y]")
    # negated forms, and via fnmatch()/filter()
    assert not fnmatch.fnmatchcase("x", "[!x[:alpha:]")
    assert fnmatch.fnmatchcase("b", "[!x[:alpha:]")
    assert fnmatch.fnmatch("x", "[x[:alpha:]")
    assert fnmatch.filter(["x", ":", "b", "["], "[x[:alpha:]") == ["x", ":", "["]
    assert fnmatch.filterfalse(["x", ":", "b", "["], "[x[:alpha:]") == ["b"]


def test_filter():
    fnmatch.filter(fs, '*.txt') == ['a.txt', 'b.txt', 'c.txt']


def test_filterfalse():
    fnmatch.filterfalse(fs, '*.txt') == ['d.mod']


def test_translate():
    fnmatch.translate("run.[py]y")  # TODO difference in output?


def test_all():
    test_fnmatch()
    test_fnmatchcase()
    test_fnmatch_newline()
    test_fnmatch_bad_range()
    test_fnmatch_posix_bracket()
    test_filter()
    test_filterfalse()
    test_translate()


if __name__ == "__main__":
    test_all()



