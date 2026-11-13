# SpearHunt

**Играть:** откройте `SpearHunt V21 - Final.rbxl` в Roblox Studio (File → Open from File) и нажмите Play.
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

Если скрипт написал `FAILED` для какого-то файла, запустите ту же команду ещё раз: готовое он пропускает.
Описания: `MERGE.md` (существа), `SOUND.md` (звук, таблички, коллизии), `SHOP.md` (магазин).
