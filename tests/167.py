
print '',
print 'hoi', 'huh',
print 'hophop'
print '',
print 'beh'

print [1,2,3,1].index(1)
print [1,2,3,1].index(1, 1)
print [1,2,3,1].index(1, -1)
print [1,2,3,1].index(1, -4)
print [1,2,3,1].index(1, -3, 4)

def RemoveElts(list):
   newlist=list[:]
   return newlist
print RemoveElts([3])

try:
    try:
       {1:2}[3]
    except KeyError, e:
       raise e
except KeyError, m:
    print m

blah = set([])
blah.add(1)
print blah

def MergeAndVerify(newModList,finalModHash):
    if newModList == []:
        return finalModHash



