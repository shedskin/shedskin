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



    





def test_all():
    test_case_1()
    test_class_body()

if __name__ == '__main__':
    test_all()