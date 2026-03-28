# Debt Assessment

Level 3 resource for the architect skill. Referenced from step 7 (failure modes + debt assessment). Carries the full debt scoring procedure.

## Determine Applicable Concepts

Use the detected patterns and anti-patterns from step 2 (inline detection results, not from a file).

- **Detected patterns**: these are the patterns whose anti-patterns you will scan for.
- **Detected anti-patterns**: these are already-confirmed anti-patterns that skip scanning and go straight into the violations list with file paths and evidence from the detection pass.

## Load Anti-patterns

Two sources:

**a) From detected patterns:** for each detected pattern, read its `concept.md` file from `~/.kord/agents/designer/memory/concepts/<pattern>/concept.md`. Extract the `### Anti-patterns` section under `## Architecture`. Each bullet is a separate scannable anti-pattern (e.g., `- No fallback — circuit opens and the caller gets raw exceptions`). If a pattern's file has no Anti-patterns section, skip it.

**b) From already-confirmed anti-patterns:** for each detected anti-pattern, read its `concept.md` and check for a `## Impact` section. The Impact section is a prose sentence describing consequences, not an explicit severity keyword. Map it to severity:

- **CRITICAL** — Impact mentions reliability, correctness, data loss, outages, security, or safety consequences (e.g., "invariants impossible to enforce," "invalid state transitions slip through")
- **RECOMMENDED** — Impact mentions maintainability, testability, comprehension, or velocity costs without immediate runtime risk (e.g., "impossible to test or modify in isolation," "business rules scattered across service classes")
- **MINOR** — Impact mentions readability, convention, or cosmetic concerns only

If the `## Impact` section is absent, fall back to the confidence level from detection as a proxy: high = CRITICAL, medium = RECOMMENDED, low = MINOR. These entries skip scanning and go directly into the violations list.

## Scan for Violations

For each anti-pattern from source (a), use Grep and Glob to search the project codebase. Items from source (b) already have severity assigned and go directly into the violations list — do not re-scan them. Score each newly found violation:

- **CRITICAL** (5 pts) — structural violations that affect reliability or correctness. These represent real risk: data loss, outages, or bugs that are hard to trace. Examples: no fallback when circuit opens, retrying non-idempotent operations, shared mutable state across bounded contexts.
- **RECOMMENDED** (2 pts) — design smells that increase maintenance cost over time. Not immediately dangerous, but they compound: each change takes longer and carries more risk. Examples: anemic domain models, god services, tight coupling between adapters.
- **MINOR** (1 pt) — style or convention violations. Low individual impact, but in aggregate they signal eroding standards. Examples: inconsistent naming, missing docs, unused abstractions.

## Calculate Score and Grade

Sum all violation points. Apply the **hard floor rule**: any project with at least one CRITICAL violation gets grade C at best. If the point total alone would yield A or B, override the grade to C. If points already place the project at C, D, or F, keep the points-based grade.

| Grade | Points | Interpretation | Suggested action |
|-------|--------|---------------|-----------------|
| **A** | 0-4 | Healthy. Minor issues only; the codebase is well-maintained. | No urgent action. Address MINOR items opportunistically during related work. |
| **B** | 5-14 | Good shape with some debt. A few design smells are accumulating. | Schedule a focused cleanup sprint. Tackle the RECOMMENDED items before they compound. |
| **C** | 15-30 | Moderate debt. Maintenance is noticeably harder in affected areas. | Prioritize the CRITICAL items. Allocate dedicated time each cycle to pay down debt. |
| **D** | 31-50 | Significant debt. Architecture is straining under accumulated violations. | Immediate attention needed. The CRITICAL violations are likely causing incidents or blocking features. Create a remediation plan. |
| **F** | 51+ | Urgent. The codebase has deep structural problems. | Stop feature work in affected areas until the worst violations are addressed. Consider whether a partial rewrite of the most damaged modules is cheaper than incremental fixes. |

## Categorize Violations

Assign each violation to exactly one category. When a violation fits two categories, assign it to the one that best describes the root cause (e.g., "no fallback on open circuit" is Resilience because the root cause is missing fault tolerance, even though it manifests during integration):

- **Structural:** architecture boundary violations, layering issues
- **Data:** data access anti-patterns, missing validation
- **Integration:** service communication issues, inter-service coupling
- **Resilience:** missing fault tolerance, failure handling gaps
- **Lifecycle:** deployment, configuration, dependency management issues

## Prioritize Recommendations

Produce 3-7 concrete fixes, ordered by:
1. Severity: CRITICAL first
2. Blast radius: violations affecting more modules rank higher
3. Fix effort: quick wins rank higher at same severity
4. Clustering: group violations that share a root cause into one recommendation

Each recommendation names the anti-pattern, affected files, and what the fix looks like. If a recommendation clusters multiple violations, list all of them and explain why one change addresses them together. Two violations share a root cause when fixing one file or introducing one abstraction resolves both (e.g., adding a resilience wrapper to an HTTP client fixes both "no circuit breaker" and "no retry" for that client; extracting a validation layer fixes both "missing input validation" and "SQL injection risk" at the same boundary).

## Edge Cases

- **No patterns or anti-patterns detected**: the project may be too small, too new, or use patterns not in the catalog. Report this clearly: "No recognized patterns detected. This can mean the project is very small, uses unconventional architecture, or the pattern catalog doesn't cover its stack." Set grade to A with score 0 and note the situation.
- **Project too small** (fewer than ~10 source files or ~500 lines of code): note that the assessment has limited value at this scale. Small projects rarely have structural debt — most issues are code-level. Still produce the assessment, but caveat the grade.
- **All violations MINOR**: this is a good result. Report Grade A or B as appropriate, and frame the MINOR items as "polish" rather than "debt." Suggest addressing them during regular code review rather than dedicated refactoring time.
- **Patterns detected but none have anti-patterns sections**: every detected pattern was found in the catalog but none of their `concept.md` files contain an `### Anti-patterns` section. This means the catalog has recognition data but no debt criteria for these patterns. If detected anti-patterns from step 2 exist, the assessment can still include those. Otherwise, note which patterns were detected and that anti-pattern coverage is unavailable for them. Do not assign a misleading Grade A — instead omit the grade and state that the assessment is incomplete.
- **Anti-patterns detected but no patterns**: the detected anti-patterns still produce violations — score and grade normally. Note that no design patterns were detected, so the scan only covers the pre-identified anti-patterns and may undercount debt.
- **Patterns not in catalog**: some detected patterns may lack a `concept.md` file or lack an Anti-patterns section. Skip those patterns and note them so the reader knows which areas had no anti-pattern coverage.
