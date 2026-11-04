def apply0(fn):
    return fn()

print(apply0(lambda *, s=str(1): s))

#*ERROR* 90.py:4: default arguments in lambdas are not supported
