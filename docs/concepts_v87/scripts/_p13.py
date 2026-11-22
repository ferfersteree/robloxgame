import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('moves.py', [
 ("    GESTURES[a.gesture](a, c, T, n)\n", "    GESTURES[a.gesture](a, c, T, n)\n    for fn in getattr(a, 'extra_reveal', []):\n        fn(c, T, n)\n"),
])
sub('kits.py', [
 ("    a.legs, a.arms, a.ears, a.wings, a.tail, a.extra_idle = [], [], [], [], [], []\n",
  "    a.legs, a.arms, a.ears, a.wings, a.tail, a.extra_idle, a.extra_reveal = [], [], [], [], [], [], []\n"),
])
sub('roster.py', [
 ("    'cavebear': ('shadow_rise', 'roar', 'Open_Burst'), 'spiritdeer': ('pillar_rise', 'bow', 'Open_Burst'),\n",
  "    'cavebear': ('shadow_rise', 'roar', 'Open_Burst'), 'spiritdeer': ('pillar_rise', 'bow', 'Open_Burst'),\n"
  "    'megadeer': ('trot', 'rear_up', 'Open_Part'), 'rhino': ('march', 'stomp_hoof', 'Open_Part'),\n"
  "    'mammoth': ('titan_step', 'roar', 'Open_Burst'), 'cavelion': ('pounce', 'stretch', 'Open_Burst'),\n"
  "    'icemammoth': ('quake_rise', 'head_toss', 'Open_Burst'), 'yeti': ('mound_burst_giant', 'chest_beat', 'Open_Burst'),\n"),
])
print('ok')
