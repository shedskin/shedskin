
# python2.3 compatibility
try: enumerate
except NameError:
    def enumerate(collection):
        i = 0
        it = iter(collection)
        while 1:
            yield (i, it.next())
            i += 1
try: set
except NameError:
    from sets import Set, ImmutableSet
    set = Set; frozenset = ImmutableSet

