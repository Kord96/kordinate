# Augur detector bundles

Generated detector execution artifacts live here.

Suggested artifacts:
- `execution-plan.json` — orchestrated detector run plan
- `frameworks/<language>.ast-grep.yaml` — bundled framework detectors
- `facts/<domain>.json` — bundled fact extractor definitions and normalization metadata
- `concept-evidence/*.json` — bundled deterministic concept-evidence manifests
- `grep-signatures.json` — grouped textual signature bundles

Execution order:
1. framework detection
2. fact extraction
3. concept detection

These files are generated for runtime execution and are not source of truth.
