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

from com.github.tarsa.tarsalzp.prelude.Streams import *
from com.github.tarsa.tarsalzp.core.Coder import Coder
from Options import Options
from sys import stderr
import sys
from time import time

__author__ = 'Piotr Tarsa'

class Main(object):
    def err(self, string):
        stderr.write(string + "\n")

    def printHelp(self):
        self.err("Syntax: command [option=value]*")
        self.err("Commands:")
        self.err("\t[no command]  - print help and show GUI")
        self.err("\tencode        - encode input")
        self.err("\tdecode        - decode compressed stream")
        self.err("\tshowOptions   - read and show compression options only")
        self.err("General options:")
        self.err("\tfi=fileName   - read from file `fileName` (all modes)")
        self.err(
            "\tfo=fileName   - write to file `fileName` (encode and decode)")
        self.err("Encoding only options (with default values):")
        options = Options.getDefault()
        self.err("\tlzpLowContextLength=" + str(options.lzpLowContextLength))
        self.err("\tlzpLowMaskSize=" + str(options.lzpLowMaskSize))
        self.err("\tlzpHighContextLength=" + str(options.lzpHighContextLength))
        self.err("\tlzpHighMaskSize=" + str(options.lzpHighMaskSize))
        self.err("\tliteralCoderOrder=" + str(options.literalCoderOrder))
        self.err("\tliteralCoderInit=" + str(options.literalCoderInit))
        self.err("\tliteralCoderStep=" + str(options.literalCoderStep))
        self.err("\tliteralCoderLimit=" + str(options.literalCoderLimit))

    def printError(self, cause):
        self.err("Error happened.")
        if (cause is not None) and (len(cause.strip()) > 0):
            self.err(cause)
        self.err("")
        self.printHelp()

    def convertOptions(self, args):
        optionsMap = {}
        for arg in args[2:]:
            splitPoint = arg.find("=")
            if splitPoint == -1:
                return None
            if optionsMap.has_key(arg[:splitPoint]):
                return None
            optionsMap[arg[:splitPoint]] = arg[splitPoint + 1:]
        return optionsMap

    def encode(self, optionsMap):
        inputStream = BufferedInputStream(sys.stdin)
        outputStream = BufferedOutputStreamWrapper(FileOutputStream(sys.stdout))
        standardInput = True
        standardOutput = True
        options = Options.getDefault()
        for keyOriginal in optionsMap:
            key = keyOriginal.lower()
            if key == "fi":
                fileHandle = open(optionsMap[keyOriginal], "rb")
                inputStream = BufferedInputStream(fileHandle)
                standardInput = False
            elif key == "fo":
                fileName = optionsMap[keyOriginal]
                outputStream = BufferedOutputStreamWrapper(
                    DelayedFileOutputStream(fileName))
                standardOutput = False
            elif key == "lzpLowContextLength".lower():
                options.lzpLowContextLength = int(optionsMap[keyOriginal])
            elif key == "lzpLowMaskSize".lower():
                options.lzpLowMaskSize = int(optionsMap[keyOriginal])
            elif key == "lzpHighContextLength".lower():
                options.lzpHighContextLength = int(optionsMap[keyOriginal])
            elif key == "lzpHighMaskSize".lower():
                options.lzpHighMaskSize = int(optionsMap[keyOriginal])
            elif key == "literalCoderOrder".lower():
                options.literalCoderOrder = int(optionsMap[keyOriginal])
            elif key == "literalCoderInit".lower():
                options.literalCoderInit = int(optionsMap[keyOriginal])
            elif key == "literalCoderStep".lower():
                options.literalCoderStep = int(optionsMap[keyOriginal])
            elif key == "literalCoderLimit".lower():
                options.literalCoderLimit = int(optionsMap[keyOriginal])
            else:
                self.err("Not suitable or unknown option: " + keyOriginal)
                return
        if not options.isValid():
            self.err("Wrong encoding options combination.")
            return
        Coder.encode(inputStream, outputStream, 65536, options)
        outputStream.flush()
        if not standardInput:
            inputStream.close()
        if not standardOutput:
            outputStream.close()

    def decode(self, optionsMap):
        inputStream = BufferedInputStream(sys.stdin)
        outputStream = BufferedOutputStreamWrapper(FileOutputStream(sys.stdout))
        standardInput = True
        standardOutput = True
        for keyOriginal in optionsMap:
            key = keyOriginal.lower()
            if key == "fi":
                fileHandle = open(optionsMap[keyOriginal], "rb")
                inputStream = BufferedInputStream(fileHandle)
                standardInput = False
            elif key == "fo":
                fileName = optionsMap[keyOriginal]
                outputStream = BufferedOutputStreamWrapper(
                    DelayedFileOutputStream(fileName))
                standardOutput = False
            else:
                self.err("Not suitable or unknown option: " + keyOriginal)
                return
        Coder.decode(inputStream, outputStream, 65536)
        outputStream.flush()
        allDecoded = inputStream.readByte() == -1
        if not standardInput:
            inputStream.close()
        if not standardOutput:
            outputStream.close()
        if not allDecoded:
            raise IOError("Not entire input was decoded.")

    def showOptions(self, optionsMap):
        inputStream = BufferedInputStream(sys.stdin)
        standardInput = True
        for keyOriginal in optionsMap:
            key = keyOriginal.lower()
            if key == "fi":
                fileHandle = open(optionsMap[keyOriginal], "rb")
                inputStream = BufferedInputStream(fileHandle)
                standardInput = False
            else:
                self.err("Not suitable or unknown option: " + keyOriginal)
                return
        options = Coder.getOptions(inputStream)
        self.err(repr(options))
        if not standardInput:
            inputStream.close()

    def dispatchCommand(self, args):
        command = args[1]
        optionsMap = self.convertOptions(args)
        if optionsMap is None:
            self.err("Duplicated or wrongly formatted options.")
        elif "encode" == command.lower():
            self.encode(optionsMap)
        elif "decode" == command.lower():
            self.decode(optionsMap)
        elif "showOptions".lower() == command.lower():
            self.showOptions(optionsMap)
        else:
            self.err("Unknown command: " + command)

    def run(self, args):
        self.err("TarsaLZP")
        self.err("Author: Piotr Tarsa")
        self.err("")
        if len(args) == 1:
            self.printHelp()
        else:
            try:
                self.dispatchCommand(args)
            except MemoryError:
                self.err("Out of memory error - try lowering mask sizes.")

    def main(self):
        start = time()
        self.run(sys.argv)
        self.err("Time taken: " + str(time() - start) + "s")
