lam = lambda a, *, b: a + b
print(lam(1, b=5))

#*ERROR* 94.py:1: keyword-only arguments in lambdas are not supported
