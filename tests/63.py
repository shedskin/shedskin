
a = []                                   # [list(int)]
a.append(1)                              # []
b = []                                   # [list(float)]
b.append(1.0)                            # []

def dupl(y):                             # y: [list(A)]
    l = []                               # [list(A)]
    l.append(y[0])                       # []
    return l                             # [list(A)]

c = dupl(a)                                  # [list(int)]
d = dupl(b)                                  # [list(float)]

