# Hunter Pass — implementation contract (V71)

Design: `docs/concepts_v70/concepts.md` section 4 and `hunter_pass_ru.md`. Two agents implement it in parallel:
LOGIC agent owns `Shared/Config.luau`, `Client/DemoServer.luau`, `Server/Shop.luau`, `Client/Perks.luau`.
UI agent owns `Client/Menus.luau`, `Client/Hud.luau`, `Client/Shop.luau`.
Neither edits the other's files. Everything below is the interface between them; follow names exactly.

## Economy model (existing, keep it)
- Coins, Strength, quests etc. live in the client economy `Client/DemoServer.luau` (table `d`, handlers `H.X` called by `Backend.call("X", ...)`). It is saved by the server as `prof.save` (client snapshot).
- Robux purchases are server-side (`Server/Shop.luau`, `prof.shop`), pushed to the client as a state table (`Perks.set(state)`, read with `Perks.state()`). Coin deliveries go through `prof.shop.pending` → client `H.ShopGrant(g)` → ack.
- Pet eggs are rolled ONLY on the server (`rollEgg`), boosts (`fortune`, `jackpot`, `fair`) are timed on the server (`prof.shop.boosts`).

## Config (LOGIC agent)
```lua
Config.PASS = {
	name = "Hunter Pass", season = "Pinewatch",
	START = <os.time of 2026-11-17 00:00:00 UTC>, -- season 0 starts here; seasons repeat every DAYS
	DAYS = 28, TIERS = 30, XP_PER_TIER = 300,
	BUNDLE_XP = 3000, BUNDLE_MAX_XP = 6000, -- bundle only offered while xp <= 6000 and premium not owned
	DAILY = { -- 4 sets, set index = (day % 4) + 1; 3 missions each, 100 XP
		{ { id = "dA1", text = "Catch 8 animals", kind = "catch", goal = 8, xp = 100 }, ... },
		...
	},
	WEEKLY = { { id = "w1", text = "Catch 50 animals", kind = "catch", goal = 50, xp = 240 }, ... }, -- 5 missions
	REWARDS = { -- [tier] = { free = { R, ... }, premium = { R, ... } }
		[1] = { free = { { type = "coins", k = 0.25 } }, premium = { { type = "egg", key = "egg_forest" } } },
		...
	},
}
```
Mission `kind`/`arg` match the existing `progress(kind, arg, amount)` calls in DemoServer:
`catch` (no arg), `zone` (arg = zone number, matches when equal), `rarity` (counts when caught rarity >= arg),
`tier` (counts a throw when its multiplier >= arg), `sell` (amount = coins), `wrap` (amount), `train` (amount = reps),
`collect` (arg = "ff" fireflies or "egg" field eggs, prefix match), `range` (amount = points, CUMULATIVE for the pass),
`course` (1 per finish). Mission texts and goals: concepts.md section 4 (daily sets A–D, weekly list).

Reward item `R.type`:
- client side: `coins` (`k` × P, P = price of the most expensive spear the player owns, at least the price of the
  first purchasable spear; round up), `power` (`n` Strength added to `d.power`).
- server side: `egg` (`key` = a Config.SHOP product key of kind "egg"; one free hatch), `boost` (`key` = shop product key
  `fortune20` / `jackpot20` / `fair30`; adds that product's boosts × dur), `tag` (`text`, `color` Color3: a title shown
  over the head when the player has no FOUNDER/rank/VIP tag), `aura` (`name`, `color`: an aura shown when the player has
  no other aura).
A lane's items are either all client side or all server side (tier 30 premium = egg_storm + aura, both server side).
Helper functions (pure, usable on both sides):
```lua
Config.passSeason(now: number?): (number, number, number)  -- season index n (>=0), seasonStart, seasonEnd (unix)
Config.passDay(now: number?): number   -- day index inside the season, 0..DAYS-1
Config.passWeek(now: number?): number  -- 0..3
Config.passTier(xp: number): number    -- floor(xp / XP_PER_TIER), clamped 0..TIERS
Config.passDaily(now: number?): { any } -- today's 3 missions
Config.passSide(r: { any }): "client" | "server"
```
Two new developer products in `Config.SHOP.PRODUCTS` (id = 0 → simulated in Studio via `testBuy`):
`{ key = "pass_premium", id = 0, price = 299, kind = "hpass", name = "Hunter Pass Premium", desc = ... }`
`{ key = "pass_bundle", id = 0, price = 499, kind = "hpass", xp = 3000, name = "Hunter Pass + 10 Tiers", desc = ... }`
(The shop catalogue must NOT list kind "hpass"; the pass window sells them.)

## Client save: `d.hpass` (LOGIC agent; must be in DemoServer `defaults()` so `Demo.load` keeps it, and validated in load)
```lua
d.hpass = {
	season = -1, xp = 0,
	day = -1, week = -1,             -- which day/week the mission progress below belongs to
	prog = { [missionId] = number }, -- progress of today's daily + this week's weekly missions
	done = { [missionId] = true },   -- missions already credited (no double XP)
	claimed = { ["f12"] = true, ["p3"] = true }, -- CLIENT-side rewards claimed: lane letter f/p .. tier
}
```
Rollover (inside DemoServer, run at every pass handler and in progress): season changed → reset everything
(xp 0, claimed {}); day changed → clear daily prog/done; week changed → clear weekly prog/done.
Mission completion credits XP immediately and emits `emitFn("hpass", { text = mission.text, xp = mission.xp, tier = newTier, tierUp = bool })`.

DemoServer handlers (LOGIC):
- `H.HpassSync()` → rollover, returns `true, d.hpass`.
- `H.HpassClaim(tier, lane)` → client-side lanes only. Checks: 1 <= tier <= Config.passTier(d.hpass.xp); lane "f" or "p";
  for "p" `Perks.hpassPremium()` must be true; not already in `d.hpass.claimed`; lane side is "client".
  Grants coins/power, marks claimed, returns `true, { coins = n, power = n }`; else `false, "reason"`.
- `H.ShopGrant` gains `g.kind == "hpassxp"`: if `g.season == current season` add `g.xp` to `d.hpass.xp` (after rollover). returns `true, 0`.

## Server (LOGIC agent, Server/Shop.luau)
- `prof.shop.hpass = { season = n, premium = bool, claimed = { ["p1"] = true } }` (server-side claims), reset when the
  season changes. `prof.shop.hpassCos = { tags = { text... }, tag = text?, tagColor = {r,g,b}?, aura = {r,g,b}?, auraName = string? }`
  (cosmetics are permanent; the latest earned is worn).
- `applyProduct` kind "hpass": set current season, premium = true; if `item.xp` insert pending
  `{ id = purchaseId, kind = "hpassxp", xp = item.xp, season = n, key = item.key }`.
- `stateOf` adds `hpass = { season = n, premium = bool, claimed = {...} }` for the CURRENT season (premium false / claimed {}
  if the stored season is old) and `hpassCos = prof.shop.hpassCos`.
- new `onInvoke` action `"hpassClaim"` (a = tier, b = lane): server-side lanes only; checks tier int 1..TIERS, lane f/p,
  premium for p, `prof.save.hpass.season == n` and `Config.passTier(capped xp) >= tier` (see Hardening), not claimed; grants
  (egg → `rollEgg(prof, Config.SHOP_BY_KEY[key], "hpass_" .. n .. "_" .. lane .. tier)`, boost → like applyProduct boost,
  tag/aura → hpassCos), marks claimed, `saveProfile`, `refreshVip`, `push`, then `ShopEv:FireClient(player, "hpassGranted", { tier = tier, lane = lane })`;
  returns `true`. Otherwise `false`.
- `badgeOf`: if no founder/rank/vip badge and `hpassCos.tag` → that tag, colour `hpassCos.tagColor`; aura from `hpassCos.aura`
  when there is no other aura.

## Perks (LOGIC agent, Client/Perks.luau)
`Perks.hpassPremium(): boolean` (state.hpass.premium and state.hpass.season == Config.passSeason()),
`Perks.hpassServerClaimed(key: string): boolean`.

## UI (UI agent)
- `Hud.luau`: new left-menu entry `{ "pass", "🎟️", "Pass", Color3.fromRGB(244, 181, 48) }` after Quests (also in the
  compact phone grid). Badge on it = number of claimable rewards (unlocked tiers not claimed: free lane always, premium lane
  only if `Perks.hpassPremium()`; claimed = `d.hpass.claimed[key]` or `Perks.hpassServerClaimed(key)`), refreshed on
  `Hud.refresh(d)` and on Perks state changes if available. Keep everything else in Hud unchanged.
- `Menus.luau`: `function Menus.pass()` opens the window (Hud.MenuClicked dispatch calls `Menus[name]`). Layout after
  `docs/concepts_v70/battle_pass.jpg`: header (season name, pass level shield, XP bar `xp % 300 / 300`, "Season ends in"
  countdown), horizontally scrolling track of 30 columns with a FREE row and a gold PREMIUM row, tile states: claimed
  (check), ready (glow + "CLAIM"), locked (lock / "Tier N"), premium-locked (lock + "PREMIUM"). Right column: Missions
  with Daily (3) and Weekly (5) lists, progress bars, XP chips, completed ones ticked. Bottom: "Get Premium  R$ 299" and,
  when eligible, "Premium + 10 Tiers  R$ 499" (hidden when premium owned). Text English. Calls `Backend.call("HpassSync")`
  on open.
  Claim: client-side lane → `Backend.call("HpassClaim", tier, lane)`; server-side lane → `Shop.hpassClaim(tier, lane)`.
- `Client/Shop.luau` (small additions only): `function Shop.buyKey(key: string)` (calls the existing local `buy`),
  `function Shop.hpassClaim(tier: number, lane: string): boolean` (first `saveNow()` so the server sees the latest xp,
  then `ShopFn:InvokeServer("hpassClaim", tier, lane)`), handle `onEvent("granted", "pass_premium"/"pass_bundle")`
  (kind "hpass": unlock screen or banner, no `item.dur`), handle `onEvent("hpassGranted", ...)` (toast / refresh the pass
  window through `Menus.refresh` is not reachable — just `UI.toast`), and make sure `renderBody` skips kind "hpass".
- Toast on the `"hpass"` Backend event (mission done: "+100 Pass XP · Catch 8 animals", tier up: banner "PASS TIER N!").
  Put the listener in Menus.luau (`Backend.onEvent`).

## Hardening and extra requirements (both agents read this — it overrides anything above)
- NAMING: `pass`/`passes`/`item.pass` already mean Roblox Game Passes in this codebase. Everything of the Hunter Pass uses
  `hpass` (product kind "hpass", `prof.shop.hpass`, `prof.shop.hpassCos`, state fields `hpass`/`hpassCos`, save field
  `d.hpass`, Backend event "hpass", pending kind "hpassxp", server action "hpassClaim", client event "hpassGranted").
  The menu key stays "pass" (`Menus.pass`, Hud MENU entry "pass"). Config helpers keep the `Config.pass*` names above.
- CLOCK: every `Config.pass*` helper defaults `now` to `Config.marketNow()` (server-synced `workspace:GetServerTimeNow()`),
  never plain `os.time()`, so client and server agree on season/day/week.
- SERVER PERSISTENCE: add `hpass = { season = -1, premium = false, claimed = {} }`, `hpassCos = {}`, `hpassBundleXp = 0`
  to `newShop()` AND copy/validate them in `loadProfile` (it whitelists saved shop fields: boosts, starter, spent, lastGift,
  exotic, receipts, pending, test — around lines 380–425). Without that, premium is lost on rejoin.
- XP TRUST: `prof.save` is whatever the client sent. In `hpassClaim` cap the xp:
  `min(TIERS*XP_PER_TIER, (day+1)*300 + (week+1)*1200 + bundleXp)` with day/week from `Config.passDay()/passWeek()` and
  bundleXp = `prof.shop.hpassBundleXp` (set to item.xp by a bundle purchase in the current season, reset with the season).
  Validate `tier` (integer, 1..TIERS, not NaN) and `lane` ("f"/"p"). Mark the reward claimed BEFORE any yielding call
  (saveProfile) and roll the mark back if granting errors.
- EGGS OFF: when `prof.eggsOff`, an egg reward becomes a coin delivery instead: insert pending
  `{ id = "hpass_<n>_<lane><tier>", kind = "coins", k = 0.5, key = "hpass" }` and still mark it claimed. The UI shows egg
  tiles with an ODDS button: add a `Shop.openOdds(key)` export in Client/Shop.luau that calls the existing local `openOdds`.
- `Shop.hpassClaim`: `saveNow()` can return false (save in flight, 1 s server throttle). Retry up to ~5 times with 0.6 s
  waits; if the server still refuses, `UI.toast` "Try again in a moment". Return boolean.
- REFRESH HOOK: `Shop.onHpassChange: (() -> ())?` — Menus sets it while the pass window is open; Client/Shop calls it
  from `onEvent("state")`, from `onEvent("granted")` for kind hpass and from `onEvent("hpassGranted")`.
- STUDIO TEST CHEAT: DemoServer handler `H.HpassDebugXp(n)` (adds n pass xp; only when
  `game:GetService("RunService"):IsStudio()`), and in Menus `renderDemo` a button "+300 PASS XP" calling it. Server
  `hpassClaim` skips the xp cap when `IS_STUDIO`, so the cheat can be tested end to end.
- MENU HEIGHT: with Pass the desktop left menu has 8 rows (+ DEMO in Studio = 9). It must fit a 1920×811 screen
  (canvas ≈ 820 units tall; the top bar ends at y≈86, the menu starts at y≈108): shrink rows when there are more than 7
  entries (e.g. 52 px rows, 8 px gaps).
- Mission XP is credited on completion only; `range` counts cumulative points for the pass even though quests use max.
- Coins P (k × P): price of the most expensive OWNED spear at claim time (documented simplification).
- NOT built (mention in reports): auto-grant of unclaimed rewards at season end.
- Do not call the Skill tool (the user asked not to use skills). Work from the code and these docs.
