import random
import time

def case_a():
    t0 = time.time()
    s = 0
    for i in range(50000000):
#    for i in range(50):
        # list comp
        s += sum([2*x for x in range(64) if x > 2])
    print('%.2f' % (time.time()-t0))

    print('---')
    print('---')
    print(s)

def case_b():
    t0 = time.time()
    s = 0
    for i in range(50000000):
#    for i in range(50):
        # list-append
        l = []
        for x in range(64):
            if x > 2:
                l.append(2*x)
        s += sum(l)
    print('%.2f' % (time.time()-t0))

    print('---')
    print('---')
    print(s)

def case_c():
    t0 = time.time()
    s = 0
    for i in range(50000000):
#    for i in range(5000):
        # random length
        l = []
        for x in range(random.randrange(64)):
            if x > 2:
                l.append(2*x)
        s += sum(l)
    print('%.2f' % (time.time()-t0))
    print(s)


case_a()
case_b()
case_c()
