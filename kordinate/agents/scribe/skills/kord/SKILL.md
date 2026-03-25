---
name: kord
description: Define a new kord — a consultation contract between agents. Creates contract, registers in KORD.md.
---

Define a new kord. $ARGUMENTS should include the kord name and optionally a description.

## Procedure

1. **Gather information** — parse from arguments or ask:
    - Kord name (required, kebab-case)
    - One-line description (required)
    - Requester — which agents can invoke this kord (required, or "any")
    - Provider — which agent answers (required, exactly one)

2. **Create kord directory:**
    ```
    ~/.claude/kord/<name>/
    ├── contract.md
    └── data.md (empty, populated on first consult)
    ```

3. **Generate contract.md** — see [contract-template.md](contract-template.md) for the template.

4. **Update KORD.md** — add the new kord entry.

5. **Report** what was created.
