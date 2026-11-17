#!/usr/bin/env python3
"""Сверка файла места (.rbxl) с папкой source/ репозитория: код в файле и в репозитории должен быть одним и тем же.

    python tools/place_vs_repo.py "SpearHunt V59 - Name.rbxl"          # сверка (код игры, без данных)
    python tools/place_vs_repo.py "SpearHunt V59 - Name.rbxl" --all    # показать и скрипты, которых в репозитории нет (данные)

Что считается: каждый .luau из source/ ищется среди скриптов файла по пути (Service/Папка/Имя); строки сравниваются без
различия LF и CRLF. Различия и скрипты, которых нет в файле, дают ненулевой код возврата. Известное и допустимое различие:
Client/AudioIds (в репозитории шаблон без номеров звуков, в файле настоящие).

Скрипты, которые есть в файле, но не лежат в source/, это в основном данные: движения и модели зверей (V15Fauna/MotionData,
Animation150/Biome*), модели копий (V15SpearPresentation/ModelsData), прикрытия (V15Covers/ModelsData), резервные копии в
ServerStorage. Они не редактируются руками, а создаются инструментами, поэтому в репозиторий не вынесены.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import rbx  # noqa: E402

ALLOWED_DIFF = {"StarterPlayer/StarterPlayerScripts/Client/AudioIds"}
DATA = re.compile(r"(BakedMotion|V15FaunaBackup|V15_SpearBackup|V16FaunaBackup|V15CoverBackup|V21_ShelterBackup|V22_Biome|Animation150/Biome|ModelsData/|NativeVendorActors|MotionData/)")


def place_scripts(path: str) -> dict[str, list[bytes]]:
    inst, parent, props = rbx.parse(path)

    def name_of(i):
        return props.get(i, {}).get("Name", b"?").decode("utf-8", "replace")

    def path_of(i):
        names = []
        while i in parent and parent[i] != -1:
            names.append(name_of(i))
            i = parent[i]
        names.append(name_of(i))
        return "/".join(reversed(names))

    out: dict[str, list[bytes]] = {}
    for i, cls in inst.items():
        if cls in ("ModuleScript", "LocalScript", "Script"):
            src = props.get(i, {}).get("Source")
            if src is not None:
                out.setdefault(path_of(i), []).append(src.replace(b"\r\n", b"\n"))
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    if not args:
        print(__doc__)
        return 2
    place = args[0]
    scripts = place_scripts(place)
    root = os.path.join(ROOT, "source")
    same, diffs, missing = 0, [], []
    repo_paths = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".luau"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")[:-5]
            repo_paths.append(rel)
            data = open(os.path.join(dp, f), "rb").read().replace(b"\r\n", b"\n")
            hits = [k for k in scripts if k.endswith(rel)]
            if not hits:
                missing.append(rel)
            elif any(data in scripts[k] for k in hits):
                same += 1
            elif rel in ALLOWED_DIFF:
                same += 1
            else:
                diffs.append(rel)
    print(f"скриптов в source/: {len(repo_paths)}; совпадают с файлом: {same}; отличаются: {len(diffs)}; нет в файле: {len(missing)}")
    for d in diffs:
        print("  ОТЛИЧАЕТСЯ:", d)
    for m in missing:
        print("  НЕТ В ФАЙЛЕ:", m)
    only = sorted(p for p in scripts if not DATA.search(p) and not any(p.endswith(r) for r in repo_paths))
    print(f"скриптов с кодом в файле, которых нет в source/: {len(only)}")
    for p in only:
        print("  ТОЛЬКО В ФАЙЛЕ:", p)
    if show_all:
        data_only = sorted(p for p in scripts if DATA.search(p))
        print(f"скриптов-данных в файле (не в репозитории): {len(data_only)}")
    return 1 if diffs or missing or only else 0


if __name__ == "__main__":
    sys.exit(main())
