# Augur Detectors

`detectors/` is the canonical home for deterministic detector assets and
detector-owned utilities.

This layer owns:
- detector definitions that produce normalized facts
- detector-side contracts in [schema.md](./schema.md)
- shared detector-side Python helpers under `utils/`

This layer does not own:
- canonical semantic references for concepts or frameworks
- semantic observations
- atlas/story/narrative generation
- run manifests such as `startup.json` or `index.json`

## Layout

```text
detectors/
  schema.md
  utils/
  frameworks/
  concepts/
  routes/
  models/
  handlers/
  boundaries/
  ...
```

Meaning:
- ordinary detector directories such as `routes/` or `models/` define one fact
  domain
- `frameworks/` is a special deterministic family for framework-presence facts
- `concepts/` is a special deterministic bridge family that still emits
  facts, not semantic observations
- canonical explanation, signatures, and review questions live under
  `../references/`
- `utils/` contains detector-side executable helpers and runners shared by
  extraction and higher-level deterministic synthesis

## Pipeline Role

The deterministic pipeline is:

```text
detector definitions + detector utils -> facts/ -> semantic analysis
```

Detectors should emit normalized facts only. If a record needs confidence,
semantic uncertainty, recommendations, or semantic entity mappings, it belongs
in `observations/`, not in detector output.
