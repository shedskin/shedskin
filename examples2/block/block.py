#!/usr/bin/env python
##                   (c) David MacKay - Free software. License: GPL
## For license statement see  http://www.gnu.org/copyleft/gpl.html
"""
This is a BLOCK compression algorithm
that uses the Huffman algorithm.

This simple block compressor assumes that the source file
is an exact multiple of the block length.
The encoding does not itself delimit the size of the file, so
the decoder needs to knows where the end of the compressed
file is. Thus we must either ensure the decoder knows
the original file's length, or we have to use a special
end-of-file character. A superior compressor would first
encode the source file's length at the head of the compressed
file; then the decoder would be able to stop at the right
point and correct any truncation errors. I'll fix this
in block2.py.

The package contains the following functions:

 findprobs(f=0.01,N=6):
    Find probabilities of all the events
    000000
    000001
     ...
    111111
    <-N ->

 Bencode(string,symbols,N):
    Reads in a string of 0s and 1s, forms blocks, and encodes with Huffman.
    
 Bdecode(string,root,N):
    Decode a binary string into blocks, then return appropriate 0s and 1s
    
 compress_it( inputfile, outputfile ):
    Make Huffman code, and compress
    
 uncompress_it( inputfile, outputfile ):
    Make Huffman code, and uncompress

 There are also three test functions.
 If block.py is run from a terminal, it invokes compress_it (using stdin)
 or uncompress_it (using stdin), respectively if there are zero arguments
 or one argument.

"""
## /home/mackay/python/compression/huffman/Huffman3.py
## This supplies the huffman algorithm, complete with encoders and decoders:

import sys, os


class node:
    def __init__(self, count, index, name=""):
        self.count = float(count)
        self.index = index
        self.name = name  ## optional argument
        if self.name == "":
            self.name = "_" + str(index)
        self.word = ""  ## codeword will go here
        self.isinternal = 0

    def __lt__(self, other):
        return self.count < other.count

    def report(self):
        if self.index == 1:
            print("#Symbol\tCount\tCodeword")
        print("%s\t(%2.2g)\t%s" % (self.name, self.count, self.word))
        pass

    def associate(self, internalnode):
        self.internalnode = internalnode
        internalnode.leaf = 1
        internalnode.name = self.name
        pass


class internalnode:
    def __init__(self):
        self.leaf = 0
        self.child = []
        pass

    def children(self, child0, child1):
        self.leaf = 0
        self.child.append(child0)
        self.child.append(child1)
        pass


def find_idx(seq, index):
    for item in seq:
        if item.index == index:
            return item


def find_name(seq, name):
    for item in seq:
        if item.name == name:
            return item


def iterate(c):
    """
    Run the Huffman algorithm on the list of "nodes" c.
    The list of nodes c is destroyed as we go, then recreated.
    Codewords 'co.word' are assigned to each node during the recreation of the list.
    The order of the recreated list may well be different.
    Use the list c for encoding.

    The root of a new tree of "internalnodes" is returned.
    This root should be used when decoding.

    >>> c = [ node(0.5,1,'a'),  \
              node(0.25,2,'b'), \
              node(0.125,3,'c'),\
              node(0.125,4,'d') ]   # my doctest query has been resolved
    >>> root = iterate(c)           # "iterate(c)" returns a node, not nothing, and doctest cares!
    >>> reportcode(c)               # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
    #Symbol   Count Codeword
    a         (0.5) 1
    b         (0.25)    01
    c         (0.12)    000
    d         (0.12)    001
    """
    if len(c) > 1:
        c.sort()  ## sort the nodes by count, using the __cmp__ function defined in the node class
        deletednode = c[
            0
        ]  ## keep copy of smallest node so that we can put it back in later
        second = c[1].index  ## index of second smallest node
        # MERGE THE BOTTOM TWO
        c[1].count += c[
            0
        ].count  ##  this merged node retains the name of the bigger leaf.
        del c[0]

        root = iterate(c)

        ## Fill in the new information in the ENCODING list, c
        ## find the codeword that has been split/joined at this step
        co = find_idx(c, second)
        #       co = find( lambda p: p.index == second , c )
        deletednode.word = co.word + "0"
        c.append(deletednode)  ## smaller one gets 0
        co.word += "1"
        co.count -= deletednode.count  ## restore correct count

        ## make the new branches in the DECODING tree
        newnode0 = internalnode()
        newnode1 = internalnode()
        treenode = co.internalnode  # find the node that got two children
        treenode.children(newnode0, newnode1)
        deletednode.associate(newnode0)
        co.associate(newnode1)
        pass
    else:
        c[0].word = ""
        root = internalnode()
        c[0].associate(root)
        pass
    return root


def encode(sourcelist, code):
    """
    Takes a list of source symbols. Returns a binary string.
    """
    answer = ""
    for s in sourcelist:
        co = find_name(code, s)
        #        co = find(lambda p: p.name == s, code)
        if not co:
            print("Warning: symbol", repr(s), "has no encoding!", file=sys.stderr)
            pass
        else:
            answer = answer + co.word
            pass
    return answer


def decode(string, root):
    """
    Decodes a binary string using the Huffman tree accessed via root
    """
    ## split the string into a list
    ## then copy the elements of the list one by one.
    answer = []
    clist = list(string)
    ## start from root
    currentnode = root
    for c in clist:
        if c == "\n":
            continue  ## special case for newline characters
        assert (c == "0") or (c == "1")
        currentnode = currentnode.child[int(c)]
        if currentnode.leaf != 0:
            answer.append(str(currentnode.name))
            currentnode = root
        pass
    assert (
        currentnode == root
    )  ## if this is not true then we have run out of characters and are half-way through a codeword
    return answer


## alternate way of calling huffman with a list of counts ## for use as package by other programs ######
## two example ways of using it:
# >>> from Huffman3 import *
# >>> huffman([1, 2, 3, 4],1)
# >>> (c,root) = huffman([1, 2, 3, 4])

## end ##########################################################################


def makenodes(probs):
    """
    Creates a list of nodes ready for the Huffman algorithm.
    Each node will receive a codeword when Huffman algorithm "iterate" runs.

    probs should be a list of pairs('<symbol>', <value>).

    >>> probs=[('a',0.5), ('b',0.25), ('c',0.125), ('d',0.125)]
    >>> symbols = makenodes(probs)
    >>> root = iterate(symbols)
    >>> zipped = encode(['a','a','b','a','c','b','c','d'], symbols)
    >>> print zipped
    1101100001000001
    >>> print decode( zipped, root )
    ['a', 'a', 'b', 'a', 'c', 'b', 'c', 'd']

    See also the file Example.py for a python program that uses this package.
    """
    m = 0
    c = []
    for p in probs:
        m += 1
        c.append(node(p[1], m, p[0]))
        pass
    return c


def dec_to_bin(n, digits):
    """n is the number to convert to binary;  digits is the number of bits you want
    Always prints full number of digits
    >>> print dec_to_bin( 17 , 9)
    000010001
    >>> print dec_to_bin( 17 , 5)
    10001

    Will behead the standard binary number if requested
    >>> print dec_to_bin( 17 , 4)
    0001
    """
    if n < 0:
        sys.stderr.write("warning, negative n not expected\n")
    i = digits - 1
    ans = ""
    while i >= 0:
        b = ((1 << i) & n) > 0
        i -= 1
        ans = ans + str(int(b))
    return ans


verbose = 0


def weight(string):
    """
    ## returns number of 0s and number of 1s in the string
    >>> print weight("00011")
    (3, 2)
    """
    w0 = 0
    w1 = 0
    for c in list(string):
        if c == "0":
            w0 += 1
            pass
        elif c == "1":
            w1 += 1
            pass
        pass
    return (w0, w1)


def findprobs(f=0.01, N=6):
    """Find probabilities of all the events
    000000
    000001
     ...
    111111
    <-N ->
    >>> print findprobs(0.1,3)              # doctest:+ELLIPSIS
    [('000', 0.7...),..., ('111', 0.001...)]
    """
    answer = []
    for n in range(2**N):
        s = dec_to_bin(n, N)
        (w0, w1) = weight(s)
        if verbose and 0:
            print(s, w0, w1)
        answer.append((s, f**w1 * (1 - f) ** w0))
        pass
    assert len(answer) == 2**N
    return answer


def Bencode(string, symbols, N):
    """
    Reads in a string of 0s and 1s.
    Creates a list of blocks of size N.
    Sends this list to the general-purpose Huffman encoder
    defined by the nodes in the list "symbols".
    """
    blocks = []
    chars = list(string)

    s = ""
    for c in chars:
        s = s + c
        if len(s) >= N:
            blocks.append(s)
            s = ""
            pass
        pass
    if len(s) > 0:
        print("warning, padding last block with 0s", file=sys.stderr)
        while len(s) < N:
            s = s + "0"
            pass
        blocks.append(s)
        pass

    if verbose:
        print("blocks to be encoded:")
        print(blocks)
        pass
    zipped = encode(blocks, symbols)
    return zipped


def Bdecode(string, root, N):
    """
    Decode a binary string into blocks.
    """
    answer = decode(string, root)
    if verbose:
        print("blocks from decoder:")
        print(answer)
        pass
    output = "".join(answer)
    ## this assumes that the source file was an exact multiple of the blocklength
    return output


def easytest():
    """
    Tests block code with N=3, f=0.01 on a tiny example.
    >>> easytest()                 # doctest:+NORMALIZE_WHITESPACE
    #Symbol Count           Codeword
    000         (0.97)          1
    001         (0.0098)    001
    010         (0.0098)    010
    011         (9.9e-05)   00001
    100         (0.0098)    011
    101         (9.9e-05)   00010
    110         (9.9e-05)   00011
    111         (1e-06)     00000
    zipped  = 1001010000010110111
    decoded = ['000', '001', '010', '011', '100', '100', '000']
    OK!
    """
    N = 3
    f = 0.01
    probs = findprobs(f, N)
    #    if len(probs) > 999 :
    #        sys.setrecursionlimit( len(probs)+100 )
    symbols = makenodes(probs)  # makenodes is defined at the bottom of Huffman3 package
    root = iterate(
        symbols
    )  # make huffman code and put it into the symbols' nodes, and return the root of the decoding tree

    symbols.sort(key=lambda x: x.index)  # sort by index
    for co in symbols:  # and write the answer
        co.report()

    source = ["000", "001", "010", "011", "100", "100", "000"]
    zipped = encode(source, symbols)
    print("zipped  =", zipped)
    answer = decode(zipped, root)
    print("decoded =", answer)
    if source != answer:
        print("ERROR")
    else:
        print("OK!")
    pass


def test():
    easytest()
    hardertest()


def hardertest():
    print("Reading the BentCoinFile")
    inputfile = open("testdata/BentCoinFile", "r")
    outputfile = open("tmp.zip", "w")
    print("Compressing to tmp.zip")
    compress_it(inputfile, outputfile)
    outputfile.close()
    inputfile.close()
    #    print "DONE compressing"

    inputfile = open("tmp.zip", "r")
    outputfile = open("tmp2", "w")
    print("Uncompressing to tmp2")
    uncompress_it(inputfile, outputfile)
    outputfile.close()
    inputfile.close()
    #    print "DONE uncompressing"

    print("Checking for differences...")
    os.system("diff testdata/BentCoinFile tmp2")
    os.system("wc tmp.zip testdata/BentCoinFile tmp2")
    pass


f = 0.01
N = 12  #  1244 bits if N==12
f = 0.01
N = 5  #  2266  bits if N==5
f = 0.01
N = 10  #  1379 bits if N==10


def compress_it(inputfile, outputfile):
    """
    Make Huffman code for blocks, and
    Compress from file (possibly stdin).
    """
    probs = findprobs(f, N)
    symbols = makenodes(probs)
    #    if len(probs) > 999 :
    #        sys.setrecursionlimit( len(probs)+100 )
    root = iterate(
        symbols
    )  # make huffman code and put it into the symbols' nodes, and return the root of the decoding tree

    string = inputfile.read()
    outputfile.write(Bencode(string, symbols, N))
    pass


def uncompress_it(inputfile, outputfile):
    """
    Make Huffman code for blocks, and
    UNCompress from file (possibly stdin).
    """
    probs = findprobs(f, N)
    #    if len(probs) > 999 :
    #        sys.setrecursionlimit( len(probs)+100 )
    symbols = makenodes(probs)
    root = iterate(
        symbols
    )  # make huffman code and put it into the symbols' nodes, and return the root of the decoding tree

    string = inputfile.read()
    outputfile.write(Bdecode(string, root, N))
    pass


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    test()
    pass
