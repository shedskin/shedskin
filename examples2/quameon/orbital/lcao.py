#!/usr/bin/python

"""\
  orbital/lcao.py - Linear Combination of Atomic Orbitals
"""

# Copyright (c) 2006,2007, Mark Dewing
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import box_bc
import math
from . import atomic_sto
from .orbital_base import orbital_base

class LCAO(orbital_base):
  def __init__(self):
    self.coeff = [[1.0]]
    self.vp_size_set = False
    self.orbs = [atomic_sto.atomic_STO()]

#  def set_npos(self,npos):
#    for orb in self.orbs:
#      orb.set_npos(npos)

  def get_vp(self):
    self.vp_size_set = True
    vp = []
    self.vp_size = []
    for orb in self.orbs:
       ovp = orb.get_vp()
       vp.extend(ovp)
       self.vp_size.append(len(ovp))
    return vp

  def set_vp(self,vp):
    if not(self.vp_size_set):
      self.get_vp()
    idx = 0
    for i,orb in enumerate(self.orbs):
      if self.vp_size[i] > 0:
        end = idx + self.vp_size[i]
        if end > len(vp):
          end = len(vp)
        orb.set_vp(vp[idx:end])
        idx += end

  def compute_value(self,p,n_orb):
    col = []
    for orb in self.orbs:
      tmp = orb.compute_value2(p,1)
      col.append(tmp)
    val = []
    for i in range(n_orb):
      sum = 0.0
      for (j,c) in enumerate(self.coeff[i]):
        sum += c*col[j]
      val.append(sum)
    return val
 
  def compute_del(self,p,n_orb):
    col = []
    for orb in self.orbs:
      tmp = orb.compute_del(p,1)[0]
      col.append(tmp)
    val = []
    for i in range(n_orb):
      sum = [0.0,0.0,0.0]
      for (j,c) in enumerate(self.coeff[i]):
        for k in range(len(col[i])):
          sum[k] += c*col[j][k]
      val.append(sum)
    return val

  def compute_del_sq(self,p,n_orb):
    col = []
    for orb in self.orbs:
      tmp = orb.compute_del_sq(p,1)[0]
      col.append(tmp)
    val = []
    for i in range(n_orb):
      sum = 0.0
      for (j,c) in enumerate(self.coeff[i]):
        sum += c*col[j]
      val.append(sum)
    return val
