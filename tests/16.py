
class integer:
    def __gt__(self, b):            # self: [integer], b: [integer]
        return 1

def maxi(a, b):                           # a: [integer]r, b: [integer]r
    if a > b:                            # [bool]
        return a                         # [integer]
    return b                             # [integer]

def qbert():                             # a: [integer], c: [integer]r, b: [integer]
    a = integer()                        # [integer]
    b = integer()                        # [integer]
    c = maxi(a, b)                        # [integer]
    return c                             # [integer]

qbert()                                  # [integer]

