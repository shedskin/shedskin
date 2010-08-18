
def doubles(x):                          # x: [dict(B, A)]
    return x.values()                    # [list(A)]

f = {1: 1.0}
h = {3.0: 3}

a = doubles(f)
b = doubles(h)

