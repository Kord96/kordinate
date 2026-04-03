---
description: Training Pipeline — monitoring guidance
---
## Monitoring

Track per-stage execution, training convergence, resource utilization, and checkpoint reliability across training runs.

### Key Metrics

- `training_stage_duration_seconds` (histogram) — execution time per pipeline stage (load, preprocess, train, evaluate, export)
- `training_loss` (gauge) — current loss value per run, tracked per epoch for convergence monitoring
- `training_evaluation_metric` (gauge) — accuracy, F1, or domain-specific metric per run at evaluation stage
- `training_gpu_utilization_ratio` (gauge) — GPU utilization during training, detects resource starvation or underuse
- `training_checkpoint_failures_total` (counter) — failed checkpoint saves that risk losing training progress
- `training_evaluation_gate_results_total` (counter) — evaluation gate outcomes (pass/fail) controlling model export

### Alerts

- Training loss plateaued or diverging after expected number of epochs
- Checkpoint save failed (potential loss of hours of training progress)
- GPU/CPU utilization abnormally low during training (resource starvation or misconfiguration)
- Evaluation gate blocking model export (model does not meet quality threshold)
- Pipeline stage duration significantly exceeding historical baseline (bottleneck or regression)
