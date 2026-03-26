---
description: Spaghetti Code anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Spaghetti Code

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Conditionals nested 5+ levels deep (if/else/if/else/try/if)
- Functions with 10+ parameters
- Functions exceeding 500 lines
- Goto-like flow: deeply nested breaks, continues, early returns scattered unpredictably, exception-driven control flow
- No clear function boundaries -- logic inlined rather than extracted into named functions
- Variables reused for multiple unrelated purposes within the same scope

### Confidence

- **high** -- functions exceed 500 lines with 5+ nesting levels and 10+ parameters
- **medium** -- functions exceed 200 lines with 3+ nesting levels and interleaved concerns
- **low** -- inconsistent indentation levels and scattered return statements suggesting tangled flow

## Impact

Untraceable control flow makes the code impossible to debug, test, or safely modify.

### Symptoms

- Developers cannot follow execution paths without a debugger
- Adding a simple feature requires reading and understanding hundreds of lines of context
- Tests must replicate complex state setups to reach specific branches
- Cyclomatic complexity metrics are extremely high (50+)
- Code reviews take disproportionately long for small changes

### Remediation

- Extract deeply nested blocks into well-named functions with clear inputs and outputs
- Replace nested conditionals with guard clauses (early returns at the top)
- Break long parameter lists into parameter objects or configuration structs
- Apply "compose small functions" principle: each function does one thing at one level of abstraction
- Introduce intermediate variables with descriptive names to document intent at each step
