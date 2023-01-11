# Recipe 496907: Mastermind-style code-breaking, by Raymond Hettinger
# http://code.activestate.com/recipes/496907/
# Version speed up and adapted to Psyco D by leonardo maffi, V.1.0, Apr 4 2009

import random
from math import log
from collections import defaultdict
from time import time as clock


DIGITS = 4
TRIALS = 1
fmt = '%0' + str(DIGITS) + 'd'
searchspace = [[int(f) for f in fmt % i] for i in range(0, 10 ** DIGITS)]
count1 = [0] * 10
count2 = [0] * 10

def compare(a, b):
    N = 10
    for i in range(N):
        count1[i] = 0
        count2[i] = 0

    strikes = 0
    i = 0
    for dig1 in a:
        dig2 = b[i]
        i += 1
        if dig1 == dig2:
            strikes += 1
        count1[dig1] += 1
        count2[dig2] += 1

    balls  = (count1[0] if count1[0] < count2[0] else count2[0])
    balls += (count1[1] if count1[1] < count2[1] else count2[1])
    balls += (count1[2] if count1[2] < count2[2] else count2[2])
    balls += (count1[3] if count1[3] < count2[3] else count2[3])
    balls += (count1[4] if count1[4] < count2[4] else count2[4])
    balls += (count1[5] if count1[5] < count2[5] else count2[5])
    balls += (count1[6] if count1[6] < count2[6] else count2[6])
    balls += (count1[7] if count1[7] < count2[7] else count2[7])
    balls += (count1[8] if count1[8] < count2[8] else count2[8])
    balls += (count1[9] if count1[9] < count2[9] else count2[9])

    return (strikes << 16) | (balls - strikes)


def rungame(target, strategy, verbose=True, maxtries=15):
    possibles = searchspace
    for i in range(maxtries):
        g = strategy(i, possibles)
        if verbose:
            print("Out of %7d possibilities.  I'll guess %r" % (len(possibles), g), end=' ')
        score = compare(g, target)
        if verbose:
            print(' ---> ', score)
        if (score >> 16) == DIGITS: # score >> 16 is strikes
            if verbose:
                print("That's it.  After %d tries, I won." % (i+1))
            break
        possibles = [n for n in possibles if compare(g, n) == score]
    return i + 1

# Strategy support =============================================

def utility(play, possibles):
    b = defaultdict(int)
    for poss in possibles:
        b[compare(play, poss)] += 1

    # info
    bits = 0
    s = float(len(possibles))
    for i in b.values():
        p = i / s
        bits -= p * log(p, 2)
    return bits

def nodup(play):
    return len(set(play)) == DIGITS

# Strategies =============================================

def s_allrand(i, possibles):
    return random.choice(possibles)

def s_trynodup(i, possibles):
    for j in range(20):
        g = random.choice(possibles)
        if nodup(g):
            break
    return g

def s_bestinfo(i, possibles):
    if i == 0:
        return s_trynodup(i, possibles)
    plays = random.sample(possibles, min(20, len(possibles)))
    _, play = max([(utility(play, possibles), play) for play in plays])
    return play

def s_worstinfo(i, possibles):
    if i == 0:
        return s_trynodup(i, possibles)
    plays = random.sample(possibles, min(20, len(possibles)))
    _, play = min([(utility(play, possibles), play) for play in plays])
    return play

def s_samplebest(i, possibles):
    if i == 0:
        return s_trynodup(i, possibles)
    if len(possibles) > 150:
        possibles = random.sample(possibles, 150)
        plays = possibles[:20]
    elif len(possibles) > 20:
        plays = random.sample(possibles, 20)
    else:
        plays = possibles
    _, play = max([(utility(play, possibles), play) for play in plays])
    return play

# Evaluate Strategies =============================================

def average(seqn):
    return sum(seqn) / float(len(seqn))

def counts(seqn):
    limit = max(10, max(seqn)) + 1
    tally = [0] * limit
    for i in seqn:
        tally[i] += 1
    return tally[1:]

def eval_strategy(name, strategy):
    start = clock()
    data = [rungame(random.choice(searchspace), strategy, verbose=False) for i in range(TRIALS)]
    print('mean=%.2f %r  %s n=%d dig=%d' % (average(data), counts(data), name, len(data), DIGITS))
    print('Time elapsed %.2f' % (clock() - start,))

def main():
    random.seed(1)
    print('-' * 60)

    names = "s_bestinfo s_samplebest s_worstinfo s_allrand s_trynodup s_bestinfo".split()
    eval_strategy('s_bestinfo', s_bestinfo)
    eval_strategy('s_samplebest', s_samplebest)
    eval_strategy('s_worstinfo', s_worstinfo)
    eval_strategy('s_trynodup', s_trynodup)
    eval_strategy('s_allrand', s_allrand)

if __name__ == '__main__':
    main()
