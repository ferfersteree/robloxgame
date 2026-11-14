# PLAN-NIGHT: effects for spear throw, animal drop and bush reveal

Branch `night-fx`. Backup: `SpearHunt V27 - Cartoon Shop.rbxl` in git (the task said V21; the open game was V27).

Status: research only. The eggs task (branch `donate-eggs`) came later in the same session and was done first. No effect code has been written on this branch yet.

What the research found (details in Obsidian `SpearHunt/Эффекты.md`)
- 40 of 46 spears already have their own V15 profile (own model, trails, impact). The 6 newest spears reuse the Singularity Spire model and profile with other colours.
- No object pools. A throw clones a 382-716 part model; a landing builds about 130 instances and up to 24 raycasts; a reveal builds a 417-605 part cover and a new animal model.
- `Fx.lowFx` is ignored by the V15 spear path, rings, lightning and the cover reveal.

Planned stages (in this order, each ends with Play, Output check, frame time, copy to `source/`, commit)
1. [ ] Engine and pools: a pool for impact rigs (rings, rays, emitters), one shared emitter per spear flight, a cap on simultaneous effects, lowFx plumbing (`SpearPres` already has an unused Quality parameter).
2. [ ] Throw: charge visuals per tier (nothing exists now), flight and impact variety per spear group from `SpearProfilesV15` data (only 5 of 40 path styles branch today), fade by one tween instead of one per part.
3. [ ] Remote throws: distance LOD and a simplified impact.
4. [ ] Animal drop: rarity-specific beats (common, rare, secret), cap on bursts, drop the 60 s light.
5. [ ] Cover reveal: per-zone effect data (25 zones), build covers ahead of time, remove the whole-workspace scan in `RevealOcclusion`.
6. [ ] Measure before and after in Studio and write the numbers here.

Notes
- Studio in the test environment ran at about 15 FPS even when idle, so absolute frame times there are not meaningful; compare before and after only.
- Screenshots in that session did not draw ViewportFrame content.
