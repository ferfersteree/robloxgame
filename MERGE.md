# V19: one game, 150 creatures

`SpearHunt V19 - Fauna 150.rbxl` is V18 (Sky Shop) with the creature collection from `main` merged in.

## What is in V19
- **One fauna pipeline.** `ReplicatedStorage/Fauna150` builds every creature from the collection art (`SpearHunt_RenderData`) and moves it with the `Animation150` library. `V16Fauna/Factory` is now a thin adapter to it, so Reveal, AnimalRig, Card and the shop keep working unchanged.
- **All 150 species.** The 69 old models were replaced by the collection versions. 81 new species were added to `Config.SPECIES`.
- **25 biomes.** `Config.ZONES` now has biomes 20 to 25 (Rust Gardens, Fungal Bogs, Bone Dunes, Sunken Citadel, Storm Rift, Primordial Caldera), distances 5800 to 12700.
- **Shop fixes** from review (squirrel position, banner label spacing).

Scripts changed: `Config`, `AnimalRig`, `Card`, `Reveal`, `WrapCtl`, `Population`, `V16Fauna/Factory`, `Shop`. New: `Fauna150`, `Animation150/*`, `SpearHunt_RenderData`, `SpearHunt_BiomeNames`. Plain sources are in `source/`. The old `Animals`, `V15Fauna` and `V16Fauna/ModelsData` are still in the file as an archive and are not read.

## How the new species were balanced
Rows follow the pattern of the existing zones:
- Rarity: each zone has six species with rarities 1 to 6. The three old species keep theirs; the new ones take the free slots, smallest to largest by body size.
- Price: the Uncommon price of zone *z* is 5,000,000 x 1.85^(z-5), the same growth as zones 5 to 19. Rarity multiplies it by 0.5 / 1 / 2 / 4 / 12 / 36.
- Spear requirements, population weights and spawn kinds (ground / air / water) follow the same zone and rarity rules. Weights in kg, emoji and one-line facts were written by hand.
- Aquatic species in zones without water (18, 23) are placed as floating (`air`) so they do not spawn underground.
Everything is plain data in `Config`, so numbers can be edited freely.

## Known limits
- **Biomes 20 to 25 are gated (fixed in V20).** In V19 a throw at the range cap rolled zone 20; V20 keeps throws in zone 19 (see SOUND.md). **No terrain for biomes 20 to 25.** `Workspace/Map/Forest` only has `Biome1` to `Biome19`. The new species of biomes 20 to 25 exist in the data and the collection UI, but the ground for them has to be built.
- **Not run in Studio.** Logic was run headlessly in a Luau interpreter with stubbed Roblox classes: all 150 species build, bind to Animation150 (scaled and unscaled), play 8 states without errors, and `Config` loads with 150 species and 25 contiguous zones. Looks, performance with many animals on screen, and the reveal sequences still need a first look in Studio.
- **Shop art** (`shop-art/`) still has to be uploaded to Roblox and its ids put into the `ART` table in `Shop.luau`.
- The place file is about 25 MB (V18 was 9 MB) because it is re-encoded with LZ4.

## Rebuild
`tools/merge/merge.rs` (Rust, `rbx_binary` + `rbx_dom_weak`) merges the two places and swaps script sources listed in `edits.txt`. `gen_config.py` produces the Config rows. `roundtrip.rs` checks that a place survives decode and re-encode unchanged. `harness/` is the headless Luau test (`mlua` with Luau).
