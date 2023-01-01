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
    assert re.sub(r"\d+", "****", txt, 2) == 'Call **** for printing, **** for user code.'
    assert re.sub(r"\d+", hexrepl, txt, 2) == 'Call 0xffd2 for printing, 0xc000 for user code.'

def test_re_subn():
    assert re.subn("(?i)b+", "x", "bbbb BBBB") == ('x x', 2)
    assert re.subn("b+", "x", "bbbb BBBB") == ('x BBBB', 1)
    assert re.subn("b+", "x", "xyz") == ('xyz', 0)

    assert re.subn('a', 'ama', 'amadeus') == ('amamamadeus', 2)
    assert re.compile('a').subn('ama', 'amadeus') == ('amamamadeus', 2)

    # assert re.subn("b*", "x", "xyz") == ('xxxyxzx', 4) ## causes crash!
    # assert re.subn("b*", "x", "xyz", 2) == ('xxxyz', 2) ## case not equal

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

if __name__ == "__main__":
    test_all()
