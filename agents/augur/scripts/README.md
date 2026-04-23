# Augur Scripts

This tree is organized by workflow role.

- `run/`
  - runtime preparation and sealing entrypoints for `/analyze`
- `synthesis/`
  - deterministic planning and atlas-scaffolding helpers
- `build/`
  - bundle generation and graph compilation
- `maintenance/`
  - local maintenance, export, and migration utilities
- `lib/`
  - shared script-side support modules

Detector-owned extraction CLIs and extraction support code live under `detectors/`, not here.
Evaluation and ablation tooling lives under `../benchmarks/`.
