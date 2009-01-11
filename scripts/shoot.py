import os, time

benchmarks = [('binary_trees', 16)]

for benchmark, arg in benchmarks:
    print 'benchmark:', benchmark

    # python
    t0 = time.time()
    os.system('python shootout_python/%s.py %s > /dev/null' % (benchmark, arg))
    print 'python: %.2f' % (time.time()-t0)

    # psyco
    t0 = time.time()
    os.system('python shootout_psyco/%s.py %s > /dev/null' % (benchmark, arg))
    print 'psyco: %.2f' % (time.time()-t0)

    # shedskin
    t0 = time.time()
    os.system('shootout/%s %s > /dev/null' % (benchmark, arg))
    print 'shedskin: %.2f' % (time.time()-t0)
    
    




