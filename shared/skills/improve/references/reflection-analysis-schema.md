# Reflection Analysis Schema

Defines the shared analysis outputs that `/improve reflection` should consume when comparing stored reflections across models.

## Goal

The reflection pipeline should support questions like:

- which models converge on the same improvement ideas?
- which models produce unique but useful ideas?
- which models are mostly redundant?
- which bundles or repo families cause models to diverge?

## Data Flow

1. runtime captures per-run reflection payloads
2. Kafka transports reflection events
3. raw reflection records are persisted under Augur-owned project storage
4. a normalized global reflection index is built from those raw records
5. aggregation produces cross-run and cross-model summaries from the index
6. `/improve reflection --from-runs` reads those summaries

## Normalized Global Index

Recommended normalized record root:

```text
/kord/augur/memory/global/reflections/records/<reflection-id>.json
```

Recommended manifest:

```text
/kord/augur/memory/global/reflections/manifest.json
```

The normalized index should preserve provenance back to the raw reflection record and should carry enough model/runtime metadata for cross-model comparison without joining against discovery data.

## Summary Output

Recommended summary file:

```text
/kord/augur/memory/projects/<repo>/reflections/summaries/<summary-id>.json
```

Or for cross-project analysis:

```text
/kord/augur/memory/global/reflections/summaries/<summary-id>.json
```

## Summary Shape

```json
{
  "summary_id": "2026-04-10T12-00-00Z__all-projects",
  "generated_at": "2026-04-10T12:00:00Z",
  "group_label": "all-projects",
  "source_reflection_ids": [],
  "record_count": 0,
  "model_profiles": [
    {
      "model": "gpt-5.4",
      "provider": "openai",
      "runtime_kind": "codex-sdk",
      "reflection_count": 12,
      "signal_count": 31
    }
  ],
  "consensus_signals": [
    {
      "signal_id": "a1b2c3d4e5f6",
      "text": "Add detector support for plugin registration tables.",
      "models": ["gpt-5.4", "gemini-3.1-pro-preview"],
      "model_count": 2
    }
  ],
  "unique_yield": [
    {
      "model": "deepseek-reasoner",
      "unique_signal_count": 4,
      "unique_signals": []
    }
  ],
  "complementarity": [
    {
      "left_model": "gpt-5.4",
      "right_model": "gemini-3.1-pro-preview",
      "shared_signal_count": 5,
      "union_signal_count": 17,
      "jaccard_similarity": 0.2941,
      "left_only_count": 7,
      "right_only_count": 5
    }
  ]
}
```

## Derived Metrics

These summaries should support at least:

- `consensus_rate`
  - proportion of signals seen from more than one model
- `unique_yield`
  - what one model surfaces that the others did not
- `redundancy`
  - repeated suggestions already covered by others
- `complementarity`
  - whether the union of two models produces meaningfully more signal than either alone

## Notes

- Raw reflections remain the source evidence.
- The normalized global index is a derived but query-friendly layer.
- Summary files are derived artifacts and may be regenerated.
- Signal clustering can start with sentence-level normalization and later become embedding- or label-based.
