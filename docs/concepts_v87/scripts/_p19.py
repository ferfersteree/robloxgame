import io
s = io.open('roster.py', encoding='utf-8').read()
a = "    'sunlion': ('flash_appear', 'roar', 'Open_Burst'), 'amber_giraffe': ('titan_step', 'head_toss', 'Open_Burst'),\n"
assert a in s
add = """    'rock_hyrax': ('crawl_out', 'sniff', 'Open_Part'), 'mountain_goat': ('leap', 'stomp_hoof', 'Open_Part'),
    'canyon_roadrunner': ('zigzag', 'tail_wave', 'Open_Part'), 'armadillo': ('roll_ball', 'look_around', 'Open_Part'),
    'canyon_condor': ('spiral_up', 'wing_flap', 'Open_Burst'), 'redthorn_lizard': ('quake_rise', 'roar', 'Open_Burst'),
    'oasis_scarab': ('roll_ball', 'antenna_twitch', 'Open_Part'), 'fennec': ('dig_out', 'ear_wiggle', 'Open_Part'),
    'dune_jerboa': ('hop_series', 'tail_wave', 'Open_Part'), 'dune_scorpion': ('burst_from_mound', 'claw_snap', 'Open_Burst'),
    'sand_wyrm': ('quake_rise', 'coil', 'Open_Burst'), 'mirage_camel': ('rune_gate', 'head_toss', 'Open_Burst'),
    'jade_tapir': ('trot', 'sniff', 'Open_Part'), 'toucan': ('swoop_arc', 'preen', 'Open_Part'),
    'leafcutter_ant': ('march', 'flex', 'Open_Part'), 'jaguar': ('pounce', 'roar', 'Open_Burst'),
    'jungle_gorilla': ('shadow_rise', 'chest_beat', 'Open_Burst'), 'emerald_treefrog': ('sky_leap', 'puff_up', 'Open_Burst'),
    'mudskipper': ('slide_out', 'fin_flap', 'Open_Part'), 'otter': ('tumble', 'clap', 'Open_Burst'),
    'mangrove_fiddler': ('dig_out', 'claw_snap', 'Open_Part'), 'crocodile': ('crawl_out', 'roar', 'Open_Part'),
    'marsh_hydra': ('quake_rise', 'look_around', 'Open_Burst'), 'mangrove_flamingo': ('vortex_lift', 'wing_puff', 'Open_Burst'),
"""
s = s.replace(a, a + add)
io.open('roster.py', 'w', encoding='utf-8', newline='\n').write(s)
