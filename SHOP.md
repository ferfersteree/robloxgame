# Robux shop (V17)

Open `SpearHunt V17 - Robux Shop.rbxl`. The **SHOP** button is first in the left menu.

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
