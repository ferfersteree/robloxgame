"""Replace the Source of several scripts (ModuleScript, LocalScript or Script) inside an .rbxl in one pass (patch.py does one module per run).

    python tools/patch_many.py in.rbxl out.rbxl <ScriptPath> <new_source_file> [<ScriptPath> <new_source_file> ...]

ScriptPath is the full instance path, e.g. StarterPlayer/StarterPlayerScripts/Client/Sfx. Only the Source property chunks
of the classes involved are rewritten (re-compressed with the codec they already used); every other chunk is copied
byte for byte.
"""
import struct
import sys

import lz4.block
import zstandard

from rbx import accum, parse, read_ints

SCRIPT_CLASSES = ("ModuleScript", "LocalScript", "Script")
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"


def main():
    src, dst = sys.argv[1:3]
    rest = sys.argv[3:]
    if len(rest) < 2 or len(rest) % 2:
        sys.exit(__doc__)
    pairs = [(rest[i], rest[i + 1]) for i in range(0, len(rest), 2)]

    data = open(src, "rb").read()
    inst, parent, props = parse(src)

    def path(i):
        r = []
        while i in parent and i != -1:
            r.append(props.get(i, {}).get("Name", b"?").decode())
            i = parent[i]
        return "/".join(reversed(r))

    by_path = {}
    for i, c in inst.items():
        if c in SCRIPT_CLASSES:
            by_path.setdefault(path(i), []).append(i)

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

    cls_ids = {}  # class id -> (class name, instance ids in file order)
    for c in chunks:
        if c[0] == b"INST":
            b = body(c)
            k, = struct.unpack("<i", b[:4])
            l, = struct.unpack("<i", b[4:8])
            cn = b[8:8 + l].decode()
            if cn in SCRIPT_CLASSES:
                n, = struct.unpack("<i", b[9 + l:13 + l])
                cls_ids[k] = (cn, accum(read_ints(b[13 + l:13 + l + 4 * n], n)))
    assert cls_ids

    new_by_class = {}  # class id -> {index inside that class: (target, new source bytes)}
    for target, newfile in pairs:
        hits = by_path.get(target, [])
        assert len(hits) == 1, f"{target}: found {len(hits)} scripts"
        for k, (cn, ids) in cls_ids.items():
            if hits[0] in ids:
                new_by_class.setdefault(k, {})[ids.index(hits[0])] = (target, open(newfile, "rb").read())
                break
        else:
            raise AssertionError(f"{target}: class not found")

    done = 0
    for c in chunks:
        if c[0] != b"PROP":
            continue
        b = body(c)
        k, = struct.unpack("<i", b[:4])
        l, = struct.unpack("<i", b[4:8])
        if k in new_by_class and b[8:8 + l] == b"Source":
            new_by_index = new_by_class[k]
            ids = cls_ids[k][1]
            q = 9 + l
            out = [b[:q]]
            for i in range(len(ids)):
                sl, = struct.unpack("<i", b[q:q + 4])
                s = b[q + 4:q + 4 + sl]
                q += 4 + sl
                if i in new_by_index:
                    print(f"  {new_by_index[i][0]}: {len(s)} -> {len(new_by_index[i][1])} bytes")
                    s = new_by_index[i][1]
                out.append(struct.pack("<i", len(s)) + s)
            assert q == len(b)
            nb = b"".join(out)
            if c[4][:4] == ZSTD_MAGIC:
                comp = zstandard.ZstdCompressor(level=19).compress(nb)
            else:
                comp = lz4.block.compress(nb, store_size=False, mode="high_compression", compression=9)
            c[1], c[2], c[4] = len(comp), len(nb), comp
            done += 1
    assert done == len(new_by_class), f"rewrote {done} Source chunks, expected {len(new_by_class)}"
    hdr = data[:32]
    outb = hdr + b"".join(c[0] + struct.pack("<iii", c[1], c[2], c[3]) + c[4] for c in chunks)
    open(dst, "wb").write(outb)
    print("patched", len(pairs), "scripts;", len(data), "->", len(outb), "bytes")


if __name__ == "__main__":
    main()
