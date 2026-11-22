# Give every r5 / r6 animal its own crown, orbit pieces and aura layout (the rarity kit was identical everywhere).
import io, re, glob

# id: (crown kind or None, orbit shape, orbit2 shape or None, aura style)
PLAN = {
    'sabertooth': (None, 'flame', None, 'rays'),
    'cavebear': (None, 'leaf', None, 'double'),
    'spiritdeer': ('leaves', 'leaf', 'star', 'petals'),
    'icemammoth': (None, 'shard', None, 'diamond'),
    'yeti': ('shards', 'shard', 'bubble', 'rays'),
    'sunlion': (None, 'flame', None, 'rays'),
    'amber_giraffe': ('crown', 'gem', 'ring', 'ring'),
    'canyon_condor': (None, 'star', None, 'double'),
    'redthorn_lizard': ('flames', 'flame', 'gem', 'diamond'),
    'sand_wyrm': (None, 'cross', None, 'petals'),
    'mirage_camel': ('stars', 'star', 'ring', 'double'),
    'jungle_gorilla': (None, 'leaf', None, 'diamond'),
    'emerald_treefrog': ('halo', 'bubble', 'leaf', 'petals'),
    'marsh_hydra': (None, 'bubble', None, 'ring'),
    'mangrove_flamingo': ('stars', 'leaf', 'bubble', 'rays'),
    'storm_griffin': (None, 'cross', None, 'rays'),
    'tempest_pterosaur': ('shards', 'star', 'cross', 'double'),
    'azure_horseshoe_crab': ('halo', 'bubble', 'gem', 'diamond'),
    'abyss_leviathan': (None, 'bubble', None, 'double'),
    'reef_lobster': ('crown', 'gem', 'bubble', 'petals'),
    'lava_golem': (None, 'flame', None, 'diamond'),
    'ember_mandrill': ('flames', 'flame', 'star', 'rays'),
    'phoenix': (None, 'flame', None, 'petals'),
    'obsidian_pangolin': ('gears', 'shard', 'flame', 'double'),
    'tundra_muskox': (None, 'cross', None, 'double'),
}


def func_span(s, name):
    a = s.index('\ndef %s(' % name)
    b = s.find('\ndef ', a + 5)
    c = s.find('\nANIMALS', a)
    if b == -1 or (c != -1 and c < b):
        b = c
    return a, b


def apply():
    changed = []
    for fn in sorted(glob.glob('biome_[0-9][0-9].py')):
        s = io.open(fn, encoding='utf-8').read()
        for aid, (crown, o1, o2, aura) in PLAN.items():
            if '\ndef %s(' % aid not in s:
                continue
            a, b = func_span(s, aid)
            body = s[a:b]
            nb = body
            if crown:
                nb = re.sub(r"kind='[a-z]+'\)", "kind='%s')" % crown, nb)
            # first orbit_kit gets o1, an orbit named orbit2 gets o2
            lines = nb.split('\n')
            first = True
            for i, ln in enumerate(lines):
                if 'orbit_kit(' in ln:
                    shp = o2 if ("name='orbit2'" in ln and o2) else (o1 if first else None)
                    if shp is None:
                        continue
                    if "shape='" in ln:
                        ln = re.sub(r"shape='[a-z]+'", "shape='%s'" % shp, ln)
                    else:
                        ln = ln.rstrip(')') + ", shape='%s')" % shp
                    lines[i] = ln
                    if "name='orbit2'" not in ln:
                        first = False
                if 'aura_kit(' in ln and 'def ' not in ln:
                    if "style='" in ln:
                        ln = re.sub(r"style='[a-z]+'", "style='%s'" % aura, ln)
                    else:
                        ln = ln.rstrip(')') + ", style='%s')" % aura
                    lines[i] = ln
            nb = '\n'.join(lines)
            if nb != body:
                s = s[:a] + nb + s[b:]
                changed.append(aid)
        io.open(fn, 'w', encoding='utf-8', newline=chr(10)).write(s)
    return changed


if __name__ == '__main__':
    print(apply())
