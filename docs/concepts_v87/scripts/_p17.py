import io
s = io.open('roster.py', encoding='utf-8').read()
a = "    'icemammoth': ('quake_rise', 'head_toss', 'Open_Burst'), 'yeti': ('mound_burst_giant', 'chest_beat', 'Open_Burst'),\n"
assert a in s
s = s.replace(a, a + "    'watchful_meerkat': ('dig_out', 'look_around', 'Open_Part'), 'gazelle': ('leap', 'jump_joy', 'Open_Part'),\n"
  "    'savanna_ostrich': ('zigzag', 'preen', 'Open_Part'), 'hyena': ('sneak_peek', 'wiggle', 'Open_Part'),\n"
  "    'sunlion': ('flash_appear', 'roar', 'Open_Burst'), 'amber_giraffe': ('titan_step', 'head_toss', 'Open_Burst'),\n")
io.open('roster.py', 'w', encoding='utf-8', newline='\n').write(s)
