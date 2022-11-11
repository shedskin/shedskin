#!/usr/bin/python

"""\
    en_dist - e-n distance histograms
"""

# Copyright (C) 2008, Mark Dewing


from stats import histogram
from .observable_base import observable_base
import box_bc

class en_dist(observable_base):
  def __init__(self,npos):
    self.dist_hist = histogram.auto_histogram(nbins=40)
    self.box = box_bc.box_nopbc()
    self.npos = npos

  def accumulate(self,epos,wavef,loc_e):
    for np in self.npos:
      for ep in epos:
        r = self.box.dist(np,ep)
        self.dist_hist.add_value(r)
    #np = self.npos[0]
    #ep0 = epos[0]
    #ep1 = epos[1]
    #r0 = self.box.dist(np,ep0)
    #r1 = self.box.dist(np,ep1)
    #print r0,r1,loc_e


#  def output(self):
#    hist = self.dist_hist.get_histogram()
#    print '# e-n distance'
#    for x,val in hist:
#      print x,val
