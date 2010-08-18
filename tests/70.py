
def ident(x):                            # x: [list(pyobj)]r
    return x                             # [list(pyobj)]

ah = []                                  # [list(pyobj)]
ident(ah).append(1)                      # []
#ident(ah).append(1.0)                    # []

bh = []                                  # [list(pyobj)]
#ident(bh).append(1)                      # []
ident(bh).append(1.0)                    # []

