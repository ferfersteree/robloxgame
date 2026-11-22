import io

s = io.open('roster.py', encoding='utf-8').read()
a = "    'tundra_muskox': ('quake_rise', 'stomp_hoof', 'Open_Burst'), 'aurora_bear': ('comet_fall', 'bow', 'Open_Burst'),\n"
assert a in s
s = s.replace(a, a + """    'aether_ribbonfish': ('flutter_out', 'coil', 'Open_Part'), 'cloud_sheep': ('drop_from_above', 'jump_joy', 'Open_Burst'),
    'island_chameleon': ('sneak_peek', 'puff_up', 'Open_Part'), 'sky_stag': ('leap', 'rear_up', 'Open_Part'),
    'cloud_glider': ('swoop_arc', 'wing_puff', 'Open_Burst'), 'sky_drake': ('spiral_up', 'roar', 'Open_Burst'),
""")
io.open('roster.py', 'w', encoding='utf-8', newline=chr(10)).write(s)
print('ok')
