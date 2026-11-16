"""Music for the egg opening (V39): rarity stingers, the build-up before the reveal and two loops for the reveal card.
Instruments are additive / physical models from foley.py (strings, brass swell, vowel choir, Karplus-Strong harp,
glockenspiel, celesta, timpani, cymbal). Key: C major (the loops also have a brighter D major variant)."""
import numpy as np

from foley import *  # noqa: F401,F403
from egg_sounds import SOUNDS, reg, nrm, notes, PENTA_HI


# ------------------------------------------------------------------ instrument shortcuts (return mono arrays)
def i_glock(rng, f, vel=1.0, dur=1.4):
    return nrm(modal(rng, f, GLOCK, dur, tau_scale=0.9)) * vel


def i_celesta(rng, f, vel=1.0, dur=1.4):
    return nrm(modal(rng, f, CELESTA, dur, tau_scale=0.9)) * vel


def i_bell(rng, f, vel=1.0, dur=2.2):
    return nrm(modal(rng, f, BELL, dur, tau_scale=0.7)) * vel


def i_harp(rng, f, vel=1.0, dur=1.8):
    return karplus(rng, f, dur, decay=0.9978, bright=0.5, pick=0.22) * vel


def i_strings(rng, ms, dur, attack=0.5, release=0.8):
    out = np.zeros(N(dur))
    for m in ms:
        out += string_pad(rng, midi(m), dur, attack=attack, release=release, voices=3, bright=0.45)
    return nrm(out)


def i_brass(rng, ms, dur, attack=0.5, release=0.6):
    out = np.zeros(N(dur))
    for m in ms:
        out += brass_swell(rng, midi(m), dur, attack=attack, release=release)
    return nrm(out)


def i_choir(rng, ms, dur, vowel="a", attack=0.5, release=0.8, voices=4):
    out = np.zeros(N(dur))
    for m in ms:
        out += choir(rng, midi(m), dur, vowel, voices=voices, attack=attack, release=release)
    return nrm(out)


class Mix:
    def __init__(self, dur):
        self.out = np.zeros(N(dur))

    def add(self, x, at=0.0, gain=1.0, wrap=False):
        place(self.out, x, at, gain, wrap)
        return self


def finish(m, rng, rt60=2.0, wet=0.3, width=0.8, circular=False):
    x = m.out if isinstance(m, Mix) else m
    n = len(x)
    if circular:
        x = reverb(x, rng, rt60, wet, circular=True)
        return to_stereo(x, rng, width)
    x = reverb(x, rng, rt60, wet)
    return to_stereo(x, rng, width)


def gliss(rng, m, start, root, step_s, count, vel, inst="harp", scale=(0, 2, 4, 7, 9)):
    """Rising run on a pentatonic scale from `root` (midi)."""
    for k in range(count):
        mm = root + 12 * (k // len(scale)) + scale[k % len(scale)]
        f = midi(mm)
        g = i_harp(rng, f, vel * (0.6 + 0.4 * k / max(1, count - 1))) if inst == "harp" else i_glock(rng, f, vel)
        m.add(g, start + k * step_s)


# ================================================================== stingers: one per rarity (0 = Common .. 6 = Divine)
@reg("egg_reveal_0", kind="sustain", stereo=True, use="reveal stinger, rarity 0 (Common): three glockenspiel notes and a soft pad")
def _r0(rng):
    m = Mix(2.6)
    for i, mm in enumerate((72, 76, 79)):
        m.add(i_glock(rng, midi(mm), 0.9), i * 0.09)
    m.add(i_glock(rng, midi(84), 1.0, 1.8), 0.30)
    m.add(i_strings(rng, (60, 64, 67), 1.8, 0.25, 0.9), 0.0, 0.45)
    m.add(nrm(sparkle_cloud(rng, 0.8, 16, PENTA_HI, GLOCK, 0.5, decay_rate=0.4)), 0.3, 0.3)
    return finish(m, rng, 1.4, 0.3)


@reg("egg_reveal_1", kind="sustain", stereo=True, use="reveal stinger, rarity 1 (Uncommon): harp arpeggio, celesta, pad")
def _r1(rng):
    m = Mix(3.0)
    for i, mm in enumerate((67, 72, 76, 79, 84)):
        m.add(i_harp(rng, midi(mm), 0.9), i * 0.07)
    m.add(i_celesta(rng, midi(96), 0.8, 1.6), 0.42)
    m.add(i_strings(rng, (48, 55, 64), 2.0, 0.3, 1.0), 0.0, 0.5)
    m.add(nrm(sparkle_cloud(rng, 1.0, 20, PENTA_HI, CELESTA, 0.6, decay_rate=0.5)), 0.4, 0.3)
    return finish(m, rng, 1.6, 0.3)


@reg("egg_reveal_2", kind="sustain", stereo=True, use="reveal stinger, rarity 2 (Rare): bell fanfare, brass swell, harp run")
def _r2(rng):
    m = Mix(3.4)
    for i, mm in enumerate((72, 79, 84)):
        m.add(i_bell(rng, midi(mm), 0.9, 1.8), i * 0.14)
    m.add(i_brass(rng, (60, 67, 72, 76), 2.0, 0.35, 0.8), 0.0, 0.5)
    m.add(i_strings(rng, (48, 55, 60), 2.2, 0.4, 1.0), 0.0, 0.4)
    gliss(rng, m, 0.42, 72, 0.035, 8, 0.7)
    return finish(m, rng, 1.8, 0.3)


@reg("egg_reveal_3", kind="sustain", stereo=True, use="reveal stinger, rarity 3 (Epic): timpani roll into a brass hit with choir")
def _r3(rng):
    m = Mix(4.0)
    for i, t in enumerate((0.0, 0.09, 0.17, 0.24, 0.30, 0.35, 0.40, 0.44)):
        m.add(timpani(rng, midi(36), 0.25 + 0.06 * i, 1.0), t, 0.7)
    m.add(i_brass(rng, (48, 55, 60, 64, 67), 0.8, 0.5, 0.1), 0.0, 0.5)
    h = 0.55
    m.add(timpani(rng, midi(24), 1.0, 1.8), h, 0.9)
    m.add(i_brass(rng, (48, 55, 60, 64, 67), 1.9, 0.06, 0.9), h, 0.55)
    m.add(i_choir(rng, (60, 64, 67, 72), 2.2, "a", 0.15, 1.0), h, 0.6)
    m.add(nrm(cymbal(rng, 1.2)), h, 0.3)
    for i, mm in enumerate((79, 84, 88)):
        m.add(i_bell(rng, midi(mm), 0.8, 1.8), h + i * 0.07)
    gliss(rng, m, h + 0.15, 72, 0.04, 10, 0.7)
    return finish(m, rng, 2.0, 0.3)


@reg("egg_reveal_4", kind="sustain", stereo=True, use="reveal stinger, rarity 4 (Legendary): orchestral hit, choir, cymbal crash, bell cascade")
def _r4(rng):
    m = Mix(4.8)
    m.add(nrm(sub_drop(70, 24, 1.8, 0.8)), 0.0, 0.9)
    m.add(timpani(rng, midi(24), 1.0, 1.8), 0.0, 0.9)
    m.add(i_brass(rng, (48, 55, 60, 64, 67), 2.0, 0.05, 1.0), 0.0, 0.6)
    m.add(i_strings(rng, (48, 55, 64, 72), 2.4, 0.1, 1.2), 0.0, 0.45)
    m.add(i_choir(rng, (60, 64, 67, 72, 76), 2.6, "a", 0.35, 1.0, 5), 0.25, 0.65)
    m.add(nrm(cymbal(rng, 2.2)), 0.0, 0.4)
    gliss(rng, m, 0.55, 67, 0.035, 12, 0.8)
    m.add(nrm(sparkle_cloud(rng, 1.8, 30, PENTA_HI, BELL, 0.5, decay_rate=0.9)), 1.0, 0.5)
    m.add(i_choir(rng, (59, 62, 67, 71), 1.9, "a", 0.3, 1.0, 4), 1.9, 0.5)
    return finish(m, rng, 2.4, 0.3)


@reg("egg_reveal_5", kind="sustain", stereo=True, use="reveal stinger, rarity 5 (Mythic): two hits, modulation up to D major")
def _r5(rng):
    m = Mix(5.8)
    m.add(nrm(sub_drop(70, 24, 1.6, 0.7)), 0.0, 0.8)
    m.add(timpani(rng, midi(24), 0.9, 1.6), 0.0, 0.8)
    m.add(i_brass(rng, (48, 55, 60, 64), 1.6, 0.05, 0.8), 0.0, 0.5)
    m.add(i_choir(rng, (60, 64, 67, 72), 1.8, "a", 0.3, 0.8), 0.2, 0.55)
    m.add(nrm(cymbal(rng, 1.8)), 0.0, 0.3)
    h2 = 1.7
    m.add(nrm(sub_drop(80, 27, 2.2, 0.9)), h2, 1.0)
    m.add(timpani(rng, midi(26), 1.0, 2.0), h2, 0.9)
    m.add(i_brass(rng, (50, 57, 62, 66, 69), 2.4, 0.05, 1.2), h2, 0.6)
    m.add(i_strings(rng, (50, 57, 66, 74), 2.8, 0.2, 1.5), h2, 0.45)
    m.add(i_choir(rng, (62, 66, 69, 74, 78), 3.0, "a", 0.3, 1.4, 5), h2 + 0.1, 0.7)
    m.add(nrm(cymbal(rng, 2.8)), h2, 0.45)
    gliss(rng, m, h2 + 0.5, 74, 0.035, 14, 0.85)
    m.add(nrm(sparkle_cloud(rng, 2.6, 40, PENTA_HI, BELL, 0.5, decay_rate=1.4)), h2 + 0.3, 0.55)
    return finish(m, rng, 2.6, 0.32)


@reg("egg_reveal_6", kind="sustain", stereo=True, use="reveal stinger, rarity 6 (Divine): brass fanfare, roll, huge choir hit, bell cascade")
def _r6(rng):
    m = Mix(7.2)
    for i, mm in enumerate((60, 64, 67, 72)):
        m.add(i_brass(rng, (mm, mm + 7), 0.55 if i < 3 else 1.5, 0.04, 0.15), i * 0.18, 0.55)
    for i in range(10):
        m.add(timpani(rng, midi(36), 0.25 + 0.07 * i, 1.0), 0.95 + i * 0.055, 0.7)
    h = 1.6
    m.add(nrm(sub_drop(90, 24, 3.0, 1.2)), h, 1.0)
    m.add(timpani(rng, midi(24), 1.0, 2.4), h, 0.9)
    m.add(i_brass(rng, (48, 55, 60, 64, 67, 72), 3.0, 0.06, 1.4), h, 0.6)
    m.add(i_strings(rng, (48, 55, 64, 72, 76), 3.4, 0.2, 1.8), h, 0.45)
    m.add(i_choir(rng, (48, 55, 60, 64, 67, 72), 3.6, "a", 0.3, 1.6, 5), h + 0.05, 0.75)
    m.add(i_choir(rng, (72, 76, 79), 3.0, "o", 0.5, 1.4, 4), h + 0.4, 0.35)
    m.add(nrm(cymbal(rng, 3.6)), h, 0.5)
    for i, mm in enumerate((72, 76, 79, 84, 88, 91, 96)):
        m.add(i_bell(rng, midi(mm), 0.8, 2.4), h + 0.05 + i * 0.08)
    gliss(rng, m, h + 0.3, 60, 0.03, 18, 0.8)
    gliss(rng, m, h + 1.4, 72, 0.03, 14, 0.7)
    m.add(nrm(sparkle_cloud(rng, 4.0, 45, PENTA_HI, BELL, 0.55, decay_rate=1.8)), h + 0.3, 0.55)
    m.add(i_choir(rng, (84, 88, 91), 2.4, "a", 0.4, 1.6, 3), h + 2.6, 0.35)
    return finish(m, rng, 3.0, 0.34, 0.9)


# ================================================================== short UI-like accents around the card
@reg("egg_card", use="the reveal card slams onto the screen")
def _card(rng):
    wh = nrm(whoosh(rng, 0.25, 400, 6000, q=1.3, peak=0.8, width=0.3, floor=0.0))
    th = nrm(thump(150, 70, 0.22, 0.07, 1.4))
    pg = i_glock(rng, midi(100), 1.0, 0.6)
    tk = nrm(transient(rng, 1500, 7000, 0.002, dur=0.03))
    return reverb(stack([(wh, 0, 0.55), (th, 0.12, 0.8), (pg, 0.12, 0.4), (tk, 0.12, 0.4)], 0.6), rng, 0.6, 0.18)


@reg("egg_new", use="NEW PET: a rising triple ping with sparkle")
def _new(rng):
    parts = [(i_celesta(rng, midi(m), 0.9, 1.2), i * 0.09, 1.0) for i, m in enumerate((79, 84, 88))]
    parts.append((nrm(sparkle_cloud(rng, 0.6, 30, PENTA_HI, GLOCK, 0.5, decay_rate=0.3)), 0.2, 0.5))
    return reverb(stack(parts, 1.1), rng, 1.2, 0.3)


@reg("egg_dupe", use="DUPLICATE: two glass clinks and shard sparkle")
def _dupe(rng):
    a = nrm(modal(rng, 1700, GLASS, 0.5, tau_scale=0.7))
    b = nrm(modal(rng, 1400, GLASS, 0.5, tau_scale=0.7))
    tr = nrm(transient(rng, 3000, 9000, 0.0012, dur=0.02))
    sh = nrm(sparkle_cloud(rng, 0.4, 24, PENTA_HI, GLASS, 0.3, decay_rate=0.25))
    return reverb(stack([(a, 0, 0.9), (tr, 0, 0.4), (b, 0.12, 0.8), (tr, 0.12, 0.4), (sh, 0.15, 0.3)], 0.9), rng, 0.7, 0.2)


# ================================================================== loops under the reveal card (10 s at 96 BPM = 4 bars)
def _loop_music(rng, shift, bright):
    L = 10.0
    m = Mix(L)
    base = [((48, 52, 55), 36), ((45, 48, 52), 33), ((41, 45, 48), 29), ((43, 47, 50), 31)]  # C, Am, F, G
    beat = 0.625
    for i, (tri, bass) in enumerate(base):
        at = i * 2.5
        tri = tuple(t + shift for t in tri)
        m.add(i_strings(rng, tuple(t + 12 for t in tri), 2.5 + 1.4, 0.8, 1.2), at, 0.5, wrap=True)
        m.add(nrm(string_pad(rng, midi(bass + shift), 2.5 + 1.0, attack=0.5, release=1.0, voices=2, bright=0.1)), at, 0.35, wrap=True)
        if bright:
            m.add(i_choir(rng, tuple(t + 24 for t in tri), 2.5 + 1.4, "a", 0.9, 1.2, 3), at, 0.28, wrap=True)
        step = beat / (4 if bright else 2)
        pattern = [0, 2, 1, 2, 0, 2, 1, 2] if not bright else [0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 2, 1, 0, 1, 2, 1]
        for k in range(int(2.5 / step)):
            n = tri[pattern[k % len(pattern)]] + 24
            m.add(i_harp(rng, midi(n), 0.55 + 0.25 * (k % 4 == 0), 1.6), at + k * step, 0.5, wrap=True)
        m.add(i_glock(rng, midi(tri[2] + 36), 0.55, 1.6), at + 1.25, 0.4, wrap=True)
        if bright:
            for h in (0.0, 1.25):
                m.add(timpani(rng, midi(bass + shift - 12), 0.35, 1.4), at + h, 0.45, wrap=True)
    return finish(m, rng, 2.2, 0.28, 0.85, circular=True)


@reg("egg_music_a", kind="loop", loop=True, stereo=True, use="music under the reveal card, calm (rarities 0-3), loops, C-Am-F-G")
def _music_a(rng):
    return _loop_music(rng, 0, False)


@reg("egg_music_b", kind="loop", loop=True, stereo=True, use="music under the reveal card, grand (rarities 4-6), loops, D-Bm-G-A with choir and timpani")
def _music_b(rng):
    return _loop_music(rng, 2, True)


# ================================================================== build-up from the moment the animal appears to the reveal
@reg("egg_surge", kind="sustain", stereo=True, use="music build-up while the animal jumps (from emerge to reveal): arpeggio, strings, roll, riser")
def _surge(rng):
    dur = 5.5
    m = Mix(dur + 1.6)
    prog = [(57, 60, 64), (53, 57, 60), (55, 59, 62), (55, 59, 62)]  # Am F G G
    seg = dur / 4
    step = 0.125
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    t = 0.0
    k = 0
    while t < dur - 0.2:
        tri = prog[min(3, int(t / seg))]
        gain = 0.18 + 0.8 * (t / dur) ** 1.3
        m.add(i_harp(rng, midi(tri[pat[k % 8]] + 12), 0.6, 1.2), t, gain)
        k += 1
        t += step
    for i, tri in enumerate(prog):
        m.add(i_strings(rng, tuple(x - 0 for x in tri), seg + 1.0, 0.6, 0.9), i * seg, 0.3 + 0.12 * i)
    for i in range(10):
        m.add(timpani(rng, midi(36), 0.22 + 0.07 * i, 1.0), dur - 1.4 + i * 0.12, 0.6)
    n = N(dur)
    rs = nrm(whoosh(rng, dur, 400, 9000, q=1.2, peak=1.0, width=0.55, floor=0.0, color="white")) * np.linspace(0, 1, n) ** 2.4
    m.add(rs, 0.0, 0.3)
    m.add(nrm(cymbal(rng, 1.8, swell=1.4, crash=False)), dur - 1.8, 0.35)
    return finish(m, rng, 1.8, 0.28, 0.8)
