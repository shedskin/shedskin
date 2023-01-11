#!/usr/bin/python

"""\
  jastrow/const_jastrow.py - constant Jastrow factors (useful mostly for testing)
"""

# Copyright (c) 2006, Mark Dewing
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution

import box_bc
import math
from .base_jastrow import base_jastrow


class const_jastrow(base_jastrow):
  def __init__(self,is_ee=False):
    self.a = -1.0
    if is_ee:
      self.a = 0.5
  def u(self,r,is_same_spin=False):
    return 1.0
  def du(self,r,is_same_spin=False):
    return 0.0
  def ddu(self,r,is_same_spin=False):
    return 0.0
  def get_vp(self):
    return [0.0]
  def set_vp(self,vp):
    pass
#  def satisfies_constraints(self,vp):
#    return True
