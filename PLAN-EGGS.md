# PLAN-EGGS: donate eggs with exotic animals

Branch `donate-eggs`. Backup: `SpearHunt V27 - Cartoon Shop.rbxl` in git (same scripts as the open Studio place at the start; the task said V21, the open game was already V27).

Design decisions
- Exotics live in `Config.EXOTICS` (not in `Config.SPECIES`), so they cannot enter Roll, Population, Ambient, Showroom or the collection. A test proves it.
- The server rolls the egg inside `applyProduct` (the same step that records the receipt), so a purchase is saved once and cannot be lost or doubled on rejoin.
- Odds shown in the UI are computed from `Config.EGGS` weights by `Config.eggOdds`, the same table the server rolls with.
- Bonuses add per stat, are capped, at most 3 equipped. They enter through `Perks` (state comes from the server).
- New modules cannot be added by the patch tool (no cargo), so code goes into Config, Perks, DemoServer, Backend, Server/Shop and Client/Shop.

Stages
1. [ ] Data and Config: 16 exotics, 4 eggs, caps, odds and roll functions, egg products (id = 0).
2. [ ] Server: egg roll in `applyProduct`, owned/equipped/levels/shards saved, equip/unequip/upgrade/hatch-ack actions, state push.
3. [ ] Exclusion from normal pools plus test.
4. [ ] Bonuses: Perks and boost hooks (luck, rare chance, coins, XP, range, grip, bag, training, forge).
5. [ ] UI: Eggs section with odds, hatch animation, Exotic window, HUD chips.
6. [ ] Balance check and frame time.
7. [ ] Final check, Obsidian notes, push.

Log
