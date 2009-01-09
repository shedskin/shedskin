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

   seq2 = (''.join(seq)).translate(table)[::-1]
   for i in xrange(0, len(seq2), 60):
      print seq2[i:i+60]


def main():
   seq = []
   for line in sys.stdin:
      if line[0] in '>;':
         show(seq)
         print line,
         del seq[:]
      else:
         seq.append(line[:-1])
   show(seq)

main()
