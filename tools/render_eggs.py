"""Renders the four shop eggs (V30: high detail) as faceted crystal eggs, offline (numpy + OpenCV + scipy).
Usage: python tools/render_eggs.py <out_dir> [key ...]
Each egg has its own look: Mystic = frosted ice, Royal = gold-banded amethyst, Cosmic = ringed starfire,
Absolute = prismatic with a halo. Common to all: glowing cracks between the shards, an inner light core,
bloom, a lit pedestal, floating sparks. The shop draws the result at runtime through EditableImage (nothing is uploaded).
"""
import sys, os, math
import numpy as np
import cv2
from scipy.spatial import cKDTree

W, H = 336, 426          # final size
SS = 3                   # supersampling

PAL = {
    "egg_mystic":   dict(base=(70, 165, 255), accent=(150, 245, 255), glow=(80, 195, 255), spread=0.04, deco="frost", beam=0.10),
    "egg_royal":    dict(base=(160, 66, 250), accent=(255, 120, 235), glow=(205, 95, 255), spread=0.05, deco="gold", beam=0.18),
    "egg_cosmic":   dict(base=(255, 128, 36), accent=(255, 226, 100), glow=(255, 150, 50), spread=0.05, deco="ring", beam=0.24),
    "egg_absolute": dict(base=(90, 235, 255), accent=(235, 250, 255), glow=(120, 240, 255), spread=0.55, deco="halo", beam=0.32),
}
GOLD = np.array([255, 206, 72], np.float32)
RAINBOW = [(255, 80, 120), (255, 200, 70), (120, 255, 140), (80, 220, 255), (130, 120, 255), (255, 100, 230)]


def over(dp, da, sp, sa):
    """premultiplied src over dst (in place); sp is premultiplied rgb (0..255), sa alpha (0..1)"""
    dp[:] = sp + dp * (1 - sa[..., None])
    da[:] = sa + da * (1 - sa)


def star(h, w, px, py, size, ss):
    """4-point glint with a hot core (alpha map, 0..1)"""
    L = int(size * ss)
    yy, xx = np.mgrid[-L:L + 1, -L:L + 1].astype(np.float32)
    g = np.exp(-(np.abs(xx) * np.abs(yy)) / (0.9 * ss * size * 0.14)) * np.exp(-(xx ** 2 + yy ** 2) / (L * L * 0.55))
    core = np.exp(-(xx ** 2 + yy ** 2) / (size * ss * 0.12) ** 2)
    g = np.clip(g + core, 0, 1)
    out = np.zeros((h, w), np.float32)
    y0, x0, y1, x1 = max(py - L, 0), max(px - L, 0), min(py + L + 1, h), min(px + L + 1, w)
    if y1 > y0 and x1 > x0:
        out[y0:y1, x0:x1] = g[(y0 - py + L):(y1 - py + L), (x0 - px + L):(x1 - px + L)]
    return out


def ring_layers(h, w, cx, cy, rx, ry, thick, colors):
    """an elliptical ring as two premultiplied layers: back (upper arc, behind the egg) and front (lower arc)"""
    back = np.zeros((h, w, 4), np.float32)
    front = np.zeros((h, w, 4), np.float32)
    n = 360
    for k in range(n):
        a0, a1 = k / n * 2 * math.pi, (k + 1.6) / n * 2 * math.pi
        c = colors(k / n)
        p0 = (int(cx + rx * math.cos(a0)), int(cy + ry * math.sin(a0)))
        p1 = (int(cx + rx * math.cos(a1)), int(cy + ry * math.sin(a1)))
        dst = front if math.sin((a0 + a1) / 2) > 0 else back
        cv2.line(dst, p0, p1, (float(c[0]), float(c[1]), float(c[2]), 255.0), thick, cv2.LINE_AA)
    out = []
    gcol = np.array(colors(0.3), np.float32)
    for d in (back, front):
        a = d[..., 3] / 255.0                      # coverage; the rgb written by cv2 is already scaled by coverage
        soft = cv2.GaussianBlur(a, (0, 0), thick * 1.6)
        prem = d[..., :3] + soft[..., None] * gcol[None, None, :] * 0.5
        out.append((np.clip(prem, 0, 255), np.clip(np.maximum(a, soft * 0.5), 0, 1)))
    return out


def render(key, clean=False):
    p = PAL[key]
    w, h = W * SS, H * SS
    cx, cy = w * 0.5, h * 0.47
    half_h = h * 0.325
    R = w * 0.285
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xx - cx
    t = (cy - yy) / half_h
    inside_t = np.abs(t) < 1
    tt = np.clip(t, -0.9999, 0.9999)
    r = R * np.sqrt(1 - tt * tt) * (1 - 0.20 * tt)
    inside = inside_t & (np.abs(x) < r)
    z = np.sqrt(np.clip(r * r - x * x, 0, None))
    t2 = np.clip(tt + 1e-3, -0.9999, 0.9999)
    r2 = R * np.sqrt(1 - t2 * t2) * (1 - 0.20 * t2)
    drdy = ((r2 - r) / (t2 - tt + 1e-9)) * (-1.0 / half_h)
    rs = np.maximum(r, 1e-3)
    n = np.stack([x / rs, -drdy, z / rs], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    n[..., 1] *= -1

    # ---- crystal shards (Voronoi cells on the surface)
    rng = np.random.default_rng(23 + sum(map(ord, key)))
    NS = 62
    cand = []
    for _ in range(NS * 4):
        ts = rng.uniform(-0.97, 0.97)
        th = rng.uniform(-math.pi * 0.62, math.pi * 0.62)
        rr = R * math.sqrt(1 - ts * ts) * (1 - 0.20 * ts)
        cand.append((rr * math.sin(th), ts * half_h, rr * math.cos(th), ts, th))
    pts_all = np.array([[c[0], c[1], c[2]] for c in cand], np.float32)
    keep = [0]
    for i in range(1, len(cand)):
        if np.min(np.linalg.norm(pts_all[keep] - pts_all[i], axis=1)) > R * 0.21:
            keep.append(i)
        if len(keep) >= NS:
            break
    seeds = [cand[k] for k in keep]
    pts = np.array([[s[0], s[1], s[2]] for s in seeds], np.float32)
    ns = len(seeds)
    snorm = np.zeros((ns, 3), np.float32)
    for k, (sx, sy, sz, ts, th) in enumerate(seeds):
        ra = R * math.sqrt(1 - ts * ts) * (1 - 0.20 * ts)
        tb = min(0.9999, ts + 1e-3)
        rb = R * math.sqrt(1 - tb * tb) * (1 - 0.20 * tb)
        nv = np.array([math.sin(th), ((rb - ra) / (tb - ts)) / half_h, math.cos(th)], np.float32)
        nv /= np.linalg.norm(nv)
        nv = nv + rng.normal(0, 0.40, 3).astype(np.float32)
        snorm[k] = nv / np.linalg.norm(nv)
    table = rng.random((ns, 4)).astype(np.float32)
    ys_, xs_ = np.nonzero(inside)
    P = np.stack([x[ys_, xs_], (cy - yy)[ys_, xs_], z[ys_, xs_]], axis=-1)
    dd, ii = cKDTree(pts).query(P, k=2)
    idx1 = np.zeros(inside.shape, np.int32); idx1[ys_, xs_] = ii[:, 0]
    d1 = np.zeros(inside.shape, np.float32); d1[ys_, xs_] = dd[:, 0]
    d2 = np.zeros(inside.shape, np.float32); d2[ys_, xs_] = dd[:, 1]
    rnd = table[idx1]
    nn = snorm[idx1] * 0.9 + n * 0.1
    nn /= np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-9
    gap = (d2 - d1) / (R * 0.10)
    bev = np.clip(1 - gap, 0, 1)
    cvec = np.zeros(inside.shape + (3,), np.float32)
    cvec[ys_, xs_] = P - pts[ii[:, 0]]
    cvec /= np.linalg.norm(cvec, axis=-1, keepdims=True) + 1e-6
    nb = nn + cvec * (bev[..., None] ** 1.4) * 0.8
    nb /= np.linalg.norm(nb, axis=-1, keepdims=True) + 1e-9
    theta = np.arctan2(x, z)

    # ---- lighting
    L = np.array([-0.45, 0.65, 0.62], np.float32); L /= np.linalg.norm(L)
    V = np.array([0, 0, 1], np.float32)
    Hh = L + V; Hh /= np.linalg.norm(Hh)
    diff = np.clip((nb * L).sum(-1), 0, 1)
    spec = np.clip((nb * Hh).sum(-1), 0, 1) ** 42
    spec2 = np.clip((nn * Hh).sum(-1), 0, 1) ** 14
    fres = np.clip(1 - nb[..., 2], 0, 1) ** 2.2
    base = np.array(p["base"], np.float32)
    accent = np.array(p["accent"], np.float32)
    sp = p["spread"]
    if sp > 0.3:
        cols_arr = np.stack([cv2.cvtColor(np.uint8([[[(hu * 255) % 256, 215, 255]]]), cv2.COLOR_HSV2RGB_FULL)[0, 0] for hu in np.linspace(0, 1, 24)]).astype(np.float32)
        hue = rnd[..., 0] * 0.35 + (tt + 1) * 0.25 + theta * 0.12
        col = cols_arr[(np.mod(hue, 1.0) * 23).astype(int)] * 0.8 + base * 0.2
    else:
        hue = (rnd[..., 0] - 0.5) * 2 * sp
        col = base[None, None, :] * (1 + (rnd[..., 1:2] - 0.5) * 0.5)
        col = col + np.stack([hue * 255, hue * 90, -hue * 120], axis=-1)
    # gem texture inside each shard: soft noise and faint internal lines
    noise = cv2.GaussianBlur(np.random.default_rng(5).standard_normal((h, w)).astype(np.float32), (0, 0), 5 * SS)
    noise /= (np.abs(noise).max() + 1e-6)
    stripes = np.sin(x * 0.135 / SS + rnd[..., 3] * 40) * 0.5 + 0.5
    bright = 0.55 + 0.85 * rnd[..., 2]
    shade = 0.10 + 0.95 * diff
    rgb = col * (shade * bright * (1 + 0.28 * noise + 0.06 * stripes))[..., None]
    rgb = rgb + accent * (fres[..., None] * 0.7)

    # inner light core seen through the crystal
    cd = np.sqrt((x / R) ** 2 + (((cy + half_h * 0.05) - yy) / half_h) ** 2)
    core = np.exp(-(cd * 1.45) ** 2)
    rgb = rgb + accent * (core * (0.20 + 0.4 * rnd[..., 1]))[..., None] * 0.55
    rgb = rgb + accent * ((0.10 + 0.15 * nb[..., 2]) * (rnd[..., 1] > 0.55))[..., None] * 0.4
    rgb = rgb + 255 * (spec * (0.35 + rnd[..., 2] * 0.9))[..., None]
    rgb = rgb + accent * (spec2 * 0.3)[..., None]

    # grooves and light leaking through the cracks
    groove = np.clip(1 - gap / 0.2, 0, 1)
    rgb = rgb * (1 - 0.65 * groove[..., None])
    crack = np.exp(-np.clip(gap, 0, 4) * 3.4)
    crack_core = np.exp(-np.clip(gap, 0, 4) * 9.0)
    if sp > 0.3:
        rain = np.stack([np.interp((tt + 1) * 0.5 * 5, np.arange(6), [c[i] for c in RAINBOW]) for i in range(3)], axis=-1).astype(np.float32)
        crack_col = rain * 0.9 + 60
    else:
        crack_col = accent[None, None, :]
    em = crack[..., None] * crack_col + crack_core[..., None] * 255 * 0.40
    rgb = rgb + em * 0.62
    edge_light = bev * np.clip(nb[..., 1] * 0.5 + 0.5, 0, 1)
    rgb = rgb + accent * (edge_light[..., None] * 0.30)

    # ---- tier decoration on the shell
    deco = p["deco"]
    if deco == "gold":
        band = (np.abs(tt - 0.34) < 0.04) | (np.abs(tt + 0.26) < 0.04)
        gl = np.clip((nn * L).sum(-1), 0, 1)
        gcol = GOLD[None, None, :] * (0.35 + 0.95 * gl[..., None]) + 255 * (np.clip((nn * Hh).sum(-1), 0, 1) ** 20 * 0.9)[..., None]
        stud = (np.abs(((theta / (2 * math.pi)) * 13 % 1) - 0.5) < 0.16) & band
        gcol = np.where(stud[..., None], np.array([255, 120, 235], np.float32) * (0.5 + 0.7 * gl[..., None]) + 120, gcol)
        rim = (np.abs(tt - 0.34) > 0.033) & (np.abs(tt + 0.26) > 0.033)
        gcol = np.where((band & rim)[..., None], gcol * 0.55, gcol)
        rgb = np.where((band & inside)[..., None], gcol, rgb)
    elif deco == "frost":
        frost = inside & (noise > 0.10) & (tt > -0.1) & (rnd[..., 3] > 0.35)
        rgb = np.where(frost[..., None], rgb * 0.40 + np.array([205, 242, 255], np.float32) * 0.60 * (0.75 + 0.25 * diff[..., None]), rgb)
        icy = inside & (np.abs(noise) < 0.02)
        rgb = np.where(icy[..., None], rgb + 120, rgb)
    rgb = np.clip(rgb, 0, 255)

    alpha = inside.astype(np.float32)
    bl = np.clip(rgb - 205, 0, 255) * alpha[..., None]
    bloom = cv2.GaussianBlur(bl, (0, 0), 12) * 0.9 + cv2.GaussianBlur(bl, (0, 0), 28) * 0.7
    egg_p = np.clip(rgb * alpha[..., None] + bloom * alpha[..., None] * 0.4, 0, 255)

    if clean:
        # hatch-scene sprite: only the egg (no pedestal, glow, ring or sparks), tightly cropped, 440 px tall
        dp = egg_p.copy(); da = alpha.copy()
        for (gx, gy, gs) in [(-0.45, 0.45, 26), (0.5, 0.15, 17)]:
            m = star(h, w, int(cx + gx * R), int(cy - gy * half_h), gs, SS) * alpha
            over(dp, da, 255 * m[..., None], np.clip(m, 0, 1))
        ys, xs = np.nonzero(da > 0.02)
        pad = 6 * SS
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, h)
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, w)
        crop = np.dstack([dp, da * 255])[y0:y1, x0:x1].astype(np.float32)
        sc = 440.0 / (y1 - y0)
        small = cv2.resize(crop, (int((x1 - x0) * sc), 440), interpolation=cv2.INTER_AREA)
        al = np.maximum(small[..., 3:4] / 255, 1e-4)
        straight = np.clip(small[..., :3] / al, 0, 255)
        return np.clip(np.dstack([straight, small[..., 3]]), 0, 255).astype(np.uint8)

    # ---- compose layers back to front (premultiplied)
    dp = np.zeros((h, w, 3), np.float32); da = np.zeros((h, w), np.float32)
    glow_col = np.array(p["glow"], np.float32)
    colm = np.exp(-(x / (R * 0.75)) ** 2) * np.clip((cy + half_h * 1.2 - yy) / (h * 0.95), 0, 1) ** 0.8
    over(dp, da, accent[None, None, :] * (colm * p["beam"])[..., None], colm * p["beam"])
    # pedestal
    py = int(cy + half_h * 1.06)
    ped = np.zeros((h, w, 4), np.float32)
    cv2.ellipse(ped, (int(cx), py), (int(R * 1.28), int(R * 0.30)), 0, 0, 360, (30, 14, 62, 235), -1, cv2.LINE_AA)
    cv2.ellipse(ped, (int(cx), py), (int(R * 1.28), int(R * 0.30)), 0, 0, 360, (float(glow_col[0]), float(glow_col[1]), float(glow_col[2]), 255), int(5 * SS), cv2.LINE_AA)
    cv2.ellipse(ped, (int(cx), py), (int(R * 0.98), int(R * 0.22)), 0, 0, 360, (float(accent[0]), float(accent[1]), float(accent[2]), 200), int(2.5 * SS), cv2.LINE_AA)
    pa = ped[..., 3] / 255
    over(dp, da, ped[..., :3] * 0.95, pa)
    # glow around and under the egg
    mask = cv2.GaussianBlur(alpha, (0, 0), 36)
    ground = np.zeros((h, w), np.float32)
    cv2.ellipse(ground, (int(cx), py), (int(R * 1.3), int(R * 0.34)), 0, 0, 360, 1.0, -1)
    ground = cv2.GaussianBlur(ground, (0, 0), 20)
    ga = np.clip(mask * 1.35 + ground * 1.0, 0, 1) * 0.8
    over(dp, da, glow_col[None, None, :] * ga[..., None], ga)

    front_layers = []
    if deco in ("ring", "halo"):
        if deco == "ring":
            col_fn = lambda u: GOLD * (0.75 + 0.25 * math.sin(u * 12.566))
            rx, ry, cyc = R * 1.62, R * 0.36, cy + half_h * 0.12
        else:
            col_fn = lambda u: np.array(RAINBOW[int(u * 6) % 6], np.float32) * 0.8 + 70
            rx, ry, cyc = R * 1.55, R * 0.42, cy - half_h * 0.05
        (bp, ba), (fp, fa) = ring_layers(h, w, cx, cyc, rx, ry, int(5 * SS), col_fn)
        over(dp, da, bp, ba)
        front_layers.append((fp, fa))
    over(dp, da, egg_p, alpha)
    for fp, fa in front_layers:
        over(dp, da, fp, fa)

    # floating sparks and big glints
    rs_ = np.random.default_rng(99)
    for k in range(16):
        ang = rs_.uniform(0, 2 * math.pi)
        rad = rs_.uniform(1.08, 1.38)
        sx_ = int(cx + math.cos(ang) * R * rad * 1.15)
        sy_ = int(cy - half_h * 0.2 + math.sin(ang) * half_h * rad * 0.95)
        size = rs_.uniform(5, 15)
        m = star(h, w, sx_, sy_, size, SS)
        c = accent if k % 3 else (GOLD if deco in ("gold", "ring") else np.array([255, 255, 255], np.float32))
        over(dp, da, c[None, None, :] * m[..., None] + 255 * (m ** 3)[..., None] * 0.6, np.clip(m, 0, 1))
    for (gx, gy, gs) in [(-0.45, 0.45, 26), (0.5, 0.15, 17), (-0.2, -0.45, 13)]:
        m = star(h, w, int(cx + gx * R), int(cy - gy * half_h), gs, SS)
        over(dp, da, 255 * m[..., None], np.clip(m, 0, 1))

    small = cv2.resize(np.dstack([dp, da * 255]).astype(np.float32), (W, H), interpolation=cv2.INTER_AREA)
    al = np.maximum(small[..., 3:4] / 255, 1e-4)
    straight = np.clip(small[..., :3] / al, 0, 255)
    return np.clip(np.dstack([straight, small[..., 3]]), 0, 255).astype(np.uint8)


def main():
    args = sys.argv[1:]
    clean = "--clean" in args
    args = [a for a in args if a != "--clean"]
    out_dir = args[0]
    keys = args[1:] or list(PAL)
    os.makedirs(out_dir, exist_ok=True)
    for key in keys:
        img = render(key, clean=clean)
        name = ("hatch_" + key) if clean else key
        cv2.imwrite(os.path.join(out_dir, name + ".png"), cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))
        bg = np.zeros(img.shape[:2] + (3,), np.float32); bg[:] = (40, 20, 70)
        a = img[..., 3:4].astype(np.float32) / 255
        prev = (img[..., :3].astype(np.float32) * a + bg * (1 - a)).astype(np.uint8)
        cv2.imwrite(os.path.join(out_dir, name + "_preview.png"), cv2.cvtColor(prev, cv2.COLOR_RGB2BGR))
        print(name, img.shape[1], img.shape[0], "ok", flush=True)


if __name__ == "__main__":
    main()
