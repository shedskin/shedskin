# non-escaping Vector

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def woef(x, y, z):
    return Vector(x, y, z)  # HERE


def main():
    s = 0
    for x in range(10**8):
        v = woef(x, x+1, x-1)
        s += v.x + v.y + v.z
    print(s)


if __name__ == '__main__':
    main()
