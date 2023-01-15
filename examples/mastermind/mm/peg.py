from . import colour

""" copyright Sean McCarthy, license GPL v2 or later """

class Peg:
    """Class representing a (coloured) peg on the mastermind board"""

    def __init__(self,colour=None):
    	self.__colour = colour

    def setColour(self, colour):
        self.__colour = colour

    def getColour(self):
        return self.__colour

    def equals(self,peg):
        return peg.getColour() == self.__colour

    def display(self):
        print(str(colour.getColourName(self.__colour)).rjust(6), end=' ')

