import environment

class Universe:
    def __init__(self):
        f = open('test.py')
        self.myenv = environment.Environment(f)

u = Universe()
