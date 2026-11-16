"""Sound-design primitives for the egg-opening set (numpy + scipy only, deterministic for a given rng).

What makes synthetic sound feel "generated" is usually: perfectly regular timing, pure sine partials, a dry
sterile signal, no noise floor. The primitives here avoid that on purpose:
  * modal synthesis with inharmonic partial tables (glass, ceramic, wood, steel, bells, membranes),
  * transients made of band-passed noise, micro-crackle from a Poisson process,
  * bubbles as Minnaert chirps, whooshes as swept resonant noise,
  * a synthetic room (early reflections + 3-band decaying tail) that glues everything together,
  * additive instruments (no aliasing): strings, brass swell, vowel choir, Karplus-Strong plucks, timpani.
All functions return float64 mono arrays at SR unless stated.
"""
import zlib

import numpy as np
from scipy import signal

SR = 44100


def N(sec):
    return int(round(sec * SR))


def tt(n):
    return np.arange(n) / SR


def rng_for(name, salt=0):
    return np.random.default_rng(zlib.crc32(name.encode()) + 7919 * salt)


# ------------------------------------------------------------------ filters
def lowpass(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, min(fc, SR * 0.45) / (SR / 2), "low", output="sos"), x)


def highpass(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc / (SR / 2), "high", output="sos"), x)


def bandpass(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], "band", output="sos"), x)


def resonator(x, f, q):
    w0 = 2 * np.pi * f / SR
    alpha = np.sin(w0) / (2 * q)
    return signal.lfilter([alpha, 0, -alpha], [1 + alpha, -2 * np.cos(w0), 1 - alpha], x)


def swept_bandpass(x, f_start, f_end, q=2.5, blocks=96, curve=None):
    """Band-pass with a moving centre (block-wise). `curve` (0..1 per block) bends the sweep."""
    n = len(x)
    out = np.zeros(n)
    edges = np.linspace(0, n, blocks + 1).astype(int)
    for i in range(blocks):
        a, b = edges[i], edges[i + 1]
        u = (i + 0.5) / blocks
        if curve is not None:
            u = float(np.interp(u, np.linspace(0, 1, len(curve)), curve))
        f = f_start * (f_end / f_start) ** u
        seg = resonator(x[max(0, a - 768):b], f, q)
        out[a:b] = seg[-(b - a):]
    return out


# ------------------------------------------------------------------ noise
def white(rng, n):
    return rng.standard_normal(n)


def pink(rng, n):
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, rng.standard_normal(n))


def brown(rng, n):
    x = np.cumsum(rng.standard_normal(n))
    x -= np.linspace(x[0], x[-1], n)
    return highpass(x, 18, 1)


# ------------------------------------------------------------------ envelopes
def env_exp(n, tau, attack=0.0005):
    e = np.exp(-tt(n) / tau)
    na = max(1, int(attack * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def env_bell(n, peak=0.5, width=0.22, floor=0.0):
    t = np.linspace(0, 1, n)
    e = np.exp(-((t - peak) ** 2) / (2 * width ** 2))
    return floor + (1 - floor) * e


def env_swell(n, power=2.0):
    return np.linspace(0, 1, n) ** power


def fade_edges(x, fin=0.0005, fout=0.01):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if 0 < a < len(x):
        x[:a] *= np.linspace(0, 1, a)
    if 0 < b < len(x):
        x[-b:] *= np.linspace(1, 0, b)
    return x


# ------------------------------------------------------------------ mixing helpers
def place(out, grain, at, gain=1.0, wrap=False):
    """Add `grain` into `out` at time `at` (seconds). wrap=True wraps around the end (for seamless loops)."""
    i = int(round(at * SR))
    n = len(out)
    if wrap:
        idx = (np.arange(len(grain)) + i) % n
        np.add.at(out, idx, grain * gain)
        return out
    if i >= n or i < 0:
        return out
    m = min(len(grain), n - i)
    out[i:i + m] += grain[:m] * gain
    return out


def stack(parts, dur=None):
    """parts: list of (array, at_seconds, gain). Returns the sum, long enough for every part."""
    end = max(int(round(a * SR)) + len(x) for x, a, g in parts)
    n = N(dur) if dur else end
    out = np.zeros(max(n, 1))
    for x, a, g in parts:
        place(out, x, a, g)
    return out


def pitch_ratio(semi):
    return 2.0 ** (semi / 12.0)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------------ materials (modal tables)
GLASS = dict(r=[1, 2.32, 4.25, 6.63, 9.38], tau=[.30, .20, .12, .07, .035], a=[1, .62, .42, .28, .16])
CERAMIC = dict(r=[1, 2.18, 3.87, 5.71, 8.04], tau=[.045, .03, .02, .012, .008], a=[1, .7, .5, .35, .2])
WOOD = dict(r=[1, 2.76, 5.40, 8.93], tau=[.07, .035, .02, .01], a=[1, .6, .35, .2])
STEEL = dict(r=[1, 1.59, 2.14, 2.65, 3.16, 3.6], tau=[.45, .33, .24, .17, .12, .08], a=[1, .8, .6, .5, .4, .3])
BELL = dict(r=[.56, .92, 1.19, 1.71, 2.0, 2.74, 3.0, 3.76, 4.07], tau=[2.5, 2.0, 1.6, 1.2, 1.0, .6, .5, .3, .25],
            a=[.8, .7, 1, .6, .9, .45, .4, .25, .2])
GLOCK = dict(r=[1, 2.76, 5.40, 8.93], tau=[1.2, .45, .18, .08], a=[1, .45, .22, .1])
CELESTA = dict(r=[1, 4.0, 10.1], tau=[1.6, .3, .09], a=[1, .3, .12])
MARIMBA = dict(r=[1, 3.93, 9.9], tau=[.9, .18, .06], a=[1, .35, .1])
MEMBRANE = dict(r=[1, 1.5, 1.99, 2.44, 2.9], tau=[1.3, .9, .65, .5, .38], a=[1, .7, .5, .35, .25])


def modal(rng, f0, mat, dur, tau_scale=1.0, jitter=0.004, attack=0.0004, amp_scale=1.0):
    n = N(dur)
    t = tt(n)
    out = np.zeros(n)
    for r, tau, a in zip(mat["r"], mat["tau"], mat["a"]):
        f = f0 * r * (1 + rng.normal(0, jitter))
        if f > SR * 0.45:
            continue
        out += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / (tau * tau_scale))
    na = max(1, int(attack * SR))
    out[:na] *= np.linspace(0, 1, na)
    nf = max(2, int(min(0.03, dur * 0.25) * SR))
    out[-nf:] *= np.linspace(1, 0, nf)
    return out * amp_scale


# ------------------------------------------------------------------ elementary sounds
def transient(rng, lo, hi, tau, dur=None, attack=0.0002):
    dur = dur or tau * 7
    n = N(dur)
    x = white(rng, n)
    x = bandpass(x, lo, hi, 2) if hi else highpass(x, lo, 2)
    return x * env_exp(n, tau, attack)


def thump(f0, f1, dur, tau, drive=1.6, curve_tau=0.08):
    n = N(dur)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / curve_tau)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t / tau)
    na = N(0.002)
    x[:na] *= np.linspace(0, 1, na)
    return np.tanh(x * drive) / np.tanh(drive)


def crackle(rng, dur, rate_fn, f_lo, f_hi, tau_lo=0.0006, tau_hi=0.003, wrap=False):
    """Poisson micro-impacts (each a short resonant ping). rate_fn(t) = events per second at time t."""
    n = N(dur)
    out = np.zeros(n)
    tgrid = np.linspace(0, dur, 240)
    tmax = max(float(max(rate_fn(t) for t in tgrid)), 1e-3)
    te = 0.0
    while True:
        te += rng.exponential(1.0 / tmax)
        if te >= dur:
            break
        if rng.random() > rate_fn(te) / tmax:
            continue
        f = float(np.exp(rng.uniform(np.log(f_lo), np.log(f_hi))))
        tau = float(rng.uniform(tau_lo, tau_hi))
        L = int(tau * 9 * SR) + 8
        tl = np.arange(L) / SR
        g = rng.lognormal(0, 0.55) * np.sin(2 * np.pi * f * tl + rng.uniform(0, 6.28)) * np.exp(-tl / tau)
        place(out, g, te, 1.0, wrap=wrap)
    return out


def bubble(rng, f0, tau=0.03, xi=0.12, dur=None):
    """Minnaert-style bubble: a decaying sine whose pitch rises as the bubble shrinks."""
    dur = dur or tau * 6.5
    n = N(dur)
    t = tt(n)
    f = f0 * (1 + xi * (t / tau))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)
    x[:max(1, int(0.0006 * SR))] *= np.linspace(0, 1, max(1, int(0.0006 * SR)))
    return x


def whoosh(rng, dur, f0, f1, q=1.6, peak=0.5, width=0.24, floor=0.02, color="pink", curve=None):
    n = N(dur)
    x = pink(rng, n) if color == "pink" else white(rng, n)
    y = swept_bandpass(x, f0, f1, q, curve=curve)
    return y * env_bell(n, peak, width, floor)


def glide_sine(f0, f1, dur, curve="exp", harmonics=None):
    n = N(dur)
    u = np.arange(n) / max(n - 1, 1)
    f = f0 * (f1 / f0) ** u if curve == "exp" else f0 + (f1 - f0) * u
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph)
    if harmonics:
        for k, a in harmonics:
            x += a * np.sin(k * ph)
    return x


# ------------------------------------------------------------------ room
def make_ir(rng, rt60=1.2, pre=0.008, damp=7000, early=True):
    n = N(rt60 * 1.25)
    t = tt(n)
    base = rng.standard_normal(n)
    low = lowpass(base, 400, 2) * np.exp(-6.91 * t / (rt60 * 1.25))
    mid = bandpass(base, 400, 3500, 2) * np.exp(-6.91 * t / rt60)
    hi = highpass(base, 3500, 2) * np.exp(-6.91 * t / (rt60 * 0.5))
    ir = low + mid + 0.8 * hi
    ir = lowpass(ir, damp, 1)
    ir *= np.minimum(1.0, t / 0.025)
    ir[:N(pre)] = 0
    if early:
        peak = np.max(np.abs(ir)) + 1e-9
        for k in range(9):
            i = N(pre + rng.uniform(0.003, 0.05))
            if i < n:
                ir[i] += (0.8 ** k) * rng.choice([-1, 1]) * rng.uniform(0.5, 1.0) * peak * 2.5
    return ir / (np.sqrt(np.sum(ir ** 2)) + 1e-12)


def reverb(x, rng, rt60=1.2, wet=0.25, circular=False, **kw):
    """Mono in -> mono out. circular=True folds the tail back onto the start (seamless loops)."""
    ir = make_ir(rng, rt60, **kw)
    w = signal.fftconvolve(x, ir)
    if circular:
        L = len(x)
        out = w[:L].copy()
        k = L
        while k < len(w):
            seg = w[k:k + L]
            out[:len(seg)] += seg
            k += L
        return x * (1 - wet) + out * wet * 2.0
    dry = np.zeros(len(w))
    dry[:len(x)] = x
    return dry * (1 - wet) + w * wet * 2.0


def to_stereo(x, rng, width=0.5, rt60=None, wet=0.0, circular=False):
    """Decorrelate a mono signal into two channels (micro-delays + opposite tilt); optional reverb per channel."""
    L = len(x)
    d = N(0.0007 + 0.0035 * width)
    left = x.copy()
    right = np.zeros(L)
    right[d:] = x[:L - d]
    left = left + width * 0.25 * lowpass(x, 3000, 1)
    right = right + width * 0.25 * highpass(x, 3000, 1)
    chans = [left, right]
    if rt60 and wet > 0:
        chans = [reverb(c, np.random.default_rng(int(rng.integers(1 << 30))), rt60, wet, circular=circular)[:L if circular else None] for c in chans]
        m = min(len(c) for c in chans)
        chans = [c[:m] for c in chans]
    return np.stack(chans)


# ------------------------------------------------------------------ mastering
def dc_block(x):
    return highpass(x, 18, 1)


def trim_tail(x, floor_db=-52.0, keep=0.04):
    pk = np.max(np.abs(x)) + 1e-12
    thr = pk * 10 ** (floor_db / 20)
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    return x[:min(len(x), idx[-1] + N(keep))]


def softclip_to(x, ceiling):
    pk = np.max(np.abs(x))
    if pk <= ceiling:
        return x
    return ceiling * np.tanh(x / ceiling)


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x) ** 2)) + 1e-12)


def to_db(v):
    return 20 * np.log10(v + 1e-12)


def master(x, kind="hit", peak_db=-2.0, rms_db=-20.0):
    """kind: hit (peak target) | sustain (rms target, peaks capped) | loop (rms target, no trim, no fades)."""
    x = np.asarray(x, dtype=np.float64)
    stereo = x.ndim == 2
    mono_ref = x.mean(axis=0) if stereo else x
    ref = dc_block(mono_ref)
    if kind != "loop":
        n_keep = len(trim_tail(ref))
        x = x[:, :n_keep] if stereo else x[:n_keep]
    ceiling = 10 ** (-1.5 / 20)
    if kind == "hit":
        pk = np.max(np.abs(x)) + 1e-12
        x = x * (10 ** (peak_db / 20) / pk)
    else:
        cur = rms(x)
        x = x * (10 ** (rms_db / 20) / cur)
        x = softclip_to(x, ceiling)
        pk = np.max(np.abs(x)) + 1e-12
        if pk > ceiling:
            x = x * (ceiling / pk)
    if kind != "loop":
        if stereo:
            x = np.stack([fade_edges(c, 0.0005, 0.02) for c in x])
        else:
            x = fade_edges(x, 0.0005, 0.02)
    return x


# ------------------------------------------------------------------ instruments (additive, alias-free)
def karplus(rng, f, dur, decay=0.9965, bright=0.55, pick=0.18):
    """Karplus-Strong string with an all-pass fractional delay (accurate pitch) and a pick-position comb."""
    n = N(dur)
    P = SR / f - 0.5
    Pi = int(np.floor(P))
    d = P - Pi
    d = min(max(d, 0.05), 0.95)
    a = (1 - d) / (1 + d)
    # loop: y = x + g * 0.5(1+z^-1) * z^-Pi * (a+z^-1)/(1+a z^-1) * y
    den = np.zeros(Pi + 4)
    den[0] = 1.0
    den[1] += a
    g = decay
    for k, c in enumerate([a, 1 + a, 1.0]):
        den[Pi + k] -= g * 0.5 * c
    num = np.array([1.0, a])
    burst = lowpass(white(rng, Pi + 4), 800 + 9000 * bright, 2)
    exc = np.zeros(n)
    exc[:len(burst)] = burst
    pk = int(pick * Pi)
    if 0 < pk < Pi:
        exc[pk:pk + len(burst)] -= burst[:max(0, min(len(burst), n - pk))]
    y = signal.lfilter(num, den, exc)
    y *= np.minimum(1, tt(n) / 0.0012)
    return y / (np.max(np.abs(y)) + 1e-9)


def harmonic_stack(f, dur, partials, vib_hz=0.0, vib_depth=0.0, rng=None, amp_fn=None, phase_rand=True):
    """Sum of harmonics. partials = list of (k, amp). amp_fn(k, t) may return a time-varying gain array."""
    n = N(dur)
    t = tt(n)
    if vib_hz:
        ph0 = rng.uniform(0, 6.28) if rng is not None else 0
        vib = 1 + vib_depth * np.sin(2 * np.pi * vib_hz * t + ph0)
        base = 2 * np.pi * np.cumsum(f * vib) / SR
    else:
        base = 2 * np.pi * f * t
    out = np.zeros(n)
    for k, a in partials:
        if f * k > SR * 0.45:
            break
        g = a if amp_fn is None else a * amp_fn(k, t)
        ph = rng.uniform(0, 6.28) if (rng is not None and phase_rand) else 0
        out += g * np.sin(k * base + ph)
    return out


def string_pad(rng, f, dur, attack=0.5, release=0.6, voices=4, detune_cents=7, bright=0.5):
    """Ensemble pad: detuned voices, 1/k harmonics, slow vibrato, gentle low-pass."""
    n = N(dur)
    out = np.zeros(n)
    kmax = max(3, int(min(14, 0.4 * SR / f)))
    parts = [(k, 1.0 / k ** (1.2 - 0.5 * bright)) for k in range(1, kmax + 1)]
    for v in range(voices):
        cents = (v - (voices - 1) / 2) * detune_cents / max(1, (voices - 1) / 2)
        out += harmonic_stack(f * 2 ** (cents / 1200), dur, parts, 4.6 + 0.4 * v, 0.0035, rng)
    out /= voices
    env = np.ones(n)
    na, nr = N(attack), N(release)
    env[:na] = np.linspace(0, 1, na) ** 1.5
    env[-nr:] = np.minimum(env[-nr:], np.linspace(1, 0, nr))
    return out * env


def brass_swell(rng, f, dur, attack=0.6, hold=0.0, release=0.4, open_to=3600, open_from=500):
    """Synth-brass: saw harmonics whose cut-off opens over time (filter swell), slight vibrato."""
    n = N(dur)
    t = tt(n)
    cutoff = open_from + (open_to - open_from) * np.clip(t / max(attack, 0.05), 0, 1) ** 1.6
    kmax = int(min(26, 0.42 * SR / f))
    parts = [(k, 1.0 / k) for k in range(1, kmax + 1)]
    amp_fn = lambda k, tt_: 1.0 / (1.0 + (k * f / cutoff) ** 4)
    out = np.zeros(n)
    for dt_c in (-6, 0, 6):
        out += harmonic_stack(f * 2 ** (dt_c / 1200), dur, parts, 5.2, 0.004, rng, amp_fn=amp_fn)
    out /= 3
    env = np.ones(n)
    na, nr = N(attack * 0.8), N(release)
    env[:na] = np.linspace(0, 1, na) ** 1.4
    env[-nr:] = np.minimum(env[-nr:], np.linspace(1, 0, nr))
    return out * env


VOWELS = {
    "a": [(730, 90, 1.0), (1090, 110, 0.55), (2440, 160, 0.25)],
    "o": [(570, 80, 1.0), (840, 90, 0.5), (2410, 150, 0.15)],
    "u": [(325, 70, 1.0), (700, 80, 0.4), (2530, 150, 0.1)],
}


def choir(rng, f, dur, vowel="a", voices=6, attack=0.7, release=0.7, spread_cents=14):
    """Vowel pad: harmonic stack shaped by formant bumps, vibrato per voice, breath noise."""
    n = N(dur)
    form = VOWELS[vowel]
    kmax = int(min(40, 0.42 * SR / f))
    out = np.zeros(n)
    for v in range(voices):
        cents = rng.uniform(-spread_cents, spread_cents)
        ff = f * 2 ** (cents / 1200)
        parts = []
        for k in range(1, kmax + 1):
            fk = k * ff
            a = 0.12 / k ** 0.6
            for (fc, bw, g) in form:
                a += g * np.exp(-0.5 * ((fk - fc) / bw) ** 2)
            parts.append((k, a))
        out += harmonic_stack(ff, dur, parts, rng.uniform(4.8, 6.2), rng.uniform(0.004, 0.009), rng)
    out /= voices
    breath = bandpass(pink(rng, n), 900, 4200, 2) * 0.05
    out = out + breath * np.linspace(0.3, 1, n)
    env = np.ones(n)
    na, nr = N(attack), N(release)
    env[:na] = np.linspace(0, 1, na) ** 1.6
    env[-nr:] = np.minimum(env[-nr:], np.linspace(1, 0, nr))
    return out * env


def timpani(rng, f, vel=1.0, dur=1.6):
    n = N(dur)
    t = tt(n)
    out = np.zeros(n)
    glide = 1 + 0.10 * np.exp(-t / 0.06)
    for r, tau, a in zip(MEMBRANE["r"], MEMBRANE["tau"], MEMBRANE["a"]):
        ph = 2 * np.pi * np.cumsum(f * r * glide) / SR + rng.uniform(0, 6.28)
        out += a * np.sin(ph) * np.exp(-t / (tau * (0.6 + 0.5 * vel)))
    stick = transient(rng, 300, 2600, 0.006, dur=0.05) * 0.9
    place(out, stick, 0, vel)
    body = thump(f * 1.0, f * 0.78, dur, 0.5, 1.2, 0.12) * 0.7
    out += body
    return out * vel


def cymbal(rng, dur, swell=0.0, crash=True):
    n = N(dur)
    x = highpass(white(rng, n), 3200, 2)
    t = tt(n)
    env = np.exp(-t / (dur * 0.38)) if crash else np.ones(n)
    if swell > 0:
        ns = N(swell)
        env[:ns] *= np.linspace(0, 1, ns) ** 2
    metal = np.zeros(n)
    for _ in range(18):
        f = rng.uniform(3200, 11000)
        metal += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / rng.uniform(0.25, 1.2) / (dur / 2.0))
    return (x * 0.7 + metal * 0.05) * env


def sub_drop(f0, f1, dur, tau=None, drive=1.3):
    return thump(f0, f1, dur, tau or dur * 0.45, drive, curve_tau=dur * 0.22)


def sparkle_cloud(rng, dur, rate, notes, mat=None, tau_scale=1.0, gain=1.0, wrap=False, decay_rate=None, seed_gain=0.5):
    """Random bell grains on a set of note frequencies. decay_rate: density multiplier exp(-t/decay_rate).
    wrap=True: seamless loop (grains that pass the end continue at the start)."""
    mat = mat or GLOCK
    tail = 0.0 if wrap else mat["tau"][0] * tau_scale * 1.0 + 0.3
    n = N(dur + tail)
    out = np.zeros(n)
    tgrid = np.linspace(0, dur, 100)

    def rate_fn(t):
        return rate * (np.exp(-t / decay_rate) if decay_rate else 1.0)

    tmax = max(float(max(rate_fn(t) for t in tgrid)), 1e-3)
    te = 0.0
    while True:
        te += rng.exponential(1.0 / tmax)
        if te >= dur:
            break
        if rng.random() > rate_fn(te) / tmax:
            continue
        f = float(rng.choice(notes))
        d = float(rng.uniform(0.35, 1.0)) * tau_scale
        g = modal(rng, f, mat, mat["tau"][0] * d * 3.2, tau_scale=d, jitter=0.003)
        place(out, g, te, gain * rng.uniform(0.25, 1.0) * seed_gain * 2, wrap=wrap)
    return out


# ------------------------------------------------------------------ analysis helpers
def describe(x):
    m = x.mean(axis=0) if x.ndim == 2 else x
    n = len(m)
    pk = float(np.max(np.abs(m)))
    spec = np.abs(np.fft.rfft(m[: min(n, 65536)] * np.hanning(min(n, 65536))))
    freqs = np.fft.rfftfreq(min(n, 65536), 1 / SR)
    cen = float((spec * freqs).sum() / (spec.sum() + 1e-12))
    env = np.abs(m)
    t_pk = float(np.argmax(env) / SR)
    thr = pk * 10 ** (-40 / 20)
    idx = np.where(env > thr)[0]
    tail40 = float(idx[-1] / SR) if len(idx) else 0.0
    return dict(sec=round(n / SR, 3), peak_db=round(to_db(pk), 1), rms_db=round(to_db(rms(m)), 1),
                centroid_hz=int(cen), t_peak=round(t_pk, 3), t_tail40=round(tail40, 3),
                finite=bool(np.isfinite(m).all()))
