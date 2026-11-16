"""Build the V39 egg-opening audio: render -> OGG, emit the Luau tables, AudioIds keys, manifest and the preview page.

Run from the repository root:
    python audio/tools/egg_build.py                 # everything
    python audio/tools/egg_build.py --only egg_riser forest_   # render just these (prefixes), still emits the rest
    python audio/tools/egg_build.py --no-render     # only the Luau tables, AudioIds, manifest and preview
Rendering is deterministic (each sound has its own seed), so a sound only changes when its recipe changes.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))

import foley  # noqa: E402
import egg_sounds  # noqa: E402,F401
import egg_music  # noqa: E402,F401
import egg_cues as C  # noqa: E402
from egg_sounds import SOUNDS  # noqa: E402

OGG_DIR = os.path.join(ROOT, "audio", "ogg")
CLIENT = os.path.join(ROOT, "source", "StarterPlayer", "StarterPlayerScripts", "Client")
EGGOPEN = os.path.join(ROOT, "source", "ReplicatedStorage", "PetModules", "EggOpenings.luau")
PREVIEW = os.path.join(ROOT, "preview", "egg-sounds.html")
MANIFEST = os.path.join(ROOT, "audio", "egg_manifest.json")


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = x[None, :]
    pcm = (x.T * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[0])
        w.setsampwidth(2)
        w.setframerate(foley.SR)
        w.writeframes(pcm.tobytes())


def render_all(only, force):
    os.makedirs(OGG_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="egg_wav_")
    info = {}
    for name, s in SOUNDS.items():
        out = os.path.join(OGG_DIR, name + ".ogg")
        wanted = (not only) or any(name.startswith(p) for p in only)
        if os.path.exists(out) and not (force or (only and wanted)):
            continue
        if not wanted and os.path.exists(out):
            continue
        x = s["fn"](foley.rng_for(name))
        kind = s["kind"]
        y = foley.master(x, kind, peak_db=-2.0, rms_db=-22.0 if kind == "loop" else -19.0)
        if not np.isfinite(y).all():
            raise SystemExit(f"{name}: non-finite samples")
        wav = os.path.join(tmp, name + ".wav")
        write_wav(wav, y)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "5", out], check=True)
        os.remove(wav)
        d = foley.describe(y)
        info[name] = d
        print(f"  rendered {name:20s} {d['sec']:5.2f}s peak {d['peak_db']:5.1f} rms {d['rms_db']:6.1f}")
    try:
        os.rmdir(tmp)
    except OSError:
        pass
    return info


def ogg_info(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=channels:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    return float(j["format"]["duration"]), int(j["streams"][0]["channels"])


def write_manifest():
    rows = []
    for name, s in SOUNDS.items():
        p = os.path.join(OGG_DIR, name + ".ogg")
        if not os.path.exists(p):
            continue
        sec, ch = ogg_info(p)
        rows.append(dict(name=name, seconds=round(sec, 2), channels=ch, loop=bool(s["loop"]), kind=s["kind"],
                         ogg_kb=round(os.path.getsize(p) / 1024, 1), use=s["use"]))
    json.dump(rows, open(MANIFEST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"manifest: {len(rows)} sounds, {sum(r['ogg_kb'] for r in rows) / 1024:.2f} MB of ogg")
    return rows


def replace_block(path, begin_prefix, end_prefix, new_block):
    s = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in s
    text = s.replace("\r\n", "\n")
    lines = text.split("\n")
    bi = next(i for i, l in enumerate(lines) if l.startswith(begin_prefix))
    ei = next(i for i, l in enumerate(lines) if l.startswith(end_prefix))
    assert bi < ei
    lines[bi:ei + 1] = new_block.split("\n")
    out = "\n".join(lines)
    if crlf:
        out = out.replace("\n", "\r\n")
    open(path, "w", encoding="utf-8", newline="").write(out)


def update_audio_ids():
    p = os.path.join(CLIENT, "AudioIds.luau")
    raw = open(p, "rb").read()
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    have = set(re.findall(rb"^\t([A-Za-z0-9_]+) = ", raw, re.M))
    missing = [f for f in C.all_files() if f.encode() not in have]
    if not missing:
        print("AudioIds template: nothing to add")
        return
    anchor = b'\tshop_claim = "",' + eol
    assert raw.count(anchor) == 1, "anchor shop_claim not found in the template"
    ins = b"".join(b"\t" + m.encode() + b' = "",' + eol for m in missing)
    open(p, "wb").write(raw.replace(anchor, anchor + ins))
    print(f"AudioIds template: added {len(missing)} keys")


# ------------------------------------------------------------------ preview page
def build_preview(rows):
    events = C.parse_events(EGGOPEN)
    snd = {}
    for r in rows:
        p = os.path.join(OGG_DIR, r["name"] + ".ogg")
        snd[r["name"]] = dict(sec=r["seconds"], loop=r["loop"], use=r["use"], ch=r["channels"],
                              b64=base64.b64encode(open(p, "rb").read()).decode())
    banks = {k: v[0] for k, v in C.BANKS.items()}
    hds = {"fast": 2.7, "mid": 3.0, "long": 3.6}
    timelines = {}
    for fam in C.FAMILY_TIMES:
        for rar in range(7):
            for hk, hd in hds.items():
                timelines[f"{fam}|{rar}|{hk}"] = C.simulate(fam, rar, hd, events[fam])
    data = dict(sounds=snd, banks=banks, timelines=timelines, rarities=C.RARITIES,
                families=[("forest", "Лесной талисман"), ("amber", "Янтарное сердце"), ("tide", "Жемчужина прилива"),
                          ("storm", "Сердце грозы"), ("astral", "Астральное ядро")])
    page = open(os.path.join(HERE, "egg_preview_template.html"), encoding="utf-8").read()
    page = page.replace("/*__DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";")
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    open(PREVIEW, "w", encoding="utf-8").write(page)
    print(f"preview page: {os.path.getsize(PREVIEW) / 1024 / 1024:.2f} MB -> {os.path.relpath(PREVIEW, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-emit", action="store_true")
    a = ap.parse_args()
    if not a.no_render:
        render_all(a.only, a.force)
    rows = write_manifest()
    if not a.no_emit:
        replace_block(os.path.join(CLIENT, "Sfx.luau"), "-- BEGIN GENERATED egg audio", "-- END GENERATED egg audio", C.lua_sfx_block())
        replace_block(os.path.join(CLIENT, "EggOpen3D.luau"), "-- BEGIN GENERATED egg cues", "-- END GENERATED egg cues", C.lua_cues_block())
        print("Luau tables written into Sfx.luau and EggOpen3D.luau")
        update_audio_ids()
        build_preview(rows)


if __name__ == "__main__":
    main()
