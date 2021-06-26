from flags import *

flag_data = pd.read_csv('flag_data.csv', sep = '|')
flag_data.set_index('Name', inplace=True)
main_flags = list(flag_data.index[flag_data.Folder == 'main'])
fetish_flags = list(flag_data.index[flag_data.Folder == 'fetish'])
palette_lookup = {}
for name, _hex in mcolors.get_named_colors_mapping().items():
    if type(_hex) == str:
        rgb = tuple(webcolors.hex_to_rgb(_hex))
        palette_lookup[rgb] = name

def existing_data():
    pride_data ={}
    for pride_flag in main_flags:
        flag = Flag(pride_flag)
        # if flag.type == 'chevron':
        print(flag.name)
        pride_data[flag.name] ={}
        df = flag.map_colors()
        palette = flag.color_map['final_rgb']
        pride_data[flag.name]['palette_rgb'] = list(palette)
        pride_data[flag.name]['palette_name'] =  [palette_lookup[x] for x in palette]
        pride_data[flag.name]['stripes'] = flag.num_stripes
        pride_data[flag.name]['stripe_palette'] =  df[df['type'] == 'stripe']['final_rgb']
        pride_data[flag.name]['stripes_dist'] =  flag.stripes_dist
        pride_data[flag.name]['chevrons'] =  flag.num_chevrons
        if hasattr(flag, 'chevron_dist'):
            pride_data[flag.name]['chevrons_dist'] =  flag.chevrons_dist
        else:
            pride_data[flag.name]['chevrons_dist'] =  None
        pride_data[flag.name]['chevron_palette'] =  list(df[df['type'] == 'chevron']['final_rgb'])
        pride_data[flag.name]['symbols'] = flag.num_symbols
        pride_data[flag.name]['symbol_palette'] =  list(df[df['type'] == 'symbol']['final_rgb'])
    return pride_data


# flag = Flag('androgynous')
# flag.flatten_image()
# pride_data[flag.name]['palette_rgb'] = flag.final_palette
# pride_data[flag.name]['palette_name'] =  [palette_lookup[x] for x in flag.final_palette]

# pride_data['asexual']['palette_rgb']
# pride_data['asexual']['palette_rgb'] = [(0, 0, 0), (169, 169, 169), (255, 255, 255), (128, 0, 128)]
# pride_data['asexual']['palette_name'] =  [palette_lookup[x] for x in pride_data['asexual']['palette_rgb']]


# pride_data['bear']['palette_rgb'] = [(101, 55, 0), (202, 107, 2), (252, 225, 102), (255, 228, 181), (255, 255, 255), (83, 98, 103), (0, 0, 0), (0, 0, 0)]
# pride_data['bear']['palette_name'] =  [palette_lookup[x] for x in pride_data['bear']['palette_rgb']]
# pride_data['bear']['stripe_palette'] = [(101, 55, 0), (202, 107, 2), (252, 225, 102), (255, 228, 181), (255, 255, 255), (83, 98, 103), (0, 0, 0)]
# pride_data['bear']['symbol_palette'] = [(0, 0, 0)]

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
