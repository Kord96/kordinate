# Fact Detectors

`detectors/facts/` is the family entrypoint for deterministic fact production.

This directory owns:
- the canonical fact-detector contract in [schema.md](./schema.md)
- the taxonomy for flat fact-domain detectors such as `routes/`, `handlers/`,
  `boundaries/`, and `events/`

Current fact-domain detector implementations still live as flat siblings under
`detectors/`:
- `auth-surface/`
- `boundaries/`
- `call-edges/`
- `config/`
- `data-touches/`
- `dispatch-bindings/`
- `events/`
- `execution-slices/`
- `external-clients/`
- `handlers/`
- `hot-files/`
- `import-graph/`
- `jobs/`
- `middleware/`
- `models/`
- `registrations/`
- `routes/`

Special families remain separate:
- `detectors/frameworks/`
- `detectors/concepts/`
- `detectors/scripts/`
- `detectors/utils/`
