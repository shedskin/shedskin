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
    bit = 0x80
    bit_accu = 0
    gone = False

    cout("P4\n%d %d\n" % (size, size))

    for y in xrange(size):
        ci = 2.0 * y / size - 1.0

        for x in xrange(size):
            cr = 2.0 * x / size - 1.5

            zr = 0; zi = 0; pr = 0; pi = 0

            for i in xrange(iter):
                zi = 2.0 * zr * zi + ci
                zr = pr - pi + cr
                pi = zi * zi
                pr = zr * zr
                if pi+pr > limit:
                    gone = True
                    break

            if gone:
                gone = False
            else:
                bit_accu |= bit

            if bit == 1:
                cout(chr(bit_accu))
                bit_accu = 0
                bit = 0x80
            else:
                bit >>= 1

        if bit != 0x80:
            cout(chr(bit_accu))
            bit_accu = 0
            bit = 0x80

main()
