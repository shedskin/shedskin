#!/usr/bin/python

"""\
  jastrow/simple_pade.py - single term Pade Jastrow factor
"""

# Copyright (c) 2006, Mark Dewing
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution

import box_bc
import math
from .base_jastrow import base_jastrow


class simple_jastrow(base_jastrow):
  def __init__(self,is_ee=False):
    self.a = -1.0
    #self.b = 0.317612
    self.b = 0.2
    if is_ee:
      self.a = 0.5
      self.b = 0.22459

  def u(self,r,is_same_spin=False):
    val = self.a*r/(1 + self.b*r)
    return val

  def du(self,r,is_same_spin=False):
    val = self.a/(1 + self.b*r)**2
    return val

  def ddu(self,r,is_same_spin=False):
    val = -2*self.a*self.b/(1 + self.b*r)**3
    return val

  def get_vp(self):
    return [self.b]

  def set_vp(self,vp):
    self.b = vp[0]

#  def satisfies_constraints(self,vp):
#    if vp[0] <= 0.0:
#      return False
#    else:
#      return True


if __name__ == '__main__':
  jas = simple_jastrow(True)
  #jas.b = 0.3652083
  jas.b = 0.0046
  #jas = simple_jastrow(False)
  #jas.b = 0.2168092
  #jas.a = -2.0

  for i in range(70):
    x = i*.1 + .1
    print(x,jas.u(x))
