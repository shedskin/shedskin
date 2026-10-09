'''
copyright leon matthews

https://lost.co.nz/articles/sixteen-years-of-python-performance/

'''
import random

SNAKES_AND_LADDERS = {
    # Ladders
    1: 38,
    4: 14,
    9: 31,
    21: 42,
    28: 84,
    36: 44,
    51: 67,
    71: 91,
    80: 100,
    # Snakes
    98: 78,
    95: 75,
    93: 73,
    87: 24,
    64: 60,
    62: 19,
    56: 53,
    49: 11,
    48: 26,
    16: 6,
}

def snakes_and_ladders() -> Game:
    moves = []
    place = 0
    while True:
        roll = int(6 * random.random()) + 1
        landed = place + roll
        if landed > 100:
            # Too high, ignore
            pass
        else:
            # Special move or as rolled
            place = SNAKES_AND_LADDERS.get(landed, landed)
        moves.append((roll, place))
        # Won? Require exact roll.
        if place == 100:
            return moves

if __name__ == '__main__':
    total = 0
    for x in range(1000000):
        moves = snakes_and_ladders()
        total += len(moves)
    print(total)
