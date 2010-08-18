
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

a = []                                   # [list(int)]
a = []                                   # [list(int)]
b = []                                   # [list(float)]
c = []                                   # [list(int)]
ident(a).append(1)                       # []
ident(b).append(1.0)                     # []
ident(c).append(1)                       # []

