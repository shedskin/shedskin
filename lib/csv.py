class reader:
    def __init__(self, csvfile):
        self.csvfile = csvfile

    def __iter__(self):
        return __iter([''])

class writer:
    def __init__(self, csvfile):
        self.csvfile = csvfile

    def writerow(self, seq):
        pass

    def writerows(self, seqs):
        pass
