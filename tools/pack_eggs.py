"""Packs the rendered PNGs (tools/render_eggs.py, tools/render_icons.py) into ModuleScript sources for Client/EggArt.
Usage: python tools/pack_eggs.py <png_dir> <out_dir> [scale] [crop]   (every <key>.png in the folder; previews are skipped)
Each output file `<key>.lua` is `return { w=, h=, adler=, z="<base64 of raw deflate of RGBA bytes>" }`.
A Studio script source is limited to 200,000 characters, so a picture whose base64 is longer than 150,000
characters is split: `<key>.lua` then has n= and `<key>.1.lua`, `<key>.2.lua`, ... hold the chunks
(they become child ModuleScripts named "1", "2", ... under the module `<key>`).
"""
import sys, os, zlib, base64
import cv2

CHUNK = 150000


def main():
    src, out = sys.argv[1], sys.argv[2]
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
    crop = len(sys.argv) > 4 and sys.argv[4] == "crop"   # trim empty margins (icons), keep the glow (eggs)
    os.makedirs(out, exist_ok=True)
    keys = sorted(f[:-4] for f in os.listdir(src) if f.endswith(".png") and not f.endswith("_preview.png"))
    for k in keys:
        im = cv2.imread(os.path.join(src, k + ".png"), cv2.IMREAD_UNCHANGED)
        if crop:
            ys, xs = (im[..., 3] > 24).nonzero()
            pad = 4
            y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, im.shape[0])
            x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, im.shape[1])
            im = im[y0:y1, x0:x1]
        if scale != 1:
            im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        rgba = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA)
        raw = rgba.tobytes()
        co = zlib.compressobj(9, zlib.DEFLATED, -15)  # raw deflate, no zlib header
        z = co.compress(raw) + co.flush()
        b64 = base64.b64encode(z).decode()
        w, h, ad = im.shape[1], im.shape[0], zlib.adler32(raw)
        nl = "\n"
        if len(b64) <= CHUNK:
            with open(os.path.join(out, k + ".lua"), "w", encoding="ascii", newline="") as f:
                f.write('return { w = %d, h = %d, adler = %d, z = "%s" }%s' % (w, h, ad, b64, nl))
            chunks = 1
        else:
            parts = [b64[i:i + CHUNK] for i in range(0, len(b64), CHUNK)]
            with open(os.path.join(out, k + ".lua"), "w", encoding="ascii", newline="") as f:
                f.write("return { w = %d, h = %d, adler = %d, n = %d }%s" % (w, h, ad, len(parts), nl))
            for i, part in enumerate(parts, 1):
                with open(os.path.join(out, "%s.%d.lua" % (k, i)), "w", encoding="ascii", newline="") as f:
                    f.write('return "%s"%s' % (part, nl))
            chunks = len(parts)
        print(k, w, h, "raw", len(raw), "deflate", len(z), "base64", len(b64), "chunks", chunks)


if __name__ == "__main__":
    main()
