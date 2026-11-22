# Turn raw toon renders into finished shop illustrations: sticker outline, soft ground shadow, glint stars.
from PIL import Image, ImageFilter, ImageDraw, ImageChops
import sys, os
def star(d, cx, cy, r, col):
    pts=[(cx,cy-r),(cx+r*.22,cy-r*.22),(cx+r,cy),(cx+r*.22,cy+r*.22),(cx,cy+r),(cx-r*.22,cy+r*.22),(cx-r,cy),(cx-r*.22,cy-r*.22)]
    d.polygon(pts,fill=col)
def finish(src, dst, box, shadow=True, glint=True, outline=6, white=0):
    im=Image.open(src).convert('RGBA'); im=im.crop(im.getbbox())
    pad=outline+white+14
    W,H=im.size
    can=Image.new('RGBA',(W+pad*2,H+pad*2+ (14 if shadow else 0)),(0,0,0,0))
    can.alpha_composite(im,(pad,pad))
    a=can.split()[3].point(lambda v:255 if v>20 else 0)
    # sticker: dark outline, then optional white rim outside it
    def grow(mask,n):
        for _ in range(n): mask=mask.filter(ImageFilter.MaxFilter(3))
        return mask
    dark=grow(a,outline)
    layer=Image.new('RGBA',can.size,(0,0,0,0))
    if white:
        w=grow(dark,white); layer.paste((255,255,255,255),mask=w)
    layer.paste((14,20,66,255),mask=dark)
    out=Image.new('RGBA',can.size,(0,0,0,0))
    if shadow:
        sh=Image.new('L',can.size,0); d=ImageDraw.Draw(sh)
        cx=can.size[0]//2; bw=int(W*.42); y=can.size[1]-12
        d.ellipse([cx-bw,y-10,cx+bw,y+8],fill=110)
        sh=sh.filter(ImageFilter.GaussianBlur(6))
        out.paste((8,16,60,255),mask=sh)
    out.alpha_composite(layer); out.alpha_composite(can)
    if glint:
        g=ImageDraw.Draw(out); w,h=out.size
        star(g,int(w*.80),int(h*.2),int(min(w,h)*.085),(255,255,255,235))
        star(g,int(w*.22),int(h*.62),int(min(w,h)*.045),(255,255,255,200))
    out.thumbnail(box,Image.LANCZOS)
    out.save(dst,optimize=True)
if __name__=='__main__':
    os.makedirs('art',exist_ok=True)
    item=lambda n,box=(512,480),**k: finish(f't_{n}.png',f'art/{n}.png',box,**k)
    for n in ['charm','purse','wrap','bag','titan','vip','luck30','coins30','brew30','server15','coins1','coins2','coins3','coins4']: item(n)
    item('spear',(512,512)); item('flyspear',(640,260),shadow=False,glint=False,outline=7)
    for a in ['moonrabbit','rabbit','squirrel','hedgehog','fox','dodo']: item(a+'_R',(420,340),glint=False,outline=6)
    for a in ['squirrel','moonrabbit']: item(a+'_F',(380,380),glint=False)
