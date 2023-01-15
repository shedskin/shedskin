#!/usr/bin/python

# ant.py
# Eric Rollins 2008

#   This program generates a random array of distances between cities, then uses
#   Ant Colony Optimization to find a short path traversing all the cities --
#   the Travelling Salesman Problem.
#
#   In this version of Ant Colony Optimization each ant starts in a random city.
#   Paths are randomly chosed with probability inversely proportional to to the
#   distance to the next city.  At the end of its travel the ant updates the
#   pheromone matrix with its path if this path is the shortest one yet found.
#   The probability of later ants taking a path is increased by the pheromone
#   value on that path.  Pheromone values evaporate (decrease) over time.
#
#   In this impementation weights between cities actually represent
#   (maxDistance - dist), so we are trying to maximize the score.
#
#   Usage: ant seed boost iterations cities
#     seed         seed for random number generator (1,2,3...).
#                  This seed controls the city distance array.  Remote
#                  executions have their seed values fixed (1,2) so each will
#                  produce a different result.
#     boost        pheromone boost for best path.  5 appears good.
#                  0 disables pheromones, providing random search.
#     iterations   number of ants to be run.
#     cities       number of cities.

import random

# type Matrix = Array[Array[double]]
# type Path = List[int]
# type CitySet = HashSet[int]

# int * int * int -> Matrix
def randomMatrix(n, upperBound, seed):
    random.seed(seed)
    m = []
    for r in range(n):
        sm = []
        m.append(sm)
        for c in range(n):
             sm.append(upperBound * random.random())
    return m

# Path -> Path
def wrappedPath(path):
    return path[1:] + [path[0]]

# Matrix * Path -> double
def pathLength(cities, path):
    pairs = list(zip(path, wrappedPath(path)))
    return sum([cities[r][c] for (r,c) in pairs])

# Boosts pheromones for cities on path.
# Matrix * Path * int -> unit
def updatePher(pher, path, boost):
    pairs = list(zip(path, wrappedPath(path)))
    for (r,c) in pairs:
        pher[r][c] = pher[r][c] + boost

# Matrix * int * int -> unit
def evaporatePher(pher, maxIter, boost):
    decr = boost / float(maxIter)
    for r in range(len(pher)):
        for c in range(len(pher[r])):
            if pher[r][c] > decr:
                pher[r][c] = pher[r][c] - decr
            else:
                pher[r][c] = 0.0

# Sum weights for all paths to cities adjacent to current.
# Matrix * Matrix * CitySet * int -> double
def doSumWeight(cities, pher, used, current):
    runningTotal = 0.0
    for city in range(len(cities)):
        if city not in used:
            runningTotal = (runningTotal +
                            cities[current][city] * (1.0 + pher[current][city]))
    return runningTotal

# Returns city at soughtTotal.
# Matrix * Matrix * CitySet * int * double -> int
def findSumWeight(cities, pher, used, current, soughtTotal):
    runningTotal = 0.0
    next = 0
    for city in range(len(cities)):
        if runningTotal >= soughtTotal:
            break
        if city not in used:
            runningTotal = (runningTotal +
                            cities[current][city] * (1.0 + pher[current][city]))
            next = city
    return next

# Matrix * Matrix -> Path
def genPath(cities, pher):
    current = random.randint(0, len(cities)-1)
    path = [current]
    used = {current:1}
    while len(used) < len(cities):
        sumWeight = doSumWeight(cities, pher, used, current)
        rndValue = random.random() * sumWeight
        current = findSumWeight(cities, pher, used, current, rndValue)
        path.append(current)
        used[current] = 1
    return path

# Matrix * int * int * int ->Path
def bestPath(cities, seed, maxIter, boost):
    pher = randomMatrix(len(cities), 0, 0)
    random.seed(seed)
    bestLen = 0.0
    bestPath = []
    for iter in range(maxIter):
        path = genPath(cities, pher)
        pathLen = pathLength(cities, path)
        if pathLen > bestLen:
            # Remember we are trying to maximize score.
            updatePher(pher, path, boost)
            bestLen = pathLen
            bestPath = path
        evaporatePher(pher, maxIter, boost)
    return bestPath

def main():
    seed = 1
    boost = 5
    iter = 1000
    numCities = 200
    maxDistance = 100
    cityDistanceSeed = 1
    print("starting")
    cities = randomMatrix(numCities, maxDistance, cityDistanceSeed)
    path = bestPath(cities, seed, iter, boost)
    print(path)
    print("len = ", pathLength(cities, path))

if __name__ == "__main__":
    main()
