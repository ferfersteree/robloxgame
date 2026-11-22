import io
def sub(fn, pairs):
    s = io.open(fn, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (fn, a[:60])
        s = s.replace(a, b)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(s)
sub('kits.py', [
 ("def fish(bw=1.0, bl=1.5, bh=1.1, face_h=0.9, fin=(0.5, 0.5, 0.12), tail=(0.14, 0.5, 0.9), dorsal=0.35, belly=True, ntail=1):",
  "def fish(bw=1.0, bl=1.5, bh=1.1, face_h=0.9, fin=(0.5, 0.5, 0.12), tail=(0.14, 0.5, 0.9), dorsal=0.35, belly=True, ntail=1, zc=None):"),
 ("    a = K.a\n    zc = K.Z0\n    sg('body', 'root', (0, 0.1, zc))\n    B = b('body', (bw, bl, bh), mm('main'), (0, 0.2, zc))\n    b('body_back',",
  "    a = K.a\n    zc = K.Z0 if zc is None else zc\n    sg('body', 'root', (0, 0.1, zc))\n    B = b('body', (bw, bl, bh), mm('main'), (0, 0.2, zc))\n    b('body_back',"),
])
print('ok')
