class reader:
    def __init__(self, csvfile):
        self.csvfile = csvfile

    def __iter__(self):
        return __iter([''])

    def next(self):
        return self.csvfile.next().split(',')
