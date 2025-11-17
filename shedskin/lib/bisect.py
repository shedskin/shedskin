# Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE)


def insort_right(a, x, lo=0, hi=0, __kw_key=None):
    insort(a, x, key=__kw_key)
def insort_left(a, x, lo=0, hi=0, __kw_key=None):
    insort(a, x, key=__kw_key)
def insort(a, x, lo=0, hi=0, __kw_key=None):
    a.append(x)
    __cmp(x, x)
    unit = iter(a).__next__()
    __cmp(__kw_key(unit), __kw_key(x))


def bisect_right(a, x, lo=0, hi=0, __kw_key=None):
    bisect(a, x, key=__kw_key)
    return 1
def bisect_left(a, x, lo=0, hi=0, __kw_key=None):
    bisect(a, x, key=__kw_key)
    return 1
def bisect(a, x, lo=0, hi=0, __kw_key=None):
    __cmp(x, x)
    unit = iter(a).__next__()
    __cmp(__kw_key(unit), x)
    return 1
