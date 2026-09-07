class Solver(object):
    def __init__(self):
        self._current = (0, 0)

    def neighbours(self, pt):
        x, y = pt
        return [(x - 1, y)]

    def solve(self, flag):
        pt = self.neighbours(self._current)[0]
        if flag:
            pt = None
        self._current = pt


Solver().solve(False)
