
class bert:                              # c: [int, str]*, bla: [int, float]*
    def hoppa(self, b, d):               # self: [bert(int;float), bert(str;int)], b: [int, float]*, d: [int, str]*
        self.bla = b                     # [int, float]
        self.c = d                       # [int, str]
    def flops(self, e, f):               # self: [bert(int;float), bert(str;int)], e: [str], f: [int, float, str]
        pass
    def unbox(self, g, h):               # self: [bert(int;float), bert(str;int)], g: [int], h: [int]
        pass

a = bert()                               # [bert(str;int)]
a.hoppa(1, '1')                          # []
a.flops('1',1)                           # []
a.unbox(1, 2)                            # []

b = bert()                               # [bert(int;float)]
b.hoppa(1.0,1)                           # []
b.flops('1',1.0)                         # []
b.unbox(1, 2)                            # []

c = bert()                               # [bert(str;int)]
c.hoppa(2, '1')                          # []
c.flops('1',1)                         # []


