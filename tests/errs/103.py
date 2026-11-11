# conversion matrix (tests/test_type_conversion): cases that cannot be
# converted or cast, so a warning is the outcome we want (for now)

def test_assign_none_scalar():
    a = 1
    a = None
    assert a is None


def test_assign_int_float_var_list():
    ints = [1, 2]
    a = [1.5]
    a = ints
    assert sum(a) == 3


def assign_ints():
    return [1, 2]

def test_assign_int_float_call_list():
    a = [1.5]
    a = assign_ints()
    assert sum(a) == 3


def test_assign_none_scalar_list():
    a = [1]
    a = [None]
    assert a[0] is None


def test_assign_empty_var_number():
    e = []
    g = [1]
    g = e
    assert len(g) == 0


def assign_empty_shared():
    return []

def test_assign_empty_call_shared():
    # one function that returns an empty list, for two element types
    a = [1]
    a = assign_empty_shared()
    b = ['x']
    b = assign_empty_shared()
    assert len(a) == 0 and len(b) == 0


class AttrIntFloatVar:
    def __init__(self):
        self.l = [1.5]

def test_attr_int_float_var():
    ints = [1, 2]
    h = AttrIntFloatVar()
    h.l = ints
    assert sum(h.l) == 3


class AttrEmptyVarNumber:
    def __init__(self):
        self.l = [1]

def test_attr_empty_var_number():
    e = []
    h = AttrEmptyVarNumber()
    h.l = e
    assert len(h.l) == 0


def test_setitem_none_scalar():
    l = [1, 2]
    l[0] = None
    assert l[0] is None and l[1] == 2


def test_setitem_int_float_var_list():
    ints = [3]
    d = {1: [1.0]}
    d[2] = ints
    assert sum(d[2]) == 3


def test_setitem_empty_var_number():
    e = []
    d = {1: [1]}
    d[2] = e
    assert len(d[2]) == 0


def arg_or_default(i=None):
    if i is None:
        return -1
    return i

def test_arg_none_scalar():
    assert arg_or_default() == -1
    assert arg_or_default(0) == 0
    assert arg_or_default(3) == 3


def arg_total_var(l):
    return sum(l)

def test_arg_int_float_var_list():
    ints = [1, 2]
    assert arg_total_var([0.5]) == 0.5
    assert arg_total_var(ints) == 3


def arg_empty_total_var(l):
    return sum(l)

def test_arg_empty_var_number():
    e = []
    assert arg_empty_total_var([1]) == 1
    assert arg_empty_total_var(e) == 0


def ret_none_scalar(c):
    if c:
        return 0
    return None

def test_ret_none_scalar():
    assert ret_none_scalar(True) == 0
    assert ret_none_scalar(False) is None


def ret_var(c):
    ints = [1, 2]
    if c:
        return [1.5]
    return ints

def test_ret_int_float_var_list():
    assert sum(ret_var(False)) == 3


def ret_empty_var_number(c):
    e = []
    if c:
        return [1]
    return e

def test_ret_empty_var_number():
    assert len(ret_empty_var_number(False)) == 0


def test_method_none_scalar():
    l = [0]
    l.append(None)
    assert l[1] is None and l[0] == 0
    d = {1: 0}
    assert d.get(2) is None


def test_method_int_float_var_list():
    ints = [1]
    ll = [[1.5]]
    ll.append(ints)
    assert sum(ll[1]) == 1


def test_method_empty_var_elem_number():
    e = []
    ll = [[1]]
    ll.append(e)
    assert len(ll[1]) == 0


def test_display_none_scalar():
    l = [0, None]
    assert l[1] is None and l[0] is not None


def test_display_int_float_var_list():
    ints = [1]
    floats = [1.5]
    ll = [floats, ints]
    assert sum(ll[1]) == 1


def test_display_empty_var_number():
    e = []
    ll = [[1], e]
    assert len(ll[1]) == 0


def test_lookup_float_int():
    x = 2.5
    l = [1, 2, 3]
    assert x not in l
    assert l.count(x) == 0
    t = (1, 2, 3)
    assert x not in t
    d = {1: 'a', 2: 'b'}
    assert x not in d
    assert d.get(x) is None


def test_lookup_none_scalar():
    l = [0, 1]
    assert None not in l
    assert l.count(None) == 0


def test_choice_none_scalar():
    c = 3
    i = 0 if c > 2 else None
    assert i is not None
    j = 0 if c > 5 else None
    assert j is None


def test_choice_int_float_var_list():
    c = 3
    ints = [1]
    floats = [2.5]
    l = ints if c > 2 else floats
    assert sum(l) == 1


def test_choice_empty_var_number():
    c = 3
    e = []
    ints = [1]
    l = e if c > 2 else ints
    assert len(l) == 0

test_assign_none_scalar()
test_assign_int_float_var_list()
test_assign_int_float_call_list()
test_assign_none_scalar_list()
test_assign_empty_var_number()
test_assign_empty_call_shared()
test_attr_int_float_var()
test_attr_empty_var_number()
test_setitem_none_scalar()
test_setitem_int_float_var_list()
test_setitem_empty_var_number()
test_arg_none_scalar()
test_arg_int_float_var_list()
test_arg_empty_var_number()
test_ret_none_scalar()
test_ret_int_float_var_list()
test_ret_empty_var_number()
test_method_none_scalar()
test_method_int_float_var_list()
test_method_empty_var_elem_number()
test_display_none_scalar()
test_display_int_float_var_list()
test_display_empty_var_number()
test_lookup_float_int()
test_lookup_none_scalar()
test_choice_none_scalar()
test_choice_int_float_var_list()
test_choice_empty_var_number()

#*WARNING* 103.py:7: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:13: incompatible types
#*WARNING* 103.py:22: incompatible types
#*WARNING* 103.py:29: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:35: incompatible types
#*WARNING* 103.py:45: incompatible types
#*WARNING* 103.py:58: incompatible types
#*WARNING* 103.py:69: incompatible types
#*WARNING* 103.py:74: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:75: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:76: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:82: incompatible types
#*WARNING* 103.py:89: incompatible types
#*WARNING* 103.py:93: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:94: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:96: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:99: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:110: incompatible types
#*WARNING* 103.py:119: incompatible types
#*WARNING* 103.py:122: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:128: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:129: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:136: incompatible types
#*WARNING* 103.py:146: incompatible types
#*WARNING* 103.py:153: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:154: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:155: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:157: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:163: incompatible types
#*WARNING* 103.py:170: incompatible types
#*WARNING* 103.py:175: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:176: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:182: incompatible types
#*WARNING* 103.py:188: incompatible types
#*WARNING* 103.py:195: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 103.py:196: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 103.py:198: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 103.py:200: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 103.py:201: looking up a float among ints: it is truncated, so 2.5 finds 2
#*WARNING* 103.py:206: looking up None among numbers: it is treated as 0
#*WARNING* 103.py:207: looking up None among numbers: it is treated as 0
#*WARNING* 103.py:212: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:213: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:214: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:215: expression has dynamic (sub)type: {None, int}
#*WARNING* 103.py:222: incompatible types
#*WARNING* 103.py:230: incompatible types
#*WARNING* 103.py: Variable (Function arg_or_default, 'i') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_assign_none_scalar, 'a') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_assign_none_scalar_list, 'a') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_choice_none_scalar, 'i') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_choice_none_scalar, 'j') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_display_none_scalar, 'l') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_method_none_scalar, 'l') has dynamic (sub)type: {None, int}
#*WARNING* 103.py: Variable (Function test_setitem_none_scalar, 'l') has dynamic (sub)type: {None, int}
