#!/usr/bin/python

"""
conway's game of life, using bill gosper's hashlife algorithm

copyright david bau

http://davidbau.com/archives/2006/07/26/python_curses_life.html
"""

import random


def lifeScore(center, surround):
    "Conway's game of life rules: birth on 3, survival on 2 or 3"
    if surround == 3 or (surround == 2 and center == 1):
        return 1
    return 0


def mapid(tup):
    "Every node gets an integer id; we use tuples of ids to index nodes."
    return [x.id for x in tup]


class LifeNode:
    "A 2^level-square life node"

    def __init__(self, board, id, children):
        "Pass a board, id, and four chidlren.  Id 0 and 1 have no children."
        if id <= 1:
            self.level = 0
            self.count = id
        else:
            nw, ne, sw, se = children
            self.level = nw.level + 1
            self.count = nw.count + ne.count + sw.count + se.count
        self.id = id
        self.children = children
        self.board = board
        self.cache = {}

    def get(self, x, y):
        "Returns the value of the cell at x, y"
        if self.level == 0:
            return self.count
        half = self.width() // 2
        child = self.children[int(x) // half + int(y) // half * 2]
        return child.get(x % half, y % half)

    def getList(self, result, x, y, rect):
        "Returns the coordinates of all the filled cells in the given rect"
        if self.count == 0:
            return
        if rect:
            minx, miny, maxx, maxy = rect
            if (
                x >= maxx
                or x + self.width() <= minx
                or y >= maxy
                or y + self.width() <= miny
            ):
                return
        if self.level == 0:
            result.append((x, y))
        else:
            half = self.width() // 2
            nw, ne, sw, se = self.children
            nw.getList(result, x, y, rect)
            ne.getList(result, x + half, y, rect)
            sw.getList(result, x, y + half, rect)
            se.getList(result, x + half, y + half, rect)

    def set(self, x, y, value):
        "Returns a near-copy of the node with the value at x, y modified"
        if self.level == 0:
            return self.board.single[value]
        half = self.width() // 2
        index = int(x) // half + int(y) // half * 2
        children = list(self.children)
        children[index] = children[index].set(x % half, y % half, value)
        return self.board.getnode(children[0], children[1], children[2], children[3])

    def nextCenter(self, steps):
        "Returns a level-1 node advanced the given number of generations."
        if steps == 0:
            return self.center()
        if steps in self.cache:
            return self.cache[steps]
        nw, ne, sw, se = self.children
        if self.level == 2:
            aa, ab, ba, bb = mapid(nw.children)
            ac, ad, bc, bd = mapid(ne.children)
            ca, cb, da, db = mapid(sw.children)
            cc, cd, dc, dd = mapid(se.children)
            nwscore = lifeScore(bb, aa + ab + ac + ba + bc + ca + cb + cc)
            nescore = lifeScore(bc, ab + ac + ad + bb + bd + cb + cc + cd)
            swscore = lifeScore(cb, ba + bb + bc + ca + cc + da + db + dc)
            sescore = lifeScore(cc, bb + bc + bd + cb + cd + db + dc + dd)
            result = self.board.memo[(nwscore, nescore, swscore, sescore)]
        else:
            halfsteps = self.gensteps() // 2
            if steps <= halfsteps:
                step1 = 0
            else:
                step1 = halfsteps
            step2 = steps - step1
            nw, ne, sw, se = self.children
            n00, n01, n02, n10, n11, n12, n20, n21, n22 = [
                self.subquad(x).nextCenter(step1) for x in range(9)
            ]
            #      map(lambda x: self.subquad(x).nextCenter(step1), range(9))
            result = self.board.getnode(
                self.board.getnode(n00, n01, n10, n11).nextCenter(step2),
                self.board.getnode(n01, n02, n11, n12).nextCenter(step2),
                self.board.getnode(n10, n11, n20, n21).nextCenter(step2),
                self.board.getnode(n11, n12, n21, n22).nextCenter(step2),
            )
        self.cache[steps] = result
        return result

    def center(self):
        if 0 in self.cache:
            return self.cache[0]
        nw, ne, sw, se = self.children
        result = self.board.getnode(
            nw.children[3], ne.children[2], sw.children[1], se.children[0]
        )
        self.cache[0] = result
        return result

    def subquad(self, i):
        nw, ne, sw, se = self.children
        if i == 0:
            return nw
        if i == 1:
            return self.board.getnode(
                nw.children[1], ne.children[0], nw.children[3], ne.children[2]
            )
        if i == 2:
            return ne
        if i == 3:
            return self.board.getnode(
                nw.children[2], nw.children[3], sw.children[0], sw.children[1]
            )
        if i == 4:
            return self.center()
        if i == 5:
            return self.board.getnode(
                ne.children[2], ne.children[3], se.children[0], se.children[1]
            )
        if i == 6:
            return sw
        if i == 7:
            return self.board.getnode(
                sw.children[1], se.children[0], sw.children[3], se.children[2]
            )
        if i == 8:
            return se

    def width(self):
        return 1 << self.level

    def gensteps(self):
        return 1 << (self.level - 2)


class LifeBoard:
    def __init__(self):
        self.originx = 0
        self.originy = 0
        E = LifeNode(self, 0, None)
        X = LifeNode(self, 1, None)
        self.single = (E, X)
        self.memo = {}
        for i in range(16):
            tup = (i & 1, (i & 2) // 2, (i & 4) // 4, (i & 8) // 8)
            objtup = [self.single[x] for x in tup]
            # objtup = map(lambda x: self.single[x], tup)
            self.memo[tup] = LifeNode(self, i + 2, objtup)
        self.empty = [E, self.memo[(0, 0, 0, 0)]]
        self.nextid = 18
        self.root = E

    def info(self):
        return " c" + str(self.count()) + " m" + str(len(self.memo))

    def width(self):
        return self.root.width()

    def getnode(self, nw, ne, sw, se):
        tup = (nw.id, ne.id, sw.id, se.id)
        if tup not in self.memo:
            result = LifeNode(self, self.nextid, [nw, ne, sw, se])
            self.nextid = self.nextid + 1
            self.memo[tup] = result
        else:
            result = self.memo[tup]
        return result

    def emptynode(self, level):
        if level < len(self.empty):
            return self.empty[level]
        e = self.emptynode(level - 1)
        result = self.getnode(e, e, e, e)
        self.empty.append(result)
        return result

    def canonicalize(self, node, trans):
        if node.id < 18:
            return node
        if node.id not in trans:
            nw, ne, sw, se = node.children
            trans[node.id] = self.getnode(
                self.canonicalize(nw, trans),
                self.canonicalize(ne, trans),
                self.canonicalize(sw, trans),
                self.canonicalize(se, trans),
            )
        return trans[node.id]

    def clear(self):
        self.root = self.single[0]
        self.collect()

    def collect(self):
        self.trim()
        self.empty = [self.single[0], self.memo[(0, 0, 0, 0)]]
        old = self.memo
        self.memo = {}
        for i in range(16):
            tup = (i & 1, (i & 2) // 2, (i & 4) // 4, (i & 8) // 8)
            self.memo[tup] = old[tup]
        trans = {}
        self.root = self.canonicalize(self.root, trans)

    def trim(self):
        while 1:
            if self.root.count == 0:
                self.root = self.single[0]
            if self.root.level <= 1:
                return
            for index in range(9):
                sub = self.root.subquad(index)
                if sub.count == self.root.count:
                    self.originx += sub.width() // 2 * (index % 3)
                    self.originy += sub.width() // 2 * (index // 3)
                    self.root = sub
                    break
            else:
                return

    def double(self):
        if self.root.level == 0:
            self.root = self.memo[(self.root.id, 0, 0, 0)]
            return
        self.originx -= self.root.width() // 2
        self.originy -= self.root.width() // 2
        e = self.emptynode(self.root.level - 1)
        nw, ne, sw, se = self.root.children
        self.root = self.getnode(
            self.getnode(e, e, e, nw),
            self.getnode(e, e, ne, e),
            self.getnode(e, sw, e, e),
            self.getnode(se, e, e, e),
        )

    def get(self, x, y):
        if (
            x < self.originx
            or y < self.originy
            or x >= self.originx + self.root.width()
            or y >= self.originy + self.root.width()
        ):
            return 0
        return self.root.get(x - self.originx, y - self.originy)

    def getAll(self, rect=None):
        cells = []
        self.root.getList(cells, self.originx, self.originy, rect)
        return cells

    def set(self, x, y, value):
        if self.get(x, y) == value:
            return
        while (
            x < self.originx
            or y < self.originy
            or x >= self.originx + self.root.width()
            or y >= self.originy + self.root.width()
        ):
            self.double()
        self.root = self.root.set(x - self.originx, y - self.originy, value)

    def step(self, steps):
        if steps == 0:
            return
        self.double()
        self.double()
        while steps > self.root.gensteps():
            steps -= self.root.gensteps()
            self.root = self.root.nextCenter(self.root.gensteps())
            self.originx = self.originx + self.root.width() // 2
            self.originy = self.originy + self.root.width() // 2
            self.double()
            self.double()
        self.root = self.root.nextCenter(steps)
        self.originx = self.originx + self.root.width() // 2
        self.originy = self.originy + self.root.width() // 2

    def count(self):
        return self.root.count


if False:  # otherwise not called
    board.getAll((0, 0, 0, 0))
    board.get(0, 0)
    board.clear()
    board.count()
    board.info()
    board.width()

if __name__ == "__main__":  # speed test
    board = LifeBoard()
    random.seed(2)
    for x in range(1600):
        board.set(random.randint(-40, 40), random.randint(-40, 40), 1)
    steps = 1
    for x in range(20):
        board.step(steps)
        steps *= 2
