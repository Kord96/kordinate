---
description: Index of recognized anti-patterns by category
curated: true
scope: global
preloaded: designer
---
# Anti-Patterns Index

61 anti-patterns across 21 categories. Each has recognition signatures and remediation steps.

## Categories

| Category | Key Question |
|----------|-------------|
| Code Structure | Is the codebase organized and maintainable? |
| Dependencies | Are dependencies clean and acyclic? |
| Naming | Are names accurate, consistent, and discoverable? |
| Coupling | Are components independent with explicit interactions? |
| Complexity | Is code readable with manageable cognitive load? |
| Data | Is data accessed and modeled correctly? |
| Concurrency | Is concurrent code safe and readable? |
| Error Handling | Are errors caught precisely and propagated correctly? |
| API | Are interfaces well-designed and efficient? |
| Security | Are credentials safe and inputs sanitized? |
| Testing | Are tests reliable, fast, and isolated? |
| Performance | Are resources used efficiently under load? |
| Resources | Are allocations bounded and cleaned up? |
| Operations | Are errors handled and config managed cleanly? |
| Configuration | Are endpoints and settings externalized? |
| Infrastructure | Are environments reproducible and consistent? |
| Observability | Are logs, metrics, and traces structured and useful? |
| Frontend | Is UI state passed efficiently through components? |
| Messaging | Are messages delivered reliably? |
| Architecture | Are service boundaries clean and changes localized? |
| Code Quality | Is code original, purposeful, and non-redundant? |

## Anti-Patterns

### Code Structure

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| God object | Classes with 1000+ lines touching many unrelated concerns | [view](patterns/god-object/pattern.md) |
| Spaghetti code | Deeply nested conditionals, 500+ line functions, untraceable flow | [view](patterns/spaghetti-code/pattern.md) |
| Lava flow | Dead code, commented-out blocks, unreachable branches | [view](patterns/lava-flow/pattern.md) |
| Golden hammer | One tool/framework forced onto every problem | [view](patterns/golden-hammer/pattern.md) |
| Cargo cult | Patterns applied without understanding (factory for one type, etc.) | [view](patterns/cargo-cult/pattern.md) |
| Big ball of mud | No directory structure, any file imports any other | [view](patterns/big-ball-of-mud/pattern.md) |

### Dependencies

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Circular dependency | A imports B imports A (direct or transitive) | [view](patterns/circular-dependency/pattern.md) |
| Tight coupling | Concrete class references everywhere, no interfaces | [view](patterns/tight-coupling/pattern.md) |
| Leaky abstraction | Implementation details in interface signatures | [view](patterns/leaky-abstraction/pattern.md) |

### Naming

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Misleading names | `get*` that mutates, `is*` returning non-boolean, `validate()` that saves | [view](patterns/misleading-names/pattern.md) |
| Inconsistent naming | Mixed camelCase/snake_case, same concept with different names across files | [view](patterns/inconsistent-naming/pattern.md) |

### Coupling

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Temporal coupling | Methods must be called in specific order but nothing enforces it | [view](patterns/temporal-coupling/pattern.md) |
| Hidden side effects | Functions that look pure but modify global state, write files, send HTTP | [view](patterns/hidden-side-effects/pattern.md) |
| Train wreck | `a.getB().getC().getD().doThing()`, violating Law of Demeter | [view](patterns/train-wreck/pattern.md) |

### Complexity

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Primitive obsession | Email/phone/money as plain strings, domain concepts without dedicated types | [view](patterns/primitive-obsession/pattern.md) |
| Boolean blindness | 3+ boolean params with no names at call site: `create(true, false, true)` | [view](patterns/boolean-blindness/pattern.md) |
| Deep nesting | 5+ levels of if/for/try nesting, arrow-shaped code | [view](patterns/deep-nesting/pattern.md) |

### Data

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| N+1 queries | Database query inside a loop, ORM lazy loading in iteration | [view](patterns/n-plus-one/pattern.md) |
| Premature optimization | Caching/denormalizing before measuring, complex structures for small data | [view](patterns/premature-optimization/pattern.md) |
| Stringly typed | Strings where enums/types should be, string comparison for branching | [view](patterns/stringly-typed/pattern.md) |
| Magic numbers | Hardcoded values with no explanation | [view](patterns/magic-numbers/pattern.md) |
| Dual writes | DB write and message publish in same method without transactional outbox | [view](patterns/dual-writes/pattern.md) |
| Schema-on-read | JSON blobs in DB columns with no defined schema, `data["field"]` access with no validation | [view](patterns/schema-on-read/pattern.md) |
| Select star | `SELECT *` in production queries, ORM loading full objects for one field | [view](patterns/select-star/pattern.md) |
| Long transactions | Database transaction wrapping HTTP calls or external API calls | [view](patterns/long-transactions/pattern.md) |

### Concurrency

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Race condition | Unsynchronized read-modify-write on shared state | [view](patterns/race-condition/pattern.md) |
| Deadlock | Multiple locks acquired in inconsistent order | [view](patterns/deadlock/pattern.md) |
| Callback hell | Deeply nested callbacks, pyramid-shaped code | [view](patterns/callback-hell/pattern.md) |

### Error Handling

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Pokemon exception | `except:` or `catch(Exception)` catching everything, "gotta catch 'em all" | [view](patterns/pokemon-exception/pattern.md) |
| Error code returns | Functions returning -1/0/null for errors in languages with exceptions | [view](patterns/error-code-returns/pattern.md) |
| Log and throw | Same exception logged at multiple layers | [view](patterns/log-and-throw/pattern.md) |
| Swallowed exception | Empty catch/except blocks, errors silently ignored | [view](patterns/swallowed-exception/pattern.md) |

### API

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Chatty API | 10+ sequential calls to assemble one view, no batch endpoints | [view](patterns/chatty-api/pattern.md) |
| Anemic domain model | Model classes with only getters/setters, all logic in services | [view](patterns/anemic-domain-model/pattern.md) |
| God endpoint | Single route handling multiple operations via action parameter | [view](patterns/god-endpoint/pattern.md) |
| Breaking changes | Removed fields without deprecation, changed types, no API versioning | [view](patterns/breaking-changes/pattern.md) |
| Over/under-fetching | Full rows when caller needs one field, N+1 API calls for one view | [view](patterns/over-under-fetching/pattern.md) |

### Security

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Hardcoded credentials | `password = "..."` or `api_key = "..."` as string literals in source | [view](patterns/hardcoded-credentials/pattern.md) |
| SQL injection | String concatenation in SQL queries, `cursor.execute("... %s" % var)` | [view](patterns/sql-injection/pattern.md) |
| Insecure deserialization | `pickle.loads()` on untrusted input, `eval()` to parse data | [view](patterns/insecure-deserialization/pattern.md) |

### Testing

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Ice cream cone | E2E/integration tests vastly outnumber unit tests, inverted test pyramid | [view](patterns/ice-cream-cone/pattern.md) |
| Flaky tests | `sleep()` in test code, wall-clock assertions, non-deterministic ordering | [view](patterns/flaky-tests/pattern.md) |
| Test pollution | Tests modifying global state, missing teardown, shared mutable fixtures | [view](patterns/test-pollution/pattern.md) |

### Performance

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Unbounded growth | Lists/dicts growing without limit, no TTL on cache entries | [view](patterns/unbounded-growth/pattern.md) |
| Sync-in-async | `requests.get()` or blocking I/O inside `async def` functions | [view](patterns/sync-in-async/pattern.md) |

### Resources

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Memory leak | Event listeners never removed, growing caches in long-running processes | [view](patterns/memory-leak/pattern.md) |
| Busy waiting | `while True: sleep(0.1)` polling loops checking a flag or state | [view](patterns/busy-waiting/pattern.md) |

### Operations

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Config sprawl | Config in env vars AND yaml AND code AND database, no single source of truth | [view](patterns/config-sprawl/pattern.md) |

### Configuration

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Hardcoded URLs | `http://localhost:8080` or domain literals in production code paths | [view](patterns/hardcoded-urls/pattern.md) |

### Infrastructure

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Snowflake server | Hand-configured servers with no IaC, ssh in deploy scripts | [view](patterns/snowflake-server/pattern.md) |
| Environment parity gap | SQLite dev/Postgres prod, `if env == "development"` with different behavior | [view](patterns/environment-parity-gap/pattern.md) |

### Observability

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Log spam | `logger.info()` inside loops, log statements in hot request paths | [view](patterns/log-spam/pattern.md) |
| Metric cardinality explosion | User ID or request ID as Prometheus label values, unbounded label cardinality | [view](patterns/metric-cardinality-explosion/pattern.md) |
| Missing log context | Log messages with no request ID or correlation ID, bare `logger.error("failed")` | [view](patterns/missing-log-context/pattern.md) |

### Frontend

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Prop drilling | Same prop passed through 5+ component layers unchanged | [view](patterns/prop-drilling/pattern.md) |

### Messaging

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Fire and forget | Publishing messages with no delivery guarantee or acknowledgment check | [view](patterns/fire-and-forget/pattern.md) |

### Architecture

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Distributed monolith | Microservices sharing a single database, must deploy together | [view](patterns/distributed-monolith/pattern.md) |
| Shotgun surgery | One logical change requires editing 10+ files across different modules | [view](patterns/shotgun-surgery/pattern.md) |
| Feature envy | Methods accessing more fields from another class than their own | [view](patterns/feature-envy/pattern.md) |

### Code Quality

| Anti-pattern | What to look for | Reference |
|-------------|-----------------|-----------|
| Copy-paste programming | Identical or near-identical code blocks in multiple files | [view](patterns/copy-paste-programming/pattern.md) |
| Reinventing the wheel | Custom implementations of stdlib/well-known library functionality | [view](patterns/reinventing-the-wheel/pattern.md) |
