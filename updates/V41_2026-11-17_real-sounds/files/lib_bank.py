"""Library bank (V41): real recordings from the Roblox Creator Store used for the egg opening instead of synthesised files.

Why: the 70 synthesised egg sounds could not be uploaded (no Open Cloud permission for the audio folder) and the user
found the existing sounds "AI-like". These are professional or real recordings that load by id with no upload.
Sources (all free in the Creator Store): Pro Sound Effects (egg shell cracks, cinematic hits, lightning, water splash),
APM Music (stingers, risers, sonic logos, hits) and a few community sound effects.

Measured in Studio (Play, Client): Sound.PlaybackLoudness at Volume 1 -> `peak`, TimeLength -> `len`. `gain` brings every
sound to a common loudness by role (target / peak, limited to 0.5 .. 4). `speed` is a PlaybackSpeed factor (risers are
sped up or slowed so that their peak lands on the moment the egg opens: prep = 2.5 .. 3.0 s after the start).

generate:  python audio/tools/lib_bank.py   (prints the Luau block; egg_build.py inserts it into Client/Sfx.luau)
"""

# key (AudioIds name): (asset id, role, peak, len, speed, label, source)
LIB = {
    # shell cracks: real egg shells (Pro Sound Effects, category Cooking)
    "egg_crack_1": (9113959343, "crack", 102, 1.02, 1.0, "Crack Egg Crunchy 11", "Pro Sound Effects"),
    "egg_crack_2": (9113959332, "crack", 95, 1.12, 1.0, "Crack Egg Crunchy 9", "Pro Sound Effects"),
    # impacts when the egg opens, by rarity size
    "egg_boom_s": (1837830050, "boom", 328, 4.32, 1.0, "BOOM-Sub Boom 01", "APM Music"),
    "egg_boom_m": (103410515538241, "boom", 462, 5.87, 1.0, "Boom Brute Force", "APM Music"),
    "egg_boom_l": (9125484511, "boom", 514, 5.53, 1.0, "Deep Hits Big Reverberant Booms Rumbling Tail 3", "Pro Sound Effects"),
    "egg_thunder": (95410087861011, "thunder", 242, 5.79, 1.0, "heavy thunder", "Yimzo (community)"),
    "storm_thunder": (72113341430811, "thunder", 148, 7.47, 1.0, "WX_Thunder_Rolling_01", "MSDLF (community)"),
    "storm_zap_1": (9116277954, "zap", 276, 1.97, 1.0, "Lightning Flashes Quick Electrical Bursts 32", "Pro Sound Effects"),
    "storm_zap_2": (9116279560, "zap", 212, 0.79, 1.0, "Lightning Flashes Quick Electrical Bursts 56", "Pro Sound Effects"),
    # bursts of light
    "egg_burst_s": (135968996204345, "sparkle", 358, 0.72, 1.0, "FIXED sparkle magic sound", "Hibuki_DSP (community)"),
    "egg_burst_m": (117011707307950, "sparkle", 414, 1.47, 1.0, "Glitter Sparkle Magic Sound", "Little Body Big Heart (community)"),
    "egg_burst_l": (132381858621446, "shimmer", 86, 4.14, 1.0, "Magic crystal sparkle sound effect 3", "community"),
    "egg_flash": (135968996204345, "sparkle", 358, 0.72, 1.0, "FIXED sparkle magic sound", "Hibuki_DSP (community)"),
    "tide_splash": (9125702987, "splash", 163, 1.76, 1.0, "Mud Puddle Splash Shallow Water Impacts Hits 16", "Pro Sound Effects"),
    # risers before the egg opens: the peak must land at prep (2.5 .. 3.0 s)
    "egg_riser_forest": (9040288138, "riser", 432, 5.64, 0.85, "Heart Strung (Alt)", "APM Music"),
    "egg_riser_amber": (9040281199, "riser", 400, 6.06, 1.7, "Heated Hijack", "APM Music"),
    "egg_riser_tide": (9043343295, "riser", 240, 4.13, 1.5, "REVERSE NOISE HARD END 09", "APM Music"),
    "egg_riser_storm": (9040281199, "riser", 400, 6.06, 1.7, "Heated Hijack", "APM Music"),
    "egg_riser_astral": (1837834284, "riser", 301, 4.00, 1.4, "REVERSE HARD STOP-Noise Build 06", "APM Music"),
    # layers and loops that had no sound at all (found by playing every egg event in Studio): shimmer pads, arcs, build-up
    "storm_crackle": (9116279560, "zap", 212, 0.79, 1.0, "Lightning Flashes Quick Electrical Bursts 56", "Pro Sound Effects"),
    "storm_arcs": (9116277954, "zap", 276, 1.97, 1.0, "Lightning Flashes Quick Electrical Bursts 32 (loop)", "Pro Sound Effects"),
    "pet_trail": (131722051883127, "shimmer", 107, 5.78, 1.0, "Magic crystal sparkle sound effect 2 (loop)", "community"),
    "amber_inflow": (131722051883127, "shimmer", 107, 5.78, 0.9, "Magic crystal sparkle sound effect 2 (loop)", "community"),
    "tide_bubbles": (131722051883127, "shimmer", 107, 5.78, 1.35, "Magic crystal sparkle sound effect 2 (loop)", "community"),
    "forest_shimmer": (132381858621446, "shimmer", 86, 4.14, 1.0, "Magic crystal sparkle sound effect 3 (loop)", "community"),
    "astral_twinkle": (117011707307950, "twinkle", 414, 1.47, 1.0, "Glitter Sparkle Magic Sound (loop)", "Little Body Big Heart (community)"),
    "egg_surge": (9040281199, "riser", 400, 6.06, 1.0, "Heated Hijack (build-up from the emerge to the reveal card)", "APM Music"),
    # stingers at the reveal card, by rarity (Common .. Divine)
    "egg_reveal_0": (1841173394, "sting", 204, 5.64, 1.0, "Magical (a)", "APM Music"),
    "egg_reveal_1": (1841209502, "sting", 239, 6.09, 1.0, "Beautiful Shimmer", "APM Music"),
    "egg_reveal_2": (1841173434, "sting", 244, 8.41, 1.0, "Magical (b)", "APM Music"),
    "egg_reveal_3": (9043144476, "sting", 314, 5.56, 1.0, "Sudden Inspiration - Tag3", "APM Music"),
    "egg_reveal_4": (9041792228, "sting", 382, 4.39, 1.0, "How The Story Goes", "APM Music"),
    "egg_reveal_5": (1836860398, "sting", 518, 5.70, 1.0, "Winning Spirit", "APM Music"),
    "egg_reveal_6": (1841180330, "sting", 357, 8.46, 1.0, "Silver Dreams", "APM Music"),
}

# keys that reuse another AudioIds key (a track already uploaded to Roblox) when they have no id of their own
REUSE = {"egg_music_a": "music_meadow", "egg_music_b": "music_cozy"}

TARGET = {"twinkle": 260, "crack": 300, "boom": 420, "thunder": 380, "zap": 260, "sparkle": 300, "shimmer": 260, "splash": 300, "riser": 350, "sting": 300}


def gain(key):
    _id, role, peak, _len, _speed, _label, _src = LIB[key]
    g = TARGET[role] / peak
    return round(min(4.0, max(0.5, g)), 2)


def lua_block():
    out = ["-- BEGIN GENERATED library sounds (audio/tools/lib_bank.py). Do not edit by hand."]
    out.append("local EGG_LIB = {")
    for k, v in LIB.items():
        out.append(f'\t{k} = "rbxassetid://{v[0]}",')
    out.append("}")
    out.append("local EGG_GAIN = {")
    for k in LIB:
        out.append(f"\t{k} = {gain(k)},")
    out.append("}")
    out.append("local EGG_SPEED = {")
    for k, v in LIB.items():
        if v[4] != 1.0:
            out.append(f"\t{k} = {v[4]},")
    out.append("}")
    out.append("local EGG_REUSE = {")
    for k, v in REUSE.items():
        out.append(f'	{k} = "{v}",')
    out.append("}")
    out.append("for k, id in EGG_LIB do LIB_IDS[k] = id end")
    out.append("for k, v in EGG_REUSE do LIB_REUSE[k] = v end")
    out.append("for k, g in EGG_GAIN do LIB_GAIN[k] = g end")
    out.append("for k, s in EGG_SPEED do LIB_SPEED[k] = s end")
    out.append("-- END GENERATED library sounds")
    return "\n".join(out) + "\n"


def credits_md():
    lines = ["# Звуки из Creator Store (V41)", "",
             "Настоящие записи, подключённые по номеру (в Roblox их загружать не нужно). Номер, длина и пик громкости измерены в Studio.", "",
             "| Ключ | Номер | Название | Источник | Длина, с | Множитель |", "|---|---|---|---|---|---|"]
    for k, v in LIB.items():
        lines.append(f"| `{k}` | {v[0]} | {v[5]} | {v[6]} | {v[3]} | ×{gain(k)}" + (f", скорость ×{v[4]}" if v[4] != 1.0 else "") + " |")
    lines += ["", "APM Music и Pro Sound Effects: звуки из их каталогов, которые Roblox выдаёт бесплатно в Creator Store (\"Courtesy of APM Music\", \"Courtesy of Pro Sound Effects\").",
              "Музыку и звуки из чужих игр не брал."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(lua_block())
