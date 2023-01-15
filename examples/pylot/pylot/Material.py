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

from . import Color

#TODO: If a material's highly specular, it probably shouldn't be as
#bright diffuse-wise.

# Properties:
#  specular is used for highlights [phong-ish] on otherwise diffuse surfaces.
#  indexOfRefraction determines both refraction angle and reflectiveness of
#    transparent surfaces.
#  attenuation_distances isn't actually a color; it's a component-wise set of
#    distances describing how each component gets absorbed by transparent
#    materials.  For each multiple of the attenuation_distance for a given
#    component that light travels through a material, it loses half its strength
#    in that component.  A distance of 0 means no attenuation.  NOTE: Not
#    setting attenuation_distances at all means that the material is opaque.
#    This is how you do transparency.
#  color is used for diffuse scattering.
#  reflective is used for opaque reflection, and to color reflections from
#    transparent materials.  Note that transparent materials must first get
#    their reflected light by Fresnel's equations, so reflective can only
#    color and modify existing reflections from transparent materials, not
#    create them where they wouldn't already exist.  When reflecting off one
#    material inside another, we use the product of both materials' reflective
#    properties.
#  emissive is used for light sources. In general colors max out at 1, but you
#    may want to set emissive surfaces higher than that for physical realism.
#    Colors will get clipped to 1 before display, and currently there's a
#    pseudo-gamma-correction done by taking the sqrt of each component before
#    clipping.
class Material(object):
  def __init__(self,
               name,
               color=None,
               attenuation_distances=None,
               reflective=None,
               indexOfRefraction=1.0,
               specular=None,
               emissive=None):
    self.name = name
    self.color = color
    if not self.color:
      self.color = Color.GREY
    self.attenuation_distances = attenuation_distances
    self.reflective = reflective
    if not self.reflective:
      if self.attenuation_distances:
        # transparent objects default to white reflections
        self.reflective = Color.WHITE
      else:
        # opaque objects default to no reflections
        self.reflective = Color.BLACK
    self.indexOfRefraction = indexOfRefraction
    self.specular = specular
    if not self.specular:
      self.specular = Color.BLACK
    self.emissive = emissive

  def __repr__(self):
    return "[Material: " + self.name + "\n" + \
           "\tcolor: " + repr(self.color) + \
           "\tattenuation_distances: " + repr(self.attenuation_distances) + \
           "\treflective: " + repr(self.reflective) + \
           "\tspecular: " + repr(self.specular) + \
           "\temissive: " + repr(self.emissive) + \
           "\tindexOfRefraction: " + repr(self.indexOfRefraction) + "]"

  def isLightSource(self):
    return self.emissive is not None

EMPTY=Material("Empty", attenuation_distances=Color.BLACK, color=Color.BLACK,
               reflective=Color.WHITE)
BLUE_SPEC=Material("Blue Specular", color=Color.BLUE,
                   specular=Color.OFF_WHITE)
RED_SPEC=Material("Red Specular", color=Color.RED,
                  specular=Color.OFF_WHITE)
GREEN_SPEC=Material("Green Specular", color=Color.GREEN,
                    specular=Color.OFF_WHITE)
PURPLE_SPEC=Material("Purple Specular", color=Color.PURPLE,
                     specular=Color.OFF_WHITE)
BLUE_FLAT=Material("Blue Flat", color=Color.BLUE)
RED_FLAT=Material("Red Flat", color=Color.RED)
GREEN_FLAT=Material("Green Flat", color=Color.GREEN)
PURPLE_FLAT=Material("Purple Flat", color=Color.PURPLE)
GREY_FLAT=Material("Grey Flat", color=Color.GREY)
WHITE_FLAT=Material("White Flat", color=Color.WHITE)
MIRROR=Material("Mirror", color=Color.Color(0.9, 0.9, 0.9),
                specular=Color.GREY, reflective=Color.Color(0.9, 0.9, 0.9))
DARK_MIRROR=Material("Dark Mirror", color=Color.Color(0.1, 0.1, 0.1),
                     specular=Color.GREY, reflective=Color.Color(0.9, 0.9, 0.9))
RED_MIRROR=Material("Red Mirror", color=Color.Color(0.1, 0.05, 0.05),
                     specular=Color.GREY, reflective=Color.RED)
WHITE_LIGHT=Material("White Light", color=Color.WHITE,
                     emissive=Color.WHITE)
BRIGHT_LIGHT=Material("Bright Light", color=Color.WHITE,
                      emissive=Color.WHITE.scale(7))
GREY_LIGHT=Material("Grey Light", color=Color.WHITE,
                    emissive=Color.GREY)
GLASS=Material("Glass", color=Color.Color(0.1, 0.1, 0.1),
               attenuation_distances=Color.Color(0.5, 0.5, 0),
               indexOfRefraction=1.5, reflective=Color.Color(0.9, 0.9, 0.9))
DIAMOND=Material("Diamond", color=Color.Color(0.1, 0.1, 0.1),
                 attenuation_distances=Color.Color(0, 0, 0.7),
                 indexOfRefraction=2.417)
