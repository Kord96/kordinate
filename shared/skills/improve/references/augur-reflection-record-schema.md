# Augur Reflection Record Schema

Defines the raw per-run reflection record stored under Augur-owned workspace memory.

Raw reflection records are append-only evidence. They are independent of `/improve`.

## Recommended Path

```text
agents/augur/memory/workspace/reflections/runs/<reflection-id>.json
```

## Schema

```json
{
  "reflection_id": "2026-04-09T12-00-00Z__microsoft--vscode__abc1234__augur__selective__holistic__run-1",
  "captured_at": "2026-04-09T12:00:15Z",
  "repo": "microsoft/vscode",
  "repo_url": "https://github.com/microsoft/vscode",
  "pinned_sha": "abc1234",
  "model": "augur",
  "memory_bundle": "selective",
  "skill_bundle": "holistic",
  "run_number": 1,
  "analysis_mode": "full",
  "correlation_id": "job-123",
  "reflection_prompt_path": "agents/augur/skills/analyze/reflection-prompt.md",
  "reflection": {
    "project": "This repo hides some core extension boundaries behind registration code rather than directories. Adapter-heavy folders look more important than they are. Queue names and contribution registries provided stronger evidence than file names for architecture inference.",
    "general": "Consider adding grep or AST support for registration tables, plugin manifests, and job registries. Avoid over-weighting folders named service or adapter when they are only thin wrappers."
  }
}
```

## Required Fields

- `reflection_id`
- `captured_at`
- `repo`
- `pinned_sha`
- `model`
- `memory_bundle`
- `skill_bundle`
- `run_number`
- `reflection.project`
- `reflection.general`

## Rules

- Raw reflection records are immutable once written.
- `reflection.project` and `reflection.general` must remain strings for daemon compatibility.
- If a field has no strong lesson, store an empty string rather than omitting it.
- Reflection records should be created whether or not `/improve` is running, as long as reflection was enabled for the run.
