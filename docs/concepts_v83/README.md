# V83: гантели и стенды в аниме-стиле (Claude Design, Blender)

15 гантелей и 15 стендов CAMP GYM, сделаны в Blender по промпту для Claude Design. С V85 встроены в игру.

- `gym_anime.blend` — все модели в одной сцене; `scripts/` — скрипты сборки (`gymlib.py`, `db_NN.py`, `st_NN.py`, `report.json`).
- `renders/`, `sheet_dumbbells.png`, `sheet_stands.png`, `scale.png` — рендеры.
- `export/` — GLB без эффектов: гантель — гриф вдоль X, верх Y, начало в центре хвата; стенд — начало в середине пола, лицом к +Z.
  Пара на стенде стоит в (±cx, hz, 0): cx и hz считаются в `st_NN.py` (для 1, 8, 15 заданы числами в вызове `display`).
- `fx_table.md` — какие эффекты у каждого уровня и чем их повторить в Roblox (без Beam и Trail: их убрали у питомцев).

### Как встроены (V85)
- GLB из `export/` загружены в Roblox (Open Cloud через Studio MCP `open_cloud_invoke`) из папки `C:\SpearHuntAssets`,
  разрешённой в Assistant Settings → MCP Permissions у закрытой копии места «SpearHunt Test (assets)». Номера: `asset_ids.json`.
- Импорт делит модель на MeshPart по материалам, теряет цвета и разворачивает её на 180° вокруг Y. `scripts/bake_gym_meshes.lua`
  (выполнялся в Studio) красит каждую деталь цветом материала из GLB (светящиеся — Neon), возвращает разворот, ставит начало
  модели в начало GLB и пишет на стенды место пары (`PairX`, `PairY`). Результат — папка `ReplicatedStorage.GymMeshes`
  (DB_01..DB_15, ST_01..ST_15), сохранённая в место V85.
- `Util.dumbbell` и `Util.gymRack` берут модели из `GymMeshes`; если папки или модели нет, строят прежние модели из деталей.
- Эффекты: искры и свет по таблице `fx_table.md` (без Beam и Trail).
- Снимки из игры: `game_stand_08.png`, `game_stand_15.png`.
