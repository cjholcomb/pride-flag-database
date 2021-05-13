from PIL import Image, ImageDraw
import argparse
import sys
import colorsys
from numpy.lib.type_check import _imag_dispatcher
import webcolors
import re
import os
import pandas as pd
from collections import defaultdict
from operator import itemgetter
from math import sqrt

re_color = re.compile('#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})')

palettes = {'css3': {'hex_to_name': webcolors.CSS3_HEX_TO_NAMES, 'name_to_hex': webcolors.CSS3_NAMES_TO_HEX},
    'xkcd': {'hex_to_name': {'#acc2d9': 'cloudy blue', '#56ae57': 'dark pastel green', '#b2996e': 'dust', '#a8ff04': 'electric lime', '#69d84f': 'fresh green', '#894585': 'light eggplant', '#70b23f': 'nasty green', '#d4ffff': 'really light blue', '#65ab7c': 'tea', '#952e8f': 'warm purple', '#fcfc81': 'yellowish tan', '#a5a391': 'cement', '#388004': 'dark grass green', '#4c9085': 'dusty teal', '#5e9b8a': 'grey teal', '#efb435': 'macaroni and cheese', '#d99b82': 'pinkish tan', '#0a5f38': 'spruce', '#0c06f7': 'strong blue', '#61de2a': 'toxic green', '#3778bf': 'windows blue', '#2242c7': 'blue blue', '#533cc6': 'blue with a hint of purple', '#9bb53c': 'booger', '#05ffa6': 'bright sea green', '#1f6357': 'dark green blue', '#017374': 'deep turquoise', '#0cb577': 'green teal', '#ff0789': 'strong pink', '#afa88b': 'bland', '#08787f': 'deep aqua', '#dd85d7': 'lavender pink', '#a6c875': 'light moss green', '#a7ffb5': 'light seafoam green', '#c2b709': 'olive yellow', '#e78ea5': 'pig pink', '#966ebd': 'deep lilac', '#ccad60': 'desert', '#ac86a8': 'dusty lavender', '#947e94': 'purpley grey', '#983fb2': 'purply', '#ff63e9': 'candy pink', '#b2fba5': 'light pastel green', '#63b365': 'boring green', '#8ee53f': 'kiwi green', '#b7e1a1': 'light grey green', '#ff6f52': 'orange pink', '#bdf8a3': 'tea green', '#d3b683': 'very light brown', '#fffcc4': 'egg shell', '#430541': 'eggplant purple', '#ffb2d0': 'powder pink', '#997570': 'reddish grey', '#ad900d': 'baby shit brown', '#c48efd': 'liliac', '#507b9c': 'stormy blue', '#7d7103': 'ugly brown', '#fffd78': 'custard', '#da467d': 'darkish pink', '#410200': 'deep brown', '#c9d179': 'greenish beige', '#fffa86': 'manilla', '#5684ae': 'off blue', '#6b7c85': 'battleship grey', '#6f6c0a': 'browny green', '#7e4071': 'bruise', '#009337': 'kelley green', '#d0e429': 'sickly yellow', '#fff917': 'sunny yellow', '#1d5dec': 'azul', '#054907': 'darkgreen', '#b5ce08': 'green/yellow', '#8fb67b': 'lichen', '#c8ffb0': 'light light green', '#fdde6c': 'pale gold', '#ffdf22': 'sun yellow', '#a9be70': 'tan green', '#6832e3': 'burple', '#fdb147': 'butterscotch', '#c7ac7d': 'toupe', '#fff39a': 'dark cream', '#850e04': 'indian red', '#efc0fe': 'light lavendar', '#40fd14': 'poison green', '#b6c406': 'baby puke green', '#9dff00': 'bright yellow green', '#3c4142': 'charcoal grey', '#f2ab15': 'squash', '#ac4f06': 'cinnamon', '#c4fe82': 'light pea green', '#2cfa1f': 'radioactive green', '#9a6200': 'raw sienna', '#ca9bf7': 'baby purple', '#875f42': 'cocoa', '#3a2efe': 'light royal blue', '#fd8d49': 'orangeish', '#8b3103': 'rust brown', '#cba560': 'sand brown', '#698339': 'swamp', '#0cdc73': 'tealish green', '#b75203': 'burnt siena', '#7f8f4e': 'camo', '#26538d': 'dusk blue', '#63a950': 'fern', '#c87f89': 'old rose', '#b1fc99': 'pale light green', '#ff9a8a': 'peachy pink', '#f6688e': 'rosy pink', '#76fda8': 'light bluish green', '#53fe5c': 'light bright green', '#4efd54': 'light neon green', '#a0febf': 'light seafoam', '#7bf2da': 'tiffany blue', '#bcf5a6': 'washed out green', '#ca6b02': 'browny orange', '#107ab0': 'nice blue', '#2138ab': 'sapphire', '#719f91': 'greyish teal', '#fdb915': 'orangey yellow', '#fefcaf': 'parchment', '#fcf679': 'straw', '#1d0200': 'very dark brown', '#cb6843': 'terracota', '#31668a': 'ugly blue', '#247afd': 'clear blue', '#ffffb6': 'creme', '#90fda9': 'foam green', '#86a17d': 'grey/green', '#fddc5c': 'light gold', '#78d1b6': 'seafoam blue', '#13bbaf': 'topaz', '#fb5ffc': 'violet pink', '#20f986': 'wintergreen', '#ffe36e': 'yellow tan', '#9d0759': 'dark fuchsia', '#3a18b1': 'indigo blue', '#c2ff89': 'light yellowish green', '#d767ad': 'pale magenta', '#720058': 'rich purple', '#ffda03': 'sunflower yellow', '#01c08d': 'green/blue', '#ac7434': 'leather', '#014600': 'racing green', '#9900fa': 'vivid purple', '#02066f': 'dark royal blue', '#8e7618': 'hazel', '#d1768f': 'muted pink', '#96b403': 'booger green', '#fdff63': 'canary', '#95a3a6': 'cool grey', '#7f684e': 'dark taupe', '#751973': 'darkish purple', '#089404': 'true green', '#ff6163': 'coral pink', '#598556': 'dark sage', '#214761': 'dark slate blue', '#3c73a8': 'flat blue', '#ba9e88': 'mushroom', '#021bf9': 'rich blue', '#734a65': 'dirty purple', '#23c48b': 'greenblue', '#8fae22': 'icky green', '#e6f2a2': 'light khaki', '#4b57db': 'warm blue', '#d90166': 'dark hot pink', '#015482': 'deep sea blue', '#9d0216': 'carmine', '#728f02': 'dark yellow green', '#ffe5ad': 'pale peach', '#4e0550': 'plum purple', '#f9bc08': 'golden rod', '#ff073a': 'neon red', '#c77986': 'old pink', '#d6fffe': 'very pale blue', '#fe4b03': 'blood orange', '#fd5956': 'grapefruit', '#fce166': 'sand yellow', '#b2713d': 'clay brown', '#1f3b4d': 'dark blue grey', '#699d4c': 'flat green', '#56fca2': 'light green blue', '#fb5581': 'warm pink', '#3e82fc': 'dodger blue', '#a0bf16': 'gross green', '#d6fffa': 'ice', '#4f738e': 'metallic blue', '#ffb19a': 'pale salmon', '#5c8b15': 'sap green', '#54ac68': 'algae', '#89a0b0': 'bluey grey', '#7ea07a': 'greeny grey', '#1bfc06': 'highlighter green', '#cafffb': 'light light blue', '#b6ffbb': 'light mint', '#a75e09': 'raw umber', '#152eff': 'vivid blue', '#8d5eb7': 'deep lavender', '#5f9e8f': 'dull teal', '#63f7b4': 'light greenish blue', '#606602': 'mud green', '#fc86aa': 'pinky', '#8c0034': 'red wine', '#758000': 'shit green', '#ab7e4c': 'tan brown', '#030764': 'darkblue', '#fe86a4': 'rosa', '#d5174e': 'lipstick', '#fed0fc': 'pale mauve', '#680018': 'claret', '#fedf08': 'dandelion', '#fe420f': 'orangered', '#6f7c00': 'poop green', '#ca0147': 'ruby', '#1b2431': 'dark', '#00fbb0': 'greenish turquoise', '#db5856': 'pastel red', '#ddd618': 'piss yellow', '#41fdfe': 'bright cyan', '#cf524e': 'dark coral', '#21c36f': 'algae green', '#a90308': 'darkish red', '#6e1005': 'reddy brown', '#fe828c': 'blush pink', '#4b6113': 'camouflage green', '#4da409': 'lawn green', '#beae8a': 'putty', '#0339f8': 'vibrant blue', '#a88f59': 'dark sand', '#5d21d0': 'purple/blue', '#feb209': 'saffron', '#4e518b': 'twilight', '#964e02': 'warm brown', '#85a3b2': 'bluegrey', '#ff69af': 'bubble gum pink', '#c3fbf4': 'duck egg blue', '#2afeb7': 'greenish cyan', '#005f6a': 'petrol', '#0c1793': 'royal', '#ffff81': 'butter', '#f0833a': 'dusty orange', '#f1f33f': 'off yellow', '#b1d27b': 'pale olive green', '#fc824a': 'orangish', '#71aa34': 'leaf', '#b7c9e2': 'light blue grey', '#4b0101': 'dried blood', '#a552e6': 'lightish purple', '#af2f0d': 'rusty red', '#8b88f8': 'lavender blue', '#9af764': 'light grass green', '#a6fbb2': 'light mint green', '#ffc512': 'sunflower', '#750851': 'velvet', '#c14a09': 'brick orange', '#fe2f4a': 'lightish red', '#0203e2': 'pure blue', '#0a437a': 'twilight blue', '#a50055': 'violet red', '#ae8b0c': 'yellowy brown', '#fd798f': 'carnation', '#bfac05': 'muddy yellow', '#3eaf76': 'dark seafoam green', '#c74767': 'deep rose', '#b9484e': 'dusty red', '#647d8e': 'grey/blue', '#bffe28': 'lemon lime', '#d725de': 'purple/pink', '#b29705': 'brown yellow', '#673a3f': 'purple brown', '#a87dc2': 'wisteria', '#fafe4b': 'banana yellow', '#c0022f': 'lipstick red', '#0e87cc': 'water blue', '#8d8468': 'brown grey', '#ad03de': 'vibrant purple', '#8cff9e': 'baby green', '#94ac02': 'barf green', '#c4fff7': 'eggshell blue', '#fdee73': 'sandy yellow', '#33b864': 'cool green', '#fff9d0': 'pale', '#758da3': 'blue/grey', '#f504c9': 'hot magenta', '#77a1b5': 'greyblue', '#8756e4': 'purpley', '#889717': 'baby shit green', '#c27e79': 'brownish pink', '#017371': 'dark aquamarine', '#9f8303': 'diarrhea', '#f7d560': 'light mustard', '#bdf6fe': 'pale sky blue', '#75b84f': 'turtle green', '#9cbb04': 'bright olive', '#29465b': 'dark grey blue', '#696006': 'greeny brown', '#adf802': 'lemon green', '#c1c6fc': 'light periwinkle', '#35ad6b': 'seaweed green', '#fffd37': 'sunshine yellow', '#a442a0': 'ugly purple', '#f36196': 'medium pink', '#947706': 'puke brown', '#fff4f2': 'very light pink', '#1e9167': 'viridian', '#b5c306': 'bile', '#feff7f': 'faded yellow', '#cffdbc': 'very pale green', '#0add08': 'vibrant green', '#87fd05': 'bright lime', '#1ef876': 'spearmint', '#7bfdc7': 'light aquamarine', '#bcecac': 'light sage', '#bbf90f': 'yellowgreen', '#ab9004': 'baby poo', '#1fb57a': 'dark seafoam', '#00555a': 'deep teal', '#a484ac': 'heather', '#c45508': 'rust orange', '#3f829d': 'dirty blue', '#548d44': 'fern green', '#c95efb': 'bright lilac', '#3ae57f': 'weird green', '#016795': 'peacock blue', '#87a922': 'avocado green', '#f0944d': 'faded orange', '#5d1451': 'grape purple', '#25ff29': 'hot green', '#d0fe1d': 'lime yellow', '#ffa62b': 'mango', '#01b44c': 'shamrock', '#ff6cb5': 'bubblegum', '#6b4247': 'purplish brown', '#c7c10c': 'vomit yellow', '#b7fffa': 'pale cyan', '#aeff6e': 'key lime', '#ec2d01': 'tomato red', '#76ff7b': 'lightgreen', '#730039': 'merlot', '#040348': 'night blue', '#df4ec8': 'purpleish pink', '#6ecb3c': 'apple', '#8f9805': 'baby poop green', '#5edc1f': 'green apple', '#d94ff5': 'heliotrope', '#c8fd3d': 'yellow/green', '#070d0d': 'almost black', '#4984b8': 'cool blue', '#51b73b': 'leafy green', '#ac7e04': 'mustard brown', '#4e5481': 'dusk', '#876e4b': 'dull brown', '#58bc08': 'frog green', '#2fef10': 'vivid green', '#2dfe54': 'bright light green', '#0aff02': 'fluro green', '#9cef43': 'kiwi', '#18d17b': 'seaweed', '#35530a': 'navy green', '#1805db': 'ultramarine blue', '#6258c4': 'iris', '#ff964f': 'pastel orange', '#ffab0f': 'yellowish orange', '#8f8ce7': 'perrywinkle', '#24bca8': 'tealish', '#3f012c': 'dark plum', '#cbf85f': 'pear', '#ff724c': 'pinkish orange', '#280137': 'midnight purple', '#b36ff6': 'light urple', '#48c072': 'dark mint', '#bccb7a': 'greenish tan', '#a8415b': 'light burgundy', '#06b1c4': 'turquoise blue', '#cd7584': 'ugly pink', '#f1da7a': 'sandy', '#ff0490': 'electric pink', '#805b87': 'muted purple', '#50a747': 'mid green', '#a8a495': 'greyish', '#cfff04': 'neon yellow', '#ffff7e': 'banana', '#ff7fa7': 'carnation pink', '#ef4026': 'tomato', '#3c9992': 'sea', '#886806': 'muddy brown', '#04f489': 'turquoise green', '#fef69e': 'buff',
    '#cfaf7b': 'fawn', '#3b719f': 'muted blue', '#fdc1c5': 'pale rose', '#20c073': 'dark mint green', '#9b5fc0': 'amethyst', '#0f9b8e': 'blue/green', '#742802': 'chestnut', '#9db92c': 'sick green', '#a4bf20': 'pea', '#cd5909': 'rusty orange', '#ada587': 'stone', '#be013c': 'rose red', '#b8ffeb': 'pale aqua', '#dc4d01': 'deep orange', '#a2653e': 'earth', '#638b27': 'mossy green', '#419c03': 'grassy green', '#b1ff65': 'pale lime green', '#9dbcd4': 'light grey blue', '#fdfdfe': 'pale grey', '#77ab56': 'asparagus', '#464196': 'blueberry', '#990147': 'purple red', '#befd73': 'pale lime', '#32bf84': 'greenish teal', '#af6f09': 'caramel', '#a0025c': 'deep magenta', '#ffd8b1': 'light peach', '#7f4e1e': 'milk chocolate', '#bf9b0c': 'ocher', '#6ba353': 'off green', '#f075e6': 'purply pink', '#7bc8f6': 'lightblue', '#475f94': 'dusky blue', '#f5bf03': 'golden', '#fffeb6': 'light beige', '#fffd74': 'butter yellow', '#895b7b': 'dusky purple', '#436bad': 'french blue', '#d0c101': 'ugly yellow', '#c6f808': 'greeny yellow', '#f43605': 'orangish red', '#02c14d': 'shamrock green', '#b25f03': 'orangish brown', '#2a7e19': 'tree green', '#490648': 'deep violet', '#536267': 'gunmetal', '#5a06ef': 'blue/purple', '#cf0234': 'cherry', '#c4a661': 'sandy brown', '#978a84': 'warm grey', '#1f0954': 'dark indigo', '#03012d': 'midnight', '#2bb179': 'bluey green', '#c3909b': 'grey pink', '#a66fb5': 'soft purple', '#770001': 'blood', '#922b05': 'brown red', '#7d7f7c': 'medium grey', '#990f4b': 'berry', '#8f7303': 'poo', '#c83cb9': 'purpley pink', '#fea993': 'light salmon', '#acbb0d': 'snot', '#c071fe': 'easter purple', '#ccfd7f': 'light yellow green', '#00022e': 'dark navy blue', '#828344': 'drab', '#ffc5cb': 'light rose', '#ab1239': 'rouge', '#b0054b': 'purplish red', '#99cc04': 'slime green', '#937c00': 'baby poop', '#019529': 'irish green', '#ef1de7': 'pink/purple', '#000435': 'dark navy', '#42b395': 'greeny blue', '#9d5783': 'light plum', '#c8aca9': 'pinkish grey', '#c87606': 'dirty orange', '#aa2704': 'rust red', '#e4cbff': 'pale lilac', '#fa4224': 'orangey red', '#0804f9': 'primary blue', '#5cb200': 'kermit green', '#76424e': 'brownish purple', '#6c7a0e': 'murky green', '#fbdd7e': 'wheat', '#2a0134': 'very dark purple', '#044a05': 'bottle green', '#fd4659': 'watermelon', '#0d75f8': 'deep sky blue', '#fe0002': 'fire engine red', '#cb9d06': 'yellow ochre', '#fb7d07': 'pumpkin orange', '#b9cc81': 'pale olive', '#edc8ff': 'light lilac', '#61e160': 'lightish green', '#8ab8fe': 'carolina blue', '#920a4e': 'mulberry', '#fe02a2': 'shocking pink', '#9a3001': 'auburn', '#65fe08': 'bright lime green', '#befdb7': 'celadon', '#b17261': 'pinkish brown', '#885f01': 'poo brown', '#02ccfe': 'bright sky blue', '#c1fd95': 'celery', '#836539': 'dirt brown', '#fb2943': 'strawberry', '#84b701': 'dark lime', '#b66325': 'copper', '#7f5112': 'medium brown', '#5fa052': 'muted green', '#6dedfd': 'robins egg', '#0bf9ea': 'bright aqua', '#c760ff': 'bright lavender', '#ffffcb': 'ivory', '#f6cefc': 'very light purple', '#155084': 'light navy', '#f5054f': 'pink red', '#645403': 'olive brown', '#7a5901': 'poop brown', '#a8b504': 'mustard green', '#3d9973': 'ocean green', '#000133': 'very dark blue', '#76a973': 'dusty green', '#2e5a88': 'light navy blue', '#0bf77d': 'minty green', '#bd6c48': 'adobe', '#ac1db8': 'barney', '#2baf6a': 'jade green', '#26f7fd': 'bright light blue', '#aefd6c': 'light lime', '#9b8f55': 'dark khaki', '#ffad01': 'orange yellow', '#c69c04': 'ocre', '#f4d054': 'maize', '#de9dac': 'faded pink', '#05480d': 'british racing green', '#c9ae74': 'sandstone', '#60460f': 'mud brown', '#98f6b0': 'light sea green', '#8af1fe': 'robin egg blue', '#2ee8bb': 'aqua marine', '#11875d': 'dark sea green', '#fdb0c0': 'soft pink', '#b16002': 'orangey brown', '#f7022a': 'cherry red', '#d5ab09': 'burnt yellow', '#86775f': 'brownish grey', '#c69f59': 'camel', '#7a687f': 'purplish grey', '#042e60': 'marine', '#c88d94': 'greyish pink', '#a5fbd5': 'pale turquoise', '#fffe71': 'pastel yellow', '#6241c7': 'bluey purple', '#fffe40': 'canary yellow', '#d3494e': 'faded red', '#985e2b': 'sepia', '#a6814c': 'coffee', '#ff08e8': 'bright magenta', '#9d7651': 'mocha', '#feffca': 'ecru', '#98568d': 'purpleish', '#9e003a': 'cranberry', '#287c37': 'darkish green', '#b96902': 'brown orange', '#ba6873': 'dusky rose', '#ff7855': 'melon', '#94b21c': 'sickly green', '#c5c9c7': 'silver', '#661aee': 'purply blue', '#6140ef': 'purpleish blue', '#9be5aa': 'hospital green', '#7b5804': 'shit brown', '#276ab3': 'mid blue', '#feb308': 'amber', '#8cfd7e': 'easter green', '#6488ea': 'soft blue', '#056eee': 'cerulean blue', '#b27a01': 'golden brown', '#0ffef9': 'bright turquoise', '#fa2a55': 'red pink', '#820747': 'red purple', '#7a6a4f': 'greyish brown', '#f4320c': 'vermillion', '#a13905': 'russet', '#6f828a': 'steel grey', '#a55af4': 'lighter purple', '#ad0afd': 'bright violet', '#004577': 'prussian blue', '#658d6d': 'slate green', '#ca7b80': 'dirty pink', '#005249': 'dark blue green', '#2b5d34': 'pine', '#bff128': 'yellowy green', '#b59410': 'dark gold', '#2976bb': 'bluish', '#014182': 'darkish blue', '#bb3f3f': 'dull red', '#fc2647': 'pinky red', '#a87900': 'bronze', '#82cbb2': 'pale teal', '#667c3e': 'military green', '#fe46a5': 'barbie pink', '#fe83cc': 'bubblegum pink', '#94a617': 'pea soup green', '#a88905': 'dark mustard', '#7f5f00': 'shit', '#9e43a2': 'medium purple', '#062e03': 'very dark green', '#8a6e45': 'dirt',  '#cc7a8b': 'dusky pink', '#9e0168': 'red violet', '#fdff38': 'lemon yellow', '#c0fa8b': 'pistachio', '#eedc5b': 'dull yellow', '#7ebd01': 'dark lime green', '#3b5b92': 'denim blue', '#01889f': 'teal blue', '#3d7afd': 'lightish blue', '#5f34e7': 'purpley blue', '#6d5acf': 'light indigo', '#748500': 'swamp green', '#706c11': 'brown green', '#3c0008': 'dark maroon', '#cb00f5': 'hot purple', '#002d04': 'dark forest green', '#658cbb': 'faded blue', '#749551': 'drab green', '#b9ff66': 'light lime green', '#9dc100': 'snot green', '#faee66': 'yellowish', '#7efbb3': 'light blue green', '#7b002c': 'bordeaux', '#c292a1': 'light mauve', '#017b92': 'ocean', '#fcc006': 'marigold', '#657432': 'muddy green', '#d8863b': 'dull orange', '#738595': 'steel', '#aa23ff': 'electric purple', '#08ff08': 'fluorescent green', '#9b7a01': 'yellowish brown', '#f29e8e': 'blush', '#6fc276': 'soft green', '#ff5b00': 'bright orange', '#fdff52': 'lemon', '#866f85': 'purple grey', '#8ffe09': 'acid green', '#eecffe': 'pale lavender', '#510ac9': 'violet blue', '#4f9153': 'light forest green', '#9f2305': 'burnt red', '#728639': 'khaki green', '#de0c62': 'cerise', '#916e99': 'faded purple', '#ffb16d': 'apricot', '#3c4d03': 'dark olive green', '#7f7053': 'grey brown', '#77926f': 'green grey', '#010fcc': 'true blue', '#ceaefa': 'pale violet', '#8f99fb': 'periwinkle blue', '#c6fcff': 'light sky blue', '#5539cc': 'blurple', '#544e03': 'green brown', '#017a79': 'bluegreen', '#01f9c6': 'bright teal', '#c9b003': 'brownish yellow', '#929901': 'pea soup', '#0b5509': 'forest', '#a00498': 'barney purple', '#2000b1': 'ultramarine', '#94568c': 'purplish', '#c2be0e': 'puke yellow', '#748b97': 'bluish grey', '#665fd1': 'dark periwinkle', '#9c6da5': 'dark lilac', '#c44240': 'reddish', '#a24857': 'light maroon', '#825f87': 'dusty purple', '#c9643b': 'terra cotta', '#90b134': 'avocado', '#01386a': 'marine blue', '#25a36f': 'teal green', '#59656d': 'slate grey', '#75fd63': 'lighter green', '#21fc0d': 'electric green', '#5a86ad': 'dusty blue', '#fec615': 'golden yellow', '#fffd01': 'bright yellow', '#dfc5fe': 'light lavender', '#b26400': 'umber', '#7f5e00': 'poop', '#de7e5d': 'dark peach', '#048243': 'jungle green', '#ffffd4': 'eggshell', '#3b638c': 'denim', '#b79400': 'yellow brown', '#84597e': 'dull purple', '#411900': 'chocolate brown', '#7b0323': 'wine red', '#04d9ff': 'neon blue', '#667e2c': 'dirty green', '#fbeeac': 'light tan', '#d7fffe': 'ice blue', '#4e7496': 'cadet blue', '#874c62': 'dark mauve', '#d5ffff': 'very light blue', '#826d8c': 'grey purple', '#ffbacd': 'pastel pink', '#d1ffbd': 'very light green', '#448ee4': 'dark sky blue', '#05472a': 'evergreen', '#d5869d': 'dull pink', '#3d0734': 'aubergine', '#4a0100': 'mahogany', '#f8481c': 'reddish orange', '#02590f': 'deep green', '#89a203': 'vomit green', '#e03fd8': 'purple pink', '#d58a94': 'dusty pink', '#7bb274': 'faded green', '#526525': 'camo green', '#c94cbe': 'pinky purple', '#db4bda': 'pink purple', '#9e3623': 'brownish red', '#b5485d': 'dark rose', '#735c12': 'mud', '#9c6d57': 'brownish', '#028f1e': 'emerald green', '#b1916e': 'pale brown', '#49759c': 'dull blue', '#a0450e': 'burnt umber', '#39ad48': 'medium green', '#b66a50': 'clay', '#8cffdb': 'light aqua', '#a4be5c': 'light olive green', '#cb7723': 'brownish orange', '#05696b': 'dark aqua', '#ce5dae': 'purplish pink', '#c85a53': 'dark salmon', '#96ae8d': 'greenish grey', '#1fa774': 'jade', '#7a9703': 'ugly green', '#ac9362': 'dark beige', '#01a049': 'emerald', '#d9544d': 'pale red', '#fa5ff7': 'light magenta', '#82cafc': 'sky', '#acfffc': 'light cyan', '#fcb001': 'yellow orange', '#910951': 'reddish purple', '#fe2c54': 'reddish pink', '#c875c4': 'orchid', '#cdc50a': 'dirty yellow', '#fd411e': 'orange red', '#9a0200': 'deep red', '#be6400': 'orange brown', '#030aa7': 'cobalt blue', '#fe019a': 'neon pink', '#f7879a': 'rose pink', '#887191': 'greyish purple', '#b00149': 'raspberry', '#12e193': 'aqua green', '#fe7b7c': 'salmon pink', '#ff9408': 'tangerine', '#6a6e09': 'brownish green', '#8b2e16': 'red brown', '#696112': 'greenish brown', '#e17701': 'pumpkin', '#0a481e': 'pine green', '#343837': 'charcoal', '#ffb7ce': 'baby pink', '#6a79f7': 'cornflower', '#5d06e9': 'blue violet', '#3d1c02': 'chocolate', '#82a67d': 'greyish green', '#be0119': 'scarlet', '#c9ff27': 'green yellow', '#373e02': 'dark olive', '#a9561e': 'sienna', '#caa0ff': 'pastel purple', '#ca6641': 'terracotta', '#02d8e9': 'aqua blue', '#88b378': 'sage green', '#980002': 'blood red', '#cb0162': 'deep pink', '#5cac2d': 'grass', '#769958': 'moss',
    '#a2bffe': 'pastel blue', '#10a674': 'bluish green', '#06b48b': 'green blue', '#af884a': 'dark tan', '#0b8b87': 'greenish blue', '#ffa756': 'pale orange', '#a2a415': 'vomit', '#154406': 'forrest green', '#856798': 'dark lavender', '#34013f': 'dark violet', '#632de9': 'purple blue', '#0a888a': 'dark cyan', '#6f7632': 'olive drab', '#d46a7e': 'pinkish', '#1e488f': 'cobalt', '#bc13fe': 'neon purple', '#7ef4cc': 'light turquoise', '#76cd26': 'apple green', '#74a662': 'dull green', '#80013f': 'wine', '#b1d1fc': 'powder blue', '#ffffe4': 'off white', '#0652ff': 'electric blue', '#045c5a': 'dark turquoise', '#5729ce': 'blue purple', '#069af3': 'azure', '#ff000d': 'bright red', '#f10c45': 'pinkish red', '#5170d7': 'cornflower blue', '#acbf69': 'light olive', '#6c3461': 'grape', '#5e819d': 'greyish blue', '#601ef9': 'purplish blue', '#b0dd16': 'yellowish green', '#cdfd02': 'greenish yellow', '#2c6fbb': 'medium blue', '#c0737a': 'dusty rose', '#d6b4fc': 'light violet', '#020035': 'midnight blue', '#703be7': 'bluish purple', '#fd3c06': 'red orange', '#960056': 'dark magenta', '#40a368': 'greenish', '#03719c': 'ocean blue', '#fc5a50': 'coral', '#ffffc2': 'cream', '#7f2b0a': 'reddish brown', '#b04e0f': 'burnt sienna', '#a03623': 'brick', '#87ae73': 'sage', '#789b73': 'grey green', '#ffffff': 'white', '#98eff9': 'robins egg blue', '#658b38': 'moss green', '#5a7d9a': 'steel blue', '#380835': 'eggplant', '#fffe7a': 'light yellow', '#5ca904': 'leaf green', '#d8dcd6': 'light grey', '#a5a502': 'puke', '#d648d7': 'pinkish purple', '#047495': 'sea blue', '#b790d4': 'pale purple', '#5b7c99': 'slate blue', '#607c8e': 'blue grey', '#0b4008': 'hunter green', '#ed0dd9': 'fuchsia', '#8c000f': 'crimson', '#ffff84': 'pale yellow', '#bf9005': 'ochre', '#d2bd0a': 'mustard yellow', '#ff474c': 'light red', '#0485d1': 'cerulean', '#ffcfdc': 'pale pink', '#040273': 'deep blue', '#a83c09': 'rust', '#90e4c1': 'light teal', '#516572': 'slate', '#fac205': 'goldenrod', '#d5b60a': 'dark yellow', '#363737': 'dark grey', '#4b5d16': 'army green', '#6b8ba4': 'grey blue', '#80f9ad': 'seafoam', '#a57e52': 'puce', '#a9f971': 'spring green', '#c65102': 'dark orange', '#e2ca76': 'sand', '#b0ff9d': 'pastel green', '#9ffeb0': 'mint', '#fdaa48': 'light orange', '#fe01b1': 'bright pink', '#c1f80a': 'chartreuse', '#36013f': 'deep purple', '#341c02': 'dark brown', '#b9a281': 'taupe', '#8eab12': 'pea green', '#9aae07': 'puke green', '#02ab2e': 'kelly green', '#7af9ab': 'seafoam green', '#137e6d': 'blue green', '#aaa662': 'khaki', '#610023': 'burgundy', '#014d4e': 'dark teal', '#8f1402': 'brick red', '#4b006e': 'royal purple', '#580f41': 'plum', '#8fff9f': 'mint green', '#dbb40c': 'gold', '#a2cffe': 'baby blue', '#c0fb2d': 'yellow green', '#be03fd': 'bright purple', '#840000': 'dark red', '#d0fefe': 'pale blue', '#3f9b0b': 'grass green', '#01153e': 'navy', '#04d8b2': 'aquamarine', '#c04e01': 'burnt orange', '#0cff0c': 'neon green', '#0165fc': 'bright blue', '#cf6275': 'rose', '#ffd1df': 'light pink', '#ceb301': 'mustard', '#380282': 'indigo', '#aaff32': 'lime', '#53fca1': 'sea green', '#8e82fe': 'periwinkle', '#cb416b': 'dark pink', '#677a04': 'olive green', '#ffb07c': 'peach', '#c7fdb5': 'pale green', '#ad8150': 'light brown', '#ff028d': 'hot pink', '#000000': 'black', '#cea2fd': 'lilac', '#001146': 'navy blue', '#0504aa': 'royal blue', '#e6daa6': 'beige', '#ff796c': 'salmon', '#6e750e': 'olive', '#650021': 'maroon', '#01ff07': 'bright green', '#35063e': 'dark purple', '#ae7181': 'mauve', '#06470c': 'forest green', '#13eac9': 'aqua', '#00ffff': 'cyan', '#d1b26f': 'tan', '#00035b': 'dark blue', '#c79fef': 'lavender', '#06c2ac': 'turquoise', '#033500': 'dark green', '#9a0eea': 'violet', '#bf77f6': 'light purple', '#89fe05': 'lime green', '#929591': 'grey', '#75bbfd': 'sky blue', '#ffff14': 'yellow', '#c20078': 'magenta', '#96f97b': 'light green', '#f97306': 'orange', '#029386': 'teal', '#95d0fc': 'light blue', '#e50000': 'red', '#653700': 'brown', '#ff81c0': 'pink', '#0343df': 'blue', '#15b01a': 'green', '#7e1e9c': 'purple'},
    'name_to_hex': {'cloudy blue': '#acc2d9', 'dark pastel green': '#56ae57', 'dust': '#b2996e', 'electric lime': '#a8ff04', 'fresh green': '#69d84f', 'light eggplant': '#894585', 'nasty green': '#70b23f', 'really light blue': '#d4ffff', 'tea': '#65ab7c', 'warm purple': '#952e8f', 'yellowish tan': '#fcfc81', 'cement': '#a5a391', 'dark grass green': '#388004', 'dusty teal': '#4c9085', 'grey teal': '#5e9b8a', 'macaroni and cheese': '#efb435', 'pinkish tan': '#d99b82', 'spruce': '#0a5f38', 'strong blue': '#0c06f7', 'toxic green': '#61de2a', 'windows blue': '#3778bf', 'blue blue': '#2242c7', 'blue with a hint of purple': '#533cc6', 'booger': '#9bb53c', 'bright sea green': '#05ffa6', 'dark green blue': '#1f6357', 'deep turquoise': '#017374', 'green teal': '#0cb577', 'strong pink': '#ff0789', 'bland': '#afa88b', 'deep aqua': '#08787f', 'lavender pink': '#dd85d7', 'light moss green': '#a6c875', 'light seafoam green': '#a7ffb5', 'olive yellow': '#c2b709', 'pig pink': '#e78ea5', 'deep lilac': '#966ebd', 'desert': '#ccad60', 'dusty lavender': '#ac86a8', 'purpley grey': '#947e94', 'purply': '#983fb2', 'candy pink': '#ff63e9', 'light pastel green': '#b2fba5', 'boring green': '#63b365', 'kiwi green': '#8ee53f', 'light grey green': '#b7e1a1', 'orange pink': '#ff6f52', 'tea green': '#bdf8a3', 'very light brown': '#d3b683', 'egg shell': '#fffcc4', 'eggplant purple': '#430541', 'powder pink': '#ffb2d0', 'reddish grey': '#997570', 'baby shit brown': '#ad900d', 'liliac': '#c48efd', 'stormy blue': '#507b9c', 'ugly brown': '#7d7103', 'custard': '#fffd78', 'darkish pink': '#da467d', 'deep brown': '#410200', 'greenish beige': '#c9d179', 'manilla': '#fffa86', 'off blue': '#5684ae', 'battleship grey': '#6b7c85', 'browny green': '#6f6c0a', 'bruise': '#7e4071', 'kelley green': '#009337', 'sickly yellow': '#d0e429', 'sunny yellow': '#fff917', 'azul': '#1d5dec', 'darkgreen': '#054907', 'green/yellow': '#b5ce08', 'lichen': '#8fb67b', 'light light green': '#c8ffb0', 'pale gold': '#fdde6c', 'sun yellow': '#ffdf22', 'tan green': '#a9be70', 'burple': '#6832e3', 'butterscotch': '#fdb147', 'toupe': '#c7ac7d', 'dark cream': '#fff39a', 'indian red': '#850e04', 'light lavendar': '#efc0fe', 'poison green': '#40fd14', 'baby puke green': '#b6c406', 'bright yellow green': '#9dff00', 'charcoal grey': '#3c4142', 'squash': '#f2ab15', 'cinnamon': '#ac4f06', 'light pea green': '#c4fe82', 'radioactive green': '#2cfa1f', 'raw sienna': '#9a6200', 'baby purple': '#ca9bf7', 'cocoa': '#875f42', 'light royal blue': '#3a2efe', 'orangeish': '#fd8d49', 'rust brown': '#8b3103', 'sand brown': '#cba560', 'swamp': '#698339', 'tealish green': '#0cdc73', 'burnt siena': '#b75203', 'camo': '#7f8f4e', 'dusk blue': '#26538d', 'fern': '#63a950', 'old rose': '#c87f89', 'pale light green': '#b1fc99', 'peachy pink': '#ff9a8a', 'rosy pink': '#f6688e', 'light bluish green': '#76fda8', 'light bright green': '#53fe5c', 'light neon green': '#4efd54', 'light seafoam': '#a0febf', 'tiffany blue': '#7bf2da', 'washed out green': '#bcf5a6', 'browny orange': '#ca6b02', 'nice blue': '#107ab0', 'sapphire': '#2138ab', 'greyish teal': '#719f91', 'orangey yellow': '#fdb915', 'parchment': '#fefcaf', 'straw': '#fcf679', 'very dark brown': '#1d0200', 'terracota': '#cb6843', 'ugly blue': '#31668a', 'clear blue': '#247afd', 'creme': '#ffffb6', 'foam green': '#90fda9', 'grey/green': '#86a17d', 'light gold': '#fddc5c', 'seafoam blue': '#78d1b6', 'topaz': '#13bbaf', 'violet pink': '#fb5ffc', 'wintergreen': '#20f986', 'yellow tan': '#ffe36e', 'dark fuchsia': '#9d0759', 'indigo blue': '#3a18b1', 'light yellowish green': '#c2ff89', 'pale magenta': '#d767ad', 'rich purple': '#720058', 'sunflower yellow': '#ffda03', 'green/blue': '#01c08d', 'leather': '#ac7434', 'racing green': '#014600', 'vivid purple': '#9900fa', 'dark royal blue': '#02066f', 'hazel': '#8e7618', 'muted pink': '#d1768f', 'booger green': '#96b403', 'canary': '#fdff63', 'cool grey': '#95a3a6', 'dark taupe': '#7f684e', 'darkish purple': '#751973', 'true green': '#089404', 'coral pink': '#ff6163', 'dark sage': '#598556', 'dark slate blue': '#214761', 'flat blue': '#3c73a8', 'mushroom': '#ba9e88', 'rich blue': '#021bf9', 'dirty purple': '#734a65', 'greenblue': '#23c48b', 'icky green': '#8fae22', 'light khaki': '#e6f2a2', 'warm blue': '#4b57db', 'dark hot pink': '#d90166', 'deep sea blue': '#015482', 'carmine': '#9d0216', 'dark yellow green': '#728f02', 'pale peach': '#ffe5ad', 'plum purple': '#4e0550', 'golden rod': '#f9bc08', 'neon red': '#ff073a', 'old pink': '#c77986', 'very pale blue': '#d6fffe', 'blood orange': '#fe4b03', 'grapefruit': '#fd5956', 'sand yellow': '#fce166', 'clay brown': '#b2713d', 'dark blue grey': '#1f3b4d', 'flat green': '#699d4c', 'light green blue': '#56fca2', 'warm pink': '#fb5581', 'dodger blue': '#3e82fc', 'gross green': '#a0bf16', 'ice': '#d6fffa', 'metallic blue': '#4f738e', 'pale salmon': '#ffb19a', 'sap green': '#5c8b15', 'algae': '#54ac68', 'bluey grey': '#89a0b0', 'greeny grey': '#7ea07a', 'highlighter green': '#1bfc06', 'light light blue': '#cafffb', 'light mint': '#b6ffbb', 'raw umber': '#a75e09', 'vivid blue': '#152eff', 'deep lavender': '#8d5eb7', 'dull teal': '#5f9e8f', 'light greenish blue': '#63f7b4', 'mud green': '#606602', 'pinky': '#fc86aa', 'red wine': '#8c0034', 'shit green': '#758000', 'tan brown': '#ab7e4c', 'darkblue': '#030764', 'rosa': '#fe86a4', 'lipstick': '#d5174e', 'pale mauve': '#fed0fc', 'claret': '#680018', 'dandelion': '#fedf08', 'orangered': '#fe420f', 'poop green': '#6f7c00', 'ruby': '#ca0147', 'dark': '#1b2431', 'greenish turquoise': '#00fbb0', 'pastel red': '#db5856', 'piss yellow': '#ddd618', 'bright cyan': '#41fdfe', 'dark coral': '#cf524e', 'algae green': '#21c36f', 'darkish red': '#a90308', 'reddy brown': '#6e1005', 'blush pink': '#fe828c', 'camouflage green': '#4b6113', 'lawn green': '#4da409', 'putty': '#beae8a', 'vibrant blue': '#0339f8', 'dark sand': '#a88f59', 'purple/blue': '#5d21d0', 'saffron': '#feb209', 'twilight': '#4e518b', 'warm brown': '#964e02', 'bluegrey': '#85a3b2', 'bubble gum pink': '#ff69af', 'duck egg blue': '#c3fbf4', 'greenish cyan': '#2afeb7', 'petrol': '#005f6a', 'royal': '#0c1793', 'butter': '#ffff81', 'dusty orange': '#f0833a', 'off yellow': '#f1f33f', 'pale olive green': '#b1d27b', 'orangish': '#fc824a', 'leaf': '#71aa34', 'light blue grey': '#b7c9e2', 'dried blood': '#4b0101', 'lightish purple': '#a552e6', 'rusty red': '#af2f0d', 'lavender blue': '#8b88f8', 'light grass green': '#9af764', 'light mint green': '#a6fbb2', 'sunflower': '#ffc512', 'velvet': '#750851', 'brick orange': '#c14a09', 'lightish red': '#fe2f4a', 'pure blue': '#0203e2', 'twilight blue': '#0a437a', 'violet red': '#a50055', 'yellowy brown': '#ae8b0c', 'carnation': '#fd798f', 'muddy yellow': '#bfac05', 'dark seafoam green': '#3eaf76', 'deep rose': '#c74767', 'dusty red': '#b9484e', 'grey/blue': '#647d8e', 'lemon lime': '#bffe28', 'purple/pink': '#d725de', 'brown yellow': '#b29705', 'purple brown': '#673a3f', 'wisteria': '#a87dc2', 'banana yellow': '#fafe4b', 'lipstick red': '#c0022f', 'water blue': '#0e87cc', 'brown grey': '#8d8468', 'vibrant purple': '#ad03de', 'baby green': '#8cff9e', 'barf green': '#94ac02', 'eggshell blue': '#c4fff7', 'sandy yellow': '#fdee73', 'cool green': '#33b864', 'pale': '#fff9d0', 'blue/grey': '#758da3', 'hot magenta': '#f504c9', 'greyblue': '#77a1b5', 'purpley': '#8756e4', 'baby shit green': '#889717', 'brownish pink': '#c27e79', 'dark aquamarine': '#017371', 'diarrhea': '#9f8303', 'light mustard': '#f7d560', 'pale sky blue': '#bdf6fe', 'turtle green': '#75b84f', 'bright olive': '#9cbb04', 'dark grey blue': '#29465b', 'greeny brown': '#696006', 'lemon green': '#adf802', 'light periwinkle': '#c1c6fc', 'seaweed green': '#35ad6b', 'sunshine yellow': '#fffd37', 'ugly purple': '#a442a0', 'medium pink': '#f36196', 'puke brown': '#947706', 'very light pink': '#fff4f2', 'viridian': '#1e9167', 'bile': '#b5c306', 'faded yellow': '#feff7f', 'very pale green': '#cffdbc', 'vibrant green': '#0add08', 'bright lime': '#87fd05', 'spearmint': '#1ef876', 'light aquamarine': '#7bfdc7', 'light sage': '#bcecac', 'yellowgreen': '#bbf90f', 'baby poo': '#ab9004', 'dark seafoam': '#1fb57a', 'deep teal': '#00555a', 'heather': '#a484ac', 'rust orange': '#c45508', 'dirty blue': '#3f829d', 'fern green': '#548d44', 'bright lilac': '#c95efb', 'weird green': '#3ae57f', 'peacock blue': '#016795', 'avocado green': '#87a922', 'faded orange': '#f0944d', 'grape purple': '#5d1451', 'hot green': '#25ff29', 'lime yellow': '#d0fe1d', 'mango': '#ffa62b', 'shamrock': '#01b44c', 'bubblegum': '#ff6cb5', 'purplish brown': '#6b4247', 'vomit yellow': '#c7c10c', 'pale cyan': '#b7fffa', 'key lime': '#aeff6e', 'tomato red': '#ec2d01', 'lightgreen': '#76ff7b', 'merlot': '#730039', 'night blue': '#040348', 'purpleish pink': '#df4ec8', 'apple': '#6ecb3c', 'baby poop green': '#8f9805', 'green apple': '#5edc1f', 'heliotrope': '#d94ff5', 'yellow/green': '#c8fd3d', 'almost black': '#070d0d', 'cool blue': '#4984b8', 'leafy green': '#51b73b', 'mustard brown': '#ac7e04', 'dusk': '#4e5481', 'dull brown': '#876e4b', 'frog green': '#58bc08', 'vivid green': '#2fef10', 'bright light green': '#2dfe54', 'fluro green': '#0aff02', 'kiwi': '#9cef43', 'seaweed': '#18d17b', 'navy green': '#35530a', 'ultramarine blue': '#1805db', 'iris': '#6258c4', 'pastel orange': '#ff964f', 'yellowish orange': '#ffab0f', 'perrywinkle': '#8f8ce7', 'tealish': '#24bca8', 'dark plum': '#3f012c', 'pear': '#cbf85f', 'pinkish orange': '#ff724c', 'midnight purple': '#280137', 'light urple': '#b36ff6', 'dark mint': '#48c072', 'greenish tan': '#bccb7a', 'light burgundy': '#a8415b', 'turquoise blue': '#06b1c4', 'ugly pink': '#cd7584', 'sandy': '#f1da7a', 'electric pink': '#ff0490', 'muted purple': '#805b87', 'mid green': '#50a747', 'greyish': '#a8a495', 'neon yellow': '#cfff04', 'banana': '#ffff7e', 'carnation pink': '#ff7fa7', 'tomato': '#ef4026', 'sea': '#3c9992', 'muddy brown': '#886806', 'turquoise green': '#04f489', 'buff': '#fef69e',
    'fawn': '#cfaf7b', 'muted blue': '#3b719f', 'pale rose': '#fdc1c5', 'dark mint green': '#20c073', 'amethyst': '#9b5fc0', 'blue/green': '#0f9b8e', 'chestnut': '#742802', 'sick green': '#9db92c', 'pea': '#a4bf20', 'rusty orange': '#cd5909', 'stone': '#ada587', 'rose red': '#be013c', 'pale aqua': '#b8ffeb', 'deep orange': '#dc4d01', 'earth': '#a2653e', 'mossy green': '#638b27', 'grassy green': '#419c03', 'pale lime green': '#b1ff65', 'light grey blue': '#9dbcd4', 'pale grey': '#fdfdfe', 'asparagus': '#77ab56', 'blueberry': '#464196', 'purple red': '#990147', 'pale lime': '#befd73', 'greenish teal': '#32bf84', 'caramel': '#af6f09', 'deep magenta': '#a0025c', 'light peach': '#ffd8b1', 'milk chocolate': '#7f4e1e', 'ocher': '#bf9b0c', 'off green': '#6ba353', 'purply pink': '#f075e6', 'lightblue': '#7bc8f6', 'dusky blue': '#475f94', 'golden': '#f5bf03', 'light beige': '#fffeb6', 'butter yellow': '#fffd74', 'dusky purple': '#895b7b', 'french blue': '#436bad', 'ugly yellow': '#d0c101', 'greeny yellow': '#c6f808', 'orangish red': '#f43605', 'shamrock green': '#02c14d', 'orangish brown': '#b25f03', 'tree green': '#2a7e19', 'deep violet': '#490648', 'gunmetal': '#536267', 'blue/purple': '#5a06ef', 'cherry': '#cf0234', 'sandy brown': '#c4a661', 'warm grey': '#978a84', 'dark indigo': '#1f0954', 'midnight': '#03012d', 'bluey green': '#2bb179', 'grey pink': '#c3909b', 'soft purple': '#a66fb5', 'blood': '#770001', 'brown red': '#922b05', 'medium grey': '#7d7f7c', 'berry': '#990f4b', 'poo': '#8f7303', 'purpley pink': '#c83cb9', 'light salmon': '#fea993', 'snot': '#acbb0d', 'easter purple': '#c071fe', 'light yellow green': '#ccfd7f', 'dark navy blue': '#00022e', 'drab': '#828344', 'light rose': '#ffc5cb', 'rouge': '#ab1239', 'purplish red': '#b0054b', 'slime green': '#99cc04', 'baby poop': '#937c00', 'irish green': '#019529', 'pink/purple': '#ef1de7', 'dark navy': '#000435', 'greeny blue': '#42b395', 'light plum': '#9d5783', 'pinkish grey': '#c8aca9', 'dirty orange': '#c87606', 'rust red': '#aa2704', 'pale lilac': '#e4cbff', 'orangey red': '#fa4224', 'primary blue': '#0804f9', 'kermit green': '#5cb200', 'brownish purple': '#76424e', 'murky green': '#6c7a0e', 'wheat': '#fbdd7e', 'very dark purple': '#2a0134', 'bottle green': '#044a05', 'watermelon': '#fd4659', 'deep sky blue': '#0d75f8', 'fire engine red': '#fe0002', 'yellow ochre': '#cb9d06', 'pumpkin orange': '#fb7d07', 'pale olive': '#b9cc81', 'light lilac': '#edc8ff', 'lightish green': '#61e160', 'carolina blue': '#8ab8fe', 'mulberry': '#920a4e', 'shocking pink': '#fe02a2', 'auburn': '#9a3001', 'bright lime green': '#65fe08', 'celadon': '#befdb7', 'pinkish brown': '#b17261', 'poo brown': '#885f01', 'bright sky blue': '#02ccfe', 'celery': '#c1fd95', 'dirt brown': '#836539', 'strawberry': '#fb2943', 'dark lime': '#84b701', 'copper': '#b66325', 'medium brown': '#7f5112', 'muted green': '#5fa052', 'robins egg': '#6dedfd', 'bright aqua': '#0bf9ea', 'bright lavender': '#c760ff', 'ivory': '#ffffcb', 'very light purple': '#f6cefc', 'light navy': '#155084', 'pink red': '#f5054f', 'olive brown': '#645403', 'poop brown': '#7a5901', 'mustard green': '#a8b504', 'ocean green': '#3d9973', 'very dark blue': '#000133', 'dusty green': '#76a973', 'light navy blue': '#2e5a88', 'minty green': '#0bf77d', 'adobe': '#bd6c48', 'barney': '#ac1db8', 'jade green': '#2baf6a', 'bright light blue': '#26f7fd', 'light lime': '#aefd6c', 'dark khaki': '#9b8f55', 'orange yellow': '#ffad01', 'ocre': '#c69c04', 'maize': '#f4d054', 'faded pink': '#de9dac', 'british racing green': '#05480d', 'sandstone': '#c9ae74', 'mud brown': '#60460f', 'light sea green': '#98f6b0', 'robin egg blue': '#8af1fe', 'aqua marine': '#2ee8bb', 'dark sea green': '#11875d', 'soft pink': '#fdb0c0', 'orangey brown': '#b16002', 'cherry red': '#f7022a', 'burnt yellow': '#d5ab09', 'brownish grey': '#86775f', 'camel': '#c69f59', 'purplish grey': '#7a687f', 'marine': '#042e60', 'greyish pink': '#c88d94', 'pale turquoise': '#a5fbd5', 'pastel yellow': '#fffe71', 'bluey purple': '#6241c7', 'canary yellow': '#fffe40', 'faded red': '#d3494e', 'sepia': '#985e2b', 'coffee': '#a6814c', 'bright magenta': '#ff08e8', 'mocha': '#9d7651', 'ecru': '#feffca', 'purpleish': '#98568d', 'cranberry': '#9e003a', 'darkish green': '#287c37', 'brown orange': '#b96902', 'dusky rose': '#ba6873', 'melon': '#ff7855', 'sickly green': '#94b21c', 'silver': '#c5c9c7', 'purply blue': '#661aee', 'purpleish blue': '#6140ef', 'hospital green': '#9be5aa', 'shit brown': '#7b5804', 'mid blue': '#276ab3', 'amber': '#feb308', 'easter green': '#8cfd7e', 'soft blue': '#6488ea', 'cerulean blue': '#056eee', 'golden brown': '#b27a01', 'bright turquoise': '#0ffef9', 'red pink': '#fa2a55', 'red purple': '#820747', 'greyish brown': '#7a6a4f', 'vermillion': '#f4320c', 'russet': '#a13905', 'steel grey': '#6f828a', 'lighter purple': '#a55af4', 'bright violet': '#ad0afd', 'prussian blue': '#004577', 'slate green': '#658d6d', 'dirty pink': '#ca7b80', 'dark blue green': '#005249', 'pine': '#2b5d34', 'yellowy green': '#bff128', 'dark gold': '#b59410', 'bluish': '#2976bb', 'darkish blue': '#014182', 'dull red': '#bb3f3f', 'pinky red': '#fc2647', 'bronze': '#a87900', 'pale teal': '#82cbb2', 'military green': '#667c3e', 'barbie pink': '#fe46a5', 'bubblegum pink': '#fe83cc', 'pea soup green': '#94a617', 'dark mustard': '#a88905', 'shit': '#7f5f00', 'medium purple': '#9e43a2', 'very dark green': '#062e03', 'dirt': '#8a6e45', 'dusky pink': '#cc7a8b', 'red violet': '#9e0168', 'lemon yellow': '#fdff38', 'pistachio': '#c0fa8b', 'dull yellow': '#eedc5b', 'dark lime green': '#7ebd01', 'denim blue': '#3b5b92', 'teal blue': '#01889f', 'lightish blue': '#3d7afd', 'purpley blue': '#5f34e7', 'light indigo': '#6d5acf', 'swamp green': '#748500', 'brown green': '#706c11', 'dark maroon': '#3c0008', 'hot purple': '#cb00f5', 'dark forest green': '#002d04', 'faded blue': '#658cbb', 'drab green': '#749551', 'light lime green': '#b9ff66', 'snot green': '#9dc100', 'yellowish': '#faee66', 'light blue green': '#7efbb3', 'bordeaux': '#7b002c', 'light mauve': '#c292a1', 'ocean': '#017b92', 'marigold': '#fcc006', 'muddy green': '#657432', 'dull orange': '#d8863b', 'steel': '#738595', 'electric purple': '#aa23ff', 'fluorescent green': '#08ff08', 'yellowish brown': '#9b7a01', 'blush': '#f29e8e', 'soft green': '#6fc276', 'bright orange': '#ff5b00', 'lemon': '#fdff52', 'purple grey': '#866f85', 'acid green': '#8ffe09', 'pale lavender': '#eecffe', 'violet blue': '#510ac9', 'light forest green': '#4f9153', 'burnt red': '#9f2305', 'khaki green': '#728639', 'cerise': '#de0c62', 'faded purple': '#916e99', 'apricot': '#ffb16d', 'dark olive green': '#3c4d03', 'grey brown': '#7f7053', 'green grey': '#77926f', 'true blue': '#010fcc', 'pale violet': '#ceaefa', 'periwinkle blue': '#8f99fb', 'light sky blue': '#c6fcff', 'blurple': '#5539cc', 'green brown': '#544e03', 'bluegreen': '#017a79', 'bright teal': '#01f9c6', 'brownish yellow': '#c9b003', 'pea soup': '#929901', 'forest': '#0b5509', 'barney purple': '#a00498', 'ultramarine': '#2000b1', 'purplish': '#94568c', 'puke yellow': '#c2be0e', 'bluish grey': '#748b97', 'dark periwinkle': '#665fd1', 'dark lilac': '#9c6da5', 'reddish': '#c44240', 'light maroon': '#a24857', 'dusty purple': '#825f87', 'terra cotta': '#c9643b', 'avocado': '#90b134', 'marine blue': '#01386a', 'teal green': '#25a36f', 'slate grey': '#59656d', 'lighter green': '#75fd63', 'electric green': '#21fc0d', 'dusty blue': '#5a86ad', 'golden yellow': '#fec615', 'bright yellow': '#fffd01', 'light lavender': '#dfc5fe', 'umber': '#b26400', 'poop': '#7f5e00', 'dark peach': '#de7e5d', 'jungle green': '#048243', 'eggshell': '#ffffd4', 'denim': '#3b638c', 'yellow brown': '#b79400', 'dull purple': '#84597e', 'chocolate brown': '#411900', 'wine red': '#7b0323', 'neon blue': '#04d9ff', 'dirty green': '#667e2c', 'light tan': '#fbeeac', 'ice blue': '#d7fffe', 'cadet blue': '#4e7496', 'dark mauve': '#874c62', 'very light blue': '#d5ffff', 'grey purple': '#826d8c', 'pastel pink': '#ffbacd', 'very light green': '#d1ffbd', 'dark sky blue': '#448ee4', 'evergreen': '#05472a', 'dull pink': '#d5869d', 'aubergine': '#3d0734', 'mahogany': '#4a0100', 'reddish orange': '#f8481c', 'deep green': '#02590f', 'vomit green': '#89a203', 'purple pink': '#e03fd8', 'dusty pink': '#d58a94', 'faded green': '#7bb274', 'camo green': '#526525', 'pinky purple': '#c94cbe', 'pink purple': '#db4bda', 'brownish red': '#9e3623', 'dark rose': '#b5485d', 'mud': '#735c12', 'brownish': '#9c6d57', 'emerald green': '#028f1e', 'pale brown': '#b1916e', 'dull blue': '#49759c', 'burnt umber': '#a0450e', 'medium green': '#39ad48', 'clay': '#b66a50', 'light aqua': '#8cffdb', 'light olive green': '#a4be5c', 'brownish orange': '#cb7723', 'dark aqua': '#05696b', 'purplish pink': '#ce5dae', 'dark salmon': '#c85a53', 'greenish grey': '#96ae8d', 'jade': '#1fa774', 'ugly green': '#7a9703', 'dark beige': '#ac9362', 'emerald': '#01a049', 'pale red': '#d9544d', 'light magenta': '#fa5ff7', 'sky': '#82cafc', 'light cyan': '#acfffc', 'yellow orange': '#fcb001', 'reddish purple': '#910951', 'reddish pink': '#fe2c54', 'orchid': '#c875c4', 'dirty yellow': '#cdc50a', 'orange red': '#fd411e', 'deep red': '#9a0200', 'orange brown': '#be6400', 'cobalt blue': '#030aa7', 'neon pink': '#fe019a', 'rose pink': '#f7879a', 'greyish purple': '#887191', 'raspberry': '#b00149', 'aqua green': '#12e193', 'salmon pink': '#fe7b7c', 'tangerine': '#ff9408', 'brownish green': '#6a6e09', 'red brown': '#8b2e16', 'greenish brown': '#696112', 'pumpkin': '#e17701', 'pine green': '#0a481e', 'charcoal': '#343837', 'baby pink': '#ffb7ce', 'cornflower': '#6a79f7', 'blue violet': '#5d06e9', 'chocolate': '#3d1c02', 'greyish green': '#82a67d', 'scarlet': '#be0119', 'green yellow': '#c9ff27', 'dark olive': '#373e02', 'sienna': '#a9561e', 'pastel purple': '#caa0ff', 'terracotta': '#ca6641', 'aqua blue': '#02d8e9', 'sage green': '#88b378', 'blood red': '#980002', 'deep pink': '#cb0162', 'grass': '#5cac2d', 'moss': '#769958',
    'pastel blue': '#a2bffe', 'bluish green': '#10a674', 'green blue': '#06b48b', 'dark tan': '#af884a', 'greenish blue': '#0b8b87', 'pale orange': '#ffa756', 'vomit': '#a2a415', 'forrest green': '#154406', 'dark lavender': '#856798', 'dark violet': '#34013f', 'purple blue': '#632de9', 'dark cyan': '#0a888a', 'olive drab': '#6f7632', 'pinkish': '#d46a7e', 'cobalt': '#1e488f', 'neon purple': '#bc13fe', 'light turquoise': '#7ef4cc', 'apple green': '#76cd26', 'dull green': '#74a662', 'wine': '#80013f', 'powder blue': '#b1d1fc', 'off white': '#ffffe4', 'electric blue': '#0652ff', 'dark turquoise': '#045c5a', 'blue purple': '#5729ce', 'azure': '#069af3', 'bright red': '#ff000d', 'pinkish red': '#f10c45', 'cornflower blue': '#5170d7', 'light olive': '#acbf69', 'grape': '#6c3461', 'greyish blue': '#5e819d', 'purplish blue': '#601ef9', 'yellowish green': '#b0dd16', 'greenish yellow': '#cdfd02', 'medium blue': '#2c6fbb', 'dusty rose': '#c0737a', 'light violet': '#d6b4fc', 'midnight blue': '#020035', 'bluish purple': '#703be7', 'red orange': '#fd3c06', 'dark magenta': '#960056', 'greenish': '#40a368', 'ocean blue': '#03719c', 'coral': '#fc5a50', 'cream': '#ffffc2', 'reddish brown': '#7f2b0a', 'burnt sienna': '#b04e0f', 'brick': '#a03623', 'sage': '#87ae73', 'grey green': '#789b73', 'white': '#ffffff', 'robins egg blue': '#98eff9', 'moss green': '#658b38', 'steel blue': '#5a7d9a', 'eggplant': '#380835', 'light yellow': '#fffe7a', 'leaf green': '#5ca904', 'light grey': '#d8dcd6', 'puke': '#a5a502', 'pinkish purple': '#d648d7', 'sea blue': '#047495', 'pale purple': '#b790d4', 'slate blue': '#5b7c99', 'blue grey': '#607c8e', 'hunter green': '#0b4008', 'fuchsia': '#ed0dd9', 'crimson': '#8c000f', 'pale yellow': '#ffff84', 'ochre': '#bf9005', 'mustard yellow': '#d2bd0a', 'light red': '#ff474c', 'cerulean': '#0485d1', 'pale pink': '#ffcfdc', 'deep blue': '#040273', 'rust': '#a83c09', 'light teal': '#90e4c1', 'slate': '#516572', 'goldenrod': '#fac205', 'dark yellow': '#d5b60a', 'dark grey': '#363737', 'army green': '#4b5d16', 'grey blue': '#6b8ba4', 'seafoam': '#80f9ad', 'puce': '#a57e52', 'spring green': '#a9f971', 'dark orange': '#c65102', 'sand': '#e2ca76', 'pastel green': '#b0ff9d', 'mint': '#9ffeb0', 'light orange': '#fdaa48', 'bright pink': '#fe01b1', 'chartreuse': '#c1f80a', 'deep purple': '#36013f', 'dark brown': '#341c02', 'taupe': '#b9a281', 'pea green': '#8eab12', 'puke green': '#9aae07', 'kelly green': '#02ab2e', 'seafoam green': '#7af9ab', 'blue green': '#137e6d', 'khaki': '#aaa662', 'burgundy': '#610023', 'dark teal': '#014d4e', 'brick red': '#8f1402', 'royal purple': '#4b006e', 'plum': '#580f41', 'mint green': '#8fff9f', 'gold': '#dbb40c', 'baby blue': '#a2cffe', 'yellow green': '#c0fb2d', 'bright purple': '#be03fd', 'dark red': '#840000', 'pale blue': '#d0fefe', 'grass green': '#3f9b0b', 'navy': '#01153e', 'aquamarine': '#04d8b2', 'burnt orange': '#c04e01', 'neon green': '#0cff0c', 'bright blue': '#0165fc', 'rose': '#cf6275', 'light pink': '#ffd1df', 'mustard': '#ceb301', 'indigo': '#380282', 'lime': '#aaff32', 'sea green': '#53fca1', 'periwinkle': '#8e82fe', 'dark pink': '#cb416b', 'olive green': '#677a04', 'peach': '#ffb07c', 'pale green': '#c7fdb5', 'light brown': '#ad8150', 'hot pink': '#ff028d', 'black': '#000000', 'lilac': '#cea2fd', 'navy blue': '#001146', 'royal blue': '#0504aa', 'beige': '#e6daa6', 'salmon': '#ff796c', 'olive': '#6e750e', 'maroon': '#650021', 'bright green': '#01ff07', 'dark purple': '#35063e', 'mauve': '#ae7181', 'forest green': '#06470c', 'aqua': '#13eac9', 'cyan': '#00ffff', 'tan': '#d1b26f', 'dark blue': '#00035b', 'lavender': '#c79fef', 'turquoise': '#06c2ac', 'dark green': '#033500', 'violet': '#9a0eea', 'light purple': '#bf77f6', 'lime green': '#89fe05', 'grey': '#929591', 'sky blue': '#75bbfd', 'yellow': '#ffff14', 'magenta': '#c20078', 'light green': '#96f97b', 'orange': '#f97306', 'teal': '#029386', 'light blue': '#95d0fc', 'red': '#e50000', 'brown': '#653700', 'pink': '#ff81c0', 'blue': '#0343df', 'green': '#15b01a', 'purple': '#7e1e9c'}}}

def convert_jpg(file, folder = 'flag_images/', delete = False):
    filepath = folder + file
    print(file)
    img = Image.open(filepath, mode = 'r')
    if img.mode != 'RGB':
       img = img.convert('RGB')
    if delete:
        img.save(folder + 'backup/' + file)
        os.remove(filepath)

    filepath = filepath[0:-3] + 'jpg'
    img.save(filepath)

def convert_all(folder = 'flag_images/'):
    for filename in os.listdir(os.path.abspath(os.getcwd()) + '/flag_images'):
        if (filename[-3:] != 'jpg') and (filename[-4] == '.'):
            convert_jpg(file = filename, folder = folder, delete = True)

def check_modes(folder = 'flag_images'):
    for filename in os.listdir(os.path.abspath(os.getcwd()) + '/flag_images'):
        if filename[-4] == '.':
            img = Image.open(folder + '/' + filename)
            print(filename, img.mode)

def closest_color(color, palette):
    min_colours = {}
    for key, name in palette['hex_to_name'].items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - color[0]) ** 2
        gd = (g_c - color[1]) ** 2
        bd = (b_c - color[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    color_name = min_colours[min(min_colours.keys())]
    color_hex = palette['name_to_hex'][color_name]
    color_rgb = webcolors.hex_to_rgb(color_hex)
    return color_rgb, color_hex, color_name
    # return min_colours[min(min_colours.keys())]

def color_name(requested_colour):
    try:
        # closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
        actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        # closest_name = closest_colour(requested_colour)
        actual_name = 'UNNAMED'
    return actual_name

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def rgb_text(color):
    return 'r' + str(color[0]) + ' g' + str(color[1]) + ' b' + str(color[2])

RGB_SCALE = 255
CMYK_SCALE = 100


def rgb_to_cmyk(color):
    r = color[0]
    g = color[1]
    b = color[2]
    if (r, g, b) == (0, 0, 0):
        return 'c0, m0, y0, k100'

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

    _c = round(c*100, 2)
    _m = round(m*100, 2)
    _y = round(y*100, 2)
    _k = round(k*100, 2)

    # rescale to the range [0,CMYK_SCALE]
    cmyk = (f'c{_c} m{_m} y{_y} k{_k}') 
    return cmyk

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
    # return sqrt((rd^2) + (gd^2) +(bd^2))
    # return sqrt((color1[0] - color2[0])^2 + (color1[1] - color2[1])^2 + (color1[2] - color2[2])^2)

def value_sort(dct):
    return {k: v for k, v in sorted(dct.items(), key=lambda item: item[1], reverse=True)}
# def find_name(color, color_lookup = css3_colors):
#     sim = [(similarity(color, c), name) for c, name in color_lookup.items()]
#     return max(sim, key=lambda x: x[0])[1]

# def color_to_rgb(color):
#     return tuple(int(x, 16) / 255.0 for x in re_color.match(color).groups())

def similarity(color1, color2):
    """Computes the pearson correlation coefficient for two colors. The result
    will be between 1.0 (very similar) and -1.0 (no similarity)."""
    c1 = color1
    c2 = color2

    s1 = sum(c1)
    s2 = sum(c2)
    sp1 = sum(map(lambda c: pow(c, 2), c1))
    sp2 = sum(map(lambda c: pow(c, 2), c2))
    sp = sum(map(lambda x: x[0] * x[1], zip(c1, c2)))

    try:
        computed = (sp - (s1 * s2 / 3.0)) / sqrt((sp1 - pow(s1, 2) / 3.0) * (sp2 - pow(s2, 2) / 3.0))
    except:
        computed = 0
    return computed

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
       self.base_image = Image.open(self.filepath)
       self.base_image = self.base_image.convert(mode ='RGB')

    # def draw_palette(self, colors, swatchsize=20):
    #     num_colors = len(colors)
    #     palette = Image.new('RGB', (swatchsize*num_colors, swatchsize))
    #     draw = ImageDraw.Draw(palette)
    #     posx = 0
    #     for color in colors:
    #         draw.rectangle([posx, 0, posx+swatchsize, swatchsize], fill=color) 
    #         posx = posx + swatchsize
    #     del draw
    #     palette.save(outfile, "PNG")
    
    def base_colors(self, resize = False):
        # Resize image to speed up processing
        img = self.base_image.copy()
        if resize:
            img.thumbnail((resize, resize))

        # Reduce to palette
        paletted = img.quantize(colors=self.num_colors, kmeans = self.num_colors).convert('RGB')
        # paletted = img.convert('P', palette=Image.ADAPTIVE, colors=self.num_colors)
        self.flattened_image = paletted
        
        # Find dominant colors
        palette = paletted.getpalette()
        color_counts = sorted(paletted.getcolors(), reverse=True)
        colors_rgb = list()
        for i in range(self.num_colors):
            colors_rgb.append(color_counts[i][1])
        colors_hex =[]
        colors_names = []
        for color in colors_rgb:
            colors_hex.append(rgb_to_hex(color))
            colors_names.append(color_name(color))
        self.base_palette = []
        self.base_palette.append(colors_rgb)
        self.base_palette.append(colors_hex)
        self.base_palette.append(colors_names)
        # self.base_palette_HEX = [color_to_rgb(color) for color in colors]
        return colors_rgb, colors_hex, colors_names

    def derive_palettes(self):
        if not hasattr(self, 'base_palette'):
            self.base_colors(resize = False)
        palette_conversion = {'base': self.base_palette[0], 'css3':[], 'xkcd':[]}
        for palette in palettes.keys():
            for base_rgb in palette_conversion['base']:
                # print(base_rgb, palettes[palette])

                _rgb, _hex, _name = closest_color(base_rgb, palettes[palette])
                palette_conversion[palette].append(_rgb)
        self.palette_matrix = palette_conversion
        return palette_conversion

    def convert_images(self, show = False):
        if not hasattr(self, 'palette_matrix'):
            self.derive_palettes()
        image_matrix = {'raw': self.base_image, 'flat':self.flattened_image}
        for palette in palettes.keys():
            conversion = dict(zip(self.palette_matrix['base'], self.palette_matrix[palette]))
            img = self.flattened_image.copy()
            pixels = img.load()
            for x in range(img.size[0]):
                for y in range(img.size[1]):
                    pixels[x, y] = conversion[pixels[x, y]]
            image_matrix[palette] = img
        if show:
            for palette in image_matrix.keys():
                print(palette)
                pause = input()
                image_matrix[palette].show()
        self.image_matrix = image_matrix

    def show_palette(self, palette):
        if not hasattr(self, 'palette_matrix'):
            self.derive_palettes()
        if palette != 'base':
            for color in self.palette_matrix[palette]:
                _rgb = color
                _hex = '#' + rgb_to_hex(color)
                _name = palettes[palette]['hex_to_name'][_hex]
                print(_rgb, _hex, _name)

                # img.putpixel((x, y), self.xkcd_convert[color])
        # if palette == xkcd_colors:
        #     self.xkcd_image = img
        # elif palette == css3_colors:
        #     self.css3_image = img
        # css3_img = self.flattend_image
        # pixels_html = css3_img.load()
        # for x in range(css3_img.size[0]):
        #     for y in range(css3_img.size[1]):
        #         pixels_html[x, y] = self.css3_convert[pixels_html[x, y]]
        #         # css3_img.putpixel((x, y), self.css3_convert[color])
        # self.css3_image = css3_img



    def base_palette(self, save = False):
        img = self.base_image
        width, height = img.size
        by_color = defaultdict(int)
        for pixel in img.getdata():
            by_color[pixel] += 1
        # top_colors = dict(sorted(by_color.items(), key = itemgetter(1), reverse= True)[:(self.num_colors)])
        palette = []
        for color, count in by_color.items():
                palette.append(color)
        # if save:
        #     save_palette(palette, outfile = 'flag_images/palettes/' + filename)
        self.raw_colors = value_sort(by_color)
        return palette


    # for filename in os.listdir(os.path.abspath(os.getcwd()) + '/flag_images'):
    #     if filename.endswith('.jpg') or filename.endswith('png'):
    #         print(filename, len(define_palette(filename = filename, save = True)))

def flag_dataframe(flag, palette = 'xkcd'):
    flag = Flag(flag)
    flag.base_colors()
    flag.derive_palettes()
    flag.convert_images(show = False)
    swatch = flag.palette_matrix[palette]
    columns = ['flag_name', 'NAME', 'RGB', 'CMYK', 'HEX', 'Marker', 'Swatch']
    df = pd.DataFrame(columns = columns)
    for color in range(0, flag.num_colors - 1):
        flag_name = flag.name
        color_tuple = tuple(swatch[color])
        color_hex = "#" + rgb_to_hex(color_tuple)
        color_rgb = rgb_text(color_tuple)
        color_name = palettes[palette]['hex_to_name'][color_hex]
        color_cmyk = rgb_to_cmyk(color_tuple)
        row = [flag_name, color_name, color_rgb, color_cmyk, color_hex, '', '']
        df = df.append(dict(zip(columns, row)), ignore_index= True)
    return df

if __name__ == '__main__':
    flag_data = pd.read_csv('flag_data.csv', sep = '|')
    flag_data.set_index('Name', inplace=True)