---
description: Big Ball of Mud anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - layered
  - hexagonal
  - distributed-monolith
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Big Ball of Mud

## Recognition

How to identify this anti-pattern in code.

### Signatures

- No directory structure convention -- files placed arbitrarily without grouping by feature, layer, or domain
- Any file can import any other file with no enforced module boundaries
- Business logic embedded directly in controllers, handlers, or route definitions
- Database queries written directly in templates, views, or presentation layer
- No separation between public API surface and internal implementation
- Circular imports treated as normal rather than as a design smell

### Confidence

- **high** -- business logic in controllers, SQL in templates, no discernible directory organization, any-to-any import graph
- **medium** -- import graph shows no layering (presentation imports data layer and vice versa), directory names are generic ("utils", "helpers", "misc")
- **low** -- inconsistent organization that mixes conventions (some modules follow a pattern, others do not)

## Impact

No discernible architecture makes it impossible to reason about the system, predict side effects, or onboard new developers.

### Symptoms

- Changing a database schema requires modifying files across every directory
- There is no answer to "where does X logic live?" -- it could be anywhere
- Developers duplicate functionality because they cannot find existing implementations
- Test setup requires initializing the entire application because nothing is isolated
- Architectural diagrams do not match the code because the code has no enforced structure

### Remediation

- Define explicit module boundaries: group code by domain or feature, enforce import rules (e.g., domain must not import from presentation)
- Extract business logic from controllers into dedicated service or domain modules
- Move database access behind repository interfaces so queries are not scattered
- Introduce an architectural linter (e.g., import-linter for Python, ArchUnit for Java) to enforce layering
- Start with one bounded context: refactor it into a clean structure as a model for the rest

### Relationship To Other Concepts

- Related to [layered](/concepts/layered) and [hexagonal](/concepts/hexagonal) as structural counterpoints that impose boundaries a big ball of mud lacks.
- Related to [distributed-monolith](/concepts/distributed-monolith) because both describe harmful coupling, though one is usually within one codebase and the other across nominal services.

### Boundary

Use `big-ball-of-mud` when the codebase has collapsed architectural boundaries and devolved into entangled, ad hoc structure with little modular discipline.

Do not use it for any legacy codebase or any large monolith. The label should be reserved for materially unstructured entanglement.
