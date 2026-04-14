# Detector layout

Augur now uses an explicit split:

- `memory/catalog/**` — semantic memory
- `detectors/**` — deterministic detection source
- `bundles/**` — generated runtime artifacts

## Target state

### Semantic side
- `memory/catalog/concepts/<name>.md`
- `memory/catalog/frameworks/<name>/framework.md`

### Detector side
- `detectors/concepts/<name>/policy.yaml`
- `detectors/concepts/<name>/signatures.yaml`
- `detectors/concepts/<name>/ast-grep.yaml`
- `detectors/concepts/<name>/semgrep.yaml`
- `detectors/frameworks/<name>/policy.yaml`
- `detectors/frameworks/<name>/signatures.yaml`

### Generated runtime bundles
- `bundles/memory/*`
- `bundles/detectors/*`
