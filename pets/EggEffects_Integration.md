# EggEffects R2

Install `EggEffects.luau` as **ReplicatedStorage/PetsTools/EggEffects** and `EggEffects.client.luau` as **StarterPlayer/StarterPlayerScripts/SpearHuntEggAmbience**. The bootstrap automatically discovers the five eggs in `Workspace/SpearHunt_PetsCollection` during normal Play. It handles late replication, removal/replacement of the collection and script destruction. There are no server scripts, remotes, uploaded textures, animation clips or opening mechanics.

The module follows the installed `roblox-mesh-vfx` pool lifecycle and right-handed BeamArc construction, kept in one small runtime instead of installing its unrelated combat/network/camera systems. Native ParticleEmitters provide the glints, dust, bubbles, sparks and motes; fixed pools provide actual small LEGO leaves, cut amber fragments and cross-shaped orbital stars. No effect recreates smoke/fire as sphere clusters.

Each model keeps `AssetId`, `DisplayName`, `AssetKind=Egg`, `FamilyId` and its existing custom rig. The runtime writes cosmetic **Motor6D.Transform** only. It never changes C0, C1, geometry joints, pivots, the shell's transform or pet faces.

Optional authored anchors are Attachments under the appropriate existing Rig bone:

| Name | Purpose |
| --- | --- |
| `FX_Center` | Main ambient frame; normally on Rig.Root at `(0, height*0.48, 0)` |
| `FX_Core` | Visible inset/window illumination, typically just behind a front inclusion |
| `FX_Crystal_01`–`FX_Crystal_04` | Storm crystal tips; put these outside the crown geometry so branching arcs remain visible |

Optional Model attributes are `EggFXHeight` (default4.8), `EggFXRadius` (shell radius, default1.55) and `EggFXCenterY` (default48% of height). Anchors override fallback positions. Local axes follow the egg's actual orientation. An isolated, single-color illuminated part may have `EggFXGlow=true` and `EggFXSequence=1..4`; multicolor unions with UsePartColor=false are deliberately excluded from recoloring.

Existing motion groups used:

| Family | Native decoration motion | Distinct surrounding effect |
| --- | --- | --- |
| forest | Sprout pitch/roll | Six irregular firefly paths, four floating two-plate leaves, rising pollen; green/gold breathing light |
| amber | CrownCap and SunLock small rotations | Five slow tumbling amber pieces, rare gold sparks and inner warm motes |
| tide | CoralCrown flowing motion | Four bubble lanes with different speeds/sizes and two intermittent curved water swishes |
| storm | CrystalCap tiny charged tremor | Seven short trunk/branch Beam segments, four sequential crystal flashes and brief sharp sparks |
| astral | OrbitGold/OrbitPearl rotate differently, CrownCap sways | Three orbital planes, three moving cross-stars, short native Trails and staggered twinkles |

All layers are client-owned, pooled, nonphysical and shadowless. PointLight.Range never exceeds3.2. The singleton PreSimulation scheduler serves all eggs: near distance≤62 runs at30updates/s, medium≤190 at15 with smaller pools/particle counts, beyond190 stops particles/lights/decor and restores ambient motor offsets. Manual low graphics settings reduce the budget further. No Instance creation or descendant scans occur inside Step. Native built-in textures were checked in the local Studio content folder.

`model:SetAttribute('EggOpening', true)` suspends and clears ambience; `false` resumes it. Set the attribute before starting an existing opening sequence. Ambient offsets are restored only if their last written value still belongs to this controller, so it does not overwrite a foreign opening/Animator pose. No opening sequence currently exists in this collection.

Public API:

```lua
local M = require(game.ReplicatedStorage.PetsTools.EggEffects)
local handle = M.new(egg)
handle:Start() -- idempotent, shared automatic scheduler
handle:Stop() -- clears particles/trails/lights, hides pooled decor, restores ambient offsets
handle:Start() -- fresh effect clock, reuses the same pool
handle:Destroy() -- idempotent, releases owner/connections/instances
```

Inside the same Luau require environment, automatic owners can be retrieved with `M.GetForModel(egg)` and queried using `GetDiagnostics()`. A Studio MCP execution context can have a separate require cache: a nil lookup there does not mean the normal LocalScript stopped. Inspect each real egg's `_EggAmbient_Client` folder and its actual moving attachments/parts/Motors, and use separate clones for lifecycle tests. Do not create a second owner for the same model. A clone outside the exhibition can use `M.new(clone,{Manual=true,ForceLOD=1,Seed=420})`, then `Start()` and `Step(time,dt)`. Absolute time makes native decor/Beam/light/motor poses repeatable; the Roblox particle simulator itself retains its normal engine randomness. Stop/restart clears its old particles before a new inspection take. Explicit edit-mode previews require `{Manual=true,AllowEditPreview=true}`; their owner folder has Archivable=false so a native save does not persist preview cosmetics.

Run `EggEffects_QA.client.luau` once via Studio MCP Client after installation. It creates five temporary client-only clones, exercises180steps per family, verifies stable allocation, unchanged rest joints, opening suspend/resume, far LOD, repeated Start/Stop/Destroy and recreation, then removes its fixtures. Visual checks and a real playtest recording remain required; compiler/code alone do not establish VFX quality.

Read and applied: roblox-vfx (including LESSONS and design/craft), roblox-mesh-vfx (Pool/BeamArc/VFXMath/performance), roblox-animation-vfx, roblox-performance, roblox-testing, roblox-code-review. The standalone `robloxstudio`/bridge route requested by some skill text is absent here; the project's available official Studio MCP is the runtime verification route used by the parent agent. No Studio content was modified by this file-authoring subtask.
