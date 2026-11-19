# Training rework V82 — contract between the model designer and the code agent

Owner's request (Russian, paraphrased): rework the dumbbells completely. 15 dumbbell levels that fit the game and do not break
progression. Each level has its own dumbbell model AND its own look of the dumbbell stand ("стенд"): upgrading the level upgrades
both. Reps no longer give +Strength one by one: they fill a bar; the bar needs more points with each level. During training an
interactive prompt in the game's style (drag an arrow along a direction, or tap a circle) gives a 1-second ×2 buff to points per rep.
The upgrade is a separate button next to the stand that appears when the player walks up to it. While training the player sees
NOTHING except the bar, the Exit button and the Strength value.

## Data (in `source/ReplicatedStorage/Shared/Config.luau`)
```lua
Config.DUMBBELL[i]      = { cost = number, gain = number, name = string, bar = number }   -- i = 1..15
--   cost: coins to reach level i (level 1 = 0). gain: points per rep. bar: points needed to fill the bar once at this level.
Config.DUMBBELL_LOOK[i] = { color = Color3, material = Enum.Material, size = number, parts = { PART, ... } }
--   same format as today (see the 7 existing entries): PART = { name, shape = "Block"|"Cylinder"|"Ball"|"Wedge",
--   size = {x,y,z}, offset = {x,y,z}, material = string (Enum.Material name), rgb = {r,g,b}, weight = bool, mirror = bool,
--   neon = bool? }. Concept axes: X along the bar, Y up. "mirror" = a ± pair (second part at -x). Max 14 parts per tier.
--   Total length about 2.6 studs (tier 1) growing to about 5.2 studs (tier 15); held in one hand of a normal character.
Config.GYM_STAND[i]     = { palette = { wood = Color3, trim = Color3, stone = Color3, sign = Color3, signText = Color3 },
                            materials = { wood = string, trim = string, stone = string },
                            extras = { PART, ... },        -- decorations added at this stage (same PART format, rack space:
                                                          -- origin = floor midpoint, +Z faces the player, rack about 10 wide x 5.5 tall x 3 deep)
                            light = Color3? }              -- optional glow colour of the current pair
```
`Util.gymRack(level)` builds the stand for a level from GYM_STAND[level] (base structure stays the CAMP GYM rack of V70, recoloured
and decorated per stage); the stand shows the CURRENT dumbbell pair prominently (plus smaller previous tiers is optional).
`Util.dumbbell(level)` keeps working for levels 1..15.

## Economy rules
- Levels 1–7 keep today's `cost` and `gain` exactly (players already own them). Levels 8–15 continue the curve; cost of level 15 should be
  in the range of a late-game spear price (see `Config.SPEARS` prices), gain grows about ×1.8–2.2 per level. Reaching the throw range cap
  (`Config.THROW.maxRange` = 8·√Strength → about 2.5M Strength) must stay a long-term goal, not instant.
- Strength per rep on average stays `gain` (the bar only chunks it): each rep adds `gain` points (×2 during the buff, ×`Perks.repMult()`);
  when the bar is full the player receives Strength = bar size + a fill bonus of 10 %, the bar resets (overflow carries). Bar sizes grow
  with the level (e.g. about 12 reps' worth at level 1 up to about 40 reps' worth at level 15).
- Saves: `d.dumbbell` clamps to 1..#Config.DUMBBELL (15); new field `d.trainPts` (number, sanitised in `Demo.load`).
