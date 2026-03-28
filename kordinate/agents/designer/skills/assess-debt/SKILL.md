---
name: assess-debt
description: Score and prioritize tech debt by scanning a project against anti-patterns from detected pattern files. Use for debt assessment, refactoring planning, or architecture health checks.
argument-hint: "<project>"
curated: true
scope: global
---

# assess-debt

Score tech debt by scanning a project against Anti-patterns sections from detected pattern files. Produces a graded report with categorized violations and prioritized recommendations for what to fix first.

## Arguments

`$ARGUMENTS` — Required: `<project>`. The project directory must exist at `~/<project>/` or `~/repos/<project>/`.

## Dependency: detect-patterns

Reads `<project-repo>/.kord/agents/designer/memory/patterns.md` written by `/detect-patterns`. If that file is absent, step 3 falls back to a quick scan.

## Steps

1. Parse project name from `$ARGUMENTS`. If missing, show usage and exit.

2. Locate the project directory. Check `~/<project>/`, then `~/repos/<project>/`. If not found, report and exit.

3. **Determine applicable patterns** — check for `<project-repo>/.kord/agents/designer/memory/patterns.md`.
   - **If present** (preferred — detect-patterns does a thorough multi-pass scan):
     1. Read the `Pattern` column from the `## Detected Patterns` table. These are the patterns whose anti-patterns you will scan for in steps 4-5.
     2. Read the `## Detected Anti-Patterns` table. These are already-confirmed anti-patterns that skip the scan in step 5 and go straight into the violations list with the file paths and detail from the `Where` and `Notes` columns. Severity assignment for these entries happens in step 4 after loading pattern files.
   - **If absent:** run a quick keyword/import/directory scan (same heuristics as `/detect-patterns` step 4, pass 1). Note in the report that results are from a quick scan and `/detect-patterns` would improve accuracy.

4. **Load anti-patterns** — two sources of anti-patterns to load:

   **a) From detected patterns:** for each pattern from step 3.1 (whether from `patterns.md` or the quick scan), read its `pattern.md` file from `~/.kord/agents/designer/memory/concepts/<pattern>/pattern.md`. Extract the `### Anti-patterns` section under `## Architecture`. This section is a bullet list where each bullet is one anti-pattern to scan for (e.g., `- No fallback — circuit opens and the caller gets raw exceptions`). Treat each bullet as a separate scannable anti-pattern. If a pattern's file has no Anti-patterns section, skip it and record it for the report header (see "Patterns detected but none have anti-patterns sections" in step 9).

   **b) From already-confirmed anti-patterns:** for each entry carried forward from step 3.2, read the anti-pattern's `pattern.md` from `~/.kord/agents/designer/memory/concepts/<anti-pattern>/pattern.md` and check for a `## Impact` section. The Impact section is a prose sentence describing consequences, not an explicit severity keyword. Map it to a severity level using these heuristics:
   - **CRITICAL** — Impact mentions reliability, correctness, data loss, outages, security, or safety consequences (e.g., "invariants impossible to enforce," "invalid state transitions slip through").
   - **RECOMMENDED** — Impact mentions maintainability, testability, comprehension, or velocity costs without immediate runtime risk (e.g., "impossible to test or modify in isolation," "business rules scattered across service classes").
   - **MINOR** — Impact mentions readability, convention, or cosmetic concerns only.

   If the `## Impact` section is absent, fall back to the `Confidence` column from the detect-patterns table as a proxy: high = CRITICAL, medium = RECOMMENDED, low = MINOR. These entries skip scanning and go directly into the violations list.

5. **Scan for violations** — for each anti-pattern from step 4a, use Grep and Glob to search the project codebase. (Items from step 4b already have severity assigned and go directly into the violations list -- do not re-scan them.) Score each newly found violation by impact:
   - **CRITICAL** (5 pts) — structural violations that affect reliability or correctness. These represent real risk: data loss, outages, or bugs that are hard to trace. Examples: no fallback when circuit opens, retrying non-idempotent operations, shared mutable state across bounded contexts.
   - **RECOMMENDED** (2 pts) — design smells that increase maintenance cost over time. Not immediately dangerous, but they compound: each change in the area takes longer and carries more risk. Examples: anemic domain models, god services, tight coupling between adapters.
   - **MINOR** (1 pt) — style or convention violations. Low individual impact, but in aggregate they signal eroding standards. Examples: inconsistent naming, missing docs, unused abstractions.

6. **Calculate score and grade**:
   - Sum all violation points.
   - **Hard floor rule:** any project with at least one CRITICAL violation gets grade C at best. If the point total alone would yield A or B, override the grade to C. If points already place the project at C, D, or F, keep the points-based grade.
   - Grade scale:

   | Grade | Points | Interpretation | Suggested action |
   |-------|--------|---------------|-----------------|
   | **A** | 0-4 | Healthy. Minor issues only; the codebase is well-maintained. | No urgent action. Address MINOR items opportunistically during related work. |
   | **B** | 5-14 | Good shape with some debt. A few design smells are accumulating. | Schedule a focused cleanup sprint. Tackle the RECOMMENDED items before they compound. |
   | **C** | 15-30 | Moderate debt. Maintenance is noticeably harder in affected areas. | Prioritize the CRITICAL items. Allocate dedicated time each cycle to pay down debt. |
   | **D** | 31-50 | Significant debt. Architecture is straining under accumulated violations. | Immediate attention needed. The CRITICAL violations are likely causing incidents or blocking features. Create a remediation plan. |
   | **F** | 51+ | Urgent. The codebase has deep structural problems. | Stop feature work in affected areas until the worst violations are addressed. Consider whether a partial rewrite of the most damaged modules is cheaper than incremental fixes. |

7. **Categorize violations** — assign each violation to exactly one of these categories to help teams divide remediation work. When a violation fits two categories, assign it to the one that best describes the root cause (e.g., "no fallback on open circuit" is Resilience because the root cause is missing fault tolerance, even though it manifests during integration):
   - **Structural:** architecture boundary violations, layering issues
   - **Data:** data access anti-patterns, missing validation
   - **Integration:** service communication issues, coupling between services
   - **Resilience:** missing fault tolerance patterns, failure handling gaps
   - **Lifecycle:** deployment, configuration, dependency management issues

8. **Prioritize recommendations** — produce a ranked list of 3-7 concrete fixes, ordered by remediation value:
   - Severity: CRITICAL first, then RECOMMENDED, then MINOR
   - Blast radius: violations affecting more modules rank higher
   - Fix effort: quick wins rank higher than multi-day refactors at the same severity
   - Clustering: group violations that share a root cause into one recommendation. Two violations share a root cause when fixing one file or introducing one abstraction resolves both (e.g., adding a resilience wrapper to an HTTP client fixes both "no circuit breaker" and "no retry" for that client; extracting a validation layer fixes both "missing input validation" and "SQL injection risk" at the same boundary).

   Each recommendation names the anti-pattern, affected files, and what the fix looks like. If a recommendation clusters multiple violations, list all of them and explain why one change addresses them together.

9. **Handle edge cases**:
   - **No patterns or anti-patterns detected** (no `patterns.md` and quick scan finds nothing, or `patterns.md` exists but both tables are empty): the project may be too small, too new, or use patterns not in the catalog. Report this clearly: "No recognized patterns detected. This can mean the project is very small, uses unconventional architecture, or the pattern catalog doesn't cover its stack. Run `/detect-patterns` for a more thorough scan." Write a minimal report with a Grade A (0 points) and a note explaining the situation.
   - **Project too small for meaningful assessment** (fewer than ~10 source files or ~500 lines of code): note that the assessment has limited value at this scale. Small projects rarely have structural debt — most issues are code-level. Still produce the report, but caveat the grade.
   - **All violations are MINOR**: this is a good result. Report Grade A or B as appropriate, and frame the MINOR items as "polish" rather than "debt." Suggest addressing them during regular code review rather than dedicated refactoring time.
   - **Patterns detected but none have anti-patterns sections**: every detected pattern was found in the catalog but none of their `pattern.md` files contain an `### Anti-patterns` section. This means the catalog has recognition data but no debt criteria for these patterns. If the `## Detected Anti-Patterns` table from step 3 has entries, the report can still include those. Otherwise, produce a minimal report noting which patterns were detected and that anti-pattern coverage is unavailable for them. Do not assign a misleading Grade A -- instead omit the grade and state that the assessment is incomplete.
   - **Anti-patterns detected but no patterns**: the `## Detected Anti-Patterns` table has entries but `## Detected Patterns` is empty. The already-confirmed anti-patterns still produce violations — score and grade them normally. Note in the report that no design patterns were detected, so the scan only covers the pre-identified anti-patterns and may undercount debt.
   - **Project uses patterns not in catalog**: some detected patterns may lack a `pattern.md` file or lack an Anti-patterns section. Skip those patterns and note them in the report header so the reader knows which areas had no anti-pattern coverage.

10. **Write the report** to `<project-repo>/.kord/agents/designer/memory/debt-assessment.md`:

   ```markdown
   # <project> — Tech Debt Assessment

   > Auto-generated by /designer:assess-debt. Last run: <date>
   > Pattern source: patterns.md (full scan) | quick scan (limited)

   <!-- Example below shows a concrete report. Replace all values with actuals from the scanned project. -->

   ## Score: 14 — Grade: C

   Moderate debt. Two CRITICAL violations in the integration and data layers pose real risk — the grade is capped at C by the hard floor rule (14 points alone would be a B). Prioritize the SQL injection and missing circuit breaker fallback before they cause an incident.

   ## By Category

   | Category | Points | Violations |
   |----------|--------|------------|
   | Structural | 0 | 0 |
   | Data | 5 | 1 |
   | Integration | 0 | 0 |
   | Resilience | 9 | 3 |
   | Lifecycle | 0 | 0 |

   ## Violations

   | Severity | Category | Pattern | Anti-pattern | File(s) | Detail |
   |----------|----------|---------|-------------|---------|--------|
   | CRITICAL | Resilience | circuit-breaker | No fallback on open circuit | `src/api/client.py` | pybreaker wraps payment calls but open state raises raw `CircuitBreakerError` to callers with no fallback. |
   | CRITICAL | Data | input-validation | String concatenation in queries | `src/api/routes.py` | User-supplied `sort_by` param interpolated into SQL via f-string instead of parameterized query. |
   | RECOMMENDED | Resilience | retry | Fixed-delay retries | `src/jobs/sync.py` | Retry loop uses `time.sleep(5)` between attempts — no backoff or jitter; thundering herd risk after outage. |
   | RECOMMENDED | Resilience | bulkhead | Shared pool across dependencies | `src/db/pool.py` | Single connection pool serves all services; one slow downstream query starves the rest. |

   ## Recommendations

   1. **Add fallback behavior to circuit breaker** (CRITICAL, Integration) — `src/api/client.py` has a circuit breaker but no fallback when it opens. Add a fallback handler that returns a cached or degraded response instead of propagating `CircuitBreakerError`. While touching this client, also convert the fixed-delay retry in `src/jobs/sync.py` to exponential backoff with jitter — both violations involve the same downstream call path. *(Fixes: no fallback on open circuit + fixed-delay retries)*
   2. **Parameterize SQL queries at API boundary** (CRITICAL, Data) — `src/api/routes.py` interpolates user input into SQL. Replace f-string interpolation with parameterized queries and add a pydantic schema to validate and whitelist the `sort_by` field. This is a quick win that eliminates an injection vector.
   3. **Isolate connection pools per service** (RECOMMENDED, Resilience) — `src/db/pool.py` uses a single shared pool. Create separate pools with individual limits so one slow consumer cannot starve others.
   ```

   Create the directory if it doesn't exist. Delegate the .md write to scribe if the guard-md hook blocks you.

11. **Report** — summarize: score, grade, grade interpretation, top 3 recommendations, and report location.
