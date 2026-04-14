---
description: Deep Nesting anti-pattern
type: anti-pattern
graphable: false
---
# Deep Nesting

## Recognition

How to identify this anti-pattern in code.

### Signatures

- 5 or more levels of if/for/try nesting
- Arrow-shaped code: indentation increases to a peak then decreases, forming a sideways arrow
- Long functions (50+ lines) with nested conditionals that span most of the body
- `}}}}}` or dedent cascades at the end of blocks
- Nested ternary expressions: `a ? b ? c : d : e ? f : g`
- Multiple nested callbacks (related to callback hell but applies to synchronous code too)

### Confidence

- **high** -- a function contains 5+ levels of indentation with mixed if/for/try blocks and exceeds 40 lines
- **medium** -- 3-4 nesting levels with each level adding a conditional that could be an early return
- **low** -- 3 nesting levels that are semantically necessary (e.g., iterating a 3D matrix)

## Impact

Hard to read, hard to test, and high cyclomatic complexity makes it impossible to reason about which path executes under which conditions.

### Symptoms

- Developers cannot determine all possible execution paths through the function
- Unit tests require dozens of cases to achieve branch coverage
- Bug fixes in one branch inadvertently break another because the conditions interact
- Code formatters produce unreadable output because the line is mostly indentation
- New developers are afraid to touch the function and work around it instead

### Remediation

- Apply guard clauses: invert conditions and return early to flatten the main path
- Extract nested blocks into well-named helper functions
- Replace nested conditionals with polymorphism or strategy pattern where applicable
- Use loop constructs like `continue` and `break` to avoid nesting inside loops
- Set a maximum nesting depth lint rule (3-4 levels) and enforce it in CI
