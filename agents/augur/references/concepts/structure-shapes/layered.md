---
kind: concept
name: layered
signatures: {}
source:
  memory_concept: memory/catalog/concepts/layered.md
type: structure-shape
abstraction:
- architectural
scope: backend
status: primary
---

# Explanation

## Recognition

### Signatures

- Directory structure: `presentation/` or `api/` → `service/` or `domain/` → `repository/` or `data/`
- Import rules: upper layers import lower layers, never reverse
- Controller → Service → Repository class pattern
- N-tier separation: web tier, application tier, data tier
- Django apps with `views.py` → `services.py` → `models.py`
- Spring `@Controller` → `@Service` → `@Repository` annotations
- Clean Architecture rings: entities → use cases → adapters → frameworks
- Layer-enforcing lint rules or architecture test frameworks (ArchUnit, import-linter)

### Confidence

- **high** — explicit layer directories with enforced import rules (lint or architecture tests preventing upward dependencies)
- **medium** — conventional layered structure but without enforcement (some cross-layer imports exist)
- **low** — code organized by feature/module rather than layer, but individual modules internally use layers

## Relationship To Other Concepts

- `layered` describes horizontal dependency structure.
- `mvc` and `mvvm` describe presentation/application coordination patterns that may live within one or more layers.
- `middleware` often implements a cross-cutting request pipeline around or before the layered core, but it is not itself the layering model.
- Prefer `layered` only when downward dependency direction across named layers is visible. Clean-architecture and onion-style systems may still fit here when the main visible signal is concentric or downward dependency discipline rather than a separate first-class topology.

### Relationship To Other Concepts

- Related to [mvc](/concepts/mvc) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [mvvm](/concepts/mvvm) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [middleware](/concepts/middleware) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `layered` when the important observation is this specific structural topology within a backend service, storage, or server-side architectural concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
