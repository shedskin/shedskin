
def count(n=0):
    while True:
        yield n
        n += 1
    
def cycle(iterable):
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
            yield element

def repeat(object, times=-1):
    if times == -1:
        while True:
            yield object
    else:
        for i in xrange(times):
            yield object
