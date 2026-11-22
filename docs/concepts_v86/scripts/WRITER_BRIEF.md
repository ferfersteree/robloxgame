# Writer brief — SpearHunt V86 spears (Blender bpy scripts)

You write Python build scripts for toon spears. You cannot run Blender. The lead runs your scripts in Blender, looks at the result and fixes things, so write clean, careful, runnable code.

**Rules**
- Write only your own files: `scripts\sp_NN.py` and `scripts\fx_NN.md`.
- Do not edit `spearlib.py`, `stage.py`, other writers' files or anything outside `docs\concepts_v86\scripts\`.
- Do not use or load any Roblox skills.
- Use only `spearlib` helpers plus `math`, `random` and `mathutils` (already imported by `from spearlib import *`).

## Read first

`scripts\spearlib.py` is the API, and these are three finished reference spears:
- `sp_01.py` — level 1, simple wooden spear with a dust impact;
- `sp_23.py` — level 23, coral spear with a crystal-growth impact;
- `sp_46.py` — level 46, legendary fang with a fire eruption.

Copy their structure exactly:
- module constants `NAME`, `N`, `BG`, `GROUND`, `TIP`, `TRAIL`, and optionally `SKY` (flight video background);
- `mats()`;
- `build()`, which returns `stats(NAME)`;
- `build_fx(M)`.

Add one more constant: `FX_EXPORT = {'suffix': 'object_name_without_SPnn_prefix', ...}`. List 2–5 FX meshes the game must rebuild, such as rings, spikes, shards, flames or crystals. Example: `{'ice_spike': 'im_spike_0', 'frost_ring': 'im_frost'}`.

## Coordinates and rules

**Axes and sizes**
- Units are studs. The spear stands along +Z.
- Tail at z = 0. The tip is at `TIP`, between 8.8 and 9.5.
- Grip is z = 2.5; spearlib converts automatically. Build everything in tail-space z.
- **Grip zone z 2.0–3.0: only the shaft (`rod`, radius 0.15–0.16), nothing else.** No torus, coil or bump may reach into 2.0–3.0. Include a torus's minor radius when you check this. Keep wraps to about 1.3–1.92 and 3.08–3.7.
- `TRAIL = 5.2`.

**Quality bar for every model**
- 22–60 separate objects in the main model.
- At least 3 accent colours.
- At most **5000 triangles**:
  - `coil()` costs about turns × 9 × segs × 2 tris; use `segs=5`;
  - `tube` with 8 segs costs about points × 16;
  - `rock` with sub=2 costs 320, sub=1 costs 80.
- Chunky, exaggerated cartoon shapes.
- A distinct silhouette: recognisable as a black shape, not "a stick and a triangle".
- Every head has layers: a socket or collar, the main blade, secondary pieces, and bindings or rings.
- Every spear has a tail piece (pommel or counterweight) and wraps or rings on the shaft.
- `marker('Tip', TIP)` and `marker('TrailRoot', TRAIL)`. The Tip marker is later snapped to the highest vertex automatically, but keep `TIP` honest.

**Coolness ramp**
- 2–10: wood, bone and early metal; modest FX.
- 11–22: elemental and themed; glowing accents begin.
- 24–34: strong elemental; glow and bigger heads.
- 35–45: legendary. Floating detached parts (rings, shards, orbs) that are still part of the main model, strong glow, big readable heads, up to about 2.4 wide.

**Materials**
- `toon(name, base, shade, light, spec, rim, emit, rimcol)` for solids.
- `glow(name, col, strength)` for emissive parts (≤ 3.6).
- `ghost(name, col, strength, alpha, power, edge)` for soft transparent blobs. Keep alpha ≤ 0.9; for big auras, ≤ 0.15.
- Material names must be unique per spear: prefix them with a short spear code, e.g. `'br_bronze'`.

## FX — three sets, each built after `fx('idle')`, `fx('flight')`, `fx('impact')`

**FX_Idle**
- Static: no keys.
- 5–12 small things near the head: glints (`star`), motes, small flames or bubbles, and an optional faint aura.

**FX_Flight** — a 1 s seamless loop
- Use only `stream(objs, path(t, i) -> (x, y, z_tail_space), smax=..., spin=...)` exactly as in the references. It makes the loop seamless; do not hand-key flight objects.
- The spear flies toward +Z, so effects travel from the head (z about 8–9.5) back past the tail (z about −3 to −4).
- 2–4 kinds of volumetric pieces, 20–40 objects total: puffs, shards, feathers, flames, sparks, rings around the axis (torus axis Z), stars, bolts.
- **No flat translucent ribbons or trails.**

**FX_Impact** — frames 101 → 145 (1.5 s)
- Call `impact_spear(TIP, depth=0.55..0.8)` first. The spear flies in and hits the ground at frame 105 (`f = IMPACT0 + 4`). Contact is about x = 0.35–0.6, y = 0, z = 0 in rig space.
- Ground is z = 0. The spear comes from −X, down to the right, at 35° above the ground.
- **Every object starts at scale 0 at `IMPACT0`.** Animate it with `key(ob, frame, loc=, rot=(deg), scale=, alpha=)`, then call `tidy(ob, 'impact')`. Use `ease_keys(ob)` where it fits.
- Everything shrinks or fades out by frame 145.
- `alpha` works only on `glow` and `ghost` materials; use `scale` for `toon` objects.
- Use 40–110 objects. Keep tubes and rocks cheap.
- **Each spear's impact must be unique.** Follow the concept table below.

`fx_NN.md`: a markdown section for that spear in the same format as `docs\concepts_v86\fx_table.md`:
- a heading line `## NN id — English name (type)`;
- **FX_Idle**, **FX_Flight** and **FX_Impact**, with the impact as a timing table;
- how to rebuild each part in Roblox: ParticleEmitter, PointLight, or Neon MeshPart + TweenService using your `FX_EXPORT` meshes;
- hex colours, rates, sizes and durations that match your script (t = 0 is the hit at frame 105, 30 fps);
- **never suggest Beam or Trail**;
- in Russian, like `fx_table.md`.

## Pitfalls that already happened

- `lathe` profiles are `(z, r)` pairs along the axis. `cyl`, `lathe`, `torus` and `cone` default to axis `'Z'`.
- `blade(outline2d, th, mat)` takes a closed outline of `(x, z)` points in the XZ plane, going around once.
- In `stream`, if you pass `smax` as a lambda it must take `(t, i)`.
- `tube(pts, rad)`: rad can be a list per point, and 0 makes a point.
- The impact `rot` in `key` is in degrees.
- Ballistic debris: copy the gravity loop from `sp_01` or `sp_46`; it must stop at the ground.
- Do not shadow helper names with variables: no variable called `bolt`, `star`, `leaf`, `flame`, `rock`, `box` or `tube`.
- **Lists such as `jitter` used inside `stream` lambdas must be defined before the call.**

## Concept table

Columns: theme / silhouette idea / impact (must be unique). Zones run meadow → forest → savanna → canyon → desert → jungle → temple → swamp → storm → reef → abyss → volcano → crystal caves → ice → sky → rift → cosmos → clockwork → spore cave → bone fields → sunken citadel → caldera. Pick `BG` and `GROUND` to match.

| N | id | idea | impact |
|---|---|---|---|
| 2 | bone | femur shaft piece, knobby bone head with a jagged bone point, sinew bindings, small skull charm (dust) | low bone-white dust ring; 5 bone splinters fly back and stick upright in the ground in a fan; pebbles |
| 3 | bronze | heavy cast bronze leaf blade with a mid-rib, flared socket, two bronze collars, round pommel (sparks) | clang: bronze shock ring flat on the ground; forward fan fountain of elongated sparks; a vertical "gong" ring expands and fades |
| 4 | feather | slim flint tip, bunch of 5–6 big coloured feathers tied below the head, beads (feathers) | feathers burst upward and float down spiralling; grass tufts pop up around |
| 5 | iron | wide boar-spear iron blade with cross lugs (wings) under it, rivets, iron bands (sparks) | heavy: 4 ground slabs crack and tilt up around; a line of orange sparks skids forward along the ground; dust |
| 6 | obsidian | black volcanic glass blade, faceted, lashed into a split wooden haft, red cord (shards) | black glass spikes erupt in a 6-point star, then shatter into flying fragments |
| 7 | crystal | clear blue crystal point in a silver claw setting, small crystal studs on the shaft (crystal) | chime: 3 glowing rings rise vertically like sound waves; a hexagon of 6 crystals grows at a fixed radius; sparkles |
| 8 | fire | iron blade with a glowing ember core, flame-shaped side vanes, charred shaft (fire) | fire explosion sphere, then a burning ring of small flames that smoulders and dies |
| 9 | ice | long ice crystal blade with a frosted collar, icicles hanging, white fur wrap (ice) | ice spikes erupt from the ground in a radial burst; a frost disc spreads |
| 10 | star | meteorite-iron head with an embedded glowing star, star-shaped guard, night-blue shaft (stars) | flash; 5 stars fly out in a circle and fall; a star-shaped glow mark on the ground |
| 11 | amber_sting | honey-amber blade (layered translucent-looking amber), insect trapped inside, wasp-stripe shaft (sparks) | honey droplets arc out, a honey puddle disc grows, 7 hex honeycomb prisms rise, golden sparks |
| 12 | solar_trident | three golden prongs with a sun disc behind them, savanna (fire) | sun burst: long thin golden rays shoot out horizontally, a sun disc rises and fades, fire ring |
| 13 | canyon_hook | red stone hook blade like a canyon arch, layered sandstone stripes (shards) | stepped red rock mesa pillars rise in a ring; red dust; stone chips |
| 14 | condor_quill | broad blade made of a giant feather quill shape, feather fins at the tail (feathers) | updraft: feathers spiral upward in a helix column; stacked wind rings rise |
| 15 | mirage_lance | pale desert lance, shimmering crystal tip, cloth wrap with tassels (crystal) | 3 ghost (transparent) mirror copies of crystal flash around; heat-wave rings; sand glitter |
| 16 | scorpion_sting | segmented stinger hook blade, armoured layered grip plates (shards) | ground splits; 2 hooked claw shards burst out and snap closed; sand puff; green venom droplets |
| 17 | emerald_vine | emerald blade wrapped by spiralling vines with leaves (crystal) | vines sprout and curl from the ground with leaves; emerald crystal buds pop on them |
| 18 | temple_guard | carved stone-and-gold guardian halberd-spear with a mask face on the socket (sparks) | carved stone glyph ring appears on the ground; 4 small rune pillars rise; golden sparks fountain up |
| 19 | mangrove_root | twisted root shaft (2–3 twisting tubes), wide wooden-root blade, moss (dust) | arching roots burst from the ground; mud clumps splash; brown dust |
| 20 | hydra_fangs | two curved fang blades side by side in a reinforced serpent-head socket (shards) | two fang spikes snap up from the ground crossing in an X; green shard spray |
| 21 | storm_trident | forked double tip, storm-cloud grey/purple, small lightning ornaments (sparks) | 3 lightning bolts strike down from above around the spear; electric ring on the ground; sparks |
| 22 | thunder_split | open zigzag lightning-shaped blade, yellow and navy (sparks) | a glowing zigzag crack splits the ground forward; bolt arcs jump along it |
| 24 | tide_crest | blade shaped as a curling wave crest, foam tips, sea-blue (ice) | a curved wave wall (torus segment) rises around and collapses; splash droplets; foam ring; ice flakes |
| 25 | abyss_anchor | heavy anchor-shaped head (flukes), chain wrap, deep-sea barnacles (shards) | shockwave ring plus a water splash crown; chain links drop and bounce |
| 26 | leviathan_fang | huge sea-monster fang in a reinforced iron frame (ice) | a giant ice fang rises out of the ground behind the spear; frozen ring; ice shards |
| 27 | ash_saw | dark serrated saw blade (teeth along one edge), ash-grey with ember glow (shards) | spinning saw-disc shards skid out along the ground; dark ash cloud; embers |
| 28 | golem_heart | layered stone head plates around a glowing warm core (sparks) | two stone golem fists rise from the ground and slam together; core pulse ring; sparks |
| 29 | magma_tongue | glowing lava blade (tongue shape) in a black stone frame (fire) | lava geyser jets from a crack; lava blobs arc; black crust rocks fall; smoke |
| 30 | phoenix_wing | flame wing-shaped blade, feather-fan grip, red-gold (fire) | two big fire wings (fans of flame-feathers) unfold from the impact, flap once, dissolve into embers |
| 31 | amethyst_geode | hollow crystal crown (ring of crystals) around an amethyst core orb (crystal) | a geode dome of inward-pointing crystals forms around the spear, then cracks open outward |
| 32 | quartz_needle | very long thin clear needle tip in a slim crystal socket, elegant (crystal) | a dense forest of thin quartz needles shoots up quickly in a disc; glass glints |
| 33 | lunar_crescent | silver crescent-moon blade, moonstone, frost (ice) | crescent ice blades sweep out in arcs along the ground; a moon disc glows above; frost |
| 34 | aurora_weave | glowing blade with coloured bands (green/teal/violet rings) around it (ice) | stacked coloured glowing rings rise in waves, rippling; ice crystals sparkle |
| 35 | cloud_feather | light feather tip on cloud puffs, white/sky-blue, floating feathers (feathers) | big soft cloud puff burst; feathers drift; a small rainbow-coloured ring set |
| 36 | sky_harpoon | long harpoon with a barbed hook, rope coil, sky-blue/brass (feathers) | 3 hook barbs anchor into the ground around; cloud puff; wind rings spiral up |
| 37 | rift_shards | cloud of dark shards hovering around the tip (floating parts), violet glow (shards) | a dark rift disc opens on the ground; shards orbit and get sucked in, then it implodes |
| 38 | void_scissors | two open blades with darkness between them (void orb), black and violet (crystal) | two glowing slash marks cut an X on the ground; a dark void bubble swells and pops |
| 39 | astral_armillary | golden tip held by orbital rings (floating rings), starry (stars) | armillary rings expand around the impact at different tilts and spin; golden star sparkles |
| 40 | singularity_spire | stepped black spire inside an event-horizon ring frame (stars) | implosion: particles sucked inward, then a ring flash outward; stepped black pillars rise |
| 41 | gear_pike | copper gears and rings on the head, clock face, ticking (sparks) | gears fly out spinning, springs bounce, steam puffs |
| 42 | spore_halberd | pale blade with a glowing mushroom cap behind it (dust) | glowing spore cloud bursts and drifts; small mushrooms sprout around |
| 43 | bone_glaive | fossil rib crescent blade, vertebra shaft pieces (shards) | rib bones erupt from the ground in a ring and arch inward like a ribcage; bone dust |
| 44 | pearl_lance | sunken citadel lance, big pearl in a clam socket, coral-gold (ice) | pearl bubble dome; ice spikes in a clam-shell fan; pearls scatter |
| 45 | rift_conductor | lightning-rod spire with prongs, violet stripes (sparks) | lightning arcs converge from a ring of points into the spear; violet electric ring |

When done, report per file in at most 3 lines: the main objects (silhouette), the impact idea, and the estimated triangle count.
