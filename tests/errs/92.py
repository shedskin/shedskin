def deco(f):
    return f

@deco
def foo():
    return 1

print(foo())

#*ERROR* 92.py:4: unsupported type of decorator
