def reduce(func, iter1, init=None):
    elem = iter(iter1).__next__()
#    elem = init
    elem = func(elem, elem)
    return elem
