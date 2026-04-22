# Observations Schemas

Contracts for Augur run-local semantic observations.

Use this directory when working on the agent-authored interpretation layer that
sits between deterministic facts and final semantic outputs.

- [observations-schema.md](observations-schema.md)
  - stable contract for run-local `observations/`
  - confidence, gaps, questions, and recommendations live here

General rule:
- detectors emit `facts/`
- the semantic phase emits `observations/`
- final semantic outputs remain `atlas.json`, `stories/`, and `narratives.yaml`
