# Fixture for test_contours: a container allocated inside a static method.

from collections import defaultdict


class Factory:
    @staticmethod
    def make():
        return defaultdict(int)


d3 = Factory.make()
d3["a"] += 1
print(d3["a"])
