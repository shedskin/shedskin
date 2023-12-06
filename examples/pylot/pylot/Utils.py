# Copyright 2010 Eric Uhrhane.
#
# This file is part of Pylot.
#
# Pylot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pylot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.import math

from math import fabs

debug = False

debug_rays = []

def nop():
  pass

def set_debug(val):
  global debug
  debug = val

def get_debug():
  return debug

def debug_print(string):
  if debug:
    print(string)

#{
# Warning: not thread-safe
def add_debug_ray(ray, color=None):
  if not debug:
    return
  global debug_rays
  if not color:
    color = "white"
  debug_rays.append((ray, color))

def clear_debug_rays():
  global debug_rays
  debug_rays = []

def get_debug_rays():
  for ray, color in debug_rays:
    print(ray, color)
  return debug_rays
#}

def Roughly(a, b):
  return fabs(a - b) < 0.000001

def NonZero(a):
  return fabs(a) > .000001
