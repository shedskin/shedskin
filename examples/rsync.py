#!/usr/bin/env python
# -*- coding: utf-8 -*-

### to compile this, copy lib/hashlib.* to the shedskin lib dir, or use shedskin -Llib!

"""
This is a pure Python implementation of the [rsync algorithm](TM96).

[TM96] Andrew Tridgell and Paul Mackerras. The rsync algorithm.
Technical Report TR-CS-96-05, Canberra 0200 ACT, Australia, 1996.
http://samba.anu.edu.au/rsync/.

"""

# taken from: http://code.activestate.com/recipes/577518-rsync-algorithm/

import collections
import hashlib

class Element:
    def __init__(self, index=-1, data=None):
        self.index = index
        self.data = data

def rsyncdelta(datastream, remotesignatures, blocksize):
    """
    Generates a binary patch when supplied with the weak and strong
    hashes from an unpatched target and a readable stream for the
    up-to-date data. The blocksize must be the same as the value
    used to generate remotesignatures.
    """
    remote_weak, remote_strong = remotesignatures

    match = True
    matchblock = -1
    delta = []

    while True:
        if match and datastream is not None:
            # Whenever there is a match or the loop is running for the first
            # time, populate the window using weakchecksum instead of rolling
            # through every single byte which takes at least twice as long.
            window = collections.deque(datastream.read(blocksize))
            checksum, a, b = weakchecksum(''.join(window))

        try:
            # If there are two identical weak checksums in a file, and the
            # matching strong hash does not occur at the first match, it will
            # be missed and the data sent over. May fix eventually, but this
            # problem arises very rarely.
            matchblock = remote_weak.index(checksum, matchblock + 1)
            stronghash = hashlib.md5(''.join(window)).hexdigest()

            if remote_strong[matchblock] == stronghash:
                match = True
                delta.append(Element(index=matchblock))

                if datastream.closed:
                    break
                continue

        except ValueError:
            # The weakchecksum did not match
            match = False
            if datastream:
                # Get the next byte and affix to the window
                newchar = datastream.read(1)
                if newchar:
                    window.append(newchar)
                else:
                    # No more data from the file; the window will slowly shrink.
                    # newchar needs to be zero from here on to keep the checksum
                    # correct.
                    newchar = '\0'
                    tailsize = datastream.tell() % blocksize
                    datastream = None

            if datastream is None and len(window) <= tailsize:
                # The likelihood that any blocks will match after this is
                # nearly nil so call it quits.
                delta.append(Element(data=list(window)))
                break

            # Yank off the extra byte and calculate the new window checksum
            oldchar = window.popleft()
            checksum, a, b = rollingchecksum(oldchar, newchar, a, b, blocksize)

            # Add the old byte the file delta. This is data that was not found
            # inside of a matching block so it needs to be sent to the target.
            if delta:
                delta[-1].data.append(oldchar)
            else:
                delta.append(Element(data=[oldchar]))

    return delta


def blockchecksums(instream, blocksize):
    """
    Returns a list of weak and strong hashes for each block of the
    defined size for the given data stream.
    """
    weakhashes = list()
    stronghashes = list()
    read = instream.read(blocksize)

    while read:
        weakhashes.append(weakchecksum(read)[0])
        stronghashes.append(hashlib.md5(read).hexdigest())
        read = instream.read(blocksize)

    return weakhashes, stronghashes


def patchstream(instream, outstream, delta, blocksize):
    """
    Patches instream using the supplied delta and write the resultant
    data to outstream.
    """
    for element in delta:
        if element.index != -1:
            instream.seek(element.index * blocksize)
            data = instream.read(blocksize)
        else:
            data = ''.join(element.data)
        outstream.write(data)


def rollingchecksum(removed, new, a, b, blocksize):
    """
    Generates a new weak checksum when supplied with the internal state
    of the checksum calculation for the previous window, the removed
    byte, and the added byte.
    """
    a -= ord(removed) - ord(new)
    b -= ord(removed) * blocksize - a
    return (b << 16) | a, a, b


def weakchecksum(data):
    """
    Generates a weak checksum from an iterable set of bytes.
    """
    a = b = 0
    l = len(data)

    for i in range(l):
        n = ord(data[i])
        a += n
        b += (l - i)*n

    return (b << 16) | a, a, b

if __name__ == '__main__':
    blocksize = 4096

    # On the system containing the file that needs to be patched
    unpatched = open("testdata/unpatched.file", "rb")
    hashes = blockchecksums(unpatched, blocksize)

    # On the remote system after having received `hashes`
    patchedfile = open("testdata/patched.file", "rb")
    delta = rsyncdelta(patchedfile, hashes, blocksize)

    # System with the unpatched file after receiving `delta`
    unpatched.seek(0)
    save_to = open("testdata/locally-patched.file", "wb")
    patchstream(unpatched, save_to, delta, blocksize)
