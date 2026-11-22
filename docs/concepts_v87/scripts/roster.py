# SpearHunt V87 - roster of all 150 animals: role data + unique (method, gesture) assignment.
# Run with system Python: writes ..\roster.json (the source of truth for every biome script) and validates it.
import json, os, sys

BIOMES = {
    1: ('forest_edge', 'Forest Edge'), 2: ('deep_woods', 'Deep Woods'), 3: ('wild_marsh', 'Wild Marsh'),
    4: ('ancient_forest', 'Ancient Forest'), 5: ('amber_savanna', 'Amber Savanna'), 6: ('red_canyons', 'Red Canyons'),
    7: ('mirage_dunes', 'Mirage Dunes'), 8: ('emerald_jungle', 'Emerald Jungle'), 9: ('mangrove_marshes', 'Mangrove Marshes'),
    10: ('storm_highlands', 'Storm Highlands'), 11: ('azure_coast', 'Azure Coast'), 12: ('coral_depths', 'Coral Depths'),
    13: ('ash_plateau', 'Ash Plateau'), 14: ('volcano_heart', 'Volcano Heart'), 15: ('crystal_caverns', 'Crystal Caverns'),
    16: ('lunar_tundra', 'Lunar Tundra'), 17: ('sky_islands', 'Sky Islands'), 18: ('twilight_rift', 'Twilight Rift'),
    19: ('starbound_frontier', 'Starbound Frontier'), 20: ('rust_gardens', 'Rust Gardens'), 21: ('fungal_bogs', 'Fungal Bogs'),
    22: ('bone_dunes', 'Bone Dunes'), 23: ('sunken_citadel', 'Sunken Citadel'), 24: ('storm_rift', 'Storm Rift'),
    25: ('primordial_caldera', 'Primordial Caldera'),
}

# id, name, biome, rarity, kind (ground/air/water/shore), height (studs), archetype
R = [
    ('rabbit', 'Rabbit', 1, 1, 'ground', 2.8, 'sit'), ('squirrel', 'Squirrel', 1, 1, 'ground', 1.9, 'sit'),
    ('hedgehog', 'Hedgehog', 1, 2, 'ground', 1.5, 'quad'), ('fox', 'Fox', 1, 3, 'ground', 2.65, 'quad'),
    ('dodo', 'Dodo', 1, 4, 'ground', 3.6, 'bird'), ('moonrabbit', 'Moon Rabbit', 1, 5, 'ground', 3.35, 'sit'),
    ('roe', 'Roe Deer', 2, 1, 'ground', 3.0, 'quad'), ('boar', 'Boar', 2, 1, 'ground', 2.6, 'quad'),
    ('badger', 'Badger', 2, 2, 'ground', 2.0, 'quad'), ('wolf', 'Wolf', 2, 3, 'ground', 2.6, 'quad'),
    ('lynx', 'Lynx', 2, 4, 'ground', 3.2, 'quad'), ('sabertooth', 'Saber-toothed Cat', 2, 5, 'ground', 5.0, 'quad'),
    ('deer', 'Deer', 3, 1, 'ground', 3.6, 'quad'), ('moose', 'Moose', 3, 2, 'ground', 5.5, 'quad'),
    ('bear', 'Bear', 3, 3, 'ground', 5.5, 'quad'), ('bison', 'Bison', 3, 4, 'ground', 6.0, 'quad'),
    ('cavebear', 'Cave Bear', 3, 5, 'ground', 8.5, 'quad'), ('spiritdeer', 'Spirit Deer', 3, 6, 'ground', 8.0, 'quad'),
    ('megadeer', 'Giant Deer', 4, 1, 'ground', 5.5, 'quad'), ('rhino', 'Woolly Rhino', 4, 2, 'ground', 5.5, 'quad'),
    ('mammoth', 'Mammoth', 4, 3, 'ground', 8.0, 'quad'), ('cavelion', 'Cave Lion', 4, 4, 'ground', 5.0, 'quad'),
    ('icemammoth', 'Ice Mammoth', 4, 5, 'ground', 11.0, 'quad'), ('yeti', 'Yeti', 4, 6, 'ground', 10.0, 'biped'),
    ('watchful_meerkat', 'Watchful Meerkat', 5, 1, 'ground', 1.9, 'sit'), ('gazelle', 'Gazelle', 5, 2, 'ground', 3.2, 'quad'),
    ('savanna_ostrich', 'Savanna Ostrich', 5, 3, 'ground', 5.0, 'bird'), ('hyena', 'Hyena', 5, 4, 'ground', 3.4, 'quad'),
    ('sunlion', 'Sun Lion', 5, 5, 'ground', 5.5, 'quad'), ('amber_giraffe', 'Amber Giraffe', 5, 6, 'ground', 12.0, 'quad'),
    ('rock_hyrax', 'Rock Hyrax', 6, 1, 'ground', 1.5, 'quad'), ('mountain_goat', 'Mountain Goat', 6, 2, 'ground', 3.2, 'quad'),
    ('canyon_roadrunner', 'Canyon Roadrunner', 6, 3, 'ground', 2.6, 'bird'), ('armadillo', 'Armadillo', 6, 4, 'ground', 2.2, 'quad'),
    ('canyon_condor', 'Canyon Condor', 6, 5, 'air', 5.0, 'bird'), ('redthorn_lizard', 'Redthorn Lizard', 6, 6, 'ground', 8.0, 'quad'),
    ('oasis_scarab', 'Oasis Scarab', 7, 1, 'ground', 1.4, 'bug'), ('fennec', 'Fennec Fox', 7, 2, 'ground', 2.4, 'quad'),
    ('dune_jerboa', 'Dune Jerboa', 7, 3, 'ground', 2.0, 'sit'), ('dune_scorpion', 'Dune Scorpion', 7, 4, 'ground', 3.0, 'bug'),
    ('sand_wyrm', 'Sand Wyrm', 7, 5, 'ground', 9.0, 'serp'), ('mirage_camel', 'Mirage Camel', 7, 6, 'ground', 9.0, 'quad'),
    ('jade_tapir', 'Jade Tapir', 8, 1, 'ground', 3.0, 'quad'), ('toucan', 'Toucan', 8, 2, 'air', 2.4, 'bird'),
    ('leafcutter_ant', 'Leafcutter Ant', 8, 3, 'ground', 1.8, 'bug'), ('jaguar', 'Jaguar', 8, 4, 'ground', 3.6, 'quad'),
    ('jungle_gorilla', 'Jungle Gorilla', 8, 5, 'ground', 8.0, 'biped'), ('emerald_treefrog', 'Emerald Treefrog', 8, 6, 'ground', 5.0, 'sit'),
    ('mudskipper', 'Mudskipper', 9, 1, 'ground', 1.4, 'fish'), ('otter', 'Otter', 9, 2, 'shore', 2.4, 'sit'),
    ('mangrove_fiddler', 'Mangrove Fiddler', 9, 3, 'ground', 2.0, 'bug'), ('crocodile', 'Crocodile', 9, 4, 'shore', 3.0, 'quad'),
    ('marsh_hydra', 'Marsh Hydra', 9, 5, 'ground', 9.0, 'quad'), ('mangrove_flamingo', 'Mangrove Flamingo', 9, 6, 'ground', 8.0, 'bird'),
    ('storm_stone_spider', 'Storm Stone Spider', 10, 1, 'ground', 1.6, 'bug'), ('storm_ram', 'Storm Ram', 10, 2, 'ground', 3.4, 'quad'),
    ('highland_yak', 'Highland Yak', 10, 3, 'ground', 5.5, 'quad'), ('thunder_eagle', 'Thunder Eagle', 10, 4, 'air', 4.0, 'bird'),
    ('storm_griffin', 'Storm Griffin', 10, 5, 'air', 8.0, 'dragon'), ('tempest_pterosaur', 'Tempest Pterosaur', 10, 6, 'air', 9.0, 'dragon'),
    ('spiral_hermit_crab', 'Spiral Hermit Crab', 11, 1, 'ground', 1.6, 'bug'), ('sea_turtle', 'Sea Turtle', 11, 2, 'shore', 2.6, 'quad'),
    ('lagoon_pelican', 'Lagoon Pelican', 11, 3, 'air', 3.4, 'bird'), ('sea_lion', 'Sea Lion', 11, 4, 'shore', 3.6, 'sit'),
    ('coral_wyvern', 'Coral Wyvern', 11, 5, 'water', 8.0, 'dragon'), ('azure_horseshoe_crab', 'Azure Horseshoe Crab', 11, 6, 'ground', 5.0, 'bug'),
    ('pearl_nautilus', 'Pearl Nautilus', 12, 1, 'water', 1.8, 'fish'), ('reef_ray', 'Reef Ray', 12, 2, 'water', 1.4, 'fish'),
    ('coral_seahorse', 'Coral Seahorse', 12, 3, 'water', 3.0, 'fish'), ('hammer_shark', 'Hammerhead Shark', 12, 4, 'water', 4.0, 'fish'),
    ('abyss_leviathan', 'Abyssal Leviathan', 12, 5, 'water', 10.0, 'serp'), ('reef_lobster', 'Reef Lobster', 12, 6, 'ground', 6.0, 'bug'),
    ('cinder_porcupine', 'Cinder Porcupine', 13, 1, 'ground', 1.8, 'quad'), ('ash_lizard', 'Ash Lizard', 13, 2, 'ground', 1.8, 'quad'),
    ('ash_anteater', 'Ash Anteater', 13, 3, 'ground', 3.2, 'quad'), ('ember_boar', 'Ember Boar', 13, 4, 'ground', 3.6, 'quad'),
    ('lava_golem', 'Lava Golem', 13, 5, 'ground', 9.0, 'biped'), ('ember_mandrill', 'Ember Mandrill', 13, 6, 'ground', 8.0, 'biped'),
    ('furnace_stag_beetle', 'Furnace Stag Beetle', 14, 1, 'ground', 1.6, 'bug'), ('obsidian_crab', 'Obsidian Crab', 14, 2, 'ground', 2.2, 'bug'),
    ('caldera_toad', 'Caldera Toad', 14, 3, 'ground', 2.8, 'sit'), ('magma_rhino', 'Magma Rhino', 14, 4, 'ground', 6.5, 'quad'),
    ('phoenix', 'Phoenix', 14, 5, 'air', 8.0, 'bird'), ('obsidian_pangolin', 'Obsidian Pangolin', 14, 6, 'ground', 6.0, 'quad'),
    ('prism_moth', 'Prism Moth', 15, 1, 'air', 1.8, 'flyer'), ('crystal_bat', 'Crystal Bat', 15, 2, 'air', 2.2, 'flyer'),
    ('geode_mole', 'Geode Mole', 15, 3, 'ground', 2.2, 'quad'), ('amethyst_fox', 'Amethyst Fox', 15, 4, 'ground', 3.2, 'quad'),
    ('crystal_anemone', 'Crystal Anemone', 15, 5, 'ground', 8.0, 'blob'), ('quartz_dragon', 'Quartz Dragon', 15, 6, 'ground', 12.0, 'dragon'),
    ('aurora_weasel', 'Aurora Weasel', 16, 1, 'ground', 1.8, 'quad'), ('arctic_hare', 'Arctic Hare', 16, 2, 'ground', 2.6, 'sit'),
    ('moon_owl', 'Moon Owl', 16, 3, 'air', 3.0, 'bird'), ('lunar_wolf', 'Lunar Wolf', 16, 4, 'ground', 4.2, 'quad'),
    ('tundra_muskox', 'Tundra Muskox', 16, 5, 'ground', 8.5, 'quad'), ('aurora_bear', 'Aurora Bear', 16, 6, 'ground', 11.0, 'quad'),
    ('aether_ribbonfish', 'Aether Ribbonfish', 17, 1, 'air', 1.6, 'serp'), ('cloud_sheep', 'Cloud Sheep', 17, 2, 'ground', 2.8, 'quad'),
    ('island_chameleon', 'Island Chameleon', 17, 3, 'ground', 2.4, 'quad'), ('sky_stag', 'Sky Stag', 17, 4, 'ground', 5.0, 'quad'),
    ('cloud_glider', 'Cloud Glider', 17, 5, 'air', 2.6, 'fish'), ('sky_drake', 'Sky Drake', 17, 6, 'air', 7.0, 'dragon'),
    ('void_lamprey', 'Void Lamprey', 18, 1, 'air', 1.6, 'serp'), ('dusk_panther', 'Dusk Panther', 18, 2, 'ground', 3.4, 'quad'),
    ('gloom_sloth', 'Gloom Sloth', 18, 3, 'ground', 3.0, 'sit'), ('shadow_mantis', 'Shadow Mantis', 18, 4, 'ground', 4.0, 'bug'),
    ('rift_axolotl', 'Rift Axolotl', 18, 5, 'air', 3.2, 'fish'), ('void_behemoth', 'Void Behemoth', 18, 6, 'ground', 13.0, 'quad'),
    ('nebula_tardigrade', 'Nebula Tardigrade', 19, 1, 'ground', 1.6, 'bug'), ('comet_fox', 'Comet Fox', 19, 2, 'ground', 2.8, 'quad'),
    ('astral_starfish', 'Astral Starfish', 19, 3, 'ground', 2.4, 'blob'), ('stellar_stag', 'Stellar Stag', 19, 4, 'ground', 5.0, 'quad'),
    ('orbital_jellyfish', 'Orbital Jellyfish', 19, 5, 'air', 8.0, 'fish'), ('astral_dragon', 'Astral Dragon', 19, 6, 'air', 12.0, 'dragon'),
    ('spring_strider', 'Spring Strider', 20, 1, 'ground', 2.0, 'bug'), ('copper_weevil', 'Copper Weevil', 20, 2, 'ground', 2.0, 'bug'),
    ('gear_sentinel', 'Gear Sentinel', 20, 3, 'ground', 4.0, 'biped'), ('magnet_tripod', 'Magnet Tripod', 20, 4, 'ground', 4.5, 'bug'),
    ('iron_hound', 'Iron Hound', 20, 5, 'ground', 8.0, 'quad'), ('clockwork_basilisk', 'Clockwork Basilisk', 20, 6, 'ground', 9.0, 'serp'),
    ('shelf_millipede', 'Shelf Millipede', 21, 1, 'ground', 1.4, 'serp'), ('peat_leech', 'Peat Leech', 21, 2, 'ground', 1.6, 'serp'),
    ('lantern_slug', 'Lantern Slug', 21, 3, 'ground', 2.4, 'serp'), ('mycelium_bloomstalker', 'Mycelium Bloomstalker', 21, 4, 'ground', 4.5, 'biped'),
    ('spore_marauder', 'Spore Marauder', 21, 5, 'ground', 8.0, 'biped'), ('cap_mantis', 'Cap Mantis', 21, 6, 'ground', 9.0, 'bug'),
    ('fossil_trilobite', 'Fossil Trilobite', 22, 1, 'ground', 0.9, 'bug'), ('dune_ankylosaur', 'Dune Ankylosaur', 22, 2, 'ground', 4.0, 'quad'),
    ('fossil_ceratopsian', 'Fossil Ceratopsian', 22, 3, 'ground', 5.5, 'quad'), ('skeletal_colossus', 'Skeletal Colossus', 22, 4, 'ground', 7.5, 'biped'),
    ('sand_reaper', 'Sand Reaper', 22, 5, 'ground', 6.0, 'bug'), ('bone_vulture', 'Bone Vulture', 22, 6, 'air', 9.0, 'bird'),
    ('abyss_sea_urchin', 'Abyss Sea Urchin', 23, 1, 'ground', 1.6, 'blob'), ('citadel_cuttlefish', 'Citadel Cuttlefish', 23, 2, 'water', 1.8, 'fish'),
    ('cathedral_clam', 'Cathedral Clam', 23, 3, 'ground', 3.0, 'blob'), ('trench_angler', 'Trench Angler', 23, 4, 'water', 4.5, 'fish'),
    ('pressure_colossus', 'Pressure Colossus', 23, 5, 'ground', 10.0, 'biped'), ('abyss_octopus', 'Abyss Octopus', 23, 6, 'water', 10.0, 'fish'),
    ('fulgurite_cricket', 'Fulgurite Cricket', 24, 1, 'ground', 1.6, 'bug'), ('rift_kangaroo', 'Rift Kangaroo', 24, 2, 'ground', 4.0, 'sit'),
    ('thunder_centaur', 'Thunder Centaur', 24, 3, 'ground', 5.5, 'quad'), ('prism_revenant', 'Prism Revenant', 24, 4, 'air', 4.5, 'flyer'),
    ('storm_harrier', 'Storm Harrier', 24, 5, 'air', 5.5, 'bird'), ('rift_serpent', 'Rift Serpent', 24, 6, 'ground', 11.0, 'serp'),
    ('caldera_tarsier', 'Caldera Tarsier', 25, 1, 'ground', 1.6, 'sit'), ('ember_salamander', 'Ember Salamander', 25, 2, 'ground', 2.0, 'quad'),
    ('magma_hippo', 'Magma Hippo', 25, 3, 'ground', 3.0, 'quad'), ('lava_dragonfly', 'Lava Dragonfly', 25, 4, 'air', 2.5, 'flyer'),
    ('volcanic_wyrm', 'Volcanic Wyrm', 25, 5, 'ground', 10.0, 'serp'), ('primordial_titan', 'Primordial Titan', 25, 6, 'ground', 14.0, 'biped'),
]

FIXED = {'rabbit': ('leap', 'sniff', 'Open_Part'), 'squirrel': ('drop_from_above', 'tail_wave', 'Open_Burst'),
         'hedgehog': ('roll_ball', 'shake_off', 'Open_Part'), 'fox': ('pounce', 'spin', 'Open_Burst'),
         'dodo': ('trot', 'wing_puff', 'Open_Part'), 'moonrabbit': ('flash_appear', 'bow', 'Open_Burst')}

# hand-picked pairs (checked for uniqueness together with the solver). Animals already built (status done in roster.json)
# are frozen automatically, so later edits never reshuffle finished biomes.
OVERRIDE = {
    'roe': ('hop_series', 'ear_wiggle', 'Open_Part'), 'boar': ('charge', 'stomp_hoof', 'Open_Burst'),
    'badger': ('dig_out', 'sniff', 'Open_Part'), 'wolf': ('trot', 'roar', 'Open_Part'),
    'lynx': ('sneak_peek', 'stretch', 'Open_Part'), 'sabertooth': ('sky_leap', 'head_toss', 'Open_Burst'),
    'deer': ('leap', 'look_around', 'Open_Part'), 'moose': ('march', 'head_toss', 'Open_Part'),
    'bear': ('sneak_peek', 'rear_up', 'Open_Part'), 'bison': ('charge', 'shake_off', 'Open_Burst'),
    'cavebear': ('shadow_rise', 'roar', 'Open_Burst'), 'spiritdeer': ('pillar_rise', 'bow', 'Open_Burst'),
    'megadeer': ('trot', 'rear_up', 'Open_Part'), 'rhino': ('march', 'stomp_hoof', 'Open_Part'),
    'mammoth': ('titan_step', 'roar', 'Open_Burst'), 'cavelion': ('pounce', 'stretch', 'Open_Burst'),
    'icemammoth': ('quake_rise', 'head_toss', 'Open_Burst'), 'yeti': ('mound_burst_giant', 'chest_beat', 'Open_Burst'),
    'watchful_meerkat': ('dig_out', 'look_around', 'Open_Part'), 'gazelle': ('leap', 'jump_joy', 'Open_Part'),
    'savanna_ostrich': ('zigzag', 'preen', 'Open_Part'), 'hyena': ('sneak_peek', 'wiggle', 'Open_Part'),
    'sunlion': ('flash_appear', 'roar', 'Open_Burst'), 'amber_giraffe': ('titan_step', 'head_toss', 'Open_Burst'),
    'rock_hyrax': ('crawl_out', 'sniff', 'Open_Part'), 'mountain_goat': ('leap', 'stomp_hoof', 'Open_Part'),
    'canyon_roadrunner': ('zigzag', 'tail_wave', 'Open_Part'), 'armadillo': ('roll_ball', 'look_around', 'Open_Part'),
    'canyon_condor': ('spiral_up', 'wing_flap', 'Open_Burst'), 'redthorn_lizard': ('quake_rise', 'roar', 'Open_Burst'),
    'oasis_scarab': ('roll_ball', 'antenna_twitch', 'Open_Part'), 'fennec': ('dig_out', 'ear_wiggle', 'Open_Part'),
    'dune_jerboa': ('hop_series', 'tail_wave', 'Open_Part'), 'dune_scorpion': ('burst_from_mound', 'claw_snap', 'Open_Burst'),
    'sand_wyrm': ('quake_rise', 'coil', 'Open_Burst'), 'mirage_camel': ('rune_gate', 'head_toss', 'Open_Burst'),
    'jade_tapir': ('trot', 'sniff', 'Open_Part'), 'toucan': ('swoop_arc', 'preen', 'Open_Part'),
    'leafcutter_ant': ('march', 'flex', 'Open_Part'), 'jaguar': ('pounce', 'roar', 'Open_Burst'),
    'jungle_gorilla': ('shadow_rise', 'chest_beat', 'Open_Burst'), 'emerald_treefrog': ('sky_leap', 'puff_up', 'Open_Burst'),
    'mudskipper': ('slide_out', 'fin_flap', 'Open_Part'), 'otter': ('tumble', 'clap', 'Open_Burst'),
    'mangrove_fiddler': ('dig_out', 'claw_snap', 'Open_Part'), 'crocodile': ('crawl_out', 'roar', 'Open_Part'),
    'marsh_hydra': ('quake_rise', 'look_around', 'Open_Burst'), 'mangrove_flamingo': ('vortex_lift', 'wing_puff', 'Open_Burst'),
    'storm_stone_spider': ('crawl_out', 'antenna_twitch', 'Open_Part'), 'storm_ram': ('charge', 'head_toss', 'Open_Burst'),
    'highland_yak': ('march', 'shake_off', 'Open_Part'), 'thunder_eagle': ('rocket_up', 'wing_flap', 'Open_Burst'),
    'storm_griffin': ('dive', 'roar', 'Open_Burst'), 'tempest_pterosaur': ('loop_in', 'wing_puff', 'Open_Burst'),
    'spiral_hermit_crab': ('sneak_peek', 'claw_snap', 'Open_Part'), 'sea_turtle': ('crawl_out', 'yawn', 'Open_Part'),
    'lagoon_pelican': ('dive', 'preen', 'Open_Burst'), 'sea_lion': ('slide_out', 'clap', 'Open_Part'),
    'coral_wyvern': ('whirlpool_rise', 'roar', 'Open_Burst'), 'azure_horseshoe_crab': ('pillar_rise', 'antenna_twitch', 'Open_Burst'),
    'pearl_nautilus': ('bubble_rise', 'spin', 'Open_Part'), 'reef_ray': ('breach_arc', 'fin_flap', 'Open_Burst'),
    'coral_seahorse': ('geyser_ride', 'coil', 'Open_Burst'), 'hammer_shark': ('jet_burst', 'head_toss', 'Open_Burst'),
    'abyss_leviathan': ('splash_up', 'roar', 'Open_Burst'), 'reef_lobster': ('comet_fall', 'claw_snap', 'Open_Burst'),
    'cinder_porcupine': ('crawl_out', 'puff_up', 'Open_Part'), 'ash_lizard': ('zigzag', 'look_around', 'Open_Part'),
    'ash_anteater': ('sneak_peek', 'sniff', 'Open_Part'), 'ember_boar': ('charge', 'roar', 'Open_Burst'),
    'lava_golem': ('quake_rise', 'chest_beat', 'Open_Burst'), 'ember_mandrill': ('flash_appear', 'clap', 'Open_Burst'),
    'furnace_stag_beetle': ('dig_out', 'antenna_twitch', 'Open_Part'), 'obsidian_crab': ('tumble', 'claw_snap', 'Open_Burst'),
    'caldera_toad': ('hop_series', 'puff_up', 'Open_Part'), 'magma_rhino': ('titan_step', 'stomp_hoof', 'Open_Burst'),
    'phoenix': ('rocket_up', 'wing_puff', 'Open_Burst'), 'obsidian_pangolin': ('pillar_rise', 'coil', 'Open_Burst'),
    'prism_moth': ('flutter_out', 'sparkle_burst', 'Open_Part'), 'crystal_bat': ('loop_in', 'ear_wiggle', 'Open_Burst'),
    'geode_mole': ('dig_out', 'yawn', 'Open_Part'), 'amethyst_fox': ('leap', 'tail_wave', 'Open_Part'),
    'crystal_anemone': ('mound_burst_giant', 'pulse', 'Open_Burst'), 'quartz_dragon': ('shadow_rise', 'wing_flap', 'Open_Burst'),
    'aurora_weasel': ('zigzag', 'stretch', 'Open_Part'), 'arctic_hare': ('hop_series', 'wave_paw', 'Open_Part'),
    'moon_owl': ('spiral_up', 'preen', 'Open_Burst'), 'lunar_wolf': ('sneak_peek', 'roar', 'Open_Part'),
    'tundra_muskox': ('quake_rise', 'stomp_hoof', 'Open_Burst'), 'aurora_bear': ('comet_fall', 'bow', 'Open_Burst'),
    'aether_ribbonfish': ('flutter_out', 'coil', 'Open_Part'), 'cloud_sheep': ('drop_from_above', 'jump_joy', 'Open_Burst'),
    'island_chameleon': ('sneak_peek', 'puff_up', 'Open_Part'), 'sky_stag': ('leap', 'rear_up', 'Open_Part'),
    'cloud_glider': ('swoop_arc', 'wing_puff', 'Open_Burst'), 'sky_drake': ('spiral_up', 'roar', 'Open_Burst'),
    'void_lamprey': ('loop_in', 'coil', 'Open_Burst'), 'dusk_panther': ('sneak_peek', 'tail_wave', 'Open_Part'),
    'gloom_sloth': ('crawl_out', 'stretch', 'Open_Part'), 'shadow_mantis': ('drop_from_above', 'claw_snap', 'Open_Burst'),
    'rift_axolotl': ('flutter_out', 'fin_flap', 'Open_Burst'), 'void_behemoth': ('shadow_rise', 'stomp_hoof', 'Open_Burst'),
}


def _frozen():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'roster.json')
    out = dict(FIXED)
    if os.path.exists(path):
        for r in json.load(open(path, encoding='utf-8'))['animals']:
            if r.get('status') == 'done':
                out[r['id']] = (r['method'], r['gesture'], r['open'])
    for k, v in OVERRIDE.items():
        out.setdefault(k, v)
    return out


# methods: which animals may use them
M_GROUND = ['leap', 'pounce', 'trot', 'hop_series', 'charge', 'dig_out', 'sneak_peek', 'drop_from_above', 'burst_from_mound',
            'grow_from_ground', 'crawl_out', 'spin_out', 'tumble', 'slide_out', 'march', 'zigzag', 'roll_ball']
M_EPIC = ['flash_appear', 'sky_leap', 'comet_fall', 'pillar_rise', 'vortex_lift', 'rune_gate']
M_GIANT = ['shadow_rise', 'quake_rise', 'titan_step', 'mound_burst_giant']
M_AIR = ['rocket_up', 'dive', 'swoop_arc', 'spiral_up', 'flutter_out', 'loop_in']
M_WATER = ['splash_up', 'breach_arc', 'bubble_rise', 'whirlpool_rise', 'jet_burst', 'geyser_ride']
M_SHORE = ['slide_out', 'splash_up', 'crawl_out', 'breach_arc', 'tumble']
NO_ROLL = {'serp', 'blob', 'bird', 'biped'}      # these never roll / tumble
SLOW = {'blob', 'serp'}                          # no leaping for blobs and snakes

G_COMMON = ['look_around', 'bow', 'spin', 'jump_joy', 'shake_off', 'stretch', 'puff_up', 'wiggle']
G_ARCH = {
    'quad': ['roar', 'rear_up', 'sniff', 'stomp_hoof', 'tail_wave', 'head_toss', 'ear_wiggle', 'yawn'],
    'sit': ['roar', 'sniff', 'tail_wave', 'wave_paw', 'yawn', 'ear_wiggle', 'clap', 'chest_beat'],
    'biped': ['roar', 'chest_beat', 'wave_paw', 'stomp_hoof', 'flex', 'clap', 'head_toss', 'yawn'],
    'bird': ['wing_flap', 'wing_puff', 'roar', 'head_toss', 'tail_wave', 'preen', 'stomp_hoof'],
    'dragon': ['roar', 'wing_flap', 'rear_up', 'tail_wave', 'head_toss', 'wing_puff', 'coil'],
    'bug': ['claw_snap', 'antenna_twitch', 'rear_up', 'stomp_hoof', 'head_toss', 'flex'],
    'serp': ['coil', 'roar', 'tail_wave', 'head_toss', 'rear_up', 'yawn'],
    'fish': ['tail_wave', 'fin_flap', 'bubble_blow', 'coil', 'head_toss', 'roar'],
    'blob': ['pulse', 'open_shut', 'sparkle_burst'],
    'flyer': ['wing_flap', 'wing_puff', 'antenna_twitch', 'head_toss', 'sparkle_burst', 'roar'],
}
OPENS = ('Open_Part', 'Open_Burst')


def allowed_methods(row):
    aid, name, biome, r, kind, h, arch = row
    if kind == 'air':
        return list(M_AIR)
    if kind == 'water':
        return list(M_WATER)
    if kind == 'shore':
        return list(M_SHORE)
    if r >= 5:
        return (list(M_GIANT) if h >= 8 else []) + list(M_EPIC)
    if h >= 8:
        return list(M_GIANT)
    ms = list(M_GROUND)
    if arch in NO_ROLL or h > 4:
        ms = [m for m in ms if m not in ('roll_ball', 'tumble')]
    if arch in SLOW:
        ms = [m for m in ms if m not in ('leap', 'pounce', 'hop_series', 'charge', 'trot', 'zigzag', 'drop_from_above', 'march')]
    if h > 5:
        ms = [m for m in ms if m not in ('drop_from_above', 'hop_series', 'sneak_peek', 'zigzag')]
    return ms


def assign():
    pairs = {}
    used = set()
    mcount, gcount = {}, {}
    FIX = _frozen()
    for aid, (m, g, o) in FIX.items():
        pairs[aid] = (m, g, o)
        used.add((m, g))
        mcount[m] = mcount.get(m, 0) + 1
        gcount[g] = gcount.get(g, 0) + 1
    by_biome = {}
    for row in R:
        by_biome.setdefault(row[2], []).append(row)
    # tightest biomes first: most air / water / epic animals
    order = sorted(by_biome, key=lambda b: -sum(1 for r in by_biome[b] if r[4] != 'ground' or r[3] >= 5))
    for b in order:
        rows = [r for r in by_biome[b] if r[0] not in FIX]
        if not rows:
            continue
        bm0 = {FIX[r[0]][0] for r in by_biome[b] if r[0] in FIX}
        bg0 = {FIX[r[0]][1] for r in by_biome[b] if r[0] in FIX}
        rows.sort(key=lambda r: len(allowed_methods(r)))
        best = [None]

        def rec(i, bm, bg, acc):
            if best[0] is not None:
                return
            if i == len(rows):
                best[0] = list(acc)
                return
            row = rows[i]
            ms = sorted([m for m in allowed_methods(row) if m not in bm], key=lambda m: (mcount.get(m, 0), m))
            gs_all = G_ARCH[row[6]] + G_COMMON
            gs = sorted([g for g in gs_all if g not in bg], key=lambda g: (gcount.get(g, 0), gs_all.index(g)))
            for m in ms:
                for g in gs:
                    if (m, g) in used:
                        continue
                    acc.append((row[0], m, g))
                    rec(i + 1, bm | {m}, bg | {g}, acc)
                    if best[0] is not None:
                        return
                    acc.pop()
        rec(0, bm0, bg0, [])
        assert best[0], 'no assignment for biome %d' % b
        for k, (aid, m, g) in enumerate(best[0]):
            row = next(r for r in rows if r[0] == aid)
            o = 'Open_Burst' if (row[3] >= 5 or m in ('pounce', 'charge', 'burst_from_mound', 'drop_from_above', 'rocket_up',
                                                     'splash_up', 'breach_arc', 'spin_out', 'tumble', 'dive')) else 'Open_Part'
            pairs[aid] = (m, g, o)
            used.add((m, g))
            mcount[m] = mcount.get(m, 0) + 1
            gcount[g] = gcount.get(g, 0) + 1
    return pairs


def build():
    pairs = assign()
    out = []
    for aid, name, biome, r, kind, h, arch in R:
        m, g, o = pairs[aid]
        out.append(dict(id=aid, name=name, biome=biome, biome_key=BIOMES[biome][0], rarity=r, kind=kind, height=h, arch=arch,
                        method=m, gesture=g, open=o))
    return out


def validate(rows):
    assert len(rows) == 150, len(rows)
    assert len({r['id'] for r in rows}) == 150
    ps = [(r['method'], r['gesture']) for r in rows]
    assert len(set(ps)) == 150, 'duplicate pairs'
    for b in BIOMES:
        rs = [r for r in rows if r['biome'] == b]
        assert len(rs) == 6, (b, len(rs))
        assert sorted(r['rarity'] for r in rs) == sorted(r['rarity'] for r in rs)
        assert len({r['method'] for r in rs}) == 6, ('methods repeat in biome', b)
        assert len({r['gesture'] for r in rs}) == 6, ('gestures repeat in biome', b)
    for r in rows:
        if r['kind'] == 'air':
            assert r['method'] in M_AIR, r
        if r['kind'] == 'water':
            assert r['method'] in M_WATER, r
    return True


if __name__ == '__main__':
    rows = build()
    validate(rows)
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'roster.json')
    old = {}
    if os.path.exists(path):
        old = {r['id']: r for r in json.load(open(path, encoding='utf-8'))['animals']}
    for r in rows:
        r['status'] = old.get(r['id'], {}).get('status', 'done' if r['biome'] == 1 else 'todo')
    json.dump(dict(biomes={str(k): dict(key=v[0], name=v[1]) for k, v in BIOMES.items()}, animals=rows),
              open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    for b in BIOMES:
        print(b, BIOMES[b][1], '|', ', '.join('%s:%s+%s' % (r['id'], r['method'], r['gesture']) for r in rows if r['biome'] == b))
    ms, gs = {}, {}
    for r in rows:
        ms[r['method']] = ms.get(r['method'], 0) + 1
        gs[r['gesture']] = gs.get(r['gesture'], 0) + 1
    print(sorted(ms.items(), key=lambda x: -x[1]))
    print(sorted(gs.items(), key=lambda x: -x[1]))
