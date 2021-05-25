from numpy.lib.financial import _ipmt_dispatcher
from numpy.lib.function_base import average
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

#standardizes commonly used colors (rainbow/skin tone) to control for jpg artifacts
basic_colors = {'hotpink': (255, 105, 180),  'xkcd:red': (229, 0, 0),  'darkorange': (255, 140, 0),  'xkcd:dandelion': (254, 223, 8),  'xkcd:emerald green': (2, 143, 30),  
    'xkcd:turquoise blue': (6, 177, 196),  'xkcd:electric blue': (6, 82, 255),  'xkcd:indigo': (56, 2, 130),  'purple': (128, 0, 128),  
    'black': (0, 0, 0),  'white': (255, 255, 255),  'xkcd:sky blue': (117, 187, 253),  'xkcd:soft pink': (253, 176, 192),  'xkcd:dark brown': (52, 28, 2),
    'xkcd:brown': (101, 55, 0),  'xkcd:rust brown': (139, 49, 3),  'xkcd:browny orange': (202, 107, 2),  'burlywood': (222, 184, 135),  'moccasin': (255, 228, 181),
    'xkcd:sand yellow': (252, 225, 102)}

#flags to use basic palette
basic_flags = {'Qpoc',  'ally',  'basic',  'bear',  'original-pride',  'pride-poc-inclusive',  'progress',  'transgender',  'twospirit'}

#define pizel counts to prevent remaindrs in division
height_lookup = {0:300, 1:300, 2:300, 3:300, 4:300, 5:300, 6:300, 7:301, 8:304, 9:306}

#key statistics to define how colors are ordered
ordering_stat = {'simple':'mean_y', 'mirrored':'max_y'}

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

def color_data(stats):
    '''
    Documents import statistics on piels within an image, by color

        Parameters:
            stats (dict): Nested (two-layer) dictionary of raw counts and posistions of colors

        Returns:
            Two-layer nested dictionary of color stats
    '''
    matrix = {}
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
        x_range = x_max - x_min
        y_range = y_max - y_min
        matrix[rgb]['max_x'] = x_max
        matrix[rgb]['min_x'] = x_min
        matrix[rgb]['max_y'] = y_max
        matrix[rgb]['min_y'] = y_min
        matrix[rgb]['mean_x'] = x_mean
        matrix[rgb]['mean_y'] = y_mean
        matrix[rgb]['range_x'] = x_range
        matrix[rgb]['range_y'] = y_range
    return matrix

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
        self.num_colors = flag_data.loc[self.name]['Colors']
        self.num_stripes = flag_data.loc[self.name]['Stripes']
        self.num_chevrons = flag_data.loc[self.name]['Chevrons']
        self.num_symbols = flag_data.loc[self.name]['Symbols']
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
        elif self.num_colors == self.num_stripes:
            self.type = 'simple'
        elif self.name in {'bigender'}:
            self.type = 'simple'
        elif self.name in {'queer'}:
            self.type = 'mirrored'
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
        if height > 500:
            img.thumbnail((500,500))
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
        color_stats = {}
        pixels = flat_image.load()
        
        #iterates through pixels, converting and documenting stats
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
        
        #converts gathered color data to necessary format
        color_stats = (color_data(color_stats))
        self.base_stats = color_stats
        
        #establishes proper final palette order. Passes appropriate stat from order_stat by type
        color_index = [color_stats[x][ordering_stat[self.type]] for x in self.base_palette]
        color_order = self.order_colors(dict(zip(self.base_palette, color_index)))
        self.ordered_palette = [self.palette_matrix[x] for x in color_order]
        
        #handle exceptions
        if self.name == 'bigender':
            self.ordered_palette.insert(4, (216, 191, 216))
        
        #saves image as attribute
        self.flat_image = flat_image
        
        #shows/saves
        if show:
            flat_image.show()
        if save:
            filepath = 'flag_images/flat/' + self.name + '_flat.png'
            flat_image.save(filepath, format='png')

    def order_colors(self, stats):
        '''
        Creates image with all colors changed to base palette

        Parameters
        ----------
            stats : dict
                Dictionary of colors (keys) to appropriate stat (values)

        Returns
        -------
        Pillow Image
        '''
        
        sorted_tuples = sorted(stats.items(), key=operator.itemgetter(1))
        sorted_dict = OrderedDict()
        for k, v in sorted_tuples:
            sorted_dict[k] = v
        
        #orders appropriate stats (defined by type)
        stat_sort = list(sorted_dict.keys())
        
        #simple flag only needs a direct list
        if self.type == 'simple':
            return stat_sort
       
       #mirroed flag duplicates the tail
        elif self.type == 'mirrored':
            mirror_add = int(self.num_stripes - self.num_colors)
            mirror_back = stat_sort[-mirror_add:]
            mirror_back.reverse()
            mirrored_palette = mirror_back + stat_sort
            return mirrored_palette

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
        if not hasattr(self, 'flat_image'):
            self.flatten_image()
        
        #derives size of output image
        height = height_lookup[self.num_stripes]
        height = height * self.multiplier
        width = 500 * self.multiplier
        
        #creates image object
        img = Image.new('RGB', size = (width, height))
        draw = ImageDraw.Draw(img)
        y = 0
        
        #iterates through palette creating 
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