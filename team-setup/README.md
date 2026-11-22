# Команда из 4 моделей

| Роль | Модель | Что делает |
|---|---|---|
| Основная сессия | Sonnet 5.5 | пишет код, гоняет тесты |
| Advisor | Fable 5.2 | только советует |
| `checker` | Opus 5.5 | тестирует готовое, пытается сломать, ничего не правит |
| `Explore` + прочие субагенты | Haiku 5.5 | поиск и чтение |

## В этом репозитории
Уже работает: `.claude/settings.json`, `.claude/agents/`, `CLAUDE.md`. Откройте проект в Claude Code.

## Во всех проектах
```bash
bash team-setup/install-user-level.sh
```

## Один раз
`/model fable` > согласиться > `/model sonnet` (нужно, если Fable идёт за usage credits).

## Проверка
`/advisor` показывает fable; `/agents` показывает checker (opus) и Explore (haiku). Когда Fable консультируется, видна строка «Advising», Ctrl+O показывает совет, `/usage` показывает цену.
