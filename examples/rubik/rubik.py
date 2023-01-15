import random
random.seed(1)

# found here: http://pastebin.com/KwGMujyB
# adapted to compile with shedskin by mark dufour

class face(object):
    def __init__(self, name, value):
        self.struc = []
        self.name = name
        self.value = value
        for x in range(3):
            self.struc.append([])
            for y in range(3):
                self.struc[x].append(value)
        
    def num2coord(self, num):
        return (num / 3, num % 3)

    def coord2num(self, coord):
        row, col = coord
        # return row*3 + col
        return int(row)*3 + int(col)

    def getUpFacePos(self, frontFace, row, col):
        if frontFace == self.FRONT or frontFace == self.UP or frontFace == self.DOWN:
            return (row, col)
        elif frontFace == self.BACK:
            return self.num2coord(8 - self.coord2num((row,col)))
        elif frontFace == self.LEFT:
            cmap = [2,5,8,1,4,7,0,3,6]
            return self.num2coord(cmap[self.coord2num((row,col))])
        elif frontFace == self.RIGHT:
            cmap = [6,3,0,7,4,1,8,5,2]
            return self.num2coord(cmap[self.coord2num((row,col))])
        
    def getDownFacePos(self, frontFace, row, col):
        if frontFace == self.FRONT or frontFace == self.UP or frontFace == self.DOWN:
            return (row, col)
        elif frontFace == self.BACK:
            return self.num2coord(8 - self.coord2num((row,col)))
        elif frontFace == self.LEFT:
            cmap = [6,3,0,7,4,1,8,5,2]
            return self.num2coord(cmap[self.coord2num((row,col))])
        elif frontFace == self.RIGHT:
            cmap = [2,5,8,1,4,7,0,3,6]
            return self.num2coord(cmap[self.coord2num((row,col))])

    def getPosFromUp(self, row, col):
        if self == self.FRONT or self == self.UP or self == self.DOWN:
            return (row, col)
        elif self == self.BACK:
            return self.num2coord(8 - self.coord2num((row,col)))
        elif self == self.LEFT:
            cmap = [6,3,0,7,4,1,8,5,2]
            return self.num2coord(cmap[self.coord2num((row,col))])
        elif self == self.RIGHT:
            cmap = [2,5,8,1,4,7,0,3,6]
            return self.num2coord(cmap[self.coord2num((row,col))])

    def getPosFromDown(self, row, col):
        if self == self.FRONT or self == self.UP or self == self.DOWN:
            return (row, col)
        elif self == self.BACK:
            return self.num2coord(8 - self.coord2num((row,col)))
        elif self == self.LEFT:
            cmap = [2,5,8,1,4,7,0,3,6]
            return self.num2coord(cmap[self.coord2num((row,col))])
        elif self == self.RIGHT:
            cmap = [6,3,0,7,4,1,8,5,2]
            return self.num2coord(cmap[self.coord2num((row,col))])

    def getCoords(self, key):
        x,y = self.num2coord(key[1])
        if key[0] == self.UP:
            x,y = self.getPosFromUp(x, y)
        elif key[0] == self.DOWN:
            x,y = self.getPosFromDown(x, y)
        elif self == self.UP:
            x,y = self.getUpFacePos(key[0], x, y)
        elif self == self.DOWN:
            x,y = self.getDownFacePos(key[0], x, y)

        # return (x,y)
        return (int(x), int(y))

    def __getitem__(self, key):
        x,y = self.getCoords(key)
        return self.struc[x][y]
    
    def __setitem__(self, key, value):
        x,y = self.getCoords(key)
        self.struc[x][y] = value

    def __len__(self):
        return 3

    def __str__(self):
        return str(self.struc)

    def __repr__(self):
        return str(self)

    def isSolved(self):
        c = self.struc[0][0]
        for x in self.struc:
            for y in x:
                if c != y: return False
        return True

    def listRep(self, frontFace):
        r = []
        for i in range(9):
            r.append(self[frontFace, i])
        return r

    def reOrder(self, frontFace, newOrder):
        oldDat = self.listRep(frontFace)
        for i in range(9):
            self[frontFace, i] = oldDat[newOrder[i]]

class cube(object):
    def __init__(self):
        W, R, B, O, G, Y = list(range(6))
        self.colors = [W, Y, R, O, G, B] # F, B, L, R, U, D
        self.colLet = {W:"W", R:"R", B:"B", O:"O", G:"G", Y:"Y"}
        self.lastFace = None
        self.recording = False

        self.moveList = []

        faces = ["F", "B", "L", "R", "U", "D"]
        self.faces = []
        for i in range(len(self.colors)):
            f = face(faces[i], self.colors[i])
            self.faces.append(f)
        for f in self.faces:
            f.FRONT, f.BACK, f.LEFT, f.RIGHT, f.UP, f.DOWN = self.faces
        self.FRONT, self.BACK, self.LEFT, self.RIGHT, self.UP, self.DOWN = self.faces

    def startRecord(self):
        self.moveList = []
        self.recording = True

    def endRecord(self):
        self.recording = False
        
    def getFaces(self, frontFace):
        if not frontFace or frontFace == self.FRONT:
            return self.FRONT, self.BACK, self.LEFT, self.RIGHT, self.UP, self.DOWN
        elif frontFace == self.BACK:
            return self.BACK, self.FRONT, self.RIGHT, self.LEFT, self.UP, self.DOWN
        elif frontFace == self.LEFT:
            return self.LEFT, self.RIGHT, self.BACK, self.FRONT, self.UP, self.DOWN
        elif frontFace == self.RIGHT:
            return self.RIGHT, self.LEFT, self.FRONT, self.BACK, self.UP, self.DOWN
        elif frontFace == self.UP:
            return self.UP, self.DOWN, self.LEFT, self.RIGHT, self.BACK, self.FRONT
        elif frontFace == self.DOWN:
            return self.DOWN, self.UP, self.LEFT, self.RIGHT, self.FRONT, self.BACK

    def inverseMove(self, move):
        return move[0] if len(move)==2 else (move+"'")
        
    def turn(self, face, clockwise=True):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(face)
        if self.recording:
            g = "%s%s" % (face.name, "" if clockwise else "'")
            self.moveList.append(g)
            f = True
            while f:
                f = False
                if len(self.moveList) > 1:
                    if self.moveList[-1] == self.inverseMove(self.moveList[-2]):
                        self.moveList.pop(); self.moveList.pop()
                        f = True
                if len(self.moveList) > 2:
                    if self.moveList[-1] == self.moveList[-2] == self.moveList[-3]:
                        self.moveList.pop(); self.moveList.pop()
                        self.moveList[-1] = self.inverseMove(self.moveList[-1])
                        f = True
        if clockwise:
            lRep = LEFT.listRep(FRONT)
            rRep = RIGHT.listRep(FRONT)
            uRep = UP.listRep(FRONT)
            dRep = DOWN.listRep(FRONT)

            #FRONT
            FRONT.reOrder(FRONT, [6,3,0,7,4,1,8,5,2])
            #LEFT
            LEFT[FRONT, 2] = dRep[0]
            LEFT[FRONT, 5] = dRep[1]
            LEFT[FRONT, 8] = dRep[2]
            #DOWN
            DOWN[FRONT, 0] = rRep[6]
            DOWN[FRONT, 1] = rRep[3]
            DOWN[FRONT, 2] = rRep[0]
            #RIGHT
            RIGHT[FRONT, 0] = uRep[6]
            RIGHT[FRONT, 3] = uRep[7]
            RIGHT[FRONT, 6] = uRep[8]
            #UP
            UP[FRONT, 6] = lRep[8]
            UP[FRONT, 7] = lRep[5]
            UP[FRONT, 8] = lRep[2]
        else:
            lRep = LEFT.listRep(FRONT)
            rRep = RIGHT.listRep(FRONT)
            uRep = UP.listRep(FRONT)
            dRep = DOWN.listRep(FRONT)

            #FRONT
            FRONT.reOrder(FRONT, [2,5,8,1,4,7,0,3,6])
            #LEFT
            LEFT[FRONT, 2] = uRep[8]
            LEFT[FRONT, 5] = uRep[7]
            LEFT[FRONT, 8] = uRep[6]
            #DOWN
            DOWN[FRONT, 0] = lRep[2]
            DOWN[FRONT, 1] = lRep[5]
            DOWN[FRONT, 2] = lRep[8]
            #RIGHT
            RIGHT[FRONT, 0] = dRep[2]
            RIGHT[FRONT, 3] = dRep[1]
            RIGHT[FRONT, 6] = dRep[0]
            #UP
            UP[FRONT, 6] = rRep[0]
            UP[FRONT, 7] = rRep[3]
            UP[FRONT, 8] = rRep[6]
            

    def turnMiddle(self, face):
        if self.recording:
            clockwise = face in (self.RIGHT, self.UP, self.BACK)
            dic = {self.LEFT:"M",self.RIGHT:"M",
                   self.UP:"E",self.DOWN:"E",
                   self.FRONT:"S",self.BACK:"S"}
            g = "%s%s" % (dic[face], "" if clockwise else "'")
            self.moveList.append(g)
            f = True
            while f:
                f = False
                if len(self.moveList) > 1:
                    if self.moveList[-1] == self.inverseMove(self.moveList[-2]):
                        self.moveList.pop(); self.moveList.pop()
                        f = True
                if len(self.moveList) > 2:
                    if self.moveList[-1] == self.moveList[-2] == self.moveList[-3]:
                        self.moveList.pop(); self.moveList.pop()
                        self.moveList[-1] = self.inverseMove(self.moveList[-1])
                        f = True
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(face)
        up = [UP[(FRONT, 3)], UP[(FRONT, 4)], UP[(FRONT, 5)]]
        left = [LEFT[(FRONT, 1)], LEFT[(FRONT, 4)], LEFT[(FRONT, 7)]]
        down = [DOWN[(FRONT, 3)], DOWN[(FRONT, 4)], DOWN[(FRONT, 5)]]
        right = [RIGHT[(FRONT, 1)], RIGHT[(FRONT, 4)], RIGHT[(FRONT, 7)]]

        UP[(FRONT, 3)] = left[2]
        UP[(FRONT, 4)] = left[1]
        UP[(FRONT, 5)] = left[0]

        LEFT[(FRONT, 1)] = down[0]
        LEFT[(FRONT, 4)] = down[1]
        LEFT[(FRONT, 7)] = down[2]

        DOWN[(FRONT, 3)] = right[2]
        DOWN[(FRONT, 4)] = right[1]
        DOWN[(FRONT, 5)] = right[0]

        RIGHT[(FRONT, 1)] = up[0]
        RIGHT[(FRONT, 4)] = up[1]
        RIGHT[(FRONT, 7)] = up[2]
        
        
        

    def randomize(self, turns = 100):
        for i in range(turns):
            if random.random() > .5:
                self.turn(random.choice(self.faces))
            else:
                self.turnMiddle(random.choice(self.faces))
                
    def isSolved(self):
        for f in self.faces:
            if not f.isSolved(): return False
        return True

    def __str__(self):
        x = ""
        for f in self.faces:
            x += l+" : "+str(f)+"\n"
        return x[:-1]

    def strCube(self,face=None,replCol=True):
        faces = self.getFaces(face)
        o = "FBLRUD"
        
        x = """
        U0 U1 U2
        U3 U4 U5   
        U6 U7 U8    
 L0 L1 L2  F0 F1 F2  R0 R1 R2  B0 B1 B2
 L3 L4 L5  F3 F4 F5  R3 R4 R5  B3 B4 B5
 L6 L7 L8  F6 F7 F8  R6 R7 R8  B6 B7 B8
        D0 D1 D2
        D3 D4 D5
        D6 D7 D8
"""
        j = 0
        for face in faces:
            for i in range(9):
                s = "%s%d" % (o[j], i)
                x = x.replace(s, str(face[faces[0], i]))
            j+=1

        if replCol:
            for col in self.colLet: 
                x = x.replace(str(col), self.colLet[col])

        return x

    def getColName(self, num):
        return self.colLet[num]
    
    def __repr__(self):
        return self.strCube(self.UP)

    def primeCube(self, frontFace = None):
        if frontFace is None: frontFace = self.FRONT
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        primeCol = UP[(FRONT, 8)]
        isPrime = False
        stFace = FRONT
        i = 0
        while UP[(FRONT, 8)] != UP[(FRONT, 4)] and i < 4:
            self.turnMiddle(FRONT)
            i+=1
        if UP[(FRONT, 8)] != UP[(FRONT, 4)]:
            i = 0
            while UP[(FRONT, 8)] != UP[(FRONT, 4)] and i < 4:
                self.turnMiddle(LEFT)
                i += 1
        if UP[(FRONT, 8)] == UP[(FRONT, 4)]:
            return FRONT
        else:
            return None

    def cornerHasColsBR(self, frontFace, needColors):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        colors = (FRONT[(FRONT, 8)], RIGHT[(FRONT, 6)], DOWN[(FRONT, 2)])
        cnt = 0
        for color in needColors:
            if color in colors:
                cnt += 1
        return cnt >= 2

    def cornerHasColsTR(self, frontFace, needColors):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        colors = (FRONT[(FRONT, 2)],
                RIGHT[(FRONT, 0)],
                UP[(FRONT, 8)])
        cnt = 0
        for color in needColors:
            if color in colors:
                cnt += 1
        return cnt >= 2

    def cornerHasColsTL(self, frontFace, needColors):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        colors = (FRONT[(FRONT, 0)],
                LEFT[(FRONT, 2)],
                UP[(FRONT, 6)])
        cnt = 0
        for color in needColors:
            if color in colors:
                cnt += 1
        return cnt >= 2

    def stepOneCompleteFace(self, frontFace, upCol):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        f0 = FRONT[(FRONT, 0)]
        f1 = FRONT[(FRONT, 2)]
        u0 = UP[(FRONT, 6)]
        u1 = UP[(FRONT, 8)]
        return (u0 == upCol) and (u0 == u1) and (f0 == f1)
    
    def stepOne(self, frontFace=None, check=True):
        counter = 0
        skip = []
        completedFaces = []
        if frontFace is None: frontFace = self.FRONT
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        # Assume we just primed
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
        upCol = UP[(FRONT, 4)]
        skipCount = 0
        while counter < 20 and len(completedFaces) < 4:

            if self.stepOneCompleteFace(FRONT, upCol): # XXX
                if FRONT not in completedFaces: completedFaces.append(FRONT)
                #print "%s is completed" % FRONT
                FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
                continue
            needCols = (upCol, FRONT[FRONT, 0])
            if FRONT[(FRONT, 2)] == upCol and self.cornerHasColsTR(FRONT, needCols): # Algo 4 # XXX
                #print "Using Algo 4"
                self.turn(FRONT)
                self.turn(DOWN)
                self.turn(FRONT, False)
                self.turn(DOWN)
                self.turn(DOWN)
                self.turn(RIGHT, False)
                self.turn(DOWN)
                self.turn(RIGHT)
                if self.stepOneCompleteFace(FRONT, upCol): # XXX
                    completedFaces.append(FRONT)
                else:
                    #print "Algo failed."
                    FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            elif RIGHT[(FRONT, 0)] == upCol and self.cornerHasColsTR(FRONT, needCols): # Algo 5 # XXX
                #print "Using Algo 5"
                self.turn(RIGHT, False)
                self.turn(DOWN, False)
                self.turn(RIGHT)
                self.turn(DOWN)
                self.turn(RIGHT, False)
                self.turn(DOWN, False)
                self.turn(RIGHT)
                if self.stepOneCompleteFace(FRONT, upCol): # XXX
                    completedFaces.append(FRONT)
                else:
                    #print "Algo failed."
                    FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            else:
                foundCorner = True
                i = 0
                while not self.cornerHasColsBR(FRONT, needCols) and i < 4: # XXX
                    self.turn(DOWN)
                    i += 1
                if i == 4 and not self.cornerHasColsBR(FRONT, needCols): # XXX
                    foundCorner = False
                if foundCorner and RIGHT[(FRONT, 6)] == upCol: # Algo 1
                    #print "Using Algo 1"
                    self.turn(RIGHT, False)
                    self.turn(DOWN, False)
                    self.turn(RIGHT)
                    
                    if self.stepOneCompleteFace(FRONT, upCol): # XXX
                        completedFaces.append(FRONT)
                    else:
                        #print "Algo failed."
                        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
                elif foundCorner and FRONT[(FRONT, 8)] == upCol: # Algo 2
                    #print "Using Algo 2"
                    self.turn(DOWN, False)
                    self.turn(RIGHT, False)
                    self.turn(DOWN)
                    self.turn(RIGHT)
                    if self.stepOneCompleteFace(FRONT, upCol): # XXX
                        completedFaces.append(FRONT)
                    else:
                        #print "Algo failed."
                        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
                elif foundCorner and DOWN[(FRONT, 2)] == upCol: # Algo 3
                    #print "Using Algo 3"
                    self.turn(RIGHT, False)
                    self.turn(DOWN)
                    self.turn(RIGHT)
                    self.turn(DOWN)
                    self.turn(DOWN)
                    self.turn(RIGHT, False)
                    self.turn(DOWN, False)
                    self.turn(RIGHT)
                    if self.stepOneCompleteFace(FRONT, upCol): # XXX
                        completedFaces.append(FRONT)
                    else:
                        #print "Algo failed."
                        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
                else:
                    #print "Skipping Face", FRONT
                    skipCount += 1
                    if skipCount == 3:
                        self.turn(RIGHT)
                        self.turn(DOWN)
                        skipCount = 0
                    #return False
                    FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            counter += 1
        if self.stepOneComplete(FRONT):
            self.lastFace = FRONT
            return FRONT
        elif check:
            return self.stepOne(frontFace, False) # XXX
        else:
            return None


    def stepOneComplete(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        midCol = UP[(UP, 4)]
        if UP[(UP, 0)] != midCol: return False
        if UP[(UP, 2)] != midCol: return False
        if UP[(UP, 6)] != midCol: return False
        if UP[(UP, 8)] != midCol: return False
        for i in range(4):
            if FRONT[(FRONT, 0)] != FRONT[(FRONT, 2)]: return False
            FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
        return True

    def stepTwo(self, frontFace, check=True):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        if not self.stepOneComplete(FRONT):
            raise RuntimeError("Step 2 conditions not met.")
        upCol = UP[(FRONT, 4)]

        i = 0
        while not self.allFirstLayer(FRONT) and i < 128:
            faceCol = FRONT[(FRONT, 0)]
            if DOWN[FRONT, 1] == upCol and FRONT[FRONT, 7] == faceCol:
                self.turnMiddle(LEFT)
                self.turn(DOWN, False)
                self.turn(DOWN, False)
                self.turnMiddle(RIGHT)
            elif FRONT[FRONT, 7] == upCol and DOWN[FRONT, 1] == faceCol:
                self.turn(DOWN, False)
                self.turnMiddle(LEFT)
                self.turn(DOWN)
                self.turnMiddle(RIGHT)
            elif RIGHT[FRONT, 3] == upCol and FRONT[FRONT, 5] == faceCol:
                self.turnMiddle(DOWN)
                self.turn(FRONT)
                self.turnMiddle(UP)
                self.turn(FRONT, False)
            elif FRONT[FRONT, 5] == upCol and RIGHT[FRONT, 3] == faceCol:
                self.turnMiddle(DOWN)
                self.turn(FRONT, False)
                self.turnMiddle(UP)
                self.turnMiddle(UP)
                self.turn(FRONT)
            elif FRONT[FRONT, 1] == upCol and UP[FRONT, 7] == faceCol:
                self.turnMiddle(LEFT)
                self.turn(DOWN, False)
                self.turn(DOWN, False)
                self.turnMiddle(RIGHT)
                self.turn(DOWN, False)
                self.turnMiddle(LEFT)
                self.turn(DOWN)
                self.turnMiddle(RIGHT)
            FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            i += 1
            if i % 4 == 0:
                self.turn(UP)

        if self.allFirstLayer(FRONT):
            return FRONT
        else:
            return None

    def firstLayer(self, face):
        r = True
        lr = face.listRep(face)[:3]
        fc = lr[0]
        for facelet in lr:
            if facelet != fc: r = False; break
        return r

    def allFirstLayer(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        for cFace in [FRONT, RIGHT, BACK, LEFT]:
            if not self.firstLayer(cFace):
                return False
        return True
    
    def firstTwoLayers(self, face):
        r = True
        lr = face.listRep(face)[:6]
        fc = lr[0]
        for facelet in lr:
            if facelet != fc: r = False; break
        return r

    def allFirstTwoLayers(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        for cFace in [FRONT, RIGHT, BACK, LEFT]:
            if not self.firstTwoLayers(cFace):
                return False
        return True
                
    def stepThree(self, frontFace, check=True):
        if not self.allFirstLayer(frontFace):
            raise RuntimeError("Step 3 conditions not met.")
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        while FRONT[FRONT, 1] != FRONT[FRONT, 4]:
            self.turnMiddle(UP)

        i = 0
        j = 0
        perf = False
        while not self.allFirstTwoLayers(frontFace) and j < 64:
            faceCol = FRONT[(FRONT, 4)]
            leftCol = LEFT[(FRONT, 4)]
            rightCol = RIGHT[(FRONT, 4)]
            tCol = FRONT[(FRONT, 7)]
            dCol = DOWN[(FRONT, 1)]
            if tCol == faceCol:
                if dCol == leftCol:
                    self.turn(DOWN)
                    self.turn(LEFT)
                    self.turn(DOWN, False)
                    self.turn(LEFT, False)
                    self.turn(DOWN, False)
                    self.turn(FRONT, False)
                    self.turn(DOWN)
                    self.turn(FRONT)
                    perf = True
                elif dCol == rightCol:
                    self.turn(DOWN, False)
                    self.turn(RIGHT, False)
                    self.turn(DOWN)
                    self.turn(RIGHT)
                    self.turn(DOWN)
                    self.turn(FRONT)
                    self.turn(DOWN, False)
                    self.turn(FRONT, False)
                    perf = True
            FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            i += 1
            if i % 4 == 0:
                j += 1
                if j % 4 == 0:
                    F, B, L, R, U, D = self.getFaces(FRONT)
                    for k in range(4):
                        if F[(F, 3)] != F[(F, 4)] or \
                           L[(F, 5)] != L[(F, 4)]:
                            self.turn(D)
                            self.turn(L)
                            self.turn(D, False)
                            self.turn(L, False)
                            self.turn(D, False)
                            self.turn(F, False)
                            self.turn(D)
                            self.turn(F)
                            break
                        elif F[(F, 5)] != F[(F, 4)] or \
                             R[(F, 3)] != R[(F, 4)]:   
                            self.turn(D, False)
                            self.turn(R, False)
                            self.turn(D)
                            self.turn(R)
                            self.turn(D)
                            self.turn(F)
                            self.turn(D, False)
                            self.turn(F, False)
                            break
                        F, B, L, R, U, D = self.getFaces(R)
                else:
                    self.turn(DOWN)

        return FRONT if self.allFirstTwoLayers(frontFace) else None

    def switch1and2(self, frontFace):
        F, B, L, R, U, D = self.getFaces(frontFace)
        self.turn(L, False)
        self.turn(U, False)
        self.turn(L)
        self.turn(F)
        self.turn(U)
        self.turn(F, False)
        self.turn(L, False)
        self.turn(U)
        self.turn(L)
        self.turn(U)
        self.turn(U)

    def switch1and3(self, frontFace):
        F, B, L, R, U, D = self.getFaces(frontFace)
        self.turn(U)
        self.turn(L, False)
        self.turn(U, False)
        self.turn(L)
        self.turn(F)
        self.turn(U)
        self.turn(F, False)
        self.turn(L, False)
        self.turn(U)
        self.turn(L)
        self.turn(U)

    def colorPos1(self, frontFace):
        F, B, L, R, U, D = self.getFaces(frontFace)
        return (F[(F, 2)],
                U[(F, 8)],
                R[(F, 0)])

    def colorPos2(self, frontFace):
        F, B, L, R, U, D = self.getFaces(frontFace)
        return (F[(F, 0)],
                U[(F, 6)],
                L[(F, 2)])

    def colorPos3(self, frontFace):
        F, B, L, R, U, D = self.getFaces(frontFace)
        return (R[(F, 2)],
                U[(F, 2)],
                B[(F, 0)])

    def colorPos4(self, frontFace):
        F, B, L, R, U, D = self.getFaces(frontFace)
        return (B[(F, 2)],
                U[(F, 0)],
                L[(F, 0)])

    def sameColors(self, one, two):
        for color in one:
            if color not in two: return False
        return True

    def stepFour(self, frontFace):
        if not self.allFirstTwoLayers(frontFace):
            raise RuntimeError("Step 4 conditions not met.")
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        self.turn(FRONT); self.turn(FRONT)
        self.turnMiddle(FRONT); self.turnMiddle(FRONT)
        self.turn(BACK, False); self.turn(BACK, False)

        upCol = UP[(FRONT, 4)]
        needColors = (upCol, FRONT[(FRONT, 4)])

        order = [
            (FRONT[(FRONT, 4)], RIGHT[(FRONT, 4)], UP[(FRONT, 4)]),
            (FRONT[(FRONT, 4)], LEFT[(FRONT, 4)], UP[(FRONT, 4)]),
            (BACK[(FRONT, 4)], RIGHT[(FRONT, 4)], UP[(FRONT, 4)]),
            (BACK[(FRONT, 4)], LEFT[(FRONT, 4)], UP[(FRONT, 4)])
        ]

        while not self.sameColors(self.colorPos4(FRONT), order[3]):
            self.turn(UP)

        cube1 = self.colorPos1(FRONT)
        cube4 = self.colorPos4(FRONT)
        pos = 3
        if not self.sameColors(order[0], cube1):
            if self.sameColors(self.colorPos2(FRONT), order[0]):
                self.switch1and2(FRONT)
            elif self.sameColors(self.colorPos3(FRONT), order[0]):
                self.switch1and3(FRONT)
            else:
                raise RuntimeError("Unexpected order?")

        if not self.sameColors(order[1], self.colorPos2(FRONT)): # 2 and 3 are swapped
            self.switch1and3(FRONT)
            self.switch1and2(FRONT)
            self.switch1and3(FRONT)
            
        
        c = [self.colorPos1(FRONT),self.colorPos2(FRONT),self.colorPos3(FRONT),self.colorPos4(FRONT)]

        for o in range(len(order)):
            if not self.sameColors(order[o], c[o]): print("FAILURE %d" % (o+1))

        while not self.sameColors(self.colorPos1(FRONT), order[0]):
            self.turn(UP)

        return FRONT

    def modelOne(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        return UP[(FRONT, 4)] == UP[(FRONT, 8)] == FRONT[(FRONT, 0)]

    def modelTwo(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        return UP[(FRONT, 4)] == RIGHT[(FRONT, 0)] == RIGHT[(FRONT, 2)]

    def modelThree(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        return UP[(FRONT, 4)] == UP[(FRONT, 8)] == RIGHT[(FRONT, 2)]

    def stepFiveAlgo(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        self.turn(LEFT, False)
        self.turn(UP, False)
        self.turn(LEFT)
        self.turn(UP, False)
        self.turn(LEFT, False)
        self.turn(UP, False)
        self.turn(UP, False)
        self.turn(LEFT)
        self.turn(UP, False)
        self.turn(UP, False)

    def upCornersDone(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        return UP[(FRONT, 0)] == UP[(FRONT, 2)] == \
               UP[(FRONT, 4)] == UP[(FRONT, 6)] == \
               UP[(FRONT, 8)]
        
    def stepFive(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        f = True
        m1 = -1
        while True:
            if self.modelOne(FRONT):
                m1 = 10
                break
            elif self.modelTwo(FRONT):
                m1 = 20
                break
            elif self.modelThree(FRONT):
                m1 = 30
                break
            else:
                if f:
                    self.stepFiveAlgo(FRONT)
                    f = False
                FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
        self.stepFiveAlgo(FRONT)
        while not self.upCornersDone(FRONT):
            if self.modelOne(FRONT) and m1 != 1:
                self.stepFiveAlgo(FRONT)
            elif self.modelTwo(FRONT) and m1 != 2:
                self.stepFiveAlgo(FRONT)
            elif self.modelThree(FRONT) and m1 != 3:
                self.stepFiveAlgo(FRONT)
            else:
                FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
        return FRONT

    def sixAlgo(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        self.turnMiddle(RIGHT)
        self.turn(UP, False)
        self.turnMiddle(LEFT)
        self.turn(UP, False)
        self.turn(UP, False)
        self.turnMiddle(RIGHT)
        self.turn(UP, False)
        self.turnMiddle(LEFT)

    def stepSix(self, frontFace):
        DEDH = 0
        FISH = 1
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        j = 0
        while not self.isSolved() and j < 15:
            pairs = []
            for i in range(4):
                if FRONT[(FRONT, 1)] == UP[(FRONT, 4)] and \
                   FRONT[(FRONT, 4)] == UP[(FRONT, 7)]:
            #       and (UP[(FRONT, 4)], FRONT[(FRONT, 4)]) not in pairs: # XXX bug?
                    self.sixAlgo(FRONT)
                    pairs.append(FRONT[(FRONT, 4)])
                FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            if len(pairs) == 0: self.sixAlgo(FRONT)
            pattern = -1
            for i in range(4):
                if UP[(FRONT, 7)] != UP[(FRONT, 4)] and \
                   UP[(FRONT, 5)] != UP[(FRONT, 4)]:
                    pattern = FISH
                    break
                elif UP[(FRONT, 3)] != UP[(FRONT, 4)] and \
                     UP[(FRONT, 5)] != UP[(FRONT, 4)]:
                    pattern = DEDH
                    break
                FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(RIGHT)
            if pattern == FISH:
                self.dedmoreFish(FRONT)
            else:
                self.dedmoreH(FRONT)
            if not self.isSolved():
                self.dedmoreH(FRONT)
            j += 1

        return self.isSolved()

    def solveCube(self):
        self.startRecord()
        faces = [self.FRONT, self.DOWN, self.BACK, self.UP, self.LEFT, self.RIGHT]
        for i in range(50):
            if (i+1) % 3 == 0: self.randomize(5)
            if self.isSolved(): break
            s = self.primeCube(faces[i % len(faces)])
            if not s:
                continue
            if self.isSolved(): break
            s = self.stepOne(s)
            if not s:
                continue
            if self.isSolved(): break
            s = self.stepTwo(s)
            if not s:
                continue
            if self.isSolved(): break
            s = self.stepThree(s)
            if not s:
                continue
            if self.isSolved(): break
            s = self.stepFour(s)
            if not s:
                continue
            if self.isSolved(): break
            s = self.stepFive(s)
            if not s:
                continue
            if self.isSolved(): break
            s2 = self.stepSix(s)
            if not s2:
                continue
            if self.isSolved(): break
        self.endRecord()
        if self.isSolved():
            print("Solved in %d moves." % len(self.moveList))
            print("".join(self.moveList))
        return self.isSolved()

    def dedmoreH(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        self.turn(RIGHT, False)
        self.turnMiddle(UP)
        self.turn(RIGHT, False)
        self.turn(RIGHT, False)
        self.turnMiddle(UP)
        self.turnMiddle(UP)
        self.turn(RIGHT, False)
        self.turn(UP, False)
        self.turn(UP, False)
        self.turn(RIGHT)
        self.turnMiddle(DOWN)
        self.turnMiddle(DOWN)
        self.turn(RIGHT, False)
        self.turn(RIGHT, False)
        self.turnMiddle(DOWN)
        self.turn(RIGHT)
        self.turn(UP, False)
        self.turn(UP, False)

    def dedmoreFish(self, frontFace):
        FRONT, BACK, LEFT, RIGHT, UP, DOWN = self.getFaces(frontFace)
        self.turn(FRONT, False)
        self.turn(LEFT, False)
        self.turn(RIGHT, False)
        self.turnMiddle(UP)
        self.turn(RIGHT, False)
        self.turn(RIGHT, False)
        self.turnMiddle(UP)
        self.turnMiddle(UP)
        self.turn(RIGHT, False)
        self.turn(UP, False) 
        self.turn(UP, False)
        self.turn(RIGHT)
        self.turnMiddle(DOWN)
        self.turnMiddle(DOWN)
        self.turn(RIGHT, False)
        self.turn(RIGHT, False)
        self.turnMiddle(DOWN)
        self.turn(RIGHT)
        self.turn(UP, False)
        self.turn(UP, False)
        self.turn(LEFT)
        self.turn(FRONT)

if __name__ == "__main__":
    print("Rubik's Cube Solver")
    print("Type v to view the cube")
    print("Type r to randomize the cube")
    print("Type s to solve the cube")
    print("Type q to quit")
    c = cube()
    for x in range(100):
        c.randomize()
        print(c.strCube())
        c.solveCube()
#    command = ""
#    while command != "q":
#        command = raw_input(">>> ")[0].lower()
#        if command == "v":
#            print c.strCube()
#        elif command == "r":
#            c.randomize()
#            print "Cube randomized"
#        elif command == "s":
#            c.solveCube()
