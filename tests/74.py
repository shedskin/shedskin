
def duplll(x):                           # x: [list(A)]
    return [x]                           # [list(list(A))]

a = duplll([1])                          # [list(list(int))]
b = duplll([1.0])                        # [list(list(float))]

def ident(x):                            # x: [list(list(A))]r
    return x                             # [list(list(A))]
def meuk(x):                             # x: [list(list(A))]
    return ident(x)                      # [list(list(A))]

c = meuk(a)                              # [list(list(int))]
d = meuk(b)                              # [list(list(float))]

def makel(x):                            # x: [list(A)]
    return [x]                           # [list(list(A))]

def dupl(x):                             # x: [list(list(A))]
    return [makel(x[0])]                 # [list(list(list(A)))]

y = [[('1',)]]                           # [list(list(tuple(str)))]
dupl(y)                                  # [list(list(list(tuple(str))))]

dupl([[1]])                              # [list(list(list(int)))]

#d = [[1]]                                # [list(list(int))]
d = [[1.0]]                              # [list(list(float))]
d                                        # [list(list(pyobj))]

def ident2(x):                           # x: [list(pyobj)]r
    return x                             # [list(pyobj)]

bh = []                                  # [list(pyobj)]
#ident2(bh).append(1)                     # []
ident2(bh).append(1.0)                   # []

ah = []                                  # [list(pyobj)]
ident2(ah).append(1)                     # []
#ident2(ah).append(1.0)                   # []

