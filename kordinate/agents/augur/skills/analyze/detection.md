# Concept Detection

Level 3 resource for the analyze skill. Referenced from step 2 (detect concepts).

## Catalog

All concept definitions are preloaded on boot. Use them directly from context.

- `concepts.md` — patterns, domain models, flow shapes, structure shapes
- `anti-patterns.md` — anti-patterns

The `type` field in each concept's frontmatter distinguishes: `pattern`, `anti-pattern`, `domain-model`, `flow-shape`, `structure-shape`.

## Detection Order

Detection runs in three steps. Implementation patterns first (they inform higher-level detection), then domain models and shapes.

```
Step 1: AST rules     — one ast-grep run + one semgrep run (fast, high confidence)
Step 2: Grep scan     — keyword search builds candidate list (fast, low confidence)
Step 3: Questions     — diagnostic evaluation confirms candidates + detects shapes (slow, medium-high confidence)
```

After all three steps: assess confidence, identify gaps.

## Step 1 — AST Rules

Run ast-grep against the project using the per-rule scanner:

```bash
python3 $KORDINATE_HOME/agents/augur/skills/analyze/scripts/run_ast_grep.py $ROOT
```

This runs each concept's `ast-grep.yaml` individually and merges results. Parse the JSON output — each match has a `ruleId` that maps to a concept name. Mark matched concepts as **confirmed, high confidence**.

Do NOT use `ast-grep scan -c sgconfig.yml` — the `ruleDirs` approach fails when concept directories contain non-rule YAML files (questions.yaml).

Run semgrep once for anti-pattern rules:

```bash
semgrep --config $KORDINATE_HOME/agents/augur/memory/concepts/*/semgrep.yaml $ROOT --json
```

Record confirmed concepts with file paths and line numbers. These skip Step 2 and Step 3.

## Step 2 — Grep Scan

For each category in the concept index, build one regex from the index table keywords and grep the project. A hit adds that concept to the **candidate list**.

Example: for the Resilience category, grep `pybreaker|opossum|CircuitBreaker|resilience4j` in one invocation.

Work through all categories (~45 grep invocations total). Skip concepts already confirmed in Step 1.

**Important:** grep builds a candidate list — it does not confirm detection. A grep hit means "worth investigating," not "pattern detected."

## Step 3 — Diagnostic Questions

Evaluate diagnostic questions for two groups:

**Group A — grep candidates.** For each concept that had grep hits in Step 2 but was not confirmed in Step 1, load its `questions.yaml` and evaluate:

- For questions with `signals` hints, grep for those signals first. All signals return zero → answer "no" without further analysis.
- For remaining questions, read the relevant code and answer yes/no with a one-line justification.
- Compute weighted score. If score >= `threshold`, mark as detected.

If a concept has no `questions.yaml`, use its `## Recognition > ### Signatures` section instead — verify with targeted Grep/Glob against the specific imports, class names, and directory layouts listed.

**Group B — domain models, flow shapes, structure shapes.** These higher-level concepts are detected from data shapes and structural patterns, not library imports. Run their questions regardless of whether they had grep hits. Every concept with `type: domain-model`, `flow-shape`, or `structure-shape` gets evaluated here.

## Confidence Assessment

After detection, assign confidence per concept:

- **high** — AST rule match (Step 1), or question score >= 80% of max
- **medium** — question score >= threshold but < 80%, or strong signature match
- **low** — single grep hit or weak signature match

Use the concept's `## Recognition > ### Confidence` section if it defines concept-specific thresholds. Otherwise use the defaults above.

## Domain Model Promotion

A project usually has one primary domain model that defines its core data shape (e.g., property-graph, ledger, catalog). When detected, promote it to the atlas `domain_model` field and reference it in component descriptions. Secondary domain models (e.g., search-index alongside a catalog) are recorded normally.

## Gap Identification

Determine which patterns are absent but expected:

1. **External calls without resilience.** Grep for HTTP clients, database drivers, RPC stubs. If no circuit-breaker, retry, timeout, or bulkhead was detected, flag as gap.
2. **Stack-implied patterns.** Web API → input validation, rate limiting. Async workers → backpressure, dead-letter. Microservices → service discovery, distributed tracing. Any service → structured logging, health checks.
3. **Catalog cross-references.** Commonly paired patterns. Event sourcing without CQRS, circuit-breaker without retry.

## Error Handling

- **No patterns detected:** Valid for small/unconventional projects. Produce empty concept sections and focus on gaps.
- **Uncommon languages:** Catalog is strongest for Python, TS/JS, Go, Java, K8s. Note coverage gaps in scan_metadata.
