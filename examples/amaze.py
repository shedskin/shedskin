"""
Amaze - A completely object-oriented Pythonic maze generator/solver.
This can generate random mazes and solve them. It should be
able to solve any kind of maze and inform you in case a maze is
unsolveable.

This uses a very simple representation of a mze. A maze is
represented as an mxn matrix with each point value being either
0 or 1. Points with value 0 represent paths and those with
value 1 represent blocks. The problem is to find a path from
point A to point B in the matrix.

The matrix is represented internally as a list of lists.

Have fun :-)
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496884
"""
import sys
import random

class MazeReaderException(Exception):
    pass

STDIN = 0
FILE_ = 1
SOCKET = 2

PATH = -1
START = -2
EXIT = -3

class MazeReader(object):

    def __init__(self):
        self.maze_rows = []
        pass

    def readStdin(self):
        print 'Enter a maze'
        print 'You can enter a maze row by row'
        print

        data = raw_input('Enter the dimension of the maze as Width X Height: ')
        w1, h1 = data.split() # XXX SS 
        w, h  = int(w1), int(h1)

        for x in range(h):
            row = ''
            while not row:
                row = raw_input('Enter row number %d: ' % (x+1))
            rowsplit = [int(y) for y in row.split()] # XXX SS
            if len(rowsplit) != w:
                raise MazeReaderException,'invalid size of maze row'
            self.maze_rows.append(rowsplit)

    def readFile(self):
        fname = 'testdata/maze.txt' #raw_input('Enter maze filename: ')
        try:
            f = open(fname)
            lines = f.readlines()
            f.close()
            lines = [ line for line in lines if line.strip() ]
            w = len(lines[0].split())
            for line in lines:
                row = [int(y) for y in line.split()]
                if len(row) != w:
                    raise MazeReaderException, 'Invalid maze file - error in maze dimensions'
                else:
                    self.maze_rows.append(row)
        except (IOError, OSError), e:
            raise MazeReaderException, str(e)

    def getData(self):
        return self.maze_rows

    def readMaze(self, source=STDIN):
        if source==STDIN:
            self.readStdin()
        elif source == FILE_:
            self.readFile()

        return self.getData()

class MazeFactory(object):
    def makeMaze(self, source=STDIN):
        reader = MazeReader()
        return Maze(reader.readMaze(source))

class MazeError(Exception):
    pass

class Maze(object):
    def __init__(self, rows=[[]]):
        self._rows = rows
        self.__validate()
        self.__normalize()

    def __str__(self):
        s = '\n'
        for row in self._rows:
            for item in row:
                if item == PATH: sitem = '*'
                elif item == START: sitem = 'S'
                elif item == EXIT: sitem = 'E'
                else: sitem = str(item)

                s = ''.join((s,'  ',sitem,'   '))
            s = ''.join((s,'\n\n'))

        return s

    def __validate(self):
        width = len(self._rows[0])
        widths = [len(row) for row in self._rows]
        if widths.count(width) != len(widths):
            raise MazeError, 'Invalid maze!'

        self._height = len(self._rows)
        self._width = width

    def __normalize(self):
        for x in range(len(self._rows)):
            row = self._rows[x]
            row = [min(int(y), 1) for y in row] #map(lambda x: min(int(x), 1), row) # SS
            self._rows[x] = row

    def validatePoint(self, pt):
        x,y = pt
        w = self._width
        h = self._height

        # Don't support Pythonic negative indices
        if x > w - 1 or x<0:
            raise MazeError, 'x co-ordinate out of range!'

        if y > h - 1 or y<0:
            raise MazeError, 'y co-ordinate out of range!'

        pass # SS

    def getItem(self, x, y):
        self.validatePoint((x,y))

        w = self._width
        h = self._height

        row = self._rows[h-y-1]
        return row[x]

    def setItem(self, x, y, value):
        h = self._height

        self.validatePoint((x,y))
        row = self._rows[h-y-1]
        row[x] = value

    def getNeighBours(self, pt):
        self.validatePoint(pt)

        x,y = pt

        h = self._height
        w = self._width

        poss_nbors = (x-1,y),(x-1,y+1),(x,y+1),(x+1,y+1),(x+1,y),(x+1,y-1),(x,y-1),(x-1,y-1)

        nbors = []
        for xx,yy in poss_nbors:
            if (xx>=0 and xx<=w-1) and (yy>=0 and yy<=h-1):
                nbors.append((xx,yy))

        return nbors

    def getExitPoints(self, pt):
        exits = []
        for xx,yy in self.getNeighBours(pt):
            if self.getItem(xx,yy)==0: # SS
                exits.append((xx,yy))

        return exits

    def calcDistance(self, pt1, pt2):
        self.validatePoint(pt1)
        self.validatePoint(pt2)

        x1,y1 = pt1
        x2,y2 = pt2

        return pow( (pow((x1-x2), 2) + pow((y1-y2),2)), 0.5)

class MazeSolver(object):
    def __init__(self, maze):
        self.maze = maze
        self._start = (0,0)
        self._end = (0,0)
        self._current = (0,0)
        self._steps = 0
        self._path = []
        self._tryalternate = False
        self._trynextbest = False
        self._disputed = (0,0)
        self._loops = 0
        self._retrace = False
        self._numretraces = 0

    def setStartPoint(self, pt):
        self.maze.validatePoint(pt)
        self._start = pt

    def setEndPoint(self, pt):
        self.maze.validatePoint(pt)
        self._end = pt

    def boundaryCheck(self):
        exits1 = self.maze.getExitPoints(self._start)
        exits2 = self.maze.getExitPoints(self._end)

        if len(exits1)==0 or len(exits2)==0:
            return False

        return True

    def setCurrentPoint(self, point):
        self._current = point
        self._path.append(point)

    def isSolved(self):
        return (self._current == self._end)

    def getNextPoint(self):
        points = self.maze.getExitPoints(self._current)

        point = self.getBestPoint(points)

        while self.checkClosedLoop(point):

            if self.endlessLoop():
                print self._loops
                point = None
                break

            point2 = point
            if point==self._start and len(self._path)>2:
                self._tryalternate = True
                break
            else:
                point = self.getNextClosestPointNotInPath(points, point2)
                if not point:
                    self.retracePath()
                    self._tryalternate = True
                    point = self._start
                    break

        return point

    def retracePath(self):
        print 'Retracing...'
        self._retrace = True

        path2 = self._path[:]
        path2.reverse()

        idx = path2.index(self._start)
        self._path += self._path[-2:idx:-1]
        self._numretraces += 1

    def endlessLoop(self):
        if self._loops>100:
            print 'Seems to be hitting an endless loop.'
            return True
        elif self._numretraces>8:
            print 'Seem to be retracing loop.'
            return True

        return False

    def checkClosedLoop(self, point):
        l = range(0, len(self._path)-1, 2)
        l.reverse()

        for x in l:
            if self._path[x] == point:
                self._loops += 1
                return True

        return False

    def getBestPoint(self, points):
        point = self.getClosestPoint(points)
        point2 = point
        altpoint = point

        if point2 in self._path:
            point = self.getNextClosestPointNotInPath(points, point2)
            if not point:
                point = point2

        if self._tryalternate:
            point = self.getAlternatePoint(points, altpoint)
            print 'Trying alternate...',self._current, point

        self._trynextbest = False
        self._tryalternate = False
        self._retrace = False

        return point

    def sortPoints(self, points):
        distances = [self.maze.calcDistance(point, self._end) for point in points]
        distances2 = distances[:]

        distances.sort()

        points2 = [()]*len(points) # SS
        count = 0

        for dist in distances:
            idx = distances2.index(dist)
            point = points[idx]

            while point in points2:
                idx = distances2.index(dist, idx+1)
                point = points[idx]

            points2[count] = point
            count += 1

        return points2

    def getClosestPoint(self, points):
        points2 = self.sortPoints(points)

        closest = points2[0]
        return closest

    def getAlternatePoint(self, points, point):
        points2 = points[:]
        print points2, point

        points2.remove(point)
        if points2:
            return random.choice(points2)

        return None

    def getNextClosestPoint(self, points, point):
        points2 = self.sortPoints(points)
        idx = points2.index(point)

        try:
            return points2[idx+1]
        except:
            return None 

    def getNextClosestPointNotInPath(self, points, point):


        point2 = self.getNextClosestPoint(points, point)
        while point2 in self._path:
            point2 = self.getNextClosestPoint(points, point2)

        return point2

    def solve(self):
        #print 'Starting point is', self._start
        #print 'Ending point is', self._end

        # First check if both start and end are same
        if self._start == self._end:
            print 'Start/end points are the same. Trivial maze.'
            print [self._start, self._end]
            return None

        # Check boundary conditions
        if not self.boundaryCheck():
            print 'Either start/end point are unreachable. Maze cannot be solved.'
            return None

        # Proper maze
        #print 'Maze is a proper maze.'

        # Initialize solver
        self.setCurrentPoint(self._start)

        unsolvable = False

        while not self.isSolved():
            self._steps += 1
            pt = self.getNextPoint()

            if pt:
                self.setCurrentPoint(pt)
            else:
                print 'Dead-lock - maze unsolvable'
                unsolvable = True
                break

        if not unsolvable:
            pass #print 'Solution path is',self._path
        else:
            print 'Path till deadlock is',self._path

        self.printResult()

    def printResult(self):
        """ Print the maze showing the path """

        for x,y in self._path:
            self.maze.setItem(x,y,PATH)

        self.maze.setItem(self._start[0], self._start[1], START)
        self.maze.setItem(self._end[0], self._end[1], EXIT)

        #print 'Maze with solution path'
        #print self.maze


class MazeGame(object):
    def __init__(self):
        self._start = (0,0)
        self._end = (0,0)

    #def createMaze(self):
    #    return None
#
#    def getStartEndPoints(self, maze):
#        return None

    def runGame(self):
        maze = self.createMaze()
        if not maze:
            return None

        #print maze
        self.getStartEndPoints(maze)

        #open('maze.txt','w').write(str(maze))

        solver = MazeSolver(maze)

        #open ('maze_pts.txt','w').write(str(self._start) + ' ' + str(self._end) + '\n')
        solver.setStartPoint(self._start)
        solver.setEndPoint(self._end)
        solver.solve()

class FilebasedMazeGame(MazeGame):

    def createMaze(self):
        f = MazeFactory()
        m = f.makeMaze(FILE_)
        #print m
        return m

    def getStartEndPoints(self, maze):

        while True:
            try:
                #pt1 = raw_input('Enter starting point: ')
                pt1 = '0 4'
                x,y = pt1.split()
                self._start = (int(x), int(y))
                maze.validatePoint(self._start)
                break
            except:
                pass

        while True:
            try:
                pt2 = '5 4' #pt2 = raw_input('Enter ending point: ')
                x,y = pt2.split()
                self._end = (int(x), int(y))
                maze.validatePoint(self._end)
                break
            except:
                pass

game = FilebasedMazeGame()
for x in range(10000):
    game.runGame()
