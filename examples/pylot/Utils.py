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

#{
def debug_print(*args):
  if debug:
    converted = []
    for a in args:
      if type(a) == str:
        converted.append(a)
      else:
        converted.append(repr(a))
    print " ".join(converted)

# Warning: not thread-safe
def add_debug_ray(ray, color=None):
  debug_print("Adding debug ray")
  if not debug:
    debug_print("Not doing it")
    return;
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
