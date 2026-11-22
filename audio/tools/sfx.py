"""Procedural sound effects for SpearHunt. Every sound is deterministic (seeded)."""
import numpy as np
from dsp import *

SOUNDS = {}   # name -> dict(data, loop, vol, use)


def reg(name, data, use, vol=0.5, loop=False, db=-3.0):
    SOUNDS[name] = dict(data=peak_norm(data, db), use=use, vol=vol, loop=loop)


def rngf(name):
    return np.random.default_rng(sum(ord(c) * (i + 7) for i, c in enumerate(name)))


# ------------------------------------------------------------------ UI
def ui_hover(f, name):
    r = rngf(name)
    dur = 0.09
    t = t_axis(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.016)
    x += 0.35 * np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 0.03)
    air = hp(noise(0.02, r), 5200) * exp_env(int(0.02 * SR), 0.004) * 0.12
    x[: len(air)] += air
    reg(name, fade(x, 0.0005, 0.01), "pointer over a button or card", vol=0.22)


for i, f in enumerate([2350, 2640, 2960]):
    ui_hover(f, f"ui_hover_{i + 1}")


def ui_press(f0, name, pitch=1.0):
    r = rngf(name)
    dur = 0.16
    body = sweep(520 * pitch, 250 * pitch, dur) * exp_env(int(dur * SR), 0.05)
    sub = sine(130 * pitch, dur) * exp_env(int(dur * SR), 0.035) * 0.5
    tick = bp(noise(0.015, r), 1500, 4200) * exp_env(int(0.015 * SR), 0.003) * 0.5
    x = body + sub
    x[: len(tick)] += tick
    top = marimba(f0, 0.35, 0.33, 0.5)
    x = fit(x, 0.35) + top * 0.35
    reg(name, fade(x, 0.0008, 0.03), "button press", vol=0.4)


for i, (f0, p) in enumerate([(1175, 1.0), (1319, 1.06), (1047, 0.95)]):
    ui_press(f0, f"ui_press_{i + 1}", p)


def ui_select(notes, name):
    x = np.zeros(int(0.9 * SR))
    for k, n in enumerate(notes):
        mix_into(x, marimba(midi(n), 0.8, 0.8), 0.07 * k, 1.0)
    x = reverb(x, rngf(name), 0.7, 0.12, 6000, stereo=False)[0]
    reg(name, x[: int(0.9 * SR)], "choosing an item, picking a tab", vol=0.4)


ui_select([76, 83], "ui_select_1")
ui_select([79, 86], "ui_select_2")

# open / close
r = rngf("ui_open")
sw = swept_bp(noise(0.45, r, "pink"), 350, 2600, 1.6) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))) ** 1.5
op = fit(sw, 0.8) * 0.9
mix_into(op, marimba(midi(79), 0.6, 0.6), 0.22, 0.55)
mix_into(op, marimba(midi(86), 0.6, 0.5), 0.30, 0.4)
reg("ui_open", fade(op, 0.002, 0.03), "window opens", vol=0.35)

r = rngf("ui_close")
sw = swept_bp(noise(0.4, r, "pink"), 2400, 320, 1.6) * np.sin(np.linspace(0, np.pi, int(0.4 * SR))) ** 1.5
cl = fit(sw, 0.6) * 0.9
mix_into(cl, marimba(midi(67), 0.5, 0.7), 0.0, 0.5)
mix_into(cl, marimba(midi(60), 0.5, 0.6), 0.09, 0.45)
reg("ui_close", fade(cl, 0.002, 0.03), "window closes", vol=0.33)


def toggle(up, name):
    x = np.zeros(int(0.5 * SR))
    a, b = (72, 79) if up else (79, 72)
    mix_into(x, marimba(midi(a), 0.4, 0.8), 0.0)
    mix_into(x, marimba(midi(b), 0.4, 0.8), 0.07)
    reg(name, x, "switch on" if up else "switch off", vol=0.35)


toggle(True, "ui_toggle_on")
toggle(False, "ui_toggle_off")

# error: a soft, muted knock
r = rngf("ui_error")
d = 0.3
x = sweep(210, 130, d) * exp_env(int(d * SR), 0.09)
x += lp(noise(d, r), 500, 2) * exp_env(int(d * SR), 0.03) * 0.5
x += marimba(midi(51), 0.3, 0.3, 0.3)
reg("ui_error", fade(x, 0.001, 0.05), "cannot do that", vol=0.45)

# back / cancel
x = np.zeros(int(0.5 * SR))
mix_into(x, marimba(midi(74), 0.4, 0.7), 0.0)
mix_into(x, marimba(midi(67), 0.4, 0.7), 0.06)
reg("ui_back", x, "back, cancel", vol=0.33)

# pop (bubble)
r = rngf("pop")
d = 0.14
x = fit(sweep(520, 1500, 0.05), d) * exp_env(int(d * SR), 0.035)
x += fit(hp(noise(0.02, r), 3000), d) * 0.2
reg("pop", fade(x, 0.0005, 0.02), "small pop for counters and bubbles", vol=0.4)

# tick
x = bell_fm(2200, 0.1, 2.0, 1.0)
reg("tick", fade(x, 0.0005, 0.02), "counter tick", vol=0.25)

# coin
x = np.zeros(int(1.0 * SR))
mix_into(x, bell_fm(1319, 0.9, 3.5, 3.0), 0.0, 1.0)
mix_into(x, bell_fm(1760, 0.9, 3.5, 3.0), 0.07, 0.8)
reg("coin", x, "coins and money", vol=0.35)
x = np.zeros(int(1.0 * SR))
mix_into(x, bell_fm(1480, 0.9, 3.5, 3.0), 0.0, 1.0)
mix_into(x, bell_fm(1976, 0.9, 3.5, 3.0), 0.06, 0.8)
reg("coin_2", x, "coins and money, variant", vol=0.35)

# buy: a happy rising arpeggio with shimmer
x = np.zeros(int(1.8 * SR))
for k, n in enumerate([72, 76, 79, 84]):
    mix_into(x, marimba(midi(n), 1.0, 0.9), 0.085 * k)
mix_into(x, bell_fm(midi(96), 1.2, 3.5, 2.0), 0.34, 0.5)
x = reverb(x, rngf("buy"), 1.2, 0.22, 7000, stereo=False)[0]
reg("buy", x[: int(1.8 * SR)], "purchase done", vol=0.45)

# level up: pentatonic climb with a swell
x = np.zeros(int(2.6 * SR))
for k, n in enumerate([67, 72, 74, 79, 81, 84, 91]):
    mix_into(x, marimba(midi(n), 1.2, 0.9), 0.1 * k)
rng = rngf("level")
swell = pad_voice(midi(72), 2.0, rng) * np.sin(np.linspace(0, np.pi, int(2.0 * SR))) ** 2 * 0.35
mix_into(x, swell, 0.1)
for k in range(6):
    mix_into(x, kalimba(midi(100 + int(rng.integers(0, 5))), 0.6, 0.3), 0.5 + 0.12 * k)
x = reverb(x, rng, 1.8, 0.3, 7000, stereo=False)[0]
reg("level", x[: int(2.6 * SR)], "level up, big win", vol=0.5)

# win: shorter fanfare
x = np.zeros(int(1.6 * SR))
for k, n in enumerate([72, 79, 84]):
    mix_into(x, marimba(midi(n), 1.0, 0.9), 0.11 * k)
mix_into(x, bell_fm(midi(91), 1.2, 3.5, 2.0), 0.33, 0.6)
x = reverb(x, rngf("win"), 1.2, 0.22, 7000, stereo=False)[0]
reg("win", x[: int(1.6 * SR)], "small win", vol=0.45)

# sparkle: tiny high kalimba glints
rng = rngf("sparkle")
x = np.zeros(int(1.0 * SR))
for k in range(5):
    mix_into(x, kalimba(midi(int(rng.choice([96, 98, 100, 103, 105]))), 0.5, 0.7), 0.05 * k + rng.uniform(0, 0.03))
x = reverb(x, rng, 0.9, 0.25, 9000, stereo=False)[0]
reg("sparkle", x[: int(1.0 * SR)], "sparkles, magic", vol=0.3)

# music-note instrument (A4). Sfx.note shifts it with PlaybackSpeed.
reg("note_marimba", marimba(440.0, 1.6, 1.0), "melodic note, pitch shifted in code", vol=0.3)

# whoosh (UI and world)
r = rngf("whoosh")
n = int(0.6 * SR)
sw = swept_bp(noise(0.6, r, "pink"), 280, 1800, 1.3) * np.sin(np.linspace(0, np.pi, n)) ** 2
reg("whoosh", fade(sw, 0.01, 0.05), "soft whoosh", vol=0.45)

# stamp (card slap)
r = rngf("stamp")
d = 0.35
x = sweep(150, 62, d) * exp_env(int(d * SR), 0.07)
x += bp(noise(d, r), 700, 2400) * exp_env(int(d * SR), 0.018) * 0.6
reg("stamp", fade(x, 0.0005, 0.05), "stamp, card slam", vol=0.55)

# heartbeat
d = 0.9
x = np.zeros(int(d * SR))
mix_into(x, sweep(85, 48, 0.18) * exp_env(int(0.18 * SR), 0.06), 0.0, 1.0)
mix_into(x, sweep(70, 42, 0.2) * exp_env(int(0.2 * SR), 0.07), 0.24, 0.8)
reg("heart", lp(x, 220, 2), "tense heartbeat", vol=0.5)

# thunder: low rumble with a gentle crack
r = rngf("thunder")
d = 2.8
n = int(d * SR)
rum = lp(noise(d, r, "brown"), 170, 3) * (1 - np.exp(-np.arange(n) / (0.15 * SR))) * np.exp(-np.arange(n) / (1.1 * SR))
crack = hp(lp(noise(0.25, r), 3200), 400) * exp_env(int(0.25 * SR), 0.05) * 0.35
x = rum
x[: len(crack)] += crack
reg("thunder", fade(x, 0.002, 0.3), "distant thunder", vol=0.55)

# boom: round impact
r = rngf("boom")
d = 0.9
x = sweep(95, 34, d) * exp_env(int(d * SR), 0.2)
x += lp(noise(d, r), 600, 2) * exp_env(int(d * SR), 0.04) * 0.7
reg("boom", fade(x, 0.0005, 0.1), "heavy impact", vol=0.6)

# crash: splintering wood
r = rngf("crash")
d = 1.1
x = np.zeros(int(d * SR))
for k in range(9):
    f = r.uniform(500, 2600)
    b = bp(noise(0.12, r), f, f * 1.6) * exp_env(int(0.12 * SR), 0.03)
    mix_into(x, b, k * 0.035 + r.uniform(0, 0.02), r.uniform(0.3, 0.9))
mix_into(x, sweep(120, 45, 0.5) * exp_env(int(0.5 * SR), 0.12), 0.0, 0.9)
reg("crash", fade(x, 0.001, 0.15), "wood cracking", vol=0.6)

# ------------------------------------------------------------------ movement
def foliage(name):
    r = rngf(name)
    d = 0.45
    n = int(d * SR)
    x = hp(noise(d, r), 1600)
    mod = lp(np.abs(r.standard_normal(n)), 14, 2)
    mod = mod / np.max(mod)
    x *= mod * np.sin(np.linspace(0, np.pi, n)) ** 1.2
    reg(name, fade(lp(x, 9000, 2), 0.01, 0.06), "bush rustle", vol=0.45)


for i in range(3):
    foliage(f"rustle_{i + 1}")


def step(kind, i):
    name = f"step_{kind}_{i + 1}"
    r = rngf(name)
    d = 0.2
    n = int(d * SR)
    if kind == "grass":
        body = lp(noise(d, r), 700, 2) * exp_env(n, 0.03)
        crisp = bp(noise(d, r), 2500 + 400 * i, 7000) * exp_env(n, 0.018) * 0.5
        thump = sweep(120 + 8 * i, 70, d) * exp_env(n, 0.03) * 0.6
        x = body + crisp + thump
    elif kind == "stone":
        tap = bp(noise(d, r), 1200 + 300 * i, 4200) * exp_env(n, 0.012)
        ring = sine(900 + 130 * i, d) * exp_env(n, 0.02) * 0.25
        thump = sweep(150, 80, d) * exp_env(n, 0.028) * 0.5
        x = tap + ring + thump
    else:  # wood
        knock = sine(300 + 40 * i, d) * exp_env(n, 0.035) * 0.8
        tap = bp(noise(d, r), 900, 3000) * exp_env(n, 0.014) * 0.7
        x = knock + tap
    reg(name, fade(x, 0.0005, 0.03), f"footstep on {kind}", vol=0.35)


for kind in ("grass", "stone", "wood"):
    for i in range(4):
        step(kind, i)

# jump / land
r = rngf("jump")
d = 0.22
x = sweep(280, 520, d) * np.sin(np.linspace(0, np.pi, int(d * SR))) * 0.6
x += hp(noise(d, r), 2000) * np.sin(np.linspace(0, np.pi, int(d * SR))) * 0.2
reg("jump", fade(x, 0.005, 0.03), "jump", vol=0.35)
r = rngf("land")
d = 0.3
x = lp(noise(d, r), 600, 2) * exp_env(int(d * SR), 0.05) + sweep(110, 60, d) * exp_env(int(d * SR), 0.06) * 0.7
x += bp(noise(d, r), 2500, 6500) * exp_env(int(d * SR), 0.02) * 0.3
reg("land", fade(x, 0.0005, 0.05), "landing", vol=0.4)

# ------------------------------------------------------------------ spear
# charge: a bowed wooden shaft that tenses while you hold the throw (seamless loop, 1.5 s)
r = rngf("charge")
d = 1.5
xfl = 0.3
t = t_axis(d + xfl)
vib = 1 + 0.012 * np.sin(2 * np.pi * 4 * t)
f0 = 150.0
x = np.zeros(len(t))
for h, a in [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15)]:
    x += a * np.sin(2 * np.pi * np.cumsum(f0 * h * vib) / SR)
x = lp(x, 1400, 2) * (0.7 + 0.3 * np.sin(2 * np.pi * (1 / d) * 2 * t))
x += lp(noise(d + xfl, r), 900, 2) * 0.12
n_ = int(d * SR)
xf = int(xfl * SR)
loop = x[:n_].copy()
loop[:xf] = loop[:xf] * np.linspace(0, 1, xf) + x[n_:n_ + xf] * np.linspace(1, 0, xf)
x = loop
reg("spear_charge", x, "holding the throw, tension (loop)", vol=0.25, loop=True)

# throw: string snap + whoosh body
r = rngf("throw")
d = 0.9
n = int(d * SR)
env = np.sin(np.linspace(0, np.pi, int(0.55 * SR))) ** 2
w = swept_bp(noise(0.55, r, "pink"), 260, 2200, 1.4) * env
body = sweep(140, 70, 0.4) * exp_env(int(0.4 * SR), 0.1) * 0.6
x = np.zeros(n)
mix_into(x, w, 0.02, 1.0)
mix_into(x, body, 0.0, 0.8)
mix_into(x, kalimba(midi(55), 0.5, 0.5), 0.0, 0.6)
reg("spear_throw", fade(x, 0.001, 0.06), "spear leaves the hand", vol=0.55)

# flight: airy whistle, seamless loop 1.0 s
r = rngf("fly")
d = 1.0
n = int(d * SR)
src = noise(d + 0.3, r, "pink")
a = resonator(src, 1700, 6) * 0.9 + resonator(src, 2500, 8) * 0.5
a = a[: n + int(0.3 * SR)]
a = a / (np.max(np.abs(a)) + 1e-9)
xf = int(0.3 * SR)
loop = a[:n].copy()
loop[:xf] = loop[:xf] * np.linspace(0, 1, xf) + a[n:n + xf] * np.linspace(1, 0, xf)
reg("spear_fly", loop, "spear in flight (loop)", vol=0.25, loop=True)

# hit variants: ground, wood, soft (animal)
def hit(kind, i):
    name = f"spear_hit_{kind}_{i + 1}"
    r = rngf(name)
    d = 0.6
    n = int(d * SR)
    if kind == "ground":
        x = sweep(130 + 10 * i, 55, d) * exp_env(n, 0.09)
        x += lp(noise(d, r), 900, 2) * exp_env(n, 0.05) * 0.8
        x += bp(noise(d, r), 1500, 5000) * exp_env(n, 0.015) * 0.35
    elif kind == "wood":
        x = sine(380 + 45 * i, d) * exp_env(n, 0.08) + 0.5 * sine(380 * 2.4 + 40 * i, d) * exp_env(n, 0.03)
        x += bp(noise(d, r), 800, 3200) * exp_env(n, 0.02) * 0.6
    else:  # soft: satisfying thud plus a bright reward ping
        x = sweep(190, 80, d) * exp_env(n, 0.07)
        x += lp(noise(d, r), 700, 2) * exp_env(n, 0.04) * 0.6
        ping = marimba(midi(79 + 2 * i), 0.5, 0.7)
        x = fit(x, d)
        mix_into(x, ping, 0.04, 0.55)
    reg(name, fade(x, 0.0005, 0.08), f"spear hits {kind}", vol=0.55)


for kind in ("ground", "wood", "soft"):
    for i in range(3):
        hit(kind, i)

# miss: soft thwip
r = rngf("miss")
d = 0.45
n = int(d * SR)
x = swept_bp(noise(d, r, "pink"), 2400, 500, 1.6) * exp_env(n, 0.12)
reg("spear_miss", fade(x, 0.001, 0.05), "throw misses", vol=0.4)

# ------------------------------------------------------------------ training, pickups, dialog
def rep(i):
    name = f"train_rep_{i + 1}"
    r = rngf(name)
    d = 0.5
    x = np.zeros(int(d * SR))
    mix_into(x, bell_fm(520 + 40 * i, 0.3, 2.3, 4.0, 0.7), 0.0, 0.8)
    mix_into(x, bell_fm(640 + 45 * i, 0.3, 2.3, 4.0, 0.7), 0.09, 0.6)
    mix_into(x, lp(noise(0.3, r), 1200, 2) * np.sin(np.linspace(0, np.pi, int(0.3 * SR))) * 0.25, 0.1)
    mix_into(x, sweep(130, 70, 0.2) * exp_env(int(0.2 * SR), 0.06), 0.0, 0.5)
    reg(name, fade(x, 0.0005, 0.06), "one training rep", vol=0.45)


for i in range(3):
    rep(i)

x = fit(marimba(midi(76), 0.6, 0.9), 0.6)
mix_into(x, marimba(midi(83), 0.5, 0.9), 0.07)
reg("pickup", x, "pick something up", vol=0.4)

for i, n in enumerate([72, 76, 79, 83]):
    reg(f"dialog_blip_{i + 1}", marimba(midi(n), 0.16, 0.8, 0.4), "dialog text blip", vol=0.18)

# soft footfalls of coins when flying to the counter
rng = rngf("coinfly")
x = np.zeros(int(0.9 * SR))
for k in range(7):
    mix_into(x, bell_fm(float(rng.choice([2093, 2349, 2637, 3136])), 0.25, 3.5, 2.0, 0.6), 0.1 * k + rng.uniform(0, 0.03), 0.6)
reg("coin_burst", x, "a handful of coins", vol=0.3)

if __name__ == "__main__":
    for k, v in SOUNDS.items():
        print(f"{k:22s} {len(v['data']) / SR:5.2f}s  rms {rms_db(v['data']):6.1f} dB")
