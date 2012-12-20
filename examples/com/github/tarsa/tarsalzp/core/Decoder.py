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

from Common import Common

__author__ = 'Piotr Tarsa'

class Decoder(Common):
    def __init__(self, inputStream, outputStream, options):
        Common.__init__(self, inputStream, outputStream, options)
        self.started = False
        self.nextHighBit = 0
        self.rcBuffer = 0
        self.rcRange = 0

    def inputByte(self):
        inputByte = self.inputStream.readByte()
        if inputByte == -1:
            raise IOError("Unexpected end of file.")
        currentByte = (inputByte >> 1) + (self.nextHighBit << 7)
        self.nextHighBit = inputByte & 1
        return currentByte

    def init(self):
        self.rcBuffer = 0
        for i in xrange(4):
            self.rcBuffer = (self.rcBuffer << 8) + self.inputByte()
        self.rcRange = 0x7fffffff
        self.started = True

    def normalize(self):
        while self.rcRange < 0x00800000:
            self.rcBuffer = (self.rcBuffer << 8) + self.inputByte()
            self.rcRange <<= 8

    def decodeFlag(self, probability):
        self.normalize()
        rcHelper = (self.rcRange >> 15) * probability
        if rcHelper > self.rcBuffer:
            self.rcRange = rcHelper
            return True
        else:
            self.rcRange -= rcHelper
            self.rcBuffer -= rcHelper
            return False

    def decodeSkewed(self):
        self.normalize()
        if self.rcBuffer < self.rcRange - 1:
            self.rcRange -= 1
            return True
        else:
            self.rcBuffer = 0
            self.rcRange = 1
            return False

    def decodeSingleOnlyLowLzp(self):
        self.computeHashesOnlyLowLzp()
        lzpStateLow = self.getLzpStateLow()
        predictedSymbolLow = self.getLzpPredictedSymbolLow()
        modelLowFrequency = self.getApmLow(lzpStateLow)
        matchLow = self.decodeFlag(modelLowFrequency)
        self.updateApmLow(lzpStateLow, matchLow)
        nextSymbol = predictedSymbolLow if matchLow else\
        self.decodeSymbol(predictedSymbolLow)
        self.updateLzpStateLow(lzpStateLow, nextSymbol, matchLow)
        self.updateContext(nextSymbol)
        return nextSymbol

    def decodeSingle(self):
        self.computeHashes()
        lzpStateLow = self.getLzpStateLow()
        predictedSymbolLow = self.getLzpPredictedSymbolLow()
        modelLowFrequency = self.getApmLow(lzpStateLow)
        lzpStateHigh = self.getLzpStateHigh()
        predictedSymbolHigh = self.getLzpPredictedSymbolHigh()
        modelHighFrequency = self.getApmHigh(lzpStateHigh)
        if modelLowFrequency >= modelHighFrequency:
            matchLow = self.decodeFlag(modelLowFrequency)
            self.updateApmLow(lzpStateLow, matchLow)
            nextSymbol = predictedSymbolLow if matchLow else\
            self.decodeSymbol(predictedSymbolLow)
            self.updateLzpStateLow(lzpStateLow, nextSymbol, matchLow)
            matchHigh = nextSymbol == predictedSymbolHigh
            self.updateApmHistoryHigh(matchHigh)
            self.updateLzpStateHigh(lzpStateHigh, nextSymbol, matchHigh)
        else:
            matchHigh = self.decodeFlag(modelHighFrequency)
            self.updateApmHigh(lzpStateHigh, matchHigh)
            nextSymbol = predictedSymbolHigh if matchHigh else\
            self.decodeSymbol(predictedSymbolHigh)
            self.updateLzpStateHigh(lzpStateHigh, nextSymbol, matchHigh)
            matchLow = nextSymbol == predictedSymbolLow
            self.updateApmHistoryLow(matchLow)
            self.updateLzpStateLow(lzpStateLow, nextSymbol, matchLow)
        self.updateContext(nextSymbol)
        return nextSymbol

    def decodeSymbol(self, mispredictedSymbol):
        self.normalize()
        self.computeLiteralCoderContext()
        if not self.useFixedProbabilities():
            mispredictedSymbolFrequency =\
            self.rangesSingle[(self.lastLiteralCoderContext << 8)\
            + mispredictedSymbol]
            self.rcRange /=\
            self.rangesTotal[self.lastLiteralCoderContext]\
            - mispredictedSymbolFrequency
            self.rangesSingle[(self.lastLiteralCoderContext << 8)
            + mispredictedSymbol] = 0
            self.rangesGrouped[((self.lastLiteralCoderContext << 8)
            + mispredictedSymbol) >> 4] -= mispredictedSymbolFrequency
            rcHelper = self.rcBuffer / self.rcRange
            cumulativeFrequency = rcHelper
            index = self.lastLiteralCoderContext << 4
            while rcHelper >= self.rangesGrouped[index]:
                rcHelper -= self.rangesGrouped[index]
                index += 1
            index <<= 4
            while rcHelper >= self.rangesSingle[index]:
                rcHelper -= self.rangesSingle[index]
                index += 1
            self.rcBuffer -= (cumulativeFrequency - rcHelper) * self.rcRange
            self.rcRange *= self.rangesSingle[index]
            nextSymbol = index & 0xff
            self.rangesSingle[(self.lastLiteralCoderContext << 8)
            + mispredictedSymbol] = mispredictedSymbolFrequency
            self.rangesGrouped[
            ((self.lastLiteralCoderContext << 8) + mispredictedSymbol)
            >> 4] += mispredictedSymbolFrequency
        else:
            self.rcRange /= 255
            rcHelper = self.rcBuffer / self.rcRange
            self.rcBuffer -= rcHelper * self.rcRange
            nextSymbol = rcHelper + (1 if rcHelper >= mispredictedSymbol else 0)
            index = (self.lastLiteralCoderContext << 8) + nextSymbol
        self.updateRecentCost(self.rangesSingle[index],
            self.rangesTotal[self.lastLiteralCoderContext])
        self.updateLiteralCoder(index)
        return nextSymbol

    def decode(self, limit):
        if not self.started:
            self.init()
        endReached = False
        for i in xrange(limit):
            endReached = not self.decodeSkewed()
            if not endReached:
                symbol = self.decodeSingleOnlyLowLzp() if self.onlyLowLzp else\
                self.decodeSingle()
                self.outputStream.writeByte(symbol)
            else:
                break
        return endReached
