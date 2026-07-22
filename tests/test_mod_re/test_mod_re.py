import re


def test_re_search():
    assert re.search('x*', 'axx').span(0) == (0, 0)
    assert re.search('x*', 'axx').span() == (0, 0)
    assert re.search('x+', 'axx').span(0) == (1, 3)
    assert re.search('x+', 'axx').span() == (1, 3)
    assert re.search('x', 'aaa') == None

    r = re.compile("^a?$")
    assert r.search("").start() == 0
    assert r.search("").end() == 0
    assert r.search("").span() == (0, 0)
    assert r.search("a").start() == 0
    assert r.search("a").end() == 1
    assert r.search("a").span() == (0, 1)


def test_re_match():
    assert re.match('a*', 'xxx').span(0) == (0, 0)
    assert re.match('a*', 'xxx').span() == (0, 0)
    assert re.match('x*', 'xxxa').span(0) == (0, 3)
    assert re.match('x*', 'xxxa').span() == (0, 3)
    assert re.match('a+', 'xxx') == None
    assert re.match('(ab|ba)', 'ab').span() == (0, 2)
    assert re.match('(ab|ba)', 'ba').span() == (0, 2)

    assert re.match(r"(\d+)\.?(\d+)?", "24").groups() == ('24', None)

    assert re.prefixmatch('x*', 'xxxa').span() == (0, 3)


def test_re_sub():
    assert re.sub('y', 'a', 'xyz') == 'xaz'
    assert re.sub("(?i)b+", "x", "bbbb BBBB") == 'x x'
    assert re.sub('.', r"\n", 'x') == '\n'


def test_re_sub_fn():
    p = re.compile(r"\d+")
    hexrepl = lambda m: hex(int(m.group()))
    txt = "Call 65490 for printing, 49152 for user code."
    assert p.sub("****", txt, 1) == 'Call **** for printing, 49152 for user code.'
    assert p.sub(hexrepl, txt, 1) == 'Call 0xffd2 for printing, 49152 for user code.'
    assert p.sub(hexrepl, txt) == 'Call 0xffd2 for printing, 0xc000 for user code.'
    assert re.sub(r"\d+", "****", txt, count=2) == 'Call **** for printing, **** for user code.'
    assert re.sub(r"\d+", hexrepl, txt, count=2) == 'Call 0xffd2 for printing, 0xc000 for user code.'


def test_re_subn():
    assert re.subn("(?i)b+", "x", "bbbb BBBB") == ('x x', 2)
    assert re.subn("b+", "x", "bbbb BBBB") == ('x BBBB', 1)
    assert re.subn("b+", "x", "xyz") == ('xyz', 0)

    assert re.subn('a', 'ama', 'amadeus') == ('amamamadeus', 2)
    assert re.compile('a').subn('ama', 'amadeus') == ('amamamadeus', 2)

    assert re.subn("b*", "x", "xyz") == ('xxxyxzx', 4) ## causes crash!
    assert re.subn("b*", "x", "xyz", count=2) == ('xxxyz', 2) ## case not equal
    assert re.subn("b*", "x", "xyz", count=2) == ('xxxyz', 2) ## case not equal


def test_re_split():
    assert re.split("(?::+)", ":a:b::c") == ['', 'a', 'b', 'c'] 
    assert re.split("(:)+", ":a:b::c") == ['', ':', 'a', ':', 'b', ':', 'c']


def test_re_compile():
    pat = re.compile('((a)|(b))(c)?')
    assert pat.match('a').groups() == ('a', 'a', None, None)
    assert pat.match('b').groups() ==('b', None, 'b', None)
    assert pat.match('ac').groups() == ('a', 'a', None, 'c')
    assert pat.match('bc').groups() ==('b', None, 'b', 'c')
    assert pat.match('bc').groups("") == ('b', "", 'b', 'c')

    assert pat.groups == 4


def test_re_example1():
    a = re.compile(
        r"\b(?P<email_name>[\w.-]+?)@(?P<email_domain>[a-z.-]{3,})\b", re.IGNORECASE
    )
    b = "bob (BoB@gmaiL.com) said to sally (sally123_43.d@hOtmail.co.uk) that no-name (not_a-real@em_ail.dres) was annoying..."
    assert a.search(b, 20).group(0) == 'sally123_43.d@hOtmail.co.uk'


def test_re_example2():
    imag = re.compile("(a)(b)")
    m = imag.match("ab")
    assert m.group() == "ab"
    assert m.group(0) == "ab"
    assert m.group(1) == "a"
    assert m.group(2) == "b"
    assert m.group(0, 2) == ('ab', 'b')
    assert m.group(2, 1, 1, 2) == ('b', 'a', 'a', 'b')

    # m.__getitem__
    assert m[1] == 'a'
    error = ''
    try:
        m.group(17) # [17]
    except IndexError as e:
        error = str(e)
    assert error == 'no such group'


def test_re_example3():
    imag = re.compile("(?P<one>a)(?P<two>b)")
    m = imag.match("ab")
    assert m.group() == 'ab'
    assert m.group("one") == 'a'
    assert m.group("two") == 'b'
    assert m.group("two", "one") == ('b', 'a')

    wap = m.group("one")
    assert wap == 'a'

    hop = m.group("one", "two", "one")
    assert hop == ('a', 'b', 'a')


def test_match_pos_endpos():
    m = re.match(r'abc', 'abcde')
    assert (m.pos, m.endpos) == (0, 5)
    m = re.search(r'abc', 'ioabcde')
    assert (m.pos, m.endpos) == (0, 7)

    m = re.fullmatch(r'abc', 'abc')
    assert (m.pos, m.endpos) == (0, 3)
    m = re.fullmatch(r'abc', 'abcd')
    assert m is None

    pat = re.compile(r'abc')

    m = pat.match('abcde')
    assert (m.pos, m.endpos) == (0, 5)
    m = pat.match('iabcde', 1)
    assert (m.pos, m.endpos) == (1, 6)
    m = pat.match('abcde', 0, 4)
    assert (m.pos, m.endpos) == (0, 4)

    m = pat.prefixmatch('abcde')
    assert (m.pos, m.endpos) == (0, 5)

    m = pat.search('iiabcde')
    assert (m.pos, m.endpos) == (0, 7)
    m = pat.search('iiabcde', 1, 5)
    assert (m.pos, m.endpos) == (1, 5)

    m = pat.fullmatch('abc')
    assert (m.pos, m.endpos) == (0, 3)
    m = pat.fullmatch('iiabcde', 2, 5)
    assert (m.pos, m.endpos) == (2, 5)


def test_flags():
    assert re.NOFLAG == 0
    assert re.IGNORECASE == 2
    assert re.LOCALE == 4
    assert re.MULTILINE == 8
    assert re.DOTALL == 16
    assert re.UNICODE == 32
    assert re.VERBOSE == 64
    assert re.DEBUG == 128
    assert re.ASCII == 256


def test_re_match_anchored():
    # re.match() must anchor at the start of the string; previously the
    # ANCHORED flag was silently dropped in __convert_flags(), making
    # module-level match() behave like search() instead.
    assert re.match('b', 'ab') is None
    assert re.match('a', 'ab') is not None
    assert re.match('a', 'ab').span() == (0, 1)


def test_re_fullmatch_anchored():
    # fullmatch() must reject partial matches, and must not crash when
    # there's no match at all (a NULL match_object* used to be
    # dereferenced unconditionally once anchoring actually worked).
    assert re.fullmatch('b', 'ab') is None
    assert re.fullmatch('ab', 'ab') is not None
    assert re.fullmatch('ab', 'abc') is None
    assert re.fullmatch('nomatch', 'ab') is None


def test_re_locale_rejected():
    error = ''
    try:
        re.compile('a', re.LOCALE)
    except re.error as e:
        error = str(e)
    assert error == 'cannot use LOCALE flag with a str pattern'


def test_re_compile_error_message():
    # a real syntax error positioned well past byte 5, so the old
    # "char " + erroroffset pointer-arithmetic bug would have produced
    # garbage instead of a proper "char <N>:..." message
    error = ''
    try:
        re.compile('aaaaaaaaaa(')
    except re.error as e:
        error = str(e)
    assert error.startswith('char ')
    offset = error[5:].split(':')[0]
    assert offset.isdigit()


def test_re_groups_count():
    assert re.compile('abc').groups == 0
    assert re.compile('(a)(b)(c)').groups == 3
    assert re.compile('(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)').groups == 12


def test_purge():
    re.purge()


def test_re_unmatched_group_returns_none():
    m = re.match(r'(a)(b)?', 'a')
    assert m.group(1) == 'a'
    assert m.group(2) is None


def test_re_unmatched_named_group_returns_none():
    m = re.match(r'(?P<one>a)(?P<two>b)?', 'a')
    assert m.group('one') == 'a'
    assert m.group('two') is None


def test_re_out_of_range_group_raises_indexerror():
    m = re.match(r'(a)(b)', 'ab')
    error = ''
    try:
        m.group(17)
    except IndexError as e:
        error = str(e)
    assert error == 'no such group'


def test_re_out_of_range_named_group_raises_indexerror():
    m = re.match(r'(?P<one>a)', 'a')
    error = ''
    try:
        m.group('nope')
    except IndexError as e:
        error = str(e)
    assert error == 'no such group'


def test_re_unmatched_group_in_groups_tuple():
    m = re.match(r'(a)(b)?', 'a')
    assert m.groups() == ('a', None)
    assert m.groups('X') == ('a', 'X')


def test_re_expand_unmatched_group_is_empty_string():
    m = re.match(r'(a)(b)?', 'a')
    assert m.expand(r'\1-\2') == 'a-'


def test_re_expand_unmatched_named_group_is_empty_string():
    m = re.match(r'(?P<one>a)(?P<two>b)?', 'a')
    assert m.expand(r'\g<one>-\g<two>') == 'a-'


def test_re_sub_unmatched_group_is_empty_string():
    assert re.sub(r'(a)(b)?', r'\1-\2', 'a') == 'a-'
    assert re.sub(r'(a)(b)?', r'\1-\2', 'ab') == 'a-b'


def test_re_sub_out_of_range_group_raises_error():
    error = ''
    try:
        re.sub(r'(a)(b)?', r'\1-\3', 'a')
    except re.error as e:
        error = str(e)
    assert error != ''


def test_all():
    test_re_search()
    test_re_match()
    test_re_sub()
    test_re_sub_fn()
    test_re_subn()
    test_re_split()
    test_re_compile()
    test_re_example1()
    test_re_example2()
    test_re_example3()
    test_match_pos_endpos()
    test_flags()
    test_re_match_anchored()
    test_re_fullmatch_anchored()
    test_re_locale_rejected()
    test_re_compile_error_message()
    test_re_groups_count()
    test_re_unmatched_group_returns_none()
    test_re_unmatched_named_group_returns_none()
    test_re_out_of_range_group_raises_indexerror()
    test_re_out_of_range_named_group_raises_indexerror()
    test_re_unmatched_group_in_groups_tuple()
    test_re_expand_unmatched_group_is_empty_string()
    test_re_expand_unmatched_named_group_is_empty_string()
    test_re_sub_unmatched_group_is_empty_string()
    test_re_sub_out_of_range_group_raises_error()
    test_purge()


if __name__ == "__main__":
    test_all()
