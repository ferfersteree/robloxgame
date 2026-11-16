"""Sound effects for the egg opening (V39). Each recipe returns a float array (mono, or stereo shape (2, n)).
Registered by name = the AudioIds key = the file name without .ogg."""
import numpy as np
from scipy import signal

from foley import *  # noqa: F401,F403

SOUNDS = {}


def reg(name, kind="hit", loop=False, stereo=False, use=""):
    def deco(fn):
        SOUNDS[name] = dict(fn=fn, kind=kind, loop=loop, stereo=stereo, use=use)
        return fn
    return deco


def nrm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def notes(*midis):
    return [midi(m) for m in midis]


PENTA_HI = notes(84, 86, 88, 91, 93, 96, 98, 100, 103)      # C6 D6 E6 G6 A6 C7 D7 E7 G7
PENTA_MID = notes(72, 74, 76, 79, 81, 84, 86, 88)           # C5 .. E6
WARM = notes(69, 72, 74, 76, 81, 84, 88)                    # A4 C5 D5 E5 A5 C6 E6


# ================================================================== scene-wide
@reg("egg_appear", use="the egg materialises in the dark room (t = 0)")
def _egg_appear(rng):
    parts = []
    for i, f in enumerate(notes(72, 76, 79, 84, 88, 91)):
        g = modal(rng, f, GLOCK, 0.7, tau_scale=0.5)
        parts.append((nrm(g), 0.05 + i * 0.055 + rng.uniform(-0.006, 0.006), 0.30 + 0.07 * i))
    parts.append((nrm(whoosh(rng, 0.7, 2500, 11000, q=1.2, peak=0.62, width=0.28, floor=0.0, color="white")), 0.0, 0.35))
    parts.append((nrm(thump(180, 70, 0.18, 0.05, 1.2)), 0.0, 0.5))
    return reverb(stack(parts, 1.3), rng, 1.3, 0.3)


def _knock(rng, f0):
    body = nrm(modal(rng, f0, WOOD, 0.3, tau_scale=1.6))
    hollow = nrm(thump(f0 * 0.55, f0 * 0.38, 0.28, 0.07, 1.4))
    tick = nrm(transient(rng, 900, 4200, 0.0025, dur=0.03))
    x = stack([(body, 0, 0.8), (hollow, 0, 1.0), (tick, 0, 0.55)], 0.32)
    x = lowpass(x, 5200, 2)  # muffled: the knock comes from inside the egg
    return reverb(x, rng, 0.35, 0.28)


@reg("egg_knock_1", use="heartbeat knock from inside the egg, accelerates before the opening (pitch rises in code)")
def _knock1(rng):
    return _knock(rng, 205)


@reg("egg_knock_2", use="heartbeat knock, second variant")
def _knock2(rng):
    return _knock(rng, 188)


def _riser(rng, dur, tone, noise, tone_gain, noise_gain):
    n = N(dur)
    u = np.linspace(0, 1, n)
    swell = u ** 2.2
    t_ = glide_sine(tone[0], tone[1], dur, harmonics=[(2, .35), (3, .18)]) * swell
    nz = whoosh(rng, dur, noise[0], noise[1], q=1.4, peak=1.0, width=0.5, floor=0.0) * swell
    return nrm(t_) * tone_gain + nrm(nz) * noise_gain


def _finish_riser(x, rng, dur, width=0.75):
    n = len(x)
    cut = N(0.07)
    x[-cut:] *= np.linspace(1, 0, cut)  # breath-in before the opening
    return to_stereo(reverb(x, rng, 1.1, 0.2)[:n], rng, width)


@reg("egg_riser_forest", kind="sustain", stereo=True, use="prep of the forest egg: rustle and wood tension, climax at t = prep")
def _riser_forest(rng):
    dur = 2.5
    x = _riser(rng, dur, (110, 330), (500, 5200), 0.35, 0.5)
    # leaf rustle bursts that grow
    n = N(dur)
    leaf = np.zeros(n)
    for te in np.sort(rng.uniform(0.2, dur - 0.1, 46) ** 1.15 / dur ** 0.15):
        b = bandpass(white(rng, N(0.08)), 1500, 6500, 2) * env_bell(N(0.08), 0.3, 0.25)
        place(leaf, b, te, 0.3 + 0.9 * te / dur)
    x = x + nrm(leaf) * 0.28
    drone = string_pad(rng, 110, dur, attack=1.4, release=0.1, voices=3, bright=0.2)
    x = x + nrm(drone) * 0.3 * np.linspace(0.1, 1, n) ** 1.5
    return _finish_riser(x, rng, dur)


@reg("egg_riser_amber", kind="sustain", stereo=True, use="prep of the amber egg: warm brass swell and gong shimmer")
def _riser_amber(rng):
    dur = 2.7
    n = N(dur)
    x = _riser(rng, dur, (150, 440), (700, 7000), 0.2, 0.3)
    for f in (220, 330, 440):
        x = x + nrm(brass_swell(rng, f, dur, attack=dur * 0.9, release=0.05)) * 0.35
    gong = nrm(modal(rng, 196, BELL, dur, tau_scale=1.4)) * np.linspace(0.2, 1, n) ** 2
    x = x + gong * 0.25
    return _finish_riser(x, rng, dur)


@reg("egg_riser_tide", kind="sustain", stereo=True, use="prep of the tide egg: bubbles speed up, water rush")
def _riser_tide(rng):
    dur = 2.7
    n = N(dur)
    x = np.zeros(n)
    te = 0.05
    while te < dur - 0.05:
        u = te / dur
        f0 = rng.uniform(450, 1500) * (1 + 1.4 * u)
        place(x, bubble(rng, f0, tau=rng.uniform(0.012, 0.04), xi=0.14), te, 0.4 + 0.8 * u)
        te += rng.exponential(1.0 / (7 + 60 * u ** 1.6))
    rush = nrm(swept_bandpass(pink(rng, n), 350, 3600, 1.1)) * np.linspace(0.1, 1, n) ** 2
    x = nrm(x) * 0.55 + rush * 0.5 + nrm(glide_sine(140, 520, dur)) * 0.18 * np.linspace(0, 1, n) ** 2
    return _finish_riser(x, rng, dur)


@reg("egg_riser_storm", kind="sustain", stereo=True, use="prep of the storm egg: electric build-up, rumble")
def _riser_storm(rng):
    dur = 2.8
    n = N(dur)
    cr = crackle(rng, dur, lambda t: 3 * np.exp(t / dur * np.log(26)), 1800, 9500, 0.0004, 0.002)
    whine = glide_sine(170, 1150, dur, harmonics=[(2, .5), (3, .33), (5, .2)])
    whine = np.tanh(whine * 1.6) * np.linspace(0, 1, n) ** 2.6
    rumble = nrm(lowpass(brown(rng, n), 180, 2)) * np.linspace(0.05, 1, n) ** 1.6
    hiss = nrm(highpass(white(rng, n), 5000, 2)) * np.linspace(0, 1, n) ** 3
    x = nrm(cr) * 0.55 + nrm(whine) * 0.25 + rumble * 0.45 + hiss * 0.2
    return _finish_riser(x, rng, dur)


@reg("egg_riser_astral", kind="sustain", stereo=True, use="prep of the astral egg: shimmering glissando, choir swell")
def _riser_astral(rng):
    dur = 3.0
    n = N(dur)
    cloud = sparkle_cloud(rng, dur, 4, PENTA_HI, CELESTA, 1.1, decay_rate=None)
    cloud = nrm(cloud[:n]) * np.linspace(0.1, 1, n) ** 1.6
    ch = np.zeros(n)
    for f in notes(57, 64, 69):
        ch += nrm(choir(rng, f, dur, "a", voices=4, attack=dur * 0.85, release=0.05))
    x = _riser(rng, dur, (220, 880), (900, 10500), 0.2, 0.3) + cloud * 0.5 + nrm(ch) * 0.35 * np.linspace(0.1, 1, n) ** 1.5
    return _finish_riser(x, rng, dur, 0.9)


# ================================================================== opening
def _open_crack(rng, big):
    main = nrm(transient(rng, 1200, 9000, 0.0035, dur=0.05))
    ping = nrm(modal(rng, rng.uniform(2200, 2800), CERAMIC, 0.25, tau_scale=1.2))
    casc = nrm(crackle(rng, 0.42, lambda t: 70 * np.exp(-t / 0.14) + 8, 1800, 7500, 0.0007, 0.004))
    pop = nrm(thump(210, 85, 0.22, 0.05, 1.5))
    scrape = nrm(bandpass(pink(rng, N(0.25)), 600, 3200, 2) * env_bell(N(0.25), 0.25, 0.18))
    x = stack([(main, 0, 1.0), (ping, 0, 0.6), (casc, 0.015, 0.5 * big), (pop, 0, 0.8), (scrape, 0.08, 0.14)], 0.6)
    return reverb(x, rng, 0.55, 0.16)


@reg("egg_crack_1", use="the shell cracks open at t = prep")
def _crack1(rng):
    return _open_crack(rng, 1.0)


@reg("egg_crack_2", use="the shell cracks open, variant with a longer cascade")
def _crack2(rng):
    return _open_crack(rng, 1.35)


def _boom(rng, size):
    d = [0.9, 1.3, 1.9][size]
    body = nrm(thump([130, 110, 95][size], [48, 40, 32][size], d, [0.22, 0.35, 0.6][size], 1.8))
    punch = nrm(lowpass(white(rng, N(0.25)), [900, 700, 520][size], 2) * env_exp(N(0.25), [0.06, 0.09, 0.14][size]))
    air = nrm(highpass(white(rng, N(0.12)), 2500, 2) * env_exp(N(0.12), 0.02))
    parts = [(body, 0, 1.0), (punch, 0, 0.7), (air, 0, 0.25)]
    if size == 2:
        parts.append((nrm(lowpass(brown(rng, N(1.6)), 140, 2)) * env_exp(N(1.6), 0.7), 0.05, 0.6))
    return reverb(stack(parts, d), rng, [0.7, 1.1, 1.7][size], [0.18, 0.22, 0.3][size])


for _i, _n in enumerate(["s", "m", "l"]):
    reg(f"egg_boom_{_n}", use=f"impact of the opening, size {_n} (small for low rarities, large for high)")(
        (lambda i: (lambda rng: _boom(rng, i)))(_i))


def _burst(rng, size):
    d = [1.0, 1.7, 2.6][size]
    wh = nrm(whoosh(rng, 0.45, 1500, 10000, q=1.3, peak=0.35, width=0.2, floor=0.0, color="white"))
    cloud = nrm(sparkle_cloud(rng, d, [40, 70, 110][size], PENTA_HI, GLOCK, [0.5, 0.7, 0.9][size], decay_rate=d * 0.5))
    pf = nrm(highpass(white(rng, N(0.1)), 3500, 2) * env_exp(N(0.1), 0.018))
    parts = [(wh, 0, 0.6), (cloud, 0.02, 0.9), (pf, 0, 0.3)]
    if size >= 1:
        parts.append((nrm(modal(rng, 523.25, BELL, d, tau_scale=0.6)), 0.03, 0.35))
    return reverb(stack(parts, d + 0.5), rng, [1.4, 1.8, 2.4][size], 0.3)


for _i, _n in enumerate(["s", "m", "l"]):
    reg(f"egg_burst_{_n}", use=f"magic burst when the shell opens, size {_n}")(
        (lambda i: (lambda rng: _burst(rng, i)))(_i))


@reg("egg_thunder", use="thunder for high rarities at the opening (and the storm egg)")
def _thunder(rng):
    return _thunder_core(rng, 2.8, 1.0)


def _thunder_core(rng, dur, crack):
    n = N(dur)
    t = tt(n)
    cr = nrm(transient(rng, 400, 9000, 0.012, dur=0.15))
    roll = 0.55 + 0.45 * np.sin(2 * np.pi * (1.3 + 0.6 * rng.random()) * t + rng.uniform(0, 6.28))
    rum = nrm(bandpass(brown(rng, n), 35, 260, 2) * np.exp(-t / 1.1) * roll)
    mid = nrm(bandpass(white(rng, n), 120, 900, 2) * np.exp(-t / 0.5))
    x = stack([(cr, 0, crack), (rum, 0.02, 0.9), (mid, 0.03, 0.4)], dur)
    return reverb(x, rng, 2.0, 0.3)


@reg("egg_divine", use="the biggest hit: top rarity opening (sub drop, choir, cymbal, bells)")
def _divine(rng):
    dur = 3.6
    sub = nrm(sub_drop(95, 26, 2.4, 0.9))
    ch = np.zeros(N(2.8))
    for f in notes(48, 55, 60, 64, 67):
        ch += choir(rng, f, 2.8, "a", voices=5, attack=0.25, release=1.2)
    cym = nrm(cymbal(rng, 3.0, swell=0.15))
    bells = nrm(sparkle_cloud(rng, 2.4, 55, PENTA_HI, BELL, 0.45, decay_rate=1.2))
    x = stack([(sub, 0, 1.0), (nrm(ch), 0.02, 0.7), (cym, 0, 0.4), (bells, 0.1, 0.5),
               (nrm(transient(rng, 300, 8000, 0.02, dur=0.2)), 0, 0.6)], dur)
    return reverb(x, rng, 2.8, 0.32)


# ================================================================== forest egg
def _snap(rng, f0):
    tr = nrm(transient(rng, 1500, 8000, 0.0025, dur=0.04))
    body = nrm(modal(rng, f0, WOOD, 0.25, tau_scale=1.0))
    spl = nrm(crackle(rng, 0.2, lambda t: 220 * np.exp(-t / 0.05) + 5, 1500, 6000, 0.0005, 0.0025))
    tear = nrm(bandpass(white(rng, N(0.12)), 2500, 7500, 2) * env_bell(N(0.12), 0.35, 0.2))
    x = stack([(tr, 0, 1.0), (body, 0, 0.7), (spl, 0.004, 0.4), (tear, 0.01, 0.3)], 0.3)
    return reverb(x, rng, 0.4, 0.15)


@reg("forest_snap_1", use="forest egg: a belt segment splinters (8 in a row, pitch rises in code)")
def _fsnap1(rng):
    return _snap(rng, 560)


@reg("forest_snap_2", use="forest egg: belt segment splinters, second variant")
def _fsnap2(rng):
    return _snap(rng, 690)


@reg("forest_leaves", use="forest egg: burst of leaf cubes and soft sparks")
def _leaves(rng):
    n = N(1.15)
    mod = np.abs(signal.lfilter([1], [1, -0.985], rng.standard_normal(n)))
    mod /= np.max(mod)
    rustle = nrm(highpass(white(rng, n), 2200, 2) * mod * env_bell(n, 0.22, 0.25, 0.0))
    wh = nrm(whoosh(rng, 0.9, 600, 5200, q=1.1, peak=0.3, width=0.25, floor=0.0))
    spark = nrm(sparkle_cloud(rng, 0.8, 26, notes(88, 91, 93, 96, 100), GLOCK, 0.5, decay_rate=0.4))
    x = stack([(rustle, 0, 0.8), (wh, 0, 0.45), (spark, 0.05, 0.5)], 1.3)
    return reverb(x, rng, 0.7, 0.2)


@reg("forest_shimmer", kind="loop", loop=True, use="forest egg: soft rising sparkles while sparks rise around the egg (loop)")
def _fshim(rng):
    dur = 3.0
    n = N(dur)
    cl = sparkle_cloud(rng, dur, 8, notes(76, 79, 81, 84, 88, 91, 93), CELESTA, 0.7, wrap=True)
    air = nrm(bandpass(pink(rng, n), 4000, 9000, 2)) * (0.6 + 0.4 * np.sin(2 * np.pi * np.arange(n) / n))
    x = nrm(cl) * 0.8 + air * 0.08
    return reverb(x, rng, 0.9, 0.3, circular=True)


# ================================================================== amber egg
@reg("amber_note", use="amber egg: a segment of the sun lights up (6 notes, pitch steps up the scale in code)")
def _amber_note(rng):
    f = 523.25
    a = modal(rng, f, MARIMBA, 1.3, tau_scale=1.0)
    b = modal(rng, f, GLOCK, 1.0, tau_scale=0.7)
    clk = nrm(transient(rng, 1800, 6000, 0.002, dur=0.02))
    x = stack([(a, 0, 0.9), (b, 0, 0.35), (clk, 0, 0.25)], 1.3)
    return reverb(x, rng, 1.2, 0.25)


@reg("amber_inflow", kind="loop", loop=True, use="amber egg: sparks fly toward the egg (loop)")
def _amber_inflow(rng):
    dur = 3.0
    n = N(dur)
    cl = nrm(sparkle_cloud(rng, dur, 12, WARM, MARIMBA, 0.8, wrap=True))
    ch = np.zeros(n)
    for te in rng.uniform(0, dur, 9):
        g = glide_sine(900, 2400, 0.14) * env_bell(N(0.14), 0.5, 0.3)
        place(ch, g, te, rng.uniform(0.3, 0.8), wrap=True)
    bed = nrm(lowpass(pink(rng, n), 900, 2)) * 0.5
    x = cl * 0.7 + nrm(ch) * 0.25 + bed * 0.12
    return reverb(x, rng, 1.0, 0.3, circular=True)


@reg("amber_sun", use="amber egg: the sun ring swells (warm gong and pad)")
def _amber_sun(rng):
    dur = 1.8
    g = nrm(modal(rng, 220, BELL, dur, tau_scale=0.8))
    na = N(0.12)
    g[:na] *= np.linspace(0, 1, na)
    pad = nrm(string_pad(rng, 220, dur, attack=0.35, release=0.8, voices=3, bright=0.3))
    x = g * 0.8 + pad * 0.4
    return reverb(x, rng, 1.8, 0.3)


def _shard(rng, f0):
    m = nrm(modal(rng, f0, GLASS, 0.5, tau_scale=0.9))
    tr = nrm(transient(rng, 3000, 10000, 0.0012, dur=0.02))
    m2 = nrm(modal(rng, f0 * 1.34, GLASS, 0.35, tau_scale=0.6))
    x = stack([(m, 0, 0.9), (tr, 0, 0.5), (m2, 0.035, 0.35)], 0.55)
    return reverb(x, rng, 0.6, 0.18)


@reg("amber_shard_1", use="amber egg: an amber shard flies off a segment (6 in a row)")
def _ashard1(rng):
    return _shard(rng, 2100)


@reg("amber_shard_2", use="amber egg: amber shard, second variant")
def _ashard2(rng):
    return _shard(rng, 2550)


# ================================================================== tide egg
@reg("tide_bubbles", kind="loop", loop=True, use="tide egg: bubbles rise around the egg (loop)")
def _tide_bubbles(rng):
    dur = 3.0
    n = N(dur)
    x = np.zeros(n)
    te = 0.0
    while te < dur:
        place(x, bubble(rng, float(np.exp(rng.uniform(np.log(500), np.log(2600)))), rng.uniform(0.012, 0.045), 0.12),
              te, rng.uniform(0.3, 1.0), wrap=True)
        te += rng.exponential(1 / 22)
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * np.arange(n) / n * 2)
    bed = nrm(bandpass(pink(rng, n), 250, 1400, 2)) * mod
    x = nrm(x) * 0.8 + bed * 0.14
    return reverb(x, rng, 0.5, 0.15, circular=True)


@reg("tide_splash", use="tide egg: the splash when the shell opens (rings and droplets)")
def _splash(rng):
    dur = 1.5
    n = N(dur)
    imp = nrm(bandpass(white(rng, n), 300, 6000, 2) * env_exp(n, 0.18, 0.001))
    cloud = np.zeros(n)
    for _ in range(130):
        te = rng.exponential(0.28)
        if te > 1.1:
            continue
        f0 = float(np.exp(rng.uniform(np.log(600), np.log(3800)))) * (1.3 - 0.5 * te)
        place(cloud, bubble(rng, f0, rng.uniform(0.01, 0.035), 0.13), te, rng.uniform(0.2, 1.0))
    bloop = nrm(thump(140, 70, 0.25, 0.08, 1.2))
    drops = np.zeros(n)
    for te in rng.uniform(0.15, 1.3, 14):
        place(drops, bubble(rng, rng.uniform(3000, 6500), 0.006, 0.1), te, rng.uniform(0.2, 0.6))
    x = stack([(imp, 0, 0.8), (nrm(cloud), 0.01, 0.9), (bloop, 0, 0.7), (nrm(drops), 0, 0.35)], dur)
    return reverb(x, rng, 0.7, 0.15)


def _pop(rng, f0):
    b = nrm(bubble(rng, f0, 0.012, 0.18, 0.12))
    tk = nrm(transient(rng, 2500, 8000, 0.0015, dur=0.015))
    sh = nrm(modal(rng, f0 * 2.4, GLASS, 0.2, tau_scale=0.3))
    return reverb(stack([(b, 0, 1.0), (tk, 0, 0.35), (sh, 0.004, 0.18)], 0.35), rng, 0.4, 0.15)


@reg("tide_pop_1", use="tide egg: a pearl row bursts into bubbles (4 pops, pitch rises in code)")
def _tpop1(rng):
    return _pop(rng, 1350)


@reg("tide_pop_2", use="tide egg: bubble pop, second variant")
def _tpop2(rng):
    return _pop(rng, 1750)


@reg("tide_ring", use="tide egg: water ring pulse")
def _tide_ring(rng):
    dur = 1.0
    n = N(dur)
    b = bubble(rng, 380, 0.09, 0.35, dur)
    rip = np.sin(2 * np.pi * 11 * tt(n)) * 0.5 + 0.5
    b = b * (0.55 + 0.45 * rip) * np.exp(-tt(n) / 0.4)
    hi = np.zeros(n)
    for te in rng.uniform(0.0, 0.5, 6):
        place(hi, bubble(rng, rng.uniform(1800, 3400), 0.012, 0.15), te, 0.3)
    return reverb(stack([(nrm(b), 0, 1.0), (nrm(hi), 0.02, 0.25)], dur), rng, 0.8, 0.2)


# ================================================================== storm egg
@reg("storm_crackle", kind="sustain", use="storm egg: sparks along the seam, accelerating (one long rising crackle)")
def _storm_crackle(rng):
    dur = 3.3
    n = N(dur)
    cr = nrm(crackle(rng, dur, lambda t: 3 * np.exp(t / dur * np.log(30)), 1800, 9500, 0.0004, 0.002))
    hiss = nrm(highpass(white(rng, n), 5500, 2)) * np.linspace(0, 1, n) ** 3
    buzz = nrm(np.sin(2 * np.pi * 100 * tt(n)) + 0.5 * np.sin(2 * np.pi * 200 * tt(n))) * np.linspace(0, 1, n) ** 2
    return reverb(cr * 0.8 + hiss * 0.2 + buzz * 0.12, rng, 0.5, 0.12)


def _zap(rng, k):
    n = N(0.45)
    tr = nrm(transient(rng, 2000, 9000, 0.008, dur=0.06))
    sweep = nrm(np.tanh(2.0 * glide_sine(6000 * k, 300 * k, 0.2, harmonics=[(2, .4), (3, .25)])) * env_exp(N(0.2), 0.07))
    tail = nrm(crackle(rng, 0.3, lambda t: 140 * np.exp(-t / 0.09) + 4, 1800, 8000, 0.0005, 0.002))
    x = stack([(tr, 0, 1.0), (sweep, 0, 0.7), (tail, 0.02, 0.5)], 0.45)
    return reverb(x, rng, 0.45, 0.14)


@reg("storm_zap_1", use="storm egg: a bolt across the seam / from the centre")
def _zap1(rng):
    return _zap(rng, 1.0)


@reg("storm_zap_2", use="storm egg: bolt, second variant")
def _zap2(rng):
    return _zap(rng, 0.78)


@reg("storm_clamp", use="storm egg: a steel clamp releases (6 in a row)")
def _clamp(rng):
    f0 = 780
    m = nrm(modal(rng, f0, STEEL, 0.55, tau_scale=0.9))
    clk = nrm(transient(rng, 2000, 8000, 0.0015, dur=0.02))
    thk = nrm(thump(160, 90, 0.15, 0.04, 1.4))
    tail = nrm(crackle(rng, 0.18, lambda t: 90 * np.exp(-t / 0.06) + 3, 2200, 8000, 0.0005, 0.002))
    x = stack([(m, 0, 0.85), (clk, 0, 0.8), (thk, 0, 0.7), (tail, 0.01, 0.3)], 0.55)
    return reverb(x, rng, 0.5, 0.15)


@reg("storm_thunder", use="storm egg: the thunder flash at the opening (sharper crack, long rumble)")
def _storm_thunder(rng):
    return _thunder_core(rng, 3.0, 1.35)


@reg("storm_arcs", kind="loop", loop=True, use="storm egg: arcs between the separated armour segments (loop)")
def _storm_arcs(rng):
    dur = 3.0
    n = N(dur)
    x = np.zeros(n)
    te = 0.0
    while te < dur:
        d = rng.uniform(0.05, 0.13)
        f = rng.uniform(110, 230)
        kmax = int(min(24, 0.4 * SR / f))
        buz = harmonic_stack(f, d, [(k, 1.0 / k) for k in range(1, kmax + 1)], rng=rng)
        buz = bandpass(buz, 700, 6500, 2) * env_bell(len(buz), 0.3, 0.3)
        cr = crackle(rng, d, lambda t: 260, 1800, 8500, 0.0004, 0.0018)
        place(x, nrm(buz) * 0.6 + nrm(cr) * 0.5, te, rng.uniform(0.4, 1.0), wrap=True)
        te += rng.exponential(1 / 2.6)
    hiss = nrm(highpass(pink(rng, n), 4500, 2)) * 0.03
    return reverb(nrm(x) * 0.9 + hiss, rng, 0.5, 0.12, circular=True)


# ================================================================== astral egg
@reg("astral_twinkle", kind="loop", loop=True, use="astral egg: stars twinkle around the egg (loop)")
def _astral_twinkle(rng):
    dur = 3.0
    n = N(dur)
    cl = nrm(sparkle_cloud(rng, dur, 7, notes(88, 91, 93, 96, 100, 103, 105), CELESTA, 1.0, wrap=True))
    t = tt(n)
    drone = np.sin(2 * np.pi * 110 * t) * 0.6 + np.sin(2 * np.pi * 165 * t) * 0.35
    drone = drone * (0.75 + 0.25 * np.sin(2 * np.pi * t / dur))
    x = cl * 0.85 + nrm(drone) * 0.12
    return reverb(x, rng, 2.0, 0.35, circular=True)


@reg("astral_ring", use="astral egg: the rings align (resonant chord of bells, sub hum)")
def _astral_ring(rng):
    dur = 2.0
    n = N(dur)
    x = np.zeros(n)
    for f in notes(69, 76, 81, 85):
        x += nrm(modal(rng, f, BELL, dur, tau_scale=0.8))
    na = N(0.3)
    x[:na] *= np.linspace(0, 1, na) ** 1.5
    sub = np.sin(2 * np.pi * 110 * tt(n)) * np.linspace(0, 1, n) ** 1.5 * np.exp(-tt(n) / 1.2)
    x = nrm(x) * 0.8 + nrm(sub) * 0.3
    return reverb(x, rng, 2.2, 0.35)


@reg("astral_burst", use="astral egg: stars fly to all sides (whoosh, dense sparkle, soft choir)")
def _astral_burst(rng):
    dur = 2.6
    wh = nrm(whoosh(rng, 0.8, 800, 10000, q=1.2, peak=0.35, width=0.22, floor=0.0, color="white"))
    cl = nrm(sparkle_cloud(rng, dur, 90, PENTA_HI, CELESTA, 0.8, decay_rate=0.9))
    ch = np.zeros(N(2.2))
    for f in notes(57, 64, 69, 73):
        ch += choir(rng, f, 2.2, "a", voices=4, attack=0.25, release=1.0)
    x = stack([(wh, 0, 0.6), (cl, 0.02, 0.9), (nrm(ch), 0.05, 0.4)], dur + 0.4)
    return reverb(x, rng, 2.4, 0.35)


@reg("astral_split", use="astral egg: the shell separates (resonant sweep, glass crack, shimmer)")
def _astral_split(rng):
    dur = 1.8
    sw = nrm(glide_sine(80, 420, 0.9, harmonics=[(2, .5), (3, .3)])) * env_bell(N(0.9), 0.6, 0.3)
    gl = nrm(modal(rng, 1250, GLASS, 0.8, tau_scale=1.0))
    tr = nrm(transient(rng, 1500, 9000, 0.004, dur=0.05))
    sh = nrm(sparkle_cloud(rng, 1.2, 30, PENTA_HI, CELESTA, 0.7, decay_rate=0.6))
    x = stack([(sw, 0, 0.6), (gl, 0.05, 0.6), (tr, 0.05, 0.6), (sh, 0.1, 0.5)], dur)
    return reverb(x, rng, 1.8, 0.3)


# ================================================================== generic events
@reg("egg_flash", use="light flash from inside the egg: a rising airy shine and a bright ping")
def _egg_flash(rng):
    sw = nrm(whoosh(rng, 0.7, 2000, 12000, q=1.1, peak=0.55, width=0.25, floor=0.0, color="white"))
    ping = nrm(modal(rng, 2637, GLOCK, 0.8, tau_scale=0.7))
    pad = nrm(string_pad(rng, 330, 0.9, attack=0.3, release=0.4, voices=3, bright=0.6))
    return reverb(stack([(sw, 0, 0.6), (ping, 0.28, 0.5), (pad, 0, 0.25)], 1.0), rng, 1.2, 0.3)


def _ring(rng, dur, f0, f1):
    n = N(dur)
    sw = nrm(glide_sine(f0, f1, dur) * env_bell(n, 0.25, 0.3, 0.0))
    nz = nrm(whoosh(rng, dur, 3000, 700, q=1.0, peak=0.3, width=0.25, floor=0.0))
    bell = nrm(modal(rng, 880, GLOCK, dur, tau_scale=0.5))
    return reverb(stack([(sw, 0, 0.6), (nz, 0, 0.35), (bell, 0.02, 0.3)], dur), rng, 0.9, 0.22)


@reg("egg_ring_s", use="shock ring on the floor, small")
def _ring_s(rng):
    return _ring(rng, 0.6, 700, 260)


@reg("egg_ring_l", use="shock ring on the floor, large")
def _ring_l(rng):
    return _ring(rng, 1.1, 520, 150)


# ================================================================== the animal
@reg("pet_emerge", use="the animal pops out of the shell: spring boing, upward whoosh, sparkle")
def _pet_emerge(rng):
    dur = 1.0
    n = N(dur)
    t = tt(n)
    f = 220 * (1 + 2.2 * (1 - np.exp(-t / 0.09)))
    boing = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.025 * np.sin(2 * np.pi * 24 * t))) / SR) * np.exp(-t / 0.22)
    wh = nrm(whoosh(rng, 0.7, 400, 5200, q=1.4, peak=0.3, width=0.22, floor=0.0))
    sp = nrm(sparkle_cloud(rng, 0.6, 40, PENTA_HI, GLOCK, 0.5, decay_rate=0.3))
    pop = nrm(thump(260, 110, 0.14, 0.04, 1.3))
    return reverb(stack([(nrm(boing), 0, 0.7), (wh, 0, 0.55), (sp, 0.04, 0.55), (pop, 0, 0.6)], 1.2), rng, 0.9, 0.22)


@reg("pet_trail", kind="loop", loop=True, use="sparkle trail while the animal is in the air (loop)")
def _pet_trail(rng):
    dur = 2.4
    n = N(dur)
    cl = nrm(sparkle_cloud(rng, dur, 16, PENTA_HI, GLOCK, 0.45, wrap=True))
    t = tt(n)
    swirl = nrm(swept_bandpass(pink(rng, n), 2200, 6000, 2.2, curve=0.5 + 0.5 * np.sin(np.linspace(0, 2 * np.pi * 2, 64))))
    x = cl * 0.8 + swirl * 0.2
    return reverb(x, rng, 0.8, 0.25, circular=True)


def _land(rng, size):
    d = [0.7, 1.1, 1.6][size]
    th = nrm(thump([100, 95, 85][size], [58, 50, 42][size], d, [0.1, 0.14, 0.2][size], 1.4))
    pf = nrm(bandpass(white(rng, N(0.2)), 200, 1500, 2) * env_exp(N(0.2), 0.07))
    sp = nrm(sparkle_cloud(rng, d * 0.8, [18, 40, 80][size], PENTA_HI, GLOCK, 0.5, decay_rate=d * 0.45))
    parts = [(th, 0, 1.0), (pf, 0, 0.5), (sp, 0.03, 0.55)]
    if size >= 1:
        parts.append((nrm(modal(rng, 784, BELL, d, tau_scale=0.4)), 0.02, 0.3))
    return reverb(stack(parts, d + 0.3), rng, [0.7, 1.1, 1.6][size], 0.22)


for _i, _n in enumerate(["s", "m", "l"]):
    reg(f"pet_land_{_n}", use=f"the animal lands, size {_n} (by rarity)")((lambda i: (lambda rng: _land(rng, i)))(_i))


@reg("pet_slowmo", use="slow motion at the jump of high rarities (the world slows down and speeds up)")
def _slowmo(rng):
    dur = 1.3
    n = N(dur)
    wh = nrm(swept_bandpass(pink(rng, n), 6000, 300, 1.5, curve=np.concatenate([np.linspace(0, 1, 40), np.linspace(1, 0.35, 40)]))) * env_bell(n, 0.5, 0.3, 0.0)
    t = tt(n)
    hum = np.sin(2 * np.pi * np.cumsum(140 - 70 * np.sin(np.pi * t / dur)) / SR) * env_bell(n, 0.5, 0.3, 0.0)
    return reverb(wh * 0.7 + nrm(hum) * 0.4, rng, 1.0, 0.25)


@reg("egg_shafts", kind="sustain", use="light shafts appear (rarity 3 and up): a soft vowel swell and high bells")
def _shafts(rng):
    dur = 2.4
    ch = np.zeros(N(dur))
    for f in notes(48, 55, 60, 64):
        ch += choir(rng, f, dur, "o", voices=4, attack=1.2, release=0.9)
    bells = nrm(sparkle_cloud(rng, 1.6, 12, PENTA_HI, GLOCK, 0.8))
    return reverb(stack([(nrm(ch), 0, 0.8), (bells, 0.8, 0.35)], dur + 0.4), rng, 2.0, 0.32)


@reg("egg_halo", kind="sustain", use="halo of the mythic and divine rarities: choir, strings and bells")
def _halo(rng):
    dur = 3.6
    ch = np.zeros(N(dur))
    for f in notes(55, 62, 67, 71, 74):
        ch += choir(rng, f, dur, "a", voices=5, attack=1.4, release=1.2)
    st = np.zeros(N(dur))
    for f in notes(43, 55, 62):
        st += string_pad(rng, f, dur, attack=1.2, release=1.2, voices=4)
    bells = nrm(sparkle_cloud(rng, 2.6, 18, PENTA_HI, BELL, 0.6, decay_rate=None))
    return reverb(stack([(nrm(ch), 0, 0.7), (nrm(st), 0, 0.4), (bells, 1.0, 0.35)], dur + 0.4), rng, 2.6, 0.32)


@reg("egg_orbit", use="the camera circles the animal (divine rarity): two passes of air")
def _orbit(rng):
    dur = 2.8
    n = N(dur)
    x = np.zeros(n)
    for c in (0.3, 0.72):
        seg = whoosh(rng, 1.2, 500, 4800, q=1.3, peak=0.5, width=0.22, floor=0.0)
        place(x, seg, c * dur - 0.5, 0.8)
    tone = nrm(glide_sine(220, 660, dur)) * env_bell(n, 0.55, 0.3, 0.0)
    return reverb(nrm(x) * 0.7 + tone * 0.25, rng, 1.4, 0.25)


def _tap(rng, f0, up):
    n = N(0.32)
    t = tt(n)
    f = f0 * (1 + (0.55 if up else -0.3) * (1 - np.exp(-t / 0.045)))
    car = np.sin(2 * np.pi * np.cumsum(f) / SR)
    mod = np.sin(2 * np.pi * np.cumsum(f * 2.0) / SR) * 0.35 * np.exp(-t / 0.08)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR + mod * 3) * np.exp(-t / 0.09)
    sp = nrm(sparkle_cloud(rng, 0.18, 30, PENTA_HI, GLOCK, 0.25))
    return reverb(stack([(nrm(x), 0, 0.9), (sp, 0.03, 0.35)], 0.5), rng, 0.4, 0.15)


@reg("pet_tap_1", use="tap on the animal: a cheerful boop going up")
def _tap1(rng):
    return _tap(rng, 620, True)


@reg("pet_tap_2", use="tap on the animal: a boop going down")
def _tap2(rng):
    return _tap(rng, 880, False)


@reg("egg_skip", use="SKIP pressed: a quick whoosh and a soft thud")
def _skip(rng):
    wh = nrm(whoosh(rng, 0.4, 500, 7000, q=1.3, peak=0.4, width=0.25, floor=0.0))
    th = nrm(thump(120, 60, 0.2, 0.06, 1.3))
    return reverb(stack([(wh, 0, 0.7), (th, 0.1, 0.6)], 0.5), rng, 0.4, 0.12)
