#!/usr/bin/env python3
"""

Generates raw DEFLATE tests from zlib's test/infcover.c

Each case becomes test/data/infcover/<name>.deflate

If zlib decodes it to a clean end of stream, the output is written to <name>.out
Note, cases with no .out are invalid or truncated and MUST FAIL!

Usage: scripts/gen_infcover.py [--fetch]
    --fetch will redownload infcover.c from upstream
"""

import pathlib
import re
import sys
import urllib.request
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tests/data/infcover.c"
OUT = ROOT / "tests/data/infcover"
URL = "https://raw.githubusercontent.com/madler/zlib/develop/test/infcover.c"

CALL = re.compile(
    r'\b(try|inf)\(((?:"[^"]*"\s*)+),\s*((?:"[^"]*"\s*)+),\s*([^;]*?)\);'
)


def literals(s):
    return "".join(re.findall(r'"([^"]*)"', s))


def cases(src):
    for kind, hexs, name, rest in CALL.findall(src):
        args = [a.strip() for a in rest.split(",")]
        # try() with err < 0 and inf() with win >= 0 use zlib/gzip wrappers.
        if kind == "try" and int(args[0]) < 0:
            continue
        if kind == "inf" and int(args[1]) >= 0:
            continue
        hexs = literals(hexs).split()
        if hexs:
            yield literals(name), bytes(int(h, 16) for h in hexs)


def main():
    if "--fetch" in sys.argv:
        SRC.write_bytes(urllib.request.urlopen(URL).read())

    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.iterdir():
        f.unlink()

    seen = set()
    for name, data in cases(SRC.read_text()):
        if data in seen:
            continue
        seen.add(data)

        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        base, n = slug, 2
        while (OUT / f"{slug}.deflate").exists():
            slug, n = f"{base}_{n}", n + 1

        (OUT / f"{slug}.deflate").write_bytes(data)
        d = zlib.decompressobj(-15)
        try:
            out = d.decompress(data)
        except zlib.error:
            continue
        if d.eof:
            (OUT / f"{slug}.out").write_bytes(out)


if __name__ == "__main__":
    main()
