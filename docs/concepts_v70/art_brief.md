# UI art brief (V71)

The owner rejected the V70 UI because it was drawn from code primitives and does not look like the concept art.
Now the real art exists in the game as uploaded Roblox images. Rebuild the screen so that it looks **exactly like the concept**:
same layout, same proportions, same frames, buttons and icons. Live text (numbers, names, prices) is drawn by the game font
(FredokaOne, white, dark outline via `UI.label`); everything else that is a picture in the concept must be an art sprite.
No emoji where a sprite exists.

## API (Client/UIKit.luau, already written; do not edit UIKit)
```lua
UI.art(key, { Size, Position, AnchorPoint, ZIndex, LayoutOrder, Name, Parent, Rotation, Color, Transparency, Slice, SliceScale, Fit, Crop }) --> ImageLabel
UI.artButton(key, { ...same..., Text, TextSize, TextColor, Sound }, onClick) --> ImageButton  -- hover/press scale + sound; attribute "Enabled"; child TextLabel "Label"
UI.artApply(imageObject, key, slice?, sliceScale?)   -- re-skin an existing ImageLabel/ImageButton
UI.artSize(key) --> Vector2  -- sprite pixel size, for aspect ratios
```
- Default is Stretch: give the element the same aspect ratio as the sprite (sizes below) or it will look squashed.
- `Slice = n` or `{left, top, right, bottom}` (pixels of the sprite kept unstretched at each edge) makes a 9-slice frame: use it for panels,
  bars and any button whose aspect differs a lot from the sprite. Rounded-button sprites: slice about 40% of the sprite height on the left and right.
  `SliceScale` shrinks the border (e.g. 0.6) when the element is smaller than the sprite.
- `Fit = true` for icons (keeps aspect inside the box), `Crop = true` for backgrounds (pass_header, shop_banner).
- An ImageLabel does not clip children to its rounded shape: keep content inside the frame's inner area. To crop a background to rounded
  corners put it in a Frame with ClipsDescendants and a UICorner is NOT enough (UICorner does not clip children): overlay a frame sprite on top instead.
- Icons sit on top of frames with a higher ZIndex. All sprites have transparent backgrounds except `pass_header` and `shop_banner`.
- `UI.badge(btn, n)`, `UI.setText(btn, text)`, `UI.punch`, `UI.shine`, `UI.tween` work on art buttons too.
- Do not call the Skill tool. Do not edit UIKit.luau. Do not create new files. Comments in Russian, short. UI text English.

## Sprites (key, width x height, what it is)
- `badge` 54x54: round dark icon badge
- `bar_cyan` 238x21: bar fill
- `bar_green` 238x21: bar fill
- `bar_purple` 236x21: bar fill
- `bar_track` 244x23: dark progress bar track
- `broker` 200x170: silver coins and scale (Silver Broker)
- `btn_big` 601x109: big glossy green button
- `btn_blue` 275x74: same shape as its siblings, colour in the name
- `btn_buy` 340x119: glossy green price button blank
- `btn_green` 276x74: same shape as its siblings, colour in the name
- `btn_grey` 239x64: same shape as its siblings, colour in the name
- `btn_orange` 276x74: same shape as its siblings, colour in the name
- `btn_purple` 237x64: same shape as its siblings, colour in the name
- `btn_red` 276x74: glossy menu button blank
- `btn_x` 122x120: red rounded-square close button with white X
- `btn_yellow` 237x64: same shape as its siblings, colour in the name
- `charm` 198x200: clover charm (Lucky Charm)
- `chip_blue` 277x91: same, blue
- `chip_dark` 206x81: dark rounded chip with thin yellow-green border (odds)
- `chip_gold` 280x91: top stat chip frame, gold, teal riveted border
- `chip_red` 278x91: same, coral
- `chip_violet` 279x90: same, violet
- `chip_xp` 216x76: gold XP chip
- `coins_chest` 200x168: coin chest (coins3)
- `coins_crate` 200x189: coin crate (coins2)
- `coins_satchel` 200x167: coin satchel (coins1)
- `coins_vault` 200x191: vault with coins and gems (coins4)
- `egg_amber` 180x200: amber egg (egg_amber)
- `egg_forest` 178x200: green leaf egg (egg_forest)
- `egg_tide` 190x200: teal pearl egg (egg_tide)
- `founder` 200x187: purple shield with star (Founder)
- `ic_bag` 181x200: blue backpack (Bag stat)
- `ic_bag2` 186x200: blue backpack (Bag button)
- `ic_coin` 192x200: gold coin with star (Coins)
- `ic_deer` 179x200: deer head (Animals)
- `ic_gear` 200x199: cog (Settings)
- `ic_pass` 200x168: golden ticket (Pass)
- `ic_potion` 146x200: red potion (Potions)
- `ic_power` 191x200: flexed arm (Strength)
- `ic_quests` 186x200: quest scroll with checks
- `ic_shop` 200x192: shop stall (Shop button)
- `ic_spear` 185x200: spear (Spears button, hotbar)
- `ic_star` 200x196: gold star (Level)
- `insight` 200x168: market map with chart (Market Insight)
- `leaves` 145x65: two green leaves (heading ornament)
- `p_aura` 200x186: sparkle ring (aura reward)
- `p_calendar` 195x200: calendar (daily/weekly header)
- `p_check` 198x166: green check
- `p_clock` 173x200: stopwatch
- `p_coins` 200x145: coin stack (coins reward)
- `p_dice` 200x160: dice (Jackpot Hour boost)
- `p_dumbbell` 200x136: dumbbell (train)
- `p_egg_amber` 174x200: amber maple egg
- `p_egg_forest` 175x200: green pine egg
- `p_egg_storm` 175x200: blue lightning egg (egg_storm)
- `p_fair` 200x191: tent (Trade Fair boost)
- `p_free` 191x191: white gift (FREE lane)
- `p_lock` 172x200: gold padlock
- `p_paw` 200x177: paw (catch missions)
- `p_potion` 181x200: golden hourglass potion (boost reward)
- `p_power` 200x180: golden arm (Strength reward)
- `p_premium` 200x132: crown with laurels (PREMIUM lane)
- `p_rope` 200x154: rope (wrap)
- `p_tag` 200x120: green pennant tag (tag reward)
- `p_target` 200x199: target (tier / range)
- `p_x` 120x119: red close button
- `panel_menu` 261x724: tall dark-teal panel with teal wooden border and rope-tied corners (left menu)
- `panel_quests` 413x321: same style, landscape (quest tracker; also good for generic windows)
- `pennant` 145x91: dark green tier tab on a gold rod
- `potion_clover` 157x200: purple potion, clover (Jackpot Hour)
- `potion_hands` 157x200: blue potion, handshake (Trade Fair)
- `potion_people` 159x200: green potion, people (Server Luck)
- `potion_sun` 158x200: orange potion, sun (Golden Hour)
- `potion_target` 159x200: red potion, target (Hunter Bundle)
- `row_cream` 491x82: cream mission row, gold rim
- `shield` 272x234: green level shield with gold laurels, empty centre
- `shop_header` 1000x151: lime striped header bar with leaves and the baked word "Shop"
- `slot` 151x143: hotbar slot, dark teal
- `slot_sel` 152x155: selected hotbar slot, cyan glow
- `smith` 200x187: anvil and hammer (Master Smith)
- `starter` 191x200: gift box with spear (Starter Pack)
- `tile_blue` 324x181: same shape as its siblings, colour in the name
- `tile_free` 227x219: light-green reward tile
- `tile_green` 440x188: wider tile with rays
- `tile_orange` 324x179: tile background with light rays
- `tile_premium` 234x220: gold reward tile with rays
- `tile_purple` 323x180: same shape as its siblings, colour in the name
- `tile_red` 440x188: wider tile with rays
- `timer` 348x92: brown wooden plaque with stopwatch at left
- `vip` 200x160: crown (VIP Hunter)
- `wood_panel` 821x255: wooden panel, gold bevel frame, maple leaves in top corners
- `wrap` 200x194: gift with pink bow (Master Wrapper)
- `xp_fill` 596x48: green XP bar (same size, gold rim)
- `xp_track` 596x48: dark XP bar track, gold rim
- `pass_header` 1024x256: opaque header scene with the baked title "Hunter Pass" on a wooden plaque with antlers
- `shop_banner` 1024x341: opaque sunlit forest clearing (featured banner and tile backgrounds)

Previews of every sheet on a dark background: `ui-art/preview/*_view.jpg`. Concepts: `docs/concepts_v70/*.jpg`.
Current look (before): `ui-art/preview/before_hud.jpg`, `ui-art/preview/before_shop.jpg`.

## V74 sprites (sheet 6: stall windows, pets, potions)
Concepts: `docs/concepts_v74/stall_market.jpg`, `docs/concepts_v74/bag_pets.jpg`. Previews: `ui-art/preview/stall_frames_view.jpg`, `stall_icons_view.jpg`.
- `sign_wood` 491x97: wooden signboard plank with rivets (window header; UI.window already draws it with the window icon and title)
- `cell_dark` 327x79: dark teal info cell with thin teal border (stat cells like "In your bag: 2")
- `row_slate` 446x80: slate-blue row panel (upgrade rows, list rows)
- `tab_on` 170x77 gold tab (selected), `tab_off` 174x77 dark-blue tab (unselected)
- `card_1` .. `card_7` about 172x202: item/pet card frames by rarity index: 1 grey common, 2 green uncommon, 3 blue rare, 4 purple epic, 5 gold legendary, 6 red-pink mythic, 7 cream divine
- `arrow_l`, `arrow_r` 107x82: grey page arrow buttons; `pill_dark` 183x65: dark page pill
- `egg_astral` 198x200: Astral Core Egg; `st_market`, `st_herbalist`, `st_armory`, `st_forge` about 180x180: stall icons
- `ic_bagup` backpack with bedroll (bigger bag), `ic_net` catch net (Catch tab), `ic_paw` green paw (Pets), `p_shards` teal crystal shards (pet shards), `ic_sell` coins with green arrow (sell)
- `gem_1` .. `gem_7` about 110px: rarity gems in the same order as the cards (market price chips "Epic x1.3": use the purple `chip_violet`/blue `chip_blue` frames from sheet 1 with a gem)
- `potion_coin` (Coins x2), `potion_bow` (Range +25%), `potion_arm` (Steady Grip), and `potion_clover` from the shop sheet (Luck x2): the four Herbalist potions
