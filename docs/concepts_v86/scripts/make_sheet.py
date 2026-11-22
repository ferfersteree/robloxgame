# Builds sheet_spears.png (all spears) or a batch preview sheet from renders\. Run with system Python (Pillow).
# usage: python make_sheet.py            -> sheet_spears.png (all 46)
#        python make_sheet.py 2 12 batch1 -> preview_batch1.png (levels 2..12)
import os, sys
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SP = [('stick', 'Stone-tipped Spear'), ('bone', 'Bone Spear'), ('bronze', 'Bronze Spear'), ('feather', 'Feathered Spear'),
      ('iron', 'Iron Spear'), ('obsidian', 'Obsidian Spear'), ('crystal', 'Crystal Spear'), ('fire', 'Fire Spear'),
      ('ice', 'Ice Spear'), ('star', 'Star Spear'), ('amber_sting', 'Amber Sting'), ('solar_trident', 'Solar Trident'),
      ('canyon_hook', 'Canyon Hook'), ('condor_quill', 'Condor Quill'), ('mirage_lance', 'Mirage Lance'),
      ('scorpion_sting', 'Scorpion Sting'), ('emerald_vine', 'Emerald Vine'), ('temple_guard', 'Temple Guard'),
      ('mangrove_root', 'Mangrove Root'), ('hydra_fangs', 'Hydra Fangs'), ('storm_trident', 'Storm Trident'),
      ('thunder_split', 'Thunder Splitter'), ('coral_branch', 'Coral Branch'), ('tide_crest', 'Tide Crest'),
      ('abyss_anchor', 'Abyssal Anchor'), ('leviathan_fang', 'Leviathan Fang'), ('ash_saw', 'Ash Saw'),
      ('golem_heart', 'Golem Heart'), ('magma_tongue', 'Magma Tongue'), ('phoenix_wing', 'Phoenix Wing'),
      ('amethyst_geode', 'Amethyst Geode'), ('quartz_needle', 'Quartz Needle'), ('lunar_crescent', 'Lunar Crescent'),
      ('aurora_weave', 'Aurora Weave'), ('cloud_feather', 'Cloud Feather'), ('sky_harpoon', 'Sky Harpoon'),
      ('rift_shards', 'Rift Shards'), ('void_scissors', 'Void Shears'), ('astral_armillary', 'Astral Armillary'),
      ('singularity_spire', 'Singularity Spire'), ('gear_pike', 'Gearwork Pike'), ('spore_halberd', 'Sporebloom Halberd'),
      ('bone_glaive', 'Boneforged Glaive'), ('pearl_lance', 'Citadel Pearl Lance'), ('rift_conductor', 'Rift Conductor'),
      ('primal_fang', 'Primordial Fang')]


def font(size):
    for f in (r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(levels, out, title, cols=8, tile=360):
    cap, pad, head = 56, 14, 100
    rows = (len(levels) + cols - 1) // cols
    W = pad + cols * (tile + pad)
    H = head + rows * (tile + cap + pad) + pad
    img = Image.new('RGB', (W, H), '#1b1626')
    d = ImageDraw.Draw(img)
    d.text((W // 2, head // 2), title, font=font(50), fill='#f6efe2', anchor='mm', stroke_width=4, stroke_fill='#000000')
    f = font(24)
    missing = []
    for i, n in enumerate(levels):
        sid, nm = SP[n - 1]
        p = os.path.join(OUT, 'renders', 'sp_%02d_%s.png' % (n, sid))
        x = pad + (i % cols) * (tile + pad)
        y = head + (i // cols) * (tile + cap + pad)
        if os.path.exists(p):
            img.paste(Image.open(p).convert('RGB').resize((tile, tile), Image.LANCZOS), (x, y))
        else:
            missing.append(n)
            d.rectangle([x, y, x + tile, y + tile], outline='#6b6080', width=3)
        d.text((x + tile // 2, y + tile + cap // 2), '%d. %s' % (n, nm), font=f, fill='#ffffff', anchor='mm', stroke_width=3, stroke_fill='#000000')
    img.save(os.path.join(OUT, out))
    return W, H, missing


if __name__ == '__main__':
    if len(sys.argv) >= 4:
        a, b, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
        lv = [n for n in range(a, b + 1)]
        print(sheet(lv, 'preview_%s.png' % tag, 'SpearHunt V86 - spears %d-%d' % (a, b), cols=min(6, len(lv)), tile=400))
    else:
        print(sheet(list(range(1, 47)), 'sheet_spears.png', 'SpearHunt V86 - 46 spears'))
