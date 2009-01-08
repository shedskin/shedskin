# The Computer Language Shootout Benchmarks
# http://shootout.alioth.debian.org/
# Contributed by Kevin Carson
# Optimized for speed by bearophile, Jan 7 2006

from sys import argv, stdout

class Pair:
    def __init__(self, a, b):
        self.a = a
        self.b = b

iub = [Pair('a', 0.27),
       Pair('c', 0.12),
       Pair('g', 0.12),
       Pair('t', 0.27),
       Pair('B', 0.02),
       Pair('D', 0.02),
       Pair('H', 0.02),
       Pair('K', 0.02),
       Pair('M', 0.02),
       Pair('N', 0.02),
       Pair('R', 0.02),
       Pair('S', 0.02),
       Pair('V', 0.02),
       Pair('W', 0.02),
       Pair('Y', 0.02)]

homosapiens = [Pair('a', 0.3029549426680),
               Pair('c', 0.1979883004921),
               Pair('g', 0.1975473066391),
               Pair('t', 0.3015094502008)]

alu = "GGCCGGGCGCGGTGGCTCACGCCTGTAATCCCAGCACTTTGGGAGGCCGAGGCGGGCGGATCACCTGAGGTCAGGAGTT"\
      "CGAGACCAGCCTGGCCAACATGGTGAAACCCCGTCTCTACTAAAAATACAAAAATTAGCCGGGCGTGGTGGCGCGCGCC"\
      "TGTAATCCCAGCTACTCGGGAGGCTGAGGCAGGAGAATCGCTTGAACCCGGGAGGCGGAGGTTGCAGTGAGCCGAGATC"\
      "GCGCCACTGCACTCCAGCCTGGGCGACAGAGCGAGACTCCGTCTCAAAAA"

IM = 139968
IA =   3877
IC =  29573

LAST = 42
def gen_random(max):
    global LAST
    LAST = (LAST * IA + IC) % IM
    return (max * LAST) / IM


def makeCumulative(genelist):
    cp = 0.0
    for i in xrange(len(genelist)):
        cp += genelist[i].b
        genelist[i].b = cp


def selectRandom(genelist):
    r = gen_random(1.0)
    for pair in genelist:
        if r < pair.b:
            return pair.a


def makeRandomFasta(id, desc, genelist, todo):
    print ">" + str(id), desc
    line_length = 60
    a = list(" " * line_length)
    for i in xrange(todo / line_length):
        for j in xrange(line_length):
            a[j] = selectRandom(genelist)
        print "".join(a)
        print

    todo = todo % line_length
    while todo > 0:
        if todo > line_length:
            out_length = line_length
        else:
            out_length = todo

        pick = ""
        for i in xrange(out_length):
            pick += selectRandom(genelist)

        print pick
        todo -= line_length


def makeRepeatFasta(id, desc, s, todo):
    print ">%s %s" % (id, desc)
    line_length = 60
    s_length = len(s)
    wrap = 0

    while todo > 0:
        if todo > line_length:
            out_length = line_length
        else:
            out_length = todo

        while out_length >= (s_length - wrap):
            stdout.write(s[wrap:])
            out_length -= s_length - wrap
            wrap = 0

        print s[wrap:wrap + out_length]
        wrap += out_length
        todo -= line_length


n = int(argv[1])

makeCumulative(iub)
makeCumulative(homosapiens)

makeRepeatFasta("ONE", "Homo sapiens alu", alu, n*2)
makeRandomFasta("TWO", "IUB ambiguity codes", iub, n*3)
makeRandomFasta("THREE", "Homo sapiens frequency", homosapiens, n*5)
