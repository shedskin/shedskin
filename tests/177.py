
# --- import problem
from testdata.bert import *
z = zeug()

# --- '_' renaming mangle
import testdata.bert

class hello:
    def hello(self):
        testdata.bert.hello(1)

s=hello().hello()


