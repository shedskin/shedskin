# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


class Error(Exception):
    pass


def copy(x):
    x.__copy__() # XXX hardcode in ss.py?
    return x

def deepcopy(x):
    x.__deepcopy__()
    return x