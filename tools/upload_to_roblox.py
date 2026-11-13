#!/usr/bin/env python3
"""Upload SpearHunt sounds and shop art to Roblox (Open Cloud Assets API) and write Client/AudioIds.

Usage (PowerShell):
    $env:ROBLOX_API_KEY = "<your Open Cloud key>"      # key needs Assets API: read + write
    python tools\\upload_to_roblox.py --user-id 123456789

What it does
  1. uploads every file in audio/ogg as an Audio asset and every PNG in shop-art as a Decal,
  2. waits until Roblox finishes (and moderation approves) each one,
  3. resolves each decal id to the image id that ImageLabel needs,
  4. writes out/AudioIds.luau with all ids. Paste its content into Client/AudioIds in Studio.

It can be stopped and started again: finished uploads are remembered in out/uploaded.json.
The API key is read only from the ROBLOX_API_KEY environment variable and is never printed or saved.
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid

API = os.environ.get("ROBLOX_API_BASE", "https://apis.roblox.com")
DELIVERY = os.environ.get("ROBLOX_DELIVERY_BASE", "https://assetdelivery.roblox.com")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")


def multipart(fields, file_field, file_name, file_bytes, file_type):
    boundary = "----spearhunt" + uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\nContent-Type: application/json\r\n\r\n{v}\r\n'.encode())
    parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{file_name}"\r\n'
                  f'Content-Type: {file_type}\r\n\r\n').encode())
    parts.append(file_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def call(req, tries=5):
    """urlopen with backoff on 429 and 5xx. Returns (status, body_bytes)."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            body = e.read()
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                wait = min(60, 3 * 2 ** attempt)
                print(f"    server said {e.code}, waiting {wait}s")
                time.sleep(wait)
                continue
            return e.code, body
        except urllib.error.URLError as e:
            if attempt < tries - 1:
                time.sleep(3 * 2 ** attempt)
                continue
            return 0, str(e).encode()
    return 0, b""


def upload(key, creator, kind, path, display):
    asset_type = "Audio" if kind == "audio" else "Decal"
    request = json.dumps({
        "assetType": asset_type,
        "displayName": display[:50],
        "description": "SpearHunt " + kind,
        "creationContext": {"creator": creator},
    })
    ctype = "audio/ogg" if kind == "audio" else "image/png"
    with open(path, "rb") as f:
        body, content_type = multipart({"request": request}, "fileContent", os.path.basename(path), f.read(), ctype)
    req = urllib.request.Request(f"{API}/assets/v1/assets", data=body, method="POST",
                                 headers={"x-api-key": key, "Content-Type": content_type})
    status, resp = call(req)
    if status != 200:
        raise RuntimeError(f"upload failed ({status}): {resp[:300].decode(errors='replace')}")
    op = json.loads(resp)
    op_id = op.get("operationId") or op.get("path", "").split("/")[-1]
    if not op_id:
        raise RuntimeError("no operation id in response")
    return op_id


def wait_asset(key, op_id, timeout=300):
    end = time.time() + timeout
    while time.time() < end:
        req = urllib.request.Request(f"{API}/assets/v1/operations/{op_id}", headers={"x-api-key": key})
        status, resp = call(req)
        if status == 200:
            data = json.loads(resp)
            if data.get("done"):
                if "error" in data:
                    raise RuntimeError("Roblox rejected it: " + json.dumps(data["error"])[:300])
                r = data.get("response", {})
                state = (r.get("moderationResult") or {}).get("moderationState", "")
                if "REJECTED" in state:
                    raise RuntimeError("moderation rejected the asset")
                return str(r.get("assetId"))
        time.sleep(2)
    raise RuntimeError("timed out waiting for Roblox")


def decal_to_image(decal_id, tries=6):
    """ImageLabel needs the image id, not the decal id. The public asset delivery answer contains it."""
    for _ in range(tries):
        req = urllib.request.Request(f"{DELIVERY}/v1/asset/?id={decal_id}", headers={"User-Agent": "spearhunt-upload"})
        status, resp = call(req, tries=1)
        if status == 200:
            m = re.search(rb"id=(\d+)", resp)
            if m:
                return m.group(1).decode()
        time.sleep(4)
    return None


def main():
    ap = argparse.ArgumentParser()
    who = ap.add_mutually_exclusive_group(required=True)
    who.add_argument("--user-id", help="your Roblox user id (number from your profile URL)")
    who.add_argument("--group-id", help="upload to a group instead")
    ap.add_argument("--only", choices=["audio", "art"], help="upload just one kind")
    ap.add_argument("--dry-run", action="store_true", help="list what would be uploaded")
    args = ap.parse_args()

    key = os.environ.get("ROBLOX_API_KEY", "")
    if not key and not args.dry_run:
        sys.exit("Set the ROBLOX_API_KEY environment variable first (see the top of this file).")
    creator = {"userId": args.user_id} if args.user_id else {"groupId": args.group_id}

    items = []
    if args.only != "art":
        d = os.path.join(ROOT, "audio", "ogg")
        items += [("audio", n[:-4], os.path.join(d, n)) for n in sorted(os.listdir(d)) if n.endswith(".ogg")]
    if args.only != "audio":
        d = os.path.join(ROOT, "shop-art")
        items += [("art", "art_" + n[:-4], os.path.join(d, n)) for n in sorted(os.listdir(d)) if n.endswith(".png")]
    print(f"{len(items)} files")
    if args.dry_run:
        for kind, name, path in items:
            print(f"  {kind:5s} {name}")
        return

    os.makedirs(OUT, exist_ok=True)
    cache_path = os.path.join(OUT, "uploaded.json")
    done = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    failed = []
    for i, (kind, name, path) in enumerate(items, 1):
        if name in done:
            print(f"[{i}/{len(items)}] {name}: already uploaded ({done[name]})")
            continue
        try:
            print(f"[{i}/{len(items)}] {name}: uploading")
            op = upload(key, creator, kind, path, "SpearHunt " + name)
            asset_id = wait_asset(key, op)
            if kind == "art":
                image = decal_to_image(asset_id)
                if image:
                    asset_id = image
                else:
                    print("    could not resolve the image id yet; kept the decal id (it may need a re-run later)")
            done[name] = asset_id
            json.dump(done, open(cache_path, "w"), indent=1)
            print(f"    ok -> rbxassetid://{asset_id}")
        except Exception as e:  # keep going, report at the end
            print(f"    FAILED: {e}")
            failed.append(name)

    # write the Lua module
    keys = [n[:-4] for n in sorted(os.listdir(os.path.join(ROOT, "audio", "ogg"))) if n.endswith(".ogg")]
    keys += ["art_" + n[:-4] for n in sorted(os.listdir(os.path.join(ROOT, "shop-art"))) if n.endswith(".png")]
    lines = ["-- Client/AudioIds",
             "-- Generated by tools/upload_to_roblox.py. Звуки и картинки магазина, загруженные в Roblox.",
             '-- "" = ещё не загружен: играет встроенный звук / показывается 3D-модель.',
             "return {"]
    for k in keys:
        v = done.get(k)
        lines.append(f'\t{k} = "{"rbxassetid://" + v if v else ""}",')
    lines.append("}")
    lua = os.path.join(OUT, "AudioIds.luau")
    open(lua, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"\nWrote {lua}  ({len([k for k in keys if k in done])} of {len(keys)} ids)")
    if failed:
        print("Failed (run the same command again to retry them):", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
