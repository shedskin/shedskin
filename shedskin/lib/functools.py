def reduce(func, iter1, init=None):
    elem = iter(iter1).next()
#    elem = init
    elem = func(elem, elem)
    return elem
