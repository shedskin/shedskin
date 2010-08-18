
# file.next
print file('run.py').next().strip()

# re.groups returns tuple
import re
m = re.match(r"(\d+)\.?(\d+)?", "24")
groups = m.groups()
print groups

# overloading __getitem__ problem
class Vector3f:
    def __getitem__(self, key):
        return 19
v = Vector3f()
print v[0]

# more string formatting
print '!'+('%06d%6r%6.2f' % (18,'hoi', 1.17))+'!'
print '!'+('%0*d%*s%*.*f' % (6,18,6,'hoi',8,2,1.171))+'!'

# and/or funtest (already worked)
hoppa = (17, 18)
a, b = hoppa or (19,20)
print a, b

hoppa = None
a, b = hoppa or (19,20)
print a, b

x = [1,2]
y = [3,4,5]
c = x and y or None
print c

y = None
z = None
c = x and y or z
print c

# TI problem (seeding bool)
def rungame(strategy, verbose):
    strategy()

def s_bestinfo():
    z = [0]
    print z

def s_worstinfo():
    z = [0]
    print z

def eval_strategy(strategy):
    rungame(strategy, False)

def main():
    eval_strategy(s_bestinfo)
    eval_strategy(s_worstinfo)

main()

# test
import signal


