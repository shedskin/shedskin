
class integer:
    def __gt__(self, b):
        return True
    def __repr__(self):
        return 'integer!'

def maxi(a, b):                           # [integer], [integer]
    if a > b:                            # [bool]
        return a                         # [integer]
    return b                             # [integer]

a = integer()                            # [integer]
b = integer()                            # [integer]
c = maxi(a, b)                            # [integer]
d = a > b                                # [bool]
print a, b, c, d

