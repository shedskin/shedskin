# __NOT macro missing parentheses
x=10
if not 1<x<10:
    print "out of constraint"

# enumerate start arg
print list(enumerate('hoppa', 2))

# ConfigParser.items model
import ConfigParser
p = ConfigParser.ConfigParser()
p.read("testdata/symbols.INI")
for entry in p.items("symbols"):
    print entry
items = p.defaults().items()
print items
sections = p.sections()
print sections
