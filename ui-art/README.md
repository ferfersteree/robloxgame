# Картинки интерфейса (V71)

Нарисованы Астрой (Codex, medium) по концептам из `docs/concepts_v70/`.
- `source/` — листы как их отдала Астра (прозрачный фон).
- `atlas/` — нарезка (`slice.py`), 5 листов 1024x1024 и две широкие картинки; `atlas.json` — где какой спрайт: [лист, x, y, ширина, высота].
- Номера в Roblox (загружены 2026-11-19 через Studio на аккаунт, который был в этот момент открыт в Studio; видели их только в Studio под этим аккаунтом):
  sh_atlas1 112688474389659 · sh_atlas2 117687606442061 · sh_atlas3 82021756938807 · sh_atlas4 138724800947424 · sh_atlas5 132249786424867 ·
  sh_pass_header 103338025764986 · sh_shop_banner 123718365046762 · sh_shop_header_wide 104155622489129 · sh_atlas6 92644721234469 (V74: лавки, питомцы, зелья, яйцо Astral; `atlas6.json`)
- В игре: таблица `ART` и функции `UI.art`, `UI.artButton` в `Client/UIKit.luau`.
- V84: `source/dialog_frames.png` (Астра, окно диалога с NPC) → `atlas/sh_atlas7.png`, координаты в `atlas7.json`; в Roblox sh_atlas7 82270850809307 (загружен 2026-11-19 через Studio). Предпросмотр: `preview/dialog_preview.png`.
