lam = lambda a, /, b: a + b
print(lam(1, 5))

#*ERROR* 95.py:1: positional-only arguments in lambdas are not supported
