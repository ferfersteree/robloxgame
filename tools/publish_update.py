#!/usr/bin/env python3
"""Publish one update of the game into the `updates/` folder of the repository and push it.

    python tools/publish_update.py V40 short-slug --title "What this update is" --readme path/to/README.md FILE [FILE ...]

What it does
  1. copies the given files into  updates/<ID>_<date>_<slug>/  (place files at the top, .luau into scripts/,
     sounds into audio/, .html into preview/, everything else into files/) and writes README.md there,
  2. adds a row to the index  updates/README.md  (newest first),
  3. commits ONLY the updates/ folder on the current branch and pushes it,
  4. mirrors the whole updates/ folder to the `main` branch (the one GitHub shows on the front page) through a temporary
     checkout and pushes it. Nothing else on `main` is touched. Skip with --no-main.

Other options: --date YYYY-MM-DD, --ref REV (take the files from that commit instead of the working tree, for
back-filling), --status TEXT (index column), --trailer LINE (repeatable, appended to the commit message),
--no-push (commit only), --dry-run (print the plan, change nothing). It never force-pushes.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HEADER = (
    "# Обновления игры\n\n"
    "Здесь лежит каждое обновление: файл места для Studio, изменённые скрипты, новые звуки и описание. "
    "Новые сверху. Файлы места открываются в Roblox Studio: File → Open from File.\n\n"
    "| Версия | Дата | Что внутри | Папка | Статус |\n"
    "|---|---|---|---|---|\n"
)


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stdout}{r.stderr}")
    return r.stdout.strip()


def dest_for(path):
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower()
    if ext == ".rbxl":
        return name
    if ext in (".luau", ".lua"):
        return "scripts/" + name
    if ext in (".ogg", ".wav", ".mp3"):
        return "audio/" + name
    if ext == ".html":
        return "preview/" + name
    if ext == ".md":
        return "docs/" + name
    return "files/" + name


def read_file(path, ref):
    if ref:
        r = subprocess.run(["git", "show", f"{ref}:{path.replace(os.sep, '/')}"], cwd=ROOT, capture_output=True)
        if r.returncode != 0:
            sys.exit(f"cannot read {path} at {ref}: {r.stderr.decode(errors='replace')}")
        return r.stdout
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with open(full, "rb") as f:
        return f.read()


def update_index(folder_name, a):
    p = os.path.join(ROOT, "updates", "README.md")
    text = INDEX_HEADER
    if os.path.exists(p):
        text = open(p, encoding="utf-8").read().replace("\r\n", "\n")
        if "|---|---|---|---|---|" not in text:
            text = INDEX_HEADER + text
    row = f"| {a.id} | {a.date} | {a.title} | [{folder_name}]({folder_name}/) | {a.status} |\n"
    # replace an existing row for the same id, else insert on top of the table
    lines = text.split("\n")
    lines = [l for l in lines if not l.startswith(f"| {a.id} |")]
    sep = next(i for i, l in enumerate(lines) if l.startswith("|---|---|"))
    lines.insert(sep + 1, row.rstrip("\n"))
    out = "\n".join(lines)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8", newline="\n").write(out)


def mirror_to_main(message, trailers):
    """Copy updates/ into a temporary checkout of origin/main, commit and push (fast-forward only)."""
    git("fetch", "-q", "origin", "main")
    tmp = tempfile.mkdtemp(prefix="rg_main_")
    os.rmdir(tmp)
    git("worktree", "add", "--detach", "-q", tmp, "origin/main")
    try:
        dst = os.path.join(tmp, "updates")
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(ROOT, "updates"), dst)
        git("add", "-A", "--", "updates", cwd=tmp)
        if not git("status", "--porcelain", "--", "updates", cwd=tmp):
            print("main: the updates/ folder is already up to date")
            return
        msg = [message + " (updates/ folder only)"] + ([""] + trailers if trailers else [])
        git("commit", "-q", "-m", "\n".join(msg), cwd=tmp)
        out = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=tmp, capture_output=True, text=True)
        if out.returncode != 0:
            sys.exit("push to main failed (not forced):\n" + out.stdout + out.stderr)
        print("main: pushed", git("rev-parse", "--short", "HEAD", cwd=tmp))
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", tmp], cwd=ROOT, capture_output=True)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, capture_output=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("id", help="version id, e.g. V40")
    ap.add_argument("slug", help="short ascii name for the folder, e.g. egg-sounds")
    ap.add_argument("files", nargs="+", help="repository paths to include")
    ap.add_argument("--title", required=True)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--status", default="не проверено в игре")
    ap.add_argument("--readme", help="markdown file used as the README of this update")
    ap.add_argument("--ref", help="read the files from this commit instead of the working tree")
    ap.add_argument("--trailer", action="append", default=[])
    ap.add_argument("--no-main", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", a.slug):
        sys.exit("slug must be ascii letters, digits, - _ .")
    folder_name = f"{a.id}_{a.date}_{a.slug}"
    folder = os.path.join(ROOT, "updates", folder_name)
    plan = [(f, dest_for(f)) for f in a.files]
    print(f"update folder: updates/{folder_name}")
    for src, dst in plan:
        print(f"  {src}  ->  {dst}")
    if a.dry_run:
        print("dry run: nothing written")
        return

    os.makedirs(folder, exist_ok=True)
    for src, dst in plan:
        data = read_file(src, a.ref)
        target = os.path.join(folder, dst)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(data)
    if a.readme:
        shutil.copyfile(a.readme if os.path.isabs(a.readme) else os.path.join(ROOT, a.readme), os.path.join(folder, "README.md"))
    elif not os.path.exists(os.path.join(folder, "README.md")):
        lines = [f"# {a.id}: {a.title}", "", f"Дата: {a.date}", "", "Файлы:", ""] + [f"- `{dst}`" for _s, dst in plan]
        open(os.path.join(folder, "README.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    update_index(folder_name, a)

    message = f"Update {a.id}: {a.title}"
    git("add", "--", "updates")
    if not git("status", "--porcelain", "--", "updates"):
        print("nothing new to commit in updates/")
    else:
        msg = message + ("\n\n" + "\n".join(a.trailer) if a.trailer else "")
        git("commit", "-q", "-m", msg)
        print("committed", git("rev-parse", "--short", "HEAD"), "on", git("rev-parse", "--abbrev-ref", "HEAD"))
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if a.no_push:
        print("--no-push: not pushed")
        return
    out = subprocess.run(["git", "push", "origin", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("push failed (not forced):\n" + out.stdout + out.stderr)
    print(f"pushed branch {branch}")
    if not a.no_main and branch != "main":
        mirror_to_main(message, a.trailer)
    print("view: https://github.com/ferfersteree/robloxgame/tree/main/updates")


if __name__ == "__main__":
    main()
