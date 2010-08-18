
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

a = []                                   # [list(int)]
a = []                                   # [list(int)]
b = []                                   # [list(float)]
c = []                                   # [list(int)]
ident(a).append(1)                       # []
ident(b).append(1.0)                     # []
ident(c).append(1)                       # []

def dupl(y):                             # y: [list(A)]
    k = []                               # [list(float)]
    k.append(1.0)                        # []

    v = []                               # [list(int)]
    v.append(1)                          # []

    l = []                               # [list(A)]
    l.append(y[0])                     # []

    return l                             # [list(A)]

b = []                                   # [list(float)]
b.append(1.0)                            # []
dupl(b)                                  # [list(float)]

a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a = []                                   # [list(int)]
a.append(1)                              # []
dupl(a)                                  # [list(int)]

def makel(x):                            # x: [A]
    l = []                               # [list(A)]
    l.append(x)                          # []
    return l                             # [list(A)]

d = makel(1)                                 # [list(int)]
e = makel(1.0)                               # [list(float)]

