#!/usr/bin/env bash
# Ставит команду из 4 моделей на УРОВНЕ ПОЛЬЗОВАТЕЛЯ (работает во всех проектах).
# Запуск из корня репозитория:  bash team-setup/install-user-level.sh
set -e
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="$HOME/.claude"
TS="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DST/agents" "$DST/backups"
bak() { [ -e "$1" ] && cp "$1" "$DST/backups/$(basename "$1").$TS.bak" && echo "backup: $1"; true; }

# settings.json: сливаем, ничего не удаляя
bak "$DST/settings.json"
python3 - "$SRC/.claude/settings.json" "$DST/settings.json" <<'PY'
import json, os, sys
new = json.load(open(sys.argv[1]))
cur = json.load(open(sys.argv[2])) if os.path.exists(sys.argv[2]) else {}
for k, v in new.items():
    if isinstance(v, dict):
        cur.setdefault(k, {}).update(v)
    else:
        cur[k] = v
json.dump(cur, open(sys.argv[2], "w"), indent=2, ensure_ascii=False)
print("merged settings.json:", {k: cur[k] for k in new})
if cur.get("effortLevel") in ("low",):
    print("WARNING: effortLevel=low: Sonnet будет редко звать советника")
PY

for f in checker Explore; do bak "$DST/agents/$f.md"; cp "$SRC/.claude/agents/$f.md" "$DST/agents/$f.md"; done

# CLAUDE.md: дописываем правило, если его ещё нет
bak "$DST/CLAUDE.md"
if ! grep -q "Consult the advisor" "$DST/CLAUDE.md" 2>/dev/null; then
  { [ -s "$DST/CLAUDE.md" ] && echo; cat "$SRC/CLAUDE.md"; } >> "$DST/CLAUDE.md"
fi
echo "Готово. Перезапусти Claude Code. Один раз выполни: /model fable (согласиться), потом /model sonnet."
