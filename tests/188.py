
import csv, collections
d = collections.defaultdict(list)
for (a,b,n,l) in csv.reader(open('testdata/woef.csv'), delimiter='|'):
    d[a,b].append((int(n),l))
for a,b in sorted(d, key=lambda t: t[1]):
    hoppa = ' '.join([l for (n,l) in sorted(d[a,b], key=lambda t: t[0])])
    hoppa = hoppa.replace('&nbsp;', ' ')
    print '<H1>%s</H1><H2>%s</H2>' % (b,a), hoppa
output = open('testdata/bla.csv', 'w')
wr = csv.writer(output, delimiter='|')
wr.writerow(['aa', 'bb', 'cc'])
wr.writerows(2*[['a', 'c', 'b']])
output.close()
print open('testdata/bla.csv').read()

print csv.field_size_limit()
print csv.field_size_limit(1000)
print csv.field_size_limit()

print sorted(csv.list_dialects())

csv.reader(open('testdata/woef.csv'), dialect = 'excel', delimiter = ',', quotechar = '"', lineterminator = '\r\n', escapechar = '')
csv.writer(file('testdata/bla.csv', 'w'), dialect = 'excel', delimiter = ',', quotechar = '"', lineterminator = '\r\n', escapechar = '')

bla = file('testdata/bla.csv', 'w')
fieldnames = ['hop', 'hap', 'ole', 'aap']
wr2 = csv.DictWriter(bla, fieldnames, restval='ah', quoting=csv.QUOTE_ALL)
rd = csv.DictReader(open('testdata/woef.csv'), fieldnames, restval='uh', restkey='oh', delimiter='|')
for d2 in rd:
    print sorted(d2.values())
    wr2.writerow(d2)
    wr2.writerows([d2])
bla.close()
rd.fieldnames = fieldnames
print rd.fieldnames
print open('testdata/bla.csv').read()

csv.DictReader(open('testdata/woef.csv'), None, dialect = 'excel', delimiter = ',', quotechar = '"', lineterminator = '', escapechar = '')
csv.DictWriter(open('testdata/woef.csv'), None, dialect = 'excel', delimiter = ',', quotechar = '"', lineterminator = '', escapechar = '')


