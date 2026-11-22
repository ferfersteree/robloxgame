import io

s = io.open('roster.py', encoding='utf-8').read()
a = "    'abyss_leviathan': ('splash_up', 'roar', 'Open_Burst'), 'reef_lobster': ('comet_fall', 'claw_snap', 'Open_Burst'),\n"
assert a in s
s = s.replace(a, a + """    'cinder_porcupine': ('crawl_out', 'puff_up', 'Open_Part'), 'ash_lizard': ('zigzag', 'look_around', 'Open_Part'),
    'ash_anteater': ('sneak_peek', 'sniff', 'Open_Part'), 'ember_boar': ('charge', 'roar', 'Open_Burst'),
    'lava_golem': ('quake_rise', 'chest_beat', 'Open_Burst'), 'ember_mandrill': ('flash_appear', 'clap', 'Open_Burst'),
    'furnace_stag_beetle': ('dig_out', 'antenna_twitch', 'Open_Part'), 'obsidian_crab': ('tumble', 'claw_snap', 'Open_Burst'),
    'caldera_toad': ('hop_series', 'puff_up', 'Open_Part'), 'magma_rhino': ('titan_step', 'stomp_hoof', 'Open_Burst'),
    'phoenix': ('rocket_up', 'wing_puff', 'Open_Burst'), 'obsidian_pangolin': ('pillar_rise', 'coil', 'Open_Burst'),
    'prism_moth': ('flutter_out', 'sparkle_burst', 'Open_Part'), 'crystal_bat': ('loop_in', 'ear_wiggle', 'Open_Burst'),
    'geode_mole': ('dig_out', 'look_around', 'Open_Part'), 'amethyst_fox': ('leap', 'tail_wave', 'Open_Part'),
    'crystal_anemone': ('mound_burst_giant', 'pulse', 'Open_Burst'), 'quartz_dragon': ('shadow_rise', 'wing_flap', 'Open_Burst'),
    'aurora_weasel': ('zigzag', 'stretch', 'Open_Part'), 'arctic_hare': ('hop_series', 'wave_paw', 'Open_Part'),
    'moon_owl': ('spiral_up', 'preen', 'Open_Burst'), 'lunar_wolf': ('sneak_peek', 'roar', 'Open_Part'),
    'tundra_muskox': ('quake_rise', 'stomp_hoof', 'Open_Burst'), 'aurora_bear': ('comet_fall', 'bow', 'Open_Burst'),
""")
io.open('roster.py', 'w', encoding='utf-8', newline=chr(10)).write(s)
print('ok')
