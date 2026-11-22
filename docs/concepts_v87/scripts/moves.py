# SpearHunt V87 - reveal methods, signature gestures, idle loops and FX, shared by every animal.
# Rotation signs (degrees): head +X = nose down; body +X = lean forward; leg -X = swing forward; tail +X = up, Z = wag;
# wing up = rot Y -sign*angle (R wing: negative). All clips are 30 fps, frames start at 1.
import random as _random
from faunalib import *
import faunalib as L
from kits import K

THEME = dict(bits=['#5cc23e', '#ff8fc0'], dust='#f1e0bc', glow='#ffe14a', splash='#bfeaff', bit_name='листья')

# ---------------------------------------------------------------- text for reveal_table.md (ru): what happens / Roblox recipe
M_TXT = {
    'leap': ('приседает в кусте и выпрыгивает дугой, приземляется со сжатием', 'твин CFrame корня по дуге (3 ключа), Motor6D ног'),
    'pounce': ('прижимается и бросается вперёд длинным прыжком, передние лапы вытянуты', 'твин корня по дуге + наклон тела'),
    'trot': ('выбегает рысцой: тело покачивается, ноги попеременно', 'линейный твин корня, циклы Motor6D ног'),
    'hop_series': ('выскакивает тремя короткими прыжками подряд', 'три дуги корня по 7 кадров'),
    'charge': ('вылетает разгоном, проскакивает точку и тормозит юзом назад', 'быстрый твин корня с перелётом и возвратом, наклон тела'),
    'dig_out': ('выкапывается из-под земли перед кустом: сначала кочка, потом зверь поднимается, виляя', 'твин корня снизу вверх с покачиванием, кочка — части с твином Size'),
    'sneak_peek': ('выглядывает из куста, прячется обратно и только потом выходит', 'твин корня вперёд-назад-вперёд'),
    'drop_from_above': ('показывается над кустом и падает сверху с сальто', 'твин корня сверху вниз + оборот 360° по X'),
    'burst_from_mound': ('земля вспучивается кочкой, зверь вырывается из неё вверх и приземляется', 'кочка из блоков (Size), твин корня вверх и вниз'),
    'grow_from_ground': ('вырастает из земли: из маленького ростка до полного размера с перелётом масштаба', 'твин масштаба модели (ScaleTo) 0.05 → 1.15 → 1'),
    'crawl_out': ('выползает, прижавшись к земле, ноги часто перебирают, потом встаёт', 'линейный твин корня, тело сжато по высоте'),
    'spin_out': ('вылетает волчком: два оборота вокруг себя, слегка над землёй', 'твин корня + поворот 720° по вертикали'),
    'tumble': ('выкатывается кувырком через голову по дуге', 'дуга корня + оборот 360° вокруг центра тела'),
    'slide_out': ('выезжает на пузе, проскальзывает точку и поднимается', 'твин корня с торможением, тело наклонено и сжато'),
    'march': ('выходит тяжёлыми шагами с остановками, тело проседает на каждом шаге', 'ступенчатый твин корня, удар — тряска камеры'),
    'zigzag': ('выбегает зигзагом, бросаясь из стороны в сторону', 'твин корня по ломаной + рыскание'),
    'roll_ball': ('выкатывается клубком и разворачивается', 'вращение вокруг центра тела, конечности поджаты (Size)'),
    'flash_appear': ('вспышка в кусте, зверь вылетает свечой с разворотом, зависает в воздухе в позе и приземляется', 'Neon-ядро + PointLight, твин корня вверх, пауза, вниз'),
    'sky_leap': ('огромный прыжок из куста в небо, зависание в высшей точке в позе, удар о землю', 'дуга корня, пауза в воздухе, быстрый спуск'),
    'comet_fall': ('падает кометой с неба, резко тормозит над землёй, зависает в позе и приземляется', 'твин корня сверху, хвост кометы — ParticleEmitter'),
    'pillar_rise': ('поднимается из земли в столбе света, зависает в позе и опускается', 'Neon-столб (Size), твин корня вверх и вниз'),
    'vortex_lift': ('вихрь поднимает зверя из куста по спирали, три оборота, зависание и спуск', 'спиральный твин корня + поворот 1080°'),
    'rune_gate': ('в воздухе раскрываются врата, зверь выходит из них плоской тенью и обретает объём, зависает и спускается', 'Neon-рамка, твин Size по X от 0'),
    'shadow_rise': ('по земле растёт тень и всё дрожит, потом гигант вырастает из куста, подпрыгивает и бьёт о землю', 'тёмный диск (Size), тряска камеры, твин масштаба и корня'),
    'quake_rise': ('земля трясётся, гигант поднимается из-под земли, вздрагивая, подпрыгивает и приземляется с ударом', 'твин корня снизу с дрожью, тряска камеры'),
    'titan_step': ('гигант выходит из куста тремя тяжёлыми шагами, вырастая с каждым шагом', 'ступенчатый твин корня и масштаба, тряска на каждом шаге'),
    'mound_burst_giant': ('огромная кочка вспучивается и лопается, гигант вылетает вверх, зависает и рушится вниз', 'кочка из блоков, твин корня вверх-пауза-вниз'),
    'rocket_up': ('вырывается из куста свечой вверх и зависает', 'быстрый твин корня вверх с перелётом'),
    'dive': ('пикирует с неба почти до земли и взмывает на высоту зависания', 'твин корня сверху вниз и вверх, наклон тела'),
    'swoop_arc': ('влетает широкой дугой сбоку с креном', 'твин корня по дуге + крен'),
    'spiral_up': ('поднимается от земли по сужающейся спирали', 'спиральный твин корня'),
    'flutter_out': ('выпархивает, ныряя вверх-вниз', 'твин корня по волне, частые взмахи'),
    'loop_in': ('влетает и делает мёртвую петлю', 'твин корня + оборот 360° по X'),
    'splash_up': ('выныривает снизу столбом брызг, взлетает выше точки и опускается', 'твин корня снизу вверх, всплеск — ParticleEmitter'),
    'breach_arc': ('выпрыгивает дугой, как дельфин, с наклоном носа', 'дуга корня + тангаж'),
    'bubble_rise': ('медленно всплывает в пузырях, покачиваясь', 'твин корня вверх с покачиванием, пузыри — ParticleEmitter'),
    'whirlpool_rise': ('поднимается из водоворота, вращаясь', 'твин корня вверх + поворот 720°'),
    'jet_burst': ('выстреливает струёй вперёд, вытянувшись, и отскакивает назад', 'быстрый твин корня с перелётом, растяжение по длине'),
    'geyser_ride': ('гейзер подбрасывает зверя вверх, тот зависает на струе и опускается', 'столб воды (Size), твин корня вверх-пауза-вниз'),
}
G_TXT = {
    'sniff': 'принюхивается: голова влево-вправо с мелкими кивками',
    'look_around': 'оглядывается: быстрый поворот головы в одну и в другую сторону',
    'bow': 'глубокий поклон',
    'spin': 'кружится на месте (оборот 360°)',
    'jump_joy': 'два радостных прыжка на месте',
    'shake_off': 'отряхивается всем телом',
    'stretch': 'потягивается: передом вниз, задом вверх',
    'puff_up': 'раздувается и сдувается',
    'wiggle': 'виляет всем телом из стороны в сторону',
    'roar': 'рёв: голова вверх, тело раздувается, от морды расходятся кольца',
    'rear_up': 'встаёт на дыбы',
    'stomp_hoof': 'бьёт передней ногой по земле',
    'tail_wave': 'машет хвостом',
    'head_toss': 'вскидывает голову и встряхивает ею',
    'ear_wiggle': 'шевелит ушами по очереди',
    'yawn': 'зевает и клюёт носом',
    'wave_paw': 'машет лапой',
    'clap': 'хлопает в ладоши',
    'chest_beat': 'бьёт себя в грудь',
    'flex': 'показывает мускулы: руки или клешни вверх',
    'wing_flap': 'три широких взмаха крыльями',
    'wing_puff': 'раздувается и трепещет крыльями',
    'preen': 'чистит перья: голова к крылу',
    'coil': 'сворачивается кольцом и распрямляется',
    'claw_snap': 'щёлкает клешнями или передними лапами',
    'antenna_twitch': 'дёргает усиками',
    'fin_flap': 'хлопает плавниками',
    'bubble_blow': 'пускает пузыри',
    'pulse': 'пульсирует: сжимается и расширяется',
    'open_shut': 'открывается и захлопывается',
    'sparkle_burst': 'вспыхивает искрами',
}


# ---------------------------------------------------------------- helpers
def rb(a, dz):
    """root rotation = where the method left it (may be a multiple of 360) + extra yaw"""
    r = a.rbase
    return (r[0], r[1], r[2] + dz)


def has(a, s):
    return s in a.segs


def kk(c, s, f, **kw):
    if s == 'root' or s in K.a.segs:
        k(c, s, int(round(f)), **kw)


def steps(a, c, f0, f1, period=4, amp=32):
    """alternating leg cycle between f0 and f1"""
    legs = a.legs
    i = 0
    f = f0
    while f <= f1:
        for j, lg in enumerate(legs):
            ph = 1 if (j % 2 == 0) == (i % 2 == 0) else -1
            if 'b' in lg[4:5] or (len(lg) > 5 and lg[4].isdigit() and int(lg[4]) % 2 == 0):
                ph = -ph
            kk(c, lg, f, rot=(amp * ph, 0, 0))
        i += 1
        f += period // 2
    for lg in legs:
        kk(c, lg, f1 + 2, rot=(0, 0, 0))


def flap(a, c, f0, f1, period=4, amp=45, base=0):
    i = 0
    f = f0
    while f <= f1:
        up = i % 2 == 0
        for w in a.wings:
            s = -1 if w.endswith('L') else 1
            kk(c, w, f, rot=(0, -s * (base + (amp if up else -amp * 0.4)), 0))
        i += 1
        f += max(1, period // 2)
    for w in a.wings:
        kk(c, w, f1 + 2, rot=(0, 0, 0))


def tuck(a, c, f0, f1, on=True):
    """legs / head pulled in (rolling, flying kick)"""
    for lg in a.legs + a.arms:
        kk(c, lg, f0, scale=0.35 if on else 1.0)
        kk(c, lg, f1, scale=0.35 if on else 1.0)
        kk(c, lg, f1 + 4, scale=1.0)


def squash(a, c, f, amt=0.8, back=4):
    kk(c, 'body', f, scale=(1 + (1 - amt) * 0.7, 1 + (1 - amt) * 0.7, amt))
    kk(c, 'body', f + back, scale=1.0)


def pose_epic(a, c, f0, f1):
    """show pose while hanging in the air: chest out, limbs and wings spread, ears up, tail up"""
    kk(c, 'body', f0 - 3, rot=(0, 0, 0))
    kk(c, 'body', f0, rot=(-16, 0, 0))
    kk(c, 'body', f1, rot=(-16, 0, 0))
    kk(c, 'body', f1 + 4, rot=(0, 0, 0))
    kk(c, 'head', f0 - 3, rot=(0, 0, 0))
    kk(c, 'head', f0, rot=(-12, 0, 0))
    kk(c, 'head', f1, rot=(-12, 0, 0))
    kk(c, 'head', f1 + 4, rot=(0, 0, 0))
    for i, lg in enumerate(a.legs):
        s = -1 if lg.endswith('L') else 1
        front = ('f' in lg[4:5]) or lg in ('leg_L', 'leg_R') or (lg[4:5].isdigit() and int(lg[4]) == 1)
        r = (-70, s * 30, 0) if front else (35, s * 15, 0)
        kk(c, lg, f0 - 3, rot=(0, 0, 0))
        kk(c, lg, f0, rot=r)
        kk(c, lg, f1, rot=r)
        kk(c, lg, f1 + 4, rot=(0, 0, 0))
    for ar in a.arms:
        if ar in a.legs:
            continue
        s = -1 if ar.endswith('L') else 1
        kk(c, ar, f0 - 3, rot=(0, 0, 0))
        kk(c, ar, f0, rot=(-30, -s * 120, 0))
        kk(c, ar, f1, rot=(-30, -s * 120, 0))
        kk(c, ar, f1 + 4, rot=(0, 0, 0))
    for w in a.wings:
        s = -1 if w.endswith('L') else 1
        kk(c, w, f0 - 3, rot=(0, 0, 0))
        kk(c, w, f0, rot=(0, -s * 50, 0))
        kk(c, w, (f0 + f1) / 2, rot=(0, -s * 30, 0))
        kk(c, w, f1, rot=(0, -s * 55, 0))
        kk(c, w, f1 + 4, rot=(0, 0, 0))
    for e in a.ears:
        s = -1 if e.endswith('L') else 1
        kk(c, e, f0 - 3, rot=(20, 0, 0))
        kk(c, e, f0, rot=(-15, s * 26, 0))
        kk(c, e, f1, rot=(-15, s * 26, 0))
        kk(c, e, f1 + 4, rot=(0, 0, 0))
    for i, t in enumerate(a.tail):
        kk(c, t, f0 - 3, rot=(0, 0, 0))
        kk(c, t, f0, rot=(28, 0, 0))
        kk(c, t, f1, rot=(28, 0, 14))
        kk(c, t, f1 + 4, rot=(0, 0, 0))
    for o in a.orbits:
        kk(c, o, f0 - 3, scale=0.5, rot=(0, 0, 0))
        kk(c, o, f0, scale=1.35, rot=(0, 0, 180))
        kk(c, o, f1, scale=1.35, rot=(0, 0, 540), ease='LINEAR')
        kk(c, o, f1 + 8, scale=1.0, rot=(0, 0, 720))


def roll_keys(a, c, f0, f1, y0, y1, turns, cz, z=0.0, f_end=None):
    """rotation about the body centre (root pivot is at the origin): compensate the offset every frame"""
    for f in range(f0, f1 + 1):
        t = (f - f0) / float(f1 - f0)
        ang = -360.0 * turns * t
        r = math.radians(ang)
        kk(c, 'root', f, loc=(0, y0 + (y1 - y0) * t + cz * math.sin(r), z + cz - cz * math.cos(r)), rot=(ang, 0, 0), ease='LINEAR')


# ---------------------------------------------------------------- ground methods (return frame of arrival at rest)
def m_leap(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, -0.15 * H), scale=0.85)
    kk(c, 'root', 5, loc=(0, D - 0.05, 0), scale=1.0)
    kk(c, 'root', 11, loc=(0, D * 0.45, 0.55 * H))
    kk(c, 'root', 17, loc=(0, 0, 0), ease='LINEAR')
    kk(c, 'body', 1, rot=(0, 0, 0), scale=(1.05, 1.05, 0.85))
    kk(c, 'body', 5, rot=(10, 0, 0), scale=(0.95, 0.95, 1.1))
    kk(c, 'body', 11, rot=(-22, 0, 0), scale=(0.92, 0.92, 1.12))
    kk(c, 'body', 17, rot=(8, 0, 0), scale=(1.14, 1.14, 0.8))
    kk(c, 'body', 21, rot=(0, 0, 0), scale=1.0)
    for lg in a.legs:
        fr = 'f' in lg[4:5]
        kk(c, lg, 1, rot=(0, 0, 0))
        kk(c, lg, 9, rot=(40 if fr else -50, 0, 0))
        kk(c, lg, 15, rot=(-30 if fr else 25, 0, 0))
        kk(c, lg, 19, rot=(0, 0, 0))
    for e in a.ears:
        kk(c, e, 1, rot=(0, 0, 0))
        kk(c, e, 11, rot=(35, 0, 0))
        kk(c, e, 18, rot=(-20, 0, 0))
        kk(c, e, 22, rot=(0, 0, 0))
    return 21


def m_pounce(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, -0.08 * H))
    kk(c, 'root', 6, loc=(0, D + 0.1 * H, -0.12 * H))
    kk(c, 'root', 12, loc=(0, D * 0.45, 0.5 * H))
    kk(c, 'root', 18, loc=(0, 0, 0), ease='LINEAR')
    kk(c, 'body', 1, rot=(0, 0, 0))
    kk(c, 'body', 6, rot=(8, 0, 0), scale=(1.05, 1.05, 0.88))
    kk(c, 'body', 12, rot=(-22, 0, 0), scale=(0.95, 1.1, 1.0))
    kk(c, 'body', 18, rot=(10, 0, 0), scale=(1.1, 0.95, 0.85))
    kk(c, 'body', 21, rot=(0, 0, 0), scale=1.0)
    for lg in a.legs:
        fr = 'f' in lg[4:5]
        kk(c, lg, 6, rot=(0, 0, 0))
        kk(c, lg, 12, rot=(-70 if fr else 60, 0, 0))
        kk(c, lg, 18, rot=(15 if fr else 0, 0, 0))
        kk(c, lg, 21, rot=(0, 0, 0))
    for t in a.tail:
        kk(c, t, 6, rot=(0, 0, 0))
        kk(c, t, 12, rot=(25, 0, 0))
        kk(c, t, 20, rot=(0, 0, 0))
    return 21


def m_trot(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, 0))
    kk(c, 'root', 20, loc=(0, 0, 0), ease='LINEAR')
    for i, f in enumerate(range(1, 21, 4)):
        kk(c, 'body', f, loc=(0, 0, 0), rot=(0, 0, 5 if i % 2 else -5))
        kk(c, 'body', f + 2, loc=(0, 0, 0.05 * H))
        kk(c, 'head', f, rot=(-6 if i % 2 else 6, 0, 0))
    steps(a, c, 1, 20, 4, 34)
    kk(c, 'body', 22, loc=(0, 0, 0), rot=(0, 0, 0))
    kk(c, 'head', 22, rot=(0, 0, 0))
    return 22


def m_hop_series(a, c):
    D, H = a.bush_d, a.H
    for i in range(3):
        f0 = 1 + i * 7
        y0, y1 = D * (1 - i / 3.0), D * (1 - (i + 1) / 3.0)
        kk(c, 'root', f0, loc=(0, y0, 0))
        kk(c, 'root', f0 + 3, loc=(0, (y0 + y1) / 2, 0.3 * H))
        kk(c, 'root', f0 + 6, loc=(0, y1, 0), ease='LINEAR')
        kk(c, 'body', f0, scale=(1.08, 1.08, 0.86), rot=(6, 0, 0))
        kk(c, 'body', f0 + 3, scale=(0.95, 0.95, 1.1), rot=(-10, 0, 0))
        for lg in a.legs:
            fr = 'f' in lg[4:5]
            kk(c, lg, f0, rot=(0, 0, 0))
            kk(c, lg, f0 + 3, rot=(30 if fr else -35, 0, 0))
        for e in a.ears:
            kk(c, e, f0, rot=(-10, 0, 0))
            kk(c, e, f0 + 3, rot=(25, 0, 0))
    kk(c, 'body', 22, scale=1.0, rot=(0, 0, 0))
    for s in a.legs + a.ears:
        kk(c, s, 22, rot=(0, 0, 0))
    return 22


def m_charge(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, 0))
    kk(c, 'root', 11, loc=(0, -0.3 * H, 0), ease='LINEAR')
    kk(c, 'root', 15, loc=(0, -0.38 * H, 0))
    kk(c, 'root', 19, loc=(0, 0, 0))
    kk(c, 'body', 1, rot=(14, 0, 0))
    kk(c, 'body', 11, rot=(14, 0, 0))
    kk(c, 'body', 15, rot=(-12, 0, 0), scale=(1.05, 0.92, 1.0))
    kk(c, 'body', 19, rot=(0, 0, 0), scale=1.0)
    kk(c, 'head', 1, rot=(18, 0, 0))
    kk(c, 'head', 11, rot=(18, 0, 0))
    kk(c, 'head', 16, rot=(-10, 0, 0))
    kk(c, 'head', 20, rot=(0, 0, 0))
    steps(a, c, 1, 11, 2, 45)
    return 20


def m_dig_out(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, 0.1, -1.05 * H), rot=(0, 0, 0))
    kk(c, 'root', 5, loc=(0, 0.1, -1.05 * H))
    for i, f in enumerate(range(6, 17, 2)):
        t = (f - 5) / 11.0
        kk(c, 'root', f, loc=(0, 0.1 * (1 - t), -1.05 * H * (1 - t)), rot=(0, 0, 14 if i % 2 else -14))
    kk(c, 'root', 18, loc=(0, 0, 0.12 * H), rot=(0, 0, 0))
    kk(c, 'root', 21, loc=(0, 0, 0))
    kk(c, 'head', 6, rot=(-25, 0, 0))
    kk(c, 'head', 16, rot=(-25, 0, 0))
    kk(c, 'head', 21, rot=(0, 0, 0))
    squash(a, c, 21, 0.86, 3)
    a.fx_extra.append(('mound', 1, 16, 0.0))
    return 22


def m_sneak_peek(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, 0))
    kk(c, 'root', 6, loc=(0, D * 0.62, 0))
    kk(c, 'root', 9, loc=(0, D * 0.62, 0))
    kk(c, 'root', 12, loc=(0, D * 0.85, 0))
    kk(c, 'root', 14, loc=(0, D * 0.85, 0))
    kk(c, 'root', 23, loc=(0, 0, 0))
    kk(c, 'head', 1, rot=(0, 0, 0))
    kk(c, 'head', 6, rot=(0, 0, 25))
    kk(c, 'head', 9, rot=(0, 0, -25))
    kk(c, 'head', 12, rot=(0, 0, 0))
    kk(c, 'head', 23, rot=(0, 0, 0))
    kk(c, 'body', 1, rot=(8, 0, 0), scale=(1.0, 1.0, 0.9))
    kk(c, 'body', 12, rot=(8, 0, 0), scale=(1.0, 1.0, 0.9))
    kk(c, 'body', 23, rot=(0, 0, 0), scale=1.0)
    steps(a, c, 14, 22, 4, 28)
    return 24


def m_drop_from_above(a, c):
    D, H = a.bush_d, a.H
    top = a.bush_h + 0.3 * H
    kk(c, 'root', 1, loc=(0, D, top), rot=(0, 0, 0), scale=0.9)
    kk(c, 'root', 5, loc=(0, D * 0.6, top + 0.3 * H), rot=(-40, 0, 0), scale=1.0)
    cz = 0.5 * H
    for f in range(6, 14):
        t = (f - 5) / 8.0
        ang = -40 - 320 * t
        r = math.radians(ang)
        kk(c, 'root', f, loc=(0, D * 0.6 * (1 - t) + cz * math.sin(r), (top + 0.3 * H) * (1 - t) ** 1.0 * (1 - t) + cz - cz * math.cos(r)),
           rot=(ang, 0, 0), ease='LINEAR')
    kk(c, 'root', 16, loc=(0, 0, 0.18 * H), rot=(-360, 0, 0))
    kk(c, 'root', 19, loc=(0, 0, 0), rot=(-360, 0, 0))
    kk(c, 'body', 13, scale=(1.2, 1.2, 0.75))
    kk(c, 'body', 16, scale=(0.9, 0.9, 1.1))
    kk(c, 'body', 20, scale=1.0)
    return 20


def m_burst_from_mound(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D * 0.3, -1.05 * H), scale=0.9)
    kk(c, 'root', 8, loc=(0, D * 0.3, -1.05 * H), scale=0.9)
    kk(c, 'root', 13, loc=(0, D * 0.12, 0.55 * H), scale=1.0)
    kk(c, 'root', 18, loc=(0, 0, 0), ease='LINEAR')
    kk(c, 'body', 8, rot=(0, 0, 0))
    kk(c, 'body', 13, rot=(-18, 0, 0), scale=(0.92, 0.92, 1.12))
    kk(c, 'body', 18, rot=(6, 0, 0), scale=(1.14, 1.14, 0.8))
    kk(c, 'body', 21, rot=(0, 0, 0), scale=1.0)
    for lg in a.legs + a.arms:
        s = -1 if lg.endswith('L') else 1
        kk(c, lg, 8, rot=(0, 0, 0))
        kk(c, lg, 13, rot=(-40, s * 25, 0))
        kk(c, lg, 19, rot=(0, 0, 0))
    a.fx_extra.append(('mound', 1, 9, a.bush_d * 0.3))
    return 21


def m_grow_from_ground(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, 0.2 * D, 0), scale=0.03)
    kk(c, 'root', 5, loc=(0, 0.2 * D, 0), scale=0.12, rot=(0, 0, -40))
    kk(c, 'root', 12, loc=(0, 0.05 * D, 0), scale=1.18, rot=(0, 0, 10))
    kk(c, 'root', 15, loc=(0, 0, 0), scale=0.94, rot=(0, 0, 0))
    kk(c, 'root', 18, loc=(0, 0, 0), scale=1.0)
    kk(c, 'head', 5, rot=(20, 0, 0))
    kk(c, 'head', 13, rot=(-15, 0, 0))
    kk(c, 'head', 18, rot=(0, 0, 0))
    return 19


def m_crawl_out(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, 0))
    kk(c, 'root', 19, loc=(0, 0, 0), ease='LINEAR')
    kk(c, 'body', 1, scale=(1.08, 1.05, 0.72), rot=(6, 0, 0))
    kk(c, 'body', 19, scale=(1.08, 1.05, 0.72), rot=(6, 0, 0))
    kk(c, 'body', 23, scale=1.0, rot=(0, 0, 0))
    for i, f in enumerate(range(1, 20, 3)):
        kk(c, 'head', f, rot=(4, 0, 10 if i % 2 else -10))
    kk(c, 'head', 23, rot=(0, 0, 0))
    steps(a, c, 1, 19, 2, 22)
    return 23


def m_spin_out(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, 0.05 * H), rot=(0, 0, 0))
    kk(c, 'root', 9, loc=(0, D * 0.45, 0.28 * H), rot=(0, 0, 400), ease='LINEAR')
    kk(c, 'root', 17, loc=(0, 0, 0.05 * H), rot=(0, 0, 720), ease='LINEAR')
    kk(c, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 720))
    for lg in a.legs:
        s = -1 if lg.endswith('L') else 1
        kk(c, lg, 1, rot=(0, s * 30, 0))
        kk(c, lg, 17, rot=(0, s * 30, 0))
        kk(c, lg, 20, rot=(0, 0, 0))
    for t in a.tail:
        kk(c, t, 1, rot=(10, 0, 30))
        kk(c, t, 17, rot=(10, 0, 30))
        kk(c, t, 21, rot=(0, 0, 0))
    squash(a, c, 20, 0.86, 3)
    return 22


def m_tumble(a, c):
    D, H = a.bush_d, a.H
    cz = 0.45 * H
    kk(c, 'root', 1, loc=(0, D, 0), rot=(0, 0, 0))
    kk(c, 'root', 4, loc=(0, D * 0.9, 0.1 * H), rot=(0, 0, 0))
    for f in range(5, 17):
        t = (f - 4) / 12.0
        ang = -360.0 * t
        r = math.radians(ang)
        arc = 0.45 * H * math.sin(math.pi * t) + 0.1 * H * (1 - t)
        kk(c, 'root', f, loc=(0, D * 0.9 * (1 - t) + cz * math.sin(r), arc + cz - cz * math.cos(r)), rot=(ang, 0, 0), ease='LINEAR')
    kk(c, 'root', 19, loc=(0, 0, 0), rot=(-360, 0, 0))
    tuck(a, c, 4, 16)
    kk(c, 'head', 4, rot=(35, 0, 0))
    kk(c, 'head', 16, rot=(35, 0, 0))
    kk(c, 'head', 20, rot=(0, 0, 0))
    squash(a, c, 18, 0.84, 3)
    return 21


def m_slide_out(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D, 0))
    kk(c, 'root', 14, loc=(0, -0.3 * H, 0))
    kk(c, 'root', 17, loc=(0, -0.3 * H, 0))
    kk(c, 'root', 22, loc=(0, 0, 0))
    kk(c, 'body', 1, rot=(14, 0, 0), scale=(1.08, 1.1, 0.78))
    kk(c, 'body', 15, rot=(14, 0, 0), scale=(1.08, 1.1, 0.78))
    kk(c, 'body', 19, rot=(-6, 0, 0), scale=1.0)
    kk(c, 'body', 22, rot=(0, 0, 0))
    kk(c, 'head', 1, rot=(-16, 0, 0))
    kk(c, 'head', 15, rot=(-16, 0, 0))
    kk(c, 'head', 20, rot=(0, 0, 0))
    for lg in a.legs:
        fr = 'f' in lg[4:5]
        kk(c, lg, 1, rot=(-70 if fr else 70, 0, 0))
        kk(c, lg, 15, rot=(-70 if fr else 70, 0, 0))
        kk(c, lg, 20, rot=(0, 0, 0))
    return 22


def m_march(a, c):
    D, H = a.bush_d, a.H
    n = 4
    for i in range(n):
        f0 = 1 + i * 5
        y0, y1 = D * (1 - i / float(n)), D * (1 - (i + 1) / float(n))
        kk(c, 'root', f0, loc=(0, y0, 0))
        kk(c, 'root', f0 + 3, loc=(0, y1, 0.06 * H))
        kk(c, 'root', f0 + 4, loc=(0, y1, 0))
        kk(c, 'body', f0 + 4, scale=(1.05, 1.05, 0.92), rot=(0, 0, 4 if i % 2 else -4))
        kk(c, 'body', f0 + 2, scale=1.0, rot=(0, 0, 0))
        for j, lg in enumerate(a.legs):
            lift = (j % 2 == i % 2)
            kk(c, lg, f0, rot=(0, 0, 0))
            kk(c, lg, f0 + 2, rot=(-38 if lift else 14, 0, 0))
            kk(c, lg, f0 + 4, rot=(0, 0, 0))
        a.fx_extra.append(('stomp', f0 + 4, 0, y1))
    kk(c, 'body', 23, scale=1.0, rot=(0, 0, 0))
    return 23


def m_zigzag(a, c):
    D, H = a.bush_d, a.H
    pts = ((1, 0.0, 1.0), (6, 0.6, 0.72), (11, -0.6, 0.45), (16, 0.45, 0.18), (21, 0.0, 0.0))
    for i, (f, x, t) in enumerate(pts):
        yaw = 0 if i in (0, len(pts) - 1) else (-35 if x > 0 else 35)
        kk(c, 'root', f, loc=(x * H * 0.6, D * t, 0), rot=(0, 0, yaw), ease='LINEAR')
    for i, f in enumerate(range(1, 21, 5)):
        kk(c, 'body', f, rot=(8, 12 if i % 2 else -12, 0))
    kk(c, 'body', 22, rot=(0, 0, 0))
    steps(a, c, 1, 20, 2, 40)
    return 22


def m_roll_ball(a, c):
    D, H = a.bush_d, a.H
    cz = 0.42 * H
    roll_keys(a, c, 1, 16, D, -0.1 * H, 1.5, cz, 0.0)
    for f in range(17, 21):
        t = (f - 16) / 4.0
        ang = -540 - 180 * t
        r = math.radians(ang)
        kk(c, 'root', f, loc=(0, -0.1 * H * (1 - t) + cz * math.sin(r), cz - cz * math.cos(r)), rot=(ang, 0, 0), ease='LINEAR')
    kk(c, 'body', 1, scale=(0.92, 0.92, 1.0))
    kk(c, 'body', 16, scale=(0.92, 0.92, 1.0))
    kk(c, 'body', 21, scale=1.0)
    kk(c, 'head', 1, rot=(50, 0, 0))
    kk(c, 'head', 16, rot=(50, 0, 0))
    kk(c, 'head', 21, rot=(0, 0, 0))
    tuck(a, c, 1, 16)
    return 21


# ---------------------------------------------------------------- epic methods (rarity 5-6): hang in the air in a pose, then land
def _hover_z(a):
    return max(1.6, min(0.75 * a.H, 5.0))


def _land(a, c, f0, f1):
    kk(c, 'root', f0, loc=(0, 0, _hover_z(a)), scale=1.0)
    kk(c, 'root', f1, loc=(0, 0, 0), ease='LINEAR')
    kk(c, 'body', f1 - 3, scale=1.0)
    kk(c, 'body', f1, scale=(1.15, 1.15, 0.8))
    kk(c, 'body', f1 + 3, scale=1.0)
    a.fx_extra.append(('land_ring', f1, 0, 0.0))


def m_flash_appear(a, c):
    D, hz = a.bush_d, _hover_z(a)
    kk(c, 'root', 1, loc=(0, D, 0.3 * a.H), scale=0.0, rot=(0, 0, -360), ease='CONSTANT')
    kk(c, 'root', 5, loc=(0, D, 0.3 * a.H), scale=0.0, rot=(0, 0, -360))
    kk(c, 'root', 9, loc=(0, D * 0.5, hz + 0.2 * a.H), scale=1.2, rot=(0, 0, -180))
    kk(c, 'root', 13, loc=(0, 0.1 * D, hz), scale=1.0, rot=(0, 0, 0))
    kk(c, 'root', 20, loc=(0, 0.05 * D, hz + 0.1 * a.H))
    pose_epic(a, c, 14, 26)
    _land(a, c, 27, 32)
    a.hang = (13, 27)
    return 35


def m_sky_leap(a, c):
    D, hz = a.bush_d, _hover_z(a)
    kk(c, 'root', 1, loc=(0, D, -0.1 * a.H), scale=0.9)
    kk(c, 'root', 5, loc=(0, D, -0.14 * a.H), scale=1.0)
    kk(c, 'root', 10, loc=(0, D * 0.5, hz * 1.25), rot=(0, 0, 0))
    kk(c, 'root', 14, loc=(0, 0.1 * D, hz * 1.1))
    kk(c, 'root', 20, loc=(0, 0.05 * D, hz * 1.18), rot=(0, 0, 0))
    kk(c, 'root', 26, loc=(0, 0, hz), rot=(0, 0, 360))
    kk(c, 'body', 1, scale=(1.08, 1.08, 0.82))
    kk(c, 'body', 5, scale=(1.08, 1.08, 0.82))
    kk(c, 'body', 9, scale=(0.92, 0.92, 1.14))
    kk(c, 'body', 13, scale=1.0)
    pose_epic(a, c, 14, 25)
    _land(a, c, 26, 30)
    a.hang = (13, 26)
    return 33


def m_comet_fall(a, c):
    D, hz = a.bush_d, _hover_z(a)
    kk(c, 'root', 1, loc=(0, D * 1.2, hz + 5.0 * max(a.H, 2.0)), scale=(0.8, 0.8, 1.25), rot=(35, 0, 0))
    kk(c, 'root', 9, loc=(0, 0.1 * D, hz * 0.8), scale=(0.9, 0.9, 1.15), rot=(20, 0, 0), ease='LINEAR')
    kk(c, 'root', 12, loc=(0, 0.05 * D, hz * 1.12), scale=1.0, rot=(0, 0, 0))
    kk(c, 'root', 19, loc=(0, 0, hz * 1.02))
    pose_epic(a, c, 13, 25)
    _land(a, c, 26, 31)
    a.fx_extra.append(('comet', 1, 9, 0.0))
    a.hang = (12, 26)
    return 34


def m_pillar_rise(a, c):
    D, hz = a.bush_d, _hover_z(a)
    kk(c, 'root', 1, loc=(0, 0.1 * D, -1.1 * a.H), rot=(0, 0, 0))
    kk(c, 'root', 4, loc=(0, 0.1 * D, -1.1 * a.H))
    kk(c, 'root', 13, loc=(0, 0.05 * D, hz * 1.1), rot=(0, 0, 360))
    kk(c, 'root', 20, loc=(0, 0, hz))
    pose_epic(a, c, 14, 25)
    _land(a, c, 26, 31)
    a.fx_extra.append(('pillar', 1, 22, 0.1 * D))
    a.hang = (13, 26)
    return 34


def m_vortex_lift(a, c):
    D, hz = a.bush_d, _hover_z(a)
    for f in range(1, 15):
        t = (f - 1) / 13.0
        ang = 1080 * t
        rr = 0.5 * a.H * (1 - t)
        r = math.radians(ang)
        kk(c, 'root', f, loc=(math.sin(r) * rr, D * (1 - t) + math.cos(r) * rr * 0.3, hz * t ** 0.8), rot=(0, 0, ang), scale=0.4 + 0.6 * t, ease='LINEAR')
    kk(c, 'root', 20, loc=(0, 0, hz * 1.08), rot=(0, 0, 1080))
    pose_epic(a, c, 15, 25)
    _land(a, c, 26, 31)
    a.fx_extra.append(('vortex', 1, 14, 0.0))
    a.hang = (14, 26)
    return 34


def m_rune_gate(a, c):
    D, hz = a.bush_d, _hover_z(a)
    kk(c, 'root', 1, loc=(0, D * 0.4, hz), scale=0.0, ease='CONSTANT')
    kk(c, 'root', 6, loc=(0, D * 0.4, hz), scale=(0.02, 1.0, 1.0))
    kk(c, 'root', 10, loc=(0, D * 0.25, hz), scale=(0.08, 1.05, 1.05))
    kk(c, 'root', 14, loc=(0, 0.05 * D, hz * 1.05), scale=(1.15, 1.0, 1.0))
    kk(c, 'root', 17, loc=(0, 0, hz), scale=1.0)
    kk(c, 'root', 22, loc=(0, 0, hz * 1.06))
    pose_epic(a, c, 16, 25)
    _land(a, c, 26, 31)
    a.fx_extra.append(('gate', 2, 16, D * 0.4))
    a.hang = (14, 26)
    return 34


def _giant_hop(a, c, f0):
    """giants do not float: a heavy little hop with the show pose, then a ground slam"""
    H = a.H
    kk(c, 'root', f0, loc=(0, 0, 0), scale=1.0, rot=(0, 0, 0))
    kk(c, 'root', f0 + 4, loc=(0, 0, 0.16 * H))
    kk(c, 'root', f0 + 7, loc=(0, 0, 0.18 * H))
    kk(c, 'root', f0 + 10, loc=(0, 0, 0), ease='LINEAR')
    if a.rarity >= 5:
        pose_epic(a, c, f0 + 3, f0 + 7)
    kk(c, 'body', f0 + 8, scale=1.0)
    kk(c, 'body', f0 + 10, scale=(1.12, 1.12, 0.84))
    kk(c, 'body', f0 + 13, scale=1.0)
    a.fx_extra.append(('land_ring', f0 + 10, 0, 0.0))
    a.fx_extra.append(('stomp', f0 + 10, 0, 0.0))
    a.hang = (f0 + 3, f0 + 8)
    return f0 + 13


def m_shadow_rise(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, D * 0.5, -0.2 * H), scale=0.0, ease='CONSTANT')
    kk(c, 'root', 9, loc=(0, D * 0.5, -0.2 * H), scale=0.0)
    kk(c, 'root', 12, loc=(0, D * 0.45, -0.1 * H), scale=0.25)
    kk(c, 'root', 20, loc=(0, 0, 0), scale=1.06)
    a.fx_extra.append(('shadow', 1, 14, D * 0.25))
    a.fx_extra.append(('quake', 2, 12, 0.0))
    kk(c, 'head', 12, rot=(18, 0, 0))
    kk(c, 'head', 20, rot=(-10, 0, 0))
    kk(c, 'head', 23, rot=(0, 0, 0))
    return _giant_hop(a, c, 21)


def m_quake_rise(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, 0.15 * D, -1.05 * H))
    kk(c, 'root', 4, loc=(0, 0.15 * D, -1.05 * H))
    for i, f in enumerate(range(5, 20, 2)):
        t = (f - 4) / 16.0
        kk(c, 'root', f, loc=((0.04 if i % 2 else -0.04) * H, 0.15 * D * (1 - t), -1.05 * H * (1 - t)), rot=(0, 0, 5 if i % 2 else -5))
    kk(c, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 0))
    a.fx_extra.append(('quake', 1, 18, 0.0))
    a.fx_extra.append(('mound', 1, 18, 0.15 * D))
    return _giant_hop(a, c, 21)


def m_titan_step(a, c):
    D, H = a.bush_d, a.H
    n = 3
    for i in range(n):
        f0 = 3 + i * 6
        y0, y1 = D * (1 - i / float(n)), D * (1 - (i + 1) / float(n))
        s0, s1 = 0.35 + 0.65 * i / n, 0.35 + 0.65 * (i + 1) / n
        kk(c, 'root', f0, loc=(0, y0, 0), scale=s0)
        kk(c, 'root', f0 + 4, loc=(0, y1, 0.07 * H), scale=s1)
        kk(c, 'root', f0 + 5, loc=(0, y1, 0), scale=s1)
        kk(c, 'body', f0 + 5, scale=(1.05, 1.05, 0.9), rot=(0, 0, 5 if i % 2 else -5))
        kk(c, 'body', f0 + 2, scale=1.0, rot=(0, 0, 0))
        for j, lg in enumerate(a.legs):
            lift = (j % 2 == i % 2)
            kk(c, lg, f0, rot=(0, 0, 0))
            kk(c, lg, f0 + 3, rot=(-36 if lift else 14, 0, 0))
            kk(c, lg, f0 + 5, rot=(0, 0, 0))
        a.fx_extra.append(('stomp', f0 + 5, 0, y1))
    kk(c, 'root', 1, loc=(0, D, 0), scale=0.35)
    kk(c, 'body', 21, scale=1.0, rot=(0, 0, 0))
    if a.rarity >= 5:
        return _giant_hop(a, c, 21)
    return 22


def m_mound_burst_giant(a, c):
    D, H = a.bush_d, a.H
    kk(c, 'root', 1, loc=(0, 0.3 * D, -1.05 * H), scale=0.9)
    kk(c, 'root', 10, loc=(0, 0.3 * D, -1.05 * H), scale=0.9)
    kk(c, 'root', 16, loc=(0, 0.1 * D, 0.25 * H), scale=1.0)
    kk(c, 'root', 21, loc=(0, 0, 0), ease='LINEAR')
    a.fx_extra.append(('mound', 1, 11, 0.3 * D))
    a.fx_extra.append(('quake', 1, 10, 0.0))
    kk(c, 'body', 10, rot=(0, 0, 0))
    kk(c, 'body', 16, rot=(-14, 0, 0))
    kk(c, 'body', 21, rot=(0, 0, 0))
    return _giant_hop(a, c, 21)


# ---------------------------------------------------------------- air methods (root rests at hover height)
def m_rocket_up(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, D, -hv + 0.4 * H), scale=0.6, rot=(-50, 0, 0))
    kk(c, 'root', 4, loc=(0, D, -hv + 0.5 * H), scale=0.8, rot=(-70, 0, 0))
    kk(c, 'root', 11, loc=(0, D * 0.3, 0.7 * H), scale=1.0, rot=(-40, 0, 0))
    kk(c, 'root', 16, loc=(0, 0, 0.15 * H), rot=(0, 0, 0))
    kk(c, 'root', 20, loc=(0, 0, 0))
    flap(a, c, 1, 18, 4, 50)
    return 20


def m_dive(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, D * 1.6, 3.0 * H + 2), rot=(55, 0, 0))
    kk(c, 'root', 11, loc=(0, D * 0.3, -hv * 0.6), rot=(40, 0, 0), ease='LINEAR')
    kk(c, 'root', 15, loc=(0, 0.05 * D, -hv * 0.3), rot=(-25, 0, 0))
    kk(c, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 0))
    for w in a.wings:
        s = -1 if w.endswith('L') else 1
        kk(c, w, 1, rot=(0, -s * 60, 0))
        kk(c, w, 11, rot=(0, -s * 60, 0))
        kk(c, w, 14, rot=(0, s * 15, 0))
        kk(c, w, 17, rot=(0, -s * 40, 0))
        kk(c, w, 21, rot=(0, 0, 0))
    return 21


def m_swoop_arc(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(-1.6 * H - 2, D, 0.5 * H), rot=(0, -40, -60))
    kk(c, 'root', 9, loc=(-0.8 * H - 1, D * 0.2, -hv * 0.35), rot=(0, -45, -40), ease='LINEAR')
    kk(c, 'root', 16, loc=(0.1 * H, -0.1 * H, 0.1 * H), rot=(0, 15, 10))
    kk(c, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 0))
    flap(a, c, 1, 18, 6, 40)
    return 20


def m_spiral_up(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    for f in range(1, 19):
        t = (f - 1) / 17.0
        ang = 720 * t
        rr = (0.6 * H + 0.6) * (1 - t)
        r = math.radians(ang)
        kk(c, 'root', f, loc=(math.sin(r) * rr, D * (1 - t) ** 2 + math.cos(r) * rr * 0.5, -hv * (1 - t) ** 1.5 + 0.3 * H * (1 - t)), rot=(0, 0, ang), ease='LINEAR')
    kk(c, 'root', 21, loc=(0, 0, 0), rot=(0, 0, 720))
    flap(a, c, 1, 19, 4, 45)
    return 21


def m_flutter_out(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    for i, f in enumerate(range(1, 20, 3)):
        t = (f - 1) / 18.0
        kk(c, 'root', f, loc=((0.25 if i % 2 else -0.25) * H * (1 - t), D * (1 - t), -hv * 0.5 * (1 - t) + (0.3 * H if i % 2 else -0.1 * H) * (1 - t)),
           rot=(0, 12 if i % 2 else -12, 0))
    kk(c, 'root', 21, loc=(0, 0, 0), rot=(0, 0, 0))
    flap(a, c, 1, 20, 2, 55)
    return 21


def m_loop_in(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, D, -hv * 0.4), rot=(0, 0, 0))
    kk(c, 'root', 5, loc=(0, D * 0.7, 0), rot=(-30, 0, 0))
    for f in range(6, 16):
        t = (f - 5) / 10.0
        ang = -30 - 330 * t
        r = math.radians(-360 * t)
        R = 0.6 * H + 0.4
        kk(c, 'root', f, loc=(0, D * 0.7 * (1 - t) - R * math.sin(-r) * 0.6, R - R * math.cos(r)), rot=(ang, 0, 0), ease='LINEAR')
    kk(c, 'root', 19, loc=(0, 0, 0), rot=(-360, 0, 0))
    flap(a, c, 1, 18, 4, 40)
    return 20


# ---------------------------------------------------------------- water methods (root rests at swim height)
def m_splash_up(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, D * 0.4, -hv - 1.1 * H), rot=(-60, 0, 0), scale=0.9)
    kk(c, 'root', 4, loc=(0, D * 0.4, -hv - 1.1 * H), rot=(-60, 0, 0))
    kk(c, 'root', 11, loc=(0, D * 0.15, 0.6 * H), rot=(-35, 0, 0), scale=1.0)
    kk(c, 'root', 16, loc=(0, 0, 0.12 * H), rot=(8, 0, 0))
    kk(c, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 0))
    a.fx_extra.append(('splash', 4, 0, D * 0.4))
    return 20


def m_breach_arc(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, D, -hv - 0.6 * H), rot=(-55, 0, 0))
    kk(c, 'root', 9, loc=(0, D * 0.5, 0.8 * H), rot=(0, 0, 0))
    kk(c, 'root', 15, loc=(0, 0.05 * D, -0.2 * H), rot=(35, 0, 0))
    kk(c, 'root', 20, loc=(0, 0, 0), rot=(0, 0, 0))
    a.fx_extra.append(('splash', 2, 0, D))
    for t in a.tail:
        for f, r in ((1, 20), (5, -20), (9, 20), (13, -20), (18, 0)):
            kk(c, t, f, rot=(0, 0, r))
    return 20


def m_bubble_rise(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    for i, f in enumerate(range(1, 20, 3)):
        t = (f - 1) / 18.0
        kk(c, 'root', f, loc=((0.12 if i % 2 else -0.12) * H, 0.2 * D * (1 - t), (-hv - 0.9 * H) * (1 - t) ** 1.3), rot=(0, 10 if i % 2 else -10, 0), scale=0.8 + 0.2 * t)
    kk(c, 'root', 21, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0)
    a.fx_extra.append(('bubbles', 1, 20, 0.2 * D))
    return 21


def m_whirlpool_rise(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, 0.2 * D, -hv - 1.0 * H), rot=(0, 0, 0), scale=0.7)
    kk(c, 'root', 16, loc=(0, 0, 0.2 * H), rot=(0, 0, 720), scale=1.0, ease='LINEAR')
    kk(c, 'root', 21, loc=(0, 0, 0), rot=(0, 0, 720))
    a.fx_extra.append(('vortex', 1, 16, 0.2 * D))
    a.fx_extra.append(('splash', 6, 0, 0.2 * D))
    return 21


def m_jet_burst(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, D, 0), scale=(0.85, 1.3, 0.85))
    kk(c, 'root', 9, loc=(0, -0.5 * H, 0), scale=(0.85, 1.3, 0.85), ease='LINEAR')
    kk(c, 'root', 13, loc=(0, -0.6 * H, 0), scale=(1.12, 0.86, 1.12))
    kk(c, 'root', 19, loc=(0, 0, 0), scale=1.0)
    a.fx_extra.append(('bubbles', 1, 10, D * 0.5))
    return 19


def m_geyser_ride(a, c):
    D, H, hv = a.bush_d, a.H, a.hover
    kk(c, 'root', 1, loc=(0, 0.15 * D, -hv - 1.0 * H))
    kk(c, 'root', 4, loc=(0, 0.15 * D, -hv - 1.0 * H))
    kk(c, 'root', 10, loc=(0, 0.1 * D, 0.9 * H), rot=(0, 0, 180))
    kk(c, 'root', 15, loc=(0, 0.05 * D, 1.0 * H), rot=(0, 0, 360))
    kk(c, 'root', 21, loc=(0, 0, 0), rot=(0, 0, 360))
    a.fx_extra.append(('pillar', 3, 18, 0.15 * D))
    a.fx_extra.append(('splash', 4, 0, 0.15 * D))
    return 21


# ---------------------------------------------------------------- gestures: keys from f0 over n frames
def _t(f0, n, x):
    return f0 + n * x


def g_sniff(a, c, f0, n):
    for x, r in ((0, (0, 0, 0)), (0.2, (12, 0, 0)), (0.36, (6, 0, 20)), (0.48, (10, 0, 18)), (0.64, (6, 0, -20)), (0.76, (10, 0, -18)), (1, (0, 0, 0))):
        kk(c, 'head', _t(f0, n, x), rot=r)
    for t in a.tail[:1]:
        for x, r in ((0, 0), (0.3, 30), (0.5, -30), (0.7, 0)):
            kk(c, t, _t(f0, n, x), rot=(0, 0, r))


def g_look_around(a, c, f0, n):
    for x, r in ((0, 0), (0.22, 38), (0.42, 38), (0.6, -38), (0.82, -38), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(0, 0, r))
    for x, r in ((0, 0), (0.3, 8), (0.7, -8), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(0, 0, r))


def g_bow(a, c, f0, n):
    for x, r in ((0, 0), (0.35, 22), (0.75, 22), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0))
        kk(c, 'head', _t(f0, n, x), rot=(r * 1.15, 0, 0))
    for e in a.ears:
        for x, r in ((0, 0), (0.4, 40), (0.75, 40), (1, 0)):
            kk(c, e, _t(f0, n, x), rot=(r, 0, 0))
    fl = [l for l in a.legs + a.arms if l.endswith('R')][:1]
    for l in fl:
        for x, r in ((0, (0, 0, 0)), (0.35, (-80, 0, -20)), (0.75, (-80, 0, -20)), (1, (0, 0, 0))):
            kk(c, l, _t(f0, n, x), rot=r)


def g_spin(a, c, f0, n):
    kk(c, 'root', f0, rot=rb(a, 0), loc=(0, 0, 0))
    kk(c, 'root', _t(f0, n, 0.85), rot=rb(a, 360), loc=(0, 0, 0))
    for x, r in ((0, 0), (0.2, 30), (0.7, 30), (0.95, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(0, 0, r))
        for t in a.tail[:1]:
            kk(c, t, _t(f0, n, x), rot=(0, 0, r * 1.2))
    a.spin_end = 360


def g_jump_joy(a, c, f0, n):
    H = a.H
    for i in range(2):
        b0 = f0 + n * 0.5 * i
        kk(c, 'root', b0, loc=(0, 0, 0))
        kk(c, 'root', b0 + n * 0.22, loc=(0, 0, 0.22 * H))
        kk(c, 'root', b0 + n * 0.44, loc=(0, 0, 0))
        kk(c, 'body', b0, scale=(1.08, 1.08, 0.88))
        kk(c, 'body', b0 + n * 0.22, scale=(0.95, 0.95, 1.08))
        kk(c, 'body', b0 + n * 0.44, scale=(1.06, 1.06, 0.92))
        for l in a.arms or a.legs[:2]:
            s = -1 if l.endswith('L') else 1
            kk(c, l, b0, rot=(0, 0, 0))
            kk(c, l, b0 + n * 0.22, rot=(-110, s * 25, 0))
            kk(c, l, b0 + n * 0.44, rot=(0, 0, 0))
    kk(c, 'body', f0 + n, scale=1.0)
    kk(c, 'root', f0 + n, loc=(0, 0, 0))


def g_shake_off(a, c, f0, n):
    m = max(4, int(n / 2))
    for i in range(m):
        amp = 18 * (1 if i % 2 == 0 else -1) * (1 - i / float(m + 1))
        kk(c, 'body', f0 + i * 2, rot=(0, amp * 0.4, amp))
        kk(c, 'head', f0 + i * 2 + 1, rot=(0, 0, -amp * 0.8))
    kk(c, 'body', f0 + n, rot=(0, 0, 0))
    kk(c, 'head', f0 + n, rot=(0, 0, 0))
    a.fx_extra.append(('drops', f0 + 2, 0, 0.0))


def g_stretch(a, c, f0, n):
    for x, r, s in ((0, 0, 1.0), (0.3, 16, (1.0, 1.12, 0.94)), (0.7, 16, (1.0, 1.12, 0.94)), (1, 0, 1.0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0), scale=s)
        kk(c, 'head', _t(f0, n, x), rot=(-r * 1.2, 0, 0))
    for l in a.legs:
        fr = ('f' in l[4:5]) or l[4:5] == '1'
        for x, r in ((0, 0), (0.3, -45 if fr else 12), (0.7, -45 if fr else 12), (1, 0)):
            kk(c, l, _t(f0, n, x), rot=(r, 0, 0))
    for t in a.tail:
        for x, r in ((0, 0), (0.35, 30), (0.7, 30), (1, 0)):
            kk(c, t, _t(f0, n, x), rot=(r, 0, 0))


def g_puff_up(a, c, f0, n):
    for x, s in ((0, 1.0), (0.3, (1.22, 1.14, 1.16)), (0.45, (1.16, 1.1, 1.12)), (0.6, (1.24, 1.15, 1.17)), (0.8, (1.2, 1.12, 1.14)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    for x, r in ((0, 0), (0.3, -16), (0.8, -16), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))


def g_wiggle(a, c, f0, n):
    for i, x in enumerate((0, 0.14, 0.28, 0.42, 0.56, 0.7, 0.84, 1.0)):
        sgn = 0 if i in (0, 7) else (1 if i % 2 else -1)
        kk(c, 'body', _t(f0, n, x), rot=(0, sgn * 10, sgn * 16), loc=(sgn * 0.04 * a.H, 0, 0))
        kk(c, 'head', _t(f0, n, x), rot=(0, -sgn * 12, -sgn * 10))
        for t in a.tail:
            kk(c, t, _t(f0, n, x), rot=(0, 0, -sgn * 30))


def g_roar(a, c, f0, n):
    for x, r, s in ((0, 0, 1.0), (0.2, 14, 1.0), (0.4, -28, 1.12), (0.5, -24, 1.08), (0.6, -28, 1.12), (0.8, -26, 1.1), (1, 0, 1.0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0), scale=s)
    for x, s, r in ((0, 1.0, 0), (0.2, (1.0, 1.0, 0.92), 6), (0.4, (1.12, 1.08, 1.1), -10), (0.8, (1.1, 1.06, 1.08), -10), (1, 1.0, 0)):
        kk(c, 'body', _t(f0, n, x), scale=s, rot=(r, 0, 0))
    for t in a.tail:
        for x, r in ((0, 0), (0.4, 30), (0.8, 30), (1, 0)):
            kk(c, t, _t(f0, n, x), rot=(r, 0, 0))
    a.fx_extra.append(('roar', int(_t(f0, n, 0.4)), 0, 0.0))


def g_rear_up(a, c, f0, n):
    H = a.H
    for x, r, z in ((0, 0, 0), (0.3, -38, 0.1), (0.5, -34, 0.08), (0.7, -38, 0.1), (1, 0, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0), loc=(0, 0, z * H))
        kk(c, 'head', _t(f0, n, x), rot=(-r * 0.6, 0, 0))
    for l in a.legs:
        fr = ('f' in l[4:5]) or l[4:5] == '1'
        s = -1 if l.endswith('L') else 1
        for i, x in enumerate((0, 0.3, 0.5, 0.7, 1)):
            rr = 0 if i in (0, 4) else (((-70 if i % 2 else -30) * (1 if s > 0 else 0.6)) if fr else 34)
            kk(c, l, _t(f0, n, x), rot=(rr, 0, 0))
    for w in a.wings:
        s = -1 if w.endswith('L') else 1
        for x, r in ((0, 0), (0.3, 50), (0.5, 20), (0.7, 50), (1, 0)):
            kk(c, w, _t(f0, n, x), rot=(0, -s * r, 0))


def g_stomp_hoof(a, c, f0, n):
    cand = [x for x in ('leg_fR', 'leg_R', 'leg_1R') if x in a.segs] + a.arms + a.legs + ['body']
    l = cand[0]
    for i, x in enumerate((0, 0.18, 0.3, 0.48, 0.6, 0.78, 0.9, 1.0)):
        up = i in (1, 3, 5)
        kk(c, l, _t(f0, n, x), rot=(-55 if up else 0, 0, 0))
        if i in (2, 4, 6):
            a.fx_extra.append(('stomp_small', int(_t(f0, n, x)), 0, 0.0))
    for x, r in ((0, 0), (0.2, 12), (0.9, 12), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))
    for x, r in ((0, 0), (0.2, 5), (0.9, 5), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0))


def g_tail_wave(a, c, f0, n):
    for i, t in enumerate(a.tail or ['body']):
        for x, r in ((0, 0), (0.2, 30), (0.4, -30), (0.6, 26), (0.8, -20), (1, 0)):
            if t == 'body':
                kk(c, t, _t(f0, n, x), rot=(0, r * 0.4, 0))
            else:
                kk(c, t, min(f0 + n, _t(f0, n, x) + i), rot=(8 if r else 0, 0, r))
    for x, r in ((0, 0), (0.4, -12), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(0, 0, r))


def g_head_toss(a, c, f0, n):
    for x, r in ((0, (0, 0, 0)), (0.2, (16, 0, 0)), (0.4, (-30, 0, 0)), (0.55, (-24, 0, 20)), (0.7, (-24, 0, -20)), (0.85, (-10, 0, 10)), (1, (0, 0, 0))):
        kk(c, 'head', _t(f0, n, x), rot=r)
    for x, r in ((0, 0), (0.4, -8), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0))
    for e in a.ears:
        for x, r in ((0, 0), (0.45, 30), (0.7, -20), (1, 0)):
            kk(c, e, _t(f0, n, x), rot=(r, 0, 0))


def g_ear_wiggle(a, c, f0, n):
    es = a.ears or ['head']
    for j, e in enumerate(es):
        s = -1 if e.endswith('L') else 1
        for i, x in enumerate((0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0)):
            on_ = ((i % 2 == 1) if j % 2 == 0 else (i % 2 == 0)) and 0 < i < 7
            if e == 'head':
                kk(c, e, _t(f0, n, x), rot=(0, (12 if on_ else -12) if 0 < i < 7 else 0, 0))
            else:
                kk(c, e, _t(f0, n, x), rot=((30, s * 22, 0) if on_ else (0, 0, 0)))
    for x, r in ((0, 0), (0.5, 10), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(0, r, 0)) if a.ears else None


def g_yawn(a, c, f0, n):
    for x, r, s in ((0, 0, 1.0), (0.3, -26, 1.08), (0.6, -26, 1.1), (0.8, 18, 1.0), (0.9, 12, 1.0), (1, 0, 1.0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0), scale=s)
    for x, s in ((0, 1.0), (0.4, (1.08, 1.04, 1.06)), (0.8, (1.0, 1.0, 0.95)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    for e in ('eye_L', 'eye_R'):
        for x, s in ((0, 1.0), (0.25, (1, 1, 0.12)), (0.7, (1, 1, 0.12)), (0.85, 1.0)):
            kk(c, e, _t(f0, n, x), scale=s)
    a.no_blink = True


def g_wave_paw(a, c, f0, n):
    arm = ([l for l in a.arms if l.endswith('R')] or [l for l in a.legs if l.endswith('R')] or a.wings or ['body'])[0]
    for i, x in enumerate((0, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0)):
        r = (0, 0, 0) if i in (0, 6) else (-150, 0, -30 if i % 2 else 25)
        kk(c, arm, _t(f0, n, x), rot=r)
    for x, r in ((0, 0), (0.3, -10), (0.8, -10), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(0, r, 0))
    for x, r in ((0, 0), (0.3, 6), (0.8, 6), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(0, r, 0))


def g_clap(a, c, f0, n):
    arms = (a.arms or a.legs[:2])[:2]
    for i, x in enumerate((0, 0.2, 0.32, 0.44, 0.56, 0.68, 0.8, 1.0)):
        for l in arms:
            s = -1 if l.endswith('L') else 1
            r = (0, 0, 0) if i in (0, 7) else ((-85, 0, -s * 32) if i % 2 == 0 else (-85, 0, s * 12))
            kk(c, l, _t(f0, n, x), rot=r)
        if i in (2, 4, 6):
            a.fx_extra.append(('spark_small', int(_t(f0, n, x)), 0, 0.0))
    for x, s in ((0, 1.0), (0.5, (1.03, 1.03, 1.06)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)


def g_chest_beat(a, c, f0, n):
    arms = (a.arms or a.legs[:2])[:2]
    for i, x in enumerate((0, 0.18, 0.3, 0.42, 0.54, 0.66, 0.78, 1.0)):
        for j, l in enumerate(arms):
            s = -1 if l.endswith('L') else 1
            hit = (i % 2 == j % 2)
            r = (0, 0, 0) if i in (0, 7) else ((-60, 0, -s * 55) if hit else (-95, 0, -s * 15))
            kk(c, l, _t(f0, n, x), rot=r)
    for x, r, s in ((0, 0, 1.0), (0.2, -14, (1.1, 1.06, 1.06)), (0.8, -14, (1.1, 1.06, 1.06)), (1, 0, 1.0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0), scale=s)
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))


def g_flex(a, c, f0, n):
    arms = (a.arms or a.legs[:2])[:2]
    for x, up in ((0, 0), (0.25, 1), (0.45, 0.8), (0.6, 1), (0.82, 1), (1, 0)):
        for l in arms:
            s = -1 if l.endswith('L') else 1
            if l.startswith('claw'):
                kk(c, l, _t(f0, n, x), rot=(0, -s * 60 * up, 0), scale=1 + 0.2 * up)
            else:
                kk(c, l, _t(f0, n, x), rot=(-20 * up, -s * 140 * up, 0), scale=1 + 0.15 * up)
    for x, s in ((0, 1.0), (0.25, (1.12, 1.04, 1.04)), (0.82, (1.12, 1.04, 1.04)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    for x, r in ((0, 0), (0.25, -10), (0.82, -10), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))


def g_wing_flap(a, c, f0, n):
    for i, x in enumerate((0, 0.14, 0.28, 0.42, 0.56, 0.7, 0.84, 1.0)):
        for w in a.wings:
            s = -1 if w.endswith('L') else 1
            r = 0 if i in (0, 7) else (65 if i % 2 else -25)
            kk(c, w, _t(f0, n, x), rot=(0, -s * r, 0))
        kk(c, 'body', _t(f0, n, x), loc=(0, 0, 0 if i in (0, 7) else (0.05 * a.H if i % 2 == 0 else 0)))
    for x, r in ((0, 0), (0.3, -12), (0.8, -12), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))
    a.fx_extra.append(('gust', int(_t(f0, n, 0.28)), 0, 0.0))


def g_wing_puff(a, c, f0, n):
    for x, s in ((0, 1.0), (0.3, (1.18, 1.1, 1.12)), (0.8, (1.18, 1.1, 1.12)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    for i, x in enumerate((0, 0.25, 0.36, 0.47, 0.58, 0.69, 0.8, 1.0)):
        for w in a.wings:
            s = -1 if w.endswith('L') else 1
            r = 0 if i in (0, 7) else (70 if i % 2 else 28)
            kk(c, w, _t(f0, n, x), rot=(0, -s * r, 0))
    for x, r in ((0, 0), (0.3, -20), (0.8, -20), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))
        for t in a.tail:
            kk(c, t, _t(f0, n, x), rot=(-r, 0, 0))


def g_preen(a, c, f0, n):
    for x, r in ((0, (0, 0, 0)), (0.25, (20, 30, 60)), (0.4, (28, 30, 66)), (0.55, (18, 30, 58)), (0.7, (28, 30, 66)), (1, (0, 0, 0))):
        kk(c, 'head', _t(f0, n, x), rot=r)
    w = [w for w in a.wings if w.endswith('L')][:1]
    for ww in w:
        for x, r in ((0, 0), (0.25, 40), (0.75, 40), (1, 0)):
            kk(c, ww, _t(f0, n, x), rot=(0, r, 0))
    for x, r in ((0, 0), (0.25, -6), (0.75, -6), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(0, r, 0))


def g_coil(a, c, f0, n):
    ch = getattr(a, 'neck', []) or []
    for i, s in enumerate(ch):
        for x, r in ((0, 0), (0.35, 26), (0.7, 26), (1, 0)):
            kk(c, s, _t(f0, n, x), rot=(r, 0, 8 * (1 if i % 2 else -1) if r else 0))
    for i, t in enumerate(a.tail):
        for x, r in ((0, 0), (0.35, 50), (0.7, 50), (1, 0)):
            kk(c, t, _t(f0, n, x), rot=(8 if r else 0, 0, r))
    for w in a.wings:
        s = -1 if w.endswith('L') else 1
        for x, r in ((0, 0), (0.35, -40), (0.7, -40), (1, 0)):
            kk(c, w, _t(f0, n, x), rot=(0, -s * r, 0))
    for x, r, s in ((0, 0, 1.0), (0.35, 20, (1.06, 1.06, 0.94)), (0.7, 20, (1.06, 1.06, 0.94)), (1, 0, 1.0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0))
        kk(c, 'body', _t(f0, n, x), scale=s)
    kk(c, 'root', f0, rot=rb(a, 0))
    kk(c, 'root', _t(f0, n, 0.35), rot=rb(a, 40))
    kk(c, 'root', _t(f0, n, 0.7), rot=rb(a, 40))
    kk(c, 'root', f0 + n, rot=rb(a, 0))


def g_claw_snap(a, c, f0, n):
    arms = (a.arms or a.legs[:2])[:2]
    for i, x in enumerate((0, 0.18, 0.3, 0.42, 0.54, 0.66, 0.78, 1.0)):
        for j, l in enumerate(arms):
            s = -1 if l.endswith('L') else 1
            if i in (0, 7):
                kk(c, l, _t(f0, n, x), rot=(0, 0, 0), scale=1.0)
            else:
                op = (i % 2 == 0)
                kk(c, l, _t(f0, n, x), rot=(-30, -s * 35, s * (25 if op else 0)), scale=1.18 if op else 1.0)
        if i in (2, 4, 6):
            a.fx_extra.append(('spark_small', int(_t(f0, n, x)), 0, 0.0))
    for x, r in ((0, 0), (0.3, -10), (0.8, -10), (1, 0)):
        kk(c, 'body', _t(f0, n, x), rot=(r, 0, 0))


def g_antenna_twitch(a, c, f0, n):
    for j, e in enumerate(a.ears or ['head']):
        s = -1 if e.endswith('L') else 1
        for i, x in enumerate((0, 0.14, 0.28, 0.42, 0.56, 0.7, 0.84, 1.0)):
            r = 0 if i in (0, 7) else (35 if (i + j) % 2 else -20)
            kk(c, e, _t(f0, n, x), rot=(r, s * r * 0.5, 0))
    for x, r in ((0, 0), (0.3, 10), (0.6, -10), (1, 0)):
        kk(c, 'head', _t(f0, n, x), rot=(0, 0, r))
        kk(c, 'body', _t(f0, n, x), rot=(0, r * 0.6, 0))


def g_fin_flap(a, c, f0, n):
    for i, x in enumerate((0, 0.14, 0.28, 0.42, 0.56, 0.7, 0.84, 1.0)):
        for w in a.wings:
            s = -1 if w.endswith('L') else 1
            r = 0 if i in (0, 7) else (55 if i % 2 else -30)
            kk(c, w, _t(f0, n, x), rot=(0, -s * r, 0))
        kk(c, 'body', _t(f0, n, x), rot=(0, 0 if i in (0, 7) else (8 if i % 2 else -8), 0))
    for t in a.tail:
        for x, r in ((0, 0), (0.25, 25), (0.5, -25), (0.75, 25), (1, 0)):
            kk(c, t, _t(f0, n, x), rot=(0, 0, r))


def g_bubble_blow(a, c, f0, n):
    for x, r, s in ((0, 0, 1.0), (0.2, 10, 1.0), (0.4, -16, 1.1), (0.6, -16, 1.04), (0.8, -16, 1.1), (1, 0, 1.0)):
        kk(c, 'head', _t(f0, n, x), rot=(r, 0, 0), scale=s)
    for x, s in ((0, 1.0), (0.2, (1.1, 1.06, 1.1)), (0.5, (0.96, 1.0, 0.96)), (0.7, (1.08, 1.04, 1.08)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    a.fx_extra.append(('bubbles_mouth', int(_t(f0, n, 0.35)), int(n * 0.6), 0.0))


def g_pulse(a, c, f0, n):
    for i, x in enumerate((0, 0.16, 0.33, 0.5, 0.66, 0.83, 1.0)):
        s = 1.0 if i in (0, 6) else ((1.18, 1.18, 0.86) if i % 2 else (0.9, 0.9, 1.16))
        kk(c, 'body', _t(f0, n, x), scale=s)
    for l in a.arms:
        for x, r in ((0, 0), (0.33, 30), (0.66, -20), (1, 0)):
            kk(c, l, _t(f0, n, x), rot=(r, 0, 0))


def g_open_shut(a, c, f0, n):
    lid = 'lid' if has(a, 'lid') else 'head'
    for i, x in enumerate((0, 0.2, 0.4, 0.5, 0.7, 0.85, 1.0)):
        op = i in (1, 2, 4)
        kk(c, lid, _t(f0, n, x), rot=(-45 if (op and lid == 'lid') else (-14 if op else 0), 0, 0))
    for x, s in ((0, 1.0), (0.2, (1.06, 1.06, 1.08)), (0.5, (1.0, 1.0, 0.94)), (0.7, (1.06, 1.06, 1.08)), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    a.fx_extra.append(('spark_small', int(_t(f0, n, 0.2)), 0, 0.0))


def g_sparkle_burst(a, c, f0, n):
    for x, s in ((0, 1.0), (0.25, (0.9, 0.9, 0.9)), (0.4, (1.22, 1.22, 1.22)), (0.6, 1.0), (1, 1.0)):
        kk(c, 'body', _t(f0, n, x), scale=s)
    for w in a.wings:
        s = -1 if w.endswith('L') else 1
        for x, r in ((0, 0), (0.25, -20), (0.4, 70), (0.7, 30), (1, 0)):
            kk(c, w, _t(f0, n, x), rot=(0, -s * r, 0))
    kk(c, 'root', f0, rot=rb(a, 0))
    kk(c, 'root', _t(f0, n, 0.9), rot=rb(a, 360))
    a.spin_end = 360
    a.fx_extra.append(('sparkle', int(_t(f0, n, 0.4)), 0, 0.0))


METHODS = {k[2:]: v for k, v in list(globals().items()) if k.startswith('m_')}
GESTURES = {k[2:]: v for k, v in list(globals().items()) if k.startswith('g_')}


# ---------------------------------------------------------------- reveal / idle / fx
def reveal(a):
    c = 'Reveal'
    clip(c, 45)
    a.fx_extra, a.hang, a.spin_end, a.no_blink = [], None, 0, False
    a.rbase = (0, 0, 0)
    T = METHODS[a.method](a, c)
    rk = [d for d in G.keys[c].get('root', []) if d['rot'] is not None]
    if rk:
        a.rbase = max(rk, key=lambda d: d['f'])['rot']
    epic = a.rarity >= 5
    if epic and a.hang is None:
        # flyers / swimmers of rarity 5-6: hold a show pose in the air before the gesture
        kk(c, 'root', T, loc=(0, 0, 0))
        kk(c, 'root', T + 4, loc=(0, 0, 0.12 * a.H))
        kk(c, 'root', T + 10, loc=(0, 0, 0))
        pose_epic(a, c, T + 2, T + 7)
        a.hang = (T + 1, T + 9)
        T += 11
    n = max(9, min(20, 44 - T))
    L_ = T + n + 1
    G.clips[c] = L_
    GESTURES[a.gesture](a, c, T, n)
    for fn in getattr(a, 'extra_reveal', []):
        fn(c, T, n)
    # everything returns to rest on the last frame
    kk(c, 'root', L_, loc=(0, 0, 0), scale=1.0)
    # safety net: every segment is back at rest on the last frame
    for s, keys in list(G.keys[c].items()):
        if s == 'root' or s.startswith('fxs_'):
            continue
        for fld, restv in (('loc', (0, 0, 0)), ('rot', (0, 0, 0)), ('scale', (1.0, 1.0, 1.0))):
            ks = [d for d in keys if d[fld] is not None]
            if not ks:
                continue
            last = max(ks, key=lambda d: d['f'])
            if fld == 'rot':
                # a whole number of turns is the rest pose too: never unwind it
                if all(abs(u / 360.0 - round(u / 360.0)) < 1e-4 for u in last[fld]):
                    continue
                kk(c, s, L_, rot=tuple(360.0 * round(u / 360.0) for u in last[fld]))
            elif any(abs(u - v) > 1e-4 for u, v in zip(last[fld], restv)):
                kk(c, s, L_, **{fld: restv})
    if not a.no_blink and has(a, 'eye_L'):
        blink(c, (min(L_ - 3, T + int(n * 0.5)),))
    # permanent FX segments fade in near the end
    for s in ('fxs_aura', 'fxs_motes', 'fxs_sparks'):
        if has(a, s):
            kk(c, s, 1, scale=0.0)
            kk(c, s, T - 3, scale=0.0)
            kk(c, s, T + 3, scale=1.25)
            kk(c, s, L_, scale=1.0)
    for s in a.glow:
        kk(c, s, T, scale=1.0)
        kk(c, s, T + n * 0.5, scale=1.05)
        kk(c, s, L_, scale=1.0)
    a.T, a.n, a.reveal_len = T, n, L_
    return L_


def idle(a):
    c = 'Idle'
    n = min(60, 40 + 4 * a.rarity)
    clip(c, n)
    kk(c, 'body', 1, scale=1.0)
    kk(c, 'body', n // 2, scale=(1.03, 1.03, 1.04))
    kk(c, 'body', n, scale=1.0)
    for x, r in ((1, 0), (int(n * 0.3), 6), (int(n * 0.62), 0), (n, 0)):
        kk(c, 'head', x, rot=(0, r, 0))
    if has(a, 'eye_L'):
        blink(c, (int(n * 0.42),) if n < 56 else (int(n * 0.3), int(n * 0.78)))
    if a.ears:
        e = a.ears[-1]
        for x, r in ((1, 0), (int(n * 0.66), 0), (int(n * 0.66) + 3, 16), (int(n * 0.66) + 6, 0), (n, 0)):
            kk(c, e, x, rot=(r, 0, 0))
    for i, t in enumerate(a.tail):
        for x, r in ((1, 0), (int(n * 0.25), 12), (int(n * 0.5), 0), (int(n * 0.75), -12), (n, 0)):
            kk(c, t, x, rot=(0, 0, r))
    if a.kind in ('air', 'water'):
        kk(c, 'root', 1, loc=(0, 0, 0))
        kk(c, 'root', n // 2, loc=(0, 0, 0.08 * a.H))
        kk(c, 'root', n, loc=(0, 0, 0))
        per = n // 4 if a.kind == 'air' else n // 2
        for i in range(0, n + 1, max(1, per // 2)):
            up = (i // max(1, per // 2)) % 2 == 0
            f = min(n, 1 + i)
            for w in a.wings:
                s = -1 if w.endswith('L') else 1
                kk(c, w, f, rot=(0, -s * (28 if up else -14), 0))
        for w in a.wings:
            s = -1 if w.endswith('L') else 1
            kk(c, w, n, rot=(0, -s * 28, 0))
    for s in a.glow:
        pulse(c, s, 16 + 2 * (a.rarity % 3), 0.035)
    for i, o in enumerate(a.orbits):
        d = -1 if i % 2 else 1
        kk(c, o, 1, rot=(0, 0, 0), loc=(0, 0, 0))
        kk(c, o, n // 2, rot=(0, 0, 180 * d), loc=(0, 0, 0.06 * a.H), ease='LINEAR')
        kk(c, o, n, rot=(0, 0, 360 * d), loc=(0, 0, 0), ease='LINEAR')
    if has(a, 'fxs_aura'):
        kk(c, 'fxs_aura', 1, rot=(0, 0, 0), ease='LINEAR')
        kk(c, 'fxs_aura', n, rot=(0, 0, -180), ease='LINEAR')
    for s in ('fxs_motes', 'fxs_sparks'):
        if has(a, s):
            kk(c, s, 1, loc=(0, 0, 0))
            kk(c, s, n // 2, loc=(0, 0, 0.1 * a.H))
            kk(c, s, n, loc=(0, 0, 0))
    for fn in a.extra_idle:
        fn(c, n)
    a.idle_len = n


def _bit(name, size, mat, bev=0.02):
    return blk(name, (size, size, size * 0.25), mat, (0, 0, 0), bev=min(bev, size * 0.1))


def fx_build(a):
    """reveal FX objects in the animal's FX collection. positions relative to the ground point of the final spot"""
    fx(True)
    th = THEME
    base = Vector(a.place)
    D, H, T, n = a.bush_d, a.H, a.T, a.n
    S = max(0.6, min(2.2, H / 3.0))
    rnd = _random.Random(len(a.id) * 131 + a.rarity)
    notes = a.fx_notes
    bits = [studs('%s_bit%d' % (a.id, i), h) for i, h in enumerate(th['bits'])]
    dust = ghost('%s_dust' % a.id, th['dust'], 1.1, 0.85, 1.2)
    glowc = th['glow']
    gm = neon('%s_fxglow' % a.id, glowc, 3.4)
    gm['hex'] = glowc
    # 1. bush burst
    nb = 4 + 2 * a.rarity
    for i in range(nb):
        o = _bit('bush_bit_%d' % i, 0.24 * S, bits[i % len(bits)])
        p0 = base + Vector((rnd.uniform(-0.8, 0.8) * S, D, rnd.uniform(0.5, 1.0) * a.bush_h * 0.6))
        p1 = p0 + Vector((rnd.uniform(-1.6, 1.6) * S, rnd.uniform(-2.2, -0.4) * S, rnd.uniform(0.5, 1.6) * S))
        f0 = 2 + i % 4
        fxkey(o, 1, loc=p0, scale=0)
        fxkey(o, f0, loc=p0, scale=0)
        fxkey(o, f0 + 2, loc=p0, scale=1)
        fxkey(o, f0 + 12, loc=p1, rot=(rnd.uniform(0, 360), 180, 90))
        fxkey(o, f0 + 26, loc=(p1.x, p1.y, base.z + 0.05), rot=(rnd.uniform(0, 360), 360, 200), scale=0.0)
    notes.append('кадр 2–6: %d частиц куста (%s, %s) вылетают вперёд — ParticleEmitter Emit(%d), размер %.2f, жизнь 0.8 с'
                 % (nb, th['bit_name'], ' / '.join(th['bits']), nb, 0.24 * S))
    # 2. arrival
    tl = T - 2
    if a.kind == 'ground' or a.kind == 'shore':
        for i in range(6):
            ang = math.radians(i * 60 + 15)
            o = blk('land_dust_%d' % i, (0.3 * S, 0.3 * S, 0.3 * S), dust, (0, 0, 0), bev=0.06 * S)
            p0 = base + Vector((0, 0, 0.15 * S))
            p1 = p0 + Vector((math.cos(ang) * 0.9 * S * 1.4, math.sin(ang) * 0.9 * S * 1.4, 0.25 * S))
            fxkey(o, 1, loc=p0, scale=0, alpha=1)
            fxkey(o, tl, loc=p0, scale=0.2, alpha=1)
            fxkey(o, tl + 8, loc=p1, scale=1.4, alpha=0.7, rot=(20, 30, 0))
            fxkey(o, tl + 16, loc=p1 + Vector((0, 0, 0.3 * S)), scale=1.8, alpha=0)
        notes.append('кадр %d: 6 кубиков пыли %s кольцом от ног — ParticleEmitter Emit(6), размер %.2f → %.2f' % (tl, th['dust'], 0.3 * S, 0.55 * S))
    else:
        o = torus('arrive_ring', 0.5 * S, 0.05 * S, ghost('%s_ring' % a.id, th['splash'], 1.6, 0.9, 0.8), 16, 4)
        p0 = base + Vector((0, 0, a.hover))
        fxkey(o, 1, loc=p0, scale=0, alpha=1)
        fxkey(o, tl, scale=0.4, alpha=1)
        fxkey(o, tl + 10, scale=3.0, alpha=0)
        notes.append('кадр %d: кольцо %s вокруг зверя на высоте зависания, растёт ×3 и гаснет — Neon-кольцо (Size, Transparency)' % (tl, th['splash']))
    # 3. rarity 3-4: element swirl during the gesture
    if a.rarity in (3, 4):
        m_ = gm if a.rarity == 4 else bits[0]
        for i in range(8):
            o = _bit('swirl_%d' % i, 0.2 * S, m_)
            ang = math.radians(i * 45)
            zc = a.hover + H * 0.5
            fxkey(o, 1, loc=base, scale=0)
            fxkey(o, T, loc=base + Vector((math.cos(ang) * H * 0.5, math.sin(ang) * H * 0.5, zc - H * 0.3)), scale=0)
            fxkey(o, T + 3, loc=base + Vector((math.cos(ang + 0.8) * H * 0.6, math.sin(ang + 0.8) * H * 0.6, zc)), scale=1, rot=(0, 90, 60))
            fxkey(o, T + n - 2, loc=base + Vector((math.cos(ang + 3.0) * H * 0.75, math.sin(ang + 3.0) * H * 0.75, zc + H * 0.4)), scale=0.8, rot=(0, 300, 200))
            fxkey(o, T + n + 1, scale=0)
        notes.append('кадры %d–%d: вихрь из 8 частиц (%s) вокруг зверя — ParticleEmitter на кольце, скорость по касательной'
                     % (T, T + n, 'Neon ' + glowc if a.rarity == 4 else th['bits'][0]))
    # 4. rarity 5-6: flash, shockwave, light rings, element burst
    if a.rarity >= 5:
        rc = '#ffd21a' if a.rarity == 5 else '#ff2a2a'
        rm = neon('%s_rar' % a.id, rc, 3.6)
        rm['hex'] = rc
        fm = neon('%s_flash' % a.id, '#fff6b0', 4.0)
        h0, h1 = a.hang
        hz = (max(1.6, min(0.75 * H, 5.0)) if a.kind in ('ground', 'shore') and H < 8 else 0.2 * H) + a.hover + H * 0.5
        hp = base + Vector((0, 0.1, hz))
        core = blk('flash_core', (0.6 * S, 0.6 * S, 0.6 * S), fm, (0, 0, 0), bev=0.1 * S)
        cpos = base + Vector((0, D, a.bush_h * 0.4))
        fxkey(core, 1, loc=cpos, scale=0, alpha=1, rot=(0, 0, 0))
        fxkey(core, 3, scale=0.6, alpha=1)
        fxkey(core, 6, scale=2.6, alpha=0.9, rot=(45, 45, 0))
        fxkey(core, 11, scale=3.2, alpha=0)
        wave = torus('shockwave', 0.6 * S, 0.07 * S, rm, 16, 4)
        fxkey(wave, 1, loc=base + Vector((0, 0.1, 0.1)), scale=0, alpha=1)
        fxkey(wave, h0, scale=0.3, alpha=1)
        fxkey(wave, h0 + 12, scale=5.0, alpha=0)
        for i, rx in enumerate((70, 110)):
            rg = torus('light_ring_%d' % i, H * 0.62, 0.05 * S, gm if i else fm, 20, 4)
            f0 = h0 + i * 2
            fxkey(rg, 1, loc=hp, scale=0, alpha=1, rot=(rx, 0, 0))
            fxkey(rg, f0, scale=0.2, alpha=1, rot=(rx, 0, 0))
            fxkey(rg, f0 + 6, scale=1.0, alpha=1, rot=(rx, 0, 120))
            fxkey(rg, h1, scale=1.25, alpha=0.8, rot=(rx, 0, 300))
            fxkey(rg, h1 + 5, scale=1.6, alpha=0)
        for i in range(12):
            ang = math.radians(i * 30)
            s_ = star('burst_%d' % i, 0.16 * S, 0.06 * S, 4, 0.05 * S, gm)
            p1 = hp + Vector((math.cos(ang) * H * 0.9, math.sin(ang) * H * 0.4, math.sin(ang * 2) * H * 0.35 + math.cos(ang) * 0.3))
            fxkey(s_, 1, loc=hp, scale=0, alpha=1)
            fxkey(s_, h0, loc=hp, scale=0.4, alpha=1)
            fxkey(s_, h0 + 9, loc=p1, scale=1.0, alpha=1, rot=(0, 0, 180))
            fxkey(s_, h0 + 20, loc=p1 - Vector((0, 0, 0.3 * H)), scale=0.0, alpha=0, rot=(0, 0, 360))
        notes.append('кадры 1–11: вспышка в кусте — Neon-ядро #fff6b0 + PointLight %s, Brightness 0 → 12 → 0, Range %d' % (rc, int(8 + 2 * H)))
        notes.append('кадр %d: ударная волна по земле — Neon-кольцо %s, радиус %.1f → %.1f за 12 кадров' % (h0, rc, 0.6 * S, 3.0 * S))
        notes.append('кадры %d–%d: зверь висит в воздухе в позе, вокруг вращаются 2 кольца света (радиус %.1f), из центра вылетают 12 частиц стихии %s — Neon-кольца + ParticleEmitter Emit(12)'
                     % (h0, h1, H * 0.62, glowc))
    # 5. method / gesture specific
    for kind, f0, f1, y in a.fx_extra:
        if kind == 'mound':
            for i in range(5):
                o = blk('mound_%d' % i, (0.6 * S, 0.6 * S, 0.5 * S), studs('%s_dirt' % a.id, th['dust']), (0, 0, 0), bev=0.08 * S)
                ang = math.radians(i * 72)
                q = base + Vector((math.cos(ang) * 0.5 * S * (i > 0), y + math.sin(ang) * 0.5 * S * (i > 0), 0.1 * S))
                fxkey(o, 1, loc=q - Vector((0, 0, 0.4 * S)), scale=0.2)
                fxkey(o, max(2, f0 + 3 + i % 2), loc=q + Vector((0, 0, 0.15 * S * (i == 0))), scale=1.0 + 0.5 * (i == 0))
                fxkey(o, f1, loc=q + Vector((0, 0, 0.2 * S)), scale=1.2)
                fxkey(o, f1 + 4, loc=q + Vector((math.cos(ang) * S, math.sin(ang) * S, 0.5 * S)), scale=0.8, rot=(40, 60, 0))
                fxkey(o, f1 + 10, loc=q + Vector((math.cos(ang) * 1.6 * S, math.sin(ang) * 1.6 * S, 0.0)), scale=0.0)
            notes.append('кадры %d–%d: кочка из 5 блоков %s растёт и разлетается — части с твином Size и CFrame' % (f0, f1 + 10, th['dust']))
        elif kind in ('stomp', 'stomp_small'):
            o = torus('stomp_%d' % f0, 0.5 * S, 0.05 * S, dust, 4, 4)
            sc = 1.0 if kind == 'stomp' else 0.5
            fxkey(o, 1, loc=base + Vector((0, y, 0.05)), scale=0, alpha=1, rot=(0, 0, 45))
            fxkey(o, f0, scale=0.3 * sc, alpha=1)
            fxkey(o, f0 + 7, scale=2.4 * sc, alpha=0)
            if kind == 'stomp':
                notes.append('кадр %d: удар о землю — кольцо пыли + тряска камеры %.2f stud на 4 кадра' % (f0, 0.04 * S))
        elif kind == 'land_ring':
            rc = '#ffd21a' if a.rarity <= 5 else '#ff2a2a'
            o = torus('land_ring', 0.7 * S, 0.06 * S, neon('%s_land' % a.id, rc, 3.4), 16, 4)
            fxkey(o, 1, loc=base + Vector((0, 0, 0.08)), scale=0, alpha=1)
            fxkey(o, f0 - 1, scale=0.3, alpha=1)
            fxkey(o, f0 + 10, scale=3.2, alpha=0)
            notes.append('кадр %d: приземление — Neon-кольцо %s расходится до радиуса %.1f' % (f0, rc, 2.2 * S))
        elif kind == 'shadow':
            o = blk('shadow', (1.0, 1.0, 0.04), smooth('%s_shadow' % a.id, '#151018', 0.9), (0, 0, 0), bev=0.01)
            fxkey(o, 1, loc=base + Vector((0, y, 0.03)), scale=(0.1, 0.1, 1), alpha=1)
            fxkey(o, f1 - 4, scale=(H * 0.9, H * 0.9, 1))
            fxkey(o, f1 + 6, scale=(H * 1.0, H * 1.0, 1))
            fxkey(o, f1 + 10, scale=(0.0, 0.0, 1))
            notes.append('кадры 1–%d: тень на земле растёт до %.1f studs — тёмная плоская часть (твин Size)' % (f1, H * 0.9))
        elif kind == 'quake':
            notes.append('кадры %d–%d: земля трясётся — тряска камеры %.2f stud, 15 Гц' % (f0, f1, 0.05 * S))
            for i in range(6):
                o = blk('quake_rock_%d' % i, (0.3 * S, 0.3 * S, 0.3 * S), studs('%s_dirt' % a.id, th['dust']), (0, 0, 0), bev=0.05 * S)
                ang = math.radians(i * 60 + 20)
                q = base + Vector((math.cos(ang) * H * 0.5, math.sin(ang) * H * 0.4, 0.1))
                ff = f0 + i * 2
                fxkey(o, 1, loc=q, scale=0)
                fxkey(o, ff, loc=q, scale=1)
                fxkey(o, ff + 4, loc=q + Vector((0, 0, 0.5 * S)), rot=(40, 30, 0))
                fxkey(o, ff + 8, loc=q, scale=0.0, rot=(90, 60, 0))
        elif kind == 'comet':
            for i in range(6):
                o = _bit('comet_%d' % i, 0.3 * S, gm)
                p0 = base + Vector((0, D * 1.2, 5.0 * max(H, 2.0) + H))
                p1 = base + Vector((0, 0.1 * D, H))
                t = i / 6.0
                fxkey(o, 1, loc=p0, scale=0, alpha=1)
                fxkey(o, f0 + i, loc=p0.lerp(p1, t), scale=1.2, alpha=1)
                fxkey(o, f0 + i + 8, loc=p0.lerp(p1, t) + Vector((0, 0.4, 0.6)), scale=0.0, alpha=0, rot=(90, 90, 0))
            notes.append('кадры 1–9: хвост кометы из частиц %s — ParticleEmitter на звере, Rate 30, жизнь 0.3 с' % glowc)
        elif kind == 'pillar':
            o = blk('pillar', (1.0, 1.0, 1.0), gm, (0, 0, 0), bev=0.05)
            hgt = H * 2.2 + a.hover
            fxkey(o, 1, loc=base + Vector((0, y, hgt / 2)), scale=(0.05, 0.05, hgt), alpha=0)
            fxkey(o, f0 + 2, scale=(H * 0.5, H * 0.5, hgt), alpha=0.75)
            fxkey(o, f1 - 4, scale=(H * 0.42, H * 0.42, hgt), alpha=0.6)
            fxkey(o, f1, scale=(0.02, 0.02, hgt), alpha=0)
            notes.append('кадры %d–%d: столб света/воды %s шириной %.1f и высотой %.1f — Neon-часть (твин Size и Transparency)' % (f0, f1, glowc, H * 0.5, hgt))
        elif kind == 'vortex':
            for i in range(10):
                o = _bit('vortex_%d' % i, 0.22 * S, bits[i % len(bits)])
                ang0 = i * 36
                for j, f in enumerate(range(f0, f1 + 1, 3)):
                    t = (f - f0) / float(max(1, f1 - f0))
                    ang = math.radians(ang0 + 540 * t)
                    rr = H * (0.7 - 0.3 * t)
                    fxkey(o, f, loc=base + Vector((math.sin(ang) * rr, y * (1 - t) + D * (1 - t) * 0.5 + math.cos(ang) * rr, H * 1.2 * t * (0.5 + i / 10.0))), scale=1 if j else 0)
                fxkey(o, f1 + 5, scale=0)
            notes.append('кадры %d–%d: вихрь из 10 частиц поднимается по спирали — ParticleEmitter с вращением вокруг оси' % (f0, f1))
        elif kind == 'gate':
            for i, (sx, sz, px, pz) in enumerate(((0.16, 2.2, -0.75, 0), (0.16, 2.2, 0.75, 0), (1.66, 0.16, 0, 1.1), (1.66, 0.16, 0, -1.1))):
                o = blk('gate_%d' % i, (sx * H * 0.6, 0.12 * S, sz * H * 0.6), gm, (0, 0, 0), bev=0.02)
                q = base + Vector((px * H * 0.6, y, _hover_z(a) + H * 0.5 + pz * H * 0.6))
                fxkey(o, 1, loc=q, scale=0, alpha=1)
                fxkey(o, f0, scale=0, alpha=1)
                fxkey(o, f0 + 3, scale=1, alpha=1)
                fxkey(o, f1 - 3, scale=1, alpha=1)
                fxkey(o, f1 + 2, scale=0, alpha=0)
            notes.append('кадры %d–%d: врата — Neon-рамка %s %.1f × %.1f в воздухе, появляется и схлопывается' % (f0, f1, glowc, H * 0.9, H * 1.3))
        elif kind == 'splash':
            sm_ = ghost('%s_splash' % a.id, th['splash'], 1.4, 0.9, 1.0)
            o = torus('splash_ring', 0.6 * S, 0.08 * S, sm_, 16, 4)
            q = base + Vector((0, y, 0.08))
            fxkey(o, 1, loc=q, scale=0, alpha=1)
            fxkey(o, f0, scale=0.3, alpha=1)
            fxkey(o, f0 + 12, scale=3.5, alpha=0)
            for i in range(8):
                d_ = blk('splash_drop_%d' % i, (0.16 * S, 0.16 * S, 0.16 * S), smooth('%s_drop' % a.id, th['splash'], 0.1), (0, 0, 0), bev=0.03 * S)
                ang = math.radians(i * 45)
                p1 = q + Vector((math.cos(ang) * 1.4 * S, math.sin(ang) * 1.4 * S, 1.8 * S))
                fxkey(d_, 1, loc=q, scale=0)
                fxkey(d_, f0, loc=q, scale=1)
                fxkey(d_, f0 + 7, loc=p1)
                fxkey(d_, f0 + 14, loc=(p1.x + math.cos(ang) * 0.6 * S, p1.y + math.sin(ang) * 0.6 * S, base.z + 0.05), scale=0.0)
            notes.append('кадр %d: всплеск — кольцо и 8 капель %s — ParticleEmitter Emit(8), скорость вверх 12' % (f0, th['splash']))
        elif kind in ('bubbles', 'bubbles_mouth'):
            bm_ = ghost('%s_bubble' % a.id, th['splash'], 1.3, 0.8, 0.9)
            for i in range(8):
                o = blk('%s_%d' % (kind, i), (0.2 * S, 0.2 * S, 0.2 * S), bm_, (0, 0, 0), bev=0.07 * S)
                if kind == 'bubbles':
                    q = base + Vector((rnd.uniform(-0.6, 0.6) * S, y + rnd.uniform(-0.4, 0.4), rnd.uniform(0.1, 0.6)))
                    ff = f0 + i * 2
                    up = a.hover + H
                else:
                    hd = a.marks['Head']
                    q = base + Vector((0, (hd[1] - 0.6) * a.S, a.hover + (hd[2] - K.Z0) * a.S))
                    ff = f0 + i
                    up = H * 0.6
                fxkey(o, 1, loc=q, scale=0, alpha=1)
                fxkey(o, ff, loc=q, scale=0.5, alpha=1)
                fxkey(o, ff + 10, loc=q + Vector((rnd.uniform(-0.3, 0.3), -0.3 if kind == 'bubbles_mouth' else 0, up)), scale=1.2, alpha=0)
            notes.append('кадры %d–%d: 8 пузырей %s поднимаются вверх — ParticleEmitter, Rate 12, размер %.2f' % (f0, f0 + 24, th['splash'], 0.2 * S))
        elif kind == 'drops':
            for i in range(8):
                ang = math.radians(i * 45 + 10)
                o = blk('shake_drop_%d' % i, (0.09 * S, 0.09 * S, 0.09 * S), smooth('%s_drop' % a.id, th['splash'], 0.1), (0, 0, 0), bev=0.02 * S, ol=0)
                p0 = base + Vector((0, 0.1, a.hover + H * 0.5))
                p1 = p0 + Vector((math.cos(ang) * H * 0.6, math.sin(ang) * H * 0.6, 0.3 * H))
                fxkey(o, 1, loc=p0, scale=0)
                fxkey(o, f0, loc=p0, scale=0)
                fxkey(o, f0 + 2, loc=p0, scale=1)
                fxkey(o, f0 + 10, loc=(p1.x, p1.y, base.z + 0.05), scale=0.8)
                fxkey(o, f0 + 13, scale=0)
            notes.append('кадр %d: 8 капель разлетаются кругом — ParticleEmitter Emit(8)' % f0)
        elif kind == 'roar':
            hd = a.marks['Head']
            q = base + Vector((0, (hd[1] - 0.7) * a.S, a.hover + (hd[2] - K.Z0) * a.S))
            for i in range(3):
                o = torus('roar_ring_%d' % i, 0.3 * S, 0.035 * S, ghost('%s_roar' % a.id, '#ffffff', 1.6, 0.9, 0.8), 12, 4)
                ff = f0 + i * 3
                fxkey(o, 1, loc=q, scale=0, alpha=1, rot=(70, 0, 0))
                fxkey(o, ff, loc=q, scale=0.3, alpha=1)
                fxkey(o, ff + 9, loc=q + Vector((0, -1.2 * S, 0.5 * S)), scale=2.4, alpha=0)
            notes.append('кадр %d: рёв — 3 белых кольца расходятся от морды — Neon-кольца (Size, Transparency) + звук' % f0)
        elif kind in ('spark_small', 'sparkle', 'gust'):
            cnt = 4 if kind == 'spark_small' else 12
            for i in range(cnt):
                ang = math.radians(i * 360.0 / cnt)
                o = _bit('%s_%d_%d' % (kind, f0, i), 0.14 * S, gm if kind != 'gust' else dust)
                p0 = base + Vector((0, -0.2 * H if kind != 'sparkle' else 0, a.hover + H * 0.5))
                rr = H * (0.35 if kind == 'spark_small' else 0.9)
                p1 = p0 + Vector((math.cos(ang) * rr, math.sin(ang) * rr * 0.6, math.sin(ang * 2) * rr * 0.4))
                fxkey(o, 1, loc=p0, scale=0, alpha=1)
                fxkey(o, f0, loc=p0, scale=1, alpha=1)
                fxkey(o, f0 + 8, loc=p1, scale=0.2, alpha=0, rot=(90, 90, 0))
            if kind != 'spark_small':
                notes.append('кадр %d: %s — ParticleEmitter Emit(12)' % (f0, 'вспышка из 12 искр ' + glowc if kind == 'sparkle' else 'порыв ветра: 12 кубиков пыли в стороны'))
    fx(False)


def build(a):
    a.bush_d = round(max(2.0, a.bush_depth * 0.5 * a.cover + 0.25 * a.len_est + 0.3), 2)
    reveal(a)
    idle(a)
    fx_build(a)
