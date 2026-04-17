# meta.json Schema

Canonical metadata record for one accepted Augur analysis directory.

Location:

```text
$AGENT_HOME_DIR/memory/projects/<project>/analysis/<analysis-id>/meta.json
```

`latest.json` is only a convenience pointer. `meta.json` is the durable per-analysis record.

## Schema

```json
{
  "project": "<project-name>",
  "analysis_id": "<analysis-run-timestamp>",
  "sha": "<analyzed commit SHA>",
  "commit_time": "<git commit unix timestamp as string>",
  "analysis_mode": "full | incremental | skip",
  "base_sha": "<base analysis SHA or empty>",
  "base_commit_time": "<base commit unix timestamp as string or empty>",
  "analyzed_at": "<RFC3339 timestamp when this analysis was finalized>",
  "blast": {
    "mode": "full | incremental | skip",
    "tier": 0,
    "reasons": ["<reason>"],
    "affected_components": ["<component-id>"],
    "affected_flows": ["<flow-id>"],
    "affected_state": ["<state-id>"],
    "affected_dependencies": ["<dependency-id>"],
    "affected_concepts": ["<concept-id>"]
  },
  "artifacts": {
    "root": "<absolute analysis dir>",
    "atlas": "<absolute atlas.json path>",
    "facts_index": "<absolute facts/index.json path or empty>",
    "stories_dir": "<absolute stories dir path or empty>",
    "narratives": "<absolute narratives.yaml path or empty>",
    "blast": "<absolute blast.json path or empty>"
  },
  "schemas": {
    "facts": "<absolute facts schema path>",
    "atlas": "<absolute atlas schema path>",
    "story": "<absolute story schema path>",
    "narratives": "<absolute narratives schema path>",
    "meta": "<absolute meta schema path>"
  },
  "execution": {
    "agent": "<deployed agent name>",
    "specialization": "<agent specialization>",
    "provider": "<provider name>",
    "runtime": "<runtime kind>",
    "model": "<model name>",
    "bundle_mode": "<selective | holistic>",
    "agent_contract_version": "<contract version>",
    "runtime_profile_version": "<runtime profile version>"
  },
  "validation": {
    "passed": true,
    "attempts": 1,
    "token": "<validation token>"
  }
}
```

## Rules

- `analysis_id` should identify the analysis run itself and should default to a sortable UTC timestamp such as `2026-04-16T20-21-02Z`.
- If multiple concurrent runs need isolation, a short suffix may be appended, e.g. `2026-04-16T20-21-02Z--abc123`.
- `sha` and `commit_time` describe the commit being analyzed, not the time the job started.
- `base_sha` / `base_commit_time` describe the analysis used for drift comparison. They may be empty on a full first-run analysis.
- `blast` is the durable summary of drift evaluation for this accepted analysis.
- `artifacts` and `schemas` should contain absolute paths so daemon and downstream consumers can follow them directly.
- `execution` records how the analysis was produced so runs can be compared across models, runtimes, and bundle strategies.
- `validation.passed` must be `true` for any analysis referenced by `latest.json`.
