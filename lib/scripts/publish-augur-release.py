#!/usr/bin/env python3
"""Charon-owned publisher for versioned Augur release artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_STORE = Path("/kord/shared/runtime/artifacts/augur")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish an Augur release into the shared artifact store")
    parser.add_argument("manifest", help="Path to augur-release.json produced by build_release_artifact.py")
    parser.add_argument("--tarball", help="Optional explicit tarball path; defaults to sibling augur-<version>.tar.gz")
    parser.add_argument("--store", default=str(DEFAULT_STORE), help="Artifact store root")
    parser.add_argument("--channel", action="append", default=[], help="Channel pointer to update, such as stable or candidate")
    return parser.parse_args()


def read_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "augur-release/v1":
        raise SystemExit(f"unsupported manifest schema: {data.get('schema')!r}")
    required = ["artifact_name", "version", "entrypoints", "included_paths"]
    missing = [key for key in required if key not in data]
    if missing:
        raise SystemExit(f"manifest missing required keys: {', '.join(missing)}")
    return data


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    manifest = read_manifest(manifest_path)
    version = str(manifest["version"])
    artifact_name = str(manifest["artifact_name"])
    tarball = Path(args.tarball).resolve() if args.tarball else (manifest_path.parent.parent / f"{artifact_name}.tar.gz").resolve()
    if not tarball.exists():
        raise SystemExit(f"tarball not found: {tarball}")

    store = Path(args.store).resolve()
    versions_dir = store / "versions" / version
    channels_dir = store / "channels"
    versions_dir.mkdir(parents=True, exist_ok=True)
    channels_dir.mkdir(parents=True, exist_ok=True)

    published_manifest = dict(manifest)
    published_manifest["publisher"] = {
        "tool": "charon",
        "published_at": utc_now(),
        "store_root": str(store),
    }

    manifest_out = versions_dir / "augur-release.json"
    tarball_out = versions_dir / tarball.name
    shutil.copy2(tarball, tarball_out)
    manifest_out.write_text(json.dumps(published_manifest, indent=2) + "\n", encoding="utf-8")

    for channel in args.channel:
        channel_path = channels_dir / f"{channel}.json"
        channel_path.write_text(
            json.dumps(
                {
                    "schema": "augur-release-channel/v1",
                    "name": channel,
                    "version": version,
                    "artifact_name": artifact_name,
                    "manifest": str(manifest_out),
                    "tarball": str(tarball_out),
                    "updated_at": utc_now(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    print(json.dumps({
        "version": version,
        "manifest": str(manifest_out),
        "tarball": str(tarball_out),
        "channels": args.channel,
        "store": str(store),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

