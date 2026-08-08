"""Loops that only append to a local str are rewritten to build into a single
buffer (see shedskin/strbuild.py). These check that the rewrite preserves
semantics, and -- just as importantly -- that it stays off in the cases where
it would not."""


def test_basic():
    out = ""
    for i in range(5):
        out += str(i)
    assert out == "01234"


def test_seeded():
    out = "seed:"
    for i in range(3):
        out += "x"
    assert out == "seed:xxx"


def test_alias_not_mutated():
    # the builder is seeded by copy, so a pre-loop alias keeps pointing at the
    # original string
    a = "start"
    b = a
    for i in range(3):
        a += "x"
    assert a == "startxxx"
    assert b == "start"


def test_zero_iterations():
    out = "init"
    for i in range(0):
        out += "never"
    assert out == "init"


def test_break_and_continue():
    out = ""
    for i in range(10):
        if i % 2 == 0:
            continue
        if i > 6:
            break
        out += str(i)
    assert out == "135"


def test_nested_loops():
    out = ""
    for i in range(3):
        for j in range(2):
            out += str(i) + str(j)
    assert out == "000110112021"


def test_two_accumulators():
    a = ""
    b = ""
    for i in range(3):
        a += "a"
        b += "b"
    assert a == "aaa"
    assert b == "bbb"


def test_while_loop():
    out = ""
    i = 0
    while i < 5:
        out += str(i)
        i += 1
    assert out == "01234"


def append_p(out):
    for i in range(3):
        out += "p"
    return out


def test_formal_parameter():
    assert append_p("start:") == "start:ppp"


def test_read_inside_loop():
    # reading the accumulator mid-loop must keep the unoptimized behaviour
    out = ""
    for i in range(4):
        out += "y"
        if len(out) == 2:
            out += "!"
    assert out == "yy!yy"


def test_self_append():
    out = "ab"
    for i in range(3):
        out += out
    assert out == "abababababababab"


def test_while_test_reads_accumulator():
    out = "a"
    while len(out) < 6:
        out += "b"
    assert out == "abbbbb"


def test_reassigned_inside_loop():
    out = ""
    for i in range(4):
        out += "a"
        if i == 1:
            out = "R"
    assert out == "Raa"


def test_read_in_iter():
    out = "xy"
    total = ""
    for c in out:
        total += c
        out += "!"
    assert out == "xy!!"
    assert total == "xy"


def test_exception_escapes_loop():
    # python leaves the accumulator holding everything appended before the
    # exception, so a loop inside a try keeps the unoptimized behaviour
    out = ""
    try:
        for i in range(10):
            out += str(i)
            if i == 4:
                raise ValueError("stop")
    except ValueError:
        pass
    assert out == "01234"


def test_for_else():
    out = ""
    for i in range(3):
        out += "z"
    else:
        out += "E"
    assert out == "zzzE"


def gen(n):
    # a generator's locals survive across yields, so the rewrite stays off
    out = ""
    for i in range(n):
        out += str(i)
        yield out


def test_generator():
    assert list(gen(3)) == ["0", "01", "012"]


class Acc:
    def __init__(self):
        self.s = ""

    def run(self, n):
        # 'out' is a local and is rewritten; 'self.s' is an attribute and is not
        out = ""
        for i in range(n):
            out += str(i)
            self.s += str(i)
        return out


def test_attribute_accumulator():
    a = Acc()
    assert a.run(3) == "012"
    assert a.s == "012"


class ClassBody:
    # a loop in a class body is not inside a function at all, so there is no
    # local accumulator to look for; the analysis must not be handed the class
    table = []
    for i in range(1, 8):
        table.append(i * 2)


def test_class_body_loop():
    assert ClassBody.table == [2, 4, 6, 8, 10, 12, 14]


def test_computed_values():
    out = ""
    for w in ["ab", "cd"]:
        out += w.upper() + "-"
    assert out == "AB-CD-"


def test_conditional_append():
    out = ""
    for i in range(6):
        if i % 2:
            out += str(i)
    assert out == "135"


def test_deeply_nested_append():
    out = ""
    for i in range(4):
        if i > 0:
            j = 0
            while j < i:
                out += "*"
                j += 1
    assert out == "******"


def test_all():
    test_basic()
    test_seeded()
    test_alias_not_mutated()
    test_zero_iterations()
    test_break_and_continue()
    test_nested_loops()
    test_two_accumulators()
    test_while_loop()
    test_formal_parameter()
    test_read_inside_loop()
    test_self_append()
    test_while_test_reads_accumulator()
    test_reassigned_inside_loop()
    test_read_in_iter()
    test_exception_escapes_loop()
    test_for_else()
    test_generator()
    test_attribute_accumulator()
    test_class_body_loop()
    test_computed_values()
    test_conditional_append()
    test_deeply_nested_append()


if __name__ == "__main__":
    test_all()
