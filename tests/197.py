# mmap
import mmap

import os

PAGESIZE = mmap.PAGESIZE

TESTFILE_IN  = os.path.join('testdata', 'board.py')
TESTFILE_OUT = os.path.join('testdata', 'mmap.out')

def setUp():
    if os.path.exists(TESTFILE_OUT):
        os.remove(TESTFILE_OUT)

def tearDown(map):
    map.close()
    try:
        os.remove(TESTFILE_OUT)
    except OSError:
        pass
            
def test_anonymous():
    '''
    Test mmap module on anonymous files.
    '''
    print '## test_anonymous:'
    map = mmap.mmap(-1, PAGESIZE)
    assert len(map) == PAGESIZE
    print '# write:'    
    ## print map.size() ## TODO: throw mmap.error: [Errno 9] Bad file descriptor?
    assert map.tell() == 0
    map.write_byte('f')
    assert map.tell() == 1
    map.write('oo bar\tbaz\nqux')
    assert map.tell() == 15
    
    print '# get/set:'
    assert map[:15] == 'foo bar\tbaz\nqux'
    print map[0]    
    map[-1]='Z'
    print map[-1]    
    print map[4:-PAGESIZE+7]
    print '%r' %map[:15] 
    map[4:7] = "foo"
    map[PAGESIZE-3:] = "xyz"
    print map[PAGESIZE-3:]
    
    print '# find/seek:'
    assert map.find("foo") == -1
    map.seek(0)
    assert map.tell() == 0
    assert map.find("foo") == 0
    assert map.rfind("foo") == 4
    map.seek(-1, 2)
    assert map.tell() == PAGESIZE-1    
    map.seek(0, 2)
    assert map.tell() == PAGESIZE
    map.seek(-PAGESIZE, 1)
    assert map.tell() == 0
    
    print '# read:'
    print map.read(3)
    print '%r' % map.read_byte()
    print '%r' % map.readline()
    print '%r' % map.read(3)
    
    print '# move:'
    map.move(8, 4, 3)

    print '# iter:'
    assert "f" in map
    assert "a" not in map

    map.flush()
    
    print '# Result:'
    print '%r' % map[:15]

## re not supported (yet)
##     m = re.search('z',map)
##     assert m.start() == PAGESIZE -1

    h = 0
    for c in map:
        h += ord(c) * 31
    print h
    
    try:
        map.resize(0x2000)
        assert len(map) == 0x2000
    except:
        pass
    
    map.close()
    
def test_basic():
    '''
    Taken from python 2.7
    '''
    print '## test_basic:'
    setUp()
    # Test mmap module on Unix systems and Windows
    # Create a file to be mmap'ed.
    f = open(TESTFILE_OUT, 'w+')

    # Write 2 pages worth of data to the file
    f.write('\0'* PAGESIZE)
    f.write('foo')
    f.write('\0'* (PAGESIZE-3) )
    f.flush()
    m = mmap.mmap(f.fileno(), 2 * PAGESIZE)
    f.close()

    # Simple sanity checks

    assert m.find('foo') == PAGESIZE

    assert len(m) == 2*PAGESIZE

    print repr(m[0])
    print repr(m[0:3])
    
    try:
        m[len(m)]
    except IndexError:
        print "ok"

    # Modify the file's content
    m[0] = '3'
    m[PAGESIZE +3: PAGESIZE +3+3] = 'bar'

    # Check that the modification worked
    print repr(m[0])
    print repr(m[0:3])
    print repr(m[PAGESIZE-1 : PAGESIZE + 7])

    m.flush()
    # Try to seek to negative position...
    try:
        m.seek(-1)
    except ValueError:
        print "ok"

    # Try to seek beyond end of mmap...
    try:
        m.seek(1, 2)
    except ValueError:
        print "ok"

    try:
        m.seek(-len(m)-1, 2)
    except ValueError:
        print "ok"

    tearDown(m)

def test_readonly():
    '''
    Reads a file.
    '''
    print '## test_readonly:'
    f = open(TESTFILE_IN, 'r+')
    mapsize = os.path.getsize(TESTFILE_IN)
    map = mmap.mmap(f.fileno(), 0)
    assert map.size() == mapsize
    print repr(map.read(mapsize))
    map.close()

def test_rfind():
    # test the new 'end' parameter works as expected
    print '## test_rfind:'
    setUp()
    f = open(TESTFILE_OUT, 'w+')
    data = 'one two ones'
    n = len(data)
    f.write(data)
    f.flush()
    m = mmap.mmap(f.fileno(), n)
    f.close()

    assert m.rfind('one') == 8
    assert m.rfind('one ') == 0
    assert m.rfind('one', 0, -1) == 8
    assert m.rfind('one', 0, -2) == 0
    assert m.rfind('one', 1, -1) == 8
    assert m.rfind('one', 1, -2) ==-1
    
    tearDown(m)
    
def test_tougher_find():
    '''
    Taken from python 2.7
    '''
    print '## test_tougher_find:'
    setUp()
    # Do a tougher .find() test.  SF bug 515943 pointed out that, in 2.2,
    # searching for data with embedded \0 bytes didn't work.
    f = open(TESTFILE_OUT, 'w+')

    data = 'aabaac\x00deef\x00\x00aa\x00'
    n = len(data)
    f.write(data)
    f.flush()
    m = mmap.mmap(f.fileno(), n)
    f.close()

    for start in range(n+1):
        for finish in range(start, n+1):
            slice = data[start : finish]
            print m.find(slice) , data.find(slice)
            print m.find(slice + 'x') == -1

    tearDown(m)

test_anonymous()
test_basic()
test_readonly()
test_rfind()
test_tougher_find()

# re search empty string, match_object.span
import re
r = re.compile('^a?$')
print r.search('').start()
print r.search('').end()
print r.search('').span()
print r.search('a').start()
print r.search('a').end()
print r.search('a').span()

# id
foo_a="foo";foo_b="foo";foo_c="foo";
print id(foo_a)==id(foo_b)==id(foo_c)

# reduce fixes, more tests
from math import fabs
print reduce(lambda x,y: x + fabs(y), xrange(10))
print reduce(lambda x,y: x + fabs(y), xrange(10), 1)
print reduce(lambda x,y: x + fabs(y), xrange(10), 1.0)
print reduce(lambda x,y: x + fabs(y), map(float, xrange(10)))
print reduce(lambda x,y: x + fabs(y), map(float, xrange(10)), 2)
print reduce(lambda x,y: x + fabs(y), map(float, xrange(10)), 2.0)
class Aap:
    def __init__(self, value):
        self.value = value
    def __add__(self, other):
        return Aap(self.value+other.value)
    def __str__(self):
        return 'Aap(%s)' % self.value
aaplist = [Aap(3), Aap(4), Aap(5)]
print sum(aaplist, Aap(6))
print reduce(lambda a,b:a+b, aaplist), reduce(lambda a,b:a+b, aaplist, Aap(6))

# set methods now often take multiple args
sett = set(range(3))
sett.update(range(2,5), range(12,14))
print sorted(sett)

#cannot hurt to test this
print [].__class__.__name__
print 'hoi'.__class__.__name__

#string formatting asterisk
print "%d * %d" % (1,2)
print "%d* %% %d" % (1,2)
print "%d%% *%d" % (1,2)

#cmp fallback to rich comparison
class inst(object):
    def __init__(self, num, opcode='add', pc='1'):
        self.opcode = opcode
        self.pc = pc
        self.num = num
    
    def __lt__( self, other):
        return self.num < other.num

    def __repr__(self): 
        return "%d" % self.num
        
Seq = [inst(3),inst(1),inst(4),inst(2)]
print Seq
print sorted(Seq)

#complex problem
a = 4j + 3j
print a
b = a.real
