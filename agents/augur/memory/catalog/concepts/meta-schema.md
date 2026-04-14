# Concept semantics note

Concept semantics now live entirely in `concept.md` under `memory/catalog/concepts/<name>/`.

Structured detector policy and executable rule assets are no longer defined from the semantic memory side. They live under:
- `detectors/facts/concept-evidence/<name>/meta.yaml`
- `detectors/facts/concept-evidence/<name>/signatures.yaml`
- `detectors/facts/concept-evidence/<name>/ast-grep.yaml`
- `detectors/facts/concept-evidence/<name>/semgrep.yaml`

Use `memory/catalog/concepts/README.md` for the semantic catalog shape and `detectors/facts/concept-evidence/schema.md` for the detector-side schema.
