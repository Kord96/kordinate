---
name: detect-patterns
description: Detect design patterns, anti-patterns, and gaps in a project's source code. Use for architecture review, codebase onboarding, debt audits, or before proposing refactors.
argument-hint: "<project>"
curated: true
scope: global
---

# detect-patterns

Scan a project's source code to identify which design patterns and anti-patterns are in use and produce a structured patterns report.

## Arguments

`$ARGUMENTS` -- Required: `<project>` (e.g., `logbd`, `stoik`). The project directory must exist at `~/<project>/`, `~/repos/<project>/`, or `~/test-repos/<project>/`.

## Steps

1. **Parse** the project name from `$ARGUMENTS`. If missing, show usage and exit.

2. **Locate the project directory.** Check `~/<project>/`, then `~/repos/<project>/`, then `~/test-repos/<project>/`. If none exist, see [Error Handling](#error-handling).

3. **Load the catalogs and detect the stack.** Read both indexes:
   - `~/.kord/agents/augur/memory/concepts.md` -- patterns index (columns: `Pattern | Description | Reference`)
   - `~/.kord/agents/augur/memory/anti-patterns.md` -- anti-patterns index (columns: `Anti-pattern | What to look for | Reference`)

   Each index header states its entry and category counts -- use those numbers in the report, do not hardcode them. Both patterns and anti-patterns live in the same directory tree: `~/.kord/agents/augur/memory/concepts/<name>/pattern.md`. The `type` field in frontmatter distinguishes them (`pattern` vs `anti-pattern`). Note: the two indexes use different category names (e.g., `resilience` in patterns vs `Error Handling` in anti-patterns) -- always pull the category from whichever index the entry appears in.

   **Detect the stack.** Before scanning, identify the project's languages and frameworks so you can prioritize relevant categories:
   - Python: check for `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`; then grep for framework imports (`flask`, `fastapi`, `django`, `celery`, `sqlalchemy`, `httpx`, `requests`).
   - TypeScript/JS: check for `package.json`, `tsconfig.json`; grep for `express`, `nestjs`, `next`, `react`.
   - Go: check for `go.mod`; grep for `net/http`, `grpc`, `gin`, `echo`.
   - Java: check for `pom.xml`, `build.gradle`; grep for `spring`, `quarkus`.
   - Kubernetes: check for `kustomization.yaml`, `helm/`, Dockerfiles.
   Record the detected stack -- it drives category selection below and gap analysis in step 5.

   **Category prioritization.** Count source files: `find <project> -name '*.py' -o -name '*.ts' -o -name '*.go' -o -name '*.java' | wc -l`. For any project, rank categories by relevance to the detected stack. Always scan: resilience, error-handling, security, structural, storage/data (these surface the highest-value findings). Add stack-specific categories (e.g., concurrency for async Python, frontend for React, messaging for Kafka consumers). For projects over 500 files, limit the initial scan to the 5-8 most relevant categories and expand only if time permits.

4. **Scan for patterns and anti-patterns.** Run the three passes below once for patterns, then once for anti-patterns. Each pass narrows or confirms candidates from the previous one.

   **Pass 1 -- broad grep to build a candidate list.** Work category by category through the prioritized list from step 3. For each entry in a category, derive grep keywords from its index table row: use the `Description` column (patterns index) or `What to look for` column (anti-patterns index) to extract framework imports (`from pybreaker`, `import opossum`), directory names (`ports/`, `adapters/`), config files (`circuit_breaker.yml`), and class/function names. A hit on any keyword adds that entry to the candidate list. Skip entries with zero hits -- do not read their full `pattern.md`.

   **Batch by category:** Build one multi-pattern regex per category (e.g., `pybreaker|opossum|CircuitBreaker|resilience4j` for Resilience) instead of grepping entry-by-entry. This keeps the number of grep invocations to one per category (~24 for patterns, ~21 for anti-patterns) rather than one per entry (~216 total).

   **Pass 2 -- tool rules on candidates that have them.** For each candidate, check for a rule file:
   - `~/.kord/agents/augur/memory/concepts/<name>/ast-grep.yaml` -- used by ~15 pattern entries (structural GoF patterns like factory, singleton, observer, decorator, strategy, builder, etc.)
   - `~/.kord/agents/augur/memory/concepts/<name>/semgrep.yaml` -- used by ~8 anti-pattern entries (security and error-handling: hardcoded-credentials, sql-injection, swallowed-exception, race-condition, etc.)

   Most entries have neither. Each entry has at most one type -- no entry currently has both. Check file existence before running.

   Run the available rule against the project:
   - `ast-grep scan --rule <rule-path> <project-dir>`
   - `semgrep --config <rule-path> <project-dir> --json`

   A tool match is strong evidence -- mark the candidate as confirmed with high confidence. Parse semgrep JSON for file paths and line numbers. Remove confirmed candidates from the Pass 3 worklist.

   **Pass 3 -- manual verification of remaining candidates.** For each candidate still unconfirmed after Pass 2 (no rule file exists, or the tool produced no matches), read its `## Recognition > ### Signatures` section from `pattern.md` and verify with targeted Grep/Glob: specific imports, class names, directory layouts, config keys, naming conventions, or structural smells listed in the signatures.

   **Confidence assessment.** After confirming a candidate in Pass 2 or 3, read its `## Recognition > ### Confidence` section, which defines what constitutes high, medium, and low for that specific pattern. If the entry lacks a `### Confidence` section, apply the default rubric:
   - **high** -- unambiguous: library import, framework config, or tool rule match with no false-positive risk.
     Example: `from pybreaker import CircuitBreaker` in `client.py` -- direct library usage, high.
   - **medium** -- partial: structural indicators present (directory layout, naming) but implementation deviates from canonical form.
     Example: `src/ports/` and `src/adapters/` exist but two modules import adapters directly -- medium.
   - **low** -- traces only: a single keyword hit or a hand-rolled implementation without standard libraries or naming.
     Example: a `for i in range(3)` retry loop with no backoff and no library -- low.

   Record for each: name, category (from catalog), confidence level, file locations, one-sentence evidence note.

5. **Identify gaps.** Determine which patterns are absent but expected given what was found in steps 3-4. Use three concrete checks:
   1. **External calls without resilience.** Grep for HTTP clients, database drivers, and RPC stubs. If external calls exist but no circuit-breaker, retry, timeout, or bulkhead was detected, flag each as a gap.
   2. **Stack-implied patterns.** Match the project's stack against expected patterns: web API implies input validation and rate limiting; async workers imply backpressure and dead-letter handling; microservices imply service discovery and distributed tracing; any service implies structured logging and health checks.
   3. **Catalog cross-references.** Review which detected patterns commonly pair together. If one half of a well-known pair is present but the other was not detected, flag it (e.g., event sourcing detected without CQRS, or circuit-breaker without retry).

6. **Gemini review** (background) — before writing the final report, kick off a peer review. Pipe the draft findings to Gemini CLI in the background:
   ```bash
   gemini -m gemini-2.5-pro -o json -p "Review this pattern analysis for a $STACK project. Flag: false positives (patterns listed but evidence is weak), missed patterns (common for this stack but not listed), incorrect categories, and gaps that should have been caught. Be specific — name the pattern and why." < /tmp/patterns-draft.md > /tmp/gemini-review-patterns.json &
   ```
   Continue to step 7 immediately — don't wait. Step 7 checks whether the review has returned before finalizing the write.

7. **Write the report** using the format in [Output Format](#output-format). If the Gemini review from step 6 has returned, incorporate valid critiques: add missed patterns with a note "(flagged by Gemini review)", adjust confidence levels, or add gaps. Ignore critiques that contradict tool evidence (ast-grep/semgrep matches outweigh Gemini opinions). If the review has not returned yet, write the report without it and note "Gemini review pending" in the report header. Create the directory if it doesn't exist. Delegate the .md write to scribe if the guard-md hook blocks you.

8. **Report** -- summarize to the caller: pattern count, anti-pattern count, key gaps, whether Gemini review was incorporated, and report location.

## Output Format

Write the report to `<project-repo>/.kord/agents/augur/memory/patterns.md` using this structure:

```markdown
# <project> -- Detected Patterns

> Auto-generated by /designer:detect-patterns. Last run: <date>
> Scanned against: <N>-pattern + <M> anti-pattern catalog. Tools used: <list which of ast-grep, semgrep, grep were available>

## Detected Patterns

| Pattern | Category | Confidence | Where | Notes |
|---------|----------|-----------|-------|-------|
| circuit-breaker | Resilience | high | `src/api/client.py` | pybreaker wrapping payment service calls |
| hexagonal | Structural | medium | `src/ports/`, `src/adapters/` | Port interfaces present but adapters bypass ports in 2 modules |
| retry | Resilience | low | `src/jobs/sync.py` | Manual retry loop, no jitter or backoff strategy |

## Detected Anti-Patterns

| Anti-Pattern | Category | Confidence | Where | Notes |
|-------------|----------|-----------|-------|-------|
| god-object | Code Structure | high | `src/services/main.py` (1847 lines) | Single class handling orders, payments, and notifications |
| swallowed-exception | Error Handling | medium | `src/api/routes.py` | Bare `except: pass` in 3 route handlers |

## Gaps

| Pattern | Why it's relevant | Recommendation |
|---------|------------------|----------------|
| bulkhead | Shared DB pool across all services | Isolate connection pools per bounded context |
```

Order by confidence (high first), then alphabetically. Use project-relative file paths. One sentence max per note. The example rows above are illustrative -- actual output reflects the scanned project.

## Error Handling

- **Project not found:** List checked paths and suggest verifying the project name. Do not scan.
- **No patterns detected:** Valid for small/unconventional projects. Write the report with empty tables and focus on gaps.
- **Uncommon languages:** Catalog is strongest for Python, TS/JS, Go, Java, K8s. Grep still works for structural patterns; note coverage gaps in the report header.
- **Tool unavailable:** If ast-grep or semgrep is missing or a rule fails, continue with grep fallback. Note which tools were unavailable in the report header.
