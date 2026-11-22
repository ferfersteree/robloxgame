# SpearHunt V86 — эффекты копий

Как читать:
- **Время** отсчитывается от касания земли (t = 0, кадр 105 в Blender, 30 fps). Копьё прилетает за 4 кадра (0.13 с) до касания.
- **Цвета** даны в sRGB hex.
- **Размеры** в studs.
- **Neon-меш** — MeshPart из `C:\SpearHuntAssets\spears\sp_NN_id_fx_<имя>.glb`, Material = Neon, анимируется через TweenService: Size, CFrame, Transparency.
- Beam и Trail не используются.
- **Оси эффектов.** Эффекты полёта крепятся к копью (TrailRoot = 2.7 над хватом). Эффекты удара ставятся в точку касания, ось Y направлена вверх.
- **Значения стартовые**: сняты с анимаций в Blender, в игре не проверялись.

---

---

## 01 stick — Stone-tipped Spear (dust)

**FX_Idle** — пыль у наконечника:
- ParticleEmitter на Tip:
  - цвет `#F1DFB8` → `#C99F6C`;
  - Size 0.08–0.15, Transparency 0.3 → 1;
  - Rate 4, Lifetime 1.2–1.8 с;
  - Speed 0.2, SpreadAngle 180, Acceleration (0, 0.3, 0).
- ParticleEmitter бликов:
  - Texture «звёздочка», цвет `#FFF6D8`, Size 0.15;
  - Rate 1.5, Lifetime 0.4 с;
  - LightEmission 1.

**FX_Flight** (цикл 1 с):
- Пыльные клубы — ParticleEmitter на TrailRoot:
  - цвет `#F1DFB8` / `#C99F6C`;
  - Size NumberSequence 0.3 → 1.2 → 0, Transparency 0.2 → 1;
  - Rate 12, Lifetime 0.9 с;
  - EmissionDirection назад, Speed 2–4, SpreadAngle 25, Drag 2.
- Камешки — ParticleEmitter:
  - Texture «камень», цвета `#9A9184` / `#8A5530`, Size 0.15;
  - Rate 7, Lifetime 0.8 с;
  - RotSpeed ±360, Speed 3–5.
- Воздушные кольца — Neon-меш `fx_air_ring`, цвет `#FFF2D2`, раз в 0.33 с:
  - появляется у острия со Size ×0.6;
  - за 1 с уходит на 6.5 назад вдоль древка, растёт до ×2.0;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0 | кратер-валик r 0.55 вырастает до 1.15 и оседает до 1.0 за 0.2 с | меш `fx_crater`, цвет `#8A5530`, Tween Size (Back Out) |
| 0–0.13 | 6 трещин длиной 0.9–1.5 расходятся по земле | 6 узких Part `#5A321C` у поверхности, Tween длины |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#FFF0CC`, Tween Size и Transparency 0 → 1, Quad Out |
| 0–1.33 | 14 клубов пыли разлетаются кольцом на 1.4–2.6 (назад сильнее) и растут до ×2.8 | ParticleEmitter Burst 14: Size 0.4 → 2.5, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3, SpreadAngle 360×20 |
| 0–1.1 | 12 комьев земли и камней летят по дуге, отскакивают и катятся | Burst 12: Texture «ком», Size 0.2–0.35, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 1.2–1.33 | кратер, трещины и комья исчезают | Tween Size → 0 |

Свет: PointLight не нужен.

---

## 02 bone — Bone Spear (dust)

**FX_Idle** — костяная пыль у наконечника:
- ParticleEmitter на Tip:
  - цвет `#F4ECD6` → `#CFC09A`;
  - Size 0.08–0.15, Transparency 0.3 → 1;
  - Rate 4, Lifetime 1.2–1.8 с;
  - Speed 0.2, SpreadAngle 180, Acceleration (0, 0.3, 0).
- ParticleEmitter бликов:
  - Texture «звёздочка», цвет `#FFFBE6`, Size 0.15;
  - Rate 1.5, Lifetime 0.4 с;
  - LightEmission 1.

**FX_Flight** (цикл 1 с):
- Пыльные клубы — ParticleEmitter на TrailRoot:
  - цвет `#F4ECD6` / `#CFC09A`;
  - Size NumberSequence 0.3 → 1.2 → 0, Transparency 0.2 → 1;
  - Rate 10, Lifetime 0.9 с;
  - EmissionDirection назад, Speed 2–4, SpreadAngle 25, Drag 2.
- Костяные осколки — ParticleEmitter с мешем `fx_chip` (шип длиной 0.34):
  - цвета `#F1E6C8` / `#CDB68A`, Size 0.3;
  - Rate 8, Lifetime 1 с;
  - RotSpeed ±360, Speed 4–6 назад, SpreadAngle 20.
- Воздушные кольца — Neon-меш `fx_dust_ring`, цвет `#FFF6DC`, 3 на цикл:
  - появляются у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад вдоль древка, растут до ×2.0;
  - Transparency 0.2 → 1.
- Искорки — ParticleEmitter: цвет `#FFFBE6`, Size 0.1, Rate 4, Lifetime 0.8 с, LightEmission 1.

**FX_Impact** (1.5 с) — «костяной веер»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0 | кратер-валик r 0.5 вырастает до ×1.15 и оседает | меш `fx_crater`, цвет `#CDB68A`, Tween Size (Back Out), 0.2 с |
| 0–0.13 | 5 тёмных трещин длиной 0.8–1.3 расходятся по земле | 5 узких Part `#4A3A36` у поверхности, Tween длины |
| 0–0.4 | плоское ударное кольцо от r 0.15 до 2.3, гаснет | меш `fx_dust_ring`, Neon `#FFF6DC`, Tween Size и Transparency 0 → 1, Quad Out |
| 0–1.33 | низкое кольцо пыли: 14 плоских клубов катятся по земле на 1.5–2.3 (назад дальше), растут до ×2.1 | ParticleEmitter Burst 14: цвета `#F4ECD6` / `#CFC09A`, Size 0.4 → 2.2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3, SpreadAngle 360×15 (почти горизонтально) |
| 0–0.47 | 5 костяных заноз отлетают назад дугой (пик 1.9) и втыкаются вертикально веером (углы 150°–210° за копьём, r 1.5–1.75, наклон наружу ~17°) | 5 мешей `fx_bone_splinter` (длина 0.85–0.95, цвета `#F1E6C8` / `#CDB68A`), Tween CFrame по дуге 0.33 с + Back Out в конце; потом лёгкая дрожь 0.1 с |
| 0–1.1 | 14 камешков и 6 костяных осколков летят по дуге, отскакивают | меш `fx_pebble` (`#A59C8C` / `#CDB68A`) и `fx_chip`: Burst 20, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 1.0–1.33 | кратер, трещины, занозы и камни уменьшаются до нуля | Tween Size → 0 |

Свет: PointLight не нужен.

---

## 03 bronze — Bronze Spear (sparks)

**FX_Idle** — блики и искры у лезвия:
- ParticleEmitter бликов на Tip:
  - Texture «звёздочка», цвет `#FFF1C0`, Size 0.15;
  - Rate 2, Lifetime 0.4 с;
  - LightEmission 1.
- ParticleEmitter искорок:
  - Texture «искра», цвет `#FFD27A`, Size 0.08–0.12;
  - Rate 4, Lifetime 1 с, Speed 0.3, SpreadAngle 180;
  - LightEmission 1.

**FX_Flight** (цикл 1 с):
- Длинные искры — меш `fx_spark` (тонкая призма, длина 0.6), Neon `#FFD27A` / `#FFF1C0` поочерёдно, 14 на цикл:
  - вытянуты вдоль оси, летят назад на 12.5, расходятся до ±0.9 в стороны;
  - Size 0 → ×1 → 0, живут 1 с.
- Бронзовые чешуйки — меш `fx_bronze_flake`, цвета `#E8B35A` / `#C98A3A`, 6 на цикл:
  - кувыркаются 720° и 540°, отлетают на 13 назад и до 0.8 в стороны.
- Кольца-звон вокруг оси — меш `fx_shock_ring` (тор, ось вдоль древка), Neon `#FFB347`, 3 на цикл:
  - стартуют у острия (Size ×0.6), уходят на 6.5 назад, растут до ×2.1;
  - Transparency 0.2 → 1.
- Тёплая пыль — ParticleEmitter за хвостом: цвет `#D9C9A0`, Size 0.3 → 1.2, Transparency 0.2 → 1, Rate 4, Lifetime 1 с.

**FX_Impact** (1.5 с) — «лязг»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#FFE2A0`, Transparency 0.2 → 1, Tween 0.33 с |
| 0 и 0.17 | два плоских бронзовых ударных кольца разбегаются по земле до r 2.6 / 2.1 | меш `fx_shock_ring`, Neon `#FFB347`, Tween Size и Transparency 0 → 1, Quad Out, 0.43 с каждое |
| 0, 0.13, 0.27 | три вертикальных «гонга» (кольцо стоит ребром, нормаль вдоль оси X) на высоте 1.0 расширяются до ×2.4–×3.4 и гаснут | меш `fx_gong_ring`, Neon `#FFB347`, CFrame ориентирован вертикально, Size 0.3 → ×2.4…×3.4, Transparency 0 → 1, 0.6 с каждое |
| 0–0.4 | тонкий диск-«мембрана» гонга растёт до ×2.6 и гаснет | Neon-Part (цилиндр) `#FFC566`, Transparency 0.3 → 1 |
| 0 | вмятина-валик r 0.5 вырастает ×1.12 и оседает | меш `fx_dent` (тор) цвет `#6B4A30`, Tween Size |
| 0–0.9 | 18 длинных искр веером вперёд (по оси +X, ±42° по горизонту, вверх 38–62°), каждая развёрнута по скорости | меш `fx_spark`, Neon `#FFD27A` / `#FFF1C0`; Burst 18: Speed 7–10, Acceleration (0, −27, 0), Lifetime 0.87; плюс 6 искр назад Burst 6 Speed 3–5 |
| 0–1.1 | 6 бронзовых чешуек летят по дуге и отскакивают | меш `fx_bronze_flake`, цвета `#E8B35A` / `#9A5F26`, Burst 6, Speed 3–5 вверх, Acceleration (0, −25, 0) |
| 0.1–1.33 | 6 тёплых клубов пыли расходятся до 1.2–1.8 и растут | ParticleEmitter Burst 6: `#D9C9A0`, Size 0.4 → 1.8, Transparency 0.2 → 1, Lifetime 1.2 |
| 1.0–1.33 | вмятина и остальное исчезают | Tween Size → 0 |

Свет: PointLight `#FFB347`, Brightness 3 → 0 за 0.4 с, Range 8.

---

## 04 feather — Feather Spear (feathers)

**FX_Idle** — пёрышки и блики у наконечника:
- ParticleEmitter «пёрышки» на Tip:
  - Texture «пёрышко», цвета по очереди `#E0483A` / `#2BB5A8` / `#F4C542` / `#3D7FD9`;
  - Size 0.2–0.3, Rate 2, Lifetime 2 с;
  - Speed 0.2, SpreadAngle 180, Acceleration (0, −0.3, 0), RotSpeed ±60.
- ParticleEmitter бликов:
  - Texture «звёздочка», цвет `#FFFBE0`, Size 0.15;
  - Rate 1.5, Lifetime 0.4 с;
  - LightEmission 1.

**FX_Flight** (цикл 1 с):
- Летящие перья — меш `fx_drift_feather` (длина 0.6), цвета шести перьев `#E0483A`, `#2BB5A8`, `#F4C542`, `#3D7FD9`, `#F6F0E0`, `#F08A30`, 10 на цикл:
  - стартуют у острия, уходят на 12 назад, расходятся до ±0.9 в стороны;
  - кувыркаются 360° и покачиваются ±40°, дрейфуют с волной ±0.2;
  - Size 0 → ×1 → 0.
- Пух — ParticleEmitter на TrailRoot:
  - цвет `#FFFAF0`, Size 0.2 → 0.9 → 0, Transparency 0.2 → 1;
  - Rate 8, Lifetime 1 с, EmissionDirection назад, Speed 2–3, SpreadAngle 30.
- Листочки — ParticleEmitter: Texture «лист», цвета `#5FBF4A` / `#3C9A3A`, Size 0.3, Rate 6, Lifetime 1 с, RotSpeed ±300, Speed 3–5 назад.

**FX_Impact** (1.5 с) — «перьевой взрыв»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#F4FFD0`, Transparency 0.4 → 1, Tween 0.33 с |
| 0–0.43 | кольцо по земле до r 2.5, гаснет | меш `fx_leaf_ring`, Neon `#D8FFA8`, Tween Size и Transparency 0 → 1, Quad Out |
| 0–1.2 | 18 перьев вылетают вверх и, кружась по спирали (1.1 оборота, радиус до 0.8–1.4), медленно опускаются; высота пика 1.6–3.2 | меш `fx_feather` (длина 0.9), цвета шести перьев по кругу; Tween CFrame по 12 точкам с шагом 0.1 с, высота z = 0.15 + H·sin(π·u^0.65); чётные крутятся по часовой, нечётные против; покачивание ±25° и ±40° |
| 0.03–0.4 | 8 пучков травы (по 3 травинки) по кругу r 1.0–2.0 выскакивают с перерегулировкой ×1.25, старт с шагом 0.03 с | меш `fx_grass_blade` (конус r 0.07, высота 0.55–0.7), цвета `#5FBF4A` / `#3C9A3A`, Tween Size (Back Out), наклон наружу ~24° |
| 0–1.3 | 6 пуховых клубов поднимаются до высоты 1.9 и растут до ×1.6 | ParticleEmitter Burst 6: `#FFFAF0`, Size 0.3 → 1.2, Transparency 0.2 → 1, Lifetime 1.2, Acceleration (0, 1, 0) |
| 1.1–1.33 | перья и трава схлопываются | Tween Size → 0 |

Свет: PointLight `#D8FFA8`, Brightness 1.5 → 0 за 0.4 с, Range 6.

---

## 05 iron — Boar Spear (sparks)

**FX_Idle** — блики и искорки у лезвия:
- ParticleEmitter бликов на Tip:
  - Texture «звёздочка», цвет `#FFD27A`, Size 0.15;
  - Rate 1.5, Lifetime 0.4 с;
  - LightEmission 1.
- ParticleEmitter искорок:
  - цвет `#FF9A3A`, Size 0.06–0.1;
  - Rate 4, Lifetime 1 с, Speed 0.3, SpreadAngle 180, LightEmission 1.

**FX_Flight** (цикл 1 с):
- Искры — Neon-меш-призма (как `fx_spark`, длина 0.5) или ParticleEmitter с вытянутой текстурой, цвета `#FF9A3A` / `#FFD27A`:
  - 12 на цикл, летят назад на 12, расходятся до ±0.9;
  - Size 0 → ×1 → 0, Lifetime 1 с.
- Железная крошка — ParticleEmitter:
  - Texture «камень», цвета `#6A7480` / `#C4602A`, Size 0.18;
  - Rate 6, Lifetime 0.9 с, RotSpeed ±360, Speed 4–6 назад.
- Пыль саванны — ParticleEmitter на TrailRoot:
  - цвета `#DCC592` / `#B69A68`, Size 0.3 → 1.4 → 0, Transparency 0.2 → 1;
  - Rate 8, Lifetime 1 с, EmissionDirection назад, Speed 2–4.
- Воздушные кольца — Neon-меш `fx_iron_ring`, цвет `#FFC27A`, 3 на цикл:
  - стартуют у острия (Size ×0.6), за 1 с уходят на 6.5 назад, растут до ×2.0;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «тяжёлый удар»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#FFB15A`, Transparency 0.4 → 1, Tween 0.33 с |
| 0–0.3 | 4 каменные плиты вокруг копья (r 1.35, углы 45°/135°/225°/315°, размер 1.15 × 0.85 × 0.3) трескаются: подпрыгивают на 0.3 и наклоняются на ~34° внутренним краем вверх, потом оседают до 26° (старт с шагом 0.03 с) | меш `fx_slab` (`#A89C84` / `#7A6E5C` по очереди), Tween CFrame и Size (Back Out), 0.3 с |
| 0–0.13 | 4 тёмные трещины длиной ~1.5 расходятся от копья между плитами | узкие Part `#4A5360` у поверхности, Tween длины |
| 0–0.5 | прямая борозда длиной 4.0 вперёд (+X) прочерчивается по земле | меш `fx_groove` (плоский брусок 4 × 0.2 × 0.05, `#4A5360`), Tween Size по X от 0.01 до 1 и CFrame вперёд, 0.33 с |
| 0–0.6 | 14 оранжевых искр скользят вперёд вдоль земли на 1.6–4.2 (старт с шагом 0.03 с), подпрыгивая на 0.12, гаснут | меш `fx_spark` (лёжа вдоль X), Neon `#FF9A3A` / `#FFD27A`; Tween CFrame 0.47–0.63 с, Transparency 0 → 1 |
| 0–1.33 | 10 клубов пыли расходятся на 1.4–2.4 (вперёд на 30% дальше) и растут до ×2.6 | ParticleEmitter Burst 10: `#DCC592` / `#B69A68`, Size 0.4 → 2.4, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 0–1.1 | 10 камешков летят по дуге и отскакивают | меш `fx_pebble` (`#A89C84` / `#4A5360`), Burst 10, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 1.0–1.33 | плиты, трещины, борозда и камни исчезают | Tween Size → 0 |

Свет: PointLight `#FF9A3A`, Brightness 2 → 0 за 0.4 с, Range 8.

---

## 06 obsidian — Obsidian Spear (shards)

**FX_Idle** — блики и стеклянные крошки у лезвия:
- ParticleEmitter бликов на Tip:
  - Texture «звёздочка», цвет `#E8D2FF`, Size 0.15;
  - Rate 1.5, Lifetime 0.4 с;
  - LightEmission 1.
- ParticleEmitter крошек:
  - Texture «осколок», цвет `#2A2236`, Size 0.1–0.16;
  - Rate 3, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180, RotSpeed ±120.

**FX_Flight** (цикл 1 с):
- Стеклянные осколки — меш `fx_drift_shard` (двойная пирамида длиной 0.4), цвета `#2A2236` и каждый третий `#5A3F8A`, 12 на цикл:
  - летят назад на 12.5, расходятся до ±1.3 в стороны;
  - кувыркаются 540° и 360°;
  - Size 0 → ×1 → 0.
- Красные угли — ParticleEmitter:
  - цвет `#FF6A4A` / `#FFC7A0`, Size 0.12, Rate 8, Lifetime 0.9 с;
  - Speed 4, SpreadAngle 40, LightEmission 1.
- Жаровые кольца — Neon-меш `fx_ember_ring`, цвет `#FF5A3A`, 3 на цикл:
  - стартуют у острия (Size ×0.6), уходят на 6.5 назад, растут до ×2.0;
  - Transparency 0.2 → 1.
- Тёмный дымок — ParticleEmitter за хвостом: цвет `#4A3858`, Size 0.3 → 1.2, Transparency 0.2 → 1, Rate 4, Lifetime 1 с.

**FX_Impact** (1.5 с) — «стеклянная звезда»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#9A6AF0`, Transparency 0.4 → 1, Tween 0.33 с |
| 0–0.43 | красное ударное кольцо по земле до r 2.5, гаснет | меш `fx_ember_ring`, Neon `#FF5A3A`, Tween Size и Transparency 0 → 1, Quad Out |
| 0.03–0.27 | 6 светящихся трещин длиной ~1.8 расходятся лучами (углы 10°, 70°, … через 60°) | узкие Neon-Part `#FF5A3A` толщиной 0.12 вдоль земли, Tween длины; к 1.0 с гаснут |
| 0.03–0.27 | 12 чёрных стеклянных шипов вырастают шестилучевой звездой: на каждом луче два шипа, r 0.8 (высота 1.0, фиолетовый `#5A3F8A`) и r 1.55 (высота 1.7, чёрный `#2A2236`), наклон наружу ~17°; перерегулировка ×1.2 | меш `fx_glass_spike` (пятигранная пирамида), Tween Size (Back Out), старт с шагом 0.03–0.1 с |
| 0.47–0.53 | все шипы разом раскалываются: исчезают за 0.07 с | Tween Size → 0 |
| 0.5–1.2 | 24 осколка (по два от шипа) разлетаются от мест шипов по дуге в стороны от центра, вращаясь, и ложатся на землю | меш `fx_glass_shard` (`#2A2236` / `#5A3F8A`), Burst 24, Speed 3–6, Acceleration (0, −27, 0), RotSpeed ±600, Lifetime 0.7 (до 22 кадров) |
| 0.5–0.97 | 6 блёсток вспыхивают над землёй на r 1.2 и гаснут | ParticleEmitter Burst 6: Texture «звёздочка», `#E8D2FF`, Size 0.3, Lifetime 0.5, LightEmission 1 |
| 1.0–1.33 | оставшиеся осколки и трещины исчезают | Tween Size → 0, Transparency → 1 |

Свет: PointLight `#FF5A3A`, Brightness 2.5 → 0 за 0.5 с, Range 8.

---

## 07 crystal — Chime Crystal Spear (crystal)

**FX_Idle** — мерцание кристалла:
- Аура — Neon-эллипсоид `#9ADCFF`, Transparency 0.95, вокруг кристалла (r 0.6, вытянут ×2.1 по высоте), пульсация Size ±5% за 1.5 с.
- ParticleEmitter бликов на Tip:
  - Texture «звёздочка», цвет `#F0FCFF`, Size 0.15–0.2;
  - Rate 2, Lifetime 0.5 с, LightEmission 1.
- Кристальная пыль — ParticleEmitter: цвет `#6FC8FF`, Size 0.08, Rate 3, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180, LightEmission 0.8.
- PointLight `#7FE6FF`, Brightness 0.6, Range 5.

**FX_Flight** (цикл 1 с):
- Осколки кристалла — меш `fx_drift_crystal` (двойная пирамида длиной 0.36), Neon `#6FC8FF` / `#9A8AFF` поочерёдно, 8 на цикл:
  - летят назад на 12.5, расходятся до ±0.9;
  - кувыркаются 540° и 360°, Size 0 → ×1 → 0.
- Звёздочки — ParticleEmitter: Texture «звёздочка», цвета `#F0FCFF` / `#5FF0FF`, Size 0.3, Rate 8, Lifetime 1 с, Speed 3–5 назад, LightEmission 1.
- Звуковые кольца — Neon-меш `fx_chime_ring`, цвет `#7FE6FF`, 4 на цикл:
  - стартуют у острия (Size ×0.5), за 1 с уходят на 7 назад, растут до ×2.1;
  - Transparency 0.2 → 1.
- Искорки — ParticleEmitter: цвет `#F0FCFF`, Size 0.1, Rate 4, Lifetime 0.9 с, LightEmission 1.

**FX_Impact** (1.5 с) — «перезвон»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#C8F8FF`, Transparency 0.4 → 1, Tween 0.33 с |
| 0–0.4 | плоское ударное кольцо по земле до r 2.2, гаснет | Neon-меш `fx_chime_ring`, `#7FE6FF`, Tween Size и Transparency 0 → 1, Quad Out |
| 0, 0.17, 0.33 | 3 больших кольца (r 0.6) поднимаются вертикально над точкой касания с 0.2 до высоты 3.4, растут от ×0.4 до ×2.3 и гаснут (как звуковые волны), 0.73 с каждое | меш `fx_chime_ring`, Neon `#7FE6FF`, Tween CFrame по Y и Size, Transparency 0 → 1 |
| 0, 0.17, 0.33 | 3 малых кольца (r 0.4) идут следом чуть выше, растут до ×1.5 | то же, меньший Size |
| 0.07–0.4 | шестиугольное кольцо r 1.5 раскрывается по земле | меш `fx_hex_ring` (тор из 6 сегментов), Neon `#7FE6FF`, Tween Size 0 → 1, держится до 1.0 с |
| 0.07–0.4 | 6 кристаллов (высота 1.15, r 0.2) вырастают в вершинах шестиугольника r 1.5 (старт с шагом 0.03 с), перерегулировка ×1.25, наклон наружу ~9° | меш `fx_hex_crystal`, цвета `#6FC8FF` / `#9A8AFF` поочерёдно, Tween Size (Back Out) |
| 0.17–0.5 | 6 малых кристаллов (высота 0.5) вырастают между ними на r 1.2 | тот же меш, Size ×0.45, цвета в обратном порядке |
| 0–1.3 | 14 звёздочек и 8 искр поднимаются на 1.5–3.6, мерцают (Size 1.0–1.6 → 0) | меш `fx_sparkle` (звезда) Neon `#F0FCFF` / `#5FF0FF` или ParticleEmitter Burst 22, Size 0.3, Lifetime 0.7–0.9, Acceleration (0, 3, 0) |
| 1.0–1.33 | кристаллы и кольцо схлопываются | Tween Size → 0 |

Свет: PointLight `#7FE6FF`, Brightness 3 → 0 за 0.7 с, Range 9.

---

## 08 fire — Ember Blade Spear (fire)

**FX_Idle** — жар и язычки у клинка:
- Тепловая аура — Neon-эллипсоид `#FF8A3A`, Transparency 0.88, вокруг клинка (r 0.6, вытянут ×2 по высоте), пульсация Size ±5% за 1 с.
- ParticleEmitter язычков на Tip:
  - Texture «язычок», цвета `#FF5A14` / `#FFC23A`;
  - Size 0.15–0.25, Rate 6, Lifetime 1 с;
  - Acceleration (0, 1.5, 0), LightEmission 1.
- ParticleEmitter угольков: цвет `#FFD25A`, Size 0.08, Rate 3, Lifetime 1.2 с, LightEmission 1.
- PointLight `#FF7A2A`, Brightness 1, Range 6.

**FX_Flight** (цикл 1 с):
- Языки пламени — меш `fx_flame_tongue`, Neon `#FF5A14` / `#FFC23A` / `#E0302A` по очереди, 12 на цикл:
  - направлены назад (развёрнуты на 180°), Size ×1.4 → ×0.8;
  - тянутся на 11.5 назад и расходятся до 0.7 в стороны.
- Искры — ParticleEmitter: цвет `#FFC23A`, Size 0.12, Rate 10, Lifetime 0.9 с, Speed 4, SpreadAngle 45, LightEmission 1.
- Огненные кольца — Neon-меш `fx_fire_ring` (тор вокруг оси), `#FF5A14` / `#FFC23A`, 3 на цикл:
  - уходят на 6 назад, Size ×0.5 → ×2.0, вращаются 360° за цикл.
- Дым — ParticleEmitter за хвостом: цвет `#4A3A3A`, Size 0.4 → 1.6, Transparency 0.2 → 1, Rate 4, Lifetime 1 с.
- PointLight `#FF7A2A`, Brightness 2, Range 9.

**FX_Impact** (1.5 с) — «огненный взрыв и горящее кольцо»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.47 | огненная сфера r 0.6 вырастает до ×2.6 за 0.13 с, до ×3.6 к 0.47 с и гаснет | Neon-шар `#FF7A22`, Tween Size, Transparency 0 → 1 |
| 0–0.27 | внутреннее ядро r 0.5 вспыхивает до ×2.4 и гаснет | Neon-шар `#FFD25A`, Tween 0.27 с |
| 0.07–0.27 | чёрное пятно копоти r 1.9 расползается по земле, держится до 1.2 с | меш `fx_scorch` (плоский диск, `#2C201C`), Tween Size |
| 0.07–0.3 | раскалённое кольцо r 1.6 на земле проявляется и тлеет (Transparency 0 → 0.3 → 1) | Neon-тор `#FF6A1A` |
| 0.17–0.6 | 14 огоньков по кольцу r 1.6 (высота 0.85) и 6 по внутреннему r 0.95 (высота 0.6) загораются по очереди (шаг ~0.03 с), мерцают ×1.0 → ×1.35 → ×0.9 | меш `fx_flame`, Neon `#FF5A14` / `#FFC23A` / `#E0302A` по кругу, Tween Size по Y с Sine |
| 0.7–1.3 | огоньки опадают до ×0.5 (тлеют) и гаснут | Tween Size → 0.5 → 0 |
| 0–1.0 | 12 углей летят по дуге на 1–2.5 и гаснут | меш `fx_ember` или ParticleEmitter Burst 12: `#FFD25A` / `#FF6A1A`, Size 0.12, Speed 5–9, Acceleration (0, −27, 0), Lifetime 0.9, LightEmission 1 |
| 0.17–1.33 | 8 клубов дыма поднимаются на 2.2–3.4 и растут до ×2.3 | ParticleEmitter Burst 8: `#4A3A3A`, Size 0.5 → 2.2, Transparency 0.2 → 1, Lifetime 1.2 |

Свет: PointLight `#FF7A2A`, Brightness 4 → 0 за 0.8 с, Range 10.

---

## 09 ice — Frost Crystal Spear (ice)

**FX_Idle** — снежинки и блики:
- ParticleEmitter снежинок на Tip:
  - Texture «снежинка», цвет `#F4FBFF`, Size 0.06–0.12;
  - Transparency 0.2 → 1, Rate 4, Lifetime 1.5 с;
  - Speed 0.2, SpreadAngle 180, Acceleration (0, −0.3, 0).
- ParticleEmitter бликов: Texture «звёздочка», цвет `#F4FCFF`, Size 0.15–0.2, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#9AE8FF`, Brightness 0.5, Range 5.

**FX_Flight** (цикл 1 с):
- Ледяные осколки — меш `fx_drift_shard` (двойная пирамида длиной 0.4), цвета `#BFE9FF` / `#6AB4F0`, 10 на цикл:
  - летят назад на 12.5, расходятся до ±1.3;
  - кувыркаются 540° и 360°, Size 0 → ×1 → 0.
- Снежные клубы — ParticleEmitter на TrailRoot:
  - цвет `#F4FBFF`, Size 0.3 → 1.4 → 0, Transparency 0.2 → 1;
  - Rate 8, Lifetime 1 с, EmissionDirection назад, Speed 2–4, SpreadAngle 30.
- Морозные кольца — Neon-меш `fx_frost_ring`, цвет `#9AE8FF`, 3 на цикл:
  - стартуют у острия (Size ×0.6), уходят на 6.5 назад, растут до ×2.0;
  - Transparency 0.2 → 1.
- Снежинки — ParticleEmitter: Texture «снежинка» (6 лучей), цвет `#F4FCFF`, Size 0.4, Rate 5, Lifetime 1 с, RotSpeed ±360, Speed 3–5 назад, LightEmission 0.6.

**FX_Impact** (1.5 с) — «ледяной веер»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#D0F6FF`, Transparency 0.4 → 1, Tween 0.33 с |
| 0–0.4 | кольцо мороза по земле до r 2.5, гаснет | меш `fx_frost_ring`, Neon `#9AE8FF`, Tween Size и Transparency 0 → 1, Quad Out |
| 0–0.4 | ледяной диск r 2.7 расползается по земле (с ×0.1 до ×1.0), держится до 1.13 с | меш `fx_frost_disc` (плоский диск, `#EEF8FF`), Tween Size, Quad Out |
| 0–0.4 | светящаяся кромка диска r 2.5 (альфа 0.9 → 0.5 → 0.3) | Neon-диск `#BFEEFF`, Transparency 0.1 → 0.5 → 1 |
| 0.03–0.3 | 6 внутренних шипов (r 0.9, высота 1.35) вырастают первыми | меш `fx_ice_spike` (шестигранная пирамида), цвета `#BFE9FF` / `#6AB4F0` поочерёдно, Tween Size (Back Out, перерегулировка ×1.15–1.3), наклон наружу ~19° |
| 0.1–0.37 | 10 средних шипов (r 1.65, высота ~1.0) | тот же меш |
| 0.17–0.43 | 12 внешних шипов (r 2.35, высота ~0.7) | тот же меш; всего 28 шипов, шаг старта 0.03 с внутри кольца |
| 0–1.1 | 10 ледяных осколков разлетаются по дуге и ложатся | меш `fx_ice_shard`, Burst 10, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0–1.33 | 8 снежных клубов поднимаются до 0.6–1.2 и растут до ×1.9 | ParticleEmitter Burst 8: `#F4FBFF`, Size 0.4 → 1.8, Transparency 0.2 → 1, Lifetime 1.2 |
| 1.0–1.33 | шипы и диск схлопываются | Tween Size → 0 |

Свет: PointLight `#9AE8FF`, Brightness 3 → 0 за 0.6 с, Range 9.

---

## 10 star — Meteorite Star Spear (stars)

**FX_Idle** — звёздочки вокруг головы:
- ParticleEmitter «звёздочки» на Tip:
  - Texture «звезда 5 лучей», цвета `#FFE27A` / `#FFF6C8`;
  - Size 0.15–0.3, Rate 3, Lifetime 1.5 с;
  - Speed 0.2, SpreadAngle 180, RotSpeed ±60, LightEmission 1.
- ParticleEmitter искорок: цвет `#4AD8E8`, Size 0.08, Rate 3, Lifetime 1.2 с, Acceleration (0, 0.5, 0), LightEmission 1.
- PointLight `#FFD24A`, Brightness 0.7, Range 5.

**FX_Flight** (цикл 1 с):
- Кувыркающиеся звёзды — меш `fx_drift_star` (пятилучевая, радиус 0.2), Neon `#FFE27A` / `#FFF6C8`, 10 на цикл:
  - летят назад на 12.5, расходятся до ±1.3;
  - вращаются на 540° вокруг вертикальной оси, Size 0 → ×1.2 → 0.
- Бирюзовые искры — ParticleEmitter: цвет `#4AD8E8`, Size 0.1, Rate 8, Lifetime 0.9 с, Speed 4, SpreadAngle 40, LightEmission 1.
- Звёздные кольца — Neon-меш `fx_flash_ring`, цвет `#FFD24A`, 3 на цикл:
  - стартуют у острия (Size ×0.6), уходят на 6.5 назад, растут до ×2.0;
  - Transparency 0.2 → 1.
- Туманность — ParticleEmitter за хвостом: цвет `#7A5AD8`, Size 0.3 → 1.4, Transparency 0.3 → 1, Rate 5, Lifetime 1 с.

**FX_Impact** (1.5 с) — «звёздная метка»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.37 | вспышка-сфера r 0.5 → 1.6, гаснет | Neon-шар `#FFE9A8`, Transparency 0.35 → 1, Tween 0.37 с |
| 0–0.43 | кольцо по земле до r 2.5, гаснет | меш `fx_flash_ring`, Neon `#FFD24A`, Tween Size и Transparency 0 → 1, Quad Out |
| 0.07–0.33 | плоская пятилучевая звезда r 2.0 (внутренний r 0.85) проявляется на земле с поворотом −40° → 0°, держится до 0.93 с, медленно тускнеет и разворачивается на 8° | меш `fx_ground_star` (плоская звезда толщиной 0.04), Neon `#FFD24A`, Tween Size, Rotation, Transparency 0 → 0.3 → 1 |
| 0.07–0.33 | внутренняя звезда r 1.0 (повёрнута на 36°) светлее | тот же меш, Size ×0.5, Neon `#FFF6C8` |
| 0–1.0 | 5 больших звёзд (r 0.4) вылетают вверх и в стороны по кругу (углы 18° + 72°·k, старт с шагом 0.03 с): подъём на 2.4–2.7, разлёт до r 2.2, вращение ±720°, падение на землю к 0.8 с | меш `fx_flying_star`, Neon `#FFE27A` / `#FFF6C8` по очереди, Tween CFrame по 4 точкам (0.2 / 0.47 / 0.8 с), Transparency к концу 0 → 1 |
| 0.1–0.8 | 10 малых звёздочек (r 0.15) разлетаются по кругу r 2.6–2.8 и падают | меш `fx_flying_star`, Size ×0.4, Neon `#4AD8E8` / `#FFE27A` |
| 0–1.3 | 18 мерцающих искр поднимаются на 1.4–3.0 | меш `fx_star_dust` (шарик r 0.06) или ParticleEmitter Burst 18: `#FFE27A` / `#4AD8E8`, Size 0.12, Lifetime 0.8, Acceleration (0, 3, 0), LightEmission 1 |
| 0–1.1 | 6 осколков метеорита летят по дуге и отскакивают | меш Part `#4E4A58` / `#7A7688`, Burst 6, Speed 6–10, Acceleration (0, −25, 0) |
| 0.1–1.33 | 4 фиолетовых облачка поднимаются и растут до ×1.9 | ParticleEmitter Burst 4: `#7A5AD8`, Size 0.5 → 2, Transparency 0.3 → 1, Lifetime 1.2 |

Свет: PointLight `#FFD24A`, Brightness 3 → 0 за 0.6 с, Range 10.

---

## 11 amber_sting — Amber Sting (sparks)

**FX_Idle** — пузырьки в янтаре и блики:
- ParticleEmitter пузырьков на Tip:
  - Texture «пузырь с ободком», цвет `#FFE6A0`;
  - Size 0.1–0.2, Transparency 0.2 → 1;
  - Rate 3, Lifetime 1.5 с, Acceleration (0, 0.6, 0).
- ParticleEmitter бликов: Texture «звёздочка», цвет `#FFE27A`, Size 0.15, Rate 2, Lifetime 0.4 с, LightEmission 1.
- Искорки мёда — цвет `#FFC83A`, Size 0.08, Rate 2, Lifetime 1.2 с, LightEmission 1.
- PointLight `#FFC83A`, Brightness 0.6, Range 5.

**FX_Flight** (цикл 1 с):
- Капли мёда — меш `fx_honey_drop` (Size вытянут ×1.3 по оси), цвета `#F5A623` / `#FFD45A` поочерёдно, 10 на цикл:
  - летят назад на 12.5, расходятся до ±1.25;
  - Size ×0.7 → ×1.5 → 0.
- Золотые искры — ParticleEmitter: цвета `#FFE27A` / `#FFC83A`, Size 0.12, Rate 10, Lifetime 0.9 с, Speed 4, SpreadAngle 45, LightEmission 1.
- Соты-кольца — Neon-меш `fx_hex_ring` (тор из 6 сегментов), цвет `#FFC83A`, 3 на цикл:
  - стартуют у острия (Size ×0.6), уходят на 6.5 назад, растут до ×2.0, поворачиваются на 120°;
  - Transparency 0.2 → 1.
- Крылышки — ParticleEmitter: Texture «листик-крылышко», цвет `#E8F2FF`, Size 0.35, Rate 4, Lifetime 1 с, RotSpeed ±300, Speed 4–6 назад.

**FX_Impact** (1.5 с) — «медовая лужа и соты»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#FFD86A`, Transparency 0.4 → 1, Tween 0.33 с |
| 0–0.43 | золотое кольцо по земле до r 2.3, гаснет | Neon-меш `fx_hex_ring` или тор, `#FFC83A`, Tween Size и Transparency 0 → 1 |
| 0.03–0.47 | медовая лужа r 2.0 растёт по земле (с ×0.1 до ×1.0), держится до 1.13 с | меш `fx_honey_puddle` (плоский диск), цвет `#F5A623`, Tween Size, Quad Out |
| 0.2–0.4 | 5 плоских капель-клякс r 0.4 вылезают на краю лужи (r 1.7–2.2) | тот же материал, Size ×1.2 → ×1.0 |
| 0.1–0.4 | 7 шестигранных призм-сот растут рядом впереди копья (центр в 1.7 по +X): центральная высотой 1.5 и 6 вокруг высотой 0.7–1.2 (шаг 0.77, старт с шагом 0.03 с), перерегулировка ×1.2 по высоте | меш `fx_honey_comb` (шестигранная призма r 0.4), цвета `#F5A623` / `#FFD45A` поочерёдно, Tween Size (Back Out) |
| 0–1.1 | 14 капель мёда летят по дуге и шлёпаются на землю | меш `fx_honey_drop` (r 0.09–0.15), цвета `#F5A623` / `#FFD45A`, Burst 14, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0–0.9 | 14 золотых искр разлетаются по дуге и гаснут | меш `fx_golden_spark` (шарик r 0.06) или ParticleEmitter Burst 14: `#FFE27A` / `#FFC83A`, Size 0.12, Lifetime 0.87, Acceleration (0, −27, 0), LightEmission 1 |
| 1.0–1.33 | лужа, соты и капли схлопываются | Tween Size → 0 |

Свет: PointLight `#FFC83A`, Brightness 3 → 0 за 0.6 с, Range 9.

---

## 12 solar_trident — Solar Trident (fire)

**FX_Idle** — солнечный жар за зубьями:
- Аура — Neon-эллипсоид `#FFC23A`, Transparency 0.88, за зубьями (r 0.7, растянут ×1.5 по ширине и ×1.6 по высоте), пульсация Size ±5% за 1.2 с.
- ParticleEmitter бликов на Tip: Texture «звёздочка», цвет `#FFF0A8`, Size 0.15, Rate 2, Lifetime 0.4 с, LightEmission 1.
- ParticleEmitter язычков вокруг зубьев:
  - Texture «язычок», цвета `#FF6A1A` / `#FFC23A`, Size 0.15–0.25;
  - Rate 5, Lifetime 1 с, Acceleration (0, 1.5, 0), LightEmission 1.
- PointLight `#FFC23A`, Brightness 1, Range 6.

**FX_Flight** (цикл 1 с):
- Языки пламени — меш `fx_flame_tongue`, Neon `#FF6A1A` / `#FFC23A` поочерёдно, 8 на цикл:
  - направлены назад, Size ×1.4 → ×0.8;
  - тянутся на 11.5 назад, расходятся до 0.8 в стороны.
- Золотые искры — ParticleEmitter: цвета `#FFD24A` / `#FFF0A8`, Size 0.12, Rate 8, Lifetime 0.9 с, Speed 4, SpreadAngle 45, LightEmission 1.
- Солнечные кольца — Neon-меш `fx_sun_ring`, цвет `#FFB52A`, 3 на цикл:
  - уходят на 6 назад, Size ×0.5 → ×2.0, вращаются 360° за цикл;
  - Transparency 0.2 → 1.
- Лучи-иглы — Neon-конус (как `fx_sun_ray`, длина 1.0, остриём назад), `#FFD24A`, 6 на цикл: летят назад на 12, расходятся до ±0.9, Size 0 → ×1.2 → 0.
- PointLight `#FFC23A`, Brightness 2, Range 9.

**FX_Impact** (1.5 с) — «взрыв солнца»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.37 | вспышка-сфера r 0.5 → 1.6, гаснет | Neon-шар `#FFD868`, Transparency 0.5 → 1, Tween 0.37 с |
| 0–0.43 | золотое кольцо по земле до r 2.5, гаснет | Neon-тор `#FFB52A`, Tween Size и Transparency 0 → 1, Quad Out |
| 0.03–0.8 | 18 тонких лучей (длинных 3.6 и коротких 2.4, чередуются, шаг 20°) выстреливают горизонтально от точки касания: вытягиваются за 0.1 с, держатся, сужаются и гаснут к 0.8 с | меш `fx_sun_ray` (тонкий конус r 0.06–0.07), Neon `#FFD24A` / `#FFF0A8`, Tween Size по длине (Back Out), Transparency 0 → 1 |
| 0–1.2 | солнечный диск r 1.0 поднимается за копьём с высоты 0.3 до 3.4, растёт до ×1.5 и гаснет; поверх него гало r 1.5 | меш `fx_sun_disc` (диск вертикально, нормаль вдоль Y), Neon `#FFD24A`; гало — Neon-шар `#FFD868`, Transparency 0.5 → 1 |
| 0.03–1.0 | 8 коротких лучей (длина 0.6) расходятся вокруг диска и поднимаются вместе с ним | меш `fx_sun_ray`, Neon `#FFF0A8`, Tween CFrame |
| 0.17–1.3 | огненное кольцо: 12 языков пламени высотой 0.95 по кругу r 1.55 (шаг 30°) загораются по очереди, мерцают ×1.0 → ×1.35, к концу тлеют до ×0.5 | меш `fx_fire_ring_flame`, Neon `#FF6A1A` / `#FFC23A` поочерёдно, Tween Size по Y |
| 0–0.9 | 10 золотых искр летят по дуге и гаснут | меш-шарик r 0.06 или ParticleEmitter Burst 10: `#FFD24A` / `#FFF0A8`, Size 0.12, Speed 5–9, Acceleration (0, −27, 0), Lifetime 0.87, LightEmission 1 |
| 1.1–1.33 | пламя гаснет | Tween Size → 0 |

Свет: PointLight `#FFC23A`, Brightness 4 → 0 за 0.8 с, Range 11.

---

## 13 canyon_hook — Canyon Hook (shards)

Меши для пересборки (`FX_EXPORT`, имена GLB `sp_13_canyon_hook_fx_<суффикс>.glb`): `mesa` (ступенчатый столб), `mesa_cap` (плита-шапка), `chip` (каменный осколок), `shock_ring` (плоское кольцо), `dust_ring` (воздушное кольцо).

**FX_Idle** — песчинки и блики у крюка:
- ParticleEmitter на Tip:
  - цвет `#E8956A` → `#B04A34`;
  - Size 0.05–0.09, Transparency 0.3 → 1;
  - Rate 5, Lifetime 1.4 с, Speed 0.2, SpreadAngle 180, Acceleration (0, 0.25, 0).
  - Зона: радиус 0.5–0.95 вокруг оси, высота 6.8–9.2 по древку.
- ParticleEmitter бликов:
  - Texture «звёздочка», цвет `#FFE2A8`, Size 0.13;
  - Rate 1.5, Lifetime 0.4 с, LightEmission 1.
- PointLight не нужен.

**FX_Flight** (цикл 1 с):
- Красная пыль — ParticleEmitter на TrailRoot:
  - цвета `#E8956A` / `#B04A34`;
  - Size NumberSequence 0.4 → 1.5 → 0, Transparency 0.15 → 1;
  - Rate 10, Lifetime 1 с, EmissionDirection назад, Speed 2–4, SpreadAngle 25, Drag 2.
- Каменные осколки — ParticleEmitter с текстурой «камень»:
  - цвета `#C4492F`, `#E6B87A`, `#E08A3C` поочерёдно;
  - Size 0.2, Rate 10, Lifetime 0.9 с, RotSpeed ±360, Speed 3–5.
- Острые сколы — меш-осколок 4-гранный (Neon `#C4492F` / `#7A2E24` поочерёдно), Size 0.3:
  - 6 штук за цикл, кувыркаются (540° и 360°);
  - уходят на 12 назад и в стороны до 1.0.
- Воздушные кольца — меш `fx_dust_ring`, Neon `#FFC88A`, 3 на цикл:
  - появляются у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад вдоль древка, растут до ×2.0;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «столбы каньона вырастают кольцом»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.5, гаснет | Neon-шар `#FFD8A0`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.6, гаснет | меш `fx_shock_ring`, Neon `#FFB877`, Tween Size и Transparency 0 → 1, Quad Out |
| 0–0.13 | вмятина-валик r 0.9 вырастает до плоского кольца высотой ×0.45 | торус `#7A2E24`, Tween Size (Back Out); держится до 1.13 с |
| 0.0–0.17 … 0.17–0.33 | 6 ступенчатых столбов-мез (r 0.4, высота 1.1–1.6) вырастают кольцом r 1.6 / 1.95 вокруг копья, углы −125…128° (за копьём пусто); каждый на 0.033 с позже предыдущего | меш `fx_mesa`, цвета `#C4492F` и `#E08A3C` поочерёдно, Tween Size по высоте от 0, Back Out 0.17 с |
| та же | на вершине каждого столба поднимается плита-шапка | меш `fx_mesa_cap`, цвет `#E6B87A`, поднимается вместе с вершиной |
| 0.1–0.4 | 5 малых ступенчатых блоков (r 0.26, высота 0.45–0.72) на r 2.6 | меш `fx_mesa`, цвета `#E6B87A` / `#C4492F` |
| 0–0.13 | 5–6 тёмных трещин длиной 0.9–1.5 расходятся по земле | узкие Part `#7A2E24` у поверхности, Tween длины |
| 0–1.33 | 12 клубов красной пыли разлетаются кольцом на 1.4–2.6 и растут до ×2.8 | ParticleEmitter Burst 12: цвета `#E8956A` / `#B04A34`, Size 0.4 → 2.5, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 0–1.1 | 14 каменных осколков и 4 валуна летят по дуге перед копьём и ложатся на землю | Burst 14 + 4: меш `fx_chip`, Size 0.16–0.28 (валуны 0.35–0.5), Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 1.13–1.33 | столбы, шапки, трещины, камни схлопываются | Tween Size → 0 |

Свет: PointLight `#FFB877`, Brightness 2 → 0 за 0.4 с, Range 7.

---

## 14 condor_quill — Condor Quill (feathers)

Меши для пересборки (`FX_EXPORT`, GLB `sp_14_condor_quill_fx_<суффикс>.glb`): `feather` (перо-лист), `wind_ring` (кольцо ветра), `shock_ring` (плоское кольцо), `puff` (шар облачка).

**FX_Idle** — оброненные перья и блики:
- ParticleEmitter на Tip:
  - Texture «перо», цвета `#FFFFFF` / `#2C2A36` / `#C9602F`;
  - Size 0.12–0.25, Rate 3, Lifetime 2 с, RotSpeed ±60;
  - Speed 0.1, SpreadAngle 180, Acceleration (0, −0.15, 0) — перья медленно планируют вниз.
  - Зона: радиус 0.6–1.0, высота 6.9–9.2 по древку.
- Блики: Texture «звёздочка», цвет `#FFF2C8`, Size 0.13, Rate 1.5, Lifetime 0.4 с, LightEmission 1.

**FX_Flight** (цикл 1 с):
- Перья — меш `fx_feather` (цвета `#2C2A36`, `#FFFFFF`, `#C9602F` поочерёдно), Size 0.55 × 0.2:
  - 14 штук за цикл, кувыркаются (360° и 200°);
  - уходят на 12.5 назад и в стороны до 1.3.
- Облачка воздуха — ParticleEmitter на TrailRoot:
  - цвета `#FFF4E4` / `#D6A77A`;
  - Size 0.35 → 1.5 → 0, Transparency 0.15 → 1;
  - Rate 8, Lifetime 1 с, EmissionDirection назад, Speed 2–4, Drag 2.
- Кольца ветра — меш `fx_wind_ring`, Neon `#BFEAFF`, 3 на цикл:
  - появляются у острия со Size ×0.6, уходят на 6.5 назад вдоль древка;
  - растут до ×2.1, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «восходящий поток»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.5, гаснет | Neon-шар `#FFF0D0`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#BFEAFF`, Tween Size и Transparency 0 → 1 |
| 0.07–1.33 | полупрозрачный столб воздуха r 0.8 × высота 3.2 растёт и гаснет | Neon-цилиндр `#DFF4FF`, Transparency 0.88 → 1 (очень слабый) |
| 0–1.33 | 18 перьев закручиваются спиралью вверх на 3.2: радиус 0.35 → 1.0, 1.45 оборота; 6 волн по 3 пера, каждая волна на 0.067 с позже предыдущей (старты 0–0.33 с) | меш `fx_feather` (`#2C2A36` / `#FFFFFF` / `#C9602F`), Size 0.6 × 0.2; движение по формуле винта в Heartbeat либо ParticleEmitter с текстурой пера: Speed 3, Acceleration (0, 1, 0), RotSpeed ±300, VelocityInheritance 0, Lifetime 1.2; на концах Size 0 |
| 0, 0.1, 0.2, 0.3, 0.4 | 5 колец ветра поднимаются стопкой (r 0.45 → 1.4, на высоту 2.0–3.0), гаснут за 0.87 с | меш `fx_wind_ring`, Neon `#BFEAFF`, Tween Position Y и Size, Transparency 0 → 1 |
| 0–1.33 | 10 клубов светлой пыли разлетаются по земле на 1.2–2.3 и растут до ×2.5 | ParticleEmitter Burst 10: цвета `#FFF4E4` / `#D6A77A`, Size 0.4 → 2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 0–1.33 | 10 золотистых искорок взлетают по спирали до высоты 3 | Burst 10: цвет `#FFF2C8`, Size 0.14, LightEmission 1, Lifetime 1.2, Acceleration (0, 2, 0) |
| 1.13–1.33 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#BFEAFF`, Brightness 1.5 → 0 за 0.5 с, Range 7.

---

## 15 mirage_lance — Mirage Lance (crystal)

Меши для пересборки (`FX_EXPORT`, GLB `sp_15_mirage_lance_fx_<суффикс>.glb`): `mirror` (призма-зеркало 6 граней, h 2.0), `heat_ring` (тонкое кольцо), `glitter` (4-лучевая звёздочка), `shard` (двойной осколок кристалла).

**FX_Idle** — мерцание кристалла:
- ParticleEmitter на Tip:
  - Texture «звёздочка», цвет `#FFFBE0`, Size 0.12–0.18;
  - Rate 3, Lifetime 0.5 с, LightEmission 1.
- ParticleEmitter песчинок:
  - цвета `#F6E2B4` / `#D8AB6A`, Size 0.05–0.09, Transparency 0.3 → 1;
  - Rate 4, Lifetime 1.5 с, Speed 0.2, Acceleration (0, 0.2, 0).
  - Зона: радиус 0.55–0.9, высота 7.0–9.4.
- Тонкое кольцо жара вокруг кристалла: меш `fx_heat_ring`, цвет `#FFD9A0`, Transparency 0.7, r 0.55 на высоте 7.0.
- PointLight `#A8F0FF`, Brightness 0.6, Range 4.

**FX_Flight** (цикл 1 с):
- Осколки кристалла — меш `fx_shard` (Neon `#A8ECFF` и `#5E7FD0` поочерёдно), Size 0.34:
  - 8 штук за цикл, кувыркаются (540° и 360°);
  - уходят на 12 назад и в стороны до 1.2.
- Песчаные клубы — ParticleEmitter на TrailRoot:
  - цвета `#F6E2B4` / `#D8AB6A`;
  - Size 0.35 → 1.5 → 0, Transparency 0.15 → 1;
  - Rate 10, Lifetime 1 с, EmissionDirection назад, Speed 2–4, Drag 2.
- Кольца марева — меш `fx_heat_ring`, цвет `#FFD9A0`, Transparency 0.5, 3 на цикл:
  - стартуют у острия, Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.1, Transparency 0.5 → 1.
- Блики — 6 штук, ParticleEmitter «звёздочка», цвет `#FFFBE0`, Size 0.14, Rate 6, Lifetime 0.5 с, LightEmission 1.

**FX_Impact** (1.5 с) — «мираж»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.5, гаснет | Neon-шар `#FFFBE8`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_heat_ring`, Neon `#A8F0FF`, Tween Size и Transparency 0 → 1 |
| 0–0.13 | песчаный холм вздувается до ×1.6 и оседает | меш-диск `#F2DFB4` |
| 0 / 0.1 / 0.2 → 1.33 | 3 прозрачные копии кристалла (высота 2.0) вспыхивают вокруг копья — углы −55°, 45°, 125°, r 1.4 / 1.7 / 1.4; мигают: Transparency 0.1 → 0.9 → 0.1 → 0.85 → 0.2 → 1 (через 0.1, 0.23, 0.33, 0.5, 0.63 с после появления), к 1.33 гаснут | меш `fx_mirror`, Neon `#B8F2FF` (Transparency 0.4–0.9, мерцание Tween); у каждой своя задержка 0.1 с |
| 0.07–0.33 | 5 малых кристаллов прорастают из песка (высота 0.5) | меш `fx_shard`, Neon `#A8ECFF` / `#5E7FD0`, Tween Size от 0 |
| 0, 0.13, 0.27, 0.4 | 4 кольца марева расходятся до r 2.9 / 2.7 / 2.4 / 2.1 и гаснут (0.67 с) | меш `fx_heat_ring`, цвет `#FFD9A0`, Transparency 0.5 → 1, Tween Size |
| 0–0.9 | 22 песчаные блёстки взлетают по дуге (до 1.5) и мерцают | Burst 22: меш `fx_glitter`, Neon `#FFFBE0`, Size 0.14–0.28, Speed 5–8 вверх, Acceleration (0, −22, 0), Lifetime 1.0 |
| 0–1.33 | 10 песчаных клубов разлетаются на 1.3–2.4, растут до ×2.6 | ParticleEmitter Burst 10: цвета `#F6E2B4` / `#D8AB6A`, Size 0.4 → 2.2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 1.13–1.33 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#B8F2FF`, Brightness 2.5 → 0 за 0.6 с, Range 8.

---

## 16 scorpion_sting — Scorpion Sting (shards)

Меши для пересборки (`FX_EXPORT`, GLB `sp_16_scorpion_sting_fx_<суффикс>.glb`): `claw` (изогнутый коготь h 2.05), `venom_drop` (капля яда), `crack` (зигзаг-трещина), `shock_ring` (плоское кольцо).

**FX_Idle** — капли яда у жала:
- ParticleEmitter на Tip:
  - цвет `#9BE848`, Size 0.08–0.16, LightEmission 1;
  - Rate 4, Lifetime 1.2 с, Speed 0.2, Acceleration (0, −0.4, 0) — капли медленно падают.
  - Зона: радиус 0.5–0.9, высота 7.2–9.3.
- Блики: Texture «звёздочка», цвет `#D8FF9A`, Size 0.13, Rate 1.5, Lifetime 0.4 с, LightEmission 1.
- PointLight `#9BE848`, Brightness 0.5, Range 4.

**FX_Flight** (цикл 1 с):
- Песчаные клубы — ParticleEmitter на TrailRoot:
  - цвета `#F2DBA8` / `#C9A068`;
  - Size 0.35 → 1.5 → 0, Transparency 0.15 → 1;
  - Rate 8, Lifetime 1 с, EmissionDirection назад, Speed 2–4, Drag 2.
- Хитиновые осколки — 4-гранные меши (`#3B2A24` / `#B07A48` поочерёдно), Size 0.36:
  - 8 штук за цикл, кувыркаются (540° и 360°);
  - уходят на 12 назад и в стороны до 1.35.
- Капли яда — ParticleEmitter Neon `#9BE848`, Size 0.16, Rate 10, Lifetime 0.9 с, Speed 3, SpreadAngle 25, EmissionDirection назад.
- Кольца — меш-кольцо, Neon `#C2F07A`, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «земля раскалывается, клешни смыкаются»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#F2FFB8`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#E8FFB0`, Tween Size и Transparency 0 → 1 |
| 0–0.17 | 5 трещин длиной 1.4–2.3 расходятся по земле веером (за копьём пусто); по каждой — тонкая зелёная жила | меш `fx_crack` `#3B2A24` + жила Neon `#9BE848` (шире — тёмная, уже — светящаяся), Tween длины; жила загорается за 0.13–0.33 и гаснет к 1.33 |
| 0–0.13 | песчаный бугор вздувается до ×1.5 | меш-диск `#B07A48` |
| 0.03–0.2 | 2 когтя (по бокам, y = ±0.95, высота ~2) вырастают, раскрытые наружу на 38° | меш `fx_claw`, цвета `#3B2A24` / `#B07A48`, Tween Size от 0 |
| 0.37–0.47 | клешни смыкаются: наклон с −38° на +26° за 0.1 с — острия клешней сходятся и перекрещиваются над точкой удара на высоте ~1.8; там вспыхивают два зелёных шарика r 0.09 (до 0.57 с, держатся до 1.0) | Tween CFrame, Linear; шарик Neon `#9BE848` |
| 0–1.33 | 10 клубов песка разлетаются на 1.3–2.4 и растут до ×2.6 | ParticleEmitter Burst 10: цвета `#F2DBA8` / `#C9A068`, Size 0.4 → 2.2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 0–1.1 | 14 капель яда летят по дуге и падают перед копьём | Burst 14: меш `fx_venom_drop`, Neon `#9BE848`, Size 0.12–0.2, Speed 6–11 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0–1.1 | 6 каменных осколков летят по дуге | Burst 6: Size 0.16–0.28, Speed 6–9, Acceleration (0, −25, 0), Lifetime 1.1 |
| 1.13–1.33 | коготь, трещины, камни схлопываются | Tween Size → 0 |

Свет: PointLight `#9BE848`, Brightness 2 → 0 за 0.5 с, Range 7.

---

## 17 emerald_vine — Emerald Vine (crystal)

Меши для пересборки (`FX_EXPORT`, GLB `sp_17_emerald_vine_fx_<суффикс>.glb`): `vine` (завиток лозы, h 1.35), `leaf` (лист 0.5 × 0.22), `bud` (изумрудный бутон h 0.4), `shock_ring` (плоское кольцо).

**FX_Idle** — споры у клинка:
- ParticleEmitter на Tip:
  - цвет `#B8FF9A`, Size 0.1–0.18, LightEmission 1, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.6 с, Speed 0.2, Acceleration (0, 0.3, 0).
  - Зона: радиус 0.55–0.95, высота 7.0–9.4.
- Блики: Texture «звёздочка», цвет `#F4FFD0`, Size 0.13, Rate 1.5, Lifetime 0.4 с, LightEmission 1.
- PointLight `#7FFFB0`, Brightness 0.5, Range 4.

**FX_Flight** (цикл 1 с):
- Листья — меш `fx_leaf` (`#7BD05A` / `#4C9A3A` поочерёдно), Size 0.4 × 0.17:
  - 12 штук за цикл, кувыркаются (360° и 240°);
  - уходят на 12.5 назад и в стороны до 1.3.
- Изумрудные осколки — 5-гранные меши Neon `#2FD68A` / `#1A9A6A`, Size 0.34:
  - 8 штук за цикл, кувыркаются (540° и 360°);
  - уходят на 12 назад и в стороны до 1.25.
- Зелёная дымка — ParticleEmitter на TrailRoot:
  - цвета `#D2F8BC` / `#7EC06A`;
  - Size 0.35 → 1.5 → 0, Transparency 0.2 → 1;
  - Rate 6, Lifetime 1 с, EmissionDirection назад, Speed 2–4, Drag 2.
- Кольца — меш-кольцо, Neon `#A8F08A`, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «лозы прорастают»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#E4FFC8`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#C8FF9A`, Tween Size и Transparency 0 → 1 |
| 0–0.4 | 6 лоз-завитков (высота 1.35, толщина 0.1 → 0) вырастают вокруг копья: углы −115°…135°, r 1.3 / 1.7; каждая на 0.033 с позже предыдущей, рост 0.23 с | меш `fx_vine` `#4C9A3A`, Tween Size от 0 (Back Out), каждая повёрнута завитком вбок |
| 0.2–0.57 | на каждой лозе распускаются 2 листа (размер 0.5) | меш `fx_leaf` `#7BD05A`, Tween Size 0 → 1 за 0.13 с |
| 0.27–0.63 | на конце каждой лозы выскакивает изумрудный бутон (h 0.4): Size 0 → 1.3 → 1.0 | меш `fx_bud`, цвета `#2FD68A` / `#1A9A6A` поочерёдно |
| 0–1.1 | 10 листьев разлетаются по дуге и падают | Burst 10: меш `fx_leaf`, Size 0.2–0.3, Speed 5–9 вверх, Acceleration (0, −17, 0), RotSpeed ±300, Lifetime 1.1 |
| 0–1.33 | 10 зелёных спор взлетают по спирали до высоты 2.4 | Burst 10: цвет `#B8FF9A`, Size 0.14, LightEmission 1, Lifetime 1.2, Acceleration (0, 1.5, 0) |
| 0–1.33 | 10 клубов дымки разлетаются на 1.3–2.3, растут до ×2.6 | ParticleEmitter Burst 10: цвета `#D2F8BC` / `#7EC06A`, Size 0.4 → 2.2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 1.13–1.33 | лозы, листья и бутоны схлопываются | Tween Size → 0 |

Свет: PointLight `#7FFFB0`, Brightness 2 → 0 за 0.5 с, Range 7.

---

## 18 temple_guard — Temple Guard (sparks)

Меши для пересборки (`FX_EXPORT`, GLB `sp_18_temple_guard_fx_<суффикс>.glb`): `pillar` (квадратный столб h 1.3 с капителью), `glyph` (плоская плитка-руна 0.3 × 0.12), `spark` (шарик-искра), `shock_ring` (плоское кольцо).

**FX_Idle** — золотые искры и блики у алебарды:
- ParticleEmitter на Tip:
  - цвет `#FFD24A`, Size 0.08–0.15, LightEmission 1;
  - Rate 5, Lifetime 1.3 с, Speed 0.3, SpreadAngle 180, Acceleration (0, 0.3, 0).
  - Зона: радиус 0.5–1.0, высота 7.0–9.3.
- Блики: Texture «звёздочка», цвет `#FFF2B0`, Size 0.13, Rate 1.5, Lifetime 0.4 с, LightEmission 1.
- PointLight `#FFD24A` у глаз маски (Attachment на сокете), Brightness 0.5, Range 3.

**FX_Flight** (цикл 1 с):
- Золотые искры — ParticleEmitter на TrailRoot:
  - цвет `#FFD24A`, Size 0.12, LightEmission 1;
  - Rate 12, Lifetime 0.9 с, EmissionDirection назад, Speed 3–5, SpreadAngle 30.
- Каменные осколки — Texture «камень», цвета `#B9AD8E` / `#7D7360`:
  - Size 0.18, Rate 8, Lifetime 0.9 с, RotSpeed ±360, Speed 3–5.
- Руны — меш-звёздочка 4-лучевая, Neon `#FFD24A`, Size 0.3, 6 штук за цикл:
  - вращаются вокруг оси движения (360°);
  - уходят на 12 назад и в стороны до 1.2.
- Кольца — меш-кольцо, Neon `#FFD24A`, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «кольцо глифов»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#FFF0B0`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#FFD24A`, Tween Size и Transparency 0 → 1 |
| 0–0.17 | каменное кольцо r 1.8 (толщина 0.1, плоское) проявляется вокруг копья; держится до 1.33 | торус `#7D7360`, Tween Size от 0 |
| 0.07–0.27 | внутреннее золотое кольцо r 1.15 загорается; гаснет к 1.33 | торус Neon `#FFD24A`, Transparency 1 → 0 → 1 |
| 0.1–0.47 | 8 глифов-плиток по кольцу r 1.48 вспыхивают один за другим (интервал 0.033 с), Size 0 → 1.2 → 1.0 | меш `fx_glyph`, Neon `#FFD24A`, Transparency 0 → 1 к 1.33 |
| 0.13–0.53 | 4 руны-столба вырастают на кольце r 1.8 (углы −110°, −40°, 40°, 110°), высота 1.3; интервал 0.067 с, рост 0.2 с | меш `fx_pillar`, цвета `#B9AD8E` / `#7D7360` поочерёдно, Tween Size по высоте от 0 |
| 0.13–1.33 | над каждым столбом всплывает золотая звезда-руна до высоты 1.7–1.9 и гаснет | меш-звезда, Neon `#FFD24A`, Tween Position Y и Transparency |
| 0–1.2 | 24 золотые искры бьют фонтаном вверх до высоты ~3 и падают в радиус 1.5 | ParticleEmitter Burst 24: цвет `#FFD24A`, Size 0.1–0.18, LightEmission 1, Speed 9–14 вверх, SpreadAngle 8, Acceleration (0, −25, 0), Lifetime 1.0 |
| 0–1.33 | 8 клубов каменной пыли разлетаются на 1.3–2.4, растут до ×2.5 | ParticleEmitter Burst 8: цвета `#E6DCC0` / `#B0A48A`, Size 0.4 → 2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 0–1.1 | 6 каменных осколков летят по дуге | Burst 6: Size 0.16–0.28, Speed 6–9, Acceleration (0, −25, 0), Lifetime 1.1 |
| 1.13–1.33 | кольцо, столбы и глифы схлопываются | Tween Size → 0 |

Свет: PointLight `#FFD24A`, Brightness 2.5 → 0 за 0.7 с, Range 8.

---

## 19 mangrove_root — Mangrove Root (dust)

Меши для пересборки (`FX_EXPORT`, GLB `sp_19_mangrove_root_fx_<суффикс>.glb`): `root_arch` (дуга-полуэллипс корня, ширина 1.4–1.8, высота 1.2–1.6), `root_spike` (корень-шип h 1.6), `mud_clump` (ком грязи), `moss` (кочка мха).

**FX_Idle** — споры и блики:
- ParticleEmitter на Tip:
  - цвет `#9AFFC8`, Size 0.1–0.18, LightEmission 1, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.6 с, Speed 0.2, Acceleration (0, 0.25, 0).
  - Зона: радиус 0.55–1.0, высота 7.0–9.3.
- Блики: Texture «звёздочка», цвет `#E8FFD0`, Size 0.13, Rate 1.5, Lifetime 0.4 с, LightEmission 1.
- PointLight не нужен.

**FX_Flight** (цикл 1 с):
- Листья мха — ParticleEmitter с текстурой листа, цвета `#62A03C` / `#9AD260`:
  - Size 0.25, Rate 10, Lifetime 0.9 с, RotSpeed ±300, Speed 3–5, EmissionDirection назад.
- Щепки корня — Texture «камень/щепка», цвета `#7C502E` / `#4A301F`:
  - Size 0.18, Rate 8, Lifetime 0.9 с, RotSpeed ±360, Speed 3–5.
- Грязевая дымка — ParticleEmitter на TrailRoot:
  - цвета `#B49A74` / `#6E5638`;
  - Size 0.35 → 1.5 → 0, Transparency 0.15 → 1;
  - Rate 8, Lifetime 1 с, Speed 2–4, Drag 2.
- Кольца — меш-кольцо, Neon `#B8FFD8`, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «корни прорывают землю»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#E8D4A8`, Transparency 0.35 → 1, Tween 0.33 с |
| 0–0.2 | грязевой вал: кольцо r 0.6 расходится до r ~1.9 (потом до 2.2), плоское | торус `#5B4632`, Tween Size (Quad Out); держится до 1.07 с |
| 0–0.2, шаг 0.033 | 6 корней-арок (высота 1.2–1.6) прорываются из земли кольцом r 1.5 / 1.9, углы −120°…130°: Size 0 → 1.2 за 0.13 с, затем 1.0 за 0.1 с | меш `fx_root_arch`, цвета `#7C502E` / `#4A301F` поочерёдно, Tween Size (Back Out) |
| 0.03–0.37 | 6 корней-шипов (h 1.6) выстреливают на r 0.9 вокруг копья | меш `fx_root_spike`, цвет `#C0955E`, Tween Size от 0 за 0.17 с |
| 0.13–0.43 | 6 кочек мха вырастают на r 2.0–2.6 | меш `fx_moss`, цвета `#62A03C` / `#9AD260` |
| 0–1.1 | 16 комьев грязи летят по дуге и падают перед копьём | Burst 16: меш `fx_mud_clump`, цвета `#5B4632` / `#4A301F`, Size 0.2–0.4, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0–1.0 | 10 брызг жидкой грязи, мелкие капли | Burst 10: цвет `#5B4632`, Size 0.1–0.18, Speed 7–11 вверх, Acceleration (0, −25, 0), Lifetime 1.0 |
| 0–1.33 | 10 клубов коричневой пыли разлетаются на 1.3–2.4, растут до ×2.6 | ParticleEmitter Burst 10: цвета `#B49A74` / `#6E5638`, Size 0.4 → 2.2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 1.13–1.33 | арки, шипы, мох и комья схлопываются | Tween Size → 0 |

Свет: PointLight не нужен.

---

## 20 hydra_fangs — Hydra Fangs (shards)

Меши для пересборки (`FX_EXPORT`, GLB `sp_20_hydra_fangs_fx_<суффикс>.glb`): `fang` (изогнутый клык h 2.0), `shard` (двойной осколок), `venom_drop` (капля яда), `shock_ring` (плоское кольцо).

**FX_Idle** — капли яда на клыках:
- ParticleEmitter на Tip:
  - цвет `#A8FF4A`, Size 0.08–0.16, LightEmission 1;
  - Rate 4, Lifetime 1.2 с, Speed 0.2, Acceleration (0, −0.4, 0) — капли стекают вниз.
  - Зона: радиус 0.6–1.0, высота 7.2–9.3.
- Блики: Texture «звёздочка», цвет `#E4FFB8`, Size 0.13, Rate 1.5, Lifetime 0.4 с, LightEmission 1.
- PointLight `#FF5A3A` на глазах змеиной головы (Attachment на сокете), Brightness 0.4, Range 3.

**FX_Flight** (цикл 1 с):
- Осколки клыков — меш `fx_shard` (4-гранный; `#F4F0D8` и `#2F9A5A` поочерёдно), Size 0.36:
  - 10 штук за цикл, кувыркаются (540° и 360°);
  - уходят на 12 назад и в стороны до 1.35.
- Капли яда — ParticleEmitter Neon `#A8FF4A`, Size 0.16, Rate 10, Lifetime 0.9 с, Speed 3, EmissionDirection назад.
- Болотная дымка — ParticleEmitter на TrailRoot:
  - цвета `#C8F0C0` / `#5A8A5A`;
  - Size 0.35 → 1.5 → 0, Transparency 0.2 → 1;
  - Rate 6, Lifetime 1 с, Speed 2–4, Drag 2.
- Кольца — меш-кольцо, Neon `#C2FF80`, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «клыки выпрыгивают крестом»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#E0FFB0`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#C8FF80`, Tween Size и Transparency 0 → 1 |
| 0 → 0.1 | клык 1 (база 0.15 впереди копья, наклон вперёд) выпрыгивает: Size 0 → ×1.18 за 0.1 с, оседает до ×1.0 за 0.23 с | меш `fx_fang` `#F4F0D8`, Tween Size (Back Out) |
| 0.07 → 0.17 | клык 2 (база 1.55 впереди, наклон назад) — то же; клыки перекрещиваются в X на высоте ~1 | тот же меш, зеркально по X |
| 0–0.17 | у основания каждого клыка тёмная яма r 0.34 | плоский шар `#1C6A40` (Size Y ×0.12) |
| 0.13–0.33 | на клыках загорается зелёная жила | Neon-полоска `#A8FF4A`, Transparency 1 → 0 → 1 к 1.33 |
| 0–0.2 | 5 трещин длиной 1.3–2.2 расходятся от клыков | узкие Part `#1C6A40`, Tween длины |
| 0.1–0.4 | 6 малых зубов (h 0.55) вырастают на r 1.9–2.5 вокруг | меш-конус `#F4F0D8`, Tween Size от 0 |
| 0–1.0 | 24 зелёных осколка бьют веером и падают на землю | Burst 24: меш `fx_shard` (`#2F9A5A` / `#F4F0D8`), Size 0.12–0.22, Speed 6–10 вверх, SpreadAngle 70, Acceleration (0, −25, 0), RotSpeed ±360, Lifetime 1.0 |
| 0–1.0 | 10 капель яда | Burst 10: меш `fx_venom_drop`, Neon `#A8FF4A`, Size 0.1–0.18, Speed 7–11, Acceleration (0, −25, 0), Lifetime 1.0 |
| 0–1.33 | 8 клубов болотной дымки разлетаются на 1.3–2.4, растут до ×2.6 | ParticleEmitter Burst 8: цвета `#C8F0C0` / `#5A8A5A`, Size 0.4 → 2.2, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 1.13–1.33 | клыки, ямы, зубы и осколки схлопываются | Tween Size → 0 |

Свет: PointLight `#A8FF4A`, Brightness 2 → 0 за 0.5 с, Range 7.

---

## 21 storm_trident — Storm Fork (sparks)

Меши для пересборки (`FX_EXPORT`, GLB `sp_21_storm_trident_fx_<суффикс>.glb`): `bolt` (зигзаг-молния высотой 6), `bolt_halo` (та же молния, толще, для ореола), `elec_ring` (плоское кольцо), `spark` (шарик-искра), `zig` (короткая зигзаг-молния длиной 0.55 для полёта).

**FX_Idle** — искрение между зубцами:
- ParticleEmitter на Tip:
  - цвета `#FFE45A` / `#9A6CFF`, Size 0.08–0.15, LightEmission 1;
  - Rate 6, Lifetime 0.6 с, Speed 0.4, SpreadAngle 180.
  - Зона: радиус 0.4–0.9, высота 7.2–9.3.
- Блики: Texture «звёздочка», цвет `#FFE45A`, Size 0.14, Rate 2, Lifetime 0.3 с, LightEmission 1.
- PointLight `#9A6CFF`, Brightness 0.6, Range 4, мерцает (Brightness 0.3 ↔ 0.8 раз в 0.2 с).

**FX_Flight** (цикл 1 с):
- Грозовые клочья — ParticleEmitter на TrailRoot:
  - цвета `#D2D2EC` / `#6A6884`;
  - Size 0.35 → 1.5 → 0, Transparency 0.15 → 1;
  - Rate 8, Lifetime 1 с, EmissionDirection назад, Speed 2–4, Drag 2.
- Искры — ParticleEmitter Neon `#FFE45A` / `#9A6CFF`, Size 0.12, Rate 12, Lifetime 0.9 с, Speed 3–5, SpreadAngle 30.
- Короткие молнии — меш `fx_zig` (длина 0.55), Neon `#FFE45A` / `#9A6CFF`:
  - 6 штук за цикл, вращаются (360° и 180°);
  - уходят на 12 назад и в стороны до 1.2.
- Кольца — меш `fx_elec_ring`, Neon `#FFE45A` / `#9A6CFF`, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «три удара молний»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.5, гаснет | Neon-шар `#FFF6C0`, Transparency 0.3 → 1, Tween 0.33 с |
| 0 / 0.1 / 0.2 | 3 молнии бьют с высоты 6 в землю вокруг копья: углы −60°, 50°, 125°, r 1.4 / 1.7 / 1.4 (ядро r 0.045, ореол r 0.17); появляются мгновенно за 0.033 с | меш `fx_bolt` Neon `#FFE45A` + `fx_bolt_halo` Neon `#9A6CFF`; Tween не нужен — просто Transparency 1 → 0 |
| +0.1, +0.13, +0.23, +0.4 (от каждого удара) | мерцание: Transparency 0.8 → 0 → 0.1 → 0.9 → 1, всего 0.43 с | Heartbeat-таймер или Tween Transparency |
| у каждого удара | вспышка в точке удара: сфера r 0.5 → 0.7, гаснет за 0.3 с | Neon-шар `#FFF2A0`, Transparency 0.2 → 1 |
| у каждого удара | подпалина — плоский диск r 0.45 | цилиндр `#3D3B58`, Size 0 → 1 за 0.1 с, держится до 1.33 |
| 0 и 0.13 | два электрических кольца от r 0.18 до 2.8 и 2.4, гаснут за 0.47 с | меш `fx_elec_ring`, Neon `#FFE45A` и `#9A6CFF`, Tween Size и Transparency 0 → 1 |
| 0.1–0.33 (шаг 0.03–0.1) | 6 мелких дуг по кольцу r 1.3 (дуги не там, где древко) мигают по очереди | короткие Part-зигзаги или меш `fx_zig` Neon `#FFE45A`, мерцание Transparency |
| 0–1.0 | 20 искр взлетают из точек ударов (по 6–7 на каждую) и падают в радиусе ~1.5 | Burst 20: меш `fx_spark`, Neon `#FFE45A` / `#9A6CFF`, Size 0.1–0.16, Speed 5–10 вверх, Acceleration (0, −25, 0), Lifetime 1.0 |
| 0.1–1.33 | 6 клубов дыма растут до ×2.5 и поднимаются на 0.6–1.2 | ParticleEmitter Burst 6: цвета `#6A6884` / `#D2D2EC`, Size 0.4 → 2.2, Transparency 0.2 → 1, Lifetime 1.2, Speed 2 |
| 1.0–1.33 | подпалины и остатки схлопываются | Tween Size → 0 |

Свет: PointLight `#FFE45A`, мерцает 3 раза (на каждом ударе Brightness 4 → 0 за 0.2 с), Range 9.

---

## 22 thunder_split — Thunder Split (sparks)

Меши для пересборки (`FX_EXPORT`, GLB `sp_22_thunder_split_fx_<суффикс>.glb`): `crack` (зигзаг-трещина длиной 3.1, тёмная корка), `crack_core` (она же тоньше, светящаяся жила), `arc` (дуга-молния между точками трещины), `shock_ring` (плоское кольцо), `zig` (короткая зигзаг-молния длиной 0.6 для полёта).

**FX_Idle** — треск вокруг зигзага:
- ParticleEmitter на Tip:
  - цвета `#FFF27A` / `#7A9CFF`, Size 0.08–0.15, LightEmission 1;
  - Rate 6, Lifetime 0.6 с, Speed 0.4, SpreadAngle 180.
  - Зона: радиус 0.5–1.0, высота 7.2–9.3.
- Блики: Texture «звёздочка», цвет `#FFF27A`, Size 0.14, Rate 2, Lifetime 0.3 с, LightEmission 1.
- PointLight `#FFD93A`, Brightness 0.6, Range 4, мерцает.

**FX_Flight** (цикл 1 с):
- Мини-молнии — меш `fx_zig` (длина 0.6), Neon `#FFF27A` / `#7A9CFF` поочерёдно:
  - 10 штук за цикл, вращаются (360° и 180°);
  - уходят на 12.5 назад и в стороны до 1.3.
- Искры — ParticleEmitter Neon `#FFF27A` / `#7A9CFF`, Size 0.12, Rate 12, Lifetime 0.9 с, Speed 3–5, SpreadAngle 30, EmissionDirection назад.
- Кольца — меш `fx_shock_ring`, Neon `#7A9CFF` / `#FFF27A` поочерёдно, 3 на цикл:
  - стартуют у острия со Size ×0.6;
  - за 1 с уходят на 6.5 назад, растут до ×2.0, Transparency 0.2 → 1.
- Блики — Texture «звёздочка», цвет `#FFF27A`, Size 0.14, Rate 5, Lifetime 0.5 с, LightEmission 1.

**FX_Impact** (1.5 с) — «молния раскалывает землю»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.5, гаснет | Neon-шар `#FFF8C8`, Transparency 0.3 → 1, Tween 0.33 с |
| 0–0.4 | ударное кольцо от r 0.15 до 2.5, гаснет | меш `fx_shock_ring`, Neon `#FFF27A`, Tween Size и Transparency 0 → 1 |
| 0–0.27 | главная трещина длиной 3.1 бежит вперёд (+X) от копья за 0.27 с; корка r 0.2 → 0.06 | меш `fx_crack` `#27306E`, Tween Size по длине (Quad Out) |
| 0.07–0.33 и 0.13–0.4 | две боковые трещины длиной 2.0 под ±32° | тот же меш, короче |
| вместе с трещиной | в каждой горит светящаяся жила (толщина 0.45 от корки), гаснет к 1.33 | меш `fx_crack_core`, Neon `#FFF27A`, Transparency 0 → 1 с 1.0 с |
| 0–0.43 | шар-вспышка r 0.18 бежит вперёд по трещине до 3.1 | Neon-шар `#FFF8C8`, Tween Position за 0.27 с, потом гаснет |
| 0.07, 0.13, 0.2, 0.27, 0.33, 0.4 | 6 дуг-молний по очереди перескакивают через куски трещины (длина ~0.7, высота до 0.55), каждая мигает 0.37 с | меш `fx_arc`, Neon `#FFF27A` / `#7A9CFF` поочерёдно, мерцание Transparency |
| 0.07–1.0 | 18 искр взлетают вдоль трещины и падают | Burst 18: Neon `#FFF27A` / `#7A9CFF`, Size 0.1–0.16, Speed 4–9 вверх, Acceleration (0, −25, 0), Lifetime 1.0 |
| 0–1.1 | 8 кусков тёмного камня разлетаются по дуге | Burst 8: цвета `#27306E` / `#4452A8`, Size 0.16–0.28, Speed 6–10, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0.1–0.3 | 6 тёмных кристаллов-осколков (h 0.45) торчат вдоль трещины | 4-гранный меш `#4452A8`, Tween Size от 0 |
| 0.1–1.33 | 5 клубов дыма растут до ×2.5 | ParticleEmitter Burst 5: цвет `#68709A`, Size 0.4 → 2.2, Transparency 0.2 → 1, Lifetime 1.2, Speed 2 |
| 1.0–1.33 | трещины, кристаллы и камни схлопываются | Tween Size → 0 |

Свет: PointLight `#FFD93A`, Brightness 3 → 0 за 0.5 с, Range 9.

---

## 23 coral_branch — Coral Branch (crystal)

**FX_Idle** — пузырьки и розовые блики:
- ParticleEmitter на Tip:
  - Texture «пузырь с ободком», цвет `#DFFBFF`;
  - Size 0.1–0.2, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.5 с, Acceleration (0, 0.8, 0).
- Блики: цвет `#FF9FB6`, Size 0.15, Rate 2, LightEmission 1.
- PointLight `#7FF6FF`, Brightness 0.6, Range 4.

**FX_Flight** (цикл 1 с):
- Пузыри — ParticleEmitter на TrailRoot:
  - Size 0.15 → 0.45 → 0;
  - Rate 16, Lifetime 0.9 с;
  - Speed 3, SpreadAngle 30;
  - лёгкое виляние через RotSpeed / волну.
- Коралловые осколки — меш `fx_shard` (Neon `#FF8FB0` и `#6FE9E0` поочерёдно), Size 0.3:
  - 8 штук за цикл;
  - кувыркаются: 540° по одной оси и 360° по другой;
  - отлетают на 12 назад и в стороны до 1.2.
- Водяные кольца — меш `fx_ripple_ring`, Neon `#7FF6FF`, 3 на цикл:
  - уходят на 7 назад вдоль древка;
  - Size ×0.5 → ×2.1, Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «риф прорастает»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | вспышка-сфера r 0.6 → 1.3, гаснет | Neon-шар `#C8FFFF`, Transparency 0.4 → 1, Tween 0.4 с |
| 0–0.23 | песчаный холм вздувается (×1.7) и оседает | меш `fx_sand_mound`, цвет `#F4DFB6` |
| 0, 0.17, 0.33 | три кольца ряби разбегаются до r 2.5 / 2.2 / 1.9 | меш `fx_ripple_ring`, Neon `#7FF6FF`, каждое 0.53 с, Transparency 0 → 1 |
| 0.07–0.8 | 16 кристаллов прорастают по спирали (золотой угол) от r 0.7 до 3.1 | меш `fx_coral_crystal` (розовые `#FF8FB0`, каждый третий бирюзовый `#6FE9E0`) |
| 0.03–0.4 | 4 коралловые веточки высотой ~1 вырастают у древка | цвет `#FF6F5E`, кончики `#FFC9A6` |
| 0–1.3 | 18 пузырей фонтаном поднимаются на 2.2–3.8 | Burst 18: Size 0.1–0.25, Acceleration (0, 4, 0), Lifetime 0.8 |
| 1.17–1.33 | всё схлопывается | Tween Size → 0 |

Детали к таблице:
- **Кристаллы.** Каждый из 16 стартует на 0.04 с позже предыдущего и наклонён наружу на ~24°. Анимация Size: 0 → 1.15 (0.17 с), затем → 1.0 (0.1 с).
- **Свет.** PointLight `#7FF6FF`: Brightness 3 → 0 за 0.6 с, Range 8.

---

## 24 tide_crest — Tide Crest (ice)

**FX_Idle** — пузырьки и блики на гребне:
- ParticleEmitter на Tip:
  - Texture «пузырь с ободком», цвет `#E2FBFF`;
  - Size 0.1–0.22, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.5 с, Acceleration (0, 0.8, 0), Speed 0.2.
- Блики: цвет `#C8FBFF`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#6FF0FF`, Brightness 0.6, Range 4.

**FX_Flight** (цикл 1 с):
- Брызги-клубы — ParticleEmitter на TrailRoot:
  - цвет `#F2FDFF`, Size 0.3 → 1.4 → 0, Transparency 0.3 → 1;
  - Rate 12, Lifetime 0.9 с, EmissionDirection назад, Speed 3–5, SpreadAngle 25.
- Ледяные хлопья — меш `fx_ice_flake` (Neon `#BFEEFF`), 8 штук за цикл:
  - Size 0.34 по длине;
  - кувыркаются 540° / 360°;
  - отлетают на 12.5 назад, в стороны до 1.35.
- Водяные кольца — меш `fx_water_ring`, Neon `#6FF0FF`, 3 за цикл:
  - уходят на 7 назад вдоль древка, Size ×0.5 → ×2.1;
  - Transparency 0.2 → 1.
- Капли — ParticleEmitter `#6FF0FF`: Size 0.14, Rate 6, Lifetime 0.9 с, Speed 4, LightEmission 1.

**FX_Impact** (1.5 с) — «волна накрывает»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | вспышка-сфера r 0.5 → 1.2, гаснет | Neon-шар `#D8FFFF`, Transparency 0.4 → 1, Tween 0.4 с |
| 0–0.13 | 9 завитков-волн встают дугой r 1.25 перед копьём (углы −84…+84°), старт от центра дуги с шагом 0.03 с | меш `fx_wave_slab` (высота 1.55, завиток внутрь), цвет `#1F7FD6`, Tween Size по Y 0 → 1.15 за 0.2 с (Back Out), у каждого свой CFrame-поворот к центру |
| 0.2–0.4 | волна держится на высоте ~1.5 | пауза |
| 0.4–1.0 | волна обрушивается: Size по Y → 0.45 → 0.08, по X ×1.9, затем исчезает | Tween Size 0.6 с, Quad In |
| 0–1.0 | белые пенные шапки на гребнях волн (9 шаров r 0.2) ныряют к центру вместе с ними | Neon-шар `#F4FCFF`, Tween Position к центру, Size → 0 |
| 0–0.47 | кольцо пены r 0.6 → 1.9 → 2.6 к 1.2 с | меш `fx_foam_ring`, Neon `#F0FFFF`, Transparency 0 → 1 |
| 0, 0.2 | два кольца ряби до r 2.3 / 1.9 за 0.53 с | меш `fx_water_ring`, Neon `#6FF0FF`, Transparency 0 → 1 |
| 0–1.2 | 16 капель разлетаются по дуге | меш `fx_splash` или ParticleEmitter Burst 16: цвета `#6FF0FF` / `#F4FCFF`, Size 0.15–0.25, Speed 7–12, Acceleration (0, −27, 0) |
| 0–1.2 | 10 ледяных хлопьев вылетают и вращаются | меш `fx_ice_flake` (Neon `#BFEEFF`), Size 0.3, Burst Speed 6–12, Acceleration (0, −27, 0) |
| 0.1–1.5 | 6 облачков водяной пыли поднимаются на 1.6–2.6, растут до ×2 | ParticleEmitter Burst 6: `#F2FDFF`, Size 0.5 → 1.8, Transparency 0.3 → 1, Lifetime 1.2 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#6FF0FF`, Brightness 3 → 0 за 0.7 с, Range 8.

---

## 25 abyss_anchor — Abyss Anchor (shards)

**FX_Idle** — бирюзовое свечение и пузырьки:
- Аура — Neon-эллипсоид `#4FFFE0` у головы, Transparency 0.9, Size ~ (2.1, 1.1, 2.1), пульсация ±5% за 1.2 с.
- ParticleEmitter на Tip:
  - Texture «пузырь с ободком», цвет `#D8FBFF`;
  - Size 0.1–0.22, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.6 с, Acceleration (0, 0.8, 0).
- Блики: цвет `#C8FFF4`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#58FFE0`, Brightness 0.8, Range 5.

**FX_Flight** (цикл 1 с):
- Пузыри — ParticleEmitter на TrailRoot:
  - Size 0.15 → 0.4 → 0;
  - Rate 12, Lifetime 0.9 с, Speed 3, SpreadAngle 30.
- Бирюзовые осколки — ParticleEmitter (Texture «осколок»):
  - цвет `#3FAE9C`, Size 0.3, 8 за цикл, RotSpeed ±360;
  - отлетают на 12.5 назад, в стороны до 1.2.
- Звенья цепи — меш `fx_chain_link`, цвет `#53647A`, 5 за цикл:
  - кувыркаются 360° / 200°;
  - отлетают на 12 назад и в стороны до 1.2, Size ×0 → ×1.3 → ×0.
- Водяные кольца — меш `fx_water_ring`, Neon `#58FFE0`, 3 за цикл:
  - уходят на 7 назад вдоль древка, Size ×0.5 → ×2.1;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «глубинный удар»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#C8FFF4`, Transparency 0.3 → 1, Tween 0.4 с |
| 0, 0.1, 0.2 | три ударные волны по земле растут до r 3.0 / 2.4 / 1.8 за 0.47 с | меш `fx_shock_ring`, Neon `#58FFE0`, Transparency 0 → 1, Quad Out |
| 0–0.33 | корона из 12 водяных шипов по кругу r 0.7–0.82, высота 1.2–1.6; вырастают, держатся 0.3 с, оседают к 0.95 с | меш `fx_crown_spike`, цвет `#6FC8EE` (Neon-вид), шаг запуска 0.03 с по 4 группам, Tween Size Back Out |
| 0.03–0.5 | 8 звеньев цепи падают с высоты 2.6–4.2 вокруг копья и 2–3 раза отскакивают (отскок 50%) | меш `fx_chain_link`, цвет `#53647A` / `#2E3A4E`, Tween CFrame по ломаной, затем Size → 0 к 1.33 с |
| 0–1.0 | 12 капель разлетаются по дуге | ParticleEmitter Burst 12: `#6FC8EE`, Size 0.15–0.25, Speed 7–12, Acceleration (0, −27, 0) |
| 0.03–0.8 | 8 пузырей поднимаются на 2.0–3.4 | меш `fx_bubble` или ParticleEmitter Burst 8: `#D8FBFF`, Size 0.15–0.4, Lifetime 0.8 |
| 0.1–1.5 | 5 облачков брызг растут до ×2.2 и тают | ParticleEmitter Burst 5: `#EAFFFF`, Size 0.5 → 1.8, Transparency 0.3 → 1 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#58FFE0`, Brightness 4 → 0 за 0.7 с, Range 9.

---

## 26 leviathan_fang — Leviathan Fang (ice)

**FX_Idle** — морозная аура и снежинки:
- Аура — Neon-эллипсоид `#7FE8FF`, Transparency 0.9, Size ~ (2.1, 1.3, 2.4) вокруг клыка, пульсация ±5% за 1.2 с.
- ParticleEmitter на Tip:
  - Texture «снежинка», цвет `#D8F6FF`;
  - Size 0.1–0.18, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.6 с, Speed 0.2, Acceleration (0, −0.3, 0).
- Блики: цвет `#E6FCFF`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#6FF0FF`, Brightness 0.8, Range 5.

**FX_Flight** (цикл 1 с):
- Ледяные осколки — меш `fx_ice_shard` (Neon `#CDF1FF`), 10 за цикл:
  - Size 0.4 по длине;
  - кувыркаются 540° / 360°;
  - отлетают на 12.5 назад, в стороны до 1.3.
- Морозные клубы — ParticleEmitter на TrailRoot:
  - цвет `#D8F6FF`, Size 0.3 → 1.5 → 0, Transparency 0.3 → 1;
  - Rate 8, Lifetime 0.9 с, EmissionDirection назад, Speed 3–4, SpreadAngle 25.
- Ледяные кольца — меш `fx_air_ring`, Neon `#8FF2FF`, 3 за цикл:
  - уходят на 7 назад вдоль древка, Size ×0.5 → ×2.1;
  - Transparency 0.2 → 1.
- Снежинки — ParticleEmitter: Texture «6-лучевая звезда», `#E6FCFF`, Size 0.28, Rate 6, Lifetime 0.9 с, RotSpeed ±300, LightEmission 1.

**FX_Impact** (1.5 с) — «клык из глубины»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#DCFBFF`, Transparency 0.3 → 1, Tween 0.4 с |
| 0.07–0.3 | гигантский ледяной клык высотой 3.4 вырастает позади копья (+1.5 по Y от точки удара, +0.9 по X), к 0.47 с «оседает» с overshoot ×1.12 → ×1.0, держится до 0.93 с, потом уходит под землю к 1.33 с | меш `fx_ice_fang`, цвет `#CDF1FF` (Neon-вид), Tween Size по Z (Back Out), затем Quad In |
| 0.07–0.3 | 3 малых клыка высотой 1.3–1.7 вырастают рядом (шаг 0.07 с) | тот же меш `fx_ice_fang`, цвет `#5FA9D8`, Size ×0.45 |
| 0–0.27 | замёрзшее кольцо r 0.9 → 1.35, держится до 1.13 с | меш `fx_frost_ring`, цвет `#CDF1FF`, Size по Z ×0.35 |
| 0–0.47 | светящееся кольцо r 0.6 → 2.4 | меш `fx_frost_glow`, Neon `#8FF2FF`, Transparency 0 → 1 |
| 0.03–1.17 | 5 ледяных трещин расходятся по земле на 1.4–2.2 | Neon-Part `#8FF2FF` толщиной 0.1, Tween длины, тают к 1.4 с |
| 0–1.2 | 14 ледяных осколков разлетаются по дуге | меш `fx_ice_shard`: `#CDF1FF` и `#5FA9D8` (каждый третий), Size 0.3–0.5, Burst Speed 7–12, Acceleration (0, −27, 0) |
| 0–1.2 | 6 ледяных глыб (чёрная окантовка не нужна) отскакивают | Part Ice `#5FA9D8`, Size 0.2–0.35, Burst Speed 5–9 |
| 0.1–1.5 | 6 снежных облачков поднимаются на 1.6–2.8, растут до ×2.4 | ParticleEmitter Burst 6: `#D8F6FF`, Size 0.5 → 2, Transparency 0.2 → 1 |
| 0.13–0.67 | 6 искр-снежинок вспыхивают вокруг | ParticleEmitter Burst 6: Texture «звезда», `#E6FCFF`, Size 0.35, Lifetime 0.4 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#6FF0FF`, Brightness 4 → 0 за 0.9 с, Range 9.

---

## 27 ash_saw — Ash Saw (shards)

**FX_Idle** — жар и тлеющие угли:
- Тепловая аура — Neon-эллипсоид `#FF8A3A`, Transparency 0.88, Size ~ (1.4, 1.0, 2.2) у лезвия, пульсация ±5% за 1 с.
- ParticleEmitter на Tip:
  - Texture «язычок», цвета `#FFC23A` / `#FF5A14`;
  - Size 0.12–0.22, Rate 7, Lifetime 1 с;
  - Acceleration (0, 1.2, 0), LightEmission 1.
- PointLight `#FF7A2A`, Brightness 1, Range 5.

**FX_Flight** (цикл 1 с):
- Искры — ParticleEmitter на TrailRoot (или меш `fx_spark`, Neon, шар r 0.06, 12 за цикл):
  - цвет `#FFC23A` / `#FF5A14`, Size 0.12, Rate 12, Lifetime 0.9 с;
  - Speed 4, SpreadAngle 45, LightEmission 1.
- Клубы пепла — ParticleEmitter за хвостом:
  - цвет `#4A4248`, Size 0.5 → 2.0, Transparency 0.2 → 1;
  - Rate 8, Lifetime 1 с.
- Пильные диски — меш `fx_saw_disc` (цвета `#8D8F9C` / `#33303A`), 5 за цикл:
  - Size ×0 → ×1.1 → ×0 (радиус 0.3);
  - вращаются 720° за цикл вокруг своей оси;
  - отлетают на 12 назад, в стороны до 0.9.
- Языки пламени — меш `fx_ember` (Neon `#FF5A14` / `#FFC23A`), 7 на цикл, острием назад, тянутся на 10.5 назад.

**FX_Impact** (1.5 с) — «пилы разлетаются»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#FFD08A`, Transparency 0.35 → 1 |
| 0–0.4 | тёмное пятно гари растёт от r 0.4 до r 2.1 (по земле), затем тает к 1.17 с | плоский шар-Neon `#18121A` (Transparency 0.2 → 1), Size по Y 0.02 |
| 0–0.4 | кольцо-искра r 0.5 → 2.5 по земле | меш `fx_ash_ring`, Neon `#FF6A1A`, Transparency 0 → 1 |
| 0.03–0.8 | 6 пильных дисков (r 0.34) веером −70…+70° едут по земле на 2.6–3.1, крутятся ~3 оборота; в конце гаснут (Size → 0 за 0.2 с) | меш `fx_saw_disc`: `#8D8F9C` и `#33303A` поочерёдно, Tween CFrame + Orientation Y, Quad Out |
| 0.1–0.6 | за каждым диском 2 огненные точки (Neon `#FF7A2A`, r 0.08) | Part Neon, Tween Size → 0 |
| 0.07–1.33 | 10 клубов пепла поднимаются на 1.8–3.2, растут до ×2.6 | ParticleEmitter Burst 10: `#4A4248`, Size 0.5 → 2.4, Transparency 0.2 → 1, Lifetime 1.2 |
| 0–1.3 | 14 углей поднимаются на 1.4–3.0 и гаснут | меш `fx_ember`, Neon `#FFC23A` / `#FF5A14`, или ParticleEmitter Burst 14 с Acceleration (0, 2, 0) |
| 0.03–1.17 | 5 тлеющих трещин по земле на 1.4–2.2 | Neon-Part `#FF6A1A` толщиной 0.1, Tween длины; тают в конце |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#FF7A2A`, Brightness 4 → 0 за 0.8 с, Range 9.

---

## 28 golem_heart — Golem Heart (sparks)

**FX_Idle** — тёплое сердце голема:
- Аура — Neon-эллипсоид `#FF9A3A`, Transparency 0.9, Size ~ (2.1, 2.1, 2.6) вокруг ядра, пульсация ±8% за 1.2 с (как удар сердца).
- ParticleEmitter на ядре:
  - цвет `#FFC24A`, Size 0.08–0.14;
  - Rate 5, Lifetime 1.2 с, Speed 0.3, SpreadAngle 180, LightEmission 1.
- PointLight `#FF8A2A`, Brightness 1.2, Range 6, пульсация яркости 1 → 1.5 за 1.2 с.

**FX_Flight** (цикл 1 с):
- Каменные осколки — меш `fx_stone_chip` (цвета `#8F8678` / `#5F574F`), 8 за цикл:
  - Size 0.2;
  - кувыркаются 720° / 540°;
  - отлетают на 13 назад, в стороны до 1.2.
- Искры — ParticleEmitter на TrailRoot: `#FFC24A`, Size 0.12, Rate 10, Lifetime 0.9 с, Speed 4, SpreadAngle 45, LightEmission 1.
- Пыль — ParticleEmitter: `#D8C8A8`, Size 0.5 → 2.0, Transparency 0.3 → 1, Rate 7, Lifetime 1 с.
- Кольца пульса — меш `fx_air_ring`, Neon `#FF8A2A`, 3 за цикл:
  - уходят на 6.5 назад вдоль древка, Size ×0.5 → ×2.0;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «каменные кулаки»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.2, гаснет | Neon-шар `#FFD08A`, Transparency 0.3 → 1 |
| 0.03–0.2 | два каменных кулака (r 0.58, по 3 костяшки r 0.19, рука-столб высотой 1.5) поднимаются из земли по бокам, на ±2.0 по Y и +1.4 по X от точки удара | меш `fx_golem_fist` (`#8F8678`), столб `#5F574F`, костяшки `#C4B8A2`; Tween CFrame по Z от −0.7 до 0.95, Back Out |
| 0.23–0.4 | замах: кулаки поднимаются до 1.15 | Tween 0.17 с |
| 0.4–0.53 | кулаки сходятся к центру (Y ±0.62) и бьют друг о друга, отскок до ±0.7 к 0.63 с | Tween CFrame 0.13 с Quad In, затем 0.1 с Back Out |
| 0.63–1.0 | кулаки держатся, на ладонях светятся оранжевые точки `#FFB03A` | Neon-шар r 0.2 на каждой ладони |
| 1.0–1.33 | кулаки уходят в землю и сжимаются | Tween CFrame по Z → −0.7, Size → 0 |
| 0.53–1.0 | кольцо удара по земле r 0.5 → 2.5 от места хлопка | меш `fx_core_ring`, Neon `#FF8A2A`, Transparency 0 → 1 |
| 0.0, 0.27 | два кольца пульса ядра у копья до r 2.0 / 1.5 | меш `fx_core_ring`, Neon `#FFD25A`, Transparency 0 → 1 |
| 0.53–1.2 | 12 искр вылетают из места хлопка | ParticleEmitter Burst 12: `#FFC24A`, Size 0.12–0.2, Speed 7–12, Acceleration (0, −27, 0), LightEmission 1 |
| 0.53–1.2 | 8 каменных осколков разлетаются | меш `fx_stone_chip`, Size 0.2–0.35, Burst Speed 6–10, Acceleration (0, −27, 0) |
| 0.03–1.5 | 8 клубов пыли у подъёма и хлопка растут до ×2.4 | ParticleEmitter Burst 8: `#D8C8A8`, Size 0.5 → 2.2, Transparency 0.2 → 1 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#FF8A2A`, Brightness 3 → 5 (0.53 с, хлопок) → 0 (1.3 с), Range 10.

---

## 29 magma_tongue — Magma Tongue (fire)

**FX_Idle** — жар и капли лавы:
- Тепловая аура — Neon-эллипсоид `#FF7A2A`, Transparency 0.88, Size ~ (1.7, 1.0, 2.5) вокруг языка, пульсация ±5% за 1 с.
- ParticleEmitter на Tip:
  - Texture «язычок», цвета `#FFC040` / `#FF5A1A`;
  - Size 0.12–0.22, Rate 7, Lifetime 1 с;
  - Acceleration (0, 1.3, 0), LightEmission 1.
- Капли лавы у основания языка — ParticleEmitter: `#FFC040`, Size 0.12, Rate 2, Lifetime 0.8 с, Acceleration (0, −6, 0).
- PointLight `#FF6A1A`, Brightness 1.3, Range 6.

**FX_Flight** (цикл 1 с):
- Капли лавы — ParticleEmitter на TrailRoot: цвета `#FF5A1A` / `#FFC040`, Size 0.28 → 0.5 → 0, Rate 8, Lifetime 0.9 с, Speed 3, SpreadAngle 25, LightEmission 1.
- Языки пламени — Neon-меш (шаблон `fx_lava_geyser`, Size ×0.25), цвета `#FF5A1A` / `#FFC040` / `#E0301A` по очереди, 8 на цикл:
  - направлены назад;
  - тянутся на 11 назад и расходятся до 0.8 в стороны.
- Дым — ParticleEmitter за хвостом: `#4A3A40`, Size 0.5 → 1.8, Transparency 0.2 → 1, Rate 6, Lifetime 1 с.
- Искры — ParticleEmitter: `#FFC040`, Size 0.12, Rate 6, Speed 4, SpreadAngle 45.
- Огненные кольца — меш `fx_fire_ring`, Neon `#FF5A1A` / `#FFC040`, 3 за цикл:
  - уходят на 6.5 назад, Size ×0.5 → ×2.0;
  - Transparency 0.2 → 1.
- PointLight `#FF6A1A`, Brightness 1.8, Range 9.

**FX_Impact** (1.5 с) — «лавовый гейзер»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#FFC878`, Transparency 0.35 → 1 |
| 0–0.4 | лавовая лужа растёт по земле до r 1.6, держится до 1.2 с, потом тает | плоская Neon-сфера `#FF5A1A`, Size по Y 0.05 |
| 0–0.2 | главная трещина длиной 3.2 вперёд по +X (7 звеньев, ширина 0.12) раскрывается; к ней добавляются 2 боковые ветки | меш `fx_lava_crack` (зигзаг длиной 3.2, Neon `#FF5A1A`) или Neon-Part `#E0301A` толщиной 0.1 для веток, Tween длины; тает с 1.0 до 1.5 с |
| 0.1, 0.2, 0.3 | три гейзера по трещине на X +0.7 / +1.7 / +2.6 (высота 2.8 / 2.2 / 1.6): вырастают за 0.13 с, держатся 0.4 с, оседают к 0.95 с | меш `fx_lava_geyser` (Neon `#FF5A1A`) + внутренний столб Size ×0.6 (Neon `#FFC040`), Tween Size по Z (Back Out) |
| 0.1–1.3 | 12 капель лавы летят дугой вперёд ±70° | меш `fx_lava_blob` или ParticleEmitter Burst 12: `#FF5A1A` / `#FFC040`, Size 0.16–0.3, Speed 8–13, Acceleration (0, −27, 0), LightEmission 1 |
| 0.03–1.2 | 8 чёрных корок-камней разлетаются и падают | меш `fx_crust_rock`, цвет `#2A2226`, Size 0.25–0.4, Burst Speed 6–10, Acceleration (0, −27, 0) |
| 0.07–1.3 | 6 языков-углей поднимаются на 1.6–3.2 | меш (шаблон `fx_lava_geyser`, Size ×0.2), Neon, Tween Position вверх 0.9 с |
| 0.13–1.5 | 8 клубов дыма поднимаются на 2.2–3.6, растут до ×2.6 | ParticleEmitter Burst 8: `#4A3A40`, Size 0.5 → 2.4, Transparency 0.1 → 1, Lifetime 1.2 |
| 1.0–1.5 | трещина и лужа гаснут (Transparency 0 → 1) | Tween Transparency |

Свет: PointLight `#FF6A1A`, Brightness 6 (t = 0) → 3 (0.5 с) → 0 (1.3 с), Range 14.

---

## 30 phoenix_wing — Phoenix Wing (fire)

**FX_Idle** — жар крыльев и угли:
- Тепловая аура — Neon-эллипсоид `#FF9A3A`, Transparency 0.88, Size ~ (3.0, 1.2, 2.2) вокруг крыльев, пульсация ±5% за 1.2 с.
- ParticleEmitter на Tip:
  - Texture «язычок», цвета `#FFD24A` / `#FF6A1A`;
  - Size 0.12–0.22, Rate 6, Lifetime 1 с;
  - Acceleration (0, 1.3, 0), LightEmission 1.
- Блики: цвет `#FFF2C0`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#FF8A2A`, Brightness 1.2, Range 6.

**FX_Flight** (цикл 1 с) — огненный хвост феникса:
- Языки пламени — меш `fx_flame_tongue`, Neon, 10 на цикл:
  - цвета `#FF6A1A`, `#FFD24A`, `#E0302A` по очереди;
  - направлены назад;
  - Size ×1.4 → ×0.8, тянутся на 11.5 назад, расходятся до 0.9 в стороны.
- Огненные перья — ParticleEmitter на TrailRoot (Texture «перо»):
  - цвета `#FFD24A` / `#FF6A1A`, Size 0.5, Rate 8, Lifetime 0.9 с;
  - RotSpeed ±200, Speed 3–4, SpreadAngle 30, LightEmission 1.
- Искры — ParticleEmitter: `#FFD24A`, Size 0.12, Rate 8, Speed 4, SpreadAngle 45.
- Огненные кольца — Neon-меш (шаблон `fx_fire_ring`, он же `im_ring`), цвета `#FF6A1A` / `#FFD24A`, 3 за цикл:
  - уходят на 6 назад, Size ×0.5 → ×2.0;
  - вращаются 360° за цикл.
- PointLight `#FF8A2A`, Brightness 2, Range 10.

**FX_Impact** (1.5 с) — «крылья разворачиваются»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.5, гаснет | Neon-шар `#FFE0A0`, Transparency 0.3 → 1 |
| 0, 0.17 | два огненных кольца по земле r 0.6 → 2.6 / 2.1 за 0.47 с | меш `fx_fire_ring`, Neon `#FFD24A` / `#FF6A1A`, Transparency 0 → 1 |
| 0–0.6 | центральный столб огня высотой 2.2 вспыхивает (0.17 с), оседает и гаснет к 0.6 с | меш `fx_wing_feather` (Size ×1.1 по ширине, высота 2.2), Neon `#FFD24A` |
| 0–0.37 | два крыла (по 6 огненных перьев высотой 1.8–2.8 каждое) разворачиваются веером от точки удара в плоскостях ±55° от плоскости копья; перья веером от 10° до 85° от вертикали, старт с шагом 0.03 с | меш `fx_wing_feather`, Neon `#FF6A1A` / `#FFD24A` / `#E0302A` по очереди, CFrame-поворот вокруг основания, Size 0.3 → 1.0 |
| 0.4–0.6 | взмах вниз: все перья опускаются до 50% угла | Tween CFrame 0.2 с, Quad InOut |
| 0.6–0.8 | взмах вверх: до 112% угла | Tween 0.2 с |
| 0.8–1.07 | крылья держатся | пауза |
| 1.07–1.2 | крылья распадаются: перья расходятся до 125% угла и сжимаются в 0 | Tween Size → 0 за 0.13 с |
| 0.47–1.1 | 14 углей поднимаются из крыльев на 1.0–1.8, гаснут | меш `fx_ember_flame`, Neon `#FFD24A` / `#FF6A1A`, Size ×1 → 0, Tween Position вверх 0.8 с |
| 0.27–1.2 | 8 огненных перьев-листьев плавно падают с высоты 2.6–3.4, покачиваясь и вращаясь | меш `fx_fall_feather`, Neon `#FFD24A` / `#FF6A1A`, Tween CFrame по 3 точкам |
| 0.2–1.2 | 6 звёздочек вспыхивают вокруг | ParticleEmitter Burst 6: Texture «звезда», `#FFF2C0`, Size 0.35, Lifetime 0.4 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#FF8A2A`, Brightness 5 (t = 0) → 3 (0.5 с) → 0 (1.3 с), Range 14.

---

## 31 amethyst_geode — Amethyst Geode (crystal)

**FX_Idle** — свечение ядра и искры:
- Аура — Neon-эллипсоид `#C46AFF`, Transparency 0.9, Size ~ (2.2, 2.2, 2.6) вокруг ядра, пульсация ±8% за 1.2 с.
- ParticleEmitter на ядре:
  - цвет `#E8B0FF`, Size 0.08–0.14;
  - Rate 5, Lifetime 1.3 с, Speed 0.3, SpreadAngle 180, LightEmission 1.
- Блики: Texture «звёздочка», цвет `#F6E0FF`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#C46AFF`, Brightness 1, Range 6.

**FX_Flight** (цикл 1 с):
- Аметистовые осколки — меш `fx_fl_crystal` (Neon `#9A4EE0` / `#C996FF` по очереди), 10 за цикл:
  - Size 0.4 по длине;
  - кувыркаются 540° / 360°;
  - отлетают на 12.5 назад, в стороны до 1.3.
- Звёздочки — ParticleEmitter: Texture «звезда 4 луча», `#F6E0FF`, Size 0.3, Rate 8, Lifetime 0.9 с, RotSpeed ±300, LightEmission 1.
- Лиловые клубы — ParticleEmitter на TrailRoot: `#E0B8FF`, Size 0.3 → 1.5 → 0, Transparency 0.3 → 1, Rate 6, Lifetime 0.9 с.
- Кольца — меш `fx_geode_ring`, Neon `#C46AFF`, 3 за цикл:
  - уходят на 7 назад вдоль древка, Size ×0.5 → ×2.1;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «жеода раскрывается»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#F0D0FF`, Transparency 0.3 → 1 |
| 0.03–0.4 | купол из ~18 кристаллов (r 0.17, высота 0.95–1.45) вырастает на полусфере радиуса 1.8 вокруг копья; все остриями внутрь; растут снизу вверх: 3 яруса на высоте 14° / 40° / 68°, старт с шагом 0.03 с | меш `fx_dome_crystal`, цвета `#9A4EE0` / `#C996FF` по очереди; Tween Size 0 → 1.15 (0.17 с), затем → 1.0 (0.1 с); кристаллы у линии древка пропущены |
| 0.1–1.0 | внутри купола светится шар-ядро r 0.9, к 1.0 с набухает до ×2.4 и гаснет | Neon-шар `#D89AFF`, Transparency 0.65 → 1 |
| 0–1.2 | на земле светящийся диск r 1.2 → 1.9 | плоская Neon-сфера `#C46AFF`, Transparency 0.6 → 1 |
| 0.67–1.1 | купол раскрывается наружу: каждый кристалл уходит от центра на 0.9, затем на 1.7 и сжимается в 0 к 1.1 с | Tween CFrame вдоль радиуса, Size → 0 |
| 0.67, 0.83 | два кольца от центра r 0.6 → 3.0 / 2.4 | меш `fx_geode_ring`, Neon `#C46AFF`, Transparency 0 → 1 |
| 0.67–1.2 | 12 осколков вылетают из раскрытой жеоды | меш `fx_shard`, цвета `#9A4EE0` / `#C996FF`, Size 0.3–0.45, Burst Speed 6–12, Acceleration (0, −27, 0) |
| 0.6–1.0 | 6 звёздочек-вспышек | ParticleEmitter Burst 6: Texture «звезда», `#F6E0FF`, Size 0.35, Lifetime 0.4 |
| 0.6–1.5 | 6 облачков пыли поднимаются на 1.0–2.0 | ParticleEmitter Burst 6: `#E0B8FF`, Size 0.5 → 1.8, Transparency 0.3 → 1 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#C46AFF`, Brightness 2 (t = 0) → 5 (0.67 с, раскрытие) → 0 (1.3 с), Range 11.

---

## 32 quartz_needle — Quartz Needle (crystal)

**FX_Idle** — тонкое сияние иглы:
- Аура — Neon-вытянутый эллипсоид `#A8E8FF`, Transparency 0.9, Size ~ (1.0, 1.0, 3.4) вдоль иглы, пульсация ±5% за 1.2 с.
- ParticleEmitter вдоль иглы:
  - цвет `#F4FEFF`, Size 0.08–0.14;
  - Rate 4, Lifetime 1.2 с, Speed 0.3, SpreadAngle 180, LightEmission 1.
- Блики: Texture «звёздочка», цвет `#F4FEFF`, Size 0.2, Rate 3, Lifetime 0.4 с, LightEmission 1.
- PointLight `#8CE6FF`, Brightness 0.8, Range 5.

**FX_Flight** (цикл 1 с):
- Иглы-штрихи — меш `fx_fl_needle` (Neon `#E8F4FF` / `#A8C4E8` по очереди), 14 за цикл:
  - Size 0.9 по длине, вытянуты вдоль оси копья, не вращаются;
  - отлетают на 12.5 назад, в стороны до 1.25;
  - длина растёт ×1.0 → ×1.8.
- Блики — ParticleEmitter: Texture «звезда 4 луча», `#F4FEFF`, Size 0.3, Rate 8, Lifetime 0.9 с, RotSpeed ±300, LightEmission 1.
- Кольца — меш `fx_glow_ring` (r 0.4), Neon `#8CE6FF`, 3 за цикл:
  - уходят на 7.5 назад вдоль древка, Size ×0.5 → ×2.3;
  - Transparency 0.2 → 1.
- Лёгкие облачка — ParticleEmitter за хвостом: `#F0FCFF`, Size 0.3 → 1.2, Transparency 0.3 → 1, Rate 5, Lifetime 0.9 с.

**FX_Impact** (1.5 с) — «лес кварцевых игл»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#E8FCFF`, Transparency 0.3 → 1 |
| 0–1.0 | на земле светящийся диск r 1.2 → 2.4 | плоская Neon-сфера `#A8E8FF`, Transparency 0.6 → 1 |
| 0.4–0.9 | кольцо по земле r 0.6 → 2.6 | меш `fx_glow_ring`, Neon `#8CE6FF`, Transparency 0 → 1 |
| 0–0.2 | ~44 тонкие иглы (r 0.05–0.085, высота 0.9–2.2) мгновенно вырастают по спирали (золотой угол) в диске радиуса 2.5 вокруг копья; ближние к копью — раньше; зона вдоль древка свободна | меш `fx_needle`, цвета `#E8F4FF` / `#A8C4E8` (каждая третья), Tween Size по Z 0.05 → 1.2 (0.1 с) → 1.0 (0.1 с), наклон наружу 7–20° |
| 0.2–1.0 | лес стоит | пауза |
| 0.73–1.23 | иглы тают от центра к краям: Size по Z → 0.05, затем 0 (шаг от центра, разброс 0.1 с) | Tween Size 0.17 с |
| 0.13–1.07 | 8 бликов-звёзд вспыхивают на остриях | меш `fx_glint` (Neon `#F4FEFF`, Size 0.4, 0 → 1.3 → 0 за 0.4 с) или ParticleEmitter Burst 8: Texture «звезда», Lifetime 0.4 |
| 0–1.2 | 8 осколков стекла отлетают по дуге | меш `fx_fl_needle` (Size ×0.5), Burst Speed 6–10, Acceleration (0, −27, 0) |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#8CE6FF`, Brightness 3 → 0 за 1 с, Range 9.

---

## 33 lunar_crescent — Lunar Crescent (ice)

**FX_Idle** — лунная дымка и блики:
- Аура — Neon-эллипсоид `#BFE6FF`, Transparency 0.9, Size ~ (2.6, 1.3, 2.2) вокруг полумесяца, пульсация ±5% за 1.2 с.
- ParticleEmitter на Tip:
  - Texture «снежинка», цвет `#F0F8FF`;
  - Size 0.08–0.16, Transparency 0.2 → 1;
  - Rate 5, Lifetime 1.6 с, Speed 0.2, Acceleration (0, −0.3, 0).
- Блики: цвет `#F4FCFF`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#BFE6FF`, Brightness 0.9, Range 6.

**FX_Flight** (цикл 1 с):
- Маленькие серебряные полумесяцы — меш `fx_fl_crescent` (цвет `#E4EAF6`), 8 за цикл:
  - Size 0.6 по диаметру;
  - вращаются 360° вокруг Z и 200° вокруг Y;
  - отлетают на 12.5 назад, в стороны до 1.3.
- Снежные клубы — ParticleEmitter на TrailRoot:
  - цвет `#F0F8FF`, Size 0.3 → 1.5 → 0, Transparency 0.3 → 1;
  - Rate 8, Lifetime 0.9 с, EmissionDirection назад, Speed 3–4, SpreadAngle 25.
- Блики — ParticleEmitter: Texture «звезда 4 луча», `#F4FCFF`, Size 0.3, Rate 6, Lifetime 0.9 с, RotSpeed ±300, LightEmission 1.
- Морозные кольца — Neon-меш (шаблон `fx_halo`, Size ×0.55), цвет `#BFE6FF`, 3 за цикл:
  - уходят на 7 назад, Size ×0.5 → ×2.1;
  - Transparency 0.2 → 1.

**FX_Impact** (1.5 с) — «лунные лезвия»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#EAF6FF`, Transparency 0.3 → 1 |
| 0.13–0.53 | морозный диск на земле r 0.12 → 1.2 → 2.6, к 1.2 с тает | плоская Neon-сфера `#D8F0FF`, Transparency 0.5 → 1 |
| 0–0.47 | кольцо r 0.6 → 3.0 по земле | меш `fx_halo` (положить плашмя), Neon `#BFE6FF`, Transparency 0 → 1 |
| 0–0.97 | 6 ледяных полумесяцев (дуга r 0.75 на 140°, толщина 0.2, плашмя) веером −75…+75° разъезжаются по земле на 2.8–3.2, крутясь ~2.5 оборота; старт группами через 0.03 с, на 0.2 с они на ~45% пути, на 0.73 с на конце, к 0.97 с исчезают | меш `fx_moon_blade`, цвет `#BFEAFF` (Neon-вид), Tween CFrame + Orientation Y, Quad Out |
| 0.17–1.33 | 12 ледяных кристаллов (r 0.07, высота 0.4–0.5) вырастают вдоль путей полумесяцев и стоят до 1.0 с | меш `fx_frost_crystal`, цвет `#BFEAFF`, Tween Size по Z 0 → 1.2 → 1.0 |
| 0.13–1.33 | луна: диск r 0.8 (плоский, лицом к камере) появляется впереди копья (+1.1 по X) на высоте 2.2, поднимается до 3.2 к 0.47 с и до 3.8 к 1.33 с, светится, затем тает | меш `fx_moon_disc`, Neon `#E6F4FF`, Tween Position, Transparency 0 → 1 |
| 0.13–1.33 | ореол — кольцо r 1.0 вокруг луны, растёт ×1.1 → ×1.6 | меш `fx_halo`, Neon `#BFE6FF`, Transparency 0 → 1 |
| 0–1.2 | 10 ледяных осколков разлетаются | меш `fx_frost_crystal` (Size ×0.8), Burst Speed 6–10, Acceleration (0, −27, 0) |
| 0.1–1.5 | 6 снежных облачков поднимаются на 1.4–2.6 и растут до ×2.4 | ParticleEmitter Burst 6: `#F0F8FF`, Size 0.5 → 2, Transparency 0.3 → 1 |
| 0.13–0.8 | 6 бликов-звёзд | ParticleEmitter Burst 6: Texture «звезда», `#F4FCFF`, Size 0.35, Lifetime 0.4 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight `#BFE6FF`, Brightness 4 → 0 за 1 с, Range 10.

---

## 34 aurora_weave — Aurora Weave (ice)

**FX_Idle** — северное сияние вокруг клинка:
- Аура — Neon-эллипсоид `#5DFFB0`, Transparency 0.9, Size ~ (2.1, 1.7, 2.8) вокруг клинка, цвет плавно меняется `#5DFFB0` → `#3BE8FF` → `#B070FF` за 3 с.
- ParticleEmitter на клинке:
  - цвета `#5DFFB0` / `#3BE8FF` / `#B070FF`, Size 0.08–0.14;
  - Rate 5, Lifetime 1.4 с, Speed 0.3, SpreadAngle 180, LightEmission 1.
- Блики: Texture «звёздочка», цвет `#F4FFFC`, Size 0.15, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#5DFFB0`, Brightness 0.9, Range 6.

**FX_Flight** (цикл 1 с):
- Цветные кольца — меш `fx_fl_ring`, Neon `#5DFFB0` / `#3BE8FF` / `#B070FF` по очереди, 6 за цикл:
  - уходят на 7.5 назад вдоль древка, Size ×0.5 → ×2.3;
  - покачиваются ±8° (волна);
  - Transparency 0.2 → 1.
- Ледяные кристаллы — меш `fx_ice_crystal` (цвет `#BFEEFF`), 8 за цикл: Size 0.38, кувыркаются 540° / 360°, отлетают на 12.5 назад, в стороны до 1.3.
- Блики — ParticleEmitter: Texture «звезда 4 луча», `#F4FFFC`, Size 0.3, Rate 8, Lifetime 0.9 с, RotSpeed ±300, LightEmission 1.
- Облачка сияния — ParticleEmitter за хвостом: цвета `#5DFFB0` / `#3BE8FF` / `#B070FF`, Size 0.3 → 1.6, Transparency 0.4 → 1, Rate 6, Lifetime 0.9 с.

**FX_Impact** (1.5 с) — «волны сияния»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка-сфера r 0.5 → 1.4, гаснет | Neon-шар `#E8FFFA`, Transparency 0.3 → 1 |
| 0.13–1.0 | светящийся диск на земле r 1.2 → 2.4 | плоская Neon-сфера `#7AFFD0`, Transparency 0.6 → 1 |
| 0–0.4 | 9 цветных колец (r 0.9, толщина 0.05) стартуют друг за другом (шаг 0.05 с) и поднимаются по очереди от земли; кольцо k уходит вверх на 0.4 + 0.3·k, растёт до ×1.6, покачивается ±8°, тает за ~0.9 с | меш `fx_aurora_ring`, Neon `#5DFFB0` / `#3BE8FF` / `#B070FF` по очереди, Tween Position + Size + Transparency, Sine InOut |
| 0.07–1.0 | 3 кольца по 8 светящихся лучей (r 0.85 / 1.05 / 1.25, высота 2.4) вырастают из земли вокруг копья, тянутся до ×1.3 и гаснут | меш `fx_light_shaft`, Neon `#5DFFB0` / `#3BE8FF` / `#B070FF`, Tween Size.Y 0.1 → 1 → 1.3 и Transparency 0 → 1, шаг запуска колец 0.1 с |
| 0.13–1.0 | 14 ледяных кристаллов (высота 0.4–0.8) вырастают по диску r 2.0; ближние раньше; стоят до 1.0 с | меш `fx_ice_crystal`, цвет `#BFEEFF`, Tween Size по Z 0 → 1.2 → 1.0 |
| 0.2–0.9 | 8 бликов-звёзд | меш `fx_star` (или ParticleEmitter Burst 8: Texture «звезда», `#F4FFFC`, Size 0.4, Lifetime 0.4) |
| 0–1.2 | 8 ледяных осколков разлетаются | меш `fx_ice_crystal` (Size ×0.8), Burst Speed 6–10, Acceleration (0, −27, 0) |
| 0.1–1.5 | 4 снежных облачка поднимаются на 1.4–2.4 | ParticleEmitter Burst 4: `#C8FFF0`, Size 0.5 → 2, Transparency 0.3 → 1 |
| 1.17–1.5 | всё схлопывается | Tween Size → 0 |

Свет: PointLight, цвет плавно `#5DFFB0` → `#B070FF`, Brightness 4 → 0 за 1 с, Range 10.

---

## 35 cloud_feather — Cloud Feather (feathers)

**FX_Idle** — лёгкая аура и блики у пера:
- ParticleEmitter «пух» на Tip: цвет `#FFFFFF` → `#CFE8FF`, Size 0.06–0.11, Transparency 0.2 → 1, Rate 5, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180, Acceleration (0, 0.3, 0).
- ParticleEmitter бликов: Texture «звёздочка», цвет `#FFFBE0`, Size 0.15, Rate 1.5, Lifetime 0.5 с, LightEmission 1.
- Слабая аура: PointLight на Tip, цвет `#CFEEFF`, Range 8, Brightness 0.8.

**FX_Flight** (цикл 1 с):
- Облачные клубы — ParticleEmitter на TrailRoot: цвет `#FFFFFF` / `#CFE8FF`, Size NumberSequence 0.6 → 1.8 → 0, Transparency 0.1 → 1, Rate 10, Lifetime 1 с, EmissionDirection назад, Speed 2–4, SpreadAngle 25.
- Перья — ParticleEmitter: Texture «перо», цвета `#FFFFFF`, `#FF9EC4`, `#58B7FF`, `#FFD35A`, Size 0.7, Rate 10, Lifetime 1 с, RotSpeed ±300, Speed 3–5, SpreadAngle 30.
- Радужные кольца — Neon-меш `rainbow_ring`, цвета `#FF4A5A`, `#FFE14A`, `#3AD8FF`, раз в 0.33 с: у острия Size ×0.5, за 1 с уходит назад на 6.5, растёт до ×2.1, Transparency 0.2 → 1.
- Звёздочки — ParticleEmitter, цвет `#FFFBE0`, Size 0.15, Rate 6, Lifetime 0.8 с.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | белая вспышка r 0.6 → 2.0 и гаснет | Neon-шар, цвет `#FFFFFF`, Tween Size 0.8 → 3.4, Transparency 0 → 1 |
| 0–1.3 | облачная подушка расплывается по земле до r ≈ 2.6 и тает | меш `cloud_puff` сплюснутый ×0.35 по Y, цвет `#CFE8FF`, Tween Size, Transparency 0.2 → 1 |
| 0–0.1 старт, 1.3 конец | 18 облачных клубов разлетаются по кругу на 1.2–3.0 (назад дальше) и растут до ×2.5 | ParticleEmitter Burst 18: меш/текстура клуба `#FFFFFF`/`#CFE8FF`, Size 0.9 → 2.5, Transparency 0.1 → 1, Lifetime 1.3, Speed 3–5, Drag 2 |
| 0–1.3 | 10 перьев взлетают на 2.2–3.4 за 0.5 с, кружатся и опадают | Burst 10: Texture «перо» (`#FFFFFF`, `#FF9EC4`, `#58B7FF`, `#FFD35A`), Size 0.8, RotSpeed ±250, Speed 5–7 вверх, Acceleration (0, −4, 0), Lifetime 1.3 |
| 0.03–0.8 | 7 радужных колец от r 0.55–1.3 растут ×2.6 с шагом 0.03 с и гаснут | меш `rainbow_ring` ×7, Neon `#FF4A5A`, `#FF9A3A`, `#FFE14A`, `#5AE06A`, `#3AD8FF`, `#4A7AFF`, `#B05AFF`, Tween Size и Transparency 0 → 1 |
| 0.07–1.3 | 8 золотистых звёзд взлетают на 1.4–3 | Burst 8: Texture «звёздочка» `#FFFBE0`, Size 0.2, LightEmission 1, Lifetime 1.2 |

Свет: PointLight `#FFFFFF`, Range 12, Brightness 2, гаснет за 0.4 с.

---

## 36 sky_harpoon — Sky Harpoon (feathers)

**FX_Idle** — облачко и блики вокруг гарпуна:
- ParticleEmitter на Tip: цвет `#FFFFFF` → `#CFE6FF`, Size 0.06–0.11, Transparency 0.2 → 1, Rate 5, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180.
- ParticleEmitter бликов: Texture «звёздочка», цвет `#FFF0A0`, Size 0.15, Rate 1.5, Lifetime 0.5 с, LightEmission 1.
- Слабая аура: PointLight `#BFEAFF`, Range 8, Brightness 0.7.

**FX_Flight** (цикл 1 с):
- Облачные клубы — ParticleEmitter на TrailRoot: `#FFFFFF` / `#CFE6FF`, Size 0.6 → 1.8 → 0, Transparency 0.1 → 1, Rate 10, Lifetime 1 с, EmissionDirection назад, Speed 2–4, SpreadAngle 25.
- Перья — ParticleEmitter: Texture «перо», цвета `#FFFFFF`, `#4FB4FF`, `#E8B43E`, Size 0.65, Rate 9, Lifetime 1 с, RotSpeed ±300, Speed 3–5.
- Кольца ветра — Neon-меш `wind_ring`, цвет `#E8FBFF`, 4 штуки за цикл (раз в 0.25 с): у острия Size ×0.5, за 1 с уходят назад на 7, растут до ×2.1, вращаются 360°, Transparency 0.2 → 1.
- Искры — ParticleEmitter, цвет `#FFF0A0`, Texture «звёздочка», Size 0.15, Rate 5, Lifetime 0.8 с.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | белая вспышка до r 1.9 | Neon-шар `#FFFFFF`, Tween Size 0.8 → 3.2, Transparency 0 → 1 |
| 0.07–0.4 | 3 латунных зубца-гарпуна (длина 1.5) вылезают из земли по кругу r 1.7 под 120° и загибаются к копью, держатся до 1.27 с | меш `barb`, цвет `#E8B43E`, Tween Size с перебором (×1.25) за 0.1 с и возврат; рядом золотая точка `#FFF0A0` |
| 0.13–0.9 | у основания каждого зубца кольцо-якорь r 0.3 → 0.65 | Neon-кольцо `#FFF0A0`, Tween Size и Transparency |
| 0–0.13 старт, 1.33 конец | 12 облачных клубов разлетаются на 1.2–3.0 (назад дальше), растут до ×2.4 | ParticleEmitter Burst 12: `#FFFFFF`/`#CFE6FF`, Size 0.9 → 2.4, Lifetime 1.3, Speed 3–5 |
| 0.07–1.33 | 6 колец ветра поднимаются спиралью с 0.2 до 4.2 с шагом 0.07 с, растут до ×2.4 и гаснут | меш `wind_ring` ×6, Neon `#E8FBFF`, Tween CFrame (вверх + вращение 720°), Size, Transparency |
| 0–1.3 | 8 перьев кружатся вверх на 2.2–3.4 и опадают | Burst 8: Texture «перо», Size 0.8, RotSpeed ±250, Lifetime 1.3 |
| 0.07–1.33 | 8 звёзд-искр разлетаются | Burst 8: `#FFF0A0`, Size 0.2, Lifetime 1.2 |

Свет: PointLight `#FFFFFF`, Range 12, Brightness 2, гаснет за 0.4 с.

---

## 37 rift_shards — Rift Shards (shards)

**FX_Idle** — фиолетовая аура и мерцание вокруг осколков:
- PointLight на Tip: цвет `#B06CFF`, Range 9, Brightness 1.
- ParticleEmitter огоньков: цвета `#F0D0FF` / `#B45CFF`, Size 0.05–0.1, Transparency 0.2 → 1, Rate 7, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180.
- ParticleEmitter бликов: Texture «звёздочка», `#F0D0FF`, Size 0.15, Rate 1, Lifetime 0.5 с, LightEmission 1.

**FX_Flight** (цикл 1 с):
- Тёмные осколки — ParticleEmitter: меш/текстура осколка, цвета `#2A2038` / `#7A2FB0`, Size 0.5, Rate 12, Lifetime 1 с, RotSpeed ±500, Speed 3–5, SpreadAngle 30.
- Дым — ParticleEmitter на TrailRoot: цвет `#5A2A8A`, Size 0.6 → 1.8 → 0, Transparency 0.2 → 1, Rate 8, Lifetime 1 с, EmissionDirection назад.
- Кольца — Neon-меш `rift_rim`, цвета `#B45CFF` / `#FF7AE8`, 3 за цикл: от острия на 6.5 назад, растут ×0.5 → 2.1, Transparency 0.2 → 1.
- Искры — ParticleEmitter, `#F0D0FF`, Size 0.12, Rate 8, Lifetime 0.8 с, Speed 4–6.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.27 | диск разлома r 1.0 раскрывается до r 3.0 (плоский, тёмный `#0E0618`), держится до ≈1.1 с, потом схлопывается к 0.15 и исчезает к 1.33 с | меш `rift_disc`, Transparency 0.1, Tween Size (Quad Out) 0.9 → 3.0; ободок меш `rift_rim`, Neon `#B45CFF`, и второй тонкий `#FF7AE8` r 2.4 |
| 0.07–1.0 | 6 фиолетовых трещин длиной 1.6–2.4 разбегаются от точки удара | `ground_crack` ×6, Neon `#B45CFF`, Tween длины |
| 0.07–0.97 | 10 тёмных осколков (`shard`) с высоты 0.8–2.2 по спирали (1.3 оборота, радиус 2.3–3.2) втягиваются в центр и сжимаются в 0 | меш `shard` `#2A2038` / `#7A2FB0`, Tween CFrame по заранее посчитанным точкам (шаг 0.067 с) |
| 0.07–0.9 | 16 светлых искр втягиваются тем же вихрем (1.6 оборота) | ParticleEmitter с Acceleration к центру или 16 Neon-шариков `#F0D0FF` / `#B45CFF`, Size 0.14 |
| 1.0–1.17 | имплозия: шар-пузырь r 0.5 → 3.0 за 0.1 с, цвет `#E6B8FF` | Neon-шар Tween Size, Transparency 0 → 1 |
| 1.1–1.33 | кольцо-вспышка `#FF7AE8` расширяется от 0.4 до 5 и гаснет | меш `rift_rim`, Tween Size, Transparency |
| 1.1–1.33 | 8 искр разлетаются наружу на 1–2.8 | Burst 8: `#F0D0FF`, Size 0.16, Lifetime 0.4 |

Свет: PointLight `#B06CFF`, Range 10, Brightness 2, держится пока открыт разлом (до 1.1 с), вспышка 4 на 0.1 с в момент имплозии.

---

## 38 void_scissors — Void Scissors (crystal)

**FX_Idle** — тьма между лезвиями:
- PointLight на Tip: цвет `#A050F0`, Range 8, Brightness 0.9.
- ParticleEmitter огоньков: `#F0D0FF` / `#B45CFF`, Size 0.05–0.1, Transparency 0.2 → 1, Rate 7, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180.
- ParticleEmitter бликов: Texture «звёздочка», `#F0D0FF`, Size 0.15, Rate 1, Lifetime 0.5 с, LightEmission 1.

**FX_Flight** (цикл 1 с):
- Полумесяцы-разрезы — Neon-меш `crescent`, цвета `#B45CFF` / `#FF6AF0`, раскиданы вокруг оси, 8 за цикл: стартуют у острия Size ×0.5, за 1 с уходят назад на 12, вращаются 400°, Transparency 0.2 → 1.
- Осколки — ParticleEmitter: меш осколка `#1C1626` / `#6A2AA8`, Size 0.45, Rate 8, Lifetime 1 с, RotSpeed ±500, Speed 3–5.
- Дым — ParticleEmitter на TrailRoot: `#4A1F78`, Size 0.6 → 1.8 → 0, Transparency 0.2 → 1, Rate 7, Lifetime 1 с.
- Кольца — Neon `#B45CFF`, 3 за цикл, как в прочих копьях: от острия на 6.5 назад, ×0.5 → 2.1.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0.07–0.8 | два светящихся разреза крестом (длина 3.6, ширина 0.2, под ±38° к оси X) вырастают по длине от 0.1 до 1.0 за 0.13 с, держатся до 0.77 с, потом сужаются и гаснут | `slash` ×2, Neon `#B45CFF`, внутри тонкая белая полоса `#F2D8FF`, Tween Size (длина) и Transparency |
| 0.07–0.67 | тёмный пузырь пустоты вздувается r 0.6 → 1.3 (×2.0) и дрожит | Neon-шар `void_bubble` `#C070FF` (обод) и тёмный шар внутри `#0A0412`, Tween Size 0.4 → 2.4 |
| 0.67–0.8 | пузырь лопается: шар растёт до ×3.3 и исчезает | Tween Size → 3.3, Transparency → 1 |
| 0.7–1.33 | 12 осколков (`shard`) из центра разлетаются на 1.4–3.0, кувыркаются | Burst 12: меш `shard` `#1C1626` / `#6A2AA8`, Size 0.5, RotSpeed ±400, Lifetime 0.6–0.9 |
| 0.7–1.13 | кольцо `#FF6AF0` расходится от 0.3 до 5 | Neon-меш кольца, Tween Size, Transparency 0 → 1 |
| 0.1–1.33 | 6 полумесяцев-разрезов разлетаются по ветру на 2.6 | `crescent` ×6, Neon `#B45CFF` / `#FF6AF0`, Tween CFrame и Transparency |
| 0.7–1.33 | 6 тёмных клубов дыма поднимаются на 1.6–2.8 | ParticleEmitter Burst 6: `#4A1F78`, Size 0.8 → 2.5, Lifetime 0.8 |
| 0.07–1.33 | 10 фиолетовых искр | Burst 10: `#F0D0FF`, Size 0.16, Lifetime 1 |

Свет: PointLight `#B45CFF`, Range 10, Brightness 2, мигает во время разрезов, вспышка 4 на 0.1 с при хлопке.

---

## 39 astral_armillary — Astral Armillary (stars)

**FX_Idle** — золотое мерцание сфер:
- PointLight на Tip: цвет `#FFE8A0`, Range 9, Brightness 1.
- ParticleEmitter звёздочек: Texture «звёздочка», `#FFFBE0`, Size 0.15–0.2, Rate 4, Lifetime 0.6 с, LightEmission 1.
- ParticleEmitter пылинок: `#FFFBE0`, Size 0.05–0.08, Transparency 0.2 → 1, Rate 6, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180.

**FX_Flight** (цикл 1 с):
- Звёзды — ParticleEmitter: Texture «5-лучевая звезда», цвета `#FFE680` / `#FFFBE0` / `#7AE8FF`, Size 0.4, Rate 10, Lifetime 1 с, RotSpeed ±540, Speed 3–5, SpreadAngle 30.
- Кольца-орбиты — Neon-меш `armillary_ring`, цвета `#FFE680` / `#7AE8FF` / `#FF8AD8`, 3 за цикл, у каждого свой наклон (−50°, 0°, +50°): от острия на 6.5 назад, растут ×0.5 → 2.1, вращаются 360°, Transparency 0.2 → 1.
- Искры — ParticleEmitter, `#FFFBE0`, Size 0.12, Rate 10, Lifetime 0.8 с.
- Золотая пыль — ParticleEmitter на TrailRoot: `#FFD870`, Size 0.6 → 1.6 → 0, Transparency 0.2 → 1, Rate 5, Lifetime 1 с.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | золотая вспышка до r 1.9 | Neon-шар `#FFF0B0`, Tween Size 0.8 → 3.2, Transparency 0 → 1 |
| 0.07–1.33 | плоская 8-лучевая звезда r 1.6 на земле растёт 0.4 → 1.5, поворачивается на 160° и гаснет | меш `ground_star`, Neon `#FFE680`, Tween Size, Rotation, Transparency |
| 0.03–1.33 | 6 колец-орбит (наклоны 0°, 60°, −60°, 30°, −30°, 90°) на высоте 1.3 над точкой касания растут с r 0.28 до ×2.2–3.5, вращаются на 360–560° и гаснут | меш `armillary_ring` ×6, Neon `#FFE680`, `#7AE8FF`, `#FF8AD8`, `#FFFBE0`, Tween Size, CFrame, Transparency |
| 0.07–1.2 | 6 планет-шариков летят по наклонным орбитам (радиус 1.9–2.15, один оборот), в конце сжимаются | 6 Neon-шариков `#7AE8FF` / `#FF8AD8` / `#FFE680`, Size 0.28, Tween CFrame по точкам (шаг 0.067 с) |
| 0.03–1.33 | 14 звёзд разлетаются на 0.8–2.6 и поднимаются до 1–3.2, вращаются | Burst 14: Texture «5-лучевая звезда» `#FFE680` / `#FFFBE0`, Size 0.3–0.5, RotSpeed ±300, Lifetime 1.2, LightEmission 1 |
| 0.1–1.33 | 8 искр и 6 звёздочек-пылинок взлетают | Burst 14: `#FFFBE0`, Size 0.12–0.25, Lifetime 1 |

Свет: PointLight `#FFE8A0`, Range 12, Brightness 2, гаснет за 0.5 с.

---

## 40 singularity_spire — Singularity Spire (stars)

**FX_Idle** — горизонт событий:
- PointLight на кольце-раме: цвет `#8A50E0`, Range 9, Brightness 0.9.
- ParticleEmitter частиц: `#FFF2D0` / `#FF9A2A`, Size 0.05–0.1, Transparency 0.2 → 1, Rate 7, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180.
- ParticleEmitter бликов: Texture «звёздочка», `#FFF2D0`, Size 0.15, Rate 1, Lifetime 0.5 с, LightEmission 1.

**FX_Flight** (цикл 1 с):
- Частицы вихрем — ParticleEmitter: `#FFF2D0` / `#FF9A2A`, Size 0.14, Rate 12, Lifetime 1 с; стартуют на кольце r 1.6, сжимаются к оси (Acceleration к оси), уходят назад.
- Тёмные блоки — ParticleEmitter: меш шестигранника `#2C2238`, Size 0.3, Rate 6, Lifetime 1 с, RotSpeed ±500, Speed 3–5.
- Дым — ParticleEmitter на TrailRoot: `#3A1A5A`, Size 0.6 → 1.8 → 0, Transparency 0.2 → 1, Rate 8, Lifetime 1 с.
- Кольца — Neon-меш `horizon_ring` r 1.0, цвета `#FF9A2A` / `#A45AFF`, 3 за цикл: от острия на 6.8 назад, сжимаются ×1.2 → 0.2, Transparency 0.2 → 1.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0.07–0.57 | тёмный шар (ядро имплозии, `#06030A`) растёт r 0.3 → 1.2 и сжимается обратно к 0.1 | меш `dark_disc`, Tween Size, Transparency 0.1 |
| 0.03–0.57 | 26 частиц с радиуса 2.4–3.8 (высота 0.4–2.6) втягиваются в центр по изогнутой траектории и сжимаются | 26 `particle` Neon `#FFF2D0` / `#FF9A2A`, Size 0.18, Tween CFrame (Quad In) к точке над касанием на высоте 0.9, либо ParticleEmitter Burst 26 с Acceleration к центру |
| 0.5–0.87 | вспышка: шар `#FFE8C0` до r 1.7 за 0.13 с, затем гаснет | Neon-шар, Tween Size 0.3 → 3.6, Transparency |
| 0.53–1.33 | два кольца-вспышки (`#FF9A2A`, `#FFF2D0`) расходятся от 0.4 до r 6 и гаснут | меш `horizon_ring` ×2, Tween Size, Transparency |
| 0.53–1.27 | 7 ступенчатых чёрных столбов (высота 2.1, 4 ступени) растут по кругу r 1.75–2.1 с шагом 0.03 с, перебор ×1.15, держатся до 1.13 с | меш `pillar` `#18121F` / `#2C2238`, Tween Size по высоте; сверху оранжевое кольцо `#FF9A2A` на 0.56 |

Свет: PointLight `#FF9A2A`, Range 12, при имплозии падает до 0, вспышка 5 на 0.15 с, потом гаснет.

---

## 41 gear_pike — Gear Pike (sparks)

**FX_Idle** — пар и искры над шестернями:
- ParticleEmitter пара: цвет `#FFFFFF`, Size 0.1–0.15, Transparency 0.3 → 1, Rate 3, Lifetime 1.5 с, Speed 0.4 вверх, SpreadAngle 20.
- ParticleEmitter искр: `#FFB030`, Size 0.05, Rate 3, Lifetime 0.8 с.
- ParticleEmitter бликов: Texture «звёздочка», `#FFF0B0`, Size 0.14, Rate 2, Lifetime 0.5 с, LightEmission 1.
- PointLight `#FFC060`, Range 8, Brightness 0.8.

**FX_Flight** (цикл 1 с):
- Шестерёнки — ParticleEmitter: меш/текстура шестерёнки, цвета `#F0C040` / `#D8743A` / `#2A9A9A`, Size 0.5, Rate 8, Lifetime 1 с, RotSpeed ±540, Speed 3–5.
- Пар — ParticleEmitter на TrailRoot: `#FFFFFF` / `#F3DCB8`, Size 0.6 → 1.8 → 0, Transparency 0.1 → 1, Rate 8, Lifetime 1 с, EmissionDirection назад.
- Кольца — Neon-меш, цвет `#FFB030`, 3 за цикл: от острия на 6.5 назад, ×0.5 → 2.1, вращение 360°, Transparency 0.2 → 1.
- Искры — ParticleEmitter, `#FFF0B0`, Size 0.12, Rate 8, Lifetime 0.8 с, Speed 4–6.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | тёплая вспышка до r 1.8 | Neon-шар `#FFE2A0`, Tween Size 0.8 → 3.0, Transparency |
| 0.07–1.33 | плоская шестерня-метка на земле (r 1.5, 14 зубцов) растёт до 1.4 и крутится на 130° | меш `gear_mark`, Neon `#FFB030`, Tween Size, Rotation, Transparency |
| 0–1.2 | 7 шестерён (r 0.3–0.5) разлетаются по дуге, крутятся, падают на землю, катятся | `gear` ×7, цвета `#F0C040` / `#D8743A` / `#2A9A9A`, Part с Velocity 6–10 и AngularVelocity, Gravity как у 12 комьев; затем Tween Size → 0 к 1.2 с |
| 0–1.2 | 8 болтов (`#5A5260`) летят по дуге | Burst 8: Size 0.14, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0.07–1.27 | 3 пружины (r 0.17, высота 0.7) у r 1.3 вырастают и пружинят: высота ×1.7 → 0.6 → 1.3 → 0.8 → 1.1 → 1.0 с шагом 0.13 с | меш `spring` `#5A5260`, Tween Size по Y (Elastic Out) |
| 0.07–1.33 | 10 клубов пара поднимаются на 1.8–3.4 и растут до ×2.2 | `steam` ParticleEmitter Burst 10: `#FFFFFF` / `#F3DCB8`, Size 0.8 → 2.5, Transparency 0.1 → 1, Lifetime 1.3 |
| 0–1.3 | 10 золотых искр разлетаются | Burst 10: `#FFF0B0`, Size 0.14, Lifetime 1 |

Свет: PointLight `#FFE2A0`, Range 10, Brightness 2, гаснет за 0.4 с.

---

## 42 spore_halberd — Spore Halberd (dust)

**FX_Idle** — споры у шляпки:
- ParticleEmitter спор: цвета `#9AFFB0` / `#5CF0E0` / `#FF9AE0`, Size 0.05–0.1, Transparency 0.2 → 1, Rate 9, Lifetime 1.8 с, Speed 0.2, Acceleration (0, 0.3, 0), SpreadAngle 180, LightEmission 1.
- ParticleEmitter бликов: Texture «звёздочка», `#9AFFB0`, Size 0.14, Rate 1, Lifetime 0.5 с.
- PointLight на шляпке: `#9AFFC0`, Range 9, Brightness 0.9.

**FX_Flight** (цикл 1 с):
- Споровые облака — ParticleEmitter на TrailRoot: `#8AFFB8` / `#7AF0E8` / `#FF9EE0`, Size 0.6 → 1.8 → 0, Transparency 0.2 → 1, Rate 9, Lifetime 1 с, EmissionDirection назад.
- Грибки — ParticleEmitter: меш `mushroom` (шляпки `#E86AB8` / `#4AD8C0`), Size 0.35, Rate 6, Lifetime 1 с, RotSpeed ±300, Speed 3–5.
- Светящиеся споры — ParticleEmitter, цвета `#9AFFB0` / `#5CF0E0` / `#FF9AE0`, Size 0.14, Rate 12, Lifetime 0.8 с, LightEmission 1.
- Кольца — Neon, `#9AFFB0` / `#5CF0E0`, 3 за цикл: от острия на 6.5 назад, ×0.5 → 2.1, Transparency 0.2 → 1.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | бледно-зелёная вспышка до r 1.8 | Neon-шар `#D8FFE8`, Tween Size 0.8 → 3.0, Transparency |
| 0–0.6 | кольцо `ground_ring` r 0.6 → 2.5 по земле, гаснет | Neon `#9AFFB0`, Tween Size, Transparency |
| 0–1.33 | 16 споровых облаков (3 цвета) разлетаются на 1.0–2.8 (назад дальше), растут до ×2.4 | `spore_cloud` ParticleEmitter Burst 16: цвета `#8AFFB8` / `#7AF0E8` / `#FF9EE0`, Size 0.9 → 2.4, Transparency 0.2 → 1, Lifetime 1.3, Speed 3, Drag 2 |
| 0.03–1.33 | 20 светящихся спор поднимаются на 1.2–2.2, дрейфуют до 2.6–4.2 и гаснут | Burst 20: `#9AFFB0` / `#5CF0E0` / `#FF9AE0`, Size 0.12–0.2, LightEmission 1, Acceleration (0, 1, 0), Lifetime 1.3 |
| 0.1–1.27 | 7 грибов вырастают по кругу r 1.5–2.5 с шагом 0.03 с: пружинят ×1.2/0.8 → 0.95/1.15 → 1.0 за 0.33 с, держатся до 1.13 с | меш `mushroom` (`#E86AB8` / `#4AD8C0`), Tween Size с Back Out; на шляпке зелёная светящаяся точка `#9AFFB0` |
| 1.2–1.33 | грибы и споры уменьшаются в 0 | Tween Size → 0 |

Свет: PointLight `#9AFFC0`, Range 11, Brightness 1.5, плавно гаснет за 1.2 с.

---

## 43 bone_glaive — Bone Glaive (shards)

**FX_Idle** — костяная пыль и янтарные искры:
- ParticleEmitter пыли: цвета `#F2E8CC` / `#CDB890`, Size 0.06–0.1, Transparency 0.3 → 1, Rate 6, Lifetime 1.5 с, Speed 0.2, SpreadAngle 180.
- ParticleEmitter бликов: Texture «звёздочка», `#FFE090`, Size 0.14, Rate 1.5, Lifetime 0.5 с, LightEmission 1.
- PointLight `#FFD890`, Range 8, Brightness 0.7.

**FX_Flight** (цикл 1 с):
- Костяные щепки — ParticleEmitter: Texture «осколок», цвета `#F4EAD0` / `#D8C4A0`, Size 0.5, Rate 10, Lifetime 1 с, RotSpeed ±500, Speed 3–5, SpreadAngle 30.
- Пыль — ParticleEmitter на TrailRoot: `#F2E8CC` / `#CDB890`, Size 0.6 → 1.8 → 0, Transparency 0.2 → 1, Rate 9, Lifetime 1 с, EmissionDirection назад.
- Позвонки — ParticleEmitter: меш `vertebra`, `#D8C4A0`, Size 0.4, Rate 4, Lifetime 1 с, RotSpeed ±400.
- Кольца — Neon `#FFA028`, 3 за цикл: от острия на 6.5 назад, ×0.5 → 2.1, Transparency 0.2 → 1.
- Искры — ParticleEmitter, `#FFE090`, Size 0.12, Rate 6, Lifetime 0.8 с.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | тёплая вспышка до r 1.8 | Neon-шар `#FFF0C8`, Tween Size 0.8 → 3.0, Transparency |
| 0.07–1.27 | костяной вал `bone_ring` r 0.9 → 2.0 по земле, держится до 1.13 с | меш `bone_ring`, цвет `#F4EAD0`, Tween Size (Back Out), потом → 0 |
| 0.07–1.27 | 10 рёбер (длина дуги ≈ 3.3, радиус 2.1, высота 2.5) вырастают из земли по кругу с шагом 0.03 с в 5 волн; растут по высоте с перебором ×1.15 и смыкаются арками к центру, как грудная клетка; держатся до 1.13 с | меш `rib` ×10 (`#F4EAD0` / `#D8C4A0`), Tween Size по Y (Back Out) 0.02 → 1.15 → 1.0; в Roblox ставим вокруг точки удара поворотом 36° |
| 0–1.2 | 5 позвонков вылетают по дуге, падают, катятся | `vertebra` ×5, Part с Velocity 6–10 вверх, Gravity, Tween Size → 0 к 1.2 с |
| 0–1.1 | 10 осколков кости и камня | Burst 10: Texture «осколок» `#F4EAD0` / `#8A7A6A`, Size 0.2–0.3, Speed 6–10 вверх, Acceleration (0, −25, 0), Lifetime 1.1 |
| 0–1.33 | 14 клубов костяной пыли разлетаются на 1.4–2.8 (назад дальше), растут до ×2.3 | ParticleEmitter Burst 14: `#F2E8CC` / `#CDB890`, Size 0.8 → 2.3, Transparency 0.1 → 1, Lifetime 1.3, Speed 3, Drag 3 |
| 0–1.3 | 8 янтарных искр | Burst 8: `#FFE090`, Size 0.14, Lifetime 1 |

Свет: PointLight `#FFD890`, Range 10, Brightness 1.5, гаснет за 0.4 с.

---

## 44 pearl_lance — Pearl Lance (ice)

**FX_Idle** — пузырьки у жемчужины:
- ParticleEmitter пузырей: Texture «пузырь с ободком», цвет `#DFFBFF`, Size 0.1–0.2, Transparency 0.2 → 1, Rate 7, Lifetime 1.8 с, Speed 0.4 вверх, SpreadAngle 30.
- ParticleEmitter бликов: Texture «звёздочка», `#FFF0B0`, Size 0.14, Rate 1.5, Lifetime 0.5 с, LightEmission 1.
- PointLight на жемчужине: `#C8F8FF`, Range 8, Brightness 0.8.

**FX_Flight** (цикл 1 с):
- Пузырьки — ParticleEmitter на TrailRoot: `#DFFBFF`, Size NumberSequence 0.2 → 0.6 → 0, Transparency 0.1 → 1, Rate 14, Lifetime 1 с, EmissionDirection назад, Speed 2–4, SpreadAngle 25.
- Жемчужины — ParticleEmitter: Texture «жемчужина» `#F6F0FF`, Size 0.2, Rate 8, Lifetime 1 с, Speed 3–5.
- Ракушки — ParticleEmitter: меш `shell_rib`, цвета `#FFB0C8` / `#FF7A68`, Size 0.5, Rate 6, Lifetime 1 с, RotSpeed ±300.
- Кольца — Neon, `#7FF4FF`, 3 за цикл: от острия на 6.5 назад, ×0.5 → 2.1, Transparency 0.2 → 1.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.4 | белая вспышка до r 1.8 | Neon-шар `#FFFFFF`, Tween Size 0.8 → 3.0, Transparency |
| 0.13–1.3 | пузырь-купол `bubble_dome` r 1.0 вырастает до 2.7×2.7×2.1, держится, к 1.13 с — до 3.4×2.6 и лопается | меш `bubble_dome`, цвет `#D8FCFF`, Transparency 0.4 → 1, Tween Size (Quad Out) |
| 0.1–1.2 | 7 створок-ракушек (длина 1.5, ширина 0.75) лежат на земле веером в 180° перед копьём, поочерёдно растут от центра | меш `shell_rib` ×7, цвета `#FF7A68` / `#FFB0C8`, Tween Size 0 → ×1.5, Rotation шагом 30° |
| 0.07–1.27 | 11 ледяных шипов выстреливают веером в форме раковины (радиус 1.3–2.2, высота 1.3–2.3, самые высокие в центре), перебор ×1.2, держатся до 1.13 с | меш `ice_spike` ×11, цвет `#C8F6FF`, Material Neon слабо, Tween Size по Y (Back Out), отклонение наружу 20° |
| 0–1.2 | 9 жемчужин (r 0.11–0.17) разлетаются по дуге веером вперёд и назад, отскакивают 2–3 раза по 45% высоты | `pearl` ×9, Part Ball с Velocity 6–10, Elasticity 0.5, Gravity, Tween Size → 0 к 1.2 с |
| 0.07–1.33 | 10 пузырей поднимаются на 2.2–3.8 | ParticleEmitter Burst 10: Texture «пузырь» `#DFFBFF`, Size 0.2–0.4, Speed 3–6, Lifetime 1.2 |
| 0.1–1.33 | 8 золотых звёзд разлетаются | Burst 8: `#FFF0B0`, Size 0.2, Lifetime 1 |

Свет: PointLight `#C8F8FF`, Range 11, Brightness 1.5, гаснет за 1.0 с.

---

## 45 rift_conductor — Rift Conductor (sparks)

**FX_Idle** — статика на электродах:
- PointLight на электродах: цвет `#B070FF`, Range 9, Brightness 1.
- ParticleEmitter искр: `#F4EAFF` / `#B45CFF` / `#7AF0FF`, Size 0.04–0.08, Transparency 0.2 → 1, Rate 7, Lifetime 1.2 с, Speed 0.5, SpreadAngle 180.
- ParticleEmitter бликов: Texture «звёздочка», `#F4EAFF`, Size 0.15, Rate 1.5, Lifetime 0.4 с, LightEmission 1.

**FX_Flight** (цикл 1 с):
- Молнии — ParticleEmitter: Texture «зигзаг» (короткая молния), цвета `#F4EAFF` / `#B45CFF` / `#7AF0FF`, Size 0.9, Rate 9, Lifetime 1 с, RotSpeed ±300, Speed 3–5, SpreadAngle 30, LightEmission 1.
- Кольца — Neon-меш, цвета `#B45CFF` / `#7AF0FF`, 3 за цикл: от острия на 6.8 назад, ×0.5 → 2.1, Transparency 0.2 → 1.
- Искры — ParticleEmitter, `#F4EAFF`, Size 0.12, Rate 10, Lifetime 0.8 с, Speed 4–6.
- Дым — ParticleEmitter на TrailRoot: `#5A2A90`, Size 0.6 → 1.6 → 0, Transparency 0.2 → 1, Rate 6, Lifetime 1 с.

**FX_Impact** (1.5 с):

| t, с | что происходит | чем повторить |
|---|---|---|
| 0.03–0.97 | по кругу r 3.1 на высоте 2.3–2.7 зажигаются 8 узлов-шаров (r 0.16, поочерёдно за 4 кадра), горят до 0.73 с | `node` ×8, Neon `#F4EAFF` / `#7AF0FF`, Size 0.35, Tween Size 0 → 1.3 за 0.1 с, потом → 0 |
| 0.1–0.7 | от каждого узла бьют 2 молнии (толстая цветная + тонкая белая) в копьё, мерцают 3 раза: вкл 0.03 с, выкл 0.03 с, вкл 0.07 с, выкл 0.03 с, вкл 0.13 с | `bolt` ×16, Neon `#F4EAFF` / `#B45CFF` / `#7AF0FF`, Part-цепочка из 6 звеньев по зигзагу (амплитуда 0.3), Transparency 0 ↔ 1 ступеньками |
| 0.07–0.87 | электрическое ядро у острия: шар r 0.5 → 1.8 за 0.2 с, пульсирует до 0.4 с, потом ×2.4 и гаснет | Neon-шар `#E8C8FF`, Tween Size, Transparency |
| 0.17–1.2 | три кольца `#B45CFF`, `#F4EAFF`, `#7AF0FF` (r 0.6) расходятся по земле до ×5.2 (тоньше с каждым) с шагом 0.1 с и гаснут | меш `electric_ring` ×3, Tween Size, Transparency 0 → 1 |
| 0.3–1.17 | 6 фиолетовых трещин длиной 1.4–2.4 разбегаются по земле, гаснут к 1.17 с | `ground_crack` ×6, Neon `#B45CFF`, Tween длины |
| 0.2–1.33 | 12 искр разлетаются на 0.6–2.4 и взлетают до 3 | Burst 12: `#F4EAFF` / `#B45CFF` / `#7AF0FF`, Size 0.14, LightEmission 1, Lifetime 1 |

Свет: PointLight `#B070FF`, Range 13, Brightness 3 с мерцанием 3 раза, гаснет к 1.0 с.

---

## 46 primal_fang — Primordial Fang (fire)

**FX_Idle** — жар и угли:
- Тепловая аура — Neon-эллипсоид `#FF8A3A`, Transparency 0.85, вокруг клыка, лёгкая пульсация Size ±5% за 1 с.
- Кольцо у основания клыка — Neon `#FFD25A`, r 0.46.
- Угли — ParticleEmitter:
  - Texture «язычок», цвета `#FFC23A` / `#FF5A14`;
  - Size 0.15–0.25, Rate 8, Lifetime 1 с;
  - Acceleration (0, 1.5, 0), LightEmission 1.
- PointLight `#FF7A2A`, Brightness 1.2, Range 6.

**FX_Flight** (цикл 1 с) — комета:
- Языки пламени — меш `fx_flame_tongue`, Neon, 14 на цикл:
  - цвета `#FF5A14`, `#FFC23A`, `#E0302A` по очереди;
  - направлены назад;
  - Size ×1.4 → ×0.8, тянутся на 11.5 назад и расходятся до 0.9 в стороны.
- Искры — ParticleEmitter:
  - цвет `#FFC23A`, Size 0.12, Rate 12, Lifetime 0.9 с;
  - Speed 4, SpreadAngle 45, LightEmission 1.
- Огненные кольца — меш `fx_fire_ring`, Neon `#FF5A14` / `#FFC23A`, 3 на цикл:
  - уходят на 6 назад, Size ×0.5 → ×2.0;
  - вращаются 360° за цикл.
- Дым — ParticleEmitter за хвостом:
  - цвет `#4A3440`, Size 0.4 → 1.8, Transparency 0.2 → 1;
  - Rate 8, Lifetime 1 с.
- PointLight `#FF7A2A`, Brightness 2, Range 10.

**FX_Impact** (1.5 с) — «извержение кальдеры»:

| t, с | что происходит | чем повторить |
|---|---|---|
| 0–0.33 | вспышка r 0.5 → 1.6, гаснет | Neon-шар `#FFD08A`, Transparency 0 → 1 |
| 0–0.6 | центральный столб огня высотой 2.6 вырастает за 0.17 с и опадает | меш `fx_flame` Size ×1.63 (высота 2.6), Neon `#FFC23A` |
| 0–0.23 | 9 светящихся трещин длиной 1.6–2.6 раскрываются лучами | Neon-Part `#FF6A1A` толщиной 0.1 вдоль земли, Tween длины, старт с шагом 0.03 с |
| 0.07–0.37 | лавовое кольцо r 0.9 растёт до ×1.5, к концу ×1.7 и гаснет | меш `fx_lava_ring`, Neon `#FF6A1A` |
| 0.1–1.0 | 7 огненных столбов по кругу r 1.45 по очереди (шаг 0.03 с) вспыхивают до высоты 2.0 и опадают | меш `fx_flame` (1.6 высотой), цвета по кругу `#FF5A14` / `#FFC23A` / `#E0302A` |
| 0–1.1 | 10 расплавленных камней разлетаются по дуге | меш `fx_molten_rock`: чёрные `#3A2F45` и Neon `#FF6A1A` поочерёдно; Burst Speed 8–13, Acceleration (0, −27, 0) |
| 0.13–1.33 | 10 клубов дыма поднимаются на 2.2–3.6 и растут до ×2.6 | ParticleEmitter Burst 10: `#4A3440`, Size 0.5 → 2.4, Transparency 0.1 → 1, Lifetime 1.2 |
| 1.0–1.33 | трещины тлеют (Transparency 0 → 1), кольцо тает | Tween Transparency |

Свет: PointLight `#FF7A2A`, Brightness 6 (t = 0) → 2 (0.5 с) → 0 (1.3 с), Range 14.
