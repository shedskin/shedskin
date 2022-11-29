
# Copyright (C) 2007, Mark Dewing
# Quameon is covered under the GNU General Public License.  Please see the
# file LICENSE that is part of this distribution.

import orbital
from . import atomic_sto

def create_sto_orbs(atomic_info):
  npos = atomic_info[0][1]
  nelec = atomic_info[0][0][1]
  orbs = []
  atsto = atomic_sto.atomic_STO()
  atsto.set_exp_coeff(1.0,[[1.0]],'s',npos)
  orbs.append(atsto)
  if nelec >= 2:
    atsto = atomic_sto.atomic_STO()
    atsto.set_exp_coeff(2.0,[[2.0]],'s',npos)
    orbs.append(atsto)
  return orbs
