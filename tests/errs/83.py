def f():
    a = [1, 2]
    return *a, 3

print(f())

#*ERROR* 83.py:3: iterable unpacking ('*') in a tuple display is not supported
