# non-escaping Vector

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


def woef(x, y, z):
    v = Vector(x, y, z)  # HERE
    return v.x + v.y + v.z


def main():
    s = 0
    for x in range(10**8):
        s += woef(x, x+1, x-1)
    print(s)


if __name__ == '__main__':
    main()
