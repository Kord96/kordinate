---
description: Training Pipeline — monitoring guidance
type: supplementary
---
# Monitoring

- Track per-stage duration (load, preprocess, train, evaluate, export) to detect bottlenecks and regressions
- Alert on training loss plateaus or divergence — metrics not improving after expected epochs
- Monitor GPU/CPU utilization, memory usage, and disk I/O during training to detect resource starvation
- Track experiment metrics (loss, accuracy, F1) per run with hyperparameter correlation
- Alert on checkpoint failures — a missed checkpoint means potential loss of hours of training progress
- Dashboard showing active training runs, stage progress, and evaluation gate pass/fail status
- Monitor model export pipeline: alert when evaluation gate blocks a model from being exported
