"""Stamp the service-worker cache name with a content hash of the app shell.

The service worker in ``public/sw.js`` names its cache ``artikel-<token>``. That
token only needs to change when a shell file actually changes, so it is derived
from a hash of exactly the files listed in the worker's ``SHELL`` array. Run it
before every deploy (wired to npm ``predeploy``) so the cache busts on real
changes and never has to be bumped by hand.

Idempotent: if no shell file changed since the last run, the token is identical
and ``sw.js`` is left untouched.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
SW_PATH = PUBLIC_DIR / "sw.js"

CACHE_RE = re.compile(r'(const CACHE = ")[^"]*(";)')
SHELL_RE = re.compile(r"const SHELL = \[(.*?)\];", re.DOTALL)
ENTRY_RE = re.compile(r'"\./([^"]*)"')


def shell_files(sw_source: str) -> list[Path]:
    """Return the existing shell files referenced by the worker's SHELL array."""
    match = SHELL_RE.search(sw_source)
    if match is None:
        raise SystemExit("stamp_sw: SHELL array not found in sw.js")
    names = [name for name in ENTRY_RE.findall(match.group(1)) if name]
    files: list[Path] = []
    for name in sorted(set(names)):
        path = PUBLIC_DIR / name
        if path.is_file():
            files.append(path)
        else:
            print(f"stamp_sw: warning - shell file missing: {name}", file=sys.stderr)
    return files


def content_token(files: list[Path]) -> str:
    """Compute a short, stable hash over the given files (name plus bytes)."""
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()[:10]


def main() -> int:
    """Rewrite the CACHE constant in sw.js when the content token changed."""
    source = SW_PATH.read_text(encoding="utf-8")
    cache_match = CACHE_RE.search(source)
    if cache_match is None:
        raise SystemExit("stamp_sw: CACHE constant not found in sw.js")

    new_name = f"artikel-{content_token(shell_files(source))}"
    updated = CACHE_RE.sub(rf"\g<1>{new_name}\g<2>", source, count=1)
    if updated == source:
        print(f"stamp_sw: cache unchanged ({new_name})")
        return 0

    SW_PATH.write_text(updated, encoding="utf-8")
    print(f"stamp_sw: cache -> {new_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
