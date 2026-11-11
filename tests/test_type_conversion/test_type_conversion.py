# conversion test matrix (issue #1178)
#
# a value often has another type than the place where it ends up: the
# variable it is assigned to, the argument it is passed as, the elements of
# the container it is added to or looked up in, the other operand, and so on.
# shedskin infers a single C++ type for each such place, so the value has to
# be converted or cast to that type. where that is not possible, we want a
# warning or an error, and never a silently wrong result.
#
# this test set enumerates these situations as a matrix with three axes:
#
#     TYPE PAIR x SOURCE x CONTEXT
#
# each cell of the matrix is a test function, with a comment line above it
# that gives its place in the matrix, and the WAY it should be handled:
#
#     # <type pair>, <source>: <way>
#     def test_<context>_<type pair>_<source>[_<detail>]():
#
# cells that do not work today are commented out, and marked with TODO and
# what goes wrong. cells for which a warning or an error is the outcome we
# want are commented out as well (marked with '->'). the ones that warn are
# repeated in tests/errs/103.py, which checks the warnings.
#
# conventions:
#
# - cells must not influence each other. so each cell has its own variables,
#   helper functions and helper classes, because anything that is shared
#   gets the merged type of all its uses. the only shared names are the
#   classes A, B and B2 (which have no attributes).
# - results are compared by value (sum(..), x + 0.5 == ..) and not with
#   str/repr, because an int that is widened prints as a float (1 -> 1.0).
# - a cell tests the conversion in its own context only. so we avoid, for
#   example, comparing two containers in a cell that is not about comparing.
#
#
# AXIS 1: TYPE PAIR (the type of the value -> the type that is expected)
#
#   bool->int     a bool used as an int: [1, True]
#   int->float    widening a number: [1.5, 2]. the same goes for
#                 int->complex and float->complex
#   float->int    narrowing a number. variables and containers always get
#                 the wider type, so this only happens when looking up a
#                 float in a container of ints: 2.5 in [1, 2]
#   none          None where a str, container or class instance is expected.
#                 these are pointers in C++, and None is a null pointer
#   none->scalar  None where an int or float is expected. these are not
#                 pointers in C++, so there is no way to represent None
#   sub->base     an instance of a subclass where a base class is expected.
#                 this includes two sibling classes that meet in their base
#   empty         a container that is empty where it is created ([], {},
#                 set()), so it has no element type of its own. it gets
#                 one from what is added to it later, or from what it
#                 meets. if neither happens it stays without one
#
#   the two types can differ at several depths:
#
#   - the value itself: a number, None, an instance
#   - the elements of a container: list, set, tuple and deque elements, dict
#     keys and values
#   - nested: the elements of the elements
#
#   at the first depth C++ mostly converts by itself. at the other depths the
#   representation matters: a list<int> is not a list<double>, and no cast
#   can make it one. but a list<B *> can be used as a list<A *>.
#
#
# AXIS 2: SOURCE (where the value comes from)
#
#   literal   a constant or display, written in place: 1, [1, 2], {1: 2}
#   new       another expression that creates a new object: a constructor
#             call (list(..), B()), a comprehension, a slice, sorted(..)
#   ifexp     a conditional expression with a new object on both sides
#   variable  an existing object, reached through a name, attribute or item.
#             it can be aliased, so replacing it with a converted copy would
#             be wrong: changes through one name would not show in the other
#   call      the result of calling a user function. an existing object as
#             well, that has the declared return type of the function
#
#
# AXIS 3: CONTEXT (where the value meets the type that is expected)
#
#   1. assign     rebinding a variable (local or global)
#   2. attr       assigning to an instance attribute
#   3. setitem    assigning to an item or a slice: l[0] = .., d[k] = ..
#   4. arg        passing an argument to a user function, method,
#                 constructor or lambda (also as default or keyword)
#   5. ret        returning or yielding from a user function or lambda
#   6. method     adding to a builtin container through one of its methods:
#                 append, insert, add, setdefault, extend, update, +=, |=
#   7. display    the elements of a display: [x, y], {k: v}, (x, y)
#   8. binop      the operands of a binary operator: +, |, &, -, ^, *
#   9. compare    the two sides of a comparison: ==, !=, <, is
#  10. lookup     looking something up in a builtin container: in, count,
#                 index, remove, d[k], get, pop, del
#  11. ctor       the argument of a builtin container constructor: list(..),
#                 set(..), dict(..), deque(..), Counter(..), sorted(..)
#  12. iter       loop variables and unpacking: for x in .., a, b = ..
#  13. choice     the branches of a conditional expression, 'and' and 'or'
#  14. lib        arguments of builtin and library functions: sum, max, zip,
#                 map, functools.reduce, itertools.chain, heapq.merge
#  15. mixed      collected tests that go through several contexts at once
#
#
# WAY (how a cell should be handled)
#
#   implicit  C++ converts the value by itself: a bool to an int, an int to
#             a float
#   cast      a pointer cast. only possible if both types have the same
#             representation: None, an instance of a subclass, an empty
#             container without element type that meets one of pointers
#             (not of numbers), and containers of those (at any depth)
#   build     a new object is created as the expected type in the first
#             place: [1, 2] as a list of floats. only possible for a source
#             that creates a new object (literal, new, ifexp)
#   copy      the operation copies the elements to another container anyway,
#             so it can convert them on the way: extend, update, list(..),
#             l1 + l2, s1 | s2. also possible for a variable or call result
#   generic   the operation only reads both values, so it could work for
#             different element types without converting: ==, <, in
#   infer     nothing has to be converted: type inference gives an empty
#             container the element type of what is added to it later
#   warn      cannot be bridged: we want a shedskin warning
#   error     cannot be bridged: we want an error (today some of these are
#             a C++ static_assert, so they show up while compiling)
#
#
# OVERVIEW (number of cells that work / TODO / correctly warn or fail)
#
#                bool->int    int->float   float->int   none         none->scalar sub->base    empty
#    1. assign   0/2/0        15/4/2       -            3/0/0        0/0/2        8/0/0        11/4/2
#    2. attr     -            1/0/1        -            1/0/0        -            2/0/0        4/0/1
#    3. setitem  0/1/0        5/4/0        -            1/0/0        0/0/1        2/0/0        4/2/0
#    4. arg      0/1/0        9/2/1        -            1/0/0        0/0/1        2/0/0        7/0/1
#    5. ret      0/1/0        5/0/1        -            1/0/0        0/0/1        2/0/0        8/0/1
#    6. method   0/1/0        12/2/1       -            1/0/0        0/0/1        2/0/0        5/17/1
#    7. display  0/1/0        3/1/1        -            1/0/0        0/0/1        2/0/0        4/0/1
#    8. binop    1/0/0        7/15/0       -            1/0/0        -            2/2/0        11/14/0
#    9. compare  -            4/5/0        -            1/0/0        0/1/0        1/0/0        6/3/0
#   10. lookup   1/0/0        2/8/0        0/0/1        2/1/0        0/0/1        2/0/0        4/10/0
#   11. ctor     -            7/1/0        -            1/0/0        -            1/0/0        2/16/0
#   12. iter     0/1/0        5/1/0        -            1/0/0        -            3/2/0        7/8/0
#   13. choice   -            2/0/1        -            1/0/0        0/0/1        2/0/0        5/0/1
#   14. lib      -            6/3/3        -            3/1/0        -            1/0/0        6/19/0
#   15. mixed    -            -            -            -            -            -            1/0/0
#
#   total        2/8/0        83/46/11     0/0/1        19/2/0       0/1/9        32/4/0       85/93/8
#
#   all cells: 221 work, 154 TODO, 29 correctly warn or fail
#
# TODO not in the matrix yet: class attributes, exceptions, string formatting,
# the array module, bytes/bytearray, user classes with __contains__/__eq__.

from collections import Counter, defaultdict, deque
import functools
import heapq
import itertools
import math


class A:
    def name(self):
        return 'A'


class B(A):
    def name(self):
        return 'B'


class B2(A):
    def name(self):
        return 'B2'


#=========================================================================
# 1. ASSIGN: rebinding a variable
#
# the variable has the type of everything that is assigned to it, so a
# value of a narrower type has to become that type
#=========================================================================


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'a' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: invalid conversion from '__ss_int' to 'pyobj*'
#
# def test_assign_bool_int_lit_scalar():
#     a = 1
#     a = True
#     assert a + 1 == 2


# int->float, literal: implicit
def test_assign_int_float_lit_scalar():
    a = 1.5
    a = 1
    assert a + 0.5 == 1.5


# int->float, variable: implicit
def test_assign_int_float_var_scalar():
    i = 3
    a = 1.5
    a = i
    assert a + 0.5 == 3.5 and i == 3


# int->float, call: implicit
def assign_three():
    return 3

def test_assign_int_float_call_scalar():
    a = 1.5
    a = assign_three()
    assert a + 0.5 == 3.5


# int->complex, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'z' has dynamic (sub)type: {complex, int}
#   variable 'w' has dynamic (sub)type: {complex, float}
#   expression has dynamic (sub)type: {complex, int}
#   expression has dynamic (sub)type: {complex, float}
#   C++: cannot convert 'complex' to 'pyobj*' in assignment
#
# def test_assign_complex_lit_scalar():
#     z = 1j
#     z = 1
#     assert z + 1j == complex(1, 1)
#     w = 1j
#     w = 2.5
#     assert w + 1j == complex(2.5, 1)


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'a' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: invalid conversion from '__ss_int' to 'pyobj*'
#
# def test_assign_none_scalar():
#     a = 1
#     a = None
#     assert a is None


# none, literal: cast
def test_assign_none_lit():
    s = 'a'
    s = None
    assert s is None
    l = [1]
    l = None
    assert l is None
    o = A()
    o = None
    assert o is None


# sub->base, new: cast
def test_assign_sub_new():
    o = A()
    o = B()
    assert o.name() == 'B'


# sub->base, variable: cast
def test_assign_sub_var():
    b = B()
    o = A()
    o = b
    assert o.name() == 'B' and b.name() == 'B'


# sub->base, call: cast
def assign_make_b():
    return B()

def test_assign_sub_call():
    o = A()
    o = assign_make_b()
    assert o.name() == 'B'


# sub->base, new: cast
def test_assign_sub_siblings():
    # siblings meet in their common base class
    o = B()
    o = B2()
    assert o.name() == 'B2'
    l = [B()]
    l = [B2()]
    assert l[0].name() == 'B2'


# bool->int, literal: build
# TODO doesn't work today: warning, then C++ compile error
#   variable 'a' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_assign_bool_int_lit_list():
#     a = [1, 2]
#     a = [True, False]
#     a.append(5)
#     assert sum(a) == 6


# int->float, literal: build
def test_assign_int_float_lit_list():
    a = [1.5]
    a = [1, 2]
    a.append(0.5)
    assert sum(a) == 3.5


# int->float, literal: build
def test_assign_int_float_lit_set():
    s = {1.5}
    s = {1, 2}
    s.add(0.5)
    assert sum(s) == 3.5


# int->float, literal: build
def test_assign_int_float_lit_dict():
    d = {1: 1.5}
    d = {2: 3}
    d[4] = 0.5
    assert sum(d.values()) == 3.5
    e = {1.5: 'a'}
    e = {2: 'b'}
    e[0.5] = 'c'
    assert sum(e) == 2.5


# int->float, literal: build
def test_assign_int_float_lit_tuple():
    t = (1.5, 2.5)
    t = (1, 2)
    t = t + (0.5,)
    assert sum(t) == 3.5
    u = (1.5, 'a')
    u = (1, 'b')
    assert u[0] + 0.5 == 1.5 and u[1] == 'b'


# int->float, literal: build
def test_assign_int_float_lit_nested():
    a = [[1.5]]
    a = [[1, 2]]
    a[0].append(0.5)
    assert sum(a[0]) == 3.5
    d = {1: [1.5]}
    d = {2: [3]}
    d[2].append(0.5)
    assert sum(d[2]) == 3.5
    t = [(1.5, 'a')]
    t = [(1, 'b')]
    assert t[0][0] + 0.5 == 1.5


# int->complex, literal: build
# TODO doesn't work today: warning, then C++ compile error
#   variable 'a' has dynamic (sub)type: {complex, int}
#   variable 'b' has dynamic (sub)type: {complex, float}
#   expression has dynamic (sub)type: {complex, int}
#   expression has dynamic (sub)type: {complex, float}
#   C++: cannot convert 'list<complex>*' to 'list<pyobj*>*' in assignment
#
# def test_assign_complex_lit_list():
#     a = [1j]
#     a = [1, 2]
#     a.append(1j)
#     assert sum(a) == complex(3, 1)
#     b = [1j]
#     b = [1.5]
#     assert b[0] + 1j == complex(1.5, 1)


# int->float, literal: build
conv_global_scalar = 1.5
conv_global_list = [1.5]

def test_assign_int_float_lit_global():
    global conv_global_scalar, conv_global_list
    conv_global_scalar = 1
    assert conv_global_scalar + 0.5 == 1.5
    conv_global_list = [1, 2]
    conv_global_list.append(0.5)
    assert sum(conv_global_list) == 3.5


# int->float, new: build
def test_assign_int_float_new_list():
    a = [1.5]
    a = list((1, 2))
    a.append(0.5)
    assert sum(a) == 3.5


# int->float, new: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in
#     assignment
#
# def test_assign_int_float_new_list_range():
#     b = [1.5]
#     b = list(range(3))
#     b.append(0.5)
#     assert sum(b) == 3.5


# int->float, new: build
def test_assign_int_float_new_set_dict():
    s = {1.5}
    s = set([1, 2])
    s.add(0.5)
    assert sum(s) == 3.5
    d = {1: 1.5}
    d = dict([(2, 3)])
    d[4] = 0.5
    assert sum(d.values()) == 3.5
    f = frozenset([1.5])
    f = frozenset([1, 2])
    assert sum(f | {0.5}) == 3.5
    t = (1.5, 2.5)
    t = tuple([1, 2])
    assert sum(t + (0.5,)) == 3.5


# int->float, new: build
def test_assign_int_float_new_comp():
    a = [1.5]
    a = [i for i in range(3)]
    a.append(0.5)
    assert sum(a) == 3.5
    s = {1.5}
    s = {i for i in range(3)}
    s.add(0.5)
    assert sum(s) == 3.5
    d = {1: 1.5}
    d = {i: i for i in range(3)}
    d[4] = 0.5
    assert sum(d.values()) == 3.5


# int->float, new: copy
def test_assign_int_float_new_copy():
    ints = [1, 2]
    a = [1.5]
    a = list(ints)
    a.append(0.5)
    assert sum(a) == 3.5 and sum(ints) == 3


# int->float, new: copy
def test_assign_int_float_new_slice():
    ints = [1, 2]
    a = [1.5]
    a = ints[:]
    a.append(0.5)
    assert sum(a) == 3.5 and sum(ints) == 3
    b = [1.5]
    b = sorted(ints)
    b.append(0.5)
    assert sum(b) == 3.5
    c = [1.5]
    c = ints.copy()
    c.append(0.5)
    assert sum(c) == 3.5


# int->float, ifexp: build
def test_assign_int_float_ifexp_list():
    c = 3
    a = [1.5]
    a = [1] if c > 2 else [2, 3]
    a.append(0.5)
    assert sum(a) == 1.5


# int->float, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in
#     assignment
#
# def test_assign_int_float_var_list():
#     ints = [1, 2]
#     a = [1.5]
#     a = ints
#     assert sum(a) == 3


# int->float, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple<__ss_float>*' in
#     assignment
#
# def test_assign_int_float_var_tuple():
#     # a tuple cannot be changed, so it could be replaced by a converted copy
#     ints = (1, 2)
#     t = (1.5, 2.5)
#     t = ints
#     assert sum(t + (0.5,)) == 3.5


# int->float, call: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in
#     assignment
#
# def assign_ints():
#     return [1, 2]
#
# def test_assign_int_float_call_list():
#     a = [1.5]
#     a = assign_ints()
#     assert sum(a) == 3


# none, literal: build
def test_assign_none_lit_list():
    a = ['x']
    a = [None]
    assert a[0] is None
    a.append('y')
    assert a[1] == 'y'
    d = {1: 'x'}
    d = {2: None}
    assert d[2] is None


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'a' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_assign_none_scalar_list():
#     a = [1]
#     a = [None]
#     assert a[0] is None


# none, variable: cast
def test_assign_none_var_list():
    nones = [None]
    a = ['x']
    a = nones
    assert a[0] is None and len(a) == 1


# sub->base, literal: cast
def test_assign_sub_lit_list():
    la = [A()]
    la = [B()]
    la.append(A())
    assert [x.name() for x in la] == ['B', 'A']
    da = {1: A()}
    da = {2: B()}
    assert da[2].name() == 'B'


# sub->base, variable: cast
def test_assign_sub_var_list():
    lb = [B()]
    la = [A()]
    la = lb
    assert [x.name() for x in la] == ['B']
    sb = {B()}
    sa = {A()}
    sa = sb
    assert [x.name() for x in sa] == ['B']
    db = {1: B()}
    da = {1: A()}
    da = db
    assert da[1].name() == 'B'
    tb = (B(), B())
    ta = (A(), A())
    ta = tb
    assert ta[1].name() == 'B'


# sub->base, variable: cast
def test_assign_sub_var_nested():
    llb = [[B()]]
    lla = [[A()]]
    lla = llb
    assert lla[0][0].name() == 'B'
    dlb = {1: [B()]}
    dla = {1: [A()]}
    dla = dlb
    assert dla[1][0].name() == 'B'


# sub->base, call: cast
def assign_make_bs():
    return [B()]

def test_assign_sub_call_list():
    la = [A()]
    la = assign_make_bs()
    assert [x.name() for x in la] == ['B']


# empty, literal: build
def test_assign_empty_lit_list():
    a = [1.5]
    a = []
    a.append(0.5)
    assert sum(a) == 0.5
    b = ['x']
    b = []
    b.append('y')
    assert b[0] == 'y'


# empty, literal: build
def test_assign_empty_lit_dict():
    d = {1: 1.5}
    d = {}
    d[2] = 0.5
    assert sum(d.values()) == 0.5
    e = {'a': 'x'}
    e = {}
    e['b'] = 'y'
    assert e['b'] == 'y'


# empty, literal: build
def test_assign_empty_lit_tuple():
    t = (1, 2)
    t = ()
    assert len(t) == 0
    u = ('a', 'b')
    u = ()
    assert len(u) == 0


# empty, literal: build
def test_assign_empty_lit_nested():
    ll = [[1]]
    ll = [[]]
    ll[0].append(2)
    assert sum(ll[0]) == 2
    d = {1: [1]}
    d = {2: []}
    d[2].append(3)
    assert sum(d[2]) == 3
    t = ([1], 'a')
    t = ([], 'b')
    t[0].append(4)
    assert sum(t[0]) == 4


# empty, new: build
def test_assign_empty_new():
    l = [1]
    l = list()
    l.append(2)
    assert sum(l) == 2
    s = {1}
    s = set()
    s.add(2)
    assert sum(s) == 2
    d = {1: 2}
    d = dict()
    d[3] = 4
    assert sum(d.values()) == 4
    f = frozenset([1])
    f = frozenset()
    assert len(f) == 0
    t = (1, 2)
    t = tuple()
    assert len(t) == 0


# empty, new: build
def test_assign_empty_new_collections():
    q = deque([1])
    q = deque()
    q.append(2)
    assert sum(q) == 2
    c = Counter([1])
    c = Counter()
    c[2] += 1
    assert sum(c) == 2
    dd = defaultdict(int, {1: 2})
    dd = defaultdict(int)
    dd[3] += 4
    assert sum(dd.values()) == 4


# empty, new: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_assign_empty_new_from_empty():
#     a = [1]
#     a = list([])
#     a.append(2)
#     assert sum(a) == 2
#     s = {1}
#     s = set([])
#     s.add(2)
#     assert sum(s) == 2


# empty, new: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*' in assignment
#
# def test_assign_empty_new_sorted():
#     b = [1]
#     b = sorted([])
#     b.append(2)
#     assert sum(b) == 2


# empty, new: build
# TODO doesn't work today: warning, then C++ compile error
#   variable 'x' has no type
#   C++: invalid conversion from 'void*' to '__ss_int'
#
# def test_assign_empty_new_comp():
#     c = [1]
#     c = [x for x in []]
#     c.append(2)
#     assert sum(c) == 2


# empty, ifexp: build
def test_assign_empty_ifexp():
    c = 3
    a = [1]
    a = [] if c > 2 else []
    a.append(2)
    assert sum(a) == 2
    b = [1]
    b = [] if c > 2 else [5]
    b.append(2)
    assert sum(b) == 2


# empty, variable: infer
def test_assign_empty_var_filled():
    # the empty list is added to later, which gives it its element type
    e = []
    g = [1]
    g = e
    g.append(2)
    assert sum(e) == 2
    n = []
    m = ['a']
    m = n
    n.append('b')
    assert m[0] == 'b'


# empty, variable: cast
def test_assign_empty_var():
    # nothing is ever added, so the list has no element type
    e = []
    f = [B()]
    f = e
    assert len(f) == 0
    n = []
    m = ['a']
    m = n
    assert len(m) == 0


# empty, variable: cast
def test_assign_empty_var_set_dict():
    es = set()
    s = {'a'}
    s = es
    assert len(s) == 0
    ed = {}
    d = {'a': 'b'}
    d = ed
    assert len(d) == 0
    et = ()
    t = ('a', 'b')
    t = et
    assert len(t) == 0


# empty, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*' in assignment
#
# def test_assign_empty_var_number():
#     e = []
#     g = [1]
#     g = e
#     assert len(g) == 0


# empty, variable: warn
# TODO should give a warning, but today: works
#
# def test_assign_empty_var_shared():
#     # one empty list that meets two different element types
#     e = []
#     a = ['x']
#     a = e
#     b = [B()]
#     b = e
#     assert len(a) == 0 and len(b) == 0


# empty, call: build
def assign_empty_ints():
    return []

def assign_empty_strs():
    return []

def test_assign_empty_call():
    a = [1]
    a = assign_empty_ints()
    a.append(2)
    assert sum(a) == 2
    b = ['x']
    b = assign_empty_strs()
    assert len(b) == 0


# empty, call: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*' in assignment
#
# def assign_empty_shared():
#     return []
#
# def test_assign_empty_call_shared():
#     # one function that returns an empty list, for two element types
#     a = [1]
#     a = assign_empty_shared()
#     b = ['x']
#     b = assign_empty_shared()
#     assert len(a) == 0 and len(b) == 0


#=========================================================================
# 2. ATTR: assigning to an instance attribute
#
# as for variables, but the attribute is shared by all instances
#=========================================================================


# int->float, literal: build
class AttrIntFloatLit:
    def __init__(self):
        self.x = 1.5
        self.l = [1.5]
        self.d = {1: [1.5]}

def test_attr_int_float_lit():
    h = AttrIntFloatLit()
    h.x = 1
    assert h.x + 0.5 == 1.5
    h.l = [1, 2]
    h.l.append(0.5)
    assert sum(h.l) == 3.5
    h.d = {2: [3]}
    h.d[2].append(0.5)
    assert sum(h.d[2]) == 3.5


# int->float, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in
#     assignment
#
# class AttrIntFloatVar:
#     def __init__(self):
#         self.l = [1.5]
#
# def test_attr_int_float_var():
#     ints = [1, 2]
#     h = AttrIntFloatVar()
#     h.l = ints
#     assert sum(h.l) == 3


# none, literal: cast
class AttrNone:
    def __init__(self):
        self.s = 'a'
        self.l = [1]
        self.o = A()
        self.names = ['a']

def test_attr_none_lit():
    h = AttrNone()
    h.s = None
    h.l = None
    h.o = None
    assert h.s is None and h.l is None and h.o is None
    h.names = [None]
    assert h.names[0] is None


# sub->base, new: cast
class AttrSub:
    def __init__(self):
        self.o = A()
        self.la = [A()]

def test_attr_sub_new():
    h = AttrSub()
    h.o = B()
    assert h.o.name() == 'B'
    h.la = [B()]
    assert h.la[0].name() == 'B'


# sub->base, variable: cast
class AttrSubVar:
    def __init__(self):
        self.o = A()
        self.la = [A()]

def test_attr_sub_var():
    b = B()
    lb = [B()]
    h = AttrSubVar()
    h.o = b
    assert h.o.name() == 'B'
    h.la = lb
    assert h.la[0].name() == 'B'


# empty, literal: infer
class AttrEmptyInit:
    def __init__(self):
        self.l = []
        self.d = {}
        self.s = set()
        self.names = []

def test_attr_empty_lit_init():
    h = AttrEmptyInit()
    h.l.append(1)
    h.d[1] = 2.5
    h.s.add('a')
    h.names.append(['x'])
    assert sum(h.l) == 1 and h.d[1] == 2.5 and 'a' in h.s
    assert h.names[0][0] == 'x'


# empty, literal: build
class AttrEmptyLit:
    def __init__(self):
        self.l = [1]
        self.d = {1: 'a'}
        self.ll = [[1]]

def test_attr_empty_lit():
    h = AttrEmptyLit()
    h.l = []
    h.l.append(2)
    assert sum(h.l) == 2
    h.d = {}
    h.d[2] = 'b'
    assert h.d[2] == 'b'
    h.ll = [[]]
    h.ll[0].append(3)
    assert sum(h.ll[0]) == 3


# empty, literal: infer
class AttrEmptyNever:
    def __init__(self):
        self.l = []

def test_attr_empty_lit_never():
    # nothing is ever added to the attribute
    h = AttrEmptyNever()
    assert len(h.l) == 0
    assert not h.l


# empty, variable: cast
class AttrEmptyVar:
    def __init__(self):
        self.names = ['a']

def test_attr_empty_var():
    e = []
    h = AttrEmptyVar()
    h.names = e
    assert len(h.names) == 0


# empty, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*' in assignment
#
# class AttrEmptyVarNumber:
#     def __init__(self):
#         self.l = [1]
#
# def test_attr_empty_var_number():
#     e = []
#     h = AttrEmptyVarNumber()
#     h.l = e
#     assert len(h.l) == 0


#=========================================================================
# 3. SETITEM: assigning to an item or a slice
#
# the container has its element type already. assigning a slice copies
# the elements, so they can be converted on the way
#=========================================================================


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'd' has dynamic (sub)type: {bool, int}
#   variable 'l' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_setitem_bool_int_lit():
#     l = [1, 2]
#     l[0] = True
#     assert sum(l) == 3
#     d = {1: 2}
#     d[3] = True
#     assert sum(d.values()) == 3


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'l' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_setitem_none_scalar():
#     l = [1, 2]
#     l[0] = None
#     assert l[0] is None and l[1] == 2


# int->float, literal: implicit
def test_setitem_int_float_lit_scalar():
    l = [1.5]
    l[0] = 1
    assert l[0] + 0.5 == 1.5
    d = {1: 1.5}
    d[2] = 3
    assert sum(d.values()) == 4.5


# int->float, literal: implicit
def test_setitem_int_float_lit_key():
    d = {1.5: 'a'}
    d[2] = 'b'
    assert sum(d) == 3.5


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_setitem_int_float_lit_key_tuple():
#     e = {(1.5, 2.5): 'a'}
#     e[(1, 2)] = 'b'
#     assert len(e) == 2
#     assert sum(k[0] for k in e) == 2.5


# int->float, literal: build
def test_setitem_int_float_lit_list():
    ll = [[1.5]]
    ll[0] = [7]
    ll[0].append(0.5)
    assert sum(ll[0]) == 7.5


# int->float, literal: build
def test_setitem_int_float_lit_dict_value():
    d = {1: [1.5]}
    d[2] = [1]
    d[3] = [4, 5]
    d[2].append(0.5)
    assert sum(d[2]) == 1.5 and sum(d[3]) == 9


# int->float, literal: build
# TODO doesn't work today: wrong result, without a warning
#   at run-time: AssertionError
#
# def test_setitem_int_float_lit_tuple():
#     m = [(1.5, 'a')]
#     m[0] = (2, 'b')
#     assert m[0][0] + 0.5 == 2.5


# int->float, variable: warn
# TODO should give a warning, but today: wrong result, without a warning
#   at run-time: AssertionError
#
# def test_setitem_int_float_var_list():
#     ints = [3]
#     d = {1: [1.0]}
#     d[2] = ints
#     assert sum(d[2]) == 3


# int->float, literal: copy
def test_setitem_int_float_lit_slice():
    l = [1.5, 2.5]
    l[0:1] = [1, 2]
    assert sum(l) == 5.5


# int->float, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to
#     'list<__ss_float>::__setslice__(__ss_int, __ss_int, __ss_int,
#     __ss_int, list<__ss_int>*&)'
#
# def test_setitem_int_float_var_slice():
#     ints = [1, 2]
#     l = [1.5, 2.5]
#     l[0:1] = ints
#     assert sum(l) == 5.5 and sum(ints) == 3


# none, literal: cast
def test_setitem_none_lit():
    l = ['a']
    l[0] = None
    assert l[0] is None
    n = [[1]]
    n[0] = None
    assert n[0] is None
    e = {1: 'a'}
    e[2] = None
    assert e[2] is None


# sub->base, new: cast
def test_setitem_sub_new():
    la = [A(), A()]
    la[0] = B()
    assert [x.name() for x in la] == ['B', 'A']
    lists = [[A()]]
    lists[0] = [B()]
    assert lists[0][0].name() == 'B'
    d = {1: A()}
    d[2] = B()
    assert d[2].name() == 'B'


# sub->base, variable: cast
def test_setitem_sub_var():
    lb = [B()]
    lists = [[A()]]
    lists[0] = lb
    assert lists[0][0].name() == 'B'
    d = {1: [A()]}
    d[2] = lb
    assert d[2][0].name() == 'B'


# empty, literal: build
def test_setitem_empty_lit():
    ll = [[1]]
    ll[0] = []
    ll[0].append(2)
    assert sum(ll[0]) == 2
    d = {1: [1.5]}
    d[2] = []
    d[2].append(0.5)
    assert sum(d[2]) == 0.5
    names = {1: ['a']}
    names[2] = []
    assert len(names[2]) == 0


# empty, new: build
def test_setitem_empty_new():
    ds = {1: {1}}
    ds[2] = set()
    ds[2].add(3)
    assert sum(ds[2]) == 3
    dd = {1: {1: 2}}
    dd[2] = {}
    dd[2][3] = 4
    assert sum(dd[2].values()) == 4
    dl = {1: [1]}
    dl[2] = list()
    dl[2].append(5)
    assert sum(dl[2]) == 5


# empty, variable: cast
def test_setitem_empty_var():
    e = []
    d = {1: ['a']}
    d[2] = e
    assert len(d[2]) == 0
    ll = [[B()]]
    ll[0] = e
    assert len(ll[0]) == 0


# empty, variable: warn
# TODO should give a warning, but today: works
#
# def test_setitem_empty_var_number():
#     e = []
#     d = {1: [1]}
#     d[2] = e
#     assert len(d[2]) == 0


# empty, literal: copy
def test_setitem_empty_lit_slice():
    l = [1, 2, 3]
    l[0:2] = []
    assert sum(l) == 3
    names = ['a', 'b']
    names[1:] = []
    assert len(names) == 1


# empty, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to
#     'list<__ss_int>::__setslice__(__ss_int, __ss_int, __ss_int,
#     __ss_int, list<void*>*&)'
#
# def test_setitem_empty_var_slice():
#     e = []
#     l = [1, 2, 3]
#     l[0:2] = e
#     assert sum(l) == 3


#=========================================================================
# 4. ARG: passing an argument to a user function, method, constructor or lambda
#
# a formal argument has the type of everything that is passed for it,
# over all calls
#=========================================================================


# int->float, literal: implicit
def arg_half(x):
    return x / 2

def test_arg_int_float_lit_scalar():
    assert arg_half(1.5) == 0.75
    assert arg_half(1) == 0.5
    i = 3
    assert arg_half(i) == 1.5


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'i' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: invalid conversion from 'pyobj*' to '__ss_int'
#
# def arg_inc(i):
#     return i + 1
#
# def test_arg_bool_int():
#     assert arg_inc(1) == 2
#     assert arg_inc(True) == 2


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'i' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def arg_or_default(i=None):
#     if i is None:
#         return -1
#     return i
#
# def test_arg_none_scalar():
#     assert arg_or_default() == -1
#     assert arg_or_default(0) == 0
#     assert arg_or_default(3) == 3


# int->float, literal: build
def arg_total(l):
    l.append(0.5)
    return sum(l)

def test_arg_int_float_lit_list():
    assert arg_total([0.5]) == 1
    assert arg_total([1, 2]) == 3.5


# int->float, literal: build
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'set<__ss_int>*' to 'set<__ss_float>*'
#
# def arg_total_set(s):
#     return sum(s)
#
# def test_arg_int_float_lit_set():
#     assert arg_total_set({0.5}) == 0.5
#     assert arg_total_set({1, 2}) == 3


# int->float, literal: build
def arg_total_dict(d):
    return sum(d.values())

def test_arg_int_float_lit_dict():
    assert arg_total_dict({1: 0.5}) == 0.5
    assert arg_total_dict({1: 2}) == 2


# int->float, literal: build
def arg_total_tuple(t):
    return sum(t)

def test_arg_int_float_lit_tuple():
    assert arg_total_tuple((0.5, 1.5)) == 2
    assert arg_total_tuple((1, 2)) == 3


# int->float, literal: build
def arg_total_nested(ll):
    return sum(ll[0])

def test_arg_int_float_lit_nested():
    assert arg_total_nested([[0.5]]) == 0.5
    assert arg_total_nested([[1, 2]]) == 3


# int->float, ifexp: build
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*'
#
# def arg_total_ifexp(l):
#     return sum(l)
#
# def test_arg_int_float_ifexp():
#     c = 3
#     assert arg_total_ifexp([0.5]) == 0.5
#     assert arg_total_ifexp([1] if c > 2 else [2, 3]) == 1
#     assert arg_total_ifexp([1] if c < 2 else [2, 3]) == 5


# int->float, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*'
#
# def arg_total_var(l):
#     return sum(l)
#
# def test_arg_int_float_var_list():
#     ints = [1, 2]
#     assert arg_total_var([0.5]) == 0.5
#     assert arg_total_var(ints) == 3


# int->float, literal: build
def arg_default_scalar(x=1):
    return x + 0.5

def arg_default_tuple(t=(1, 2)):
    return sum(t)

def test_arg_int_float_default():
    assert arg_default_scalar() == 1.5
    assert arg_default_scalar(2.5) == 3
    assert arg_default_tuple() == 3
    assert arg_default_tuple((0.5, 1.5)) == 2


# int->float, literal: build
def arg_keyword(n, l=None):
    if l is None:
        return n
    return n + sum(l)

def test_arg_int_float_keyword():
    assert arg_keyword(1) == 1
    assert arg_keyword(1, l=[0.5]) == 1.5
    assert arg_keyword(1, l=[1, 2]) == 4


# int->float, literal: build
class ArgBox:
    def __init__(self, l):
        self.l = l

    def add(self, l):
        self.l = self.l + l

def test_arg_int_float_method():
    box = ArgBox([1.5])
    assert sum(box.l) == 1.5
    box2 = ArgBox([1, 2])
    assert sum(box2.l) == 3
    box2.add([0.5])
    box2.add([1])
    assert sum(box2.l) == 4.5


# int->float, literal: build
def test_arg_int_float_lambda():
    f = lambda l: sum(l)
    assert f([0.5]) == 0.5
    assert f([1, 2]) == 3


# none, literal: cast
def arg_is_none(s):
    return s is None

def arg_len(l=None):
    if l is None:
        return -1
    return len(l)

def test_arg_none():
    assert not arg_is_none('a')
    assert arg_is_none(None)
    assert arg_len() == -1
    assert arg_len([1]) == 1
    assert arg_len(None) == -1


# sub->base, new: cast
def arg_name(o):
    return o.name()

def arg_names(l):
    return [o.name() for o in l]

def test_arg_sub_new():
    assert arg_name(A()) == 'A'
    assert arg_name(B()) == 'B'
    assert arg_names([A()]) == ['A']
    assert arg_names([B()]) == ['B']


# sub->base, variable: cast
def arg_names_var(l):
    return [o.name() for o in l]

def arg_names_nested(ll):
    return [o.name() for l in ll for o in l]

def test_arg_sub_var():
    lb = [B()]
    assert arg_names_var([A()]) == ['A']
    assert arg_names_var(lb) == ['B']
    llb = [[B()]]
    assert arg_names_nested([[A()]]) == ['A']
    assert arg_names_nested(llb) == ['B']


# empty, literal: build
def arg_empty_total(l):
    return sum(l)

def arg_empty_names(l):
    return len(l)

def test_arg_empty_lit():
    assert arg_empty_total([1, 2]) == 3
    assert arg_empty_total([]) == 0
    assert arg_empty_names(['a']) == 1
    assert arg_empty_names([]) == 0


# empty, new: build
def arg_empty_total_set(s):
    return sum(s)

def arg_empty_total_dict(d):
    return sum(d.values())

def arg_empty_total_tuple(t):
    return sum(t)

def test_arg_empty_new():
    assert arg_empty_total_set({1, 2}) == 3
    assert arg_empty_total_set(set()) == 0
    assert arg_empty_total_dict({1: 2}) == 2
    assert arg_empty_total_dict({}) == 0
    assert arg_empty_total_tuple((1, 2)) == 3
    assert arg_empty_total_tuple(()) == 0


# empty, literal: build
def arg_empty_total_nested(ll):
    return sum(len(l) for l in ll)

def test_arg_empty_lit_nested():
    assert arg_empty_total_nested([[1], [2, 3]]) == 3
    assert arg_empty_total_nested([[]]) == 0
    assert arg_empty_total_nested([[1], []]) == 1
    assert arg_empty_total_nested([]) == 0


# empty, literal: infer
def arg_empty_only(l):
    return len(l)

def test_arg_empty_lit_only():
    # the function is only ever called with an empty list
    assert arg_empty_only([]) == 0


# empty, literal: build
def arg_empty_default_list(l=[]):
    return sum(l)

def arg_empty_default_dict(d={}):
    return sum(d.values())

def arg_empty_default_tuple(t=()):
    return sum(t)

def test_arg_empty_default():
    assert arg_empty_default_list() == 0
    assert arg_empty_default_list([1, 2]) == 3
    assert arg_empty_default_dict() == 0
    assert arg_empty_default_dict({1: 2}) == 2
    assert arg_empty_default_tuple() == 0
    assert arg_empty_default_tuple((1, 2)) == 3


# empty, literal: build
class ArgEmptyBox:
    def __init__(self, l):
        self.l = l

    def total(self, extra):
        return sum(self.l) + sum(extra)

def test_arg_empty_method():
    box = ArgEmptyBox([1, 2])
    assert box.total([3]) == 6
    assert box.total([]) == 3
    box2 = ArgEmptyBox([])
    assert box2.total([]) == 0
    box2.l.append(4)
    assert box2.total([1]) == 5


# empty, variable: cast
def arg_empty_names_var(l):
    return len(l)

def test_arg_empty_var():
    e = []
    assert arg_empty_names_var(['a']) == 1
    assert arg_empty_names_var(e) == 0


# empty, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*'
#
# def arg_empty_total_var(l):
#     return sum(l)
#
# def test_arg_empty_var_number():
#     e = []
#     assert arg_empty_total_var([1]) == 1
#     assert arg_empty_total_var(e) == 0


#=========================================================================
# 5. RET: returning or yielding from a user function or lambda
#
# the return type is the type of everything that is returned
#=========================================================================


# int->float, literal: implicit
def ret_scalar(c):
    if c:
        return 1.5
    return 1

def test_ret_int_float_lit_scalar():
    assert ret_scalar(True) == 1.5
    assert ret_scalar(False) + 0.5 == 1.5


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   expression has dynamic (sub)type: {bool, int}
#   C++: could not convert '2' from '__ss_int' to '__ss_bool' (only when
#     part of this file: the cell works on its own)
#
# def ret_bool_int(c):
#     if c:
#         return 2
#     return True
#
# def test_ret_bool_int():
#     assert ret_bool_int(True) + 1 == 3
#     assert ret_bool_int(False) + 1 == 2


# none->scalar, literal: warn
# -> warning, then wrong result (see tests/errs/103.py)
#   expression has dynamic (sub)type: {None, int}
#   at run-time: AssertionError
#
# def ret_none_scalar(c):
#     if c:
#         return 0
#     return None
#
# def test_ret_none_scalar():
#     assert ret_none_scalar(True) == 0
#     assert ret_none_scalar(False) is None


# int->float, literal: build
def ret_list(c):
    if c:
        return [1.5]
    return [1, 2]

def ret_dict(c):
    if c:
        return {1: 1.5}
    return {2: 3}

def ret_tuple(c):
    if c:
        return (1.5, [1.5])
    return (1, [1])

def test_ret_int_float_lit_list():
    r = ret_list(False)
    r.append(0.5)
    assert sum(r) == 3.5
    assert sum(ret_list(True)) == 1.5
    d = ret_dict(False)
    d[4] = 0.5
    assert sum(d.values()) == 3.5
    t = ret_tuple(False)
    t[1].append(0.5)
    assert t[0] + sum(t[1]) == 2.5


# int->float, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in return
#
# def ret_var(c):
#     ints = [1, 2]
#     if c:
#         return [1.5]
#     return ints
#
# def test_ret_int_float_var_list():
#     assert sum(ret_var(False)) == 3


# int->float, literal: implicit
def ret_gen_scalar():
    yield 1
    yield 2.5

def test_ret_int_float_yield_scalar():
    assert sum(ret_gen_scalar()) == 3.5


# int->float, literal: build
def ret_gen_list():
    yield [1.5]
    yield [1, 2]

def test_ret_int_float_yield_list():
    ls = list(ret_gen_list())
    ls[1].append(0.5)
    assert sum(ls[1]) == 3.5


# int->float, literal: build
def test_ret_int_float_lambda():
    f = lambda c: [1.5] if c else [1, 2]
    r = f(False)
    r.append(0.5)
    assert sum(r) == 3.5


# none, literal: cast
def ret_none_str(c):
    if c:
        return 'a'
    return None

def ret_none_list(c):
    if c:
        return [1]
    return None

def ret_none_elem(c):
    if c:
        return ['a']
    return [None]

def test_ret_none():
    assert ret_none_str(True) == 'a'
    assert ret_none_str(False) is None
    assert ret_none_list(False) is None
    assert ret_none_elem(False)[0] is None


# sub->base, new: cast
def ret_sub(c):
    if c:
        return A()
    return B()

def ret_sub_list(c):
    if c:
        return [A()]
    return [B()]

def test_ret_sub_new():
    assert ret_sub(True).name() == 'A'
    assert ret_sub(False).name() == 'B'
    assert ret_sub_list(False)[0].name() == 'B'


# sub->base, variable: cast
def ret_sub_var(c):
    lb = [B()]
    if c:
        return [A()]
    return lb

def test_ret_sub_var():
    assert ret_sub_var(False)[0].name() == 'B'
    assert ret_sub_var(True)[0].name() == 'A'


# empty, literal: build
def ret_empty_list(c):
    if c:
        return [1]
    return []

def ret_empty_names(c):
    if c:
        return ['a']
    return []

def test_ret_empty_lit():
    r = ret_empty_list(False)
    r.append(2)
    assert sum(r) == 2
    assert sum(ret_empty_list(True)) == 1
    assert len(ret_empty_names(False)) == 0


# empty, new: build
def ret_empty_set(c):
    if c:
        return {1}
    return set()

def ret_empty_dict(c):
    if c:
        return {1: 2}
    return {}

def ret_empty_tuple(c):
    if c:
        return (1, 2)
    return ()

def test_ret_empty_new():
    s = ret_empty_set(False)
    s.add(2)
    assert sum(s) == 2
    d = ret_empty_dict(False)
    d[3] = 4
    assert sum(d.values()) == 4
    assert len(ret_empty_tuple(False)) == 0


# empty, literal: build
def ret_empty_nested(c):
    if c:
        return [[1]]
    return [[]]

def ret_empty_pair(c):
    if c:
        return [1], ['a']
    return [], []

def test_ret_empty_lit_nested():
    r = ret_empty_nested(False)
    r[0].append(2)
    assert sum(r[0]) == 2
    a, b = ret_empty_pair(False)
    a.append(3)
    b.append('x')
    assert sum(a) == 3 and b[0] == 'x'


# empty, literal: infer
def ret_empty_make():
    return []

def ret_empty_make_dict():
    return {}

def test_ret_empty_lit_filled():
    # the result is added to later, which gives it its element type
    l = ret_empty_make()
    l.append(1)
    assert sum(l) == 1
    d = ret_empty_make_dict()
    d['a'] = 2
    assert d['a'] == 2


# empty, variable: cast
def ret_empty_var(c):
    e = []
    if c:
        return ['a']
    return e

def test_ret_empty_var():
    assert len(ret_empty_var(False)) == 0
    assert len(ret_empty_var(True)) == 1


# empty, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*' in return
#
# def ret_empty_var_number(c):
#     e = []
#     if c:
#         return [1]
#     return e
#
# def test_ret_empty_var_number():
#     assert len(ret_empty_var_number(False)) == 0


# empty, literal: build
def ret_empty_gen():
    yield []
    yield [1, 2]

def test_ret_empty_yield():
    ls = list(ret_empty_gen())
    ls[0].append(3)
    assert sum(ls[0]) == 3 and sum(ls[1]) == 3


# empty, literal: build
def test_ret_empty_lambda():
    f = lambda c: [1] if c else []
    r = f(False)
    r.append(2)
    assert sum(r) == 2


# empty, call: cast
def ret_empty_split_ones(xs):
    if not xs:
        return [], []
    return [x for x in xs if x > 1], [x for x in xs if x <= 1]

def ret_empty_copy_list(xs):
    return [x for x in xs]

class RetEmptySplitter:
    def split(self, xs):
        return [x for x in xs if x > 1], [x for x in xs if x <= 1]

def test_ret_empty_call():
    # the declared return type merges over all calls, so differs from the
    # type inferred for a call that only returns empty lists
    assert ret_empty_split_ones([3, 1, 2]) == ([3, 2], [1])
    hi, lo = ret_empty_split_ones([])
    assert len(hi) == 0 and len(lo) == 0
    assert str(hi) == '[]' and str(lo) == '[]'
    r = ret_empty_split_ones([])
    assert r == ([], [])
    r = ret_empty_split_ones([3, 1, 2])
    assert r == ([3, 2], [1])
    assert ret_empty_copy_list([1, 2]) == [1, 2]
    e = ret_empty_copy_list([])
    assert len(e) == 0
    s = RetEmptySplitter()
    assert s.split([3, 1]) == ([3], [1])
    a, b = s.split([])
    assert len(a) == 0 and len(b) == 0


#=========================================================================
# 6. METHOD: adding to a builtin container through a method
#
# methods that add one element (append, add, setdefault) need a value of
# the element type. methods that add all elements of another container
# (extend, update, +=, |=) copy them, so they can convert on the way
#=========================================================================


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'l' has dynamic (sub)type: {bool, int}
#   variable 's' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_method_bool_int_lit():
#     l = [1]
#     l.append(True)
#     assert sum(l) == 2
#     s = {2}
#     s.add(True)
#     assert sum(s) == 3


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'l' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_method_none_scalar():
#     l = [0]
#     l.append(None)
#     assert l[1] is None and l[0] == 0
#     d = {1: 0}
#     assert d.get(2) is None


# int->float, literal: implicit
def test_method_int_float_lit_scalar():
    l = [1.5]
    l.append(1)
    l.insert(0, 2)
    assert sum(l) == 4.5
    s = {1.5}
    s.add(1)
    assert sum(s) == 2.5
    d = {1: 1.5}
    d.setdefault(2, 3)
    assert sum(d.values()) == 4.5
    q = deque([1.5])
    q.append(1)
    q.appendleft(2)
    assert sum(q) == 4.5


# int->float, variable: implicit
def test_method_int_float_var_scalar():
    i = 2
    l = [1.5]
    l.append(i)
    assert sum(l) == 3.5
    d = {1.5: 'a'}
    d.setdefault(i, 'b')
    assert sum(d) == 3.5


# int->float, literal: build
def test_method_int_float_lit_list():
    ll = [[1.5]]
    ll.append([1])
    ll.insert(0, [2])
    ll[0].append(0.5)
    ll[2].append(0.5)
    assert sum(ll[0]) == 2.5 and sum(ll[2]) == 1.5
    sets = [{1.5}]
    sets.append({1})
    sets[1].add(0.5)
    assert sum(sets[1]) == 1.5
    d = {1: [1.5]}
    d.setdefault(2, [3]).append(0.5)
    assert sum(d[2]) == 3.5
    q = deque([[1.5]])
    q.append([1])
    q[1].append(0.5)
    assert sum(q[1]) == 1.5


# int->float, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*'
#
# def test_method_int_float_var_list():
#     ints = [1]
#     ll = [[1.5]]
#     ll.append(ints)
#     assert sum(ll[1]) == 1


# int->float, literal: copy
def test_method_int_float_lit_iter_list():
    l = [1.5]
    l.extend([1, 2])
    l += [3]
    assert sum(l) == 7.5


# int->float, literal: copy
def test_method_int_float_lit_iter_set():
    s = {1.5}
    s.update([1, 2])
    assert sum(s) == 4.5


# int->float, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<__ss_float>*'
#
# def test_method_int_float_lit_iter_set_ior():
#     s = {1.5}
#     s |= {3}
#     assert sum(s) == 4.5


# int->float, literal: copy
def test_method_int_float_lit_iter_dict():
    d = {1: 1.5}
    d.update({2: 3})
    d |= {3: 4}
    assert sum(d.values()) == 8.5


# int->float, literal: copy
def test_method_int_float_lit_iter_deque():
    q = deque([0.5])
    q.extend([1, 2])
    q.extendleft(range(2))
    q += [3]
    assert sum(q) == 7.5


# int->float, variable: copy
def test_method_int_float_var_iter_list():
    ints = [1, 2]
    l = [1.5]
    l.extend(ints)
    assert sum(l) == 4.5 and sum(ints) == 3


# int->float, variable: copy
def test_method_int_float_var_iter_list_iadd():
    ints = [1, 2]
    l = [1.5]
    l += ints
    assert sum(l) == 4.5 and sum(ints) == 3


# int->float, variable: copy
def test_method_int_float_var_iter_set():
    ints = [1, 2]
    s = {1.5}
    s.update(ints)
    assert sum(s) == 4.5


# int->float, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<__ss_float>*'
#
# def test_method_int_float_var_iter_set_ior():
#     intset = {1, 2}
#     s = {2.5}
#     s |= intset
#     assert sum(s) == 5.5 and sum(intset) == 3


# int->float, variable: copy
def test_method_int_float_var_iter_dict():
    intdict = {2: 3}
    d = {1: 1.5}
    d.update(intdict)
    assert sum(d.values()) == 4.5
    d2 = {1: 1.5}
    d2 |= intdict
    assert sum(d2.values()) == 4.5


# int->float, variable: copy
def test_method_int_float_var_iter_deque():
    ints = [1, 2]
    q = deque([0.5])
    q.extend(ints)
    q += ints
    assert sum(q) == 6.5


# none, literal: cast
def test_method_none():
    l = ['a']
    l.append(None)
    assert l[1] is None
    ll = [[1]]
    ll.append(None)
    assert ll[1] is None
    d = {1: 'a'}
    d.setdefault(2, None)
    assert d[2] is None
    names = [['a']]
    names.append([None])
    assert names[1][0] is None


# sub->base, new: cast
def test_method_sub_new():
    la = [A()]
    la.append(B())
    la.insert(0, B())
    la.extend([B()])
    la += [B()]
    assert [x.name() for x in la] == ['B', 'A', 'B', 'B', 'B']
    lla = [[A()]]
    lla.append([B()])
    assert lla[1][0].name() == 'B'
    sa = {A()}
    sa.add(B())
    assert sorted(x.name() for x in sa) == ['A', 'B']
    da = {1: A()}
    da.setdefault(2, B())
    assert da[2].name() == 'B'


# sub->base, variable: cast
def test_method_sub_var():
    b = B()
    lb = [B()]
    la = [A()]
    la.append(b)
    la.extend(lb)
    la += lb
    assert [x.name() for x in la] == ['A', 'B', 'B', 'B']
    lla = [[A()]]
    lla.append(lb)
    assert lla[1][0].name() == 'B'
    d = {1: [A()]}
    d.setdefault(2, lb)
    assert d[2][0].name() == 'B'


# empty, literal: infer
def test_method_empty_receiver():
    # an empty container gets its element type from what is added to it
    l = []
    l.append(1)
    l.extend([2, 3])
    l.insert(0, 4)
    assert sum(l) == 10
    d = {}
    d[1] = 'a'
    d.setdefault(2, 'b')
    d.update({3: 'c'})
    assert sorted(d) == [1, 2, 3]
    names = []
    names.append('a')
    assert names[0] == 'a'
    ll = []
    ll.append([1])
    assert sum(ll[0]) == 1


# empty, new: infer
def test_method_empty_receiver_new():
    s = set()
    s.add(1)
    s.update([2, 3])
    assert sum(s) == 6
    l = list()
    l.append(1.5)
    assert sum(l) == 1.5
    d = dict()
    d['a'] = 1
    assert d['a'] == 1
    q = deque()
    q.append(1)
    q.appendleft(2)
    assert sum(q) == 3
    c = Counter()
    c['a'] += 1
    c.update('ab')
    assert c['a'] == 2
    dd = defaultdict(list)
    dd[1].append('x')
    assert dd[1][0] == 'x'


# empty, literal: build
def test_method_empty_lit_elem():
    ll = [[1]]
    ll.append([])
    ll.insert(0, [])
    ll[0].append(2)
    ll[2].append(3)
    assert sum(ll[0]) == 2 and sum(ll[2]) == 3
    d = {1: [1]}
    d.setdefault(2, []).append(3)
    assert sum(d[2]) == 3
    names = [['a']]
    names.append([])
    assert len(names[1]) == 0


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' (only
#     when part of this file: the cell works on its own. the deque gets
#     the element type of the deque in test_method_int_float_lit_list)
#
# def test_method_empty_lit_elem_deque():
#     q = deque([[1]])
#     q.append([])
#     q[1].append(2)
#     assert sum(q[1]) == 2


# empty, new: build
def test_method_empty_new_elem():
    sets = [{1}]
    sets.append(set())
    sets[1].add(2)
    assert sum(sets[1]) == 2
    dicts = [{1: 2}]
    dicts.append({})
    dicts[1][3] = 4
    assert sum(dicts[1].values()) == 4
    d = {1: {1}}
    d.setdefault(2, set()).add(3)
    assert sum(d[2]) == 3


# empty, variable: cast
def test_method_empty_var_elem():
    e = []
    names = [['a']]
    names.append(e)
    assert len(names[1]) == 0
    g = [[B()]]
    g.append(e)
    assert len(g[1]) == 0
    d = {1: ['a']}
    d.setdefault(2, e)
    assert len(d[2]) == 0


# empty, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*'
#
# def test_method_empty_var_elem_number():
#     e = []
#     ll = [[1]]
#     ll.append(e)
#     assert len(ll[1]) == 0


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_lit_iter():
#     l = [1]
#     l.extend([])
#     assert sum(l) == 1
#     names = ['a']
#     names.extend([])
#     assert len(names) == 1


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_lit_iter_iadd():
#     l = [1]
#     l += []
#     assert sum(l) == 1
#     names = ['a']
#     names += []
#     assert len(names) == 1


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no match for 'operator[]' (operand types are '__GC_DICT<__ss_int,
#     __ss_int>' and
#
# def test_method_empty_lit_iter_dict():
#     d = {1: 2}
#     d.update({})
#     assert sum(d.values()) == 2
#     e = {1: 2}
#     e |= {}
#     assert sum(e.values()) == 2


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'pyseq<void*>::for_in_unit' to '__ss_int'
#
# def test_method_empty_lit_iter_deque():
#     q = deque([1])
#     q.extend([])
#     q.extendleft([])
#     assert sum(q) == 1


# empty, new: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'set<void*>::for_in_unit' to '__ss_int'
#
# def test_method_empty_new_iter_set():
#     s = {1}
#     s.update(set())
#     assert sum(s) == 1
#     strs = {'a'}
#     strs.update(set())
#     assert len(strs) == 1


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'pyseq<void*>::for_in_unit' to '__ss_int'
#
# def test_method_empty_lit_iter_set():
#     s = {1}
#     s.update([])
#     assert sum(s) == 1


# empty, new: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_new_iter_list():
#     l = [1]
#     l.extend(())
#     l.extend(set())
#     assert sum(l) == 1


# empty, new: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<__ss_int>*'
#
# def test_method_empty_new_iter_set_ior():
#     s = {1}
#     s |= set()
#     assert sum(s) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_var_iter():
#     e = []
#     names = ['a']
#     names.extend(e)
#     assert len(names) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_var_iter_iadd():
#     e = []
#     names = ['a']
#     names += e
#     assert len(names) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<str*>*'
#
# def test_method_empty_var_iter_set():
#     e = []
#     strs = {'a'}
#     strs.update(e)
#     assert len(strs) == 1
#     es = set()
#     strs |= es
#     assert len(strs) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_var_iter_number():
#     e = []
#     l = [1]
#     l.extend(e)
#     assert sum(l) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_method_empty_var_iter_iadd_number():
#     e = []
#     l = [1]
#     l += e
#     assert sum(l) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<__ss_int>*'
#
# def test_method_empty_var_iter_set_number():
#     e = []
#     s = {1}
#     s.update(e)
#     assert sum(s) == 1
#     es = set()
#     s |= es
#     assert sum(s) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no match for 'operator[]' (operand types are '__GC_DICT<str*,
#     str*>' {aka 'boost::unordered::unordered_flat_map<str*, str*,
#     ss_hash<str*>, ss_eq<str*>, __ss_era
#
# def test_method_empty_var_iter_dict():
#     e = {}
#     d = {'a': 'b'}
#     d.update(e)
#     d |= e
#     assert len(d) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no match for 'operator[]' (operand types are '__GC_DICT<__ss_int,
#     __ss_int>' and
#
# def test_method_empty_var_iter_dict_number():
#     e = {}
#     n = {1: 2}
#     n.update(e)
#     n |= e
#     assert sum(n.values()) == 2


#=========================================================================
# 7. DISPLAY: the elements of a list, set, dict or tuple display
#
# the elements have to become the element type of the display
#=========================================================================


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'l' has dynamic (sub)type: {bool, int}
#   variable 'd' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_display_bool_int():
#     l = [1, True]
#     assert sum(l) == 2
#     d = {1: 2, 3: True}
#     assert sum(d.values()) == 3


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'l' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: cannot convert 'list<__ss_int>*' to 'list<pyobj*>*' in assignment
#
# def test_display_none_scalar():
#     l = [0, None]
#     assert l[1] is None and l[0] is not None


# int->float, literal: implicit
def test_display_int_float_scalar():
    l = [1, 2.5]
    assert sum(l) == 3.5
    s = {1, 2.5}
    assert sum(s) == 3.5
    d = {1: 1, 2: 2.5}
    assert sum(d.values()) == 3.5
    e = {1: 'a', 2.5: 'b'}
    assert sum(e) == 3.5
    c = [x if x > 1 else 0.5 for x in [1, 2]]
    assert sum(c) == 2.5


# int->complex, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'l' has dynamic (sub)type: {complex, float, int}
#   expression has dynamic (sub)type: {complex, float, int}
#   C++: cannot convert 'list<complex>*' to 'list<pyobj*>*' in assignment
#
# def test_display_complex():
#     l = [1, 2.5, 1j]
#     assert sum(l) == complex(3.5, 1)


# int->float, variable: implicit
def test_display_int_float_var_scalar():
    i = 1
    x = 2.5
    l = [i, x]
    assert sum(l) == 3.5
    d = {i: x, x: i}
    assert sum(d) == 3.5 and sum(d.values()) == 3.5


# int->float, literal: build
def test_display_int_float_nested():
    ll = [[1.5], [1]]
    ll[1].append(0.5)
    assert sum(ll[1]) == 1.5
    ld = [{1: 1.5}, {2: 3}]
    ld[1][4] = 0.5
    assert sum(ld[1].values()) == 3.5
    lt = [(1.5, 'a'), (1, 'b')]
    assert lt[1][0] + 0.5 == 1.5
    dl = {1: [1.5], 2: [1]}
    dl[2].append(0.5)
    assert sum(dl[2]) == 1.5
    tl = ([1.5], [1])
    tl[1].append(0.5)
    assert sum(tl[1]) == 1.5


# int->float, variable: warn
# -> warning, then wrong result (see tests/errs/103.py)
#   incompatible types
#   at run-time: AssertionError
#
# def test_display_int_float_var_list():
#     ints = [1]
#     floats = [1.5]
#     ll = [floats, ints]
#     assert sum(ll[1]) == 1


# none, literal: cast
def test_display_none():
    l = [None, 'a']
    assert l[0] is None and l[1] == 'a'
    ll = [[1], None]
    assert ll[1] is None
    d = {1: None, 2: 'a'}
    assert d[1] is None
    names = [['a'], [None]]
    assert names[1][0] is None
    nones = [None]
    strs = [['s'], nones]
    assert strs[1][0] is None


# sub->base, new: cast
def test_display_sub_new():
    l = [A(), B()]
    assert [x.name() for x in l] == ['A', 'B']
    ll = [[A()], [B()]]
    assert ll[1][0].name() == 'B'
    d = {1: A(), 2: B()}
    assert d[2].name() == 'B'
    t = (A(), B())
    assert t[1].name() == 'B'
    l3 = [B(), B2()]
    assert [x.name() for x in l3] == ['B', 'B2']


# sub->base, variable: cast
def test_display_sub_var():
    a = A()
    b = B()
    l = [a, b]
    assert [x.name() for x in l] == ['A', 'B']
    lb = [B()]
    ll = [[A()], lb]
    assert ll[1][0].name() == 'B'
    d = {1: [A()], 2: lb}
    assert d[2][0].name() == 'B'


# empty, literal: build
def test_display_empty_lit():
    ll = [[1], []]
    ll[1].append(2)
    assert sum(ll[1]) == 2
    d = {1: [1], 2: []}
    d[2].append(3)
    assert sum(d[2]) == 3
    t = ([1], [])
    t[1].append(4)
    assert sum(t[1]) == 4
    names = [[], ['a']]
    assert len(names[0]) == 0
    lt = [(1, 2), ()]
    assert len(lt[1]) == 0


# empty, new: build
def test_display_empty_new():
    ls = [{1}, set()]
    ls[1].add(2)
    assert sum(ls[1]) == 2
    ld = [{1: 2}, {}]
    ld[1][3] = 4
    assert sum(ld[1].values()) == 4
    lq = [deque([1]), deque()]
    lq[1].append(2)
    assert sum(lq[1]) == 2


# empty, literal: infer
def test_display_empty_lit_only():
    # all elements are empty: they get their type from what is added later
    ll = [[], []]
    ll[0].append(1)
    assert sum(ll[0]) == 1 and len(ll[1]) == 0
    d = {1: []}
    d[1].append('a')
    assert d[1][0] == 'a'
    pairs = [([], 'a')]
    pairs[0][0].append(1.5)
    assert sum(pairs[0][0]) == 1.5
    t = ([], {})
    t[0].append(1)
    t[1]['a'] = 2
    assert sum(t[0]) == 1 and t[1]['a'] == 2


# empty, variable: cast
def test_display_empty_var():
    e = []
    names = [['a'], e]
    assert len(names[1]) == 0
    d = {1: [B()], 2: e}
    assert len(d[2]) == 0


# empty, variable: warn
# -> works (see tests/errs/103.py)
#   incompatible types
#
# def test_display_empty_var_number():
#     e = []
#     ll = [[1], e]
#     assert len(ll[1]) == 0


#=========================================================================
# 8. BINOP: the operands of a binary operator
#
# the result is a new object, so its elements can be converted while
# they are copied from the operands. augmented assignment (+=, |=) changes
# the left operand in place, so only the right one can be converted
#=========================================================================


# bool->int, variable: implicit
def test_binop_bool_arith():
    t, f = True, False
    i, x = 2, 2.0
    assert t / i == 0.5
    assert str(t / t) == '1.0'
    assert str(t // i) == '0'
    assert str(t % i) == '1'
    assert divmod(t, i) == (0, 1)
    assert str(i ** t) == '2'
    assert str(t ** x) == '1.0'
    assert str(t + t) == '2'
    assert str(t * 3) == '3'
    assert str(t + x) == '3.0'
    assert str(-t) == '-1'
    assert str(t & 3) == '1'


# int->float, variable: implicit
def test_binop_int_float_scalar():
    i = 1
    x = 2.5
    assert i + x == 3.5
    assert x - i == 1.5
    assert i * x == 2.5
    assert x // i == 2
    assert i / 2 == 0.5
    assert 2 ** x > 5.6
    y = 1
    y += 0.5
    assert y == 1.5


# int->complex, variable: implicit
def test_binop_complex_scalar():
    i = 1
    x = 2.5
    z = 1j
    assert i + z == complex(1, 1)
    assert z * x == complex(0, 2.5)
    assert x - z == complex(2.5, -1)


# int->complex, literal: build
# TODO doesn't work today: warning, then C++ compile error
#   variable 'l' has dynamic (sub)type: {complex, int}
#   expression has dynamic (sub)type: {complex, int}
#   C++: cannot convert 'list<complex>*' to 'list<pyobj*>*' in assignment
#
# def test_binop_complex_lit_list():
#     l = [1j] + [1]
#     assert sum(l) == complex(1, 1)


# int->float, literal: build
def test_binop_int_float_lit_list():
    a = [1, 2] + [0.5]
    assert sum(a) == 3.5
    b = [0.5] + [1, 2]
    assert sum(b) == 3.5
    c = [1.5, 2.5]
    assert sum(c + [3]) == 7
    assert sum([3] + c) == 7
    assert sum(c + [2, 3]) == 9
    assert sum([2, 3] + c) == 9


# int->float, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'list<__ss_float>*' to 'list<__ss_int>*'
#
# def test_binop_int_float_var_list_lit():
#     ints = [1, 2]
#     assert sum(ints + [0.5]) == 3.5
#     assert sum([0.5] + ints) == 3.5


# int->float, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'list<__ss_float>*' to 'list<__ss_int>*'
#
# def test_binop_int_float_var_list():
#     ints = [1, 2]
#     floats = [1.5]
#     assert sum(ints + floats) == 4.5
#     assert sum(floats + ints) == 4.5


# int->float, literal: build
def test_binop_int_float_lit_mul():
    floats = [0] * 3
    floats[0] = 0.5
    assert sum(floats) == 0.5


# int->float, new: build
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'tuple2<__ss_int, __ss_int>*' to
#     'tuple<__ss_float>*' in assignment
#
# def test_binop_int_float_new_mul_tuple():
#     t = (0, 1) * 2
#     t = (0.5, 1.5)
#     assert sum(t) == 2


# int->float, literal: build
def test_binop_int_float_lit_tuple():
    t = (1.5, 2.5)
    assert sum(t + (1, 2)) == 7
    assert sum((1, 2) + t) == 7
    assert sum((1, 2) + (0.5,)) == 3.5


# int->float, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_binop_int_float_var_tuple():
#     ints = (1, 2)
#     floats = (1.5, 2.5)
#     assert sum(floats + ints) == 7
#     assert sum(ints + floats) == 7


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<__ss_float>*'
#
# def test_binop_int_float_lit_set():
#     s = {1.0, 2.5}
#     assert sum(s | {3}) == 6.5
#     assert sum(s & {1}) == 1
#     assert sum(s - {1}) == 2.5
#     assert sum(s ^ {1, 5}) == 7.5


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_float>*' to 'set<__ss_int>*'
#
# def test_binop_int_float_lit_set_left():
#     s = {1.0, 2.5}
#     assert sum({3} | s) == 6.5
#     assert sum({1, 5} ^ s) == 7.5
#     assert sum({1, 5} & s) == 1
#     assert sum({1, 5} - s) == 5


# int->float, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<__ss_float>*'
#
# def test_binop_int_float_var_set():
#     s = {1.0, 2.5}
#     t = {1, 5}
#     assert sum(s | t) == 8.5
#     assert sum(s & t) == 1
#     assert sum(s - t) == 2.5
#     assert sum(s ^ t) == 7.5


# int->float, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_float>*' to 'set<__ss_int>*'
#
# def test_binop_int_float_var_set_left():
#     s = {1.0, 2.5}
#     t = {1, 5}
#     assert sum(t | s) == 8.5
#     assert sum(t - s) == 5


# int->float, variable: copy
def test_binop_int_float_var_set_method():
    s = {1.0, 2.5}
    t = {1, 5}
    assert sum(s.union(t)) == 8.5
    assert sum(s.intersection(t)) == 1
    assert sum(s.difference(t)) == 2.5
    assert sum(s.symmetric_difference(t)) == 7.5


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<__ss_int, __ss_int>*' to 'dict<__ss_int,
#     __ss_float>*'
#
# def test_binop_int_float_lit_dict():
#     d = {1: 1.5}
#     assert sum((d | {2: 3}).values()) == 4.5


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<__ss_int, __ss_float>*' to 'dict<__ss_int,
#     __ss_int>*'
#
# def test_binop_int_float_lit_dict_left():
#     d = {1: 1.5}
#     assert sum(({2: 3} | d).values()) == 4.5


# int->float, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<__ss_int, __ss_int>*' to 'dict<__ss_int,
#     __ss_float>*'
#
# def test_binop_int_float_var_dict():
#     d = {1: 1.5}
#     e = {2: 3}
#     assert sum((d | e).values()) == 4.5


# int->float, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<__ss_int, __ss_float>*' to 'dict<__ss_int,
#     __ss_int>*'
#
# def test_binop_int_float_var_dict_left():
#     d = {1: 1.5}
#     e = {2: 3}
#     assert sum((e | d).values()) == 4.5


# int->float, literal: copy
def test_binop_int_float_lit_augassign_list():
    l = [1.5]
    l += [1]
    l += (2, 3)
    assert sum(l) == 7.5


# int->float, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<__ss_float>*'
#
# def test_binop_int_float_lit_augassign_set():
#     s = {1.5, 2.0}
#     s |= {1}
#     s -= {2}
#     s ^= {4}
#     s &= {1, 4, 1.5}
#     assert sum(s) == 6.5


# int->float, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_binop_int_float_lit_augassign_tuple():
#     t = (1.5,)
#     t += (1,)
#     assert sum(t) == 2.5


# none, literal: cast
def test_binop_none():
    l = ['a'] + [None]
    assert l[1] is None
    m = [None] + ['a']
    assert m[0] is None
    strs = ['a']
    nones = [None]
    n = strs + nones
    assert n[1] is None


# sub->base, new: cast
def test_binop_sub_new():
    l = [A()] + [B()]
    assert [x.name() for x in l] == ['A', 'B']
    m = [B()] + [A()]
    assert [x.name() for x in m] == ['B', 'A']
    t = (A(),) + (B(),)
    assert t[1].name() == 'B'


# sub->base, variable: cast
def test_binop_sub_var():
    la = [A()]
    lb = [B()]
    assert [x.name() for x in la + lb] == ['A', 'B']
    assert [x.name() for x in lb + la] == ['B', 'A']


# sub->base, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<B*>*' to 'set<A*>*'
#
# def test_binop_sub_var_set():
#     sa = {A()}
#     sb = {B()}
#     assert sorted(x.name() for x in sa | sb) == ['A', 'B']
#     assert len(sa & sb) == 0


# sub->base, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<A*>*' to 'set<B*>*'
#
# def test_binop_sub_var_set_left():
#     sa = {A()}
#     sb = {B()}
#     assert sorted(x.name() for x in sb | sa) == ['A', 'B']
#     assert len(sb - sa) == 1


# empty, literal: build
def test_binop_empty_lit_list():
    assert [] + [1] == [1]
    assert [] + [1, 2] == [1, 2]


# empty, literal: build
def test_binop_empty_lit_list_right():
    assert sum([1] + []) == 1
    assert sum([1, 2] + []) == 3
    l = [1.5]
    assert sum(l + []) == 1.5
    assert sum([] + l) == 1.5
    names = ['a']
    assert len(names + []) == 1 and len([] + names) == 1


# empty, literal: build
def test_binop_empty_lit_tuple():
    t = (1, 2)
    assert sum(t + ()) == 3
    assert sum(() + t) == 3
    assert sum(() + (1,)) == 1


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<__ss_int, __ss_int>*' to 'dict<void*,
#     void*>*'
#
# def test_binop_empty_lit_dict():
#     assert len({} | {1: 2}) == 1


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<void*, void*>*' to 'dict<__ss_int,
#     __ss_int>*'
#
# def test_binop_empty_lit_dict_right():
#     assert len({1: 2} | {}) == 1
#     d = {1: 'a'}
#     assert len(d | {}) == 1


# empty, new: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<void*>*'
#
# def test_binop_empty_new_set():
#     assert len(set() | {1}) == 1


# empty, new: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<__ss_int>*'
#
# def test_binop_empty_new_set_right():
#     assert len({1} | set()) == 1


# empty, new: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<__ss_int>*'
#
# def test_binop_empty_new_set_var():
#     s = {1, 2}
#     assert sum(s | set()) == 3
#     assert sum(s - set()) == 3
#     assert len(s & set()) == 0
#     assert sum(s ^ set()) == 3
#     strs = {'a'}
#     assert len(strs | set()) == 1


# empty, new: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<void*>*'
#
# def test_binop_empty_new_set_var_left():
#     s = {1, 2}
#     assert sum(set() | s) == 3
#     assert len(set() - s) == 0
#     strs = {'a'}
#     assert len(set() | strs) == 1


# empty, new: build
def test_binop_empty_new_counter():
    assert Counter() + Counter('ab') == Counter('ab')


# empty, literal: build
def test_binop_empty_lit_mul():
    l = [] * 3
    l.append(1)
    assert sum(l) == 1
    ll = [[]] * 2
    ll[0].append(2)
    assert sum(ll[1]) == 2
    t = () * 2
    assert len(t) == 0


# empty, variable: copy
def test_binop_empty_var_list():
    e = []
    names = ['a']
    assert len(e + names) == 1
    assert len(names + e) == 1
    assert len(e + e) == 0


# empty, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*'
#
# def test_binop_empty_var_list_number():
#     e = []
#     l = [1, 2]
#     assert sum(l + e) == 3


# empty, variable: copy
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'list<__ss_int>*' to 'list<void*>*'
#
# def test_binop_empty_var_list_number_left():
#     e = []
#     l = [1, 2]
#     assert sum(e + l) == 3


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<str*>*'
#
# def test_binop_empty_var_set():
#     es = set()
#     strs = {'a'}
#     assert len(strs | es) == 1
#     assert len(strs & es) == 0
#     assert len(strs - es) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<str*>*' to 'set<void*>*'
#
# def test_binop_empty_var_set_left():
#     es = set()
#     strs = {'a'}
#     assert len(es | strs) == 1
#     assert len(es - strs) == 0


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<void*>*' to 'set<__ss_int>*'
#
# def test_binop_empty_var_set_number():
#     es = set()
#     s = {1, 2}
#     assert sum(s | es) == 3
#     assert sum(s - es) == 3


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'set<__ss_int>*' to 'set<void*>*'
#
# def test_binop_empty_var_set_number_left():
#     es = set()
#     s = {1, 2}
#     assert sum(es | s) == 3
#     assert len(es - s) == 0


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<void*, void*>*' to 'dict<str*, str*>*'
#
# def test_binop_empty_var_dict():
#     ed = {}
#     d = {'a': 'b'}
#     assert len(d | ed) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'dict<str*, str*>*' to 'dict<void*, void*>*'
#
# def test_binop_empty_var_dict_left():
#     ed = {}
#     d = {'a': 'b'}
#     assert len(ed | d) == 1


# empty, variable: infer
def test_binop_empty_accumulate_list():
    # an empty container that is rebound to the result of an operator
    l = []
    for i in range(3):
        l = l + [i]
    assert sum(l) == 3
    m = []
    for i in range(3):
        m = [i] + m
    assert sum(m) == 3
    n = []
    for i in range(3):
        n += [i]
    assert sum(n) == 3
    t = ()
    for i in range(3):
        t = t + (i,)
    assert sum(t) == 3


# empty, variable: infer
def test_binop_empty_accumulate_set():
    s = set()
    for i in range(3):
        s = s | {i}
    assert sorted(s) == [0, 1, 2]
    t = set()
    for i in range(3):
        t = t ^ {i, i + 1}
    assert sorted(t) == [0, 3]
    u = set()
    for i in range(3):
        u = u.union([i])
    assert sorted(u) == [0, 1, 2]
    w = set()
    for c in 'abc':
        w = {c} | w
    assert sorted(w) == ['a', 'b', 'c']
    y = set()
    for i in range(3):
        y = y.symmetric_difference([i, i + 1])
    assert sorted(y) == [0, 3]
    z = set()
    for i in range(3):
        z |= {i}
    assert sorted(z) == [0, 1, 2]


# empty, variable: infer
def test_binop_empty_accumulate_dict():
    h = {}
    for i in range(3):
        h = h | {i: str(i)}
    assert h == {0: '0', 1: '1', 2: '2'}
    j = {}
    for i in range(3):
        j = {str(i): i} | j
    assert j == {'0': 0, '1': 1, '2': 2}
    k = {}
    for i in range(3):
        k |= {i: i}
    assert sum(k.values()) == 3


# empty, variable: infer
def test_binop_empty_accumulate_frozenset():
    a = frozenset()
    for i in range(3):
        a = frozenset([i]) | a
    assert sorted(a) == [0, 1, 2]
    b = frozenset()
    assert len(b) == 0
    if len(a) == 3:
        b = frozenset(['x', 'y'])
    assert sorted(b) == ['x', 'y']
    c = frozenset()
    for i in range(3):
        c = c.union([i])
    assert sorted(c) == [0, 1, 2]
    d = frozenset()
    for ch in 'abc':
        d |= frozenset([ch])
    assert sorted(d) == ['a', 'b', 'c']
    e = frozenset()
    for i in range(3):
        e = e | frozenset([i])
    assert sorted(e) == [0, 1, 2]


# empty, variable: infer
def test_binop_empty_accumulate_counter():
    c = Counter()
    for word in ['ab', 'bc']:
        c = c + Counter(word)
    assert c['b'] == 2 and c['a'] == 1
    d = Counter()
    for word in ['ab', 'bc']:
        d += Counter(word)
    assert d['b'] == 2


#=========================================================================
# 9. COMPARE: the two sides of a comparison
#
# comparing only reads both sides, so nothing has to be converted as long
# as the elements can be compared with each other
#=========================================================================


# int->float, variable: implicit
def test_compare_int_float_scalar():
    i = 2
    x = 2.0
    b = True
    assert i == x and not i != x
    assert i < 2.5 and x >= i
    assert 1 == 1.0
    assert b == 1 and b == 1.0 and b < 2


# none->scalar, literal: warn
# TODO should give a warning, but today: wrong result, without a warning
#   at run-time: AssertionError
#
# def test_compare_none_scalar():
#     i = 0
#     assert i is not None
#     assert i != None


# int->float, literal: build
def test_compare_int_float_lit_list():
    l = [1.5]
    assert l != [1] and not l == [1]
    assert [1] < l and l > [1]
    assert [1, 2] == [1.0, 2.0]
    assert [[1]] != [[1.5]]


# int->float, literal: build
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__eq(set<__ss_float>*&,
#     set<__ss_int>*)'
#
# def test_compare_int_float_lit_set():
#     s = {1.0, 2.0}
#     assert s == {1, 2} and {1} < s and s >= {1}
#     assert {1, 2} == {1.0, 2.0}


# int->float, literal: build
def test_compare_int_float_lit_dict():
    d = {1: 1.5}
    assert d != {1: 1}
    assert {1: 2} == {1.0: 2.0}


# int->float, literal: build
def test_compare_int_float_lit_tuple():
    t = (1.5, 2.5)
    assert t != (1, 2) and (1, 2) < t
    assert (1, 2) == (1.0, 2.0)
    u = (1.5, 'a')
    assert u != (1, 'a') and (1, 'a') < u


# int->float, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__eq(list<__ss_int>*&,
#     list<__ss_float>*&)'
#
# def test_compare_int_float_var_list():
#     ints = [1, 2]
#     floats = [1.0, 2.0]
#     assert ints == floats and not ints != floats
#     assert floats == ints
#     assert not ints < floats and ints <= floats


# int->float, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__eq(set<__ss_int>*&,
#     set<__ss_float>*&)'
#
# def test_compare_int_float_var_set():
#     si = {1, 2}
#     sf = {1.0, 2.0}
#     assert si == sf and sf == si and si <= sf


# int->float, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__eq(tuple<__ss_int>*&,
#     tuple<__ss_float>*&)'
#
# def test_compare_int_float_var_tuple():
#     ti = (1, 2)
#     tf = (1.0, 2.0)
#     assert ti == tf and tf == ti


# int->float, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__eq(dict<__ss_int,
#     __ss_int>*&, dict<__ss_int, __ss_float>*&)'
#
# def test_compare_int_float_var_dict():
#     di = {1: 2}
#     df = {1: 2.0}
#     assert di == df and df == di


# none, literal: cast
def test_compare_none():
    s = 'a'
    assert s != None and not s == None and s is not None
    l = [1]
    assert l != None and l is not None
    o = A()
    assert o is not None and o != None
    assert ['a'] != [None]
    assert [None] == [None]
    names = ['a', None]
    assert names == ['a', None]


# sub->base, variable: cast
def test_compare_sub():
    a = A()
    b = B()
    assert a != b and not a == b
    assert a is not b
    o = A()
    o = b
    assert o == b and o is b and b is o
    la = [a, b]
    lb = [b]
    assert la != lb
    assert la[1:] == lb and lb == la[1:]
    assert [b] == lb


# empty, literal: build
def test_compare_empty_lit_list():
    l = [1]
    assert l != [] and not l == []
    assert [] != l and [] < l and l > []
    assert [] == []
    names = ['a']
    assert names != [] and [] != names
    ll = [[1]]
    assert ll != [[]] and ll != []


# empty, new: build
def test_compare_empty_new():
    s = {1}
    assert s != set() and set() != s and set() < s
    assert set() == set()
    d = {1: 2}
    assert d != {} and {} != d
    assert {} == {}
    t = (1, 2)
    assert t != () and () != t and () < t
    assert () == ()


# empty, variable: generic
def test_compare_empty_var():
    e = []
    names = ['a']
    assert e != names and names != e
    assert e == [] and [] == e
    assert e < names
    assert not e


# empty, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__ne(list<void*>*&,
#     list<__ss_int>*&)'
#
# def test_compare_empty_var_number():
#     e = []
#     l = [1]
#     assert e != l and l != e
#     assert e < l


# empty, variable: generic
def test_compare_empty_var_set():
    es = set()
    strs = {'a'}
    assert es != strs and strs != es
    assert not es


# empty, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__ne(set<void*>*&,
#     set<__ss_int>*&)'
#
# def test_compare_empty_var_set_number():
#     es = set()
#     s = {1}
#     assert es != s and s != es


# empty, variable: generic
def test_compare_empty_var_dict():
    ed = {}
    d = {'a': 'b'}
    assert ed != d and d != ed
    assert not ed


# empty, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: no matching function for call to '__ne(dict<void*, void*>*&,
#     dict<__ss_int, __ss_int>*&)'
#
# def test_compare_empty_var_dict_number():
#     ed = {}
#     d = {1: 2}
#     assert ed != d and d != ed


# empty, call: generic
def compare_empty_evens(xs):
    return [x for x in xs if x % 2 == 0]

def test_compare_empty_call():
    assert compare_empty_evens([1, 2]) == [2]
    assert compare_empty_evens([1]) == []
    assert compare_empty_evens([]) == []
    assert not compare_empty_evens([])


#=========================================================================
# 10. LOOKUP: looking up a value in a builtin container
#
# the value is compared with the elements (or keys). for sets and dicts
# it is hashed as well, and a value must hash like the element it equals
#=========================================================================


# bool->int, literal: implicit
def test_lookup_bool_int():
    l = [1, 2, 1]
    assert True in l and False not in l
    assert l.count(True) == 2
    assert l.index(True) == 0
    d = {1: 'a'}
    assert d[True] == 'a'


# int->float, literal: implicit
def test_lookup_int_float_scalar():
    l = [1.0, 2.0, 2.5]
    assert 2 in l and 3 not in l
    assert l.count(2) == 1
    assert l.index(2) == 1
    l.remove(1)
    assert sum(l) == 4.5
    t = (1.0, 2.5)
    assert 1 in t and t.count(1) == 1 and t.index(1) == 0
    s = {2.0, 2.5}
    assert 2 in s
    s.discard(2)
    s.remove(2.5)
    assert len(s) == 0
    d = {1.5: 'a', 2.0: 'b'}
    assert d[2] == 'b'
    assert d.get(2) == 'b'
    assert 2 in d
    assert d.pop(2) == 'b'
    assert len(d) == 1
    q = deque([1.0, 2.5])
    assert 1 in q and q.count(1) == 1
    c = Counter([1.0, 2.5])
    assert 1 in c and c[1] == 1


# int->float, variable: implicit
def test_lookup_int_float_var_scalar():
    i = 2
    l = [1.0, 2.0, 2.5]
    assert i in l and l.count(i) == 1 and l.index(i) == 1
    d = {1.5: 'a', 2.0: 'b'}
    assert d[i] == 'b' and i in d and d.get(i) == 'b'
    s = {2.0, 2.5}
    assert i in s


# float->int, variable: warn
# -> warning, then wrong result (see tests/errs/103.py)
#   looking up a float among ints: it is truncated, so 2.5 finds 2
#   at run-time: AssertionError
#
# def test_lookup_float_int():
#     x = 2.5
#     l = [1, 2, 3]
#     assert x not in l
#     assert l.count(x) == 0
#     t = (1, 2, 3)
#     assert x not in t
#     d = {1: 'a', 2: 'b'}
#     assert x not in d
#     assert d.get(x) is None


# none->scalar, literal: warn
# -> warning, then wrong result (see tests/errs/103.py)
#   looking up None among numbers: it is treated as 0
#   at run-time: AssertionError
#
# def test_lookup_none_scalar():
#     l = [0, 1]
#     assert None not in l
#     assert l.count(None) == 0


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_lookup_int_float_lit_tuple_set():
#     visited = {(1.0, 2.0)}
#     assert (1, 2) in visited
#     assert (2, 1) not in visited


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_lookup_int_float_lit_tuple_list():
#     l = [(0.0, 0.0), (1.0, 2.0)]
#     assert (1, 2) in l
#     assert l.index((1, 2)) == 1
#     assert l.count((1, 2)) == 1
#     l.remove((0, 0))
#     assert len(l) == 1


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*'
#
# def test_lookup_int_float_lit_list_list():
#     lists = [[1.5], [2.0]]
#     assert [2] in lists
#     assert lists.index([2]) == 1


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_lookup_int_float_lit_tuple_dict():
#     d = {(1.0, 2.0): 'a'}
#     assert d[(1, 2)] == 'a'
#     assert (1, 2) in d


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'dict<tuple2<__ss_float,
#     __ss_float>*, str*>::pop(tuple<__ss_int>*)'
#
# def test_lookup_int_float_lit_tuple_dict_method():
#     d = {(1.0, 2.0): 'a', (3.0, 4.0): 'b'}
#     assert d.get((3, 4)) == 'b'
#     assert d.get((5, 6)) is None
#     assert d.pop((1, 2)) == 'a'
#     del d[(3, 4)]
#     assert len(d) == 0


# int->float, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_lookup_int_float_var_tuple_set():
#     k = (1, 2)
#     visited = {(1.0, 2.0)}
#     assert k in visited


# int->float, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_lookup_int_float_var_tuple_dict():
#     k = (1, 2)
#     d = {(1.0, 2.0): 'a'}
#     assert d[k] == 'a' and k in d


# int->float, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'tuple<__ss_int>*' to 'tuple2<__ss_float,
#     __ss_float>*'
#
# def test_lookup_int_float_var_tuple_list():
#     k = (1, 2)
#     l = [(0.0, 0.0), (1.0, 2.0)]
#     assert k in l and l.index(k) == 1


# none, literal: cast
def test_lookup_none():
    l = ['a', None]
    assert None in l
    assert None not in ['a']
    assert l.count(None) == 1
    assert l.index(None) == 1


# none, literal: cast
# TODO doesn't work today: wrong result, without a warning
#   at run-time: ValueError: list.remove(x): x not in list
#
# def test_lookup_none_remove():
#     l = ['a', None]
#     l.remove(None)
#     assert len(l) == 1


# none, literal: cast
def test_lookup_none_list():
    ll = [[1], None]
    assert None in ll
    assert ll.index(None) == 1


# sub->base, variable: cast
class LookupNode:
    def __init__(self, n):
        self.n = n

class LookupLeaf(LookupNode):
    pass

class LookupInner(LookupNode):
    pass

def test_lookup_sub():
    leaves = [LookupLeaf(1), LookupLeaf(2)]
    tl = (leaves[0], leaves[1])
    seen = set(leaves)
    names = {leaves[0]: 'first', leaves[1]: 'second'}
    nodes = [leaves[1], LookupInner(7), leaves[0]]
    hits = []
    for x in nodes:
        hit = x in leaves
        hits.append(hit)
        assert (x in tl) == hit
        assert (x in seen) == hit
        assert (x in names) == hit
        assert (x not in leaves) == (not hit)
        assert (x not in seen) == (not hit)
        assert leaves.count(x) == int(hit)
    assert hits == [True, False, True]


# sub->base, variable: cast
def test_lookup_sub_base_container():
    b = B()
    la = [A(), b]
    assert b in la and la.index(b) == 1 and la.count(b) == 1
    sa = {A(), b}
    assert b in sa
    da = {b: 1}
    da[A()] = 2
    assert da[b] == 1 and b in da
    la.remove(b)
    assert len(la) == 1


# empty, literal: generic
def test_lookup_empty_container_lit():
    # looking up in a container that is empty
    assert 'a' not in []
    assert [].count('a') == 0
    assert 'a' not in {}
    assert 'a' not in ()


# empty, literal: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def test_lookup_empty_container_lit_number():
#     assert 1 not in []
#     assert [].count(1) == 0
#     assert 1 not in {}
#     assert 1 not in ()


# empty, new: generic
def test_lookup_empty_container_new():
    assert 'a' not in set()
    assert 'a' not in dict()
    assert 'a' not in list()
    assert 'a' not in deque()
    assert Counter()['a'] == 0


# empty, new: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def test_lookup_empty_container_new_number():
#     assert 1 not in set()
#     assert 1 not in dict()
#     assert 1 not in list()
#     assert 1 not in deque()
#     assert Counter()[1] == 0


# empty, variable: generic
def test_lookup_empty_container_var():
    e = []
    assert 'a' not in e
    assert e.count('a') == 0
    es = set()
    assert 'a' not in es
    ed = {}
    assert 'a' not in ed
    assert ed.get('a') is None


# empty, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def test_lookup_empty_container_var_number():
#     e = []
#     assert 1 not in e
#     assert e.count(1) == 0


# empty, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def test_lookup_empty_container_var_number_set_dict():
#     es = set()
#     assert 1 not in es
#     ed = {}
#     assert 1 not in ed


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*'
#
# def test_lookup_empty_value_lit():
#     # looking up an empty container
#     ll = [[1], []]
#     assert [] in ll
#     names = [['a']]
#     assert [] not in names


# empty, literal: build
def test_lookup_empty_value_lit_method():
    ll = [[1], []]
    assert ll.index([]) == 1
    assert ll.count([]) == 1
    ll.remove([])
    assert len(ll) == 1


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<void*>*' to 'tuple2<str*, str*>*'
#
# def test_lookup_empty_value_lit_tuple():
#     visited = {('a', 'b'), ()}
#     assert () in visited
#     d = {(): 'a', ('a', 'b'): 'b'}
#     assert d[()] == 'a'
#     assert () in d


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'tuple<void*>*' to 'tuple2<__ss_int, __ss_int>*'
#
# def test_lookup_empty_value_lit_tuple_number():
#     visited = {(1, 2), ()}
#     assert () in visited
#     d = {(): 'a', (1, 2): 'b'}
#     assert d[()] == 'a'
#     assert () in d


# empty, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<str*>*'
#
# def test_lookup_empty_value_var():
#     e = []
#     names = [['a']]
#     assert e not in names
#     assert names.count(e) == 0


# empty, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<B*>*'
#
# def test_lookup_empty_value_var_sub():
#     e = []
#     g = [[B()]]
#     assert e not in g


# empty, variable: generic
# TODO doesn't work today: warning, then C++ compile error
#   incompatible types
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*'
#
# def test_lookup_empty_value_var_number():
#     e = []
#     ll = [[1]]
#     assert e not in ll
#     assert ll.count(e) == 0


#=========================================================================
# 11. CTOR: the argument of a builtin container constructor
#
# a constructor copies the elements, so it can convert them on the way.
# what is constructed gets the element type of what is added later
#=========================================================================


# int->float, literal: copy
def test_ctor_int_float_lit():
    l = list((1, 2))
    l.append(0.5)
    assert sum(l) == 3.5
    s = set([1, 2])
    s.add(0.5)
    assert sum(s) == 3.5
    d = dict({1: 2})
    d[2] = 0.5
    assert sum(d.values()) == 2.5
    e = dict({1: 2})
    e[0.5] = 3
    assert sum(e) == 1.5
    t = tuple([1, 2])
    t = (0.5, 1.5)
    assert sum(t) == 2
    f = frozenset([1, 2])
    f = frozenset([0.5])
    assert sum(f) == 0.5


# int->float, literal: copy
def test_ctor_int_float_lit_collections():
    q = deque([1, 2])
    q.append(0.5)
    assert sum(q) == 3.5
    q2 = deque((1, 2), 5)
    q2.append(0.5)
    assert sum(q2) == 3.5 and q2.maxlen == 5
    q3 = deque(range(3), maxlen=2)
    q3.appendleft(0.5)
    assert sum(q3) == 1.5
    c = Counter([1, 2, 2])
    c[0.5] += 1
    assert sum(c) == 3.5 and c[2] == 2
    c2 = Counter({1: 2})
    c2[0.5] += 1
    assert sum(c2) == 1.5 and c2[1] == 2
    dd = defaultdict(float, {1: 2})
    dd[2] += 0.5
    assert sum(dd.values()) == 2.5


# int->float, variable: copy
def test_ctor_int_float_var_list():
    ints = [1, 2]
    l = list(ints)
    l.append(0.5)
    assert sum(l) == 3.5 and sum(ints) == 3


# int->float, variable: copy
def test_ctor_int_float_var_set():
    ints = [1, 2]
    s = set(ints)
    s.add(0.5)
    assert sum(s) == 3.5
    f = frozenset(ints)
    f = frozenset([0.5])
    assert sum(f) == 0.5


# int->float, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in
#     assignment
#
# def test_ctor_int_float_var_sorted():
#     ints = [1, 2]
#     r = sorted(ints)
#     r.append(0.5)
#     assert sum(r) == 3.5


# int->float, variable: copy
def test_ctor_int_float_var_dict():
    intdict = {1: 2}
    d = dict(intdict)
    d[2] = 0.5
    assert sum(d.values()) == 2.5 and sum(intdict.values()) == 2


# int->float, variable: copy
def test_ctor_int_float_var_tuple():
    ints = [1, 2]
    t = tuple(ints)
    t = (0.5, 1.5)
    assert sum(t) == 2


# int->float, variable: copy
def test_ctor_int_float_var_collections():
    ints = [1, 2]
    q = deque(ints)
    q.append(0.5)
    assert sum(q) == 3.5 and sum(ints) == 3
    q2 = deque(q)
    assert sum(q2) == 3.5
    intq = deque([1, 2])
    q3 = deque(intq)
    q3.append(0.5)
    assert sum(q3) == 3.5 and sum(intq) == 3
    c = Counter(ints)
    c[0.5] += 1
    assert sum(c) == 3.5
    intdict = {1: 2}
    c2 = Counter(intdict)
    c2[0.5] += 1
    assert sum(c2) == 1.5
    c3 = Counter([0.5])
    c3.update(ints)
    c3.update(intdict)
    c3.subtract(intdict)
    assert sum(c3) == 3.5 and c3[1] == 1
    dd = defaultdict(float, intdict)
    dd[2] += 0.5
    assert sum(dd.values()) == 2.5


# none, literal: copy
def test_ctor_none():
    l = list(['a'])
    l.append(None)
    assert l[1] is None
    q = deque(['a'])
    q.append(None)
    assert q[1] is None


# sub->base, variable: copy
def test_ctor_sub():
    lb = [B()]
    la = list(lb)
    la.append(A())
    assert [x.name() for x in la] == ['B', 'A']
    assert [x.name() for x in lb] == ['B']
    sa = set(lb)
    sa.add(A())
    assert sorted(x.name() for x in sa) == ['A', 'B']
    qa = deque(lb)
    qa.append(A())
    assert [x.name() for x in qa] == ['B', 'A']
    ta = tuple(lb)
    ta = (A(), A())
    assert ta[0].name() == 'A'


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_ctor_empty_lit():
#     l = list([])
#     l.append(1)
#     assert sum(l) == 1
#     names = list(())
#     names.append('a')
#     assert names[0] == 'a'


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: expected primary-expression before ',' token
#
# def test_ctor_empty_lit_set():
#     s = set([])
#     s.add(1)
#     assert sum(s) == 1
#     f = frozenset([])
#     assert len(f) == 0


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no match for 'operator[]' (operand types are '__GC_DICT<__ss_int,
#     __ss_int>' and
#
# def test_ctor_empty_lit_dict():
#     d = dict({})
#     d[1] = 2
#     assert sum(d.values()) == 2


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<__ss_int>*' in assignment
#
# def test_ctor_empty_lit_sorted():
#     r = sorted([])
#     r.append(1)
#     assert sum(r) == 1


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_ctor_empty_lit_tuple():
#     t = tuple([])
#     assert len(t) == 0
#     u = (1, 2)
#     u = tuple([])
#     assert len(u) == 0


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'pyseq<void*>::for_in_unit' to '__ss_int'
#
# def test_ctor_empty_lit_deque():
#     q = deque([])
#     q.append(1)
#     assert sum(q) == 1
#     q2 = deque([], 3)
#     q2.append('a')
#     assert q2[0] == 'a' and q2.maxlen == 3


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def test_ctor_empty_lit_counter():
#     c = Counter([])
#     c[1] += 1
#     assert c[1] == 1
#     c2 = Counter({})
#     c2['a'] += 1
#     assert c2['a'] == 1


# empty, literal: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to
#     '__collections__::defaultdict<__ss_int, void*>::defaultdict(__ss_int
#     (&)(), dict<void*, void*>*)'
#
# def test_ctor_empty_lit_defaultdict():
#     dd = defaultdict(int, {})
#     dd[1] += 2
#     assert dd[1] == 2


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_ctor_empty_var():
#     e = []
#     names = list(e)
#     names.append('a')
#     assert names[0] == 'a' and len(e) == 0


# empty, variable: copy
def test_ctor_empty_var_set():
    e = []
    strs = set(e)
    strs.add('a')
    assert len(strs) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'pyseq<void*>::for_in_unit' to 'str*'
#
# def test_ctor_empty_var_deque():
#     e = []
#     q = deque(e)
#     q.append('a')
#     assert q[0] == 'a'


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: 'void*' is not a pointer-to-object type
#
# def test_ctor_empty_var_sorted():
#     e = []
#     r = sorted(e)
#     assert len(r) == 0
#     t = tuple(e)
#     assert len(t) == 0


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_ctor_empty_var_number():
#     e = []
#     l = list(e)
#     l.append(1)
#     assert sum(l) == 1 and len(e) == 0


# empty, variable: copy
def test_ctor_empty_var_set_number():
    e = []
    s = set(e)
    s.add(1)
    assert sum(s) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'pyseq<void*>::for_in_unit' to '__ss_int'
#
# def test_ctor_empty_var_deque_number():
#     e = []
#     q = deque(e)
#     q.append(1)
#     assert sum(q) == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'void*'
#
# def test_ctor_empty_var_counter_number():
#     e = []
#     c = Counter(e)
#     c[1] += 1
#     assert c[1] == 1


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no match for 'operator[]' (operand types are '__GC_DICT<str*,
#     str*>' {aka 'boost::unordered::unordered_flat_map<str*, str*,
#     ss_hash<str*>, ss_eq<str*>, __ss_era
#
# def test_ctor_empty_var_dict():
#     ed = {}
#     d = dict(ed)
#     d['a'] = 'b'
#     assert d['a'] == 'b' and len(ed) == 0


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no match for 'operator[]' (operand types are '__GC_DICT<__ss_int,
#     __ss_int>' and
#
# def test_ctor_empty_var_dict_number():
#     ed = {}
#     n = dict(ed)
#     n[1] = 2
#     assert n[1] == 2


#=========================================================================
# 12. ITER: loop variables and unpacking
#
# the loop variable (or unpacking target) can be wider than the elements
#=========================================================================


# int->float, literal: implicit
def test_iter_int_float_lit_scalar():
    total = 0.0
    for x in [1, 2.5, 3]:
        total += x
    assert total == 6.5
    y = 0.5
    for y in [1, 2]:
        pass
    assert y + 0.5 == 2.5
    z = 0.5
    for z in range(3):
        pass
    assert z + 0.5 == 2.5
    assert [w + 0.5 for w in (1, 2.5)] == [1.5, 3.0]


# int->float, variable: implicit
def test_iter_int_float_var_scalar():
    ints = [1, 2]
    y = 0.5
    for y in ints:
        pass
    assert y + 0.5 == 2.5
    d = {1: 2}
    k, v = 0.5, 0.5
    for k, v in d.items():
        pass
    assert k + v + 0.5 == 3.5
    n, m = 0.5, 0.5
    for n, m in enumerate(ints):
        pass
    assert n + m + 0.5 == 3.5


# bool->int, literal: implicit
# TODO doesn't work today: warning, then C++ compile error
#   variable 'j' has dynamic (sub)type: {bool, int}
#   variable 'i' has dynamic (sub)type: {bool, int}
#   expression has dynamic (sub)type: {bool, int}
#   C++: invalid conversion from '__ss_int' to 'pyobj*'
#
# def test_iter_bool_int():
#     total = 0
#     for i in [1, True]:
#         total += i
#     assert total == 2
#     j = 5
#     for j in [True, False]:
#         pass
#     assert j + 1 == 1


# int->float, literal: build
def test_iter_int_float_lit_list():
    l = [1.5]
    for l in [[1], [2, 3]]:
        pass
    l.append(0.5)
    assert sum(l) == 5.5


# int->float, variable: warn
# TODO should give a warning, but today: C++ compile error, without a warning
#   C++: cannot convert 'list<__ss_int>*' to 'list<__ss_float>*' in
#     assignment
#
# def test_iter_int_float_var_list():
#     ll = [[1], [2, 3]]
#     l = [1.5]
#     for l in ll:
#         pass
#     assert sum(l) == 5


# int->float, literal: build
def test_unpack_int_float_lit():
    a, b = 1.5, 'x'
    a, b = 1, 'y'
    assert a + 0.5 == 1.5 and b == 'y'
    l, n = [1.5], 0
    l, n = [1, 2], 1
    l.append(0.5)
    assert sum(l) == 3.5 and n == 1
    [p, q] = [1.5, 2.5]
    [p, q] = [1, 2]
    assert p + q + 0.5 == 3.5


# int->float, variable: build
def test_unpack_int_float_var():
    # both variables hold both lists, so the int literal is built wider
    p = [1.5]
    q = [1]
    p, q = q, p
    assert sum(p) == 1 and sum(q) == 1.5


# none, literal: cast
def test_iter_none():
    result = []
    for s in [None, 'a']:
        result.append(s)
    assert result[0] is None and result[1] == 'a'
    lens = []
    for l in [[1], None, [2, 3]]:
        lens.append(len(l) if l is not None else -1)
    assert lens == [1, -1, 2]
    t, u = 'a', [1]
    t, u = None, None
    assert t is None and u is None


# sub->base, new: cast
def test_iter_sub_new():
    names = []
    for x in [A(), B()]:
        names.append(x.name())
    assert names == ['A', 'B']
    names2 = []
    for y in [B(), None, A()]:
        names2.append(y.name() if y else '-')
    assert names2 == ['B', '-', 'A']
    o, p = A(), A()
    o, p = B(), B()
    assert o.name() + p.name() == 'BB'


# sub->base, variable: cast
def test_iter_sub_var():
    lb = [B()]
    o = A()
    names = [o.name()]
    for o in lb:
        names.append(o.name())
    assert names == ['A', 'B']


# sub->base, variable: cast
def test_unpack_sub_var():
    b = B()
    p, n = A(), 0
    p, n = b, 1
    assert p.name() == 'B' and n == 1


# sub->base, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<B*>*' to 'list<A*>*' in assignment
#
# def test_unpack_sub_var_list():
#     lb = [B()]
#     q, n = [A()], 0
#     q, n = lb, 1
#     assert q[0].name() == 'B' and n == 1


# sub->base, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<B*>*' to 'list<A*>*' in assignment
#
# def test_iter_sub_var_list():
#     llb = [[B()]]
#     la = [A()]
#     for la in llb:
#         pass
#     assert la[0].name() == 'B'


# empty, literal: infer
# TODO works, but gives a warning
#   variable 'z' has no type
#   variable 'k' has no type
def test_iter_empty_lit():
    n = 0
    for x in []:
        n += 1
    for y in ():
        n += 1
    assert n == 0
    assert len([z for z in []]) == 0
    assert len({k: k for k in []}) == 0
    assert sum(1 for w in []) == 0


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'void*' to 'str*'
#
# def test_iter_empty_lit_typed():
#     # the loop variable has a type already
#     s = 'a'
#     for s in []:
#         pass
#     assert s == 'a'
#     l = ['a']
#     for l in []:
#         pass
#     assert len(l) == 1


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'void*' to '__ss_int'
#
# def test_iter_empty_lit_typed_number():
#     x = 1
#     for x in []:
#         pass
#     assert x == 1


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: 'void*' is not a pointer-to-object type
#
# def test_iter_empty_lit_typed_unpack():
#     a, b = 1, 'x'
#     for a, b in []:
#         pass
#     assert a == 1 and b == 'x'


# empty, literal: build
def test_iter_empty_lit_list():
    l = [1]
    for l in [[], [2]]:
        pass
    l.append(3)
    assert sum(l) == 5
    m = [1]
    for m in [[2], []]:
        pass
    m.append(3)
    assert sum(m) == 3
    total = 0
    for n in [[1], [], [2, 3]]:
        total += len(n)
    assert total == 3


# empty, new: infer
def test_iter_empty_new():
    n = 0
    for x in set():
        n += 1
    for y in dict():
        n += 1
    for k, v in {}.items():
        n += 1
    for z in list():
        n += 1
    for i, w in enumerate([]):
        n += 1
    assert n == 0


# empty, variable: infer
# TODO works, but gives a warning
#   variable 'y' has no type
def test_iter_empty_var():
    e = []
    n = 0
    for x in e:
        n += 1
    assert n == 0
    assert len([y for y in e]) == 0


# empty, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from 'void*' to 'str*'
#
# def test_iter_empty_var_typed():
#     e = []
#     s = 'a'
#     for s in e:
#         pass
#     assert s == 'a'


# empty, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<str*>*' in assignment
#
# def test_iter_empty_var_typed_list():
#     e = []
#     l = ['a']
#     for l in [e]:
#         pass
#     assert len(l) == 0


# empty, variable: warn
# TODO should give a warning, but today: C++ compile error, without a warning
#   C++: invalid conversion from 'void*' to '__ss_int'
#
# def test_iter_empty_var_typed_number():
#     e = []
#     x = 1
#     for x in e:
#         pass
#     assert x == 1


# empty, literal: infer
def test_unpack_empty_lit():
    a, b = [], []
    a.append(1)
    b.append('x')
    assert sum(a) == 1 and b[0] == 'x'
    d, s = {}, set()
    d[1] = 2
    s.add('a')
    assert d[1] == 2 and 'a' in s


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<str*>*' in assignment
#
# def test_unpack_empty_lit_typed():
#     names, m = ['a'], 0
#     names, m = [], 1
#     assert len(names) == 0 and m == 1


# empty, literal: build
def test_unpack_empty_lit_typed_number():
    l, n = [1], 0
    l, n = [], 1
    l.append(2)
    assert sum(l) == 2 and n == 1


# empty, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: cannot convert 'list<void*>*' to 'list<str*>*' in assignment
#
# def test_unpack_empty_var():
#     e = []
#     names, n = ['a'], 0
#     names, n = e, 1
#     assert len(names) == 0 and n == 1


# empty, call: cast
# TODO works, but gives a warning
#   variable 'y' has no type
def iter_empty_copy(xs):
    return [x for x in xs]

def iter_empty_nest_list(xs):
    return [[x for x in xs]]

def test_iter_empty_call():
    assert iter_empty_copy([1, 2]) == [1, 2]
    assert iter_empty_nest_list([1]) == [[1]]
    n = 0
    for y in iter_empty_copy([]):
        n += 1
    assert n == 0
    assert len([y for y in iter_empty_copy([])]) == 0
    assert len({y for y in iter_empty_copy([])}) == 0
    assert sum(1 for y in iter_empty_copy([])) == 0
    for z in iter_empty_nest_list([])[0]:
        n += 1
    assert n == 0


#=========================================================================
# 13. CHOICE: conditional expressions, 'and' and 'or'
#
# both branches have to become the type of the whole expression
#=========================================================================


# int->float, literal: implicit
def test_choice_int_float_scalar():
    c = 3
    x = 1 if c > 2 else 2.5
    assert x + 0.5 == 1.5
    i = 2
    y = i if c > 2 else 2.5
    assert y + 0.5 == 2.5
    z = 0 or 2.5
    assert z == 2.5
    w = i and 2.5
    assert w == 2.5


# none->scalar, literal: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   variable 'i' has dynamic (sub)type: {None, int}
#   variable 'j' has dynamic (sub)type: {None, int}
#   expression has dynamic (sub)type: {None, int}
#   C++: invalid conversion from '__ss_int' to 'pyobj*'
#
# def test_choice_none_scalar():
#     c = 3
#     i = 0 if c > 2 else None
#     assert i is not None
#     j = 0 if c > 5 else None
#     assert j is None


# int->float, literal: build
def test_choice_int_float_lit_list():
    c = 3
    l = [1] if c > 2 else [2.5]
    l.append(0.5)
    assert sum(l) == 1.5
    m = [2.5] if c > 2 else [1]
    assert sum(m) == 2.5
    d = {1: 2} if c > 2 else {1: 2.5}
    d[2] = 0.5
    assert sum(d.values()) == 2.5
    n = [1] and [2.5]
    assert sum(n) == 2.5
    o = [1] or [2.5]
    o.append(0.5)
    assert sum(o) == 1.5


# int->float, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: conditional expression between distinct pointer types
#     'list<__ss_int>*' and 'list<__ss_float>*' lacks a cast
#
# def test_choice_int_float_var_list():
#     c = 3
#     ints = [1]
#     floats = [2.5]
#     l = ints if c > 2 else floats
#     assert sum(l) == 1


# none, literal: cast
def test_choice_none():
    c = 3
    s = 'a' if c > 5 else None
    assert s is None
    l = [1] if c > 5 else None
    assert l is None
    t = None or 'a'
    assert t == 'a'
    names = ['a'] if c > 5 else [None]
    assert names[0] is None


# sub->base, new: cast
def test_choice_sub_new():
    c = 3
    o = A() if c > 5 else B()
    assert o.name() == 'B'
    l = [A()] if c > 5 else [B()]
    assert l[0].name() == 'B'
    p = A() and B()
    assert p.name() == 'B'


# sub->base, variable: cast
def test_choice_sub_var():
    c = 3
    a = A()
    b = B()
    o = a if c > 5 else b
    assert o.name() == 'B'
    la = [A()]
    lb = [B()]
    l = la if c > 5 else lb
    assert l[0].name() == 'B'
    m = lb if c > 5 else la
    assert m[0].name() == 'A'
    n = la and lb
    assert n[0].name() == 'B'


# empty, literal: build
def test_choice_empty_lit():
    c = 3
    l = [1] if c > 5 else []
    l.append(2)
    assert sum(l) == 2
    m = [] if c > 5 else [1]
    assert sum(m) == 1
    names = [] if c > 2 else ['a']
    assert len(names) == 0
    t = (1, 2) if c > 5 else ()
    assert len(t) == 0


# empty, new: build
def test_choice_empty_new():
    c = 3
    s = {1} if c > 5 else set()
    s.add(2)
    assert sum(s) == 2
    d = {} if c > 2 else {1: 2}
    d[3] = 4
    assert sum(d.values()) == 4
    q = deque([1]) if c > 5 else deque()
    q.append(2)
    assert sum(q) == 2


# empty, literal: build
def test_choice_empty_lit_boolop():
    l = [] or [1]
    assert sum(l) == 1
    m = [1] and []
    m.append(2)
    assert sum(m) == 2
    n = [1, 2]
    o = n or []
    assert sum(o) == 3
    names = ['a']
    p = names and []
    assert len(p) == 0


# empty, literal: build
def choice_empty_default(l=None):
    l = l or []
    l.append(1)
    return sum(l)

def choice_empty_default2(l=None):
    m = l if l is not None else []
    return len(m)

def test_choice_empty_lit_none():
    # the usual way to have an empty container as default argument
    assert choice_empty_default() == 1
    assert choice_empty_default([2]) == 3
    assert choice_empty_default2() == 0
    assert choice_empty_default2(['a']) == 1


# empty, variable: cast
def test_choice_empty_var():
    c = 3
    e = []
    names = ['a']
    l = e if c > 2 else names
    assert len(l) == 0
    m = names if c > 5 else e
    assert len(m) == 0
    n = e or names
    assert len(n) == 1


# empty, variable: warn
# -> warning, then C++ compile error (see tests/errs/103.py)
#   incompatible types
#   C++: conditional expression between distinct pointer types
#     'list<void*>*' and 'list<__ss_int>*' lacks a cast
#
# def test_choice_empty_var_number():
#     c = 3
#     e = []
#     ints = [1]
#     l = e if c > 2 else ints
#     assert len(l) == 0


#=========================================================================
# 14. LIB: arguments of builtin and library functions
#
# functions that take several values or iterables, which then have to
# agree with each other, or with the result
#=========================================================================


# int->float, literal: implicit
def test_lib_int_float_scalar():
    assert max(1, 2.5) == 2.5
    assert min(1, 2.5) + 0.5 == 1.5
    assert max(2.5, 1) == 2.5
    i = 3
    x = 2.5
    assert max(i, x) == 3 and min(i, x) == 2.5
    assert max(i, x, 4) == 4
    assert math.sqrt(4) == 2.0
    assert math.floor(2.5) + 0.5 == 2.5
    assert abs(-i) + 0.5 == 3.5
    assert divmod(7, 2.0) == (3.0, 1.0)
    assert round(2.5) == 2 and round(i) == 3
    assert float(i) == 3.0 and int(x) == 2
    assert '%.1f' % 1 == '1.0'
    assert '%d' % 2.5 == '2'


# int->float, literal: implicit
def test_lib_int_float_lit_iter():
    assert sum([1, 2], 0.5) == 3.5
    assert sum([0.5, 1.5], 1) == 3
    assert max([1, 2.5]) == 2.5
    assert sorted([3, 1.5, 2])[0] == 1.5
    assert list(zip([1], [0.5])) == [(1, 0.5)]
    assert list(map(lambda v: v + 0.5, [1, 2])) == [1.5, 2.5]
    assert functools.reduce(lambda a, b: a + b, [1, 2], 0.5) == 3.5
    assert sum(x for x in [1, 2.5]) == 3.5
    assert [x for x in enumerate([0.5])] == [(0, 0.5)]


# int->float, variable: implicit
def test_lib_int_float_var_iter():
    ints = [1, 2]
    floats = [0.5, 1.5]
    assert sum(ints, 0.5) == 3.5
    assert sum(floats, 1) == 3
    assert list(zip(ints, floats)) == [(1, 0.5), (2, 1.5)]
    assert max(ints, default=0) == 2
    assert min(max(ints), max(floats)) == 1.5


# int->float, variable: implicit
def lib_add2(a, b):
    return a + b

def test_lib_int_float_var_reduce():
    ints = [1, 2]
    assert functools.reduce(lib_add2, ints, 0.5) == 3.5


# int->float, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '___max(int, __ss_void_struct&,
#     __ss_int, list<__ss_int>*&, list<__ss_float>*&)'
#
# def test_lib_int_float_var_minmax():
#     ints = [1, 2]
#     floats = [0.5, 1.5]
#     assert max(ints, floats) == [1, 2]
#     assert min(ints, floats) == [0.5, 1.5]


# int->float, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '___max(int, __ss_void_struct&,
#     __ss_int, list<__ss_float>*, list<__ss_int>*)'
#
# def test_lib_int_float_lit_sorted():
#     floats = [0.5, 1.5]
#     assert sorted([floats, [1]])[1] == [1]
#     assert max([0.5], [1]) == [1]


# int->float, literal: error
# -> C++ compile error, without a warning
#   C++: static assertion failed: itertools.chain: mixing iterables of
#     different numeric types (such as int and float) is not supported
#
# def test_lib_int_float_chain():
#     assert sum(itertools.chain([1, 2], [0.5])) == 3.5


# int->float, literal: error
# -> C++ compile error, without a warning
#   C++: static assertion failed: heapq.merge: mixing iterables of
#     different numeric types (such as int and float) is not supported
#
# def test_lib_int_float_merge():
#     assert list(heapq.merge([1, 3], [0.5])) == [0.5, 1, 3]


# int->float, variable: error
# -> C++ compile error, without a warning
#   C++: static assertion failed: itertools.chain: mixing iterables of
#     different numeric types (such as int and float) is not supported
#
# def test_lib_int_float_chain_var():
#     ints = [1, 2]
#     floats = [0.5]
#     assert sum(itertools.chain(ints, floats)) == 3.5
#     assert list(heapq.merge(ints, floats)) == [0.5, 1, 2]


# int->float, literal: implicit
def test_lib_int_float_itertools():
    assert list(itertools.accumulate([1, 2.5])) == [1, 3.5]
    assert list(itertools.repeat(1, 2)) == [1, 1]
    assert list(itertools.product([1], [0.5])) == [(1, 0.5)]


# int->float, literal: implicit
def test_lib_int_float_heapq():
    assert heapq.nlargest(1, [1, 2.5]) == [2.5]
    assert heapq.nsmallest(1, [1, 2.5]) == [1]


# int->float, literal: implicit
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'heappush(list<__ss_float>*&,
#     __ss_int)'
#
# def test_lib_int_float_heappush():
#     h = [1.5, 2.5]
#     heapq.heappush(h, 1)
#     assert heapq.heappop(h) == 1


# none, literal: cast
def test_lib_none():
    assert list(zip(['a'], [None])) == [('a', None)]
    assert sorted(['b', 'a'], key=None) == ['a', 'b']


# none, literal: cast
def test_lib_none_reduce():
    assert functools.reduce(lambda a, b: a if a else b, ['', 'x'], None) == 'x'


# none, literal: cast
def test_lib_none_filter():
    assert list(filter(None, [0, 1, 2])) == [1, 2]


# none, literal: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: invalid conversion from '__ss_int' to 'pyseq<str*>::for_in_unit'
#
# def test_lib_none_default():
#     assert max(['a', 'b'], default=None) == 'b'


# sub->base, variable: cast
def test_lib_sub():
    la = [A()]
    lb = [B()]
    assert [x.name() for x in itertools.chain(la, lb)] == ['A', 'B']
    assert [(x.name(), y.name()) for x, y in zip(la, lb)] == [('A', 'B')]
    assert [x.name() for x in sorted(la + lb, key=lambda o: o.name())] == ['A', 'B']
    assert max(la + lb, key=lambda o: o.name()).name() == 'B'
    assert [x.name() for x in reversed(lb)] == ['B']


# empty, literal: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_lit():
#     assert len([]) == 0 and len({}) == 0 and len(()) == 0
#     assert not any([]) and all([])
#     assert ''.join([]) == ''
#     assert str([]) == '[]' and str({}) == '{}' and str(()) == '()'
#     assert repr(set()) == 'set()'


# empty, literal: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '__eq(__sumtype1<void*>::type,
#     __ss_int)'
#
# def test_lib_empty_lit_sum():
#     assert sum([]) == 0


# empty, literal: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: 'void*' is not a pointer-to-object type
#
# def test_lib_empty_lit_sorted():
#     assert len(sorted([])) == 0
#     assert len(list(reversed([]))) == 0
#     assert len(list(enumerate([]))) == 0


# empty, literal: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '__eq(pyseq<void*>::for_in_unit,
#     __ss_int)'
#
# def test_lib_empty_lit_default():
#     assert max([], default=0) == 0
#     assert min([], default=5) == 5


# empty, literal: build
def test_lib_empty_lit_mixed():
    # an empty container together with one that has elements
    assert len(list(zip([], [1]))) == 0
    assert len(list(zip([1], []))) == 0
    assert len(list(zip(['a'], []))) == 0


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '__eq(__sumtype2<void*,
#     __ss_int>::type, __ss_int)'
#
# def test_lib_empty_lit_mixed_sum():
#     assert sum([], 5) == 5
#     assert functools.reduce(lambda a, b: a + b, [], 5) == 5


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '___max(int, __ss_void_struct&,
#     __ss_int, list<__ss_int>*, list<void*>*)'
#
# def test_lib_empty_lit_mixed_max():
#     assert max([1], []) == [1]
#     assert min([1], []) == []
#     assert sorted([[1], []]) == [[], [1]]


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'reduce(list<__ss_int>*
#     (&)(list<__ss_int>*, list<__ss_int>*), list<list<__ss_int>*>*,
#     list<void*>*)'
#
# def test_lib_empty_lit_mixed_reduce():
#     assert functools.reduce(lambda a, b: a + b, [[1], []], []) == [1]


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_lit_chain():
#     assert list(itertools.chain(['a'], [])) == ['a']
#     assert list(itertools.chain([], ['a'])) == ['a']


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_lit_chain_number():
#     assert list(itertools.chain([], [1])) == [1]
#     assert list(itertools.chain([1], [])) == [1]


# empty, literal: infer
def test_lib_empty_lit_chain_only():
    assert len(list(itertools.chain([], []))) == 0


# empty, literal: build
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_lit_merge():
#     assert list(heapq.merge([], [1])) == [1]
#     assert list(heapq.merge([1], [])) == [1]


# empty, literal: build
def test_lib_empty_lit_product():
    assert len(list(itertools.product([1], []))) == 0
    assert len(list(itertools.product([], ['a']))) == 0


# empty, literal: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: call of overloaded 'accumulate(list<void*>*, void*, void*)' is
#     ambiguous
#
# def test_lib_empty_lit_accumulate():
#     assert len(list(itertools.accumulate([]))) == 0


# empty, literal: infer
def test_lib_empty_lit_heappush():
    h = []
    heapq.heappush(h, 1)
    heapq.heappush(h, 0)
    assert heapq.heappop(h) == 0


# empty, variable: infer
def test_lib_empty_var():
    e = []
    assert len(e) == 0
    assert not any(e) and all(e)
    assert str(e) == '[]'
    es = set()
    ed = {}
    assert len(es) == 0 and len(ed) == 0
    assert str(ed) == '{}'


# empty, variable: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '__eq(__sumtype1<void*>::type,
#     __ss_int)'
#
# def test_lib_empty_var_sum():
#     e = []
#     assert sum(e) == 0


# empty, variable: infer
# TODO doesn't work today: C++ compile error, without a warning
#   C++: 'void*' is not a pointer-to-object type
#
# def test_lib_empty_var_sorted():
#     e = []
#     assert len(sorted(e)) == 0
#     assert len(list(reversed(e))) == 0
#     assert len(list(enumerate(e))) == 0


# empty, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_var_mixed():
#     e = []
#     names = ['a']
#     assert len(list(zip(e, names))) == 0
#     assert ''.join(e) == ''


# empty, variable: cast
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_var_mixed_chain():
#     e = []
#     names = ['a']
#     assert list(itertools.chain(e, names)) == ['a']
#     assert list(itertools.chain(names, e)) == ['a']


# empty, variable: generic
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '___max(int, __ss_void_struct&,
#     __ss_int, list<str*>*&, list<void*>*&)'
#
# def test_lib_empty_var_mixed_max():
#     e = []
#     names = ['a']
#     assert max(names, e) == ['a']


# empty, variable: copy
def test_lib_empty_var_mixed_number():
    e = []
    l = [1]
    assert len(list(zip(e, l))) == 0


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to 'push_back(void*&)'
#
# def test_lib_empty_var_mixed_chain_number():
#     e = []
#     l = [1]
#     assert list(itertools.chain(e, l)) == [1]
#     assert list(itertools.chain(l, e)) == [1]


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: static assertion failed: heapq.merge: mixing iterables of
#     different numeric types (such as int and float) is not supported
#
# def test_lib_empty_var_mixed_merge_number():
#     e = []
#     l = [1]
#     assert list(heapq.merge(l, e)) == [1]


# empty, variable: copy
# TODO doesn't work today: C++ compile error, without a warning
#   C++: no matching function for call to '__eq(__sumtype2<void*,
#     __ss_int>::type, __ss_int)'
#
# def test_lib_empty_var_mixed_sum_number():
#     e = []
#     assert sum(e, 5) == 5


#=========================================================================
# 15. MIXED: collected tests that go through several contexts at once
#
# these are kept as they were found in other test sets
#=========================================================================


# empty, call: cast
def empty_split(xs):
    if not xs:
        return [], []
    return [x for x in xs if x > 1], [x for x in xs if x <= 1]

def empty_copy(xs):
    return [x for x in xs]

def empty_het_pair(xs):
    return [x for x in xs], 'a'

def empty_nest_list(xs):
    return [[x for x in xs]]

def empty_dict_of_list(xs):
    return {1: [x for x in xs]}

class EmptyHolder:
    def __init__(self):
        self.v = empty_copy([])
        self.p, self.q = empty_split([])

def empty_wrap_copy():
    return empty_copy([])

def test_empty_call_contexts():
    assert empty_split([3, 1, 2]) == ([3, 2], [1])
    assert empty_copy([1, 2]) == [1, 2]
    assert empty_het_pair([1]) == ([1], 'a')
    assert empty_nest_list([1]) == [[1]]
    assert empty_dict_of_list([1]) == {1: [1]}

    # nested unpacking, chained assignment
    (a, b), c = empty_split([]), 1
    assert len(a) == 0 and len(b) == 0 and c == 1
    d = e = empty_copy([])
    assert len(d) == 0 and len(e) == 0

    # item of the result
    x = empty_split([])[0]
    assert len(x) == 0
    x2 = empty_split([])[-1]
    assert len(x2) == 0
    h = empty_het_pair([])[0]
    assert len(h) == 0 and empty_het_pair([])[1] == 'a'
    m = empty_nest_list([])[0]
    assert len(m) == 0
    dl = empty_dict_of_list([])[1]
    assert len(dl) == 0
    p, q = empty_nest_list([])[0], 1
    assert len(p) == 0 and q == 1

    # attributes, containers, return, conditional
    o = EmptyHolder()
    assert len(o.v) == 0 and len(o.p) == 0 and len(o.q) == 0
    assert len(empty_wrap_copy()) == 0
    l = [empty_copy([])]
    assert len(l) == 1 and len(l[0]) == 0
    t = (empty_copy([]), 1)
    assert len(t[0]) == 0
    w = empty_copy([]) if len(l) == 1 else empty_copy([])
    assert len(w) == 0
    w2 = empty_copy([]) or empty_copy([])
    assert len(w2) == 0





def test_all():
    test_assign_int_float_lit_scalar()
    test_assign_int_float_var_scalar()
    test_assign_int_float_call_scalar()
    test_assign_none_lit()
    test_assign_sub_new()
    test_assign_sub_var()
    test_assign_sub_call()
    test_assign_sub_siblings()
    test_assign_int_float_lit_list()
    test_assign_int_float_lit_set()
    test_assign_int_float_lit_dict()
    test_assign_int_float_lit_tuple()
    test_assign_int_float_lit_nested()
    test_assign_int_float_lit_global()
    test_assign_int_float_new_list()
    test_assign_int_float_new_set_dict()
    test_assign_int_float_new_comp()
    test_assign_int_float_new_copy()
    test_assign_int_float_new_slice()
    test_assign_int_float_ifexp_list()
    test_assign_none_lit_list()
    test_assign_none_var_list()
    test_assign_sub_lit_list()
    test_assign_sub_var_list()
    test_assign_sub_var_nested()
    test_assign_sub_call_list()
    test_assign_empty_lit_list()
    test_assign_empty_lit_dict()
    test_assign_empty_lit_tuple()
    test_assign_empty_lit_nested()
    test_assign_empty_new()
    test_assign_empty_new_collections()
    test_assign_empty_ifexp()
    test_assign_empty_var_filled()
    test_assign_empty_var()
    test_assign_empty_var_set_dict()
    test_assign_empty_call()
    test_attr_int_float_lit()
    test_attr_none_lit()
    test_attr_sub_new()
    test_attr_sub_var()
    test_attr_empty_lit_init()
    test_attr_empty_lit()
    test_attr_empty_lit_never()
    test_attr_empty_var()
    test_setitem_int_float_lit_scalar()
    test_setitem_int_float_lit_key()
    test_setitem_int_float_lit_list()
    test_setitem_int_float_lit_dict_value()
    test_setitem_int_float_lit_slice()
    test_setitem_none_lit()
    test_setitem_sub_new()
    test_setitem_sub_var()
    test_setitem_empty_lit()
    test_setitem_empty_new()
    test_setitem_empty_var()
    test_setitem_empty_lit_slice()
    test_arg_int_float_lit_scalar()
    test_arg_int_float_lit_list()
    test_arg_int_float_lit_dict()
    test_arg_int_float_lit_tuple()
    test_arg_int_float_lit_nested()
    test_arg_int_float_default()
    test_arg_int_float_keyword()
    test_arg_int_float_method()
    test_arg_int_float_lambda()
    test_arg_none()
    test_arg_sub_new()
    test_arg_sub_var()
    test_arg_empty_lit()
    test_arg_empty_new()
    test_arg_empty_lit_nested()
    test_arg_empty_lit_only()
    test_arg_empty_default()
    test_arg_empty_method()
    test_arg_empty_var()
    test_ret_int_float_lit_scalar()
    test_ret_int_float_lit_list()
    test_ret_int_float_yield_scalar()
    test_ret_int_float_yield_list()
    test_ret_int_float_lambda()
    test_ret_none()
    test_ret_sub_new()
    test_ret_sub_var()
    test_ret_empty_lit()
    test_ret_empty_new()
    test_ret_empty_lit_nested()
    test_ret_empty_lit_filled()
    test_ret_empty_var()
    test_ret_empty_yield()
    test_ret_empty_lambda()
    test_ret_empty_call()
    test_method_int_float_lit_scalar()
    test_method_int_float_var_scalar()
    test_method_int_float_lit_list()
    test_method_int_float_lit_iter_list()
    test_method_int_float_lit_iter_set()
    test_method_int_float_lit_iter_dict()
    test_method_int_float_lit_iter_deque()
    test_method_int_float_var_iter_list()
    test_method_int_float_var_iter_list_iadd()
    test_method_int_float_var_iter_set()
    test_method_int_float_var_iter_dict()
    test_method_int_float_var_iter_deque()
    test_method_none()
    test_method_sub_new()
    test_method_sub_var()
    test_method_empty_receiver()
    test_method_empty_receiver_new()
    test_method_empty_lit_elem()
    test_method_empty_new_elem()
    test_method_empty_var_elem()
    test_display_int_float_scalar()
    test_display_int_float_var_scalar()
    test_display_int_float_nested()
    test_display_none()
    test_display_sub_new()
    test_display_sub_var()
    test_display_empty_lit()
    test_display_empty_new()
    test_display_empty_lit_only()
    test_display_empty_var()
    test_binop_bool_arith()
    test_binop_int_float_scalar()
    test_binop_complex_scalar()
    test_binop_int_float_lit_list()
    test_binop_int_float_lit_mul()
    test_binop_int_float_lit_tuple()
    test_binop_int_float_var_set_method()
    test_binop_int_float_lit_augassign_list()
    test_binop_none()
    test_binop_sub_new()
    test_binop_sub_var()
    test_binop_empty_lit_list()
    test_binop_empty_lit_list_right()
    test_binop_empty_lit_tuple()
    test_binop_empty_new_counter()
    test_binop_empty_lit_mul()
    test_binop_empty_var_list()
    test_binop_empty_accumulate_list()
    test_binop_empty_accumulate_set()
    test_binop_empty_accumulate_dict()
    test_binop_empty_accumulate_frozenset()
    test_binop_empty_accumulate_counter()
    test_compare_int_float_scalar()
    test_compare_int_float_lit_list()
    test_compare_int_float_lit_dict()
    test_compare_int_float_lit_tuple()
    test_compare_none()
    test_compare_sub()
    test_compare_empty_lit_list()
    test_compare_empty_new()
    test_compare_empty_var()
    test_compare_empty_var_set()
    test_compare_empty_var_dict()
    test_compare_empty_call()
    test_lookup_bool_int()
    test_lookup_int_float_scalar()
    test_lookup_int_float_var_scalar()
    test_lookup_none()
    test_lookup_none_list()
    test_lookup_sub()
    test_lookup_sub_base_container()
    test_lookup_empty_container_lit()
    test_lookup_empty_container_new()
    test_lookup_empty_container_var()
    test_lookup_empty_value_lit_method()
    test_ctor_int_float_lit()
    test_ctor_int_float_lit_collections()
    test_ctor_int_float_var_list()
    test_ctor_int_float_var_set()
    test_ctor_int_float_var_dict()
    test_ctor_int_float_var_tuple()
    test_ctor_int_float_var_collections()
    test_ctor_none()
    test_ctor_sub()
    test_ctor_empty_var_set()
    test_ctor_empty_var_set_number()
    test_iter_int_float_lit_scalar()
    test_iter_int_float_var_scalar()
    test_iter_int_float_lit_list()
    test_unpack_int_float_lit()
    test_unpack_int_float_var()
    test_iter_none()
    test_iter_sub_new()
    test_iter_sub_var()
    test_unpack_sub_var()
    test_iter_empty_lit()
    test_iter_empty_lit_list()
    test_iter_empty_new()
    test_iter_empty_var()
    test_unpack_empty_lit()
    test_unpack_empty_lit_typed_number()
    test_iter_empty_call()
    test_choice_int_float_scalar()
    test_choice_int_float_lit_list()
    test_choice_none()
    test_choice_sub_new()
    test_choice_sub_var()
    test_choice_empty_lit()
    test_choice_empty_new()
    test_choice_empty_lit_boolop()
    test_choice_empty_lit_none()
    test_choice_empty_var()
    test_lib_int_float_scalar()
    test_lib_int_float_lit_iter()
    test_lib_int_float_var_iter()
    test_lib_int_float_var_reduce()
    test_lib_int_float_itertools()
    test_lib_int_float_heapq()
    test_lib_none()
    test_lib_none_reduce()
    test_lib_none_filter()
    test_lib_sub()
    test_lib_empty_lit_mixed()
    test_lib_empty_lit_chain_only()
    test_lib_empty_lit_product()
    test_lib_empty_lit_heappush()
    test_lib_empty_var()
    test_lib_empty_var_mixed_number()
    test_empty_call_contexts()


if __name__ == '__main__':
    test_all()
