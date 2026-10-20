class M:
    def __init__(self, x):
        self.x = x

    def __imatmul__(self, other):
        self.x *= other.x
        return self

a = M(3)
a @= M(4)
print(a.x)

#*ERROR* 71.py:10: matrix multiplication ('@=') is not supported
