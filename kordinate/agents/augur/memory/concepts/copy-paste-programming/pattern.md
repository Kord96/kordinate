---
description: Copy-Paste Programming anti-pattern
type: anti-pattern
graphable: false
---
# Copy-Paste Programming

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Identical or near-identical code blocks in multiple files
- Duplicated error handling logic with minor variations across modules
- Same regex, validation, or transformation logic in 3+ places
- `# copied from X` or `// TODO: deduplicate` comments
- Functions with the same name or signature in different modules doing essentially the same thing
- Test files with large blocks of duplicated setup code

### Confidence

- **high** -- two or more code blocks of 10+ lines are textually identical or differ only in variable names, confirmed by clone detection tools or diff comparison
- **medium** -- the same business rule, validation regex, or error handling pattern appears in 3+ locations with minor variations
- **low** -- functions in different modules perform similar transformations with different implementations, or `# copied from` comments exist in the codebase

## Impact

Bugs fixed in one copy but not others, leading to inconsistent behavior and a maintenance burden that scales with the number of duplicates.

### Symptoms

- A bug fix applied in one location does not resolve the same bug in duplicated code elsewhere
- Behavior diverges between features that should work identically
- Code reviews repeatedly flag "this exists elsewhere" but deduplication never happens
- Refactoring one module requires hunting for and updating all copies
- Test coverage appears high but is redundant, testing the same logic multiple times

### Remediation

- Extract duplicated logic into a shared function, module, or utility library
- Use parameterization or configuration to handle variations between the copies instead of separate code paths
- Run clone detection tools (jscpd, PMD CPD, Simian) in CI to prevent new duplication from being merged
- Apply the Rule of Three: tolerate minor duplication up to two occurrences, extract on the third
- For duplicated test setup, use fixtures, factories, or shared test helpers
