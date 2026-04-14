---
description: Training Pipeline architectural pattern
type: pattern
testable: true
observable: true
graphable: true
abstraction: [data, ml]
---
# Training Pipeline

## Recognition

How to identify this pattern in code.

### Signatures

- Sequential stages: data loading, preprocessing, training, evaluation, model export
- Hyperparameter configuration files (YAML/JSON) or config objects
- Experiment tracking with run IDs, logged metrics, and parameters
- Methods like `fit()`, `train()`, `evaluate()`, `save_model()`
- Epoch loops, batch iterators, learning rate schedulers
- Checkpoint saving and resumption for long-running training
- Libraries: PyTorch Lightning, Keras, TFX, Kubeflow Pipelines, Metaflow, Airflow, Ray Train

### Confidence

- **high** — multi-stage pipeline with data loading, `fit()`/`train()`, evaluation, and model export, plus experiment tracking
- **medium** — training script with epoch loop, metric logging, and checkpoint saving
- **low** — script that loads data, calls a model's fit method, and saves the result

## Architecture

Look for a structured pipeline with reproducible stages from raw data to validated model artifact.

### Review Checklist

- Each stage (load, preprocess, train, evaluate, export) is a discrete, testable unit
- Hyperparameters are externalized in config, not hardcoded in training code
- Experiment tracking records all parameters, metrics, and artifacts per run
- Checkpoints are saved periodically so training can resume after failure
- Evaluation stage gates the model: only models meeting threshold metrics are exported
- Data versioning or snapshotting ensures reproducibility of training runs

### Anti-patterns

- Monolithic training script with no separation between data prep, training, and evaluation
- Hardcoded hyperparameters scattered throughout training code
- No checkpointing, requiring full restart on any failure during long training runs
- Training results not tracked, making it impossible to compare runs or reproduce outcomes
