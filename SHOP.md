# Shop restyle with rendered 3D art (V29, on the eggs branch)

The shop now looks like the reference: a deep purple crystal hall instead of the meadow, dark tiles with a bright coloured outline, wide egg banners and glossy 3D pictures instead of the flat cartoon icons.

- **Eggs.** Each egg is a wide banner: a faceted crystal egg on the left (own colours: Mystic blue, Royal purple, Cosmic gold, Absolute rainbow), the rarity cards with exact percentages and the best animal of each rarity, the big green Robux button bottom right and an ODDS button for the full list. Percentages come from `Config.eggOdds`, so they match the server roll. The hatch window shows the same egg.
- **Icons.** Coin packs (4), the three potions, gift, crowns (VIP and Founder), crystal ball, clover, globe, anvil with hammer and scales are rendered glossy 3D pictures. Items without a rendered picture (Hunter's Bundle banner, spears, bag) keep their old icons.
- **How it is made, nothing uploaded to Roblox.** The pictures are rendered offline by `tools/render_eggs.py` and `tools/render_icons.py` (numpy and OpenCV: faceted shards with lighting for eggs, ray marching of simple shapes for icons). `tools/pack_eggs.py` packs each PNG as deflate + base64 into a ModuleScript under `Client/EggArt`. At runtime `Client/EggArt` unpacks the data (yielding every 5,000 symbols, one picture at a time; the four eggs are unpacked 3 s after the game starts so the hatch window has its egg) and draws it into an `EditableImage` shown in an `ImageLabel`. A checksum guards the unpacking. If `EditableImage` is unavailable (the experience setting, an older device), a probe at the first request fails every picture at once and every spot shows the old cartoon icon without decoding anything.
- **Requirement in a published game (from Roblox docs, found by a research agent, not tested by me).** `EditableImage` fails by default in published experiences. It needs Experience Settings > Security > "Allow Mesh / Image APIs", and the doc says the owner must be 13+ age verified and ID verified. No age or ID rule for players was found. Clients have strict memory budgets and creation can return nil, so the code already falls back to the old icons. Whether a blank image created from scratch needs less than an asset-based one is not stated in the docs. Beta status is unconfirmed. Sources: create.roblox.com/docs/reference/engine/classes/EditableImage and /studio/experience-settings, devforum threads 3267293 and 3818624. **Do this step before launch and check the shop in the published game.**
- **Fallback if that is not possible.** The same pictures are in `shop-art/rendered/` as PNGs (eggs 300x380, icons 176x176). They can be uploaded as normal images and wired through the existing `art_<name>` flow (`Client/AudioIds`). I was not allowed to upload them myself.
- **Re-packing the art (how the data got into Studio).** Render: `python tools/render_eggs.py <dir>` and `python tools/render_icons.py <dir>`. Pack: `python tools/pack_eggs.py <dir> <out> 0.8` for eggs, `... 1.0 crop` for icons. The packed `<key>.lua` files are too big to pass through the assistant, so they were served from `python -m http.server 8777 --bind 127.0.0.1` in the output folder and pulled in Studio (Edit mode, command line) with `HttpService.HttpEnabled` switched on only for that call and restored to its old value (false) afterwards, creating one ModuleScript per picture under `Client/EggArt`. `python` works on this machine, `python3` does not. The data modules are also saved in `source/.../Client/EggArt/`.
- **Open Studio caveats.** First open of the shop still has one frame of about 160 ms (it was 600 ms before the animal portraits were built one per frame and pictures one at a time); after that frames are even and the 30-second state push no longer rebuilds the window. One unidentified warning appears now: `ContentId rbxassetid://10725837187 failed ... No asset content representation`; it is not referenced by any script, so it comes from something inside the place (not from the new code).
- **Seen in Studio.** Screenshots of the shop window in Play: eggs, passes, boosts, bundle banner and Founder banner. The world render in screenshots worked this time, so the animal portraits in the egg cards were seen too.
- **Not done.** Spear icons, the bag icon and the rank card art were not redone. The coins and other icons are rendered at 176 px (about 1x on a normal screen; they look soft on very high-DPI screens). No multi-buy bundles (x3, x10) like in the reference: that needs new products.

---

# Donate eggs and exotic animals (V28)

Open `SpearHunt V28 - Eggs.rbxl`. Four eggs (Robux Developer Products, id = 0, simulated in Studio) hatch 16 exotic animals that cannot be found while hunting.

## Where things live
- `Config.EXOTICS`: the 16 species (base model from Fauna150, style, scale, bonuses). **Not** in `Config.SPECIES`, so Roll, Population, Ambient, Showroom and the collection (all read `Config.SPECIES`) cannot see them. Test run in Studio: 0 pool leaks, 0 exotics in 60,000 normal hunt rolls.
- `Config.EGGS`: one weight table per egg. The server rolls from it (`Config.eggRoll`) and the odds window shows percentages computed from the same table (`Config.eggOdds`). Observed over 100,000 rolls per egg, the difference from the shown odds is at most 0.3 percentage points.
- `Config.EXOTIC`: equip limit (3), level bonus (+10% per level, max 5), per-stat caps and floors, shard rewards and upgrade costs. All numbers in one place.
- `Server/Shop`: `rollEgg` runs inside `applyProduct`, the same step that writes the receipt id and saves, so a purchase is recorded once. It stores owned, equipped, levels, shards and a hatch queue in the DataStore profile, and handles `exoticEquip`, `exoticUnequip`, `exoticUpgrade`, `hatchAck`.
- `Perks`: reads the server state and adds exotic bonuses to the existing sums (luck, rare-chance caps, sale coins, XP, bag slots, training power, forge discount) plus throw range and steady grip. Hooks in `DemoServer`/`Backend` (`boostMult`) and the bag size.
- `Client/Shop`: Eggs section with tiles and an ODDS button, odds window, hatch animation (shaking egg, cracks, flash, reveal card), Exotic collection window (equip, upgrade with shards), chips for equipped exotics at the bottom left.

## Eggs and exact odds
| Egg | R$ | Odds |
|---|---|---|
| Mystic | 99 | Common 80%, Rare 20% |
| Royal | 249 | Common 24%, Rare 44%, Epic 18%, Legendary 12%, Mythic 2% |
| Cosmic | 499 | Rare 24%, Epic 42%, Legendary 24%, Mythic 8%, Absolute 2% |
| Absolute | 999 | Epic 15%, Legendary 45%, Mythic 30%, Absolute 10% |

There is no pity counter and no hidden condition. A duplicate gives shards (5, 12, 30, 80, 200, 500 by rarity) used to upgrade owned exotics.

## The 16 exotics (bonus, then trade-off)
Common: Candy Hopper (luck +6%), Neon Fox (coins +8%), Bubble Boar (XP +10%). Rare: Glowstripe Wolf (range +12%, coins -6%), Frostfur Bear (bag +20, luck -5%), Ruby Antlerlord (rare chance +10%), Prism Otter (training +15%). Epic: Storm Kitsune (luck +20%, grip -10%), Magma Titan (coins +20%, range -10%), Ghost Lynx (rare chance +14%, XP +10%). Legendary: Solar Maned Lion (luck +30%, grip -12%), Void Mammoth (bag +35, forge -15%, range -8%), Aurora Phoenix (rare chance +20%, XP +20%). Mythic: Astral Wyrm (luck +45%, rare chance +25%, coins -15%), Leviathan Prime (range +25%, grip +15%, luck -10%). Absolute: Prismatic Overlord (luck +55%, rare chance +30%, coins +25%, XP +25%, range +15%, bag -20).

## Stacking and balance
Bonuses of one stat add. The per-stat caps apply to the sum of the equipped exotics only; passes and boosts are added on top of that result (`Perks.luckMult` and the others), so exotics can never give more than the cap whatever else the player owns. Caps: luck +100%, rare chance +60%, coins +60%, XP +100%, range +30%, grip +30%, bag +40 slots, training +100%, forge -40%; penalties floor at -40% (bag -40 slots). At most 3 equipped. Levels scale both the bonus and the penalty (+10% per level), and the Exotic window now shows the levelled numbers.

Simulated with the real `Config.exoticTotals` over all 560 loadouts of 3 (not estimated):
- Level 0 best loadout for luck x coins x rare-chance: x4.03 (Magma Titan + Astral Wyrm + Prismatic Overlord). Level 5: x4.67 (Ruby Antlerlord + Magma Titan + Prismatic Overlord). That product is an upper bound for income, because luck only improves odds inside a pool and the rare caps saturate.
- Luck alone: the best exotic loadout gives +100% (candy hopper + two luck mythics at level 5). On top of potion + Lucky Charm + Server Luck (4.00) that is x1.25; for a player with no pass or potion it is x2.00.
- Rare-chance caps: base stack 3.00 (potion, charm, Jackpot Hour, Server Luck), exotics add up to +0.60 (3.60, x1.2).
- Range +30% and grip +30% at most; bag +40 slots at most.
The top results need the 999 R$ Prismatic Overlord (2% in Cosmic, 10% in Absolute) plus upgrades paid in shards, so the realistic early loadout is far below those numbers. If it still feels too strong, lower `Config.EXOTIC.CAP` (one table).

## Region rule for paid random items
Roblox restricts paid random items in some regions. The server asks `PolicyService:GetPolicyInfoForPlayerAsync` when the profile loads and keeps `ArePaidRandomItemsRestricted` as `prof.eggsOff`. If the lookup fails outside Studio, eggs stay off (fail closed). When off, the Eggs tiles and odds are hidden ("Eggs are not available in your region. Your exotic animals still work."), `buy` refuses egg products, and the Studio test purchase refuses them. The region is resolved before the profile counts as loaded, and until it is known the state says eggs are off. A receipt that arrives anyway (the player paid through another path) is still granted, because the player already paid. The collection and bonuses keep working.

## Companions (auras, trails)
Each equipped exotic follows its owner as a small floating companion built from the same Fauna150 model, with a particle aura (rate by rarity), a Trail, a light for Legendary and above and a vertical light Beam for Mythic and Absolute. The server writes the equipped ids into the player attribute `Exo`, so other players see them too (within 90 studs, at most 6 foreign companions). Low graphics (`lowFx`): only your own, without particles, trails, beams or lights. No uploaded assets. Code: `Pets` in `Client/Shop.luau`; Checked in Play with numbers (not by eye): the three companions sit at the sides (none covers the screen centre, measured with `WorldToViewportPoint`), the models' heads point the same way as the player (`Pets.yaw = 0`; with pi they faced backwards), and they are built one per 0.12 s, which cut the worst frame while equipping from 122 ms to 37 ms (average 16.7 ms). Each companion is 100 to 170 parts (about 880 instances for three). A reveal scene may hide a companion that blocks the view (`RevealOcclusion` treats it as scenery).

## Tests (saved in `tests/`)
- `tests/eggs_pool_exclusion.luau`: no exotic in `Config.SPECIES`, 0 leaks in 15,000 normal rolls over all 25 zones, odds sum to 100%, rolls match shown odds (max 0.22 pp over 100k).
- `tests/eggs_persistence.server.luau`: the persistence cases below (25 checks, all pass).

## Persistence tests (no DataStore in Studio)
`Server/Shop` has a Studio-only `Shop._test` hook that swaps the DataStore for a fake one (JSON round-trip like the real one). A temporary script ran these cases, all passed: receipt grants one animal and is idempotent; the same receipt again does not give a second animal; rejoin keeps owned, hatch queue and receipt; a Roblox retry after rejoin does not duplicate; `hatchAck` then rejoin does not replay the hatch; a failed save returns NotProcessedYet and rolls everything back, and the retry grants exactly once; an old save without `exotic` loads; corrupt data (unknown species, negative numbers, wrong types) is dropped; the equip limit and the level clamp are applied on load; a region-restricted profile cannot buy eggs.
A hatch bug found and fixed on the way: the CONTINUE button of the hatch window was wired to the wrong object, so the window could not be closed. Verified with a real click.

## Review of V29 (checker agent)
The inflate decoder was ported to Python and checked against zlib on all 19 pictures and 300 random streams: identical. Fixed from that review: the hatch egg could be empty while the pictures queue was busy (eggs are now unpacked ahead), the fallback was slow when `EditableImage` is off (now an immediate probe), the shop window ignored coin pack amounts, the starter offer and the gift timer while open (now part of the refresh signature, timer in 5-minute steps), and the base64 loop never yielded (fixed).

## Review round (checker agent) and fixes
A separate review agent read the code. Confirmed and fixed: tile texts contradicted the odds (Royal contains 24% Common, Cosmic 24% Rare, Absolute 15% Epic; the texts now say so); the region was resolved after the profile counted as loaded; a failed save rolled back changes made by other requests (two receipts at once could lose a paid egg; now a profile is `busy` while a receipt saves, other receipts and requests wait and Roblox retries them, and the client is not sent unconfirmed state); the hatch queue dropped unplayed hatches after 20 (now 100); the Exotic window rebuilt all portraits every 30 s (now only when the exotic state changes) and dead models blocked the rainbow animation cap (now pruned); text said "SEE ODDS" for a button named ODDS. Re-tested with 25 checks including two receipts at once with a failing save and an error thrown inside the grant (the profile does not stay busy: grant and save run in a `pcall`). The region field name was verified in Play: `ArePaidRandomItemsRestricted` exists and is a boolean.
Not fixed, noted: the bag upgrade preview in the Menus window ignores bonus bag slots (same for the V26 rank bonus); the spear stats shown in Menus do not include exotic range and grip (display only; the throw itself uses them).

## Known limits
- **Not tested with real money.** Only Studio test purchases. Persistence was tested against a fake DataStore, not the real one. There is no session lock: a player who joins a second server before the first one has saved could overwrite a newer save (the same as the rest of the shop profile).
- Screenshots in the Studio session used for testing drew neither ViewportFrames nor the 3D world, so the portraits, the rainbow colour animation, the companions' auras and which way they face were **not seen**. Their structure was checked (objects, emitters, trails, beams, lights and sizes in Play).
- Frame time with 3 companions (about 880 instances): 16.7 ms average with and without them in a Play session. During a hatch the average did not change either.
- The economy is still client-side (`Config.BACKEND = "Demo"`): exotic bonuses come from server-validated state but are applied on the client. For a real-money launch the sums should also be applied on the server (`Config.exoticTotals` works on both sides).

---

# Cartoon shop icons (V27)

Open `SpearHunt V27 - Cartoon Shop.rbxl`. The shop item icons are no longer small 3D models in a viewport (blocky and soft). They are drawn from UI shapes (rounded frames with a gradient, a thick dark outline, glints and sparkles), so they stay sharp at any size and need no uploaded images. Code: `drawCartoon` in `Client/Shop.luau`; the table `CARTOON_KEYS` lists the icons (coin packs, Lucky Charm clover, Market Insight crystal ball, Silver Broker scales, Master Smith anvil and hammer, Master Wrapper gift, VIP and Founder crowns, Golden Hour flask, Jackpot slot machine, Trade Fair stall, Hunter's Bundle, Server Luck globe, bag). To add one, add a key to `CARTOON_KEYS` and a branch in `drawCartoon` (canvas 100 x 100). Spear icons still use the game's 3D spear models. Hunter's Bundle is now a wide banner under Server Luck.

Checked in a live Studio session by looking at screenshots of every section of the shop window. Not checked on small screens.

---

# Supporter ranks and exclusives (V26)

Open `SpearHunt V26 - Supporters.rbxl`. V26 is V25 plus a donation ladder. Tested in a live Studio session (Play): test purchases give the right rank, tag, aura and bag slots, the daily gift pays once and is then locked for 20 hours, and the shop window shows the rank card, Founder banner and bundle. Not tested: real purchases, saving, and how it looks on small screens.

## Supporter rank
The server adds up Robux spent: owned passes by price (so a purchase made on the website counts) plus Developer Product receipts (`CurrencySpent`). In Studio, a test purchase adds the item's price, so ranks can be tried with all ids at 0.

| Rank | Spent | Perks with no free route |
|---|---|---|
| Bronze | 50 R$ | tag and aura, prices recover x1.25 after selling, daily gift 4% |
| Silver | 200 R$ | + 20 bag slots (the free bag stops at 100), recover x1.5, gift 8% |
| Gold | 500 R$ | + 40 bag slots, recover x2, gift 15% |
| Diamond | 1000 R$ | + 60 bag slots, recover x3, gift 25%, Market Insight for free |

Everyone gets a daily gift of 2%. Gift size is a share of the price of your next spear (`Config.shopCoins`), so it stays meaningful at every stage. The timer lives on the server (`prof.shop.lastGift`, 20 hours) and the coins arrive through the same `pending` queue as coin packs, so they are acknowledged and saved once.

## What others see
Every player with a rank, VIP or Founder gets a tag over the head and an aura (particles) on the character, in the rank colour. VIP and rank share one tag. Founder is purple. Done in code, no uploaded assets.

## Founder's Edition (Game Pass, 799 R$)
Purple FOUNDER tag, the strongest aura and +5% on the daily gift. It costs 799 R$, so it also counts as Gold rank. It is a pass on purpose: a pass can be taken off sale, a product can be bought twice. No stock counter or countdown is shown. If you want a cutoff, pick a date and take the pass off sale then.

## Hunter's Bundle (199 R$)
Golden Hour, Jackpot Hour and Trade Fair together for 30 minutes. Bought separately the same time is 79 x1.5 + 99 x1.5 + 59 = 326 R$, so the bundle saves about 40%. It is a normal boost product, so no new purchase code was needed.

## Pace check
Ranks add no coin multipliers. Daily gift at Diamond is 25% of the next spear's price per day, about a quarter of a spear a day, and the extra bag slots only help with big bags. The free-versus-paid table from V25 is unchanged.

## Known limits
- Not run in Studio. Check that the tag and aura show for a ranked player, that "CLAIM" pays out, and that the rank card fits in the shop window.
- Rank bag slots are applied through `Backend.applyPerks()` when the server pushes the shop state; confirm the bag size in the Bag window after a test purchase.
- Pass ids and product ids are still 0. Create the Founder pass and the bundle product too (see "Before launch" below).
- Shop art for Founder and the bundle is not drawn; the shop uses simple 3D icons.

---

# Robux shop and market economy (V25)

Open `SpearHunt V25 - Market.rbxl`. V25 is V24 plus the changes below. It has **not been run in Studio** (see "Known limits"). The older V17/V18 notes further down still describe the shop's look and the pre-launch steps; the passes and products listed there were replaced by V25.

## Rule for every paid item
For each item we ask: "what does a free player do to get this?" Only items with no free equivalent are sold. The old passes failed that test: Golden Purse (coins x2) and Lucky Charm (luck x2) were permanent copies of the Herbalist's coin and luck potions, Titan Training skipped a trivial grind (power from dumbbells comes in minutes), Big Game Bag was a bag upgrade a free player buys for 1M coins, and the three brews were the potions sold for Robux.

## New catalogue (`Config.SHOP`)
| Item | Price (R$) | What it does | Free equivalent |
|---|---|---|---|
| Lucky Charm (pass) | 399 | Rare animal chances +50% forever, luck x2 | none permanent (potion: +25% for 5 min) |
| Market Insight (pass) | 299 | Shows which rarity is in hot demand for the next 6 hours | none, free players see only the current hour |
| Silver Broker (pass) | 349 | Selling many of one animal drops its price far less, and bad-demand hours are floored at x0.9 | none |
| Master Smith (pass) | 399 | Forge levels 6 and 7 (free limit is 5) and forging costs 25% less | none |
| Master Wrapper (pass) | 249 | One bow wraps the whole bag | wrapping one catch at a time |
| VIP Hunter (pass) | 449 | Sell from anywhere, gold tag, +15% XP | walking to the market |
| Golden Hour | 79 | Gold and Rainbow mutations much more common, 20 min of play (chance x3, caps +50%, so at high luck the gain is about +50%) | none |
| Jackpot Hour | 99 | Rare animal chances +100%, 20 min of play | none |
| Trade Fair | 59 | No price drops from selling and demand never below x1, 30 min of play | none |
| Server Luck | 149 | Luck x2 and rare chances +25% for the whole server, 15 min | none |
| Starter Pack | 79 | Iron Spear, 4000 coins, bag level 3, 30 min of Golden Hour; only below level 10 | no |
| Coin packs (4) | 49 to 399 | Coins scaled to the price of your next spear | shortcut, grows with progress |

Removed: Golden Purse, Titan Training, Big Game Bag, Luck Brew, Coin Brew, Hunter's Brew. Their ids were all 0, so nothing live was affected. Boost ids `fortune`, `jackpot` and `fair` exist only in `Config.BOOSTS` for the HUD. Coins cannot buy them.

## Market (`Config.MARKET`, `Config.marketQuote`)
Every sale now goes through the market.
- **Demand per species per hour** is a pure function of server time and the species index, so every player sees the same prices without a server. It changes smoothly between hours. Each hour has a hot rarity (x1.3), a cold rarity (x0.85) and a hot habitat (ground, air or water, x1.2). Every 3 hours one species is in a craze (x1.8) and another in a glut (x0.6). Demand is normalised (x0.92) so the average is 1.02, and clamped to 0.5 to 2.2.
- **Saturation**: every animal of one species sold in a batch multiplies its price by 0.97 (floor 0.5). It recovers by one animal every 20 s. The player's recent sales are saved in `data.market`.
- Items are priced from the most valuable down, so saturation hits cheap ones first. Wrapped items keep x2 and the coin potion x2 is applied last.
- The Bag and Market windows show the market line (current ratio, hot and cold rarity, craze and glut). With Market Insight they also list the hot rarity for the next 6 hours.

Measured on 4000 simulated catches (`Roll.species` with the real data):

| Bag size | Free | Silver Broker | Trade Fair |
|---|---|---|---|
| 12 | x0.97 to 1.00 | x1.02 to 1.05 | x1.09 to 1.10 |
| 45 | x0.90 to 0.94 | x1.00 to 1.03 | x1.08 to 1.11 |
| 100 | x0.82 to 0.89 | x0.97 to 0.99 | x1.07 to 1.10 |

A player with the default bag who sells often is not penalised. Selling a huge batch costs 6 to 18%, which is what the Broker and the Fair remove. Timing the sale to the hot rarity is the free skill.

## Progression balance (what was wrong in V24)
Measured with the real `Roll`/`Config` formulas (EV of a x10 throw in the best zone the spear can still catch):
1. **Zones 1 to 4 were a wall.** Spears 6 to 10 cost 120K to 50M coins while a throw earned 40 to 700, so the next spear took 5,000 to 109,000 throws. From spear 11 it took 32 to 45 throws. Zone 5 species were worth about 3,800 times more than zone 4.
2. **Zones 20 to 25 were uncatchable.** The best spear (Singularity Spire, sharpness 22, power 20) could not take 29 of the 30 species of zones 21 to 25 (they need up to 28 and 26).
3. **Luck did nothing after spear 6.** All rarity caps (`RARITY_CHANCE_CAPS`) are reached at luck 160, so Luck x2 was a no-op. Mutation chance saturates at luck 3,600.

Fixes:
- Species of zones 5 to 25 cost x0.00044 (`Config.PRICE_PHI`), so income grows smoothly after zone 4.
- Spear prices are recomputed: price(j) = income of spear j-1 x T(j), with T from 15 throws (spear 2) to 600 (spear 46). A free player who sells everything unwrapped and uses no potions needs about 10,900 throws for all 46 spears (about 36 hours at 12 s a throw), against roughly 280,000 before. Wrapping every catch (x2) roughly halves that, and the coin potion doubles sales while it runs. Quest, course, egg and level rewards were **not** rebalanced: spears 5 to 10 became 17 to 180 times cheaper, so about 31K coins of quest rewards now cover the first six spears.
- **6 new spears** (41 to 46: Gearwork Pike, Sporebloom Halberd, Boneforged Glaive, Citadel Pearl Lance, Rift Conductor, Primordial Fang) with sharpness 23 to 28 and power 21 to 26 can take every species of zones 20 to 25. They have no models yet: they reuse the Singularity Spire model and its effects profile (`SpearFactoryV15`, `SpearProfilesV15`).
- Spear luck raises the rarity caps (`Config.capLuckMul`: x1.25 at luck 1,000, x2 at 1e6), so late spears matter again.
- Potions cost a share of the income they produce (`Config.potionCost`: 10% for luck, range and grip and 35% for coins, of the income during the potion. It is priced from the best spear you own, so swapping spears does not lower it. The coin potion doubles a whole sale, so it is charged 35% of the larger of that income and the value of the bag at that moment). They were 120 to 260 coins forever and so free from zone 5 on.
- The forge keeps 5 free levels; levels 6 and 7 need Master Smith.

## What a paid item is worth (EV of a throw, free = 1)
| Spear | Charm | Jackpot | Golden | Free luck potion | All paid effects |
|---|---|---|---|---|---|
| Bronze | x1.54 | x1.27 | x1.76 | x1.35 | x4.9 |
| Star | x1.64 | x1.83 | x1.63 | x1.40 | x4.5 |
| Hydra Fangs | x1.27 | x1.42 | x1.33 | x1.16 | x2.2 |
| Singularity Spire | x1.24 | x1.37 | x1.33 | x1.14 | x2.1 |

Timed items last 20 to 30 minutes of play. Only the Charm is permanent.

## Known limits
- **Not run in Studio.** Checked: the new blocks of code compile in Studio's Luau (the market, potion price, catalogue, shop icons, Perks, Roll, the DemoServer sell and forge handlers, the Menus lines and the later fixes; the full files were not compiled as one piece), the market and potion formulas ran in a live Studio session against the real species data, and the calibration used the real `Roll` and `Config`. Not checked: the changed windows (Bag, Market, Forge, Potions, Shop), real purchases, saving, and the effects of the new spears. The Bag and Market market line is long on small screens.
- Spears 41 to 46 look like the Singularity Spire (in the menus, in flight and in the player's hand: `SpearFactoryV15` and `Server/Cosmetics` fall back to that model; there is no model in `Assets.Spears` for them). They need their own models in `V15SpearPresentation/ModelsData`.
- Economy still runs on the client (`Config.BACKEND = "Demo"`). Server-side markets and saturation are the next step before real-money launch.
- The aiming HUD passes the luck to `Backend.capMul(luck)`, so its rarity chances include the new spear luck bonus. The shop tiles for the new items use simple built-in 3D icons; illustrations for them (`shop-art/`) are missing.
- **Old saves.** The DataStore is still `SpearHunt_v1`. A V24 save would keep bag items caught at old prices (about 2,270 times higher for zone 5+). Nothing is published yet, so there are no real saves; bump the key or re-price items on load before the first launch if that changes.
- Zone and species prices of zones 5 to 25 changed, so numbers in saved data and screenshots from V24 do not match. Saved bags keep the price they were caught at.
- All product and pass ids are still 0 (see the steps below).

---

# Robux shop (V17)

Open `SpearHunt V18 - Sky Shop.rbxl` (V17 has the same shop with the old red look). The **SHOP** button is first in the left menu.

## Before launch
1. Creator Dashboard: create 6 Game Passes and 9 Developer Products (list in `Config.SHOP` in `ReplicatedStorage/Shared/Config`).
2. Paste each numeric id into `id = 0` of the matching entry. `id = 0` means "not created yet": in Studio the purchase is simulated, in a live game the button shows SOON.
3. Game Settings > Security > enable **Studio Access to API Services** to test saving.
4. Publish. Prices on buttons are read from Roblox automatically.

## What was added
- `Client/Shop` window, `Client/Perks` (pass/boost math), `Server/Shop` (ProcessReceipt, Game Pass check, DataStore save, server-wide Luck).
- Luck/coin/XP/strength/bag bonuses hooked into `DemoServer`, `Backend`, `Roll` (rare-limit multiplier), `Menus`, `WrapCtl`.
- The DEMO cheat panel now exists only inside Studio.
- Player progress now saves to DataStore `SpearHunt_v1`.

Economy still runs on the client (`Config.BACKEND = "Demo"`); moving it to the server is the next step before real-money launch.

## V18 — Sky Shop (new look)
Open `SpearHunt V18 - Sky Shop.rbxl`. Only `StarterPlayerScripts/Client/Shop` changed; prices, purchases, saving and boosts are untouched. The plain source is in `source/StarterPlayer/StarterPlayerScripts/Client/Shop.luau`.

Style (reference video, adapted to the game): a sunny Forest Edge meadow (hills, trees, flowers, sun) inside the window, a cyan banner with a moving pattern, a red basket on a round badge at top left, gold-lined section bars (Game Passes / Boosts / Coins), colored product tiles with shine sweeps and bobbing 3D icons, wide purple Starter Pack and green Server Luck banners.

Labels: every product has a one-glance label. The big gold line is the benefit ("LUCK ×2", "+60 SLOTS"), the small line is the duration or condition ("forever", "30 min"). Texts live in the `PITCH` table at the top of `Shop.luau`.

Art: `shop-art/` holds cartoon illustrations (thick outline, toon shading, glints) redrawn from the game's own models: the starter spear, the zone-1 animals and the items the shop code builds. Roblox cannot load them from the repo, so they have to be uploaded once:
1. Creator Hub > Assets (Creations) > upload every PNG from `shop-art/` as an **Image**.
2. Put each asset id into `Client/AudioIds` under the key `art_<file name without .png>`, for example `art_charm = "rbxassetid://123456789"` (`tools/upload_to_roblox.py` does steps 1 and 2 for you).
3. Until an id is set, that item falls back to the live 3D model, so nothing breaks.

Motion: the spear tows the "Shop" banner across the window, the meadow unrolls, badge / animals / close button and tiles pop in one by one. Closing folds the meadow up and shrinks the banner away. The opening animation plays once; content refreshes do not replay it.

`preview/shop-preview.html` is an HTML mock of this window; `preview/render/` has the tools that render the game's models to the preview images.

Status: syntax-checked and the file decodes with `rbx_binary`, but it has not been run in Studio. If V18 fails to open, paste `source/.../Shop.luau` into `Client/Shop` of V17.

`tools/patch.py` swaps one script's source inside an `.rbxl` (`python3 tools/patch.py in.rbxl out.rbxl new.luau StarterPlayer/StarterPlayerScripts/Client/Shop`).

## Art ids
Shop art ids are now read from `Client/AudioIds` (keys `art_<name>`). `tools/upload_to_roblox.py` uploads the PNGs from `shop-art/` together with the sounds and writes the ids there.
