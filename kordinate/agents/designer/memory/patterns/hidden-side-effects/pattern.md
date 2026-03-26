---
description: Hidden Side Effects anti-pattern
type: anti-pattern
curated: true
scope: global
preloaded: none
---
# Hidden Side Effects

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
