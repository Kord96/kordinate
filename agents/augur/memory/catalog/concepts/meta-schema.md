# Concept semantics note

Concept semantics now live entirely in `concept.md` under `memory/catalog/concepts/<name>/`.

Structured detector policy and executable rule assets are no longer defined from the semantic memory side. They live under:
- `detectors/concepts/<name>/meta.yaml`
- `detectors/concepts/<name>/signatures.yaml`
- `detectors/concepts/<name>/ast-grep.yaml`
- `detectors/concepts/<name>/semgrep.yaml`

Use `memory/catalog/concepts/README.md` for the semantic catalog shape and `detectors/concepts/schema.md` for the detector-side schema.
