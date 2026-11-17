"""Find names that are used as a call / index head but are not in scope (typos, a local function used before its
declaration, a forgotten require). Luau has no compile-time error for these: they are nil globals and fail at run time.

    python tools/luau_names.py [files or folders ...]      (default: source/)

Not a type checker and not a full resolver: type annotations are not analysed, so only names that are used as
`name(`, `name.` or `name[` are looked at (types are never used like that), and a table constructor key `{ name = 1 }` is not
a use. Scopes follow function / do / if / while / for / repeat blocks. A local declared AFTER a function that uses it is
reported, which is exactly the case that breaks at run time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from luau_check import lex, collect  # noqa: E402

GLOBALS = set("""
game workspace script shared _G _VERSION self
Instance Vector3 Vector2 Vector3int16 Vector2int16 CFrame Color3 ColorSequence ColorSequenceKeypoint NumberSequence NumberSequenceKeypoint
NumberRange UDim UDim2 Rect Ray Region3 Region3int16 Enum TweenInfo RaycastParams OverlapParams Random BrickColor PhysicalProperties Axes Faces
Font DateTime CatalogSearchParams DockWidgetPluginGuiInfo SharedTable Path2DControlPoint RotationCurveKey FloatCurveKey PathWaypoint Content
math string table os task coroutine utf8 buffer bit32 debug
pcall xpcall error assert print warn tostring tonumber type typeof select ipairs pairs next rawget rawset rawequal rawlen setmetatable getmetatable
require tick time wait delay spawn unpack newproxy collectgarbage settings UserSettings stats version elapsedTime loadstring getfenv setfenv
plugin
""".split())

# Known and harmless: callbacks of `fx.burst(n, function ... K.prof(...) end)` in EggOpenings are leftovers of the JS port and are
# never called (EggPlayer's fx.burst is a no-op), so the missing `K` never fails.
KNOWN_DEAD_CODE = {("EggOpenings.luau", "K")}


def check_file(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    toks = lex(src)
    scopes = [set()]
    problems = []
    n = len(toks)
    brackets = []  # stack of "(", "{", "["
    pending = None  # names to declare in the scope opened by the next `do`
    i = 0

    def declare(name):
        scopes[-1].add(name)

    def defined(name):
        return any(name in s for s in scopes) or name in GLOBALS

    while i < n:
        t = toks[i]
        k, v = t.k, t.v
        if k == "kw":
            if v == "function":
                # function name ... or anonymous; open a scope for the parameters
                j = i + 1
                # `function a.b.c:d(` or `function name(`: the head is a use, not a declaration (unless local)
                head = toks[j] if j < n else None
                scopes.append(set())
                if head is not None and head.k == "name":
                    # method definition adds `self`
                    jj = j
                    while jj + 1 < n and toks[jj + 1].k == "op" and toks[jj + 1].v in (".", ":"):
                        if toks[jj + 1].v == ":":
                            scopes[-1].add("self")
                        jj += 2
                    prev_is_local = i > 0 and toks[i - 1].k == "kw" and toks[i - 1].v == "local"
                    if prev_is_local:
                        scopes[-2].add(head.v)
                    elif toks[j + 1].k == "op" and toks[j + 1].v in (".", ":"):
                        if not defined(head.v):
                            problems.append((head.line, head.v))
                    else:
                        scopes[-2].add(head.v)  # global-style function declaration defines the name from here on
                    i = jj + 1
                # parameters
                while i < n and not (toks[i].k == "op" and toks[i].v == "("):
                    i += 1
                depth = 0
                while i < n:
                    tt = toks[i]
                    if tt.k == "op" and tt.v == "(":
                        depth += 1
                    elif tt.k == "op" and tt.v == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    elif depth == 1 and tt.k == "name" and (toks[i - 1].k == "op" and toks[i - 1].v in ("(", ",")):
                        scopes[-1].add(tt.v)
                    elif depth == 1 and tt.k == "op" and tt.v == "...":
                        pass
                    i += 1
                i += 1
                continue
            if v == "local":
                nxt = toks[i + 1]
                if nxt.k == "kw" and nxt.v == "function":
                    # `local function name`: handled when the `function` keyword is reached (needs the local flag)
                    i += 1
                    continue
                # local a, b: T, c = ...
                j = i + 1
                names = []
                while j < n and toks[j].k == "name":
                    names.append(toks[j].v)
                    j += 1
                    if j < n and toks[j].k == "op" and toks[j].v == ":":
                        # skip the type: up to the next top-level `,` or `=`
                        j += 1
                        d = 0
                        while j < n:
                            tt = toks[j]
                            if tt.k == "op" and tt.v in ("(", "{", "<", "["):
                                d += 1
                            elif tt.k == "op" and tt.v in (")", "}", ">", "]"):
                                d -= 1
                            elif d <= 0 and tt.k == "op" and tt.v in (",", "="):
                                break
                            elif d <= 0 and tt.k == "kw":
                                break
                            j += 1
                    if j < n and toks[j].k == "op" and toks[j].v == ",":
                        j += 1
                        continue
                    break
                # the right-hand side is analysed first (a local does not see itself), so declare after it
                pending_locals = names
                # scan the RHS tokens as ordinary tokens, declare at the end of the statement: simplest is to declare now
                for nm in pending_locals:
                    declare(nm)
                i = j
                continue
            if v == "for":
                # for a, b in ... do / for i = ...
                j = i + 1
                names = []
                while j < n and toks[j].k == "name":
                    names.append(toks[j].v)
                    j += 1
                    if j < n and toks[j].k == "op" and toks[j].v == ",":
                        j += 1
                    else:
                        break
                pending = names
                i = j
                continue
            if v == "do":
                scopes.append(set())
                if pending:
                    scopes[-1].update(pending)
                    pending = None
                i += 1
                continue
            if v in ("then", "repeat"):
                scopes.append(set())
                i += 1
                continue
            if v == "else":
                if len(scopes) > 1:
                    scopes.pop()
                scopes.append(set())
                i += 1
                continue
            if v == "elseif":
                if len(scopes) > 1:
                    scopes.pop()
                i += 1
                continue
            if v in ("end", "until"):
                if len(scopes) > 1:
                    scopes.pop()
                i += 1
                continue
            i += 1
            continue
        if k == "op":
            if v in ("(", "{", "["):
                brackets.append(v)
            elif v in (")", "}", "]"):
                if brackets:
                    brackets.pop()
            i += 1
            continue
        if k == "name":
            prev = toks[i - 1] if i > 0 else None
            nxt = toks[i + 1] if i + 1 < n else None
            after_dot = prev is not None and prev.k == "op" and prev.v in (".", ":", "::")
            is_key = brackets and brackets[-1] == "{" and nxt is not None and nxt.k == "op" and nxt.v == "=" and prev is not None and prev.k == "op" and prev.v in ("{", ",", ";")
            is_head = nxt is not None and nxt.k == "op" and nxt.v in ("(", ".", "[")
            # `a: Type = ...` parameter / local type annotations are skipped by the rules above; a name before `:` is not a head
            if not after_dot and not is_key and is_head and not defined(v):
                problems.append((t.line, v))
        i += 1
    return problems


def main(argv):
    paths = argv or ["source"]
    files = list(collect(paths))
    total = 0
    for f in files:
        probs = check_file(f)
        if probs:
            seen = set()
            for line, name in probs:
                if (line, name) in seen or (os.path.basename(f), name) in KNOWN_DEAD_CODE:
                    continue
                seen.add((line, name))
                print(f"{f}:{line}: '{name}' is not in scope")
                total += 1
    print(f"checked {len(files)} file(s): {total} suspicious use(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
