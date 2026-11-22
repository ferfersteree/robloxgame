# compose contact tiles into labelled sheets: python sheet.py out.png [filter...]
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
d = os.path.join(os.environ['TEMP'], 'v87_contact')
files = sorted(glob.glob(os.path.join(d, '*.png')))
flt = sys.argv[2:]
if flt:
    files = [f for f in files if any(x in os.path.basename(f) for x in flt)]
cols = 8
t = 240
rows = (len(files) + cols - 1) // cols
im = Image.new('RGB', (cols * t, rows * (t + 22)), (30, 30, 36))
dr = ImageDraw.Draw(im)
try:
    fn = ImageFont.truetype('arial.ttf', 15)
except Exception:
    fn = ImageFont.load_default()
for i, f in enumerate(files):
    x, y = (i % cols) * t, (i // cols) * (t + 22)
    im.paste(Image.open(f).convert('RGB').resize((t, t)), (x, y))
    dr.text((x + 4, y + t + 2), os.path.basename(f)[:-4], font=fn, fill=(255, 255, 255))
im.save(sys.argv[1])
print(len(files), im.size)
