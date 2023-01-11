# placed in the public domain by John Eriksson, http://arainyday.se

# Version 1.1
#
# Changes in 1.1:
# In order to optimize the list handling I implemented the location id (lid) attribute.
# This will make the all list serahces to become extremely more optimized.

class Path:
    def __init__(self,nodes, totalCost):
        self.nodes = nodes;
        self.totalCost = totalCost;

    def getNodes(self):
        return self.nodes

    def getTotalMoveCost(self):
        return self.totalCost

class Node:
    def __init__(self,location,mCost,lid,parent=None):
        self.location = location # where is this node located
        self.mCost = mCost # total move cost to reach this node
        self.parent = parent # parent node
        self.score = 0 # calculated score for this node
        self.lid = lid # set the location id - unique for each location in the map

    def __eq__(self, n):
        if n.lid == self.lid:
            return True
        else:
            return False

class AStar:

    def __init__(self,maphandler):
        self.mh = maphandler

    def _getBestOpenNode(self):
        bestNode = None
        for n in self.on:
            if not bestNode:
                bestNode = n
            else:
                if n.score<=bestNode.score:
                    bestNode = n
        return bestNode

    def _tracePath(self,n):
        nodes = []
        totalCost = n.mCost
        p = n.parent
        nodes.insert(0,n)

        while 1:
            if p.parent is None:
                break

            nodes.insert(0,p)
            p=p.parent

        return Path(nodes,totalCost)

    def _handleNode(self,node,end):
        i = self.o.index(node.lid)
        self.on.pop(i)
        self.o.pop(i)
        self.c.append(node.lid)

        nodes = self.mh.getAdjacentNodes(node,end)

        for n in nodes:
            if n.location == end:
                # reached the destination
                return n
            elif n.lid in self.c:
                # already in close, skip this
                continue
            elif n.lid in self.o:
                # already in open, check if better score
                i = self.o.index(n.lid)
                on = self.on[i];
                if n.mCost<on.mCost:
                    self.on.pop(i);
                    self.o.pop(i);
                    self.on.append(n);
                    self.o.append(n.lid);
            else:
                # new node, append to open list
                self.on.append(n);
                self.o.append(n.lid);

        return None

    def findPath(self,fromlocation, tolocation):
        self.o = []
        self.on = []
        self.c = []

        end = tolocation
        fnode = self.mh.getNode(fromlocation)
        self.on.append(fnode)
        self.o.append(fnode.lid)
        nextNode = fnode

        while nextNode is not None:
            finish = self._handleNode(nextNode,end)
            if finish:
                return self._tracePath(finish)
            nextNode=self._getBestOpenNode()

        return None

class SQ_Location:
    """A simple Square Map Location implementation"""
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self, l):
        """MUST BE IMPLEMENTED"""
        if l.x == self.x and l.y == self.y:
            return True
        else:
            return False

class SQ_MapHandler:
    """A simple Square Map implementation"""

    def __init__(self,mapdata,width,height):
        self.m = mapdata
        self.w = width
        self.h = height

    def getNode(self, location):
        """MUST BE IMPLEMENTED"""
        x = location.x
        y = location.y
        if x<0 or x>=self.w or y<0 or y>=self.h:
            return None
        d = self.m[(y*self.w)+x]
        if d == -1:
            return None

        return Node(location,d,((y*self.w)+x))

    def getAdjacentNodes(self, curnode, dest):
        """MUST BE IMPLEMENTED"""
        result = []

        cl = curnode.location
        dl = dest

        n = self._handleNode(cl.x+1,cl.y,curnode,dl.x,dl.y)
        if n: result.append(n)
        n = self._handleNode(cl.x-1,cl.y,curnode,dl.x,dl.y)
        if n: result.append(n)
        n = self._handleNode(cl.x,cl.y+1,curnode,dl.x,dl.y)
        if n: result.append(n)
        n = self._handleNode(cl.x,cl.y-1,curnode,dl.x,dl.y)
        if n: result.append(n)

        return result

    def _handleNode(self,x,y,fromnode,destx,desty):
        n = self.getNode(SQ_Location(x,y))
        if n is not None:
            dx = max(x,destx) - min(x,destx)
            dy = max(y,desty) - min(y,desty)
            emCost = dx+dy
            n.mCost += fromnode.mCost
            n.score = n.mCost+emCost
            n.parent=fromnode
            return n

        return None

if False: # shedskin
    AStar(SQ_MapHandler([1], 1, 1)).findPath(SQ_Location(1,1), SQ_Location(1,1))
