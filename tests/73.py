
def ident(x):                            # x: [list(A)]r
    return x                             # [list(A)]

def makel(x):                            # x: [list(A)]
    return [x]                           # [list(list(A))]

def dupl(x):                             # x: [list(list(A))]
    return [makel(x[0])]                 # [list(list(list(A)))]

y = [[1.0]]                              # [list(list(float))]
dupl(y)                                  # [list(list(list(float)))]
dupl([[1]])                              # [list(list(list(int)))]

ah = []                                  # [list(float)]
ident(ah).append(1.0)                    # []

bh = []                                  # [list(int)]
ident(bh).append(1)                      # []

