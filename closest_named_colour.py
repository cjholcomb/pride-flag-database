#!/usr/bin/env python

"""Get closest named colour according to XKCD's colour naming survey
`http://xkcd.com/color/rgb/`.

rgb.txt from `http://xkcd.com/color/rgb.txt` must reside alongside this script.

Exceptions are made for true black and true white: these are omitted from the
searched colours. "black" and "white" are returned only if the queried colour is
true black or true white.
"""
from pylab import np
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import csv
import os
import struct

_initialized = False

def _init():
    global _initialized

    if _initialized:
        return

    global colours

    colours = []
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rgb.txt')
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            if row[0] == '#':
                continue
            try:
                name = row[0]

                # Reserve "black" and "white" for true black and white
                if name == "black" or name == "white":
                    continue

                srgb = sRGBColor.new_from_rgb_hex(row[1])
                colours.append({
                    "name": name,
                    "hex": row[1],
                    "srgb": srgb,
                    "lab": convert_color(srgb, LabColor),
                })
            except:
                pass

    _initialized = True

def closest_named_colour(rgb):
    """Get closest named colour according to XKCD's colour naming survey
    http://xkcd.com/color/rgb/

    Exception: "black" and "white" are only returned when the input colour is
    true black or true white.

    :param rgb: Hex value (3 or 6 digits, with or without leading `#`) or triple
    of rgb colour (0-255).
    :return: name, named_rgb, input_rgb
    """

    _init()

    if isinstance(rgb, basestring):
        srgb = sRGBColor.new_from_rgb_hex(rgb)
    else:
        srgb = sRGBColor(rgb[0], rgb[1], rgb[2], True)
    lab = convert_color(srgb, LabColor)

    # If true black or white, use the reserved values
    upscaled = srgb.get_upscaled_value_tuple()
    if upscaled[0] == 0 and upscaled[1] == 0 and upscaled[2] == 0:
        return "black", '#000000', srgb.get_rgb_hex()
    if upscaled[0] == 255 and upscaled[1] == 255 and upscaled[2] == 255:
        return "white", '#ffffff', srgb.get_rgb_hex()

    # Find closest entry
    arr = [delta_e_cie2000(lab, c["lab"]) for c in colours]
    idx = np.where(arr == np.min(arr))[0][0]
    closest = colours[idx]
    return closest["name"], closest["srgb"].get_rgb_hex(), srgb.get_rgb_hex()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Find the closest XKCD colour name")
    parser.add_argument('colour', type=str, nargs='+',
            help="A colour in 3- or 6-digit hex syntax, with or without leading `#`")
    parser.add_argument('--css', action='store_true',
            help="Output a CSS variable for each colour")
    args = parser.parse_args()


    def camel_case(string):
        output = ''.join(x for x in string.replace("'", '').title() if x.isalpha())
        return output[0].lower() + output[1:]

    for colour in args.colour:
        closest = closest_named_colour(colour)
        if args.css:
            colour_hex = colour
            if colour_hex[0] != '#':
                colour_hex = '#' + colour_hex
            print('--%s: %s;' % (camel_case(closest[0]), colour_hex))
        else:
            print(closest)
