"""Renders the four shop eggs as faceted crystal eggs (offline, numpy + OpenCV) and writes PNGs.
Usage: python tools/render_eggs.py <out_dir>
The shop draws these pictures at runtime through EditableImage (see tools/pack_eggs.py): nothing is uploaded to Roblox.
"""
import sys, math
import numpy as np
import cv2

W, H = 300, 380          # final size
SS = 3                   # supersampling
PAL = {
    # base colour of the crystal, accent (rim/glow), facet hue spread, specular tint
    "egg_mystic":   dict(base=(70, 170, 255), accent=(120, 235, 255), spread=0.04, glow=(80, 190, 255)),
    "egg_royal":    dict(base=(170, 70, 255), accent=(255, 110, 235), spread=0.05, glow=(200, 90, 255)),
    "egg_cosmic":   dict(base=(255, 140, 40), accent=(255, 225, 90), spread=0.05, glow=(255, 150, 50)),
    "egg_absolute": dict(base=(90, 235, 255), accent=(200, 245, 255), spread=0.55, glow=(110, 240, 255)),
}


def hsv_shift(rgb, dh, ds=1.0, dv=1.0):
    arr = np.uint8([[rgb]])
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV_FULL).astype(np.float32)[0, 0]
    hsv[0] = (hsv[0] + dh * 255) % 256
    hsv[1] = min(255, hsv[1] * ds)
    hsv[2] = min(255, hsv[2] * dv)
    out = cv2.cvtColor(np.uint8([[hsv]]), cv2.COLOR_HSV2RGB_FULL)[0, 0]
    return out.astype(np.float32)


def render(key, rows=9, cols=11):
    p = PAL[key]
    w, h = W * SS, H * SS
    cx, cy = w * 0.5, h * 0.52
    half_h = h * 0.40
    R = w * 0.33
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xx - cx
    t = (cy - yy) / half_h                     # +1 top, -1 bottom
    inside_t = np.abs(t) < 1
    tt = np.clip(t, -0.9999, 0.9999)
    squash = 1 - 0.20 * tt                      # narrower top
    r = R * np.sqrt(1 - tt * tt) * squash
    inside = inside_t & (np.abs(x) < r)
    z = np.sqrt(np.clip(r * r - x * x, 0, None))
    # smooth normal of the surface of revolution: (x/r, -dr/dy, z/r)
    eps = 1e-3
    t2 = np.clip(tt + eps, -0.9999, 0.9999)
    r2 = R * np.sqrt(1 - t2 * t2) * (1 - 0.20 * t2)
    drdt = (r2 - r) / (t2 - tt + 1e-9)
    drdy = drdt * (-1.0 / half_h)                # t decreases with y
    rs = np.maximum(r, 1e-3)
    n = np.stack([x / rs, -drdy, z / rs], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    # screen-space y points down; flip so +y is up for lighting
    n[..., 1] *= -1

    # ---- facets: irregular crystal shards (Voronoi cells on the egg surface)
    from scipy.spatial import cKDTree
    rng = np.random.default_rng(11 + len(key))
    NS = 46
    seeds = []
    for _ in range(NS * 3):
        tt_s = rng.uniform(-0.97, 0.97)
        th = rng.uniform(-math.pi * 0.62, math.pi * 0.62)       # front side (+ margin)
        rs_ = R * math.sqrt(1 - tt_s * tt_s) * (1 - 0.20 * tt_s)
        seeds.append((rs_ * math.sin(th), tt_s * half_h, rs_ * math.cos(th), tt_s, th))
    # relax a little (Lloyd-like repulsion) so shards have similar sizes
    pts = np.array([[s_[0], s_[1], s_[2]] for s_ in seeds], np.float32)
    keep = [0]
    for i_ in range(1, len(pts)):
        if all(np.linalg.norm(pts[i_] - pts[k_]) > R * 0.26 for k_ in keep):
            keep.append(i_)
        if len(keep) >= NS:
            break
    seeds = [seeds[k_] for k_ in keep]
    pts = np.array([[s_[0], s_[1], s_[2]] for s_ in seeds], np.float32)
    ns = len(seeds)
    snorm = np.zeros((ns, 3), np.float32)
    for k_, (sx_, sy_, sz_, tt_s, th) in enumerate(seeds):
        eps2 = 1e-3
        r_a = R * math.sqrt(1 - tt_s * tt_s) * (1 - 0.20 * tt_s)
        t_b = min(0.9999, tt_s + eps2)
        r_b = R * math.sqrt(1 - t_b * t_b) * (1 - 0.20 * t_b)
        slope_ = ((r_b - r_a) / (t_b - tt_s)) * (1.0 / half_h)
        nv = np.array([math.sin(th), slope_, math.cos(th)], np.float32)
        nv /= np.linalg.norm(nv)
        tilt_ = rng.normal(0, 0.42, 3).astype(np.float32)
        nv = nv + tilt_
        nv /= np.linalg.norm(nv)
        snorm[k_] = nv
    table = rng.random((ns, 3)).astype(np.float32)
    ys_, xs_ = np.nonzero(inside)
    P = np.stack([x[ys_, xs_], (cy - yy)[ys_, xs_], z[ys_, xs_]], axis=-1)
    tree = cKDTree(pts)
    dd, ii = tree.query(P, k=2)
    idx1 = np.zeros(inside.shape, np.int32); idx1[ys_, xs_] = ii[:, 0]
    d1 = np.zeros(inside.shape, np.float32); d1[ys_, xs_] = dd[:, 0]
    d2 = np.zeros(inside.shape, np.float32); d2[ys_, xs_] = dd[:, 1]
    rnd = table[idx1]
    nc = snorm[idx1]
    nn = nc * 0.9 + n * 0.1
    nn /= np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-9
    gap = (d2 - d1) / (R * 0.11)                    # 0 at a shard border
    d_edge = np.clip(gap, 0, 1) * 0.16
    bev = np.clip(1 - gap, 0, 1)
    fu = fv = np.zeros_like(d1)
    # bevel tilts the normal away from the shard centre (chamfer look)
    away = P.copy()
    cvec = np.zeros(inside.shape + (3,), np.float32)
    cvec[ys_, xs_] = P - pts[ii[:, 0]]
    cvec /= np.linalg.norm(cvec, axis=-1, keepdims=True) + 1e-6
    nb = nn + cvec * (bev[..., None] ** 1.4) * 0.8
    nb /= np.linalg.norm(nb, axis=-1, keepdims=True) + 1e-9
    j = np.floor((tt + 1) * 4)
    theta = np.arctan2(x, z)

    L = np.array([-0.45, 0.65, 0.62], np.float32); L /= np.linalg.norm(L)
    V = np.array([0, 0, 1], np.float32)
    Hh = (L + V); Hh /= np.linalg.norm(Hh)
    diff = np.clip((nb * L).sum(-1), 0, 1)
    spec = np.clip((nb * Hh).sum(-1), 0, 1) ** 38
    spec2 = np.clip((nn * Hh).sum(-1), 0, 1) ** 12
    fres = np.clip(1 - nb[..., 2], 0, 1) ** 2.2

    base = np.array(p["base"], np.float32)
    accent = np.array(p["accent"], np.float32)
    # per-facet colour: hue shift + brightness
    sp = p["spread"]
    hue = (rnd[..., 0] - 0.5) * 2 * sp
    if sp > 0.3:  # iridescent: hue grows with height and position
        hue = (rnd[..., 0] * 0.35 + (tt + 1) * 0.25 + theta * 0.12)
    # build colour by interpolating between a few hue-shifted bases
    def tint(dh):
        return hsv_shift(tuple(int(v) for v in base), dh)
    if sp > 0.3:
        cols_arr = np.stack([cv2.cvtColor(np.uint8([[[ (hu * 255) % 256, 215, 255 ]]]), cv2.COLOR_HSV2RGB_FULL)[0, 0] for hu in np.linspace(0, 1, 16)]).astype(np.float32)
        idx = (np.mod(hue, 1.0) * 15).astype(int)
        col = cols_arr[idx]
        col = col * 0.8 + base * 0.2
    else:
        col = base[None, None, :] * (1 + (rnd[..., 1:2] - 0.5) * 0.45)
        col = col + np.stack([hue * 255, hue * 90, -hue * 120], axis=-1)
    bright = 0.55 + 0.85 * rnd[..., 2]
    shade = 0.22 + 1.05 * diff
    rgb = col * (shade * bright)[..., None]
    rgb = rgb + accent * (fres[..., None] * 1.0)                   # glowing rim
    rgb = rgb + accent * ((0.18 + 0.25 * nb[..., 2])[..., None]) * (rnd[..., 1:2] > 0.35) * 0.55   # inner emission on some facets
    rgb = rgb + 255 * (spec * (0.55 + rnd[..., 2] * 0.9))[..., None]
    rgb = rgb + accent * (spec2 * 0.25)[..., None]
    # bevel edges: light on upper-left, dark grooves
    groove = np.clip(1 - gap / 0.22, 0, 1)
    rgb = rgb * (1 - 0.55 * groove[..., None])
    edge_light = bev * np.clip(nb[..., 1] * 0.5 + 0.5, 0, 1)
    rgb = rgb + accent * (edge_light[..., None] * 0.35)
    rgb = np.clip(rgb, 0, 255)

    alpha = inside.astype(np.float32)
    # soft-ish silhouette is handled by supersampling
    layer = np.dstack([rgb, alpha * 255]).astype(np.float32)

    # ---- outer glow + ground glow
    glow_col = np.array(p["glow"], np.float32)
    mask = cv2.GaussianBlur(alpha, (0, 0), 34 * SS / 3)
    ground = np.zeros((h, w), np.float32)
    cv2.ellipse(ground, (int(cx), int(cy + half_h * 1.02)), (int(R * 1.1), int(R * 0.22)), 0, 0, 360, 1.0, -1)
    ground = cv2.GaussianBlur(ground, (0, 0), 14 * SS / 3)
    glow_a = np.clip(mask * 1.25 + ground * 0.9, 0, 1) * (1 - alpha)
    # composite in premultiplied space, un-premultiply at the very end (EditableImage wants straight alpha)
    a_e = layer[..., 3:4] / 255
    a_g = (glow_a * 190 / 255)[..., None]
    prem = layer[..., :3] * a_e + glow_col * a_g * (1 - a_e)
    alpha_t = a_e + a_g * (1 - a_e)
    # sparkles (4-point stars), additive
    spark = np.zeros((h, w), np.float32)
    for (sx, sy, sz) in [(0.30, 0.22, 1.0), (0.74, 0.36, 0.7), (0.36, 0.78, 0.55), (0.68, 0.08, 0.5)]:
        px, py = int(sx * w), int(sy * h)
        L1 = int(30 * SS * sz)
        yy2, xx2 = np.mgrid[-L1:L1 + 1, -L1:L1 + 1].astype(np.float32)
        star = np.exp(-(np.abs(xx2) * np.abs(yy2)) / (0.9 * SS * sz * 4)) * np.exp(-(xx2 ** 2 + yy2 ** 2) / (L1 * L1 * 0.5))
        y0, x0 = max(py - L1, 0), max(px - L1, 0)
        y1, x1 = min(py + L1 + 1, h), min(px + L1 + 1, w)
        spark[y0:y1, x0:x1] = np.maximum(spark[y0:y1, x0:x1], star[(y0 - py + L1):(y1 - py + L1), (x0 - px + L1):(x1 - px + L1)])
    prem = np.clip(prem + 255 * spark[..., None], 0, 255)
    alpha_t = np.maximum(alpha_t, spark[..., None])
    packed = np.dstack([prem, alpha_t * 255]).astype(np.float32)
    small = cv2.resize(packed, (W, H), interpolation=cv2.INTER_AREA)
    al = np.maximum(small[..., 3:4] / 255, 1e-4)
    straight = np.clip(small[..., :3] / al, 0, 255)
    return np.clip(np.dstack([straight, small[..., 3]]), 0, 255).astype(np.uint8)


def main():
    out_dir = sys.argv[1]
    import os
    os.makedirs(out_dir, exist_ok=True)
    for key in PAL:
        img = render(key)
        bgra = cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
        cv2.imwrite(os.path.join(out_dir, key + ".png"), bgra)
        # preview on a dark purple background
        bg = np.zeros((H, W, 3), np.float32); bg[:] = (40, 20, 70)
        a = img[..., 3:4].astype(np.float32) / 255
        prev = (img[..., :3].astype(np.float32) * a + bg * (1 - a)).astype(np.uint8)
        cv2.imwrite(os.path.join(out_dir, key + "_preview.png"), cv2.cvtColor(prev, cv2.COLOR_RGB2BGR))
        print(key, "ok")


if __name__ == "__main__":
    main()
