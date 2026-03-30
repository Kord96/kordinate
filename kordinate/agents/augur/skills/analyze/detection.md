# Concept Detection

Level 3 resource for the analyze skill. Referenced from step 2 (detect concepts). Carries the full detection procedure from the concept catalog.

## Prerequisites

`ast-grep` and `semgrep` must be installed. Verify before starting detection:
```bash
ast-grep --version && semgrep --version
```
If either is missing, report the error and stop — detection cannot run without these tools.

## Catalog

The concept catalog — all indexes and concept definitions — is preloaded on boot. Use it directly from context.

- `concepts.md` — patterns, domain models, flow shapes, structure shapes index
- `anti-patterns.md` — anti-patterns index

Each index header states its entry and category counts. The `type` field in each concept's frontmatter distinguishes: `pattern`, `anti-pattern`, `domain-model`, `flow-shape`, `structure-shape`.

## Stack Detection and Category Prioritization

Before scanning, identify the project's languages and frameworks (already detected in step 1) to prioritize relevant categories. Always scan: resilience, error-handling, security, structural, storage/data. Add stack-specific categories. For projects over 500 files, limit to the 5-8 most relevant categories.

## Pass 1 — Broad Grep (Candidate List)

Work category by category. For each entry, derive grep keywords from its index table row. A hit adds that entry to the candidate list.

**Batch by category:** one multi-pattern regex per category (e.g., `pybreaker|opossum|CircuitBreaker|resilience4j` for Resilience). ~45 grep invocations total, not ~265.

## Pass 2 — Tool Rules (ast-grep / semgrep)

**Batched execution.** Run ast-grep once against the entire project using the generated sgconfig.yml:

```bash
cd $KORDINATE_HOME && ast-grep scan -c sgconfig.yml $ROOT --json 2>/dev/null
```

This scans all ~175 ast-grep rules in one pass. Parse the JSON output — each match has a `ruleId` that maps to a concept name. Mark matched concepts as confirmed with high confidence.

For semgrep rules (~8 anti-patterns), run one batched scan:

```bash
semgrep --config $KORDINATE_HOME/agents/augur/memory/concepts/*/semgrep.yaml $ROOT --json 2>/dev/null
```

Tool matches are strong evidence — high confidence. Remove confirmed candidates from the Pass 3 worklist.

If individual rules fail (syntax errors in rule files), those concepts fall through to Pass 3. The batch scan continues past individual rule failures.

## Pass 3 — Manual Signature Verification

For each candidate still unconfirmed after Pass 2, use the concept's `## Recognition > ### Signatures` section and verify with targeted Grep/Glob.

## Pass 3.5 — Diagnostic Question Evaluation

For candidates still unconfirmed after Pass 3. Check for a question file at `~/.kord/agents/augur/memory/concepts/<name>/questions.yaml`. If one exists:

- For questions with `signals` hints, grep for those signals first. If all signals return zero results, answer "no".
- For remaining questions, read relevant code and answer yes/no with a one-line justification.
- Compute the weighted score (sum of weights for "yes" answers).
- If score >= `threshold`, mark as detected. Derive confidence from score/max_score ratio: >= 80% = high, >= threshold = medium.

**Domain models, flow shapes, and structure shapes** (`type: domain-model`, `flow-shape`, `structure-shape`) — for these concept types, questions are the primary detection method. Run their questions even if they weren't grep candidates in Pass 1. These higher-level concepts are recognized from structural patterns and data shapes, not from library imports.

## Confidence Assessment

After confirming a candidate in Pass 2, 3, or 3.5, use the concept's `## Recognition > ### Confidence` section. If absent, apply the default rubric:

- **high** — unambiguous: library import, framework config, or tool rule match
- **medium** — partial: structural indicators but implementation deviates from canonical form
- **low** — traces only: a single keyword hit or hand-rolled implementation

**Domain models** are special: a project usually has one primary domain model (e.g., property-graph, ledger, catalog). When detected, promote it to the atlas `domain_model` field.

## Gap Identification

Determine which patterns are absent but expected:

1. **External calls without resilience.** Grep for HTTP clients, database drivers, RPC stubs. If no circuit-breaker, retry, timeout, or bulkhead was detected, flag as gap.
2. **Stack-implied patterns.** Web API → input validation, rate limiting. Async workers → backpressure, dead-letter. Microservices → service discovery, distributed tracing. Any service → structured logging, health checks.
3. **Catalog cross-references.** Commonly paired patterns. Event sourcing without CQRS, circuit-breaker without retry.

## Error Handling

- **No patterns detected:** Valid for small/unconventional projects. Produce empty concept sections and focus on gaps.
- **Uncommon languages:** Catalog is strongest for Python, TS/JS, Go, Java, K8s. Note coverage gaps in scan_metadata.
