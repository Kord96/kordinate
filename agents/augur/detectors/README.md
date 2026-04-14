# Augur deterministic detectors

Detector source assets define the deterministic Phase 1 pipeline. They are
separate from semantic memory and should be organized by the kind of facts they
help produce, not by which rule engine happens to execute them.

Current source families:

- `facts/` — normalized fact producers, including shared framework detection
- `concepts/` — transitional source tree for deterministic concept-evidence
  inference rules and metadata
- `frameworks/` — transitional legacy framework-specific source tree being
  folded into `facts/frameworks`

Generated runtime bundles live under `../bundles/detectors/`. Those are still
the runtime inputs today, but they should be understood as derived artifacts of
the deterministic detector source tree rather than the source of truth.
