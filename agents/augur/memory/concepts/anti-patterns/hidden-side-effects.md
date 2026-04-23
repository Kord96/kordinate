---
kind: concept
name: hidden-side-effects
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

- Functions that look pure (no indication in name or signature) but modify global state or module-level variables
- Methods that write files, send HTTP requests, or update a database without any hint in their name
- Functions that mutate their input arguments instead of returning new values
- `@property` decorators or getters that trigger I/O, database queries, or network calls
- Constructors (`__init__`, `constructor`) that perform network calls, file writes, or other I/O
- Functions named as queries (`find`, `get`, `calculate`) that also modify caches, counters, or logs with business meaning

### Confidence

- **high** -- a function with a query-like name (get, find, calculate) performs writes to a database, file system, or external service
- **medium** -- a function mutates its input arguments in place while also returning a value, making the mutation easy to miss
- **low** -- a function modifies module-level state (counters, caches) as a secondary effect that is arguably acceptable

## Impact

Unpredictable behavior and untestable code because callers cannot reason about what a function does based on its signature alone.

### Symptoms

- Tests require elaborate setup/teardown because "read" operations leave behind state changes
- Calling a function twice produces different results because the first call mutated hidden state
- Mocking is difficult because the function reaches out to external systems unexpectedly
- Debugging reveals that values changed "on their own" -- the mutation was hidden in an unrelated function
- Parallel execution breaks because functions that appeared safe to parallelize share hidden mutable state

### Remediation

- Make side effects explicit in the function name: `fetch_and_cache_user`, `calculate_and_log_total`
- Separate queries from commands: functions that return data should not modify state (CQS principle)
- Pass dependencies explicitly rather than reaching for globals: use dependency injection
- Make @property accessors trivial -- never perform I/O or heavy computation behind a property
- Document side effects in docstrings and type hints (e.g., `-> None` for functions that mutate in place)

### Relationship To Other Concepts

- Related to [log-and-throw](/concepts/log-and-throw) when functions or handlers perform surprising extra behavior in addition to their apparent responsibility.
- Related to [command](/concepts/command) because command/query separation helps keep side-effecting work explicit.
- Related to [query-object](/concepts/query-object) as a counterpoint where read-only operations are intentionally separated from mutating ones.

### Boundary

Use `hidden-side-effects` when code appears read-only or innocuous but performs mutation, I/O, caching, or external effects that are not made explicit by its interface or naming.

Do not use it for ordinary side-effecting commands. The problem is surprise and concealment, not mutation itself.
