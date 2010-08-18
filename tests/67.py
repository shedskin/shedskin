
def dupl(y):                             # y: [list(A)]
    return [y[0]]                        # [list(A)]

a = [1]                                  # [list(int)]
a = [2]                                  # [list(int)]
b = [1.0]                                # [list(float)]
c = dupl(a)                                  # [list(int)]
d = dupl(b)                                  # [list(float)]

