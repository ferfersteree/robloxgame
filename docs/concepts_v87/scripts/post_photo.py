# labels on the biome photo + studs_tile.png (run with system Python: Pillow + numpy)
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAR = {0: (255, 255, 255), 1: (200, 200, 200), 2: (110, 220, 110), 3: (90, 170, 255), 4: (200, 120, 255), 5: (255, 214, 40), 6: (255, 70, 60)}


def font(sz):
    for f in ('arialbd.ttf', 'segoeuib.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(f, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def label(raw, labels, out, title):
    im = Image.open(raw).convert('RGB')
    d = ImageDraw.Draw(im, 'RGBA')
    f1, f3 = font(30), font(40)
    try:
        f2 = ImageFont.truetype('seguisym.ttf', 22)
    except Exception:
        f2 = font(22)
    placed = []
    labs = sorted(json.load(open(labels)), key=lambda l: -l['rarity'])
    for lb in labs:
        x, y = lb['x'], lb['y']
        t1 = lb['name']
        t2 = ('R%d ' % lb['rarity'] + '★' * lb['rarity']) if lb['rarity'] else ''
        w1 = d.textlength(t1, font=f1)
        w2 = d.textlength(t2, font=f2) if t2 else 0
        w = max(w1, w2) + 28
        h = 74 if t2 else 44
        x0 = min(max(x - w / 2, 8), im.width - w - 8)
        y0 = max(y - h, 8)
        # keep labels from covering each other: move up until free
        def hits(xx, yy):
            return [r for r in placed if xx < r[2] + 6 and r[0] < xx + w + 6 and yy < r[3] + 6 and r[1] < yy + h + 6]
        if hits(x0, y0):
            # first try sliding sideways (away from the picture centre), then upwards
            side = -1 if x < im.width / 2 else 1
            for step in range(1, 12):
                xx = x0 + side * step * 24
                if 8 <= xx <= im.width - w - 8 and not hits(xx, y0):
                    x0 = xx
                    break
            else:
                for _ in range(20):
                    hit = hits(x0, y0)
                    if not hit:
                        break
                    y0 = max(8, min(r[1] for r in hit) - h - 8)
        placed.append((x0, y0, x0 + w, y0 + h))
        col = RAR[lb['rarity']]
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 12, fill=(28, 20, 34, 215), outline=col + (255,), width=3)
        d.text((x0 + (w - w1) / 2, y0 + 5), t1, font=f1, fill=(255, 255, 255, 255))
        if t2:
            d.text((x0 + (w - w2) / 2, y0 + 42), t2, font=f2, fill=col + (255,))
    tw = d.textlength(title, font=f3)
    d.rounded_rectangle((24, 20, 24 + tw + 36, 80), 14, fill=(28, 20, 34, 215))
    d.text((42, 26), title, font=f3, fill=(255, 255, 255, 255))
    im.save(out)


def studs_tile(out, n=512, studs=4):
    """seamless grey stud overlay: 4 studs across, 2x2-stud checker cells (same maths as the SH_Studs node group)"""
    y, x = np.mgrid[0:n, 0:n]
    p = np.stack([(x + 0.5) / n * studs, (y + 0.5) / n * studs], -1)
    f = np.abs(p - np.floor(p) - 0.5) - 0.2
    dd = np.linalg.norm(np.maximum(f, 0), axis=-1) - 0.1

    def ss(e0, e1, v):
        t = np.clip((v - e0) / (e1 - e0), 0, 1)
        return t * t * (3 - 2 * t)
    inside = ss(0.035, -0.035, dd)
    ring = ss(0.045, 0.0, np.abs(dd))
    par = (np.floor(p[..., 0] / 2) + np.floor(p[..., 1] / 2)) % 2
    v = (1 + 0.07 * (2 * par - 1)) * (1 - 0.05 * inside) * (1 - 0.2 * ring)
    # soft bevel light: brighter top-left edge of the stud, darker bottom-right
    gy, gx = np.gradient(inside)
    v = v + (-(gx + gy)) * 0.9
    g = np.clip(v * 0.82 * 255, 0, 255).astype(np.uint8)
    Image.fromarray(g, 'L').convert('RGB').save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'label':
        label(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        studs_tile(sys.argv[2])
