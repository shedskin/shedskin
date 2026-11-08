"""functions used as values in another module (1029-C1)

named so that util_funcs.hpp is included after test_import.hpp
"""

from spam import Spam


def inc(a):
    return a + 1


def shout(s):
    return s.upper()


def spam_name(sp):
    return sp.name() + '!'


def make_spam():
    return Spam()
