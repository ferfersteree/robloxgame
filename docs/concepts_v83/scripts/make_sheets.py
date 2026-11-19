# Builds sheet_dumbbells.png and sheet_stands.png (5x3 with captions) from renders/. Run with system Python (needs Pillow).
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = ['Wooden', 'Stone', 'Bronze', 'Iron', 'Granite', 'Golden', 'Mammoth', 'Crystal',
         'Obsidian', 'Frost', 'Magma', 'Storm', 'Jade', 'Celestial', 'Primal']


def font(size):
    for f in (r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(kind, tile, title, out):
    tw, th = tile
    cap, pad, head = 64, 16, 110
    W = pad + 5 * (tw + pad)
    Hh = head + 3 * (th + cap + pad) + pad
    img = Image.new('RGB', (W, Hh), '#1b1626')
    d = ImageDraw.Draw(img)
    d.text((W // 2, head // 2), title, font=font(54), fill='#f6efe2', anchor='mm', stroke_width=4, stroke_fill='#000000')
    f = font(34)
    missing = []
    for i, nm in enumerate(NAMES):
        n = i + 1
        p = os.path.join(OUT, 'renders', '%s_%02d_%s.png' % (kind, n, nm.lower()))
        x = pad + (i % 5) * (tw + pad)
        y = head + (i // 5) * (th + cap + pad)
        if os.path.exists(p):
            im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
            img.paste(im, (x, y))
        else:
            missing.append(n)
            d.rectangle([x, y, x + tw, y + th], outline='#6b6080', width=3)
        d.text((x + tw // 2, y + th + cap // 2), '%d. %s' % (n, nm), font=f, fill='#ffffff', anchor='mm', stroke_width=3, stroke_fill='#000000')
    img.save(os.path.join(OUT, out))
    return W, Hh, missing


if __name__ == '__main__':
    print(sheet('db', (512, 512), 'SpearHunt V83 - 15 dumbbells', 'sheet_dumbbells.png'))
    print(sheet('st', (640, 400), 'SpearHunt V83 - 15 CAMP GYM stands', 'sheet_stands.png'))
