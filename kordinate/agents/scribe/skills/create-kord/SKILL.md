---
name: create-kord
description: Define a new kord — a consultation contract between agents. Creates contract, expiry script, and registers in KORD.md.
curated: true
---

Define a new kord. $ARGUMENTS should include the kord name and optionally a description.

Authenticate before writing: use `/authenticate`.

## Usage

```
/create-kord charon-sauron "pre-deployment health checks"
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

4. **Generate expiry.sh** (stateful only) — delegates to the generic `lib/kord-expiry.sh` script, which reads `cache_inputs` from contract.md frontmatter:
    ```bash
    #!/bin/bash
    exec "${KORDINATE_HOME:-$HOME/.kord}/lib/kord-expiry.sh" "$(cd "$(dirname "$0")" && pwd)"
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

- Cache invalidation is two-stage: `expiry.sh` delegates to `lib/kord-expiry.sh`, which reads `cache_inputs` from contract.md frontmatter. Exit 0 (fresh), exit 1 (stale), or exit 2 (uncertain). Exit 2 triggers a lightweight agent review via `review.md` before deciding whether to regenerate.
- New kords specify cache inputs in the contract's frontmatter under `cache_inputs:` (paths, threshold, stale_threshold, max_age). The generic expiry script reads these — no per-kord customization needed.
- Stateless kords have ONLY contract.md — no expiry.sh, data.md, or review.md.
