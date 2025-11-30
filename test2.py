# return tuple escaping once

def blaap(x, y):
    return (2*x, 3*y)


def main():
    s = 0
    for i in range(10**8):
        a, b = blaap(i, i+1)
        s += a + b
    print(s)


if __name__ == '__main__':
    main()


