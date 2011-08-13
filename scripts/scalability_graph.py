import sys
import Gnuplot

name_sloc = {}
grab = False
for line in file('README'):
    line = line.strip()
    if line.startswith('(sloccount)'):
        grab = True
    elif grab:
        split = line.split()
        if len(split) >= 2 and split[0].isdigit():
            name_sloc[split[1]] = int(split[0])
print len(name_sloc)

g = Gnuplot.Gnuplot()

for filename in sys.argv[1:]:
    print filename
    name_time = {}
    for line in file(sys.argv[1]):
        line = line.strip()
        if line.startswith('*** test'):
            name = line.split()[-2]
        if line.startswith('[elapsed'):
            name_time[name] = float(line.split()[-2])

    data = []
    for name in sorted(name_sloc, key=name_sloc.__getitem__):
        if name not in ['amaze.py', 'life.py']:
            if name in name_time:
                data.append((name_sloc[name], name_time[name]))
            else:
                print 'NG!', name

    g.replot(data)

while True: 
    pass
