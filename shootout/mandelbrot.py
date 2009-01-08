# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Tupteq

import sys

def cout(c):
    sys.stdout.write(c)

def main():
    iter = 50
    limit = 2.
    size = int(sys.argv[1])
    fsize = float(size)
    bit_num = 7
    byte_acc = 0

    cout("P4\n%d %d\n" % (size, size))

    for y in xrange(size):
        fy = 2j * y / fsize - 1j
        for x in xrange(size):
            z = 0j
            c = 2. * x / fsize - 1.5 + fy

            for i in xrange(iter):
                z = z * z + c
                if abs(z) >= limit:
                    break
            else:
                byte_acc += 1 << bit_num

            if bit_num == 0:
                cout(chr(byte_acc))
                bit_num = 7
                byte_acc = 0
            else:
                bit_num -= 1

        if bit_num != 7:
            cout(chr(byte_acc))
            bit_num = 7
            byte_acc = 0

main()
