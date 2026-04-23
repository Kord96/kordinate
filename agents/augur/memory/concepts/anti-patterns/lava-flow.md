---
kind: concept
name: lava-flow
signatures: {}
type: anti-pattern
abstraction: []
scope: backend
status: supporting
family: anti-patterns
---

# Explanation

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Commented-out code blocks left in the source
- Unreachable branches (conditions that can never be true, code after unconditional returns)
- Unused imports and variables (flagged by linters but ignored)
- Comments containing `# TODO: remove`, `# HACK`, `# FIXME: delete this`, or `# no longer used`
- Functions or methods called from nowhere in the codebase
- `@deprecated` annotations with no replacement timeline or migration path
- Feature flags that were never cleaned up after rollout

### Confidence

- **high** -- functions with zero callers, commented-out code blocks exceeding 10 lines, unreachable branches confirmed by static analysis
- **medium** -- `@deprecated` without a removal date, TODO comments referencing removal, unused imports
- **low** -- code that appears to duplicate functionality elsewhere, suspiciously old unchanged files in active directories

## Impact

Increases codebase size, confuses readers about what is live, and produces false positives in grep results.

### Symptoms

- Grepping for a function name returns dead code alongside live code, slowing investigation
- New developers attempt to use deprecated APIs because they appear available
- Test coverage reports show untestable dead branches dragging down metrics
- Build times and artifact sizes grow without delivering new value
- Refactoring hesitates because nobody knows if the "unused" code is actually needed somewhere

### Remediation

- Run static analysis tools to identify unreachable code and unused symbols
- Delete commented-out code -- it lives in version control history if ever needed
- Enforce `@deprecated` annotations with a removal-by date and track them in a backlog
- Add linter rules that fail on unused imports, variables, and unreachable code
- Schedule regular dead-code sweeps as part of maintenance sprints

### Relationship To Other Concepts

- Related to [feature-flag](/concepts/feature-flag) when stale flag branches and cleanup debt accumulate into abandoned code strata.
- Related to [copy-paste-programming](/concepts/copy-paste-programming) because duplicated abandoned paths often accumulate into dead layers of code.
- Related to [shotgun-surgery](/concepts/shotgun-surgery) when nobody deletes obsolete code because changes require too many uncertain edits.

### Boundary

Use `lava-flow` when dead or abandoned code remains in place and actively confuses maintenance or understanding.

Do not use it for code that is merely stable, old, or intentionally dormant behind a planned compatibility surface.
