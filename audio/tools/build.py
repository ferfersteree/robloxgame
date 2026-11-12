import os, json, subprocess, wave, numpy as np
import sfx, music
from dsp import SR, rms_db
OUT = "out"; os.makedirs(OUT + "/wav", exist_ok=True); os.makedirs(OUT + "/ogg", exist_ok=True); os.makedirs(OUT + "/mp3", exist_ok=True)
items = {}
for k, v in sfx.SOUNDS.items():
    items[k] = dict(data=v["data"][None, :], use=v["use"], vol=v["vol"], loop=v["loop"], kind="sfx")
for k, v in music.tracks().items():
    items[k] = dict(data=v, use="background music (loops)", vol=0.12, loop=True, kind="music")
items["amb_forest"] = dict(data=music.forest_ambience(), use="forest ambience bed (loops)", vol=0.12, loop=True, kind="ambience")
def write_wav(path, x):
    x = np.clip(x, -1, 1)
    pcm = (x.T * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[0]); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
man = []
bad = []
for k, it in items.items():
    x = it["data"]
    if not np.isfinite(x).all(): bad.append((k, "nan"))
    if np.max(np.abs(x)) > 0.999: bad.append((k, "clip"))
    write_wav(f"{OUT}/wav/{k}.wav", x)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/wav/{k}.wav", "-c:a", "libvorbis", "-q:a", "5", f"{OUT}/ogg/{k}.ogg"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/wav/{k}.wav", "-c:a", "libmp3lame", "-b:a", "112k", f"{OUT}/mp3/{k}.mp3"], check=True)
    m = x.mean(axis=0)
    seam = abs(float(m[0] - m[-1])) / (np.max(np.abs(m)) + 1e-9)
    man.append(dict(name=k, kind=it["kind"], seconds=round(x.shape[1] / SR, 2), loop=it["loop"], volume=it["vol"], use=it["use"],
                    ogg_kb=round(os.path.getsize(f"{OUT}/ogg/{k}.ogg") / 1024, 1), rms_db=round(rms_db(x), 1), loop_seam=round(seam, 4)))
json.dump(man, open(f"{OUT}/manifest.json", "w"), indent=1)
print("files", len(man), "problems", bad)
print("total ogg MB", round(sum(m["ogg_kb"] for m in man) / 1024, 2))
for m in man:
    if m["loop"]: print(m["name"], m["seconds"], "s seam", m["loop_seam"], "ogg KB", m["ogg_kb"])
