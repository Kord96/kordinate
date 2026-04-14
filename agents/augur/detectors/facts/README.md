# Fact extractors

Deterministic fact extractors live here.

This layer sits between raw detector execution and semantic atlas synthesis:

```text
framework detection -> fact extraction (including concept-evidence) -> atlas synthesis
```

Responsibilities:
- read code and manifests deterministically
- emit normalized facts following `schemas/facts-schema.md`
- emit deterministic concept evidence as normalized facts when applicable
- stay concrete and directly observable

Non-responsibilities:
- do not emit architectural concepts
- do not emit anti-patterns
- do not write atlas fields directly

Suggested layout:

```text
detectors/facts/<domain>/
  policy.yaml         # orchestration, framework applicability, fallback rules
  signatures.yaml     # broad textual/structural signals
  ast-grep.yaml       # optional executable structural rules
  semgrep.yaml        # optional executable semantic/security rules
```

Special deterministic families:

```text
detectors/facts/frameworks/<name>/         # framework-presence detection
detectors/facts/concept-evidence/<name>/   # concept-candidate evidence detection
```

Initial domains:
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

`frameworks` and `concept-evidence` are special deterministic families, not ordinary fact domains.

Borrow from codesight here:
- narrow, framework-native extractors
- AST-first where practical
- regex/signature fallback when needed
- direct usefulness even before atlas generation
