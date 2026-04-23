# Facts Schemas

Contracts for Augur run-local deterministic fact artifacts.

Use this directory when working on the facts layer specifically.

- [facts-schema.md](facts-schema.md)
  - consumer-facing facts contract entrypoint
  - points to the canonical detector-owned facts schema
- [concepts-schema.md](concepts-schema.md)
  - raw deterministic precursor contract for `observations/concepts.json`

Canonical source:
- [../../detectors/schema.md](../../detectors/schema.md)
  - canonical normalized facts schema owned by detector infrastructure

General rule:
- use these files for stable artifact contracts
- use run-local `index.json` for retrieval policy and run-specific interpretation guidance
