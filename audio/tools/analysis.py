"""Spectrogram sheets (PNG) so a sound can be inspected without listening. numpy + scipy + Pillow."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import signal

from foley import SR

# small "inferno"-like colour ramp
_STOPS = [(0.0, (0, 0, 4)), (0.25, (66, 10, 104)), (0.5, (147, 38, 103)), (0.75, (229, 92, 48)), (0.9, (252, 165, 10)), (1.0, (252, 255, 164))]


def _cmap(v):
    v = np.clip(v, 0, 1)
    xs = [s[0] for s in _STOPS]
    out = np.zeros(v.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(v, xs, [s[1][c] for s in _STOPS])
    return out.astype(np.uint8)


def spectrogram_image(x, width=720, height=150, fmax=12000, floor_db=-90):
    m = x.mean(axis=0) if np.ndim(x) == 2 else x
    nper = 1024
    f, t, S = signal.spectrogram(m, SR, nperseg=nper, noverlap=nper * 3 // 4, scaling="spectrum", mode="magnitude")
    keep = f <= fmax
    S = 20 * np.log10(S[keep] + 1e-9)
    S = (S - floor_db) / (0 - floor_db)
    S = np.clip(S, 0, 1)[::-1]
    img = Image.fromarray(_cmap(S)).resize((width, height), Image.BILINEAR)
    # waveform strip
    strip = Image.new("RGB", (width, 34), (14, 14, 20))
    d = ImageDraw.Draw(strip)
    n = len(m)
    cols = np.array_split(np.abs(m), width)
    pk = np.max(np.abs(m)) + 1e-12
    for i, c in enumerate(cols):
        h = int(16 * (np.max(c) / pk)) if len(c) else 0
        d.line([(i, 17 - h), (i, 17 + h)], fill=(120, 200, 255))
    out = Image.new("RGB", (width, height + 34))
    out.paste(strip, (0, 0))
    out.paste(img, (0, 34))
    return out


def sheet(items, path, cols=2, width=720, height=150):
    """items: list of (label, array). Saves a PNG grid."""
    tiles = []
    for label, x in items:
        im = spectrogram_image(x, width, height)
        d = ImageDraw.Draw(im)
        secs = (x.shape[-1]) / SR
        d.rectangle([0, 34, 300, 50], fill=(0, 0, 0))
        d.text((4, 36), f"{label}  {secs:.2f}s", fill=(255, 255, 255))
        tiles.append(im)
    rows = (len(tiles) + cols - 1) // cols
    W = cols * (width + 4)
    H = rows * (height + 34 + 4)
    sh = Image.new("RGB", (W, H), (30, 30, 36))
    for i, im in enumerate(tiles):
        r, c = divmod(i, cols)
        sh.paste(im, (c * (width + 4), r * (height + 34 + 4)))
    sh.save(path)
    return path
