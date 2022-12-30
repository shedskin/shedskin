import re


def test_re_search():

    assert re.search('x*', 'axx').span(0) == (0, 0)
    assert re.search('x*', 'axx').span() == (0, 0)
    assert re.search('x+', 'axx').span(0) == (1, 3)
    assert re.search('x+', 'axx').span() == (1, 3)
    assert re.search('x', 'aaa') == None

def test_re_match():
    assert re.match('a*', 'xxx').span(0) == (0, 0)
    assert re.match('a*', 'xxx').span() == (0, 0)
    assert re.match('x*', 'xxxa').span(0) == (0, 3)
    assert re.match('x*', 'xxxa').span() == (0, 3)
    assert re.match('a+', 'xxx') == None
    assert re.match('(ab|ba)', 'ab').span() == (0, 2)
    assert re.match('(ab|ba)', 'ba').span() == (0, 2)

def test_re_sub():
    assert re.sub('y', 'a', 'xyz') == 'xaz'
    assert re.sub("(?i)b+", "x", "bbbb BBBB") == 'x x'
    assert re.sub('.', r"\n", 'x') == '\n'

    assert re.subn("(?i)b+", "x", "bbbb BBBB") == ('x x', 2)
    assert re.subn("b+", "x", "bbbb BBBB") == ('x BBBB', 1)
    assert re.subn("b+", "x", "xyz") == ('xyz', 0)
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

def test_re_example():
    a = re.compile(
        r"\b(?P<email_name>[\w.-]+?)@(?P<email_domain>[a-z.-]{3,})\b", re.IGNORECASE
    )
    b = "bob (BoB@gmaiL.com) said to sally (sally123_43.d@hOtmail.co.uk) that no-name (not_a-real@em_ail.dres) was annoying..."
    assert a.search(b, 20).group(0) == 'sally123_43.d@hOtmail.co.uk'

def test_all():
    test_re_search()
    test_re_match()
    test_re_sub()
    test_re_split()
    test_re_compile()
    test_re_example()

if __name__ == "__main__":
    test_all()
