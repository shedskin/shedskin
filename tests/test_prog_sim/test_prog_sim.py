class Agent():
    def __init__(self, x=None, y=None):
        """agent initialization
        """
        self.age = 0

    def update(self, food=()):
        self.age = self.age + 1
        # here: agent position update logic

class Predator(Agent):
    def __init__(self, x=None, y=None):
        Agent.__init__(self)
        self.vmax = 2.5

class Prey(Agent):
    def __init__(self, x=None, y=None):
        Agent.__init__(self)
        self.vmax = 2.0

class Plant(Agent):
    def __init__(self, x=None, y=None):
        Agent.__init__(self)
        self.vmax = 0

def main():
    # create initial agents
    preys = [Prey() for i in range(10)]
    predators = [Predator() for i in range(10)]
    plants = [Plant() for i in range(100)]
    timestep = 0

    while timestep < 10_000:
        # update all agents
        [a.update(food=plants) for a in preys]
        [a.update(food=preys) for a in predators]

        # here: handle eaten plants and create new plants
        # here: handle eaten prey and create new prey
        # here: handle old predators and create new predators

        timestep += 1

    return timestep


def test_sim():
    assert main() == 10_000

def test_all():
    test_sim()

if __name__ == "__main__":
    test_all()

