# Concept Detection

Level 3 resource for the architect skill. Referenced from step 2 (detect concepts). Carries the full detection procedure from the concept catalog.

## Catalog Loading

Read both indexes from `~/.kord/agents/augur/memory/`:

- `concepts.md` — patterns index (columns: `Pattern | Description | Reference`)
- `anti-patterns.md` — anti-patterns index (columns: `Anti-pattern | What to look for | Reference`)

Each index header states its entry and category counts — use those numbers in the report, do not hardcode them. Both patterns and anti-patterns live in `~/.kord/agents/augur/memory/concepts/<name>/concept.md`. The `type` field in frontmatter distinguishes them (`pattern` vs `anti-pattern`). The two indexes use different category names (e.g., `resilience` in patterns vs `Error Handling` in anti-patterns) — always pull the category from whichever index the entry appears in.

## Stack Detection and Category Prioritization

Before scanning, identify the project's languages and frameworks (already detected in step 1) to prioritize relevant categories:

- Python: `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`; framework imports (`flask`, `fastapi`, `django`, `celery`, `sqlalchemy`, `httpx`, `requests`)
- TypeScript/JS: `package.json`, `tsconfig.json`; `express`, `nestjs`, `next`, `react`
- Go: `go.mod`; `net/http`, `grpc`, `gin`, `echo`
- Java: `pom.xml`, `build.gradle`; `spring`, `quarkus`
- Kubernetes: `kustomization.yaml`, `helm/`, Dockerfiles

Estimate project size by globbing source files (`**/*.py`, `**/*.ts`, etc.). Rank categories by relevance to the detected stack. Always scan: resilience, error-handling, security, structural, storage/data. Add stack-specific categories (concurrency for async Python, frontend for React, messaging for Kafka consumers). For projects over 500 files, limit the initial scan to the 5-8 most relevant categories and expand only if time permits.

## Pass 1 — Broad Grep (Candidate List)

Work category by category through the prioritized list. For each entry in a category, derive grep keywords from its index table row: use the `Description` column (patterns index) or `What to look for` column (anti-patterns index) to extract framework imports (`from pybreaker`, `import opossum`), directory names (`ports/`, `adapters/`), config files (`circuit_breaker.yml`), and class/function names. A hit on any keyword adds that entry to the candidate list. Skip entries with zero hits — do not read their full `concept.md`.

**Batch by category:** Build one multi-pattern regex per category (e.g., `pybreaker|opossum|CircuitBreaker|resilience4j` for Resilience) instead of grepping entry-by-entry. This keeps the number of grep invocations to one per category (~24 for patterns, ~21 for anti-patterns) rather than one per entry (~216 total).

## Pass 2 — Tool Rules (ast-grep / semgrep)

For each candidate, check for a rule file:

- `~/.kord/agents/augur/memory/concepts/<name>/ast-grep.yaml` — used by ~15 pattern entries (structural GoF patterns like factory, singleton, observer, decorator, strategy, builder, etc.)
- `~/.kord/agents/augur/memory/concepts/<name>/semgrep.yaml` — used by ~8 anti-pattern entries (security and error-handling: hardcoded-credentials, sql-injection, swallowed-exception, race-condition, etc.)

Most entries have neither. Each entry has at most one type — no entry currently has both. Check file existence before running.

Run the available rule against the project:
- `ast-grep scan --rule <rule-path> <project-dir>`
- `semgrep --config <rule-path> <project-dir> --json`

A tool match is strong evidence — mark the candidate as confirmed with high confidence. Parse semgrep JSON for file paths and line numbers. Remove confirmed candidates from the Pass 3 worklist.

## Pass 3 — Manual Signature Verification

For each candidate still unconfirmed after Pass 2 (no rule file exists, or the tool produced no matches), read its `## Recognition > ### Signatures` section from `concept.md` and verify with targeted Grep/Glob: specific imports, class names, directory layouts, config keys, naming conventions, or structural smells listed in the signatures.

## Pass 3.5 — Diagnostic Question Evaluation

For candidates still unconfirmed after Pass 3 (signature verification was inconclusive or contradictory), check for a question file at `~/.kord/agents/augur/memory/concepts/<name>/questions.yaml`. If one exists, load it and evaluate:

- For questions with `signals` hints, grep for those signals first. If all signals return zero results, answer "no" without further analysis.
- For remaining questions, read relevant code and answer yes/no with a one-line justification.
- Compute the weighted score (sum of weights for "yes" answers).
- If score >= `threshold`, mark as detected. Derive confidence from score/max_score ratio: >= 80% = high, >= threshold = medium.

Batch all questions for one concept into a single analysis pass — do not make separate passes per question. This pass typically adds 2-5 minutes for 10-30 candidate concepts.

## Confidence Assessment

After confirming a candidate in Pass 2, 3, or 3.5, read its `## Recognition > ### Confidence` section, which defines what constitutes high, medium, and low for that specific pattern. If the entry lacks a `### Confidence` section, apply the default rubric:

- **high** — unambiguous: library import, framework config, or tool rule match with no false-positive risk.
  Example: `from pybreaker import CircuitBreaker` in `client.py` — direct library usage, high.
- **medium** — partial: structural indicators present (directory layout, naming) but implementation deviates from canonical form.
  Example: `src/ports/` and `src/adapters/` exist but two modules import adapters directly — medium.
- **low** — traces only: a single keyword hit or a hand-rolled implementation without standard libraries or naming.
  Example: a `for i in range(3)` retry loop with no backoff and no library — low.

Record for each: name, category (from catalog), confidence level, file locations, one-sentence evidence note.

## Gap Identification

Determine which patterns are absent but expected given what was found. Use three checks:

1. **External calls without resilience.** Grep for HTTP clients, database drivers, and RPC stubs. If external calls exist but no circuit-breaker, retry, timeout, or bulkhead was detected, flag each as a gap.
2. **Stack-implied patterns.** Match the project's stack against expected patterns: web API implies input validation and rate limiting; async workers imply backpressure and dead-letter handling; microservices imply service discovery and distributed tracing; any service implies structured logging and health checks.
3. **Catalog cross-references.** Review which detected patterns commonly pair together. If one half of a well-known pair is present but the other was not detected, flag it (e.g., event sourcing detected without CQRS, or circuit-breaker without retry).

## Error Handling

- **No patterns detected:** Valid for small/unconventional projects. Produce empty concept sections and focus on gaps.
- **Uncommon languages:** Catalog is strongest for Python, TS/JS, Go, Java, K8s. Grep still works for structural patterns; note coverage gaps in scan_metadata.
- **Tool unavailable:** If ast-grep or semgrep is missing or a rule fails, continue with grep fallback. Note which tools were unavailable in scan_metadata.
