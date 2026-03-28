# Debt Assessment

Level 3 resource for the architect skill. Referenced from step 7 (failure modes + debt assessment). Carries the full debt scoring procedure.

## Determine Applicable Concepts

Use the detected patterns and anti-patterns from step 2 (inline detection results, not from a file).

- **Detected patterns**: these are the patterns whose anti-patterns you will scan for.
- **Detected anti-patterns**: these are already-confirmed anti-patterns that skip scanning and go straight into the violations list with file paths and evidence from the detection pass.

## Load Anti-patterns

Two sources:

**a) From detected patterns:** for each detected pattern, read its `concept.md` file from `~/.kord/agents/designer/memory/concepts/<pattern>/concept.md`. Extract the `### Anti-patterns` section under `## Architecture`. Each bullet is a separate scannable anti-pattern (e.g., `- No fallback — circuit opens and the caller gets raw exceptions`). If a pattern's file has no Anti-patterns section, skip it.

**b) From already-confirmed anti-patterns:** for each detected anti-pattern, read its `concept.md` and check for a `## Impact` section. Map impact to severity:

- **CRITICAL** — Impact mentions reliability, correctness, data loss, outages, security, or safety consequences
- **RECOMMENDED** — Impact mentions maintainability, testability, comprehension, or velocity costs without immediate runtime risk
- **MINOR** — Impact mentions readability, convention, or cosmetic concerns only

If `## Impact` is absent, derive severity from confidence: high = CRITICAL, medium = RECOMMENDED, low = MINOR. These entries skip scanning.

## Scan for Violations

For each anti-pattern from source (a), use Grep and Glob to search the project codebase. Score each:

- **CRITICAL** (5 pts) — structural violations that affect reliability or correctness. Real risk: data loss, outages, hard-to-trace bugs.
- **RECOMMENDED** (2 pts) — design smells that increase maintenance cost. Not immediately dangerous but they compound.
- **MINOR** (1 pt) — style or convention violations. Low individual impact.

## Calculate Score and Grade

Sum all violation points. Apply the hard floor rule: any project with at least one CRITICAL violation gets grade C at best.

| Grade | Points | Interpretation | Suggested action |
|-------|--------|---------------|-----------------|
| **A** | 0-4 | Healthy. Minor issues only. | No urgent action. Address MINOR items opportunistically. |
| **B** | 5-14 | Good shape with some debt. | Schedule focused cleanup. Tackle RECOMMENDED items. |
| **C** | 15-30 | Moderate debt. Maintenance noticeably harder. | Prioritize CRITICAL items. Allocate dedicated time. |
| **D** | 31-50 | Significant debt. Architecture straining. | Immediate attention. Create remediation plan. |
| **F** | 51+ | Urgent. Deep structural problems. | Stop feature work in affected areas. Consider partial rewrite. |

## Categorize Violations

Assign each violation to exactly one category. When it fits two, assign to the root cause:

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

Each recommendation names the anti-pattern, affected files, and what the fix looks like. If clustering, list all violations and explain why one change addresses them.

## Edge Cases

- **No patterns or anti-patterns detected**: project may be too small, too new, or use patterns not in the catalog. Note this in debt.interpretation. Set grade to A with score 0.
- **Project too small** (fewer than ~10 source files or ~500 lines): note limited value. Still assess.
- **All violations MINOR**: good result. Frame MINOR items as "polish" not "debt."
- **Patterns detected but none have anti-patterns sections**: catalog has recognition data but no debt criteria. Note which patterns lacked coverage. Do not assign misleading grade A — state assessment is incomplete.
- **Anti-patterns detected but no patterns**: already-confirmed anti-patterns still produce violations. Score normally. Note the scan only covers pre-identified anti-patterns.
- **Patterns not in catalog**: some detected patterns may lack a `concept.md` file. Skip and note in scan_metadata.
