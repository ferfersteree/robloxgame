# PLAN-EGGS: donate eggs with exotic animals

Branch `donate-eggs`. Backup: `SpearHunt V27 - Cartoon Shop.rbxl` in git (same scripts as the open Studio place at the start; the task said V21, the open game was already V27).

Design decisions
- Exotics live in `Config.EXOTICS` (not in `Config.SPECIES`), so they cannot enter Roll, Population, Ambient, Showroom or the collection. A test proves it.
- The server rolls the egg inside `applyProduct` (the same step that records the receipt), so a purchase is saved once and cannot be lost or doubled on rejoin.
- Odds shown in the UI are computed from `Config.EGGS` weights by `Config.eggOdds`, the same table the server rolls with.
- Bonuses add per stat, are capped, at most 3 equipped. They enter through `Perks` (state comes from the server).
- New modules cannot be added by the patch tool (no cargo), so code goes into Config, Perks, DemoServer, Backend, Server/Shop and Client/Shop.

Stages
1. [x] Data and Config: 16 exotics, 4 eggs, caps, odds and roll functions, egg products (id = 0).
2. [x] Server: egg roll in `applyProduct`, owned/equipped/levels/shards saved, equip/unequip/upgrade/hatch-ack actions, state push.
3. [x] Exclusion from normal pools plus test.
4. [x] Bonuses: Perks and boost hooks (luck, rare chance, coins, XP, range, grip, bag, training, forge).
5. [x] UI: Eggs section with odds, hatch animation, Exotic window, HUD chips.
6. [x] Balance simulated over all 560 loadouts, frame time measured, persistence tested with a fake DataStore.
7. [x] Final check and Obsidian notes (no push, by instruction).

Log
- Stages 1-5 done in Studio and synced to `source/` (saved with `save_place`, extracted with a script).
- Stage 6: frame time measured (no extra cost during hatch). Balance of a full loadout was estimated, not simulated.
- Not done: particle auras (cannot render in viewports), visual check of portraits (Studio capture did not draw ViewportFrames), real-money and DataStore tests.
- Nothing was pushed to GitHub (the task said not to publish anything). Commits are local on branch `donate-eggs`.
- Round 2: region gate (PolicyService), hatch CONTINUE button bug fixed, levelled numbers in the Exotic window, companions with auras/trails/beams (`Pets`), balance simulation, persistence tests. See SHOP.md.
- Still not seen by eye: portraits and companions (Studio capture draws neither viewports nor the 3D world). Still not done: real-money test, real DataStore test, server-side application of bonuses.
