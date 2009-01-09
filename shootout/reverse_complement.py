#!/usr/bin/python
#
# The Great Computer Language Shootout
# http://shootout.alioth.debian.org/
#
# contributed by Jacob Lee, Steven Bethard, et al

import sys, string

def show(seq,
         table=string.maketrans('ACBDGHK\nMNSRUTWVYacbdghkmnsrutwvy',
                                'TGVHCDM\nKNSYAAWBRTGVHCDMKNSYAAWBR')):

   seq = (''.join(seq)).translate(table)[::-1]
   for i in xrange(0, len(seq), 60):
      print seq[i:i+60]


def main():
   seq = []
   add_line = seq.append
   for line in sys.stdin:
      if line[0] in '>;':
         show(seq)
         print line,
         del seq[:]
      else:
         add_line(line[:-1])
   show(seq)

main()
