def gen():
    x = yield 1
    print(x)
    yield 2

print(list(gen()))

#*ERROR* 58.py:2: 'yield' as an expression is not supported
