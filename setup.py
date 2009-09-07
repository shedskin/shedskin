#!/usr/bin/env python
import os
ss = file('shedskin.py', 'w')
print >>ss, '''#!/usr/bin/env python
import sys
sys.path.append("%s")
import shedskin
shedskin.main()
''' % os.getcwd()
ss.close()
os.system('chmod a+wrx shedskin.py')
