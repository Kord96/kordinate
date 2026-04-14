---
description: Layered structure — horizontal layers with dependency flowing downward
type: structure-shape
abstraction: [architectural]
status: primary
scope: backend
relationships:
  related_to: [mvc, mvvm, middleware]
---
# Layered

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
