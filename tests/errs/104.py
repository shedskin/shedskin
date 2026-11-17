# assigning a value without a type (it becomes 'void *' in C++) to a target
# that has a type: we want a warning, rather than only a C++ compile error

def test_for_lit():
    x = 1
    for x in []:
        pass
    s = 'a'
    for s in []:
        pass


def test_for_lit_unpack():
    a, b = 1, 'x'
    for a, b in []:
        pass


def test_for_var_unpack():
    e = []
    a, b = 1, 'x'
    for a, b in e:
        pass


def test_assign_subscript():
    x = 1
    if len([1]) == 0:
        x = [][0]


def test_assign_unpack():
    a, b = 1, 2
    if len([1]) == 0:
        a, b = [][0]


test_for_lit()
test_for_lit_unpack()
test_for_var_unpack()
test_assign_subscript()
test_assign_unpack()

#*WARNING* 104.py:6: expression has no type
#*WARNING* 104.py:9: expression has no type
#*WARNING* 104.py:15: expression has no type
#*WARNING* 104.py:22: expression has no type
#*WARNING* 104.py:29: expression has no type
#*WARNING* 104.py:35: expression has no type
