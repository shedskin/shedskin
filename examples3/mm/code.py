import random
from . import peg
from . import colour

""" copyright Sean McCarthy, license GPL v2 or later """

class Code:
    """Class representing a collection of pegs"""

    #__defaultCodeSize = 4
    #__pegList = []

    def __init__(self, __pegList=None):
    #    self.__pegList = __pegList
        self.__defaultCodeSize = 4
        self.__pegList = __pegList

    def setPegs(self, __pegList):
        self.__pegList = __pegList

    def setRandomCode(self, codeSize=-1):
        if codeSize == -1:
            codeSize = self.__defaultCodeSize
        random.seed()
        self.__pegList = []
        for i in range(codeSize):
            x = peg.Peg(random.randint(0,colour.Colours.numberOfColours-1))
            self.__pegList.append(x)

    def getPegs(self):
        return self.__pegList

    def equals(self,code):
        c1 = code.getPegs();
        for i in range(4):
            if (not c1[i].equals(self.__pegList[i])):
                return False
        return True

    def compare(self,code):
        resultPegs = []
        secretUsed = [] 
        guessUsed = []
        count = 0
        codeLength = len(self.__pegList)
        for i in range(codeLength):
            secretUsed.append(False)
            guessUsed.append(False)

        """
           Black pegs first: correct colour in correct position

        """
        for i in range(codeLength):
            if (self.__pegList[i].equals(code.getPegs()[i])):
                secretUsed[i] = True
                guessUsed[i] = True
                resultPegs.append(peg.Peg(colour.Colours.black))
                count += 1

        """
           White pegs: trickier

           White pegs are for pegs of the correct colour, but in the wrong
           place. Each peg should only be evaluated once, hence the "used"
           lists.

           Condition below is a shortcut- if there were 3 blacks pegs
           then the remaining peg can't be a correct colour (think about it)

        """
        if (count < codeLength-1):
            for i in range(codeLength):
                if (guessUsed[i]):
                    continue
                for j in range(codeLength):
                    if (i != j and not secretUsed[j] \
                    and not guessUsed[i] \
                    and self.__pegList[j].equals(code.getPegs()[i])):
                        resultPegs.append(peg.Peg(colour.Colours.white))
                        secretUsed[j] = True
                        guessUsed[i] = True

        return Code(resultPegs)

