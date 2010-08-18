
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

b = [1.0]                                # [list(float)]
a = [1]                                  # [list(int)]
a = [2]                                  # [list(int)]
ident(a).append(1)                       # []
ident(b).append(1.0)                     # []

def hoppa(y):                            # y: [list(A)]
    k = [1.0]                            # [list(float)]
    l = [y[0]]                           # [list(A)]
    return l                             # [list(A)]

c = hoppa(a)                             # [list(int)]
d = hoppa(b)                             # [list(float)]

