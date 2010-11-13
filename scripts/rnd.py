import sys, os, random
_, logfile, parts = sys.argv
nr_time = {}
for l in file(logfile):
    if l.startswith('*** success'):
        nr_time[int(l.split()[2])] = float(l.split()[3][1:-1])
print nr_time
parts = int(parts)
best_time = None
seed = 0
while True:
    random.seed(seed)
    nrs = range(max(nr_time)+1)
    random.shuffle(nrs)
    times = []
    for part in range(parts):
        times.append(sum([nr_time.get(nr, 0) for nr in nrs[part::parts]]))
    if best_time is None or max(times) < best_time:
        best_time = max(times)
        print 'best_time:', best_time, seed
        for part in range(parts):
            print part, nrs[part::parts]
    seed += 1
