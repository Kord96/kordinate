#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail if a rendered platform overlay still contains unresolved REGISTRY placeholders.",
    )
    parser.add_argument("overlay_dir", help="path to rendered platform overlay directory")
    args = parser.parse_args()

    overlay_dir = Path(args.overlay_dir)
    if not overlay_dir.exists():
      raise SystemExit(f"overlay directory does not exist: {overlay_dir}")
    if not overlay_dir.is_dir():
      raise SystemExit(f"overlay path is not a directory: {overlay_dir}")

    matches: list[str] = []
    for path in sorted(overlay_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "REGISTRY/" in text:
            matches.append(str(path))

    if matches:
        joined = "\n".join(matches)
        raise SystemExit(
            "rendered platform overlay still contains unresolved REGISTRY placeholders:\n"
            f"{joined}",
        )

    print(f"overlay ok: {overlay_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
