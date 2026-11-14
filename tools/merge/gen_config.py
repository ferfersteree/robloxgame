import re,json,math
cfgp='/tmp/claude-0/-home-user-robloxgame/a87b1e1b-c730-4078-b9bf-90a63b9c1951/scratchpad/src/ReplicatedStorage/Shared/Config.ModuleScript.lua'
cfg=open(cfgp,encoding='utf-8').read()
prof=json.load(open('profiles.json'))
rows=re.findall(r'\{ id = "([a-z0-9_]+)", icon = "([^"]*)", zone = (\d+), rarity = (\d),',cfg)
have={a:(int(z),int(r)) for a,i,z,r in rows}
zdesc=dict((int(a),b) for a,b in re.findall(r'\{ id = (\d+), name = "[^"]*".*?desc = "([^"]*)"',cfg))
new=[k for k in prof if k not in have]
assert len(new)==81
# ---- hand-written content for the new species: icon, kg range, one-line fact
D={
'amber_giraffe':('🦒',800,1400,'It nibbles the tallest acacia leaves nobody else can reach.'),
'savanna_ostrich':('🦤',90,150,'Runs faster than any hunter on the open golden plain.'),
'watchful_meerkat':('🐿️',0.6,1.0,'One always stands guard while the rest dig.'),
'canyon_roadrunner':('🐦',0.3,0.5,'Races along canyon trails in a cloud of red dust.'),
'rock_hyrax':('🐹',3,5,'Sunbathes on warm ledges and whistles when you get close.'),
'redthorn_lizard':('🦎',0.1,0.3,'Its red spines match the canyon walls exactly.'),
'mirage_camel':('🐪',450,700,'Seems to shimmer in the heat long before it arrives.'),
'dune_jerboa':('🐭',0.05,0.15,'Leaps three meters across the sand on tiny legs.'),
'oasis_scarab':('🪲',0.02,0.06,'Rolls a ball of sun-warmed clay between the palms.'),
'jade_tapir':('🐗',150,300,'Its green hide vanishes among broad jungle leaves.'),
'emerald_treefrog':('🐸',0.01,0.03,'Sings after rain from the very top of the canopy.'),
'leafcutter_ant':('🐜',0.001,0.004,'Carries a leaf ten times its own size.'),
'mangrove_flamingo':('🦩',2,4,'Stands on one leg for hours in the shallows.'),
'mudskipper':('🐟',0.05,0.2,'A fish that walks out of the water to hunt on the mud.'),
'mangrove_fiddler':('🦀',0.02,0.08,'Waves one giant claw to win its mate.'),
'highland_yak':('🐂',350,800,'Shaggy and unbothered by the fiercest mountain storm.'),
'tempest_pterosaur':('🦅',25,60,'Rides the storm front with wings like leather sails.'),
'storm_stone_spider':('🕷️',8,20,'Weaves webs between lightning-struck stones.'),
'lagoon_pelican':('🐦',8,15,'Scoops up a whole lagoon of fish in one bill.'),
'spiral_hermit_crab':('🦀',1,4,'Hauls a spiral shell as big as a house.'),
'azure_horseshoe_crab':('🦀',2,5,'An ancient survivor of the shallow blue tides.'),
'coral_seahorse':('🐴',40,120,'Coils its tail around coral and drifts with the current.'),
'pearl_nautilus':('🐚',20,60,'Its shell grows one pearly chamber at a time.'),
'reef_lobster':('🦞',5,15,'Rules the reef cracks with enormous claws.'),
'ash_anteater':('🐻',30,60,'Sniffs out insects hiding under warm ash.'),
'cinder_porcupine':('🦔',15,30,'Its quills glow like embers at dusk.'),
'ember_mandrill':('🐒',40,90,'Bright face, brighter temper.'),
'obsidian_pangolin':('🦔',25,60,'Rolls into a ball of black volcanic glass.'),
'furnace_stag_beetle':('🪲',0.3,0.9,'Its horns glow orange in the heat of the vents.'),
'caldera_toad':('🐸',3,9,'Soaks in hot springs that would boil anyone else.'),
'geode_mole':('🐹',1,3,'Tunnels through crystal and leaves tiny geodes behind.'),
'prism_moth':('🦋',0.01,0.03,'Splits moonlight into rainbows with every wingbeat.'),
'crystal_anemone':('🪸',5,15,'Never moves, yet the cave glitters around it.'),
'moon_owl':('🦉',2,5,'Silent wings glow pale under the silver moon.'),
'tundra_muskox':('🐃',250,500,'Herds form a ring around the calves in a blizzard.'),
'aurora_weasel':('🦦',0.5,1.5,'Its fur ripples with colors like the northern lights.'),
'cloud_glider':('🐿️',0.8,2,'Glides between floating islands on soft cloud-fur.'),
'aether_ribbonfish':('🐠',10,40,'A ribbon of silver that swims through thin air.'),
'island_chameleon':('🦎',1,4,'Changes color to match the sky island it clings to.'),
'rift_axolotl':('🦎',0.3,0.9,'Smiles calmly at the edge of a shadow rift.'),
'gloom_sloth':('🦥',8,20,'Moves so slowly that moss grows on its coat.'),
'void_lamprey':('🐍',3,10,'Drifts through the dark with a ring of tiny teeth.'),
'nebula_tardigrade':('🐻',0.1,0.4,'Survives anywhere, even among the stars.'),
'orbital_jellyfish':('🪼',5,20,'Floats in slow orbits around a glowing core.'),
'astral_starfish':('⭐',2,6,'Each arm points to a different distant star.'),
'iron_hound':('🐕',120,260,'Bolted together from old plates, still loyal.'),
'gear_sentinel':('🤖',500,900,'Stands guard while its gears tick slowly.'),
'clockwork_basilisk':('🐍',300,800,'Its stare winds every spring in the garden.'),
'copper_weevil':('🪲',0.5,1.5,'Chews rust off the old pipes and turns green.'),
'magnet_tripod':('🔩',60,150,'Three legs, one strong magnet, no patience.'),
'spring_strider':('🦗',10,30,'Bounces over the gardens on coiled legs.'),
'lantern_slug':('🐌',2,6,'Carries a soft glowing lantern on its back.'),
'spore_marauder':('🍄',150,400,'Leaves a trail of drifting spores behind it.'),
'cap_mantis':('🦗',20,60,'Hides under a mushroom cap, waiting for lunch.'),
'mycelium_bloomstalker':('🌸',80,200,'Walks on threads of living mycelium.'),
'shelf_millipede':('🐛',3,8,'A hundred tiny legs and a shelf-fungus back.'),
'peat_leech':('🪱',1,3,'Waits quietly under the dark peat.'),
'bone_vulture':('🦅',40,90,'Circles over the dunes in a cloak of old bones.'),
'sand_reaper':('🦂',200,450,'Cuts through the dunes with a scythe-shaped tail.'),
'skeletal_colossus':('💀',2000,5000,'Its ribs are a whole canyon of white arches.'),
'fossil_ceratopsian':('🦖',700,1800,'A horned giant that never quite finished fossilizing.'),
'fossil_trilobite':('🪲',0.1,0.4,'Older than the sand it hides in.'),
'dune_ankylosaur':('🦖',900,2200,'Armored like a boulder and just as hard to move.'),
'trench_angler':('🐟',150,400,'Lures prey with a lantern in the deepest trench.'),
'abyss_octopus':('🐙',200,600,'Eight arms, each one holding a different secret.'),
'pressure_colossus':('🗿',3000,7000,'Built to stand where the sea presses hardest.'),
'cathedral_clam':('🐚',400,900,'Its shell rings like a bell in the current.'),
'citadel_cuttlefish':('🦑',10,30,'Flashes warning colors across the citadel walls.'),
'abyss_sea_urchin':('🦔',20,50,'Spines taller than a knight in armor.'),
'rift_serpent':('🐉',400,1000,'Slides between storm clouds and the torn ground.'),
'storm_harrier':('🦅',15,35,'Hunts along the lightning ridges at dusk.'),
'prism_revenant':('👻',5,15,'A restless shimmer that bends light around itself.'),
'thunder_centaur':('🐴',400,800,'Gallops with a crack of thunder at every stride.'),
'fulgurite_cricket':('🦗',0.5,1.5,'Chirps in sparks inside fused lightning glass.'),
'rift_kangaroo':('🦘',60,140,'Bounds between rift ledges in single leaps.'),
'ember_salamander':('🦎',6,15,'Basks in lava pools like a cat on a windowsill.'),
'volcanic_wyrm':('🐲',1500,4000,'Wakes only when the caldera needs to breathe.'),
'primordial_titan':('🗿',20000,60000,'The first creature, still walking after the first fire.'),
'magma_hippo':('🦛',1200,2500,'Wallows in lava that is nearly cool enough to be mud.'),
'lava_dragonfly':('🪰',0.5,2,'Wings like sheets of glowing glass.'),
'caldera_tarsier':('🐒',1,3,'Huge eyes that glow in the red light of the crater.'),
}
assert set(D)==set(new),(set(new)-set(D),set(D)-set(new))
ZN={20:('Rust Gardens','#c9803a','⚙️','Overgrown gear gardens, copper pipes and slow clockwork blooms.','Ticking gears reveal where a clockwork creature is hiding.',5800,6700),
21:('Fungal Bogs','#7bd6b0','🍄','Giant caps, glowing spores and damp peat.','Drifting spores glow brighter near a hidden creature.',6700,7700),
22:('Bone Dunes','#e8dcc0','🦴','Fossil ribs, bleached dunes and buried skeleton arches.','Rattling bones in the sand give away what is moving below.',7700,8800),
23:('Sunken Citadel','#3aa0c8','🏰','A drowned fortress of pearl walls, glowing vents and slow currents.','Bubbles rise along the walls where something big is swimming.',8800,10000),
24:('Storm Rift','#8a7cff','🌩️','A torn sky of lightning, floating shards and humming fulgurite.','Lightning strikes the ground just before a creature crosses the rift.',10000,11300),
25:('Primordial Caldera','#ff7a3d','🌋','The first volcano: molten lakes, ancient ash and giant fossils.','The ground glows hotter along the route of the biggest creature.',11300,12700)}
LOOK={20:('16.5',1.9,'#7a6a55','#b0a08a','#c4a070',.24,1.5,'#c4a070','#8a7a62','#f3ead8',.10,.12,.5),
21:('19.5',1.0,'#3f6a60','#86aa9c','#6fb89a',.45,3.0,'#7cc4a4','#5f8a78','#e6f0ea',.12,.14,1.0),
22:('15.0',2.4,'#a39a82','#c4bca6','#e6dcc0',.18,.8,'#e6dcc0','#a8a08a','#faf6ea',.10,.09,.35),
23:('12.0',1.2,'#3f7098','#7fa2c0','#4f8fba',.30,1.6,'#5a9ac4','#4f7ea6','#e2eef6',.10,.10,.8),
24:('21.0',1.3,'#5a5a8c','#9a9ac4','#8a80c8',.26,1.7,'#8e84cc','#6c68a8','#e8e8f4',.08,.15,1.1),
25:('18.0',1.7,'#6a4a44','#b09890','#d87850',.26,1.8,'#d88056','#8e6a62','#f0e4de',.08,.15,1.1)}
# ---- zone rows
def fh(h): return 'Color3.fromHex("%s")'%h
zlines=[]
for z,(n,col,ic,ds,mech,fr,to) in ZN.items():
    L=LOOK[z]
    look='{ ClockTime = %s, Brightness = %s, Ambient = %s, OutdoorAmbient = %s, FogColor = %s, Density = %s, Haze = %s, AtmoColor = %s, Decay = %s, Tint = %s, Saturation = %s, Contrast = %s, Bloom = %s }'%(L[0],L[1],fh(L[2]),fh(L[3]),fh(L[4]),L[5],L[6],fh(L[7]),fh(L[8]),fh(L[9]),L[10],L[11],L[12])
    zlines.append('\t{ id = %d, name = "%s", from = %d, to = %d, color = %s, icon = "%s", desc = "%s", mechanic = "%s", activeCap = 7, rareLargeCap = 1, look = %s },'%(z,n,fr,to,fh(col),ic,ds,mech,look))
open('config_zones.lua','w',encoding='utf-8').write('\n'.join(zlines)+'\n')
zd={**zdesc,**{z:v[3] for z,v in ZN.items()}}
# ---- rarity assignment per zone
def vol(k):
    b=prof[k]['bounds'];return (b[1][0]-b[0][0])*(b[1][1]-b[0][1])*(b[1][2]-b[0][2])
byz={}
for k in new: byz.setdefault(prof[k]['biome'],[]).append(k)
rar={}
for z,ks in byz.items():
    taken={r for a,(zz,r) in have.items() if zz==z}
    free=[r for r in range(1,7) if r not in taken]
    if len(free)!=len(ks): # zones 1..4 are full; zones 5-19 have 3 taken
        raise SystemExit('zone %d free %s new %s'%(z,free,ks))
    for k,r in zip(sorted(ks,key=vol),free): rar[k]=r
# ---- numbers
P5=5000000
def P(z): return P5*1.85**(z-5)
top_existing={}
for a,(z,r) in have.items(): top_existing[z]=max(top_existing.get(z,0),r)
def mult(z,r):
    if z>=20: return {1:.5,2:1,3:2,4:4,5:10,6:30}[r]
    if r<=4: return {1:.5,2:1,3:2,4:4}[r]
    if r==5: return 12 if top_existing[z]!=5 and top_existing[z]!=6 else (12 if top_existing[z]==5 else 7)
    return 36 if top_existing[z]==5 else 12
def tier(r): return 0 if r<=2 else (1 if r<=4 else 2)
POP={1:80,2:63,3:45,4:29,5:8,6:5}
aquatic_ok={9,11,12}
out=[]
def fmt(v):
    return ('%d'%v) if float(v).is_integer() else ('%g'%v)
def pr(z,r):
    v=P(z)*mult(z,r)
    # keep three significant digits like the existing rows' feel
    return int(round(v))
for k in sorted(new,key=lambda k:(prof[k]['biome'],rar[k])):
    p=prof[k];z=p['biome'];r=rar[k];ic,wmin,wmax,fact=D[k]
    mode=p['mode']
    sp=z; 
    if mode=='air': hab,mv,spk,extra='air','fly','air',', spawnHeights = { 8, 38 }'
    elif mode=='water' and z in aquatic_ok: hab,mv,spk,extra='water','swim','water',', spawnDepths = { 3, 18 }'
    elif mode=='water': hab,mv,spk,extra='air','fly','air',', spawnHeights = { 3, 12 }'
    else: hab,mv,spk,extra='ground','ground','ground',''
    name=' '.join(w.capitalize() for w in k.split('_'))
    sharp=z+1+tier(r); wt=z-1+tier(r)
    if z>=20: sharp=z+1+tier(r); wt=z-1+tier(r)
    out.append('\t{ id = "%s", icon = "%s", zone = %d, rarity = %d, wMin = %s, wMax = %s, price = %d, sharp = %d, weight = %d, name = "%s", fact = "%s", habitat = "%s", movementMode = "%s", spawnKind = "%s", populationWeight = %d, habitatDescription = "%s"%s },'%(k,ic,z,r,fmt(wmin),fmt(wmax),pr(z,r),sharp,wt,name,fact,hab,mv,spk,POP[r],zd[z],extra))
open('config_species.lua','w',encoding='utf-8').write('\n'.join(out)+'\n')
print(len(out),'species rows;',len(zlines),'zone rows')
print(out[0]);print(out[40]);print(out[-1]);print(zlines[0][:220])
import collections
print(collections.Counter((prof[k]['biome'],rar[k]) for k in new).most_common(3))
