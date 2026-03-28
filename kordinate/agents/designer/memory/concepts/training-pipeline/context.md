# Testing

- Test each pipeline stage (load, preprocess, train, evaluate, export) independently with small datasets
- Verify reproducibility: same data + same hyperparameters + same seed = same training result
- Test checkpoint save and resume: interrupt training, restore from checkpoint, and verify continued training matches uninterrupted
- Test the evaluation gate: models below threshold metrics must not be exported
- Verify hyperparameter externalization — changing config without code changes produces different training runs
- Test data versioning: training with a pinned data snapshot produces reproducible results
- Integration test the full pipeline end-to-end with a tiny dataset to verify stage wiring
- Assert that experiment tracking logs all parameters, metrics, and artifacts for every run

# Monitoring

- Track per-stage duration (load, preprocess, train, evaluate, export) to detect bottlenecks and regressions
- Alert on training loss plateaus or divergence — metrics not improving after expected epochs
- Monitor GPU/CPU utilization, memory usage, and disk I/O during training to detect resource starvation
- Track experiment metrics (loss, accuracy, F1) per run with hyperparameter correlation
- Alert on checkpoint failures — a missed checkpoint means potential loss of hours of training progress
- Dashboard showing active training runs, stage progress, and evaluation gate pass/fail status
- Monitor model export pipeline: alert when evaluation gate blocks a model from being exported

