import io
s = io.open('moves.py', encoding='utf-8').read()
a = "kk(c, s, max(L_, last['f'] + 2) if last['f'] >= L_ - 1 else L_, **{fld: restv})"
assert a in s
s = s.replace(a, "kk(c, s, L_, **{fld: restv})")
io.open('moves.py', 'w', encoding='utf-8', newline='\n').write(s)
