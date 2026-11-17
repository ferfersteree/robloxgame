#!/usr/bin/env python3
"""Одна команда проверки репозитория перед тем, как назвать работу законченной.

    python tools/check.py

Что проверяется (всё без Studio и без сети, ничего не исполняется):
  1. синтаксис всех .luau в source/ и tests/            (tools/luau_check.py)
  2. имена без объявления: опечатки, локальные функции ниже места вызова   (tools/luau_names.py)
  3. модели копий 41-46: блок EXTRA в SpearFactoryV15.luau совпадает с тем, что рисует tools/spear_models.py,
     в каждой модели не больше 1100 кубиков
  4. в README.md назван «новейший» файл места и он лежит в корне репозитория
  5. в отслеживаемых текстовых файлах нет присвоенного значения ключа ROBLOX_API_KEY
  6. код в source/ совпадает с кодом в новейшем файле места из README (tools/place_vs_repo.py; около 15 секунд;
     пропустить: python tools/check.py --fast)
Код возврата 0 только если всё в порядке. Это не заменяет проверку в Studio (звук, вид, ввод, DataStore).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
results: list[tuple[str, bool, str]] = []


def run(label: str, args: list[str]) -> None:
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (p.stdout.strip().splitlines() or [""])[-1]
    ok = p.returncode == 0 and "with errors" not in tail.replace("0 with errors", "") and not tail.startswith("FAIL")
    if p.returncode == 0 and "suspicious" in tail:
        ok = tail.startswith("checked") and " 0 suspicious" in tail
    results.append((label, ok, tail if ok else (p.stdout + p.stderr).strip()[-800:]))


def check_models() -> None:
    sys.path.insert(0, str(TOOLS))
    import spear_models as sm  # noqa: E402

    factory = (ROOT / "source/ReplicatedStorage/V15SpearPresentation/SpearFactoryV15.luau").read_bytes().decode("utf-8").replace("\r\n", "\n")
    a, b = factory.find("-- BEGIN V51 EXTRA"), factory.find("-- END V51 EXTRA")
    fresh = sm.lua_block()
    same = a >= 0 and b >= 0 and factory[a : b + len("-- END V51 EXTRA")] == fresh
    big = [f"{k}={len(v['vox'])}" for k, v in sm.build_all().items() if len(v["vox"]) > 1100]
    msg = "блок EXTRA совпадает с рисунком" if same else "блок EXTRA устарел: python tools/spear_models.py patch"
    if big:
        msg += "; слишком много кубиков: " + ", ".join(big)
    results.append(("модели копий 41-46", same and not big, msg))


def check_readme() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"Новее всех: `([^`]+\.rbxl)`", text)
    if not m:
        results.append(("README: новейший файл места", False, "в README.md нет строки «Новее всех: `….rbxl`»"))
        return
    ok = (ROOT / m.group(1)).is_file()
    results.append(("README: новейший файл места", ok, m.group(1) + (" найден" if ok else " НЕ найден в корне")))


def check_secrets() -> None:
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    bad = []
    pat = re.compile(r"ROBLOX_API_KEY\s*[=:]\s*[\"']?[A-Za-z0-9+/_\-]{24,}")
    for f in files:
        if not f.lower().endswith((".py", ".md", ".luau", ".txt", ".json", ".js", ".html", ".yml", ".yaml", ".cmd", ".ps1", ".sh")):
            continue
        try:
            t = (ROOT / f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if pat.search(t):
            bad.append(f)
    results.append(("ключ Roblox в файлах", not bad, "не найден" if not bad else "найден в: " + ", ".join(bad)))


def check_place() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"Новее всех: `([^`]+\.rbxl)`", text)
    if not m or not (ROOT / m.group(1)).is_file():
        results.append(("код совпадает с файлом места", False, "нет новейшего файла места"))
        return
    p = subprocess.run([sys.executable, "tools/place_vs_repo.py", m.group(1)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [l for l in p.stdout.strip().splitlines() if l.strip()]
    shown = lines[0] if p.returncode == 0 and lines else "; ".join(lines[:12])
    results.append(("код совпадает с файлом места", p.returncode == 0, shown[:600]))


def main() -> int:
    run("синтаксис .luau (source, tests)", ["-I", "tools/luau_check.py", "source", "tests"])
    run("имена без объявления", ["tools/luau_names.py", "source", "tests"])
    check_models()
    check_readme()
    check_secrets()
    if "--fast" not in sys.argv:
        check_place()
    width = max(len(r[0]) for r in results)
    bad = 0
    for label, ok, msg in results:
        print(f"{'OK  ' if ok else 'FAIL'} {label.ljust(width)}  {msg}")
        bad += 0 if ok else 1
    print("\nВСЁ В ПОРЯДКЕ" if not bad else f"\nпровалено проверок: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
