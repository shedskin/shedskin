#
# Copyright (c) 2012, Piotr Tarsa
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of the author nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import array

__author__ = 'Piotr Tarsa'

class BufferedInputStream(object):
    Limit = 65536
    def __init__(self, input):
        self.input = input
        self.buffer = None
        self.position = 0
        self.limit = 0

    def readByte(self):
        while self.position == self.limit:
            self.position = 0
            self.buffer = array.array("B")
            try:
                self.buffer.fromfile(self.input, BufferedInputStream.Limit)
            except EOFError:
                pass
            self.limit = len(self.buffer)
            if not self.limit:
                return -1
        result = self.buffer[self.position]
        self.position += 1
        return result

    def close(self):
        self.input.close()


class BufferedOutputStreamWrapper(object):
    Limit = 65536
    def __init__(self, outputStream):
        self.outputStream = outputStream
        self.buffer = array.array("B", (0 for _ in xrange(
            BufferedOutputStreamWrapper.Limit)))
        self.position = 0
        self.limit = len(self.buffer)

    def writeByte(self, octet):
        if self.position == self.limit:
            self.flush()
        self.buffer[self.position] = octet
        self.position += 1

    def flush(self):
        self.outputStream.writeByteArray(self.buffer[:self.position])
        self.position = 0

    def close(self):
        self.outputStream.close()

class OutputStream(object):
    pass

class FileOutputStream(OutputStream):
    def __init__(self, fileHandle):
        self.output = fileHandle

    def writeByteArray(self, byteArray):
        byteArray.tofile(self.output)

    def close(self):
        self.output.close()

class DelayedFileOutputStream(OutputStream):
    def __init__(self, fileName):
        self.fileName = fileName
        self.initialized = False
        self.output = None

    def writeByteArray(self, byteArray):
        if not self.initialized:
            self.initialized = True
            self.output = open(self.fileName, "w+b")
        byteArray.tofile(self.output)

    def close(self):
        if self.initialized:
            self.output.close()
