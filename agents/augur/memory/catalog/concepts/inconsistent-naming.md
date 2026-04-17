---
description: Inconsistent Naming anti-pattern
type: anti-pattern
graphable: false
status: supporting
scope: backend
relationships:
  related_to:
  - misleading-names
  - stringly-typed
  - magic-numbers
aliases: []
disambiguates_from: []
preferred_over: []
implies: []
anti_signals: []
detector_coverage: partial
examples: []
---
# Inconsistent Naming

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Mix of camelCase and snake_case in the same file or module
- Same concept referred to by different names: `user`/`usr`/`u`, `config`/`conf`/`cfg`/`settings`
- Inconsistent pluralization: `get_users()` returns one user, `fetch_item()` returns a list
- Abbreviations used inconsistently: `repo` in one file, `repository` in another for the same thing
- Boolean variables lacking `is_`/`has_`/`should_` prefix in some places but not others
- Event names mixing tenses: `userCreated`, `deleteUser`, `onUpdatingProfile`

### Confidence

- **high** -- the same file contains both camelCase and snake_case for non-FFI code, or the same entity has 3+ different names across the codebase
- **medium** -- two modules use different names for the same domain concept (e.g., `order` vs `purchase`)
- **low** -- minor abbreviation inconsistencies across distant parts of the codebase

## Impact

Cognitive overhead increases for every reader, and text searches miss relevant code because the same concept has multiple spellings.

### Symptoms

- grep/search for a concept misses half the relevant code because of alternate names
- New contributors introduce yet another variant because they copy from different parts of the codebase
- Refactoring tools fail to catch all references because names diverge
- Code reviews repeatedly flag naming nits, wasting review cycles
- Auto-generated documentation looks incoherent with mixed conventions

### Remediation

- Establish a project glossary mapping domain concepts to their one canonical name
- Configure linters to enforce a single casing convention per language (e.g., snake_case for Python, camelCase for JavaScript)
- Run a codebase-wide rename to unify existing divergent names
- Add naming conventions to the contribution guide and enforce in CI
- Use IDE refactoring tools rather than find-and-replace to catch all references safely

### Relationship To Other Concepts

- Related to [misleading-names](/concepts/misleading-names) because both reduce semantic clarity, though inconsistent naming is about drift across the codebase rather than one bad label.
- Related to [stringly-typed](/concepts/stringly-typed) when inconsistent string names become the only schema for important concepts.
- Related to [magic-numbers](/concepts/magic-numbers) as another readability smell caused by under-expressed semantics.

### Boundary

Use `inconsistent-naming` when the same concept is named differently across modules, layers, or APIs, creating avoidable cognitive load.

Do not use it for one poorly named symbol in isolation; the issue is inconsistency, not just naming quality.
