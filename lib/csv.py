class reader:
    def __init__(self, csvfile):
        self.count = 0

    def __iter__(self):
        return self

    def next(self):
        self.count += 1
        if self.count == 5:
            raise StopIteration
        return ['hoei', 'hop', '18', 'hurk']
