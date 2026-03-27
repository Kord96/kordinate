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

    Stateful kords:
    ```
    $KORDINATE_HOME/agents/<provider>/kords/<name>/
    ├── contract.md     # frontmatter + guidelines + cache inputs
    ├── data.md         # cached response (empty until first consultation)
    ├── expiry.sh       # two-stage cache check (exit 0/1/2)
    └── review.md       # prompt template for stage 2 agent review
    ```

    Stateless kords:
    ```
    $KORDINATE_HOME/agents/<provider>/kords/<name>/
    └── contract.md     # frontmatter + skill field
    ```

3. **Generate contract.md** — see [contract-template.md](../remember/contract-template.md) for the template. Include `mode` and `skill` fields in frontmatter.

4. **Generate expiry.sh** (stateful only) — use two-stage cache invalidation. Specify the directories/files the provider depends on (listed in the contract's "Cache Inputs" section):
    ```bash
    #!/bin/bash
    # Two-stage cache expiry. Exit 0 = fresh, 1 = stale, 2 = uncertain.
    KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
    KORDINATE_HOME="${KORDINATE_HOME:-$HOME/.kord}"
    source "$KORDINATE_HOME/lib/cache.sh"

    # Stage 1: Deterministic checks
    # No cached data → definitely stale
    [ -s "$KORD_DIR/data.md" ] || exit 1

    # Hash unchanged → definitely fresh
    cache_check "$KORD_DIR/.hash" \
      "<input-path-1>" \
      "<input-path-2>" \
      && exit 0

    # Hash changed but cache exists → uncertain (needs agent review)
    exit 2
    ```
    Make executable: `chmod +x expiry.sh`

5. **Generate review.md** (stateful only) — use the standard review prompt template:
    ```markdown
    ---
    description: Cache review prompt — sent to provider when expiry is uncertain
    curated: true
    scope: global
    ---

    You are reviewing whether your cached response is still valid.

    ## Changed Inputs

    {{DIFF}}

    ## Cached Response

    {{CACHED_DATA}}

    ## Decision

    Based on the changes above, is your cached response still accurate and complete?

    - If the changes are irrelevant to your cached response (e.g., comments, formatting, unrelated files), respond: `VALID`
    - If the changes affect the accuracy of your cached response, respond: `STALE`

    Respond with ONLY `VALID` or `STALE` on the first line, followed by a brief reason.
    ```

    The `{{DIFF}}` and `{{CACHED_DATA}}` placeholders are filled by Beorn at runtime.

6. **Regenerate KORD.md** — run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

7. **Report** what was created:
    - Stateful: "Kord `<name>` defined. Files: contract.md, data.md, expiry.sh, review.md"
    - Stateless: "Kord `<name>` defined. Files: contract.md"

## Notes

- Cache invalidation is two-stage: `expiry.sh` returns exit 0 (fresh), exit 1 (stale), or exit 2 (uncertain). Exit 2 triggers a lightweight agent review via `review.md` before deciding whether to regenerate.
- New kords should specify their hash inputs in the contract's "Cache Inputs" section and use those same paths in `expiry.sh`.
- Stateless kords have ONLY contract.md — no expiry.sh, data.md, or review.md.
