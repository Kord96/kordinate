# Augur Run Manifest Schema

Defines the per-run manifest written for each benchmark execution of Augur `/analyze`.

The run manifest is the canonical operational record for one execution:

- which repo and commit were used
- which model and bundle settings were used
- whether the run succeeded
- where outputs were written
- how long each stage took
- what scores and validations were produced
- which reflection record belongs to the run

## Recommended Path

```text
benchmark/manifests/<timestamp>/<model>/<memory-bundle>__<skill-bundle>/<owner>--<repo>.json
```

## Schema

```json
{
  "run_id": "2026-04-09T12-00-00Z__microsoft--vscode__abc1234__augur__selective__holistic__run-1",
  "timestamp": "2026-04-09T12:00:00Z",
  "repo": "microsoft/vscode",
  "repo_url": "https://github.com/microsoft/vscode",
  "pinned_sha": "abc1234",
  "model": "augur",
  "provider": "augur",
  "memory_bundle": "selective",
  "skill_bundle": "holistic",
  "run_number": 1,
  "analysis_mode": "full",
  "success": true,
  "failure_reason": null,
  "correlation_id": "job-123",
  "runtime_ms": {
    "setup": 1200,
    "gather": 8400,
    "facts": 5300,
    "concepts": 9400,
    "atlas": 4100,
    "stories": 7300,
    "validation": 1400,
    "total": 37100
  },
  "tokens": {
    "input": 42000,
    "output": 6300,
    "total": 48300
  },
  "estimated_cost": 0.0,
  "outputs": {
    "atlas_path": "benchmark/runs/.../atlas.json",
    "facts_dir": "benchmark/runs/.../facts/",
    "stories_dir": "benchmark/runs/.../stories/",
    "transcript_path": "benchmark/runs/.../transcript.md"
  },
  "validation": {
    "output_files_exist": true,
    "schema_valid": true,
    "grounding_refs_resolve": true,
    "analyzed_sha_matches": true
  },
  "scores": {
    "quality_score": 0.81,
    "concepts_f1": 0.79,
    "components": 0.84,
    "grounding": 0.86,
    "api_surface": 0.72,
    "externals_and_state": 0.83,
    "failure_modes": 0.76,
    "stories": 0.68,
    "incremental_mode": 1.0
  },
  "grading_path": "benchmark/scorecards/.../grading.json",
  "comparison_path": "benchmark/scorecards/.../comparison.json",
  "reflection_id": "2026-04-09T12-00-00Z__microsoft--vscode__abc1234__augur__selective__holistic__run-1",
  "reflection_path": "agents/augur/memory/workspace/reflections/runs/2026-04-09T12-00-00Z__microsoft--vscode__abc1234__augur__selective__holistic__run-1.json",
  "notes": []
}
```

## Required Fields

- `run_id`
- `timestamp`
- `repo`
- `pinned_sha`
- `model`
- `memory_bundle`
- `skill_bundle`
- `run_number`
- `success`
- `runtime_ms.total`
- `outputs`
- `validation`
- `reflection_id`
- `reflection_path`

## Rules

- `run_id` should be globally unique.
- `runtime_ms.total` should equal the full wall-clock runtime for the run.
- Stage timings should use `0` if a stage was skipped.
- `failure_reason` should be null on success.
- `scores` may be omitted only if the run failed before scoring.
- `reflection_path` should point to a raw reflection record, not a summary.
