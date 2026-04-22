# meta.json Schema

Canonical agent-owned metadata record for one accepted Augur analysis directory.

Location:

```text
$AGENT_HOME_DIR/memory/projects/<project>/analysis/<sha>/<analysis-id>/meta.json
```

`analysis/latest.json` and `analysis/<sha>/latest.json` are convenience pointers. `meta.json` is the durable per-analysis record.

Daemon-owned runtime telemetry belongs to `klaude-daemon` response metadata and Loki logs, not to Augur `meta.json`.

## Schema

```json
{
  "request_id": "<daemon request id or empty>",
  "repository": {
    "project": "<owner/repo or slug>",
    "commit": "<analyzed commit SHA>",
    "commit_time": "<git commit unix timestamp as string>",
    "base_commit": "<base analysis SHA or empty>",
    "base_commit_time": "<base commit unix timestamp as string or empty>",
    "file_count": 0,
    "files_read_count": 0,
    "repo_tokens_est": 0
  },
  "agent": {
    "name": "<deployed agent name>",
    "specialization": "<agent specialization>",
    "bundle_mode": "evidence-driven",
    "agent_contract_version": "<contract version>",
    "runtime_profile_version": "<runtime profile version>"
  },
  "analysis": {
    "id": "<analysis-run-timestamp>",
    "mode": "full | incremental | skip",
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
      "root": "<relative analysis dir marker>",
      "atlas": "<relative atlas.json path>",
      "facts_index": "<relative facts/index.json path or empty>",
      "stories_dir": "<relative stories dir path or empty>",
      "narratives": "<relative narratives.yaml path or empty>",
      "blast": "<relative blast.json path or empty>",
      "overlays_dir": "<relative overlays dir path>",
      "overlays_index": "<relative overlays/index.json path>",
      "reflections_dir": "<relative reflections dir path>",
      "reflections_index": "<relative reflections/index.json path>"
    },
    "schemas": {
      "facts": "<absolute facts schema path>",
      "atlas": "<absolute atlas schema path>",
      "story": "<absolute story schema path>",
      "narratives": "<absolute narratives schema path>",
      "meta": "<absolute meta schema path>"
    },
    "inputs": {
      "bundles": [
        {
          "kind": "memory | skill | runtime",
          "id": "<bundle id>",
          "path": "<absolute path>",
          "tokens_est": 0
        }
      ],
      "loaded_refs": [
        {
          "kind": "memory | skill | schema | guide | runtime",
          "path": "<absolute path>",
          "tokens_est": 0
        }
      ],
      "artifacts": [
        {
          "kind": "<artifact kind>",
          "path": "<absolute path>",
          "tokens_est": 0
        }
      ],
      "totals": {
        "bundle_tokens_est": 0,
        "loaded_ref_tokens_est": 0,
        "artifact_tokens_est": 0,
        "repo_tokens_est": 0,
        "validation_tokens_est": 0,
        "total_tokens_est": 0
      }
    },
    "validation": {
      "passed": true,
      "attempts": 1,
      "token": "<validation token>"
    }
  }
}
```

## Rules

- `request_id` should be the daemon request correlation id when available. It is the join key back to shared daemon telemetry.
- `repository.project` identifies the analyzed repository and should use the canonical display id when known, such as `Kord96/logbd`.
- `repository.commit_time` describes the commit being analyzed, not the time the job started.
- `repository.base_commit` / `repository.base_commit_time` describe the analysis used for drift comparison. They may be empty on a full first-run analysis.
- `repository.file_count` should count repo files in the analyzed working tree. `files_read_count` and `repo_tokens_est` are Augur-side estimates derived from grounded repo refs, not daemon billing truth.
- `analysis.id` should identify the analysis run itself and should default to a sortable UTC timestamp such as `2026-04-16T20-21-02Z`.
- If multiple concurrent runs need isolation, a short suffix may be appended, e.g. `2026-04-16T20-21-02Z--abc123`.
- `analysis.mode` should describe the accepted Augur workflow mode (`full`, `incremental`, or `skip`).
- `analysis.blast` is the durable summary of drift evaluation for this accepted analysis.
- `analysis.artifacts` should use run-relative paths so the analysis directory remains portable.
- `analysis.schemas` should contain absolute paths so daemon and downstream consumers can follow them directly.
- `analysis.inputs` is Augur-owned prompt/input estimation, not runtime billing truth. All estimated token fields must use `_est`.
- `analysis.inputs.bundles` should describe selected bundle files. `loaded_refs` should list additional Augur-loaded files such as guides and schemas. `artifacts` should list prepared run artifacts consulted for startup or repair context.
- `analysis.validation.passed` must be `true` for any analysis referenced by `analysis/latest.json` or `analysis/<sha>/latest.json`.
