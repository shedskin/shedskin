""" copyright Sean McCarthy, license GPL v2 or later """

def getColourName(i):
    if i == 0:
        return "red"
    elif i == 1:
        return "green"
    elif i == 2:
        return "purple"
    elif i == 3:
        return "yellow"
    elif i == 4:
        return "white"
    elif i == 5:
        return "black"

class Colours:
    numberOfColours = 6
    red = 0
    green = 1
    purple = 2
    yellow = 3
    white = 4
    black = 5 

    def getNumberOfColours(self):
        return self.numberOfColours

