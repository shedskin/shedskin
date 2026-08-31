def inner():
    yield 1
    yield 2

def outer():
    yield 0
    yield from inner()

#*ERROR* 50.py:7: 'yield from' is not supported
