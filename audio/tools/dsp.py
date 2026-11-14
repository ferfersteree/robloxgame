"""Small DSP toolkit for the SpearHunt sound set (numpy + scipy only)."""
import numpy as np
from scipy import signal

SR = 44100


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def fit(x, dur=None):
    n = int(dur * SR) if dur else len(x)
    out = np.zeros(n)
    m = min(n, len(x))
    out[:m] = x[:m]
    return out


def mix_into(dst, src, at=0.0, gain=1.0):
    i = int(at * SR)
    if i >= len(dst):
        return dst
    n = min(len(src), len(dst) - i)
    dst[i:i + n] += src[:n] * gain
    return dst


def exp_env(n, tau):
    t = np.arange(n) / SR
    return np.exp(-t / tau)


def adsr(n, a=0.005, d=0.05, s=0.6, r=0.05):
    env = np.ones(n)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(na, 1)
    env[:na] = np.linspace(0, 1, na)
    if nd > 0 and na + nd < n:
        env[na:na + nd] = np.linspace(1, s, nd)
        env[na + nd:] = s
    if nr > 0 and nr < n:
        env[-nr:] *= np.linspace(1, 0, nr)
    return env


def fade(x, fin=0.002, fout=0.01):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a > 0 and a < len(x):
        x[:a] *= np.linspace(0, 1, a)
    if b > 0 and b < len(x):
        x[-b:] *= np.linspace(1, 0, b)
    return x


def sine(f, dur, phase=0.0):
    t = t_axis(dur)
    if np.isscalar(f):
        return np.sin(2 * np.pi * f * t + phase)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph + phase)


def sweep(f0, f1, dur, curve="exp"):
    n = int(dur * SR)
    if curve == "exp":
        f = f0 * (f1 / f0) ** (np.arange(n) / max(n - 1, 1))
    else:
        f = np.linspace(f0, f1, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def noise(dur, rng, color="white"):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    if color == "pink":
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        x = signal.lfilter(b, a, x)
    elif color == "brown":
        x = np.cumsum(x)
        x -= np.linspace(x[0], x[-1], n)
    return x / (np.max(np.abs(x)) + 1e-9)


def lp(x, fc, order=4):
    sos = signal.butter(order, min(fc, SR * 0.49) / (SR / 2), "low", output="sos")
    return signal.sosfilt(sos, x)


def hp(x, fc, order=4):
    sos = signal.butter(order, fc / (SR / 2), "high", output="sos")
    return signal.sosfilt(sos, x)


def bp(x, f0, f1, order=3):
    sos = signal.butter(order, [f0 / (SR / 2), min(f1, SR * 0.49) / (SR / 2)], "band", output="sos")
    return signal.sosfilt(sos, x)


def resonator(x, f, q):
    """Two-pole resonant band-pass (constant skirt) for sweeping 'air' sounds."""
    w0 = 2 * np.pi * f / SR
    alpha = np.sin(w0) / (2 * q)
    b = [alpha, 0, -alpha]
    a = [1 + alpha, -2 * np.cos(w0), 1 - alpha]
    return signal.lfilter(b, a, x)


def swept_bp(x, f_start, f_end, q=2.5, blocks=64):
    """Band-pass with a moving centre frequency (block-wise, with overlap smoothing)."""
    n = len(x)
    out = np.zeros(n)
    edges = np.linspace(0, n, blocks + 1).astype(int)
    for i in range(blocks):
        a, b = edges[i], edges[i + 1]
        f = f_start * (f_end / f_start) ** ((i + 0.5) / blocks)
        seg = resonator(x[max(0, a - 512):b], f, q)
        out[a:b] = seg[-(b - a):]
    return out


def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def peak_norm(x, db=-3.0):
    p = np.max(np.abs(x)) + 1e-12
    return x * (10 ** (db / 20) / p)


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


# ---------------------------------------------------------------- instruments
def marimba(f, dur=1.2, vel=1.0, bright=1.0):
    """Warm mallet bar: fundamental plus the 4th and 10th partials with different decays."""
    t = t_axis(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / (0.55 * dur))
    x += 0.32 * bright * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.12)
    x += 0.10 * bright * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t / 0.045)
    # mallet click
    n = int(0.004 * SR)
    click = np.zeros(len(t))
    click[:n] = np.hanning(n * 2)[n:] * 0.25 * vel
    return fade((x * vel + click), 0.001, 0.02)


def kalimba(f, dur=1.4, vel=1.0):
    t = t_axis(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.5)
    x += 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.05)
    x += 0.08 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.2)
    return fade(x * vel, 0.001, 0.03)


def bell_fm(f, dur=1.2, ratio=3.5, index=3.0, vel=1.0):
    t = t_axis(dur)
    idx = index * np.exp(-t / 0.18)
    mod = np.sin(2 * np.pi * f * ratio * t)
    x = np.sin(2 * np.pi * f * t + idx * mod) * np.exp(-t / (0.4 * dur))
    return fade(x * vel, 0.001, 0.04)


def pad_voice(f, dur, rng, detune=0.004):
    t = t_axis(dur)
    x = np.zeros(len(t))
    for k, d in enumerate([-1, 0, 1]):
        ph = rng.uniform(0, 2 * np.pi)
        ff = f * (1 + d * detune)
        x += np.sin(2 * np.pi * ff * t + ph) + 0.25 * np.sin(2 * np.pi * 2 * ff * t + ph)
    x /= 3
    return x


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def reverb(x, rng, rt60=1.6, wet=0.25, damp=5200, pre=0.012, stereo=True):
    n = int(rt60 * 1.2 * SR)
    t = np.arange(n) / SR
    outs = []
    for ch in range(2 if stereo else 1):
        ir = rng.standard_normal(n) * np.exp(-6.9 * t / rt60)
        ir = lp(ir, damp, 2)
        ir[: int(pre * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        outs.append(ir)
    if np.ndim(x) == 1:
        x = np.stack([x, x]) if stereo else x[None]
    res = []
    for ch in range(x.shape[0]):
        wetsig = signal.fftconvolve(x[ch], outs[ch % len(outs)])[: x.shape[1] + n]
        dry = np.zeros_like(wetsig)
        dry[: x.shape[1]] = x[ch]
        res.append(dry * (1 - wet) + wetsig * wet * 2.2)
    return np.stack(res)
