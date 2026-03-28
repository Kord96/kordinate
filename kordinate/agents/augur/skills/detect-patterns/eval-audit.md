# Eval Audit

Level 3 resource for detect-patterns skill.

## Procedure

1. Read `eval-results.json` from the last eval run
2. For each concept with matches, sample 3-5 actual code matches using ast-grep
3. For each sample, judge: is this a TRUE POSITIVE (the code genuinely uses this pattern) or FALSE POSITIVE (the rule matched something unrelated)?
4. For false positives, explain WHY and suggest a specific rule fix
5. Apply the fix to the ast-grep.yaml file
6. Re-run eval on the affected repos to verify improvement
7. Commit the fix with a message describing what was wrong and how it was fixed
8. Repeat until no suspects remain or diminishing returns

## Judgment Guidelines

- A match is TRUE POSITIVE if the matched code genuinely implements the concept's structural pattern
- A match is FALSE POSITIVE if the rule matched incidentally (e.g. `.get()` matching dict access instead of queue consumption)
- High counts (>100) in repos that shouldn't use the pattern are likely false positives
- Compare counts across repos — if decorator shows 6000 in Django (expected) and 0 in trpc (expected), that's healthy variance, not a problem
- Frontend-only patterns (React hooks, JSX) matching in Python repos are always false positives

## Triage Priority

Work through results in this order:

1. **Suspicious high counts** — concepts with >100 matches in repos where the pattern is unlikely. These are almost certainly false positives with overly broad rules.
2. **Cross-language leaks** — Python-only patterns matching in TypeScript repos or vice versa. Indicates missing language constraint in the rule.
3. **Zero-match rules** — concepts with 0 matches across all repos. Either the rule is too narrow, or the test codebases genuinely don't use the pattern. Check the rule against a synthetic example to distinguish.
4. **Moderate counts** — concepts with 5-50 matches. Spot-check 3 samples to confirm they're genuine.

## Sampling Technique

To inspect actual matches for a concept:

```bash
ast-grep scan --rule agent-memory/concepts/<name>/ast-grep.yaml <repo-dir> --json | head -c 5000
```

This gives the JSON output with matched code snippets, file paths, and line numbers. Read the matched source code in context (a few lines above and below) to judge.

## Fixing Rules

Common fixes for false positives:

| Problem | Fix |
|---------|-----|
| Rule too broad (e.g. matches any `.get()`) | Add `has` constraints for surrounding context |
| Missing language filter | Add `language:` field or split into per-language rules |
| Matches comments/strings | Use `kind:` to target specific AST node types |
| Matches similar-but-different pattern | Add `not` constraints to exclude the lookalike |
| Single keyword match | Require structural parent (e.g. match `get` only inside a class with `put`) |

After applying a fix, re-run the eval script on the affected repo:

```bash
REPOS="<repo-path>" bash eval-ast-rules.sh
```

Compare the new count to the old count. If it dropped significantly without losing known true positives, the fix is good.

## Completion Criteria

The audit is done when:
- No concept has suspicious high counts in unexpected repos
- Spot-checked samples for moderate-count concepts are >80% true positives
- Zero-match rules have been verified as either correct (pattern not present) or fixed
- All fixes are committed with clear messages
