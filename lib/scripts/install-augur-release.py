#!/usr/bin/env python3
"""Install a published Augur release from the shared Charon-managed artifact store."""

from __future__ import annotations

import argparse
import json
import shutil
import tarfile
from pathlib import Path


DEFAULT_STORE = Path("/kord/shared/runtime/artifacts/augur")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install an Augur release from the shared artifact store")
    parser.add_argument("--store", default=str(DEFAULT_STORE), help="Artifact store root")
    parser.add_argument("--version", help="Exact version to install")
    parser.add_argument("--channel", help="Channel name such as stable or candidate")
    parser.add_argument("--dest", required=True, help="Destination directory for the unpacked release root")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_version(store: Path, version: str | None, channel: str | None) -> tuple[str, Path]:
    if version:
        version_dir = store / "versions" / version
        return version, version_dir
    if channel:
        channel_path = store / "channels" / f"{channel}.json"
        if not channel_path.exists():
            raise SystemExit(f"channel not found: {channel_path}")
        data = load_json(channel_path)
        resolved = data.get("version")
        if not resolved:
            raise SystemExit(f"channel file missing version: {channel_path}")
        return str(resolved), store / "versions" / str(resolved)
    raise SystemExit("pass either --version or --channel")


def main() -> int:
    args = parse_args()
    store = Path(args.store).resolve()
    version, version_dir = resolve_version(store, args.version, args.channel)
    manifest_path = version_dir / "augur-release.json"
    if not manifest_path.exists():
        raise SystemExit(f"manifest not found: {manifest_path}")
    manifest = load_json(manifest_path)
    tarballs = sorted(version_dir.glob("augur-*.tar.gz"))
    if not tarballs:
        raise SystemExit(f"no release tarball found in {version_dir}")
    tarball = tarballs[0]

    dest = Path(args.dest).resolve()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    with tarfile.open(tarball, "r:gz") as archive:
        archive.extractall(dest)

    print(json.dumps({
        "version": version,
        "manifest": str(manifest_path),
        "tarball": str(tarball),
        "installed_root": str(dest / manifest["artifact_name"]),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
