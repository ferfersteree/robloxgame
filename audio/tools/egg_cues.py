"""Single source of truth for the sound of the egg opening (V39).

From here the build script generates
  * the Luau tables inside Client/Sfx.luau (banks, fallbacks, volumes) and Client/EggOpen3D.luau (cue rules, beats),
  * the AudioIds keys, and
  * the preview page (a simulation of the opening that plays every sound at the moment the game would).

The matching logic of the game is written once in Luau (EggOpen3D.luau); `simulate()` below mirrors it so that the
preview shows what the game does. Keep the two in step when you change one.
"""
import re

# ------------------------------------------------------------------ banks: what Sfx.play(<bank>) plays
# bank -> (files, fallback bank that already exists in the game, default volume)
# fallback = what the game plays until the new file is uploaded (nothing if None, for loops and music)
BANKS = {
    "egg_appear": (["egg_appear"], "sparkle", 0.5),
    "egg_knock": (["egg_knock_1", "egg_knock_2"], "tick", 0.5),
    "egg_riser_forest": (["egg_riser_forest"], "whoosh", 0.5),
    "egg_riser_amber": (["egg_riser_amber"], "whoosh", 0.5),
    "egg_riser_tide": (["egg_riser_tide"], "whoosh", 0.5),
    "egg_riser_storm": (["egg_riser_storm"], "whoosh", 0.5),
    "egg_riser_astral": (["egg_riser_astral"], "whoosh", 0.5),
    "egg_crack": (["egg_crack_1", "egg_crack_2"], "hit_wood", 0.75),
    "egg_boom_s": (["egg_boom_s"], "pop", 0.7),
    "egg_boom_m": (["egg_boom_m"], "boom", 0.8),
    "egg_boom_l": (["egg_boom_l"], "boom", 0.9),
    "egg_burst_s": (["egg_burst_s"], "sparkle", 0.5),
    "egg_burst_m": (["egg_burst_m"], "sparkle", 0.55),
    "egg_burst_l": (["egg_burst_l"], "sparkle", 0.6),
    "egg_thunder": (["egg_thunder"], "thunder", 0.7),
    "egg_divine": (["egg_divine"], "thunder", 0.8),
    "forest_snap": (["forest_snap_1", "forest_snap_2"], "hit_wood", 0.55),
    "forest_leaves": (["forest_leaves"], "rustle", 0.6),
    "forest_shimmer": (["forest_shimmer"], None, 0.28),
    "amber_note": (["amber_note"], "ping", 0.55),
    "amber_inflow": (["amber_inflow"], None, 0.26),
    "amber_sun": (["amber_sun"], "level", 0.5),
    "amber_shard": (["amber_shard_1", "amber_shard_2"], "pickup", 0.5),
    "tide_bubbles": (["tide_bubbles"], None, 0.3),
    "tide_splash": (["tide_splash"], "whoosh", 0.7),
    "tide_pop": (["tide_pop_1", "tide_pop_2"], "pop", 0.5),
    "tide_ring": (["tide_ring"], "pop", 0.5),
    "storm_crackle": (["storm_crackle"], None, 0.5),
    "storm_zap": (["storm_zap_1", "storm_zap_2"], "sparkle", 0.6),
    "storm_clamp": (["storm_clamp"], "hit_wood", 0.6),
    "storm_thunder": (["storm_thunder"], "thunder", 0.8),
    "storm_arcs": (["storm_arcs"], None, 0.3),
    "astral_twinkle": (["astral_twinkle"], None, 0.3),
    "astral_ring": (["astral_ring"], "level", 0.55),
    "astral_burst": (["astral_burst"], "win", 0.6),
    "astral_split": (["astral_split"], "whoosh", 0.6),
    "egg_flash": (["egg_flash"], "sparkle", 0.5),
    "egg_ring_s": (["egg_ring_s"], "pop", 0.3),
    "egg_ring_l": (["egg_ring_l"], "whoosh", 0.4),
    "pet_emerge": (["pet_emerge"], "whoosh", 0.7),
    "pet_trail": (["pet_trail"], None, 0.22),
    "pet_land_s": (["pet_land_s"], "land", 0.6),
    "pet_land_m": (["pet_land_m"], "land", 0.7),
    "pet_land_l": (["pet_land_l"], "land", 0.75),
    "pet_slowmo": (["pet_slowmo"], "whoosh", 0.6),
    "egg_shafts": (["egg_shafts"], "whoosh", 0.5),
    "egg_halo": (["egg_halo"], "level", 0.55),
    "egg_orbit": (["egg_orbit"], "whoosh", 0.5),
    "pet_tap": (["pet_tap_1", "pet_tap_2"], "pop", 0.5),
    "egg_skip": (["egg_skip"], "swoosh", 0.5),
    "egg_reveal_0": (["egg_reveal_0"], "win", 0.62),
    "egg_reveal_1": (["egg_reveal_1"], "win", 0.62),
    "egg_reveal_2": (["egg_reveal_2"], "win", 0.62),
    "egg_reveal_3": (["egg_reveal_3"], "win", 0.62),
    "egg_reveal_4": (["egg_reveal_4"], "level", 0.62),
    "egg_reveal_5": (["egg_reveal_5"], "level", 0.62),
    "egg_reveal_6": (["egg_reveal_6"], "level", 0.62),
    "egg_card": (["egg_card"], "stamp", 0.5),
    "egg_new": (["egg_new"], "coin", 0.6),
    "egg_dupe": (["egg_dupe"], "tick", 0.55),
    "egg_music_a": (["egg_music_a"], None, 0.2),
    "egg_music_b": (["egg_music_b"], None, 0.2),
    "egg_surge": (["egg_surge"], None, 0.34),
}

# ------------------------------------------------------------------ reaction to the events of EggOpenings (type: burst, ring, flash, bolt, stream)
# A rule fires for an event when all its conditions hold:
#   g = group prefix, nog = event has no group, c0/c1 = count range, r0/r1 = range of the ring's end radius (studs/unit)
# Action: name = bank (one-shot), loop = bank (looped layer, stopped at the stream's end), silent = swallow the event.
# Pitch: pitches = list indexed by how many times the rule fired, or base * step^(n-1); jit = random +- share (default 0.03).
# If no rule of the family matches, the first matching rule of `generic` plays.
CUES = {
    "generic": {
        "flash": [dict(name="egg_flash", vol=0.45)],
        "ring": [dict(r0=3.5, name="egg_ring_l", vol=0.35), dict(name="egg_ring_s", vol=0.3)],
        "burst": [dict(c0=20, name="egg_burst_m", vol=0.4), dict(c0=8, name="egg_burst_s", vol=0.35), dict(name="egg_burst_s", vol=0.2)],
        "bolt": [dict(name="storm_zap", vol=0.45)],
    },
    "forest": {
        "stream": [dict(loop="forest_shimmer", vol=0.28, fade=0.6)],
        "burst": [
            dict(g="belt", name="forest_snap", vol=0.55, base=0.92, step=1.035, jit=0.05),
            dict(nog=True, c0=20, c1=24, name="forest_leaves", vol=0.6),
            dict(nog=True, c0=25, name="egg_burst_s", vol=0.35),
        ],
        "flash": [dict(name="egg_flash", vol=0.5)],
        "ring": [dict(name="egg_ring_l", vol=0.4)],
    },
    "amber": {
        "stream": [dict(loop="amber_inflow", vol=0.26, fade=0.6)],
        "burst": [
            dict(g="seg", c1=5, name="amber_note", vol=0.5, pitches=[1.0, 1.122, 1.26, 1.498, 1.682, 2.0], jit=0.01),
            dict(g="seg", c0=6, name="amber_shard", vol=0.5, jit=0.08),
        ],
        "ring": [
            dict(g="seg", name="egg_ring_s", vol=0.22),
            dict(nog=True, name="amber_sun", vol=0.5, pitches=[1.0, 1.26], jit=0.01),
        ],
        "flash": [dict(name="egg_flash", vol=0.5)],
    },
    "tide": {
        "stream": [dict(loop="tide_bubbles", vol=0.3, fade=0.6)],
        "flash": [dict(name="egg_flash", vol=0.5)],
        "ring": [dict(r0=3.5, name="tide_splash", vol=0.7), dict(name="tide_ring", vol=0.5)],
        "burst": [
            dict(g="r", name="tide_pop", vol=0.5, base=1.0, step=1.14, jit=0.02),
            dict(nog=True, c0=25, name="egg_burst_m", vol=0.35),
        ],
    },
    "storm": {
        "stream": [
            dict(g="crack", name="storm_crackle", vol=0.5),
            dict(nog=True, loop="storm_arcs", vol=0.3, fade=0.4),
        ],
        "bolt": [
            dict(g="crack", name="storm_zap", vol=0.55, jit=0.06),
            dict(g="cl", name="storm_clamp", vol=0.55, jit=0.05),
            dict(nog=True, c0=4, name="storm_zap", vol=0.75, base=0.9),
        ],
        "burst": [dict(g="cl", silent=True)],
        "flash": [dict(name="storm_thunder", vol=0.8)],
        "ring": [dict(name="egg_ring_l", vol=0.5)],
    },
    "astral": {
        "stream": [dict(loop="astral_twinkle", vol=0.3, fade=0.6)],
        "ring": [
            dict(r1=3.8, name="astral_ring", vol=0.55),
            dict(r0=3.9, name="astral_split", vol=0.6),
        ],
        "burst": [dict(c0=25, name="astral_burst", vol=0.6)],
        "flash": [dict(name="egg_flash", vol=0.5)],
    },
}

RAR_BOOM = ["egg_boom_s", "egg_boom_s", "egg_boom_m", "egg_boom_m", "egg_boom_l", "egg_boom_l", "egg_boom_l"]
RAR_BURST = ["egg_burst_s", "egg_burst_s", "egg_burst_m", "egg_burst_m", "egg_burst_l", "egg_burst_l", "egg_burst_l"]
RAR_LAND = ["pet_land_s", "pet_land_s", "pet_land_m", "pet_land_m", "pet_land_m", "pet_land_l", "pet_land_l"]
RAR_REVEAL = [f"egg_reveal_{i}" for i in range(7)]
RAR_MUSIC = ["egg_music_a"] * 4 + ["egg_music_b"] * 3

# ------------------------------------------------------------------ scene-wide beats (anchors are moments of the scene clock)
# anchors: start = 0, prep (the shell opens), tE (the animal emerges), shafts = tE + hd*0.3, pulse = tE + hd*0.45,
#          jump = tE + hd*0.5, tL (the animal lands), tR (the reveal card appears)
# fields: at, off, name | names (index = rarity + 1), fam (append _<family>), rmin / rmax, vol, pitch,
#         layer (looped or once music layer), once, fade, stop (anchor), stopOff
BEATS = [
    dict(at="start", name="egg_appear", vol=0.5),
    dict(at="start", name="egg_riser", fam=True, vol=0.5),
    dict(at="prep", name="egg_crack", vol=0.75),
    dict(at="prep", names=RAR_BOOM, vol=0.8),
    dict(at="prep", names=RAR_BURST, vol=0.5, off=0.03),
    dict(at="prep", name="egg_thunder", rmin=5, vol=0.7),
    dict(at="prep", name="egg_divine", rmin=6, vol=0.8),
    dict(at="tE", name="pet_emerge", vol=0.7),
    dict(at="tE", layer=True, name="pet_trail", vol=0.22, fade=0.25, off=0.1, stop="tL", stopOff=0.15),
    dict(at="tE", layer=True, once=True, name="egg_surge", vol=0.34, fade=0.12, stop="tR", stopOff=0.25),
    dict(at="shafts", name="egg_shafts", rmin=2, rmax=4, vol=0.5),
    dict(at="shafts", name="egg_halo", rmin=5, vol=0.55),
    dict(at="pulse", name="egg_flash", rmin=6, vol=0.6, pitch=0.85),
    dict(at="jump", name="pet_slowmo", rmin=4, vol=0.6),
    dict(at="jump", name="egg_orbit", rmin=6, vol=0.5),
    dict(at="tL", names=RAR_LAND, vol=0.7),
    dict(at="tR", names=RAR_REVEAL, vol=0.62),
    dict(at="tR", name="egg_card", vol=0.5, off=0.05),
    dict(at="tR", layer=True, names=RAR_MUSIC, vol=0.2, fade=1.6, off=0.6),
]

TICK = dict(name="egg_knock", pitch0=0.85, pitch1=1.45, vol0=0.45, vol1=0.7)   # heartbeat before the opening
TAP = dict(name="pet_tap", vol=0.5)
SKIP = dict(name="egg_skip", vol=0.5)
DUCK = dict(factor=0.12, fade_in=0.5, fade_out=1.0)   # background music while the scene is on

REVEAL_DELAY = [0.35, 0.45, 0.6, 0.8, 1.0, 1.3, 1.7]  # as in EggOpen3D
FAMILY_TIMES = {  # prep, open, emerge (EggOpen3D / EggOpenings)
    "forest": (2.5, 1.5, 0.55), "amber": (2.7, 1.7, 0.6), "tide": (2.7, 1.6, 0.6),
    "storm": (2.8, 1.6, 0.6), "astral": (3.0, 1.8, 0.62),
}
RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Divine"]


def all_files():
    """Every file name (AudioIds key) used by the banks."""
    out = []
    for files, _alias, _vol in BANKS.values():
        for f in files:
            if f not in out:
                out.append(f)
    return out


# ------------------------------------------------------------------ parse the event schedule of EggOpenings.luau
def parse_events(path):
    src = open(path, encoding="utf-8").read()
    res = {}
    for m in re.finditer(r'register\("(\w+)", \{', src):
        fam = m.group(1)
        i = src.find("events = {", m.end())
        j = i + len("events = {")
        depth = 1
        k = j
        while depth and k < len(src):
            c = src[k]
            depth += (c == "{") - (c == "}")
            k += 1
        body = src[j:k - 1]
        evs = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            ev = {}
            for key, pat in (("t", r"\bt = ([0-9.]+)"), ("count", r"count = ([0-9.]+)"), ("untilT", r"untilT = ([0-9.]+)"), ("r1", r"r1 = ([0-9.]+)")):
                mm = re.search(pat, line)
                if mm:
                    ev[key] = float(mm.group(1))
            for key, pat in (("type", r'type = "(\w+)"'), ("group", r'group = "(\w+)"')):
                mm = re.search(pat, line)
                if mm:
                    ev[key] = mm.group(1)
            if "t" in ev and "type" in ev:
                evs.append(ev)
        res[fam] = evs
    return res


# ------------------------------------------------------------------ simulation (mirror of the Luau logic)
def _rule_matches(rule, e):
    g = e.get("group")
    if "g" in rule and not (g and g[:len(rule["g"])] == rule["g"]):
        return False
    if rule.get("nog") and g:
        return False
    c = e.get("count", 1)
    if "c0" in rule and c < rule["c0"]:
        return False
    if "c1" in rule and c > rule["c1"]:
        return False
    r1 = e.get("r1", 0)
    if "r0" in rule and r1 < rule["r0"]:
        return False
    if "r1" in rule and r1 > rule["r1"]:
        return False
    return True


def _rule_pitch(rule, n):
    p = rule.get("p", 1.0)
    if "pitches" in rule:
        p = rule["pitches"][min(len(rule["pitches"]), n) - 1]
    elif "step" in rule:
        p = rule.get("base", 1.0) * rule["step"] ** (n - 1)
    return p


def simulate(family, rar, hd, events, landAt=0.78):
    """Cue list for the opening: dicts with t, kind (shot | layer | stop), bank, pitch, vol, why."""
    prep, opn, emerge = FAMILY_TIMES[family]
    tE = prep + opn * emerge
    tL = tE + hd * landAt
    tP = tE + hd
    tR = tP + REVEAL_DELAY[rar]
    anchors = dict(start=0.0, prep=prep, tE=tE, tL=tL, tP=tP, tR=tR, jump=tE + hd * 0.5, shafts=tE + hd * 0.3, pulse=tE + hd * 0.45)
    cues = []

    # heartbeat knocks
    t, last, dt = 0.0, 0.0, 1 / 60
    while t < prep:
        u = min(max(t / prep, 0), 1)
        if t - last > 0.34 - 0.24 * u:
            last = t
            cues.append(dict(t=round(t, 3), kind="shot", bank=TICK["name"], pitch=round(TICK["pitch0"] + u * (TICK["pitch1"] - TICK["pitch0"]), 3),
                             vol=round(TICK["vol0"] + u * (TICK["vol1"] - TICK["vol0"]), 3), why="knock inside the egg"))
        t += dt

    # events of the egg
    counts = {}
    fam_rules = CUES.get(family, {})
    for e in sorted(events, key=lambda x: x["t"]):
        rules = fam_rules.get(e["type"], [])
        handled = False
        for r in rules:
            if _rule_matches(r, e):
                handled = True
                counts[id(r)] = counts.get(id(r), 0) + 1
                n = counts[id(r)]
                if r.get("silent"):
                    continue
                note = f'{e["type"]}' + (f' {e["group"]}' if e.get("group") else "") + (f' x{int(e["count"])}' if "count" in e else "")
                if "loop" in r:
                    end = e.get("untilT", e["t"] + 2.0)
                    cues.append(dict(t=e["t"], kind="layer", bank=r["loop"], vol=r.get("vol"), fade=r.get("fade", 0.4), stop=end, why=note))
                else:
                    p = _rule_pitch(r, n)
                    cues.append(dict(t=e["t"], kind="shot", bank=r["name"], pitch=round(p, 3), vol=r.get("vol"), jit=r.get("jit", 0.03), why=note))
        if not handled:
            for r in CUES["generic"].get(e["type"], []):
                if _rule_matches(r, e):
                    note = f'{e["type"]} (generic)' + (f' {e["group"]}' if e.get("group") else "")
                    cues.append(dict(t=e["t"], kind="shot", bank=r["name"], pitch=1.0, vol=r.get("vol"), jit=0.03, why=note))
                    break

    # scene beats
    for b in BEATS:
        if rar < b.get("rmin", 0) or rar > b.get("rmax", 6):
            continue
        name = b["names"][min(len(b["names"]), rar + 1) - 1] if "names" in b else b["name"]
        if b.get("fam"):
            name = f"{name}_{family}"
        t0 = anchors[b["at"]] + b.get("off", 0.0)
        why = f'beat {b["at"]}'
        if b.get("layer"):
            stop = anchors[b["stop"]] + b.get("stopOff", 0.0) if b.get("stop") else None
            cues.append(dict(t=round(t0, 3), kind="layer", bank=name, vol=b.get("vol"), fade=b.get("fade", 0.5), stop=stop, once=bool(b.get("once")), why=why))
        else:
            cues.append(dict(t=round(t0, 3), kind="shot", bank=name, pitch=b.get("pitch", 1.0), vol=b.get("vol"), jit=0.03, why=why))
    cues.sort(key=lambda c: c["t"])
    return dict(cues=cues, anchors={k: round(v, 3) for k, v in anchors.items()}, end=round(tR + 3.0, 2))


# ------------------------------------------------------------------ Luau emitters
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def lua(v, ind=0):
    pad = "\t" * ind
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(v, 4)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, (list, tuple)):
        if all(not isinstance(x, (dict, list, tuple)) for x in v):
            return "{ " + ", ".join(lua(x) for x in v) + " }"
        return "{\n" + "".join(pad + "\t" + lua(x, ind + 1) + ",\n" for x in v) + pad + "}"
    if isinstance(v, dict):
        items = []
        for k, x in v.items():
            key = k if _IDENT.match(k) else f'["{k}"]'
            items.append(f"{key} = {lua(x, ind + 1)}")
        flat = "{ " + ", ".join(items) + " }"
        if len(flat) < 150 and "\n" not in flat:
            return flat
        return "{\n" + "".join(pad + "\t" + it + ",\n" for it in items) + pad + "}"
    raise TypeError(type(v))


def lua_sfx_block():
    banks = {k: v[0] for k, v in BANKS.items()}
    alias = {k: v[1] for k, v in BANKS.items() if v[1]}
    vol = {k: v[2] for k, v in BANKS.items()}
    out = ["-- BEGIN GENERATED egg audio (audio/tools/egg_cues.py). Do not edit by hand: change the script and run egg_build.py.",
           "local EGG_BANKS = {"]
    for k, v in banks.items():
        out.append(f"\t{k} = {lua(v)},")
    out += ["}", "-- until a file is uploaded the game plays this existing sound instead (a missing entry means silence)", "local EGG_ALIAS = {"]
    for k, v in alias.items():
        out.append(f'\t{k} = "{v}",')
    out += ["}", "local EGG_VOL = {"]
    for k, v in vol.items():
        out.append(f"\t{k} = {v},")
    out += ["}",
            "for name, files in EGG_BANKS do",
            "\tBANKS[name] = files",
            "\tASWRITTEN[name] = true",
            "\tBANK_VOL[name] = EGG_VOL[name]",
            "end",
            "for name, alt in EGG_ALIAS do",
            "\tALIAS[name] = alt",
            "end",
            "-- END GENERATED egg audio"]
    return "\n".join(out)


def lua_cues_block():
    out = ["-- BEGIN GENERATED egg cues (audio/tools/egg_cues.py). Do not edit by hand: change the script and run egg_build.py.",
           "local CUES = {"]
    for fam, types in CUES.items():
        out.append(f"\t{fam} = {{")
        for ty, rules in types.items():
            out.append(f"\t\t{ty} = {{")
            for r in rules:
                out.append(f"\t\t\t{lua(r)},")
            out.append("\t\t},")
        out.append("\t},")
    out.append("}")
    out.append("local BEATS = {")
    for b in BEATS:
        out.append(f"\t{lua(b)},")
    out.append("}")
    out.append(f"local TICK = {lua(TICK)}")
    out.append(f"local TAP = {lua(TAP)}")
    out.append(f"local SKIP = {lua(SKIP)}")
    out.append(f"local DUCK = {lua(DUCK)}")
    out.append("-- END GENERATED egg cues")
    return "\n".join(out)


if __name__ == "__main__":
    print(lua_sfx_block()[:600])
    print("...")
    print(lua_cues_block()[:900])
