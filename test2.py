# non-escaping tuple

def woef(x, y, z):
    v = (x, y, z)  # HERE
    return sum(v)


def main():
    s = 0
    for x in range(10**8):
        s += woef(x, x+1, x-1)
    print(s)


if __name__ == '__main__':
    main()
