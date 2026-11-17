# V59: весь код игры лежит в репозитории

Дата: 2026-11-17 · Файла места нет: игра остаётся `SpearHunt V58 - Spear Icons.rbxl`; в этой папке дерево `source/` с 29 скриптами, которых раньше в репозитории не было.

## Что сделано

До сих пор в `source/` лежали только скрипты, которые я правил, а 29 рабочих скриптов жили только внутри файла места: `UIKit`, `Theme`, `Animator`, `Ambient`, `Guide`, `NativeVendors`, `NativeMotion`, `RevealOcclusion`, `WorldFx`, `ZoneFx`, `IslandTreeLOD_V15`, общие модули `Net`, `Num`, `Util`, `PoseData`, `Server/Main`, `Server/Plots`, `PetsTools/EggEffects`, `V15Covers/*`, `V15Fauna/Factory`, `Animation150/Motion` и `Profiles`, `V15SpearPresentation/{PlayerThrowV15, SpearPresentationV15, MeshVFX/*}`. Теперь все они выгружены из открытой Studio побайтно (контрольная сумма каждого файла совпала) и лежат в `source/` по тем же путям, что в игре. Внутри этой папки обновления они лежат деревом: `source/ReplicatedStorage/...`, `source/StarterPlayer/...`, `source/ServerScriptService/...`.

Итого в `source/` 139 скриптов, и это весь код игры. В файле места остаются только скрипты-данные (610 штук): движения и модели зверей, модели копий и прикрытий, резервные копии. Их никто не правит руками, они создаются инструментами.

## Инструменты

- `tools/place_vs_repo.py`: сверка `source/` с файлом места (139 из 139 совпадают; допустимое различие одно, `Client/AudioIds`: в репозитории шаблон без номеров звуков, в файле настоящие); также ищет скрипты с кодом, которых нет в `source/`.
- `tools/check.py` теперь включает эту сверку (около 15 секунд, `--fast` пропускает её).
- `tools/publish_update.py --keep-tree`: файлы из `source/` кладёт в папку обновления с сохранением структуры.

## Что не проверено

Ничего нового в игре не менялось.
