---
kind: concept
name: model-registry
signatures: {}
type: pattern
abstraction:
- lifecycle
- ml
scope: cross-cutting
status: primary
family: design-patterns
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- Versioned model storage with unique model names and version numbers
- Model metadata: metrics, parameters, training data lineage, artifact paths
- Stage transitions: `staging` -> `production` -> `archived`
- Methods like `log_model()`, `register_model()`, `load_model()`, `transition_model_version_stage()`
- Model artifact storage (serialized weights, ONNX exports, container images)
- Model lineage tracking: which data, code, and config produced each version
- Libraries: MLflow Model Registry, Weights & Biases, SageMaker Model Registry, Vertex AI Model Registry, Neptune

### Confidence

- **high** — `log_model()`/`register_model()` calls with versioned stage transitions and artifact storage
- **medium** — versioned model artifacts with metadata (metrics, parameters) stored alongside them
- **low** — model files saved with version numbers in filenames or directory structure

## Architecture

Look for a central catalog that versions, tracks, and governs model lifecycle from training through production.

### Review Checklist

- Every model version records its training metrics, parameters, and data lineage
- Stage transitions (staging to production) require explicit approval or automated validation
- Model artifacts are immutable once registered; new versions are created, not overwritten
- Loading a model by name resolves to the correct version for the target stage
- Registry integrates with CI/CD for automated model validation before promotion
- Retired models are archived, not deleted, preserving audit history

### Anti-patterns

- Overwriting model files in place with no version history
- No recorded link between a model version and its training data or code
- Promoting models to production without validation gates or metric checks
- Storing models only on local filesystem with no central registry

### Relationship To Other Concepts

- Related to [feature-store](/concepts/feature-store) because models and features often need coordinated version lineage.
- Related to [training-pipeline](/concepts/training-pipeline) when trained artifacts are promoted into the registry.
- Related to [experiment-framework](/concepts/experiment-framework) when promotion decisions depend on tracked experiment outcomes.

### Boundary

Use `model-registry` when trained models are cataloged, versioned, promoted, and governed through an explicit registry or approval process.

Do not use it for any model artifact folder. The key signal is a managed lifecycle registry for model versions.
