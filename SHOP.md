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
