# Fixture for test_contours: a lambda mapped over one container attribute,
# while another attribute of the same object holds tuples.


class Entry:
    def __init__(self, size):
        self.size = size


class Table:
    def __init__(self):
        self.entries = [Entry(1), Entry(2)]
        self.offsets = [(0, 1), (1, 3)]

    def sizes(self):
        return list(map(lambda entry: entry.size, self.entries))

    def spans(self):
        return [end - start for start, end in self.offsets]


table = Table()
print(table.sizes(), table.spans())
