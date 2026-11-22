# V87 spear effects: data schema (contract between writers)

Source of truth for what each spear does: `docs/concepts_v86/fx_table.md` (46 sections, prose + tables, written by
Claude Design). Data lives in `source/ReplicatedStorage/Art87/SpearFxData1.luau` (spears 1-23) and
`SpearFxData2.luau` (spears 24-46). The player is `source/ReplicatedStorage/Art87/SpearFx87.luau`.

Each data module returns `{ [spearId] = Entry }` (spear ids as in `Config.SPEARS`, e.g. `stick`, `coral_branch`).

```lua
Entry = {
  idle = { emitters = { Emitter... }, light = Light? },          -- while the spear is in the hand
  flight = { emitters = { Emitter... }, rings = { Ring... }, light = Light? },  -- attached to the flying spear
  impact = {                                                     -- at the landing point, t = 0 at touch-down
    duration = 1.5,                                              -- seconds, everything is gone after this
    light = { color = "#rrggbb", range = 12, brightness = 3, t1 = 0.4 }?,  -- fades out by t1
    bursts = { Emitter... },                                     -- emitters with count = N fire once (Emit) at t0
    meshes = { Mesh... },                                        -- tweened Neon / plain meshes
  },
}

Emitter = {
  at = "tip" | "trail" | "grip" | "ground",   -- ground only in impact
  texture = "sparkle" | "star" | "smoke" | "dust" | "spark" | "rock" | "leaf" | "feather" | "snow" | "fire" | "bubble" | "crystal" | "shard" | "spore" | "gear" | "bolt" | "drop",
  c0 = "#rrggbb", c1 = "#rrggbb",             -- colour over life
  s0 = 0.3, s1 = 0.0, smid = nil,             -- size at start / end (optional mid peak)
  t0 = 0.2, t1 = 1,                           -- transparency start / end
  rate = 12,                                  -- per second (idle / flight); ignored when count is set
  count = nil,                                -- impact bursts: number of particles emitted once
  delay = 0,                                  -- impact bursts: seconds after touch-down
  life = { 0.8, 1.2 },                        -- seconds
  speed = { 2, 4 },
  spread = 25,                                -- degrees (SpreadAngle X and Y)
  dir = "back" | "up" | "out" | "forward",    -- back = along -spear, up = world up, out = all around
  accel = { 0, -25, 0 }?, drag = 2?, rot = 360?, light = 0..1 (LightEmission)?,
}

Ring = { mesh = "air_ring", color = "#rrggbb", every = 0.33, s0 = 0.6, s1 = 2.0, travel = 6.5, life = 1, a0 = 0.2 }

Mesh = {
  mesh = "crater" | "shock_ring" | ... | "part" | "ball" | "cyl",  -- mesh = name after "_fx_" in C:\SpearHuntAssets\spears\sp_NN_id_fx_<name>.glb
                                                                    -- (baked as ReplicatedStorage.Art87.SpearFX.sp_NN_id_fx_<name>); part/ball/cyl = plain Part shapes
  color = "#rrggbb", neon = true,
  count = 1,                       -- copies placed around a circle of radius r (count > 1), evenly or random
  r = 0,                           -- circle radius in studs
  t0 = 0, t1 = 0.4,                -- tween start / end (seconds from touch-down)
  size0 = { 0.3, 0.3, 0.3 }, size1 = { 5, 0.2, 5 },   -- Size tween (studs)
  a0 = 0, a1 = 1,                  -- Transparency tween
  y0 = 0, y1 = 0,                  -- height above ground tween
  spin = 0,                        -- degrees per second around Y
  easing = "Quad" | "Back" | "Sine" | "Linear" | "Bounce",
  hold = 0,                        -- seconds to stay at the end state before vanishing (until duration)
}
```

Rules for the translators:
- Keep every visible beat of the table, but merge beats that would need more than 12 meshes or 6 emitters per spear.
- No Beam, no Trail (the player refuses them).
- Use the meshes that exist: list `C:\SpearHuntAssets\spears\sp_NN_id_fx_*.glb` for that spear.
- Colours as `#rrggbb` strings exactly as in the table. Sizes in studs, times in seconds.
- Any field you are unsure about: leave it out, the player has defaults.
