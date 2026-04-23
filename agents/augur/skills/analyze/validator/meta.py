"""Validate sealed `meta.json` against the current nested schema."""

from __future__ import annotations

from pathlib import Path


def validate_meta(meta: dict, analysis_dir: Path) -> list[dict]:
    issues: list[dict] = []

    def error(msg: str) -> None:
        issues.append({"level": "ERROR", "section": "meta", "message": msg})

    def warn(msg: str) -> None:
        issues.append({"level": "WARNING", "section": "meta", "message": msg})

    def require_string(block: dict, key: str, label: str) -> None:
        value = block.get(key)
        if not isinstance(value, str) or not value:
            error(f"meta.json {label} is required")

    if not isinstance(meta, dict):
        error("meta.json must be an object")
        return issues

    request_id = meta.get("request_id")
    if request_id is not None and not isinstance(request_id, str):
        error("meta.json request_id must be a string")

    repository = meta.get("repository")
    if not isinstance(repository, dict):
        error("meta.json repository must be an object")
    else:
        for key in ("project", "commit", "commit_time", "base_commit", "base_commit_time"):
            if key not in repository or not isinstance(repository.get(key), str):
                error(f"meta.json repository.{key} must be a string")
        for key in ("file_count", "files_read_count", "repo_tokens_est"):
            if key not in repository or not isinstance(repository.get(key), int):
                error(f"meta.json repository.{key} must be an integer")

    agent = meta.get("agent")
    if not isinstance(agent, dict):
        error("meta.json agent must be an object")
    else:
        for key in ("name", "specialization", "bundle_mode", "agent_contract_version", "runtime_profile_version"):
            if key not in agent or not isinstance(agent.get(key), str):
                error(f"meta.json agent.{key} must be a string")

    analysis = meta.get("analysis")
    if not isinstance(analysis, dict):
        error("meta.json analysis must be an object")
        return issues

    require_string(analysis, "id", "analysis.id")
    require_string(analysis, "mode", "analysis.mode")
    require_string(analysis, "analyzed_at", "analysis.analyzed_at")

    blast = analysis.get("blast")
    if not isinstance(blast, dict):
        error("meta.json analysis.blast must be an object")
    else:
        if not isinstance(blast.get("mode"), str):
            error("meta.json analysis.blast.mode must be a string")
        if not isinstance(blast.get("tier"), int):
            error("meta.json analysis.blast.tier must be an integer")
        for key in (
            "reasons",
            "affected_components",
            "affected_flows",
            "affected_state",
            "affected_dependencies",
            "affected_concepts",
        ):
            value = blast.get(key)
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                error(f"meta.json analysis.blast.{key} must be a string list")

    def resolve_artifact_ref(value: str) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else (analysis_dir / candidate)

    artifacts = analysis.get("artifacts")
    if not isinstance(artifacts, dict):
        error("meta.json analysis.artifacts must be an object")
    else:
        required_artifacts = (
            "root",
            "atlas",
            "startup",
            "index",
            "stories_dir",
            "narratives",
            "blast",
            "overlays_dir",
            "overlays_index",
            "reflections_dir",
            "reflections_index",
        )
        for key in required_artifacts:
            value = artifacts.get(key)
            if not isinstance(value, str):
                error(f"meta.json analysis.artifacts.{key} must be a string")
        root = artifacts.get("root")
        if isinstance(root, str) and root:
            resolved_root = resolve_artifact_ref(root)
            if resolved_root != analysis_dir:
                warn(f"meta.json analysis.artifacts.root '{root}' does not match analysis dir '{analysis_dir}'")

    schemas = analysis.get("schemas")
    if not isinstance(schemas, dict):
        error("meta.json analysis.schemas must be an object")
    else:
        for key in ("facts", "atlas", "story", "narratives", "meta"):
            value = schemas.get(key)
            if not isinstance(value, str) or not value.startswith("/"):
                error(f"meta.json analysis.schemas.{key} must be an absolute path")

    inputs = analysis.get("inputs")
    if not isinstance(inputs, dict):
        error("meta.json analysis.inputs must be an object")
    else:
        for key in ("bundles", "loaded_refs", "artifacts"):
            value = inputs.get(key)
            if not isinstance(value, list):
                error(f"meta.json analysis.inputs.{key} must be a list")
        totals = inputs.get("totals")
        if not isinstance(totals, dict):
            error("meta.json analysis.inputs.totals must be an object")
        else:
            for key in (
                "bundle_tokens_est",
                "loaded_ref_tokens_est",
                "artifact_tokens_est",
                "repo_tokens_est",
                "validation_tokens_est",
                "total_tokens_est",
            ):
                if not isinstance(totals.get(key), int):
                    error(f"meta.json analysis.inputs.totals.{key} must be an integer")

    validation = analysis.get("validation")
    if not isinstance(validation, dict):
        error("meta.json analysis.validation must be an object")
    else:
        if not isinstance(validation.get("passed"), bool):
            error("meta.json analysis.validation.passed must be a boolean")
        if not isinstance(validation.get("attempts"), int):
            error("meta.json analysis.validation.attempts must be an integer")
        if not isinstance(validation.get("token"), str):
            error("meta.json analysis.validation.token must be a string")

    return issues
