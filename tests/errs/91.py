def deco(c):
    return c

@deco
class A:
    pass

print(A())

#*ERROR* 91.py:4: class decorators are not supported
