#!/usr/bin/env python3
"""V61: данные размеров зверей и сценария их появления из куста. Источник правды для двух блоков в коде.

    python tools/creature_data.py            # показать сводку и проверить (уникальность, полнота)
    python tools/creature_data.py patch      # вписать блоки в source/ReplicatedStorage/Fauna150.luau и V15Covers/Stage.luau
    python tools/creature_data.py verify     # блоки в коде совпадают с тем, что рисует этот файл (для tools/check.py)

1) SIZE: настоящий размер животного (самая большая сторона, метры). Рост игрока 1,8 м = 5,4 студа, то есть 3 студа на метр.
   Fauna150.WorldScale(id) приводит нарисованную модель (самая большая сторона из высоты и длины) к этому размеру.
2) REVEAL: для каждого вида своя пара «манера выхода из куста» (13 вариантов) + «фирменный жест» (16 вариантов).
   Пары не повторяются у 150 видов (проверка ниже), числа (длительность, размах, пауза «затишья», сила испуга) у каждого свои.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAUNA = os.path.join(ROOT, "source/ReplicatedStorage/Fauna150.luau")
STAGE = os.path.join(ROOT, "source/ReplicatedStorage/V15Covers/Stage.luau")
CONFIG = os.path.join(ROOT, "source/ReplicatedStorage/Shared/Config.luau")

# id: (размер в метрах, манера выхода, фирменный жест)
# манеры: walk leap burst rise drop swoop surge pounce roll skitter stomp pop flash
# жесты:  rear shake bow spin hop2 stomp3 lookaround flare wiggle roar sniff stretch coil bounce sway twirl
D = {
    # 1 Forest Edge
    "dodo": (0.9, "walk", "shake"), "fox": (1.0, "pounce", "bow"), "hedgehog": (0.25, "roll", "wiggle"),
    "moonrabbit": (0.55, "flash", "bounce"), "rabbit": (0.45, "leap", "hop2"), "squirrel": (0.35, "pop", "twirl"),
    # 2 Deep Woods
    "badger": (0.75, "rise", "sniff"), "boar": (1.5, "burst", "shake"), "lynx": (1.0, "pounce", "stretch"),
    "roe": (1.2, "leap", "lookaround"), "sabertooth": (2.0, "pounce", "roar"), "wolf": (1.4, "burst", "roar"),
    # 3 Wild Marsh
    "bear": (2.0, "rise", "rear"), "bison": (3.0, "stomp", "shake"), "cavebear": (2.6, "rise", "stretch"),
    "deer": (2.0, "walk", "bow"), "moose": (3.0, "stomp", "lookaround"), "spiritdeer": (2.4, "flash", "stretch"),
    # 4 Ancient Forest
    "cavelion": (2.8, "pounce", "rear"), "icemammoth": (6.0, "stomp", "roar"), "mammoth": (5.5, "stomp", "sway"),
    "megadeer": (3.2, "walk", "flare"), "rhino": (3.5, "burst", "stomp3"), "yeti": (2.8, "drop", "rear"),
    # 5 Amber Savanna
    "amber_giraffe": (5.0, "walk", "stretch"), "gazelle": (1.4, "leap", "stretch"), "hyena": (1.4, "pounce", "wiggle"),
    "savanna_ostrich": (2.4, "burst", "flare"), "sunlion": (2.4, "walk", "roar"), "watchful_meerkat": (0.4, "pop", "lookaround"),
    # 6 Red Canyons
    "armadillo": (0.6, "roll", "stretch"), "canyon_condor": (1.2, "swoop", "flare"), "canyon_roadrunner": (0.7, "burst", "bounce"),
    "mountain_goat": (1.5, "leap", "stomp3"), "redthorn_lizard": (0.4, "skitter", "sway"), "rock_hyrax": (0.5, "pop", "stretch"),
    # 7 Mirage Dunes
    "dune_jerboa": (0.2, "leap", "twirl"), "dune_scorpion": (0.6, "skitter", "shake"), "fennec": (0.6, "pop", "sniff"),
    "mirage_camel": (3.0, "walk", "stomp3"), "oasis_scarab": (0.4, "rise", "shake"), "sand_wyrm": (5.0, "rise", "coil"),
    # 8 Emerald Jungle
    "emerald_treefrog": (0.4, "leap", "bounce"), "jade_tapir": (2.0, "walk", "sniff"), "jaguar": (1.7, "pounce", "coil"),
    "jungle_gorilla": (1.7, "drop", "roar"), "leafcutter_ant": (0.5, "skitter", "sniff"), "toucan": (0.65, "swoop", "bow"),
    # 9 Mangrove Marshes
    "crocodile": (3.5, "surge", "shake"), "mangrove_fiddler": (0.4, "skitter", "wiggle"), "mangrove_flamingo": (1.5, "walk", "twirl"),
    "marsh_hydra": (3.5, "rise", "wiggle"), "mudskipper": (0.3, "leap", "wiggle"), "otter": (1.2, "surge", "twirl"),
    # 10 Storm Highlands
    "highland_yak": (2.5, "stomp", "bow"), "storm_griffin": (3.0, "swoop", "roar"), "storm_ram": (1.6, "burst", "bow"),
    "storm_stone_spider": (1.8, "drop", "shake"), "tempest_pterosaur": (2.5, "swoop", "sniff"), "thunder_eagle": (1.1, "swoop", "rear"),
    # 11 Azure Coast
    "azure_horseshoe_crab": (0.6, "skitter", "hop2"), "coral_wyvern": (3.0, "surge", "coil"), "lagoon_pelican": (1.4, "swoop", "bounce"),
    "sea_lion": (2.0, "surge", "bounce"), "sea_turtle": (1.4, "surge", "sway"), "spiral_hermit_crab": (1.0, "skitter", "lookaround"),
    # 12 Coral Depths
    "abyss_leviathan": (7.0, "surge", "roar"), "coral_seahorse": (2.0, "surge", "stretch"), "hammer_shark": (3.0, "surge", "spin"),
    "pearl_nautilus": (1.4, "flash", "spin"), "reef_lobster": (1.2, "skitter", "stomp3"), "reef_ray": (1.8, "swoop", "sway"),
    # 13 Ash Plateau
    "ash_anteater": (1.8, "walk", "coil"), "ash_lizard": (0.9, "skitter", "twirl"), "cinder_porcupine": (1.1, "roll", "shake"),
    "ember_boar": (1.8, "burst", "sniff"), "ember_mandrill": (1.7, "drop", "flare"), "lava_golem": (3.5, "rise", "stomp3"),
    # 14 Volcano Heart
    "caldera_toad": (1.0, "leap", "flare"), "furnace_stag_beetle": (0.9, "skitter", "flare"), "magma_rhino": (3.8, "burst", "lookaround"),
    "obsidian_crab": (1.4, "skitter", "bow"), "obsidian_pangolin": (1.6, "roll", "rear"), "phoenix": (2.2, "flash", "flare"),
    # 15 Crystal Caverns
    "amethyst_fox": (1.2, "flash", "bow"), "crystal_anemone": (1.4, "rise", "flare"), "crystal_bat": (1.0, "swoop", "wiggle"),
    "geode_mole": (1.0, "pop", "shake"), "prism_moth": (1.2, "swoop", "twirl"), "quartz_dragon": (5.0, "rise", "spin"),
    # 16 Lunar Tundra
    "arctic_hare": (0.7, "leap", "spin"), "aurora_bear": (2.8, "walk", "rear"), "aurora_weasel": (0.9, "pounce", "twirl"),
    "lunar_wolf": (1.8, "flash", "roar"), "moon_owl": (1.4, "swoop", "lookaround"), "tundra_muskox": (2.2, "burst", "sway"),
    # 17 Sky Islands
    "aether_ribbonfish": (2.0, "swoop", "coil"), "cloud_glider": (2.2, "swoop", "stretch"), "cloud_sheep": (1.4, "leap", "sniff"),
    "island_chameleon": (0.8, "walk", "lookaround"), "sky_drake": (4.0, "swoop", "stomp3"), "sky_stag": (2.8, "leap", "rear"),
    # 18 Twilight Rift
    "dusk_panther": (1.9, "pounce", "sniff"), "gloom_sloth": (1.3, "walk", "sway"), "rift_axolotl": (0.9, "surge", "wiggle"),
    "shadow_mantis": (2.0, "drop", "twirl"), "void_behemoth": (5.0, "rise", "lookaround"), "void_lamprey": (1.8, "surge", "sniff"),
    # 19 Starbound Frontier
    "astral_dragon": (6.0, "swoop", "spin"), "astral_starfish": (1.0, "flash", "twirl"), "comet_fox": (1.3, "burst", "spin"),
    "nebula_tardigrade": (0.8, "walk", "wiggle"), "orbital_jellyfish": (2.0, "flash", "sway"), "stellar_stag": (3.0, "leap", "bow"),
    # 20 Rust Gardens
    "clockwork_basilisk": (4.0, "walk", "spin"), "copper_weevil": (1.0, "skitter", "stretch"), "gear_sentinel": (4.0, "stomp", "spin"),
    "iron_hound": (2.0, "burst", "stretch"), "magnet_tripod": (2.6, "stomp", "flare"), "spring_strider": (2.2, "leap", "coil"),
    # 21 Fungal Bogs
    "cap_mantis": (2.2, "drop", "bow"), "lantern_slug": (1.2, "walk", "bounce"), "mycelium_bloomstalker": (2.8, "rise", "bounce"),
    "peat_leech": (0.9, "skitter", "coil"), "shelf_millipede": (1.2, "skitter", "bounce"), "spore_marauder": (3.0, "burst", "hop2"),
    # 22 Bone Dunes
    "bone_vulture": (2.0, "swoop", "shake"), "dune_ankylosaur": (4.0, "stomp", "wiggle"), "fossil_ceratopsian": (5.0, "burst", "wiggle"),
    "fossil_trilobite": (0.5, "skitter", "spin"), "sand_reaper": (3.5, "drop", "stretch"), "skeletal_colossus": (7.0, "rise", "roar"),
    # 23 Sunken Citadel
    "abyss_octopus": (3.0, "surge", "flare"), "abyss_sea_urchin": (1.0, "roll", "twirl"), "cathedral_clam": (1.6, "rise", "bow"),
    "citadel_cuttlefish": (1.2, "surge", "lookaround"), "pressure_colossus": (6.0, "stomp", "rear"), "trench_angler": (3.0, "flash", "lookaround"),
    # 24 Storm Rift
    "fulgurite_cricket": (1.0, "leap", "shake"), "prism_revenant": (3.2, "flash", "rear"), "rift_kangaroo": (2.2, "leap", "sway"),
    "rift_serpent": (6.0, "rise", "twirl"), "storm_harrier": (1.6, "swoop", "hop2"), "thunder_centaur": (3.2, "burst", "rear"),
    # 25 Primordial Caldera
    "caldera_tarsier": (0.9, "pop", "bow"), "ember_salamander": (1.8, "skitter", "rear"), "lava_dragonfly": (1.5, "flash", "wiggle"),
    "magma_hippo": (3.5, "stomp", "stretch"), "primordial_titan": (12.0, "drop", "stomp3"), "volcanic_wyrm": (8.0, "rise", "sway"),
}

FAMS = ["walk", "leap", "burst", "rise", "drop", "swoop", "surge", "pounce", "roll", "skitter", "stomp", "pop", "flash"]
FLOS = ["rear", "shake", "bow", "spin", "hop2", "stomp3", "lookaround", "flare", "wiggle", "roar", "sniff", "stretch", "coil", "bounce", "sway", "twirl"]
# (секунд на выход, секунд раскрытия куста, пауза до появления зверя): зависят только от манеры
FAM_TIMING = {
    "walk": (1.30, 0.85, 0.45), "leap": (0.95, 0.40, 0.22), "burst": (0.85, 0.28, 0.10), "rise": (1.40, 0.65, 0.20),
    "drop": (1.25, 0.60, 0.10), "swoop": (1.30, 0.50, 0.20), "surge": (1.05, 0.40, 0.15), "pounce": (1.40, 0.55, 0.30),
    "roll": (1.30, 0.55, 0.30), "skitter": (1.45, 0.60, 0.30), "stomp": (1.80, 1.00, 0.50), "pop": (1.20, 0.30, 0.05),
    "flash": (1.30, 0.50, 0.10),
}
STUDS_PER_M = 3.0


def config_ids() -> list[str]:
    cfg = open(CONFIG, encoding="utf-8").read()
    return re.findall(r'\{ id = "(\w+)", icon = "[^"]*", zone = \d+, rarity = \d', cfg)


def jitter(key: str, salt: str, lo: float, hi: float) -> float:
    h = int(hashlib.md5((key + salt).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return lo + (hi - lo) * h


def resolve() -> dict[str, tuple[float, str, str]]:
    """повторяющиеся пары (манера, жест) заменяются ближайшим свободным жестом; возвращает итоговую таблицу"""
    ids = config_ids()
    owner: dict[tuple[str, str], str] = {}
    dups = []
    for sid in ids:
        m, fam, flo = D[sid]
        if (fam, flo) in owner:
            dups.append(sid)
        else:
            owner[(fam, flo)] = sid
    out = {sid: D[sid] for sid in ids}
    changed = []
    for sid in dups:
        m, fam, flo = D[sid]
        for alt in FLOS:
            if (fam, alt) not in owner:
                owner[(fam, alt)] = sid
                out[sid] = (m, fam, alt)
                changed.append("%s: %s+%s -> %s+%s" % (sid, fam, flo, fam, alt))
                break
        else:
            raise SystemExit("нет свободного жеста для " + sid)
    resolve.changed = changed  # type: ignore[attr-defined]
    return out


def tables() -> tuple[dict, dict]:
    table = resolve()
    sizes, reveal = {}, {}
    seen = set()
    for sid, (m, fam, flo) in table.items():
        sizes[sid] = m
        dur, copen, lead = FAM_TIMING[fam]
        row = (
            fam,
            flo,
            round(dur * jitter(sid, "dur", 0.88, 1.18), 2),   # длительность выхода
            round(jitter(sid, "amp", 0.80, 1.25), 2),          # размах движений
            round(jitter(sid, "hold", 0.22, 0.62), 2),         # затишье перед выходом (секунды тишины)
            round(jitter(sid, "scare", 0.55, 1.25), 2),        # сила испуга (тряска камеры, всплеск)
            round(copen * jitter(sid, "open", 0.92, 1.10), 2), # раскрытие куста
            round(lead * jitter(sid, "lead", 0.9, 1.15), 2),   # сколько куст раскрывается до появления зверя
        )
        assert row[2:] not in seen, sid
        seen.add(row[2:])
        reveal[sid] = row
    return sizes, reveal


def lua_sizes(sizes: dict) -> str:
    rows = ["\t%s = %s," % (k, repr(v)) for k, v in sizes.items()]
    return "-- BEGIN V61 SIZES (tools/creature_data.py)\nlocal SIZE_M: { [string]: number } = {\n" + "\n".join(rows) + "\n}\n-- END V61 SIZES"


def lua_reveal(reveal: dict) -> str:
    rows = ['\t%s = { fam = "%s", flo = "%s", dur = %s, amp = %s, hold = %s, scare = %s, open = %s, lead = %s },' % ((k,) + v) for k, v in reveal.items()]
    return "-- BEGIN V61 REVEAL (tools/creature_data.py)\nlocal REVEAL: { [string]: any } = {\n" + "\n".join(rows) + "\n}\n-- END V61 REVEAL"


def splice(path: str, block: str, tag: str, write: bool) -> bool:
    src = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    a = src.find("-- BEGIN V61 " + tag)
    b = src.find("-- END V61 " + tag)
    if a < 0 or b < 0:
        print("нет маркеров BEGIN/END V61 %s в %s" % (tag, path))
        return False
    b += len("-- END V61 " + tag)
    same = src[a:b] == block
    if write and not same:
        open(path, "w", encoding="utf-8", newline="\n").write(src[:a] + block + src[b:])
        return True
    return same


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    ids = config_ids()
    missing = [i for i in ids if i not in D]
    extra = [i for i in D if i not in ids]
    if missing or extra or len(ids) != 150:
        print("FAIL: не хватает", missing, "лишние", extra, "всего в Config", len(ids))
        sys.exit(1)
    sizes, reveal = tables()
    pairs = {(r[0], r[1]) for r in reveal.values()}
    if len(pairs) != 150:
        print("FAIL: пары не уникальны", len(pairs))
        sys.exit(1)
    if cmd == "patch":
        splice(FAUNA, lua_sizes(sizes), "SIZES", True)
        splice(STAGE, lua_reveal(reveal), "REVEAL", True)
        print("blocks written")
    elif cmd == "verify":
        ok = splice(FAUNA, lua_sizes(sizes), "SIZES", False) and splice(STAGE, lua_reveal(reveal), "REVEAL", False)
        print("creature blocks %s" % ("match" if ok else "STALE: python tools/creature_data.py patch"))
        sys.exit(0 if ok else 1)
    else:
        print("species:", len(ids), "| unique (family, gesture) pairs:", len(pairs))
        if getattr(resolve, "changed", None):
            print("duplicates resolved:", *resolve.changed, sep="\n  ")
        from collections import Counter
        print("families:", dict(Counter(r[0] for r in reveal.values())))
        print("gestures:", dict(Counter(r[1] for r in reveal.values())))


if __name__ == "__main__":
    main()
