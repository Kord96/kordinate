"""Validate sealed `meta.json`.

Checks owned here:
- required sealed metadata fields
- artifact path references
- schema path references
- optional validation metadata block

This module only validates the post-seal metadata file.
"""

from pathlib import Path

def validate_meta(meta: dict, analysis_dir: Path) -> list[dict]:
    issues = []

    def error(msg):
        issues.append({"level": "ERROR", "section": "meta", "message": msg})

    def warn(msg):
        issues.append({"level": "WARNING", "section": "meta", "message": msg})

    required_fields = [
        "project",
        "analysis_id",
        "sha",
        "commit_time",
        "analysis_mode",
        "blast",
        "artifacts",
        "schemas",
    ]
    for field in required_fields:
        if field not in meta:
            error(f"meta.json missing required field: {field}")

    artifacts = meta.get("artifacts")
    if isinstance(artifacts, dict):
        def resolve_artifact_ref(value: str) -> Path:
            candidate = Path(value)
            return candidate if candidate.is_absolute() else (analysis_dir / candidate)

        for key, value in artifacts.items():
            if value and not isinstance(value, str):
                error(f"meta.json artifacts.{key} must be a string path when present")
        root = artifacts.get("root")
        if isinstance(root, str) and root:
            resolved_root = resolve_artifact_ref(root)
            if resolved_root != analysis_dir:
                warn(f"meta.json artifacts.root '{root}' does not match analysis dir '{analysis_dir}'")
    elif artifacts is not None:
        error("meta.json artifacts must be an object")

    schemas = meta.get("schemas")
    if isinstance(schemas, dict):
        for key, value in schemas.items():
            if not value:
                error(f"meta.json schemas.{key} is required")
            elif not isinstance(value, str) or not value.startswith("/"):
                error(f"meta.json schemas.{key} must be an absolute path")
    elif schemas is not None:
        error("meta.json schemas must be an object")

    validation = meta.get("validation")
    if validation is not None:
        if not isinstance(validation, dict):
            error("meta.json validation must be an object")
        else:
            attempts = validation.get("attempts")
            if attempts is not None and not isinstance(attempts, int):
                error("meta.json validation.attempts must be an integer")
            passed = validation.get("passed")
            if passed is not None and not isinstance(passed, bool):
                error("meta.json validation.passed must be a boolean")
            token = validation.get("token")
            if token is not None and not isinstance(token, str):
                error("meta.json validation.token must be a string")

    return issues
