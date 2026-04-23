# Augur Release Schema

Canonical contract for `augur-release.json`, the manifest shipped inside a publishable Augur release artifact.

This manifest exists to decouple Augur runtime consumers from the `kordinate` source tree.
Charon and any local runner should depend on this manifest rather than on hard-coded repo paths.

## Core Rules

- `schema` must be `"augur-release/v1"`.
- `artifact_name` is the canonical release id and should be stable across publication and installation.
- `version` is the human-selected release version or channel candidate.
- `source_commit` should identify the source revision used to build the artifact.
- `entrypoints` must use paths relative to the release root.
- `included_paths` must list only paths that are actually present in the artifact.
- `bundles.generated` indicates whether the generated bundles included in the artifact are ready for runtime use.

## Minimal Shape

```json
{
  "schema": "augur-release/v1",
  "artifact_name": "augur-2026-04-23+abc1234",
  "version": "2026-04-23+abc1234",
  "source_commit": "abc1234",
  "built_at": "2026-04-23T21:00:00Z",
  "source_repo": "augur",
  "layout_version": "1",
  "bundles": {
    "generated": true
  },
  "entrypoints": {
    "prepare_analysis_dir": "scripts/run/prepare_analysis_dir.py",
    "prepare_deterministic_run": "scripts/run/prepare_deterministic_run.py",
    "build_analysis_context": "scripts/run/build_analysis_context.py",
    "build_prompt_context": "scripts/run/build_prompt_context.py",
    "build_validation_repair_prompt": "scripts/run/build_validation_repair_prompt.py",
    "finalize_analysis": "scripts/run/finalize_analysis.py",
    "validator": "skills/analyze/validator/validate.py"
  },
  "included_paths": [
    "IDENTITY.md",
    "README.md",
    "INDEX.yaml",
    "detectors",
    "memory",
    "schemas",
    "skills",
    "scripts",
    ".generated/bundles"
  ]
}
```

## Recommended Optional Fields

```json
{
  "compatibility": {
    "analysis_layout": "v4",
    "atlas_schema": "v4",
    "story_schema": "v1",
    "narratives_schema": "v1"
  },
  "checksums": {
    "tarball_sha256": "<hex>"
  },
  "publisher": {
    "tool": "charon",
    "channel": "stable"
  }
}
```

## Publication Model

A publishable Augur release normally consists of:

```text
augur-<version>.tar.gz
augur-release.json
```

The tarball should unpack into one release root containing the exact paths referenced by `included_paths` and `entrypoints`.

## Consumer Expectations

Consumers such as Charon or local runners should:

- resolve the release root first
- read `augur-release.json`
- resolve runtime entrypoints from `entrypoints`
- avoid depending on `/app/agents/augur` or `agents/augur/...` hard-coded source paths

