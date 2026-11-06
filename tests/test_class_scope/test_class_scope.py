debug = True


class Debug:
    def debug(self, msg):
        if debug:
            return(msg)


def test_case_1():
    assert Debug().debug("debug") == "debug"


class ClassBody:  # issue 1031
    n = 0
    n += 1
    s = ""
    s += "x"
    total = 0
    for i in range(3):
        total += i
    t = sum(j for j in range(3))
    st = {k * 2 for k in range(3)}
    dc = {k: k * k for k in range(3)}


def test_class_body():
    assert ClassBody.n == 1
    assert ClassBody.s == "x"
    assert ClassBody.total == 3
    assert ClassBody.t == 3
    assert ClassBody.st == {0, 2, 4}
    assert ClassBody.dc == {0: 0, 1: 1, 2: 4}


lst = ["global"]


class ClassAttrComp:  # 1021-C6: comprehension over a class attribute
    lst = [1, 2, 3]
    lc = [y + 1 for y in lst]
    ge = sum(y * 2 for y in lst)
    st = {y % 2 for y in lst}
    dc = {y: y * y for y in lst}
    sl = [y for y in sorted(lst[1:], reverse=True)]
    nested = [y for y in [z * 10 for z in lst]]
    pairs = [(x, y) for x in lst for y in range(x)]


def test_class_attr_comp():
    assert ClassAttrComp.lc == [2, 3, 4]
    assert ClassAttrComp.ge == 12
    assert ClassAttrComp.st == {0, 1}
    assert ClassAttrComp.dc == {1: 1, 2: 4, 3: 9}
    assert ClassAttrComp.sl == [3, 2]
    assert ClassAttrComp.nested == [10, 20, 30]
    assert ClassAttrComp.pairs == [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2)]



    





def test_all():
    test_case_1()
    test_class_body()
    test_class_attr_comp()

if __name__ == '__main__':
    test_all()