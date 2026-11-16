# SpearHunt

## Последние версии: с новой картой и без неё

**Новее всех: `SpearHunt V39 - Egg Sounds.rbxl`** (V38 плюс звук на каждый момент открытия яйца: 70 новых звуков, фанфары по редкости, музыка под карточкой; послушать до загрузки можно в `preview/egg-sounds.html`, описание в `SOUND.md`, раздел V39). Звуки V39 ещё не загружены в Roblox: пока играют прежние похожие.

Предыдущая: `SpearHunt V38 - Cube Shop.rbxl` (на базе V37, с новой картой): магазин в кубическом стиле и 16 своих звуков магазина. Звуки загружены в Roblox, их номера вписаны в `Client/AudioIds` внутри файла (в `source/` остаётся шаблон с пустыми номерами). Подробности: `SHOP.md`, раздел V38.

Два файла места, открывайте любой в Roblox Studio (File → Open from File) и нажмите Play:

- **`SpearHunt V37 - HTML World.rbxl`** — с новой картой. Растения, камни, кристаллы и здания зон из HTML-версии мира строятся кубиками вокруг камеры (`StarterPlayerScripts/Client/HtmlWorld`, данные в `ReplicatedStorage/HtmlWorld`). Выключатель: атрибут `Enabled` у папки `ReplicatedStorage/HtmlWorld` (поставьте false, и карта как в V36).
- **`SpearHunt V36 - Throwing Grounds.rbxl`** — без новой карты. То же самое (зона Throwing Grounds, кубические иконки магазина, 3D-открытие яиц, питомцы), но без HtmlWorld.

Исходники: ветка `donate-eggs` — с новой картой (`source/ReplicatedStorage/HtmlWorld`, `source/.../Client/HtmlWorld.luau`, генератор `tools/html_world_build.py`); ветка `donate-eggs-no-html-world` — то же без новой карты. Файл V36 лежит в обеих ветках, V37 только в `donate-eggs`.
В файлах мест лежат настоящие номера звуков и картинок (`Client/AudioIds`), в `source/` для него шаблон с пустыми номерами.

---

**Играть (старая версия):** откройте `SpearHunt V21 - Final.rbxl` в Roblox Studio (File → Open from File) и нажмите Play.
Это ветка `claude/upbeat-ritchie-4rq2ur`. Файлы в ветке `main` — только исходные загрузки.

В файле уже есть: магазин в новом стиле, 150 существ с анимациями, перевёрнутые таблички, звуковая система.
Чтобы **звуки, музыка и картинки магазина** зазвучали и появились, их нужно один раз загрузить в Roblox:

1. Создайте ключ: https://create.roblox.com/dashboard/credentials → Create API Key → доступ **Assets API: Read и Write** → ключ сохраните.
2. Узнайте свой Roblox user id (число в адресе вашего профиля roblox.com/users/ЧИСЛО/profile).
3. В PowerShell, в папке репозитория (нужен Python 3; `winget install Python.Python.3.12`):

```
$env:ROBLOX_API_KEY = "ваш_ключ"
python tools\upload_to_roblox.py --user-id ВАШ_ID
```

4. Скрипт загрузит 72 звука и 24 картинки (минуты; Roblox проверяет аудио) и создаст `out\AudioIds.luau`.
5. В Studio откройте `StarterPlayer → StarterPlayerScripts → Client → AudioIds`, замените весь текст на содержимое `out\AudioIds.luau`, сохраните игру (Ctrl+S).

6. Если скрипт написал, что картинки ждут шага в Studio, откройте в Studio **View → Command Bar**, вставьте туда содержимое `out\resolve_art_in_studio.lua` и нажмите Enter (один раз): оно заменит номера картинок в `AudioIds`. Снова сохраните игру (Ctrl+S).

Если скрипт написал `FAILED` для какого-то файла, запустите ту же команду ещё раз: готовое он пропускает.
Описания: `MERGE.md` (существа), `SOUND.md` (звук, таблички, коллизии), `SHOP.md` (магазин).
