from . import game
from . import code
from . import peg
from . import colour
import re
import sys

""" copyright Sean McCarthy, license GPL v2 or later """

class Mastermind:

    """
        The game of Mastermind

        This class provides a function "play" for invoking a new game.

        The objective of the game is to guess a code composed of 4 coloured
        pegs. The code can be composed of any combination of the six colours
        (red, green, purple, yellow, white, black), and can include duplicates.

        For each guess a result code may be returned composed of black and/or
        white pegs. A black peg indicates a peg of the right colour and in the
        right position. A white peg indicates a peg of the right colour but in
        the wrong position. The arrangement of the pegs does not correspond to
        the pegs in the guess- black pegs will always be shown first, followed
        but white pegs.

        The game ends with either a correct guess or after running out of 
        guesses.
    """

    def play(self,guesses=8):
        self.greeting()
        gm = game.Game(guesses)
        while not gm.isOver():
            print("Guess: ",gm.getTries()+1,"/",gm.getMaxTries())
            gm.makeGuess(self.__readGuess())
            print("--------Board--------")
            self.display(gm)
            print("---------------------")
	
        if gm.isWon():
            print("Congratulations!")
        else:
            print("Secret Code: ", end=' ')
            self.displaySecret(gm)

    def greeting(self):
        print("")
        print("---------------------")
        print("Welcome to Mastermind")
        print("---------------------")
        print("")
        print("Each guess should be 4 colours from any of:")
        print("red yellow green purple black white")
        print("")

    def display(self,game):
        for r in game.getBoard().getRows():
            for p in r.getGuess().getPegs():
                print(str(colour.getColourName(p.getColour())).rjust(6), end=' ')
            print(" | Result:\t", end=' ')
            for p in r.getResult().getPegs():
                print(str(colour.getColourName(p.getColour())).rjust(6), end=' ')
            print("")

    def displaySecret(self,game):
        for p in game.getSecretCode().getPegs():
            print(str(colour.getColourName(p.getColour())).rjust(6), end=' ')

    def __readGuess(self):
        guessPegs = []
        print("Type four (space seperated) colours from:")
        print("[r]ed [y]ellow [g]reen [p]urple [b]lack [w]hite")

        inputOk = False
        while not inputOk:
            colours = re.split("\\s", input("> "), 4)
            for c in colours:
                peg = self.__parseColour(c)
                if peg is not None:
                    guessPegs.append(peg)
            inputOk = (len(guessPegs) == 4)
            if not inputOk:
                print("Invalid input, use colours as stated")
                guessPegs = []
        return code.Code(guessPegs)

    def __parseColour(self,s):
        if (re.search("^r",s) is not None):
            return peg.Peg(colour.Colours.red)
        elif (re.search("^p",s) is not None):
            return peg.Peg(colour.Colours.purple)
        elif (re.search("^g",s) is not None):
            return peg.Peg(colour.Colours.green)
        elif (re.search("^y",s) is not None):
            return peg.Peg(colour.Colours.yellow)
        elif (re.search("^w",s) is not None):
            return peg.Peg(colour.Colours.white)
        elif (re.search("^b",s) is not None):
            return peg.Peg(colour.Colours.black)
        else:
            return None

"""
    Instantiate mastermind and invoke play method to play game

"""

def main():
    m = Mastermind()
    guesses = 8
    if len(sys.argv) > 1 and re.match("\d", sys.argv[1]) is not None:
        guesses = int(sys.argv[1])
    m.play(guesses)

if __name__ == "__main__":
    main()
