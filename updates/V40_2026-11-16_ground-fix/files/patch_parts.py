"""Move whole subtrees of a place file by a fixed offset (the CFrame position of every part under the given paths).

    python tools/patch_parts.py in.rbxl out.rbxl --delta 0,-1.9,3 --shift Workspace/Map/Village --shift Workspace/Map/Ambushes/ThrowingGrounds

Paths are instance names joined with "/" starting at the service (Workspace/Map/Village). Only the PROP chunks that hold
the CFrame of the moved part classes are rewritten, with the codec they already used (zstd or lz4); every other chunk is
copied byte for byte. Rotations are kept exactly. A model with an explicit pivot (WorldPivotData) inside a moved subtree has
its pivot moved by the same offset, so the pivot is never left behind.

Used for V40: the village (808 parts) and the Throwing Grounds (1043 parts) back down by 1.9 and +3 in z.
"""
import argparse
import struct
import sys

import lz4.block
import zstandard

from rbx import accum, parse, read_ints

PART_CLASSES = {"Part", "MeshPart", "WedgePart", "SpawnLocation", "UnionOperation", "TrussPart", "CornerWedgePart",
                "NegateOperation", "Seat", "VehicleSeat"}
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


def dec_floats(b, p, n):
    out = []
    for i in range(n):
        v = (b[p + i] << 24) | (b[p + n + i] << 16) | (b[p + 2 * n + i] << 8) | b[p + 3 * n + i]
        v = ((v >> 1) | ((v & 1) << 31)) & 0xFFFFFFFF
        out.append(struct.unpack("<f", struct.pack("<I", v))[0])
    return out, p + 4 * n


def enc_floats(vals):
    n = len(vals)
    planes = [bytearray(n) for _ in range(4)]
    for i, f in enumerate(vals):
        v = struct.unpack("<I", struct.pack("<f", f))[0]
        v = ((v << 1) | (v >> 31)) & 0xFFFFFFFF
        planes[0][i] = (v >> 24) & 255
        planes[1][i] = (v >> 16) & 255
        planes[2][i] = (v >> 8) & 255
        planes[3][i] = v & 255
    return bytes(planes[0] + planes[1] + planes[2] + planes[3])


def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--delta", required=True, help="dx,dy,dz in studs")
    ap.add_argument("--shift", action="append", required=True, help="instance path to move, e.g. Workspace/Map/Village")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    dx, dy, dz = (float(v) for v in a.delta.split(","))

    data = open(a.src, "rb").read()
    inst, parent, props = parse(a.src)
    memo = {}

    def path(i):
        if i in memo:
            return memo[i]
        par = parent.get(i, -1)
        nm = props.get(i, {}).get("Name", b"?").decode("utf-8", "replace")
        memo[i] = nm if par == -1 or par not in inst else path(par) + "/" + nm
        return memo[i]

    roots = [r.strip("/") for r in a.shift]
    in_root = {}
    for i in inst:
        pth = path(i)
        for r in roots:
            if pth == r or pth.startswith(r + "/"):
                in_root[i] = r
                break
    for r in roots:
        hit = [i for i, rr in in_root.items() if rr == r and path(i) == r]
        assert len(hit) == 1, f"{r}: found {len(hit)} instances with that path"
    targets = {i for i in in_root if inst[i] in PART_CLASSES}
    per_root = {r: sum(1 for i in targets if in_root[i] == r) for r in roots}
    print("parts to move:", per_root, "total", len(targets))

    # raw chunk walk
    p = 32
    chunks = []
    while p < len(data):
        name = data[p:p + 4]
        cl, ul, res = struct.unpack("<iii", data[p + 4:p + 16])
        n = cl if cl else ul
        chunks.append([name, cl, ul, res, data[p + 16:p + 16 + n]])
        p += 16 + n
        if name.startswith(b"END"):
            break
    assert p == len(data), "trailing bytes in the file"

    def body(c):
        name, cl, ul, res, raw = c
        if cl == 0:
            return raw
        if raw[:4] == ZSTD_MAGIC:
            return zstandard.ZstdDecompressor().decompress(raw, max_output_size=ul)
        return lz4.block.decompress(raw, uncompressed_size=ul)

    classes = {}
    for c in chunks:
        if c[0] == b"INST":
            b = body(c)
            k, = struct.unpack("<i", b[:4])
            l, = struct.unpack("<i", b[4:8])
            cn = b[8:8 + l].decode()
            n, = struct.unpack("<i", b[9 + l:13 + l])
            classes[k] = (cn, accum(read_ints(b[13 + l:13 + l + 4 * n], n)))

    changed = 0
    for c in chunks:
        if c[0] != b"PROP":
            continue
        b = body(c)
        k, = struct.unpack("<i", b[:4])
        l, = struct.unpack("<i", b[4:8])
        pn = b[8:8 + l].decode()
        cn, ids = classes[k]
        if pn == "WorldPivotData" and cn == "Model":
            # Optional CFrame: 0x10, rotations, x/y/z arrays, 0x02, one flag byte per model (1 = explicit pivot)
            n = len(ids)
            q = 9 + l
            assert b[q] == 0x10, "unexpected WorldPivotData layout"
            q += 1
            for _ in range(n):
                rid = b[q]
                q += 1
                if rid == 0:
                    q += 36
            rot_end = q
            xs, q = dec_floats(b, q, n)
            ys, q = dec_floats(b, q, n)
            zs, q = dec_floats(b, q, n)
            assert b[q] == 0x02 and q + 1 + n == len(b), "WorldPivotData chunk not fully understood"
            flags = b[q + 1:q + 1 + n]
            assert b[rot_end:q] == enc_floats(xs) + enc_floats(ys) + enc_floats(zs), "float re-encoding is not byte-exact"
            moved = 0
            for j, i in enumerate(ids):
                if flags[j] and i in in_root:
                    xs[j], ys[j], zs[j] = f32(xs[j] + dx), f32(ys[j] + dy), f32(zs[j] + dz)
                    moved += 1
                    print(f"  explicit pivot moved: {path(i)}")
            if moved:
                nb = b[:rot_end] + enc_floats(xs) + enc_floats(ys) + enc_floats(zs) + b[q:]
                if c[4][:4] == ZSTD_MAGIC:
                    comp = zstandard.ZstdCompressor(level=19).compress(nb)
                else:
                    comp = lz4.block.compress(nb, store_size=False, mode="high_compression", compression=9)
                c[1], c[2], c[4] = len(comp), len(nb), comp
            continue
        if pn != "CFrame" or cn not in PART_CLASSES or not (set(ids) & targets):
            continue
        n = len(ids)
        q = 9 + l
        assert b[8 + l] == 0x10
        for _ in range(n):
            rid = b[q]
            q += 1
            if rid == 0:
                q += 36
        rot_end = q
        xs, q = dec_floats(b, q, n)
        ys, q = dec_floats(b, q, n)
        zs, q = dec_floats(b, q, n)
        assert q == len(b), "CFrame chunk not fully understood"
        assert b[rot_end:] == enc_floats(xs) + enc_floats(ys) + enc_floats(zs), "float re-encoding is not byte-exact"
        moved = 0
        for j, i in enumerate(ids):
            if i in targets:
                xs[j] = f32(xs[j] + dx)
                ys[j] = f32(ys[j] + dy)
                zs[j] = f32(zs[j] + dz)
                moved += 1
        nb = b[:rot_end] + enc_floats(xs) + enc_floats(ys) + enc_floats(zs)
        if c[4][:4] == ZSTD_MAGIC:
            comp = zstandard.ZstdCompressor(level=19).compress(nb)
        else:
            comp = lz4.block.compress(nb, store_size=False, mode="high_compression", compression=9)
        c[1], c[2], c[4] = len(comp), len(nb), comp
        changed += moved
        print(f"  {cn}: moved {moved} of {n}")
    assert changed == len(targets), f"moved {changed}, expected {len(targets)}"
    if a.dry_run:
        print("dry run: nothing written")
        return
    hdr = data[:32]
    outb = hdr + b"".join(c[0] + struct.pack("<iii", c[1], c[2], c[3]) + c[4] for c in chunks)
    open(a.dst, "wb").write(outb)
    print("patched", changed, "parts;", len(data), "->", len(outb), "bytes")


if __name__ == "__main__":
    main()
