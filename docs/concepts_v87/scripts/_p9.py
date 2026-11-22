import io
s = io.open('roster.py', encoding='utf-8').read()
a = "    'lynx': ('sneak_peek', 'stretch', 'Open_Part'), 'sabertooth': ('sky_leap', 'head_toss', 'Open_Burst'),\n"
assert a in s
s = s.replace(a, a + "    'deer': ('leap', 'look_around', 'Open_Part'), 'moose': ('march', 'head_toss', 'Open_Part'),\n"
  "    'bear': ('sneak_peek', 'rear_up', 'Open_Part'), 'bison': ('charge', 'shake_off', 'Open_Burst'),\n"
  "    'cavebear': ('shadow_rise', 'roar', 'Open_Burst'), 'spiritdeer': ('pillar_rise', 'bow', 'Open_Burst'),\n")
io.open('roster.py', 'w', encoding='utf-8', newline='\n').write(s)
