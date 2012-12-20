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
from FsmGenerator import FsmGenerator
from Lg2 import Lg2

__author__ = 'Piotr Tarsa'

class Common(object):
    CostScale = 7
    # Calculating states
    StateTable = FsmGenerator().stateTable

    def __init__(self, inputStream, outputStream, options):
        self.inputStream = inputStream
        self.outputStream = outputStream
        self.lzpLowContextLength = options.lzpLowContextLength
        self.lzpLowMaskSize = options.lzpLowMaskSize
        self.lzpHighContextLength = options.lzpHighContextLength
        self.lzpHighMaskSize = options.lzpHighMaskSize
        self.literalCoderOrder = options.literalCoderOrder
        self.literalCoderInit = options.literalCoderInit
        self.literalCoderStep = options.literalCoderStep
        self.literalCoderLimit = options.literalCoderLimit
        # Lempel-Ziv Predictive init
        lzpLowCount = 1 << self.lzpLowMaskSize
        lzpHighCount = 1 << self.lzpHighMaskSize
        self.lzpLowMask = lzpLowCount - 1
        self.lzpHighMask = lzpHighCount - 1
        self.lzpLow = array.array("H", (0xffb5 for _ in xrange(lzpLowCount)))
        self.onlyLowLzp =\
        (self.lzpLowContextLength == self.lzpHighContextLength)\
        & (self.lzpLowMaskSize == self.lzpHighMaskSize)
        if self.onlyLowLzp:
            self.lzpHigh = None
        else:
            self.lzpHigh = array.array("H",
                (0xffb5 for _ in xrange(lzpHighCount)))
            # Literal coder init
        literalCoderContextMaskSize = 8 * self.literalCoderOrder
        self.rangesSingle = array.array("H",
            (self.literalCoderInit for _ in xrange(1
            << (literalCoderContextMaskSize + 8))))
        self.rangesGrouped = array.array("H",
            (self.literalCoderInit * 16 for _ in xrange(1
            << (literalCoderContextMaskSize + 4))))
        self.rangesTotal = array.array("H",
            (self.literalCoderInit * 256 for _ in xrange(1
            << literalCoderContextMaskSize)))
        self.recentCost = 8 << Common.CostScale + 14
        # Adaptive probability map init
        self.apmLow = array.array("H", (0x4000 for _ in xrange(16 * 256)))
        if self.onlyLowLzp:
            self.apmHigh = None
        else:
            self.apmHigh = array.array("H",
                (0x4000 for _ in xrange(16 * 256)))
        self.historyLow = 0
        self.historyHigh = 0
        self.historyLowMask = 15
        self.historyHighMask = 15
        # Contexts and hashes
        self.lastLiteralCoderContext = 0
        self.context = array.array("B", (0 for _ in xrange(8)))
        self.contextIndex = 0
        self.hashLow = 0
        self.hashHigh = 0
        self.precomputedHashes = array.array("l",
            ((((2166136261 * 16777619) ^ i) * 16777619) & 0x7fffffff
                for i in xrange(256)))

    # Contexts and hashes
    def updateContext(self, input):
        self.contextIndex = (self.contextIndex - 1) & 7
        self.context[self.contextIndex] = input

    def computeLiteralCoderContext(self):
        self.lastLiteralCoderContext = self.context[self.contextIndex]
        if self.literalCoderOrder == 2:
            self.lastLiteralCoderContext = (self.lastLiteralCoderContext << 8)\
            + self.context[(self.contextIndex + 1) & 7]

    def computeHashesOnlyLowLzp(self):
        localIndex = (self.contextIndex + 1) & 7
        hash = self.precomputedHashes[self.context[self.contextIndex]]
        i = 1
        while True:
            hash ^= self.context[localIndex]
            localIndex = (localIndex + 1) & 7
            i += 1
            if i == self.lzpLowContextLength:
                break
            hash *= 16777619
            hash &= 0x3fffffff
        self.hashLow = hash & self.lzpLowMask

    def computeHashes(self):
        localIndex = (self.contextIndex + 1) & 7
        hash = self.precomputedHashes[self.context[self.contextIndex]]
        i = 1
        while True:
            hash ^= self.context[localIndex]
            localIndex = (localIndex + 1) & 7
            i += 1
            if i == self.lzpLowContextLength:
                break
            hash *= 16777619
            hash &= 0x3fffffff
        self.hashLow = hash & self.lzpLowMask
        while i < self.lzpHighContextLength:
            i += 1
            hash *= 16777619
            hash &= 0x3fffffff
            hash ^= self.context[localIndex]
            localIndex = (localIndex + 1) & 7
        self.hashHigh = hash & self.lzpHighMask

    # Calculating states
    def getNextState(self, state, match):
        return Common.StateTable[state * 2 + (1 if match else 0)]

    # Lempel-Ziv Predictive stuff
    def getLzpStateLow(self):
        return (self.lzpLow[self.hashLow] & 0xff00) >> 8

    def getLzpStateHigh(self):
        return (self.lzpHigh[self.hashHigh] & 0xff00) >> 8

    def getLzpPredictedSymbolLow(self):
        return self.lzpLow[self.hashLow] & 0xff

    def getLzpPredictedSymbolHigh(self):
        return self.lzpHigh[self.hashHigh] & 0xff

    def updateLzpStateLow(self, lzpStateLow, input, match):
        self.lzpLow[self.hashLow] = (self.getNextState(lzpStateLow, match)
                                     << 8) + input

    def updateLzpStateHigh(self, lzpStateHigh, input, match):
        self.lzpHigh[self.hashHigh] = (self.getNextState(lzpStateHigh, match)
                                       << 8) + input

    # Adaptive probability map stuff
    def getApmLow(self, state):
        return self.apmLow[(self.historyLow << 8) + state]

    def getApmHigh(self, state):
        return self.apmHigh[(self.historyHigh << 8) + state]

    def updateApmHistoryLow(self, match):
        self.historyLow = ((self.historyLow << 1) + (0 if match else 1))\
        & self.historyLowMask

    def updateApmHistoryHigh(self, match):
        self.historyHigh = ((self.historyHigh << 1) + (0 if match else 1))\
        & self.historyHighMask

    def updateApmLow(self, state, match):
        index = (self.historyLow << 8) + state
        if match:
            self.apmLow[index] += ((1 << 15) - self.apmLow[index]) >> 7
        else:
            self.apmLow[index] -= self.apmLow[index] >> 7
        self.updateApmHistoryLow(match)

    def updateApmHigh(self, state, match):
        index = (self.historyHigh << 8) + state
        if match:
            self.apmHigh[index] += ((1 << 15) - self.apmHigh[index]) >> 7
        else:
            self.apmHigh[index] -= self.apmHigh[index] >> 7
        self.updateApmHistoryHigh(match)

    # Literal coder stuff
    def rescaleLiteralCoder(self):
        for indexCurrent in xrange(self.lastLiteralCoderContext << 8,
            (self.lastLiteralCoderContext + 1) << 8):
            self.rangesSingle[indexCurrent] -=\
            self.rangesSingle[indexCurrent] >> 1
        totalFrequency = 0
        for groupCurrent in xrange(self.lastLiteralCoderContext << 4,
            (self.lastLiteralCoderContext + 1) << 4):
            groupFrequency = 0
            for indexCurrent in xrange(groupCurrent << 4,
                (groupCurrent + 1) << 4):
                groupFrequency += self.rangesSingle[indexCurrent]
            self.rangesGrouped[groupCurrent] = groupFrequency
            totalFrequency += groupFrequency
        self.rangesTotal[self.lastLiteralCoderContext] = totalFrequency

    def updateLiteralCoder(self, index):
        self.rangesSingle[index] += self.literalCoderStep
        self.rangesGrouped[index >> 4] += self.literalCoderStep
        self.rangesTotal[self.lastLiteralCoderContext]\
        += self.literalCoderStep
        if self.rangesTotal[self.lastLiteralCoderContext]\
        > self.literalCoderLimit:
            self.rescaleLiteralCoder()

    def useFixedProbabilities(self):
        return self.recentCost > 8 << Common.CostScale + 14

    def updateRecentCost(self, symbolFrequency, totalFrequency):
        self.recentCost -= self.recentCost >> Common.CostScale
        self.recentCost += Lg2.nLog2(totalFrequency)
        self.recentCost -= Lg2.nLog2(symbolFrequency)
