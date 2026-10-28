def reduce(func, iter1, initial):
    acc = initial
    acc = func(acc, iter(iter1).__next__())
    return acc

def __reduce2(func, iter1):
    elem = iter(iter1).__next__()
    acc = elem
    acc = func(acc, elem)
    return acc
