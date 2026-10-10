#!/usr/bin/env python3

"""
Convert and optimise images for display in an Acorn Electron MODE 1 variant
with four colours per line but eight colours available for selection on each
line.

Copyright (C) 2015, 2025 Paul Boddie <paul@boddie.org.uk>

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

import time
from optimiserlib import *
from os.path import split, splitext
try:
    import EXIF
except ImportError:
    import exifread as EXIF
import PIL.Image
import sys

def test():

    "Generate slices of the colour cube."

    size = 512
    for r in (0, 63, 127, 191, 255):
        im = PIL.Image.new("RGB", (size, size))
        for g in range(0, size):
            for b in range(0, size):
                value = get_value((r, (g * 256) / size, (b * 256 / size)))
                im.putpixel((g, b), value)
        im.save("rgb%d.png" % r)

def test_flat(rgb):

    "Generate a flat image for the colour 'rgb'."

    size = 64
    im = PIL.Image.new("RGB", (size, size))
    for y in range(0, size):
        for x in range(0, size):
            im.putpixel((x, y), get_value(rgb))
    im.save("rgb%02d%02d%02d.png" % rgb)

def rotate_and_scale(exif, im, width, height, rotate, scale_factor):

    """
    Using the given 'exif' information, rotate and scale image 'im' given the
    indicated 'width' and 'height' constraints and any explicit 'rotate'
    indication. The returned image will be within the given 'width' and
    'height', filling either or both, and preserve its original aspect ratio.
    """

    if rotate or exif and exif["Image Orientation"].values == [6]:
        im = im.rotate(270)

    w, h = im.size

    # Get the relationship between the base width and the image width.

    width_scale_factor = (width / scale_factor) / w
    height_scale_factor = float(height) / h
    min_scale_factor = min(width_scale_factor, height_scale_factor)

    if min_scale_factor < 1:
        width = int(min_scale_factor * w * scale_factor)
        height = int(min_scale_factor * h)
        return im.resize((width, height))
    elif scale_factor != 1:
        width = int(w * scale_factor)
        return im.resize((width, h))
    else:
        return im

def get_parameter(options, flag, conversion, default, missing):

    """
    From 'options', return any parameter following the given 'flag', applying
    the 'conversion' which has the given 'default' if no valid parameter is
    found, or returning the given 'missing' value if the flag does not appear at
    all.
    """

    try:
        i = options.index(flag)
        try:
            return conversion(options[i+1])
        except (IndexError, ValueError):
            return default
    except ValueError:
        return missing

# Main program.

if __name__ == "__main__":

    # Test options.

    if "--test" in sys.argv:
        test()
        sys.exit(0)
    elif "--test-flat" in sys.argv:
        test_flat((120, 40, 60))
        sys.exit(0)
    elif "--help" in sys.argv or len(sys.argv) < 3:
        basename = split(sys.argv[0])[1]
        sys.stderr.write("""\
Usage:

%s <input filename> <output filename> [ <options> ]

%s -v <filename> [ -C <number of colours> ]

Options are...

-W - Indicate the output width (default is 320)
-C - Number of colours per scanline (default is 4)
-A - Produce an output image with the same aspect ratio as the input
     (useful for previewing)

-s - Saturate the input image (optional float, 1.0 if unspecified)
-d - Desaturate the input image (optional float, 1.0 if unspecified)
-D - Darken the input image (optional float, 1.0 if unspecified)
-B - Brighten the input image (optional float, 1.0 if unspecified)

-l - Use colours producing the least error
     (slower but useful for fewer than 4 colours)

-r - Rotate the input image clockwise explicitly
     (EXIF information is used otherwise)
-p - Generate a separate preview image
-h - Make the preview image with half horizontal resolution (MODE 2)
-v - Verify the output image (loaded if -n is given)
-n - Generate no output image

Specifying -v instead of input filename permits the verification of
previously-generated images. Doing so causes all other options except for -C
to be ignored.

""" % (basename, basename))
        sys.exit(1)

    base_width = width = 320
    base_height = height = 256

    input_filename, output_filename = sys.argv[1:3]
    basename, ext = splitext(output_filename)
    preview_filename = "".join([basename + "_preview", ext])

    verify_only = input_filename == "-v"
    options = sys.argv[3:]

    # Basic image properties.

    width = get_parameter(options, "-W", int, base_width, base_width)
    number_of_colours = get_parameter(options, "-C", int, 4, 4)
    preserve_aspect_ratio = "-A" in options

    # Determine any differing horizontal scale factor.

    scale_factor = float(width) / base_width

    # Preprocessing options that employ parameters.

    saturate = get_parameter(options, "-s", float, 1.0, 0.0)
    desaturate = get_parameter(options, "-d", float, 1.0, 0.0)
    darken = get_parameter(options, "-D", float, 1.0, 0.0)
    brighten = get_parameter(options, "-B", float, 1.0, 0.0)

    # General output options.

    no_normal_output = "-n" in options or verify_only
    verify = "-v" in options or verify_only

    rotate = "-r" in options and not verify_only
    preview = "-p" in options and not verify_only

    half_resolution_preview = "-h" in options
    least_error = "-l" in options

    make_image = not no_normal_output

    # Load the input image if requested.

    if make_image or preview:
        exif = EXIF.process_file(open(input_filename, "rb"))
        im = PIL.Image.open(input_filename).convert("RGB")
        im = rotate_and_scale(exif, im, width, height, rotate, scale_factor)
        image_width, image_height = im.size

        sim = SimpleImage(list(im.getdata()), im.size)
        process_image(sim, saturate, desaturate, darken, brighten)
        im.putdata(sim.getdata())

    # Generate a preview if requested.

    if preview:
        imp = im.copy()
        if half_resolution_preview:
            imp = imp.resize((image_width / 2, image_height))
        sim = SimpleImage(list(imp.getdata()), imp.size)
        convert_image(sim, 8)
        imp.putdata(sim.getdata())
        if half_resolution_preview:
            imp = imp.resize((image_width, image_height))

        # Scale images to a height determined by the aspect ratio.

        if preserve_aspect_ratio and scale_factor != 1:
            imp = imp.resize((image_width, int(image_height * scale_factor)))

        imp.save(preview_filename)

    # Generate an output image if requested.

    if make_image:
        sim = SimpleImage(list(im.getdata()), im.size)
        for x in range(10):
            t0 = time.time()
            convert_image(sim, number_of_colours, least_error)
            t1 = (time.time()-t0)
        print('TIME %.2f' % t1)
        im.putdata(sim.getdata())

        # Scale images to a height determined by the aspect ratio.

        if preserve_aspect_ratio and scale_factor != 1:
            im = im.resize((image_width, int(image_height * scale_factor)))

        im.save(output_filename)

    # Verify the output image (which may be loaded) if requested.

    if verify:
        if no_normal_output:
            im = PIL.Image.open(output_filename).convert("RGB")

        im = SimpleImage(list(im.getdata()), im.size)
        result = count_colours(im, number_of_colours)
        if result is not None:
            y, colours = result
            sys.stdout.write("Image %s: row %d has the following colours: %s\n" % (output_filename, y, "; ".join([repr(c) for c in colours])))

# vim: tabstop=4 expandtab shiftwidth=4
