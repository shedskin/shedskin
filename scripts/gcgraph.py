# boehm gc: ./configure --enable-gc-debug 
# #define GC_DEBUG in top of lib/builtin.hpp (before including gc headers)
# add -pg -ggdb to shedskin FLAGS
# shedskin some_program && make
# export GC_BACKTRACES=100
# ./program > gcdump 2>&1
# python gcgraph.pyn > gc.dot
# dot gc.dot -Tpng -ogcgraph.png

# XXX hardcoded for looking at dictentries on 32-bit linux specifically for now

dictentry_pos = {
    0: 'hash',
    4: 'key',
    8: 'value',
    12: 'use',
}

sizeof_dictentry = 16

SMALL = 100

import collections
lines = [l.strip() for l in open('gcdump')]
#print len(lines)
result = collections.defaultdict(int)
for i, line in enumerate(lines):
    if line.startswith('****Chosen'):
#        print
#        print i
        szpos = lines[i+1].find('sz=')
        if szpos != -1: 
            szpos += 3
        szpos2 = lines[i+1].find(',', szpos)
        if szpos == -1:
            szpos = lines[i+1].find('length:')+7
            szpos2 = len(lines[i+1])
        lastsize = int(lines[i+1][szpos:szpos2])
#        print 'chosen with size', lastsize

    if line.startswith('Reachable via'):
        if ' from root ' in line:
            pass #print 'reachable from root'
        else:
            pos = lines[i].find('offset ')+7
            pos2 = lines[i].find(' ', pos)
            offset = int(lines[i][pos:pos2])
#            print 'reachable from offset', offset

            szpos = lines[i+1].find('sz=')
            if szpos != -1: 
                szpos += 3
            szpos2 = lines[i+1].find(',', szpos)
            if szpos == -1:
                szpos = lines[i+1].find('length:')+7
                szpos2 = len(lines[i+1])
            thissize = int(lines[i+1][szpos:szpos2])
#            print 'in object with size', thissize

            lastsize2 = lastsize
            if lastsize2 <= SMALL:
                lastsize2 = 'small'
            thissize2 = thissize
            if thissize2 <= SMALL:
                thissize2 = 'small'
            else:
                offset = offset % sizeof_dictentry # XXX
            result[thissize2, offset, lastsize2] += 1
            lastsize = thissize

print 'digraph gcgraph {'
for (size, offset, size2), count in result.items():
    if size == size2 == 'small':
        continue
    if SMALL < size < 1000000:
        continue
    if size > SMALL:
        offset = dictentry_pos.get(offset, offset)
    print '"size %s" -> "size %s" [ label = "%s (%s times)" ];' % (size, size2, offset, count)
print '}'
