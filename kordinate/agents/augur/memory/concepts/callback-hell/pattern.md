---
description: Callback Hell anti-pattern
type: anti-pattern
graphable: false
---
# Callback Hell

## Recognition

How to identify this anti-pattern in code.

### Signatures

- Deeply nested callbacks (4+ levels of indentation from nested anonymous functions)
- Pyramid-shaped code where each async step is indented further than the last
- `.then().then().then()` chains exceeding 5 links without intermediate variables
- Error handling duplicated at every callback level instead of centralized
- No use of async/await despite the language and runtime supporting it

### Confidence

- **high** -- 4+ nested callback levels with error handling duplicated at each level in a language that supports async/await
- **medium** -- 3+ nested callbacks or a `.then()` chain longer than 5 steps without named intermediate functions
- **low** -- a single 2-level nested callback that could become deeper as the feature grows

## Impact

Unreadable and error-prone async code where control flow, error handling, and resource cleanup are nearly impossible to reason about.

### Symptoms

- Developers cannot trace the execution order without careful manual indentation-counting
- Errors are silently swallowed because a catch handler was missed at one nesting level
- Adding a new async step requires re-indenting large blocks of code
- Resource cleanup (closing connections, releasing locks) is duplicated or missed across branches
- Testing requires complex mocking of nested callback chains

### Remediation

- Convert nested callbacks to async/await syntax where the language supports it
- Extract each callback into a named function with a clear purpose and flat structure
- Use promise/future combinators (`Promise.all`, `Promise.race`) for parallel operations instead of nesting
- Centralize error handling with a single try/catch or `.catch()` at the top level of the async flow
- For languages without async/await, adopt a control flow library (async.js, Reactor) that linearizes callback sequences
