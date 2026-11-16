#!/usr/bin/env python3
"""Syntax checker for Luau source files (pure Python, nothing downloaded, nothing executed).

    python tools/luau_check.py <file.luau> [more files or folders]
    python tools/luau_check.py --self-test

It parses the whole file (statements, expressions, type annotations, generics, `continue`, `+=`, if-expressions,
interpolated strings, attributes) and reports the first syntax error with its line. It does NOT type-check and does not
know Roblox globals, so a typo in a variable name is not found - only broken structure (missing `end`/`then`/`)`,
stray tokens, bad type syntax, `return` in the middle of a block).
Verified on every .luau file of this repository (all of them are known to work in Studio).
"""
import os
import re
import sys

KEYWORDS = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
            "not", "or", "repeat", "return", "then", "true", "until", "while"}
OPS3 = ["...", "..=", "//="]
OPS2 = ["..", "::", "==", "~=", "<=", ">=", "+=", "-=", "*=", "/=", "%=", "^=", "//", "->"]
OPS1 = "+-*/%^#&|~<>=(){}[];:,.?@"
COMPOUND = {"+=", "-=", "*=", "/=", "%=", "^=", "//=", "..="}
NUM = re.compile(r"0[xX][0-9a-fA-F_]*(?:\.[0-9a-fA-F_]*)?(?:[pP][+-]?\d+)?|0[bB][01_]+|(?:\d[\d_]*(?:\.(?!\.)[\d_]*)?|\.\d[\d_]*)(?:[eE][+-]?\d+)?")
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class LuauSyntaxError(Exception):
    def __init__(self, line, msg):
        super().__init__(f"line {line}: {msg}")
        self.line, self.msg = line, msg


class Tok:
    __slots__ = ("k", "v", "line")

    def __init__(self, k, v, line):
        self.k, self.v, self.line = k, v, line

    def __repr__(self):
        return f"{self.k}:{self.v!r}@{self.line}"


# ------------------------------------------------------------------ lexer
def _skip_string(src, i, q, line):
    """src[i] is the opening quote; returns (index after the closing quote, line)."""
    n = len(src)
    i += 1
    while i < n:
        c = src[i]
        if c == "\\":
            if i + 1 < n and src[i + 1] == "\n":
                line += 1
            i += 2
            continue
        if c == "\n":
            raise LuauSyntaxError(line, "unfinished string")
        if c == q:
            return i + 1, line
        i += 1
    raise LuauSyntaxError(line, "unfinished string")


def _skip_backtick(src, i, line):
    n = len(src)
    i += 1
    while i < n:
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == "\n":
            line += 1
        if c == "`":
            return i + 1, line
        if c == "{":
            depth = 1
            i += 1
            while i < n and depth:
                d = src[i]
                if d in "\"'":
                    i, line = _skip_string(src, i, d, line)
                    continue
                if d == "`":
                    i, line = _skip_backtick(src, i, line)
                    continue
                if d == "\n":
                    line += 1
                depth += (d == "{") - (d == "}")
                i += 1
            continue
        i += 1
    raise LuauSyntaxError(line, "unfinished interpolated string")


def lex(src):
    toks = []
    i, n, line = 0, len(src), 1
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            i += 1
            continue
        if c in " \t\r":
            i += 1
            continue
        if src.startswith("--", i):
            m = re.match(r"--\[(=*)\[", src[i:i + 64])
            if m:
                close = "]" + m.group(1) + "]"
                j = src.find(close, i + len(m.group(0)))
                if j < 0:
                    raise LuauSyntaxError(line, "unfinished long comment")
                line += src.count("\n", i, j)
                i = j + len(close)
                continue
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if c.isalpha() or c == "_":
            m = NAME.match(src, i)
            w = m.group(0)
            toks.append(Tok("kw" if w in KEYWORDS else "name", w, line))
            i = m.end()
            continue
        if c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            m = NUM.match(src, i)
            toks.append(Tok("num", m.group(0), line))
            i = m.end()
            continue
        if c in "\"'":
            j, line2 = _skip_string(src, i, c, line)
            toks.append(Tok("str", src[i:j], line))
            i, line = j, line2
            continue
        if c == "`":
            j, line2 = _skip_backtick(src, i, line)
            toks.append(Tok("str", "`..`", line))
            i, line = j, line2
            continue
        if c == "[":
            m = re.match(r"\[(=*)\[", src[i:i + 64])
            if m:
                close = "]" + m.group(1) + "]"
                j = src.find(close, i + len(m.group(0)))
                if j < 0:
                    raise LuauSyntaxError(line, "unfinished long string")
                toks.append(Tok("str", "[[..]]", line))
                line += src.count("\n", i, j)
                i = j + len(close)
                continue
        for op in OPS3:
            if src.startswith(op, i):
                toks.append(Tok("op", op, line))
                i += 3
                break
        else:
            for op in OPS2:
                if src.startswith(op, i):
                    toks.append(Tok("op", op, line))
                    i += 2
                    break
            else:
                if c in OPS1:
                    toks.append(Tok("op", c, line))
                    i += 1
                else:
                    raise LuauSyntaxError(line, f"unexpected character {c!r}")
    toks.append(Tok("eof", "<eof>", line))
    return toks


# ------------------------------------------------------------------ parser
BIN = {"or": (1, 1), "and": (2, 2), "<": (3, 3), ">": (3, 3), "<=": (3, 3), ">=": (3, 3), "~=": (3, 3), "==": (3, 3),
       "..": (9, 8), "+": (10, 10), "-": (10, 10), "*": (11, 11), "/": (11, 11), "//": (11, 11), "%": (11, 11), "^": (14, 13)}
UNARY_PRI = 12
BLOCK_END = {"end", "else", "elseif", "until"}


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.p = 0

    # --- helpers
    def peek(self, k=0):
        return self.t[min(self.p + k, len(self.t) - 1)]

    def next(self):
        tok = self.t[self.p]
        if tok.k != "eof":
            self.p += 1
        return tok

    def err(self, msg, tok=None):
        tok = tok or self.peek()
        raise LuauSyntaxError(tok.line, f"{msg} (near {tok.v!r})")

    def is_op(self, v, k=0):
        t = self.peek(k)
        return t.k == "op" and t.v == v

    def is_kw(self, v, k=0):
        t = self.peek(k)
        return t.k == "kw" and t.v == v

    def accept_op(self, v):
        if self.is_op(v):
            self.next()
            return True
        return False

    def accept_kw(self, v):
        if self.is_kw(v):
            self.next()
            return True
        return False

    def expect_op(self, v):
        if not self.accept_op(v):
            self.err(f"expected '{v}'")

    def expect_kw(self, v, opener=None):
        if not self.accept_kw(v):
            self.err(f"expected '{v}'" + (f" to close '{opener[0]}' from line {opener[1]}" if opener else ""))

    def expect_name(self):
        t = self.peek()
        if t.k != "name":
            self.err("expected a name")
        return self.next()

    # --- blocks and statements
    def at_end(self):
        t = self.peek()
        return t.k == "eof" or (t.k == "kw" and t.v in BLOCK_END)

    def block(self):
        while not self.at_end():
            last = self.statement()
            self.accept_op(";")
            if last:
                if not self.at_end():
                    self.err("'return' must be the last statement of a block")
                break

    def statement(self):
        t = self.peek()
        if t.k == "kw":
            v = t.v
            if v == "if":
                return self.if_stat()
            if v == "while":
                self.next()
                self.expr()
                self.expect_kw("do")
                self.block()
                self.expect_kw("end", (v, t.line))
                return False
            if v == "do":
                self.next()
                self.block()
                self.expect_kw("end", (v, t.line))
                return False
            if v == "for":
                return self.for_stat()
            if v == "repeat":
                self.next()
                self.block()
                self.expect_kw("until", (v, t.line))
                self.expr()
                return False
            if v == "function":
                self.next()
                self.expect_name()
                while self.is_op(".") or self.is_op(":"):
                    colon = self.is_op(":")
                    self.next()
                    self.expect_name()
                    if colon:
                        break
                self.func_body(t)
                return False
            if v == "local":
                return self.local_stat()
            if v == "return":
                self.next()
                if not self.at_end() and not self.is_op(";"):
                    self.exprlist()
                return True
            if v == "break":
                self.next()
                return False
            self.err("unexpected keyword")
        if t.k == "op" and t.v == "@":
            self.attributes()
            if self.is_kw("local") and self.is_kw("function", 1):
                self.next()
                self.next()
                self.expect_name()
                self.func_body(t)
            elif self.is_kw("function"):
                self.next()
                self.expect_name()
                while self.is_op(".") or self.is_op(":"):
                    colon = self.is_op(":")
                    self.next()
                    self.expect_name()
                    if colon:
                        break
                self.func_body(t)
            else:
                self.err("attribute must precede a function")
            return False
        if t.k == "name":
            nt = self.peek(1)
            if t.v == "continue" and not (nt.k == "op" and nt.v in {"=", ".", ":", "(", "[", ",", "+=", "-=", "*=", "/=", "..="}):
                self.next()
                return False
            if t.v == "type" and nt.k == "name":
                return self.type_decl()
            if t.v == "export" and nt.k == "name" and nt.v == "type":
                self.next()
                return self.type_decl()
        return self.expr_stat()

    def attributes(self):
        while self.accept_op("@"):
            self.expect_name()
            if self.accept_op("("):
                depth = 1
                while depth and self.peek().k != "eof":
                    tt = self.next()
                    if tt.k == "op" and tt.v == "(":
                        depth += 1
                    elif tt.k == "op" and tt.v == ")":
                        depth -= 1

    def if_stat(self):
        t = self.next()
        self.expr()
        self.expect_kw("then")
        self.block()
        while self.is_kw("elseif"):
            self.next()
            self.expr()
            self.expect_kw("then")
            self.block()
        if self.accept_kw("else"):
            self.block()
        self.expect_kw("end", ("if", t.line))
        return False

    def for_stat(self):
        t = self.next()
        self.binding()
        if self.accept_op("="):
            self.expr()
            self.expect_op(",")
            self.expr()
            if self.accept_op(","):
                self.expr()
        else:
            while self.accept_op(","):
                self.binding()
            self.expect_kw("in")
            self.exprlist()
        self.expect_kw("do")
        self.block()
        self.expect_kw("end", ("for", t.line))
        return False

    def binding(self):
        self.expect_name()
        if self.accept_op(":"):
            self.type_()

    def local_stat(self):
        t = self.next()
        if self.is_kw("function"):
            self.next()
            self.expect_name()
            self.func_body(t)
            return False
        self.binding()
        if self.accept_op("<"):  # attribs <const>
            self.expect_name()
            self.expect_op(">")
        while self.accept_op(","):
            self.binding()
        if self.accept_op("="):
            self.exprlist()
        return False

    def type_decl(self):
        self.next()  # 'type'
        self.expect_name()
        if self.is_op("<"):
            self.generics(True)
        self.expect_op("=")
        self.type_()
        return False

    def expr_stat(self):
        is_call = self.suffixed()
        if self.is_op(",") or self.is_op("="):
            while self.accept_op(","):
                self.suffixed()
            self.expect_op("=")
            self.exprlist()
            return False
        t = self.peek()
        if t.k == "op" and t.v in COMPOUND:
            self.next()
            self.expr()
            return False
        if not is_call:
            self.err("syntax error: statement is not a call or assignment")
        return False

    # --- functions
    def generics(self, allow_default=False):
        self.expect_op("<")
        while True:
            self.expect_name()
            self.accept_op("...")
            if allow_default and self.accept_op("="):
                self.type_()
            if not self.accept_op(","):
                break
        self.expect_op(">")

    def func_body(self, opener):
        if self.is_op("<"):
            self.generics()
        self.expect_op("(")
        if not self.is_op(")"):
            while True:
                if self.accept_op("..."):
                    if self.accept_op(":"):
                        self.type_()
                    break
                self.binding()
                if not self.accept_op(","):
                    break
        self.expect_op(")")
        if self.accept_op(":"):
            self.type_()
        self.block()
        self.expect_kw("end", ("function", opener.line))

    # --- expressions
    def exprlist(self):
        self.expr()
        while self.accept_op(","):
            self.expr()

    def expr(self, limit=0):
        t = self.peek()
        if (t.k == "kw" and t.v == "not") or (t.k == "op" and t.v in ("-", "#")):
            self.next()
            self.expr(UNARY_PRI)
        else:
            self.simple_exp()
        while True:
            t = self.peek()
            op = t.v if t.k in ("op", "kw") else None
            if op in BIN and BIN[op][0] > limit:
                self.next()
                self.expr(BIN[op][1])
            else:
                break

    def simple_exp(self):
        t = self.peek()
        k, v = t.k, t.v
        if k in ("num", "str"):
            self.next()
        elif k == "kw" and v in ("nil", "true", "false"):
            self.next()
        elif k == "op" and v == "...":
            self.next()
        elif k == "op" and v == "{":
            self.table()
        elif k == "kw" and v == "function":
            self.next()
            self.func_body(t)
        elif k == "op" and v == "@":
            self.attributes()
            self.expect_kw("function")
            self.func_body(t)
        elif k == "kw" and v == "if":
            self.next()
            self.expr()
            self.expect_kw("then")
            self.expr()
            while self.accept_kw("elseif"):
                self.expr()
                self.expect_kw("then")
                self.expr()
            self.expect_kw("else")
            self.expr()
        else:
            self.suffixed()
        while self.accept_op("::"):
            self.type_()

    def suffixed(self):
        t = self.peek()
        if t.k == "name":
            self.next()
        elif t.k == "op" and t.v == "(":
            self.next()
            self.expr()
            self.expect_op(")")
        else:
            self.err("unexpected symbol")
        is_call = False
        while True:
            t = self.peek()
            if t.k == "op" and t.v == ".":
                self.next()
                self.expect_name_or_kw()
                is_call = False
            elif t.k == "op" and t.v == "[":
                self.next()
                self.expr()
                self.expect_op("]")
                is_call = False
            elif t.k == "op" and t.v == ":":
                self.next()
                self.expect_name_or_kw()
                self.call_args()
                is_call = True
            elif (t.k == "op" and t.v in ("(", "{")) or t.k == "str":
                self.call_args()
                is_call = True
            else:
                break
        return is_call

    def expect_name_or_kw(self):
        t = self.peek()
        if t.k in ("name", "kw"):
            return self.next()
        self.err("expected a field name")

    def call_args(self):
        t = self.peek()
        if t.k == "str":
            self.next()
        elif t.k == "op" and t.v == "{":
            self.table()
        elif t.k == "op" and t.v == "(":
            self.next()
            if not self.is_op(")"):
                self.exprlist()
            self.expect_op(")")
        else:
            self.err("expected call arguments")

    def table(self):
        t = self.next()  # {
        while not self.is_op("}"):
            if self.is_op("["):
                self.next()
                self.expr()
                self.expect_op("]")
                self.expect_op("=")
                self.expr()
            elif self.peek().k == "name" and self.is_op("=", 1):
                self.next()
                self.next()
                self.expr()
            else:
                self.expr()
            if not (self.accept_op(",") or self.accept_op(";")):
                break
        if not self.accept_op("}"):
            self.err(f"expected '}}' to close '{{' from line {t.line}")

    # --- types
    def type_(self):
        self.accept_op("|") or self.accept_op("&")
        self.simple_type()
        while self.is_op("|") or self.is_op("&"):
            self.next()
            self.simple_type()

    def simple_type(self):
        self.base_type()
        while self.accept_op("?"):
            pass

    def base_type(self):
        t = self.peek()
        k, v = t.k, t.v
        if k == "kw" and v in ("nil", "true", "false"):
            self.next()
        elif k == "str":
            self.next()
        elif k == "op" and v == "...":
            self.next()
            self.simple_type()
        elif k == "name":
            self.next()
            if v == "typeof" and self.is_op("("):
                self.next()
                self.expr()
                self.expect_op(")")
                return
            while self.accept_op("."):
                self.expect_name()
            if self.is_op("<"):
                self.next()
                while not self.is_op(">"):
                    self.type_()
                    if not self.accept_op(","):
                        break
                self.expect_op(">")
        elif k == "op" and v == "{":
            self.table_type()
        elif k == "op" and v in ("(", "<"):
            if v == "<":
                self.generics()
            self.expect_op("(")
            while not self.is_op(")"):
                if self.peek().k == "name" and self.is_op(":", 1):
                    self.next()
                    self.next()
                self.type_()
                if not self.accept_op(","):
                    break
            self.expect_op(")")
            if self.accept_op("->"):
                self.type_()
        else:
            self.err("expected a type")

    def table_type(self):
        t = self.next()  # {
        while not self.is_op("}"):
            if self.is_op("["):
                self.next()
                self.type_()
                self.expect_op("]")
                self.expect_op(":")
                self.type_()
            else:
                if self.peek().k == "name" and self.peek().v in ("read", "write") and self.peek(1).k == "name":
                    self.next()
                if self.peek().k == "name" and self.is_op(":", 1):
                    self.next()
                    self.next()
                self.type_()
            if not (self.accept_op(",") or self.accept_op(";")):
                break
        if not self.accept_op("}"):
            self.err(f"expected '}}' to close the table type from line {t.line}")


def check_source(src):
    """Returns None if the source parses, else the error message."""
    try:
        toks = lex(src)
        p = Parser(toks)
        p.block()
        if p.peek().k != "eof":
            p.err("unexpected token (extra 'end' or stray code?)")
    except LuauSyntaxError as e:
        return str(e)
    except RecursionError:
        return "too deeply nested for this checker"
    return None


def check_file(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return check_source(f.read())


def collect(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, _dirs, files in os.walk(p):
                for f in sorted(files):
                    if f.endswith((".luau", ".lua")):
                        yield os.path.join(d, f)
        else:
            yield p


SELF_TEST_OK = [
    "local a = 1\nreturn a",
    "local function f(x: number, ...: any): (number, string?)\n\treturn x, nil\nend",
    "type T = { [string]: number | nil, name: string, f: (a: number) -> boolean }\nlocal t: T = {}",
    "for i = 1, 10 do if i % 2 == 0 then continue end t[i] += 1 end",
    "local s = `hi {name}, {if x then 1 else 2}`\nx ..= s",
    "local x = if a then b elseif c then d else e",
    "local y = (z :: any).field",
    "obj:method(1)(2).x[3] = f{1, 2; 3}\nprint 'x'",
    "repeat local a = 1 until a > 0",
    "export type K<T = number> = { T }\nlocal f = function<T>(x: T): T return x end",
    "@native\nlocal function g() end",
]
SELF_TEST_BAD = [
    ("missing end", "local function f()\n\treturn 1\n"),
    ("missing then", "if a\n\tx = 1\nend"),
    ("stray end", "local a = 1\nend"),
    ("unclosed paren", "print((1 + 2)"),
    ("return not last", "local function f()\n\treturn 1\n\tlocal a = 2\nend"),
    ("bare expression", "local a = 1\na"),
    ("bad table", "local t = { a = 1, b = }"),
    ("missing do", "for i = 1, 3\n\tprint(i)\nend"),
    ("bad type", "local x: = 1"),
    ("unfinished string", 'local s = "abc\nprint(s)'),
]


def self_test():
    bad = 0
    for src in SELF_TEST_OK:
        e = check_source(src)
        if e:
            print("FAIL (should parse):", src.splitlines()[0], "->", e)
            bad += 1
    for label, src in SELF_TEST_BAD:
        e = check_source(src)
        if not e:
            print("FAIL (should be rejected):", label)
            bad += 1
    print("self-test:", "ok" if not bad else f"{bad} problem(s)")
    return bad


def main(argv):
    if argv and argv[0] == "--self-test":
        sys.exit(1 if self_test() else 0)
    if not argv:
        print(__doc__)
        sys.exit(2)
    failed = 0
    total = 0
    for path in collect(argv):
        total += 1
        e = check_file(path)
        if e:
            failed += 1
            print(f"{path}: {e}")
    print(f"checked {total} file(s): {total - failed} ok, {failed} with errors")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
