
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

a = []                                   # [list(int)]
ident(a)                                 # [list(int)]
u = a                                    # [list(int)]
u.append(1)                              # []

b = ['']                                 # [list(str)]
ident(b).append('')                      # []
b.extend(b)                              # []

