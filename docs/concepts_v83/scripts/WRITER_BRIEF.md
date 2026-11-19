# Brief: write Blender builder scripts for SpearHunt gym dumbbells + stands (V83)

You write Python builder scripts only. You CANNOT run Blender; do not try to launch it, do not touch any file outside this `scripts/` folder, do not edit existing files (gymlib.py, db_01/08/15.py, st_01/08/15.py, stage.py). Do not use any Roblox skills. Just create the new files assigned to you.

## Read first (in this folder)
- `gymlib.py` — the ONLY API you may use. Read every helper signature and body carefully: begin, fx, toon, glow, ghost, lathe, cyl, sphere, cone, torus, box, rock, crystal, tube, coil, arc_pts, star, leaf, flame, text, zigzag, bolt, aim, radial, stats, display. No `bpy.ops`, no modifiers, no image textures. Small pure-python helper functions inside your file are fine.
- `db_08.py`, `db_15.py` — approved reference dumbbells (quality bar and coding style).
- `st_01.py`, `st_08.py`, `st_15.py` — approved reference stands. NOTE: they use a legacy `drop(DROP)` trick; you must NOT use drop(). Write your stand directly in final coordinates.

## Style
Anime / cartoon: juicy flat colours, chunky rounded exaggerated forms, 3-tone toon materials (`toon`), thick dark outline (automatic), glow via `glow` (Roblox Neon) and soft auras via `ghost`. Each level must be recognisable by its BLACK SILHOUETTE alone, not just colour: give it unique protruding shapes. Every dumbbell is an art object, never "a handle and two discs".

## Files per level NN (two files)

### db_NN.py

```python
from gymlib import *
BG = '#rrggbb'          # render background: light colour for low levels, dark saturated colour for glowing levels
NAME = 'DB_NN_Name'     # exact collection name given in your assignment
def mats():
    return dict(...)    # toon/glow materials, shared with the stand
def build():
    begin(NAME, ol=0.03)
    # main model
    fx(True)
    # effects (separate objects, never part of the main model)
    fx(False)
    return stats(NAME)
```

Rules for the dumbbell:
- 1 unit = 1 stud. Bar along X, up = Z, origin at grip centre (0,0,0). Total length along X = L from your assignment (plus or minus 0.1).
- Handle radius 0.15. The zone |x| < 0.5 must contain ONLY the handle and thin grip detail with radius <= 0.185 (wrap coil, thin rings). Collars and heads start at |x| >= 0.56.
- Heads: layered, chamfered plates or bodies (multi-point lathe profiles, not plain cylinders), an ornament or emblem on the plates, end caps, collar, theme details, at least 3 accent colours. Build both heads with `for s in (-1, 1)`; for lathe-along-X parts mirror with `scale=(s, 1, 1)`, for placed parts multiply x by s.
- 30-70 separate objects in the main model; total <= 7000 triangles. Estimate as you go: lathe = 2*segs*len(profile); bevelled box = 100 (bsegs=1: 44); crystal = 24-36; sphere(8,5) = 80; cone(6) = 18; tube = 2*segs*len(pts); coil = 2*segs*turns*steps; torus = 2*segs*rsegs; rock sub=1: 80, sub=2: 320. Keep segs modest (8-16).
- Head radius including decor about 0.6-1.0, growing slowly with level. Protrusions (horns, spikes, tusks) may go further, but keep the whole model within about -1.5..1.5 in Y and -1.2..+2.0 in Z.
- FX amount is given in your assignment. FX limits: glow strength <= 3.5; `ghost` alpha <= 0.12 and strength <= 1.2 (stronger values wash out the model). Name FX objects `fx_*`.
- Emissive parts that belong to the model itself (runes, lava cracks, eyes) may be in the main model with `glow(...)` strength <= 3.
- Material names are global: prefix yours with the theme (for example `toon('iron_plate', ...)`). You may reuse these existing ones with exactly these arguments: `toon('gold', '#ffcf4d', shade='#c2742a', light='#fff2a6', spec=1.0)`, `toon('bone', '#f6e8c8', shade='#b08f78', light='#ffffff', spec=0.5)`, `toon('silver', '#dfe6f7', shade='#7f86c4', light='#ffffff', spec=1.0)`, `glow('spark_white', '#ffffff', 2.5)`.

### st_NN.py

```python
from gymlib import *
import db_NN
NAME = 'ST_NN_Name'
T = 1.3                                        # deck top height, 1.2-1.6
def build():
    begin(NAME, ol=0.04)
    M = db_NN.mats()
    s = stats(db_NN.NAME)                      # the dumbbell is already built when this runs
    half = s['size'][0] / 2
    cx = half + 0.2                            # pair centres at x = -cx and +cx
    hz = T + 0.1 - s['min'][2]                 # handle height so the dumbbell clears the deck
    top = hz + s['max'][2]                     # highest point of the pair
    # main model ... cradles ... sign
    fx(True)
    # effects
    fx(False)
    display(NAME, db_NN.NAME, [((-cx, 0, hz), (0, 0, 0)), ((cx, 0, hz), (0, 0, 0))], [], (T,))
    return stats(NAME)
```

The stand is a "CAMP GYM" display rack on the player's plot. It holds ONLY the current pair of dumbbells: two full-size dumbbells side by side along X. NO shelves for other levels.
- Origin in the middle of the base on the floor: z=0 is the floor, nothing below z=0. Front faces -Y (the player walks up from -Y): nothing may stick out beyond y = -1.6, and nothing may stand in front of the pair and hide it.
- Footprint about 10 wide (X) by 3 deep (Y). If the pair needs more (2*L + 0.6 > 9.6) widen up to 11.4. Main model height <= 5.5.
- A deck, altar or table top at height T. Build 2 cradles per dumbbell under its handle at x = cx-0.42 and cx+0.42 (and mirrored), y=0, reaching up to about hz - 0.15: forks, claws, hooks or pedestal posts in the level's theme. The pair must be the main accent.
- A sign with mesh text: `text('sign_text', 'CAMP GYM', 0.58, 0.05, material, loc=(0, y, z), rot=(90, 0, 0))`. It is about 4.3 wide and 0.6 tall and faces -Y. Put it on a plaque either behind and above the pair (plaque at y about +1.0..1.2, text 0.1 in front of the plaque face, z >= top + 0.5 but keep total height <= 5.5; if that does not fit, use the other option) or on the front face of the base/altar below the deck. The dumbbells must not hide it.
- Same theme, materials, colours and effect types as the dumbbell of this level (reuse `db_NN.mats()`), plus extra materials if needed.
- Unique silhouette per level: canopy, pillars, totems, horns, rings, arches, spires and so on. Richness grows with level: low levels rough and simple; middle levels carved stone, metal, torches; levels 12-14 a shrine with floating parts, glow and aura.
- 65-110 separate objects, <= 12000 triangles (the text is about 900). FX in the fx(True) block, same limits as for the dumbbell.

## API gotchas (the scripts are run unseen, so be exact)
- `lathe(name, prof, mat, segs, axis, caps=True, **kw)`: prof is a list of (axial, radius). A first or last point with radius 0 closes that end. Radii must be >= 0.
- Placement kwargs on every primitive: `loc=(x,y,z)`, `rot=(degX,degY,degZ)`, `scale=number or (x,y,z)`, `ol=outline thickness` (0 = none; 0.015-0.02 for tiny parts), `sharp=`, `smooth=`.
- `crystal`, `cone`, `flame` point along local +Z from their origin: orient them with `rot=aim(direction_vector)`. `crystal(..., both=True)` is centred and double-pointed.
- `box(name, (sx,sy,sz), mat, bev=..., bsegs=...)` is centred on loc. `cyl(name, r, length, mat, segs, bev, axis)` is centred, along X by default.
- `tube(name, pts, rad, mat, segs)`: rad is a float or a list with len == len(pts); 0 at an end makes a point. Needs at least 2 distinct points; consecutive points must differ.
- `torus(name, R, r, mat, segs, rsegs, axis)`: ring around `axis` ('X' by default = a ring around the bar).
- `radial(s, tilt, ang)` is a unit Vector tilted `tilt` degrees from the +X or -X axis (sign s), rotated `ang` degrees around X. Vector maths: `Vector((x, y, z)) + d * k`.
- `text(...)` only for the sign. `leaf` and `star` lie in the XY plane.
- `bolt(name, a, b, mat, r, n, amp, seed)` makes a lightning zigzag between two points.
- Use only names that exist in gymlib. `math`, `random`, `Vector` come through `from gymlib import *`.
- After writing, run `python -m py_compile <file>` on each file (bpy does not exist outside Blender, so only syntax can be checked) and re-read your code once against the helper signatures.

## Deliver
Create exactly the files for your levels, then reply with a short list: file, object count estimate, triangle estimate, silhouette idea in one line.
