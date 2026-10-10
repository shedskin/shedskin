#!/usr/bin/env python3

"""
Convert and optimise images for display in an Acorn Electron MODE 1 variant
with four colours per line but eight colours available for selection on each
line.

Copyright (C) 2015 Paul Boddie <paul@boddie.org.uk>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from random import random, randrange
import itertools
import math

corners = [
    (0, 0, 0), (255, 0, 0), (0, 255, 0), (255, 255, 0),
    (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)
    ]

# Basic colour operations.

def within(v, lower, upper):
    return min(max(v, lower), upper)

def clip(v):
    return int(within(v, 0, 255))

def distance(rgb1, rgb2):
    return math.sqrt(pow(abs(rgb1[0] - rgb2[0]), 2) + pow(abs(rgb1[1] - rgb2[1]), 2) + pow(abs(rgb1[2] - rgb2[2]), 2))

def restore(srgb):
    r, g, b = srgb
    return int(r * 255.0), int(g * 255.0), int(b * 255.0)

def scale(rgb):
    r, g, b = rgb
    return r / 255.0, g / 255.0, b / 255.0

def invert(srgb):
    r, g, b = srgb
    return 1.0 - r, 1.0 - g, 1.0 - b

scaled_corners = map(scale, corners)
zipped_corners = list(zip(corners, scaled_corners))

# Colour distribution functions.

def combination(rgb):

    "Return the colour distribution for 'rgb'."

    # Get the colour with components scaled from 0 to 1, plus the inverted
    # component values.

    srgb = scale(rgb)
    rgbi = invert(srgb)
    pairs = list(zip(rgbi, srgb))

    # For each corner of the colour cube (primary and secondary colours plus
    # black and white), calculate the corner value's contribution to the
    # input colour.

    d = []
    for corner, scaled in zipped_corners:
        rs, gs, bs = scaled

        # Obtain inverted channel values where corner channels are low;
        # obtain original channel values where corner channels are high.

        d.append((pairs[0][int(rs)] * pairs[1][int(gs)] * pairs[2][int(bs)], corner))

    # Balance the corner contributions.

    return balance(d)

def complements(rgb):

    "Return 'rgb' and its complement."

    r, g, b = rgb
    return rgb, restore(invert(scale(rgb)))

bases = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
base_complements = list(map(complements, bases))

def balance(d):

    """
    Balance distribution 'd', cancelling opposing values and their complements
    and replacing their common contributions with black and white contributions.
    """

    dd = dict([(value, f) for f, value in d])
    for primary, secondary in base_complements:
        common = min(dd[primary], dd[secondary])
        dd[primary] -= common
        dd[secondary] -= common
    return [(f, value) for value, f in dd.items()]

def combine(d):

    "Combine distribution 'd' to get a colour value."

    out = [0, 0, 0]
    for v, rgb in d:
        out[0] += v * rgb[0]
        out[1] += v * rgb[1]
        out[2] += v * rgb[2]
    return tuple(map(int, out))

def pattern(rgb, chosen=None):

    """
    Obtain a sorted colour distribution for 'rgb', optionally limited to any
    specified 'chosen' colours.
    """

    l = [(f, value) for f, value in combination(rgb) if not chosen or value in chosen]
    l.sort(reverse=True)
    return l

def get_value(rgb, chosen=None, fail=False):

    """
    Get an output colour for 'rgb', optionally limited to any specified 'chosen'
    colours. If 'fail' is set to a true value, return None if the colour cannot
    be expressed using any of the chosen colours.
    """

    l = pattern(rgb, chosen)
    limit = sum([f for f, c in l])
    if not limit:
        if fail:
            return None
        else:
            return l[randrange(0, len(l))][1]

    choose = random() * limit
    threshold = 0
    for f, c in l:
        threshold += f
        if choose < threshold:
            return c
    return c

# Colour processing operations.

def sign(x):
    if x >= 0:
        return 1
    else:
        return -1

def saturate_rgb(rgb, exp):
    r, g, b = rgb
    return saturate_value(r, exp), saturate_value(g, exp), saturate_value(b, exp)

def saturate_value(x, exp):
    return int(127.5 + sign(x - 127.5) * 127.5 * pow(abs(x - 127.5) / 127.5, exp))

def amplify_rgb(rgb, exp):
    r, g, b = rgb
    return amplify_value(r, exp), amplify_value(g, exp), amplify_value(b, exp)

def amplify_value(x, exp):
    return int(pow(x / 255.0, exp) * 255.0)

# Image operations.

def get_colours(im, y):

    "Get a colour distribution from image 'im' for the row 'y'."

    width, height = im.size
    c = {}
    x = 0
    while x < width:
        rgb = im.getpixel((x, y))

        # Sum the colour probabilities.

        for f, value in combination(rgb):
            if value not in c:
                c[value] = f
            else:
                c[value] += f

        x += 1

    d = [(n/width, value) for value, n in c.items()]
    d.sort(reverse=True)
    return d

def get_combinations(c, n):

    """
    Get combinations of colours from 'c' of size 'n' in decreasing order of
    probability.
    """

    all = []
    for l in itertools.combinations(c, n):
        total = 0
        for f, value in l:
            total += f
        all.append((total, l))
    all.sort(reverse=True)
    return [l for total, l in all]

def count_colours(im, colours):

    """
    Count colours on each row of image 'im', returning a tuple indicating the
    first row with more than the given number of 'colours' together with the
    found colours; otherwise returning None.
    """

    width, height = im.size

    y = 0
    while y < height:
        l = set()
        x = 0
        while x < width:
            l.add(im.getpixel((x, y)))
            x += 1
        if len(l) > colours:
            return (y, l)
        y += 1
    return None

def process_image(im, saturate, desaturate, darken, brighten):

    """
    Process image 'im' using the given options: 'saturate', 'desaturate',
    'darken', 'brighten'.
    """

    width, height = im.size

    if saturate or desaturate or darken or brighten:
        y = 0
        while y < height:
            x = 0
            while x < width:
                rgb = im.getpixel((x, y))
                if saturate or desaturate:
                    rgb = saturate_rgb(rgb, saturate and 0.5 / saturate or 2.0 * desaturate)
                if darken or brighten:
                    rgb = amplify_rgb(rgb, brighten and 0.5 / brighten or 2.0 * darken)
                im.putpixel((x, y), rgb)
                x += 1
            y += 1

def convert_image(im, colours, least_error=False):

    "Convert image 'im' to an appropriate output representation."

    width, height = im.size

    y = 0
    while y < height:
        c = get_colours(im, y)

        suggestions = []

        for l in get_combinations(c, colours):
            most = [value for f, value in l]
            error = 0

            x = 0
            while x < width:
                rgb = im.getpixel((x, y))
                value = get_value(rgb, most)
                if least_error:
                    error += distance(value, rgb)
                elif value is None:
                    error += 1
                x += 1

            if not least_error and not error:
                break # use this combination

            suggestions.append((error, l))

        # Find the most accurate suggestion.

        else:
            suggestions.sort()
            most = [value for f, value in suggestions[0][1]] # get the combination

        x = 0
        while x < width:
            rgb = im.getpixel((x, y))
            value = get_value(rgb, most)
            im.putpixel((x, y), value)

            if x < width - 1:
                rgbn = im.getpixel((x+1, y))
                rgbn = (
                    clip(rgbn[0] + (rgb[0] - value[0]) / 4.0),
                    clip(rgbn[1] + (rgb[1] - value[1]) / 4.0),
                    clip(rgbn[2] + (rgb[2] - value[2]) / 4.0)
                    )
                im.putpixel((x+1, y), rgbn)

            if y < height - 1:
                rgbn = im.getpixel((x, y+1))
                rgbn = (
                    clip(rgbn[0] + (rgb[0] - value[0]) / 2.0),
                    clip(rgbn[1] + (rgb[1] - value[1]) / 2.0),
                    clip(rgbn[2] + (rgb[2] - value[2]) / 2.0)
                    )
                im.putpixel((x, y+1), rgbn)

            x += 1

        y += 1

class SimpleImage:

    "An image behaving like PIL.Image."

    def __init__(self, data, size):
        self.data = data
        self.width, self.height = self.size = size

    def copy(self):
        return SimpleImage(self.data[:], self.size)

    def getpixel(self, xy):
        x, y = xy
        return self.data[y * self.width + x]

    def putpixel(self, xy, value):
        x, y = xy
        self.data[y * self.width + x] = value

    def getdata(self):
        return self.data

# Exercise functions for Shedskin.

if __name__ == "__main__":
    rgb = (200, 100, 50)
    saturate_rgb(rgb, 1.0)
    amplify_rgb(rgb, 1.0)
    get_value(rgb)
    get_value(rgb, [(255, 255, 255), (255, 0, 0), (255, 255, 0), (0, 0, 0)])
    combine([(1.0, (255, 0, 0)), (0.0, (0, 0, 0))])
    clip(200.0)
    get_combinations([(0.5, (255, 0, 0)), (0.25, (255, 255, 0)), (0.25, (0, 0, 0))], 2)

    data = [(0, 0, 0), (0, 0, 0)]
    im = SimpleImage(data, (2, 1))
    im2 = im.copy()
    im2.getpixel((0, 0)) == (0, 0, 0)
    im2.putpixel((0, 0), (255, 255, 255))
    im2.getdata() == [(255, 255, 255), (0, 0, 0)]

    get_colours(im, 0) == [(1.0, (0, 0, 0))]
    count_colours(im, 4)

    process_image(im, 1.0, 0.0, 1.0, 0.0)
    convert_image(im, 4, True)

# vim: tabstop=4 expandtab shiftwidth=4
