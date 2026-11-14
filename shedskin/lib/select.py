# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)
__void = 0

# as CPython, error is OSError itself (a typedef in select.hpp)
class error(OSError): pass
__exception = error('')
__exception.errno = 0

# like CPython, the arguments hold file descriptors (ints) or objects with a
# fileno() method, and each result holds the ready elements themselves
def select(rFDs, wFDs, xFDs, timeout=__void):
    for x in rFDs:
        x.fileno()
    for x in wFDs:
        x.fileno()
    for x in xFDs:
        x.fileno()
    return (list(rFDs), list(wFDs), list(xFDs))
