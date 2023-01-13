from . import board
from . import row
from . import code

""" copyright Sean McCarthy, license GPL v2 or later """

class Game:
    """Class Game, provides functions for playing"""

    def __init__(self,maxguesses=16):
        secret = code.Code()
        secret.setRandomCode()
        self.__secretCode = secret
        self.__board = board.Board()
        self.__maxguesses = maxguesses
        self.__tries = 0

    def getBoard(self):
        return self.__board

    def getSecretCode(self):
        return self.__secretCode

    def makeGuess(self,guessCode):
        self.__tries += 1
        self.__board.addRow(row.Row(guessCode, self.getResult(guessCode)))

    def getResult(self,guessCode):
        return self.__secretCode.compare(guessCode)

    def lastGuess(self):
        return self.__board.getRow(self.__tries-1).getGuess()

    def isOver(self):
        if self.__tries > 0:
            return self.__tries >= self.__maxguesses \
            or self.lastGuess().equals(self.__secretCode)
        return False

    def isWon(self):
        return self.lastGuess().equals(self.getSecretCode())

    def getTries(self):
        return self.__tries

    def getMaxTries(self):
        return self.__maxguesses

