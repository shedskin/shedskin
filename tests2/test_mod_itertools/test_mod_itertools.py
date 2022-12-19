import itertools


#print('### Ifilter ###')
#
#pred1 = lambda x: x % 2
#
#for h in itertools.ifilter(pred1, range(10)):
#   print(h)
#for i in itertools.ifilter(None, range(10)):
#   print(i)
#
#print('### Ifilterfalse ###')
#
#pred1 = lambda x: x % 2
#
#for j in itertools.ifilterfalse(pred1, range(10)):
#  print(j)
#for j in itertools.ifilterfalse(None, range(10)):
#  print(j)





#print('### Imap ###')
#
#def foo(a):
#   return '{%i}' % a
#def foo2(a, b):
#   return '{%i//%f}' % (a, b)
#def foo3(a, b, c):
#   return '{%i//%f//%s}' % (a, b, c)
#def foo4(a, b, c, d):
#   return '{%i//%f//%s//%i}' % (a, b, c, d)
#def foo5(a, b, c, d, e):
#   return '{%i//%f//%s//%i//%s}' % (a, b, c, d, str(e))
#
#for iia in itertools.imap(foo, (21, 12, 42)):
#   print(iia)
#print('-')
#for iib in itertools.imap(foo2, (21, 12, 42), (.21, .12)):
#   print(iib)
#print('-')
#for iic in itertools.imap(foo3, (21, 12, 42), (.21, .12), ('a', 'b', 'c')):
#   print(iic)
#print('-')
#for iid in itertools.imap(foo4, (21, 12, 42), (.21, .12), ('a', 'b', 'c'), (42, 12, 14, 6)):
#   print(iid)
#print('-')
#for iie in itertools.imap(foo5, (21, 12, 42), (.21, .12), ('a', 'b', 'c'), (42, 12, 14, 6), ([5, 4], [8, 9])):
#   print(iie)



# TODO


#print('### Izip ###')
#
#for ar in itertools.izip():
#    print(ar)
#print('-')
#for at in itertools.izip([1, 3, 4]):
#    print(at)
#print('-')
#for au in itertools.izip([1, 3, 4], [42, 21], [12, 21, 33, 55]):
#    print(au)
#print('-')
#for au2 in itertools.izip([1, 3, 4], ['a', 'b']):
#   print(au2)

#print('### Izip_longest ###')
#
#for av1 in itertools.izip_longest():
#   print(av1)
#print('-')
#for av in itertools.izip_longest(fillvalue = 42):
#   print(av)
#print('-')
#for aw1 in itertools.izip_longest(['a', 'b', 'c']):
#   print(aw1)
#print('-')
#for aw2 in itertools.izip_longest([1, 3, 4], fillvalue = 42):
#    print(aw2)
#print('-')
#for ax in itertools.izip_longest([1, 3, 4], [42, 21], [12, 21, 33, 55], fillvalue = 42):
#    print(ax)
#print('-')
#for aw3 in itertools.izip_longest([[1, 2], [3, 4], [5, 6]], ['a', 'b']):
#    print(aw3)



#for d in itertools.compress([42, 32, 21, 55, 303], [True, False, True, False, True]):
#   print c


def get_count(threshold=16, n=0, step=1):
    res=[]
    for i in itertools.count(n, step):
        if step > 0:
            if i > threshold:
                break
        else:
            if i < threshold:
                break
        res.append(i)
    return res

def test_count():
    assert get_count(threshold=16, n=3) == [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    assert get_count(threshold=-16, n=4, step=-3) == [4, 1, -2, -5, -8, -11, -14]


def get_cycle(iterable, max_iters=10):
    res = []
    n_iters = 0
    for i in itertools.cycle(iterable):
        n_iters += 1
        if n_iters > max_iters:
           break
        res.append(i)
    return res


def test_cycle():
    assert get_cycle([1,2,3], max_iters=10) == [1, 2, 3, 1, 2, 3, 1, 2, 3, 1]

    woo = itertools.cycle(set([1, 2, 3]))
    assert next(woo, -1) == 1
    assert next(woo, -1) == 2
    assert next(woo, -1) == 3
    assert next(woo, -1) == 1
    assert next(woo, -1) == 2
    assert next(woo, -1) == 3

def test_repeat():
    r = itertools.repeat(10)
    assert next(r) == 10
    assert next(r) == 10
    assert next(r) == 10

    assert list(itertools.repeat(42, 3)) == [42, 42, 42]

def test_chain():
    assert list(itertools.chain([1, 2, 3])) == [1, 2, 3]
    assert list(itertools.chain([1, 2, 3])) == [1, 2, 3]
    assert list(itertools.chain([1, 2], [3, 4])) == [1, 2, 3, 4]
    assert list(itertools.chain([1, 2], [3, 4], [5, 6])) == [1, 2, 3, 4, 5, 6]

pred = lambda x: x < 5

def test_dropwhile():
    assert list(itertools.dropwhile(pred, [1, 4, 6, 4, 1])) == [6, 4, 1]

def test_takewhile():
    assert list(itertools.takewhile(pred, [1,4,6,4,1])) == [1, 4]

def key(x):
   if x > 5:
      return 1
   else:
      return 0

def test_groupby():
    res = []
    for k, g in itertools.groupby([1, 4, 6, 4, 1], key):
        for f in g:
            res.append(f)
        res.append(k)
    assert res == [1, 4, 0, 6, 1, 4, 1, 0]

def test_islice():
    assert list(itertools.islice('ABCDEFG', 2)) == ['A', 'B']
    assert list(itertools.islice('ABCDEFG', 2, None)) == ['C', 'D', 'E', 'F', 'G']
    assert list(itertools.islice('ABCDEFG', 2, 4, 1)) == ['C', 'D']
    assert list(itertools.islice('ABCDEFG', 2, 4, 2)) == ['C']
    assert list(itertools.islice('ABCDEFG', 2, 4)) == ['C', 'D']
    assert list(itertools.islice('ABCDEFG', 0, 4, 2)) == ['A', 'C']
    assert list(itertools.islice('ABCDEFG', None, 4, 2)) == ['A', 'C']
    assert list(itertools.islice('ABCDEFG', None, 4)) == ['A', 'B', 'C', 'D']
    assert list(itertools.islice('ABCDEFG', 2, None, 2)) == ['C', 'E', 'G']
    assert list(itertools.islice('ABCDEFG', None)) == ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    assert list(itertools.islice('ABCDEFG', None, None, 2)) == ['A', 'C', 'E', 'G']
    assert list(itertools.islice('ABCDEFG', None, None)) == ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    assert list(itertools.islice('ABCDEFG', 2, None, None)) == ['C', 'D', 'E', 'F', 'G']
    assert list(itertools.islice('ABCDEFG', None, None, None)) == ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    assert list(itertools.islice('ABCDEFG', 2, 0)) == []
    assert list(itertools.islice('ABCDEFG', 2, 0, 2)) == []
    assert list(itertools.islice('ABCDEFG', 0, 0, 2)) == []

def test_permutations():
    assert list(itertools.permutations('ABDC', 0)) == [()]
    assert list(itertools.permutations('ABDC', 1)) == [('A',), ('B',), ('D',), ('C',)]
    assert list(itertools.permutations('ABDC', 2)) == [
        ('A', 'B'), ('A', 'D'), ('A', 'C'),
        ('B', 'A'), ('B', 'D'), ('B', 'C'), 
        ('D', 'A'), ('D', 'B'), ('D', 'C'), 
        ('C', 'A'), ('C', 'B'), ('C', 'D')]

def test_combinations():
    assert list(itertools.combinations('ABDC', 0)) == [()]
    assert list(itertools.combinations('ABDC', 1)) == [('A',), ('B',), ('D',), ('C',)]
    assert list(itertools.combinations('ABDC', 2)) == [
        ('A', 'B'), 
        ('A', 'D'), 
        ('A', 'C'), 
        ('B', 'D'), 
        ('B', 'C'), 
        ('D', 'C'),
    ]

def test_product():
    assert list(itertools.product()) == [()]
    assert list(itertools.product('A')) ==  [('A',)]
    assert list(itertools.product('AB')) == [('A',), ('B',)]
    assert list(itertools.product('A', '')) == []
    assert list(itertools.product('A', 'B')) == [('A', 'B')]
    assert list(itertools.product('AB', repeat = 2)) == [('A', 'A'), ('A', 'B'), ('B', 'A'), ('B', 'B')]
    assert list(itertools.product('A', 'B', repeat = 2)) == [('A', 'B', 'A', 'B')]
    assert list(itertools.product('AB', 'CD')) ==  [('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D')]
    # assert list(itertools.product('AB', 'CD', repeat = 2)) ==  []
    assert list(itertools.product([.4, .42], [1, 2, 3])) == [(0.4, 1), (0.4, 2), (0.4, 3), (0.42, 1), (0.42, 2), (0.42, 3)]
    assert list(itertools.product('AB', [1, 2, 3])) == [('A', 1), ('A', 2), ('A', 3), ('B', 1), ('B', 2), ('B', 3)]

def gen():
    for ae in [1, 2, 3, 4, 5]:
        yield ae

def test_tee():
    it1, it2 = itertools.tee(gen())
    assert list(it1) == [1, 2, 3, 4, 5]
    assert list(it2) == [1, 2, 3, 4, 5]

    it3, it4, it5 = itertools.tee(gen(), 3)

    assert list(it3) == [1, 2, 3, 4, 5]
    assert list(it4) == [1, 2, 3, 4, 5]
    assert list(it5) == [1, 2, 3, 4, 5]


def test_all():
    test_count()
    test_cycle()
    test_repeat()
    test_chain()
    test_dropwhile()
    test_takewhile()
    test_groupby()
    test_islice()
    test_permutations()
    test_combinations()
    test_product()

if __name__ == '__main__':
    test_all()

