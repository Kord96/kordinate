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
/scribe:kord deployer-sauron "pre-deployment health checks"
/scribe:kord pattern-review "architecture review for deployment changes"
```

## Procedure

1. **Gather information** — parse from arguments or ask:
    - Kord name (required, kebab-case)
    - One-line description (required)
    - Requester — which agents can invoke this kord (required, or "any")
    - Provider — which agent answers (required, exactly one)
    - Mode — `stateless` (skill is self-contained) or `stateful` (needs agent context). Default: `stateful`.
    - Skill — if stateless, which skill to expose (required for stateless)

2. **Create kord directory:**
    ```
    $KORDINATE_HOME/kords/<name>/
    ├── contract.md
    ├── data.md (empty, populated on first consult)
    └── expiry.sh
    ```

3. **Generate contract.md** — see [contract-template.md](../remember/contract-template.md) for the template. Include `mode` and `skill` fields in frontmatter.

4. **Generate expiry.sh:**
    ```bash
    #!/bin/bash
    KORD_DIR="$(cd "$(dirname "$0")" && pwd)"
    VALID_MARKER="$KORD_DIR/.valid"
    if [ -f "$VALID_MARKER" ]; then
      exit 0  # fresh
    fi
    exit 1  # stale
    ```
    Make executable: `chmod +x expiry.sh`

5. **Regenerate KORD.md** — run `$KORDINATE_HOME/agents/scribe/skills/remember/generate-kord.sh` to rebuild the index.

6. **Report** what was created:
    - "Kord `<name>` defined. Files: contract.md, data.md, expiry.sh"

## Notes

- The `.valid` marker is created by `/consult` after a successful consultation and deleted by the invalidation hook when provider state changes.
- Stateless kords don't need expiry.sh or data.md — the skill runs fresh every time.
