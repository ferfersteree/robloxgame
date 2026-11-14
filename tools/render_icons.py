"""Glossy 3D shop icons rendered offline (numpy ray marching over simple shapes), written as RGBA PNGs.
Usage: python tools/render_icons.py <out_dir> [name ...]
The shop draws them at runtime with EditableImage (Client/EggArt); nothing is uploaded to Roblox.
"""
import sys, os, math
import numpy as np
import cv2

SIZE = 176
SS = 3

# ------------------------------------------------------------------ shapes (signed distance functions)


def rot(ax, ay, az):
    ax, ay, az = [math.radians(v) for v in (ax, ay, az)]
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return (rz @ ry @ rx).astype(np.float32)


class Shape:
    def __init__(self, kind, c, size, col, rotd=(0, 0, 0), rnd=0.0, spec=0.7, shine=40, glow=0.0, tex=None):
        self.kind, self.c = kind, np.array(c, np.float32)
        self.size = size
        self.col = np.array(col, np.float32) / 255.0
        self.R = rot(*rotd)
        self.rnd, self.spec, self.shine, self.glow, self.tex = rnd, spec, shine, glow, tex

    def dist(self, P):
        q = (P - self.c) @ self.R
        k = self.kind
        s = self.size
        if k == "sphere":
            return np.linalg.norm(q, axis=-1) - s
        if k == "ell":
            r = np.array(s, np.float32)
            k0 = np.linalg.norm(q / r, axis=-1)
            k1 = np.linalg.norm(q / (r * r), axis=-1)
            return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)
        if k == "box":
            b = np.array(s, np.float32)
            d = np.abs(q) - b + self.rnd
            return np.linalg.norm(np.maximum(d, 0), axis=-1) + np.minimum(d.max(-1), 0) - self.rnd
        if k == "cyl":
            rad, h = s
            d = np.stack([np.linalg.norm(q[:, [0, 2]], axis=-1) - rad + self.rnd, np.abs(q[:, 1]) - h + self.rnd], -1)
            return np.minimum(d.max(-1), 0) + np.linalg.norm(np.maximum(d, 0), axis=-1) - self.rnd
        if k == "torus":
            R, r = s
            t = np.stack([np.linalg.norm(q[:, [0, 2]], axis=-1) - R, q[:, 1]], -1)
            return np.linalg.norm(t, axis=-1) - r
        if k == "cap":  # vertical capsule: radius, half height
            r, h = s
            y = np.clip(q[:, 1], -h, h)
            return np.linalg.norm(q - np.stack([np.zeros_like(y), y, np.zeros_like(y)], -1), axis=-1) - r
        if k == "cone":  # cone along y, apex up: base radius, half height
            r, h = s
            rr = np.linalg.norm(q[:, [0, 2]], axis=-1)
            t = np.clip((q[:, 1] + h) / (2 * h), 0, 1)
            return np.maximum(rr - r * (1 - t), np.maximum(-q[:, 1] - h, q[:, 1] - h)) * 0.8
        raise ValueError(k)

    def color(self, P):
        if self.tex is None:
            return np.broadcast_to(self.col, P.shape)
        return self.tex(P, self.col)


def scene_dist(shapes, P):
    best = None
    ids = None
    for i, sh in enumerate(shapes):
        d = sh.dist(P)
        if best is None:
            best, ids = d, np.zeros(len(P), np.int32)
        else:
            m = d < best
            best = np.where(m, d, best)
            ids = np.where(m, i, ids)
    return best, ids


def smin_dist(shapes, P):
    return scene_dist(shapes, P)[0]


def render(shapes, cam_pos=(0.0, 2.2, 6.2), look=(0, 0.1, 0), fov=26, key_light=(-0.5, 0.85, 0.55), bg_glow=None):
    S = SIZE * SS
    cam = np.array(cam_pos, np.float32)
    look = np.array(look, np.float32)
    fwd = look - cam; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = 1.0 / math.tan(math.radians(fov) / 2)
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    u = (xs + 0.5) / S * 2 - 1
    v = -((ys + 0.5) / S * 2 - 1)
    dirs = fwd[None, :] * f + right[None, :] * u.reshape(-1, 1) + up[None, :] * v.reshape(-1, 1)
    dirs /= np.linalg.norm(dirs, axis=-1, keepdims=True)
    N = dirs.shape[0]
    t = np.full(N, 2.5, np.float32)
    active = np.arange(N)
    hit = np.zeros(N, bool)
    for _ in range(80):
        if len(active) == 0:
            break
        P = cam[None, :] + dirs[active] * t[active, None]
        d = smin_dist(shapes, P)
        h = d < 0.0025
        hit[active[h]] = True
        t[active] += np.maximum(d, 0.002)
        keep = (~h) & (t[active] < 11)
        active = active[keep]
    hi = np.nonzero(hit)[0]
    img = np.zeros((N, 4), np.float32)
    depth = np.full(N, 99, np.float32)
    ident = np.full(N, -1, np.int32)
    if len(hi):
        P = cam[None, :] + dirs[hi] * t[hi, None]
        e = 0.004
        nx = smin_dist(shapes, P + [e, 0, 0]) - smin_dist(shapes, P - [e, 0, 0])
        ny = smin_dist(shapes, P + [0, e, 0]) - smin_dist(shapes, P - [0, e, 0])
        nz = smin_dist(shapes, P + [0, 0, e]) - smin_dist(shapes, P - [0, 0, e])
        n = np.stack([nx, ny, nz], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
        _, ids = scene_dist(shapes, P)
        col = np.zeros((len(hi), 3), np.float32)
        spec = np.zeros(len(hi), np.float32); shine = np.zeros(len(hi), np.float32); glow = np.zeros(len(hi), np.float32)
        for i, sh in enumerate(shapes):
            m = ids == i
            if m.any():
                col[m] = sh.color(P[m])
                spec[m] = sh.spec; shine[m] = sh.shine; glow[m] = sh.glow
        L = np.array(key_light, np.float32); L /= np.linalg.norm(L)
        Vv = -dirs[hi]
        H = L[None, :] + Vv; H /= np.linalg.norm(H, axis=-1, keepdims=True)
        diff = np.clip((n * L).sum(-1), 0, 1)
        fill = np.clip((n * np.array([0.7, 0.2, 0.4], np.float32)).sum(-1), 0, 1) * 0.25
        sp = np.clip((n * H).sum(-1), 0, 1) ** shine * spec
        fres = np.clip(1 - (n * Vv).sum(-1), 0, 1) ** 2.5
        # ambient occlusion: how much free space along the normal
        ao = np.ones(len(hi), np.float32)
        for k, hk in enumerate((0.08, 0.2, 0.4)):
            dd = smin_dist(shapes, P + n * hk)
            ao -= np.clip(hk - dd, 0, 1) * (1.0 / (1 + k)) * 0.9
        ao = np.clip(ao, 0.25, 1)
        amb = np.where(n[:, 1:2] > 0, 1, 0.55) * np.array([0.52, 0.46, 0.72], np.float32)[None, :] * 0.55
        rgb = col * (amb * ao[:, None] + diff[:, None] * 0.95 + fill[:, None]) + sp[:, None] + fres[:, None] * np.array([0.7, 0.55, 1.0], np.float32) * 0.28
        rgb = rgb + col * glow[:, None]
        img[hi, :3] = np.clip(rgb, 0, 1)
        img[hi, 3] = 1
        depth[hi] = t[hi]
        ident[hi] = ids
    rgb = img[:, :3].reshape(S, S, 3)
    a = img[:, 3].reshape(S, S)
    dep = depth.reshape(S, S)
    idm = ident.reshape(S, S)
    # outline: depth jumps and object changes
    gy, gx = np.gradient(dep)
    edge = (np.abs(gx) + np.abs(gy) > 0.12) | (np.abs(np.diff(idm, axis=0, append=idm[-1:]) ) > 0) | (np.abs(np.diff(idm, axis=1, append=idm[:, -1:])) > 0)
    edge = cv2.dilate(edge.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & (a > 0)
    rgb = np.where(edge[..., None], rgb * 0.45 + np.array([0.05, 0.0, 0.12], np.float32), rgb)
    out = np.dstack([rgb * a[..., None], a])
    # soft shadow blob under the object (premultiplied)
    sh = np.zeros((S, S), np.float32)
    ys_, xs_ = np.nonzero(a > 0)
    if len(ys_):
        cx_, by_ = xs_.mean(), ys_.max()
        wd = max(10, (xs_.max() - xs_.min()) * 0.5)
        cv2.ellipse(sh, (int(cx_), int(by_ - wd * 0.07)), (int(wd * 0.95), int(wd * 0.2)), 0, 0, 360, 1.0, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), wd * 0.12) * 0.5
    a_t = np.maximum(a, sh * (1 - a))
    prem = out[..., :3] + (np.array([0.1, 0.0, 0.2], np.float32) * sh[..., None]) * (1 - a[..., None])
    packed = np.dstack([prem * 255, a_t * 255]).astype(np.float32)
    small = cv2.resize(packed, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    al = np.maximum(small[..., 3:4] / 255, 1e-4)
    straight = np.clip(small[..., :3] / al, 0, 255)
    return np.clip(np.dstack([straight, small[..., 3]]), 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ scenes
GOLD = (255, 196, 40)
GOLD2 = (255, 226, 110)


def coin(c, tilt=(0, 0, 0)):
    return [Shape("cyl", c, (0.52, 0.065), GOLD, tilt, rnd=0.03, spec=1.0, shine=60),
            Shape("cyl", (c[0], c[1] + 0.012, c[2]), (0.38, 0.07), GOLD2, tilt, rnd=0.02, spec=0.9, shine=60)] if tilt == (0, 0, 0) else \
           [Shape("cyl", c, (0.52, 0.065), GOLD, tilt, rnd=0.03, spec=1.0, shine=60),
            Shape("cyl", c, (0.38, 0.07), GOLD2, tilt, rnd=0.02, spec=0.9, shine=60)]


def stack(x, z, n, y0=-0.55):
    out = []
    for i in range(n):
        out += coin((x, y0 + i * 0.145, z))
    return out


def scene_coins(n):
    sh = []
    if n == 1:
        sh += stack(0, 0, 5, -0.3) + coin((0.55, -0.62, 0.55), (0, 0, 0))[:1]
        sh += [Shape("cyl", (-0.55, -0.62, 0.45), (0.52, 0.065), GOLD, (0, 0, 0), rnd=0.03, spec=1.0)]
    elif n == 2:
        sh += stack(-0.45, 0.0, 6, -0.45) + stack(0.55, 0.15, 4, -0.5) + [Shape("cyl", (0.1, -0.6, 0.85), (0.52, 0.065), GOLD, (0, 20, 0), rnd=0.03, spec=1.0)]
        sh += [Shape("cyl", (0.1, -0.35, 0.95), (0.5, 0.065), GOLD, (68, 0, 8), rnd=0.03, spec=1.0), Shape("cyl", (0.1, -0.34, 0.97), (0.36, 0.07), GOLD2, (68, 0, 8), rnd=0.02)]
    elif n == 3:
        sh += stack(-0.8, -0.1, 5, -0.5) + stack(0.0, 0.1, 8, -0.5) + stack(0.8, -0.1, 6, -0.5)
        sh += [Shape("cyl", (-0.4, -0.62, 0.9), (0.52, 0.065), GOLD, (0, 15, 0), rnd=0.03), Shape("cyl", (0.45, -0.62, 0.85), (0.52, 0.065), GOLD, (0, -10, 0), rnd=0.03)]
    else:
        # sack of coins with a pile in front
        sh += [Shape("ell", (0, -0.1, -0.2), (0.95, 1.0, 0.85), (172, 118, 60), rnd=0, spec=0.25, shine=12),
               Shape("cyl", (0, 0.82, -0.2), (0.34, 0.12), (150, 98, 46), rnd=0.05, spec=0.25),
               Shape("torus", (0, 0.72, -0.2), (0.36, 0.07), (230, 70, 70), spec=0.5)]
        sh += stack(-0.75, 0.75, 4, -0.62) + stack(0.1, 0.95, 5, -0.62) + stack(0.85, 0.7, 3, -0.62)
        sh += [Shape("cyl", (0.4, -0.7, 1.45), (0.52, 0.065), GOLD, (0, 25, 0), rnd=0.03), Shape("cyl", (-0.5, -0.7, 1.4), (0.52, 0.065), GOLD, (0, -15, 0), rnd=0.03)]
    return sh


def flask(col, liquid2=None, star=True):
    sh = [Shape("sphere", (0, -0.15, 0), 0.82, col, spec=1.0, shine=70, glow=0.18),
          Shape("cyl", (0, 0.72, 0), (0.27, 0.34), tuple(int(v * 0.5 + 120) for v in col), rnd=0.05, spec=1.0, shine=70),
          Shape("torus", (0, 1.06, 0), (0.3, 0.07), (235, 245, 255), spec=1.0),
          Shape("cyl", (0, 1.2, 0), (0.22, 0.17), (176, 120, 66), rnd=0.05, spec=0.3, shine=14),
          Shape("sphere", (-0.32, 0.12, 0.62), 0.14, (255, 255, 255), spec=1.0, shine=90, glow=0.5),
          Shape("sphere", (0.2, -0.5, 0.74), 0.07, (255, 255, 255), spec=1.0, glow=0.5),
          Shape("sphere", (0.45, -0.32, 0.62), 0.05, (255, 255, 255), spec=1.0, glow=0.5)]
    if star:
        sh += [Shape("ell", (0.0, -0.18, 0.78), (0.3, 0.3, 0.07), (255, 240, 150), spec=1.0, glow=0.4)]
    return sh


def scene_gift():
    pink = (240, 70, 160); gold = GOLD
    return [Shape("box", (0, -0.35, 0), (0.95, 0.6, 0.95), pink, rnd=0.08, spec=0.8),
            Shape("box", (0, 0.35, 0), (1.05, 0.22, 1.05), (255, 100, 180), rnd=0.07, spec=0.8),
            Shape("box", (0, -0.2, 0), (0.16, 0.8, 0.98), gold, rnd=0.03, spec=1.0),
            Shape("box", (0, 0.36, 0), (0.16, 0.24, 1.08), gold, rnd=0.03, spec=1.0),
            Shape("box", (0, -0.2, 0), (0.98, 0.8, 0.16), gold, rnd=0.03, spec=1.0),
            Shape("ell", (-0.42, 0.78, 0), (0.42, 0.3, 0.2), gold, (0, 0, 25), spec=1.0),
            Shape("ell", (0.42, 0.78, 0), (0.42, 0.3, 0.2), gold, (0, 0, -25), spec=1.0),
            Shape("sphere", (0, 0.72, 0), 0.2, GOLD2, spec=1.0)]


def scene_crown(gem=((230, 50, 70), (60, 140, 255), (70, 220, 110))):
    sh = [Shape("cyl", (0, -0.35, 0), (0.95, 0.28), GOLD, rnd=0.1, spec=1.0, shine=70),
          Shape("torus", (0, -0.62, 0), (0.95, 0.07), GOLD2, spec=1.0), Shape("torus", (0, -0.1, 0), (0.95, 0.06), GOLD2, spec=1.0)]
    for i in range(5):
        a = i / 5 * 2 * math.pi
        x, z = math.sin(a) * 0.72, math.cos(a) * 0.72
        sh += [Shape("cone", (x, 0.3, z), (0.3, 0.55), GOLD, spec=1.0, shine=70), Shape("sphere", (x, 0.92, z), 0.15, GOLD2, spec=1.0)]
    for i, g in enumerate(gem):
        a = (i - 1) * 0.9
        sh += [Shape("sphere", (math.sin(a) * 0.95, -0.34, math.cos(a) * 0.95), 0.17, g, spec=1.0, shine=90, glow=0.25)]
    return sh


def scene_ball():
    return [Shape("cyl", (0, -0.85, 0), (0.85, 0.2), (150, 100, 60), rnd=0.08, spec=0.5),
            Shape("torus", (0, -0.62, 0), (0.6, 0.12), GOLD, spec=1.0),
            Shape("sphere", (0, 0.2, 0), 0.9, (110, 150, 255), spec=1.0, shine=90, glow=0.35),
            Shape("sphere", (0, 0.15, 0), 0.5, (190, 215, 255), spec=0.6, glow=0.6),
            Shape("sphere", (-0.35, 0.55, 0.7), 0.16, (255, 255, 255), spec=1.0, glow=0.7),
            Shape("ell", (0.0, 0.15, 0.48), (0.22, 0.22, 0.05), (255, 240, 150), spec=1.0, glow=0.8)]


def scene_clover():
    g = (70, 200, 70)
    sh = []
    for a, dz in ((45, 1), (135, 1), (225, 1), (315, 1)):
        x, y = math.cos(math.radians(a)) * 0.5, math.sin(math.radians(a)) * 0.5
        sh += [Shape("ell", (x, y + 0.2, 0), (0.52, 0.52, 0.22), g, (0, 0, a), spec=0.9, shine=50)]
    sh += [Shape("sphere", (0, 0.2, 0.18), 0.17, GOLD, spec=1.0), Shape("cap", (0.1, -0.8, 0), (0.1, 0.45), (50, 150, 60), (0, 0, 15), spec=0.6)]
    return sh


def globe_tex(P, col):
    n = np.sin(P[:, 0] * 5 + 1) * np.sin(P[:, 1] * 4 + 2) + np.sin(P[:, 2] * 6) * 0.6 + np.sin(P[:, 0] * 11 + P[:, 1] * 7) * 0.3
    land = (n > 0.55)[:, None]
    return np.where(land, np.array([0.35, 0.8, 0.35], np.float32), np.array([0.2, 0.5, 1.0], np.float32))


def scene_globe():
    return [Shape("cyl", (0, -1.0, 0), (0.6, 0.12), (150, 100, 60), rnd=0.05, spec=0.4),
            Shape("cap", (0, -0.7, 0), (0.1, 0.3), GOLD, spec=1.0),
            Shape("sphere", (0, 0.2, 0), 0.9, (60, 130, 255), spec=0.9, shine=50, glow=0.1, tex=globe_tex),
            Shape("torus", (0, 0.2, 0), (1.08, 0.07), GOLD, (62, 0, 28), spec=1.0)]


def scene_anvil():
    return [Shape("box", (0, -0.6, 0), (0.7, 0.2, 0.5), (90, 90, 110), rnd=0.05, spec=0.8),
            Shape("box", (0, -0.2, 0), (0.45, 0.25, 0.4), (110, 112, 135), rnd=0.05, spec=0.8),
            Shape("box", (0, 0.2, 0), (1.0, 0.25, 0.5), (150, 152, 175), rnd=0.06, spec=1.0, shine=60),
            Shape("cone", (-1.15, 0.2, 0), (0.28, 0.32), (150, 152, 175), (0, 0, 90), spec=1.0),
            Shape("cap", (0.55, 0.85, 0.2), (0.09, 0.55), (150, 100, 55), (0, 0, 30), spec=0.3),
            Shape("box", (0.22, 1.35, 0.2), (0.3, 0.2, 0.2), (200, 205, 225), (0, 0, 30), rnd=0.04, spec=1.0, shine=60),
            Shape("sphere", (-0.2, 0.62, 0.3), 0.09, (255, 190, 80), spec=1.0, glow=0.8)]


def scene_scales():
    return [Shape("cyl", (0, -0.85, 0), (0.6, 0.12), (150, 100, 60), rnd=0.05, spec=0.4),
            Shape("cap", (0, -0.1, 0), (0.09, 0.78), GOLD, spec=1.0),
            Shape("box", (0, 0.72, 0), (1.15, 0.07, 0.07), GOLD, (0, 0, 5), rnd=0.03, spec=1.0),
            Shape("sphere", (0, 0.76, 0), 0.14, GOLD2, spec=1.0),
            Shape("cap", (-1.1, 0.2, 0), (0.025, 0.5), (230, 230, 240), (0, 0, 8), spec=0.8),
            Shape("cap", (1.1, 0.2, 0), (0.025, 0.5), (230, 230, 240), (0, 0, -8), spec=0.8),
            Shape("cyl", (-1.2, -0.28, 0), (0.45, 0.06), (210, 215, 235), rnd=0.05, spec=1.0),
            Shape("cyl", (1.2, -0.28, 0), (0.45, 0.06), (210, 215, 235), rnd=0.05, spec=1.0),
            Shape("cyl", (-1.2, -0.17, 0), (0.28, 0.05), GOLD, rnd=0.02, spec=1.0), Shape("cyl", (1.2, -0.17, 0), (0.28, 0.05), GOLD, rnd=0.02, spec=1.0)]


ICONS = {
    "coins1": (lambda: scene_coins(1), {}), "coins2": (lambda: scene_coins(2), {}), "coins3": (lambda: scene_coins(3), {}),
    "coins4": (lambda: scene_coins(4), dict(cam_pos=(0, 2.8, 7.4))),
    "fortune20": (lambda: flask((255, 190, 40)), {}), "jackpot20": (lambda: flask((255, 80, 150)), {}), "fair30": (lambda: flask((40, 210, 200)), {}),
    "wrap": (scene_gift, {}), "vip": (scene_crown, {}), "founder": (lambda: scene_crown(((190, 90, 255), (90, 170, 255), (255, 110, 220))), {}),
    "insight": (scene_ball, {}), "charm": (scene_clover, dict(cam_pos=(0, 0.6, 6.8))), "server15": (scene_globe, {}),
    "smith": (scene_anvil, dict(cam_pos=(1.0, 2.4, 7.2))), "broker": (scene_scales, dict(cam_pos=(0, 1.6, 7.6))),
}


def main():
    out_dir = sys.argv[1]
    names = sys.argv[2:] or list(ICONS)
    os.makedirs(out_dir, exist_ok=True)
    for n in names:
        fn, kw = ICONS[n]
        img = render(fn(), **kw)
        cv2.imwrite(os.path.join(out_dir, n + ".png"), cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))
        bg = np.zeros((SIZE, SIZE, 3), np.float32); bg[:] = (60, 28, 110)
        a = img[..., 3:4].astype(np.float32) / 255
        cv2.imwrite(os.path.join(out_dir, n + "_preview.png"), cv2.cvtColor((img[..., :3] * a + bg * (1 - a)).astype(np.uint8), cv2.COLOR_RGB2BGR))
        print(n, "ok", flush=True)


if __name__ == "__main__":
    main()
