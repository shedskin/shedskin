
class fred:
    def __add__(self, x):                # [fred], [fred]
        return x                         # [int]

a = fred()                               # [fred] = [fred]
b = a + a                                # [int] = [int]

