def reduce(func, iter1, initial):
    elem = iter(iter1).__next__()
    elem = initial
    elem = func(elem, elem)
    return elem

def __reduce2(func, iter1):
    elem = iter(iter1).__next__()
    return func(elem, elem)
