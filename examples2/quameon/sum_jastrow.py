#!/usr/bin/python

"""\
  sum_jastrow.py - compute sums of individual jastrow terms
"""

# Copyright (C) 2006-2007, Mark Dewing
# http://quameon.sourceforge.net/
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import box_bc
import math
from jastrow import const_jastrow
from jastrow.simple_pade import simple_jastrow

class ee_jastrow:
  def __init__(self):
    self.box = box_bc.box_nopbc()
    self.func = simple_jastrow(True)
    #self.func = const_jastrow(True)

  def is_same_spin(self,i,j,n):
    x = i < n/2
    y = j < n/2
    return not(x^y)

#  def set_base_function(self,func):
#    self.func = func

  def compute_value(self,epos,p,idx):
    val = 0.0
    for i in range(0,len(epos)):
      if i != idx:
        r = self.box.dist(p,epos[i])
        spin = self.is_same_spin(i,idx,len(epos))
        val += self.func.u(r,spin)
    return val

  def compute_del(self,epos,p,idx):
    val = []
    for e in p:
      val.append(0.0)
    for i in range(0,len(epos)):
      if i != idx:
        (diff,r) = self.box.dist_v(p,epos[i])
        spin = self.is_same_spin(i,idx,len(epos))
        for i in range(len(val)):
          #if r > 0:
          val[i] += self.func.du(r,spin)*diff[i]/r
    return val

  def compute_del_sq(self,epos,p,idx):
    val = 0.0
    for i in range(0,len(epos)):
      if i != idx:
        r = self.box.dist(p,epos[i])
        spin = self.is_same_spin(i,idx,len(epos))
        val += 2*self.func.du(r,spin)/r + self.func.ddu(r,spin)
    return val

  def get_vp(self):
    return self.func.get_vp()

  def set_vp(self,vp):
    self.func.set_vp(vp)

#  def satisfies_constraints(self,vp):
#    return self.func.satisfies_constraints(vp)


class en_jastrow:
  def __init__(self,npos=[]):
    self.npos = npos
    self.box = box_bc.box_nopbc()
    self.func = simple_jastrow()
    #self.func = const_jastrow()

  def set_npos(self,npos):
    self.npos = npos

#  def set_base_function(self,func):
#    self.func = func

  def compute_value(self,p):
    val = 0.0
    for i in range(0,len(self.npos)):
      r = self.box.dist(p,self.npos[i])
      val += self.func.u(r)
    return val

  def compute_del(self,p):
    val = []
    for e in p:
      val.append(0.0)
    for i in range(0,len(self.npos)):
      (diff,r) = self.box.dist_v(p,self.npos[i])
      du = self.func.du(r)
      for i in range(len(val)):
        val[i] += du*diff[i]/r
    return val

  def compute_del_sq(self,p):
    val = 0.0
    for i in range(0,len(self.npos)):
      r = self.box.dist(p,self.npos[i])
      val += 2*self.func.du(r)/r + self.func.ddu(r)
    return val

  def get_vp(self):
    return self.func.get_vp()

  def set_vp(self,vp):
    self.func.set_vp(vp)

#  def satisfies_constraints(self,vp):
#    return self.func.satisfies_constraints(vp)
