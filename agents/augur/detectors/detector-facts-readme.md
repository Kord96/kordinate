# Detector Fact Production

This note narrows the role of detector-owned fact production.

## Responsibility

Detectors:
- read repo code, manifests, or previously emitted facts deterministically
- emit normalized fact records that follow [schema.md](./schema.md)
- stay concrete and reproducible

Detectors must not:
- emit semantic observations
- emit confidence-based architectural conclusions
- write atlas/story/narrative structures directly

## Source Layout

```text
detectors/<domain>/
  policy.yaml
  signatures.yaml
  ast-grep.yaml       # optional
  semgrep.yaml        # optional
```

Special deterministic families:

```text
detectors/frameworks/<name>/
detectors/concepts/<name>/
```

Shared executable helpers live in:

```text
detectors/utils/
```

## Current Domain Families

- `frameworks`
- `routes`
- `models`
- `middleware`
- `external-clients`
- `registrations`
- `handlers`
- `dispatch-bindings`
- `boundaries`
- `config`
- `import-graph`
- `hot-files`
- `jobs`
- `events`
- `auth-surface`
- `call-edges`
- `data-touches`
- `execution-slices`
- `concepts`

`frameworks` and `concepts` are special deterministic families, but
they still belong to the same detector layer and still emit facts.

## Design Guidance

- keep detectors narrow
- prefer framework-native detection where useful
- prefer executable structural rules when practical
- allow aggregate or bridge detectors when they still emit deterministic facts
- keep detector metadata close to the detector definition, not duplicated on
  each emitted fact
