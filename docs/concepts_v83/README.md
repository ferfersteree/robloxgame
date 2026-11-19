# V83: гантели и стенды в аниме-стиле (Claude Design, Blender)

15 гантелей и 15 стендов CAMP GYM, сделаны в Blender по промпту для Claude Design. В игру ещё не встроены.

- `gym_anime.blend` — все модели в одной сцене; `scripts/` — скрипты сборки (`gymlib.py`, `db_NN.py`, `st_NN.py`, `report.json`).
- `renders/`, `sheet_dumbbells.png`, `sheet_stands.png`, `scale.png` — рендеры.
- `export/` — GLB без эффектов: гантель — гриф вдоль X, верх Y, начало в центре хвата; стенд — начало в середине пола, лицом к +Z.
  Пара на стенде стоит в (±cx, hz, 0): cx и hz считаются в `st_NN.py` (для 1, 8, 15 заданы числами в вызове `display`).
- `fx_table.md` — какие эффекты у каждого уровня и чем их повторить в Roblox (без Beam и Trail: их убрали у питомцев).

## Почему ещё не в игре
Меши загружаются в Roblox через Studio MCP (`open_cloud_invoke`, POST /assets/v1/assets), но папку для загрузок
(Assistant Settings → MCP Permissions) можно разрешить только у места, сохранённого в Roblox. Файлы, открытые с диска,
такой настройки не имеют. План: сохранить копию места в Roblox (отдельной игрой), разрешить папку с GLB
(путь без кириллицы, например `C:\SpearHuntAssets`), загрузить 30 моделей, вставить их в ReplicatedStorage и
перевести `Util.dumbbell` и `Util.gymRack` на них, оставив нынешние модели из деталей запасным вариантом.
