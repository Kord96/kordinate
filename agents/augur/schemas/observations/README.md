# Observations Schemas

Contracts for Augur run-local semantic observations.

Use this directory when working on the normalized interpretation layer that sits
between deterministic facts and final semantic outputs.

- [observations-schema.md](observations-schema.md)
  - stable contract for run-local `observations/`
  - confidence, gaps, questions, and recommendations live here

General rule:
- detectors emit `facts/`
- deterministic or semantic observation builders emit `observations/`
- final semantic outputs remain `atlas.json`, `stories/`, and `narratives.yaml`
