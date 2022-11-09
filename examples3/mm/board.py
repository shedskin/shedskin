from . import row

""" copyright Sean McCarthy, license GPL v2 or later """

class Board:
    """Class board, a collection of rows"""

    def __init__(self):
        self.__board = []

    def getRow(self,rownum):
        return self.__board[rownum]

    def addRow(self, row):
        self.__board.append(row)

    def getRows(self):
        return self.__board

