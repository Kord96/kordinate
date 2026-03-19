Audit documentation for drift against implementation sources.

Compares doc pages to their source files using `docs/.source-map.yaml`. Reports which docs may be stale because their implementation sources changed.

**Input**: $ARGUMENTS (optional: specific doc page to check, e.g. `agents.md`. If omitted, checks all.)

## Usage

```
/scribe:audit-docs
/scribe:audit-docs agents.md
```

## Procedure

1. Read `docs/.source-map.yaml` to get the doc→source mapping.

2. For each doc page (or the specified one):
   a. Resolve the source file paths relative to the repo root.
   b. Run the cache check:
      ```bash
      KORDINATE_HOME="${KORDINATE_HOME:-$(git rev-parse --show-toplevel)/kordinate}"
      source "$KORDINATE_HOME/lib/cache.sh"
      cache_check "docs/.source-hashes/.<doc-page>.hash" <source-files...>
      echo $?
      ```
   c. If exit code is 1 (stale) or hash file missing: flag the doc as potentially outdated.
   d. If exit code is 0 (fresh): skip.

3. For each stale doc:
   a. Read the doc page and the changed source files.
   b. Compare: are there facts in the source that aren't reflected in the doc?
   c. Report findings with specific discrepancies.

4. After reviewing, store updated hashes for docs that are confirmed up-to-date:
   ```bash
   mkdir -p docs/.source-hashes
   cache_store "docs/.source-hashes/.<doc-page>.hash" <source-files...>
   ```

5. Summarize: which docs are stale, which are current, and what needs updating.

## Output format

```
docs audit — 2026-03-19

  agents.md         ✓ current
  hooks.md          ⚠ stale — guard-kubectl.sh changed (new bootstrap auth check)
  consultation.md   ✓ current
  memory.md         ✓ current
  infrastructure.md ⚠ stale — infra.md updated (new gateway IP)

2 docs need review, 3 current.
```

## Restrictions

- Read-only analysis — do not edit docs during audit
- Only report factual discrepancies, not style differences
- If a source file is missing, note it but don't fail
