#!/usr/bin/env python

# placed in the public domain by Stavros Korokithakis

import time
import copy
from random import randrange, randint, seed, random, choice, triangular
seed(42)

# The size of the data bus of the multiplexer.
DATA_SIZE = 4
# The size of the selector, in bits (this is log2   (DATA_SIZE)).
MUX_SIZE = 2
MAX_DEPTH = 5

OPCODE_NONE = 0
OPCODE_AND = 1
OPCODE_OR = 2
OPCODE_NOT = 3
OPCODE_IF = 4

ARG_NUM = (0, 2, 2, 1, 3)

STATE_OPCODE = 0
STATE_ARGUMENT = 1
STATE_SUBTREE = 2

def fitness(individual):
    return individual.fitness

def make_random_genome(node, depth=0):
    if depth >= MAX_DEPTH or random() > 0.7:
        node.opcode = OPCODE_NONE
        node.args = None
        node.value = randrange(MUX_SIZE + DATA_SIZE)
    else:
        node.opcode = randint(OPCODE_AND, OPCODE_IF)
        node.value = 0
        node.args = tuple([TreeNode() for _ in range(ARG_NUM[node.opcode])])
        for arg in node.args:
            make_random_genome(arg, depth+1)

class TreeNode:
    def __init__(self, opcode=OPCODE_NONE, value=-1, args=None):
        self.opcode = opcode
        self.value = value
        self.args = args

    def mutate(self):
        """Mutate this node."""
        # If we're a terminal node, stop so we don't exceed our depth.
        if self.opcode == OPCODE_NONE:
            return

        if random() > 0.5:
            # Turn this node into a terminal node.
            make_random_genome(self, MAX_DEPTH)
        else:
            # Turn this into a different node.
            make_random_genome(self, MAX_DEPTH-1)


    def execute(self, input):
        if self.opcode == OPCODE_NONE:
            return (input & (1 << self.value)) >> self.value
        elif self.opcode == OPCODE_AND:
            return self.args[0].execute(input) & \
                   self.args[1].execute(input)
        elif self.opcode == OPCODE_OR:
            return self.args[0].execute(input) | \
                   self.args[1].execute(input)
        elif self.opcode == OPCODE_NOT:
            return 1 ^ self.args[0].execute(input)
        elif self.opcode == OPCODE_IF:
            if self.args[0].execute(input):
                return self.args[1].execute(input)
            else:
                return self.args[2].execute(input)

    def __str__(self):
        if self.opcode == OPCODE_NONE:
            output = "(bit %s)" % self.value
        elif self.opcode == OPCODE_AND:
            output = "(and %s %s)" % self.args
        elif self.opcode == OPCODE_OR:
            output = "(or %s %s)" % self.args
        elif self.opcode == OPCODE_NOT:
            output = "(not %s)" % self.args
        elif self.opcode == OPCODE_IF:
            output = "(if %s then %s else %s)" % self.args

        return output

class Individual:
    def __init__(self, genome=None):
        """
        Initialise the multiplexer with a genome and data size.
        """
        if genome is None:
            self.genome = TreeNode()
            make_random_genome(self.genome, 0)
        else:
            self.genome = genome
        # Memoize fitness for sorting.
        self.fitness = 0.0

    def __str__(self):
        """Represent this individual."""
        return "Genome: %s, fitness %s." % (self.genome, self.fitness)

    def copy(self):
        return Individual(copy.deepcopy(self.genome))

    def mutate(self):
        """Mutate this individual."""
        if self.genome.args:
            node, choice = self.get_random_node()
            node.args[choice].mutate()

    def get_random_node(self, max_depth=MAX_DEPTH):
        """Get a random node from the tree."""
        root = self.genome
        previous_root = root
        choice = 0
        for counter in range(max_depth):
            if root.args and random() > 1 / MAX_DEPTH:
                previous_root = root
                choice = randrange(len(root.args))
                root = root.args[choice]
            else:
                break
        return (previous_root, choice)

    def update_fitness(self, full_test=False):
        """Calculate the individual's fitness and update it."""
        correct = 0
        if full_test:
            data = (1 << DATA_SIZE) - 1
            for mux in range(DATA_SIZE):
                for _ in range(2):
                    # Flip the bit in question.
                    data ^= (1 << mux)
                    input = (data << 2) | mux
                    output = self.genome.execute(input)

                    # Do some bit twiddling...
                    correct_output = (data & (1 << mux)) >> mux
                    if output == correct_output:
                        correct += 1
            total = DATA_SIZE * 2
        else:
            for mux in range(DATA_SIZE):
                for data in range(1 << DATA_SIZE):
                    input = (data << 2) | mux
                    output = self.genome.execute(input)

                    # Do some bit twiddling...
                    correct_output = (data & (1 << mux)) >> mux
                    if output == correct_output:
                        correct += 1
            total = (1 << DATA_SIZE) * DATA_SIZE

        self.fitness = (1.0 * correct) / total
        return self.fitness

class Pool:
    population_size = 300

    def __init__(self):
        """Initialise the pool."""
        self.population = [Individual() for _ in range(Pool.population_size)]
        self.epoch = 0

    def crossover(self, father, mother):
        son = father.copy()
        daughter = mother.copy()
        son_node, son_choice = son.get_random_node()
        daughter_node, daughter_choice = daughter.get_random_node()
        if son_node.args and daughter_node.args:
            temp_node = son_node.args[son_choice]
            son_node.args = son_node.args[:son_choice] + (daughter_node.args[daughter_choice], ) + son_node.args[son_choice+1:]
            daughter_node.args = daughter_node.args[:daughter_choice] + (temp_node, ) + daughter_node.args[daughter_choice+1:]
        return son, daughter

    def advance_epoch(self):
        """Pass the time."""
        # Sort ascending because this is cost rather than fitness.
        self.population.sort(key=fitness, reverse=True)
        new_population = []

        # Clone our best people.
        iters = int(Pool.population_size * 0.4)
        for counter in range(iters):
            new_individual = self.population[counter].copy()
            new_population.append(new_individual)

        # Breed our best people, producing four offspring for each couple.
        iters = int(Pool.population_size * 0.6)
        for counter in range(0, iters, 2):
            # Perform rank roulette selection.
            father = self.population[int(triangular(0, iters, 0))]
            mother = self.population[int(triangular(0, iters, 0))]
            children = self.crossover(father, mother)
            children[0].mutate()
            new_population += children

        self.population = new_population
        for person in self.population:
            person.update_fitness()
        self.epoch += 1

    def get_best_individual(self):
        """Get the best individual of this pool."""
        return max(self.population, key=fitness)


def main():
    pool = Pool()
    start_time = time.time()
    for epoch in range(100):
        pool.advance_epoch()
        best_individual = pool.get_best_individual()
        if not epoch % 10:
            print("Epoch: %s, best fitness: %s" % (epoch, best_individual.fitness))

    print("Epoch: %s, best fitness: %s" % (epoch, best_individual.fitness))
    print("Finished in %0.3f sec, best individual: %s" % (time.time() - start_time, best_individual))

if __name__ == "__main__":
    main()
