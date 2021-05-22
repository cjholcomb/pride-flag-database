from flags_database import convert_all
from PIL import Image, ImageDraw
# from PIL import ImageFilter
# import argparse
# import sys
# import colorsys
# from numpy.lib.type_check import _imag_dispatcher
import webcolors
# import re
# import os
import pandas as pd
from collections import defaultdict
# import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
# from operator import itemgetter
from math import sqrt

basic_colors = {'hotpink': (255, 105, 180),  'xkcd:red': (229, 0, 0),  'darkorange': (255, 140, 0),  'xkcd:dandelion': (254, 223, 8),  'xkcd:emerald green': (2, 143, 30),  
    'xkcd:turquoise blue': (6, 177, 196),  'xkcd:electric blue': (6, 82, 255),  'xkcd:indigo': (56, 2, 130),  'purple': (128, 0, 128),  
    'black': (0, 0, 0),  'white': (255, 255, 255),  'xkcd:sky blue': (117, 187, 253),  'xkcd:soft pink': (253, 176, 192),  'xkcd:dark brown': (52, 28, 2),
    'xkcd:brown': (101, 55, 0),  'xkcd:rust brown': (139, 49, 3),  'xkcd:browny orange': (202, 107, 2),  'burlywood': (222, 184, 135),  'moccasin': (255, 228, 181),
    'xkcd:sand yellow': (252, 225, 102)}

basic_flags ={'Qpoc',  'ally',  'basic',  'bear',  'original-pride',  'pride-poc-inclusive',  'progress',  'transgender',  'twospirit'}

def value_sort(dct):
    return {k: v for k, v in sorted(dct.items(), key=lambda item: item[1], reverse=True)}

def color_swatch(colors, swatchsize=100, save=False, label = False):
    num_colors = len(colors)
    palette = Image.new('RGB', (swatchsize*num_colors, swatchsize))
    draw = ImageDraw.Draw(palette)
    posx = 0
    for color in colors:
        draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=color) 
        posx = posx + swatchsize
    del draw
    palette.show(title = label)
    if save:
        palette.save('swatches/' + palette + '/' + flag_name + '_' + '.png', format = 'png')

def color_distance(color1, color2):
    r1 = color1[0]
    r2 = color2[0]
    g1 = color1[1]
    g2 = color2[1]
    b1 = color1[2]
    b2 = color2[2]

    rd = r1-r2
    gd = g1-g2
    bd = b1-b2
    
    sum = (rd)**2 + (gd)**2 +(bd)**2
    return round(sqrt(sum), 2)

def closest_color(color, palette):
    distances = {}
    for choice in palette:
        distances[choice] = color_distance(color, choice)
    smallest_distance = min(list(distances.values()))
    right_choice =[key for key, value in distances.items() if value == smallest_distance]
    return tuple(right_choice[0])

def transcribe(colors_rgb, palette):
    colors_hex = []
    colors_names =[]
    for color in colors_rgb:
        _hex = webcolors.rgb_to_hex(color)
        colors_hex.append(_hex)
        colors_names.append(palettes[palette]['hex_to_name'][_hex])
    return {'RGB':colors_rgb, 'hex':colors_hex, 'names':colors_names}

def rgb_to_cmyk(color):
    r = color[0]
    g = color[1]
    b = color[2]
    if (r, g, b) == (0, 0, 0):
        return '0%', '0%', '0%', '100%'

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255

    # extract out k [0, 1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0,CMYK_SCALE]
    _c = str(round(c*100, 2)) + "%"
    _m = str(round(m*100, 2)) + "%"
    _y = str(round(y*100, 2)) + "%"
    _k = str(round(k*100, 2)) + "%"
    
    return _c, _m, _y, _k
class Flag:
    '''
    stores all relevant info for a given flag
    '''

    def __init__(self, name, folder = 'flag_images'):
        self.name = name
        self.num_colors = flag_data.loc[self.name]['Colors']
        self.description = flag_data.loc[self.name]['Description']
        self.folder = folder
        self.filepath = folder + '/' + name + '.jpg'
        self.raw_image = Image.open(self.filepath)
        self.raw_image = self.raw_image.convert(mode ='RGB')

    def define_palette(self):
        img = self.raw_image
        width, height = img.size
        if height > 500:
            img.thumbnail((500,500))
        by_color = defaultdict(int)
        for pixel in img.getdata():
            by_color[pixel] += 1
        by_color = dict(by_color)
        if self.name in basic_flags:
            palette_choices = list(basic_colors.values())
        else:
            palette_choices = list(palette_lookup.keys())
        sorted_colors = list(value_sort(by_color).keys())
        base_colors = []
        final_colors = []
        i = 0
        while len(base_colors) < self.num_colors:
            converted = closest_color(sorted_colors[i], palette_choices)
            if converted not in final_colors:
                final_colors.append(converted)
                base_colors.append(sorted_colors[i])
            i += 1
        self.raw_palette = sorted_colors
        self.base_palette = base_colors
        self.final_palette = final_colors
        palette_matrix = dict(zip(base_colors, final_colors))
        self.palette_matrix = palette_matrix
        return palette_matrix

    def flatten_image(self, show = False, save = False):
        if not hasattr(self, 'palette_matrix'):
            self.define_palette()
        conversion = {}
        for color in self.raw_palette:
            if color not in conversion.keys():
                conversion[color] = closest_color(color, self.base_palette)
        raw_image = self.raw_image
        flat_image = raw_image.copy()
        pixels = flat_image.load()
        for x in range(flat_image.size[0]):
            for y in range(flat_image.size[1]):
                pixels[x, y] = conversion[pixels[x, y]]
        self.flat_image = flat_image
        if show:
            flat_image.show()
        if save:
            filepath = 'flag_images/flat/' + self.name + '_flat.png'
            flat_image.save(filepath, format='png')

    def final_image(self, show = True, save = False):
        if not hasattr(self, 'flat_image'):
            self.flatten_image()
        conversion = self.palette_matrix
        img = self.flat_image.copy()
        pixels = img.load()
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                pixels[x, y] = conversion[pixels[x, y]]
        self.final_image = img
        if show:
            img.show()
        if save:
            filepath = 'flag_images/final/' + self.name + '.png'
            img.save(filepath, format = 'png')
        return img

    def palette_detail(self, medium = 'Marker', export = False):
        if not hasattr(self, 'palette_matrix'):
            self.define_palette()
        columns = ['flag', 'NAME', 'HEX', 'Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Black', 'Preview', medium, 'Swatch']
        df = pd.DataFrame(columns = columns)
        colors = list(self.palette_matrix.values())
        for color in colors:
            color_tuple = tuple(color)
            color_hex = webcolors.rgb_to_hex(color_tuple)
            color_red = color_tuple[0]
            color_green = color_tuple[1]
            color_blue = color_tuple[2]
            color_name = palette_lookup[color_tuple]
            if color_name[0:4] == 'xkcd':
                    color_name = color_name[5:]
            color_cyan, color_magenta, color_yellow, color_black = rgb_to_cmyk(color_tuple)
            row = [self.name, color_name, color_hex, color_red, color_green, color_blue, color_cyan, color_magenta, color_yellow, color_black, '', '', '']
            df = df.append(dict(zip(columns, row)), ignore_index= True)
        # df.set_index('NAME', inplace = True)
        self.palette_df = df
        if export:
            filepath = 'flag_images/dataframes/' + self.name + '.csv'
            (df.to_csv(filepath))
        return df

if __name__ == '__main__':
    flag_data = pd.read_csv('flag_data.csv', sep = '|')
    flag_data.set_index('Name', inplace=True)
    main_flags = list(flag_data.index[flag_data.Folder == 'main'])
    fetish_flags = list(flag_data.index[flag_data.Folder == 'fetish'])
    palette_lookup = {}
    for name, _hex in mcolors.get_named_colors_mapping().items():
        if type(_hex) == str:
            rgb = tuple(webcolors.hex_to_rgb(_hex))
            palette_lookup[rgb] = name