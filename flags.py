from numpy.lib.financial import _ipmt_dispatcher
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
from collections import defaultdict, OrderedDict
# import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
# from operator import itemgetter
from math import sqrt
import operator

basic_colors = {'hotpink': (255, 105, 180),  'xkcd:red': (229, 0, 0),  'darkorange': (255, 140, 0),  'xkcd:dandelion': (254, 223, 8),  'xkcd:emerald green': (2, 143, 30),  
    'xkcd:turquoise blue': (6, 177, 196),  'xkcd:electric blue': (6, 82, 255),  'xkcd:indigo': (56, 2, 130),  'purple': (128, 0, 128),  
    'black': (0, 0, 0),  'white': (255, 255, 255),  'xkcd:sky blue': (117, 187, 253),  'xkcd:soft pink': (253, 176, 192),  'xkcd:dark brown': (52, 28, 2),
    'xkcd:brown': (101, 55, 0),  'xkcd:rust brown': (139, 49, 3),  'xkcd:browny orange': (202, 107, 2),  'burlywood': (222, 184, 135),  'moccasin': (255, 228, 181),
    'xkcd:sand yellow': (252, 225, 102)}

basic_flags = {'Qpoc',  'ally',  'basic',  'bear',  'original-pride',  'pride-poc-inclusive',  'progress',  'transgender',  'twospirit'}

height_lookup = {0:300, 1:300, 2:300, 3:300, 4:300, 5:300, 6:300, 7:301, 8:304, 9:306}

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

def color_data(stats):
    matrix = {}
    for rgb in stats.keys():
        matrix[rgb] = {}
        matrix[rgb]['hex'] = webcolors.rgb_to_hex(rgb)
        matrix[rgb]['volume'] = stats[rgb]['volume']
        x_max = max(stats[rgb]['x_pos'])
        y_max = max(stats[rgb]['y_pos'])
        x_min = min(stats[rgb]['x_pos'])
        y_min = min(stats[rgb]['y_pos'])
        x_range = x_max - x_min
        y_range = y_max - y_min
        matrix[rgb]['max_x'] = x_max
        matrix[rgb]['min_x'] = x_min
        matrix[rgb]['max_y'] = y_max
        matrix[rgb]['min_y'] = y_min
        matrix[rgb]['range_x'] = x_range
        matrix[rgb]['range_y'] = y_range
    return matrix

class Flag:
    '''
    stores all relevant info for a given flag
    '''

    def __init__(self, name, folder = 'flag_images', image_multiplier = 2):
        self.name = name
        self.num_colors = flag_data.loc[self.name]['Colors']
        self.num_stripes = flag_data.loc[self.name]['Stripes']
        self.num_chevrons = flag_data.loc[self.name]['Chevrons']
        self.num_symbols = flag_data.loc[self.name]['Symbols']
        self.irregular = flag_data.loc[self.name]['Irregular']
        self.description = flag_data.loc[self.name]['Description']
        self.folder = folder
        self.filepath = folder + '/' + name + '.jpg'
        self.raw_image = Image.open(self.filepath)
        self.raw_image = self.raw_image.convert(mode ='RGB')
        self.define_type()
        if image_multiplier > 0:
            self.multiplier = image_multiplier
        else:
            self.multiplier = 1

    def define_type(self):
        if self.irregular:
            self.type = 'irregular'
        elif self.num_chevrons:
            self.type = 'chevron'
        elif self.num_colors == self.num_stripes:
            self.type = 'simple'
        elif self.num_stripes == (self.num_colors* 2) - 1:
            self.type = 'mirrored'
        elif self.num_symbols:
            self.type = 'symbol'
        else:
            self.type = 'undefined'

    
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
                base_color = closest_color(color, self.base_palette)
                conversion[color] = base_color
        raw_image = self.raw_image
        flat_image = raw_image.copy()
        color_stats = {}
        pixels = flat_image.load()
        for x in range(flat_image.size[0]):
            for y in range(flat_image.size[1]):
                pixels[x, y] = conversion[pixels[x, y]]
                color_new = conversion[pixels[x, y]]
                if color_new not in color_stats.keys():
                    color_stats[color_new] = {}
                    color_stats[color_new]['volume'] = 0
                    color_stats[color_new]['x_pos'] = {x}
                    color_stats[color_new]['y_pos'] = {y}
                color_stats[color_new]['volume'] += 1
                color_stats[color_new]['x_pos'].add(x)
                color_stats[color_new]['y_pos'].add(y)
        color_stats = (color_data(color_stats))
        self.base_stats = color_stats
        color_heights = [color_stats[x]['max_y'] for x in self.base_palette]
        color_order = self.order_colors(dict(zip(self.base_palette, color_heights)))
        self.ordered_palette = [self.palette_matrix[x] for x in color_order]
        self.flat_image = flat_image
        if show:
            flat_image.show()
        if save:
            filepath = 'flag_images/flat/' + self.name + '_flat.png'
            flat_image.save(filepath, format='png')

    def order_colors(self, stats):
        sorted_tuples = sorted(stats.items(), key=operator.itemgetter(1))
        sorted_dict = OrderedDict()
        for k, v in sorted_tuples:
            sorted_dict[k] = v
        ymax_sort = list(sorted_dict.keys())
        if self.type == 'simple':
            return ymax_sort
        elif self.type == 'mirrored':
            mirror_add = int(self.num_stripes - self.num_colors)
            # print(mirror_add)
            mirror_back = ymax_sort[-mirror_add:]
            mirror_back.reverse()
            # print(mirror_back)
            mirrored_palette = mirror_back + ymax_sort
            # ymax_sort.extend(mirror_back)
            return mirrored_palette


    def final_image(self, show = True, save = False):
        if self.type in ('simple', 'mirrored'):
            img = self.reconstruct()
        else:
            if not hasattr(self, 'flat_image'):
                self.flatten_image()
            conversion = self.palette_matrix
            img = self.flat_image.copy()
            pixels = img.load()
            color_stats = {}
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    color_old = pixels[x, y]
                    color_new = conversion[pixels[x, y]]
                    pixels[x, y] = conversion[pixels[x, y]]
            self.final_image = img
        if show:
            img.show()
        if save:
            filepath = 'flag_images/final/' + self.name + '.png'
            img.save(filepath, format = 'png')
        return img

    def palette_detail(self, medium = 'Marker', export = False):
        if not hasattr(self, 'ordered_palette'):
            self.flatten_image()
        columns = ['flag', 'NAME', 'HEX', 'Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Black', 'Preview', medium, 'Swatch']
        df = pd.DataFrame(columns = columns)
        colors = self.ordered_palette
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

    def reconstruct(self):
        if not hasattr(self, 'flat_image'):
            self.flatten_image()
        height = height_lookup[self.num_stripes]
        height = height * self.multiplier
        width = 500 * self.multiplier
        img = Image.new('RGB', size = (width, height))
        draw = ImageDraw.Draw(img)
        y = 0
        stripe_height = height/self.num_stripes
        for color in self.ordered_palette:
            draw.rectangle([0, y, width, y + stripe_height], fill = color)
            if y == 0:
                y = 1
            y += stripe_height
        del draw
        return img


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