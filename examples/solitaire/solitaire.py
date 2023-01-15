#!/usr/bin/env python3

"""
Python implementation of Bruce Schneier's Solitaire Encryption
Algorithm (http://www.counterpane.com/solitaire.html).

John Dell'Aquila <jbd@alum.mit.edu>
"""

import string
import sys


def toNumber(c):
    """
    Convert letter to number: Aa->1, Bb->2, ..., Zz->26.
    Non-letters are treated as X's.
    """
    if c in string.ascii_letters:
        return ord(c.upper()) - 64
    return 24  # 'X'


def toChar(n):
    """
    Convert number to letter: 1->A,  2->B, ..., 26->Z,
    27->A, 28->B, ... ad infitum
    """
    return chr((n - 1) % 26 + 65)


class Solitaire:
    """Solitaire Encryption Algorithm
    http://www.counterpane.com/solitaire.html
    """

    def _setKey(self, passphrase):
        """
        Order deck according to passphrase.
        """
        self.deck = list(range(1, 55))
        # card numbering:
        #  1, 2,...,13 are A,2,...,K of clubs
        # 14,15,...,26 are A,2,...,K of diamonds
        # 27,28,...,39 are A,2,...,K of hearts
        # 40,41,...,52 are A,2,...,K of spades
        # 53 & 54 are the A & B jokers
        for c in passphrase:
            self._round()
            self._countCut(toNumber(c))

    def _down1(self, card):
        """
        Move designated card down 1 position, treating
        deck as circular.
        """
        d = self.deck
        n = d.index(card)
        if n < 53:  # not last card - swap with successor
            d[n], d[n + 1] = d[n + 1], d[n]
        else:  # last card - move below first card
            d[1:] = d[-1:] + d[1:-1]

    def _tripleCut(self):
        """
        Swap cards above first joker with cards below
        second joker.
        """
        d = self.deck
        a, b = d.index(53), d.index(54)
        if a > b:
            a, b = b, a
        d[:] = d[b + 1 :] + d[a : b + 1] + d[:a]

    def _countCut(self, n):
        """
        Cut after the n-th card, leaving the bottom
        card in place.
        """
        d = self.deck
        n = min(n, 53)  # either joker is 53
        d[:-1] = d[n:-1] + d[:n]

    def _round(self):
        """
        Perform one round of keystream generation.
        """
        self._down1(53)  # move A joker down 1
        self._down1(54)  # move B joker down 2
        self._down1(54)
        self._tripleCut()
        self._countCut(self.deck[-1])

    def _output(self):
        """
        Return next output card.
        """
        d = self.deck
        while 1:
            self._round()
            topCard = min(d[0], 53)  # either joker is 53
            if d[topCard] < 53:  # don't return a joker
                return d[topCard]

    def encrypt(self, txt, key):
        """
        Return 'txt' encrypted using 'key'.
        """
        self._setKey(key)
        # pad with X's to multiple of 5
        txt = txt + "X" * ((5 - len(txt)) % 5)
        cipher = [None] * len(txt)
        for n in range(len(txt)):
            cipher[n] = toChar(toNumber(txt[n]) + self._output())
        # add spaces to make 5 letter blocks
        for n in range(len(cipher) - 5, 4, -5):
            cipher[n:n] = [" "]
        return "".join(cipher)

    def decrypt(self, cipher, key):
        """
        Return 'cipher' decrypted using 'key'.
        """
        self._setKey(key)
        # remove white space between code blocks
        cipher = "".join(cipher.split())
        txt = [None] * len(cipher)
        for n in range(len(cipher)):
            txt[n] = toChar(toNumber(cipher[n]) - self._output())
        return "".join(txt)


testCases = (  # test vectors from Schneier paper
    ("AAAAAAAAAAAAAAA", "", "EXKYI ZSGEH UNTIQ"),
    ("AAAAAAAAAAAAAAA", "f", "XYIUQ BMHKK JBEGY"),
    ("AAAAAAAAAAAAAAA", "fo", "TUJYM BERLG XNDIW"),
    ("AAAAAAAAAAAAAAA", "foo", "ITHZU JIWGR FARMW"),
    ("AAAAAAAAAAAAAAA", "a", "XODAL GSCUL IQNSC"),
    ("AAAAAAAAAAAAAAA", "aa", "OHGWM XXCAI MCIQP"),
    ("AAAAAAAAAAAAAAA", "aaa", "DCSQY HBQZN GDRUT"),
    ("AAAAAAAAAAAAAAA", "b", "XQEEM OITLZ VDSQS"),
    ("AAAAAAAAAAAAAAA", "bc", "QNGRK QIHCL GWSCE"),
    ("AAAAAAAAAAAAAAA", "bcd", "FMUBY BMAXH NQXCJ"),
    ("AAAAAAAAAAAAAAAAAAAAAAAAA", "cryptonomicon", "SUGSR SXSWQ RMXOH IPBFP XARYQ"),
    ("SOLITAIRE", "cryptonomicon", "KIRAK SFJAN"),
)


def usage():
    print(
        """Usage:
    sol.py {-e | -d} _key_ < _file_
    sol.py -test
    
    N.B. WinNT requires "python sol.py ..."
    for input redirection to work (NT bug).
    """
    )
    sys.exit(2)


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        usage()
    elif args[1] == "-test":
        s = Solitaire()
        for txt, key, cipher in testCases:
            coded = s.encrypt(txt, key)
            assert cipher == coded
            decoded = s.decrypt(coded, key)
            # assert decoded[:len(txt)] == string.upper(txt)
            print(decoded[: len(txt)], txt.upper())
            # assert decoded[:len(txt)] == txt.upper()
        print("All tests passed.")
    elif len(args) < 3:
        usage()
    elif args[1] == "-e":
        print(Solitaire().encrypt(sys.stdin.read(), args[2]))
    elif args[1] == "-d":
        print(Solitaire().decrypt(sys.stdin.read(), args[2]))
    else:
        usage()
