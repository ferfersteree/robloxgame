"""Generative background music and a forest ambience bed (stereo, seamless loops)."""
import numpy as np
from dsp import *


def stereo_pan(x, pan):
    """pan -1..1 equal-power"""
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)])


def add(dst, src, at, pan=0.0, gain=1.0):
    st = stereo_pan(src, pan) * gain
    i = max(0, int(at * SR))
    if i >= dst.shape[1]:
        return
    n = min(st.shape[1], dst.shape[1] - i)
    dst[:, i:i + n] += st[:, :n]


def soft_bass(f, dur, vel=1.0):
    t = t_axis(dur)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.2)
    x *= np.exp(-t / (0.6 * dur)) * adsr(len(t), 0.01, 0.05, 1.0, 0.15)
    return x * vel


def shaker(rng, vel=1.0):
    d = 0.09
    x = hp(noise(d, rng), 5500) * exp_env(int(d * SR), 0.02)
    return x * vel


def soft_kick(vel=1.0):
    d = 0.3
    x = sweep(110, 48, d) * exp_env(int(d * SR), 0.09)
    return lp(x, 400, 2) * vel


def render(name, bpm, bars, chords, scale, melody_oct, seed, swing=0.0, pulse=False,
           arp_density=0.62, pad_gain=0.2, shake=0.0, mel_gain=0.55, arp_gain=0.5, bell=False):
    rng = np.random.default_rng(seed)
    beat = 60.0 / bpm
    bar = 4 * beat
    total = bars * bar
    tail = 3.0
    out = np.zeros((2, int((total + tail) * SR)))
    for b in range(bars):
        ch = chords[(b // 2) % len(chords)] if len(chords) * 2 <= bars else chords[b % len(chords)]
        t0 = b * bar
        # pad
        for k, n in enumerate(ch["pad"]):
            v = pad_voice(midi(n), bar + 1.6, rng)
            v = lp(v, 1700, 2) * adsr(len(v), 0.9, 0.2, 0.85, 1.2) * pad_gain
            add(out, v, t0, pan=(k - 1.5) * 0.35)
        # bass
        add(out, soft_bass(midi(ch["root"]), 1.7 * beat * 2, 0.55), t0, 0.0)
        if pulse:
            add(out, soft_bass(midi(ch["root"]), beat * 0.9, 0.4), t0 + 2 * beat, 0.0)
            add(out, soft_bass(midi(ch["root"] + 7), beat * 0.9, 0.3), t0 + 3 * beat, 0.0)
            add(out, soft_kick(0.4), t0, 0.0)
            add(out, soft_kick(0.3), t0 + 2 * beat, 0.0)
        # arpeggio on the eighth-note grid
        tones = ch["arp"]
        step = beat / 2
        idx = int(rng.integers(0, len(tones)))
        for s in range(8):
            if rng.random() > arp_density:
                continue
            idx = (idx + int(rng.choice([1, 1, 2, -1]))) % len(tones)
            at = t0 + s * step + (swing * step if s % 2 else 0) + rng.uniform(-0.004, 0.004)
            f = midi(tones[idx])
            note = (bell_fm(f, 1.4, 3.5, 1.6, 0.6) if bell else kalimba(f, 1.5, 0.7)) * float(rng.uniform(0.45, 0.9))
            add(out, note, at, pan=float(rng.uniform(-0.6, 0.6)), gain=arp_gain)
        # melody: a short pentatonic phrase every second bar
        if b % 2 == 1 and rng.random() < 0.85:
            pos = int(rng.integers(0, len(scale)))
            at = t0 + float(rng.choice([0.0, 0.5, 1.0])) * beat
            for k in range(int(rng.integers(3, 6))):
                pos = int(np.clip(pos + int(rng.choice([-2, -1, -1, 1, 1, 2])), 0, len(scale) - 1))
                f = midi(scale[pos] + 12 * melody_oct)
                dur = float(rng.choice([0.5, 1.0, 1.0, 1.5])) * beat
                add(out, marimba(f, 1.3, 0.85), at, pan=0.15, gain=mel_gain)
                at += dur
                if at > t0 + bar * 1.8:
                    break
        # shaker brush
        if shake > 0:
            for s in range(8):
                if s % 2 == 1:
                    add(out, shaker(rng, shake * float(rng.uniform(0.6, 1.0))), t0 + s * beat / 2, pan=float(rng.uniform(-0.3, 0.3)))
    # reverb on everything
    wet = reverb(out, rng, 2.4, 0.3, 6500)
    n = out.shape[1]
    wet = wet[:, :n]
    # make the loop seamless: fold the tail back onto the head
    ti = int(total * SR)
    tl = n - ti
    body = wet[:, :ti].copy()
    body[:, :tl] += wet[:, ti:ti + tl]
    # gentle glue
    body = softclip(body / (np.max(np.abs(body)) + 1e-9), 1.1)
    return peak_norm(body, -6.0)


def chord(root, pad, arp):
    return dict(root=root, pad=pad, arp=arp)


def tracks():
    out = {}
    # 1: meadow, C major pentatonic, relaxed
    c = [
        chord(36, [55, 59, 64, 67], [72, 76, 79, 83, 86]),       # Cmaj7
        chord(33, [52, 57, 60, 64], [69, 72, 76, 79, 81]),       # Am7
        chord(29, [53, 57, 60, 64], [65, 69, 72, 76, 81]),       # Fmaj7
        chord(31, [50, 55, 59, 64], [67, 71, 74, 79, 83]),       # G6
    ]
    out["music_meadow"] = render("meadow", 72, 32, c, [0, 2, 4, 7, 9], 5, 11, swing=0.18, shake=0.05)
    # 2: hunt, D minor pentatonic, a little more pulse
    c = [
        chord(38, [53, 57, 60, 64], [69, 72, 74, 77, 81]),       # Dm7
        chord(34, [53, 58, 62, 65], [70, 74, 77, 79, 82]),       # Bbmaj7
        chord(41, [53, 57, 60, 65], [65, 69, 72, 77, 79]),       # F
        chord(36, [55, 60, 64, 67], [72, 76, 79, 81, 84]),       # C
    ]
    out["music_hunt"] = render("hunt", 88, 32, c, [2, 5, 7, 9, 0], 5, 23, swing=0.12, pulse=True, arp_density=0.7, shake=0.08, pad_gain=0.16)
    # 3: cozy, F major, slow bells for menus and the shop
    c = [
        chord(29, [53, 57, 60, 64], [72, 77, 81, 84, 88]),       # Fmaj7
        chord(26, [50, 57, 62, 65], [69, 74, 77, 81, 86]),       # Dm7
        chord(34, [53, 58, 62, 65], [70, 74, 77, 82, 86]),       # Bbmaj7
        chord(36, [52, 55, 60, 64], [72, 76, 79, 84, 88]),       # C
    ]
    out["music_cozy"] = render("cozy", 60, 24, c, [5, 7, 9, 0, 2], 5, 37, swing=0.0, arp_density=0.45, pad_gain=0.24, bell=True, arp_gain=0.38, mel_gain=0.4)
    return out


def forest_ambience():
    rng = np.random.default_rng(91)
    d = 28.0
    pad_t = 2.0
    n = int((d + pad_t) * SR)
    t = np.arange(n) / SR
    # wind
    wind = noise(d + pad_t, rng, "pink")
    wind = bp(wind, 160, 1100, 2)
    mod = 0.65 + 0.35 * np.sin(2 * np.pi * 0.11 * t + 1.0) * np.sin(2 * np.pi * 0.047 * t)
    wind = wind * mod
    wind_r = np.roll(wind, int(0.013 * SR))
    out = np.stack([wind, wind_r]) * 0.55
    # soft leaf hiss
    leaf = hp(noise(d + pad_t, rng), 4500) * (0.04 + 0.03 * np.sin(2 * np.pi * 0.23 * t) ** 2)
    out += np.stack([leaf, np.roll(leaf, 300)])
    # birds: a few two-note FM chirps with random pan
    for k in range(9):
        at = rng.uniform(1.0, d - 2.0)
        f0 = rng.uniform(2300, 3600)
        for q in range(int(rng.integers(2, 5))):
            dur = 0.09 + 0.03 * rng.random()
            fr = np.linspace(f0, f0 * rng.uniform(1.12, 1.4), int(dur * SR))
            ch = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.linspace(0, np.pi, int(dur * SR))) ** 2
            add(out, ch * 0.08, at + q * (dur + 0.05), pan=float(rng.uniform(-0.8, 0.8)))
    out = reverb(out, rng, 1.8, 0.18, 6000)[:, :n]
    # seamless loop: crossfade the extra seconds onto the head
    L = int(d * SR)
    xf = int(pad_t * SR)
    body = out[:, :L].copy()
    body[:, :xf] = body[:, :xf] * np.linspace(0, 1, xf) ** 0.5 + out[:, L:L + xf] * np.linspace(1, 0, xf) ** 0.5
    return peak_norm(body, -9.0)


if __name__ == "__main__":
    for k, v in tracks().items():
        print(k, v.shape[1] / SR, "s", round(rms_db(v), 1), "dB")
    a = forest_ambience()
    print("amb", a.shape[1] / SR, "s", round(rms_db(a), 1), "dB")
