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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import math

from .Utils import Roughly #, debug_print
#{
#}
from . import Color
from .Ray import Ray
from .Vector4 import Vector4, fresnel_reflectance_at_angle
from .World import World
from .Shape import rayHitsPlane
from . import Material

MAX_GENERATIONS = 10

# Later we'll have a subclass of Camera for each of raytracing, pathtracing,
# etc.  If possible, we'll keep all the differences here.
class Camera(object):
  def __init__(self, world, eye, target, up, distance,
               w, h, cols, rows, ortho=False):
#{
    assert type(world) == World
    assert type(eye) == Vector4
    assert type(target) == Vector4
    assert type(up) == Vector4
#}
    assert eye.w == 1
    assert target.w == 1
    self.world = world
    if not up.w: # Up can be a vector or a point.
      up = up + eye
    assert up.w == 1 # Use points for all three.
    self.eye = eye
    self.direction = (target - eye).normalize()
    self.up = -(up-eye).cross(self.direction).cross(self.direction).normalize()
    assert w > 0
    assert h > 0
    assert distance > 0
    self.distance = distance
    self.w = float(w)
    self.h = float(h)
    self.cols = cols
    self.rows = rows
    self.left = self.up.cross(self.direction)
    self.screenCenter = self.eye + self.direction.scale(self.distance)
    self.screenTopLeft = self.screenCenter + self.up.scale(self.h / 2) + \
                                        self.left.scale(self.w / 2)
    self.xIncrement = self.left.scale(-self.w / float(self.cols))
    self.yIncrement = self.up.scale(-self.h / float(self.rows))
    self.ortho = ortho

    screenBottomRight = self.screenTopLeft + \
                        self.xIncrement.scale(self.cols - 0.5) + \
                        self.yIncrement.scale(self.rows - 0.5)

  def __repr__(self):
    s = ("eye %s; direction %s; up %s; dist %f; w %f; h %f; cols %d; " +
         "rows %d; ortho %s") % (repr(self.eye), repr(self.direction),
                                 repr(self.up), self.distance, self.w, self.h,
                                 self.cols, self.rows, repr(self.ortho))
    return s

  def getDirectLighting(self, ray, hitLocation, lights, shape, surfaceNormal):
    material = shape.material
    color = Color.BLACK
    for light in lights:
      if light is not shape:
        lightDirection = (light.getLocation() - hitLocation).normalize()
        lightDotSurfaceNormal = lightDirection.dot(surfaceNormal)
        if lightDotSurfaceNormal > 0:
          lightHit = self.world.intersect(Ray(hitLocation, lightDirection),
                                          ignore=shape)
          # intersect *should* never miss, but...
          if lightHit.hit and lightHit.shape is light:
            lightReflection = -lightDirection.reflect(surfaceNormal)
            highlight = math.pow(lightReflection.dot(-ray.offset), 20)
            intensity = light.getIntensity(hitLocation)
            color += (material.color * light.material.emissive).scale(
                lightDotSurfaceNormal * intensity)
            color += (light.material.emissive * material.specular).scale(
                highlight * intensity)
#            debug_print("light is " + repr(light))
#            debug_print("got direct lighting color " + repr(color))
    return color

  def getLightingFromSecondaryRay(self, ray, lights, generation, strength,
                                  materialStack, ignore=None, inside=None):
#    debug_print("In getLightingFromSecondaryRay(%d)" % generation)
    insideMaterial = materialStack[-1]
    hit = self.world.intersect(ray, ignore=ignore, inside=inside,
                               insideMaterial=insideMaterial)
    color = Color.BLACK
    if hit.hit:
#      add_debug_ray(Ray(ray.origin, ray.offset.scale(hit.distance)), "red")
      if insideMaterial.attenuation_distances:
        # Here we lower strength due to absorbtion in insideMaterial in the
        # hit.distance traveled.  We attenuate by 50% for each unit of distance,
        # where the unit length is a property of the material.  So
        #   strength *= pow(0.5, (distance / attenuation_distance))
        # We compute a custom attenuator per component.
        attenuators = []
        for d in insideMaterial.attenuation_distances.toList():
          if d:
            p = math.pow(0.5, hit.distance / d)
          else:
            p = 1.0
          attenuators.append(p)
#        debug_print("attenuators is " + repr(attenuators))
#        debug_print("strength was " + repr(strength))
        strength *= Color.fromList(attenuators)
#        debug_print("strength is " + repr(strength))
        # Too dim to matter after attenuation?
        if sum(strength.toList()) < 0.01:
#          debug_print("Out early getLightingFromSecondaryRay(%d)" % generation)
          return color
      color = self.getLighting(ray, hit, lights,
                               generation=generation+1,
                               strength=strength,
                               materialStack=materialStack)
#    debug_print("returning color " + repr(color))
#    debug_print("Out getLightingFromSecondaryRay(%d)" % generation)
    return color

  def getReflectedLighting(self, ray, hit, hitLocation, lights, shape,
                           surfaceNormal, materialStack, strength, generation):
#    debug_print("In getReflectedLighting(%d)" % generation)
    material = shape.material
    reflection = Ray(hitLocation, ray.offset.reflect(surfaceNormal))
    color = self.getLightingFromSecondaryRay(reflection, lights, generation,
                                             strength, materialStack,
                                             ignore=shape)
#    debug_print("Reflected color is " + repr(color))
#    debug_print("Out getReflectedLighting(%d)" % generation)
    return color

  def getRefractedLighting(self, ray, hit, hitLocation, lights, shape,
                           surfaceNormal, materialStack, fromMaterial,
                           toMaterial, insideShape, strength, generation):
#    debug_print("In getRefractedLighting(%d)" % generation)
#    debug_print("strength is " + repr(strength))
#    debug_print("shape is " + repr(shape))

    if fromMaterial == toMaterial:
      refractionVector = ray.offset
    else:
      refractionVector = ray.offset.refract(surfaceNormal,
                                            fromMaterial.indexOfRefraction,
                                            toMaterial.indexOfRefraction)
    color = Color.BLACK
    if refractionVector:
      # Ideally this would never fail, since we check the strength of the
      # refracted ray using fresnel_reflectance_at_angle before getting here.
      # But it's possible that, due to floating point errors, this disagrees
      # about whether we've hit total internal reflection or not.
      refraction = Ray(hitLocation, refractionVector)
#      debug_print("Refracted ray is " + repr(refraction))
      color = self.getLightingFromSecondaryRay(refraction, lights, generation,
                                               strength, materialStack,
                                               inside=insideShape)
#    debug_print("Out getRefractedLighting(%d)" % generation)
    return color

  # By default this assumes that the camera is always in free space, not inside
  # an object with a material other than EMPTY.  If you want to start out under
  # water, in glass, etc., you'll have to set up the materialStack
  # appropriately.
  def getLighting(self, ray, hit, lights, generation=1, strength=None,
                  materialStack=None):
#    debug_print("In getLighting(%d)" % generation)
    assert Roughly(ray.offset.length(), 1)
    shape = hit.shape
    if not materialStack:
      assert(not hit.inverted)
      materialStack = [Material.EMPTY]
    fromMaterial = materialStack[-1]
    if hit.inverted:
      assert len(materialStack) > 1
      refractMaterialStack = materialStack[:-1]
      insideShape = None
    else:
      refractMaterialStack = materialStack + [shape.material]
      insideShape = shape
      # insideShape is the shape we just entered.  This is a hack for spheres,
      # so that we know to detect the refracted ray hitting the inside of the
      # shape without bouncing off anything else first.  All other shapes are
      # currently planar, so this won't affect them.
    toMaterial = refractMaterialStack[-1]
    if not strength:
      strength = Color.WHITE

    if not hit.inverted and toMaterial.emissive:
      color = toMaterial.emissive * strength
    else:
      color = Color.BLACK
    hitLocation = ray.origin + ray.offset.scale(hit.distance)
    surfaceNormal = shape.getNormal(hitLocation)

#    debug_print("Before getDirectLighting, strength is " + repr(strength))
#    debug_print("Before getDirectLighting, color is " + repr(color))
    temp = self.getDirectLighting(ray, hitLocation, lights, shape,
                                  surfaceNormal)
#    debug_print("getDirectLighting returned" + repr(temp))
#    debug_print("product is " + repr(temp * strength))
    color += temp * strength
#    debug_print("After getDirectLighting, strength is " + repr(strength))
#    debug_print("After getDirectLighting, color is " + repr(color))
    if generation < MAX_GENERATIONS:
      if toMaterial.attenuation_distances: # Refraction is possible.
        # Reflection:
        # The cosine of the incident angle Ti is the ratio of adjacent /
        # hypotenuse, which here is |normal.incident| / incident, where incident
        # is of length 1.
        Ti = math.acos(math.fabs(surfaceNormal.dot(ray.offset)))
        proportionReflected = fresnel_reflectance_at_angle(
            Ti, fromMaterial.indexOfRefraction, toMaterial.indexOfRefraction)
        # We use the product of fromMaterial.reflective and
        # toMaterial.reflective so that reflections into and out of objects
        # work.  It's sort of arbitrary, but reflecting off the inside of a
        # glass object shouldn't just use toMaterial [empty space], and bouncing
        # off, say, glass under water might be affected by attributes of both.
        # If you don't set reflective on a transparent material, it'll all just
        # work with no reduction in strength beyond the Fresnel value anyway.
        reflectedStrength = strength.scale(proportionReflected) * \
            fromMaterial.reflective * toMaterial.reflective
        transmittedStrength = strength.scale(1 - proportionReflected)
      else:
        reflectedStrength = \
            strength * fromMaterial.reflective * toMaterial.reflective

      if sum(reflectedStrength.toList()) > 0.01:
        # strong enough to matter
        color += self.getReflectedLighting(
            ray, hit, hitLocation, lights, shape, surfaceNormal, materialStack,
            reflectedStrength, generation)
      # Refraction:
      if (toMaterial.attenuation_distances) and \
          sum(transmittedStrength.toList()) > 0.01:
        color += self.getRefractedLighting(ray, hit, hitLocation, lights,
                                           shape, surfaceNormal,
                                           refractMaterialStack, fromMaterial,
                                           toMaterial, insideShape,
                                           transmittedStrength, generation)
#    debug_print("Out getLighting(%d)" % generation)
    return color

  def runPixel(self, pixel, lights):
    if self.ortho:
      ray = Ray(pixel, self.direction)
    else:
      ray = Ray(self.eye, (pixel - self.eye).normalize())
    hit = self.world.intersect(ray)
    if hit.hit:
      return self.getLighting(ray, hit, lights).toImageColor()
    else:
      return Color.BLACK.toImageColor()

  def pixelForCoords(self, i, j):
    ret = self.screenTopLeft + self.xIncrement.scale(i - 0.5) + \
                               self.yIncrement.scale(j - 0.5)
    return ret

  def runPixelRange(self, r):
    lights = self.world.lightSources()
    (startCol, endCol), (startRow, endRow) = r
    return (r, 
        b''.join([self.runPixel(self.pixelForCoords(i, j), lights)
                 for j in range(startRow, endRow)
                 for i in range(startCol, endCol)]))

  # For raytracing, once you've got a hit, shoot rays at all light sources
  # [Shapes with emissive color set].  Skip any who are behind the surface hit
  # [dot with normal and check the sign], and tell world.intersect to ignore our
  # surface, to avoid glitches in which we self-shadow.  If the light source is
  # the first thing the ray hits, gather light from it to determine our local
  # diffuse lighting.  Add in local emissive lighting.  Later also spawn
  # reflection+transmission rays to add in those components of lighting as well.
  def runImage(self):
    return self.runPixelRange(((0, self.cols), (0, self.rows)))

  def mapPointToScreen(self, point):
    if self.ortho:
      direction = self.direction
    else:
      diff = point - self.eye
      if Roughly(diff.length_2(), 0):
        return None
      direction = diff.normalize()
    ray = Ray(self.eye, direction)
    hit = rayHitsPlane(-self.direction, self.screenCenter, ray)
    if hit.hit:
      assert not hit.inverted
    # TODO: This won't map points behind the eye.
      location = ray.origin + ray.offset.scale(hit.distance)
      offset = self.screenTopLeft - location
      distanceFromLeft = offset.dot(self.left)
      distanceFromTop = offset.dot(self.up)
      pixel = (int(distanceFromLeft / self.w * float(self.cols)),
               int(distanceFromTop / self.h * float(self.rows)))
      return pixel
    return None
