
def bla(l):                              # l: [list(A)]
    return [y for y in l]                # [list(A)]

a = bla([1, 2, 3])                                 # [list(int)]
b = bla([1.1, 2.2, 3.3])                               # [list(float)]
print a, b

