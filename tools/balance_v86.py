#!/usr/bin/env python3
"""V86 balance table: strength levels, dumbbells and spear reach, computed the same way as Config.luau.

    python tools/balance_v86.py            # prints the table
    python tools/balance_v86.py --md FILE  # also writes it as Markdown

Reads Config.ZONES, Config.SPEARS, Config.STRENGTH and Config.DUMBBELL from source/ReplicatedStorage/Shared/Config.luau
and repeats Config.range / Config.spearMaxZone / Config.strengthXp in Python. For every spear it shows:
  reach    - farthest zone whose Common the spear still takes (Config.spearMaxZone). Since V88 it no longer caps the flight
  lvl/str  - the strength level (and Strength) a full-charge throw needs to hit that cap
  zone-in  - the level a full-charge throw needs to enter the spear's zone
  dumbbell - the best dumbbell that costs at most 50% of the spear price (what a player buying this spear can afford)
  reps/min - reps and minutes (1.1 s per auto rep) from the previous spear's cap level to this one with that dumbbell
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "source/ReplicatedStorage/Shared/Config.luau").read_text(encoding="utf-8")


def block(name: str) -> str:
    i = SRC.index(name)
    j = SRC.index("\n}\n", i)
    return SRC[i:j]


def num(line: str, key: str) -> float | None:
    m = re.search(r"\b" + key + r" = ([0-9.e+]+)", line)
    return float(m.group(1)) if m else None


def rows(name: str) -> list[str]:
    return [l for l in block(name).split("\n") if l.strip().startswith("{")]


ZONES = [dict(id=int(num(l, "id")), name=re.search(r'name = "([^"]+)"', l).group(1), frm=num(l, "from"), to=num(l, "to"))
         for l in rows("Config.ZONES = {")]
SPEARS = [dict(id=re.search(r'id = "(\w+)"', l).group(1), price=num(l, "price"), range=num(l, "range"), zone=int(num(l, "zone")),
               sharp=num(l, "sharp"), heavy=num(l, "heavy"))
          for l in rows("Config.SPEARS = {")]
SPECIES = [dict(zone=int(num(l, "zone")), rarity=int(num(l, "rarity")), sharp=num(l, "sharp"), weight=num(l, "weight"))
           for l in rows("Config.SPECIES = {")]
DUMB = [dict(cost=num(l, "cost"), gain=num(l, "gain"), name=re.search(r'name = "(\w+)"', l).group(1))
        for l in rows("Config.DUMBBELL = {")]
st = block("Config.STRENGTH = {")
S = {k: num(st, k) for k in ("start", "perLevel", "xpBase", "xpGrowth", "levelsPerZone", "maxLevel")}
MAX_LEVEL = int(S["maxLevel"])
MAX_DIST = float(re.search(r"Config.MAX_THROW_DISTANCE = (\d+)", SRC).group(1))


def strength_of(L: int) -> float:
    return S["start"] + S["perLevel"] * (min(max(1, L), MAX_LEVEL) - 1)


def strength_xp(L: int) -> float:
    return max(1, math.floor(S["xpBase"] * S["xpGrowth"] ** (max(1, L) - 1) + 0.5))


def range_pts():
    step = S["perLevel"] * S["levelsPerZone"]
    first = {}
    for sp in SPEARS:
        first.setdefault(sp["zone"], sp["range"])
    pts = [(S["start"], 25.0)]
    for z in range(2, len(ZONES) + 1):
        zn = ZONES[z - 1]
        pts.append((S["start"] + step * (z - 1), (zn["frm"] + zn["to"]) * 0.5 / first.get(z, 1)))
    pts.append((S["start"] + step * len(ZONES), ZONES[-1]["to"] / SPEARS[-1]["range"]))
    return pts


PTS = range_pts()


def rng(p: float) -> float:
    p = max(p, 1)
    if p <= PTS[0][0]:
        return PTS[0][1] * math.sqrt(p / PTS[0][0])
    for (a, ra), (b, rb) in zip(PTS, PTS[1:]):
        if p <= b:
            t = (p - a) / (b - a)
            return ra * (rb / ra) ** t
    return PTS[-1][1]


def max_zone(sp) -> int:
    """Config.spearMaxZone: farthest zone whose Common the spear can take (never below its own zone)."""
    best = sp["zone"]
    for a in SPECIES:
        if a["rarity"] == 1 and best < a["zone"] <= len(ZONES) and a["sharp"] <= sp["sharp"] and a["weight"] <= sp["heavy"]:
            best = a["zone"]
    return best


def reach(sp) -> float:
    return min(ZONES[max_zone(sp) - 1]["to"] - 0.01, MAX_DIST)


def level_for(dist: float, spear_range: float) -> int:
    L = 1
    # like the game: Strength stops at STRENGTH.maxLevel; a cap past max-strength reach is shown at maxLevel
    while rng(strength_of(L)) * spear_range < dist and L < MAX_LEVEL:
        L += 1
    return L


def xp_between(a: int, b: int) -> float:
    return sum(strength_xp(L) for L in range(a, b))


def short(x: float) -> str:
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if x >= div:
            return f"{x / div:.3g}{suf}"
    return f"{x:.0f}"


def table() -> list[str]:
    out = ["| # | spear | price | zone | reach | zone-in lvl | cap lvl (Str) | dumbbell (gain) | reps | min |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    prev_cap = 1
    assert all(b[1] > a[1] for a, b in zip(PTS, PTS[1:])), "range table must grow"
    assert all(b["gain"] > a["gain"] and b["cost"] > a["cost"] for a, b in zip(DUMB, DUMB[1:])), "dumbbells must grow"
    for i, sp in enumerate(SPEARS, 1):
        z = ZONES[sp["zone"] - 1]
        cap = level_for(reach(sp), sp["range"])
        zin = level_for(z["frm"], sp["range"])
        k = max(j for j, d in enumerate(DUMB) if d["cost"] <= 0.5 * sp["price"] or j == 0)
        d = DUMB[k]
        lo = max(prev_cap, 1)
        reps = xp_between(lo, cap) / d["gain"] if cap > lo else 0
        out.append(f"| {i} | {sp['id']} | {short(sp['price'])} | {sp['zone']} {z['name']} | {reach(sp):.0f} (z{max_zone(sp)}) | {zin} | {cap} ({strength_of(cap):.0f}) | "
                   f"{k + 1} {d['name']} ({short(d['gain'])}) | {reps:.0f} | {reps * 1.1 / 60:.1f} |")
        prev_cap = max(prev_cap, cap)
    return out


if __name__ == "__main__":
    lines = table()
    print("\n".join(lines))
    if "--md" in sys.argv:
        path = Path(sys.argv[sys.argv.index("--md") + 1])
        head = ["# V86 balance: strength levels, dumbbells, spear reach", "",
                "Generated by `python tools/balance_v86.py --md docs/balance_v86.md` from `Config.luau`.", "",
                f"Strength = {S['start']:.0f} + {S['perLevel']:.0f} per level. XP to the next level = {S['xpBase']:.0f} x {S['xpGrowth']}^(level-1). "
                "A dumbbell gives its gain in XP per rep. V88: the spear no longer caps the flight (Config.spearReach is the end of the world), "
                "so the *reach* column is only the farthest zone whose Common animal the spear can still take (animals farther out can escape: too tough / too heavy).", "",
                "*cap lvl*: the strength level at which a full-charge throw reaches the spear's cap. *reps / min*: training from the "
                "previous spear's cap level to this one with the best dumbbell that costs at most half the spear price (auto rep every 1.1 s).", ""]
        path.write_text("\n".join(head + lines) + "\n", encoding="utf-8")
        print("written", path)
