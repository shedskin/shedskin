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

from com.github.tarsa.tarsalzp.prelude.Long import Long
from com.github.tarsa.tarsalzp.Options import Options
from Decoder import Decoder
from Encoder import Encoder

__author__ = 'Piotr Tarsa'

class Coder(object):
    HeaderValue = Long(0x208b, 0xbb9f, 0x5b12, 0x98be)

    @staticmethod
    def getOptions(inputStream):
        header = Long(0, 0, 0, 0)
        for i in xrange(8):
            header.shl8()
            inputByte = inputStream.readByte()
            if inputByte == -1:
                raise IOError("Unexpected end of file.")
            header.d |= inputByte
        if (header.a != Coder.HeaderValue.a) | (header.b
        != Coder.HeaderValue.b) | (header.c != Coder.HeaderValue.c) | (header.d
        != Coder.HeaderValue.d):
            raise IOError("Wrong file header. Probably not a compressed file.")
        return Coder.getOptionsHeaderless(inputStream)

    @staticmethod
    def getOptionsHeaderless(inputStream):
        packedOptions = Long(0, 0, 0, 0)
        for i in xrange(8):
            packedOptions.shl8()
            inputByte = inputStream.readByte()
            if inputByte == -1:
                raise IOError("Unexpected end of file.")
            packedOptions.d |= inputByte
        result = Options.fromPacked(packedOptions)
        if result is None:
            raise ValueError("Invalid compression options.")
        else:
            return result

    @staticmethod
    def checkInterval(intervalLength):
        if intervalLength <= 0:
            raise ValueError("Interval length has to be positive.")

    @staticmethod
    def decode(inputStream, outputStream, intervalLength):
        Coder.checkInterval(intervalLength)
        options = Coder.getOptions(inputStream)
        Coder.decodeRaw(inputStream, outputStream, intervalLength,
            options)

    @staticmethod
    def decodeRaw(inputStream, outputStream, intervalLength, options):
        Coder.checkInterval(intervalLength)
        decoder = Decoder(inputStream, outputStream, options)
        amountProcessed = 0
        while not decoder.decode(intervalLength):
            amountProcessed += intervalLength

    @staticmethod
    def encode(inputStream, outputStream, intervalLength, options):
        Coder.checkInterval(intervalLength)
        encoder = Encoder(inputStream, outputStream, options)
        header = Long(Coder.HeaderValue.a, Coder.HeaderValue.b,
            Coder.HeaderValue.c, Coder.HeaderValue.d)
        for i in xrange(8):
            outputStream.writeByte(header.a >> 8)
            header.shl8()
        packedOptions = options.toPacked()
        for i in xrange(8):
            outputStream.writeByte(packedOptions.a >> 8)
            packedOptions.shl8()
        Coder.doEncode(encoder, intervalLength)

    @staticmethod
    def encodeRaw(inputStream, outputStream, intervalLength, options):
        Coder.checkInterval(intervalLength)
        encoder = Encoder(inputStream, outputStream, options)
        Coder.doEncode(encoder, intervalLength)

    @staticmethod
    def doEncode(encoder, intervalLength):
        amountProcessed = 0
        while not encoder.encode(intervalLength):
            amountProcessed += intervalLength
        encoder.flush()
