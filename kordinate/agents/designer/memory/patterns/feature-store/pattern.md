---
description: Feature Store architectural pattern
type: pattern
curated: true
scope: global
preloaded: none
---
# Feature Store

## Recognition

How to identify this pattern in code.

### Signatures

- Centralized feature repository with feature definitions and metadata
- Dual serving paths: online (low-latency) and offline (batch/historical)
- Methods like `get_online_features()`, `get_historical_features()`, `apply()`
- Feature views or feature tables defining transformations from raw data to features
- Point-in-time-correct joins for training data to prevent data leakage
- Entity keys mapping features to business objects (user, item, transaction)
- Libraries: Feast, Tecton, Hopsworks, SageMaker Feature Store, Databricks Feature Store

### Confidence

- **high** — `get_online_features()`/`get_historical_features()` calls with feature view definitions and entity keys
- **medium** — centralized feature definitions with separate online and offline storage backends
- **low** — shared data transformations reused between training pipelines and serving code

## Architecture

Look for a centralized registry that serves pre-computed features consistently to both training and inference.

### Review Checklist

- Feature definitions are versioned and shared between training and serving
- Online store serves features with latency under the serving SLA
- Offline store supports point-in-time-correct joins for training data
- Feature transformations are defined once and materialized to both stores
- Entity keys are consistent across features and across online/offline paths
- Feature freshness and staleness are monitored with clear SLAs

### Anti-patterns

- Duplicating feature logic in training scripts and serving code (training-serving skew)
- No point-in-time correctness, causing future data to leak into training features
- Online store used for batch training (latency costs, missing historical data)
- Features defined ad-hoc per model with no shared registry or versioning
