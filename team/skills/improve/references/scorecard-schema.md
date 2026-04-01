# Scorecard Schema

Level 3 reference for the train-detection skill. Defines the evaluation output format.

## Per-Round Scorecard

Written to `/tmp/train-results/scorecard-<timestamp>.json` after each training round.

```json
{
  "timestamp": "ISO-8601",
  "rounds": 5,
  "language_filter": "python",
  "topic_filter": null,
  "repos": [
    {
      "name": "owner--repo-name",
      "language": "Python",
      "stars": 230,
      "files": 42,
      "detected_concepts": ["circuit-breaker", "retry", "factory"],
      "ground_truth_concepts": ["circuit-breaker", "retry", "decorator"],
      "true_positives": ["circuit-breaker", "retry"],
      "false_positives": ["factory"],
      "false_negatives": ["decorator"]
    }
  ],
  "per_concept": {
    "<concept-name>": {
      "tp": 0,
      "fp": 0,
      "fn": 0,
      "tn": 0,
      "precision": 0.0,
      "recall": 0.0,
      "f1": 0.0
    }
  },
  "aggregate": {
    "total_concepts_evaluated": 0,
    "concepts_with_detections": 0,
    "concepts_in_ground_truth": 0,
    "precision": 0.0,
    "recall": 0.0,
    "f1": 0.0
  },
  "worst_precision": ["<concept-name>"],
  "worst_recall": ["<concept-name>"],
  "anchor_results": {
    "passed": true,
    "regressions": [],
    "repos_checked": [
      {
        "repo": "pallets/flask",
        "expected": ["decorator", "middleware", "plugin", "factory", "config-management", "router"],
        "detected": ["decorator", "middleware", "plugin", "factory", "config-management", "router"],
        "missed": [],
        "false_positives": []
      }
    ]
  },
  "improvements_applied": [
    {
      "concept": "<concept-name>",
      "type": "signature|question|ast-rule|threshold",
      "change": "Added grep keyword 'EventEmitter' to Recognition signatures",
      "reason": "Missed in 2/5 repos where event-driven pattern was implemented via custom EventEmitter class"
    }
  ]
}
```

## Training Log (Persistent)

Appended to `~/.kord/agents/augur/memory/training-log.json` after each round. Tracks improvement over time.

```json
{
  "runs": [
    {
      "timestamp": "ISO-8601",
      "repos_count": 5,
      "language": "python",
      "aggregate_f1": 0.81,
      "aggregate_precision": 0.85,
      "aggregate_recall": 0.78,
      "improvements_count": 3,
      "worst_concepts": ["hexagonal", "decorator"]
    }
  ]
}
```

## Metrics

- **Precision** = TP / (TP + FP) -- "of what we detected, how much was real?"
- **Recall** = TP / (TP + FN) -- "of what was real, how much did we detect?"
- **F1** = 2 * (P * R) / (P + R) -- harmonic mean, balances both

Per-concept metrics use micro-averaging across all repos in the round.
Aggregate metrics use macro-averaging across all concepts that appeared in at least one repo.

Concepts that appear in zero repos and are detected in zero repos are excluded from aggregate metrics (they contribute no signal).
