"""Склеивает превью поз каждого клипа в одну полосу: python contact_sheet.py"""
import json, os
from PIL import Image, ImageDraw
here = os.path.dirname(os.path.abspath(__file__))
prev = os.path.join(os.path.dirname(here), "previews")
data = json.load(open(os.path.join(here, "new_anims.json")))
for clip, c in data["clips"].items():
    names = []
    for _, p in c["keys"]:
        if p not in names:
            names.append(p)
    tiles = []
    for view in ("34", "front"):
        row = [Image.open(os.path.join(prev, "pose_%s_%s.png" % (n, view))).convert("RGB") for n in names]
        tiles.append(row)
    w, h = tiles[0][0].size
    sheet = Image.new("RGB", (w * len(names), h * 2))
    d = ImageDraw.Draw(sheet)
    for r, row in enumerate(tiles):
        for i, im in enumerate(row):
            sheet.paste(im, (i * w, r * h))
            if r == 0:
                d.text((i * w + 8, 8), names[i], fill=(255, 255, 255))
    sheet.save(os.path.join(prev, "clip_%s.png" % clip))
    print(clip, names)
