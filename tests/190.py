
import itertools

print '### Count ###'

#for a in itertools.count(4, 3):
#   if a > 16:
#       break
#   print a

for ca in itertools.count(3):
   if ca > 16:
       break
   print ca

#for cb in itertools.count(4, -3):
#   if cb < -16:
#       break
#   print cb

print '### Cycle ###'

ctt = 0
for b in itertools.cycle([1, 2, 3]):
   ctt += 1
   if ctt > 10:
       break
   print b

print '-'

woo = itertools.cycle(set([1, 2, 3]))
print woo.next()
print woo.next()
print woo.next()

print '### Repeat ###'

ctt2 = 0
for c in itertools.repeat(42):
   ctt2 += 1
   if ctt2 > 5:
       break
   print c

for c in itertools.repeat(42, 3):
   print c

print '### Chain ###'

for al in itertools.chain([1, 2]):
    print al
print '-'
for am in itertools.chain([1, 2], [3, 4]):
    print am
print '-'
for an in itertools.chain([1, 2], [3, 4], [5, 6]):
    print an
print '-'
for ao in itertools.chain([1, 2], [3, 4], [5, 6], [7, 8]):
    print ao
print '-'
for ap in itertools.chain([1, 2], [3, 4], [5, 6], [7, 8], [9, 10]):
    print ap
print '-'
for aq in itertools.chain([1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12, 13]):
    print aq

print '### Compress ###'

#for d in itertools.compress([42, 32, 21, 55, 303], [True, False, True, False, True]):
#   print c

print '### Dropwhile ###'

pred = lambda x: x < 5

for e in itertools.dropwhile(pred, [1, 4, 6, 4, 1]):
   print e

print '### Groupby ###'

def key(x):
   if x > 5:
      return 1
   else:
      return 0

for k, g in itertools.groupby([1, 4, 6, 4, 1], key):
   for f in g:
       print f,
   print ':', k

print '### Ifilter ###'

pred1 = lambda x: x % 2

for h in itertools.ifilter(pred1, range(10)):
   print h
for i in itertools.ifilter(None, range(10)):
   print i

print '### Ifilterfalse ###'

pred1 = lambda x: x % 2

for j in itertools.ifilterfalse(pred1, range(10)):
  print j
for j in itertools.ifilterfalse(None, range(10)):
  print j

print '### Islice ###'

print '--1'
for l in itertools.islice('ABCDEFG', 2):
    print l
print '--2'
for m in itertools.islice('ABCDEFG', 2, None):
    print m
print '--3'
for n in itertools.islice('ABCDEFG', 2, 4, 1):
    print n
print '--4'
for o in itertools.islice('ABCDEFG', 2, 4, 2):
    print o
print '--5'
for p in itertools.islice('ABCDEFG', 2, 4):
    print p
print '--6'
for r in itertools.islice('ABCDEFG', 0, 4, 2):
    print r
print '--7'
for s in itertools.islice('ABCDEFG', None, 4, 2):
    print s
print '--8'
for t in itertools.islice('ABCDEFG', None, 4):
    print t
print '--9'
for u in itertools.islice('ABCDEFG', 2, None, 2):
    print u
print '--10'
for v in itertools.islice('ABCDEFG', None):
    print v
print '--11'
for w in itertools.islice('ABCDEFG', None, None, 2):
    print w
print '--12'
for y in itertools.islice('ABCDEFG', None, None):
    print y
print '--13'
for z in itertools.islice('ABCDEFG', 2, None, None):
    print z
print '--14'
for aa in itertools.islice('ABCDEFG', None, None, None):
    print aa
print '--15'
for ab in itertools.islice('ABCDEFG', 2, 0):
    print ab
print '--16'
for ac in itertools.islice('ABCDEFG', 2, 0, 2):
    print ac
print '--17'
for ad in itertools.islice('ABCDEFG', 0, 0, 2):
    print ad

print '### Imap ###'

def foo(a):
   return '{%i}' % a
def foo2(a, b):
   return '{%i//%f}' % (a, b)
def foo3(a, b, c):
   return '{%i//%f//%s}' % (a, b, c)
def foo4(a, b, c, d):
   return '{%i//%f//%s//%i}' % (a, b, c, d)
def foo5(a, b, c, d, e):
   return '{%i//%f//%s//%i//%s}' % (a, b, c, d, str(e))

for iia in itertools.imap(foo, (21, 12, 42)):
   print iia
print '-'
for iib in itertools.imap(foo2, (21, 12, 42), (.21, .12)):
   print iib
print '-'
for iic in itertools.imap(foo3, (21, 12, 42), (.21, .12), ('a', 'b', 'c')):
   print iic
print '-'
for iid in itertools.imap(foo4, (21, 12, 42), (.21, .12), ('a', 'b', 'c'), (42, 12, 14, 6)):
   print iid
print '-'
for iie in itertools.imap(foo5, (21, 12, 42), (.21, .12), ('a', 'b', 'c'), (42, 12, 14, 6), ([5, 4], [8, 9])):
   print iie

print '### Starmap ###'

# TODO

print '### Tee ###'

def gen():
   for ae in [1, 2, 3, 4, 5]:
       yield ae
it1, it2 = itertools.tee(gen())
for af in it1:
   print af
for ag in it2:
   print ag
it3, it4, it5 = itertools.tee(gen(), 3)
for ah in it3:
   print ah
for ai in it4:
   print ai
for aj in it5:
   print aj

print '### Takewhile ###'

pred2 = lambda x: x < 5

for ak in itertools.takewhile(pred2, [1,4,6,4,1]):
   print ak

print '### Izip ###'

for ar in itertools.izip():
    print ar
print '-'
for at in itertools.izip([1, 3, 4]):
    print at
print '-'
for au in itertools.izip([1, 3, 4], [42, 21], [12, 21, 33, 55]):
    print au
print '-'
for au2 in itertools.izip([1, 3, 4], ['a', 'b']):
   print au2

print '### Izip_longest ###'

for av1 in itertools.izip_longest():
   print av1
print '-'
for av in itertools.izip_longest(fillvalue = 42):
   print av
print '-'
for aw1 in itertools.izip_longest(['a', 'b', 'c']):
   print aw1
print '-'
for aw2 in itertools.izip_longest([1, 3, 4], fillvalue = 42):
    print aw2
print '-'
for ax in itertools.izip_longest([1, 3, 4], [42, 21], [12, 21, 33, 55], fillvalue = 42):
    print ax
print '-'
for aw3 in itertools.izip_longest([[1, 2], [3, 4], [5, 6]], ['a', 'b']):
    print aw3

print '### Product ###'

for ay in itertools.product():
    print ay
print '-'
for az in itertools.product('A'):
    print az
print '-'
for ba in itertools.product('AB'):
    print ba
print '-'
for bb in itertools.product('A', ''):
    print bb
print '-'
for bc in itertools.product('A', 'B'):
    print bc
print '-'
for bd in itertools.product('AB', repeat = 2):
    print bd
print '-'
for be in itertools.product('A', 'B', repeat = 2):
    print be
print '-'
for bf in itertools.product('AB', 'CD'):
    print bf
print '-'
for bg in itertools.product('AB', 'CD', repeat = 2):
    print bg
print '-'
for bhy in itertools.product([.4, .42], [1, 2, 3]):
    print '%.2f %d' % bhy
print '-'
for bhz in itertools.product('AB', [1, 2, 3]):
    print bhz

print '### Permutations ###'

for bh in itertools.permutations('ABDC'):
    print bh
print '-'
for bi in itertools.permutations('ABDC', 0):
    print bi
print '-'
for bj in itertools.permutations('ABDC', 1):
    print bj
print '-'
for bk in itertools.permutations('ABDC', 2):
    print bk
print '-'
for bl in itertools.permutations('ABDC', 3):
    print bl
print '-'
for bm in itertools.permutations('ABDC', 5):
    print bm

print '### Combinations ###'

for bn in itertools.combinations('ABDC', 0):
    print bn
print '-'
for bo in itertools.combinations('ABDC', 1):
    print bo
print '-'
for bp in itertools.combinations('ABDC', 2):
    print bp
print '-'
for bq in itertools.combinations('ABDC', 3):
    print bq
print '-'
for br in itertools.combinations('ABDC', 5):
    print br

print '### Combinations_with_replacement ###'

#for bs in itertools.combinations_with_replacement('ABDC', 0):
#    print bs
#print '-'
#for bt in itertools.combinations_with_replacement('ABDC', 1):
#    print bt
#print '-'
#for bu in itertools.combinations_with_replacement('ABDC', 2):
#    print bu
#print '-'
#for bv in itertools.combinations_with_replacement('ABDC', 3):
#    print bv
#print '-'
#for bw in itertools.combinations_with_replacement('ABDC', 5):
#    print bw

