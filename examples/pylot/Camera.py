import math
from Utils import Roughly, debug_print, add_debug_ray, set_debug
import Color
from Ray import Ray
from Vector4 import Vector4, fresnel_reflectance_at_angle
from World import World
from Shape import Sphere, ParallelogramAt, rayHitsPlane
import Material

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
      if light <> shape:
        lightDirection = (light.getLocation() - hitLocation).normalize()
        lightDotSurfaceNormal = lightDirection.dot(surfaceNormal)
        if lightDotSurfaceNormal > 0:
          lightHit = self.world.intersect(Ray(hitLocation, lightDirection),
                                          ignore=shape)
          # intersect *should* never miss, but...
          if lightHit and lightHit.shape == light:
            debug_print("lightHit:", lightHit)
            debug_print("lightDotSurfaceNormal:", lightDotSurfaceNormal)
            debug_print("lightDirection:", lightDirection)
            lightReflection = -lightDirection.reflect(surfaceNormal)
            debug_print("lightReflection:", lightReflection)
            highlight = math.pow(lightReflection.dot(-ray.offset), 20)
            debug_print("highlight:", highlight)
            intensity = light.getIntensity(hitLocation)
            debug_print("intensity:", intensity)
            debug_print("color:", color)
            color = color + (material.color * light.material.emissive).scale(
                lightDotSurfaceNormal * intensity)
            debug_print("color1:", color)
            color = color + (light.material.emissive * material.specular).scale(
                highlight * intensity)
            debug_print("color1:", color)
    return color

  def getLightingFromSecondaryRay(self, ray, lights, generation, strength,
                                  materialStack, ignore=None, inside=None):
    debug_print("in getLightingFromSecondaryRay %d" % generation)
    insideMaterial = materialStack[-1]
    hit = self.world.intersect(ray, ignore=ignore, inside=inside,
                               insideMaterial=insideMaterial)
    color = Color.BLACK
    if hit:
      debug_print("Hit: ", hit)
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
        strength *= Color.fromList(attenuators)
        # Too dim to matter after attenuation?
        if sum(strength.toList()) < 0.01:
          return color
      color = self.getLighting(ray, hit, lights,
                               generation=generation+1,
                               strength=strength,
                               materialStack=materialStack)
    debug_print("out getLightingFromSecondaryRay %d" % generation)
    return color

  def getReflectedLighting(self, ray, hit, hitLocation, lights, shape,
                           surfaceNormal, materialStack, strength, generation):
    debug_print("in getReflectedLighting %d" % generation)
    material = shape.material
    reflection = Ray(hitLocation, ray.offset.reflect(surfaceNormal))
    add_debug_ray(reflection, "orange")
    color = self.getLightingFromSecondaryRay(reflection, lights, generation,
                                             strength, materialStack,
                                             ignore=shape)
    debug_print("out getReflectedLighting %d" % generation)
    return color

  # TODO: Figure out why the reflection of the wall on the cube inside the glass
  # sphere looks round.  Where are the other walls, too?
  def getRefractedLighting(self, ray, hit, hitLocation, lights, shape,
                           surfaceNormal, materialStack, strength, generation):
    debug_print("in getRefractedLighting %d" % generation)
    fromMaterial = materialStack[-1]
    if hit.inverted:
      debug_print("Popping off materialStack: ", materialStack[-1]);
      assert len(materialStack) > 1
      refractMaterialStack = materialStack[:-1]
      inside = None
    else:
      debug_print("Adding to materialStack: ", shape.material);
      refractMaterialStack = materialStack + [shape.material]
      inside = shape
    toMaterial = refractMaterialStack[-1]

    refraction = Ray(hitLocation,
                     ray.offset.refract(surfaceNormal,
                                        fromMaterial.indexOfRefraction,
                                        toMaterial.indexOfRefraction))
    add_debug_ray(ray, "yellow")
    color = self.getLightingFromSecondaryRay(refraction, lights, generation,
                                             strength, refractMaterialStack,
                                             inside=inside)
    debug_print("out getRefractedLighting %d" % generation)
    return color

  # By default this assumes that the camera is always in free space, not inside
  # an object with a material other than EMPTY.  If you want to start out under
  # water, in glass, etc., you'll have to set up the materialStack
  # appropriately.
  def getLighting(self, ray, hit, lights, generation=1, strength=None,
                  materialStack=None):
    debug_print("in getLighting %d" % generation)
    assert Roughly(ray.offset.length(), 1)
    if not materialStack:
      materialStack = [Material.EMPTY]
    insideMaterial = materialStack[-1]
    if not strength:
      strength = Color.WHITE
    shape = hit.shape
    material = shape.material

    if material.emissive:
      color = material.emissive
    else:
      color = Color.BLACK
    hitLocation = ray.origin + ray.offset.scale(hit.distance)
    debug_print("hitLocation: ", hitLocation)
    surfaceNormal = shape.getNormal(hitLocation)

    color = color + self.getDirectLighting(ray, hitLocation, lights, shape,
                                           surfaceNormal) * strength
    if generation < MAX_GENERATIONS:
      if material.attenuation_distances:
        # Reflection:
        # The cosine of the incident angle Ti is the ratio of adjacent /
        # hypotenuse, which here is |normal.incident| / incident, where incident
        # is of length 1.
        Ti = math.acos(math.fabs(surfaceNormal.dot(ray.offset)))
        proportionReflected = fresnel_reflectance_at_angle(
            Ti, insideMaterial.indexOfRefraction, material.indexOfRefraction)
        reflectedStrength = strength.scale(proportionReflected) * \
            material.reflective
        transmittedStrength = strength.scale(1 - proportionReflected)
      else:
        reflectedStrength = strength * material.reflective

      if sum(reflectedStrength.toList()) > 0.01:
        # strong enough to matter
        color = color + self.getReflectedLighting(
            ray, hit, hitLocation, lights, shape, surfaceNormal, materialStack,
            reflectedStrength, generation)
      # Refraction:
      if (material.attenuation_distances) and \
          sum(transmittedStrength.toList()) > 0.01:
        color = \
            color + self.getRefractedLighting(ray, hit, hitLocation, lights,
                                              shape, surfaceNormal,
                                              materialStack,
                                              transmittedStrength, generation)
    debug_print("out getLighting %d" % generation)
    return color

  def runPixel(self, pixel, lights):
    if self.ortho:
      ray = Ray(pixel, self.direction)
    else:
      ray = Ray(self.eye, (pixel - self.eye).normalize())
    hit = self.world.intersect(ray)
    if hit:
      return self.getLighting(ray, hit, lights).toImageColor()
    else:
      return "black"

  def pixelForCoords(self, i, j):
    ret = self.screenTopLeft + self.xIncrement.scale(i - 0.5) + \
                               self.yIncrement.scale(j - 0.5)
    return ret

  def runPixelRange(self, r):
    lights = self.world.lightSources()
    (startCol, endCol), (startRow, endRow) = r
    return \
        [((i, j), self.runPixel(self.pixelForCoords(i, j), lights))
           for i in range(startCol, endCol) for j in range(startRow, endRow)]

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
    if hit:
      (hitLocation, distance), inverted = hit
      assert not inverted
    # TODO: This won't map points behind the eye.
      offset = self.screenTopLeft - hitLocation
      distanceFromLeft = offset.dot(self.left)
      distanceFromTop = offset.dot(self.up)
      pixel = (int(distanceFromLeft / self.w * float(self.cols)),
               int(distanceFromTop / self.h * float(self.rows)))
      return pixel
    return None
