---
description: AST rule coverage catalog — scores, methodology, and quality criteria for ast-grep pattern detection rules
---

# AST Rule Coverage

## Scoring System

Each concept is scored 1-5 based on how well ast-grep can detect it structurally:

| Score | Meaning | Action |
|---|---|---|
| **5** | Universal structural shape — one logical rule works across languages | Write ast-grep rule (per language grammar) |
| **4** | Clear structure but framework-specific — needs variant rules per framework | Write ast-grep rules per framework |
| **3** | Partially structural — name conventions + structure together | Consider ast-grep + grep combo |
| **2** | Mostly semantic — metrics, ratios, or naming only | Skip for ast-grep |
| **1** | Fully architectural/conceptual — no code shape | Skip entirely |

## Score 5 Concepts (33)

Universal structural patterns. One logical rule per language.

### Data Structures
- `bloom-filter` — bit array with multiple hash functions
- `lru-cache` — cache with eviction policy (covered by score 4 due to library-specific APIs)
- `ring-buffer` — fixed array with modulo wrap index
- `trie` — TrieNode with children dict and is_end flag
- `spatial-partitioning` — QuadTree/Octree with insert/query

### Behavioral
- `chain-of-responsibility` — handler with next/successor reference and pass-through
- `command` — (existing rule) execute/undo method pair with command queue
- `iterator` — (existing rule) __iter__/__next__ or Symbol.iterator
- `memento` — save_state/restore_state or createMemento method pairs
- `observer` — (existing rule) emit/subscribe or add_listener pattern
- `state-machine` — (existing rule) states enum with transition map
- `strategy` — (existing rule) interchangeable algorithm classes with shared interface
- `template-method` — abstract class with concrete method calling hook methods
- `visitor` — (existing rule) accept/visit double dispatch
- `specification` — is_satisfied_by with and/or/not combinators
- `monad` — bind/flatMap/and_then chaining on typed wrappers

### Creational
- `abstract-factory` — class with multiple create_*() factory methods
- `builder` — (existing rule) fluent setter chain with build() terminal
- `singleton` — (existing rule) __new__ or getInstance with class-level instance
- `decorator` — (existing rule) wrapper preserving interface with added behavior
- `object-pool` — acquire/release method pair with pool size config
- `composite` — node with children list and recursive operation

### Structural
- `bridge` — abstraction class holding implementor interface reference

### Concurrency
- `producer-consumer` — queue.put/queue.get in separate loops
- `read-write-lock` — RWMutex or acquire_read/acquire_write
- `backpressure` — bounded queue/channel with maxsize or capacity arg
- `busy-waiting` — while loop containing only sleep and condition check

### Error Handling
- `result-type` — Result/Either with Ok/Err and match/fold
- `pokemon-exception` — bare except or catch(Exception) with empty body
- `error-code-returns` — return -1/null for errors instead of exceptions
- `callback-hell` — 4+ nested callback indentation levels

### Domain
- `saga` / `saga-orchestrator` — SagaStep with execute/compensate methods
- `unit-of-work` — commit/rollback with register_dirty tracking
- `entity-component-system` — World/Registry with add_component/query
- `cache-aside` — cache.get → db.fetch → cache.set three-step sequence

### Specialized
- `ast` — node class hierarchy with visit_* methods
- `lexer-parser` — Lexer/Scanner with next_token and Token enum
- `intermediate-representation` — IRBuilder/emit with basic blocks
- `game-loop` — while loop with update/render and delta time
- `tick-simulation` — tick/step method with tick counter increment

## Quality Evaluation Methodology

### Per-Rule Quality Criteria

Each ast-grep rule is evaluated on 4 dimensions:

| Criterion | Weight | How to Measure |
|---|---|---|
| **Precision** | 40% | What % of matches are true positives? Run against 3+ known codebases. Target: >80% |
| **Recall** | 30% | What % of known instances does it find? Compare against manual audit of test codebase. Target: >60% |
| **Generality** | 20% | Does it work across coding styles? Test against idiomatic and non-idiomatic implementations |
| **Noise** | 10% | How many false positives in a large codebase? Run against 10k+ line project. Target: <5 false positives |

### Evaluation Process

1. **Write the rule** — one YAML file per language per concept
2. **Test against known positive** — run on a codebase known to use the pattern. Must match.
3. **Test against known negative** — run on a codebase that does NOT use the pattern. Must not match.
4. **Test against ambiguous** — run on a codebase with similar-but-different patterns. Check false positives.
5. **Score** — calculate precision/recall/generality/noise. If composite score < 0.6, revise the rule.

### Test Codebases

| Codebase | Language | Known Patterns |
|---|---|---|
| `sous-storefront` | TypeScript/React | reactive-store, route-guard, error-boundary, hydration, component |
| `stoik` | Python | stream-to-store, producer-consumer, backpressure, retry |
| `kordinate` | Python/TypeScript | middleware, plugin, chain-of-responsibility |

### Rule File Convention

Rules live at `concepts/<name>/ast-grep.yaml`. Multiple language variants in one file separated by `---`:

```yaml
id: <concept>-<language>-<variant>
language: Python
rule:
  pattern: |
    <structural pattern>
---
id: <concept>-<language>-<variant>
language: TypeScript
rule:
  pattern: |
    <structural pattern>
```

### Existing Rules (40)

**ast-grep score-5 (15):** active-record, builder, command, config-management, decorator, dependency-injection, factory, iterator, observer, pipeline-filter, repository, singleton, state-machine, strategy, visitor

**ast-grep score-4 (17):** api-key-auth, content-negotiation, correlation-id, cors, distributed-lock, distributed-tracing, health-check, metrics-instrumentation, oauth-oidc, optimistic-locking, optimistic-update, rate-limiting, server-sent-events, service-manager, stream-to-store, token-auth, websocket

**semgrep (8):** hardcoded-credentials, insecure-deserialization, log-and-throw, n-plus-one, race-condition, sql-injection, swallowed-exception, sync-in-async
