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
from Lg2 import Lg2

__author__ = 'Piotr Tarsa'

class FsmGenerator(object):
    def __init__(self):
        self.stateTable = array.array("B", (0 for _ in xrange(512)))
        self.LimitX = 20
        self.LimitY = 20
        self.p = 0
        self.freqMask = [-1] * ((self.LimitX + 1) * (self.LimitY + 1) * 3 * 3)
        self.initStates(0, 0, 2, 2)

    def divisor(self, a, b):
        return (Lg2.nLog2(b) >> 3) + (Lg2.nLog2(1950) >> 3) - (12 << 11)

    def repeated(self, a, b):
        return (((a + 1) * 1950) / self.divisor(a, b)) \
        if (b > 0) & (self.divisor(a, b) > 1200) else (a + 1)

    def opposite(self, a, b):
        return ((b * 1950) / self.divisor(a, b)) \
        if (b > 0) & (self.divisor(a, b) > 1200) else b


    def initStates(self, x, y, h1, h0):
        x = min(x, self.LimitX)
        y = min(y, self.LimitY)
        index = ((y * (self.LimitX + 1) + x) * 3 + h1) * 3 + h0
        if self.freqMask[index] == -1:
            self.freqMask[index] = self.p
            c = self.p
            self.p += 1
            self.stateTable[c * 2 + 0] = self.initStates(self.repeated(x, y),
                self.opposite(x, y), h0, 0)
            self.stateTable[c * 2 + 1] = self.initStates(self.opposite(y, x),
                self.repeated(y, x), h0, 1)
        return self.freqMask[index]
