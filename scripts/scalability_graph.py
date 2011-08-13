import sys
import Gnuplot
import math

name_sloc = {}
grab = False
for line in file('README'):
    line = line.strip()
    if line.startswith('(sloccount)'):
        grab = True
    elif grab:
        split = line.split()
        if len(split) >= 2 and split[0].isdigit():
            #name_sloc[split[1]] = math.log(int(split[0]))
            name_sloc[split[1]] = int(split[0])
print len(name_sloc)

g = Gnuplot.Gnuplot()

for filename in sys.argv[1:]:
    print filename
    name_time = {}
    for line in file(filename):
        line = line.strip()
        if line.startswith('*** test'):
            name = line.split()[-2]
            if name == 'sto_atom.py':
                name = 'quameon'
            elif name == 'c64.py':
                name = 'c64_main.py'
            elif name == 'SimpleGeometry.py':
                name = 'pylot_main.py'
            elif name == 'mandelbrot2.py':
                name = 'mandelbrot2_main.py'

        if line.startswith('[elapsed'):
            name_time[name] = float(line.split()[-2])

    data = []
    for name in sorted(name_sloc, key=name_sloc.__getitem__):
        if name not in ['amaze.py', 'life.py']:
            if name in name_time:
                data.append((name_sloc[name], name_time[name]))
                #print name, name_sloc[name], name_time[name]
            else:
                print 'NG!', name

    for x,y in data:
        print x, y

    g.replot(Gnuplot.Data(data, with_='linespoints'))

#g.replot('17.2768267-0.0596341*x+0.0000533*x**2')

while True: 
    pass
