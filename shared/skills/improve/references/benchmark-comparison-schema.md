# Benchmark Comparison Schema

Defines the normalized snapshot and trend artifacts used to compare benchmark runs over time.

This schema is model-agnostic and supports:

- `generic` vs `augur`
- backend-vs-backend comparisons
- bundle-vs-bundle comparisons
- longitudinal benchmark tracking

## Snapshot Summary

Recommended path:

```text
/kord/augur/memory/global/benchmarks/snapshots/<snapshot-id>.json
```

Example:

```json
{
  "snapshot_id": "2026-04-11__pilot-v1",
  "benchmark_version": "pilot-v1",
  "captured_at": "2026-04-11T12:00:00Z",
  "repo_count": 12,
  "run_count": 48,
  "dimensions": {
    "agent_modes": ["generic", "augur"],
    "backend_models": ["gpt-5.4", "gemini-3.1-pro-preview"],
    "memory_bundles": ["selective", "holistic"],
    "skill_bundles": ["selective", "holistic"]
  },
  "aggregates": [
    {
      "agent_mode": "augur",
      "backend_model": "gpt-5.4",
      "memory_bundle": "selective",
      "skill_bundle": "selective",
      "quality_score_mean": 0.81,
      "runtime_ms_mean": 37100,
      "tokens_total_mean": 48300,
      "estimated_cost_mean": 0.0,
      "cache_hit_ratio_mean": 0.74,
      "uncached_prefix_bytes_mean": 6400,
      "quality_per_second_mean": 0.0218,
      "quality_per_1k_tokens_mean": 0.0168,
      "quality_per_dollar_mean": null
    }
  ],
  "comparisons": [
    {
      "comparison_type": "generic-vs-augur",
      "backend_model": "gpt-5.4",
      "repo_scope": "same-snapshot",
      "auguration_delta_quality": 0.12,
      "augmentation_delta_runtime_ms": 6400,
      "augmentation_delta_tokens": 9200,
      "augmentation_delta_estimated_cost": 0.0,
      "augmentation_delta_cache_hit_ratio": 0.21
    }
  ]
}
```

## Trend Summary

Recommended path:

```text
/kord/augur/memory/global/benchmarks/trends/<trend-id>.json
```

Example:

```json
{
  "trend_id": "quality-cache-trend__gpt-5.4__pilot-v1",
  "benchmark_version": "pilot-v1",
  "series": [
    {
      "captured_at": "2026-04-10T12:00:00Z",
      "agent_mode": "augur",
      "backend_model": "gpt-5.4",
      "quality_score_mean": 0.77,
      "runtime_ms_mean": 40200,
      "tokens_total_mean": 52500,
      "cache_hit_ratio_mean": 0.61
    },
    {
      "captured_at": "2026-04-11T12:00:00Z",
      "agent_mode": "augur",
      "backend_model": "gpt-5.4",
      "quality_score_mean": 0.81,
      "runtime_ms_mean": 37100,
      "tokens_total_mean": 48300,
      "cache_hit_ratio_mean": 0.74
    }
  ]
}
```

## Required Comparison Dimensions

Every benchmark comparison system should support:

- `quality`
- `speed`
- `tokens`
- `estimated_cost`
- `cache_hit_ratio`
- `uncached_prefix_bytes`
- `quality_per_second`
- `quality_per_1k_tokens`
- `quality_per_dollar`

## Core Questions

The comparison layer should make it easy to answer:

- Is Augur better than generic on the same repo and model?
- Is Augur faster or slower than generic?
- How many additional tokens does Augur spend?
- Is the quality gain worth the cost and latency?
- Are layered prompts improving cache utilization over time?
- Which backends benefit most from Augur scaffolding?
