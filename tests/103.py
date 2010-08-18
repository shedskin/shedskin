

class fred:                              # x: [float, int]*
    def bla(self):                       # self: [fred(A)]
        self.meth_templ(1, 1)            # [int]
        self.meth_templ(1.0, 1)          # [float]

        self.hop(self.x)                 # [A]

    def meth_templ(self, x, z):          # self: [fred(A)], x: [B]r, z: [int]
        y = x                            # [B]
        return y                         # [B]

    def hop(self, x):                    # self: [fred(A)], x: [A]r
        return x                         # [A]

a = fred()                               # [fred(int)]
a.x = 1                                  # [int]
a.bla()                                  # []

b = fred()                               # [fred(float)]
b.x = 1.0                                # [float]
b.bla()                                  # []

