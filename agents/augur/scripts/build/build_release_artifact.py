#!/usr/bin/env python3
"""Build a publishable Augur release artifact and manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INCLUDE_PATHS = [
    "IDENTITY.md",
    "README.md",
    "INDEX.yaml",
    "detectors",
    "memory",
    "schemas",
    "skills",
    "scripts",
    ".generated/bundles",
]
DEFAULT_ENTRYPOINTS = {
    "prepare_analysis_dir": "scripts/run/prepare_analysis_dir.py",
    "prepare_deterministic_run": "scripts/run/prepare_deterministic_run.py",
    "build_analysis_context": "scripts/run/build_analysis_context.py",
    "build_prompt_context": "scripts/run/build_prompt_context.py",
    "build_validation_repair_prompt": "scripts/run/build_validation_repair_prompt.py",
    "finalize_analysis": "scripts/run/finalize_analysis.py",
    "validator": "skills/analyze/validator/validate.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a publishable Augur release artifact")
    parser.add_argument("--output-dir", required=True, help="Directory that will receive the release")
    parser.add_argument("--version", help="Release version; defaults to <date>+<git-sha>")
    parser.add_argument("--source-repo", default="augur", help="Source repository name recorded in the manifest")
    parser.add_argument("--skip-bundles", action="store_true", help="Do not rebuild generated bundles before packaging")
    return parser.parse_args()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def resolve_version(explicit: str | None) -> str:
    if explicit:
        return explicit
    return f"{utc_now().date().isoformat()}+{short_commit()}"


def ensure_bundles() -> None:
    subprocess.check_call(["python3", str(ROOT / "scripts" / "build" / "build_skill_bundles.py")], cwd=ROOT)
    subprocess.check_call(["python3", str(ROOT / "scripts" / "build" / "build_memory_bundles.py")], cwd=ROOT)
    subprocess.check_call(["python3", str(ROOT / "scripts" / "build" / "build_detector_bundles.py")], cwd=ROOT)
    subprocess.check_call(["python3", str(ROOT / "scripts" / "build" / "build_runtime_bundles.py")], cwd=ROOT)


def copy_selected_paths(staging_root: Path) -> None:
    for rel in DEFAULT_INCLUDE_PATHS:
        src = ROOT / rel
        dst = staging_root / rel
        if not src.exists():
            raise FileNotFoundError(f"required release path missing: {src}")
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def build_manifest(version: str, source_repo: str) -> dict:
    return {
        "schema": "augur-release/v1",
        "artifact_name": f"augur-{version}",
        "version": version,
        "source_commit": short_commit(),
        "built_at": iso_now(),
        "source_repo": source_repo,
        "layout_version": "1",
        "bundles": {
            "generated": True,
        },
        "entrypoints": dict(DEFAULT_ENTRYPOINTS),
        "included_paths": list(DEFAULT_INCLUDE_PATHS),
        "compatibility": {
            "analysis_layout": "v4",
            "atlas_schema": "v4",
            "story_schema": "v1",
            "narratives_schema": "v1",
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    version = resolve_version(args.version)
    output_dir = Path(args.output_dir).resolve()
    release_dir = output_dir / f"augur-{version}"
    staging_root = release_dir / "root"
    tarball_path = output_dir / f"augur-{version}.tar.gz"
    manifest_path = release_dir / "augur-release.json"

    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_bundles:
        ensure_bundles()

    copy_selected_paths(staging_root)

    manifest = build_manifest(version, args.source_repo)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (staging_root / "augur-release.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with tarfile.open(tarball_path, "w:gz") as archive:
        archive.add(staging_root, arcname=f"augur-{version}")

    manifest["checksums"] = {"tarball_sha256": sha256(tarball_path)}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (staging_root / "augur-release.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "release_dir": str(release_dir),
        "release_root": str(staging_root),
        "manifest": str(manifest_path),
        "tarball": str(tarball_path),
        "version": version,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
