---
name: create-kord
description: Define a new kord — a consultation contract between agents. Creates contract, expiry script, and registers in KORD.md.
curated: true
scope: global
---

Define a new kord. $ARGUMENTS should include the kord name and optionally a description.

Authenticate before writing: use `/authenticate`.

## Usage

```
/create-kord deployer-sauron "pre-deployment health checks"
/create-kord pattern-review "architecture review for deployment changes"
```

## Procedure

1. **Gather information** — parse from arguments or ask:
    - Kord name (required, kebab-case)
    - One-line description (required)
    - Requester — which agents can invoke this kord (required, or "any")
    - Provider — which agent answers (required, exactly one; determines directory path, not written to frontmatter)
    - Mode — `stateless` (skill is self-contained) or `stateful` (needs agent context). Default: `stateful`.
    - Skill — if stateless, which skill to expose (required for stateless)

2. **Create kord directory** under the provider's agent directory:
    ```
    $KORDINATE_HOME/agents/<provider>/kords/<name>/
    ├── contract.md
    ├── data.md (empty, populated on first consult)
    └── expiry.sh
    ```

3. **Generate contract.md** — see [contract-template.md](../remember/contract-template.md) for the template. Include `mode` and `skill` fields in frontmatter.

4. **Generate expiry.sh** — use hash-based cache invalidation. Specify the directories/files the provider depends on (listed in the contract's "Cache Inputs" section):
    ```bash
    #!/bin/bash
    # Hash-based cache expiry. Exit 0 = fresh, exit 1 = stale.
    KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
    KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
    source "$KORDINATE_HOME/lib/cache.sh"

    # Check if cached data exists
    [ -f "$KORD_DIR/data.md" ] || exit 1

    # Check input hash — stale if dependencies changed since last consultation
    cache_check "$KORD_DIR/.hash" \
      "<input-path-1>" \
      "<input-path-2>" \
      || exit 1

    exit 0  # fresh
    ```
    Make executable: `chmod +x expiry.sh`

5. **Regenerate KORD.md** — run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

6. **Report** what was created:
    - "Kord `<name>` defined. Files: contract.md, data.md, expiry.sh"

## Notes

- Cache invalidation is hash-based: `expiry.sh` sources `$KORDINATE_HOME/lib/cache.sh` and compares a stored hash (`.hash`) against the current hash of the provider's input paths. After a successful consultation, Beorn runs `cache_store` to snapshot the hash alongside `data.md`.
- New kords should specify their hash inputs in the contract's "Cache Inputs" section and use those same paths in `expiry.sh`.
- Stateless kords don't need expiry.sh or data.md — the skill runs fresh every time.
