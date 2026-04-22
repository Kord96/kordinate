#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from analysis_paths import write_analysis_indexes, write_json, write_latest_analysis_pointer


ROOT = Path(__file__).resolve().parents[1]
ATLAS_SCHEMA = ROOT / "schemas" / "atlas-schema.md"
FACTS_SCHEMA = ROOT / "detectors" / "facts" / "schema.md"
STORY_SCHEMA = ROOT / "schemas" / "story-schema.md"
NARRATIVES_SCHEMA = ROOT / "schemas" / "narratives-schema.md"
META_SCHEMA = ROOT / "schemas" / "meta-schema.md"
REPO_BUNDLE_EXTS = ("", ".md", ".json", ".yaml", ".yml")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_env(name: str) -> str:
    return str((os.environ.get(name) or "")).strip()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def latest_validation_iteration(analysis_dir: Path) -> dict[str, Any]:
    log_path = analysis_dir / "log.json"
    if not log_path.exists():
        return {}
    payload = read_json(log_path)
    iterations = payload.get("iterations") or []
    if not isinstance(iterations, list) or not iterations:
        return {}
    latest = iterations[-1]
    return latest if isinstance(latest, dict) else {}


def analysis_context(analysis_dir: Path) -> tuple[str, str, Path]:
    analysis_id = analysis_dir.name
    if analysis_dir.parent.name == "analysis":
        project = analysis_dir.parents[1].name
        agent_home = analysis_dir.parents[4]
        return project, analysis_id, agent_home
    if analysis_dir.parent.parent.name == "analysis":
        project = analysis_dir.parents[2].name
        agent_home = analysis_dir.parents[5]
        return project, analysis_id, agent_home
    raise SystemExit(f"analysis directory is not under memory/projects/<project>/analysis/<sha>/<id>: {analysis_dir}")


def relative_to_run_root(analysis_dir: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(analysis_dir.resolve()))
    except Exception:
        return str(path.resolve())


def estimate_tokens_from_text(text: str) -> int:
    normalized = text or ""
    if not normalized:
        return 0
    return max(1, math.ceil(len(normalized) / 4))


def estimate_tokens_from_file(path: Path) -> int:
    try:
        return estimate_tokens_from_text(path.read_text(encoding="utf-8"))
    except Exception:
        return 0


def resolve_repo_bundle_file(dir_name: str, selection: str | None) -> Path | None:
    if not selection:
        return None
    bundle_dir = ROOT / ".generated" / "bundles" / dir_name
    if not bundle_dir.exists():
        return None
    for ext in REPO_BUNDLE_EXTS:
        candidate = bundle_dir / f"{selection}{ext}"
        if candidate.exists():
            return candidate.resolve()
    return None


def git_tracked_files(working_dir: Path) -> list[Path]:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(working_dir), "ls-files"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        files = []
        for line in output.splitlines():
            rel = line.strip()
            if not rel:
                continue
            candidate = (working_dir / rel).resolve()
            if candidate.is_file():
                files.append(candidate)
        return files
    except Exception:
        files: list[Path] = []
        for path in working_dir.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {".git", "node_modules"} for part in path.parts):
                continue
            files.append(path.resolve())
        return files


def collect_repo_refs_from_any(value: Any, repo_root: Path, out: set[Path]) -> None:
    if isinstance(value, str) and ":" in value:
        candidate = (repo_root / value.split(":", 1)[0]).resolve()
        try:
            candidate.relative_to(repo_root.resolve())
        except Exception:
            return
        if candidate.exists() and candidate.is_file():
            out.add(candidate)
        return
    if isinstance(value, dict):
        for item in value.values():
            collect_repo_refs_from_any(item, repo_root, out)
    elif isinstance(value, list):
        for item in value:
            collect_repo_refs_from_any(item, repo_root, out)


def collect_repo_refs(analysis_dir: Path, working_dir: Path) -> set[Path]:
    refs: set[Path] = set()
    atlas_path = analysis_dir / "atlas.json"
    if atlas_path.exists():
        collect_repo_refs_from_any(read_json(atlas_path), working_dir, refs)
    stories_dir = analysis_dir / "stories"
    if stories_dir.exists():
        for story_path in stories_dir.glob("*.yaml"):
            try:
                collect_repo_refs_from_any(read_yaml(story_path), working_dir, refs)
            except Exception:
                continue
    return refs


def collect_bundle_inputs() -> list[dict[str, Any]]:
    selections = [
        ("memory", read_env("AUGUR_MEMORY_BUNDLE")),
        ("skill", read_env("AUGUR_SKILL_BUNDLE")),
        ("runtime", read_env("AUGUR_RUNTIME_BUNDLE")),
    ]
    bundles: list[dict[str, Any]] = []
    for kind, selection in selections:
        if not selection:
            continue
        path = resolve_repo_bundle_file(kind, selection)
        if not path:
            continue
        bundles.append({
            "kind": kind,
            "id": selection,
            "path": str(path),
            "tokens_est": estimate_tokens_from_file(path),
        })
    return bundles


def collect_loaded_refs(analysis_mode: str) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    mode_guide = ROOT / "skills" / "analyze" / "modes" / f"{analysis_mode}.md"
    if analysis_mode in {"full", "incremental"} and mode_guide.exists():
        refs.append({
            "kind": "guide",
            "path": str(mode_guide.resolve()),
            "tokens_est": estimate_tokens_from_file(mode_guide),
        })
    for schema_path in (FACTS_SCHEMA, ATLAS_SCHEMA, STORY_SCHEMA, NARRATIVES_SCHEMA, META_SCHEMA):
        refs.append({
            "kind": "schema",
            "path": str(schema_path.resolve()),
            "tokens_est": estimate_tokens_from_file(schema_path),
        })
    return refs


def collect_artifact_inputs(analysis_dir: Path, working_dir: Path, analysis_mode: str) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    blast_path = analysis_dir / "blast.json"
    if blast_path.exists():
        artifacts.append({
            "kind": "blast",
            "path": str(blast_path.resolve()),
            "tokens_est": estimate_tokens_from_file(blast_path),
        })

    startup_path = analysis_dir / "startup.json"
    if startup_path.exists():
        artifacts.append({
            "kind": "startup",
            "path": str(startup_path.resolve()),
            "tokens_est": estimate_tokens_from_file(startup_path),
        })

    if working_dir.exists():
        try:
            payload = subprocess.check_output(
                [
                    "python3",
                    str(ROOT / "scripts" / "build_analysis_context.py"),
                    "--project",
                    read_env("AUGUR_PROJECT") or analysis_dir.parents[2].name,
                    "--working-dir",
                    str(working_dir),
                    "--run-dir",
                    str(analysis_dir),
                    "--analysis-mode",
                    analysis_mode if analysis_mode in {"full", "incremental"} else "full",
                ],
                text=True,
            ).strip()
            context = json.loads(payload)
            for starter in context.get("starter_files") or []:
                candidate = Path(str(starter)).resolve()
                if not candidate.exists() or not candidate.is_file():
                    continue
                artifacts.append({
                    "kind": "starter",
                    "path": str(candidate),
                    "tokens_est": estimate_tokens_from_file(candidate),
                })
        except Exception:
            pass

    dedup: dict[str, dict[str, Any]] = {}
    for item in artifacts:
        dedup[item["path"]] = item
    return list(dedup.values())


def build_inputs_block(analysis_dir: Path, working_dir: Path, analysis_mode: str) -> tuple[dict[str, Any], int, int]:
    bundles = collect_bundle_inputs()
    loaded_refs = collect_loaded_refs(analysis_mode)
    artifacts = collect_artifact_inputs(analysis_dir, working_dir, analysis_mode)
    repo_refs = collect_repo_refs(analysis_dir, working_dir)
    repo_tokens_est = sum(estimate_tokens_from_file(path) for path in repo_refs)
    validation_tokens_est = sum(item["tokens_est"] for item in artifacts if item["kind"] in {"startup", "starter", "blast"})
    totals = {
        "bundle_tokens_est": sum(item["tokens_est"] for item in bundles),
        "loaded_ref_tokens_est": sum(item["tokens_est"] for item in loaded_refs),
        "artifact_tokens_est": sum(item["tokens_est"] for item in artifacts),
        "repo_tokens_est": repo_tokens_est,
        "validation_tokens_est": validation_tokens_est,
        "total_tokens_est": (
            sum(item["tokens_est"] for item in bundles)
            + sum(item["tokens_est"] for item in loaded_refs)
            + sum(item["tokens_est"] for item in artifacts)
            + repo_tokens_est
        ),
    }
    return {
        "bundles": bundles,
        "loaded_refs": loaded_refs,
        "artifacts": artifacts,
        "totals": totals,
    }, len(repo_refs), repo_tokens_est


def build_meta_payload(
    analysis_dir: Path,
    validation_token: str = "",
    validation_attempts: int = 0,
) -> dict[str, Any]:
    analysis_dir = analysis_dir.resolve()
    atlas_path = analysis_dir / "atlas.json"
    if not atlas_path.exists():
        raise SystemExit(f"atlas.json not found at {atlas_path}")

    atlas = read_json(atlas_path)
    blast_path = analysis_dir / "blast.json"
    blast = read_json(blast_path) if blast_path.exists() else {}
    latest_validation = latest_validation_iteration(analysis_dir)
    existing_meta_path = analysis_dir / "meta.json"
    existing_meta = read_json(existing_meta_path) if existing_meta_path.exists() else {}

    latest_status = str(latest_validation.get("status") or "")
    validation_passed = latest_status == "valid"
    if latest_status and not validation_passed:
        raise SystemExit(f"cannot finalize analysis with log.json validation status '{latest_status}'")
    if not latest_status and not (((existing_meta.get("analysis") or {}).get("validation") or {}).get("passed")):
        raise SystemExit("cannot finalize analysis without a valid log.json validation entry or an already-passed meta.json")

    project_slug, analysis_id, agent_home = analysis_context(analysis_dir)
    project_name = str(atlas.get("project") or ((existing_meta.get("repository") or {}).get("project")) or project_slug)
    sha = str(atlas.get("metadata", {}).get("analyzed_at_sha") or ((existing_meta.get("repository") or {}).get("commit")) or blast.get("current_sha") or "")
    commit_time = str(blast.get("current_commit_time") or ((existing_meta.get("repository") or {}).get("commit_time")) or "")
    base_sha = str(blast.get("previous_sha") or ((existing_meta.get("repository") or {}).get("base_commit")) or atlas.get("metadata", {}).get("base_sha") or "")
    base_commit_time = str(blast.get("previous_commit_time") or ((existing_meta.get("repository") or {}).get("base_commit_time")) or atlas.get("metadata", {}).get("base_commit_time") or "")
    analysis_mode = str(atlas.get("metadata", {}).get("analysis_mode") or ((existing_meta.get("analysis") or {}).get("mode")) or blast.get("mode") or "")
    analyzed_at = str(((existing_meta.get("analysis") or {}).get("analyzed_at")) or now_iso())
    request_id = read_env("AUGUR_REQUEST_ID") or str(existing_meta.get("request_id") or "")

    working_dir = Path(read_env("AUGUR_WORKING_DIR") or "").expanduser().resolve() if read_env("AUGUR_WORKING_DIR") else None
    tracked_files = git_tracked_files(working_dir) if working_dir and working_dir.exists() else []
    bundle_mode = read_env("AUGUR_BUNDLE_MODE") or str((existing_meta.get("agent") or {}).get("bundle_mode") or "selective")
    inputs, files_read_count, repo_tokens_est = build_inputs_block(
        analysis_dir,
        working_dir if working_dir and working_dir.exists() else analysis_dir,
        analysis_mode if analysis_mode in {"full", "incremental"} else "full",
    )

    startup_manifest = analysis_dir / "startup.json"
    run_index = analysis_dir / "index.json"
    stories_dir = analysis_dir / "stories"
    narratives_path = analysis_dir / "narratives.yaml"
    overlays_dir = analysis_dir / "overlays"
    reflections_dir = analysis_dir / "reflections"
    overlays_index = overlays_dir / "index.json"
    reflections_index = reflections_dir / "index.json"
    overlays_dir.mkdir(parents=True, exist_ok=True)
    reflections_dir.mkdir(parents=True, exist_ok=True)
    if not overlays_index.exists():
        write_json(overlays_index, {"analysis_id": analysis_id, "overlays": []})
    if not reflections_index.exists():
        write_json(reflections_index, {"analysis_id": analysis_id, "reflections": []})

    meta = {
        "request_id": request_id,
        "repository": {
            "project": project_name,
            "commit": sha,
            "commit_time": commit_time,
            "base_commit": base_sha,
            "base_commit_time": base_commit_time,
            "file_count": len(tracked_files),
            "files_read_count": files_read_count,
            "repo_tokens_est": repo_tokens_est,
        },
        "agent": {
            "name": read_env("AUGUR_AGENT_NAME"),
            "specialization": read_env("AUGUR_AGENT_SPECIALIZATION"),
            "bundle_mode": bundle_mode,
            "agent_contract_version": read_env("AUGUR_AGENT_CONTRACT_VERSION"),
            "runtime_profile_version": read_env("AUGUR_RUNTIME_PROFILE_VERSION"),
        },
        "analysis": {
            "id": analysis_id,
            "mode": analysis_mode,
            "analyzed_at": analyzed_at,
            "blast": {
                "mode": blast.get("mode", ""),
                "tier": blast.get("tier", 0),
                "reasons": blast.get("reasons", []),
                "affected_components": blast.get("affected_components", []),
                "affected_flows": blast.get("affected_flows", []),
                "affected_state": blast.get("affected_state", []),
                "affected_dependencies": blast.get("affected_dependencies", []),
                "affected_concepts": blast.get("affected_concepts", []),
            },
            "artifacts": {
                "root": ".",
                "atlas": relative_to_run_root(analysis_dir, atlas_path),
                "startup": relative_to_run_root(analysis_dir, startup_manifest) if startup_manifest.exists() else "",
                "index": relative_to_run_root(analysis_dir, run_index) if run_index.exists() else "",
                "stories_dir": relative_to_run_root(analysis_dir, stories_dir) if stories_dir.exists() else "",
                "narratives": relative_to_run_root(analysis_dir, narratives_path) if narratives_path.exists() else "",
                "blast": relative_to_run_root(analysis_dir, blast_path) if blast_path.exists() else "",
                "overlays_dir": relative_to_run_root(analysis_dir, overlays_dir),
                "overlays_index": relative_to_run_root(analysis_dir, overlays_index),
                "reflections_dir": relative_to_run_root(analysis_dir, reflections_dir),
                "reflections_index": relative_to_run_root(analysis_dir, reflections_index),
            },
            "schemas": {
                "facts": str(FACTS_SCHEMA),
                "atlas": str(ATLAS_SCHEMA),
                "story": str(STORY_SCHEMA),
                "narratives": str(NARRATIVES_SCHEMA),
                "meta": str(META_SCHEMA),
            },
            "inputs": inputs,
            "validation": {
                "passed": validation_passed or bool((((existing_meta.get("analysis") or {}).get("validation") or {}).get("passed"))),
                "attempts": int(latest_validation.get("iteration") or validation_attempts or (((existing_meta.get("analysis") or {}).get("validation") or {}).get("attempts")) or 0),
                "token": str(validation_token or (((existing_meta.get("analysis") or {}).get("validation") or {}).get("token")) or ""),
            },
        },
    }
    return meta


def finalize_analysis_dir(
    analysis_dir: Path,
    validation_token: str = "",
    validation_attempts: int = 0,
) -> dict[str, Any]:
    analysis_dir = analysis_dir.resolve()
    meta = build_meta_payload(
        analysis_dir,
        validation_token=validation_token,
        validation_attempts=validation_attempts,
    )
    project_slug, analysis_id, agent_home = analysis_context(analysis_dir)
    repository = meta.get("repository") or {}
    existing_meta_path = analysis_dir / "meta.json"
    write_json(existing_meta_path, meta)
    write_latest_analysis_pointer(
        project_slug,
        analysis_id,
        str(repository.get("commit") or ""),
        str(repository.get("commit_time") or ""),
        agent_home=agent_home,
        analysis_path=analysis_dir,
    )
    write_analysis_indexes(project_slug, agent_home=agent_home)
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize an Augur analysis directory by writing meta.json and updating latest.json.")
    parser.add_argument("analysis_dir", type=Path)
    parser.add_argument("--validation-token", default="")
    parser.add_argument("--validation-attempts", type=int, default=0)
    args = parser.parse_args()

    meta = finalize_analysis_dir(
        args.analysis_dir,
        validation_token=args.validation_token,
        validation_attempts=args.validation_attempts,
    )
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
