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

Game assets used: the flying spear is the real starter spear model, the animals (rabbit, squirrel, hedgehog, fox, dodo, moon rabbit) are the real models from `ReplicatedStorage/Animals`, shown in viewports. Small animals peek out from behind the banner and walk across the meadow.

Motion: the spear tows the "Shop" banner across the window, the meadow unrolls, badge / animals / close button and tiles pop in one by one. Closing folds the meadow up and shrinks the banner away. The opening animation plays once; content refreshes do not replay it.

`preview/shop-preview.html` is an HTML mock of this window; `preview/render/` has the tools that render the game's models to the preview images.

Status: syntax-checked and the file decodes with `rbx_binary`, but it has not been run in Studio. If V18 fails to open, paste `source/.../Shop.luau` into `Client/Shop` of V17.

`tools/patch.py` swaps one script's source inside an `.rbxl` (`python3 tools/patch.py in.rbxl out.rbxl new.luau StarterPlayer/StarterPlayerScripts/Client/Shop`).
