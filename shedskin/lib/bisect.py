# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

def insort_right(a, x, lo=0, hi=0):
    insort(a, x)
def insort_left(a, x, lo=0, hi=0):
    insort(a, x)
def insort(a, x, lo=0, hi=0):
    a.append(x)
    __cmp(x, x)

def bisect_right(a, x, lo=0, hi=0):
    bisect(a, x)
    return 1
def bisect_left(a, x, lo=0, hi=0):
    bisect(a, x)
    return 1
def bisect(a, x, lo=0, hi=0):
    __cmp(x, x)
    return 1

