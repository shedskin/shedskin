# (c) Bearophile
#
# genetic algorithm

from random import random, randint, choice
from math import sin, pi
from copy import copy 

infiniteNeg = -1e302


class Individual:
    def __init__(self, ngenes):
        self.ngenes = ngenes
        self.genome = [random()<0.5 for i in xrange(ngenes)]
        self.fitness = infiniteNeg
    def bin2dec(self, inf=0, sup=0): 
        if sup == 0: sup = self.ngenes - 1 
        result = 0
        for i in xrange(inf, sup+1):
            if self.genome[i]:
                result += 1 << (i-inf)
        return result
    def computeFitness(self):
        self.fitness = self.fitnessFun(self.computeValuesGenome())
    def __repr__(self):
        return "".join([str(int(gene)) for gene in self.genome])

    def fitnessFun(self, x):
        return x + abs(sin(32*x))
    def computeValuesGenome(self, xMin=0, xMax=pi):
        scaleFactor = (xMax-xMin) / (1<<self.ngenes)
        return self.bin2dec() * scaleFactor


class SGA:
    def __init__(self):
        self.popSize = 200            # Ex. 200
        self.genomeSize = 16          # Ex. 16
        self.generationsMax = 16      # Ex. 100
        self.crossingOverProb = 0.75  # In [0,1] ex. 0.75
        self.selectivePressure = 0.75 # In [0,1] ex. 0.75
        self.geneMutationProb = 0.005  # Ex. 0.005

    def generateRandomPop(self):
        self.population = [Individual(self.genomeSize) for i in xrange(self.popSize)]

    def computeFitnessPop(self):
        for individual in self.population:
            individual.computeFitness()

    def mutatePop(self):
        nmutations = int(round(self.popSize * self.genomeSize * self.geneMutationProb))
        for i in xrange(nmutations):
            individual = choice(self.population) 
            gene = randint(0, self.genomeSize-1)
            individual.genome[gene] = not individual.genome[gene] 

    def tounamentSelectionPop(self):
        pop2 = []
        for i in xrange(self.popSize):
            individual1 = choice(self.population) 
            individual2 = choice(self.population)
            if random() < self.selectivePressure:
                if individual1.fitness > individual2.fitness:
                    pop2.append(individual1)
                else:
                    pop2.append(individual2)
            else:
                if individual1.fitness > individual2.fitness:
                    pop2.append(individual2)
                else:
                    pop2.append(individual1)
        return pop2 # fixed

    def crossingOverPop(self):
        nCrossingOver = int(round(self.popSize * self.crossingOverProb))
        for i in xrange(nCrossingOver):
            ind1 = choice(self.population) 
            ind2 = choice(self.population) 
            crossPosition = randint(0, self.genomeSize-1)
            for j in xrange(crossPosition+1):
                ind1.genome[j], ind2.genome[j] = ind2.genome[j], ind1.genome[j]

    def showGeneration_bestIndFind(self):
        fitnessTot = 0.0
        bestIndividualGeneration = self.population[0]
        for individual in self.population:
            fitnessTot += individual.fitness
            if individual.fitness > bestIndividualGeneration.fitness:
                bestIndividualGeneration = individual
        if self.bestIndividual.fitness < bestIndividualGeneration.fitness:
            self.bestIndividual = copy(bestIndividualGeneration) 


    def run(self):
        self.generateRandomPop()
        self.bestIndividual = Individual(self.genomeSize)
        for self.generation in xrange(1, self.generationsMax+1):
            self.computeFitnessPop()
            self.showGeneration_bestIndFind()
            self.population = self.tounamentSelectionPop()  
            self.mutatePop()
            self.crossingOverPop()

sga = SGA()
sga.generationsMax = 3000
sga.genomeSize = 20
sga.popSize = 30
sga.geneMutationProb = 0.01
sga.run()

