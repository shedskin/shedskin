'''
  Copyright (c) 2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
  http://www.hxa7241.org/minilight/
'''

import time

from ml import entry

def main():
    entry.main('cornellbox.txt')

if __name__=='__main__':
    main()  # stabilize pypy

    t0 = time.time()
    main()
    print('TIME %.2f' % (time.time()-t0))
