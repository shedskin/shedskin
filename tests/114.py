
def bla():
    a = []                               # [list(int)]
    a.append(1)                          # []

    b = a                                # [list(int)]

    a = []                               # [list(int)]
    a.append(2)                          # []

    print b                              # [list(int)]

bla()                                    # []

