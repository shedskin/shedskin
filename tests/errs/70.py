class M:
    def __init__(self, x):
        self.x = x

    def __matmul__(self, other):
        return M(self.x * other.x)

print((M(3) @ M(4)).x)

#*ERROR* 70.py:8: matrix multiplication ('@') is not supported
