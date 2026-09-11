# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


class Error(Exception):
    pass


def copy(a):
    a.__copy__() # XXX hardcode in ss.py?
    return a

def deepcopy(a):
    a.__deepcopy__()
    return a