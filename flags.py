from numpy.core.fromnumeric import _searchsorted_dispatcher
from numpy.lib.financial import _ipmt_dispatcher
from numpy.lib.function_base import average
from flags_database import convert_all
from PIL import Image, ImageDraw
import numpy as np
import math
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

#standardizes commonly used colors (rainbow/skin tone) to control for jpg artifacts
basic_colors = {'hotpink': (255, 105, 180),  'xkcd:red': (229, 0, 0),  'darkorange': (255, 140, 0),  'xkcd:dandelion': (254, 223, 8),  'xkcd:emerald green': (2, 143, 30),  
    'xkcd:turquoise blue': (6, 177, 196),  'xkcd:electric blue': (6, 82, 255),  'xkcd:indigo': (56, 2, 130),  'purple': (128, 0, 128),  
    'black': (0, 0, 0),  'white': (255, 255, 255),  'xkcd:sky blue': (117, 187, 253),  'xkcd:soft pink': (253, 176, 192),  'xkcd:dark brown': (52, 28, 2),
    'xkcd:brown': (101, 55, 0),  'xkcd:rust brown': (139, 49, 3),  'xkcd:browny orange': (202, 107, 2),  'burlywood': (222, 184, 135),  'moccasin': (255, 228, 181),
    'xkcd:sand yellow': (252, 225, 102), 'xkcd:gunmetal':(83, 98, 103)}

chevron_params = {'progress': {'angle': 90, 'start_point': 0.42}, 'demisexual': {'angle': 77, 'start_point': 0.38}}

stripes_widths= {'bisexual': [0, 0.4, 0.6], 'demisexual': [0, .45, .55]}

#flags to use basic palette
basic_flags = {'Qpoc',  'ally',  'basic',  'bear',  'original-pride',  'pride-poc-inclusive',  'progress',  'transgender',  'twospirit'}

#define pizel counts to prevent remaindrs in division
height_lookup = {0:300, 1:300, 2:300, 3:300, 4:300, 5:300, 6:300, 7:301, 8:304, 9:306}

#key statistics to define how colors are ordered
ordering_stat = {'simple':'mean_y', 'mirrored':'max_y', 'chevron': 'range_y'}

def value_sort(dct):
    '''
    Orders a dictionary by values, ascending
    '''
    return {k: v for k, v in sorted(dct.items(), key=lambda item: item[1], reverse=True)}

def color_swatch(colors, vertical = False, swatchsize=100, show = True, save=False, filepath = None):
    '''
    Produces a .png  of color swatch
    
        Parameters:
            colors (list): List of (r, g, b) values, 0-255
            vertical (bool): Determines if image will be stacked vertically or horizontally
            swatchsize (int): Size of each color block, in pixels
            show (bool): Determines if the palette will be shown to the user
            save (bool): Determines if the image will be saved
            filepath (str): Where to save the .png file

        Returns:
            Image object
    '''    
    num_colors = len(colors)
    if vertical:
        height = swatchsize * num_colors
        width = swatchsize
    else:
        height = swatchsize
        width = swatchsize * num_colors
    palette = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(palette)
    posx = 0
    posy = 0
    for color in colors:
        draw.rectangle([posx, posy, posx+swatchsize, posy + swatchsize], fill=color) 
        posx = posx + (swatchsize * (not vertical))
        posy = posy + (swatchsize * (vertical))
    del draw
    palette.show()
    if save:
        palette.save(filepath)
    return palette

def color_distance(color1, color2):
    '''
    Computes the euclidean distance between two colors

        Parameters:
            color1 (tuple): (r, g, b) value, 0-255
            color2 (tuple): (r, g, b) value, 0-255

        Returns:
            Float
    '''    
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
    '''
    Determines a color's nearest neighbor within a given palette

        Parameters:
            color (tuple): (r, g, b) value, 0-255
            palette (list): List of (r, g, b) values, 0-255
        
        Returns:
            (r, g, b) tuple
    '''    
    distances = {}
    for choice in palette:
        distances[choice] = color_distance(color, choice)
    smallest_distance = min(list(distances.values()))
    right_choice =[key for key, value in distances.items() if value == smallest_distance]
    return tuple(right_choice[0])

def transcribe(colors_rgb, palette):
    '''
    Produces hex values and names for provided color

        Parameters:
            colors_rgb (list):  List of (r, g, b) values, 0-255
            palette (dict): Dictionary of rgb values and their names

        Returns:
            Dictionary, three lists as values (rgb tuples, hex strings, name strings)
    '''    
    colors_hex = []
    colors_names =[]
    for color in colors_rgb:
        colors_hex.append( webcolors.rgb_to_hex(color))
        colors_names.append(palette[color])
    return {'RGB':colors_rgb, 'hex':colors_hex, 'names':colors_names}

def rgb_to_cmyk(color):
    '''
    Converts rgb values to cmyk

        Parameters:
            color (tuple): (r, g, b) value, 0-255

        Returns:
            tuple of four strings, c, m, y, and k
    '''
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

def sortby_value(dct):
    '''
    Sorts a single dictionary by valuues, ascending.

    Parameters:
        dct (dict):Single-layer dictionary

    Returns:
        Sorted dictionary
    '''
    sorted_tuples = sorted(dct.items(), key=operator.itemgetter(1))
    sorted_dict = OrderedDict()
    for k, v in sorted_tuples:
        sorted_dict[k] = v
    return sorted_dict

def color_data(stats, img):
    '''
    Documents import statistics on piels within an image, by color

        Parameters:
            stats (dict): Nested (two-layer) dictionary of raw counts and posistions of colors
            img (Pillow Image): Image being analyzed

        Returns:
            Two-layer nested dictionary of color stats
    '''
    matrix = {}
    matrix['full_height'] =  img.size[1]
    matrix['full_width'] = img.size[0]
    for rgb in stats.keys():
        matrix[rgb] = {}
        matrix[rgb]['hex'] = webcolors.rgb_to_hex(rgb)
        matrix[rgb]['volume'] = stats[rgb]['volume']
        x_max = max(stats[rgb]['x_pos'])
        y_max = max(stats[rgb]['y_pos'])
        x_min = min(stats[rgb]['x_pos'])
        y_min = min(stats[rgb]['y_pos'])
        x_mean = sum(stats[rgb]['x_pos']) / len(stats[rgb]['x_pos'])
        y_mean = sum(stats[rgb]['y_pos']) / len(stats[rgb]['y_pos'])
        x_range = x_max - x_min + 1
        y_range = y_max - y_min + 1
        matrix[rgb]['max_x'] = x_max
        matrix[rgb]['min_x'] = x_min
        matrix[rgb]['max_y'] = y_max
        matrix[rgb]['min_y'] = y_min
        matrix[rgb]['mean_x'] = x_mean
        matrix[rgb]['mean_y'] = y_mean
        matrix[rgb]['range_x'] = x_range
        matrix[rgb]['range_y'] = y_range
    return matrix

def pixel_replace(img, conversion, stats = False):
    pixels = img.load()
    width, height = (img.size[0], img.size[1])
    if stats:
        color_stats = {}
        # color_stats[width] = width
        # color_stats[height] = height
    for x in range(width):
        for y in range(height):
            pixels[x, y] = conversion[pixels[x, y]]
            if stats:
                color_new = conversion[pixels[x, y]]
                if color_new not in color_stats.keys():
                    color_stats[color_new] = {}
                    color_stats[color_new]['volume'] = 0
                    color_stats[color_new]['x_pos'] = {x}
                    color_stats[color_new]['y_pos'] = {y}
                color_stats[color_new]['volume'] += 1
                color_stats[color_new]['x_pos'].add(x)
                color_stats[color_new]['y_pos'].add(y)
    if stats:
        return img, color_stats
    else:
        return img

def compute_chevron(angle =  90, apex = None, invert = False):
    angle_sm = (180 - angle) /2
    angle = math.radians(angle)
    angle_sm = math.radians(angle_sm)
    side = (math.sin(angle_sm))/ (math.sin(angle)) 
    width = (side**2) /2
    if not apex:
        apex = width
    point_cen = (apex, 0.5)
    point_top = ((apex - width), 0)
    point_bot = ((apex - width), 1)
    
    return [point_cen, point_bot, (0, 1), (0, 0), point_top ]

    

class Flag:
    """
    Documents metadata for a flag image
        
        Atrributes
        ----------
        name : str
            name of the flag
        num_colors : int
            number of distinct colors in the flag
        num_chevrons : int
            number of distinct stripes in the flag
        num_stripes : int
            number of distinct chevrons in the flag
        num_symbols : int
            number of distinct symbols in the flag
        description : str
            description of flag's meaning
        folder : str
            folder where image can be found
        filepath : str
            full filepath to file
        type : str
            type of flag, describes stucture of image, how colors are arranged
        multiplier : int
            size of output image. 1 = ~300x500, 2 = ~600x1000, etc.
        raw_palette : list
            list of all distinct colors found in original image. (r, g, b) tuples, 0-255.
        base_palette : list
            list of dominant colors (length = num_colors) from original image. (r, g, b) tuples, 0-255.
        final_palette : list
            list of colors closest to each of base palette colors. (r, g, b) tuples, 0-255.
        ordered_palette : list
            list of final palette colors ordered properly for display/image reconstruction. (r, g, b) tuples, 0-255.
        palette_matrix : dict
            dictionary to convert base pallete (keys) to final palette (values)
        base_stats : dict
            dictionary of pixel makeup of flag image
        raw_image : Pillow Image
            original upladed image file
        flat_image : Pillow Image
            image with jpg artifcats removed, all colors changed to base palette
        final_image : Pillow Image
            image with all colors changed to final palette
        palette_df : Pandas dataframe
            Dataframe of info to display to user
    
        Methods
        -------
        definte_type():
            Establishes type attribute
        define_palette():
            Computes palettes for image
        flatten_image(show = False, save = False):
            Creates image with all colors changed to base palette
        order_colors(stats):
            Derives correct order of colors for display to user and reconstruction
        final_image(show = False, save = False):
            Creates image file with all colors changed to named colors
        palette_detail(self, medium = 'Marker', export = False):
            Produces dataframe of display info for user
        reconstruct:
            Creates a new image from scratch with final palette
        """

    def __init__(self, name, folder = 'flag_images', image_multiplier = 2):
        '''
        Establishes attributes from existing database and raw image file

        Parameters
        ----------
            name : str
                name of flag file (without extention)
            folder : str
                folder to find flag image
            image_multiplier : int
                sets multiplier attribute, determines size of output images
        '''
            
        self.name = name
        self.num_colors = int(flag_data.loc[self.name]['Colors'])
        self.num_stripes = int(flag_data.loc[self.name]['Stripes'])
        self.num_chevrons = int(flag_data.loc[self.name]['Chevrons'])
        self.num_symbols = int(flag_data.loc[self.name]['Symbols'])
        self.description = flag_data.loc[self.name]['Description']
        self.folder = folder
        self.filepath = folder + '/' + name + '.jpg'
        self.raw_image = Image.open(self.filepath)
        self.raw_image = self.raw_image.convert(mode ='RGB')
        self.chevron_params = {}
        self.define_type()
        if image_multiplier > 0:
            self.multiplier = image_multiplier
        else:
            self.multiplier = 1
        self.stripe_colors = []
        self.chevron_colors = []
        self.symbol_colors =[]
        if name in stripes_widths.keys():
            self.stripes_dist = stripes_widths[name]
        else:
            self.stripes_dist = None
        
    def define_type(self):
        '''
        Establishes type attribute

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        if flag_data.loc[self.name]['Irregular']:
            self.type = 'irregular'
        elif self.num_chevrons:
            self.type = 'chevron'
            self.chevron_params = chevron_params[self.name]
        elif self.num_colors == self.num_stripes:
            self.type = 'simple'
        elif self.name in {'bigender', 'queer'}:
            self.type = 'simple'
        elif self.num_stripes == (self.num_colors* 2) - 1:
            self.type = 'mirrored'
        elif self.num_symbols:
            self.type = 'symbol'
        else:
            self.type = 'undefined'

    def define_palette(self):
        '''
        Computes palettes for image

        Parameters
        ----------
        None

        Returns
        -------
        dictionary to convert base pallete (keys) to final palette (values)
        '''
        img = self.raw_image
        width, height = img.size
        
        #reduces large images to improve performance
        # if height > 500:
        #     img.thumbnail((500,500))
        by_color = defaultdict(int)
        
        #collects all distinct colors in the image
        for pixel in img.getdata():
            by_color[pixel] += 1
        by_color = dict(by_color)
        
        #establishes palette and sorts
        if self.name in basic_flags:
            palette_choices = list(basic_colors.values())
        else:
            palette_choices = list(palette_lookup.keys())
        sorted_colors = list(value_sort(by_color).keys())
        
        #pulls dominant colors, converts to palette
        base_colors = []
        final_colors = []
        i = 0
        while len(base_colors) < self.num_colors:
            converted = closest_color(sorted_colors[i], palette_choices)
            if converted not in final_colors:
                final_colors.append(converted)
                base_colors.append(sorted_colors[i])
            i += 1
        
        #handle exceptions
        if self.name == 'pride-poc-inclusive':
            final_colors = [(128, 0, 128) if x == (255, 105, 180) else x for x in final_colors]
        if self.name == 'progress':
            final_colors = [(6, 82, 255) if x == (128, 0, 128) else x for x in final_colors]
            final_colors = [(128, 0, 128) if x == (56, 2, 130) else x for x in final_colors]
            

        #stores palettes in attributes
        self.raw_palette = sorted_colors
        self.base_palette = base_colors
        self.final_palette = final_colors
        
        #creates dictionary for conversion
        palette_matrix = dict(zip(base_colors, final_colors))
        self.palette_matrix = palette_matrix
        return palette_matrix

    def flatten_image(self, show = False, save = False):
        '''
        Creates image with all colors changed to base palette

        Parameters
        ----------
            show : bool
                Determines if the palette will be shown to the user
            save : bool 
                Determines if the image will be saved
            

        Returns
        -------
        Pillow Image
        '''
        
        #runs methods to establish required attributes
        if not hasattr(self, 'palette_matrix'):
            self.define_palette()
        
        #establishes conversion dictionary from raw to base palette
        conversion = {}
        for color in self.raw_palette:
            if color not in conversion.keys():
                base_color = closest_color(color, self.base_palette)
                conversion[color] = base_color
        
        #creates an image copy to change
        raw_image = self.raw_image
        flat_image = raw_image.copy()
        flat_image, color_stats = pixel_replace(flat_image, conversion = conversion, stats = True)
        # color_stats = {}
        # pixels = flat_image.load()
        
        # #iterates through pixels, converting and documenting stats
        # for x in range(flat_image.size[0]):
        #     for y in range(flat_image.size[1]):
        #         pixels[x, y] = conversion[pixels[x, y]]
        #         color_new = conversion[pixels[x, y]]
        #         if color_new not in color_stats.keys():
        #             color_stats[color_new] = {}
        #             color_stats[color_new]['volume'] = 0
        #             color_stats[color_new]['x_pos'] = {x}
        #             color_stats[color_new]['y_pos'] = {y}
        #         color_stats[color_new]['volume'] += 1
        #         color_stats[color_new]['x_pos'].add(x)
        #         color_stats[color_new]['y_pos'].add(y)
        
        #converts gathered color data to necessary format
        self.raw_stats = color_stats
        color_stats = (color_data(color_stats, flat_image))
        self.base_stats = color_stats
        
        #establishes proper final palette order. Passes appropriate stat from order_stat by type
        # self.order_colors()
        
        
        #saves image as attribute
        self.flat_image = flat_image
        
        #shows/saves
        if show:
            flat_image.show()
        if save:
            filepath = 'flag_images/flat/' + self.name + '_flat.png'
            flat_image.save(filepath, format='png')

    def map_colors(self):
        if not hasattr(self, 'base_palette'):
            self.flatten_image()
        columns = ['position', 'type', 'base_rgb', 'final_rgb', 'final_hex', 'final_name', 'volume', 'min_x', 'max_x', 'range_x', 'center_x', 'min_y',  'max_y', 'range_y', 'center_y']
        width = self.base_stats['full_width']
        height = self.base_stats['full_height']
        num_pixels = height * width
        df = pd.DataFrame(columns= columns)
        for color in self.base_palette:
            dct = {}
            final_color = self.palette_matrix[color]
            dct['base_rgb'] = color
            dct['final_rgb'] = final_color
            dct['final_hex'] = webcolors.rgb_to_hex(final_color)
            dct['final_name'] = palette_lookup[final_color]
            dct['volume'] = self.base_stats[color]['volume'] / num_pixels
            dct['min_x'] = self.base_stats[color]['min_x'] / width
            dct['max_x'] = self.base_stats[color]['max_x'] / width
            dct['range_x'] = self.base_stats[color]['range_x'] / width
            dct['center_x'] = (dct['range_x'] / 2) + dct['min_x']
            dct['min_y'] = self.base_stats[color]['min_y'] / height
            dct['max_y'] = self.base_stats[color]['max_y'] / height
            dct['range_y'] = self.base_stats[color]['range_y'] / height
            dct['center_y'] = (dct['range_y'] / 2) + dct['min_y']
            df = df.append(dct, ignore_index= True)

        if self.type == 'symbol':
            df = df.sort_values(by = 'volume', ascending = False)
            # return df
            symbol_df = df.sort_values(by = 'volume', ascending = True).head(self.num_symbols)
            # return symbol_df
            df = df.drop(df.tail(1).index)
            # return df
            symbol_df['position'] = list(range(100, ((self.num_symbols+1) *100) , 100))
            symbol_df['type'] = 'symbol'
            # return symbol_df

        #handle exceptions
        if self.name == 'bigender':
            repeat = list(df.iloc[0])
            repeat[-1] = 0.6
            addition = dict(zip(columns, repeat))
            df = df.append(addition, ignore_index= True)
            # return df

        if self.name == 'queer':
            df.iloc[0,-1] = 0
            repeat = list(df.iloc[0])
            repeat[-1] = 1.1
            addition = dict(zip(columns, repeat))
            df = df.append(addition, ignore_index= True)
            # return df

        if self.name == 'demisexual':
            df['range_y'] = [0.45, 0.45, 1, .1]
            df['min_y'] = [0, 0.55, 0, 0.45]
            # return df


        if self.type == 'chevron':
            chevron_df = df.sort_values(by = 'range_y', ascending = False).head(self.num_chevrons)
            chevron_df['type'] = 'chevron'
            chevron_df['position'] = list(range(self.num_stripes + 1, self.num_stripes + self.num_chevrons +1))
            chevron_df.set_index('position', inplace= True)
            # return chevron_df



        
        df = df.sort_values(by = 'range_y').head(self.num_stripes)
        # return df
        df = df.sort_values(by = 'min_y')
        # return df
        if self.type == 'mirrored':
            # return df
            mirrored_df = df.head(self.num_colors-1).sort_values(by = 'min_y', ascending= False)
            # return mirrored_df
            df = df.sort_values(by = 'max_y', ascending= False).append(mirrored_df)
            # return df
        if self.name in {'bigender', 'queer'}:
            df = df.sort_values(by = 'center_y')
        df['position'] = list(range(1, self.num_stripes+1))
        df['type'] = 'stripe'
        if self.type == 'symbol':
            df = df.append(symbol_df)
        df.set_index('position', inplace = True)
        
        if self.type == 'chevron':
            df = df.append(chevron_df)

        df= self.recalibrate_map(df, stripe_dist = self.stripes_dist)


        
        self.color_map = df
        return df

        # if self.type == 'simple':
            
        #     stripes_positions = dict(zip(stripes_df['final_name'], range(1, self.num_stripes + 1)))
        #     stripes_df['position'] = stripes_df['final_name'].map(stripes_positions)
        #     stripes_df['type'] = 'stripe'
        #     df = stripes_df
        #     df = self.recalibrate_map(df)
        # if self.type == 'mirrored':
        #     stripes_df = df.sort_values(by = 'range_y').head(self.num_stripes).sort_values(by = 'max_y')
        #     mirrored_df = stripes_df.tail(self.num_colors-1)
        #     stripes_df = stripes_df.sort_values(by = 'max_y', ascending= False).append(mirrored_df)
        #     stripes_df['position'] = list(range(1, self.num_stripes+1))
        #     stripes_df['type'] = 'stripe'
        #     df = stripes_df
        #     df= self.recalibrate_map(df)

        #     # mirrored_df = stripes_df.sort_values(by = 'position', ascending= False).t(self.num_colors - 1)
        #     # return mirrored_df
        # # if self.type == 'mirrored':
        #     # stripes_df['position'] = stripes_positions[df['final_name']]
        
        # self.color_map = df
        # return df

    def recalibrate_map(self, df, stripe_dist , chevron_dist = None):
        if not stripe_dist:
            ratio = 1 /self.num_stripes
            stripe_dist = np.linspace(0, 1 - ratio, self.num_stripes)
            # print(df)
        if not chevron_dist:
            if self.num_chevrons > 0:
                start_point =  self.chevron_params['start_point']
                angle = self.chevron_params['angle']
                chevron_width = start_point / self.num_chevrons
                chevron_dist = np.linspace(start_point, chevron_width * 1.5, self.num_chevrons)
            # print(chevron_dist)
        points = {}
        # end = self.num_stripes
        if self.type == 'mirrored':
            end = self.num_colors

        for index, row in df.iterrows():
            # pos = row['position']
            pos = index
            # print(pos, row['final_name'])
            if row['type'] == 'stripe':
                min_x = 0
                max_x = 1
                range_x = 1
                center_x = 0.5
                min_y = stripe_dist[index - 1]
                if pos == len(stripe_dist):
                    max_y = 1
                else:
                    max_y = stripe_dist[pos]
                range_y = max_x - max_y
                center_y = (range_y /2) + min_y
                point_rb = (max_x, max_y)
                point_lb = (min_x, max_y)
                point_lt = (min_x, min_y)
                point_rt = (max_x, min_y)

                # df.at[index, 'min_x'] = max_x
                # df.at[index, 'max_x'] = max_y
                # df.at[index, 'range_x'] = range_x
                # df.at[index, 'center_x'] = center_x
                # df.at[index, 'min_y'] = min_y
                # df.at[index, 'max_y'] = max_y
                # df.at[index, 'range_y'] = row['max_y'] - row['min_y']
                # df.at[index, 'center_y'] = (row['range_y'] / 2) + row['min_y']

                points[(row['final_rgb'], pos)] = [point_rb, point_lb, point_lt, point_rt]
                # if index == end:
                    # break
        
            elif row['type'] == 'chevron':
                
                chevron_num = pos - self.num_stripes
                start_point = 0.45

                if self.num_chevrons == 1:
                    points[(row['final_rgb'], pos)] = [(chevron_dist[0], 0.5), (0, 1), (0, 0)]
                else:
                    points[(row['final_rgb'], pos)] = compute_chevron(angle =  angle, apex = chevron_dist[chevron_num - 1])
        
        self.points = points
        # print(len(points), points)
        return df
 
    def extract_symbol(self, save = False, show = False):
        if not hasattr(self, 'base_stats'):
            self.flatten_image()
        volumes = [self.base_stats[x]['volume'] for x in self.base_stats.keys() if type(self.base_stats[x]) == dict]
        base_colors = list(self.base_stats.keys())[2:]
        symbol_colors = list(value_sort(dict(zip(base_colors, volumes))).keys())
        # print(self.num_symbols)
        symbol_colors = symbol_colors[-1*(self.num_symbols):]
        self.symbol_colors = symbol_colors
        symbol_conversion = dict(zip(symbol_colors, [self.palette_matrix[x] for x in symbol_colors]))
        symbol_stats = {}
        for color in symbol_colors:
            symbol_stats[color] = self.base_stats.pop(color)
        self.symbol_stats = symbol_stats
        img = self.flat_image
        buffer = 0
        x_buffer = 0
        y_buffer = 0
        for color in symbol_stats.keys():
            ranges = []
            ranges.append(symbol_stats[color]['range_y'])
            ranges.append(symbol_stats[color]['range_x'])
            buffer = max(ranges) * 0.1
        img = img.crop((symbol_stats[color]['min_x'] - buffer, symbol_stats[color]['min_y'] - buffer , symbol_stats[color]['max_x'] + buffer, symbol_stats[color]['max_y'] + buffer))
        symbol_position = (symbol_stats[color]['min_x'] - buffer, symbol_stats[color]['min_y'] - buffer)
        self.symbol_position = symbol_position 

        for base, final in self.palette_matrix.items():
            if base not in symbol_conversion.keys():
                symbol_conversion[base] = (255, 255, 255, 0)
        # img.show()
        symbol_conversion[(0, 0, 0)] = (255, 255, 255, 0)
        # print(symbol_conversion)
        self.symbol_matrix = symbol_conversion
        # print(symbol_conversion)
        img = (pixel_replace(img, symbol_conversion, stats = False))
        square = max(img.size)
        # print(square)
        background = Image.new('RGB', (square, square), (255, 255, 255, 0))
        # background.show()
        if img.size[0] ==  square:
            background.paste(img, (0, int((square - img.size[1])/2)))
            # print(background.size)
            img = background
            # background.show()
        elif img.size[1]== square:
            background.paste(img, (int((square - img.size[0])/2), 0))
            # print(background.size)
            img = background
        img.resize((500, 500))
        self.symbol_extract = img
        if save:
            filepath = 'flag_images/symbols/' + self.name + '_symbol.png'
            img.save(filepath)
        if show:
            img.show()
        return img

    def extract_stencil(self, save = True):
        if not hasattr(self, 'symbol_matrix'):
            self.extract_symbol()
        stencil_conversion = {}
        for k, v in self.symbol_matrix.items():
            if k in self.symbol_colors:
                stencil_conversion[v] = (0,0,0)
            else:
                stencil_conversion[v] = (255, 255, 255)
        if (255, 255, 255) not in stencil_conversion.keys():
                stencil_conversion[255,255,255] = (255, 255, 255)

        img = pixel_replace(self.symbol_extract, stencil_conversion)
        img.show()

    def order_colors(self):
        '''
        Produces list of colors in correct order for palette

        Parameters
        ----------
            List of rgb colors ordered properly (stripes top-to-bottom, chevrons inside to outside, symbols)

        Returns
        -------
        Pillow Image
        '''
        
        if not hasattr(self, 'base_stats'):
            self.flatten_image()
        
        
        
        #orders appropriate stats (defined by type)
        # stat_sort = list(sorted_dict.keys())
        
        #simple flag only needs a direct list
        if self.type == 'simple':
            stats_dict = dict(zip(self.base_palette, [self.base_stats[x]['mean_y'] for x in self.base_palette]))
            stats_dict = sortby_value(stats_dict)
            ordered_palette = dict(zip(stats_dict.keys(), [self.palette_matrix[x] for x in stats_dict.keys()]))
            self.palette_matrix = ordered_palette
            self.ordered_palette = list(ordered_palette.values())
            return ordered_palette
       
       #mirrored flag duplicates the tail
        elif self.type == 'mirrored':
            stats_dict = dict(zip(self.base_palette, [self.base_stats[x]['max_y'] for x in self.base_palette]))
            stats_dict = sortby_value(stats_dict)            
            ordered_palette = dict(zip(stats_dict.keys(), [self.palette_matrix[x] for x in stats_dict.keys()]))
            self.palette_matrix = ordered_palette
            
            mirror_add = int(self.num_stripes - self.num_colors)
            mirror_back = (list(ordered_palette.keys()))[-mirror_add:]
            mirror_back.reverse()
            mirrored_palette = mirror_back + list(stats_dict.keys())
            self.ordered_palette = mirrored_palette
            return mirrored_palette

        #chevron flags ???
        elif self.type == 'chevron':
            rangey_dict = dict(zip(self.base_palette, [self.base_stats[x]['range_y'] for x in self.base_palette]))
            rangey_dict = sortby_value(rangey_dict)
            meanx_dict = dict(zip(self.base_palette, [self.base_stats[x]['mean_x'] for x in self.base_palette]))
            meanx_dict = sortby_value(meanx_dict)
            meany_dict = dict(zip(self.base_palette, [self.base_stats[x]['mean_y'] for x in self.base_palette]))
            meany_dict = sortby_value(meany_dict)
            maxx_dict = dict(zip(self.base_palette, [self.base_stats[x]['max_x'] for x in self.base_palette]))
            maxx_dict = sortby_value(maxx_dict)

            stripes = list(rangey_dict.keys())[:self.num_stripes]
            stripes_list = [x for x in meany_dict.keys() if x in stripes]
            chevrons = list(meanx_dict.keys())[:self.num_chevrons]
            self.chevron_colors = chevrons
            ordered_palette = stripes_list
            ordered_palette.extend(chevrons)
            self.ordered_palette = ordered_palette
            return ordered_palette

    def final_image(self, show = True, save = False):
        '''
        Creates image file with all colors changed to named colors

        Parameters
        ----------
            show : bool
                Determines if the palette will be shown to the user
            save : bool 
                Determines if the image will be saved
            

        Returns
        -------
        Pillow Image
        '''
        
        #uses reconstruct method if flag is of appropriate type
        if self.type in ('simple', 'mirrored'):
            img = self.reconstruct()
        else:
        
            #runs methods to create needed attributes
            if not hasattr(self, 'flat_image'):
                self.flatten_image()
            
            #iterates through image, changing pixels
            conversion = self.palette_matrix
            img = self.flat_image.copy()
            pixels = img.load()
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    pixels[x, y] = conversion[pixels[x, y]]
            
            #writes image as attribute
            self.final_image = img
        
        #show and save
        if show:
            img.show()
        if save:
            filepath = 'flag_images/final/' + self.name + '.png'
            img.save(filepath, format = 'png')
        return img

    def palette_detail(self, medium = 'Marker', export = False):
        '''
        Produces dataframe of display info for user

        Parameters
        ----------
            medium : str
                Adds columns for user to provide physical swatch
            export : bool 
                Determines if the dataframe will be saved as a csv
            

        Returns
        -------
        Pandas Dataframe
        '''
        
        #runs methods to create needed attributes
        if not hasattr(self, 'ordered_palette'):
            self.flatten_image()
        
        #establishes structure of dataframe
        columns = ['flag', 'NAME', 'HEX', 'Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Black', 'Preview']
        if medium:
            columns.extend([medium, 'Swatch'])
        df = pd.DataFrame(columns = columns)
        
        #iterates through palette, fills dataframe
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
            row = [self.name, color_name, color_hex, color_red, color_green, color_blue, color_cyan, color_magenta, color_yellow, color_black, '']
            if medium:
                row.extend(['', ''])
            df = df.append(dict(zip(columns, row)), ignore_index= True)
        
        #sets attribute
        self.palette_df = df
        
        #exports the file
        if export:
            filepath = 'flag_images/dataframes/' + self.name + '.csv'
            (df.to_csv(filepath))
        return df

    def reconstruct(self):
        '''
        Recreates image (if possible)

        Parameters
        ----------
            None
            
        Returns
        -------
        Pillow Image
        '''
        
        #runs methods to create needed attributes
        if not hasattr(self, 'color_map'):
            self.map_colors()
        
        #derives size of output image
        height = height_lookup[self.num_stripes]
        height = height * self.multiplier
        width = 500 * self.multiplier
        num_pixels = height * width

        conversion = {'volume':num_pixels, 'min_x':width, 'max_x':width, 'range_x':width, 'center_x':width, 'min_y':height,  'max_y':height, 'range_y':height, 'center_y':height}

        df = self.color_map
        for stat, multiplier in conversion.items():
            df[stat] = df[stat].apply(lambda x: int(x * multiplier))
            df['min_y'] = df['min_y'].apply(lambda x: x + 1 if x > 1 else 0)
        #creates image object
        img = Image.new('RGB', size = (width, height))
        draw = ImageDraw.Draw(img)
        for color, points in self.points.items():
            new_points = []
            for point in points:
                new_points.append( (point[0] * width, point[1]* height))
            # print(new_points, color)
            draw.polygon(new_points, fill =  color[0])
            # img.show()
            # input('x')



        # for index, row in df.iterrows():
        #     points = []
        #     for point in row['points']:
        #         # print(point[0], point[1])
        #         points.append(tuple((point[0] * width, point[1]* height)))
        #     df.at[index, 'points'] = points
        #     if row['type'] == 'stripe':
        #         draw.rectangle([row['points']], fill = row['final_rgb'])
            # if row['type'] == 'chevron':
            #     if index == self.num_stripes + 1:
            #         point1 = (row['max_x'], height / 2)
            #         point2 = (df.loc[1]['min_x'], height)
            #         point3 = (row['min_x'], height)
            #         point4 = (row['min_x'], 0)
            #         point5 = (df.loc[1]['min_x'], 0)
            #         points = [point1, point2, point3, point4, point5]
            #         draw.polygon(points, fill = row['final_rgb'])
            #     elif row['min_x'] > 0:
            #         point1 = (row['max_x'], height / 2)
            #         point2 = (df.loc[index-1]['min_x'], height)
            #         point3 = (row['min_x'], height)
            #         point4 = (row['min_x'], 0)
            #         point5 = (df.loc[index-1]['min_x'], 0)
            #         points = [point1, point2, point3, point4, point5]
            #         draw.polygon(points, fill = row['final_rgb'])
            #     elif ((row['min_y'] == 0) & (row['min_x'] == 0)):
            #         point1 = (row['max_x'], height / 2)
            #         point2 = (df.loc[index-1]['min_x'], height)
            #         point3 = (0, height)
            #         point4 = (0, 0)
            #         point5 = (df.loc[index-1]['min_x'], 0)
            #         points = [point1, point2, point3, point4, point5]
            #         draw.polygon(points, fill = row['final_rgb'])
            #     else:
            #         point1 = (row['max_x'], height / 2)
            #         point2 = (0, row['max_y'])
            #         point2 = (0, row['min_y'])
            #         points = [point1, point2, point3]
            #         draw.polygon(points, fill = row['final_rgb'])


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