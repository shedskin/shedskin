
class fred:                              # y: [int]*
    def __eq__(self, x):                 # self: [fred], x: [fred]
        return self.y == x.y             # [int]

a = fred()                               # [fred]
a.y = 1                                  # [int]
b = fred()                               # [fred]
b.y = 2                                  # [int]

print a == b                             # [int]
print a == a                             # [int]
print b == b                             # [int]

